from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from uuid import uuid4

from experiments.financial.ledger.transaction import (
    EntrySide,
    LedgerEntry,
    LedgerTransaction,
    money,
    new_transaction_id,
)
from experiments.financial.pix.idempotency import InMemoryIdempotencyStore


class PaymentIntentStatus(str, Enum):
    CREATED = "created"
    SETTLED = "settled"
    CANCELLED = "cancelled"
    FAILED = "failed"


def new_payment_intent_id(prefix: str = "pi") -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


@dataclass(frozen=True, slots=True)
class PaymentIntent:
    intent_id: str
    payer_account_id: str
    merchant_payable_account_id: str
    fee_revenue_account_id: str
    amount: Decimal
    fee: Decimal
    idempotency_key: str
    description: str
    currency: str = "BRL"
    status: PaymentIntentStatus = PaymentIntentStatus.CREATED
    settled_transaction_id: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.intent_id.strip():
            raise ValueError("intent_id não pode ser vazio")

        if not self.payer_account_id.strip():
            raise ValueError("payer_account_id não pode ser vazio")

        if not self.merchant_payable_account_id.strip():
            raise ValueError("merchant_payable_account_id não pode ser vazio")

        if not self.fee_revenue_account_id.strip():
            raise ValueError("fee_revenue_account_id não pode ser vazio")

        if not self.idempotency_key.strip():
            raise ValueError("idempotency_key não pode ser vazio")

        if not self.description.strip():
            raise ValueError("description não pode ser vazio")

        amount = money(self.amount)
        fee = money(self.fee)

        if amount <= Decimal("0.00"):
            raise ValueError("amount deve ser maior que zero")

        if fee < Decimal("0.00"):
            raise ValueError("fee não pode ser negativa")

        if fee >= amount:
            raise ValueError("fee deve ser menor que amount")

        object.__setattr__(self, "amount", amount)
        object.__setattr__(self, "fee", fee)

        currency = self.currency.upper().strip()

        if len(currency) != 3:
            raise ValueError("currency deve ter 3 letras, exemplo: BRL")

        object.__setattr__(self, "currency", currency)

        if isinstance(self.status, str):
            object.__setattr__(self, "status", PaymentIntentStatus(self.status))

    @property
    def net_amount(self) -> Decimal:
        return self.amount - self.fee


class PixLikePaymentService:
    def __init__(
        self,
        idempotency_store: InMemoryIdempotencyStore | None = None,
    ) -> None:
        self.idempotency_store = idempotency_store or InMemoryIdempotencyStore()
        self._intents: dict[str, PaymentIntent] = {}

    def create_intent(
        self,
        *,
        payer_account_id: str,
        merchant_payable_account_id: str,
        fee_revenue_account_id: str,
        amount: str | int | float | Decimal,
        fee: str | int | float | Decimal,
        idempotency_key: str,
        description: str,
        currency: str = "BRL",
    ) -> PaymentIntent:
        payload = {
            "payer_account_id": payer_account_id,
            "merchant_payable_account_id": merchant_payable_account_id,
            "fee_revenue_account_id": fee_revenue_account_id,
            "amount": str(money(amount)),
            "fee": str(money(fee)),
            "idempotency_key": idempotency_key,
            "description": description,
            "currency": currency.upper().strip(),
        }

        replay = self.idempotency_store.get_response(idempotency_key, payload)

        if replay is not None:
            intent_id = replay["intent_id"]
            return self._intents[intent_id]

        intent = PaymentIntent(
            intent_id=new_payment_intent_id(),
            payer_account_id=payer_account_id,
            merchant_payable_account_id=merchant_payable_account_id,
            fee_revenue_account_id=fee_revenue_account_id,
            amount=money(amount),
            fee=money(fee),
            idempotency_key=idempotency_key,
            description=description,
            currency=currency,
        )

        self._intents[intent.intent_id] = intent

        self.idempotency_store.save_response(
            idempotency_key,
            payload,
            {"intent_id": intent.intent_id},
        )

        return intent

    def get_intent(self, intent_id: str) -> PaymentIntent:
        intent = self._intents.get(intent_id)

        if intent is None:
            raise ValueError(f"payment intent não encontrado: {intent_id}")

        return intent

    def settle_intent(self, intent_id: str) -> LedgerTransaction:
        intent = self.get_intent(intent_id)

        if intent.status == PaymentIntentStatus.SETTLED:
            raise ValueError(f"payment intent já liquidado: {intent_id}")

        if intent.status != PaymentIntentStatus.CREATED:
            raise ValueError(
                f"payment intent não pode ser liquidado no status {intent.status.value}"
            )

        entries = [
            LedgerEntry(
                account_id=intent.payer_account_id,
                side=EntrySide.DEBIT,
                amount=intent.amount,
                currency=intent.currency,
                memo="débito do pagador",
            ),
            LedgerEntry(
                account_id=intent.merchant_payable_account_id,
                side=EntrySide.CREDIT,
                amount=intent.net_amount,
                currency=intent.currency,
                memo="valor líquido a liquidar para lojista",
            ),
        ]

        if intent.fee > Decimal("0.00"):
            entries.append(
                LedgerEntry(
                    account_id=intent.fee_revenue_account_id,
                    side=EntrySide.CREDIT,
                    amount=intent.fee,
                    currency=intent.currency,
                    memo="receita de tarifa",
                )
            )

        transaction = LedgerTransaction(
            transaction_id=new_transaction_id(),
            description=f"Liquidação payment intent {intent.intent_id}",
            entries=tuple(entries),
        )

        settled = replace(
            intent,
            status=PaymentIntentStatus.SETTLED,
            settled_transaction_id=transaction.transaction_id,
        )

        self._intents[intent.intent_id] = settled

        return transaction
