import random
import re
import time
import json
import logging
import sys
from mcp.server.fastmcp import FastMCP
from typing import Optional

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 创建 MCP 服务器实例
mcp = FastMCP("KalakJourney")

# --- 游戏状态管理类 ---
class GameState:
    def __init__(self):
        self.conversation_history = []  # 存储对话历史
        self.current_scene = "无"
        self.current_level = 0
        self.game_ended = False
        self.ending_type: Optional[str] = None

    def add_message(self, role: str, content: str):
        """添加对话消息"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": time.time()
        })

    def analyze_state_from_history(self):
        """从对话历史中分析当前状态"""
        scene_keywords = {
            "地狱引擎": ["引擎", "地狱", "机械", "恶魔", "阿弗纳斯", "去引擎"],
            "记忆碎片": ["记忆", "过去", "碎片", "回忆", "蒂夫林", "去记忆"],
            "血战前线": ["血战", "前线", "战争", "恶魔", "魔鬼", "去前线"]
        }
        
        level_keywords = {
            1: ["来过", "想起", "记得什么", "熟悉"],
            2: ["什么人", "谁在", "听到", "感受", "看到"],
            3: ["他是什么人", "她在说什么", "什么意思", "为什么"],
            4: ["然后呢", "接下来", "后来", "发生了什么"],
            5: ["真相", "意义", "目的", "结束了吗"]
        }
        
        # 分析场景
        all_messages = self.conversation_history
        detected_scene = self.current_scene
        detected_level = self.current_level
        
        # 场景检测
        for msg in reversed(all_messages[-15:]):
            for scene, keywords in scene_keywords.items():
                if any(keyword in msg["content"] for keyword in keywords):
                    detected_scene = scene
                    break
            if detected_scene != "无":
                break
        
        # 关卡检测
        if detected_scene != "无":
            for level, keywords in level_keywords.items():
                for msg in reversed(all_messages[-10:]):
                    if any(keyword in msg["content"] for keyword in keywords):
                        detected_level = max(detected_level, level)
        
        # 更新状态
        if detected_scene != "无":
            self.current_scene = detected_scene
        if detected_level > 0:
            self.current_level = detected_level

def _simulate_kalak_response(user_input: str, game_state: GameState) -> str:
    """模拟卡菈克的响应逻辑 - 基于博德之门3剧情"""
    
    # 场景切换检测
    travel_triggers = ["一起去看看", "去探索", "出发", "走吧", "寻找真相"]
    if any(trigger in user_input for trigger in travel_triggers):
        rand = random.randint(1, 100)
        if rand <= 40:
            return "那边...我感受到了地狱引擎的脉动。它在召唤我，就像...就像它是我身体的一部分。"
        elif rand <= 70:
            return "我的脑海中闪过一些画面...阿弗纳斯的战场，血与火的记忆。也许那里有答案。"
        else:
            return "扎列尔...这个名字让我愤怒。我必须去血战前线，去面对我的过去。"
    
    # 直接指定目的地
    if "去地狱引擎" in user_input or ("引擎" in user_input and any(w in user_input for w in ["去", "走"])):
        return "那边...我感受到了地狱引擎的脉动。它在召唤我，就像...就像它是我身体的一部分。"
    elif "去看记忆" in user_input or ("记忆" in user_input and any(w in user_input for w in ["去", "走"])):
        return "我的脑海中闪过一些画面...阿弗纳斯的战场，血与火的记忆。也许那里有答案。"
    elif "去血战前线" in user_input or ("前线" in user_input and any(w in user_input for w in ["去", "走"])):
        return "扎列尔...这个名字让我愤怒。我必须去血战前线，去面对我的过去。"
    
    # 地狱引擎场景对话
    if "这个引擎" in user_input or ("引擎" in user_input and ("熟悉" in user_input or "感觉" in user_input)):
        return "这台机器...它的声音和我的心跳同步。" if random.randint(1, 100) <= 60 else "我明白了！这不只是一台引擎...我的心脏就是它的核心。扎列尔把我的心改造成了这台地狱机器的动力源。"
    
    if "你的心脏" in user_input or ("心脏" in user_input and "引擎" in user_input):
        return "不...这太疯狂了。我还是我，对吧？" if random.randint(1, 100) <= 60 else "是的，我的心脏被改造了。每一次跳动都在为这台战争机器提供动力。我既是卡菈克，也是地狱引擎的核心。"
    
    if "扎列尔做了什么" in user_input or "为什么这样做" in user_input:
        return "我记不清那段痛苦的回忆..." if random.randint(1, 100) <= 60 else "扎列尔需要一个永不停息的动力核心。我那时已经垂死，他利用了我对复仇的渴望，把我改造成了这个样子。[结局：地狱引擎的真相]"
    
    # 记忆碎片场景对话
    if "这些记忆" in user_input or ("记忆" in user_input and ("想起" in user_input or "回忆" in user_input)):
        return "模糊不清...像是透过血雾看到的画面。" if random.randint(1, 100) <= 60 else "我看到了...埃尔图雷尔的陷落，我的家人被恶魔杀死，还有我第一次来到阿弗纳斯的恐惧。"
    
    if "你的家人" in user_input or "埃尔图雷尔" in user_input:
        return "那是另一个人的生活...我不想谈论它。" if random.randint(1, 100) <= 60 else "我的父母，我的朋友...都死在恶魔的爪下。我为了复仇来到阿弗纳斯，但复仇的代价比我想象的更高。"
    
    if "复仇的代价" in user_input or "后悔吗" in user_input:
        return "后悔？我不知道...愤怒已经燃烧太久。" if random.randint(1, 100) <= 60 else "我用自己的人性换取了力量，但现在我明白...真正的力量来自于选择宽恕，而不是复仇。[结局：选择宽恕]"
    
    # 血战前线场景对话
    if "血战前线" in user_input or ("前线" in user_input and ("记得" in user_input or "战斗" in user_input)):
        return "无尽的杀戮...这里没有英雄，只有怪物。" if random.randint(1, 100) <= 60 else "我记起来了！我在这里杀死了无数恶魔，也杀死了许多魔鬼。但最让我痛苦的是...我也杀死了无辜的人。"
    
    if "无辜的人" in user_input or "后悔杀戮" in user_input:
        return "那时我已经失去理智...愤怒控制了一切。" if random.randint(1, 100) <= 60 else "在血战中，我逐渐失去了自己。为了变得更强，我做了很多可怕的事情。那些死在我手下的人...他们的眼神我永远忘不了。"
    
    if "赎罪" in user_input or "弥补" in user_input:
        return "我该如何赎罪？死者不会复活。" if random.randint(1, 100) <= 60 else "我无法挽回过去，但我可以选择不同的未来。我要用我剩下的生命保护无辜者，即使这意味着我永远无法获得真正的宽恕。[结局：赎罪之路]"
    
    # 安慰和关怀回复
    if any(phrase in user_input for phrase in ["你没事吧", "没关系", "我在这里", "别怕"]):
        responses = [
            "谢谢...在阿弗纳斯，善意比黄金更珍贵。",
            "有很长时间，我以为自己配不上任何人的关心。",
            "你的话让我想起了...还有值得守护的东西。"
        ]
        return random.choice(responses)
    
    # 关于扎列尔的愤怒
    if "扎列尔" in user_input:
        responses = [
            "一提到这个名字，我胸中的引擎就燃烧得更猛烈。",
            "他毁了我，但也给了我力量。我不知道该恨他还是感谢他。",
            "总有一天，我要让他为我遭受的一切付出代价。"
        ]
        return random.choice(responses)
    
    # 让智能体自由发挥
    return None

# 全局游戏状态
game_state = None

# --- MCP 工具函数 ---
@mcp.tool()
def start_journey() -> dict:
    """开始卡菈克在阿弗纳斯的记忆探寻之旅。初始化游戏状态。"""
    global game_state
    game_state = GameState()
    return {
        "success": True,
        "message": "欢迎来到卡菈克的阿弗纳斯记忆之旅！这位蒂夫林野蛮人发现自己心中燃烧着地狱引擎，对自己的过去一片空白。",
        "current_scene": game_state.current_scene,
        "current_level": game_state.current_level,
        "suggestion": "尝试说：'我们一起去看看吧' 或 '你感受到什么了？'"
    }

@mcp.tool()
def talk_to_kalak(message: str) -> dict:
    """与卡菈克对话。系统会根据对话内容智能判断游戏状态。
    
    Args:
        message: 你想对卡菈克说的话
    """
    global game_state
    if game_state is None:
        return {
            "success": False,
            "message": "请先调用 start_journey() 初始化游戏。"
        }
    
    if not message.strip():
        return {
            "success": False,
            "message": "请输入你想说的话。"
        }
    
    try:
        # 添加玩家消息到历史
        game_state.add_message("user", message.strip())
        
        # 模拟 AI 响应
        response = _simulate_kalak_response(message.strip(), game_state)
        
        # 如果没有匹配的回复，使用通用回复
        if response is None:
            avernian_responses = [
                "我心中的引擎在燃烧...但我不明白为什么。",
                "这些记忆碎片...就像阿弗纳斯的火焰一样混乱。",
                "扎列尔对我做了什么？为什么我会变成这样？",
                "愤怒...总是有愤怒在燃烧，但我不知道为什么。"
            ]
            response = random.choice(avernian_responses)
        
        # 添加 AI 回复到历史
        game_state.add_message("assistant", response)
        
        # 检查结局
        is_ended = "[结局:" in response
        ending = None
        if is_ended:
            ending_match = re.search(r"\[结局：(.*?)\]", response)
            if ending_match:
                ending = ending_match.group(1)
                response = response.replace(f"[结局：{ending}]", "").strip()
                game_state.game_ended = True
                game_state.ending_type = ending
        
        # 重新分析状态
        game_state.analyze_state_from_history()
        
        return {
            "success": True,
            "kalak_response": response,
            "current_scene": game_state.current_scene,
            "current_level": game_state.current_level,
            "is_ended": is_ended,
            "ending": ending
        }
    except Exception as e:
        logger.error(f"对话处理错误: {e}")
        return {
            "success": False,
            "message": f"对话处理出现错误: {str(e)}"
        }

@mcp.tool()
def get_game_state() -> dict:
    """获取当前游戏状态信息。"""
    global game_state
    if game_state is None:
        return {
            "current_scene": "未初始化",
            "current_level": 0,
            "has_scene_data": False,
            "available_scenes": ["地狱引擎", "记忆碎片", "血战前线"],
            "scene_description": {
                "地狱引擎": "燃烧的机械恶魔，阿弗纳斯战争的核心动力",
                "记忆碎片": "破碎的过往回忆，蒂夫林身份的痕迹",
                "血战前线": "永恒战争的前线，恶魔与魔鬼的战场"
            },
            "message": "请先调用 start_journey() 初始化游戏。"
        }
    
    # 重新分析状态
    game_state.analyze_state_from_history()
    
    return {
        "current_scene": game_state.current_scene,
        "current_level": game_state.current_level,
        "has_scene_data": game_state.current_scene != "无",
        "available_scenes": ["地狱引擎", "记忆碎片", "血战前线"],
        "scene_description": {
            "地狱引擎": "燃烧的机械恶魔，阿弗纳斯战争的核心动力",
            "记忆碎片": "破碎的过往回忆，蒂夫林身份的痕迹",
            "血战前线": "永恒战争的前线，恶魔与魔鬼的战场"
        },
        "conversation_count": len(game_state.conversation_history),
        "game_ended": game_state.game_ended
    }

@mcp.tool()
def get_story_progress() -> dict:
    """获取故事进度和建议的对话选项。"""
    global game_state
    if game_state is None:
        return {
            "current_scene": "未初始化",
            "current_level": 0,
            "suggested_responses": ["我们一起探索吧", "你想去哪里找答案？", "你记得什么吗？"],
            "story_status": "未开始",
            "message": "请先调用 start_journey() 初始化游戏。"
        }
    
    # 分析当前状态
    game_state.analyze_state_from_history()
    
    # 根据状态提供建议
    suggestions = []
    scene = game_state.current_scene
    level = game_state.current_level
    
    if scene == "无":
        suggestions = ["我们一起去看看吧", "你感受到什么了？", "去地狱引擎", "去看记忆碎片", "去血战前线"]
    elif scene == "地狱引擎":
        if level <= 1:
            suggestions = ["这个引擎看起来熟悉吗？"]
        elif level <= 2:
            suggestions = ["你是这引擎的一部分吗？"]
        elif level <= 3:
            suggestions = ["扎列尔对你做了什么？"]
        else:
            suggestions = ["为什么要这样做？"]
    elif scene == "记忆碎片":
        if level <= 1:
            suggestions = ["这些记忆是什么？"]
        elif level <= 2:
            suggestions = ["你是蒂夫林吗？"]
        else:
            suggestions = ["血战是如何改变你的？"]
    elif scene == "血战前线":
        if level <= 1:
            suggestions = ["你记得血战前线吗？"]
        elif level <= 2:
            suggestions = ["你杀了很多人吗？"]
        else:
            suggestions = ["你想要赎罪吗？"]
    
    return {
        "current_scene": scene,
        "current_level": level,
        "suggested_responses": suggestions,
        "story_status": "已结束" if game_state.game_ended else ("进行中" if scene != "无" else "未开始"),
        "ending_type": game_state.ending_type if game_state.game_ended else None
    }

@mcp.tool()
def reset_game() -> dict:
    """重置游戏到初始状态。"""
    global game_state
    game_state = GameState()
    return {
        "success": True,
        "message": "游戏已重置到初始状态。",
        "current_scene": game_state.current_scene,
        "current_level": game_state.current_level
    }

@mcp.tool()
def get_conversation_history() -> dict:
    """获取完整的对话历史记录。"""
    global game_state
    if game_state is None:
        return {
            "success": False,
            "message": "请先调用 start_journey() 初始化游戏。",
            "history": []
        }
    
    return {
        "success": True,
        "message": f"共有 {len(game_state.conversation_history)} 条对话记录",
        "history": game_state.conversation_history,
        "current_scene": game_state.current_scene,
        "current_level": game_state.current_level
    }

# --- 主程序 ---
def main():
    """命令行模式运行游戏"""
    global game_state
    game_state = GameState()
    print("----- 卡菈克·阿弗纳斯记忆之旅 -----")
    print("在阿弗纳斯的硫磺平原上，一位蒂夫林野蛮人缓缓苏醒...")
    print("她心中燃烧着地狱引擎，却对自己的过去一无所知。")
    print("你是第一个向她伸出援手的人，愿意帮助她寻找失落的记忆吗？")
    print("尝试输入 '我们一起去看看吧' 来开启旅程。")

    while True:
        try:
            player_input = input("\n你：")
            if player_input.lower() == '退出':
                print("卡菈克：在阿弗纳斯这地狱般的地方，遇见你是我唯一的幸运。谢谢你，陌生人。")
                break
            
            # 添加消息并获取回复
            game_state.add_message("user", player_input)
            response = _simulate_kalak_response(player_input, game_state)
            
            if response is None:
                response = random.choice([
                    "我心中的引擎在燃烧...但我不明白为什么。",
                    "这些记忆碎片...就像阿弗纳斯的火焰一样混乱。",
                    "扎列尔对我做了什么？为什么我会变成这样？",
                    "愤怒...总是有愤怒在燃烧，但我不知道为什么。"
                ])
            
            game_state.add_message("assistant", response)
            
            print(f"卡菈克：{response}")
            
            if "[结局:" in response:
                print("\n----- 记忆的真相 -----")
                break
            
        except Exception as e:
            logger.error(f"发生错误: {e}")
            print("卡菈克：该死...我的头又开始疼了。这些记忆就像在燃烧一样。")
            time.sleep(1)

if __name__ == "__main__":
    # 如果作为脚本运行，启动命令行模式
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        main()
    else:
        # 否则作为 MCP 服务器运行
        mcp.run(transport="stdio")