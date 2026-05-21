import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
import os
import warnings

warnings.filterwarnings("ignore")


# ------------------------------------------------
# PATH CONFIG
# ------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "blinkit_cleaned.csv"
)

IMAGE_DIR = os.path.join(
    BASE_DIR,
    "images"
)

os.makedirs(
    IMAGE_DIR,
    exist_ok=True
)


# ------------------------------------------------
# THEME
# ------------------------------------------------

BLINKIT_YELLOW="#F8C302"
BLINKIT_GREEN="#1B7A34"

PALETTE=[
BLINKIT_YELLOW,
BLINKIT_GREEN,
"#E74C3C",
"#3498DB",
"#9B59B6",
"#1ABC9C",
"#E67E22",
"#2C3E50"
]

sns.set_theme(
style="whitegrid",
palette=PALETTE
)

plt.rcParams.update({
"figure.dpi":150,
"axes.spines.top":False,
"axes.spines.right":False
})


# ------------------------------------------------
# LOAD
# ------------------------------------------------

def load(path):

    df=pd.read_csv(path)

    for col in [
        "date_added",
        "expiry_date"
    ]:
        if col in df.columns:
            df[col]=pd.to_datetime(
                df[col],
                errors="coerce"
            )

    if "revenue" not in df.columns:
        df["revenue"]=(
            df["final_price"]*
            df["sold_quantity"]
        )

    print(
      f"Loaded {df.shape[0]:,} rows"
    )

    return df


# ------------------------------------------------
# SUMMARY
# ------------------------------------------------

def print_summary(df):

    print("\nBUSINESS SUMMARY")
    print("-"*50)

    print(
      "Revenue:",
      df["revenue"].sum()
    )

    print(
      "Avg Rating:",
      round(
        df["rating"].mean(),
        2
      )
    )

    print(
      "Cities:",
      df["city"].nunique()
    )

    print(
      "Categories:",
      df["category"].nunique()
    )


# ------------------------------------------------
# CHART 1
# ------------------------------------------------

def chart1(df):

    data=(
      df.groupby("category")
      ["revenue"]
      .sum()
      .sort_values(
        ascending=False
      )
      /1e7
    )

    plt.figure(
        figsize=(10,6)
    )

    data.plot(
      kind="bar",
      color=BLINKIT_YELLOW,
      edgecolor="black"
    )

    plt.title(
      "Revenue by Category"
    )

    plt.ylabel(
      "Crores"
    )

    plt.tight_layout()

    plt.savefig(
      os.path.join(
        IMAGE_DIR,
        "01_revenue_category.png"
      )
    )

    plt.close()

    print("Chart1 saved")


# ------------------------------------------------
# CHART 2
# ------------------------------------------------

def chart2(df):

    data=(
      df.groupby("city")
      ["revenue"]
      .sum()
      .sort_values()
      /1e7
    )

    plt.figure(
      figsize=(10,7)
    )

    data.plot(
      kind="barh",
      color=BLINKIT_GREEN
    )

    plt.title(
      "Revenue by City"
    )

    plt.tight_layout()

    plt.savefig(
      os.path.join(
        IMAGE_DIR,
        "02_city_revenue.png"
      )
    )

    plt.close()

    print("Chart2 saved")


# ------------------------------------------------
# CHART 3
# ------------------------------------------------

def chart3(df):

    plt.figure(
      figsize=(12,6)
    )

    sns.boxplot(
      data=df,
      x="category",
      y="final_price"
    )

    plt.xticks(
      rotation=25
    )

    plt.title(
      "Price Distribution"
    )

    plt.tight_layout()

    plt.savefig(
      os.path.join(
        IMAGE_DIR,
        "03_price_boxplot.png"
      )
    )

    plt.close()

    print("Chart3 saved")


# ------------------------------------------------
# CHART 4
# ------------------------------------------------

def chart4(df):

    plt.figure(
      figsize=(9,6)
    )

    plt.scatter(
      df["rating"],
      df["demand_index"],
      alpha=.5
    )

    plt.title(
      "Rating vs Demand"
    )

    plt.xlabel(
      "Rating"
    )

    plt.ylabel(
      "Demand"
    )

    plt.tight_layout()

    plt.savefig(
      os.path.join(
        IMAGE_DIR,
        "04_rating_demand.png"
      )
    )

    plt.close()

    print("Chart4 saved")


