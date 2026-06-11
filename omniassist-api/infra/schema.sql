-- OmniAssist AI — schema DDL (generated from models)

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "vector";

CREATE TABLE organizations (
	name VARCHAR(160) NOT NULL, 
	slug VARCHAR(80) NOT NULL, 
	plan VARCHAR(40) NOT NULL, 
	brand_color VARCHAR(9) NOT NULL, 
	settings JSONB NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_organizations PRIMARY KEY (id)
);
CREATE UNIQUE INDEX ix_organizations_slug ON organizations (slug);

CREATE TABLE users (
	email VARCHAR(255) NOT NULL, 
	full_name VARCHAR(160) NOT NULL, 
	hashed_password VARCHAR(255), 
	avatar_url VARCHAR(512), 
	title VARCHAR(120), 
	auth_provider VARCHAR(20) NOT NULL, 
	google_sub VARCHAR(64), 
	is_active BOOLEAN NOT NULL, 
	is_email_verified BOOLEAN NOT NULL, 
	is_superuser BOOLEAN NOT NULL, 
	mfa_enabled BOOLEAN NOT NULL, 
	last_login_at TIMESTAMP WITH TIME ZONE, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_users PRIMARY KEY (id)
);
CREATE INDEX ix_users_google_sub ON users (google_sub);
CREATE UNIQUE INDEX ix_users_email ON users (email);

CREATE TABLE ai_agents (
	org_id UUID NOT NULL, 
	type VARCHAR(20) NOT NULL, 
	name VARCHAR(120) NOT NULL, 
	system_prompt TEXT NOT NULL, 
	model VARCHAR(60) NOT NULL, 
	temperature FLOAT NOT NULL, 
	tone VARCHAR(40) NOT NULL, 
	confidence_threshold INTEGER NOT NULL, 
	tools JSONB NOT NULL, 
	languages JSONB NOT NULL, 
	config JSONB NOT NULL, 
	enabled BOOLEAN NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_ai_agents PRIMARY KEY (id), 
	CONSTRAINT fk_ai_agents_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE
);
CREATE INDEX ix_ai_agents_org_type ON ai_agents (org_id, type);

CREATE TABLE analytics_daily (
	org_id UUID NOT NULL, 
	day DATE NOT NULL, 
	channel VARCHAR(20) NOT NULL, 
	conversations INTEGER NOT NULL, 
	ai_resolved INTEGER NOT NULL, 
	handoffs INTEGER NOT NULL, 
	tickets_created INTEGER NOT NULL, 
	tickets_resolved INTEGER NOT NULL, 
	leads_created INTEGER NOT NULL, 
	revenue_influenced NUMERIC(12, 2) NOT NULL, 
	avg_csat FLOAT, 
	avg_frt_seconds FLOAT, 
	sentiment_breakdown JSONB NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_analytics_daily PRIMARY KEY (id), 
	CONSTRAINT uq_analytics_org_day_channel UNIQUE (org_id, day, channel), 
	CONSTRAINT fk_analytics_daily_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE
);
CREATE INDEX ix_analytics_org_day ON analytics_daily (org_id, day);

CREATE TABLE api_keys (
	org_id UUID NOT NULL, 
	name VARCHAR(80) NOT NULL, 
	prefix VARCHAR(20) NOT NULL, 
	hashed_key VARCHAR(128) NOT NULL, 
	scopes VARCHAR[] NOT NULL, 
	last_used_at TIMESTAMP WITH TIME ZONE, 
	revoked BOOLEAN NOT NULL, 
	created_by UUID, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_api_keys PRIMARY KEY (id), 
	CONSTRAINT fk_api_keys_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE
);
CREATE UNIQUE INDEX ix_api_keys_hashed_key ON api_keys (hashed_key);
CREATE INDEX ix_api_keys_org ON api_keys (org_id);

CREATE TABLE audit_logs (
	org_id UUID, 
	actor_id UUID, 
	actor_name VARCHAR(160), 
	action VARCHAR(80) NOT NULL, 
	resource_type VARCHAR(60) NOT NULL, 
	resource_id VARCHAR(80), 
	detail TEXT, 
	diff JSONB NOT NULL, 
	ip_address INET, 
	user_agent VARCHAR(400), 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_audit_logs PRIMARY KEY (id), 
	CONSTRAINT fk_audit_logs_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE
);
CREATE INDEX ix_audit_logs_resource ON audit_logs (resource_type, resource_id);
CREATE INDEX ix_audit_logs_org_created ON audit_logs (org_id, created_at);
CREATE INDEX ix_audit_logs_actor ON audit_logs (actor_id);

CREATE TABLE business_impact_metrics (
	org_id UUID NOT NULL, 
	period_start DATE NOT NULL, 
	period_end DATE NOT NULL, 
	granularity VARCHAR(12) NOT NULL, 
	ai_resolution_rate NUMERIC(5, 2), 
	cost_savings_usd NUMERIC(14, 2), 
	revenue_influenced_usd NUMERIC(14, 2), 
	churn_reduction_pct NUMERIC(5, 2), 
	agent_productivity NUMERIC(8, 2), 
	customer_retention_pct NUMERIC(5, 2), 
	tickets_handled INTEGER, 
	tickets_ai_resolved INTEGER, 
	avg_first_response_min NUMERIC(8, 2), 
	csat_avg NUMERIC(4, 2), 
	details JSONB NOT NULL, 
	computed_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_business_impact_metrics PRIMARY KEY (id), 
	CONSTRAINT uq_business_impact_org_period UNIQUE (org_id, period_start, period_end, granularity), 
	CONSTRAINT fk_business_impact_metrics_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE
);
CREATE INDEX ix_business_impact_org ON business_impact_metrics (org_id, period_start);

CREATE TABLE company_profiles (
	org_id UUID NOT NULL, 
	overview TEXT, 
	mission TEXT, 
	value_props JSONB NOT NULL, 
	website VARCHAR(512), 
	industry VARCHAR(120), 
	contact JSONB NOT NULL, 
	meta JSONB NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_company_profiles PRIMARY KEY (id), 
	CONSTRAINT uq_company_profile_org UNIQUE (org_id), 
	CONSTRAINT fk_company_profiles_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE
);

