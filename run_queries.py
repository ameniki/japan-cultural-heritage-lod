#!/usr/bin/env python3
"""queries/ 以下のSPARQLクエリをLODに対して実行し、結果を表示する。"""

from pathlib import Path

from rdflib import Graph

ROOT = Path(__file__).resolve().parent


def main() -> None:
    graph = Graph()
    graph.parse(ROOT / "japan-cultural-heritage.ttl", format="turtle")

    for path in sorted((ROOT / "queries").glob("*.rq")):
        print(f"===== {path.name}")
        result = graph.query(path.read_text(encoding="utf-8"))
        print("\t".join(str(v) for v in result.vars))
        for row in result:
            print("\t".join(str(value) for value in row))
        print()


if __name__ == "__main__":
    main()
