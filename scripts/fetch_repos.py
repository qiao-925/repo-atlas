from pathlib import Path


def main() -> None:
    Path("data/raw").mkdir(parents=True, exist_ok=True)
    print("fetch_repos placeholder")


if __name__ == "__main__":
    main()
