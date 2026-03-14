// escrow.js — EscrowCreate and EscrowFinish logic

/**
 * Create a time-based XRP escrow.
 * Funds are locked until `releaseAfterSeconds` seconds from now.
 *
 * @param {Client} client
 * @param {Wallet} senderWallet
 * @param {string} destination
 * @param {string} amountDrops   - amount in XRP drops (1 XRP = 1,000,000 drops)
 * @param {number} releaseAfterSeconds
 */
export async function createEscrow(client, senderWallet, destination, amountDrops, releaseAfterSeconds) {
  // XRPL time epoch starts 2000-01-01. Convert from Unix epoch.
  const XRPL_EPOCH_OFFSET = 946684800;
  const finishAfter = Math.floor(Date.now() / 1000) - XRPL_EPOCH_OFFSET + releaseAfterSeconds;

  const tx = {
    TransactionType: "EscrowCreate",
    Account: senderWallet.address,
    Destination: destination,
    Amount: amountDrops,
    FinishAfter: finishAfter,
  };

  console.log(`  Creating escrow: ${amountDrops} drops → ${destination} (releases in ${releaseAfterSeconds}s)`);
  const result = await client.submitAndWait(tx, { wallet: senderWallet });
  console.log(`  EscrowCreate tx: ${result.result.hash}  (${result.result.meta.TransactionResult})`);

  // Extract the escrow sequence number from the metadata
  const escrowSequence = result.result.tx_json.Sequence;
  return { result, escrowSequence };
}

/**
 * Finish (release) an existing escrow once the FinishAfter time has passed.
 *
 * @param {Client} client
 * @param {Wallet} finisherWallet  - any account can finish a time-based escrow
 * @param {string} owner           - original EscrowCreate account
 * @param {number} offerSequence   - sequence of the EscrowCreate transaction
 */
export async function finishEscrow(client, finisherWallet, owner, offerSequence) {
  const tx = {
    TransactionType: "EscrowFinish",
    Account: finisherWallet.address,
    Owner: owner,
    OfferSequence: offerSequence,
  };

  console.log(`  Finishing escrow (seq ${offerSequence}) owned by ${owner}`);
  const result = await client.submitAndWait(tx, { wallet: finisherWallet });
  console.log(`  EscrowFinish tx: ${result.result.hash}  (${result.result.meta.TransactionResult})`);
  return result;
}

/**
 * Cancel an expired escrow (only after CancelAfter, if set).
 */
export async function cancelEscrow(client, senderWallet, owner, offerSequence) {
  const tx = {
    TransactionType: "EscrowCancel",
    Account: senderWallet.address,
    Owner: owner,
    OfferSequence: offerSequence,
  };

  console.log(`  Cancelling escrow (seq ${offerSequence})`);
  const result = await client.submitAndWait(tx, { wallet: senderWallet });
  console.log(`  EscrowCancel tx: ${result.result.hash}  (${result.result.meta.TransactionResult})`);
  return result;
}
