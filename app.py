import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge
import numpy as np
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
</style>
""", unsafe_allow_html=True)

ROBOFLOW_SERVER_URL = "https://serverless.roboflow.com"
ROBOFLOW_WORKSPACE = "nckh-nan"
ROBOFLOW_WORKFLOW_ID = "breakfast-demo-vbreakfast-demo-3-yolo11s-t1-logic"
NUTRITION_CSV_PATH = Path(__file__).with_name("dinh_duong_thanh_phan.csv")
ROBOFLOW_CONFIDENCE_THRESHOLD = 0.4
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


def calculate_detected_nutrition(nutrition_table, predictions):
    counts = Counter(prediction["class"] for prediction in predictions)
    details = []
    totals = {"calo": 0.0, "protein": 0.0, "carb": 0.0, "fat": 0.0}
    for component_code, count in counts.items():
        if component_code not in nutrition_table.index:
            continue
        row = nutrition_table.loc[component_code]
        mass = float(row["khoi_luong_mac_dinh_g"]) * count
        ratio = mass / 100
        detail = {
            "ten": row["ten_thanh_phan"],
            "ma": component_code,
            "so_luong": count,
            "khoi_luong": mass,
            "calo": float(row["calo_100g"]) * ratio,
            "protein": float(row["protein_100g"]) * ratio,
            "carb": float(row["carb_100g"]) * ratio,
            "fat": float(row["fat_100g"]) * ratio,
            "nguon": row.get("nguon_so_lieu", "") if hasattr(row, "get") else "",
        }
        details.append(detail)
        for nutrient in totals:
            totals[nutrient] += detail[nutrient]
    return counts, details, totals


def roboflow_detection_page():
    st.title("📷 Nhận Diện Thành Phần Món Ăn")
    st.markdown(
        "Roboflow Workflow dùng YOLO để phát hiện từng thành phần trong ảnh; "
        "dinh dưỡng được cộng dồn theo bảng thành phần."
    )
    st.caption(
        "Việc huấn luyện model được thực hiện riêng trên Roboflow/Colab; trang này "
        "gửi ảnh tới Workflow đã cấu hình để nhận diện."
    )
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
    counts, details, totals = calculate_detected_nutrition(nutrition_table, predictions)

    ten_cac_thanh_phan = ", ".join(
        f"{c['ten']}" + (f" ×{c['so_luong']}" if c["so_luong"] > 1 else "")
        for c in details
    ) or "Không có thành phần khớp bảng"
    st.markdown(f"""
    <div class="rf-card">
        <span class="rf-badge rf-badge-success">🍽️ Phát hiện: {ten_cac_thanh_phan}</span>
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
        <div class="rf-source-note">📖 Số liệu từng thành phần: Bảng TPTP Việt Nam – Viện Dinh dưỡng Quốc gia 2007</div>
    </div>
    """, unsafe_allow_html=True)

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

    if details:
        details_df = pd.DataFrame(details)[
            ["ten", "so_luong", "khoi_luong", "calo", "protein", "carb", "fat"]
        ]
        details_df.columns = [
            "Thành phần", "Số lượng", "Khối lượng (g)", "Calo",
            "Protein (g)", "Carb (g)", "Fat (g)",
        ]
        st.dataframe(
            details_df.style.format({
                "Khối lượng (g)": "{:.0f}",
                "Calo": "{:.0f}",
                "Protein (g)": "{:.1f}",
                "Carb (g)": "{:.1f}",
                "Fat (g)": "{:.1f}",
            }),
            use_container_width=True,
            hide_index=True,
        )
    unknown_classes = set(counts) - set(nutrition_table.index)
    if unknown_classes:
        st.warning(
            "Các lớp chưa có trong bảng dinh dưỡng nên chưa được tính: "
            + ", ".join(sorted(unknown_classes))
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

# ============================================================
# GỢI Ý MÓN ĂN SÁNG CHO HỌC SINH THPT
# ============================================================
# Lượng kcal là mức ước tính theo khẩu phần tham khảo và có thể chỉnh sửa.
DISHES = [
    {"name":"🥖 Bánh mì","calories":"400 – 600 kcal","short_description":"Bữa sáng tiện lợi, giàu năng lượng và dễ kết hợp nhiều nhóm thực phẩm.","items":["Bánh mì","Thịt, trứng hoặc chả cá","Rau xanh, dưa leo","Nước sốt"],"nutrition":"Cung cấp carbohydrate từ bánh mì; thịt, trứng hoặc chả cá cung cấp protein; rau xanh góp phần bổ sung chất xơ.","goodFeedback":["Tiện lợi, phù hợp với học sinh có thời gian ăn sáng hạn chế.","Có thể kết hợp tinh bột, protein và rau trong cùng khẩu phần.","Có nhiều lựa chọn nhân để thay đổi thực đơn."],"warnFeedback":["Nên ưu tiên thêm rau và lựa chọn nhân ít chất béo.","Không nên sử dụng quá nhiều pate, sốt hoặc thực phẩm chế biến sẵn."],"tip":"Ưu tiên bánh mì có trứng/thịt + nhiều rau; có thể kết hợp thêm sữa hoặc trái cây."},
    {"name":"🍚 Xôi mặn","calories":"350 – 450 kcal","short_description":"Món ăn giàu năng lượng từ gạo nếp, kết hợp nhiều loại nhân mặn.","items":["Gạo nếp","Pate","Chả lụa","Chà bông","Trứng cút","Lạp xưởng"],"nutrition":"Gạo nếp cung cấp carbohydrate và năng lượng; thịt, chả và trứng bổ sung protein.","goodFeedback":["Cung cấp năng lượng cho hoạt động học tập buổi sáng.","Có thể thay đổi nhân để tạo sự đa dạng."],"warnFeedback":["Một số loại nhân có thể chứa nhiều chất béo và natri.","Nên kết hợp thêm rau hoặc trái cây để tăng chất xơ và vitamin."],"tip":"Chọn khẩu phần vừa phải và bổ sung trái cây hoặc sữa để bữa sáng đa dạng hơn."},
    {"name":"🥟 Bánh bao nhân thịt","calories":"Khoảng 350 kcal","short_description":"Lựa chọn nhanh gọn với vỏ bánh bột mì, nhân thịt và trứng cút.","items":["Vỏ bánh","Thịt băm","Trứng cút","Gia vị và nhân phụ"],"nutrition":"Cung cấp carbohydrate từ vỏ bánh và protein từ thịt, trứng.","goodFeedback":["Dễ mang theo và sử dụng vào buổi sáng.","Có cả nguồn tinh bột và protein trong một khẩu phần."],"warnFeedback":["Có thể chưa cung cấp đủ rau và chất xơ.","Nên kết hợp thêm sữa, trái cây hoặc rau củ phù hợp."],"tip":"Có thể dùng cùng một hộp sữa và một phần trái cây để tăng sự đa dạng dinh dưỡng."},
    {"name":"🍜 Phở / Hủ tiếu / Bún bò","calories":"450 – 600 kcal","short_description":"Nhóm món nước quen thuộc, kết hợp sợi bánh/bún, thịt và rau.","items":["Bánh phở, hủ tiếu hoặc bún","Thịt","Rau và rau thơm","Nước dùng"],"nutrition":"Cung cấp carbohydrate từ bánh hoặc sợi bún, protein từ thịt và một phần vitamin, khoáng chất từ rau ăn kèm.","goodFeedback":["Có thể kết hợp nhiều nhóm thực phẩm trong một bữa.","Rau ăn kèm giúp tăng sự đa dạng của khẩu phần."],"warnFeedback":["Nước dùng có thể chứa nhiều natri tùy cách chế biến.","Nên tăng rau và lựa chọn lượng thịt phù hợp."],"tip":"Ưu tiên thêm rau, hạn chế nước dùng quá mặn và cân đối khẩu phần theo nhu cầu cá nhân."},
    {"name":"🥢 Bánh cuốn","calories":"400 – 500 kcal","short_description":"Món ăn mềm, dễ ăn, kết hợp bánh, thịt, giò chả và rau ăn kèm.","items":["Bánh cuốn","Nhân thịt băm","Giò chả","Chả giò","Rau thơm","Nước chấm"],"nutrition":"Cung cấp carbohydrate từ bánh, protein từ thịt và giò chả, đồng thời có thêm rau ăn kèm.","goodFeedback":["Dễ ăn và phù hợp với khẩu vị của nhiều học sinh.","Có thể kết hợp thêm rau thơm và rau sống."],"warnFeedback":["Một số thành phần chế biến sẵn có thể chứa nhiều natri.","Nên điều chỉnh lượng chả và nước chấm."],"tip":"Tăng rau ăn kèm và dùng lượng nước chấm vừa phải để bữa sáng cân đối hơn."},
    {"name":"🍝 Nui xào","calories":"450 – 550 kcal","short_description":"Món ăn kết hợp nui, trứng, thịt bò và rau củ trong một khẩu phần.","items":["Nui","Trứng chiên","Thịt bò","Rau củ"],"nutrition":"Cung cấp carbohydrate từ nui, protein từ trứng và thịt bò, cùng chất xơ và vitamin từ rau củ.","goodFeedback":["Thành phần đa dạng, dễ kết hợp tinh bột, protein và rau củ.","Có thể thay đổi loại rau để tăng sự đa dạng."],"warnFeedback":["Nên kiểm soát lượng dầu khi chế biến.","Có thể tăng lượng rau củ để bổ sung chất xơ."],"tip":"Ưu tiên nhiều rau củ, lượng dầu vừa phải và khẩu phần thịt phù hợp."},
    {"name":"🍛 Cơm tấm","calories":"550 – 650 kcal","short_description":"Bữa sáng giàu năng lượng với cơm tấm, thịt hoặc chả trứng và rau củ.","items":["Cơm tấm","Sườn nướng hoặc chả trứng","Mỡ hành","Dưa leo","Củ cải/dưa chua","Nước mắm chua ngọt"],"nutrition":"Cung cấp năng lượng từ cơm, protein từ thịt hoặc trứng và một phần chất xơ từ rau củ, đồ chua.","goodFeedback":["Cung cấp lượng năng lượng tương đối cao cho buổi sáng.","Có thể kết hợp cơm, protein và rau củ trong cùng khẩu phần."],"warnFeedback":["Nên cân đối lượng cơm và thịt theo nhu cầu.","Mỡ hành và nước mắm nên sử dụng vừa phải."],"tip":"Tăng rau củ, dùng lượng mỡ hành và nước mắm vừa phải để bữa sáng cân đối hơn."},
    {"name":"🥗 Bún thịt nướng","calories":"Khoảng 500 kcal","short_description":"Món ăn đa dạng với bún, thịt nướng, rau sống, đồ chua và đậu phộng.","items":["Bún tươi","Thịt heo nướng","Chả giò (tùy khẩu phần)","Rau sống, giá đỗ, rau thơm","Dưa leo","Củ cải, cà rốt","Đậu phộng rang","Mỡ hành","Nước mắm chua ngọt"],"nutrition":"Kết hợp carbohydrate từ bún, protein từ thịt, chất xơ và vitamin từ rau củ, cùng chất béo từ đậu phộng và mỡ hành.","goodFeedback":["Thành phần phong phú, có nhiều nhóm thực phẩm.","Rau sống và đồ chua góp phần bổ sung chất xơ.","Có thể điều chỉnh khẩu phần theo nhu cầu."],"warnFeedback":["Nên kiểm soát lượng mỡ hành, đậu phộng và nước mắm.","Có thể giảm chả giò nếu khẩu phần đã có nhiều chất béo."],"tip":"Tăng rau sống, điều chỉnh lượng nước mắm và mỡ hành để bữa sáng cân đối hơn."},
]

# Weekly nutrition data
WEEKLY = [
    {'day': 'T2', 'calo': 480, 'target': 500},
    {'day': 'T3', 'calo': 510, 'target': 500},
    {'day': 'T4', 'calo': 390, 'target': 500},
    {'day': 'T5', 'calo': 520, 'target': 500},
    {'day': 'T6', 'calo': 450, 'target': 500},
    {'day': 'T7', 'calo': 370, 'target': 500},
    {'day': 'CN', 'calo': 490, 'target': 500},
]

# Navigation
NAV = [
    {'icon': '🏠', 'label': 'Trang chủ'},
    {'icon': '📷', 'label': 'Nhận diện món ăn'},
    {'icon': '📊', 'label': 'Lịch sử dinh dưỡng'},
    {'icon': '🎯', 'label': 'Mục tiêu cá nhân'},
    {'icon': '📚', 'label': 'Kiến thức dinh dưỡng'},
    {'icon': '⚙️', 'label': 'Cài đặt'},
]

def get_score_color(score):
    """Get color based on nutrition score"""
    if score >= 80:
        return '#047857'  # green
    elif score >= 60:
        return '#10b981'  # lighter green
    else:
        return '#f97316'  # orange

def get_bmi_category(bmi):
    """Get BMI category and color"""
    if bmi < 18.5:
        return {'label': 'Thiếu cân', 'color': '#f97316'}
    elif bmi < 23:
        return {'label': 'Bình thường', 'color': '#10b981'}
    elif bmi < 27.5:
        return {'label': 'Thừa cân', 'color': '#f97316'}
    else:
        return {'label': 'Béo phì', 'color': '#ef4444'}

def draw_score_ring(score):
    """Draw a circular nutrition score ring"""
    fig, ax = plt.subplots(figsize=(4, 4))
    color = get_score_color(score)
    
    # Draw the pie chart as a donut
    sizes = [score, 100 - score]
    colors = [color, '#e5e7eb']
    ax.pie(sizes, colors=colors, startangle=90, counterclock=False,
           wedgeprops=dict(width=0.5, edgecolor='white'))
    
    # Add text in center
    ax.text(0, 0, f'{score}\n/ 100', ha='center', va='center',
            fontsize=32, fontweight='bold', color=color)
    
    ax.set_aspect('equal')
    plt.tight_layout()
    return fig

def home_page():
    """Trang chủ - giới thiệu và gợi ý bữa sáng."""
    st.title("🏠 Trang Chủ - NutriScan")
    st.markdown("**Hệ thống Dinh dưỡng Bữa Sáng cho Học sinh THPT**")
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Cân nặng", "65 kg", "↑ 1 kg")
    with col2: st.metric("Chiều cao", "172 cm", "")
    with col3:
        bmi = 65 / (1.72 ** 2)
        category = get_bmi_category(bmi)
        st.metric("BMI", f"{bmi:.1f}", category["label"])
    with col4: st.metric("Năng lượng bữa sáng", "350–650 kcal", "Tham khảo")
    st.divider()
    st.subheader("🍽️ Gợi ý món ăn sáng cho học sinh THPT")
    st.markdown("Bữa sáng nên đa dạng các nhóm thực phẩm, kết hợp nguồn tinh bột, protein, rau củ và trái cây phù hợp với nhu cầu năng lượng của học sinh.")
    st.info("💡 **Lưu ý:** Lượng kcal là mức ước tính theo khẩu phần tham khảo. Giá trị thực tế thay đổi tùy nguyên liệu, khẩu phần và cách chế biến.")
    for row_start in range(0, len(DISHES), 3):
        cols = st.columns(3)
        for col, idx in zip(cols, range(row_start, min(row_start + 3, len(DISHES)))):
            dish = DISHES[idx]
            with col:
                summary = ", ".join(dish["items"][:4]) + ("..." if len(dish["items"]) > 4 else "")
                card = f"""<div class="rf-card"><div style="font-size:22px;font-weight:800;color:#047857;">{dish["name"]}</div><div style="margin:8px 0;color:#374151;font-size:14px;">{dish["short_description"]}</div><div class="rf-badge rf-badge-success">🔥 {dish["calories"]}</div><div style="font-size:13px;color:#4b5563;line-height:1.6;"><b>🥘 Thành phần:</b> {summary}</div></div>"""
                st.markdown(card, unsafe_allow_html=True)
                if st.button("📋 Xem chi tiết", key=f"detail_{idx}", use_container_width=True):
                    st.session_state.selected_dish = idx
                    st.session_state.page = "detail"
                    st.rerun()


def dish_detail_page():
    """Trang chi tiết món ăn."""
    if st.session_state.get("selected_dish") is None:
        st.warning("Vui lòng chọn một món ăn.")
        return
    if st.button("← Quay lại trang chủ"):
        st.session_state.page = "home"
        st.rerun()
    dish = DISHES[st.session_state.selected_dish]
    st.title(dish["name"])
    st.markdown("**Gợi ý dinh dưỡng dành cho học sinh THPT**")
    st.markdown("---")
    col1, col2 = st.columns([1, 1.4])
    with col1:
        card = f"""<div class="rf-card"><div style="font-size:28px;text-align:center;">🍽️</div><h2 style="text-align:center;margin-bottom:4px;">{dish["name"]}</h2><div style="text-align:center;font-size:24px;font-weight:800;color:#047857;">{dish["calories"]}</div><div style="text-align:center;color:#6b7280;margin-top:4px;">Năng lượng ước tính</div></div>"""
        st.markdown(card, unsafe_allow_html=True)
    with col2:
        st.subheader("📖 Mô tả")
        st.write(dish["short_description"])
        st.subheader("💪 Giá trị dinh dưỡng")
        st.write(dish["nutrition"])
    st.markdown("---")
    st.subheader("🥘 Thành phần món ăn")
    ingredient_cols = st.columns(3)
    for idx, item in enumerate(dish["items"]):
        with ingredient_cols[idx % 3]:
            st.markdown(f"""<div style="background:#ecfdf5;border:1.5px solid #a7f3d0;padding:.75rem;border-radius:.6rem;text-align:center;font-size:13px;font-weight:600;color:#047857;margin-bottom:.7rem;">{item}</div>""", unsafe_allow_html=True)
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("✅ Điểm tích cực")
        for feedback in dish["goodFeedback"]:
            st.markdown(f"<div class='good-feedback'>✅ {feedback}</div>", unsafe_allow_html=True)
    with col2:
        st.subheader("⚠️ Cần lưu ý")
        for feedback in dish["warnFeedback"]:
            st.markdown(f"<div class='warn-feedback'>⚠️ {feedback}</div>", unsafe_allow_html=True)
    st.markdown("---")
    st.subheader("💡 Gợi ý lựa chọn")
    tip = f"""<div class="rf-card" style="background:#fffbeb;border-color:#fde68a;"><div style="font-size:15px;line-height:1.7;color:#78350f;">{dish["tip"]}</div></div>"""
    st.markdown(tip, unsafe_allow_html=True)
    st.caption("Thông tin mang tính tham khảo giáo dục dinh dưỡng; nhu cầu năng lượng thực tế của mỗi học sinh có thể khác nhau.")


def nutrition_history():
    """Weekly nutrition history"""
    st.title("📊 Lịch Sử Dinh Dưỡng")
    st.markdown("**Theo dõi lượng calo hàng tuần**")
    st.markdown("---")
    
    df = pd.DataFrame(WEEKLY)
    
    # Summary stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        avg_calo = df['calo'].mean()
        st.metric("Trung bình Calo", f"{avg_calo:.0f}", "kcal/ngày")
    with col2:
        max_calo = df['calo'].max()
        st.metric("Cao nhất", f"{max_calo}", "kcal")
    with col3:
        min_calo = df['calo'].min()
        st.metric("Thấp nhất", f"{min_calo}", "kcal")
    with col4:
        target = df['target'].iloc[0]
        achieved = len(df[df['calo'] >= df['target']])
        st.metric("Đạt mục tiêu", f"{achieved}/7", "ngày")
    
    st.markdown("---")
    
    # Bar chart with better styling
    st.subheader("📈 Biểu Đồ Calo Tuần Này")
    fig, ax = plt.subplots(figsize=(14, 6))
    x = np.arange(len(df))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, df['calo'], width, label='Thực tế', 
                   color=['#10b981' if v >= t else '#f97316' for v, t in zip(df['calo'], df['target'])],
                   edgecolor='#d1d5db', linewidth=1.5)
    bars2 = ax.bar(x + width/2, df['target'], width, label='Mục tiêu', 
                   color='#d1d5db', edgecolor='#9ca3af', linewidth=1.5, alpha=0.7)
    
    ax.set_xlabel('Ngày', fontsize=12, fontweight='bold')
    ax.set_ylabel('Calories (kcal)', fontsize=12, fontweight='bold')
    ax.set_title('Lượng Calo - Tuần Này', fontsize=14, fontweight='bold', color='#047857')
    ax.set_xticks(x)
    ax.set_xticklabels(df['day'], fontsize=11, fontweight='bold')
    ax.legend(fontsize=11, loc='upper left')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.set_facecolor('#f9fafb')
    
    # Add value labels on bars
    for bar in bars1:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
    
    st.markdown("---")
    
    # Table view with styling
    st.subheader("📋 Chi Tiết Theo Ngày")
    df_display = df.copy()
    df_display['Trạng Thái'] = df_display.apply(
        lambda row: '✅ Đạt' if row['calo'] >= row['target'] else '❌ Chưa đạt',
        axis=1
    )
    st.dataframe(df_display[['day', 'calo', 'target', 'Trạng Thái']], 
                 use_container_width=True, hide_index=True)

def personal_goals():
    """Personal nutrition goals"""
    st.title("🎯 Mục Tiêu Cá Nhân")
    st.markdown("**Thiết lập và theo dõi mục tiêu dinh dưỡng của bạn**")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚙️ Mục Tiêu Hiện Tại")
        st.markdown("Điều chỉnh các mục tiêu dinh dưỡng hàng ngày:")
        
        daily_calories = st.slider("🔥 Calo mỗi ngày (kcal)", 1800, 3000, 2400, 50)
        st.caption("Khuyến cáo: 2400-2600 kcal cho học sinh THPT")
        
        protein_goal = st.slider("💪 Protein (g/ngày)", 40, 150, 80, 5)
        st.caption("Khuyến cáo: 70-80g mỗi ngày")
        
        carbs_goal = st.slider("🌾 Carbohydrate (g/ngày)", 100, 400, 250, 10)
        st.caption("Khuyến cáo: 250-300g mỗi ngày")
        
        fat_goal = st.slider("🧈 Chất Béo (g/ngày)", 30, 120, 70, 5)
        st.caption("Khuyến cáo: 60-75g mỗi ngày")
    
    with col2:
        st.subheader("📊 Thống Kê Hôm Nay")
        st.markdown("Tiến độ dinh dưỡng của bạn:")
        
        current_calories = 520
        current_protein = 28
        current_carbs = 58
        current_fat = 18
        
        # Create progress bars with styling
        st.markdown(f"""
        <div style='background: #ecfdf5; border: 1.5px solid #a7f3d0; padding: 1rem; border-radius: 0.75rem; margin-bottom: 0.75rem;'>
            <div style='display: flex; justify-content: space-between; margin-bottom: 0.5rem;'>
                <span style='font-weight: 600; color: #047857;'>🔥 Calo</span>
                <span style='font-weight: 600; color: #047857;'>{current_calories}/{daily_calories}</span>
            </div>
            <div style='background: #d1d5db; border-radius: 0.5rem; height: 8px; overflow: hidden;'>
                <div style='background: #10b981; height: 100%; width: {(current_calories/daily_calories)*100}%;'></div>
            </div>
            <div style='text-align: right; font-size: 12px; color: #6b7280; margin-top: 0.25rem;'>{(current_calories/daily_calories)*100:.1f}%</div>
        </div>
        
        <div style='background: #ecfdf5; border: 1.5px solid #a7f3d0; padding: 1rem; border-radius: 0.75rem; margin-bottom: 0.75rem;'>
            <div style='display: flex; justify-content: space-between; margin-bottom: 0.5rem;'>
                <span style='font-weight: 600; color: #047857;'>💪 Protein</span>
                <span style='font-weight: 600; color: #047857;'>{current_protein}/{protein_goal}g</span>
            </div>
            <div style='background: #d1d5db; border-radius: 0.5rem; height: 8px; overflow: hidden;'>
                <div style='background: #10b981; height: 100%; width: {(current_protein/protein_goal)*100}%;'></div>
            </div>
            <div style='text-align: right; font-size: 12px; color: #6b7280; margin-top: 0.25rem;'>{(current_protein/protein_goal)*100:.1f}%</div>
        </div>
        
        <div style='background: #ecfdf5; border: 1.5px solid #a7f3d0; padding: 1rem; border-radius: 0.75rem; margin-bottom: 0.75rem;'>
            <div style='display: flex; justify-content: space-between; margin-bottom: 0.5rem;'>
                <span style='font-weight: 600; color: #047857;'>🌾 Carbs</span>
                <span style='font-weight: 600; color: #047857;'>{current_carbs}/{carbs_goal}g</span>
            </div>
            <div style='background: #d1d5db; border-radius: 0.5rem; height: 8px; overflow: hidden;'>
                <div style='background: #10b981; height: 100%; width: {(current_carbs/carbs_goal)*100}%;'></div>
            </div>
            <div style='text-align: right; font-size: 12px; color: #6b7280; margin-top: 0.25rem;'>{(current_carbs/carbs_goal)*100:.1f}%</div>
        </div>
        
        <div style='background: #ecfdf5; border: 1.5px solid #a7f3d0; padding: 1rem; border-radius: 0.75rem;'>
            <div style='display: flex; justify-content: space-between; margin-bottom: 0.5rem;'>
                <span style='font-weight: 600; color: #047857;'>🧈 Chất Béo</span>
                <span style='font-weight: 600; color: #047857;'>{current_fat}/{fat_goal}g</span>
            </div>
            <div style='background: #d1d5db; border-radius: 0.5rem; height: 8px; overflow: hidden;'>
                <div style='background: #10b981; height: 100%; width: {(current_fat/fat_goal)*100}%;'></div>
            </div>
            <div style='text-align: right; font-size: 12px; color: #6b7280; margin-top: 0.25rem;'>{(current_fat/fat_goal)*100:.1f}%</div>
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

