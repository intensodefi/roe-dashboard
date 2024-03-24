import streamlit as st
import pandas as pd
import plotly.express as px


def calculate_tvr(row, is_backfund=False):
    DAU_value = 10  # $10 per DAU
    TVL_value_per_1000 = 1 / 1000  # $1 TVR per $1000 TVL
    volume_value_per_10000 = 1 / 10000  # $1 TVR per $10,000 volume
    days = 7 if is_backfund else 30  # Number of days for DAU calculation
    
    # Calculate TVR components
    tvr_user_metrics = (row['DAU 7D-MA'] if is_backfund else row['DAU 30D-MA']) * days * DAU_value
    tvr_liquidity = row['TVL'] * TVL_value_per_1000 * days
    tvr_volume = (row['Volume 7D-MA'] if is_backfund else row['Volume 30D-MA']) * volume_value_per_10000
    tvr_fees = row['Fee 7D-MA'] if is_backfund else row['Fee 30D-MA']
    
    # Total TVR
    total_tvr = tvr_user_metrics + tvr_liquidity + tvr_volume + tvr_fees
    return total_tvr

def calculate_roe(row):
    tve = row['Grant Amount - ARB']
    tvr = row['TVR']
    if tve > 0 and not pd.isna(tvr):
        roe = ((tve - tvr) / tve) + 1
    else:
        roe = None
    return roe

def load_and_process_data(file_path, is_backfund=False):
    df = pd.read_csv(file_path)
    df['TVR'] = df.apply(lambda row: calculate_tvr(row, is_backfund=is_backfund), axis=1)
    df['ROE'] = df.apply(calculate_roe, axis=1)
    return df[['Protocol','Type', 'Grant Amount - ARB', 'TVR', 'ROE']]

def main():
    st.title("Arbitrum grantees ROE Dashboard")

    # Methodology explanation
    st.write("""
    This dashboard calculates and displays the Total Value Returned (TVR) and Return on Ecosystem (ROE) for each protocol. The methodology for TVR calculation is as follows:
    - **User Metrics (DAU):** \$10 TVR for each Daily Active User over 7 or 30 days.
    - **Liquidity (TVL):** \$1 TVR for each \$10000 of Total Value Locked over 7 or 30 days.
    - **Volume:** \$1 TVR for each \$10000 of volume.
    - **Fees:** Direct inclusion of fees generated as part of TVR.
    - **Formula:** ROE is calculated using the formula: **ROE = [(TVE - TVR)/TVE] + 1**, where TVE is the Total Value of Ecosystem, represented by the grant amount.
    - **Data sources:** https://www.openblocklabs.com/app/arbitrum/grantees
    """)

    backfund_file = 'STIP_Backfund_used.csv'
    round1_file = 'STIP_Round1_used.csv'

    st.subheader("STIP Backfund Data")
    backfund_df = load_and_process_data(backfund_file, is_backfund=True)
    st.write(backfund_df)
    fig1 = px.bar(backfund_df, x='Protocol', y='ROE', color='Protocol',
             color_continuous_scale=px.colors.sequential.Viridis,
             labels={'ROE': 'Return on Equity'}, title="ROE by Protocol - STIP Backfund")
    st.plotly_chart(fig1)

    fig2 = px.bar(backfund_df, x='Type', y='ROE', color='Type',
             color_continuous_scale=px.colors.sequential.Viridis,
             labels={'ROE': 'Return on Equity'}, title="ROE by Type - STIP Backfund")

    st.plotly_chart(fig2)

    st.subheader("STIP Round 1 Data")
    round1_df = load_and_process_data(round1_file, is_backfund=False)
    st.write(round1_df)

    fig3 = px.bar(round1_df, x='Protocol', y='ROE', color='Protocol',
                color_continuous_scale=px.colors.sequential.Viridis,
                labels={'ROE': 'Return on Equity'}, title="ROE by Protocol - STIP Round 1")
    st.plotly_chart(fig3)

    fig4 = px.bar(round1_df, x='Type', y='ROE', color='Type',
             color_continuous_scale=px.colors.sequential.Viridis,
             labels={'ROE': 'Return on Equity'}, title="ROE by Type - STIP Round 1")

    st.plotly_chart(fig4)
    

if __name__ == "__main__":
    main()
