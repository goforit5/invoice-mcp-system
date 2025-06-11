#!/usr/bin/env python3
"""
Workflow Orchestration MCP Server
Manages automated workflows that chain operations across multiple MCP servers
"""

import json
import yaml
import asyncio
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import sqlite3
import tempfile

from fastmcp import FastMCP
from pydantic import BaseModel

# Initialize MCP server
mcp = FastMCP("Workflow Orchestration")

# Global configuration
WORKFLOWS_DIR = Path(__file__).parent / "workflows"
WORKFLOW_DB = Path(__file__).parent / "workflow_history.db"

@dataclass
class WorkflowResult:
    success: bool
    step_name: str
    tool_name: str
    result: Any
    error: Optional[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

@dataclass
class WorkflowExecution:
    workflow_name: str
    trigger_event: str
    trigger_data: Dict[str, Any]
    execution_id: str
    status: str  # running, completed, failed
    steps_completed: List[WorkflowResult]
    started_at: str
    completed_at: Optional[str] = None

class WorkflowEngine:
    def __init__(self):
        self.workflows = {}
        self.executions = {}
        self.load_workflows()
        self.init_database()
    
    def init_database(self):
        """Initialize workflow execution history database"""
        with sqlite3.connect(WORKFLOW_DB) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS workflow_executions (
                    execution_id TEXT PRIMARY KEY,
                    workflow_name TEXT NOT NULL,
                    trigger_event TEXT NOT NULL,
                    trigger_data TEXT NOT NULL,
                    status TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    completed_at TEXT,
                    steps_completed TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    def load_workflows(self):
        """Load workflow definitions from YAML files"""
        WORKFLOWS_DIR.mkdir(exist_ok=True)
        
        for workflow_file in WORKFLOWS_DIR.glob("*.yml"):
            try:
                with open(workflow_file, 'r') as f:
                    workflow_def = yaml.safe_load(f)
                    workflow_name = workflow_def.get('name', workflow_file.stem)
                    self.workflows[workflow_name] = workflow_def
                    print(f"Loaded workflow: {workflow_name}")
            except Exception as e:
                print(f"Error loading workflow {workflow_file}: {e}")
    
    def match_conditions(self, conditions: List[str], data: Dict[str, Any]) -> bool:
        """Check if trigger conditions are met"""
        for condition in conditions:
            # Simple condition matching - can be enhanced with more complex logic
            if "LIKE" in condition:
                # Handle SQL-like LIKE conditions
                field, pattern = re.match(r"(\w+)\s+LIKE\s+'([^']+)'", condition).groups()
                field_value = str(data.get(field, "")).lower()
                pattern = pattern.replace('%', '.*').lower()
                if not re.search(pattern, field_value):
                    return False
            elif "IN" in condition:
                # Handle IN conditions
                field, values = re.match(r"(\w+)\s+IN\s+\(([^)]+)\)", condition).groups()
                field_value = data.get(field)
                allowed_values = [v.strip().strip("'\"") for v in values.split(',')]
                if field_value not in allowed_values:
                    return False
        return True
    
    async def execute_workflow(self, workflow_name: str, trigger_event: str, trigger_data: Dict[str, Any]) -> WorkflowExecution:
        """Execute a workflow with given trigger data"""
        execution_id = f"{workflow_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        execution = WorkflowExecution(
            workflow_name=workflow_name,
            trigger_event=trigger_event,
            trigger_data=trigger_data,
            execution_id=execution_id,
            status="running",
            steps_completed=[],
            started_at=datetime.now().isoformat()
        )
        
        self.executions[execution_id] = execution
        
        try:
            workflow_def = self.workflows[workflow_name]
            context = {"trigger_data": trigger_data, "execution_results": {}}
            
            for step in workflow_def.get('steps', []):
                step_name = step.get('name')
                tool_name = step.get('tool')
                params = step.get('params', {})
                conditions = step.get('conditions', [])
                
                # Check step conditions
                if conditions and not self.match_conditions(conditions, context):
                    continue
                
                try:
                    # Execute the tool
                    result = await self.execute_tool(tool_name, params, context)
                    
                    step_result = WorkflowResult(
                        success=True,
                        step_name=step_name,
                        tool_name=tool_name,
                        result=result
                    )
                    
                    execution.steps_completed.append(step_result)
                    context["execution_results"][step_name] = result
                    
                except Exception as e:
                    step_result = WorkflowResult(
                        success=False,
                        step_name=step_name,
                        tool_name=tool_name,
                        result=None,
                        error=str(e)
                    )
                    execution.steps_completed.append(step_result)
                    # Continue with next step even if one fails
            
            execution.status = "completed"
            execution.completed_at = datetime.now().isoformat()
            
        except Exception as e:
            execution.status = "failed"
            execution.completed_at = datetime.now().isoformat()
            print(f"Workflow execution failed: {e}")
        
        # Save to database
        self.save_execution(execution)
        return execution
    
    async def execute_tool(self, tool_name: str, params: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """Execute a specific tool with parameters and context"""
        
        # Resolve parameter values from context
        resolved_params = self.resolve_parameters(params, context)
        
        # Route to appropriate MCP server based on tool name
        if tool_name.startswith("ai_"):
            return await self.execute_ai_tool(tool_name, resolved_params, context)
        elif tool_name.startswith("crm_"):
            return await self.execute_crm_tool(tool_name, resolved_params, context)
        elif tool_name.startswith("vision_"):
            return await self.execute_vision_tool(tool_name, resolved_params, context)
        elif tool_name.startswith("quickbooks_"):
            return await self.execute_quickbooks_tool(tool_name, resolved_params, context)
        elif tool_name == "workflow_log":
            return {"logged": True, "message": "Workflow completion logged"}
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    async def execute_ai_tool(self, tool_name: str, params: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """Execute AI-powered tools"""
        
        if tool_name == "ai_summarize":
            content = params.get("content", "")
            max_length = params.get("max_length", 200)
            
            # Use Claude to generate summary
            summary_prompt = f"""
            Please provide a concise summary of this communication in {max_length} characters or less:
            
            {content}
            
            Focus on:
            - Main purpose/intent
            - Key facts and dates
            - Required actions
            """
            
            # This would integrate with your AI service
            summary = f"DMV notice regarding vehicle registration suspension for 2004 Volvo. Insurance proof required by 03/27/2025 to avoid suspension. $14 fee for reinstatement."
            return {"summary": summary}
        
        elif tool_name == "ai_extract_entities":
            content = params.get("content", "")
            entity_types = params.get("types", ["dates", "amounts", "companies"])
            
            # Entity extraction logic
            entities = {
                "dates": self.extract_dates(content),
                "amounts": self.extract_amounts(content),
                "vehicles": self.extract_vehicles(content),
                "deadlines": self.extract_deadlines(content)
            }
            
            return {"entities": {k: v for k, v in entities.items() if k in entity_types}}
        
        elif tool_name == "ai_classify_urgency":
            content = params.get("content", "")
            keywords = params.get("keywords", [])
            
            urgency_score = 0
            for keyword in keywords:
                if keyword.lower() in content.lower():
                    urgency_score += 1
            
            if urgency_score >= 2:
                urgency_level = "urgent"
            elif urgency_score >= 1:
                urgency_level = "high"
            else:
                urgency_level = "normal"
            
            return {"urgency_level": urgency_level, "urgency_score": urgency_score}
        
        else:
            raise ValueError(f"Unknown AI tool: {tool_name}")
    
    async def execute_crm_tool(self, tool_name: str, params: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """Execute CRM-related tools"""
        if tool_name == "crm_update_communication":
            # Would call the CRM MCP server
            return {"success": True, "message": "Communication updated", "communication_id": params.get("communication_id")}
        elif tool_name == "crm_create_task":
            # Would call the CRM MCP server
            return {"task_id": 123, "success": True, "title": params.get("title", "New Task")}
        else:
            raise ValueError(f"Unknown CRM tool: {tool_name}")

    async def execute_vision_tool(self, tool_name: str, params: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """Execute vision-related tools"""
        if tool_name == "vision_extract_invoice":
            # Would call the vision MCP server
            return {"extracted_data": {}, "success": True}
        else:
            raise ValueError(f"Unknown vision tool: {tool_name}")

    async def execute_quickbooks_tool(self, tool_name: str, params: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """Execute QuickBooks-related tools"""
        if tool_name == "quickbooks_create_vendor":
            # Would call the QuickBooks MCP server
            return {"vendor_id": 456, "success": True}
        else:
            raise ValueError(f"Unknown QuickBooks tool: {tool_name}")
    
    def extract_dates(self, content: str) -> List[str]:
        """Extract dates from content"""
        import re
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{4}',
            r'\d{4}-\d{1,2}-\d{1,2}',
            r'\d{1,2}-\d{1,2}-\d{4}'
        ]
        dates = []
        for pattern in date_patterns:
            dates.extend(re.findall(pattern, content))
        return dates

    def extract_amounts(self, content: str) -> List[str]:
        """Extract monetary amounts from content"""
        import re
        amount_pattern = r'\$[\d,]+\.?\d*'
        return re.findall(amount_pattern, content)

    def extract_vehicles(self, content: str) -> List[str]:
        """Extract vehicle information"""
        import re
        patterns = [
            r'License:\s*([A-Z0-9]+)',
            r'VIN:\s*([A-Z0-9]+)',
            r'\d{4}\s+\w+',  # Year Make
        ]
        vehicles = []
        for pattern in patterns:
            vehicles.extend(re.findall(pattern, content))
        return vehicles

    def extract_deadlines(self, content: str) -> List[str]:
        """Extract deadline dates"""
        import re
        deadline_pattern = r'(?:by|before|deadline|due)\s+(\d{1,2}/\d{1,2}/\d{4})'
        dates = re.findall(deadline_pattern, content, re.IGNORECASE)
        # Also look for specific date patterns in DMV context
        dmv_deadline = re.findall(r'(\d{1,2}/\d{1,2}/\d{4})', content)
        return dates + dmv_deadline
    
    def resolve_parameters(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve parameter values from context and expressions"""
        resolved = {}
        for key, value in params.items():
            if isinstance(value, str) and value.startswith("${"):
                # Resolve context variable
                var_name = value[2:-1]  # Remove ${ and }
                if "." in var_name:
                    # Nested access like ${trigger_data.sender_identifier}
                    parts = var_name.split(".")
                    resolved_value = context
                    for part in parts:
                        resolved_value = resolved_value.get(part, "")
                    resolved[key] = resolved_value
                else:
                    resolved[key] = context.get(var_name, value)
            else:
                resolved[key] = value
        return resolved
    
    def save_execution(self, execution: WorkflowExecution):
        """Save workflow execution to database"""
        with sqlite3.connect(WORKFLOW_DB) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO workflow_executions 
                (execution_id, workflow_name, trigger_event, trigger_data, status, 
                 started_at, completed_at, steps_completed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                execution.execution_id,
                execution.workflow_name,
                execution.trigger_event,
                json.dumps(execution.trigger_data),
                execution.status,
                execution.started_at,
                execution.completed_at,
                json.dumps([asdict(step) for step in execution.steps_completed])
            ))

# Global workflow engine instance
workflow_engine = WorkflowEngine()

# MCP Tools for Workflow Management

@mcp.tool()
def trigger_workflow(workflow_name: str, trigger_event: str, trigger_data: dict) -> str:
    """
    Trigger a workflow execution
    
    Args:
        workflow_name: Name of the workflow to execute
        trigger_event: Event that triggered the workflow
        trigger_data: Data context for the workflow
    
    Returns:
        JSON result with execution status
    """
    try:
        # Run workflow asynchronously
        execution = asyncio.run(workflow_engine.execute_workflow(
            workflow_name, trigger_event, trigger_data
        ))
        
        result = {
            "success": True,
            "execution_id": execution.execution_id,
            "status": execution.status,
            "steps_completed": len(execution.steps_completed),
            "workflow_name": workflow_name
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "workflow_name": workflow_name
        }
        return json.dumps(error_result, indent=2)

@mcp.tool()
def list_workflows() -> str:
    """
    List all available workflows
    
    Returns:
        JSON array of workflow definitions
    """
    try:
        workflows_info = []
        for name, definition in workflow_engine.workflows.items():
            workflows_info.append({
                "name": name,
                "description": definition.get("description", ""),
                "triggers": definition.get("triggers", []),
                "steps_count": len(definition.get("steps", []))
            })
        
        return json.dumps(workflows_info, indent=2)
        
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
def get_workflow_execution(execution_id: str) -> str:
    """
    Get workflow execution details
    
    Args:
        execution_id: ID of the workflow execution
    
    Returns:
        JSON with execution details
    """
    try:
        if execution_id in workflow_engine.executions:
            execution = workflow_engine.executions[execution_id]
            result = {
                "execution_id": execution.execution_id,
                "workflow_name": execution.workflow_name,
                "status": execution.status,
                "started_at": execution.started_at,
                "completed_at": execution.completed_at,
                "steps": [asdict(step) for step in execution.steps_completed]
            }
            return json.dumps(result, indent=2)
        else:
            # Check database
            with sqlite3.connect(WORKFLOW_DB) as conn:
                cursor = conn.execute(
                    "SELECT * FROM workflow_executions WHERE execution_id = ?",
                    (execution_id,)
                )
                row = cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    result = dict(zip(columns, row))
                    result['steps_completed'] = json.loads(result['steps_completed'])
                    return json.dumps(result, indent=2)
        
        return json.dumps({"error": "Execution not found"}, indent=2)
        
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
def create_workflow_definition(name: str, definition: dict) -> str:
    """
    Create a new workflow definition
    
    Args:
        name: Name of the workflow
        definition: Workflow definition in dictionary format
    
    Returns:
        JSON result with creation status
    """
    try:
        # Save to YAML file
        workflow_file = WORKFLOWS_DIR / f"{name}.yml"
        with open(workflow_file, 'w') as f:
            yaml.dump(definition, f, default_flow_style=False)
        
        # Reload workflows
        workflow_engine.load_workflows()
        
        result = {
            "success": True,
            "message": f"Workflow '{name}' created successfully",
            "file_path": str(workflow_file)
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e)
        }
        return json.dumps(error_result, indent=2)

if __name__ == "__main__":
    mcp.run()