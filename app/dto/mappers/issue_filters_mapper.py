from app.dto.issues_filter_dto import IssueFilterDTO
from app.schemas.issue_schemas import IssuesFiltersSchema


def map_filters_to_dto(filters: IssuesFiltersSchema) -> IssueFilterDTO:
    return IssueFilterDTO(
        start_date=filters.creation.start_date,
        end_date=filters.creation.end_date,
        transition_start_date=filters.transition.start_date,
        transition_end_date=filters.transition.end_date,
        transition_statuses=filters.transition.statuses,
        buildings_id=filters.place.buildings_id,
        services_id=filters.work.services_id,
        works_category_id=filters.work.work_categories_id,
        rooms_id=filters.place.rooms_id,
        priorities_id=filters.priorities_id,
        urgencies=filters.urgency,
        current_statuses=filters.current_statuses,
        limit=filters.pagination.limit,
        offset=filters.pagination.offset
    )