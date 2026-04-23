from pathlib import Path


def main() -> None:
    Path("data/reports").mkdir(parents=True, exist_ok=True)
    print("render_reports placeholder")


if __name__ == "__main__":
    main()
