# XRPL Multi-Primitive Demo

> **Ripple Hackathon Submission** — Primary + Secondary Track
> Live on **XRPL Testnet** · Zero backend · Pure browser HTML

---

## What This Is

Two fully working demos built on the XRP Ledger, running entirely in the browser with no backend, no deployment pipeline, and no wallet extension required. Both demos auto-fund wallets from the testnet faucet, execute real on-chain transactions, and link every hash directly to the Testnet Explorer.

| Demo | Track | Primitives |
|---|---|---|
| [`xrpl-primary`](./xrpl-primary/) | Primary Challenge | `Payment` · `TrustSet` · `EscrowCreate` · `EscrowFinish` |
| [`xrpl-lending`](./xrpl-lending/) | Secondary Challenge | `VaultCreate (XLS-65)` · `VaultDeposit` · `LoanCreate (XLS-66)` · `LoanRepay` |

---

## Live Demos

Open either `demo.html` directly in your browser — no server needed.

```
xrpl-primary/demo.html   →  Escrow Payment demo
xrpl-lending/demo.html   →  Lending Vault cycle
```

Both demos connect to `wss://s.altnet.rippletest.net:51233` (XRPL Testnet). All funds are free testnet XRP.

---

## Demo 1 — Escrow Payment (`xrpl-primary`)

A 5-step Spider-Verse themed escrow payment flow using four XRPL primitives.

```
① Fund        Fund two wallets via testnet faucet (~10s)
② Trust       TrustSet RLUSD on both wallets
③ Escrow      EscrowCreate — lock XRP with a time-based FinishAfter
④ Release     Countdown timer → EscrowFinish releases funds
⑤ Done        All TX hashes shown with Explorer links
```

**Key features:**
- Live balance tracking — sender balance displayed in real time after each step
- Input validation — escrow amount capped at `balance − 12 XRP` (XRPL reserve)
- RLUSD correctly encoded as 40-char hex (`524C555344000000000000000000000000000000`)
- `FinishAfter` includes a +10s ledger-close buffer to prevent `tecNO_PERMISSION`
- Sequence guard — `EscrowFinish` refused if `escSeq` is null, with friendly error

---

## Demo 2 — Lending Vault (`xrpl-lending`)

A 6-step institutional DeFi cycle across three roles: Broker, Depositor, and Borrower.

```
① Fund        Three wallets funded via faucet (~20s)
② Vault       Broker creates a Single Asset Vault (XLS-65 / EscrowCreate proxy)
③ Deposit     Depositor funds the vault with XRP
④ Borrow      Borrower draws a loan (XLS-66 / Payment proxy)
⑤ Repay       Borrower repays principal + 2% interest
⑥ Done        Full cycle summary with all TX hashes
```

**Key features:**
- Pool size tracked in state — borrow is capped at what was actually deposited
- Deposit validated against depositor's live balance minus XRPL reserve
- Repay validated against borrower's live balance before submission
- XLS-65/66 not yet live on testnet → graceful EscrowCreate + Payment simulation, labelled `[SIM]`
- Reset button fully restores all button states for a clean second run

---

## How to Run

### Browser (recommended — no install)

1. Clone or download this repo
2. Open `xrpl-primary/demo.html` or `xrpl-lending/demo.html` in Chrome / Firefox
3. Click **⚡ Fund** and follow the steps

That's it. No npm, no server, no config.

### Node CLI (optional)

Each app also ships a Node.js CLI version for terminal use:

```bash
# Primary escrow demo
cd xrpl-primary
npm install
node index.js

# Lending vault demo
cd xrpl-lending
npm install
node index.js
```

Requires **Node.js ≥ 18** and an internet connection to reach XRPL Testnet.

---

## Tech Stack

| Layer | Choice | Why |
|---|---|---|
| Ledger | XRPL Testnet | Native escrow, trust lines, and lending primitives |
| SDK | xrpl.js v3 | Official Ripple SDK, CDN-loaded in browser |
| Frontend | Vanilla HTML/CSS/JS | Zero dependencies, instant load, fully auditable |
| Fonts | Bangers + Space Mono | Into the Spider-Verse aesthetic |
| Node CLI | Node.js ESM | Optional terminal flow for devs |

---

## Project Structure

