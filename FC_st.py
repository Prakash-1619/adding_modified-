# streamlit_app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

# ------------------------------
# LOAD DATA
# ------------------------------
forecast_df = pd.read_csv("forecast_lowess_all_areas.csv", parse_dates=["month"])
metrics_df = pd.read_csv("metrics_lowess_all_areas.csv")

# ------------------------------
# STREAMLIT APP
# ------------------------------
st.title("Real Estate Forecast Analysis")
st.markdown("Select an area to visualize forecast, metrics, and scatter plots.")

# Area selection
areas = forecast_df['area'].unique()
selected_area = st.selectbox("Select Area", areas)

# Filter data for selected area
area_forecast = forecast_df[forecast_df['area'] == selected_area].copy()
area_metrics = metrics_df[metrics_df['Area'] == selected_area].copy()

# ------------------------------
# FORECAST vs ACTUAL PLOT
# ------------------------------
st.subheader("Forecast vs LOWESS Smoothed Actuals")
plt.figure(figsize=(10,5))
for phase, color, marker in zip(["train","test","forecast"], ["red","orange","green"], ["o","o","o"]):
    df_phase = area_forecast[area_forecast['phase']==phase]
    plt.plot(df_phase['month'], df_phase['predicted'], color=color, linestyle='--', marker=marker, label=f"{phase.capitalize()} Predicted")
plt.plot(area_forecast['month'], area_forecast['actual_smoothed'], color="blue", linestyle=":", label="Actual (LOWESS)")
plt.xlabel("Month")
plt.ylabel("Median Price")
plt.title(f"{selected_area} - Forecast vs Actual (LOWESS)")
plt.legend()
plt.grid(alpha=0.3)
st.pyplot(plt.gcf())
plt.clf()

# ------------------------------
# METRICS BAR PLOT
# ------------------------------
st.subheader("Train/Test Metrics")
metrics_plot = area_metrics[['Train_MAE','Train_RMSE','Train_R2','Test_MAE','Test_RMSE','Test_R2']].T
metrics_plot.columns = ['Value']
metrics_plot.index.name = 'Metric'
metrics_plot.reset_index(inplace=True)

plt.figure(figsize=(8,4))
colors = ['red' if 'Train' in m else 'orange' for m in metrics_plot['Metric']]
plt.bar(metrics_plot['Metric'], metrics_plot['Value'], color=colors)
plt.xticks(rotation=45)
plt.ylabel("Metric Value")
plt.title(f"{selected_area} - Metrics")
plt.grid(axis='y', alpha=0.3)
st.pyplot(plt.gcf())
plt.clf()

# ------------------------------
# SCATTER PLOTS WITH LINEAR FIT AND R2
# ------------------------------
st.subheader("Actual vs Predicted Scatter Plots")

for phase in ["train","test"]:
    df_phase = area_forecast[area_forecast['phase']==phase].dropna()
    X = df_phase['actual_smoothed'].values.reshape(-1,1)
    y = df_phase['predicted'].values
    r2 = r2_score(X, y)
    
    # Linear fit
    lr = LinearRegression()
    lr.fit(X, y)
    y_pred_line = lr.predict(X)
    
    plt.figure(figsize=(6,6))
    plt.scatter(X, y, alpha=0.7, label='Data Points')
    plt.plot(X, y_pred_line, 'r--', label=f'Linear Fit (R²={r2:.3f})')
    plt.xlabel("Actual (LOWESS)")
    plt.ylabel("Predicted")
    plt.title(f"{selected_area} - {phase.capitalize()} Scatter Plot")
    plt.legend()
    plt.grid(alpha=0.3)
    st.pyplot(plt.gcf())
    plt.clf()
