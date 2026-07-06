"""create project, satellite_image, prediction, report tables

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-07-04 00:00:00.000000
"""

from collections.abc import Sequence

import geoalchemy2
import sqlalchemy as sa
from alembic import op

revision: str = "b2c3d4e5f6a7"
down_revision: str | None = "a1b2c3d4e5f6"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    """Create projects, satellite_images, predictions, reports, and their join table."""
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    op.create_table(
        "projects",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "owner_id",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("ACTIVE", "ARCHIVED", "COMPLETED", name="project_status"),
            nullable=False,
            server_default="ACTIVE",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_projects_owner_id", "projects", ["owner_id"])
    op.create_index("ix_projects_owner_id_status", "projects", ["owner_id", "status"])

    op.create_table(
        "satellite_images",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "project_id",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("file_path", sa.String(length=512), nullable=False),
        sa.Column("file_size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("sensor_type", sa.String(length=100), nullable=True),
        sa.Column("crs", sa.String(length=50), nullable=True),
        sa.Column("width_px", sa.Integer(), nullable=True),
        sa.Column("height_px", sa.Integer(), nullable=True),
        sa.Column("band_count", sa.Integer(), nullable=True),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "footprint",
            geoalchemy2.Geometry(geometry_type="POLYGON", srid=4326, spatial_index=False),
            nullable=True,
        ),
        sa.Column(
            "status",
            sa.Enum("UPLOADED", "PROCESSING", "PROCESSED", "FAILED", name="image_status"),
            nullable=False,
            server_default="UPLOADED",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_satellite_images_project_id", "satellite_images", ["project_id"])
    op.create_index(
        "ix_satellite_images_project_id_status", "satellite_images", ["project_id", "status"]
    )
    op.create_index(
        "ix_satellite_images_footprint",
        "satellite_images",
        ["footprint"],
        postgresql_using="gist",
    )

    op.create_table(
        "predictions",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "satellite_image_id",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("satellite_images.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("model_name", sa.String(length=255), nullable=False),
        sa.Column("model_version", sa.String(length=50), nullable=True),
        sa.Column(
            "prediction_type",
            sa.Enum(
                "SEGMENTATION",
                "LAND_COVER_CLASSIFICATION",
                "VEGETATION_INDEX",
                "CROP_ANALYSIS",
                name="prediction_type",
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("PENDING", "RUNNING", "COMPLETED", "FAILED", name="prediction_status"),
            nullable=False,
            server_default="PENDING",
        ),
        sa.Column(
            "result_geometry",
            geoalchemy2.Geometry(geometry_type="GEOMETRY", srid=4326, spatial_index=False),
            nullable=True,
        ),
        sa.Column("result_data", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("error_message", sa.String(length=1000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_predictions_satellite_image_id", "predictions", ["satellite_image_id"])
    op.create_index(
        "ix_predictions_satellite_image_id_type",
        "predictions",
        ["satellite_image_id", "prediction_type"],
    )
    op.create_index(
        "ix_predictions_result_geometry", "predictions", ["result_geometry"], postgresql_using="gist"
    )

    op.create_table(
        "reports",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "project_id",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "generated_by",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column(
            "format",
            sa.Enum("PDF", "DOCX", "HTML", name="report_format"),
            nullable=False,
            server_default="PDF",
        ),
        sa.Column(
            "status",
            sa.Enum("PENDING", "GENERATING", "COMPLETED", "FAILED", name="report_status"),
            nullable=False,
            server_default="PENDING",
        ),
        sa.Column("file_path", sa.String(length=512), nullable=True),
        sa.Column("error_message", sa.String(length=1000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_reports_project_id", "reports", ["project_id"])
    op.create_index("ix_reports_generated_by", "reports", ["generated_by"])
    op.create_index("ix_reports_project_id_status", "reports", ["project_id", "status"])

    op.create_table(
        "report_predictions",
        sa.Column(
            "report_id",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("reports.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "prediction_id",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("predictions.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )


def downgrade() -> None:
    """Drop all tables and enum types created by this migration, in dependency order."""
    op.drop_table("report_predictions")

    op.drop_index("ix_reports_project_id_status", table_name="reports")
    op.drop_index("ix_reports_generated_by", table_name="reports")
    op.drop_index("ix_reports_project_id", table_name="reports")
    op.drop_table("reports")
    sa.Enum(name="report_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="report_format").drop(op.get_bind(), checkfirst=True)

    op.drop_index("ix_predictions_result_geometry", table_name="predictions")
    op.drop_index("ix_predictions_satellite_image_id_type", table_name="predictions")
    op.drop_index("ix_predictions_satellite_image_id", table_name="predictions")
    op.drop_table("predictions")
    sa.Enum(name="prediction_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="prediction_type").drop(op.get_bind(), checkfirst=True)

    op.drop_index("ix_satellite_images_footprint", table_name="satellite_images")
    op.drop_index("ix_satellite_images_project_id_status", table_name="satellite_images")
    op.drop_index("ix_satellite_images_project_id", table_name="satellite_images")
    op.drop_table("satellite_images")
    sa.Enum(name="image_status").drop(op.get_bind(), checkfirst=True)

    op.drop_index("ix_projects_owner_id_status", table_name="projects")
    op.drop_index("ix_projects_owner_id", table_name="projects")
    op.drop_table("projects")
    sa.Enum(name="project_status").drop(op.get_bind(), checkfirst=True)
