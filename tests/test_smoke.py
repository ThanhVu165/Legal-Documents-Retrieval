import importlib
import importlib.metadata
import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_package_metadata():
    package = importlib.import_module("legal_retrieval")
    assert package.__version__ == importlib.metadata.version("legal-retrieval")


@pytest.mark.parametrize("name,keys", [
    ("corpus", {"dataset", "paths", "schema", "cleaning", "chunking", "seed", "output_format"}),
    ("retrieval", {"baseline", "dense", "top_k", "document_aggregation", "scores"}),
    ("training", {"status", "checkpoint", "seed", "hyperparameters", "validation_metric", "paths"}),
])
def test_configs(name, keys):
    config = yaml.safe_load((ROOT / "configs" / f"{name}.yaml").read_text(encoding="utf-8"))
    assert keys <= config.keys()
    if name == "corpus":
        assert config["dataset"]["id"] == "th1nhng0/vietnamese-legal-documents"
        assert config["dataset"]["revision"] is None
        assert config["schema"]["id_field"] is None
    elif name == "retrieval":
        assert config["baseline"] == "bm25"
        assert all(isinstance(k, int) and k > 0 for k in config["top_k"])
        assert config["scores"] == {"bm25": "lexical_score", "dense": "cosine_similarity"}
    else:
        assert config["status"] == "proposed_not_run"
        assert config["hyperparameters"]["learning_rate"] > 0


def test_scaffold_imports():
    for name in (
        "data.cleaning", "data.segmentation", "data.chunking", "retrieval.bm25",
        "retrieval.dense", "retrieval.search_service", "models.train_bkai",
        "evaluation.metrics", "evaluation.error_analysis", "app.highlighting", "app.feedback", "utils",
    ):
        assert importlib.import_module(f"legal_retrieval.{name}")


def test_environment_checker():
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/check_environment.py")],
        capture_output=True, text=True, check=True,
    )
    assert "Python" in result.stdout
    assert "GPU" in result.stdout


def test_notebook():
    notebook = json.loads((ROOT / "notebooks/colab_setup.ipynb").read_text(encoding="utf-8"))
    assert notebook["nbformat"] == 4
    assert notebook["cells"]
    for cell in notebook["cells"]:
        if cell["cell_type"] == "code":
            compile("".join(cell["source"]), "colab_setup.ipynb", "exec")
