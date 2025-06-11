#!/usr/bin/env node
/**
 * MCP server for fetch functionality
 */

import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
import { fetchUrl } from './index.js';

// Create an MCP server
const server = new McpServer({
  name: "Fetch MCP",
  version: "1.0.0",
  description: "Web content fetching service for Claude and other LLMs"
});

// Register the fetchUrl tool using the correct API
server.tool('fetchUrl', 
  'Fetches content from a specified URL and returns it as text or markdown',
  {
    url: z.string().describe('The URL to fetch content from'),
    maxLength: z.number().default(15000).describe('Maximum length of content to return'),
    startIndex: z.number().default(0).describe('Index to start from for paginated fetching'),
    raw: z.boolean().default(false).describe('Return raw content without HTML to Markdown conversion')
  },
  async (params) => {
    try {
      console.log(`Fetching URL: ${params.url} (maxLength: ${params.maxLength}, startIndex: ${params.startIndex}, raw: ${params.raw})`);
      const result = await fetchUrl(params.url, { 
        startIndex: params.startIndex, 
        maxLength: params.maxLength, 
        raw: params.raw 
      });
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(result)
          }
        ]
      };
    } catch (error) {
      console.error(`Error fetching URL: ${error.message}`);
      throw new Error(`Failed to fetch URL: ${error.message}`);
    }
  }
);

// Register info resource
server.resource(
  'about',
  'info://about',
  { mimeType: 'text/plain' },
  async () => {
    return {
      contents: [
        {
          uri: 'info://about',
          text: `
    Fetch MCP
    ----------------
    A web content fetching service that enables:
    - Retrieving content from web pages
    - Converting HTML to Markdown
    - Chunking large content with pagination
    - Support for raw content (JSON, etc.)
    
    Use the 'fetchUrl' tool to retrieve content from a URL.
    `
        }
      ]
    };
  }
);

// Start the server with stdio transport
console.log('Starting Fetch MCP server...');
const stdioTransport = new StdioServerTransport();

server.connect(stdioTransport)
  .then(() => {
    console.log('Fetch MCP server is running');
  })
  .catch(error => {
    console.error(`Failed to start Fetch MCP server: ${error.message}`);
    process.exit(1);
  });