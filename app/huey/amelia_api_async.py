import asyncio
import json
from datetime import date, datetime, timedelta
from enum import Enum
from time import sleep
from typing import Any, TypedDict
from urllib.parse import urlencode

from httpx import Response, TimeoutException, TimeoutException, ConnectError
import httpx
from loguru import logger

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
    USERS = "/users"
    ARCHIVE_ISSUES_WITH_QUERY = "/issues/archive?"
    ISSUES_STATUSES_WITH_QUERY = "/issue_histories?"
    CURRENT_ISSUES_WITH_QUERY = "/issues"
    TECH_PASSPORT_WITH_ID = "/rooms/form_data?id="
    
    DYNAMIC_ISSUES = "/dynamic/issues?"
    ISSUE = "/issues"


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
    DYNAMIC_ISSUES = "dynamic_issues"



class Pagination(TypedDict):
    per_page: int

class Borders(TypedDict):
    start: int
    end: int

class AmeliaApiAsync():

        def __init__(
                self,
                base_url: str = config.API_BASE_URL,
                pagination_per_page:  int = 20,
                timeout: int = 100
            ):

            self.session = httpx.AsyncClient(timeout=timeout)
            self.base_url = base_url
            self.headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                "Authorization": ""
            }

            self.pagination: Pagination = {
                "per_page": pagination_per_page
            }
            self.timeout = timeout
        
        def encode_params(self, params: dict):
            """
            Encodes the parameters to make sure array-like parameters are properly formatted.
            """
            # Ensure the lists are encoded as comma-separated values
            for key, value in params.items():
                if isinstance(value, list):
                    params[key] = ','.join(map(str, value))
            return urlencode(params)
        
        async def get(self, route: str, params: str = "") -> Response | None:
            flag = True
            response = None
            while flag:
                try:
                    response = await self.session.get(self.base_url + route + params, timeout=self.timeout)
                    st_code = response.status_code 
                    
                    if st_code == 401:
                        logger.error(f"Some error: status code is {st_code}, text: {response.text}")
                        logger.error(response.json(), response.headers, sep="\n\n")
                        await asyncio.sleep(20)
                        await self.auth()
                        logger.info("Next try")
                        continue
                    elif st_code == 404:
                        logger.error(f"Some error: status code is {st_code}, text: {response.text}")
                        return response
                    flag = False
                except TimeoutException:
                    logger.exception("Timeout error. Retrying...")
                    await asyncio.sleep(config.API_CALLS_TIMEOUT_DELAY * 30)
                    continue
                except ConnectError:
                    logger.error("Connection error. Retrying...")
                    await asyncio.sleep(config.API_CALLS_TIMEOUT_DELAY * 30)
                    continue
                except Exception as e:
                    logger.exception(f"Unexpected error: {e}. Retrying...")
                    await asyncio.sleep(config.API_CALLS_TIMEOUT_DELAY)
                    continue
            return response    

        async def patch(self, route: str, params) -> Response | None:
            flag = True
            response = None
            while flag:
                try:
                    response = await self.session.patch(self.base_url + route, json=params, timeout=self.timeout)
                    st_code = response.status_code 

                    if st_code == 401:
                        logger.error(f"Some error: status code is {st_code}, text: {response.text}")
                        logger.error(response.json(), response.headers, sep="\n\n")
                        await asyncio.sleep(20)
                        await self.auth()
                        logger.info("Next try")
                        continue
                    elif st_code == 404:
                        logger.error(f"Some error: status code is {st_code}, text: {response.text}")
                        return response
                    flag = False
                except TimeoutException as e:
                    logger.exception("Time out error", e)
                    sleep(config.API_CALLS_TIMEOUT_DELAY * 30)
                    logger.exception("Next try")
                    continue
                except ConnectionError as e:
                    logger.error("Connecttion error. ", e)
                    sleep(config.API_CALLS_TIMEOUT_DELAY * 30)
                    logger.error("Next try")
                    continue
                except Exception as e: 
                        logger.exception("Some error: ", e)
                        sleep(config.API_CALLS_TIMEOUT_DELAY)
                        logger.exception("Next try")
                        continue
            return response    

        def create_json_for_request(self, grid: APIGrids, page: int=1, issue_id: int=0, service_id=None, **kwargs) -> dict[str, Any]:
            """
            Generate query string parameters
            """
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
                filters = {}
                role = kwargs["role"]
                if role:
                    filters = {
                        "role": role 
                    }
                data = {
                    "json" : json.dumps({
                        "table":{
                            "sortBy":"id",
                            "descending": True,
                            "page": page,
                            "rowsPerPage": 0,
                            "rowsNumber": 0,
                            "query": "",
                            "filters": filters,
                            "except_filters": {
                            },
                            "grid": grid.value
                        }
                    })
                }
            elif grid == APIGrids.ROOMS:
                building_id: int | None = kwargs["building_id"]
                building_id_filter = {"building_id": building_id} if building_id else {}
                data = {
                    "json" : json.dumps({
                        "table":{
                            "sortBy":"id",
                            "descending": True,
                            "page": page,
                            "rowsPerPage": 0,
                            "rowsNumber": 0,
                            "query": "",
                            "filters": building_id_filter,
                            "except_filters": {},
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

        def generate_query_params_issues(self, page: int, **kwargs):
            
            params = {
                "page": page,
                "sort_by": "id",
                "descending": True,
                "facility_id": 2,
                # "query":"",
                "filters[transition_status_id][]": [
                    "16,130,179", "33,125,177", "134", "6",
                    "10,20,124,176", "96,132,180", "9,19,131,185",
                    "21,128,184", "1,11,127,183", "5,22,126,182",
                    "4", "2,12,133,175", "8,18,129,178", "7"
                ],
                "filters[transition_date[from]]": kwargs["start_date"],
                "filters[transition_date[to]]": kwargs["end_date"]
            }

            return params
        
        async def auth(self) -> int:
            flag = True
            while flag:
                try:
                    response = await self.session.post(
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
                    sleep(config.API_CALLS_DELAY)
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
        
        def check_time_range(self, time_range: list[str]) -> list[str]:
            try:
                if time_range == []:
                    start_date = date.today().strftime("%Y-%m-%dT%H:%M:%S")
                    end_date = (date.today() + timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%S")
                    return [start_date, end_date]
                
                return time_range
            except ValueError:
                logger.error("Error validation time range")
                return []