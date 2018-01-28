import threading
import weakref
import logging

logger = logging.getLogger("bot.events")


### These class are taken from https://github.com/nitely/python-signals
class BoundMethodWeakref(object):
    def __init__(self, func):
        self.func_name = func.__name__
        self.wref = weakref.ref(func.__self__)  # __self__ returns the class

    def __call__(self):
        func_cls = self.wref()
        if func_cls is None:  # lost reference
            return None
        else:
            func = getattr(func_cls, self.func_name)
            return func


def weak_ref(callback):
    if getattr(callback, '__self__', None) is not None:  # is a bound method?
        return BoundMethodWeakref(callback)
    else:
        return weakref.ref(callback)


class Signal(object):
    def __init__(self):
        self.callbacks = []
        self.r_lock = threading.RLock()

    def connect(self, callback):
        with self.r_lock:
            callback = weak_ref(callback)
            self.callbacks.append(callback)

    def disconnect(self, callback):
        with self.r_lock:
            for index, weakref_callback in enumerate(self.callbacks):
                if callback == weakref_callback():
                    del self.callbacks[index]
                    break

    def emit(self, *args, **kwargs):
        if len(self.callbacks) == 0:
            return
        with self.r_lock:
            for index, weakref_callback in enumerate(self.callbacks):
                callback = weakref_callback()
                if callback is not None:
                    callback(*args, **kwargs)
                else:  # lost reference
                    del self.callbacks[index]
