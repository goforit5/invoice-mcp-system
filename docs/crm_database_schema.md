# CRM Database Schema

This document defines the complete SQLite database schema for our integrated CRM, financial management, and mail processing system.

## Overview

The database combines contact relationship management with financial tracking and automated mail processing (both email and physical mail scanning). It handles subscriptions, expenses, banking, and creates a unified system for managing all business and personal communications. All tables are designed for simplicity while maintaining powerful querying capabilities.

## Key Features

- **Contact & Company Management**: Traditional CRM functionality with relationships
- **Financial Tracking**: Complete expense, income, and subscription management
- **Universal Communication Processing**: Unified handling of emails, physical mail, iMessage, WhatsApp, Instagram DMs, SMS, and more
- **Cross-Platform Identity Resolution**: Links the same person across all communication platforms
- **AI-Optimized Design**: Schema designed specifically for LLM processing and understanding
- **Smart Integration**: Automatic linking between communications, contacts, and financial records
- **Task Management**: Follow-ups and reminders for all activities
- **Enterprise Data Protection**: Soft delete architecture with audit trails and compliance support
- **Corporate Governance**: Policy-driven data retention and deletion approval workflows

## LLM-Optimized Design Features

### **Semantic Field Names**
- `sender_contact_id` instead of ambiguous `contact_id`
- `communication_timestamp` instead of generic `date`
- `processing_status` with descriptive values like 'needs_processing', 'flagged_for_review'

### **Structured AI Integration**
- Built-in AI processing fields: `ai_generated_summary`, `ai_extracted_entities`, `ai_sentiment_score`
- Processing cost tracking: `tokens_used`, `cost_cents`
- Confidence scoring for all automated processes

### **Platform-Agnostic Communication**
- Single table handles all communication types with platform-specific metadata
- Cross-platform conversation threading
- Identity resolution across platforms

### **Rich Context for LLMs**
- Detailed categorization: `content_category`, `conversation_type`, `urgency_level`
- Action item extraction: `action_items_extracted`, `requires_follow_up`
- Comprehensive metadata for informed decision-making

### **Data Protection & Compliance**
- Soft delete architecture: Records marked as deleted without losing data
- Audit trails: Complete deletion history with reasons and responsible parties
- Policy enforcement: Automated retention and approval workflows
- GDPR/CCPA compliance: Right to be forgotten with restoration windows

## Core CRM Tables

### 1. contacts
```sql
CREATE TABLE contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE,
    phone TEXT,
    title TEXT,
    company_id INTEGER,
    notes TEXT,
    status TEXT DEFAULT 'active', -- active, inactive, prospect
    source TEXT, -- how you met them
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Soft Delete Fields
    deleted_at DATETIME,
    deleted_by TEXT,
    deletion_reason TEXT,
    deletion_context_json TEXT,
    
    FOREIGN KEY (company_id) REFERENCES companies(id)
);
```

### 2. companies
```sql
CREATE TABLE companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    industry TEXT,
    website TEXT,
    phone TEXT,
    address TEXT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Soft Delete Fields
    deleted_at DATETIME,
    deleted_by TEXT,
    deletion_reason TEXT,
    deletion_context_json TEXT
);
```

### 3. interactions
```sql
CREATE TABLE interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_id INTEGER NOT NULL,
    type TEXT NOT NULL, -- email, call, meeting, note
    subject TEXT,
    notes TEXT NOT NULL,
    interaction_date DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Soft Delete Fields
    deleted_at DATETIME,
    deleted_by TEXT,
    deletion_reason TEXT,
    deletion_context_json TEXT,
    
    FOREIGN KEY (contact_id) REFERENCES contacts(id)
);
```

### 4. tags
```sql
CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    color TEXT DEFAULT '#3B82F6', -- hex color for UI
    
    -- Soft Delete Fields
    deleted_at DATETIME,
    deleted_by TEXT,
    deletion_reason TEXT,
    deletion_context_json TEXT
);

CREATE TABLE contact_tags (
    contact_id INTEGER,
    tag_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Soft Delete Fields
    deleted_at DATETIME,
    deleted_by TEXT,
    deletion_reason TEXT,
    deletion_context_json TEXT,
    
    PRIMARY KEY (contact_id, tag_id),
    FOREIGN KEY (contact_id) REFERENCES contacts(id),
    FOREIGN KEY (tag_id) REFERENCES tags(id)
);
```

