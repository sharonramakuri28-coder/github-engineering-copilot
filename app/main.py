from fastapi import FastAPI
from app.routers import auth, repos

app = FastAPI(
    title="GitHub Engineering Copilot",
    description="AI-powered GitHub repository analysis platform",
    version="1.0.0"
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(repos.router, prefix="/repos", tags=["Repositories"])

@app.get("/")
def root():
    return {"message": "GitHub Engineering Copilot is running"}