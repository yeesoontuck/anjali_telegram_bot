# Telegram Financial Bot 🤖💰

This is a Telegram bot designed to help users with their **financial queries**. It can:
- Answer questions about financial concepts.
- Analyze uploaded **PDFs**, **CSVs**, and **images**.
- Generate insights and provide explanations.
- Generate a PDF of the bot's response when you type `"generate PDF"`.

### How to Use
Just send a message, upload a file, or share a photo in Telegram. The bot will respond with the appropriate insights.
To download the response as a PDF, type:
`"generate PDF"`

### Requirements
- Python 3.8+
- python-telegram-bot
- Any other libraries listed in `requirements.txt`

### Setup
1. Create a `.env` file and add the following environment variables:

TELEGRAM_TOKEN=your_telegram_token 
GEMINI_API_KEY=your_gemini_api_key

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. run the bot:

```bash
python telegram_bot.py
```

