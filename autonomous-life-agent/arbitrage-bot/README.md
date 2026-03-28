# Arbitrage Bot

24/7 crypto arbitrage bot that finds price differences across exchanges and profits from them. Small margins per trade ($0.50-5), but it runs constantly and stacks.

## How It Makes Money

Three strategies running in parallel:

| Strategy | How It Works | Profit/Trade | Speed |
|----------|-------------|-------------|-------|
| **Cross-Exchange** | BTC is $50,010 on Coinbase but $50,050 on Kraken → buy low, sell high | $0.50-5 | Moderate |
| **Triangular** | USDT→BTC→ETH→USDT within one exchange, if the math works out to more USDT | $0.10-2 | Fast |
| **Spread Scalp** | When bid-ask spread is 2x wider than normal → buy bid, sell ask | $0.10-1 | Very fast |

The bot runs all three simultaneously and picks the best opportunity each cycle.

## Quick Start (One Click)

```bash
cd arbitrage-bot
python setup.py    # Interactive wizard — installs deps, asks for API keys
python start.py    # Runs forever (Ctrl+C to stop)
```

That's it. The setup wizard walks you through everything.

## Commands

```bash
python start.py              # Run in foreground (see all trades live)
python start.py --bg         # Run as background daemon (runs forever)
python start.py --stop       # Stop the daemon
python start.py --status     # Check if running + quick P&L
python bot.py --report       # Full P&L report
python bot.py --scan-only    # Just scan, don't execute (watch mode)
```

## What You Need

1. **Accounts on 1-2 crypto exchanges** (Coinbase + Kraken recommended for US)
2. **API keys** with trade permission (setup wizard handles this)
3. **$50-200 starting capital** split across your exchanges
4. **A machine that stays on** (your laptop, a VPS, a Raspberry Pi)

## How Profits Stack

With $200 capital across 2 exchanges at default settings:

| Scenario | Trades/Day | Avg Profit | Daily | Monthly |
|----------|-----------|-----------|-------|---------|
| Conservative | 5-10 | $0.30 | $1.50-3 | $45-90 |
| Average | 20-50 | $0.50 | $10-25 | $300-750 |
| Good market conditions | 50-100+ | $0.75 | $37-75 | $1,125-2,250 |

Results vary based on market volatility (more volatility = more opportunities).

## Safety Features

- **Paper trading by default** — runs with fake money until you switch to live
- **Daily loss limit** — stops trading if down $10 in a day
- **Consecutive loss circuit breaker** — pauses after 5 losses in a row
- **Max trade cap** — $25 per trade default (configurable)
- **Max daily trades** — 200 cap
- **Full audit log** — every trade logged to `logs/trades.json`
- **No withdrawal permissions** — API keys should only have trade access

## Configuration (.env)

```bash
# Key settings you can tune:
MIN_SPREAD=0.003        # 0.3% minimum spread to trade (raise = fewer but safer trades)
MAX_TRADE_USD=25.00     # Max USD per trade
MAX_TOTAL_CAPITAL=200   # Total capital budget
SCAN_INTERVAL=5         # Seconds between scans
LIVE_TRADING=false      # false = paper trading, true = real money
PAIRS=BTC/USDT,ETH/USDT,SOL/USDT,XRP/USDT,DOGE/USDT,AVAX/USDT,LINK/USDT,DOT/USDT
```

## Exchange Setup

### Coinbase (Recommended — US)
1. Go to https://www.coinbase.com/settings/api
2. Create API key with "Trade" permission only
3. Do NOT enable "Transfer" or "Withdraw"

### Kraken (Recommended — US)
1. Go to https://www.kraken.com/u/security/api
2. Create key with "Create & modify orders" only
3. Do NOT enable "Withdraw funds"

### Deposit Funds
Split your capital across exchanges:
- $100 USDT on Coinbase
- $100 USDT on Kraken
- (Or any split you prefer)

## Project Structure

```
arbitrage-bot/
├── setup.py          # One-click setup wizard
├── start.py          # Launcher (foreground/background/status)
├── bot.py            # Main bot loop
├── config.py         # Settings from .env
├── tracker.py        # P&L tracking + circuit breakers
├── logger.py         # Logging setup
├── exchanges/
│   └── manager.py    # Multi-exchange connection + order execution
├── strategies/
│   ├── cross_exchange.py  # Buy low on A, sell high on B
│   ├── triangular.py      # 3-pair loops within one exchange
│   └── spread_scalp.py    # Wide spread detection + capture
├── logs/
│   ├── trades.json        # Every trade recorded
│   ├── summary.json       # Running P&L summary
│   ├── bot_YYYYMMDD.log   # Daily log files
│   └── bot.pid            # Daemon PID file
└── .env                   # Your API keys (never commit this)
```

## FAQ

**Q: Is this legal?**
A: Yes. Arbitrage trading is legal in all jurisdictions. You're buying and selling on legitimate exchanges.

**Q: Can I lose money?**
A: In theory yes — if prices move against you between buy and sell. The bot has safety limits to minimize this. Paper trade first.

**Q: How much do I need to start?**
A: $50 minimum across 2 exchanges. $200 recommended for meaningful returns.

**Q: Does it work while I sleep?**
A: Yes. Run `python start.py --bg` and it runs until you stop it. Crypto markets are 24/7.

**Q: What if an exchange goes down?**
A: The bot catches errors and continues scanning other exchanges. No crash.
