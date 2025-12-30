from codeatlas.patch_skel import patch_skeleton


def test_patch_skeleton_replace_symbol():
    pkt = patch_skeleton(path="x.py", qualname="A.m")
    assert pkt["v"] == 1
    assert pkt["ops"][0]["op"] == "replace_symbol"
    assert pkt["ops"][0]["qualname"] == "A.m"


def test_patch_skeleton_replace_file():
    pkt = patch_skeleton(path="x.txt", qualname=None, op="replace_file")
    assert pkt["ops"][0]["op"] == "replace_file"
    assert "content" in pkt["ops"][0]
