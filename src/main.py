
from fastapi import FastAPI
import uvicorn

from api.endpoints import router
app = FastAPI(title="API Список дел")

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
