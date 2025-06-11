#!/usr/bin/env python3
"""
CRM Database MCP Server

FastMCP server providing tools and resources for CRM database operations.
Designed specifically for LLM agent interactions with comprehensive
contact management, communication processing, and financial tracking.
"""

import sqlite3
import json
import logging
import asyncio
import requests
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any, Union
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from mcp.server.fastmcp import FastMCP, Context
from database import CRMDatabase
from models import (
    Contact, Company, Communication, Task, Transaction, Account, Subscription,
    CreateContactRequest, CreateCommunicationRequest, SearchRequest,
    CommunicationSummary, ContactSummary, SearchResult, OperationResult,
    Platform, Direction, ProcessingStatus, ContentCategory, UrgencyLevel
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database path
DB_PATH = Path(__file__).parent / "crm.db"

# FastMCP server context
class CRMContext:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db = CRMDatabase(str(db_path))

@asynccontextmanager
async def crm_lifespan(server: FastMCP) -> AsyncIterator[CRMContext]:
    """Initialize CRM database on startup"""
    logger.info(f"Initializing CRM database at {DB_PATH}")
    
    # Initialize database if it doesn't exist
    if not DB_PATH.exists():
        db = CRMDatabase(str(DB_PATH))
        with db:
            db.init_database()
            db.create_sample_data()
        logger.info("Database initialized with sample data")
    
    # Create context
    context = CRMContext(DB_PATH)
    
    try:
        yield context
    finally:
        logger.info("Shutting down CRM server")

# Create FastMCP server
mcp = FastMCP("CRM Database", lifespan=crm_lifespan)

# Helper functions
def get_db_connection() -> sqlite3.Connection:
    """Get database connection with row factory"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def format_results_for_llm(results: List[sqlite3.Row], description: str) -> str:
    """Format database results for LLM consumption"""
    if not results:
        return f"No results found. {description}"
    
    formatted_results = []
    for row in results:
        row_dict = dict(row)
        formatted_results.append(row_dict)
    
    return f"{description}\n\nResults ({len(results)} found):\n{json.dumps(formatted_results, indent=2, default=str)}"

def safe_execute(conn: sqlite3.Connection, query: str, params: tuple = ()) -> List[sqlite3.Row]:
    """Safely execute query with error handling"""
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()
    except Exception as e:
        logger.error(f"Database query failed: {e}")
        logger.error(f"Query: {query}")
        logger.error(f"Params: {params}")
        raise

# =============================================================================
# MCP TOOLS - Database Operations
# =============================================================================

@mcp.tool()
def create_contact(first_name: str, last_name: str, email: str = None, 
                  phone: str = None, title: str = None, company_name: str = None,
                  notes: str = None, source: str = None) -> str:
    """
    Create a new contact in the CRM system.
    
    Args:
        first_name: Contact's first name (required)
        last_name: Contact's last name (required)
        email: Primary email address (optional)
        phone: Primary phone number (optional)
        title: Job title or position (optional)
        company_name: Company name - will create company if doesn't exist (optional)
        notes: Additional notes about the contact (optional)
        source: How you met this contact (optional)
    
    Returns:
        JSON result with contact creation status and new contact ID
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Handle company creation/lookup
            company_id = None
            if company_name:
                # Check if company exists (active only)
                cursor.execute("SELECT id FROM companies WHERE name = ? AND deleted_at IS NULL", (company_name,))
                company_row = cursor.fetchone()
                
                if company_row:
                    company_id = company_row[0]
                else:
                    # Create new company
                    cursor.execute("""
                        INSERT INTO companies (name, created_at, updated_at)
                        VALUES (?, ?, ?)
                    """, (company_name, datetime.now(), datetime.now()))
                    company_id = cursor.lastrowid
            
            # Create contact
            cursor.execute("""
                INSERT INTO contacts (
                    first_name, last_name, email, phone, title, company_id,
                    notes, source, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                first_name, last_name, email, phone, title, company_id,
                notes, source, datetime.now(), datetime.now()
            ))
            
            contact_id = cursor.lastrowid
            conn.commit()
            
            # Get the created contact for response
            cursor.execute("""
                SELECT c.*, comp.name as company_name 
                FROM contacts c
                LEFT JOIN companies comp ON c.company_id = comp.id AND comp.deleted_at IS NULL
                WHERE c.id = ? AND c.deleted_at IS NULL
            """, (contact_id,))
            
            contact = dict(cursor.fetchone())
            
            result = OperationResult(
                success=True,
                message=f"Contact '{first_name} {last_name}' created successfully",
                data={"contact_id": contact_id, "contact": contact}
            )
            
            return json.dumps(result.dict(), indent=2, default=str)
            
    except Exception as e:
        error_result = OperationResult(
            success=False,
            message=f"Failed to create contact: {str(e)}",
            error_details=str(e)
        )
        return json.dumps(error_result.dict(), indent=2)

@mcp.tool()
def search_contacts(query: str, limit: int = 20) -> str:
    """
    Search contacts by name, email, or notes.
    
    Args:
        query: Search terms (searches name, email, phone, notes)
        limit: Maximum number of results to return (default 20)
    
    Returns:
        JSON array of matching contacts with company information
    """
    try:
        with get_db_connection() as conn:
            # Use FTS if available, otherwise fallback to LIKE search
            try:
                results = safe_execute(conn, """
                    SELECT c.*, comp.name as company_name,
                           bm25(contacts_fts) as relevance_score
                    FROM contacts_fts
                    JOIN contacts c ON contacts_fts.rowid = c.id AND c.deleted_at IS NULL
                    LEFT JOIN companies comp ON c.company_id = comp.id AND comp.deleted_at IS NULL
                    WHERE contacts_fts MATCH ?
                    ORDER BY bm25(contacts_fts)
                    LIMIT ?
                """, (query, limit))
            except:
                # Fallback to LIKE search
                search_term = f"%{query}%"
                results = safe_execute(conn, """
                    SELECT c.*, comp.name as company_name
                    FROM contacts c
                    LEFT JOIN companies comp ON c.company_id = comp.id AND comp.deleted_at IS NULL
                    WHERE (c.first_name LIKE ? OR c.last_name LIKE ? 
                       OR c.email LIKE ? OR c.notes LIKE ?)
                       AND c.deleted_at IS NULL
                    ORDER BY c.last_name, c.first_name
                    LIMIT ?
                """, (search_term, search_term, search_term, search_term, limit))
            
            return format_results_for_llm(results, f"Contact search results for: '{query}'")
            
    except Exception as e:
        return f"Search failed: {str(e)}"

@mcp.tool()
def create_communication(platform: str, sender_identifier: str, content: str,
                        subject: str = None, direction: str = "incoming",
                        sender_name: str = None, timestamp: str = None) -> str:
    """
    Create a new communication record.
    
    Args:
        platform: Communication platform (email, imessage, whatsapp, etc.)
        sender_identifier: Platform-specific sender ID (email, phone, username)
        content: Message content
        subject: Subject line or conversation topic (optional)
        direction: 'incoming' or 'outgoing' (default: incoming)
        sender_name: Display name of sender (optional)
        timestamp: ISO timestamp string (optional, uses current time if not provided)
    
    Returns:
        JSON result with communication creation status
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Parse timestamp
            if timestamp:
                try:
                    comm_timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                except:
                    comm_timestamp = datetime.now()
            else:
                comm_timestamp = datetime.now()
            
            # Try to match sender to existing contact
            sender_contact_id = None
            if platform == "email":
                cursor.execute("SELECT id FROM contacts WHERE email = ? AND deleted_at IS NULL", (sender_identifier,))
                contact_row = cursor.fetchone()
                if contact_row:
                    sender_contact_id = contact_row[0]
            else:
                # Check contact_identities table
                cursor.execute("""
                    SELECT ci.contact_id FROM contact_identities ci
                    JOIN contacts c ON ci.contact_id = c.id AND c.deleted_at IS NULL
                    WHERE ci.platform = ? AND ci.platform_identifier = ? AND ci.deleted_at IS NULL
                """, (platform, sender_identifier))
                identity_row = cursor.fetchone()
                if identity_row:
                    sender_contact_id = identity_row[0]
            
            # Create communication record
            cursor.execute("""
                INSERT INTO communications (
                    platform, sender_contact_id, sender_display_name, sender_identifier,
                    subject_line, message_content_text, direction, communication_timestamp,
                    processing_status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                platform, sender_contact_id, sender_name, sender_identifier,
                subject, content, direction, comm_timestamp,
                'processed', datetime.now(), datetime.now()
            ))
            
            comm_id = cursor.lastrowid
            conn.commit()
            
            result = OperationResult(
                success=True,
                message=f"Communication from {sender_identifier} created successfully",
                data={"communication_id": comm_id}
            )
            
            return json.dumps(result.dict(), indent=2, default=str)
            
    except Exception as e:
        error_result = OperationResult(
            success=False,
            message=f"Failed to create communication: {str(e)}",
            error_details=str(e)
        )
        return json.dumps(error_result.dict(), indent=2)

@mcp.tool()
def search_communications(query: str, platform: str = None, days_back: int = 30, limit: int = 20) -> str:
    """
    Search communications by content, sender, or subject.
    
    Args:
        query: Search terms (searches content, subject, sender name)
        platform: Filter by specific platform (optional)
        days_back: How many days back to search (default 30)
        limit: Maximum number of results (default 20)
    
    Returns:
        JSON array of matching communications
    """
    try:
        with get_db_connection() as conn:
            # Build query conditions
            conditions = ["c.communication_timestamp >= ?", "c.deleted_at IS NULL"]
            params = [datetime.now() - timedelta(days=days_back)]
            
            if platform:
                conditions.append("c.platform = ?")
                params.append(platform)
            
            # Add search terms
            search_term = f"%{query}%"
            conditions.append("""(
                c.message_content_text LIKE ? OR 
                c.subject_line LIKE ? OR 
                c.sender_display_name LIKE ?
            )""")
            params.extend([search_term, search_term, search_term])
            
            where_clause = " AND ".join(conditions)
            params.append(limit)
            
            results = safe_execute(conn, f"""
                SELECT 
                    c.*,
                    cont.first_name || ' ' || cont.last_name as contact_name,
                    comp.name as company_name
                FROM communications c
                LEFT JOIN contacts cont ON c.sender_contact_id = cont.id AND cont.deleted_at IS NULL
                LEFT JOIN companies comp ON c.sender_company_id = comp.id AND comp.deleted_at IS NULL
                WHERE {where_clause}
                ORDER BY c.communication_timestamp DESC
                LIMIT ?
            """, tuple(params))
            
            return format_results_for_llm(results, f"Communication search results for: '{query}'")
            
    except Exception as e:
        return f"Communication search failed: {str(e)}"

@mcp.tool()
def get_contact_timeline(contact_id: int, days_back: int = 90) -> str:
    """
    Get complete communication timeline for a contact.
    
    Args:
        contact_id: ID of the contact
        days_back: How many days of history to include (default 90)
    
    Returns:
        JSON with contact info and chronological communication timeline
    """
    try:
        with get_db_connection() as conn:
            # Get contact info
            contact_info = safe_execute(conn, """
                SELECT c.*, comp.name as company_name
                FROM contacts c
                LEFT JOIN companies comp ON c.company_id = comp.id AND comp.deleted_at IS NULL
                WHERE c.id = ? AND c.deleted_at IS NULL
            """, (contact_id,))
            
            if not contact_info:
                return f"Contact with ID {contact_id} not found"
            
            contact = dict(contact_info[0])
            
            # Get communications
            cutoff_date = datetime.now() - timedelta(days=days_back)
            communications = safe_execute(conn, """
                SELECT *
                FROM communications
                WHERE (sender_contact_id = ? OR recipient_contact_id = ?)
                  AND communication_timestamp >= ?
                  AND deleted_at IS NULL
                ORDER BY communication_timestamp DESC
            """, (contact_id, contact_id, cutoff_date))
            
            # Get tasks
            tasks = safe_execute(conn, """
                SELECT *
                FROM tasks
                WHERE contact_id = ? AND created_at >= ? AND deleted_at IS NULL
                ORDER BY created_at DESC
            """, (contact_id, cutoff_date))
            
            timeline_data = {
                "contact": contact,
                "communications": [dict(row) for row in communications],
                "active_tasks": [dict(row) for row in tasks],
                "summary": {
                    "total_communications": len(communications),
                    "pending_tasks": len([t for t in tasks if not dict(t)["completed"]]),
                    "last_contact_date": communications[0]["communication_timestamp"] if communications else None
                }
            }
            
            return json.dumps(timeline_data, indent=2, default=str)
            
    except Exception as e:
        return f"Failed to get contact timeline: {str(e)}"

@mcp.tool()
def create_task(title: str, description: str = None, contact_id: int = None,
               company_id: int = None, due_date: str = None, priority: str = "normal") -> str:
    """
    Create a new task or follow-up item.
    
    Args:
        title: Task title (required)
        description: Task description (optional)
        contact_id: Associated contact ID (optional)
        company_id: Associated company ID (optional)
        due_date: Due date in YYYY-MM-DD format (optional)
        priority: Task priority - low, normal, high, urgent (default: normal)
    
    Returns:
        JSON result with task creation status
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Parse due date
            parsed_due_date = None
            if due_date:
                try:
                    parsed_due_date = datetime.strptime(due_date, "%Y-%m-%d").date()
                except:
                    return f"Invalid due date format. Use YYYY-MM-DD"
            
            cursor.execute("""
                INSERT INTO tasks (
                    title, description, contact_id, company_id, due_date, priority, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (title, description, contact_id, company_id, parsed_due_date, priority, datetime.now()))
            
            task_id = cursor.lastrowid
            conn.commit()
            
            result = OperationResult(
                success=True,
                message=f"Task '{title}' created successfully",
                data={"task_id": task_id}
            )
            
            return json.dumps(result.dict(), indent=2, default=str)
            
    except Exception as e:
        error_result = OperationResult(
            success=False,
            message=f"Failed to create task: {str(e)}",
            error_details=str(e)
        )
        return json.dumps(error_result.dict(), indent=2)

@mcp.tool()
def execute_sql_query(sql: str) -> str:
    """
    Execute a read-only SQL query on the CRM database.
    SECURITY: Only SELECT statements are allowed.
    
    Args:
        sql: SQL SELECT statement to execute
    
    Returns:
        JSON results of the query
    """
    # Security check - only allow SELECT statements
    sql_upper = sql.strip().upper()
    if not sql_upper.startswith('SELECT'):
        return "Error: Only SELECT statements are allowed for security reasons"
    
    # Additional security - block certain keywords
    dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE']
    for keyword in dangerous_keywords:
        if keyword in sql_upper:
            return f"Error: '{keyword}' statements are not allowed"
    
    try:
        with get_db_connection() as conn:
            results = safe_execute(conn, sql)
            return format_results_for_llm(results, f"Query results for: {sql[:100]}...")
            
    except Exception as e:
        return f"SQL query failed: {str(e)}"

# =============================================================================
# CONTACT MANAGEMENT TOOLS
# =============================================================================

@mcp.tool()
def update_contact(contact_id: int, first_name: str = None, last_name: str = None,
                  email: str = None, phone: str = None, title: str = None,
                  company_name: str = None, notes: str = None, status: str = None) -> str:
    """
    Update an existing contact's information.
    
    Args:
        contact_id: ID of the contact to update (required)
        first_name: New first name (optional)
        last_name: New last name (optional)
        email: New email address (optional)
        phone: New phone number (optional)
        title: New job title (optional)
        company_name: New company name (optional)
        notes: New notes (optional)
        status: New status (active, inactive, prospect) (optional)
    
    Returns:
        JSON result with update status
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check if contact exists and is not deleted
            cursor.execute("SELECT id FROM contacts WHERE id = ? AND deleted_at IS NULL", (contact_id,))
            if not cursor.fetchone():
                return json.dumps({"success": False, "message": "Contact not found or deleted"})
            
            # Handle company lookup/creation if provided
            company_id = None
            if company_name:
                cursor.execute("SELECT id FROM companies WHERE name = ? AND deleted_at IS NULL", (company_name,))
                company_row = cursor.fetchone()
                if company_row:
                    company_id = company_row[0]
                else:
                    cursor.execute("""
                        INSERT INTO companies (name, created_at, updated_at)
                        VALUES (?, ?, ?)
                    """, (company_name, datetime.now(), datetime.now()))
                    company_id = cursor.lastrowid
            
            # Build update query dynamically
            update_fields = []
            update_values = []
            
            if first_name is not None:
                update_fields.append("first_name = ?")
                update_values.append(first_name)
            if last_name is not None:
                update_fields.append("last_name = ?")
                update_values.append(last_name)
            if email is not None:
                update_fields.append("email = ?")
                update_values.append(email)
            if phone is not None:
                update_fields.append("phone = ?")
                update_values.append(phone)
            if title is not None:
                update_fields.append("title = ?")
                update_values.append(title)
            if company_id is not None:
                update_fields.append("company_id = ?")
                update_values.append(company_id)
            if notes is not None:
                update_fields.append("notes = ?")
                update_values.append(notes)
            if status is not None:
                update_fields.append("status = ?")
                update_values.append(status)
            
            if not update_fields:
                return json.dumps({"success": False, "message": "No fields to update"})
            
            update_fields.append("updated_at = ?")
            update_values.append(datetime.now())
            update_values.append(contact_id)
            
            update_query = f"""
                UPDATE contacts 
                SET {', '.join(update_fields)}
                WHERE id = ? AND deleted_at IS NULL
            """
            
            cursor.execute(update_query, update_values)
            conn.commit()
            
            # Get updated contact
            cursor.execute("""
                SELECT c.*, comp.name as company_name 
                FROM contacts c
                LEFT JOIN companies comp ON c.company_id = comp.id AND comp.deleted_at IS NULL
                WHERE c.id = ? AND c.deleted_at IS NULL
            """, (contact_id,))
            
            updated_contact = dict(cursor.fetchone())
            
            result = OperationResult(
                success=True,
                message=f"Contact updated successfully",
                data={"contact": updated_contact}
            )
            
            return json.dumps(result.dict(), indent=2, default=str)
            
    except Exception as e:
        error_result = OperationResult(
            success=False,
            message=f"Failed to update contact: {str(e)}",
            error_details=str(e)
        )
        return json.dumps(error_result.dict(), indent=2)

@mcp.tool()
def get_contact_details(contact_id: int) -> str:
    """
    Get detailed information about a specific contact.
    
    Args:
        contact_id: ID of the contact to retrieve
    
    Returns:
        JSON with complete contact information
    """
    try:
        with get_db_connection() as conn:
            # Get contact with company information
            contact_info = safe_execute(conn, """
                SELECT c.*, comp.name as company_name, comp.industry as company_industry
                FROM contacts c
                LEFT JOIN companies comp ON c.company_id = comp.id AND comp.deleted_at IS NULL
                WHERE c.id = ? AND c.deleted_at IS NULL
            """, (contact_id,))
            
            if not contact_info:
                return json.dumps({"success": False, "message": "Contact not found"})
            
            contact = dict(contact_info[0])
            
            # Get recent communications
            communications = safe_execute(conn, """
                SELECT platform, sender_display_name, subject_line, 
                       communication_timestamp, direction
                FROM communications
                WHERE (sender_contact_id = ? OR recipient_contact_id = ?)
                  AND deleted_at IS NULL
                ORDER BY communication_timestamp DESC
                LIMIT 5
            """, (contact_id, contact_id))
            
            # Get active tasks
            tasks = safe_execute(conn, """
                SELECT title, due_date, priority, completed
                FROM tasks
                WHERE contact_id = ? AND deleted_at IS NULL
                ORDER BY due_date ASC
                LIMIT 5
            """, (contact_id,))
            
            # Get identities
            identities = safe_execute(conn, """
                SELECT platform, platform_identifier, platform_display_name
                FROM contact_identities
                WHERE contact_id = ? AND deleted_at IS NULL
            """, (contact_id,))
            
            result = {
                "success": True,
                "contact": contact,
                "recent_communications": [dict(row) for row in communications],
                "active_tasks": [dict(row) for row in tasks],
                "identities": [dict(row) for row in identities]
            }
            
            return json.dumps(result, indent=2, default=str)
            
    except Exception as e:
        return json.dumps({"success": False, "message": f"Failed to get contact: {str(e)}"})

@mcp.tool()
def delete_contact(contact_id: int, reason: str, deleted_by: str = "user") -> str:
    """
    Soft delete a contact with audit trail.
    
    Args:
        contact_id: ID of the contact to delete
        reason: Reason for deletion
        deleted_by: Who is deleting the contact
    
    Returns:
        JSON result with deletion status
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check if contact exists and is not already deleted
            cursor.execute("SELECT id, first_name, last_name FROM contacts WHERE id = ? AND deleted_at IS NULL", (contact_id,))
            contact_row = cursor.fetchone()
            if not contact_row:
                return json.dumps({"success": False, "message": "Contact not found or already deleted"})
            
            contact_name = f"{contact_row[1]} {contact_row[2]}"
            deletion_timestamp = datetime.now()
            
            # Soft delete the contact
            cursor.execute("""
                UPDATE contacts 
                SET deleted_at = ?, deleted_by = ?, deletion_reason = ?
                WHERE id = ?
            """, (deletion_timestamp, deleted_by, reason, contact_id))
            
            # Create audit record
            cursor.execute("""
                INSERT INTO deletion_audit (
                    table_name, record_id, deletion_type, deleted_by, deletion_reason
                ) VALUES (?, ?, ?, ?, ?)
            """, ('contacts', contact_id, 'soft', deleted_by, reason))
            
            conn.commit()
            
            result = OperationResult(
                success=True,
                message=f"Contact '{contact_name}' deleted successfully",
                data={"contact_id": contact_id, "deleted_at": deletion_timestamp}
            )
            
            return json.dumps(result.dict(), indent=2, default=str)
            
    except Exception as e:
        error_result = OperationResult(
            success=False,
            message=f"Failed to delete contact: {str(e)}",
            error_details=str(e)
        )
        return json.dumps(error_result.dict(), indent=2)

# =============================================================================
# COMPANY MANAGEMENT TOOLS
# =============================================================================

@mcp.tool()
def create_company(name: str, industry: str = None, website: str = None,
                  phone: str = None, address: str = None, notes: str = None) -> str:
    """
    Create a new company in the CRM system.
    
    Args:
        name: Company name (required)
        industry: Industry/business type (optional)
        website: Company website URL (optional)
        phone: Main phone number (optional)
        address: Business address (optional)
        notes: Additional notes (optional)
    
    Returns:
        JSON result with company creation status and new company ID
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check if company already exists
            cursor.execute("SELECT id FROM companies WHERE name = ? AND deleted_at IS NULL", (name,))
            if cursor.fetchone():
                return json.dumps({"success": False, "message": "Company with this name already exists"})
            
            # Create company
            cursor.execute("""
                INSERT INTO companies (
                    name, industry, website, phone, address, notes, 
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, industry, website, phone, address, notes, datetime.now(), datetime.now()))
            
            company_id = cursor.lastrowid
            conn.commit()
            
            # Get the created company
            cursor.execute("SELECT * FROM companies WHERE id = ?", (company_id,))
            company = dict(cursor.fetchone())
            
            result = OperationResult(
                success=True,
                message=f"Company '{name}' created successfully",
                data={"company_id": company_id, "company": company}
            )
            
            return json.dumps(result.dict(), indent=2, default=str)
            
    except Exception as e:
        error_result = OperationResult(
            success=False,
            message=f"Failed to create company: {str(e)}",
            error_details=str(e)
        )
        return json.dumps(error_result.dict(), indent=2)

@mcp.tool()
def search_companies(query: str, limit: int = 20) -> str:
    """
    Search companies by name, industry, or notes.
    
    Args:
        query: Search terms (searches name, industry, website, notes)
        limit: Maximum number of results to return (default 20)
    
    Returns:
        JSON array of matching companies
    """
    try:
        with get_db_connection() as conn:
            search_term = f"%{query}%"
            results = safe_execute(conn, """
                SELECT *
                FROM companies
                WHERE (name LIKE ? OR industry LIKE ? OR website LIKE ? OR notes LIKE ?)
                  AND deleted_at IS NULL
                ORDER BY name
                LIMIT ?
            """, (search_term, search_term, search_term, search_term, limit))
            
            return format_results_for_llm(results, f"Company search results for: '{query}'")
            
    except Exception as e:
        return f"Company search failed: {str(e)}"

@mcp.tool()
def update_company(company_id: int, name: str = None, industry: str = None,
                  website: str = None, phone: str = None, address: str = None,
                  notes: str = None) -> str:
    """
    Update an existing company's information.
    
    Args:
        company_id: ID of the company to update (required)
        name: New company name (optional)
        industry: New industry (optional)
        website: New website URL (optional)
        phone: New phone number (optional)
        address: New address (optional)
        notes: New notes (optional)
    
    Returns:
        JSON result with update status
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check if company exists
            cursor.execute("SELECT id FROM companies WHERE id = ? AND deleted_at IS NULL", (company_id,))
            if not cursor.fetchone():
                return json.dumps({"success": False, "message": "Company not found or deleted"})
            
            # Build update query
            update_fields = []
            update_values = []
            
            if name is not None:
                update_fields.append("name = ?")
                update_values.append(name)
            if industry is not None:
                update_fields.append("industry = ?")
                update_values.append(industry)
            if website is not None:
                update_fields.append("website = ?")
                update_values.append(website)
            if phone is not None:
                update_fields.append("phone = ?")
                update_values.append(phone)
            if address is not None:
                update_fields.append("address = ?")
                update_values.append(address)
            if notes is not None:
                update_fields.append("notes = ?")
                update_values.append(notes)
            
            if not update_fields:
                return json.dumps({"success": False, "message": "No fields to update"})
            
            update_fields.append("updated_at = ?")
            update_values.append(datetime.now())
            update_values.append(company_id)
            
            update_query = f"""
                UPDATE companies 
                SET {', '.join(update_fields)}
                WHERE id = ? AND deleted_at IS NULL
            """
            
            cursor.execute(update_query, update_values)
            conn.commit()
            
            # Get updated company
            cursor.execute("SELECT * FROM companies WHERE id = ?", (company_id,))
            updated_company = dict(cursor.fetchone())
            
            result = OperationResult(
                success=True,
                message="Company updated successfully",
                data={"company": updated_company}
            )
            
            return json.dumps(result.dict(), indent=2, default=str)
            
    except Exception as e:
        error_result = OperationResult(
            success=False,
            message=f"Failed to update company: {str(e)}",
            error_details=str(e)
        )
        return json.dumps(error_result.dict(), indent=2)

@mcp.tool()
def get_company_details(company_id: int) -> str:
    """
    Get detailed information about a specific company.
    
    Args:
        company_id: ID of the company to retrieve
    
    Returns:
        JSON with complete company information including contacts
    """
    try:
        with get_db_connection() as conn:
            # Get company info
            company_info = safe_execute(conn, """
                SELECT * FROM companies WHERE id = ? AND deleted_at IS NULL
            """, (company_id,))
            
            if not company_info:
                return json.dumps({"success": False, "message": "Company not found"})
            
            company = dict(company_info[0])
            
            # Get company contacts
            contacts = safe_execute(conn, """
                SELECT id, first_name, last_name, email, phone, title, status
                FROM contacts
                WHERE company_id = ? AND deleted_at IS NULL
                ORDER BY last_name, first_name
            """, (company_id,))
            
            # Get recent communications
            communications = safe_execute(conn, """
                SELECT platform, sender_display_name, subject_line, 
                       communication_timestamp, direction
                FROM communications
                WHERE sender_company_id = ? AND deleted_at IS NULL
                ORDER BY communication_timestamp DESC
                LIMIT 10
            """, (company_id,))
            
            # Get transactions
            transactions = safe_execute(conn, """
                SELECT amount, description, transaction_date, transaction_type
                FROM transactions
                WHERE company_id = ? AND deleted_at IS NULL
                ORDER BY transaction_date DESC
                LIMIT 10
            """, (company_id,))
            
            result = {
                "success": True,
                "company": company,
                "contacts": [dict(row) for row in contacts],
                "recent_communications": [dict(row) for row in communications],
                "recent_transactions": [dict(row) for row in transactions]
            }
            
            return json.dumps(result, indent=2, default=str)
            
    except Exception as e:
        return json.dumps({"success": False, "message": f"Failed to get company: {str(e)}"})

@mcp.tool()
def get_company_contacts(company_id: int) -> str:
    """
    Get all contacts for a specific company.
    
    Args:
        company_id: ID of the company
    
    Returns:
        JSON array of contacts at the company
    """
    try:
        with get_db_connection() as conn:
            results = safe_execute(conn, """
                SELECT c.*, comp.name as company_name
                FROM contacts c
                JOIN companies comp ON c.company_id = comp.id AND comp.deleted_at IS NULL
                WHERE c.company_id = ? AND c.deleted_at IS NULL
                ORDER BY c.last_name, c.first_name
            """, (company_id,))
            
            return format_results_for_llm(results, f"Contacts for company ID: {company_id}")
            
    except Exception as e:
        return f"Failed to get company contacts: {str(e)}"

# =============================================================================
# FINANCIAL MANAGEMENT TOOLS
# =============================================================================

@mcp.tool()
def create_transaction(account_id: int, amount: float, description: str,
                      category: str = None, vendor_name: str = None,
                      company_id: int = None, transaction_date: str = None,
                      transaction_type: str = "expense", notes: str = None) -> str:
    """
    Create a new financial transaction.
    
    Args:
        account_id: ID of the account for this transaction (required)
        amount: Transaction amount - positive for income, negative for expenses (required)
        description: Transaction description (required)
        category: Transaction category (optional)
        vendor_name: Vendor/payee name (optional)
        company_id: Associated company ID (optional)
        transaction_date: Date in YYYY-MM-DD format (optional, defaults to today)
        transaction_type: Type (expense, income, transfer) (optional)
        notes: Additional notes (optional)
    
    Returns:
        JSON result with transaction creation status
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Verify account exists
            cursor.execute("SELECT id FROM accounts WHERE id = ? AND deleted_at IS NULL", (account_id,))
            if not cursor.fetchone():
                return json.dumps({"success": False, "message": "Account not found"})
            
            # Parse transaction date
            if transaction_date:
                try:
                    parsed_date = datetime.strptime(transaction_date, "%Y-%m-%d").date()
                except:
                    return json.dumps({"success": False, "message": "Invalid date format. Use YYYY-MM-DD"})
            else:
                parsed_date = date.today()
            
            # Create transaction
            cursor.execute("""
                INSERT INTO transactions (
                    account_id, amount, description, category, vendor_name,
                    company_id, transaction_date, transaction_type, notes, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (account_id, amount, description, category, vendor_name,
                  company_id, parsed_date, transaction_type, notes, datetime.now()))
            
            transaction_id = cursor.lastrowid
            conn.commit()
            
            # Get created transaction with account info
            cursor.execute("""
                SELECT t.*, a.name as account_name, c.name as company_name
                FROM transactions t
                JOIN accounts a ON t.account_id = a.id
                LEFT JOIN companies c ON t.company_id = c.id AND c.deleted_at IS NULL
                WHERE t.id = ?
            """, (transaction_id,))
            
            transaction = dict(cursor.fetchone())
            
            result = OperationResult(
                success=True,
                message=f"Transaction created successfully",
                data={"transaction_id": transaction_id, "transaction": transaction}
            )
            
            return json.dumps(result.dict(), indent=2, default=str)
            
    except Exception as e:
        error_result = OperationResult(
            success=False,
            message=f"Failed to create transaction: {str(e)}",
            error_details=str(e)
        )
        return json.dumps(error_result.dict(), indent=2)

@mcp.tool()
def search_transactions(query: str = None, account_id: int = None, company_id: int = None,
                       category: str = None, days_back: int = 30, limit: int = 20) -> str:
    """
    Search financial transactions with various filters.
    
    Args:
        query: Search term for description or vendor (optional)
        account_id: Filter by specific account (optional)
        company_id: Filter by specific company (optional)
        category: Filter by transaction category (optional)
        days_back: How many days back to search (default 30)
        limit: Maximum number of results (default 20)
    
    Returns:
        JSON array of matching transactions
    """
    try:
        with get_db_connection() as conn:
            # Build WHERE conditions
            conditions = ["t.deleted_at IS NULL"]
            params = []
            
            if query:
                conditions.append("(t.description LIKE ? OR t.vendor_name LIKE ?)")
                search_term = f"%{query}%"
                params.extend([search_term, search_term])
            
            if account_id:
                conditions.append("t.account_id = ?")
                params.append(account_id)
            
            if company_id:
                conditions.append("t.company_id = ?")
                params.append(company_id)
            
            if category:
                conditions.append("t.category = ?")
                params.append(category)
            
            if days_back:
                conditions.append("t.transaction_date >= ?")
                cutoff_date = date.today() - timedelta(days=days_back)
                params.append(cutoff_date)
            
            params.append(limit)
            
            where_clause = " AND ".join(conditions)
            
            results = safe_execute(conn, f"""
                SELECT t.*, a.name as account_name, c.name as company_name
                FROM transactions t
                JOIN accounts a ON t.account_id = a.id AND a.deleted_at IS NULL
                LEFT JOIN companies c ON t.company_id = c.id AND c.deleted_at IS NULL
                WHERE {where_clause}
                ORDER BY t.transaction_date DESC, t.created_at DESC
                LIMIT ?
            """, tuple(params))
            
            description = f"Transaction search results"
            if query:
                description += f" for: '{query}'"
            
            return format_results_for_llm(results, description)
            
    except Exception as e:
        return f"Transaction search failed: {str(e)}"

@mcp.tool()
def create_account(name: str, account_type: str, account_number: str = None,
                  bank_name: str = None, balance: float = 0.0) -> str:
    """
    Create a new financial account.
    
    Args:
        name: Account name (required)
        account_type: Account type (checking, savings, credit, investment) (required)
        account_number: Account number (optional, last 4 digits recommended)
        bank_name: Bank or financial institution name (optional)
        balance: Starting balance (optional, default 0.0)
    
    Returns:
        JSON result with account creation status
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Create account
            cursor.execute("""
                INSERT INTO accounts (
                    name, type, account_number, bank_name, balance,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, account_type, account_number, bank_name, balance,
                  datetime.now(), datetime.now()))
            
            account_id = cursor.lastrowid
            conn.commit()
            
            # Get created account
            cursor.execute("SELECT * FROM accounts WHERE id = ?", (account_id,))
            account = dict(cursor.fetchone())
            
            result = OperationResult(
                success=True,
                message=f"Account '{name}' created successfully",
                data={"account_id": account_id, "account": account}
            )
            
            return json.dumps(result.dict(), indent=2, default=str)
            
    except Exception as e:
        error_result = OperationResult(
            success=False,
            message=f"Failed to create account: {str(e)}",
            error_details=str(e)
        )
        return json.dumps(error_result.dict(), indent=2)

@mcp.tool()
def search_accounts(query: str = None, account_type: str = None, active_only: bool = True) -> str:
    """
    Search financial accounts.
    
    Args:
        query: Search term for account name or bank name (optional)
        account_type: Filter by account type (optional)
        active_only: Only return active accounts (default True)
    
    Returns:
        JSON array of matching accounts
    """
    try:
        with get_db_connection() as conn:
            conditions = ["deleted_at IS NULL"]
            params = []
            
            if query:
                conditions.append("(name LIKE ? OR bank_name LIKE ?)")
                search_term = f"%{query}%"
                params.extend([search_term, search_term])
            
            if account_type:
                conditions.append("type = ?")
                params.append(account_type)
            
            if active_only:
                conditions.append("is_active = 1")
            
            where_clause = " AND ".join(conditions)
            
            results = safe_execute(conn, f"""
                SELECT * FROM accounts
                WHERE {where_clause}
                ORDER BY name
            """, tuple(params))
            
            return format_results_for_llm(results, f"Account search results")
            
    except Exception as e:
        return f"Account search failed: {str(e)}"

# =============================================================================
# TASK MANAGEMENT TOOLS
# =============================================================================

@mcp.tool()
def update_task(task_id: int, title: str = None, description: str = None,
               due_date: str = None, priority: str = None, completed: bool = None) -> str:
    """
    Update an existing task.
    
    Args:
        task_id: ID of the task to update (required)
        title: New task title (optional)
        description: New task description (optional)
        due_date: New due date in YYYY-MM-DD format (optional)
        priority: New priority (low, normal, high, urgent) (optional)
        completed: Mark task as completed (optional)
    
    Returns:
        JSON result with update status
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check if task exists
            cursor.execute("SELECT id FROM tasks WHERE id = ? AND deleted_at IS NULL", (task_id,))
            if not cursor.fetchone():
                return json.dumps({"success": False, "message": "Task not found or deleted"})
            
            # Build update query
            update_fields = []
            update_values = []
            
            if title is not None:
                update_fields.append("title = ?")
                update_values.append(title)
            if description is not None:
                update_fields.append("description = ?")
                update_values.append(description)
            if due_date is not None:
                try:
                    parsed_date = datetime.strptime(due_date, "%Y-%m-%d").date()
                    update_fields.append("due_date = ?")
                    update_values.append(parsed_date)
                except:
                    return json.dumps({"success": False, "message": "Invalid date format. Use YYYY-MM-DD"})
            if priority is not None:
                update_fields.append("priority = ?")
                update_values.append(priority)
            if completed is not None:
                update_fields.append("completed = ?")
                update_values.append(completed)
                if completed:
                    update_fields.append("completed_at = ?")
                    update_values.append(datetime.now())
            
            if not update_fields:
                return json.dumps({"success": False, "message": "No fields to update"})
            
            update_values.append(task_id)
            
            update_query = f"""
                UPDATE tasks 
                SET {', '.join(update_fields)}
                WHERE id = ? AND deleted_at IS NULL
            """
            
            cursor.execute(update_query, update_values)
            conn.commit()
            
            # Get updated task
            cursor.execute("""
                SELECT t.*, c.first_name || ' ' || c.last_name as contact_name,
                       comp.name as company_name
                FROM tasks t
                LEFT JOIN contacts c ON t.contact_id = c.id AND c.deleted_at IS NULL
                LEFT JOIN companies comp ON t.company_id = comp.id AND comp.deleted_at IS NULL
                WHERE t.id = ?
            """, (task_id,))
            
            updated_task = dict(cursor.fetchone())
            
            result = OperationResult(
                success=True,
                message="Task updated successfully",
                data={"task": updated_task}
            )
            
            return json.dumps(result.dict(), indent=2, default=str)
            
    except Exception as e:
        error_result = OperationResult(
            success=False,
            message=f"Failed to update task: {str(e)}",
            error_details=str(e)
        )
        return json.dumps(error_result.dict(), indent=2)

@mcp.tool()
def complete_task(task_id: int) -> str:
    """
    Mark a task as completed.
    
    Args:
        task_id: ID of the task to complete
    
    Returns:
        JSON result with completion status
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check if task exists and is not completed
            cursor.execute("""
                SELECT id, title, completed FROM tasks 
                WHERE id = ? AND deleted_at IS NULL
            """, (task_id,))
            task_row = cursor.fetchone()
            
            if not task_row:
                return json.dumps({"success": False, "message": "Task not found or deleted"})
            
            if task_row[2]:  # already completed
                return json.dumps({"success": False, "message": "Task is already completed"})
            
            # Mark as completed
            cursor.execute("""
                UPDATE tasks 
                SET completed = 1, completed_at = ?
                WHERE id = ?
            """, (datetime.now(), task_id))
            
            conn.commit()
            
            result = OperationResult(
                success=True,
                message=f"Task '{task_row[1]}' marked as completed",
                data={"task_id": task_id, "completed_at": datetime.now()}
            )
            
            return json.dumps(result.dict(), indent=2, default=str)
            
    except Exception as e:
        error_result = OperationResult(
            success=False,
            message=f"Failed to complete task: {str(e)}",
            error_details=str(e)
        )
        return json.dumps(error_result.dict(), indent=2)

@mcp.tool()
def search_tasks(query: str = None, contact_id: int = None, company_id: int = None,
                priority: str = None, completed: bool = None, overdue_only: bool = False,
                limit: int = 20) -> str:
    """
    Search tasks with various filters.
    
    Args:
        query: Search term for title or description (optional)
        contact_id: Filter by specific contact (optional)
        company_id: Filter by specific company (optional)
        priority: Filter by priority (low, normal, high, urgent) (optional)
        completed: Filter by completion status (optional)
        overdue_only: Only show overdue tasks (optional)
        limit: Maximum number of results (default 20)
    
    Returns:
        JSON array of matching tasks
    """
    try:
        with get_db_connection() as conn:
            conditions = ["t.deleted_at IS NULL"]
            params = []
            
            if query:
                conditions.append("(t.title LIKE ? OR t.description LIKE ?)")
                search_term = f"%{query}%"
                params.extend([search_term, search_term])
            
            if contact_id:
                conditions.append("t.contact_id = ?")
                params.append(contact_id)
            
            if company_id:
                conditions.append("t.company_id = ?")
                params.append(company_id)
            
            if priority:
                conditions.append("t.priority = ?")
                params.append(priority)
            
            if completed is not None:
                conditions.append("t.completed = ?")
                params.append(completed)
            
            if overdue_only:
                conditions.append("t.due_date < ? AND t.completed = 0")
                params.append(date.today())
            
            params.append(limit)
            
            where_clause = " AND ".join(conditions)
            
            results = safe_execute(conn, f"""
                SELECT t.*, 
                       c.first_name || ' ' || c.last_name as contact_name,
                       comp.name as company_name
                FROM tasks t
                LEFT JOIN contacts c ON t.contact_id = c.id AND c.deleted_at IS NULL
                LEFT JOIN companies comp ON t.company_id = comp.id AND comp.deleted_at IS NULL
                WHERE {where_clause}
                ORDER BY t.due_date ASC, t.priority DESC, t.created_at DESC
                LIMIT ?
            """, tuple(params))
            
            description = "Task search results"
            if query:
                description += f" for: '{query}'"
            
            return format_results_for_llm(results, description)
            
    except Exception as e:
        return f"Task search failed: {str(e)}"

# =============================================================================
# MCP RESOURCES - Read-Only Data Access
# =============================================================================

@mcp.resource("schema://tables")
def get_database_schema() -> str:
    """Get complete database schema information for LLM understanding"""
    schema_info = {
        "database_name": "CRM Database",
        "description": "Integrated CRM, financial, and communication management system",
        "tables": {
            "contacts": {
                "description": "Contact information and relationships",
                "key_fields": ["id", "first_name", "last_name", "email", "company_id", "status"]
            },
            "companies": {
                "description": "Company information",
                "key_fields": ["id", "name", "industry", "website", "phone"]
            },
            "communications": {
                "description": "All communication records (email, messages, physical mail)",
                "key_fields": ["id", "platform", "sender_contact_id", "content", "timestamp", "category"]
            },
            "tasks": {
                "description": "Follow-up tasks and action items",
                "key_fields": ["id", "title", "contact_id", "due_date", "priority", "completed"]
            },
            "transactions": {
                "description": "Financial transactions",
                "key_fields": ["id", "account_id", "amount", "description", "category", "date"]
            },
            "subscriptions": {
                "description": "Recurring subscription services",
                "key_fields": ["id", "service_name", "amount", "billing_cycle", "next_billing_date"]
            },
            "accounts": {
                "description": "Financial accounts (checking, savings, credit)",
                "key_fields": ["id", "name", "type", "balance", "bank_name"]
            }
        },
        "relationships": {
            "contacts_to_companies": "contacts.company_id -> companies.id",
            "communications_to_contacts": "communications.sender_contact_id -> contacts.id",
            "tasks_to_contacts": "tasks.contact_id -> contacts.id",
            "transactions_to_accounts": "transactions.account_id -> accounts.id"
        }
    }
    
    return json.dumps(schema_info, indent=2)

@mcp.resource("contacts://{contact_id}")
def get_contact_resource(contact_id: str) -> str:
    """Get comprehensive contact information including relationships and history"""
    try:
        contact_id_int = int(contact_id)
        return get_contact_timeline(contact_id_int, days_back=180)
    except ValueError:
        return f"Invalid contact ID: {contact_id}"

@mcp.resource("dashboard://summary")
def get_dashboard_summary() -> str:
    """Get CRM dashboard summary with key metrics"""
    try:
        with get_db_connection() as conn:
            # Get counts
            contact_count = safe_execute(conn, "SELECT COUNT(*) as count FROM contacts WHERE status = 'active' AND deleted_at IS NULL")[0][0]
            company_count = safe_execute(conn, "SELECT COUNT(*) as count FROM companies WHERE deleted_at IS NULL")[0][0]
            
            # Communication metrics
            comm_metrics = safe_execute(conn, """
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN processing_status = 'needs_processing' THEN 1 ELSE 0 END) as unprocessed,
                    SUM(CASE WHEN urgency_level = 'urgent' THEN 1 ELSE 0 END) as urgent,
                    SUM(CASE WHEN requires_follow_up = 1 THEN 1 ELSE 0 END) as needs_followup
                FROM communications 
                WHERE communication_timestamp >= date('now', '-30 days')
                  AND deleted_at IS NULL
            """)[0]
            
            # Task metrics
            task_metrics = safe_execute(conn, """
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN completed = 0 THEN 1 ELSE 0 END) as pending,
                    SUM(CASE WHEN completed = 0 AND due_date <= date('now') THEN 1 ELSE 0 END) as overdue
                FROM tasks
                WHERE deleted_at IS NULL
            """)[0]
            
            # Recent activity
            recent_activity = safe_execute(conn, """
                SELECT 
                    'communication' as type,
                    sender_display_name as title,
                    platform || ': ' || substr(message_content_text, 1, 100) as description,
                    communication_timestamp as timestamp
                FROM communications
                WHERE deleted_at IS NULL
                ORDER BY communication_timestamp DESC
                LIMIT 5
            """)
            
            dashboard_data = {
                "metrics": {
                    "active_contacts": contact_count,
                    "total_companies": company_count,
                    "communications_30_days": dict(comm_metrics),
                    "task_summary": dict(task_metrics)
                },
                "recent_activity": [dict(row) for row in recent_activity]
            }
            
            return json.dumps(dashboard_data, indent=2, default=str)
            
    except Exception as e:
        return f"Failed to generate dashboard: {str(e)}"

@mcp.resource("reports://upcoming_tasks")
def get_upcoming_tasks() -> str:
    """Get tasks due in the next 7 days"""
    try:
        with get_db_connection() as conn:
            upcoming_tasks = safe_execute(conn, """
                SELECT 
                    t.*,
                    c.first_name || ' ' || c.last_name as contact_name,
                    comp.name as company_name
                FROM tasks t
                LEFT JOIN contacts c ON t.contact_id = c.id AND c.deleted_at IS NULL
                LEFT JOIN companies comp ON t.company_id = comp.id AND comp.deleted_at IS NULL
                WHERE t.completed = 0
                  AND t.due_date BETWEEN date('now') AND date('now', '+7 days')
                  AND t.deleted_at IS NULL
                ORDER BY t.due_date, t.priority DESC
            """)
            
            return format_results_for_llm(upcoming_tasks, "Tasks due in the next 7 days")
            
    except Exception as e:
        return f"Failed to get upcoming tasks: {str(e)}"

# =============================================================================
# WORKFLOW INTEGRATION TOOLS
# =============================================================================

def trigger_workflow_async(workflow_name: str, trigger_event: str, trigger_data: Dict[str, Any]):
    """Trigger workflow asynchronously (non-blocking)"""
    try:
        # This would call the workflow MCP server
        # For now, just log the trigger
        logger.info(f"Workflow trigger: {workflow_name} for event {trigger_event}")
        
        # In production, this would make an HTTP call to workflow server
        # requests.post("http://localhost:3001/trigger", json={
        #     "workflow_name": workflow_name,
        #     "trigger_event": trigger_event,
        #     "trigger_data": trigger_data
        # })
        
    except Exception as e:
        logger.error(f"Failed to trigger workflow: {e}")

@mcp.tool()
def create_communication_with_workflow(platform: str, sender_identifier: str, content: str,
                                     subject: str = None, direction: str = "incoming",
                                     sender_name: str = None, timestamp: str = None,
                                     auto_trigger_workflows: bool = True) -> str:
    """
    Create a new communication record with automatic workflow triggering.
    
    Args:
        platform: Communication platform (email, imessage, whatsapp, etc.)
        sender_identifier: Platform-specific sender ID (email, phone, username)
        content: Message content
        subject: Subject line or conversation topic (optional)
        direction: 'incoming' or 'outgoing' (default: incoming)
        sender_name: Display name of sender (optional)
        timestamp: ISO timestamp string (optional, uses current time if not provided)
        auto_trigger_workflows: Whether to automatically trigger workflows (default: True)
    
    Returns:
        JSON result with communication creation status
    """
    try:
        # Create the communication using existing function
        result = create_communication(platform, sender_identifier, content, subject, 
                                    direction, sender_name, timestamp)
        
        if auto_trigger_workflows:
            # Parse the result to get communication data
            result_data = json.loads(result)
            
            if result_data.get("success"):
                comm_id = result_data["data"]["communication_id"]
                
                # Get the full communication record for workflow trigger
                with get_db_connection() as conn:
                    comm_record = safe_execute(conn, """
                        SELECT * FROM communications WHERE id = ?
                    """, (comm_id,))
                    
                    if comm_record:
                        comm_dict = dict(comm_record[0])
                        
                        # Trigger workflow asynchronously
                        trigger_workflow_async(
                            workflow_name="DMV Document Processing",
                            trigger_event="communication.created",
                            trigger_data=comm_dict
                        )
        
        return result
        
    except Exception as e:
        error_result = OperationResult(
            success=False,
            message=f"Failed to create communication with workflow: {str(e)}",
            error_details=str(e)
        )
        return json.dumps(error_result.dict(), indent=2)

@mcp.tool()
def update_communication_fields(communication_id: int, updates: dict) -> str:
    """
    Update specific fields of a communication record.
    
    Args:
        communication_id: ID of the communication to update
        updates: Dictionary of field names and values to update
    
    Returns:
        JSON result with update status
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Build dynamic update query
            set_clauses = []
            update_values = []
            
            for field, value in updates.items():
                # Convert field names from workflow format to database format
                if field == "sender_company_id":
                    set_clauses.append("sender_company_id = ?")
                    update_values.append(value)
                elif field == "ai_generated_summary":
                    set_clauses.append("ai_generated_summary = ?")
                    update_values.append(json.dumps(value) if isinstance(value, dict) else str(value))
                elif field == "ai_extracted_entities":
                    set_clauses.append("ai_extracted_entities = ?")
                    update_values.append(json.dumps(value) if isinstance(value, dict) else str(value))
                elif field == "urgency_level":
                    set_clauses.append("urgency_level = ?")
                    update_values.append(value)
                elif field == "requires_follow_up":
                    set_clauses.append("requires_follow_up = ?")
                    update_values.append(1 if value else 0)
                elif field == "follow_up_due_date":
                    set_clauses.append("follow_up_due_date = ?")
                    update_values.append(value)
                elif field == "content_category":
                    set_clauses.append("content_category = ?")
                    update_values.append(value)
            
            if not set_clauses:
                raise ValueError("No valid fields provided for update")
            
            # Add updated_at timestamp
            set_clauses.append("updated_at = CURRENT_TIMESTAMP")
            update_values.append(communication_id)
            
            update_query = f"""
                UPDATE communications 
                SET {', '.join(set_clauses)}
                WHERE id = ? AND deleted_at IS NULL
            """
            
            cursor.execute(update_query, update_values)
            
            if cursor.rowcount == 0:
                raise ValueError(f"Communication {communication_id} not found or already deleted")
            
            conn.commit()
            
            result = OperationResult(
                success=True,
                message=f"Communication {communication_id} updated successfully",
                data={"communication_id": communication_id, "updated_fields": list(updates.keys())}
            )
            
            return json.dumps(result.dict(), indent=2)
            
    except Exception as e:
        error_result = OperationResult(
            success=False,
            message=f"Failed to update communication: {str(e)}",
            error_details=str(e)
        )
        return json.dumps(error_result.dict(), indent=2)

@mcp.tool()
def get_communication_with_workflow_data(communication_id: int) -> str:
    """
    Get communication record with all workflow-enhanced data.
    
    Args:
        communication_id: ID of the communication to retrieve
    
    Returns:
        JSON with complete communication information including AI analysis
    """
    try:
        with get_db_connection() as conn:
            # Get communication with all related data
            comm_record = safe_execute(conn, """
                SELECT 
                    c.*,
                    comp.name as sender_company_name,
                    cont.first_name || ' ' || cont.last_name as sender_contact_name
                FROM communications c
                LEFT JOIN companies comp ON c.sender_company_id = comp.id AND comp.deleted_at IS NULL
                LEFT JOIN contacts cont ON c.sender_contact_id = cont.id AND cont.deleted_at IS NULL
                WHERE c.id = ? AND c.deleted_at IS NULL
            """, (communication_id,))
            
            if not comm_record:
                raise ValueError(f"Communication {communication_id} not found")
            
            comm_data = dict(comm_record[0])
            
            # Parse JSON fields
            if comm_data.get('ai_extracted_entities'):
                try:
                    comm_data['ai_extracted_entities'] = json.loads(comm_data['ai_extracted_entities'])
                except:
                    pass
            
            result = OperationResult(
                success=True,
                message="Communication retrieved successfully",
                data={"communication": comm_data}
            )
            
            return json.dumps(result.dict(), indent=2, default=str)
            
    except Exception as e:
        error_result = OperationResult(
            success=False,
            message=f"Failed to get communication: {str(e)}",
            error_details=str(e)
        )
        return json.dumps(error_result.dict(), indent=2)

# =============================================================================
# SERVER SETUP
# =============================================================================

if __name__ == "__main__":
    # Run the server
    mcp.run()