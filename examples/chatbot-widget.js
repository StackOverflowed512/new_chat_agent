/**
 * Chatbot Widget - Embeddable Chat Interface
 * 
 * Usage:
 * 1. Include this script in your HTML:
 *    <script src="https://chat-agent-9wt6.onrender.com/static/chatbot-widget.js"></script>
 * 
 * 2. Initialize the widget:
 *    <script>
 *      ChatbotWidget.init({
 *        apiUrl: 'https://chat-agent-9wt6.onrender.com',
 *        position: 'bottom-right', // or 'bottom-left'
 *        primaryColor: '#4F46E5',
 *        userName: 'John Doe',
 *        userEmail: 'john@example.com'
 *      });
 *    </script>
 */

(function() {
  'use strict';

  const ChatbotWidget = {
    config: {
      apiUrl: 'https://chat-agent-9wt6.onrender.com',
      position: 'bottom-right',
      primaryColor: '#4F46E5',
      userName: null,
      userEmail: null,
      welcomeMessage: 'Hi! How can I help you today?'
    },
    
    sessionId: null,
    isOpen: false,
    messageHistory: [],

    init: function(options) {
      // Merge user options with defaults
      this.config = { ...this.config, ...options };
      
      // Create widget HTML
      this.createWidget();
      
      // Attach event listeners
      this.attachEventListeners();
      
      // Add welcome message
      this.addMessage('bot', this.config.welcomeMessage);
    },

    createWidget: function() {
      const widgetHTML = `
        <div id="chatbot-widget" class="chatbot-widget ${this.config.position}">
          <!-- Chat Button -->
          <button id="chatbot-toggle" class="chatbot-toggle" aria-label="Open chat">
            <svg class="chatbot-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
            <svg class="chatbot-close-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>

          <!-- Chat Window -->
          <div id="chatbot-window" class="chatbot-window">
            <!-- Header -->
            <div class="chatbot-header">
              <div class="chatbot-header-content">
                <div class="chatbot-avatar">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2zm0 18a8 8 0 1 1 8-8 8 8 0 0 1-8 8z"></path>
                    <circle cx="12" cy="12" r="3"></circle>
                  </svg>
                </div>
                <div>
                  <div class="chatbot-title">Chat Assistant</div>
                  <div class="chatbot-status">Online</div>
                </div>
              </div>
              <button id="chatbot-close" class="chatbot-close-btn" aria-label="Close chat">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </button>
            </div>

            <!-- Messages -->
            <div id="chatbot-messages" class="chatbot-messages"></div>

            <!-- Input -->
            <div class="chatbot-input-container">
              <textarea 
                id="chatbot-input" 
                class="chatbot-input" 
                placeholder="Type your message..."
                rows="1"
              ></textarea>
              <button id="chatbot-send" class="chatbot-send-btn" aria-label="Send message">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="22" y1="2" x2="11" y2="13"></line>
                  <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                </svg>
              </button>
            </div>
          </div>
        </div>
      `;

      // Add CSS
      this.addStyles();

      // Add HTML to page
      document.body.insertAdjacentHTML('beforeend', widgetHTML);
    },

    addStyles: function() {
      const style = document.createElement('style');
      style.textContent = `
        .chatbot-widget {
          position: fixed;
          z-index: 9999;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        }

        .chatbot-widget.bottom-right {
          bottom: 20px;
          right: 20px;
        }

        .chatbot-widget.bottom-left {
          bottom: 20px;
          left: 20px;
        }

        .chatbot-toggle {
          width: 60px;
          height: 60px;
          border-radius: 50%;
          background: ${this.config.primaryColor};
          border: none;
          cursor: pointer;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.3s ease;
          color: white;
        }

        .chatbot-toggle:hover {
          transform: scale(1.1);
          box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
        }

        .chatbot-toggle .chatbot-close-icon {
          display: none;
        }

        .chatbot-widget.open .chatbot-toggle .chatbot-icon {
          display: none;
        }

        .chatbot-widget.open .chatbot-toggle .chatbot-close-icon {
          display: block;
        }

        .chatbot-window {
          position: absolute;
          bottom: 80px;
          right: 0;
          width: 380px;
          height: 600px;
          max-height: calc(100vh - 120px);
          background: white;
          border-radius: 16px;
          box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
          display: none;
          flex-direction: column;
          overflow: hidden;
        }

        .chatbot-widget.bottom-left .chatbot-window {
          right: auto;
          left: 0;
        }

        .chatbot-widget.open .chatbot-window {
          display: flex;
        }

        .chatbot-header {
          background: ${this.config.primaryColor};
          color: white;
          padding: 16px;
          display: flex;
          align-items: center;
          justify-content: space-between;
        }

        .chatbot-header-content {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .chatbot-avatar {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          background: rgba(255, 255, 255, 0.2);
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .chatbot-title {
          font-weight: 600;
          font-size: 16px;
        }

        .chatbot-status {
          font-size: 12px;
          opacity: 0.9;
        }

        .chatbot-close-btn {
          background: none;
          border: none;
          color: white;
          cursor: pointer;
          padding: 4px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 4px;
          transition: background 0.2s;
        }

        .chatbot-close-btn:hover {
          background: rgba(255, 255, 255, 0.1);
        }

        .chatbot-messages {
          flex: 1;
          overflow-y: auto;
          padding: 16px;
          background: #f9fafb;
        }

        .chatbot-message {
          margin-bottom: 16px;
          display: flex;
          gap: 8px;
          animation: messageSlideIn 0.3s ease;
        }

        @keyframes messageSlideIn {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .chatbot-message.user {
          flex-direction: row-reverse;
        }

        .chatbot-message-avatar {
          width: 32px;
          height: 32px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;
          font-size: 14px;
          font-weight: 600;
        }

        .chatbot-message.bot .chatbot-message-avatar {
          background: ${this.config.primaryColor};
          color: white;
        }

        .chatbot-message.user .chatbot-message-avatar {
          background: #e5e7eb;
          color: #374151;
        }

        .chatbot-message-content {
          max-width: 70%;
          padding: 12px 16px;
          border-radius: 12px;
          line-height: 1.5;
          font-size: 14px;
        }

        .chatbot-message.bot .chatbot-message-content {
          background: white;
          color: #1f2937;
          border-bottom-left-radius: 4px;
        }

        .chatbot-message.user .chatbot-message-content {
          background: ${this.config.primaryColor};
          color: white;
          border-bottom-right-radius: 4px;
        }

        .chatbot-typing {
          display: flex;
          gap: 4px;
          padding: 12px 16px;
        }

        .chatbot-typing span {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: #9ca3af;
          animation: typing 1.4s infinite;
        }

        .chatbot-typing span:nth-child(2) {
          animation-delay: 0.2s;
        }

        .chatbot-typing span:nth-child(3) {
          animation-delay: 0.4s;
        }

        @keyframes typing {
          0%, 60%, 100% {
            transform: translateY(0);
            opacity: 0.7;
          }
          30% {
            transform: translateY(-10px);
            opacity: 1;
          }
        }

        .chatbot-input-container {
          padding: 16px;
          background: white;
          border-top: 1px solid #e5e7eb;
          display: flex;
          gap: 8px;
          align-items: flex-end;
        }

        .chatbot-input {
          flex: 1;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          padding: 10px 12px;
          font-size: 14px;
          resize: none;
          max-height: 100px;
          font-family: inherit;
          outline: none;
          transition: border-color 0.2s;
        }

        .chatbot-input:focus {
          border-color: ${this.config.primaryColor};
        }

        .chatbot-send-btn {
          width: 40px;
          height: 40px;
          border-radius: 8px;
          background: ${this.config.primaryColor};
          border: none;
          color: white;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s;
          flex-shrink: 0;
        }

        .chatbot-send-btn:hover:not(:disabled) {
          background: ${this.adjustColor(this.config.primaryColor, -10)};
        }

        .chatbot-send-btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        @media (max-width: 480px) {
          .chatbot-window {
            width: calc(100vw - 40px);
            height: calc(100vh - 120px);
          }
        }
      `;
      document.head.appendChild(style);
    },

    attachEventListeners: function() {
      const toggle = document.getElementById('chatbot-toggle');
      const closeBtn = document.getElementById('chatbot-close');
      const sendBtn = document.getElementById('chatbot-send');
      const input = document.getElementById('chatbot-input');

      toggle.addEventListener('click', () => this.toggleWidget());
      closeBtn.addEventListener('click', () => this.toggleWidget());
      sendBtn.addEventListener('click', () => this.sendMessage());
      
      input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          this.sendMessage();
        }
      });

      // Auto-resize textarea
      input.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 100) + 'px';
      });
    },

    toggleWidget: function() {
      this.isOpen = !this.isOpen;
      const widget = document.getElementById('chatbot-widget');
      
      if (this.isOpen) {
        widget.classList.add('open');
        document.getElementById('chatbot-input').focus();
      } else {
        widget.classList.remove('open');
      }
    },

    addMessage: function(sender, content) {
      const messagesContainer = document.getElementById('chatbot-messages');
      const messageDiv = document.createElement('div');
      messageDiv.className = `chatbot-message ${sender}`;
      
      const avatar = sender === 'bot' ? '🤖' : '👤';
      
      messageDiv.innerHTML = `
        <div class="chatbot-message-avatar">${avatar}</div>
        <div class="chatbot-message-content">${this.escapeHtml(content)}</div>
      `;
      
      messagesContainer.appendChild(messageDiv);
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
      
      this.messageHistory.push({ sender, content });
    },

    showTyping: function() {
      const messagesContainer = document.getElementById('chatbot-messages');
      const typingDiv = document.createElement('div');
      typingDiv.id = 'chatbot-typing-indicator';
      typingDiv.className = 'chatbot-message bot';
      typingDiv.innerHTML = `
        <div class="chatbot-message-avatar">🤖</div>
        <div class="chatbot-message-content">
          <div class="chatbot-typing">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      `;
      messagesContainer.appendChild(typingDiv);
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    },

    hideTyping: function() {
      const typingIndicator = document.getElementById('chatbot-typing-indicator');
      if (typingIndicator) {
        typingIndicator.remove();
      }
    },

    async sendMessage() {
      const input = document.getElementById('chatbot-input');
      const message = input.value.trim();
      
      if (!message) return;
      
      // Add user message to UI
      this.addMessage('user', message);
      input.value = '';
      input.style.height = 'auto';
      
      // Disable send button
      const sendBtn = document.getElementById('chatbot-send');
      sendBtn.disabled = true;
      
      // Show typing indicator
      this.showTyping();
      
      try {
        const response = await fetch(`${this.config.apiUrl}/api/chat`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            message: message,
            session_id: this.sessionId,
            user_name: this.config.userName,
            user_email: this.config.userEmail
          })
        });
        
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        
        const data = await response.json();
        
        // Store session ID
        this.sessionId = data.session_id;
        
        // Hide typing and show response
        this.hideTyping();
        this.addMessage('bot', data.response);
        
      } catch (error) {
        console.error('Chat error:', error);
        this.hideTyping();
        this.addMessage('bot', 'Sorry, I encountered an error. Please try again.');
      } finally {
        sendBtn.disabled = false;
        input.focus();
      }
    },

    escapeHtml: function(text) {
      const div = document.createElement('div');
      div.textContent = text;
      return div.innerHTML;
    },

    adjustColor: function(color, amount) {
      // Simple color adjustment (darken/lighten)
      const num = parseInt(color.replace('#', ''), 16);
      const r = Math.max(0, Math.min(255, (num >> 16) + amount));
      const g = Math.max(0, Math.min(255, ((num >> 8) & 0x00FF) + amount));
      const b = Math.max(0, Math.min(255, (num & 0x0000FF) + amount));
      return '#' + ((r << 16) | (g << 8) | b).toString(16).padStart(6, '0');
    }
  };

  // Expose to global scope
  window.ChatbotWidget = ChatbotWidget;
})();
