import express from 'express';
import multer from 'multer';
import cors from 'cors';
import path from 'path';
import fs from 'fs';
import { spawn } from 'child_process';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = 3001;

// Enable CORS for frontend
app.use(cors());
app.use(express.json());

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    // Save uploaded files to test-documents directory
    const uploadDir = path.join(__dirname, '../../test-documents');
    cb(null, uploadDir);
  },
  filename: function (req, file, cb) {
    // Add timestamp to filename for 10x developer workflow
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
    const ext = path.extname(file.originalname);
    const basename = path.basename(file.originalname, ext);
    cb(null, `${basename}_${timestamp}${ext}`);
  }
});

const upload = multer({ 
  storage: storage,
  fileFilter: (req, file, cb) => {
    // Only accept PDF files
    if (file.mimetype === 'application/pdf') {
      cb(null, true);
    } else {
      cb(new Error('Only PDF files are allowed'), false);
    }
  }
});

// Helper function to call Vision MCP server with progress tracking
async function callVisionMCPWithProgress(filePath, sendProgress) {
  return new Promise((resolve, reject) => {
    // Call the Vision MCP server's extractbrokerage tool
    const mcpServerPath = path.join(__dirname, '../../src/vision/server.py');
    const pythonPath = path.join(__dirname, '../../vision-mcp-env/bin/python');
    
    console.log('🔧 Calling Vision MCP server...');
    console.log('🐍 Python path:', pythonPath);
    console.log('🤖 MCP server path:', mcpServerPath);
    console.log('📁 File path:', filePath);
    
    sendProgress('pdf_analysis', { message: 'Converting PDF to images...' });
    
    // Enhanced Python script with detailed logging and progress tracking
    const pythonScript = `
import sys
import json
import traceback
import time

print("🔄 STAGE: PDF_ANALYSIS", file=sys.stderr)
print("📄 Starting PDF processing...", file=sys.stderr)

# Add the vision module path
sys.path.append('${path.join(__dirname, '../../src/vision')}')

try:
    from index import extract_pdf_text, extract_structured_brokerage_data, save_brokerage_json
    
    print("🔄 STAGE: VISION_EXTRACTION", file=sys.stderr)
    print("🤖 Extracting text from PDF with AI vision...", file=sys.stderr)
    
    # Extract text from PDF with detailed progress
    text_result = extract_pdf_text('${filePath}')
    
    print(f"✅ Extracted text from {text_result['total_pages']} pages", file=sys.stderr)
    print(f"📊 Total characters extracted: {sum(len(page['text']) for page in text_result['extracted_text'])}", file=sys.stderr)
    print(f"💰 Vision processing cost: \${text_result['total_cost_summary']['total_cost']:.4f}", file=sys.stderr)
    
    # Combine all page text
    combined_text = ""
    for page_data in text_result["extracted_text"]:
        combined_text += page_data["text"] + "\\n\\n"
    
    print("🔄 STAGE: STRUCTURE_PARSING", file=sys.stderr)
    print("🧠 Converting to structured data with AI...", file=sys.stderr)
    
    # Extract structured data
    structured_result = extract_structured_brokerage_data(combined_text, text_result["filename"])
    
    print("✅ Structured data extraction complete", file=sys.stderr)
    print(f"💰 Structure parsing cost: \${structured_result['extraction_cost']['total_cost']:.4f}", file=sys.stderr)
    
    # Validation summary
    audit = structured_result["structured_data"].get("audit", {})
    print(f"🔍 Audit status: {audit.get('overall_status', 'UNKNOWN')}", file=sys.stderr)
    print(f"👁️  Human review required: {audit.get('requires_human_review', False)}", file=sys.stderr)
    
    print("🔄 STAGE: SAVING", file=sys.stderr)
    print("💾 Saving structured data...", file=sys.stderr)
    
    # Save structured data with timestamp
    import os
    from datetime import datetime
    
    # Create timestamped output filename
    base_filename = os.path.splitext(text_result["filename"])[0]
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    timestamped_filename = f"{base_filename}_{timestamp}"
    
    output_file = save_brokerage_json(structured_result["structured_data"], timestamped_filename)
    
    print(f"📁 Saved to: {output_file}", file=sys.stderr)
    
    # Calculate total cost
    total_extraction_cost = text_result["total_cost_summary"]["total_cost"]
    structured_cost = structured_result["extraction_cost"]["total_cost"]
    total_cost = total_extraction_cost + structured_cost
    
    print(f"💰 Total processing cost: \${total_cost:.4f}", file=sys.stderr)
    print("✅ Processing complete!", file=sys.stderr)
    
    result = {
        "filename": text_result["filename"],
        "total_pages": text_result["total_pages"],
        "processing_time": text_result["processing_time"],
        "extracted_text": text_result["extracted_text"],
        "structured_data": structured_result["structured_data"],
        "output_file": output_file,
        "cost_breakdown": {
            "text_extraction_cost": total_extraction_cost,
            "structured_extraction_cost": structured_cost,
            "total_cost": round(total_cost, 6)
        }
    }
    
    print(json.dumps(result, indent=2))
    
except Exception as e:
    print(f"❌ ERROR: {str(e)}", file=sys.stderr)
    print(f"📍 Traceback: {traceback.format_exc()}", file=sys.stderr)
    error_result = {
        "error": str(e),
        "traceback": traceback.format_exc(),
        "file_path": '${filePath}'
    }
    print(json.dumps(error_result, indent=2))
    sys.exit(1)
`;

    const python = spawn(pythonPath, ['-c', pythonScript]);

    let result = '';
    let currentStage = 'pdf_analysis';
    let pageCount = 0;
    let totalPages = 0;

    python.stdout.on('data', (data) => {
      result += data.toString();
    });

    python.stderr.on('data', (data) => {
      const output = data.toString();
      console.log('🔍 Python output:', output.trim());
      
      // Parse stage changes and send progress updates
      if (output.includes('STAGE: PDF_ANALYSIS')) {
        currentStage = 'pdf_analysis';
        sendProgress('pdf_analysis', { 
          message: 'Converting PDF to high-resolution images...'
        });
      } else if (output.includes('STAGE: VISION_EXTRACTION')) {
        currentStage = 'vision_extraction';
        sendProgress('vision_extraction', { 
          message: 'Starting AI vision processing...',
          currentPage: 0,
          totalPages: 0
        });
      } else if (output.includes('STAGE: STRUCTURE_PARSING')) {
        currentStage = 'structure_parsing';
        sendProgress('structure_parsing', { 
          message: 'Converting to structured data...',
          currentPage: totalPages,
          totalPages: totalPages
        });
      } else if (output.includes('STAGE: SAVING')) {
        sendProgress('saving', { message: 'Validating and saving results...' });
      }
      
      // Extract page count when available
      const pagesMatch = output.match(/Extracted text from (\d+) pages/);
      if (pagesMatch) {
        totalPages = parseInt(pagesMatch[1]);
        sendProgress('vision_extraction', { 
          message: `Processed ${totalPages} pages with AI vision`,
          currentPage: totalPages,
          totalPages: totalPages
        });
      }
      
      // Extract cost information
      const costMatch = output.match(/Total processing cost: \$([0-9.]+)/);
      if (costMatch) {
        sendProgress('complete_processing', { 
          message: 'Processing complete!',
          totalCost: parseFloat(costMatch[1])
        });
      }
    });

    python.on('close', (code) => {
      console.log(`🏁 Python process exited with code ${code}`);
      
      if (code === 0) {
        try {
          const parsedResult = JSON.parse(result);
          if (parsedResult.error) {
            console.error('❌ Python script error:', parsedResult.error);
            sendProgress('error', { error: parsedResult.error });
            reject(new Error(parsedResult.error));
          } else {
            console.log('✅ Processing successful!');
            resolve(parsedResult);
          }
        } catch (parseError) {
          console.error('❌ JSON parse error:', parseError.message);
          sendProgress('error', { error: `Failed to parse result: ${parseError.message}` });
          reject(new Error(`Failed to parse result: ${parseError.message}`));
        }
      } else {
        console.error('❌ Python script failed with code:', code);
        sendProgress('error', { error: `Processing failed with code ${code}` });
        reject(new Error(`Python script failed with code ${code}`));
      }
    });
  });
}

