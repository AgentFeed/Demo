from __future__ import annotations


class IntegrationError(RuntimeError):
    """Base error for configured external integrations."""


class IntegrationNotConfigured(IntegrationError):
    """Raised when a real provider was requested without its credentials."""


class IntegrationResponseError(IntegrationError):
    """Raised when an external provider returns an unusable response."""
