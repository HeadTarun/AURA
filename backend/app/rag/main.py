import streamlit as st
from vector_db.rag_pipeline import ask_question

st.set_page_config(
    page_title="RAG Support Chatbot",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 RAG Support Chatbot")
st.write("Ask questions from the knowledge base.")

# Session state to store chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
question = st.chat_input("Ask your question...")

if question:

    # show user message
    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("user"):
        st.markdown(question)

    # generate answer
    try:
        answer = ask_question(question)

    except Exception as e:
        answer = f"Error: {e}"

    # show assistant message
    with st.chat_message("assistant"):
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})