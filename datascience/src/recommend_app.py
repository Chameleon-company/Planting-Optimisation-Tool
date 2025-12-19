from suitability_scoring.recommend import (
    get_batch_recommendations_service,
    get_recommendations_service,
)


def main():
    """ """
    farm_ids = list(range(1, 1001))
    result = get_batch_recommendations_service(farm_ids)
    result = get_recommendations_service(1)
    print(result)


if __name__ == "__main__":
    main()
