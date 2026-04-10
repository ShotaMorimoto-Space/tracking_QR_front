import streamlit as st
import uuid
import pandas as pd
import requests
import os

def generate_uids_ui():
    st.header("UID一括生成フォーム")

    zebra_id = st.text_input("案件ID（zebra_id）")
    campaign_name = st.text_input("キャンペーン名（campaign_name）")
    target_url = st.text_input("ターゲットURL（httpsから）")
    slug_prefix = st.text_input("企業名やサービス名（URLに含める短縮名）") 
    num_uids = st.number_input("発行するUID数", min_value=1, value=10, step=1)

    if st.button("UIDを生成して登録"):
        if not (zebra_id and campaign_name and target_url and slug_prefix):
            st.error("すべての項目を入力してください。")
            return

        logs = []
        for i in range(1, num_uids + 1):
            uid = uuid.uuid4().hex
            logs.append({
                "client_id": i,
                "zebra_id": zebra_id,
                "campaign_name": campaign_name,
                "uid": uid,
                "target_url": target_url,
                "slug_prefix": slug_prefix
            })

        backend_base_url = os.getenv(
            "BACKEND_BASE_URL",
            "https://qr-tracking-dba2gxd0gzd7a7h6.koreacentral-01.azurewebsites.net",
        ).rstrip("/")
        public_base_url = (os.getenv("PUBLIC_BASE_URL") or "https://tr.fujiplus.jp").rstrip("/")

        api_key = os.getenv("BACKEND_API_KEY")
        headers = {"X-API-Key": api_key} if api_key else {}

        # 🚀 一括登録（POST /log/bulk）
        response = requests.post(
            f"{backend_base_url}/bulk_log",
            json=logs,
            headers=headers,
            timeout=15,
        )

        if response.status_code != 200:
            st.error("一括登録に失敗しました。")
            return

        results = response.json()

        uid_list = []
        for log, result in zip(logs, results):
            uid_url = f"{public_base_url}/track?uid={log['uid']}"
            slug_url = f"{public_base_url}/track/{result['slug']}"

            uid_list.append({
                "client_id": log["client_id"],
                "zebra_id": log["zebra_id"],
                "campaign_name": log["campaign_name"],
                "uid": log["uid"],
                "short": result["slug"],
                "uid_url": uid_url,
                "short_url": slug_url,
                "target_url": log["target_url"],
            })

        st.success(f"{len(uid_list)}件のUIDを登録しました！")

        df = pd.DataFrame(uid_list)
        st.subheader("作成されたUIDリスト")
        st.dataframe(df)

        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="CSVファイルをダウンロード",
            data=csv,
            file_name="uid_list.csv",
            mime="text/csv"
        )
