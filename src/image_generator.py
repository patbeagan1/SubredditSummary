import itertools
import os
import shutil
import subprocess
from datetime import datetime

from src.download_manager import DownloadManager


class ImageGenerator:
    '''
    Used to generate a montage image, from a list of downloaded files.
    '''

    def __init__(self, dir_staging, dir_output):
        self._dir_staging = dir_staging
        self._dir_output = dir_output

    def generate_image(self, subreddit_name, iter, filterStr: str):
        iter = itertools.islice(iter, 10)

        intermediate_file = f"{self._dir_staging}/intermediate.webp"
        formatted_datetime = datetime.now().strftime("%Y.%m.%d-%H.%M.%S")
        title_submission = f"reddit.com/r/{subreddit_name} {filterStr} @ {formatted_datetime}"
        filename = f"{subreddit_name}-{filterStr}-{formatted_datetime}"

        os.makedirs(self._dir_staging, exist_ok=True)
        self._downloadImages(iter)
        self._create_montage(intermediate_file, title_submission)
        os.rename(intermediate_file, f"{self._dir_output}/{filename}.webp")
        shutil.rmtree(self._dir_staging)

    def _create_montage(self, intermediate_file, title_submission):
        args = ["montage",
                f"{self._dir_staging}/*",
                "-title", title_submission,
                "-tile", "x1",
                "-geometry", "250x250+4+4>",
                "-set", "label",
                # https://imagemagick.org/script/escape.php
                f"%wx%h\\n%[IPTC:2:12]\\n%[IPTC:2:118]\\n%[IPTC:2:25]",
                intermediate_file]
        subprocess.run(args)

    def _downloadImages(self, iterable):
        threads = []
        for submission in iterable:
            try:
                self._download_single_image(submission, threads)
            except Exception as identifier:
                print(identifier)
                pass
        for t in threads:
            t.join()

    def _download_single_image(self, submission, threads):
        filename, file_extension = os.path.splitext(submission.url)
        if hasattr(submission, 'post_hint') and submission.post_hint == "image" and file_extension != ".gif":
            print(submission.url)
            t = DownloadManager(submission, self._dir_staging)
            t.start()
            threads.append(t)