### 5. tasks
```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_id INTEGER,
    company_id INTEGER,
    communication_id INTEGER, -- task created from communication
    title TEXT NOT NULL,
    description TEXT,
    due_date DATE,
    priority TEXT DEFAULT 'normal', -- low, normal, high, urgent
    completed BOOLEAN DEFAULT FALSE,
    task_type TEXT, -- follow_up, payment, review, etc.
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    
    -- Soft Delete Fields
    deleted_at DATETIME,
    deleted_by TEXT,
    deletion_reason TEXT,
    deletion_context_json TEXT,
    
    FOREIGN KEY (contact_id) REFERENCES contacts(id),
    FOREIGN KEY (company_id) REFERENCES companies(id),
    FOREIGN KEY (communication_id) REFERENCES communications(id)
);
```

## Financial Management Tables

### 6. accounts
```sql
CREATE TABLE accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL, -- "Chase Checking", "Amex Business"
    type TEXT NOT NULL, -- checking, savings, credit, investment
    account_number TEXT, -- last 4 digits only
    bank_name TEXT,
    balance DECIMAL(10,2) DEFAULT 0.00,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Soft Delete Fields
    deleted_at DATETIME,
    deleted_by TEXT,
    deletion_reason TEXT,
    deletion_context_json TEXT
);
```

### 7. subscriptions
```sql
CREATE TABLE subscriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_name TEXT NOT NULL, -- "Netflix", "Adobe Creative"
    company_id INTEGER, -- link to companies table
    amount DECIMAL(8,2) NOT NULL,
    currency TEXT DEFAULT 'USD',
    billing_cycle TEXT NOT NULL, -- monthly, yearly, weekly
    next_billing_date DATE NOT NULL,
    account_id INTEGER, -- which account it charges
    category TEXT, -- software, entertainment, utilities
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Soft Delete Fields
    deleted_at DATETIME,
    deleted_by TEXT,
    deletion_reason TEXT,
    deletion_context_json TEXT,
    
    FOREIGN KEY (company_id) REFERENCES companies(id),
    FOREIGN KEY (account_id) REFERENCES accounts(id)
);
```

### 8. transactions
```sql
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    amount DECIMAL(10,2) NOT NULL, -- negative for expenses
    description TEXT NOT NULL,
    category TEXT, -- groceries, business, subscription
    vendor_name TEXT,
    company_id INTEGER, -- link to companies if business expense
    subscription_id INTEGER, -- if this is a subscription payment
    transaction_date DATE NOT NULL,
    transaction_type TEXT, -- debit, credit, transfer
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Soft Delete Fields (Financial data requires special handling)
    deleted_at DATETIME,
    deleted_by TEXT,
    deletion_reason TEXT,
    deletion_context_json TEXT,
    
    FOREIGN KEY (account_id) REFERENCES accounts(id),
    FOREIGN KEY (company_id) REFERENCES companies(id),
    FOREIGN KEY (subscription_id) REFERENCES subscriptions(id)
);
```

### 9. budgets
```sql
CREATE TABLE budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL, -- "Monthly Software", "Q1 Marketing"
    category TEXT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    period TEXT NOT NULL, -- monthly, yearly, quarterly
    start_date DATE NOT NULL,
    end_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Soft Delete Fields
    deleted_at DATETIME,
    deleted_by TEXT,
    deletion_reason TEXT,
    deletion_context_json TEXT
);
```

## Communication Processing Tables

