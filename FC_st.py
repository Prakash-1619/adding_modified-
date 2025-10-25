import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

# -----------------------------
# Load precomputed CSVs
# -----------------------------
forecast_df = pd.read_csv("all_areas_forecast.csv", parse_dates=['Date'])
metrics_df = pd.read_csv("all_areas_metrics.csv")
avp_df = pd.read_csv("all_areas_actual_vs_predicted.csv", parse_dates=['Date'])

# -----------------------------
# Streamlit app
# -----------------------------
st.title("Real Estate Forecast Dashboard")

# Area selection
areas = forecast_df['Area'].unique()
selected_area = st.selectbox("Select Area", areas)

# Filter data for selected area
forecast_area = forecast_df[forecast_df['Area'] == selected_area]
metrics_area = metrics_df[metrics_df['Area'] == selected_area]
avp_area = avp_df[avp_df['Area'] == selected_area]

# -----------------------------
# Forecast plot: Actual + Models
# -----------------------------
fig_forecast = go.Figure()

colors = {'ARIMA':'green', 'SARIMA':'orange', 'Prophet':'blue'}

# Plot Actual
fig_forecast.add_trace(go.Scatter(
    x=forecast_area['Date'], y=forecast_area['Actual'],
    mode='lines+markers', name='Actual', line=dict(color='black', width=2)
))

# Plot models fitted + forecast
for model in ['ARIMA', 'SARIMA', 'Prophet']:
    # Fitted (dash)
    fig_forecast.add_trace(go.Scatter(
        x=forecast_area['Date'], y=forecast_area[f'{model}_Fitted'],
        mode='lines', name=f'{model} Fitted', line=dict(color=colors[model], dash='dash')
    ))
    # Forecast (solid)
    fig_forecast.add_trace(go.Scatter(
        x=forecast_area['Date'], y=forecast_area[f'{model}_Forecast'],
        mode='lines', name=f'{model} Forecast', line=dict(color=colors[model])
    ))

fig_forecast.update_layout(title=f"Actual vs Forecast — {selected_area}",
                           xaxis_title="Date", yaxis_title="Median Price",
                           template="plotly_white")
st.plotly_chart(fig_forecast, use_container_width=True)

# -----------------------------
# Metrics bar chart
# -----------------------------
fig_metrics = go.Figure()
metric_names = ['RMSE','MAE','MAPE']

for model in ['ARIMA','SARIMA','Prophet']:
    train_vals = metrics_area[(metrics_area['Model']==model)&(metrics_area['Dataset']=='Train')][metric_names].values.flatten()
    test_vals = metrics_area[(metrics_area['Model']==model)&(metrics_area['Dataset']=='Test')][metric_names].values.flatten()
    fig_metrics.add_trace(go.Bar(x=metric_names, y=train_vals, name=f"{model} Train", marker_color=colors[model]))
    fig_metrics.add_trace(go.Bar(x=metric_names, y=test_vals, name=f"{model} Test", marker_color=colors[model], opacity=0.6))

fig_metrics.update_layout(barmode='group', title=f"Metrics — {selected_area}",
                          xaxis_title="Metric", yaxis_title="Value",
                          template="plotly_white")
st.plotly_chart(fig_metrics, use_container_width=True)

# -----------------------------
# Scatter plots: Actual vs Predicted with linear fit and R²
# -----------------------------
st.subheader("Scatter Plot: Actual vs Predicted")

for dataset in ['Train','Test']:
    st.markdown(f"**{dataset} Dataset**")
    fig_scatter = go.Figure()
    avp_ds = avp_area[avp_area['Dataset']==dataset]
    for model in ['ARIMA','SARIMA','Prophet']:
        avp_model = avp_ds[avp_ds['Model']==model]
        x = avp_model['Actual'].values
        y = avp_model['Predicted'].values
        # Drop NaNs
        mask = ~np.isnan(x) & ~np.isnan(y)
        x, y = x[mask], y[mask]
        if len(x) > 1:
            # Linear fit
            lr = LinearRegression().fit(x.reshape(-1,1), y.reshape(-1,1))
            y_fit = lr.predict(x.reshape(-1,1)).ravel()
            r2 = r2_score(x, y)
            # Scatter points
            fig_scatter.add_trace(go.Scatter(x=x, y=y, mode='markers', name=f"{model} (R²={r2:.3f})",
                                             marker_color=colors[model]))
            # Linear fit line
            fig_scatter.add_trace(go.Scatter(x=x, y=y_fit, mode='lines', showlegend=True,
                                             name=f"{model} Fit", line=dict(color=colors[model], dash='dash')))
    # y=x reference line
    y_min, y_max = avp_ds['Actual'].min(), avp_ds['Actual'].max()
    fig_scatter.add_trace(go.Scatter(x=[y_min, y_max], y=[y_min, y_max], mode='lines', name='y=x',
                                     line=dict(color='black', dash='dot')))
    fig_scatter.update_layout(title=f"{dataset}: Actual vs Predicted",
                              xaxis_title="Actual Median Price", yaxis_title="Predicted Median Price",
                              template="plotly_white")
    st.plotly_chart(fig_scatter, use_container_width=True)

