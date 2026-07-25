# 日本の世界文化遺産LOD

Wikidataのオープンデータを基に、日本に関係する世界文化遺産をRDFとして整理したLinked Open Dataです。

## 公開URL

- RDF（Turtle）: <https://ameniki.github.io/japan-cultural-heritage-lod/japan-cultural-heritage.ttl>
- 案内ページ: <https://ameniki.github.io/japan-cultural-heritage-lod/>

## 収録内容

- 世界文化遺産: 21件
- 世界遺産評価基準: 6件（文化遺産基準 (i)〜(vi)）
- 主な情報:
  - 日本語名称
  - UNESCO世界遺産ID
  - 世界遺産評価基準
  - Wikidata上の同一リソース
  - UNESCO公式ページ
  - Wikidataに登録された代表座標

## LODとしての設計

各遺産には、GitHub Pagesで参照できるHTTP URIを付与しています。

```text
https://ameniki.github.io/japan-cultural-heritage-lod/
japan-cultural-heritage.ttl#site-Q188754
```

外部データとの接続には次の語彙を利用しています。

- `owl:sameAs`: Wikidata上の同一リソース
- `rdfs:seeAlso`: UNESCO World Heritage Centreの個別ページ
- `dct:source`: データの出典
- `wgs:lat` / `wgs:long`: WGS84の緯度・経度

これにより、文化遺産名の一覧にとどまらず、評価基準を介した比較や、Wikidata・UNESCOの追加情報への連携ができます。

## ファイル

| ファイル | 内容 |
|---|---|
| `japan-cultural-heritage.ttl` | 公開するRDFデータ |
| `generate_lod.py` | WikidataからRDFを生成するRDFLibプログラム |
| `verify_lod.py` | 構文と必須関係を検証するプログラム |
| `data/wikidata-sites.json` | 生成時に取得したSPARQL結果 |
| `queries/cultural-heritage.rq` | データ抽出用SPARQL |
| `queries/example.rq` | 生成したLODに対する検索例 |

## 再生成と検証

Python 3と[`uv`](https://docs.astral.sh/uv/)を利用する場合:

```bash
uv venv
uv pip install -r requirements.txt
.venv/bin/python generate_lod.py
.venv/bin/python verify_lod.py
```

検証成功時は `validation=PASS` と、遺産数・評価基準数・トリプル数が表示されます。

## データ源とライセンス

- データ源: [Wikidata](https://www.wikidata.org/)
- Wikidataのデータライセンス: [CC0 1.0](https://www.wikidata.org/wiki/Wikidata:Licensing)
- 本リポジトリ: [CC0 1.0 Universal](LICENSE)

抽出条件は、所在地の国が日本、世界遺産に指定されている、UNESCO IDを持つ、文化遺産基準 (i)〜(vi) のいずれかを持つ、の4点です。

## データ上の注意

- 内容は2026年7月25日に取得したWikidataのスナップショットです。
- シリアル・トランスナショナル遺産の座標は、個々の構成資産ではなくWikidataに登録された代表座標の場合があります。
- WikidataのUNESCO IDに `rev` が含まれる場合、UNESCO公式ページへのリンクでは数字部分を使用しています。

## 生成AIの利用

このLODの設計、生成プログラム、READMEの作成にはOpenAI Codexを利用しました。生成結果について、RDFLibによる構文解析、件数、必須リンク、評価基準との関係を検証しています。
