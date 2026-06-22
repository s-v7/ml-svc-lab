from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
import json
from typing import Any


def build_request_hash(payload: dict[str, Any]) -> str:
    normalized = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )
    return sha256(normalized.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class IdempotencyRecord:
    key: str
    request_hash: str
    response: dict[str, Any]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.key.strip():
            raise ValueError("idempotency key não pode ser vazia")


class InMemoryIdempotencyStore:
    def __init__(self) -> None:
        self._records: dict[str, IdempotencyRecord] = {}

    def get_response(
        self,
        key: str,
        payload: dict[str, Any],
    ) -> dict[str, Any] | None:
        self._validate_key(key)

        record = self._records.get(key)

        if record is None:
            return None

        request_hash = build_request_hash(payload)

        if record.request_hash != request_hash:
            raise ValueError("idempotency key reutilizada com payload diferente")

        return deepcopy(record.response)

    def save_response(
        self,
        key: str,
        payload: dict[str, Any],
        response: dict[str, Any],
    ) -> dict[str, Any]:
        self._validate_key(key)

        existing = self.get_response(key, payload)

        if existing is not None:
            return existing

        record = IdempotencyRecord(
            key=key,
            request_hash=build_request_hash(payload),
            response=deepcopy(response),
        )

        self._records[key] = record

        return deepcopy(response)

    @staticmethod
    def _validate_key(key: str) -> None:
        if not key.strip():
            raise ValueError("idempotency key não pode ser vazia")
