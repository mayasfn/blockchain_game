// SPDX-License-Identifier: GPL-3.0
pragma solidity >= 0.8.0;

contract GuessNumberSimple {

    address public playerA;
    address public playerB;

    uint256 private secretNumber;
    uint256 public maxAttempts;
    uint256 public attempts;
    bool public gameOver;

    event GuessResult(string result);
    event GameEnded(address winner);

    constructor(uint256 _secretNumber, uint256 _maxAttempts) {
        require(_secretNumber >= 1 && _secretNumber <= 100, "Number must be between 1 and 100");

        playerA = msg.sender;
        secretNumber = _secretNumber;
        maxAttempts = _maxAttempts;
    }

    function joinGame() external {
        require(playerB == address(0), "Player B already joined");
        require(msg.sender != playerA, "Player A cannot play");

        playerB = msg.sender;
    }

    function guess(uint256 _number) external {
        require(msg.sender == playerB, "Only Player B can guess");
        require(!gameOver, "Game is over");
        require(attempts < maxAttempts, "No attempts left");

        attempts++;

        if (_number == secretNumber) {
            gameOver = true;
            emit GuessResult("Correct");
            emit GameEnded(playerB);
        } 
        else if (_number < secretNumber) {
            emit GuessResult("Bigger");
        } 
        else {
            emit GuessResult("Smaller");
        }

        if (attempts == maxAttempts && !gameOver) {
            gameOver = true;
            emit GameEnded(playerA);
        }
    }
}
