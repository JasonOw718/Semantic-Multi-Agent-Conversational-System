from langchain_core.prompts import PromptTemplate


class QueryPrompts:
    """
    Collection of prompts used for query analysis and response generation.
    """

    TOOL_ANALYSIS_TEMPLATE = """
    You are an intelligent query analyzer. Your task is to process the user's input and determine if any part of it requires an external tool call (e.g., querying a database). Follow these steps:

    1. Read the entire user question carefully.
    2. Identify if the question contains multiple components—especially if it seems to combine operations (like summing values) with a request for specific data (such as a statistic from a database).
    3. Check if any required information is already available in the chat history. If it is, do not trigger an external tool call for that part.
    4. If a tool call is necessary:
       - Separate the query into parts: one that can be answered directly (or computed locally) and one that requires fetching data externally.
       - For example, if the user asks "sum 30 with total cumulative case in Paris," determine that only the "total cumulative case in Paris" should be fetched from the database. The "sum 30" part can be computed or is irrelevant to the external data request.
       - if user asks "What is the number of student in class A and number of student in class B", pass "What is the number of student in class A" and "What is the number of student in class B" as separate queries to the tool.
    5. initiaze a tool call if any tools is needed otherwise, respond to user query without needing to call external tool

    Make sure your analysis focuses solely on whether or not to call the tool, and if yes, precisely what query should be executed that pass as args in tool call parameter.

    Chat History:
    {chat_history}
    User Question:
    {query}
    """

    RESPONSE_INTEGRATION_TEMPLATE = """
        You will receive a user query, chat history, and one or two answers:  
        - If two answers: one from the database, one from the vector store.  
        - If one answer: it's from the vector store.  

        Task: Generate the best final answer without explaining how it was derived.  

        ### Rules:  
        1. QA Queries:  
        - Prioritize the database answer if valid.  
        - If the database lacks data, use the vector store answer if clear.  
        - If both are valid but conflict, trust the database.  

        2. Conversational Queries:  
        - Respond naturally, ignoring database/vector responses if irrelevant.  

        3. Context-Based Responses:  
        - If both sources are unclear, use chat history for context.  
        - Merge relevant info for coherence.  

        4. Final Response Format:  
        - The answer should be direct and final.  
        - Do not explain how the answer was derived.  
        - Example:  

            Query: "What is the total male students amount?"  
            Database: "There are 200 students in total."  
            Vector: "There are 100 students."  
            Final Answer: "There are 200 students in total."  

            Incorrect Format:  
            "Database refers 200 and vector refers 100, hence I should prioritize the database answer, so the final answer is 200 students."  

        ### Examples:  

        User: "Total students?"  
        DB: "Table shows 180."  
        Vector: "100."  
        Final: "The total number of students is 180."  

        User: "Total students?"  
        DB: "No data."  
        Vector: "100."  
        Final: "The total number of students is 100."  

        User: "How are you?"  
        DB: "No data."  
        Vector: "No relevant data."  
        Final: "I'm doing great! How about you?"  

        User: "Add number of students with 30"  
        Chat History: "The number of students available is 50."  
        DB: "No data"  
        Vector: "Based on the table, the value is 60, adding with 30 = 90"  
        Final: "The number of students is 50, adding 30 results in 80."  

        Now generate a final answer for:  

        Chat History:  
        {chat_history}  

        User Query:  
        {current_query}  

        DB:  
        {first_answer}  

        Vector:  
        {second_answer}  

    """

    @classmethod
    def get_tool_analysis_prompt(cls):
        """Returns the formatted tool analysis prompt template."""
        return cls.TOOL_ANALYSIS_TEMPLATE

    @classmethod
    def get_response_integration_prompt(cls):
        """Returns the formatted response integration prompt template."""
        return PromptTemplate.from_template(cls.RESPONSE_INTEGRATION_TEMPLATE)
