from typing import Annotated, TypedDict, List
from langchain_core.messages import AIMessage, HumanMessage, AnyMessage, ToolMessage
from langgraph.graph.message import add_messages

class InputState(TypedDict):
    user_query:HumanMessage

class OutputState(TypedDict):
    answer: AIMessage

class ProcessState(InputState):
    messages: Annotated[List[AnyMessage],add_messages]
    database_answer: List[ToolMessage]
    vectorstore_answer: ToolMessage
