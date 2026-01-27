# Chatbot API Integration Guide

## Quick Start

Your chatbot is already deployed and ready to use as an API! Here's how to integrate it into any website.

---

## Method 1: Embeddable Widget (Easiest)

This is the **fastest way** to add the chatbot to any website. Just copy and paste!

### Step 1: Copy the Widget File
Copy `examples/chatbot-widget.js` to your website's static files directory.

### Step 2: Add to Your HTML
Add these lines before the closing `</body>` tag:

```html
<!-- Include the widget script -->
<script src="path/to/chatbot-widget.js"></script>

<!-- Initialize the widget -->
<script>
  ChatbotWidget.init({
    apiUrl: 'https://chat-agent-9wt6.onrender.com',
    position: 'bottom-right',  // or 'bottom-left'
    primaryColor: '#4F46E5',
    userName: 'John Doe',      // Optional
    userEmail: 'john@example.com'  // Optional
  });
</script>
```

### Step 3: Done!
The chatbot will appear as a floating button in the bottom-right corner of your website.

### Configuration Options
```javascript
ChatbotWidget.init({
  apiUrl: 'https://chat-agent-9wt6.onrender.com',  // Required: Your API URL
  position: 'bottom-right',                         // Optional: 'bottom-right' or 'bottom-left'
  primaryColor: '#4F46E5',                          // Optional: Brand color
  userName: 'John Doe',                             // Optional: User's name
  userEmail: 'john@example.com',                    // Optional: User's email
  welcomeMessage: 'Hi! How can I help?'             // Optional: Custom welcome message
});
```

---

## Method 2: Custom UI with Direct API Calls

Build your own chat interface using the REST API.

### Basic Example (Vanilla JavaScript)

```javascript
let sessionId = null;

async function sendMessage(message) {
  try {
    const response = await fetch('https://chat-agent-9wt6.onrender.com/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: message,
        session_id: sessionId,  // null for first message
        user_name: 'John Doe',
        user_email: 'john@example.com'
      })
    });

    const data = await response.json();
    sessionId = data.session_id;  // Store for next message
    
    return data.response;
  } catch (error) {
    console.error('Error:', error);
    return 'Sorry, something went wrong.';
  }
}

// Usage
sendMessage('Hello!').then(response => {
  console.log('Bot:', response);
});
```

### Complete Custom UI Example
See `examples/custom-ui.html` for a full-page chat interface example.

---

## Method 3: React Integration

### Installation
Copy `examples/react-chatbot/Chatbot.jsx` to your React project.

### Usage
```jsx
import Chatbot from './components/Chatbot';

function App() {
  return (
    <div>
      <h1>My Website</h1>
      
      <Chatbot 
        apiUrl="https://chat-agent-9wt6.onrender.com"
        userName="John Doe"
        userEmail="john@example.com"
        primaryColor="#4F46E5"
        position="bottom-right"
      />
    </div>
  );
}

export default App;
```

---

## Method 4: Other Frameworks

### Vue.js Example
```vue
<template>
  <div class="chat-widget">
    <button @click="isOpen = !isOpen">Chat</button>
    <div v-if="isOpen" class="chat-window">
      <div v-for="msg in messages" :key="msg.id">
        {{ msg.content }}
      </div>
      <input v-model="input" @keyup.enter="sendMessage" />
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      isOpen: false,
      messages: [],
      input: '',
      sessionId: null
    };
  },
  methods: {
    async sendMessage() {
      const response = await fetch('https://chat-agent-9wt6.onrender.com/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: this.input,
          session_id: this.sessionId
        })
      });
      const data = await response.json();
      this.sessionId = data.session_id;
      this.messages.push({ content: data.response });
      this.input = '';
    }
  }
};
</script>
```

