# 進め方


PostgreSQL経験があるなら、**「見る」「検索する」だけなら1〜2時間で動くレベル**です。

## 作るもの

画面

```text
からあげ図鑑

検索: [グルクン      ]

-----------------
グルクン唐揚げ
食材: 魚

フグ唐揚げ
食材: 魚
-----------------
```

構成

```text
Streamlit
   ↓
Supabase
```

---

# ① Supabaseアカウント作成

[Supabase](https://supabase.com?utm_source=chatgpt.com)

* GitHubでログイン
* New Project
* Project Name

例

```text
karaage-zukan
```

* パスワード設定

作成完了まで数分待つ

---

# ② テーブル作成

左メニュー

```text
Table Editor
```

↓

```text
Create a new table
```

テーブル名

```text
karaage
```

カラム

| 項目          | 型    |
| ----------- | ---- |
| id          | int8 |
| name        | text |
| ingredient  | text |
| description | text |

idは

```text
Primary Key
Identity
```

にする

---

# ③ サンプルデータ投入

SQL Editor

```sql
insert into karaage
(name, ingredient, description)
values
('グルクン唐揚げ', '魚', '沖縄の定番'),
('フグ唐揚げ', '魚', '山口名物'),
('ごぼう唐揚げ', '野菜', '居酒屋で人気');
```

実行

---

# ④ APIキー取得

左下

```text
Settings
```

↓

```text
API
```

取得するもの

```text
Project URL
anon public key
```

例

```text
https://xxxxx.supabase.co

eyJhb...
```

---

# ⑤ Streamlit準備

インストール

```bash
pip install streamlit
pip install supabase
```

---

# ⑥ app.py作成

```python
import streamlit as st
from supabase import create_client

url = "SupabaseのURL"
key = "anon key"

supabase = create_client(url, key)

st.title("からあげ図鑑")

keyword = st.text_input("検索")

query = supabase.table("karaage").select("*")

if keyword:
    query = query.ilike("name", f"%{keyword}%")

result = query.execute()

for item in result.data:
    st.subheader(item["name"])
    st.write(f"食材: {item['ingredient']}")
    st.write(item["description"])
    st.divider()
```

---

# ⑦ 実行

```bash
streamlit run app.py
```

ブラウザで表示

---

# ⑧ 画像

次に追加したくなったら

Supabase Storageを使う

```text
karaage/
 ├ グルクン.jpg
 ├ フグ.jpg
```

みたいに保存できます。

---

# MVP完成

この時点で

✅ Supabase接続

✅ 一覧表示

✅ 名前検索

ができています。

---

さらに、からあげ図鑑向けなら最初からテーブルを少しだけ拡張しておくと後が楽です。

```sql
create table karaage (
    id bigint generated always as identity primary key,
    name text not null,
    ingredient text not null,
    category text,
    region text,
    description text
);
```

例えば

| name    | ingredient | category | region |
| ------- | ---------- | -------- | ------ |
| グルクン唐揚げ | 魚          | 海水魚      | 沖縄     |
| フグ唐揚げ   | 魚          | 海水魚      | 山口     |
| ごぼう唐揚げ  | 野菜         | 根菜       | 全国     |

としておくと、将来

* 魚だけ表示
* 沖縄だけ表示
* 野菜だけ表示

の絞り込みが簡単になります。まずはここまで作れば、「からあげ図鑑」の第一歩として十分です。



## 第3段階
- ユーザー登録
- 写真投稿
- みんなで図鑑作成
本格運用


# 作りたいもの


## ① 唐揚げ図鑑（みんなのデータ）

全ユーザーで共有する図鑑です。

例

| 名前      | 食材   | 地域 |
| ------- | ---- | -- |
| グルクン唐揚げ | 魚    | 沖縄 |
| フグ唐揚げ   | 魚    | 山口 |
| ごぼう唐揚げ  | 野菜   | 全国 |
| タコ唐揚げ   | 軟体動物 | 全国 |

登録内容

* 名前
* 食材分類
* 地域
* 写真
* 説明
* 投稿者

イメージとしてはWikipediaに近いです。

---

## ② マイコレクション（食べた記録）

ユーザーごとの記録です。

例えば

### グルクン唐揚げ

✅ 食べた

場所：沖縄県石垣島

日付：2026/7/1

評価：★★★★★

写真あり

---

### フグ唐揚げ

❌ 未捕獲

こんな感じです。

ポケモン図鑑の

* 発見済み
* 未発見

に近いですね。

---

## ③ マイ登録唐揚げ

自分が発見した唐揚げです。

例えば

「カボチャの唐揚げ」

が図鑑になかった。

↓

自分が登録。

↓

図鑑に採用。

↓

発見者として名前が残る。

これはゲーム性が出ます。

---

私はさらに、

## ④ コレクション率

を入れたいです。

例えば

* 全図鑑 500種
* 発見済み 120種

達成率24%

みたいな。

---

## ⑤ バッジ機能

例

🐔 鶏マスター
（鶏系20種達成）

🐟 魚類マスター
（魚系30種達成）

🥬 野菜ハンター
（野菜系15種達成）

🌴 沖縄コンプリート
（沖縄唐揚げ10種達成）

---

## 最初のMVP（試作品）

実は最初から全部作る必要はありません。

まずは

### 図鑑

* 名前
* 食材
* 写真

### マイコレクション

* 食べた
* 写真
* 日付

だけで十分です。

例えば

```
グルクン唐揚げ
食べた！

2026/07/08
石垣島
★★★★★
```

が登録できれば成立します。

---

私はこのアプリの本質は、

**「唐揚げを記録すること」ではなく、「未知の唐揚げを探しに行きたくなること」**

だと思います。

その意味では、

1. みんなで図鑑を作る
2. 自分で食べてコレクトする
3. 達成率が上がる

の3本柱が中心になります。これだけでも十分に一つのサービスとして成立する設計です。
