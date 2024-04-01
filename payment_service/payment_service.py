from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uvicorn
import os

app = FastAPI()

# Подключение к базе данных оплаты
PAYMENT_DATABASE_URL = "sqlite:///./payment.db"  # Используем SQLite 
payment_engine = create_engine(PAYMENT_DATABASE_URL)

# Создание базового класса для моделей SQLAlchemy оплаты
PaymentBase = declarative_base()

# Определение модели Payment
class Payment(PaymentBase):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, index=True)
    status = Column(String)

# Создание таблицы в базе данных оплаты
PaymentBase.metadata.create_all(bind=payment_engine)

# Создание сессии SQLAlchemy для оплаты
PaymentSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=payment_engine)

# POST-запрос для создания записи об оплате
@app.post("/payment/{order_id}")
def create_payment(order_id: int):
    db = PaymentSessionLocal()
    
    # Моковая функция для имитации обработки оплаты
    payment_status = "paid" if order_id % 2 == 0 else "pending"
    
    # Создание объекта Payment и добавление в БД оплаты
    db_payment = Payment(order_id=order_id, status=payment_status)
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)

    db.close()

    return {"message": f"Payment processed for order {order_id}", "payment_id": db_payment.id}

# GET-запрос для чтения данных об оплате из БД
@app.get("/payment/{order_id}")
def read_payment(order_id: int):
    db = PaymentSessionLocal()
    payment = db.query(Payment).filter(Payment.order_id == order_id).first()
    db.close()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    return {"order_id": payment.order_id, "status": payment.status}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)