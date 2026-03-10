from fastapi import FastAPI

app = FastAPI()

#Ass2-Q3-list for feedback
feedback = []

#Ass2-Q6-product list
orders = []

# Product List
products = [
    {"id": 1, "name": "Mouse", "price": 500, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Keyboard", "price": 1200, "category": "Electronics", "in_stock": True},
    {"id": 3, "name": "Monitor", "price": 8000, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Headphones", "price": 2000, "category": "Electronics", "in_stock": True},

    # Question 1 : Add 3 More Products
    {"id": 5, "name": "Laptop Stand", "price": 1200, "category": "Accessories", "in_stock": True},
    {"id": 6, "name": "Mechanical Keyboard", "price": 3500, "category": "Accessories", "in_stock": True},
    {"id": 7, "name": "Webcam", "price": 2200, "category": "Electronics", "in_stock": False}
]

# Home API
@app.get("/")
def home():
    return {"message": "Welcome to Ecommerce API"}

# Get All Products
@app.get("/products")
def get_products():
    return {"products": products, "total": len(products)}

#Question 2 :Add a Category Filter Endpoint
@app.get("/products/category/{category_name}")
def get_products_by_category(category_name: str):
    filtered_products = []

    for product in products:
        if product["category"].lower() == category_name.lower():
            filtered_products.append(product)

    return {
        "category": category_name,
        "products": filtered_products,
        "total": len(filtered_products)
    }

# Question 3 : Show Only In-Stock Products
@app.get("/products/instock")
def get_instock_products():
    instock_products = []

    for product in products:
        if product["in_stock"] == True:
            instock_products.append(product)

    return {
        "products": instock_products,
        "count": len(instock_products)
    }

#Question 4 :Build a Store Info Endpoint
@app.get("/store/summary")
def store_summary():
    total_products = len(products)

    instock_count = len([p for p in products if p["in_stock"]])
    outofstock_count = len([p for p in products if not p["in_stock"]])

    categories = list(set([p["category"] for p in products]))

    return {
        "total_products": total_products,
        "in_stock": instock_count,
        "out_of_stock": outofstock_count,
        "categories": categories
    }

#Question 5:Search Products by Name
@app.get("/products/search/{keyword}")
def search_products(keyword: str):
    matched_products = []

    for product in products:
        if keyword.lower() in product["name"].lower():
            matched_products.append(product)

    if len(matched_products) == 0:
        return {"message": "No products matched your search"}

    return {
        "products": matched_products,
        "total_matches": len(matched_products)
    }

#Q6 :Cheapest & Most Expensive Product
@app.get("/products/deals")
def product_deals():
    best_deal = min(products, key=lambda p: p["price"])
    premium_pick = max(products, key=lambda p: p["price"])

    return {
        "best_deal": best_deal,
        "premium_pick": premium_pick
    }


#Ass 2
#Q1 :Filter Products by Minimum Price
@app.get("/products/filter")
def filter_products(category: str = None, max_price: int = None, min_price: int = None):
    
    filtered_products = products

    if category:
        filtered_products = [p for p in filtered_products if p["category"].lower() == category.lower()]

    if min_price:
        filtered_products = [p for p in filtered_products if p["price"] >= min_price]

    if max_price:
        filtered_products = [p for p in filtered_products if p["price"] <= max_price]

    return {
        "products": filtered_products,
        "total": len(filtered_products)
    }

#Q2 :Get Only the Price of a Product
@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):
    
    for product in products:
        if product["id"] == product_id:
            return {
                "name": product["name"],
                "price": product["price"]
            }

    return {"error": "Product not found"}

#Q3 :Accept Customer Feedback

#pydantic model
from pydantic import BaseModel, Field
from typing import Optional

class CustomerFeedback(BaseModel):
    customer_name: str = Field(..., min_length=2)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)

#post endpoint
@app.post("/feedback")
def submit_feedback(data: CustomerFeedback):
    
    feedback.append(data.dict())

    return {
        "message": "Feedback submitted successfully",
        "feedback": data,
        "total_feedback": len(feedback)
    }

#Q4 : Build a Product Summary Dashboard

@app.get("/products/summary")
def products_summary():

    total_products = len(products)

    in_stock_count = len([p for p in products if p["in_stock"]])
    out_of_stock_count = len([p for p in products if not p["in_stock"]])

    most_expensive_product = max(products, key=lambda p: p["price"])
    cheapest_product = min(products, key=lambda p: p["price"])

    categories = list(set([p["category"] for p in products]))

    return {
        "total_products": total_products,
        "in_stock_count": in_stock_count,
        "out_of_stock_count": out_of_stock_count,
        "most_expensive": {
            "name": most_expensive_product["name"],
            "price": most_expensive_product["price"]
        },
        "cheapest": {
            "name": cheapest_product["name"],
            "price": cheapest_product["price"]
        },
        "categories": categories
    }

#Q5 :Validate & Place a Bulk Order

#OrderItem Model
from pydantic import BaseModel, Field
from typing import List

class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1, le=50)

#BulkOrder Model
from typing import List

class BulkOrder(BaseModel):
    company_name: str = Field(..., min_length=2)
    contact_email: str = Field(..., min_length=5)
    items: List[OrderItem] = Field(..., min_items=1)

#Endpoint
@app.post("/orders/bulk")
def bulk_order(order: BulkOrder):

    confirmed = []
    failed = []
    grand_total = 0

    for item in order.items:

        product = next((p for p in products if p["id"] == item.product_id), None)

        if not product:
            failed.append({
                "product_id": item.product_id,
                "reason": "Product not found"
            })
            continue

        if not product["in_stock"]:
            failed.append({
                "product_id": item.product_id,
                "reason": f"{product['name']} is out of stock"
            })
            continue

        subtotal = product["price"] * item.quantity
        grand_total += subtotal

        confirmed.append({
            "product": product["name"],
            "qty": item.quantity,
            "subtotal": subtotal
        })

    return {
        "company": order.company_name,
        "confirmed": confirmed,
        "failed": failed,
        "grand_total": grand_total
    }

#Q6 :Order Status Tracker

#Update POST /orders
from pydantic import BaseModel

class Order(BaseModel):
    product_id: int
    quantity: int


@app.post("/orders")
def create_order(order: Order):

    order_data = {
        "id": len(orders) + 1,
        "product_id": order.product_id,
        "quantity": order.quantity,
        "status": "pending"
    }

    orders.append(order_data)

    return order_data

#Create GET /orders/{order_id}
@app.get("/orders/{order_id}")
def get_order(order_id: int):

    for order in orders:
        if order["id"] == order_id:
            return order

    return {"error": "Order not found"}

#Create PATCH /orders/{order_id}/confirm
@app.patch("/orders/{order_id}/confirm")
def confirm_order(order_id: int):

    for order in orders:
        if order["id"] == order_id:
            order["status"] = "confirmed"
            return order

    return {"error": "Order not found"}


























