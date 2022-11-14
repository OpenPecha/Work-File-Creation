from pathlib import Path
import pydantic
from typing import Optional,List,Dict
import re
import yaml
import inspect
from git import Repo
from github import Github
import json


class Instance(pydantic.BaseModel):
    id:str
    title:str
    alternative_title:str
    authors:str
    bdrc_id:str
    location_info:str


class Work(pydantic.BaseModel):
    id: str
    title: str
    alternative_title: str
    bdrc_work_id: str
    authors:str
    instances: Optional[List[Instance]]


    def get_instances(self) ->List[Instance]:
        return self.instances


    def set_instance(self,instance_obj:Instance)->None:
        if self.instances:
            self.instances.append(instance_obj)
        else:
            self.instances = []
            self.instances.append(instance_obj)   



def get_openpechaId_from_catalog(workId):
    catalog = Path("catalog.csv").read_text()
    for line in catalog.splitlines():
        if f"bdr:{workId}" in line:
            openPechaId = re.match("\[(.*)\]",line).group(1)
            return openPechaId
    return


def convert_to_yaml(work_obj:Work):
    attributes = json.loads(json.dumps(work_obj, default=lambda o: o.__dict__))
    y = yaml.dump(attributes,sort_keys=False)
    return y



def publish_repo(file,token):
    g = Github(token)
    works_repo_name = "OpenPecha-Data/works"
    works_repo = g.get_repo(works_repo_name)
    works_repo.create_file("demo.yml","demo",Path(file).read_text())


def create_work_file(work_dic):
    try:
        work_obj = Work(**work_dic)
        work_yml = convert_to_yaml(work_obj)
        print(type(work_obj.__dict__))
        Path(f"{work_obj.id}.yml").write_text(work_yml,encoding="utf-8")
    except Exception as e:
        print(e)


if __name__ == "__main__":
    work_dic = {
            'id': "X123",
            'title': "chojuk",
            'alternative_title': "bodhi",
            'authors': "pandit",
            'bdrc_work_id': "BDr123",
            'instances':[{
                "id": "123",
                "title": "sub",
                "alternative_title": "xcx",
                "authors": "des",
                "bdrc_id": "Des",
                "location_info": "Sdes"
                }]
        }
    create_work_file(work_dic)
    



