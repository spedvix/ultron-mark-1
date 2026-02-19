"""
Task scheduler for periodic tasks and reminders.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Set

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger

from src.ai.chat_handler import ChatHandler
from src.config.settings import settings
from src.google.calendar_manager import GoogleCalendarManager
from src.notion.notion_manager import NotionManager
from src.scraper.announcement_scraper import AnnouncementScraper
from src.telegram_bot.bot import UltronBot


class TaskScheduler:
    """Manages scheduled tasks and reminders."""

    def __init__(self) -> None:
        self.scheduler = AsyncIOScheduler()
        self.notion = NotionManager()
        self.calendar = GoogleCalendarManager()
        self.bot = UltronBot()
        self.chat_handler = ChatHandler()

        self.seen_announcements_path = settings.DATA_DIR / "announcements_seen.json"
        self.seen_announcements: Set[str] = self._load_seen_announcements()

    # ------------------------------------------------------------------ #
    # Scheduler orchestration
    # ------------------------------------------------------------------ #
    def start(self) -> None:
        """Start all scheduled jobs."""
        self.scheduler.add_job(
            self.check_announcements,
            CronTrigger(hour="*"),
            id="check_announcements",
            replace_existing=True,
        )
        self.scheduler.add_job(
            self.check_assignment_reminders,
            CronTrigger(hour="9,18"),
            id="assignment_reminders",
            replace_existing=True,
        )
        self.scheduler.add_job(
            self.check_exam_reminders,
            CronTrigger(hour="9"),
            id="exam_reminders",
            replace_existing=True,
        )
        self.scheduler.add_job(
            self.send_daily_schedule,
            CronTrigger(hour="7", minute="30"),
            id="daily_schedule",
            replace_existing=True,
        )
        self.scheduler.add_job(
            self.send_weekly_summary,
            CronTrigger(day_of_week="sun", hour="20"),
            id="weekly_summary",
            replace_existing=True,
        )

        self.scheduler.start()
        logger.info("Task scheduler started")

    def shutdown(self) -> None:
        """Shutdown the scheduler."""
        self.scheduler.shutdown()
        logger.info("Task scheduler stopped")

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _load_seen_announcements(self) -> Set[str]:
        if not self.seen_announcements_path.exists():
            return set()
        try:
            data = json.loads(self.seen_announcements_path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return set(data)
        except json.JSONDecodeError:
            logger.warning("Could not decode announcements cache; starting fresh")
        return set()

    def _save_seen_announcements(self) -> None:
        try:
            payload = sorted(self.seen_announcements)
            self.seen_announcements_path.write_text(
                json.dumps(payload, indent=2), encoding="utf-8"
            )
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("Failed to persist announcements cache: %s", exc)

    def _announcement_id(self, announcement: Dict[str, str]) -> str:
        return announcement.get("link") or f"{announcement['title']}|{announcement.get('date', '')}"

    async def _summarize_announcement(self, announcement: Dict[str, str], text: str) -> str:
        prompt = (
            "You are Ultron, an academic assistant supporting a student at their university. "
            "Read the university announcement below and craft a short direct message for the student. "
            "Keep it to at most two sentences, start with 'Hey,' and emphasise the key action, important "
            "dates, and where to follow up. Keep the tone encouraging and clear. Do not include markdown headings."
            f"\n\nAnnouncement title: {announcement['title']}\n"
            f"Announcement date: {announcement.get('date', 'Unknown')}\n"
            f"Announcement text:\n{text.strip()}"
        )
        try:
            self.chat_handler.reset_conversation()
            return await self.chat_handler.get_response(prompt)
        except Exception as exc:
            logger.error("Failed to get AI summary for announcement '%s': %s", announcement["title"], exc)
            snippet = text.strip()[:200]
            return (
                f"Hey, yeni bir duyuru var: {announcement['title']} "
                f"({announcement.get('date', 'tarih bilinmiyor')}). {snippet}..."
            )

    def _get_assignments(self) -> List[Dict]:
        if self.calendar.client:
            return self.calendar.get_assignments()
        return self.notion.get_assignments()

    def _get_exams(self) -> List[Dict]:
        if self.calendar.client:
            return self.calendar.get_exams()
        return self.notion.get_exams()

    def _get_schedule(self):
        if self.calendar.client:
            return self.calendar.get_weekly_events()
        return self.notion.get_weekly_schedule()

    # ------------------------------------------------------------------ #
    # Jobs
    # ------------------------------------------------------------------ #
    async def check_announcements(self) -> None:
        """Fetch announcements, summarise unseen items, and send via Telegram."""
        try:
            logger.info("Checking for new announcements...")
            scraper = AnnouncementScraper()
            announcements = scraper.scrape()

            new_items: List[Dict[str, str]] = []
            for announcement in announcements:
                identifier = self._announcement_id(announcement)
                if identifier not in self.seen_announcements:
                    new_items.append(announcement)

            if not new_items:
                logger.info("No new announcements found")
                return

            logger.info("Sending %s new announcement summaries", len(new_items))
            for announcement in new_items:
                identifier = self._announcement_id(announcement)
                detail_text = ""
                if announcement.get("link"):
                    detail_text = scraper.fetch_full_content(announcement["link"]) or ""
                if not detail_text:
                    detail_text = announcement.get("content") or ""

                summary = await self._summarize_announcement(announcement, detail_text)
                message = summary.strip()
                if announcement.get("link"):
                    message += f"\n\nDetay: {announcement['link']}"

                await self.bot.send_message(message)
                self.seen_announcements.add(identifier)

            self._save_seen_announcements()
        except Exception as exc:
            logger.error("Error checking announcements: %s", exc)

    async def check_assignment_reminders(self) -> None:
        """Send assignment reminders for upcoming deadlines."""
        try:
            logger.info("Checking assignment reminders...")
            assignments = self._get_assignments()
            now = datetime.now()

            for assignment in assignments:
                due_date_str = assignment.get("due_date") or assignment.get("date")
                if not due_date_str:
                    continue

                try:
                    due_date = datetime.fromisoformat(due_date_str.replace("Z", "+00:00"))
                except ValueError:
                    logger.debug("Skipping assignment with unparsable date: %s", assignment.get("title"))
                    continue

                days_until_due = (due_date - now).days
                if days_until_due not in {7, 3, 1}:
                    continue

                course_name = assignment.get("class") or assignment.get("course") or "Course TBA"
                status = assignment.get("status") or "Pending"
                message = (
                    f"*Assignment Reminder*\n\n"
                    f"{assignment['title']}\n"
                    f"Class: {course_name}\n"
                    f"Due in: {days_until_due} day{'s' if days_until_due != 1 else ''}\n"
                    f"Status: {status}"
                )
                if assignment.get("description"):
                    snippet = assignment["description"].strip()[:200]
                    message += f"\nDetails: {snippet}"

                await self.bot.send_reminder(assignment["title"], message)
                logger.info("Sent assignment reminder for %s", assignment["title"])
        except Exception as exc:
            logger.error("Error checking assignment reminders: %s", exc)

    async def check_exam_reminders(self) -> None:
        """Send exam reminders for upcoming exams."""
        try:
            logger.info("Checking exam reminders...")
            exams = self._get_exams()
            now = datetime.now()

            for exam in exams:
                exam_date_str = exam.get("date") or exam.get("due_date")
                if not exam_date_str:
                    continue

                try:
                    exam_date = datetime.fromisoformat(exam_date_str.replace("Z", "+00:00"))
                except ValueError:
                    logger.debug("Skipping exam with unparsable date: %s", exam.get("title"))
                    continue

                days_until_exam = (exam_date - now).days
                if days_until_exam not in {14, 7, 3, 1}:
                    continue

                course_name = exam.get("class") or exam.get("course") or "Course TBA"
                location = exam.get("location") or "Location TBA"
                message = (
                    f"*Exam Reminder*\n\n"
                    f"{exam['title']}\n"
                    f"Class: {course_name}\n"
                    f"Date: {exam_date_str}\n"
                    f"In {days_until_exam} day{'s' if days_until_exam != 1 else ''}\n"
                    f"Location: {location}"
                )
                if days_until_exam <= 3:
                    message += "\nTime to focus on revision!"

                await self.bot.send_reminder(f"Exam: {exam['title']}", message)
                logger.info("Sent exam reminder for %s", exam["title"])
        except Exception as exc:
            logger.error("Error checking exam reminders: %s", exc)

    async def send_daily_schedule(self) -> None:
        """Send the daily class schedule."""
        try:
            logger.info("Sending daily schedule...")
            schedule = self._get_schedule()
            today = datetime.now().strftime("%A")
            today_classes = schedule.get(today, [])

            if not today_classes:
                message = f"*{today}'s Schedule*\n\nNo classes today. Enjoy your time off!"
                await self.bot.send_message(message)
                logger.info("Daily schedule sent (no classes)")
                return

            lines = [f"*{today}'s Schedule*"]
            for cls in today_classes:
                name = cls.get("name") or cls.get("title") or "Class"
                schedule_text = cls.get("schedule") or ""
                if not schedule_text:
                    start_time = cls.get("start_time") or ""
                    end_time = cls.get("end_time") or ""
                    schedule_text = f"{start_time} - {end_time}".strip(" -")
                instructor = cls.get("instructor") or cls.get("description") or "Instructor TBA"
                room = cls.get("room") or "Room TBA"
                lines.append(f"- {name}")
                lines.append(f"  Time: {schedule_text or 'TBD'}")
                lines.append(f"  Instructor: {instructor}")
                lines.append(f"  Room: {room}\n")

            await self.bot.send_message("\n".join(lines).strip())
            logger.info("Daily schedule sent")
        except Exception as exc:
            logger.error("Error sending daily schedule: %s", exc)

    async def send_weekly_summary(self) -> None:
        """Send a weekly academic summary."""
        try:
            logger.info("Sending weekly summary...")
            assignments = self._get_assignments()
            exams = self._get_exams()

            lines = ["*Weekly Summary*", "", "Assignments:"]
            if assignments:
                for assignment in assignments[:5]:
                    due_label = assignment.get("due_date") or assignment.get("date") or "TBD"
                    lines.append(f"- {assignment['title']} (due {due_label})")
            else:
                lines.append("No upcoming assignments.")

            lines.append("")
            lines.append("Exams:")
            if exams:
                for exam in exams[:3]:
                    date_label = exam.get("date") or exam.get("due_date") or "TBD"
                    lines.append(f"- {exam['title']} ({date_label})")
            else:
                lines.append("No upcoming exams.")

            lines.append("")
            lines.append("Keep up the great work!")

            await self.bot.send_message("\n".join(lines))
            logger.info("Weekly summary sent")
        except Exception as exc:
            logger.error("Error sending weekly summary: %s", exc)


# Example usage
if __name__ == "__main__":  # pragma: no cover - manual testing helper
    import asyncio

    async def test_scheduler():
        scheduler = TaskScheduler()
        scheduler.start()
        try:
            while True:
                await asyncio.sleep(60)
        except KeyboardInterrupt:
            scheduler.shutdown()

    asyncio.run(test_scheduler())
