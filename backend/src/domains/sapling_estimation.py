from pydantic import BaseModel, ConfigDict


class SaplingEstimation(BaseModel):
    """
    The 'Contract' for the Sapling Estimation logic.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    boundary: str

    @classmethod
    def from_db_model(cls, boundary_obj):
        """
        Adapter method to transform the heavy ORM object into
        the lightweight domain contract.
        """
        return cls(id=boundary_obj.id, boundary=str(boundary_obj.boundary))
