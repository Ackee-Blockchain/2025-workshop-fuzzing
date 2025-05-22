// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Token {
    address public immutable owner;
    mapping(address => uint256) public tokenBalance;

    event Transfer(address indexed from, address indexed to, uint256 value);
    event TokensMinted(address indexed to, uint256 amount);

    error NotEnoughTokens(uint256 requested, uint256 balance);
    error NotAuthorized(address caller);

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        if (msg.sender != owner) {
            revert NotAuthorized(msg.sender);
        }
        _;
    }

    function mintTokens(address recipient, uint256 amount) external onlyOwner {
        tokenBalance[recipient] += amount;
        emit TokensMinted(recipient, amount);
    }

    function transfer(address to, uint256 amount) external {
        if (tokenBalance[msg.sender] < amount) {
            revert NotEnoughTokens(amount, tokenBalance[msg.sender]);
        }

        tokenBalance[msg.sender] -= amount;
        tokenBalance[to] += amount;

        emit Transfer(msg.sender, to, amount);
    }

    function transferWithBytes(bytes calldata data) external {
        (address to, uint256 amount) = abi.decode(data, (address, uint256));
        if (tokenBalance[msg.sender] < amount) {
            revert NotEnoughTokens(amount, tokenBalance[msg.sender]);
        }
        tokenBalance[msg.sender] -= amount;
        tokenBalance[to] += amount;
        emit Transfer(msg.sender, to, amount);
    }

    function getBalance(address account) external view returns (uint256) {
        return tokenBalance[account];
    }
}