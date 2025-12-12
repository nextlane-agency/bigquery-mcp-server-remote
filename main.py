# main.py
# This is the main entry point for the FastAPI application.
# It handles HTTP requests, manages user sessions, and invokes the agent runner.
import os
import re

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.adk.errors.already_exists_error import AlreadyExistsError

from agent import root_agent
from constants import PROJECT_ID, LOCATION, APP_NAME, TABLES

load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Initialize Session Service (InMemory for simplicity) and the Agent Runner.
# The Runner coordinates the interaction between the user, the agent, and the tools.
session_service = InMemorySessionService()
runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service,
)

class QueryRequest(BaseModel):
    """Request model for the /query endpoint."""
    question: str
    user_id: str = "user1234"
    session_id: str = "default-session"


class QueryResponse(BaseModel):
    """Response model for the /query endpoint."""
    answer: str
    sql: str | None = None

async def _ensure_session(app_name: str, user_id: str, session_id: str):
    """
    Ensures that a session exists for the given user and session ID.
    Creates a new session if one does not exist.
    """
    try:
        await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
    )
    except AlreadyExistsError:
        # Session already exists, which is fine.
        pass


@app.post("/query", response_model=QueryResponse)
async def query_bigquery(body: QueryRequest):
    """
    Endpoint to process user queries.
    It constructs a context-aware prompt with available tables and delegates to the agent.
    """
    # Ensure a session exists for this conversation
    await _ensure_session(APP_NAME, body.user_id, body.session_id)

    # Build table list from constants.TABLES
    table_lines = []
    for idx, t in enumerate(TABLES, start=1):
        fq = f"{PROJECT_ID}.{t['dataset']}.{t['table']}"
        table_lines.append(f"  {idx}. {fq}")
    tables_block = "\n".join(table_lines)

    # Construct the user query with context about available tables and instructions.
    user_query = (
        f"User question: {body.question}\n\n"
        f"Project ID: {PROJECT_ID}\n"
        f"Location: {LOCATION}\n"
        f"Available BigQuery tables (fixed for this app):\n"
        f"{tables_block}\n\n"
        "Use the ask_data_insights tool to analyze these tables as needed.\n"
        "You may also use get_table_info, get_dataset_info, or execute_sql\n"
        "for schema inspection or precise SQL queries.\n"
        "When calling ask_data_insights, construct the 'table_references'\n"
        "argument from the above list of tables."
    )

    content = types.Content(
        role="user",
        parts=[types.Part(text=user_query)],
    )

    # Run the agent asynchronously
    events = runner.run_async(
        user_id=body.user_id,
        session_id=body.session_id,
        new_message=content,
    )

    final_text = ""

    # Process the stream of events to get the final text response
    async for event in events:
        if event.is_final_response():
            if event.content and event.content.parts:
                part = event.content.parts[0]
                if getattr(part, "text", None):
                    final_text = part.text
    
    # Extract the SQL query from the response if present (looking for ```sql blocks)
    # This allows the UI to display the generated SQL separately.
    sql_query = None
    if final_text:
        blocks = re.findall(r"```sql(.*?)```", final_text, flags=re.DOTALL | re.IGNORECASE)
        if blocks:
            sql_query = blocks[-1].strip()

    return QueryResponse(
        answer=final_text or "[no response from agent]",
        sql=sql_query,
    )
