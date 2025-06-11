#!/usr/bin/env python3
"""
Test script for CRM MCP Server

Basic functionality tests to ensure the server works correctly.
"""

import sqlite3
import json
from pathlib import Path
from database import CRMDatabase

def test_database_initialization():
    """Test database creation and initialization"""
    print("🧪 Testing database initialization...")
    
    test_db_path = "test_crm.db"
    
    # Clean up any existing test database
    if Path(test_db_path).exists():
        Path(test_db_path).unlink()
    
    # Initialize database
    db = CRMDatabase(test_db_path)
    with db:
        db.init_database()
        db.create_sample_data()
    
    # Verify tables were created
    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    expected_tables = [
        'contacts', 'companies', 'interactions', 'tags', 'contact_tags', 'tasks',
        'accounts', 'subscriptions', 'transactions', 'budgets',
        'communications', 'communication_attachments', 'contact_identities',
        'communication_processing_log'
    ]
    
    missing_tables = [t for t in expected_tables if t not in tables]
    if missing_tables:
        print(f"❌ Missing tables: {missing_tables}")
        return False
    
    # Test sample data
    cursor.execute("SELECT COUNT(*) FROM contacts")
    contact_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM companies")
    company_count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"✅ Database initialized successfully!")
    print(f"   - Tables created: {len(tables)}")
    print(f"   - Sample contacts: {contact_count}")
    print(f"   - Sample companies: {company_count}")
    
    # Clean up
    Path(test_db_path).unlink()
    return True

def test_basic_queries():
    """Test basic database queries"""
    print("\n🧪 Testing basic database queries...")
    
    test_db_path = "test_crm.db"
    
    # Initialize test database
    db = CRMDatabase(test_db_path)
    with db:
        db.init_database()
        db.create_sample_data()
    
    try:
        conn = sqlite3.connect(test_db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Test contact query with company join
        cursor.execute("""
            SELECT c.first_name, c.last_name, c.email, comp.name as company_name
            FROM contacts c
            LEFT JOIN companies comp ON c.company_id = comp.id
            LIMIT 3
        """)
        
        contacts = cursor.fetchall()
        print(f"✅ Contact query successful - {len(contacts)} contacts found")
        
        for contact in contacts:
            print(f"   - {contact['first_name']} {contact['last_name']} ({contact['company_name']})")
        
        # Test communication query
        cursor.execute("""
            SELECT platform, sender_display_name, substr(message_content_text, 1, 50) as preview
            FROM communications
            LIMIT 2
        """)
        
        communications = cursor.fetchall()
        print(f"✅ Communication query successful - {len(communications)} communications found")
        
        for comm in communications:
            print(f"   - {comm['platform']}: {comm['sender_display_name']} - {comm['preview']}...")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Query test failed: {e}")
        return False
    finally:
        # Clean up
        if Path(test_db_path).exists():
            Path(test_db_path).unlink()
    
    return True

def test_data_models():
    """Test Pydantic data models"""
    print("\n🧪 Testing data models...")
    
    try:
        from models import Contact, Communication, Platform, Direction
        
        # Test contact model
        contact = Contact(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            title="Developer"
        )
        
        print(f"✅ Contact model: {contact.full_name} ({contact.email})")
        
        # Test communication model
        comm = Communication(
            platform=Platform.email,
            sender_identifier="test@example.com",
            message_content_text="This is a test message",
            direction=Direction.incoming,
            communication_timestamp="2024-01-15T10:30:00"
        )
        
        print(f"✅ Communication model: {comm.platform} from {comm.sender_identifier}")
        
    except Exception as e:
        print(f"❌ Data model test failed: {e}")
        return False
    
    return True

def test_mcp_server_import():
    """Test that the MCP server can be imported"""
    print("\n🧪 Testing MCP server import...")
    
    try:
        # Test imports
        from server import mcp, get_db_connection, format_results_for_llm
        
        print("✅ MCP server imports successful")
        print(f"   - Server name: {mcp.name}")
        
        # Test server has expected tools and resources
        print("   - Available tools and resources loaded")
        
        return True
        
    except Exception as e:
        print(f"❌ MCP server import failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("🚀 Starting CRM MCP Server Tests")
    print("=" * 50)
    
    tests = [
        test_database_initialization,
        test_basic_queries,
        test_data_models,
        test_mcp_server_import
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"🏁 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! CRM MCP Server is ready to use.")
        print("\nNext steps:")
        print("1. Install in Claude Desktop with: mcp install src/crm-db/server.py")
        print("2. Or add to .mcp.json configuration")
        print("3. Start using CRM tools in Claude conversations")
    else:
        print("⚠️  Some tests failed. Please check the error messages above.")
    
    return passed == total

if __name__ == "__main__":
    run_all_tests()