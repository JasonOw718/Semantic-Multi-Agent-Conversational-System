from langchain_google_genai import ChatGoogleGenerativeAI,GoogleGenerativeAIEmbeddings
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()

gemini_key = os.getenv("GOOGLE_API_KEY")
groq_key = os.getenv("GROQ_API_KEY")
gemini_backup = os.getenv("BACKUP_GEMINI_KEY")
groq_backup = os.getenv("BACKUP_GROQ_KEY")
gemini_second_backup = os.getenv("BACKUP_GEMINI_KEY2")
os.environ["GOOGLE_API_KEY"] = gemini_backup
gemini = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash", temperature=0
)
groq = ChatGroq(model="llama-3.3-70b-versatile", temperature=0, api_key=groq_key)
backup_gemini = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite",
    temperature=0,
    api_key=gemini_backup,
)
backup_groq = ChatGroq(
    model="llama-3.3-70b-versatile", temperature=0, api_key=groq_backup
)

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
