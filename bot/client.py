import os
from binance.client import Client
from binance.exceptions import BinanceAPIException
from dotenv import load_dotenv

from bot.logging_config import setup_logger

logger = setup_logger(__name__)

# Binance Futures Testnet base URLs
TESTNET_API_URL = "https://testnet.binancefuture.com"
TESTNET_STREAM_URL = "wss://stream.binancefuture.com"


def get_client() -> Client:
    """
    Reads API credentials from the environment (or .env file),
    creates and returns a Binance Client pointed at the Futures Testnet.

    Raises:
        EnvironmentError: if API keys are missing from the environment.
        BinanceAPIException: if the client cannot authenticate with the testnet.
        ConnectionError: if the testnet cannot be reached.
    """
    load_dotenv()  # loads .env if present; silently skips if not

    api_key = os.getenv("BINANCE_API_KEY", "").strip()
    api_secret = os.getenv("BINANCE_API_SECRET", "").strip()

    if not api_key or not api_secret:
        logger.error("BINANCE_API_KEY or BINANCE_API_SECRET is missing from environment.")
        raise EnvironmentError(
            "API credentials not found. "
            "Copy .env.example → .env and fill in your Testnet keys."
        )

    logger.debug("Initialising Binance Futures Testnet client.")

    try:
        client = Client(
            api_key=api_key,
            api_secret=api_secret,
            testnet=True,          # points the client at Futures Testnet endpoints
        )

        # Override base URLs explicitly to be sure we never hit live Binance
        client.API_URL = TESTNET_API_URL + "/fapi"
        client.FUTURES_URL = TESTNET_API_URL + "/fapi"

        # Quick connectivity/auth check — fetches server time, very lightweight
        server_time = client.futures_time()
        logger.info(
            "Connected to Binance Futures Testnet. "
            "Server time: %s ms", server_time["serverTime"]
        )

    except BinanceAPIException as e:
        logger.error("Binance API error during client initialisation: %s", e)
        raise

    except Exception as e:
        logger.error("Failed to connect to Binance Futures Testnet: %s", e)
        raise ConnectionError(
            f"Could not reach Binance Futures Testnet at {TESTNET_API_URL}. "
            "Check your internet connection and API keys."
        ) from e

    return client