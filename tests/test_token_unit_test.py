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
def test_token_mint_tokens():
    print("") # just for readability

    # Get some accounts to work with
    owner = chain.accounts[0]
    alice = chain.accounts[1]

    # Deploy the contract
    token = Token.deploy(from_=owner)

    assert token.getBalance(alice.address) == 0, "Alice should have 0 tokens"

    # Test 2: Create tokens for Alice
    tx = token.mintTokens(alice.address, 1000, from_=owner)
    print(tx.call_trace)
    print(tx.events)

    events: list[Token.TokensMinted] = []
    for e in tx.events:
        if isinstance(e, Token.TokensMinted):
            events.append(e)

    assert len(events) == 1, "There should be 1 TokensMinted event"
    assert events[0].to == alice.address, "Recipient should be Alice"
    assert events[0].amount == 1000, "Amount should be 1000"

    assert token.getBalance(alice.address) == 1000, "Alice should have 1000 tokens"

    print("test_token_mint_tokens done")

@chain.connect()
def test_token_transfer():

    # Get some accounts to work with
    owner = chain.accounts[0]
    alice = chain.accounts[1]
    bob = chain.accounts[2]

    # Deploy the contract
    token = Token.deploy(from_=owner)

    token.mintTokens(alice.address, 1000, from_=owner)
    assert token.getBalance(alice.address) == 1000, "Alice should have 1000 tokens"

    tx = token.transfer(bob.address, 500, from_=alice.address)

    events: list[Token.Transfer] = []
    for e in tx.events:
        if isinstance(e, Token.Transfer):
            events.append(e)

    assert len(events) == 1, "There should be 1 Transfer event"
    assert events[0].from_ == alice.address, "Sender should be Alice"
    assert events[0].to == bob.address, "Recipient should be Bob"
    assert events[0].value == 500, "Amount should be 500"

    # Check balances after transfer
    assert token.getBalance(alice.address) == 500, "Alice should have 500 tokens left"
    assert token.getBalance(bob.address) == 500, "Bob should have received 500 tokens"

    print("test_token_basic_operations done")

@chain.connect()
def test_token_transfer_not_enough_tokens():

    # Get some accounts to work with
    owner = chain.accounts[0]
    alice = chain.accounts[1]
    bob = chain.accounts[2]

    # Deploy the contract
    token = Token.deploy(from_=owner)

    assert token.getBalance(alice.address) == 0, "Alice should have 0 tokens"

    with must_revert(Token.NotEnoughTokens):
        token.transfer(bob.address, 500, from_=alice.address)

    print("test_token_basic_operations done")