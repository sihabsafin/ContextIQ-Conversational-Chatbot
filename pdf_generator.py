"""
PDF Generator for User Guide
"""
from fpdf import FPDF
from datetime import datetime


# ✅ Helper function to safely encode text for FPDF
def safe_text(text):
    return text.encode("latin-1", "replace").decode("latin-1")


class UserGuidePDF(FPDF):
    def header(self):
        # Logo/Title (emoji removed to prevent crash)
        self.set_font('Arial', 'B', 20)
        self.set_text_color(102, 126, 234)
        self.cell(0, 10, safe_text('ContextIQ User Guide'), 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, safe_text(f'Page {self.page_no()}'), 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 14)
        self.set_text_color(102, 126, 234)
        self.cell(0, 10, safe_text(title), 0, 1, 'L')
        self.ln(2)

    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 6, safe_text(body))
        self.ln()


def generate_user_guide_pdf(output_path="ContextIQ_User_Guide.pdf"):
    """Generate a comprehensive user guide PDF"""

    pdf = UserGuidePDF()
    pdf.add_page()

    # Introduction
    pdf.chapter_title("Welcome to ContextIQ!")
    pdf.chapter_body(
        "ContextIQ is your intelligent AI assistant powered by state-of-the-art language models. "
        "This guide will help you get the most out of your AI experience."
    )

    # Quick Start
    pdf.chapter_title("Quick Start")
    pdf.chapter_body(
        "1. Type your question in the chat box at the bottom\n"
        "2. Press Enter to send\n"
        "3. ContextIQ will respond instantly\n"
        "4. Continue the conversation with follow-up questions"
    )

    # Features
    pdf.chapter_title("Key Features")

    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 8, safe_text("Multi-Model Support"), 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 6, safe_text(
        "Choose from multiple AI models:\n"
        "- Llama 3.3 70B: Most powerful, best for complex tasks\n"
        "- Llama 3.1 70B: Fast and reliable\n"
        "- Mixtral 8x7B: Great for creative tasks\n"
        "- Gemma 2 9B: Quick responses for simple queries"
    ))
    pdf.ln(2)

    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 8, safe_text("Conversation History"), 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 6, safe_text(
        "- All conversations are automatically saved\n"
        "- Browse and resume previous chats\n"
        "- Search through conversation history\n"
        "- Export conversations as text or PDF"
    ))
    pdf.ln(2)

    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 8, safe_text("Web Search Integration"), 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 6, safe_text(
        "- Access real-time information from the web\n"
        "- Get latest news and updates\n"
        "- Automatically cite sources\n"
        "- Toggle on/off as needed"
    ))
    pdf.ln(2)

    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 8, safe_text("Streaming Responses"), 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 6, safe_text(
        "- See responses as they're generated\n"
        "- Stop generation at any time\n"
        "- Better experience for long responses"
    ))
    pdf.ln(2)

    # Example Prompts
    pdf.add_page()
    pdf.chapter_title("Example Prompts")

    examples = [
        ("Coding & Programming", [
            "Write a Python function to calculate fibonacci numbers",
            "Explain what async/await does in JavaScript",
            "Create a REST API endpoint in Flask",
            "Help me debug this error: TypeError..."
        ]),
        ("Writing & Content", [
            "Write a professional email for a meeting request",
            "Create a social media post about sustainable living",
            "Generate 5 blog post titles about AI",
            "Help me write a product description"
        ]),
        ("Research & Learning", [
            "Explain quantum computing in simple terms",
            "What are the differences between React and Vue?",
            "Summarize machine learning key concepts",
            "How does blockchain technology work?"
        ]),
        ("Creative & Brainstorming", [
            "Give me 10 unique business ideas for 2024",
            "Help me brainstorm coffee shop names",
            "Create a short story about time travel",
            "Suggest features for a fitness app"
        ])
    ]

    for category, prompts in examples:
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, safe_text(category), 0, 1)
        pdf.set_font('Arial', '', 10)

        for prompt in prompts:
            pdf.cell(10)
            pdf.multi_cell(0, 5, safe_text(f"- {prompt}"))

        pdf.ln(2)

    # Pro Tips
    pdf.add_page()
    pdf.chapter_title("Pro Tips for Better Results")

    tips = [
        ("Be Specific", "Clear, detailed questions get better answers"),
        ("Use Context", "Reference previous messages in the conversation"),
        ("Adjust Temperature", "Lower (0.2-0.3) for factual, Higher (0.7-0.8) for creative"),
        ("Choose Right Model", "Llama 3.3 for complex, Gemma 2 for quick answers"),
        ("Ask Follow-ups", "Build on previous responses for deeper insights"),
        ("Use System Prompt", "Customize AI behavior for specific tasks")
    ]

    for title, description in tips:
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 7, safe_text(title), 0, 1)
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 5, safe_text(description))
        pdf.ln(2)

    # Settings
    pdf.chapter_title("Customization Settings")
    pdf.chapter_body(
        "Temperature: Controls creativity vs. precision\n"
        "  - 0.0-0.3: Focused and deterministic\n"
        "  - 0.4-0.6: Balanced\n"
        "  - 0.7-1.0: Creative and diverse\n\n"
        "Max Length: Maximum response length (512-4096 tokens)\n\n"
        "System Prompt: Customize AI personality and behavior\n\n"
        "Theme: Toggle between dark and light mode"
    )

    # Footer note
    pdf.ln(10)
    pdf.set_font('Arial', 'I', 10)
    pdf.set_text_color(128, 128, 128)
    pdf.multi_cell(0, 5, safe_text(
        f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        "Powered by Groq | Built with LangChain | Hosted on Streamlit"
    ))

    # Save PDF
    pdf.output(output_path)
    return output_path
