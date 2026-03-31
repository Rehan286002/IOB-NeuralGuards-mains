from pydantic import BaseModel, PositiveFloat, field_validator
from typing import Optional
from datetime import datetime

class Transaction(BaseModel):
    txn_id: str
    sender_upi: str
    receiver_upi: str
    amount: PositiveFloat
    timestamp: datetime
    channel: str
    audio_ref: Optional[str] = None

    @field_validator('channel')
    @classmethod
    def validate_channel(cls, v: str) -> str:
        allowed = {'UPI', 'VOICE_123PAY'}
        if v not in allowed:
            raise ValueError(f'Channel must be one of {allowed}')
        return v
