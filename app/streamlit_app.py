import streamlit as st
import requests
import json
import time

# --- Configuration ---
API_URL = "http://127.0.0.1:8000"  # Local API URL
st.set_page_config(page_title="AI Job Application Assistant", layout="wide")

# --- Session State Initialization ---
# This ensures that variables persist across reruns
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent_state" not in st.session_state:
    st.session_state.agent_state = "START" # START, REVIEW, GET_EMAIL, CONFIRM, DONE
if "email_draft" not in st.session_state:
    st.session_state.email_draft = ""
if "recipient_email" not in st.session_state:
    st.session_state.recipient_email = ""


# --- UI Rendering ---
st.title("🤖 AI Job Application Assistant")
st.markdown("Welcome! This AI agent will help you draft and send a personalized job application email.")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Main Application Logic ---

# STATE 1: Starting the process
if st.session_state.agent_state == "START":
    st.markdown("---")
    st.subheader("Step 1: Provide Your Details")
    
    uploaded_resume = st.file_uploader("Upload your Resume (PDF or DOCX)", type=["pdf", "docx"])
    job_description = st.text_area("Paste the Job Description here", height=200)

    if st.button("Start Application Process", disabled=(not uploaded_resume or not job_description)):
        st.session_state.messages.append({"role": "user", "content": "Starting the process with my resume and job description."})
        with st.chat_message("user"):
            st.markdown("Starting the process with my resume and job description.")

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            with st.spinner("Agent is analyzing, researching, and drafting the email..."):
                files = {'resume': (uploaded_resume.name, uploaded_resume, uploaded_resume.type)}
                data = {'job_description': job_description}
                
                try:
                    with requests.post(f"{API_URL}/start", files=files, data=data, stream=True) as r:
                        r.raise_for_status()
                        for chunk in r.iter_content(chunk_size=None):
                            if chunk:
                                try:
                                    # Process Server-Sent Events (SSE)
                                    raw_data = chunk.decode('utf-8')
                                    if raw_data.startswith('data:'):
                                        json_data = json.loads(raw_data.split('data: ', 1)[1])
                                        if "content" in json_data:
                                            full_response += json_data["content"]
                                            message_placeholder.markdown(full_response + "▌")
                                        if "session_id" in json_data:
                                            st.session_state.session_id = json_data["session_id"]
                                except json.JSONDecodeError:
                                    pass # Ignore non-JSON chunks

                except requests.exceptions.RequestException as e:
                    st.error(f"API Error: {e}")
                    full_response = "Sorry, I couldn't connect to the agent."

            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            st.session_state.email_draft = full_response
            st.session_state.agent_state = "REVIEW"
            st.rerun()

# STATE 2: Reviewing the draft
elif st.session_state.agent_state == "REVIEW":
    st.markdown("---")
    st.subheader("Step 2: Review the Email Draft")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Approve Draft"):
            st.session_state.messages.append({"role": "user", "content": "The draft is approved."})
            st.session_state.agent_state = "GET_EMAIL"
            st.rerun()
    with col2:
        if st.button("❌ Request Changes"):
            st.warning("Please provide your feedback in the chat input below.")

    feedback = st.chat_input("Provide feedback or type 'approve'...")
    if feedback:
        st.session_state.messages.append({"role": "user", "content": feedback})
        # Handle feedback through the API... (This part is simplified for now)
        # For a full implementation, you would send this to the /feedback endpoint
        # and update the draft.
        if "approve" in feedback.lower():
            st.session_state.agent_state = "GET_EMAIL"
            st.rerun()
        else:
            # In a real app, you'd call the /feedback endpoint here
            st.warning("Change request noted. In this demo, please approve to continue.")


# STATE 3: Getting the recipient's email
elif st.session_state.agent_state == "GET_EMAIL":
    st.markdown("---")
    st.subheader("Step 3: Provide Recipient's Email")

    recipient_email = st.text_input("Recruiter's Email Address")
    if st.button("Confirm Recipient"):
        if recipient_email:
            st.session_state.recipient_email = recipient_email
            st.session_state.messages.append({"role": "user", "content": f"The recipient is {recipient_email}."})
            
            with st.chat_message("user"):
                st.markdown(f"The recipient is {recipient_email}.")

            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                with st.spinner("Agent is preparing the final confirmation..."):
                    # This call asks the agent for the final confirmation message
                    try:
                        response_data = {"session_id": st.session_state.session_id, "feedback": f"The recipient email is {recipient_email}"}
                        with requests.post(f"{API_URL}/feedback", json=response_data, stream=True) as r:
                             r.raise_for_status()
                             for chunk in r.iter_content(chunk_size=None):
                                if chunk:
                                    try:
                                        raw_data = chunk.decode('utf-8')
                                        if raw_data.startswith('data:'):
                                            json_data = json.loads(raw_data.split('data: ', 1)[1])
                                            if "content" in json_data:
                                                full_response += json_data["content"]
                                                message_placeholder.markdown(full_response + "▌")
                                    except json.JSONDecodeError:
                                        pass
                    except requests.exceptions.RequestException as e:
                        st.error(f"API Error: {e}")
                        full_response = "Sorry, something went wrong."
                
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                st.session_state.agent_state = "CONFIRM"
                st.rerun()

# STATE 4: Final confirmation
elif st.session_state.agent_state == "CONFIRM":
    st.markdown("---")
    st.subheader("Step 4: Final Confirmation to Send")

    if st.button("🚀 Yes, Send the Email"):
        st.session_state.messages.append({"role": "user", "content": "Yes, please send it."})
        with st.chat_message("user"):
            st.markdown("Yes, please send it.")
        
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            with st.spinner("Agent is sending the email..."):
                 try:
                    response_data = {"session_id": st.session_state.session_id, "feedback": "Yes, send the email.", "recipient_email": st.session_state.recipient_email}
                    with requests.post(f"{API_URL}/feedback", json=response_data, stream=True) as r:
                         r.raise_for_status()
                         for chunk in r.iter_content(chunk_size=None):
                            if chunk:
                                try:
                                    raw_data = chunk.decode('utf-8')
                                    if raw_data.startswith('data:'):
                                        json_data = json.loads(raw_data.split('data: ', 1)[1])
                                        if "content" in json_data:
                                            full_response += json_data["content"]
                                            message_placeholder.markdown(full_response + "▌")
                                except json.JSONDecodeError:
                                    pass
                 except requests.exceptions.RequestException as e:
                    st.error(f"API Error: {e}")
                    full_response = "Sorry, the email could not be sent."
            
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            st.session_state.agent_state = "DONE"
            st.balloons()
            st.rerun()

# STATE 5: Done
elif st.session_state.agent_state == "DONE":
    st.success("Application process completed successfully!")
    if st.button("Start New Application"):
        # Reset the state for a new application
        st.session_state.session_id = None
        st.session_state.messages = []
        st.session_state.agent_state = "START"
        st.session_state.email_draft = ""
        st.session_state.recipient_email = ""
        st.rerun()
