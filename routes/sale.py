from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional, Union, List
from dependencies import injections
from store.pydantics import user_models, product_models, sale
from store.models import Store, StoreProductReportsIn,Sale, SaleItems , StoreProductReportsOut, UserRole, Product
from sqlalchemy.orm import joinedload, selectinload
from decimal import Decimal

router = APIRouter(
    tags=["Sotuv"]
)





# 2652430232520 - fanta
# 2363416188891 - pepsi
# 1724613084989 - prannik
@router.post("/sale", response_model= Union[sale.SaleOut, product_models.WarningResponse])
async def create_sale(sale:sale.Sale ,current_user = injections.user_or_admin, db = injections.database_dep):
    """
    Create a new sale with items
    """
    
    sale_obj = await injections.session_manager(Sale(
        store_id = sale.store_id,
        card_payment = sale.card_payment,
        cash_payment = sale.cash_payment,
        debt_payment = sale.debt_payment,
        total = sale.total,
        debt = sale.debt,
        owner_id = current_user.id,
        
        client_name = sale.client_name,
        client_number = sale.client_number,
        client_number2 = sale.client_number2,
    ), db)
    
    for i in sale.items:
        item = db.query(StoreProductReportsIn).filter(StoreProductReportsIn.id == i.product_id).first()
        # print(item.quantity_left, i.quantity)
        num = Decimal(str(item.quantity_left)) - Decimal(str(i.quantity))
        if item.quantity_left < i.quantity or num < 0:
            db.delete(sale_obj)
            db.commit()
            return {"warning":"Miqdorni To'gri kiriting"}
    
    for i in sale.items:
        item = db.query(StoreProductReportsIn).filter(StoreProductReportsIn.id == i.product_id).first()
        item.quantity_left =  float(Decimal(str(item.quantity_left)) - Decimal(str(i.quantity)))
        item = await injections.session_manager(item, db)
        item_out = await injections.session_manager(StoreProductReportsOut(
            quantity_out = i.quantity,
            price = item.price,
            sale_price = item.sale_price,
            product_id = i.product_id,
            owner_id = current_user.id,
            owner_type = "jh"
        ), db)
        sale_items = await injections.session_manager(SaleItems(
            quantity = i.quantity,
            sale_id = sale_obj.id,
            product_id = i.product_id
        ), db)
        
    return sale_obj



def get_all_sales(db, store_id):
    query = db.query(Sale)\
        .options(
            joinedload(Sale.store),
            joinedload(Sale.owner),
            selectinload(Sale.items).joinedload(SaleItems.product).joinedload(StoreProductReportsIn.product)
        )
    
    if store_id:
        query = query.filter(Sale.store_id == store_id)
        
    return query.all()


@router.get("/sales")
async def  get_products(current_user =  injections.user_or_admin,db = injections.database_dep):
    store = db.query(Store)
    if current_user.role == UserRole.ADMIN:
        store = store.filter(Store.boss_id == current_user.id).first()
    if current_user.role == UserRole.STAFF:
        store = store.filter(Store.boss_id == current_user.manager_id).first()
    
    return get_all_sales(db, store.id)


@router.delete("/sale-delete")
async def sale_delete(sale: sale.SaleDelete,
                        current_user  =  injections.admin_user, 
                        db = injections.database_dep):
    
    """ this Route is to delete sales in the store by providing id of the store"""
    __sales__ = db.query(Sale).filter(Sale.id == sale.id).first()
    for i in __sales__.items:
        db.delete(i)
        
    db.delete(__sales__)
    db.commit()
    return {"message":"Deleted successfully"}


@router.post("/salepay")
async def sale_pay(sale: sale.SalePay,
                        current_user  =  injections.admin_user, 
                        db = injections.database_dep):
    
    """ this Route is to pays sales in the store by providing id of the store"""
    __sales__ = db.query(Sale).filter(Sale.id == sale.id).first()
    __sales__.debt -= sale.payment
    if sale.payment_type == "card":
        __sales__.card_payment += sale.payment
        __sales__.debt_payment += sale.payment
    else:
        __sales__.cash_payment += sale.payment
        __sales__.debt_payment += sale.payment
        
    db.add(__sales__)
    db.commit()
    return {"message":"Paid successfully"}





