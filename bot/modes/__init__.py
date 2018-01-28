import logging

logger = logging.getLogger("bot.modes")

from bot.modes.Battle import NPCBattle, VagabondBattle

battle_modes = [NPCBattle, VagabondBattle]
