from decimal import Decimal

import pytest

from experiments.financial.ledger.account import Account, AccountType
from experiments.financial.ledger.balance_projection import project_balances
from experiments.financial.ledger.transaction import (
    EntrySide,
    LedgerEntry,
    LedgerTransaction,
)


def test_balanced_transaction_is_valid() -> None:
    transaction = LedgerTransaction(
        transaction_id="txn_001",
        description="transação balanceada",
        entries=(
            LedgerEntry("acct_a", EntrySide.DEBIT, "100.00"),
            LedgerEntry("acct_b", EntrySide.CREDIT, "100.00"),
        ),
    )

    assert transaction.total_debits == Decimal("100.00")
    assert transaction.total_credits == Decimal("100.00")


def test_unbalanced_transaction_raises_error() -> None:
    with pytest.raises(ValueError, match="desbalanceada"):
        LedgerTransaction(
            transaction_id="txn_002",
            description="transação inválida",
            entries=(
                LedgerEntry("acct_a", EntrySide.DEBIT, "100.00"),
                LedgerEntry("acct_b", EntrySide.CREDIT, "90.00"),
            ),
        )


def test_project_balances_for_pix_like_flow() -> None:
    cash = Account("acct_cash", "Caixa", AccountType.ASSET)
    customer_wallet = Account("acct_customer_wallet", "Carteira cliente", AccountType.LIABILITY)
    merchant_payable = Account("acct_merchant_payable", "A pagar lojista", AccountType.LIABILITY)
    fees_revenue = Account("acct_fees_revenue", "Receita tarifas", AccountType.REVENUE)

    funding = LedgerTransaction(
        transaction_id="txn_funding",
        description="funding cliente",
        entries=(
            LedgerEntry("acct_cash", EntrySide.DEBIT, "1000.00"),
            LedgerEntry("acct_customer_wallet", EntrySide.CREDIT, "1000.00"),
        ),
    )

    payment = LedgerTransaction(
        transaction_id="txn_payment",
        description="pagamento pix-like",
        entries=(
            LedgerEntry("acct_customer_wallet", EntrySide.DEBIT, "150.00"),
            LedgerEntry("acct_merchant_payable", EntrySide.CREDIT, "148.00"),
            LedgerEntry("acct_fees_revenue", EntrySide.CREDIT, "2.00"),
        ),
    )

    balances = project_balances(
        accounts=[cash, customer_wallet, merchant_payable, fees_revenue],
        transactions=[funding, payment],
    )

    assert balances["acct_cash"].balance == Decimal("1000.00")
    assert balances["acct_customer_wallet"].balance == Decimal("850.00")
    assert balances["acct_merchant_payable"].balance == Decimal("148.00")
    assert balances["acct_fees_revenue"].balance == Decimal("2.00")
