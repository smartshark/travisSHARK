from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Optional
from mongoengine import ObjectIdField


@dataclass
class TravisBuild:
    tr_id: int
    ci_system_ids: List[int]
    project: str
    commit_id: str
    number: int
    state: str
    event_type: str
    duration: Optional[int] = None
    pr_number: Optional[int] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    stages: List[str] = field(default_factory=list)


@dataclass
class TravisJob:
    tr_id: int
    build_id: ObjectIdField
    allow_failure: bool
    number: str
    state: str
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    stages: List[str] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)
    config: dict = field(default_factory=dict)
    job_log: Optional[str] = None
