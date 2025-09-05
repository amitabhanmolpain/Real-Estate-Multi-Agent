from fastapi import FastAPI

def create_app(agent=None):
    app = FastAPI()

    @app.get("/")
    def root():
        return {"message": "Hello from the agent server"}

    if agent:
        app.state.agent = agent

    return app
