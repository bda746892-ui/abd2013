from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import requests
import os

# --- إعدادات المفاتيح (تُسحب الآن من إعدادات الاستضافة - Environment Variables) ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

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

if __name__ == '__main__':
    # التحقق من وجود المفاتيح قبل التشغيل
    if not TELEGRAM_TOKEN or not OPENROUTER_API_KEY:
        print("خطأ: يرجى التأكد من ضبط متغيرات TELEGRAM_TOKEN و OPENROUTER_API_KEY في إعدادات السيرفر.")
    else:
        # بناء التطبيق
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        
        # إضافة الأوامر والموزعات
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        
        print("أنجيلينا تترصد للضحايا الآن...")
        app.run_polling()
