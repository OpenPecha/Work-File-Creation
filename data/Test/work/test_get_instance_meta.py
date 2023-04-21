from pathlib import Path
from core.work import Instances


def test_get_instance_meta():
    instance_id = ""
    expected_instance_meta_path = Path("Test") / "work" / "data" / "expected_insatnce_meta.yml"
    expected_instance_meta = expected_instance_meta_path.read_text(encoding='utf-8')
    
    instance_obj = Instances()
    instance_meta = instance_obj.get_instance_meta(instance_id)
    assert instance_meta == expected_instance_meta