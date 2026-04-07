# -*- coding: utf-8 -*-
from fastapi import FastAPI
from datetime import datetime
import random

app = FastAPI(title="能源化工新闻分析系统", version="1.0.0")

@app.get("/health")
def health_check():
    return {"status": "healthy", "time": datetime.now().isoformat()}

@app.get("/api/v1/visualization/dashboard")
def dashboard():
    return {
        "timestamp": datetime.now().isoformat(),
        "score_cards": [
            {"commodity": "WTI", "score": 72.5, "rating": "看涨", "signal": "买入"},
            {"commodity": "Brent", "score": 68.3, "rating": "看涨", "signal": "持有"},
            {"commodity": "HH", "score": 55.2, "rating": "中性", "signal": "持有"},
        ],
        "recent_alerts": [
            {"id": "1", "level": "red", "message": "WTI地缘风险上升", "commodity": "WTI"},
        ],
        "top_news": [
            {"id": "1", "title": "OPEC+延长减产协议", "source": "Reuters"},
        ],
        "market_overview": {"total_news_24h": 156, "active_alerts": 8}
    }

if __name__ == "__main__":
    import uvicorn
    print("服务启动中，访问 http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
