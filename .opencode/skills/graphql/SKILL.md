---
name: graphql
description: 'GraphQL API design: schema design, resolvers, N+1 problem, DataLoader,
  mutations, subscriptions, authentication, error handling, cursor-based pagination.
  Trigger: When designing or implementing GraphQL APIs in Bun (TypeScript), Python
  (AI/ML core), or React (Apollo Client) / Angular (Apollo Angular) frontend
  consumption, per the project''s frontend choice.'
version: 1.1
metadata:
  phase:
  - construction
  layer:
  - backend
  enforcement: recommended
  depends_on:
  - backend-api
  - security
  - error-handling
  consumed_by:
  - agent-backend
  - agent-fullstack
  agent_roles:
  - design-agent
  - delivery-agent
  validation_profile: architecture-consistency
  mcp_usage: none
---

## Propósito

Diseñar e implementar APIs GraphQL correctas, eficientes y seguras: schema primero, resolvers sin N+1, paginación cursor-based, autenticación y errores consistentes en múltiples lenguajes.

## Objetivo

1. ¿Cómo se diseña el schema GraphQL (tipos, queries, mutations, subscriptions)?
2. ¿Cómo se evita el problema N+1 en resolvers?
3. ¿Cómo se implementa paginación cursor-based según la especificación Relay?
4. ¿Cómo se maneja autenticación y autorización en GraphQL?
5. ¿Cómo se estructuran errores y excepciones?
6. ¿Cómo se implementan suscripciones en tiempo real?

## Relación con otras skills

- `backend-api` comparte patrones de respuesta y estructura de proyecto.
- `security` provee autenticación, autorización y rate limiting aplicables a GraphQL.
- `error-handling` define el formato de errores que GraphQL debe adoptar en `errors` array.
- `performance` aporta DataLoader y caché para resolver N+1.

## Qué debe hacer el agente

1. Diseñar schema primero (SDL). El schema es el contrato, no la implementación.
2. Usar DataLoader para batching de acceso a datos y evitar N+1.
3. Implementar paginación cursor-based con `Connection`/`Edge`/`PageInfo`.
4. Centralizar autenticación en contexto global del request.
5. Estructurar errores con `extensions.code` categorizado para el frontend.
6. Usar input types dedicados para mutaciones, no argumentos sueltos.
7. Implementar subscriptions solo cuando haya eventos reales del servidor.
8. Deprecar campos con `@deprecated` en lugar de romper el schema.

## Alcance

Incluye: schema design, resolvers, DataLoader, paginación, auth (Keycloak/OAuth2), errores, subscriptions, testing, consumo frontend con Apollo Client (React) o Apollo Angular (Angular), según el framework elegido por el proyecto.
No incluye: federación Apollo, GraphQL Mesh, schema stitching, BFF vs gateway decisions.

## Principios

- Schema-first: el schema SDL es el contrato, no el código del resolver.
- Un resolver no debe hacer más de una llamada a DB. Si lo hace, usa DataLoader.
- Las mutaciones devuelven el tipo mutado. Siempre. No scalars.
- Input types reutilizables, no argumentos planos.
- Los errores de negocio van en `errors[]`, no en `null` data.
- Las queries expuestas deben tener límite de profundidad o cantidad.

## Technical Design

### Schema SDL

```graphql
type Query {
  user(id: ID!): User
  users(first: Int!, after: String): UserConnection!
}
type Mutation {
  createUser(input: CreateUserInput!): CreateUserPayload!
}
type User {
  id: ID!
  name: String!
  posts(first: Int!, after: String): PostConnection!
}
```

### DataLoader (Bun + graphql-yoga)

