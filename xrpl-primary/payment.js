// payment.js — RLUSD stablecoin payment logic

/**
 * Send RLUSD from one account to another.
 * @param {Client} client
 * @param {Wallet} senderWallet
 * @param {string} destination  - recipient address
 * @param {string} issuer       - RLUSD issuer address
 * @param {string} amount       - amount of RLUSD to send
 */
export async function sendRLUSD(client, senderWallet, destination, issuer, amount) {
  const tx = {
    TransactionType: "Payment",
    Account: senderWallet.address,
    Destination: destination,
    Amount: {
      currency: "RLUSD",
      issuer,
      value: amount,
    },
  };

  console.log(`  Sending ${amount} RLUSD → ${destination}`);
  const result = await client.submitAndWait(tx, { wallet: senderWallet });
  console.log(`  Payment tx: ${result.result.hash}  (${result.result.meta.TransactionResult})`);
  return result;
}
