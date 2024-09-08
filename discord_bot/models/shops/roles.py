from mdoels.shops.shop import Shop, Item
from config.config import check
from config import emoji
from discord.ext import commands

import discord


class RolesShop(Shop):
    """Shop to buy roles."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
