import logging
from abc import abstractmethod

# from bot.providers.predefined import Predefined
# from bot.providers.provider import Provider
from bot.providers.duellinks import DuelLinksInfo, alphabet
from bot.common import crop_image


class AbstractIgnoreEvent(object):
    """
    Class implemented checks to avoid ui elements that should not be access
    as well as doing the task required to avoid specified ui
    """
    sort_value = -1
    root = logging.getLogger("bot.modes.event_checker")

    def __init__(self, provider):
        self.provider = provider  # type: Provider

    @abstractmethod
    def is_occurrence(self, img=None):
        raise NotImplementedError("is_occurrence not implemented")

    @abstractmethod
    def event_condition(self, dl_info: DuelLinksInfo, img=None):
        """

        :param dl_info:
        :type dl_info: DuelLinksInfo
        """
        raise NotImplementedError("event_condition not implemented")

    def event_occurred(self, dl_info: DuelLinksInfo, img=None):
        raise NotImplementedError("event_occured not implemented")


class StreetReplay(AbstractIgnoreEvent):
    looking_for = 'Street Replay'
    alphabet_set = ''.join(set(looking_for)).replace(' ', '')

    def is_occurrence(self, img=None):
        if img is None:
            img = self.provider.get_img_from_screen_shot()
        street_replay = self.provider.predefined.street_replay
        img = crop_image(img, **street_replay)
        word = self.provider.img_to_string(img, self.alphabet_set, mask_area=([200], [255]))
        matched = list(set(word.lower().split(' ')) & set(self.looking_for.lower().split(' ')))
        if len(matched) > 0:
            return True
        return False

    def event_condition(self, dl_info: DuelLinksInfo, img=None):
        return self.provider.predefined.street_replay_location == dl_info.page \
               and self.is_occurrence(img)

    def event_occurred(self, dl_info: DuelLinksInfo, img=None):
        dl_info.status = "street replay cancelling"
        self.provider.compare_with_cancel_button(info=dl_info, img=img)


class RankedDuelsQuickStart(AbstractIgnoreEvent):
    looking_for = 'Ranked Duels Quick Start'
    alphabet_set = ''.join(set(looking_for)).replace(' ', '')

    def is_occurrence(self, img=None):
        if img is None:
            img = self.provider.get_img_from_screen_shot()
        quick_ranked_area = self.provider.predefined.quick_rankduel_area
        img = crop_image(img, **quick_ranked_area)
        word = self.provider.img_to_string(img, self.alphabet_set, mask_area=([200], [255]))
        matched = list(set(word.lower().split(' ')) & set(self.looking_for.lower().split(' ')))
        if len(matched) > 0:
            return True
        return False

    def event_condition(self, dl_info: DuelLinksInfo, img=None):
        return self.provider.predefined.quick_rankduel_location == dl_info.page \
               and self.is_occurrence(img)

    def event_occurred(self, dl_info: DuelLinksInfo, img=None):
        dl_info.status = "{} cancelling".format(self.looking_for)
        self.provider.compare_with_cancel_button(info=dl_info, img=img)
