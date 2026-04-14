import streamlit as st
import pandas as pd
import random

# --- 1. 系統初始化 ---
st.set_page_config(page_title="AssetFlow Pro", layout="wide")

# 固定 Sheet ID
SHEET_ID = "1EKdI8hhHikVy2ZyV1zRoQse2ngEF7cDAA5QU-gojgvQ"

# --- 2. 核心演算邏輯 ---
def is_advanced_survival(nums, mode):
    total = sum(nums)
    r_range = max(nums) - min(nums)
    # 根據模式設定生存邊界
    t_min, t_max = (110, 190) if mode == "大樂透" else (65, 135)
    r_min, r_max = (30, 45) if mode == "大樂透" else (20, 35)
    # 奇偶檢查 (1:5 ~ 5:1 之間，排除全奇或全偶)
    even_count = len([n for n in nums if n % 2 == 0])
    return (t_min <= total <= t_max) and (r_min <= r_range <= r_max) and (1 <= even_count <= len(nums)-1)

def get_pro_insight_rec(data, mode):
    if data.empty: return []
    max_num = 49 if mode == "大樂透" else 39
    pick_k = 6 if mode == "大樂透" else 5
    
    last_nums = sorted([int(x) for x in data.iloc[0].values])
    neighbor_pool = set([n for n in sum([[x-1,x,x+1] for x in last_nums], []) if 1 <= n <= max_num])
    
    all_nums = data.values.flatten()
    freq = pd.Series(all_nums).value_counts()
    weights = {i: freq.get(i, 1) for i in range(1, max_num + 1)}
    for n in neighbor_pool: weights[n] *= 1.5 
        
    for _ in range(5000):
        candidate = sorted(random.choices(list(weights.keys()), weights=list(weights.values()), k=pick_k))
        if len(set(candidate)) == pick_k:
            has_consecutive = any(candidate[i+1] - candidate[i] == 1 for i in range(len(candidate)-1))
            if has_consecutive and is_advanced_survival(candidate, mode):
                return candidate
    return sorted(random.sample(range(1, max_num + 1), pick_k))

# --- 3. UI 主介面 ---
st.title("🛡️ AssetFlow 戰情室 v3.9.2")

# A. 模式選擇 (置頂 Radio)
mode = st.radio("🎰 選擇分析模式", ["大樂透", "今彩 539"], horizontal=True)

# B. 讀取對應 GID (請填入你的 539 GID)
GID_539 = "1711116840" 
GID = "204446723" if mode == "大樂透" else GID_539
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

@st.cache_data(ttl=60)
def load_data(url, current_mode):
    try:
        df = pd.read_csv(url)
        cols = ['獎號1','獎號2','獎號3','獎號4','獎號5']
        if current_mode == "大樂透": cols.append('獎號6')
        return df[cols].dropna().astype(int)
    except: return pd.DataFrame()

df = load_data(url, mode)

# C. 戰情看版
if not df.empty:
    c1, c2 = st.columns([1, 1])
    
    with c1:
        st.subheader(f"🚀 {mode} 智慧推薦")
        if st.button(f"✨ 啟動分析並執行回測"):
            res = get_pro_insight_rec(df, mode)
            st.session_state.current_res = res
            
    if 'current_res' in st.session_state:
        res = st.session_state.current_res
        st.success(f"### 推薦號碼：{res}")
        
        # --- 自動回測邏輯 (直接顯示，不跳轉) ---
        user_set = set(res)
        win_stats = {3: 0, 4: 0, 5: 0}
        for _, row in df.iterrows():
            match = len(user_set.intersection(set(row.values)))
            if match in win_stats: win_stats[match] += 1
        
        st.divider()
        st.subheader("🔄 即時生存回測 (歷史表現)")
        r1, r2, r3 = st.columns(3)
        r1.metric("中 3 碼", f"{win_stats[3]} 次")
        r2.metric("中 4 碼", f"{win_stats[4]} 次")
        rate = (sum(win_stats.values()) / len(df)) * 100
        r3.metric("總生存率", f"{rate:.2f}%")
        st.caption(f"數據基準：近 {len(df)} 期歷史獎號")
else:
    st.error("🚨 數據讀取失敗，請確認 GID 是否正確。")