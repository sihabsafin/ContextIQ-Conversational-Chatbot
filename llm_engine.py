from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
import os

# Explicitly read the key
if not os.getenv("GROQ_API_KEY"):
    raise ValueError("GROQ_API_KEY is not set in environment variables")
    
# Initialize Groq LLM
llm = ChatGroq(
    model="gemma2-9b-it",
    temperature=0.3
)

# Prompt template with history placeholder
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an intelligent, professional AI assistant. "
        "Answer clearly, concisely, and accurately. "
        "If you are unsure, say you do not know."
    ),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

def get_ai_response(user_input: str, chat_history: list) -> str:
    """
    chat_history: list of LangChain messages (HumanMessage, AIMessage)
    """

    messages = prompt.format_messages(
        history=chat_history,
        input=user_input
    )

    response = llm.invoke(messages)
    return response.content
