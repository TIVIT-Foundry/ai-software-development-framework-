---
name: kafka
description: 'Apache Kafka patterns: producers, consumers, topics, partitions, consumer groups, message schemas, error handling, exactly-once semantics, multi-tenant isolation. Trigger: When implementing event-driven architecture, message queues, or real-time data streaming with Kafka.'
version: 1.0
metadata:
  phase:
    - construction
  layer:
    - backend
  enforcement: recommended
  depends_on:
    - observabilidad
    - error-handling
  consumed_by:
    - agent-backend
  agent_roles:
    - delivery-agent
  validation_profile: architecture
  mcp_usage: context7
---

## Purpose

Define the patterns for Apache Kafka integration in the framework. Covers producer and consumer patterns, topic design, partitioning strategies, consumer group management, message schemas (Avro/JSON), error handling, exactly-once semantics, and multi-tenant isolation. This skill ensures consistent event-driven architecture patterns.

## When to use this skill

Activate this skill when:

- Implementing event-driven architecture
- Setting up message queues for async processing
- Building real-time data streaming pipelines
- Implementing event sourcing
- Setting up Kafka with FastAPI backend
- Implementing pub/sub patterns
- Building event-driven microservices communication

**Do not** activate when:

- Using simple task queues (use Redis queues)
- Implementing WebSocket real-time (use `real-time`)
- Building synchronous request-response APIs (use `backend-api`)

## Relation to other skills

| Skill | Relation | Description |
|-------|----------|-------------|
| `observabilidad` | Complementaria | OpenTelemetry for Kafka tracing |
| `error-handling` | Complementaria | Dead letter queues, retry strategies |
| `docker-local` | Predecesora | Kafka in docker-compose |
| `real-time` | Complementaria | WebSocket for real-time UI updates |
| `ci-cd` | Complementaria | Kafka deployment in pipelines |

## Critical Rules

1. **Topics per domain** — One topic per bounded context, not per event type
2. **Partition by tenant_id** — Ensure tenant isolation at partition level
3. **Consumer groups for scaling** — Multiple consumers in same group for parallelism
4. **Schema registry** — Use Avro/JSON schemas for message validation
5. **Idempotent consumers** — Handle duplicate messages gracefully
6. **Dead letter queues** — Failed messages go to DLQ, not lost

## What the agent must do

1. **Design topics** — Topic naming, partitions, replication factor
2. **Create producers** — FastAPI endpoints that publish events
3. **Create consumers** — Background workers that consume events
4. **Configure consumer groups** — Parallel processing with consumer groups
5. **Implement error handling** — DLQ, retry, circuit breaker
6. **Add observability** — OpenTelemetry tracing for Kafka
7. **Ensure multi-tenant isolation** — Partition key by tenant_id

## Code patterns

### Kafka Configuration

```python
from pydantic import BaseSettings

class KafkaSettings(BaseSettings):
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_SCHEMA_REGISTRY_URL: str = "http://localhost:8081"
    KAFKA_CONSUMER_GROUP: str = "app-consumers"
    KAFKA_AUTO_OFFSET_RESET: str = "earliest"
    
    class Config:
        env_file = ".env"

settings = KafkaSettings()
```

### Producer Pattern

```python
from aiokafka import AioKafkaProducer
from fastapi import APIRouter, Depends
from pydantic import BaseModel
import json
import asyncio

class EventProducer:
    def __init__(self, settings: KafkaSettings):
        self.settings = settings
        self.producer: AioKafkaProducer | None = None
    
    async def start(self):
        self.producer = AioKafkaProducer(
            bootstrap_servers=self.settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )
        await self.producer.start()
    
    async def stop(self):
        if self.producer:
            await self.producer.stop()
    
    async def publish(
        self,
        topic: str,
        value: dict,
        key: str | None = None,
        partition: int | None = None,
        headers: dict | None = None
    ):
        if not self.producer:
            raise RuntimeError("Producer not started")
        
        kafka_headers = [(k, v.encode()) for k, v in (headers or {}).items()]
        
        await self.producer.send_and_wait(
            topic,
            value=value,
            key=key,
            partition=partition,
            headers=kafka_headers
        )

# Singleton producer
producer = EventProducer(settings)

# FastAPI lifecycle
@router.on_event("startup")
async def startup():
    await producer.start()

@router.on_event("shutdown")
async def shutdown():
    await producer.stop()
```

### Consumer Pattern

```python
from aiokafka import AioKafkaConsumer
import asyncio
import json
from typing import Callable, Awaitable

class EventConsumer:
    def __init__(self, settings: KafkaSettings):
        self.settings = settings
        self.consumer: AioKafkaConsumer | None = None
        self.handlers: dict[str, Callable[[dict], Awaitable[None]]] = {}
    
    def register_handler(self, topic: str, handler: Callable[[dict], Awaitable[None]]):
        self.handlers[topic] = handler
    
    async def start(self, topics: list[str]):
        self.consumer = AioKafkaConsumer(
            *topics,
            bootstrap_servers=self.settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id=self.settings.KAFKA_CONSUMER_GROUP,
            auto_offset_reset=self.settings.KAFKA_AUTO_OFFSET_RESET,
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            key_deserializer=lambda k: k.decode('utf-8') if k else None,
            enable_auto_commit=False
        )
        await self.consumer.start()
    
    async def stop(self):
        if self.consumer:
            await self.consumer.stop()
    
    async def consume(self):
        if not self.consumer:
            raise RuntimeError("Consumer not started")
        
        async for message in self.consumer:
            try:
                topic = message.topic
                handler = self.handlers.get(topic)
                
                if handler:
                    await handler(message.value)
                else:
                    print(f"No handler for topic: {topic}")
                
                # Commit offset after successful processing
                await self.consumer.commit()
                
            except Exception as e:
                # Send to DLQ
                await self.send_to_dlq(message, e)

consumer = EventConsumer(settings)

# Register handlers
async def handle_user_created(event: dict):
    print(f"User created: {event}")

consumer.register_handler("user-events", handle_user_created)

# Start consumer in background
asyncio.create_task(consumer.start(["user-events", "order-events"]))
```

