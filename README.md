# Binance Futures Testnet Trading Bot

A lightweight Python CLI for placing **Market** and **Limit** orders on the
[Binance Futures Testnet](https://testnet.binancefuture.com) (USDT-M).

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # Binance client wrapper (testnet connection + auth)
│   ├── orders.py          # Order placement logic (market + limit)
│   ├── validators.py      # Input validation for all CLI arguments
│   └── logging_config.py  # Rotating file logger + console logger setup
├── logs/
│   └── trading_bot.log    # Auto-created on first run
├── cli.py                 # CLI entry point
├── .env.example           # Template for API credentials
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Get Testnet API Keys

1. Go to [https://testnet.binancefuture.com](https://testnet.binancefuture.com)
2. Log in with your GitHub account
3. Navigate to **API Key** section and generate a key pair
4. Copy the **API Key** and **Secret Key**

### 2. Clone & Install

```bash
git clone https://github.com/your-username/trading_bot.git
cd trading_bot

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Configure Credentials

```bash
cp .env.example .env
```

Open `.env` and fill in your keys:

```env
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
```

> ⚠️ Never commit your `.env` file. It is already listed in `.gitignore`.

---

## How to Run

### Market Order — BUY

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
```

### Market Order — SELL

```bash
python cli.py --symbol BTCUSDT --side SELL --type MARKET --quantity 0.01
```

### Limit Order — BUY

```bash
python cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.01 --price 80000
```

### Limit Order — SELL

```bash
python cli.py --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.1 --price 3000
```

### Help

```bash
python cli.py --help
```

---

## Example Output

```
────────────────────────────────────────────────────
  ORDER REQUEST SUMMARY
────────────────────────────────────────────────────
  Symbol     : BTCUSDT
  Side       : BUY
  Type       : MARKET
  Quantity   : 0.01
────────────────────────────────────────────────────

────────────────────────────────────────────────────
  ORDER RESPONSE
────────────────────────────────────────────────────
  Order ID     : 3951823641
  Symbol       : BTCUSDT
  Side         : BUY
  Type         : MARKET
  Status       : FILLED
  Orig Qty     : 0.01
  Executed Qty : 0.01
  Avg Price    : 96432.50
────────────────────────────────────────────────────

  ✓ MARKET order placed successfully on Binance Futures Testnet.
```

---

## Logging

All activity is logged to `logs/trading_bot.log`.

- **Console** — INFO level and above (clean, readable output)
- **Log file** — DEBUG level and above (full request/response detail)
- Log file rotates at **5 MB**, keeping the last 3 backups

Sample log entries:

```
2025-01-15 14:23:01 | INFO     | bot.client | Connected to Binance Futures Testnet. Server time: 1736950981000 ms
2025-01-15 14:23:01 | INFO     | bot.orders | Placing MARKET order | symbol=BTCUSDT side=BUY quantity=0.01
2025-01-15 14:23:02 | DEBUG    | bot.orders | Request payload: {'symbol': 'BTCUSDT', 'side': 'BUY', 'type': 'MARKET', 'quantity': 0.01}
2025-01-15 14:23:02 | DEBUG    | bot.orders | Raw response: {'orderId': 3951823641, 'symbol': 'BTCUSDT', ...}
2025-01-15 14:23:02 | INFO     | bot.orders | MARKET order placed successfully | orderId=3951823641 status=FILLED executedQty=0.01 avgPrice=96432.50
```

---

## Error Handling

The bot handles and reports the following failures cleanly:

| Scenario | Message shown |
|---|---|
| Missing API keys | Prompts to fill `.env` |
| Invalid symbol / side / type | Descriptive validation error |
| Price missing for LIMIT order | Reminds user to add `--price` |
| Binance API rejection | Binance error code + message |
| Network timeout | Asks user to check connection |
| No internet connection | Clear connectivity error |

All errors exit with code `1`. Successful runs exit with code `0`.

---

## Assumptions

- All orders are placed on **Binance Futures Testnet** (USDT-M). No live funds are used.
- LIMIT orders use **GTC** (Good Till Cancelled) as the default `timeInForce`.
- Quantity precision follows the symbol's rules on the testnet — if an order is rejected for precision, adjust your `--quantity` accordingly (e.g. use `0.001` instead of `0.0011111`).
- API keys are loaded from a `.env` file in the project root, or from environment variables directly.

---

## Requirements

- Python 3.10+
- Binance Futures Testnet account and API keys