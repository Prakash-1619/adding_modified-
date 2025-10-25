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
    import streamlit as st
    import pandas as pd
    import numpy as np
    import plotly.graph_objects as go
    import plotly.express as px
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import r2_score
    
    # -----------------------------
    # Read data from uploaded file
    # -----------------------------
    
    # -----------------------------
    # Load data
    # -----------------------------
    #forecast_df = pd.read_csv("all_areas_forecast.csv", parse_dates=['Date'])
    metrics_df = pd.read_csv("all_areas_metrics.csv")
    scatter_df = pd.read_csv("all_areas_actual_vs_predicted.csv", parse_dates=['Date'])
    
    # Strip column names to remove any extra spaces
    #forecast_df.columns = forecast_df.columns.str.strip()
    metrics_df.columns = metrics_df.columns.str.strip()
    scatter_df.columns = scatter_df.columns.str.strip()

    
    
    # -----------------------------
    # Read data from uploaded file
    # -----------------------------
    @st.cache_data
    def load_data():
        # Read the uploaded CSV file
        df = pd.read_csv("all_areas_actual_vs_predicted.csv", parse_dates=['Date'])
        df.columns = df.columns.str.strip()
        return df
    
    # Load the data
    scatter_df = load_data()
    
    # -----------------------------
    # Create forecast_df and metrics_df from scatter_df
    # -----------------------------
    # forecast_df is essentially the same as scatter_df for our purposes
    forecast_df = scatter_df.copy()
    
    # Create metrics_df by calculating metrics from scatter_df
    def calculate_metrics(df):
        metrics = []
        for area in df['Area'].unique():
            area_data = df[df['Area'] == area]
            for model in area_data['Model'].unique():
                model_data = area_data[area_data['Model'] == model]
                for dataset in ['Train', 'Test']:
                    dataset_data = model_data[model_data['Dataset'] == dataset]
                    if len(dataset_data) > 0:
                        actual = dataset_data['Actual'].values
                        predicted = dataset_data['Predicted'].values
                        
                        # Calculate metrics
                        mae = np.mean(np.abs(actual - predicted))
                        mse = np.mean((actual - predicted) ** 2)
                        rmse = np.sqrt(mse)
                        mape = np.mean(np.abs((actual - predicted) / actual)) * 100
                        r2 = r2_score(actual, predicted)
                        
                        metrics.append({
                            'Area': area,
                            'Model': model,
                            'Dataset': dataset,
                            'MAE': mae,
                            'MSE': mse,
                            'RMSE': rmse,
                            'MAPE': mape,
                            'R2': r2
                        })
        return pd.DataFrame(metrics)
    
    metrics_df = calculate_metrics(scatter_df)
    
    # -----------------------------
    # Sidebar selection
    # -----------------------------
    area_list = forecast_df['Area'].unique()
    selected_area = st.sidebar.selectbox("Select Area", area_list)
    
    # Filter for selected area
    forecast_area = forecast_df[forecast_df['Area'] == selected_area]
    metrics_area = metrics_df[metrics_df['Area'] == selected_area]
    scatter_area = scatter_df[scatter_df['Area'] == selected_area]
    
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
        colors = {'ARIMA': 'green', 'SARIMA': 'orange', 'Prophet': 'blue'}
    
        for model in models:
            df_model = forecast_area[forecast_area['Model'] == model]
            
            # Fitted (Train)
            df_train = df_model[df_model['Dataset'] == 'Train']
            if not df_train.empty:
                fig_line.add_trace(go.Scatter(
                    x=df_train['Date'],
                    y=df_train['Predicted'],
                    mode='lines',
                    name=f'{model} Fitted',
                    line=dict(color=colors.get(model, 'gray'), dash='dash')
                ))
            
            # Forecast (Test)
            df_test = df_model[df_model['Dataset'] == 'Test']
            if not df_test.empty:
                fig_line.add_trace(go.Scatter(
                    x=df_test['Date'],
                    y=df_test['Predicted'],
                    mode='lines',
                    name=f'{model} Forecast',
                    line=dict(color=colors.get(model, 'gray'))
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
            # Format metrics for better display
            display_metrics = metrics_area.copy()
            numeric_cols = ['MAE', 'MSE', 'RMSE', 'MAPE', 'R2']
            for col in numeric_cols:
                if col in display_metrics.columns:
                    display_metrics[col] = display_metrics[col].round(4)
            st.dataframe(display_metrics)
    
        # -----------------------------
        # Metrics Comparison Plots
        # -----------------------------
        st.subheader("Model Performance Metrics Comparison")
        
        if metrics_area.empty:
            st.info("No metrics data available for visualization.")
        else:
            # Select which metrics to display
            metric_options = ['MAE', 'RMSE', 'MAPE', 'R2']
            selected_metrics = st.multiselect(
                "Select metrics to display:",
                metric_options,
                default=metric_options
            )
            
            if selected_metrics:
                # Create separate plots for Train and Test datasets
                for dataset in ['Train', 'Test']:
                    st.markdown(f"**{dataset} Dataset**")
                    
                    dataset_metrics = metrics_area[metrics_area['Dataset'] == dataset]
                    
                    if dataset_metrics.empty:
                        st.info(f"No {dataset} metrics available.")
                        continue
                    
                    # Create subplots for selected metrics
                    fig_metrics = go.Figure()
                    
                    for metric in selected_metrics:
                        if metric in dataset_metrics.columns:
                            for model in dataset_metrics['Model'].unique():
                                model_data = dataset_metrics[dataset_metrics['Model'] == model]
                                if not model_data.empty:
                                    fig_metrics.add_trace(go.Bar(
                                        name=f"{model} - {metric}",
                                        x=[f"{model}"],
                                        y=[model_data[metric].values[0]],
                                        legendgroup=model,
                                        marker_color=colors.get(model, 'gray'),
                                        text=[f"{model_data[metric].values[0]:.4f}"],
                                        textposition='auto',
                                    ))
                    
                    # Update layout for better visualization
                    fig_metrics.update_layout(
                        title=f"{dataset} Dataset - Model Comparison",
                        xaxis_title="Models",
                        yaxis_title="Metric Values",
                        barmode='group',
                        template='plotly_white',
                        showlegend=True
                    )
                    
                    st.plotly_chart(fig_metrics, use_container_width=True)
                    
                    # Also create a radar chart for comprehensive model comparison
                    if len(selected_metrics) >= 3:  # Radar chart needs at least 3 metrics
                        st.markdown(f"**{dataset} Dataset - Radar Chart Comparison**")
                        
                        fig_radar = go.Figure()
                        
                        for model in dataset_metrics['Model'].unique():
                            model_data = dataset_metrics[dataset_metrics['Model'] == model]
                            if not model_data.empty:
                                # Normalize metrics for radar chart (except R2 which is already normalized)
                                values = []
                                for metric in selected_metrics:
                                    val = model_data[metric].values[0]
                                    if metric == 'R2':
                                        # R2 is already between 0-1 (or negative)
                                        values.append(max(0, val))  # Ensure non-negative for radar
                                    else:
                                        # For error metrics, lower is better - invert for visualization
                                        max_val = dataset_metrics[metric].max()
                                        if max_val > 0:
                                            # Normalize and invert so better performance = larger area
                                            values.append(1 - (val / max_val))
                                        else:
                                            values.append(1)
                                
                                fig_radar.add_trace(go.Scatterpolar(
                                    r=values,
                                    theta=selected_metrics,
                                    fill='toself',
                                    name=model,
                                    line=dict(color=colors.get(model, 'gray'))
                                ))
                        
                        fig_radar.update_layout(
                            polar=dict(
                                radialaxis=dict(
                                    visible=True,
                                    range=[0, 1]
                                )),
                            showlegend=True,
                            title=f"{dataset} Dataset - Radar Chart (Normalized, Higher = Better)"
                        )
                        
                        st.plotly_chart(fig_radar, use_container_width=True)
            
            # -----------------------------
            # Performance Summary
            # -----------------------------
            st.subheader("Performance Summary")
            
            # Create a summary table highlighting best performing model for each metric
            summary_data = []
            for dataset in ['Train', 'Test']:
                dataset_metrics = metrics_area[metrics_area['Dataset'] == dataset]
                if not dataset_metrics.empty:
                    for metric in ['MAE', 'RMSE', 'MAPE', 'R2']:
                        if metric in dataset_metrics.columns:
                            if metric == 'R2':
                                # For R2, higher is better
                                best_idx = dataset_metrics[metric].idxmax()
                                best_value = dataset_metrics.loc[best_idx, metric]
                                best_model = dataset_metrics.loc[best_idx, 'Model']
                            else:
                                # For error metrics, lower is better
                                best_idx = dataset_metrics[metric].idxmin()
                                best_value = dataset_metrics.loc[best_idx, metric]
                                best_model = dataset_metrics.loc[best_idx, 'Model']
                            
                            summary_data.append({
                                'Dataset': dataset,
                                'Metric': metric,
                                'Best Model': best_model,
                                'Value': f"{best_value:.4f}"
                            })
            
            if summary_data:
                summary_df = pd.DataFrame(summary_data)
                st.dataframe(summary_df)
                
                # Add some insights
                st.markdown("**Key Insights:**")
                train_metrics = metrics_area[metrics_area['Dataset'] == 'Train']
                test_metrics = metrics_area[metrics_area['Dataset'] == 'Test']
                
                if not train_metrics.empty and not test_metrics.empty:
                    # Check for overfitting
                    for model in models:
                        train_r2 = train_metrics[train_metrics['Model'] == model]['R2']
                        test_r2 = test_metrics[test_metrics['Model'] == model]['R2']
                        if not train_r2.empty and not test_r2.empty:
                            train_r2_val = train_r2.values[0]
                            test_r2_val = test_r2.values[0]
                            if train_r2_val > 0.8 and test_r2_val < 0.5:
                                st.warning(f"⚠️ {model} shows potential overfitting (high train R²={train_r2_val:.3f}, low test R²={test_r2_val:.3f})")
                            elif test_r2_val > 0.7:
                                st.success(f"✅ {model} shows good generalization (test R²={test_r2_val:.3f})")
