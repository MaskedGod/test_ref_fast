from pydantic import BaseModel
from datetime import datetime


class ReferralCodeResponse(BaseModel):
    code: str
    expiry_date: datetime
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ReferralResponse(BaseModel):
    referee_email: str
    created_at: datetime

    class Config:
        from_attributes = True
