# GitHub Engineering Copilot

An AI-powered backend application built with FastAPI that analyzes GitHub repositories, pull requests, and issues.

## Features

- JWT Authentication
- GitHub Repository Analysis
- Pull Request Listing
- AI-assisted Pull Request Summary
- Issue Analysis
- Interactive Swagger API Documentation

## Tech Stack

- Python
- FastAPI
- GitHub REST API
- JWT Authentication
- Pydantic
- Requests

## API Endpoints

### Authentication
- POST `/auth/login`

### Repository
- GET `/repos/{owner}/{repo}`

### Pull Requests
- GET `/repos/{owner}/{repo}/pulls`
- GET `/repos/{owner}/{repo}/pulls/{pr_number}/summary`

### Issues
- POST `/repos/{owner}/{repo}/issues/analyze`

## Run Locally

```bash
git clone https://github.com/sharonramakuri28-coder/github-engineering-copilot.git
cd github-engineering-copilot

python -m venv venv

# Windows
venv\Scripts\activate

pip install -r requirements.txt

python -m uvicorn app.main:app --reload
```

Open:

```
http://127.0.0.1:8000/docs
```

to access the interactive Swagger UI.

## Project Structure

```
app/
├── auth.py
├── ai_client.py
├── github_client.py
├── main.py
└── routers/
    ├── auth.py
    └── repos.py
```

## Future Improvements

- Claude API integration
- PostgreSQL database
- Docker support
- GitHub Actions CI
- Unit test coverage
