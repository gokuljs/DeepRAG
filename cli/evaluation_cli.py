import argparse
from lib.evaluation import evaluate
def main():
    parser = argparse.ArgumentParser(description="Search Evaluation CLI")
    parser.add_argument(
        "command",
        choices=["evaluate"],
        help="Command to run",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=3,
        help="Number of results to evaluate (k for precision@k, recall@k)",
    )

    args = parser.parse_args()
    limit = args.limit

    match args.command:
        case "evaluate":
            evaluate(limit)
        case _:
            print("Invalid command")

if __name__ == "__main__":

    main()