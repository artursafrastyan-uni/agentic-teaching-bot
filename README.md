# Agentic Telegram Teaching Assistant

This repository contains a modular, state-driven Telegram Bot that acts as an Agentic Teaching Assistant. The system receives lecture slides (PDF), extracts their content, utilizes a local Large Language Model to synthesize a highly structured lesson plan, supplements the plan with live web research, and finally dispatches the combined educational package directly to an educator's email inbox.

## Setup Instructions

### 1. Prerequisites
- Python 3.10+
- A valid Telegram Bot Token from [@BotFather](https://core.telegram.org/bots#6-botfather).
- A Gmail account with an App Password generated for SMTP email sending.
- A GGUF formatted local LLM. The system is tested primarily on `Meta-Llama-3-8B-Instruct.Q4_K_M.gguf`.

### 2. Installation
Clone the repository and set up a virtual environment:

```bash
git clone <repository-url>
cd agentic-teaching-bot
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

*(Note: Ensure `llama-cpp-python` is installed according to your hardware acceleration capabilities for optimal LLM generation speed.)*

### 3. Environment Configuration
Copy the `.env.example` file to `.env`:
```bash
cp .env.example .env
```
Populate `.env` with your credentials:
```env
TELEGRAM_BOT_TOKEN="your_bot_token"
EMAIL_SENDER="your_email@example.com"
EMAIL_PASSWORD="your_app_password"
```

### 4. Running the Bot
```bash
python bot.py
```
Open Telegram and start chatting with your bot!

---

## Design Report

### Architecture Overview
The system follows a modular pipeline wrapped within an Event-Driven State Machine architecture (`TeachingAgentOrchestrator`). The `bot.py` handles user interface (UI) interactions via `python-telegram-bot` and immediately passes contextual data down to the orchestrator layer, keeping the messaging logic completely separate from the heavy computational steps.

1. **Ingestion (`tools/slides.py`)**: Uses `pypdf` to parse text and map pages to semantic boundaries.
2. **LLM Synthesis (`llm_backend.py`)**: A wrapper around `llama-cpp-python` provides memory-optimized context loading for a Llama-3-8B GGUF model running entirely locally.
3. **Information Retrieval (`tools/web_search.py`)**: To avoid DuckDuckGo rate limiting and proxy failures, a robust custom Wikipedia API fetcher pulls exact, highly educational summaries dynamically using full-text search.
4. **Delivery (`tools/email_sender.py`)**: Connects over secure SSL/TLS `smtplib` to asynchronously dispatch the final compiled package.

### Model Choice
**Meta-Llama-3-8B-Instruct (Q4_K_M)** was selected due to its superb instruction-following capabilities. The Q4_K_M quantization strikes the ideal balance between low RAM footprint (allowing it to run comfortably on consumer CPU/RAM setups) and logical coherency needed for structured lesson plan synthesis.

### System Prompts
The core synthesis utilizes strict role-based prompting:
*System Prompt*: "You are an expert teaching assistant. Create a lesson plan based on the slides. Context: [User defined duration and audience]. Include objectives, a timed outline, and one practical exercise."

### Limitations
- **PDF Constraints**: Currently, the parser relies heavily on extractable PDF text objects. Scanned images or image-heavy PDFs will yield limited context.
- **Computational Latency**: Being a local CPU-bound model, LLM inference introduces a processing delay of roughly 30-90 seconds. 
- **Web Search Scope**: The retrieval currently isolates searches to Wikipedia via strict semantic querying to ensure reliability; thus, specific cutting-edge developments not indexed there might be missed.

---

## Evaluation Section

### Test Case 1: Functional Flow (Success)
- **Input**: A PDF on "Intro to NLP", Command: `/plan 60 minutes undergrads`, `ok` confirmation, `/send artur_safrastyan@edu.aua.am`
- **Output**: The bot correctly extracted the text, drafted a 60-minute targeted plan for undergrads, grabbed 3 relevant Wikipedia links for NLP, displayed the preview, and successfully fired the email upon user confirmation.
- **Latency**: ~45 seconds on local hardware.

### Test Case 2: Grounding & Web Search Validation
- **Input**: The generated plan for the NLP slides heavily focuses on Tokenization and Word Embeddings. The orchestrator isolates the keywords and initiates `/research`.
- **Output**: The system returned `Wikipedia: Natural language processing`, `Wikipedia: Word embedding`, and successfully provided snippets summarizing each, directly mapped to the slide content claims. No hallucinated links were produced.

### Test Case 3: Failure Handlers (Bad Inputs)
- **Input**: Uploaded an invalid file (e.g. image or .docx), and attempted to use a malformed email address in the send command (e.g., `/send not_an_email`).
- **Output**: The bot gracefully rejected the non-PDF file with "Unsupported file format. Please upload a PDF". The bot also regex-caught the bad email, immediately warning: "The provided text does not look like a valid email address." and halted the SMTP dispatcher.
