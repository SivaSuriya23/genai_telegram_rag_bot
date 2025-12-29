# Mini-RAG Telegram Bot

A lightweight GenAI Telegram bot using Retrieval-Augmented Generation (RAG).

## Features
- Answers questions from internal documents
- Uses local embeddings and LLM
- Source-aware responses

## Tech Stack
- Telegram Bot API
- Sentence Transformers (MiniLM)
- SQLite
- Ollama (LLaMA 3)

## How to Run
1. Install dependencies
   pip install -r requirements.txt

2. Start Ollama
   ollama run llama3

3. Ingest documents
   python rag/ingest.py

4. Run bot
   python app.py

## Commands
- /ask <question>
- /help
