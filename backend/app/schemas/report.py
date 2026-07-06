"""Pydantic schemas for Report create/response payloads."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.report import ReportFormat, ReportStatus


class ReportCreate(BaseModel):
    """Payload required to request generation of a new report."""

    project_id: uuid.UUID
    title: str = Field(min_length=1, max_length=255)
    format: ReportFormat = ReportFormat.PDF
    prediction_ids: list[uuid.UUID] = Field(default_factory=list)


class ReportResponse(BaseModel):
    """Public representation of a report record."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    generated_by: uuid.UUID | None
    title: str
    format: ReportFormat
    status: ReportStatus
    file_path: str | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime
