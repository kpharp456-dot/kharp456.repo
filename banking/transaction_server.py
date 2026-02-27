from flask import Flask, request, jsonify, send_from_directory
import plaid_client
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory('.', 'test.html')

@app.route('/transactions')
def transaction_table():
    return send_from_directory('.', 'transaction_table.html')

@app.route('/get-transactions')
def get_transactions():
    try:
        print("Fetching transactions...")
        client = plaid_client.PlaidClient()
        access_token = "access-sandbox-ccee832e-7967-422c-b902-09e9d5387a5d"
        
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        transactions = client.get_transactions(access_token, start_date, end_date)
        
        if transactions:
            transactions_data = []
            for t in transactions:
                transactions_data.append({
                    'date': str(t.date),
                    'name': t.name,
                    'amount': float(t.amount),
                    'category': t.category[0] if t.category else 'Uncategorized'
                })
            
            print(f"Returning {len(transactions_data)} transactions")
            return jsonify({'success': True, 'transactions': transactions_data})
        else:
            return jsonify({'success': False, 'error': 'No transactions found'})
            
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/save-transactions', methods=['POST'])
def save_transactions():
    try:
        data = request.json
        print(f"Saving {len(data.get('transactions', []))} transactions")
        return jsonify({'success': True, 'message': 'Changes saved'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print("🌐 Starting transaction server at http://localhost:5000")
    print("📊 Go to http://localhost:5000/transactions")
    app.run(debug=True, port=5000)
