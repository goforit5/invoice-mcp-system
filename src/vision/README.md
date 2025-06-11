# Vision MCP for Claude

A Model Context Protocol (MCP) server for PDF text extraction using OpenAI's Vision API, allowing Claude to extract text from PDF documents.

## Features

- Extract text from PDF files using OpenAI Vision API
- Page-by-page text extraction with structured JSON output
- High-quality image conversion (200 DPI)
- Comprehensive error handling and logging
- Security: Only processes files from designated test-documents directory
- Compatible with Claude Code's MCP protocol

## Requirements

### Dependencies

```bash
pip install "mcp[cli]" openai pdf2image Pillow
```

### System Requirements

- **poppler-utils** for PDF rendering:
  - macOS: `brew install poppler`
  - Ubuntu/Debian: `sudo apt-get install poppler-utils`
  - Windows: Download from [poppler-windows](https://github.com/oschwartz10612/poppler-windows)

### OpenAI API Key

Set your OpenAI API key as an environment variable:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

## Usage

### Starting the Server

```bash
python /Users/andrew/Projects/claudecode1/src/vision/server.py
```

### MCP Configuration

Add to your MCP configuration:

```json
{
  "vision": {
    "command": "python",
    "args": ["/Users/andrew/Projects/claudecode1/src/vision/server.py"],
    "env": {
      "OPENAI_API_KEY": "your-api-key-here"
    }
  }
}
```

### Tool Parameters

The `extractPdfText` tool accepts:

- `file_path` (required): Path to PDF file in `/Users/andrew/Projects/claudecode1/test-documents`

### Response Format

```json
{
  "filename": "document.pdf",
  "total_pages": 3,
  "extracted_text": [
    {
      "page": 1,
      "text": "Text content from page 1..."
    },
    {
      "page": 2,
      "text": "Text content from page 2..."
    },
    {
      "page": 3,
      "text": "Text content from page 3..."
    }
  ],
  "processing_time": "2.5s"
}
```

## Integration with Claude

Use the PDF text extraction functionality with prompts like:

```
Use the extractPdfText tool to extract text from /Users/andrew/Projects/claudecode1/test-documents/sample.pdf
```

## Security Features

1. **Path Validation**: Only processes files from the designated test-documents directory
2. **File Type Validation**: Only accepts PDF files
3. **Error Handling**: Comprehensive error handling for missing files, API failures, etc.

## How It Works

1. **PDF Conversion**: Converts PDF pages to high-quality PNG images (200 DPI)
2. **Image Encoding**: Converts images to base64 format for API transmission
3. **Text Extraction**: Uses OpenAI's GPT-4o-mini vision model to extract text
4. **Structured Output**: Returns organized JSON with text per page and metadata

## Cost Considerations

- Uses GPT-4o-mini for cost efficiency ($0.15 per 1M input tokens)
- High detail image processing for better text recognition
- Token usage depends on image complexity and text density

## Troubleshooting

### Common Issues

1. **poppler-utils not found**: Install poppler-utils for your system
2. **OpenAI API key**: Ensure OPENAI_API_KEY environment variable is set
3. **File permissions**: Ensure the server has read access to test-documents directory
4. **Large PDFs**: Processing time increases with page count and complexity

### Logging

The server provides detailed logging for:
- PDF conversion progress
- Page-by-page processing status
- API call results
- Error conditions

## MCP Protocol Implementation

This server implements the Model Context Protocol (MCP) standard:

1. Uses FastMCP Python SDK for protocol compliance
2. Registers the `extractPdfText` tool with proper parameter validation
3. Provides resource endpoint for server information
4. Uses stdio transport for Claude integration
5. Follows MCP best practices for error handling and responses