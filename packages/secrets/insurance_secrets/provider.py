"""Secret provider abstractions.

Production adapters can implement AWS Secrets Manager, HashiCorp Vault, SOPS,
or Kubernetes Secret backends behind this interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
import os


class SecretProvider(ABC):
    """Abstract secret provider boundary."""

    @abstractmethod
    def get(self, name: str) -> str | None:
        """Return a secret value by logical name."""

    def require(self, name: str) -> str:
        value = self.get(name)
        if not value:
            raise RuntimeError(f"Required secret is missing: {name}")
        return value


class EnvSecretProvider(SecretProvider):
    """Environment-variable secret provider for local and CI deployments."""

    def get(self, name: str) -> str | None:
        return os.getenv(name)
