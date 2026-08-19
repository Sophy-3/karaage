"""みんなのからあげ図鑑 - Phase 1."""
from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

import streamlit as st
import streamlit.components.v1 as components
from supabase import Client, create_client

APP_TITLE = "みんなのからあげ図鑑"
PAGES = ["ホーム", "みんなのからあげ図鑑", "からあげを登録する", "マイコレクション", "マイページ"]

st.set_page_config(page_title=APP_TITLE, page_icon="🍗", layout="wide")


@st.cache_resource
def client() -> Client:
    return create_client(st.secrets["supabase"]["url"], st.secrets["supabase"]["key"])


def init_state() -> None:
    for key, value in {"user_id": None, "user_name": None, "page": "ホーム", "detail_id": None}.items():
        st.session_state.setdefault(key, value)


def category_name(row: dict[str, Any]) -> str:
    value = row.get("categories") or row.get("category")
    if isinstance(value, dict):
        return str(value.get("name") or "その他")
    if isinstance(value, list) and value:
        return str(value[0].get("name") or "その他")
    return str(value or "その他")


def get_data() -> tuple[list[dict[str, Any]], list[dict[str, Any]], set[str]]:
    db = client()
    categories = db.table("categories").select("id,name").order("name").execute().data
    karaage = db.table("karaage").select("id,name,recipe_url,created_at,created_by,categories(name)").order("created_at", desc=True).execute().data
    collected = db.table("user_karaage").select("karaage_id").eq("user_id", st.session_state.user_id).execute().data
    return categories, karaage, {str(item["karaage_id"]) for item in collected}


