# Scheduled Check-In Bot

This project is a Python-based scheduled check-in bot for the INF601 Practice Hub API. The bot collects posts created by the instructor, saves the collected post data and attachments, identifies instructor posts containing "check-in" in the title, and automatically replies to eligible check-in posts.

The project uses GitHub Actions to run the bot automatically on a schedule. It also supports manual workflow runs through GitHub Actions.

## Installation

Clone the repository and install the required Python dependencies:

```bash
pip install -r requirements.txt
```

## How to Run

Set the required environment variables before running the program:

```bash
export PRACTICE_API_TOKEN="your_token_here"
export PRACTICE_API_URL="https://practice.fhsucyber.com"
export INSTRUCTOR_ID="7"
```

Run the bot with:

```bash
python3 checkin_bot.py
```

The API token should be kept private and should not be committed to the repository.

## GitHub Actions

The bot is configured to run automatically using GitHub Actions. The workflow is located in `.github/workflows/checkinbot.yml`.

The workflow can also be started manually using the **Run workflow** option in the GitHub Actions tab.

The workflow uses the following GitHub repository secrets and variable:

- `PRACTICE_API_TOKEN` - repository secret containing the Practice Hub API token.
- `PRACTICE_API_URL` - repository secret containing the Practice Hub API URL.
- `INSTRUCTOR_ID` - repository variable containing the instructor's user ID.

After each run, the collected data is saved in the `artifact/` directory and uploaded as a GitHub Actions artifact. If the collected artifact has changed, the workflow also commits the updated artifact/ directory back to the repository.

## Check-In Handling

The bot identifies instructor posts that contain "check-in" in the title. Before replying, it checks the existing comments to determine whether I have already responded.

If a reply already exists from my account, the bot skips the post to prevent duplicate replies. If the API returns a 423 status because the check-in reply window is closed, the bot handles the response without crashing.

## AI Usage

I used Claude Code to help explain the assignment requirements, understand the Practice Hub API documentation, provide guidance on Python and GitHub Actions, and troubleshoot errors encountered while developing the project.

I created the project files, configured the repository, tested the API requests, reviewed the program output, configured the GitHub repository secrets and variable, and manually tested the GitHub Actions workflow. I reviewed and tested the code to make sure I understood how it works.

I modified the suggested code while developing the project, including changing the API pagination to use `limit` and `offset`, filtering posts using the instructor ID, saving collected posts and attachments in the `artifact/` directory, adding duplicate-reply protection, handling the 423 response for closed check-in windows, and configuring the scheduled GitHub Actions workflow.

I can explain the Python code and GitHub Actions workflow used in this project.
