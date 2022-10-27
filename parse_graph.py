from symbol import except_clause
from openpecha.buda.api import get_buda_scan_info
import csv
import requests
import pyewts

from pathlib import Path
from rdflib import Graph
from rdflib.namespace import RDF, RDFS, SKOS, OWL, Namespace, NamespaceManager, XSD
from openpecha.core.ids import get_work_id


BDR = Namespace("http://purl.bdrc.io/resource/")
BDO = Namespace("http://purl.bdrc.io/ontology/core/")
BDA = Namespace("http://purl.bdrc.io/admindata/")
ADM = Namespace("http://purl.bdrc.io/ontology/admin/")
EWTSCONV = pyewts.pyewts()



def ewtstobo(ewtsstr):
    res = EWTSCONV.toUnicode(ewtsstr)
    return res

def get_author_ids(agent_ids):
    author_ids = []
    g = Graph()
    try:
        for agent_id in agent_ids:
            ttl = requests.get(f"https://purl.bdrc.io/query/graph/OP_info?R_RES=bdr:{agent_id}&format=ttl")
            g.parse(data=ttl.text, format='ttl')
            
            authors = g.objects(BDR[agent_id], BDO["author"])
            for author in authors:
                author_id = author.split("/")[-1]
                author_ids.append(author_id)
        return author_ids
    except:
        return None


def get_agent_ids(creator_ids):
    agent_ids = []
    g = Graph()
    try:
        for creator_id in creator_ids:
            ttl = requests.get(f"https://purl.bdrc.io/query/graph/OP_info?R_RES=bdr:{creator_id}&format=ttl")
            g.parse(data=ttl.text, format='ttl')
            
            agents = g.objects(BDR[creator_id], BDO["agent"])
            for agent in agents:
                agent_id = agent.split("/")[-1]
                agent_ids.append(agent_id)
        return agent_ids
    except:
        return None
            

def parse_author_ids(g, work_id):
    creator_ids = []
    try:
        creators = g.objects(BDR[work_id], BDO["creator"])
        for creator in creators:
            creator_id = creator.split("/")[-1]
            creator_ids.append(creator_id)
        agent_ids = get_agent_ids(creator_ids)
        # author_ids = get_author_ids(agent_ids)
        return agent_ids
    except:
        return None
        
def get_graph_of_id(id):
    g = Graph()
    try:
        ttl = requests.get(f"https://purl.bdrc.io/query/graph/OP_info?R_RES=bdr:{id}&format=ttl")
        g.parse(data=ttl.text, format="ttl")
        return g
    except:
        return 


def get_author(g, work_id):
    authors = []
    author_ids = parse_author_ids(g, work_id)
    for author_id in author_ids:
        author_g = get_graph_of_id(author_id)
        author = author_g.value(BDR[author_id], SKOS["prefLabel"])
        if author.language == "bo-x-ewts":
            author = ewtstobo(author)
            authors.append(author)
        else:
            authors.append(author.value)
    return authors


def get_titles(g, id):
    title = g.value(BDR[id], SKOS["prefLabel"])
    alternative_title = g.value(BDR[id], SKOS["altLabel"])
    return title, alternative_title

def get_instance_info(instance_id):
    pass

def get_instance_info_list(instance_ids):
    instances = []
    for instance_id in instance_ids:
        instance_info = get_instance_info(instance_id)
        instances.append(instance_info)
    return instances

def get_work_info(id, OP_work_id):
    instance_ids = []
    g = Graph()
    try:
        ttl_response = requests.get(f"https://purl.bdrc.io/query/graph/OP_info?R_RES=bdr:{id}&format=ttl")
        g.parse(data=ttl_response.text, format="ttl")
        
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
            'instances': get_instance_info_list(instances)
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
            work_info = get_work_info(work)
            OP_work_id = get_op_work_id(work)
            # print(scan_info)