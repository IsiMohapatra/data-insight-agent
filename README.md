# 🛠️ CAN Signal Query Assistant 
This project enables natural language interaction with CAN signal data using a Large Language Model (LLM) and dynamic tool calling. It parses user queries and automatically maps them to backend functions, leveraging Groq's LLM APIs and context built from measurement files (Excel + MF4).

---

## 🚀 Features

- 🔍 Natural language prompt interpretation via Groq LLM
- ⚙️ Automatic function calling based on RAG (Retrieval-Augmented Generation)
- 📁 Context generation using Excel mapping and MF4 (.mf4 log) files
- 🔧 Modular tool execution with support for expansion via JSON rules
- 🧠 Smart fallback to friendly chat for small talk or irrelevant prompts

---

## 🧩 Project Structure

project/
│
├── main.py # Entry point with LLM + Groq integration
│
├── rag/ # Context building and function rules
│ ├── context_builder.py # Creates and stores context from files
│ ├── manual.json # Rules mapping user intent to tools
│ └── context.json # Stores pre-processed signal context
│
├── tools/ # LLM-callable tool functions
│ └── <tool_functions>.py
│
├── .env # Environment variables (e.g., GROQ_API_KEY)
├── requirements.txt # Python dependencies
└── README.md # Project documentation

 ## 🧩 Getting Started

### 1. Clone the repository

### 2. Install dependencies
pip install -r requirements.txt

### 3. Set up environment variables
Create a .env file in the root directory:
GROQ_API_KEY=your_groq_api_key_here

### 4. Add Your Files
Place your Excel signal mapping file (e.g. english-inca mapping.xlsx)
Place your MF4 measurement file (CAN log)
Update the paths in main.py if needed.

### 5. Usage
Run the assistant: python main.py

Example:
👤 Your prompt: What is the max value for engine speed and plot it against vehicle speed?

The assistant will:
1.Call Groq LLM to interpret the prompt
2.Match it with available tools from manual.json
3.Dynamically invoke the correct function with relevant context

