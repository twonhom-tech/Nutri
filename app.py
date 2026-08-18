import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge
import numpy as np

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
</style>
""", unsafe_allow_html=True)

# Vietnamese dishes database
DISHES = [
    {
        'name': 'Cơm tấm sườn bì chả',
        'image': 'https://images.unsplash.com/photo-1569050467447-ce54b3bbc37d?w=600&h=400&fit=crop&auto=format',
        'calories': 520,
        'protein': 28,
        'carbs': 58,
        'fat': 18,
        'fiber': 3.2,
        'vitamins': 72,
        'score': 74,
        'items': ['Cơm tấm (200g)', 'Sườn nướng (80g)', 'Bì heo (30g)', 'Chả trứng (40g)', 'Dưa leo (50g)', 'Cà chua (30g)'],
        'goodFeedback': [
            'Cung cấp đủ protein từ thịt sườn và chả.',
            'Có rau tươi kèm theo (dưa leo, cà chua).',
            'Năng lượng phù hợp cho buổi học sáng.',
        ],
        'warnFeedback': [
            'Hàm lượng chất xơ còn thấp — nên thêm rau xanh.',
            'Chất béo từ bì heo khá cao, nên ăn vừa phải.',
        ],
    },
    {
        'name': 'Bánh mì thịt nguội',
        'image': 'https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=600&h=400&fit=crop&auto=format',
        'calories': 380,
        'protein': 18,
        'carbs': 45,
        'fat': 14,
        'fiber': 2.1,
        'vitamins': 55,
        'score': 62,
        'items': ['Bánh mì (100g)', 'Thịt nguội (60g)', 'Pate (20g)', 'Dưa leo (40g)', 'Hành ngò (10g)', 'Tương ớt (10g)'],
        'goodFeedback': [
            'Dễ ăn, tiện lợi cho buổi sáng.',
            'Có rau thơm và dưa leo.',
        ],
        'warnFeedback': [
            'Thiếu chất xơ và vitamin đáng kể.',
            'Pate và thịt nguội chứa nhiều natri — không nên ăn mỗi ngày.',
            'Nên bổ sung thêm 1 ly sữa hoặc trái cây.',
        ],
    },
    {
        'name': 'Phở bò tái chín',
        'image': 'https://images.unsplash.com/photo-1618160702438-9b02ab6515c9?w=600&h=400&fit=crop&auto=format',
        'calories': 450,
        'protein': 32,
        'carbs': 52,
        'fat': 10,
        'fiber': 4.5,
        'vitamins': 85,
        'score': 88,
        'items': ['Bánh phở (150g)', 'Thịt bò tái (60g)', 'Thịt bò chín (40g)', 'Giá đỗ (50g)', 'Hành lá (15g)', 'Rau thơm (20g)'],
        'goodFeedback': [
            'Protein cao, chất béo thấp — rất cân bằng.',
            'Giàu chất xơ từ rau giá và rau thơm.',
            'Đạt chuẩn dinh dưỡng bữa sáng học sinh.',
        ],
        'warnFeedback': [
            'Nước dùng có thể chứa nhiều natri — không uống hết nước.',
        ],
    },
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
    """Home page - overview of nutrition"""
    st.title("🏠 Trang Chủ - NutriScan")
    st.markdown("**Hệ thống Dinh dưỡng Bữa Sáng cho Học sinh**")
    
    # User stats section
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
    
    # Featured dishes
    st.subheader("🍽️ Các Món Ăn Gợi Ý")
    st.markdown("---")
    
    cols = st.columns(3)
    for idx, dish in enumerate(DISHES):
        with cols[idx]:
            # Create card container
            st.image(dish['image'], use_column_width=True)
            
            # Dish name with styling
            st.markdown(f"### {dish['name']}")
            
            # Score and nutrition info in columns
            col_score, col_info = st.columns([1, 1.5])
            with col_score:
                fig = draw_score_ring(dish['score'])
                st.pyplot(fig, use_container_width=True)
                plt.close(fig)
            
            with col_info:
                st.markdown(f"""
                **{dish['calories']} kcal**
                
                🥛 Protein: {dish['protein']}g  
                🌾 Carbs: {dish['carbs']}g  
                🧈 Fat: {dish['fat']}g  
                🥦 Fiber: {dish['fiber']}g
                """)
            
            # Detail button
            if st.button("📋 Chi tiết", key=f"detail_{idx}", use_container_width=True):
                st.session_state.selected_dish = idx
                st.session_state.page = "detail"
                st.rerun()

def dish_detail_page():
    """Detailed view of a selected dish"""
    if 'selected_dish' not in st.session_state:
        st.warning("Vui lòng chọn một món ăn")
        return
    
    if st.button("← Quay lại", use_container_width=False):
        st.session_state.page = 'home'
        st.rerun()
    
    dish = DISHES[st.session_state.selected_dish]
    
    st.title(f"📋 {dish['name']}")
    st.markdown("**Phân tích chi tiết bởi NutriScan AI**")
    st.markdown("---")
    
    # Image and score
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        st.image(dish['image'], use_column_width=True, caption=dish['name'])
    
    with col2:
        st.subheader("Xếp hạng")
        fig = draw_score_ring(dish['score'])
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
    
    st.markdown("---")
    
    # Nutritional info
    st.subheader("📊 Thông Tin Dinh Dưỡng")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class='metric'>
            <div style='font-size: 24px; text-align: center;'>🔥</div>
            <div style='text-align: center; color: #047857; font-weight: 800; font-size: 18px;'>{dish['calories']}</div>
            <div style='text-align: center; color: #6b7280; font-size: 12px; font-weight: 600;'>Năng lượng (kcal)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='metric'>
            <div style='font-size: 24px; text-align: center;'>💪</div>
            <div style='text-align: center; color: #047857; font-weight: 800; font-size: 18px;'>{dish['protein']}g</div>
            <div style='text-align: center; color: #6b7280; font-size: 12px; font-weight: 600;'>Protein</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='metric'>
            <div style='font-size: 24px; text-align: center;'>🌾</div>
            <div style='text-align: center; color: #047857; font-weight: 800; font-size: 18px;'>{dish['carbs']}g</div>
            <div style='text-align: center; color: #6b7280; font-size: 12px; font-weight: 600;'>Carbs</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class='metric'>
            <div style='font-size: 24px; text-align: center;'>🧈</div>
            <div style='text-align: center; color: #047857; font-weight: 800; font-size: 18px;'>{dish['fat']}g</div>
            <div style='text-align: center; color: #6b7280; font-size: 12px; font-weight: 600;'>Chất Béo</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class='metric'>
            <div style='font-size: 24px; text-align: center;'>🥦</div>
            <div style='text-align: center; color: #047857; font-weight: 800; font-size: 18px;'>{dish['fiber']}g</div>
            <div style='text-align: center; color: #6b7280; font-size: 12px; font-weight: 600;'>Chất Xơ</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Macronutrient chart
    st.subheader("📊 Cấu Trúc Dinh Dưỡng")
    macro_data = pd.DataFrame({
        'Chất Dinh Dưỡng': ['Protein', 'Carbs', 'Fat', 'Fiber'],
        'Giá Trị': [dish['protein'], dish['carbs'], dish['fat'], dish['fiber']],
        'Màu': ['#10b981', '#6ee7b7', '#fde68a', '#f97316']
    })
    fig, ax = plt.subplots(figsize=(12, 5))
    bars = ax.bar(macro_data['Chất Dinh Dưỡng'], macro_data['Giá Trị'], color=macro_data['Màu'], edgecolor='#d1d5db', linewidth=1.5)
    ax.set_ylabel('Grams', fontsize=12, fontweight='bold')
    ax.set_xlabel('Nutrients', fontsize=12, fontweight='bold')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.set_facecolor('#f9fafb')
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}g',
                ha='center', va='bottom', fontweight='bold', fontsize=11)
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
    
    st.markdown("---")
    
    # Ingredients
    st.subheader("🥘 Thành Phần")
    cols = st.columns(3)
    for idx, item in enumerate(dish['items']):
        with cols[idx % 3]:
            st.markdown(f"""
            <div style='background: #ecfdf5; border: 1.5px solid #a7f3d0; padding: 0.75rem; border-radius: 0.5rem; text-align: center; font-size: 13px; font-weight: 600; color: #047857;'>
                {item}
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Feedback sections
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✅ Điểm Tốt")
        for feedback in dish['goodFeedback']:
            st.markdown(f"<div class='good-feedback'>✅ {feedback}</div>", unsafe_allow_html=True)
    
    with col2:
        st.subheader("⚠️ Cần Chú Ý")
        for feedback in dish['warnFeedback']:
            st.markdown(f"<div class='warn-feedback'>⚠️ {feedback}</div>", unsafe_allow_html=True)

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
        st.title("📷 Nhận Diện Món Ăn")
        st.markdown("**Công nghệ AI nhận diện dinh dưỡng từ ảnh**")
        st.markdown("---")
        st.info("🚀 Chức năng nhận diện AI sẽ sớm được cập nhật với khả năng phân tích ảnh thực tế!")
        uploaded_file = st.file_uploader("📸 Tải lên ảnh món ăn", type=['jpg', 'jpeg', 'png'])
        if uploaded_file:
            col1, col2 = st.columns([1, 1])
            with col1:
                st.image(uploaded_file, caption="Ảnh đã tải", use_column_width=True)
            with col2:
                st.markdown("""
                **Thông tin được phân tích:**
                - 📊 Cấu trúc dinh dưỡng
                - 🔥 Tổng năng lượng
                - 💪 Hàm lượng protein
                - 🥦 Chất xơ và vitamin
                - ⚠️ Lời khuyên cá nhân hóa
                """)
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
