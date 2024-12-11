from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from model import QAModel

app = FastAPI()
model = QAModel()

@app.post("/stream")
async def stream(request: Request):
    data = await request.json()
    question = data.get("question", "Нет вопроса")
    history = data.get("history", [])  # Получаем историю из запроса

    return StreamingResponse(
        model(question, history=history),
        media_type="text/plain",
        headers={
            "X-Accel-Buffering": "no",
            "Cache-Control": "no-cache",
            "Content-Type": "text/event-stream"
        }
    )
