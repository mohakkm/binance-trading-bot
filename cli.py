#!/usr/bin/env python3
"""
cli.py — Entry point for the Binance Futures Testnet Trading Bot.

Usage examples:
  python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
  python cli.py --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.1 --price 3000
"""

import argparse
import sys

from bot.client import get_client
from bot.logging_config import setup_logger
from bot.orders import place_limit_order, place_market_order
from bot.validators import validate_all

logger = setup_logger(__name__)


# ── Display helpers ────────────────────────────────────────────────────────────

def print_separator(char: str = "─", width: int = 52) -> None:
    print(char * width)


def print_request_summary(args: argparse.Namespace) -> None:
    """Prints a clean table of what the user asked for before the order is sent."""
    print_separator()
    print("  ORDER REQUEST SUMMARY")
    print_separator()
    print(f"  Symbol     : {args.symbol.upper()}")
    print(f"  Side       : {args.side.upper()}")
    print(f"  Type       : {args.type.upper()}")
    print(f"  Quantity   : {args.quantity}")
    if args.type.upper() == "LIMIT":
        print(f"  Price      : {args.price}")
    print_separator()
    print()


def print_order_result(result: dict) -> None:
    """Prints the order response details returned by Binance."""
    print_separator()
    print("  ORDER RESPONSE")
    print_separator()
    print(f"  Order ID     : {result['orderId']}")
    print(f"  Symbol       : {result['symbol']}")
    print(f"  Side         : {result['side']}")
    print(f"  Type         : {result['type']}")
    print(f"  Status       : {result['status']}")
    print(f"  Orig Qty     : {result['origQty']}")
    print(f"  Executed Qty : {result['executedQty']}")
    print(f"  Avg Price    : {result['avgPrice']}")
    if result["type"] == "LIMIT":
        print(f"  Limit Price  : {result['price']}")
        print(f"  Time In Force: {result['timeInForce']}")
    print_separator()
    print()


def print_success(order_type: str) -> None:
    print(f"  ✓ {order_type} order placed successfully on Binance Futures Testnet.")
    print()


def print_error(message: str) -> None:
    print()
    print("  ✗ ERROR:", message)
    print()


# ── Argument parser ────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Place Market or Limit orders on Binance Futures Testnet (USDT-M).",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01\n"
            "  python cli.py --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.1 --price 3000\n"
        ),
    )

    parser.add_argument(
        "--symbol", "-s",
        required=True,
        help="Trading pair symbol (e.g. BTCUSDT, ETHUSDT)",
    )
    parser.add_argument(
        "--side",
        required=True,
        choices=["BUY", "SELL", "buy", "sell"],
        metavar="SIDE",
        help="Order side: BUY or SELL",
    )
    parser.add_argument(
        "--type", "-t",
        required=True,
        choices=["MARKET", "LIMIT", "market", "limit"],
        metavar="TYPE",
        help="Order type: MARKET or LIMIT",
    )
    parser.add_argument(
        "--quantity", "-q",
        required=True,
        help="Quantity to trade (e.g. 0.01)",
    )
    parser.add_argument(
        "--price", "-p",
        required=False,
        default=None,
        help="Limit price — required for LIMIT orders (e.g. 80000)",
    )

    return parser


# ── Main flow ──────────────────────────────────────────────────────────────────

def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    logger.info(
        "CLI invoked | symbol=%s side=%s type=%s quantity=%s price=%s",
        args.symbol, args.side, args.type, args.quantity, args.price,
    )

    # Step 1: Print what the user asked for
    print_request_summary(args)

    # Step 2: Validate all inputs
    try:
        params = validate_all(
            symbol=args.symbol,
            side=args.side,
            order_type=args.type,
            quantity=args.quantity,
            price=args.price,
        )
    except ValueError as e:
        logger.error("Input validation failed: %s", e)
        print_error(str(e))
        sys.exit(1)

    # Step 3: Initialise the Binance client
    try:
        client = get_client()
    except (EnvironmentError, ConnectionError) as e:
        logger.error("Client initialisation failed: %s", e)
        print_error(str(e))
        sys.exit(1)

    # Step 4: Place the order
    try:
        if params["order_type"] == "MARKET":
            result = place_market_order(
                client=client,
                symbol=params["symbol"],
                side=params["side"],
                quantity=params["quantity"],
            )
        else:  # LIMIT
            result = place_limit_order(
                client=client,
                symbol=params["symbol"],
                side=params["side"],
                quantity=params["quantity"],
                price=params["price"],
            )
    except RuntimeError as e:
        logger.error("Order placement failed: %s", e)
        print_error(str(e))
        sys.exit(1)

    # Step 5: Print result and exit cleanly
    print_order_result(result)
    print_success(params["order_type"])
    logger.info("Session completed successfully.")
    sys.exit(0)


if __name__ == "__main__":
    main()