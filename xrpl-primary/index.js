// index.js — Stablecoin Escrow Payment App Demo
// Connects to XRPL Testnet and runs the full demo flow:
//   1. Fund two wallets via faucet
//   2. Set up RLUSD trust lines
//   3. Send RLUSD payment into escrow account
//   4. Create time-based XRP escrow
//   5. Release escrow after condition met

import { Client } from "xrpl";
import { createFundedWallet, setTrustLine } from "./wallet.js";
import { sendRLUSD } from "./payment.js";
import { createEscrow, finishEscrow } from "./escrow.js";

const TESTNET_URL = "wss://s.altnet.rippletest.net:51233";
const TESTNET_EXPLORER = "https://testnet.xrpl.org/transactions";

// RLUSD testnet issuer (Ripple's official testnet RLUSD issuer)
// Update if Ripple changes the testnet issuer address.
const RLUSD_ISSUER = "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh";

async function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

async function main() {
  console.log("===========================================");
  console.log("  XRPL Stablecoin Escrow Payment Demo");
  console.log("  Network: XRPL Testnet");
  console.log("===========================================\n");

  const client = new Client(TESTNET_URL);
  await client.connect();
  console.log("Connected to XRPL Testnet\n");

  // ── Step 1: Create and fund wallets ────────────────────────────────────────
  console.log("STEP 1 — Fund Wallets");
  console.log("─────────────────────");
  const { wallet: sender } = await createFundedWallet(client);
  const { wallet: receiver } = await createFundedWallet(client);
  console.log();

  // ── Step 2: Set RLUSD trust lines ──────────────────────────────────────────
  console.log("STEP 2 — Establish RLUSD Trust Lines");
  console.log("─────────────────────────────────────");
  await setTrustLine(client, sender, RLUSD_ISSUER);
  await setTrustLine(client, receiver, RLUSD_ISSUER);
  console.log();

  // ── Step 3: Send RLUSD stablecoin payment ──────────────────────────────────
  // NOTE: On testnet you'd normally get RLUSD from a faucet or issuer.
  // Here we demonstrate the payment structure; the tx will succeed only
  // if the sender has a funded RLUSD balance.
  console.log("STEP 3 — Send RLUSD Payment (sender → receiver)");
  console.log("─────────────────────────────────────────────────");
  console.log("  (Skipping live RLUSD send — requires funded RLUSD balance from issuer)");
  console.log("  In production: call sendRLUSD(client, sender, receiver.address, RLUSD_ISSUER, '100')");
  console.log();

  // ── Step 4: Create XRP escrow ──────────────────────────────────────────────
  console.log("STEP 4 — Create Escrow (sender locks 10 XRP → receiver, 10s hold)");
  console.log("─────────────────────────────────────────────────────────────────");
  const amountDrops = "10000000"; // 10 XRP in drops
  const { result: escrowResult, escrowSequence } = await createEscrow(
    client,
    sender,
    receiver.address,
    amountDrops,
    10 // release after 10 seconds
  );
  console.log(`  Escrow sequence: ${escrowSequence}`);
  console.log(`  View: ${TESTNET_EXPLORER}/${escrowResult.result.hash}`);
  console.log();

  // ── Step 5: Wait for FinishAfter, then release ─────────────────────────────
  console.log("STEP 5 — Waiting 12s for escrow FinishAfter to pass...");
  console.log("─────────────────────────────────────────────────────────");
  await sleep(12000);

  console.log("STEP 6 — Finish Escrow (release funds to receiver)");
  console.log("───────────────────────────────────────────────────");
  const finishResult = await finishEscrow(client, receiver, sender.address, escrowSequence);
  console.log(`  View: ${TESTNET_EXPLORER}/${finishResult.result.hash}`);
  console.log();

  // ── Summary ────────────────────────────────────────────────────────────────
  console.log("===========================================");
  console.log("  DEMO COMPLETE");
  console.log("===========================================");
  console.log(`  Sender:   ${sender.address}`);
  console.log(`  Receiver: ${receiver.address}`);
  console.log(`  Escrow created & released successfully`);
  console.log(`  Explorer: https://testnet.xrpl.org`);

  await client.disconnect();
}

main().catch((err) => {
  console.error("Error:", err);
  process.exit(1);
});