# ------------------------------------------------
# CHART 5
# ------------------------------------------------

def chart5(df):

    bins=[0,10,20,30,100]

    labels=[
      "0-10",
      "10-20",
      "20-30",
      "30+"
    ]

    d=df.copy()

    d["disc_bucket"]=pd.cut(
      d["discount_pct"],
      bins=bins,
      labels=labels
    )

    agg=d.groupby(
      "disc_bucket"
    )["sold_quantity"].mean()

    plt.figure(
      figsize=(8,5)
    )

    agg.plot(
      kind="bar",
      color=BLINKIT_YELLOW
    )

    plt.title(
      "Discount Impact"
    )

    plt.tight_layout()

    plt.savefig(
      os.path.join(
        IMAGE_DIR,
        "05_discount_impact.png"
      )
    )

    plt.close()

    print("Chart5 saved")


# ------------------------------------------------
# CHART 6
# ------------------------------------------------

def chart6(df):

    pivot=(
      df.groupby(
        ["category","is_organic"]
      )["revenue"]
      .sum()
      .unstack()
      .fillna(0)
    )

    pivot.plot(
      kind="bar",
      stacked=True,
      figsize=(11,6)
    )

    plt.title(
      "Organic Revenue"
    )

    plt.tight_layout()

    plt.savefig(
      os.path.join(
        IMAGE_DIR,
        "06_organic.png"
      )
    )

    plt.close()

    print("Chart6 saved")


# ------------------------------------------------
# CHART 7
# ------------------------------------------------

def chart7(df):

    heat=(
      df.groupby(
       ["city","delivery_status"]
      )
      .size()
      .unstack(fill_value=0)
    )

    plt.figure(
      figsize=(10,6)
    )

    sns.heatmap(
      heat,
      annot=True,
      cmap="YlGn"
    )

    plt.title(
      "Delivery Heatmap"
    )

    plt.tight_layout()

    plt.savefig(
      os.path.join(
        IMAGE_DIR,
        "07_heatmap.png"
      )
    )

    plt.close()

    print("Chart7 saved")


# ------------------------------------------------
# CHART 8
# ------------------------------------------------

def chart8(df):

    if "date_added" not in df:
        return

    monthly=(
      df.set_index(
       "date_added"
      )["revenue"]
      .resample("ME")
      .sum()
    )

    plt.figure(
      figsize=(12,5)
    )

    monthly.plot()

    plt.title(
      "Monthly Revenue Trend"
    )

    plt.tight_layout()

    plt.savefig(
      os.path.join(
        IMAGE_DIR,
        "08_trend.png"
      )
    )

    plt.close()

    print("Chart8 saved")


# ------------------------------------------------
# CORRELATION
# ------------------------------------------------

def correlation(df):

    cols=[
      "price",
      "final_price",
      "discount_pct",
      "rating",
      "delivery_time_min",
      "sold_quantity",
      "profit_margin_pct",
      "demand_index",
      "revenue"
    ]

    cols=[
      c for c in cols
      if c in df.columns
    ]

    corr=df[cols].corr()

    plt.figure(
      figsize=(10,8)
    )

    sns.heatmap(
      corr,
      annot=True,
      cmap="RdYlGn"
    )

    plt.title(
      "Correlation Matrix"
    )

    plt.tight_layout()

    plt.savefig(
      os.path.join(
        IMAGE_DIR,
        "09_correlation.png"
      )
    )

    plt.close()

    print(
      "Correlation saved"
    )


# ------------------------------------------------
# MAIN
# ------------------------------------------------

if __name__=="__main__":

    df=load(
      DATA_PATH
    )

    print_summary(df)

    chart1(df)
    chart2(df)
    chart3(df)
    chart4(df)
    chart5(df)
    chart6(df)
    chart7(df)
    chart8(df)

    correlation(df)

    print(
      "\nAll charts saved in images folder"
    )