### 10. communications
```sql
CREATE TABLE communications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Platform and Source Information
    platform TEXT NOT NULL, -- 'email', 'physical_mail', 'imessage', 'whatsapp', 'instagram_dm', 'sms', 'slack', 'telegram'
    platform_message_id TEXT, -- unique ID from source platform
    platform_thread_id TEXT, -- conversation thread on source platform
    
    -- Contact and Relationship Information  
    sender_contact_id INTEGER, -- linked contact who sent this
    recipient_contact_id INTEGER, -- linked contact who received this
    sender_company_id INTEGER, -- company sender if business communication
    
    -- Sender Identity Information (for contact matching)
    sender_display_name TEXT, -- name shown on platform
    sender_identifier TEXT NOT NULL, -- email, phone, username, address depending on platform
    sender_platform_username TEXT, -- @username for social platforms
    
    -- Recipient Information
    recipient_identifier TEXT, -- my email, phone, username, etc.
    is_group_conversation BOOLEAN DEFAULT FALSE,
    group_name TEXT, -- name of group chat if applicable
    group_participants TEXT, -- JSON array of participant identifiers
    
    -- Message Content
    subject_line TEXT, -- email subject, document title, or conversation topic
    message_content_text TEXT NOT NULL, -- main text content (OCR for physical mail)
    message_content_html TEXT, -- HTML content for emails
    content_language TEXT DEFAULT 'english',
    
    -- Media and Attachments
    has_media_attachments BOOLEAN DEFAULT FALSE,
    media_type TEXT, -- 'text_only', 'image', 'video', 'audio', 'document', 'voice_message', 'sticker'
    attachment_count INTEGER DEFAULT 0,
    
    -- Communication Metadata
    direction TEXT NOT NULL, -- 'incoming', 'outgoing'
    communication_timestamp DATETIME NOT NULL, -- when message was sent/received
    processed_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Processing and Classification
    processing_status TEXT DEFAULT 'needs_processing', -- 'needs_processing', 'processed', 'archived', 'flagged_for_review'
    content_category TEXT, -- 'business', 'personal', 'financial', 'legal', 'marketing', 'notification', 'bill', 'invoice'
    conversation_type TEXT, -- 'one_on_one', 'group_chat', 'broadcast', 'newsletter', 'automated'
    urgency_level TEXT DEFAULT 'normal', -- 'low', 'normal', 'high', 'urgent'
    
    -- Action and Follow-up Information
    requires_follow_up BOOLEAN DEFAULT FALSE,
    follow_up_due_date DATE,
    action_items_extracted TEXT, -- JSON array of action items found in message
    
    -- File and Storage Information
    original_file_path TEXT, -- path to original file (scan, email export, etc.)
    content_extraction_confidence DECIMAL(3,2), -- OCR or parsing confidence (0.00-1.00)
    
    -- Platform-Specific Metadata (JSON)
    platform_specific_data TEXT, -- JSON object with platform-specific fields
    
    -- Conversation Threading
    conversation_thread_global_id TEXT, -- links messages across platforms for same conversation
    reply_to_communication_id INTEGER, -- if this is a reply to another message
    
    -- AI Processing
    ai_generated_summary TEXT, -- LLM-generated summary of important points
    ai_extracted_entities TEXT, -- JSON array of people, companies, dates, amounts extracted
    ai_sentiment_score DECIMAL(3,2), -- sentiment analysis score (-1.00 to 1.00)
    
    -- Manual Notes and Tags
    manual_notes TEXT, -- human-added notes
    custom_tags TEXT, -- JSON array of user-defined tags
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Soft Delete Fields
    deleted_at DATETIME,
    deleted_by TEXT,
    deletion_reason TEXT,
    deletion_context_json TEXT,
    
    FOREIGN KEY (sender_contact_id) REFERENCES contacts(id),
    FOREIGN KEY (recipient_contact_id) REFERENCES contacts(id),
    FOREIGN KEY (sender_company_id) REFERENCES companies(id),
    FOREIGN KEY (reply_to_communication_id) REFERENCES communications(id)
);
```

### 11. communication_attachments
```sql
CREATE TABLE communication_attachments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    communication_id INTEGER NOT NULL,
    
    -- File Information
    original_filename TEXT NOT NULL,
    stored_filename TEXT NOT NULL, -- internal storage filename
    file_path TEXT NOT NULL, -- full path to stored file
    content_type TEXT NOT NULL, -- 'image/jpeg', 'video/mp4', 'audio/aac', 'application/pdf'
    file_size_bytes INTEGER,
    
    -- Media-Specific Information
    media_category TEXT, -- 'photo', 'video', 'audio', 'document', 'voice_message', 'sticker', 'gif'
    media_duration_seconds INTEGER, -- for audio/video
    image_width INTEGER, -- for images
    image_height INTEGER, -- for images
    
    -- Content Extraction
    extracted_text_content TEXT, -- OCR from images, transcription from audio
    extraction_method TEXT, -- 'ocr', 'speech_to_text', 'manual_entry'
    extraction_confidence DECIMAL(3,2), -- confidence in extracted content
    
    -- AI Analysis
    ai_generated_description TEXT, -- LLM description of image/video content
    ai_detected_objects TEXT, -- JSON array of objects detected in media
    ai_detected_text TEXT, -- text detected in images
    
    -- Platform-Specific Metadata
    platform_attachment_id TEXT, -- ID on source platform
    platform_metadata TEXT, -- JSON with platform-specific data
    
    -- Organization
    page_or_sequence_number INTEGER, -- for multi-page documents or photo sequences
    is_primary_attachment BOOLEAN DEFAULT FALSE, -- main attachment vs secondary
    attachment_description TEXT, -- manual description
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Soft Delete Fields
    deleted_at DATETIME,
    deleted_by TEXT,
    deletion_reason TEXT,
    deletion_context_json TEXT,
    
    FOREIGN KEY (communication_id) REFERENCES communications(id)
);
```

