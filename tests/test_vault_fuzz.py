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

    ## Define data structures
    token: MockERC20
    vault: SingleTokenVault
    vault_owner: Account

    min_deposit_amount: int
    max_deposit_amount: int

    deposit_amounts: dict[Account, int]
    token_balances: dict[Account, int]


    def pre_sequence(self):

        self.vault_owner = random_account()
        self.token_balances = defaultdict(int)

        self.deposit_amounts = defaultdict(int)
        self.token = MockERC20.deploy("MockERC20", "MCK")


        self.min_deposit_amount = random_int(0, 10**18)
        self.max_deposit_amount = random_int(self.min_deposit_amount, 10**20)

        self.vault = SingleTokenVault.deploy(self.token.address, self.min_deposit_amount, self.max_deposit_amount, from_=self.vault_owner)

        logger.info(f"initialized contracts")


    @flow()
    def flow_deposit(self):

        user = random_account()
        amount = random_int(self.min_deposit_amount, self.max_deposit_amount)

        mint_erc20(self.token, user, amount)
        self.token_balances[user] += amount

        self.token.approve(self.vault.address, amount, from_=user)
        with may_revert() as e:
            tx = self.vault.deposit(amount, from_=user)

            # print(tx.call_trace)

        assert e.value is None

        events: list[SingleTokenVault.Deposited] = []
        for e in tx.events:
            if isinstance(e, SingleTokenVault.Deposited):
                events.append(e)

        ## Shorter version of the above
        # events = [e for e in tx.events if isinstance(e, SingleTokenVault.Deposited)]

        assert len(events) == 1
        assert events[0].user == user.address
        assert events[0].amount == amount

        self.deposit_amounts[user] += amount

        self.token_balances[user] -= amount
        self.token_balances[self.vault] += amount

        logger.info(f"deposited {amount} from {user.address}")


    @flow()
    def flow_withdraw(self):

        eligible_users = [user for user in self.deposit_amounts.keys() if self.deposit_amounts[user] > 0]

        if not eligible_users:
            return "No eligible users"

        user = random.choice(eligible_users)

        amount = random_int(0, self.deposit_amounts[user])

        if self.vault.balanceOf(self.vault) < amount:
            return "vault Insufficient balance"

        tx = self.vault.withdraw(amount, from_=user)

        events: list[SingleTokenVault.Withdrawn] = []
        for e in tx.events:
            if isinstance(e, SingleTokenVault.Withdrawn):
                events.append(e)

        assert len(events) == 1
        assert events[0].user == user.address
        assert events[0].amount == amount

        self.deposit_amounts[user] -= amount

        self.token_balances[self.vault] -= amount
        self.token_balances[user] += amount

        logger.info(f"withdrawn {amount} from {user.address}")

    @flow()
    def flow_emergency_withdraw(self):

        amount = self.token_balances[self.vault]

        if amount == 0:
            return "No tokens to withdraw"

        self.vault.emergencyWithdraw(from_=self.vault_owner)

        self.token_balances[self.vault] -= amount
        self.token_balances[self.vault_owner] += amount

        logger.info(f"emergency withdrawn from {self.vault.address}")

    @flow()
    def flow_set_deposit_limits(self):
        min_amount = random_int(0, 10**18)
        max_amount = random_int(min_amount, 10**21)
        tx = self.vault.setDepositLimits(min_amount, max_amount, from_=self.vault_owner)

        events = [e for e in tx.events if isinstance(e, SingleTokenVault.DepositLimitsUpdated)]
        assert len(events) == 1
        assert events[0].minAmount == min_amount
        assert events[0].maxAmount == max_amount

        self.min_deposit_amount = min_amount
        self.max_deposit_amount = max_amount

        logger.info(f"set deposit limits to {min_amount} and {max_amount}")


    @flow()
    def flow_transfer_token_to_random(self):

        source = random.choice(list(chain.accounts))
        amount = random_int(0, 10**20)
        mint_erc20(self.token, source, amount)
        self.token_balances[source] += amount

        targets = list(chain.accounts) +[self.vault, self.token]
        target = random.choice(targets)

        self.token.transfer(target, amount, from_=source)

        self.token_balances[target] += amount
        self.token_balances[source] -= amount

        logger.info(f"randomly transferred {amount} to {target.address}")



    @invariant()
    def invariant_deposit_amounts(self):
        for user in self.deposit_amounts.keys():
            assert self.vault.balanceOf(user.address) == self.deposit_amounts[user]

    @invariant()
    def invariant_token_balances(self):
        for user in self.token_balances.keys():
            assert self.token.balanceOf(user.address) == self.token_balances[user]

    @invariant()
    def invariant_min_deposit_amount(self):
        assert self.vault.minDepositAmount() == self.min_deposit_amount

    @invariant()
    def invariant_max_deposit_amount(self):
        assert self.vault.maxDepositAmount() == self.max_deposit_amount


@chain.connect()
def test_vault_fuzz():

    VaultFuzz.run(10, 1000)
