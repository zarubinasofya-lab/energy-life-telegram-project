CHANNEL_ID = "@club_energy_life"
import asyncio
import random
from pathlib import Path

from openai import (
    OpenAI,
    APIError,
    RateLimitError,
    APITimeoutError,
    APIConnectionError,
    AuthenticationError,
    BadRequestError
)


from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

from zoneinfo import ZoneInfo
from config import BOT_TOKEN, OPENAI_API_KEY


ADMIN_ID = 461655268
 
client = OpenAI(api_key=OPENAI_API_KEY)

CONTENT_PLAN = {
    0: "health",                  # Понедельник
    1: "energy",                  # Вторник
    2: "opportunities",           # Среда
    3: "story",                   # Четверг
    4: "fohow",                   # Пятница
    5: "polls",                   # Суббота
    6: "energy_life_fohow_bot"    # Воскресенье
}

POSTS_DIR = Path("posts")

TOPIC_FILES = {
    "morning": "morning.txt",
    "evening": "evening.txt",
    "energy": "energy.txt",
    "health": "health.txt",
    "opportunities": "opportunities.txt",
    "story": "story.txt",
    "energy_life_fohow_bot": "energy_life_fohow_bot.txt",
    "fohow": "fohow.txt"
}

COMMON_TAGS = [
    "#энергияжизни",
    "#wellness"
]

TOPIC_TAGS = {
    "morning": [
        "#доброеутро",
        "#энергиядня",
        "#утро",
        "#настройнадень",
        "#заботаосебе"
    ],
    "evening": [
        "#добрыйвечер",
        "#вечер",
        "#восстановление",
        "#спокойствие",
        "#заботаосебе"
    ],
    "energy": [
        "#энергия",
        "#ресурс",
        "#жизненнаяэнергия",
        "#баланс",
        "#самочувствие"
    ],
    "health": [
        "#здоровье",
        "#активноедолголетие",
        "#здоровыйобразжизни",
        "#профилактика",
        "#качестовожизни"
    ],
    "opportunities": [
        "#возможности",
        "#развитие",
        "#дополнительныйдоход",
        "#новоенаправление",
        "#wellnessбизнес"
    ],
    "story": [
        "#история",
        "#вдохновение",
        "#личныйпуть",
        "#изменения",
        "#развитие"
    ],
    "fohow": [
        "#китай",
	"#fohow",
        "#фохоу",
        "#восточныетрадиции",
        "#активноедолголетие",
        "#wellness"
    ],
    "energy_life_fohow_bot": [
        "#тест",
        "#энергияжизни",
        "#новыевозможности",
        "#здоровье",
        "#развитие"
    ],
    "polls": [
        "#опрос",
        "#мнение",
        "#выбор",
        "#здоровье",
        "#энергия"
    ]
}

def add_tags_to_post(post: str, topic: str) -> str:
    topic_tags = TOPIC_TAGS.get(topic, [])

    selected_tags = []

    selected_tags.extend(COMMON_TAGS)

    if topic_tags:
        selected_tags.extend(
            random.sample(
                topic_tags,
                min(3, len(topic_tags))
            )
        )

    unique_tags = []

    for tag in selected_tags:
        if tag not in unique_tags:
            unique_tags.append(tag)

    tags_text = " ".join(unique_tags)

    return f"{post}\n\n{tags_text}"

IMAGES_DIR = Path("images")
IMAGE_EXTENSIONS = ["*.jpg", "*.jpeg", "*.png"]


def get_ready_post(topic: str) -> str:
    filename = TOPIC_FILES.get(topic)

    if not filename:
        raise ValueError(f"Нет файла для раздела: {topic}")

    file_path = POSTS_DIR / filename

    if not file_path.exists():
        raise FileNotFoundError(f"Файл с постами не найден: {file_path}")

    content = file_path.read_text(encoding="utf-8")

    posts = [
        post.strip()
        for post in content.split("---")
        if post.strip()
    ]

    if not posts:
        raise ValueError(f"В файле {file_path} нет готовых постов.")

    return random.choice(posts)

def get_ready_poll() -> dict:
    file_path = POSTS_DIR / "polls.txt"

    if not file_path.exists():
        raise FileNotFoundError(f"Файл с опросами не найден: {file_path}")

    content = file_path.read_text(encoding="utf-8")

    blocks = [
        block.strip()
        for block in content.split("---")
        if block.strip()
    ]

    polls = []

    for block in blocks:
        lines = [
            line.strip()
            for line in block.splitlines()
            if line.strip()
        ]

        if len(lines) >= 5:
            polls.append({
                "question": lines[0],
                "options": lines[1:5]
            })

    if not polls:
        raise ValueError("В файле polls.txt нет корректных опросов.")

    return random.choice(polls)

