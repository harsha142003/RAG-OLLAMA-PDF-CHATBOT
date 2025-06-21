import streamlit as st
from PyPDF2 import PdfReader
from langchain_community.llms import Ollama
from dotenv import load_dotenv
import os

load_dotenv()

st.set_page_config(page_title="PDF ChatBot", layout="wide")

# --- Initialize session state ---
if 'chat_histories' not in st.session_state:
    st.session_state['chat_histories'] = {"Default": []}
if 'current_chat' not in st.session_state:
    st.session_state['current_chat'] = "Default"
if 'nav_page' not in st.session_state:
    st.session_state['nav_page'] = "Chat"
if 'selected_model' not in st.session_state:
    st.session_state['selected_model'] = "Ollama"
if 'gemini_api_key' not in st.session_state:
    st.session_state['gemini_api_key'] = ""

# --- Sidebar Navigation with HTML-like Buttons ---
nav_options = ["Home", "About", "Chat"]
nav_labels = {"Home": "Home", "About": "About", "Chat": "Chat"}

st.sidebar.markdown("""
    <style>
    .nav-btn {
        background: transparent;
        color: #fff;
        border: none;
        padding: 0.6rem 1.2rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        width: 100%;
        text-align: left;
        font-size: 1.08rem;
        transition: background 0.2s;
        cursor: pointer;
        outline: none;
        display: block;
    }
    .nav-btn.selected {
        background: #4FC3F7 !important;
        color: #23242a !important;
        font-weight: bold;
    }
    .nav-btn:hover {
        background: #333a44;
    }
    </style>
""", unsafe_allow_html=True)

st.sidebar.markdown('<div style="margin-bottom:1.5rem;"><b>Navigation</b></div>', unsafe_allow_html=True)

for nav in nav_options:
    selected = st.session_state['nav_page'] == nav
    btn_class = "nav-btn selected" if selected else "nav-btn"
    # Only render one button per nav item, styled with CSS
    if st.sidebar.button(nav_labels[nav], key=f"nav_{nav}", help=f"Go to {nav}", use_container_width=True):
        if not selected:
            st.session_state['nav_page'] = nav
            st.rerun()

# --- Sidebar Chat History & Model Selection ---
st.sidebar.markdown('<div class="sidebar-history-title">Chats</div>', unsafe_allow_html=True)
chat_names = list(st.session_state['chat_histories'].keys())
current_chat = st.sidebar.selectbox("Select chat", chat_names, index=chat_names.index(st.session_state['current_chat']), key="chat_select")
st.session_state['current_chat'] = current_chat

# --- Model Selection ---
model_options = ["Ollama", "Gemini"]
selected_model = st.sidebar.selectbox("Model", model_options, key="model_select")
st.session_state['selected_model'] = selected_model

# --- Main Area ---
st.markdown('<div class="main-area">', unsafe_allow_html=True)

if st.session_state['nav_page'] == "Home":
    st.header("RAG Based PDF Reader ChatBot Using Ollama")
    image_path = "RAG.png"
    st.image(image_path)

elif st.session_state['nav_page'] == "About":
    st.header("About Our Project")
    st.subheader("Project Overview")
    st.write("This project is a RAG (Retrieve and Generate) based PDF reader chatbot using the Ollama LLM.")
    st.write("The chatbot allows users to interact with and query the content of uploaded PDFs.")
    st.subheader("Technology Used")
    st.write("1. **Streamlit**: For building the user interface.")
    st.write("2. **Ollama LLM**: For generating responses based on the content of the PDF.")
    st.write("3. **PyPDF2**: For extracting text from PDF files.")
    st.subheader("Functionality")
    st.write("1. **PDF Upload**: Users can upload a PDF file.")
    st.write("2. **Text Extraction**: The content of the PDF is extracted for processing.")
    st.write("3. **Question Answering**: Users can ask questions about the PDF content, and the chatbot provides answers based on the extracted text.")
    st.subheader("Technical Details")
    st.write("1. **PDF Content Extraction**: The text from the uploaded PDF is processed to make it queryable.")
    st.write("2. **Ollama Model Integration**: The chatbot uses the Ollama LLM to generate answers based on the PDF content.")
    st.write("3. **Streamlit UI**: Provides a user-friendly interface for interaction.")

