import streamlit as st
import pandas as pd
from collections import Counter
from pathlib import Path
import os
import tempfile
from PIL import Image, ImageDraw, ImageFont
from inference_sdk import InferenceHTTPClient, InferenceConfiguration
from streamlit.errors import StreamlitSecretNotFoundError

# Page configuration
st.set_page_config(
    page_title="NutriScan - Dinh dưỡng học đường",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to match React design
st.markdown("""
<style>
    * {
        font-family: 'Segoe UI', 'Noto Sans', sans-serif;
    }

    /* Main background */
    .stMainBlockContainer {
        background-color: #f9fafb;
    }

    /* Sidebar styling - light green background */
    [data-testid="stSidebar"] {
        background-color: #ecfdf5 !important;
        border-right: 1.5px solid #e5e7eb;
    }

    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        background-color: #ecfdf5 !important;
    }

    /* Header styling */
    [data-testid="stHeader"] {
        background-color: #ffffff !important;
        border-bottom: 1.5px solid #e5e7eb;
    }

    /* Card styling */
    [data-testid="stVerticalBlockBelowGlue"] > div > div > div {
        border: 1.5px solid #e5e7eb;
        border-radius: 1rem;
        background-color: #ffffff;
        padding: 1.5rem;
    }

    /* Title color - dark green */
    h1, h2, h3 {
        color: #047857 !important;
        font-weight: 800 !important;
    }

    /* Links and buttons */
    a {
        color: #047857 !important;
    }

    /* Sidebar link active state */
    [data-testid="stSidebar"] .stRadio > div > label {
        color: #374151 !important;
        font-weight: 600 !important;
    }

    [data-testid="stSidebar"] .stRadio > div > label:hover {
        color: #047857 !important;
        background-color: #d1fae5 !important;
    }

    /* Input fields */
    input {
        border: 1.5px solid #a7f3d0 !important;
        border-radius: 0.5rem !important;
        background-color: #f9fafb !important;
        color: #111827 !important;
    }

    input:focus {
        border-color: #10b981 !important;
        box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1) !important;
    }

    /* Metric cards styling */
    .metric {
        background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
        border: 1.5px solid #a7f3d0;
        border-radius: 1rem;
        padding: 1rem;
    }

    /* Success/Good feedback */
    .good-feedback {
        background-color: #ecfdf5;
        color: #065f46;
        border-left: 4px solid #10b981;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }

    /* Warning/Alert feedback */
    .warn-feedback {
        background-color: #fef3c7;
        color: #c2410c;
        border-left: 4px solid #f97316;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }

    /* Button styling */
    .stButton > button {
        background-color: #047857 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 0.75rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }

    .stButton > button:hover {
        background-color: #065f46 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(4, 120, 87, 0.3) !important;
    }

    /* Metric value styling */
    .metric-value {
        color: #047857;
        font-weight: 800;
        font-size: 1.5rem;
    }

    /* Expander styling */
    [data-testid="stExpander"] {
        border: 1.5px solid #a7f3d0 !important;
        border-radius: 0.75rem !important;
    }

    /* Selectbox and other inputs */
    .stSelectbox, .stNumberInput, .stSlider {
        border: 1.5px solid #a7f3d0;
        border-radius: 0.5rem;
    }

    /* Roboflow detection cards */
    .rf-card {
        background: white; border-radius: 16px; padding: 18px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.04);
        border: 1px solid #F1F5F9; margin-bottom: 14px;
    }
    .rf-badge {
        display: inline-flex; align-items: center; gap: 6px; padding: 6px 14px;
        border-radius: 9999px; font-size: 14px; font-weight: 600; margin-bottom: 4px;
    }
    .rf-badge-success { background: #DCFCE7; color: #166534; }
    .rf-badge-info    { background: #DBEAFE; color: #1E40AF; }
    .rf-badge-warning { background: #FEF3C7; color: #92400E; }
    .rf-badge-danger  { background: #FEE2E2; color: #991B1B; }
    .rda-card {
        background: white; border-radius: 16px; padding: 18px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.04);
        border: 1px solid #F1F5F9; margin-bottom: 14px;
    }
    .rda-bar-track {
        position: relative; height: 14px; border-radius: 9999px; background: #F1F5F9;
        margin: 12px 0 6px; overflow: visible;
    }
    .rda-bar-fill {
        height: 100%; border-radius: 9999px; background: linear-gradient(90deg, #FB923C, #F97316);
    }
    .rda-bar-zone {
        position: absolute; top: -3px; bottom: -3px; background: rgba(22,163,74,0.15);
        border-left: 2px dashed #16A34A; border-right: 2px dashed #16A34A;
    }
    .rda-label-row { display: flex; justify-content: space-between; font-size: 12px; color: #78716C; }
    .rf-metric-grid {
        display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 14px 0 6px;
    }
    .rf-metric-card {
        background: linear-gradient(180deg, #FFF7ED 0%, #FFFFFF 100%);
        border: 1px solid #FED7AA; border-radius: 12px; padding: 12px 8px; text-align: center;
    }
    .rf-metric-label { font-size: 12px; color: #78716C; font-weight: 500; }
    .rf-metric-value { font-size: 20px; color: #1C1917; font-weight: 700; margin-top: 2px; }
    .rf-source-note { font-size: 12px; color: #64748B; margin-top: 6px; }
    @media (max-width: 640px) { .rf-metric-grid { grid-template-columns: repeat(2, 1fr); } }

    /* Conclusion card */
    .conclusion-card {
        background: #F8FAFC; border: 1.5px solid #CBD5E1;
        border-radius: 14px; padding: 18px 20px; margin: 12px 0;
    }
    .conclusion-title {
        font-size: 1rem; font-weight: 700; color: #1C1917; margin-bottom: 10px;
    }
    .conclusion-level {
        display: inline-block; font-size: 0.82rem; font-weight: 600;
        padding: 3px 10px; border-radius: 999px; margin-bottom: 10px;
    }
    .level-dat    { background: #D1FAE5; color: #065F46; }
    .level-thieu  { background: #FEF3C7; color: #92400E; }
    .level-vuot   { background: #FEE2E2; color: #991B1B; }
    .conclusion-pro { color: #15803D; font-size: 0.88rem; margin: 5px 0; }
    .conclusion-con { color: #B45309; font-size: 0.88rem; margin: 5px 0; }

    /* Dish suggestion cards */
    .dish-card {
        background: white; border: 1.5px solid #a7f3d0; border-radius: 16px;
        padding: 20px 16px; text-align: center;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06); margin-bottom: 16px; min-height: 210px;
    }
    .dish-icon { font-size: 44px; display: block; margin-bottom: 10px; }
    .dish-name { font-size: 15px; font-weight: 700; color: #047857; margin-bottom: 6px; }
    .dish-cal {
        font-size: 12px; font-weight: 700; color: #ea580c;
        background: #fff7ed; border: 1px solid #fed7aa;
        padding: 2px 10px; border-radius: 9999px; display: inline-block; margin-bottom: 10px;
    }
    .dish-desc { font-size: 12px; color: #6b7280; line-height: 1.6; text-align: left; }
</style>
""", unsafe_allow_html=True)

ROBOFLOW_SERVER_URL = "https://serverless.roboflow.com"
ROBOFLOW_WORKSPACE = "nckh-nan"
ROBOFLOW_WORKFLOW_ID = "breakfast-demo-vbreakfast-demo-3-yolo11s-t1-logic"
NUTRITION_CSV_PATH = Path(__file__).with_name("dinh_duong_thanh_phan.csv")
MON_CSV_PATH = Path(__file__).with_name("mon_thanh_phan.csv")
ROBOFLOW_CONFIDENCE_THRESHOLD = 0.4
NGUON_TU_DO = (
    "Số liệu đo khối lượng từng thành phần món ăn do nhóm nghiên cứu khoa học (NCKH) "
    "tự thực hiện và phân tích từng thành phần, dựa trên dữ liệu dinh dưỡng từ"
    "Viện Dinh dưỡng Quốc gia."
)
DAILY_CALORIES_KCAL = {"Nam": 2820, "Nữ": 2380}
BREAKFAST_CALORIE_RANGE = {
    gender: (round(calories * 0.25), round(calories * 0.30))
    for gender, calories in DAILY_CALORIES_KCAL.items()
}
NGUON_RDA = (
    "Quyết định 3958/QĐ-BYT (25/12/2025, Bộ Y tế) — Hướng dẫn dinh dưỡng đối "
    "với bữa ăn học đường. Nhu cầu năng lượng cả ngày HS THPT: Nam 2.820 kcal, "
    "Nữ 2.380 kcal; bữa sáng chiếm 25–30% năng lượng cả ngày."
)

DISH_CONCLUSIONS = {
    "com_suon": {
        "pros": [
            "Cung cấp đủ protein từ thịt sườn và chả.",
            "Có rau tươi kèm theo (dưa leo, cà chua).",
            "Năng lượng phù hợp cho buổi học sáng.",
        ],
        "cons": [
            "Hàm lượng chất xơ còn thấp — nên thêm rau xanh.",
            "Chất béo từ bì heo khá cao, nên ăn vừa phải.",
        ],
    },
    "xoi_man": {
        "pros": [
            "Cung cấp năng lượng cao nhờ tinh bột từ nếp — phù hợp cho buổi sáng cần nhiều sức.",
            "Có protein từ thịt, tôm khô, lạp xưởng và trứng.",
            "Bổ sung chất béo thực vật tốt từ nước cốt dừa, giúp xôi dẻo béo và no lâu.",
        ],
        "cons": [
            "Hàm lượng chất xơ còn thấp — nên thêm rau củ như cà rốt, đậu Hà Lan hoặc ăn kèm dưa leo, giá đỗ.",
            "Lượng natri (muối) khá cao do tôm khô, lạp xưởng và củ cải muối — nên ăn vừa phải, người huyết áp cao cần lưu ý.",
            "Lạp xưởng và nước cốt dừa chứa nhiều chất béo — ăn nhiều dễ tăng cân, nên kết hợp vận động.",
        ],
    },
    "sandwich": {
        "pros": [
            "Cung cấp tinh bột từ bánh mì — tạo năng lượng nhanh cho buổi sáng.",
            "Có protein từ trứng, thịt gà, cá ngừ hoặc tôm tùy loại nhân.",
            "Kèm rau xà lách, dưa leo, cà chua — bổ sung chất xơ và vitamin.",
            "Dễ làm, nhanh gọn, linh hoạt thay đổi nhân để không bị ngán.",
        ],
        "cons": [
            "Sốt mayonnaise và phô mai chứa nhiều chất béo — nên dùng vừa phải.",
            "Nhân chế biến sẵn (xúc xích, thịt xông khói, cá ngừ đóng hộp) có thể chứa nhiều muối.",
            "Một số biến tấu chiên ngập dầu làm tăng đáng kể calo và chất béo.",
        ],
    },
    "banh_bao": {
        "pros": [
            "Cung cấp tinh bột từ vỏ bánh — tạo năng lượng nhanh, tiện lợi cho buổi sáng.",
            "Có protein từ nhân thịt băm và trứng cút.",
            "Tiện lợi, dễ ăn, phù hợp cho học sinh bận rộn.",
        ],
        "cons": [
            "Hàm lượng chất xơ thấp — nên ăn kèm thêm rau hoặc trái cây.",
            "Nhân chế biến sẵn có thể chứa nhiều muối và chất bảo quản.",
            "Một số biến tấu chiên ngập dầu làm tăng đáng kể calo và chất béo.",
        ],
    },
    "pho": {
        "pros": [
            "Cung cấp tinh bột từ bánh phở bột gạo — tạo năng lượng ổn định cho buổi sáng.",
            "Có protein từ thịt bò/gà cắt lát mỏng — giúp no lâu và đủ sức cho buổi học.",
            "Nước dùng ninh xương kèm thảo quả, quế, hồi — giàu calci và khoáng chất, hỗ trợ xương chắc khỏe.",
            "Ăn kèm rau thơm, giá đỗ, hành lá và chanh — bổ sung chất xơ, vitamin và hỗ trợ tiêu hóa.",
            "Là món điểm tâm truyền thống, dễ tiêu hóa nhờ nước dùng nóng.",
        ],
        "cons": [
            "Người ăn kiêng tinh bột nên giảm lượng bánh phở, ăn nhiều thịt và rau hơn.",
            "Lượng muối trong nước dùng và nước mắm khá cao — người huyết áp cao hoặc có vấn đề về thận cần hạn chế.",
            "Một số quán sử dụng nhiều mì chính — nên chọn quán nêm nếm tự nhiên.",
        ],
    },
    "banh_cuon": {
        "pros": [
            "Cung cấp tinh bột từ vỏ bánh bột gạo hấp tráng mỏng — năng lượng nhẹ nhàng, dễ tiêu hóa.",
            "Có protein từ nhân thịt heo xay, nấm mèo và hành tím — hỗ trợ no lâu.",
            "Thường ăn kèm chả lụa, giá đỗ và rau thơm — bổ sung thêm chất đạm, chất xơ và vitamin.",
            "Nước chấm chua ngọt từ nước mắm, chanh, ớt, tỏi — kích thích vị giác, dễ ăn.",
        ],
        "cons": [
            "Vỏ bánh từ gạo tinh chế nên chất xơ thấp — nên tăng cường rau sống, giá đỗ ăn kèm.",
            "Nhân thịt xào với dầu ăn và mỡ hành phi khá nhiều chất béo — người kiểm soát cân nặng nên ăn vừa phải.",
            "Nước mắm ăn kèm thường mặn — người huyết áp cao hoặc có vấn đề về thận cần lưu ý.",
            "Một số biến tấu (bánh cuốn thịt nướng, bánh cuốn trứng) có thêm calo và chất béo.",
        ],
    },
    "nui_xao": {
        "pros": [
            "Cung cấp tinh bột từ nui bột mì — tạo năng lượng khá tốt cho buổi sáng.",
            "Có protein từ thịt bò, tôm, trứng, xúc xích tùy loại — giúp no lâu.",
            "Rau củ kèm theo (ớt chuông, cải ngọt, cà rốt, hành tây) bổ sung chất xơ và vitamin.",
            "Nước sốt đậm đà từ nước tương, dầu hào, tương cà — giúp món ăn thơm ngon, dễ ăn.",
            "Chế biến nhanh gọn, linh hoạt nhiều biến tấu để đổi bữa không bị ngán.",
        ],
        "cons": [
            "Nui từ bột mì tinh chế nên chất xơ vẫn thấp — nên tăng cường rau củ ăn kèm.",
            "Món xào dùng nhiều dầu ăn — người kiểm soát cân nặng nên giảm lượng dầu.",
            "Nước sốt chứa dầu hào, nước tương và hạt nêm với lượng muối khá cao — người huyết áp cao cần lưu ý.",
            "Một số biến tấu dùng xúc xích hoặc thêm mayonnaise làm tăng calo và chất béo.",
        ],
    },
    "banh_mi": {
        "pros": [
            "Cung cấp tinh bột từ ổ bánh mì — tạo năng lượng tiện lợi cho buổi sáng.",
            "Có protein từ nhân như thịt, chả, trứng hoặc cá — giúp bữa ăn no và đầy đủ hơn.",
            "Thường ăn kèm dưa leo, rau thơm và đồ chua — bổ sung rau củ, tạo vị tươi ngon.",
            "Có nhiều loại nhân để lựa chọn, dễ thay đổi theo khẩu vị.",
        ],
        "cons": [
            "Pate, bơ, mayonnaise và một số loại thịt chế biến sẵn làm tăng lượng chất béo và muối.",
            "Lượng rau trong một ổ bánh mì thường không nhiều — có thể thêm rau hoặc ăn kèm trái cây để tăng chất xơ.",
        ],
    },
}

def danh_gia_khau_phan_sang(calo_do_duoc, gioi_tinh):
    """So sánh calo bữa sáng với khuyến nghị theo giới tính.
    Trả về: (phan_tram, muc_thap, muc_cao, trang_thai, mo_ta)
    """
    muc_thap, muc_cao = BREAKFAST_CALORIE_RANGE[gioi_tinh]
    trung_binh = (muc_thap + muc_cao) / 2
    phan_tram = calo_do_duoc / trung_binh * 100
    if calo_do_duoc < muc_thap:
        trang_thai = "thieu"
        mo_ta = f"Thiếu năng lượng so với khuyến nghị (dưới {muc_thap} kcal)"
    elif calo_do_duoc > muc_cao:
        trang_thai = "vuot"
        mo_ta = f"Vượt khuyến nghị (trên {muc_cao} kcal)"
    else:
        trang_thai = "dat"
        mo_ta = f"Đạt khuyến nghị ({muc_thap}–{muc_cao} kcal)"
    return phan_tram, muc_thap, muc_cao, trang_thai, mo_ta


def get_roboflow_api_key():
    try:
        secret_key = st.secrets.get("ROBOFLOW_API_KEY", "")
    except StreamlitSecretNotFoundError:
        secret_key = ""
    return (secret_key or os.getenv("ROBOFLOW_API_KEY", "")).strip()


@st.cache_resource
def load_roboflow_client(api_key):
    if not api_key:
        return None
    return InferenceHTTPClient(
        api_url=ROBOFLOW_SERVER_URL,
        api_key=api_key,
    ).configure(InferenceConfiguration(api_key_transport="header"))


@st.cache_data
def load_nutrition_table():
    if not NUTRITION_CSV_PATH.is_file():
        raise FileNotFoundError(
            f"Không tìm thấy bảng dinh dưỡng: {NUTRITION_CSV_PATH.name}"
        )
    return pd.read_csv(NUTRITION_CSV_PATH).set_index("ma_thanh_phan")


@st.cache_data
def load_mon_name_map():
    """Trả về dict {lop_nhan_dien_mon: ten_mon} để lấy tên món từ class Roboflow."""
    if not MON_CSV_PATH.is_file():
        return {}
    df = pd.read_csv(MON_CSV_PATH)
    mask = df["lop_nhan_dien_mon"].notna() & (df["lop_nhan_dien_mon"].str.strip() != "")
    return (
        df[mask]
        .drop_duplicates("lop_nhan_dien_mon")
        .set_index("lop_nhan_dien_mon")["ten_mon"]
        .to_dict()
    )


@st.cache_data
def load_mon_ma_map():
    """Trả về dict {lop_nhan_dien_mon: ma_mon} để tra kết luận dinh dưỡng."""
    if not MON_CSV_PATH.is_file():
        return {}
    df = pd.read_csv(MON_CSV_PATH)
    mask = df["lop_nhan_dien_mon"].notna() & (df["lop_nhan_dien_mon"].str.strip() != "")
    return (
        df[mask]
        .drop_duplicates("lop_nhan_dien_mon")
        .set_index("lop_nhan_dien_mon")["ma_mon"]
        .to_dict()
    )


def calculate_detected_nutrition(nutrition_table, predictions):
    """Tính dinh dưỡng từ những thành phần Roboflow phát hiện.
    Mỗi lớp chỉ tính 1 phần dù xuất hiện nhiều khung (bbox).
    Lớp chưa có trong bảng dinh dưỡng vẫn được liệt kê với giá trị '—'."""
    seen_classes = dict.fromkeys(p["class"] for p in predictions)  # unique, preserve order
    counts = Counter(p["class"] for p in predictions)
    details = []
    totals = {"calo": 0.0, "protein": 0.0, "carb": 0.0, "fat": 0.0}
    unmatched = set()
    for code in seen_classes:
        if code not in nutrition_table.index:
            unmatched.add(code)
            details.append({
                "ten": code,
                "so_khung": counts[code],
                "khoi_luong": None,
                "calo": None,
                "protein": None,
                "carb": None,
                "fat": None,
            })
            continue
        row = nutrition_table.loc[code]
        mass = float(row["khoi_luong_mac_dinh_g"])
        ratio = mass / 100
        detail = {
            "ten": row["ten_thanh_phan"],
            "so_khung": counts[code],
            "khoi_luong": mass,
            "calo": float(row["calo_100g"]) * ratio,
            "protein": float(row["protein_100g"]) * ratio,
            "carb": float(row["carb_100g"]) * ratio,
            "fat": float(row["fat_100g"]) * ratio,
        }
        details.append(detail)
        for k in totals:
            totals[k] += detail[k]
    return details, totals, unmatched


def run_roboflow_workflow(client, uploaded_file):
    suffix = Path(uploaded_file.name).suffix.lower() or ".jpg"
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(uploaded_file.getbuffer())
            temp_path = temp_file.name
        return client.run_workflow(
            workspace_name=ROBOFLOW_WORKSPACE,
            workflow_id=ROBOFLOW_WORKFLOW_ID,
            images={"image": temp_path},
            use_cache=True,
        )
    finally:
        if temp_path:
            Path(temp_path).unlink(missing_ok=True)


def find_roboflow_predictions(value):
    if isinstance(value, dict):
        for key in ("model_predictions", "predictions", "detections"):
            predictions = value.get(key)
            if isinstance(predictions, list):
                return predictions
            if isinstance(predictions, dict):
                nested = predictions.get("predictions") or predictions.get("detections")
                if isinstance(nested, list):
                    return nested
        for nested_value in value.values():
            found = find_roboflow_predictions(nested_value)
            if found is not None:
                return found
    elif isinstance(value, list):
        for item in value:
            found = find_roboflow_predictions(item)
            if found is not None:
                return found
    return None


def parse_roboflow_predictions(result):
    if isinstance(result, list):
        result = {
            key: value
            for item in result if isinstance(item, dict)
            for key, value in item.items()
        }
    raw_predictions = find_roboflow_predictions(result) or []
    predictions = []
    for prediction in raw_predictions:
        if not isinstance(prediction, dict):
            continue
        class_name = (
            prediction.get("class")
            or prediction.get("label")
            or prediction.get("class_name")
            or prediction.get("name")
        )
        if not class_name:
            continue
        try:
            confidence = float(prediction.get("confidence", prediction.get("score", 0)))
        except (TypeError, ValueError):
            confidence = 0.0
        if confidence < ROBOFLOW_CONFIDENCE_THRESHOLD:
            continue
        coordinates = {}
        for key in ("x", "y", "width", "height"):
            try:
                coordinates[key] = float(prediction.get(key, 0))
            except (TypeError, ValueError):
                coordinates[key] = 0.0
        predictions.append({
            "class": str(class_name),
            "confidence": confidence,
            **coordinates,
        })
    return predictions


def draw_roboflow_predictions(image, predictions):
    annotated = image.convert("RGB").copy()
    draw = ImageDraw.Draw(annotated)
    width, height = annotated.size
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 16)
    except OSError:
        font = ImageFont.load_default()

    for prediction in predictions:
        x, y = prediction["x"], prediction["y"]
        box_width, box_height = prediction["width"], prediction["height"]
        x1, y1 = max(0, x - box_width / 2), max(0, y - box_height / 2)
        x2, y2 = min(width, x + box_width / 2), min(height, y + box_height / 2)
        label = f'{prediction["class"]} {prediction["confidence"]:.0%}'
        draw.rectangle([x1, y1, x2, y2], outline=(0, 180, 0), width=3)
        text_box = draw.textbbox((x1, y1), label, font=font)
        text_width = text_box[2] - text_box[0]
        text_height = text_box[3] - text_box[1]
        label_y = max(0, y1 - text_height - 6)
        draw.rectangle([x1, label_y, x1 + text_width + 8, y1], fill=(0, 150, 0))
        draw.text((x1 + 4, label_y + 2), label, fill="white", font=font)
    return annotated


