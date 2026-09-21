from fastapi import FastAPI

app = FastAPI(
    title="Taama Claim Checker",
    description="Deterministic Australia claim compliance checker.",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "name": "Taama Claim Checker",
        "status": "running",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}