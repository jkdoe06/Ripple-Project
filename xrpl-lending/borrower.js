// borrower.js — Borrower role (XLS-66 Lending Protocol)
// Borrower draws a loan from the vault and repays it.

/**
 * Draw a loan from the lending vault (XLS-66 LoanCreate).
 *
 * @param {Client} client
 * @param {Wallet} borrowerWallet
 * @param {string} vaultID
 * @param {object} borrowAmount  — { currency, issuer, value }
 * @param {object} collateral    — XRP drops or IOU to lock as collateral
 */
export async function drawLoan(client, borrowerWallet, vaultID, borrowAmount, collateral) {
  const tx = {
    TransactionType: "LoanCreate",   // XLS-66
    Account: borrowerWallet.address,
    VaultID: vaultID,
    Amount: borrowAmount,
    // Collateral: collateral,       // Uncomment when XLS-66 finalises field names
  };

  console.log(`  Borrower (${borrowerWallet.address}) drawing ${borrowAmount.value} ${borrowAmount.currency}...`);
  const result = await client.submitAndWait(tx, { wallet: borrowerWallet });
  console.log(`  LoanCreate tx: ${result.result.hash}  (${result.result.meta.TransactionResult})`);

  const loanID = result.result.meta?.CreatedNode?.NewFields?.LoanID
    ?? `${borrowerWallet.address}:${result.result.tx_json.Sequence}`;
  return { result, loanID };
}

/**
 * Repay a loan (XLS-66 LoanRepay).
 * Borrower returns principal + accrued interest.
 *
 * @param {Client} client
 * @param {Wallet} borrowerWallet
 * @param {string} loanID
 * @param {object} repayAmount  — { currency, issuer, value }
 */
export async function repayLoan(client, borrowerWallet, loanID, repayAmount) {
  const tx = {
    TransactionType: "LoanRepay",    // XLS-66
    Account: borrowerWallet.address,
    LoanID: loanID,
    Amount: repayAmount,
  };

  console.log(`  Borrower repaying loan ${loanID}: ${repayAmount.value} ${repayAmount.currency}`);
  const result = await client.submitAndWait(tx, { wallet: borrowerWallet });
  console.log(`  LoanRepay tx: ${result.result.hash}  (${result.result.meta.TransactionResult})`);
  return result;
}
