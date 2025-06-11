#!/usr/bin/env python3
"""
Simple validation script for CRM MCP Server
Tests basic functionality without external dependencies
"""

import sqlite3
import json
from pathlib import Path

def validate_database_creation():
    """Test that we can create and query the database"""
    
    # Import our modules
    try:
        from database import CRMDatabase
        print("✅ Database module imports successfully")
    except ImportError as e:
        print(f"❌ Failed to import database module: {e}")
        return False
    
    # Create test database
    test_db = "validate_test.db"
    if Path(test_db).exists():
        Path(test_db).unlink()
    
    try:
        # Initialize database
        db = CRMDatabase(test_db)
        with db:
            db.init_database()
            print("✅ Database schema created successfully")
            
            # Test basic insert
            db.conn.execute("""
                INSERT INTO companies (name, industry) 
                VALUES ('Test Company', 'Technology')
            """)
            
            db.conn.execute("""
                INSERT INTO contacts (first_name, last_name, email, company_id)
                VALUES ('John', 'Test', 'john@test.com', 1)
            """)
            
            db.conn.commit()
            print("✅ Basic data insertion works")
            
            # Test query
            cursor = db.conn.execute("""
                SELECT c.first_name, c.last_name, comp.name as company_name
                FROM contacts c
                JOIN companies comp ON c.company_id = comp.id
            """)
            
            result = cursor.fetchone()
            if result:
                print(f"✅ Query successful: {result[0]} {result[1]} at {result[2]}")
            else:
                print("❌ Query returned no results")
                return False
        
        # Clean up
        Path(test_db).unlink()
        return True
        
    except Exception as e:
        print(f"❌ Database validation failed: {e}")
        if Path(test_db).exists():
            Path(test_db).unlink()
        return False

def validate_models():
    """Test that Pydantic models work"""
    try:
        from models import Contact, Communication, Platform, Direction
        print("✅ Models module imports successfully")
        
        # Test contact creation
        contact = Contact(
            first_name="Test",
            last_name="User",
            email="test@example.com"
        )
        print(f"✅ Contact model works: {contact.full_name}")
        
        # Test communication creation
        comm = Communication(
            platform=Platform.email,
            sender_identifier="test@example.com",
            message_content_text="Test message",
            direction=Direction.incoming,
            communication_timestamp="2024-01-15T10:30:00"
        )
        print(f"✅ Communication model works: {comm.platform}")
        
        return True
        
    except Exception as e:
        print(f"❌ Models validation failed: {e}")
        return False

def validate_server_structure():
    """Test that server file is structured correctly"""
    try:
        # Test that we can import the main components
        from server import mcp
        print("✅ Server imports successfully")
        print(f"   Server name: {mcp.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Server validation failed: {e}")
        return False

def main():
    """Run all validation tests"""
    print("🔍 Validating CRM MCP Server")
    print("=" * 40)
    
    tests = [
        ("Database Creation", validate_database_creation),
        ("Data Models", validate_models),
        ("Server Structure", validate_server_structure)
    ]
    
    passed = 0
    for test_name, test_func in tests:
        print(f"\n📋 Testing {test_name}...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} passed")
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print("\n" + "=" * 40)
    print(f"📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All validations passed!")
        print("\n📝 Next steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Initialize database: python database.py --init --sample-data")
        print("3. Install MCP server: mcp install server.py --name 'CRM Database'")
        print("4. Use in Claude Desktop!")
    else:
        print("⚠️ Some validations failed. Check error messages above.")
    
    return passed == len(tests)

if __name__ == "__main__":
    main()