def get_ready_image(topic: str):
    folder_path = IMAGES_DIR / topic

    if not folder_path.exists():
        return None

    image_files = []

    for extension in IMAGE_EXTENSIONS:
        image_files.extend(folder_path.glob(extension))

    if not image_files:
        return None

    return random.choice(image_files)


def generate_post(topic: str) -> str:
    prompts = {

        "morning": (
          "Напиши утренний Telegram-пост для канала «Энергия жизни».\n"
          "Тема: доброе утро, энергия дня, спокойный старт, забота о себе.\n"
          "Стиль: теплый, мягкий, вдохновляющий.\n"
          "Без продаж, без медицинских обещаний, без упоминания MLM.\n"
          "Объем 70–110 слов.\n"
          "В конце добавь легкий вопрос или пожелание на день."
          "В пост добавляй смайлы по смыслу"
        ),

        "evening": (
          "Напиши вечерний Telegram-пост для канала «Энергия жизни».\n"
          "Тема: завершение дня, восстановление, спокойствие, благодарность себе, забота о состоянии.\n"
          "Стиль: теплый, спокойный, мягкий.\n"
          "Без продаж, без медицинских обещаний, без упоминания MLM.\n"
          "Объем 70–110 слов.\n"
          "В конце добавь мягкий вопрос или пожелание спокойного вечера."
	  "В пост добавляй смайлы по смыслу"

        ),


        "partner_story": (
            "Напиши вдохновляющую историю партнера wellness-направления. "
            "Без обещаний дохода. Без MLM. "
            "Сделай акцент на развитии, окружении, новых возможностях и личностном росте. "
            "Объем 150-200 слов."
	    "В пост добавляй смайлы по смыслу"

        ),
        "energy": (
            "Напиши Telegram-пост для канала «Энергия жизни» на тему энергии дня. "
            "Стиль: спокойный, теплый, полезный. "
            "Без медицинских обещаний, без продаж, без слова MLM. "
            "Объем до 120 слов. В конце задай вопрос аудитории."
	    "В пост добавляй смайлы по смыслу"
        ),
        "health": (
            "Напиши Telegram-пост для канала «Энергия жизни» о здоровье, энергии и активном долголетии. "
            "Стиль: экспертный, но простой. "
            "Без медицинских обещаний и диагнозов. "
            "Объем до 150 слов. В конце добавь мягкий вопрос."
	    "В пост добавляй смайлы по смыслу"
        ),
        "opportunities": (
            "Напиши Telegram-пост для канала «Энергия жизни» о новых возможностях, развитии "
            "и дополнительном доходе. "
            "Без обещаний заработка, без агрессивных продаж, без слова MLM. "
            "Объем до 150 слов. Стиль вдохновляющий."
	    "В пост добавляй смайлы по смыслу"
        ),
        "story": (
            "Напиши короткую вдохновляющую историю для Telegram-канала «Энергия жизни». "
            "Тема: человек решил изменить качество жизни, заняться здоровьем и развитием. "
            "Без выдуманных доходов, без обещаний лечения. "
            "Объем до 180 слов."
	    "В пост добавляй смайлы по смыслу"
        ),
        "energy_life_fohow_bot": (
            "Напиши Telegram-пост для канала «Энергия жизни».\n"
            "Цель поста — заинтересовать человека пройти тест.\n"
            "Темы: здоровье, энергия, развитие, новые возможности.\n"
            "Без агрессивных продаж.\n"
            "Без упоминания MLM.\n"
            "Без обещаний дохода.\n"
            "Объем 120-180 слов.\n\n"
            "В конце обязательно напиши:\n\n"
            "🔍 Хотите узнать, какое направление подходит именно вам?\n\n"
            "Пройдите короткий тест:\n"
            "@energy_life_fohow_bot"
	    "В пост добавляй смайлы по смыслу"
        ),
        "fohow": (
            "Напиши Telegram-пост для канала «Энергия жизни» о компании Fohow.\n"
            "Цель — мягко познакомить аудиторию с компанией и направлением wellness.\n"
            "Пиши спокойно, без агрессивных продаж и без давления.\n"
            "Не обещай лечение заболеваний.\n"
            "Не обещай гарантированный доход.\n"
            "Не используй слово MLM.\n"
            "Объясни, что Fohow связана с темами wellness, активного долголетия, "
            "традиционных восточных подходов к здоровью и развитием партнерского направления.\n"
            "Объем 120–180 слов.\n"
            "В конце добавь мягкий вопрос аудитории."
	    "В пост добавляй смайлы по смыслу"
        )
    }

    if topic not in prompts:
        raise ValueError(f"Неизвестная тема поста: {topic}")

    try:
        response = client.responses.create(
            model="gpt-5-mini",
            input=prompts[topic]
        )

        post = response.output_text.strip()

        if not post:
            raise ValueError("OpenAI вернул пустой текст.")

        return post

    except AuthenticationError:
        raise Exception("Ошибка OpenAI: неверный API-ключ.")

    except RateLimitError:
        raise Exception("Ошибка OpenAI: превышен лимит запросов или закончился баланс.")

    except APITimeoutError:
        raise Exception("Ошибка OpenAI: сервер долго не отвечает. Попробуйте позже.")

    except APIConnectionError:
        raise Exception("Ошибка OpenAI: проблема с подключением к интернету.")

    except BadRequestError as e:
        raise Exception(f"Ошибка OpenAI: неверный запрос. {e}")

    except APIError as e:
        raise Exception(f"Ошибка OpenAI API: {e}")

    except Exception as e:
        raise Exception(f"Неизвестная ошибка OpenAI: {e}")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Доступ закрыт.")
        return

    keyboard = [
        [InlineKeyboardButton("🌅 Утро", callback_data="generate_morning")],
        [InlineKeyboardButton("🌙 Вечер", callback_data="generate_evening")],
        [InlineKeyboardButton("🌿 Энергия дня", callback_data="generate_energy")],
        [InlineKeyboardButton("❤️ Здоровье", callback_data="generate_health")],
        [InlineKeyboardButton("🚀 Возможности", callback_data="generate_opportunities")],
        [InlineKeyboardButton("👤 История", callback_data="generate_story")],
        [InlineKeyboardButton("📊 Опрос", callback_data="generate_poll")],
        [InlineKeyboardButton("🤖 Пост @energy_life", callback_data="generate_energy_life_fohow_bot")],	[InlineKeyboardButton("🏮 Пост о Fohow", callback_data="generate_fohow")]
    ]

    await update.message.reply_text(
        "Выберите рубрику для генерации поста:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def generate_poll() -> dict:
    prompt = (
        "Придумай Telegram-опрос для канала «Энергия жизни».\n"
        "Темы: здоровье, энергия, активное долголетие, развитие, новые возможности.\n\n"
        "Верни строго в таком формате:\n"
        "Вопрос: текст вопроса\n"
        "1. вариант\n"
        "2. вариант\n"
        "3. вариант\n"
        "4. вариант\n\n"
        "Без пояснений."
    )

    try:
        response = client.responses.create(
            model="gpt-5-mini",
            input=prompt
        )

        text = response.output_text.strip()

        if not text:
            raise ValueError("OpenAI вернул пустой опрос.")

    except Exception as e:
        print(f"Ошибка генерации опроса: {e}")

        return {
            "question": "Что для вас сейчас актуальнее всего?",
            "options": ["Здоровье", "Энергия", "Развитие", "Новые возможности"]
        }

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    question = ""
    options = []

    for line in lines:
        if line.lower().startswith("вопрос:"):
            question = line.replace("Вопрос:", "").strip()
        elif line.startswith(("1.", "2.", "3.", "4.")):
            options.append(line[2:].strip())

    if not question or len(options) < 4:
        question = "Что для вас сейчас актуальнее всего?"
        options = ["Здоровье", "Энергия", "Развитие", "Новые возможности"]

    return {
        "question": question,
        "options": options[:4]
    }


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        await query.message.reply_text("Доступ закрыт.")
        return

    # Генерация контента
    if query.data.startswith("generate_"):
        topic = query.data.replace("generate_", "")

        await query.message.reply_text("⏳ Генерирую контент...")

        # Генерация опроса
        if topic == "poll":

            poll = generate_poll()

            context.user_data["last_poll"] = poll

            preview = (
                f"📊 {poll['question']}\n\n"
                f"1️⃣ {poll['options'][0]}\n"
                f"2️⃣ {poll['options'][1]}\n"
                f"3️⃣ {poll['options'][2]}\n"
                f"4️⃣ {poll['options'][3]}"
            )

            keyboard = [
                [InlineKeyboardButton(
                    "✅ Опубликовать опрос",
                    callback_data="publish_poll"
                )],
                [InlineKeyboardButton(
                    "🔄 Сгенерировать заново",
                    callback_data="generate_poll"
                )],
                [InlineKeyboardButton(
                    "❌ Отмена",
                    callback_data="cancel"
                )]
            ]

            await query.message.reply_text(
                preview,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        # Генерация обычного поста
        else:
            try:
              post = generate_post(topic)
              post = add_tags_to_post(post, topic)
            except Exception as e:
              await query.message.reply_text(
                f"❌ Не удалось сгенерировать пост.\n\n"
                f"Причина: {e}"
              )
              return

            context.user_data["last_post"] = post
            context.user_data["last_topic"] = topic

            keyboard = [
                [InlineKeyboardButton(
                    "✅ Опубликовать в канал",
                    callback_data="publish"
                )],
                [InlineKeyboardButton(
                    "🔄 Сгенерировать заново",
                    callback_data=f"generate_{topic}"
                )],
                [InlineKeyboardButton(
                    "❌ Отмена",
                    callback_data="cancel"
                )]
            ]

            await query.message.reply_text(
                post,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

    # Публикация обычного поста
       
    elif query.data == "publish":

        post = context.user_data.get("last_post")
        topic = context.user_data.get("last_topic")

        if not post:
            await query.message.reply_text(
                "Нет поста для публикации."
            )
            return

        image_status = "не нужна"

        if topic:
            try:
                image_path = get_ready_image(topic)

                if image_path:
                    with image_path.open("rb") as photo:
                        await context.bot.send_photo(
                            chat_id=CHANNEL_ID,
                            photo=photo
                        )

                    image_status = f"отправлена: {image_path.name}"
                else:
                    image_status = "не найдена"

            except Exception as image_error:
                image_status = f"ошибка картинки: {image_error}"

                await query.message.reply_text(
                    f"⚠️ Картинку отправить не удалось.\n\n"
                    f"Причина: {image_error}\n\n"
                    f"Пост всё равно будет опубликован."
                )

        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=post
        )

        await query.message.reply_text(
            f"✅ Пост опубликован в канал.\n"
            f"Картинка: {image_status}"
        )


    # Публикация Telegram-опроса
    elif query.data == "publish_poll":

        poll = context.user_data.get("last_poll")

        if not poll:
            await query.message.reply_text(
                "Нет опроса для публикации."
            )
            return

        await context.bot.send_poll(
            chat_id=CHANNEL_ID,
            question=poll["question"],
            options=poll["options"],
            is_anonymous=True
        )

        await query.message.reply_text(
            "✅ Опрос опубликован в канал."
        )

    # Отмена
    elif query.data == "cancel":

        context.user_data["last_post"] = None
        context.user_data["last_poll"] = None

        await query.message.reply_text(
            "❌ Действие отменено."
        )


async def publish_topic(app, topic, with_image=False):
    image_status = "не нужна"

    try:
        # Картинка перед основным постом
        if with_image:
            try:
                image_path = get_ready_image(topic)

                if image_path:
                    with image_path.open("rb") as photo:
                        await app.bot.send_photo(
                            chat_id=CHANNEL_ID,
                            photo=photo
                        )

                    image_status = f"отправлена: {image_path.name}"
                else:
                    image_status = "не найдена"

            except Exception as image_error:
                image_status = f"ошибка картинки: {image_error}"

                await app.bot.send_message(
                    chat_id=ADMIN_ID,
                    text=(
                        "⚠️ Не удалось отправить картинку перед основным постом.\n\n"
                        f"Раздел: {topic}\n"
                        f"Причина: {image_error}\n\n"
                        "Пост всё равно будет опубликован."
                    )
                )

        # Основной пост или опрос
        if topic == "polls":
            poll = get_ready_poll()

            await app.bot.send_poll(
                chat_id=CHANNEL_ID,
                question=poll["question"],
                options=poll["options"],
                is_anonymous=True
            )

        else:
            post = get_ready_post(topic)
            post = add_tags_to_post(post, topic)


            await app.bot.send_message(
                chat_id=CHANNEL_ID,
                text=post
            )

        await app.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                f"✅ Автопост опубликован из готового файла: {topic}\n"
                f"Картинка: {image_status}"
            )
        )

    except Exception as e:
        print(f"Ошибка автопостинга: {e}")

        await app.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                f"❌ Ошибка автопостинга.\n\n"
                f"Раздел: {topic}\n"
                f"Причина: {e}"
            )
        )


def main():

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    scheduler = BackgroundScheduler(timezone=ZoneInfo("Europe/Moscow"))

    # 09:00 — утренний пост без картинки
    scheduler.add_job(
        lambda: asyncio.run(
            publish_topic(app, "morning")
        ),
        trigger="cron",
        hour=9,
        minute=0
    )

    # 15:00 — основной пост с картинкой
    scheduler.add_job(
        lambda: asyncio.run(
            publish_topic(
                app,
                CONTENT_PLAN[datetime.now(ZoneInfo("Europe/Moscow")).weekday()],
                with_image=True
            )
        ),
        trigger="cron",
        hour=22,
        minute=50
    )

    # 21:00 — вечерний пост без картинки
    scheduler.add_job(
        lambda: asyncio.run(
            publish_topic(app, "evening")
        ),
        trigger="cron",
        hour=21,
        minute=0
    )

    scheduler.start()

    print("Контент-бот запущен...")
    print("Автопостинг включен:")
    print("09:00 — утренний пост")
    print("15:00 — основной пост")
    print("21:00 — вечерний пост")

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()