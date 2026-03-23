import argparse
from lib.rag import rag, rag_summarize


def main():
    parser = argparse.ArgumentParser(
        description="Retrieval Augmented Generation CLI")
    subparsers = parser.add_subparsers(
        dest="command", help="Available commands")

    rag_parser = subparsers.add_parser(
        "rag", help="Perform RAG (search + generate answer)"
    )
    rag_parser.add_argument("query", type=str, help="Search query for RAG")
    summary_parser = subparsers.add_parser(
        "summarize", help="For summarizing llm search results")
    summary_parser.add_argument(
        "query", type=str, help="enter your search query to summarize")
    summary_parser.add_argument(
        "--limit", type=int, default=5, help="search limits")
    args = parser.parse_args()

    match args.command:
        case "rag":
            query = args.query
            rag(query=query)
        case "summarize":
            rag_summarize(args.query, args.limit)

        case _:
            parser.print_help()


if __name__ == "__main__":
    main()
