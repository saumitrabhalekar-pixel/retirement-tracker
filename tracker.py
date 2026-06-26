import streamlit as st
import yfinance as yf
import pandas as pd
import time
import os
import plotly.express as px
from plyer import notification

st.set_page_config(page_title='Wealth Builder Pro', page_icon='Money', layout='wide')
st.markdown('<h1 style="text-align: center; color: #1a5f2a;">Retirement Wealth Builder Pro</h1>', unsafe_allow_html=True)

SCAN_FILE = 'latest_scan.csv'
PORTFOLIO_FILE = 'my_portfolio.csv'

NSE_STOCKS = [
    'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS', 'HINDUNILVR.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'ITC.NS', 'KOTAKBANK.NS',
    'LT.NS', 'AXISBANK.NS', 'BAJFINANCE.NS', 'MARUTI.NS', 'ASIANPAINT.NS', 'HCLTECH.NS', 'TITAN.NS', 'SUNPHARMA.NS', 'TATAMOTORS.NS', 'WIPRO.NS',
    'ULTRACEMCO.NS', 'NESTLEIND.NS', 'NTPC.NS', 'POWERGRID.NS', 'TATASTEEL.NS', 'ONGC.NS', 'HINDALCO.NS', 'COALINDIA.NS', 'BAJAJFINSV.NS', 'ADANIENT.NS',
    'TECHM.NS', 'GRASIM.NS', 'APOLLOHOSP.NS', 'BRITANNIA.NS', 'DMART.NS', 'SHRIRAMFIN.NS', 'LTIM.NS', 'TATACONSUM.NS', 'M_M.NS', 'ADANIPORTS.NS',
    'DRREDDY.NS', 'CIPLA.NS', 'EICHERMOT.NS', 'HEROMOTOCO.NS', 'DIVISLAB.NS', 'BAJAJAUTO.NS', 'INDUSINDBK.NS', 'HDFCLIFE.NS', 'SBILIFE.NS', 'BPCL.NS',
    'IOC.NS', 'JSWSTEEL.NS', 'TATACOMM.NS', 'DABUR.NS', 'PIDILITIND.NS', 'VEDL.NS', 'HAL.NS', 'BAJAJHLDNG.NS', 'AMBUJACEM.NS', 'ACC.NS',
    'TRENT.NS', 'IDFCFIRSTB.NS', 'FEDERALBNK.NS', 'BANDHANBNK.NS', 'ICICIPRULI.NS', 'YESBANK.NS', 'PNB.NS', 'BANKBARODA.NS', 'CANBK.NS', 'UNIONBANK.NS',
    'TVSMOTOR.NS', 'MRF.NS', 'BERGEPAINT.NS', 'SIEMENS.NS', 'HAVELLS.NS', 'LTTS.NS', 'PERSISTENT.NS', 'COFORGE.NS', 'MPHASIS.NS',
    'ZYDUSLIFE.NS', 'ALKEM.NS', 'LUPIN.NS', 'AUROPHARMA.NS', 'BIOCON.NS', 'PEL.NS', 'CROMPTON.NS', 'VOLTAS.NS', 'BLUESTARCO.NS', 'POLYCAB.NS',
    'SOLARINDS.NS', 'TATAPOWER.NS', 'ADANIGREEN.NS', 'TORNTPOWER.NS', 'JSWENERGY.NS', 'NHPC.NS', 'SJVN.NS',
    'DLF.NS', 'OBEROIRLTY.NS', 'MACROTECH.NS', 'PRESTIGE.NS', 'GODREJCP.NS', 'GODREJPROP.NS', 'EXIDEIND.NS', 'AMARAJABAT.NS'
]

def analyze_stock(symbol):
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        hist = stock.history(period='1y')
        if hist.empty or len(hist) < 200: 
            return None
            
        current_price = hist['Close'].iloc[-1]
        dma_50 = hist['Close'].rolling(50).mean().iloc[-1]
        dma_200 = hist['Close'].rolling(200).mean().iloc[-1]
        
        pe_ratio = info.get('trailingPE', 0)
        roe = info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else 0
        debt_to_equity = info.get('debtToEquity', 0)
        revenue_growth = info.get('revenueGrowth', 0) * 100 if info.get('revenueGrowth') else 0
        
        score = 0
        if roe > 15: score += 25
        elif roe > 10: score += 10
        if revenue_growth > 10: score += 25
        elif revenue_growth > 5: score += 10
        if 0 < pe_ratio < 25: score += 25
        elif 25 <= pe_ratio < 35: score += 10
        if debt_to_equity < 50: score += 15
        elif debt_to_equity < 100: score += 5
        
        if current_price > dma_200: score += 5
        if current_price > dma_50: score += 5
            
        if score >= 80: signal = 'STRONG BUY'
        elif score >= 65: signal = 'BUY'
        elif score >= 45: signal = 'HOLD'
        else: signal = 'AVOID'
            
        return {
            'Symbol': symbol.replace('.NS', ''), 
            'Price': float(current_price),
            'P/E': float(pe_ratio) if pe_ratio else 0, 
            'ROE (%)': float(roe),
            'Growth (%)': float(revenue_growth), 
            'Score': int(score), 
            'Signal': signal
        }
    except: 
        return None

