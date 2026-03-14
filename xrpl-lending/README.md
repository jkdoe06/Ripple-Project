# XRPL Lending — Lending Primitives Demo

Demonstrates XRPL lending primitives using the Single Asset Vault (XLS-65) and Lending Protocol (XLS-66) standards.

## Roles

| Role | Description |
|---|---|
| **Loan Broker** | Creates and manages the lending vault |
| **Depositor** | Provides liquidity to the vault |
| **Borrower** | Draws a loan against deposited collateral |

## Flow

1. Broker creates a Single Asset Vault (XLS-65)
2. Depositor funds the vault with RLUSD liquidity
3. Borrower draws a loan from the vault
4. Borrower repays the loan with interest

## XRPL Primitives

- **XLS-65** — Single Asset Vault: pooled liquidity management
- **XLS-66** — Lending Protocol: loan issuance and repayment
- **Token Escrow** (optional): collateral locking
- **Credentials** (optional): KYC/identity gating

## Setup

```bash
npm install
node index.js
```

## Network

Deploys to **XRPL Testnet**: `wss://s.altnet.rippletest.net:51233`
