from __future__ import annotations

import asyncio
from contextlib import suppress
from datetime import datetime, timezone
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import select

from ..connectors.announcements import RSSAnnouncementConnector, StaticAnnouncementScraper
from ..connectors.email import GmailRestConnector, IMAPXOauthConnector
from ..connectors.notion import NotionConnector
from ..db.base import SessionLocal, init_engine
from ..db.models import Deadline, DeadlineStatus
from ..db.repo import Repository
from ..extractors.pipeline import ExtractionPipeline
from ..settings import settings
from ..utils.logging import get_logger


logger = get_logger(__name__)


class SyncService:
    def __init__(self) -> None:
        init_engine()

    def sync_email(self) -> None:
        connector = self._build_email_connector()
        if connector is None:
            logger.info("Email connector not configured; skipping email sync")
            return
        session = SessionLocal()
        repo = Repository(session)
        pipeline = ExtractionPipeline(repo)
        try:
            messages = connector.sync(repo)
            pipeline.ingest_emails(messages, source=self._email_source_name(connector))
            self._record_sync(repo, "sync:email:last_run")
            session.commit()
            logger.info("Email sync committed")
        except Exception:
            session.rollback()
            logger.exception("Email sync failed; transaction rolled back")
            raise
        finally:
            session.close()

    def sync_announcements(self) -> None:
        session = SessionLocal()
        repo = Repository(session)
        pipeline = ExtractionPipeline(repo)
        total_items = 0
        rss = RSSAnnouncementConnector()
        try:
            rss_items = rss.fetch()
        finally:
            rss.close()
        if rss_items:
            pipeline.ingest_announcements(rss_items, source="rss")
            total_items += len(rss_items)

        scraper = StaticAnnouncementScraper()
        try:
            static_items = scraper.fetch()
        finally:
            scraper.close()
        if static_items:
            pipeline.ingest_announcements(static_items, source="scrape")
            total_items += len(static_items)
        try:
            self._record_sync(repo, "sync:announcements:last_run")
            session.commit()
            logger.info("Announcement sync committed (%s items)", total_items)
        except Exception:
            session.rollback()
            logger.exception("Announcement sync failed")
            raise
        finally:
            session.close()

    def sync_notion(self) -> None:
        session = SessionLocal()
        repo = Repository(session)
        pipeline = ExtractionPipeline(repo)
        try:
            connector = NotionConnector()
        except ValueError:
            session.close()
            logger.info("Notion connector not configured; skipping notion sync")
            return
        try:
            pages = connector.fetch()
            pipeline.ingest_notion(pages, source="notion")
            self._record_sync(repo, "sync:notion:last_run")
            session.commit()
            logger.info("Notion sync committed (%s pages)", len(pages))
        except Exception:
            session.rollback()
            logger.exception("Notion sync failed")
            raise
        finally:
            session.close()

    def reconcile_deadlines(self) -> None:
        session = SessionLocal()
        repo = Repository(session)
        now = datetime.now(timezone.utc)
        try:
            overdue = 0
            stmt = select(Deadline).where(Deadline.status == DeadlineStatus.OPEN)
            for deadline in session.execute(stmt).scalars():
                if deadline.due_ts < now:
                    deadline.status = DeadlineStatus.OVERDUE
                    overdue += 1
            self._record_sync(repo, "sync:deadlines:last_run")
            session.commit()
            if overdue:
                logger.info("Marked %s deadlines as overdue", overdue)
        except Exception:
            session.rollback()
            logger.exception("Deadline reconciliation failed")
            raise
        finally:
            session.close()

    def _build_email_connector(self):
        with suppress(ValueError):
            return GmailRestConnector()
        with suppress(ValueError):
            return IMAPXOauthConnector()
        return None

    @staticmethod
    def _email_source_name(connector) -> str:
        if isinstance(connector, GmailRestConnector):
            return "gmail"
        return "imap"

    @staticmethod
    def _record_sync(repo: Repository, key: str) -> None:
        repo.set_sync_cursor(key, datetime.now(timezone.utc).isoformat())


def create_scheduler() -> AsyncIOScheduler:
    service = SyncService()
    scheduler = AsyncIOScheduler(timezone=settings.scheduler_tz)
    scheduler.add_job(service.sync_email, IntervalTrigger(minutes=10), id="email_sync", coalesce=True, max_instances=1)
    scheduler.add_job(service.sync_announcements, IntervalTrigger(minutes=20), id="announcements_sync", coalesce=True, max_instances=1)
    scheduler.add_job(service.sync_notion, IntervalTrigger(minutes=30), id="notion_sync", coalesce=True, max_instances=1)
    scheduler.add_job(service.reconcile_deadlines, IntervalTrigger(hours=1), id="deadline_reconcile", coalesce=True, max_instances=1)
    scheduler.sync_service = service  # type: ignore[attr-defined]
    return scheduler


def main() -> None:
    scheduler = create_scheduler()
    scheduler.start()
    logger.info("Scheduler started")
    loop = asyncio.get_event_loop()
    try:
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopping...")
    finally:
        scheduler.shutdown()


if __name__ == "__main__":
    main()

