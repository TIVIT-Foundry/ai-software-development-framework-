---
name: real-time
description: "Real-time communication patterns with WebSockets and SSE using FastAPI. Covers pub/sub architecture, Redis backplane for scaling, reconnect logic with exponential backoff, presence tracking, channel/group authorization, message ordering, and fallback to polling. Trigger: When implementing real-time features, live updates, notifications push, or collaborative features."
version: 1.0
metadata:
  phase:
  - operations
  layer:
  - backend
  enforcement: recommended
  depends_on:
  - backend-api
  - authentication
  - playwright
  consumed_by:
  - angular
  agent_roles:
  - delivery-agent
  validation_profile: architecture-consistency
  mcp_usage: none
---

# real-time

## Propósito

Esta skill define cómo implementar comunicación en tiempo real entre servidor y clientes usando WebSockets nativos o SSE con FastAPI.  
Su función es asegurar que las notificaciones push, actualizaciones en vivo y features colaborativas funcionen de forma fiable, escalable y segura.

Esta skill complementa `backend-api` (REST endpoints) y `authentication` (identidad). Mientras aquellos manejan comunicación request/response, esta skill maneja comunicación bidireccional y push.

## Objetivo

Usa esta skill para responder estas preguntas:

1. ¿Cuándo usar WebSockets o SSE?
2. ¿Cómo se escala con múltiples servidores (Redis pub/sub)?
3. ¿Cómo se maneja reconexión con exponential backoff?
4. ¿Cómo se gestiona la presencia de usuarios online?
5. ¿Cómo se autorizan canales y grupos?

## Relación con otras skills

- `backend-api` define los endpoints REST que coexisten con las conexiones WebSocket.
- `authentication` proporciona la identidad del usuario para conexiones WebSocket.
- `authorization` define quién puede unirse a qué canales/grupos.
- `notifications` puede usar esta skill para push de notificaciones en tiempo real.
- `angular` consume las conexiones WebSocket desde el frontend.

## Qué debe hacer el agente cuando esta skill está activa

1. Seleccionar la tecnología de comunicación en tiempo real (WebSockets, SSE).
2. Definir la arquitectura de canales y el modelo de mensajes.
3. Implementar autenticación de conexiones WebSocket.
4. Implementar autorización por canal/grupo.
5. Configurar Redis pub/sub para escalado horizontal.
6. Implementar reconexión con exponential backoff en el cliente.
7. Implementar presence tracking (usuarios online).
8. Definir el modelo de mensajes y su serialización.

## Entradas esperadas

Esta skill asume que ya existe:
- estructura de endpoints (`backend-api`);
- autenticación (`authentication`);
- autorización (`authorization`).

Si falta esta base, la skill debe pedirla antes de concluir.

## Alcance de la fase

La fase sí incluye:
- selección de tecnología (WebSockets, SSE);
- arquitectura de canales;
- autenticación y autorización de conexiones;
- Redis pub/sub para escalado;
- reconexión en el cliente;
- presence tracking;
- modelo de mensajes;
- serialización.

La fase no incluye todavía:
- streaming de video/audio en vivo;
- IoT device communication;
- server-sent events para feeds masivos (millones de conexiones);
- WebRTC para comunicación peer-to-peer.

## Principios que siempre debe respetar

- Las conexiones WebSocket DEBEN autenticarse antes de unirse a canales.
- Los canales/grupos DEBEN tener autorización explícita (no broadcast global).
- La reconexión DEBE usar exponential backoff con jitter.
- Los mensajes DEBEN tener ID secuencial para detectar gaps.
- El servidor DEBE manejar reconexiones de forma idempotente (replay de mensajes perdidos).
- Los mensajes DEBEN ser serializados con tipo (no strings sin formato).
- Las conexiones DEBEN tener heartbeat para detectar desconexiones.
- El Redis pub/sub DEBE configurarse para producción.

## Qué decide esta skill y qué delega

Esta skill sí decide:
- la tecnología de comunicación en tiempo real;
- la arquitectura de canales;
- la estrategia de reconexión;
- el modelo de mensajes.

Esta skill delega:
- la autenticación de conexiones a `authentication`;
- la autorización de canales a `authorization`;
- la estructura de endpoints a `backend-api`;
- las notificaciones push a `notifications`.

## Qué debe definir el diseño

### 1. Selección de tecnología

| Tecnología | Protocolo | Pros | Contras | Uso recomendado |
|------------|----------|------|---------|-----------------|
| **WebSockets** | WS | Simple, estándar, bidireccional | Sin fallback nativo | APIs simples, comunicación bidireccional |
| **SSE** | HTTP | Simple, unidireccional, HTTP/2 | Solo servidor→cliente | Notificaciones push, feeds, dashboards |

**Decisión por defecto**: WebSockets para comunicación bidireccional, SSE para notificaciones push unidireccionales.

### 2. WebSockets con FastAPI

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from jose import jwt, JWTError
from typing import Dict
import json

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        self.active_connections.pop(user_id, None)

    async def send_personal_message(self, message: dict, user_id: str):
        ws = self.active_connections.get(user_id)
        if ws:
            await ws.send_json(message)

    async def broadcast(self, message: dict):
        for ws in self.active_connections.values():
            await ws.send_json(message)

