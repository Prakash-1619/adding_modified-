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
    test_file_path = "test_data_20 areas_1.csv"  # Replace with your CSV path
    
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
        
        main_tabs = st.tabs(["Price_trend_areawise","Column-wise Analysis", "Area-wise Analysis"])
        
        # =========================
        # 1️⃣ Column-wise Analysis
        # =========================
        with main_tabs[0]:
            import streamlit as st
            import pandas as pd
            import plotly.express as px
            import os
            
            def create_time_series_plot(df, time_period):
                """
                Create a time series plot based on selected time period
                """
                df = df.copy()
                df['instance_date'] = pd.to_datetime(df['instance_date'])
                
                if time_period == 'Monthly':
                    df['time_period'] = df['instance_date'].dt.strftime('%b %Y')
                    df['sort_key'] = df['instance_date'].dt.to_period('M')
                    title_suffix = 'Month'
                
                elif time_period == 'Quarterly':
                    df['time_period'] = 'Q' + df['instance_date'].dt.quarter.astype(str) + ' ' + df['instance_date'].dt.year.astype(str)
                    df['sort_key'] = df['instance_date'].dt.to_period('Q')
                    title_suffix = 'Quarter'
                
                elif time_period == 'Half-Yearly':
                    # Create half-year periods (H1: Jan-Jun, H2: Jul-Dec)
                    df['half_year'] = ((df['instance_date'].dt.month - 1) // 6) + 1
                    df['time_period'] = 'H' + df['half_year'].astype(str) + ' ' + df['instance_date'].dt.year.astype(str)
                    df['sort_key'] = df['instance_date'].dt.year.astype(str) + '-' + df['half_year'].astype(str)
                    title_suffix = 'Half-Year'
                
                # Group by time period and area
                period_avg = df.groupby(['time_period', 'sort_key', 'area_name_en'])['meter_sale_price'].mean().reset_index()
                period_avg = period_avg.sort_values('sort_key')
                
                return period_avg, title_suffix
            
            def main():
                #st.set_page_config(page_title="Real Estate Analytics", page_icon="🏠", layout="wide")
                
                #st.title("🏠 Real Estate Price Analytics")
                st.markdown("Analyze average meter sale prices across different time periods")
                
                # File path input
                file_path =  "df_trained_dataset_6000.csv"
                
                if os.path.exists(file_path):
                    try:
                        df = pd.read_csv(file_path)
                        #st.success(f"✅ File loaded successfully: {file_path}")
                        
                        # Validate required columns
                        required_columns = ['instance_date', 'area_name_en', 'meter_sale_price']
                        missing_columns = [col for col in required_columns if col not in df.columns]
                        
                        if missing_columns:
                            st.error(f"Missing required columns: {', '.join(missing_columns)}")
                            st.info("Please make sure your CSV contains: instance_date, area_name_en, meter_sale_price")
                            
                            # Show available columns
                            st.write("Available columns in your file:")
                            st.write(list(df.columns))
                            return
                        
                        # Display basic info about the loaded data
                        st.sidebar.header("Data Overview")
                        st.sidebar.write(f"Total records: {len(df):,}")
                        st.sidebar.write(f"Date range: {df['instance_date'].min()} to {df['instance_date'].max()}")
                        st.sidebar.write(f"Areas: {df['area_name_en'].nunique()}")
                        st.sidebar.write(f"Average price: {df['meter_sale_price'].mean():.2f}")
                        
                        # Show first few rows of the data
                        st.subheader("Preview of Your Data")
                        st.dataframe(df.head(10), use_container_width=True)
                        
                        # Sidebar filters
                        st.sidebar.header("Filters")
                        
                        # Time period selection
                        time_period = st.sidebar.selectbox(
                            "Select Time Period",
                            options=['Monthly', 'Quarterly', 'Half-Yearly'],
                            index=0
                        )
                        
                        # Area filter
                        areas = df['area_name_en'].unique()
                        selected_areas = st.sidebar.multiselect(
                            "Select Areas to Display",
                            options=areas,
                            default=areas[:5] if len(areas) > 5 else areas
                        )
                        
                        if selected_areas:
                            df_filtered = df[df['area_name_en'].isin(selected_areas)]
                        else:
                            df_filtered = df.copy()
                        
                        # Date range filter
                        min_date = pd.to_datetime(df_filtered['instance_date']).min()
                        max_date = pd.to_datetime(df_filtered['instance_date']).max()
                        
                        date_range = st.sidebar.date_input(
                            "Select Date Range",
                            value=(min_date, max_date),
                            min_value=min_date,
                            max_value=max_date
                        )
                        
                        if len(date_range) == 2:
                            start_date, end_date = date_range
                            df_filtered = df_filtered[
                                (pd.to_datetime(df_filtered['instance_date']) >= pd.to_datetime(start_date)) & 
                                (pd.to_datetime(df_filtered['instance_date']) <= pd.to_datetime(end_date))
                            ]
                        
                        # Process data based on selected time period
                        processed_df, title_suffix = create_time_series_plot(df_filtered, time_period)
                        
                        # Display the plot
                        st.header(f"{time_period} Analysis")
                        
                        fig = px.line(processed_df, x='time_period', y='meter_sale_price', color='area_name_en',
                                     title=f'Average Meter Sale Price by {title_suffix} and Area',
                                     markers=True, line_shape='linear')
                        
                        fig.update_layout(
                            xaxis_title=title_suffix,
                            yaxis_title='Average Meter Sale Price',
                            legend_title='Area Name',
                            hovermode='x unified'
                        )
                        
                        fig.update_xaxes(tickangle=45)
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Display the dataframe
                        st.subheader(f"{time_period} Summary Data")
                        
                        # Create a clean dataframe for display
                        display_df = processed_df[['time_period', 'area_name_en', 'meter_sale_price']].copy()
                        display_df = display_df.rename(columns={
                            'time_period': title_suffix,
                            'area_name_en': 'Area Name',
                            'meter_sale_price': 'Average Price'
                        })
                        
                        # Pivot for better readability
                        pivot_df = display_df.pivot_table(
                            index=title_suffix,
                            columns='Area Name',
                            values='Average Price',
                            aggfunc='mean'
                        ).round(2)
                        
                        st.dataframe(pivot_df.style.background_gradient(cmap='Blues'), use_container_width=True)
                    
                    except Exception as e:
                        st.error(f"Error processing file: {str(e)}")
                
                else:
                    st.error(f"❌ File not found: {file_path}")
                    st.info("""
                    **How to use:**
                    1. Make sure your CSV file is in the same directory as this script
                    2. Enter the filename (e.g., 'data.csv') or full path
                    3. Your CSV should have these columns: instance_date, area_name_en, meter_sale_price
                    
                    **Example file structure:**
                    """)
                    
                    # Display sample data structure
                    sample_data = {
                        'instance_date': ['2023-01-15', '2023-01-20', '2023-02-10', '2023-02-25', '2023-03-15'],
                        'area_name_en': ['Downtown', 'Suburb', 'Downtown', 'Suburb', 'Downtown'],
                        'meter_sale_price': [5000, 4500, 5200, 4600, 5300]
                    }
                    sample_df = pd.DataFrame(sample_data)
                    #st.dataframe(sample_df, use_container_width=True)
            
            if __name__ == "__main__":
                main()
        with main_tabs[1]:
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
        with main_tabs[2]:
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

import pandas as pd
import numpy as np
import pickle
import glob
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
if sidebar_option == "📈 Model Results":
    import streamlit as st
    import pandas as pd
    import numpy as np
    import pickle
    import glob
    import os
    import plotly.express as px
    import plotly.graph_objects as go
    from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
    
    # =========================
    # HEADER
    # =========================
    st.set_page_config(page_title="Area Price Forecast Dashboard", layout="wide")
    st.title("🏢 Area-wise Real Estate Forecast Dashboard")
    st.markdown("### Predict, Visualize, and Validate Area-wise Prices")
    
    # =========================
    # SIDEBAR
    # =========================
    st.sidebar.header("Upload & Filters")
    
    uploaded_file = st.sidebar.file_uploader("Upload Test CSV", type=["csv"])
    selected_areas = st.sidebar.multiselect("Select Areas", [], default=[])
    
    # Optional Date filter
    start_date = st.sidebar.date_input("Start Date")
    end_date = st.sidebar.date_input("End Date")
    
    # =========================
    # LOAD ENCODER, TRAIN COLUMNS, MODELS
    # =========================
    with open("onehot_encoder.pkl", "rb") as f:
        ohe = pickle.load(f)
    
    with open("train_columns.pkl", "rb") as f:
        train_columns = pickle.load(f)
    
    # Load all models
    area_models = {}
    for f in glob.glob("dt_model_*.pkl"):
        area_name = os.path.basename(f).replace("dt_model_", "").replace(".pkl", "").replace("_", " ")
        with open(f, "rb") as file:
            area_models[area_name] = pickle.load(file)
    
    if not uploaded_file:
        st.warning("Please upload a test CSV to proceed.")
        st.stop()
    
    # Load test data
    test_samples = pd.read_csv(uploaded_file)
    
    # Apply date filter if columns exist
    if 'instance_date' in test_samples.columns:
        test_samples['instance_date'] = pd.to_datetime(test_samples['instance_date'])
        test_samples = test_samples[(test_samples['instance_date'] >= pd.to_datetime(start_date)) &
                                    (test_samples['instance_date'] <= pd.to_datetime(end_date))]
    
    # Update area choices if not manually selected
    if not selected_areas:
        selected_areas = list(area_models.keys())[:3]
    
    # =========================
    # TABS
    # =========================
    tab1, tab2, tab3 = st.tabs(["📈 Model Results", "🔮 Forecasting / Trends", "🧪 Validation"])
    
    # =========================
    # TAB 1: Model Results
    # =========================
    with tab1:
        st.subheader("Predictions & Metrics")
        area_choice = st.selectbox("Choose Area to View Predictions", selected_areas)
        model = area_models[area_choice]
    
        # Prepare test features
        X_test = test_samples.drop(columns=['meter_sale_price', 'instance_date'], errors='ignore')
        for col in train_columns:
            if col not in X_test.columns:
                X_test[col] = 0
        X_test = X_test[train_columns]
    
        predictions = model.predict(X_test)
        st.dataframe(pd.DataFrame({"Predicted Price": predictions}))
    
        # Performance Metrics
        if 'meter_sale_price' in test_samples.columns:
            y_true = test_samples['meter_sale_price']
            col1, col2, col3 = st.columns(3)
            col1.metric("R2 Score", round(r2_score(y_true, predictions), 3))
            col2.metric("MAE", round(mean_absolute_error(y_true, predictions), 2))
            col3.metric("MSE", round(mean_squared_error(y_true, predictions), 2))
    
        # Download Predictions
        result_df = test_samples.copy()
        result_df['Predicted_Price'] = predictions
        csv = result_df.to_csv(index=False).encode()
        st.download_button("Download Predictions CSV", csv, "predictions.csv", "text/csv")
    
    # =========================
    # TAB 2: Forecasting / Trends
    # =========================
    with tab2:
        st.subheader("Forecasting Trends per Area")
        fig = go.Figure()
        for area in selected_areas:
            model = area_models[area]
            preds = model.predict(X_test)
            fig.add_trace(go.Scatter(x=test_samples['instance_date'], y=preds,
                                     mode='lines+markers', name=f"{area} Forecast"))
        fig.update_layout(title="Area-wise Price Forecast",
                          xaxis_title="Date", yaxis_title="Predicted Price",
                          legend_title="Areas", hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)
    
    # =========================
    # TAB 3: Validation / Actual vs Predicted
    # =========================
    with tab3:
        st.subheader("Actual vs Predicted Comparison")
        for area in selected_areas:
            model = area_models[area]
            preds = model.predict(X_test)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=test_samples['instance_date'], y=test_samples.get('meter_sale_price', [0]*len(test_samples)),
                                     mode='lines+markers', name='Actual'))
            fig.add_trace(go.Scatter(x=test_samples['instance_date'], y=preds,
                                     mode='lines+markers', name='Predicted'))
            fig.update_layout(title=f"Actual vs Predicted - {area}",
                              xaxis_title="Date", yaxis_title="Price",
                              legend_title="Legend", hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)
    
        ###############################################################################################################################################################################################################################
        with tab3:
            import streamlit as st
            import pandas as pd
            import numpy as np
            import pickle
            import glob
            import os
            import plotly.graph_objects as go
            
            st.title("🔮 Area-wise Price Forecasting")
            
            # =========================
            # 1️⃣ Load single test dataset
            # =========================
            file_path = "test_data_2024-Q4.csv"  # <-- update your CSV path
            
            try:
                test_df = pd.read_csv(file_path)
            except Exception as e:
                st.error(f"Error loading test data: {e}")
                st.stop()
            
            drop_cols = ['Unnamed: 0', 'quarter', 'Year']
            test_df = test_df.drop(columns=[c for c in drop_cols if c in test_df.columns], errors='ignore')
            
            # =========================
            # 2️⃣ Load pickles
            # =========================
            with open("onehot_encoder.pkl", "rb") as f:
                ohe = pickle.load(f)
            
            with open("train_columns.pkl", "rb") as f:
                train_columns = pickle.load(f)
            
            # =========================
            # 3️⃣ Load area models
            # =========================
            area_model_files = glob.glob(os.path.join("area_models", "*.pkl"))
            area_models = {}
            for f in area_model_files:
                area_name = os.path.basename(f).replace("dt_model_", "").replace(".pkl", "")
                with open(f, "rb") as file:
                    area_models[area_name] = pickle.load(file)
            
            # =========================
            # 4️⃣ Get areas available in the test dataset and models
            # =========================
            areas_in_test = test_df['area_name_en'].unique().tolist()
            available_areas = [a for a in areas_in_test if a in area_models]
            
            # Sidebar: select areas dynamically
            selected_areas = st.sidebar.multiselect(
                "Select Areas",
                options=available_areas,
                default=available_areas[:2] if len(available_areas) > 2 else available_areas
            )
            
            if not selected_areas:
                st.warning("No areas available in test dataset or no model found.")
                st.stop()
            
            # =========================
            # 5️⃣ Load growth factors
            # =========================
            growth_df = pd.read_csv('quarterly_forecasts_with_CI.csv')
            growth_df = growth_df[['forecast_quarter', 'area_name_en', 'growth_factor_upper']]
            growth_pivot = growth_df.pivot(index='area_name_en', columns='forecast_quarter', values='growth_factor_upper').reset_index()
            
            # =========================
            # 6️⃣ Load historical median from training data
            # =========================
            train_data = pd.read_csv("df_trained_dataset_6000.csv")
            train_data['instance_date'] = pd.to_datetime(train_data['instance_date'])
            train_data['year_quarter'] = train_data['instance_date'].dt.year.astype(str) + '-Q' + train_data['instance_date'].dt.quarter.astype(str)
            historical_median = train_data.groupby(['area_name_en', 'year_quarter'])['meter_sale_price'].median().reset_index()
            historical_pivot = historical_median.pivot(index='area_name_en', columns='year_quarter', values='meter_sale_price').reset_index()
            
            # =========================
            # 7️⃣ Prediction + Forecast per area
            # =========================
            for area in selected_areas:
                st.subheader(f"📊 {area} - Historical + Prediction + Forecast")
            
                model = area_models.get(area)
                if model is None:
                    st.warning(f"No model found for {area}")
                    continue
            
                # Prepare test data for this area
                X_test_area = test_df[test_df['area_name_en'] == area].copy()
                if X_test_area.empty:
                    st.warning(f"No test records for {area}")
                    continue
            
                X_test_area_no_area = X_test_area.drop(columns=['area_name_en'], errors='ignore')
            
                # Apply OHE
                cat_cols = X_test_area_no_area.select_dtypes(include='object').columns.tolist()
                if cat_cols:
                    X_cat_test = ohe.transform(X_test_area_no_area[cat_cols])
                    X_cat_test = pd.DataFrame(X_cat_test, columns=ohe.get_feature_names_out(cat_cols), index=X_test_area_no_area.index)
                    X_test_area_no_area = X_test_area_no_area.drop(columns=cat_cols)
                    X_test_area = pd.concat([X_test_area_no_area, X_cat_test], axis=1)
                else:
                    X_test_area = X_test_area_no_area.copy()
            
                # Align with training columns
                for col in train_columns:
                    if col not in X_test_area.columns:
                        X_test_area[col] = 0
                X_test_area = X_test_area[train_columns].select_dtypes(include=[np.number])
            
                # Predict median
                preds = model.predict(X_test_area)
                median_pred = np.median(preds)
            
                # Forecast
                if area in growth_pivot['area_name_en'].values:
                    area_growth = growth_pivot[growth_pivot['area_name_en'] == area].iloc[0].drop('area_name_en')
                    forecast_values = median_pred * area_growth.values
                    forecast_quarters = area_growth.index.tolist()
                else:
                    forecast_values = []
                    forecast_quarters = []
            
                # Historical median
                hist_row = historical_pivot[historical_pivot['area_name_en'] == area].drop('area_name_en', axis=1)
                historical_quarters = hist_row.columns.tolist()
                historical_values = hist_row.values.flatten().tolist() if not hist_row.empty else []
            
                # Combine for table and plot
                combined_quarters = historical_quarters + ['Current'] + list(forecast_quarters)
                combined_values = historical_values + [median_pred] + list(forecast_values)
            
                df_display = pd.DataFrame({
                    'Quarter': combined_quarters,
                    'Median Price (AED)': combined_values
                })
                st.dataframe(df_display, use_container_width=True)
            
                # Plot
                fig = go.Figure()
                if historical_values:
                    fig.add_trace(go.Scatter(x=historical_quarters, y=historical_values, mode='lines+markers',
                                             name='Historical Median', line=dict(color='blue', width=3), marker=dict(size=8)))
                fig.add_trace(go.Scatter(x=['Current'], y=[median_pred], mode='markers',
                                         name='Prediction (Median)', marker=dict(color='red', size=10, symbol='diamond')))
                if forecast_values:
                    fig.add_trace(go.Scatter(x=forecast_quarters, y=forecast_values, mode='lines+markers',
                                             name='Forecast', line=dict(color='green', width=3, dash='dash'), marker=dict(size=8)))
                fig.update_layout(title=f"{area} - Historical, Prediction & Forecast",
                                  xaxis_title="Quarter", yaxis_title="Price (AED)", template="plotly_white", height=450)
                st.plotly_chart(fig, use_container_width=True)