```typescript
import DataLoader from "@dataloader/core";
import { createYoga, createSchema } from "graphql-yoga";
import { db } from "../db/client"; // Bun.sql o pg client

// 1) Batch loader: una sola query para N ids
const userLoader = new DataLoader<number, User | null>(async (ids) => {
  const users = await db`
    SELECT * FROM users WHERE id = ANY(${ids as number[]})
  `;
  const lookup = new Map(users.map((u) => [u.id, u]));
  return ids.map((id) => lookup.get(id) ?? null);
});

// 2) Yoga context inyecta el loader por request (caching aislado)
export const yoga = createYoga<{ user?: AuthUser }>({
  schema: createSchema({
    typeDefs: /* GraphQL */ `
      type Query {
        user(id: ID!): User
        users(first: Int!, after: String): UserConnection!
      }
      type User {
        id: ID!
        name: String!
        posts(first: Int!, after: String): PostConnection!
      }
    `,
    resolvers: {
      Query: {
        user: async (_, { id }, ctx) => ctx.loaders.user.load(Number(id)),
      },
      User: {
        posts: async (parent, { first, after }, ctx) =>
          ctx.loaders.postsByUserId.load(parent.id),
      },
    },
  }),
  context: (req) => ({
    user: req.request.headers.get("authorization")
      ? verifyJwt(req.request.headers.get("authorization")!)
      : undefined,
    loaders: {
      user: userLoader, // nuevo DataLoader por request si se quiere aislar cache
      postsByUserId: new DataLoader<number, Post[]>(async (ids) => {
        const rows = await db`
          SELECT * FROM posts WHERE author_id = ANY(${ids as number[]})
          ORDER BY created_at DESC
        `;
        return ids.map((id) => rows.filter((p) => p.author_id === id));
      }),
    },
  }),
});
```

Notas Bun:
- `@dataloader/core` es compatible con Bun (sin polyfills).
- `graphql-yoga` corre nativamente en Bun sin adaptadores.
- Cada loader debe crearse por request cuando se quiere aislar la caché entre usuarios (multi-tenant).
- Usar `Bun.serve({ fetch: yoga.fetch })` o montar dentro de Hono/Elysia.

### DataLoader (Python + Strawberry)

```python
from strawberry.dataloader import DataLoader

async def load_users(ids: list[int]) -> list[User | None]:
    users = await db.fetch("SELECT * FROM users WHERE id = ANY($1)", ids)
    lookup = {u["id"]: u for u in users}
    return [lookup.get(i) for i in ids]

user_loader = DataLoader(load_fn=load_users)
```

### Paginación cursor-based (Relay)

```graphql
type UserConnection {
  edges: [UserEdge!]!
  pageInfo: PageInfo!
}
type UserEdge {
  node: User!
  cursor: String!
}
type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}
```

### Auth in resolvers (Keycloak / OAuth2)

Patrón común: validar el JWT de Keycloak en el contexto del request y exponer `ctx.user` a los resolvers. La autorización fina (RBAC/ABAC) se hace en el resolver con guards.

```typescript
// Bun + graphql-yoga: middleware de auth Keycloak/OAuth2
import { createYoga } from "graphql-yoga";
import jwt from "jose";

const KEYCLOAK_JWKS = createRemoteJWKSet(
  new URL(`${process.env.KEYCLOAK_URL}/realms/${process.env.KEYCLOAK_REALM}/protocol/openid-connect/certs`)
);

async function verifyToken(authHeader: string | null) {
  if (!authHeader?.startsWith("Bearer ")) return undefined;
  const token = authHeader.slice(7);
  try {
    const { payload } = await jwtVerify(token, KEYCLOAK_JWKS, {
      issuer: `${process.env.KEYCLOAK_URL}/realms/${process.env.KEYCLOAK_REALM}`,
    });
    return payload as { sub: string; tenant_id?: string; realm_access?: { roles: string[] } };
  } catch {
    return undefined; // 401 lo maneja el guard del resolver
  }
}

export const yoga = createYoga({
  schema,
  context: async ({ request }) => ({
    user: await verifyToken(request.headers.get("authorization")),
    requireRole: (role: string) => {
      if (!ctx.user?.realm_access?.roles.includes(role)) {
        throw new GraphQLError("Forbidden", { extensions: { code: "FORBIDDEN" } });
      }
    },
  }),
});

// Resolver con guard
const resolvers = {
  Query: {
    adminUsers: async (_, __, ctx) => {
      ctx.requireRole("admin");
      return listUsers(ctx);
    },
  },
};
```

