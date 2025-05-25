from wake.testing import *

# Print failing tx call trace
def revert_handler(e):
    if e.value.tx is not None:
        print(e.value.tx.call_trace)

from pytypes.contracts.Token import Token
from pytypes.tests.helpers.MockERC20 import MockERC20
from pytypes.contracts.Vault import SingleTokenVault

# from pytypes.openzeppelin.contracts.token.ERC20.ERC20 import ERC20


@chain.connect()
@on_revert(revert_handler)
def test_default():
    # Deploy the contract
    token = Token.deploy(from_=chain.accounts[0])

    assert token.owner() == chain.accounts[0].address, "Owner should be set to deployer"
    print("test_default done")


@chain.connect()
def test_token_basic_operations():

    # Get some accounts to work with
    owner = chain.accounts[0]
    alice = chain.accounts[1]
    bob = chain.accounts[2]

    # Deploy the contract
    token = Token.deploy(from_=owner)

    # Test 1: Check if owner is set correctly
    assert token.owner() == owner.address, "Owner should be set to deployer"

    # Test 2: Create tokens for Alice
    tx = token.mintTokens(alice.address, 1000, from_=owner)
    print(tx.call_trace)
    print(tx.events)
    assert token.getBalance(alice.address) == 1000, "Alice should have 1000 tokens"

    token.transfer(bob.address, 500, from_=alice.address)

    # Check balances after transfer
    assert token.getBalance(alice.address) == 500, "Alice should have 500 tokens left"
    assert token.getBalance(bob.address) == 500, "Bob should have received 500 tokens"

    print("test_token_basic_operations done")


# @chain.connect()
# def test_vault_basic_operations():
#     token = MockERC20.deploy("MockERC20", "MCK")
#     vault = SingleTokenVault.deploy(token, 1000, 1000000)

#     user = chain.accounts[0]
#     mint_erc20(token, user, 1000)
#     token.approve(vault, 1000, from_=user)
#     tx = vault.deposit(1000, from_=user)
#     print("")
#     print(tx.call_trace)
#     print(tx.events)

#     assert vault.balanceOf(user) == 1000





