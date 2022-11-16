from symbol import except_clause
from openpecha.buda.api import get_buda_scan_info
import csv
import requests
import pyewts

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
       
def get_instance_info(id):
    instance_g = get_graph_of_id(id)
    location_id = instance_g.objects(BDR[id], BDO["contentLocation"])
    location_info = get_location_info(location_id)
    rootInstanceid = location_info["contentLocationInstance"]
    title, alternative_title  = get_titles(instance_g, id)
    authors = get_author(get_graph_of_id(rootInstanceid), rootInstanceid)
    instance_info= {
        "id": id,
        "title": title,
        "alternative_title": alternative_title,
        "authors": authors,
        "bdrc_id": rootInstanceid,
        "location_info": location_info
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
        if author.language == "bo-x-ewts":
            author = ewtstobo(author)
            authors.append(author)
        else:
            authors.append(author.value)
    return authors

def get_text(value):
    if value:
        if value.language == "bo-x-ewts":
            return ewtstobo(value)
        else:
            return value.split("/")[0]
    else:
        return

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

def get_work_info(id, OP_work_id):
    instance_ids = []
    try:
        g = get_graph_of_id(id)
        
        title, alternative_title = get_titles(g, id)
        authors = get_author(g, id)
        
        instances = g.objects(BDR[id], BDO["workHasInstance"])
        for instance in instances:
            instance_id = instance.split("/")[-1]
            instance_ids.append(instance_id)
        work_info = {
            'id': OP_work_id,
            'title': title,
            'alternative_title': alternative_title,
            'authors': authors,
            'bdrc_work_id': id,
            'instances': get_instance_info_list(instance_ids)
        }
        return work_info
    except:
        return {}

def get_op_work_id(work_id):
    with open("./data/idtowork.csv", newline="") as csvfile:
        infos = csv.reader(csvfile, delimiter=",")
        for info in infos:
            id = info[0]
            work = info[1]
            if work_id == work:
                return id
        return get_work_id()
        
        

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