// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/Pausable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title SingleTokenVault
 * @dev A vault contract that manages deposits and withdrawals for a single ERC20 token
 */
contract SingleTokenVault is Pausable, Ownable {
    // Custom Errors
    error InvalidToken();
    error InvalidDepositLimits();
    error BelowMinDeposit();
    error AboveMaxDeposit();
    error TransferFailed();
    error InsufficientBalance();
    error WithdrawalTooSoon(uint256 timeLeft);
    error ZeroAmount();

    IERC20 public immutable token;

    // User address => balance
    mapping(address => uint256) private _balances;

    uint256 public maxDepositAmount;
    uint256 public minDepositAmount;
    uint256 public totalDeposits;

    // Time lock for withdrawals (in seconds)
    uint256 public withdrawalDelay;
    mapping(address => uint256) public lastWithdrawalTime;

    // Events
    event Deposited(address indexed user, uint256 amount);
    event Withdrawn(address indexed user, uint256 amount);
    event DepositLimitsUpdated(uint256 minAmount, uint256 maxAmount);
    event WithdrawalDelayUpdated(uint256 newDelay);
    event EmergencyWithdrawn(address indexed token, uint256 amount);

    constructor(
        address _token,
        uint256 _minDepositAmount,
        uint256 _maxDepositAmount,
        uint256 _withdrawalDelay
    ) Ownable(msg.sender) {
        if (_token == address(0)) revert InvalidToken();
        if (_maxDepositAmount <= _minDepositAmount) revert InvalidDepositLimits();

        token = IERC20(_token);
        minDepositAmount = _minDepositAmount;
        maxDepositAmount = _maxDepositAmount;
        withdrawalDelay = _withdrawalDelay;
    }

    /**
     * @dev Deposits tokens into the vault
     * @param amount The amount of tokens to deposit
     */
    function deposit(uint256 amount) external whenNotPaused {
        if (amount == 0) revert ZeroAmount();
        if (amount < minDepositAmount) revert BelowMinDeposit();
        if (amount > maxDepositAmount) revert AboveMaxDeposit();

        bool success = token.transferFrom(msg.sender, address(this), amount);
        if (!success) revert TransferFailed();

        _balances[msg.sender] += amount;
        totalDeposits += amount;

        lastWithdrawalTime[msg.sender] = block.timestamp;
        emit Deposited(msg.sender, amount);
    }

    /**
     * @dev Withdraws tokens from the vault
     * @param amount The amount of tokens to withdraw
     */
    function withdraw(uint256 amount) external whenNotPaused {
        if (amount == 0) revert ZeroAmount();
        if (_balances[msg.sender] < amount) revert InsufficientBalance();

        uint256 timeLeft = _getTimeUntilWithdrawal(msg.sender);
        if (timeLeft > 0) revert WithdrawalTooSoon(timeLeft);

        _balances[msg.sender] -= amount;
        totalDeposits -= amount;

        bool success = token.transfer(msg.sender, amount);
        if (!success) revert TransferFailed();

        lastWithdrawalTime[msg.sender] = block.timestamp;
        emit Withdrawn(msg.sender, amount);
    }

    /**
     * @dev Emergency withdraw all tokens (only owner)
     */
    function emergencyWithdraw() external onlyOwner {
        uint256 balance = token.balanceOf(address(this));
        if (balance == 0) revert ZeroAmount();

        bool success = token.transfer(owner(), balance);
        if (!success) revert TransferFailed();

        emit EmergencyWithdrawn(address(token), balance);
    }

    /**
     * @dev Returns the balance of a user
     * @param user The user address
     */
    function balanceOf(address user) external view returns (uint256) {
        return _balances[user];
    }

    /**
     * @dev Returns time until next withdrawal is allowed
     * @param user The user address
     */
    function timeUntilWithdrawal(address user) external view returns (uint256) {
        return _getTimeUntilWithdrawal(user);
    }

    /**
     * @dev Internal function to calculate time until withdrawal
     */
    function _getTimeUntilWithdrawal(address user) internal view returns (uint256) {
        uint256 nextWithdrawalTime = lastWithdrawalTime[user] + withdrawalDelay;
        if (block.timestamp >= nextWithdrawalTime) {
            return 0;
        }
        return nextWithdrawalTime - block.timestamp;
    }

    /**
     * @dev Updates deposit limits (only owner)
     */
    function setDepositLimits(uint256 _minAmount, uint256 _maxAmount) external onlyOwner {
        if (_maxAmount <= _minAmount) revert InvalidDepositLimits();
        minDepositAmount = _minAmount;
        maxDepositAmount = _maxAmount;
        emit DepositLimitsUpdated(_minAmount, _maxAmount);
    }

    /**
     * @dev Updates withdrawal delay (only owner)
     */
    function setWithdrawalDelay(uint256 _delay) external onlyOwner {
        withdrawalDelay = _delay;
        emit WithdrawalDelayUpdated(_delay);
    }

    /**
     * @dev Pauses the contract
     */
    function pause() external onlyOwner {
        _pause();
    }

    /**
     * @dev Unpauses the contract
     */
    function unpause() external onlyOwner {
        _unpause();
    }
}