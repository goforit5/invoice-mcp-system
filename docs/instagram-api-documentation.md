# Instagram API Documentation

## Overview
The Instagram API allows developers to build applications that can access Instagram professional account data, manage content, moderate comments, and access insights.

## Important Notice
- **Instagram Basic Display API is deprecated** (shutdown December 4, 2024)
- Use the current Instagram API instead

## Authentication Methods

### 1. Instagram API with Instagram Login
- Direct Instagram account authentication
- For accessing Instagram professional accounts

### 2. Instagram API with Facebook Login for Business
- Uses Facebook Login to access Instagram Business accounts
- Requires Facebook Page connection

## Authentication Flow
1. User grants permissions through login process
2. Receive short-lived access token (1 hour validity)
3. Exchange for long-lived access token (60 days validity)

## Access Levels

### Standard Access (Default)
- Basic functionality available immediately

### Advanced Access
- Requires App Review and Business Verification
- Unlocks additional features and higher rate limits

## Rate Limits
- **4800 calls per 24 hours** based on "Number of Impressions"
- Specific rate limits apply to messaging and conversation endpoints
- Rate limiting is per application, not per user

## Key Features

### Content Management
- Getting and managing published media
- Content publishing (with restrictions for some account types)
- Media retrieval and metadata access

### Community Management
- Comment moderation and management
- Discovering hashtagged media and @mentions
- User interaction tracking

### Analytics & Insights
- Measuring media and profile interactions
- Performance metrics and analytics
- Audience insights

### Messaging
- Instagram messaging capabilities
- Conversation management
- Webhook notifications for messages

## Account Requirements
- **Instagram Professional Account required** (Business or Creator)
- Cannot access consumer (non-Professional) Instagram accounts
- Some features require Facebook Page connection

## Technical Limitations
- No support for ordering results
- Limited pagination options
- Content publishing restrictions for certain account types

## Webhooks
- **Mandatory webhook implementation** for notifications
- Must set up webhooks server
- Subscribe to relevant events for real-time updates

## Common Use Cases
1. Social media management tools
2. Content scheduling and publishing
3. Comment moderation systems
4. Analytics and reporting dashboards
5. Customer service through Instagram messaging
6. Hashtag and mention monitoring

## Implementation Recommendations

### For MCP Server Development
1. Choose appropriate authentication method (Instagram Login vs Facebook Login)
2. Implement webhook server for real-time notifications
3. Handle token refresh for long-lived tokens
4. Implement proper rate limiting and error handling
5. Consider Advanced Access requirements for enhanced features

### Required Components
- OAuth 2.0 authentication flow
- Token management system
- Webhook endpoint handling
- Rate limit management
- Error handling and retry logic

## Next Steps for MCP Implementation
1. Set up development environment
2. Register application and get credentials
3. Implement authentication flow
4. Set up webhook server
5. Build API wrapper functions
6. Test with Instagram professional account
7. Implement rate limiting and caching

## Resources
- Official Instagram API Documentation: https://developers.facebook.com/docs/instagram-api
- Instagram Platform Overview: https://developers.facebook.com/docs/instagram-api/overview
- App Review Process: Required for Advanced Access
- Business Verification: Required for certain features