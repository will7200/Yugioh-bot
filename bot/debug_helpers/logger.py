import logging
from collections import deque


class LastRecordHandler(logging.Handler):
    def __init__(self, max_length=10):
        logging.Handler.__init__(self)
        self.lastRecords = deque(maxlen=max_length)
        self.max_length = max_length

    def emit(self, record):
        self.lastRecords.append(record)

    def get_record(self, index=-1):
        " Defaults to getting the last know record"
        if len(self.lastRecords) > 0 and -1 <= index < min(self.max_length,len(self.lastRecords)):
            return self.lastRecords[index]
        else:
            return None
