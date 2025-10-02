# Real Estate Multi-Agent System 🏡

A multi-agent real estate platform with specialized agents for buyers, sellers, price estimation, and neighborhood analysis.

## Project Structure

```
Real_Estate_Agent/
├── .env
├── requirements.txt
├── streamlit.py
├── agents/
│   ├── buyer_agent/
│   │   ├── __main__.py
│   │   ├── agent.py
│   │   └── task_manager.py
│   ├── seller_agent/
│   │   ├── __main__.py
│   │   ├── agent.py
│   │   └── task_manager.py
│   ├── price_agent/
│   │   ├── __main__.py
│   │   ├── agent.py
│   │   └── task_manager.py
│   ├── neighborhood_agent/
│   │   ├── __main__.py
│   │   ├── agent.py
│   │   └── task_manager.py
│   └── host_agent/
│       ├── __main__.py
│       ├── agent.py
│       └── task_manager.py
├── common/
│   ├── a2a_client.py
│   └── a2a_server.py
└── shared/
    └── schema.py
```

## Required Dependencies

Install all packages from `requirements.txt`:

```bash
pip install -r requirements.txt
```

**Package List:**
- `google-adk`
- `litellm`
- `fastapi`
- `uvicorn`
- `httpx`
- `pydantic`
- `openai`
- `streamlit`
- `requests`

## Environment Configuration

Create `.env` file in project root:

```
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=your_api_key_here
```

## Running in VS Code

### Method 1: Using VS Code Terminals

1. Open project in VS Code
2. Open 5 integrated terminals (`Terminal > New Terminal`)
3. Run each command in separate terminals:

```bash
# Terminal 1
python -m agents.buyer_agent

# Terminal 2  
python -m agents.seller_agent

# Terminal 3
python -m agents.price_agent

# Terminal 4
python -m agents.neighborhood_agent

# Terminal 5
streamlit run streamlit.py
```

### Method 2: Using VS Code Tasks

Create `.vscode/tasks.json`:

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Start All Agents",
            "type": "shell",
            "command": "python",
            "args": ["-m", "agents.buyer_agent"],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "panel": "new"
            }
        }
    ]
}
```

### Access Application
- Open browser to `http://localhost:8501`
- Use VS Code's built-in browser: `Ctrl+Shift+P` → "Simple Browser"