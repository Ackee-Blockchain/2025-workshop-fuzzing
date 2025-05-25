// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title EIP712Example
 * @dev Simple voting contract using EIP712 signatures
 */
contract EIP712Example {
    // EIP-712 type hashes
    bytes32 public constant DOMAIN_TYPEHASH = keccak256(
        "EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)"
    );

    bytes32 public constant VOTE_TYPEHASH = keccak256(
        "Vote(string proposal,bool support,uint256 nonce)"
    );

    struct Vote {
        string proposal;
        bool support;
        uint256 nonce;
    }

    // Contract state
    string public name;
    mapping(address => uint256) public nonces;
    mapping(string => mapping(bool => uint256)) public voteCount;

    // Domain separator
    bytes32 private immutable _DOMAIN_SEPARATOR;

    // Events
    event VoteCast(address indexed voter, string proposal, bool support);

    // Custom errors
    error InvalidSignature();

    constructor() {
        name = "SimpleVoting";

        _DOMAIN_SEPARATOR = keccak256(
            abi.encode(
                DOMAIN_TYPEHASH,
                keccak256(bytes(name)),
                keccak256(bytes("1")),
                block.chainid,
                address(this)
            )
        );
    }

    function DOMAIN_SEPARATOR() external view returns (bytes32) {
        return _DOMAIN_SEPARATOR;
    }

    /**
     * @dev Cast a vote using EIP712 signature
     * @param voter Address of the voter
     * @param proposal The proposal being voted on
     * @param support True for yes, false for no
     * @param v v component of signature
     * @param r r component of signature
     * @param s s component of signature
     */
    function castVoteBySignature(
        address voter,
        string calldata proposal,
        bool support,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) external {
        // Create the vote hash
        bytes32 structHash = keccak256(
            abi.encode(
                VOTE_TYPEHASH,
                keccak256(bytes(proposal)),
                support,
                nonces[voter]++
            )
        );

        bytes32 hash = keccak256(
            abi.encodePacked(
                "\x19\x01",
                _DOMAIN_SEPARATOR,
                structHash
            )
        );

        // Verify signature
        address signer = ecrecover(hash, v, r, s);
        if (signer != voter) {
            revert InvalidSignature();
        }

        // Record the vote
        voteCount[proposal][support] += 1;

        emit VoteCast(voter, proposal, support);
    }

    /**
     * @dev Get vote counts for a proposal
     * @param proposal The proposal to check
     * @return yesVotes Number of yes votes
     * @return noVotes Number of no votes
     */
    function getVoteCounts(string calldata proposal) external view returns (uint256 yesVotes, uint256 noVotes) {
        return (voteCount[proposal][true], voteCount[proposal][false]);
    }
}