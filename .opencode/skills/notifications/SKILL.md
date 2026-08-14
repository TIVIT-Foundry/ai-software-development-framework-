---
name: notifications
description: 'Notification patterns: in-app, email, push, webhook notifications with
  templates and delivery tracking. Trigger: When implementing notifications, alerts,
  or messaging systems.'
version: 1.1
metadata:
  phase:
  - construction
  layer:
  - backend
  - frontend
  enforcement: recommended
  depends_on:
  - backend-api
  consumed_by:
  - agent-backend
  - agent-fullstack
  - mobile-pwa
  agent_roles:
  - design-agent
  - delivery-agent
  validation_profile: architecture-consistency
mcp_usage: none
---

## Tabla de contenidos

- Critical Rules
- Notification Types
- Notification Database Schema
- Notification Status Machine
- Event-Driven Delivery (Preferred)
- Template Pattern
- In-App Notification (Frontend — React)
- In-App Notification (Frontend — Angular)
- Provider Options
- Retry Policy
- Delivery Tracking
- Notificaciones push modernas e integración con real-time
  - 1. Firebase Cloud Messaging (FCM)
  - 2. Apple Push Notification Service (APNs)
  - 3. Notificaciones WebSocket (integración con skill real-time)
  - 4. Gestión de preferencias de notificación por usuario
  - 5. Gestión de templates de email

## Critical Rules
| Rule | Type | Rationale |
|------|------|-----------|
| Use async/event-driven delivery | ALWAYS | Avoid blocking on notification send |
| Persist notification state for retry | ALWAYS | Reliability |
| Support opt-out/unsubscribe | ALWAYS | Legal/compliance |
| Use templates for content | ALWAYS | Consistency and maintainability |
| Never include sensitive data in notification body | NEVER | Security risk |
| Log notification outcome (sent, failed, bounced) | ALWAYS | Observability |

## Notification Types

| Type | Channel | Use case |
|------|---------|---------|
| In-app | WebSocket / polling / SSE | Real-time alerts |
| Email | SMTP / SES / SendGrid | Confirmations, digests |
| SMS | Twilio / Vonage | Critical alerts |
| Push | FCM / APNs / OneSignal | Mobile apps |
| Webhook | HTTP POST | System-to-system events |
| Slack/Teams | Incoming webhooks | Team alerts |

## Notification Database Schema
```sql
CREATE TABLE Notifications.NotificationMessage (
    notification_message_id   SERIAL PRIMARY KEY,
    user_id                  VARCHAR(128) NOT NULL,
    channel                 VARCHAR(50)  NOT NULL,  -- 'email', 'in-app', 'push'
    template_id              VARCHAR(100) NOT NULL,
    subject                 VARCHAR(500) NULL,
    body                    TEXT NOT NULL,
    status                  VARCHAR(50)  NOT NULL DEFAULT 'PENDING',  -- PENDING/SENT/FAILED
    sent_at                  TIMESTAMPTZ     NULL,
    retry_count              INT           NOT NULL DEFAULT 0,
    max_retries              INT           NOT NULL DEFAULT 3,
    record_creation_date      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);
```

## Notification Status Machine
```
PENDING → SENDING → SENT
PENDING → SENDING → FAILED → RETRY → SENT / PERMANENTLY_FAILED
```

## Event-Driven Delivery (Preferred)
```
Domain Event (OrderCreated) → Event Bus / Queue →
Notification Consumer → Resolve template → Deliver to channel → Update status
```

## Template Pattern
```typescript
interface NotificationTemplate {
  templateId: string;
  channel: 'email' | 'in-app' | 'push';
  subject: (vars: Record<string, string>) => string;
  body: (vars: Record<string, string>) => string;
}

const ORDER_CREATED: NotificationTemplate = {
  templateId: 'order.created',
  channel: 'email',
  subject: ({ orderNumber }) => `Order #${orderNumber} confirmed`,
  body: ({ orderNumber, userName }) =>
    `Hello ${userName}, your order #${orderNumber} has been confirmed.`,
};
```

## In-App Notification (Frontend — React)

```typescript
// use-notifications-stream.ts
import { useCallback, useEffect, useRef, useState } from 'react';

export interface Notification {
  id: string;
  templateId: string;
  subject: string;
  body: string;
  read: boolean;
  receivedAt: string;
}