```
├── README.md                  ← You are here
├── LICENSE
├── .gitignore
├── DEVELOPER_FEEDBACK.md      ← $250 feedback bounty submission
├── PITCH_SCRIPT.md            ← 2-minute video pitch script
│
├── xrpl-primary/              ← Primary Track submission
│   ├── demo.html              ← ★ Browser demo (open this)
│   ├── index.js               ← Node CLI entry
│   ├── wallet.js              ← Wallet funding helpers
│   ├── payment.js             ← Payment + TrustSet logic
│   ├── escrow.js              ← EscrowCreate + EscrowFinish logic
│   ├── package.json
│   ├── PLAN.md                ← Implementation plan
│   └── README.md
│
└── xrpl-lending/              ← Secondary Track submission
    ├── demo.html              ← ★ Browser demo (open this)
    ├── index.js               ← Node CLI entry
    ├── broker.js              ← Vault creation logic
    ├── depositor.js           ← Vault deposit logic
    ├── borrower.js            ← Loan draw + repay logic
    ├── vault.js               ← XLS-65/66 helpers + fallback
    ├── package.json
    ├── PLAN.md                ← Implementation plan
    └── README.md
```

---

## XRPL Primitives Reference

### Primary Track

| Primitive | XRPL Type | Purpose |
|---|---|---|
| `TrustSet` | Native | Enable RLUSD on both wallets. Currency encoded as 40-char hex. |
| `EscrowCreate` | Native | Lock XRP with `FinishAfter` timestamp |
| `EscrowFinish` | Native | Release escrowed funds after hold period |
| `Payment` | Native | Fund wallets via faucet |

### Secondary Track

| Primitive | Standard | Purpose |
|---|---|---|
| `VaultCreate` | XLS-65 | Create a Single Asset Vault (pooled liquidity) |
| `VaultDeposit` | XLS-65 | Depositor provides liquidity, receives LP shares |
| `LoanCreate` | XLS-66 | Borrower draws a loan from the vault |
| `LoanRepay` | XLS-66 | Borrower repays principal + interest |

> **Note:** XLS-65 and XLS-66 are amendment-gated and not yet active on testnet as of this submission. Both demos fall back to `EscrowCreate + Payment` to prove the capital flow, labelled clearly as `[SIM]` in the console.

---

## Balance Validation & Safety

Both demos enforce real-time balance checks before any transaction is submitted.

**XRPL reserves** that are accounted for:
- `10 XRP` — base account reserve (cannot be spent)
- `2 XRP` — per owned object reserve (EscrowCreate adds one object)

**Checks performed:**

| Demo | Step | Check |
|---|---|---|
| Primary | EscrowCreate | `amount ≤ senderBalance − 12 XRP` |
| Lending | VaultDeposit | `amount ≤ depositorBalance − 12 XRP` |
| Lending | LoanCreate | `loan ≤ poolXRP` (amount actually deposited) |
| Lending | LoanRepay | `repay ≤ borrowerBalance − 10 XRP` |

If any check fails, a red warning appears on the input and the transaction is not submitted.

---

## Known Testnet Quirks

| Issue | Cause | Fix Applied |
|---|---|---|
| `tecNO_PERMISSION` on EscrowFinish | `FinishAfter` already past by validation time | Added +10s ledger-close buffer |
| `temMALFORMED` on TrustSet | RLUSD is 5 chars, not valid 3-char ISO | Encoded as 40-char hex |
| `tecNO_PERMISSION` from XLS-65/66 | Amendment not active on testnet | EscrowCreate + Payment simulation |
| `undefined` OfferSequence | xrpl.js v3 puts Sequence at `r.result.Sequence` not `r.result.tx_json.Sequence` | Null-coalescing fallback |
| Error on pre-validation failure | `r.result.meta` is undefined before ledger accepts tx | Optional chaining `?.TransactionResult ?? 'unknown'` throughout |

---

## Developer Feedback

See [`DEVELOPER_FEEDBACK.md`](./DEVELOPER_FEEDBACK.md) for the full $250 bounty submission covering:
- MCP server strengths and gaps (amendment detection, XLS field names)
- SKILL.md format feedback (what worked, what needs worked examples)

---

## Pitch

See [`PITCH_SCRIPT.md`](./PITCH_SCRIPT.md) for a ready-to-record 2-minute demo pitch script with delivery notes.

---

## Network

- **Testnet WebSocket:** `wss://s.altnet.rippletest.net:51233`
- **Testnet Explorer:** https://testnet.xrpl.org
- **Testnet Faucet:** https://faucet.altnet.rippletest.net/accounts

---

## License

MIT — see [LICENSE](./LICENSE)
