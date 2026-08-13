---
name: docker-local
description: 'Docker local development setup for Python/FastAPI + Bun backend: compose configuration,
  multi-stage builds, service networking, Kafka, Redis, PostgreSQL, OTel. Trigger: When setting
  up Docker for local development or containerizing services.'
version: 1.3
metadata:
  phase:
  - construction
  layer:
  - backend
  enforcement: recommended
  depends_on:
  consumed_by:
  - agent-backend
  - app-bootstrap
  - kubernetes
  agent_roles:
  - delivery-agent
  validation_profile: architecture-consistency
mcp_usage: none
---

## Critical Rules
| Rule | Type | Rationale |
|------|------|-----------|
| Use multi-stage builds | ALWAYS | Smaller production images |
| Never include secrets in Dockerfile | NEVER | Images are shareable |
| Use `.dockerignore` | ALWAYS | Reduce build context size |
| Use named networks for inter-service communication | ALWAYS | Service discovery by name |
| Pin base image versions | ALWAYS | Reproducible builds |
| Use environment variables for configuration | ALWAYS | 12-factor app compliance |

## docker-compose.yml Structure
```yaml
services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DB_CONNECTION}
      - APP_ENV=development
    depends_on:
      - db
    networks:
      - app-network

  db:
    image: postgres:16
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - db-data:/var/lib/postgresql/data
    networks:
      - app-network

volumes:
  db-data:

networks:
  app-network:
    driver: bridge
```

## Multi-Stage Dockerfile (Python FastAPI)
```dockerfile
FROM python:3.12-slim AS build
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --target=/install -r requirements.txt

FROM gcr.io/distroless/python3-debian12 AS runtime
WORKDIR /app
COPY --from=build /install /usr/local/lib/python3.12/site-packages
COPY . .
ENV TZ=UTC
EXPOSE 8000
USER nobody
HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Naming Conventions
| Element | Pattern | Example |
|---------|---------|---------|
| Container name | `{project}-{service}` | `myapp-api`, `myapp-db` |
| Network | `{project}-network` | `myapp-network` |
| Volume | `{project}-{data}` | `myapp-db-data` |
| Image tag | `{service}:{version}` | `api:1.0.0` |

## Inter-Service Communication
Use service names within the Docker network:
```
# From 'api' service, reach 'db' service:
ConnectionStrings__Default = "Host=db;Port=5432;Database=mydb;..."
# NOT localhost:5432
```

## Useful Commands
```bash
docker compose up -d         # Start all services
docker compose ps            # Check status
docker compose logs -f api   # Follow API logs
docker compose down          # Stop all
docker compose build --no-cache api  # Rebuild service
```

## Local Development Workflow
1. Copy `.env.example` → `.env.local` and fill values
2. `docker compose up -d`
3. `docker compose ps` — verify all healthy
4. `curl http://localhost:8000/health` — verify API running
5. Run frontend dev server separately: `vite` (React), `ng serve` (Angular), o `bun --watch src/main.ts` (Bun backend)

## .dockerignore
```
.git
.github
__pycache__
.env*
*.md
tests/
docs/
```

## Dockerfile multi-stage (Python)

### Python FastAPI — 3-stage con uv

```dockerfile
# Stage 1: Dependencies con uv
FROM ghcr.io/astral-sh/uv:python3.12-bookworm AS builder
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Cache de dependencias
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# Stage 2: Build final con solo runtime
FROM python:3.12-slim-bookworm AS runtime
WORKDIR /app

RUN groupadd -r appgroup && \
    useradd -r -g appgroup -d /app -s /bin/false appuser && \
    chown -R appuser:appuser /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"
ENV TZ=UTC

COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv
COPY --chown=appuser:appuser . .

USER appuser
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Variante con pip + requirements.txt

```dockerfile
FROM python:3.12-slim AS build
WORKDIR /app
RUN pip install --no-cache-dir --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir --target=/install -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
RUN groupadd -r appuser && useradd -r -g appuser appuser && \
    chown -R appuser:appuser /app
