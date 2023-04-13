from main import create_work,dump_yaml
from pathlib import Path
import csv

WORKS_DIR = "new_works"

def get_work_ids():
    with open('bdrc.csv', newline='') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        next(csvreader)
        for row in csvreader:
            op_work_id = row[0]
            bdrc_work_id = row[1]
            yield op_work_id,bdrc_work_id


def main():
   for work_ids in get_work_ids():
        op_work_id,bdrc_work_id = work_ids
        print(bdrc_work_id)
        work = create_work(op_work_id,op_work_id)
        dump_yaml(work,Path(f"{WORKS_DIR}/{work['id']}.yml"))


if __name__ == "__main__":
    main()
    