###########################################################################################################################################################################################################################
###########################################################################################################################################################################################################################



# =========================
# 🤖 MODEL INPUT / PREDICTION SECTION
# =========================
from datetime import datetime, timedelta
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pickle
import os
from statsmodels.nonparametric.smoothers_lowess import lowess
from datetime import datetime, timedelta

# =========================
# INITIALIZATION & MODEL LOADING
# =========================
@st.cache_resource
def load_area_models():
    """Load all area-specific models"""
    area_models = {}
    area_files = [
        "dt_model_Al_Barsha_South_Fifth.pkl", "dt_model_Al_Barsha_South_Fourth.pkl", 
        "dt_model_Al_Barshaa_South_Third.pkl", "dt_model_Al_Hebiah_Fourth.pkl",
        "dt_model_Al_Khairan_First.pkl", "dt_model_Al_Merkadh.pkl", 
        "dt_model_Al_Thanyah_Fifth.pkl", "dt_model_Al_Warsan_First.pkl",
        "dt_model_Al_Yelayiss_2.pkl", "dt_model_Bukadra.pkl", 
        "dt_model_Burj_Khalifa.pkl", "dt_model_Business_Bay.pkl",
        "dt_model_Hadaeq_Sheikh_Mohammed_Bin_Rashid.pkl", "dt_model_Jabal_Ali_First.pkl",
        "dt_model_Madinat_Al_Mataar.pkl", "dt_model_Madinat_Dubai_Almelaheyah.pkl",
        "dt_model_Marsa_Dubai.pkl", "dt_model_Me'Aisem_First.pkl",
        "dt_model_Nadd_Hessa.pkl", "dt_model_Wadi_Al_Safa_5.pkl"
    ]
    
    loaded_models = {}
    missing_models = []
    
    for model_file in area_files:
        try:
            # Extract area name from filename
            area_name = model_file.replace('dt_model_', '').replace('.pkl', '').replace('_', ' ')
            
            # Load the model
            with open(model_file, 'rb') as f:
                model = pickle.load(f)
            
            loaded_models[area_name] = model
            
        except FileNotFoundError:
            missing_models.append(model_file)
        except Exception as e:
            st.sidebar.error(f"❌ Error loading {model_file}: {str(e)}")
    
    if missing_models:
        st.sidebar.warning(f"Missing models: {len(missing_models)} files")
    
    return loaded_models