COPY --from=build /install /usr/local/lib/python3.12/site-packages
COPY --chown=appuser:appuser . .
ENV TZ=UTC
USER appuser
HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Bun — Runtime del backend general

> **Stack de referencia:** Python + FastAPI para AI/ML core; **Bun (TypeScript)** para backend general.

### Dockerfile Bun (multi-stage)

```dockerfile
# Stage 1: Instalar dependencias
FROM oven/bun:1 AS builder
WORKDIR /app
COPY package.json bun.lock* ./
RUN bun install --frozen-lockfile

# Stage 2: Runtime optimizado
FROM oven/bun:1-slim AS runtime
WORKDIR /app
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /bin/false appuser && \
    chown -R appuser:appuser /app

COPY --from=builder --chown=appuser:appuser /app/node_modules ./node_modules
COPY --chown=appuser:appuser . .

USER appuser
EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1

CMD ["bun", "run", "src/main.ts"]
```

### Servicio Bun en docker-compose

```yaml
  api-bun:
    build:
      context: ../backend-bun
      dockerfile: Dockerfile
    container_name: myapp-api-bun
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@db:5432/mydb
      - REDIS_URL=redis://redis:6379
      - KAFKA_BROKERS=kafka:9092
    volumes:
      - ../backend-bun/src:/app/src:ro
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
      kafka:
        condition: service_healthy
    networks:
      - app-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      <<: *health-check
    profiles:
      - core
```

## docker-compose para desarrollo local

### docker-compose.yml completo

```yaml
version: "3.9"

x-logging: &default-logging
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"

x-health-check: &health-check
  interval: 30s
  timeout: 10s
  retries: 5
  start_period: 40s

networks:
  app-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16

  monitoring:
    driver: bridge

volumes:
  postgres-data:
    driver: local
  redis-data:
    driver: local
  kafka-data:
    driver: local

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile.dev
      args:
        BUILD_CONFIGURATION: Debug
    container_name: myapp-api
    ports:
      - "8000:8000"
      - "5678:5678"
    environment:
      - APP_ENV=development
      - UVICORN_PORT=8000
      - DATABASE_URL=postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@db:5432/mydb
      - Redis__Connection=redis:6379
      - OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
    volumes:
      - ./src:/app/src:ro
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
      kafka:
        condition: service_healthy
    networks:
      - app-network
    restart: unless-stopped
    logging: *default-logging
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      <<: *health-check
    profiles:
      - core

  api-bun:
    build:
      context: ../backend-bun
      dockerfile: Dockerfile
    container_name: myapp-api-bun
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgresql://${DB_USER:-appuser}:${DB_PASSWORD:-devpassword}@db:5432/mydb
      - REDIS_URL=redis://redis:6379
      - KAFKA_BROKERS=kafka:9092
      - OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
    volumes:
      - ../backend-bun/src:/app/src:ro
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
      kafka:
        condition: service_healthy
    networks:
      - app-network
    restart: unless-stopped
    logging: *default-logging
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      <<: *health-check
    profiles:
      - core

  db:
    image: postgres:16-alpine
    container_name: myapp-db
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: ${DB_USER:-appuser}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-devpassword}
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./scripts/init-db.sh:/docker-entrypoint-initdb.d/init-db.sh:ro  # copiar de .opencode/scripts/init-db.sh
    networks:
      - app-network
    restart: unless-stopped
    logging: *default-logging
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-appuser} -d mydb"]
      <<: *health-check
    profiles:
      - core

  redis:
    image: redis:7-alpine
    container_name: myapp-redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - app-network
    restart: unless-stopped
    logging: *default-logging
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3
    profiles:
      - core

  ### Servicios con perfil dev (no levantar en CI)

  adminer:
    image: adminer:4
    container_name: myapp-adminer
    ports:
      - "9090:8080"
    networks:
      - app-network
    depends_on:
      db:
        condition: service_healthy
    profiles:
      - dev
      - admin

  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: myapp-pgadmin
    environment:
      PGADMIN_DEFAULT_EMAIL: ${PGADMIN_EMAIL:-admin@local.dev}
      PGADMIN_DEFAULT_PASSWORD: ${PGADMIN_PASSWORD:-admin}
    ports:
      - "5050:80"
    volumes:
      - pgadmin-data:/var/lib/pgadmin
    networks:
      - app-network
    depends_on:
      db:
        condition: service_healthy
    profiles:
      - dev
      - admin

  redis-commander:
    image: rediscommander/redis-commander:latest
    container_name: myapp-redis-commander
    environment:
      REDIS_HOSTS: local:redis:6379
    ports:
      - "8081:8081"
    networks:
      - app-network
    depends_on:
      - redis
    profiles:
      - dev

  ### Kafka (KRaft mode — sin Zookeeper)

  kafka:
    image: apache/kafka:3.7.0
    container_name: myapp-kafka
    environment:
      KAFKA_NODE_ID: 1
      KAFKA_PROCESS_ROLES: broker,controller
      KAFKA_LISTENERS: PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:9093
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@kafka:9093
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
      CLUSTER_ID: 'MkU3OEVBNTcwNTJENDM2Qk'
    ports:
      - "9092:9092"
    volumes:
      - kafka-data:/var/lib/kafka/data
    networks:
      - app-network
    restart: unless-stopped
    logging: *default-logging
    healthcheck:
      test: ["CMD-SHELL", "/opt/kafka/bin/kafka-broker-api-versions.sh --bootstrap-server localhost:9092 > /dev/null 2>&1"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s
    profiles:
      - core
      - messaging

  kafka-ui:
    image: provectuslabs/kafka-ui:latest
    container_name: myapp-kafka-ui
    environment:
      KAFKA_CLUSTERS_0_NAME: local
      KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS: kafka:9092
    ports:
      - "8080:8080"
    networks:
      - app-network
    depends_on:
      kafka:
        condition: service_healthy
    profiles:
      - dev
      - messaging

  mailpit:
    image: axllent/mailpit:latest
    container_name: myapp-mailpit
    ports:
      - "8025:8025"
      - "1025:1025"
    networks:
      - app-network
    profiles:
      - dev

  otel-collector:
    image: otel/opentelemetry-collector-contrib:latest
    container_name: myapp-otel
    command: ["--config=/etc/otel-config.yaml"]
    volumes:
      - ./otel-config.yaml:/etc/otel-config.yaml:ro
    ports:
      - "4317:4317"
      - "4318:4318"
    networks:
      - app-network
      - monitoring
    profiles:
      - dev
      - observability
```

