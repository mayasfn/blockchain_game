// SPDX-License-Identifier: GPL-3.0
pragma solidity >= 0.8.0;

contract GuessNumber {

    // Room structure (max 2 users)
    struct Room {
        uint256[2] users;
        uint8 userCount;
        bool exists; //In Solidity, mappings always return a value, even if nothing was ever stored, so need to have a bool
        uint8 connectedUserNumber;

        uint256[] guesses;      // all user 2's guesses
        uint8[] feedbacks;      // all user 1's feedbacks : 0 = equal, 1 = bigger, 2 = smaller

        uint256 maxRounds;      // game limit (X turns)
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
    event GameFinished(uint256 roomNumber, uint8 winner, bool user1Lied);

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

    function revealSecret(uint256 roomNumber, uint256 secret) external {
        Room storage room = rooms[roomNumber];
        require(room.exists, "Room does not exist");
        require(room.guesses.length == room.maxRounds, "Game not finished");
        require(room.feedbacks.length == room.guesses.length, "Missing feedback");

        bool user1Lied = false;
        bool user2Won = false;
    
        for (uint256 i = 0; i < room.guesses.length; i++) {
            uint256 g = room.guesses[i];
            uint8 f = room.feedbacks[i];
    
            if (g == secret) {
                user2Won = true;
                if (f != 0) user1Lied = true;
                break;
            }
    
            if (g < secret && f != 1) user1Lied = true;    
            if (g > secret && f != 2) user1Lied = true;
        }
    
        uint8 winner = (user1Lied || user2Won) ? 2 : 1;
        emit GameFinished(roomNumber, winner, user1Lied);
}


}


