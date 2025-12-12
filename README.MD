# BigQuery MCP Server - Local Run

This project implements a Model Context Protocol (MCP) server for BigQuery, allowing for conversational analytics and schema inspection. It uses the Google Gen AI Toolbox, the **ADK Framework**, and a FastAPI application to serve the agent.

## Prerequisites

- **Python 3.10+**: Ensure Python is installed.
- **Google Cloud Project**: You need a GCP project with BigQuery enabled.
- **Unix-based OS**: macOS or Linux (for the toolbox binary).


## Installation

1.  **Clone the repository**:
    Clone this repository into your working directory:
    ```bash
    git clone <your-repo-url>
    cd BigqueryMCP
    ```

2.  **Download the Gen AI Toolbox**:
    This is also know as MCP Toolbox for Databases. Run the following commands to download the appropriate binary for your OS.

    **For macOS (Apple Silicon/M1/M2/M3):**
    ```bash
    export VERSION=v0.22.0
    export OS="darwin/arm64"
    curl -o toolbox "https://storage.googleapis.com/genai-toolbox/$VERSION/$OS/toolbox"
    chmod +x toolbox
    ```

    **For macOS (Intel):**
    ```bash
    export VERSION=v0.22.0
    export OS="darwin/amd64"
    curl -o toolbox "https://storage.googleapis.com/genai-toolbox/$VERSION/$OS/toolbox"
    chmod +x toolbox
    ```

    **For Linux:**
    ```bash
    export VERSION=v0.22.0
    export OS="linux/amd64"
    curl -o toolbox "https://storage.googleapis.com/genai-toolbox/$VERSION/$OS/toolbox"
    chmod +x toolbox
    ```

    **For Windows:**
    ```bash
    export VERSION=v0.22.0
    export OS="windows/amd64"
    curl -o toolbox.exe "https://storage.googleapis.com/genai-toolbox/$VERSION/$OS/toolbox.exe"
    ```


    **Verify installation:**
    ```bash
    ./toolbox --version
    ```

3.  **Install Python Dependencies**:
    It is recommended to use a virtual environment.
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

## Configuration

1.  **Environment Variables**:
    *   Copy the example environment file to a new file named `.env`:
        ```bash
        cp .env_example .env
        ```
    *   Open `.env` and provide a valid `GOOGLE_API_KEY`.

        ```
2.  **App Configuration (`constants.py`)**:
    Open `constants.py` and update the following:
    *   **`PROJECT_ID`**: Replace `"project_id"` with your actual Google Cloud Project ID (the one linked to your billing account).
    *   **`LOCATION`**: Ensure this matches your BigQuery dataset location (e.g., `"us-central1"`).
    *   **`TABLES`**: Update the list of tables with your specific `dataset` and `table` names.

3.  **Tools Configuration (`tools.yaml`)**:
    Open `tools.yaml` and update the `PROJECT_ID` and `LOCATION` fields to match your configuration in `constants.py`.
    *   `PROJECT_ID`: Your Google Cloud Project ID.
    *   `LOCATION`: Your BigQuery location.

## Usage

1.  **Run the FastAPI Application**:
    Start the server using `uvicorn`.
    ```bash
    uvicorn main:app --reload
    ```

2.  **Access the API**:
    The API will be available at `http://127.0.0.1:8000`.
    - **POST /query**: Send a natural language question to analyze your BigQuery data.

    **Example Request:**
    ```json
    {
      "question": "Give me 10 different zip codes randomly.",
      "user_id": "test_user",
      "session_id": "test_session"
    }
    ```

    **Example Response:**
    ```json
    {
      "answer": "Here are 10 random zip codes from the `school_location` table: 13210-1687, 40422-1394, 85283, 04106-1698, 46805, 90301-2904, 76904, 52803-2898, 33033-1412, 77477-0000\\n\\nSQL used:\\n```sql\\nSELECT DISTINCT zip FROM `long-arcadia-475313-s8.ADKPractice.school_location` ORDER BY RAND() LIMIT 10\\n```",
      "sql": "SELECT DISTINCT zip FROM `long-arcadia-475313-s8.ADKPractice.school_location` ORDER BY RAND() LIMIT 10"
    }
    ```

## Project Structure

- `main.py`: The FastAPI application entry point and endpoint definitions.
- `agent.py`: Configuration of the LLM agent and MCP toolset.
- `constants.py`: Project constants like Project ID, Location, and Table definitions.
- `tools.yaml`: Definition of BigQuery MCP tools (Data Insights, Table Info, etc.).
- `toolbox`: The binary executable for the Gen AI Toolbox (must be downloaded).