// Keep original function for backward compatibility
async function callVisionMCP(filePath) {
  return new Promise((resolve, reject) => {
    callVisionMCPWithProgress(filePath, () => {}).then(resolve).catch(reject);
  });
}

// Log processing results to CSV database
async function logToDatabase(filename, result) {
  try {
    const csvPath = path.join(__dirname, '../../data/processed_documents.csv');
    
    // Generate unique ID
    const id = Date.now().toString();
    const timestamp = new Date().toISOString();
    
    // Extract data from result
    const structuredData = result.structured_data;
    const accountsFound = structuredData.accounts?.length || 0;
    const holdingsCount = structuredData.accounts?.reduce((total, acc) => total + (acc.holdings?.length || 0), 0) || 0;
    const overallStatus = structuredData.audit?.overall_status || 'UNKNOWN';
    const requiresHumanReview = structuredData.audit?.requires_human_review === true;
    const totalValue = structuredData.statement_total_value || '';
    
    // Create CSV row with enhanced cost breakdown
    const pagesProcessed = result.total_pages || 1;
    const visionCost = result.cost_breakdown.text_extraction_cost || 0;
    const llmCost = result.cost_breakdown.structured_extraction_cost || 0;
    const automationRate = requiresHumanReview ? "85%" : "100%";
    
    const csvRow = [
      id,
      timestamp,
      result.filename,
      filename,
      result.output_file,
      pagesProcessed,
      visionCost.toFixed(4),
      llmCost.toFixed(4),
      result.cost_breakdown.total_cost.toFixed(4),
      result.processing_time,
      accountsFound,
      holdingsCount,
      overallStatus.toUpperCase(),
      requiresHumanReview,
      totalValue,
      automationRate
    ].map(field => `"${field}"`).join(',');
    
    // Append to CSV file
    fs.appendFileSync(csvPath, '\n' + csvRow);
    
    console.log('✅ Logged to database:', filename);
  } catch (error) {
    console.error('❌ Failed to log to database:', error);
  }
}

