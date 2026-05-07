import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import random
import re

from agents.orchestrator import TeachingAgentOrchestrator

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def get_agent(context: ContextTypes.DEFAULT_TYPE) -> TeachingAgentOrchestrator:
    # Use context.user_data to maintain session state per user
    if "agent" not in context.user_data:
        context.user_data["agent"] = TeachingAgentOrchestrator()
    return context.user_data["agent"]

# --- Command Handlers ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Introduces the bot and shows a small example."""
    welcome_text = (
        "👋 Welcome! I am your Agentic Telegram Teaching Assistant that AUA won't provide.\n\n"
        "I can help you build lesson plans from your lecture slides, "
        "find supporting web materials, and email the final package to you,\n\n"
        "though you could do it yourself if weren't lazy, but that's why I'm here.\n\n"
        "**How to use me:**\n"
        "1. **Upload** a PDF file containing your lecture slides (PPTX support is a bonus for later!).\n"
        "2. Run `/plan [duration] [target audience]` (e.g., `/plan 60 minutes high schoolers`) to generate a lesson plan preview.\n"
        "3. Reply with `ok` if the plan is fine, or `redo` to generate it again.\n"
        "4. Once you approve the plan, I will automatically research web links and show the final package preview.\n"
        "5. Review the final package and run `/send [your email]` to receive it.\n\n"
        "Type `/help` anytime to see these instructions again."
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lists commands, arguments, and basic limitations."""
    help_text = (
        "📚 *Available Commands:*\n"
        "`/start` - Introduce the bot and show a small example.\n"
        "`/help` - List commands, arguments, and basic limitations.\n"
        "`/plan [duration] [target audience]` - Run the slide-based lesson planning workflow (e.g., `/plan 60 minutes college students`).\n"
        "`/research` - Return a compact list of supporting web resources.\n"
        "`/status` - Show uploaded files, current state, and errors.\n"
        "`/send [email]` - Send the latest approved report by email (e.g., `/send example@example.com`).\n\n"
        "*Limitations:*\n"
        "- Only PDF files are currently supported.\n"
        "- Ensure the slides contain extractable text (no scanned images)."
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows uploaded files, current state, and errors."""
    agent = get_agent(context)
    
    file_status = "None" if not agent.state["pdf_path"] else os.path.basename(agent.state["pdf_path"])
    plan_status = "Ready" if agent.state["lesson_plan"] else "Not started"
    research_status = "Ready" if agent.state["research_links"] else "Not started"
    
    status_text = (
        "📊 *Current Status:*\n"
        f"- Uploaded file: {file_status}\n"
        f"- Lesson Plan: {plan_status}\n"
        f"- Web Research: {research_status}"
    )
    await update.message.reply_text(status_text, parse_mode="Markdown")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Downloads PDF slides and triggers text extraction."""
    document = update.message.document
    if not document.file_name.lower().endswith(".pdf"):
        await update.message.reply_text("Unsupported file format. Please upload a PDF file containing your lecture slides.")
        return
        
    FUN_FACTS = [
        "Did you know? Adolf Hitler’s opening speech at the 1936 Berlin Olympics is the first high-power television signal to escape Earth's ionosphere, traveling into deep space, meaning if there is life outside earth thats the first thing they'll hear.",
        "Ioseb Jughashvili was a talented young Georgian poet who wrote poems with romantic and patriotic themes, he later was named Time's person of the year and nominated for the nobel peace prize twice. Some of you might know this lovely gentleman as Stalin.",
        "Russia's last emperor, Nicholas II, earned the nickname 'Bloody Nicholas' after 1300 people were killed in a stampede during his coronation. The reason the crowd of 500.000 began the stampede were free promise of free bread and sausages.",
        "Despite Luxembourg not having a standing army they still resisted Nazi occupation longer than Denmark, who lasted for ~6 hours.",
        "The famous fashion designer Coco Chanel who created one of the most iconic looks of the 20th century was a Nazi spy and collaborator.",
        "On August 6th, 1945, the United States dropped the world's first atomic bomb on Hiroshima, Japan, on August 8th, The USSR declared war on Japan and invaded Manchuria, on August 9th, the United States dropped the world's second atomic bomb on Nagasaki, Japan. Talk about a bad few days."
    ]

    fact = random.choice(FUN_FACTS)
    
    await update.message.reply_text(f"Downloading and parsing slides...\n\n*While you wait, here is a historic fact:*\n{fact}", parse_mode="Markdown")
    file = await context.bot.get_file(document.file_id)
    
    os.makedirs("downloads", exist_ok=True)
    pdf_path = os.path.join("downloads", document.file_name)
    await file.download_to_drive(pdf_path)
    
    agent = get_agent(context)
    try:
        agent.ingest_slides(pdf_path)
        await update.message.reply_text("Slides successfully parsed! You can now run `/plan`.")
    except Exception as e:
        await update.message.reply_text(f"Error parsing slides: {e}")

async def plan_command(update: Update, context: ContextTypes.DEFAULT_TYPE, redo=False):
    """Calls orchestrator to generate a lesson plan via LLM."""
    agent = get_agent(context)
    
    if not redo:
        if not context.args:
            await update.message.reply_text("Please provide duration and audience. Example: `/plan 60 minutes for high school students`", parse_mode="Markdown")
            return
        context_info = " ".join(context.args)
        agent.state["last_context_info"] = context_info
    else:
        context_info = agent.state.get("last_context_info", "60 minutes, general audience")
        
    await update.message.reply_text(f"Generating lesson plan for '{context_info}'... This will take a moment (I am using the local LLM).")
    
    try:
        result = agent.generate_lesson_plan(context_info=context_info)
        if result.startswith("Error"):
            await update.message.reply_text(result)
        else:
            await update.message.reply_text(f"📚 **Drafted Lesson Plan Preview:**\n\n{result[:3000]}")
            await update.message.reply_text("Does this plan look okay? Reply with `ok` to proceed to web research, or `redo` to generate it again.")
    except Exception as e:
        await update.message.reply_text(f"Error during planning: {e}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles text replies like ok or redo."""
    text = update.message.text.lower().strip()
    agent = get_agent(context)
    
    if text == "ok":
        if agent.state.get("lesson_plan"):
            await update.message.reply_text("Great! Moving forward to web research...")
            await research_command(update, context)
        else:
            await update.message.reply_text("We don't have a plan yet. Please upload a PDF and run `/plan` first.")
    elif text == "redo":
        if agent.state.get("slide_text"):
            await plan_command(update, context, redo=True)
        else:
            await update.message.reply_text("Please upload a PDF first.")

async def research_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Calls orchestrator to search duckduckgo."""
    agent = get_agent(context)
    await update.message.reply_text(f"Researching the web for '{agent.state.get('topic', 'resources')}'...")
    
    try:
        result = agent.perform_web_research()
        if result.startswith("Error"):
            await update.message.reply_text(result)
        else:
            await update.message.reply_text(f"🌐 **Web Links Found:**\n\n{result}", disable_web_page_preview=True)
            
            # Prepare final preview
            report = agent.prepare_final_report()
            await update.message.reply_text(f"📝 **Final Package Preview:**\n\n{report[:3500]}")
            await update.message.reply_text("Does this look good? To confirm and send, reply with `/send my_email@example.com`.")
    except Exception as e:
        await update.message.reply_text(f"Error during research: {e}")

async def send_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Calls orchestrator to email the final report."""
    agent = get_agent(context)
    
    if not context.args:
        await update.message.reply_text("Please provide an email address. Example: `/send artur_safrastyan@edu.aua.am`", parse_mode="Markdown")
        return
        
    recipient = context.args[0]
    
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(email_regex, recipient):
        await update.message.reply_text("The provided text does not look like a valid email address. Please use the format: `/send name@example.com`", parse_mode="Markdown")
        return
        
    await update.message.reply_text(f"Attempting to send email to {recipient}...")
    
    success, message = agent.email_report(recipient)
    await update.message.reply_text(message)

def main():
    """Start the bot."""
    print("Starting Your custom Telegram Bot...")
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Register command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("plan", plan_command))
    app.add_handler(CommandHandler("research", research_command))
    app.add_handler(CommandHandler("send", send_command))
    
    # Register text handler for ok/redo
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Register document handler for slides
    app.add_handler(MessageHandler(filters.Document.PDF, handle_document))
    
    print("Bot is running! Press Ctrl+C to stop and ruin the fun.")
    app.run_polling()

if __name__ == '__main__':
    main()
