from web3 import Web3
from eth_account import Account

def check_wallet_connection(wallet_address: str, private_key: str, rpc_url: str):
    try:
        # Connect to blockchain node
        web3 = Web3(Web3.HTTPProvider(rpc_url))

        if not web3.is_connected():
            return False, "Cannot connect to blockchain node"

        # Normalize address
        wallet_address = web3.to_checksum_address(wallet_address)

        # Create account from private key
        account = Account.from_key(private_key)

        # Check address match
        if account.address != wallet_address:
            return False, "Private key does not match wallet address"

        # Optional: check balance
        balance = web3.eth.get_balance(wallet_address)

        return True, f"Connected successfully. Balance: {web3.from_wei(balance, 'ether')} ETH"

    except ValueError:
        return False, "Invalid private key or wallet address"
    except Exception as e:
        return False, str(e)
