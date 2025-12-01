import streamlit as st
import re
import pandas as pd
import numpy as np
from datetime import datetime

# ==========================================
# 1. НАСТРОЙКИ И КОНФИГУРАЦИЯ
# ==========================================
st.set_page_config(
    page_title="Syndicate Odds Analyst (Final)",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- БОКОВАЯ ПАНЕЛЬ ---
with st.sidebar:
    st.header("⚙️ Банк и Риск")
    BANKROLL = st.number_input("Ваш Банк ($)", value=1000, step=100)
    KELLY_FRACTION = st.slider("Дробный Келли (Сила ставки)", 0.1, 0.5, 0.3, 0.05)
    
    st.divider()
    st.markdown("### 🧠 КАК ЧИТАТЬ ГРАФИКИ")
    st.markdown("📉 **Цена (Odds) падает**: Вероятность растет.")
    st.markdown("📈 **Риск (R) растет**: Букмекер нагружает исход.")
    st.markdown("✅ **СИГНАЛ**: Линии идут в разные стороны (Крест).")

# ==========================================
# 2. МАТЕМАТИЧЕСКОЕ ЯДРО (R-MODEL)
# ==========================================

def calculate_r_metrics_universal(history_data, mode="3way"):
    """
    Считает Private Margin (PM) и Risk (R) для любого кол-ва исходов.
    """
    if not history_data: return None
    processed = []
    base_pm = None 
    
    for row in history_data:
        odds = row['odds'] # Список кэфов
        
        # 1. Считаем Имплицитную вероятность (Implied Probability)
        implied = [1/k for k in odds]
        sum_imp = sum(implied)
        
        # 2. Десятичная маржа
        margin_dec = sum_imp - 1
        
        # 3. Private Margin (PM) - распределение маржи
        pm = [(margin_dec * (i / sum_imp)) for i in implied]
        
        row['pm'] = pm
        
        # 4. R-Migration (Изменение риска относительно открытия)
        if base_pm is None:
            base_pm = pm
            row['r'] = [0.0] * len(odds)
        else:
            r_values = []
            for i in range(len(odds)):
                base_val = base_pm[i]
                curr_val = pm[i]
                # Защита от деления на 0
                val = ((curr_val - base_val) / base_val * 100) if base_val != 0 else 0
                r_values.append(val)
            row['r'] = r_values
            
        processed.append(row)
    return processed

def calculate_kelly_stake(odds, fair_prob, bank, frac):
    """Калькулятор Келли"""
    b = odds - 1
    p = fair_prob
    q = 1 - p
    f = (b * p - q) / b
    return max(0, round(f * frac * bank, 2))

# ==========================================
# 3. УМНЫЕ ПАРСЕРЫ (CLEANERS)
# ==========================================

def parse_pinnacle_universal(raw_text):
    data = []
    lines = raw_text.strip().split('\n')
    current_year = datetime.now().year
    mode = "unknown"
    
    for line in lines:
        # Пропускаем закрытые линии
        if "Closed" in line: continue
        
        # --- ОЧИСТКА ДАННЫХ ---
        # Удаляем слова Early, Live, HT, FT
        clean_line = re.sub(r'(Early|Live|HT|FT)', '', line, flags=re.IGNORECASE)
        # Удаляем счет (1-0, 2-1) и минуты (87')
        clean_line = re.sub(r'\d+-\d+', '', clean_line)
        clean_line = re.sub(r"\d+'", '', clean_line)
        
        parts = re.split(r'\s+', clean_line.strip())
        
        if len(parts) >= 2:
            try:
                nums = []
                for p in parts:
                    # Чистим от u/o (under/over)
                    clean_p = p.lower().replace('u','').replace('o','')
                    
                    # Если есть слеш (2/2.5) - это линия, пропускаем
                    if '/' in clean_p: continue 
                        
                    if clean_p.replace('.','').isdigit():
                        val = float(clean_p)
                        # Фильтр кэфов (от 1.01 до 100)
                        if 1.01 <= val <= 100.0:
                            nums.append(val)
                
                final_odds = []
                
                # --- ЛОГИКА ОПРЕДЕЛЕНИЯ ТИПА (1X2 или TOTALS) ---
                if len(nums) == 3:
                    # Считаем сумму вероятностей
                    imp_sum = sum([1/n for n in nums])
                    
                    # Если сумма > 1.25 (Маржа > 25%), значит среднее число - это ЛИНИЯ (напр. 2.5), а не кэф
                    if imp_sum > 1.25:
                        final_odds = [nums[0], nums[2]] # Берем края
                        mode = "2way"
                    else:
                        final_odds = nums # Берем все 3 (1X2)
                        mode = "3way"
                        
                elif len(nums) == 2:
                    final_odds = nums
                    mode = "2way"
                    
                elif len(nums) > 3:
                     # Если куча чисел, берем 1-е и последнее (края), предполагая 2-way
                     final_odds = [nums[0], nums[-1]]
                     mode = "2way"

                if final_odds:
                    # --- ПАРСИНГ ВРЕМЕНИ ---
                    # Ищем время (12:11)
                    date_match = re.search(r'\d{1,2}:\d{2}', line)
                    time_str = date_match.group(0) if date_match else "00:00"
                    
                    # Ищем дату (25/11)
                    day_match = re.search(r'\d{1,2}/\d{1,2}', line)
                    day_str = day_match.group(0) if day_match else datetime.now().strftime("%d/%m")
                    
                    full_date_str = f"{current_year}-{day_str.replace('/','-')} {time_str}"
                    
                    try:
                        dt_obj = datetime.strptime(full_date_str, "%Y-%d-%m %H:%M")
                    except:
                        dt_obj = datetime.now()

                    data.append({
                        "odds": final_odds,
                        "dt": dt_obj,
                        "time_str": f"{day_str} {time_str}"
                    })
            except: continue

    if not data: return None
    # Сортируем от старых к новым
    data.sort(key=lambda x: x['dt'])
    
    # Считаем R-метрики
    data = calculate_r_metrics_universal(data, mode)
    
    # Считаем % изменения первого кэфа (Home или Over)
    move_pct = (data[-1]['odds'][0] - data[0]['odds'][0]) / data[0]['odds'][0] * 100
    
    return {
        "open": data[0],
        "current": data[-1],
        "history": data,
        "move_pct": move_pct,
        "mode": mode
    }

def parse_market_universal(raw_text):
    """Простой парсер для софтов"""
    targets = []
    lines = raw_text.strip().split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # Пропускаем пустые и цифры
        if not line or line[0].isdigit(): 
            i += 1; continue
            
        name = line
        if i+1 < len(lines):
            try:
                # Ищем кэфы в следующей строке
                parts = re.split(r'\s+', lines[i+1])
                nums = [float(p) for p in parts if p.replace('.','').isdigit()]
                
                if nums:
                    # Берем первый кэф (Home или Over) для сравнения
                    targets.append({"name": name, "odds": nums[0]}) 
                i += 2 
            except: i += 1
        else: i += 1
    return {"softs": targets}

# ==========================================
# 4. ЛОГИКА АНАЛИЗА И СИГНАЛОВ
# ==========================================

def run_universal_analysis(pin_data, market_data):
    mode = pin_data['mode']
    curr_r = pin_data['current']['r'][0] # R первого исхода
    trend = pin_data['move_pct']
    
    status = "NEUTRAL"
    msg = "Рынок спокоен."
    color = "gray"
    
    # --- СЦЕНАРИИ СИНДИКАТА ---
    
    # 1. SMART MONEY (Идеальный вход)
    # Цена падает (-1.5%), Риск растет (>0%)
    if trend < -1.5 and curr_r > 0:
        status = "💎 SMART MONEY"
        color = "green"
        msg = f"Истинный прогруз! Цена упала ({trend:.1f}%), а букмекер нагрузил риск (+{curr_r:.1f}%)."
        
    # 2. DEFENSIVE (Опасно)
    # Цена падает, но Риск падает (Букмекер "прячется")
    elif trend < -1.5 and curr_r < -2.0:
        status = "🛡️ DEFENSIVE"
        color = "orange"
        msg = f"Цена упала, но букмекер снизил риск ({curr_r:.1f}%). Возможно, режут лимиты."
        
    # 3. ANOMALY / TRAP
    # Цена стоит, а Риск скачет
    elif abs(trend) < 1.0 and abs(curr_r) > 10.0:
        status = "⚠️ ANOMALY"
        color = "red"
        msg = "Цена стоит на месте, а Риск аномально скачет. Манипуляция?"
        
    # 4. HUGE VALUE (Поиск ошибок без тренда)
    elif abs(trend) < 1.0:
        status = "🔎 SCANNING"
        msg = "Тренда нет, ищем ошибки в линиях софтов..."

    # --- ПОИСК ВАЛУЕВ У СОФТОВ ---
    targets = []
    
    # Считаем Честную Цену (Fair Price)
    current_odds = pin_data['current']['odds']
    sum_imp = sum([1/k for k in current_odds])
    
    # Вероятность 1-го исхода без маржи
    fair_prob = (1/current_odds[0]) / sum_imp
    fair_price = 1 / fair_prob
    
    for s in market_data['softs']:
        roi = (s['odds'] / fair_price) - 1
        if roi > 0.025: # Валуй > 2.5%
            stake = calculate_kelly_stake(s['odds'], fair_prob, BANKROLL, KELLY_FRACTION)
            targets.append({
                "name": s['name'], 
                "odds": s['odds'], 
                "roi": roi*100, 
                "stake": stake
            })
            
    # Уточнение статуса, если нашли супер-валуй
    if targets and status == "🔎 SCANNING":
        best_roi = max([t['roi'] for t in targets])
        if best_roi > 5.0:
            status = "🔥 GAP VALUE"
            color = "green"
            msg = f"Найден огромный разрыв цен! Софты отстают на {best_roi:.1f}%."
            
    return status, msg, color, targets, curr_r, mode

# ==========================================
# 5. ИНТЕРФЕЙС (UI)
# ==========================================

st.title("💎 Syndicate Odds Analyst")
st.caption("Universal Engine v7.0 (Final)")

c1, c2 = st.columns(2)
pin_txt = c1.text_area("1. Pinnacle History (Любой формат)", height=150, 
                       placeholder="Вставь данные... (1X2 или Тоталы)\nПрограмма сама поймет формат.")
mkt_txt = c2.text_area("2. Market Odds", height=150, 
                       placeholder="Вставь список БК...\nBet365\n2.05...")

if st.button("🚀 ЗАПУСТИТЬ АНАЛИЗ", type="primary", use_container_width=True):
    if pin_txt and mkt_txt:
        pin = parse_pinnacle_universal(pin_txt)
        mkt = parse_market_universal(mkt_txt)
        
        if pin:
            status, msg, color, targets, r_val, mode = run_universal_analysis(pin, mkt)
            
            st.divider()
            
            # --- ЗАГОЛОВОК ---
            color_map = {"green": ":green", "orange": ":orange", "red": ":red", "gray": ":gray"}
            target_name = "Home (П1)" if mode == "3way" else "Over (ТБ) / Фора 1"
            
            st.markdown(f"### Режим: **{mode.upper()}**. Цель анализа: **{target_name}**")
            st.header(f"{color_map[color]}[ {status} ]")
            st.info(f"**Вердикт:** {msg}")
            
            # --- РЕКОМЕНДАЦИИ ---
            if targets:
                st.subheader("📢 ЛУЧШИЕ ТОЧКИ ВХОДА")
                # Сортируем по ROI
                best_bet = sorted(targets, key=lambda x: x['roi'], reverse=True)[0]
                
                # КРАСИВАЯ КАРТОЧКА
                st.success(
                    f"🏆 **СТАВИТЬ НА:** {target_name}\n\n"
                    f"🏦 **БК:** {best_bet['name']} @ {best_bet['odds']}\n\n"
                    f"📈 **ВАЛУЙ:** +{best_bet['roi']:.1f}%\n\n"
                    f"💵 **СУММА:** ${best_bet['stake']}"
                )
                
                with st.expander("Показать все валуйные конторы"):
                    df = pd.DataFrame(targets)
                    st.dataframe(df.style.format({"odds": "{:.2f}", "roi": "+{:.1f}%", "stake": "${:.0f}"}))
            else:
                if status == "💎 SMART MONEY":
                    st.warning("Тренд отличный, но Софты уже опустили кэфы. Валуя нет.")
                else:
                    st.write("Рекомендаций нет.")

            st.divider()

            # --- ГРАФИКИ ---
            st.subheader("📊 Графики Синдиката")
            
            chart_data = []
            for row in pin['history']:
                chart_data.append({
                    "Время": row['time_str'],
                    "Цена (Odds)": row['odds'][0],
                    "Риск (R%)": row['r'][0]
                })
            df_chart = pd.DataFrame(chart_data).set_index("Время")
            
            g1, g2 = st.columns(2)
            with g1:
                st.write("**📉 ЦЕНА (Чем ниже, тем лучше)**")
                st.line_chart(df_chart["Цена (Odds)"], color="#FF4B4B")
            with g2:
                st.write("**📈 РИСК R (Чем выше, тем увереннее)**")
                st.line_chart(df_chart["Риск (R%)"], color="#00AA00")
                
        else:
            st.error("❌ Не удалось распознать данные Pinnacle. Проверь, что копируешь.")
    else:
        st.warning("Пожалуйста, заполни оба поля данными.")
