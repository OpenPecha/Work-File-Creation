from pathlib import Path
from core.work import Work

def test_get_work_id_from_title():

    title = ""
    expected_work_id = "W"
    
    work_obj = Work()
    work_id = work_obj.get_work_id_from_title(title)
    assert work_id == expected_work_id

def test_get_work_meta():
    
    work_id = ""
    expected_work_meta_path = Path("Test") / "data" / "expected_work_meta"
    expected_work_meta = expected_work_meta_path.read_text(encoding='utf-8')
    
    work_obj = Work()
    work_meta = work_obj.get_work_meta(work_id)
    assert work_meta == expected_work_meta

