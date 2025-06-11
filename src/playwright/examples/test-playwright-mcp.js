// Simple script to test that the Playwright MCP server is working correctly

console.log('Starting Playwright MCP test...');

// This is a simple test script that you would run in Claude
// Below are example commands that Claude would issue to the Playwright MCP server

/*
Example interaction with Claude:

User: Can you use Playwright to visit example.com and tell me what the heading says?

Claude:
I'll use Playwright to visit example.com and check the heading.

[Claude would make these API calls to the Playwright MCP server]
1. browser_navigate with url: "https://example.com"
2. browser_snapshot to get the page content
3. Analyze the snapshot to find the heading
4. Return the heading text to the user

Sample response from the snapshot would include DOM elements like:
{
  "nodeName": "H1",
  "textContent": "Example Domain",
  "ref": "node-123",
  ...
}

Claude would then report: "The heading on example.com says 'Example Domain'."
*/

console.log('To test the Playwright MCP server:');
console.log('1. Start the server with: npm run mcp-playwright');
console.log('2. Configure Claude to use your Playwright MCP server');
console.log('3. Ask Claude to use Playwright to visit a website and interact with it');
console.log('\nExample prompt: "Use Playwright to visit example.com and tell me what the main heading says."');