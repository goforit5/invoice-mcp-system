#!/usr/bin/env python3
"""
Data Models for CRM System

Pydantic models for structured data processing by LLM agents.
These models provide clear schemas for all CRM data operations.
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date
from pydantic import BaseModel, Field, validator
from enum import Enum

# Enums for standardized values
class ContactStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    prospect = "prospect"

class Platform(str, Enum):
    email = "email"
    physical_mail = "physical_mail"
    imessage = "imessage"
    whatsapp = "whatsapp"
    instagram_dm = "instagram_dm"
    sms = "sms"
    slack = "slack"
    telegram = "telegram"

class Direction(str, Enum):
    incoming = "incoming"
    outgoing = "outgoing"

class ProcessingStatus(str, Enum):
    needs_processing = "needs_processing"
    processed = "processed"
    archived = "archived"
    flagged_for_review = "flagged_for_review"

class ContentCategory(str, Enum):
    business = "business"
    personal = "personal"
    financial = "financial"
    legal = "legal"
    marketing = "marketing"
    notification = "notification"
    bill = "bill"
    invoice = "invoice"

class UrgencyLevel(str, Enum):
    low = "low"
    normal = "normal"
    high = "high"
    urgent = "urgent"

class TaskPriority(str, Enum):
    low = "low"
    normal = "normal"
    high = "high"
    urgent = "urgent"

# Core Models
class Contact(BaseModel):
    """Contact information model"""
    id: Optional[int] = None
    first_name: str = Field(..., description="Contact's first name")
    last_name: str = Field(..., description="Contact's last name")
    email: Optional[str] = Field(None, description="Primary email address")
    phone: Optional[str] = Field(None, description="Primary phone number")
    title: Optional[str] = Field(None, description="Job title or position")
    company_id: Optional[int] = Field(None, description="Associated company ID")
    notes: Optional[str] = Field(None, description="Additional notes about contact")
    status: ContactStatus = Field(ContactStatus.active, description="Contact status")
    source: Optional[str] = Field(None, description="How you met this contact")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @property
    def full_name(self) -> str:
        """Get full name"""
        return f"{self.first_name} {self.last_name}"

class Company(BaseModel):
    """Company information model"""
    id: Optional[int] = None
    name: str = Field(..., description="Company name")
    industry: Optional[str] = Field(None, description="Industry category")
    website: Optional[str] = Field(None, description="Company website URL")
    phone: Optional[str] = Field(None, description="Main company phone")
    address: Optional[str] = Field(None, description="Company address")
    notes: Optional[str] = Field(None, description="Additional company notes")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class Communication(BaseModel):
    """Communication record model"""
    id: Optional[int] = None
    
    # Platform and source
    platform: Platform = Field(..., description="Communication platform")
    platform_message_id: Optional[str] = Field(None, description="Unique ID from source platform")
    platform_thread_id: Optional[str] = Field(None, description="Thread ID on source platform")
    
    # Contact relationships
    sender_contact_id: Optional[int] = Field(None, description="ID of sending contact")
    recipient_contact_id: Optional[int] = Field(None, description="ID of receiving contact")
    sender_company_id: Optional[int] = Field(None, description="ID of sender's company")
    
    # Sender information
    sender_display_name: Optional[str] = Field(None, description="Display name of sender")
    sender_identifier: str = Field(..., description="Platform-specific sender identifier")
    sender_platform_username: Optional[str] = Field(None, description="Username on platform")
    
    # Recipient information
    recipient_identifier: Optional[str] = Field(None, description="Platform-specific recipient identifier")
    is_group_conversation: bool = Field(False, description="Whether this is a group chat")
    group_name: Optional[str] = Field(None, description="Name of group chat")
    group_participants: Optional[List[str]] = Field(None, description="List of group participants")
    
    # Content
    subject_line: Optional[str] = Field(None, description="Subject or conversation topic")
    message_content_text: str = Field(..., description="Main message content")
    message_content_html: Optional[str] = Field(None, description="HTML content for emails")
    content_language: str = Field("english", description="Content language")
    
    # Media and attachments
    has_media_attachments: bool = Field(False, description="Whether message has attachments")
    media_type: Optional[str] = Field(None, description="Type of media content")
    attachment_count: int = Field(0, description="Number of attachments")
    
    # Metadata
    direction: Direction = Field(..., description="Message direction")
    communication_timestamp: datetime = Field(..., description="When message was sent/received")
    processed_timestamp: Optional[datetime] = Field(None, description="When message was processed")
    
    # Processing and classification
    processing_status: ProcessingStatus = Field(ProcessingStatus.needs_processing)
    content_category: Optional[ContentCategory] = Field(None, description="Message category")
    conversation_type: Optional[str] = Field(None, description="Type of conversation")
    urgency_level: UrgencyLevel = Field(UrgencyLevel.normal, description="Message urgency")
    
    # Actions and follow-up
    requires_follow_up: bool = Field(False, description="Whether follow-up is needed")
    follow_up_due_date: Optional[date] = Field(None, description="When follow-up is due")
    action_items_extracted: Optional[List[str]] = Field(None, description="Extracted action items")
    
    # File storage
    original_file_path: Optional[str] = Field(None, description="Path to original file")
    content_extraction_confidence: Optional[float] = Field(None, description="OCR confidence score")
    
    # Platform-specific data
    platform_specific_data: Optional[Dict[str, Any]] = Field(None, description="Platform metadata")
    
    # Threading
    conversation_thread_global_id: Optional[str] = Field(None, description="Global conversation ID")
    reply_to_communication_id: Optional[int] = Field(None, description="ID of message being replied to")
    
    # AI processing
    ai_generated_summary: Optional[str] = Field(None, description="AI-generated summary")
    ai_extracted_entities: Optional[List[Dict[str, Any]]] = Field(None, description="AI-extracted entities")
    ai_sentiment_score: Optional[float] = Field(None, description="Sentiment analysis score")
    
    # Manual annotations
    manual_notes: Optional[str] = Field(None, description="Human-added notes")
    custom_tags: Optional[List[str]] = Field(None, description="User-defined tags")
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class Task(BaseModel):
    """Task model for follow-ups and actions"""
    id: Optional[int] = None
    contact_id: Optional[int] = Field(None, description="Associated contact ID")
    company_id: Optional[int] = Field(None, description="Associated company ID")
    communication_id: Optional[int] = Field(None, description="Communication that created this task")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    due_date: Optional[date] = Field(None, description="Task due date")
    priority: TaskPriority = Field(TaskPriority.normal, description="Task priority")
    completed: bool = Field(False, description="Whether task is completed")
    task_type: Optional[str] = Field(None, description="Type of task")
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class Transaction(BaseModel):
    """Financial transaction model"""
    id: Optional[int] = None
    account_id: int = Field(..., description="Account ID for transaction")
    amount: float = Field(..., description="Transaction amount (negative for expenses)")
    description: str = Field(..., description="Transaction description")
    category: Optional[str] = Field(None, description="Transaction category")
    vendor_name: Optional[str] = Field(None, description="Vendor name")
    company_id: Optional[int] = Field(None, description="Associated company ID")
    subscription_id: Optional[int] = Field(None, description="Associated subscription ID")
    transaction_date: date = Field(..., description="Date of transaction")
    transaction_type: Optional[str] = Field(None, description="Type of transaction")
    notes: Optional[str] = Field(None, description="Additional notes")
    created_at: Optional[datetime] = None

class Account(BaseModel):
    """Financial account model"""
    id: Optional[int] = None
    name: str = Field(..., description="Account name")
    type: str = Field(..., description="Account type (checking, savings, credit, etc.)")
    account_number: Optional[str] = Field(None, description="Account number (last 4 digits)")
    bank_name: Optional[str] = Field(None, description="Bank name")
    balance: float = Field(0.0, description="Current balance")
    is_active: bool = Field(True, description="Whether account is active")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class Subscription(BaseModel):
    """Subscription service model"""
    id: Optional[int] = None
    service_name: str = Field(..., description="Name of subscription service")
    company_id: Optional[int] = Field(None, description="Associated company ID")
    amount: float = Field(..., description="Subscription amount")
    currency: str = Field("USD", description="Currency code")
    billing_cycle: str = Field(..., description="Billing frequency")
    next_billing_date: date = Field(..., description="Next billing date")
    account_id: Optional[int] = Field(None, description="Account charged for subscription")
    category: Optional[str] = Field(None, description="Subscription category")
    is_active: bool = Field(True, description="Whether subscription is active")
    notes: Optional[str] = Field(None, description="Additional notes")
    created_at: Optional[datetime] = None

# Search and query models
class SearchResult(BaseModel):
    """Generic search result model"""
    type: str = Field(..., description="Type of result (contact, communication, etc.)")
    id: int = Field(..., description="Record ID")
    title: str = Field(..., description="Result title")
    summary: str = Field(..., description="Brief summary")
    relevance_score: Optional[float] = Field(None, description="Search relevance score")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class CommunicationSummary(BaseModel):
    """Communication summary for dashboard/reports"""
    total_communications: int
    unprocessed_count: int
    urgent_count: int
    requiring_follow_up: int
    by_platform: Dict[str, int]
    by_category: Dict[str, int]
    recent_activity: List[Dict[str, Any]]

class ContactSummary(BaseModel):
    """Contact summary with interaction metrics"""
    contact: Contact
    total_communications: int
    last_interaction_date: Optional[datetime]
    interaction_frequency: str  # "high", "medium", "low"
    pending_tasks: int
    relationship_strength: str  # "strong", "medium", "weak"

# Request/Response models for API operations
class CreateContactRequest(BaseModel):
    """Request model for creating a contact"""
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    title: Optional[str] = None
    company_name: Optional[str] = None  # Will create/link company
    notes: Optional[str] = None
    source: Optional[str] = None

class CreateCommunicationRequest(BaseModel):
    """Request model for creating a communication"""
    platform: Platform
    sender_identifier: str
    content: str
    subject: Optional[str] = None
    timestamp: Optional[datetime] = None
    direction: Direction = Direction.incoming
    platform_metadata: Optional[Dict[str, Any]] = None

class SearchRequest(BaseModel):
    """Request model for search operations"""
    query: str
    search_type: Optional[str] = None  # "contacts", "communications", "all"
    limit: int = 50
    include_archived: bool = False
    date_range: Optional[Dict[str, date]] = None

# Response models
class OperationResult(BaseModel):
    """Standard operation result"""
    success: bool
    message: str
    data: Optional[Any] = None
    error_details: Optional[str] = None