```python
# Python + Strawberry: auth Keycloak/OAuth2 con PyJWT
import jwt
from jwt import PyJWKSet
from fastapi import Request
import strawberry
from strawberry.types import Info

KEYCLOAK_URL = os.getenv("KEYCLOAK_URL")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM")
JWKS_URL = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/certs"

async def get_current_user(request: Request) -> dict | None:
    auth = request.headers.get("authorization")
    if not auth or not auth.startswith("Bearer "):
        return None
    token = auth.split(" ", 1)[1]
    try:
        # Validar firma contra JWKS de Keycloak (PyJWT selecciona la key por kid)
        jwks = await fetch_jwks(JWKS_URL)
        signing_key = PyJWKSet.from_dict(jwks).get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token, signing_key.key,
            issuer=f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}",
            algorithms=["RS256"],
        )
        return payload  # { sub, tenant_id, realm_access: { roles: [...] } }
    except (jwt.InvalidTokenError, StopIteration):
        return None

@strawberry.type
class Query:
    @strawberry.field(permission_classes=[IsAuthenticated])
    async def me(self, info: Info) -> User:
        user = info.context["user"]
        return await get_user(user["sub"])

    @strawberry.field
    async def admin_users(self, info: Info) -> list[User]:
        user = info.context["user"]
        if "admin" not in (user.get("realm_access", {}).get("roles", [])):
            raise Exception("Forbidden")  # mapeado a extensions.code=FORBIDDEN
        return await list_users()
```

### Frontend: Apollo Client (React) (consumo de GraphQL)

`@apollo/client` es el cliente GraphQL estándar para React. Integración con Keycloak vía `ApolloLink` que inyecta el Bearer token.

```tsx
// core/graphql/apollo-client.ts — registro de Apollo en React
import { ApolloClient, InMemoryCache, HttpLink, ApolloLink } from "@apollo/client";
import { relayStylePagination } from "@apollo/client/utilities";
import { useAuthStore } from "../auth/auth.store";

const httpLink = new HttpLink({ uri: "/graphql" });

const authLink = new ApolloLink((operation, forward) => {
  const token = useAuthStore.getState().accessToken;
  operation.setContext({
    headers: { ...(token ? { Authorization: `Bearer ${token}` } : {}) },
  });
  return forward(operation);
});

export const apolloClient = new ApolloClient({
  link: authLink.concat(httpLink),
  cache: new InMemoryCache({
    typePolicies: {
      User: {
        fields: {
          posts: relayStylePagination(), // paginación cursor-based en cache
        },
      },
    },
  }),
});
```

```tsx
// main.tsx — provider en la raíz de la app
import { ApolloProvider } from "@apollo/client";
import { apolloClient } from "./core/graphql/apollo-client";

<ApolloProvider client={apolloClient}>
  <App />
</ApolloProvider>;
```

```typescript
// users.queries.ts — queries tipadas con codegen (@graphql-codegen/cli)
import { gql } from "@apollo/client";

export const GET_USERS = gql`
  query Users($first: Int!, $after: String) {
    users(first: $first, after: $after) {
      edges {
        node { id name }
        cursor
      }
      pageInfo { hasNextPage endCursor }
    }
  }
`;

export const CREATE_USER = gql`
  mutation CreateUser($input: CreateUserInput!) {
    createUser(input: $input) {
      id name
    }
  }
`;
```

```tsx
// UsersList.tsx — hooks generados (useUsersQuery / useCreateUserMutation)
import { useQuery, useMutation } from "@apollo/client";
import { GET_USERS, CREATE_USER } from "./users.queries";

export function UsersList() {
  const { data, fetchMore } = useQuery(GET_USERS, {
    variables: { first: 20 },
    fetchPolicy: "cache-and-network",
  });
  const [createUser] = useMutation(CREATE_USER, {
    update: (cache) => {
      cache.modify({ fields: { users: (existing) => existing } });
    },
  });

  const edges = data?.users?.edges ?? [];
  const hasNext = data?.users?.pageInfo?.hasNextPage;

  const loadMore = () => {
    fetchMore({
      variables: { after: data?.users?.pageInfo?.endCursor },
    });
  };

  return (
    <>
      {edges.map((edge) => (
        <div key={edge.node.id}>{edge.node.name}</div>
      ))}
      <button onClick={loadMore} disabled={!hasNext}>Cargar más</button>
    </>
  );
}
```