### Angular Example
```typescript
import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-chatbot',
  template: `
    <div class="chat-widget">
      <button (click)="toggleChat()">Chat</button>
      <div *ngIf="isOpen" class="chat-window">
        <div *ngFor="let msg of messages">{{ msg.content }}</div>
        <input [(ngModel)]="input" (keyup.enter)="sendMessage()" />
      </div>
    </div>
  `
})
export class ChatbotComponent {
  isOpen = false;
  messages: any[] = [];
  input = '';
  sessionId: number | null = null;

  constructor(private http: HttpClient) {}

  toggleChat() {
    this.isOpen = !this.isOpen;
  }

  sendMessage() {
    this.http.post('https://chat-agent-9wt6.onrender.com/api/chat', {
      message: this.input,
      session_id: this.sessionId
    }).subscribe((data: any) => {
      this.sessionId = data.session_id;
      this.messages.push({ content: data.response });
      this.input = '';
    });
  }
}
```

---

## API Endpoints Reference

### POST /api/chat
Send a message and receive a response.

**Request:**
```json
{
  "message": "Hello",
  "session_id": null,
  "user_name": "John Doe",
  "user_email": "john@example.com"
}
```

**Response:**
```json
{
  "response": "Hi! How can I help you?",
  "session_id": 123,
  "tool_executed": null
}
```

### GET /api/config
Get current chatbot configuration.

### POST /api/config
Update chatbot configuration.

### GET /api/analytics
Get usage analytics.

### POST /api/config/upload_brochure
Upload PDF/text file to update knowledge base.

**See `API_DOCUMENTATION.md` for complete API reference.**

---

## Session Management

### How Sessions Work
1. **First message**: Send with `session_id: null`
2. **Server returns**: A `session_id` in the response
3. **Subsequent messages**: Include the same `session_id`
4. **Conversation context**: Automatically maintained by the API

### Example Flow
```javascript
// First message
let sessionId = null;

const response1 = await sendMessage('Hello', sessionId);
sessionId = response1.session_id;  // Store this!

// Second message (continues conversation)
const response2 = await sendMessage('Tell me more', sessionId);
```

---

## Error Handling

Always implement error handling for network requests:

```javascript
async function sendMessage(message, sessionId) {
  try {
    const response = await fetch('https://chat-agent-9wt6.onrender.com/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, session_id: sessionId })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Chat error:', error);
    return {
      response: 'Sorry, something went wrong. Please try again.',
      session_id: sessionId
    };
  }
}
```

---

## CORS and Security

### CORS
The API currently allows requests from **all origins** (`*`). This means you can call it from any website without CORS issues.

### Security Recommendations
For production use, consider:
1. Implementing API authentication
2. Rate limiting
3. Restricting CORS to specific domains
4. Adding request validation

---

## Testing Your Integration

### 1. Test with cURL
```bash
curl -X POST https://chat-agent-9wt6.onrender.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "user_name": "Test User"}'
```

### 2. Test with Python
See `examples/test_api.py` for a complete test script.

### 3. Test with Browser Console
Open your browser's developer console and run:
```javascript
fetch('https://chat-agent-9wt6.onrender.com/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: 'Hello' })
})
.then(r => r.json())
.then(data => console.log(data));
```

---

## Deployment Checklist

- [ ] Copy widget file to your static files
- [ ] Update `apiUrl` to your production URL
- [ ] Test on different browsers (Chrome, Firefox, Safari)
- [ ] Test on mobile devices
- [ ] Verify session persistence works
- [ ] Test error handling
- [ ] Check loading states and animations
- [ ] Verify CORS is working
- [ ] Test with real user scenarios

---

## Troubleshooting

### Widget doesn't appear
- Check browser console for errors
- Verify the script is loaded correctly
- Ensure `ChatbotWidget.init()` is called after the script loads

### API requests fail
- Check network tab in browser dev tools
- Verify the API URL is correct
- Check CORS headers
- Ensure request format matches API documentation

### Session not persisting
- Verify you're storing and sending the `session_id`
- Check that `session_id` is included in subsequent requests

### Styling conflicts
- The widget uses scoped styles to avoid conflicts
- If needed, adjust z-index or positioning in the CSS

---

## Support and Documentation

- **API Documentation**: See `API_DOCUMENTATION.md`
- **Examples**: Check the `examples/` folder
- **Live Demo**: Open `examples/simple-integration.html` in a browser

---

## Next Steps

1. Choose your integration method (Widget, Custom UI, or Framework)
2. Follow the relevant section above
3. Test thoroughly
4. Deploy to production
5. Monitor usage with `/api/analytics`

Happy coding! 🚀
