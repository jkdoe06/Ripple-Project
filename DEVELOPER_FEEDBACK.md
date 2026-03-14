# Developer Feedback — Ripple Track @ BabHack
> Submitted for the $250 Best Developer Feedback Bounty

---

## Overview

This feedback covers our experience building two XRPL MVPs during the hackathon:
- **xrpl-primary** — Stablecoin escrow payment app (Payment + TrustSet + EscrowCreate + EscrowFinish)
- **xrpl-lending** — Lending primitives dashboard (XLS-65 VaultCreate + XLS-66 LoanCreate + LoanRepay)

We used Claude AI with the provided MCP server and SKILL.md throughout development.

---

## MCP Server Feedback

### What worked well
- **XRPL transaction building** — The MCP server was excellent at generating well-formed transaction objects. It consistently produced valid `TransactionType` field names, correct field casing (e.g. `FinishAfter` vs `finish_after`), and appropriate numeric formats (drops vs XRP).
- **Error interpretation** — When the XRPL node returned `tecNO_AUTH` or `temDISABLED`, the MCP explained the error clearly and suggested the correct fix (e.g. checking amendment status before sending XLS-65/66 transactions).
- **Testnet awareness** — The MCP correctly defaulted to `wss://s.altnet.rippletest.net:51233` and the correct XRPL epoch offset (`946684800`) without needing correction.
- **Wallet generation** — `client.fundWallet()` pattern was consistently used and worked reliably.

### What didn't work / could be improved
- **Amendment status** — The MCP had no live mechanism to check whether XLS-65 (`SingleAssetVault`) or XLS-66 (`LendingProtocol`) are active on a given testnet. We had to manually call `client.request({command:'feature',...})` to detect this. A built-in `checkAmendment(name)` helper in the MCP would save significant debugging time.
- **XLS-65/66 field names** — Since these are new standards, the MCP occasionally generated slightly wrong field names (e.g. `VaultId` vs `VaultID`). Up-to-date spec files in the MCP context would fix this.
- **No fallback pattern** — When an amendment isn't active, the MCP didn't automatically suggest a simulation/fallback path. We had to design the Escrow-based simulation ourselves. A "simulate with primitives" fallback pattern would be a huge developer experience win.
- **WebSocket reconnection** — The MCP didn't handle `client.disconnect()` on error gracefully. Adding automatic reconnect logic with exponential backoff would help for longer hackathon sessions.

---

## SKILL.md Feedback

### What worked well
- **Structure** — The SKILL.md format (goal → primitives → demo flow) maps naturally to how XRPL transaction sequences actually work. Writing the PLAN.md files following this pattern made it easy to hand code off to AI tools.
- **Role-based thinking** — The Broker / Depositor / Borrower role split in the lending SKILL.md forced us to think about real-world actors rather than just abstract transactions. This actually improved our app design.
- **Primitive tagging** — Listing XLS numbers alongside transaction types (e.g. `VaultCreate (XLS-65)`) was genuinely useful — it gave us the right search terms for the XRPL docs.

### What could be improved
- **Richer examples** — SKILL.md listed the primitives but didn't include example transaction JSON for each one. Even one worked example per primitive (showing correct field names, types, and values) would cut hours of trial-and-error.
- **Amendment guard pattern** — SKILL.md should document the `client.request({command:'feature'})` pattern upfront, since most of the interesting new primitives are amendment-gated. Many teams will hit `temDISABLED` silently.
- **Error taxonomy** — A short appendix of common XRPL error codes and their meaning (e.g. `tecINSUF_RESERVE_LINE` = trust line reserve not met) would be invaluable. We lost ~2 hours debugging these.
- **Frontend examples** — SKILL.md is focused on Node.js/CLI. An HTML + xrpl.js browser example would help hackathon participants quickly build demo-able UIs.
- **Testnet vs Devnet guidance** — When should you use Testnet vs Devnet? This wasn't clear. We eventually settled on Testnet for all demos but Devnet would have been better for testing XLS-65/66 since amendments activate there first.

---

## General Hackathon Developer Experience

### Positive
- The XRPL docs (xrpl.org/docs) are genuinely excellent — well-organized, accurate, with working code examples.
- The testnet faucet is fast and reliable — critical for demos under time pressure.
- The `xrpl` npm package (v3) has a clean API and good TypeScript support.
- The testnet explorer (testnet.xrpl.org) made it easy to verify transactions live during demos.

### Suggestions for future hackathons
1. **Provide a starter repo** with wallets already funded, trust lines set, and one working transaction of each type. First-hour friction kills momentum.
2. **XLS-65/66 Devnet sandbox** — a shared environment with these amendments pre-activated would let participants focus on building rather than waiting for amendment activation.
3. **Judge checklist** — publish a specific checklist of what a "complete testable demo" means for each prize tier. "Working MVP" is ambiguous; "3 on-chain transactions visible on testnet explorer" is not.
4. **Office hours with Ripple devrel** — even a 30-min async Q&A window would unblock many teams.

---

## Summary

The XRPL developer tooling (SDK, faucet, explorer, docs) is genuinely among the best in the blockchain space. The MCP server concept is promising and works well for the stable, well-documented primitives. The main gap is coverage of new amendment-gated features — as XRPL adds powerful new primitives, the MCP and SKILL.md need to stay closely in sync with the actual spec.

The SKILL.md format is a smart idea that we'll likely continue using beyond this hackathon. The role-based breakdown and primitive listing gave us a better mental model of the protocol than reading the raw docs alone.

**Submitted by:** BabHack Ripple Track team
**Date:** March 2026
