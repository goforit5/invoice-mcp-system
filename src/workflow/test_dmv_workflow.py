#!/usr/bin/env python3
"""
Test script for DMV Document Processing Workflow
Demonstrates end-to-end workflow orchestration
"""

import json
import sys
import asyncio
from pathlib import Path

# Add project path
sys.path.append(str(Path(__file__).parent.parent))

from workflow.server import WorkflowEngine

async def test_dmv_workflow():
    """Test the DMV document processing workflow"""
    
    print("🚀 Testing DMV Document Processing Workflow")
    print("=" * 60)
    
    # Initialize workflow engine
    engine = WorkflowEngine()
    
    # Sample DMV communication data (from our earlier processing)
    dmv_communication_data = {
        "id": 4,
        "platform": "mail",
        "sender_identifier": "dmv.ca.gov",
        "sender_display_name": "California Department of Motor Vehicles",
        "subject_line": "Notice of Intent to Suspend - License Plate 6YIH881",
        "message_content_text": "NOTICE OF INTENT TO SUSPEND vehicle registration for 2004 Volvo (License: 6YIH881, VIN: YV1SW64A642416622). DMV does not have record of insurance coverage. Must provide liability insurance proof by 03/27/2025 or registration will be suspended. $14.00 fee required for reinstatement after suspension.",
        "direction": "incoming",
        "communication_timestamp": "2025-02-21 12:00:00",
        "urgency_level": "normal"
    }
    
    print(f"📧 Processing communication: {dmv_communication_data['subject_line']}")
    print(f"📤 From: {dmv_communication_data['sender_display_name']}")
    print()
    
    try:
        # Execute the workflow
        execution = await engine.execute_workflow(
            workflow_name="DMV Document Processing",
            trigger_event="communication.created",
            trigger_data=dmv_communication_data
        )
        
        print(f"✅ Workflow Execution ID: {execution.execution_id}")
        print(f"📊 Status: {execution.status}")
        print(f"⏱️  Started: {execution.started_at}")
        print(f"🏁 Completed: {execution.completed_at}")
        print(f"📋 Steps Completed: {len(execution.steps_completed)}")
        print()
        
        # Show step-by-step results
        print("🔍 Step-by-Step Results:")
        print("-" * 40)
        
        for i, step in enumerate(execution.steps_completed, 1):
            status_emoji = "✅" if step.success else "❌"
            print(f"{i}. {status_emoji} {step.step_name}")
            print(f"   Tool: {step.tool_name}")
            print(f"   Timestamp: {step.timestamp}")
            
            if step.success and step.result:
                if isinstance(step.result, dict):
                    # Show key results
                    if step.step_name == "ai_summary":
                        summary = step.result.get("summary", "")
                        print(f"   Summary: {summary[:100]}...")
                    elif step.step_name == "extract_entities":
                        entities = step.result.get("entities", {})
                        print(f"   Entities: {json.dumps(entities, indent=6)}")
                    elif step.step_name == "classify_urgency":
                        urgency = step.result.get("urgency_level", "unknown")
                        score = step.result.get("urgency_score", 0)
                        print(f"   Urgency: {urgency} (score: {score})")
                    else:
                        print(f"   Result: {step.result}")
                else:
                    print(f"   Result: {step.result}")
            elif step.error:
                print(f"   Error: {step.error}")
            
            print()
        
        # Show workflow summary
        print("📈 Workflow Summary:")
        print("-" * 20)
        print(f"• AI Summary Generated: {'✅' if any(s.step_name == 'ai_summary' and s.success for s in execution.steps_completed) else '❌'}")
        print(f"• Entities Extracted: {'✅' if any(s.step_name == 'extract_entities' and s.success for s in execution.steps_completed) else '❌'}")
        print(f"• Urgency Classified: {'✅' if any(s.step_name == 'classify_urgency' and s.success for s in execution.steps_completed) else '❌'}")
        print(f"• Company Linked: {'✅' if any(s.step_name == 'link_company' and s.success for s in execution.steps_completed) else '❌'}")
        print(f"• Follow-up Task Created: {'✅' if any(s.step_name == 'create_follow_up_task' and s.success for s in execution.steps_completed) else '❌'}")
        print()
        
        # Show what would happen in production
        print("🔮 Production Integration:")
        print("-" * 25)
        print("In production, this workflow would:")
        print("1. Call OpenAI/Claude API for AI summarization")
        print("2. Update CRM communication record with AI insights")
        print("3. Create high-priority task with deadline")
        print("4. Send notifications/alerts for urgent items")
        print("5. Link related entities across all MCP servers")
        print("6. Generate follow-up reminders")
        print()
        
        return execution
        
    except Exception as e:
        print(f"❌ Workflow execution failed: {e}")
        return None

def demonstrate_workflow_concepts():
    """Show the key concepts and benefits"""
    print("💡 Workflow Engine Key Concepts:")
    print("=" * 40)
    print()
    
    print("🏗️  **Architecture Benefits:**")
    print("   • Cross-MCP orchestration (CRM + Vision + QuickBooks + AI)")
    print("   • Event-driven automation (documents trigger workflows)")
    print("   • Declarative YAML workflow definitions")
    print("   • Async execution with full audit trails")
    print("   • Conditional logic and parameter resolution")
    print()
    
    print("🔄 **Workflow Patterns:**")
    print("   • Document Processing → AI Analysis → CRM Updates → Task Creation")
    print("   • Invoice → Vision Extraction → QB Vendor Match → CRM Tracking")
    print("   • Communication → Entity Extraction → Auto-categorization → Follow-ups")
    print()
    
    print("📊 **Scalability for 100s of Workflows:**")
    print("   • YAML-based workflow definitions (easy to create/modify)")
    print("   • Pluggable tool system (add new MCPs seamlessly)")
    print("   • Conditional execution (smart workflow routing)")
    print("   • Database-backed execution history")
    print("   • Parameter resolution from context")
    print()
    
    print("🎯 **Next Steps:**")
    print("   • Add more workflow definitions (invoice_processing.yml, etc.)")
    print("   • Implement HTTP API for MCP server communication")
    print("   • Create workflow builder UI")
    print("   • Add workflow testing framework")
    print("   • Implement notification/alerting system")
    print()

if __name__ == "__main__":
    print("🧪 DMV Workflow Test Suite")
    print("=" * 50)
    print()
    
    # Demonstrate concepts first
    demonstrate_workflow_concepts()
    
    print("🚀 Running Workflow Test...")
    print()
    
    # Run the actual test
    result = asyncio.run(test_dmv_workflow())
    
    if result:
        print("✅ Workflow test completed successfully!")
        print(f"📁 Execution saved to database with ID: {result.execution_id}")
    else:
        print("❌ Workflow test failed!")
    
    print()
    print("🎉 End-to-End Workflow Demo Complete!")