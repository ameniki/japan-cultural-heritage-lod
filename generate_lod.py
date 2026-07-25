#!/usr/bin/env python3
"""Wikidataから日本の世界文化遺産LODを生成する。"""

from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, XSD


ROOT = Path(__file__).resolve().parent
ENDPOINT = "https://query.wikidata.org/sparql"
BASE_URL = (
    "https://ameniki.github.io/japan-cultural-heritage-lod/"
    "japan-cultural-heritage.ttl#"
)
DOWNLOAD_URL = (
    "https://ameniki.github.io/japan-cultural-heritage-lod/"
    "japan-cultural-heritage.ttl"
)

EX = Namespace(BASE_URL)
DCAT = Namespace("http://www.w3.org/ns/dcat#")
GEO = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")

CRITERIA = {
    "Q23038972": "世界遺産基準 (i)",
    "Q23038976": "世界遺産基準 (ii)",
    "Q23038977": "世界遺産基準 (iii)",
    "Q23038978": "世界遺産基準 (iv)",
    "Q23038979": "世界遺産基準 (v)",
    "Q23038980": "世界遺産基準 (vi)",
}

SPARQL = """
SELECT
  ?site
  ?siteLabel
  (SAMPLE(?coord) AS ?coordSample)
  (SAMPLE(?unescoId) AS ?unescoIdSample)
  (GROUP_CONCAT(
    DISTINCT STRAFTER(STR(?criterion), "entity/");
    separator=","
  ) AS ?criteria)
WHERE {
  VALUES ?criterion {
    wd:Q23038972 wd:Q23038976 wd:Q23038977
    wd:Q23038978 wd:Q23038979 wd:Q23038980
  }
  ?site
    wdt:P1435 wd:Q9259;
    wdt:P17 wd:Q17;
    wdt:P2614 ?criterion;
    wdt:P757 ?unescoId.
  OPTIONAL { ?site wdt:P625 ?coord. }
  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "ja,en".
    ?site rdfs:label ?siteLabel.
  }
}
GROUP BY ?site ?siteLabel
ORDER BY ?unescoIdSample
""".strip()


def fetch_wikidata() -> dict:
    """Wikidata Query ServiceからSPARQL結果を取得する。"""
    query_url = f"{ENDPOINT}?{urlencode({'query': SPARQL})}"
    request = Request(
        query_url,
        headers={
            "Accept": "application/sparql-results+json",
            "User-Agent": "ameniki-semweb-course-lod/1.0 (academic assignment)",
        },
    )
    with urlopen(request, timeout=60) as response:
        return json.load(response)


def parse_point(value: str) -> tuple[str, str] | None:
    """WikidataのWKT Point(経度 緯度)を分解する。"""
    match = re.fullmatch(r"Point\(([-0-9.]+) ([-0-9.]+)\)", value)
    if not match:
        return None
    longitude, latitude = match.groups()
    return latitude, longitude


