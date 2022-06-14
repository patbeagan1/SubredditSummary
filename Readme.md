A script for comparing the best results of a subreddit week over week. It demonstrates a couple of techniques:
- Using argparse
- Using environment variables in a script
- Using imagemagick via python
- Modifying image metadata
- Reddit api access

## Setup

### External tools required
- exiftool
- imagemagick
- praw (a reddit wrapper for python)

#### Environment

```bash
# file: ~/.../reddit-secrets.sh 
export REDDIT_CLIENT_ID="K8_mYcLiEntId"
export REDDIT_CLIENT_SECRET="mYCLiEnT-SeCrEt_QvUes"
export REDDIT_REDIRECT_URI="localhost:8080"
export REDDIT_USER_AGENT="subreddit summary by u/myUsername"
export SUBREDDIT_SUMMARY_OUTPUT_DIR="/Users/MyUser/myUsername"

# file: ~/.bashrc or ~/.zshrc
source ~/.../reddit-secrets.sh
```

## Usage 

```
usage: subreddit_summary.py [-h] [-c] [-a] [subreddits ...]

A script that will create a summary of the most popular posts in a given subreddit.

positional arguments:
  subreddits

optional arguments:
  -h, --help      show this help message and exit
  -c, --condense  condense multiple summary results from the same subreddit into one image
  -a, --all       By default, we only get the 'Hot' results, which are trending. By passing in this flag, we will also
                  generate results for top=day, top=week and top=month.
```

## Example

### Generating a simple summary 

```bash
./subreddit_summary.py wallpapers
```
![wallpapers-hot-2022 06 12-21 43 52](https://user-images.githubusercontent.com/10187351/173271012-6bdac67b-03cc-4cdc-88a0-cc375d1a9491.jpg)

### Consolidating summary files

```bash
./subreddit_summary.py wallpapers
./subreddit_summary.py wallpapers
./subreddit_summary.py -c wallpapers 
```
![hot_wallpapers](https://user-images.githubusercontent.com/10187351/173473035-4b58fd98-d28e-4250-a551-c57a4faeaeae.jpg)

### Generating **all** summaries (`hot`, `top_month`, `top_week`, `top_day`)

```bash
./subreddit_summary.py -a wallpapers
```
||||
|-|-|-|
|![wallpapers-top_month-2022 06 12-22 02 02 webp](https://user-images.githubusercontent.com/10187351/173272308-694ea34f-2c5e-44eb-8174-574933700ad0.jpg)|![wallpapers-top_week-2022 06 12-22 08 21 webp](https://user-images.githubusercontent.com/10187351/173272818-afbe0224-5a7f-4233-95a0-633bd65c6343.jpg)|![wallpapers-top_day-2022 06 12-22 02 27 webp](https://user-images.githubusercontent.com/10187351/173272311-ac6e74cb-8e95-4626-a466-dabc9284c4e8.jpg)|

### Generating multiple summaries at once

```bash
./subreddit_summary.py aww wallpapers
```
|||
|-|-|
|![wallpapers-hot-2022 06 12-22 23 53 webp](https://user-images.githubusercontent.com/10187351/173274083-0ee1ab35-22fb-4e2a-90e7-0b10d31eb06b.jpg)|![aww-hot-2022 06 12-22 23 51 webp](https://user-images.githubusercontent.com/10187351/173274085-7d3850ca-6cc9-4356-b566-256b491e9b76.jpg)|
