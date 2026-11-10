# Thesis: 2027 on X: data and script

This folder reproduces every X number in the report "Every's Thesis Conference on X: Data Analysis and Livestream Chat Feedback."

Run it with Python 3.9 or later, no extra packages: `python3 numbers.py`. It writes `numbers.json`, with every figure in the report, and `topics-per-post.json`, with the topic labels for each community post.

What's here:

- `posts.json`: the 524 candidate posts about the conference, October 27 to November 10, 2026, pulled from X with SocialData. Retweets and the 98 excluded accounts are already out.
- `decisions.json`: every post-level decision, by post id, with its reason: the 25 posts removed because they are not about Thesis, the 12 copy-paste promo posts removed, the 28 borderline posts kept, and the 8 posts added back because posts in the set replied to or quoted them.
- `excluded-accounts.json`: how many of the 98 accounts removed by hand fall under each reason. Handles are withheld.
- `coding.py`: the hand coding of the community posts, with the codebook at the top.
- `numbers.py`: the script. It applies decisions.json, groups the accounts, and computes every table.
