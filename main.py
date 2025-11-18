import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Policy, Deal

app = FastAPI(title="Deals Finder API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Deals Finder backend is running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response

# Basic schema endpoint to expose models for the built-in DB viewer
class SchemaResponse(BaseModel):
    schemas: List[str]

@app.get("/schema", response_model=SchemaResponse)
def get_schema():
    return {"schemas": ["user", "product", "policy", "deal"]}

# ------------------- Deals Endpoints -------------------

# Create a deal
@app.post("/deals")
def create_deal(deal: Deal):
    try:
        payload = deal.model_dump()
        # Auto compute discount if original_price provided
        op = payload.get("original_price")
        p = payload.get("price")
        if op and op > 0 and p is not None:
            payload["discount_percent"] = round(max(0.0, (1 - (p / op)) * 100), 2)
        inserted_id = create_document("deal", payload)
        return {"id": inserted_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# List/search deals
@app.get("/deals")
def list_deals(
    q: Optional[str] = Query(default=None, description="Search text"),
    brand: Optional[str] = None,
    category: Optional[str] = None,
    min_discount: Optional[float] = Query(default=None, ge=0, le=100),
    limit: int = Query(default=50, ge=1, le=200)
):
    try:
        filter_q: dict = {}
        if q:
            filter_q["$or"] = [
                {"title": {"$regex": q, "$options": "i"}},
                {"brand": {"$regex": q, "$options": "i"}},
                {"tags": {"$elemMatch": {"$regex": q, "$options": "i"}}},
            ]
        if brand:
            filter_q["brand"] = {"$regex": f"^{brand}$", "$options": "i"}
        if category:
            filter_q["category"] = {"$regex": f"^{category}$", "$options": "i"}
        if min_discount is not None:
            filter_q["discount_percent"] = {"$gte": float(min_discount)}

        docs = get_documents("deal", filter_q, limit)
        for d in docs:
            if isinstance(d.get("_id"), ObjectId):
                d["id"] = str(d.pop("_id"))
        # sort client-side by best discount then lowest price
        docs.sort(key=lambda x: (-(x.get("discount_percent") or 0), x.get("price") or 0))
        return {"items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Distinct brands for filter UI
@app.get("/brands")
def list_brands():
    try:
        names = db["deal"].distinct("brand") if db is not None else []
        names = sorted([n for n in names if n])
        return {"items": names[:200]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
