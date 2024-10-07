from typing import Optional

from pydantic import BaseModel, Field, field_validator


class Score(BaseModel):
    home: int = Field(default=0)
    away: int = Field(default=0)

    @field_validator("home", "away", mode="before")
    def convert_to_int(cls, value):
        if isinstance(value, str):
            # If value is an empty string, return 0
            if value == "":
                return 0
            # Otherwise, try to convert it to an integer
            return int(value)
        elif isinstance(value, int):
            return value
        else:
            raise ValueError(f"Invalid value: {value}")

