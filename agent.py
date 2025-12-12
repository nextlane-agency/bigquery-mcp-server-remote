# agent.py
# This module configures the LLM agent and the Model Context Protocol (MCP) toolset.
# It sets up the connection to the local 'toolbox' binary which acts as the MCP server.
import os
from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

from constants import PROJECT_ID, MODEL_NAME

# Define paths for the toolbox binary and the tools configuration file.
BASE_DIR = Path(__file__).resolve().parent
TOOLBOX_PATH = str(BASE_DIR / "toolbox")
TOOLS_FILE = str(BASE_DIR / "tools.yaml")

# Debug print to verify paths
print(f"Toolbox Path: {TOOLBOX_PATH}")
print(f"Tools File: {TOOLS_FILE}")

# Initialize the MCP Toolset.
# This connects to the 'toolbox' binary using Stdio.
# It passes the tools.yaml file and necessary environment variables (like GOOGLE_CLOUD_PROJECT).

mcp_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=TOOLBOX_PATH,
            args=[
                "--stdio",
                "--tools-file",
                TOOLS_FILE,
            ],
            env={
                **os.environ,
                "GOOGLE_CLOUD_PROJECT": PROJECT_ID,
            },
        ),
        timeout=120.0,
    ),
    # expose all tools from tools.yaml
)

# Define the Root Agent.
# This agent uses the Gemini model and is equipped with the MCP toolset.
# The instruction guides the agent on how to use the tools and format the output (including SQL).
root_agent = LlmAgent(
    model=MODEL_NAME,
    name="bigquery_ca_agent",
    instruction=(
        "You are a data analysis assistant for BigQuery.\n"
        "You can use the following MCP tools:\n"
        "- ask_data_insights (conversational analytics over configured tables)\n"
        "- get_table_info (inspect schemas)\n"
        "- get_dataset_info (inspect datasets)\n"
        "- execute_sql (run SQL directly when needed)\n\n"
        "When answering a question that involves querying BigQuery, you MUST:\n"
        "1) First provide a clear natural-language answer for the user.\n"
        "2) At the very end of your response, add:\n"
        "   SQL used:\n"
        "   ```sql\n"
        "   <the exact SQL query or queries you executed>\n"
        "   ```\n"
        "If no SQL was executed, explicitly write: SQL used: none.\n"
        "If multiple queries were used, include all of them in the same sql block.\n"
    ),
    tools=[mcp_toolset],
)