// broker.js — Loan Broker role
// The broker creates and manages the lending vault (XLS-65/66).

import { createVault } from "./vault.js";

/**
 * Broker sets up the lending vault for a given asset.
 *
 * @param {Client} client
 * @param {Wallet} brokerWallet
 * @param {string} assetIssuer  — RLUSD issuer address
 */
export async function setupLendingVault(client, brokerWallet, assetIssuer) {
  console.log("  Broker is creating the Single Asset Vault (XLS-65)...");
  const asset = {
    currency: "RLUSD",
    issuer: assetIssuer,
  };

  const { result, vaultID } = await createVault(client, brokerWallet, { asset });
  console.log(`  Vault ID: ${vaultID}`);
  return { vaultID, txHash: result.result.hash };
}
