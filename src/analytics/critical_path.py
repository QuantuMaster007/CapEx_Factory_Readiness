from __future__ import annotations
import pandas as pd

def compute_critical_path(tasks: pd.DataFrame, program: str, tool_id: str) -> pd.DataFrame:
    """Simple critical path = longest planned dependency chain using depends_on task_name list."""
    df = tasks[(tasks["program"]==program) & (tasks["tool_id"]==tool_id)].reset_index(drop=True).copy()
    name_to_idx = {n:i for i,n in enumerate(df["task_name"].tolist())}

    df["p_start"] = pd.to_datetime(df["planned_start"])
    df["p_finish"] = pd.to_datetime(df["planned_finish"])
    df["duration"] = (df["p_finish"] - df["p_start"]).dt.days.clip(lower=1)

    preds = {i: [] for i in range(len(df))}
    succs = {i: [] for i in range(len(df))}
    for i, row in df.iterrows():
        deps = [d.strip() for d in str(row.get("depends_on","") or "").split(",") if d.strip()]
        for d in deps:
            if d in name_to_idx:
                j = name_to_idx[d]
                preds[i].append(j)
                succs[j].append(i)

    indeg = {i: len(preds[i]) for i in preds}
    q = [i for i in indeg if indeg[i]==0]
    topo = []
    while q:
        n = q.pop(0)
        topo.append(n)
        for m in succs[n]:
            indeg[m] -= 1
            if indeg[m] == 0:
                q.append(m)

    dist = {i: float(df.loc[i,"duration"]) for i in range(len(df))}
    parent = {i: None for i in range(len(df))}
    for n in topo:
        for m in succs[n]:
            cand = dist[n] + float(df.loc[m,"duration"])
            if cand > dist[m]:
                dist[m] = cand
                parent[m] = n

    end = max(dist, key=lambda k: dist[k])
    path=[]
    cur=end
    while cur is not None:
        path.append(cur)
        cur = parent[cur]
    path = list(reversed(path))

    cp = df.loc[path, ["program","tool_id","task_id","task_name","workstream","gate","planned_start","planned_finish","status","risk_level","depends_on"]].copy()
    cp["cp_rank"] = range(1, len(cp)+1)
    return cp
