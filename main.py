import os
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Pizza, Order, OrderItem

app = FastAPI(title="Pizza API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CreatePizzaRequest(Pizza):
    pass

class CreateOrderRequest(BaseModel):
    customer_name: str
    phone: str
    address: str
    items: List[OrderItem]

@app.get("/")
def read_root():
    return {"message": "Pizza API is running"}

@app.get("/api/menu")
def get_menu():
    try:
        pizzas = get_documents("pizza")
        # Convert ObjectId to string
        for p in pizzas:
            p["id"] = str(p.pop("_id"))
        return pizzas
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/menu", status_code=201)
def add_pizza(pizza: CreatePizzaRequest):
    try:
        pizza_id = create_document("pizza", pizza)
        return {"id": pizza_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/order", status_code=201)
def create_order(payload: CreateOrderRequest):
    try:
        # Calculate totals
        subtotal = sum(item.unit_price * item.quantity for item in payload.items)
        tax = round(subtotal * 0.08, 2)
        total = round(subtotal + tax, 2)

        order = Order(
            customer_name=payload.customer_name,
            phone=payload.phone,
            address=payload.address,
            items=payload.items,
            subtotal=round(subtotal, 2),
            tax=tax,
            total=total,
            status="pending"
        )
        order_id = create_document("order", order)
        return {"id": order_id, "total": total}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/orders")
def list_orders():
    try:
        orders = get_documents("order")
        for o in orders:
            o["id"] = str(o.pop("_id"))
        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
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
            response["database_url"] = "✅ Configured"
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

    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
