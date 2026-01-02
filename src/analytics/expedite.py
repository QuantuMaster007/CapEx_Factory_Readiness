from __future__ import annotations
import pandas as pd

def expedite_summary(lead: pd.DataFrame) -> pd.DataFrame:
    df = lead.copy()
    df["expedite_spend_usd"] = pd.to_numeric(df["expedite_spend_usd"], errors="coerce").fillna(0.0)
    summ = (df.groupby(["vendor","expedite_reason"], as_index=False)
              .agg(expedite_spend_usd=("expedite_spend_usd","sum"),
                   lines=("tool_id","count"),
                   tools=("tool_id","nunique")))
    return summ.sort_values("expedite_spend_usd", ascending=False)
