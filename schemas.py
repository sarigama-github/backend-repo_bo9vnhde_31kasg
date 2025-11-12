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

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: Optional[str] = Field(None, description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Collection(BaseModel):
    """
    Fashion collections (e.g., Men's Luxury, Women's Couture, Streetwear)
    Collection name: "collection"
    """
    slug: str = Field(..., description="URL-friendly identifier, e.g., mens-luxury")
    title: str = Field(..., description="Display name of the collection")
    description: Optional[str] = Field(None, description="Short description")
    cover_image: Optional[HttpUrl] = Field(None, description="Hero/cover image URL")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in KES")
    category: str = Field(..., description="Category, e.g., accessories, apparel")
    gender: Optional[str] = Field(None, description="men | women | unisex")
    collection: Optional[str] = Field(None, description="Collection slug this belongs to")
    images: Optional[List[HttpUrl]] = Field(default_factory=list, description="Image URLs")
    tags: Optional[List[str]] = Field(default_factory=list, description="Searchable tags/keywords")
    in_stock: bool = Field(True, description="Whether product is in stock")

class ChatMessage(BaseModel):
    """
    Stores messages for AI Fashion Concierge conversations
    Collection name: "chatmessage"
    """
    session_id: str = Field(..., description="Conversation session identifier")
    role: str = Field(..., description="user | assistant")
    content: str = Field(..., description="Message text")

# Add more schemas as needed for orders, carts, etc.