export function useNotificationsStream() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const eventSourceRef = useRef<EventSource | null>(null);

  const connect = useCallback(() => {
    const eventSource = new EventSource('/api/notifications/stream');

    eventSource.onmessage = (event) => {
      const notification: Notification = JSON.parse(event.data);
      setNotifications((prev) => [notification, ...prev]);
    };

    eventSourceRef.current = eventSource;
  }, []);

  const disconnect = useCallback(() => {
    eventSourceRef.current?.close();
    eventSourceRef.current = null;
  }, []);

  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);

  return { notifications };
}
```

**Uso en componente:**

```tsx
// NotificationList.tsx
import { useNotificationsStream } from './use-notifications-stream';

export function NotificationList() {
  const { notifications } = useNotificationsStream();

  return (
    <div className="notification-list">
      {notifications.map((n) => (
        <div key={n.id} className={`notification-item${!n.read ? ' unread' : ''}`}>
          <strong>{n.subject}</strong>
          <p>{n.body}</p>
        </div>
      ))}
    </div>
  );
}
```

## In-App Notification (Frontend — Angular)

```typescript
// notification.service.ts
import { Injectable, inject, NgZone, OnDestroy } from '@angular/core';
import { Subject, Observable } from 'rxjs';

export interface Notification {
  id: string;
  templateId: string;
  subject: string;
  body: string;
  read: boolean;
  receivedAt: string;
}

@Injectable({ providedIn: 'root' })
export class NotificationService implements OnDestroy {
  private readonly zone = inject(NgZone);
  private readonly destroy$ = new Subject<void>();
  private readonly notifications$ = new Subject<Notification>();
  private eventSource: EventSource | null = null;

  /** Observable de notificaciones entrantes (SSE) */
  get notifications(): Observable<Notification> {
    return this.notifications$.asObservable();
  }

  connect(): void {
    this.eventSource = new EventSource('/api/notifications/stream');

    this.zone.runOutsideAngular(() => {
      this.eventSource!.onmessage = (event) => {
        const notification: Notification = JSON.parse(event.data);
        this.zone.run(() => this.notifications$.next(notification));
      };
    });
  }

  disconnect(): void {
    this.eventSource?.close();
    this.eventSource = null;
  }

  ngOnDestroy(): void {
    this.disconnect();
    this.destroy$.next();
    this.destroy$.complete();
  }
}
```

**Uso en componente:**

```typescript
// notification-list.component.ts
import { Component, inject, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Subject, takeUntil } from 'rxjs';
import { NotificationService, Notification } from './notification.service';

