from abc import abstractmethod


class Misc(object):
    @abstractmethod
    def is_process_running(self):
        raise NotImplementedError("is_process_running not implemented")

    @abstractmethod
    def start_process(self):
        raise NotImplementedError("start_process not implemented")

    @abstractmethod
    def kill_process(self):
        raise NotImplementedError("kill_process not implemented")
