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
const PORT = 3002;

// Store active processing sessions for SSE
const processingClients = new Map();

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

// Send progress update to connected clients
function sendProgress(filename, stage, details = {}) {
  processingClients.forEach((res, clientId) => {
    res.write(`data: ${JSON.stringify({ filename, stage, ...details })}\n\n`);
  });
}

// Helper function to call Vision MCP server for invoice extraction
async function callInvoiceMCP(filePath, filename) {
  return new Promise((resolve, reject) => {
    const pythonPath = path.join(__dirname, '../../vision-mcp-env/bin/python');
    const visionDir = path.join(__dirname, '../../src/vision');
    
    console.log('Calling Vision MCP server for invoice extraction...');
    console.log('Python path:', pythonPath);
    console.log('Vision dir:', visionDir);
    console.log('File path:', filePath);
    
    sendProgress(filename, 'starting', { message: 'Initializing PDF processing...' });
    
    // Create a temporary Python script file
    const tempScript = `
import sys
import json
import traceback
import os
from datetime import datetime

# Add the vision module path
sys.path.append('${visionDir.replace(/\\/g, '/')}')

def main():
    try:
        from index import extract_pdf_text, extract_structured_invoice_data, save_invoice_json
        
        file_path = '${filePath.replace(/\\/g, '/')}'
        print(f"Processing file: {file_path}", file=sys.stderr)
        
        # Extract text from PDF
        text_result = extract_pdf_text(file_path)
        print("Text extraction complete", file=sys.stderr)
        
        # Combine all page text
        combined_text = ""
        for page_data in text_result["extracted_text"]:
            combined_text += page_data["text"] + "\\n\\n"
        
        # Extract structured data
        print("Starting structured data extraction...", file=sys.stderr)
        try:
            structured_result = extract_structured_invoice_data(combined_text, text_result["filename"])
            print("Structured extraction complete", file=sys.stderr)
        except Exception as e:
            print(f"Error in structured extraction: {e}", file=sys.stderr)
            raise e
        
        # Save structured data with timestamp
        print("Saving structured data...", file=sys.stderr)
        try:
            base_filename = os.path.splitext(text_result["filename"])[0]
            timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
            timestamped_filename = f"{base_filename}_{timestamp}"
            
            output_file = save_invoice_json(structured_result["structured_data"], timestamped_filename)
            print(f"Saved to: {output_file}", file=sys.stderr)
        except Exception as e:
            print(f"Error saving data: {e}", file=sys.stderr)
            raise e
        
        # Calculate total cost
        total_extraction_cost = text_result["total_cost_summary"]["total_cost"]
        structured_cost = structured_result["extraction_cost"]["total_cost"]
        total_cost = total_extraction_cost + structured_cost
        
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
        print(f"Error in processing: {str(e)}", file=sys.stderr)
        error_result = {
            "error": str(e),
            "traceback": traceback.format_exc(),
            "file_path": file_path
        }
        print(json.dumps(error_result, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main()
`;

    const python = spawn(pythonPath, ['-c', tempScript], {
      stdio: ['pipe', 'pipe', 'pipe']
    });

    // Set a manual timeout - increased to 5 minutes for complex invoices
    const timeoutId = setTimeout(() => {
      console.log('Killing Python process due to timeout...');
      python.kill('SIGKILL');
      reject(new Error('Processing timeout after 5 minutes'));
    }, 300000);

    let result = '';
    let error = '';

    python.stdout.on('data', (data) => {
      result += data.toString();
    });

    python.stderr.on('data', (data) => {
      error += data.toString();
      const stderrData = data.toString();
      console.log('Python stderr:', stderrData);
      
      // Send progress updates based on stderr messages
      if (stderrData.includes('Processing file:')) {
        sendProgress(filename, 'processing', { message: 'Converting PDF to images...' });
      } else if (stderrData.includes('Text extraction complete')) {
        sendProgress(filename, 'text_complete', { message: 'Text extraction complete, analyzing content...' });
      } else if (stderrData.includes('Starting structured data extraction')) {
        sendProgress(filename, 'structuring', { message: 'AI parsing invoice data into structured format...' });
      } else if (stderrData.includes('Structured extraction complete')) {
        sendProgress(filename, 'structured_complete', { message: 'Data extraction complete, saving results...' });
      } else if (stderrData.includes('Saving structured data')) {
        sendProgress(filename, 'saving', { message: 'Validating and saving structured data...' });
      } else if (stderrData.includes('Saved to:')) {
        sendProgress(filename, 'saved', { message: 'Processing complete!' });
      }
    });

    python.on('close', (code) => {
      clearTimeout(timeoutId);
      console.log(`Python process exited with code ${code}`);
      if (error) console.log('Python stderr:', error);
      
      if (code === 0) {
        try {
          const parsedResult = JSON.parse(result);
          if (parsedResult.error) {
            console.error('Python script error:', parsedResult.error);
            sendProgress(filename, 'error', { message: `Error: ${parsedResult.error}` });
            reject(new Error(parsedResult.error));
          } else {
            sendProgress(filename, 'complete', { message: 'Processing complete!' });
            resolve(parsedResult);
          }
        } catch (parseError) {
          console.error('JSON parse error:', parseError.message);
          console.error('Raw result:', result);
          reject(new Error(`Failed to parse result: ${parseError.message}`));
        }
      } else if (code === null) {
        console.error('Python process was terminated (timeout or signal)');
        sendProgress(filename, 'error', { message: 'Processing timeout - please try a smaller file or try again later' });
        reject(new Error('Processing was terminated - likely due to timeout or system resource issues'));
      } else {
        console.error('Python script failed with code:', code);
        sendProgress(filename, 'error', { message: `Processing failed: ${error}` });
        reject(new Error(`Python script failed with code ${code}: ${error}`));
      }
    });

    python.on('error', (err) => {
      clearTimeout(timeoutId);
      console.error('Python process error:', err);
      reject(err);
    });
  });
}

