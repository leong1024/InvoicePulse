from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.drift_status import router as drift_router


app = FastAPI(title="InvoicePulse API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(drift_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