CREATE TABLE competitors (
	org_id UUID NOT NULL, 
	name VARCHAR(160) NOT NULL, 
	website VARCHAR(512), 
	positioning TEXT, 
	strengths JSONB NOT NULL, 
	weaknesses JSONB NOT NULL, 
	meta JSONB NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_competitors PRIMARY KEY (id), 
	CONSTRAINT fk_competitors_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE
);
CREATE INDEX ix_competitors_org ON competitors (org_id);

CREATE TABLE contacts (
	org_id UUID NOT NULL, 
	external_id VARCHAR(120), 
	name VARCHAR(160) NOT NULL, 
	email VARCHAR(255), 
	phone VARCHAR(40), 
	company VARCHAR(160), 
	avatar_url VARCHAR(512), 
	locale VARCHAR(12), 
	attributes JSONB NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_contacts PRIMARY KEY (id), 
	CONSTRAINT uq_contact_org_email UNIQUE (org_id, email), 
	CONSTRAINT fk_contacts_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE
);
CREATE INDEX ix_contacts_org_phone ON contacts (org_id, phone);
CREATE INDEX ix_contacts_org_name ON contacts (org_id, name);

CREATE TABLE devices (
	user_id UUID NOT NULL, 
	fingerprint VARCHAR(128) NOT NULL, 
	name VARCHAR(160), 
	os VARCHAR(60), 
	browser VARCHAR(60), 
	last_ip INET, 
	last_seen_at TIMESTAMP WITH TIME ZONE, 
	is_trusted BOOLEAN NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_devices PRIMARY KEY (id), 
	CONSTRAINT fk_devices_user_id_users FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);
CREATE INDEX ix_devices_user ON devices (user_id);

CREATE TABLE executive_insights (
	org_id UUID NOT NULL, 
	kind VARCHAR(20) NOT NULL, 
	title VARCHAR(255) NOT NULL, 
	summary TEXT NOT NULL, 
	recommendation TEXT, 
	severity VARCHAR(20) NOT NULL, 
	metrics JSONB NOT NULL, 
	period_start TIMESTAMP WITH TIME ZONE, 
	period_end TIMESTAMP WITH TIME ZONE, 
	is_pinned BOOLEAN NOT NULL, 
	generated_by VARCHAR(20) NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_executive_insights PRIMARY KEY (id), 
	CONSTRAINT fk_executive_insights_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE
);
CREATE INDEX ix_executive_insights_kind ON executive_insights (org_id, kind);
CREATE INDEX ix_executive_insights_org ON executive_insights (org_id, created_at);

CREATE TABLE hr_policies (
	org_id UUID NOT NULL, 
	title VARCHAR(200) NOT NULL, 
	type VARCHAR(40) NOT NULL, 
	body TEXT NOT NULL, 
	effective_date DATE, 
	applies_to VARCHAR(40) NOT NULL, 
	meta JSONB NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_hr_policies PRIMARY KEY (id), 
	CONSTRAINT fk_hr_policies_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE
);
CREATE INDEX ix_hr_policies_org ON hr_policies (org_id);

CREATE TABLE integrations_catalog (
	org_id UUID NOT NULL, 
	name VARCHAR(120) NOT NULL, 
	category VARCHAR(80), 
	description TEXT, 
	logo_url VARCHAR(512), 
	docs_url VARCHAR(512), 
	is_available BOOLEAN NOT NULL, 
	meta JSONB NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_integrations_catalog PRIMARY KEY (id), 
	CONSTRAINT fk_integrations_catalog_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE
);
CREATE INDEX ix_integrations_catalog_org ON integrations_catalog (org_id);

CREATE TABLE internal_documents (
	org_id UUID NOT NULL, 
	title VARCHAR(255) NOT NULL, 
	category VARCHAR(40) NOT NULL, 
	content TEXT, 
	source_url VARCHAR(1024), 
	status VARCHAR(20) NOT NULL, 
	visibility VARCHAR(20) NOT NULL, 
	owner_id UUID, 
	tags VARCHAR[] NOT NULL, 
	meta JSONB NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_internal_documents PRIMARY KEY (id), 
	CONSTRAINT fk_internal_documents_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE, 
	CONSTRAINT fk_internal_documents_owner_id_users FOREIGN KEY(owner_id) REFERENCES users (id) ON DELETE SET NULL
);
CREATE INDEX ix_internal_documents_category ON internal_documents (org_id, category);
CREATE INDEX ix_internal_documents_org ON internal_documents (org_id);

CREATE TABLE kb_documents (
	org_id UUID NOT NULL, 
	title VARCHAR(255) NOT NULL, 
	source_type VARCHAR(20) NOT NULL, 
	source_url VARCHAR(1024), 
	storage_path VARCHAR(512), 
	content_type VARCHAR(120), 
	status VARCHAR(20) NOT NULL, 
	error TEXT, 
	chunk_count INTEGER NOT NULL, 
	size_bytes INTEGER NOT NULL, 
	created_by UUID, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_kb_documents PRIMARY KEY (id), 
	CONSTRAINT fk_kb_documents_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE
);
CREATE INDEX ix_kb_documents_org_status ON kb_documents (org_id, status);

CREATE TABLE memberships (
	org_id UUID NOT NULL, 
	user_id UUID NOT NULL, 
	role VARCHAR(40) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	invited_by UUID, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_memberships PRIMARY KEY (id), 
	CONSTRAINT uq_membership_org_user UNIQUE (org_id, user_id), 
	CONSTRAINT fk_memberships_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE, 
	CONSTRAINT fk_memberships_user_id_users FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);
CREATE INDEX ix_memberships_org_status ON memberships (org_id, status);

