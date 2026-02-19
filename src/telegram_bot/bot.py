"""
Telegram bot for Ultron - handles text, files, and integrations.
"""
from __future__ import annotations

import asyncio
from collections import defaultdict, deque
from datetime import datetime, timedelta
from io import BytesIO
from typing import Dict, List, Optional, Tuple

from loguru import logger
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from src.ai.file_processor import FileProcessor
from src.ai.ultron_agent import UltronAgent
from src.config.settings import settings
from src.google.calendar_manager import GoogleCalendarManager
from src.notion.notion_manager import NotionManager
from src.scraper.announcement_scraper import AnnouncementScraper

Conversation = List[Dict[str, str]]


class UltronBot:
    """Telegram bot for Ultron."""

    def __init__(self) -> None:
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID
        self.application: Optional[Application] = None

        self.notion = NotionManager()
        self.calendar = GoogleCalendarManager()
        self.agent = UltronAgent()
        self.conversations: Dict[int, Conversation] = defaultdict(list)

    # ------------------------------------------------------------------ #
    # Lifecycle
    # ------------------------------------------------------------------ #
    async def start(self) -> None:
        if not self.token:
            raise RuntimeError("TELEGRAM_BOT_TOKEN must be configured.")

        self.application = Application.builder().token(self.token).build()

        self.application.add_handler(CommandHandler("start", self.cmd_start))
        self.application.add_handler(CommandHandler("help", self.cmd_help))
        self.application.add_handler(CommandHandler("assignments", self.cmd_assignments))
        self.application.add_handler(CommandHandler("exams", self.cmd_exams))
        self.application.add_handler(CommandHandler("schedule", self.cmd_schedule))
        self.application.add_handler(CommandHandler("announcements", self.cmd_announcements))
        self.application.add_handler(CommandHandler("research", self.cmd_research))
        self.application.add_handler(CommandHandler("status", self.cmd_status))
        self.application.add_handler(CommandHandler("logs", self.cmd_logs))
        self.application.add_handler(CommandHandler("reset", self.cmd_reset))
        self.application.add_handler(CommandHandler("logs", self.cmd_logs))

        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.application.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, self.handle_file))

        self.application.add_handler(CallbackQueryHandler(self.handle_callback))

        logger.info("Starting Telegram bot…")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()

    async def stop(self) -> None:
        if self.application:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()

    # ------------------------------------------------------------------ #
    # Commands
    # ------------------------------------------------------------------ #
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat = update.effective_chat
        if chat:
            self.chat_id = chat.id

        keyboard = [
            [
                InlineKeyboardButton("📚 Assignments", callback_data="assignments"),
                InlineKeyboardButton("📝 Exams", callback_data="exams"),
            ],
            [
                InlineKeyboardButton("📆 Schedule", callback_data="schedule"),
                InlineKeyboardButton("📢 Announcements", callback_data="announcements"),
            ],
            [
                InlineKeyboardButton("🧠 Research", callback_data="research"),
                InlineKeyboardButton("💬 Chat", callback_data="chat"),
            ],
            [
                InlineKeyboardButton("📄 Logs", callback_data="logs"),
                InlineKeyboardButton("🛠 Status", callback_data="status"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "🤖 Welcome to Ultron – Your AI Academic Assistant!\n\n"
            "I can manage assignments, exams, schedules, announcements, and deep-dive chats. "
            "Tap a quick action or just start typing to chat.",
            reply_markup=reply_markup,
        )

    async def cmd_help(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        help_text = (
            "📘 *Ultron Commands*\n\n"
            "• `/assignments` – Upcoming assignments\n"
            "• `/exams` – Upcoming exams\n"
            "• `/schedule` – Weekly schedule snapshot\n"
            "• `/announcements` – Latest university announcements\n"
            "• `/research <topic>` – (Coming soon) deep research\n"
            "• `/reset` – Clear our conversation history\n\n"
            "✨ Drop files or images, and I'll analyse them like in the dashboard chat."
        )
        await update.message.reply_text(help_text, parse_mode="Markdown")

    async def cmd_reset(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        chat_id = update.effective_chat.id
        self.conversations.pop(chat_id, None)
        await update.message.reply_text("🧼 Conversation reset. Let's start fresh!")

    async def cmd_assignments(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text("📚 Fetching your assignments…")
        assignments = self.calendar.get_assignments() if self.calendar.client else self.notion.get_assignments()

        if not assignments:
            await update.message.reply_text("No upcoming assignments found!")
            return

        lines = ["*Upcoming Assignments*"]
        for assignment in assignments[:10]:
            course = assignment.get("class") or assignment.get("course") or "Course TBA"
            due_date = assignment.get("due_date") or assignment.get("date") or "TBD"
            status = assignment.get("status") or "Scheduled"
            lines.append(f"- *{assignment['title']}*")
            lines.append(f"  Class: {course}")
            lines.append(f"  Due: {due_date}")
            lines.append(f"  Status: {status}\n")

        await update.message.reply_text("\n".join(lines).strip(), parse_mode="Markdown")

    async def cmd_exams(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text("📝 Fetching your exams…")
        exams = self.calendar.get_exams() if self.calendar.client else self.notion.get_exams()

        if not exams:
            await update.message.reply_text("No upcoming exams found!")
            return

        lines = ["*Upcoming Exams*"]
        for exam in exams[:10]:
            course = exam.get("class") or exam.get("course") or "Course TBA"
            date_text = exam.get("date") or exam.get("due_date") or "TBD"
            exam_type = exam.get("type") or exam.get("status") or "Exam"
            location = exam.get("location") or "Location TBA"
            lines.append(f"- *{exam['title']}*")
            lines.append(f"  Class: {course}")
            lines.append(f"  Date: {date_text}")
            lines.append(f"  Type: {exam_type}")
            lines.append(f"  Location: {location}\n")

        await update.message.reply_text("\n".join(lines).strip(), parse_mode="Markdown")

    async def cmd_schedule(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text("📆 Generating weekly schedule…")
        schedule_data = self.calendar.get_weekly_events() if self.calendar.client else self.notion.get_weekly_schedule()

        ordered_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        lines = ["*Weekly Schedule*"]
        has_entries = False
        for day in ordered_days:
            classes = schedule_data.get(day, []) if isinstance(schedule_data, dict) else []
            lines.append(f"*{day}*")
            if not classes:
                lines.append("  - No entries")
            else:
                has_entries = True
                for cls in classes:
                    name = cls.get("name") or cls.get("title") or "Class"
                    schedule_text = cls.get("schedule") or ""
                    if not schedule_text:
                        start = cls.get("start_time") or ""
                        end = cls.get("end_time") or ""
                        schedule_text = f"{start} - {end}".strip(" -")
                    location = cls.get("room") or cls.get("location") or "Room TBA"
                    lines.append(f"  - {name} ({schedule_text or 'TBD'})")
                    lines.append(f"    Location: {location}")
                    description = cls.get("description")
                    if description:
                        snippet = description.strip().splitlines()[0][:100]
                        lines.append(f"    Notes: {snippet}")
            lines.append("")

        if not has_entries:
            lines.append("No classes or events were found for the upcoming week.")

        await update.message.reply_text("\n".join(lines).strip(), parse_mode="Markdown")

    async def cmd_announcements(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text("📢 Checking announcements…")
        scraper = AnnouncementScraper()
        announcements = scraper.scrape()

        if not announcements:
            await update.message.reply_text("No announcements found!")
            return

        for announcement in announcements[:5]:
            message = (
                f"*{announcement['title']}*\n"
                f"{announcement.get('date', 'Date unavailable')}\n\n"
                f"{announcement.get('content', '')[:500]}…\n"
                f"{announcement.get('link', '')}"
            )
            await update.message.reply_text(message.strip(), parse_mode="Markdown")

    async def cmd_research(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not context.args:
            await update.message.reply_text("Please provide a research topic! Example: `/research machine learning`", parse_mode="Markdown")
            return

        topic = " ".join(context.args)
        await update.message.reply_text(
            f"🧠 Starting deep research on: *{topic}*\n\nThis may take a few minutes…",
            parse_mode="Markdown",
        )
        await update.message.reply_text(
            "Research feature coming soon! NightCrawler integration is in progress.",
        )

    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat = update.effective_chat
        if not chat:
            return

        self.chat_id = self.chat_id or chat.id
        notification_target = update.message or (update.callback_query.message if getattr(update, "callback_query", None) else None)

        if notification_target:
            await notification_target.reply_text("🔍 Reviewing system logs...")
        else:
            await chat.send_action("typing")

        reply, metadata = await self._chat_with_ultron(
            chat.id,
            "Please analyze the Ultron system logs from the last 24 hours and summarize any errors or warnings. If everything is healthy, confirm systems are nominal.",
            use_history=False,
            store_history=False,
        )

        response_text = reply.strip()
        meta_appendix = self._format_metadata(metadata)
        if meta_appendix:
            response_text += f"\n\n{meta_appendix}"

        if self.application:
            await self.application.bot.send_message(chat_id=chat.id, text=response_text)


    async def cmd_logs(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        message_obj = None
        if update.message:
            message_obj = update.message
        elif update.callback_query and update.callback_query.message:
            message_obj = update.callback_query.message

        if not message_obj:
            logger.warning("Unable to locate message context for /logs command")
            return

        log_file = settings.LOGS_DIR / settings.LOG_FILE_NAME
        if not log_file.exists():
            await message_obj.reply_text("No log file found yet.")
            return

        cutoff = datetime.now() - timedelta(hours=24)
        filtered_lines = deque(maxlen=5000)

        try:
            with log_file.open("r", encoding="utf-8", errors="ignore") as fh:
                for line in fh:
                    parts = line.split(" | ", 1)
                    if len(parts) < 2:
                        continue
                    timestamp_str = parts[0].strip()
                    try:
                        ts = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        continue
                    if ts >= cutoff:
                        filtered_lines.append(line)
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("Failed to read log file: %s", exc)
            await message_obj.reply_text("Unable to read log file.")
            return

        if not filtered_lines:
            await message_obj.reply_text("No log entries found in the last 24 hours.")
            return

        payload = "".join(filtered_lines)
        buffer = BytesIO(payload.encode("utf-8"))
        buffer.name = "ultron_logs.txt"
        await message_obj.reply_document(
            document=buffer,
            filename=buffer.name,
            caption="Ultron logs (last 24 hours)",
        )

    # ------------------------------------------------------------------ #
    # Chat handling
    # ------------------------------------------------------------------ #
    async def handle_message(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        chat = update.effective_chat
        if not chat:
            return
        self.chat_id = self.chat_id or chat.id

        user_message = (update.message.text or "").strip()
        if not user_message:
            await update.message.reply_text("I didn't catch that. Could you try again?")
            return

        await chat.send_action("typing")
        reply, metadata = await self._chat_with_ultron(chat.id, user_message)

        response_text = reply.strip()
        meta_appendix = self._format_metadata(metadata)
        if meta_appendix:
            response_text += f"\n\n{meta_appendix}"

        await update.message.reply_text(response_text)

    async def handle_file(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        chat = update.effective_chat
        if not chat:
            return
        self.chat_id = self.chat_id or chat.id

        message = update.message
        caption = (message.caption or "").strip()

        await chat.send_action("typing")

        try:
            file_bytes, filename = await self._download_file(message)
        except ValueError as exc:
            await message.reply_text(str(exc))
            return

        processed = FileProcessor.process_file(file_bytes, filename)
        if not processed.get("success"):
            await message.reply_text(f"File processing failed: {processed.get('error', 'Unknown error')}")
            return

        user_text = caption or f"Please analyse the attached file `{filename}`."
        reply, metadata = await self._chat_with_ultron(
            chat.id,
            user_text,
            attachment=processed,
        )

        response_text = reply.strip()
        meta_appendix = self._format_metadata(metadata)
        if meta_appendix:
            response_text += f"\n\n{meta_appendix}"

        await message.reply_text(response_text, parse_mode=None)

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()
        data = query.data

        if data == "assignments":
            await self.cmd_assignments(query, context)
        elif data == "exams":
            await self.cmd_exams(query, context)
        elif data == "schedule":
            await self.cmd_schedule(query, context)
        elif data == "announcements":
            await self.cmd_announcements(query, context)
        elif data == "research":
            await query.edit_message_text("Use `/research <topic>` to initiate a deep research request.")
        elif data == "chat":
            await query.edit_message_text("💬 Chat mode activated! Send a message or drop a file anytime.")
        elif data == "logs":
            await self.cmd_logs(update, context)
        elif data == "status":
            await self.cmd_status(update, context)
        elif data == "logs":
            await self.cmd_logs(update, context)

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #
    async def _chat_with_ultron(
        self,
        chat_id: int,
        message: str,
        attachment: Optional[Dict] = None,
        *,
        use_history: bool = True,
        store_history: bool = True,
    ) -> Tuple[str, Dict]:
        base_history = list(self.conversations.get(chat_id, [])) if use_history else []

        image_data = None
        file_content = None
        if attachment:
            if attachment.get("type") == "image":
                image_data = attachment.get("base64_data")
            else:
                file_content = attachment.get("content")

        response = await self.agent.chat(
            message=message,
            conversation_history=base_history[-12:] if use_history else None,
            image_data=image_data,
            file_content=file_content,
        )

        reply = response.get("message", "I ran into an issue handling that. Could you try again?")
        metadata = response.get("metadata", {})

        if store_history:
            updated_history = list(self.conversations.get(chat_id, [])) if use_history else []
            updated_history.append({"role": "user", "content": message})
            updated_history.append({"role": "assistant", "content": reply})
            self.conversations[chat_id] = updated_history[-20:]

        return reply, metadata

    async def _download_file(self, message) -> Tuple[bytes, str]:
        if message.photo:
            photo = message.photo[-1]
            telegram_file = await photo.get_file()
            filename = f"photo_{telegram_file.file_id}.jpg"
        elif message.document:
            document = message.document
            telegram_file = await document.get_file()
            filename = document.file_name or f"document_{telegram_file.file_id}"
        else:
            raise ValueError("Unsupported file type. Please send an image or document.")

        byte_array = await telegram_file.download_as_bytearray()
        return bytes(byte_array), filename

    def _format_metadata(self, metadata: Dict) -> str:
        if not metadata:
            return ""

        flags = []
        if metadata.get("used_notion_data"):
            flags.append("📘 Notion")
        if metadata.get("used_search"):
            flags.append("🌐 Web Search")
        if metadata.get("used_logs"):
            flags.append("🛠 Logs")

        parts = []
        if flags:
            parts.append("Sources: " + ", ".join(flags))
        if metadata.get("tokens"):
            parts.append(f"Tokens used: {metadata['tokens']}")

        return "\n".join(parts)

    async def send_message(self, message: str, parse_mode: str = "Markdown") -> None:
        if self.application and self.chat_id:
            await self.application.bot.send_message(chat_id=self.chat_id, text=message, parse_mode=parse_mode)

    async def send_reminder(self, title: str, message: str) -> None:
        reminder_text = f"⏰ *Reminder: {title}*\n\n{message}"
        await self.send_message(reminder_text, parse_mode="Markdown")


if __name__ == "__main__":  # pragma: no cover
    bot = UltronBot()
    asyncio.run(bot.start())
