import streamlit as st
import pandas as pd
import requests
import altair as alt

def report_dashboard_ui():
    st.header("レポートダッシュボード")

    zebra_id = st.text_input("案件ID（zebra_id）で絞り込み（空白可）")
    campaign_name = st.text_input("キャンペーン名で絞り込み（空白可）")
    target_url = st.text_input("ターゲットURLで絞り込み（空白可）")

    params = {}
    if zebra_id:
        params["zebra_id"] = zebra_id
    if campaign_name:
        params["campaign_name"] = campaign_name
    if target_url:
        params["target_url"] = target_url

    if st.button("レポート生成"):
        response = requests.get("https://qr-tracking-dba2gxd0gzd7a7h6.koreacentral-01.azurewebsites.net/log", params=params)

        if response.status_code != 200:
            st.error("アクセスログの取得に失敗しました。")
            return

        logs = response.json()

        if not logs:
            st.info("該当するアクセス記録がありません。")
            return

        df = pd.DataFrame(logs)

        # ---- 🧮 指標の計算 ----
        total_uids = len(df)
        total_access = df["access_count"].sum()
        accessed_uid_count = df[df["access_count"] > 0].shape[0]
        conversion_rate = (accessed_uid_count / total_uids) * 100 if total_uids > 0 else 0

        st.subheader("DM Station あしあと追跡レポート")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("合計ID数", total_uids)
        col2.metric("アクセス合計数", total_access)
        col3.metric("アクセスされたID数", accessed_uid_count)
        col4.metric("CV率（％）", f"{conversion_rate:.2f}%")

        # ---- 日別アクセス数グラフ ----
        if "last_accessed_at" in df.columns:
            df["last_accessed_at"] = pd.to_datetime(df["last_accessed_at"], errors="coerce")
            daily_summary = (
                df.dropna(subset=["last_accessed_at"])
                .groupby(df["last_accessed_at"].dt.date)
                .size()
                .reset_index(name="アクセス数")
            )

            st.subheader("日別アクセス数")
            chart = alt.Chart(daily_summary).mark_bar().encode(
                x=alt.X("last_accessed_at:T", title="日付"),
                y=alt.Y("アクセス数:Q"),
                tooltip=["last_accessed_at", "アクセス数"]
            ).properties(height=300)

            st.altair_chart(chart, use_container_width=True)

        # ---- 🧾 全件表示＋ダウンロード ----
        st.subheader("📄 アクセスログ一覧")
        st.dataframe(df)

        csv = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="CSVダウンロード",
            data=csv,
            file_name="access_report.csv",
            mime="text/csv"
        )
