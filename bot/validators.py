from bot.logging_config import setup_logger

logger = setup_logger(__name__)

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT"}


def validate_symbol(symbol: str) -> str:
    """
    Validates and normalises the trading symbol.
    - Must be a non-empty string
    - Uppercased automatically (forgiving of lowercase input)

    Returns the cleaned symbol string.
    Raises ValueError on failure.
    """
    if not isinstance(symbol, str) or not symbol.strip():
        raise ValueError("Symbol must be a non-empty string (e.g. BTCUSDT).")

    cleaned = symbol.strip().upper()

    # Basic sanity: only letters allowed in a Binance symbol
    if not cleaned.isalpha():
        raise ValueError(
            f"Invalid symbol '{cleaned}'. "
            "Symbols should contain only letters (e.g. BTCUSDT, ETHUSDT)."
        )

    logger.debug("Symbol validated: %s", cleaned)
    return cleaned


def validate_side(side: str) -> str:
    """
    Validates the order side.
    - Must be BUY or SELL (case-insensitive)

    Returns the uppercased side string.
    Raises ValueError on failure.
    """
    if not isinstance(side, str) or not side.strip():
        raise ValueError("Side must be BUY or SELL.")

    cleaned = side.strip().upper()

    if cleaned not in VALID_SIDES:
        raise ValueError(
            f"Invalid side '{cleaned}'. "
            f"Accepted values: {', '.join(sorted(VALID_SIDES))}."
        )

    logger.debug("Side validated: %s", cleaned)
    return cleaned


def validate_order_type(order_type: str) -> str:
    """
    Validates the order type.
    - Must be MARKET or LIMIT (case-insensitive)

    Returns the uppercased order type string.
    Raises ValueError on failure.
    """
    if not isinstance(order_type, str) or not order_type.strip():
        raise ValueError("Order type must be MARKET or LIMIT.")

    cleaned = order_type.strip().upper()

    if cleaned not in VALID_ORDER_TYPES:
        raise ValueError(
            f"Invalid order type '{cleaned}'. "
            f"Accepted values: {', '.join(sorted(VALID_ORDER_TYPES))}."
        )

    logger.debug("Order type validated: %s", cleaned)
    return cleaned


def validate_quantity(quantity: str | float) -> float:
    """
    Validates the order quantity.
    - Must be convertible to a positive float
    - Must be greater than zero

    Returns the quantity as a float.
    Raises ValueError on failure.
    """
    try:
        qty = float(quantity)
    except (TypeError, ValueError):
        raise ValueError(
            f"Invalid quantity '{quantity}'. "
            "Quantity must be a positive number (e.g. 0.01)."
        )

    if qty <= 0:
        raise ValueError(
            f"Quantity must be greater than zero. Got: {qty}."
        )

    logger.debug("Quantity validated: %s", qty)
    return qty


def validate_price(price: str | float | None, order_type: str) -> float | None:
    """
    Validates the order price.
    - Required (and must be a positive float) when order_type is LIMIT
    - Must be None or omitted for MARKET orders

    Returns the price as a float for LIMIT orders, or None for MARKET.
    Raises ValueError on failure.
    """
    if order_type == "MARKET":
        if price is not None:
            logger.debug("Price ignored for MARKET order.")
        return None

    # LIMIT — price is required
    if price is None:
        raise ValueError(
            "Price is required for LIMIT orders. "
            "Provide it with --price (e.g. --price 80000)."
        )

    try:
        p = float(price)
    except (TypeError, ValueError):
        raise ValueError(
            f"Invalid price '{price}'. "
            "Price must be a positive number (e.g. 80000.50)."
        )

    if p <= 0:
        raise ValueError(
            f"Price must be greater than zero. Got: {p}."
        )

    logger.debug("Price validated: %s", p)
    return p


def validate_all(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str | float,
    price: str | float | None = None,
) -> dict:
    """
    Runs all validators in sequence and returns a clean params dict.
    This is the single entry point the CLI and tests should call.

    Returns:
        {
            "symbol":     str,
            "side":       str,
            "order_type": str,
            "quantity":   float,
            "price":      float | None,
        }

    Raises ValueError (with a descriptive message) on the first failure.
    """
    logger.debug("Starting full input validation.")

    validated_type = validate_order_type(order_type)   # validate type first — needed by price check

    params = {
        "symbol":     validate_symbol(symbol),
        "side":       validate_side(side),
        "order_type": validated_type,
        "quantity":   validate_quantity(quantity),
        "price":      validate_price(price, validated_type),
    }

    logger.debug("All inputs validated successfully: %s", params)
    return params