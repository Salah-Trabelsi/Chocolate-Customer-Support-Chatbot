from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.sql import func

from app.core.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    dob = Column(Date, nullable=False)
    postcode = Column(String(50), nullable=False)
    first_line_address = Column(String(255), nullable=False)
    phone_number = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(20), unique=True, nullable=False, index=True)
    customer_id = Column(String(20), ForeignKey("customers.customer_id"), nullable=False)
    status = Column(String(50), nullable=False)
    payment_id = Column(String(20), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(20), ForeignKey("orders.order_id"), nullable=False)
    product_id = Column(String(100), nullable=False)
    product_name = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False)


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(String(20), unique=True, nullable=False, index=True)
    order_id = Column(String(20), ForeignKey("orders.order_id"), nullable=False)
    customer_id = Column(String(20), ForeignKey("customers.customer_id"), nullable=False)
    status = Column(String(50), nullable=False)
    payment_method = Column(String(100), nullable=False)
    amounts = Column(JSON, nullable=False)
    total_converted = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())