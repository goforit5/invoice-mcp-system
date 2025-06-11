"""
PDF text extraction using OpenAI Vision API
"""

import os
import base64
import time
import json
from typing import Dict, List
from pathlib import Path
import logging

from pdf2image import convert_from_path
from openai import OpenAI
from PIL import Image
import io

# Configure logging
logger = logging.getLogger(__name__)

# Initialize OpenAI client - force use of environment variable from MCP config
# Debug: Print all environment variables containing "API" to see what's available
logger.info("Environment variables containing 'API':")
for key, value in os.environ.items():
    if 'API' in key.upper():
        logger.info(f"  {key}: {value[:10]}...{value[-4:] if len(value) > 14 else value}")

# Get the key from environment
openai_key = os.environ.get('OPENAI_API_KEY')
if not openai_key:
    raise ValueError("OPENAI_API_KEY environment variable is required")

logger.info(f"Using API key: {openai_key[:20]}...{openai_key[-8:]}")

client = OpenAI(api_key=openai_key)

# Load pricing data
def load_pricing() -> Dict:
    """Load OpenAI model pricing data"""
    pricing_file = Path(__file__).parent / "pricing.json"
    try:
        with open(pricing_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Could not load pricing data: {e}")
        return {"models": {}}

def calculate_cost(model: str, input_tokens: int, output_tokens: int, cached_tokens: int = 0) -> Dict:
    """Calculate cost for API usage"""
    pricing = load_pricing()
    
    if model not in pricing["models"]:
        logger.warning(f"Pricing not found for model: {model}")
        return {"error": f"Pricing not found for model: {model}"}
    
    model_pricing = pricing["models"][model]
    
    # Calculate costs (prices are per 1M tokens)
    input_cost = (input_tokens / 1_000_000) * model_pricing["input"]
    output_cost = (output_tokens / 1_000_000) * model_pricing["output"]
    
    cached_cost = 0
    if cached_tokens > 0 and model_pricing.get("cached_input"):
        cached_cost = (cached_tokens / 1_000_000) * model_pricing["cached_input"]
    
    total_cost = input_cost + output_cost + cached_cost
    
    return {
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cached_tokens": cached_tokens,
        "input_cost": round(input_cost, 6),
        "output_cost": round(output_cost, 6),
        "cached_cost": round(cached_cost, 6),
        "total_cost": round(total_cost, 6),
        "currency": "USD"
    }

def extract_pdf_text(file_path: str) -> Dict:
    """
    Extract text from PDF using OpenAI Vision API
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Dictionary with extracted text per page
    """
    start_time = time.time()
    
    # Validate file exists and is PDF
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")
    
    if not file_path.lower().endswith('.pdf'):
        raise ValueError("File must be a PDF")
    
    try:
        # Convert PDF pages to images
        logger.info(f"Converting PDF to images: {file_path}")
        images = convert_from_path(file_path, dpi=200, fmt='PNG')
        
        extracted_text = []
        total_pages = len(images)
        total_cost_data = {
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_cached_tokens": 0,
            "total_cost": 0.0,
            "pages_processed": 0,
            "model_used": None
        }
        
        logger.info(f"Processing {total_pages} pages")
        
        # Process each page
        for page_num, image in enumerate(images, 1):
            logger.info(f"Processing page {page_num}/{total_pages}")
            
            # Convert PIL image to base64
            img_base64 = image_to_base64(image)
            
            # Extract text using OpenAI Vision API
            page_result = extract_text_from_image(img_base64, page_num)
            
            extracted_text.append({
                "page": page_num,
                "text": page_result["text"],
                "token_usage": page_result["token_usage"],
                "cost": page_result["cost"]
            })
            
            # Accumulate totals
            if page_result["token_usage"]:
                total_cost_data["total_input_tokens"] += page_result["token_usage"]["prompt_tokens"]
                total_cost_data["total_output_tokens"] += page_result["token_usage"]["completion_tokens"]
                total_cost_data["total_cached_tokens"] += page_result["token_usage"].get("cached_tokens", 0)
                total_cost_data["pages_processed"] += 1
                total_cost_data["model_used"] = page_result["token_usage"]["model"]
                
            if page_result["cost"] and "total_cost" in page_result["cost"]:
                total_cost_data["total_cost"] += page_result["cost"]["total_cost"]
        
        processing_time = round(time.time() - start_time, 2)
        
        result = {
            "filename": Path(file_path).name,
            "total_pages": total_pages,
            "extracted_text": extracted_text,
            "processing_time": f"{processing_time}s",
            "total_cost_summary": total_cost_data
        }
        
        logger.info(f"Text extraction completed in {processing_time}s")
        return result
        
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        raise Exception(f"Failed to process PDF: {str(e)}")

def image_to_base64(image: Image.Image) -> str:
    """
    Convert PIL Image to base64 string
    
    Args:
        image: PIL Image object
        
    Returns:
        Base64 encoded image string
    """
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)
    
    img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    return f"data:image/png;base64,{img_base64}"

