from symbol import except_clause
from openpecha.buda.api import get_buda_scan_info
import csv
import requests
import pyewts
import re
import requests
import csv
import shutil
from pathlib import Path
from git import Repo

from pathlib import Path
from rdflib import Graph
from rdflib.namespace import RDF, RDFS, SKOS, OWL, Namespace, NamespaceManager, XSD
from openpecha.core.ids import get_work_id
from openpecha.utils import dump_yaml


BDR = Namespace("http://purl.bdrc.io/resource/")
BDO = Namespace("http://purl.bdrc.io/ontology/core/")
BDA = Namespace("http://purl.bdrc.io/admindata/")
ADM = Namespace("http://purl.bdrc.io/ontology/admin/")
EWTSCONV = pyewts.pyewts()


config = {
    "OP_ORG": "https://github.com/Openpecha-Data"
    }

def get_catalog_info():
    file_path = './'
    repo_path = download_repo("catalog", file_path)
    catalog_info = get_repos_info(repo_path)
    return catalog_info


def get_repos_info(repo_path):
    curr = {}
    catalog_info = {}
    with open(f"{repo_path}/data/catalog.csv", newline="") as file:
        pechas = list(csv.reader(file, delimiter=","))
        for pecha in pechas[1:]:
            pecha_id = re.search("\[.+\]", pecha[0])[0][1:-1]
            work_id = pecha[-2]
            curr[pecha_id] = {
                "work_id": work_id
            }
            catalog_info.update(curr)
            curr = {}
    shutil.rmtree(str(repo_path))
    return catalog_info


def get_branch(repo, branch):
    if branch in repo.heads:
        return branch
    return "master"


def download_repo(repo_name, out_path=None, branch="master"):
    pecha_url = f"{config['OP_ORG']}/{repo_name}.git"
    out_path = Path(out_path)
    out_path.mkdir(exist_ok=True, parents=True)
    repo_path = out_path / repo_name
    Repo.clone_from(pecha_url, str(repo_path))
    repo = Repo(str(repo_path))
    branch_to_pull = get_branch(repo, branch)
    repo.git.checkout(branch_to_pull)
    return repo_path


def ewtstobo(ewtsstr):
    res = EWTSCONV.toUnicode(ewtsstr)
    return res

def get_value(g, id, type):
    if g.value(BDR[id], BDO[type]):
        value = g.value(BDR[id], BDO[type])
        return value.split("/")[-1]
    else:
        return None

def get_location_info(location_ids):
    for location_id in location_ids:
        id = location_id.split("/")[-1]
    g = get_graph_of_id(id)
    location_info = {
        "contentLocationEndLine": get_value(g, id, "contentLocationEndLine"),
        "contentLocationEndPage": get_value(g, id, "contentLocationEndPage"),
        "contentLocationInstance": get_value(g, id, "contentLocationInstance"),
        "contentLocationLine": get_value(g, id, "contentLocationLine"),
        "contentLocationPage": get_value(g, id, "contentLocationPage"),
        "contentLocationVolume": get_value(g, id, "contentLocationVolume")
    }
    return location_info

def get_root_instance_id(g, id):
    root_instance_ids = g.objects(BDR[id], BDO["inRootInstance"])
    for root_instance_id in root_instance_ids:
        root_instance = root_instance_id.split("/")[-1]
    return root_instance
       
def get_colophon(g, id):
    colophon = g.value(BDR[id], BDO["colophon"])
    return get_text(colophon)
    
def get_opf_id(instance_id, work_id):
    for pecha_id, work_info in catalog_info.items():
        if work_info["work_id"] == instance_id:
            return pecha_id
        elif work_info["work_id"] == work_id:
            return pecha_id
    return 

def get_instance_info(id):
    instance_g = get_graph_of_id(id)
    location_id = instance_g.objects(BDR[id], BDO["contentLocation"])
    location_info = get_location_info(location_id)
    rootInstanceid = get_root_instance_id(instance_g, id)
    titles= get_titles_of_instance(instance_g, id)
    colophon = get_colophon(instance_g, id)
    pecha_id = get_opf_id(id, location_info["contentLocationInstance"])
    instance_info= {
        "id": id,
        "titles": titles,
        "colophon": colophon,
        "rootInstanceid": rootInstanceid,
        "location_info": location_info,
        "opf_id": pecha_id
    }
    return instance_info

