from pathlib import Path
from openpecha.utils import load_yaml, dump_yaml
from git import Repo
from rename_repo_name import update_alignment_name
from openpecha.core.ids import get_alignment_id
from openpecha.core.pecha import OpenPechaFS

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

def get_source_and_target_id(alignment_repo_path):
    alignment_id = alignment_repo_path.name
    alignment_path = Path(f"{alignment_repo_path}/{alignment_id}.opa/Alignment.yml")
    alignment = load_yaml(alignment_path)
    for id, info in alignment["segment_sources"].items():
        if info["relation"] == "source":
            source_id = id
        elif info["relation"] == "target":
            target_id = id
    return source_id, target_id


def update_alignment_repo_name(repo_path, token):
    new_alignment_id = get_alignment_id()
    update_alignment_name(repo_path, new_alignment_id, token)


def update_the_opfs(source_id, target_id):
    output_path = Path(f"./pechas/")
    source_path = download_repo(source_id, output_path)
    # meta_path = Path(f"{source_path}/{source_path.name}.opf/meta.yml")
    # metadata = load_yaml(meta_path)
    pecha = OpenPechaFS(source_path)
    pecha.bases = Path(f"{pecha.base_path}")
    
    

if __name__ == "__main__":
    token = ""
    alignment_id = "85a2e5297d9b4d0d81a168a2327683f2"
    alignment_repo_path = download_repo(alignment_id, Path(f"./alignments"))
    source_id, target_id = get_source_and_target_id(alignment_repo_path)
    update_alignment_repo_name(alignment_repo_path, token)
    update_the_opfs(source_id, target_id)
    