def roboflow_detection_page():
    st.title("📷 Nhận Diện Thành Phần Món Ăn")
    gender = st.radio("Giới tính học sinh", ["Nam", "Nữ"], horizontal=True)
    uploaded_file = st.file_uploader(
        "Chọn ảnh món ăn", type=["jpg", "jpeg", "png"], key="roboflow_image"
    )
    if uploaded_file is None:
        return

    image = Image.open(uploaded_file)
    st.image(image, caption="Ảnh đã tải lên", use_container_width=True)
    api_key = get_roboflow_api_key()
    if not api_key:
        st.warning(
            "Chưa cấu hình ROBOFLOW_API_KEY. Thêm khóa vào Streamlit Secrets "
            "hoặc biến môi trường để nhận diện."
        )
        return
    try:
        nutrition_table = load_nutrition_table()
    except (FileNotFoundError, KeyError, pd.errors.ParserError) as error:
        st.error(f"Không thể tải bảng dinh dưỡng: {error}")
        return

    if not st.button("🔍 Nhận diện & tính dinh dưỡng", type="primary"):
        return
    try:
        with st.spinner("Đang gửi ảnh lên Roboflow Serverless Cloud..."):
            result = run_roboflow_workflow(load_roboflow_client(api_key), uploaded_file)
            predictions = parse_roboflow_predictions(result)
    except Exception as error:
        st.error(f"Lỗi khi gọi Roboflow Workflow: {type(error).__name__}: {error}")
        return

    with st.expander("Xem phản hồi từ Roboflow"):
        st.json(result)
    if not predictions:
        st.warning(
            f"Không phát hiện thành phần nào với độ tin cậy từ "
            f"{ROBOFLOW_CONFIDENCE_THRESHOLD:.0%} trở lên."
        )
        return

    st.image(
        draw_roboflow_predictions(image, predictions),
        caption="Các thành phần được Roboflow phát hiện",
        use_container_width=True,
    )

    details, totals, unmatched = calculate_detected_nutrition(nutrition_table, predictions)

    mon_name_map = load_mon_name_map()
    mon_ma_map = load_mon_ma_map()
    ten_mon_list = list(dict.fromkeys(
        mon_name_map[p["class"]] for p in predictions if p["class"] in mon_name_map
    ))
    ma_mon_list = list(dict.fromkeys(
        mon_ma_map[p["class"]] for p in predictions if p["class"] in mon_ma_map
    ))
    if ten_mon_list:
        ten_mon_hien_thi = ", ".join(ten_mon_list)
    elif details:
        ten_mon_hien_thi = details[0]["ten"]
    else:
        ten_mon_hien_thi = "Chưa nhận diện được"
    st.markdown(f"""
    <div class="rf-card">
        <div style="font-size:1.15rem; font-weight:700; margin-bottom:0.5rem;">
            🍽️ Món nhận diện: {ten_mon_hien_thi}
        </div>
        <div class="rf-metric-grid">
            <div class="rf-metric-card">
                <div class="rf-metric-label">Tổng Calo</div>
                <div class="rf-metric-value">{totals['calo']:.0f}</div>
            </div>
            <div class="rf-metric-card">
                <div class="rf-metric-label">Protein (g)</div>
                <div class="rf-metric-value">{totals['protein']:.1f}</div>
            </div>
            <div class="rf-metric-card">
                <div class="rf-metric-label">Carb (g)</div>
                <div class="rf-metric-value">{totals['carb']:.1f}</div>
            </div>
            <div class="rf-metric-card">
                <div class="rf-metric-label">Fat (g)</div>
                <div class="rf-metric-value">{totals['fat']:.1f}</div>
            </div>
        </div>
        <div class="rf-source-note">📖 {NGUON_TU_DO} — mỗi thành phần tính 1 phần chuẩn</div>
    </div>
    """, unsafe_allow_html=True)

    if details:
        st.subheader("📋 Thành phần nhận diện được")
        details_df = pd.DataFrame(details)[
            ["ten", "so_khung", "khoi_luong", "calo", "protein", "carb", "fat"]
        ]
        details_df.columns = [
            "Tên thành phần", "Số khung", "Khối lượng (g)", "Calo",
            "Protein (g)", "Carb (g)", "Fat (g)",
        ]
        def fmt_num(x, fmt):
            return "—" if x is None or (isinstance(x, float) and pd.isna(x)) else fmt.format(x)
        st.dataframe(
            details_df.style.format({
                "Khối lượng (g)": lambda x: fmt_num(x, "{:.0f}"),
                "Calo":           lambda x: fmt_num(x, "{:.0f}"),
                "Protein (g)":    lambda x: fmt_num(x, "{:.1f}"),
                "Carb (g)":       lambda x: fmt_num(x, "{:.1f}"),
                "Fat (g)":        lambda x: fmt_num(x, "{:.1f}"),
            }),
            use_container_width=True,
            hide_index=True,
        )

    phan_tram, muc_thap, muc_cao, trang_thai, mo_ta = danh_gia_khau_phan_sang(totals["calo"], gender)
    mau_badge = {"thieu": "rf-badge-warning", "dat": "rf-badge-success", "vuot": "rf-badge-danger"}[trang_thai]
    icon_badge = {"thieu": "⬇️", "dat": "✅", "vuot": "⬆️"}[trang_thai]
    truc_max = muc_cao * 1.4
    vt_thap = muc_thap / truc_max * 100
    vt_cao = muc_cao / truc_max * 100
    vt_do_duoc = min(totals["calo"] / truc_max * 100, 100)
    st.markdown(f"""
    <div class="rda-card">
        <span class="rf-badge {mau_badge}">{icon_badge} {mo_ta}</span>
        <div class="rda-bar-track">
            <div class="rda-bar-zone" style="left:{vt_thap:.1f}%; width:{vt_cao - vt_thap:.1f}%;"></div>
            <div class="rda-bar-fill" style="width:{vt_do_duoc:.1f}%;"></div>
        </div>
        <div class="rda-label-row">
            <span>0 kcal</span>
            <span>Khuyến nghị: {muc_thap}–{muc_cao} kcal</span>
        </div>
        <div class="rf-metric-grid" style="grid-template-columns: repeat(2, 1fr);">
            <div class="rf-metric-card">
                <div class="rf-metric-label">Đo được</div>
                <div class="rf-metric-value">{totals['calo']:.0f} kcal</div>
            </div>
            <div class="rf-metric-card">
                <div class="rf-metric-label">% so với mức TB khuyến nghị</div>
                <div class="rf-metric-value">{phan_tram:.0f}%</div>
            </div>
        </div>
        <div class="rf-source-note">📖 Ngưỡng khuyến nghị bữa sáng ({gender}): {muc_thap}–{muc_cao} kcal. {NGUON_RDA}</div>
    </div>
    """, unsafe_allow_html=True)

    # Kết luận dinh dưỡng theo từng món nhận diện được
    level_label = {"dat": "Đạt khuyến nghị", "thieu": "Chưa đạt", "vuot": "Cần cải thiện"}[trang_thai]
    level_class = {"dat": "level-dat", "thieu": "level-thieu", "vuot": "level-vuot"}[trang_thai]
    for i, ma_mon in enumerate(ma_mon_list):
        conclusion = DISH_CONCLUSIONS.get(ma_mon)
        if not conclusion:
            continue
        ten_mon_hien_thi_ket_luan = ten_mon_list[i] if i < len(ten_mon_list) else ma_mon
        pros_html = "".join(
            f'<div class="conclusion-pro">✅ {p}</div>' for p in conclusion["pros"]
        )
        cons_html = "".join(
            f'<div class="conclusion-con">⚠️ {c}</div>' for c in conclusion["cons"]
        )
        st.markdown(f"""
        <div class="conclusion-card">
            <div class="conclusion-title">📊 Nhận xét: {ten_mon_hien_thi_ket_luan}</div>
            <span class="conclusion-level {level_class}">{level_label}</span>
            <div style="margin-top:8px; font-weight:600; font-size:0.88rem; color:#15803D; margin-bottom:4px;">Ưu điểm</div>
            {pros_html}
            <div style="margin-top:10px; font-weight:600; font-size:0.88rem; color:#B45309; margin-bottom:4px;">Lưu ý</div>
            {cons_html}
        </div>
        """, unsafe_allow_html=True)

    if unmatched:
        st.warning(
            "Các lớp phát hiện nhưng chưa có trong bảng dinh dưỡng nên chưa được tính: "
            + ", ".join(sorted(unmatched))
        )
    confidence_df = pd.DataFrame([
        {"Thành phần": item["class"], "Độ tin cậy": item["confidence"]}
        for item in predictions
    ])
    st.dataframe(
        confidence_df.style.format({"Độ tin cậy": "{:.1%}"}),
        use_container_width=True,
        hide_index=True,
    )

