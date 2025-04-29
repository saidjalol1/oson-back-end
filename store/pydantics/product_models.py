from datetime import date, datetime
from typing import Union, Optional, List
from pydantic import BaseModel


class Category(BaseModel):
    name : str
    store_id : int
    
    
class ProductIn(BaseModel):
    price : float
    sale_price : float
    quantity_in: int
    store_id: int
    provider_id : Optional[int] = None
    payment : Optional[int] = None
    id: int
    

class ProductCreate(BaseModel):
    name : str
    store_id: int
    category_id: int
    
    
class ProductUpdate(BaseModel):
    id:int
    name: str
    category_id: int
    

class ProductDelete(BaseModel):
    id:int


class StoreInReport(BaseModel):
    id: int
    quantity_in : int
    quantity_left : int
    price : float
    sale_price : float
    date_added : datetime
    product_id : int

    
class ProductOut(BaseModel):
    id: int
    name : str
    barcode : str
    store_reports_in : List[StoreInReport]
    category : Category
    category_id : int
    class Config:
        from_attributes = True


class CategoryOut(Category):
    id: int
    products: List[ProductOut]
    class Config:
        from_attributes = True


class CategoryUpdate(BaseModel):
    id:int
    name : str
    store_id : int
    

class StoreOut(BaseModel):
    id : int
    products : List[ProductOut]
    
    class Config:
        from_attributes = True


class WarningResponse(BaseModel):
    warning: str
    
class PaymentOut(BaseModel):
    id: int
    payment : int
    date_added: datetime


class StoreReportInOut(StoreInReport):
    product: ProductOut
    debt_left: int
    total: int
    payments: List[PaymentOut]
    class Config:
        from_attributes = True


class ProviderIn(BaseModel):
    store_id: int
    full_name : str
    phone_number : str
    phone_number2 : str
    
    
class ProviderEdit(BaseModel):
    id:int
    store_id: int
    full_name : str
    phone_number : str
    phone_number2 : str
    
    
class ProviderOut(ProviderIn):
    id: int
    items_provided : Optional[List[StoreReportInOut]] = None
    debt_left: Union[float]
    total: Union[float]
    

class ProductInsOut(BaseModel):
    id: int
    product: Optional[ProductOut] = None
    payment: float
    quantity_in : int
    price: int
    date_added : datetime
    total: int
    debt_left: Optional[int] = None
    provider : Optional[ProviderOut] = None
    
    class Config:
        from_attributes = True
        