### Wait-for-it — script de inicialización

```bash
#!/bin/bash
# wait-for-it.sh: espera a que un servicio TCP esté disponible
# Uso: ./wait-for-it.sh host:port -- comando

HOST=$(echo $1 | cut -d: -f1)
PORT=$(echo $1 | cut -d: -f2)
shift

echo "Esperando a $HOST:$PORT..."
while ! nc -z "$HOST" "$PORT" 2>/dev/null; do
  sleep 1
done
echo "$HOST:$PORT está disponible"

exec "$@"
```

### Uso en entrypoint del contenedor

```dockerfile
COPY wait-for-it.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/wait-for-it.sh
ENTRYPOINT ["wait-for-it.sh", "db:5432", "--", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Variables de entorno (.env.example)

```bash
# Base de datos
DB_USER=appuser
DB_PASSWORD=devpassword
DB_NAME=mydb

# Redis
REDIS_PASSWORD=

# Kafka
KAFKA_BROKERS=kafka:9092
KAFKA_TOPIC_PREFIX=myapp

# Autenticación
JWT_SECRET=change-me-in-production-min-32-chars
JWT_ISSUER=myapp.local
JWT_AUDIENCE=myapp-api

# Observabilidad
OTEL_SERVICE_NAME=myapp-api
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317

# Perfiles Docker Compose
COMPOSE_PROFILE=core,dev
```

### Comandos útiles con perfiles

```bash
# Solo servicios core (API Python + API Bun + DB + Redis + Kafka)
docker compose --profile core up -d

# Desarrollo completo (core + dev tools)
docker compose --profile core --profile dev up -d

