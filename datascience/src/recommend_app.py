import argparse

from app.orchestrators import (
    get_batch_recommendations_service,
    get_recommendations_service,
)


def parse_int_list(token):
    """
    Parse a token that can be:
      - a single integer (e.g., '5')
      - a comma-separated list (e.g., '1,2,3')
      - a range (e.g., '10-20')
      - a mixed combo (e.g., '1,2,10-12')
    Returns a list of ints.
    """
    # If called as a type for argparse (nargs='+' case), value may be a single token
    # that contains commas, or not. We'll normalize both.
    parts = token.split(",")
    result = []

    for part in parts:
        part = part.strip()
        if "-" in part:
            start_str, end_str = part.split("-", 1)
            start = int(start_str)
            end = int(end_str)
            if start > end:
                raise argparse.ArgumentTypeError(f"Invalid range '{part}': start > end")
            result.extend(range(start, end + 1))
        else:
            result.append(int(part))
    return result


def build_parser():
    parser = argparse.ArgumentParser(
        description="Get recommendations for farms (single or batch)."
    )

    group = parser.add_mutually_exclusive_group(required=True)

    # Option 1: single farm id
    group.add_argument(
        "--farm-id",
        type=int,
        help="A single farm ID (e.g., --farm-id 123).",
    )

    # Option 2: multiple farm ids
    # Supports: --farm-ids 1 2 3    (space-separated via nargs)
    #           --farm-ids 1,2,3    (comma-separated via custom type)
    #           --farm-ids 1-1000   (range of values)
    #           --farm-ids 5,10,20-25 (mix of comma-separated and range)
    group.add_argument(
        "--farm-ids",
        nargs="+",
        type=parse_int_list,  # allows comma-separated and ranges in each token
        help=(
            "One or more farm IDs. Supports space-/comma-separated and ranges.\n"
            "Examples:\n"
            "  --farm-ids 1 2 3\n"
            "  --farm-ids 1,2,3\n"
            "  --farm-ids 1-1000\n"
            "  --farm-ids 5,10,20-25"
        ),
    )

    return parser


def flatten_farm_ids(nested):
    """
    Argparse with type=parse_int_list and nargs='+' yields a list of lists.
    """
    out = []
    for chunk in nested:
        out.extend(chunk)
    return out


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.farm_id is not None:
        result = get_recommendations_service(args.farm_id)
        print(result)
        return

    # args.farm_ids is a list of lists due to type=parse_int_list with nargs='+'
    farm_ids = flatten_farm_ids(args.farm_ids)

    # De-duplicate and sort for stability
    farm_ids = sorted(set(farm_ids))

    result = get_batch_recommendations_service(farm_ids)
    print(result)


if __name__ == "__main__":
    main()
