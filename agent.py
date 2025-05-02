import os
from dotenv import load_dotenv
from single_step_agent import SingleStepAgent
from smolagents import LiteLLMModel

# Load environment variables from .env
load_dotenv()

# Ensure GROQ_API_KEY is set in environment (Groq provider reads it automatically)
groq_key = os.environ.get("GROQ_API_KEY")
if not groq_key:
    raise RuntimeError("GROQ_API_KEY environment variable is not set. Make sure .env file is present.")

# Initialize the Groq LLM instance via model_id prefix
# Prefixing model_id with 'groq/' tells LiteLLMModel to use the Groq provider
# num_ctx is not supported by Groq; omit it
llm = LiteLLMModel(
    model_id="groq/llama-3.3-70b-versatile",
)

# Create the agent, passing the model instance
def create_agent():
    return SingleStepAgent(
        model=llm,
        command="python",
        args=["mcp_server.py"],
    )