# Con herramientas de messaging (Kafka UI)
docker compose --profile core --profile messaging up -d

# Solo administración de BD
docker compose --profile admin up -d

# Construir sin cache y levantar
docker compose build --no-cache api && docker compose --profile core up -d

# Ver logs de un servicio específico
docker compose logs -f api

# Ejecutar comando dentro del contenedor
docker compose exec api alembic upgrade head

# Kafka: crear topic
docker compose exec kafka /opt/kafka/bin/kafka-topics.sh \
  --create --topic myapp-events \
  --bootstrap-server localhost:9092 \
  --partitions 3 --replication-factor 1

# Kafka: listar topics
docker compose exec kafka /opt/kafka/bin/kafka-topics.sh \
  --list --bootstrap-server localhost:9092

# Kafka: consumir mensajes (debug)
docker compose exec kafka /opt/kafka/bin/kafka-console-consumer.sh \
  --topic myapp-events --bootstrap-server localhost:9092 \
  --from-beginning

# Detener todo (incluye todos los perfiles)
docker compose down -v
```

## Buenas prácticas de seguridad Docker

### Ejecutar como non-root

```dockerfile
# Python
RUN groupadd -r appuser && useradd -r -g appuser appuser
USER appuser
```

### Read-only root filesystem

```yaml
# En docker-compose.yml
services:
  api:
    read_only: true
    tmpfs:
      - /tmp:size=100M
      - /app/logs:size=50M
```

### Drop capabilities

```yaml
# docker-compose.yml
services:
  api:
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE
    security_opt:
      - no-new-privileges:true
```

### Ejemplo completo de seguridad en compose

```yaml
services:
  api:
    build: .
    user: "1000:1000"
    read_only: true
    tmpfs:
      - /tmp:size=100M
    cap_drop:
      - ALL
    cap_add: []
    security_opt:
      - no-new-privileges:true
    environment:
      - UVICORN_PORT=8000
```

### Escaneo de vulnerabilidades

```bash
# Docker Scout (integrado en Docker Desktop)
docker scout quickview myapp-api:latest
docker scout cves myapp-api:latest
docker scout recommendations myapp-api:latest

# Trivy (open-source, recomendado para CI)
trivy image myapp-api:latest
trivy image --severity HIGH,CRITICAL myapp-api:latest
trivy image --exit-code 1 --severity CRITICAL myapp-api:latest

# Trivy en CI (GitHub Actions)
# - name: Scan Docker image
#   uses: aquasecurity/trivy-action@master
#   with:
#     image-ref: 'myapp-api:latest'
#     format: 'sarif'
#     output: 'trivy-results.sarif'
#     severity: 'CRITICAL,HIGH'

# Análisis de SBOM
docker sbom myapp-api:latest > sbom.spdx.json
trivy sbom sbom.spdx.json
```

### .dockerignore

```gitignore
# .dockerignore universal
.git
.gitignore
.github
.env*
*.md
tests/
docs/
.DS_Store
docker-compose*.yml
__pycache__/
*.pyc
*.pyo
.pytest_cache/
.coverage
htmlcov/
.venv/
env/
```

### Resumen checklist de seguridad

| Práctica | Stack | Recomendación |
|----------|-------|---------------|
| Non-root user | Python | Siempre en runtime stage |
| Read-only FS | Python | tmpfs para escritura temporal |
| Drop capabilities | Python | `cap_drop: ALL` por defecto |
| No-new-privileges | Python | `security_opt` en compose |
| Pin versiones | Python | Evitar `:latest` en producción |
| Scan images | Python | Trivy en CI + Docker Scout local |
| Minimum layers | Python | Multi-stage,合并 RUN commands |
| SBOM generado | Python | `docker sbom` o Trivy SBOM |
| Sin secrets en build | Python | Usar build args con valores por defecto seguros |
| Distroless cuando sea posible | Python | Menor superficie de ataque |
| Healthcheck explícito | Python | Evitar contenedores zombie |
| Logging limitado | Python | `json-file` con max-size/max-file |
