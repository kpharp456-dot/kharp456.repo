"""
Environment Switcher for Plaid API
Easy switching between Sandbox (free) and Development (real data) modes
"""

import os
import json
from dotenv import load_dotenv, set_key

class EnvironmentSwitcher:
    def __init__(self):
        """Initialize the environment switcher"""
        load_dotenv()
        self.env_file = '.env'
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        
    def get_current_environment(self):
        """Get the current Plaid environment"""
        return os.getenv('PLAID_ENV', 'sandbox')
    
    def get_data_paths(self):
        """Get environment-specific data paths"""
        env = self.get_current_environment()
        
        transactions_dir = os.path.join(self.base_dir, 'transaction_history', env)
        lists_dir = os.path.join(self.base_dir, 'lists', env)
        
        os.makedirs(transactions_dir, exist_ok=True)
        os.makedirs(lists_dir, exist_ok=True)
        
        return {
            'transactions_dir': transactions_dir,
            'lists_dir': lists_dir,
            'transactions_file': os.path.join(transactions_dir, 'transactions.json'),
            'banks_file': os.path.join(lists_dir, 'connected_banks.json'),
            'rules_file': os.path.join(lists_dir, 'categorization_rules.json'),
            'categories_file': os.path.join(lists_dir, 'categories.json'),
            'environment': env
        }
    
    def switch_environment(self, new_env):
        """Switch to a different Plaid environment"""
        if new_env not in ['sandbox', 'production']:
            raise ValueError("Environment must be 'sandbox' or 'production'")
        
        # Check if credentials exist for the new environment
        env_secret_key = f'PLAID_{new_env.upper()}_SECRET'
        current_secret = os.getenv(env_secret_key)
        
        if not current_secret or current_secret == f'your_{new_env}_secret_here':
            raise ValueError(f"No valid credentials found for {new_env} environment. Please set {env_secret_key} in .env file")
        
        # Update the .env file
        set_key(self.env_file, 'PLAID_ENV', new_env)
        
        # Reload environment variables
        load_dotenv(override=True)
        
        return f"Switched to {new_env} environment"
    
    def get_environment_info(self):
        """Get information about current environment"""
        current_env = self.get_current_environment()
        
        info = {
            'sandbox': {
                'name': 'Sandbox',
                'description': 'Free testing environment with fake data',
                'cost': 'Free',
                'data': 'Test transactions and accounts',
                'color': '#28a745'
            },
            'production': {
                'name': 'Production',
                'description': 'Live environment for real bank data',
                'cost': 'Pay-per-use',
                'data': 'Your actual bank transactions',
                'color': '#dc3545'
            }
        }
        
        current_info = info.get(current_env, info['sandbox'])
        current_info['current'] = current_env
        
        return current_info

# Global instance
env_switcher = EnvironmentSwitcher()