CREATE TABLE notifications (
	org_id UUID NOT NULL, 
	user_id UUID, 
	type VARCHAR(40) NOT NULL, 
	channel VARCHAR(20) NOT NULL, 
	title VARCHAR(255) NOT NULL, 
	body TEXT, 
	payload JSONB NOT NULL, 
	read BOOLEAN NOT NULL, 
	delivery_status VARCHAR(20) NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_notifications PRIMARY KEY (id), 
	CONSTRAINT fk_notifications_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE, 
	CONSTRAINT fk_notifications_user_id_users FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);
CREATE INDEX ix_notifications_org_user ON notifications (org_id, user_id, read);

CREATE TABLE onboarding_flows (
	org_id UUID NOT NULL, 
	name VARCHAR(160) NOT NULL, 
	description TEXT, 
	audience VARCHAR(20) NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	is_default BOOLEAN NOT NULL, 
	meta JSONB NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_onboarding_flows PRIMARY KEY (id), 
	CONSTRAINT fk_onboarding_flows_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE
);
CREATE INDEX ix_onboarding_flows_org ON onboarding_flows (org_id);

CREATE TABLE password_reset_tokens (
	user_id UUID NOT NULL, 
	token_hash VARCHAR(128) NOT NULL, 
	expires_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	used BOOLEAN NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_password_reset_tokens PRIMARY KEY (id), 
	CONSTRAINT fk_password_reset_tokens_user_id_users FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);
CREATE UNIQUE INDEX ix_password_reset_tokens_token_hash ON password_reset_tokens (token_hash);
CREATE INDEX ix_pwd_reset_user ON password_reset_tokens (user_id);

CREATE TABLE policies (
	org_id UUID NOT NULL, 
	title VARCHAR(200) NOT NULL, 
	type VARCHAR(40) NOT NULL, 
	body TEXT, 
	effective_date DATE, 
	is_public BOOLEAN NOT NULL, 
	meta JSONB NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_policies PRIMARY KEY (id), 
	CONSTRAINT fk_policies_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE
);
CREATE INDEX ix_policies_org ON policies (org_id);

CREATE TABLE products (
	org_id UUID NOT NULL, 
	name VARCHAR(160) NOT NULL, 
	slug VARCHAR(120), 
	type VARCHAR(20) NOT NULL, 
	summary TEXT, 
	description TEXT, 
	status VARCHAR(20) NOT NULL, 
	meta JSONB NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_products PRIMARY KEY (id), 
	CONSTRAINT fk_products_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE
);
CREATE INDEX ix_products_org ON products (org_id);

CREATE TABLE roadmap_items (
	org_id UUID NOT NULL, 
	title VARCHAR(200) NOT NULL, 
	description TEXT, 
	status VARCHAR(20) NOT NULL, 
	quarter VARCHAR(16), 
	release_date DATE, 
	is_public BOOLEAN NOT NULL, 
	position INTEGER NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_roadmap_items PRIMARY KEY (id), 
	CONSTRAINT fk_roadmap_items_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE
);
CREATE INDEX ix_roadmap_items_org ON roadmap_items (org_id);

CREATE TABLE settings (
	org_id UUID NOT NULL, 
	key VARCHAR(80) NOT NULL, 
	value JSONB NOT NULL, 
	encrypted BOOLEAN NOT NULL, 
	description TEXT, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_settings PRIMARY KEY (id), 
	CONSTRAINT uq_setting_org_key UNIQUE (org_id, key), 
	CONSTRAINT fk_settings_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE
);

CREATE TABLE workflows (
	org_id UUID NOT NULL, 
	name VARCHAR(160) NOT NULL, 
	description TEXT, 
	status VARCHAR(20) NOT NULL, 
	trigger_type VARCHAR(20) NOT NULL, 
	trigger_config JSONB NOT NULL, 
	definition JSONB NOT NULL, 
	version INTEGER NOT NULL, 
	is_template BOOLEAN NOT NULL, 
	created_by UUID, 
	run_count INTEGER NOT NULL, 
	last_run_at TIMESTAMP WITH TIME ZONE, 
	meta JSONB NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_workflows PRIMARY KEY (id), 
	CONSTRAINT fk_workflows_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE, 
	CONSTRAINT fk_workflows_created_by_users FOREIGN KEY(created_by) REFERENCES users (id) ON DELETE SET NULL
);
CREATE INDEX ix_workflows_trigger ON workflows (org_id, trigger_type);
CREATE INDEX ix_workflows_org ON workflows (org_id);
CREATE INDEX ix_workflows_status ON workflows (org_id, status);

CREATE TABLE competitor_comparisons (
	org_id UUID NOT NULL, 
	competitor_id UUID NOT NULL, 
	dimension VARCHAR(120) NOT NULL, 
	us_value TEXT, 
	them_value TEXT, 
	advantage VARCHAR(12), 
	notes TEXT, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_competitor_comparisons PRIMARY KEY (id), 
	CONSTRAINT fk_competitor_comparisons_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE, 
	CONSTRAINT fk_competitor_comparisons_competitor_id_competitors FOREIGN KEY(competitor_id) REFERENCES competitors (id) ON DELETE CASCADE
);
CREATE INDEX ix_competitor_comparisons_competitor ON competitor_comparisons (competitor_id);
CREATE INDEX ix_competitor_comparisons_org ON competitor_comparisons (org_id);

CREATE TABLE conversations (
	org_id UUID NOT NULL, 
	contact_id UUID NOT NULL, 
	channel VARCHAR(20) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	subject VARCHAR(255), 
	language VARCHAR(40) NOT NULL, 
	ai_handled BOOLEAN NOT NULL, 
	sentiment VARCHAR(20), 
	assignee_id UUID, 
	external_ref VARCHAR(160), 
	last_message_at TIMESTAMP WITH TIME ZONE, 
	unread_count INTEGER NOT NULL, 
	meta JSONB NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_conversations PRIMARY KEY (id), 
	CONSTRAINT fk_conversations_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE, 
	CONSTRAINT fk_conversations_contact_id_contacts FOREIGN KEY(contact_id) REFERENCES contacts (id) ON DELETE CASCADE, 
	CONSTRAINT fk_conversations_assignee_id_users FOREIGN KEY(assignee_id) REFERENCES users (id) ON DELETE SET NULL
);
CREATE INDEX ix_conversations_external_ref ON conversations (external_ref);
CREATE INDEX ix_conversations_org_status ON conversations (org_id, status, last_message_at);
CREATE INDEX ix_conversations_org_channel ON conversations (org_id, channel);
CREATE INDEX ix_conversations_assignee ON conversations (assignee_id);