def settings_page():
    """Settings and preferences"""
    st.title("⚙️ Cài Đặt")
    st.markdown("**Quản lý hồ sơ và tùy chọn của bạn**")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👤 Thông Tin Cá Nhân")
        name = st.text_input("Tên", value="Học sinh", key="name_input")
        age = st.number_input("Tuổi", 10, 100, 15, key="age_input")
        gender = st.radio("Giới tính", ("Nam", "Nữ"), key="gender_input")
        height = st.number_input("Chiều cao (cm)", 100, 220, 172, key="height_input")
        weight = st.number_input("Cân nặng (kg)", 30, 200, 65, key="weight_input")
        
        if height and weight:
            bmi = weight / ((height/100) ** 2)
            category = get_bmi_category(bmi)
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%); border: 2px solid #{category['color'].replace('#', '')}; padding: 1rem; border-radius: 0.75rem; margin-top: 1rem;'>
                <div style='text-align: center;'>
                    <div style='color: #6b7280; font-size: 13px; font-weight: 600;'>Chỉ số BMI của bạn</div>
                    <div style='color: #047857; font-size: 32px; font-weight: 800; margin: 0.5rem 0;'>{bmi:.1f}</div>
                    <div style='background: {category['color']}; color: white; padding: 0.5rem 1rem; border-radius: 0.5rem; font-weight: 600; display: inline-block;'>{category['label']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("🎨 Tùy Chọn Hiển Thị")
        theme = st.selectbox("Chủ đề", ["Sáng (Mặc định)", "Tối"], key="theme_input")
        language = st.selectbox("Ngôn ngữ", ["Tiếng Việt 🇻🇳", "English 🇬🇧", "中文 🇨🇳"], key="language_input")
        notifications = st.checkbox("Bật thông báo nhắc nhở", value=True, key="notification_input")
        data_sharing = st.checkbox("Cho phép chia sẻ dữ liệu (ẩn danh) để cải thiện ứng dụng", value=False, key="sharing_input")
        
        st.markdown("---")
        st.subheader("📋 Quản Lý Dữ Liệu")
        col_export, col_reset = st.columns(2)
        
        with col_export:
            if st.button("📥 Xuất Dữ Liệu", use_container_width=True):
                st.success("✅ Dữ liệu của bạn sẽ được tải xuống dưới dạng CSV")
        
        with col_reset:
            if st.button("🔄 Đặt Lại", use_container_width=True):
                st.warning("⚠️ Hãy chắc chắn - hành động này không thể hoàn tác!")
    
    st.markdown("---")
    
    # Save settings
    col_save, col_info = st.columns([1, 3])
    with col_save:
        if st.button("💾 Lưu Cài Đặt", use_container_width=True):
            st.success("✅ Cài đặt của bạn đã được lưu thành công!")
    with col_info:
        st.caption("Cài đặt sẽ tự động lưu khi bạn thay đổi")

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
    elif selected == "Lịch sử dinh dưỡng":
        nutrition_history()
    elif selected == "Mục tiêu cá nhân":
        personal_goals()
    elif selected == "Kiến thức dinh dưỡng":
        nutrition_knowledge()
    elif selected == "Cài đặt":
        settings_page()
    
    # Check if detail page should be shown
    if st.session_state.page == 'detail':
        if st.button("← Quay lại trang chủ", key="back_button"):
            st.session_state.page = 'home'
            st.rerun()
        dish_detail_page()

if __name__ == "__main__":
    main()
