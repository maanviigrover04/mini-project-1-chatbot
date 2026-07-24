import os
import time
import requests
import streamlit as st
from dotenv import load_dotenv
import PyPDF2

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "llama-3.3-70b-versatile"

# --- Page Config ---
st.set_page_config(page_title="Luma", page_icon="✨", layout="centered")

# --- Custom CSS ---
def local_css():
    st.markdown("""
    <style>
    /* Global Font & Gradient Background */
    .stApp {
        background: linear-gradient(135deg, #ffffff 0%, #e8f0fe 100%);
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }
    
    /* Header styling */
    .luma-header {
        text-align: center;
        padding-top: 2rem;
        padding-bottom: 1rem;
    }
    .luma-title {
        font-size: 3rem;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 0px;
    }
    .luma-subtitle {
        font-size: 1.2rem;
        color: #7f8c8d;
        font-weight: 300;
        margin-top: 0px;
        margin-bottom: 2rem;
    }

    /* Message Bubbles Container */
    .chat-row {
        display: flex;
        margin-bottom: 1rem;
        width: 100%;
    }
    .chat-row.user {
        justify-content: flex-end;
    }
    .chat-row.assistant {
        justify-content: flex-start;
    }
    
    /* Message Bubbles */
    .chat-bubble {
        padding: 14px 20px;
        border-radius: 20px;
        max-width: 75%;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        font-size: 1rem;
        line-height: 1.5;
        transition: transform 0.2s ease;
    }
    .chat-bubble:hover {
        transform: translateY(-2px);
    }
    
    /* User Bubble (Right, Soft Blue/Purple) */
    .user-bubble {
        background: linear-gradient(135deg, #8ba8ff 0%, #9084f7 100%);
        color: white;
        border-bottom-right-radius: 4px;
    }
    
    /* Assistant Bubble (Left, Light Grey) */
    .assistant-bubble {
        background-color: #ffffff;
        color: #343a40;
        border-bottom-left-radius: 4px;
        border: 1px solid #e9ecef;
    }
    
    /* Hide the default Streamlit footer */
    footer {display: none;}
    </style>
    """, unsafe_allow_html=True)

# --- Logic Functions ---
def extract_text_from_file(uploaded_file):
    if uploaded_file is None:
        return None
    try:
        if uploaded_file.name.lower().endswith('.txt'):
            return uploaded_file.getvalue().decode("utf-8")
        elif uploaded_file.name.lower().endswith('.pdf'):
            reader = PyPDF2.PdfReader(uploaded_file)
            content = ""
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    content += text + "\n"
            return content
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return None
    return None

def call_groq_api(messages):
    if not GROQ_API_KEY:
        return "Error: GROQ_API_KEY is not set in your .env file."

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
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"API Error: {e}"

# --- Main App ---
def main():
    local_css()
    
    # Initialize Session State
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "document_context" not in st.session_state:
        st.session_state.document_context = None
    if "initial_prompt" not in st.session_state:
        st.session_state.initial_prompt = None

    # Sidebar
    with st.sidebar:
        st.markdown("### Luma Settings")
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.document_context = None
            st.rerun()
            
        st.markdown("---")
        st.markdown("### Document Q&A")
        uploaded_file = st.file_uploader("Upload context (.txt, .pdf)", type=["txt", "pdf"])
        
        if uploaded_file:
            if st.button("Load Document", type="primary"):
                with st.spinner("Reading..."):
                    text = extract_text_from_file(uploaded_file)
                    if text:
                        st.session_state.document_context = text
                        st.success("Document loaded! Luma will use this as context.")
                    else:
                        st.error("Failed to extract text.")

    # Header
    st.markdown("""
        <div class="luma-header">
            <h1 class="luma-title">Luma</h1>
            <p class="luma-subtitle">Where conversations feel lighter.</p>
        </div>
    """, unsafe_allow_html=True)

    # Welcome & Quick Replies (if chat is empty)
    if not st.session_state.messages:
        # Initial greeting
        st.markdown("""
            <div class="chat-row assistant">
                <div class="chat-bubble assistant-bubble">
                    Hello! I'm Luma. How can I help you today?
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            if st.button("💡 Study tips", use_container_width=True):
                st.session_state.initial_prompt = "Can you give me some effective study tips?"
                st.rerun()
        with col2:
            if st.button("😄 Tell me a joke", use_container_width=True):
                st.session_state.initial_prompt = "Tell me a funny joke!"
                st.rerun()
        with col3:
            if st.button("❓ Help", use_container_width=True):
                st.session_state.initial_prompt = "What can you do?"
                st.rerun()

    # Display History
    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg["content"]
        
        # We replace newlines with <br> for HTML rendering of normal text
        safe_content = content.replace('\\n', '<br>').replace('\n', '<br>')
        
        if role == "user":
            st.markdown(f"""
                <div class="chat-row user">
                    <div class="chat-bubble user-bubble">
                        {safe_content}
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="chat-row assistant">
                    <div class="chat-bubble assistant-bubble">
                        {safe_content}
                    </div>
                </div>
            """, unsafe_allow_html=True)

    # Input Handling
    prompt = st.chat_input("Type your message here...")
    
    # Process Quick Reply if clicked
    if st.session_state.initial_prompt:
        prompt = st.session_state.initial_prompt
        st.session_state.initial_prompt = None

    if prompt:
        safe_prompt = prompt.replace('\\n', '<br>').replace('\n', '<br>')
        
        # 1. Immediately display the user's message
        st.markdown(f"""
            <div class="chat-row user">
                <div class="chat-bubble user-bubble">
                    {safe_prompt}
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Append user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # 2. Display a loading indicator while fetching
        with st.spinner("Luma is typing..."):
            time.sleep(0.6) # Simulated slight delay for a natural feel
            
            # Prepare messages payload
            api_messages = [{"role": "system", "content": "You are Luma, a helpful, calming, and intelligent AI assistant. Keep responses well-formatted and easy to read."}]
            
            # Add document context if it exists
            if st.session_state.document_context:
                doc_instruction = (
                    "You have been provided with a document. "
                    "If the user's question is related to the document, answer the question based ONLY on the following document content. "
                    "If the question is completely unrelated to the document, behave normally and answer using your general knowledge.\\n\\n"
                    f"Document Content:\\n{st.session_state.document_context}"
                )
                api_messages.append({"role": "system", "content": doc_instruction})
                
            # Add history (excluding the injected system document prompt)
            for m in st.session_state.messages:
                api_messages.append(m)
            
            # Fetch AI response
            ai_response = call_groq_api(api_messages)
            
        # 3. Save AI response and refresh to render
        if ai_response:
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            st.rerun()

if __name__ == "__main__":
    main()


