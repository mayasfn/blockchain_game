// SPDX-License-Identifier: GPL-3.0
pragma solidity >= 0.8.0;

contract GuessNumber {

    // Room structure (max 2 users)
    struct Room {
        uint256[2] users;
        uint8 userCount;
        bool exists; //In Solidity, mappings always return a value, even if nothing was ever stored, so need to have a bool
        uint8 connectedUserNumber;

        uint256 lastGuess;      // Last number sent by user 2
        uint8 lastFeedback;     // 0 = equal, 1 = bigger, 2 = smaller
        uint256 round;          // Game round counter
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

    function createRoom(uint256 userId) external returns (uint256 roomNumber) {
        roomNumber = getRoomNumber();

        Room storage room = rooms[roomNumber];
        room.users[0] = userId;
        room.userCount = 1;
        room.exists = true;

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

        room.lastGuess = guess;
        room.round += 1;
        emit GuessSent(roomNumber, guess, room.round);
    }

    /* =========================
        GET USER 2 LAST GUESS
    ==========================*/
    function getUser2Guess(uint256 roomNumber)external view returns (uint256 guess, uint256 round)
    {
        Room storage room = rooms[roomNumber];
        require(room.exists, "Room does not exist");
        
        return (room.lastGuess, room.round);
    }

    /* =========================
        USER 1 SENDS FEEDBACK
    ==========================*/
    function setUser1Feedback(uint256 roomNumber, uint8 feedback) external {
        require(feedback <= 2, "Invalid feedback");

        Room storage room = rooms[roomNumber];
        require(room.exists, "Room does not exist");

        room.lastFeedback = feedback;

        emit FeedbackSent(roomNumber, feedback, room.round);
    }

    /* =========================
        GET USER 1 FEEDBACK
    ==========================*/
    function getUser1Feedback(uint256 roomNumber) external view returns (uint8 feedback, uint256 round)
    {
        Room storage room = rooms[roomNumber];
        require(room.exists, "Room does not exist");

        return (room.lastFeedback, room.round);
    }
}


