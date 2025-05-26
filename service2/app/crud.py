from sqlalchemy.orm import Session
from . import models, schemas
import httpx

def get_order(db: Session, order_id: int):
    return db.query(models.Order).filter(models.Order.id == order_id).first()

def get_orders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Order).offset(skip).limit(limit).all()

def create_order(db: Session, order: schemas.OrderCreate):
    # 여기서는 Service1의 아이템을 확인하는 로직이 있을 수 있습니다.
    # 실제 프로덕션에서는 메시지 큐나 적절한 오류 처리를 사용해야 합니다.
    try:
        # httpx.get("http://service1:8081/items/{order.item_id}")
        # 아이템 재고 확인 및 업데이트 로직
        pass
    except Exception as e:
        print(f"Error checking item availability: {e}")
    
    db_order = models.Order(
        customer_id=order.customer_id,
        item_id=order.item_id,
        quantity=order.quantity,
        total_price=order.total_price,
        shipping_address=order.shipping_address,
        status=order.status
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def update_order(db: Session, order_id: int, order: schemas.OrderUpdate):
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    
    update_data = order.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_order, key, value)
    
    db.commit()
    db.refresh(db_order)
    return db_order

def delete_order(db: Session, order_id: int):
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    db.delete(db_order)
    db.commit()
    return db_order