# =========================
# LOAD ENCODER AND TRAIN COLUMNS
# =========================
@st.cache_resource
def load_encoder_and_columns():
    """Load the encoder and training columns"""
    try:
        with open('onehot_encoder.pkl', 'rb') as f:
            ohe = pickle.load(f)
        with open('train_columns.pkl', 'rb') as f:
            train_columns = pickle.load(f)
        return ohe, train_columns
    except Exception as e:
        st.error(f"Error loading encoder/columns: {str(e)}")
        return None, None

# =========================
# LOAD TRAINING DATA WITH SELECTED FEATURES
# =========================
@st.cache_data
def load_training_data():
    """Load training data with selected features for LOESS trend analysis"""
    try:
        # Load your training data
        train_data = pd.read_csv('df_trained_dataset_6000.csv')
        
        # Ensure we have the necessary columns for trend analysis
        required_cols = ['area_name_en', 'instance_date', 'meter_sale_price', 
                        'rooms_en', 'floor_bin', 'swimming_pool', 'balcony', 
                        'elevator', 'metro', 'has_parking', 'procedure_area']
        
        if all(col in train_data.columns for col in required_cols):
            # Convert date column to datetime and extract year
            train_data['instance_date'] = pd.to_datetime(train_data['instance_date'])
            train_data['year'] = train_data['instance_date'].dt.year
            return train_data
        else:
            missing_cols = [col for col in required_cols if col not in train_data.columns]
            st.warning(f"Training data missing columns: {missing_cols}")
            return None
    except Exception as e:
        st.warning(f"Could not load training data for trend analysis: {str(e)}")
        return None

