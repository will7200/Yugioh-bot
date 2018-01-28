import re
from abc import abstractmethod
from enum import Enum

from bot.modes.Events import Signal
# from bot.providers.duellinks import DuelLinksInfo
# from bot.providers import Provider
from bot.common import crop_image
from bot.shared import LOW_CORR, alpha_numeric


class CheckPoints(Enum):
    beforeStarting = 1
    afterStarting = 2
    beforeEnding = 3
    afterEnding = 4
    checkingBattle = 5


class AbstractBattle(object):
    sort_value = -1

    def __init__(self, provider):
        signalers = {}
        for cp in CheckPoints:
            signalers[cp] = Signal()
        self.signalers = signalers
        self.registered_callbacks = {}
        self.provider = provider  # type: Provider
        self.name_mode = ' '.join(re.findall('[A-Z][^A-Z]*', self.__class__.__name__))

    @abstractmethod
    def battle(self, info, check_battle: bool = False):
        """Method to accomplish the goal of going from start to finish of a Duel Links battle"""
        raise NotImplementedError("battle method not implemented")

    @abstractmethod
    def check_battle(self, info, img):
        raise NotImplementedError("check_battle method not implemented")

    def log(self, info):
        self.provider.root.info("{} Mode,Points: ({},{}) at location: ({}), message: {}".format(
            self.name_mode,
            info.x, info.y, info.page, info.status
        ))

    def __lt__(self, other):
        return self.sort_value < other.sort_value

    def register_callback(self, name, method):
        assert isinstance(name, CheckPoints)
        self.signalers[name].connect(method)

    def start(self, battle, version, info):
        self.provider.tapnsleep(battle, 0)
        if version == 2:
            self.battle(info)
        else:
            self.battle(info, check_battle=True)

    def emit_all(self, *args, **kwargs):
        for cp in CheckPoints:
            self.signalers[cp].emit(*args, **kwargs)


class NPCBattle(AbstractBattle):
    sort_value = 1

    def __init__(self, *args, **kwargs):
        super(NPCBattle, self).__init__(*args, **kwargs)
        self.name_mode = 'NPC Battle'

    def battle(self, info, check_battle: bool = False):
        self.signalers[CheckPoints.beforeStarting].emit(info)
        self.provider.root.info("Battling with {}".format(info.name))
        if check_battle:
            self.provider.wait_for_auto_duel()
            self.provider.__check_battle_is_running__()
        self.signalers[CheckPoints.afterStarting].emit(info)
        self.provider.wait_for('OK')
        self.signalers[CheckPoints.beforeEnding].emit(info)
        if info:
            info.status = "Battle Ended"
            self.log(info)
        self.provider.wait_for_ui(.5)
        self.provider.tap(*self.provider.predefined.button_duel)
        self.provider.wait_for('NEXT', True)
        self.provider.tapnsleep(self.provider.predefined.button_duel, .5)
        self.provider.wait_for('NEXT', True)
        self.provider.wait_for_ui(.3)
        self.provider.tap(*self.provider.predefined.button_duel)
        self.provider.wait_for_white_bottom(True)
        self.provider.wait_for_ui(.5)
        self.provider.tapnsleep(self.provider.predefined.button_duel, .1)
        dialog = True
        while dialog:
            dialog = self.provider.check_if_battle(self.provider.get_img_from_screen_shot())
            if dialog:
                self.provider.tap(*self.provider.predefined.button_duel)
        self.provider.wait_for_ui(.5)
        self.provider.scan_for_ok(LOW_CORR)
        self.provider.wait_for_ui(.1)
        self.provider.scan_for_ok(LOW_CORR)
        self.signalers[CheckPoints.afterEnding].emit(info)

    def check_battle(self, info, img):
        """Will Always return true since this is the last possible battle mode available"""
        img = crop_image(img, **self.provider.predefined.duelist_name_area)
        name = self.provider.img_to_string(img, alpha_numeric).lower()
        info.name = name
        return True


class VagabondBattle(NPCBattle):
    sort_value = 2

    def check_battle(self, info, img):
        img = crop_image(img, **self.provider.predefined.duelist_name_area)
        name = self.provider.img_to_string(img, alpha_numeric).lower()
        if 'vagabond' in name or 'vaga' in name:
            info.name = name.replace('the', '').strip()
            return True
        return False


if __name__ == '__main__':
    ab = AbstractBattle()


    def fake(arg1, karg='Nope'):
        print(arg1, karg)


    ab.register_callback(CheckPoints.beforeStarting, fake)
    ab.register_callback(CheckPoints.afterEnding, fake)
    ab.signalers[CheckPoints.beforeStarting].emit('aasdf', 'aas')
