import streamlit as st
import pandas as pd
import random

# --- 1. 環境與 UI 設定 ---
st.set_page_config(page_title="AssetFlow | v3.8.4 Pro Full", layout="wide")

# --- 2. 說明文案模組 (Sidebar) ---
def show_documentation():
    with st.sidebar:
        st.title("📚 系統說明手冊")
        st.info("專業量化選號工具：結合歷史權重與最新慣性分析。")
        with st.expander("🔬 生存演算法規則"):
            st.write("""
            - **總和**: 110 - 190
            - **跨距**: 30 - 45
            - **奇偶比**: 2:4, 3:3, 4:2
            - **尾數**: 單一尾數重複不超過 2
            """)
        with st.expander("🎯 v3.8 觀察家核心"):
            st.write("""
            - **鄰號加權**: 最新期鄰近號碼 1.5x
            - **連號強制**: 提升生成連號之機率
            - **雲端同步**: 直接連動 Google Sheets
            """)
        st.divider()
        st.caption("AssetFlow Project by Marco")

# --- 3. 核心演算邏輯 ---
def is_advanced_survival(nums):
    total = sum(nums)
    r_range = max(nums) - min(nums)
    even_count = len([n for n in nums if n % 2 == 0])
    tails = [n % 10 for n in nums]
    max_tail_rep = max([tails.count(t) for t in set(tails)]) if tails else 0
    return (110 <= total <= 190) and (30 <= r_range <= 45) and (2 <= even_count <= 4) and (max_tail_rep <= 2)

def get_pro_insight_rec(data):
    if data.empty: return sorted(random.sample(range(1, 50), 6)), []
    
    # 抓取第一行 (最新一期)
    last_nums = sorted([int(x) for x in data.iloc[0].values])
    neighbor_pool = []
    for n in last_nums:
        neighbor_pool.extend([n-1, n, n+1])
    neighbor_pool = set([n for n in neighbor_pool if 1 <= n <= 49])
    
    # 權重地圖
    all_nums = data.values.flatten()
    freq = pd.Series(all_nums).value_counts()
    weights = {i: freq.get(i, 1) for i in range(1, 50)}
    for n in neighbor_pool:
        weights[n] *= 1.5 
        
    for _ in range(5000):
        candidate = sorted(random.choices(list(weights.keys()), weights=list(weights.values()), k=6))
        # 必須包含慣性鄰號與連號
        has_momentum = any(c in neighbor_pool for c in candidate)
        has_consecutive = any(candidate[i+1] - candidate[i] == 1 for i in range(len(candidate)-1))
        
        if len(set(candidate)) == 6 and has_momentum and has_consecutive:
            if is_advanced_survival(candidate):
                return candidate, last_nums
    return sorted(random.sample(range(1, 50), 6)), last_nums

# --- 4. 數據讀取與快取 ---
show_documentation()
SHEET_ID = "1EKdI8hhHikVy2ZyV1zRoQse2ngEF7cDAA5QU-gojgvQ"
GID = "204446723"
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

@st.cache_data(ttl=60)
def load_data(url):
    try:
        df = pd.read_csv(url)
        cols = ['獎號1','獎號2','獎號3','獎號4','獎號5','獎號6']
        # 確保資料完整性
        df = df[cols].dropna().astype(int)
        return df
    except:
        return pd.DataFrame()

df = load_data(url)

# --- 5. UI 呈現 ---
st.title("🛡️ AssetFlow v3.8.4 | 旗艦完整版")

if not df.empty:
    st.success(f"📡 數據連線正常 (分析期數：{len(df)})")
    
    # 初始化 session_state
    if 'rec_v38' not in st.session_state: st.session_state.rec_v38 = []
    if 'test_nums' not in st.session_state: st.session_state.test_nums = [1,2,3,4,5,6]

    tab1, tab2, tab3 = st.tabs(["🚀 智慧推薦", "📡 慣性分析", "🔄 歷史回測"])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("💡 智慧選號生成")
            if st.button("執行動態慣性選號"):
                rec, last = get_pro_insight_rec(df)
                st.session_state.rec_v38 = rec
                st.session_state.last_v38 = last
            
            if st.session_state.rec_v38:
                res = st.session_state.rec_v38
                st.markdown(f"### 推薦號碼：:green[{res}]")
                st.write("**統計指標：**")
                cols = st.columns(3)
                cols[0].write(f"🌡️ 總和: {sum(res)}")
                cols[1].write(f"📏 跨距: {max(res)-min(res)}")
                has_con = any(res[i+1] - res[i] == 1 for i in range(len(res)-1))
                cols[2].write(f"🔗 連號: {'✅ 有' if has_con else '❌ 無'}")
        
        with c2:
            st.subheader("📘 專家解讀")
            st.info("該組合已考量最新一期的鄰號加權，並透過生存法則過濾掉高難度組合。")
            if 'last_v38' in st.session_state:
                st.write(f"參考基準：{st.session_state.last_v38}")

    with tab2:
        st.subheader("🔍 最新慣性分析基準")
        last_nums = df.iloc[0].values.tolist()
        st.write(f"當前最新開獎紀錄：**{last_nums}**")
        st.write("🟢 慣性補強號碼池：")
        neighbor_map = sorted(list(set(sum([[x-1,x,x+1] for x in last_nums], []))))
        st.write([n for n in neighbor_map if 1 <= n <= 49])
        st.caption("※ 系統會針對上述鄰號區間給予額外權重，模擬開獎的『拖牌』慣性。")

    with tab3:
        st.subheader("🔄 歷史回測與驗證")
        # 帶入推薦功能
        if st.session_state.rec_v38:
            if st.button(f"📥 帶入推薦號碼：{st.session_state.rec_v38}"):
                st.session_state.test_nums = st.session_state.rec_v38
                st.rerun()

        # 手動調整與回測
        selected = st.multiselect("手動調整號碼進行回測", options=list(range(1, 50)), default=st.session_state.test_nums, max_selections=6)
        
        if len(selected) == 6:
            user_set = set(selected)
            win_stats = {3: 0, 4: 0, 5: 0}
            for _, row in df.iterrows():
                match_count = len(user_set.intersection(set(row.values)))
                if match_count in win_stats:
                    win_stats[match_count] += 1
            
            r1, r2, r3 = st.columns(3)
            r1.metric("中 3 碼 (普獎)", f"{win_stats[3]} 次")
            r2.metric("中 4 碼", f"{win_stats[4]} 次")
            rate = (sum(win_stats.values()) / len(df)) * 100
            r3.metric("歷史存活頻率", f"{rate:.2f}%")
else:
    st.error("🚨 無法連接數據庫。請確保 Google Sheets 標題列為：獎號1, 獎號2, 獎號3, 獎號4, 獎號5, 獎號6")