CREATE TABLE faqs (
	org_id UUID NOT NULL, 
	product_id UUID, 
	question TEXT NOT NULL, 
	answer TEXT NOT NULL, 
	category VARCHAR(80), 
	tags VARCHAR[] NOT NULL, 
	is_public BOOLEAN NOT NULL, 
	position INTEGER NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_faqs PRIMARY KEY (id), 
	CONSTRAINT fk_faqs_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE, 
	CONSTRAINT fk_faqs_product_id_products FOREIGN KEY(product_id) REFERENCES products (id) ON DELETE SET NULL
);
CREATE INDEX ix_faqs_org ON faqs (org_id);

CREATE TABLE features (
	org_id UUID NOT NULL, 
	product_id UUID, 
	name VARCHAR(160) NOT NULL, 
	description TEXT, 
	category VARCHAR(80), 
	meta JSONB NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_features PRIMARY KEY (id), 
	CONSTRAINT fk_features_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE, 
	CONSTRAINT fk_features_product_id_products FOREIGN KEY(product_id) REFERENCES products (id) ON DELETE SET NULL
);
CREATE INDEX ix_features_org ON features (org_id);

CREATE TABLE internal_chunks (
	org_id UUID NOT NULL, 
	document_id UUID NOT NULL, 
	chunk_index INTEGER NOT NULL, 
	content TEXT NOT NULL, 
	token_count INTEGER NOT NULL, 
	embedding VECTOR(1024), 
	pinecone_id VARCHAR(80), 
	meta JSONB NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_internal_chunks PRIMARY KEY (id), 
	CONSTRAINT uq_internal_chunk_document_index UNIQUE (document_id, chunk_index), 
	CONSTRAINT fk_internal_chunks_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE, 
	CONSTRAINT fk_internal_chunks_document_id_internal_documents FOREIGN KEY(document_id) REFERENCES internal_documents (id) ON DELETE CASCADE
);
CREATE INDEX ix_internal_chunks_org ON internal_chunks (org_id);
CREATE INDEX ix_internal_chunks_pinecone ON internal_chunks (pinecone_id);
CREATE INDEX ix_internal_chunks_document ON internal_chunks (document_id);

CREATE TABLE kb_chunks (
	org_id UUID NOT NULL, 
	document_id UUID NOT NULL, 
	chunk_index INTEGER NOT NULL, 
	content TEXT NOT NULL, 
	token_count INTEGER NOT NULL, 
	embedding VECTOR(1024), 
	pinecone_id VARCHAR(80), 
	meta JSONB NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_kb_chunks PRIMARY KEY (id), 
	CONSTRAINT fk_kb_chunks_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE, 
	CONSTRAINT fk_kb_chunks_document_id_kb_documents FOREIGN KEY(document_id) REFERENCES kb_documents (id) ON DELETE CASCADE
);
CREATE INDEX ix_kb_chunks_document ON kb_chunks (document_id);
CREATE INDEX ix_kb_chunks_org ON kb_chunks (org_id);
CREATE INDEX ix_kb_chunks_pinecone ON kb_chunks (pinecone_id);

CREATE TABLE leads (
	org_id UUID NOT NULL, 
	contact_id UUID, 
	name VARCHAR(160) NOT NULL, 
	company VARCHAR(160), 
	email VARCHAR(255), 
	phone VARCHAR(40), 
	stage VARCHAR(20) NOT NULL, 
	score INTEGER NOT NULL, 
	value NUMERIC(12, 2) NOT NULL, 
	source VARCHAR(20) NOT NULL, 
	owner_id UUID, 
	next_action VARCHAR(255), 
	next_action_due TIMESTAMP WITH TIME ZONE, 
	qualification JSONB NOT NULL, 
	notes TEXT, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_leads PRIMARY KEY (id), 
	CONSTRAINT fk_leads_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE, 
	CONSTRAINT fk_leads_contact_id_contacts FOREIGN KEY(contact_id) REFERENCES contacts (id) ON DELETE SET NULL, 
	CONSTRAINT fk_leads_owner_id_users FOREIGN KEY(owner_id) REFERENCES users (id) ON DELETE SET NULL
);
CREATE INDEX ix_leads_org_stage ON leads (org_id, stage);
CREATE INDEX ix_leads_org_score ON leads (org_id, score);
CREATE INDEX ix_leads_owner ON leads (owner_id);

CREATE TABLE onboarding_steps (
	org_id UUID NOT NULL, 
	flow_id UUID NOT NULL, 
	title VARCHAR(200) NOT NULL, 
	description TEXT, 
	action_type VARCHAR(40), 
	action_url VARCHAR(512), 
	position INTEGER NOT NULL, 
	is_required BOOLEAN NOT NULL, 
	meta JSONB NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_onboarding_steps PRIMARY KEY (id), 
	CONSTRAINT uq_onboarding_step_flow_position UNIQUE (flow_id, position), 
	CONSTRAINT fk_onboarding_steps_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE, 
	CONSTRAINT fk_onboarding_steps_flow_id_onboarding_flows FOREIGN KEY(flow_id) REFERENCES onboarding_flows (id) ON DELETE CASCADE
);
CREATE INDEX ix_onboarding_steps_flow ON onboarding_steps (flow_id, position);
CREATE INDEX ix_onboarding_steps_org ON onboarding_steps (org_id);

