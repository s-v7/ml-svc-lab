from __future__ import annotations

from experiments.financial.ledger.account import Account, AccountType
from experiments.financial.ledger.balance_projection import format_balance, project_balances
from experiments.financial.ledger.transaction import (
    EntrySide,
    LedgerEntry,
    LedgerTransaction,
    new_transaction_id,
)
from experiments.financial.pix.payment_intent import PixLikePaymentService


def main() -> None:
    cash = Account("acct_cash", "Conta caixa da instituição", AccountType.ASSET)
    customer_wallet = Account(
        "acct_customer_wallet",
        "Saldo disponível do cliente",
        AccountType.LIABILITY,
    )
    merchant_payable = Account(
        "acct_merchant_payable",
        "Valor a liquidar para lojista",
        AccountType.LIABILITY,
    )
    fees_revenue = Account(
        "acct_fees_revenue",
        "Receita de tarifas",
        AccountType.REVENUE,
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

    service = PixLikePaymentService()

    intent = service.create_intent(
        payer_account_id="acct_customer_wallet",
        merchant_payable_account_id="acct_merchant_payable",
        fee_revenue_account_id="acct_fees_revenue",
        amount="150.00",
        fee="2.00",
        idempotency_key="idem_demo_pix_001",
        description="Pagamento Pix-like pedido #001",
    )

    replay = service.create_intent(
        payer_account_id="acct_customer_wallet",
        merchant_payable_account_id="acct_merchant_payable",
        fee_revenue_account_id="acct_fees_revenue",
        amount="150.00",
        fee="2.00",
        idempotency_key="idem_demo_pix_001",
        description="Pagamento Pix-like pedido #001",
    )

    settlement = service.settle_intent(intent.intent_id)

    balances = project_balances(accounts, [funding, settlement])

    print("== Pix-like Payment Intent Demo ==")
    print()
    print(f"intent original: {intent.intent_id}")
    print(f"intent replay:   {replay.intent_id}")
    print(f"mesma intent?    {intent.intent_id == replay.intent_id}")
    print()
    print(f"settlement transaction: {settlement.transaction_id}")
    print(f"D={settlement.total_debits} C={settlement.total_credits}")
    print()
    print("Saldos projetados:")

    for balance in balances.values():
        print(format_balance(balance))


if __name__ == "__main__":
    main()
