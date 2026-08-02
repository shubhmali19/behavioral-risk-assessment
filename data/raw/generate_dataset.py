import numpy as np
import pandas as pd

np.random.seed(42)
N = 22000

# --- Demographic ---
age = np.random.normal(35, 10, N).clip(18, 75).astype(int)

gender = np.random.choice(['Male', 'Female', 'Other'], N, p=[0.50, 0.47, 0.03])

education = np.where(
    age < 22, np.random.choice(['High School', 'Graduate'], N, p=[0.5, 0.5]),
    np.random.choice(['High School', 'Graduate', 'Post Graduate', 'PhD'], N, p=[0.20, 0.40, 0.30, 0.10])
)

occupation_base = np.random.choice(
    ['Salaried', 'Self-Employed', 'Business', 'Freelancer', 'Student', 'Retired'],
    N, p=[0.40, 0.18, 0.15, 0.10, 0.10, 0.07]
)
# Override for young age → more students
occupation = np.where(age < 24, np.random.choice(['Student', 'Salaried', 'Freelancer'], N, p=[0.5, 0.3, 0.2]), occupation_base)

# Income level correlated with occupation
def occ_to_income(occ):
    mapping = {
        'Business': np.random.choice(['Middle', 'High'], p=[0.35, 0.65]),
        'Salaried': np.random.choice(['Low', 'Middle', 'High'], p=[0.25, 0.55, 0.20]),
        'Self-Employed': np.random.choice(['Low', 'Middle', 'High'], p=[0.30, 0.45, 0.25]),
        'Freelancer': np.random.choice(['Low', 'Middle', 'High'], p=[0.35, 0.45, 0.20]),
        'Student': np.random.choice(['Low', 'Middle'], p=[0.80, 0.20]),
        'Retired': np.random.choice(['Low', 'Middle', 'High'], p=[0.40, 0.40, 0.20]),
    }
    return mapping.get(occ, 'Middle')

income_level = np.array([occ_to_income(o) for o in occupation])

marital_status = np.where(
    age < 25, np.random.choice(['Single', 'Married'], N, p=[0.85, 0.15]),
    np.where(age < 35, np.random.choice(['Single', 'Married', 'Divorced'], N, p=[0.40, 0.52, 0.08]),
    np.where(age < 55, np.random.choice(['Single', 'Married', 'Divorced', 'Widowed'], N, p=[0.15, 0.65, 0.15, 0.05]),
    np.random.choice(['Single', 'Married', 'Divorced', 'Widowed'], N, p=[0.08, 0.55, 0.20, 0.17])))
)

dep_base = np.random.poisson(1.2, N)
dep_base = np.where(marital_status == 'Single', np.random.poisson(0.3, N), dep_base)
dep_base = np.where(age < 25, 0, dep_base)
dependents = dep_base.clip(0, 5)

location = np.where(
    income_level == 'High', np.random.choice(['Urban', 'Semi-Urban', 'Rural'], N, p=[0.70, 0.22, 0.08]),
    np.where(income_level == 'Middle', np.random.choice(['Urban', 'Semi-Urban', 'Rural'], N, p=[0.45, 0.35, 0.20]),
    np.random.choice(['Urban', 'Semi-Urban', 'Rural'], N, p=[0.25, 0.35, 0.40]))
)

employment_type = np.where(
    occupation == 'Student', 'Part-Time',
    np.where(occupation == 'Retired', 'Unemployed',
    np.where(occupation == 'Freelancer', np.random.choice(['Contract', 'Part-Time'], N, p=[0.6, 0.4]),
    np.where(occupation == 'Business', 'Full-Time',
    np.random.choice(['Full-Time', 'Part-Time', 'Contract', 'Unemployed'], N, p=[0.65, 0.15, 0.15, 0.05]))))
)

years_of_experience = (age - 22 + np.random.normal(0, 2, N)).clip(0, 40).astype(int)
years_of_experience = np.where(occupation == 'Student', 0, years_of_experience)

# --- Financial ---
base_income = {
    'Business': 80000, 'Salaried': 45000, 'Self-Employed': 55000,
    'Freelancer': 40000, 'Student': 12000, 'Retired': 25000
}
edu_mult = {'High School': 0.8, 'Graduate': 1.0, 'Post Graduate': 1.3, 'PhD': 1.6}

monthly_income = np.array([
    max(5000, int(base_income.get(o, 40000) * edu_mult.get(e, 1.0) * np.random.lognormal(0, 0.35)))
    for o, e in zip(occupation, education)
]).clip(5000, 200000)

expense_ratio = np.random.uniform(0.40, 0.90, N)
expense_ratio = expense_ratio + dependents * 0.04
expense_ratio = expense_ratio.clip(0.30, 0.95)
monthly_expenses = (monthly_income * expense_ratio + np.random.normal(0, 2000, N)).clip(3000, 180000).astype(int)

