import argparse

from suitability_scoring.recommend import (
    get_batch_recommendations_service,
    get_recommendations_service,
)


def parse_int_list(value):
    """
    Accepts either a comma-separated list ("1,2,3") or a single int-like string,
    or space-separated via nargs in argparse. Returns a list of ints.
    """
    # If called as a type for argparse (nargs='+' case), value may be a single token
    # that contains commas, or not. We'll normalize both.
    parts = []
    if isinstance(value, list):
        # Shouldn't happen when used as type; but keep defensive
        for v in value:
            parts.extend(str(v).split(","))
    else:
        parts = str(value).split(",")

    try:
        ints = [int(v.strip()) for v in parts if v.strip() != ""]
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"Invalid integer in list: {e}")
    if not ints:
        raise argparse.ArgumentTypeError("No valid farm IDs provided.")
    return ints


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
    group.add_argument(
        "--farm-ids",
        nargs="+",
        type=parse_int_list,  # allows comma-separated in each token
        help="One or more farm IDs (space- or comma-separated). Example: --farm-ids 1 2 3 OR --farm-ids 1,2,3",
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
