# 🎮 Detoxify: Gamified Digital Wellbeing

**Detoxify** is an AI-powered, gamified web application designed to help users reduce their screen time. By combining OCR technology for automated tracking with a "Play-to-Earn" rewards system, Detoxify turns the difficult task of digital detoxing into an engaging game.

## 🚀 Key Features

### 1. 🤖 AI-Powered Tracking (OCR)
- Upload screenshots of your phone's "Digital Wellbeing" or "Screen Time" page.
- **EasyOCR** automatically extracts:
  - Total Screen Time
  - YouTube Usage
  - Instagram Usage
- No manual data entry required!

### 2. 🏆 Gamified Challenges
Complete difficulties levels to earn points:
- **Easy:** *The 10% Cut* (Reduce daily usage by 10%).
- **Medium:** *YouTube Diet* & *Reel Rehab* (Limit specific apps under 3 hours).
- **Hard:** *Monk Mode* (Total usage under 2 hours).

### 3. 🔮 AI Prediction Model
- Uses **Linear Regression (Machine Learning)** to analyze your past behavior.
- Forecasts your screen time for the next 7 days to help you plan ahead.

### 4. 💰 Virtual Economy
- Earn **Points** for every successful day.
- Redeem points for **Wallet Balance** (in ₹ INR). []
- **Withdrawal System:** Simulated interface for UPI and Bank Transfers.

### 5. 📊 Analytics Dashboard
- Interactive **Plotly** charts visualizing your digital history.
- Compare Total Time vs. Social Media usage side-by-side.
- Daily "Tip of the Day" for mental wellness.

---

## 🛠️ Tech Stack

- **Frontend:** [Streamlit](https://streamlit.io/)
- **Backend:** Python
- **Database:** SQLite (Serverless)
- **Machine Learning:** Scikit-learn (Linear Regression)
- **Computer Vision:** EasyOCR & OpenCV (Text Extraction)
- **Visualization:** Plotly Express

---

## ⚙️ Installation & Setup

Follow these steps to run the project locally on your machine.

### Prerequisites
- Python 3.8 or higher installed.

### 1. Clone the Repository
```bash
git clone [https://github.com/yourusername/detoxify.git](https://github.com/yourusername/detoxify.git)
cd detoxify
```

### 2. Install the packages in the requirements.txt.

### 3. Run the Application
```bash
streamlit run app.py
```
### 📝 License
[GNU General Public License (GPL) v3.0](LICENSE)

`This project is created as a 5th Sem Mini-Project for the Dept of AIML Engineering.`

### Contributors
This project was developed as a 3rd year mini-project for AI-ML by the following team members:

* **Sharvesh R** - USN: 1NH23AI147 (Role: Project Report and licensing)
* **Shreyas Pai** - USN: 1NH23AI151 (Role: Lead Backend Developer)
* **Sumanth Kalyan K** - USN: 1NH23AI159 (Role: Frontend Developer)

### Acknowledgements
Special Thanks to :
* Dr. N.V. Uma Reddy (HoD of AIML (NHCE)) & Dr. Sreejith S. (Associate Professor of AIML (NHCE), and our project guide) & Prof. Rajasree (Senior Assistant Professor of AIML (NHCE), and our project coordinator).
* `2025-2026, AIML Department, New Horizon College of Engineering, Bengaluru, Karnataka, India`
