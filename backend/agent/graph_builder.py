from langgraph.graph import StateGraph, END, START
from langchain_core.tools.base import BaseTool
from typing import List
from agent.nodes import QueryProcessingNodes
from agent.tool_node import ToolNode
from agent.state import ProcessState, InputState, OutputState
import uuid


class GraphBuilder:
    """
    Builder for creating and configuring the query processing graph.
    """

    def __init__(
        self, model_with_tool, chain_multimodal_rag, llm, tools: List[BaseTool]
    ):
        """
        Initialize with required models, chains and tools.

        Args:
            model_with_tool: LLM with tool-using capabilities
            chain_multimodal_rag: RAG chain for vector store lookup
            llm: LLM for final response generation
            tools: List of tools available for queries
        """
        self.tools = tools
        self.nodes = QueryProcessingNodes(
            model_with_tool, chain_multimodal_rag, llm, str(uuid.uuid4())
        )

    def build(self):
        """
        Build and configure the query processing graph.

        Returns:
            Compiled StateGraph
        """
        builder = StateGraph(ProcessState, input=InputState, output=OutputState)

        # Add nodes
        builder.add_node("assistant", self.nodes.determine_tool_call)
        builder.add_node("tools", ToolNode(self.tools))
        builder.add_node("finalize_response", self.nodes.finalize_response)
        builder.add_node("search_vectorstore", self.nodes.search_vectorstore)
        builder.add_node("retrieve_history", self.nodes.retrieve_history)

        # Add edges
        builder.add_edge(START, "retrieve_history")
        builder.add_edge("retrieve_history", "assistant")
        builder.add_conditional_edges("assistant", self.nodes.router)
        builder.add_edge("tools", "search_vectorstore")
        builder.add_edge("search_vectorstore", "finalize_response")
        builder.add_edge("finalize_response", END)

        # Compile and return
        return builder.compile()
