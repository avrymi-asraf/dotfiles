# Architecture Analysis Guide

Use this when performing deep reconnaissance of a codebase.

## Preferred order of inspection

1. **Manifests & entry points**
   - package.json / pyproject.toml / go.mod / Cargo.toml / pom.xml / build.gradle
   - README, CONTRIBUTING, ARCHITECTURE.md, docs/
   - main.ts / main.py / index.js / cmd/ / app.py / server.go
   - Dockerfile, docker-compose, k8s manifests, terraform, pulumi

2. **Boundary discovery**
   - Public API surface (routers, controllers, handlers, GraphQL schema, OpenAPI)
   - Auth & identity (middleware, guards, JWT, session, OAuth)
   - Data layer (models, repositories, ORMs, migrations, SQL schemas)
   - External integrations (HTTP clients, SDKs, message queues, third-party services)
   - Background work (workers, cron, queues, event handlers)
   - Frontend / clients (if present in the same repo)

3. **Relationship extraction**
   - Direct calls and imports that cross module boundaries
   - Shared data stores or event buses
   - Config that wires services together
   - Deployment topology that implies runtime relationships

4. **Flow selection criteria**
   Prefer flows that are:
   - Frequently executed (happy path of core features)
   - Architecturally interesting (cross multiple layers or services)
   - Risky or complex (auth, payments, build/deploy, data consistency)
   - Documented or implied by product features

Avoid pure internal utility chains or one-off admin scripts unless they are central.

## Node granularity rules

- Prefer **services / bounded contexts / major packages** over individual functions.
- Promote a function to a node only if it is a clear architectural boundary (e.g. a public API endpoint that many things call, or a critical adapter).
- Collapse pure implementation details (helpers, private methods) into their parent.
- Always include external systems the code depends on (Stripe, S3, Auth0, etc.) as explicit nodes of type `external`.

## Edge labels that work well

calls, invokes, reads, writes, queries, publishes, subscribes, authenticates, authorizes, deploys, builds, triggers, depends-on, streams-to, caches, validates

Keep labels short and consistent.

## Common layer / group names

Client Surfaces · Frontend · API Gateway · Auth · Core Services · Domain · Workers · Background · Data · Storage · Cache · Messaging · Infrastructure · Distribution · Build Pipeline · External Services

Choose 4–8 groups that create a clean left-to-right or top-to-bottom mental model.