# Dishes for home page suggestion cards
DISHES = [
    {
        'icon': '🥖',
        'name': 'Bánh Mì',
        'calories': '400–600',
        'desc': 'Nhân đa dạng: thịt, trứng, chả cá kèm rau & sốt. Tinh bột cao, cung cấp năng lượng tốt cho buổi sáng.',
    },
    {
        'icon': '🍙',
        'name': 'Xôi Mặn',
        'calories': '350–450',
        'desc': 'Gạo nếp dẻo thơm kèm pate, chả lụa, chà bông, trứng cút, lạp xưởng. No lâu, giàu tinh bột và protein.',
    },
    {
        'icon': '🥟',
        'name': 'Bánh Bao',
        'calories': '~350',
        'desc': 'Vỏ bánh mềm, nhân thịt băm và trứng cút. Đơn giản, tiện lợi, phù hợp bữa sáng nhanh.',
    },
    {
        'icon': '🍜',
        'name': 'Phở / Hủ Tiếu / Bún Bò',
        'calories': '450–600',
        'desc': 'Sợi bánh + thịt các loại + rau thơm, giá đỗ. Món nước giàu protein, dễ tiêu hóa, ít béo.',
    },
    {
        'icon': '🥙',
        'name': 'Bánh Cuốn',
        'calories': '400–500',
        'desc': 'Bánh tráng hấp mềm cuộn với giò chả, chả giò, nhân thịt băm. Nhẹ bụng, vừa miệng.',
    },
    {
        'icon': '🍝',
        'name': 'Nui Xào',
        'calories': '450–550',
        'desc': 'Nui, trứng chiên, thịt bò, rau củ xào chung. Đơn giản, đủ chất, nhanh chuẩn bị.',
    },
    {
        'icon': '🍛',
        'name': 'Cơm Tấm',
        'calories': '550–650',
        'desc': 'Cơm tấm, sườn nướng / chả trứng, mỡ hành, đồ chua (dưa leo, củ cải), nước mắm chua ngọt.',
    },
    {
        'icon': '🍖',
        'name': 'Bún Thịt Nướng',
        'calories': '~500',
        'desc': 'Bún tươi, thịt heo nướng thơm, chả giò, rau sống, dưa chua, đậu phộng rang, mỡ hành.',
    },
]