CREATE TABLE pricing_plans (
	org_id UUID NOT NULL, 
	product_id UUID, 
	name VARCHAR(120) NOT NULL, 
	price_amount NUMERIC(12, 2), 
	currency VARCHAR(8) NOT NULL, 
	billing_period VARCHAR(20) NOT NULL, 
	features JSONB NOT NULL, 
	limits JSONB NOT NULL, 
	is_public BOOLEAN NOT NULL, 
	position INTEGER NOT NULL, 
	meta JSONB NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_pricing_plans PRIMARY KEY (id), 
	CONSTRAINT fk_pricing_plans_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE, 
	CONSTRAINT fk_pricing_plans_product_id_products FOREIGN KEY(product_id) REFERENCES products (id) ON DELETE CASCADE
);
CREATE INDEX ix_pricing_plans_org ON pricing_plans (org_id);

CREATE TABLE sessions (
	user_id UUID NOT NULL, 
	device_id UUID, 
	refresh_jti VARCHAR(64) NOT NULL, 
	refresh_token_hash VARCHAR(128) NOT NULL, 
	expires_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	revoked BOOLEAN NOT NULL, 
	revoked_at TIMESTAMP WITH TIME ZONE, 
	ip_address INET, 
	user_agent VARCHAR(400), 
	last_used_at TIMESTAMP WITH TIME ZONE, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_sessions PRIMARY KEY (id), 
	CONSTRAINT fk_sessions_user_id_users FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
	CONSTRAINT fk_sessions_device_id_devices FOREIGN KEY(device_id) REFERENCES devices (id) ON DELETE SET NULL, 
	CONSTRAINT uq_sessions_refresh_jti UNIQUE (refresh_jti)
);
CREATE INDEX ix_sessions_refresh_jti ON sessions (refresh_jti);
CREATE INDEX ix_sessions_user_active ON sessions (user_id, revoked);

CREATE TABLE user_onboarding (
	org_id UUID NOT NULL, 
	user_id UUID NOT NULL, 
	flow_id UUID NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	completion_pct INTEGER NOT NULL, 
	started_at TIMESTAMP WITH TIME ZONE, 
	completed_at TIMESTAMP WITH TIME ZONE, 
	last_activity_at TIMESTAMP WITH TIME ZONE, 
	meta JSONB NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_user_onboarding PRIMARY KEY (id), 
	CONSTRAINT uq_user_onboarding_user_flow UNIQUE (user_id, flow_id), 
	CONSTRAINT fk_user_onboarding_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE, 
	CONSTRAINT fk_user_onboarding_user_id_users FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
	CONSTRAINT fk_user_onboarding_flow_id_onboarding_flows FOREIGN KEY(flow_id) REFERENCES onboarding_flows (id) ON DELETE CASCADE
);
CREATE INDEX ix_user_onboarding_user ON user_onboarding (user_id);
CREATE INDEX ix_user_onboarding_org_status ON user_onboarding (org_id, status);

CREATE TABLE workflow_runs (
	org_id UUID NOT NULL, 
	workflow_id UUID NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	trigger_source VARCHAR(120), 
	triggered_by UUID, 
	context JSONB NOT NULL, 
	result JSONB NOT NULL, 
	error TEXT, 
	started_at TIMESTAMP WITH TIME ZONE, 
	finished_at TIMESTAMP WITH TIME ZONE, 
	duration_ms INTEGER, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_workflow_runs PRIMARY KEY (id), 
	CONSTRAINT fk_workflow_runs_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE, 
	CONSTRAINT fk_workflow_runs_workflow_id_workflows FOREIGN KEY(workflow_id) REFERENCES workflows (id) ON DELETE CASCADE, 
	CONSTRAINT fk_workflow_runs_triggered_by_users FOREIGN KEY(triggered_by) REFERENCES users (id) ON DELETE SET NULL
);
CREATE INDEX ix_workflow_runs_status ON workflow_runs (org_id, status);
CREATE INDEX ix_workflow_runs_workflow ON workflow_runs (workflow_id, created_at);
CREATE INDEX ix_workflow_runs_org ON workflow_runs (org_id, created_at);

CREATE TABLE activities (
	org_id UUID NOT NULL, 
	lead_id UUID NOT NULL, 
	type VARCHAR(40) NOT NULL, 
	title VARCHAR(255) NOT NULL, 
	body TEXT, 
	actor_id UUID, 
	meta JSONB NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_activities PRIMARY KEY (id), 
	CONSTRAINT fk_activities_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE, 
	CONSTRAINT fk_activities_lead_id_leads FOREIGN KEY(lead_id) REFERENCES leads (id) ON DELETE CASCADE
);
CREATE INDEX ix_activities_lead ON activities (lead_id, created_at);

CREATE TABLE agent_runs (
	org_id UUID NOT NULL, 
	agent_id UUID, 
	conversation_id UUID, 
	intent VARCHAR(80), 
	confidence FLOAT, 
	handed_off BOOLEAN NOT NULL, 
	input_tokens INTEGER NOT NULL, 
	output_tokens INTEGER NOT NULL, 
	latency_ms INTEGER NOT NULL, 
	graph_state JSONB NOT NULL, 
	tools_used JSONB NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_agent_runs PRIMARY KEY (id), 
	CONSTRAINT fk_agent_runs_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE, 
	CONSTRAINT fk_agent_runs_agent_id_ai_agents FOREIGN KEY(agent_id) REFERENCES ai_agents (id) ON DELETE SET NULL, 
	CONSTRAINT fk_agent_runs_conversation_id_conversations FOREIGN KEY(conversation_id) REFERENCES conversations (id) ON DELETE CASCADE
);
CREATE INDEX ix_agent_runs_org ON agent_runs (org_id, created_at);
CREATE INDEX ix_agent_runs_conversation ON agent_runs (conversation_id);

