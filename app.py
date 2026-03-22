import streamlit as st
import os
from config import config
from models.embeddings import search, get_collection_count
from models.llm import classify_question, generate_concise_answer, generate_detailed_answer, web_search_fallback
from utils.db_connector import run_text_to_sql

# Page configuration
st.set_page_config(page_title="Data Lineage Chatbot", layout="wide")

# App Header
st.title("Data Lineage & Catalogue Assistant")
st.subheader("Ask anything about your company data, lineage, and policies")

# Sidebar
with st.sidebar:
    st.markdown("## YourCompany")
    st.markdown("---")
    
    # Response Mode
    mode = st.radio("Response Mode:", ["Concise", "Detailed"])
    
    # Connection Status
    st.markdown("### Status")
    db_exists = os.path.exists(config.DATABASE_PATH)
    if db_exists:
        st.success("🟢 Database Connected")
    else:
        st.error("🔴 Database Missing")
    
    doc_count = get_collection_count()
    st.info(f"📚 Documents indexed: {doc_count}")

    # API Key Check
    if not config.GROQ_API_KEY or config.GROQ_API_KEY == "your_groq_api_key_here":
        st.warning("⚠️ GROQ_API_KEY is missing or invalid in .env")
    else:
        st.success("🔑 API Key Detected")

    # Clear Chat
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("What would you like to know?"):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Thinking Spinner
    with st.spinner("Thinking..."):
        try:
            # Step 1: Classify the question
            category = classify_question(prompt)
            
            context = ""
            source_label = ""
            is_web_search = False

            # Step 2: Route to correct component
            if category == "database":
                context = run_text_to_sql(prompt)
                source_label = "Database"
            elif category == "docs":
                # Search knowledge base
                chunks = search(prompt, n=3)
                
                # Check for low confidence / missing docs fallback
                if len(chunks) < 1:
                    context = web_search_fallback(prompt)
                    source_label = "Web Search"
                    is_web_search = True
                else:
                    context = "\n\n".join(chunks)
                    source_label = "Documents"
            else:
                answer = "I can only answer questions about your company data, lineage, and governance policies."
                context = "Unknown"
            
            # Step 3: Generate the final answer if not already handled
            if context != "Unknown" and not is_web_search:
                if mode == "Concise":
                    answer = generate_concise_answer(prompt, context)
                else:
                    answer = generate_detailed_answer(prompt, context)
            elif is_web_search:
                answer = context # context already contains the web answer

            # Step 4: Display answer and sources
            with st.chat_message("assistant"):
                st.markdown(answer)
                
                # Display source label
                if source_label:
                    color = "orange" if is_web_search else "green"
                    st.markdown(f"**Source:** :{color}[{source_label}]")
                
                # Expandable source details
                with st.expander("View raw context used:"):
                    st.code(context)

            # Add assistant message to history
            st.session_state.messages.append({"role": "assistant", "content": answer})

        except Exception as e:
            error_msg = str(e)
            if "AuthenticationError" in error_msg or "401" in error_msg:
                st.error("Authentication Error: Your GROQ_API_KEY is invalid. Please check your `.env` file.")
            else:
                st.error(f"An error occurred: {error_msg}")
