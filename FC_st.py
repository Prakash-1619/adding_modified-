import numpy as np
import pandas as pd
import pmdarima as pm
from statsmodels.nonparametric.smoothers_lowess import lowess
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error, r2_score
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

# ------------------------------
# CONFIG
# ------------------------------
horizon_months = 6
seasonal_m = 12
min_length = 18
lowess_frac = 0.25

metrics_list = []
predictions_store = []
model_summaries = {}

monthly_df["month"] = pd.to_datetime(monthly_df["month"])

# ------------------------------
# HELPER FUNCTION
# ------------------------------
def safe_metrics(y_true, y_pred):
    mae = mean_absolute_error(y_true, y_pred)
    mape = mean_absolute_percentage_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    return mae, mape, rmse, r2

# ------------------------------
# LOOP OVER AREAS
# ------------------------------
for area_name, df_area in monthly_df.groupby("area_name_en"):
    df_area = df_area.sort_values("month").dropna(subset=["median_price"]).reset_index(drop=True)
    if len(df_area) < min_length or df_area["median_price"].std() == 0:
        print(f"⚠️ Skipping {area_name}: insufficient data.")
        continue

    # LOWESS smoothing
    y = df_area["median_price"].values
    x = np.arange(len(y))
    df_area["actual_smoothed"] = lowess(y, x, frac=lowess_frac, return_sorted=False)

    # Train/Test split
    train, test = df_area.iloc[:-horizon_months], df_area.iloc[-horizon_months:]

    # SARIMA fit
    try:
        sarima_model = pm.auto_arima(
            train["actual_smoothed"].astype(float),
            start_p=0, start_q=0, max_p=5, max_q=5,
            d=None, D=None,
            seasonal=True, m=seasonal_m,
            start_P=0, start_Q=0, max_P=2, max_Q=2,
            stepwise=True, suppress_warnings=True,
            trace=False, error_action="ignore"
        )
    except Exception as e:
        print(f"❌ {area_name}: model fit failed → {e}")
        continue

    # Save model summary as string
    model_summaries[area_name] = str(sarima_model.summary())

    # Extract orders
    try:
        p, d, q = sarima_model.order
        P, D, Q, m = sarima_model.seasonal_order
    except Exception:
        p, d, q, P, D, Q, m = [np.nan]*7

    # Train fitted
    try:
        fitted = pd.Series(sarima_model.arima_res_.fittedvalues, index=train.index)
    except:
        fitted = pd.Series(sarima_model.predict_in_sample(), index=train.index)

    offset = max(1, (d or 0) + (D or 0) * (m or seasonal_m))
    fitted.iloc[:offset] = np.nan
    fitted.interpolate(method="linear", inplace=True)
    fitted.fillna(method="bfill", inplace=True)

    # Test prediction
    test_pred = pd.Series(sarima_model.predict(n_periods=len(test)), index=test.index)

    # Future forecast
    full_series = df_area["actual_smoothed"].astype(float)
    try:
        sarima_full = pm.auto_arima(
            full_series,
            start_p=0, start_q=0, max_p=5, max_q=5,
            d=d, D=D,
            seasonal=True, m=seasonal_m,
            start_P=0, start_Q=0, max_P=2, max_Q=2,
            stepwise=True, suppress_warnings=True,
            trace=False, error_action="ignore"
        )
    except:
        sarima_full = sarima_model

    future_fore = sarima_full.predict(n_periods=horizon_months)
    future_dates = pd.date_range(df_area["month"].iloc[-1] + pd.offsets.MonthBegin(1),
                                 periods=horizon_months, freq="MS")

    # ------------------------------
    # METRICS
    # ------------------------------
    train_mae, train_mape, train_rmse, train_r2 = safe_metrics(train["actual_smoothed"], fitted)
    test_mae, test_mape, test_rmse, test_r2 = safe_metrics(test["actual_smoothed"], test_pred)

    metrics_list.append({
        "Area": area_name,
        "p": p, "d": d, "q": q, "P": P, "D": D, "Q": Q, "m": m,
        "Train_MAE": train_mae, "Train_MAPE": train_mape,
        "Train_RMSE": train_rmse, "Train_R2": train_r2,
        "Test_MAE": test_mae, "Test_MAPE": test_mape,
        "Test_RMSE": test_rmse, "Test_R2": test_r2
    })

    # ------------------------------
    # STORE FORECASTS
    # ------------------------------
    train_df = pd.DataFrame({
        "area": area_name, "phase": "train",
        "month": train["month"], "actual_smoothed": train["actual_smoothed"], "predicted": fitted
    })
    test_df = pd.DataFrame({
        "area": area_name, "phase": "test",
        "month": test["month"], "actual_smoothed": test["actual_smoothed"], "predicted": test_pred
    })
    future_df = pd.DataFrame({
        "area": area_name, "phase": "forecast",
        "month": future_dates, "actual_smoothed": np.nan, "predicted": future_fore
    })
    all_df = pd.concat([train_df, test_df, future_df], ignore_index=True)
    predictions_store.append(all_df)

    # ------------------------------
    # SCATTER PLOTS
    # ------------------------------
    for phase, x_vals, y_vals in [("Train", train["actual_smoothed"], fitted),
                                  ("Test", test["actual_smoothed"], test_pred)]:
        r2_val = r2_score(x_vals, y_vals)
        plt.figure(figsize=(6,6))
        plt.scatter(x_vals, y_vals, alpha=0.7)
        plt.plot([x_vals.min(), x_vals.max()], [x_vals.min(), x_vals.max()], "r--")
        plt.xlabel("Actual (LOWESS)")
        plt.ylabel("Predicted")
        plt.title(f"{area_name} - {phase} Scatter Plot\nR²={r2_val:.4f}")
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.show()

# ------------------------------
# SAVE ALL TABLES
# ------------------------------
forecast_df = pd.concat(predictions_store, ignore_index=True)
forecast_df.to_csv("forecast_lowess_all_areas.csv", index=False)

metrics_df = pd.DataFrame(metrics_list)
metrics_cols = ["Area", "Train_MAE", "Train_MAPE", "Train_RMSE", "Train_R2",
                "Test_MAE", "Test_MAPE", "Test_RMSE", "Test_R2",
                "p", "d", "q", "P", "D", "Q", "m"]
metrics_df = metrics_df[metrics_cols]
metrics_df.to_csv("metrics_lowess_all_areas.csv", index=False)

# Optional: save model summaries as CSV
model_summary_df = pd.DataFrame({
    "Area": list(model_summaries.keys()),
    "SARIMA_Summary": list(model_summaries.values())
})
model_summary_df.to_csv("sarima_model_summary_all_areas.csv", index=False)

print("✅ Forecast, metrics, and model summaries saved successfully!")
