from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import httpx
from typing import Dict
import os
from dotenv import load_dotenv

app = FastAPI()

load_dotenv()

# --- Configuration ---
# Mount the assets directory to serve images like your logo
if os.path.exists("assets"):
    app.mount("/assets", StaticFiles(directory="assets"), name="assets")

# URL for your running Rasa server
RASA_SERVER_URL = f"{os.getenv('RASA_SERVER_URL')}/webhooks/rest/webhook"

# Allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Frontend UI ---
@app.get("/", response_class=HTMLResponse)
def home():
    # The HTML and CSS are identical to your original code to preserve the design.
    # The JavaScript has been modified for Rasa integration.
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
              </div>
            
            <div class="typing-indicator" id="typing-indicator">
              <span class="typing-dots">vaspx is typing</span>
            </div>
            
            <div class="privacy-notice" id="privacy-notice">
              <button class="privacy-close" onclick="closePrivacyNotice()">×</button>
              By proceeding, you agree that Vasp can process
              <div>personal information about our conversation, including a text/transcript recording to allow us to respond to your inquiry. Please see <a href="https://www.vasptechnologies.com/privacy-policy" target="_blank" class="privacy-link">Vasp's Privacy Statement</a> to learn about how Vasp processes personal information.
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
          // Unique session ID for the user's conversation with Rasa
          const sessionId = 'user_' + Date.now();
          
          function getCurrentTime() {
            const now = new Date();
            return now.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
          }
          
          // Renders a message from the bot
          function addBotMessage(content) {
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

            // Convert **text** to <strong>text</strong>
            const formattedContent = content.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
            messageContent.innerHTML = formattedContent;

            messageWrapper.appendChild(messageHeader);
            messageWrapper.appendChild(messageContent);

            messagesContainer.appendChild(messageWrapper);
            scrollToBottom();
          }
          
          // Renders a message from the user
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
          
          function closePrivacyNotice() {
            document.getElementById('privacy-notice').style.display = 'none';
          }
          
          function handleKeyPress(event) {
            if (event.key === 'Enter') {
              sendMessage();
            }
          }
          
          // Called when the user clicks the send button or presses Enter
          function sendMessage() {
            const input = document.getElementById('message-input');
            const message = input.value.trim();
            if (message) {
              addUserMessage(message);
              input.value = '';
              sendToChatbot(message);
            }
          }
          
          // Sends the user's message to the backend and displays the bot's response
          async function sendToChatbot(message) {
            showTypingIndicator();
            
            try {
              const response = await fetch('/chat', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ message: message, sender: sessionId })
              });

              if (!response.ok) {
                  throw new Error(`HTTP Error: ${response.status}`);
              }
              
              const data = await response.json();
              
              hideTypingIndicator();

              if (data.responses && data.responses.length > 0) {
                  // Combine all text parts from Rasa into a single string with newlines
                  const combinedText = data.responses
                      .map(resp => resp.text)
                      .filter(text => text) // Removes any empty responses
                      .join('\\n\\n'); // Joins messages with a paragraph break

                  // Display the single combined message
                  if (combinedText) {
                      addBotMessage(combinedText);
                  }
              } else {
                  addBotMessage("I'm sorry, I didn't get a response. Please try again.");
              }
              
            } catch (error) {
              console.error('Error:', error);
              hideTypingIndicator();
              addBotMessage("❌ Sorry, I'm having trouble connecting. Please ensure the server is running and try again.");
            }
          }
          
          // Initialize chatbot with a hardcoded welcome message on page load
          document.addEventListener('DOMContentLoaded', function() {
            const welcomeMessage = "Hi, I am VaspX, an assistant of Vasp Technologies, how can I assist you today?";
            addBotMessage(welcomeMessage);
          });
        </script>
      </body>
    </html>
    """


# --- Backend API ---
@app.post("/chat")
async def chat(request: Dict):
    """
    This endpoint receives a message from the frontend, forwards it to the
    Rasa server, and returns Rasa's response.
    """
    try:
        user_message = request.get("message", "")
        sender_id = request.get("sender", "default")
        
        # Payload for the Rasa server
        rasa_payload = {
            "sender": sender_id,
            "message": user_message
        }
        
        # Send the message to the Rasa server and get the response
        async with httpx.AsyncClient() as client:
            rasa_response = await client.post(
                RASA_SERVER_URL,
                json=rasa_payload,
                timeout=30.0
            )
            rasa_response.raise_for_status() # Raise an exception for bad status codes
            
            bot_responses = rasa_response.json()
            return {"responses": bot_responses}
            
    except httpx.RequestError as e:
        print(f"Error connecting to Rasa: {e}")
        return {
            "responses": [{
                "text": f"Error: Could not connect to the Rasa server at {RASA_SERVER_URL}. Please check if it's running."
            }]
        }
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {
            "responses": [{
                "text": "An unexpected error occurred on the server. Please check the logs."
            }]
        }

# Health check endpoint
@app.get("/health")
def health():
    return {"status": "healthy", "message": "Vasp Assistant is running!"}
