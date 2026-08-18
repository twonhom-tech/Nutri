# Hệ Thống Dinh Dưỡng (Nutrition System)

A Vietnamese nutrition tracking application built with Streamlit. This app helps track daily nutrition intake, provides meal recommendations, and educates users about balanced nutrition.

## Features

- 🏠 **Home Dashboard**: Overview of nutritional stats and featured dishes
- 📷 **Food Recognition**: Upload food images for nutritional analysis (placeholder for AI feature)
- 📊 **Nutrition History**: Weekly calorie tracking and trends
- 🎯 **Personal Goals**: Set and track personalized nutrition targets
- 📚 **Nutrition Knowledge**: Educational content about balanced diet and health
- ⚙️ **Settings**: Customize personal information and preferences

## Vietnamese Dishes Included

1. **Cơm tấm sườn bì chả** (Broken rice with pork ribs) - Score: 74/100
2. **Bánh mì thịt nguội** (Vietnamese sandwich) - Score: 62/100
3. **Phở bò tái chín** (Vietnamese beef soup) - Score: 88/100

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone or navigate to the project directory:
```bash
cd NutritionSystem
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the App

```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

## Project Structure

```
NutritionSystem/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── [archived React files] # Original React/Vite project files
```

## Key Dependencies

- **streamlit**: Web framework for building the UI
- **pandas**: Data manipulation and analysis
- **matplotlib**: Data visualization (charts and graphs)
- **numpy**: Numerical computations
- **pillow**: Image handling

## Usage Tips

- Use the sidebar to navigate between different sections
- Click on dishes to see detailed nutritional breakdowns
- Set your personal nutrition goals in the "Mục tiêu cá nhân" section
- Check the "Kiến thức dinh dưỡng" section for nutrition education

## Language

The application interface is primarily in **Vietnamese (Tiếng Việt)**.

## Future Enhancements

- [ ] AI-powered food recognition from images
- [ ] Database integration for meal logging
- [ ] User authentication and personalization
- [ ] Push notifications for nutrition reminders
- [ ] Mobile app version
- [ ] Integration with fitness trackers

## License

MIT License - Feel free to modify and use for your projects.

---

For any questions or improvements, feel free to contribute!