### 12. contact_identities
```sql
-- Links multiple platform identities to the same contact
CREATE TABLE contact_identities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_id INTEGER NOT NULL,
    platform TEXT NOT NULL, -- 'email', 'phone', 'whatsapp', 'instagram', 'imessage', etc.
    platform_identifier TEXT NOT NULL, -- email address, phone number, username, etc.
    platform_display_name TEXT, -- how they appear on that platform
    verification_status TEXT DEFAULT 'unverified', -- 'verified', 'unverified', 'suspected'
    is_primary_for_platform BOOLEAN DEFAULT FALSE, -- main identifier for this person on this platform
    last_seen_date DATE, -- when this identity was last used
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Soft Delete Fields
    deleted_at DATETIME,
    deleted_by TEXT,
    deletion_reason TEXT,
    deletion_context_json TEXT,
    
    FOREIGN KEY (contact_id) REFERENCES contacts(id),
    UNIQUE(platform, platform_identifier) -- prevent duplicate identities
);
```

### 13. communication_processing_log
```sql
CREATE TABLE communication_processing_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    communication_id INTEGER NOT NULL,
    
    -- Processing Information
    processing_step TEXT NOT NULL, -- 'import', 'ocr', 'contact_matching', 'categorization', 'entity_extraction', 'ai_analysis'
    processing_status TEXT NOT NULL, -- 'started', 'completed', 'failed', 'skipped'
    processing_engine TEXT, -- 'tesseract_ocr', 'openai_gpt4', 'anthropic_claude', 'manual'
    
    -- Results and Metrics
    processing_result_summary TEXT, -- brief description of what was accomplished
    confidence_score DECIMAL(3,2), -- confidence in processing results
    processing_duration_ms INTEGER,
    tokens_used INTEGER, -- for AI processing
    cost_cents INTEGER, -- processing cost in cents
    
    -- Error Handling
    error_message TEXT, -- if processing failed
    retry_count INTEGER DEFAULT 0,
    
    -- Detailed Results (JSON)
    processing_results_json TEXT, -- detailed results in structured format
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Note: Processing logs typically should not be soft deleted for audit purposes
    -- But included for completeness in the soft delete architecture
    deleted_at DATETIME,
    deleted_by TEXT,
    deletion_reason TEXT,
    deletion_context_json TEXT,
    
    FOREIGN KEY (communication_id) REFERENCES communications(id)
);
```

## Data Protection & Governance Tables

### 14. deletion_audit
```sql
CREATE TABLE deletion_audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name TEXT NOT NULL,
    record_id INTEGER NOT NULL,
    deletion_type TEXT NOT NULL, -- 'soft', 'hard', 'cascade'
    deleted_by TEXT NOT NULL,
    deletion_reason TEXT,
    related_records_json TEXT, -- Track what else was affected
    deletion_policy_applied TEXT, -- Which policy was used
    can_be_restored BOOLEAN DEFAULT TRUE,
    retention_expires_at DATETIME, -- When hard delete is allowed
    approval_required BOOLEAN DEFAULT FALSE,
    approved_by TEXT,
    approved_at DATETIME,
    deleted_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 15. deletion_policies
```sql
CREATE TABLE deletion_policies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name TEXT NOT NULL,
    soft_delete_retention_days INTEGER DEFAULT 90,
    hard_delete_allowed BOOLEAN DEFAULT FALSE,
    requires_approval BOOLEAN DEFAULT FALSE,
    cascade_to_related BOOLEAN DEFAULT TRUE,
    compliance_category TEXT, -- 'financial', 'personal', 'business', 'communication'
    policy_description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

