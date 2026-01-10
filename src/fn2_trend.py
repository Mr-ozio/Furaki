import pandas as pd

def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["created_at"])
    df = df[df["price"] > 10000]
    return df

def analyze_trend(df: pd.DataFrame, label: str):
    df["month"] = df["created_at"].dt.to_period("M")
    monthly = df.groupby("month")["price"].median().reset_index()
    monthly["month"] = monthly["month"].dt.to_timestamp()

    print(f"\nTrend cen – {label}")
    print(monthly)

    if len(monthly) >= 6:
        first = monthly.head(3)["price"].mean()
        last = monthly.tail(3)["price"].mean()

        if last > first:
            print(f"Ceny rosną (z {first:.0f} do {last:.0f})")
        elif last < first:
            print(f"Ceny spadają (z {first:.0f} do {last:.0f})")
        else:
            print("Ceny stabilne")

def main():
    try:
        df_se = load_data("data/fn2_sweden.csv")
        analyze_trend(df_se, "Szwecja")
    except:
        pass

    try:
        df_pl = load_data("data/fn2_poland.csv")
        analyze_trend(df_pl, "Polska")
    except:
        pass

if __name__ == "__main__":
    main()
