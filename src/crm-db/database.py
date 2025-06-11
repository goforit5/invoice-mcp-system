#!/usr/bin/env python3
"""
CRM Database Initialization and Management

This module handles SQLite database creation, schema setup, and basic operations
for the CRM system designed for LLM processing.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime, date
from typing import Optional, List, Dict, Any
import argparse

class CRMDatabase:
    def __init__(self, db_path: str = "crm.db"):
        self.db_path = Path(db_path)
        self.conn = None
    
    def connect(self):
        """Connect to the database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Enable dict-like access
        return self.conn
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def init_database(self):
        """Initialize database with complete schema"""
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        
        # Create all tables
        self._create_core_tables(cursor)
        self._create_financial_tables(cursor)
        self._create_communication_tables(cursor)
        self._create_data_protection_tables(cursor)
        self._create_indexes(cursor)
        self._create_fts_tables(cursor)
        
        self.conn.commit()
        print(f"Database initialized successfully at {self.db_path}")
    
    def _create_core_tables(self, cursor):
        """Create core CRM tables"""
        
        # 1. contacts
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE,
            phone TEXT,
            title TEXT,
            company_id INTEGER,
            notes TEXT,
            status TEXT DEFAULT 'active',
            source TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            
            -- Soft Delete Fields
            deleted_at DATETIME,
            deleted_by TEXT,
            deletion_reason TEXT,
            deletion_context_json TEXT,
            
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
        """)
        
        # 2. companies
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
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
        )
        """)
        
        # 3. interactions
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER NOT NULL,
            type TEXT NOT NULL,
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
        )
        """)
        
        # 4. tags
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            color TEXT DEFAULT '#3B82F6',
            
            -- Soft Delete Fields
            deleted_at DATETIME,
            deleted_by TEXT,
            deletion_reason TEXT,
            deletion_context_json TEXT
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS contact_tags (
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
        )
        """)
        
        # 5. tasks
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER,
            company_id INTEGER,
            communication_id INTEGER,
            title TEXT NOT NULL,
            description TEXT,
            due_date DATE,
            priority TEXT DEFAULT 'normal',
            completed BOOLEAN DEFAULT FALSE,
            task_type TEXT,
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
        )
        """)
    
    def _create_financial_tables(self, cursor):
        """Create financial management tables"""
        
        # 6. accounts
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            account_number TEXT,
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
        )
        """)
        
        # 7. subscriptions
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_name TEXT NOT NULL,
            company_id INTEGER,
            amount DECIMAL(8,2) NOT NULL,
            currency TEXT DEFAULT 'USD',
            billing_cycle TEXT NOT NULL,
            next_billing_date DATE NOT NULL,
            account_id INTEGER,
            category TEXT,
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
        )
        """)
        
        # 8. transactions
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            description TEXT NOT NULL,
            category TEXT,
            vendor_name TEXT,
            company_id INTEGER,
            subscription_id INTEGER,
            transaction_date DATE NOT NULL,
            transaction_type TEXT,
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
        )
        """)
        
        # 9. budgets
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            period TEXT NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE,
            is_active BOOLEAN DEFAULT TRUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            
            -- Soft Delete Fields
            deleted_at DATETIME,
            deleted_by TEXT,
            deletion_reason TEXT,
            deletion_context_json TEXT
        )
        """)
    
    def _create_communication_tables(self, cursor):
        """Create communication processing tables"""
        
        # 10. communications
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS communications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            
            -- Platform and Source Information
            platform TEXT NOT NULL,
            platform_message_id TEXT,
            platform_thread_id TEXT,
            
            -- Contact and Relationship Information  
            sender_contact_id INTEGER,
            recipient_contact_id INTEGER,
            sender_company_id INTEGER,
            
            -- Sender Identity Information
            sender_display_name TEXT,
            sender_identifier TEXT NOT NULL,
            sender_platform_username TEXT,
            
            -- Recipient Information
            recipient_identifier TEXT,
            is_group_conversation BOOLEAN DEFAULT FALSE,
            group_name TEXT,
            group_participants TEXT,
            
            -- Message Content
            subject_line TEXT,
            message_content_text TEXT NOT NULL,
            message_content_html TEXT,
            content_language TEXT DEFAULT 'english',
            
            -- Media and Attachments
            has_media_attachments BOOLEAN DEFAULT FALSE,
            media_type TEXT,
            attachment_count INTEGER DEFAULT 0,
            
            -- Communication Metadata
            direction TEXT NOT NULL,
            communication_timestamp DATETIME NOT NULL,
            processed_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            
            -- Processing and Classification
            processing_status TEXT DEFAULT 'needs_processing',
            content_category TEXT,
            conversation_type TEXT,
            urgency_level TEXT DEFAULT 'normal',
            
            -- Action and Follow-up Information
            requires_follow_up BOOLEAN DEFAULT FALSE,
            follow_up_due_date DATE,
            action_items_extracted TEXT,
            
            -- File and Storage Information
            original_file_path TEXT,
            content_extraction_confidence DECIMAL(3,2),
            
            -- Platform-Specific Metadata
            platform_specific_data TEXT,
            
            -- Conversation Threading
            conversation_thread_global_id TEXT,
            reply_to_communication_id INTEGER,
            
            -- AI Processing
            ai_generated_summary TEXT,
            ai_extracted_entities TEXT,
            ai_sentiment_score DECIMAL(3,2),
            
            -- Manual Notes and Tags
            manual_notes TEXT,
            custom_tags TEXT,
            
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
        )
        """)
        
        # 11. communication_attachments
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS communication_attachments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            communication_id INTEGER NOT NULL,
            
            -- File Information
            original_filename TEXT NOT NULL,
            stored_filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            content_type TEXT NOT NULL,
            file_size_bytes INTEGER,
            
            -- Media-Specific Information
            media_category TEXT,
            media_duration_seconds INTEGER,
            image_width INTEGER,
            image_height INTEGER,
            
            -- Content Extraction
            extracted_text_content TEXT,
            extraction_method TEXT,
            extraction_confidence DECIMAL(3,2),
            
            -- AI Analysis
            ai_generated_description TEXT,
            ai_detected_objects TEXT,
            ai_detected_text TEXT,
            
            -- Platform-Specific Metadata
            platform_attachment_id TEXT,
            platform_metadata TEXT,
            
            -- Organization
            page_or_sequence_number INTEGER,
            is_primary_attachment BOOLEAN DEFAULT FALSE,
            attachment_description TEXT,
            
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            
            -- Soft Delete Fields
            deleted_at DATETIME,
            deleted_by TEXT,
            deletion_reason TEXT,
            deletion_context_json TEXT,
            
            FOREIGN KEY (communication_id) REFERENCES communications(id)
        )
        """)
        
        # 12. contact_identities
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS contact_identities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER NOT NULL,
            platform TEXT NOT NULL,
            platform_identifier TEXT NOT NULL,
            platform_display_name TEXT,
            verification_status TEXT DEFAULT 'unverified',
            is_primary_for_platform BOOLEAN DEFAULT FALSE,
            last_seen_date DATE,
            notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            
            -- Soft Delete Fields
            deleted_at DATETIME,
            deleted_by TEXT,
            deletion_reason TEXT,
            deletion_context_json TEXT,
            
            FOREIGN KEY (contact_id) REFERENCES contacts(id),
            UNIQUE(platform, platform_identifier)
        )
        """)
        
        # 13. communication_processing_log
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS communication_processing_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            communication_id INTEGER NOT NULL,
            
            -- Processing Information
            processing_step TEXT NOT NULL,
            processing_status TEXT NOT NULL,
            processing_engine TEXT,
            
            -- Results and Metrics
            processing_result_summary TEXT,
            confidence_score DECIMAL(3,2),
            processing_duration_ms INTEGER,
            tokens_used INTEGER,
            cost_cents INTEGER,
            
            -- Error Handling
            error_message TEXT,
            retry_count INTEGER DEFAULT 0,
            
            -- Detailed Results
            processing_results_json TEXT,
            
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            
            -- Note: Processing logs typically should not be soft deleted for audit purposes
            -- But included for completeness in the soft delete architecture
            deleted_at DATETIME,
            deleted_by TEXT,
            deletion_reason TEXT,
            deletion_context_json TEXT,
            
            FOREIGN KEY (communication_id) REFERENCES communications(id)
        )
        """)
    
    def _create_data_protection_tables(self, cursor):
        """Create data protection and governance tables"""
        
        # 14. deletion_audit
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS deletion_audit (
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
        )
        """)
        
        # 15. deletion_policies
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS deletion_policies (
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
        )
        """)
        
        # 16. data_retention_schedules
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS data_retention_schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_name TEXT NOT NULL,
            record_category TEXT, -- 'communication', 'financial', 'personal'
            retention_period_days INTEGER NOT NULL,
            auto_delete_enabled BOOLEAN DEFAULT FALSE,
            legal_hold_override BOOLEAN DEFAULT FALSE,
            compliance_basis TEXT, -- 'GDPR', 'CCPA', 'SOX', 'Company_Policy'
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_applied DATETIME
        )
        """)
    
    def _create_indexes(self, cursor):
        """Create performance indexes"""
        
        indexes = [
            # Core CRM indexes
            "CREATE INDEX IF NOT EXISTS idx_contacts_company ON contacts(company_id)",
            "CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email)",
            "CREATE INDEX IF NOT EXISTS idx_interactions_contact ON interactions(contact_id)",
            "CREATE INDEX IF NOT EXISTS idx_interactions_date ON interactions(interaction_date)",
            "CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date)",
            "CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority, completed)",
            "CREATE INDEX IF NOT EXISTS idx_tasks_communication ON tasks(communication_id)",
            
            # Financial indexes
            "CREATE INDEX IF NOT EXISTS idx_transactions_account ON transactions(account_id)",
            "CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date)",
            "CREATE INDEX IF NOT EXISTS idx_transactions_company ON transactions(company_id)",
            "CREATE INDEX IF NOT EXISTS idx_subscriptions_next_billing ON subscriptions(next_billing_date)",
            "CREATE INDEX IF NOT EXISTS idx_subscriptions_company ON subscriptions(company_id)",
            
            # Communication indexes
            "CREATE INDEX IF NOT EXISTS idx_communications_sender_contact ON communications(sender_contact_id)",
            "CREATE INDEX IF NOT EXISTS idx_communications_company ON communications(sender_company_id)",
            "CREATE INDEX IF NOT EXISTS idx_communications_date ON communications(communication_timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_communications_status ON communications(processing_status)",
            "CREATE INDEX IF NOT EXISTS idx_communications_category ON communications(content_category)",
            "CREATE INDEX IF NOT EXISTS idx_communications_platform ON communications(platform)",
            "CREATE INDEX IF NOT EXISTS idx_communications_source_id ON communications(platform_message_id)",
            "CREATE INDEX IF NOT EXISTS idx_communications_thread ON communications(conversation_thread_global_id)",
            "CREATE INDEX IF NOT EXISTS idx_communications_action_required ON communications(requires_follow_up, follow_up_due_date)",
            
            # Contact identities
            "CREATE INDEX IF NOT EXISTS idx_contact_identities_contact ON contact_identities(contact_id)",
            "CREATE INDEX IF NOT EXISTS idx_contact_identities_platform ON contact_identities(platform, platform_identifier)",
            
            # Data protection indexes
            "CREATE INDEX IF NOT EXISTS idx_deletion_audit_table_record ON deletion_audit(table_name, record_id)",
            "CREATE INDEX IF NOT EXISTS idx_deletion_audit_deleted_by ON deletion_audit(deleted_by)",
            "CREATE INDEX IF NOT EXISTS idx_deletion_audit_date ON deletion_audit(deleted_at)",
            "CREATE INDEX IF NOT EXISTS idx_deletion_policies_table ON deletion_policies(table_name)",
            "CREATE INDEX IF NOT EXISTS idx_retention_schedules_table ON data_retention_schedules(table_name)",
            
            # Soft delete indexes for all tables
            "CREATE INDEX IF NOT EXISTS idx_contacts_deleted ON contacts(deleted_at)",
            "CREATE INDEX IF NOT EXISTS idx_companies_deleted ON companies(deleted_at)",
            "CREATE INDEX IF NOT EXISTS idx_communications_deleted ON communications(deleted_at)",
            "CREATE INDEX IF NOT EXISTS idx_tasks_deleted ON tasks(deleted_at)",
            "CREATE INDEX IF NOT EXISTS idx_transactions_deleted ON transactions(deleted_at)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
    
    def _create_fts_tables(self, cursor):
        """Create full-text search tables"""
        
        # Communications FTS
        cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS communications_fts USING fts5(
            message_content_text, 
            subject_line, 
            sender_display_name,
            content=communications,
            content_rowid=id
        )
        """)
        
        # Contacts FTS
        cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS contacts_fts USING fts5(
            first_name,
            last_name, 
            email,
            notes,
            content=contacts,
            content_rowid=id
        )
        """)
    
    def create_sample_data(self):
        """Create sample data for testing"""
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        
        # Sample companies
        companies_data = [
            ("Acme Corporation", "Technology", "https://acme.com", "555-0100", "123 Business St, City, State 12345"),
            ("Global Services Inc", "Consulting", "https://globalservices.com", "555-0200", "456 Enterprise Ave, City, State 12345"),
            ("Pacific Gas & Electric", "Utilities", "https://pge.com", "1-800-743-5000", "PO Box 770000, San Francisco, CA 94177")
        ]
        
        for company_data in companies_data:
            cursor.execute("""
                INSERT OR IGNORE INTO companies (name, industry, website, phone, address)
                VALUES (?, ?, ?, ?, ?)
            """, company_data)
        
        # Sample contacts
        contacts_data = [
            ("John", "Smith", "john.smith@acme.com", "555-0101", "CEO", 1, "Key decision maker"),
            ("Sarah", "Johnson", "sarah.j@globalservices.com", "555-0201", "Project Manager", 2, "Primary contact for consulting projects"),
            ("Mike", "Davis", "mike.davis@acme.com", "555-0102", "CTO", 1, "Technical lead"),
        ]
        
        for contact_data in contacts_data:
            cursor.execute("""
                INSERT OR IGNORE INTO contacts (first_name, last_name, email, phone, title, company_id, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, contact_data)
        
        # Sample accounts
        accounts_data = [
            ("Chase Checking", "checking", "1234", "Chase Bank", 5250.00),
            ("Savings Account", "savings", "5678", "Chase Bank", 12000.00),
            ("Business Credit Card", "credit", "9999", "American Express", -850.00)
        ]
        
        for account_data in accounts_data:
            cursor.execute("""
                INSERT OR IGNORE INTO accounts (name, type, account_number, bank_name, balance)
                VALUES (?, ?, ?, ?, ?)
            """, account_data)
        
        # Sample communications
        cursor.execute("""
            INSERT OR IGNORE INTO communications (
                platform, sender_contact_id, sender_display_name, sender_identifier,
                subject_line, message_content_text, direction, communication_timestamp,
                content_category, processing_status
            ) VALUES (
                'email', 1, 'John Smith', 'john.smith@acme.com',
                'Project Update', 'Hi team, the project is progressing well. We should have the deliverables ready by Friday.',
                'incoming', datetime('now', '-2 days'),
                'business', 'processed'
            )
        """)
        
        self.conn.commit()
        print("Sample data created successfully")
    
    def create_default_deletion_policies(self):
        """Create default deletion policies for enterprise data protection"""
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        
        # Default deletion policies
        policies_data = [
            # Financial data: 7-year retention, approval required
            ("transactions", 2555, False, True, True, "financial", 
             "Financial transactions must be retained for 7 years for tax compliance"),
            ("accounts", 2555, False, True, True, "financial",
             "Account information retained for 7 years for financial auditing"),
            ("subscriptions", 365, True, False, True, "financial",
             "Subscription data can be hard deleted after 1 year"),
            
            # Personal communications: 90-day soft delete, then hard delete allowed
            ("communications", 90, True, False, True, "personal",
             "Personal communications can be hard deleted after 90 days"),
            ("communication_attachments", 90, True, False, True, "personal",
             "Communication attachments follow parent communication policy"),
            
            # Business contacts: 1-year retention, approval required
            ("contacts", 365, False, True, True, "business",
             "Business contacts require approval for deletion"),
            ("companies", 365, False, True, True, "business",
             "Company records require approval for deletion"),
            
            # CRM data: 180-day retention, no approval needed
            ("interactions", 180, True, False, True, "business",
             "Interaction records can be hard deleted after 180 days"),
            ("tasks", 180, True, False, True, "business",
             "Completed tasks can be hard deleted after 180 days"),
            
            # Identity data: 365-day retention, approval required
            ("contact_identities", 365, False, True, True, "personal",
             "Identity mappings require approval for GDPR compliance"),
            
            # Processing logs: Never delete for audit trail
            ("communication_processing_log", 2555, False, True, False, "audit",
             "Processing logs retained permanently for audit compliance"),
            ("deletion_audit", 2555, False, True, False, "audit",
             "Deletion audit logs retained permanently for compliance")
        ]
        
        for policy_data in policies_data:
            cursor.execute("""
                INSERT OR IGNORE INTO deletion_policies (
                    table_name, soft_delete_retention_days, hard_delete_allowed,
                    requires_approval, cascade_to_related, compliance_category,
                    policy_description
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, policy_data)
        
        # Default data retention schedules
        schedules_data = [
            ("communications", "personal", 2555, False, False, "GDPR"),
            ("transactions", "financial", 2555, False, True, "SOX"),
            ("contacts", "business", 2555, False, True, "Company_Policy")
        ]
        
        for schedule_data in schedules_data:
            cursor.execute("""
                INSERT OR IGNORE INTO data_retention_schedules (
                    table_name, record_category, retention_period_days,
                    auto_delete_enabled, legal_hold_override, compliance_basis
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, schedule_data)
        
        self.conn.commit()
        print("Default deletion policies and retention schedules created successfully")

def main():
    """CLI interface for database management"""
    parser = argparse.ArgumentParser(description="CRM Database Management")
    parser.add_argument("--init", action="store_true", help="Initialize database with schema")
    parser.add_argument("--sample-data", action="store_true", help="Add sample data")
    parser.add_argument("--deletion-policies", action="store_true", help="Create default deletion policies")
    parser.add_argument("--db-path", default="crm.db", help="Database file path")
    
    args = parser.parse_args()
    
    db = CRMDatabase(args.db_path)
    
    if args.init:
        with db:
            db.init_database()
            if args.sample_data:
                db.create_sample_data()
            if args.deletion_policies:
                db.create_default_deletion_policies()
    elif args.sample_data:
        with db:
            db.create_sample_data()
    elif args.deletion_policies:
        with db:
            db.create_default_deletion_policies()
    else:
        print("Use --init to initialize database, --sample-data to add sample data, or --deletion-policies to create default policies")

if __name__ == "__main__":
    main()