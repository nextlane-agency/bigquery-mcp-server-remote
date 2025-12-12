# constants.py
# This file contains configuration constants for the application.
# Centralizing these values makes it easier to manage environment-specific settings.

# GCP + BigQuery config
# TODO: Update PROJECT_ID with your actual Google Cloud Project ID (linked to billing)
PROJECT_ID = "project_id"
LOCATION = "us-central1"

# ADK / Agent config
APP_NAME = "bigquery_conversational_app"
MODEL_NAME = "gemini-2.0-flash"

# Fixed list of tables for your app (edit this only)
# Each element is a dict with dataset + table.
# This list is used to inform the agent about which tables it can query.
TABLES = [
    {
        "dataset": "ADKPractice",
        "table": "bbc_news_fulltext",
    },
    {
        "dataset": "ADKPractice",
        "table": "school_location",
    },
    # add more here:
    # {"dataset": "other_dataset", "table": "other_table"},
]
