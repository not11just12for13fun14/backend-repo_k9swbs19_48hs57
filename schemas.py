"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List

# Example schemas (you can keep or remove if not used):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# --------------------------------------------------
# Pizza App Schemas
# --------------------------------------------------

class Pizza(BaseModel):
    """
    Pizza menu items
    Collection name: "pizza"
    """
    name: str
    description: Optional[str] = None
    price: float = Field(..., ge=0)
    image_url: Optional[str] = None
    vegetarian: bool = False
    spicy: bool = False
    sizes: List[str] = ["Small", "Medium", "Large"]

class OrderItem(BaseModel):
    pizza_id: str
    name: str
    size: str
    quantity: int = Field(1, ge=1)
    unit_price: float = Field(..., ge=0)
    toppings: List[str] = []

class Order(BaseModel):
    """
    Customer orders
    Collection name: "order"
    """
    customer_name: str
    phone: str
    address: str
    items: List[OrderItem]
    subtotal: float = Field(..., ge=0)
    tax: float = Field(..., ge=0)
    total: float = Field(..., ge=0)
    status: str = Field("pending", description="pending, confirmed, delivered, cancelled")
