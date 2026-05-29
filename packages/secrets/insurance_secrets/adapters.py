"""Optional production secret provider adapters."""

from __future__ import annotations

import json
from pathlib import Path

from insurance_secrets.provider import SecretProvider


class FileSecretProvider(SecretProvider):
    """Load secrets from a JSON file, suitable for SOPS-decrypted runtime files."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.data = json.loads(self.path.read_text(encoding="utf-8"))

    def get(self, name: str) -> str | None:
        value = self.data.get(name)
        return str(value) if value is not None else None


class AwsSecretsManagerProvider(SecretProvider):
    """AWS Secrets Manager provider using boto3 when installed."""

    def __init__(self, region_name: str | None = None, prefix: str = ""):
        try:
            import boto3
        except ImportError as exc:
            raise RuntimeError("Install boto3 to use AwsSecretsManagerProvider") from exc
        self.client = boto3.client("secretsmanager", region_name=region_name)
        self.prefix = prefix

    def get(self, name: str) -> str | None:
        secret_id = f"{self.prefix}{name}"
        response = self.client.get_secret_value(SecretId=secret_id)
        return response.get("SecretString")


class VaultSecretProvider(SecretProvider):
    """HashiCorp Vault KV provider using hvac when installed."""

    def __init__(self, url: str, token: str, mount_point: str = "secret", base_path: str = ""):
        try:
            import hvac
        except ImportError as exc:
            raise RuntimeError("Install hvac to use VaultSecretProvider") from exc
        self.client = hvac.Client(url=url, token=token)
        self.mount_point = mount_point
        self.base_path = base_path.strip("/")

    def get(self, name: str) -> str | None:
        path = f"{self.base_path}/{name}" if self.base_path else name
        response = self.client.secrets.kv.v2.read_secret_version(path=path, mount_point=self.mount_point)
        data = response.get("data", {}).get("data", {})
        value = data.get(name) or data.get("value")
        return str(value) if value is not None else None
