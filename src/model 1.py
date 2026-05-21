import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import os
import warnings

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

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
# CONFIG
# ------------------------------------------------

BLINKIT_YELLOW="#F8C302"
BLINKIT_GREEN="#1B7A34"

FEATURES=[
"final_price",
"discount_pct",
"rating",
"num_reviews",
"delivery_time_min",
"stock",
"profit_margin_pct",
"demand_index",
"weight_g",
"shelf_life_days",
"is_organic",
"category",
"city",
"packaging_type",
"offer_type",
"delivery_status"
]

TARGET="sold_quantity"


# ------------------------------------------------
# PREPARE DATA
# ------------------------------------------------

def prepare(path):

    df=pd.read_csv(path)

    if "revenue" not in df.columns:
        df["revenue"]=(
            df["final_price"]*
            df["sold_quantity"]
        )


    # keep only columns that exist
    use_cols=[
      c for c in FEATURES+[TARGET]
      if c in df.columns
    ]

    df=df[use_cols].copy()


    # categorical encoding
    cat_cols=df.select_dtypes(
       include=["object","bool"]
    ).columns

    le=LabelEncoder()

    for col in cat_cols:
        df[col]=le.fit_transform(
            df[col].astype(str)
        )


    df.dropna(inplace=True)


    X=df.drop(
       TARGET,
       axis=1
    )

    y=df[TARGET]

    print(
      f"Prepared {X.shape[0]:,} rows x {X.shape[1]} features"
    )

    return X,y


# ------------------------------------------------
# EVALUATE
# ------------------------------------------------

def evaluate_model(
model,
X_train,
X_test,
y_train,
y_test,
name
):

    model.fit(
      X_train,
      y_train
    )

    pred=model.predict(
      X_test
    )


    mae=mean_absolute_error(
      y_test,
      pred
    )

    rmse=np.sqrt(
      mean_squared_error(
         y_test,
         pred
      )
    )

    r2=r2_score(
      y_test,
      pred
    )


    cv=cross_val_score(
      model,
      X_train,
      y_train,
      cv=5,
      scoring="r2"
    ).mean()


    print("\n",name)
    print("MAE:",round(mae,2))
    print("RMSE:",round(rmse,2))
    print("R2:",round(r2,4))
    print("CV:",round(cv,4))


    return {
      "model":model,
      "name":name,
      "mae":mae,
      "rmse":rmse,
      "r2":r2,
      "pred":pred
    }


# ------------------------------------------------
# FEATURE IMPORTANCE
# ------------------------------------------------

def plot_importance(
model,
features,
name
):

    if not hasattr(
      model,
      "feature_importances_"
    ):
       return

    imp=pd.Series(
      model.feature_importances_,
      index=features
    ).sort_values().tail(15)

    plt.figure(
      figsize=(10,6)
    )

    imp.plot(
      kind="barh",
      color=BLINKIT_YELLOW
    )

    plt.title(
      f"Feature Importance {name}"
    )

    plt.tight_layout()

    plt.savefig(
      os.path.join(
       IMAGE_DIR,
       f"model_importance_{name}.png"
      )
    )

    plt.close()

    print(
      "Feature chart saved"
    )


# ------------------------------------------------
# ACTUAL VS PREDICTED
# ------------------------------------------------

def plot_actual(
y_test,
pred,
name
):

    plt.figure(
      figsize=(7,7)
    )

    plt.scatter(
      y_test,
      pred,
      alpha=.3
    )

    mn=min(
      y_test.min(),
      pred.min()
    )

    mx=max(
      y_test.max(),
      pred.max()
    )

    plt.plot(
      [mn,mx],
      [mn,mx],
      "--"
    )

    plt.title(
      f"Actual vs Pred {name}"
    )

    plt.tight_layout()

    plt.savefig(
      os.path.join(
       IMAGE_DIR,
       f"actual_pred_{name}.png"
      )
    )

    plt.close()

    print(
      "Prediction plot saved"
    )


# ------------------------------------------------
# MODEL COMPARISON
# ------------------------------------------------

def comparison(results):

    names=[
      r["name"]
      for r in results
    ]

    r2s=[
      r["r2"]
      for r in results
    ]


    plt.figure(
      figsize=(8,5)
    )

    plt.bar(
      names,
      r2s
    )

    plt.title(
      "Model Comparison"
    )

    plt.tight_layout()

    plt.savefig(
      os.path.join(
       IMAGE_DIR,
       "model_compare.png"
      )
    )

    plt.close()


# ------------------------------------------------
# MAIN
# ------------------------------------------------

if __name__=="__main__":

    X,y=prepare(
      DATA_PATH
    )


    X_train,X_test,y_train,y_test=(
      train_test_split(
        X,
        y,
        test_size=.2,
        random_state=42
      )
    )


    scaler=StandardScaler()

    X_train_sc=scaler.fit_transform(
      X_train
    )

    X_test_sc=scaler.transform(
      X_test
    )


    models=[

      (
       "Ridge",
       Ridge(),
       True
      ),

      (
       "RandomForest",
       RandomForestRegressor(
         n_estimators=200,
         random_state=42,
         n_jobs=-1
       ),
       False
      ),

      (
       "GradientBoosting",
       GradientBoostingRegressor(
         n_estimators=200,
         learning_rate=.05,
         random_state=42
       ),
       False
      )
    ]


    results=[]


    for name,model,scaled in models:

        Xtr=(
          X_train_sc
          if scaled
          else X_train
        )

        Xte=(
          X_test_sc
          if scaled
          else X_test
        )

        res=evaluate_model(
            model,
            Xtr,
            Xte,
            y_train,
            y_test,
            name
        )

        results.append(res)

        plot_importance(
          model,
          X.columns.tolist(),
          name
        )

        plot_actual(
          y_test,
          res["pred"],
          name
        )


    comparison(
      results
    )


    best=max(
      results,
      key=lambda r:r["r2"]
    )

    print(
      "\nBest Model:",
      best["name"]
    )

    print(
      "\nModel outputs saved."
    )