def extract_text_from_image(image_data_url: str, page_num: int) -> Dict:
    """
    Extract text from image using OpenAI Vision API
    
    Args:
        image_data_url: Base64 encoded image data URL
        page_num: Page number for logging
        
    Returns:
        Dictionary with extracted text, token usage, and cost information
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Extract ALL text from this invoice/document image. Pay special attention to:\n- Header information (invoice number, dates)\n- Billing/customer information (Bill To, Ship To sections)\n- Vendor/company information\n- Line items and charges\n- Totals and payment information\n- Footer terms and conditions\n\nPreserve the exact formatting, spacing, and structure. Include every piece of text visible in the image, even small print or lightly formatted sections."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_data_url,
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            max_tokens=10000
        )
        
        extracted_text = response.choices[0].message.content or ""
        
        # Get token usage
        usage = response.usage
        cached_tokens = 0
        if hasattr(usage, 'prompt_tokens_details') and usage.prompt_tokens_details:
            cached_tokens = getattr(usage.prompt_tokens_details, 'cached_tokens', 0)
        
        token_usage = {
            "model": response.model,
            "prompt_tokens": usage.prompt_tokens,
            "completion_tokens": usage.completion_tokens,
            "total_tokens": usage.total_tokens,
            "cached_tokens": cached_tokens
        }
        
        # Calculate cost
        cost_info = calculate_cost(
            model=response.model,
            input_tokens=usage.prompt_tokens,
            output_tokens=usage.completion_tokens,
            cached_tokens=token_usage["cached_tokens"]
        )
        
        logger.info(f"Page {page_num}: Extracted {len(extracted_text)} characters")
        logger.info(f"Page {page_num}: Token usage - Input: {usage.prompt_tokens}, Output: {usage.completion_tokens}, Total: {usage.total_tokens}")
        logger.info(f"Page {page_num}: Cost - ${cost_info.get('total_cost', 'N/A')}")
        
        return {
            "text": extracted_text,
            "token_usage": token_usage,
            "cost": cost_info
        }
        
    except Exception as e:
        logger.error(f"Error extracting text from page {page_num}: {e}")
        return {
            "text": f"[Error extracting text from page {page_num}: {str(e)}]",
            "token_usage": None,
            "cost": None
        }

def load_invoice_template() -> Dict:
    """Load the invoice template JSON"""
    template_file = Path(__file__).parent / "invoice_template.json"
    try:
        with open(template_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Could not load invoice template: {e}")
        raise Exception(f"Failed to load invoice template: {str(e)}")

def extract_structured_invoice_data(extracted_text: str, filename: str) -> Dict:
    """
    Extract structured invoice data using OpenAI to parse the text into the template format
    
    Args:
        extracted_text: The raw extracted text from the PDF
        filename: Name of the source file
        
    Returns:
        Dictionary with structured invoice data
    """
    try:
        # Load the template
        template = load_invoice_template()
        
        # Create prompt for structured extraction
        prompt = f"""
Parse the following invoice text and extract the information into this JSON structure. 
Only fill in fields where you can find the information in the text. Leave fields as null if the information is not present.
Return ONLY the JSON, no additional text or formatting.

Template structure:
{json.dumps(template, indent=2)}

