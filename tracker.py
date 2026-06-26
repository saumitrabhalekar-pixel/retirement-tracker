import streamlit as st
import yfinance as yf
import pandas as pd
import time
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title='Wealth Builder Pro', page_icon='Money', layout='wide')
st.markdown('<h1 style="text-align: center; color: #1a5f2a;">Retirement Wealth Builder Pro</h1>', unsafe_allow_html=True)

SCAN_FILE = 'latest_scan.csv'
PORTFOLIO_FILE = 'my_portfolio.csv'

# UPGRADED LIST: LARGE, MID, AND SMALL CAPS WITH HIGH POTENTIAL
NSE_STOCKS = [
    # LARGE CAPS
    'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS', 'HINDUNILVR.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'ITC.NS', 'KOTAKBANK.NS',
    'LT.NS', 'AXISBANK.NS', 'BAJFINANCE.NS', 'MARUTI.NS', 'ASIANPAINT.NS', 'HCLTECH.NS', 'TITAN.NS', 'SUNPHARMA.NS', 'TATAMOTORS.NS', 'WIPRO.NS',
    'ULTRACEMCO.NS', 'NESTLEIND.NS', 'NTPC.NS', 'POWERGRID.NS', 'TATASTEEL.NS', 'ONGC.NS', 'HINDALCO.NS', 'COALINDIA.NS', 'BAJAJFINSV.NS', 'ADANIENT.NS',
    'TECHM.NS', 'GRASIM.NS', 'APOLLOHOSP.NS', 'BRITANNIA.NS', 'DMART.NS', 'SHRIRAMFIN.NS', 'LTIM.NS', 'TATACONSUM.NS', 'M_M.NS', 'ADANIPORTS.NS',
    'DRREDDY.NS', 'CIPLA.NS', 'EICHERMOT.NS', 'HEROMOTOCO.NS', 'DIVISLAB.NS', 'BAJAJAUTO.NS', 'INDUSINDBK.NS', 'HDFCLIFE.NS', 'SBILIFE.NS', 'BPCL.NS',
    # MID CAPS (High Growth Potential)
    'TRENT.NS', 'PIDILITIND.NS', 'INDIANHOTEL.NS', 'TATAPOWER.NS', 'DABUR.NS', 'HAL.NS', 'TVSMOTOR.NS', 'ZOMATO.NS', 'BERGEPAINT.NS', 'DALBHARAT.NS',
    'VOLTAS.NS', 'AUBANK.NS', 'RBLBANK.NS', 'FEDERALBNK.NS', 'IDFCFIRSTB.NS', 'POLYCAB.NS', 'HAVELLS.NS', 'CROMPTON.NS', 'LAURUSLABS.NS', 'ALKEM.NS',
    'TATAELXSI.NS', 'COFORGE.NS', 'PERSISTENT.NS', 'MPHASIS.NS', 'LTIEMINDTREE.NS', 'ZEEL.NS', 'SBICARD.NS', 'CHOLAFIN.NS', 'MOTHERSON.NS', 'BHARATFORG.NS',
    # SMALL CAPS (The Future Bluechips)
    'ASTRAL.NS', 'KEIIND.NS', 'AARTIDRUGS.NS', 'IRFC.NS', 'RVNL.NS', 'WELSPUNLIV.NS', 'KPITTECH.NS', 'DIXON.NS', 'DEEPAKNTR.NS', 'TATAINVEST.NS',
    'HAPPSTMNDS.NS', 'JBMCOOL.NS', 'MICROFIN.NS', 'CAPLIPOINT.NS', 'ZAGGLE.NS', 'SOLARINDS.NS', 'TORNTPOWER.NS', 'ADANIGREEN.NS', 'NHPC.NS', 'SJVN.NS'
]

def analyze_stock(symbol):
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        hist = stock.history(period='1y')
        if hist.empty or len(hist) < 200: return None
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
            
        return {'Symbol': symbol.replace('.NS', ''), 'Price': float(current_price), 'P/E': float(pe_ratio) if pe_ratio else 0, 'ROE (%)': float(roe), 'Growth (%)': float(revenue_growth), 'Score': int(score), 'Signal': signal}
    except: return None

