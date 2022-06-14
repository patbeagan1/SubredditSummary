import os
import subprocess
import threading
from urllib.parse import urlparse

import requests


class DownloadManager(threading.Thread):
    '''
    Controls a single download thread.
    This is used to download a single url.
    '''

    def __init__(self, submission, dir_staging):
        threading.Thread.__init__(self)
        self._submission = submission
        self._dir_staging = dir_staging

    def run(self):
        print(f"hello from: {self._submission.title}")
        filename = self._download(self._submission.url)
        subprocess.run([
            "exiftool",
            f"-IPTC:Keywords+='by u/{self._submission.author}'",
            f"-IPTC:SubjectReference+='postId: {self._submission.id}'",
            f"-IPTC:Contact+='{'%.36s' % self._submission.title}'",
            "-overwrite_original",
            filename])

    def _download(self, url):
        filename = self._get_filename(url)
        open(filename, 'wb').write(requests.get(url, allow_redirects=True).content)
        return filename

    def _get_filename(self, url):
        a = urlparse(url)
        return self._dir_staging + "/" + os.path.basename(a.path)
