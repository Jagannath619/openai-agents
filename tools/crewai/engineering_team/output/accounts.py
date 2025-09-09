from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, getcontext, ROUND_HALF_UP
from enum import Enum
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union
import re
import uuid

# Configure Decimal context
getcontext().prec = 28

# Constants
MONEY_PLACES = Decimal("0.01")
QTY_PLACES = Decimal("0.000001")

# Exceptions
class AccountError(Exception):
    pass

class InsufficientFunds(AccountError):
    pass

class InsufficientHoldings(AccountError):
    pass

class InvalidQuantity(AccountError):
    pass

class NegativeAmount(AccountError):
    pass

class InvalidSymbol(AccountError):
    pass

class PriceUnavailable(AccountError):
    pass

# Enums
class TransactionType(Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    BUY = "BUY"
    SELL = "SELL"

# Helper functions

def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def quantize_money(value: Union[int, float, str, Decimal]) -> Decimal:
    d = Decimal(str(value))
    return d.quantize(MONEY_PLACES, rounding=ROUND_HALF_UP)


def quantize_qty(value: Union[int, float, str, Decimal]) -> Decimal:
    d = Decimal(str(value))
    return d.quantize(QTY_PLACES, rounding=ROUND_HALF_UP)


def get_share_price(symbol: str) -> Decimal:
    if not isinstance(symbol, str) or not symbol:
        raise InvalidSymbol("Symbol must be a non-empty string")
    s = symbol.upper()
    prices = {
        "AAPL": Decimal("150.00"),
        "TSLA": Decimal("250.00"),
        "GOOGL": Decimal("2800.00"),
    }
    try:
        return prices[s]
    except KeyError:
        raise PriceUnavailable(f"No price available for symbol: {s}")

# Dataclasses
@dataclass(frozen=True)
class Transaction:
    id: str
    type: TransactionType
    timestamp: datetime
    symbol: Optional[str]
    quantity: Optional[Decimal]
    price: Optional[Decimal]
    amount: Optional[Decimal]
    total: Optional[Decimal]
    note: Optional[str]


class Account:
    def __init__(
        self,
        owner: str,
        base_currency: str = "USD",
        price_fn: Optional[Callable[[str], Decimal]] = None,
        initial_deposit: Optional[Union[int, float, str, Decimal]] = None,
        now: Optional[datetime] = None,
    ) -> None:
        if not isinstance(owner, str) or not owner.strip():
            raise AccountError("owner must be a non-empty string")
        self.owner: str = owner.strip()
        self.base_currency: str = base_currency
        self._price_fn: Callable[[str], Decimal] = price_fn if price_fn is not None else get_share_price
        self._txns: List[Transaction] = []
        self._cash: Decimal = Decimal("0")
        self._positions: Dict[str, Decimal] = {}
        # perform initial deposit if provided
        if initial_deposit is not None:
            ts = self._validate_timestamp(now if now is not None else self._now())
            self.deposit(initial_deposit, timestamp=ts, note="Initial deposit")

    # Public API
    def deposit(
        self,
        amount: Union[int, float, str, Decimal],
        timestamp: Optional[datetime] = None,
        note: Optional[str] = None,
    ) -> Transaction:
        ts = self._validate_timestamp(timestamp if timestamp is not None else self._now())
        self._enforce_chronology(ts)
        amt = self._to_money_positive(amount)
        self._cash = quantize_money(self._cash + amt)
        txn = self._build_cash_txn(TransactionType.DEPOSIT, ts, amt, note)
        self._append_txn(txn)
        return txn

    def withdraw(
        self,
        amount: Union[int, float, str, Decimal],
        timestamp: Optional[datetime] = None,
        note: Optional[str] = None,
    ) -> Transaction:
        ts = self._validate_timestamp(timestamp if timestamp is not None else self._now())
        self._enforce_chronology(ts)
        amt = self._to_money_positive(amount)
        if self._cash < amt:
            raise InsufficientFunds("Insufficient cash to withdraw the requested amount")
        self._cash = quantize_money(self._cash - amt)
        txn = self._build_cash_txn(TransactionType.WITHDRAWAL, ts, amt, note)
        self._append_txn(txn)
        return txn

    def buy(
        self,
        symbol: str,
        quantity: Union[int, float, str, Decimal],
        price: Optional[Union[int, float, str, Decimal]] = None,
        timestamp: Optional[datetime] = None,
        note: Optional[str] = None,
    ) -> Transaction:
        ts = self._validate_timestamp(timestamp if timestamp is not None else self._now())
        self._enforce_chronology(ts)
        sym = self._ensure_symbol(symbol)
        qty = self._to_qty_positive(quantity)
        px = self._determine_price(sym, price)
        total_cost = quantize_money(qty * px)
        if self._cash < total_cost:
            raise InsufficientFunds("Insufficient cash to execute buy order")
        # Update positions and cash
        self._positions[sym] = quantize_qty(self._positions.get(sym, Decimal("0")) + qty)
        self._cash = quantize_money(self._cash - total_cost)
        txn = Transaction(
            id=uuid.uuid4().hex,
            type=TransactionType.BUY,
            timestamp=ts,
            symbol=sym,
            quantity=qty,
            price=px,
            amount=None,
            total=quantize_money(-total_cost),
            note=note,
        )
        self._append_txn(txn)
        return txn

    def sell(
        self,
        symbol: str,
        quantity: Union[int, float, str, Decimal],
        price: Optional[Union[int, float, str, Decimal]] = None,
        timestamp: Optional[datetime] = None,
        note: Optional[str] = None,
    ) -> Transaction:
        ts = self._validate_timestamp(timestamp if timestamp is not None else self._now())
        self._enforce_chronology(ts)
        sym = self._ensure_symbol(symbol)
        qty = self._to_qty_positive(quantity)
        current_qty = self._positions.get(sym, Decimal("0"))
        if current_qty < qty:
            raise InsufficientHoldings("Insufficient holdings to execute sell order")
        px = self._determine_price(sym, price)
        proceeds = quantize_money(qty * px)
        # Update positions and cash
        new_qty = quantize_qty(current_qty - qty)
        if new_qty == Decimal("0"):
            self._positions.pop(sym, None)
        else:
            self._positions[sym] = new_qty
        self._cash = quantize_money(self._cash + proceeds)
        txn = Transaction(
            id=uuid.uuid4().hex,
            type=TransactionType.SELL,
            timestamp=ts,
            symbol=sym,
            quantity=qty,
            price=px,
            amount=None,
            total=proceeds,
            note=note,
        )
        self._append_txn(txn)
        return txn

    # Reporting
    def holdings(self, as_of: Optional[datetime] = None) -> Dict[str, Decimal]:
        if as_of is None:
            return dict(self._positions)
        as_ts = self._validate_timestamp(as_of)
        positions, _ = self._recompute_as_of(as_ts)
        return positions

    def cash_balance(self, as_of: Optional[datetime] = None) -> Decimal:
        if as_of is None:
            return self._cash
        as_ts = self._validate_timestamp(as_of)
        _, cash = self._recompute_as_of(as_ts)
        return cash

    def portfolio_value(
        self,
        as_of: Optional[datetime] = None,
        price_fn: Optional[Callable[[str], Decimal]] = None,
    ) -> Decimal:
        pf = price_fn if price_fn is not None else self._price_fn
        positions = self.holdings(as_of=as_of)
        total = Decimal("0")
        for sym, qty in positions.items():
            try:
                px = pf(sym)
            except Exception as e:
                raise PriceUnavailable(str(e))
            px = quantize_money(px)
            if px <= 0:
                raise PriceUnavailable(f"Non-positive price for symbol: {sym}")
            total += quantize_money(qty * px)
        return quantize_money(total)

    def equity(
        self,
        as_of: Optional[datetime] = None,
        price_fn: Optional[Callable[[str], Decimal]] = None,
    ) -> Decimal:
        return quantize_money(self.cash_balance(as_of) + self.portfolio_value(as_of, price_fn))

    def profit_loss(
        self,
        as_of: Optional[datetime] = None,
        price_fn: Optional[Callable[[str], Decimal]] = None,
    ) -> Decimal:
        eq = self.equity(as_of, price_fn)
        nc = self._net_contributions(as_of)
        return quantize_money(eq - nc)

    def profit_loss_vs_first_deposit(
        self,
        as_of: Optional[datetime] = None,
        price_fn: Optional[Callable[[str], Decimal]] = None,
    ) -> Decimal:
        first_dep = Decimal("0")
        for t in self._txns:
            if t.type == TransactionType.DEPOSIT:
                first_dep = t.amount if t.amount is not None else Decimal("0")
                break
        return quantize_money(self.equity(as_of, price_fn) - first_dep)

    def transactions(
        self,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        types: Optional[Iterable[TransactionType]] = None,
        symbol: Optional[str] = None,
    ) -> List[Transaction]:
        st = self._validate_timestamp(start) if start is not None else None
        en = self._validate_timestamp(end) if end is not None else None
        type_set = set(types) if types is not None else None
        sym = self._ensure_symbol(symbol) if symbol is not None else None
        out: List[Transaction] = []
        for t in self._txns:
            if st is not None and t.timestamp < st:
                continue
            if en is not None and t.timestamp > en:
                continue
            if type_set is not None and t.type not in type_set:
                continue
            if sym is not None and t.symbol != sym:
                continue
            out.append(t)
        return out

    def get_transaction(self, txn_id: str) -> Optional[Transaction]:
        for t in self._txns:
            if t.id == txn_id:
                return t
        return None

    def stats(
        self,
        as_of: Optional[datetime] = None,
        price_fn: Optional[Callable[[str], Decimal]] = None,
    ) -> Dict[str, Any]:
        ts = self._validate_timestamp(as_of) if as_of is not None else self._now()
        holds = self.holdings(as_of)
        cash = self.cash_balance(as_of)
        pv = self.portfolio_value(as_of, price_fn)
        eq = quantize_money(cash + pv)
        nc = self._net_contributions(as_of)
        pnl = quantize_money(eq - nc)
        pnl_first = self.profit_loss_vs_first_deposit(as_of, price_fn)
        txns_count = len(self.transactions(end=as_of)) if as_of is not None else len(self._txns)
        return {
            "owner": self.owner,
            "base_currency": self.base_currency,
            "as_of": ts,
            "cash": cash,
            "holdings": holds,
            "portfolio_value": pv,
            "equity": eq,
            "net_contributions": nc,
            "pnl": pnl,
            "pnl_vs_first_deposit": pnl_first,
            "positions_count": len(holds),
            "transactions_count": txns_count,
        }

    def set_price_fn(self, price_fn: Callable[[str], Decimal]) -> None:
        if not callable(price_fn):
            raise AccountError("price_fn must be callable")
        self._price_fn = price_fn

    # Internal helpers
    def _now(self) -> datetime:
        return now_utc()

    def _validate_timestamp(self, ts: datetime) -> datetime:
        if not isinstance(ts, datetime):
            raise AccountError("timestamp must be a datetime")
        if ts.tzinfo is None or ts.tzinfo.utcoffset(ts) is None:
            raise AccountError("timestamp must be timezone-aware in UTC")
        if ts.tzinfo != timezone.utc:
            # reject non-UTC-aware datetimes to avoid ambiguity
            raise AccountError("timestamp must be in UTC timezone")
        return ts

    def _enforce_chronology(self, ts: datetime) -> None:
        if self._txns and ts < self._txns[-1].timestamp:
            raise AccountError("Transaction timestamp is earlier than the last recorded transaction")

    def _ensure_symbol(self, symbol: str) -> str:
        if not isinstance(symbol, str):
            raise InvalidSymbol("symbol must be a string")
        s = symbol.strip().upper()
        if not s:
            raise InvalidSymbol("symbol must be non-empty")
        if not re.fullmatch(r"[A-Z0-9.-]+", s):
            raise InvalidSymbol("symbol contains invalid characters")
        return s

    def _to_money_positive(self, value: Union[int, float, str, Decimal]) -> Decimal:
        amt = quantize_money(value)
        if amt <= 0:
            raise NegativeAmount("amount must be positive")
        return amt

    def _to_qty_positive(self, value: Union[int, float, str, Decimal]) -> Decimal:
        qty = quantize_qty(value)
        if qty <= 0:
            raise InvalidQuantity("quantity must be positive")
        return qty

    def _determine_price(self, symbol: str, price: Optional[Union[int, float, str, Decimal]]) -> Decimal:
        if price is None:
            try:
                px = self._price_fn(symbol)
            except Exception as e:
                raise PriceUnavailable(str(e))
        else:
            px = Decimal(str(price))
        px = quantize_money(px)
        if px <= 0:
            raise PriceUnavailable("price must be positive")
        return px

    def _build_cash_txn(
        self, ttype: TransactionType, ts: datetime, amount: Decimal, note: Optional[str]
    ) -> Transaction:
        if ttype == TransactionType.DEPOSIT:
            total = amount
        elif ttype == TransactionType.WITHDRAWAL:
            total = -amount
        else:
            raise AccountError("_build_cash_txn called with non-cash transaction type")
        return Transaction(
            id=uuid.uuid4().hex,
            type=ttype,
            timestamp=ts,
            symbol=None,
            quantity=None,
            price=None,
            amount=amount,
            total=quantize_money(total),
            note=note,
        )

    def _append_txn(self, txn: Transaction) -> None:
        # Ensure order (redundant if _enforce_chronology already called)
        if self._txns and txn.timestamp < self._txns[-1].timestamp:
            raise AccountError("Out-of-order transaction timestamps are not allowed")
        self._txns.append(txn)

    def _net_contributions(self, as_of: Optional[datetime]) -> Decimal:
        total = Decimal("0")
        end_ts = self._validate_timestamp(as_of) if as_of is not None else None
        for t in self._txns:
            if end_ts is not None and t.timestamp > end_ts:
                break
            if t.type == TransactionType.DEPOSIT and t.amount is not None:
                total += t.amount
            elif t.type == TransactionType.WITHDRAWAL and t.amount is not None:
                total -= t.amount
        return quantize_money(total)

    def _recompute_as_of(self, as_of: datetime) -> Tuple[Dict[str, Decimal], Decimal]:
        positions: Dict[str, Decimal] = {}
        cash = Decimal("0")
        for t in self._txns:
            if t.timestamp > as_of:
                break
            if t.type == TransactionType.DEPOSIT:
                cash = quantize_money(cash + (t.amount or Decimal("0")))
            elif t.type == TransactionType.WITHDRAWAL:
                cash = quantize_money(cash - (t.amount or Decimal("0")))
            elif t.type == TransactionType.BUY:
                # total is negative cash delta
                if t.symbol and t.quantity is not None:
                    positions[t.symbol] = quantize_qty(positions.get(t.symbol, Decimal("0")) + t.quantity)
                cash = quantize_money(cash + (t.total or Decimal("0")))
            elif t.type == TransactionType.SELL:
                if t.symbol and t.quantity is not None:
                    new_qty = quantize_qty(positions.get(t.symbol, Decimal("0")) - t.quantity)
                    if new_qty == Decimal("0"):
                        positions.pop(t.symbol, None)
                    else:
                        positions[t.symbol] = new_qty
                cash = quantize_money(cash + (t.total or Decimal("0")))
        return positions, cash


# Basic self-test when run as a script
if __name__ == "__main__":
    acct = Account(owner="alice", initial_deposit="10000.00")
    b1 = acct.buy("AAPL", "10")
    s1 = acct.sell("AAPL", "5")
    try:
        acct.withdraw("20000")
    except InsufficientFunds:
        print("Caught expected InsufficientFunds on withdraw")
    try:
        acct.buy("TSLA", "1000")
    except InsufficientFunds:
        print("Caught expected InsufficientFunds on buy")
    try:
        acct.sell("AAPL", "100")
    except InsufficientHoldings:
        print("Caught expected InsufficientHoldings on sell")

    print("Cash:", acct.cash_balance())
    print("Holdings:", acct.holdings())
    print("Portfolio Value:", acct.portfolio_value())
    print("Equity:", acct.equity())
    print("PnL:", acct.profit_loss())
    print("PnL vs first deposit:", acct.profit_loss_vs_first_deposit())
    print("Stats:", acct.stats())