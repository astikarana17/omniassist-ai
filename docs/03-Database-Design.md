# OmniAssist AI — Database Design & ER Diagram

> Phase 1 · v1.0 · Target: Supabase PostgreSQL (project `pfcfrberlamzpopmbthr`)
> Extensions used: `uuid-ossp`, `pgcrypto`, `vector` (pgvector 0.8.0), `pg_trgm`, `pgmq`, `pg_cron`.
> **Multi-tenancy:** every business table carries `org_id` + Row-Level Security.

## 1. ER Diagram

```mermaid
erDiagram
    ORGANIZATIONS ||--o{ USERS : has
    ORGANIZATIONS ||--o{ MEMBERSHIPS : has
    USERS ||--o{ MEMBERSHIPS : in
    ROLES ||--o{ MEMBERSHIPS : assigned
    ORGANIZATIONS ||--o{ CHANNELS : configures
    ORGANIZATIONS ||--o{ CONTACTS : owns
    ORGANIZATIONS ||--o{ CONVERSATIONS : owns
    CONTACTS ||--o{ CONVERSATIONS : starts
    CHANNELS ||--o{ CONVERSATIONS : via
    CONVERSATIONS ||--o{ MESSAGES : contains
    CONVERSATIONS ||--o{ TICKETS : spawns
    USERS ||--o{ TICKETS : assigned
    CONVERSATIONS ||--o{ HANDOFFS : triggers
    USERS ||--o{ HANDOFFS : receives
    ORGANIZATIONS ||--o{ KB_DOCUMENTS : owns
    KB_DOCUMENTS ||--o{ KB_CHUNKS : split_into
    ORGANIZATIONS ||--o{ AI_AGENTS : configures
    AI_AGENTS ||--o{ AGENT_RUNS : executes
    CONVERSATIONS ||--o{ AGENT_RUNS : for
    MESSAGES ||--o{ SENTIMENTS : analyzed
    TICKETS ||--o{ TICKET_SUMMARIES : summarized
    CONVERSATIONS ||--o{ FEEDBACK : rated
    ORGANIZATIONS ||--o{ AUDIT_LOGS : records
    ORGANIZATIONS ||--o{ NOTIFICATIONS : sends
    ORGANIZATIONS ||--o{ ANALYTICS_DAILY : rolls_up
    ORGANIZATIONS ||--o{ API_KEYS : issues

    ORGANIZATIONS {
        uuid id PK
        text name
        text slug
        text plan
        jsonb settings
        timestamptz created_at
    }
    USERS {
        uuid id PK
        text email
        text full_name
        text avatar_url
        text auth_provider
        timestamptz created_at
    }
    ROLES {
        uuid id PK
        text key
        text name
        jsonb permissions
    }
    MEMBERSHIPS {
        uuid id PK
        uuid org_id FK
        uuid user_id FK
        uuid role_id FK
        text status
        timestamptz created_at
    }
    CHANNELS {
        uuid id PK
        uuid org_id FK
        text type
        text name
        jsonb config
        uuid secret_ref
        boolean enabled
    }
    CONTACTS {
        uuid id PK
        uuid org_id FK
        text external_id
        text name
        text email
        text phone
        jsonb attributes
    }
    CONVERSATIONS {
        uuid id PK
        uuid org_id FK
        uuid contact_id FK
        uuid channel_id FK
        text status
        text assignee_type
        uuid assignee_id
        text language
        timestamptz last_message_at
        timestamptz created_at
    }
    MESSAGES {
        uuid id PK
        uuid org_id FK
        uuid conversation_id FK
        text sender_type
        uuid sender_id
        text content
        jsonb attachments
        jsonb meta
        timestamptz created_at
    }
    TICKETS {
        uuid id PK
        uuid org_id FK
        uuid conversation_id FK
        text subject
        text status
        text priority
        uuid assignee_id FK
        text[] tags
        timestamptz sla_due_at
        timestamptz created_at
    }
    HANDOFFS {
        uuid id PK
        uuid org_id FK
        uuid conversation_id FK
        text reason
        uuid to_user_id FK
        text status
        timestamptz created_at
    }
    KB_DOCUMENTS {
        uuid id PK
        uuid org_id FK
        text title
        text source_type
        text source_url
        text status
        timestamptz created_at
    }
    KB_CHUNKS {
        uuid id PK
        uuid org_id FK
        uuid document_id FK
        text content
        vector embedding
        text pinecone_id
        jsonb meta
    }
    AI_AGENTS {
        uuid id PK
        uuid org_id FK
        text type
        text name
        text system_prompt
        jsonb tools
        jsonb config
        boolean enabled
    }
    AGENT_RUNS {
        uuid id PK
        uuid org_id FK
        uuid agent_id FK
        uuid conversation_id FK
        jsonb graph_state
        numeric confidence
        int input_tokens
        int output_tokens
        timestamptz created_at
    }
    SENTIMENTS {
        uuid id PK
        uuid org_id FK
        uuid message_id FK
        text label
        numeric score
    }
    TICKET_SUMMARIES {
        uuid id PK
        uuid org_id FK
        uuid ticket_id FK
        text summary
        text resolution
        text[] next_steps
    }
    FEEDBACK {
        uuid id PK
        uuid org_id FK
        uuid conversation_id FK
        uuid message_id FK
        text type
        int rating
        text comment
    }
    AUDIT_LOGS {
        uuid id PK
        uuid org_id FK
        uuid actor_id
        text action
        text resource_type
        uuid resource_id
        jsonb diff
        inet ip
        timestamptz created_at
    }
    NOTIFICATIONS {
        uuid id PK
        uuid org_id FK
        text channel
        text event
        jsonb payload
        text status
    }
    ANALYTICS_DAILY {
        uuid id PK
        uuid org_id FK
        date day
        text channel
        int conversations
        int ai_resolved
        int handoffs
        numeric avg_csat
        numeric avg_frt_seconds
    }
    API_KEYS {
        uuid id PK
        uuid org_id FK
        text name
        text hashed_key
        text[] scopes
        timestamptz last_used_at
    }
```