manager = ConnectionManager()


@app.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    # Authenticate via JWT token
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            await websocket.close(code=4001, reason="Invalid token")
            return
    except JWTError:
        await websocket.close(code=4001, reason="Invalid token")
        return

    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            # Handle message types
            if message.get("type") == "subscribe":
                await manager.send_personal_message(
                    {"type": "subscribed", "channel": message.get("channel")},
                    user_id
                )
    except WebSocketDisconnect:
        manager.disconnect(user_id)
```

### 3. SSE (Server-Sent Events) con FastAPI

```python
from fastapi import Request
from fastapi.responses import StreamingResponse
import asyncio
import json

@app.get("/events/stream")
async def event_stream(request: Request):
    async def event_generator():
        while True:
            if await request.is_disconnected():
                break
            # Generate event data
            event_data = {"type": "update", "payload": {...}}
            yield f"data: {json.dumps(event_data)}\n\n"
            await asyncio.sleep(1)
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # For Nginx
        }
    )
```

### 4. Redis pub/sub para escalado

```python
import redis.asyncio as redis
import json

class RedisBroadcaster:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)

    async def publish(self, channel: str, message: dict):
        await self.redis.publish(channel, json.dumps(message))

    async def subscribe(self, channel: str):
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(channel)
        return pubsub

    async def listen(self, pubsub, websocket: WebSocket):
        async for msg in pubsub.listen():
            if msg["type"] == "message":
                await websocket.send_text(msg["data"])
```

### 5. Modelo de mensajes

```typescript
// src/types/realtime.ts
export interface RealtimeMessage<T = unknown> {
  id: string;                    // Sequential ID for gap detection
  type: MessageType;             // Message type discriminator
  channel: string;               // Channel/group name
  payload: T;                    // Typed payload
  timestamp: string;             // ISO 8601
  correlationId?: string;        // For request-response correlation
}

export type MessageType =
  | 'entity.created'
  | 'entity.updated'
  | 'entity.deleted'
  | 'notification.sent'
  | 'presence.joined'
  | 'presence.left'
  | 'system.heartbeat';

export interface EntityCreatedPayload {
  entityType: string;
  entityId: string;
  data: Record<string, unknown>;
}

export interface EntityUpdatedPayload {
  entityType: string;
  entityId: string;
  changes: Record<string, unknown>;
  previousValues?: Record<string, unknown>;
}
```

### 6. Reconexión con exponential backoff (frontend Angular)

```typescript
// src/app/features/realtime/realtime.service.ts
import { Injectable, inject, OnDestroy } from '@angular/core';
import { Subject, Observable, timer, of } from 'rxjs';
import { takeUntil, switchMap, filter, catchError, retryWhen, delayWhen } from 'rxjs/operators';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

const MAX_RECONNECT_ATTEMPTS = 10;
const BASE_DELAY_MS = 1000;
const MAX_DELAY_MS = 30000;

function calculateDelay(attempt: number): number {
  const exponentialDelay = BASE_DELAY_MS * Math.pow(2, attempt);
  const jitter = Math.random() * 1000;
  return Math.min(exponentialDelay + jitter, MAX_DELAY_MS);
}

@Injectable({ providedIn: 'root' })
export class RealtimeService implements OnDestroy {
  private ws: WebSocket | null = null;
  private attempt = 0;
  private reconnectTimer = 0;

  private readonly messages$ = new Subject<RealtimeMessage>();
  private readonly destroy$ = new Subject<void>();

  /** Stream de mensajes entrantes. Los componentes se suscriben con takeUntilDestroyed. */
  readonly onMessage$: Observable<RealtimeMessage> = this.messages$.asObservable();

  connect(url: string): void {
    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.attempt = 0;
    };

    this.ws.onmessage = (event) => {
      this.messages$.next(JSON.parse(event.data));
    };

