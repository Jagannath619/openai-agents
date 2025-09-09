import gradio as gr
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from accounts import (
    Account,
    AccountError,
    InsufficientFunds,
    InsufficientHoldings,
    InvalidQuantity,
    NegativeAmount,
    InvalidSymbol,
    PriceUnavailable,
    TransactionType,
)


def parse_as_of(as_of_str: Optional[str]) -> Optional[datetime]:
    if as_of_str is None:
        return None
    s = as_of_str.strip()
    if not s:
        return None
    try:
        # Accept "Z" suffix or "+00:00", or naive time treated as UTC
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        # Ensure UTC
        if dt.tzinfo != timezone.utc:
            # convert to UTC
            dt = dt.astimezone(timezone.utc)
        return dt
    except Exception:
        raise AccountError("Invalid as_of datetime. Use ISO 8601, e.g. 2024-01-01T12:34:56Z")


def holdings_table(holds: Dict[str, object]) -> List[List[str]]:
    rows: List[List[str]] = []
    for sym, qty in sorted(holds.items()):
        rows.append([sym, str(qty)])
    return rows


def txns_table(txns) -> List[List[str]]:
    rows: List[List[str]] = []
    for t in txns:
        rows.append(
            [
                t.id,
                t.type.value,
                t.timestamp.isoformat(),
                t.symbol or "",
                "" if t.quantity is None else str(t.quantity),
                "" if t.price is None else str(t.price),
                "" if t.amount is None else str(t.amount),
                "" if t.total is None else str(t.total),
                t.note or "",
            ]
        )
    return rows


def summarize(acct: Optional[Account], as_of_str: Optional[str]) -> Tuple[str, str, str, str, str, List[List[str]], List[List[str]], str]:
    if acct is None:
        return (
            "No account",
            "",
            "",
            "",
            "",
            [],
            [],
            "No account yet. Create one below.",
        )
    try:
        as_of = parse_as_of(as_of_str)
        holds = acct.holdings(as_of=as_of)
        cash = acct.cash_balance(as_of=as_of)
        try:
            pv = acct.portfolio_value(as_of=as_of)
        except PriceUnavailable as e:
            pv = None
        equity = acct.equity(as_of=as_of) if pv is not None else None
        pnl = acct.profit_loss(as_of=as_of) if pv is not None else None
        pnl_first = acct.profit_loss_vs_first_deposit(as_of=as_of) if pv is not None else None
        txns = acct.transactions(end=as_of)

        owner_text = acct.owner
        cash_text = str(cash)
        pv_text = "N/A" if pv is None else str(pv)
        equity_text = "N/A" if equity is None else str(equity)
        pnl_text = "N/A" if pnl is None else str(pnl)
        pnl_first_text = "N/A" if pnl_first is None else str(pnl_first)

        return (
            owner_text,
            cash_text,
            pv_text,
            equity_text,
            pnl_text,
            pnl_first_text,
            holdings_table(holds),
            txns_table(txns),
            "OK",
        )
    except Exception as e:
        return (
            acct.owner,
            "",
            "",
            "",
            "",
            [],
            [],
            f"ERROR: {e}",
        )


def create_account(owner: str, initial_deposit: str, _: Optional[Account]) -> Tuple[Optional[Account], str, str, str, str, str, List[List[str]], List[List[str]], str]:
    try:
        owner = (owner or "").strip()
        if not owner:
            raise AccountError("Owner name is required")
        init_dep = initial_deposit.strip() if isinstance(initial_deposit, str) else ""
        acct = Account(owner=owner, initial_deposit=init_dep if init_dep else None)
        owner_text, cash_text, pv_text, equity_text, pnl_text, pnl_first_text, holds, txns, status = summarize(acct, None)
        status = "OK: Account created/reset"
        return acct, owner_text, cash_text, pv_text, equity_text, pnl_text, holds, txns, status
    except Exception as e:
        # Do not change state on error
        return None, "No account", "", "", "", "", [], [], f"ERROR: {e}"


