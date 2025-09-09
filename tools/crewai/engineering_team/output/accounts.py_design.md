# accounts.py — Single-module Design Spec

A self-contained Python module providing a simple, in-memory account management system for a trading simulation platform.

- Single public class: Account
- Self-contained price function: get_share_price(symbol)
- In-memory transaction ledger with time-based reporting
- Safety checks for cash and holdings
- Monetary operations use Decimal for accuracy

## Module Overview

- Purpose: Manage cash, holdings, and transactions for a single user trading simulated equities. Provide current and historical reports (as-of time) for holdings, portfolio value, and P&L.
- State: In-memory only (no external storage). Not thread-safe.
- Time: UTC-aware datetimes; operations default to current UTC if not provided.
- Pricing: Pluggable price provider; default test implementation with fixed prices for AAPL, TSLA, GOOGL.

## Key Design Decisions

- Precision and rounding: Use Decimal for all money and quantities; quantize amounts to cents and quantities to 6 decimal places.
- Profit and loss definition: P&L (since inception) computed as Equity(as_of) - NetContributions(as_of), where NetContributions = sum(deposits) - sum(withdrawals) up to as_of. This generalizes “from the initial deposit.”
- As-of semantics: Include all transactions with timestamp <= as_of; tie-breaking by transaction insertion order.
- Validation: Prevent negative balances and positions by enforcing constraints at transaction time.

## Data Types and Constants

- Monetary precision: MONEY_PLACES = Decimal('0.01')
- Quantity precision: QTY_PLACES = Decimal('0.000001')
- Base currency: Default "USD"; informational only.

## Exceptions

- class AccountError(Exception): Base exception for the module.
- class InsufficientFunds(AccountError): Raised when a withdrawal or buy exceeds available cash at the time of operation.
- class InsufficientHoldings(AccountError): Raised when attempting to sell more shares than currently held.
- class InvalidQuantity(AccountError): Raised when a quantity is non-positive or invalid.
- class NegativeAmount(AccountError): Raised when deposit/withdraw amounts are non-positive or invalid.
- class InvalidSymbol(AccountError): Raised for invalid symbol inputs.
- class PriceUnavailable(AccountError): Raised when no price is available for a symbol.

## Enums

- class TransactionType(Enum)
  - DEPOSIT
  - WITHDRAWAL
  - BUY
  - SELL

## Dataclasses

- @dataclass(frozen=True)
  - name: Transaction
  - fields:
    - id: str  // unique identifier (UUID4 hex)
    - type: TransactionType
    - timestamp: datetime  // timezone-aware UTC
    - symbol: Optional[str]  // for equity trades; None for cash ops
    - quantity: Optional[Decimal]  // for trades; quantized to QTY_PLACES; positive
    - price: Optional[Decimal]  // per-share price used at execution; MONEY_PLACES; positive
    - amount: Optional[Decimal]  // cash amount for deposits/withdrawals; MONEY_PLACES; positive
    - total: Optional[Decimal]  // signed cash delta of txn, quantized to MONEY_PLACES
    - note: Optional[str]  // free form

  - notes:
    - For DEPOSIT: amount > 0; total = +amount
    - For WITHDRAWAL: amount > 0; total = -amount
    - For BUY: quantity > 0; price > 0; total = -(quantity * price)
    - For SELL: quantity > 0; price > 0; total = +(quantity * price)

## Public API

### Class: Account

- Constructor
  - def __init__(self, owner: str, base_currency: str = "USD", price_fn: Optional[Callable[[str], Decimal]] = None, initial_deposit: Optional[Union[int, float, str, Decimal]] = None, now: Optional[datetime] = None) -> None
  - Behavior:
    - Initialize an empty account with zero cash and holdings.
    - owner: informational label for the account.
    - base_currency: string code; no FX conversion is performed.
    - price_fn: callable that returns Decimal price for symbol; defaults to module-level get_share_price.
    - If initial_deposit is provided, performs a deposit transaction at time now (or current UTC).
    - Internal state:
      - _txns: list[Transaction] in chronological/insertion order.
      - _cash: Decimal current cash balance (derived and maintained incrementally).
      - _positions: dict[str, Decimal] current share quantities per symbol.
      - _price_fn: callable
    - Validates owner is non-empty string.

