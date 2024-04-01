import json
import pathlib
from typing import List, Dict

import requests
from requests.auth import HTTPBasicAuth
from pydantic import BaseModel

from app.utils import paths
from app.utils.logger import app_logger
from app.utils.settings import settings


_basic_auth = HTTPBasicAuth(settings.HOLMES_ZD_USERNAME, settings.HOLMES_ZD_TOKEN)
_search_url = settings.HOLMES_ZD_BASE_URL + "/search"
_ticket_url = settings.HOLMES_ZD_BASE_URL + "/tickets"
_data_path = paths.get_path(paths.get_root_dir(), "data", "raw", "zendesk")


class Comment(BaseModel):
    id: int
    author_id: int
    public: bool
    created_at: str
    body: str


class Ticket(BaseModel):
    id: int
    subject: str
    requester_id: int
    comments: List[Comment] = []


def download_tickets():
    params = {
        "query": "type:ticket status:closed",
        "sort_by": "created_at",
        "sort_order": "desc",
        "per_page": "50",
    }

    app_logger.info("Downloading Zendesk Tickets...")

    res_tickets = requests.get(_search_url, auth=_basic_auth, params=params)

    print(res_tickets.url)
    tickets = res_tickets.json()["results"]
    for ticket in tickets:
        ticket_id = ticket["id"]
        ticket_file = paths.get_path(_data_path, f"{ticket_id}_ticket.json")

        with open(ticket_file, "w") as file:
            json.dump(ticket, file, indent=4)

        comments_url = _ticket_url + f"/{ticket_id}/comments"
        app_logger.info(f"Downloading Zendesk Comments for Ticket: {ticket_id}")
        res_comments = requests.get(comments_url, auth=_basic_auth)
        comments = res_comments.json()["comments"]
        comments_file = paths.get_path(_data_path, f"{ticket_id}_comments.json")

        with open(comments_file, "w") as file:
            json.dump(comments, file, indent=4)


def get_tickets() -> List[Ticket]:
    grouped_files: Dict[str, List[str]] = {}
    tickets: List[Ticket] = []

    for file_path in pathlib.Path(paths.get_path(_data_path)).rglob("*.json"):
        file_name = file_path.name
        ticket_id = file_name.split("_")[0]
        grouped_files.setdefault(ticket_id, []).append(file_name)

    for ticket_id, grp_file_names in grouped_files.items():
        ticket: Ticket = None
        comments: List[Comment] = []
        for file_name in grp_file_names:
            file_path = paths.get_path(_data_path, file_name)
            with open(file_path, "r") as file:
                json_data = json.load(file)

                if "comments" in file_name:
                    for comment_dict in json_data:
                        comment = Comment.model_validate(comment_dict)
                        comments.append(comment)
                else:
                    ticket = Ticket.model_validate(json_data)
        ticket.comments = comments
        tickets.append(ticket)
    return tickets


# download_tickets()
get_tickets()
