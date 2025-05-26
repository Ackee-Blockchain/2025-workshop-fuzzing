# Wake testing libraries
from collections import defaultdict
from dataclasses import dataclass
import logging
from wake.testing import *
from wake.testing.fuzzing import *


from pytypes.contracts.Vault import SingleTokenVault
from pytypes.tests.helpers.MockERC20 import MockERC20

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class VaultFuzz(FuzzTest):

    # Define data structures

    def pre_sequence(self):

        # Initalize contracts here

        logger.info("initialized contracts")

    # Create flow functions for each state changing function in the contract


    @flow()
    def flow_something(self):

        ## prepare random input

        ## run transaction

        ## check events

        ## update python state
        pass


    @invariant()
    def invariant_something(self):
        for account in chain.accounts:

            # check state
            pass


@chain.connect()
def test_vault_fuzz():
    VaultFuzz.run(sequences_count=1, flows_count=100)