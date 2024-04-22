import json
from os import sep
import time
from typing import Any, TypedDict
from loguru import logger
from requests import Session, Response, post, get
from enum import Enum
from app.celery.helpers import ReturnTypeFromJsonQuery

from config import config

class APIRoutes:
    LOGIN = "/auth/login"
    FACILITIES_WITH_QUERY = "/facilities?"
    COMPANIES_WITH_QUERY = "/companies?"
    PRIORITIES_WITH_QUERY = "/priorities?"
    WORKFLOWS_WITH_QUERY = "/workflows?"
    SERVICES_WITH_QUERY = "/services?"
    WORK_CATEGORIES_WITH_QUERY = "/work_categories?"
    BUILDINGS_WITH_QUERY = "/buildings?"
    FLOORS_WITH_QUERY = "/floors?"
    ROOMS_WITH_QUERY = "/rooms?"
    USERS_WITH_QUERY = "/users?"
    ARCHIVE_ISSUES_WITH_QUERY = "/issues/archive?"
    ISSUES_STATUSES_WITH_QUERY = "/issue_histories?"
    CURRENT_ISSUES_WITH_QUERY = "/issues"
    TECH_PASSPORT_WITH_ID = "/rooms/form_data?id="


    @classmethod
    def statuses_for_workflows(cls, workflow_id: int):
        return f"/workflows/{workflow_id}/statuses"

class APIGrids(Enum):
    FACILITIES = "facilities"
    COMPANIES = "companies"
    PRIORITIES = "priorities"
    WORKFLOWS = "workflows"
    SERVICES = "services"
    WORK_CATEGORIES = "work_categories"
    BUILDINGS = "buildings"
    FLOORS = "floors"
    ROOMS = "rooms"
    USERS = "users"
    ARCHIVE_ISSUES = "archive"
    ISSUES_STATUSES = "history"
    CURRENT_ISSUES = "issues"



class Pagination(TypedDict):
    per_page: int

class AmeliaApi():

    def __init__(
            self,
            base_url: str = config.API_BASE_URL,
            pagination_per_page:  int = 20,
            timeout: int = 10
        ):

        self.session: Session = Session()
        self.base_url = base_url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Authorization": ""
        }

        self.pagination: Pagination = {
            "per_page": pagination_per_page
        }
        self.timeout = timeout


    def get(self, route: str, params: dict[str, Any] = {}) -> Response | None:
        flag = True
        response = None
        while flag:
            try:
                response = self.session.get(self.base_url + route, params=params, timeout=self.timeout)
                st_code = response.status_code 
                if st_code != 200:
                    logger.error(f"Some error: status code is {st_code}, text: {response.text}")
                    response = None
                elif st_code == 401:
                    logger.error(f"Some error: status code is {st_code}, text: {response.text}")
                    logger.error(response.json(), response.headers, sep="\n\n")
                    time.sleep(20)
                    logger.info("Next try")
                    continue
                flag = False
            except Exception as e:
                    logger.exception("Some error: ", e)
                    time.sleep(1)
                    continue    
        return response    
            
    
    def create_json_for_request(self, grid: APIGrids, page: int=1, issue_id: int=0, service_id=None) -> dict[str, Any]:
        data: dict[str, Any] = {}
        if grid == APIGrids.WORKFLOWS:
            data = {
                "json" : json.dumps({
                    "sortBy":"id",
                    "descending": True,
                    "page": page,
                    "rowsPerPage": 0,
                    "rowsNumber": 0,
                    "query": "",
                    "filters": {},
                    "except_filters": {},
                    "grid": grid.value
                })
            }
        elif grid == APIGrids.ISSUES_STATUSES:
            data = {
                "json" : json.dumps({
                    "table":{
                        "sortBy":"id",
                        "descending": True,
                        "page": page,
                        "rowsPerPage": 0,
                        "rowsNumber": 0,
                        "query": "",
                        "filters": {
                            "issue_id": issue_id,
                            "text": "Статус изменен"
                        },
                        "except_filters": {},
                        "grid": grid.value
                    }
                })
            }
        elif grid == APIGrids.ARCHIVE_ISSUES:
            data = {
                "json" : json.dumps({
                    "table":{
                        "sortBy":"id",
                        "descending": True,
                        "page": page,
                        "rowsPerPage": 0,
                        "rowsNumber": 0,
                        "query": "",
                        "filters": {
                            "type":"MaintenanceIssue",
                            "service_id": service_id},
                        "except_filters": {},
                        "grid": grid.value
                    }
                })
            }
        elif grid == APIGrids.CURRENT_ISSUES:
            data = {
                "json" : json.dumps({
                    "table":{
                        "sortBy":"id",
                        "descending": True,
                        "page": page,
                        "rowsPerPage": 0,
                        "rowsNumber": 0,
                        "query": "",
                        "filters": {
                            "type":"MaintenanceIssue",
                            "service_id": service_id
                            },
                        "except_filters": {},
                        "grid": grid.value
                    }
                })
            }
        elif grid == APIGrids.USERS: 
            data = {
                "json" : json.dumps({
                    "table":{
                        "sortBy":"id",
                        "descending": True,
                        "page": page,
                        "rowsPerPage": 0,
                        "rowsNumber": 0,
                        "query": "",
                        "filters": {
                        },
                        "except_filters": {
                        },
                        "grid": grid.value
                    }
                })
            }
        else: 
            data = {
                "json" : json.dumps({
                    "table":{
                        "sortBy":"id",
                        "descending": True,
                        "page": page,
                        "rowsPerPage": 0,
                        "rowsNumber": 0,
                        "query": "",
                        "filters": {},
                        "except_filters": {},
                        "grid": grid.value
                    }
                })
            }

        return data

    
    def auth(self) -> int:
        flag = True
        while flag:
            try:
                response = post(
                    url=self.base_url+APIRoutes.LOGIN,
                    headers=self.headers,
                    json={
                        "user": {
                            "email": config.API_USER,
                            "password": config.API_USER_PASSWORD
                        }
                    },
                    timeout=self.timeout
                )
                if response.status_code != 200:
                    return 1
                else:
                    flag = False
                    self.headers["Authorization"] = f"Bearer {response.json()['token']}"
                    self.session.headers.update(self.headers)
            except Exception as e:
                print("Some error: ", e)
                time.sleep(1)
                continue
        return 0

    def get_pagination(self) -> Pagination:
        return self.pagination
    
    def get_count_of_pages(self, data: ReturnTypeFromJsonQuery):
        count_objects: int = data.count

        if count_objects == 0:
            return 1
        pages: int = count_objects // self.get_pagination()["per_page"] + 2
        return pages