// Log processing results to CSV database
async function logToDatabase(filename, result) {
  try {
    const csvPath = path.join(__dirname, '../../data/processed_invoices.csv');
    
    // Create CSV file with headers if it doesn't exist
    if (!fs.existsSync(csvPath)) {
      const headers = [
        'id', 'timestamp', 'original_filename', 'processed_filename', 'output_file',
        'total_pages', 'vision_cost', 'llm_cost', 'total_cost', 'processing_time',
        'invoice_number', 'vendor_name', 'customer_name', 'total_amount', 'line_items_count',
        'status', 'requires_human_review', 'automation_rate'
      ].join(',');
      
      fs.writeFileSync(csvPath, headers);
    }
    
    // Generate unique ID
    const id = Date.now().toString();
    const timestamp = new Date().toISOString();
    
    // Extract data from result
    const structuredData = result.structured_data;
    const invoiceNumber = structuredData.invoice_metadata?.invoice_number || '';
    const vendorName = structuredData.vendor?.name || '';
    const customerName = structuredData.customer?.name || '';
    const totalAmount = structuredData.totals?.total || '';
    const lineItemsCount = structuredData.line_items?.length || 0;
    
    // Determine status and review requirements
    const hasAllRequiredFields = invoiceNumber && vendorName && customerName && totalAmount;
    const status = hasAllRequiredFields ? 'COMPLETE' : 'PARTIAL';
    const requiresHumanReview = !hasAllRequiredFields || lineItemsCount === 0;
    const automationRate = requiresHumanReview ? "85%" : "100%";
    
    // Create CSV row with enhanced cost breakdown
    const pagesProcessed = result.total_pages || 1;
    const visionCost = result.cost_breakdown.text_extraction_cost || 0;
    const llmCost = result.cost_breakdown.structured_extraction_cost || 0;
    
    const csvRow = [
      id,
      timestamp,
      result.filename,
      filename,
      result.output_file,
      pagesProcessed,
      visionCost.toFixed(4),
      llmCost.toFixed(4),
      result.cost_breakdown.total_cost,
      result.processing_time,
      invoiceNumber,
      vendorName,
      customerName,
      totalAmount,
      lineItemsCount,
      status.toUpperCase(),
      requiresHumanReview,
      automationRate
    ].map(field => `"${field}"`).join(',');
    
    // Append to CSV file
    fs.appendFileSync(csvPath, '\n' + csvRow);
    
    console.log('✅ Logged to database:', filename);
  } catch (error) {
    console.error('❌ Failed to log to database:', error);
  }
}

// Upload and process endpoint
app.post('/api/upload', upload.single('pdf'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No PDF file uploaded' });
    }

    console.log('File uploaded:', req.file.filename);
    const filePath = req.file.path;

    // Process the PDF using Vision MCP
    console.log('Processing PDF with Vision MCP...');
    const result = await callInvoiceMCP(filePath, req.file.filename);

    // Log to CSV database
    await logToDatabase(req.file.filename, result);

    res.json({
      success: true,
      filename: req.file.filename,
      result: result
    });

  } catch (error) {
    console.error('Error processing file:', error);
    res.status(500).json({ 
      error: 'Failed to process PDF', 
      details: error.message 
    });
  }
});

