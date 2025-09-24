import streamlit as st
import streamlit.components.v1 as components
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np


import streamlit as st

# Page config
st.set_page_config(initial_sidebar_state="expanded", layout="wide", page_title="FlipOse-RE-Analytics")

# Custom CSS
st.markdown("""
    <style>
        [data-testid="collapsedControl"] {
            position: fixed;
            top: 500px;
            left: 50px;
            z-index: 100;
        }
        .block-container {
            padding-top: 2.5rem;
        }
    </style>
""", unsafe_allow_html=True)
###

# Sidebar navigation
page = st.sidebar.radio("Versions", ["V1", "V2","V2.1"])

if page == "V1":
    # Sidebar
    st.sidebar.title("🔍 FlipOse-RE-Analytics-V1")
    
    ################################################################################################################################
    
    # --- File Paths ---
    df_path = "target_df.csv"
    area_stats_path = "df_area_plot_stats.xlsx"
    cat_plot_path = "original_df_description_year.xlsx"
    summary = "data_summary.xlsx"
    sample = "sample_df.csv"
    
    # --- Load Data with Error Handling ---
    
    def load_csv(file_path):
        try:
            return pd.read_csv(file_path)
        except FileNotFoundError:
            st.sidebar.error(f"File not found: {file_path}")
            st.stop()
    
    def load_excel(file_path):
        try:
            return pd.read_excel(file_path)
        except FileNotFoundError:
            st.sidebar.error(f"File not found: {file_path}")
            st.stop()
    
    # --- Load Main Dataset ---
    df = load_csv(df_path)
    st.sidebar.success("All data loaded, 🔍 Explore the Dash Board")
    
    # --- Load Area Stats ---
    df_area_plot_stats = load_excel(area_stats_path)
    
    # --- Sidebar Navigation ---
    sidebar_option = st.sidebar.radio("Choose View", [
        "Data Summary",
        "Pareto Analysis",
        "Univariate Analysis",
        "Bivariate Analysis",
        "Geo Graphical Analysis",
        "Price Prediction Model"
    ])
    
    # --- View 1: Data Summary ---
    if sidebar_option == "Data Summary":
        st.subheader("📄 Transactions Data")
        tab1, tab2, tab3 = st.tabs(["Preview", "Summary","Notes"])
        with tab1:
            sample_df = pd.read_csv(sample)
            st.markdown("--> Repeated columns i.e Arabic and Id columns are dropped from Data")
            sample_df  = sample_df.drop(sample_df.columns[0], axis=1)
            st.dataframe(sample_df)
    
    
        with tab2:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(label="Number Of Columns", value = 46)
            with col2:
                st.metric(label="Total Records", value = "1,424,588")
            with col3:
                st.metric(label="Start Date(Instance_date)", value="1966-01-18")
            with col4:
                st.metric(label="End Date(Instance_date)", value="2025-04-03")
            
            summary_df = pd.read_excel(summary)
            # Format all numeric columns with commas
            for col in summary_df.select_dtypes(include='number').columns:
                summary_df[col] = summary_df[col].apply(lambda x: f"{x:,.0f}" if pd.notnull(x) else x)
    
            summary_df.index = range(1, len(summary_df) + 1)
            summary_df.rename(columns={'No_of_units': 'Num_of_Unique_values'}, inplace=True)
            summary_df = summary_df.drop(columns = ["S.no", "Level"])
            st.dataframe(summary_df)
    
        with tab3:
            notes = "notes.xlsx"
            notes_df = pd.read_excel(notes)
            if 'nRecords' in notes_df.columns:
                notes_df['nRecords'] = notes_df['nRecords'].apply(lambda x: f"{x:,}" if pd.notnull(x) else x)
                st.dataframe(notes_df)
            
    
    # --- View 2: Pareto Analysis ---
    elif sidebar_option == "Pareto Analysis":
        st.markdown("### Pareto Analysis by Area_name_en")
    
        try:
            pereto_file = "pereto_analysis_file.xlsx"
            pereto_analyis = pd.ExcelFile(pereto_file)
            pereto_sheet_names = pereto_analyis.sheet_names
        except FileNotFoundError:
            st.error(f"File not found: {pereto_file}")
            st.stop()
    
        # Read all sheets
        all_sheets_df = pd.read_excel(pereto_analyis, sheet_name=pereto_sheet_names)
    
        # Extract specific sheets
        pareto_summary = all_sheets_df["Pereto_Analysis_by_area_name"]
        ABC_summary = all_sheets_df["ABC_Area_name"]
    
        # Create tabs
        tab1, tab2, tab3 = st.tabs(["Table", "Chart", "ABC summary"])
    
        with tab1:
            #st.markdown("### Pareto Analysis by Area_name_en")
            pareto_summary.rename(columns={'Cum%_areas': 'Cum%_Areas'}, inplace=True)
            pareto_summary.rename(columns={'Percentage(%)': '%_nRecords'}, inplace=True) 
            pareto_summary.rename(columns={'Cumulative_%': 'Cum%_Records'}, inplace=True)
            pareto_summary['nRecords'] = pareto_summary['nRecords'].apply(lambda x: f"{x:,.0f}" if pd.notnull(x) else x)
            pareto_summary['Cum%_Records'] = pareto_summary['Cum%_Records'].apply(lambda x: f"{x:.2f}%" if pd.notnull(x) else x)
            pareto_summary['%_nRecords'] = pareto_summary['%_nRecords'].apply(lambda x: f"{x:.2f}%" if pd.notnull(x) else x)
            pareto_summary['Cum%_Areas'] = pareto_summary['Cum%_Areas'].apply(lambda x: f"{x:.2f}%" if pd.notnull(x) else x)
            pareto_summary.index = range(1, len(pareto_summary) + 1)
            st.dataframe(pareto_summary, use_container_width=True)
    
        with tab2:
            # Load Excel data
            excel_file_path = "pereto_analysis_only.xlsx"
            df2 = pd.read_excel(excel_file_path)
    
            # Remove any row where area_name_en is 'Total' (case-insensitive)
            df2 = df2[~df2['area_name_en'].str.strip().str.lower().eq('total')]
    
            # Sort and calculate cumulative values
            df2_sorted = df2.sort_values(by='nRecords', ascending=False).reset_index(drop=True)
            df2_sorted['Cumulative_nRecords'] = df2_sorted['nRecords'].cumsum()
            df2_sorted['Cumulative_%'] = (df2_sorted['Cumulative_nRecords'] / df2_sorted['nRecords'].sum()) * 100
    
            # Create figure with secondary y-axis
            fig = make_subplots(specs=[[{"secondary_y": True}]])
    
            # Add bar for nRecords
            fig.add_trace(
                go.Bar(
                    name='nRecords',
                    x=df2_sorted['area_name_en'],
                    y=df2_sorted['nRecords'],
                    marker_color='blue',
                    hovertemplate='<b>%{x}</b><br>nRecords: %{y}<extra></extra>'
                ),
                secondary_y=False,
            )
    
            # Add line for Cumulative %
            fig.add_trace(
                go.Scatter(
                    name='Cumulative_%',
                    x=df2_sorted['area_name_en'],
                    y=df2_sorted['Cumulative_%'],
                    mode='lines',
                    marker_color='red',
                    hovertemplate='<b>%{x}</b><br>Cumulative %: %{y:.2f}%<extra></extra>'
                ),
                secondary_y=True,
            )
    
            # Axis settings
            fig.update_xaxes(title_text='area_name_en')
    
            # Set fixed linear y-axis for better scaling
            fig.update_yaxes(
                title_text='nRecords',
                tickvals=np.arange(0, 100001, 20000),
                range=[0, 100000],
                secondary_y=False
            )
            fig.update_yaxes(title_text='Cumulative %', secondary_y=True)
    
            # Add breakdown lines at specified areas
            wadi_safa_index = df2_sorted[df2_sorted['area_name_en'] == 'Wadi Al Safa 5'].index
            al_hebiah_index = df2_sorted[df2_sorted['area_name_en'] == 'Al Hebiah Third'].index
    
            if not wadi_safa_index.empty:
                fig.add_vline(
                    x=wadi_safa_index[0],
                    line_dash="dash",
                    line_color="green",
                    #annotation_text="Wadi Al Safa 5 (40%)",
                    #annotation_position="top"
                )
    
            if not al_hebiah_index.empty:
                fig.add_vline(
                    x=al_hebiah_index[0],
                    line_dash="dash",
                    line_color="purple",
                    #annotation_text="Al Hebiah Third (70%)",
                    #annotation_position="top"
                )
    
            # Layout settings
            fig.update_layout(
                title_text='Pareto Analysis by Area',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                hovermode='x unified',
                height=600,
                barmode='group'
            )
    
            # Display chart in Streamlit
            st.plotly_chart(fig, use_container_width=True)
    
    
        with tab3:
            st.markdown("ABC Table")
            ABC_summary.rename(columns={'Cum%_records': 'Cum%_Records'}, inplace=True)
            ABC_summary.rename(columns={'Cum%_areas': 'Cum%_Areas'}, inplace=True)
            ABC_summary.rename(columns={'Group_name': 'Group'}, inplace=True)
    
            ABC_summary['nRecords'] = ABC_summary['nRecords'].apply(lambda x: f"{x:,.0f}" if pd.notnull(x) else x)
            ABC_summary['%Area'] = ABC_summary['%Area'].apply(lambda x: f"{x:.2f}%" if pd.notnull(x) else x)
            ABC_summary['%Records '] = ABC_summary['%Records '].apply(lambda x: f"{x:.2f}%" if pd.notnull(x) else x)
            ABC_summary['Cum%_Records'] = ABC_summary['Cum%_Records'].apply(lambda x: f"{x:.2f}%" if pd.notnull(x) else x)
            ABC_summary['Cum%_Areas'] = ABC_summary['Cum%_Areas'].apply(lambda x: f"{x:.2f}%" if pd.notnull(x) else x)
    
            ABC_summary.index = range(1, len(ABC_summary) + 1)
    
            # Swap the columns
            cols = list(ABC_summary.columns)
            i, j = cols.index('Cum%_Records'), cols.index('Cum%_Areas')
            cols[i], cols[j] = cols[j], cols[i]
            ABC_summary = ABC_summary[cols]
    
            st.dataframe(ABC_summary, use_container_width=True)
    
            
            df = ABC_summary
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(
                go.Bar(name='%Area', x=df['Group'], y=df['%Area'], marker_color='skyblue',
                       hovertemplate='<b>%{x}</b><br>%Area: %{y:.2f}%<extra></extra>'),
                secondary_y=False)
            fig.add_trace(
                go.Bar(name='%Records', x=df['Group'], y=df['%Records '], marker_color='lightcoral',
                       hovertemplate='<b>%{x}</b><br>%Records: %{y:.2f}%<extra></extra>'),
                secondary_y=False)
            fig.add_trace(
                go.Scatter(name='Cum%_records', x=df['Group'], y=df['Cum%_Records'], mode='lines+markers',
                           marker_color='green',
                           hovertemplate='<b>%{x}</b><br>Cum% Records: %{y:.2f}%<extra></extra>'),
                secondary_y=True)
            fig.add_trace(
                go.Scatter(name='Cum%_areas', x=df['Group'], y=df['Cum%_Areas'], mode='lines+markers',
                           marker_color='darkorange',
                           hovertemplate='<b>%{x}</b><br>Cum% Areas: %{y:.2f}%<extra></extra>'),
                secondary_y=True)
            fig.update_xaxes(title_text='Group')
            fig.update_yaxes(title_text='Counts (%Area, %Records)', secondary_y=False)
            fig.update_yaxes(title_text='Cumulative Percentage', secondary_y=True)
            fig.update_layout(
                title_text='ABC chart',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                hovermode='x unified'
            )
            st.plotly_chart(fig)
            
    # --- View 3: Univariate Analysis  ---
    if sidebar_option == "Univariate Analysis":
    
        # Load Excel Sheets
        try:
            cat_plot_path = "original_df_description_tables.xlsx"
            xls = pd.ExcelFile(cat_plot_path)
            sheet_names = xls.sheet_names
        except FileNotFoundError:
            st.error(f"File not found: {cat_plot_path}")
            st.stop()
    
        main_tabs = st.tabs([ "Dimensions","Metrics"])
    
        with main_tabs[0]:
            # Select sheet before tabs
            selected_sheet = st.selectbox("Distribution of nRecords by", sheet_names)
            df = pd.read_excel(xls, sheet_name=selected_sheet)
            col1 = df.columns[0]  # Category column
            #st.markdown("### 📊 Bar Plot (nRecords)")
            if "nRecords" in df.columns:
                fig_bar = px.bar(df, x=col1, y="nRecords", title=f"nRecords by {col1}", color=col1)
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.warning("'nRecords' column not found.")
        with main_tabs[1]:
            # Dropdown for selecting the category column
            cat_cols = ["meter_sale_price", "procedure_area"]
            cat = st.selectbox("Select the metrics column:", cat_cols)
    
            # Create sub-tabs under the selected category
            sub_tabs = st.tabs(["Table", "Histogram", "Boxplot"])
    
            # 1️⃣ TABLE TAB
            with sub_tabs[0]:
                # Define mapping of category to list of files
                table_files = {
                    "meter_sale_price": [
                        "meter_sale_price_table_final.xlsx",
                        "bin_df_manual.xlsx"
                    ],
                    "procedure_area": [
                        "procedure_area_table_final.xlsx",
                        "bin_df_Procedure_area_manual_xyz.xlsx"
                    ]
                }
    
                # Get the selected category (ensure 'cat' is assigned earlier in your code)
                selected_tables = table_files.get(cat)
    
                if selected_tables:
                    for table_file in selected_tables:
                        try:
                            df = pd.read_excel(table_file)
    
                            # Apply comma formatting ONLY to bin files
                            if "bin_df" in table_file and "nRecords" in df.columns:
                                df['nRecords'] = df['nRecords'].apply(lambda x: f"{x:,}")
    
                            # Display the table
                            #st.markdown(f"#### Displaying: `{table_file}`")
                            st.dataframe(df, use_container_width=True)
    
                        except FileNotFoundError:
                            st.error(f"File not found: {table_file}")
                        except Exception as e:
                            st.error(f"Error reading `{table_file}`: {e}")
    
    
            # 2️⃣ HISTOGRAM TAB
            with sub_tabs[1]:
                # Mapping for bar chart Excel files (inside tab for clarity)
                plot_bar = {
                    "meter_sale_price": "bin_df_manual.xlsx",
                    "procedure_area": "bin_df_Procedure_area_manual_xyz.xlsx"
                }
    
                selected_bar = plot_bar.get(cat)
                if selected_bar:
                    try:
                        df_bar = pd.read_excel(selected_bar)
                        #st.markdown(f"### Barchart for `{cat}`")
                        fig = px.bar(
                            df_bar,
                            x= "bin_range",
                            y="nRecords",
                            #labels={"meter_sale_price": "meter_sale_price", "nRecords": "Number of Records"},
                            title=f"Distribution of {cat.replace('_', ' ').title()}",
                            text_auto=True)
                        # Add black border and control bar width
                        fig.update_traces(marker_line_color='black', marker_line_width=1)
    
                        # Optional: customize layout
                        fig.update_layout(
                            #xaxis_title="meter_sale_price",
                            #yaxis_title="Number of Records",
                            bargap=0,  # Adjust space between bars
                            height=500
                            )
                        st.plotly_chart(fig, use_container_width=True)
                    except FileNotFoundError:
                        st.error(f"File not found: {selected_bar}")
                    except Exception as e:
                        st.error(f"Error creating bar chart: {e}")
    
            with sub_tabs[2]:
                # Mapping for boxplot HTML files
                plot_box = {
                    "meter_sale_price": "meter_sale_price_with_boxplot.html",
                    "procedure_area": "procedure_area_with_boxplot.html"
                }
    
                # Mapping for corresponding PNG images
                plot_images = {
                    "meter_sale_price": "boxplot_meter_sale_price_raw.png",
                    "procedure_area": "boxplot_procedure_area_raw.png"
                }
    
                selected_file = plot_box.get(cat)
                selected_image = plot_images.get(cat)
    
                # Adjusting columns: 2 for image (col1), 3 for boxplot (col2)
                col1, col2 = st.columns([2, 3])
    
                with col1:
                    if selected_image:
                        try:
                            # Display image with automatic scaling to container width
                            st.image(selected_image, use_container_width=True)
                        except FileNotFoundError:
                            st.error(f"Image not found: {selected_image}")
                        except Exception as e:
                            st.error(f"Error loading image: {e}")
    
                with col2:
                    if selected_file:
                        try:
                            with open(selected_file, "r") as file:
                                html_content = file.read()
                                components.html(html_content, height=500, width=800, scrolling=True)
                        except FileNotFoundError:
                            st.error(f"File not found: {selected_file}")
                        except Exception as e:
                            st.error(f"Error loading boxplot HTML: {e}")
    
            
                        
    # --- View 3: Bivariate Analysis  ---
    if sidebar_option == "Bivariate Analysis":
        
        # Step 1: Dropdown selector at the top
        cat_cols = [
            "trans_group_en", "property_type_en", "property_sub_type_en", "property_usage_en", 
            "nearest_metro_en","nearest_landmark_en","nearest_mall_en", "room_en", "reg_type_en", 
            "procedure_name_en","instance_year"
        ]
        cat = st.selectbox("nRecords and Avg_Meter_Sale_Price (Dirham) by:", cat_cols)
        main_tabs = st.tabs([ "Table","charts"])
        with main_tabs[1]:
            # Step 3: Read the Excel for box plot data
            try:
                cat_plot_path = "original_df_description_tables.xlsx"
                xls = pd.ExcelFile(cat_plot_path)
                sheet_names = xls.sheet_names
                selected_sheet = sheet_names[cat_cols.index(cat)]  # Optional: auto match sheet to cat
                df = pd.read_excel(xls, sheet_name=selected_sheet)
            except FileNotFoundError:
                st.error(f"Excel file not found: {cat_plot_path}")
                st.stop()
            except Exception as e:
                st.error(f"Error loading Excel sheet: {e}")
                st.stop()
    
            # Step 4: Display two columns
            col1, col2 = st.columns(2)
    
        with col1:
            # Function to create overlay plot for a single sheet
            def plot_avg_price_and_count_overlay(df1, df2, category_col, labels=("Raw data", "Model_Data")):
                """
                Returns a Plotly figure showing average meter sale price and record count overlay for two DataFrames.
                """
                target_col = "Avg_meter_sale_price"
    
                fig = make_subplots(specs=[[{"secondary_y": True}]])
    
                # First DataFrame
                fig.add_trace(go.Bar(
                    x=df1[category_col],
                    y=df1['nRecords'],
                    name=f'nRecords ({labels[0]})',
                    opacity=0.6
                ), secondary_y=False)
    
                fig.add_trace(go.Scatter(
                    x=df1[category_col],
                    y=df1[target_col],
                    mode='lines+markers',
                    name=f'Avg Price ({labels[0]})'
                ), secondary_y=True)
    
                # Second DataFrame
                fig.add_trace(go.Bar(
                    x=df2[category_col],
                    y=df2['nRecords'],
                    name=f'nRecords ({labels[1]})',
                    opacity=0.6
                ), secondary_y=False)
    
                fig.add_trace(go.Scatter(
                    x=df2[category_col],
                    y=df2[target_col],
                    mode='lines+markers',
                    name=f'Avg Price ({labels[1]})'
                ), secondary_y=True)
    
                # Layout
                fig.update_layout(
                    title=(f'nRecords & Avg Price'),
                    xaxis_title=category_col,
                    yaxis=dict(title='nRecords'),
                    yaxis2=dict(title='Average Meter Sale Price', overlaying='y', side='right'),
                    legend=dict(x=0.99, y=1.2),
                    hovermode='x unified',
                    barmode='group'
                )
    
                return fig
                
            file1 = "description_raw.xlsx"
            file2 = "description_units20.xlsx"
    
            if file1 and file2:
                    raw_excel = pd.read_excel(file1, sheet_name=None)
                    model_excel = pd.read_excel(file2, sheet_name=None)
    
                    #common_sheets = sorted(set(raw_excel.keys()) & set(model_excel.keys()))
    
                    if selected_sheet:
                            # Load data from the selected sheet
                            df1 = raw_excel[selected_sheet]
                            df2 = model_excel[selected_sheet]
    
                            if len(df1.columns) > 0:
                                category_col = df1.columns[0]
                                fig = plot_avg_price_and_count_overlay(df1, df2, category_col)
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.warning(f"⚠️ Sheet '{selected_sheet}' has no columns to plot.")
            else:
                    st.info("Upload both Excel files to continue.")
    
    
        with col2:
            def plot_boxplot_per_category(df, cat_col):
                required_cols = {'min', '25%', '50%', '75%', 'max'}
                if not required_cols.issubset(df.columns):
                    st.warning("DataFrame missing required quantile columns.")
                    return None
    
                fig = go.Figure()
                for _, row in df.iterrows():
                    category = row[cat_col]
                    q1 = row['25%']
                    median = row['50%']
                    q3 = row['75%']
                    min_val = row['min']
                    max_val = row['max']
                    iqr = q3 - q1
                    lower_fence = max(min_val, q1 - 1.5 * iqr)
                    upper_fence = min(max_val, q3 + 1.5 * iqr)
    
                    fig.add_trace(go.Box(
                        name=str(category),  # Label on x-axis
                        q1=[q1],
                        median=[median],
                        q3=[q3],
                        lowerfence=[lower_fence],
                        upperfence=[upper_fence],
                        boxpoints=False,
                    ))
    
                fig.update_layout(
                    title=("Distribution of meter_sale_price"),
                    yaxis_title="Meter Sale Price",
                    boxmode='group',
                    xaxis_title=cat_col,
                    xaxis=dict(tickangle=45, automargin=True),  # Label rotation
                )
                return fig
    
            box_plot = plot_boxplot_per_category(df, df.columns[0])
            if box_plot:
                st.plotly_chart(box_plot, use_container_width=True)
                
        with main_tabs[0]:
            note = "notes.xlsx"
            note_df = pd.read_excel(note)
            st.markdown("Data Explaination")
            st.dataframe(note_df)
            try:
                # Load the raw description data from the corresponding sheet
                description_data = pd.read_excel("table_stats_bivariate.xlsx", sheet_name=cat)
                description_data['Avg_meter_sale_price'] = description_data['Avg_meter_sale_price'].apply(lambda x: f"{x:.2f}" if pd.notnull(x) else x)
                description_data['q1'] = description_data['q1'].apply(lambda x: f"{x:.2f}" if pd.notnull(x) else x)
                description_data['Median'] = description_data['Median'].apply(lambda x: f"{x:.2f}" if pd.notnull(x) else x)
                description_data['q3'] = description_data['q3'].apply(lambda x: f"{x:.2f}" if pd.notnull(x) else x)
                #st.subheader(f"Raw Description Table - {cat}")
                st.dataframe(description_data, use_container_width=True)
            except Exception as e:
                st.error(f"Failed to load data for table view: {e}")
    
    
            
            
            
            
    # --- View 5: Price Prediction Model ---
    # Define file paths
    EXCEL_PATH = "Over_all_output.xlsx"
    model_perfomance =  "Model_performance.xlsx"
    html_lr = "predicted_vs_actual_linear.html"
    html_dt = "predicted_vs_actual_decision_tree.html"
    html_xgb = "predicted_vs_actual_XGB_regressor.html"
    html_comparision = "model_perfor_comparision.html"
    
    # Load Excel file with caching
    @st.cache_data
    def load_excel(path):
        xls = pd.ExcelFile(path)
        sheets = xls.sheet_names
        data = {sheet: xls.parse(sheet) for sheet in sheets}
        return data
    
    
    # === Sidebar Selection ===
    if sidebar_option == "Price Prediction Model":
    
        # === Top-Level Tabs ===
        if st.sidebar.button("Show Data Preparation Details"):
            st.markdown("""
                - Data used for model is based on the following:
                    - Outliers removed using `meter_sale_price` and `procedure_area` columns.
                    - From outliers-removed data, we have considered data from the year **2020**.
                        - For the model, we have used data with property type **"Units"**.
                - We had a large number of independent variables in the dataset.
                - To identify the most relevant predictors, we applied a **stepwise regression model**.
                - This method helped us select the best combination of input variables for modeling.
                - Using these selected variables, we built the final model and obtained the results.
                """)
        main_tabs = st.tabs(["📈 Model Performance Tables","📉 Prediction Model Visuals"])
        
        # === Tab 1: Prediction Model Visuals ===
        with main_tabs[1]:
            if os.path.exists(EXCEL_PATH):
                xl = pd.ExcelFile(EXCEL_PATH)
                sheet_names = xl.sheet_names
    
            if len(sheet_names) >= 2:
                first_sheet_name = sheet_names[0]  # Index 1 = second sheet
                df = xl.parse(sheet_name=first_sheet_name)
                df = df.round(2)
                if 'nObservations' in df.columns:
                    df['nObservations'] = df['nObservations'].apply(lambda x: f"{x:,.0f}" if pd.notnull(x) else x)
                    if 'MAPE' in df.columns:
                        df['MAPE'] = df['MAPE'].apply(lambda x: f"{x * 100:.2f}%" if pd.notnull(x) else x)
                df.index = range(1, len(df) + 1)
    
                st.subheader(f"📊 {first_sheet_name}")
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("The Excel file has less than 2 sheets.")
                
            st.subheader("🔍 Overall Comparison Report")
            if os.path.exists(html_comparision):
                with open(html_comparision, "r", encoding="utf-8") as f:
                    components.html(f.read(), height=300, scrolling=True)
            else:
                st.warning(f"Comparison HTML not found at: {html_comparision}")
    
            st.subheader("📊 Logistic Regression")
            st.markdown("###Equation : Predicted_price = 0.40134 * Actual_price + 8966.97")
            if os.path.exists(html_lr):
                with open(html_lr, "r", encoding="utf-8") as f:
                    components.html(f.read(), height=400, scrolling=True)
            else:
                st.warning(f"Logistic Regression HTML not found at: {html_lr}")
    
            st.subheader("🌳 Decision Tree")
            st.markdown("###Equation : Predicted_price = 0.465166 * Actual_price + 7993.22")
            if os.path.exists(html_dt):
                with open(html_dt, "r", encoding="utf-8") as f:
                    components.html(f.read(), height=400, scrolling=True)
            else:
                st.warning(f"Decision Tree HTML not found at: {html_dt}")
    
            st.subheader("🚀 XGBoost")
            st.markdown("###Equation : Predicted_price = 0.463650 * Actual_price + 8055.86")
            if os.path.exists(html_xgb):
                with open(html_xgb, "r", encoding="utf-8") as f:
                    components.html(f.read(), height=400, scrolling=True)
            else:
                st.warning(f"XGBoost HTML not found at: {html_xgb}")
    
        # === Tab 3: Area & Sector Sheets ===
        with main_tabs[0]:
                
            Over_all, sector_tab,area_tab = st.tabs(["Over All","Sector wise","Area wise"])
            with Over_all:
                abc = "Over_all_output.xlsx"
                overall_sheets = pd.read_excel(abc, sheet_name=None)
                if overall_sheets:
                    # Process each sheet
                    for sheet_name in overall_sheets:
                        df = overall_sheets[sheet_name]
                        # Format 'MAPE' as percentage string
                        if 'MAPE' in df.columns:
                            df['MAPE'] = df['MAPE'].apply(lambda x: f"{x * 100:.2f}%" if pd.notnull(x) else x)
                            # Format 'nObservations' with commas
                            if 'nObservations' in df.columns:
                                df['nObservations'] = df['nObservations'].apply(lambda x: f"{x:,}" if pd.notnull(x) else x)
                                overall_sheets[sheet_name] = df  # Update in dictionary
                                # Display each sheet in a tab
                    overall_tabs = st.tabs(list(overall_sheets.keys()))
                    for tab, (sheet_name, df) in zip(overall_tabs, overall_sheets.items()):
                        with tab:
                            st.dataframe(df, use_container_width=True)
                
               
            with sector_tab:
                pqr = "sector_name_Output.xlsx"
    
                # Read all sheets
                sector_sheets = pd.read_excel(pqr, sheet_name=None)
    
                if sector_sheets:
                    # Process each sheet
                    for sheet_name in sector_sheets:
                        df = sector_sheets[sheet_name]
                
                        # Format 'MAPE' as percentage string
                        if 'MAPE' in df.columns:
                            df['MAPE'] = df['MAPE'].apply(lambda x: f"{x * 100:.2f}%" if pd.notnull(x) else x)
    
                        # Format 'nObservations' with commas
                        if 'nObservations' in df.columns:
                            df['nObservations'] = df['nObservations'].apply(lambda x: f"{x:,}" if pd.notnull(x) else x)
    
                        sector_sheets[sheet_name] = df  # Update in dictionary
    
                    # Display each sheet in a tab
                    sector_tabs = st.tabs(list(sector_sheets.keys()))
                    for tab, (sheet_name, df) in zip(sector_tabs, sector_sheets.items()):
                        with tab:
                            st.dataframe(df, use_container_width=True)
            
            with area_tab:
                xyz = "Area_name_output.xlsx"
    
                # Read all sheets
                area_sheets = pd.read_excel(xyz, sheet_name=None)
    
                if area_sheets:
                    for sheet_name in area_sheets:
                        df = area_sheets[sheet_name]
                
                        # Convert MAPE to percentage
                        if 'MAPE' in df.columns:
                            df['MAPE'] = df['MAPE'].apply(lambda x: f"{x * 100:.2f}%" if pd.notnull(x) else x)
    
                        # Format nObservations with commas
                        if 'nObservations' in df.columns:
                            df['nObservations'] = df['nObservations'].apply(lambda x: f"{x:,}" if pd.notnull(x) else x)
    
                        area_sheets[sheet_name] = df  # Update back in dict
    
                    # Create tabs and display each sheet
                    area_tabs = st.tabs(list(area_sheets.keys()))
                    for tab, (sheet_name, df) in zip(area_tabs, area_sheets.items()):
                        with tab:
                            st.dataframe(df, use_container_width=True)
    
                        
                    
    
    # --- View 6: Geo Graphical Analysis ---
    if sidebar_option == "Geo Graphical Analysis":
        st.subheader("Dubai Area-wise Bubble Map")
        
        df_excel = pd.read_excel("new_tdf.xlsx")
        units_excel = pd.read_excel("units_20.xlsx")
        outlier_excel = pd.read_excel("outliers.xlsx")  # Replace with your actual outlier dataset
        tab1, = st.tabs(["Average Meter Sale Price"])
    
        # Create the single tab
        with tab1:
    
            # Add filtered data (e.g., >= 2020)
            figs = px.scatter_mapbox(
                units_excel,
                lat='area_lat',
                lon='area_lon',
                size='Transaction Count',
                color='Average Meter Sale Price',
                hover_name='area_name_en',
                hover_data={
                    'Transaction Count': True,
                    'Average Meter Sale Price': ':.2f',
                    'area_lat': False,
                    'area_lon': False
                },
                color_continuous_scale='Hot',
                size_max=30,
                zoom=9,
                title="Dubai Area-wise Average Meter Sale Price(Dirham) and Transaction Count"
            )
    
            for trace in figs.data:
                trace.name = "Model_Data"
                trace.legendgroup = "Model_Data"
                trace.showlegend = True
                
                
    
            # Add filtered data (e.g., >= 2020)
            fig2 = px.scatter_mapbox(
                df_excel,
                lat='area_lat',
                lon='area_lon',
                size='Transaction Count',
                color='Average Meter Sale Price',
                hover_name='area_name_en',
                hover_data={
                    'Transaction Count': True,
                    'Average Meter Sale Price': ':.2f',
                    'area_lat': False,
                    'area_lon': False
                },
                color_continuous_scale='Hot',
                size_max=30,
                opacity=0.8,
                zoom=9,
            )
    
            for trace in fig2.data:
                trace.name = "Raw data"
                trace.legendgroup = "Raw data"
                trace.showlegend = True
                figs.add_trace(trace)
                
    
            # Add outlier data
            fig3 = px.scatter_mapbox(
                outlier_excel,
                lat='area_lat',
                lon='area_lon',
                size='Transaction Count',
                color='Average Meter Sale Price',
                hover_name='area_name_en',
                hover_data={
                    'Transaction Count': True,
                    'Average Meter Sale Price': ':.2f',
                    'area_lat': False,
                    'area_lon': False
                },
                color_continuous_scale='Hot',
                size_max=30,
                opacity=0.7,
                zoom=9
            )
    
            for trace in fig3.data:
                trace.name = "Non_Model_Data"
                trace.legendgroup = "Non_Model_Data"
                trace.showlegend = True
                figs.add_trace(trace)
    
            figs.update_layout(
                mapbox_style='open-street-map',
                margin={"r": 0, "t": 40, "l": 0, "b": 0},
                legend=dict(
                    x=0.01,
                    y=0.99,
                    bgcolor='rgba(255,255,255,0.8)',
                    bordercolor='black',
                    borderwidth=1
                )
            )
    
            st.plotly_chart(figs, use_container_width=True)
            st.markdown(
                """
                <div style="text-align: left; font-size: 15px; margin-top: 10px;">
                    <b>Size of bubble</b> = Number of Transactions &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; 
                    <b>Colour of bubble</b> = Average Meter Sale Price
                </div>
                """,
                unsafe_allow_html=True
            )


