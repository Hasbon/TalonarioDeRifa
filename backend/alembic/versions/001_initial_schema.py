"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-10-20

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("username", sa.String(64), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(200), nullable=False),
        sa.Column("role", sa.Enum("admin", "seller", name="userrole"), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_users_username", "users", ["username"])

    op.create_table(
        "raffles",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("primary_prize", sa.Text(), nullable=False),
        sa.Column("alternative_prize_amount", sa.Integer(), nullable=False),
        sa.Column("ticket_price", sa.Integer(), nullable=False),
        sa.Column("draw_date", sa.Date(), nullable=False),
        sa.Column("delivery_datetime", sa.DateTime(timezone=True), nullable=False),
        sa.Column("lottery_name", sa.String(200), nullable=False),
        sa.Column("lottery_draw_reference", sa.String(255), nullable=False),
        sa.Column(
            "status",
            sa.Enum("draft", "active", "closed", "drawn", name="rafflestatus"),
            nullable=False,
        ),
        sa.Column("public_contact", sa.Text(), nullable=False),
        sa.Column("public_rules", sa.Text(), nullable=False),
        sa.Column("privacy_notice", sa.Text(), nullable=False),
        sa.Column("logo_url", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "customers",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("full_name", sa.String(200), nullable=False),
        sa.Column("phone", sa.String(32), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_customers_phone", "customers", ["phone"])

    op.create_table(
        "tickets",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("raffle_id", sa.String(36), sa.ForeignKey("raffles.id"), nullable=False),
        sa.Column("number_code", sa.String(2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("raffle_id", "number_code", name="uq_raffle_number"),
    )

    op.create_table(
        "sales",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("ticket_id", sa.String(36), sa.ForeignKey("tickets.id"), nullable=False),
        sa.Column("customer_id", sa.String(36), sa.ForeignKey("customers.id"), nullable=False),
        sa.Column("seller_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("ticket_price", sa.Integer(), nullable=False),
        sa.Column(
            "commercial_status",
            sa.Enum("active", "cancelled", name="commercialstatus"),
            nullable=False,
        ),
        sa.Column(
            "payment_status",
            sa.Enum("unpaid", "partial", "paid", name="paymentstatussale"),
            nullable=False,
        ),
        sa.Column("payment_due_date", sa.Date(), nullable=True),
        sa.Column("internal_notes", sa.Text(), nullable=True),
        sa.Column("assigned_at", sa.DateTime(timezone=True)),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancellation_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_index(
        "uq_active_sale_per_ticket",
        "sales",
        ["ticket_id"],
        unique=True,
        postgresql_where=sa.text("commercial_status = 'active'"),
        sqlite_where=sa.text("commercial_status = 'active'"),
    )

    op.create_table(
        "payments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("sale_id", sa.String(36), sa.ForeignKey("sales.id"), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("payment_method", sa.String(64), nullable=False),
        sa.Column("payment_reference", sa.String(200), nullable=True),
        sa.Column(
            "status",
            sa.Enum("pending", "confirmed", "voided", name="paymentrecordstatus"),
            nullable=False,
        ),
        sa.Column("registered_by", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("payment_date", sa.DateTime(timezone=True)),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "ticket_public_tokens",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("ticket_id", sa.String(36), sa.ForeignKey("tickets.id"), nullable=False),
        sa.Column("sale_id", sa.String(36), sa.ForeignKey("sales.id"), nullable=True),
        sa.Column("public_token", sa.String(64), nullable=False, unique=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "lottery_results",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("raffle_id", sa.String(36), sa.ForeignKey("raffles.id"), nullable=False),
        sa.Column("lottery_name", sa.String(200), nullable=False),
        sa.Column("draw_reference", sa.String(255), nullable=False),
        sa.Column("draw_date", sa.Date(), nullable=False),
        sa.Column("winning_number", sa.String(32), nullable=False),
        sa.Column("derived_winner_code", sa.String(2), nullable=False),
        sa.Column("official_source_url", sa.String(500), nullable=False),
        sa.Column(
            "verification_status",
            sa.Enum("draft", "verified", "confirmed", name="verificationstatus"),
            nullable=False,
        ),
        sa.Column("verified_by", sa.String(36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("entity_type", sa.String(64), nullable=False),
        sa.Column("entity_id", sa.String(36), nullable=True),
        sa.Column("previous_values", sa.JSON(), nullable=True),
        sa.Column("new_values", sa.JSON(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("lottery_results")
    op.drop_table("ticket_public_tokens")
    op.drop_table("payments")
    op.drop_index("uq_active_sale_per_ticket", table_name="sales")
    op.drop_table("sales")
    op.drop_table("tickets")
    op.drop_table("customers")
    op.drop_table("raffles")
    op.drop_index("ix_users_username", table_name="users")
    op.drop_table("users")