- Cash management
  - def deposit(self, amount: Union[int, float, str, Decimal], timestamp: Optional[datetime] = None, note: Optional[str] = None) -> Transaction
    - Adds cash to the account.
    - amount must be > 0 after quantization to MONEY_PLACES.
    - Updates _cash and appends a DEPOSIT transaction.
    - Returns the created Transaction.

  - def withdraw(self, amount: Union[int, float, str, Decimal], timestamp: Optional[datetime] = None, note: Optional[str] = None) -> Transaction
    - Removes cash from the account.
    - amount must be > 0 after quantization.
    - Validates that current available cash >= amount; else raise InsufficientFunds.
    - Updates _cash and appends a WITHDRAWAL transaction.
    - Returns the created Transaction.

- Trading
  - def buy(self, symbol: str, quantity: Union[int, float, str, Decimal], price: Optional[Union[int, float, str, Decimal]] = None, timestamp: Optional[datetime] = None, note: Optional[str] = None) -> Transaction
    - Records a buy of given quantity of symbol.
    - Validates symbol string (non-empty, alphanumeric, uppercased).
    - quantity must be > 0 after quantization to QTY_PLACES.
    - Determines execution price:
      - If price is None, uses self._price_fn(symbol), must return positive Decimal.
      - If provided, quantize and validate > 0.
    - Computes total_cost = quantity * price, quantized to MONEY_PLACES.
    - Validates current cash >= total_cost; else raise InsufficientFunds.
    - Updates _positions[symbol] += quantity; _cash -= total_cost.
    - Appends a BUY transaction with price, quantity, and total = -total_cost.
    - Returns the created Transaction.

  - def sell(self, symbol: str, quantity: Union[int, float, str, Decimal], price: Optional[Union[int, float, str, Decimal]] = None, timestamp: Optional[datetime] = None, note: Optional[str] = None) -> Transaction
    - Records a sell of given quantity of symbol.
    - Validates symbol string.
    - quantity must be > 0 after quantization to QTY_PLACES.
    - Determines execution price:
      - If price is None, uses self._price_fn(symbol).
      - Else quantize and validate.
    - Validates current holdings for symbol >= quantity; else raise InsufficientHoldings.
    - Computes proceeds = quantity * price, quantized.
    - Updates _positions[symbol] -= quantity; if resulting position is zero, remove key; _cash += proceeds.
    - Appends a SELL transaction with price, quantity, total = +proceeds.
    - Returns the created Transaction.

- Reporting (current and as-of)
  - def holdings(self, as_of: Optional[datetime] = None) -> Dict[str, Decimal]
    - Returns a mapping of symbol -> quantity as of timestamp (or current if None).
    - For as_of is None: returns a shallow copy of current _positions.
    - For as_of provided: recomputes positions by replaying _txns up to as_of.

  - def cash_balance(self, as_of: Optional[datetime] = None) -> Decimal
    - Returns cash balance as of timestamp (or current if None).
    - For as_of is None: returns current _cash.
    - For as_of provided: computes sum of txn.total for DEPOSIT/WITHDRAWAL/BUY/SELL up to as_of.

  - def portfolio_value(self, as_of: Optional[datetime] = None, price_fn: Optional[Callable[[str], Decimal]] = None) -> Decimal
    - Returns the market value of holdings as of timestamp, priced using provided price_fn or self._price_fn.
    - Computes positions as of as_of; for each symbol, fetches price and sums quantity * price, quantized to MONEY_PLACES.
    - If price function fails for a symbol, raises PriceUnavailable.

  - def equity(self, as_of: Optional[datetime] = None, price_fn: Optional[Callable[[str], Decimal]] = None) -> Decimal
    - Returns cash_balance(as_of) + portfolio_value(as_of, price_fn), quantized.

  - def profit_loss(self, as_of: Optional[datetime] = None, price_fn: Optional[Callable[[str], Decimal]] = None) -> Decimal
    - Returns P&L since inception (net of cash flows): equity(as_of) - net_contributions(as_of).
    - net_contributions(as_of) = sum of deposit amounts - sum of withdrawal amounts up to as_of.
    - Quantized to MONEY_PLACES.

  - def profit_loss_vs_first_deposit(self, as_of: Optional[datetime] = None, price_fn: Optional[Callable[[str], Decimal]] = None) -> Decimal
    - Returns equity(as_of) - first_deposit_amount, where first_deposit_amount is the amount of the very first deposit (0 if none).
    - Provided to meet “from the initial deposit” wording explicitly.
    - Quantized to MONEY_PLACES.

  - def transactions(self, start: Optional[datetime] = None, end: Optional[datetime] = None, types: Optional[Iterable[TransactionType]] = None, symbol: Optional[str] = None) -> List[Transaction]
    - Returns a list of transactions filtered by optional start (inclusive), end (inclusive), types, and symbol.
    - Results are in chronological/insertion order.
    - Each element is an immutable Transaction.

  - def get_transaction(self, txn_id: str) -> Optional[Transaction]
    - Returns a transaction by id or None if not found.

  - def stats(self, as_of: Optional[datetime] = None, price_fn: Optional[Callable[[str], Decimal]] = None) -> Dict[str, Any]
    - Returns a summary snapshot dictionary containing:
      - owner, base_currency
      - as_of (datetime used)
      - cash (Decimal)
      - holdings (Dict[str, Decimal])
      - portfolio_value (Decimal)
      - equity (Decimal)
      - net_contributions (Decimal)
      - pnl (Decimal)
      - pnl_vs_first_deposit (Decimal)
      - positions_count (int)
      - transactions_count (int)

  - def set_price_fn(self, price_fn: Callable[[str], Decimal]) -> None
    - Assigns a new price provider for future operations and reports.

