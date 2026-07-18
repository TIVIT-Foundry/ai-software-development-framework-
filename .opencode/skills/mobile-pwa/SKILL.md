---
name: mobile-pwa
description: 'Progressive Web App and mobile patterns with Angular: service workers, offline support, push notifications, responsive design, and app-shell. Trigger: When building a PWA, mobile-optimizing an Angular app, or adding offline capabilities.'
version: 1.0
metadata:
  phase:
    - construction
  layer:
    - frontend
  enforcement: optional
  depends_on:
    - angular
    - notifications
  consumed_by:
    - agent-frontend
  agent_roles:
    - delivery-agent
  validation_profile: architecture
  mcp_usage: context7
---

## Purpose

Define how Angular applications are packaged as PWAs with offline support, push notifications, install prompts, and mobile-optimized UX.

## When to use this skill

Activate when:
- The Angular app must work offline
- Push notifications are required
- Targeting mobile users with installable app behavior

## Relation to other skills

| Skill | Relation | Description |
|-------|----------|-------------|
| `angular` | depends_on | Base Angular patterns |
| `notifications` | depends_on | Push notifications |
| `design-system` | cross-cutting | Responsive components |

## Critical Rules

1. Use `@angular/pwa` schematic to bootstrap PWA features.
2. Configure service worker caching strategies per asset type.
3. Implement app shell for instant first paint.
4. Use responsive design and touch-friendly controls.
5. Request notification permissions only after user interaction.
6. Test on real devices and slow networks.

## Outputs produced

| Artifact | Path | Description |
|----------|------|-------------|
| Manifest | `src/manifest.webmanifest` | App metadata |
| Service worker config | `ngsw-config.json` | Cache strategies |
| App shell | `src/app/app-shell/` | Skeleton UI |
| Push handler | `src/app/core/push.service.ts` | Notification handling |

## Example: ngsw-config.json

```json
{
  "assetGroups": [
    {
      "name": "app",
      "installMode": "prefetch",
      "resources": {
        "files": ["/favicon.ico", "/index.html", "/manifest.webmanifest"]
      }
    }
  ]
}
```

## Checklist

- [ ] `@angular/pwa` added
- [ ] Web manifest configured
- [ ] Service worker caching strategy defined
- [ ] App shell implemented
- [ ] Push notifications gated by permission
- [ ] Tested on mobile/slow network
