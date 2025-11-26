from datetime import datetime
import json
from dataclasses import asdict
from typing import List, Optional
from src.domain.models import PlanVersion, WorkoutPlan, NutritionPlan
from src.domain.repositories import PlanVersionRepository

class VersionService:
    def __init__(self, version_repo: PlanVersionRepository):
        self.version_repo = version_repo
    
    def create_version(self, plan, changed_by: str, summary: str) -> PlanVersion:
        """Create a new version snapshot of a plan"""
        # Determine plan type
        plan_type = "workout" if isinstance(plan, WorkoutPlan) else "nutrition"
        
        # Get current versions to determine next number
        existing_versions = self.version_repo.get_by_plan_id(plan.id)
        next_version_number = 1
        if existing_versions:
            next_version_number = max(v.version_number for v in existing_versions) + 1
        
        # Create snapshot
        # We use asdict to serialize the plan, but we need to handle datetime objects
        # For simplicity in this MVP, we'll assume the JSON serializer in ORM handles it
        # or we convert to string here.
        # Let's use a helper to serialize properly
        snapshot = self._serialize_plan(plan)
        
        version = PlanVersion(
            id=f"{plan.id}_v{next_version_number}",
            plan_id=plan.id,
            plan_type=plan_type,
            version_number=next_version_number,
            created_by=changed_by,
            created_at=datetime.now(),
            changes_summary=summary,
            data_snapshot=snapshot,
            state_at_version=plan.state
        )
        
        self.version_repo.save(version)
        return version
    
    def get_history(self, plan_id: str) -> List[PlanVersion]:
        """Get version history for a plan"""
        return self.version_repo.get_by_plan_id(plan_id)
    
    def _serialize_plan(self, plan) -> dict:
        """Helper to serialize plan to dict with datetime handling"""
        data = asdict(plan)
        
        # Convert datetimes to isoformat strings
        if 'start_date' in data and data['start_date']:
            data['start_date'] = data['start_date'].isoformat()
        if 'end_date' in data and data['end_date']:
            data['end_date'] = data['end_date'].isoformat()
        if 'created_at' in data and data['created_at']:
            data['created_at'] = data['created_at'].isoformat()
        if 'modified_at' in data and data['modified_at']:
            data['modified_at'] = data['modified_at'].isoformat()
            
        return data
