# Wake testing libraries
from dataclasses import dataclass
from wake.testing import *
from wake.testing import Eip712Domain

# Import the pytypes of the contract to interact with
from pytypes.contracts.EIP712Example import EIP712Example


@chain.connect()
def test_permit_token():

    alice = chain.accounts[0]
    bob = chain.accounts[1]

    eip712_example = EIP712Example.deploy()

    vote_data = EIP712Example.Vote(
        proposal="Proposal 1",
        support=True,
        nonce=0
    )

    permit_domain = Eip712Domain(
        name="SimpleVoting",
        version="1",
        chainId=chain.chain_id,
        verifyingContract=eip712_example.address,
    )

    signature = alice.sign_structured(
        vote_data,
        permit_domain,
    )

    assert eip712_example.getVoteCounts(proposal=vote_data.proposal) == (0, 0)

    eip712_example.castVoteBySignature(
        voter=alice.address,
        proposal=vote_data.proposal,
        support=vote_data.support,
        v=int.from_bytes(signature[64:65], "big"),
        r=signature[0:32],
        s=signature[32:64],
        from_=bob.address
    )

    assert eip712_example.getVoteCounts(proposal=vote_data.proposal) == (1, 0)




@chain.connect()
def test_permit_token():

    alice = chain.accounts[0]
    bob = chain.accounts[1]

    eip712_example = EIP712Example.deploy()

    vote_data = EIP712Example.Vote(
        proposal="Proposal 1",
        support=True,
        nonce=0
    )

    permit_domain = Eip712Domain(
        name="SimpleVoting",
        version="1",
        chainId=chain.chain_id,
        verifyingContract=eip712_example.address,
    )

    vote_typehash = keccak256(b"Vote(string proposal,bool support,uint256 nonce)")

    vote_hash = keccak256(abi.encode(vote_typehash, keccak256(vote_data.proposal.encode()), vote_data.support, uint256(vote_data.nonce)))

    domain_separator = eip712_example.DOMAIN_SEPARATOR()

    signing_hash = keccak256(abi.encode_packed(b"\x19\x01", domain_separator, vote_hash))

    signature = alice.sign(signing_hash)

    # signature = alice.sign_structured(
    #     vote_data,
    #     permit_domain,
    # )

    assert eip712_example.getVoteCounts(proposal=vote_data.proposal) == (0, 0)

    eip712_example.castVoteBySignature(
        voter=alice.address,
        proposal=vote_data.proposal,
        support=vote_data.support,
        v=int.from_bytes(signature[64:65], "big"),
        r=signature[0:32],
        s=signature[32:64],
        from_=bob.address
    )

    assert eip712_example.getVoteCounts(proposal=vote_data.proposal) == (1, 0)