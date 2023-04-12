from pydantic import BaseModel,validator
from typing import Optional,List,Dict
import re

class Instance(BaseModel):
    """span={
    'base_name':(start,end)}"""
    bdrc_instance_id: str
    titles: List[str]
    authors: Optional[List[str]]
    language: Optional[str]
    span: Optional[dict]
    diplomatic_id:Optional[str]
    alignmnet_ids:Optional[List[str]]
    collection_ids:Optional[List[str]]

    @validator("diplomatic_id")
    def validate_diplonatic_id(cls,value):
        if not value:
            return value
        elif not re.match(r"I.*",value):
            raise ValueError("Pecha Id is not Diplomatic")

    
class Work(BaseModel):
    id: str
    title: str
    alternative_title: Optional[str]
    bdrc_work_id: str
    authors: List[str]
    best_instance:Optional[Instance]
    instances: Optional[List[Instance]]

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