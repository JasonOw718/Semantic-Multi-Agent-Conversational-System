import json
from agent.state import ProcessState
from langchain_core.messages import ToolMessage


class ToolNode:
    """A node that runs the tools requested in the last AIMessage."""

    def __init__(self, tools: list) -> None:
        self.tools_by_name = {tool.name: tool for tool in tools}

    def __call__(self, inputs: ProcessState) -> ProcessState:

        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("No message found in input")
        outputs = []
        for tool_call in message.tool_calls:
            if tool_call["name"] not in self.tools_by_name:
                continue
            print(f"---calling {tool_call['name']}---")
            tool_result = self.tools_by_name[tool_call["name"]].invoke(
                tool_call["args"]["query"]
            )
            print(tool_result.content)
            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result.content),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
        return {"database_answer": outputs}
