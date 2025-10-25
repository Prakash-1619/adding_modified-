import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

app_choice = st.sidebar.selectbox("tab", ["Auto Arima with Lowess", "Previous models"])

if app_choice = "Auto Arima with Lowess":
    # ------------------------------
    # LOAD DATA
    # ------------------------------
    forecast_df = pd.read_csv("forecast_lowess_all_areas.csv", parse_dates=["month"])
    metrics_df = pd.read_csv("metrics_lowess_all_areas.csv")
    summary_df = pd.read_csv("sarima_model_summary_all_areas.csv")  # contains 'Area' and 'SARIMA_Summary'
    
    # ------------------------------
    # STREAMLIT APP
    # ------------------------------
    st.title("Real Estate Forecast Analysis with Model Summary")
    
    # Area selection
    areas = forecast_df['area'].unique()
    selected_area = st.selectbox("Select Area", areas)
    
    # Filter data
    area_forecast = forecast_df[forecast_df['area'] == selected_area].copy()
    area_metrics = metrics_df[metrics_df['Area'] == selected_area].copy()
    area_summary = summary_df[summary_df['Area'] == selected_area]["SARIMA_Summary"].values
    summary_text = area_summary[0] if len(area_summary) > 0 else "Model summary not available"
    
    # ------------------------------
    # TABS
    # ------------------------------
    tab1, tab2 = st.tabs(["Forecast & Metrics", "Model Summary"])
    
    # ------------------------------
    # TAB 1: Forecast & Metrics
    # ------------------------------
    with tab1:
        st.subheader("Forecast vs Actual (LOWESS)")
        fig_fc = go.Figure()
        fig_fc.add_trace(go.Scatter(
            x=area_forecast['month'], y=area_forecast['actual_smoothed'],
            mode='lines', name='Actual (LOWESS)', line=dict(color='blue', dash='dot')
        ))
        for phase, color in zip(['train','test','forecast'], ['red','orange','green']):
            df_phase = area_forecast[area_forecast['phase']==phase]
            fig_fc.add_trace(go.Scatter(
                x=df_phase['month'], y=df_phase['predicted'],
                mode='lines+markers', name=f'{phase.capitalize()} Predicted',
                line=dict(color=color, dash='dash')
            ))
        fig_fc.update_layout(
            xaxis_title='Month',
            yaxis_title='Median Price',
            title=f'{selected_area} - Forecast vs Actual (LOWESS)',
            template='plotly_white'
        )
        st.plotly_chart(fig_fc, use_container_width=True)
    
        st.subheader("Train/Test Metrics")
        metrics_plot = area_metrics[['Train_MAE','Train_RMSE','Train_R2','Test_MAE','Test_RMSE','Test_R2']].T
        metrics_plot.columns = ['Value']
        metrics_plot.index.name = 'Metric'
        metrics_plot.reset_index(inplace=True)
        colors = ['red' if 'Train' in m else 'orange' for m in metrics_plot['Metric']]
        fig_metrics = go.Figure(go.Bar(
            x=metrics_plot['Metric'],
            y=metrics_plot['Value'],
            marker_color=colors,
            text=metrics_plot['Value'].round(3),
            textposition='auto'
        ))
        fig_metrics.update_layout(
            title=f'{selected_area} - Train/Test Metrics',
            yaxis_title='Metric Value',
            template='plotly_white'
        )
        st.plotly_chart(fig_metrics, use_container_width=True)
    
        st.subheader("Actual vs Predicted Scatter Plots")
        for phase in ['train','test']:
            df_phase = area_forecast[area_forecast['phase']==phase].dropna()
            X = df_phase['actual_smoothed'].values.reshape(-1,1)
            y = df_phase['predicted'].values
            r2 = r2_score(X, y)
            lr = LinearRegression()
            lr.fit(X, y)
            y_line = lr.predict(X)
            fig_scatter = go.Figure()
            fig_scatter.add_trace(go.Scatter(x=X.flatten(), y=y, mode='markers', name='Data Points'))
            fig_scatter.add_trace(go.Scatter(x=X.flatten(), y=y_line, mode='lines', 
                                             name=f'Linear Fit (R²={r2:.3f})', line=dict(color='red', dash='dash')))
            fig_scatter.update_layout(
                title=f'{selected_area} - {phase.capitalize()} Scatter Plot',
                xaxis_title='Actual (LOWESS)',
                yaxis_title='Predicted',
                template='plotly_white'
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
    
    # ------------------------------
    # TAB 2: Model Summary
    # ------------------------------
    with tab2:
        st.subheader(f"SARIMA Model Summary for {selected_area}")
        st.code(summary_text, language='text')  # keeps formatting and scrollable
