from web3 import Web3
import json
import time

# CONNECTION

url = 'https://ethereum-sepolia-rpc.publicnode.com'
w3 = Web3(Web3.HTTPProvider(url))

print("Connected:", w3.is_connected())

mywallet = "YOUR_WALLET"
myprivkey = "YOUR_KEY"

balance = w3.eth.get_balance(mywallet)
print("Balance:", w3.from_wei(balance, "ether"), "ETH")

contract_address = "YOUR_CONTRACT"

abi = [
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_secretNumber",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "_maxAttempts",
				"type": "uint256"
			}
		],
		"stateMutability": "payable",
		"type": "constructor"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": False,
				"internalType": "address",
				"name": "winner",
				"type": "address"
			},
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "amountWon",
				"type": "uint256"
			}
		],
		"name": "GameEnded",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": False,
				"internalType": "string",
				"name": "result",
				"type": "string"
			}
		],
		"name": "GuessResult",
		"type": "event"
	},
	{
		"inputs": [],
		"name": "attempts",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "betAmount",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "gameOver",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_number",
				"type": "uint256"
			}
		],
		"name": "guess",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "joinGame",
		"outputs": [],
		"stateMutability": "payable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "maxAttempts",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "playerA",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "playerB",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]

contract = w3.eth.contract(address=contract_address, abi=abi)

# JOIN GAME

bet = contract.functions.betAmount().call()
print("Bet required:", w3.from_wei(bet, "ether"), "ETH")

nonce = w3.eth.get_transaction_count(mywallet)

tx = contract.functions.joinGame().build_transaction({
    "from": mywallet,
    "value": bet,
    "nonce": nonce,
    "gas": 300000,
    "gasPrice": w3.eth.gas_price
})

signed_tx = w3.eth.account.sign_transaction(tx, myprivkey)
tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

print("Joining game...")
receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Joined! Tx:", tx_hash.hex())

# GAME LOOP

print("\n--- GAME STARTED ---\n")

while True:

    game_over = contract.functions.gameOver().call()
    if game_over:
        print("Game is already over.")
        break

    guess = int(input("Enter your guess (1-100): "))

    nonce = w3.eth.get_transaction_count(mywallet)

    tx = contract.functions.guess(guess).build_transaction({
        "from": mywallet,
        "nonce": nonce,
        "gas": 300000,
        "gasPrice": w3.eth.gas_price
    })

    signed_tx = w3.eth.account.sign_transaction(tx, myprivkey)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    
    # READ EVENTS
    

    guess_events = contract.events.GuessResult().process_receipt(receipt)
    for event in guess_events:
        print("Result:", event["args"]["result"])

    game_events = contract.events.GameEnded().process_receipt(receipt)
    for event in game_events:
        print("\nGAME OVER!")
        print("Winner:", event["args"]["winner"])
        print("Amount Won:", w3.from_wei(event["args"]["amountWon"], "ether"), "ETH")
        exit()

    print("Attempts used:",
          contract.functions.attempts().call(),
          "/",
          contract.functions.maxAttempts().call())
