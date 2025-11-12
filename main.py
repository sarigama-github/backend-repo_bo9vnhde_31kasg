import os
from typing import List, Optional
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from database import db, create_document, get_documents

app = FastAPI(title="Lou Vou Collections Kenya API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Schemas (Pydantic IO models) ----------
class CollectionIn(BaseModel):
    slug: str = Field(..., description="URL-friendly identifier, e.g., mens-luxury")
    title: str
    description: Optional[str] = None
    cover_image: Optional[str] = None

class ProductIn(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    gender: Optional[str] = Field(None, description="men | women | unisex")
    collection: Optional[str] = None
    images: Optional[List[str]] = []
    tags: Optional[List[str]] = []
    in_stock: bool = True

class StylistRequest(BaseModel):
    occasion: str
    gender: Optional[str] = None
    vibe: Optional[str] = None
    weather: Optional[str] = None
    budget_max: Optional[float] = None


@app.get("/")
def read_root():
    return {"message": "Lou Vou API running"}


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
            response["database_name"] = getattr(db, 'name', 'unknown')
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"

    return response


@app.get("/schema")
def get_schema():
    """Expose Pydantic schema definitions to admin tools/viewers."""
    try:
        import schemas as s
        # return class names for reference
        return {
            "schemas": [c for c in dir(s) if c[:1].isupper()],
            "info": "Pydantic models available. Each lowercased name maps to a collection.",
        }
    except Exception as e:
        return {"error": str(e)}


# ---------- Collections Endpoints ----------
@app.get("/api/collections")
def list_collections(limit: Optional[int] = Query(None, ge=1, le=100)):
    docs = get_documents("collection", {}, limit)
    for d in docs:
        d["_id"] = str(d.get("_id"))
    return {"items": docs}


@app.post("/api/collections")
def create_collection(payload: CollectionIn):
    cid = create_document("collection", payload.model_dump())
    return {"id": cid}


# ---------- Products Endpoints ----------
@app.get("/api/products")
def list_products(
    gender: Optional[str] = None,
    collection: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    q: Optional[str] = None,
    limit: Optional[int] = Query(24, ge=1, le=100),
):
    filt = {}
    if gender:
        filt["gender"] = gender
    if collection:
        filt["collection"] = collection
    if min_price is not None or max_price is not None:
        price_cond = {}
        if min_price is not None:
            price_cond["$gte"] = min_price
        if max_price is not None:
            price_cond["$lte"] = max_price
        filt["price"] = price_cond
    if q:
        filt["$or"] = [
            {"title": {"$regex": q, "$options": "i"}},
            {"description": {"$regex": q, "$options": "i"}},
            {"tags": {"$elemMatch": {"$regex": q, "$options": "i"}}},
        ]

    docs = get_documents("product", filt, limit)
    for d in docs:
        d["_id"] = str(d.get("_id"))
    return {"items": docs}


@app.post("/api/products")
def create_product(payload: ProductIn):
    pid = create_document("product", payload.model_dump())
    return {"id": pid}


# ---------- AI Virtual Stylist ----------
@app.post("/api/stylist")
def ai_stylist(req: StylistRequest):
    """Rule-based recommendations as a placeholder for AI.
    Filters products by gender, tags (occasion/vibe/weather), and budget.
    """
    filt: dict = {}
    if req.gender:
        filt["gender"] = req.gender

    tag_queries = [req.occasion]
    if req.vibe:
        tag_queries.append(req.vibe)
    if req.weather:
        tag_queries.append(req.weather)

    tag_queries = [t for t in tag_queries if t]
    if tag_queries:
        filt["tags"] = {"$in": [t.lower() for t in tag_queries]}

    if req.budget_max is not None:
        filt["price"] = {"$lte": req.budget_max}

    items = get_documents("product", filt, limit=12)
    for d in items:
        d["_id"] = str(d.get("_id"))

    intro = "Refined selections tailored to your moment."
    return {
        "message": intro,
        "criteria": req.model_dump(),
        "recommendations": items,
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
