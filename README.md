# 🎮 Detoxify: Gamified Digital Wellbeing

**Detoxify** is an AI-powered, gamified web application designed to help users reduce their screen time. By combining OCR technology for automated tracking with a "Play-to-Earn" rewards system, Detoxify turns the difficult task of digital detoxing into an engaging game.

> ⚠️ **Note:** This project is currently in its **Prototype Stage**. Certain advanced features like ML-based prediction and financial withdrawals are simulated for demonstration purposes.

---

## 🚀 Key Features

### 1. 🤖 AI-Powered Tracking (OCR)
- Upload screenshots of your phone's "Digital Wellbeing" or "Screen Time" page.    
- **EasyOCR** automatically extracts:
  - Total Screen Time
  - YouTube Usage
  - Instagram Usage
- No manual data entry required!!

### 2. 🏆 Gamified Challenges
Complete difficulties levels to earn points:
- **Easy:** *The 10% Cut* (Reduce daily usage by 10%).
- **Medium:** *YouTube Diet* & *Reel Rehab* (Limit specific apps under 3 hours).
- **Hard:** *Monk Mode* (Total usage under 2 hours).

### 3. 📊 Analytics Dashboard
- Interactive **Plotly** charts visualizing your digital history.
- Compare Total Time vs. Social Media usage side-by-side.
- Daily "Tip of the Day" for mental wellness.
- Real-time "Redeemable Value" calculation based on user performance.
  

> 🧪 Experimental Features (In-Development / Demo Only)

> These features below represents the future roadmap of Detoxify and are currently in the **simulation/testing phase**:

### 4. 🔮 AI Prediction Model:
  - **Status:** *Conceptual/Experimental.*
  - Integrated with **scikit-learn (Linear Regression)** to model and forecast weekly screen time trends.
  - **Logic:** The algorithmic logic is fully functional; however, the model currently operates in a **"Cold Start"** phase and requires consistent user logging to improve predictive accuracy. (have not tested with the accuracy at present, so can't tell as per now)
    
### 5. 💸 UPI & Bank Withdrawal:
  - **Status:** *Demo UI.*
  - A simulated interface for UPI and Bank transfers to demonstrate the "cash-out" user journey.
  - **Logic:**  For the prototype, these transactions are **simulated** and do not connect to live payment gateways. We will try in future to contact with UPI gateways or Bank for real-time transactions.
    
---

## 🛠️ Tech Stack

- **Frontend:** [Streamlit](https://streamlit.io/)
- **Backend:** Python
- **Database:** SQLite (Serverless)
- **Machine Learning:** Scikit-learn (Linear Regression)
- **Computer Vision:** EasyOCR (Text Extraction)
- **Visualization:** Plotly Express

---

## ⚙️ Installation & Setup

Follow these steps to run the project locally on your machine.

### Prerequisites
- Python 3.8 or higher installed.

### 1. Clone the Repository
```bash
git clone https://github.com/shreyaspai-2005/Detoxify
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
