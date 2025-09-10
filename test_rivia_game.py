#!/usr/bin/env python3
"""
测试瑞维亚记忆之旅MCP服务器的功能
Test the Rivia Memory Journey MCP server functionality
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

def test_game_functions():
    """测试所有游戏功能"""
    print("=== 瑞维亚记忆之旅MCP服务器功能测试 ===")
    print()
    
    # 导入游戏函数
    from main_mcp_simulator import start_journey, talk_to_rivia, get_game_state, get_story_progress, reset_game
    
    # 1. 测试开始游戏
    print("1. 开始游戏:")
    result = start_journey()
    print(f"   成功: {result['success']}")
    print(f"   消息: {result['message']}")
    print(f"   当前场景: {result['current_scene']}")
    print(f"   当前关卡: {result['current_level']}")
    print(f"   建议: {result['suggestion']}")
    print()
    
    # 2. 测试获取游戏状态
    print("2. 获取游戏状态:")
    result = get_game_state()
    print(f"   当前场景: {result['current_scene']}")
    print(f"   当前关卡: {result['current_level']}")
    print(f"   有场景数据: {result['has_scene_data']}")
    print(f"   可用场景: {result['available_scenes']}")
    print()
    
    # 3. 测试获取故事进度
    print("3. 获取故事进度:")
    result = get_story_progress()
    print(f"   当前场景: {result['current_scene']}")
    print(f"   当前关卡: {result['current_level']}")
    print(f"   故事状态: {result['story_status']}")
    print(f"   建议回复: {result['suggested_responses']}")
    print()
    
    # 4. 测试与瑞维亚对话
    print("4. 与瑞维亚对话 - 开始旅行:")
    result = talk_to_rivia("我们一起旅行吧")
    print(f"   成功: {result['success']}")
    print(f"   瑞维亚的回复: {result['rivia_response']}")
    print(f"   当前场景: {result['current_scene']}")
    print(f"   当前关卡: {result['current_level']}")
    print(f"   游戏结束: {result['is_ended']}")
    print()
    
    # 5. 再次获取游戏状态（场景可能已改变）
    print("5. 获取更新后的游戏状态:")
    result = get_game_state()
    print(f"   当前场景: {result['current_scene']}")
    print(f"   当前关卡: {result['current_level']}")
    print(f"   有场景数据: {result['has_scene_data']}")
    print()
    
    # 6. 测试场景相关对话
    if result['current_scene'] == "乡村小镇":
        print("6. 场景对话测试 - 乡村小镇:")
        result = talk_to_rivia("你来过这个小镇吗？能想起来什么吗？")
    elif result['current_scene'] == "海边":
        print("6. 场景对话测试 - 海边:")
        result = talk_to_rivia("你来过这个海边吗？能想起来什么吗？")
    elif result['current_scene'] == "雪山":
        print("6. 场景对话测试 - 雪山:")
        result = talk_to_rivia("你来过这个雪山吗？能想起来什么吗？")
    else:
        print("6. 默认对话测试:")
        result = talk_to_rivia("你好瑞维亚")
    
    print(f"   瑞维亚的回复: {result['rivia_response']}")
    print(f"   当前关卡: {result['current_level']}")
    print()
    
    # 7. 测试重置游戏
    print("7. 重置游戏:")
    result = reset_game()
    print(f"   成功: {result['success']}")
    print(f"   消息: {result['message']}")
    print(f"   当前场景: {result['current_scene']}")
    print(f"   当前关卡: {result['current_level']}")
    print()
    
    print("=== 所有测试完成 ===")

def test_error_cases():
    """测试错误情况"""
    print("\n=== 错误情况测试 ===")
    
    from main_mcp_simulator import talk_to_rivia, reset_game
    
    # 重置游戏确保初始状态
    reset_game()
    
    # 1. 测试空消息
    print("1. 测试空消息:")
    result = talk_to_rivia("")
    print(f"   成功: {result['success']}")
    print(f"   错误消息: {result['message']}")
    print()
    
    # 2. 测试空白消息
    print("2. 测试空白消息:")
    result = talk_to_rivia("   ")
    print(f"   成功: {result['success']}")
    print(f"   错误消息: {result['message']}")
    print()
    
    print("=== 错误情况测试完成 ===")

if __name__ == "__main__":
    test_game_functions()
    test_error_cases()