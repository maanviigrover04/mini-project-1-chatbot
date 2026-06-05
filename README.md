# AI Chatbot 🤖

A conversational AI chatbot built with Python that can answer questions and analyze uploaded documents using the Groq API.

## Features
- 💬 Interactive chat with an AI assistant
- 📄 Upload .txt or .pdf documents for context-based Q&A
- 🧠 Powered by Groq API (LLaMA model)
- 💾 Maintains conversation history

## Tech Stack
- Python
- Groq API
- PyPDF2 (for PDF support)

## Installation

1. Clone the repository
   git clone https://github.com/maanvigrover04/mini-project-1-ai-chatbot.git

2. Install dependencies
   pip install -r requirements.txt

3. Create a .env file and add your Groq API key
   GROQ_API_KEY=your_api_key_here

## Usage

Run the chatbot:
   python chatbot.py

To upload a document during chat:
   !upload path/to/your/file.txt

Type 'exit' to quit.

## Author
Maanvi Grover