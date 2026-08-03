# 日本の世界文化遺産LOD

セマンティックWebの講義で学んだRDF、RDFS、URI設計、外部データとのリンクを確認するために作成した小規模なLODです。

日本の世界文化遺産から次の5件を対象としました。

- 姫路城（兵庫県、1993年登録）
- 法隆寺地域の仏教建造物（奈良県、1993年登録）
- 厳島神社（広島県、1996年登録）
- 原爆ドーム（広島県、1996年登録）
- 佐渡島の金山（新潟県、2024年登録）

## 公開URL

- LOD（Turtle）  
  <https://ameniki.github.io/japan-cultural-heritage-lod/japan-cultural-heritage.ttl>
- GitHub Pages  
  <https://ameniki.github.io/japan-cultural-heritage-lod/>

## スキーマ

クラスは3つ、プロパティは3つです。

| 種類 | 名前（`ex:` は上記TTLのフラグメント名前空間） | 説明 |
| --- | --- | --- |
| クラス | `ex:CulturalProperty` | 文化財 |
| クラス | `ex:WorldHeritageSite` | 世界文化遺産（`rdfs:subClassOf ex:CulturalProperty`） |
| クラス | `ex:Prefecture` | 都道府県 |
| プロパティ | `ex:locatedIn` | 所在都道府県（domain: `ex:WorldHeritageSite` / range: `ex:Prefecture`） |
| プロパティ | `ex:registrationYear` | 世界遺産登録年（range: `xsd:gYear`） |
| プロパティ | `ex:unescoId` | UNESCO世界遺産ID（range: `xsd:string`） |

遺産と都道府県の双方に `owl:sameAs` でWikidataのURIを与え、さらに `rdfs:seeAlso` でUNESCO世界遺産センターの該当ページへリンクしています。所在地を文字列ではなく `ex:Prefecture` のインスタンスへのリンクにしたため、都道府県を軸に外部データと接続できます。

例:

```turtle
ex:himejiCastle a ex:WorldHeritageSite ;
    rdfs:label "姫路城"@ja ;
    ex:locatedIn ex:hyogo ;
    ex:registrationYear "1993"^^xsd:gYear ;
    ex:unescoId "661" ;
    owl:sameAs <https://www.wikidata.org/entity/Q188754> ;
    rdfs:seeAlso <https://whc.unesco.org/en/list/661> .
```

## ファイル

- `build_lod.py`: RDFLibでLODを生成するスクリプト
- `verify_lod.py`: 生成したTurtleの構文とクラス・プロパティ構成を検証するスクリプト
- `run_queries.py`: `queries/` のSPARQLクエリを実行するスクリプト
- `japan-cultural-heritage.ttl`: 生成されたLOD（75トリプル）
- `queries/example.rq`: 遺産名・所在都道府県・登録年を取得するクエリ
- `queries/by-prefecture.rq`: 都道府県ごとの件数を集計するクエリ
- `index.html`: GitHub Pagesの案内ページ

## 生成と検証の手順

```bash
python3 -m venv .venv
./.venv/bin/pip install rdflib
./.venv/bin/python build_lod.py    # japan-cultural-heritage.ttl を生成
./.venv/bin/python verify_lod.py   # 構文と件数を検証
./.venv/bin/python run_queries.py  # SPARQLクエリを実行
```

## 出典とライセンス

- Wikidata QID・UNESCO世界遺産ID・登録年の確認: [Wikidata](https://www.wikidata.org/)（CC0 1.0）
- 世界遺産一覧の確認: [UNESCO World Heritage Centre](https://whc.unesco.org/)
- 本データのライセンス: [CC0 1.0 Universal](LICENSE)

## 生成AIの利用

Turtleの記述、スクリプトの作成、READMEの整理、GitHubでの公開作業にOpenAI CodexおよびClaudeを利用しました。生成結果については、RDFLibでのパース、Wikidata APIによるQID・登録年・UNESCO IDの照合、公開URLのHTTPステータス確認を行って妥当性を確認しています。
