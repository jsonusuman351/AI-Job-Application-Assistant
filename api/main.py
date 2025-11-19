import os
import uuid
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

# Load environment variables at the very beginning
load_dotenv()

from pydantic_models import StartRequest, UserFeedbackRequest
from agent_logic import agent_runnable, read_resume_file

app = FastAPI()

# Configure CORS to allow frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

UPLOADS_DIR = "uploads"
os.makedirs(UPLOADS_DIR, exist_ok=True)

@app.post("/start")
async def start_conversation(
    resume: UploadFile = File(...), 
    job_description: str = Form(...)
):
    """
    Endpoint to start a new job application process.
    It saves the resume, creates a new session, and starts the agent.
    """
    session_id = str(uuid.uuid4())
    
    # Save the uploaded resume
    resume_path = os.path.join(UPLOADS_DIR, f"{session_id}_{resume.filename}")
    with open(resume_path, "wb") as buffer:
        buffer.write(await resume.read())

    # Read the resume content
    resume_content = read_resume_file(resume_path)
    if "Error:" in resume_content:
        # Handle cases where the file couldn't be read
        async def error_stream():
            yield f"data: {{\"error\": \"{resume_content}\"}}\n\n"
        return StreamingResponse(error_stream(), media_type="text/event-stream")

    # Initial prompt for the agent
    initial_prompt = (
        f"Here is my resume:\n---RESUME---\n{resume_content}\n\n"
        f"Here is the job description I want to apply for:\n---JOB DESCRIPTION---\n{job_description}"
    )
    
    # The configuration for the LangGraph stream
    config = {"configurable": {"thread_id": session_id}}

    async def event_stream():
        # Stream the agent's response
        async for chunk in agent_runnable.astream(
            {"messages": [HumanMessage(content=initial_prompt)], "resume_path": resume_path},
            config=config
        ):
            # The output of the stream is the entire state, we only need the last message
            if "messages" in chunk:
                last_message = chunk["messages"][-1]
                if last_message.content:
                    yield f"data: {{\"content\": \"{last_message.content}\", \"session_id\": \"{session_id}\"}}\n\n"
        
        # Signal that the stream is complete
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.post("/feedback")
async def continue_conversation(request: UserFeedbackRequest):
    """
    Endpoint to continue the conversation with user feedback or approval.
    """
    config = {"configurable": {"thread_id": request.session_id}}
    
    # The user's feedback becomes the new message for the agent
    user_message = request.feedback
    if request.recipient_email:
        user_message += f"\nRecipient Email: {request.recipient_email}"

    async def event_stream():
        # Stream the agent's response
        async for chunk in agent_runnable.astream(
            {"messages": [HumanMessage(content=user_message)]},
            config=config
        ):
            if "messages" in chunk:
                last_message = chunk["messages"][-1]
                if last_message.content:
                    yield f"data: {{\"content\": \"{last_message.content}\"}}\n\n"
        
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