tab1, tab2, tab3 = st.tabs(['Market Scanner', 'Strong Buys Only', 'My Portfolio'])

with tab1:
    if st.button('Run Deep Scanner (Takes 2 mins)', type='primary', use_container_width=True):
        my_bar = st.progress(0, text='Starting scan...')
        results = []
        alerts = 0
        
        for i, symbol in enumerate(NSE_STOCKS):
            data = analyze_stock(symbol)
            if data:
                results.append(data)
                if data['Score'] >= 80:
                    notification.notify(title='Stock Alert: ' + data['Symbol'], message='Score: ' + str(data['Score']) + ' | Price: Rs ' + str(data['Price']), timeout=10)
                    alerts += 1
                    time.sleep(2)
            my_bar.progress((i + 1) / len(NSE_STOCKS), text='Scanning ' + symbol.replace('.NS', '') + '...')
            time.sleep(0.3)
            
        if results:
            df = pd.DataFrame(results).sort_values(by='Score', ascending=False)
            df.to_csv(SCAN_FILE, index=False)
            st.success('Done! ' + str(alerts) + ' Strong Buys found and saved.')
            
            col1, col2, col3 = st.columns(3)
            col1.metric('Scanned', len(df))
            col2.metric('Strong Buys', len(df[df['Signal']=='STRONG BUY']))
            col3.metric('Desktop Alerts', alerts)
            
            st.dataframe(df.head(30), use_container_width=True, hide_index=True)

with tab2:
    st.subheader('Laser Focus: Only The Best Stocks')
    if os.path.exists(SCAN_FILE):
        df = pd.read_csv(SCAN_FILE)
        strong_buys = df[df['Signal'] == 'STRONG BUY']
        
        if len(strong_buys) > 0:
            st.success('Found ' + str(len(strong_buys)) + ' perfect candidates for your retirement portfolio.')
            
            for index, row in strong_buys.iterrows():
                col1, col2, col3, col4 = st.columns(4)
                col1.metric(row['Symbol'], 'Rs ' + str(row['Price']))
                col2.metric('Score', str(row['Score']) + '/100')
                col3.metric('Fundamentals', 'ROE: ' + str(round(row['ROE (%)'], 1)) + '%')
                col4.metric('Valuation', 'P/E: ' + str(round(row['P/E'], 1)))
                st.markdown('---')
        else:
            st.warning('No stocks hit the 80+ score threshold today. Patience is key!')
    else:
        st.info('Please run the Scanner in Tab 1 first!')

with tab3:
    st.subheader('Track Your Live Investments')
    
    with st.form('add_stock_form'):
        c1, c2, c3 = st.columns(3)
        new_sym = c1.text_input('Stock Symbol (e.g., RELIANCE)').upper()
        new_qty = c2.number_input('Quantity', min_value=1)
        new_price = c3.number_input('Buy Price (Rs)', min_value=0.01)
        
        submitted = st.form_submit_button('Add to My Portfolio')
        if submitted and new_sym:
            new_data = pd.DataFrame([[new_sym, new_qty, new_price]])
            if os.path.exists(PORTFOLIO_FILE):
                new_data.to_csv(PORTFOLIO_FILE, mode='a', header=False, index=False)
            else:
                new_data.to_csv(PORTFOLIO_FILE, header=['Symbol', 'Qty', 'Buy_Price'], index=False)
            st.success('Added ' + new_sym + ' to portfolio!')
            time.sleep(1)
            st.rerun()
            
    st.markdown('---')
    
    if os.path.exists(PORTFOLIO_FILE):
        port_df = pd.read_csv(PORTFOLIO_FILE)
        if len(port_df) > 0:
            st.write('Live Profit & Loss')
            live_data = []
            
            for index, row in port_df.iterrows():
                sym = row['Symbol'] + '.NS'
                try:
                    live_price = yf.Ticker(sym).history(period='1d')['Close'].iloc[-1]
                    buy_val = row['Qty'] * row['Buy_Price']
                    current_val = row['Qty'] * live_price
                    pnl = current_val - buy_val
                    pnl_pct = (pnl / buy_val) * 100
                    
                    live_data.append({
                        'Symbol': row['Symbol'],
                        'Qty': row['Qty'],
                        'Buy Price': 'Rs ' + str(round(row['Buy_Price'], 2)),
                        'Live Price': 'Rs ' + str(round(live_price, 2)),
                        'Invested': 'Rs ' + str(round(buy_val, 2)),
                        'Current Value': 'Rs ' + str(round(current_val, 2)),
                        'P&L': 'Rs ' + str(round(pnl, 2)),
                        'P&L %': str(round(pnl_pct, 2)) + '%'
                    })
                    time.sleep(0.5)
                except:
                    pass
                    
            if live_data:
                live_df = pd.DataFrame(live_data)
                st.dataframe(live_df, use_container_width=True, hide_index=True)
        else:
            st.info('Your portfolio is empty. Add stocks above!')
    else:
        st.info('Your portfolio is empty. Add stocks above!')