// Upload and process endpoint with streaming progress
app.post('/api/upload', upload.single('pdf'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No PDF file uploaded' });
    }

    console.log('📄 File uploaded:', req.file.filename);
    console.log('📊 File size:', (req.file.size / 1024 / 1024).toFixed(1), 'MB');
    const filePath = req.file.path;

    // Set up Server-Sent Events for real-time progress
    res.writeHead(200, {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Headers': 'Cache-Control'
    });

    const sendProgress = (stage, data = {}) => {
      const progressData = JSON.stringify({ stage, ...data, timestamp: new Date().toISOString() });
      res.write(`data: ${progressData}\n\n`);
      console.log(`🔄 Progress: ${stage}`, data);
    };

    sendProgress('initializing', { 
      fileName: req.file.filename, 
      fileSize: `${(req.file.size / 1024 / 1024).toFixed(1)} MB` 
    });

    // Process the PDF using Vision MCP with progress tracking
    console.log('🤖 Starting Vision MCP processing...');
    const result = await callVisionMCPWithProgress(filePath, sendProgress);

    // Log to CSV database
    console.log('💾 Logging to database...');
    sendProgress('saving', { outputFile: result.output_file });
    await logToDatabase(req.file.filename, result);

    sendProgress('complete', { result });
    res.write('data: [DONE]\n\n');
    res.end();

  } catch (error) {
    console.error('❌ Error processing file:', error);
    const errorData = JSON.stringify({ 
      stage: 'error', 
      error: error.message, 
      timestamp: new Date().toISOString() 
    });
    res.write(`data: ${errorData}\n\n`);
    res.end();
  }
});

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Get processed files from output directory
app.get('/api/results', (req, res) => {
  try {
    const outputDir = path.join(__dirname, '../../output/brokerage');
    const files = fs.readdirSync(outputDir)
      .filter(file => file.endsWith('.json'))
      .map(file => {
        const filePath = path.join(outputDir, file);
        const stats = fs.statSync(filePath);
        return {
          filename: file,
          created: stats.mtime,
          size: stats.size
        };
      })
      .sort((a, b) => b.created - a.created);

    res.json({ files });
  } catch (error) {
    console.error('Error reading results:', error);
    res.status(500).json({ error: 'Failed to read results' });
  }
});

// Get specific result file
app.get('/api/result/:filename', (req, res) => {
  try {
    const filename = req.params.filename;
    const filePath = path.join(__dirname, '../../output/brokerage', filename);
    
    if (!fs.existsSync(filePath)) {
      return res.status(404).json({ error: 'File not found' });
    }

    const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    res.json(data);
  } catch (error) {
    console.error('Error reading result file:', error);
    res.status(500).json({ error: 'Failed to read result file' });
  }
});

