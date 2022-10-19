from ast import In
from pathlib import Path
import pydantic
from typing import Optional,List,Dict
import re

class Instance(pydantic.BaseModel):
    id:str
    #title:str
    #language:str
    #bdrc_instance_id:str
    #opf_id:str
    #bdrc_collection_info:Dict[str:str]
    #source_metadata:Dict[str,str]


class Work(pydantic.BaseModel):
    id: str
    #title: str
    #alt_titles: List[str]
    #bdrc_work_id: str
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

if __name__ == "__main__":
    obj1 = Instance(id="123")
    obj2 = Work(id="345")
    obj2.set_instance(obj1)
    print(obj2.get_instances())

