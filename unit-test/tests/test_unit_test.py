from wake.testing import *

# Print failing tx call trace
def revert_handler(e):
    if e.value.tx is not None:
        print(e.value.tx.call_trace)

from pytypes.contracts.Token import Token


@chain.connect()
@on_revert(revert_handler)
def test_default():


    # Deploy the contract
    token = Token.deploy()

    assert token.owner() == chain.accounts[0].address
    # default call account is
    assert chain.default_call_account == chain.accounts[0]


@chain.connect()
def test_token_basic_operations():

    # Deploy the contract
    token = Token.deploy()

    # Get some accounts to work with
    owner = chain.accounts[0]
    alice = chain.accounts[1]
    bob = chain.accounts[2]

    # Test 1: Check if owner is set correctly
    assert token.owner() == owner.address, "Owner should be set to deployer"

    # Test 2: Create tokens for Alice
    token.mintTokens(alice.address, 1000)
    assert token.getBalance(alice.address) == 1000, "Alice should have 1000 tokens"

    token.transfer(bob.address, 500)

    # Check balances after transfer
    assert token.getBalance(alice.address) == 500, "Alice should have 500 tokens left"
    assert token.getBalance(bob.address) == 500, "Bob should have received 500 tokens"


# @chain.connect()
# def test_token_authorization():
#     token = Token.deploy()

#     # Get a non-owner account
#     non_owner = chain.accounts[1]

#     # Test: Non-owner cannot create tokens
#     with non_owner.as_default():
#         with must_revert(Token.NotAuthorized):
            # token.createTokens(non_owner.address, 1000)




