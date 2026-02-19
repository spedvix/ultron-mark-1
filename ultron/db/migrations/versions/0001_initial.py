"""Initial Ultron schema"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    artifact_kind = sa.Enum(
        "email",
        "announcement",
        "notion",
        "syllabus",
        "assignment",
        "exam",
        "policy",
        name="artifact_kind",
    )
    deadline_status = sa.Enum("open", "done", "overdue", "cancelled", name="deadline_status")

    artifact_kind.create(op.get_bind(), checkfirst=True)
    deadline_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "courses",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("dept", sa.String(length=128), nullable=True),
    )
    op.create_index("ix_courses_code", "courses", ["code"])

    op.create_table(
        "artifacts",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("kind", artifact_kind, nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("url", sa.String(length=1024), nullable=False),
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.Column("source_loc", sa.String(length=255), nullable=True),
        sa.Column("published_ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("discovered_ts", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("hash", sa.String(length=64), nullable=False),
    )
    op.create_index("ix_artifacts_title", "artifacts", ["title"])
    op.create_index("ix_artifacts_url", "artifacts", ["url"])
    op.create_index("ix_artifacts_published_ts", "artifacts", ["published_ts"])
    op.create_index("ix_artifacts_discovered_ts", "artifacts", ["discovered_ts"])
    op.create_index("ix_artifacts_source_hash", "artifacts", ["source", "hash"], unique=True)
    op.create_unique_constraint("uq_artifacts_hash", "artifacts", ["hash"])

    op.create_table(
        "deadlines",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("course_id", sa.String(length=36), sa.ForeignKey("courses.id"), nullable=True),
        sa.Column("artifact_id", sa.String(length=36), sa.ForeignKey("artifacts.id"), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("due_ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tz", sa.String(length=64), nullable=False, server_default=sa.text("'Europe/Istanbul'")),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False, server_default=sa.text("0.0")),
        sa.Column("status", deadline_status, nullable=False, server_default=sa.text("'open'")),
    )
    op.create_index("ix_deadlines_course_id", "deadlines", ["course_id"])
    op.create_index("ix_deadlines_artifact_id", "deadlines", ["artifact_id"])
    op.create_index("ix_deadlines_due_ts", "deadlines", ["due_ts"])

    op.create_table(
        "sync_state",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("source", sa.String(length=64), nullable=False, unique=True),
        sa.Column("cursor", sa.String(length=255), nullable=True),
        sa.Column("extra", sa.Text(), nullable=True),
        sa.Column("updated_ts", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "links",
        sa.Column("artifact_id", sa.String(length=36), sa.ForeignKey("artifacts.id"), primary_key=True),
        sa.Column("href", sa.String(length=1024), primary_key=True),
        sa.Column("label", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("sync_state")
    op.drop_table("links")
    op.drop_index("ix_deadlines_due_ts", table_name="deadlines")
    op.drop_index("ix_deadlines_artifact_id", table_name="deadlines")
    op.drop_index("ix_deadlines_course_id", table_name="deadlines")
    op.drop_table("deadlines")
    op.drop_constraint("uq_artifacts_hash", "artifacts", type_="unique")
    op.drop_index("ix_artifacts_source_hash", table_name="artifacts")
    op.drop_index("ix_artifacts_discovered_ts", table_name="artifacts")
    op.drop_index("ix_artifacts_published_ts", table_name="artifacts")
    op.drop_index("ix_artifacts_url", table_name="artifacts")
    op.drop_index("ix_artifacts_title", table_name="artifacts")
    op.drop_table("artifacts")
    op.drop_index("ix_courses_code", table_name="courses")
    op.drop_table("courses")

    sa.Enum(name="deadline_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="artifact_kind").drop(op.get_bind(), checkfirst=True)
