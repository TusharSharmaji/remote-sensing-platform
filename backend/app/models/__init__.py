"""SQLAlchemy ORM models package.

All model modules are imported here so that Base.metadata is fully populated
before Alembic autogeneration or Base.metadata.create_all() run.
"""

from app.models.prediction import Prediction, PredictionStatus, PredictionType
from app.models.project import Project, ProjectStatus
from app.models.report import Report, ReportFormat, ReportStatus, report_predictions
from app.models.satellite_image import ImageStatus, SatelliteImage
from app.models.user import User, UserRole

__all__ = [
    "User",
    "UserRole",
    "Project",
    "ProjectStatus",
    "SatelliteImage",
    "ImageStatus",
    "Prediction",
    "PredictionType",
    "PredictionStatus",
    "Report",
    "ReportFormat",
    "ReportStatus",
    "report_predictions",
]
