import datetime
import os
import sys

# Check if at least a title argument is provided
if len(sys.argv) < 2:
    print("Error: No title provided. Usage: python script.py 'Your Post Title' tag1 tag2 ...")
    sys.exit(1)

# Set your Jekyll posts directory
posts_dir = "_posts"

# Get the post title from the first argument
post_title = sys.argv[1]

# Get tags from subsequent arguments, if any
tags = sys.argv[2:]  # All arguments after the title are considered as tags
tags_formatted = '\n  - '.join(tags)  # Format tags for YAML, each on a new line

# Generate a filename based on the current date and the provided post title
filename_date = datetime.datetime.now().strftime("%Y-%m-%d")
filename = f"{filename_date}-{post_title.replace(' ', '-').lower()}.md"

# Define the front matter template
front_matter = f"""---
title: "{post_title}"
date: {datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")}
categories:
  - blog
tags:
  - {tags_formatted}
---

# Your content goes here.
"""

# Create the full file path
file_path = os.path.join(posts_dir, filename)

# Write the new post with front matter
with open(file_path, 'w') as file:
    file.write(front_matter)

print(f"Post created: {file_path}")

