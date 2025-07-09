import streamlit as st
import pandas as pd
import requests

def access_logs_ui():
    st.header("アクセスログ一覧")

    # クエリ条件（任意）
    zebra_id = st.text_input("案件ID（zebra_id）で絞り込み（空白可）")
    campaign_name = st.text_input("キャンペーン名で絞り込み（空白可）")
    target_url = st.text_input("ターゲットURLで絞り込み（空白可）")

    # クエリパラメータ組み立て
    params = {}
    if zebra_id:
        params["zebra_id"] = zebra_id
    if campaign_name:
        params["campaign_name"] = campaign_name
    if target_url:
       params["target_url"] = target_url

    if st.button("ログ取得"):
        response = requests.get("https://qr-tracking-dba2gxd0gzd7a7h6.koreacentral-01.azurewebsites.net/log", params=params)

        if response.status_code != 200:
            st.error("アクセスログの取得に失敗しました。")
            return

        logs = response.json()

        if not logs:
            st.info("該当するアクセス記録はありません。")
            return

        # Pandas DataFrame に変換
        df = pd.DataFrame(logs)

                # ✅ 表示順の調整
        desired_order = [
            "id", "zebra_id", "campaign_name", "target_url", "uid",
            "access_count", "last_accessed_at"
        ]
        df = df[desired_order]


        # 表示
        st.dataframe(df)
        # CSV出力
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="アクセスログをCSVでダウンロード",
            data=csv,
            file_name="access_logs.csv",
            mime="text/csv"
        )

        # Excel出力
        import io
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name="AccessLogs")

        st.download_button(
            label="アクセスログをExcelでダウンロード",
            data=excel_buffer.getvalue(),
            file_name="access_logs.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
         )
