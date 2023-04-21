from main import dump_yaml
from pathlib import Path
from typing import Dict
from pydantic import ValidationError
from core.work import Work
from parse_graph import get_work_info

import json
import csv
import asyncio
import aiohttp


WORKS_DIR = "new_works"

def get_work_ids():
    with open('bdrc.csv', newline='') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        next(csvreader)
        for row in csvreader:
            op_work_id = row[0]
            bdrc_work_id = row[1]
            yield op_work_id,bdrc_work_id

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
    return validated_work

async def main():
   for work_ids in get_work_ids():
        op_work_id,bdrc_work_id = work_ids
        print(bdrc_work_id)
        work =  await create_work(bdrc_work_id,op_work_id)
        dump_yaml(work,Path(f"{WORKS_DIR}/{work['id']}.yml"))


if __name__ == "__main__":
    asyncio.run(main())    