# =========================
# LOAD FORECASTING DATA
# =========================
@st.cache_data
def load_forecasting_data():
    """Load forecasting-specific data"""
    try:
        # Load growth factors
        growth_df = pd.read_csv('arima_areas_growth_6M.csv')
        growth_df = growth_df[['ds', 'area_name_en', 'growth_factor_upper']]
        growth_pivot = growth_df.pivot(index='area_name_en', columns='ds', values='growth_factor_upper').reset_index()
        
        return growth_pivot
    except Exception as e:
        st.error(f"Error loading forecasting data: {str(e)}")
        return None

# =========================
# FILTER TRAINING DATA BY SELECTED FEATURES
# =========================
def filter_training_data_by_features(train_data, selected_features):
    """Filter training data to show only properties with similar features"""
    try:
        filtered_data = train_data.copy()
        
        # Apply filters based on selected features
        if 'rooms_en' in selected_features and selected_features['rooms_en']:
            filtered_data = filtered_data[filtered_data['rooms_en'] == selected_features['rooms_en']]
        
        if 'floor_bin' in selected_features and selected_features['floor_bin']:
            filtered_data = filtered_data[filtered_data['floor_bin'] == selected_features['floor_bin']]
        
        # Filter binary features
        binary_features = ['swimming_pool', 'balcony', 'elevator', 'metro', 'has_parking']
        for feature in binary_features:
            if feature in selected_features and selected_features[feature] is not None:
                filtered_data = filtered_data[filtered_data[feature] == selected_features[feature]]
        
        # Filter area within a reasonable range (±20%)
        if 'procedure_area' in selected_features and selected_features['procedure_area']:
            area_value = selected_features['procedure_area']
            lower_bound = area_value * 0.8
            upper_bound = area_value * 1.2
            filtered_data = filtered_data[
                (filtered_data['procedure_area'] >= lower_bound) & 
                (filtered_data['procedure_area'] <= upper_bound)
            ]
        
        return filtered_data
        
    except Exception as e:
        st.warning(f"Error filtering training data: {str(e)}")
        return train_data  # Return original data if filtering fails