CREATE TABLE customer_accounts (
	org_id UUID NOT NULL, 
	name VARCHAR(200) NOT NULL, 
	primary_email VARCHAR(255), 
	owner_id UUID, 
	plan VARCHAR(40), 
	mrr NUMERIC(12, 2) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	lead_id UUID, 
	last_active_at TIMESTAMP WITH TIME ZONE, 
	onboarded_at TIMESTAMP WITH TIME ZONE, 
	meta JSONB NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_customer_accounts PRIMARY KEY (id), 
	CONSTRAINT fk_customer_accounts_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE, 
	CONSTRAINT fk_customer_accounts_owner_id_users FOREIGN KEY(owner_id) REFERENCES users (id) ON DELETE SET NULL, 
	CONSTRAINT fk_customer_accounts_lead_id_leads FOREIGN KEY(lead_id) REFERENCES leads (id) ON DELETE SET NULL
);
CREATE INDEX ix_customer_accounts_active ON customer_accounts (org_id, last_active_at);
CREATE INDEX ix_customer_accounts_owner ON customer_accounts (owner_id);
CREATE INDEX ix_customer_accounts_org_status ON customer_accounts (org_id, status);

CREATE TABLE messages (
	org_id UUID NOT NULL, 
	conversation_id UUID NOT NULL, 
	sender_type VARCHAR(20) NOT NULL, 
	sender_id UUID, 
	author_name VARCHAR(160), 
	content TEXT NOT NULL, 
	language VARCHAR(12), 
	confidence FLOAT, 
	sources JSONB NOT NULL, 
	attachments JSONB NOT NULL, 
	meta JSONB NOT NULL, 
	delivery_status VARCHAR(20), 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_messages PRIMARY KEY (id), 
	CONSTRAINT fk_messages_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE, 
	CONSTRAINT fk_messages_conversation_id_conversations FOREIGN KEY(conversation_id) REFERENCES conversations (id) ON DELETE CASCADE
);
CREATE INDEX ix_messages_org ON messages (org_id);
CREATE INDEX ix_messages_conversation ON messages (conversation_id, created_at);

CREATE TABLE tickets (
	org_id UUID NOT NULL, 
	number INTEGER NOT NULL, 
	subject VARCHAR(255) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	priority VARCHAR(20) NOT NULL, 
	channel VARCHAR(20) NOT NULL, 
	sentiment VARCHAR(20), 
	tags VARCHAR[] NOT NULL, 
	conversation_id UUID, 
	requester_id UUID, 
	assignee_id UUID, 
	sla_due_at TIMESTAMP WITH TIME ZONE, 
	first_response_at TIMESTAMP WITH TIME ZONE, 
	resolved_at TIMESTAMP WITH TIME ZONE, 
	sla_breached BOOLEAN NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_tickets PRIMARY KEY (id), 
	CONSTRAINT fk_tickets_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE, 
	CONSTRAINT fk_tickets_conversation_id_conversations FOREIGN KEY(conversation_id) REFERENCES conversations (id) ON DELETE SET NULL, 
	CONSTRAINT fk_tickets_requester_id_contacts FOREIGN KEY(requester_id) REFERENCES contacts (id) ON DELETE SET NULL, 
	CONSTRAINT fk_tickets_assignee_id_users FOREIGN KEY(assignee_id) REFERENCES users (id) ON DELETE SET NULL
);
CREATE INDEX ix_tickets_assignee ON tickets (assignee_id);
CREATE UNIQUE INDEX ix_tickets_org_number ON tickets (org_id, number);
CREATE INDEX ix_tickets_org_status ON tickets (org_id, status, sla_due_at);

CREATE TABLE user_onboarding_steps (
	org_id UUID NOT NULL, 
	user_onboarding_id UUID NOT NULL, 
	step_id UUID NOT NULL, 
	is_completed BOOLEAN NOT NULL, 
	completed_at TIMESTAMP WITH TIME ZONE, 
	skipped BOOLEAN NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_user_onboarding_steps PRIMARY KEY (id), 
	CONSTRAINT uq_user_onboarding_step_parent_step UNIQUE (user_onboarding_id, step_id), 
	CONSTRAINT fk_user_onboarding_steps_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE, 
	CONSTRAINT fk_user_onboarding_steps_user_onboarding_id_user_onboarding FOREIGN KEY(user_onboarding_id) REFERENCES user_onboarding (id) ON DELETE CASCADE, 
	CONSTRAINT fk_user_onboarding_steps_step_id_onboarding_steps FOREIGN KEY(step_id) REFERENCES onboarding_steps (id) ON DELETE CASCADE
);
CREATE INDEX ix_user_onboarding_steps_org ON user_onboarding_steps (org_id);
CREATE INDEX ix_user_onboarding_steps_parent ON user_onboarding_steps (user_onboarding_id);

CREATE TABLE voice_calls (
	org_id UUID NOT NULL, 
	conversation_id UUID, 
	call_sid VARCHAR(64) NOT NULL, 
	from_number VARCHAR(40) NOT NULL, 
	to_number VARCHAR(40) NOT NULL, 
	direction VARCHAR(12) NOT NULL, 
	duration_seconds INTEGER NOT NULL, 
	transcript JSONB NOT NULL, 
	summary TEXT, 
	sentiment VARCHAR(20), 
	recording_url VARCHAR(512), 
	ended_at TIMESTAMP WITH TIME ZONE, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_voice_calls PRIMARY KEY (id), 
	CONSTRAINT fk_voice_calls_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE, 
	CONSTRAINT fk_voice_calls_conversation_id_conversations FOREIGN KEY(conversation_id) REFERENCES conversations (id) ON DELETE SET NULL
);
CREATE INDEX ix_voice_calls_call_sid ON voice_calls (call_sid);
CREATE INDEX ix_voice_calls_org ON voice_calls (org_id, created_at);

CREATE TABLE workflow_run_steps (
	org_id UUID NOT NULL, 
	run_id UUID NOT NULL, 
	node_id VARCHAR(80) NOT NULL, 
	node_type VARCHAR(40) NOT NULL, 
	step_order INTEGER NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	input JSONB NOT NULL, 
	output JSONB NOT NULL, 
	error TEXT, 
	started_at TIMESTAMP WITH TIME ZONE, 
	finished_at TIMESTAMP WITH TIME ZONE, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_workflow_run_steps PRIMARY KEY (id), 
	CONSTRAINT fk_workflow_run_steps_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE, 
	CONSTRAINT fk_workflow_run_steps_run_id_workflow_runs FOREIGN KEY(run_id) REFERENCES workflow_runs (id) ON DELETE CASCADE
);
CREATE INDEX ix_workflow_run_steps_org ON workflow_run_steps (org_id);
CREATE INDEX ix_workflow_run_steps_run ON workflow_run_steps (run_id, step_order);

