import os
import time
from threading import Thread

import ffmpeg
import requests
from django.db import models

from TV_LEARNING.settings import HTTP_PROXY, TEMP_DIR, NGINX_MOVIES_PATH, MAX_TRYS_TO_DOWNLOAD, MAX_TRYS_TO_CONVERT, \
    PREPROCESSOR_MAX_TREADS, PREPROCESSOR_DISPATCHING_PERIOD_SECONDS
from common_utils.logging_utils import LoggerFactory
from movies_manager.models import Movie

if not os.path.exists(TEMP_DIR):
    os.mkdir(TEMP_DIR)

if not os.path.exists(NGINX_MOVIES_PATH):
    os.mkdir(NGINX_MOVIES_PATH)

logger = LoggerFactory.get_instance()


class PreprocessingMovie(models.Model):
    IN_QUEUE = "Q"
    DOWNLOADING = "D"
    CONVERTING = "C"
    SUCCESSFUL = "S"
    FAILED = "F"
    STATES = [
        (IN_QUEUE, "Waiting in queue"),
        (DOWNLOADING, "Downloading..."),
        (CONVERTING, "Converting..."),
        (SUCCESSFUL, "Successful!"),
        (FAILED, "Failed!"),
    ]
    not_complete_states = [IN_QUEUE, DOWNLOADING, CONVERTING]

    thread_by_id = {}

    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    download_url = models.CharField(max_length=1000, null=False, blank=False)
    use_proxy_to_download = models.BooleanField(default=False)
    downloading_trys = models.IntegerField(default=0)
    converting_trys = models.IntegerField(default=0)
    state = models.CharField(max_length=20, blank=False, null=False, choices=STATES, default=IN_QUEUE)

    def get_movie_file_name(self):
        return f'{self.movie.id}.mp4'

    def get_downloading_path(self):
        return os.path.join(TEMP_DIR, self.get_movie_file_name())

    def download_by_url(self):
        proxies = None
        if self.use_proxy_to_download:
            proxies = {'http': HTTP_PROXY, 'https': HTTP_PROXY}

        downloading_path = self.get_downloading_path()
        with requests.get(self.download_url, stream=True, proxies=proxies) as r, open(downloading_path, 'wb') as f:
            r.raise_for_status()
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

        if not os.path.isfile(downloading_path):
            raise Exception('Created file does not exist!')

    def convert_movie(self):
        converted_movie_path = os.path.join(NGINX_MOVIES_PATH, self.get_movie_file_name())

        if os.path.isfile(converted_movie_path):
            os.remove(converted_movie_path)

        downloaded_movie_path = self.get_downloading_path()

        ffmpeg.input(downloaded_movie_path).output(converted_movie_path, vcodec='libx264',
                                                   crf=34,  # Constant Rate Factor (CRF)
                                                   s='480x270',  # Resolution
                                                   r='25',  # Frame rate
                                                   bitrate='30k',  # Video bitrate
                                                   movflags='+faststart').run()

        if not os.path.isfile(converted_movie_path):
            raise Exception('Converted movie does not exist!')

    def set_state(self, state):
        self.state = state
        self.save()

    # This method will do all steps of preprocessing of a model, downloading + converting
    # If each step failed, it will retry
    def worker_process(self):
        movie_name = f'{self.movie.title1[:10]}...(id={self.movie.id})'

        self.set_state(PreprocessingMovie.DOWNLOADING)

        while self.state is PreprocessingMovie.DOWNLOADING:
            try:
                self.downloading_trys += 1
                self.save()
                self.download_by_url()
                self.set_state(PreprocessingMovie.CONVERTING)
            except Exception as e:
                logger.error(f'Downloading of {movie_name} was failed:')
                logger.error(e)
                if self.downloading_trys >= MAX_TRYS_TO_DOWNLOAD:
                    self.set_state(PreprocessingMovie.FAILED)
                    return

        while self.state is PreprocessingMovie.CONVERTING:
            try:
                self.converting_trys += 1
                self.save()
                self.convert_movie()
                os.remove(self.get_downloading_path())
                self.movie.specific_stream_url = ''
                self.movie.save()
                self.set_state(PreprocessingMovie.SUCCESSFUL)
            except Exception as e:
                logger.error(f'Converting of {movie_name} was failed:')
                logger.error(e)
                if self.converting_trys >= MAX_TRYS_TO_CONVERT:
                    self.set_state(PreprocessingMovie.FAILED)
                    return

    @staticmethod
    def thread_dispatcher():
        while True:
            keys_to_delete = []
            for preprocessor_movie_id, thread in PreprocessingMovie.thread_by_id.items():
                thread: Thread
                if not thread.is_alive():
                    keys_to_delete.append(preprocessor_movie_id)
            for key in keys_to_delete:
                del PreprocessingMovie.thread_by_id[key]

            for instance in PreprocessingMovie.objects.filter(state__in=PreprocessingMovie.not_complete_states):
                if len(PreprocessingMovie.thread_by_id) >= PREPROCESSOR_MAX_TREADS:
                    break

                if PreprocessingMovie.thread_by_id.__contains__(instance.id):
                    continue

                thread = Thread(target=instance.worker_process)
                PreprocessingMovie.thread_by_id[instance.id] = thread
                thread.start()

            time.sleep(PREPROCESSOR_DISPATCHING_PERIOD_SECONDS)