### Frontend: Apollo Angular (consumo de GraphQL)

Apollo Angular es el cliente GraphQL estándar para Angular. Integración con Keycloak vía interceptor HTTP que inyecta el Bearer token.

```typescript
// app.config.ts — registro de Apollo en standalone Angular
import { ApplicationConfig } from "@angular/core";
import { provideApollo } from "apollo-angular";
import { HttpLink } from "apollo-angular/http";
import { InMemoryCache } from "@apollo/client/core";
import { provideHttpClient, withInterceptors } from "@angular/common/http";
import { keycloakAuthInterceptor } from "./core/auth/keycloak.interceptor";

export const appConfig: ApplicationConfig = {
  providers: [
    provideHttpClient(withInterceptors([keycloakAuthInterceptor])),
    provideApollo(() => {
      const httpLink = inject(HttpLink);
      return {
        link: httpLink.create({ uri: "/graphql" }),
        cache: new InMemoryCache({
          typePolicies: {
            User: {
              fields: {
                posts: relayStylePagination(), // paginación cursor-based en cache
              },
            },
          },
        }),
      };
    }),
  ],
};
```

```typescript
// keycloak.interceptor.ts — inyecta Bearer token de Keycloak
import { HttpInterceptorFn } from "@angular/common/http";
import { inject } from "@angular/core";
import { KeycloakService } from "keycloak-js";

export const keycloakAuthInterceptor: HttpInterceptorFn = (req, next) => {
  const kc = inject(KeycloakService);
  if (!kc.authenticated) return next(req);
  const cloned = req.clone({
    setHeaders: { Authorization: `Bearer ${kc.token}` },
  });
  return next(cloned);
};
```

```typescript
// users.query.ts — queries tipadas con codegen
import { gql } from "apollo-angular";

export const GET_USERS = gql`
  query Users($first: Int!, $after: String) {
    users(first: $first, after: $after) {
      edges {
        node { id name }
        cursor
      }
      pageInfo { hasNextPage endCursor }
    }
  }
`;

export const CREATE_USER = gql`
  mutation CreateUser($input: CreateUserInput!) {
    createUser(input: $input) {
      id name
    }
  }
`;
```

```typescript
// users.service.ts — uso con signals (Angular 17+)
import { Injectable, inject, signal } from "@angular/core";
import { Apollo } from "apollo-angular";
import { toSignal } from "@angular/core/rxjs-interop";
import { GET_USERS, CREATE_USER } from "./users.query";

@Injectable({ providedIn: "root" })
export class UsersService {
  private apollo = inject(Apollo);

  // Observable → signal reactivo
  users = toSignal(
    this.apollo.watchQuery({
      query: GET_USERS,
      variables: { first: 20 },
      fetchPolicy: "cache-and-network",
    }).valueChanges,
    { initialValue: null }
  );

  create(input: CreateUserInput) {
    return this.apollo.mutate({
      mutation: CREATE_USER,
      variables: { input },
      // Actualización optimista del cache
      update: (cache, { data }) => {
        cache.modify({
          fields: {
            users: (existing) => ({ ...existing }),
          },
        });
      },
    });
  }
}
```

```typescript
// users.component.ts — componente standalone
import { Component, inject } from "@angular/core";
import { UsersService } from "./users.service";

@Component({
  selector: "app-users",
  standalone: true,
  template: `
    @for (edge of svc.users()?.data?.users?.edges ?? []; track edge.node.id) {
      <div>{{ edge.node.name }}</div>
    }
    <button (click)="loadMore()" [disabled]="!hasNext">Cargar más</button>
  `,
})
export class UsersComponent {
  svc = inject(UsersService);
  get hasNext() {
    return this.svc.users()?.data?.users?.pageInfo?.hasNextPage;
  }
  loadMore() {
    // Apollo fetchMore con cursor-based pagination
  }
}
```