CREATE TABLE customer_health_scores (
	org_id UUID NOT NULL, 
	customer_id UUID NOT NULL, 
	score INTEGER NOT NULL, 
	category VARCHAR(20) NOT NULL, 
	churn_risk FLOAT, 
	usage_score INTEGER, 
	engagement_score INTEGER, 
	support_score INTEGER, 
	satisfaction_score INTEGER, 
	adoption_score INTEGER, 
	drivers JSONB NOT NULL, 
	computed_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_customer_health_scores PRIMARY KEY (id), 
	CONSTRAINT fk_customer_health_scores_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE, 
	CONSTRAINT fk_customer_health_scores_customer_id_customer_accounts FOREIGN KEY(customer_id) REFERENCES customer_accounts (id) ON DELETE CASCADE
);
CREATE INDEX ix_customer_health_customer ON customer_health_scores (customer_id, computed_at);
CREATE INDEX ix_customer_health_category ON customer_health_scores (org_id, category);
CREATE INDEX ix_customer_health_org ON customer_health_scores (org_id, computed_at);

CREATE TABLE engagement_actions (
	org_id UUID NOT NULL, 
	customer_id UUID NOT NULL, 
	assignee_id UUID, 
	type VARCHAR(40) NOT NULL, 
	title VARCHAR(255) NOT NULL, 
	reason TEXT, 
	priority VARCHAR(20) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	due_at TIMESTAMP WITH TIME ZONE, 
	completed_at TIMESTAMP WITH TIME ZONE, 
	ai_generated BOOLEAN NOT NULL, 
	meta JSONB NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_engagement_actions PRIMARY KEY (id), 
	CONSTRAINT fk_engagement_actions_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE, 
	CONSTRAINT fk_engagement_actions_customer_id_customer_accounts FOREIGN KEY(customer_id) REFERENCES customer_accounts (id) ON DELETE CASCADE, 
	CONSTRAINT fk_engagement_actions_assignee_id_users FOREIGN KEY(assignee_id) REFERENCES users (id) ON DELETE SET NULL
);
CREATE INDEX ix_engagement_actions_org ON engagement_actions (org_id);
CREATE INDEX ix_engagement_actions_customer ON engagement_actions (customer_id);
CREATE INDEX ix_engagement_actions_status ON engagement_actions (org_id, status);

CREATE TABLE feedback (
	org_id UUID NOT NULL, 
	conversation_id UUID, 
	message_id UUID, 
	type VARCHAR(20) NOT NULL, 
	rating INTEGER, 
	comment TEXT, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_feedback PRIMARY KEY (id), 
	CONSTRAINT fk_feedback_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE, 
	CONSTRAINT fk_feedback_conversation_id_conversations FOREIGN KEY(conversation_id) REFERENCES conversations (id) ON DELETE CASCADE, 
	CONSTRAINT fk_feedback_message_id_messages FOREIGN KEY(message_id) REFERENCES messages (id) ON DELETE SET NULL
);
CREATE INDEX ix_feedback_org ON feedback (org_id, created_at);

CREATE TABLE knowledge_gaps (
	org_id UUID NOT NULL, 
	question TEXT NOT NULL, 
	normalized_q TEXT, 
	agent_run_id UUID, 
	conversation_id UUID, 
	document_id UUID, 
	occurrences INTEGER NOT NULL, 
	avg_confidence FLOAT, 
	suggestion TEXT, 
	suggested_answer TEXT, 
	status VARCHAR(20) NOT NULL, 
	resolved_by UUID, 
	resolved_at TIMESTAMP WITH TIME ZONE, 
	last_seen_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	meta JSONB NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_knowledge_gaps PRIMARY KEY (id), 
	CONSTRAINT fk_knowledge_gaps_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE, 
	CONSTRAINT fk_knowledge_gaps_agent_run_id_agent_runs FOREIGN KEY(agent_run_id) REFERENCES agent_runs (id) ON DELETE SET NULL, 
	CONSTRAINT fk_knowledge_gaps_conversation_id_conversations FOREIGN KEY(conversation_id) REFERENCES conversations (id) ON DELETE SET NULL, 
	CONSTRAINT fk_knowledge_gaps_document_id_kb_documents FOREIGN KEY(document_id) REFERENCES kb_documents (id) ON DELETE SET NULL, 
	CONSTRAINT fk_knowledge_gaps_resolved_by_users FOREIGN KEY(resolved_by) REFERENCES users (id) ON DELETE SET NULL
);
CREATE INDEX ix_knowledge_gaps_occurrences ON knowledge_gaps (org_id, occurrences);
CREATE INDEX ix_knowledge_gaps_org_status ON knowledge_gaps (org_id, status);

CREATE TABLE meetings (
	org_id UUID NOT NULL, 
	title VARCHAR(200) NOT NULL, 
	type VARCHAR(20) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	organizer_id UUID, 
	lead_id UUID, 
	customer_id UUID, 
	attendee_name VARCHAR(160), 
	attendee_email VARCHAR(255), 
	starts_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	ends_at TIMESTAMP WITH TIME ZONE, 
	timezone VARCHAR(60) NOT NULL, 
	location VARCHAR(512), 
	meeting_url VARCHAR(512), 
	external_event_id VARCHAR(160), 
	notes TEXT, 
	followup_sent BOOLEAN NOT NULL, 
	meta JSONB NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_meetings PRIMARY KEY (id), 
	CONSTRAINT fk_meetings_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE, 
	CONSTRAINT fk_meetings_organizer_id_users FOREIGN KEY(organizer_id) REFERENCES users (id) ON DELETE SET NULL, 
	CONSTRAINT fk_meetings_lead_id_leads FOREIGN KEY(lead_id) REFERENCES leads (id) ON DELETE SET NULL, 
	CONSTRAINT fk_meetings_customer_id_customer_accounts FOREIGN KEY(customer_id) REFERENCES customer_accounts (id) ON DELETE SET NULL
);
CREATE INDEX ix_meetings_status ON meetings (org_id, status);
CREATE INDEX ix_meetings_org_start ON meetings (org_id, starts_at);
CREATE INDEX ix_meetings_lead ON meetings (lead_id);

