import json
import redis.asyncio as redis
from typing import Dict, Any
import os
import logging

# Initialize Redis client (typically configured centrally).
redis_client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))

logger = logging.getLogger(__name__)

async def get_revenue_summary(property_id: str, tenant_id: str, month: int, year: int) -> Dict[str, Any]:
    """
    Fetches monthly revenue summary, utilizing caching and timezone awareness.
    """
    # 1. Get property timezone
    tz_cache_key = f"property_tz:{tenant_id}:{property_id}"
    timezone_str_bytes = await redis_client.get(tz_cache_key)
    
    if timezone_str_bytes:
        timezone_str = timezone_str_bytes.decode('utf-8')
    else:
        from app.services.reservations import get_property_timezone
        timezone_str = await get_property_timezone(property_id, tenant_id)
        await redis_client.setex(tz_cache_key, 86400, timezone_str)
        
    # 2. Resolve month and year using property timezone
    import zoneinfo
    from datetime import datetime
    tz = zoneinfo.ZoneInfo(timezone_str)
    
    if month is None or year is None:
        now = datetime.now(tz)
        month = now.month
        year = now.year

    cache_key = f"revenue_monthly:{tenant_id}:{property_id}:{year}:{month}"
    
    # Try to get from cache
    cached = await redis_client.get(cache_key)
    if cached:
        logger.info(f"Monthly revenue summary found in cache for cache_key: {cache_key}")
        result = json.loads(cached)
        result["month"] = month
        result["year"] = year
        return result
    
    from app.services.reservations import calculate_monthly_revenue
    result = await calculate_monthly_revenue(property_id, tenant_id, month, year, timezone_str)
    
    logger.info(f"Monthly revenue summary calculated for cache_key: {cache_key}, result: {result}")
    await redis_client.setex(cache_key, 300, json.dumps(result))
    
    result["month"] = month
    result["year"] = year
    return result
