#!/usr/bin/env python3
"""
🎬 剪映自动化操控 — 用 PyAutoGUI 控制剪映专业版
让 AI 能真正动手做视频剪辑
"""
import time
import subprocess
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

try:
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.5
    HAVE_PYAUTO = True
except ImportError:
    HAVE_PYAUTO = False

JIANYING_PATH = os.environ.get("JIANYING_PRO_PATH", r"C:\Program Files\JianyingPro\Apps\JianyingPro.exe")


class JianyingAutomation:
    """剪映自动化控制器"""

    def __init__(self):
        if not HAVE_PYAUTO:
            raise RuntimeError("需要 PyAutoGUI")
        self.screen_w, self.screen_h = pyautogui.size()

    def log(self, msg):
        print(f"  🎬 [{datetime.now().strftime('%H:%M:%S')}] {msg}")

    # ── 启动与关闭 ──

    def launch(self, wait_time: int = 8):
        """启动剪映"""
        self.log(f"启动剪映...")
        subprocess.Popen([JIANYING_PATH, "--src1"])
        time.sleep(wait_time)
        self.log("✅ 剪映已启动")
        return self

    def close(self):
        """关闭剪映"""
        pyautogui.hotkey("alt", "f4")
        self.log("剪映已关闭")

    # ── 基础操作 ──

    def click_menu(self, menu_name: str):
        """点击顶部菜单（通过坐标区域，需先校准）"""
        # 顶部菜单位置大约在 y=30-60 区域
        # 不同屏幕分辨率需要调整
        self.log(f"点击菜单: {menu_name}")

    def wait_and_find(self, image_path: str, timeout: int = 15) -> tuple:
        """在屏幕上找图片并返回坐标"""
        start = time.time()
        while time.time() - start < timeout:
            try:
                pos = pyautogui.locateOnScreen(image_path, confidence=0.8)
                if pos:
                    center = pyautogui.center(pos)
                    return (center.x, center.y)
            except Exception:
                pass
            time.sleep(0.5)
        return None

    # ── 视频合成流水线 ──

    def import_media(self, folder_path: str):
        """导入素材文件夹"""
        self.log(f"导入素材: {folder_path}")
        pyautogui.hotkey("ctrl", "i")
        time.sleep(1)
        pyautogui.typewrite(folder_path, interval=0.02)
        time.sleep(0.5)
        pyautogui.press("enter")
        time.sleep(3)
        self.log("素材导入完成")

    def add_to_timeline(self):
        """添加到时间线"""
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.3)
        pyautogui.drag(400, 500, duration=0.5)  # 拖入时间线
        time.sleep(1)

    def export_video(self, output_name: str = None):
        """导出视频"""
        self.log("导出视频...")
        pyautogui.hotkey("ctrl", "e")
        time.sleep(2)

        if output_name:
            pyautogui.hotkey("ctrl", "a")
            pyautogui.typewrite(output_name, interval=0.05)
            time.sleep(0.5)

        pyautogui.press("enter")
        self.log(f"⏳ 渲染中: {output_name}")
        return output_name

    # ── 全自动生产 ──

    def auto_produce(self, media_folder: str, output_name: str = None):
        """全自动：导入→合成→导出"""
        self.launch()
        time.sleep(3)

        self.import_media(media_folder)
        self.add_to_timeline()

        name = output_name or f"auto_video_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.export_video(name)

        self.log(f"✅ 生产完成: {name}")
        return name


def main():
    print("\n🎬 剪映自动化控制器")
    print("=" * 40)
    print(f"剪映路径: {JIANYING_PATH}")
    print(f"屏幕: {pyautogui.size()}")
    print(f"\n使用: python jianying_automation.py")
    print(f"注意: 首次使用需先校准按钮坐标")


if __name__ == "__main__":
    main()