def build_graph(results: dict) -> Graph:
    """SPARQL結果からRDFグラフを構築する。"""
    graph = Graph()
    graph.bind("ex", EX)
    graph.bind("dcat", DCAT)
    graph.bind("dct", DCTERMS)
    graph.bind("wgs", GEO, replace=True)
    graph.bind("owl", OWL)
    graph.bind("rdf", RDF)
    graph.bind("rdfs", RDFS)
    graph.bind("xsd", XSD)

    dataset = EX["dataset"]
    distribution = EX["distribution-turtle"]
    site_class = EX["WorldCulturalHeritageSite"]
    criterion_class = EX["WorldHeritageCriterion"]

    graph.add((dataset, RDF.type, DCAT.Dataset))
    graph.add(
        (
            dataset,
            DCTERMS.title,
            Literal("日本の世界文化遺産LOD", lang="ja"),
        )
    )
    graph.add(
        (
            dataset,
            DCTERMS.description,
            Literal(
                "Wikidataの文化遺産基準(i)〜(vi)とUNESCO IDを用いて"
                "抽出した、日本に関係する世界文化遺産のLOD。",
                lang="ja",
            ),
        )
    )
    graph.add((dataset, DCTERMS.issued, Literal("2026-07-25", datatype=XSD.date)))
    graph.add((dataset, DCTERMS.source, URIRef("https://www.wikidata.org/")))
    graph.add(
        (
            dataset,
            DCTERMS.license,
            URIRef("https://creativecommons.org/publicdomain/zero/1.0/"),
        )
    )
    graph.add((dataset, DCAT.distribution, distribution))

    graph.add((distribution, RDF.type, DCAT.Distribution))
    graph.add((distribution, DCAT.downloadURL, URIRef(DOWNLOAD_URL)))
    graph.add((distribution, DCTERMS.format, Literal("text/turtle")))

    graph.add((site_class, RDF.type, RDFS.Class))
    graph.add((site_class, RDFS.label, Literal("世界文化遺産", lang="ja")))
    graph.add((criterion_class, RDF.type, RDFS.Class))
    graph.add((criterion_class, RDFS.label, Literal("世界遺産評価基準", lang="ja")))

    property_specs = {
        EX["unescoId"]: (
            "UNESCO世界遺産ID",
            site_class,
            XSD.string,
            RDF.Property,
        ),
        EX["meetsCriterion"]: (
            "該当する世界遺産評価基準",
            site_class,
            criterion_class,
            OWL.ObjectProperty,
        ),
    }
    for prop, (label, domain, range_, prop_type) in property_specs.items():
        graph.add((prop, RDF.type, prop_type))
        graph.add((prop, RDFS.label, Literal(label, lang="ja")))
        graph.add((prop, RDFS.domain, domain))
        graph.add((prop, RDFS.range, range_))

    for qid, label in CRITERIA.items():
        criterion = EX[f"criterion-{qid}"]
        graph.add((criterion, RDF.type, criterion_class))
        graph.add((criterion, RDFS.label, Literal(label, lang="ja")))
        graph.add(
            (
                criterion,
                OWL.sameAs,
                URIRef(f"https://www.wikidata.org/entity/{qid}"),
            )
        )

    rows = results["results"]["bindings"]
    for row in rows:
        wikidata_url = row["site"]["value"].replace("http://", "https://", 1)
        qid = wikidata_url.rsplit("/", 1)[-1]
        site = EX[f"site-{qid}"]
        unesco_id = row["unescoIdSample"]["value"]
        unesco_number_match = re.match(r"\d+", unesco_id)

        graph.add((site, RDF.type, site_class))
        graph.add((site, RDFS.label, Literal(row["siteLabel"]["value"], lang="ja")))
        graph.add((site, DCTERMS.identifier, Literal(qid)))
        graph.add((site, EX["unescoId"], Literal(unesco_id)))
        graph.add((site, OWL.sameAs, URIRef(wikidata_url)))
        graph.add((site, DCTERMS.source, URIRef(wikidata_url)))

        if unesco_number_match:
            graph.add(
                (
                    site,
                    RDFS.seeAlso,
                    URIRef(
                        "https://whc.unesco.org/en/list/"
                        f"{unesco_number_match.group()}"
                    ),
                )
            )

        for criterion_qid in row["criteria"]["value"].split(","):
            if criterion_qid not in CRITERIA:
                raise ValueError(f"想定外の世界遺産基準: {criterion_qid}")
            graph.add(
                (
                    site,
                    EX["meetsCriterion"],
                    EX[f"criterion-{criterion_qid}"],
                )
            )

        coord = row.get("coordSample", {}).get("value")
        if coord and (point := parse_point(coord)):
            latitude, longitude = point
            graph.add((site, GEO.lat, Literal(latitude, datatype=XSD.decimal)))
            graph.add((site, GEO.long, Literal(longitude, datatype=XSD.decimal)))

    return graph


def main() -> None:
    results = fetch_wikidata()
    rows = results["results"]["bindings"]
    if len(rows) != 21:
        raise RuntimeError(f"想定21件に対して{len(rows)}件取得しました")

    snapshot_path = ROOT / "data" / "wikidata-sites.json"
    snapshot_path.write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    graph = build_graph(results)
    output_path = ROOT / "japan-cultural-heritage.ttl"
    turtle = graph.serialize(format="turtle").rstrip() + "\n"
    output_path.write_text(turtle, encoding="utf-8")

    print(f"generated_sites={len(rows)}")
    print(f"generated_triples={len(graph)}")
    print(f"output={output_path}")


if __name__ == "__main__":
    main()
