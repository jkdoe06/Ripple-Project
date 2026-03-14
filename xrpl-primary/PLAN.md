# XRPL Primary — Implementation Plan

## Goal
Build a stablecoin escrow payment MVP using XRPL primitives on Testnet/Devnet.

## Architecture

### Components
- `index.js` — Entry point, demo runner
- `wallet.js` — Wallet creation and funding via faucet
- `escrow.js` — Escrow create, finish, cancel logic
- `payment.js` — RLUSD stablecoin payment logic

### XRPL Primitives Used
| Primitive | Purpose |
|---|---|
| RLUSD (IOU) | Stablecoin transfer |
| EscrowCreate | Lock funds with condition |
| EscrowFinish | Release funds when condition met |
| Payment | Direct token transfer |
| Batch | Group multiple transactions |

## Implementation Steps

1. **Wallet Setup** — Generate sender/receiver wallets, fund via testnet faucet
2. **Trust Line** — Establish RLUSD trust line between accounts
3. **Payment** — Send RLUSD from sender to escrow account
4. **EscrowCreate** — Lock funds with a finish-after timestamp
5. **EscrowFinish** — Release after condition is met
6. **Demo Output** — Log all tx hashes and ledger state

## XRPL Testnet
- WebSocket: `wss://s.altnet.rippletest.net:51233`
- Faucet: `https://faucet.altnet.rippletest.net/accounts`
- Explorer: `https://testnet.xrpl.org`
