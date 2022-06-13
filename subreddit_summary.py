#!/usr/bin/env python3

from datetime import datetime
from glob import glob
from urllib.parse import urlparse
import os
import praw
import requests
import shutil
import subprocess
import sys
import threading
import itertools

dir_output = os.environ["SUBREDDIT_SUMMARY_OUTPUT_DIR"]
dir_staging = f"{dir_output}/staging"

reddit = praw.Reddit(
    client_id=os.environ['REDDIT_CLIENT_ID'],
    client_secret=os.environ['REDDIT_CLIENT_SECRET'],
    redirect_uri=os.environ['REDDIT_REDIRECT_URI'],
    user_agent=os.environ['REDDIT_USER_AGENT'],
)


class DownloadManager(threading.Thread):
    '''
    Controls a single download thread.
    This is used to download a single url.
    '''

    def __init__(self, submission):
        threading.Thread.__init__(self)
        self.submission = submission

    def run(self):
        print(f"hello from: {self.submission.title}")
        filename = self._download(self.submission.url)
        subprocess.run([
            "exiftool",
            f"-IPTC:Keywords+='by u/{self.submission.author}'",
            f"-IPTC:SubjectReference+='postId: {self.submission.id}'",
            f"-IPTC:Contact+='{'%.36s' % self.submission.title}'",
            "-overwrite_original",
            filename])

    def _download(self, url):
        filename = self._get_filename(url)
        open(filename, 'wb').write(requests.get(url, allow_redirects=True).content)
        return filename

    def _get_filename(self, url):
        a = urlparse(url)
        return dir_staging + "/" + os.path.basename(a.path)


class ImageGenerator:
    '''
    Used to generate a montage image, from a list of downloaded files.
    '''

    def generate_image(self, subreddit_name, iter, filterStr: str):
        iter = itertools.islice(iter, 10)

        intermediate_file = f"{dir_staging}/intermediate.webp"
        formatted_datetime = datetime.now().strftime("%Y.%m.%d-%H.%M.%S")
        title_submission = f"reddit.com/r/{subreddit_name} {filterStr} @ {formatted_datetime}"
        filename = f"{subreddit_name}-{filterStr}-{formatted_datetime}"

        os.makedirs(dir_staging, exist_ok=True)
        self._downloadImages(iter)
        self._create_montage(intermediate_file, title_submission)
        os.rename(intermediate_file, f"{dir_output}/{filename}.webp")
        shutil.rmtree(dir_staging)

    def _create_montage(self, intermediate_file, title_submission):
        args = ["montage",
                f"{dir_staging}/*",
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
            t = DownloadManager(submission)
            t.start()
            threads.append(t)


class Condenser:
    '''
    Used to condense several week's worth of montages into a single image.

    This can lead to images of arbitrary size, so it should be used sparingly.
    '''

    def condense(self, type_str: str, subreddit_arr):
        for i in subreddit_arr:
            sub_condensed = f"{i}-{type_str}"
            glob_of_files = glob(f"{dir_output}/{sub_condensed}*")
            if glob_of_files:
                aggregate_image = f"{dir_output}/{type_str}_{i}.jpg"
                self._create_aggregate_image(aggregate_image, glob_of_files)
                self._move_input_files(glob_of_files, sub_condensed)

    def _move_input_files(self, glob_of_files, sub_condensed):
        resolved_location = f"{dir_output}/resolved_{sub_condensed}"
        os.makedirs(resolved_location, exist_ok=True)
        for j in glob_of_files:
            try:
                os.rename(j, f"{resolved_location}/{os.path.basename(j)}")
            except expression as identifier:
                print(identifier)

    def _create_aggregate_image(self, aggregate_image, glob_of_files):
        args = [
                   "convert",
                   "-append"
               ] + glob_of_files + [
                   aggregate_image,
                   aggregate_image
               ]
        subprocess.run(args)


def get_parser():
    import argparse
    parser = argparse.ArgumentParser(description="""
    A script that will create a summary of the most popular posts in a given subreddit.
    """)
    parser.add_argument(
        "-c",
        "--condense",
        dest="condense",
        help="condense multiple summary results from the same subreddit into one image",
        action="store_true",
    )
    parser.add_argument(
        "-a",
        "--all",
        dest="gen_all",
        help="""
        By default, we only get the 'Hot' results, which are trending.
        By passing in this flag, we will also generate results for top=day, top=week and top=month.
        """,
        action="store_true",
    )
    parser.add_argument(
        "subreddits",
        nargs="*"
    )
    return parser


if __name__ == "__main__":

    args = sys.argv[1:]
    parser = get_parser()
    args = parser.parse_args(args)

    generator = ImageGenerator()
    condenser = Condenser()

    if args.condense and args.subreddits:
        condenser.condense("hot", args.subreddits)
        condenser.condense("top_month", args.subreddits)
        condenser.condense("top_week", args.subreddits)
        condenser.condense("top_day", args.subreddits)

    elif args.subreddits:
        for sub in args.subreddits:
            generator.generate_image(sub, reddit.subreddit(sub).hot(limit=20), "hot")
            if args.gen_all:
                generator.generate_image(sub, reddit.subreddit(sub).top("month", limit=20), "top_month")
                generator.generate_image(sub, reddit.subreddit(sub).top("week", limit=20), "top_week")
                generator.generate_image(sub, reddit.subreddit(sub).top("day", limit=20), "top_day")
    else:
        parser.print_help()
        exit(1)
