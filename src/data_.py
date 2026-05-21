"""
data_cleaning.py
Blinkit Analytics Project - Data Cleaning & Feature Engineering
"""

import pandas as pd
import numpy as np
import os

# --------------------------------------------------
# PATH CONFIG (ROBUST)
# --------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

RAW_PATH = os.path.join(BASE_DIR,"data","blinkit_dataset.csv")
CLEANED_PATH = os.path.join(BASE_DIR,"data","blinkit_cleaned.csv")


# --------------------------------------------------
# LOAD
# --------------------------------------------------

def load_data(path):
    df = pd.read_csv(path)

    print(f"Loaded {df.shape[0]:,} rows x {df.shape[1]} columns")
    print(df.columns.tolist())   # verify columns

    return df


# --------------------------------------------------
# INSPECT
# --------------------------------------------------

def inspect(df):

    print("\n--- Data Types ---")
    print(df.dtypes)

    print("\n--- Missing Values ---")
    print(df.isnull().sum())

    print("\n--- Duplicates ---")
    print(df.duplicated().sum())

    print("\n--- Summary Stats ---")
    print(df.describe())


# --------------------------------------------------
# CLEAN
# --------------------------------------------------

def clean(df):

    df = df.copy()

    # Remove duplicates
    before=len(df)
    df.drop_duplicates(inplace=True)
    print("Duplicates removed:", before-len(df))


    # Fill missing
    if "offer_type" in df.columns:
        df["offer_type"]=df["offer_type"].fillna("No Offer")


    # Date parsing
    for col in ["date_added","expiry_date"]:
        if col in df.columns:
            df[col]=pd.to_datetime(
    df[col],
    dayfirst=True,
    errors="coerce"
            )


    # Clean strings safely
    str_cols=df.select_dtypes(include=["object","string"]).columns

    for col in str_cols:
        df[col]=df[col].astype(str).str.strip()


    # Standardize text columns
    for col in [
        "delivery_status",
        "packaging_type",
        "offer_type"
    ]:
        if col in df.columns:
            df[col]=df[col].str.lower()


    # Clip values
    if "rating" in df.columns:
        df["rating"]=df["rating"].clip(0,5)

    if "discount_pct" in df.columns:
        df["discount_pct"]=df["discount_pct"].clip(0,100)


    # Fix final price
    if all(
        c in df.columns for c in
        ["price","discount_pct","final_price"]
    ):

        expected=(
            df["price"] *
            (1-df["discount_pct"]/100)
        ).round(2)

        mismatch=(
            df["final_price"]-expected
        ).abs()>1

        print(
            "Final price mismatches fixed:",
            mismatch.sum()
        )

        df.loc[mismatch,"final_price"]=expected[mismatch]


    print("Cleaning complete")
    return df


# --------------------------------------------------
# FEATURE ENGINEERING
# --------------------------------------------------

def engineer_features(df):

    df=df.copy()


    if all(c in df.columns for c in
        ["final_price","sold_quantity"]):

        df["revenue"]=(
            df["final_price"]*
            df["sold_quantity"]
        ).round(2)


    if all(c in df.columns for c in
        ["revenue","profit_margin_pct"]):

        df["profit"]=(
            df["revenue"]*
            df["profit_margin_pct"]/100
        ).round(2)


    if all(c in df.columns for c in
        ["price","final_price"]):

        df["discount_value"]=(
            df["price"]-
            df["final_price"]
        ).round(2)


    # Price Segments
    if "final_price" in df.columns:

        df["price_segment"]=pd.cut(
            df["final_price"],
            bins=[0,100,300,600,10000],
            labels=[
                "Budget",
                "Mid-Range",
                "Premium",
                "Luxury"
            ]
        )


    # Demand segment
    if "demand_index" in df.columns:

        df["demand_segment"]=pd.cut(
            df["demand_index"],
            bins=[-1,33,66,100],
            labels=[
                "Low",
                "Medium",
                "High"
            ]
        )


    # Stock status
    if all(c in df.columns for c in
        ["stock","reorder_level"]):

        df["stock_status"]=np.where(
            df["stock"]==0,
            "Out of Stock",

            np.where(
                df["stock"]<
                df["reorder_level"],
                "Critical",

                np.where(
                    df["stock"]<
                    df["reorder_level"]*1.5,
                    "Low",
                    "Healthy"
                )
            )
        )


    # Date Features
    if "date_added" in df.columns:

        df["year_added"]=df["date_added"].dt.year
        df["month_added"]=df["date_added"].dt.month
        df["quarter_added"]=df["date_added"].dt.quarter


    if all(c in df.columns for c in
        ["expiry_date","date_added"]):

        df["days_to_expiry"]=(
            df["expiry_date"]-
            df["date_added"]
        ).dt.days


    # Sell-through
    if all(c in df.columns for c in
        ["sold_quantity","stock"]):

        df["sell_through_rate"]=(
            df["sold_quantity"]/
            df["stock"].replace(0,np.nan)
        ).round(4)


    # Delivery Score
    if all(c in df.columns for c in
        ["delivery_status","delivery_time_min"]):

        df["delivery_score"]=np.where(
            df["delivery_status"]=="on-time",

            100-df["delivery_time_min"].clip(0,60),

            50-df["delivery_time_min"].clip(0,60)
        )


    print("Feature engineering complete")
    return df


# --------------------------------------------------
# EXPORT
# --------------------------------------------------

def export(df,path):

    os.makedirs(
        os.path.dirname(path),
        exist_ok=True
    )

    df.to_csv(
        path,
        index=False
    )

    print("Exported:",path)


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__=="__main__":

    df=load_data(RAW_PATH)

    inspect(df)

    df=clean(df)

    df=engineer_features(df)

    export(
        df,
        CLEANED_PATH
    )

    print("\nDone Successfully")