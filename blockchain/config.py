from web3 import Web3

RPC_URL = 'https://ethereum-sepolia-rpc.publicnode.com'

CONTRACT_ADDRESS = Web3.to_checksum_address(
    "0x5B10785A6D02a18678dd1A009FC1735346D71857"
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
				"internalType": "uint256",
				"name": "userId",
				"type": "uint256"
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
				"internalType": "uint256",
				"name": "userId",
				"type": "uint256"
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
				"name": "userId",
				"type": "uint256"
			},
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
				"name": "user",
				"type": "uint8"
			}
		],
		"name": "connectedUserNumber",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "userId",
				"type": "uint256"
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
			}
		],
		"name": "getUser1Feedback",
		"outputs": [
			{
				"internalType": "uint8",
				"name": "feedback",
				"type": "uint8"
			},
			{
				"internalType": "uint256",
				"name": "round",
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
				"name": "roomNumber",
				"type": "uint256"
			}
		],
		"name": "getUser2Guess",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "guess",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "round",
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
				"internalType": "uint8",
				"name": "connectedUserNumber",
				"type": "uint8"
			},
			{
				"internalType": "uint256",
				"name": "lastGuess",
				"type": "uint256"
			},
			{
				"internalType": "uint8",
				"name": "lastFeedback",
				"type": "uint8"
			},
			{
				"internalType": "uint256",
				"name": "round",
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
	}
]