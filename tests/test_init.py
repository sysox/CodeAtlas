from pathlib import Path

from codeatlas.store_init import init_workspace


def test_init_creates_atlas_layout(tmp_path: Path):
    ap = init_workspace(tmp_path)
    assert ap.atlas_dir.exists()
    assert ap.cfg_path.exists()
    assert ap.tree_dir.exists()
    assert ap.nodes_path.exists()
    assert ap.index_dir.exists()
    assert ap.paths_index_path.exists()
    assert ap.fingerprints_path.exists()
