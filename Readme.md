A script for comparing the top results of a subreddit week over week

## Setup

### External tools required
- exiftool
- imagemagick
- praw

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

## Example


