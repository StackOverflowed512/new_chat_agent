# Chatbot API Documentation

## Base URL
```
Production: https://chat-agent-9wt6.onrender.com
Local: http://localhost:8000
```

## Overview
This chatbot provides a RESTful API that can be integrated into any website or application. The API supports chat conversations, configuration management, analytics, and file uploads.

---

## Authentication
Currently, the API is **open** (no authentication required). CORS is enabled for all origins (`*`).

---

## API Endpoints

### 1. Chat Endpoint
**Send a message to the chatbot and receive a response.**

#### Request
```http
POST /api/chat
Content-Type: application/json

{
  "message": "Hello, I need help",
  "session_id": null,          // Optional: null for new session, or existing session ID
  "user_name": "John Doe",     // Optional: user's name
  "user_email": "john@example.com"  // Optional: user's email
}
```

#### Response
```json
{
  "response": "Hello! How can I help you today?",
  "session_id": 123,
  "tool_executed": null  // Will contain tool name if a tool was used (e.g., "generate_flyer")
}
```

#### Example with cURL
```bash
curl -X POST https://chat-agent-9wt6.onrender.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What services do you offer?",
    "user_name": "Jane Smith",
    "user_email": "jane@example.com"
  }'
```

#### Example with JavaScript (Fetch)
```javascript
async function sendMessage(message, sessionId = null) {
  const response = await fetch('https://chat-agent-9wt6.onrender.com/api/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message: message,
      session_id: sessionId,
      user_name: 'John Doe',
      user_email: 'john@example.com'
    })
  });
  
  const data = await response.json();
  return data;
}

// Usage
sendMessage("Hello!").then(data => {
  console.log("Bot:", data.response);
  console.log("Session ID:", data.session_id);
});
```

---

### 2. Get Configuration
**Retrieve current chatbot configuration.**

#### Request
```http
GET /api/config
```

#### Response
```json
{
  "company_name": "Your Company",
  "ceo_email": "ceo@company.com",
  "agent_name": "Company Assistant",
  "system_prompt": "You are a helpful assistant..."
}
```

#### Example
```javascript
fetch('https://chat-agent-9wt6.onrender.com/api/config')
  .then(res => res.json())
  .then(config => console.log(config));
```

---

### 3. Update Configuration
**Update chatbot configuration.**

#### Request
```http
POST /api/config
Content-Type: application/json

{
  "company_name": "New Company Name",
  "ceo_email": "newemail@company.com",
  "agent_name": "Custom Assistant",
  "system_prompt": "Custom system prompt",
  "extra_config": {
    "custom_field": "custom_value"
  }
}
```

#### Response
```json
{
  "status": "Configuration updated",
  "config": {
    "company_name": "New Company Name",
    ...
  }
}
```

---

### 4. Get Available Presets
**Get list of domain-specific presets.**

#### Request
```http
GET /api/presets
```

#### Response
```json
[
  {
    "id": "travel",
    "company_name": "Travel Agency",
    "ceo_email": "ceo@travel.com",
    "description": "Travel and tourism services"
  },
  ...
]
```

---

### 5. Apply Preset
**Apply a domain-specific preset.**

#### Request
```http
POST /api/presets/apply
Content-Type: application/json

{
  "preset_id": "travel"
}
```

#### Response
```json
{
  "status": "success",
  "message": "Applied preset: Travel Agency"
}
```

---

### 6. Upload Brochure/Knowledge Base
**Upload a PDF or text file to update the chatbot's knowledge base.**

#### Request
```http
POST /api/config/upload_brochure
Content-Type: multipart/form-data

file: [PDF or Text File]
```

#### Response
```json
{
  "status": "success",
  "message": "Brochure processed and Knowledge Base updated.",
  "extracted_chars": 5432
}
```

#### Example with JavaScript
```javascript
async function uploadBrochure(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('https://chat-agent-9wt6.onrender.com/api/config/upload_brochure', {
    method: 'POST',
    body: formData
  });
  
  return await response.json();
}

// Usage with file input
document.getElementById('fileInput').addEventListener('change', (e) => {
  const file = e.target.files[0];
  uploadBrochure(file).then(result => console.log(result));
});
```

---

### 7. Get Analytics
**Retrieve chatbot usage analytics.**

#### Request
```http
GET /api/analytics
```

#### Response
```json
{
  "total_sessions": 150,
  "average_duration_minutes": 5.2,
  "users": [
    {
      "name": "John Doe",
      "email": "john@example.com",
      "mobile": "1234567890",
      "last_topic": "Product Inquiry"
    }
  ]
}
```

---

## Session Management

### How Sessions Work
1. **First Message**: Send a message with `session_id: null`
2. **Response**: You'll receive a `session_id` in the response
3. **Subsequent Messages**: Include the same `session_id` to continue the conversation
4. **Conversation History**: The API automatically maintains conversation context

### Example Flow
```javascript
let currentSessionId = null;

async function chat(message) {
  const response = await fetch('https://chat-agent-9wt6.onrender.com/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: message,
      session_id: currentSessionId
    })
  });
  
  const data = await response.json();
  currentSessionId = data.session_id; // Store for next message
  return data.response;
}

// First message
chat("Hello").then(response => console.log(response));

// Second message (uses same session)
chat("Tell me more").then(response => console.log(response));
```

---

## Error Handling

### HTTP Status Codes
- `200` - Success
- `404` - Resource not found (e.g., invalid session_id)
- `422` - Validation error (invalid request format)
- `500` - Server error

### Example Error Response
```json
{
  "detail": "Session not found"
}
```

### Error Handling Example
```javascript
async function sendMessage(message, sessionId) {
  try {
    const response = await fetch('https://chat-agent-9wt6.onrender.com/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, session_id: sessionId })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'API request failed');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Chat error:', error);
    return { response: 'Sorry, something went wrong. Please try again.', session_id: sessionId };
  }
}
```

---

## Rate Limiting
Currently, there are **no rate limits** implemented. Consider implementing rate limiting for production use.

---

## CORS Policy
The API allows requests from **all origins** (`*`). This means you can call it from any website without CORS issues.

---

## Best Practices

1. **Store Session ID**: Always store the session_id to maintain conversation context
2. **Handle Errors**: Implement proper error handling for network failures
3. **User Information**: Provide user_name and user_email for better analytics
4. **Loading States**: Show loading indicators while waiting for responses
5. **Timeout**: Implement request timeouts (recommended: 30 seconds)

---

## Next Steps
- See `examples/` folder for complete integration examples
- Check `INTEGRATION_GUIDE.md` for step-by-step integration instructions
- Review `chatbot-widget.js` for a ready-to-use embeddable widget
