from flask import Flask, request, jsonify, send_from_directory
import plaid_client
from environment_switcher import env_switcher
from datetime import datetime, timedelta
import json
import os
import shutil

app = Flask(__name__)

def get_paths():
    """Get environment-specific file paths"""
    return env_switcher.get_data_paths()

def get_transactions_file():
    return get_paths()['transactions_file']

def get_banks_file():
    return get_paths()['banks_file']

def get_rules_file():
    return get_paths()['rules_file']

def get_categories_file():
    return get_paths()['categories_file']

def get_transactions_dir():
    return get_paths()['transactions_dir']

def save_transactions_to_file(transactions):
    """Save transactions to a JSON file"""
    try:
        transactions_file = get_transactions_file()
        with open(transactions_file, 'w') as f:
            json.dump(transactions, f, indent=2)
        print(f"✅ Saved {len(transactions)} transactions to {transactions_file}")
        return True
    except Exception as e:
        print(f"❌ Error saving transactions: {e}")
        return False

def load_transactions_from_file():
    """Load transactions from a JSON file"""
    try:
        transactions_file = get_transactions_file()
        if os.path.exists(transactions_file):
            with open(transactions_file, 'r') as f:
                content = f.read().strip()
                if content:
                    transactions = json.loads(content)
                    print(f"✅ Loaded {len(transactions)} transactions from {transactions_file}")
                    return transactions
                else:
                    print("⚠️  Transaction file is empty")
                    return None
        else:
            print("📝 No saved transactions file found, fetching from Plaid")
            return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error in transactions file: {e}")
        return None
    except Exception as e:
        print(f"❌ Error loading transactions: {e}")
        return None

