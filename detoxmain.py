import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import time
import random
import easyocr
import numpy as np
from PIL import Image
import re
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression


st.set_page_config(page_title="Detoxify - Gamified Screen Time", page_icon="🎮", layout="wide")

SCREEN_TIME_TIPS = [
    "Turn on 'Grayscale Mode' in your phone settings. It makes the screen less stimulating.",
    "Charge your phone in a different room while you sleep to avoid late-night scrolling.",
    "Use the '20-20-20' rule: Every 20 mins, look at something 20 feet away for 20 seconds.",
    "Disable non-essential notifications (like social media likes) to reduce distraction triggers.",
    "Replace the first 30 minutes of phone time in the morning with a short walk or reading.",
    "Delete social media apps on weekends for a mini-detox.",
    "Set app limits directly in your phone's Digital Wellbeing settings.",
    "Leave your phone behind when you go to the bathroom.",
    "Use an actual alarm clock instead of your phone to wake up.",
    "Designate 'phone-free zones' in your house, like the dining table.",
    "Do a 1hr walk/jog outside without your phone to be fit and healthy!",
    "Try to play a physical game to boost your stamina and lose weight!",
    "Read a physical book for 30 minutes before bed instead of watching reels."
]


def init_db():
    conn = sqlite3.connect('detox_users.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY, 
                    password TEXT, 
                    points INTEGER, 
                    balance_inr REAL,
                    baseline_screentime INTEGER
                )''')

    c.execute('''CREATE TABLE IF NOT EXISTS daily_logs (
                    username TEXT,
                    date TEXT,
                    total_minutes INTEGER,
                    youtube_minutes INTEGER,
                    instagram_minutes INTEGER,
                    PRIMARY KEY (username, date)
                )''')

    c.execute('''CREATE TABLE IF NOT EXISTS challenges_log (
                    username TEXT,
                    challenge_id TEXT,
                    date TEXT,
                    PRIMARY KEY (username, challenge_id, date)
                )''')
    conn.commit()
    conn.close()

def run_query(query, params=(), fetch=False):
    conn = sqlite3.connect('detox_users.db')
    c = conn.cursor()
    c.execute(query, params)
    if fetch:
        data = c.fetchall()
        conn.close()
        return data
    conn.commit()
    conn.close()


def reset_user_progress(username):
    """Resets all logs, points, and challenge history for a specific user."""
    conn = sqlite3.connect('detox_users.db')
    c = conn.cursor()
    c.execute("DELETE FROM daily_logs WHERE username = ?", (username,))
    c.execute("DELETE FROM challenges_log WHERE username = ?", (username,))
    c.execute("UPDATE users SET points = 0, balance_inr = 0.0 WHERE username = ?", (username,))
    conn.commit()
    conn.close()
    st.toast("♻️ Account Reset Successful! All progress wiped.", icon="🗑️")
    time.sleep(1)


def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

def register_user(username, password):
    try:
        run_query("INSERT INTO users (username, password, points, balance_inr, baseline_screentime) VALUES (?, ?, ?, ?, ?)", 
                  (username, make_hashes(password), 0, 0.0, 300)) # default is 300
        return True
    except sqlite3.IntegrityError:
        return False

def login_user(username, password):
    data = run_query("SELECT * FROM users WHERE username = ?", (username,), fetch=True)
    if data:
        if check_hashes(password, data[0][1]):
            return data[0]
    return None


def get_user_stats(username):
    data = run_query("SELECT points, balance_inr, baseline_screentime FROM users WHERE username = ?", (username,), fetch=True)
    return data[0] if data else (0, 0.0, 300)

def add_points(username, amount):
    current_stats = get_user_stats(username)
    new_points = current_stats[0] + amount
    run_query("UPDATE users SET points = ? WHERE username = ?", (new_points, username))
    st.toast(f"🎉 +{amount} Points Earned!", icon="🪙")

def time_to_str(mins):
    h, m = divmod(mins, 60)
    return f"{h}h {m}m"

def parse_ocr(image):
    """Extracts time data from screenshot with app-specific matching"""
    reader = easyocr.Reader(['en'], gpu=False)
    result = reader.readtext(np.array(image), detail=0)

    app_times = {}
    current_app = None

    time_pattern = re.compile(r'(?:(\d+)\s*[hH]\s*)?(?:(\d+)\s*[mM])?')

    for text in result:
        clean_text = text.strip()

        match = time_pattern.fullmatch(clean_text)
        is_time = False
        minutes = 0
        
        if match:
            h_str, m_str = match.groups()
            if h_str or m_str:
                is_time = True
                h = int(h_str) if h_str else 0
                m = int(m_str) if m_str else 0
                minutes = (h * 60) + m

        if is_time and current_app and minutes > 0:
            app_times[current_app.lower()] = minutes
            current_app = None
        elif not is_time and len(clean_text) > 2:
            current_app = clean_text

    youtube = app_times.get('youtube', 0)
    instagram = app_times.get('instagram', 0)
    
    detected_values = list(app_times.values())
    if detected_values:
        total = sum(detected_values)
    else:
        total = 0

    return total, youtube, instagram


CHALLENGES = {
    "C1": {
        "title": "The 10% Cut", 
        "desc": "Reduce screentime by 10% per day for 1 week.", 
        "points": 25, 
        "difficulty": "EASY", 
        "days": 7,
        "reward_text": "+25 pts/week"
    },
    "C2": {
        "title": "YouTube Diet", 
        "desc": "Keep YouTube under 3 hours per day for 2 weeks.", 
        "points": 50, 
        "difficulty": "MEDIUM", 
        "days": 14,
        "reward_text": "+50 pts/2 weeks"
    },
    "C3": {
        "title": "Monk Mode", 
        "desc": "Total screentime under 2 hours per day for 1 month.", 
        "points": 100, 
        "difficulty": "HARD", 
        "days": 30,
        "reward_text": "+100 pts/1 month"
    },
    "C4": {
        "title": "Reel Rehab", 
        "desc": "Keep Instagram under 3 hours per day for 2 weeks.", 
        "points": 50, 
        "difficulty": "MEDIUM", 
        "days": 14,
        "reward_text": "+50 pts/2 weeks"
    }
}

def check_challenges(username, today_log):
    stats = get_user_stats(username)
    baseline = stats[2]
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    completed_today = run_query("SELECT challenge_id FROM challenges_log WHERE username = ? AND date = ?", (username, today_str), fetch=True)
    completed_ids = [x[0] for x in completed_today]
    
    # 1. Challenge 1 (Total)
    if "C1" not in completed_ids:
        target = baseline * 0.9
        if today_log['total'] > 0 and today_log['total'] <= target:
            run_query("INSERT INTO challenges_log VALUES (?, ?, ?)", (username, "C1", today_str))
            count = run_query("SELECT COUNT(*) FROM challenges_log WHERE username = ? AND challenge_id = ?", (username, "C1"), fetch=True)[0][0]
            if count == CHALLENGES["C1"]["days"]:
                add_points(username, CHALLENGES["C1"]["points"])
                st.toast(f"🏆 Challenge C1 Completed! +{CHALLENGES['C1']['points']} Points!", icon="🎉")

    # 2. Challenge 2 (YouTube)
    if "C2" not in completed_ids:
        if today_log['total'] > 0 and today_log['youtube'] <= 180:
            run_query("INSERT INTO challenges_log VALUES (?, ?, ?)", (username, "C2", today_str))
            count = run_query("SELECT COUNT(*) FROM challenges_log WHERE username = ? AND challenge_id = ?", (username, "C2"), fetch=True)[0][0]
            if count == CHALLENGES["C2"]["days"]:
                add_points(username, CHALLENGES["C2"]["points"])
                st.toast(f"🏆 Challenge C2 Completed! +{CHALLENGES['C2']['points']} Points!", icon="🎉")

    # 3. Challenge 3 (Total Hard)
    if "C3" not in completed_ids:
        if today_log['total'] > 0 and today_log['total'] <= 120:
            run_query("INSERT INTO challenges_log VALUES (?, ?, ?)", (username, "C3", today_str))
            count = run_query("SELECT COUNT(*) FROM challenges_log WHERE username = ? AND challenge_id = ?", (username, "C3"), fetch=True)[0][0]
            if count == CHALLENGES["C3"]["days"]:
                add_points(username, CHALLENGES["C3"]["points"])
                st.toast(f"🏆 Challenge C3 Completed! +{CHALLENGES['C3']['points']} Points!", icon="🎉")

    # 4. Challenge 4 (Instagram)
    if "C4" not in completed_ids:
        if today_log['total'] > 0 and today_log['instagram'] <= 180:
            run_query("INSERT INTO challenges_log VALUES (?, ?, ?)", (username, "C4", today_str))
            count = run_query("SELECT COUNT(*) FROM challenges_log WHERE username = ? AND challenge_id = ?", (username, "C4"), fetch=True)[0][0]
            if count == CHALLENGES["C4"]["days"]:
                add_points(username, CHALLENGES["C4"]["points"])
                st.toast(f"🏆 Challenge C4 Completed! +{CHALLENGES['C4']['points']} Points!", icon="🎉")


def main():
    init_db()
    
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['username'] = None
    
    if not st.session_state['logged_in']:
        st.markdown("<h1 style='text-align: center;'>🎮 Detoxify</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Gamify your digital wellbeing.</p>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Login")
                if submit:
                    user = login_user(username, password)
                    if user:
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = username
                        st.session_state['daily_tip'] = random.choice(SCREEN_TIME_TIPS)
                        st.rerun()
                    else:
                        st.error("Invalid Username or Password")
        
        with tab2:
            with st.form("reg_form"):
                new_user = st.text_input("New Username")
                new_pass = st.text_input("New Password", type="password")
                base_time = st.number_input("Avg Daily Screentime (mins)", value=300)
                submit_reg = st.form_submit_button("Register")
                if submit_reg:
                    if register_user(new_user, new_pass):
                        run_query("UPDATE users SET baseline_screentime = ? WHERE username = ?", (base_time, new_user))
                        st.success("Account created! Please Login.")
                    else:
                        st.error("Username already taken.")
                        
    else:
        user = st.session_state['username']
        stats = get_user_stats(user)
        points = stats[0]
        balance = stats[1]
        baseline = stats[2]
        
        with st.sidebar:
            st.title(f"Hi, {user}!")
            st.metric("Points", points, delta_color="off")
            st.metric("Wallet Balance", f"₹{balance:.2f}")
            st.markdown("---")
            menu = st.radio("Navigate", ["Dashboard", "Log Data", "Challenges", "Prediction", "Rewards Store", "Withdraw Funds"])
            
            st.markdown("---")
            if st.button("⚠️ Reset Progress (Debug)", type="primary"):
                reset_user_progress(user)
                st.rerun()
                
            if st.button("Logout"):
                st.session_state['logged_in'] = False
                if 'daily_tip' in st.session_state:
                    del st.session_state['daily_tip']
                st.rerun()

        if menu == "Dashboard":
            st.title("📊 Your Progress")
            col1, col2, col3 = st.columns(3)
            col1.metric("Target Screentime", time_to_str(int(baseline * 0.9)), "10% Reduction Goal")
            col2.metric("Current Points", points)
            col3.metric("Redeemable Value", f"₹{(points / 100):.2f}")
            
            history = run_query("SELECT date, total_minutes, youtube_minutes, instagram_minutes FROM daily_logs WHERE username = ? ORDER BY date", (user,), fetch=True)
            if history:
                df = pd.DataFrame(history, columns=['Date', 'Total Time', 'YouTube Time', 'Instagram Time'])
                
                fig = px.bar(
                    df, 
                    x='Date', 
                    y=['Total Time', 'YouTube Time', 'Instagram Time'], 
                    barmode='group', 
                    title="Your Digital History"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No data logged yet. Go to 'Log Data' to start!")
            
            if 'daily_tip' in st.session_state:
                st.info(f"💡 **Tip of the Day:** {st.session_state['daily_tip']}")

        elif menu == "Log Data":
            st.title("📝 Log Today's Activity")
            st.write("Upload your phone's 'Digital Wellbeing' or 'Screen Time' summary.")
            
            img_file = st.file_uploader("Upload Screenshot", type=['png', 'jpg', 'jpeg'])
            
            if img_file:
                image = Image.open(img_file)
                st.image(image, caption="Uploaded Image", width=200)
                
                if st.button("Analyze Image"):
                    with st.spinner("Scanning..."):
                        try:
                            t_ocr, yt_ocr, insta_ocr = parse_ocr(image)
                            st.session_state['ocr_results'] = {'total': t_ocr, 'youtube': yt_ocr, 'instagram': insta_ocr}
                        except Exception as e:
                            st.error(f"OCR Error: {e}")

                if 'ocr_results' in st.session_state:
                    res = st.session_state['ocr_results']
                    st.info(f"**Analysis Result:** Total: {res['total']} mins | YouTube: {res['youtube']} mins | Instagram: {res['instagram']} mins")
                    
                    if st.button("Confirm & Save This Data"):
                        date_str = datetime.now().strftime("%Y-%m-%d")
                        run_query("INSERT OR REPLACE INTO daily_logs VALUES (?, ?, ?, ?, ?)", 
                                  (user, date_str, res['total'], res['youtube'], res['instagram']))
                        
                        check_challenges(user, {'total': res['total'], 'youtube': res['youtube'], 'instagram': res['instagram']})
                        
                        st.success("✅ Data Logged Successfully!")
                        del st.session_state['ocr_results']
                        time.sleep(1.5)
                        st.rerun()

        elif menu == "Challenges":
            st.title("🏆 Active Challenges")
            today_str = datetime.now().strftime("%Y-%m-%d")
            
            log_data = run_query("SELECT total_minutes, youtube_minutes, instagram_minutes FROM daily_logs WHERE username = ? AND date = ?", (user, today_str), fetch=True)
            current_total = log_data[0][0] if log_data else 0
            current_yt = log_data[0][1] if log_data else 0
            current_insta = log_data[0][2] if log_data else 0
            
            completed_today_data = run_query("SELECT challenge_id FROM challenges_log WHERE username = ? AND date = ?", (user, today_str), fetch=True)
            completed_ids_today = [x[0] for x in completed_today_data]

            for cid, data in CHALLENGES.items():
                count_data = run_query("SELECT COUNT(*) FROM challenges_log WHERE username = ? AND challenge_id = ?", (user, cid), fetch=True)
                days_completed = count_data[0][0] if count_data else 0
                target_days = data['days']
                
                progress_pct = min(1.0, days_completed / target_days)

                limit_str = ""
                is_failed_today = False
                today_val = 0
                
                if cid == "C1":
                    target_min = int(baseline * 0.9)
                    limit_str = f"Limit: {target_min}m"
                    if current_total > target_min and current_total > 0: is_failed_today = True
                    today_val = current_total
                elif cid == "C2":
                    limit_str = "Limit: 180m"
                    if current_yt > 180: is_failed_today = True
                    today_val = current_yt
                elif cid == "C3":
                    limit_str = "Limit: 120m"
                    if current_total > 120: is_failed_today = True
                    today_val = current_total
                elif cid == "C4":
                    limit_str = "Limit: 180m"
                    if current_insta > 180: is_failed_today = True
                    today_val = current_insta

                if cid in completed_ids_today:
                    today_status_msg = "✅ Day Complete"
                elif is_failed_today:
                    today_status_msg = f"🔴 Today Failed ({today_val}m / {limit_str})"
                else:
                    today_status_msg = f"🟢 Today on Track ({today_val}m / {limit_str})"

                with st.container():
                    st.markdown(f"**{data['difficulty']}**: {data['title']}")
                    st.caption(data['desc'])
                    
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        st.progress(progress_pct)
                        st.caption(f"📅 Progress: **Day {days_completed}** of {target_days} | {today_status_msg}")
                    
                    with col_b:
                        st.markdown(f"**{data['reward_text']}**")
                        if days_completed >= target_days:
                            st.success("CLAIMED!")
                        elif cid in completed_ids_today:
                            st.info("DAY DONE")
                        else:
                            st.warning("PENDING")
                    st.divider()


        elif menu == "Prediction":
            st.title("🔮 AI Screen Time Predictor")
            st.write("We use a Linear Regression model to predict your future screen time based on your history.")
            
            data = run_query("SELECT date, total_minutes FROM daily_logs WHERE username = ? ORDER BY date", (user,), fetch=True)
            
            if len(data) < 3:
                st.warning("⚠️ Not enough data! Please log at least 3 days of screen time to unlock predictions.")
            else:
                df = pd.DataFrame(data, columns=['Date', 'Total Minutes'])
                df['Date'] = pd.to_datetime(df['Date'])
                df['Day_Ordinal'] = df['Date'].map(datetime.toordinal)
                
                X = df[['Day_Ordinal']]
                y = df['Total Minutes']
                model = LinearRegression()
                model.fit(X, y)

                days_to_predict = st.slider("Forecast Range (Days)", 1, 7, 3)
                max_date = df['Date'].max()
                
                future_dates = []
                future_preds = []
                
                for i in range(1, days_to_predict + 1):
                    next_date = max_date + timedelta(days=i)
                    next_ord = next_date.toordinal()
                    # Predict
                    pred_val = model.predict([[next_ord]])[0]
                    future_dates.append(next_date)
                    future_preds.append(max(0, int(pred_val))) #prevents -ve min
                    
                pred_df = pd.DataFrame({'Date': future_dates, 'Predicted Minutes': future_preds})
                
                st.subheader(f"📅 Forecast for Next {days_to_predict} Days")
                
                history_chart = df[['Date', 'Total Minutes']].copy()
                history_chart['Type'] = 'Actual History'
                
                pred_chart = pred_df.rename(columns={'Predicted Minutes': 'Total Minutes'})
                pred_chart['Type'] = 'AI Prediction'
                
                combined_df = pd.concat([history_chart, pred_chart])
                
                fig = px.line(combined_df, x='Date', y='Total Minutes', color='Type', markers=True, 
                              title="Screen Time Trend & Forecast")
                fig.update_traces(line=dict(width=3))
                st.plotly_chart(fig, use_container_width=True)
                
                st.dataframe(pred_df)


        elif menu == "Rewards Store":
            st.title("🏪 Rewards Store")
            st.info("ℹ️ **Exchange Rate:** 100 Points = ₹5.00")
            col1, col2 = st.columns(2)
            col1.metric("Your Points", points)
            col2.metric("Current Balance", f"₹{balance:.2f}")
            st.subheader("Redeem Options")
            
            packs = [(5, 100), (10, 250), (25, 500), (50, 985)]
            
            for rs, pts in packs:
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    c1.markdown(f"#### 💰 ₹{rs}.00 Pack")
                    c1.write(f"Cost: {pts} Points")
                    if c2.button(f"Redeem ₹{rs}", key=f"redeem_{rs}"):
                        if points >= pts:
                            new_bal = balance + float(rs)
                            new_pts = points - pts
                            run_query("UPDATE users SET points = ?, balance_inr = ? WHERE username = ?", (new_pts, new_bal, user))
                            st.balloons()
                            st.rerun()
                        else:
                            st.error(f"Need {pts - points} more points!")


        elif menu == "Withdraw Funds":
            st.title("💸 Withdraw Funds")
            st.info(f"**Available Balance: ₹{balance:.2f}**")
            st.subheader("Withdrawal Details")
            
            amount = st.number_input("Amount to Withdraw (₹)", min_value=0.0, step=1.0, format="%.2f")
            method = st.radio("Select Withdrawal Method", ["UPI", "Bank Transfer"], horizontal=True)
            
            details_valid = False
            if method == "UPI":
                upi_id = st.text_input("Enter UPI ID (e.g., user@upi)")
                if upi_id: details_valid = True
            else:
                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    acc_num = st.text_input("Account Number")
                with col_b2:
                    ifsc = st.text_input("IFSC Code")
                if acc_num and ifsc: details_valid = True
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Initiate Withdrawal", type="primary"):
                if amount <= 0:
                    st.error("Please enter a valid amount.")
                elif amount > balance:
                    st.error(f"Insufficient Funds! Your balance is only ₹{balance:.2f}")
                elif not details_valid:
                        st.error("Please fill in all payment details.")
                else:
                    with st.spinner("Connecting to Payment Gateway..."):
                        time.sleep(2) 
                    new_balance = balance - amount
                    run_query("UPDATE users SET balance_inr = ? WHERE username = ?", (new_balance, user))
                    st.success(f"✅ Withdrawal of ₹{amount:.2f} Successful!")
                    st.balloons()
                    time.sleep(2)
                    st.rerun()

if __name__ == "__main__":
    main()