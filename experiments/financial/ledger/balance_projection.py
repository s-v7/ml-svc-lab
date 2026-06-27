from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable

from experiments.financial.ledger.account import Account, AccountType
from experiments.financial.ledger.transaction import EntrySide, LedgerEntry, LedgerTransaction


DEBIT_NORMAL = {AccountType.ASSET, AccountType.EXPENSE}
CREDIT_NORMAL = {AccountType.LIABILITY, AccountType.EQUITY, AccountType.REVENUE}


@dataclass(frozen=True, slots=True)
class AccountBalance:
    account_id: str
    name: str
    account_type: AccountType
    currency: str
    balance: Decimal


def signed_amount(account: Account, entry: LedgerEntry) -> Decimal:
    if account.account_type in DEBIT_NORMAL:
        return entry.amount if entry.side == EntrySide.DEBIT else -entry.amount

    if account.account_type in CREDIT_NORMAL:
        return entry.amount if entry.side == EntrySide.CREDIT else -entry.amount

    raise ValueError(f"tipo de conta inválido: {account.account_type}")


def project_balances(
    accounts: Iterable[Account],
    transactions: Iterable[LedgerTransaction],
) -> dict[str, AccountBalance]:
    account_map = {account.account_id: account for account in accounts}

    balances = {
        account.account_id: Decimal("0.00")
        for account in account_map.values()
    }

    for transaction in transactions:
        for entry in transaction.entries:
            account = account_map.get(entry.account_id)

            if account is None:
                raise ValueError(
                    f"lançamento referencia conta inexistente: {entry.account_id}"
                )

            if account.currency != entry.currency:
                raise ValueError(
                    f"moeda incompatível na conta {account.account_id}: "
                    f"{account.currency} != {entry.currency}"
                )

            balances[account.account_id] += signed_amount(account, entry)

    return {
        account_id: AccountBalance(
            account_id=account_id,
            name=account_map[account_id].name,
            account_type=account_map[account_id].account_type,
            currency=account_map[account_id].currency,
            balance=balance,
        )
        for account_id, balance in balances.items()
    }


def format_balance(balance: AccountBalance) -> str:
    return (
        f"{balance.account_id} | {balance.name} | "
        f"{balance.account_type.value} | {balance.currency} {balance.balance}"
    )
