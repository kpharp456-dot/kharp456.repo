# Personal Banking Dashboard

A personal finance web app that connects to bank accounts via the Plaid API to fetch, categorize, and analyze transactions.

## Features

- **Transaction management** - View, edit, and categorize transactions across all connected accounts
- **Multi-bank support** - Connect and manage multiple bank accounts
- **Categorization rules** - Define rules to automatically categorize transactions by name pattern
- **Analytics** - Spending breakdowns and trends across categories
- **Persistent storage** - Transactions saved locally as JSON; changes backed up automatically before each save

## Tech Stack

- **Backend**: Python + Flask
- **Frontend**: HTML + vanilla JavaScript + Bootstrap
- **Data source**: Plaid API (production)

## Quick Start

### 1. Set up the virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install flask plaid-python
```

### 2. Configure Plaid credentials

Set your `PLAID_CLIENT_ID`, `PLAID_SECRET`, and environment in `banking/persistent_server.py`.

### 3. Start the server

```bash
python banking/persistent_server.py
```

The app runs at `http://localhost:5000`.

## Project Structure

```
banking/
  persistent_server.py       # Flask server and Plaid integration
  transaction_table.html     # Transaction editor UI
  analytics.html             # Spending analytics UI
  categories.html            # Category management UI
  categorization_rules.html  # Categorization rules UI
  transaction_history/
    production/              # Saved transaction JSON files
  lists/
    production/              # Connected banks config
```

## Data Notes

- Amounts follow the convention: **positive = money in, negative = money out**
- Plaid's default sign convention is inverted for depository accounts; the server handles this automatically
