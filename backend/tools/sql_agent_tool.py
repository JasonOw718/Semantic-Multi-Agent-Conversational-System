from tools.database_toolkits import CustomSQLDatabaseToolkit
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent


class SQLAgentTool:
    """Class representing a single SQL database agent tool."""

    def __init__(self, db_instance, llm,system_message):
        """Initialize a new SQL Agent Tool.

        Args:
            db_instance: SQLDatabase instance
            llm: large language model
            system_message: System prompt for the agent
        """
        self.db_instance = db_instance
        self.llm = llm
        self.toolkit = CustomSQLDatabaseToolkit(db=self.db_instance, llm=self.llm)
        self.system_message = system_message
        self.agent_executor = create_react_agent(
            self.llm,
            self.toolkit.get_tools(),
            prompt=self.system_message,
        )
        self.tool = self._create_tool()

    def _create_tool(self):
        """Create the tool function for this SQL agent."""

        @tool
        def _tool(query: str) -> str:
            """Tool placeholder - description will be set by formatter."""
            response = self.agent_executor.invoke({"messages": query})["messages"][-1]
            return response

        return _tool

    def generate_tool_metadata(self, structured_response_llm):
        """Generate metadata for the tool using the provided LLM.

        Args:
            structured_response_llm: LLM configured to output structured responses

        Returns:
            Updated tool with name and description
        """
        db_name = self.db_instance.get_usable_table_names()
        db_context = self.db_instance.get_table_info()

        prompt_template = """
          Generate a response in JSON format using the following structure:
          {{
            "tool_name": "<the name of the tool>",
            "tool_description": "<a detailed description of the tool>"
          }}

          The tool details are as follows:
          - It executes an SQL query on a specific database.
          - This tool is connected to the database identified as "{db_name}".
          - Use this tool when you need to retrieve or manipulate data that resides in the "{db_name}" database.
          - The database context is: {db_context}.
          - Specifically, this tool is for querying the database for a specific document.
          - The tool name should reflect the specific nature of the query (for example, "Query_Airline_Statistic_Tool" or "Query_User's_Behavior_Tool")
            rather than Database Query Tool or SQL query tool, gives a specific name based on domain.
          - Include guidance on when to call this tool or database.

          Please ensure the output includes both the "tool_name" and "tool_description" keys as shown.
        """

        formatted_prompt = prompt_template.format(
            db_name=db_name, db_context=db_context
        )
        response = None
        while response == None:
            response = structured_response_llm.invoke(formatted_prompt)
        self.tool.name = response.tool_name
        extended_description = (
            response.tool_description
            + " The args should be in text form of user's plain text question instead of sql query. Pass query string to this tool "
        )
        self.tool.description = extended_description

        return self.tool
