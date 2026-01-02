from typing import List
from fastapi import APIRouter, Depends
from app.api import deps
from app.models.user import User
from app.services.activity_log import ActivityLogService
from app.services.home import HomeService

router = APIRouter()

@router.get("/", response_model=List[dict])
async def get_activity_logs(
    homeId: str,
    limit: int = 50,
    current_user: User = Depends(deps.get_current_user)
):
    """Lấy activity logs theo homeId"""
    # Kiểm tra user có quyền xem home này không
    home = await HomeService.get_home_by_id(homeId, current_user)
    if not home:
        return []
    
    logs = await ActivityLogService.get_logs_by_home(homeId, limit)
    
    # Convert sang dict để trả về
    return [
        {
            "id": str(log.id),
            "homeId": str(log.homeId) if log.homeId else None,
            "userId": str(log.userId) if log.userId else None,
            "type": log.type,
            "action": log.action,
            "message": log.message,
            "timestamp": log.timestamp.isoformat()
        }
        for log in logs
    ]
