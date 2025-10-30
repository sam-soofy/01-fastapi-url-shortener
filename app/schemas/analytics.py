from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel, ConfigDict


class AnalyticsSummary(BaseModel):
    total_clicks: int
    clicks_in_range: int
    unique_visitors: int
    date_range_days: int
    device_breakdown: Dict[str, int]  # device_type: count
    browser_breakdown: Dict[str, int]  # browser: count
    top_referrers: Dict[str, int]  # referrer: count
    daily_clicks: Dict[str, int]  # date: count

    model_config = ConfigDict(from_attributes=True)


class URLClickResponse(BaseModel):
    id: int
    clicked_at: datetime
    ip_address: Optional[str] = None
    referrer: Optional[str] = None
    device_type: Optional[str] = None
    browser: Optional[str] = None
    country: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
