from main import create_work,dump_yaml
from pathlib import Path
import csv
import logging

logging.basicConfig(filename='err.log', filemode='w', format='%(message)s', level=logging.INFO)


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
        try:
            work = create_work(bdrc_work_id,op_work_id)
            dump_yaml(work,Path(f"{WORKS_DIR}/{work['id']}.yml"))
        except Exception as e:
            logging.info(f"{bdrc_work_id},{e}")


if __name__ == "__main__":
    main()
    