### 16. data_retention_schedules
```sql
CREATE TABLE data_retention_schedules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name TEXT NOT NULL,
    record_category TEXT, -- 'communication', 'financial', 'personal'
    retention_period_days INTEGER NOT NULL,
    auto_delete_enabled BOOLEAN DEFAULT FALSE,
    legal_hold_override BOOLEAN DEFAULT FALSE,
    compliance_basis TEXT, -- 'GDPR', 'CCPA', 'SOX', 'Company_Policy'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_applied DATETIME
);
```

## Relationships & Connections

### Key Foreign Key Relationships
- `contacts.company_id` → `companies.id` (many-to-one)
- `interactions.contact_id` → `contacts.id` (many-to-one)
- `tasks.contact_id` → `contacts.id` (many-to-one, optional)
- `tasks.company_id` → `companies.id` (many-to-one, optional)
- `tasks.communication_id` → `communications.id` (many-to-one, optional)
- `contact_tags.contact_id` → `contacts.id` (many-to-many via junction)
- `contact_tags.tag_id` → `tags.id` (many-to-many via junction)
- `subscriptions.company_id` → `companies.id` (many-to-one)
- `subscriptions.account_id` → `accounts.id` (many-to-one)
- `transactions.account_id` → `accounts.id` (many-to-one)
- `transactions.company_id` → `companies.id` (many-to-one, optional)
- `transactions.subscription_id` → `subscriptions.id` (many-to-one, optional)
- `communications.sender_contact_id` → `contacts.id` (many-to-one, optional)
- `communications.recipient_contact_id` → `contacts.id` (many-to-one, optional)
- `communications.sender_company_id` → `companies.id` (many-to-one, optional)
- `communications.reply_to_communication_id` → `communications.id` (many-to-one, optional)
- `communication_attachments.communication_id` → `communications.id` (many-to-one)
- `contact_identities.contact_id` → `contacts.id` (many-to-one)
- `communication_processing_log.communication_id` → `communications.id` (many-to-one)

### Smart Integration Points
- **Business Expenses**: Link transactions to companies and contacts for expense tracking
- **Subscription Management**: Connect recurring payments to vendor companies
- **Vendor Relationships**: Track both business relationships and financial transactions
- **Payment History**: Full audit trail of payments to specific vendors/contacts
- **Mail-to-Finance Integration**: Automatically create transactions from bill/invoice mail
- **Contact Discovery**: Create new contacts from unmatched mail senders
- **Task Generation**: Auto-create follow-up tasks from mail requiring action
- **Communication History**: Unified view of all interactions (calls, emails, physical mail)

## Use Cases & Query Patterns

### Daily Mail Processing Workflow
1. **Scan Physical Mail**: OCR documents → extract text → categorize → match to contacts/companies
2. **Process Emails**: Import → categorize → link to existing relationships
3. **Auto-Create Tasks**: Bills requiring payment → follow-up needed → document review
4. **Generate Transactions**: Invoice received → create expense record → link to vendor
5. **Update Contact Records**: New contact info from mail → update existing records

### CRM Management
- **Contact Tracking**: Find all contacts at a company, interaction history, status changes
- **Relationship Management**: Map business relationships, track communication frequency
- **Task Management**: Follow-ups, overdue items, priority-based queues
- **Tag-Based Organization**: Categorize contacts by industry, relationship type, status

### Financial Management
- **Expense Tracking**: Monthly/yearly spending by category, vendor analysis
- **Subscription Management**: Upcoming renewals, cost analysis, cancellation tracking
- **Budget Monitoring**: Actual vs planned spending, category overruns
- **Cash Flow**: Account balance trends, payment scheduling

### Mail Processing & Organization
- **Unified Mail View**: All communication (email + physical) in chronological order
- **Action Items**: Mail requiring follow-up, payment due dates, document reviews
- **Vendor Communication**: Complete mail history with specific companies/contacts
- **Document Management**: OCR searchable archive, attachment organization

### Smart Integration Queries
- **Vendor Intelligence**: Payment history + contact info + recent communications
- **Business Relationship Analysis**: Financial transactions linked to relationship strength
- **Automated Workflow**: Mail → Contact/Company matching → Task creation → Transaction recording
- **Communication Timeline**: Unified view of calls, emails, physical mail, meetings

