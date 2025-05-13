from datetime import date, datetime
from typing import Union, Optional, List
from pydantic import BaseModel
from .user_models import UserOut
from .product_models import Category


class SaleItems(BaseModel):
    quantity: float
    product_id: int
    
    class Config:
        from_attributes = True


class Sale(BaseModel):
    store_id: int
    card_payment : Optional[float] = None
    cash_payment : Optional[float] = None
    debt_payment : Optional[float] = None
    debt : Optional[float] = None
    total : Optional[float] = None
    items: List[SaleItems]
    
    client_name : Optional[str] = None
    client_number : Optional[str] = None
    client_number2 : Optional[str] = None
    class Config:
        from_attributes = True




# Sale Create Shcema
class Product(BaseModel):
    id: int
    name: str
    
class Report(BaseModel):
    quantity_in : float
    quantity_left : float
    product : Product
    price: float
    sale_price: float
    id: int
    
class SaleItem(BaseModel):
    quantity: float
    product_id: int
    product: Report
    
class SaleOut(BaseModel):
    id: int
    debt: float
    total: int
    card_payment :int = None
    cash_payment :int = None
    debt_payment :int = None
    owner : UserOut
    items : List[SaleItem]
    
# 1690618978212
class SaleDelete(BaseModel):
    id: int
    

class SalePay(BaseModel):
    id: int
    payment: int
    payment_type: str
    

class ProviderPay(BaseModel):
    report_id: int
    payment: int