from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import json
from typing import Dict, List
import re

app = FastAPI()

app.mount("/assets", StaticFiles(directory="assets"), name="assets")

# Allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom chatbot knowledge base - You can train the bot by adding more Q&A pairs
KNOWLEDGE_BASE = {
    "greetings": {
        "patterns": ["hello", "hi", "hey", "good morning", "good evening", "greetings"],
        "responses": ["Hello! How can I assist you today?", "Hi there! What can I help you with?", "Greetings! How may I help you?"]
    },
    "company_info": {
        "patterns": ["about vasp", "what is vasp", "company info", "who are you", "tell me about vasp"],
        "responses": ["Vasp is a leading technology company specializing in innovative solutions. We provide cutting-edge services to help businesses grow and succeed."]
    },
    "services": {
        "patterns": ["services", "what do you offer", "products", "solutions", "what can you do"],
        "responses": ["We offer a wide range of services including:\n• Web Development\n• Mobile App Development\n• Cloud Solutions\n• AI/ML Services\n• Consulting Services\n\nWould you like to know more about any specific service?"]
    },
    "contact": {
        "patterns": ["contact", "phone", "email", "address", "location", "how to reach"],
        "responses": ["You can contact us through:\n• Email: contact@vasp.com\n• Phone: +1-234-567-8900\n• Address: 123 Tech Street, Innovation City\n• Website: www.vasp.com"]
    },
    "pricing": {
        "patterns": ["price", "cost", "pricing", "how much", "rates", "fees"],
        "responses": ["Our pricing varies based on your specific needs and project requirements. Please contact our sales team at sales@vasp.com for a customized quote, or schedule a consultation call."]
    },
    "support": {
        "patterns": ["help", "support", "assistance", "problem", "issue", "trouble"],
        "responses": ["I'm here to help! You can:\n• Ask me questions about our services\n• Contact our support team at support@vasp.com\n• Browse our help documentation\n• Schedule a support call\n\nWhat specific help do you need?"]
    },
    "thanks": {
        "patterns": ["thank", "thanks", "appreciate", "grateful"],
        "responses": ["You're welcome! Is there anything else I can help you with?", "Happy to help! Feel free to ask if you have more questions."]
    }
}

def find_best_response(user_input: str) -> str:
    """Find the best response based on user input using simple pattern matching"""
    user_input = user_input.lower()
    
    for category, data in KNOWLEDGE_BASE.items():
        for pattern in data["patterns"]:
            if pattern in user_input:
                import random
                return random.choice(data["responses"])
    
    # Default response if no pattern matches
    return "I understand you're looking for information. Could you please be more specific? You can ask me about our services, contact information, pricing, or any other questions about Vasp."

