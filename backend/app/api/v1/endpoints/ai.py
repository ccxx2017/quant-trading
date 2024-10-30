# app/api/v1/endpoints/ai.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.ai_service import AIService

router = APIRouter()
ai_service = AIService()

@router.websocket("/ws/analyze")
async def analyze_market_ws(websocket: WebSocket):
    try:
        await websocket.accept()
        test_data = "平安银行(000001.SZ)是一家深圳的银行类上市公司，于1991年上市。"
        await ai_service.analyze_market_stream(test_data, websocket)
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        print(f"Error in websocket: {str(e)}")
        if websocket.client_state.CONNECTED:
            await websocket.send_text(f"Error: {str(e)}")