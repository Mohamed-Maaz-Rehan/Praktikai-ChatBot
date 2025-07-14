import os
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import openai

# Load environment variables from .env file
load_dotenv()

# Set Azure OpenAI credentials
openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_version = "2023-12-01-preview"
openai.api_key = os.getenv("AZURE_OPENAI_KEY")
deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# Load system prompt and startup message
with open("system_prompt.txt", "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

with open("startup_message.txt", "r", encoding="utf-8") as f:
    STARTUP_MESSAGE = f.read()

# Define FastAPI app
app = FastAPI()

# Define request and response models
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

# Define chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": request.message}
    ]
    try:
        response = openai.ChatCompletion.create(
            engine=deployment_name,
            messages=messages,
            temperature=0.7
        )
        reply = response.choices[0].message["content"]
    except Exception as e:
        reply = f"Error generating response: {str(e)}"

    return JSONResponse(content={"response": reply})

from fastapi import Form
from fastapi.responses import HTMLResponse

@app.get("/", response_class=HTMLResponse)
async def get_chat_form():
    with open("startup_message.txt", "r", encoding="utf-8") as f:
        startup_message = f.read()

    return f"""
    <html>
        <head><title>Chatbot</title></head>
        <body>
            <h2>{startup_message}</h2>
            <form action="/chat-ui" method="post">
                <input type="text" name="message" placeholder="Type your message here" required />
                <input type="submit" value="Send" />
            </form>
        </body>
    </html>
    """

@app.post("/chat-ui", response_class=HTMLResponse)
async def chat_ui(message: str = Form(...)):
    with open("system_prompt.txt", "r", encoding="utf-8") as f:
        system_prompt = f.read()

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message}
    ]
    try:
        response = openai.ChatCompletion.create(
            engine=deployment_name,
            messages=messages,
            temperature=0.7
        )
        reply = response.choices[0].message["content"]
    except Exception as e:
        reply = f"Error generating response: {str(e)}"

    with open("startup_message.txt", "r", encoding="utf-8") as f:
        startup_message = f.read()

    return f"""
    <html>
        <head><title>Chatbot</title></head>
        <body>
            <h2>{startup_message}</h2>
            <form action="/chat-ui" method="post">
                <input type="text" name="message" value="{message}" required />
                <input type="submit" value="Send" />
            </form>
            <hr>
            <p><strong>You:</strong> {message}</p>
            <p><strong>Bot:</strong> {reply}</p>
        </body>
    </html>
    """
