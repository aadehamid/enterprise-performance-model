import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import Routes
from app.database import MessageHistory
from app.generation import Agent

REFERER = {"referer": "http://localhost:5173/"}


@pytest.fixture
def make_client(tmp_path):
    def build(llm, graph):
        history = MessageHistory(driver=graph, db_path=str(tmp_path / "history.db"))
        agent = Agent(graph, llm, archive=history)
        app = FastAPI()
        Routes(app=app, agent=agent, message_history=history, allowed_origins=["http://localhost:5173"])
        return TestClient(app)

    return build
