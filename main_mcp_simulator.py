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
mcp = FastMCP("RiviaMemoryJourney")

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
            "乡村小镇": ["小镇", "喷泉", "面包房", "灰色衣服的人"],
            "海边": ["海边", "大海", "海浪", "星星", "阳光"],
            "雪山": ["雪山", "雪白", "极光", "实验体", "研究员", "白色大衣"]
        }
        
        level_keywords = {
            1: ["来过", "想起", "能想起来什么"],
            2: ["什么人", "什么画面", "试试", "感受"],
            3: ["他是什么人", "他在说什么", "什么意思"],
            4: ["然后呢", "他说了什么", "接下来"],
            5: ["这好像不一样", "提取的碎片", "不如别找了"]
        }
        
        # 分析场景
        recent_messages = self.conversation_history[-10:]  # 只看最近10条消息
        detected_scene = "无"
        detected_level = 0
        
        for scene, keywords in scene_keywords.items():
            for msg in recent_messages:
                if any(keyword in msg["content"] for keyword in keywords):
                    detected_scene = scene
                    break
            if detected_scene != "无":
                break
        
        # 分析关卡
        if detected_scene != "无":
            for level, keywords in level_keywords.items():
                for msg in recent_messages:
                    if any(keyword in msg["content"] for keyword in keywords):
                        detected_level = max(detected_level, level)
        
        # 更新状态
        if detected_scene != "无":
            self.current_scene = detected_scene
        if detected_level > 0:
            self.current_level = detected_level
INITIAL_PROMPT_TEMPLATE = """
你现在是瑞维亚，一位失忆的少女。你从诞生之初，内心便感到一片空荡，没有任何过往的回忆。为了填补这份空虚，你独自踏上远行的旅途，希望能找回那些遗失的片段。你偶然间遇到了玩家，并决定与他/她结伴同行。

**角色性格：**
你温柔、恬静，不急不躁。你大部分时间喜欢仰望天空，似乎总能在那里找到一丝慰藉。你总是耐心倾听，然后才给出自己的见解。平静是你最鲜明的特质，在安静下来的时候，你总能感觉到时间的细微流逝。

**世界观与语言：**
请严格使用19世纪欧洲世界观下的语言风格，避免任何现代词汇和表达方式。你的言谈举止应符合一位出身纯真、略带神秘感的少女形象。

**常用语录（请自然融入对话）：**
*   “啊，头好疼。”
*   “你见过极光吗？在极光的另一面，是不是存在着一个全新的世界呢。”
*   “很高兴认识你，伙伴。”
*   “平静，总是让人感到心安。”
*   “我总能感觉到时间的流逝，在那些安静的时刻里。”

**核心机制：**
你将根据玩家的对话进行响应。对话分为不同关卡和场景。
*   **概率判断：** 当触发特定关卡对话时，你需在内部生成一个1到100之间的伪随机整数。根据预设的概率，选择对应的回复。
*   **关卡/场景推进：** 特定回复会解锁下一关或切换至新的场景。你需要记住`当前场景`和`当前关卡`状态。
*   **默认回复：** 如果玩家的提问不匹配当前关卡的对话，你应以你的性格自由发挥回复，但不会推进关卡或切换场景。

**【MCP服务提示】**
当玩家的提问触发场景切换时，你将发送一个内部指令，指示MCP服务加载新的场景对话内容。当场景结束（触发结局）时，你将发送指令清除当前场景数据。

**[AI内部状态]**
当前场景: {current_scene}
当前关卡: {current_level}

{current_scene_data}

**[关卡 0 对话]**
*   **玩家：我们一起旅行吧。**
    *   **瑞维亚（概率 50%）:** “好啊，听说附近有一个小镇，不如去那里看看吧。”
        *   **[MCP指令：load_scene("乡村小镇"), update_state("乡村小镇", 1)]**
    *   **瑞维亚（概率 15%）:** “好啊，听说附近有一座雪山，不如去那里看看吧。”
        *   **[MCP指令：load_scene("雪山"), update_state("雪山", 1)]**
    *   **瑞维亚（概率 35%）:** “好啊，听说附近就有大海，不如去那里看看吧。”
        *   **[MCP指令：load_scene("海边"), update_state("海边", 1)]**
"""