- Internal helpers (private, but defined for clarity)
  - def _now(self) -> datetime
    - Returns current UTC time; used when timestamp not supplied.
  - def _ensure_symbol(self, symbol: str) -> str
    - Validates and normalizes symbol (strips, uppercases), raises InvalidSymbol if invalid.
  - def _to_money(self, value: Union[int, float, str, Decimal]) -> Decimal
    - Converts to Decimal and quantizes to MONEY_PLACES; raises NegativeAmount if <= 0 where applicable.
  - def _to_qty(self, value: Union[int, float, str, Decimal]) -> Decimal
    - Converts to Decimal and quantizes to QTY_PLACES; raises InvalidQuantity if <= 0.
  - def _append_txn(self, txn: Transaction) -> None
    - Appends to ledger, maintaining ordering; updates current caches if txn timestamp is >= last txn; otherwise, invalidates and recomputes caches (or prohibits out-of-order insertions; see note below).
    - Simpler approach: prohibit out-of-order timestamps; raise AccountError if timestamp < last txn timestamp. Design defaults to this for predictable behavior.

  - def _net_contributions(self, as_of: Optional[datetime]) -> Decimal
    - Computes deposits - withdrawals up to as_of.

  - def _recompute_as_of(self, as_of: datetime) -> Tuple[Dict[str, Decimal], Decimal]
    - Replays txns up to as_of and returns (positions, cash).

- Out-of-order timestamps policy
  - To keep logic simple and current-state caches valid, deposit/withdraw/buy/sell must have timestamp >= last transaction timestamp. Otherwise AccountError is raised.
  - Historical simulations can still be performed by constructing operations in timestamp order.

## Helper Functions (Module-Level)

- def get_share_price(symbol: str) -> Decimal
  - Test price provider returning fixed Decimal prices:
    - "AAPL": Decimal("150.00")
    - "TSLA": Decimal("250.00")
    - "GOOGL": Decimal("2800.00")
  - Case-insensitive handling (uppercased internally).
  - Raises PriceUnavailable for unknown symbols.

- def now_utc() -> datetime
  - Returns timezone-aware current UTC datetime (datetime.now(timezone.utc)).

- def quantize_money(value: Union[int, float, str, Decimal]) -> Decimal
  - Converts to Decimal and quantizes to MONEY_PLACES (rounding=ROUND_HALF_UP).

- def quantize_qty(value: Union[int, float, str, Decimal]) -> Decimal
  - Converts to Decimal and quantizes to QTY_PLACES (rounding=ROUND_HALF_UP).

## Data Validation Rules

- Amounts and quantities must be strictly positive after quantization.
- Withdrawals cannot exceed current cash balance.
- Buys cannot exceed current cash balance at execution price.
- Sells cannot exceed current holdings quantity for the symbol.
- Symbols:
  - Non-empty, alphanumeric plus limited set of allowed characters (A–Z, 0–9, dot, hyphen).
  - Normalized to uppercase.
- Timestamps:
  - Must be timezone-aware (UTC); if naive or not UTC, they are converted to UTC assuming they represent UTC, or rejected (design choice: reject to avoid ambiguity). This design rejects non-UTC-aware datetimes with AccountError.

## As-of Time Semantics

