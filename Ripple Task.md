# 🌊 Ripple Track — Task Brief ($4k total)

> Saved from Notion: EXTERNAL Tracks & Judges
> Strategy: lots of small wins — target every prize tier

---

## 🥇 Primary Challenge — $3,000 pool
**Prizes:** $2,000 (1st) · $750 (2nd) · $250 Best Developer Feedback bounty

### What to build
An MVP that leverages **multiple** XRP Ledger core features to solve a real-world problem.

### What success looks like
- Stablecoin flows using **RLUSD**
- Combination of XRPL native features:
  - Lending Protocol + Single Asset Vault
  - **Smart escrow**
  - Multi-purpose tokens
  - **Batch transactions**
  - TokenEscrow
- Payment apps leveraging stablecoins, microfinance, tokenization
- Multi-feature integrations (reflect real mainnet complexity)

### Hard requirements
- [ ] Working, testable MVP
- [ ] **Publicly available on GitHub** with detailed README
- [ ] Deployed on **XRPL Testnet or Devnet**
- [ ] Combines multiple XRPL primitives (not a single-feature demo)

### Feedback bounty ($250)
Submit developer feedback at the provided link covering:
- What worked, what didn't, what could be better
- Feedback on the **MCP server**
- Feedback on the usefulness of **SKILL.md**

---

## 🥈 Secondary Challenge — $750
**"Put XRPL's Lending Primitives to Work"**

### Primitives
- **XLS-65** — Single Asset Vault: pool liquidity from multiple depositors
- **XLS-66** — Lending Protocol: fixed-term, uncollateralized loans from pooled capital

### Use cases
- Private credit, trade finance, PayFi

### Ideas
- Lending dashboard: broker creates vault → depositor funds → borrower draws & repays
- PayFi app: stablecoin flows via pooled vault liquidity
- Yield-tracking interface for depositors
- Bonus: pair with **Token Escrow (XLS-85)** (collateralised loans) or **Credentials (XLS-70)** (permissioned SAV/LP flows)

### Hard requirements
- [ ] Deploy on XRPL Testnet or Devnet
- [ ] Demonstrate **at least one complete, testable loan or vault flow**

---

## 🎯 Win Strategy (Lots of Small Wins)

| Prize | Target | App | Effort |
|---|---|---|---|
| $750 Primary 2nd | Solid working escrow+payment MVP | `apps/xrpl-primary` | Medium |
| $750 Secondary | Working vault+loan demo | `apps/xrpl-lending` | Medium |
| $250 Feedback | Write great MCP+SKILL.md feedback | `DEVELOPER_FEEDBACK.md` | Low |

**Total target: ~$1,750**

---

## 📁 Files

```
apps/xrpl-primary/
  demo.html        ← Spider-Verse UI demo
  index.js         ← CLI runner
  escrow.js        ← EscrowCreate/Finish/Cancel
  payment.js       ← RLUSD payment
  wallet.js        ← Faucet + TrustSet
  package.json
  README.md
  PLAN.md

apps/xrpl-lending/
  demo.html        ← Spider-Verse lending dashboard
  index.js         ← CLI runner
  broker.js        ← VaultCreate (XLS-65)
  depositor.js     ← VaultDeposit
  borrower.js      ← LoanCreate + LoanRepay (XLS-66)
  vault.js         ← Vault helpers
  package.json
  README.md
  PLAN.md

DEVELOPER_FEEDBACK.md  ← $250 bounty submission
```
