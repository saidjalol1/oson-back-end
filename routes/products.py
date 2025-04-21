from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional, Union, List
from dependencies import injections
from store.pydantics import user_models, product_models, sale
from store.models import User, Store, Product, StoreProductReportsIn, UserRole, ProductCategory,Provider, ProviderPayment
from dependencies.barcode_generator import generate_barcode
from sqlalchemy.exc import IntegrityError   

router = APIRouter(
    tags=["Products"]
)

@router.get("/providers", response_model=List[product_models.ProviderOut])
async def  get_providers(current_user =  injections.admin_user,db = injections.database_dep):
    store = db.query(Store)
    if current_user.role == UserRole.ADMIN:
        store = store.filter(Store.boss_id == current_user.id).first()
    if current_user.role == UserRole.STAFF:
        store = store.filter(Store.boss_id == current_user.manager_id).first()
    
    return store.providers


@router.post("/provider-create")
async def  get_providers(provider: product_models.ProviderIn,current_user =  injections.admin_user,db = injections.database_dep):
    return await injections.session_manager(Provider(**provider.model_dump()), db)

@router.post("/provider-edit")
async def  get_providers(provider: product_models.ProviderEdit,current_user =  injections.admin_user,db = injections.database_dep):
    prov = db.query(Provider).filter(Provider.id == provider.id).first()
    
    if not prov:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    for field, value in provider.model_dump().items():
        setattr(prov, field, value)

    db.commit()
    db.refresh(prov)
    return prov

@router.post("/providerpay")
async def sale_pay(payment_obj: sale.ProviderPay,
                        current_user  =  injections.admin_user, 
                        db = injections.database_dep):
    payment = await injections.session_manager(ProviderPayment(
        **{
            "report_id" :payment_obj.report_id,
            "payment": payment_obj.payment
        }
    ), db)
    return {"message":"Paid successfully"}


@router.get("/product", response_model=product_models.StoreOut)
async def  get_products(current_user =  injections.user_or_admin,db = injections.database_dep):
    store = db.query(Store)
    if current_user.role == UserRole.ADMIN:
        store = store.filter(Store.boss_id == current_user.id).first()
    if current_user.role == UserRole.STAFF:
        store = store.filter(Store.boss_id == current_user.manager_id).first()
    return store
     

@router.post("/product-create", response_model=Union[product_models.ProductOut, product_models.WarningResponse])
async def product_create(product: product_models.ProductCreate,
                        current_user : User =  injections.admin_user, 
                        db = injections.database_dep):
    
    """ this Route is to create product in the store by providing id of the store"""
    try:
        existence_check = db.query(Product).filter(Product.name == product.name, product.store_id == product.store_id).first()
        if existence_check:
            return {"warning":"Bu nom ostida mahsulot mavjud omborda boshqa nom bilan urinib ko'ring !!!"}
        barcode = generate_barcode(product.name)
        _product_ = await injections.session_manager(Product(**{"name":product.name,"barcode":barcode, "store_id":product.store_id, "category_id": product.category_id}), db)
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig)
        injections.error_messages(error_msg)
    return _product_


@router.post("/product-enter")
async def product_create(product: product_models.ProductIn, current_user: User = injections.admin_user, db = injections.database_dep):
    """ this Route is to enter product in the store by providing id of the store"""
    try:
        _product_ = db.query(Product).filter(Product.id == product.id, Product.store_id == product.store_id).first()
        if _product_:
            _product_in_report = await injections.session_manager(StoreProductReportsIn(
                **{
                    "quantity_in": product.quantity_in, 
                    "quantity_left": product.quantity_in,  # Ensure correct field here
                    "price": product.price, 
                    "sale_price": product.sale_price,
                    "product_id": _product_.id,
                    "provider_id": product.provider_id
                }), db
            )
            return {"message": "success"}
        else:
            return {"warning": "Bu Mahsulot omborda topilmadi !!!"}
    except Exception as e:
        return {"error": str(e)}


@router.post("/product-update", response_model=product_models.ProductOut)
async def product_update(product: product_models.ProductUpdate,
                        current_user : User =  injections.admin_user, 
                        db = injections.database_dep):
    
    """ this Route is to Update product in the store by providing id of the store"""
    __product__ = db.query(Product).filter(Product.id == product.id).first()
    __product__.name = product.name
    __product__.category_id = product.category_id
    return await injections.session_manager(__product__, db)

    
@router.delete("/product-delete")
async def product_delete(product: product_models.ProductDelete,
                        current_user : User =  injections.admin_user, 
                        db = injections.database_dep):
    
    """ this Route is to delete product in the store by providing id of the store"""
    __product__ = db.query(Product).filter(Product.id == product.id).first()
    for i in __product__.store_reports_in:
        for j in i.sold_items:
            db.delete(j.sale)
            db.delete(j)
        db.delete(i)
    for i in __product__.store_reports_out:
        db.delete(i)
    db.delete(__product__)
    db.commit()
    return {"message":"Deleted successfully"}

    
@router.post("/category-create", response_model=Union[product_models.CategoryOut,product_models.WarningResponse])
async def product_crtryeate(category: product_models.Category,
                        current_user : User =  injections.admin_user, 
                        db = injections.database_dep):
    
    """ this Route is to create category in the store by providing id of the store"""
    existence_check = db.query(ProductCategory).filter(ProductCategory.name == category.name, ProductCategory.store_id == category.store_id).first()
    if existence_check:
        return {"warning":"Bu nom ostida Categoriya mavjud omborda boshqa nom bilan urinib ko'ring !!!"}
    
    return await injections.session_manager(ProductCategory(**category.model_dump()), db)


@router.post("/category-update", response_model=Union[product_models.CategoryOut,product_models.WarningResponse])
async def product_update(category: product_models.CategoryUpdate,
                        current_user : User =  injections.admin_user, 
                        db = injections.database_dep):
    
    """ this Route is to update category in the store by providing id of the store"""
    existence_check = db.query(ProductCategory).filter(ProductCategory.store_id == category.store_id, ProductCategory.id == category.id).first()
    if existence_check:
        existence_check.name = category.name
        return  await injections.session_manager(existence_check, db)
    return {"warning":"Bu nom ostida Categoriya mavjud emas !!!"}


@router.get("/categories", response_model=List[product_models.CategoryOut])
async def  get_products(current_user =  injections.user_or_admin,db = injections.database_dep):
    store = db.query(Store)
    if current_user.role == UserRole.ADMIN:
        store = store.filter(Store.boss_id == current_user.id).first()
    if current_user.role == UserRole.STAFF:
        store = store.filter(Store.boss_id == current_user.manager_id).first()
    categories = store.categories
    
    return categories
    

@router.get("/products-in", response_model=List[product_models.ProductInsOut])
async def  get_reports(current_user =  injections.user_or_admin,db = injections.database_dep):
    store = db.query(Store)
    if current_user.role == UserRole.ADMIN:
        store = store.filter(Store.boss_id == current_user.id).first()
    if current_user.role == UserRole.STAFF:
        store = store.filter(Store.boss_id == current_user.manager_id).first()
    return db.query(StoreProductReportsIn).join(StoreProductReportsIn.product).filter(
        StoreProductReportsIn.product.has(store_id=store.id)
    ).all()