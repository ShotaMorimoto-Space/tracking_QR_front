import streamlit as st
import requests
from components.generate_uids import generate_uids_ui
from components.access_logs import access_logs_ui
from components.report_dashboard import report_dashboard_ui

st.title("DMトラッキング管理システム")

# ✅ 起動時に一度だけ実行されるウォームアップ処理
@st.cache_resource
def warm_up_backend():
    try:
        dummy_uid = "warmup-dummy"
        response = requests.post(
            "https://qr-tracking-dba2gxd0gzd7a7h6.koreacentral-01.azurewebsites.net/log",
            params={
                "uid": dummy_uid,
                "client_id": 0,
                "zebra_id": "warmup",
                "campaign_name": "warmup",
                "target_url": "https://example.com",
                "slug_prefix": "warmup"
            },
            timeout=5
        )
        return response.status_code == 200
    except Exception:
        return False

# ウォームアップ結果を表示
if warm_up_backend():
    st.info("✅ バックエンドウォームアップ完了")
else:
    st.warning("⚠️ ウォームアップに失敗しました（初回の処理に時間がかかる可能性があります）")

# メニュー選択
menu = st.sidebar.selectbox(
    "メニューを選択してください",
    ("UID一括生成", "アクセスログ一覧", "レポートダッシュボード")
)

if menu == "UID一括生成":
    generate_uids_ui()
elif menu == "アクセスログ一覧":
    access_logs_ui()
elif menu == "レポートダッシュボード":
    report_dashboard_ui()