def get_advanced_chart(symbol):
    sym = symbol.upper() + '.NS'
    hist = yf.Ticker(sym).history(period='6mo')
    if hist.empty:
        st.error('Could not find data. Make sure you typed the correct NSE symbol (e.g., RELIANCE).')
        return
    delta = hist['Close'].diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    hist['RSI'] = 100 - (100 / (1 + rs))

    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.6, 0.2, 0.2])
    fig.add_trace(go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'], name='Price'), row=1, col=1)
    colors = ['green' if c >= o else 'red' for c, o in zip(hist['Close'], hist['Open'])]
    fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], marker_color=colors, name='Volume'), row=2, col=1)
    fig.add_trace(go.Scatter(x=hist.index, y=hist['RSI'], name='RSI', line=dict(color='purple', width=2)), row=3, col=1)
    fig.add_hline(y=70, line_dash='dash', line_color='red', row=3, col=1)
    fig.add_hline(y=30, line_dash='dash', line_color='green', row=3, col=1)
    fig.update_layout(height=700, xaxis_rangeslider_visible=False, template='plotly_dark')
    st.plotly_chart(fig, use_container_width=True)

tab1, tab2, tab3, tab4 = st.tabs(['Market Scanner', 'Strong Buys Only', 'My Portfolio', 'Advanced Charts'])

with tab1:
    if st.button('Run Deep Scanner (Takes ~45 secs)', type='primary', use_container_width=True):
        my_bar = st.progress(0, text='Starting scan...')
        results = []
        for i, symbol in enumerate(NSE_STOCKS):
            data = analyze_stock(symbol)
            if data: results.append(data)
            # Removed time.sleep to prevent Streamlit Cloud from timing out!
            my_bar.progress((i + 1) / len(NSE_STOCKS), text='Scanning ' + symbol.replace('.NS', '') + '...')
        if results:
            df = pd.DataFrame(results).sort_values(by='Score', ascending=False)
            df.to_csv(SCAN_FILE, index=False)
            st.success('Scan Complete!')
            col1, col2, col3 = st.columns(3)
            col1.metric('Total Scanned', len(df))
            col2.metric('Strong Buys', len(df[df['Signal']=='STRONG BUY']))
            col3.metric('Buys', len(df[df['Signal']=='BUY']))
            st.dataframe(df, use_container_width=True, hide_index=True)

with tab2:
    st.subheader('Laser Focus: Only The Best Stocks')
    if os.path.exists(SCAN_FILE):
        df = pd.read_csv(SCAN_FILE)
        strong_buys = df[df['Signal'] == 'STRONG BUY']
        if len(strong_buys) > 0:
            st.success('Found ' + str(len(strong_buys)) + ' high-potential candidates.')
            for index, row in strong_buys.iterrows():
                col1, col2, col3, col4 = st.columns(4)
                col1.metric(row['Symbol'], 'Rs ' + str(row['Price']))
                col2.metric('Score', str(row['Score']) + '/100')
                col3.metric('Fundamentals', 'ROE: ' + str(round(row['ROE (%)'], 1)) + '%')
                col4.metric('Valuation', 'P/E: ' + str(round(row['P/E'], 1)))
                st.markdown('---')
        else:
            st.warning('No stocks hit 80+ today. Check the Scanner tab to see what scored 60-79!')
    else:
        st.info('Run Scanner in Tab 1 first!')

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
            st.success('Added ' + new_sym + '!')
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
                    live_data.append({'Symbol': row['Symbol'], 'Qty': row['Qty'], 'Buy Price': 'Rs ' + str(round(row['Buy_Price'], 2)), 'Live Price': 'Rs ' + str(round(live_price, 2)), 'Invested': 'Rs ' + str(round(buy_val, 2)), 'Current Value': 'Rs ' + str(round(current_val, 2)), 'P&L': 'Rs ' + str(round(pnl, 2)), 'P&L %': str(round(pnl_pct, 2)) + '%'})
                except: pass
            if live_data:
                st.dataframe(pd.DataFrame(live_data), use_container_width=True, hide_index=True)
        else: st.info('Portfolio is empty.')
    else: st.info('Portfolio is empty.')

with tab4:
    st.subheader('Stock Technical Charts (Candlesticks, Volume, RSI)')
    chart_sym = st.text_input('Enter Stock Symbol to see chart (e.g., TRENT, KPITTECH, IRFC)')
    if st.button('Show Chart'):
        if chart_sym:
            get_advanced_chart(chart_sym)
        else:
            st.warning('Please type a stock name first.')