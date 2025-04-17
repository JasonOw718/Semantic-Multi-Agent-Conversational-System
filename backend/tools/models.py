from pydantic import BaseModel, Field


class ResponseFormatter(BaseModel):
    """Always use this tool to structure your response to the user."""

    tool_description: str = Field(description="The description of the tool")
    tool_name: str = Field(description="The name of the tool")
