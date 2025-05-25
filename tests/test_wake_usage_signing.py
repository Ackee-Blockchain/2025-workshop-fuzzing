# Wake testing libraries
from dataclasses import dataclass
from wake.testing import *
from wake.testing import Eip712Domain

# Import the pytypes of the contract to interact with
from pytypes.contracts.EIP712Example import EIP712Example
from pytypes.contracts.PermitToken import PermitToken


def revert_handler(e):
    if e.tx is not None:
        print(e.tx.call_trace)


@chain.connect()
@on_revert(revert_handler)
def test_signing_data():

    alice = chain.accounts[0]
    bob = chain.accounts[1]

    eip712_example = EIP712Example.deploy()

    vote_data = EIP712Example.Vote(
        proposal="Proposal 1",
        support=True,
        nonce=eip712_example.nonces(alice.address)
    )

    permit_domain = Eip712Domain(
        name="SimpleVoting",
        version="1",
        chainId=chain.chain_id,
        verifyingContract=eip712_example.address,
    )

    vote_typehash = keccak256(b"Vote(string proposal,bool support,uint256 nonce)")

    assert vote_typehash == eip712_example.VOTE_TYPEHASH()

    vote_hash = keccak256(abi.encode(vote_typehash, keccak256(vote_data.proposal.encode('utf-8')), vote_data.support, uint256(vote_data.nonce)))

    # print("vote_hash", vote_hash.hex())

    domain_separator = eip712_example.DOMAIN_SEPARATOR()

    signing_hash = keccak256(abi.encode_packed(b"\x19\x01", domain_separator, vote_hash))

    signature = alice.sign_hash(signing_hash)

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



@chain.connect()
def test_eip712_example():

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

    permit_token = PermitToken.deploy(alice)

    @dataclass
    class Permit:
        owner: Address
        spender: Address
        value: uint256
        nonce: uint256
        deadline: uint256

    permit_domain = Eip712Domain(
        name="PermitToken",
        version="1",
        chainId=chain.chain_id,
        verifyingContract=permit_token.address,
    )

    permit_data = Permit(
        owner=alice.address,
        spender=bob.address,
        value=1000,
        nonce=permit_token.nonces(alice.address),
        deadline=chain.blocks["latest"].timestamp + 1000,
    )


    ## Alice sign the permit to increase the allowance of bob
    ## Automatically generate the TYPEHASH
    signature = alice.sign_structured(
        message=permit_data,
        domain=permit_domain,
    )

    allowance = permit_token.allowance(owner=alice.address, spender=bob.address)
    assert allowance == 0

    permit_token.permit(
        owner=permit_data.owner,
        spender=permit_data.spender,
        value_=permit_data.value,
        deadline=permit_data.deadline,
        v=int.from_bytes(signature[64:65], "big"),
        r=signature[0:32],
        s=signature[32:64],
        from_=bob
    )

    allowance = permit_token.allowance(owner=alice.address, spender=bob.address)
    assert allowance == 1000

