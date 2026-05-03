import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import os

sns.set(style="whitegrid")

# Ensure visuals folder exists INSIDE scripts
os.makedirs("visuals", exist_ok=True)

# Helper function to read Spark CSV output
def read_spark_csv(path):
    file = glob.glob(path + "/part-*.csv")[0]
    return pd.read_csv(file)

# --- 1. TOP COMPLAINT TYPES ---
df_top = read_spark_csv("outputs/top_complaints")
df_top = df_top.sort_values("count", ascending=True)

plt.figure(figsize=(10,6))
sns.barplot(x="count", y="complaint_type", data=df_top, palette="viridis")
plt.title("Top 10 Complaint Types in NYC (2020–2025)")
plt.xlabel("Number of Complaints")
plt.ylabel("Complaint Type")
plt.tight_layout()
plt.savefig("visuals/top_complaints.png")
plt.close()

# --- 2. BOROUGH-WISE COMPLAINTS ---
df_borough = read_spark_csv("outputs/borough_counts")
df_borough = df_borough.sort_values("count", ascending=False)

plt.figure(figsize=(8,6))
sns.barplot(x="borough", y="count", data=df_borough, palette="magma")
plt.title("Complaints by Borough (2020–2025)")
plt.xlabel("Borough")
plt.ylabel("Number of Complaints")
plt.tight_layout()
plt.savefig("visuals/borough_counts.png")
plt.close()

# --- 3. MONTHLY TREND ---
df_monthly = read_spark_csv("outputs/monthly_trend")
df_monthly["year_month"] = df_monthly["year"].astype(str) + "-" + df_monthly["month"].astype(str).str.zfill(2)
df_monthly = df_monthly.sort_values(["year", "month"])

plt.figure(figsize=(12,6))
sns.lineplot(x="year_month", y="count", data=df_monthly, marker="o")
plt.title("Monthly Complaint Trend (2020–2025)")
plt.xlabel("Year-Month")
plt.ylabel("Number of Complaints")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("visuals/monthly_trend.png")
plt.close()

# --- 4. PEAK COMPLAINT HOURS ---
df_hours = read_spark_csv("outputs/hourly_trend")
df_hours = df_hours.sort_values("hour")

plt.figure(figsize=(10,6))
sns.barplot(x="hour", y="count", data=df_hours, palette="coolwarm")
plt.title("Peak Complaint Hours (2020–2025)")
plt.xlabel("Hour of Day")
plt.ylabel("Number of Complaints")
plt.tight_layout()
plt.savefig("visuals/hourly_trend.png")
plt.close()

print("All visualizations saved in the 'visuals' folder!")