elif st.session_state['nav_page'] == "Chat":
    st.title("PDF ChatBot (CodeLlama)")

    # --- PDF Upload (always visible, native Streamlit) ---
    pdf_file = st.file_uploader("Upload your PDF", type="pdf", key="pdf-uploader", label_visibility="visible")
    if pdf_file is not None:
        if 'pdf_text' not in st.session_state or st.session_state.get('last_pdf_filename') != pdf_file.name:
            with st.spinner('Extracting text from the PDF...'):
                reader = PdfReader(pdf_file)
                text = ''
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text
                st.session_state['pdf_text'] = text
                st.session_state['last_pdf_filename'] = pdf_file.name
        pdf_text = st.session_state['pdf_text']
    else:
        pdf_text = None

    # --- Chat History ---
    chat_history = st.session_state['chat_histories'][st.session_state['current_chat']]

    # --- Welcome Message ---
    if not chat_history:
        st.markdown('<div class="welcome">Where should we begin?</div>', unsafe_allow_html=True)

    # --- Chat Container ---
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for i, (q, a) in enumerate(chat_history):
        st.markdown(
            f'''
            <div style="display: flex; justify-content: flex-end; margin-bottom: 4px;">
                <div style="
                    background: #23242a;
                    color: #4FC3F7;
                    padding: 12px 18px;
                    border-radius: 16px 16px 0 16px;
                    max-width: 70%;
                    font-weight: 600;
                    font-size: 1.08rem;
                    box-shadow: 0 2px 8px #1112;">
                    <span style="color:#4FC3F7;font-weight:bold;">You:</span> {q}
                </div>
            </div>
            <div style="display: flex; justify-content: flex-start; margin-bottom: 18px;">
                <div style="
                    background: #343541;
                    color: #FFD54F;
                    padding: 12px 18px;
                    border-radius: 16px 16px 16px 0;
                    max-width: 70%;
                    font-size: 1.08rem;
                    box-shadow: 0 2px 8px #1112;">
                    <span style="color:#FFD54F;font-weight:bold;">Bot:</span> {a}
                </div>
            </div>
            ''',
            unsafe_allow_html=True
        )
    st.markdown('', unsafe_allow_html=True)

    # --- Input Bar (Streamlit form only, always visible) ---
    input_key = f"input_{st.session_state['current_chat']}"
    with st.form(key="chat_form", clear_on_submit=True):
        question = st.text_input("Ask anything about your PDF", key=input_key)
        send = st.form_submit_button("Send")

    if send:
        if not pdf_text:
            st.warning("Please upload a PDF first.")
        elif not question.strip():
            st.warning("Please enter a question.")
        else:
            with st.spinner('Getting the answer from the model...'):
                context = "\n".join([f"Q: {q}\nA: {a}" for q, a in chat_history])
                prompt = f"You are a helpful assistant. Use the following PDF content to answer questions.\nPDF Content: {pdf_text}\n{context}\nQ: {question}\nA:"
                if st.session_state['selected_model'] == "Ollama":
                    llm = Ollama(model="codellama:latest")
                    response = llm.invoke(prompt)
                else:
                    import requests
                    api_key = os.getenv('GEMINI_API_KEY', '')
                    if not api_key:
                        st.warning("Gemini API key not found in .env file.")
                        st.stop()
                    url = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"
                    headers = {"Content-Type": "application/json"}
                    data = {
                        "contents": [{"parts": [{"text": prompt}]}]
                    }
                    params = {"key": api_key}
                    resp = requests.post(url, headers=headers, params=params, json=data)
                    if resp.status_code == 200:
                        response = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                    else:
                        response = f"Gemini API Error: {resp.text}"
            chat_history.append((question, response))
            st.session_state['chat_histories'][st.session_state['current_chat']] = chat_history
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
