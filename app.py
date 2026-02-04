import streamlit as st
from llm_engine import get_ai_response, initialize_llm
from pathlib import Path
from langchain_core.messages import HumanMessage, AIMessage
import time
from datetime import datetime

# Page config
st.set_page_config(
    page_title="ContextIQ - AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize theme in session state (dark mode by default)
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "dark"

# Load CSS based on theme
css_file = "assets/style-dark.css" if st.session_state.theme_mode == "dark" else "assets/style-light.css"
css_path = Path(css_file)
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    # Theme toggle
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("**Theme Mode**")
    with col2:
        theme_icon = "☀️" if st.session_state.theme_mode == "dark" else "🌙"
        if st.button(theme_icon, key="theme_toggle", help="Toggle theme"):
            st.session_state.theme_mode = "light" if st.session_state.theme_mode == "dark" else "dark"
            st.rerun()
    
    st.divider()
    
    # Model selection
    model_option = st.selectbox(
        "🤖 AI Model",
        [
            "llama-3.3-70b-versatile",
            "llama-3.1-70b-versatile", 
            "mixtral-8x7b-32768",
            "gemma2-9b-it"
        ],
        index=0,
        help="Llama 3.3 70B is most powerful"
    )
    
    # Temperature
    temperature = st.slider(
        "🌡️ Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.3,
        step=0.1,
        help="Lower = focused, Higher = creative"
    )
    
    # Max tokens
    max_tokens = st.slider(
        "📏 Max Length",
        min_value=512,
        max_value=4096,
        value=2048,
        step=512,
        help="Maximum response length"
    )
    
    # System prompt
    with st.expander("🎯 System Prompt"):
        custom_system_prompt = st.text_area(
            "Customize AI behavior",
            value="You are ContextIQ, an intelligent and helpful AI assistant. Answer clearly, accurately, and concisely.",
            height=100
        )
    
    st.divider()
    
    # Clear button
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.lc_history = []
        st.rerun()
    
    # User Guide button
    if st.button("📚 User Guide", use_container_width=True):
        st.session_state.show_guide = not st.session_state.get("show_guide", False)
        st.rerun()
    
    # Stats
    st.divider()
    st.markdown("### 📊 Session Stats")
    if "messages" in st.session_state:
        user_msgs = len([m for m in st.session_state.messages if m["role"] == "user"])
        bot_msgs = len([m for m in st.session_state.messages if m["role"] == "assistant"])
        st.metric("Your Messages", user_msgs)
        st.metric("AI Responses", bot_msgs)
    
    st.divider()
    st.caption("⚡ Powered by Groq")
    st.caption("🔗 Built with LangChain")
    st.caption("🚀 Hosted on Streamlit")

# Header
header_gradient = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)" if st.session_state.theme_mode == "dark" else "linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)"
st.markdown(f"""
<div style='text-align: center; padding: 20px 0;'>
    <h1 style='background: {header_gradient}; -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0;'>🤖 ContextIQ</h1>
    <p style='font-size: 18px; color: #888; margin-top: 5px;'>Your Intelligent AI Assistant</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "lc_history" not in st.session_state:
    st.session_state.lc_history = []

if "llm_initialized" not in st.session_state:
    st.session_state.llm_initialized = False

if "current_model" not in st.session_state:
    st.session_state.current_model = None

if "show_guide" not in st.session_state:
    st.session_state.show_guide = False

# Show User Guide if toggled
if st.session_state.show_guide:
    st.markdown("""
    <div class='user-guide'>
        <h2>📚 How to Use ContextIQ</h2>
        
        <h3>🎯 Quick Start</h3>
        <p>Simply type your question in the chat box below and press Enter. ContextIQ will respond instantly!</p>
        
        <h3>💡 Example Prompts to Try</h3>
        
        <div class='example-section'>
            <h4>💻 Coding & Programming</h4>
            <ul>
                <li><code>Write a Python function to calculate fibonacci numbers</code></li>
                <li><code>Explain what async/await does in JavaScript</code></li>
                <li><code>How do I fix this error: TypeError: 'NoneType' object is not subscriptable</code></li>
                <li><code>Create a REST API endpoint in Flask for user authentication</code></li>
            </ul>
        </div>
        
        <div class='example-section'>
            <h4>✍️ Writing & Content</h4>
            <ul>
                <li><code>Write a professional email to request a meeting</code></li>
                <li><code>Create a social media post about sustainable living</code></li>
                <li><code>Help me write a compelling product description for a smartwatch</code></li>
                <li><code>Generate 5 creative blog post titles about AI technology</code></li>
            </ul>
        </div>
        
        <div class='example-section'>
            <h4>🔍 Research & Learning</h4>
            <ul>
                <li><code>Explain quantum computing in simple terms</code></li>
                <li><code>What are the main differences between React and Vue.js?</code></li>
                <li><code>Summarize the key concepts of machine learning</code></li>
                <li><code>How does blockchain technology work?</code></li>
            </ul>
        </div>
        
        <div class='example-section'>
            <h4>💡 Creative & Brainstorming</h4>
            <ul>
                <li><code>Give me 10 unique business ideas for 2024</code></li>
                <li><code>Help me brainstorm names for a coffee shop</code></li>
                <li><code>Create a short story about a time traveler</code></li>
                <li><code>Suggest innovative features for a fitness app</code></li>
            </ul>
        </div>
        
        <div class='example-section'>
            <h4>📊 Data & Analysis</h4>
            <ul>
                <li><code>Analyze the pros and cons of remote work</code></li>
                <li><code>Create a comparison table of different cloud providers</code></li>
                <li><code>What are the key metrics for a successful SaaS business?</code></li>
                <li><code>Help me create a SWOT analysis for a startup</code></li>
            </ul>
        </div>
        
        <h3>⚙️ Pro Tips</h3>
        <ul>
            <li><strong>Be Specific:</strong> Clear questions get better answers</li>
            <li><strong>Use Context:</strong> Reference previous messages in the conversation</li>
            <li><strong>Adjust Temperature:</strong> Lower (0.2-0.3) for factual, Higher (0.7-0.8) for creative</li>
            <li><strong>Choose Right Model:</strong> Llama 3.3 for complex tasks, Gemma 2 for quick answers</li>
            <li><strong>Ask Follow-ups:</strong> Build on previous responses for deeper insights</li>
        </ul>
        
        <h3>🎨 Customize Your Experience</h3>
        <ul>
            <li><strong>Theme:</strong> Click ☀️/🌙 icon to switch between dark and light mode</li>
            <li><strong>Model:</strong> Select different AI models from the dropdown</li>
            <li><strong>Temperature:</strong> Adjust for more creative or focused responses</li>
            <li><strong>System Prompt:</strong> Customize AI's behavior and personality</li>
        </ul>
        
        <p style='text-align: center; margin-top: 20px; font-size: 14px;'>
            <strong>Ready to start?</strong> Close this guide and type your first question below! 🚀
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("✖️ Close Guide", use_container_width=True):
        st.session_state.show_guide = False
        st.rerun()

# Initialize LLM
if not st.session_state.llm_initialized or st.session_state.current_model != model_option:
    try:
        with st.spinner("🔄 Initializing AI model..."):
            initialize_llm(
                model=model_option,
                temperature=temperature,
                max_tokens=max_tokens,
                system_prompt=custom_system_prompt
            )
            st.session_state.llm_initialized = True
            st.session_state.current_model = model_option
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.info("💡 Make sure your GROQ_API_KEY is set in Streamlit secrets")
        st.stop()

# Display welcome message or chat history
if not st.session_state.messages:
    welcome_bg = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)" if st.session_state.theme_mode == "dark" else "linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)"
    st.markdown(f"""
    <div style='text-align: center; padding: 60px 20px; background: {welcome_bg}; border-radius: 15px; color: white; margin: 20px 0;'>
        <h2 style='margin-bottom: 20px;'>👋 Welcome to ContextIQ!</h2>
        <p style='font-size: 18px; margin-bottom: 30px;'>Your powerful AI assistant is ready to help</p>
        <div style='display: flex; justify-content: center; gap: 30px; flex-wrap: wrap;'>
            <div style='text-align: center;'>
                <div style='font-size: 32px; margin-bottom: 10px;'>💻</div>
                <div>Coding Help</div>
            </div>
            <div style='text-align: center;'>
                <div style='font-size: 32px; margin-bottom: 10px;'>✍️</div>
                <div>Writing</div>
            </div>
            <div style='text-align: center;'>
                <div style='font-size: 32px; margin-bottom: 10px;'>🔍</div>
                <div>Research</div>
            </div>
            <div style='text-align: center;'>
                <div style='font-size: 32px; margin-bottom: 10px;'>💡</div>
                <div>Ideas</div>
            </div>
        </div>
        <p style='margin-top: 30px; font-size: 14px; opacity: 0.9;'>Click "📚 User Guide" in sidebar for example prompts!</p>
    </div>
    """, unsafe_allow_html=True)