# Serve chatbot UI at /
@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8" />
        <title>Vasp Assistant</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
          * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
          }
          
          body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #f4f4f4;
            height: 100vh;
            overflow: hidden;
          }
          
          .chat-container {
            width: 100%;
            height: 100vh;
            background: #ffffff;
            display: flex;
            flex-direction: column;
            position: relative;
          }
          
          .chat-content {
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
          }
          
          .chat-messages {
            flex: 1;
            padding: 24px;
            overflow-y: auto;
            background: #ffffff;
          }
          
          .message-wrapper {
            margin-bottom: 24px;
            animation: fadeIn 0.3s ease-in;
          }
          
          .user-message-wrapper {
            margin-bottom: 24px;
            text-align: right;
            animation: fadeIn 0.3s ease-in;
          }
          
          .message-header {
            display: flex;
            align-items: center;
            margin-bottom: 12px;
          }
          
          .bot-avatar {
            width: 32px;
            height: 32px;
            border-radius: 0%;
            background: url("/assets/vasptech.png") no-repeat center center;
            background-size: cover;
            margin-right: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
          }
          
          .user-avatar {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background: linear-gradient(135deg, #34a853 0%, #137333 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            margin-left: 12px;
            position: relative;
          }
          
          .user-avatar::before {
            content: '👤';
            font-size: 16px;
            filter: brightness(0) invert(1);
          }
          
          .user-message-header {
            display: flex;
            align-items: center;
            justify-content: flex-end;
            margin-bottom: 12px;
          }
          
          .message-info {
            display: flex;
            align-items: center;
            gap: 8px;
          }
          
          .user-message-info {
            display: flex;
            align-items: center;
            gap: 8px;
            flex-direction: row-reverse;
          }
          
          .bot-name, .user-name {
            font-weight: 600;
            color: #161616;
            font-size: 14px;
          }
          
          .timestamp {
            color: #6f6f6f;
            font-size: 14px;
          }
          
          .message-content {
            color: #161616;
            font-size: 14px;
            line-height: 1.5;
            margin-bottom: 20px;
            white-space: pre-line;
          }
          
          .user-message-content {
            background: #e3f2fd;
            color: #161616;
            font-size: 14px;
            line-height: 1.5;
            padding: 12px 16px;
            border-radius: 18px;
            border-bottom-right-radius: 4px;
            display: inline-block;
            max-width: 80%;
            text-align: left;
          }
          
          .options-container {
            display: flex;
            flex-direction: column;
            gap: 8px;
            margin-top: 16px;
          }
          
          .option-button {
            background: #f4f4f4;
            border: 1px solid #e0e0e0;
            color: #161616;
            padding: 16px 20px;
            text-align: left;
            font-size: 14px;
            font-weight: 500;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: space-between;
            min-height: 52px;
          }
          
          .option-button:hover {
            background: #e8e8e8;
            border-color: #c6c6c6;
          }
          
          .option-button:active {
            background: #d4d4d4;
          }
          
          .option-icon {
            color: #0f62fe;
            font-size: 16px;
            margin-left: 8px;
          }

          .option-icon-img {
            width: 16px;
            height: 16px;
            object-fit: contain;
          }
          
          .external-link-icon {
            color: #0f62fe;
            font-size: 14px;
          }

          .external-link-icon-img {
            width: 16px;
            height: 16px;
            object-fit: contain;
          }
          
          .go-back-btn {
            background: #0f62fe;
            border: none;
            color: white;
            padding: 12px 24px;
            font-size: 14px;
            font-weight: 500;
            border-radius: 4px;
            cursor: pointer;
            margin-top: 12px;
            align-self: flex-start;
            transition: background-color 0.2s ease;
          }
          
          .go-back-btn:hover {
            background: #0353e9;
          }
          
          .suggestion-text {
            color: #525252;
            font-size: 14px;
            margin-top: 20px;
            margin-bottom: 16px;
          }
          
          .privacy-notice {
            background: #f4f4f4;
            border-top: 1px solid #e0e0e0;
            padding: 16px 24px;
            font-size: 12px;
            color: #525252;
            line-height: 1.4;
            position: relative;
          }
          
          .privacy-close {
            position: absolute;
            top: 0px;
            right: 0px;
            background: none;
            border: none;
            font-size: 16px;
            cursor: pointer;
            color: #525252;
            transition: transform 0.5s ease, background 0.5s ease;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
          }
          
          .privacy-close:hover {
            transform: scale(1.4); /* zoom in by 40% */
          }
          
          .privacy-link {
            color: #0f62fe;
            text-decoration: none;
          }
          
          .privacy-link:hover {
            text-decoration: underline;
          }
          
          .input-container {
            padding: 16px 24px;
            border-top: 1px solid #e0e0e0;
            background: #ffffff;
          }
          
          .input-wrapper {
            display: flex;
            align-items: center;
            background: #f4f4f4;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            padding: 0 16px;
          }
          
          .input-wrapper:focus-within {
            border-color: #0f62fe;
            box-shadow: 0 0 0 2px rgba(15, 98, 254, 0.1);
          }
          
          .message-input {
            flex: 1;
            border: none;
            background: none;
            padding: 16px 0;
            font-size: 14px;
            color: #161616;
            outline: none;
          }
          
          .message-input::placeholder {
            color: #a8a8a8;
          }
          
          .send-button {
            background: none;
            border: none;
            color: #0f62fe;
            font-size: 16px;
            cursor: pointer;
            padding: 8px;
            margin-left: 8px;
            border-radius: 4px;
            transition: background-color 0.2s ease;
          }
          
          .send-button:hover:not(:disabled) {
            background: rgba(15, 98, 254, 0.1);
          }
          
          .send-button:disabled {
            color: #c6c6c6;
            cursor: not-allowed;
          }
          
          .typing-indicator {
            padding: 12px 24px;
            font-style: italic;
            color: #666;
            font-size: 14px;
            display: none;
          }
          
          .typing-indicator.show {
            display: block;
          }
          
          .typing-dots::after {
            content: '';
            animation: dots 1.5s steps(4, end) infinite;
          }
          
          @keyframes dots {
            0%, 20% { content: ''; }
            40% { content: '.'; }
            60% { content: '..'; }
            80%, 100% { content: '...'; }
          }
          
          @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
          }
          
          .hidden {
            display: none;
          }
          
          @media (max-width: 768px) {
            .chat-messages {
              padding: 16px;
            }
            
            .privacy-notice {
              padding: 12px 16px 12px 16px;
            }
            
            .input-container {
              padding: 12px 16px;
            }
          }
        </style>
      </head>
      <body>
        <div class="chat-container">
          <div class="chat-content">
            <div class="chat-messages" id="chat-messages">
              <!-- Messages will be inserted here -->
            </div>
            
            <div class="typing-indicator" id="typing-indicator">
              <span class="typing-dots">vaspx is typing</span>
            </div>
            
            <div class="privacy-notice" id="privacy-notice">
              <button class="privacy-close" onclick="closePrivacyNotice()">×</button>
              By proceeding, you agree that Vasp can process
              <div>personal information about our conversation, including a text/transcript recording to allow us to respond to your inquiry. Please see <a href="#" class="privacy-link">Vasp's Privacy Statement</a> to learn about how Vasp processes personal information.
              </div>
            </div>
            
            <div class="input-container">
              <div class="input-wrapper">
                <input type="text" class="message-input" placeholder="Type something..." id="message-input" onkeypress="handleKeyPress(event)">
                <button class="send-button" onclick="sendMessage()" id="send-button">➤</button>
              </div>
            </div>
          </div>
        </div>

        <script>
          let currentStep = 'start';
          let conversationHistory = [];
          
          function getCurrentTime() {
            const now = new Date();
            return now.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
          }
          
          function addBotMessage(content, options = null, showGoBack = false) {
            const messagesContainer = document.getElementById('chat-messages');
            
            const messageWrapper = document.createElement('div');
            messageWrapper.className = 'message-wrapper';
            
            const messageHeader = document.createElement('div');
            messageHeader.className = 'message-header';
            
            const botAvatar = document.createElement('div');
            botAvatar.className = 'bot-avatar';
            
            const messageInfo = document.createElement('div');
            messageInfo.className = 'message-info';
            
            const botName = document.createElement('span');
            botName.className = 'bot-name';
            botName.textContent = 'vaspx';
            
            const timestamp = document.createElement('span');
            timestamp.className = 'timestamp';
            timestamp.textContent = getCurrentTime();
            
            messageInfo.appendChild(botName);
            messageInfo.appendChild(timestamp);
            messageHeader.appendChild(botAvatar);
            messageHeader.appendChild(messageInfo);
            
            const messageContent = document.createElement('div');
            messageContent.className = 'message-content';
            messageContent.textContent = content;
            
            messageWrapper.appendChild(messageHeader);
            messageWrapper.appendChild(messageContent);
            
            if (options && options.length > 0) {
              const optionsContainer = document.createElement('div');
              optionsContainer.className = 'options-container';
              
              options.forEach(option => {
                const button = document.createElement('button');
                button.className = 'option-button';
                
                const textSpan = document.createElement('span');
                textSpan.textContent = option.text;
                
                const iconSpan = document.createElement('span');

                if (option.url) {
                  iconSpan.className = 'external-link-icon';

                  const img = document.createElement('img');
                  img.src = 'assets/external-link.png';
                  img.alt = '↗';
                  img.className = 'option-icon-img';

                  iconSpan.appendChild(img);

                  button.onclick = () => window.open(option.url, '_blank');
                } else {
                  iconSpan.className = 'option-icon';

                  const img = document.createElement('img');
                  img.src = 'assets/right-arrow.png';
                  img.alt = '→';
                  img.className = 'option-icon-img';

                  iconSpan.appendChild(img);

                  button.onclick = () => handleOptionClick(option.value || option.text);
                }

                button.appendChild(textSpan);
                button.appendChild(iconSpan);
                optionsContainer.appendChild(button);
              });
              
              messageWrapper.appendChild(optionsContainer);
            }
            
            if (showGoBack) {
              const goBackBtn = document.createElement('button');
              goBackBtn.className = 'go-back-btn';
              goBackBtn.textContent = 'Go back';
              goBackBtn.onclick = () => handleOptionClick('start');
              messageWrapper.appendChild(goBackBtn);
            }
            
            messagesContainer.appendChild(messageWrapper);
            scrollToBottom();
          }
          
          function addUserMessage(content) {
            const messagesContainer = document.getElementById('chat-messages');
            
            const messageWrapper = document.createElement('div');
            messageWrapper.className = 'user-message-wrapper';
            
            const messageHeader = document.createElement('div');
            messageHeader.className = 'user-message-header';
            
            const userAvatar = document.createElement('div');
            userAvatar.className = 'user-avatar';
            
            const messageInfo = document.createElement('div');
            messageInfo.className = 'user-message-info';
            
            const userName = document.createElement('span');
            userName.className = 'user-name';
            userName.textContent = 'You';
            
            const timestamp = document.createElement('span');
            timestamp.className = 'timestamp';
            timestamp.textContent = getCurrentTime();
            
            messageInfo.appendChild(userAvatar);
            messageInfo.appendChild(userName);
            messageInfo.appendChild(timestamp);
            messageHeader.appendChild(messageInfo);
            
            const messageContent = document.createElement('div');
            messageContent.className = 'user-message-content';
            messageContent.textContent = content;
            
            messageWrapper.appendChild(messageHeader);
            messageWrapper.appendChild(messageContent);
            messagesContainer.appendChild(messageWrapper);
            scrollToBottom();
          }
          
          function showTypingIndicator() {
            document.getElementById('typing-indicator').classList.add('show');
            scrollToBottom();
          }
          
          function hideTypingIndicator() {
            document.getElementById('typing-indicator').classList.remove('show');
          }
          
          function scrollToBottom() {
            const messagesContainer = document.getElementById('chat-messages');
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
          }
          
          function handleOptionClick(value) {
            currentStep = value;
            loadChat(value);
          }
          
          function closePrivacyNotice() {
            document.getElementById('privacy-notice').style.display = 'none';
          }
          
          function handleKeyPress(event) {
            if (event.key === 'Enter') {
              sendMessage();
            }
          }
          
          function sendMessage() {
            const input = document.getElementById('message-input');
            const message = input.value.trim();
            if (message) {
              addUserMessage(message);
              input.value = '';
              
              // Add to conversation history
              conversationHistory.push({type: 'user', message: message});
              
              // Send to chatbot
              sendToChatbot(message);
            }
          }
          
          async function sendToChatbot(message) {
            showTypingIndicator();
            
            try {
              const url = window.location.origin + "/chat?user_input=" + encodeURIComponent(message);
              const response = await fetch(url);
              const data = await response.json();
              
              hideTypingIndicator();
              addBotMessage(data.message, data.options, data.showGoBack);
              
              // Add to conversation history
              conversationHistory.push({type: 'bot', message: data.message});
              
            } catch (error) {
              console.error('Error:', error);
              hideTypingIndicator();
              addBotMessage("❌ Sorry, there was an error. Please try again.");
            }
          }
          
          async function loadChat(userInput = null) {
            if (userInput && userInput !== 'start') {
              return sendToChatbot(userInput);
            }
            
            try {
              const url = window.location.origin + "/chat?user_input=" + encodeURIComponent(userInput || "");
              const response = await fetch(url);
              const data = await response.json();
              
              addBotMessage(data.message, data.options, data.showGoBack);
              
            } catch (error) {
              console.error('Error:', error);
              addBotMessage("❌ Sorry, there was an error. Please try again.");
            }
          }
          
          // Initialize chatbot when page loads
          document.addEventListener('DOMContentLoaded', function() {
            loadChat();
          });
        </script>
      </body>
    </html>
    """

# Chatbot API endpoint
@app.get("/chat")
def chat(user_input: str = None):
    """
    Main chatbot logic with custom training capability
    """
    
    if not user_input or user_input == "start":
        return {
            "message": "Welcome to the Vasp assistant. I'm here to connect you to the people and information at Vasp that you need.\n\nTo help you connect with the right team members, please let us know the type of help you need.",
            "options": [
                {"text": "Get community support", "value": "community_support"},
                {"text": "Get technical support", "value": "technical_support"}
            ],
            "showGoBack": False
        }
    
    elif user_input == "community_support":
        return {
            "message": "Welcome to the Vasp assistant. I'm here to connect you to the people and information at Vasp that you need.\n\nTo help you connect with the right team members, please let us know the type of help you need.",
            "options": [
                {"text": "I need support", "value": "need_support"},
                {"text": "I have a sales question", "value": "sales_question"},
                {"text": "I'm looking for something else", "url": "https://vasp.com/help"}
            ],
            "showGoBack": False
        }
    
    elif user_input == "technical_support":
        return {
            "message": "Welcome to the Vasp assistant. I'm here to connect you to the people and information at Vasp that you need.\n\nTo help you connect with the right team members, please let us know the type of help you need.",
            "options": [
                {"text": "I need support", "value": "need_support"},
                {"text": "I have a sales question", "value": "sales_question"},
                {"text": "I'm looking for something else", "url": "https://vasp.com/help"}
            ],
            "showGoBack": False
        }
    
    elif user_input == "need_support":
        return {
            "message": "I can help you get connected with our support team. What type of support do you need?",
            "options": [
                {"text": "Technical issues", "value": "technical_issues"},
                {"text": "Account problems", "value": "account_problems"},
                {"text": "Billing questions", "value": "billing_questions"},
                {"text": "Other support", "value": "other_support"}
            ],
            "showGoBack": True
        }
    
    elif user_input == "sales_question":
        return {
            "message": "I can connect you with our sales team to answer your questions about Vasp products and services.",
            "options": [
                {"text": "Product information", "value": "product_info"},
                {"text": "Pricing questions", "value": "pricing"},
                {"text": "Schedule a demo", "url": "https://calendly.com/vasp-demo"},
                {"text": "Contact sales", "url": "mailto:sales@vasp.com"}
            ],
            "showGoBack": True
        }
    
    # Handle custom queries using the knowledge base
    else:
        response = find_best_response(user_input)
        return {
            "message": response,
            "options": [
                {"text": "Ask another question", "value": "ask_more"},
                {"text": "Contact support", "url": "mailto:support@vasp.com"},
                {"text": "Go back to main menu", "value": "start"}
            ],
            "showGoBack": False
        }

# Training endpoint - Add new knowledge to the chatbot
@app.post("/train")
def train_chatbot(training_data: dict):
    """
    Train the chatbot with new Q&A pairs
    Expected format:
    {
        "category": "new_category",
        "patterns": ["pattern1", "pattern2"],
        "responses": ["response1", "response2"]
    }
    """
    try:
        category = training_data.get("category")
        patterns = training_data.get("patterns", [])
        responses = training_data.get("responses", [])
        
        if category and patterns and responses:
            KNOWLEDGE_BASE[category] = {
                "patterns": [p.lower() for p in patterns],
                "responses": responses
            }
            return {"status": "success", "message": f"Added training data for category: {category}"}
        else:
            return {"status": "error", "message": "Invalid training data format"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Get current knowledge base
@app.get("/knowledge")
def get_knowledge():
    """Get the current knowledge base"""
    return {"knowledge_base": KNOWLEDGE_BASE}

# Health check endpoint
@app.get("/health")
def health():
    return {"status": "healthy", "message": "Vasp Assistant is running!"}
