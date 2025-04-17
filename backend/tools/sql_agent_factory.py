import os
from typing import List
from langchain_community.utilities import SQLDatabase
from langchain import hub
from langchain_core.tools import tool
from tools.sql_agent_tool import SQLAgentTool

class SQLAgentToolFactory:
    """Factory class for creating SQL Agent Tools from database files."""

    def __init__(self, database_folder, llm, response_structure):
        """Initialize the factory.

        Args:
            database_folder: Path to folder containing database files
            llm: Primary language model
            backup_llm: Backup language model
            structured_response_llm: LLM configured for structured output
        """
        self.database_folder = database_folder
        self.llm = llm
        self.response_structure = response_structure
        self.system_message = self._get_system_message()

    def _get_system_message(self):
        """Get the system message for SQL agents."""
        prompt_template = hub.pull("langchain-ai/sql-agent-system-prompt")
        return prompt_template.format(dialect="SQLite", top_k=5)

    def create_tools(self) -> List[tool]:
        """Create tools for all database files in the folder.

        Returns:
            List of configured tool functions
        """
        tools = []

        for file in os.listdir(self.database_folder):
            if file.endswith(".db"):
                db_path = os.path.join(self.database_folder, file)
                uri = f"sqlite:///{db_path}"
                db_instance = SQLDatabase.from_uri(uri)

                sql_agent_tool = SQLAgentTool(
                    db_instance=db_instance,
                    llm=self.llm,
                    system_message=self.system_message,
                )

                tool = sql_agent_tool.generate_tool_metadata(
                    self.llm.with_structured_output(self.response_structure)
                )
                tools.append(tool)

        return tools
