# Change Point Analysis and Statistical Modeling of Time Series Data

## Task 1: Laying the Foundation for Analysis

**Objective:**  
Define the data analysis workflow and develop a thorough understanding of the model and data for Brent oil price analysis.

---

## Instructions

### 1. Defining the Data Analysis Workflow

- **Outline Analysis Steps:**  
  Document all steps involved in analyzing Brent oil prices, from data loading and preprocessing to insight generation.

- **Research and Compile Event Data:**  
  Identify major geopolitical events, OPEC decisions, and economic shocks relevant to the oil market.  
  Compile a structured dataset (CSV file) with at least 10–15 key events, including approximate start dates.

- **State Assumptions and Limitations:**  
  Clearly document assumptions and limitations of your analysis.  
  Include a critical discussion on the difference between **statistical correlation** and **causal impact**.

- **Determine Communication Channels:**  
  Identify primary media channels and formats for communicating results to stakeholders (e.g., dashboards, reports, alerts).

---

### 2. Understanding the Model and Data

- **Review Key References:**  
  Read main references and literature related to time series analysis and change point detection to understand the core concepts and models.

- **Analyze Time Series Properties:**  
  Investigate key characteristics of Brent oil price data before modeling:
  - **Trend Analysis:** Identify long-term trends.
  - **Stationarity Testing:** Perform ADF/KPSS tests.
  - **Volatility Patterns:** Examine volatility clustering and regime changes.

- **Explain Change Point Models:**  
  Describe the purpose of change point models in analyzing price fluctuations and identifying structural breaks.

- **Expected Outputs:**  
  Explain expected outputs from change point analysis, such as:
  - Dates of significant changes
  - New parameter values (mean, volatility)
  - Confidence intervals and regime classifications  
  Discuss limitations of these methods.


---

## Task 2: Change Point Modeling and Insight Generation

### Objective
Apply **Bayesian Change Point Detection** to identify and quantify structural breaks in Brent oil prices and associate them with real-world events such as conflicts, sanctions, and OPEC policy changes.

---

### 1. Core Analysis (Mandatory)

#### 1.1 Data Preparation and Exploratory Data Analysis (EDA)

- Load historical Brent oil price data
- Convert the `Date` column to `datetime` format
- Plot the raw price series to observe:
  - Long-term trends
  - Major shocks
  - Periods of high volatility
- Compute **log returns** to improve stationarity:
  
  \[
  r_t = \log(price_t) - \log(price_{t-1})
  \]

- Plot log returns to examine **volatility clustering**

---

#### 1.2 Bayesian Change Point Model (PyMC)

The Bayesian model is designed to detect a **single structural break** in the price or return series.

**Model Components:**

- **Switch Point (τ):**
  - Defined as a discrete uniform prior across all time indices

- **Before / After Parameters:**
  - Two separate means (μ₁, μ₂) representing regimes before and after τ

- **Switching Function:**
  - Uses `pm.math.switch()` to apply the appropriate mean based on time index

- **Likelihood:**
  - Observed data modeled using a Normal distribution with regime-dependent mean

- **Sampling:**
  - MCMC sampling performed using `pm.sample()`

---

#### 1.3 Model Diagnostics and Interpretation

- **Convergence Checks**
  - Review `pm.summary()` output
  - Ensure `r_hat ≈ 1.0`
  - Inspect trace plots using `pm.plot_trace()`

- **Change Point Identification**
  - Plot posterior distribution of τ
  - Sharp peaks indicate strong confidence in detected change points

- **Impact Quantification**
  - Compare posterior distributions of μ₁ and μ₂
  - Make probabilistic statements about price shifts

- **Event Association**
  - Compare detected change point dates with known events
  - Formulate hypotheses linking events to price changes

**Example Interpretation:**

> Following the OPEC production cut announcement around *[Date]*, the model detects a change point, with the average daily price shifting from **$X** to **$Y**, representing an increase of **Z%**.

---

### 2. Advanced Extensions (Optional / Future Work)

- **Incorporate External Variables**
  - GDP growth
  - Inflation rates
  - Exchange rates

- **Advanced Modeling Approaches**
  - **VAR (Vector Autoregression):**  
    Analyze dynamic relationships between oil prices and macroeconomic variables
  - **Markov-Switching Models:**  
    Explicitly model regime changes such as *calm* vs *volatile* markets

---

## Task 3: Interactive Dashboard for Data Analysis Results

### Objective
Develop an interactive dashboard that allows stakeholders to **explore oil price trends, detected change points, and event impacts**.

---

### Backend (Flask)

- Serve processed data and model outputs through RESTful APIs
- Handle requests for:
  - Historical price data
  - Change point detection results
  - Event correlation and impact metrics

**Key API Endpoints:**
- `/api/prices` – Historical Brent oil prices
- `/api/changepoints` – Detected change points and posterior summaries
- `/api/events` – Event data and correlations

---

### Frontend (React)

- Build a user-friendly and responsive interface
- Display interactive visualizations for analysis results
- Ensure compatibility across:
  - Desktop
  - Tablet
  - Mobile devices

**Core UI Features:**
- Date range selectors and filters
- Event highlight functionality (price spikes/drops)
- Drill-down views for deeper analysis
- Clear presentation of model insights

---

### Recommended Charting Libraries

- **Recharts**
- **React Chart.js 2**
- **D3.js**

---

### Key Dashboard Capabilities

- Visualize historical price trends alongside key events
- Highlight how political and economic events influence prices
- Display indicators such as:
  - Volatility
  - Average price changes around events
- Enable dynamic filtering and time-window exploration

---

## Technologies Used

- **Python:** Pandas, NumPy, PyMC, Matplotlib
- **Backend:** Flask
- **Frontend:** React
- **Visualization:** Recharts / Chart.js / D3.js

---

## Expected Outcomes

- Clear identification of structural breaks in Brent oil prices
- Quantitative assessment of event-driven price impacts
- An interactive dashboard supporting stakeholder exploration and insight generation

---




