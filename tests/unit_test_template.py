from wake.testing import *

# Print failing tx call trace
def revert_handler(e):
    if e.value.tx is not None:
        print(e.value.tx.call_trace)

from pytypes.contracts.Token import Token


@chain.connect()
@on_revert(revert_handler)
def test_unit():
    pass

@chain.connect()
@on_revert(revert_handler)
def test_unit_second():
    pass
