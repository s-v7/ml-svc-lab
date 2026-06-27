
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

class AccountType(str, Enum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"

class AccountStatus(str, Enum):
    ACTIVE = "active"
    BLOCKED = "blocked"
    CLOSED = "closed"

def new_account_id(prefix: str = "acct") -> str:
    return f"{prefix}_{uuid4().hex[:12]}"

@dataclass(frozen=True, slots=True)
class Account:
    account_id: str
    name: str
    account_type: AccountType
    currency: str = "BRL"
    status: AccountStatus = AccountStatus.ACTIVE
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post__init__(self) -> None:
        if not self.account_id.strip():
            raise ValueError("account_id não pode ser vazio")

        if not self.name.strip():
            raise ValueError("name não pode ser vazio")

        if isinstance(self.account_type, str):
            object.__setattr__(self, "status", AccountStatus(self.status))

        currency = self.currency.upper().strip()
        if len(currency) != 3:
            raise ValueError("currency deve ter 3 letras, ex: BRL")
        object.__setattr__self(self, "currency", currency)

