# Dataset Description

**Records:** 22000  
**Columns:** 30

## Schema

| Column | Type | Description |
|--------|------|-------------|
| age | int | Age of individual (18–75) |
| gender | str | Male / Female / Other |
| education | str | High School / Graduate / Post Graduate / PhD |
| occupation | str | Salaried / Self-Employed / Business / Freelancer / Student / Retired |
| income_level | str | Low / Middle / High |
| marital_status | str | Single / Married / Divorced / Widowed |
| dependents | int | Number of dependents (0–5) |
| location | str | Urban / Semi-Urban / Rural |
| employment_type | str | Full-Time / Part-Time / Contract / Unemployed |
| years_of_experience | int | Work experience in years (0–40) |
| monthly_income | int | Monthly income in INR (5000–200000) |
| monthly_expenses | int | Monthly expenses in INR |
| savings_rate | float | (Income - Expenses) / Income + noise |
| emergency_fund_months | int | Months of emergency fund saved (0–24) |
| total_debt | int | Total outstanding debt in INR (0–5000000) |
| loan_amount | int | Active loan amount in INR (0–3000000) |
| credit_score | int | Credit score (300–900) |
| investment_experience_years | int | Years of investment experience (0–20) |
| investment_frequency | str | Never / Rarely / Monthly / Weekly |
| insurance_coverage | str | None / Basic / Comprehensive |
| shopping_frequency | str | Rarely / Monthly / Weekly / Daily |
| online_spending_pct | float | % of expenses spent online (0–80) |
| luxury_spending_pct | float | % of expenses on luxury (0–50) |
| subscription_count | int | Number of active subscriptions (0–15) |
| gaming_expenses_monthly | int | Monthly gaming spend in INR (0–10000) |
| travel_expenses_annual | int | Annual travel spend in INR (0–200000) |
| risk_category | str | TARGET: Low / Medium / High |
| investment_preference | str | TARGET: FD / Mutual Funds / Stocks / Gold / Crypto |
| expected_savings_increase | float | TARGET: Expected savings increase % (0–30) |
| financial_decision_score | float | TARGET: Composite financial score (0–100) |

## Distribution Summary

### risk_category
risk_category
Medium    9900
Low       7700
High      4400

### investment_preference
investment_preference
Mutual Funds    6311
Stocks          4816
FD              4742
Gold            3444
Crypto          2687

### income_level
income_level
Middle    9557
Low       7273
High      5170

### Numeric Summary
       monthly_income  monthly_expenses  savings_rate  credit_score    total_debt  financial_decision_score
count    22000.000000      22000.000000  22000.000000  22000.000000  2.200000e+04              22000.000000
mean     51344.567136      35027.610409      0.316463    789.217500  3.895583e+04                 54.121019
std      32673.174306      24127.711503      0.168389     52.290863  1.156650e+05                  8.947942
min       5000.000000       3000.000000     -0.100000    300.000000  1.300000e+01                  0.000000
25%      28547.750000      17758.750000      0.189100    758.000000  3.680000e+03                 48.020000
50%      45802.000000      30212.000000      0.319000    791.000000  1.071700e+04                 54.195000
75%      67233.000000      46355.750000      0.448600    823.000000  3.225875e+04                 60.410000
max     200000.000000     180000.000000      0.600000    900.000000  4.166885e+06                 85.340000