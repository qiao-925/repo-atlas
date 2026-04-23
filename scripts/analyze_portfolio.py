from pathlib import Path


def main() -> None:
    Path("data/derived").mkdir(parents=True, exist_ok=True)
    print("analyze_portfolio placeholder")


if __name__ == "__main__":
    main()
