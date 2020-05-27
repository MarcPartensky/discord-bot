from config.config import masters, cluster
from models.shops.commands import CommandsShop
commands = CommandsShop(masters, cluster.shops.commands, cluster.users)
