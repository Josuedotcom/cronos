"""Create base schema for Cronos MVP.

Revision ID: 001_create_base_schema
Revises:
Create Date: 2026-04-16
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "001_create_base_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    op.create_table(
        "companies",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("subdomain", sa.String(length=100), nullable=False, unique=True),
        sa.Column(
            "timezone",
            sa.String(length=50),
            nullable=True,
            server_default=sa.text("'America/Bogota'"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=True,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=True,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index("idx_companies_subdomain", "companies", ["subdomain"])

    op.create_table(
        "suborganizations",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "company_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("companies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column(
            "parent_suborganization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("suborganizations.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=True,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=True,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index("idx_suborganizations_company", "suborganizations", ["company_id"])
    op.create_index(
        "idx_suborganizations_parent", "suborganizations", ["parent_suborganization_id"]
    )

    op.create_table(
        "areas",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "company_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("companies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "suborganization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("suborganizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("manager_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=True,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=True,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index("idx_areas_company", "areas", ["company_id"])
    op.create_index("idx_areas_suborganization", "areas", ["suborganization_id"])

    op.create_table(
        "workers",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "company_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("companies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "suborganization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("suborganizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "area_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("areas.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("cedula", sa.String(length=20), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=100), nullable=True),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column(
            "contract_type",
            sa.String(length=20),
            nullable=True,
            server_default=sa.text("'standard'"),
        ),
        sa.Column("hourly_rate", sa.Numeric(10, 2), nullable=False),
        sa.Column("hire_date", sa.Date(), nullable=False),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=True,
            server_default=sa.text("'active'"),
        ),
        sa.Column(
            "role",
            sa.String(length=20),
            nullable=True,
            server_default=sa.text("'worker'"),
        ),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=True,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=True,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.CheckConstraint(
            "contract_type IN ('standard', 'shift_36h')",
            name="ck_workers_contract_type",
        ),
        sa.CheckConstraint(
            "status IN ('active', 'inactive', 'on_leave')", name="ck_workers_status"
        ),
        sa.CheckConstraint(
            "role IN ('worker', 'manager', 'hr_admin', 'system_admin')",
            name="ck_workers_role",
        ),
        sa.UniqueConstraint("company_id", "cedula", name="uq_workers_company_cedula"),
    )
    op.create_index("idx_workers_company", "workers", ["company_id"])
    op.create_index("idx_workers_area", "workers", ["area_id"])
    op.create_index("idx_workers_email", "workers", ["email"])
    op.create_index("idx_workers_company_area", "workers", ["company_id", "area_id"])

    op.create_foreign_key(
        "fk_areas_manager_id",
        "areas",
        "workers",
        ["manager_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_table(
        "shift_templates",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "company_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("companies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "suborganization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("suborganizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "area_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("areas.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("code", sa.String(length=10), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "is_active", sa.Boolean(), nullable=True, server_default=sa.text("TRUE")
        ),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=True,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=True,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.UniqueConstraint("area_id", "code", name="uq_shift_templates_area_code"),
    )
    op.create_index("idx_shift_templates_area", "shift_templates", ["area_id"])
    op.create_index("idx_shift_templates_company", "shift_templates", ["company_id"])

    op.create_table(
        "shift_assignments",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "company_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("companies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "worker_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("workers.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "shift_template_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("shift_templates.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("assignment_date", sa.Date(), nullable=False),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=True,
            server_default=sa.text("'scheduled'"),
        ),
        sa.Column(
            "is_overtime_shift",
            sa.Boolean(),
            nullable=True,
            server_default=sa.text("FALSE"),
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_by_worker_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("workers.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=True,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=True,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.CheckConstraint(
            "status IN ('scheduled', 'completed', 'absent', 'swapped')",
            name="ck_shift_assignments_status",
        ),
        sa.UniqueConstraint(
            "worker_id", "assignment_date", name="uq_shift_assignments_worker_date"
        ),
    )
    op.create_index("idx_shift_assignments_worker", "shift_assignments", ["worker_id"])
    op.create_index(
        "idx_shift_assignments_date", "shift_assignments", ["assignment_date"]
    )
    op.create_index(
        "idx_shift_assignments_company", "shift_assignments", ["company_id"]
    )
    op.create_index(
        "idx_shift_assignments_worker_date",
        "shift_assignments",
        ["worker_id", "assignment_date"],
    )
    op.create_index(
        "idx_shift_assignments_template", "shift_assignments", ["shift_template_id"]
    )

    op.create_table(
        "timesheet_days",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "company_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("companies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "worker_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("workers.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("timesheet_date", sa.Date(), nullable=False),
        sa.Column(
            "ordinary_hours",
            sa.Numeric(5, 2),
            nullable=True,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "night_hours", sa.Numeric(5, 2), nullable=True, server_default=sa.text("0")
        ),
        sa.Column(
            "sunday_day_hours",
            sa.Numeric(5, 2),
            nullable=True,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "sunday_night_hours",
            sa.Numeric(5, 2),
            nullable=True,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "overtime_day", sa.Numeric(5, 2), nullable=True, server_default=sa.text("0")
        ),
        sa.Column(
            "overtime_night",
            sa.Numeric(5, 2),
            nullable=True,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "overtime_sunday_day",
            sa.Numeric(5, 2),
            nullable=True,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "overtime_sunday_night",
            sa.Numeric(5, 2),
            nullable=True,
            server_default=sa.text("0"),
        ),
        sa.Column("total_regular_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("total_surcharge_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("total_gross_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=True,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=True,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.UniqueConstraint(
            "worker_id", "timesheet_date", name="uq_timesheet_days_worker_date"
        ),
    )
    op.create_index("idx_timesheet_days_worker", "timesheet_days", ["worker_id"])
    op.create_index("idx_timesheet_days_date", "timesheet_days", ["timesheet_date"])
    op.create_index(
        "idx_timesheet_days_worker_date",
        "timesheet_days",
        ["worker_id", "timesheet_date"],
    )

    op.create_table(
        "holiday_calendar",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "company_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("companies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("holiday_date", sa.Date(), nullable=False),
        sa.Column("holiday_name", sa.String(length=100), nullable=False),
        sa.Column(
            "is_public_holiday",
            sa.Boolean(),
            nullable=True,
            server_default=sa.text("TRUE"),
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=True,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.UniqueConstraint(
            "company_id", "holiday_date", name="uq_holiday_calendar_company_date"
        ),
    )
    op.create_index("idx_holiday_calendar_company", "holiday_calendar", ["company_id"])
    op.create_index("idx_holiday_calendar_date", "holiday_calendar", ["holiday_date"])

    op.create_table(
        "surcharge_rules",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "company_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("companies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("surcharge_type", sa.String(length=50), nullable=False),
        sa.Column("percentage", sa.Numeric(5, 2), nullable=False),
        sa.Column("effective_from", sa.Date(), nullable=False),
        sa.Column("effective_to", sa.Date(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=True,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=True,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.UniqueConstraint(
            "company_id",
            "surcharge_type",
            "effective_from",
            name="uq_surcharge_rules_company_type_effective_from",
        ),
    )
    op.create_index("idx_surcharge_rules_company", "surcharge_rules", ["company_id"])


def downgrade() -> None:
    op.drop_index("idx_surcharge_rules_company", table_name="surcharge_rules")
    op.drop_table("surcharge_rules")

    op.drop_index("idx_holiday_calendar_date", table_name="holiday_calendar")
    op.drop_index("idx_holiday_calendar_company", table_name="holiday_calendar")
    op.drop_table("holiday_calendar")

    op.drop_index("idx_timesheet_days_worker_date", table_name="timesheet_days")
    op.drop_index("idx_timesheet_days_date", table_name="timesheet_days")
    op.drop_index("idx_timesheet_days_worker", table_name="timesheet_days")
    op.drop_table("timesheet_days")

    op.drop_index("idx_shift_assignments_template", table_name="shift_assignments")
    op.drop_index("idx_shift_assignments_worker_date", table_name="shift_assignments")
    op.drop_index("idx_shift_assignments_company", table_name="shift_assignments")
    op.drop_index("idx_shift_assignments_date", table_name="shift_assignments")
    op.drop_index("idx_shift_assignments_worker", table_name="shift_assignments")
    op.drop_table("shift_assignments")

    op.drop_index("idx_shift_templates_company", table_name="shift_templates")
    op.drop_index("idx_shift_templates_area", table_name="shift_templates")
    op.drop_table("shift_templates")

    op.drop_constraint("fk_areas_manager_id", "areas", type_="foreignkey")
    op.drop_index("idx_workers_company_area", table_name="workers")
    op.drop_index("idx_workers_email", table_name="workers")
    op.drop_index("idx_workers_area", table_name="workers")
    op.drop_index("idx_workers_company", table_name="workers")
    op.drop_table("workers")

    op.drop_index("idx_areas_suborganization", table_name="areas")
    op.drop_index("idx_areas_company", table_name="areas")
    op.drop_table("areas")

    op.drop_index("idx_suborganizations_parent", table_name="suborganizations")
    op.drop_index("idx_suborganizations_company", table_name="suborganizations")
    op.drop_table("suborganizations")

    op.drop_index("idx_companies_subdomain", table_name="companies")
    op.drop_table("companies")
