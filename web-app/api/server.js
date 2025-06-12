#!/usr/bin/env node

// This file now redirects to the new MCP-based server
// The new server provides 100% MCP tool-based processing

console.log('🔄 Redirecting to MCP-based server...');
console.log('📄 Starting Universal Document AI with MCP tools');

// Import and start the MCP-based server
import('./mcp-server.js')
  .then(() => {
    console.log('✅ MCP-based server loaded successfully');
  })
  .catch((error) => {
    console.error('❌ Failed to load MCP-based server:', error);
    process.exit(1);
  });