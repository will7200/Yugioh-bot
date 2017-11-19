import logging


class LastRecordHandler(logging.Handler):
    def __init__(self):
        logging.Handler.__init__(self)
        self.lastRecord = None

    def emit(self, record):
        self.lastRecord = record

    def get_record(self):
        return self.lastRecord.getMessage()
