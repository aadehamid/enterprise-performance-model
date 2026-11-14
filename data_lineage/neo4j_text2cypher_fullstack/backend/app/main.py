import os

import uvicorn

from app.config import (
    NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE,
    LLM_PROVIDER, LLM_MODEL, LLM_TEMPERATURE,
    OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_PROJECT, GOOGLE_LOCATION,
    ALLOWED_ORIGINS,
)
from app.database import Neo4jDriver, MessageHistory
from app.generation import LLM, Agent
from app.api import API, Routes

driver = Neo4jDriver.get_instance(
    uri=NEO4J_URI, username=NEO4J_USERNAME, password=NEO4J_PASSWORD
).driver

llm = LLM.get_instance(
    provider=LLM_PROVIDER,
    model=LLM_MODEL,
    temperature=LLM_TEMPERATURE,
    openai_key=OPENAI_API_KEY,
    anthropic_key=ANTHROPIC_API_KEY,
    project=GOOGLE_PROJECT,
    location=GOOGLE_LOCATION,
).llm

message_history = MessageHistory(driver=driver, database=NEO4J_DATABASE)
agent = Agent(driver=driver, llm=llm, archive=message_history, database=NEO4J_DATABASE, retry=2)

app = API.get_instance(allowed_origins=ALLOWED_ORIGINS).app
Routes(app=app, agent=agent, message_history=message_history,
       allowed_origins=ALLOWED_ORIGINS)


@app.on_event("shutdown")
def _shutdown():
    driver.close()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