// Server-Sent Events endpoint for real-time progress
app.get('/api/progress', (req, res) => {
  res.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Cache-Control'
  });

  // Generate unique client ID
  const clientId = Date.now() + Math.random();
  processingClients.set(clientId, res);

  // Send initial connection message
  res.write(`data: ${JSON.stringify({ stage: 'connected', message: 'Connected to progress updates' })}\n\n`);

  // Handle client disconnect
  req.on('close', () => {
    processingClients.delete(clientId);
  });
});

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Get processed files from output directory
app.get('/api/results', (req, res) => {
  try {
    const outputDir = path.join(__dirname, '../../output/invoices');
    
    // Create output directory if it doesn't exist
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    
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
    const filePath = path.join(__dirname, '../../output/invoices', filename);
    
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
    const csvPath = path.join(__dirname, '../../data/processed_invoices.csv');
    
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
        total_pages: parseInt(recordData.total_pages) || 1,
        processing_time: recordData.processing_time,
        extracted_text: [{ page_number: 1, text: "Text extraction data not available for historical records", processing_time: "N/A", cost: 0 }],
        structured_data: resultData,
        output_file: outputFilePath,
        cost_breakdown: {
          text_extraction_cost: parseFloat(recordData.vision_cost) || 0,
          structured_extraction_cost: parseFloat(recordData.llm_cost) || 0,
          total_cost: parseFloat(recordData.total_cost) || 0
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
    const csvPath = path.join(__dirname, '../../data/processed_invoices.csv');
    
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
    const csvPath = path.join(__dirname, '../../data/processed_invoices.csv');
    
    if (!fs.existsSync(csvPath)) {
      return res.json({ 
        totalProcessed: 0,
        totalCost: 0,
        autoProcessed: 0,
        humanReviewRequired: 0,
        totalInvoiceValue: 0
      });
    }

    const csvContent = fs.readFileSync(csvPath, 'utf8');
    const lines = csvContent.trim().split('\n');
    
    if (lines.length <= 1) {
      return res.json({ 
        totalProcessed: 0,
        totalCost: 0,
        autoProcessed: 0,
        humanReviewRequired: 0,
        totalInvoiceValue: 0
      });
    }

    const records = lines.slice(1);
    const totalProcessed = records.length;
    let totalCost = 0;
    let autoProcessed = 0;
    let humanReviewRequired = 0;
    let totalInvoiceValue = 0;

    records.forEach(line => {
      const values = line.match(/(".*?"|[^",\s]+)(?=\s*,|\s*$)/g) || [];
      const cost = parseFloat(values[8]?.replace(/"/g, '') || '0');
      const requiresReview = values[16]?.replace(/"/g, '') === 'true';
      const invoiceAmount = parseFloat(values[13]?.replace(/[",\s$]/g, '') || '0');
      
      totalCost += cost;
      totalInvoiceValue += invoiceAmount;
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
      totalInvoiceValue: parseFloat(totalInvoiceValue.toFixed(2)),
      automationRate: totalProcessed > 0 ? ((autoProcessed / totalProcessed) * 100).toFixed(1) : 0
    });
  } catch (error) {
    console.error('Error calculating stats:', error);
    res.status(500).json({ error: 'Failed to calculate stats' });
  }
});

// Update invoice data endpoint
app.put('/api/invoice/:id', (req, res) => {
  try {
    const { id } = req.params;
    const updatedData = req.body;
    
    // Get the record from database to find the output file
    const csvPath = path.join(__dirname, '../../data/processed_invoices.csv');
    
    if (!fs.existsSync(csvPath)) {
      return res.status(404).json({ error: 'Database not found' });
    }

    const csvContent = fs.readFileSync(csvPath, 'utf8');
    const lines = csvContent.trim().split('\n');
    const headers = lines[0].split(',');
    
    const record = lines.slice(1).find(line => {
      const values = line.match(/(".*?"|[^",\s]+)(?=\s*,|\s*$)/g) || [];
      const recordId = values[0]?.replace(/"/g, '');
      return recordId === id;
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

    // Update the JSON file
    const outputFilePath = recordData.output_file;
    if (fs.existsSync(outputFilePath)) {
      fs.writeFileSync(outputFilePath, JSON.stringify(updatedData, null, 2));
      res.json({ success: true, message: 'Invoice updated successfully' });
    } else {
      res.status(404).json({ error: 'Output file not found' });
    }
  } catch (error) {
    console.error('Error updating invoice:', error);
    res.status(500).json({ error: 'Failed to update invoice' });
  }
});

app.listen(PORT, () => {
  console.log(`Invoice Processing API server running on http://localhost:${PORT}`);
  console.log('Available endpoints:');
  console.log('  POST /api/upload - Upload and process PDF');
  console.log('  GET  /api/health - Health check');
  console.log('  GET  /api/results - List processed files');
  console.log('  GET  /api/result/:filename - Get specific result');
  console.log('  PUT  /api/invoice/:id - Update invoice data');
});