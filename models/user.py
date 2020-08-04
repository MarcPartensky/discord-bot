from models.mongo import Post
import discord

import time
import math

class User(Post):
    """Representation of an user with a mongo post."""

    default_energy_limit = 200
    default_energy_rate =  10*3600 # in energy unit / seconds

    @property
    @staticmethod:
    def defaults():
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
        )

    def __init__(self, *args, **kwargs):
        """Create an user object."""
        super().__init__(*args, **kwargs)
        self.setdefaults(**User.defaults)

    def level(self):
        """Compute the level of a member using his xp."""
        return self.xp

    def update_energy(self):
        """Update the energy of a member using the energy of the member and the energy timestamp."""
        delta_time = (time.time() - self.energy_timestamp)
        delta_energy = delta_time * self.energy_rate
        self.energy = min(self.energy+self.delta_energy, self.energy_limit)



