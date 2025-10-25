import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

app_choice = st.sidebar.selectbox("tab", ["Auto Arima with Lowess", "Previous models"])

if app_choice ==  "Auto Arima with Lowess":
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

if app_choice ==  "Previous models":
    import streamlit as st
    import pandas as pd
    import numpy as np
    import plotly.graph_objects as go
    import plotly.express as px
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import r2_score
    
    # -----------------------------
    # Load data
    # -----------------------------
    forecast_df = pd.read_csv("all_areas_forecast.csv", parse_dates=['Date'])
    metrics_df = pd.read_csv("all_areas_metrics.csv")
    scatter_df = pd.read_csv("all_areas_actual_vs_predicted.csv", parse_dates=['Date'])
    
    # Strip column names to remove any extra spaces
    forecast_df.columns = forecast_df.columns.str.strip()
    metrics_df.columns = metrics_df.columns.str.strip()
    scatter_df.columns = scatter_df.columns.str.strip()
    
    # -----------------------------
    # Sidebar selection
    # -----------------------------
    area_list = forecast_df['Area'].unique()
    selected_area = st.sidebar.selectbox("Select Area", area_list)
    
    # Filter for selected area
    forecast_area = forecast_df[forecast_df['Area']==selected_area]
    metrics_area = metrics_df[metrics_df['Area']==selected_area]
    scatter_area = scatter_df[scatter_df['Area']==selected_area]
    
    # Check if area data exists
    if forecast_area.empty:
        st.warning(f"No forecast data found for area: {selected_area}")
    else:
        # -----------------------------
        # Line plot: Actual + Fitted + Forecast
        # -----------------------------
        st.subheader(f"Forecast Line Plot — {selected_area}")
    
        fig_line = go.Figure()
    
        # Actual values
        fig_line.add_trace(go.Scatter(
            x=forecast_area['Date'],
            y=forecast_area['Actual'],
            mode='lines+markers',
            name='Actual',
            line=dict(color='black', width=2)
        ))
    
        models = forecast_area['Model'].unique()
        colors = {'ARIMA':'green','SARIMA':'orange','Prophet':'blue'}
    
        for model in models:
            df_model = forecast_area[forecast_area['Model']==model]
            
            # Fitted (Train)
            df_train = df_model[df_model['Dataset']=='Train']
            fig_line.add_trace(go.Scatter(
                x=df_train['Date'],
                y=df_train['Predicted'],
                mode='lines',
                name=f'{model} Fitted',
                line=dict(color=colors.get(model,'gray'), dash='dash')
            ))
            
            # Forecast (Test)
            df_test = df_model[df_model['Dataset']=='Test']
            fig_line.add_trace(go.Scatter(
                x=df_test['Date'],
                y=df_test['Predicted'],
                mode='lines',
                name=f'{model} Forecast',
                line=dict(color=colors.get(model,'gray'))
            ))
    
        fig_line.update_layout(
            xaxis_title='Date',
            yaxis_title='Price',
            legend_title='Legend',
            template='plotly_white'
        )
    
        st.plotly_chart(fig_line, use_container_width=True)
    
        # -----------------------------
        # Metrics table
        # -----------------------------
        st.subheader("Metrics Table (Train/Test)")
        if metrics_area.empty:
            st.info("No metrics data available for this area.")
        else:
            st.dataframe(metrics_area)
    
        # -----------------------------
        # Scatter plots: Actual vs Predicted
        # -----------------------------
        st.subheader("Actual vs Predicted — Scatter Plots with Linear Fit")
    
        for dataset in ['Train','Test']:
            st.markdown(f"**{dataset} Dataset**")
            fig_scatter = go.Figure()
            for model in models:
                df_sc = scatter_area[(scatter_area['Model']==model) & (scatter_area['Dataset']==dataset)]
                if len(df_sc)==0:
                    continue
                x = df_sc['Actual'].values
                y = df_sc['Predicted'].values
                
                # Scatter points
                fig_scatter.add_trace(go.Scatter(
                    x=x, y=y, mode='markers', name=model, marker=dict(color=colors.get(model,'gray'))
                ))
                
                # Linear regression line
                lr = LinearRegression()
                lr.fit(x.reshape(-1,1), y.reshape(-1,1))
                y_fit = lr.predict(x.reshape(-1,1)).ravel()
                r2 = r2_score(y, y_fit)
                fig_scatter.add_trace(go.Scatter(
                    x=x, y=y_fit, mode='lines', name=f"{model} Fit (R²={r2:.3f})",
                    line=dict(color=colors.get(model,'gray'), dash='dash')
                ))
            
            # y=x reference line
            if not scatter_area.empty:
                min_val = min(df_sc['Actual'].min(), df_sc['Predicted'].min())
                max_val = max(df_sc['Actual'].max(), df_sc['Predicted'].max())
                fig_scatter.add_trace(go.Scatter(
                    x=[min_val,max_val], y=[min_val,max_val], mode='lines',
                    name='y=x', line=dict(color='black', dash='dot')
                ))
            
            fig_scatter.update_layout(
                xaxis_title='Actual',
                yaxis_title='Predicted',
                legend_title='Legend',
                template='plotly_white'
            )
            
            st.plotly_chart(fig_scatter, use_container_width=True)
