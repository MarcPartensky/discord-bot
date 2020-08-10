from models.mongo import BindPost
import discord

import time
import math

class User(BindPost):
    """Representation of an user with a mongo post."""

    default_energy_limit = 200
    default_energy_rate =  10*3600 # in energy unit / seconds

    @staticmethod
    def defaults() -> dict:
        return dict(
            wallet=0,
            creation=time.time(),
            use=0,
            last_use=None,
            xp=0,
            energy=0,
            energy_timestamp=0,
            energy_limit=User.default_energy_limit,
            energy_rate=User.default_energy_rate,
            level_up_money = 20,
            level_up_counter = 0,
            
        )

    @property
    def level(self) -> int:
        """Compute the level of a member using his xp.
        The precise function is the following one:
        lambda x: int(max(1/2 * (math.sqrt(8*self.xp/10+1)  - 1), 1))"""
        return int(max(1/2 * (math.sqrt(8*self.xp/10+1)  - 1), 1))

    def update_energy(self):
        """Update the energy of a member using the energy of the member and the energy timestamp."""
        delta_time = (time.time() - self.energy_timestamp)
        delta_energy = delta_time * self.energy_rate
        self.energy = min(self.energy+delta_energy, self.energy_limit)

    @property
    def xp_left(self) -> int:
        """Return the xp left to level up."""
        level = self.level
        next_level = level+1
        level_to_xp = lambda x:x*(x+1)/2*10
        return level_to_xp(next_level) - self.xp

    def update_level_up_reward(self):
        """Update the reward counter."""
        while self.level_up_counter >= self.level:
            self.reward_level_up()
            
    def reward_level_up(self):
        """Reward the user for a level up."""
        self.money += self.level_up_money
        self.level_up_counter += 1
        
    def update(self):
        """Update an user account."""
        self.setdefaults(**User.defaults())
        self.update_energy()
        self.update_level_up()