CREATE TABLE sentiments (
	org_id UUID NOT NULL, 
	message_id UUID, 
	conversation_id UUID, 
	label VARCHAR(20) NOT NULL, 
	score FLOAT NOT NULL, 
	escalate BOOLEAN NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_sentiments PRIMARY KEY (id), 
	CONSTRAINT fk_sentiments_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE, 
	CONSTRAINT fk_sentiments_message_id_messages FOREIGN KEY(message_id) REFERENCES messages (id) ON DELETE CASCADE, 
	CONSTRAINT fk_sentiments_conversation_id_conversations FOREIGN KEY(conversation_id) REFERENCES conversations (id) ON DELETE CASCADE
);
CREATE INDEX ix_sentiments_message ON sentiments (message_id);

CREATE TABLE ticket_attachments (
	org_id UUID NOT NULL, 
	ticket_id UUID NOT NULL, 
	filename VARCHAR(255) NOT NULL, 
	content_type VARCHAR(120) NOT NULL, 
	size_bytes BIGINT NOT NULL, 
	storage_path VARCHAR(512) NOT NULL, 
	uploaded_by UUID, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_ticket_attachments PRIMARY KEY (id), 
	CONSTRAINT fk_ticket_attachments_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE, 
	CONSTRAINT fk_ticket_attachments_ticket_id_tickets FOREIGN KEY(ticket_id) REFERENCES tickets (id) ON DELETE CASCADE
);
CREATE INDEX ix_ticket_attachments_ticket ON ticket_attachments (ticket_id);

CREATE TABLE ticket_comments (
	org_id UUID NOT NULL, 
	ticket_id UUID NOT NULL, 
	author_id UUID, 
	body TEXT NOT NULL, 
	is_internal BOOLEAN NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_ticket_comments PRIMARY KEY (id), 
	CONSTRAINT fk_ticket_comments_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE, 
	CONSTRAINT fk_ticket_comments_ticket_id_tickets FOREIGN KEY(ticket_id) REFERENCES tickets (id) ON DELETE CASCADE, 
	CONSTRAINT fk_ticket_comments_author_id_users FOREIGN KEY(author_id) REFERENCES users (id) ON DELETE SET NULL
);
CREATE INDEX ix_ticket_comments_ticket ON ticket_comments (ticket_id, created_at);

CREATE TABLE ticket_summaries (
	org_id UUID NOT NULL, 
	ticket_id UUID NOT NULL, 
	summary TEXT NOT NULL, 
	resolution TEXT, 
	next_steps VARCHAR[] NOT NULL, 
	model VARCHAR(60), 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_ticket_summaries PRIMARY KEY (id), 
	CONSTRAINT fk_ticket_summaries_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE, 
	CONSTRAINT uq_ticket_summaries_ticket_id UNIQUE (ticket_id), 
	CONSTRAINT fk_ticket_summaries_ticket_id_tickets FOREIGN KEY(ticket_id) REFERENCES tickets (id) ON DELETE CASCADE
);

CREATE TABLE usage_events (
	org_id UUID NOT NULL, 
	customer_id UUID, 
	user_id UUID, 
	event_type VARCHAR(60) NOT NULL, 
	feature VARCHAR(120), 
	quantity NUMERIC(12, 2) NOT NULL, 
	occurred_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	meta JSONB NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_usage_events PRIMARY KEY (id), 
	CONSTRAINT fk_usage_events_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE, 
	CONSTRAINT fk_usage_events_customer_id_customer_accounts FOREIGN KEY(customer_id) REFERENCES customer_accounts (id) ON DELETE CASCADE, 
	CONSTRAINT fk_usage_events_user_id_users FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE SET NULL
);
CREATE INDEX ix_usage_events_customer ON usage_events (customer_id, occurred_at);
CREATE INDEX ix_usage_events_type ON usage_events (org_id, event_type);
CREATE INDEX ix_usage_events_org ON usage_events (org_id, occurred_at);

CREATE TABLE meeting_reminders (
	org_id UUID NOT NULL, 
	meeting_id UUID NOT NULL, 
	remind_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	channel VARCHAR(20) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	sent_at TIMESTAMP WITH TIME ZONE, 
	meta JSONB NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT pk_meeting_reminders PRIMARY KEY (id), 
	CONSTRAINT fk_meeting_reminders_org_id_organizations FOREIGN KEY(org_id) REFERENCES organizations (id) ON DELETE CASCADE, 
	CONSTRAINT fk_meeting_reminders_meeting_id_meetings FOREIGN KEY(meeting_id) REFERENCES meetings (id) ON DELETE CASCADE
);
CREATE INDEX ix_meeting_reminders_due ON meeting_reminders (remind_at);
CREATE INDEX ix_meeting_reminders_meeting ON meeting_reminders (meeting_id);
CREATE INDEX ix_meeting_reminders_org ON meeting_reminders (org_id);

CREATE INDEX IF NOT EXISTS ix_kb_chunks_embedding_hnsw ON kb_chunks USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS ix_contacts_name_trgm ON contacts USING gin (name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS ix_internal_chunks_embedding_hnsw ON internal_chunks USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS ix_faqs_question_trgm ON faqs USING gin (question gin_trgm_ops);
CREATE INDEX IF NOT EXISTS ix_knowledge_gaps_question_trgm ON knowledge_gaps USING gin (question gin_trgm_ops);
CREATE INDEX IF NOT EXISTS ix_internal_documents_title_trgm ON internal_documents USING gin (title gin_trgm_ops);