# =========================
# LOESS TREND ANALYSIS FUNCTION
# =========================
def calculate_loess_trend(filtered_data, area_name, current_year):
    """Calculate LOESS trend for filtered data of specific area and features"""
    try:
        # Filter data for the specific area
        area_data = filtered_data[filtered_data['area_name_en'] == area_name].copy()
        
        if len(area_data) < 2:  # Need at least 2 data points for trend
            return None, None, None
        
        # Group by year and calculate median price (more robust than mean)
        yearly_avg = area_data.groupby('year')['meter_sale_price'].median().reset_index()
        
        if len(yearly_avg) < 2:
            return None, None, None
        
        # Apply LOESS smoothing
        y_values = yearly_avg['meter_sale_price'].values
        x_values = yearly_avg['year'].values
        
        loess_smoothed = lowess(y_values, x_values, frac=0.8, it=3)
        
        # Create trend DataFrame
        trend_df = pd.DataFrame({
            'year': loess_smoothed[:, 0],
            'smoothed_price': loess_smoothed[:, 1]
        })
        
        # Calculate latest trend
        if len(trend_df) >= 2:
            trend_df = trend_df.sort_values('year')
            latest_trend = trend_df.iloc[-1]['smoothed_price']
            return trend_df, latest_trend, yearly_avg
        else:
            return trend_df, None, yearly_avg
            
    except Exception as e:
        st.warning(f"Could not calculate LOESS trend for {area_name}: {str(e)}")
        return None, None, None

