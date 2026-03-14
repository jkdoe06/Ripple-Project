// depositor.js — Depositor role
// Depositor provides RLUSD liquidity to the vault and receives LP shares.

import { depositToVault } from "./vault.js";

/**
 * Depositor funds the vault with RLUSD.
 *
 * @param {Client} client
 * @param {Wallet} depositorWallet
 * @param {string} vaultID
 * @param {string} assetIssuer
 * @param {string} amount           — RLUSD amount to deposit
 */
export async function fundVault(client, depositorWallet, vaultID, assetIssuer, amount) {
  console.log(`  Depositor (${depositorWallet.address}) funding vault with ${amount} RLUSD...`);

  const depositAmount = {
    currency: "RLUSD",
    issuer: assetIssuer,
    value: amount,
  };

  const result = await depositToVault(client, depositorWallet, vaultID, depositAmount);
  console.log(`  Deposit complete. Depositor now holds LP shares.`);
  return result;
}
