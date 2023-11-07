from threading import Thread
import typing as t
from time import sleep
from datetime import datetime

class Auto:

    def __init__(self, shedule:int, method:callable, *args, **kwargs):
        """ 定时执行任务 """
        self.shedule = shedule
        self.method = method
        self.args = args
        self.kwargs = kwargs

    def _task(self):
        now_minute = datetime.now().minute
        sleep(((self.shedule + 60 - now_minute ) % 60) * 60)

        while True:
            self.method(*self.args, **self.kwargs)
            sleep(3600)

    def start(self):
        thd = Thread(target=self._task)
        thd.setDaemon(True)
        thd.start()
