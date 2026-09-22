# Finding the Optimal Model for the Time Series of Tourist Nights Spent in the Czech Republic

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Jupyter Notebook](https://img.shields.io/badge/jupyter-notebook-orange.svg)](https://jupyter.org/)
[![Eurostat API](https://img.shields.io/badge/data-Eurostat%20API-green.svg)](https://ec.europa.eu/eurostat)
[![statsmodels](https://img.shields.io/badge/econometrics-statsmodels-informational.svg)](https://www.statsmodels.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Term Paper for the **Time Series** Course  
**Jan Evangelista Purkyně University in Ústí nad Labem (UJEP)**  
**Main Analyzed Time Series:** `nights_CZ_total` – monthly number of nights spent by guests in collective accommodation establishments in the Czech Republic (January 2013 – February 2026).

---

## 📋 Executive Summary

The objective of this project is a systematic econometric and statistical analysis of the monthly time series of tourist nights spent in the Czech Republic, identifying its deterministic and stochastic properties, and finding an optimal forecasting model. The analyzed series is characterized by:
1. **Long-term non-linear trend** (stable growth prior to 2020, severe structural shock during the COVID-19 pandemic in 2020–2021, and post-pandemic recovery).
2. **Pronounced and asymmetric annual seasonality** with a sharp summer peak in July and August (>8 million nights spent) and deep winter troughs (~2.5–3.5 million nights spent).
3. **Significant temporal dependence and autocorrelation**.

A hierarchy of models is systematically constructed and compared throughout the project:
- **Deterministic regression models** (polynomial trend + monthly dummies + COVID intervention + harmonic Fourier regression $K=1 \dots 5$).
- **Univariate stochastic model** $SARIMA(2,0,0)(0,0,2)_{12}$.
- **Cross-correlation analysis (CCF)** with trend and seasonal prewhitening for 9 tourist series of neighboring countries (DE, PL, SK, AT).
- **Multivariate model** $SARIMAX$ with an optimal combination of external night spent series (Germany, Poland, Slovakia).
- **Spectral analysis using a periodogram** to verify dominant periodicities.
- **Comprehensive residual diagnostics** (ACF, Ljung-Box tests at lags 12, 24, and 36 months, RMSE, AIC/BIC).
- **10-month forecast** (March 2026 – December 2026) including 95% confidence and prediction intervals.

### 🏆 Key Model Comparison Results

| Model | Description / Specification | AIC Source | AIC | BIC | RMSE | Ljung-Box $p$ (lag 12) | Ljung-Box $p$ (lag 24) |
|---|---|---|---|---|---|---|---|
| **Fourier Regression** | Quadratic polynomial + COVID + Fourier $K=5$ | OLS | 4,636.85 | 4,679.73 | 522,320 | 0.000 | 0.000 |
| **SARIMA** | $SARIMA(2,0,0)(0,0,2)_{12}$ | SARIMAX refit | 4,038.25 | 4,052.70 | 732,597 | 0.010 | 0.000 |
| **SARIMAX (Winner)** | Exog: DE, PL, SK nights + $SARIMA(2,0,0)(0,0,2)_{12}$ | SARIMAX | **3,663.14** | **3,689.15** | **206,263** | **0.065** | 0.006 |

> **Conclusion:** **SARIMAX with external series of nights spent in Germany, Poland, and Slovakia** was selected as the clear best-performing model. It achieved the lowest information criteria ($AIC = 3,663.14$), the lowest error ($RMSE = 206,263$), and was the only model to pass the Ljung-Box test at annual lag 12 ($p = 0.065 > 0.05$), demonstrating its ability to capture cross-border tourism dynamics in Central Europe.

---

## 📑 Table of Contents

1. [Introduction and Project Objective](#1-introduction-and-project-objective)
2. [Data and Data Preparation](#2-data-and-data-preparation)
3. [Graphical Analysis of the Main Series](#3-graphical-analysis-of-the-main-series)
4. [Decomposition and Trend Smoothing](#4-decomposition-and-trend-smoothing)
5. [Regression Models: Trend and Seasonality](#5-regression-models-trend-and-seasonality)
6. [SARIMA Model for the Individual Series](#6-sarima-model-for-the-individual-series)
7. [Cross-Correlation with Other Time Series](#7-cross-correlation-with-other-time-series)
8. [SARIMAX with External Regressors](#8-sarimax-with-external-regressors)
9. [Period Check, Diagnostics, and Forecasting](#9-period-check-diagnostics-and-forecasting)
   - [9.1 Period Verification Using the Periodogram](#91-period-verification-using-the-periodogram)
   - [9.2 Summary Residual Diagnostics](#92-summary-residual-diagnostics)
   - [9.3 10-Step-Ahead Forecast](#93-10-step-ahead-forecast)
10. [Final Comparison and Evaluation](#10-final-comparison-and-evaluation)

---

## 1. Introduction and Project Objective

The goal of this project is to identify a suitable econometric model for the monthly time series of tourist nights spent in the Czech Republic. The series represents an ideal case study of real-world economic data:
- It features a pronounced and stable **annual seasonality** peaking during the summer months.
- It exhibits a long-term **trend** that was disrupted by a severe shock during the COVID-19 pandemic (March 2020 to December 2021).
- It displays stochastic memory requiring the modeling of error component dependencies.

The analysis proceeds through 10 methodological steps, ranging from exploratory graphical analysis and decomposition to deterministic regression, SARIMA models, cross-correlations, and a final SARIMAX model providing a 10-month forecast.

---

## 2. Data and Data Preparation

Data are retrieved directly from the official **Eurostat Dissemination API** across two key datasets:
- `tour_occ_nim`: nights spent in collective accommodation establishments (*nights spent*),
- `tour_occ_arm`: arrivals of residents and non-residents at collective accommodation establishments (*arrivals*).

The geographical scope covers the Czech Republic and neighboring countries in the Central European region: **Czech Republic (`CZ`), Germany (`DE`), Austria (`AT`), Slovakia (`SK`), and Poland (`PL`)**, categorized by total guests (`TOTAL`), domestic guests (`DOM`), and non-residents/foreigners (`FOR`).

### Overview of Data Dimensions and Cleaning

Eurostat provides data in a wide format. The code implements a transformation into long format (*melt*), followed by pivoting into a monthly matrix aligned to a monthly start frequency (`MS`).

```python
# Key Eurostat download parameters
dataset_codes = ["tour_occ_nim", "tour_occ_arm"]
countries = ["CZ", "DE", "AT", "SK", "PL"]
resid_categories = ["TOTAL", "DOM", "FOR"]
since_time_period = "2013-01"
```

| Metric | Value | Note |
|---|---|---|
| **Number of months** | 158 | From January 2013 (`2013-01-01`) to February 2026 (`2026-02-01`) |
| **Number of retrieved series** | 30 | 5 countries $\times$ 3 categories $\times$ 2 indicators |
| **Missing values in the main series (`nights_CZ_total`)** | **0** | Main series is 100% complete without gaps |
| **Missing values in auxiliary series** | 2 | Handled via linear time interpolation |

---

## 3. Graphical Analysis of the Main Series

Prior to modeling, a visual inspection of the `nights_CZ_total` series (in millions of nights spent) was conducted.

![Monthly Tourist Nights Spent in the Czech Republic](images/plot_1.png)

### Seasonal Profile and Distribution of Values

To thoroughly evaluate seasonal behavior, the average monthly nights spent were calculated alongside a boxplot depicting variability across calendar months:

![Seasonal Profile: Monthly Mean and Distribution](images/plot_2.png)

### 💡 Graphical Analysis Interpretation:
1. **Long-term evolution:** Up to 2019, the series exhibited stable upward growth. During 2020–2021, a sharp decline occurred due to border closures and accommodation shutdowns during COVID-19. Starting in 2022, a systematic return toward pre-crisis levels is observed.
2. **Seasonal pattern:** The annual cycle features an asymmetric shape. The peak occurs in July and August (averaging over 7–8 million nights spent), while November, January, and February are the lowest months (approx. 2.5–3.5 million).
3. **Modeling implications:** Due to the sharp summer peak, a simple sine wave is insufficient for modeling seasonality; higher harmonics (Fourier series) or seasonal difference/lag operators are required.

---

## 4. Decomposition and Trend Smoothing

The time series was decomposed into trend-cycle, seasonal, and residual components using **robust STL decomposition** (Seasonal-Trend decomposition using LOESS) with period $s = 12$. Choosing a robust algorithm prevents the trend from being distorted by pandemic outlier observations.

![STL Decomposition of Nights Spent in the Czech Republic](images/plot_3.png)

To verify trend identification, a symmetric centered 12-month moving average ($2 \times 12$ MA) was applied:

![Trend Identification via 12-Month Moving Average](images/plot_4.png)

### 💡 Decomposition Interpretation:
- **Seasonal component:** Demonstrates high stability with constant amplitude and an invariant profile across the entire 13-year span.
- **Trend component:** Both STL and the $2 \times 12$ MA accurately reflect the structural break in 2020. The pandemic shock was not a seasonal fluctuation, but a deep contraction of the underlying trend.
- **Residual component:** Remains in a narrow band around zero in normal years, but exhibits large deviations during 2020–2021, confirming the necessity of an intervention term for the COVID period in regression models.

---

## 5. Regression Models: Trend and Seasonality

In the initial modeling stage, deterministic models capturing trend, calendar seasonality, and the pandemic intervention effect were tested.

### Tested Specifications:
1. **Model 1 (M1):** Linear trend + monthly dummy variables.
2. **Model 2 (M2):** Quadratic trend ($t + t^2$) + monthly dummy variables.
3. **Model 3 (M3):** Quadratic trend + monthly dummy variables + COVID dummy intervention (1 during 2020-03 to 2021-12, 0 otherwise).
4. **Fourier Models ($K = 1 \dots 5$):** Quadratic trend + COVID intervention + Fourier harmonic terms:
   $$y_t = \beta_0 + \beta_1 t + \beta_2 t^2 + \gamma \cdot \text{covid}_t + \sum_{k=1}^{K} \left[ \alpha_k \sin\left(\frac{2\pi k t}{12}\right) + \beta_k \cos\left(\frac{2\pi k t}{12}\right) \right] + \epsilon_t$$

### Comparison of Deterministic Models

| Model | AIC | BIC | Adj. $R^2$ | RMSE | Ljung-Box $p$ (lag 12) |
|---|---|---|---|---|---|
| **Fourier_K5** | **4,636.85** | **4,679.73** | **0.911** | **522,320** | 0.000000 |
| M3_quadratic_trend_month_dummies_covid | 4,638.80 | 4,684.74 | 0.910 | 522,242 | 0.000000 |
| Fourier_K4 | 4,660.71 | 4,697.46 | 0.895 | 570,454 | 0.000000 |
| Fourier_K3 | 4,683.34 | 4,713.96 | 0.877 | 620,611 | 0.000000 |
| Fourier_K2 | 4,727.13 | 4,751.63 | 0.836 | 721,950 | 0.000000 |
| M2_quadratic_trend_month_dummies | 4,800.17 | 4,843.05 | 0.749 | 875,772 | 0.000000 |
| M1_linear_trend_month_dummies | 4,803.56 | 4,843.38 | 0.742 | 890,850 | 0.000000 |
| Fourier_K1 | 4,825.54 | 4,843.91 | 0.691 | 998,260 | 0.000000 |

The best-performing deterministic model was **`Fourier_K5`**. Its estimated coefficients are presented below:

| Variable | Coefficient | $p$-value | Statistical Significance |
|---|---|---|---|
| $t$ (linear trend) | $+18,297.22$ | $< 0.001$ | Significant at the 1% level |
| $t^2$ (quadratic trend) | $-63.91$ | $0.012$ | Significant at the 5% level |
| $\text{covid}$ (intervention) | $-2,225,520.94$ | $< 0.001$ | Average monthly decline of 2.23M nights spent |
| $\sin_1$ | $-1,284,266.76$ | $< 0.001$ | Significant |
| $\cos_1$ | $-1,415,251.91$ | $< 0.001$ | Significant |
| $\sin_2$ | $+972,062.32$ | $< 0.001$ | Significant |
| $\cos_2$ | $-111,554.72$ | $0.073$ | Marginally significant |
| $\sin_3$ | $-381,946.11$ | $< 0.001$ | Significant |
| $\cos_3$ | $+358,055.07$ | $< 0.001$ | Significant |
| $\sin_4$ | $-32,651.51$ | $0.596$ | Not significant |
| $\cos_4$ | $-346,084.70$ | $< 0.001$ | Significant |
| $\sin_5$ | $+162,639.33$ | $0.009$ | Significant |
| $\cos_5$ | $+282,480.05$ | $< 0.001$ | Significant |

### Fit Plot and Residual Diagnostics of the Deterministic Model

![Observed Series and Best Deterministic Regression Model (Fourier K5)](images/plot_5.png)
![ACF of Best Deterministic Model Residuals (Fourier K5)](images/plot_6.png)

### ⚠️ Why Does the Deterministic Model Fall Short?
Although the model achieves a high $R^2_{adj} = 0.911$, **the residual ACF and Ljung-Box test unequivocally reject the white noise hypothesis ($p = 0.000000$)**:
1. Strong autocorrelation at lag 1 ($r_1 \approx 0.68$).
2. Significant seasonal peak at lag 12 ($r_{12} \approx 0.31$).
Residuals retain systematic stochastic information that standard regression cannot capture, providing strong justification for **ARIMA/SARIMA** models.

---

## 6. SARIMA Model for the Individual Series

To capture intrinsic autocorrelation memory and seasonal dependency, a univariate SARIMA model was investigated.

### ACF and PACF Analysis

![ACF and PACF of Original and Seasonally Differenced Series](images/plot_7.png)

1. The ACF of the original series decays slowly with pronounced seasonal waves at period 12.
2. After seasonal differencing $\nabla_{12} Y_t = Y_t - Y_{t-12}$, stationarity improves, though significant spikes at seasonal multiples remain in the ACF.

### Model Order Selection

The `pmdarima.auto_arima` algorithm with seasonal step `m=12` identified the optimal structure:
$$\mathbf{SARIMA(2, 0, 0)(0, 0, 2)_{12}}$$

The model was subsequently refitted in `statsmodels.tsa.statespace.sarimax.SARIMAX`:
- **Selected order:** $p=2, d=0, q=0$ and $P=0, D=0, Q=2, s=12$
- **Information criteria:** $AIC = 4,038.246$, $BIC = 4,052.698$

### Mathematical Equation of the Estimated Model:
$$(1 - \phi_1 B - \phi_2 B^2) Y_t = (1 + \Theta_1 B^{12} + \Theta_2 B^{24}) \epsilon_t$$

Substituting estimated parameters:
$$Y_t = 1.186 \cdot Y_{t-1} - 0.257 \cdot Y_{t-2} + \epsilon_t + 0.766 \cdot \epsilon_{t-12} + 0.612 \cdot \epsilon_{t-24}$$

| Parameter | Coefficient | Std. Error | $p$-value | Interpretation |
|---|---|---|---|---|
| `ar.L1` ($\phi_1$) | $+1.186$ | $0.290$ | $< 0.001$ | Strong positive momentum from previous month |
| `ar.L2` ($\phi_2$) | $-0.257$ | $0.274$ | $0.349$ | Damping effect of second lag |
| `ma.S.L12` ($\Theta_1$) | $+0.766$ | $0.172$ | $< 0.001$ | Strong year-over-year memory of shocks |
| `ma.S.L24` ($\Theta_2$) | $+0.612$ | $0.168$ | $< 0.001$ | Two-year seasonal memory of shocks |
| $\sigma^2$ | $1.626 \times 10^{12}$ | - | $< 0.001$ | White noise variance |

### SARIMA Fit Plot and Residual Diagnostics

During diagnostics, the first 24 observations were excluded (*burn-in period*) due to Kalman filter initialization in state-space estimation.

![Observed Series and Fitted Values of SARIMA Model](images/plot_8.png)
![Residuals and Residual ACF of SARIMA Model](images/plot_9.png)

| Lag | Ljung-Box Statistic ($Q$) | $p$-value |
|---|---|---|
| **12** | $26.276$ | $0.010$ |
| **24** | $57.366$ | $< 0.001$ |
| **36** | $115.797$ | $< 0.001$ |

### 💡 SARIMA Model Evaluation:
The SARIMA model yields a dramatic improvement in information criteria (AIC dropped from 4,636 to 4,038). Nevertheless, the Ljung-Box test at lag 12 ($p = 0.010 < 0.05$) indicates that unexplained autocorrelation persists in the residuals. Internal history alone is insufficient.

---

## 7. Cross-Correlation with Other Time Series

To evaluate whether external information could enhance model performance, cross-correlation function (CCF) analysis was conducted. To avoid spurious correlation arising from shared trend and seasonality, **all series were first detrended, deseasonalized, and cleared of the COVID intervention shock (residual prewhitening approach)**.

### Residual Cross-Correlation Results:

| Time Series | Optimal Lag | Cross-Correlation ($r$) | Absolute Value ($|r|$) |
|---|---|---|---|
| `arrivals_CZ_total` | **0** | **0.989** | **0.989** |
| `arrivals_DE_total` | **0** | **0.900** | **0.900** |
| `arrivals_PL_total` | **0** | **0.891** | **0.891** |
| `nights_DE_total` | **0** | **0.878** | **0.878** |
| `arrivals_SK_total` | **0** | **0.873** | **0.873** |
| `nights_PL_total` | **0** | **0.870** | **0.870** |
| `nights_SK_total` | **0** | **0.857** | **0.857** |
| `arrivals_AT_total` | **0** | **0.850** | **0.850** |
| `nights_AT_total` | **0** | **0.735** | **0.735** |

### Cross-Correlation Plots (CCF) for Key Neighboring Series

![Cross-correlation: nights_CZ_total vs nights_DE_total](images/plot_10.png)
![Cross-correlation: nights_CZ_total vs nights_PL_total](images/plot_11.png)
![Cross-correlation: nights_CZ_total vs nights_SK_total](images/plot_12.png)
![Cross-correlation: nights_CZ_total vs arrivals_CZ_total](images/plot_13.png)

### 💡 Key Cross-Correlation Insights:
Across all series, the **absolute maximum of cross-correlation occurs at lag 0 (contemporaneous relationship)** with correlation coefficients between $0.86$ and $0.99$. No significant leading relationship (e.g., lag $+1$ or $+2$) was found. This demonstrates that the Central European tourism market responds simultaneously, confirming the relevance of **contemporaneous external regressors** in SARIMAX modeling.

---

## 8. SARIMAX with External Regressors

An external regressor matrix was integrated into the state-space model. All explanatory variables were standardized using `StandardScaler` (zero mean, unit variance) to ensure numerical optimization stability.

### Comparison of Tested SARIMAX Specifications:

| Specification | Included External Variables | AIC | BIC | RMSE | LB $p$ (lag 12) | LB $p$ (lag 24) |
|---|---|---|---|---|---|---|
| **E (Winner)** | **`nights_DE_total`, `nights_PL_total`, `nights_SK_total`** | **3,663.14** | **3,689.15** | **206,263** | **0.065** | 0.006 |
| **B** | `arrivals_CZ_total`, `arrivals_DE_total` | 3,667.63 | 3,690.75 | 196,728 | 0.016 | 0.000 |
| **C** | `arrivals_CZ_total`, `arrivals_DE_total`, `arrivals_PL_total` | 3,675.61 | 3,701.62 | 219,981 | 0.238 | 0.040 |
| **A** | `arrivals_CZ_total` | 3,703.23 | 3,723.46 | 211,489 | 0.000 | 0.000 |
| **D** | `arrivals_DE_total`, `arrivals_PL_total`, `arrivals_SK_total` | 3,850.48 | 3,876.50 | 387,000 | 0.000 | 0.000 |

Model E was selected as the superior specification according to AIC, relying exclusively on cross-border nights spent from neighboring countries (Germany, Poland, Slovakia).

### Estimated Coefficients of the Winning SARIMAX Model:

| Parameter | Coefficient | Std. Error | $p$-value | Statistical Interpretation |
|---|---|---|---|---|
| `intercept` | $+2,845,562.34$ | $18,624.56$ | $< 0.001$ | Baseline level |
| `nights_DE_total` | $+302,814.58$ | $132,987.24$ | **0.023** | Significant positive impact of German tourism |
| `nights_PL_total` | $+813,806.76$ | $157,987.18$ | **< 0.001** | Highly significant impact of Polish tourism |
| `nights_SK_total` | $+730,580.45$ | $94,630.98$ | **< 0.001** | Highly significant impact of Slovak tourism |
| `ar.L1` | $+0.293$ | $0.117$ | **0.012** | Significant 1st-order autoregression |
| `ar.L2` | $-0.003$ | $0.111$ | **0.980** | **Insignificant parameter (Principle of Parsimony)** |
| `ma.S.L12` | $+0.367$ | $0.156$ | **0.018** | Significant seasonal MA component |
| `ma.S.L24` | $+0.465$ | $0.136$ | **0.001** | Significant seasonal MA component |

> **Methodological Note on Parsimony:** Parameter `ar.L2` has a $p$-value of $0.980$, being statistically indistinguishable from zero. This occurred due to mechanically transferring the $(2,0,0)$ order from the univariate SARIMA model. With neighboring series included, those series captured part of the short-term dynamics, rendering the second AR term redundant. In practice, fixing this parameter to zero would reduce the model to $SARIMA(1,0,0)(0,0,2)_{12}$.

### SARIMAX Fit Plot and Residual Diagnostics

![Observed Series and Fitted Values of SARIMAX Model](images/plot_14.png)
![Residuals and Residual ACF of Winning SARIMAX Model](images/plot_15.png)

| Lag | Ljung-Box Statistic ($Q$) | $p$-value | White Noise Test Result ($\alpha = 0.05$) |
|---|---|---|---|
| **12** | **20.117** | **0.065** | **White noise hypothesis CANNOT be rejected ($p > 0.05$)** |
| **24** | 44.896 | 0.006 | Autocorrelation present |
| **36** | 73.973 | 0.000 | Autocorrelation present |

By including neighboring countries, autocorrelation at lag 12 was successfully removed ($p = 0.065$). The SARIMAX model represents a substantial qualitative leap forward.

---

## 9. Period Check, Diagnostics, and Forecasting

### 9.1 Period Verification Using the Periodogram

As an independent non-parametric validation of periodicity, the spectral density of the series (periodogram with demeaned data) was calculated:

![Periodogram of the Main Series](images/plot_16.png)

| Rank | Frequency (cycles/month) | Period Length (months) | Spectral Power | Theoretical Interpretation |
|---|---|---|---|---|
| **1.** | **0.0823** | **12.15** | **$2.53 \times 10^{14}$** | **Dominant annual period ($s=12$)** |
| **2.** | 0.1646 | 6.08 | $5.87 \times 10^{13}$ | 1st harmonic component (semi-annual cycle) |
| **3.** | 0.1709 | 5.85 | $2.48 \times 10^{13}$ | Sideband |
| **4.** | 0.0886 | 11.29 | $1.57 \times 10^{13}$ | Annual cycle sideband |
| **5.** | 0.2532 | 3.95 | $8.95 \times 10^{12}$ | 2nd harmonic component (quarterly cycle) |
| **6.** | 0.3354 | 2.98 | $7.50 \times 10^{12}$ | 3rd harmonic component |

The periodogram rigorously confirms setting the seasonal parameter to $s = 12$ in SARIMA and SARIMAX, as well as the validity of the harmonic Fourier terms.

---

### 9.2 Summary Residual Diagnostics

The table below directly contrasts the three primary candidate models examined in this work:

| Model | Model Class | AIC | BIC | RMSE | LB $p$ (lag 12) | LB $p$ (lag 24) | LB $p$ (lag 36) |
|---|---|---|---|---|---|---|---|
| **Fourier_K5 Regression** | OLS Regression | 4,636.85 | 4,679.73 | 522,320 | 0.000000 | 0.000000 | 0.000000 |
| **SARIMA(2,0,0)(0,0,2)[12]** | State Space | 4,038.25 | 4,052.70 | 732,597 | 0.010078 | 0.000135 | 0.000000 |
| **SARIMAX (Model E)** | State Space + Exog | **3,663.14** | **3,689.15** | **206,263** | **0.064971** | 0.005698 | 0.000213 |

> **Methodological Note on AIC:** AIC values between OLS regression and state-space models (SARIMA/SARIMAX) are not directly comparable due to differences in log-likelihood evaluation (RSS vs. Kalman filter innovations). However, SARIMA and SARIMAX are estimated within an identical framework, where the ~375 point drop in AIC definitively proves SARIMAX dominance.

---

### 9.3 10-Step-Ahead Forecast

The forecasting horizon was defined for **10 future months: from March 2026 (`2026-03-01`) to December 2026 (`2026-12-01`)**.

#### Forecasting Methodology by Model:
1. **Fourier Regression:** Deterministic trend extrapolation assuming zero future COVID intervention, alongside relevant trigonometric components. Prediction intervals incorporate the estimated residual variance.
2. **SARIMA:** Stochastic forecast generated via the Kalman filter state-space algorithm.
3. **SARIMAX:** Requires future values of external regressors. These were forecasted using **dedicated `auto_arima` models for Germany, Poland, and Slovakia**, then standardized and supplied into the SARIMAX model, representing a realistic conditional forecast.

#### Individual Model Forecasts:

![10-Month Forecast: Fourier Regression](images/plot_17.png)
![10-Month Forecast: SARIMA](images/plot_18.png)
![10-Month Forecast: SARIMAX](images/plot_19.png)

#### Final Comparison of 10-Month Forecast Paths:

![10-Month Forecast Comparison](images/plot_20.png)

#### Point Forecast Table (in Millions of Nights Spent):

| Month | Fourier Regression | SARIMA | SARIMAX (Winner) | 95% Confidence Interval (SARIMAX) |
|---|---|---|---|---|
| **2026-03** | 3.794 | 4.393 | **3.969** | $[3.459;\ 4.478]$ |
| **2026-04** | 3.796 | 4.959 | **4.240** | $[3.710;\ 4.771]$ |
| **2026-05** | 4.595 | 5.588 | **5.138** | $[4.605;\ 5.670]$ |
| **2026-06** | 5.078 | 5.378 | **5.528** | $[4.995;\ 6.061]$ |
| **2026-07** | 8.103 | 6.154 | **7.272** | $[6.740;\ 7.805]$ |
| **2026-08** | 8.033 | 6.265 | **7.582** | $[7.049;\ 8.114]$ |
| **2026-09** | 5.259 | 4.302 | **5.158** | $[4.625;\ 5.690]$ |
| **2026-10** | 4.438 | 4.536 | **4.720** | $[4.188;\ 5.253]$ |
| **2026-11** | 3.524 | 3.719 | **4.026** | $[3.493;\ 4.558]$ |
| **2026-12** | 3.512 | 3.739 | **3.993** | $[3.461;\ 4.526]$ |

### 💡 Evaluation of Forecasts:
- **Fourier Regression** generates rigidly sharp summer spikes (over 8.1M) while disregarding the recent state of the series.
- **SARIMA** exhibits extremely wide confidence intervals and projects implausibly low values at year-end (with negative lower confidence bounds).
- **SARIMAX** delivers the most realistic and balanced seasonal trajectory, peaking at 7.58M in August with tight, economically credible confidence intervals.

---

## 10. Final Comparison and Evaluation

This project completed a full modeling lifecycle for the tourist nights spent series in the Czech Republic:
1. **Deterministic Regression:** The Fourier $K=5$ model effectively captured average annual seasonality and quadratic trend ($R^2_{adj} = 0.911$), but failed residual diagnostics due to severe autocorrelation ($r_1 \approx 0.68$).
2. **Univariate SARIMA:** The $SARIMA(2,0,0)(0,0,2)_{12}$ model addressed part of the autocorrelation structure and lowered AIC, though residuals were still not purely random.
3. **Multivariate SARIMAX:** Combining a stochastic error structure with nights spent in Germany, Poland, and Slovakia produced the best overall performance ($AIC = 3,663.14$, $RMSE = 206,263$, Ljung-Box $p = 0.065$).

### Limitations and Potential Extensions:
- **COVID Intervention in SARIMAX:** The pandemic was modeled via a binary step dummy in regression. In SARIMAX, a transfer function capturing gradual recovery could be explored.
- **Parsimony:** The estimated parameter `ar.L2` ($p = 0.980$) is statistically non-significant; fixing it to zero would save one degree of freedom.
- **Conditional Forecasts:** SARIMAX forecasts rely on separate predictions of external regressors, whose estimation variance is not fully incorporated into standard analytical confidence bands.