def stats(total: int, count: int) -> tuple[float, int, int]:
    return ((count / total * 100) if total else 0.0, count // 10, 10 - count % 10 if count % 10 else 10)


def nav(page: str, detail_id: str | None = None) -> None:
    st.session_state.page = page
    if detail_id is not None:
        st.session_state.detail_id = detail_id


def metrics(total: int, count: int) -> None:
    rate, stamps, next_stamp = stats(total, count)
    cols = st.columns(4)
    cols[0].metric("図鑑登録数", f"{total} 種類")
    cols[1].metric("マイコレクション", f"{count} 種類")
    cols[2].metric("達成率", f"{rate:.1f}%")
    cols[3].metric("スタンプ", f"{stamps} 個")
    st.caption(f"次のスタンプまであと {next_stamp} 種類")


def login() -> None:
    st.title(APP_TITLE)
    st.caption("みんなでからあげを登録し、作ったからあげをマイコレクションに集めるアプリです。")
    with st.container(border=True):
        st.subheader("はじめる")
        with st.form("login"):
            name = st.text_input("ユーザー名", max_chars=30, placeholder="例：からあげ太郎")
            submit = st.form_submit_button("はじめる", type="primary")
        if submit:
            name = name.strip()
            if not name:
                st.error("ユーザー名を入力してください。")
                return
            try:
                found = client().table("users").select("id,name").eq("name", name).limit(1).execute().data
                user = found[0] if found else client().table("users").insert({"name": name}).execute().data[0]
                st.session_state.user_id, st.session_state.user_name = str(user["id"]), user["name"]
                st.rerun()
            except Exception as error:
                st.error("ユーザー情報を保存できませんでした。Supabase の設定を確認してください。")
                st.caption(str(error))


def sidebar() -> None:
    with st.sidebar:
        st.title("🍗 みんなのからあげ図鑑")
        st.caption(f"こんにちは、{st.session_state.user_name}さん")
        selected = st.radio("メニュー", PAGES, index=PAGES.index(st.session_state.page))
        if selected != st.session_state.page:
            nav(selected)
            st.rerun()
        if st.button("ログアウト", use_container_width=True):
            st.session_state.user_id = st.session_state.user_name = None
            nav("ホーム")
            st.rerun()


def collect(karaage_id: str, is_collected: bool) -> None:
    if is_collected:
        st.success("このからあげはマイコレクションに登録済みです。", icon="✅")
    elif st.button("作ってコレクトする", key=f"collect_{karaage_id}", type="primary", icon=":material/check_circle:"):
        try:
            client().table("user_karaage").insert({"user_id": st.session_state.user_id, "karaage_id": karaage_id}).execute()
            st.success("マイコレクションに追加しました！")
            st.rerun()
        except Exception as error:
            st.error("コレクションへの追加に失敗しました。")
            st.caption(str(error))


def home(rows: list[dict[str, Any]], collected: set[str]) -> None:
    st.title(APP_TITLE)
    st.write("今日はどのからあげをコレクションする？からあげを登録してみんなで図鑑を育てよう。作ったからあげは自分のコレクション！")
    metrics(len(rows), len(collected))
    one, two = st.columns(2)
    if one.button("からあげを探す", type="primary", use_container_width=True):
        nav("みんなのからあげ図鑑"); st.rerun()
    if two.button("からあげを登録する", use_container_width=True):
        nav("からあげを登録する"); st.rerun()
    st.divider(); st.subheader("最近登録されたからあげ")
    for item in rows[:3]:
        with st.container(border=True):
            st.subheader(item["name"]); st.caption(f"カテゴリー：{category_name(item)}")
            if st.button("詳細を見る", key=f"home_{item['id']}"):
                nav("みんなのからあげ図鑑", str(item["id"])); st.rerun()


def catalog(rows: list[dict[str, Any]], categories: list[dict[str, Any]], collected: set[str]) -> None:
    st.title("みんなのからあげ図鑑")
    search, category = st.columns([2, 1])
    query = search.text_input("からあげを検索", placeholder="例：グルクン")
    chosen = category.selectbox("カテゴリー", ["すべて"] + [x["name"] for x in categories])
    filtered = [x for x in rows if (not query or query.casefold() in x["name"].casefold()) and (chosen == "すべて" or category_name(x) == chosen)]
    st.caption(f"{len(filtered)} 種類を表示中")
    for item in filtered:
        done = str(item["id"]) in collected
        with st.container(border=True):
            left, right = st.columns([4, 1]); left.subheader(item["name"]); right.write("✅ コレクト済み" if done else "○ 未コレクト")
            st.caption(f"カテゴリー：{category_name(item)}")
            a, b = st.columns(2)
            if a.button("詳細を見る", key=f"detail_{item['id']}"):
                st.session_state.detail_id = str(item["id"]); st.rerun()
            if item.get("recipe_url"):
                b.link_button("レシピを見る", item["recipe_url"], key=f"recipe_{item['id']}")
    if st.session_state.detail_id:
        item = next((x for x in rows if str(x["id"]) == str(st.session_state.detail_id)), None)
        st.session_state.detail_id = None
        if item:
            st.divider()
            st.markdown('<div id="karaage-detail"></div>', unsafe_allow_html=True)
            st.subheader(item["name"]); st.write(f"カテゴリー：{category_name(item)}")
            st.link_button("レシピを見る", item["recipe_url"], icon=":material/open_in_new:")
            collect(str(item["id"]), str(item["id"]) in collected)
            components.html(
                """
                <script>
                  window.setTimeout(() => {
                    window.parent.document
                      .getElementById("karaage-detail")
                      ?.scrollIntoView({ behavior: "smooth", block: "start" });
                  }, 100);
                </script>
                """,
                height=0,
            )


def register(categories: list[dict[str, Any]]) -> None:
    st.title("からあげを登録する")
    st.caption("レシピ本文は転載せず、レシピURLを登録します。")
    if not categories:
        st.warning("カテゴリがありません。supabase_schema.sql の初期データを登録してください。"); return
    mapping = {x["name"]: x["id"] for x in categories}
    with st.form("register", clear_on_submit=True):
        name = st.text_input("からあげ名 *", max_chars=100)
        category = st.selectbox("カテゴリ *", list(mapping))
        url = st.text_input("レシピURL *", placeholder="https://example.com/recipe")
        submit = st.form_submit_button("みんなのからあげ図鑑に登録する", type="primary")
    if submit:
        parsed = urlparse(url.strip())
        if not name.strip() or not url.strip(): st.error("からあげ名とレシピURLは必須です。"); return
        if parsed.scheme not in {"http", "https"} or not parsed.netloc: st.error("有効な http(s) URL を入力してください。"); return
        try:
            client().table("karaage").insert({"name": name.strip(), "category_id": mapping[category], "recipe_url": url.strip(), "created_by": st.session_state.user_id}).execute()
            st.success("みんなのからあげ図鑑に登録しました！")
        except Exception as error:
            st.error("からあげを登録できませんでした。"); st.caption(str(error))


def my_catalog(rows: list[dict[str, Any]], collected: set[str]) -> None:
    st.title("マイコレクション"); metrics(len(rows), len(collected))
    for item in rows:
        with st.container(border=True):
            st.write(f"{'✅' if str(item['id']) in collected else '○'}  **{item['name']}**")
            st.caption(f"カテゴリー：{category_name(item)}")


def my_page(rows: list[dict[str, Any]], collected: set[str]) -> None:
    st.title("マイページ"); st.subheader(f"{st.session_state.user_name}さんのコレクション"); metrics(len(rows), len(collected))
    left, right = st.columns(2)
    if left.button("マイコレクションを見る", use_container_width=True): nav("マイコレクション"); st.rerun()
    if right.button("からあげを登録する", use_container_width=True): nav("からあげを登録する"); st.rerun()


def main() -> None:
    init_state()
    if not st.session_state.user_id: login(); return
    sidebar()
    try:
        categories, rows, collected = get_data()
    except Exception as error:
        st.error("図鑑データを読み込めませんでした。Supabase のテーブルと RLS ポリシーを確認してください。")
        st.code(str(error), language="text"); return
    page = st.session_state.page
    if page == "ホーム":
        home(rows, collected)
    elif page == "みんなのからあげ図鑑":
        catalog(rows, categories, collected)
    elif page == "からあげを登録する":
        register(categories)
    elif page == "マイコレクション":
        my_catalog(rows, collected)
    else:
        my_page(rows, collected)


if __name__ == "__main__": main()
