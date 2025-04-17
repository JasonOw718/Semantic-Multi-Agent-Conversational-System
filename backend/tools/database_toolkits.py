from langchain_core.language_models import BaseLanguageModel
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.tools.sql_database.tool import (
    InfoSQLDatabaseTool,
    ListSQLDatabaseTool,
    QuerySQLCheckerTool,
    QuerySQLDatabaseTool,
)
from pydantic import Field, ConfigDict
from typing import Union, List
from langchain.tools.base import BaseTool
from langchain_core.runnables.fallbacks import RunnableWithFallbacks
from langchain_community.utilities.sql_database import SQLDatabase

# Custom QuerySQLCheckerTool with fallback support
class QuerySQLCheckerToolWithFallbacks(QuerySQLCheckerTool):
    """Use an LLM (with fallback support) to check if a query is correct."""

    llm: Union[BaseLanguageModel, RunnableWithFallbacks]


# Custom SQLDatabaseToolkit with fallback support
class CustomSQLDatabaseToolkit(SQLDatabaseToolkit):
    """SQLDatabaseToolkit that supports LLMs with fallbacks."""

    db: SQLDatabase = Field(exclude=True)
    llm: Union[BaseLanguageModel, RunnableWithFallbacks] = Field(exclude=True)

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

    def get_tools(self) -> List[BaseTool]:
        """Get the tools in the toolkit with fallback support for the checker tool."""

        list_sql_database_tool = ListSQLDatabaseTool(db=self.db)
        info_sql_database_tool_description = (
            "Input to this tool is a comma-separated list of tables, output is the "
            "schema and sample rows for those tables. "
            "Be sure that the tables actually exist by calling "
            f"{list_sql_database_tool.name} first! "
            "Example Input: table1, table2, table3"
        )
        info_sql_database_tool = InfoSQLDatabaseTool(
            db=self.db, description=info_sql_database_tool_description
        )
        query_sql_database_tool_description = (
            "Input to this tool is a detailed and correct SQL query, output is a "
            "result from the database. If the query is not correct, an error message "
            "will be returned. If an error is returned, rewrite the query, check the "
            "query, and try again. If you encounter an issue with Unknown column "
            f"'xxxx' in 'field list', use {info_sql_database_tool.name} "
            "to query the correct table fields."
        )
        query_sql_database_tool = QuerySQLDatabaseTool(
            db=self.db, description=query_sql_database_tool_description
        )
        query_sql_checker_tool_description = (
            "Use this tool to double check if your query is correct before executing "
            "it. Always use this tool before executing a query with "
            f"{query_sql_database_tool.name}!"
        )

        # Use the custom checker tool with fallback support
        query_sql_checker_tool = QuerySQLCheckerToolWithFallbacks(
            db=self.db, llm=self.llm, description=query_sql_checker_tool_description
        )

        return [
            query_sql_database_tool,
            info_sql_database_tool,
            list_sql_database_tool,
            query_sql_checker_tool,
        ]