### Error format

```json
{
  "data": { "createUser": null },
  "errors": [{
    "message": "Email already exists",
    "extensions": { "code": "CONFLICT", "field": "email" }
  }]
}
```

## Preguntas guía

- ¿El schema refleja el dominio o la base de datos?
- ¿Cada resolver accede a DB una sola vez?
- ¿Las listas tienen paginación cursor-based o están desprotegidas?
- ¿Las mutaciones reciben `input` y devuelven `payload`?
- ¿La autenticación se valida en contexto de request?

## Salidas esperadas

- Schema SDL completo (types, queries, mutations, subscriptions).
- Resolvers con DataLoader registrados.
- Paginación cursor-based en todas las listas.
- Mutaciones con input/payload types.
- Middleware de autenticación y error handling.

## Criterios de calidad

- 0 queries N+1 en resolvers (verificable con logging de consultas SQL).
- Paginación obligatoria en toda lista con `first`/`after`.
- Errores con `extensions.code` categorizado.
- Input types reutilizados, no argumentos duplicados.

## Comportamiento esperado del agente

Cuando se detecte un resolver con múltiples queries SQL en un loop, el agente debe introducir DataLoader.
Cuando una lista no tenga paginación, debe agregar cursor-based pagination.
Cuando una mutación exponga argumentos planos, debe crear un `input` type.
Cuando un error de negocio devuelva `null` sin código, debe estructurarlo en `extensions`.

## Plantilla de respuesta

```
1. Schema SDL (types, queries, mutations, subscriptions).
2. DataLoader registration per entity.
3. Pagination on all list fields.
4. Auth middleware / resolver guard.
5. Error format with extensions.code.
6. Test cases for N+1 and auth.
```

## Ejemplos

### N+1 detection

```
Query: { users { posts { title } } }
Without DataLoader: 1 query for users + N queries for posts.
With DataLoader: 1 query for users + 1 batch query for posts.
```

### Subscription

```graphql
type Subscription {
  postCreated: Post!
}
```
```typescript
// Bun + graphql-yoga: subscription con pub/sub (Redis backplane para escalar)
import { createYoga, createSchema } from "graphql-yoga";
import { PubSub } from "graphql-subscriptions";

const pubsub = new PubSub();

// Resolver de subscription
const resolvers = {
  Subscription: {
    postCreated: () => pubsub.asyncIterator("POST_CREATED"),
  },
  Mutation: {
    createPost: async (_, { input }, ctx) => {
      const post = await db`INSERT INTO posts ${db(input)} RETURNING *`;
      pubsub.publish("POST_CREATED", { postCreated: post[0] });
      return post[0];
    },
  },
};

// Para multi-tenant: filtrar por tenant_id en el canal
// pubsub.asyncIterator(`POST_CREATED:${ctx.user.tenant_id}`)
```
```python
# Python + Strawberry: subscription con pub/sub
import strawberry
from strawberry.subscriptions import GRAPHQLWS

@strawberry.type
class Subscription:
    @strawberry.subscription
    async def post_created(self, info: Info) -> Post:
        async for post in pubsub.subscribe("POST_CREATED"):
            yield post
```

## Checklist

- [ ] Schema diseñado SDL-first.
- [ ] DataLoader para cada entidad con acceso a DB en resolvers.
- [ ] Paginación cursor-based (Relay) en todas las listas.
- [ ] Input types para todas las mutaciones.
- [ ] Payload types con el objeto mutado.
- [ ] `@deprecated` en campos obsoletos.
- [ ] Auth check en contexto de request.
- [ ] Error format con `extensions.code`.
- [ ] Profundidad máxima de query configurada.
- [ ] Subscription implementada solo si hay eventos reales.