def do_deposit(acct: Optional[Account], amount: str, as_of_str: Optional[str]) -> Tuple[str, str, str, str, str, List[List[str]], List[List[str]], str]:
    if acct is None:
        return "No account", "", "", "", "", [], [], "ERROR: Create an account first"
    try:
        amt = (amount or "").strip()
        if not amt:
            raise NegativeAmount("Amount is required")
        acct.deposit(amt)
        owner_text, cash_text, pv_text, equity_text, pnl_text, pnl_first_text, holds, txns, _ = summarize(acct, as_of_str)
        return owner_text, cash_text, pv_text, equity_text, pnl_text, pnl_first_text, holds, txns, "OK: Deposit recorded"
    except (NegativeAmount, AccountError) as e:
        return acct.owner, "", "", "", "", [], [], f"ERROR: {e}"


def do_withdraw(acct: Optional[Account], amount: str, as_of_str: Optional[str]) -> Tuple[str, str, str, str, str, List[List[str]], List[List[str]], str]:
    if acct is None:
        return "No account", "", "", "", "", [], [], "ERROR: Create an account first"
    try:
        amt = (amount or "").strip()
        if not amt:
            raise NegativeAmount("Amount is required")
        acct.withdraw(amt)
        owner_text, cash_text, pv_text, equity_text, pnl_text, pnl_first_text, holds, txns, _ = summarize(acct, as_of_str)
        return owner_text, cash_text, pv_text, equity_text, pnl_text, pnl_first_text, holds, txns, "OK: Withdrawal recorded"
    except (NegativeAmount, InsufficientFunds, AccountError) as e:
        return acct.owner, "", "", "", "", [], [], f"ERROR: {e}"


def do_buy(acct: Optional[Account], symbol: str, quantity: str, price: str, as_of_str: Optional[str]) -> Tuple[str, str, str, str, str, List[List[str]], List[List[str]], str]:
    if acct is None:
        return "No account", "", "", "", "", [], [], "ERROR: Create an account first"
    try:
        sym = (symbol or "").strip()
        qty = (quantity or "").strip()
        pr = (price or "").strip()
        px = pr if pr else None
        acct.buy(sym, qty, price=px)
        owner_text, cash_text, pv_text, equity_text, pnl_text, pnl_first_text, holds, txns, _ = summarize(acct, as_of_str)
        used_px = f" @ {px}" if px is not None else ""
        return owner_text, cash_text, pv_text, equity_text, pnl_text, pnl_first_text, holds, txns, f"OK: Bought {qty} {sym}{used_px}"
    except (InvalidSymbol, InvalidQuantity, PriceUnavailable, InsufficientFunds, AccountError) as e:
        return acct.owner, "", "", "", "", [], [], f"ERROR: {e}"


def do_sell(acct: Optional[Account], symbol: str, quantity: str, price: str, as_of_str: Optional[str]) -> Tuple[str, str, str, str, str, List[List[str]], List[List[str]], str]:
    if acct is None:
        return "No account", "", "", "", "", [], [], "ERROR: Create an account first"
    try:
        sym = (symbol or "").strip()
        qty = (quantity or "").strip()
        pr = (price or "").strip()
        px = pr if pr else None
        acct.sell(sym, qty, price=px)
        owner_text, cash_text, pv_text, equity_text, pnl_text, pnl_first_text, holds, txns, _ = summarize(acct, as_of_str)
        used_px = f" @ {px}" if px is not None else ""
        return owner_text, cash_text, pv_text, equity_text, pnl_text, pnl_first_text, holds, txns, f"OK: Sold {qty} {sym}{used_px}"
    except (InvalidSymbol, InvalidQuantity, PriceUnavailable, InsufficientHoldings, AccountError) as e:
        return acct.owner, "", "", "", "", [], [], f"ERROR: {e}"


def do_refresh(acct: Optional[Account], as_of_str: Optional[str]) -> Tuple[str, str, str, str, str, List[List[str]], List[List[str]], str]:
    owner_text, cash_text, pv_text, equity_text, pnl_text, pnl_first_text, holds, txns, status = summarize(acct, as_of_str)
    return owner_text, cash_text, pv_text, equity_text, pnl_text, pnl_first_text, holds, txns, status


