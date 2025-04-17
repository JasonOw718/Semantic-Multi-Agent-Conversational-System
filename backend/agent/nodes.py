from typing import Literal
from langchain_core.messages import ToolMessage
from agent.prompts import QueryPrompts
from agent.state import ProcessState,InputState,OutputState
from langchain_core.runnables import RunnablePassthrough
from agent.chat_history import CustomMongoDBChatMessageHistory
import uuid

class QueryProcessingNodes:
    """
    Collection of node functions for the query processing graph.
    """

    def __init__(self, model_with_tool, chain_multimodal_rag, llm,storage_id):
        """
        Initialize with required models and chains.

        Args:
            model_with_tool: LLM with tool-using capabilities
            chain_multimodal_rag: RAG chain for vector store lookup
            llm: LLM for final response generation
        """
        self.model_with_tool = model_with_tool
        self.chain_multimodal_rag = chain_multimodal_rag
        self.llm = llm
        self.__chat_message_history = CustomMongoDBChatMessageHistory(
            session_id=storage_id,
            connection_string="mongodb://localhost:27017",
            database_name="my_db",
            collection_name="chat_histories",
        )

    def retrieve_history(self,state:InputState) -> ProcessState:
        print("---retrieving history---")
        user_query = state["user_query"]
        self.__chat_message_history.add_user_message(user_query.content)
        return {"messages": self.__chat_message_history.messages}

    def determine_tool_call(self, state: ProcessState) -> ProcessState:
        """
        Analyze the user query to determine if a tool call is needed.

        Args:
            state: Current graph state with messages

        Returns:
            Updated state with analyzer's response
        """
        print("---determine_tool_call---")
        messages = state["messages"]
        tool_call_prompt = QueryPrompts.get_tool_analysis_prompt().format(
            chat_history=messages, query=state["user_query"]
        )
        result = self.model_with_tool.invoke(tool_call_prompt)
        print(result)
        return {"messages": [result]}

    def router(self, state: ProcessState) -> Literal["tools", "search_vectorstore"]:
        """
        Routes the flow based on whether a tool call was initiated.

        Args:
            state: Current graph state

        Returns:
            Next node to route to
        """
        messages = state["messages"]
        if messages[-1].tool_calls:
            return "tools"
        return "search_vectorstore"

    def search_vectorstore(self, state: ProcessState) -> ProcessState:
        """
        Searches the vector store for information related to the query.

        Args:
            state: Current graph state

        Returns:
            Updated state with vector store results
        """
        print("---searching vectorstore---")
        user_query = state["user_query"]
        result = self.chain_multimodal_rag.invoke(user_query.content)
        print(result)
        return {"vectorstore_answer": ToolMessage(content=result,tool_call_id=str(uuid.uuid4()))}

    def finalize_response(self, state: ProcessState) -> OutputState:
        """
        Generates the final response by integrating tool and vector store results.

        Args:
            state: Current graph state

        Returns:
            Updated state with final response
        """
        print("---finalize_response---")
        db_ans = ""
        try:
            db_ans = state["database_answer"]
        except:
            db_ans = ""
        chain = (
            RunnablePassthrough().assign(
                chat_history=lambda x: x["messages"],
                current_query=lambda x: x["user_query"],
                first_answer=lambda x: db_ans,
                second_answer=lambda x: x["vectorstore_answer"],
            )
            | QueryPrompts.get_response_integration_prompt()
            | self.llm
        )

        final_response = chain.invoke(state)
        self.__chat_message_history.add_ai_message(final_response.content)
        return {"answer": final_response}
