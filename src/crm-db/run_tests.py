#!/usr/bin/env python3
"""
Comprehensive test runner for CRM MCP Server
"""

import sys
import os
import traceback
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import sqlite3
        print("✅ sqlite3 import OK")
        
        from database import CRMDatabase
        print("✅ database module import OK")
        
        from models import Contact, Communication, Platform, Direction
        print("✅ models module import OK")
        
        # Test that FastMCP dependencies exist
        try:
            from mcp.server.fastmcp import FastMCP
            print("✅ FastMCP import OK")
        except ImportError as e:
            print(f"⚠️  FastMCP not available: {e}")
            print("   This is expected if MCP is not installed")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        traceback.print_exc()
        return False

def test_database_operations():
    """Test database creation and basic operations"""
    print("\n🧪 Testing database operations...")
    
    try:
        from database import CRMDatabase
        
        # Use temp file
        test_db = "/tmp/crm_test.db"
        if os.path.exists(test_db):
            os.unlink(test_db)
        
        # Create and initialize database
        db = CRMDatabase(test_db)
        with db:
            print("✅ Database connection established")
            
            db.init_database()
            print("✅ Database schema created")
            
            # Test table creation
            tables = db.conn.execute("""
                SELECT name FROM sqlite_master WHERE type='table'
            """).fetchall()
            
            table_names = [row[0] for row in tables]
            expected_tables = [
                'contacts', 'companies', 'communications', 'tasks',
                'accounts', 'transactions', 'subscriptions'
            ]
            
            missing = [t for t in expected_tables if t not in table_names]
            if missing:
                print(f"❌ Missing tables: {missing}")
                return False
            
            print(f"✅ All {len(table_names)} tables created")
            
            # Test sample data
            db.create_sample_data()
            print("✅ Sample data created")
            
            # Test queries
            contact_count = db.conn.execute("SELECT COUNT(*) FROM contacts").fetchone()[0]
            company_count = db.conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
            
            print(f"✅ Sample data: {contact_count} contacts, {company_count} companies")
            
            # Test join query
            result = db.conn.execute("""
                SELECT c.first_name, c.last_name, comp.name 
                FROM contacts c 
                LEFT JOIN companies comp ON c.company_id = comp.id 
                LIMIT 1
            """).fetchone()
            
            if result:
                print(f"✅ Join query works: {result[0]} {result[1]} at {result[2]}")
            else:
                print("❌ Join query returned no results")
                return False
        
        # Clean up
        if os.path.exists(test_db):
            os.unlink(test_db)
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        traceback.print_exc()
        return False

def test_models():
    """Test Pydantic models"""
    print("\n🧪 Testing Pydantic models...")
    
    try:
        from models import Contact, Communication, Platform, Direction
        from datetime import datetime
        
        # Test Contact model
        contact = Contact(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            title="Developer"
        )
        print(f"✅ Contact model: {contact.full_name}")
        
        # Test Communication model
        comm = Communication(
            platform=Platform.email,
            sender_identifier="john@example.com",
            message_content_text="Hello world",
            direction=Direction.incoming,
            communication_timestamp=datetime.now()
        )
        print(f"✅ Communication model: {comm.platform}")
        
        # Test model validation
        try:
            invalid_comm = Communication(
                platform="invalid_platform",  # Should fail validation
                sender_identifier="test@test.com",
                message_content_text="test",
                direction=Direction.incoming,
                communication_timestamp=datetime.now()
            )
            print("❌ Model validation failed - should have rejected invalid platform")
            return False
        except Exception:
            print("✅ Model validation works correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Models test failed: {e}")
        traceback.print_exc()
        return False

def test_server_structure():
    """Test server structure without running it"""
    print("\n🧪 Testing server structure...")
    
    try:
        # Test that server file can be imported
        import server
        print("✅ Server module imports successfully")
        
        # Check if FastMCP server is available
        if hasattr(server, 'mcp'):
            print(f"✅ FastMCP server created: {server.mcp.name}")
        else:
            print("⚠️  FastMCP server not found (MCP may not be installed)")
        
        # Test helper functions
        if hasattr(server, 'format_results_for_llm'):
            result = server.format_results_for_llm([], "Test")
            print("✅ Helper functions work")
        
        return True
        
    except Exception as e:
        print(f"❌ Server structure test failed: {e}")
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all tests"""
    print("🚀 Starting CRM MCP Server Comprehensive Tests")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Database Operations", test_database_operations),
        ("Pydantic Models", test_models),
        ("Server Structure", test_server_structure)
    ]
    
    passed = 0
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} - PASSED")
            else:
                print(f"❌ {test_name} - FAILED")
        except Exception as e:
            print(f"❌ {test_name} - FAILED with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! CRM MCP Server is ready for use with Claude Code.")
        print("\n📝 Next steps:")
        print("1. Install MCP dependencies: pip install 'mcp[cli]'")
        print("2. Initialize database: python database.py --init --sample-data")
        print("3. Start server: python server.py")
        print("4. Use with Claude Code MCP tools!")
    else:
        print("⚠️  Some tests failed. Check error messages above.")
        print("Make sure all dependencies are installed:")
        print("pip install 'mcp[cli]' pydantic fastapi python-dateutil")
    
    return passed == len(tests)

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)