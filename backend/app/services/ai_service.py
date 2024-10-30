# app/services/ai_service.py
from openai import OpenAI
from fastapi import WebSocket
from app.core.config import settings

class AIService:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.ZHIPU_API_KEY,
            base_url="https://api.lingyiwanwu.com/v1"
        )
    
    async def analyze_market_stream(self, market_data: str, websocket: WebSocket):
        try:
            stream = self.client.chat.completions.create(
                model="yi-large",
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的金融分析师，请对给定的市场数据进行分析。"
                    },
                    {
                        "role": "user",
                        "content": f"请分析以下股票数据：{market_data}"
                    }
                ],
                temperature=0.3,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    await websocket.send_text(chunk.choices[0].delta.content)
                    
        except Exception as e:
            await websocket.send_json({"status": "error", "message": str(e)})