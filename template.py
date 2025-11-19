import os
from pathlib import Path

import logging

# Basic logging configuration for the project
logging.basicConfig(level=logging.INFO, format='[%(asctime)s]: %(message)s:')

# Project name
project_name = "AI_Job_Assistant"

# List of all files and folders to be created for the project structure
list_of_files = [
    ".env",
    "api/requirements.txt",
    "api/main.py",
    "api/agent_logic.py",       # This file will contain the complete agent workflow
    "api/tools.py",             # This file will contain tools for web search and sending emails
    "api/utils.py",             # This file will contain helper functions such as reading resumes
    "api/pydantic_models.py",   # This file will contain data models for the API
    "app/requirements.txt",
    "app/streamlit_app.py",
    "uploads/"                  # This folder will temporarily store user resumes
]

# Loop through the list and create files and folders as needed
for filepath in list_of_files:
    filepath = Path(filepath)
    filedir, filename = os.path.split(filepath)

    # Create the directory if it does not exist
    if filedir != "":
        os.makedirs(filedir, exist_ok=True)
        logging.info(f"Creating directory: {filedir} for file: {filename}")

    # Create the file if it does not exist or is empty
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        with open(filepath, 'w') as f:
            pass  # Create an empty file
            logging.info(f"Creating empty file: {filepath}")
    else:
        logging.info(f"{filename} already exists")
