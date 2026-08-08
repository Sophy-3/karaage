import streamlit as st
from supabase import Client, create_client


st.set_page_config(
    page_title="からあげ図鑑",
    page_icon="🍗",
    layout="centered",
)

st.session_state.setdefault("karaage_rows", None)
st.session_state.setdefault("karaage_count", 0)

with st.container(horizontal_alignment="center"):
    st.title("からあげ図鑑", text_alignment="center")
    st.caption("お気に入りのからあげに出会うための、とっておきの図鑑", text_alignment="center")

st.space("medium")

with st.container(border=True):
    st.subheader(":material/menu_book: ただいま準備中")
    st.write("まもなく、いろいろなからあげを紹介していきます。お楽しみに！")


@st.cache_resource
def get_supabase_client() -> Client:
    return create_client(
        st.secrets["supabase"]["url"],
        st.secrets["supabase"]["key"],
    )


def display_karaage_cards(rows: list[dict]) -> None:
    if not rows:
        with st.container(border=True, horizontal_alignment="center"):
            st.markdown(":orange-badge[はじめての一品を待っています]")
            st.subheader(":material/restaurant: まだ、からあげは登録されていません")
            st.caption("登録されたら、ここにおいしそうなからあげが並びます。")
        return

    st.subheader(":material/favorite: からあげコレクション")
    st.caption(f"{len(rows)} 件のからあげを見つけました。")

    title_columns = ("name", "title", "shop_name", "store_name")
    for number, row in enumerate(rows, start=1):
        title = next(
            (str(row[column]) for column in title_columns if row.get(column)),
            f"からあげ #{number}",
        )

        with st.container(border=True):
            st.markdown(f":orange-badge[からあげ #{number}]")
            st.subheader(title)
            for column, value in row.items():
                if column in title_columns and str(value) == title:
                    continue

                label = column.replace("_", " ").capitalize()
                st.caption(label)
                if isinstance(value, (dict, list)):
                    st.json(value, expanded=False)
                else:
                    st.write(value if value is not None else "―")


st.space("small")
with st.container(border=True):
    st.subheader(":material/cloud_done: Supabase接続")
    st.caption("からあげデータベースとの接続を確認できます。")

    if st.button("接続を確認する", type="primary", icon=":material/link:"):
        try:
            response = get_supabase_client().table("karaage").select(
                "*", count="exact"
            ).execute()
            st.session_state["karaage_rows"] = response.data
            st.session_state["karaage_count"] = response.count or 0
            st.success(
                f"接続できました。karaage テーブルには {st.session_state['karaage_count']} 件のデータがあります。",
                icon=":material/check_circle:",
            )
        except Exception as error:
            st.session_state["karaage_rows"] = None
            st.error(
                "Supabaseへの接続を確認できませんでした。URL・キー・RLS設定を確認してください。",
                icon=":material/error:",
            )
            st.caption(f"詳細: {error}")


if st.session_state["karaage_rows"] is not None:
    st.space("small")
    display_karaage_cards(st.session_state["karaage_rows"])
