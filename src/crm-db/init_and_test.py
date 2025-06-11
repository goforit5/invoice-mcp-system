#!/usr/bin/env python3
"""
Initialize CRM database and verify it works
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

def create_minimal_database():
    """Create a working minimal version of the CRM database"""
    
    db_path = Path(__file__).parent / "crm.db"
    
    # Remove existing database
    if db_path.exists():
        db_path.unlink()
    
    print(f"Creating CRM database at: {db_path}")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Create companies table
        cursor.execute("""
        CREATE TABLE companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            industry TEXT,
            website TEXT,
            phone TEXT,
            address TEXT,
            notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        print("✅ Created companies table")
        
        # Create contacts table
        cursor.execute("""
        CREATE TABLE contacts (
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
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
        """)
        print("✅ Created contacts table")
        
        # Create communications table
        cursor.execute("""
        CREATE TABLE communications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT NOT NULL,
            platform_message_id TEXT,
            sender_contact_id INTEGER,
            sender_display_name TEXT,
            sender_identifier TEXT NOT NULL,
            subject_line TEXT,
            message_content_text TEXT NOT NULL,
            direction TEXT NOT NULL,
            communication_timestamp DATETIME NOT NULL,
            processed_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            processing_status TEXT DEFAULT 'needs_processing',
            content_category TEXT,
            urgency_level TEXT DEFAULT 'normal',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sender_contact_id) REFERENCES contacts(id)
        )
        """)
        print("✅ Created communications table")
        
        # Create tasks table
        cursor.execute("""
        CREATE TABLE tasks (
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
            FOREIGN KEY (contact_id) REFERENCES contacts(id),
            FOREIGN KEY (company_id) REFERENCES companies(id),
            FOREIGN KEY (communication_id) REFERENCES communications(id)
        )
        """)
        print("✅ Created tasks table")
        
        # Create accounts table
        cursor.execute("""
        CREATE TABLE accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            account_number TEXT,
            bank_name TEXT,
            balance DECIMAL(10,2) DEFAULT 0.00,
            is_active BOOLEAN DEFAULT TRUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        print("✅ Created accounts table")
        
        # Create transactions table
        cursor.execute("""
        CREATE TABLE transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            description TEXT NOT NULL,
            category TEXT,
            vendor_name TEXT,
            company_id INTEGER,
            transaction_date DATE NOT NULL,
            transaction_type TEXT,
            notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id),
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
        """)
        print("✅ Created transactions table")
        
        # Create subscriptions table
        cursor.execute("""
        CREATE TABLE subscriptions (
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
            FOREIGN KEY (company_id) REFERENCES companies(id),
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        )
        """)
        print("✅ Created subscriptions table")
        
        # Create indexes
        indexes = [
            "CREATE INDEX idx_contacts_company ON contacts(company_id)",
            "CREATE INDEX idx_contacts_email ON contacts(email)",
            "CREATE INDEX idx_communications_sender ON communications(sender_contact_id)",
            "CREATE INDEX idx_communications_date ON communications(communication_timestamp)",
            "CREATE INDEX idx_tasks_due_date ON tasks(due_date)",
            "CREATE INDEX idx_transactions_account ON transactions(account_id)",
            "CREATE INDEX idx_transactions_date ON transactions(transaction_date)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        print("✅ Created indexes")
        
        # Insert sample data
        
        # Sample companies
        companies = [
            ("Acme Corporation", "Technology", "https://acme.com", "555-0100", "123 Business St"),
            ("Global Services", "Consulting", "https://global.com", "555-0200", "456 Enterprise Ave"),
            ("Tech Solutions", "Software", "https://techsol.com", "555-0300", "789 Innovation Dr")
        ]
        
        for company in companies:
            cursor.execute("""
                INSERT INTO companies (name, industry, website, phone, address)
                VALUES (?, ?, ?, ?, ?)
            """, company)
        
        # Sample contacts
        contacts = [
            ("John", "Smith", "john.smith@acme.com", "555-0101", "CEO", 1, "Key decision maker"),
            ("Sarah", "Johnson", "sarah@global.com", "555-0201", "Project Manager", 2, "Primary contact"),
            ("Mike", "Davis", "mike@techsol.com", "555-0301", "CTO", 3, "Technical lead")
        ]
        
        for contact in contacts:
            cursor.execute("""
                INSERT INTO contacts (first_name, last_name, email, phone, title, company_id, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, contact)
        
        # Sample accounts
        accounts = [
            ("Chase Checking", "checking", "1234", "Chase Bank", 5250.00),
            ("Savings Account", "savings", "5678", "Chase Bank", 12000.00)
        ]
        
        for account in accounts:
            cursor.execute("""
                INSERT INTO accounts (name, type, account_number, bank_name, balance)
                VALUES (?, ?, ?, ?, ?)
            """, account)
        
        # Sample communications
        cursor.execute("""
            INSERT INTO communications (
                platform, sender_contact_id, sender_display_name, sender_identifier,
                subject_line, message_content_text, direction, communication_timestamp
            ) VALUES (
                'email', 1, 'John Smith', 'john.smith@acme.com',
                'Project Update', 'Hi team, the project is progressing well. We should have deliverables ready by Friday.',
                'incoming', ?
            )
        """, (datetime.now(),))
        
        cursor.execute("""
            INSERT INTO communications (
                platform, sender_contact_id, sender_display_name, sender_identifier,
                subject_line, message_content_text, direction, communication_timestamp
            ) VALUES (
                'whatsapp', 2, 'Sarah Johnson', '+15550201',
                'Meeting Tomorrow', 'Can we reschedule our meeting to 3 PM tomorrow?',
                'incoming', ?
            )
        """, (datetime.now(),))
        
        # Sample tasks
        cursor.execute("""
            INSERT INTO tasks (contact_id, title, description, due_date, priority)
            VALUES (1, 'Follow up on project', 'Check on project deliverables status', DATE('now', '+3 days'), 'high')
        """)
        
        cursor.execute("""
            INSERT INTO tasks (contact_id, title, description, due_date, priority)
            VALUES (2, 'Schedule meeting', 'Set up meeting with Sarah for next week', DATE('now', '+1 day'), 'normal')
        """)
        
        conn.commit()
        print("✅ Sample data inserted")
        
        # Test queries
        
        # Test contacts with companies
        cursor.execute("""
            SELECT c.first_name, c.last_name, c.email, comp.name as company_name
            FROM contacts c
            LEFT JOIN companies comp ON c.company_id = comp.id
        """)
        
        contacts_result = cursor.fetchall()
        print(f"\n📋 Contacts ({len(contacts_result)}):")
        for row in contacts_result:
            print(f"   - {row['first_name']} {row['last_name']} ({row['email']}) at {row['company_name']}")
        
        # Test communications
        cursor.execute("""
            SELECT c.platform, c.sender_display_name, c.subject_line, 
                   substr(c.message_content_text, 1, 50) as preview
            FROM communications c
            ORDER BY c.communication_timestamp DESC
        """)
        
        comms_result = cursor.fetchall()
        print(f"\n💬 Communications ({len(comms_result)}):")
        for row in comms_result:
            print(f"   - {row['platform']}: {row['sender_display_name']} - {row['subject_line']}")
            print(f"     {row['preview']}...")
        
        # Test tasks
        cursor.execute("""
            SELECT t.title, t.description, t.due_date, t.priority,
                   c.first_name || ' ' || c.last_name as contact_name
            FROM tasks t
            LEFT JOIN contacts c ON t.contact_id = c.id
            WHERE t.completed = 0
        """)
        
        tasks_result = cursor.fetchall()
        print(f"\n✅ Pending Tasks ({len(tasks_result)}):")
        for row in tasks_result:
            print(f"   - {row['title']} (Due: {row['due_date']}, Priority: {row['priority']})")
            print(f"     Contact: {row['contact_name']}")
        
        # Test accounts
        cursor.execute("SELECT name, type, balance FROM accounts")
        accounts_result = cursor.fetchall()
        print(f"\n💰 Accounts ({len(accounts_result)}):")
        for row in accounts_result:
            print(f"   - {row['name']} ({row['type']}): ${row['balance']:.2f}")
        
        conn.close()
        
        print(f"\n🎉 CRM database successfully created and tested!")
        print(f"   Database location: {db_path}")
        print(f"   Database size: {db_path.stat().st_size / 1024:.1f} KB")
        
        return True
        
    except Exception as e:
        print(f"❌ Database creation failed: {e}")
        import traceback
        traceback.print_exc()
        conn.close()
        return False

