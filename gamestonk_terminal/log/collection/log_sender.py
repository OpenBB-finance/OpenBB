# IMPORTATION STANDARD
# import logging
from threading import Thread
from queue import Queue, SimpleQueue
from pathlib import Path

# IMPORTATION THIRDPARTY

# IMPORTATION INTERNAL
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.log.collection.s3_sender import send_to_s3
from gamestonk_terminal.log.generation.directories import get_tmp_dir, get_archive_dir

# DO NOT USE THE FILE LOGGER IN THIS MODULE


class QueueItem:
    @property
    def path(self) -> Path:
        return self.__path

    @property
    def last(self) -> bool:
        return self.__last

    def __init__(self, path: Path, last: bool = False):
        self.__path = path
        self.__last = last

    def __str__(self):
        return "{" + f'"last": {self.last}, "path": {self.path}' + "}"


class LogSender(Thread):
    @property
    def queue(self) -> Queue:
        return self.__queue

    # OVERRIDE
    def run(self):
        queue = self.__queue

        while True:
            item = queue.get()
            file = item.path
            last = item.last

            print(f"LogSender, processing : {file}")

            if gtff.LOG_COLLECTION:
                print(f"Sending to S3 : {file}")

                archives_dir = get_archive_dir()
                tmp_dir = get_tmp_dir()
                try:
                    send_to_s3(file=file, archives_dir=archives_dir, tmp_dir=tmp_dir)
                except Exception as e:
                    print("Sending to S3 failed : %s" % e)
                finally:
                    pass

            if last:
                break

    # OVERRIDE
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.__queue = SimpleQueue()

    def send_path(self, path: Path, last: bool = False):
        """What ever path we send it need to the closed !"""
        queue = self.__queue
        queue.put(QueueItem(path=path, last=last))


LOG_SENDER = LogSender(daemon=True)
LOG_SENDER.start()
