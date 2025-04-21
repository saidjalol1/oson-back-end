from sqlalchemy import Column, Integer, String, ForeignKey, Text, Table, Boolean, Float, DateTime, Numeric, Enum
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from store import db_conf
import enum

class UserRole(enum.Enum):
    SUPERUSER = "superuser"
    ADMIN = "admin"
    STAFF = "staff"


class User(db_conf.Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)  
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    manager = relationship("User", remote_side=[id], back_populates="staffs")
    staffs = relationship("User", back_populates="manager")

    stores = relationship("Store", back_populates="boss")
    sales = relationship("Sale", back_populates="owner")


class Provider(db_conf.Base):
    __tablename__ = "provider"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    phone_number = Column(String)
    phone_number2 = Column(String)
    store_id = Column(Integer, ForeignKey("store.id"), nullable=False)
    
    store = relationship("Store", back_populates="providers")
    items_provided = relationship("StoreProductReportsIn", back_populates="provider")
    
    
    @hybrid_property
    def debt_left(self):
        return sum([i.debt_left for i in self.items_provided])
    
    @hybrid_property
    def total(self):
        return sum([i.total for i in self.items_provided])
    
    
class Store(db_conf.Base):
    __tablename__ = "store"
    id = Column(Integer, primary_key=True, index=True)
    boss_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    boss = relationship("User", back_populates="stores")
    products = relationship("Product", back_populates="store")
    categories = relationship("ProductCategory", back_populates="store")
    
    providers = relationship("Provider", back_populates="store")
    sales = relationship("Sale", back_populates="store")  
    

class ProductCategory(db_conf.Base):
    __tablename__ = "category"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    store_id = Column(Integer, ForeignKey("store.id"), nullable=False)
    store = relationship("Store", back_populates="categories")
    products = relationship("Product", back_populates="category")
    
    
class Product(db_conf.Base):
    __tablename__ = "product"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    barcode = Column(String, nullable=False)
    store_id = Column(Integer, ForeignKey("store.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("category.id"), nullable=True)
    
    store = relationship("Store", back_populates="products")   
    category = relationship("ProductCategory", back_populates="products")   
    store_reports_in = relationship("StoreProductReportsIn", back_populates="product")
    store_reports_out = relationship("StoreProductReportsOut", back_populates="product")


class StoreProductReportsIn(db_conf.Base):
    __tablename__ = "store_product_reports_in"
    id = Column(Integer, primary_key=True, index=True)
    quantity_in = Column(Integer, nullable=False)    
    quantity_left = Column(Integer, nullable=False)
    price = Column(Numeric(10, 3), nullable=False)
    sale_price = Column(Numeric(10, 3), nullable=False)
    date_added = Column(DateTime, default=db_conf.current_time)
    product_id = Column(Integer, ForeignKey("product.id"))
    provider_id = Column(Integer, ForeignKey("provider.id"))
    payment = Column(Numeric(10, 3))
    
    
    product = relationship("Product", back_populates="store_reports_in")
    provider  = relationship("Provider", back_populates="items_provided")
    sold_items = relationship("SaleItems", back_populates="product")
    payments = relationship("ProviderPayment", back_populates="report")
    
    @hybrid_property
    def debt_left(self):
        total = self.price * self.quantity_in
        return (total - self.payment) - sum([i.payment for i in self.payments])
    
    @hybrid_property
    def total(self):
        return self.price * self.quantity_in


class ProviderPayment(db_conf.Base):
    __tablename__ = "payment"
    id = Column(Integer, primary_key=True, index=True)
    payment = Column(Numeric(10, 3))
    date_added = Column(DateTime, default=db_conf.current_time)
    report_id = Column(Integer, ForeignKey("store_product_reports_in.id"))
    
    report = relationship(StoreProductReportsIn, back_populates="payments")
    

class StoreProductReportsOut(db_conf.Base):
    __tablename__ = "store_product_reports_out"
    id = Column(Integer, primary_key=True, index=True)
    quantity_out = Column(Integer, nullable=False)    
    price = Column(Numeric(10,3), nullable=False)
    sale_price = Column(Numeric(10,3) ,nullable=False)
    date_added = Column(DateTime, default=db_conf.current_time)
    product_id = Column(Integer, ForeignKey("product.id"))
    owner_id = Column(Integer, nullable=False)
    owner_type = Column(String, nullable=False)
    product = relationship("Product", back_populates="store_reports_out")


class Sale(db_conf.Base):
    __tablename__ = "sales"
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("store.id"), nullable=False)
    card_payment = Column(Numeric(10, 3))
    cash_payment = Column(Numeric(10, 3))
    debt_payment = Column(Numeric(10, 3))
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    debt = Column(Numeric(10, 3))
    total = Column(Numeric(10, 3))
    
    client_name = Column(String)
    client_number = Column(String)
    client_number2 = Column(String)
    date_added = Column(DateTime, default=db_conf.current_time)
    store = relationship("Store", back_populates="sales")   
    owner = relationship("User", back_populates="sales")   
    items = relationship("SaleItems", back_populates="sale")   
    

class SaleItems(db_conf.Base):
    __tablename__ = "sale_items"
    id = Column(Integer, primary_key=True, index=True)
    quantity = Column(Integer)
    
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("store_product_reports_in.id"))
    
    sale = relationship("Sale", back_populates="items")   
    product = relationship("StoreProductReportsIn", back_populates = "sold_items")