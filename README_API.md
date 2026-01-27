# Chatbot API - Ready to Use! 🚀

Your chatbot is **deployed and ready** to be used as an API from any website!

## 🌐 Live API URL
```
https://chat-agent-9wt6.onrender.com
```

## ⚡ Quick Start (2 Minutes)

Add these lines to any HTML page:

```html
<!-- Include the widget -->
<script src="https://chat-agent-9wt6.onrender.com/static/chatbot-widget.js"></script>

<!-- Initialize -->
<script>
  ChatbotWidget.init({
    apiUrl: 'https://chat-agent-9wt6.onrender.com'
  });
</script>
```

**That's it!** A chat button will appear in the bottom-right corner.

## 📚 Documentation

- **[API Documentation](API_DOCUMENTATION.md)** - Complete API reference
- **[Integration Guide](INTEGRATION_GUIDE.md)** - Step-by-step integration instructions
- **[Examples](examples/)** - Working code examples

## 🎯 Integration Methods

### 1. Embeddable Widget (Easiest)
Perfect for adding chat to any website with minimal code.

```html
<script src="https://chat-agent-9wt6.onrender.com/static/chatbot-widget.js"></script>
<script>
  ChatbotWidget.init({
    apiUrl: 'https://chat-agent-9wt6.onrender.com',
    primaryColor: '#4F46E5',
    userName: 'John Doe',
    userEmail: 'john@example.com'
  });
</script>
```

**See:** `examples/simple-integration.html`

### 2. Custom UI with API Calls
Build your own interface using the REST API.

```javascript
const response = await fetch('https://chat-agent-9wt6.onrender.com/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'Hello!',
    session_id: null
  })
});

const data = await response.json();
console.log(data.response);
```

**See:** `examples/custom-ui.html`

### 3. React Component
Drop-in React component for React applications.

```jsx
import Chatbot from './Chatbot';

function App() {
  return <Chatbot apiUrl="https://chat-agent-9wt6.onrender.com" />;
}
```

**See:** `examples/react-chatbot/Chatbot.jsx`

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat` | POST | Send message, get response |
| `/api/config` | GET | Get chatbot configuration |
| `/api/config` | POST | Update configuration |
| `/api/presets` | GET | Get available presets |
| `/api/analytics` | GET | Get usage analytics |
| `/api/config/upload_brochure` | POST | Upload knowledge base |

## 💬 Example API Call

```bash
curl -X POST https://chat-agent-9wt6.onrender.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, I need help",
    "user_name": "John Doe",
    "user_email": "john@example.com"
  }'
```

**Response:**
```json
{
  "response": "Hi! How can I help you today?",
  "session_id": 123,
  "tool_executed": null
}
```

## 🧪 Testing

### Quick Test (Browser Console)
```javascript
fetch('https://chat-agent-9wt6.onrender.com/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: 'Hello' })
})
.then(r => r.json())
.then(data => console.log(data));
```

### Python Test Script
```bash
cd examples
python test_api.py
```

For interactive mode:
```bash
python test_api.py interactive
```

## 📱 Features

- ✅ **RESTful API** - Standard HTTP endpoints
- ✅ **Session Management** - Maintains conversation context
- ✅ **CORS Enabled** - Works from any domain
- ✅ **No Authentication** - Easy to integrate (add auth for production)
- ✅ **Embeddable Widget** - Drop-in solution
- ✅ **Custom UI Support** - Build your own interface
- ✅ **Framework Support** - React, Vue, Angular examples
- ✅ **Analytics** - Track usage and conversations
- ✅ **File Upload** - Update knowledge base via API

## 🎨 Customization

### Widget Options
```javascript
ChatbotWidget.init({
  apiUrl: 'https://chat-agent-9wt6.onrender.com',
  position: 'bottom-right',        // or 'bottom-left'
  primaryColor: '#4F46E5',         // Your brand color
  userName: 'John Doe',            // Optional
  userEmail: 'john@example.com',   // Optional
  welcomeMessage: 'Hi! How can I help?' // Custom greeting
});
```

## 📂 Project Structure

```
.
├── API_DOCUMENTATION.md      # Complete API reference
├── INTEGRATION_GUIDE.md      # Step-by-step integration guide
├── README_API.md            # This file
├── examples/
│   ├── chatbot-widget.js    # Embeddable widget
│   ├── simple-integration.html  # Widget demo
│   ├── custom-ui.html       # Custom UI example
│   ├── react-chatbot/
│   │   └── Chatbot.jsx      # React component
│   └── test_api.py          # API test script
└── static/
    └── chatbot-widget.js    # Served widget file
```

## 🚀 Deployment

Your chatbot is already deployed at:
```
https://chat-agent-9wt6.onrender.com
```

To use it on your website:
1. Choose an integration method (widget, custom UI, or framework)
2. Copy the relevant code from the examples
3. Update the API URL if needed
4. Test thoroughly
5. Deploy!

## 🔒 Security Notes

**Current Setup:**
- CORS: Allows all origins (`*`)
- Authentication: None
- Rate Limiting: None

**For Production:**
Consider adding:
- API key authentication
- Rate limiting
- CORS restrictions to specific domains
- Request validation
- HTTPS enforcement

## 📖 Documentation Links

- **API Reference**: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- **Integration Guide**: [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)
- **Examples**: [examples/](examples/)

## 🆘 Troubleshooting

### Widget doesn't appear
- Check browser console for errors
- Verify script URL is correct
- Ensure `ChatbotWidget.init()` is called

### API requests fail
- Check network tab in dev tools
- Verify API URL is correct
- Check CORS headers

### Session not persisting
- Ensure you're storing `session_id`
- Include `session_id` in subsequent requests

## 📞 Support

For issues or questions:
1. Check the documentation files
2. Review the examples
3. Test with `test_api.py`
4. Check browser console for errors

## 🎉 You're Ready!

Your chatbot API is live and ready to integrate into any website. Choose your preferred method and start building!

**Happy coding! 🚀**
