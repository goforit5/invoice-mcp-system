/**
 * Fetch MCP Module
 * Provides web content fetching capabilities for Claude
 */

import https from 'https';
import http from 'http';
import { URL } from 'url';

// Cache for storing fetched content
const contentCache = new Map();
const CACHE_TTL = 15 * 60 * 1000; // 15 minutes

/**
 * Fetch content from a URL
 * @param {string} url - The URL to fetch
 * @param {Object} options - Options for fetching
 * @returns {Promise<Object>} - The fetched content
 */
export function fetchUrl(url, { startIndex = 0, maxLength = 15000, raw = false } = {}) {
  return new Promise((resolve, reject) => {
    if (!url) {
      return reject(new Error('URL is required'));
    }

    // Check if URL is valid
    let parsedUrl;
    try {
      parsedUrl = new URL(url);
    } catch (error) {
      return reject(new Error('Invalid URL'));
    }

    // Check cache first
    const cacheKey = `${url}:${startIndex}:${maxLength}:${raw}`;
    if (contentCache.has(cacheKey)) {
      const cachedData = contentCache.get(cacheKey);
      if (Date.now() - cachedData.timestamp < CACHE_TTL) {
        return resolve(cachedData.data);
      } else {
        // Remove expired cache entry
        contentCache.delete(cacheKey);
      }
    }

    const client = parsedUrl.protocol === 'https:' ? https : http;

    // Always force HTTPS if HTTP is provided
    if (parsedUrl.protocol === 'http:') {
      parsedUrl.protocol = 'https:';
    }

    const options = {
      method: 'GET',
      headers: {
        'User-Agent': 'Claude-Fetch/1.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml,application/json,text/plain;q=0.9,*/*;q=0.8',
      }
    };

    const req = client.request(parsedUrl, options, (res) => {
      // Handle redirects
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        return fetchUrl(res.headers.location, { startIndex, maxLength, raw })
          .then(resolve)
          .catch(reject);
      }

      if (res.statusCode !== 200) {
        return reject(new Error(`HTTP error: ${res.statusCode}`));
      }

      let contentType = res.headers['content-type'] || '';
      let isHTML = contentType.includes('text/html');
      let isJSON = contentType.includes('application/json');
      let isText = contentType.includes('text/');

      // Set encoding for text content
      if (isHTML || isText || isJSON) {
        res.setEncoding('utf8');
      } else if (!raw) {
        // If not text and raw mode is not requested, reject
        return reject(new Error('Unsupported content type: ' + contentType));
      }

      let rawData = '';
      let byteCounter = 0;
      let contentStarted = false;

      res.on('data', (chunk) => {
        // For binary data in raw mode
        if (typeof chunk !== 'string') {
          byteCounter += chunk.length;
          if (byteCounter > startIndex + maxLength) {
            req.destroy(); // Stop the request once we have enough data
          }

          if (byteCounter > startIndex) {
            if (!contentStarted) {
              rawData = chunk.slice(startIndex - (byteCounter - chunk.length));
              contentStarted = true;
            } else {
              rawData = Buffer.concat([rawData, chunk]);
            }
          }

          return;
        }

        // For text data
        byteCounter += Buffer.byteLength(chunk, 'utf8');

        if (rawData.length < maxLength) {
          rawData += chunk;
          if (rawData.length > maxLength) {
            rawData = rawData.slice(0, maxLength);
            req.destroy(); // Stop the request once we have enough data
          }
        } else {
          req.destroy(); // Stop the request once we have enough data
        }
      });

      res.on('end', () => {
        let content = rawData;

        // If this is HTML and not in raw mode, convert to Markdown
        if (isHTML && !raw) {
          content = convertHtmlToMarkdown(content);
        }

        // For text content, handle the startIndex by characters
        if (typeof content === 'string' && startIndex > 0) {
          content = content.slice(startIndex, startIndex + maxLength);
        }

        // Truncate to the specified length
        if (typeof content === 'string' && content.length > maxLength) {
          content = content.slice(0, maxLength);
        }

        const isTruncated = byteCounter > startIndex + maxLength;

        const result = {
          content: content,
          contentType: contentType,
          truncated: isTruncated,
          startIndex: startIndex,
          length: typeof content === 'string' ? content.length : content.byteLength,
        };

        // Cache the result
        contentCache.set(cacheKey, {
          timestamp: Date.now(),
          data: result
        });

        // Cleanup old cache entries periodically
        cleanupCache();

        resolve(result);
      });
    });

    req.on('error', (error) => {
      reject(error);
    });

    req.end();
  });
}

