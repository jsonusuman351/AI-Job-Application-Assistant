from pydantic import BaseModel
from typing import Optional

class StartRequest(BaseModel):
    """
    Model for the initial request to start the job application process.
    """
    session_id: Optional[str] = None
    job_description: str

class UserFeedbackRequest(BaseModel):
    """

    Model for sending user feedback or approval to the agent.
    """
    session_id: str
    feedback: str # e.g., "approve", "regenerate", or specific change requests
    recipient_email: Optional[str] = None # Only needed for the final send step
