# INF601 - Advanced Programming in Python
# Adeola Ajayi
# Scheduled Check-In Bot

"""
Scheduled Check-In Bot
=======================
Runs on a GitHub Actions schedule. Talks to the Practice Hub REST API and:

  Task 1: Collects every post from the instructor (title, body, tags,
          timestamps, and every attached file) into artifact/collected.json
          and artifact/files/.

  Task 2: Finds the instructor's "check-in" posts (title contains the
          words "check-in", possibly with other text around it) and
          replies to each one with a comment, once, within its open
          reply window.
"""

import json
import os
from pathlib import Path

import requests

# ---------------------------------------------------------------------------
# Configuration (read from environment -- set as GitHub Actions secrets/vars)
# ---------------------------------------------------------------------------

PRACTICE_API_TOKEN = os.environ.get("PRACTICE_API_TOKEN")
PRACTICE_API_URL = os.environ.get("PRACTICE_API_URL")
INSTRUCTOR_ID = os.environ.get("INSTRUCTOR_ID")

if not PRACTICE_API_TOKEN:
    raise ValueError("PRACTICE_API_TOKEN is not set.")

if not PRACTICE_API_URL:
    raise ValueError("PRACTICE_API_URL is not set.")

if not INSTRUCTOR_ID:
    raise ValueError("INSTRUCTOR_ID is not set.")

# ---------------------------------------------------------------------------
# Practice Hub API client
# ---------------------------------------------------------------------------

class PracticeHubClient:
    def __init__(self, base_url, token):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {token}"
        }

    def get_posts_page(self, author=None, limit=100, offset=0):
        params = {
            "limit": limit,
            "offset": offset
        }

        if author is not None:
            params["author"] = author

        response = requests.get(
            f"{self.base_url}/api/v1/posts",
            headers=self.headers,
            params=params,
            timeout=30
        )


        response.raise_for_status()
        return response.json()



    def get_me(self):
        response = requests.get(
            f"{self.base_url}/api/v1/me",
            headers=self.headers,
            timeout=30
        )

        response.raise_for_status()
        return response.json()


    def get_comments(self, post_id):
        response = requests.get(
            f"{self.base_url}/api/v1/posts/{post_id}/comments",
            headers=self.headers,
            timeout=30
        )

        response.raise_for_status()
        return response.json()

    def post_comment(self, post_id, body):
       response = requests.post(
           f"{self.base_url}/api/v1/posts/{post_id}/comments",
           headers=self.headers,
           json={"body": body},
           timeout=30
    )

       return response
    

    def has_already_replied(self, post_id, my_user_id):
        comments = self.get_comments(post_id)

        for comment in comments:
            if str(comment.get("author_id")) == str(my_user_id):
                return True

        return False


    def is_checkin_post(self, post):
        title = post.get("title", "")
        return "check-in" in title.lower()


    def process_checkins(self, posts, my_user_id):
        for post in posts:
            if not self.is_checkin_post(post):
                continue

            post_id = post.get("id")
            title = post.get("title", "")

            if self.has_already_replied(post_id, my_user_id):
                print(f"Already replied to check-in: {title}")
                continue

            response = self.post_comment(
                post_id,
                "Checking in!"
            )

            if response.status_code == 201:
                print(f"Successfully replied to check-in: {title}")
            elif response.status_code == 423:
                print(f"Check-in window is closed or unavailable: {title}")
            else:
                print(
                    f"Could not reply to check-in: {title} "
                    f"(status {response.status_code})"
                )

    def get_all_posts(self):
        all_posts = []
        offset = 0

        while True:
            posts = self.get_posts_page(offset=offset)

            if not posts:
                break

            all_posts.extend(posts)
            offset += len(posts)

        return all_posts

    def get_instructor_posts(self, instructor_id):
        instructor_posts = []
        offset = 0

        while True:
           posts = self.get_posts_page(
               author=instructor_id,
               limit=100,
               offset=offset
         )

           if not posts:
              break

           instructor_posts.extend(posts)
           offset += len(posts)

        return instructor_posts


    def save_posts(self, posts):
        artifact_dir = Path("artifact")
        artifact_dir.mkdir(exist_ok=True)

        files_dir = artifact_dir / "files"
        files_dir.mkdir(exist_ok=True)

        output_file = artifact_dir / "collected.json"

        with output_file.open("w", encoding="utf-8") as file:
            json.dump(posts, file, indent=2)

        print(f"Saved {len(posts)} posts to {output_file}")


    def download_attachments(self, posts):
        files_dir = Path("artifact") / "files"
        files_dir.mkdir(parents=True, exist_ok=True)

        for post in posts:
            post_id = post.get("id")
            attachments = post.get("attachments", [])

            for attachment in attachments:
                attachment_id = attachment.get("id")
                filename = attachment.get("filename")
                download_url = attachment.get("download_url")

                if not download_url:
                    continue

                safe_filename = f"{post_id}_{attachment_id}_{filename}"
                file_path = files_dir / safe_filename

                response = requests.get(
                    download_url,
                    headers=self.headers,
                    timeout=30
            )

                response.raise_for_status()

                with file_path.open("wb") as file:
                    file.write(response.content)

                print(f"Downloaded attachment: {file_path}")


if __name__ == "__main__":
    client = PracticeHubClient(
        PRACTICE_API_URL,
        PRACTICE_API_TOKEN
    )

    me = client.get_me()
    my_user_id = me.get("id")

    posts = client.get_instructor_posts(INSTRUCTOR_ID)

    print("Instructor ID:", INSTRUCTOR_ID)
    print("Number of instructor posts returned:", len(posts))

    for post in posts:
        print(post.get("id"), "-", post.get("title"))

    client.save_posts(posts)
    client.download_attachments(posts)
    client.process_checkins(posts, my_user_id)