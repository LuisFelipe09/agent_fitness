from typing import Optional, List
from sqlalchemy.orm import Session
from src.domain.models import PlanVersion
from src.domain.repositories import PlanVersionRepository
from src.infrastructure.orm_models import PlanVersionORM

class SqlAlchemyPlanVersionRepository(PlanVersionRepository):
    def __init__(self, db: Session):
        self.db = db
    
    def save(self, version: PlanVersion) -> None:
        version_orm = PlanVersionORM(
            id=version.id,
            plan_id=version.plan_id,
            plan_type=version.plan_type,
            version_number=version.version_number,
            created_by=version.created_by,
            created_at=version.created_at,
            changes_summary=version.changes_summary,
            data_snapshot=version.data_snapshot,
            state_at_version=version.state_at_version
        )
        self.db.add(version_orm)
        self.db.commit()
    
    def get_by_plan_id(self, plan_id: str) -> List[PlanVersion]:
        versions_orm = self.db.query(PlanVersionORM).filter(PlanVersionORM.plan_id == plan_id).order_by(PlanVersionORM.version_number.desc()).all()
        return [
            PlanVersion(
                id=v.id,
                plan_id=v.plan_id,
                plan_type=v.plan_type,
                version_number=v.version_number,
                created_by=v.created_by,
                created_at=v.created_at,
                changes_summary=v.changes_summary,
                data_snapshot=v.data_snapshot,
                state_at_version=v.state_at_version
            )
            for v in versions_orm
        ]
    
    def get_by_id(self, version_id: str) -> Optional[PlanVersion]:
        v = self.db.query(PlanVersionORM).filter(PlanVersionORM.id == version_id).first()
        if not v:
            return None
        return PlanVersion(
            id=v.id,
            plan_id=v.plan_id,
            plan_type=v.plan_type,
            version_number=v.version_number,
            created_by=v.created_by,
            created_at=v.created_at,
            changes_summary=v.changes_summary,
            data_snapshot=v.data_snapshot,
            state_at_version=v.state_at_version
        )
