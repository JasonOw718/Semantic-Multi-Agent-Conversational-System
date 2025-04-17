from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
import logging
from pymongo import errors
from typing import List
from langchain_core.messages import (
    BaseMessage,
    message_to_dict,
    messages_from_dict,
)
from datetime import datetime

logger = logging.getLogger(__name__)

class CustomMongoDBChatMessageHistory(MongoDBChatMessageHistory):
    @property
    def messages(self) -> List[BaseMessage]:  # type: ignore
        """Retrieve the messages from MongoDB"""
        try:
            if self.history_size is None:
                cursor = (
                    self.collection.find({self.session_id_key: self.session_id})
                    .sort("History.date", -1)
                    .limit(6)
                )
            else:
                skip_count = max(
                    0,
                    self.collection.count_documents(
                        {self.session_id_key: self.session_id}
                    )
                    - self.history_size,
                )
                cursor = self.collection.find(
                    {self.session_id_key: self.session_id}, skip=skip_count
                )
        except errors.OperationFailure as error:
            logger.error(error)

        if cursor:
            items = [document[self.history_key] for document in cursor]
        else:
            items = []

        items.reverse()
        messages = messages_from_dict(items)
        return messages

    def add_message(self, message: BaseMessage) -> None:
        """Append the message to the record in MongoDB"""

        dict_message = message_to_dict(message)
        dict_message["date"] = datetime.now()
        try:
            self.collection.insert_one(
                {
                    self.session_id_key: self.session_id,
                    self.history_key: dict_message,
                }
            )
        except errors.WriteError as err:
            logger.error(err)
