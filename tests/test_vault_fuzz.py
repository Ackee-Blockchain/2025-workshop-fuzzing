# Wake testing libraries
from collections import defaultdict
from dataclasses import dataclass
from wake.testing import *
from wake.testing.fuzzing import *


from pytypes.contracts.Vault import SingleTokenVault

from pytypes.tests.helpers.MockERC20 import MockERC20


# @dataclass
# class Deposi

class VaultFuzz(FuzzTest):

    token: MockERC20
    vault: SingleTokenVault

    min_deposit_amount: int
    max_deposit_amount: int
    withdraw_delay: int

    deposit_amounts: dict[Account, int]
    last_udpate_timestamp: dict[Account, int]


    def pre_sequence(self):

        self.deposit_amounts = defaultdict(int)
        self.token = MockERC20.deploy("MockERC20", "MCK")

        self.min_deposit_amount = random_int(0, 10**18)
        self.max_deposit_amount = random_int(self.min_deposit_amount, 10**20)

        self.withdraw_delay = random_int(0, 24 * 60 * 60)

        self.vault = SingleTokenVault.deploy(self.token.address, self.min_deposit_amount, self.max_deposit_amount, self.withdraw_delay)

    # @flow()
    def flow_something(self):

        ## prepare input

        ## run transaction

        ## check event

        ## check state

        ## update state
        pass


    @flow()
    def flow_deposit(self):

        user = random_account()


        amount = random_int(self.min_deposit_amount, self.max_deposit_amount)

        mint_erc20(self.token, user, amount)

        self.token.approve(self.vault.address, amount, from_=user)
        tx = self.vault.deposit(amount, from_=user)

        print(tx.call_trace)


        events: list[SingleTokenVault.Deposited] = []
        for e in tx.events:
            if isinstance(e, SingleTokenVault.Deposited):
                events.append(e)

        assert len(events) == 1
        assert events[0].user == user.address
        assert events[0].amount == amount

        self.deposit_amounts[user] += amount
        self.last_udpate_timestamp[user] = chain.blocks["latest"].timestamp


    @flow()
    def flow_withdraw(self):

        eligible_users = [user for user in self.deposit_amounts.keys() if self.deposit_amounts[user] > 0 and self.vault.timeUntilWithdrawal(user.address) == 0]

        if not eligible_users:
            return "No eligible users"

        user = random.choice(eligible_users)

        amount = random_int(0, self.deposit_amounts[user])

        tx = self.vault.withdraw(amount, from_=user)






    @invariant()
    def invariant_deposit_amounts(self):
        for user in self.deposit_amounts.keys():
            assert self.vault.balanceOf(user.address) == self.deposit_amounts[user]






@chain.connect()
def test_vault_fuzz():

    VaultFuzz.run(1, 100)