### Reporting & Analytics
- **Monthly Business Review**: Expenses by vendor, communication frequency, outstanding tasks
- **Subscription Audit**: All recurring charges, renewal dates, cost optimization opportunities
- **Contact Engagement**: Interaction frequency, last contact date, follow-up needs
- **Mail Processing Stats**: OCR accuracy, processing time, categorization effectiveness
- **Financial Insights**: Spending patterns, vendor concentration, budget performance

### Advanced Use Cases
- **Predictive Tasks**: Automatically create payment reminders before due dates
- **Duplicate Detection**: Match mail senders to existing contacts using fuzzy matching
- **Smart Categorization**: ML-powered mail classification based on content and patterns
- **Relationship Mapping**: Identify decision makers and influencers within companies
- **Compliance Tracking**: Document retention, important mail archiving, audit trails

## Indexes (Recommended)

```sql
-- Core CRM indexes
CREATE INDEX idx_contacts_company ON contacts(company_id);
CREATE INDEX idx_contacts_email ON contacts(email);
CREATE INDEX idx_interactions_contact ON interactions(contact_id);
CREATE INDEX idx_interactions_date ON interactions(interaction_date);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_priority ON tasks(priority, completed);
CREATE INDEX idx_tasks_mail ON tasks(mail_id);

-- Financial indexes
CREATE INDEX idx_transactions_account ON transactions(account_id);
CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_transactions_company ON transactions(company_id);
CREATE INDEX idx_subscriptions_next_billing ON subscriptions(next_billing_date);
CREATE INDEX idx_subscriptions_company ON subscriptions(company_id);

-- Mail processing indexes
CREATE INDEX idx_mail_contact ON mail(contact_id);
CREATE INDEX idx_mail_company ON mail(company_id);
CREATE INDEX idx_mail_date ON mail(mail_date);
CREATE INDEX idx_mail_status ON mail(status);
CREATE INDEX idx_mail_category ON mail(category);
CREATE INDEX idx_mail_type ON mail(type);
CREATE INDEX idx_mail_source_id ON mail(source_id);
CREATE INDEX idx_mail_thread ON mail(thread_id);
CREATE INDEX idx_mail_action_required ON mail(requires_action, action_due_date);

-- Full-text search indexes (SQLite FTS5)
CREATE VIRTUAL TABLE mail_fts USING fts5(
    content_text, 
    subject, 
    sender_name,
    content=mail,
    content_rowid=id
);

CREATE VIRTUAL TABLE contacts_fts USING fts5(
    first_name,
    last_name, 
    email,
    notes,
    content=contacts,
    content_rowid=id
);
```

## Data Types & Conventions

- **DECIMAL(10,2)**: For monetary amounts (supports up to $99,999,999.99)
- **DATETIME**: ISO 8601 format (YYYY-MM-DD HH:MM:SS)
- **DATE**: ISO 8601 date format (YYYY-MM-DD)
- **BOOLEAN**: SQLite stores as INTEGER (0/1)
- **TEXT**: UTF-8 encoded strings
- **JSON Fields**: Used for flexible arrays (tags, email lists) stored as TEXT
- **Currency amounts**: Stored as positive for income, negative for expenses in transactions
- **Timestamps**: All tables include created_at, updated_at where applicable
- **File paths**: Absolute paths to stored documents/scans
- **Confidence scores**: DECIMAL(3,2) for OCR accuracy (0.00 to 1.00)

## Example Workflow: Processing a Utility Bill

```sql
-- 1. Mail arrives and is scanned/OCR'd
INSERT INTO mail (
    type, source_id, sender_name, subject, content_text, 
    mail_date, category, requires_action, action_due_date, file_path
) VALUES (
    'physical', 'scan_20240115_001', 'Pacific Gas & Electric',
    'Monthly utility bill', 'Account: 1234... Amount Due: $156.78... Due Date: 2024-02-01...',
    '2024-01-15', 'bill', TRUE, '2024-02-01', '/scans/2024/01/pge_bill.pdf'
);

-- 2. Auto-match to existing company
UPDATE mail SET company_id = (
    SELECT id FROM companies WHERE name LIKE '%Pacific Gas%' LIMIT 1
) WHERE id = LAST_INSERT_ROWID();

-- 3. Create task for payment
INSERT INTO tasks (
    company_id, mail_id, title, description, due_date, 
    priority, task_type
) VALUES (
    (SELECT company_id FROM mail WHERE id = LAST_INSERT_ROWID()),
    LAST_INSERT_ROWID(),
    'Pay PG&E utility bill',
    'Amount: $156.78, Account: 1234',
    '2024-02-01',
    'normal',
    'payment'
);

-- 4. Create pending transaction
INSERT INTO transactions (
    account_id, amount, description, category, company_id,
    transaction_date, transaction_type, notes
) VALUES (
    1, -- checking account
    -156.78,
    'PG&E utility bill',
    'utilities',
    (SELECT company_id FROM mail WHERE id = LAST_INSERT_ROWID()),
    '2024-02-01',
    'debit',
    'Auto-created from scanned mail'
);
```

