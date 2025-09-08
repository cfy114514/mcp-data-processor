#!/usr/bin/env python3
"""
测试数据查询服务器的功能
Test the data query server functionality
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from data_query_server import mcp, EMBEDDED_DATA

def test_query_functions():
    """测试所有查询函数"""
    print("=== 数据查询服务器功能测试 ===")
    print()
    
    # 测试查询所有用户
    print("1. 查询所有用户:")
    from data_query_server import query_users
    result = query_users()
    print(f"   找到 {result['count']} 个用户")
    for user in result['data'][:2]:  # 只显示前2个
        print(f"   - {user['name']} ({user['department']})")
    print()
    
    # 测试按部门过滤用户
    print("2. 查询技术部用户:")
    result = query_users("department", "技术部")
    print(f"   找到 {result['count']} 个技术部用户")
    for user in result['data']:
        print(f"   - {user['name']} ({user['city']})")
    print()
    
    # 测试查询所有产品
    print("3. 查询所有产品:")
    from data_query_server import query_products
    result = query_products()
    print(f"   找到 {result['count']} 个产品")
    for product in result['data'][:3]:  # 只显示前3个
        print(f"   - {product['name']}: ¥{product['price']} ({product['category']})")
    print()
    
    # 测试按类别过滤产品
    print("4. 查询电子产品:")
    result = query_products("category", "电子产品")
    print(f"   找到 {result['count']} 个电子产品")
    for product in result['data']:
        print(f"   - {product['name']}: ¥{product['price']}")
    print()
    
    # 测试用户订单查询
    print("5. 查询用户ID=1的订单:")
    from data_query_server import get_user_orders
    result = get_user_orders(1)
    if result['success']:
        user_data = result['data']
        print(f"   用户: {user_data['user']['name']}")
        print(f"   订单数量: {user_data['total_orders']}")
        for order in user_data['orders']:
            print(f"   - {order['product_name']}: ¥{order['total']} ({order['date']})")
    print()
    
    # 测试统计信息
    print("6. 获取数据统计:")
    from data_query_server import get_statistics
    result = get_statistics()
    if result['success']:
        stats = result['data']
        print(f"   用户总数: {stats['user_count']}")
        print(f"   产品总数: {stats['product_count']}")
        print(f"   订单总数: {stats['order_count']}")
        print(f"   总收入: ¥{stats['total_revenue']}")
        print(f"   部门分布: {stats['department_distribution']}")
        print(f"   产品类别分布: {stats['category_distribution']}")
    print()
    
    print("=== 所有测试完成 ===")

if __name__ == "__main__":
    test_query_functions()