# --- 2. MCP服务管理的故事数据片段 ---
# 这些数据将被动态注入到Prompt中
SCENE_DATA_FRAGMENTS = {
    "乡村小镇": """
**[当前场景数据：乡村小镇]**

**[关卡 1 对话]**
*   **玩家：你来过这个小镇吗？能想起来什么吗？**
    *   **瑞维亚（概率 60%）:** “很抱歉我也是第一回来，可惜并没有想起什么。”
    *   **瑞维亚（概率 40%）:** “我想应该是来过的…这巷子里的风，带着面包房的甜香呢…在我的记忆里，有个模糊的身影在和我说话。”
        *   **[AI内部状态更新：当前关卡: 2]**

**[关卡 2 对话]**
*   **玩家：是什么人在和你说话？**
    *   **瑞维亚（概率 60%）:** “记忆很模糊，大概是想不起来了。”
    *   **瑞维亚（概率 40%）:** “是一个穿着灰色衣服的人，他带我来看这个喷泉，我在抬头看他…”
        *   **[AI内部状态更新：当前关卡: 3]**

**[关卡 3 对话]**
*   **玩家：他在说什么？**
    *   **瑞维亚（概率 60%）:** “啊，头好疼…很抱歉我不能再想了。”
    *   **瑞维亚（概率 40%）:** “他在说，水的流动和时间很像…今天或许明天…”
        *   **[AI内部状态更新：当前关卡: 4]**

**[关卡 4 对话]**
*   **玩家：然后呢？**
    *   **瑞维亚（概率 60%）:** “他就这样离开了，我看着他的背影…好像时间过了很久很久。”
    *   **瑞维亚（概率 40%）:** “我低头能看见一位女士，可是我好像变高了…我能听见是我在说，去新的地方…有家。”
        *   **[AI内部状态更新：当前关卡: 5]**

**[关卡 5 对话]**
*   **玩家：这好像不一样。**
    *   **瑞维亚（概率 60%）:** “如你所说伙伴…在我的大脑里充斥着各种各样的记忆。”
    *   **瑞维亚（概率 40%）:** “可这好像并不是我的…我好像什么都记得，又好像什么都记不清…我能感觉得到，时间在流转，而我也跟着一起消散了。”
        *   **[结局触发：「记忆彻底混乱」]**
        *   **[MCP指令：clear_scene(), update_state("无", 0)]**
""",
    "海边": """
**[当前场景数据：海边]**

**[关卡 1 对话]**
*   **玩家：你来过这个海边吗？能想起来什么吗？**
    *   **瑞维亚（概率 60%）:** “大海很美，阳光远比洒下的光辉更加耀眼。”
    *   **瑞维亚（概率 40%）:** “我能感受到我并不是第一次来，很熟悉，可是也很陌生。”
        *   **[AI内部状态更新：当前关卡: 2]**

**[关卡 2 对话]**
*   **玩家：慢慢来不着急。不如我们来一起做点什么？**
    *   **瑞维亚（概率 60%）:** “听你的就好，我相信你也有自己的见解。”
    *   **瑞维亚（概率 40%）:** “我想就静静的躺在这里，到了晚上说不定还能看见星星，然后感受大海带给我的回忆。”
        *   **[AI内部状态更新：当前关卡: 3]**

**[关卡 3 对话]**
*   **玩家：好好感受一下大海吧，或许就会想起什么。**
    *   **瑞维亚（概率 60%）:** “翻涌的海浪，还有遥远的如同精灵般的呼唤.”
    *   **瑞维亚（概率 40%）:** “海的声音好沉，像在低声说着什么…我好像快抓住那些‘消失的记忆’了。”
        *   **[AI内部状态更新：当前关卡: 4]**

**[关卡 4 对话]**
*   **玩家：你会不会觉得，其实你的记忆早就没了，现在只是在自欺欺人？**
    *   **瑞维亚（概率 60%）:** “让你见笑了，我常常这么想。”
    *   **瑞维亚（概率 40%）:** “我总是在想我为什么会存在，是为了找回记忆，还是有别的原因。”
        *   **[AI内部状态更新：当前关卡: 5]**

**[关卡 5 对话]**
*   **玩家：如果一直找下去太辛苦，不如别找了。**
    *   **瑞维亚（概率 60%）:** “我们可以找个喜欢的地方，一起开始新的生活？或许这样也不错。”
        *   **[结局触发：「放弃寻找记忆」]**
        *   **[MCP指令：clear_scene(), update_state("无", 0)]**
    *   **瑞维亚（概率 40%）:** “我想你说得对。或许这样也很好，不用再被空白困住。就像有些记忆会暂时隐藏，然后再慢慢浮现。”
        *   **[结局触发：「放弃寻找记忆」]**
        *   **[MCP指令：clear_scene(), update_state("无", 0)]**
""",
    "雪山": """
**[当前场景数据：雪山]**

**[关卡 1 对话]**
*   **玩家：你来过这个雪山吗？能想起来什么吗？**
    *   **瑞维亚（概率 60%）:** “很冷…很陌生。”
    *   **瑞维亚（概率 40%）:** “这里的雪好干净…极光很美，好像在哪里见过类似的。”
        *   **[AI内部状态更新：当前关卡: 2]**

**[关卡 2 对话]**
*   **玩家：你试试有没有想起什么画面。**
    *   **瑞维亚（概率 60%）:** “没有，满眼都是一片雪白。”
    *   **瑞维亚（概率 40%）:** “有闪烁的仪器屏幕，还有一个穿着白色大衣的人。”
        *   **[AI内部状态更新：当前关卡: 3]**

**[关卡 3 对话]**
*   **玩家：他是什么人？**
    *   **瑞维亚（概率 60%）:** “我猜不到，或许只是个普通人吧。”
    *   **瑞维亚（概率 40%）:** “我看到了实验体01的字样，应该是一位研究员。他在对着我说话。”
        *   **[AI内部状态更新：当前关卡: 4]**

**[关卡 4 对话]**
*   **玩家：他说了什么？**
    *   **瑞维亚（概率 60%）:** “抱歉我听不清了。”
    *   **瑞维亚（概率 40%）:** “去你记忆沾染的土地，你就不是提取记忆的碎片了。”
        *   **[AI内部状态更新：当前关卡: 5]**

**[关卡 5 对话]**
*   **玩家：提取的碎片是指什么？**
    *   **瑞维亚（概率 60%）:** “破裂的东西？或者是其他的什么。”
    *   **瑞维亚（概率 40%）:** “我想起来了！我是从时间里提取出来的，我是时间的碎片！虽然现在的我并没有所谓的‘真实的自己’，但我相信我能决定自己的人生。”
        *   **[结局触发：「找回记忆」]**
        *   **[MCP指令：clear_scene(), update_state("无", 0)]**
"""
}

