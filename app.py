import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px

st.title("📈 Stock Market Analyzer")

# User inputs
stock_symbol1 = st.text_input("Enter First Stock Symbol (e.g., AAPL):", "AAPL")
stock_symbol2 = st.text_input("Enter Second Stock Symbol (Optional):", "")
start_date = st.date_input("Start Date", pd.to_datetime("2023-01-01"))
end_date = st.date_input("End Date", pd.to_datetime("today"))

if st.button("Analyze Stock(s)"):
    # Determine which stocks to download
    tickers = [stock_symbol1]
    if stock_symbol2.strip() != "":
        tickers.append(stock_symbol2.strip())

    # Download data
    data = yf.download(tickers, start=start_date, end=end_date)

    if data.empty:
        st.warning("No data found. Please check the stock symbols or date range.")
    else:
        # Flatten columns if MultiIndex
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = ['_'.join(col).strip() for col in data.columns.values]

        st.subheader("📄 Stock Data (Last 5 rows)")
        st.write(data.tail())

        # ------------------ SINGLE STOCK ANALYSIS ------------------
        if len(tickers) == 1:
            stock_symbol = tickers[0]
            close_col = f"Close_{stock_symbol}" if f"Close_{stock_symbol}" in data.columns else "Close"
            volume_col = f"Volume_{stock_symbol}" if f"Volume_{stock_symbol}" in data.columns else "Volume"
            open_col = f"Open_{stock_symbol}" if f"Open_{stock_symbol}" in data.columns else "Open"
            high_col = f"High_{stock_symbol}" if f"High_{stock_symbol}" in data.columns else "High"
            low_col = f"Low_{stock_symbol}" if f"Low_{stock_symbol}" in data.columns else "Low"

            # Moving averages
            data["MA20"] = data[close_col].rolling(window=20).mean()
            data["MA50"] = data[close_col].rolling(window=50).mean()

            st.subheader("📊 Closing Price with Moving Averages")
            fig_ma = px.line(data, x=data.index, y=[close_col, "MA20", "MA50"],
                             labels={"value": "Price", "variable": "Legend"},
                             title=f"{stock_symbol} Closing Price with 20 & 50 Day MAs")
            st.plotly_chart(fig_ma)

            # Daily returns
            data["Daily Return %"] = data[close_col].pct_change() * 100
            st.subheader("📉 Daily Return Percentage")
            fig_ret = px.line(data, x=data.index, y="Daily Return %",
                              title=f"{stock_symbol} Daily Return %")
            st.plotly_chart(fig_ret)

            # Volume chart
            st.subheader("📦 Trading Volume")
            fig_vol = px.bar(data, x=data.index, y=volume_col, title=f"{stock_symbol} Trading Volume")
            st.plotly_chart(fig_vol)

            # Candlestick chart
            st.subheader("🕯️ Candlestick Chart")
            fig_candle = go.Figure(data=[go.Candlestick(
                x=data.index,
                open=data[open_col],
                high=data[high_col],
                low=data[low_col],
                close=data[close_col]
            )])
            fig_candle.update_layout(title=f"{stock_symbol} Candlestick Chart", xaxis_rangeslider_visible=False)
            st.plotly_chart(fig_candle)

            # ---------------- KPIs ----------------
            st.subheader("📌 Key Performance Indicators (KPIs)")
            highest_price = data[close_col].max()
            lowest_price = data[close_col].min()
            avg_price = data[close_col].mean()
            max_daily_return = data["Daily Return %"].max()
            volatility = data["Daily Return %"].std()

            st.metric("Highest Close Price", f"${highest_price:.2f}")
            st.metric("Lowest Close Price", f"${lowest_price:.2f}")
            st.metric("Average Close Price", f"${avg_price:.2f}")
            st.metric("Max Daily Return %", f"{max_daily_return:.2f}%")
            st.metric("Volatility (Std Dev %)", f"{volatility:.2f}%")

            # CSV Download Button
            st.subheader("⬇️ Download Processed Data")
            csv_data = data.to_csv().encode('utf-8')
            st.download_button(label="Download CSV", data=csv_data, file_name=f"{stock_symbol}_analysis.csv", mime='text/csv')

        # ------------------ TWO STOCKS COMPARISON ------------------
        else:
            st.subheader("⚔️ Two Stocks Comparison (Closing Prices)")
            close_cols = [f"Close_{tick}" for tick in tickers]
            fig_compare = px.line(data, x=data.index, y=close_cols, 
                                  title=f"Closing Price Comparison: {tickers[0]} vs {tickers[1]}")
            st.plotly_chart(fig_compare)

            # Daily returns comparison
            st.subheader("📉 Daily Returns Comparison")
            daily_returns = data[close_cols].pct_change() * 100
            daily_returns.columns = [f"{tick} Return %" for tick in tickers]
            fig_ret_compare = px.line(daily_returns, x=daily_returns.index, 
                                      y=daily_returns.columns,
                                      title="Daily Returns (%) Comparison")
            st.plotly_chart(fig_ret_compare)

            # CSV Download Button
            st.subheader("⬇️ Download Comparison Data")
            csv_data = data.to_csv().encode('utf-8')
            st.download_button(label="Download CSV", data=csv_data, file_name=f"{tickers[0]}_vs_{tickers[1]}_analysis.csv", mime='text/csv')




 