savings_rate_raw = (monthly_income - monthly_expenses) / monthly_income
savings_rate = (savings_rate_raw + np.random.normal(0, 0.05, N)).clip(-0.1, 0.60)

# Financial discipline score (internal helper, 0-1)
fin_discipline = (savings_rate.clip(0, 1) * 0.5 + np.random.uniform(0, 0.5, N)).clip(0, 1)

emergency_fund_months = (fin_discipline * 20 + np.random.normal(0, 2, N)).clip(0, 24).astype(int)

total_debt = np.where(
    income_level == 'High', np.random.lognormal(10, 1.5, N).clip(0, 5000000),
    np.where(income_level == 'Middle', np.random.lognormal(9.5, 1.5, N).clip(0, 3000000),
    np.random.lognormal(8.5, 1.5, N).clip(0, 1500000))
).astype(int)

loan_amount = (total_debt * np.random.uniform(0, 0.8, N)).clip(0, 3000000).astype(int)

debt_to_income = total_debt / (monthly_income * 12 + 1)
credit_score_base = 750 - debt_to_income * 100 + savings_rate * 80 + years_of_experience * 2
credit_score = (credit_score_base + np.random.normal(0, 40, N)).clip(300, 900).astype(int)

investment_experience_years = (years_of_experience * 0.4 * fin_discipline + np.random.normal(0, 2, N)).clip(0, 20).astype(int)

inv_freq_prob = np.stack([
    (1 - fin_discipline) * 0.5,
    (1 - fin_discipline) * 0.3,
    fin_discipline * 0.5,
    fin_discipline * 0.3
], axis=1)
inv_freq_prob = inv_freq_prob / inv_freq_prob.sum(axis=1, keepdims=True)
investment_frequency = np.array([
    np.random.choice(['Never', 'Rarely', 'Monthly', 'Weekly'], p=p)
    for p in inv_freq_prob
])

ins_prob = np.stack([
    (1 - fin_discipline) * 0.5,
    np.ones(N) * 0.4,
    fin_discipline * 0.5
], axis=1)
ins_prob = ins_prob / ins_prob.sum(axis=1, keepdims=True)
insurance_coverage = np.array([
    np.random.choice(['None', 'Basic', 'Comprehensive'], p=p)
    for p in ins_prob
])

# --- Lifestyle ---
shopping_frequency = np.random.choice(['Rarely', 'Monthly', 'Weekly', 'Daily'], N, p=[0.15, 0.35, 0.35, 0.15])
online_spending_pct = (np.random.beta(2, 3, N) * 80 + np.random.normal(0, 3, N)).clip(0, 80).round(1)
luxury_spending_pct = np.where(
    income_level == 'High', (np.random.beta(2, 3, N) * 50 + np.random.normal(0, 3, N)).clip(0, 50),
    (np.random.beta(1, 4, N) * 30 + np.random.normal(0, 2, N)).clip(0, 30)
).round(1)
subscription_count = (np.random.poisson(3, N) + (income_level == 'High') * 2).clip(0, 15).astype(int)
gaming_expenses_monthly = (np.random.exponential(500, N) * (age < 35)).clip(0, 10000).astype(int)
travel_expenses_annual = np.where(
    income_level == 'High', np.random.lognormal(10, 1, N).clip(0, 200000),
    np.where(income_level == 'Middle', np.random.lognormal(9, 1, N).clip(0, 100000),
    np.random.lognormal(7.5, 1, N).clip(0, 50000))
).astype(int)

# --- Target Variables ---
# Risk scoring
risk_score = (
    - savings_rate * 30
    + (1 - credit_score / 900) * 25
    + (debt_to_income.clip(0, 5) / 5) * 20
    - investment_experience_years / 20 * 15
    + (emergency_fund_months < 3) * 10
    + np.random.normal(0, 8, N)
)

# Target: Low ~35%, Medium ~45%, High ~20%
p20 = np.percentile(risk_score, 35)
p65 = np.percentile(risk_score, 80)
risk_category = np.where(risk_score < p20, 'Low', np.where(risk_score < p65, 'Medium', 'High'))

inv_pref_choices = ['FD', 'Mutual Funds', 'Stocks', 'Gold', 'Crypto']
def inv_pref(risk):
    if risk == 'Low':
        return np.random.choice(inv_pref_choices, p=[0.40, 0.25, 0.10, 0.20, 0.05])
    elif risk == 'Medium':
        return np.random.choice(inv_pref_choices, p=[0.15, 0.35, 0.25, 0.15, 0.10])
    else:
        return np.random.choice(inv_pref_choices, p=[0.05, 0.20, 0.35, 0.10, 0.30])

investment_preference = np.array([inv_pref(r) for r in risk_category])

expected_savings_increase = (fin_discipline * 25 + np.random.normal(0, 3, N)).clip(0, 30).round(2)

