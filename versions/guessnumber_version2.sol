// SPDX-License-Identifier: GPL-3.0
pragma solidity >= 0.8.0;

contract GuessNumberWithBet {

    address public playerA;
    address public playerB;

    uint256 private secretNumber;
    uint256 public maxAttempts;
    uint256 public attempts;
    uint256 public betAmount;

    bool public gameOver;

    event GuessResult(string result);
    event GameEnded(address winner, uint256 amountWon);

    constructor(uint256 _secretNumber, uint256 _maxAttempts) payable {
        require(msg.value > 0, "Must send ETH");
        require(_secretNumber >= 1 && _secretNumber <= 100, "Number must be between 1 and 100");

        playerA = msg.sender;
        secretNumber = _secretNumber;
        maxAttempts = _maxAttempts;
        betAmount = msg.value;
    }

    function joinGame() external payable {
        require(playerB == address(0), "Player B already joined");
        require(msg.value == betAmount, "Must match bet");
        require(msg.sender != playerA, "Player A cannot play");

        playerB = msg.sender;
    }

    function guess(uint256 _number) external {
        require(msg.sender == playerB, "Only Player B can guess");
        require(!gameOver, "Game over");
        require(attempts < maxAttempts, "No attempts left");

        attempts++;

        if (_number == secretNumber) {
            _endGame(playerB);
            emit GuessResult("Correct");
        } 
        else if (_number < secretNumber) {
            emit GuessResult("Bigger");
        } 
        else {
            emit GuessResult("Smaller");
        }

        if (attempts == maxAttempts && !gameOver) {
            _endGame(playerA);
        }
    }

    function _endGame(address winner) internal {
        gameOver = true;

        uint256 total = address(this).balance;

        (bool success, ) = payable(winner).call{value: total}("");
        require(success, "Transfer failed");

        emit GameEnded(winner, total);
    }
}
