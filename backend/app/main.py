from fastapi import FastAPI

app = FastAPI(title="AI Crypto Advisor")


@app.get("/")
def health_check():
    return {"status": "ok"}