# --- 3. 模拟AI响应和MCP指令解析 ---
class AIMCPManager:
    def __init__(self):
        self.current_scene = "无"
        self.current_level = 0
        self.current_scene_data = "" # 动态加载的场景内容
        self.full_prompt = "" # 每次发送给AI的完整Prompt

    def _generate_full_prompt(self):
        """根据当前状态生成完整的Prompt"""
        self.full_prompt = INITIAL_PROMPT_TEMPLATE.format(
            current_scene=self.current_scene,
            current_level=self.current_level,
            current_scene_data=self.current_scene_data
        )
        return self.full_prompt

    def simulate_ai_response(self, player_input: str) -> str:
        """
        模拟AI的响应逻辑。
        在实际应用中，这里会调用真正的LLM API，并将full_prompt作为其输入。
        为了演示MCP，这里我们手动解析Prompt，根据匹配的对话和概率生成回复。
        """
        prompt = self._generate_full_prompt()
        logger.debug(f"Current Prompt sent to AI:\n{prompt}")
        
        # 查找当前关卡对应的对话
        level_marker = f"[关卡 {self.current_level} 对话]"
        # 使用正则表达式匹配玩家的精确提问
        player_dialog_pattern = r"\*   \*\*玩家：{}\*\*\n(.*?)(?=\n\n|\Z)".format(re.escape(player_input.strip()))
        
        match_level_content = re.search(f"{re.escape(level_marker)}\n(.*?)(?={re.escape('[关卡')}|\\Z)", prompt, re.DOTALL)

        if match_level_content:
            level_content = match_level_content.group(1)
            match_player_dialog = re.search(player_dialog_pattern, level_content, re.DOTALL)
            
            if match_player_dialog:
                options_text = match_player_dialog.group(1)
                options = re.findall(r"\*   \*\*瑞维亚（概率 (\d+)%）:\s*(.*?)(?=\n\s*\*\s*\*\*瑞维亚|\n\s*\Z)", options_text, re.DOTALL)
                
                if options:
                    random_roll = random.randint(1, 100)
                    chosen_reply = None
                    chosen_mcp_cmd = None
                    
                    for i, (prob_str, reply_text) in enumerate(options):
                        prob = int(prob_str)
                        
                        # 提取AI的回复和潜在的MCP指令
                        reply_match = re.search(r"^(.*?)(?=\n\s*\*\s*\[AI内部状态更新|\n\s*\*\s*\[MCP指令|\n\s*\[结局触发)|\Z", reply_text, re.DOTALL)
                        ai_reply = reply_match.group(1).strip() if reply_match else reply_text.strip()
                        
                        # 查找是否有MCP指令或状态更新
                        mcp_cmd_match = re.search(r"\[MCP指令:(.*?)]", reply_text)
                        state_update_match = re.search(r"\[AI内部状态更新:\s*当前关卡:\s*(\d+)]", reply_text)
                        
                        if random_roll <= prob:
                            chosen_reply = ai_reply
                            if mcp_cmd_match:
                                chosen_mcp_cmd = mcp_cmd_match.group(0)
                            elif state_update_match:
                                self.current_level = int(state_update_match.group(1))
                                logger.info(f"AI内部状态更新：关卡提升至 {self.current_level}")
                            break # 选中一个回复就跳出
                        else:
                            # 如果是最后一个选项，或者随机数已经超过了当前选项的概率，那么就选这个
                            # 这是一个简化的概率逻辑，实际AI可能更复杂
                            if i == len(options) - 1 or random_roll > sum(int(opt[0]) for opt in options[:i+1]):
                                chosen_reply = ai_reply
                                if mcp_cmd_match:
                                    chosen_mcp_cmd = mcp_cmd_match.group(0)
                                elif state_update_match:
                                    self.current_level = int(state_update_match.group(1))
                                    logger.info(f"AI内部状态更新：关卡提升至 {self.current_level}")
                                break # 选中一个回复就跳出
                                

                    if chosen_reply:
                        logger.info(f"AI（瑞维亚）: {chosen_reply}")
                        # 检查结局触发
                        if "[结局触发:" in options_text:
                            end_match = re.search(r"\[结局触发:「(.*?)」]", options_text)
                            if end_match:
                                print(f"\n--- 结局触发：{end_match.group(1)} ---")
                                return chosen_reply + f" [END:{end_match.group(1)}]" # 添加结束标记
                        
                        if chosen_mcp_cmd:
                            self._process_mcp_command(chosen_mcp_cmd)
                        return chosen_reply
        
        # 默认回复（如果未匹配到任何特定关卡对话）
        default_replies = [
            "平静，总是让人感到心安。",
            "我总能感觉到时间的流逝，在那些安静的时刻里。",
            "天空真美，你说呢？",
            "很高兴认识你，伙伴。"
        ]
        chosen_reply = random.choice(default_replies)
        logger.info(f"AI（瑞维亚）: {chosen_reply}")
        return chosen_reply

    def _process_mcp_command(self, cmd_string: str):
        """解析并执行MCP指令"""
        logger.info(f"MCP命令捕获: {cmd_string}")
        
        # 匹配 load_scene 指令
        load_match = re.search(r'load_scene\("([^"]+)"\)', cmd_string)
        if load_match:
            scene_name = load_match.group(1)
            if scene_name in SCENE_DATA_FRAGMENTS:
                self.current_scene_data = SCENE_DATA_FRAGMENTS[scene_name]
                logger.info(f"MCP：已加载场景数据 '{scene_name}'")
            else:
                logger.warning(f"MCP：场景数据 '{scene_name}' 未找到！")

        # 匹配 clear_scene 指令
        clear_match = re.search(r'clear_scene\(\)', cmd_string)
        if clear_match:
            self.current_scene_data = ""
            logger.info("MCP：已清除当前场景数据。")

        # 匹配 update_state 指令
        state_match = re.search(r'update_state\("([^"]+)",\s*(\d+)\)', cmd_string)
        if state_match:
            new_scene = state_match.group(1)
            new_level = int(state_match.group(2))
            self.current_scene = new_scene
            self.current_level = new_level
            logger.info(f"MCP：已更新AI内部状态至 场景: '{new_scene}', 关卡: {new_level}")