// Get result by ID from database
app.get('/api/record/:id', (req, res) => {
  try {
    const csvPath = path.join(__dirname, '../../data/processed_documents.csv');
    
    if (!fs.existsSync(csvPath)) {
      return res.status(404).json({ error: 'Database not found' });
    }

    const csvContent = fs.readFileSync(csvPath, 'utf8');
    const lines = csvContent.trim().split('\n');
    const headers = lines[0].split(',');
    
    const record = lines.slice(1).find(line => {
      const values = line.match(/(".*?"|[^",\s]+)(?=\s*,|\s*$)/g) || [];
      const id = values[0]?.replace(/"/g, '');
      return id === req.params.id;
    });

    if (!record) {
      return res.status(404).json({ error: 'Record not found' });
    }

    const values = record.match(/(".*?"|[^",\s]+)(?=\s*,|\s*$)/g) || [];
    const recordData = {};
    headers.forEach((header, index) => {
      const value = values[index] ? values[index].replace(/^"(.*)"$/, '$1') : '';
      recordData[header] = value;
    });

    // Load the actual result file
    const outputFilePath = recordData.output_file;
    if (fs.existsSync(outputFilePath)) {
      const resultData = JSON.parse(fs.readFileSync(outputFilePath, 'utf8'));
      
      // Mock the result structure to match what the UI expects
      const mockResult = {
        filename: recordData.original_filename,
        total_pages: 1, // We don't have this data, so mock it
        processing_time: recordData.processing_time,
        extracted_text: [{ page_number: 1, text: "Text extraction data not available for historical records", processing_time: "N/A", cost: 0 }],
        structured_data: resultData,
        output_file: outputFilePath,
        cost_breakdown: {
          text_extraction_cost: parseFloat(recordData.total_cost) * 0.6, // Estimate
          structured_extraction_cost: parseFloat(recordData.total_cost) * 0.4, // Estimate
          total_cost: parseFloat(recordData.total_cost)
        }
      };

      res.json(mockResult);
    } else {
      res.status(404).json({ error: 'Result file not found' });
    }
  } catch (error) {
    console.error('Error reading record:', error);
    res.status(500).json({ error: 'Failed to read record' });
  }
});

// Get processing database (CSV as JSON)
app.get('/api/database', (req, res) => {
  try {
    const csvPath = path.join(__dirname, '../../data/processed_documents.csv');
    
    if (!fs.existsSync(csvPath)) {
      return res.json({ records: [] });
    }

    const csvContent = fs.readFileSync(csvPath, 'utf8');
    const lines = csvContent.trim().split('\n');
    
    if (lines.length <= 1) {
      return res.json({ records: [] });
    }

    const headers = lines[0].split(',');
    const records = lines.slice(1).map(line => {
      const values = line.match(/(".*?"|[^",\s]+)(?=\s*,|\s*$)/g) || [];
      const record = {};
      headers.forEach((header, index) => {
        const value = values[index] ? values[index].replace(/^"(.*)"$/, '$1') : '';
        record[header] = value;
      });
      return record;
    });

    res.json({ 
      records: records.reverse(), // Most recent first
      total: records.length 
    });
  } catch (error) {
    console.error('Error reading database:', error);
    res.status(500).json({ error: 'Failed to read database' });
  }
});

// Get database statistics
app.get('/api/stats', (req, res) => {
  try {
    const csvPath = path.join(__dirname, '../../data/processed_documents.csv');
    
    if (!fs.existsSync(csvPath)) {
      return res.json({ 
        totalProcessed: 0,
        totalCost: 0,
        autoProcessed: 0,
        humanReviewRequired: 0
      });
    }

    const csvContent = fs.readFileSync(csvPath, 'utf8');
    const lines = csvContent.trim().split('\n');
    
    if (lines.length <= 1) {
      return res.json({ 
        totalProcessed: 0,
        totalCost: 0,
        autoProcessed: 0,
        humanReviewRequired: 0
      });
    }

    const records = lines.slice(1);
    const totalProcessed = records.length;
    let totalCost = 0;
    let autoProcessed = 0;
    let humanReviewRequired = 0;

    records.forEach(line => {
      const values = line.match(/(".*?"|[^",\s]+)(?=\s*,|\s*$)/g) || [];
      const cost = parseFloat(values[5]?.replace(/"/g, '') || '0');
      const requiresReview = values[10]?.replace(/"/g, '') === 'true';
      
      totalCost += cost;
      if (requiresReview) {
        humanReviewRequired++;
      } else {
        autoProcessed++;
      }
    });

    res.json({
      totalProcessed,
      totalCost: parseFloat(totalCost.toFixed(4)),
      autoProcessed,
      humanReviewRequired,
      automationRate: totalProcessed > 0 ? ((autoProcessed / totalProcessed) * 100).toFixed(1) : 0
    });
  } catch (error) {
    console.error('Error calculating stats:', error);
    res.status(500).json({ error: 'Failed to calculate stats' });
  }
});

app.listen(PORT, () => {
  console.log(`Brokerage Extraction API server running on http://localhost:${PORT}`);
  console.log('Available endpoints:');
  console.log('  POST /api/upload - Upload and process PDF');
  console.log('  GET  /api/health - Health check');
  console.log('  GET  /api/results - List processed files');
  console.log('  GET  /api/result/:filename - Get specific result');
});