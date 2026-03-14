// wallet.js — Wallet creation and testnet funding
import { Client, Wallet } from "xrpl";

const TESTNET_URL = "wss://s.altnet.rippletest.net:51233";

/**
 * Fund a new wallet via XRPL testnet faucet.
 * Returns { wallet, balance }
 */
export async function createFundedWallet(client) {
  console.log("  Requesting testnet faucet funding...");
  const { wallet, balance } = await client.fundWallet();
  console.log(`  Wallet: ${wallet.address}  Balance: ${balance} XRP`);
  return { wallet, balance };
}

/**
 * Establish a trust line so an account can hold RLUSD.
 * issuer: the RLUSD issuer address on testnet
 */
export async function setTrustLine(client, wallet, issuer, limit = "1000000") {
  const tx = {
    TransactionType: "TrustSet",
    Account: wallet.address,
    LimitAmount: {
      currency: "RLUSD",
      issuer,
      value: limit,
    },
  };
  const result = await client.submitAndWait(tx, { wallet });
  console.log(`  TrustSet tx: ${result.result.hash}  (${result.result.meta.TransactionResult})`);
  return result;
}
