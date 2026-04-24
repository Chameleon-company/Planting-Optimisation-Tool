from pydantic import BaseModel, ConfigDict


class AgroforestryTypeRead(BaseModel):
    id: int
    type_name: str

    model_config = ConfigDict(from_attributes=True)
