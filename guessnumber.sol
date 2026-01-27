// SPDX-License-Identifier: GPL-3.0
pragma solidity >= 0.8.0;

contract GuessNumber {

    // Room structure (max 2 users)
    struct Room {
        uint256[2] users;
        uint8 userCount;
        bool exists; //In Solidity, mappings always return a value, even if nothing was ever stored, so need to have a bool
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
    function createRoom(uint256 userId) external returns (uint256 roomNumber) {
        roomNumber = getRoomNumber();

        Room storage room = rooms[roomNumber];
        room.users[0] = userId;
        room.userCount = 1;
        room.exists = true;

        return roomNumber; // send room number to user
    }

    /* =========================
        CONNECT TO ROOM
    ==========================*/
    function connectToRoom(uint256 userId, uint256 roomNumber) external  returns (uint256 status)
    {
        Room storage room = rooms[roomNumber];

        if (!room.exists) {
            return 103;
        }

        if (room.userCount == 1) {
            room.users[room.userCount] = userId;
            room.userCount += 1;
            return 101;
        }

        if (room.userCount >= 2) {
            return 102;
        }

        return 104;
    }

    /* =========================
        DELETE ROOM
    ==========================*/
    function deleteRoom(uint256 roomNumber) external {
        require(rooms[roomNumber].exists, "Room does not exist");
        delete rooms[roomNumber];
    }
}

