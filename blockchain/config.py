from web3 import Web3

RPC_URL = 'https://ethereum-sepolia-rpc.publicnode.com'

CONTRACT_ADDRESS = Web3.to_checksum_address(
    "0x5118245cc1530308f0436C4Ca75524EA7dCe39f1"
)

CONTRACT_ABI = [
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "roomNumber",
				"type": "uint256"
			},
			{
				"indexed": False,
				"internalType": "uint8",
				"name": "feedback",
				"type": "uint8"
			},
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "round",
				"type": "uint256"
			}
		],
		"name": "FeedbackSent",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "roomNumber",
				"type": "uint256"
			},
			{
				"indexed": False,
				"internalType": "address",
				"name": "winner",
				"type": "address"
			},
			{
				"indexed": False,
				"internalType": "bool",
				"name": "user1Lied",
				"type": "bool"
			}
		],
		"name": "GameFinished",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "roomNumber",
				"type": "uint256"
			},
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "guess",
				"type": "uint256"
			},
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "round",
				"type": "uint256"
			}
		],
		"name": "GuessSent",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "roomNumber",
				"type": "uint256"
			},
			{
				"indexed": False,
				"internalType": "address",
				"name": "creator",
				"type": "address"
			}
		],
		"name": "RoomCreated",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "roomNumber",
				"type": "uint256"
			}
		],
		"name": "RoomDeleted",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "roomNumber",
				"type": "uint256"
			},
			{
				"indexed": False,
				"internalType": "address",
				"name": "player",
				"type": "address"
			},
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "status",
				"type": "uint256"
			}
		],
		"name": "UserConnected",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "roomNumber",
				"type": "uint256"
			}
		],
		"name": "claimTimeout",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "roomNumber",
				"type": "uint256"
			}
		],
		"name": "connectToRoom",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "status",
				"type": "uint256"
			}
		],
		"stateMutability": "payable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "numberRounds",
				"type": "uint256"
			},
			{
				"internalType": "bytes32",
				"name": "_secretHash",
				"type": "bytes32"
			}
		],
		"name": "createRoom",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "roomNumber",
				"type": "uint256"
			}
		],
		"stateMutability": "payable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "roomNumber",
				"type": "uint256"
			}
		],
		"name": "deleteRoom",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "roomNumber",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "secret",
				"type": "uint256"
			}
		],
		"name": "revealSecret",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "roomNumber",
				"type": "uint256"
			},
			{
				"internalType": "uint8",
				"name": "feedback",
				"type": "uint8"
			}
		],
		"name": "setUser1Feedback",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "roomNumber",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "guess",
				"type": "uint256"
			}
		],
		"name": "setUser2Guess",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "withdrawWinnings",
		"outputs": [],
		"stateMutability": "nonpayable",
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
		"name": "getHash",
		"outputs": [
			{
				"internalType": "bytes32",
				"name": "",
				"type": "bytes32"
			}
		],
		"stateMutability": "pure",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"name": "pendingWithdrawals",
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
		"inputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"name": "rooms",
		"outputs": [
			{
				"internalType": "address",
				"name": "guess_player",
				"type": "address"
			},
			{
				"internalType": "address",
				"name": "feedback_player",
				"type": "address"
			},
			{
				"internalType": "uint8",
				"name": "connectedUserNumber",
				"type": "uint8"
			},
			{
				"internalType": "bytes32",
				"name": "secretHash",
				"type": "bytes32"
			},
			{
				"internalType": "uint8",
				"name": "userCount",
				"type": "uint8"
			},
			{
				"internalType": "bool",
				"name": "exists",
				"type": "bool"
			},
			{
				"internalType": "uint256",
				"name": "maxRounds",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "entryFee",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "revealDeadline",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]