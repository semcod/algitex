"""AutoFix — backward compatibility shim.

This module re-exports from the new autofix package for backward compatibility.
New code should import directly from algitex.tools.autofix.
"""

# Re-export everything from the new package
from algitex.tools.autofix import (
    AutoFix,
    FixResult,
    Task,
    OllamaBackend,
    AiderBackend,
    ProxyBackend,
)

__all__ = ["AutoFix", "FixResult", "Task", "OllamaBackend", "AiderBackend", "ProxyBackend"]
