from decimal import Decimal

import pytest

from experiments.financial.ledger.account import Account, AccountType
from experiments.financial.ledger.balance_projection import project_balances
from experiments.financial.ledger.transaction import (
    EntrySide,
    LedgerEntry,
    LedgerTransaction,
)
from experiments.financial.pix.payment_intent import (
    PaymentIntentStatus,
    PixLikePaymentService,
)


def test_create_intent_is_idempotent_for_same_payload() -> None:
    service = PixLikePaymentService()

    intent_1 = service.create_intent(
        payer_account_id="acct_customer_wallet",
        merchant_payable_account_id="acct_merchant_payable",
        fee_revenue_account_id="acct_fees_revenue",
        amount="150.00",
        fee="2.00",
        idempotency_key="idem_001",
        description="Pagamento pedido #001",
    )

    intent_2 = service.create_intent(
        payer_account_id="acct_customer_wallet",
        merchant_payable_account_id="acct_merchant_payable",
        fee_revenue_account_id="acct_fees_revenue",
        amount="150.00",
        fee="2.00",
        idempotency_key="idem_001",
        description="Pagamento pedido #001",
    )

    assert intent_1.intent_id == intent_2.intent_id


def test_same_idempotency_key_with_different_payload_raises_error() -> None:
    service = PixLikePaymentService()

    service.create_intent(
        payer_account_id="acct_customer_wallet",
        merchant_payable_account_id="acct_merchant_payable",
        fee_revenue_account_id="acct_fees_revenue",
        amount="150.00",
        fee="2.00",
        idempotency_key="idem_002",
        description="Pagamento pedido #002",
    )

    with pytest.raises(ValueError, match="payload diferente"):
        service.create_intent(
            payer_account_id="acct_customer_wallet",
            merchant_payable_account_id="acct_merchant_payable",
            fee_revenue_account_id="acct_fees_revenue",
            amount="151.00",
            fee="2.00",
            idempotency_key="idem_002",
            description="Pagamento pedido #002",
        )


def test_settle_intent_generates_ledger_transaction_and_balances() -> None:
    cash = Account("acct_cash", "Caixa", AccountType.ASSET)
    customer_wallet = Account(
        "acct_customer_wallet",
        "Carteira cliente",
        AccountType.LIABILITY,
    )
    merchant_payable = Account(
        "acct_merchant_payable",
        "A pagar lojista",
        AccountType.LIABILITY,
    )
    fees_revenue = Account(
        "acct_fees_revenue",
        "Receita tarifas",
        AccountType.REVENUE,
    )

    funding = LedgerTransaction(
        transaction_id="txn_funding",
        description="funding cliente",
        entries=(
            LedgerEntry("acct_cash", EntrySide.DEBIT, "1000.00"),
            LedgerEntry("acct_customer_wallet", EntrySide.CREDIT, "1000.00"),
        ),
    )

    service = PixLikePaymentService()

    intent = service.create_intent(
        payer_account_id="acct_customer_wallet",
        merchant_payable_account_id="acct_merchant_payable",
        fee_revenue_account_id="acct_fees_revenue",
        amount="150.00",
        fee="2.00",
        idempotency_key="idem_003",
        description="Pagamento pedido #003",
    )

    settlement = service.settle_intent(intent.intent_id)
    settled_intent = service.get_intent(intent.intent_id)

    assert settlement.total_debits == Decimal("150.00")
    assert settlement.total_credits == Decimal("150.00")
    assert settled_intent.status == PaymentIntentStatus.SETTLED

    balances = project_balances(
        accounts=[cash, customer_wallet, merchant_payable, fees_revenue],
        transactions=[funding, settlement],
    )

    assert balances["acct_cash"].balance == Decimal("1000.00")
    assert balances["acct_customer_wallet"].balance == Decimal("850.00")
    assert balances["acct_merchant_payable"].balance == Decimal("148.00")
    assert balances["acct_fees_revenue"].balance == Decimal("2.00")


def test_settle_intent_twice_raises_error() -> None:
    service = PixLikePaymentService()

    intent = service.create_intent(
        payer_account_id="acct_customer_wallet",
        merchant_payable_account_id="acct_merchant_payable",
        fee_revenue_account_id="acct_fees_revenue",
        amount="150.00",
        fee="2.00",
        idempotency_key="idem_004",
        description="Pagamento pedido #004",
    )

    service.settle_intent(intent.intent_id)

    with pytest.raises(ValueError, match="já liquidado"):
        service.settle_intent(intent.intent_id)