# Navigation
NAV = [
    {'icon': '🏠', 'label': 'Trang chủ'},
    {'icon': '📷', 'label': 'Nhận diện món ăn'},
    {'icon': '📚', 'label': 'Kiến thức dinh dưỡng'},
]

def get_bmi_category(bmi):
    if bmi < 18.5:
        return {'label': 'Thiếu cân', 'color': '#f97316'}
    elif bmi < 23:
        return {'label': 'Bình thường', 'color': '#10b981'}
    elif bmi < 27.5:
        return {'label': 'Thừa cân', 'color': '#f97316'}
    else:
        return {'label': 'Béo phì', 'color': '#ef4444'}


def home_page():
    st.title("🏠 Trang Chủ - NutriScan")
    st.markdown("**Hệ thống Dinh dưỡng Bữa Sáng cho Học sinh**")

    height = st.session_state.get('height') or 0
    weight = st.session_state.get('weight') or 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Cân nặng", f"{int(weight)} kg" if weight else "—")
    with col2:
        st.metric("Chiều cao", f"{int(height)} cm" if height else "—")
    with col3:
        if height and weight:
            bmi = weight / ((height / 100) ** 2)
            category = get_bmi_category(bmi)
            st.metric("BMI", f"{bmi:.1f}", category['label'])
        else:
            st.metric("BMI", "—", "Nhập chiều cao & cân nặng")
    with col4:
        st.metric("Năng lượng hôm nay", "— kcal")

    st.divider()

    st.subheader("🍽️ Các Món Ăn Gợi Ý")
    st.caption("Các món ăn sáng phổ biến của học sinh — dùng trang Nhận diện để tính dinh dưỡng chính xác")

    for row_start in range(0, len(DISHES), 3):
        row_dishes = DISHES[row_start:row_start + 3]
        cols = st.columns(3)
        for col, dish in zip(cols, row_dishes):
            with col:
                st.markdown(f"""
<div class="dish-card">
    <div class="dish-icon">{dish['icon']}</div>
    <div class="dish-name">{dish['name']}</div>
    <div class="dish-cal">🔥 {dish['calories']} kcal</div>
    <div class="dish-desc">{dish['desc']}</div>
</div>
""", unsafe_allow_html=True)

