#!/usr/bin/env python
"""
Simple entry point to run the Amazon Product Analysis tool.
"""

import sys
from langchain_app.main import run_analysis, print_results
from argparse import ArgumentParser


def main():
    """Run the main application."""
    if len(sys.argv) < 2:
        print(
            "Usage: python run_analysis.py <amazon_url> [--max-products N] [--max-competitive N]"
        )
        print(
            "Example: python run_analysis.py https://www.amazon.com/dp/B08B9H2ZYT --max-products 5 --max-competitive 3"
        )
        return 1

    # Set up command line argument parsing
    parser = ArgumentParser(description="Amazon Product Analysis Tool")
    parser.add_argument("url", help="Amazon product URL to analyze")
    parser.add_argument(
        "-m",
        "--max-products",
        type=int,
        default=10,
        help="Maximum number of products to collect (default: 10)",
    )
    parser.add_argument(
        "-c",
        "--max-competitive",
        type=int,
        default=5,
        help="Maximum number of competitive products to analyze (default: 5)",
    )

    args = parser.parse_args()

    try:
        # Run the analysis
        print(f"Analyzing Amazon product: {args.url}")
        print(
            f"Max products: {args.max_products}, Max competitive products: {args.max_competitive}"
        )

        final_state = run_analysis(
            args.url,
            max_products=args.max_products,
            max_competitive=args.max_competitive,
        )

        print(final_state["supervisor"].keys())

        print_results(final_state["supervisor"])
        return 0
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
