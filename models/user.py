import discord

import time
import math

from models.mongo import BindPost
from config.config import cluster


class User(BindPost):
    """Representation of an user with a mongo post."""

    default_energy_limit = 200
    default_energy_rate = 10 * 3600  # in energy unit / seconds

    @staticmethod
    def defaults() -> dict:
        return dict(
            wallet=0,
            creation=time.time(),
            use=0,
            last_use=None,
            xp=0,
            messages=0,
            energy=0,
            energy_timestamp=0,
            energy_limit=User.default_energy_limit,
            energy_rate=User.default_energy_rate,
            level_up_money=20,
            level_up_counter=0,
            roles=[],
        )

    @property
    def level(self) -> int:
        """Compute the level of a member using his xp.
        The precise function is the following one:
        lambda x: int(max(1/2 * (math.sqrt(8*self.xp/10+1)  - 1), 1))"""
        return int(max(1 / 2 * (math.sqrt(8 * self.xp / 10 + 1) - 1), 1))

    def update_energy(self):
        """Update the energy of a member using the energy of the member and the energy timestamp."""
        delta_time = time.time() - self.energy_timestamp
        delta_energy = delta_time * self.energy_rate
        self.energy = min(self.energy + delta_energy, self.energy_limit)

    @property
    def xp_left(self) -> int:
        """Return the xp left to level up."""
        level = self.level
        next_level = level + 1
        level_to_xp = lambda x: x * (x + 1) / 2 * 10
        return level_to_xp(next_level) - self.xp

    def update_level_up(self):
        """Update the reward counter."""
        while self.level_up_counter < self.level:
            self.reward_level_up()

    def reward_level_up(self):
        """Reward the user for a level up."""
        self.wallet += self.level_up_money
        self.level_up_counter += 1

    def update_role(self, member: discord.Member):
        """Update the roles of an user given his level."""
        if not "roles" in self:
            self.roles = []
        # Iterate on all the roles available
        for name, level in cluster.users.options.roles.items():
            if name == "_id":
                continue
            if int(level) >= int(self.level) and name not in self.roles:
                self.roles.append(name)

    def update(self, member: discord.Member):
        """Update an user account."""
        self.setdefaults(**User.defaults())
        self.update_energy()
        self.update_level_up()
        self.update_role(member)
