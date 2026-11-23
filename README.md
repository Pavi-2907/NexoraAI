# NexoraAI

NexoraAI is an AI-powered assistant built using Python, FastAPI, and Groq. It provides conversational responses to user questions and uses web search when current or recently updated information is required.

## Current Features

- AI-powered question answering
- General knowledge and technical explanations
- Intelligent web-search requirement classification
- Conditional web search using Groq Browser Search
- Source URL extraction
- Structured API responses

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| FastAPI | Backend API framework |
| Groq | LLM API integration |
| Groq Browser Search | Retrieving current information |
| Uvicorn | ASGI server |
| python-dotenv | Environment variable management |

## Project Structure

```text
NexoraAI/
├── app/
│   ├── endpoints/
│   │   └── text.py
│   ├── routers/
│   │   └── routes.py
│   ├── services/
│   │   └── llm_service.py
│   ├── .gitignore
│   ├── main.py
│   └── requirements.txt
├── planning.md
└── README.md
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone <your-github-repository-url>
cd NexoraAI/app
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

### 3. Activate the Virtual Environment

**Windows PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file in the application directory:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b
```

Replace `your_groq_api_key` with your actual Groq API key.

## Running the Application

Start the FastAPI application using Uvicorn:

```bash
uvicorn main:app --reload
```

Once the server starts, the application will be available at:

- **API Base URL:** http://127.0.0.1:8000
- **Interactive API Documentation:** http://127.0.0.1:8000/docs

The `--reload` option automatically restarts the development server when code changes are detected.

## Project Status

Currently in progress. New features and improvements are being developed.
