import os
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain_community.memory import ConversationBufferMemory


# LLM
llm = ChatGroq(
    model="gemma2-9b-it",
    temperature=0.3
)

# Memory (chat history)
memory = ConversationBufferMemory(
    return_messages=True
)

# Prompt
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an intelligent, professional AI assistant. "
        "Answer clearly, concisely, and helpfully. "
        "If unsure, say you don't know."
    ),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

def get_ai_response(user_input: str) -> str:
    history = memory.load_memory_variables({})["history"]

    messages = prompt.format_messages(
        history=history,
        input=user_input
    )

    response = llm.invoke(messages)

    memory.save_context(
        {"input": user_input},
        {"output": response.content}
    )

    return response.content
