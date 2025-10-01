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
        "validation",
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
            #st.sidebar.success("✅ OneHot Encoder loaded")
        except Exception as e:
            st.error(f"❌ Error loading OneHot encoder: {e}")
            st.stop()
        file_options = {
            "Test_data": "test_data_20 areas_1.csv",
            "Test_data_sample_50": "all_values_area_data_test.csv" , # change this to your second file path
            "all_data_sample_50": "all_values_area_data.csv"}
        
        # Create selectbox
        selected_file_label = st.selectbox("Choose data file to load:",options=list(file_options.keys()))
        file_path = file_options[selected_file_label]
        # =========================
        # 2️⃣ LOAD AREA-WISE MODELS
        # =========================
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
        
        for model_file in area_files:
            try:
                area_name = model_file.split("dt_model_")[1].replace(".pkl", "").replace("_", " ")
                with open(model_file, "rb") as f:
                    area_models[area_name] = pickle.load(f)
                #st.sidebar.success(f"✅ {area_name}")
            except FileNotFoundError:
                st.sidebar.warning(f"⚠️ {model_file} not found")
            except Exception as e:
                st.sidebar.error(f"❌ {model_file}: {str(e)}")
        
        # =========================
        # 3️⃣ STREAMLIT UI
        # =========================
        #st.title("🏠 Dubai Real Estate Price Predictor")
        #st.write("Area-wise model performance analysis")
        
        # Create tabs for different functionalities
        tab1, tab2,tab3 = st.tabs(["📊 Predictions & Analysis","🔮 Forecasting_year_trends","validation"])
        
        with tab1:
            st.header("📊 Model Predictions & Performance Analysis")
            import pandas as pd
            
            # =========================
            # 4️⃣ LOAD AND PREPARE TEST DATA FOR PREDICTIONS TAB
            # =========================
            try:
                test_samples = pd.read_csv(file_path)
                test_samples = test_samples.drop(columns=[col for col in drop_col if col in test_samples.columns])
                st.dataframe(test_samples)
                # Remove unwanted columns including 'Unnamed: 0'
                columns_to_drop = ['Unnamed: 0', 'instance_date', 'quarter', 'area_name_en', 'Year']
                columns_to_drop = [col for col in columns_to_drop if col in test_samples.columns]
                
                X_test = test_samples.drop(columns=columns_to_drop + ['meter_sale_price'], errors='ignore')
                y_test = test_samples['meter_sale_price']
                
                st.success(f"✅ Test data loaded: {X_test.shape[0]} samples, {X_test.shape[1]} features")
                #st.dataframe(test_samples.head(), use_container_width=True)
                
                # Identify categorical columns
                cat_cols = X_test.select_dtypes(include='object').columns.tolist()
        
                # Apply saved encoder
                if cat_cols:
                    X_cat_test = ohe.transform(X_test[cat_cols])
                    X_cat_test = pd.DataFrame(X_cat_test, columns=ohe.get_feature_names_out(cat_cols), index=X_test.index)
                    X_test = X_test.drop(columns=cat_cols)
                    X_test = pd.concat([X_test, X_cat_test], axis=1)
                
                # Ensure we only have numeric columns
                X_test = X_test.select_dtypes(include=[np.number])
                
                # =========================
                # 5️⃣ PREDICTION & METRICS
                # =========================
                if st.button("🚀 Run Predictions", type="primary", key="predict_btn"):
                    if len(area_models) == 0:
                        st.error("❌ No models loaded. Please check model files.")
                        st.stop()
                    
                    y_pred_total = pd.Series(index=test_samples.index, dtype=float)
                    test_metrics = {}
                    area_predictions = {}
            
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
                                y_pred = model.predict(X_area_test)
                                y_pred_total.loc[mask] = y_pred
            
                                # Metrics
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
                                
                                # Store predictions for plotting
                                area_predictions[area] = {
                                    'actual': y_area_test,
                                    'predicted': y_pred
                                }
                            except Exception as e:
                                st.error(f"❌ Error predicting for {area}: {e}")
                                continue
            
                    status_text.text("✅ Prediction completed!")
                    progress_bar.empty()
            
                    # =========================
                    # 6️⃣ DISPLAY RESULTS
                    # =========================
                    if test_metrics:
                        test_metrics_df = pd.DataFrame(test_metrics).T
                        test_metrics_df = test_metrics_df.sort_values(by='R2', ascending=False)
                        
                        # Display metrics table
                        st.subheader("📈 Prediction Results")
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
                            st.metric("Total Areas Processed", len(test_metrics))
                        with col2:
                            avg_r2 = test_metrics_df['R2'].mean()
                            st.metric("Average R² Score", f"{avg_r2:.4f}")
                        with col3:
                            total_samples = test_metrics_df['Samples'].sum()
                            st.metric("Total Samples", total_samples)
                        with col4:
                            avg_rmse = test_metrics_df['RMSE'].mean()
                            st.metric("Average RMSE", f"{avg_rmse:.2f}")
                        
                        # Best and worst performing areas
                        col1, col2 = st.columns(2)
                        with col1:
                            best_area = test_metrics_df.loc[test_metrics_df['R2'].idxmax()]
                            st.metric("Best R² Score", 
                                     f"{best_area['R2']:.4f}", 
                                     f"{test_metrics_df['R2'].idxmax()}")
                        
                        with col2:
                            worst_area = test_metrics_df.loc[test_metrics_df['R2'].idxmin()]
                            st.metric("Worst R² Score", 
                                     f"{worst_area['R2']:.4f}", 
                                     f"{test_metrics_df['R2'].idxmin()}")
                        
                        # =========================
                        # 7️⃣ VISUALIZATIONS FOR PREDICTIONS TAB
                        # =========================
                        st.subheader("📊 Prediction Visualizations")
                        
                        # Tab for different visualizations
                        viz_tab1, viz_tab2, viz_tab3 = st.tabs(["📈 Performance Metrics", "🔍 Actual vs Predicted", "📊 Area Comparison"])
                        
                        with viz_tab1:
                            # R2 Score Bar Chart
                            fig_r2 = px.bar(
                                x=test_metrics_df.index,
                                y=test_metrics_df['R2'],
                                title="R² Scores by Area",
                                labels={'x': 'Area', 'y': 'R² Score'},
                                color=test_metrics_df['R2'],
                                color_continuous_scale="RdYlGn"
                            )
                            fig_r2.update_layout(height=500)
                            st.plotly_chart(fig_r2, use_container_width=True)
                            
                            # RMSE and MAE comparison
                            fig_errors = go.Figure()
                            fig_errors.add_trace(go.Bar(name='RMSE', x=test_metrics_df.index, y=test_metrics_df['RMSE']))
                            fig_errors.add_trace(go.Bar(name='MAE', x=test_metrics_df.index, y=test_metrics_df['MAE']))
                            fig_errors.update_layout(title="Error Metrics by Area", barmode='group', height=500)
                            st.plotly_chart(fig_errors, use_container_width=True)
                        
                        with viz_tab2:
                            # Scatter plots for actual vs predicted
                            selected_area = st.selectbox("Select Area for Detailed Analysis", list(area_predictions.keys()))
                            
                            if selected_area in area_predictions:
                                actual = area_predictions[selected_area]['actual']
                                predicted = area_predictions[selected_area]['predicted']
                                
                                fig_scatter = px.scatter(
                                    x=actual, y=predicted,
                                    title=f"Actual vs Predicted Prices - {selected_area}",
                                    labels={'x': 'Actual Price', 'y': 'Predicted Price'},
                                    trendline="ols"
                                )
                                
                                # Add perfect prediction line
                                max_val = max(actual.max(), predicted.max())
                                min_val = min(actual.min(), predicted.min())
                                fig_scatter.add_trace(go.Scatter(
                                    x=[min_val, max_val], y=[min_val, max_val],
                                    mode='lines', name='Perfect Prediction',
                                    line=dict(dash='dash', color='red')
                                ))
                                
                                fig_scatter.update_layout(height=500)
                                st.plotly_chart(fig_scatter, use_container_width=True)
                                
                                # Residual plot
                                residuals = actual - predicted
                                fig_residual = px.scatter(
                                    x=predicted, y=residuals,
                                    title=f"Residual Plot - {selected_area}",
                                    labels={'x': 'Predicted Price', 'y': 'Residuals'}
                                )
                                fig_residual.add_hline(y=0, line_dash="dash", line_color="red")
                                fig_residual.update_layout(height=400)
                                #st.plotly_chart(fig_residual, use_container_width=True)
                        
                        with viz_tab3:
                            # Price comparison chart
                            fig_prices = go.Figure()
                            fig_prices.add_trace(go.Bar(name='Actual Price', x=test_metrics_df.index, y=test_metrics_df['Avg_Actual_Price']))
                            fig_prices.add_trace(go.Bar(name='Predicted Price', x=test_metrics_df.index, y=test_metrics_df['Avg_Predicted_Price']))
                            fig_prices.update_layout(title="Average Actual vs Predicted Prices by Area", barmode='group', height=500)
                            st.plotly_chart(fig_prices, use_container_width=True)
                            
                            # Error percentage by area
                            error_percentage = ((test_metrics_df['Avg_Actual_Price'] - test_metrics_df['Avg_Predicted_Price']) / test_metrics_df['Avg_Actual_Price'] * 100).abs()
                            fig_error_pct = px.bar(
                                x=error_percentage.index,
                                y=error_percentage.values,
                                title="Absolute Error Percentage by Area",
                                labels={'x': 'Area', 'y': 'Error %'},
                                color=error_percentage.values,
                                color_continuous_scale="Reds"
                            )
                            fig_error_pct.update_layout(height=400)
                            st.plotly_chart(fig_error_pct, use_container_width=True)
                        
                        # Download results
                        results_df = test_samples.copy()
                        results_df['predicted_price'] = y_pred_total
                        results_df['prediction_error'] = results_df['meter_sale_price'] - results_df['predicted_price']
                        results_df['error_percentage'] = (results_df['prediction_error'] / results_df['meter_sale_price'] * 100).round(2)
                        
                        csv = results_df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Full Predictions CSV",
                            data=csv,
                            file_name="dubai_real_estate_predictions.csv",
                            mime="text/csv"
                        )
                            
                    else:
                        st.warning("No predictions were made. Check if area names match the trained models.")
                        
            except FileNotFoundError:
                st.error("❌ Test data file 'test_data_20 areas_1.csv' not found. Please make sure the file exists in the same directory.")
            except Exception as e:
                st.error(f"❌ Error loading test data: {str(e)}")
        
    
    ####################################################################________________________>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>______________________________________################################################
        with tab2:
            #st.header("🔮 Price Forecasting")
            #st.markdown("Area-wise predictions with growth factor projections")

            # =========================
            # 8️⃣ LOAD DATA FOR FORECASTING TAB
            # =========================
            @st.cache_data
            def load_forecasting_data():
                """Load forecasting-specific data"""
                try:
                    # Load test data for forecasting
                    #test_samples_forecast = pd.read_csv(selected_file_label)
                    
                    test_samples_forecast = pd.read_csv(file_path)
                    test_samples_forecast = test_samples_forecast.drop(columns=[col for col in drop_col if col in test_samples_forecast.columns])
                    st.dataframe(test_samples_forecast)
                    # Remove unwanted columns
                    columns_to_drop = ['Unnamed: 0', 'instance_date', 'quarter', 'Year']
                    columns_to_drop = [col for col in columns_to_drop if col in test_samples_forecast.columns]
                    X_test_forecast = test_samples_forecast.drop(columns=columns_to_drop + ['meter_sale_price'], errors='ignore')
                    
                    # Load train columns
                    with open("train_columns.pkl", "rb") as f:
                        train_columns = pickle.load(f)
                    
                    # Load growth factors - ALL THREE FACTORS
                    growth_df = pd.read_csv('arima_areas_growth_6M.csv')
                    growth_df = growth_df[['ds', 'area_name_en', 'growth_factor', 'growth_factor_lower', 'growth_factor_upper']]
                    
                    # Create pivot tables for all three growth factors
                    growth_pivot = growth_df.pivot(index='area_name_en', columns='ds', values='growth_factor').reset_index()
                    growth_lower_pivot = growth_df.pivot(index='area_name_en', columns='ds', values='growth_factor_lower').reset_index()
                    growth_upper_pivot = growth_df.pivot(index='area_name_en', columns='ds', values='growth_factor_upper').reset_index()
                    
                    # Load and prepare historical quarterly median prices from training data
                    train_data = pd.read_csv("df_trained_dataset_6000.csv")  # Assuming you have training data
                    # Extract year-quarter from instance_date
                    train_data['instance_date'] = pd.to_datetime(train_data['instance_date'])
                    train_data['year_quarter'] = train_data['instance_date'].dt.year.astype(str) + '-Q' + train_data['instance_date'].dt.quarter.astype(str)
                    
                    # Calculate median prices per area per quarter
                    historical_median = train_data.groupby(['area_name_en', 'year_quarter'])['meter_sale_price'].median().reset_index()
                    historical_pivot = historical_median.pivot(index='area_name_en', columns='year_quarter', values='meter_sale_price').reset_index()
                    
                    # Calculate overall historical trends (across all areas)
                    overall_historical_median = train_data.groupby(['year_quarter'])['meter_sale_price'].median().reset_index()
                    overall_historical_pivot = overall_historical_median.set_index('year_quarter')['meter_sale_price'].to_dict()
                    
                    # Get the most recent 4 quarters for historical context
                    recent_quarters = sorted(historical_median['year_quarter'].unique())#[-12:]
                    historical_pivot_recent = historical_pivot[['area_name_en'] + recent_quarters]
                    
                    return test_samples_forecast, X_test_forecast, train_columns, growth_pivot, growth_lower_pivot, growth_upper_pivot, historical_pivot_recent, recent_quarters, overall_historical_pivot
                except Exception as e:
                    st.error(f"Error loading forecasting data: {str(e)}")
                    return None, None, None, None, None, None, None, None, None

            # Load data for forecasting
            with st.spinner("Loading forecasting data..."):
                test_samples_forecast, X_test_forecast_raw, train_columns, growth_pivot, growth_lower_pivot, growth_upper_pivot, historical_pivot, historical_quarters, overall_historical_pivot = load_forecasting_data()

            if test_samples_forecast is None:
                st.error("❌ Failed to load forecasting data")
                st.stop()
            
            # Prepare test data for forecasting
            try:
                # Separate area_name_en column for later use
                area_names_forecast = X_test_forecast_raw['area_name_en']
                X_test_forecast_no_area = X_test_forecast_raw.drop(columns=['area_name_en'], errors='ignore')
                
                # Identify categorical columns (excluding area_name_en)
                cat_cols = X_test_forecast_no_area.select_dtypes(include='object').columns.tolist()
                
                # Apply one-hot encoding
                if cat_cols:
                    X_cat_test = ohe.transform(X_test_forecast_no_area[cat_cols])
                    X_cat_test = pd.DataFrame(X_cat_test, columns=ohe.get_feature_names_out(cat_cols), index=X_test_forecast_no_area.index)
                    
                    X_test_forecast = X_test_forecast_no_area.drop(columns=cat_cols)
                    X_test_forecast = pd.concat([X_test_forecast, X_cat_test], axis=1)
                else:
                    X_test_forecast = X_test_forecast_no_area.copy()
                
                # Ensure we have all training columns
                for col in train_columns:
                    if col not in X_test_forecast.columns:
                        X_test_forecast[col] = 0
                
                X_test_forecast = X_test_forecast[train_columns]
                X_test_forecast = X_test_forecast.select_dtypes(include=[np.number])
                
            except Exception as e:
                st.error(f"❌ Error preparing forecasting data: {str(e)}")
                st.stop()
            
            # =========================
            # 9️⃣ FORECASTING CONTROLS
            # =========================
            st.sidebar.title("🔧 Forecast Controls")
            
            # Area selection
            available_areas = list(area_models.keys())
            selected_areas_forecast = st.sidebar.multiselect(
                "Select Areas for Forecasting",
                options=available_areas,
                default=available_areas[:4] if len(available_areas) > 4 else available_areas,
                key="forecast_areas_sidebar"
            )
            
            # Feature grouping options
            grouping_options = ['rooms_en', 'floor_bin', 'swimming_pool', 'balcony', 'elevator', 'metro', 'has_parking']
            selected_grouping = st.sidebar.selectbox(
                "Group by Feature",
                options=grouping_options,
                index=0,
                key="grouping_feature_sidebar"
            )
            
            # Display options
            st.sidebar.markdown("---")
            st.sidebar.subheader("📊 Display Options")
            show_historical = st.sidebar.checkbox("Show Historical Quarterly Trends", value=True, key="show_historical")
            show_overall_trend = st.sidebar.checkbox("Show Overall Market Trend", value=True, key="show_overall")
            show_growth_scenarios = st.sidebar.checkbox("Show All Growth Scenarios", value=True, key="show_scenarios")
            num_historical_quarters = st.sidebar.slider("Number of Historical Quarters to Show", 
                                                      min_value=1, max_value=12, value=4, key="hist_quarters")
            
            # =========================
            # 🔟 FORECASTING EXECUTION
            # =========================
            if st.button("🚀 Generate Forecast", type="primary", key="forecast_button"):
                if len(selected_areas_forecast) == 0:
                    st.warning("Please select at least one area for forecasting")
                    st.stop()
                    
                with st.spinner("Generating forecasts..."):
                    # Dynamic grouping features
                    if selected_grouping == 'rooms_en':
                        grouping_features = [col for col in X_test_forecast.columns if col.startswith("rooms_en_")]
                    elif selected_grouping == 'floor_bin':
                        grouping_features = [col for col in X_test_forecast.columns if col.startswith("floor_bin_")]
                    else:
                        grouping_features = [selected_grouping]
                
                    pred_list = []
                    overall_predictions = []
                
                    for area in selected_areas_forecast:
                        if area not in area_models:
                            continue
                
                        model = area_models[area]
                        mask = test_samples_forecast['area_name_en'] == area
                        X_area_test = X_test_forecast.loc[mask]
                
                        if len(X_area_test) > 0:
                            y_pred = model.predict(X_area_test)
                
                            # Collect predictions for feature-wise analysis
                            df_area_pred = X_area_test[grouping_features].copy()
                            df_area_pred['area_name_en'] = area
                            df_area_pred['prediction'] = y_pred
                            pred_list.append(df_area_pred)
                            
                            # Collect predictions for overall trend
                            overall_df = pd.DataFrame({
                                'area_name_en': [area] * len(y_pred),
                                'prediction': y_pred
                            })
                            overall_predictions.append(overall_df)
                
                    if not pred_list:
                        st.error("No predictions generated. Check area selection.")
                        st.stop()
                        
                    pred_df = pd.concat(pred_list)
                    overall_pred_df = pd.concat(overall_predictions)
                
                    # Feature-wise grouping
                    group_cols = ['area_name_en'] + grouping_features
                    median_pred_group = pred_df.groupby(group_cols)['prediction'].median().reset_index()
                    
                    # Overall trend (across all selected areas and features)
                    overall_median = overall_pred_df.groupby(['area_name_en'])['prediction'].median().reset_index()
                
                    # Merge with growth factors for all three scenarios
                    forecast_df = median_pred_group.merge(growth_pivot, on='area_name_en', how='left')
                    forecast_lower_df = median_pred_group.merge(growth_lower_pivot, on='area_name_en', how='left')
                    forecast_upper_df = median_pred_group.merge(growth_upper_pivot, on='area_name_en', how='left')
                    
                    overall_forecast_df = overall_median.merge(growth_pivot, on='area_name_en', how='left')
                    overall_forecast_lower_df = overall_median.merge(growth_lower_pivot, on='area_name_en', how='left')
                    overall_forecast_upper_df = overall_median.merge(growth_upper_pivot, on='area_name_en', how='left')
                    
                    # Merge with historical data
                    if historical_pivot is not None:
                        forecast_df = forecast_df.merge(historical_pivot, on='area_name_en', how='left')
                        forecast_lower_df = forecast_lower_df.merge(historical_pivot, on='area_name_en', how='left')
                        forecast_upper_df = forecast_upper_df.merge(historical_pivot, on='area_name_en', how='left')
                        
                        overall_forecast_df = overall_forecast_df.merge(historical_pivot, on='area_name_en', how='left')
                        overall_forecast_lower_df = overall_forecast_lower_df.merge(historical_pivot, on='area_name_en', how='left')
                        overall_forecast_upper_df = overall_forecast_upper_df.merge(historical_pivot, on='area_name_en', how='left')
                
                    # Apply growth factors to future quarters for all three scenarios
                    future_quarter_cols = [col for col in growth_pivot.columns if col != 'area_name_en']
                    for q in future_quarter_cols:
                        if q in forecast_df.columns:
                            forecast_df[q] = forecast_df['prediction'] * forecast_df[q]
                            forecast_lower_df[q] = forecast_lower_df['prediction'] * forecast_lower_df[q]
                            forecast_upper_df[q] = forecast_upper_df['prediction'] * forecast_upper_df[q]
                            
                        if q in overall_forecast_df.columns:
                            overall_forecast_df[q] = overall_forecast_df['prediction'] * overall_forecast_df[q]
                            overall_forecast_lower_df[q] = overall_forecast_lower_df['prediction'] * overall_forecast_lower_df[q]
                            overall_forecast_upper_df[q] = overall_forecast_upper_df['prediction'] * overall_forecast_upper_df[q]
                
                    # Final forecast with historical data
                    all_quarter_cols = []
                    if show_historical and historical_pivot is not None:
                        available_historical = [col for col in historical_pivot.columns if col != 'area_name_en']
                        selected_historical = available_historical[-num_historical_quarters:]
                        all_quarter_cols = selected_historical + ['prediction'] + future_quarter_cols
                    else:
                        all_quarter_cols = ['prediction'] + future_quarter_cols
                    
                    final_forecast = forecast_df[group_cols + all_quarter_cols]
                    final_forecast_lower = forecast_lower_df[group_cols + all_quarter_cols]
                    final_forecast_upper = forecast_upper_df[group_cols + all_quarter_cols]
                    
                    final_overall_forecast = overall_forecast_df[['area_name_en'] + all_quarter_cols]
                    final_overall_forecast_lower = overall_forecast_lower_df[['area_name_en'] + all_quarter_cols]
                    final_overall_forecast_upper = overall_forecast_upper_df[['area_name_en'] + all_quarter_cols]
                
                # =========================
                # 1️⃣1️⃣ FORECASTING VISUALIZATIONS
                # =========================
                st.success(f"✅ Forecast generated for {len(final_forecast)} feature combinations")
                
                # Display forecast tables
                st.subheader("📋 Forecast Results")
                
                # Scenario selection for table display
                scenario_tabs = st.tabs(["📊 Base Scenario", "📉 Lower Bound", "📈 Upper Bound"])
                
                with scenario_tabs[0]:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Feature-wise Forecast (Base)**")
                        display_df = final_forecast.copy()
                        for col in all_quarter_cols:
                            if col in display_df.columns:
                                display_df[col] = display_df[col].round(2)
                        st.dataframe(display_df, use_container_width=True)
                    with col2:
                        st.markdown("**Overall Area Forecast (Base)**")
                        overall_display_df = final_overall_forecast.copy()
                        for col in all_quarter_cols:
                            if col in overall_display_df.columns:
                                overall_display_df[col] = overall_display_df[col].round(2)
                        st.dataframe(overall_display_df, use_container_width=True)
                
                with scenario_tabs[1]:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Feature-wise Forecast (Lower Bound)**")
                        display_df_lower = final_forecast_lower.copy()
                        for col in all_quarter_cols:
                            if col in display_df_lower.columns:
                                display_df_lower[col] = display_df_lower[col].round(2)
                        st.dataframe(display_df_lower, use_container_width=True)
                    with col2:
                        st.markdown("**Overall Area Forecast (Lower Bound)**")
                        overall_display_df_lower = final_overall_forecast_lower.copy()
                        for col in all_quarter_cols:
                            if col in overall_display_df_lower.columns:
                                overall_display_df_lower[col] = overall_display_df_lower[col].round(2)
                        st.dataframe(overall_display_df_lower, use_container_width=True)
                
                with scenario_tabs[2]:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Feature-wise Forecast (Upper Bound)**")
                        display_df_upper = final_forecast_upper.copy()
                        for col in all_quarter_cols:
                            if col in display_df_upper.columns:
                                display_df_upper[col] = display_df_upper[col].round(2)
                        st.dataframe(display_df_upper, use_container_width=True)
                    with col2:
                        st.markdown("**Overall Area Forecast (Upper Bound)**")
                        overall_display_df_upper = final_overall_forecast_upper.copy()
                        for col in all_quarter_cols:
                            if col in overall_display_df_upper.columns:
                                overall_display_df_upper[col] = overall_display_df_upper[col].round(2)
                        st.dataframe(overall_display_df_upper, use_container_width=True)
                
                # Visualizations
                st.subheader("📈 Forecast Visualizations")
                
                # Helper function for quarter formatting
                def format_quarter_label(quarter_str):
                    if '-' in quarter_str:
                        parts = quarter_str.split('-')
                        if len(parts) == 2:
                            return f"{parts[0]} {parts[1]}"
                    return quarter_str.replace('_', ' ').title()
                
                # Helper function to prepare forecast data for plotting from a DataFrame row
                def prepare_forecast_data(forecast_row, selected_historical, future_quarter_cols, show_historical):
                    time_periods = []
                    prices = []
                    
                    # Add historical quarters
                    if show_historical:
                        historical_cols = [col for col in selected_historical if col in forecast_row.index and pd.notna(forecast_row[col])]
                        for hq in historical_cols:
                            time_periods.append(format_quarter_label(hq))
                            prices.append(forecast_row[hq])
                    
                    # Add current prediction
                    time_periods.append('Current')
                    prices.append(forecast_row['prediction'])
                    
                    # Add future quarters
                    for fq in future_quarter_cols:
                        if fq in forecast_row.index and pd.notna(forecast_row[fq]):
                            time_periods.append(format_quarter_label(fq))
                            prices.append(forecast_row[fq])
                    
                    return time_periods, prices

                # 1. OVERALL MARKET TREND (ACROSS ALL SELECTED AREAS)
                if show_overall_trend:
                    st.markdown("### 🌐 Overall Market Trend - All Scenarios")
                    fig_overall = go.Figure()
                    
                    # Add overall historical trend line
                    if show_historical and overall_historical_pivot:
                        historical_quarters_sorted = sorted([q for q in overall_historical_pivot.keys() if q in selected_historical])
                        historical_prices = [overall_historical_pivot[q] for q in historical_quarters_sorted]
                        historical_labels = [format_quarter_label(q) for q in historical_quarters_sorted]
                        
                        fig_overall.add_trace(go.Scatter(
                            x=historical_labels,
                            y=historical_prices,
                            mode='lines+markers',
                            name='Overall Market Historical',
                            line=dict(color='blue', width=4, dash='solid'),
                            marker=dict(size=8)
                        ))
                    
                    # Calculate median predictions across all areas for each scenario
                    scenarios = [
                        (final_overall_forecast, 'Base Scenario', 'red', 'solid'),
                        (final_overall_forecast_lower, 'Lower Bound', 'orange', 'dot'),
                        (final_overall_forecast_upper, 'Upper Bound', 'green', 'dash')
                    ]
                    
                    for scenario_df, scenario_name, color, dash_style in scenarios:
                        future_prices = []
                        valid_future_quarters = []
                        
                        for area in selected_areas_forecast:
                            area_data = scenario_df[scenario_df['area_name_en'] == area]
                            if not area_data.empty:
                                area_future_prices = []
                                for q in future_quarter_cols:
                                    if q in area_data.columns and pd.notna(area_data[q].iloc[0]):
                                        area_future_prices.append(area_data[q].iloc[0])
                                        if q not in valid_future_quarters:
                                            valid_future_quarters.append(q)
                                if area_future_prices:
                                    future_prices.append(area_future_prices)
                        
                        if future_prices:
                            # Calculate median future prices across all areas
                            max_len = max(len(prices) for prices in future_prices)
                            padded_prices = []
                            for prices in future_prices:
                                if len(prices) < max_len:
                                    padded_prices.append(prices + [np.nan] * (max_len - len(prices)))
                                else:
                                    padded_prices.append(prices)
                            
                            future_median_prices = np.nanmedian(padded_prices, axis=0)
                            future_labels = [format_quarter_label(q) for q in valid_future_quarters]
                            
                            # Combine historical, current and future
                            time_periods = []
                            overall_prices = []
                            
                            if show_historical:
                                time_periods.extend(historical_labels)
                                overall_prices.extend(historical_prices)
                            
                            # Add current overall prediction
                            current_overall_median = overall_pred_df['prediction'].median()
                            time_periods.append('Current')
                            overall_prices.append(current_overall_median)
                            
                            time_periods.extend(future_labels)
                            overall_prices.extend(future_median_prices)
                            
                            fig_overall.add_trace(go.Scatter(
                                x=time_periods,
                                y=overall_prices,
                                mode='lines+markers',
                                name=scenario_name,
                                line=dict(color=color, width=3, dash=dash_style),
                                marker=dict(size=8)
                            ))
                    
                    fig_overall.update_layout(
                        title="Overall Market Price Trend & Forecast - All Scenarios",
                        xaxis_title="Time Period",
                        yaxis_title="Median Price (AED)",
                        height=500,
                        template="plotly_white",
                        showlegend=True
                    )
                    
                    if show_historical:
                        fig_overall.add_vline(
                            x=len(historical_labels) - 0.5, 
                            line_width=2, 
                            line_dash="dot", 
                            line_color="gray",
                            annotation_text="Historical → Forecast"
                        )
                    
                    st.plotly_chart(fig_overall, use_container_width=True)
                
                # 2. AREA-WISE FORECAST CHARTS WITH ALL SCENARIOS
                for area in selected_areas_forecast:
                    area_data_base = final_forecast[final_forecast['area_name_en'] == area]
                    area_overall_base = final_overall_forecast[final_overall_forecast['area_name_en'] == area]
                    area_overall_lower = final_overall_forecast_lower[final_overall_forecast_lower['area_name_en'] == area]
                    area_overall_upper = final_overall_forecast_upper[final_overall_forecast_upper['area_name_en'] == area]
                    
                    if area_data_base.empty:
                        continue
                        
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"### 📊 {area} - Feature-wise Forecast (Base Scenario)")
                        fig_features = go.Figure()
                        
                        for idx, (_, row) in enumerate(area_data_base.iterrows()):
                            # Create feature label
                            feature_label = ""
                            for gf in grouping_features:
                                if gf in row and row[gf] == 1:
                                    feature_label += f"{gf.replace('_', ' ').title()}, "
                            feature_label = feature_label.rstrip(", ") or f"Config {idx+1}"
                            
                            time_periods, prices = prepare_forecast_data(row, selected_historical, future_quarter_cols, show_historical)
                            
                            # Plot feature-wise trend
                            fig_features.add_trace(go.Scatter(
                                x=time_periods, y=prices,
                                mode='lines+markers',
                                name=feature_label,
                                line=dict(width=3),
                                marker=dict(size=6)
                            ))
                        
                        fig_features.update_layout(
                            title=f"Feature-wise Forecast - {area} (Base)",
                            xaxis_title="Time Period",
                            yaxis_title="Price (AED)",
                            height=400,
                            template="plotly_white"
                        )
                        st.plotly_chart(fig_features, use_container_width=True)
                    
                    with col2:
                        st.markdown(f"### 📈 {area} - Overall Trend (All Scenarios)")
                        fig_overall_area = go.Figure()
                        
                        # Plot all three scenarios for the area
                        scenarios = [
                            (area_overall_base, 'Base Scenario', 'red', 'solid'),
                            (area_overall_lower, 'Lower Bound', 'orange', 'dot'),
                            (area_overall_upper, 'Upper Bound', 'green', 'dash')
                        ]
                        
                        for scenario_df, scenario_name, color, dash_style in scenarios:
                            if not scenario_df.empty:
                                row = scenario_df.iloc[0]
                                time_periods, prices = prepare_forecast_data(row, selected_historical, future_quarter_cols, show_historical)
                                
                                fig_overall_area.add_trace(go.Scatter(
                                    x=time_periods, y=prices,
                                    mode='lines+markers',
                                    name=f'{area} - {scenario_name}',
                                    line=dict(color=color, width=3, dash=dash_style),
                                    marker=dict(size=8)
                                ))
                        
                        fig_overall_area.update_layout(
                            title=f"Overall Area Forecast - {area} (All Scenarios)",
                            xaxis_title="Time Period",
                            yaxis_title="Price (AED)",
                            height=400,
                            template="plotly_white"
                        )
                        st.plotly_chart(fig_overall_area, use_container_width=True)
                
                # 3. COMPARISON HEATMAP FOR BASE SCENARIO
                st.subheader("🔥 Market Comparison Heatmap (Base Scenario)")
                
                # Prepare heatmap data for base scenario
                heatmap_data = []
                row_labels = []
                time_periods_heatmap = []
                
                if show_historical:
                    historical_labels = [format_quarter_label(hq) for hq in selected_historical]
                    time_periods_heatmap.extend(historical_labels)
                time_periods_heatmap.append('Current')
                future_labels = [format_quarter_label(fq) for fq in future_quarter_cols]
                time_periods_heatmap.extend(future_labels)
                
                # Add overall market trend for base scenario
                if show_overall_trend:
                    overall_prices_heatmap = []
                    # Historical
                    if show_historical and overall_historical_pivot:
                        for hq in selected_historical:
                            if hq in overall_historical_pivot:
                                overall_prices_heatmap.append(overall_historical_pivot[hq])
                    # Current and future
                    current_overall_median = overall_pred_df['prediction'].median()
                    overall_prices_heatmap.append(current_overall_median)
                    
                    # Calculate future median for base scenario
                    future_prices_base = []
                    for area in selected_areas_forecast:
                        area_data = final_overall_forecast[final_overall_forecast['area_name_en'] == area]
                        if not area_data.empty:
                            area_future_prices = []
                            for q in future_quarter_cols:
                                if q in area_data.columns and pd.notna(area_data[q].iloc[0]):
                                    area_future_prices.append(area_data[q].iloc[0])
                            if area_future_prices:
                                future_prices_base.append(area_future_prices)
                    
                    if future_prices_base:
                        max_len = max(len(prices) for prices in future_prices_base)
                        padded_prices = []
                        for prices in future_prices_base:
                            if len(prices) < max_len:
                                padded_prices.append(prices + [np.nan] * (max_len - len(prices)))
                            else:
                                padded_prices.append(prices)
                        future_median_prices = np.nanmedian(padded_prices, axis=0)
                        overall_prices_heatmap.extend(future_median_prices)
                    
                    if len(overall_prices_heatmap) == len(time_periods_heatmap):
                        heatmap_data.append(overall_prices_heatmap)
                        row_labels.append("Overall Market")
                
                # Add area trends for base scenario
                for area in selected_areas_forecast:
                    area_data = final_overall_forecast[final_overall_forecast['area_name_en'] == area]
                    if not area_data.empty:
                        row = area_data.iloc[0]
                        area_prices = []
                        
                        # Historical
                        if show_historical:
                            for hq in selected_historical:
                                if hq in row and pd.notna(row[hq]):
                                    area_prices.append(row[hq])
                                else:
                                    area_prices.append(np.nan)
                        
                        # Current and future
                        area_prices.append(row['prediction'])
                        for fq in future_quarter_cols:
                            if fq in row and pd.notna(row[fq]):
                                area_prices.append(row[fq])
                            else:
                                area_prices.append(np.nan)
                        
                        if len(area_prices) == len(time_periods_heatmap):
                            heatmap_data.append(area_prices)
                            row_labels.append(area)
                
                if heatmap_data:
                    heatmap_df = pd.DataFrame(
                        heatmap_data,
                        index=row_labels,
                        columns=time_periods_heatmap
                    )
                    
                    fig_heat = px.imshow(
                        heatmap_df,
                        title="Price Comparison Heatmap - Base Scenario (AED)",
                        color_continuous_scale="Viridis",
                        aspect="auto",
                        labels=dict(x="Time Period", y="Area/Market", color="Price (AED)")
                    )
                    fig_heat.update_layout(height=500)
                    st.plotly_chart(fig_heat, use_container_width=True)
                
                # Download forecast results for all scenarios
                st.subheader("📥 Download Forecast Results")
                
                download_col1, download_col2, download_col3 = st.columns(3)
                
                with download_col1:
                    csv_base = final_forecast.to_csv(index=False)
                    st.download_button(
                        label="📥 Base Scenario",
                        data=csv_base,
                        file_name="dubai_forecast_base_scenario.csv",
                        mime="text/csv",
                        key="forecast_base_download")
                
                with download_col2:
                    csv_lower = final_forecast_lower.to_csv(index=False)
                    st.download_button(
                        label="📥 Lower Bound",
                        data=csv_lower,
                        file_name="dubai_forecast_lower_bound.csv",
                        mime="text/csv",
                        key="forecast_lower_download")
                
                with download_col3:
                    csv_upper = final_forecast_upper.to_csv(index=False)
                    st.download_button(
                        label="📥 Upper Bound",
                        data=csv_upper,
                        file_name="dubai_forecast_upper_bound.csv",
                        mime="text/csv",
                        key="forecast_upper_download")
    ###############################################################################################################################################################################################################################

