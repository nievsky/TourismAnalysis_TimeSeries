import pandas as pd
import numpy as np
import pmdarima as pm
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import warnings

warnings.filterwarnings("ignore")

# 1. Load Data
notebook_path = r'C:\Users\alecs\My Drive\UJEP\CAS\Seminar\seminarni_prace.ipynb'
# Assuming we can just re-run the data loading part
dataset_codes = ["tour_occ_nim", "tour_occ_arm"]
countries = ["CZ", "DE", "AT", "SK", "PL"]
resid_categories = ["TOTAL", "DOM", "FOR"]
# Actually, since it takes time to download, let's just grab it from a local run or just simulate the exact steps.
# To save time, I will download it again or use a simpler way if I can.
import requests
EUROSTAT_BASE_URL = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/{dataset_code}"
def fetch_eurostat_series(dataset_code, geo, c_resid):
    params = {"format": "JSON", "lang": "en", "freq": "M", "unit": "NR", "nace_r2": "I551-I553", "geo": geo, "c_resid": c_resid, "sinceTimePeriod": "2013-01"}
    response = requests.get(EUROSTAT_BASE_URL.format(dataset_code=dataset_code), params=params, timeout=60)
    payload = response.json()
    time_index = payload["dimension"]["time"]["category"]["index"]
    months = [month for month, _ in sorted(time_index.items(), key=lambda item: item[1])]
    values = payload.get("value", {})
    row = {"geo": geo, "c_resid": c_resid}
    for position, month in enumerate(months):
        row[month] = values.get(str(position), np.nan)
    return row

nights_raw = [fetch_eurostat_series("tour_occ_nim", geo, c_resid) for c_resid in resid_categories for geo in countries]
arrivals_raw = [fetch_eurostat_series("tour_occ_arm", geo, c_resid) for c_resid in resid_categories for geo in countries]

def wide_to_long_and_pivot(raw, prefix):
    df = pd.DataFrame(raw)
    date_cols = [c for c in df.columns if '-' in c]
    long_df = df.melt(id_vars=["geo", "c_resid"], value_vars=date_cols, var_name="date", value_name="value")
    long_df["date"] = pd.to_datetime(long_df["date"])
    long_df["value"] = pd.to_numeric(long_df["value"])
    pivot = long_df.pivot_table(index="date", columns=["geo", "c_resid"], values="value", aggfunc="first")
    pivot.columns = [f"{prefix}_{geo}_{resid.lower()}" for geo, resid in pivot.columns]
    return pivot.sort_index()

nights_pivot = wide_to_long_and_pivot(nights_raw, "nights")
arrivals_pivot = wide_to_long_and_pivot(arrivals_raw, "arrivals")
data = pd.concat([nights_pivot, arrivals_pivot], axis=1).asfreq("MS")
last_main = data["nights_CZ_total"].last_valid_index()
data = data.loc[:last_main]
data_clean = data.interpolate(method="time").ffill().bfill()
y = data_clean["nights_CZ_total"]

# --- Q2: Holt Winters ---
hw_model = ExponentialSmoothing(y, trend="add", seasonal="add", seasonal_periods=12, initialization_method="estimated")
hw_fit = hw_model.fit()
print("=== Q2: Holt-Winters Parameters ===")
print(hw_fit.params_formatted)
print("AIC:", hw_fit.aic)

# --- Q5: ACF of residuals of best deterministic model ---
model_df = pd.DataFrame({"y": y})
model_df["t"] = np.arange(1, len(model_df) + 1)
model_df["t2"] = model_df["t"] ** 2
model_df["month"] = model_df.index.month.astype(str)
model_df["covid"] = ((model_df.index >= "2020-03-01") & (model_df.index <= "2021-12-01")).astype(int)
for k in range(1, 6):
    model_df[f"sin_{k}"] = np.sin(2 * np.pi * k * model_df["t"] / 12)
    model_df[f"cos_{k}"] = np.cos(2 * np.pi * k * model_df["t"] / 12)

fourier_terms = " + ".join([f"sin_{k} + cos_{k}" for k in range(1, 6)])
formula = f"y ~ t + I(t**2) + covid + {fourier_terms}"
fit = smf.ols(formula=formula, data=model_df).fit()
acf_vals = sm.tsa.acf(fit.resid, nlags=15)
print("\n=== Q5: ACF of Deterministic Model ===")
print("ACF vals (lag 0-15):", acf_vals)

# --- Q6: SARIMA Equation ---
# Use the order the notebook found
# Based on the text, it selected a seasonal model. I need to run auto_arima to be sure, or check the text.
sarima_auto = pm.auto_arima(y, seasonal=True, m=12, start_p=0, start_q=0, max_p=3, max_q=3, start_P=0, start_Q=0, max_P=2, max_Q=2, d=None, D=None, trace=False, error_action="ignore", suppress_warnings=True, stepwise=True, information_criterion="aic")
order = sarima_auto.order
seasonal_order = sarima_auto.seasonal_order
print("\n=== Q6: SARIMA Order ===")
print("Order:", order, "Seasonal Order:", seasonal_order)
sarima_fit = SARIMAX(y, order=order, seasonal_order=seasonal_order, enforce_stationarity=False, enforce_invertibility=False).fit(disp=False)
print("Coefficients:")
print(sarima_fit.params)

# --- Q7: SARIMAX Coefficients ---
exog_cols = ["nights_DE_total", "nights_PL_total", "nights_SK_total"]
X = data_clean[exog_cols]
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_scaled = pd.DataFrame(scaler.fit_transform(X), index=X.index, columns=exog_cols)
# Notebook used SARIMAX with order=(2, 0, 0), seasonal_order=(0, 0, 2, 12)
sarimax_fit = SARIMAX(y, exog=X_scaled, order=(2,0,0), seasonal_order=(0,0,2,12), trend="c", enforce_stationarity=False, enforce_invertibility=False).fit(disp=False)
print("\n=== Q7: SARIMAX Params ===")
print(sarimax_fit.summary().tables[1])
