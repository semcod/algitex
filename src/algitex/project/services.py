"""Service management mixins for Project class."""

from __future__ import annotations

from typing import Optional

from algitex.tools.services import ServiceChecker


class ServiceMixin:
    """Service management functionality for Project."""

    def __init__(self) -> None:
        self.services = ServiceChecker()

    def check_services(self, services: Optional[dict] = None) -> dict:
        """Check status of all services."""
        statuses = self.services.check_all(services)
        return {s.name: s.to_dict() for s in statuses}

    def print_service_status(self, show_details: bool = False) -> None:
        """Print service status in a formatted way."""
        statuses = self.services.check_all()
        self.services.print_status(statuses, show_details)

    def ensure_service(self, service: str, timeout_seconds: int = 60) -> bool:
        """Wait for a service to become healthy."""
        return self.services.wait_for_services([service], timeout_seconds)
