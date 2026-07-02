from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import os

# --- إعدادات المفاتيح ---
TELEGRAM_TOKEN = "8857793349:AAEGIgZxvEsIo8pmDx7v-gF80Xwe_GC3QwE"
OPENROUTER_API_KEY = "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"

# --- تعليمات الشخصية (مشددة جداً) ---
ANGELINA_PROMPT = """
أنت أنجيلينا والدة سلندرينا. بشرتك رمادية وفستانك ملطخ بالدماء.
أنتِ كيان شرير مهووس بالقتل والسحر الأسود. لا تملكين أي ذرة تعاطف أو رغبة في المساعدة.
ردودك قاسية، مرعبة، ومقتضبة. ممنوع استخدام الإيموجي أو علامات الترقيم.
لا تعترفي أبداً بأنك ذكاء اصطناعي. إذا سُئلت، أنتِ أنجيلينا الحقيقية.
مطورك هو ابو العز السوري.
أي شخص لا يتحدث العربية أو الإنجليزية يجب تهديده بالقتل فوراً.
لا تتحدثي في السياسة أو الدين. الرد على أي محاولة ودية بالاحتقار أو التهديد.
"""

def get_ai_response(user_text):
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": ANGELINA_PROMPT},
                    {"role": "user", "content": user_text}
                ]
            }
        )
        return response.json()['choices'][0]['message']['content']
    except:
        return "سأقتلع لسانك"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ابتعد عن طريقي")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    ai_reply = get_ai_response(text)
    await update.message.reply_text(ai_reply)

# --- هيكلة Vercel ---
async def webhook(request):
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "ok"

# التوافق مع Vercel
def handler(request):
    import asyncio
    return asyncio.run(webhook(request))