def nutrition_knowledge():
    """Nutrition education"""
    st.title("📚 Kiến Thức Dinh Dưỡng")
    st.markdown("**Tìm hiểu về dinh dưỡng cân bằng và lối sống lành mạnh**")
    st.markdown("---")

    with st.expander("📖 Dinh Dưỡng Cân Bằng", expanded=True):
        st.markdown("""
        **Dinh dưỡng cân bằng** bao gồm các nhóm chất dinh dưỡng chính:

        - **Protein (20-30%)** 💪: Xây dựng và sửa chữa cơ
          - Nguồn: Thịt, cá, trứng, đậu, sữa, hạt

        - **Carbohydrate (45-65%)** 🌾: Cung cấp năng lượng
          - Ưu tiên: Tinh bột phức hợp (gạo lứt, bánh mì nguyên cám)

        - **Chất Béo (20-35%)** 🧈: Hỗ trợ các chức năng cơ thể
          - Chọn: Dầu cá, dầu ô liu, hạt, quả khô
        """)

    with st.expander("🥗 Rau Xanh & Trái Cây"):
        st.markdown("""
        - **Ăn 5 phần rau quả mỗi ngày** - tương đương 400g
        - **Nhiều màu = nhiều vitamin & chất khoáng khác nhau**
          - 🟢 Rau xanh: Sắt, canxi
          - 🟡 Quả vàng: Beta-caroten
          - 🔴 Cà chua: Lycopene
        - **Nguồn tốt của chất xơ** - giúp tiêu hóa và no lâu
        """)

    with st.expander("💧 Nước & Chất Lỏng"):
        st.markdown("""
        - **Uống 8-10 ly nước mỗi ngày** (khoảng 2 lít)
        - **Lợi ích:**
          - Giúp tiêu hóa tốt
          - Duy trì năng lượng và tập trung
          - Làm sạch độc tố
        - **Hạn chế:**
          - Đồ uống có đường (nước ngọt, trà có đường)
          - Nước có gas quá nhiều
        """)

    with st.expander("⚖️ Quản Lý Cân Nặng - Chỉ Số BMI"):
        st.markdown("""
        **Công thức tính:** BMI = Cân nặng (kg) / [Chiều cao (m)]²

        **Phân loại:**
        - **< 18.5**: 🟡 Thiếu cân - Nên ăn thêm, bổ sung vitamin
        - **18.5 - 23**: 🟢 Bình thường - Duy trì tốt!
        - **23 - 27.5**: 🟠 Thừa cân - Cần điều chỉnh thói quen
        - **> 27.5**: 🔴 Béo phì - Tham khảo bác sĩ, dinh dưỡng sĩ
        """)

    with st.expander("🍽️ Gợi Ý Bữa Sáng Cân Bằng"):
        st.markdown("""
        **Thành phần lý tưởng của bữa sáng:**

        1. **Nhóm tinh bột** (1/3 bữa): Gạo, bánh mì, yến mạch
        2. **Nhóm protein** (1/3 bữa): Thịt, cá, trứng, đậu
        3. **Nhóm rau xanh + trái cây** (1/3 bữa): Rau sống, quả tươi

        **Ví dụ bữa sáng cân bằng:**
        - Cơm tấm + sườn nướng + rau tươi
        - Bánh mì nguyên cám + trứng + dưa leo + sữa
        - Cháo gà + rau cải + cà chua
        """)

    with st.expander("⏰ Thời Gian Ăn Tối Ưu"):
        st.markdown("""
        - **Bữa sáng lý tưởng:** 6:00-8:00 sáng
        - **Tầm quan trọng:** Ăn sáng trong vòng 1 giờ sau khi thức dậy
        - **Tác động:** Kích hoạt trao đổi chất tốt nhất trong ngày
        - **Ưu điểm:** Tăng khả năng tập trung, tránh quên học
        """)

