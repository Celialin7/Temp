import time
import random
import pyautogui
import logging

# 设置 logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# pyautogui 设置：关闭默认暂停，提高速度
pyautogui.PAUSE = 0
pyautogui.MINIMUM_DURATION = 0
pyautogui.MINIMUM_SLEEP = 0

# 可用的 tweening 函数（使移动有自然加减速）
TWEENS = [
    pyautogui.easeInQuad,    # 慢起步，快结束
    pyautogui.easeOutQuad,   # 快起步，慢结束
    pyautogui.easeInOutQuad, # 两端慢，中间快（最像人类）
    pyautogui.easeInElastic, # 弹性效果
    pyautogui.easeOutBounce # 轻微反弹
]

def human_delay(min_sec=3, max_sec=15):
    """人类-like 动作间隔延迟，使用高斯分布避免模式"""
    mean = (min_sec + max_sec) / 2
    sigma = (max_sec - min_sec) / 4
    delay = random.gauss(mean, sigma)
    delay = max(min_sec, min(max_sec, delay))  # 限制范围
    logging.info(f"等待 {delay:.2f} 秒")
    time.sleep(delay)

def human_move_to(x, y, variance=10):
    """自然移动鼠标到目标，带随机偏差和 tween"""
    # 轻微目标偏移（人类不总精确点击同一像素）
    x += random.randint(-variance, variance)
    y += random.randint(-variance, variance)
    
    duration = random.uniform(0.5, 2.0)  # 移动时间随机
    tween = random.choice(TWEENS)       # 随机缓动
    
    current_x, current_y = pyautogui.position()
    logging.info(f"移动鼠标从 ({current_x}, {current_y}) 到 ({x}, {y})")
    pyautogui.moveTo(x, y, duration=duration, tween=tween)

def human_click(x=None, y=None):
    """人类-like 点击，可指定位置或当前"""
    if x is not None and y is not None:
        human_move_to(x, y)
    
    click_delay = random.uniform(0.05, 0.2)  # 按下-释放间小延迟
    logging.info("点击鼠标")
    pyautogui.mouseDown()
    time.sleep(click_delay)
    pyautogui.mouseUp()

def human_type(text, error_rate=0.05):
    """人类-like 打字，带随机键间延迟，偶尔打错并纠正"""
    logging.info(f"输入文本: {text}")
    for char in text:
        if random.random() < error_rate:  # 偶尔打错
            wrong = random.choice('abcdefghijklmnopqrstuvwxyz')
            pyautogui.typewrite(wrong)
            time.sleep(random.uniform(0.1, 0.4))
            pyautogui.press('backspace')  # 纠正
            time.sleep(random.uniform(0.1, 0.3))
        
        pyautogui.typewrite(char)
        time.sleep(random.uniform(0.05, 0.25))  # 键间随机延迟

# 示例使用：无限循环模拟随机行为
if __name__ == "__main__":
    logging.info("启动人类行为模拟")
    time.sleep(5)  # 给你时间切换窗口
    
    while True:
        # 随机选择动作
        action = random.choice(['click', 'type', 'move'])
        
        if action == 'click':
            # 示例：点击屏幕中心附近
            width, height = pyautogui.size()
            human_click(width // 2, height // 2)
        
        elif action == 'type':
            human_type("这是一个测试句子 ")
        
        elif action == 'move':
            width, height = pyautogui.size()
            human_move_to(random.randint(100, width-100), random.randint(100, height-100))
        
        human_delay(4, 20)  # 下次动作前随机长等待





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