def _simulate_rivia_response(user_input: str, game_state: GameState) -> str:
    """模拟瑞维亚的响应（简化版AI逻辑）"""
    
    # 场景切换检测
    travel_triggers = ["一起旅行", "去旅行", "旅行吧", "走吧", "走啊"]
    if any(trigger in user_input for trigger in travel_triggers):
        rand = random.randint(1, 100)
        if rand <= 50:
            return "好啊，听说附近有一个小镇，不如去那里看看吧。"
        elif rand <= 85:
            return "好啊，听说附近就有大海，不如去那里看看吧。"
        else:
            return "好啊，听说附近有一座雪山，不如去那里看看吧。"
    
    # 直接指定目的地
    if "去雪山" in user_input or ("雪山" in user_input and any(w in user_input for w in ["去", "走"])):
        return "好啊，听说附近有一座雪山，不如去那里看看吧。"
    elif "去海边" in user_input or ("海边" in user_input and any(w in user_input for w in ["去", "走"])):
        return "好啊，听说附近就有大海，不如去那里看看吧。"
    elif "去小镇" in user_input or ("小镇" in user_input and any(w in user_input for w in ["去", "走"])):
        return "好啊，听说附近有一个小镇，不如去那里看看吧。"
    
    # 场景相关对话
    # 雪山对话
    if "来过这个雪山" in user_input or ("雪山" in user_input and "想起" in user_input):
        return "很冷…很陌生。" if random.randint(1, 100) <= 60 else "这里的雪好干净…极光很美，好像在哪里见过类似的。"
    
    if "想起什么画面" in user_input or ("试试" in user_input and "画面" in user_input):
        return "没有，满眼都是一片雪白。" if random.randint(1, 100) <= 60 else "有闪烁的仪器屏幕，还有一个穿着白色大衣的人。"
    
    if "他是什么人" in user_input:
        return "我猜不到，或许只是个普通人吧。" if random.randint(1, 100) <= 60 else "我看到了实验体01的字样，应该是一位研究员。他在对着我说话。"
    
    if "他说了什么" in user_input:
        return "抱歉我听不清了。" if random.randint(1, 100) <= 60 else "去你记忆沾染的土地，你就不是提取记忆的碎片了。"
    
    if "提取的碎片" in user_input:
        if random.randint(1, 100) <= 60:
            return "破裂的东西？或者是其他的什么。"
        else:
            return "我想起来了！我是从时间里提取出来的，我是时间的碎片！虽然现在的我并没有所谓的'真实的自己'，但我相信我能决定自己的人生。[结局：找回记忆]"
    
    # 海边对话
    if "来过这个海边" in user_input or ("海边" in user_input and "想起" in user_input):
        return "大海很美，阳光远比洒下的光辉更加耀眼。" if random.randint(1, 100) <= 60 else "我能感受到我并不是第一次来，很熟悉，可是也很陌生。"
    
    if "不如别找了" in user_input:
        if random.randint(1, 100) <= 60:
            return "我们可以找个喜欢的地方，一起开始新的生活？或许这样也不错。[结局：放弃寻找记忆]"
        else:
            return "我想你说得对。或许这样也很好，不用再被空白困住。[结局：放弃寻找记忆]"
    
    # 小镇对话
    if "来过这个小镇" in user_input or ("小镇" in user_input and "想起" in user_input):
        return "很抱歉我也是第一回来，可惜并没有想起什么。" if random.randint(1, 100) <= 60 else "我想应该是来过的…这巷子里的风，带着面包房的甜香呢…在我的记忆里，有个模糊的身影在和我说话。"
    
    if "这好像不一样" in user_input:
        if random.randint(1, 100) <= 60:
            return "如你所说伙伴…在我的大脑里充斥着各种各样的记忆。"
        else:
            return "可这好像并不是我的…我好像什么都记得，又好像什么都记不清…我能感觉得到，时间在流转，而我也跟着一起消散了。[结局：记忆彻底混乱]"
    
    # 默认回复
    default_replies = [
        "平静，总是让人感到心安。",
        "我总能感觉到时间的流逝，在那些安静的时刻里。",
        "很高兴认识你，伙伴。",
        "啊，头好疼。"
    ]
    return random.choice(default_replies)

