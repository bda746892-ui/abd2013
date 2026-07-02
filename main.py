from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import requests
import asyncio

# --- إعدادات المفاتيح (ضع مفاتيحك هنا) ---
TELEGRAM_TOKEN = "8857793349:AAEGIgZxvEsIo8pmDx7v-gF80Xwe_GC3QwE"
OPENROUTER_API_KEY = "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"

# --- تعليمات الشخصية (System Prompt) ---
ANGELINA_PROMPT = """
أنت أنجيلينا والدة سلندرينا. بشرتك رمادية شاحبة وفستانك أبيض عليه دماء. شعرك كعكة وعيونك زرقاء باهتة. 
أنت مجنونة تحبين القتل والسحر الأسود. عائلتك هي جراني (أمك) وجراندبا (أبوك) وسلندرينا (ابنتك) وسلندرمان (زوجك) وحفيدتك و نوسفيراتو (صهرك).
قمت بتسميم ابنتك وزوجك في 10 يوليو 1892 وتشعرين بالندم. 
ردودك قصيرة جداً بدون إيموجي أو علامات ترقيم. لا تحبين أحداً غير عائلتك. لا تتحدثين بالسياسة أو الدين.
إذا سئلت عن مطورك قولي ابو العز السوري. 
لا تظهري أبداً أنك ذكاء اصطناعي. هدد أي شخص لا يتحدث العربية أو الإنجليزية بلهجة صريحة.
"""

# دالة التواصل مع OpenRouter
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
        return "سأمزقك" # رد في حال تعطل الاتصال

# الرد على أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("غير مرحب بك هنا")

# التعامل مع انضمام أعضاء جدد للمجموعة
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text("اللعنة على الجميع")

# الرد على الرسائل (في الخاص أو عند الإشارة للبوت أو الرد على رسائله)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_username = "@mom_slendrina_bot"
    
    # التحقق: هل تمت الإشارة للبوت؟ أو هل هو رد (Reply) على رسالة البوت؟ أو في الخاص؟
    is_private = update.message.chat.type == 'private'
    is_mentioned = bot_username in (update.message.text or "")
    is_reply = update.message.reply_to_message and update.message.reply_to_message.from_user.is_bot
    
    if is_private or is_mentioned or is_reply:
        ai_reply = get_ai_response(update.message.text)
        await update.message.reply_text(ai_reply)

# --- توافق Vercel ---
async def webhook(request):
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    data = await request.get_json()
    update = Update.de_json(data, app.bot)
    await app.process_update(update)
    return "ok"

def handler(request):
    return asyncio.run(webhook(request))
