from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from app.services.cache import get_revenue_summary
from app.core.auth import authenticate_request as get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database_pool import get_db_session

router = APIRouter()

@router.get("/dashboard/summary")
async def get_dashboard_summary(
    property_id: str,
    month: int = None,
    year: int = None,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    
    tenant_id = getattr(current_user, "tenant_id", "default_tenant") or "default_tenant"
    
    revenue_data = await get_revenue_summary(property_id, tenant_id, month, year)
    
    total_revenue_float = round(float(revenue_data['total']), 2)
    
    return {
        "property_id": revenue_data['property_id'],
        "total_revenue": total_revenue_float,
        "currency": revenue_data['currency'],
        "reservations_count": revenue_data['count']
    }

@router.get("/dashboard/properties")
async def get_dashboard_properties(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> List[Dict[str, Any]]:
    
    tenant_id = getattr(current_user, "tenant_id", "default_tenant") or "default_tenant"
    
    query = text("""
        SELECT id, name
        FROM properties
        WHERE tenant_id = :tenant_id
        ORDER BY name ASC
    """)
    
    result = await db.execute(query, {"tenant_id": tenant_id})
    properties = [{"id": row.id, "name": row.name} for row in result.fetchall()]
    
    return properties
