from fastapi import FastAPI, Query

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/v1/ownership/resolve")
def resolve_owner(cluster_id: str = Query(min_length=1) , namespace: str = Query(min_length=1)):
    return {
        "cluster_id": cluster_id,
        "namespace": namespace,
        "message:": "Chưa kết nối dữ liệu Rancher"
    }