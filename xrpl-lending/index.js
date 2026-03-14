// index.js — XRPL Lending Primitives Demo
// Orchestrates the full lending flow:
//   1. Broker creates a Single Asset Vault (XLS-65)
//   2. Depositor funds the vault with RLUSD
//   3. Borrower draws a loan (XLS-66)
//   4. Borrower repays the loan

import { Client } from "xrpl";
import { setupLendingVault } from "./broker.js";
import { fundVault } from "./depositor.js";
import { drawLoan, repayLoan } from "./borrower.js";

const TESTNET_URL = "wss://s.altnet.rippletest.net:51233";
const TESTNET_EXPLORER = "https://testnet.xrpl.org/transactions";

// RLUSD testnet issuer — update if Ripple changes this
const RLUSD_ISSUER = "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh";

async function createFundedWallet(client, label) {
  console.log(`  Funding wallet for [${label}]...`);
  const { wallet, balance } = await client.fundWallet();
  console.log(`  ${label}: ${wallet.address}  (${balance} XRP)`);
  return wallet;
}

async function setTrustLine(client, wallet, issuer) {
  const tx = {
    TransactionType: "TrustSet",
    Account: wallet.address,
    LimitAmount: { currency: "RLUSD", issuer, value: "1000000" },
  };
  const r = await client.submitAndWait(tx, { wallet });
  console.log(`  TrustSet (${wallet.address}): ${r.result.meta.TransactionResult}`);
}

// ─── Amendment Guard ──────────────────────────────────────────────────────────
// XLS-65/66 are not yet active on all XRPL networks.
// This checks if the amendment is enabled; if not, falls back to a simulation.
async function checkAmendment(client, amendmentName) {
  try {
    const resp = await client.request({ command: "feature", feature: amendmentName });
    return resp.result?.[amendmentName]?.enabled === true;
  } catch {
    return false;
  }
}

// ─── Fallback simulation (Escrow-based) ───────────────────────────────────────
async function simulateLendingWithEscrow(client, broker, depositor, borrower) {
  console.log("\n  [FALLBACK] XLS-65/66 not active — simulating with Escrow + Payment\n");

  const XRPL_EPOCH_OFFSET = 946684800;
  const finishAfter = Math.floor(Date.now() / 1000) - XRPL_EPOCH_OFFSET + 20;

  // Depositor locks funds in escrow (simulates vault deposit)
  const escrowTx = {
    TransactionType: "EscrowCreate",
    Account: depositor.address,
    Destination: borrower.address,
    Amount: "5000000", // 5 XRP simulating loan disbursement
    FinishAfter: finishAfter,
  };
  const escrowResult = await client.submitAndWait(escrowTx, { wallet: depositor });
  const seq = escrowResult.result.tx_json.Sequence;
  console.log(`  [Sim] EscrowCreate (deposit→loan): ${escrowResult.result.hash}`);

  // Borrower finishes escrow after 22s (simulates loan draw)
  console.log("  [Sim] Waiting 22s for escrow release...");
  await new Promise((r) => setTimeout(r, 22000));

  const finishTx = {
    TransactionType: "EscrowFinish",
    Account: borrower.address,
    Owner: depositor.address,
    OfferSequence: seq,
  };
  const finishResult = await client.submitAndWait(finishTx, { wallet: borrower });
  console.log(`  [Sim] EscrowFinish (loan drawn): ${finishResult.result.hash}`);

  // Borrower repays via direct Payment (simulates loan repayment)
  const repayTx = {
    TransactionType: "Payment",
    Account: borrower.address,
    Destination: depositor.address,
    Amount: "5100000", // 5.1 XRP (principal + simulated interest)
  };
  const repayResult = await client.submitAndWait(repayTx, { wallet: borrower });
  console.log(`  [Sim] Payment (repayment + interest): ${repayResult.result.hash}`);

  return { escrowResult, finishResult, repayResult };
}

// ─── Main ──────────────────────────────────────────────────────────────────────
async function main() {
  console.log("===========================================");
  console.log("  XRPL Lending Primitives Demo");
  console.log("  XLS-65 Single Asset Vault + XLS-66 Lending");
  console.log("  Network: XRPL Testnet");
  console.log("===========================================\n");

  const client = new Client(TESTNET_URL);
  await client.connect();
  console.log("Connected to XRPL Testnet\n");

  // ── Step 1: Fund all role wallets ────────────────────────────────────────
  console.log("STEP 1 — Fund Wallets (Broker / Depositor / Borrower)");
  console.log("──────────────────────────────────────────────────────");
  const broker = await createFundedWallet(client, "Broker");
  const depositor = await createFundedWallet(client, "Depositor");
  const borrower = await createFundedWallet(client, "Borrower");
  console.log();

  // ── Step 2: Trust lines ──────────────────────────────────────────────────
  console.log("STEP 2 — Establish RLUSD Trust Lines");
  console.log("─────────────────────────────────────");
  await setTrustLine(client, broker, RLUSD_ISSUER);
  await setTrustLine(client, depositor, RLUSD_ISSUER);
  await setTrustLine(client, borrower, RLUSD_ISSUER);
  console.log();

  // ── Check amendments ─────────────────────────────────────────────────────
  const hasVault = await checkAmendment(client, "SingleAssetVault");
  const hasLending = await checkAmendment(client, "LendingProtocol");

  if (hasVault && hasLending) {
    // ── Step 3: Broker creates vault (XLS-65) ──────────────────────────────
    console.log("STEP 3 — Broker Creates Single Asset Vault (XLS-65)");
    console.log("─────────────────────────────────────────────────────");
    const { vaultID } = await setupLendingVault(client, broker, RLUSD_ISSUER);
    console.log();

    // ── Step 4: Depositor funds vault ──────────────────────────────────────
    console.log("STEP 4 — Depositor Funds Vault");
    console.log("──────────────────────────────");
    await fundVault(client, depositor, vaultID, RLUSD_ISSUER, "1000");
    console.log();

    // ── Step 5: Borrower draws loan (XLS-66) ──────────────────────────────
    console.log("STEP 5 — Borrower Draws Loan (XLS-66)");
    console.log("──────────────────────────────────────");
    const borrowAmount = { currency: "RLUSD", issuer: RLUSD_ISSUER, value: "500" };
    const { loanID } = await drawLoan(client, borrower, vaultID, borrowAmount, null);
    console.log();

    // ── Step 6: Borrower repays ────────────────────────────────────────────
    console.log("STEP 6 — Borrower Repays Loan");
    console.log("─────────────────────────────");
    const repayAmount = { currency: "RLUSD", issuer: RLUSD_ISSUER, value: "510" }; // +2% interest
    await repayLoan(client, borrower, loanID, repayAmount);
    console.log();

  } else {
    console.log("  XLS-65/66 amendments not yet active on this network.");
    await simulateLendingWithEscrow(client, broker, depositor, borrower);
  }

  // ── Summary ────────────────────────────────────────────────────────────────
  console.log("\n===========================================");
  console.log("  DEMO COMPLETE");
  console.log("===========================================");
  console.log(`  Broker:    ${broker.address}`);
  console.log(`  Depositor: ${depositor.address}`);
  console.log(`  Borrower:  ${borrower.address}`);
  console.log(`  Explorer:  https://testnet.xrpl.org`);

  await client.disconnect();
}

main().catch((err) => {
  console.error("Error:", err);
  process.exit(1);
});
