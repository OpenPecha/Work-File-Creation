import os
import subprocess
from pathlib import Path
from openpecha import *
from openpecha.utils import load_yaml, dump_yaml
from openpecha.github_utils import create_github_repo



def rename_repo_of_opf(new_pecha_id, pecha_path, token):
    new_pecha_path = Path(f"./new_opf/{new_pecha_id}")
    os.mkdir(new_pecha_path)
    org = "Openpecha-Data"
    remote_repo_url = create_github_repo(new_pecha_path, org, token)
    subprocess.run(f'cd {pecha_path}; git remote set-url origin {remote_repo_url}',shell=True)


def update_readme_of_opf(new_pecha_id, pecha_path):
    pecha_id = pecha_path.name
    readme_path = Path(f"{pecha_path}/README.md")
    if readme_path.exists():
        readme = readme_path.read_text(encoding='utf-8')
        new_readme = readme.replace(pecha_id, new_pecha_id)
        readme_path.write_text(new_readme, encoding='utf-8')


def rename_meta_of_opf(new_pecha_id, pecha_path):
    meta_path = Path(f"{pecha_path}/{new_pecha_id}.opf/meta.yml")
    meta = load_yaml(meta_path)
    meta['id'] = new_pecha_id
    dump_yaml(meta, meta_path)


def rename_opf_dir_name_of_opf(new_pecha_id, pecha_path):
    pecha_id = pecha_path.stem
    subprocess.run(f'cd {pecha_path}; git mv {pecha_id}.opf {new_pecha_id}.opf', shell=True)

    
def update_repo_name_of_opf(pecha_path, token):
    meta = load_yaml(Path(f"{pecha_path}/{pecha_path.name}.opf/meta.yml"))
    new_pecha_id = meta['id']
    rename_opf_dir_name_of_opf(new_pecha_id, pecha_path)
    update_readme_of_opf(new_pecha_id, pecha_path)
    rename_repo_of_opf(new_pecha_id, pecha_path, token)
    return new_pecha_id

def rename_repo_of_alignment(new_pecha_id, pecha_path, token):
    new_pecha_path = Path(f"./new_opa/{new_pecha_id}")
    os.mkdir(new_pecha_path)
    org = "Openpecha-Data"
    remote_repo_url = create_github_repo(new_pecha_path, org, token)
    subprocess.run(f'cd {pecha_path}; git remote set-url origin {remote_repo_url}',shell=True)

def rename_meta_of_alignment(new_pecha_id, pecha_path):
    meta_path = Path(f"{pecha_path}/{new_pecha_id}.opa/meta.yml")
    meta = load_yaml(meta_path)
    meta['id'] = new_pecha_id
    dump_yaml(meta, meta_path)


def rename_alignment_dir_name(new_pecha_id, pecha_path):
    pecha_id = pecha_path.stem
    subprocess.run(f'cd {pecha_path}; git mv {pecha_id}.opa {new_pecha_id}.opa', shell=True)
    
def update_alignment_name(repo_path, new_alignment_id, token):
    rename_alignment_dir_name(new_alignment_id, repo_path)
    rename_meta_of_alignment(new_alignment_id, repo_path)
    rename_repo_of_alignment(new_alignment_id, repo_path, token)