- For as_of=None, current cached state is used (fast path).
- For as_of provided, replay transactions whose timestamp <= as_of in stored order to compute cash and positions.
- Transaction ordering: chronological by timestamp; if multiple have same timestamp, the order they were appended determines processing order.

## Error Handling Semantics

- All validation failures raise specific AccountError subclasses where applicable.
- Price lookup errors raise PriceUnavailable.
- Unknown or invalid symbols raise InvalidSymbol.

## Complexity Considerations

- Current state queries are O(1).
- As-of queries are O(n) in number of transactions up to as_of.
- Transaction storage is O(n).
- This is suitable for small to moderate volumes typical of a simulation environment.

## Extensibility Hooks

- Pluggable price function via constructor or set_price_fn.
- Potential fee model can be added by extending buy/sell to accept an optional fee parameter and include in totals.
- Persistence can be added later by serializing Transaction objects and reconstructing Account state.

## Testability Notes

- Deterministic testing by passing explicit timestamps and a stub price_fn.
- All public methods return immutable Transaction objects (where applicable) and Decimals for deterministic assertions.
- get_share_price provides fixed outputs for basic integration tests.

## Example Method Signatures Summary

- Account
  - __init__(self, owner: str, base_currency: str = "USD", price_fn: Optional[Callable[[str], Decimal]] = None, initial_deposit: Optional[Union[int, float, str, Decimal]] = None, now: Optional[datetime] = None) -> None
  - deposit(self, amount: Union[int, float, str, Decimal], timestamp: Optional[datetime] = None, note: Optional[str] = None) -> Transaction
  - withdraw(self, amount: Union[int, float, str, Decimal], timestamp: Optional[datetime] = None, note: Optional[str] = None) -> Transaction
  - buy(self, symbol: str, quantity: Union[int, float, str, Decimal], price: Optional[Union[int, float, str, Decimal]] = None, timestamp: Optional[datetime] = None, note: Optional[str] = None) -> Transaction
  - sell(self, symbol: str, quantity: Union[int, float, str, Decimal], price: Optional[Union[int, float, str, Decimal]] = None, timestamp: Optional[datetime] = None, note: Optional[str] = None) -> Transaction
  - holdings(self, as_of: Optional[datetime] = None) -> Dict[str, Decimal]
  - cash_balance(self, as_of: Optional[datetime] = None) -> Decimal
  - portfolio_value(self, as_of: Optional[datetime] = None, price_fn: Optional[Callable[[str], Decimal]] = None) -> Decimal
  - equity(self, as_of: Optional[datetime] = None, price_fn: Optional[Callable[[str], Decimal]] = None) -> Decimal
  - profit_loss(self, as_of: Optional[datetime] = None, price_fn: Optional[Callable[[str], Decimal]] = None) -> Decimal
  - profit_loss_vs_first_deposit(self, as_of: Optional[datetime] = None, price_fn: Optional[Callable[[str], Decimal]] = None) -> Decimal
  - transactions(self, start: Optional[datetime] = None, end: Optional[datetime] = None, types: Optional[Iterable[TransactionType]] = None, symbol: Optional[str] = None) -> List[Transaction]
  - get_transaction(self, txn_id: str) -> Optional[Transaction]
  - stats(self, as_of: Optional[datetime] = None, price_fn: Optional[Callable[[str], Decimal]] = None) -> Dict[str, Any]
  - set_price_fn(self, price_fn: Callable[[str], Decimal]) -> None

- Module-level
  - get_share_price(symbol: str) -> Decimal
  - now_utc() -> datetime
  - quantize_money(value: Union[int, float, str, Decimal]) -> Decimal
  - quantize_qty(value: Union[int, float, str, Decimal]) -> Decimal

## Operational Examples (Design Intent)

- Create account with initial deposit:
  - Account(owner="alice", initial_deposit="10000.00")
- Buy shares:
  - buy("AAPL", "10")  // uses default price provider if price not specified
- Query as-of end of day:
  - holdings(as_of=specific_datetime)
  - portfolio_value(as_of=specific_datetime)
  - profit_loss(as_of=specific_datetime)

This design ensures:
- Users can create accounts, deposit/withdraw, buy/sell with affordability checks.
- Holdings, portfolio value, and profit/loss are available at any point in time.
- Full transaction history is maintained and filterable.
- A default price provider is available for testing with fixed AAPL, TSLA, and GOOGL prices.