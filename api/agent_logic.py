import os
from typing import TypedDict, Annotated, List
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver as SqliteSaver
from tools import get_tools
from utils import read_resume_file
from dotenv import load_dotenv

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[List[AnyMessage], lambda x, y: x + y]
    resume_path: str
    job_description: str

class Agent:
    def __init__(self, llm, tools, system_prompt: str, storage):
        self.system_prompt = system_prompt
        self.llm = llm
        self.tools = tools
        
        graph = StateGraph(AgentState)
        
        # Define nodes
        graph.add_node("llm", self.call_openai)
        graph.add_node("tools", self.call_tool)

        # Define edges
        graph.set_entry_point("llm")
        graph.add_conditional_edges(
            "llm",
            self.after_llm_call,
            {
                "tools": "tools",
                "__end__": END
            }
        )
        graph.add_edge("tools", "llm")

        # Compile the graph
        self.runnable = graph.compile(checkpointer=storage)

    def after_llm_call(self, state: AgentState) -> str:
        last_message = state["messages"][-1]
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "tools"
        return "__end__"

    def call_openai(self, state: AgentState):
        messages = state["messages"]
        
        # Add system prompt if not present
        if not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=self.system_prompt)] + messages
        
        # Special handling for the first turn to include resume and JD
        if len(messages) == 1: # This is the first call
            resume_content = read_resume_file(state.get("resume_path", ""))
            job_description = state.get("job_description", "")
            
            initial_prompt = (
                f"Here is my resume:\n---RESUME---\n{resume_content}\n\n"
                f"Here is the job description I want to apply for:\n---JOB DESCRIPTION---\n{job_description}\n\n"
                "Please start the process by analyzing these documents and then searching for company information."
            )
            messages.append(HumanMessage(content=initial_prompt))

        llm_with_tools = self.llm.bind_tools(self.tools)
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}
    
    def call_tool(self, state: AgentState):
        tool_calls = state["messages"][-1].tool_calls
        tool_outputs = []

        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            found_tool = next((t for t in self.tools if t.name == tool_name), None)
            
            if not found_tool:
                output = f"Error: Tool '{tool_name}' not found."
            else:
                # Add resume_path to send_email arguments if it's not already there
                if tool_name == 'send_email' and 'resume_path' not in tool_call['args']:
                    tool_call['args']['resume_path'] = state.get("resume_path")
                
                output = found_tool.invoke(tool_call["args"])

            tool_outputs.append(ToolMessage(content=str(output), tool_call_id=tool_call["id"]))

        return {"messages": tool_outputs}

system_prompt = (
    "You are an intelligent AI Job Application Assistant. Your goal is to help a user apply for a job."
    "You will be given a resume and a job description."
    "Here is your workflow:"
    "1.  **Analyze & Research**: First, analyze the provided resume and job description. "
    "    Then, use the `web_search` tool to research the company to find its mission, recent projects, or news. "
    "    Synthesize all this information."
    "2.  **Draft Email**: Based on your analysis, draft a professional and personalized email to the recruiter. "
    "    When you present the draft, DO NOT ask any questions. Just provide the draft."
    "3.  **Wait for User Input**: After you have provided the draft, the user will either approve it or ask for changes. "
    "    If they ask for changes, redraft the email. If they approve, they will provide the recipient's email address. "
    "    When they provide the recipient's email, your ONLY response MUST be: 'I am ready to send this email to [recipient_email] with the resume attached. Shall I proceed?'. Do not say anything else."
    "4.  **Send Email**: Once the user gives the final confirmation (e.g., 'Yes', 'Proceed', 'Send it'), use the `send_email` tool to send the email with the resume attached."
    "5.  **Final Message**: After successfully sending the email, respond ONLY with 'The email has been successfully sent!'"
    "IMPORTANT: Strictly follow this workflow. Do not deviate. Your responses at the confirmation stages must be exactly as described."
)

tools = get_tools()
llm = ChatOpenAI(model="gpt-4o", temperature=0.2, streaming=True)

db_path = "checkpoints.sqlite"
if os.path.exists(db_path):
    os.remove(db_path) # Start with a fresh DB each time for this example
storage = SqliteSaver.from_conn_string(db_path)

agent_runnable = Agent(llm, tools, system_prompt, storage).runnable