@Component({
  selector: 'app-notification-list',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="notification-list">
      @for (n of notifications; track n.id) {
        <div class="notification-item" [class.unread]="!n.read">
          <strong>{{ n.subject }}</strong>
          <p>{{ n.body }}</p>
        </div>
      }
    </div>
  `,
})
export class NotificationListComponent implements OnInit, OnDestroy {
  private readonly notificationService = inject(NotificationService);
  private readonly destroy$ = new Subject<void>();

  notifications: Notification[] = [];

  ngOnInit(): void {
    this.notificationService.connect();
    this.notificationService.notifications
      .pipe(takeUntil(this.destroy$))
      .subscribe((n) => this.notifications.unshift(n));
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
```

## Provider Options

| Channel | Options |
|---------|---------|
| Email | AWS SES, SendGrid, Mailgun, Postmark |
| SMS | Twilio, Vonage, AWS SNS |
| Push | FCM (Android), APNs (iOS), OneSignal |
| Queuing | RabbitMQ, AWS SQS, Redis Streams |

## Retry Policy
```python
# Python tenacity retry with exponential backoff
from tenacity import retry, wait_exponential, stop_after_attempt

@retry(
    wait=wait_exponential(multiplier=1, max=10),
    stop=stop_after_attempt(3),
)
async def send_notification():
    ...
```

## Delivery Tracking
| Metric | Description |
|--------|-------------|
| `sent_count` | Successfully delivered |
| `failed_count` | Failed after all retries |
| `open_rate` | % of emails opened (email only) |
| `bounce_rate` | Invalid addresses (email only) |

## Notificaciones push modernas e integración con real-time

### 1. Firebase Cloud Messaging (FCM)

**Arquitectura de integración:**

```
Backend → FCM Admin SDK → FCM Service → Dispositivo (Android/iOS/Web)
```

**Registro de device tokens:**

```sql
CREATE TABLE Notifications.DeviceToken (
    device_token_id     SERIAL PRIMARY KEY,
    user_id            VARCHAR(128) NOT NULL,
    token             VARCHAR(500) NOT NULL,
    platform          VARCHAR(20)  NOT NULL,  -- 'android', 'ios', 'web'
    app_version        VARCHAR(50)  NULL,
    is_active          BIT           NOT NULL DEFAULT 1,
    registered_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    last_used_at        TIMESTAMPTZ     NULL,
    CONSTRAINT UQ_DeviceToken_Token UNIQUE (token)
);

CREATE INDEX IX_DeviceToken_UserId ON Notifications.DeviceToken (user_id, is_active);
```

**Patrón de envío por backend (Python):**

```python
from firebase_admin import messaging
from typing import Any


class FcmNotificationService:
    def __init__(self, token_repository):
        self._token_repository = token_repository

    async def send_to_tokens(
        self,
        tokens: list[str],
        title: str,
        body: str,
        data: dict[str, str],
    ) -> messaging.BatchResponse:
        message = messaging.MulticastMessage(
            tokens=tokens,
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data,
            android=messaging.AndroidConfig(
                priority="high",
                notification=messaging.AndroidNotification(
                    icon="notification_icon",
                    click_action="OPEN_DETAIL",
                ),
            ),
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        sound="default",
                        badge=1,
                    ),
                ),
            ),
        )

        response = messaging.send_multicast(message)

        await self._handle_failed_tokens(tokens, response.responses)

        return response

    async def _handle_failed_tokens(
        self,
        tokens: list[str],
        responses: list[messaging.SendResponse],
    ) -> None:
        for i, send_response in enumerate(responses):
            if not send_response.success:
                error = send_response.exception
                if (
                    error is not None
                    and isinstance(error, messaging.MessagingError)
                    and hasattr(error, "code")
                    and error.code == messaging.MessagingErrorCode.UNREGISTERED
                ):
                    await self._token_repository.deactivate(tokens[i])
```

**Topics (suscripción temática):**

```python
# Suscripción a topics por tenant/rol
messaging.subscribe_to_topic(tokens, f"tenant-{tenant_id}-alerts")
messaging.subscribe_to_topic(tokens, f"tenant-{tenant_id}-{role}")

# Envío masivo por topic
messaging.send(
    messaging.Message(
        topic=f"tenant-{tenant_id}-alerts",
        notification=messaging.Notification(title="Alerta", body=message),
    )
)
```

**Reglas:**
| Regla | Tipo | Razón |
|-------|------|-------|
| Invalidar tokens con error `UNREGISTERED` | SIEMPRE | Evitar envíos a tokens inválidos |
| Rotar tokens al reinstalar la app | SIEMPRE | Un dispositivo = un token activo |
| Usar topics para broadcasts masivos | SIEMPRE | Escalabilidad frente a envío individual |
| Limitar data payload a 4 KB | SIEMPRE | Restricción FCM |

---

### 2. Apple Push Notification Service (APNs)

**Cuándo usar APNs directo (sin FCM):**

| Escenario | Usar APNs directo |
|-----------|-------------------|
| App solo iOS, sin Android | Sí — menor latencia |
| Se requiere entrega instantánea | Sí — conexión directa con APNs |
| Se necesita notificación crítica (Critical Alerts) | Sí — requiere entitlement especial |
| App multiplataforma | No — usar FCM como capa unificada |

**Configuración necesaria:**

```
1. Apple Developer Account → Certificado push (.p8 key)
2. Registrar App ID con Push Notification capability
3. Provisionar key en Settings → Keys → Apple Push Notification service
4. Distribuir .p8 al backend
```

**Envío directo con APNs (Python):**

```python
import time
import httpx
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from typing import Any


class ApnsNotificationService:
    def __init__(
        self,
        http_client: httpx.AsyncClient,
        apns_key: str,
        team_id: str,
        key_id: str,
        bundle_id: str,
        token_repository,
    ):
        self._http_client = http_client
        self._apns_key = apns_key
        self._team_id = team_id
        self._key_id = key_id
        self._bundle_id = bundle_id
        self._token_repository = token_repository

    async def send(
        self,
        device_token: str,
        title: str,
        body: str,
        custom_data: dict[str, object] | None = None,
        is_critical: bool = False,
    ) -> None:
        aps: dict[str, Any] = {
            "alert": {"title": title, "body": body},
            "badge": 1,
            "content-available": 1,
        }

        if is_critical:
            aps["sound"] = {"critical": 1, "name": "default", "volume": 0.5}
        else:
            aps["sound"] = "default"

        payload: dict[str, Any] = {"aps": aps}
        if custom_data:
            payload.update(custom_data)

        jwt_token = self._generate_apns_jwt()

        headers = {
            "authorization": f"bearer {jwt_token}",
            "apns-topic": self._bundle_id,
            "apns-push-type": "critical" if is_critical else "alert",
        }

        response = await self._http_client.post(
            f"https://api.push.apple.com/3/device/{device_token}",
            json=payload,
            headers=headers,
        )

        if response.status_code == 410:  # Gone
            await self._token_repository.deactivate(device_token)

    def _generate_apns_jwt(self) -> str:
        # JWT con ES256, kid = Key ID, iss = Team ID
        now = int(time.time())
        private_key = serialization.load_pem_private_key(
            self._apns_key.encode(),
            password=None,
            backend=default_backend(),
        )

        token = jwt.encode(
            {
                "iss": self._team_id,
                "iat": now,
            },
            private_key,
            algorithm="ES256",
            headers={"kid": self._key_id},
        )

        return token
```

**Reglas APNs:**
| Regla | Tipo | Razón |
|-------|------|-------|
| Usar API v2 (`api.push.apple.com`) | SIEMPRE | v1 deprecada |
| Incluir `apns-push-type` header | SIEMPRE | Requerido desde iOS 13+ |
| Manejar `410 Gone` para invalidar tokens | SIEMPRE | Limpieza de BD |
| JWT con expiración < 1 hora | SIEMPRE | Restricción APNs |

---

### 3. Notificaciones WebSocket (integración con skill real-time)

**Patrón de integración:**

Las notificaciones WebSocket delegan la conexión a la skill `real-time` y la lógica de negocio a esta skill (`notifications`).

```
┌─────────────┐    evento     ┌─────────────┐    publish    ┌───────────┐
│  Backend     │─────────────►│  Event Bus  │──────────────►│  Redis    │
│  (dominio)   │              │  (RabbitMQ) │              │  Stream   │
└─────────────┘               └─────────────┘              └─────┬─────┘
                                                                  │ subscribe
┌─────────────┐    WS / SSE   ┌─────────────┐    receive    ┌─────▼─────┐
│  Frontend    │◄──────────────│  real-time   │◄──────────────│  Worker   │
│  (React)     │               │  (pub/sub)   │               │  (notif)  │
└─────────────┘               └─────────────┘               └───────────┘
```

**Servicio de notificación WS:**

```python
class WebSocketNotificationService:
    def __init__(self, hub_context, repo):
        self._hub_context = hub_context
        self._repo = repo

    async def send_to_user(self, user_id: str, payload: dict):
        await self._repo.save({
            "user_id": user_id,
            "channel": "in-app",
            "template_id": payload["template_id"],
            "subject": payload["subject"],
            "body": payload["body"],
            "status": "SENT",
            "sent_at": datetime.utcnow(),
        })

        await self._hub_context.send_to_group(
            f"user-{user_id}",
            "notification_received",
            {
                "template_id": payload["template_id"],
                "subject": payload["subject"],
                "body": payload["body"],
                "received_at": datetime.utcnow().isoformat(),
            },
        )

    async def send_to_tenant(self, tenant_id: str, payload: dict):
        await self._hub_context.send_to_group(
            f"tenant-{tenant_id}",
            "notification_received",
            payload,
        )
```

**Hook React para notificaciones WS (referencia a skill `real-time`):**

```typescript
// use-realtime-notifications.ts
import { useCallback, useEffect, useRef, useState } from 'react';
import type { Notification } from './use-notifications-stream';

interface WsNotificationPayload {
  template_id: string;
  subject: string;
  body: string;
  received_at: string;
}

export function useRealtimeNotifications() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const socketRef = useRef<WebSocket | null>(null);

  const connect = useCallback(() => {
    const socket = new WebSocket('/ws/notifications');

    socket.onmessage = (event) => {
      const payload: WsNotificationPayload = JSON.parse(event.data);
      const notification: Notification = {
        id: crypto.randomUUID(),
        templateId: payload.template_id,
        subject: payload.subject,
        body: payload.body,
        read: false,
        receivedAt: payload.received_at,
      };

      setNotifications((prev) => [notification, ...prev]);

      // Notificación del navegador si hay permiso
      if (typeof Notification !== 'undefined' && Notification.permission === 'granted') {
        new window.Notification(payload.subject, { body: payload.body });
      }
    };

    socket.onerror = (err) => console.error('WS notifications error', err);
    socketRef.current = socket;
  }, []);

  const markAsRead = useCallback(async (id: string) => {
    await fetch(`/api/notifications/${id}/read`, { method: 'POST' });
    setNotifications((prev) => prev.map((n) => (n.id === id ? { ...n, read: true } : n)));
  }, []);

  const disconnect = useCallback(() => {
    socketRef.current?.close();
    socketRef.current = null;
  }, []);

  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);

  return { notifications, markAsRead };
}
```

**Reglas WS:**
| Regla | Tipo | Razón |
|-------|------|-------|
| Persistir notificación ANTES de enviar por WS | SIEMPRE | No perder datos si WS falla |
| Usar groups por usuario/tenant | SIEMPRE | Aislamiento multi-tenant |
| Implementar fallback a polling si WS desconecta | SIEMPRE | Resiliencia |

---

### 4. Gestión de preferencias de notificación por usuario

**Esquema de preferencias:**

```sql
CREATE TABLE Notifications.NotificationPreference (
    notification_preference_id  SERIAL PRIMARY KEY,
    user_id                     VARCHAR(128) NOT NULL,
    category                  VARCHAR(100) NOT NULL,  -- 'orders', 'security', 'marketing'
    channel                    VARCHAR(50)  NOT NULL,  -- 'email', 'push', 'in-app', 'sms'
    is_opted_in                  BIT           NOT NULL DEFAULT 1,
    frequency                  VARCHAR(20)  NOT NULL DEFAULT 'immediate',  -- 'immediate', 'daily', 'weekly', 'off'
    quiet_hours_start            TIME          NULL,  -- Ej: 22:00
    quiet_hours_end              TIME          NULL,  -- Ej: 07:00
    record_creation_date         TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    record_update_date           TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    CONSTRAINT UQ_NotifPref_User_Category_Channel UNIQUE (user_id, category, channel)
);
```

**Catálogo de categorías por defecto:**

```sql
INSERT INTO Notifications.NotificationPreferenceCategory (Category, DisplayName, IsMandatory)
VALUES
    ('security',  'Seguridad y alertas críticas', 1),  -- No se puede desactivar
    ('orders',     'Actualizaciones de pedidos',    0),
    ('account',    'Cambios en la cuenta',          0),
    ('marketing',  'Promociones y novedades',       0);
```

**Servicio de preferencias:**

```python
from datetime import datetime, time, timezone
from typing import Any


class NotificationPreferenceService:
    def __init__(self, repo):
        self._repo = repo

    async def should_send(self, user_id: str, category: str, channel: str) -> bool:
        # Categorías obligatorias siempre se envían
        if await self._repo.is_mandatory(category):
            return True

        pref = await self._repo.get(user_id, category, channel)

        if pref is None:
            return True  # Default: opt-in si no hay preferencia explícita

        if not pref.is_opted_in:
            return False

        if channel == "push" and self._is_in_quiet_hours(pref):
            return False

        return True

    async def apply_digest_frequency(self, user_id: str, frequency: str) -> Any:
        if frequency == "off":
            return await self._repo.opt_out_all(user_id)

        return await self._repo.set_frequency_for_all(user_id, frequency)

    def _is_in_quiet_hours(self, pref) -> bool:
        if pref.quiet_hours_start is None or pref.quiet_hours_end is None:
            return False

        now = datetime.now(timezone.utc).time()
        return pref.quiet_hours_start <= now <= pref.quiet_hours_end
```

**API de preferencias:**

```typescript
// GET  /api/users/{userId}/notification-preferences
// PUT  /api/users/{userId}/notification-preferences
// POST /api/users/{userId}/notification-preferences/reset-defaults

interface NotificationPreferenceUpdate {
  category: string;
  channel: string;
  isOptedIn: boolean;
  frequency?: 'immediate' | 'daily' | 'weekly' | 'off';
  quietHoursStart?: string;  // HH:mm
  quietHoursEnd?: string;    // HH:mm
}
```

**Hooks React para preferencias (con @tanstack/react-query):**

```typescript
// use-notification-preferences.ts
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import type { NotificationPreferenceUpdate, NotificationPreference } from './notification-preferences.model';

const apiClient = {
  get: <T>(url: string) => fetch(url).then((r) => r.json() as Promise<T>),
  put: (url: string, body: unknown) =>
    fetch(url, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }),
};

export function useNotificationPreferences(userId: string) {
  return useQuery({
    queryKey: ['notification-preferences', userId],
    queryFn: () => apiClient.get<NotificationPreference[]>(`/api/users/${userId}/notification-preferences`),
  });
}

export function useUpdateNotificationPreferences(userId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (prefs: NotificationPreferenceUpdate[]) =>
      apiClient.put(`/api/users/${userId}/notification-preferences`, prefs),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notification-preferences', userId] });
    },
  });
}
```

**Uso en componente:**

```tsx
// NotificationPreferences.tsx
import { useNotificationPreferences, useUpdateNotificationPreferences } from './use-notification-preferences';

interface Pref { category: string; channel: string; isOptedIn: boolean }

export function NotificationPreferences({ userId }: { userId: string }) {
  const prefs = useNotificationPreferences(userId);
  const updateMutation = useUpdateNotificationPreferences(userId);

  const toggle = (pref: Pref) => {
    updateMutation.mutate([{ category: pref.category, channel: pref.channel, isOptedIn: !pref.isOptedIn }]);
  };

  if (prefs.isLoading) return <p>Cargando...</p>;

  return (
    <>
      {prefs.data?.map((pref) => (
        <div className="pref-row" key={`${pref.category}-${pref.channel}`}>
          <span>{pref.category} — {pref.channel}</span>
          <input type="checkbox" checked={pref.isOptedIn} onChange={() => toggle(pref)} />
        </div>
      ))}
    </>
  );
}
```

**Reglas de preferencias:**
| Regla | Tipo | Razón |
|-------|------|-------|
| Categorías obligatorias (seguridad) no se pueden desactivar | SIEMPRE | Compliance y seguridad |
| Default = opt-in si no hay preferencia explícita | SIEMPRE | No silenciar notificaciones críticas por omisión |
| Respetar quiet hours para push | SIEMPRE | UX y regulaciones |
| Permitir reset a defaults | SIEMPRE | Recuperación de estado |
| Guardar log de cambios de preferencia | RECOMENDADO | Auditoría |

---

### 5. Gestión de templates de email

**Motor de templates: comparativa**

| Motor | Fortaleza | Cuándo usar |
|-------|-----------|-------------|
| Handlebars | Lógica simple, amplio ecosistema | Templates transaccionales con variables |
| MJML | Responsive, diseño visual | Newsletters y emails marketing |
| Jinja2 (Python) | Integración nativa backend | Proyectos Python sin dependencias extra |
| React Email | Componentes para email (legacy/comparación) | Proyectos full-stack con React (no es stack TIVIT) |

**Patrón con Handlebars (recomendado para multi-propósito):**

```typescript
import Handlebars from 'handlebars';

const templates: Record<string, Handlebars.TemplateDelegate> = {};

export function registerTemplate(templateId: string, source: string): void {
  templates[templateId] = Handlebars.compile(source);
}

export function renderTemplate(
  templateId: string,
  vars: Record<string, unknown>
): string {
  const template = templates[templateId];
  if (!template) throw new Error(`Template not found: ${templateId}`);
  return template(vars);
}
```

**Patrón con MJML (emails responsive):**

```typescript
import mjml from 'mjml';
import Handlebars from 'handlebars';

export function renderMjmlTemplate(
  mjmlSource: string,
  vars: Record<string, unknown>
): { html: string; errors: string[] } {
  const compiled = Handlebars.compile(mjmlSource);
  const merged = compiled(vars);
  const result = mjml(merged, { validationLevel: 'soft' });
  return { html: result.html, errors: result.errors };
}
```

**Almacenamiento de templates en BD:**

```sql
CREATE TABLE Notifications.EmailTemplate (
    email_template_id      SERIAL PRIMARY KEY,
    template_id           VARCHAR(100) NOT NULL,
    channel              VARCHAR(50)  NOT NULL DEFAULT 'email',
    locale               VARCHAR(10)  NOT NULL DEFAULT 'es',
    subject_template      VARCHAR(500) NOT NULL,
    body_template          TEXT NOT NULL,  -- Handlebars o MJML
    content_type           VARCHAR(20)  NOT NULL DEFAULT 'html',  -- 'html', 'mjml'
    is_active              BIT           NOT NULL DEFAULT 1,
    version               INT           NOT NULL DEFAULT 1,
    record_creation_date    TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    record_update_date      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    CONSTRAINT UQ_EmailTemplate_Id_Locale_Version UNIQUE (template_id, locale, version)
);
```

**Servicio de templates con fallback de locale:**

```python
class TemplateNotFoundException(Exception):
    def __init__(self, template_id: str):
        super().__init__(f"Template not found: {template_id}")


class RenderedEmail:
    def __init__(self, subject: str, body: str):
        self.subject = subject
        self.body = body


class EmailTemplateService:
    def __init__(self, repo, renderer, mjml_renderer):
        self._repo = repo
        self._renderer = renderer
        self._mjml_renderer = mjml_renderer

    async def render(
        self,
        template_id: str,
        locale: str,
        vars: dict[str, str],
    ) -> RenderedEmail:
        template = (
            await self._repo.get_active(template_id, locale)
            or await self._repo.get_active(template_id, "es")
        )

        if template is None:
            raise TemplateNotFoundException(template_id)

        subject = self._renderer.render(template.subject_template, vars)
        body = self._renderer.render(template.body_template, vars)

        if template.content_type == "mjml":
            body = self._mjml_renderer.render(body)

        return RenderedEmail(subject, body)
```

**Preview y testing de templates:**

```python
from fastapi import APIRouter, Depends
from pydantic import BaseModel


router = APIRouter(prefix="/api/admin/email-templates", tags=["email-templates"])


class PreviewRequest(BaseModel):
    locale: str = "es"
    variables: dict[str, str] = {}


class TestSendRequest(BaseModel):
    locale: str = "es"
    variables: dict[str, str] = {}
    test_email_address: str


class EmailPreview(BaseModel):
    subject: str
    html_body: str
    text_body: str


@router.post("/{template_id}/preview")
async def preview(
    template_id: str,
    request: PreviewRequest,
    template_service: "EmailTemplateService" = Depends(),
) -> EmailPreview:
    rendered = await template_service.render(
        template_id,
        request.locale or "es",
        request.variables,
    )

    return EmailPreview(
        subject=rendered.subject,
        html_body=rendered.body,
        text_body=html_to_text(rendered.body),
    )


@router.post("/{template_id}/test-send", status_code=204)
async def send_test(
    template_id: str,
    request: TestSendRequest,
    template_service: "EmailTemplateService" = Depends(),
    email_provider=Depends(),
) -> None:
    rendered = await template_service.render(
        template_id,
        request.locale or "es",
        request.variables,
    )

    await email_provider.send(
        request.test_email_address,
        rendered.subject,
        rendered.body,
    )
```

**Componente React de preview:**

```tsx
// EmailPreview.tsx
import { useState } from 'react';

export interface EmailPreviewResult {
  subject: string;
  htmlBody: string;
  textBody: string;
}

interface EmailPreviewProps {
  templateId: string;
  locale?: string;
  variables?: Record<string, string>;
}

export function EmailPreview({ templateId, locale = 'es', variables = {} }: EmailPreviewProps) {
  const [preview, setPreview] = useState<EmailPreviewResult | null>(null);

  const loadPreview = async () => {
    const res = await fetch(`/api/admin/email-templates/${templateId}/preview`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ locale, variables }),
    });
    setPreview(await res.json());
  };

  return (
    <>
      {preview && (
        <div className="email-preview">
          <div className="email-preview__subject">{preview.subject}</div>
          <iframe className="email-preview__body" srcDoc={preview.htmlBody} title="Email preview" />
        </div>
      )}
      <button onClick={loadPreview}>Preview</button>
    </>
  );
}
```

**Reglas de templates:**
| Regla | Tipo | Razón |
|-------|------|-------|
| Separar Subject y Body como templates distintos | SIEMPRE | Mantenibilidad |
| Fallback al locale default (`es`) si no existe traducción | SIEMPRE | Evitar emails vacíos |
| Versionar templates en BD | SIEMPRE | Rollback y auditoría |
| Preview endpoint protegido (solo admin) | SIEMPRE | Seguridad |
| Datos sensibles nunca en templates | NUNCA | Prevención de exposición |
| Validar MJML antes de guardar | SIEMPRE | Evitar runtime errors |