Invoice text to parse:
{extracted_text}
"""
        
        logger.info("Extracting structured invoice data...")
        
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=10000,
            temperature=0
        )
        
        # Parse the response as JSON with enhanced error handling
        response_content = response.choices[0].message.content
        logger.info(f"Raw AI response length: {len(response_content)} characters")
        
        try:
            structured_data = json.loads(response_content)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed at position {e.pos}: {e.msg}")
            logger.error(f"Problematic JSON around error: {response_content[max(0, e.pos-100):e.pos+100]}")
            
            # Enhanced JSON repair logic (same as brokerage)
            import re
            fixed_content = response_content.strip()
            
            # Remove any non-JSON prefix/suffix
            if '```json' in fixed_content:
                start = fixed_content.find('```json') + 7
                end = fixed_content.rfind('```')
                if end > start:
                    fixed_content = fixed_content[start:end].strip()
                    logger.info("Removed ```json``` code block wrapper")
            elif '```' in fixed_content:
                start = fixed_content.find('```') + 3
                end = fixed_content.rfind('```')
                if end > start:
                    fixed_content = fixed_content[start:end].strip()
                    logger.info("Removed ``` code block wrapper")
            
            # Ensure proper start
            if not fixed_content.startswith('{'):
                start_idx = fixed_content.find('{')
                if start_idx > 0:
                    fixed_content = fixed_content[start_idx:]
            
            # Fix formatting issues
            fixed_content = re.sub(r',(\s*[}\]])', r'\1', fixed_content)
            
            # Fix common JSON string formatting issues
            # 1. Fix double quotes that got turned into escaped quotes incorrectly
            fixed_content = re.sub(r'""([^"]*)\\"', r'"\1"', fixed_content)
            
            # 2. Fix malformed escape sequences like \"
            fixed_content = re.sub(r'\\(")', r'\1', fixed_content)
            
            # 3. Remove any stray backslashes before quotes in values
            fixed_content = re.sub(r'(:\s*"[^"]*)\\"([^"]*")', r'\1"\2', fixed_content)
            
            # 4. Fix missing commas - common issue when AI generates complex JSON
            # Look for patterns like: "field": value\n    "next_field" (missing comma)
            fixed_content = re.sub(r'([^,\s])\s*\n\s*"', r'\1,\n    "', fixed_content)
            
            # 5. Fix mathematical expressions that break JSON (remove them or wrap in strings)
            # Pattern: "field": 8.15 * 65.00 (should be a number or string)
            def fix_math_expressions(match):
                key, expr = match.groups()
                # If it contains math operators, convert to string
                if any(op in expr for op in ['*', '/', '+', '-', '(', ')']):
                    return f'{key}"{expr}"'
                return match.group(0)
            
            fixed_content = re.sub(r'(:\s*)([0-9\.\*\+\-\(\)\s/]+)(?=\s*[,}\]])', fix_math_expressions, fixed_content)
            
            # Handle truncation
            if not fixed_content.endswith('}'):
                open_braces = fixed_content.count('{')
                close_braces = fixed_content.count('}')
                open_brackets = fixed_content.count('[')
                close_brackets = fixed_content.count(']')
                
                fixed_content = re.sub(r',\s*"[^"]*":\s*[^,}\]]*$', '', fixed_content)
                fixed_content = re.sub(r',\s*"[^"]*":\s*$', '', fixed_content)
                
                if open_brackets > close_brackets:
                    fixed_content += ']' * (open_brackets - close_brackets)
                if open_braces > close_braces:
                    fixed_content += '}' * (open_braces - close_braces)
            
            logger.info(f"Attempting to parse fixed content (first 200 chars): {fixed_content[:200]}")
            try:
                structured_data = json.loads(fixed_content)
                logger.info("✅ Successfully repaired and parsed JSON")
            except json.JSONDecodeError as e2:
                logger.error(f"Invoice JSON repair attempt failed: {e2}")
                logger.error(f"Failed content snippet around error: {fixed_content[max(0, e2.pos-100):e2.pos+100]}")
                
                # Try chunk extraction for invoices too
                start_idx = fixed_content.find('{')
                if start_idx >= 0:
                    for chunk_size in [len(fixed_content), len(fixed_content)//2, len(fixed_content)//4]:
                        try:
                            chunk = fixed_content[start_idx:start_idx + chunk_size]
                            chunk = re.sub(r',\s*$', '', chunk.rstrip())
                            
                            open_braces = chunk.count('{')
                            close_braces = chunk.count('}')
                            open_brackets = chunk.count('[')
                            close_brackets = chunk.count(']')
                            
                            chunk += ']' * max(0, open_brackets - close_brackets)
                            chunk += '}' * max(0, open_braces - close_braces)
                            
                            structured_data = json.loads(chunk)
                            logger.warning(f"✅ Extracted partial invoice JSON with {len(chunk)} characters")
                            break
                        except:
                            continue
                    else:
                        logger.error("All JSON repair attempts failed - creating minimal response")
                        structured_data = {
                            "invoice_metadata": {
                                "source_file_name": filename,
                                "extraction_error": "Failed to parse AI response as valid JSON"
                            }
                        }
                else:
                    logger.error("All JSON repair attempts failed - creating minimal response")
                    structured_data = {
                        "invoice_metadata": {
                            "source_file_name": filename,
                            "extraction_error": "Failed to parse AI response as valid JSON"
                        }
                    }
        
        # Add source file name
        structured_data["invoice_metadata"]["source_file_name"] = filename
        
        # Calculate cost for this operation
        usage = response.usage
        cost_info = calculate_cost(
            model=response.model,
            input_tokens=usage.prompt_tokens,
            output_tokens=usage.completion_tokens
        )
        
        logger.info(f"Structured extraction - Token usage: Input: {usage.prompt_tokens}, Output: {usage.completion_tokens}")
        logger.info(f"Structured extraction cost: ${cost_info.get('total_cost', 'N/A')}")
        
        return {
            "structured_data": structured_data,
            "extraction_cost": cost_info
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {e}")
        # Return fallback data instead of raising exception
        return {
            "structured_data": {
                "invoice_metadata": {
                    "source_file_name": filename,
                    "extraction_error": "Failed to parse AI response as valid JSON"
                }
            },
            "extraction_cost": {"total_cost": 0.0}
        }
    except Exception as e:
        logger.error(f"Error extracting structured invoice data: {e}")
        raise Exception(f"Failed to extract structured invoice data: {str(e)}")

def save_invoice_json(structured_data: Dict, filename: str) -> str:
    """
    Save structured invoice data to JSON file
    
    Args:
        structured_data: The structured invoice data
        filename: Original filename to base the output name on
        
    Returns:
        Path to the saved JSON file
    """
    try:
        # Create output filename
        base_name = Path(filename).stem
        output_dir = Path(__file__).parent.parent.parent / "output" / "invoices"
        output_file = output_dir / f"{base_name}_structured.json"
        
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save the structured data
        with open(output_file, 'w') as f:
            json.dump(structured_data, f, indent=2)
        
        logger.info(f"Saved structured invoice data to: {output_file}")
        return str(output_file)
        
    except Exception as e:
        logger.error(f"Error saving invoice JSON: {e}")
        raise Exception(f"Failed to save invoice JSON: {str(e)}")

def load_brokerage_template() -> Dict:
    """Load the brokerage statement template JSON"""
    template_file = Path(__file__).parent / "brokerage_template.json"
    try:
        with open(template_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Could not load brokerage template: {e}")
        raise Exception(f"Failed to load brokerage template: {str(e)}")

def extract_structured_brokerage_data(extracted_text: str, filename: str) -> Dict:
    """
    Extract structured brokerage statement data using OpenAI to parse the text into the template format
    
    Args:
        extracted_text: The raw extracted text from the PDF
        filename: Name of the source file
        
    Returns:
        Dictionary with structured brokerage data
    """
    try:
        # Load the template
        template = load_brokerage_template()
        
        # Create prompt for structured extraction
        prompt = f"""