/**
 * Very simple HTML to Markdown conversion
 * @param {string} html - The HTML to convert
 * @returns {string} - The converted Markdown
 */
function convertHtmlToMarkdown(html) {
  // This is a very simplified converter
  // In a production environment, use a dedicated library

  let markdown = html;

  // Remove DOCTYPE, html, head tags and their content
  markdown = markdown.replace(/<\!DOCTYPE.*?>|<html.*?>|<\/html>|<head>.*?<\/head>/gs, '');

  // Remove scripts and styles
  markdown = markdown.replace(/<script.*?>.*?<\/script>|<style.*?>.*?<\/style>/gs, '');

  // Convert headings
  markdown = markdown.replace(/<h1.*?>(.*?)<\/h1>/g, '# $1\n\n');
  markdown = markdown.replace(/<h2.*?>(.*?)<\/h2>/g, '## $1\n\n');
  markdown = markdown.replace(/<h3.*?>(.*?)<\/h3>/g, '### $1\n\n');
  markdown = markdown.replace(/<h4.*?>(.*?)<\/h4>/g, '#### $1\n\n');
  markdown = markdown.replace(/<h5.*?>(.*?)<\/h5>/g, '##### $1\n\n');
  markdown = markdown.replace(/<h6.*?>(.*?)<\/h6>/g, '###### $1\n\n');

  // Convert paragraphs
  markdown = markdown.replace(/<p.*?>(.*?)<\/p>/gs, '$1\n\n');

  // Convert links
  markdown = markdown.replace(/<a.*?href="(.*?)".*?>(.*?)<\/a>/g, '[$2]($1)');

  // Convert bold and italic
  markdown = markdown.replace(/<strong.*?>(.*?)<\/strong>|<b.*?>(.*?)<\/b>/g, '**$1$2**');
  markdown = markdown.replace(/<em.*?>(.*?)<\/em>|<i.*?>(.*?)<\/i>/g, '*$1$2*');

  // Convert lists
  markdown = markdown.replace(/<ul.*?>(.*?)<\/ul>/gs, (match, content) => {
    return content.replace(/<li.*?>(.*?)<\/li>/gs, '- $1\n');
  });

  markdown = markdown.replace(/<ol.*?>(.*?)<\/ol>/gs, (match, content) => {
    let counter = 1;
    return content.replace(/<li.*?>(.*?)<\/li>/gs, (m, item) => {
      return `${counter++}. ${item}\n`;
    });
  });

  // Remove remaining HTML tags
  markdown = markdown.replace(/<[^>]*>/g, '');

  // Decode HTML entities
  markdown = markdown.replace(/&lt;/g, '<');
  markdown = markdown.replace(/&gt;/g, '>');
  markdown = markdown.replace(/&quot;/g, '"');
  markdown = markdown.replace(/&apos;/g, "'");
  markdown = markdown.replace(/&amp;/g, '&');

  // Fix multiple line breaks
  markdown = markdown.replace(/\n\s*\n\s*\n/g, '\n\n');

  return markdown.trim();
}

/**
 * Clean up expired cache entries
 */
function cleanupCache() {
  const now = Date.now();
  for (const [key, value] of contentCache.entries()) {
    if (now - value.timestamp > CACHE_TTL) {
      contentCache.delete(key);
    }
  }
}