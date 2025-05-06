from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, desc
from datetime import datetime, timedelta
from typing import Optional
from datetime import date
from store import db_conf
from store.db_conf import get_db
from dependencies import injections 
from store.models import Store, Product, Sale, SaleItems, User, StoreProductReportsIn, Provider, UserRole

router = APIRouter()



from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, and_, or_
from datetime import datetime, timedelta
from typing import List
from pydantic import BaseModel

router = APIRouter(tags=["store_stats"])

# Helper function to get current store (you'll need to implement auth)
def get_current_store(store_id: int, db: Session = Depends(get_db)):
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    return store

# Pydantic models for responses
class SalesSummary(BaseModel):
    total: float
    cash: float
    card: float
    debt: float
    count: int

class ProductSales(BaseModel):
    product_id: int
    product_name: str
    quantity_sold: int
    total_amount: float

class ProviderDebt(BaseModel):
    provider_id: int
    provider_name: str
    total_debt: float
    phone_number: str

class InventoryAlert(BaseModel):
    product_id: int
    product_name: str
    quantity_left: int
    barcode: str

class StaffPerformance(BaseModel):
    staff_id: int
    staff_name: str
    sales_count: int
    total_sales: float


class SaleSummaryResponse(BaseModel):
    date: date
    total_sales: float
    card_payments: float
    cash_payments: float
    debt_payments: float
    total_items_sold: int


@router.get("/stores/sales-summary", response_model=list[SaleSummaryResponse])
async def get_sales_summary(
    start_date: Optional[date] = Query(None, description="Start date for filtering"),
    end_date: Optional[date] = Query(None, description="End date for filtering"),
    min_card_payment: Optional[float] = Query(None, description="Minimum card payment amount"),
    max_card_payment: Optional[float] = Query(None, description="Maximum card payment amount"),
    min_cash_payment: Optional[float] = Query(None, description="Minimum cash payment amount"),
    max_cash_payment: Optional[float] = Query(None, description="Maximum cash payment amount"),
    min_debt_payment: Optional[float] = Query(None, description="Minimum debt payment amount"),
    max_debt_payment: Optional[float] = Query(None, description="Maximum debt payment amount"),
    db: Session = Depends(get_db),
    current_user = injections.admin_user
):
    
    store = db.query(Store)
    if current_user.role == UserRole.ADMIN:
        store = store.filter(Store.boss_id == current_user.id).first()
    if current_user.role == UserRole.STAFF:
        store = store.filter(Store.boss_id == current_user.manager_id).first()
    
    store_id = store.id
    # Base query
    query = db.query(
        func.date(Sale.date_added).label("date"),
        func.sum(Sale.total).label("total_sales"),
        func.sum(Sale.card_payment).label("card_payments"),
        func.sum(Sale.cash_payment).label("cash_payments"),
        func.sum(Sale.debt_payment).label("debt_payments"),
        func.sum(SaleItems.quantity).label("total_items_sold")
    ).join(
        SaleItems, Sale.id == SaleItems.sale_id
    ).filter(
        Sale.store_id == store_id
    ).group_by(
        func.date(Sale.date_added)
    ).order_by(
        func.date(Sale.date_added)
    )

    # Date filtering
    if start_date:
        query = query.filter(func.date(Sale.date_added) >= start_date)
    if end_date:
        query = query.filter(func.date(Sale.date_added) <= end_date)

    # Payment filtering
    if min_card_payment is not None:
        query = query.filter(Sale.card_payment >= min_card_payment)
    if max_card_payment is not None:
        query = query.filter(Sale.card_payment <= max_card_payment)
    if min_cash_payment is not None:
        query = query.filter(Sale.cash_payment >= min_cash_payment)
    if max_cash_payment is not None:
        query = query.filter(Sale.cash_payment <= max_cash_payment)
    if min_debt_payment is not None:
        query = query.filter(Sale.debt_payment >= min_debt_payment)
    if max_debt_payment is not None:
        query = query.filter(Sale.debt_payment <= max_debt_payment)

    results = query.all()
    return [{
        "date": row.date,
        "total_sales": float(row.total_sales) if row.total_sales else 0.0,
        "card_payments": float(row.card_payments) if row.card_payments else 0.0,
        "cash_payments": float(row.cash_payments) if row.cash_payments else 0.0,
        "debt_payments": float(row.debt_payments) if row.debt_payments else 0.0,
        "total_items_sold": row.total_items_sold if row.total_items_sold else 0
    } for row in results]





@router.get("/inventory/value")
async def get_inventory_value(
    db: Session = Depends(get_db),
    current_user =  injections.admin_user,
):
    store = db.query(Store)
    if current_user.role == UserRole.ADMIN:
        store = store.filter(Store.boss_id == current_user.id).first()
    if current_user.role == UserRole.STAFF:
        store = store.filter(Store.boss_id == current_user.manager_id).first()
        
    """Get total value of inventory"""
    total_value = db.query(
        func.sum(StoreProductReportsIn.quantity_left * StoreProductReportsIn.price)
    ).join(
        Product, StoreProductReportsIn.product_id == Product.id
    ).filter(
        Product.store_id == store.id
    ).scalar()
    
    total_debt = db.query(Sale).filter(Sale.total > Sale.debt).all()
    
    return {
        "total_value": total_value or 0, 
        "total_debt":sum([i.total for i in total_debt]),
        "left_debt": sum([i.debt for i in total_debt])
    }

  