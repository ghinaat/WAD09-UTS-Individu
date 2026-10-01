from pydantic import BaseModel, Field


class SessionBase(BaseModel):
    route_name: str = Field(..., min_length=3, max_length=120)
    driver_name: str = Field(..., min_length=2, max_length=80)
    departure_time: str = Field(..., min_length=4, max_length=20)
    passenger_name: str = Field(..., min_length=2, max_length=80)
    destination: str = Field(..., min_length=2, max_length=120)
    seat_count: int = Field(..., ge=1, le=20)
    status: str = Field(default="scheduled", min_length=3, max_length=20)


class SessionCreate(SessionBase):
    pass


class SessionOut(SessionBase):
    id: int