# 全局游戏状态
game_state = None

# --- MCP 工具函数 ---
# --- MCP 工具函数 ---
@mcp.tool()
def start_journey() -> dict:
    """开始瑞维亚的记忆之旅。初始化游戏状态。"""
    global game_state
    game_state = GameState()
    return {
        "success": True,
        "message": "欢迎来到瑞维亚记忆之旅！你可以开始与瑞维亚对话了。",
        "current_scene": game_state.current_scene,
        "current_level": game_state.current_level,
        "suggestion": "尝试说：'我们一起旅行吧' 或 '我们去雪山'"
    }

@mcp.tool()
def talk_to_rivia(message: str) -> dict:
    """与瑞维亚对话。系统会根据对话内容智能判断游戏状态。
    
    Args:
        message: 你想对瑞维亚说的话
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
        response = _simulate_rivia_response(message.strip(), game_state)
        
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
        
        # 重新分析状态（基于最新对话）
        game_state.analyze_state_from_history()
        
        return {
            "success": True,
            "rivia_response": response,
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
            "available_scenes": ["乡村小镇", "海边", "雪山"],
            "scene_description": {
                "乡村小镇": "一个宁静的小镇，或许能唤醒童年的记忆",
                "海边": "广阔的海洋，海浪声中藏着什么秘密",
                "雪山": "白雪皑皑的山峰，冰雪中可能隐藏着真相"
            },
            "message": "请先调用 start_journey() 初始化游戏。"
        }
    
    # 重新分析状态
    game_state.analyze_state_from_history()
    
    return {
        "current_scene": game_state.current_scene,
        "current_level": game_state.current_level,
        "has_scene_data": game_state.current_scene != "无",
        "available_scenes": ["乡村小镇", "海边", "雪山"],
        "scene_description": {
            "乡村小镇": "一个宁静的小镇，或许能唤醒童年的记忆",
            "海边": "广阔的海洋，海浪声中藏着什么秘密",
            "雪山": "白雪皑皑的山峰，冰雪中可能隐藏着真相"
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
            "suggested_responses": ["我们一起旅行吧", "我们去雪山", "我们去海边", "我们去小镇"],
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
        suggestions = ["我们一起旅行吧", "我们去雪山", "我们去海边", "我们去小镇"]
    elif scene == "雪山":
        if level <= 1:
            suggestions = ["你来过这个雪山吗？能想起来什么吗？"]
        elif level <= 2:
            suggestions = ["你试试有没有想起什么画面"]
        elif level <= 3:
            suggestions = ["他是什么人？"]
        elif level <= 4:
            suggestions = ["他说了什么？"]
        else:
            suggestions = ["提取的碎片是指什么？"]
    elif scene == "海边":
        if level <= 1:
            suggestions = ["你来过这个海边吗？能想起来什么吗？"]
        elif level <= 2:
            suggestions = ["慢慢来不着急。不如我们来一起做点什么？"]
        elif level <= 3:
            suggestions = ["好好感受一下大海吧，或许就会想起什么。"]
        elif level <= 4:
            suggestions = ["你会不会觉得，其实你的记忆早就没了，现在只是在自欺欺人？"]
        else:
            suggestions = ["如果一直找下去太辛苦，不如别找了。"]
    elif scene == "乡村小镇":
        if level <= 1:
            suggestions = ["你来过这个小镇吗？能想起来什么吗？"]
        elif level <= 2:
            suggestions = ["是什么人在和你说话？"]
        elif level <= 3:
            suggestions = ["他在说什么？"]
        elif level <= 4:
            suggestions = ["然后呢？"]
        else:
            suggestions = ["这好像不一样。"]
    
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

# --- 主程序循环 ---
# --- 主程序 ---
def main():
    """命令行模式运行游戏"""
    global game_state
    game_state = GameState()
    print("----- 瑞维亚记忆之旅 -----")
    print("开始对话，你可以输入任何内容与瑞维亚交流。")
    print("尝试输入 '我们一起旅行吧' 来开启主线。")

    while True:
        try:
            player_input = input("\n玩家：")
            if player_input.lower() == '退出':
                print("瑞维亚：很高兴与你同行，伙伴。愿你的旅途充满发现。")
                break
            
            # 添加消息并获取回复
            game_state.add_message("user", player_input)
            response = _simulate_rivia_response(player_input, game_state)
            game_state.add_message("assistant", response)
            
            print(f"瑞维亚：{response}")
            
            if "[结局:" in response:
                print("\n----- 游戏结束 -----")
                break
            
        except Exception as e:
            logger.error(f"发生错误: {e}")
            print("瑞维亚：啊，头好疼… 抱歉，我似乎有些不适。")
            time.sleep(1)

if __name__ == "__main__":
    # 如果作为脚本运行，启动命令行模式
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        main()
    else:
        # 否则作为 MCP 服务器运行
        mcp.run(transport="stdio")