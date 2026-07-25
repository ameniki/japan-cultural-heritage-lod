#!/usr/bin/env python3
"""生成済みLODの構文と必須関係を検証する。"""

from __future__ import annotations

import json
from pathlib import Path

from rdflib import Graph, Namespace
from rdflib.namespace import OWL, RDF, RDFS


ROOT = Path(__file__).resolve().parent
EX = Namespace(
    "https://ameniki.github.io/japan-cultural-heritage-lod/"
    "japan-cultural-heritage.ttl#"
)


def main() -> None:
    ttl_path = ROOT / "japan-cultural-heritage.ttl"
    snapshot_path = ROOT / "data" / "wikidata-sites.json"

    graph = Graph()
    graph.parse(ttl_path, format="turtle")

    sites = set(
        graph.subjects(RDF.type, EX["WorldCulturalHeritageSite"])
    )
    criteria = set(
        graph.subjects(RDF.type, EX["WorldHeritageCriterion"])
    )
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    snapshot_rows = snapshot["results"]["bindings"]

    assert len(sites) == 21, f"文化遺産数が不正: {len(sites)}"
    assert len(criteria) == 6, f"評価基準数が不正: {len(criteria)}"
    assert len(snapshot_rows) == 21, "Wikidataスナップショット件数が不正"

    for site in sites:
        assert list(graph.objects(site, RDFS.label)), f"ラベルなし: {site}"
        same_as = list(graph.objects(site, OWL.sameAs))
        see_also = list(graph.objects(site, RDFS.seeAlso))
        criteria_links = list(graph.objects(site, EX["meetsCriterion"]))
        assert len(same_as) == 1, f"Wikidataリンク不正: {site}"
        assert str(same_as[0]).startswith(
            "https://www.wikidata.org/entity/Q"
        ), f"Wikidataリンク形式不正: {site}"
        assert len(see_also) == 1, f"UNESCOリンク不正: {site}"
        assert str(see_also[0]).startswith(
            "https://whc.unesco.org/en/list/"
        ), f"UNESCOリンク形式不正: {site}"
        assert criteria_links, f"世界遺産基準なし: {site}"
        assert all(
            criterion in criteria for criterion in criteria_links
        ), f"未定義の世界遺産基準: {site}"

    print("validation=PASS")
    print(f"sites={len(sites)}")
    print(f"criteria={len(criteria)}")
    print(f"triples={len(graph)}")
    print(f"snapshot_rows={len(snapshot_rows)}")


if __name__ == "__main__":
    main()
