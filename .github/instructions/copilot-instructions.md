# LocuSum — Copilot Instructions (Project-Specific)

Source of truth
- Read docs/dev-plan.md first. It defines stack, APIs, DB models, real-time strategy, and testing/security requirements used across the codebase.

Architecture (big picture)
- Frontend: Next.js 14 (TS, App Router), Tailwind + shadcn/ui, Zustand. Real-time: Socket.io client for chat; SSE/WebSocket relay for AI streaming.
- Backend: NestJS (Fastify adapter, TS). Real-time: Socket.io (chat), SSE/WebSocket relay (AI).
- DB: PostgreSQL + Prisma. Use keyset pagination for messages, pgvector for embeddings/RAG, consider partitioning Message at scale.
- Auth: NextAuth.js. Infra: Vercel (web), Railway/Render (API), Supabase Postgres/Storage.

Key domain models (Prisma)
- User, Group, GroupMember(@@unique([groupId,userId])), Message(self-relation for threads via threadParentId).
- Message pagination is keyset-based (before=<messageId>&limit=50). Preserve stable ordering by createdAt/ID and proper indexes.
- Prepare pgvector indexes (ivfflat/hnsw) where embeddings are stored (e.g., message summaries or knowledge docs).

API surface (reflect docs/dev-plan.md)
- Groups: GET/POST /api/groups, GET /api/groups/[id], POST /api/groups/[id]/invite, POST /api/invite/[token]
- Messages: GET /api/groups/[id]/messages (keyset), POST /api/groups/[id]/messages, POST /api/groups/[id]/ai/ask (non-stream)
- AI: POST /api/ai/process (non-stream), GET /api/groups/[id]/ai/stream (SSE; fallback WS relay), GET/POST /api/ai/settings/[groupId]

Real-time patterns
- Chat uses Socket.io rooms per group (room key typically group:<id>). Join on entering a chat; leave on exit.
- AI responses are streamed via SSE endpoint; if SSE not available, bridge via a WS relay channel.

AI integration and limits
- Provider: OpenRouter. Implement retries/circuit breaker per docs/dev-plan.md risks.
- Track token usage per user/group; enforce soft limits (disable AI when exceeded). Persist counters in DB; wrap AI calls with accounting middleware.
- Provide AI typing indicators and streamed deltas to client.

Developer workflows (adjust script names to package.json)
- Install: pnpm i (or npm ci)
- DB: npx prisma generate && npx prisma migrate dev
- Web (Next): next dev
- API (Nest + Fastify): nest start --watch
- Env: set OPENROUTER_API_KEY, DATABASE_URL, NEXTAUTH_SECRET, SUPABASE_URL, SUPABASE_ANON_KEY (use Vault/Doppler/GitHub Secrets; no secrets in repo/logs)

Testing strategy
- Integration tests should run against a mock OpenRouter server; point OPENROUTER_BASE_URL to the mock.
- Load tests for concurrent users; verify Socket.io reconnect and SSE backoff behavior.
- Validate keyset pagination (boundary cases: empty, first page, mid-stream insert).

Security and compliance
- Input validation/sanitization on API. Rate limiting on auth, messages, AI calls.
- PII redaction in logs (mask emails/IDs/content snippets). Use structured logging with filters.
- Encrypt data at rest where applicable. Rotate secrets via Vault/Doppler/GitHub Secrets.

Performance notes
- Prefer keyset over offset pagination for messages. Add composite indexes on (groupId, createdAt, id).
- Profile hot queries; ensure connection pooling. Consider partitioning Message by group/time at scale.

Conventions
- TypeScript strict, ESLint + Prettier. shadcn/ui for components, Zustand for lightweight chat state.
- Keep endpoints and event names aligned with docs/dev-plan.md; avoid inventing new patterns without updating the doc.

Where to look first
- docs/dev-plan.md (definitions)
- Prisma schema and API route handlers (models/endpoints)
- Real-time gateway (Socket.io) and AI stream controller (SSE)
