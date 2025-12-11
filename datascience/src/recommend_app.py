from suitability_scoring.recommend import build_payloads_for_farms


def main():
    """ """
    farm_ids = list(range(1, 1001))
    output = build_payloads_for_farms(farm_ids)
    print(output)


if __name__ == "__main__":
    main()
