#!/usr/bin/env python3

import os
import praw
import sys

from src.condenser import Condenser
from src.image_generator import ImageGenerator

dir_output = os.environ["SUBREDDIT_SUMMARY_OUTPUT_DIR"]
dir_staging = f"{dir_output}/staging"

reddit = praw.Reddit(
    client_id=os.environ['REDDIT_CLIENT_ID'],
    client_secret=os.environ['REDDIT_CLIENT_SECRET'],
    redirect_uri=os.environ['REDDIT_REDIRECT_URI'],
    user_agent=os.environ['REDDIT_USER_AGENT'],
)


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

    generator = ImageGenerator(dir_staging, dir_output)
    condenser = Condenser(dir_output)

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
