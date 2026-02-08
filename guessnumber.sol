// SPDX-License-Identifier: GPL-3.0
pragma solidity >= 0.8.0;

contract GuessNumber {

    // Room structure (max 2 users)
    struct Room {
        address guess_player;
        address feedback_player;

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

    /* =========================
        CREATE ROOM
    ==========================*/
    event RoomCreated(uint256 roomNumber, uint256 userId);
    event UserConnected(uint256 roomNumber, uint256 userId, uint256 status);
    event GuessSent(uint256 roomNumber, uint256 guess, uint256 round);
    event FeedbackSent(uint256 roomNumber, uint8 feedback, uint256 round);
    event RoomDeleted(uint256 roomNumber);
    event GameFinished(uint256 roomNumber, address winner, bool user1Lied); // todo : you need to send if user 2 guessed properly or not and if he won just cause user 1 lied 

    function createRoom(uint256 userId, uint256 numberRounds) external returns (uint256 roomNumber) {
        roomNumber = getRoomNumber();

        Room storage room = rooms[roomNumber];
        room.users[0] = userId;
        room.userCount = 1;
        room.exists = true;
        room.maxRounds = numberRounds;

        emit RoomCreated(roomNumber, userId);
        return roomNumber; // send room number to user
    }

    /* =========================
        CONNECT TO ROOM
    ==========================*/
    function connectToRoom(uint256 userId, uint256 roomNumber) external  returns (uint256 status)
    {
        Room storage room = rooms[roomNumber];

        if (!room.exists) {
            emit UserConnected(roomNumber, userId, 103);
            return 103;
        }

        if (room.userCount == 1) {
            room.users[room.userCount] = userId;
            room.userCount += 1;
            if(room.connectedUserNumber ==1){
                emit UserConnected(roomNumber, userId, 102);
                return 102;
            }
            else{
                emit UserConnected(roomNumber, userId, 101);
                return 101;
            }
            
        }

        if (room.userCount >= 2) {
            emit UserConnected(roomNumber, userId, 104);
            return 104;
        }

        return 104;
    }

    function connectedUserNumber(uint256 roomNumber, uint8 user) external {
        Room storage room = rooms[roomNumber];

        require(room.exists, "Room does not exist");
        require(room.connectedUserNumber <= 2, "Invalid user status");

        room.connectedUserNumber = user;
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
        require(room.userCount == 2, "Room not ready");
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
        require(msg.sender == room.users[0], "Only player 1 can reveal");

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
            if (gguess > secret && feedback != 2){ user1Lied = true;, break;}
        }

        address winner = (user1Lied || user2Won) ? room.users[1] : room.users[0];
        endingWithdrawals[winner] += room.entryFee; // TODO properly rewrite winnings
        emit GameFinished(roomNumber, winner, user1Lied);
    }

    // The "Pull" function: Player calls this to get their fake ETH back to MetaMask

    function withdrawpendingWithdrawals() external {
        uint256 amount = pendingWithdrawals[msg.sender];
        require(amount > 0, "No funds to withdraw");
        // Security: Reset balance BEFORE the transfer (prevents reentrancy)
        pendingWithdrawals[msg.sender] = 0;
        (bool success, ) = payable(msg.sender).call{value: amount}("");
        require(success, "Transfer failed");
    }

    // If Player 1 disappears, Player 2 calls this to win by default
    function claimTimeout(uint256 roomNumber) external {
        Room storage room = rooms[roomNumber];
        require(block.timestamp > room.revealDeadline, "Wait for deadline");
        require(msg.sender == room.player2, "Only player 2 can claim");

        uint256 totalPot = room.entryFee * 2;
        pendingWithdrawals[room.player2] += totalPot;
        delete rooms[roomNumber];
    }


}


