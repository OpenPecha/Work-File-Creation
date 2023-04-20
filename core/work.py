from pydantic import BaseModel,validator
from typing import Optional,List,Dict
import re

class Instance(BaseModel):
    """span={
    'base_name':(start,end)}"""
    id :Optional[str]
    bdrc_instance_id: str
    authors: Optional[List[str]]
    language: Optional[str]
    span: Optional[dict]
    alignmnet_ids:Optional[List[str]]
    collection_ids:Optional[List[str]]


    
class Work(BaseModel):
    id: str
    title: Optional[str]
    alternative_title: Optional[str]
    bdrc_work_id: str
    authors: List[str]
    best_instance:Optional[Instance]
    instances: Optional[List[Instance]]
