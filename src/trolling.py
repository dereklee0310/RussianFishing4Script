import _thread
import logging
import time

import numpy as np
import pyautogui
import pytesseract
from PIL import Image

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# 指定 tesseract 目录
pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'


class Trolling():
    """拖钓"""

    def trolling(self, point, stamina_sleep, eat_sleep) -> None:
        # 两点之间路线巡航（线程1）
        _thread.start_new_thread(self.cruise, (point[0], point[1], point[2], point[3]))
        # 检查体力，喝咖啡（线程2）
        _thread.start_new_thread(self.stamina, (stamina_sleep,))
        # 检查饱食度，喝热可可（线程3）
        _thread.start_new_thread(self.eat, (eat_sleep,))
        # 拖钓循环
        while True:
            # 检查1竿、2竿是否中鱼
            # 中鱼就收线，收完线提竿过秤
            # 没中鱼就把竿子放回去（按0）
            logger.info("一轮拖钓循环结束")
            time.sleep(60)

    # 获取实时位置
    def get_external_position(self):
        # 获取右下角位置截图
        screenshot = pyautogui.screenshot(region=[2380, 1330, 100, 30])
        # 保存截图为文件
        src_location = "D:/PycharmProjects/RussianFishing4Script/screenshots/location.png"
        screenshot.save(src_location)
        try:
            img = Image.open(src_location)
            text = pytesseract.image_to_string(img)
            index = text.find(":")
            x = int(text[0:index])
            y = int(text[index + 1:])
            return np.array([x, y])
        except Exception:
            logger.error("当前位置识别错误")
        return np.array([-1, -1])

    # 是否能获取到当前位置
    def is_know_position(self, position):
        return not (np.array([-1, -1]) == position).all()

    def get_fish_num(self):
        # 获取鱼护位置截图
        screenshot = pyautogui.screenshot(region=[2480, 1167, 50, 25])
        # 保存截图为文件
        src_location = "D:/PycharmProjects/RussianFishing4Script/screenshots/fish_num.png"
        screenshot.save(src_location)
        try:
            img = Image.open(src_location)
            text = pytesseract.image_to_string(img)
            index = text.find("/")
            x = int(text[0:index])
            return x
        except Exception:
            logger.error("鱼护数量识别错误")
        return -1

    def cross_product_2d(self, v1, v2):
        return v1[0] * v2[1] - v1[1] * v2[0]

    # 2点之间巡航
    def cruise(self, x1, y1, x2, y2):
        # 上一个位置
        last_a = np.array([-1, -1])
        # 当前位置
        a = np.array([-1, -1])
        # 点b和c的固定位置
        b = np.array([x1, y1])
        c = np.array([x2, y2])
        # 目标位置
        target_position = b
        while True:
            # 调整位置更新频率
            time.sleep(15)
            a1 = self.get_external_position()
            if not self.is_know_position(a1):
                continue
            if (a1 == last_a).all():
                continue
            else:
                last_a = a
                a = a1
            if not self.is_know_position(last_a):
                continue
            # 判断和目标点距离以决定要不要切换目标点
            d = np.linalg.norm(a - target_position)
            # 切换目标位置
            if d < 10:
                if (target_position == b).all():
                    target_position = c
                else:
                    target_position = b
            # 求向量 last_a->a 和 a->target_position 的夹角角度
            v1 = a - last_a
            v2 = target_position - a
            dot_product = np.dot(v1, v2)
            norm_v1 = np.linalg.norm(v1)
            norm_v2 = np.linalg.norm(v2)
            cos_angle = dot_product / (norm_v1 * norm_v2)
            angle = np.arccos(np.clip(cos_angle, -1.0, 1.0))
            angle_degrees = np.degrees(angle)
            logger.info("当前位置: %s, 上个位置: %s, 目标位置: %s, 目标距离: %s, 向量夹角: %s度", a, last_a,
                        target_position, d, angle_degrees)
            # 纠正角度，使a指向target_point
            seconds_to_press = angle_degrees * 0.152  # 每55秒旋转360度
            # 计算叉积确定旋转方向
            cross_product = self.cross_product_2d(v1, v2)
            if cross_product > 0:
                # 叉积是正值表示逆时针方向
                pyautogui.keyDown('a')
                time.sleep(seconds_to_press)
                pyautogui.keyUp('a')
            elif cross_product < 0:
                pyautogui.keyDown('d')
                time.sleep(seconds_to_press)
                pyautogui.keyUp('d')
            else:
                logger.info("方向正确")

    # 恢复体力
    def stamina(self, sleep) -> None:
        while True:
            logger.info("恢复体力")
            time.sleep(sleep)

    # 恢复饱食度
    def eat(self, sleep) -> None:
        while True:
            logger.info("恢复饱食度")
            time.sleep(sleep)


if __name__ == "__main__":
    # 26米坑
    p26 = [60, 325, 85, 270]
    # 恢复体力检查间隔
    staminaSleep = 20
    # 恢复饱食度检查间隔
    eatSleep = 60
    trolling = Trolling()
    trolling.trolling(point=p26, stamina_sleep=staminaSleep, eat_sleep=eatSleep)