### Topic Design

```python
# Topic naming convention: {domain}-{entity}-{event-type}
# Examples:
# - users-user-created
# - users-user-updated
# - orders-order-placed
# - payments-payment-completed

TOPICS = {
    # User domain
    "users-events": {
        "partitions": 3,
        "replication_factor": 1,
        "config": {
            "retention.ms": 604800000,  # 7 days
            "cleanup.policy": "delete"
        }
    },
    # Order domain
    "orders-events": {
        "partitions": 6,
        "replication_factor": 1,
        "config": {
            "retention.ms": 2592000000,  # 30 days
            "cleanup.policy": "compact"
        }
    },
    # Dead letter queue
    "dlq-all": {
        "partitions": 1,
        "replication_factor": 1,
        "config": {
            "retention.ms": 2592000000,  # 30 days
            "cleanup.policy": "delete"
        }
    }
}
```

### Multi-Tenant Partitioning

```python
async def publish_tenant_event(
    topic: str,
    tenant_id: str,
    event_type: str,
    payload: dict
):
    # Partition key ensures tenant isolation
    partition_key = f"{tenant_id}:{event_type}"
    
    await producer.publish(
        topic=topic,
        value={
            "tenant_id": tenant_id,
            "event_type": event_type,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat()
        },
        key=partition_key  # Ensures same tenant goes to same partition
    )
```

### Dead Letter Queue

```python
class DLQHandler:
    def __init__(self, producer: EventProducer):
        self.producer = producer
    
    async def send_to_dlq(self, original_message, error: Exception):
        await self.producer.publish(
            topic="dlq-all",
            value={
                "original_topic": original_message.topic,
                "original_partition": original_message.partition,
                "original_offset": original_message.offset,
                "original_key": original_message.key,
                "original_value": original_message.value,
                "error_type": type(error).__name__,
                "error_message": str(error),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

dlq = DLQHandler(producer)

# In consumer
async def consume_with_dlq():
    async for message in consumer:
        try:
            handler = handlers.get(message.topic)
            if handler:
                await handler(message.value)
            await consumer.commit()
        except Exception as e:
            await dlq.send_to_dlq(message, e)
            await consumer.commit()  # Commit to move past failed message
```

### Exactly-Once Semantics

```python
from aiokafka import AioKafkaProducer

async def process_and_produce_transactionally(
    input_message: dict,
    output_topic: str
):
    producer = AioKafkaProducer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        enable_idempotence=True,
        transactional_id=f"txn-{input_message['id']}"
    )
    
    await producer.start()
    
    try:
        # Begin transaction
        producer.begin_transaction()
        
        # Process message
        result = await process_message(input_message)
        
        # Produce output in transaction
        await producer.send_and_wait(
            output_topic,
            value=result,
            key=input_message.get("key")
        )
        
        # Commit transaction
        await producer.commit_transaction()
        
    except Exception as e:
        await producer.abort_transaction()
        raise
    finally:
        await producer.stop()
```

### FastAPI Integration

```python
from fastapi import APIRouter, BackgroundTasks

router = APIRouter()

class PublishRequest(BaseModel):
    topic: str
    event_type: str
    tenant_id: str
    payload: dict

@router.post("/events/publish")
async def publish_event(request: PublishRequest):
    await publish_tenant_event(
        topic=request.topic,
        tenant_id=request.tenant_id,
        event_type=request.event_type,
        payload=request.payload
    )
    return {"status": "published"}

@router.get("/events/consume/{topic}")
async def get_events(topic: str, limit: int = 10):
    # For admin/debug purposes
    events = await fetch_recent_events(topic, limit)
    return {"events": events}
```

### Consumer with FastAPI Background

```python
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await producer.start()
    
    # Start consumer in background
    consumer_task = asyncio.create_task(
        run_consumer(["users-events", "orders-events"])
    )
    
    yield
    
    # Shutdown
    consumer_task.cancel()
    await producer.stop()

app = FastAPI(lifespan=lifespan)

async def run_consumer(topics: list[str]):
    await consumer.start(topics)
    await consumer.consume()
```

## Decision table

| Situation | Wrong response | Expected response |
|-----------|---------------|-------------------|
| Topic design | One topic per event | One topic per domain |
| Partitioning | Random | By tenant_id |
| Error handling | Retry forever | DLQ + max retries |
| Consumer scaling | Single consumer | Consumer groups |
| Message format | Plain text | Avro/JSON with schema |
| Offsets | Auto-commit | Manual commit after processing |

## Verification checklist

- [ ] Kafka bootstrap servers configured
- [ ] Topics designed by domain
- [ ] Producer with serialization
- [ ] Consumer with deserialization
- [ ] Consumer groups configured
- [ ] Partition key by tenant_id
- [ ] DLQ implemented
- [ ] Manual offset commit
- [ ] OpenTelemetry tracing
