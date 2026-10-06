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
    "Số liệu dinh dưỡng từng thành phần món ăn do nhóm nghiên cứu khoa học (NCKH) "
    "tự thực hiện đo khối lượng và phân tích từng thành phần — không lấy từ "
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
def load_mon_table():
    """Bảng món ăn → thành phần chuẩn (mon_thanh_phan.csv).

    Mỗi món có 1 "lớp nhận diện" (lop_nhan_dien_mon) là lớp Roboflow đặc trưng,
    duy nhất chỉ xuất hiện ở món đó (ví dụ lớp "Banh cuon" → món "Bánh cuốn").
    Khi lớp này được YOLO phát hiện trong ảnh, hệ thống coi như đã NHẬN DIỆN
    ĐƯỢC MÓN ĂN, và từ đó liệt kê + cộng dồn TOÀN BỘ các thành phần chuẩn của
    món (theo số liệu nhóm NCKH tự đo khối lượng từng thành phần), chứ không
    chỉ tính riêng lớp vừa phát hiện.
    """
    if not MON_CSV_PATH.is_file():
        raise FileNotFoundError(f"Không tìm thấy bảng món ăn: {MON_CSV_PATH.name}")
    df = pd.read_csv(MON_CSV_PATH)
    df["ma_lop_thanh_phan"] = df["ma_lop_thanh_phan"].fillna("")
    df["lop_nhan_dien_mon"] = df["lop_nhan_dien_mon"].fillna("")
    return df


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


def nhan_dien_mon_va_tinh_dinh_duong(mon_table, nutrition_table, predictions):
    """Nhận diện MÓN ĂN trước, rồi liệt kê + cộng dồn thành phần bên trong món.

    Quy trình:
    1. Lấy tập các lớp YOLO phát hiện được trong ảnh.
    2. Với mỗi món trong `mon_table` có "lớp nhận diện" (lop_nhan_dien_mon) khớp
       với 1 lớp vừa phát hiện → coi là ĐÃ NHẬN DIỆN ĐƯỢC MÓN ĂN đó. Dinh dưỡng
       của món lấy TOÀN BỘ các thành phần chuẩn đã khai báo trong bảng (số liệu
       nhóm NCKH tự đo khối lượng từng thành phần của món), không phụ thuộc
       việc từng thành phần nhỏ có thực sự được YOLO khoanh vùng riêng hay không.
    3. Mỗi món chỉ tính dinh dưỡng MỘT LẦN dù ảnh có nhiều khung cùng lớp neo
       (ví dụ nhiều khung "Banh cuon" vẫn chỉ là 1 phần Bánh cuốn).
    4. Những lớp phát hiện được nhưng KHÔNG thuộc thành phần của món nào vừa
       nhận diện (ví dụ 1 món ăn kèm thêm, hoặc chưa nhận diện được món nào)
       được tính bổ sung riêng theo bảng thành phần đơn lẻ (dinh_duong_thanh_phan.csv),
       mỗi lớp tính 1 lần.

    Trả về: (dishes_found, extra_details, totals, unmatched_classes, counts)
    """
    counts = Counter(prediction["class"] for prediction in predictions)
    detected_classes = set(counts)

    anchor_rows = mon_table[
        (mon_table["loai_dong"] == "tong_mon") & (mon_table["lop_nhan_dien_mon"] != "")
    ]
    matched_mon = anchor_rows[anchor_rows["lop_nhan_dien_mon"].isin(detected_classes)]

    totals = {"calo": 0.0, "protein": 0.0, "carb": 0.0, "fat": 0.0}
    dishes_found = []
    accounted_classes = set()

    for _, tong_row in matched_mon.iterrows():
        ma_mon = tong_row["ma_mon"]
        comp_rows = mon_table[
            (mon_table["ma_mon"] == ma_mon) & (mon_table["loai_dong"] == "thanh_phan")
        ]
        dishes_found.append({
            "ten_mon": tong_row["ten_mon"],
            "lop_nhan_dien": tong_row["lop_nhan_dien_mon"],
            "components": comp_rows,
            "tong": tong_row,
        })
        accounted_classes.add(tong_row["lop_nhan_dien_mon"])
        for lop in comp_rows["ma_lop_thanh_phan"]:
            if lop:
                accounted_classes.add(lop)
        totals["calo"] += float(tong_row["calo_kcal"])
        totals["protein"] += float(tong_row["protein_g"])
        totals["carb"] += float(tong_row["carb_g"])
        totals["fat"] += float(tong_row["fat_g"])

    extra_classes = detected_classes - accounted_classes
    extra_details = []
    for component_code in sorted(extra_classes):
        if component_code not in nutrition_table.index:
            continue
        row = nutrition_table.loc[component_code]
        mass = float(row["khoi_luong_mac_dinh_g"])  # tính 1 lần/lớp, không nhân theo số khung
        ratio = mass / 100
        detail = {
            "ten": row["ten_thanh_phan"],
            "ma": component_code,
            "so_khung": counts[component_code],
            "khoi_luong": mass,
            "calo": float(row["calo_100g"]) * ratio,
            "protein": float(row["protein_100g"]) * ratio,
            "carb": float(row["carb_100g"]) * ratio,
            "fat": float(row["fat_100g"]) * ratio,
            "nguon": row.get("nguon_so_lieu", "") if hasattr(row, "get") else "",
        }
        extra_details.append(detail)
        for nutrient in totals:
            totals[nutrient] += detail[nutrient]

    unmatched_classes = extra_classes - set(nutrition_table.index)
    return dishes_found, extra_details, totals, unmatched_classes, counts