    this.ws.onclose = (event) => {
      if (event.code !== 1000) {
        this.attempt += 1;
        if (this.attempt < MAX_RECONNECT_ATTEMPTS) {
          const delay = calculateDelay(this.attempt);
          console.log(`Reconnecting in ${delay}ms (attempt ${this.attempt})`);
          this.reconnectTimer = window.setTimeout(() => this.connect(url), delay);
        }
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  send(data: unknown): void {
    this.ws?.send(JSON.stringify(data));
  }

  close(): void {
    this.ws?.close(1000, 'Service destroyed');
    this.ws = null;
  }

  ngOnDestroy(): void {
    window.clearTimeout(this.reconnectTimer);
    this.close();
    this.destroy$.next();
    this.destroy$.complete();
  }
}
```

### 7. Suscripción a canal (Angular Service + takeUntilDestroyed)

```typescript
// src/app/features/realtime/channel-subscription.service.ts
import { Injectable, inject } from '@angular/core';
import { Observable, filter } from 'rxjs';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { RealtimeService } from './realtime.service';
import { RealtimeMessage } from '@/types/realtime';

@Injectable({ providedIn: 'root' })
export class ChannelSubscriptionService {
  private readonly realtime = inject(RealtimeService);

  /** Devuelve un Observable filtrado por canal y tipo de mensaje. */
  subscribe<T>(channel: string, messageType: string): Observable<RealtimeMessage<T>> {
    return this.realtime.onMessage$.pipe(
      filter(
        (msg) => msg.type === messageType && msg.channel === channel
      ),
      takeUntilDestroyed()
    ) as Observable<RealtimeMessage<T>>;
  }
}

// Uso en un componente standalone:
// private readonly subscriptions = inject(ChannelSubscriptionService);
// ngOnInit(): void {
//   this.subscriptions.subscribe<Task>('tasks', 'entity.updated')
//     .subscribe((msg) => this.onTaskUpdated(msg));
// }
```

### 8. Presence tracking

```python
import redis.asyncio as redis

class PresenceService:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    async def user_connected(self, user_id: str, connection_id: str):
        await self.redis.sadd(f"presence:user:{user_id}", connection_id)
        await self.redis.expire(f"presence:user:{user_id}", 300)  # 5 min TTL

    async def user_disconnected(self, user_id: str, connection_id: str):
        await self.redis.srem(f"presence:user:{user_id}", connection_id)
        remaining = await self.redis.scard(f"presence:user:{user_id}")
        if remaining == 0:
            await self.redis.delete(f"presence:user:{user_id}")

    async def is_user_online(self, user_id: str) -> bool:
        return await self.redis.scard(f"presence:user:{user_id}") > 0
```

## Preguntas guía

### 1. Sobre tecnología
- ¿Se usa WebSockets o SSE?
- ¿Se necesita comunicación bidireccional o solo servidor→cliente?

### 2. Sobre escalado
- ¿Se necesita Redis pub/sub para múltiples servidores?
- ¿Cuántas conexiones simultáneas se esperan?
- ¿Se necesita sticky sessions?

### 3. Sobre seguridad
- ¿Cómo se autentica la conexión WebSocket?
- ¿Cómo se autoriza la suscripción a canales/grupos?
- ¿Se necesita encriptación de mensajes?

### 4. Sobre presencia
- ¿Se necesita saber quién está online?
- ¿Se necesita heartbeat o ping/pong?
- ¿Cómo se maneja la desconexión no limpia?

### 5. Sobre mensajes
- ¿Qué tipos de mensajes se envían?
- ¿Se necesita garantía de entrega (at-least-once)?
- ¿Se necesita orden secuencial?

## Salidas esperadas de esta skill

### A. WebSocket/SSE endpoints configurados
- Endpoint WebSocket con autenticación y autorización por canal.
- Endpoint SSE para notificaciones push.
- ConnectionManager para gestionar conexiones.

### B. Redis pub/sub para escalado
- Configuración de Redis pub/sub en el backend.

### C. Servicios de conexión (frontend Angular)
- `RealtimeService` con reconexión y exponential backoff.
- `ChannelSubscriptionService` para suscribirse a canales con `takeUntilDestroyed`.

### D. Modelo de mensajes
- Tipos `RealtimeMessage`, `MessageType`, payloads tipados.
- Serialización JSON con tipo discriminador.

### E. Presence tracking
- Servicio de presence con Redis.
- Notificación de join/leave.

### F. Consumidores de esta skill
- `angular` consume los servicios de conexión y suscripción;
- `notifications` usa canales para push de notificaciones;
- `authentication` provee el token para la conexión WebSocket;
- `authorization` define quién puede unirse a cada canal.

## Criterios de calidad

- Las conexiones WebSocket se autentican antes de unirse a canales.
- Los canales/grupos tienen autorización explícita.
- La reconexión usa exponential backoff con jitter.
- Los mensajes tienen ID secuencial para detectar gaps.
- El servidor maneja reconexiones de forma idempotente.
- Las conexiones tienen heartbeat para detectar desconexiones.
- Redis pub/sub está configurado para producción.
- Los mensajes son tipados (no strings sin formato).

## Comportamiento esperado del agente

Cuando el usuario pida polling como mecanismo principal, el agente debe explicar que WebSockets/SSE es más eficiente y proponer la opción más adecuada.  
Cuando el usuario no autorice canales, el agente debe advertir que broadcast global es un riesgo de seguridad y proponer autorización por grupo.  
Cuando el usuario no maneje reconexión, el agente debe proponer exponential backoff con jitter.  
Cuando el usuario use strings sin formato para mensajes, el agente debe proponer tipos discriminados y schemas.

## Checklist final de la skill

- ¿Se seleccionó la tecnología (WebSockets/SSE)?
- ¿Se configuró el ConnectionManager con autenticación?
- ¿Se configuró Redis pub/sub para producción?
- ¿La reconexión usa exponential backoff con jitter?
- ¿Los mensajes son tipados con ID secuencial?
- ¿Se implementó presence tracking?
- ¿Los canales tienen autorización explícita?
- ¿Se crearon los servicios de conexión en el frontend Angular?
- ¿Se documentaron los tipos de mensajes?
