from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException
from requests.exceptions import ConnectionError, Timeout, RequestException

from bot.logging_config import setup_logger

logger = setup_logger(__name__)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _parse_response(response: dict) -> dict:
    """
    Extracts the fields the CLI cares about from a raw Binance order response.
    Gracefully falls back to "N/A" for fields that may not be present
    (e.g. avgPrice is 0 or absent on freshly placed LIMIT orders).
    """
    avg_price = response.get("avgPrice", "0") or "0"

    return {
        "orderId":     response.get("orderId", "N/A"),
        "symbol":      response.get("symbol", "N/A"),
        "side":        response.get("side", "N/A"),
        "type":        response.get("type", "N/A"),
        "status":      response.get("status", "N/A"),
        "executedQty": response.get("executedQty", "0"),
        "avgPrice":    avg_price if float(avg_price) > 0 else "N/A (order pending)",
        "price":       response.get("price", "N/A"),
        "origQty":     response.get("origQty", "N/A"),
        "timeInForce": response.get("timeInForce", "N/A"),
    }


def _handle_exception(e: Exception, context: str) -> None:
    """
    Logs the error with context and re-raises a clean exception
    so the CLI layer always gets a human-readable message.
    """
    if isinstance(e, BinanceOrderException):
        logger.error("[%s] Order rejected by Binance: code=%s msg=%s", context, e.code, e.message)
        raise RuntimeError(f"Order rejected by Binance: {e.message} (code {e.code})") from e

    if isinstance(e, BinanceAPIException):
        logger.error("[%s] Binance API error: code=%s msg=%s", context, e.code, e.message)
        raise RuntimeError(f"Binance API error: {e.message} (code {e.code})") from e

    if isinstance(e, Timeout):
        logger.error("[%s] Request timed out.", context)
        raise RuntimeError("Request to Binance timed out. Check your connection.") from e

    if isinstance(e, ConnectionError):
        logger.error("[%s] Network connection error: %s", context, e)
        raise RuntimeError("Could not reach Binance. Check your internet connection.") from e

    if isinstance(e, RequestException):
        logger.error("[%s] HTTP request error: %s", context, e)
        raise RuntimeError(f"HTTP error while contacting Binance: {e}") from e

    # Unexpected — log and bubble up as-is
    logger.error("[%s] Unexpected error: %s", context, e, exc_info=True)
    raise


# ── Order functions ────────────────────────────────────────────────────────────

def place_market_order(
    client: Client,
    symbol: str,
    side: str,
    quantity: float,
) -> dict:
    """
    Places a MARKET order on Binance Futures Testnet.

    Args:
        client:   Authenticated Binance Client (from client.get_client())
        symbol:   Trading pair, e.g. "BTCUSDT"
        side:     "BUY" or "SELL"
        quantity: Amount to trade

    Returns:
        Parsed order result dict with orderId, status, executedQty, avgPrice, etc.

    Raises:
        RuntimeError: with a human-readable message on any API or network failure.
    """
    payload = {
        "symbol":   symbol,
        "side":     side,
        "type":     "MARKET",
        "quantity": quantity,
    }

    logger.info("Placing MARKET order | symbol=%s side=%s quantity=%s", symbol, side, quantity)
    logger.debug("Request payload: %s", payload)

    try:
        response = client.futures_create_order(**payload)
        logger.debug("Raw response: %s", response)

        result = _parse_response(response)
        logger.info(
            "MARKET order placed successfully | orderId=%s status=%s executedQty=%s avgPrice=%s",
            result["orderId"], result["status"], result["executedQty"], result["avgPrice"],
        )
        return result

    except Exception as e:
        _handle_exception(e, context="MARKET_ORDER")


def place_limit_order(
    client: Client,
    symbol: str,
    side: str,
    quantity: float,
    price: float,
) -> dict:
    """
    Places a LIMIT order on Binance Futures Testnet.

    Args:
        client:   Authenticated Binance Client (from client.get_client())
        symbol:   Trading pair, e.g. "BTCUSDT"
        side:     "BUY" or "SELL"
        quantity: Amount to trade
        price:    Limit price

    Returns:
        Parsed order result dict with orderId, status, executedQty, avgPrice, etc.

    Raises:
        RuntimeError: with a human-readable message on any API or network failure.
    """
    payload = {
        "symbol":      symbol,
        "side":        side,
        "type":        "LIMIT",
        "quantity":    quantity,
        "price":       price,
        "timeInForce": "GTC",   # Good Till Cancelled — standard for limit orders
    }

    logger.info(
        "Placing LIMIT order | symbol=%s side=%s quantity=%s price=%s",
        symbol, side, quantity, price,
    )
    logger.debug("Request payload: %s", payload)

    try:
        response = client.futures_create_order(**payload)
        logger.debug("Raw response: %s", response)

        result = _parse_response(response)
        logger.info(
            "LIMIT order placed successfully | orderId=%s status=%s origQty=%s price=%s",
            result["orderId"], result["status"], result["origQty"], result["price"],
        )
        return result

    except Exception as e:
        _handle_exception(e, context="LIMIT_ORDER")