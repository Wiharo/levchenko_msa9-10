from fastapi import FastAPI, HTTPException, Depends, status, Form
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import uvicorn
import os
from keycloak.keycloak_openid import KeycloakOpenID



app = FastAPI()

# Данные для подключения к Keycloak
KEYCLOAK_URL = "http://0.0.0.0:8180/"
KEYCLOAK_CLIENT_ID = "mikhin"
KEYCLOAK_REALM = "delivery_service_realm"
KEYCLOAK_CLIENT_SECRET = "WZD8DnZbd0i8IXub7UGu7Qn7nTrco2Zj"
KEYCLOAK_CLIENT_SECRET2 = "AliwqwCWP6RvWgENTnWaFvopI3G5s7lm"

keycloak_openid = KeycloakOpenID(server_url=KEYCLOAK_URL,
                                  client_id=KEYCLOAK_CLIENT_ID,
                                  realm_name=KEYCLOAK_REALM,
                                  client_secret_key=KEYCLOAK_CLIENT_SECRET)

user_token = ""


from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app)

@app.post("/get-token")
async def get_token(username: str = Form(...), password: str = Form(...)):
    try:
        # Получение токена
        token = keycloak_openid.token(grant_type=["password"],
                                      username=username,
                                      password=password)
        global user_token
        user_token = token
        return token
    except Exception as e:
        print(e)  # Логирование для диагностики
        raise HTTPException(status_code=400, detail="Не удалось получить токен")
    
def check_user_roles():
    global user_token
    token = user_token
    try:
        #userinfo = keycloak_openid.userinfo(token["access_token"])
        token = keycloak_openid.token("testuser", "1")
        token_info = keycloak_openid.introspect(token["access_token"])
        if "testRole" not in token_info["realm_access"]["roles"]:
            raise HTTPException(status_code=403, detail="Access denied")
        return token_info
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token or access denied")
    



# Подключение к базе данных
current_directory = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(current_directory, "test.db")
DATABASE_URL = f"sqlite:///{db_path}"  
engine = create_engine(DATABASE_URL)

# Создание базового класса для моделей SQLAlchemy
Base = declarative_base()

# Определение модели Delivery
class Delivery(Base):
    __tablename__ = "deliveries"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, index=True)
    status = Column(String)

# Создание таблицы в базе данных
Base.metadata.create_all(bind=engine)

# Создание сессии SQLAlchemy
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Моковая функция для имитации обработки оплаты
def simulate_payment(order_id: int):
    payment_status = "paid" if order_id % 2 == 0 else "pending"
    return {"order_id": order_id, "status": payment_status}

# Функция для создания доставки и записи в БД
def create_delivery_and_record(db, order_id: int):
    payment_result = simulate_payment(order_id)
    delivery_status = "processed" if payment_result["status"] == "paid" else "not processed"

    # Создание объекта Delivery и добавление в БД
    db_delivery = Delivery(order_id=order_id, status=delivery_status)
    db.add(db_delivery)
    db.commit()
    db.refresh(db_delivery)

    return {"message": f"Processing delivery for order {order_id}", "delivery_id": db_delivery.id}

# POST-запрос для создания доставки
@app.post("/delivery/{order_id}")
def create_delivery(order_id: int):
    if(check_user_roles()):
        db = SessionLocal()
        result = create_delivery_and_record(db, order_id)
        db.close()
        return result
    else:
        return "Wrong JWT Token"

# GET-запрос для чтения данных о доставке из БД
@app.get("/delivery/{order_id}")
def read_delivery(order_id: int):
    if(check_user_roles()):
        db = SessionLocal()
        delivery = db.query(Delivery).filter(Delivery.order_id == order_id).first()
        db.close()

        if not delivery:
            raise HTTPException(status_code=404, detail="Delivery not found")

        return {"order_id": delivery.order_id, "status": delivery.status}
    else:
        return "Wrong JWT Token"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)