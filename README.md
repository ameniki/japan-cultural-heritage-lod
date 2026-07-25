# 日本の世界文化遺産LOD

セマンティックWebの講義で学んだRDF、Turtle、URI、外部データとのリンクを確認するために作成した小規模なLODです。

日本の世界文化遺産から次の5件を例として選びました。

- 姫路城
- 法隆寺地域の仏教建造物
- 厳島神社
- 原爆ドーム
- 佐渡島の金山

## 公開URL

- LOD（Turtle）  
  <https://ameniki.github.io/japan-cultural-heritage-lod/japan-cultural-heritage.ttl>
- GitHub Pages  
  <https://ameniki.github.io/japan-cultural-heritage-lod/>

## 作成したデータ

5件の文化遺産を `ex:WorldHeritageSite` クラスのインスタンスとして記述しました。
それぞれに日本語名、都道府県、世界遺産登録年を付けています。

また、`owl:sameAs` を使ってWikidataのURIと結び付けました。
これにより、このLODから外部のデータへたどることができます。

例:

```turtle
ex:himejiCastle a ex:WorldHeritageSite ;
    rdfs:label "姫路城"@ja ;
    schema:addressRegion "兵庫県"@ja ;
    ex:registrationYear "1993"^^xsd:gYear ;
    owl:sameAs <https://www.wikidata.org/entity/Q188754> .
```

## ファイル

- `japan-cultural-heritage.ttl`: 作成したLOD
- `queries/example.rq`: 文化遺産名と登録年を取得するSPARQLクエリ
- `index.html`: GitHub Pagesの簡単な案内ページ

## 出典とライセンス

- 外部リンク先: [Wikidata](https://www.wikidata.org/)
- 登録年の確認: [UNESCO World Heritage Centre](https://whc.unesco.org/)
- ライセンス: [CC0 1.0 Universal](LICENSE)

## 生成AIの利用

Turtleの記述、READMEの整理、GitHubでの公開作業にOpenAI Codexを利用しました。
作成後にTurtleの構文と公開URLを確認しています。
