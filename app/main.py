from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from app.chatbot import ask_chatbot
from app.rag import extract_text_from_url, ask_gemini
from fastapi.staticfiles import StaticFiles

app = FastAPI()

templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Landing page
@app.get("/", response_class=HTMLResponse)
async def landing(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Options page with chatbot and rag choice
@app.get("/options", response_class=HTMLResponse)
async def options(request: Request):
    return templates.TemplateResponse("options.html", {"request": request})

# Chatbot page
@app.get("/chatbot", response_class=HTMLResponse)
async def chatbot_page(request: Request):
    return templates.TemplateResponse("chatbot.html", {"request": request})

# Chatbot API endpoint to handle user messages
@app.post("/chatbot/api")
async def chatbot_api(message: str = Form(...)):
    response = ask_chatbot(message)
    return JSONResponse({"response": response})

# RAG page
@app.get("/rag", response_class=HTMLResponse)
async def rag_page(request: Request):
    return templates.TemplateResponse("rag.html", {"request": request})

# RAG API endpoints
@app.post("/rag/api/extract")
async def rag_extract(url: str = Form(...)):
    content = extract_text_from_url(url)
    return JSONResponse({"content": content})

@app.post("/rag/api/ask")
async def rag_ask(question: str = Form(...), context: str = Form(...)):
    answer = ask_gemini(question, context)
    return JSONResponse({"answer": answer})
