from pathlib import Path
from pydantic import BaseModel,validator
from typing import Optional,List,Dict
import re
import yaml
from github import Github
import json
import re

class Instance(BaseModel):
    id: str
    title: List[str]
    colophon: str
    authors: List[str]
    bdrc_id: str
    location_info: dict
    diplomatic_id:Optional[List[str]]
    alignmnet_ids:Optional[List[str]]
    collection_ids:Optional[List[str]]

    @validator("diplomatic_id")
    def validate_diplonatic_id(cls,value):
        if not re.match(r"I.*",value):
            raise ValueError("Pecha Id is not Diplomatic")

    
class Work(BaseModel):
    id: str
    title: str
    alternative_title: Optional[str]
    language: str
    bdrc_work_id: str
    authors: List[str]
    best_instance:Optional[Instance]
    instances: Optional[List[Instance]]


    def get_instances(self) ->List[Instance]:
        return self.instances


    def set_instance(self,instance:Dict)->None:
        try:
            instance_obj = Instance(**instance)
            if self.instances:
                self.instances.append(instance_obj)
            else:
                self.instances = []
                self.instances.append(instance_obj)  
        except Exception as e:
            print(e)
         



def get_openpechaId_from_catalog(workId):
    catalog = Path("catalog.csv").read_text()
    for line in catalog.splitlines():
        if f"bdr:{workId}" in line:
            openPechaId = re.match("\[(.*)\]",line).group(1)
            return openPechaId
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
        

def is_work_file_created(work_id):
    work_files = [work_file.stem for work_file in Path("./works").iterdir()]
    if work_id in work_files:
        return True
    return False


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
    work = load_yaml(Path("works/WC8BEB943.yml"))
    demo_instance = work["instances"][0]
    work_dic = load_yaml(Path("W0D4D7940.yml"))
    obj = Work(**work_dic)
    obj.set_instance(demo_instance)
    #create_work_file(work_dic)
    #is_work_file_created("123")


