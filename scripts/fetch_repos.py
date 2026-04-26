import json
import subprocess
import sys
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
REPOS_JSON_PATH = RAW_DATA_DIR / "repos.json"


def main() -> None:
    """Fetches all repositories for a GitHub user and saves them to a JSON file."""
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    print("Fetching repositories for user 'qiao-925'...")

    try:
        # Using gh cli to fetch all repos, including private, forks, and archived
        command = [
            "gh", "repo", "list", "qiao-925",
            "--limit", "500",
            "--json", "name,isPrivate,isFork,isArchived,isTemplate,createdAt,updatedAt,pushedAt,primaryLanguage,description,stargazerCount,forkCount,diskUsage,repositoryTopics,parent,homepageUrl,licenseInfo"
        ]

        result = subprocess.run(command, capture_output=True, text=True, check=True)
        repos_data = json.loads(result.stdout)

        with open(REPOS_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(repos_data, f, indent=2, ensure_ascii=False)

        print(f"Successfully fetched {len(repos_data)} repositories.")
        print(f"Data saved to {REPOS_JSON_PATH}")

    except FileNotFoundError:
        print("Error: 'gh' command not found. Please ensure the GitHub CLI is installed and in your PATH.")
        raise SystemExit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error executing 'gh' command: {e}")
        print(f"Stderr: {e.stderr}")
        raise SystemExit(1)
    except json.JSONDecodeError:
        print("Error: Failed to parse JSON from 'gh' command output.")
        raise SystemExit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
