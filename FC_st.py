import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

# -----------------------------
# Load data
# -----------------------------
forecast_df = pd.read_csv("all_areas_forecast.csv", parse_dates=['Date'])
metrics_df = pd.read_csv("all_areas_metrics.csv")
scatter_df = pd.read_csv("all_areas_actual_vs_predicted.csv", parse_dates=['Date'])

# -----------------------------
# Sidebar selection
# -----------------------------
area_list = forecast_df['Area'].unique()
selected_area = st.sidebar.selectbox("Select Area", area_list)

# Filter for selected area
forecast_area = forecast_df[forecast_df['Area']==selected_area]
metrics_area = metrics_df[metrics_df['Area']==selected_area]
scatter_area = scatter_df[scatter_df['Area']==selected_area]

# -----------------------------
# Line plot: Actual + Fitted + Forecast
# -----------------------------
st.subheader(f"Forecast Line Plot — {selected_area}")

fig_line = px.line()
fig_line.add_scatter(x=forecast_area['Date'], y=forecast_area['Actual'],
                     mode='lines+markers', name='Actual', line=dict(color='black', width=2))

models = forecast_area['Model'].unique()
colors = {'ARIMA':'green','SARIMA':'orange','Prophet':'blue'}

for model in models:
    df_model = forecast_area[forecast_area['Model']==model]
    # Fitted (train)
    df_train = df_model[df_model['Dataset']=='Train']
    fig_line.add_scatter(x=df_train['Date'], y=df_train['Predicted'],
                         mode='lines', name=f'{model} Fitted', line=dict(color=colors[model], dash='dash'))
    # Forecast (test + future)
    df_test = df_model[df_model['Dataset']=='Test']
    fig_line.add_scatter(x=df_test['Date'], y=df_test['Predicted'],
                         mode='lines', name=f'{model} Forecast', line=dict(color=colors[model]))

st.plotly_chart(fig_line, use_container_width=True)

# -----------------------------
# Metrics table
# -----------------------------
st.subheader("Metrics Table (Train/Test)")

st.dataframe(metrics_area)

# -----------------------------
# Scatter plots: Actual vs Predicted
# -----------------------------
st.subheader("Actual vs Predicted — Scatter Plots with Linear Fit")

for dataset in ['Train','Test']:
    st.markdown(f"**{dataset} Dataset**")
    fig_scatter = px.scatter()
    for model in models:
        df_sc = scatter_area[(scatter_area['Model']==model) & (scatter_area['Dataset']==dataset)]
        if len(df_sc)==0:
            continue
        x = df_sc['Actual'].values
        y = df_sc['Predicted'].values
        fig_scatter.add_scatter(x=x, y=y, mode='markers', name=model, marker=dict(color=colors[model]))
        # Linear regression
        lr = LinearRegression()
        lr.fit(x.reshape(-1,1), y.reshape(-1,1))
        y_fit = lr.predict(x.reshape(-1,1)).ravel()
        r2 = r2_score(x, y)
        fig_scatter.add_scatter(x=x, y=y_fit, mode='lines', name=f"{model} Fit (R²={r2:.3f})", line=dict(color=colors[model], dash='dash'))
    # y=x reference
    min_val = min(df_sc['Actual'].min(), df_sc['Predicted'].min())
    max_val = max(df_sc['Actual'].max(), df_sc['Predicted'].max())
    fig_scatter.add_scatter(x=[min_val,max_val], y=[min_val,max_val], mode='lines', name='y=x', line=dict(color='black', dash='dot'))
    
    st.plotly_chart(fig_scatter, use_container_width=True)
