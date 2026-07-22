---
name: mobile-pwa
description: 'Progressive Web App and mobile patterns with React: service workers via vite-plugin-pwa, offline support, push notifications, responsive design, and app-shell. Trigger: When building a PWA, mobile-optimizing a React app, or adding offline capabilities.'
version: 2.0
metadata:
  phase:
    - construction
  layer:
    - frontend
  enforcement: optional
  depends_on:
    - react
    - notifications
  consumed_by:
    - agent-frontend
  agent_roles:
    - delivery-agent
  validation_profile: architecture
  mcp_usage: context7
---

## Purpose

Define how React applications (Vite) are packaged as PWAs with offline support, push notifications, install prompts, and mobile-optimized UX.

## When to use this skill

Activate when:
- The React app must work offline
- Push notifications are required
- Targeting mobile users with installable app behavior

## Relation to other skills

| Skill | Relation | Description |
|-------|----------|-------------|
| `react` | depends_on | Base React patterns |
| `notifications` | depends_on | Push notifications |
| `design-system` | cross-cutting | Responsive components |

## Critical Rules

1. Use `vite-plugin-pwa` to generate the manifest and service worker at build time.
2. Configure caching strategies per asset type via `workbox` options.
3. Implement an app shell (`AppShell` component) for instant first paint.
4. Use responsive design and touch-friendly controls.
5. Request notification permissions only after user interaction.
6. Test on real devices and slow networks.

## Outputs produced

| Artifact | Path | Description |
|----------|------|-------------|
| Manifest | `public/manifest.webmanifest` | App metadata |
| PWA config | `vite.config.ts` (`VitePWA({...})`) | Cache strategies |
| App shell | `src/shared/components/AppShell.tsx` | Skeleton UI |
| Push handler | `src/core/push/usePushNotifications.ts` | Notification handling |

## Example: vite.config.ts

```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      manifest: {
        name: 'App',
        short_name: 'App',
        start_url: '/',
        display: 'standalone',
        theme_color: '#0f172a',
        icons: [
          { src: 'icon-192.png', sizes: '192x192', type: 'image/png' },
          { src: 'icon-512.png', sizes: '512x512', type: 'image/png' },
        ],
      },
      workbox: {
        runtimeCaching: [
          {
            urlPattern: /^\/api\//,
            handler: 'NetworkFirst',
            options: { cacheName: 'api-cache', expiration: { maxEntries: 50, maxAgeSeconds: 300 } },
          },
          {
            urlPattern: /\.(?:png|jpg|jpeg|svg|woff2)$/,
            handler: 'CacheFirst',
            options: { cacheName: 'assets-cache', expiration: { maxEntries: 100, maxAgeSeconds: 2592000 } },
          },
        ],
      },
    }),
  ],
});
```

## Example: push notification hook

```ts
import { useCallback, useState } from 'react';

export function usePushNotifications() {
  const [permission, setPermission] = useState<NotificationPermission>(Notification.permission);

  const requestPermission = useCallback(async () => {
    const result = await Notification.requestPermission();
    setPermission(result);
    return result;
  }, []);

  return { permission, requestPermission };
}
```

## Checklist

- [ ] `vite-plugin-pwa` added and configured
- [ ] Web manifest configured (`manifest.webmanifest`)
- [ ] Service worker caching strategy defined per asset type (`workbox.runtimeCaching`)
- [ ] App shell implemented
- [ ] Push notifications gated by user interaction/permission
- [ ] Tested on mobile/slow network
