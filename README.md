# Binance Futures Trading Bot

A lightweight Python CLI for placing **Market** and **Limit** orders on
[Binance Demo Trading](https://demo.binance.com/futures) (USDⓈ-M Futures).

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # Binance client wrapper (demo connection + auth)
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

### 1. Get Demo Trading API Keys

1. Go to [https://demo.binance.com/futures](https://demo.binance.com/futures)
2. Log in with your Binance account (Google login works)
3. Click your **Account icon** (top right) → **API Management**
4. Click **Create API** → give it a name → copy the **API Key** and **Secret Key**

> Note: Binance Demo Trading uses virtual funds only. No real money is involved.

### 2. Clone & Install

```bash
git clone https://github.com/your-username/binance-trading-bot.git
cd binance-trading-bot

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Configure Credentials

```bash
cp .env.example .env            # Windows: copy .env.example .env
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
  Order ID     : 13329991393
  Symbol       : BTCUSDT
  Side         : BUY
  Type         : MARKET
  Status       : NEW
  Orig Qty     : 0.0100
  Executed Qty : 0.0000
  Avg Price    : N/A (order pending)
────────────────────────────────────────────────────

  ✓ MARKET order placed successfully on Binance Futures Demo.
```

---

## Logging

All activity is logged to `logs/trading_bot.log`.

- **Console** — INFO level and above (clean, readable output)
- **Log file** — DEBUG level and above (full request/response detail)
- Log file rotates at **5 MB**, keeping the last 3 backups

Sample log entries:

```
2026-05-28 22:31:07 | INFO     | __main__   | CLI invoked | symbol=BTCUSDT side=BUY type=MARKET quantity=0.01 price=None
2026-05-28 22:31:08 | INFO     | bot.client | Connected to Binance Futures Testnet. Server time: 1779987668607 ms
2026-05-28 22:31:08 | INFO     | bot.orders | Placing MARKET order | symbol=BTCUSDT side=BUY quantity=0.01
2026-05-28 22:31:09 | INFO     | bot.orders | MARKET order placed successfully | orderId=13329991393 status=NEW executedQty=0.0000 avgPrice=N/A (order pending)
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

- All orders are placed on **Binance Demo Trading** (USDⓈ-M Futures). No live funds are used.
- The base API URL used is `https://demo-fapi.binance.com` as per Binance's official demo trading API documentation.
- LIMIT orders use **GTC** (Good Till Cancelled) as the default `timeInForce`.
- Market orders on the demo environment may show `status: NEW` briefly before filling — this is expected behaviour of the demo environment, not a bug.
- Quantity precision follows the symbol's rules — if an order is rejected for precision, adjust your `--quantity` accordingly (e.g. use `0.001` instead of `0.0011`).
- API keys are loaded from a `.env` file in the project root, or from environment variables directly.

---

## Requirements

- Python 3.10+
- Binance account (free) for Demo Trading access