with gr.Blocks(title="Trading Simulation - Account Demo") as demo:
    gr.Markdown("# Trading Simulation - Simple Account Demo")

    acct_state = gr.State(value=None)

    with gr.Group():
        gr.Markdown("Create/Reset Account (single user demo)")
        with gr.Row():
            owner_in = gr.Textbox(label="Owner", placeholder="e.g., alice")
            init_dep_in = gr.Textbox(label="Initial Deposit (optional)", placeholder="e.g., 10000.00")
            create_btn = gr.Button("Create / Reset Account", variant="primary")

    with gr.Group():
        gr.Markdown("As-of Reporting (optional)")
        as_of_in = gr.Textbox(
            label="As of (UTC, ISO 8601, e.g., 2024-01-01T12:34:56Z). Leave blank for now.",
            placeholder="YYYY-MM-DDTHH:MM:SSZ",
        )
        refresh_btn = gr.Button("Refresh Summary")

    with gr.Group():
        gr.Markdown("Summary")
        with gr.Row():
            owner_out = gr.Textbox(label="Owner", interactive=False)
            cash_out = gr.Textbox(label="Cash", interactive=False)
            portfolio_out = gr.Textbox(label="Portfolio Value", interactive=False)
            equity_out = gr.Textbox(label="Equity", interactive=False)
        with gr.Row():
            pnl_out = gr.Textbox(label="PnL (vs net contributions)", interactive=False)
            pnl_first_out = gr.Textbox(label="PnL vs First Deposit", interactive=False)

    with gr.Group():
        gr.Markdown("Cash Management")
        with gr.Row():
            deposit_in = gr.Textbox(label="Deposit Amount", placeholder="e.g., 500.00")
            deposit_btn = gr.Button("Deposit")
            withdraw_in = gr.Textbox(label="Withdraw Amount", placeholder="e.g., 200.00")
            withdraw_btn = gr.Button("Withdraw")

    with gr.Group():
        gr.Markdown("Trading")
        with gr.Row():
            symbol_in = gr.Textbox(label="Symbol", placeholder="AAPL, TSLA, GOOGL")
            qty_in = gr.Textbox(label="Quantity", placeholder="e.g., 1.5")
            price_in = gr.Textbox(label="Limit Price (optional, leave blank for market)", placeholder="")
        with gr.Row():
            buy_btn = gr.Button("Buy", variant="secondary")
            sell_btn = gr.Button("Sell", variant="secondary")

    with gr.Group():
        gr.Markdown("Holdings and Transactions")
        holdings_df = gr.Dataframe(headers=["Symbol", "Quantity"], row_count=0, col_count=(2, "fixed"), wrap=True, interactive=False)
        txns_df = gr.Dataframe(
            headers=["ID", "Type", "Timestamp", "Symbol", "Quantity", "Price", "Amount", "Total", "Note"],
            row_count=0,
            col_count=(9, "fixed"),
            wrap=True,
            interactive=False,
        )

    status_out = gr.Textbox(label="Status", interactive=False)

    # Wire events
    create_btn.click(
        fn=create_account,
        inputs=[owner_in, init_dep_in, acct_state],
        outputs=[acct_state, owner_out, cash_out, portfolio_out, equity_out, pnl_out, pnl_first_out, holdings_df, txns_df, status_out],
    )

    refresh_btn.click(
        fn=do_refresh,
        inputs=[acct_state, as_of_in],
        outputs=[owner_out, cash_out, portfolio_out, equity_out, pnl_out, pnl_first_out, holdings_df, txns_df, status_out],
    )

    deposit_btn.click(
        fn=do_deposit,
        inputs=[acct_state, deposit_in, as_of_in],
        outputs=[owner_out, cash_out, portfolio_out, equity_out, pnl_out, pnl_first_out, holdings_df, txns_df, status_out],
    )

    withdraw_btn.click(
        fn=do_withdraw,
        inputs=[acct_state, withdraw_in, as_of_in],
        outputs=[owner_out, cash_out, portfolio_out, equity_out, pnl_out, pnl_first_out, holdings_df, txns_df, status_out],
    )

    buy_btn.click(
        fn=do_buy,
        inputs=[acct_state, symbol_in, qty_in, price_in, as_of_in],
        outputs=[owner_out, cash_out, portfolio_out, equity_out, pnl_out, pnl_first_out, holdings_df, txns_df, status_out],
    )

    sell_btn.click(
        fn=do_sell,
        inputs=[acct_state, symbol_in, qty_in, price_in, as_of_in],
        outputs=[owner_out, cash_out, portfolio_out, equity_out, pnl_out, pnl_first_out, holdings_df, txns_df, status_out],
    )


if __name__ == "__main__":
    demo.launch()