from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class FilterBase(BaseModel):
    name: str
    description: str | None = None
    params: dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True


class FilterCreate(FilterBase):
    pass


class FilterUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    params: dict[str, Any] | None = None
    is_active: bool | None = None


class FilterRead(FilterBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
