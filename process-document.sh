#!/bin/bash
# Process Any Document Script
# Usage: ./process-document.sh <path-to-pdf>

if [ -z "$1" ]; then
    echo "Usage: ./process-document.sh <path-to-pdf>"
    echo "Example: ./process-document.sh test-documents/invoice.pdf"
    exit 1
fi

echo "Processing document: $1"
echo "This will:"
echo "1. Extract data using Vision API"
echo "2. Create CRM records"
echo "3. Generate tasks"
echo "4. Provide full analysis"
echo ""
echo "Please run this command in Claude Code:"
echo "Use the prompt at /Users/andrew/Projects/claudecode1/.claude/prompts/process-any-document.md to process $1"