def test_database_queries():
    """Test various database queries"""
    
    db_path = Path(__file__).parent / "crm.db"
    
    if not db_path.exists():
        print("❌ Database not found. Run create_minimal_database() first.")
        return False
    
    print("🔍 Testing database queries...")
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Test complex join query
        cursor.execute("""
            SELECT 
                c.first_name || ' ' || c.last_name as full_name,
                c.email,
                comp.name as company_name,
                COUNT(comm.id) as message_count,
                COUNT(t.id) as task_count
            FROM contacts c
            LEFT JOIN companies comp ON c.company_id = comp.id
            LEFT JOIN communications comm ON c.id = comm.sender_contact_id
            LEFT JOIN tasks t ON c.id = t.contact_id AND t.completed = 0
            GROUP BY c.id, c.first_name, c.last_name, c.email, comp.name
        """)
        
        summary_result = cursor.fetchall()
        print(f"\n📊 Contact Summary:")
        for row in summary_result:
            print(f"   - {row['full_name']} ({row['email']})")
            print(f"     Company: {row['company_name']}")
            print(f"     Messages: {row['message_count']}, Pending Tasks: {row['task_count']}")
        
        # Test search functionality
        cursor.execute("""
            SELECT c.first_name, c.last_name, c.email
            FROM contacts c
            WHERE c.first_name LIKE '%John%' OR c.last_name LIKE '%John%' OR c.email LIKE '%john%'
        """)
        
        search_result = cursor.fetchall()
        print(f"\n🔍 Search results for 'John': {len(search_result)} found")
        for row in search_result:
            print(f"   - {row['first_name']} {row['last_name']} ({row['email']})")
        
        conn.close()
        print("✅ Database queries test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Database queries test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 CRM Database Initialization and Testing")
    print("=" * 50)
    
    success = create_minimal_database()
    
    if success:
        print("\n" + "=" * 50)
        success = test_database_queries()
    
    if success:
        print("\n" + "=" * 50)
        print("🎉 All tests passed! CRM database is ready for use.")
        print("\nNext steps:")
        print("1. Install MCP dependencies: pip install 'mcp[cli]'")
        print("2. Test the MCP server: python server.py")
        print("3. Use with Claude Code!")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")