else:
    # Display chat messages
    for i, msg in enumerate(st.session_state.messages):
        if msg["role"] == "user":
            st.markdown(
                f"""
                <div class='chat-bubble-user'>
                    <strong>You</strong><br/>
                    {msg['content']}
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div class='chat-bubble-bot'>
                    <strong>ContextIQ</strong><br/>
                    {msg['content']}
                </div>
                """,
                unsafe_allow_html=True
            )

# Chat input
user_input = st.chat_input("💬 Ask me anything...", key="user_input")

if user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.lc_history.append(HumanMessage(content=user_input))
    
    # Generate AI response
    with st.spinner("🧠 Thinking..."):
        start_time = time.time()
        
        try:
            response = get_ai_response(
                user_input,
                st.session_state.lc_history,
                temperature=temperature,
                max_tokens=max_tokens,
                system_prompt=custom_system_prompt
            )
            
            response_time = time.time() - start_time
            
            # Add AI response
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "response_time": response_time
            })
            st.session_state.lc_history.append(AIMessage(content=response))
            
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}\n\nPlease try again."
            st.session_state.messages.append({
                "role": "assistant",
                "content": error_msg
            })
    
    st.rerun()

# Footer
footer_color = "#888" if st.session_state.theme_mode == "dark" else "#666"
st.markdown(f"""
<div style='text-align: center; padding: 30px 0 10px 0; color: {footer_color}; font-size: 13px; border-top: 1px solid {"#333" if st.session_state.theme_mode == "dark" else "#eee"}; margin-top: 40px;'>
    <p>Built with ❤️ using Groq, LangChain & Streamlit</p>
    <p style='margin-top: 5px;'>⚡ Ultra-fast AI responses • 🎯 Multiple models • 🎨 Beautiful interface</p>
</div>
""", unsafe_allow_html=True)
