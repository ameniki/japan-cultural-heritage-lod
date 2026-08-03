#!/usr/bin/env python3
"""日本の世界文化遺産LODをRDFLibで生成する。

出力: japan-cultural-heritage.ttl

各遺産のWikidata QID、UNESCO世界遺産ID、登録年はWikidata
(https://www.wikidata.org/, CC0) を参照して確認した値を定数として持つ。
"""

from pathlib import Path

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCAT, DCTERMS, OWL, RDF, RDFS, XSD

ROOT = Path(__file__).resolve().parent
TTL_PATH = ROOT / "japan-cultural-heritage.ttl"

BASE = "https://ameniki.github.io/japan-cultural-heritage-lod/japan-cultural-heritage.ttl#"
DOWNLOAD_URL = (
    "https://ameniki.github.io/japan-cultural-heritage-lod/japan-cultural-heritage.ttl"
)

EX = Namespace(BASE)
WD = "https://www.wikidata.org/entity/"
WHC = "https://whc.unesco.org/en/list/"

# 都道府県: ローカル名 -> (ラベル, Wikidata QID)
PREFECTURES = {
    "hyogo": ("兵庫県", "Q130290"),
    "nara": ("奈良県", "Q131287"),
    "hiroshima": ("広島県", "Q617375"),
    "niigata": ("新潟県", "Q132705"),
}

# 世界文化遺産: ローカル名 -> (ラベル, QID, 都道府県, 登録年, UNESCO ID)
SITES = [
    ("himejiCastle", "姫路城", "Q188754", "hyogo", "1993", "661"),
    ("horyuji", "法隆寺地域の仏教建造物", "Q1333799", "nara", "1993", "660"),
    ("itsukushimaShrine", "厳島神社", "Q191763", "hiroshima", "1996", "776"),
    ("genbakuDome", "原爆ドーム", "Q231140", "hiroshima", "1996", "775"),
    ("sadoGoldMine", "佐渡島の金山", "Q127378385", "niigata", "2024", "1698"),
]


def build_graph() -> Graph:
    g = Graph()
    g.bind("ex", EX)
    g.bind("dcat", DCAT)
    g.bind("dct", DCTERMS)
    g.bind("owl", OWL)
    g.bind("rdf", RDF)
    g.bind("rdfs", RDFS)
    g.bind("xsd", XSD)

    # --- データセットのメタデータ ---
    dataset = EX["dataset"]
    g.add((dataset, RDF.type, DCAT.Dataset))
    g.add((dataset, DCTERMS.title, Literal("日本の世界文化遺産LOD", lang="ja")))
    g.add(
        (
            dataset,
            DCTERMS.description,
            Literal(
                "日本の世界文化遺産5件について、所在都道府県・世界遺産登録年・"
                "UNESCO世界遺産IDを記述したLOD。",
                lang="ja",
            ),
        )
    )
    g.add((dataset, DCTERMS.creator, Literal("野口凌", lang="ja")))
    g.add((dataset, DCTERMS.issued, Literal("2026-08-03", datatype=XSD.date)))
    g.add(
        (
            dataset,
            DCTERMS.license,
            URIRef("https://creativecommons.org/publicdomain/zero/1.0/"),
        )
    )
    g.add((dataset, DCTERMS.source, URIRef("https://www.wikidata.org/")))
    g.add((dataset, DCTERMS.source, URIRef("https://whc.unesco.org/")))
    g.add((dataset, DCAT.downloadURL, URIRef(DOWNLOAD_URL)))

    # --- クラス ---
    g.add((EX.CulturalProperty, RDF.type, RDFS.Class))
    g.add((EX.CulturalProperty, RDFS.label, Literal("文化財", lang="ja")))

    g.add((EX.WorldHeritageSite, RDF.type, RDFS.Class))
    g.add((EX.WorldHeritageSite, RDFS.label, Literal("世界文化遺産", lang="ja")))
    g.add((EX.WorldHeritageSite, RDFS.subClassOf, EX.CulturalProperty))

    g.add((EX.Prefecture, RDF.type, RDFS.Class))
    g.add((EX.Prefecture, RDFS.label, Literal("都道府県", lang="ja")))

    # --- プロパティ ---
    g.add((EX.locatedIn, RDF.type, RDF.Property))
    g.add((EX.locatedIn, RDFS.label, Literal("所在都道府県", lang="ja")))
    g.add((EX.locatedIn, RDFS.domain, EX.WorldHeritageSite))
    g.add((EX.locatedIn, RDFS.range, EX.Prefecture))

    g.add((EX.registrationYear, RDF.type, RDF.Property))
    g.add((EX.registrationYear, RDFS.label, Literal("世界遺産登録年", lang="ja")))
    g.add((EX.registrationYear, RDFS.domain, EX.WorldHeritageSite))
    g.add((EX.registrationYear, RDFS.range, XSD.gYear))

    g.add((EX.unescoId, RDF.type, RDF.Property))
    g.add((EX.unescoId, RDFS.label, Literal("UNESCO世界遺産ID", lang="ja")))
    g.add((EX.unescoId, RDFS.domain, EX.WorldHeritageSite))
    g.add((EX.unescoId, RDFS.range, XSD.string))

    # --- 都道府県のインスタンス ---
    for local, (label, qid) in PREFECTURES.items():
        pref = EX[local]
        g.add((pref, RDF.type, EX.Prefecture))
        g.add((pref, RDFS.label, Literal(label, lang="ja")))
        g.add((pref, OWL.sameAs, URIRef(WD + qid)))

    # --- 世界文化遺産のインスタンス ---
    for local, label, qid, pref, year, unesco_id in SITES:
        site = EX[local]
        g.add((site, RDF.type, EX.WorldHeritageSite))
        g.add((site, RDFS.label, Literal(label, lang="ja")))
        g.add((site, EX.locatedIn, EX[pref]))
        g.add((site, EX.registrationYear, Literal(year, datatype=XSD.gYear)))
        g.add((site, EX.unescoId, Literal(unesco_id, datatype=XSD.string)))
        g.add((site, OWL.sameAs, URIRef(WD + qid)))
        g.add((site, RDFS.seeAlso, URIRef(WHC + unesco_id)))

    return g


def main() -> None:
    graph = build_graph()
    graph.serialize(destination=TTL_PATH, format="turtle")
    print(f"wrote {TTL_PATH.name}: {len(graph)} triples")


if __name__ == "__main__":
    main()
