from __future__ import annotations

import subprocess
from pathlib import Path

from .models import ServiceStatus


class LocalSystemChecks:
    """Local command and file existence checks."""

    def __init__(self, timeout: float):
        self.timeout = timeout

    def check_command_exists(self, name: str, command: str) -> ServiceStatus:
        """Check if a command-line tool exists."""
        try:
            result = subprocess.run(
                ["which", command],
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )

            if result.returncode == 0:
                path = result.stdout.strip()
                return ServiceStatus(
                    name=name,
                    healthy=True,
                    url=path,
                    details={"path": path},
                )

            return ServiceStatus(name=name, healthy=False, url="", error="Command not found")
        except subprocess.TimeoutExpired:
            return ServiceStatus(
                name=name,
                healthy=False,
                url="",
                error="Timeout checking command",
            )
        except Exception as e:
            return ServiceStatus(name=name, healthy=False, url="", error=str(e))

    def check_file_exists(self, name: str, path: str) -> ServiceStatus:
        """Check if a file exists."""
        file_path = Path(path)

        if file_path.exists():
            stat = file_path.stat()
            return ServiceStatus(
                name=name,
                healthy=True,
                url=str(file_path),
                details={"size": stat.st_size, "modified": stat.st_mtime},
            )

        return ServiceStatus(
            name=name,
            healthy=False,
            url=str(file_path),
            error="File not found",
        )
