from parse_graph import get_work_info,work_catalog
from core.work import Work
from pathlib import Path
from typing import Dict
from pydantic import ValidationError
from github import Github
import json
import yaml
import re
import os


def dump_yaml(data: Dict, output_fn: Path) -> Path:
    with output_fn.open("w", encoding="utf-8") as fn:
        yaml.dump(
            data,
            fn,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
            Dumper=yaml.SafeDumper,
        )
    return output_fn


def get_openpechaId_from_catalog(workId):
    catalog = Path("catalog.csv").read_text()
    for line in catalog.splitlines():
        if f"bdr:{workId}" in line:
            openPechaId = re.match("\[(.*)\]",line).group(1)
            return openPechaId
    return

def add_instances_to_work(old_work,work):
    pass


def push_work(work,token):
    g = Github(token)
    works_repo_name = "OpenPecha-Data/works"
    works_repo = g.get_repo(works_repo_name)
    op_id = is_work_file_created(work["bdrc_work_id"])
    if op_id:
        work_file_name = f"{op_id}.yml"
        old_work_content = works_repo.get_contents(f"/works/{work_file_name}")
        old_work = yaml.safe_load(old_work_content.decoded_content)
        new_work = add_instances_to_work(old_work,work)
        new_work_content = yaml.dump(new_work)
        works_repo.update_file(
            path=f"works/{work_file_name}",
            message=f"Update {work_file_name}",
            content=new_work_content,
            sha=old_work_content.sha,
                )
    else:
        work_file_name = f"{work['id']}.yml"
        work_yml = yaml.dump(work,
                    default_flow_style=False,
                    sort_keys=False,
                    allow_unicode=True,
                    Dumper=yaml.SafeDumper
                    )
        works_repo.create_file(f"works/{work_file_name}",f"Created {work_file_name}",work_yml)


def is_work_file_created(work_id):
    works = work_catalog.split("\n")
    for work in works[1:]:
        row = work.split(",")
        id = row[0]
        work = row[2]
        if work_id == work:
            return id
    return


def validate_work(work:Dict):
    try:
        work_obj = Work(**work)
        attributes = json.loads(json.dumps(work_obj, default=lambda o: o.__dict__))
        return attributes
    except ValidationError as e:
        print(e)


def create_work(bdr_work_id,op_work_id=None):
    work = get_work_info(bdr_work_id,op_work_id)
    validated_work = validate_work(work)
    return validated_wor:wq

def delete_file(token,path):
    g = Github(token)
    works_repo_name = "OpenPecha-Data/works"
    works_repo = g.get_repo(works_repo_name)
    file = works_repo.get_contents(path)
    works_repo.delete_file(path, "test", file.sha)


if __name__ == "__main__":
    token = os.getenv("GITHUB_TOKEN")
    work = create_work(bdr_work_id="WA0RT0010")
    #dump_yaml(work,Path("test.yml"))
    #push_work(work,token)
