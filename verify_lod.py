#!/usr/bin/env python3
"""生成したLODの構文と内容を検証する。"""

from pathlib import Path

from rdflib import Graph, Namespace
from rdflib.namespace import OWL, RDF, RDFS

ROOT = Path(__file__).resolve().parent
TTL_PATH = ROOT / "japan-cultural-heritage.ttl"
EX = Namespace(
    "https://ameniki.github.io/japan-cultural-heritage-lod/japan-cultural-heritage.ttl#"
)


def main() -> None:
    g = Graph()
    g.parse(TTL_PATH, format="turtle")  # 構文エラーがあればここで例外

    classes = set(g.subjects(RDF.type, RDFS.Class))
    properties = set(g.subjects(RDF.type, RDF.Property))
    sites = set(g.subjects(RDF.type, EX.WorldHeritageSite))
    prefectures = set(g.subjects(RDF.type, EX.Prefecture))
    same_as = list(g.subject_objects(OWL.sameAs))

    print(f"トリプル数        : {len(g)}")
    print(f"クラス数          : {len(classes)}")
    print(f"プロパティ数      : {len(properties)}")
    print(f"世界文化遺産の件数: {len(sites)}")
    print(f"都道府県の件数    : {len(prefectures)}")
    print(f"owl:sameAsの本数  : {len(same_as)}")

    assert len(classes) == 3, "クラス数が想定と異なる"
    assert len(properties) == 3, "プロパティ数が想定と異なる"
    assert len(sites) == 5, "世界文化遺産の件数が想定と異なる"
    assert len(prefectures) == 4, "都道府県の件数が想定と異なる"
    assert len(same_as) == 9, "owl:sameAsの本数が想定と異なる"

    # 全ての遺産が所在都道府県を持ち、そのリンク先がex:Prefectureであること
    for site in sites:
        pref = g.value(site, EX.locatedIn)
        assert pref is not None, f"{site} に ex:locatedIn がない"
        assert (pref, RDF.type, EX.Prefecture) in g, f"{pref} が ex:Prefecture でない"

    print("検証OK: すべてのチェックを通過した")


if __name__ == "__main__":
    main()
