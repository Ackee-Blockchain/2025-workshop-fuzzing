# Wake testing libraries
from dataclasses import dataclass
from wake.testing import *
from wake.testing import Eip712Domain

# Import the pytypes of the contract to interact with
from pytypes.contracts.Token import Token
from pytypes.contracts.PermitToken import PermitToken


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




