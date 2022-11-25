from pathlib import Path
from github import Github
import csv
import re
import os
import shutil
from git import Repo

config = {
    "OP_ORG": "https://github.com/Openpecha-Data"
    }


def get_branch(repo, branch):
    if branch in repo.heads:
        return branch
    return "master"


def download_repo(repo_name, out_path=None, branch="master"):
    try:
        pecha_url = f"{config['OP_ORG']}/{repo_name}.git"
        out_path = Path(out_path)
        out_path.mkdir(exist_ok=True, parents=True)
        repo_path = out_path / repo_name
        Repo.clone_from(pecha_url, str(repo_path))
        repo = Repo(str(repo_path))
        branch_to_pull = get_branch(repo, branch)
        repo.git.checkout(branch_to_pull)
        return repo_path
    except:
        return None

def get_repo_names(g, repos_in_catalog):
    repo_names = {}
    curr_repo = {}
    repo_list = ["catalog","users","ebook-template","alignments","openpecha-template"
                    "collections","data-translation-memory",
                "openpecha-toolkit", "openpecha.github.io", "Transifex-Glossary", 
                "W00000003","works","works-bak", ".github"]
    num = 0
    for repo in g.get_user("Openpecha-Data").get_repos():
        repo_name = repo.name
        if repo_name in repo_list:
            continue
        else:
            if repo_name in repos_in_catalog:
                continue
            else:
                num += 1
                curr_repo[num] = {
                    "repo": repo_name
                }
                repo_names.update(curr_repo)
                curr_repo = {}
    return repo_names

def get_pecha_ids_from_catalog():
    repo_path = download_repo("catalog", Path(f"./",))
    pecha_ids = ""
    with open(f"{repo_path}/data/catalog.csv", newline="") as file:
        pechas = list(csv.reader(file, delimiter=","))
        for pecha in pechas[1:]:
            pecha_id = re.search("\[.+\]", pecha[0])[0][1:-1]
            pecha_ids += pecha_id+"\n"
    shutil.rmtree(str(repo_path))
    return pecha_ids

def check_if_repo_is_alignment(repo_path):
    pecha_id = repo_path.name
    if os.path.isdir(Path(f"{repo_path}/{pecha_id}.opa")):
        return True
    else:
        return False

def get_all_alignment_ids(pecha_ids):
    alignment_ids = ""
    undownloaded = ""
    for pecha_id in pecha_ids:
        repo_path = download_repo(pecha_id, Path(f"./"))
        if repo_path:
            check = check_if_repo_is_alignment(repo_path)
            shutil.rmtree(str(repo_path))
            if check:
                alignment_ids += pecha_id+"\n"
        else:
            undownloaded += pecha_id+"\n"
    Path(f"./ids/undownloaded.txt").write_text(undownloaded, encoding='utf-8')
    return alignment_ids

if __name__ == "__main__":
    token = ""
    g = Github(token)
    # pecha_ids = get_pecha_ids_from_catalog()
    pecha_ids = Path(f"./ids/pecha_ids.txt").read_text(encoding='utf-8').splitlines()
    alignment_ids = get_all_alignment_ids(pecha_ids)
    Path(f"./ids/alignment_ids.txt").write_text(alignment_ids, encoding='utf-8')
    