This schema supports a complete mail processing and CRM system with financial integration, enabling automated workflows from mail receipt to task creation to financial recording.

## Data Protection & Compliance Architecture

### Soft Delete Implementation

All tables include soft delete fields for enterprise data protection:

```sql
-- Standard soft delete fields added to all tables
deleted_at DATETIME,           -- When deleted (NULL = active)
deleted_by TEXT,              -- Who deleted it  
deletion_reason TEXT,         -- Why it was deleted
deletion_context_json TEXT    -- Additional deletion metadata
```

### Query Patterns for Soft Deletes

**Active Records Only (Default):**
```sql
SELECT * FROM communications WHERE deleted_at IS NULL;
```

**Include Deleted Records (Admin/Audit):**
```sql
SELECT * FROM communications; -- All records
SELECT * FROM communications WHERE deleted_at IS NOT NULL; -- Deleted only
```

**Active Record Views:**
```sql
CREATE VIEW active_contacts AS SELECT * FROM contacts WHERE deleted_at IS NULL;
CREATE VIEW active_communications AS SELECT * FROM communications WHERE deleted_at IS NULL;
```

### Safe Deletion Process

1. **Check Dependencies**: Identify related records
2. **Apply Policy**: Use deletion_policies table rules
3. **Audit Trail**: Record in deletion_audit table
4. **Soft Delete**: Mark records with deletion timestamp
5. **Cascade**: Handle related records per policy

### Corporate Data Protection Benefits

**GDPR/CCPA Compliance:**
- Right to be forgotten with restoration window
- Complete audit trail for compliance reporting
- Policy-driven retention periods
- Data subject access request support

**Business Continuity:**
- Accidental deletion recovery (30-90 days)
- Analytics preservation for historical reporting
- Referential integrity maintenance
- Rollback capabilities for data corruption

**Security & Governance:**
- Role-based deletion permissions
- Approval workflows for sensitive data
- Legal hold override capabilities
- Compliance category enforcement

### Example Deletion Policies

```sql
-- Financial data: 7-year retention, approval required
INSERT INTO deletion_policies (
    table_name, soft_delete_retention_days, hard_delete_allowed,
    requires_approval, compliance_category
) VALUES (
    'transactions', 2555, FALSE, TRUE, 'financial'
);

-- Personal communications: 90-day soft delete, then hard delete allowed
INSERT INTO deletion_policies (
    table_name, soft_delete_retention_days, hard_delete_allowed,
    requires_approval, compliance_category
) VALUES (
    'communications', 90, TRUE, FALSE, 'personal'
);

-- Business contacts: 1-year retention, approval required
INSERT INTO deletion_policies (
    table_name, soft_delete_retention_days, hard_delete_allowed,
    requires_approval, compliance_category
) VALUES (
    'contacts', 365, FALSE, TRUE, 'business'
);
```

### Safe Deletion Workflow Example

```sql
-- 1. Mark communication as deleted
UPDATE communications 
SET deleted_at = CURRENT_TIMESTAMP,
    deleted_by = 'user@company.com',
    deletion_reason = 'User privacy request'
WHERE id = 123;

-- 2. Create audit record
INSERT INTO deletion_audit (
    table_name, record_id, deletion_type, deleted_by, deletion_reason
) VALUES (
    'communications', 123, 'soft', 'user@company.com', 'User privacy request'
);

-- 3. Cascade to related records (if policy allows)
UPDATE communication_attachments 
SET deleted_at = CURRENT_TIMESTAMP,
    deleted_by = 'system_cascade',
    deletion_reason = 'Parent communication deleted'
WHERE communication_id = 123;
```

This comprehensive data protection architecture ensures enterprise-grade compliance while maintaining operational flexibility and business intelligence capabilities.