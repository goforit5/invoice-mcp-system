#!/usr/bin/env python3
"""
Simple test to verify CRM MCP server functionality
"""

import sys
import os
import sqlite3
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_basic_database():
    """Test basic database functionality without external dependencies"""
    print("Testing basic database functionality...")
    
    # Test database creation
    test_db_path = "/tmp/simple_crm_test.db"
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    try:
        # Create a simple database with one table
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        
        # Create a simple contacts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert test data
        cursor.execute("""
            INSERT INTO contacts (first_name, last_name, email)
            VALUES ('John', 'Doe', 'john@example.com')
        """)
        
        cursor.execute("""
            INSERT INTO contacts (first_name, last_name, email)
            VALUES ('Jane', 'Smith', 'jane@example.com')
        """)
        
        conn.commit()
        
        # Test query
        cursor.execute("SELECT COUNT(*) FROM contacts")
        count = cursor.fetchone()[0]
        
        cursor.execute("SELECT first_name, last_name, email FROM contacts")
        contacts = cursor.fetchall()
        
        conn.close()
        
        print(f"✅ Created database with {count} contacts")
        for contact in contacts:
            print(f"   - {contact[0]} {contact[1]} ({contact[2]})")
        
        # Clean up
        os.remove(test_db_path)
        print("✅ Database test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_import_modules():
    """Test importing our modules"""
    print("Testing module imports...")
    
    try:
        # Test database module
        try:
            from database import CRMDatabase
            print("✅ database.py imports successfully")
        except Exception as e:
            print(f"❌ database.py import failed: {e}")
            return False
        
        # Test models module  
        try:
            from models import Contact, Platform, Direction
            print("✅ models.py imports successfully")
        except Exception as e:
            print(f"❌ models.py import failed: {e}")
            return False
        
        # Test server module (may fail if MCP not installed)
        try:
            import server
            print("✅ server.py imports successfully")
        except ImportError as e:
            if "mcp" in str(e).lower():
                print("⚠️  server.py requires MCP package (pip install 'mcp[cli]')")
                print("   This is expected if MCP dependencies aren't installed")
            else:
                print(f"❌ server.py import failed: {e}")
                return False
        except Exception as e:
            print(f"❌ server.py import failed: {e}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Module import test failed: {e}")
        return False

def test_database_class():
    """Test our CRMDatabase class"""
    print("Testing CRMDatabase class...")
    
    try:
        from database import CRMDatabase
        
        test_db_path = "/tmp/crm_class_test.db"
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        
        # Test database initialization
        db = CRMDatabase(test_db_path)
        
        with db:
            print("✅ Database connection established")
            
            # Initialize schema
            db.init_database()
            print("✅ Database schema initialized")
            
            # Check that tables were created
            cursor = db.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = ['contacts', 'companies', 'communications', 'tasks']
            found_tables = [t for t in expected_tables if t in tables]
            
            print(f"✅ Created {len(tables)} tables, found expected: {found_tables}")
            
            # Test sample data creation
            db.create_sample_data()
            print("✅ Sample data created")
            
            # Test basic queries
            cursor.execute("SELECT COUNT(*) FROM contacts")
            contact_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM companies")
            company_count = cursor.fetchone()[0]
            
            print(f"✅ Sample data: {contact_count} contacts, {company_count} companies")
        
        # Clean up
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
            
        print("✅ CRMDatabase class test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ CRMDatabase class test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_models():
    """Test Pydantic models"""
    print("Testing Pydantic models...")
    
    try:
        from models import Contact, Communication, Platform, Direction
        from datetime import datetime
        
        # Test Contact model
        contact = Contact(
            first_name="Test",
            last_name="User",
            email="test@example.com"
        )
        print(f"✅ Contact model: {contact.full_name}")
        
        # Test Communication model
        comm = Communication(
            platform=Platform.email,
            sender_identifier="test@example.com", 
            message_content_text="Hello world",
            direction=Direction.incoming,
            communication_timestamp=datetime.now()
        )
        print(f"✅ Communication model: {comm.platform} from {comm.sender_identifier}")
        
        print("✅ Pydantic models test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Models test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all simple tests"""
    print("🚀 Running Simple CRM MCP Server Tests")
    print("=" * 50)
    
    tests = [
        ("Basic Database", test_basic_database),
        ("Module Imports", test_import_modules),
        ("CRMDatabase Class", test_database_class),
        ("Pydantic Models", test_models)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        print("-" * 20)
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All basic tests passed!")
        print("\n📝 CRM MCP Server is ready for use with Claude Code!")
        print("\nTo complete setup:")
        print("1. Install MCP: pip install 'mcp[cli]'")
        print("2. Initialize: python database.py --init --sample-data")
        print("3. Test server: python server.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    print(f"\nTest run completed: {'SUCCESS' if success else 'FAILURE'}")