"""
Plaid Client Setup Script
Connects to Plaid API and provides basic banking data access.
"""

import os
import json
from dotenv import load_dotenv
import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode

# Load environment variables
load_dotenv()

class PlaidClient:
    def __init__(self):
        """Initialize Plaid client with environment-specific credentials."""
        self.client_id = os.getenv('PLAID_CLIENT_ID')
        self.env = os.getenv('PLAID_ENV', 'sandbox')
        
        if not self.client_id:
            raise ValueError("PLAID_CLIENT_ID must be set in .env file")
        
        # Get environment-specific secret
        self.secret = self.get_environment_secret()
        
        if not self.secret:
            raise ValueError(f"No secret found for {self.env} environment")
        
        # Configure Plaid host based on environment
        # Plaid only has Sandbox and Production environments
        host = {
            'sandbox': plaid.Environment.Sandbox,
            'production': plaid.Environment.Production
        }.get(self.env, plaid.Environment.Sandbox)
        
        # Create Plaid client
        configuration = plaid.Configuration(
            host=host,
            api_key={
                'clientId': self.client_id,
                'secret': self.secret,
            }
        )
        
        self.api_client = plaid.ApiClient(configuration)
        self.client = plaid_api.PlaidApi(self.api_client)
        
        print(f"✅ Plaid client initialized for {self.env} environment")
    
    def get_environment_secret(self):
        """Get the appropriate secret for the current environment."""
        env_secrets = {
            'sandbox': os.getenv('PLAID_SANDBOX_SECRET'),
            'production': os.getenv('PLAID_PRODUCTION_SECRET')
        }
        
        return env_secrets.get(self.env)
    
    def create_link_token(self, user_id='user_123'):
        """
        Create a link token for Plaid Link frontend integration.
        Returns the link token needed to initialize Plaid Link.
        """
        try:
            request = LinkTokenCreateRequest(
                products=[Products('auth'), Products('transactions')],
                client_name="Personal Banking Dashboard",
                country_codes=[CountryCode('US')],
                language='en',
                user=LinkTokenCreateRequestUser(
                    client_user_id=user_id
                )
            )
            
            response = self.client.link_token_create(request)
            link_token = response['link_token']
            
            print(f"✅ Link token created successfully")
            print(f"🔗 Use this token in Plaid Link frontend: {link_token}")
            
            return link_token
            
        except plaid.ApiException as e:
            print(f"❌ Error creating link token: {e}")
            return None
    
    def exchange_public_token(self, public_token):
        """
        Exchange a public token from Plaid Link for an access token.
        This happens after user successfully connects their bank.
        """
        try:
            request = plaid.model.item_public_token_exchange_request.ItemPublicTokenExchangeRequest(
                public_token=public_token
            )
            
            response = self.client.item_public_token_exchange(request)
            access_token = response['access_token']
            item_id = response['item_id']
            
            print(f"✅ Successfully exchanged public token")
            print(f"🏦 Access token: {access_token}")
            print(f"📋 Item ID: {item_id}")
            
            return access_token, item_id
            
        except plaid.ApiException as e:
            print(f"❌ Error exchanging public token: {e}")
            return None, None
    
    def get_accounts(self, access_token):
        """
        Get account information for a connected bank account.
        """
        try:
            request = plaid.model.accounts_get_request.AccountsGetRequest(
                access_token=access_token
            )
            
            response = self.client.accounts_get(request)
            accounts = response['accounts']
            
            print(f"✅ Retrieved {len(accounts)} accounts")
            
            for account in accounts:
                print(f"\n📊 Account: {account.name}")
                print(f"   Type: {account.type}")
                print(f"   Subtype: {account.subtype}")
                print(f"   Balance: ${account.balances.current:.2f}")
            
            return accounts
            
        except plaid.ApiException as e:
            print(f"❌ Error getting accounts: {e}")
            return None
    
    def get_transactions(self, access_token, start_date, end_date):
        """
        Get transactions for a date range.
        """
        try:
            request = plaid.model.transactions_get_request.TransactionsGetRequest(
                access_token=access_token,
                start_date=start_date,
                end_date=end_date
            )
            
            response = self.client.transactions_get(request)
            transactions = response['transactions']
            
            print(f"✅ Retrieved {len(transactions)} transactions")
            
            for transaction in transactions[:5]:  # Show first 5 transactions
                print(f"\n💳 {transaction.date}: {transaction.name}")
                print(f"   Amount: ${transaction.amount:.2f}")
                print(f"   Category: {transaction.category}")
            
            return transactions
            
        except plaid.ApiException as e:
            print(f"❌ Error getting transactions: {e}")
            return None

def main():
    """Example usage of the Plaid client."""
    print("🚀 Starting Plaid Integration Demo")
    print("=" * 50)
    
    try:
        # Initialize client
        client = PlaidClient()
        
        # Step 1: Create link token (for frontend integration)
        print("\n📝 Step 1: Creating link token...")
        link_token = client.create_link_token()
        
        if link_token:
            print(f"\n⚠️  NEXT STEPS:")
            print(f"1. Use this link token in a web frontend with Plaid Link")
            print(f"2. After user connects bank, you'll get a public_token")
            print(f"3. Exchange public_token for access_token")
            print(f"4. Use access_token to fetch account data")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