import pandas as pd
import streamlit as st
import pickle
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')
# =====================
# TAB 3: Area-wise Prediction & Forecast
# =====================
if sidebar_option == "validation":
    import streamlit as st
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    import numpy as np
    from datetime import datetime
    
   
    # =========================
    # LOAD DATA
    # =========================
    @st.cache_data
    def load_data():
        # Load your datasets
        train_data = pd.read_csv('df_trained_dataset_6000.csv')  # Replace with your train data path
        forecasts_df = pd.read_csv('2024_preditions_forcast.csv')  # Your forecasts dataframe with all columns
        
        # Ensure quarter columns are properly formatted
        if 'quarter' in train_data.columns:
            train_data['quarter'] = pd.to_datetime(train_data['quarter'])
        if 'forecast_quarter' in forecasts_df.columns:
            forecasts_df['forecast_quarter'] = pd.to_datetime(forecasts_df['forecast_quarter'])
        
        return train_data, forecasts_df
    
    try:
        train_data, forecasts_df = load_data()
        
        # =========================
        # SIDEBAR - AREA SELECTION
        # =========================
        st.sidebar.header("🔍 Area Selection & Filters")
        
        # Get unique areas from forecasts
        available_areas = forecasts_df['area_name_en'].unique()
        selected_area = st.sidebar.selectbox(
            "Select Area:",
            options=available_areas,
            index=0
        )
        
        # Date range filter for train data
        if 'quarter' in train_data.columns:
            min_date = train_data['quarter'].min()
            max_date = train_data['quarter'].max()
            
            st.sidebar.subheader("📅 Date Range Filter")
            date_range = st.sidebar.date_input(
                "Select date range for historical data:",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
        
        # Forecast quarters filter
        st.sidebar.subheader("🔮 Forecast Horizon")
        forecast_quarters = sorted(forecasts_df['forecast_quarter'].unique())
        selected_forecast_quarters = st.sidebar.multiselect(
            "Select forecast quarters to display:",
            options=forecast_quarters,
            default=forecast_quarters
        )
        
        # =========================
        # FILTER DATA FOR SELECTED AREA
        # =========================
        # Filter train data for selected area
        area_train_data = train_data[train_data['area_name_en'] == selected_area].copy()
        
        # Filter forecasts for selected area and selected quarters
        area_forecasts = forecasts_df[
            (forecasts_df['area_name_en'] == selected_area) & 
            (forecasts_df['forecast_quarter'].isin(selected_forecast_quarters))
        ].copy().sort_values('forecast_quarter')
        
        # =========================
        # CALCULATE QUARTERLY MEDIAN PRICES FROM TRAIN DATA
        # =========================
        if not area_train_data.empty and 'quarter' in area_train_data.columns:
            # Apply date filter if selected
            if 'date_range' in locals() and len(date_range) == 2:
                start_date, end_date = date_range
                area_train_data = area_train_data[
                    (area_train_data['quarter'] >= pd.Timestamp(start_date)) & 
                    (area_train_data['quarter'] <= pd.Timestamp(end_date))
                ]
            
            quarterly_median = area_train_data.groupby('quarter')['meter_sale_price'].agg([
                'median', 'count', 'mean', 'std'
            ]).reset_index()
            quarterly_median.columns = ['quarter', 'median_price', 'sample_count', 'mean_price', 'price_std']
            quarterly_median = quarterly_median.sort_values('quarter')
        else:
            quarterly_median = pd.DataFrame(columns=['quarter', 'median_price', 'sample_count', 'mean_price', 'price_std'])
        
        # =========================
        # MAIN DASHBOARD
        # =========================
        if not area_forecasts.empty:
            # Key Metrics
            st.subheader(f"📊 Key Metrics - {selected_area}")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                current_forecast = area_forecasts['forecast_price'].iloc[0]
                st.metric("Current Forecast Price", f"${current_forecast:,.2f}")
            
            with col2:
                growth = area_forecasts['growth_factor'].iloc[0] * 100
                st.metric("Growth Factor", f"{growth:.2f}%")
            
            with col3:
                if 'avg_predicted' in area_forecasts.columns:
                    predicted_price = area_forecasts['avg_predicted'].iloc[0]
                    st.metric("Average Predicted Price", f"${predicted_price:,.2f}")
            
            with col4:
                if not quarterly_median.empty:
                    latest_median = quarterly_forecasts['median_price'].iloc[-1]
                    st.metric("Latest Historical Median", f"${latest_median:,.2f}")
            
            # =========================
            # TREND VISUALIZATION
            # =========================
            st.subheader(f"📈 Price Trends & Forecasts for {selected_area}")
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))
            
            # Plot 1: Price Trends
            # Historical median prices
            if not quarterly_median.empty:
                ax1.plot(quarterly_median['quarter'], quarterly_median['median_price'], 
                        label='Historical Median Price', color='blue', linewidth=3, marker='o', markersize=6)
                
                # Add confidence interval for historical data
                if 'price_std' in quarterly_median.columns:
                    ax1.fill_between(quarterly_median['quarter'],
                                   quarterly_median['median_price'] - quarterly_median['price_std'],
                                   quarterly_median['median_price'] + quarterly_median['price_std'],
                                   alpha=0.2, color='blue', label='Historical Price Variability')
            
            # Plot average predictions
            if not area_forecasts.empty and 'avg_predicted' in area_forecasts.columns:
                # Use the first forecast quarter as prediction point
                pred_quarter = area_forecasts['forecast_quarter'].iloc[0]
                pred_price = area_forecasts['avg_predicted'].iloc[0]
                ax1.scatter(pred_quarter, pred_price, color='red', s=150, 
                           label='Model Prediction', zorder=10, marker='D')
                ax1.annotate(f'Prediction: ${pred_price:,.0f}', 
                            (pred_quarter, pred_price),
                            textcoords="offset points", 
                            xytext=(15, 15), 
                            ha='left',
                            fontsize=10,
                            bbox=dict(boxstyle="round,pad=0.3", facecolor="red", alpha=0.2))
            
            # Plot forecasts
            if not area_forecasts.empty:
                # Main forecast line
                ax1.plot(area_forecasts['forecast_quarter'], area_forecasts['forecast_price'],
                        label='Price Forecast', color='green', linewidth=4, linestyle='--', marker='s', markersize=8)
                
                # Forecast uncertainty (yhat_lower to yhat_upper)
                ax1.fill_between(area_forecasts['forecast_quarter'],
                               area_forecasts['yhat_lower'],
                               area_forecasts['yhat_upper'],
                               alpha=0.3, color='green', label='Forecast Confidence Interval')
                
                # Annotate forecast points with growth factors
                for idx, row in area_forecasts.iterrows():
                    ax1.annotate(f"+{row['growth_factor']*100:.1f}%",
                                (row['forecast_quarter'], row['forecast_price']),
                                textcoords="offset points",
                                xytext=(10, 10 if idx % 2 == 0 else -20),
                                ha='center',
                                fontsize=9,
                                fontweight='bold',
                                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen", alpha=0.7))
            
            ax1.set_xlabel('Quarter', fontsize=12)
            ax1.set_ylabel('Price per Meter ($)', fontsize=12)
            ax1.set_title(f'Real Estate Price Trends - {selected_area}\n'
                         f'Historical Median vs Predictions vs Forecasts', fontsize=14, fontweight='bold')
            ax1.legend(fontsize=10)
            ax1.grid(True, alpha=0.3)
            ax1.tick_params(axis='x', rotation=45)
            
            # Plot 2: Growth Factors
            if not area_forecasts.empty:
                # Main growth factor line
                ax2.plot(area_forecasts['forecast_quarter'], area_forecasts['growth_factor'] * 100,
                        label='Growth Factor', color='purple', linewidth=3, marker='o', markersize=6)
                
                # Growth factor uncertainty
                ax2.fill_between(area_forecasts['forecast_quarter'],
                               area_forecasts['growth_factor_lower'] * 100,
                               area_forecasts['growth_factor_upper'] * 100,
                               alpha=0.3, color='purple', label='Growth Factor Range')
                
                # Add zero reference line
                ax2.axhline(y=0, color='red', linestyle='--', alpha=0.5, label='Zero Growth')
                
                # Annotate growth factors
                for idx, row in area_forecasts.iterrows():
                    ax2.annotate(f"{row['growth_factor']*100:+.1f}%",
                                (row['forecast_quarter'], row['growth_factor'] * 100),
                                textcoords="offset points",
                                xytext=(0, 10),
                                ha='center',
                                fontsize=9,
                                fontweight='bold')
            
            ax2.set_xlabel('Quarter', fontsize=12)
            ax2.set_ylabel('Growth Factor (%)', fontsize=12)
            ax2.set_title('Growth Factor Trends with Confidence Intervals', fontsize=14, fontweight='bold')
            ax2.legend(fontsize=10)
            ax2.grid(True, alpha=0.3)
            ax2.tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            st.pyplot(fig)
            
            # =========================
            # DATA TABLES
            # =========================
            st.subheader("📋 Detailed Data View")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Historical Price Data**")
                if not quarterly_median.empty:
                    historical_display = quarterly_median[['quarter', 'median_price', 'mean_price', 'sample_count']].copy()
                    historical_display = historical_display.round(2)
                    st.dataframe(historical_display.style.format({
                        'median_price': '${:,.2f}',
                        'mean_price': '${:,.2f}',
                        'sample_count': '{:.0f}'
                    }), use_container_width=True, height=300)
                else:
                    st.info("No historical data available for this area")
            
            with col2:
                st.write("**Forecast & Prediction Data**")
                display_forecasts = area_forecasts[['forecast_quarter', 'forecast_price', 
                                                  'yhat_lower', 'yhat_upper', 
                                                  'growth_factor', 'growth_factor_lower', 
                                                  'growth_factor_upper', 'avg_predicted']].copy()
                display_forecasts = display_forecasts.round(4)
                st.dataframe(display_forecasts.style.format({
                    'forecast_price': '${:,.2f}',
                    'yhat_lower': '${:,.2f}',
                    'yhat_upper': '${:,.2f}',
                    'growth_factor': '{:.2%}',
                    'growth_factor_lower': '{:.2%}',
                    'growth_factor_upper': '{:.2%}',
                    'avg_predicted': '${:,.2f}'
                }), use_container_width=True, height=300)
            
            # =========================
            # PERFORMANCE SUMMARY
            # =========================
            st.subheader("🎯 Performance Summary")
            
            if not area_forecasts.empty and 'avg_actual' in area_forecasts.columns:
                perf_col1, perf_col2, perf_col3, perf_col4 = st.columns(4)
                
                with perf_col1:
                    if 'avg_actual' in area_forecasts.columns and 'avg_predicted' in area_forecasts.columns:
                        actual = area_forecasts['avg_actual'].iloc[0]
                        predicted = area_forecasts['avg_predicted'].iloc[0]
                        error_pct = ((predicted - actual) / actual) * 100
                        st.metric("Prediction Accuracy", f"{abs(error_pct):.2f}%", 
                                 delta=f"{error_pct:.2f}%", delta_color="inverse")
                
                with perf_col2:
                    latest_growth = area_forecasts['growth_factor'].iloc[0] * 100
                    st.metric("Current Growth Rate", f"{latest_growth:.2f}%")
                
                with perf_col3:
                    if 'sample_count' in area_forecasts.columns:
                        samples = area_forecasts['sample_count'].iloc[0]
                        st.metric("Test Samples", f"{samples:.0f}")
                
                with perf_col4:
                    forecast_horizon = len(area_forecasts)
                    st.metric("Forecast Periods", f"{forecast_horizon}")
        
        else:
            st.warning(f"No forecast data available for {selected_area} in selected quarters")
            
        # =========================
        # AREA COMPARISON
        # =========================
        st.sidebar.subheader("🔁 Compare Areas")
        compare_areas = st.sidebar.multiselect(
            "Select areas to compare:",
            options=available_areas,
            default=[selected_area] if selected_area in available_areas else []
        )
        
        if len(compare_areas) > 1:
            st.subheader("🔄 Multi-Area Comparison")
            
            comp_fig, (comp_ax1, comp_ax2) = plt.subplots(2, 1, figsize=(14, 10))
            
            colors = plt.cm.Set3(np.linspace(0, 1, len(compare_areas)))
            
            for i, area in enumerate(compare_areas):
                area_comp_data = forecasts_df[
                    (forecasts_df['area_name_en'] == area) & 
                    (forecasts_df['forecast_quarter'].isin(selected_forecast_quarters))
                ].sort_values('forecast_quarter')
                
                if not area_comp_data.empty:
                    # Price comparison
                    comp_ax1.plot(area_comp_data['forecast_quarter'], 
                                 area_comp_data['forecast_price'],
                                 label=area, color=colors[i], linewidth=2.5, marker='o')
                    
                    # Growth factor comparison
                    comp_ax2.plot(area_comp_data['forecast_quarter'], 
                                 area_comp_data['growth_factor'] * 100,
                                 label=area, color=colors[i], linewidth=2.5, marker='s')
            
            comp_ax1.set_xlabel('Quarter')
            comp_ax1.set_ylabel('Forecast Price ($)')
            comp_ax1.set_title('Area-wise Price Forecast Comparison')
            comp_ax1.legend()
            comp_ax1.grid(True, alpha=0.3)
            comp_ax1.tick_params(axis='x', rotation=45)
            
            comp_ax2.set_xlabel('Quarter')
            comp_ax2.set_ylabel('Growth Factor (%)')
            comp_ax2.set_title('Area-wise Growth Factor Comparison')
            comp_ax2.legend()
            comp_ax2.grid(True, alpha=0.3)
            comp_ax2.tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            st.pyplot(comp_fig)
    
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("Please ensure all data files are available in the correct format.")


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
    """Load forecasting-specific data with all growth factors"""
    try:
        # Load growth factors with all three columns
        growth_df = pd.read_csv('arima_areas_growth_6M.csv')
        
        # Check if all required columns exist
        required_growth_cols = ['ds', 'area_name_en', 'growth_factor', 'growth_factor_upper', 'growth_factor_lower']
        
        if all(col in growth_df.columns for col in required_growth_cols):
            return growth_df
        else:
            st.warning("Forecasting data missing some growth factor columns")
            return None
    except Exception as e:
        st.error(f"Error loading forecasting data: {str(e)}")
        return None

# =========================
# FILTER TRAINING DATA BY EXACT SELECTED FEATURES
# =========================
def filter_training_data_by_exact_features(train_data, selected_features, area_name):
    """Filter training data to show only properties with EXACT same features in the same area"""
    try:
        filtered_data = train_data.copy()
        
        # First filter by area
        filtered_data = filtered_data[filtered_data['area_name_en'] == area_name]
        
        # Apply filters based on EXACT selected features
        if 'rooms_en' in selected_features and selected_features['rooms_en']:
            filtered_data = filtered_data[filtered_data['rooms_en'] == selected_features['rooms_en']]
        
        if 'floor_bin' in selected_features and selected_features['floor_bin']:
            filtered_data = filtered_data[filtered_data['floor_bin'] == selected_features['floor_bin']]
        
        # Filter binary features EXACTLY
        binary_features = ['swimming_pool', 'balcony', 'elevator', 'metro', 'has_parking']
        for feature in binary_features:
            if feature in selected_features and selected_features[feature] is not None:
                filtered_data = filtered_data[filtered_data[feature] == selected_features[feature]]
        
        # Filter area within a reasonable range (±10% for exact matching)
        if 'procedure_area' in selected_features and selected_features['procedure_area']:
            area_value = selected_features['procedure_area']
            lower_bound = area_value * 0.9
            upper_bound = area_value * 1.1
            filtered_data = filtered_data[
                (filtered_data['procedure_area'] >= lower_bound) & 
                (filtered_data['procedure_area'] <= upper_bound)
            ]
        
        return filtered_data
        
    except Exception as e:
        st.warning(f"Error filtering training data: {str(e)}")
        return train_data[train_data['area_name_en'] == area_name]  # Return area data if filtering fails

# =========================
# CALCULATE TREND FOR EXACT SAME FEATURES
# =========================
def calculate_trend_for_exact_features(filtered_data, current_year):
    """Calculate trend for properties with exact same features"""
    try:
        if len(filtered_data) < 2:  # Need at least 2 data points for trend
            return None, None, None
        
        # Group by year and calculate median price
        yearly_data = filtered_data.groupby('year')['meter_sale_price'].agg(['median', 'count']).reset_index()
        yearly_data = yearly_data.rename(columns={'median': 'meter_sale_price', 'count': 'data_points'})
        
        if len(yearly_data) < 2:
            return None, None, None
        
        # Apply LOESS smoothing
        y_values = yearly_data['meter_sale_price'].values
        x_values = yearly_data['year'].values
        
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
            return trend_df, latest_trend, yearly_data
        else:
            return trend_df, None, yearly_data
            
    except Exception as e:
        st.warning(f"Could not calculate trend for exact features: {str(e)}")
        return None, None, None

# =========================
# CREATE COMBINED TREND AND FORECAST PLOT WITH ALL GROWTH FACTORS
# =========================
def create_combined_trend_forecast_plot(historical_data, trend_data, current_price, forecast_data, area_name, selected_features):
    """Create a combined plot showing historical trend for exact features and future forecast with confidence intervals"""
    
    fig = go.Figure()
    current_year = datetime.now().year
    
    # Add historical data points (EXACT same features)
    if historical_data is not None and len(historical_data) > 0:
        # Add individual data points
        fig.add_trace(go.Scatter(
            x=historical_data['year'],
            y=historical_data['meter_sale_price'],
            mode='markers',
            name=f'Historical Properties (Exact Features)',
            marker=dict(color='blue', size=8, opacity=0.7),
            hovertemplate='Year: %{x}<br>Price: AED %{y:,.0f}<br>Data Points: %{customdata}<extra></extra>',
            customdata=historical_data['data_points']
        ))
    
    # Add LOESS trend line for exact features
    if trend_data is not None and len(trend_data) > 0:
        fig.add_trace(go.Scatter(
            x=trend_data['year'],
            y=trend_data['smoothed_price'],
            mode='lines',
            name='Historical Trend (Exact Features)',
            line=dict(color='red', width=3),
            hovertemplate='Year: %{x}<br>Trend Price: AED %{y:,.0f}<extra></extra>'
        ))
    
    # Add current prediction point
    fig.add_trace(go.Scatter(
        x=[current_year],
        y=[current_price],
        mode='markers',
        name='Current Prediction',
        marker=dict(color='green', size=15, symbol='star'),
        hovertemplate='Current Prediction<br>Price: AED %{y:,.0f}<extra></extra>'
    ))
    
    # Add forecast data with confidence intervals
    if forecast_data is not None and len(forecast_data) > 0:
        forecast_years = []
        forecast_main = []
        forecast_upper = []
        forecast_lower = []
        
        # Sort forecast data by period to ensure chronological order
        sorted_periods = sorted(forecast_data.keys())
        
        for i, period in enumerate(sorted_periods):
            growth_factors = forecast_data[period]
            forecast_year = current_year + (i + 1) * 0.25  # Quarterly increments
            
            forecast_years.append(forecast_year)
            forecast_main.append(current_price * growth_factors['main'])
            forecast_upper.append(current_price * growth_factors['upper'])
            forecast_lower.append(current_price * growth_factors['lower'])
        
        # Add confidence interval area
        fig.add_trace(go.Scatter(
            x=forecast_years + forecast_years[::-1],
            y=forecast_upper + forecast_lower[::-1],
            fill='toself',
            fillcolor='rgba(255,165,0,0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            name='Forecast Confidence Interval',
            showlegend=True,
            hoverinfo='skip'
        ))
        
        # Add main forecast line
        fig.add_trace(go.Scatter(
            x=forecast_years,
            y=forecast_main,
            mode='lines+markers',
            name='Future Forecast (Main)',
            line=dict(color='orange', width=3),
            marker=dict(color='orange', size=8),
            hovertemplate='Year: %{x:.2f}<br>Forecast: AED %{y:,.0f}<extra></extra>'
        ))
        
        # Add upper bound line
        fig.add_trace(go.Scatter(
            x=forecast_years,
            y=forecast_upper,
            mode='lines',
            name='Forecast Upper Bound',
            line=dict(color='orange', width=1, dash='dash'),
            opacity=0.7,
            hovertemplate='Year: %{x:.2f}<br>Upper Bound: AED %{y:,.0f}<extra></extra>'
        ))
        
        # Add lower bound line
        fig.add_trace(go.Scatter(
            x=forecast_years,
            y=forecast_lower,
            mode='lines',
            name='Forecast Lower Bound',
            line=dict(color='orange', width=1, dash='dash'),
            opacity=0.7,
            hovertemplate='Year: %{x:.2f}<br>Lower Bound: AED %{y:,.0f}<extra></extra>'
        ))
    
    # Create feature description for title
    feature_desc = f"{selected_features['rooms_en']}, {selected_features['floor_bin']}, {selected_features['procedure_area']} sqMt"
    
    # Update layout
    fig.update_layout(
        title=f"Price Timeline - {area_name}<br><sub>Features: {feature_desc}</sub>",
        xaxis_title="Year",
        yaxis_title="Price (AED)",
        height=500,
        template="plotly_white",
        hovermode='closest',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

# =========================
# PREPARE FORECAST DATA WITH ALL GROWTH FACTORS
# =========================
def prepare_forecast_data(growth_pivot, area_name):
    """Prepare forecast data with all three growth factors"""
    if growth_pivot is None:
        return None
    
    try:
        # Filter growth data for the selected area
        area_growth = growth_pivot[growth_pivot['area_name_en'] == area_name]
        
        if area_growth.empty:
            return None
        
        # Get unique periods (ds values)
        periods = area_growth['ds'].unique()
        
        forecast_data = {}
        
        for period in periods:
            period_data = area_growth[area_growth['ds'] == period].iloc[0]
            
            forecast_data[period] = {
                'main': period_data['growth_factor'],
                'upper': period_data['growth_factor_upper'],
                'lower': period_data['growth_factor_lower']
            }
        
        return forecast_data
        
    except Exception as e:
        st.warning(f"Error preparing forecast data: {str(e)}")
        return None

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
                    # FILTER TRAINING DATA BY EXACT SAME FEATURES
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
                    
                    exact_features_data = None
                    if train_data is not None:
                        exact_features_data = filter_training_data_by_exact_features(
                            train_data, selected_features, area_name
                        )
                        
                        st.subheader("📊 Historical Data with Exact Same Features")
                        st.write(f"Found {len(exact_features_data)} historical properties with EXACT same features in {area_name}")
                        
                        if len(exact_features_data) > 0:
                            # Show summary of the filtered data
                            st.dataframe(exact_features_data[['instance_date', 'meter_sale_price', 'rooms_en', 'floor_bin', 'procedure_area']].head(10))
                    
                    # =========================
                    # CALCULATE TREND FOR EXACT SAME FEATURES
                    # =========================
                    current_year = datetime.now().year
                    trend_df = None
                    historical_yearly = None
                    
                    if exact_features_data is not None and len(exact_features_data) > 0:
                        trend_df, latest_trend, historical_yearly = calculate_trend_for_exact_features(
                            exact_features_data, current_year
                        )
                    
                    # =========================
                    # PREPARE FORECAST DATA WITH ALL GROWTH FACTORS
                    # =========================
                    forecast_data = prepare_forecast_data(growth_pivot, area_name)
                    
                    # =========================
                    # CREATE COMBINED PLOT WITH CONFIDENCE INTERVALS
                    # =========================
                    st.subheader("📈 Price Timeline: Historical Trend (Exact Features) + Forecast")
                    
                    combined_fig = create_combined_trend_forecast_plot(
                        historical_yearly, 
                        trend_df, 
                        predicted_price, 
                        forecast_data, 
                        area_name,
                        selected_features
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
                    # DISPLAY FORECAST TABLE WITH ALL GROWTH FACTORS
                    # =========================
                    if forecast_data:
                        st.subheader("🔮 Future Price Forecast with Confidence Intervals")
                        st.write("Future prices calculated as: Prediction × Growth Factor")
                        
                        forecast_table_data = []
                        cumulative_price_main = predicted_price
                        cumulative_price_upper = predicted_price
                        cumulative_price_lower = predicted_price
                        
                        # Sort periods chronologically
                        sorted_periods = sorted(forecast_data.keys())
                        
                        for period in sorted_periods:
                            growth_factors = forecast_data[period]
                            
                            cumulative_price_main = cumulative_price_main * growth_factors['main']
                            cumulative_price_upper = cumulative_price_upper * growth_factors['upper']
                            cumulative_price_lower = cumulative_price_lower * growth_factors['lower']
                            
                            forecast_table_data.append({
                                'Period': period,
                                'Main Growth Factor': f"{growth_factors['main']:.4f}",
                                'Upper Growth Factor': f"{growth_factors['upper']:.4f}",
                                'Lower Growth Factor': f"{growth_factors['lower']:.4f}",
                                'Forecasted Price (Main)': f"AED {cumulative_price_main:,.0f}",
                                'Forecasted Price (Upper)': f"AED {cumulative_price_upper:,.0f}",
                                'Forecasted Price (Lower)': f"AED {cumulative_price_lower:,.0f}"
                            })
                        
                        forecast_df = pd.DataFrame(forecast_table_data)
                        st.table(forecast_df)
                    
                    # =========================
                    # DISPLAY TREND ANALYSIS FOR EXACT FEATURES
                    # =========================
                    if trend_df is not None and latest_trend is not None:
                        st.subheader("📊 Trend Analysis for Exact Features")
                        
                        # Calculate trend direction and percentage difference
                        price_diff = predicted_price - latest_trend
                        price_diff_percent = (price_diff / latest_trend) * 100
                        
                        if price_diff > 0:
                            trend_direction = "increased"
                            trend_color = "green"
                        else:
                            trend_direction = "decreased"
                            trend_color = "red"
                        
                        st.info(f"""
                        **Historical Trend Analysis:**
                        - Based on **{len(exact_features_data)}** properties with **exact same features** in {area_name}
                        - Historical trend shows similar properties were around **AED {latest_trend:,.0f}**
                        - Current prediction shows a **{abs(price_diff_percent):.1f}% {trend_direction}** from historical trend
                        - This indicates the market value for these specific features has **{trend_direction}** over time
                        """)
                    
                    elif exact_features_data is not None and len(exact_features_data) > 0:
                        st.warning(f"⚠️ Found {len(exact_features_data)} properties with similar features, but insufficient data for trend analysis.")
                    else:
                        st.warning("⚠️ No historical data found with exact same features. The prediction is based on the model training.")
                    
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
    if growth_pivot is not None:
        st.sidebar.write(f"Growth data columns: {list(growth_pivot.columns)}")
