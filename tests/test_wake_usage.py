# Wake testing libraries
from wake.testing import *


# Import the pytypes of the contract to interact with
from pytypes.contracts.Token import Token


# Connect to the chain. Wake test automatically run the tests functions.
@chain.connect()
def test_default():
    print("hello")


@chain.connect()
def test_account():
    # Defalult accounts are given by the chain as touple.
    print(chain.accounts[0])
    print(len(chain.accounts))



# You can change default chain account size
@chain.connect(accounts=50)
def test_increase_accounts():
    print(len(chain.accounts))
    assert len(chain.accounts) == 50



@chain.connect()
def test_default_call_account():
    # default call account is the first account in the chain.
    # when calling transaction, the default call account is used. if it is not specified.

    token = Token.deploy()
    assert token.owner() == chain.accounts[0].address


@chain.connect()
def test_transaction_call():
    token = Token.deploy()

    ## By using pytypes, you can call transaction easily.
    token.mintTokens(chain.accounts[1], 1000)

    ## Also you can call view functions.
    ## And checking the expected balance.
    assert token.getBalance(chain.accounts[1].address) == 1000



@chain.connect()
def test_transaction_details():
    token = Token.deploy()

    ## The transaction object is returned for the transaction call.
    tx = token.mintTokens(chain.accounts[1], 1000)

    ## You can get transaction information for debugging.
    print("")
    print("call trace:")
    print(tx.call_trace)

    print("events:")
    print(tx.events)



@chain.connect()
def test_specify_sender():
    token = Token.deploy()
    tx = token.mintTokens(chain.accounts[1], 1000)
    assert token.getBalance(chain.accounts[1].address) == 1000


    ## You can specify the sender of the transaction.
    tx = token.transfer(chain.accounts[2], 100, from_=chain.accounts[1])

    ## Checking the result
    assert token.getBalance(chain.accounts[1].address) == 900
    assert token.getBalance(chain.accounts[2].address) == 100


@chain.connect()
def test_check_events():
    token = Token.deploy()

    ## This transaction emit TokensMinted event.
    tx = token.mintTokens(chain.accounts[1], 1000)


    ## Getting all TokensMinted events from the transaction.
    token_minted_events: list[Token.TokensMinted] = []
    for event in tx.events:
        if isinstance(event, Token.TokensMinted):
            token_minted_events.append(event)

    ## Checking the event and their attributes.
    assert len(token_minted_events) == 1
    assert token_minted_events[0].to == chain.accounts[1].address
    assert token_minted_events[0].amount == 1000


@chain.connect()
def test_check_events_short():
    token = Token.deploy()

    ## This transaction emit TokensMinted event.
    tx = token.mintTokens(chain.accounts[1], 1000)

    ## Checking event same as `test_check_events()` in short making use of python feature.
    event = next(e for e in tx.events if isinstance(e, Token.TokensMinted))
    assert event.to == chain.accounts[1].address
    assert event.amount == 1000



@chain.connect()
def test_expect_revert():
    token = Token.deploy()

    ## This should revert since mintTokens can only be called by the owner.
    with must_revert():
        token.mintTokens(chain.accounts[1], 1000, from_=chain.accounts[1])


    ## Also specifying revert Error.
    with must_revert(Token.NotAuthorized):
        token.mintTokens(chain.accounts[1], 1000, from_=chain.accounts[1])

    ## Or specifying attributes of the error.
    with must_revert(Token.NotAuthorized(chain.accounts[1].address)):
        token.mintTokens(chain.accounts[1], 1000, from_=chain.accounts[1])


    ## Or check error later.
    with must_revert() as e:
        token.mintTokens(chain.accounts[1], 1000, from_=chain.accounts[1])

    assert isinstance(e.value, Token.NotAuthorized)
    assert e.value.caller == chain.accounts[1].address



@chain.connect()
def test_access_timestamp():

    ## You can access block information.
    print("latest block number", chain.blocks["latest"].number)

    prev_block = chain.blocks["latest"].number
    prev_timestamp = chain.blocks["latest"].timestamp

    ## You can access timestamp of the block.
    print("latest block timestamp", chain.blocks["latest"].timestamp)

    ## You can manipulate the timestamp by mining block
    chain.mine(lambda x: x + 10) # increase 10 seconds with mining blocks.
    print("latest block number", chain.blocks["latest"].number)
    print("latest block timestamp", chain.blocks["latest"].timestamp)

    assert chain.blocks["latest"].timestamp == prev_timestamp + 10
    assert chain.blocks["latest"].number == prev_block + 1


@chain.connect()
def test_transaction_with_bytes():
    token = Token.deploy()
    tx = token.mintTokens(chain.accounts[0], 1000)


    to = chain.accounts[1].address
    amount = 100

    data = abi.encode(to, uint256(amount)) # You can do abi.encode similary in the solidity.

    tx = token.transferWithBytes(data)

    (to_decoded, amount_decoded) = abi.decode(data, [Address, uint256]) # Also abi.decode similary in the solidity.

    assert to_decoded == to
    assert amount_decoded == amount

    assert token.getBalance(chain.accounts[1].address) == 100
    assert token.getBalance(chain.accounts[0].address) == 900

