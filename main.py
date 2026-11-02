
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="AI Business Agent",
    description="WhatsApp AI Customer Support Platform",
    version="1.0.0"
)

@app.get("/")
async def home():
    return {
        "status": "online",
        "app": "AI Business Agent",
        "message": "Сервер фаъол аст!"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

class BusinessInfo(BaseModel):
    business_name: str
    category: str
    language: str = "both"
    description: str = ""

class ChatMessage(BaseModel):
    message: str
    business: BusinessInfo

@app.post("/api/test")
async def test_agent(data: ChatMessage):
    prompt = f"""
    Ту ёрдамчии зеҳнии бизнес ҳастӣ.
    Номи бизнес: {data.business.business_name}
    Соҳа: {data.business.category}
    Маълумот: {data.business.description}
    Забон: тоҷикӣ ва русӣ.

    Ба мизоҷ боодобона, кӯтоҳ ва фаҳмо ҷавоб деҳ.
    Агар маълумот кофӣ набошад, чизеро ихтироъ накун.
    Саволро барои оператор қайд кун.

    Паёми мизоҷ:
    {data.message}
    """

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return {
            "status": "demo",
            "reply": "Салом! Мо паёми шуморо гирифтем. Лутфан каме интизор шавед."
        }

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt
        )

        return {
            "status": "success",
            "reply": response.output_text
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="AI error: " + str(error)
        )

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    data = await request.json()
    print("WhatsApp webhook:", data)
    return {"status": "received"}

@app.get("/webhook/whatsapp")
async def verify_whatsapp_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN", "")

    if mode == "subscribe" and token == verify_token and challenge:
        return int(challenge)

    raise HTTPException(status_code=403, detail="Verification failed")