# =========================
# CREATE COMBINED TREND AND FORECAST PLOT
# =========================
def create_combined_trend_forecast_plot(historical_data, trend_data, current_price, forecast_data, area_name):
    """Create a combined plot showing historical trend and future forecast"""
    
    fig = go.Figure()
    current_year = datetime.now().year
    
    # Add historical data points (filtered by features)
    if historical_data is not None and len(historical_data) > 0:
        fig.add_trace(go.Scatter(
            x=historical_data['year'],
            y=historical_data['meter_sale_price'],
            mode='markers',
            name='Historical Properties (Similar Features)',
            marker=dict(color='blue', size=6, opacity=0.6),
            hovertemplate='Year: %{x}<br>Price: AED %{y:,.0f}<extra></extra>'
        ))
    
    # Add LOESS trend line
    if trend_data is not None and len(trend_data) > 0:
        fig.add_trace(go.Scatter(
            x=trend_data['year'],
            y=trend_data['smoothed_price'],
            mode='lines',
            name='Historical Trend (LOESS)',
            line=dict(color='red', width=3),
            hovertemplate='Year: %{x}<br>Trend Price: AED %{y:,.0f}<extra></extra>'
        ))
    
    # Add current prediction point
    fig.add_trace(go.Scatter(
        x=[current_year],
        y=[current_price],
        mode='markers',
        name='Current Prediction',
        marker=dict(color='green', size=12, symbol='star'),
        hovertemplate='Current Prediction<br>Price: AED %{y:,.0f}<extra></extra>'
    ))
    
    # Add forecast data (prediction × growth factor)
    if forecast_data is not None and len(forecast_data) > 0:
        forecast_years = []
        forecast_prices = []
        
        for i, (period, growth_factor) in enumerate(forecast_data.items()):
            forecast_year = current_year + (i + 1) * 0.25  # Quarterly increments
            forecast_price = current_price * growth_factor
            forecast_years.append(forecast_year)
            forecast_prices.append(forecast_price)
        
        fig.add_trace(go.Scatter(
            x=forecast_years,
            y=forecast_prices,
            mode='lines+markers',
            name='Future Forecast (Prediction × Growth Factor)',
            line=dict(color='orange', width=3, dash='dash'),
            marker=dict(color='orange', size=8),
            hovertemplate='Year: %{x:.2f}<br>Forecast: AED %{y:,.0f}<extra></extra>'
        ))
    
    # Update layout
    fig.update_layout(
        title=f"Price Timeline - {area_name} (Similar Features)",
        xaxis_title="Year",
        yaxis_title="Price (AED)",
        height=500,
        template="plotly_white",
        hovermode='closest',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig


# =========================
# MAIN APP
# =========================

# Load models and data
with st.spinner("Loading models and data..."):
    area_models = load_area_models()
    ohe, train_columns = load_encoder_and_columns()
    train_data = load_training_data()
    growth_pivot = load_forecasting_data()

# Check if essential components are loaded
if not area_models:
    st.error("❌ No area models were loaded. Please check your model files.")
    st.stop()

if ohe is None or train_columns is None:
    st.error("❌ Encoder or training columns not loaded properly.")
    st.stop()

# =========================
# 🤖 MODEL INPUT / PREDICTION SECTION
# =========================
if sidebar_option == "🤖 Model Input / Prediction":
    st.header("🤖 Property Price Prediction")
    st.markdown("Predict property prices for specific area and features")
    
    # =========================
    # USER INPUT FORM
    # =========================
    st.sidebar.subheader("🏠 Property Features")
    
    # Get available areas from the loaded models
    available_areas = list(area_models.keys())
    
    # Area selection
    selected_area = st.sidebar.selectbox(
        "Select Area",
        options=available_areas,
        key="selected_area"
    )
    
    # Property features input
    st.sidebar.subheader("Property Features")
    
    rooms_options = ['1 B/R', 'Studio', '2 B/R', '3 B/R', 'PENTHOUSE', 'More than 3B/R']
    floor_bin_options = ['1-10', '11-20', '41-50', '21-30', 'Below 1st floor', '31-40',
                       '51-60', 'Other', '-9-0', '61-70', 'Top floor', '91-100', '81-90',
                       '71-80', 'Duplex']
    
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        rooms_en = st.selectbox("Number of Rooms", options=rooms_options, index=2)
        floor_bin = st.selectbox("Floor Level", options=floor_bin_options, index=1)
        swimming_pool = st.selectbox("Swimming Pool", options=[0, 1], format_func=lambda x: "Yes" if x == 1 else "No")
        balcony = st.selectbox("Balcony", options=[0, 1], format_func=lambda x: "Yes" if x == 1 else "No")
    
    with col2:
        elevator = st.selectbox("Elevator", options=[0, 1], format_func=lambda x: "Yes" if x == 1 else "No")
        metro = st.selectbox("Near Metro", options=[0, 1], format_func=lambda x: "Yes" if x == 1 else "No")
        has_parking = st.selectbox("Parking", options=[0, 1], format_func=lambda x: "Yes" if x == 1 else "No")
        procedure_area = st.number_input("Area (sqMt)", min_value=2, max_value=350, value=120, step=1)
    
    # =========================
    # PREPARE INPUT DATA FUNCTION
    # =========================
    def prepare_input_data(area, rooms, floor, pool, balcony_val, elevator_val, metro_val, parking, area_size):
        """Prepare user input for prediction"""
        
        input_data = pd.DataFrame({
            'rooms_en': [rooms],
            'floor_bin': [floor],
            'swimming_pool': [pool],
            'balcony': [balcony_val],
            'elevator': [elevator_val],
            'metro': [metro_val],
            'has_parking': [parking],
            'area_name_en': [area],
            'procedure_area': [area_size]
        })
        
        # Separate area name for later use
        area_name = input_data['area_name_en'].iloc[0]
        input_no_area = input_data.drop(columns=['area_name_en'])
        
        # Apply one-hot encoding to categorical columns
        cat_cols = ['rooms_en', 'floor_bin']
        
        try:
            # Transform using the fitted OHE
            X_cat = ohe.transform(input_no_area[cat_cols])
            X_cat_df = pd.DataFrame(X_cat, columns=ohe.get_feature_names_out(cat_cols))
            
            # Combine with numerical features
            X_numerical = input_no_area.drop(columns=cat_cols)
            X_processed = pd.concat([X_numerical, X_cat_df], axis=1)
            
        except Exception as e:
            st.error(f"Error in encoding: {str(e)}")
            return None, None, None
        
        # Ensure we have all training columns
        for col in train_columns:
            if col not in X_processed.columns:
                X_processed[col] = 0
        
        # Select only the columns that were used during training
        X_processed = X_processed[train_columns]
        X_processed = X_processed.select_dtypes(include=[np.number])
        
        return X_processed, area_name, input_data

    # =========================
    # PREDICTION EXECUTION
    # =========================
    if st.sidebar.button("🚀 Predict Price", type="primary", key="predict_button"):
        with st.spinner("Generating prediction..."):
            # Prepare input data
            X_input, area_name, original_input = prepare_input_data(
                selected_area, rooms_en, floor_bin, swimming_pool, balcony, 
                elevator, metro, has_parking, procedure_area
            )
            
            if X_input is None:
                st.error("❌ Failed to prepare input data")
                st.stop()
            
            if area_name in area_models:
                model = area_models[area_name]
                
                try:
                    # Make prediction
                    predicted_price = model.predict(X_input)[0]
                    
                    # =========================
                    # FILTER TRAINING DATA BY SELECTED FEATURES
                    # =========================
                    selected_features = {
                        'rooms_en': rooms_en,
                        'floor_bin': floor_bin,
                        'swimming_pool': swimming_pool,
                        'balcony': balcony,
                        'elevator': elevator,
                        'metro': metro,
                        'has_parking': has_parking,
                        'procedure_area': procedure_area
                    }
                    
                    filtered_data = None
                    if train_data is not None:
                        filtered_data = filter_training_data_by_features(train_data, selected_features)
                        
                        st.subheader("📊 Filtered Historical Data")
                        st.write(f"Found {len(filtered_data)} historical properties with similar features in {area_name}")
                        
                        if len(filtered_data) > 0:
                            st.dataframe(filtered_data[['instance_date', 'meter_sale_price', 'rooms_en', 'floor_bin', 'procedure_area']].head(10))
                    
                    # =========================
                    # CALCULATE LOESS TREND ON FILTERED DATA
                    # =========================
                    current_year = datetime.now().year
                    trend_df = None
                    historical_avg = None
                    
                    if filtered_data is not None and len(filtered_data) > 0:
                        trend_df, latest_trend, historical_avg = calculate_loess_trend(
                            filtered_data, area_name, current_year
                        )
                    
                    # =========================
                    # PREPARE FORECAST DATA (Prediction × Growth Factor)
                    # =========================
                    forecast_data = {}
                    if growth_pivot is not None:
                        area_growth = growth_pivot[growth_pivot['area_name_en'] == area_name]
                        
                        if not area_growth.empty:
                            # Get growth factor columns (excluding area name)
                            growth_columns = [col for col in growth_pivot.columns if col != 'area_name_en']
                            
                            for quarter_col in growth_columns:
                                if quarter_col in area_growth.columns:
                                    growth_factor = area_growth[quarter_col].iloc[0]
                                    forecast_data[quarter_col] = growth_factor
                    
                    # =========================
                    # CREATE COMBINED PLOT
                    # =========================
                    st.subheader("📈 Price Timeline: Historical Trend + Forecast")
                    
                    combined_fig = create_combined_trend_forecast_plot(
                        historical_avg, 
                        trend_df, 
                        predicted_price, 
                        forecast_data, 
                        area_name
                    )
                    
                    st.plotly_chart(combined_fig, use_container_width=True)
                    
                    # =========================
                    # DISPLAY PREDICTION RESULTS
                    # =========================
                    st.success("✅ Prediction Generated!")
                    
                    # Display input summary
                    st.subheader("📋 Selected Property Features")
                    input_display = original_input.copy()
                    input_display = input_display.T.reset_index()
                    input_display.columns = ['Feature', 'Value']
                    
                    feature_display_map = {
                        'rooms_en': 'Number of Rooms',
                        'floor_bin': 'Floor Level',
                        'swimming_pool': 'Swimming Pool',
                        'balcony': 'Balcony',
                        'elevator': 'Elevator',
                        'metro': 'Near Metro',
                        'has_parking': 'Parking',
                        'area_name_en': 'Area',
                        'procedure_area': 'Area (SqMt)'
                    }
                    
                    input_display['Feature'] = input_display['Feature'].map(feature_display_map)
                    input_display['Value'] = input_display['Value'].apply(
                        lambda x: "Yes" if x == 1 else "No" if x == 0 else x
                    )
                    
                    st.table(input_display)
                    
                    # Display prediction
                    st.subheader("💰 Current Price Prediction")
                    st.metric(
                        label="Predicted Property Price",
                        value=f"AED {predicted_price:,.0f}",
                    )
                    
                    # =========================
                    # DISPLAY FORECAST TABLE
                    # =========================
                    if forecast_data:
                        st.subheader("🔮 Future Price Forecast")
                        st.write("Future prices calculated as: Prediction × Growth Factor")
                        
                        forecast_table_data = []
                        cumulative_price = predicted_price
                        
                        for period, growth_factor in forecast_data.items():
                            cumulative_price = cumulative_price * growth_factor
                            forecast_table_data.append({
                                'Period': period,
                                'Growth Factor': f"{growth_factor:.4f}",
                                'Forecasted Price': f"AED {cumulative_price:,.0f}"
                            })
                        
                        forecast_df = pd.DataFrame(forecast_table_data)
                        st.table(forecast_df)
                    
                    # =========================
                    # DISPLAY TREND ANALYSIS
                    # =========================
                    if trend_df is not None and latest_trend is not None:
                        st.subheader("📊 Trend Analysis")
                        st.info(f"Based on {len(filtered_data)} similar properties in {area_name}, " 
                               f"the historical trend shows properties with these features have "
                               f"been trending around AED {latest_trend:,.0f}")
                    
                except Exception as e:
                    st.error(f"❌ Prediction error: {str(e)}")
                
            else:
                st.error(f"❌ No model found for area: {area_name}")
    
    else:
        st.info("👆 Enter property features in the sidebar and click 'Predict Price' to generate forecasts")

# =========================
# DEBUG INFORMATION
# =========================
if st.sidebar.checkbox("Show Debug Info"):
    st.sidebar.subheader("Debug Information")
    st.sidebar.write(f"Models loaded: {len(area_models)}")
    st.sidebar.write(f"Available areas: {list(area_models.keys())}")
    st.sidebar.write(f"OHE loaded: {ohe is not None}")
    st.sidebar.write(f"Train columns: {len(train_columns) if train_columns else 0}")
    st.sidebar.write(f"Training data loaded: {train_data is not None}")
