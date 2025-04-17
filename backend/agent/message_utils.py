from langchain_core.messages import ToolMessage

class MessageUtils:
    """
    Utility functions for working with message objects in the conversation.
    """

    @staticmethod
    def find_tool_messages(conversation):
        """
        Extracts tool messages from a conversation, focusing on the most recent consecutive sequence.

        Args:
            conversation: List of message objects from the conversation history

        Returns:
            List of the most recent consecutive tool messages
        """
        tool_messages = []
        last_consecutive_tool_messages = []

        for message in conversation:
            # Check if the message is a ToolMessage
            is_tool_message = (
                isinstance(message, ToolMessage)
                or (
                    hasattr(message, "__class__")
                    and message.__class__.__name__ == "ToolMessage"
                )
                or (hasattr(message, "name") and hasattr(message, "tool_call_id"))
            )

            if is_tool_message:
                # Add to current consecutive sequence
                last_consecutive_tool_messages.append(message)
            else:
                # If we hit a non-tool message and we have tool messages accumulated,
                # reset the consecutive sequence (but keep the overall list)
                if last_consecutive_tool_messages:
                    tool_messages = last_consecutive_tool_messages.copy()
                    last_consecutive_tool_messages = []

        # In case the conversation ends with tool messages,
        # make sure we capture them
        if last_consecutive_tool_messages:
            tool_messages = last_consecutive_tool_messages

        return tool_messages
