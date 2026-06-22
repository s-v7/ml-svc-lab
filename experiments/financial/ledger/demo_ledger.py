from __future__ import annotations

from experiments.financial.ledger.account import Account, AccountType
from experiments.financial.ledger.balance_projection import format_balance, project_balances
from experiments.financial.ledger.transaction import (
    EntrySide,
    LedgerEntry,
    LedgerTransaction,
    new_transaction_id,
)


def main() -> None:
    cash = Account(
        account_id="acct_cash",
        name="Conta caixa da instituição",
        account_type=AccountType.ASSET,
    )

    customer_wallet = Account(
        account_id="acct_customer_wallet",
        name="Saldo disponível do cliente",
        account_type=AccountType.LIABILITY,
    )

    merchant_payable = Account(
        account_id="acct_merchant_payable",
        name="Valor a liquidar para lojista",
        account_type=AccountType.LIABILITY,
    )

    fees_revenue = Account(
        account_id="acct_fees_revenue",
        name="Receita de tarifas",
        account_type=AccountType.REVENUE,
    )

    accounts = [cash, customer_wallet, merchant_payable, fees_revenue]

    funding = LedgerTransaction(
        transaction_id=new_transaction_id(),
        description="Cliente adiciona saldo na carteira",
        entries=(
            LedgerEntry("acct_cash", EntrySide.DEBIT, "1000.00"),
            LedgerEntry("acct_customer_wallet", EntrySide.CREDIT, "1000.00"),
        ),
    )

    pix_like_payment = LedgerTransaction(
        transaction_id=new_transaction_id(),
        description="Pagamento Pix-like com tarifa",
        entries=(
            LedgerEntry("acct_customer_wallet", EntrySide.DEBIT, "150.00"),
            LedgerEntry("acct_merchant_payable", EntrySide.CREDIT, "148.00"),
            LedgerEntry("acct_fees_revenue", EntrySide.CREDIT, "2.00"),
        ),
    )

    transactions = [funding, pix_like_payment]
    balances = project_balances(accounts, transactions)

    print("== Financial Ledger Demo ==")
    print()
    print("Transações:")

    for transaction in transactions:
        print(
            f"- {transaction.transaction_id} | {transaction.description} | "
            f"D={transaction.total_debits} C={transaction.total_credits}"
        )

    print()
    print("Saldos projetados:")

    for balance in balances.values():
        print(format_balance(balance))


if __name__ == "__main__":
    main()
