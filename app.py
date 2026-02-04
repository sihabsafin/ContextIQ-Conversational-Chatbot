import streamlit as st
from llm import get_answer

st.set_page_config(
    page_title="GenAI Q&A Chatbot",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 GenAI Q&A Chatbot")
st.caption("Powered by Groq + LangChain")

user_input = st.text_input(
    "Ask your question:",
    placeholder="e.g. What is Generative AI?"
)

if st.button("Get Answer"):
    if user_input.strip():
        with st.spinner("Thinking..."):
            answer = get_answer(user_input)
        st.markdown("### ✅ Answer")
        st.write(answer)
    else:
        st.warning("Please enter a question.")