## 2. Table Catalog (purpose + notes)

| Table | Purpose | Notes |
|-------|---------|-------|
| `organizations` | Tenant root | `plan` drives limits; `settings` jsonb |
| `users` | Global identity | Linked to Supabase Auth `auth.users.id` |
| `roles` | RBAC roles | Seeded: owner, admin, agent, viewer |
| `memberships` | user↔org↔role | A user can belong to many orgs |
| `channels` | Channel config | `type` ∈ web, whatsapp, email, voice; secret in Vault |
| `contacts` | End customers | Dedup by email/phone/external_id |
| `conversations` | Thread of messages | `status` ∈ open, pending, resolved, snoozed |
| `messages` | Individual messages | `sender_type` ∈ contact, ai, agent, system |
| `tickets` | Work items | SLA timers, priority, assignment |
| `handoffs` | AI→human events | Carries reason + context pointer |
| `kb_documents` | KB sources | upload/crawl/faq; status: processing/ready/failed |
| `kb_chunks` | Embedded chunks | `embedding vector(1536/3072)` + `pinecone_id` |
| `ai_agents` | Agent configs | support/sales; prompt + tools + model config |
| `agent_runs` | Each AI turn | tokens, confidence, graph state for replay/handoff |
| `sentiments` | Per-message sentiment | label + score |
| `ticket_summaries` | AI summaries | on close/handoff |
| `feedback` | Thumbs + CSAT | per message/conversation |
| `audit_logs` | Immutable audit | append-only; no UPDATE/DELETE |
| `notifications` | Outbound events | slack/email; status queued/sent/failed |
| `analytics_daily` | Pre-aggregated metrics | filled by `pg_cron` rollup |
| `api_keys` | Tenant API access | hashed; scopes |

## 3. Key Design Decisions

1. **UUID PKs** (`uuid_generate_v4()`), `created_at timestamptz default now()` everywhere.
2. **`org_id` on every business table** + **RLS** policy `org_id = auth.jwt() ->> 'org_id'`.
3. **Vector storage dual-path:**
   - `kb_chunks.embedding vector(N)` with **HNSW** index for pgvector tier.
   - `kb_chunks.pinecone_id` references the same chunk in Pinecone (namespace = `org_id`).
4. **Soft delete** via `deleted_at` on content tables; audit logs are hard-append-only.
5. **Indexes:** `conversations(org_id, status, last_message_at)`, `messages(conversation_id, created_at)`, `tickets(org_id, status, sla_due_at)`, `kb_chunks` HNSW + `pinecone_id`, `pg_trgm` on `contacts(name,email)`.
6. **Enums** implemented as `text` + `CHECK` constraints (easier migrations than PG enums).

## 4. RLS Policy Pattern (illustrative, not executed yet)

```sql
-- Example only — applied via migrations in Phase 2
alter table conversations enable row level security;

create policy tenant_isolation_select on conversations
  for select using (org_id = (auth.jwt() ->> 'org_id')::uuid);

create policy tenant_isolation_mod on conversations
  for all using (org_id = (auth.jwt() ->> 'org_id')::uuid)
          with check (org_id = (auth.jwt() ->> 'org_id')::uuid);
```

## 5. Vector Index (pgvector tier, illustrative)

```sql
create index on kb_chunks using hnsw (embedding vector_cosine_ops);
```

## 6. Migration Strategy

- Managed via **Supabase migrations** (`supabase/migrations/*.sql`), applied with `apply_migration` MCP tool in Phase 2.
- One migration per logical group: `0001_core_tenancy`, `0002_channels_contacts`, `0003_conversations_messages`, `0004_tickets_handoffs`, `0005_kb_vectors`, `0006_ai_agents_runs`, `0007_analytics_audit`, `0008_rls_policies`, `0009_seed_roles`.
