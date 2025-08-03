"""Helper utilities for working with Docker."""

import subprocess
from typing import Tuple

def is_docker_available() -> Tuple[bool, str]:
    """Check if Docker is installed and accessible.

    Returns:
        Tuple of (available, message)
    """
    try:
        result = subprocess.run(
            ["docker", "version"],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        return False, result.stderr.strip() or "docker command failed"
    except FileNotFoundError:
        return False, "docker executable not found"
    except Exception as exc:  # pragma: no cover - unexpected errors
        return False, str(exc)