def roboflow_detection_page():
    st.title("📷 Nhận Diện Thành Phần Món Ăn")
    st.markdown(
        "Roboflow Workflow dùng YOLO để phát hiện thành phần trong ảnh; hệ thống "
        "sẽ **nhận diện tên món ăn trước** (qua thành phần đặc trưng của món, ví dụ "
        "thấy \"vỏ bánh cuốn\" → nhận diện món Bánh cuốn), sau đó liệt kê toàn bộ "
        "các thành phần chuẩn bên trong món đó và cộng dồn dinh dưỡng (mỗi món chỉ "
        "tính 1 phần, không nhân theo số khung phát hiện được)."
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
        mon_table = load_mon_table()
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
    dishes_found, extra_details, totals, unmatched_classes, counts = (
        nhan_dien_mon_va_tinh_dinh_duong(mon_table, nutrition_table, predictions)
    )

    if dishes_found:
        ten_cac_mon = ", ".join(d["ten_mon"] for d in dishes_found)
        nhan_dien_label = f"🍽️ Món ăn nhận diện: {ten_cac_mon}"
    else:
        nhan_dien_label = "⚠️ Chưa nhận diện được món ăn cụ thể — tính theo từng thành phần riêng lẻ"
    st.markdown(f"""
    <div class="rf-card">
        <span class="rf-badge rf-badge-success">{nhan_dien_label}</span>
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
        <div class="rf-source-note">📖 {NGUON_TU_DO}</div>
    </div>
    """, unsafe_allow_html=True)

    for dish in dishes_found:
        st.markdown(f"#### 🍽️ {dish['ten_mon']}")
        st.caption(
            f"Nhận diện qua lớp \"{dish['lop_nhan_dien']}\" — liệt kê toàn bộ thành phần "
            f"chuẩn của món (số liệu nhóm NCKH tự đo khối lượng từng thành phần)."
        )
        comp_df = dish["components"][
            ["thanh_phan", "khoi_luong_g", "calo_kcal", "protein_g", "carb_g", "fat_g"]
        ].copy()
        comp_df.columns = ["Thành phần", "Khối lượng (g)", "Calo", "Protein (g)", "Carb (g)", "Fat (g)"]
        tong = dish["tong"]
        comp_df.loc[len(comp_df)] = [
            "— Tổng cả món —", tong["khoi_luong_g"], tong["calo_kcal"],
            tong["protein_g"], tong["carb_g"], tong["fat_g"],
        ]
        st.dataframe(
            comp_df.style.format({
                "Khối lượng (g)": "{:.0f}", "Calo": "{:.0f}",
                "Protein (g)": "{:.1f}", "Carb (g)": "{:.1f}", "Fat (g)": "{:.1f}",
            }),
            use_container_width=True,
            hide_index=True,
        )

    if extra_details:
        st.markdown("#### ➕ Thành phần phát hiện thêm (ngoài món chính)")
        st.caption(
            "Các lớp này được YOLO phát hiện nhưng không thuộc thành phần chuẩn của "
            "món vừa nhận diện (hoặc chưa nhận diện được món nào) — tính riêng theo "
            "bảng thành phần đơn lẻ, mỗi lớp 1 phần, không nhân theo số khung."
        )
        extra_df = pd.DataFrame(extra_details)[
            ["ten", "so_khung", "khoi_luong", "calo", "protein", "carb", "fat", "nguon"]
        ]
        extra_df.columns = [
            "Thành phần", "Số khung phát hiện", "Khối lượng tính (g)", "Calo",
            "Protein (g)", "Carb (g)", "Fat (g)", "Nguồn số liệu",
        ]
        st.dataframe(
            extra_df.style.format({
                "Khối lượng tính (g)": "{:.0f}", "Calo": "{:.0f}",
                "Protein (g)": "{:.1f}", "Carb (g)": "{:.1f}", "Fat (g)": "{:.1f}",
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

    if unmatched_classes:
        st.warning(
            "Các lớp được phát hiện nhưng chưa có số liệu dinh dưỡng (thành phần/món "
            "chưa có trong dữ liệu NCKH) nên chưa được tính: "
            + ", ".join(sorted(unmatched_classes))
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

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Cân nặng", "65 kg", "↑ 1 kg")
    with col2:
        st.metric("Chiều cao", "172 cm", "")
    with col3:
        bmi = 65 / (1.72 ** 2)
        category = get_bmi_category(bmi)
        st.metric("BMI", f"{bmi:.1f}", category['label'])
    with col4:
        st.metric("Năng lượng hôm nay", "520 kcal", "-30 kcal")

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