def get_instance_info_list(instance_ids):
    instances = []
    for instance_id in instance_ids:
        instance_info = get_instance_info(instance_id)
        instances.append(instance_info)
    return instances

def get_ids(ids, type):
    _ids = []
    for id in ids:
        g = get_graph_of_id(id)
        names = g.objects(BDR[id], BDO[type])
        for name in names:
            _id = name.split("/")[-1]
            _ids.append(_id)
    return _ids

def parse_author_ids(g, work_id):
    creator_ids = []
    try:
        creators = g.objects(BDR[work_id], BDO["creator"])
        for creator in creators:
            creator_id = creator.split("/")[-1]
            creator_ids.append(creator_id)
        author_ids = get_ids(creator_ids, "agent")
        return author_ids
    except:
        return None

def get_author(g, id):
    authors = []
    author_ids = parse_author_ids(g, id)
    for author_id in author_ids:
        author_g = get_graph_of_id(author_id)
        author = author_g.value(BDR[author_id], SKOS["prefLabel"])
        authors.append(get_text(author))
    return authors

def get_text(value):
    if value:
        if value.language == "bo-x-ewts" or "sa-x-ewts":
            return ewtstobo(value)
        else:
            return value.split("/")[0]
    else:
        return

def get_titles_of_instance(g, id):
    titles = []
    title_objects = g.objects(BDR[id], BDO["hasTitle"])
    for title_object in title_objects:
        title_id = title_object.split("/")[-1]
        title_g = get_graph_of_id(title_id)
        title_ = title_g.value(BDR[title_id], RDFS["label"])
        title = get_text(title_)
        titles.append(title)
    return titles
        
def get_titles(g, id):
    title = g.value(BDR[id], SKOS["prefLabel"])
    alternative_title = g.value(BDR[id], SKOS["altLabel"])
    title = get_text(title)
    alternative_title = get_text(alternative_title)
    return title, alternative_title


def get_graph_of_id(id):
    g = Graph()
    try:
        ttl = requests.get(f"https://purl.bdrc.io/query/graph/OP_info?R_RES=bdr:{id}&format=ttl")
        g.parse(data=ttl.text, format="ttl")
        return g
    except:
        return None
def get_language(g, id):
    _objects = g.objects(BDR[id], BDO["language"])
    for _object in _objects:
        return _object.split("/")[-1]

def get_work_info(id, OP_work_id):
    instance_ids = []
    try:
        g = get_graph_of_id(id)
        
        title, alternative_title = get_titles(g, id)
        authors = get_author(g, id)
        language = get_language(g, id)
        
        instances = g.objects(BDR[id], BDO["workHasInstance"])
        for instance in instances:
            instance_id = instance.split("/")[-1]
            instance_ids.append(instance_id)
        work_info = {
            "id": OP_work_id,
            "titles": title,
            "alternative_title": alternative_title,
            "authors": authors,
            "language": language,
            "bdrc_work_id": id,
            "instances": get_instance_info_list(instance_ids)
        }
        return work_info
    except:
        return {}

def get_op_work_id(work_id):
    with open("./data/bdrc.csv", newline="") as csvfile:
        infos = csv.reader(csvfile, delimiter=",")
        for info in infos:
            id = info[0]
            work = info[1]
            if work_id == work:
                return id
        return get_work_id()
        
catalog_info = get_catalog_info()       

if __name__ == '__main__':
    with open("./data/idtowork.csv", newline="") as csvfile:
        infos = csv.reader(csvfile, delimiter=",")
        for info in infos:
            id = info[0]
            work = info[1].split("/")[-1]
            OP_work_id = get_op_work_id(work)
            work_info = get_work_info(work, OP_work_id)
            works_path = Path(f"./works/{OP_work_id}.yml")
            dump_yaml(work_info,works_path)