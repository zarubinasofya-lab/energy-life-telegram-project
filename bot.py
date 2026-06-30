import logging
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from config import TOKEN
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)


ADMIN_ID = 461655268
GOOGLE_SHEET_ID = "1KN6ISDAF3TE3T9FtN0Ijy9ZQ3LS2zES_TSR6MgiLR8o"
CREDENTIALS_FILE = "credentials.json"

ASK_NAME, ASK_AGE, ASK_CITY, ASK_JOB, ASK_INTEREST, ASK_TIME, ASK_EXPERIENCE, ASK_LEARNING = range(8)
 
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
      [InlineKeyboardButton("🔍 Проверить потенциал", callback_data="income_test")],
      [InlineKeyboardButton("🌿 Узнать о проекте", callback_data="about_project")],
      [InlineKeyboardButton("💬 Задать вопрос", callback_data="question")],
      [InlineKeyboardButton("📞 Связаться со мной", callback_data="contact")],
 
    ]

    
    text = (
        "Здравствуйте!\n\n"
        "Вы в проекте «Энергия жизни».\n\n"
        "Здесь мы говорим о здоровье, энергии, активном долголетии "
        "и новых возможностях для развития.\n\n"
        "Выберите, что вам интересно:"
    )

    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "income_test":
        context.user_data.clear()
        context.user_data["step"] = ASK_NAME

        await query.message.reply_text(
            "Отлично. Пройдем короткий тест — это займет 1–2 минуты.\n\n"
            "1/8. Как вас зовут?"
        )

    elif query.data == "about_project":
        keyboard = [
            [InlineKeyboardButton("❤️ Здоровье", callback_data="about_health")],
            [InlineKeyboardButton("💰 Возможности", callback_data="about_opportunities")],
            [InlineKeyboardButton("🤝 Сообщество", callback_data="about_community")],
            [InlineKeyboardButton("🚀 Как начать", callback_data="about_start")]
        ]

        await query.message.reply_text(
            "🌿 Энергия жизни\n\n"
            "Это сообщество людей, которым интересны:\n\n"
            "✓ здоровье и активное долголетие\n"
            "✓ современные wellness-технологии\n"
            "✓ личностное развитие\n"
            "✓ новые возможности для улучшения качества жизни\n\n"
            "Что вас интересует?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "about_health":
        keyboard = [
            [InlineKeyboardButton("🔍 Пройти тест", callback_data="income_test")],
            [InlineKeyboardButton("📞 Связаться со мной", callback_data="contact")]
        ]

        await query.message.reply_text(
            "❤️ Здоровье и энергия\n\n"
            "Многие люди приходят в проект через интерес к здоровью.\n\n"
            "Сегодня особенно актуальны темы:\n\n"
            "• энергия и восстановление\n"
            "• стресс и качество сна\n"
            "• активное долголетие\n"
            "• современные wellness-подходы\n\n"
            "Мы регулярно публикуем полезные материалы и делимся опытом людей.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "about_opportunities":
        keyboard = [
            [InlineKeyboardButton("🔍 Проверить потенциал", callback_data="income_test")],
            [InlineKeyboardButton("📞 Узнать подробнее", callback_data="contact")]
        ]

        await query.message.reply_text(
            "💰 Новые возможности\n\n"
            "Многие участники проекта начинали не с бизнеса.\n\n"
            "Они искали:\n\n"
            "• дополнительный доход\n"
            "• новое окружение\n"
            "• развитие\n"
            "• возможность работать в удобном графике\n\n"
            "Со временем часть из них стала развивать собственное направление "
            "в сфере здоровья и wellness.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "about_community":
        keyboard = [
            [InlineKeyboardButton("🔍 Пройти тест", callback_data="income_test")],
            [InlineKeyboardButton("📞 Связаться со мной", callback_data="contact")]
        ]

        await query.message.reply_text(
            "🤝 Сообщество\n\n"
            "Одно из главных преимуществ проекта — окружение.\n\n"
            "Вы можете общаться с людьми, которые:\n\n"
            "✓ развиваются\n"
            "✓ интересуются здоровьем\n"
            "✓ изучают новые wellness-подходы\n"
            "✓ открыты к новым возможностям\n\n"
            "Вместе двигаться намного проще.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "about_start":
        keyboard = [
            [InlineKeyboardButton("🔍 Пройти тест", callback_data="income_test")],
            [InlineKeyboardButton("📞 Связаться со мной", callback_data="contact")]
        ]

        await query.message.reply_text(
            "🚀 Как начать\n\n"
            "Начать очень просто.\n\n"
            "Шаг 1. Пройти короткий тест.\n\n"
            "Шаг 2. Получить рекомендации.\n\n"
            "Шаг 3. Пообщаться с наставником.\n\n"
            "Шаг 4. Принять решение, подходит ли вам проект.\n\n"
            "Никаких сложных действий на первом этапе — только знакомство и ответы на ваши вопросы.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "health":
        await query.message.reply_text(
            "В канале «Энергия жизни» мы делимся материалами о здоровье, энергии, "
            "активном долголетии и качестве жизни.\n\n"
            "Что вам сейчас интересно больше всего?\n\n"
            "• Больше энергии\n"
            "• Качественный сон\n"
            "• Снижение стресса\n"
            "• Активное долголетие"
        )

    elif query.data == "question":
        await query.message.reply_text(
            "Вы можете написать мне напрямую:\n\n"
            "@Fendou988777\n\n"
            "Я отвечу на ваш вопрос лично."
        )

    elif query.data == "materials":
        await query.message.reply_text(
            "Отлично! Я подготовлю для вас полезные материалы по теме здоровья, энергии "
            "и активного долголетия.\n\n"
            "А пока рекомендую подписаться на канал «Энергия жизни», там регулярно выходят "
            "простые советы и полезные материалы."
        )

    elif query.data == "details":
        await query.message.reply_text(
            "Отлично!\n\n"
            "Я могу подробнее рассказать, как направление здоровья и wellness может стать "
            "дополнительной возможностью для развития и дохода.\n\n"
            "Лучше всего обсудить это лично в коротком разговоре.\n\n"
            "Напишите мне удобное время для связи.\n\n"
            "Или можете сразу написать напрямую:\n\n"
            "@Fendou988777"
        )

    elif query.data == "meeting":
        await query.message.reply_text(
            "Отлично!\n\n"
            "Чтобы обсудить, какой формат сотрудничества может подойти именно вам, "
            "лучше провести короткую личную встречу.\n\n"
            "Напишите мне удобное время для связи.\n\n"
            "Или можете сразу написать напрямую:\n\n"
            "@Fendou988777"
        )

    elif query.data == "contact":
        await query.message.reply_text(
            "Вы можете написать мне напрямую:\n\n"
            "@Fendou988777"
        )

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get("step")
    text = update.message.text

    if step is None:
        await update.message.reply_text("Нажмите /start, чтобы открыть меню.")
        return

    if step == ASK_NAME:
        context.user_data["name"] = text
        context.user_data["step"] = ASK_AGE
        await update.message.reply_text("2/8. Ваш возраст?")

    elif step == ASK_AGE:
        context.user_data["age"] = text
        context.user_data["step"] = ASK_CITY
        await update.message.reply_text("3/8. В какой стране/городе вы живете?")

    elif step == ASK_CITY:
        context.user_data["city"] = text
        context.user_data["step"] = ASK_JOB
        await update.message.reply_text("4/8. В какой сфере вы сейчас работаете или развиваетесь?")

    elif step == ASK_JOB:
        context.user_data["job"] = text
        context.user_data["step"] = ASK_INTEREST

        keyboard = [
            [InlineKeyboardButton("Здоровье", callback_data="interest_health")],
            [InlineKeyboardButton("Дополнительный доход", callback_data="interest_income")],
            [InlineKeyboardButton("Собственное дело", callback_data="interest_business")],
            [InlineKeyboardButton("Общение и развитие", callback_data="interest_growth")]
        ]

        await update.message.reply_text(
            "5/8. Что вам интереснее всего?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


async def test_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("interest_"):
        context.user_data["interest"] = data.replace("interest_", "")
        context.user_data["step"] = ASK_TIME

        keyboard = [
            [InlineKeyboardButton("До 3 часов", callback_data="time_low")],
            [InlineKeyboardButton("3–5 часов", callback_data="time_mid")],
            [InlineKeyboardButton("5–10 часов", callback_data="time_high")],
            [InlineKeyboardButton("Больше 10 часов", callback_data="time_max")]
        ]

        await query.message.reply_text(
            "6/8. Сколько времени в неделю готовы уделять новому направлению?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith("time_"):
        context.user_data["time"] = data.replace("time_", "")
        context.user_data["step"] = ASK_EXPERIENCE

        keyboard = [
            [InlineKeyboardButton("Да", callback_data="experience_yes")],
            [InlineKeyboardButton("Нет", callback_data="experience_no")]
        ]

        await query.message.reply_text(
            "7/8. Был ли у вас опыт продаж или партнерского бизнеса?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith("experience_"):
        context.user_data["experience"] = data.replace("experience_", "")
        context.user_data["step"] = ASK_LEARNING

        keyboard = [
            [InlineKeyboardButton("Да", callback_data="learning_yes")],
            [InlineKeyboardButton("Пока не уверен(а)", callback_data="learning_maybe")]
        ]

        await query.message.reply_text(
            "8/8. Готовы ли вы обучаться новому?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith("learning_"):
        context.user_data["learning"] = data.replace("learning_", "")
        await show_result(query, context)




async def send_lead_notification(context: ContextTypes.DEFAULT_TYPE):
    data = context.user_data

    text = (
        "🔥 Новый лид\n\n"
        f"Имя: {data.get('name', '-')}\n"
        f"Возраст: {data.get('age', '-')}\n"
        f"Город: {data.get('city', '-')}\n"
        f"Занятость: {data.get('job', '-')}\n\n"
        f"Тип: {data.get('type', '-')}\n"
        f"Интерес: {data.get('interest', '-')}\n"
        f"Время: {data.get('time', '-')}\n"
        f"Опыт: {data.get('experience', '-')}\n\n"
        f"Username: {data.get('username', '-')}"
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=text
    )

async def show_result(query, context: ContextTypes.DEFAULT_TYPE):
    interest = context.user_data.get("interest")
    time = context.user_data.get("time")
    experience = context.user_data.get("experience")
    learning = context.user_data.get("learning")

    if interest == "business" and experience == "yes" and time in ["high", "max"]:
        user_type = "Лидер"
        result_text = (
            "Спасибо за ответы.\n\n"
            "По вашим ответам видно, что у вас есть потенциал не только для дополнительного дохода, "
            "но и для построения команды.\n\n"
            "Лучше всего обсудить это лично, чтобы понять, какой формат подойдет именно вам."
        )
        button_text = "Записаться на встречу"
        callback = "meeting"

    elif interest in ["income", "business", "growth"] and learning in ["yes", "maybe"]:
        user_type = "Партнер"
        result_text = (
            "Спасибо за ответы.\n\n"
            "По вашим ответам видно, что вам может быть интересно направление дополнительного дохода "
            "через сферу здоровья и wellness.\n\n"
            "У вас есть хороший стартовый потенциал: интерес к развитию и готовность изучать новое."
        )
        button_text = "Хочу узнать подробнее"
        callback = "details"

    else:
        user_type = "Клиент"
        result_text = (
            "Спасибо за ответы.\n\n"
            "По вашим ответам видно, что вам ближе тема здоровья, энергии и качества жизни.\n\n"
            "Я могу прислать вам полезные материалы по этой теме."
        )
        button_text = "Получить материалы"
        callback = "materials"
    
    interest_map = {
      "health": "Здоровье",
      "income": "Дополнительный доход",
      "business": "Собственное дело",
      "growth": "Общение и развитие"
    }

    time_map = {
      "low": "До 3 часов",
      "mid": "3–5 часов",
      "high": "5–10 часов",
      "max": "Более 10 часов"
    }

    experience_map = {
      "yes": "Да",
      "no": "Нет"
    }
    

    context.user_data["telegram_id"] = query.from_user.id

    context.user_data["username"] = (
        f"@{query.from_user.username}"
        if query.from_user.username
        else ""
    )


    context.user_data["interest"] = interest_map.get(
      context.user_data.get("interest"),
      context.user_data.get("interest")
    )

    context.user_data["time"] = time_map.get(
      context.user_data.get("time"),
      context.user_data.get("time")
    )

    context.user_data["experience"] = experience_map.get(
      context.user_data.get("experience"),
      context.user_data.get("experience")
    )
    

    context.user_data["type"] = user_type


    try:
      save_to_google_sheets(context)
    except Exception as e:
      logging.exception("Ошибка сохранения в Google Sheets")

    try:
      await send_lead_notification(context)
    except Exception as e:
      logging.exception("Ошибка отправки уведомления админу")

    context.user_data["step"] = None

    keyboard = [[InlineKeyboardButton(button_text, callback_data=callback)]]
    await query.message.reply_text(result_text, reply_markup=InlineKeyboardMarkup(keyboard))


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logging.exception("Ошибка в боте:", exc_info=context.error)

def main():
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .connect_timeout(30)
        .read_timeout(30)
        .write_timeout(30)
        .pool_timeout(30)
        .build()
    )

    app.add_error_handler(error_handler)

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        CallbackQueryHandler(
            test_button_handler,
            pattern="^(interest_|time_|experience_|learning_)"
        )
    )

    app.add_handler(CallbackQueryHandler(button_handler))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            text_handler
        )
    )

    print("Бот запущен...")
    app.run_polling(
        drop_pending_updates=True
    )
    




def save_to_google_sheets(context: ContextTypes.DEFAULT_TYPE):
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]

    creds = Credentials.from_service_account_file(
        CREDENTIALS_FILE,
        scopes=scopes
    )

    client = gspread.authorize(creds)
    sheet = client.open_by_key(GOOGLE_SHEET_ID).sheet1

    data = context.user_data
    row = [
      datetime.now().strftime("%d.%m.%Y %H:%M"),
      data.get("name", ""),
      data.get("age", ""),
      data.get("city", ""),
      data.get("job", ""),
      data.get("type", ""),
      data.get("interest", ""),
      data.get("time", ""),
      data.get("experience", ""),
      data.get("telegram_id", ""),
      data.get("username", "")
    ]

    
    sheet.append_row(row)


if __name__ == "__main__":
    main()