elif page == "V2":
    
    # Custom CSS (same style if you want consistency)
    st.markdown("""
        <style>
            [data-testid="collapsedControl"] {
                position: fixed;
                top: 500px;
                left: 50px;
                z-index: 100;
            }
            .block-container {
                padding-top: 2.5rem;
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.sidebar.title("🔍 FlipOse-RE-Analytics-V2")
    
    def load_csv(file_path):
        try:
            return pd.read_csv(file_path)
        except FileNotFoundError:
            st.sidebar.error(f"File not found: {file_path}")
            st.stop()
    
    def load_excel(file_path):
        try:
            return pd.read_excel(file_path)
        except FileNotFoundError:
            st.sidebar.error(f"File not found: {file_path}")
            st.stop()
    
    # --- Load Main Dataset ---
        # --- File Paths ---
    #df_path = "target_df.csv"
    #area_stats_path = "df_area_plot_stats.xlsx"
    #cat_plot_path = "original_df_description_year.xlsx"
    summary = "V2_data_summary.xlsx"
    #sample = "sample_df.csv"
    # --- Load Area Stats ---
    #df_area_plot_stats = load_excel(area_stats_path)
    
    # --- Sidebar Navigation ---
    sidebar_option = st.sidebar.radio("Choose View", [
        "Data Summary",
        #"Pareto Analysis",
        "Univariate Analysis",
        "Bivariate Analysis",
        "Correlation",
        "Price Prediction Model"
    ])
    
    # --- View 1: Data Summary ---
    if sidebar_option == "Data Summary":
        st.subheader("📄 Micro_Data_combined")
        tab1, tab2 = st.tabs(["Summary","Notes"])
        with tab1:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(label="Number Of Columns", value = 107)
            with col2:
                st.metric(label="Total Records", value = "5,88,863")
            with col3:
                st.metric(label="Start Date(Instance_date)", value="2020-01-01")
            with col4:
                st.metric(label="End Date(Instance_date)", value="2025-04-03")
            
            summary_df = pd.read_excel(summary)
            # Format all numeric columns with commas
            for col in summary_df.select_dtypes(include='number').columns:
                summary_df[col] = summary_df[col].apply(lambda x: f"{x:,.0f}" if pd.notnull(x) else x)
    
            summary_df.index = range(1, len(summary_df) + 1)
            #summary_df.rename(columns={'No_of_units': 'Num_of_Unique_values'}, inplace=True)
            #summary_df = summary_df.drop(columns = ["S.no", "Level"])
            st.dataframe(summary_df)
    
        with tab2:
            notes = "V2_Notes.xlsx"
            notes_df = pd.read_excel(notes)
            if 'nRecords' in notes_df.columns:
                notes_df['nRecords'] = notes_df['nRecords'].apply(lambda x: f"{x:,}" if pd.notnull(x) else x)
                st.dataframe(notes_df)
    if sidebar_option == "Univariate Analysis":
        
        # Load Excel Sheets
        try:
            cat_plot_path = "V2-column_value_counts_with_avg_price.xlsx"
            xls = pd.ExcelFile(cat_plot_path)
            sheet_names = xls.sheet_names
        except FileNotFoundError:
            st.error(f"File not found: {cat_plot_path}")
            st.stop()
    
        main_tabs = st.tabs(["Dimensions", "Metrics"])
    
        with main_tabs[0]:  # DIMENSIONS
            dim_tabs = st.tabs(["nRecords Chart & Table", "Area-wise Chart & Table"])
        
            # 1️⃣ FIRST TAB
            with dim_tabs[0]:
                selected_sheet = st.selectbox("Distribution of nRecords by", sheet_names, key="nrecords_sheet")
                df = pd.read_excel(xls, sheet_name=selected_sheet)
                col_x = df.columns[0]  # Category column
        
                if "nRecords" in df.columns:
                    chart_df = df[df["nRecords"] != 0]  # filter out zero y-values
                    if not chart_df.empty:
                        fig_bar = px.bar(chart_df, x=col_x, y="nRecords",
                                         title=f"nRecords by {col_x}",
                                         color=col_x)
                        st.plotly_chart(fig_bar, use_container_width=True, key="nrecords_chart")
                    else:
                        st.warning("No data available with non-zero nRecords.")
                else:
                    st.warning("'nRecords' column not found.")
        
                st.dataframe(df, use_container_width=True, key="nrecords_table")
        
            # 2️⃣ SECOND TAB
            with dim_tabs[1]:
                cat_plot_path_1 = "V2_area_wise_value_counts.xlsx"
                area_wise = pd.ExcelFile(cat_plot_path_1)
                sheet_names_1 = area_wise.sheet_names
                selected_sheet_custom_1 = st.selectbox("Select Area_name", sheet_names_1, key="custom_sheet")
                df_custom_1 = pd.read_excel(area_wise, sheet_name=selected_sheet_custom_1)
            
                col_x_1 = df_custom_1.columns[0]  # X-axis
                y_axis_col = st.sidebar.selectbox(
                    "Select Area_name:",
                    [col for col in df_custom_1.columns if col != col_x_1],
                    key="custom_y_axis"
                )
            
                chart_df_custom = df_custom_1[df_custom_1[y_axis_col] != 0]  # filter out zero Y values
            
                if not chart_df_custom.empty:
                    fig_custom = px.bar(chart_df_custom, x=col_x_1, y=y_axis_col,
                                        title=f"{y_axis_col} by {col_x_1}",
                                        color=col_x_1)
                    st.plotly_chart(fig_custom, use_container_width=True)
                else:
                    st.warning(f"No data available for {y_axis_col} with non-zero values.")
            
                # Show only X and selected Y column (non-zero rows)
                st.dataframe(chart_df_custom[[col_x_1, y_axis_col]], use_container_width=True, key="custom_table")






    
        # ----------------- METRICS TAB -----------------
        with main_tabs[1]:
            
            # Map display names to file paths
            html_files = {
                "Meter Sale Price ": "meter_sale_price_boxplot.html",
                "Procedure Area ": "procedure_area_boxplot.html",
                "Actual_worth": "actual_worth_boxplot.html",
                "Unit balcony area": "unit_balcony_area_boxplot.html"
            }
            
            # Dropdown for selection
            selected_name = st.selectbox("Select a visualization:", list(html_files.keys()))
            
            # Get the corresponding HTML file path
            selected_file = html_files[selected_name]
            
            # Display the HTML
            try:
                with open(selected_file, "r") as file:
                    html_content = file.read()
                    components.html(html_content, height=600, scrolling=True)
            except FileNotFoundError:
                st.error(f"File not found: {selected_file}")
            except Exception as e:
                st.error(f"Error loading HTML: {e}")

        # --- View 3: Bivariate Analysis  ---
    if sidebar_option == "Bivariate Analysis":
                # Load Excel Sheets
        try:
            cat_plot_path = "V2-column_value_counts_with_avg_price.xlsx"
            xls = pd.ExcelFile(cat_plot_path)
            sheet_names = xls.sheet_names
        except FileNotFoundError:
            st.error(f"File not found: {cat_plot_path}")
            st.stop()
        selected_sheet = st.selectbox("Distribution of nRecords by", sheet_names, key="nrecords_sheet")
        df = pd.read_excel(xls, sheet_name=selected_sheet)
        col_x = df.columns[0]  # Category column

        if "nRecords" in df.columns and "Avg_Meter_Sale_Price" in df.columns:
            chart_df = df[(df["nRecords"] != 0) & (df["Avg_Meter_Sale_Price"].notnull())]  # filter out zero y-values
            if not chart_df.empty:
                # Create figure with secondary y-axis
                from plotly.subplots import make_subplots
                import plotly.graph_objects as go

                fig = make_subplots(specs=[[{"secondary_y": True}]])

                # Bar for nRecords
                fig.add_trace(
                    go.Bar(x=chart_df[col_x], y=chart_df["nRecords"], name="nRecords"),
                    secondary_y=False
                )

                # Line for Avg_meter_sale_price
                fig.add_trace(
                    go.Scatter(x=chart_df[col_x], y=chart_df["Avg_Meter_Sale_Price"],
                               mode="lines+markers", name="Avg_meter_sale_price"),
                    secondary_y=True
                )

                fig.update_layout(
                    title=f"nRecords and Avg_meter_sale_price by {col_x}",
                    xaxis_title=col_x,
                    yaxis_title="nRecords",
                    yaxis2_title="Avg_meter_sale_price (Dirham)"
                )

                st.plotly_chart(fig, use_container_width=True, key="nrecords_chart")
            else:
                st.warning("No data available with non-zero nRecords and valid Avg_meter_sale_price.")
        else:
            st.warning("'nRecords' or 'Avg_meter_sale_price' column not found.")

        st.dataframe(df, use_container_width=True, key="nrecords_table")

 # Define file paths
    metrics = "V2_Model_metrics.xlsx"
    model_perfomance =  "Model_performance.xlsx"
    html_lr = "predicted_vs_actual_linear.html"
    html_dt = "predicted_vs_actual_decision_tree.html"
    html_xgb = "predicted_vs_actual_XGB_regressor.html"
    html_comparision = "model_perfor_comparision.html"
    
    # Load Excel file with caching
    @st.cache_data
    def load_excel(path):
        xls = pd.ExcelFile(path)
        sheets = xls.sheet_names
        data = {sheet: xls.parse(sheet) for sheet in sheets}
        return data
    
    
    # === Sidebar Selection ===
    if sidebar_option == "Price Prediction Model":
    
        # === Top-Level Tabs ===
        if st.sidebar.button("Show Data Preparation Details"):
            st.markdown("""
                - Data used for model is based on the following:
                    - Outliers removed using `meter_sale_price` and `procedure_area` columns.
                    - From outliers-removed data, we have considered data from the year **2020**.
                        - For the model, we have used data with property type **"Units"**.
                - We had a large number of independent variables in the dataset.
                - To identify the most relevant predictors, we applied a **stepwise regression model**.
                - This method helped us select the best combination of input variables for modeling.
                - Using these selected variables, we built the final model and obtained the results.
                """)
        main_tabs = st.tabs(["📈 Model Performance Tables","📉 Prediction Model Visuals"])
        
        # === Tab 1: Prediction Model Visuals ===
                
        with main_tabs[1]:
            area_sheet = "V2_area_wise outputs.xlsx"
        
            # Load Excel file as ExcelFile so we can parse by sheet name
            xl = pd.ExcelFile(area_sheet)
            sheet_names = xl.sheet_names
        
            combined_df = pd.DataFrame()
        
            for sheet in sheet_names[:2]:  # Take only first 2 sheets
                df_temp = xl.parse(sheet_name=sheet)
                df_temp = df_temp.round(2)
        
                if 'area_name_en' in df_temp.columns and 'R2' in df_temp.columns:
                    df_temp['R2'] = pd.to_numeric(df_temp['R2'], errors='coerce')
                    df_temp['Sheet'] = sheet  # Label for distinguishing lines
                    combined_df = pd.concat([combined_df, df_temp[['area_name_en', 'R2', 'Sheet']]])
        
            if not combined_df.empty:
                # Sort for proper plotting
                combined_df = combined_df.sort_values(by='area_name_en')
        
                # Plot both sheets on same line chart
                fig = px.line(
                    combined_df,
                    x='area_name_en',
                    y='R2',
                    color='Sheet',
                    markers=True,
                    title="R² Comparison by Area (Both Sheets)"
                )
                fig.update_layout(
                    xaxis_title="Area Name",
                    yaxis_title="R²",
                    hovermode="x unified"
                )
                st.plotly_chart(fig, use_container_width=True)
        
                # Show combined dataframe
                st.dataframe(combined_df, use_container_width=True)
            else:
                st.warning("No valid data found in the first two sheets.")

        
        



    
        # === Tab 3: Area & Sector Sheets ===
        with main_tabs[0]:
                
            Over_all,area_tab = st.tabs(["Over All","Area wise"])
            with Over_all:
                abc_1 = "V2_Model_metrics.xlsx"
                overall_sheets = pd.read_excel(abc_1, sheet_name=None)
                if overall_sheets:
                    # Process each sheet
                    for sheet_name in overall_sheets:
                        df = overall_sheets[sheet_name]
                        # Format 'MAPE' as percentage string
                        if 'MAPE' in df.columns:
                            df['MAPE'] = df['MAPE'].apply(lambda x: f"{x * 100:.2f}%" if pd.notnull(x) else x)
                            # Format 'nObservations' with commas
                            #if 'nObservations' in df.columns:
                                #df['nObservations'] = df['nObservations'].apply(lambda x: f"{x:,}" if pd.notnull(x) else x)
                            overall_sheets[sheet_name] = df  # Update in dictionary
                                # Display each sheet in a tab
                    overall_tabs = st.tabs(list(overall_sheets.keys()))
                    for tab, (sheet_name, df) in zip(overall_tabs, overall_sheets.items()):
                        with tab:
                            st.dataframe(df, use_container_width=True)
            
            with area_tab:
                xyz = "V2_area_wise outputs.xlsx"
    
                # Read all sheets
                area_sheets = pd.read_excel(xyz, sheet_name=None)
    
                if area_sheets:
                    for sheet_name in area_sheets:
                        df = area_sheets[sheet_name]
                
                        # Convert MAPE to percentage
                        if 'MAPE' in df.columns:
                            df['MAPE'] = df['MAPE'].apply(lambda x: f"{x :.2f}%" if pd.notnull(x) else x)
    
                        # Format nObservations with commas
                        if 'nObservations' in df.columns:
                            df['nObservations'] = df['nObservations'].apply(lambda x: f"{x:,}" if pd.notnull(x) else x)
    
                        area_sheets[sheet_name] = df  # Update back in dict
    
                    # Create tabs and display each sheet
                    area_tabs = st.tabs(list(area_sheets.keys()))
                    for tab, (sheet_name, df) in zip(area_tabs, area_sheets.items()):
                        with tab:
                            st.dataframe(df, use_container_width=True)

    # --- View 6: Geo Graphical Analysis ---
    if sidebar_option == "Correlation":
        from PIL import Image
        import plotly.express as px
    
        correlation, Dropping_Features = st.tabs(["correlation", "Dropping_Features"])
    
        with correlation:
            # Read PNG file
            image = Image.open("Associations_correlation.png")
            img_array = np.array(image)
    
            # Create Plotly figure for zoom/pan
            fig_corr = px.imshow(img_array)
            fig_corr.update_xaxes(visible=False)
            fig_corr.update_yaxes(visible=False)
            fig_corr.update_layout(
                title="Dython Nominal Associayions",
                dragmode="pan"
            )
    
            # Show in Streamlit
            st.plotly_chart(fig_corr, use_container_width=True, key="corr_tab")
    
        with Dropping_Features:
            # First image
            image_1 = Image.open("V2_high_correlated.png")
            img_array_1 = np.array(image_1)
    
            fig_drop1 = px.imshow(img_array_1)
            fig_drop1.update_xaxes(visible=False)
            fig_drop1.update_yaxes(visible=False)
            fig_drop1.update_layout(
                title="High Correlated Features",
                dragmode="pan"
            )
    
            st.plotly_chart(fig_drop1, use_container_width=True, key="drop_tab_1")
    
            # Second image
            image_2 = Image.open("V2_drop_features.png")
            img_array_2 = np.array(image_2)
    
            fig_drop2 = px.imshow(img_array_2)
            fig_drop2.update_xaxes(visible=False)
            fig_drop2.update_yaxes(visible=False)
            fig_drop2.update_layout(
                title="Dropped Features",
                dragmode="pan"
            )
    
            st.plotly_chart(fig_drop2, use_container_width=True, key="drop_tab_2")

    
#########################################################################################################################################################################
#######################################################################################################################################################################

elif page == "V2.1":
    
    st.sidebar.title("🔍 FlipOse-RE-Analytics-V2.1")
    
    # Sidebar navigation
    sidebar_option = st.sidebar.radio("Choose Section", [
        "📂 Data Files",
        "📊 EDA & Feature Engineering",
        "📈 Model Results",
        "🤖 Model Input / Prediction"
    ])
    drop_col = ['Unnamed: 0']  # list instead of string
    
    train_file_path = "df_trained_dataset_6000.csv"  # Replace with your CSV path
    test_file_path = "test_data_20 areas.csv"  # Replace with your CSV path
    
    # --- Load Train Data ---
    try:
        df_train = pd.read_csv(train_file_path)
        # Drop columns if they exist
        df_train = df_train.drop(columns=[col for col in drop_col if col in df_train.columns])
        # st.dataframe(df_train)
    except FileNotFoundError:
        st.error(f"Training file not found: {train_file_path}")
    
    # --- Load Test Data ---
    try:
        df_test = pd.read_csv(test_file_path)
        df_test = df_test.drop(columns=[col for col in drop_col if col in df_test.columns])
        # st.dataframe(df_test)
    except FileNotFoundError:
        st.error(f"Test file not found: {test_file_path}")


        
    # --- Data Files Tab with inner tabs ---
    if sidebar_option == "📂 Data Files":
        st.header("📂 Data Files Overview")
        
        # Create inner tabs for Training and Test data
        tab1, tab2 = st.tabs(["Training Data", "Test Data"])
        
        # --- Training Data Tab ---
        with tab1:
            st.subheader("Training Dataset")
            st.dataframe(df_train)
    
        
        # --- Test Data Tab ---
        with tab2:
            st.subheader("Test Dataset")
            st.dataframe(df_test)
        
    # --- EDA & Feature Engineering Tab ---
    if sidebar_option == "📊 EDA & Feature Engineering":
        st.header("📊 EDA & Feature Engineering")
        
        main_tabs = st.tabs(["Column-wise Analysis", "Area-wise Analysis"])
        
        # =========================
        # 1️⃣ Column-wise Analysis
        # =========================
        with main_tabs[0]:
            sub_tab1, sub_tab2 = st.tabs(["Distribution", "Metrics"])
            
            # --- Distribution Tab ---
            with sub_tab1:
                st.subheader("Categorical Columns Distribution")
                
                # Original list of categorical columns
                cat_cols = ['rooms_en','floor_bin','swimming_pool','balcony','elevator', 
                            'metro','has_parking','area_name_en','property_sub_type_en']
                
                # Filter columns that exist in df_train
                cat_cols_existing = [col for col in cat_cols if col in df_train.columns]
                
                if not cat_cols_existing:
                    st.warning("No categorical columns found in the dataset.")
                else:
                    for col in cat_cols_existing:
                        chart_df = df_train.groupby(col).agg(
                            nRecords=('meter_sale_price','count'),
                            Avg_Meter_Sale_Price=('meter_sale_price','mean')
                        ).reset_index()
                        
                        fig = px.bar(chart_df, x=col, y='nRecords', color=col,
                                     title=f"{col} Distribution vs Avg Meter Sale Price")
                        fig.add_scatter(x=chart_df[col], y=chart_df['Avg_Meter_Sale_Price'],
                                        mode='lines+markers', name='Avg Meter Sale Price', yaxis='y2')
                        fig.update_layout(
                            yaxis2=dict(title='Avg Meter Sale Price', overlaying='y', side='right')
                        )
                        st.plotly_chart(fig, use_container_width=True)
            
            # --- Metrics Tab ---
            with sub_tab2:
                st.subheader("Metrics on meter_sale_price & procedure_area")
                
                numeric_cols = ['meter_sale_price', 'procedure_area']
                numeric_cols_existing = [col for col in numeric_cols if col in df_train.columns]
                
                if not numeric_cols_existing:
                    st.warning("No numeric columns found in the dataset.")
                else:
                    # Plot histogram + boxplot for each numeric column
                    for col in numeric_cols_existing:
                        st.markdown(f"### {col} Distribution")
                        fig_hist = px.histogram(df_train, x=col, nbins=50, marginal="box",
                                                title=f"{col} Distribution with Boxplot")
                        st.plotly_chart(fig_hist, use_container_width=True)
                    
                    # Show descriptive statistics once
                    st.dataframe(df_train[numeric_cols_existing].describe().round(2))
        
        # =========================
        # 2️⃣ Area-wise Analysis
        # =========================
        with main_tabs[1]:
            st.subheader("Area-wise Analysis")
            
            if 'area_name_en' not in df_train.columns:
                st.warning("'area_name_en' column not found in dataset.")
            else:
                areas = df_train['area_name_en'].unique().tolist()
                # Add a unique key to avoid duplication
                selected_area = st.selectbox("Select Area", areas, key="select_area_area_wise")
                df_area = df_train[df_train['area_name_en'] == selected_area]
                
                area_tabs = st.tabs(["Dimensions", "Metrics", "Categorical Distributions"])
                
                # --- Dimensions Tab ---
                with area_tabs[0]:
                    st.subheader(f"Dimensions for {selected_area}")
                    st.dataframe(df_area.describe(include='all').transpose())
                
                # --- Metrics Tab ---
                with area_tabs[1]:
                    st.subheader(f"Metrics on meter_sale_price & procedure_area for {selected_area}")
                    
                    numeric_cols = ['meter_sale_price', 'procedure_area']
                    numeric_cols_existing = [col for col in numeric_cols if col in df_area.columns]
                    
                    if not numeric_cols_existing:
                        st.warning("No numeric columns found in the area dataset.")
                    else:
                        for col in numeric_cols_existing:
                            st.markdown(f"### {col} Distribution for {selected_area}")
                            fig_area = px.histogram(df_area, x=col, nbins=50, marginal="box",
                                                    title=f"{col} Distribution with Boxplot for {selected_area}")
                            st.plotly_chart(fig_area, use_container_width=True)
                        
                        st.dataframe(df_area[numeric_cols_existing].describe().round(2))
                
                # --- Categorical Distributions Tab ---
                with area_tabs[2]:
                    st.subheader(f"Categorical Column Distributions for {selected_area}")
                    
                    cat_cols = ['rooms_en','floor_bin','swimming_pool','balcony','elevator', 
                                'metro','has_parking','property_sub_type_en']
                    cat_cols_existing = [col for col in cat_cols if col in df_area.columns]
                    
                    if not cat_cols_existing:
                        st.warning("No categorical columns found for this area.")
                    else:
                        for col in cat_cols_existing:
                            chart_df = df_area.groupby(col).agg(
                                nRecords=('meter_sale_price','count'),
                                Avg_Meter_Sale_Price=('meter_sale_price','mean')
                            ).reset_index()
                            
                            fig = px.bar(chart_df, x=col, y='nRecords', color=col,
                                         title=f"{col} Distribution vs Avg Meter Sale Price for {selected_area}")
                            fig.add_scatter(x=chart_df[col], y=chart_df['Avg_Meter_Sale_Price'],
                                            mode='lines+markers', name='Avg Meter Sale Price', yaxis='y2')
                            fig.update_layout(
                                yaxis2=dict(title='Avg Meter Sale Price', overlaying='y', side='right')
                            )
                            # Use a unique key per plot
                            st.plotly_chart(fig, use_container_width=True, key=f"{col}_{selected_area}")
import streamlit as st
import pandas as pd
import numpy as np
import pickle
import glob
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
if sidebar_option == "📈 Model Results":
    # =========================
    # 0️⃣ IMPORT REQUIRED LIBRARIES
    # =========================
    from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
    import numpy as np
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import plotly.express as px
    
    # =========================
    # 1️⃣ LOAD ONEHOT ENCODER
    # =========================
    try:
        with open("onehot_encoder.pkl", "rb") as f:
            ohe = pickle.load(f)
    except FileNotFoundError:
        st.error("❌ OneHot encoder file 'onehot_encoder.pkl' not found")
        st.stop()
    
    # =========================
    # 2️⃣ LOAD AREA-WISE MODELS
    # =========================
    area_models = {}
    area_files = [
        "dt_model_Al_Barsha_South_Fifth.pkl",
        "dt_model_Al_Barsha_South_Fourth.pkl",
        "dt_model_Al_Barshaa_South_Third.pkl",
        "dt_model_Al_Hebiah_Fourth.pkl",
        "dt_model_Al_Khairan_First.pkl",
        "dt_model_Al_Merkadh.pkl",
        "dt_model_Al_Thanyah_Fifth.pkl",
        "dt_model_Al_Warsan_First.pkl",
        "dt_model_Al_Yelayiss_2.pkl",
        "dt_model_Bukadra.pkl",
        "dt_model_Burj_Khalifa.pkl",
        "dt_model_Business_Bay.pkl",
        "dt_model_Hadaeq_Sheikh_Mohammed_Bin_Rashid.pkl",
        "dt_model_Jabal_Ali_First.pkl",
        "dt_model_Madinat_Al_Mataar.pkl",
        "dt_model_Madinat_Dubai_Almelaheyah.pkl",
        "dt_model_Marsa_Dubai.pkl",
        "dt_model_Me'Aisem_First.pkl",
        "dt_model_Nadd_Hessa.pkl",
        "dt_model_Wadi_Al_Safa_5.pkl"
    ]
    
    successful_models = 0
    for model_file in area_files:
        try:
            area_name = model_file.split("dt_model_")[1].replace(".pkl", "").replace("_", " ")
            with open(model_file, "rb") as f:
                area_models[area_name] = pickle.load(f)
            successful_models += 1
            st.sidebar.success(f"✅ {area_name}")
        except FileNotFoundError:
            st.sidebar.warning(f"⚠️ {model_file} not found")
        except Exception as e:
            st.sidebar.error(f"❌ {model_file}: {str(e)}")
    
    if successful_models == 0:
        st.error("❌ No models were successfully loaded. Please check your model files.")
        st.stop()
    
    # =========================
    # 3️⃣ STREAMLIT UI
    # =========================
    st.title("🏠 Dubai Real Estate Price Predictor")
    st.write(f"Loaded {successful_models} area-wise models")
    
    # =========================
    # 4️⃣ LOAD AND PREPARE TEST DATA
    # =========================
    try:
        test_samples = pd.read_csv("test_data_20 areas_1.csv")
        
        # Remove unwanted columns including Unnamed: 0 and index-like columns
        columns_to_drop = ['Unnamed: 0', 'instance_date', 'quarter', 'Year']
        test_samples = test_samples.drop(columns=[col for col in columns_to_drop if col in test_samples.columns], errors='ignore')
        
        st.subheader("📊 Test Data Preview")
        st.dataframe(test_samples.head(), use_container_width=True)
        st.write(f"Dataset shape: {test_samples.shape}")
        
        # =========================
        # 5️⃣ PREPARE TEST DATA FOR PREDICTION
        # =========================
        # Identify target column and features
        target_col = 'meter_sale_price'
        if target_col not in test_samples.columns:
            st.error(f"❌ Target column '{target_col}' not found in test data")
            st.stop()
        
        # Separate features and target
        X_test = test_samples.drop(columns=[target_col, 'area_name_en'], errors='ignore')
        y_test = test_samples[target_col]
        
        # Clean feature names - remove any index-like columns
        index_like_cols = [col for col in X_test.columns if 'unnamed' in col.lower() or col.lower() in ['index', 'level_0']]
        if index_like_cols:
            st.warning(f"⚠️ Removing index-like columns: {index_like_cols}")
            X_test = X_test.drop(columns=index_like_cols, errors='ignore')
        
        # Identify categorical columns
        cat_cols = X_test.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Apply OneHot Encoding
        if cat_cols:
            try:
                X_cat_test = ohe.transform(X_test[cat_cols])
                X_cat_test = pd.DataFrame(X_cat_test, columns=ohe.get_feature_names_out(cat_cols), index=X_test.index)
                X_test = X_test.drop(columns=cat_cols)
                X_test = pd.concat([X_test, X_cat_test], axis=1)
                st.success(f"✅ Applied OneHot encoding to {len(cat_cols)} categorical columns")
            except Exception as e:
                st.error(f"❌ Error in OneHot encoding: {str(e)}")
                st.stop()
        
        # Ensure all columns are numeric
        for col in X_test.columns:
            if X_test[col].dtype == 'object':
                try:
                    X_test[col] = pd.to_numeric(X_test[col], errors='coerce')
                except:
                    X_test = X_test.drop(columns=[col], errors='ignore')
        
        # Handle missing values
        if X_test.isnull().sum().sum() > 0:
            st.warning("⚠️ Missing values detected. Filling with 0.")
            X_test = X_test.fillna(0)
        
        st.success(f"✅ Prepared test data with {X_test.shape[1]} features")
        
        # =========================
        # 6️⃣ CREATE TABS FOR DIFFERENT FUNCTIONALITIES
        # =========================
        pred_tab, forecast_tab = st.tabs(["📊 Predictions", "🔮 Forecasting"])
        
        with pred_tab:
            st.subheader("Model Predictions & Performance")
            
            if st.button("🚀 Run Predictions", type="primary", key="predict_btn"):
                with st.spinner("Running predictions..."):
                    y_pred_total = pd.Series(index=test_samples.index, dtype=float)
                    test_metrics = {}
                    areas_processed = 0
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    areas = test_samples['area_name_en'].unique()
                    
                    for i, area in enumerate(areas):
                        status_text.text(f"Processing {area}... ({i+1}/{len(areas)})")
                        progress_bar.progress((i + 1) / len(areas))
                        
                        if area not in area_models:
                            st.warning(f"⚠️ Skipping area '{area}' (model not available)")
                            continue
                        
                        model = area_models[area]
                        mask = test_samples['area_name_en'] == area
                        X_area_test = X_test.loc[mask]
                        y_area_test = y_test.loc[mask]
                        
                        if len(X_area_test) > 0:
                            try:
                                # Align features with model expectations
                                model_features = model.feature_names_in_ if hasattr(model, 'feature_names_in_') else None
                                if model_features is not None:
                                    # Ensure feature alignment
                                    missing_features = set(model_features) - set(X_area_test.columns)
                                    extra_features = set(X_area_test.columns) - set(model_features)
                                    
                                    if missing_features:
                                        st.warning(f"Area {area}: Adding missing features: {list(missing_features)}")
                                        for feature in missing_features:
                                            X_area_test[feature] = 0
                                    
                                    if extra_features:
                                        st.warning(f"Area {area}: Removing extra features: {list(extra_features)}")
                                        X_area_test = X_area_test[model_features]
                                
                                y_pred = model.predict(X_area_test)
                                y_pred_total.loc[mask] = y_pred
                                
                                # Calculate metrics
                                r2 = r2_score(y_area_test, y_pred)
                                rmse = np.sqrt(mean_squared_error(y_area_test, y_pred))
                                mae = mean_absolute_error(y_area_test, y_pred)
                                
                                test_metrics[area] = {
                                    'R2': round(r2, 4), 
                                    'RMSE': round(rmse, 2), 
                                    'MAE': round(mae, 2),
                                    'Samples': len(y_area_test),
                                    'Avg_Actual_Price': round(y_area_test.mean(), 2),
                                    'Avg_Predicted_Price': round(y_pred.mean(), 2)
                                }
                                areas_processed += 1
                                
                            except Exception as e:
                                st.error(f"❌ Error predicting for {area}: {str(e)}")
                                continue
                    
                    progress_bar.empty()
                    status_text.text("✅ Prediction completed!")
                    
                    # Display results
                    if test_metrics:
                        st.subheader("📈 Prediction Results")
                        
                        test_metrics_df = pd.DataFrame(test_metrics).T
                        test_metrics_df = test_metrics_df.sort_values(by='R2', ascending=False)
                        
                        # Display metrics table
                        st.dataframe(test_metrics_df.style.format({
                            'R2': '{:.4f}',
                            'RMSE': '{:.2f}',
                            'MAE': '{:.2f}',
                            'Avg_Actual_Price': '{:,.2f}',
                            'Avg_Predicted_Price': '{:,.2f}'
                        }), use_container_width=True)
                        
                        # Summary statistics
                        st.subheader("📊 Summary Statistics")
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Areas Processed", areas_processed)
                        with col2:
                            avg_r2 = test_metrics_df['R2'].mean()
                            st.metric("Average R²", f"{avg_r2:.4f}")
                        with col3:
                            total_samples = test_metrics_df['Samples'].sum()
                            st.metric("Total Samples", total_samples)
                        with col4:
                            avg_rmse = test_metrics_df['RMSE'].mean()
                            st.metric("Average RMSE", f"{avg_rmse:.2f}")
                        
                        # Download results
                        results_df = test_samples.copy()
                        results_df['predicted_price'] = y_pred_total
                        results_df['prediction_error'] = results_df['meter_sale_price'] - results_df['predicted_price']
                        results_df['error_percentage'] = (results_df['prediction_error'] / results_df['meter_sale_price'] * 100).round(2)
                        
                        csv = results_df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Predictions CSV",
                            data=csv,
                            file_name="dubai_real_estate_predictions.csv",
                            mime="text/csv"
                        )
                    else:
                        st.warning("No predictions were successfully completed.")
        
        with forecast_tab:
            st.subheader("Price Forecasting")
            st.info("Forecasting functionality will be available after successful predictions")
            
            # Simple forecasting interface
            if st.button("Initialize Forecasting", key="forecast_init"):
                st.success("Forecasting module ready. Run predictions first for best results.")
                
    except FileNotFoundError:
        st.error("❌ Test data file 'test_data_20 areas_1.csv' not found.")
        st.info("Please make sure the file exists in the same directory as this script.")
    except Exception as e:
        st.error(f"❌ Error loading or processing test data: {str(e)}")
        st.info("Please check your test data file format and content.")
    
    # =========================
    # 7️⃣ SIDEBAR INFORMATION
    # =========================
    st.sidebar.title("ℹ️ Model Information")
    st.sidebar.write(f"**Successful Models:** {successful_models}")
    st.sidebar.write(f"**Test Data Samples:** {len(test_samples) if 'test_samples' in locals() else 'N/A'}")
    st.sidebar.write(f"**Features:** {X_test.shape[1] if 'X_test' in locals() else 'N/A'}")
    
    st.sidebar.markdown("""
    **Metrics Guide:**
    - **R² Score**: 1.0 = perfect, 0.0 = baseline
    - **RMSE**: Lower = better (price units)
    - **MAE**: Lower = better (price units)
    """)
        
            

        
