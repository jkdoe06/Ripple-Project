# XRPL Primary — Stablecoin Escrow Payment App

A real-world MVP built on XRPL primitives, deployed to XRPL Testnet.

## Overview

This app allows users to send RLUSD stablecoin payments with conditional escrow release on the XRP Ledger.

## Features

- Send RLUSD stablecoin payments
- Lock funds into smart escrow
- Automatic escrow release on condition met
- Batch transactions support
- Token tokenization

## Demo Flow

1. User sends RLUSD stablecoin to the app
2. Funds are placed into XRPL escrow
3. Condition is met (time-based or crypto-condition)
4. Escrow automatically releases funds to recipient

## Setup

```bash
npm install
node index.js
```

## Network

Deploys to **XRPL Testnet**: `wss://s.altnet.rippletest.net:51233`

Get testnet XRP: https://faucet.altnet.rippletest.net/accounts
