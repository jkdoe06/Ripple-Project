# XRPL Lending — Implementation Plan

## Goal
Demonstrate XRPL lending primitives: vault creation, liquidity deposit, loan draw, and repayment.

## Standards
- **XLS-65** — Single Asset Vault
- **XLS-66** — Lending Protocol (on top of XLS-65)

## Architecture

### Roles
| Role | Wallet | Responsibility |
|---|---|---|
| Broker | `broker.js` | Creates vault, sets parameters |
| Depositor | `depositor.js` | Deposits RLUSD into vault |
| Borrower | `borrower.js` | Draws and repays loans |

### Files
```
apps/xrpl-lending/
├── index.js        # Demo orchestrator
├── broker.js       # Vault creation (XLS-65)
├── depositor.js    # Liquidity deposit
├── borrower.js     # Loan draw & repayment
├── vault.js        # Vault state helpers
└── package.json
```

## Implementation Steps

1. **Broker creates vault** — `VaultCreate` transaction (XLS-65), sets asset type (RLUSD), fee parameters
2. **Depositor funds vault** — `VaultDeposit` transaction, receives LP shares in return
3. **Borrower draws loan** — `LoanCreate` transaction (XLS-66), specifies collateral and amount
4. **Borrower repays** — `LoanRepay` transaction, returns principal + interest
5. **Optional: Credentials** — KYC gating via `CredentialCreate` / `CredentialAccept`

## Notes
- XLS-65/66 are amendment-gated features. Check testnet amendment status before running.
- Fallback: simulate vault/loan logic with Escrow + Payment primitives if amendments not yet active.
