"""
Design for Multi-Bank Support
This shows how to enhance the system for multiple bank connections
"""

# 1. NEW DATA STRUCTURE - Store multiple banks
BANKS_FILE = 'transaction_history/connected_banks.json'

def load_connected_banks():
    """Load all connected bank information"""
    try:
        if os.path.exists(BANKS_FILE):
            with open(BANKS_FILE, 'r') as f:
                return json.load(f)
        return {}
    except:
        return {}

def save_connected_banks(banks):
    """Save all connected bank information"""
    with open(BANKS_FILE, 'w') as f:
        json.dump(banks, f, indent=2)

# 2. NEW BANK DATA STRUCTURE
banks_data = {
    "bank_1": {
        "item_id": "1Xl6zNezxQtlXWz9gPZAcZaxqjGGVpu5p8Axj",
        "access_token": "access-sandbox-ccee832e-7967-422c-b902-09e9d5387a5d",
        "institution_name": "Plaid Bank",
        "accounts": [
            {"name": "Plaid Checking", "type": "depository", "subtype": "checking"},
            {"name": "Plaid Saving", "type": "depository", "subtype": "savings"}
        ],
        "date_connected": "2026-01-30T15:26:00Z"
    },
    "bank_2": {
        "item_id": "another-item-id-here",
        "access_token": "access-sandbox-another-token",
        "institution_name": "Another Bank",
        "accounts": [
            {"name": "Another Checking", "type": "depository", "subtype": "checking"}
        ],
        "date_connected": "2026-01-30T16:00:00Z"
    }
}

# 3. NEW API ENDPOINTS
@app.route('/add-bank', methods=['POST'])
def add_bank():
    """Add a new bank connection"""
    data = request.json
    public_token = data.get('public_token')
    bank_name = data.get('bank_name', 'Unknown Bank')
    
    # Exchange public token for access token
    client = plaid_client.PlaidClient()
    access_token, item_id = client.exchange_public_token(public_token)
    
    # Get account info
    accounts = client.get_accounts(access_token)
    
    # Load existing banks
    banks = load_connected_banks()
    
    # Add new bank
    bank_id = f"bank_{len(banks) + 1}"
    banks[bank_id] = {
        "item_id": item_id,
        "access_token": access_token,
        "institution_name": bank_name,
        "accounts": [{"name": acc.name, "type": acc.type, "subtype": acc.subtype} for acc in accounts],
        "date_connected": datetime.now().isoformat()
    }
    
    # Save updated banks list
    save_connected_banks(banks)
    
    return jsonify({'success': True, 'bank_id': bank_id, 'banks': banks})

@app.route('/get-all-transactions')
def get_all_transactions():
    """Get transactions from ALL connected banks"""
    all_transactions = []
    banks = load_connected_banks()
    
    for bank_id, bank_info in banks.items():
        try:
            client = plaid_client.PlaidClient()
            transactions = client.get_transactions(
                bank_info['access_token'], 
                start_date, 
                end_date
            )
            
            # Add bank info to each transaction
            for t in transactions:
                all_transactions.append({
                    'date': str(t.date),
                    'name': t.name,
                    'amount': float(t.amount),
                    'category': t.category[0] if t.category else 'Uncategorized',
                    'bank_id': bank_id,
                    'bank_name': bank_info['institution_name']
                })
                
        except Exception as e:
            print(f"Error fetching from {bank_info['institution_name']}: {e}")
    
    # Sort by date
    all_transactions.sort(key=lambda x: x['date'], reverse=True)
    
    return jsonify({'success': True, 'transactions': all_transactions})

@app.route('/connected-banks')
def list_connected_banks():
    """List all connected banks"""
    banks = load_connected_banks()
    return jsonify({'success': True, 'banks': banks})

@app.route('/remove-bank/<bank_id>', methods=['DELETE'])
def remove_bank(bank_id):
    """Remove a bank connection"""
    banks = load_connected_banks()
    
    if bank_id in banks:
        del banks[bank_id]
        save_connected_banks(banks)
        return jsonify({'success': True, 'message': f'Removed {bank_id}'})
    else:
        return jsonify({'success': False, 'error': 'Bank not found'})

# 4. FRONTEND CHANGES NEEDED
"""
- Add "Connect Another Bank" button
- Show bank names in transaction list
- Filter transactions by bank
- Manage connected banks (add/remove)
- Show account balances by bank
"""

print("This design shows how to add multi-bank support!")
print("Key changes:")
print("1. Store multiple access tokens in connected_banks.json")
print("2. New API endpoints for bank management")
print("3. Aggregate transactions from all banks")
print("4. Frontend updates to show bank information")
