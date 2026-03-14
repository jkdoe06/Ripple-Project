// vault.js — Single Asset Vault helpers (XLS-65)
// XLS-65 introduces VaultCreate, VaultDeposit, VaultWithdraw transactions.
// These are amendment-gated. This module wraps them with clear error messaging.

/**
 * Create a Single Asset Vault (XLS-65).
 * The broker/owner sets the asset type and fee parameters.
 *
 * @param {Client} client
 * @param {Wallet} brokerWallet
 * @param {object} opts
 *   - asset: { currency, issuer }  — the vault's single asset type
 *   - depositFee: string           — basis points fee on deposit (e.g. "100" = 1%)
 */
export async function createVault(client, brokerWallet, { asset, depositFee = "0" }) {
  const tx = {
    TransactionType: "VaultCreate",
    Account: brokerWallet.address,
    Asset: asset,
    // WithdrawalPolicy: "strategyFirst" (default per XLS-65)
    // MPTokenMetadata can be added for LP token metadata
  };

  console.log(`  Creating vault for asset ${asset.currency} (issuer: ${asset.issuer})`);
  const result = await client.submitAndWait(tx, { wallet: brokerWallet });
  console.log(`  VaultCreate tx: ${result.result.hash}  (${result.result.meta.TransactionResult})`);

  // The vault ID is derived from account + sequence
  const vaultID = result.result.meta?.CreatedNode?.NewFields?.VaultID
    ?? `${brokerWallet.address}:${result.result.tx_json.Sequence}`;
  return { result, vaultID };
}

/**
 * Deposit liquidity into a vault (XLS-65).
 * Depositor receives LP shares (MPTokens) in return.
 *
 * @param {Client} client
 * @param {Wallet} depositorWallet
 * @param {string} vaultID
 * @param {object} amount  — { currency, issuer, value }
 */
export async function depositToVault(client, depositorWallet, vaultID, amount) {
  const tx = {
    TransactionType: "VaultDeposit",
    Account: depositorWallet.address,
    VaultID: vaultID,
    Amount: amount,
  };

  console.log(`  Depositing ${amount.value} ${amount.currency} into vault ${vaultID}`);
  const result = await client.submitAndWait(tx, { wallet: depositorWallet });
  console.log(`  VaultDeposit tx: ${result.result.hash}  (${result.result.meta.TransactionResult})`);
  return result;
}

/**
 * Withdraw liquidity from a vault by redeeming LP shares.
 *
 * @param {Client} client
 * @param {Wallet} depositorWallet
 * @param {string} vaultID
 * @param {object} amount  — LP token amount to redeem
 */
export async function withdrawFromVault(client, depositorWallet, vaultID, amount) {
  const tx = {
    TransactionType: "VaultWithdraw",
    Account: depositorWallet.address,
    VaultID: vaultID,
    Amount: amount,
  };

  console.log(`  Withdrawing from vault ${vaultID}`);
  const result = await client.submitAndWait(tx, { wallet: depositorWallet });
  console.log(`  VaultWithdraw tx: ${result.result.hash}  (${result.result.meta.TransactionResult})`);
  return result;
}
