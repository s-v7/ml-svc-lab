
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from uuid import uuid4

MONEY_SCALE = Decimal("0.01")

class EntrySide(str, Enum):
    DEBIT = "debit"
    CREDIT = "credit"

def money(value: str | int | float | Decimal) -> Decimal:
    return Decimal(str(value)).quantize(MONEY_SCALE)

def new_transaction_id(prefix: str = "txn") -> str:
    return f"{prefix}_{uuid4().hex[:12]}"

@dataclass(frozen=True, slots=True)
class LedgerEntry:
    account_id: str
    side: EntrySide
    amount: Decimal
    currency: str = "BRL"
    memo: str = ""

    def __post_init__(self) -> None:
        if not self.account_id.strip():
            raise ValueError("account_id não poder vazio")

        if isinstance(self.side, str):
            object.__setattr__(self, "side", EntrySide(self.side))

        amount = money(self.amount)
        if amount <= Decimal("0.00"):
            raise ValueError("amount deve ser maior que zero")

        object.__setattr__(self, "amount", amount)
        currency = self.currency.upper().strip()
        if len(currency) != 3:
            raise ValueError("currency deve ter 3 letras, ex: BRL")
        object.__setattr__(self, "currency", currency)

@dataclass(frozen=True, slots=True)
class LedgerTransaction:
    transaction_id: str
    description: str
    entries: tuple[LedgerEntry, ...]
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.transaction_id.strip():
            raise ValueError("transaction_id não pode ser vazio")

        if not self.transaction_id.strip():
            raise ValueError("description não pode ser vazio")

        if len(self.entries) < 2:
            raise ValueError("uma transaction contábil precisa de pelo menos 2 lançamentos")

        currencies = {entry.currency for entry in self.entries}
        if len(currencies) != 1:
            raise ValueError("todos os lançamentos da transaction devem usar a mesma moeda")
        
        if self.total_debits != self.total_credits:
            raise ValueError(
               f"Transaction desbalanceada: débito={self.total_debits} "
               f"Cŕeditos={self.total_credits}"
            )
    @property
    def currency(self) -> str:
        return self.entries[0].currency
    @property
    def total_debits(self) -> Decimal:
        return sum((entry.amount for entry in self.entries if entry.side == EntrySide.DEBIT), Decimal("0.00"))
    @property
    def total_credits(self) -> Decimal:
        return sum((entry.amount for entry in self.entries if entry.side == EntrySide.CREDIT), Decimal("0.00"))

def create_transfer_transaction(
    from_account_id: str,
    to_account_id: str,
    amount: str | int | float | Decimal,
    description: str,
    currency: str = "BRL"
) -> LedgerTransaction:

    value = money(amount)
    return LedgerTransaction(
        transaction_id=new_transaction_id(),
        description=description,
        entries=(
            LedgerEntry(
                account_id=to_account_id,
                side=EntrySide.DEBIT,
                amount=value,
                currency=currency,
                memo="entrada da transferência"
            ),
            LedgerEntry(
                account_id=from_account_id,
                side=EntrySide.CREDIT,
                amount=value,
                currency=currency,
                memo="saída da transferência"
            ),
        ),
    )


