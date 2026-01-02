import time
import random
import pyautogui
import logging

# 设置 logging（可选，如果你不想看到日志，可以把 level 改成 logging.WARNING）
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# pyautogui 设置：关闭默认暂停，提高速度
pyautogui.PAUSE = 0
pyautogui.MINIMUM_DURATION = 0
pyautogui.MINIMUM_SLEEP = 0

# 可用的 tweening 函数（使鼠标移动有自然加减速）
TWEENS = [
    pyautogui.easeInQuad,
    pyautogui.easeOutQuad,
    pyautogui.easeInOutQuad,
    pyautogui.easeInElastic,
    pyautogui.easeOutBounce
]

def human_delay(min_sec=4, max_sec=20):
    """人类-like 动作间隔延迟，使用高斯分布避免固定模式"""
    mean = (min_sec + max_sec) / 2
    sigma = (max_sec - min_sec) / 4
    delay = random.gauss(mean, sigma)
    delay = max(min_sec, min(max_sec, delay))  # 限制在范围内
    logging.info(f"等待 {delay:.2f} 秒后进行下一次动作")
    time.sleep(delay)

def human_move_to(x, y, variance=15):
    """自然移动鼠标到目标位置，带随机偏差和缓动"""
    x += random.randint(-variance, variance)
    y += random.randint(-variance, variance)
    
    duration = random.uniform(0.4, 1.8)
    tween = random.choice(TWEENS)
    
    current_x, current_y = pyautogui.position()
    logging.info(f"移动鼠标从 ({current_x}, {current_y}) 到 ({x}, {y})")
    pyautogui.moveTo(x, y, duration=duration, tween=tween)

def human_click(x=None, y=None):
    """人类-like 点击"""
    if x is not None and y is not None:
        human_move_to(x, y)
    
    click_delay = random.uniform(0.05, 0.18)
    logging.info("执行点击")
    pyautogui.mouseDown()
    time.sleep(click_delay)
    pyautogui.mouseUp()

def human_type(text, error_rate=0.06):
    """人类-like 打字，使用 press() 避免 typewrite 的输入法卡死问题"""
    logging.info(f"输入文本: {text}")
    for char in text:
        # 偶尔模拟打错并纠正（更像人类）
        if random.random() < error_rate:
            wrong = random.choice('abcdefghijklmnopqrstuvwxyz ')
            pyautogui.press(wrong)
            time.sleep(random.uniform(0.15, 0.45))
            pyautogui.press('backspace')
            time.sleep(random.uniform(0.1, 0.35))
        
        # 【核心修改】：用 press() 替代 typewrite(char)
        if char == ' ':
            pyautogui.press('space')
        elif len(char) == 1:
            # 处理大小写（人类打字会自然按 shift）
            if char.isupper():
                pyautogui.keyDown('shift')
                pyautogui.press(char.lower())
                pyautogui.keyUp('shift')
            else:
                pyautogui.press(char)
        # 正常键间随机延迟（真正控制打字速度，像人类）
        time.sleep(random.uniform(0.05, 0.28))

# ==================== 主程序启动部分 ====================
if __name__ == "__main__":
    logging.info("人类行为模拟器启动！5秒后开始自动操作...")
    time.sleep(5)  # 给你5秒时间切换到目标窗口！！！

    logging.info("开始无限随机模拟人类行为（鼠标移动、点击、打字）")

    while True:  # 无限循环，持续模拟
        width, height = pyautogui.size()
        
        # 随机选择一种动作
        action = random.choice(['move_and_click', 'type_something', 'random_move'])
        
        if action == 'move_and_click':
            # 随机移动到屏幕某个位置并点击
            target_x = random.randint(100, width - 100)
            target_y = random.randint(100, height - 100)
            human_click(target_x, target_y)
        
        elif action == 'type_something':
            # 随机输入一些常见短句（你可以自行修改或增加）
            sentences = [
                "hello world ",
                "testing 123 ",
                "this is a test ",
                "good morning ",
                "how are you ",
                "ok let's go "
            ]
            human_type(random.choice(sentences))
        
        elif action == 'random_move':
            # 只随机移动鼠标，不点击
            target_x = random.randint(100, width - 100)
            target_y = random.randint(100, height - 100)
            human_move_to(target_x, target_y)
        
        # 每次动作完成后，随机等待一段时间再进行下一次
        human_delay(4, 20)





第二段：
import time
import random
import pyautogui
import logging
import numpy as np  # 新增：用于计算曲线点

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
pyautogui.PAUSE = 0

def human_delay(min_sec=3, max_sec=15):
    mean = (min_sec + max_sec) / 2
    sigma = (max_sec - min_sec) / 4
    delay = random.gauss(mean, sigma)
    delay = max(min_sec, min(max_sec, delay))
    logging.info(f"等待 {delay:.2f} 秒")
    time.sleep(delay)

def bezier_curve_move_to(target_x, target_y, deviation=100, points=30):
    """使用二次 Bezier 曲线模拟人类弯曲路径移动"""
    start_x, start_y = pyautogui.position()
    
    # 随机控制点（使路径弯曲）
    ctrl_x = (start_x + target_x) / 2 + random.randint(-deviation, deviation)
    ctrl_y = (start_y + target_y) / 2 + random.randint(-deviation, deviation)
    
    # 生成曲线点
    t = np.linspace(0, 1, points)
    path_x = (1-t)**2 * start_x + 2*(1-t)*t * ctrl_x + t**2 * target_x
    path_y = (1-t)**2 * start_y + 2*(1-t)*t * ctrl_y + t**2 * target_y
    
    # 添加轻微噪声
    path_x += np.random.randint(-5, 6, size=points)
    path_y += np.random.randint(-5, 6, size=points)
    
    logging.info(f"Bezier 曲线移动到 ({target_x}, {target_y})")
    for i in range(1, len(path_x)):
        duration = random.uniform(0.02, 0.08)  # 每步小移动
        pyautogui.moveTo(path_x[i], path_y[i], duration=duration)

def human_click(x=None, y=None):
    if x is not None and y is not None:
        bezier_curve_move_to(x, y)
    pyautogui.click()

def human_type(text, error_rate=0.08):
    # 同方案1
    logging.info(f"输入文本: {text}")
    for char in text:
        if random.random() < error_rate:
            wrong = random.choice('abcdefghijklmnopqrstuvwxyz')
            pyautogui.typewrite(wrong)
            time.sleep(random.uniform(0.2, 0.5))
            pyautogui.press('backspace')
            time.sleep(random.uniform(0.1, 0.4))
        pyautogui.typewrite(char)
        time.sleep(random.uniform(0.06, 0.3))

# 示例使用类似方案1，替换 human_move_to 为 bezier_curve_move_to
