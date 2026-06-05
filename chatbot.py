import os                #utilized for file handling and environment variable access
import json              #used for handling JSON data when communicating with the API
import requests          #used for making HTTP requests to the Groq API
from dotenv import load_dotenv       #used for loading environment variables from a .env file

# Optional: PyPDF2 for reading PDF documents
try:
    import PyPDF2
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

# Load environment variables from .env file
load_dotenv()

# Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")               
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"  #Groq API endpoint for chat completions
MODEL_NAME = "llama-3.3-70b-versatile"

def read_document(file_path):
    """
    Reads the content of a document (.txt or .pdf).
    """
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return None
    
    _, ext = os.path.splitext(file_path)
    content = ""
    
    try:
        if ext.lower() == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        elif ext.lower() == '.pdf':
            if not PDF_SUPPORT:
                print("Error: PyPDF2 is not installed. Please run 'pip install PyPDF2' to read PDF files.")
                return None
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        content += text + "\n"
        else:
            print(f"Error: Unsupported file format '{ext}'. Only .txt and .pdf are supported.")
            return None
        
        if not content.strip():
            print("Warning: The document is empty or could not be read.")
            return None
            
        return content
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

def call_groq_api(messages):
    """
    Sends a request to the Groq API and returns the AI's response content.
    """
    if not GROQ_API_KEY:
        print("Error: GROQ_API_KEY is not set in the .env file.")
        return None

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": MODEL_NAME,
        "messages": messages
    }

    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        response_data = response.json()
        return response_data['choices'][0]['message']['content']
        
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        if 'response' in locals() and response is not None:
            try:
                print(f"Response details: {response.json()}")
            except ValueError:
                print(f"Response status: {response.status_code}")
        return None
    except KeyError as e:
        print(f"Unexpected API response format: Missing key {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def main():
    print("Welcome to the AI Chatbot!")
    print("Type 'exit' to end the chat.")
    print("To upload a document context, type: !upload <path_to_file>")
    print("-" * 50)
    
    document_context = None
    messages = [
        {"role": "system", "content": "You are a helpful and intelligent AI assistant."}
    ]

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break
            
        if not user_input:
            print("Please enter a valid message.")
            continue
            
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break
            
        # Advanced Feature: Handle file upload command
        if user_input.lower().startswith('!upload '):
            file_path = user_input[8:].strip()
            print(f"Reading document: {file_path}...")
            content = read_document(file_path)
            if content:
                document_context = content
                print("Success: Document loaded. I will answer questions based on this document when relevant.")
            else:
                print("Failed to load the document.")
            continue
        
        # Prepare the messages for the current API call
        current_messages = list(messages) # Shallow copy of the conversation history
        
        # If a document is loaded, add a temporary system instruction for document-based Q&A
        if document_context:
            doc_instruction = (
                "You have been provided with a document. "
                "If the user's question is related to the document, answer the question based ONLY on the following document content. "
                "If the question is completely unrelated to the document, behave normally and answer using your general knowledge.\n\n"
                f"Document Content:\n{document_context}"
            )
            # Inject this specific context before the latest user message
            current_messages.append({"role": "system", "content": doc_instruction})
            
        # Append the current user prompt
        current_messages.append({"role": "user", "content": user_input})
        
        # Make the API call
        print("Assistant is typing...")
        ai_response = call_groq_api(current_messages)
        
        if ai_response:
            print(f"\nAssistant: {ai_response}")
            
            # Save ONLY the user and assistant turns to the permanent conversation history
            # The temporary document context (doc_instruction) is NOT saved permanently to save tokens
            messages.append({"role": "user", "content": user_input})
            messages.append({"role": "assistant", "content": ai_response})

if __name__ == "__main__":
    main()