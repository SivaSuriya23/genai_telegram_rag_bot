import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from rag.retriever import retrieve
from rag.prompt import build_prompt

# ===============================
# Configuration
# ===============================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"

if not TELEGRAM_TOKEN:
    raise RuntimeError(
        "TELEGRAM_BOT_TOKEN environment variable is not set. "
        "Please set it before running the bot."
    )

# ===============================
# Command Handlers
# ===============================

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Mini-RAG Telegram Bot\n\n"
        "/ask <question> – Ask a question from the knowledge base\n"
        "/help – Show this help message"
    )

async def ask_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Please provide a question.\n\nExample:\n/ask What is the leave policy?"
        )
        return

    query = " ".join(context.args)

    # Retrieve relevant chunks
    results = retrieve(query)

    if not results:
        await update.message.reply_text("I couldn't find relevant information.")
        return

    context_text = "\n".join([r[2] for r in results])
    prompt = build_prompt(context_text, query)

    # Call Ollama
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )
        response.raise_for_status()
        answer = response.json().get("response", "No response generated.")
    except Exception as e:
        await update.message.reply_text(f"Error calling LLM: {e}")
        return

    sources = ", ".join(sorted(set([r[1] for r in results])))

    await update.message.reply_text(
        f"{answer}\n\n📄 Sources: {sources}"
    )

# ===============================
# App Entry Point
# ===============================

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("ask", ask_cmd))

    print("✅ Telegram bot started. Waiting for messages...")
    app.run_polling()

if __name__ == "__main__":
    main()
