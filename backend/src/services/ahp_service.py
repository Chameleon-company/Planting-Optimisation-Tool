from ahp.ahp_core import AhpCore
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.parameters import Parameter
from src.services.species import get_recommend_config


class AhpService:
    def __init__(self):
        # Instantiate the core math logic when the service is created
        self.ahp_core = AhpCore()

    async def calculate_and_save_ahp_weights(self, db: AsyncSession, matrix: list[list[float]], species_id: int):
        """Calculate, validate, and conditionally persist AHP weights.

        Args:
            db: Async database session used to read and write parameters.
            matrix: Pairwise comparison matrix used to compute AHP weights.
            species_id: Identifier of the species whose parameters are updated.

        Returns:
            dict[str, object]: Result payload containing computed weights,
            consistency ratio, consistency status, and a status message.

        Raises:
            ValueError: If no features are configured or matrix size does not
                match the configured feature count.
        """
        # Fetch features from YAML Config
        cfg = get_recommend_config()

        # Pull the 'features' dictionary out of the YAML
        raw_features = cfg.get("features", {})

        if not raw_features:
            raise ValueError("No features found in recommend.yaml configuration.")

        # Extract just the top-level keys as a list of strings
        # This will be: ["rainfall_mm", "temperature_celsius", "elevation_m", "ph", "soil_texture"]
        features = list(raw_features.keys())

        # Validate Matrix Size
        n = len(matrix)
        if n != len(features):
            raise ValueError(f"Matrix size {n} does not match {len(features)} features.")

        # Calculate using AHP Core Logic
        result = self.ahp_core.calculate_weights(matrix)

        # Map raw array to factor names
        weights_dict = dict(zip(features, result["weights"]))

        # Save to DB if consistent
        if result["is_consistent"]:
            # Fetch all existing parameters for this species_id in ONE query
            stmt = select(Parameter).where(Parameter.species_id == species_id)
            db_result = await db.execute(stmt)
            existing_parameters = db_result.scalars().all()

            # Create a dictionary of existing parameters keyed by feature name for easy lookup
            existing_param_dict = {param.feature: param for param in existing_parameters}

            # Loop through our newly calculated weights
            for feature_name, weight_val in weights_dict.items():
                if feature_name in existing_param_dict:
                    # If it exists, update the weight (SQLAlchemy tracks this change)
                    existing_param_dict[feature_name].weight = weight_val
                else:
                    # If it doesn't exist, create a new record
                    # score_method, trap_left_tol, and trap_right_tol will naturally default to None
                    new_param = Parameter(species_id=species_id, feature=feature_name, weight=weight_val)
                    db.add(new_param)

            # Commit all changes (inserts and updates) together
            await db.commit()
            msg = "Success"
        else:
            msg = "Inconsistent Judgments - Not Saved"

        # Return results
        return {"weights": weights_dict, "consistency_ratio": result["consistency_ratio"], "is_consistent": result["is_consistent"], "message": msg}
