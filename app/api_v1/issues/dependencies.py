from datetime import datetime
from typing import Annotated

from fastapi import Depends, Query

from app.schemas.issue_schemas import (CreationTime, IssuesFiltersSchema,
                                       Pagination, Place, TransitionStatuses,
                                       Work, end_date, start_date)

datetime_regex = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"

def  filters_dep(
    transition_start_date: datetime = Query(
        start_date(), example="2024-09-10T00:00:00", alias="transitionStartDate"
    ),
    transition_end_date: datetime = Query(
        end_date(), example="2024-09-30T00:00:00", alias="transitionEndDate"
    ),
    transition_statuses: list[str] = Query(
        [], example=["взята в работу", "новая"], alias="transitionStatuses"
    ),
    place_buildings_id: list[int] = Query(
        [], alias="placeBuildingsId"
    ),
    creation_start_date: datetime = Query(
        start_date(), example="2024-08-05T00:00:00", alias="creationStartDate"
    ),
    creation_end_date: datetime = Query(
        end_date(), example="2024-09-05T00:00:00", alias="creationEndDate"
    ),
    work_services_id: list[int] = Query(
        [], example=[7, 10], alias="workServicesId",
    ),
    work_work_categories_id: list[int] = Query(
        [], example=[200, 399], alias="workWorkCategoriesId"
    ),
    priorities_id: list[int] = Query(
        [], example=[1, 2], alias="prioritiesId"
    ),
    pagination_limit: int = Query(
        50, example=50, alias="paginationLimit"
    ),
    pagination_ofset: int = Query(
        0, example=0, alias="paginationOfset"
    ),
):
    return IssuesFiltersSchema(
         transition=TransitionStatuses(
            start_date=transition_start_date,
            end_date=transition_end_date,
            statuses=transition_statuses
        ),
        place=Place(
            buildings_id=place_buildings_id,
            rooms_id=[]
        ),
        creation=CreationTime(
            start_date=creation_start_date,
            end_date=creation_end_date
        ),
        work=Work(
            services_id=work_services_id,
            work_categories_id=work_work_categories_id
        ),
        priorities_id=priorities_id,
        pagination=Pagination(
            limit=pagination_limit,
            ofset=pagination_ofset
        )
    )

FiltersDep = Annotated[
    IssuesFiltersSchema,
    Depends(filters_dep)
]