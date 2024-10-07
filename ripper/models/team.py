from typing import Optional

from pydantic import BaseModel


class Team(BaseModel):
    name: str
    conference: Optional[str] = None
