"""Khảo sát dataset công khai tại SHA khóa; không xuất dump corpus gốc."""

import argparse
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from legal_retrieval.data.inspection import inspect_dataset  # noqa: E402
from legal_retrieval.data.schema import load_config  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    """Xác minh revision hiện tại/đã khóa và lưu JSON tổng hợp kết quả khảo sát."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/corpus.yaml"))
    parser.add_argument("--output", type=Path, default=Path("results/w01/inspection.json"))
    parser.add_argument("--configs", nargs="+", help="Tên config đã phát hiện cần khảo sát")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        config = load_config(args.config)
        report = inspect_dataset(config["dataset"]["id"], config["dataset"]["revision"],
                                 args.configs or config["dataset"].get("configs"))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        logging.info("Inspection saved: %s", args.output)
        return 0
    except (OSError, ValueError, KeyError) as exc:
        logging.error("Inspection failed: %s", exc)
        return 1


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
