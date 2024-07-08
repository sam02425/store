from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models.database import Customer, Product, Inventory, CartItem, Planogram
from ..utils.db_utils import get_db_session
from pydantic import BaseModel
from typing import List
from ..config import config


app = FastAPI()

class CustomerCreate(BaseModel):
    face_encoding: str

class ProductCreate(BaseModel):
    name: str
    sku: str
    price: float

class InventoryUpdate(BaseModel):
    product_id: int
    quantity: int
    aisle_id: str

class CartItemCreate(BaseModel):
    customer_id: int
    product_id: int
    quantity: int

class PlanogramCreate(BaseModel):
    aisle_id: str
    product_id: int
    position_x: int
    position_y: int

@app.post("/customers/", response_model=int)
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db_session)):
    db_customer = Customer(face_encoding=customer.face_encoding)
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer.id

@app.post("/products/", response_model=int)
def create_product(product: ProductCreate, db: Session = Depends(get_db_session)):
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product.id

@app.put("/inventory/")
def update_inventory(inventory: InventoryUpdate, db: Session = Depends(get_db_session)):
    db_inventory = db.query(Inventory).filter_by(product_id=inventory.product_id, aisle_id=inventory.aisle_id).first()
    if db_inventory:
        db_inventory.quantity = inventory.quantity
    else:
        db_inventory = Inventory(**inventory.dict())
        db.add(db_inventory)
    db.commit()
    return {"status": "success"}

@app.post("/cart/")
def add_to_cart(cart_item: CartItemCreate, db: Session = Depends(get_db_session)):
    db_cart_item = CartItem(**cart_item.dict())
    db.add(db_cart_item)
    db.commit()
    return {"status": "success"}

@app.get("/cart/{customer_id}")
def get_cart(customer_id: int, db: Session = Depends(get_db_session)):
    cart_items = db.query(CartItem).filter(CartItem.customer_id == customer_id).all()
    return cart_items

@app.get("/inventory/{aisle_id}")
def get_inventory(aisle_id: str, db: Session = Depends(get_db_session)):
    inventory = db.query(Inventory).filter(Inventory.aisle_id == aisle_id).all()
    return inventory

@app.post("/planogram/")
def create_planogram(planogram: PlanogramCreate, db: Session = Depends(get_db_session)):
    db_planogram = Planogram(**planogram.dict())
    db.add(db_planogram)
    db.commit()
    return {"status": "success"}

@app.get("/planogram/{aisle_id}")
def get_planogram(aisle_id: str, db: Session = Depends(get_db_session)):
    planogram = db.query(Planogram).filter(Planogram.aisle_id == aisle_id).all()
    return planogram

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT)
