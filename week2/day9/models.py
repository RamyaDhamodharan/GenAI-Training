from pydantic import BaseModel


class Medication(BaseModel):
    name: str
    dose: str | None = None