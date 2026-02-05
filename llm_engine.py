from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
from langchain.callbacks.base import BaseCallbackHandler
import streamlit as st
import os

# LangSmith tracing setup
def setup_langsmith_tracing():
    """Setup LangSmith tracing if API key is available"""
    try:
        langsmith_key = st.secrets.get("LANGSMITH_API_KEY", "")
        if langsmith_key:
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
            os.environ["LANGCHAIN_API_KEY"] = langsmith_key
            os.environ["LANGCHAIN_PROJECT"] = "ContextIQ-Chatbot"
            return True
        return False
    except Exception as e:
        print(f"LangSmith setup error: {e}")
        return False

# Streaming callback handler
class StreamHandler(BaseCallbackHandler):
    def __init__(self, container):
        self.container = container
        self.text = ""
    
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.container.markdown(self.text + "▌")
    
    def on_llm_end(self, *args, **kwargs) -> None:
        self.container.markdown(self.text)

# Global LLM instance
llm = None
current_config = {}

def initialize_llm(
    model: str = "llama-3.3-70b-versatile",
    temperature: float = 0.3,
    max_tokens: int = 2048,
    system_prompt: str = None,
    streaming: bool = True
):
    """Initialize the Groq LLM with specified parameters"""
    global llm, current_config
    
    # Setup LangSmith tracing
    setup_langsmith_tracing()
    
    # Get API key from Streamlit secrets
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except:
        raise ValueError(
            "GROQ_API_KEY not found in Streamlit secrets. "
            "Please add it in your Streamlit Cloud dashboard or .streamlit/secrets.toml"
        )
    
    try:
        # Initialize Groq LLM with proper model names
        # Map old model names to new ones if needed
        model_mapping = {
            "llama-3.3-70b-versatile": "llama-3.3-70b-versatile",
            "llama-3.1-70b-versatile": "llama-3.1-70b-versatile",
            "mixtral-8x7b-32768": "mixtral-8x7b-32768",
            "gemma2-9b-it": "gemma2-9b-it"
        }
        
        actual_model = model_mapping.get(model, model)
        
        llm = ChatGroq(
            model=actual_model,
            temperature=temperature,
            max_tokens=max_tokens,
            groq_api_key=api_key,
            streaming=streaming,
            max_retries=3,
            request_timeout=60,
        )
        
        current_config = {
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "system_prompt": system_prompt,
            "streaming": streaming
        }
        
        return True
        
    except Exception as e:
        raise Exception(f"Failed to initialize LLM: {str(e)}")

def get_prompt_template(system_prompt: str = None):
    """Create prompt template with optional custom system prompt"""
    default_prompt = (
        "You are ContextIQ, an intelligent, professional, and helpful AI assistant. "
        "Answer clearly, concisely, and accurately. Provide detailed explanations when needed. "
        "Use proper formatting with markdown when appropriate. "
        "If you are unsure about something, honestly say you do not know."
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt or default_prompt),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ])
    
    return prompt

def get_ai_response(
    user_input: str,
    chat_history: list,
    temperature: float = None,
    max_tokens: int = None,
    system_prompt: str = None,
    streaming: bool = True,
    stream_container=None
) -> str:
    """Generate AI response with conversation history and optional streaming"""
    global llm
    
    if llm is None:
        raise RuntimeError("LLM not initialized. Please restart the app.")
    
    try:
        # Update LLM settings if provided
        if temperature is not None and temperature != current_config.get("temperature"):
            llm.temperature = temperature
        
        if max_tokens is not None and max_tokens != current_config.get("max_tokens"):
            llm.max_tokens = max_tokens
        
        # Get prompt template
        prompt = get_prompt_template(system_prompt)
        
        # Format messages with history
        messages = prompt.format_messages(
            history=chat_history[:-1],  # Exclude current user message
            input=user_input
        )
        
        # Invoke LLM with or without streaming
        if streaming and stream_container:
            stream_handler = StreamHandler(stream_container)
            response = llm.invoke(messages, config={"callbacks": [stream_handler]})
            return response.content
        else:
            response = llm.invoke(messages)
            return response.content
        
    except Exception as e:
        error_str = str(e).lower()
        
        # Provide helpful error messages
        if "rate_limit" in error_str or "rate limit" in error_str:
            return (
                "⚠️ **Rate Limit Reached**\n\n"
                "Please wait a moment and try again. Groq has generous free tier limits, "
                "but they do apply per minute."
            )
        elif "api_key" in error_str or "authentication" in error_str:
            return (
                "⚠️ **API Key Issue**\n\n"
                "Please check that your GROQ_API_KEY is correctly set in Streamlit secrets."
            )
        elif "timeout" in error_str:
            return (
                "⚠️ **Request Timeout**\n\n"
                "The request took too long. Please try again or select a different model."
            )
        elif "model" in error_str or "not found" in error_str:
            return (
                f"⚠️ **Model Error**\n\n"
                f"The model '{current_config.get('model')}' may not be available. "
                f"Try selecting a different model from the sidebar."
            )
        else:
            return f"⚠️ **Error**: {str(e)}\n\nPlease try again or contact support if the issue persists."

def regenerate_response(
    user_input: str,
    chat_history: list,
    temperature: float = None,
    max_tokens: int = None,
    system_prompt: str = None,
    streaming: bool = True,
    stream_container=None
) -> str:
    """Regenerate the last AI response with potentially different parameters"""
    return get_ai_response(
        user_input,
        chat_history,
        temperature,
        max_tokens,
        system_prompt,
        streaming,
        stream_container
    )
