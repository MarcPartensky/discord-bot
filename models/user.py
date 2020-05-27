from models.mongo import Post
import discord

import time

class User(Post):
    defaults = dict(
        wallet=0,
        creation=time.time(),
        use=0,
        last_use=None,
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setdefaults(**User.defaults)

    def setdefaults(self, **kwargs):
        for k,v in kwargs.items():
            self.setdefault(k, v)