# Main app structure
def main():
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = 'home'
    if 'selected_dish' not in st.session_state:
        st.session_state.selected_dish = None

    # Sidebar header with logo
    st.sidebar.markdown("""
    <div style='text-align: center; margin-bottom: 2rem;'>
        <div style='font-size: 48px; margin-bottom: 0.5rem;'>🥗</div>
        <h1 style='color: #047857; font-size: 24px; margin: 0; font-weight: 800;'>NutriScan</h1>
        <p style='color: #6b7280; margin: 0.25rem 0 0 0; font-size: 12px; font-weight: 600;'>Dinh dưỡng học đường</p>
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown("---")

    # Sidebar student info form (from React code)
    with st.sidebar:
        st.markdown("### 👤 Thông tin học sinh")

        # Initialize session state for student info
        if 'grade' not in st.session_state:
            st.session_state.grade = ''
        if 'height' not in st.session_state:
            st.session_state.height = ''
        if 'weight' not in st.session_state:
            st.session_state.weight = ''

        # Grade selection with checkboxes
        st.markdown("**Khối lớp**")
        cols = st.columns(3)
        grades = ['10', '11', '12']

        for idx, grade_val in enumerate(grades):
            with cols[idx]:
                if st.checkbox(f'Lớp {grade_val}',
                              value=(st.session_state.grade == grade_val),
                              key=f'grade_checkbox_{grade_val}'):
                    st.session_state.grade = grade_val
                else:
                    if st.session_state.grade == grade_val:
                        st.session_state.grade = ''

        st.markdown("")

        # Height & Weight inputs
        col1, col2 = st.columns(2)

        with col1:
            height = st.number_input(
                "Chiều cao (cm)",
                min_value=100,
                max_value=220,
                value=int(st.session_state.height) if st.session_state.height else 160,
                key='height_input_sidebar'
            )
            st.session_state.height = height

        with col2:
            weight = st.number_input(
                "Cân nặng (kg)",
                min_value=20,
                max_value=200,
                value=int(st.session_state.weight) if st.session_state.weight else 50,
                key='weight_input_sidebar'
            )
            st.session_state.weight = weight

        # BMI Calculation
        if height and weight:
            bmi = weight / ((height / 100) ** 2)
            category = get_bmi_category(bmi)

            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
                        border: 1.5px solid #{category["color"].replace("#", "")};
                        padding: 0.75rem; border-radius: 0.75rem; text-align: center; margin-top: 0.5rem;'>
                <div style='color: #6b7280; font-size: 11px; font-weight: 600; margin-bottom: 0.25rem;'>Chỉ số BMI</div>
                <div style='color: #047857; font-size: 28px; font-weight: 800;'>{bmi:.1f}</div>
                <div style='font-size: 11px; font-weight: 600; margin-top: 0.25rem;'>
                    <span style='background: {category["color"]}; color: white; padding: 0.25rem 0.75rem;
                                 border-radius: 0.5rem; display: inline-block;'>
                        {category["label"]}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='background: #f9fafb; border: 1px dashed #a7f3d0; padding: 0.75rem;
                        border-radius: 0.75rem; text-align: center; font-size: 11px; color: #9ca3af;'>
                Nhập chiều cao & cân nặng để tính BMI
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

    # Sidebar navigation
    st.sidebar.markdown("### 📱 Menu Điều Hướng")

    selected = st.sidebar.radio(
        "Chọn trang:",
        options=[nav['label'] for nav in NAV],
        format_func=lambda x: f"{next(n['icon'] for n in NAV if n['label'] == x)} {x}",
        label_visibility="collapsed"
    )

    st.sidebar.markdown("---")

    # Footer in sidebar
    st.sidebar.markdown("""
    <div style='text-align: center; margin-top: 2rem; padding-top: 1rem; border-top: 1.5px solid #a7f3d0;'>
        <p style='font-size: 11px; color: #6b7280; margin: 0.5rem 0;'>
            <strong>🏫 Trường THPT Nguyễn An Ninh</strong>
        </p>
        <p style='font-size: 10px; color: #9ca3af; margin: 0;'>
            Tp. Hồ Chí Minh
        </p>
        <p style='font-size: 10px; color: #9ca3af; margin: 0.5rem 0 0 0;'>
            📧 nan@thptnan.edu.vn
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Main content area
    st.markdown("""
    <style>
        .main-header {
            background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
            border-bottom: 2px solid #a7f3d0;
            padding: 1.5rem;
            border-radius: 0.75rem;
            margin-bottom: 1.5rem;
        }
        .main-header h1 {
            color: #047857;
            margin: 0;
        }
        .main-header p {
            color: #6b7280;
            margin: 0.25rem 0 0 0;
            font-size: 14px;
        }
    </style>
    """, unsafe_allow_html=True)

    # Route to pages
    if selected == "Trang chủ":
        st.session_state.page = 'home'
        home_page()
    elif selected == "Nhận diện món ăn":
        roboflow_detection_page()
    elif selected == "Kiến thức dinh dưỡng":
        nutrition_knowledge()

if __name__ == "__main__":
    main()