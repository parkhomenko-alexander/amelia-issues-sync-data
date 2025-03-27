from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class IssueFilterDTO:
    start_date: datetime
    end_date: datetime
    transition_start_date: datetime
    transition_end_date: datetime
    transition_statuses: list[str] | None
    buildings_id: list[int] | None
    services_id: list[int] | None
    works_category_id: list[int] | None
    rooms_id: list[int] | None
    priorities_id: list[int] | None
    urgencies: list[str] | None
    current_statuses: list[str] | None
    limit: int
    offset: int
