from wake.testing import *

# Print failing tx call trace
def revert_handler(e):
    if e.tx is not None:
        print(e.tx.call_trace)


from pytypes.tests.helpers.MockERC20 import MockERC20
from pytypes.contracts.Vault import SingleTokenVault

@chain.connect()
@on_revert(revert_handler)
def test_vault_basic_operations():
    token = MockERC20.deploy("MockERC20", "MCK")
    vault = SingleTokenVault.deploy(token, 1000, 1000000)

    user = chain.accounts[0]
    mint_erc20(token, user, 1000)
    token.approve(vault, 1000, from_=user)
    tx = vault.deposit(1000, from_=user)
    print("")
    print(tx.call_trace) # call trace is useful for debugging
    print(tx.events) # events is useful for testing

    assert vault.balanceOf(user) == 1000