Parse the following brokerage statement text and extract the information into this JSON structure. 
Only fill in fields where you can find the information in the text. Leave fields as null if the information is not present.
For holdings arrays, include all securities/positions found in the statement.
For monetary values, use numbers without currency symbols or commas.
For dates, use format YYYY-MM-DD if possible.
Return ONLY the JSON, no additional text or formatting.

Template structure:
{json.dumps(template, indent=2)}

Brokerage statement text to parse:
{extracted_text}
"""
        
        logger.info("Extracting structured brokerage data...")
        
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=30000,
            temperature=0
        )
        
        # Parse the response as JSON with enhanced error handling
        response_content = response.choices[0].message.content
        logger.info(f"Raw AI response length: {len(response_content)} characters")
        
        # Log a snippet for debugging
        logger.info(f"Response snippet: {response_content[:200]}...{response_content[-100:]}")
        
        try:
            structured_data = json.loads(response_content)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed at position {e.pos}: {e.msg}")
            logger.error(f"Problematic JSON around error: {response_content[max(0, e.pos-100):e.pos+100]}")
            
            # Enhanced JSON repair logic
            import re
            fixed_content = response_content.strip()
            
            # Step 1: Remove any non-JSON prefix/suffix (like markdown code blocks)
            if '```json' in fixed_content:
                start = fixed_content.find('```json') + 7
                end = fixed_content.rfind('```')
                if end > start:
                    fixed_content = fixed_content[start:end].strip()
                    logger.info("Removed ```json``` code block wrapper")
            elif '```' in fixed_content:
                start = fixed_content.find('```') + 3
                end = fixed_content.rfind('```')
                if end > start:
                    fixed_content = fixed_content[start:end].strip()
                    logger.info("Removed ``` code block wrapper")
            
            # Step 2: Ensure it starts and ends properly
            if not fixed_content.startswith('{'):
                start_idx = fixed_content.find('{')
                if start_idx > 0:
                    fixed_content = fixed_content[start_idx:]
            
            # Step 3: Fix common JSON formatting issues
            # Remove trailing commas before closing brackets/braces
            fixed_content = re.sub(r',(\s*[}\]])', r'\1', fixed_content)
            
            # Fix common JSON string formatting issues (same as invoice)
            # 1. Fix double quotes that got turned into escaped quotes incorrectly
            fixed_content = re.sub(r'""([^"]*)\\"', r'"\1"', fixed_content)
            
            # 2. Fix malformed escape sequences like \"
            fixed_content = re.sub(r'\\(")', r'\1', fixed_content)
            
            # 3. Remove any stray backslashes before quotes in values
            fixed_content = re.sub(r'(:\s*"[^"]*)\\"([^"]*")', r'\1"\2', fixed_content)
            
            # 4. Fix missing commas and mathematical expressions (same as invoice)
            fixed_content = re.sub(r'([^,\s])\s*\n\s*"', r'\1,\n    "', fixed_content)
            
            def fix_math_expressions(match):
                key, expr = match.groups()
                if any(op in expr for op in ['*', '/', '+', '-', '(', ')']):
                    return f'{key}"{expr}"'
                return match.group(0)
            
            fixed_content = re.sub(r'(:\s*)([0-9\.\*\+\-\(\)\s/]+)(?=\s*[,}\]])', fix_math_expressions, fixed_content)
            
            # Step 4: Handle truncated JSON
            if not fixed_content.endswith('}'):
                logger.warning("JSON appears truncated - attempting to complete it")
                
                # Count open/close braces and brackets
                open_braces = fixed_content.count('{')
                close_braces = fixed_content.count('}')
                open_brackets = fixed_content.count('[')
                close_brackets = fixed_content.count(']')
                
                # Remove any incomplete field at the end
                # Look for incomplete patterns like ', "field": partial_value' at the end
                fixed_content = re.sub(r',\s*"[^"]*":\s*[^,}\]]*$', '', fixed_content)
                fixed_content = re.sub(r',\s*"[^"]*":\s*$', '', fixed_content)
                
                # Close missing brackets first, then braces
                missing_brackets = open_brackets - close_brackets
                missing_braces = open_braces - close_braces
                
                if missing_brackets > 0:
                    fixed_content += ']' * missing_brackets
                if missing_braces > 0:
                    fixed_content += '}' * missing_braces
                    
                logger.info(f"Added {missing_brackets} closing brackets and {missing_braces} closing braces")
            
            # Try parsing the repaired JSON
            logger.info(f"Attempting to parse fixed content (first 200 chars): {fixed_content[:200]}")
            try:
                structured_data = json.loads(fixed_content)
                logger.info("✅ Successfully repaired and parsed JSON")
            except json.JSONDecodeError as e2:
                logger.error(f"Repair attempt failed: {e2}")
                logger.error(f"Failed content snippet around error: {fixed_content[max(0, e2.pos-100):e2.pos+100]}")
                
                # Last resort: extract the largest valid JSON substring
                start_idx = fixed_content.find('{')
                if start_idx == -1:
                    logger.error("No valid JSON object found in response")
                    structured_data = {
                        "statement_metadata": {
                            "source_file_name": filename,
                            "extraction_error": "No valid JSON object found in response"
                        }
                    }
                else:
                    # Try progressively smaller chunks from the beginning
                    for chunk_size in [len(fixed_content), len(fixed_content)//2, len(fixed_content)//4]:
                        try:
                            # Take chunk and try to close it properly
                            chunk = fixed_content[start_idx:start_idx + chunk_size]
                            
                            # Clean up the chunk end
                            chunk = re.sub(r',\s*$', '', chunk.rstrip())
                            
                            # Ensure proper closing
                            open_braces = chunk.count('{')
                            close_braces = chunk.count('}')
                            open_brackets = chunk.count('[')
                            close_brackets = chunk.count(']')
                            
                            chunk += ']' * max(0, open_brackets - close_brackets)
                            chunk += '}' * max(0, open_braces - close_braces)
                            
                            structured_data = json.loads(chunk)
                            logger.warning(f"✅ Extracted partial JSON with {len(chunk)} characters")
                            break
                        except Exception as chunk_error:
                            logger.debug(f"Chunk size {chunk_size} failed: {chunk_error}")
                            continue
                    else:
                        # If all else fails, create a minimal valid response
                        logger.error("All JSON repair attempts failed - creating minimal response")
                        structured_data = {
                            "statement_metadata": {
                                "source_file_name": filename,
                                "extraction_error": "Failed to parse AI response as valid JSON"
                            }
                        }
        
        # Add source file name
        structured_data["statement_metadata"]["source_file_name"] = filename
        
        # Calculate cost for this operation
        usage = response.usage
        cost_info = calculate_cost(
            model=response.model,
            input_tokens=usage.prompt_tokens,
            output_tokens=usage.completion_tokens
        )
        
        logger.info(f"Structured brokerage extraction - Token usage: Input: {usage.prompt_tokens}, Output: {usage.completion_tokens}")
        logger.info(f"Structured brokerage extraction cost: ${cost_info.get('total_cost', 'N/A')}")
        
        return {
            "structured_data": structured_data,
            "extraction_cost": cost_info
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {e}")
        # Return fallback data instead of raising exception
        return {
            "structured_data": {
                "statement_metadata": {
                    "source_file_name": filename,
                    "extraction_error": "Failed to parse AI response as valid JSON"
                }
            },
            "extraction_cost": {"total_cost": 0.0}
        }
    except Exception as e:
        logger.error(f"Error extracting structured brokerage data: {e}")
        raise Exception(f"Failed to extract structured brokerage data: {str(e)}")

def save_brokerage_json(structured_data: Dict, filename: str) -> str:
    """
    Save structured brokerage data to JSON file
    
    Args:
        structured_data: The structured brokerage data
        filename: Original filename to base the output name on
        
    Returns:
        Path to the saved JSON file
    """
    try:
        # Create output filename
        base_name = Path(filename).stem
        output_dir = Path(__file__).parent.parent.parent / "output" / "brokerage"
        output_file = output_dir / f"{base_name}_brokerage.json"
        
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save the structured data
        with open(output_file, 'w') as f:
            json.dump(structured_data, f, indent=2)
        
        logger.info(f"Saved structured brokerage data to: {output_file}")
        return str(output_file)
        
    except Exception as e:
        logger.error(f"Error saving brokerage JSON: {e}")
        raise Exception(f"Failed to save brokerage JSON: {str(e)}")