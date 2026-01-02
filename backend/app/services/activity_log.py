from typing import List, Optional
from datetime import datetime
from beanie import PydanticObjectId
from app.models.activity_log import ActivityLog, LogType

class ActivityLogService:
    @staticmethod
    async def create_log(
        action: str,
        message: str,
        userId: Optional[str] = None,
        homeId: Optional[str] = None,
        log_type: str = LogType.INFO
    ) -> ActivityLog:
        """Tạo activity log"""
        log = ActivityLog(
            action=action,
            message=message,
            userId=PydanticObjectId(userId) if userId else None,
            homeId=PydanticObjectId(homeId) if homeId else None,
            type=log_type,
            timestamp=datetime.utcnow()
        )
        await log.create()
        return log

    @staticmethod
    async def get_logs_by_user(userId: str, limit: int = 50) -> List[ActivityLog]:
        """Lấy logs của user"""
        logs = await ActivityLog.find(
            ActivityLog.userId == PydanticObjectId(userId)
        ).sort(-ActivityLog.timestamp).limit(limit).to_list()
        return logs

    @staticmethod
    async def get_logs_by_home(homeId: str, limit: int = 50) -> List[ActivityLog]:
        """Lấy logs theo home"""
        logs = await ActivityLog.find(
            ActivityLog.homeId == PydanticObjectId(homeId)
        ).sort(-ActivityLog.timestamp).limit(limit).to_list()
        return logs

    @staticmethod
    async def get_all_logs(limit: int = 100) -> List[ActivityLog]:
        """Lấy tất cả logs"""
        logs = await ActivityLog.find().sort(-ActivityLog.timestamp).limit(limit).to_list()
        return logs
