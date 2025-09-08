# data_query_server.py
from mcp.server.fastmcp import FastMCP
import sys
import logging
from typing import Optional

logger = logging.getLogger('DataQuery')

# Fix UTF-8 encoding for Windows console
if sys.platform == 'win32' and hasattr(sys.stderr, 'reconfigure') and hasattr(sys.stdout, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')
    sys.stdout.reconfigure(encoding='utf-8')

# 内置数据集
EMBEDDED_DATA = {
    "users": [
        {"id": 1, "name": "张三", "age": 28, "city": "北京", "department": "技术部"},
        {"id": 2, "name": "李四", "age": 32, "city": "上海", "department": "销售部"},
        {"id": 3, "name": "王五", "age": 25, "city": "深圳", "department": "技术部"},
        {"id": 4, "name": "赵六", "age": 30, "city": "广州", "department": "市场部"},
        {"id": 5, "name": "孙七", "age": 27, "city": "杭州", "department": "技术部"},
    ],
    "products": [
        {"id": 1, "name": "笔记本电脑", "price": 5999, "category": "电子产品", "stock": 50},
        {"id": 2, "name": "无线鼠标", "price": 99, "category": "电子产品", "stock": 200},
        {"id": 3, "name": "机械键盘", "price": 399, "category": "电子产品", "stock": 80},
        {"id": 4, "name": "办公椅", "price": 899, "category": "家具", "stock": 30},
        {"id": 5, "name": "显示器", "price": 1299, "category": "电子产品", "stock": 45},
    ],
    "orders": [
        {"id": 1, "user_id": 1, "product_id": 1, "quantity": 1, "total": 5999, "date": "2024-01-15"},
        {"id": 2, "user_id": 2, "product_id": 2, "quantity": 2, "total": 198, "date": "2024-01-16"},
        {"id": 3, "user_id": 3, "product_id": 3, "quantity": 1, "total": 399, "date": "2024-01-17"},
        {"id": 4, "user_id": 1, "product_id": 4, "quantity": 1, "total": 899, "date": "2024-01-18"},
        {"id": 5, "user_id": 4, "product_id": 5, "quantity": 2, "total": 2598, "date": "2024-01-19"},
    ]
}

# Create an MCP server
mcp = FastMCP("DataQuery")

@mcp.tool()
def query_users(filter_by: Optional[str] = None, value: Optional[str] = None) -> dict:
    """查询用户数据。可以按字段过滤，如 filter_by='department', value='技术部'"""
    users = EMBEDDED_DATA["users"]
    
    if filter_by and value:
        filtered_users = [user for user in users if str(user.get(filter_by, "")).lower() == value.lower()]
        logger.info(f"Filtering users by {filter_by}={value}, found {len(filtered_users)} results")
        return {"success": True, "count": len(filtered_users), "data": filtered_users}
    
    logger.info(f"Retrieved all users, count: {len(users)}")
    return {"success": True, "count": len(users), "data": users}

@mcp.tool()
def query_products(filter_by: Optional[str] = None, value: Optional[str] = None) -> dict:
    """查询产品数据。可以按字段过滤，如 filter_by='category', value='电子产品'"""
    products = EMBEDDED_DATA["products"]
    
    if filter_by and value:
        if filter_by == "price_range":
            # 特殊处理价格范围查询，格式: "100-500"
            if "-" in value:
                min_price, max_price = map(int, value.split("-"))
                filtered_products = [p for p in products if min_price <= p["price"] <= max_price]
            else:
                filtered_products = []
        else:
            filtered_products = [product for product in products if str(product.get(filter_by, "")).lower() == value.lower()]
        
        logger.info(f"Filtering products by {filter_by}={value}, found {len(filtered_products)} results")
        return {"success": True, "count": len(filtered_products), "data": filtered_products}
    
    logger.info(f"Retrieved all products, count: {len(products)}")
    return {"success": True, "count": len(products), "data": products}

@mcp.tool()
def query_orders(filter_by: Optional[str] = None, value: Optional[str] = None) -> dict:
    """查询订单数据。可以按字段过滤，如 filter_by='user_id', value='1'"""
    orders = EMBEDDED_DATA["orders"]
    
    if filter_by and value:
        if filter_by in ["user_id", "product_id", "quantity"]:
            filtered_orders = [order for order in orders if order.get(filter_by) == int(value)]
        else:
            filtered_orders = [order for order in orders if str(order.get(filter_by, "")).lower() == value.lower()]
        
        logger.info(f"Filtering orders by {filter_by}={value}, found {len(filtered_orders)} results")
        return {"success": True, "count": len(filtered_orders), "data": filtered_orders}
    
    logger.info(f"Retrieved all orders, count: {len(orders)}")
    return {"success": True, "count": len(orders), "data": orders}

@mcp.tool()
def get_user_orders(user_id: int) -> dict:
    """获取指定用户的所有订单信息，包含用户详情和订单详情"""
    users = EMBEDDED_DATA["users"]
    orders = EMBEDDED_DATA["orders"]
    products = EMBEDDED_DATA["products"]
    
    # 查找用户
    user = next((u for u in users if u["id"] == user_id), None)
    if not user:
        return {"success": False, "message": f"用户 ID {user_id} 不存在"}
    
    # 查找用户订单
    user_orders = [order for order in orders if order["user_id"] == user_id]
    
    # 丰富订单信息（添加产品详情）
    enriched_orders = []
    for order in user_orders:
        product = next((p for p in products if p["id"] == order["product_id"]), None)
        enriched_order = order.copy()
        enriched_order["product_name"] = product["name"] if product else "未知产品"
        enriched_orders.append(enriched_order)
    
    result = {
        "user": user,
        "orders": enriched_orders,
        "total_orders": len(enriched_orders)
    }
    
    logger.info(f"Retrieved orders for user {user_id}, found {len(enriched_orders)} orders")
    return {"success": True, "data": result}

@mcp.tool()
def get_statistics() -> dict:
    """获取数据统计信息"""
    users = EMBEDDED_DATA["users"]
    products = EMBEDDED_DATA["products"]
    orders = EMBEDDED_DATA["orders"]
    
    # 统计用户部门分布
    dept_stats = {}
    for user in users:
        dept = user["department"]
        dept_stats[dept] = dept_stats.get(dept, 0) + 1
    
    # 统计产品类别分布
    category_stats = {}
    for product in products:
        category = product["category"]
        category_stats[category] = category_stats.get(category, 0) + 1
    
    # 计算订单总金额
    total_revenue = sum(order["total"] for order in orders)
    
    stats = {
        "user_count": len(users),
        "product_count": len(products),
        "order_count": len(orders),
        "total_revenue": total_revenue,
        "department_distribution": dept_stats,
        "category_distribution": category_stats
    }
    
    logger.info("Generated statistics summary")
    return {"success": True, "data": stats}

# Start the server
if __name__ == "__main__":
    mcp.run(transport="stdio")
