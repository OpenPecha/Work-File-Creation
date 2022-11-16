from pathlib import Path
import pydantic
from typing import Optional,List,Dict
import re
import yaml
from github import Github
import json


class Instance(pydantic.BaseModel):
    id:str
    title:str
    alternative_title:Optional[str]
    authors:List[str]
    bdrc_id:str
    location_info:dict


class Work(pydantic.BaseModel):
    id: str
    title: str
    alternative_title: Optional[str]
    bdrc_work_id: str
    authors:List[str]
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
    dump_yaml(attributes,Path(f"{work_obj.id}.yml"))
    #y = yaml.dump(attributes,sort_keys=False)
    return 



def publish_repo(file,token):
    g = Github(token)
    works_repo_name = "OpenPecha-Data/works"
    works_repo = g.get_repo(works_repo_name)
    works_repo.create_file("demo.yml","demo",Path(file).read_text())


def create_work_file(work_dic):
    try:
        work_obj = Work(**work_dic)
        attributes = json.loads(json.dumps(work_obj, default=lambda o: o.__dict__))
        dump_yaml(attributes,Path(f"{work_obj.id}.yml"))
    except Exception as e:
        print(e)


def load_yaml(fn: Path) -> None:
    return yaml.load(fn.open(encoding="utf-8"), Loader=yaml.CSafeLoader)


def dump_yaml(data: Dict, output_fn: Path) -> Path:
    with output_fn.open("w", encoding="utf-8") as fn:
        yaml.dump(
            data,
            fn,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
            Dumper=yaml.CSafeDumper,
        )
    return output_fn


if __name__ == "__main__":
    work_dic = load_yaml(Path("./works/W0D4D7940.yml"))
    create_work_file(work_dic)
    



