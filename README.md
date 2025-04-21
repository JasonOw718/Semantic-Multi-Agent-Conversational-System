
# **Semantic-Multi-Agent-Conversational-System**

This project implements a **Multi-Agent Retrieval-Augmented Generation (RAG) system** that can extract and process data from multiple sources, perform semantic search across various document types (text, images, and tables), and provide contextual responses to user queries. It utilizes **Azure Document Intelligence API**, **Google Gemini**, **LangGraph agent architecture**, and **FastAPI** for building scalable RESTful APIs.

---

## 🚀 **Features**

- **Multi-Agent Architecture:**  
  Implements a multi-agent system with SQL sub-agents tailored for different data sources. Each agent specializes in handling specific data types, improving query accuracy and enhancing the system’s response capabilities.

- **Multimodal RAG System:**  
  Contextually retrieves and integrates text, images, and tables based on user input, providing a rich, multimodal response.

- **Data Extraction Pipeline:**  
  Built an extraction pipeline using the **Azure Document Intelligence API** and the **Unstructured Python SDK** to extract data from various document types, including structured tables and unstructured text/images.

- **Semantic Search:**  
  Uses **Multi-Vector Retriever** to index extracted data for semantic search, enabling accurate retrieval of relevant content from documents based on the user's query.

- **Short-term Memory:**  
  Implements **MongoDB** as short-term memory to retain user session data and conversation context.

- **API Development:**  
  Developed scalable RESTful APIs using **FastAPI** and **LangServe** for seamless integration with external systems.

---

## 🛠️ **Tech Stack**

### **Backend**
- **FastAPI** for RESTful APIs
- **LangServe** for LangGraph agent management
- **MongoDB** for session memory
- **Azure Document Intelligence API** for document extraction
- **Google Gemini API** and **GroQ API** for advanced NLP queries
- **Multi-Vector Retriever** for semantic search

### **Frontend**
- **React.js** (optional, for any UI frontend if required)

### **Database**
- **MongoDB** for short-term memory and state management
- **SQL Database** (MySQL/PostgreSQL) for structured data storage
- **FAISS vectorstore** for unstructured data such as text

---

## 🔧 **Installation**

### 1. **Clone the Repository**

```bash
git clone https://github.com/your-username/multi-agent-rag-system.git
cd multi-agent-rag-system
```

### 2. **Backend Setup**

#### Install required Python dependencies:

```bash
cd backend
pip install -r requirements.txt
```

#### Create a `.env` file with the necessary environment variables:

```bash
# .env
AZURE_ENDPOINT="https://<your-azure-endpoint>"
AZURE_DOCUMENT_INTELLEGENCE_KEY="<your-azure-doc-intelligence-key>"
GOOGLE_API_KEY="<your-google-api-key>"
GROQ_API_KEY="<your-groq-api-key>"
DATABASE_FOLDER_PATH="./data/database"
CSV_FOLDER_PATH="./data/csv"
```

#### Run the Backend

```bash
uvicorn main:app --reload
```

### 3. **Frontend Setup (if applicable)**

```bash
cd frontend
npm install
npm start
```

---

## 📸 **Demo Video**

Watch the demo video to see how the system works in action:

[![Multi-Agent RAG System Demo](https://img.youtube.com/vi/6gN00klvvHI/0.jpg)](https://youtu.be/6gN00klvvHI)

> 📺 Click the thumbnail above or [watch the video here](https://youtu.be/6gN00klvvHI).

---

## 📝 **How It Works**

1. **Document Extraction:**  
   The system leverages the **Azure Document Intelligence API** to process and extract structured and unstructured data from multiple document formats. This data includes text, tables, and images.

2. **Data Indexing:**  
   The extracted data is indexed into a **Multi-Vector Retriever** system that allows semantic search, meaning it can find contextually relevant data even if exact text matches are not found.

3. **Query Handling:**  
   When a user submits a query, the **LangGraph** agents process the request using a multi-agent architecture, where SQL agents handle structured data, and other agents handle unstructured data (text, images). The system intelligently combines the results to respond accurately.

4. **Short-Term Memory:**  
   The system uses **MongoDB** to store temporary session data, such as the current context of the conversation, allowing it to provide contextual responses over multiple interactions.

5. **Semantic Search:**  
   The **Multi-Vector Retriever** uses embeddings to store data, enabling semantic search capabilities across text, tables, and images.

---

## ⚙️ **Configuration**

### **Environment Variables**

Make sure to configure the following environment variables in the `.env` file:

```bash
# Azure Configuration
AZURE_ENDPOINT="https://<your-azure-endpoint>"
AZURE_DOCUMENT_INTELLEGENCE_KEY="<your-azure-doc-intelligence-key>"

# Google API Key
GOOGLE_API_KEY="<your-google-api-key>"

# GroQ API Key
GROQ_API_KEY="<your-groq-api-key>"

# Database Paths
DATABASE_FOLDER_PATH="./data/database"
CSV_FOLDER_PATH="./data/csv"
```

### **Security Configuration**

For security reasons, use environment variables to manage sensitive information such as API keys and database paths.

---

## 📌 **Project Timeline**

**Nov 2024 – March 2025**

---

## 📬 **Contact**

For questions, suggestions, or collaboration:

- LinkedIn: [linkedin](https://www.linkedin.com/in/owkasheng)  
- Email: kashengow@gmail.com

---

## 💡 **Future Enhancements**

- Improve the **multi-agent system** to handle more complex queries and diverse data types.
- Implement long-term memory storage for more contextual and personalized responses.
- Extend the **semantic search** capabilities to support even larger datasets and different formats.
