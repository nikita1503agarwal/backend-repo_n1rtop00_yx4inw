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

from pydantic import BaseModel, Field, EmailStr, HttpUrl
from typing import Optional, Literal, List

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
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

# Insurance for crypto staking
class Policy(BaseModel):
    """
    Policy collection schema for crypto staking insurance
    Collection name: "policy"
    """
    email: EmailStr = Field(..., description="Policy holder email")
    asset: Literal['ETH', 'SOL', 'ATOM', 'ADA', 'AVAX', 'DOT', 'MATIC', 'BNB', 'Other'] = Field(..., description="Staked asset")
    amount_staked: float = Field(..., gt=0, description="Amount staked (in asset units)")
    usd_value: float = Field(..., gt=0, description="USD value of stake at policy creation")
    coverage_percent: float = Field(..., gt=0, le=100, description="Coverage percentage of USD value")
    duration_days: int = Field(..., ge=7, le=365, description="Coverage duration in days")
    premium_usd: float = Field(..., ge=0, description="Premium to be paid in USD")
    status: Literal['active', 'cancelled', 'expired', 'pending'] = Field('active', description="Policy status")

# Fashion deals
class Deal(BaseModel):
    """
    Deals collection schema for apparel/brands discounts
    Collection name: "deal"
    """
    title: str = Field(..., description="Deal title")
    brand: str = Field(..., description="Brand or store e.g. Macy's, Nike")
    category: Literal['Men','Women','Kids','Sportswear','Shoes','Accessories','Home'] = Field(..., description="Category")
    url: HttpUrl = Field(..., description="Link to product/deal")
    image: Optional[HttpUrl] = Field(None, description="Image URL")
    price: float = Field(..., ge=0, description="Sale price")
    original_price: Optional[float] = Field(None, ge=0, description="Original price before discount")
    discount_percent: Optional[float] = Field(None, ge=0, le=100, description="Computed discount percent")
    tags: Optional[List[str]] = Field(default=None, description="Search tags")
    store: Optional[str] = Field(None, description="Store name if different from brand")

# Add your own schemas here:
# --------------------------------------------------

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