financial_decision_score = (
    savings_rate.clip(0, 1) * 30
    + (credit_score - 300) / 600 * 25
    + (1 - debt_to_income.clip(0, 5) / 5) * 20
    + investment_experience_years / 20 * 15
    + emergency_fund_months / 24 * 10
    + np.random.normal(0, 5, N)
).clip(0, 100).round(2)

# --- Assemble DataFrame ---
df = pd.DataFrame({
    'age': age,
    'gender': gender,
    'education': education,
    'occupation': occupation,
    'income_level': income_level,
    'marital_status': marital_status,
    'dependents': dependents,
    'location': location,
    'employment_type': employment_type,
    'years_of_experience': years_of_experience,
    'monthly_income': monthly_income,
    'monthly_expenses': monthly_expenses,
    'savings_rate': savings_rate.round(4),
    'emergency_fund_months': emergency_fund_months,
    'total_debt': total_debt,
    'loan_amount': loan_amount,
    'credit_score': credit_score,
    'investment_experience_years': investment_experience_years,
    'investment_frequency': investment_frequency,
    'insurance_coverage': insurance_coverage,
    'shopping_frequency': shopping_frequency,
    'online_spending_pct': online_spending_pct,
    'luxury_spending_pct': luxury_spending_pct,
    'subscription_count': subscription_count,
    'gaming_expenses_monthly': gaming_expenses_monthly,
    'travel_expenses_annual': travel_expenses_annual,
    'risk_category': risk_category,
    'investment_preference': investment_preference,
    'expected_savings_increase': expected_savings_increase,
    'financial_decision_score': financial_decision_score,
})

print("Shape:", df.shape)
print("\nFirst 5 rows:")
print(df.head())
print("\nrisk_category value_counts:")
print(df['risk_category'].value_counts())
print("\nrisk_category proportions:")
print(df['risk_category'].value_counts(normalize=True).round(3))

df.to_csv('dataset.csv', index=False)
print("\nSaved dataset.csv")

# --- Description markdown ---
desc_lines = [
    "# Dataset Description\n",
    f"**Records:** {len(df)}  \n**Columns:** {len(df.columns)}\n",
    "## Schema\n",
    "| Column | Type | Description |",
    "|--------|------|-------------|",
    "| age | int | Age of individual (18–75) |",
    "| gender | str | Male / Female / Other |",
    "| education | str | High School / Graduate / Post Graduate / PhD |",
    "| occupation | str | Salaried / Self-Employed / Business / Freelancer / Student / Retired |",
    "| income_level | str | Low / Middle / High |",
    "| marital_status | str | Single / Married / Divorced / Widowed |",
    "| dependents | int | Number of dependents (0–5) |",
    "| location | str | Urban / Semi-Urban / Rural |",
    "| employment_type | str | Full-Time / Part-Time / Contract / Unemployed |",
    "| years_of_experience | int | Work experience in years (0–40) |",
    "| monthly_income | int | Monthly income in INR (5000–200000) |",
    "| monthly_expenses | int | Monthly expenses in INR |",
    "| savings_rate | float | (Income - Expenses) / Income + noise |",
    "| emergency_fund_months | int | Months of emergency fund saved (0–24) |",
    "| total_debt | int | Total outstanding debt in INR (0–5000000) |",
    "| loan_amount | int | Active loan amount in INR (0–3000000) |",
    "| credit_score | int | Credit score (300–900) |",
    "| investment_experience_years | int | Years of investment experience (0–20) |",
    "| investment_frequency | str | Never / Rarely / Monthly / Weekly |",
    "| insurance_coverage | str | None / Basic / Comprehensive |",
    "| shopping_frequency | str | Rarely / Monthly / Weekly / Daily |",
    "| online_spending_pct | float | % of expenses spent online (0–80) |",
    "| luxury_spending_pct | float | % of expenses on luxury (0–50) |",
    "| subscription_count | int | Number of active subscriptions (0–15) |",
    "| gaming_expenses_monthly | int | Monthly gaming spend in INR (0–10000) |",
    "| travel_expenses_annual | int | Annual travel spend in INR (0–200000) |",
    "| risk_category | str | TARGET: Low / Medium / High |",
    "| investment_preference | str | TARGET: FD / Mutual Funds / Stocks / Gold / Crypto |",
    "| expected_savings_increase | float | TARGET: Expected savings increase % (0–30) |",
    "| financial_decision_score | float | TARGET: Composite financial score (0–100) |",
    "",
    "## Distribution Summary\n",
    "### risk_category",
    df['risk_category'].value_counts().to_string(),
    "",
    "### investment_preference",
    df['investment_preference'].value_counts().to_string(),
    "",
    "### income_level",
    df['income_level'].value_counts().to_string(),
    "",
    "### Numeric Summary",
    df[['monthly_income','monthly_expenses','savings_rate','credit_score','total_debt','financial_decision_score']].describe().to_string(),
]

with open('dataset_description.md', 'w') as f:
    f.write('\n'.join(desc_lines))
print("Saved dataset_description.md")
print("AGENT1_COMPLETE")
