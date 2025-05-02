from smolagents import LiteLLMModel, ToolCallingAgent, ToolCollection
from mcp import StdioServerParameters

class SingleStepAgent:
    def __init__(
        self,
        *,
        model_id: str | None = None,
        model: LiteLLMModel | None = None,
        command: str,
        args: list[str],
        context_size: int = 8192,
    ):
        # Accept either a LiteLLMModel instance or a model_id string
        if model is not None:
            self.model = model
        elif model_id is not None:
            self.model = LiteLLMModel(
                model_id=model_id,
                num_ctx=context_size
            )
        else:
            raise ValueError("Must pass either model or model_id")

        # Setup the MCP tool server parameters
        self.server_parameters = StdioServerParameters(
            command=command,
            args=args,
            env=None,
        )
        self.tool_context = None
        self.agent = None

    def __enter__(self):
        # Start the MCP tool server
        self.tool_context = ToolCollection.from_mcp(
            self.server_parameters,
            trust_remote_code=True
        )
        self.tool_collection = self.tool_context.__enter__()
        # Create the agent with the provided LiteLLMModel
        self.agent = ToolCallingAgent(
            tools=self.tool_collection.tools,
            model=self.model,
            max_steps=1
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.tool_context:
            self.tool_context.__exit__(exc_type, exc_val, exc_tb)

    def ask(self, prompt: str):
        return self.agent.run(prompt)