def backup_transactions(transactions):
    """Create a backup of transactions"""
    transactions_dir = get_transactions_dir()
    backup_file = os.path.join(transactions_dir, f'transactions_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
    try:
        with open(backup_file, 'w') as f:
            json.dump(transactions, f, indent=2)
        print(f"🔄 Created backup: {backup_file}")
        return backup_file
    except Exception as e:
        print(f"❌ Error creating backup: {e}")
        return None

def load_connected_banks():
    """Load all connected bank information"""
    try:
        banks_file = get_banks_file()
        if os.path.exists(banks_file):
            with open(banks_file, 'r') as f:
                content = f.read().strip()
                if not content:
                    return {}
                return json.loads(content)
        return {}
    except json.JSONDecodeError as e:
        banks_file = get_banks_file()
        print(f"❌ JSON decode error in {banks_file}: {e}")
        if os.path.exists(banks_file):
            backup_file = f"{banks_file}.corrupted_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.rename(banks_file, backup_file)
            print(f"🔄 Corrupted file backed up to: {backup_file}")
        return {}
    except Exception as e:
        print(f"❌ Error loading banks: {e}")
        return {}

def get_last_transaction_date():
    """Get the date of the most recent transaction in the saved file"""
    try:
        transactions_file = get_transactions_file()
        if os.path.exists(transactions_file):
            with open(transactions_file, 'r') as f:
                transactions = json.load(f)
                if transactions:
                    latest_date = None
                    for transaction in transactions:
                        transaction_date = datetime.strptime(transaction['date'], '%Y-%m-%d').date()
                        if latest_date is None or transaction_date > latest_date:
                            latest_date = transaction_date
                    return latest_date
        return None
    except Exception as e:
        print(f"❌ Error getting last transaction date: {e}")
        return None

def fetch_all_transactions():
    """Fetch transactions from ALL connected banks and save to file"""
    try:
        print("🔄 Auto-fetching transactions from all connected banks...")
        
        banks = load_connected_banks()
        all_transactions = {}  # Use dict with transaction_id as key for deduplication
        
        if not banks:
            print("⚠️  No banks connected. Skipping auto-fetch.")
            return False
        
        end_date = datetime.now().date()
        
        # Determine start date based on existing data
        last_date = get_last_transaction_date()
        if last_date:
            # Start from 5 days before last transaction to catch any missed ones
            start_date = last_date - timedelta(days=180)
            print(f"📅 Incremental fetch: {start_date} to {end_date} (since last transaction)")
        else:
            # First run - get last 90 days
            start_date = end_date - timedelta(days=90)
            print(f"📅 Initial fetch: {start_date} to {end_date} (last 90 days)")
        
        for bank_id, bank_info in banks.items():
            try:
                print(f"📥 Fetching from {bank_info['institution_name']}...")
                client = plaid_client.PlaidClient()
                transactions = client.get_transactions(bank_info['access_token'], start_date, end_date)
                
                if transactions:
                    new_count = 0
                    for t in transactions:
                        # Use transaction_id as unique key for deduplication
                        transaction_key = t.transaction_id if hasattr(t, 'transaction_id') else f"{bank_id}_{t.date}_{t.name}_{t.amount}"
                        
                        all_transactions[transaction_key] = {
                            'transaction_id': transaction_key,
                            'date': str(t.date),
                            'name': t.name,
                            'amount': float(t.amount),
                            'category': t.category[0] if t.category else 'Uncategorized',
                            'bank_id': bank_id,
                            'bank_name': bank_info['institution_name']
                        }
                        new_count += 1
                    print(f"✅ Got {new_count} transactions from {bank_info['institution_name']}")
                else:
                    print(f"⚠️  No transactions from {bank_info['institution_name']}")
                        
            except Exception as e:
                print(f"❌ Error fetching from {bank_info['institution_name']}: {e}")
        
        if all_transactions:
            # Load existing transactions and merge with new ones
            existing_transactions = []
            transactions_file = get_transactions_file()
            if os.path.exists(transactions_file):
                try:
                    with open(transactions_file, 'r') as f:
                        existing_transactions = json.load(f)
                except:
                    existing_transactions = []
            
            # Merge existing with new, using transaction_id for deduplication
            merged_transactions = {}
            
            # Add existing transactions first
            for transaction in existing_transactions:
                if 'transaction_id' in transaction:
                    merged_transactions[transaction['transaction_id']] = transaction
            
            # Add new transactions (will overwrite duplicates with same ID)
            for transaction_id, transaction in all_transactions.items():
                merged_transactions[transaction_id] = transaction
            
            # Convert to list and sort by date (newest first)
            final_transactions = list(merged_transactions.values())
            final_transactions.sort(key=lambda x: x['date'], reverse=True)
            
            # Apply categorization rules to new transactions
            final_transactions = apply_categorization_rules(final_transactions)
            
            # Save to file
            save_transactions_to_file(final_transactions)
            
            new_transaction_count = len(all_transactions)
            total_transaction_count = len(final_transactions)
            print(f"🎉 Added {new_transaction_count} new transactions. Total: {total_transaction_count} from {len(banks)} banks")
            return True
        else:
            print("⚠️  No new transactions found from any bank")
            return False
            
    except Exception as e:
        print(f"❌ Error in auto-fetch: {e}")
        return False

def save_connected_banks(banks):
    """Save all connected bank information"""
    try:
        banks_file = get_banks_file()
        with open(banks_file, 'w') as f:
            json.dump(banks, f, indent=2)
        print(f"✅ Saved {len(banks)} connected banks")
        return True
    except Exception as e:
        print(f"❌ Error saving banks: {e}")
        return False

def load_categories():
    """Load categories from JSON file"""
    try:
        categories_file = get_categories_file()
        if os.path.exists(categories_file):
            with open(categories_file, 'r') as f:
                content = f.read().strip()
                if not content:
                    return {"categories": ["Uncategorized"]}
                return json.loads(content)
        else:
            # Create default categories file if it doesn't exist
            default_categories = {
                "categories": [
                    "Food & Dining",
                    "Transportation", 
                    "Shopping",
                    "Entertainment",
                    "Bills & Utilities",
                    "Healthcare",
                    "Travel",
                    "Education",
                    "Personal Care",
                    "Groceries",
                    "Income",
                    "Transfer",
                    "Uncategorized"
                ]
            }
            save_categories(default_categories)
            return default_categories
    except Exception as e:
        print(f"❌ Error loading categories: {e}")
        return {"categories": ["Uncategorized"]}

def save_categories(categories):
    """Save categories to JSON file"""
    try:
        categories_file = get_categories_file()
        with open(categories_file, 'w') as f:
            json.dump(categories, f, indent=2)
        print(f"✅ Saved {len(categories.get('categories', []))} categories")
        return True
    except Exception as e:
        print(f"❌ Error saving categories: {e}")
        return False

def load_categorization_rules():
    """Load categorization rules from JSON file"""
    try:
        rules_file = get_rules_file()
        if os.path.exists(rules_file):
            with open(rules_file, 'r') as f:
                content = f.read().strip()
                if not content:
                    return {"rules": []}
                return json.loads(content)
        else:
            # Create default rules file if it doesn't exist
            default_rules = {
                "rules": [
                    {
                        "id": "uber_rule",
                        "name": "Uber Rides",
                        "description": "Categorize all Uber transactions as Transportation",
                        "conditions": {
                            "name_contains": ["uber", "lyft"],
                            "category": null
                        },
                        "actions": {
                            "set_category": "Transportation"
                        },
                        "enabled": true
                    },
                    {
                        "id": "mcdonalds_rule",
                        "name": "Fast Food",
                        "description": "Categorize fast food restaurants",
                        "conditions": {
                            "name_contains": ["mcdonald", "burger king", "wendy", "taco bell", "kfc"],
                            "category": null
                        },
                        "actions": {
                            "set_category": "Food & Dining"
                        },
                        "enabled": true
                    },
                    {
                        "id": "income_rule",
                        "name": "Income Detection",
                        "description": "Categorize negative amounts as Income",
                        "conditions": {
                            "amount_less_than": 0,
                            "category": null
                        },
                        "actions": {
                            "set_category": "Income"
                        },
                        "enabled": true
                    }
                ]
            }
            save_categorization_rules(default_rules)
            return default_rules
    except Exception as e:
        print(f"❌ Error loading categorization rules: {e}")
        return {"rules": []}

def save_categorization_rules(rules):
    """Save categorization rules to JSON file"""
    try:
        rules_file = get_rules_file()
        with open(rules_file, 'w') as f:
            json.dump(rules, f, indent=2)
        print(f"✅ Saved {len(rules.get('rules', []))} categorization rules")
        return True
    except Exception as e:
        print(f"❌ Error saving categorization rules: {e}")
        return False

def apply_categorization_rules(transactions):
    """Apply categorization rules to transactions"""
    try:
        rules_data = load_categorization_rules()
        rules = rules_data.get('rules', [])
        
        if not rules:
            return transactions
        
        categorized_count = 0
        
        for transaction in transactions:
            # Skip if already categorized (not Uncategorized)
            if transaction.get('category') and transaction['category'] != 'Uncategorized':
                continue
                
            for rule in rules:
                if not rule.get('enabled', True):
                    continue
                
                # Check if transaction matches rule conditions
                if matches_rule_conditions(transaction, rule.get('conditions', {})):
                    # Apply rule actions
                    actions = rule.get('actions', {})
                    if 'set_category' in actions:
                        transaction['category'] = actions['set_category']
                        categorized_count += 1
                        print(f"🏷️  Applied rule '{rule['name']}' to: {transaction['name']}")
                    break  # Stop after first matching rule
        
        if categorized_count > 0:
            print(f"🎉 Auto-categorized {categorized_count} transactions using rules")
        
        return transactions
        
    except Exception as e:
        print(f"❌ Error applying categorization rules: {e}")
        return transactions

def matches_rule_conditions(transaction, conditions):
    """Check if a transaction matches rule conditions"""
    if not conditions:
        return True
    
    # Check name_contains condition
    if 'name_contains' in conditions:
        name_lower = transaction.get('name', '').lower()
        name_patterns = conditions['name_contains']
        if not any(pattern.lower() in name_lower for pattern in name_patterns):
            return False
    
    # Check amount_greater_than condition
    if 'amount_greater_than' in conditions:
        if transaction.get('amount', 0) <= conditions['amount_greater_than']:
            return False
    
    # Check amount_less_than condition
    if 'amount_less_than' in conditions:
        if transaction.get('amount', 0) >= conditions['amount_less_than']:
            return False
    
    # Check category condition (null means uncategorized)
    if 'category' in conditions:
        if conditions['category'] is None:
            if transaction.get('category') and transaction['category'] != 'Uncategorized':
                return False
        elif transaction.get('category') != conditions['category']:
            return False
    
    # Check bank_name condition
    if 'bank_name' in conditions:
        if conditions['bank_name'] not in transaction.get('bank_name', ''):
            return False
    
    return True

@app.route('/')
def index():
    return send_from_directory('.', 'home_page.html')

@app.route('/analytics')
def analytics_page():
    """Return analytics dashboard page"""
    return send_from_directory('.', 'analytics.html')

@app.route('/environment')
def environment_page():
    """Return environment settings page"""
    return send_from_directory('.', 'environment.html')

@app.route('/banking')
def transaction_table():
    return send_from_directory('.', 'transaction_table.html')

@app.route('/connect')
def connect_bank():
    return send_from_directory('.', 'web_interface.html')

@app.route('/transactions')  # Keep for backward compatibility
def transaction_table_old():
    return send_from_directory('.', 'transaction_table.html')

@app.route('/get-transactions')
def get_transactions():
    """Get transactions from ALL connected banks"""
    try:
        print("Fetching transactions from all banks...")
        
        # First try to load from file
        saved_transactions = load_transactions_from_file()
        
        if saved_transactions:
            return jsonify({'success': True, 'transactions': saved_transactions})
        
        # If no saved file, fetch from all connected banks (initial fetch)
        banks = load_connected_banks()
        all_transactions = {}  # Use dict for deduplication
        
        if not banks:
            return jsonify({'success': False, 'error': 'No banks connected. Please connect a bank first.'})
        
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=90)  # Initial fetch: last 90 days
        print(f"📅 Initial fetch: {start_date} to {end_date} (last 90 days)")
        
        for bank_id, bank_info in banks.items():
            try:
                print(f"Fetching from {bank_info['institution_name']}...")
                client = plaid_client.PlaidClient()
                transactions = client.get_transactions(bank_info['access_token'], start_date, end_date)
                
                if transactions:
                    for t in transactions:
                        # Use transaction_id as unique key for deduplication
                        transaction_key = t.transaction_id if hasattr(t, 'transaction_id') else f"{bank_id}_{t.date}_{t.name}_{t.amount}"
                        
                        all_transactions[transaction_key] = {
                            'transaction_id': transaction_key,
                            'date': str(t.date),
                            'name': t.name,
                            'amount': float(t.amount),
                            'category': t.category[0] if t.category else 'Uncategorized',
                            'bank_id': bank_id,
                            'bank_name': bank_info['institution_name']
                        }
                        
            except Exception as e:
                print(f"Error fetching from {bank_info['institution_name']}: {e}")
        
        if all_transactions:
            # Convert dict to list and sort by date (newest first)
            transactions_list = list(all_transactions.values())
            transactions_list.sort(key=lambda x: x['date'], reverse=True)
            
            # Apply categorization rules
            transactions_list = apply_categorization_rules(transactions_list)
            
            # Save to file for next time
            save_transactions_to_file(transactions_list)
            
            print(f"Returning {len(transactions_list)} unique transactions from {len(banks)} banks")
            return jsonify({'success': True, 'transactions': transactions_list})
        else:
            return jsonify({'success': False, 'error': 'No transactions found'})
            
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/save-transactions', methods=['POST'])
def save_transactions():
    try:
        data = request.json
        edited_transactions = data.get('transactions', [])
        
        # Create backup before saving
        backup_file = backup_transactions(edited_transactions)
        
        # Save to file
        if save_transactions_to_file(edited_transactions):
            message = f'✅ Saved {len(edited_transactions)} transactions'
            if backup_file:
                message += f' (backup: {backup_file})'
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'error': 'Failed to save transactions'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/exchange-token', methods=['POST'])
def exchange_token():
    """Exchange public token for access token and add new bank"""
    try:
        data = request.json
        public_token = data.get('public_token')
        bank_name = data.get('bank_name', 'Unknown Bank')
        
        if not public_token:
            return jsonify({'success': False, 'error': 'No public token provided'})
        
        # Initialize Plaid client
        client = plaid_client.PlaidClient()
        
        # Exchange public token for access token
        access_token, item_id = client.exchange_public_token(public_token)
        
        if access_token and item_id:
            # Get account information
            accounts = client.get_accounts(access_token)
            
            # Load existing banks
            banks = load_connected_banks()
            
            # Generate unique bank ID
            bank_id = f"bank_{len(banks) + 1}"
            while bank_id in banks:
                bank_id = f"bank_{len(banks) + 2}"
            
            # Add new bank
            banks[bank_id] = {
                "item_id": item_id,
                "access_token": access_token,
                "institution_name": bank_name,
                "accounts": [{"name": acc.name, "type": str(acc.type), "subtype": str(acc.subtype)} for acc in accounts],
                "date_connected": datetime.now().isoformat()
            }
            
            # Save updated banks list
            save_connected_banks(banks)
            
            return jsonify({
                'success': True,
                'bank_id': bank_id,
                'access_token': access_token,
                'item_id': item_id,
                'accounts': [{'name': acc.name, 'type': acc.type} for acc in accounts] if accounts else [],
                'all_banks': banks
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to exchange token'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/refresh-transactions')
def refresh_transactions():
    """Manually refresh transactions from all banks"""
    try:
        success = fetch_all_transactions()
        if success:
            return jsonify({'success': True, 'message': 'Transactions refreshed successfully'})
        else:
            return jsonify({'success': False, 'error': 'Failed to refresh transactions'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/load-fresh')
def load_fresh():
    """Force reload from Plaid instead of saved file"""
    try:
        # Remove saved file to force fresh load
        transactions_file = get_transactions_file()
        if os.path.exists(transactions_file):
            os.remove(transactions_file)
            print("🗑️ Removed saved transactions file")
        
        return jsonify({'success': True, 'message': 'Fresh load enabled'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/download/<filename>')
def download_file(filename):
    """Download a transaction history file"""
    try:
        transactions_dir = get_transactions_dir()
        filepath = os.path.join(transactions_dir, filename)
        if os.path.exists(filepath) and filename.endswith('.json'):
            return send_from_directory(transactions_dir, filename, as_attachment=True)
        else:
            return jsonify({'success': False, 'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/connected-banks')
def list_connected_banks():
    """List all connected banks - returns HTML page"""
    return send_from_directory('.', 'connected_banks.html')

@app.route('/api/connected-banks')
def api_connected_banks():
    """API endpoint to get connected banks data"""
    banks = load_connected_banks()
    return jsonify({'success': True, 'banks': banks})

@app.route('/remove-bank/<bank_id>', methods=['DELETE'])
def remove_bank(bank_id):
    """Remove a bank connection"""
    try:
        banks = load_connected_banks()
        
        if bank_id in banks:
            bank_name = banks[bank_id]['institution_name']
            del banks[bank_id]
            save_connected_banks(banks)
            
            # Clear transactions file to force refresh
            transactions_file = get_transactions_file()
            if os.path.exists(transactions_file):
                os.remove(transactions_file)
            
            return jsonify({'success': True, 'message': f'Removed {bank_name}'})
        else:
            return jsonify({'success': False, 'error': 'Bank not found'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/categorization-rules')
def categorization_rules_page():
    """Return categorization rules management page"""
    return send_from_directory('.', 'categorization_rules.html')

@app.route('/api/categorization-rules')
def api_categorization_rules():
    """Get all categorization rules"""
    rules = load_categorization_rules()
    return jsonify({'success': True, 'rules': rules.get('rules', [])})

@app.route('/api/categorization-rules', methods=['POST'])
def api_save_categorization_rules():
    """Save categorization rules"""
    try:
        data = request.json
        rules = data.get('rules', [])
        
        rules_data = {"rules": rules}
        if save_categorization_rules(rules_data):
            return jsonify({'success': True, 'message': f'Saved {len(rules)} rules'})
        else:
            return jsonify({'success': False, 'error': 'Failed to save rules'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/apply-categorization-rules', methods=['POST'])
def api_apply_categorization_rules():
    """Apply categorization rules to existing transactions"""
    try:
        # Load existing transactions
        transactions = load_transactions_from_file()
        if not transactions:
            return jsonify({'success': False, 'error': 'No transactions found'})
        
        # Apply rules
        categorized_transactions = apply_categorization_rules(transactions)
        
        # Save updated transactions
        if save_transactions_to_file(categorized_transactions):
            return jsonify({'success': True, 'message': 'Rules applied to all transactions'})
        else:
            return jsonify({'success': False, 'error': 'Failed to save transactions'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/categories')
def categories_page():
    """Return categories management page"""
    return send_from_directory('.', 'categories.html')

@app.route('/api/categories')
def api_categories():
    """Get all categories"""
    categories = load_categories()
    return jsonify({'success': True, 'categories': categories.get('categories', [])})

@app.route('/api/categories', methods=['POST'])
def api_save_categories():
    """Save categories"""
    try:
        data = request.json
        categories = data.get('categories', [])
        
        categories_data = {"categories": categories}
        if save_categories(categories_data):
            return jsonify({'success': True, 'message': f'Saved {len(categories)} categories'})
        else:
            return jsonify({'success': False, 'error': 'Failed to save categories'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/environment')
def api_get_environment():
    """Get current Plaid environment info"""
    try:
        env_info = env_switcher.get_environment_info()
        return jsonify({'success': True, 'environment': env_info})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/environment', methods=['POST'])
def api_switch_environment():
    """Switch Plaid environment"""
    try:
        data = request.json
        new_env = data.get('environment')
        
        if not new_env:
            return jsonify({'success': False, 'error': 'Environment is required'})
        
        result = env_switcher.switch_environment(new_env)
        return jsonify({'success': True, 'message': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/plaid/create_link_token', methods=['POST'])
def create_link_token():
    """Create a fresh Plaid link token"""
    try:
        client = plaid_client.PlaidClient()
        link_token = client.create_link_token()
        return jsonify({'success': True, 'link_token': link_token})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    current_env = env_switcher.get_environment_info()
    env_name = current_env['name']
    env_color = '🟢' if current_env['current'] == 'sandbox' else ''
    
    print("🌐 Starting MULTI-BANK transaction server at http://localhost:5000")
    print("🏦 Go to http://localhost:5000/banking for transaction editor")
    print("🔗 Go to http://localhost:5000/connect to add banks")
    print("📊 Go to http://localhost:5000/connected-banks to view all banks")
    print("🔧 Go to http://localhost:5000/environment to switch sandbox/real data")
    print("📈 Go to http://localhost:5000/analytics for charts and insights")
    print("🔄 Go to http://localhost:5000/refresh-transactions to manually refresh")
    print(" Changes are now saved to transactions.json")
    print("🔄 Go to http://localhost:5000/load-fresh to reload from all banks")
    
    paths = get_paths()
    print(f"📁 Data stored in environment-specific folders:")
    print(f"   Transactions: {paths['transactions_dir']}")
    print(f"   Lists: {paths['lists_dir']}")
    print("🏛️  Multiple bank support ENABLED")
    print(f"{env_color} Plaid Environment: {env_name} ({current_env['description']})")
    print("💰 COST-SAVING MODE: Manual refresh only (no auto API calls)")
    
    # Check if we have saved transactions
    transactions_file = get_transactions_file()
    if os.path.exists(transactions_file):
        try:
            with open(transactions_file, 'r') as f:
                content = f.read().strip()
                if content:
                    saved_count = len(json.loads(content))
                    print(f"\n📊 Loaded {saved_count} cached transactions from file")
                    print("💡 Use '💰 Fetch from Banks (API)' button to fetch latest data")
                else:
                    print(f"\n⚠️  Transaction file is empty")
                    print("💡 Connect banks and use '💰 Fetch from Banks (API)' to get started")
        except json.JSONDecodeError:
            print(f"\n⚠️  Transaction file has invalid JSON")
            print("💡 Connect banks and use '💰 Fetch from Banks (API)' to get started")
    else:
        print("\n⚠️  No cached transactions found")
        print("💡 Connect banks and use '💰 Fetch from Banks (API)' to get started")
    
    print("\n" + "="*50)
    print("✅ Server ready! Access your banking dashboard.")
    print("="*50 + "\n")
    
    app.run(debug=True, port=5000)
