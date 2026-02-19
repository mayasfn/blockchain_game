// SPDX-License-Identifier: GPL-3.0
pragma solidity >= 0.8.0;

contract GuessNumber {

    // Room structure (max 2 users)
    struct Room {
        address guess_player;
        address feedback_player;
        uint8 connectedUserNumber;
        bytes32 secretHash; // The locked-in secret
        uint256[] guesses;      // all user 2's guesses
        uint8[] feedbacks;      // all user 1's feedbacks : 0 = equal, 1 = bigger, 2 = smaller

        uint8 userCount;
        bool exists; //In Solidity, mappings always return a value, even if nothing was ever stored, so need to have a bool


        uint256 maxRounds;      // game limit (X turns)
        uint256 entryFee;     // Amount of ETH staked
        uint256 revealDeadline; // Time by which player1 MUST reveal --> todo a revoir 
    }

    // roomNumber => Room
    mapping(uint256 => Room) public rooms;

    // Auto-increment room number
    uint256 private currentRoomNumber;

    /* =========================
        ROOM NUMBER GENERATOR
    ==========================*/
    function getRoomNumber() internal returns (uint256) {
        currentRoomNumber += 1;
        return currentRoomNumber;
    }

    function getHash(uint256 _number) public pure returns (bytes32) {
        return keccak256(abi.encodePacked(_number));
    }
    /* =========================
        CREATE ROOM
    ==========================*/
    event RoomCreated(uint256 roomNumber, address creator);
    event UserConnected(uint256 roomNumber, address player, uint256 status);
    event GuessSent(uint256 roomNumber, uint256 guess, uint256 round);
    event FeedbackSent(uint256 roomNumber, uint8 feedback, uint256 round);
    event RoomDeleted(uint256 roomNumber);
    event GameFinished(uint256 roomNumber, address winner, bool user1Lied);

    function createRoom(uint256 numberRounds, bytes32 _secretHash) external payable returns (uint256 roomNumber) {
        require(msg.value > 0, "Entry fee required"); // Optional: enforce a bet
        roomNumber = getRoomNumber();

        Room storage room = rooms[roomNumber];
        room.secretHash = _secretHash;
        room.feedback_player = msg.sender; // Set User 1
        room.userCount = 1;
        room.exists = true;
        room.maxRounds = numberRounds;
        room.entryFee = msg.value; // Store the bet amount

        emit RoomCreated(roomNumber, msg.sender);
        return roomNumber; // send room number to user
    }

    /* =========================
        CONNECT TO ROOM
    ==========================*/
    function connectToRoom(uint256 roomNumber) external payable returns (uint256 status) {
            Room storage room = rooms[roomNumber];

            if (!room.exists) return 103;
            if (room.userCount >= 2) return 104;
            require(msg.value == room.entryFee, "Must match entry fee");
            require(msg.sender != room.feedback_player, "You cannot play against yourself");
            room.guess_player = msg.sender;
            room.userCount = 2;
            // Set a 24-hour deadline from the moment player 2 joins
            room.revealDeadline = block.timestamp + 24 hours;

            emit UserConnected(roomNumber, msg.sender, 101);
            return 101;
        }

    /* =========================
        DELETE ROOM
    ==========================*/
    function deleteRoom(uint256 roomNumber) external {
        require(rooms[roomNumber].exists, "Room does not exist");
        delete rooms[roomNumber];
        emit RoomDeleted(roomNumber);
    }


    /* =========================
        USER 2 SENDS GUESS
    ==========================*/
    function setUser2Guess(uint256 roomNumber, uint256 guess) external {
        Room storage room = rooms[roomNumber];

        require(room.exists, "Room does not exist");
        require(msg.sender == room.guess_player, "Only guesser can play");
        require(room.guesses.length < room.maxRounds, "Max rounds reached");

        room.guesses.push(guess);
        emit GuessSent(roomNumber, guess, room.guesses.length);
    }

    /* =========================
        USER 1 SENDS FEEDBACK
    ==========================*/
    function setUser1Feedback(uint256 roomNumber, uint8 feedback) external {
        require(feedback <= 2, "Invalid feedback");

        Room storage room = rooms[roomNumber];
        require(msg.sender == room.feedback_player, "Only host can give feedback");
        require(room.exists, "Room does not exist");
        require(room.feedbacks.length < room.guesses.length, "Feedback already sent");

        room.feedbacks.push(feedback);

        emit FeedbackSent(roomNumber, feedback, room.feedbacks.length);
    }

    /* ================================
        END OF GAME VERIFICATIONS
    =================================*/

    // Map addresses to their pendingWithdrawals (The "Pull" Payout Ledger)
    mapping(address => uint256) public pendingWithdrawals;

    function revealSecret(uint256 roomNumber, uint256 secret) external {
        Room storage room = rooms[roomNumber];
        require(room.exists, "Room does not exist");
        require(room.guesses.length == room.maxRounds, "Game not finished");
        require(room.feedbacks.length == room.guesses.length, "Missing feedback");
        require(msg.sender == room.feedback_player, "Only host can reveal");
        require(keccak256(abi.encodePacked(secret)) == room.secretHash, "Revealed secret does not match hash!");
        bool user1Lied = false;
        bool user2Won = false;
    
        // all user 1's feedbacks : 0 = equal, 1 = bigger, 2 = smaller
        for (uint256 i = 0; i < room.guesses.length; i++) {
            uint256 guess = room.guesses[i];
            uint8 feedback = room.feedbacks[i];
    
            if (guess == secret) {
                user2Won = true;
                if (feedback != 0) user1Lied = true;
                break;
            }
    
            if (guess < secret && feedback != 1) {user1Lied = true;  break;}  
            if (guess > secret && feedback != 2){ user1Lied = true; break;}
        }

        address winner = (user1Lied || user2Won) ? room.guess_player: room.feedback_player;
        uint256 totalPot = room.entryFee * 2;
        pendingWithdrawals[winner] += totalPot;
        emit GameFinished(roomNumber, winner, user1Lied);
        delete rooms[roomNumber];
    }

    /* =========================
        CLAIM TIMEOUT (Path 2)
       - Called by User 2 if User 1 ghosts
       - Sends money IMMEDIATELY (Push Pattern)
    ==========================*/
    function claimTimeout(uint256 roomNumber) external {
        Room storage room = rooms[roomNumber];
        require(room.exists, "Room does not exist");
        require(block.timestamp > room.revealDeadline, "Wait for deadline");
        require(msg.sender == room.guess_player, "Only player 2 can claim");

        uint256 totalPot = room.entryFee * 2;
        
        // Security: Delete room FIRST to prevent re-entrancy
        delete rooms[roomNumber];

        // DIRECT SEND: No need to call withdraw
        (bool success, ) = payable(msg.sender).call{value: totalPot}("");
        require(success, "Transfer failed");
    }
    /* =========================
        WITHDRAW WINNINGS
       - Used by the winner of Path 1
    ==========================*/
    function withdrawWinnings() external {
        uint256 amount = pendingWithdrawals[msg.sender];
        require(amount > 0, "No funds to withdraw");

        // Security: Reset balance BEFORE transfer
        pendingWithdrawals[msg.sender] = 0;

        (bool success, ) = payable(msg.sender).call{value: amount}("");
        require(success, "Transfer failed");
    }
}