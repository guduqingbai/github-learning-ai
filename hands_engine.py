#!/usr/bin/env python3
"""
🖐️👁️ 手眼系统 — Playwright 看 + PyAutoGUI 动
真正的动手能力：开浏览器、看网页、点按钮、填表单、截屏

依赖: playwright, PyAutoGUI
首次使用需: python -m playwright install chromium
"""
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"


class HandsEngine:
    """手眼系统 — 看得见、摸得着"""

    def __init__(self):
        self.context = None
        self.page = None
        self.browser = None
        self.playwright = None
        self.ready = False
        self._cdp_mode = False
        self._chrome_proc = None

    def log(self, msg: str):
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"  🤖 [{ts}] {msg}")

    # ═══════════════════════════════════════
    #  👁️ 视觉 — Playwright 浏览器操控
    # ═══════════════════════════════════════

    def launch_browser(self, headless: bool = True, user_data_dir: str = None,
                       anti_detect: bool = True):
        """启动浏览器 — 使用 persistent context 保留登录态

        Args:
            headless: 是否无头模式
            user_data_dir: Chrome 用户数据目录（传 None 则用 data/playwright_profile）
            anti_detect: 启用反检测措施（隐藏 Playwright 指纹）
        """
        from playwright.sync_api import sync_playwright
        import os
        self.playwright = sync_playwright().start()
        chrome_paths = [
            "C:/Program Files/Google/Chrome/Application/chrome.exe",
            "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
        ]
        chrome_exe = next((p for p in chrome_paths if os.path.exists(p)), None)

        ctx_kwargs = {
            "headless": headless,
            "viewport": {"width": 1280, "height": 800},
            "user_data_dir": user_data_dir or str(DATA_DIR / "playwright_profile"),
        }
        if chrome_exe and "chrome" in chrome_exe.lower():
            ctx_kwargs["channel"] = "chrome"
        if chrome_exe:
            ctx_kwargs["executable_path"] = chrome_exe
        if anti_detect:
            ctx_kwargs["args"] = [
                "--disable-blink-features=AutomationControlled",
                "--disable-features=ChromeWhatsNewUI",
            ]

        self.context = self.playwright.chromium.launch_persistent_context(**ctx_kwargs)

        # 反检测: 隐藏 Playwright 痕迹
        self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
        if anti_detect:
            self.page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                Object.defineProperty(navigator, 'plugins', { get: () => [1,2,3,4,5] });
                Object.defineProperty(navigator, 'languages', { get: () => ['zh-CN', 'zh'] });
            """)

        self.ready = True
        self.log(f"✅ 浏览器已启动 (persistent context{' + anti-detect' if anti_detect else ''})")
        return self

    def launch_cdp(self, port: int = 9222, user_data_dir: str = None,
                   browser: str = "auto"):
        """通过 CDP 连接真实浏览器 — 最强反检测

        启动独立浏览器进程并开启远程调试端口，Playwright 通过 CDP 直连。
        真实浏览器 + 真实用户数据，无 Playwright 指纹，无法被检测为自动化。

        Args:
            port: 远程调试端口
            user_data_dir: 用户数据目录。None 则自动检测真实目录
            browser: "chrome", "edge", 或 "auto"（自动检测）
        """
        import subprocess, os, time, socket

        # 浏览器路径检测
        browser_paths = {
            "edge": os.path.expandvars(
                r"%PROGRAMFILES(X86)%\Microsoft\Edge\Application\msedge.exe"
            ),
            "chrome": "C:/Program Files/Google/Chrome/Application/chrome.exe",
        }
        browser_data_dirs = {
            "edge": os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\User Data"),
            "chrome": os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data"),
        }

        # 自动检测可用浏览器
        if browser == "auto":
            for name, path in browser_paths.items():
                if os.path.exists(path):
                    browser = name
                    break
            else:
                raise FileNotFoundError("未找到 Chrome 或 Edge")

        path = browser_paths.get(browser, browser_paths["chrome"])
        if not os.path.exists(path):
            raise FileNotFoundError(f"{browser} 未找到: {path}")

        # 检测浏览器是否正在运行
        exe_name = os.path.basename(path)
        running = any(exe_name in x.lower() for x in os.popen("tasklist").read())

        if user_data_dir is None:
            if running:
                user_data_dir = str(DATA_DIR / f"playwright_{browser}_profile")
                self.log(f"ℹ️ {browser} 正在运行，使用独立 profile")
            else:
                user_data_dir = browser_data_dirs.get(browser, browser_data_dirs["chrome"])
                self.log(f"ℹ️ 使用 {browser} 真实用户数据")
        self.log(f"🚀 启动 {browser} (CDP 端口 {port})")
        self._chrome_proc = subprocess.Popen([
            path,
            f"--remote-debugging-port={port}",
            f"--user-data-dir={user_data_dir}",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-features=ChromeWhatsNewUI",
            "--disable-sync",  # 关闭同步加速启动
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # 等待浏览器就绪（轮询端口，最多 40 秒）
        import socket
        for i in range(40):
            time.sleep(1)
            try:
                s = socket.create_connection(("127.0.0.1", port), timeout=1)
                s.close()
                self.log(f"  {browser} 就绪 ({i+1}s)")
                break
            except (ConnectionRefusedError, OSError):
                if i == 39:
                    self._chrome_proc.terminate()
                    self._chrome_proc = None
                    raise TimeoutError(f"{browser} 启动超时 (端口 {port})")

        from playwright.sync_api import sync_playwright
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.connect_over_cdp(f"http://localhost:{port}")

        # 取第一个已有 context 或新建
        contexts = self.browser.contexts
        if contexts:
            self.context = contexts[0]
            pages = self.context.pages
            self.page = pages[0] if pages else self.context.new_page()
        else:
            self.context = self.browser.new_context()
            self.page = self.context.new_page()

        self._cdp_mode = True
        self.ready = True
        self.log("✅ 真实 Chrome 已启动 (CDP 模式 — 无法被检测)")
        return self

    def close_browser(self):
        """关闭浏览器"""
        if self.page and self._cdp_mode:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        if self._chrome_proc:
            self._chrome_proc.terminate()
        self.ready = False
        self.log("🔒 浏览器已关闭")

    def navigate(self, url: str, wait_until: str = "domcontentloaded") -> bool:
        """导航到URL"""
        if not self.ready:
            self.log("⚠️ 浏览器未启动")
            return False
        try:
            self.page.goto(url, wait_until=wait_until, timeout=30000)
            self.log(f"🌐 已加载: {url}")
            return True
        except Exception as e:
            self.log(f"❌ 加载失败: {e}")
            return False

    def see(self) -> str:
        """看当前页面的文本内容"""
        if not self.ready:
            return ""
        text = self.page.inner_text("body")[:2000]
        return text

    def screenshot(self, name: str = "web") -> Path:
        """截取浏览器当前画面"""
        DATA_DIR.mkdir(exist_ok=True)
        path = DATA_DIR / f"hands_{name}_{datetime.now().strftime('%H%M%S')}.png"
        self.page.screenshot(path=str(path))
        self.log(f"📸 网页截图: {path.name}")
        return path

    def find_text(self, text: str) -> bool:
        """在页面找文字"""
        body = self.page.inner_text("body")
        return text.lower() in body.lower()

    def click_text(self, text: str):
        """点击包含指定文字的链接/按钮"""
        self.log(f"🎯 点击: '{text}'")
        self.page.get_by_text(text, exact=False).first.click()
        time.sleep(1)

    def fill_input(self, placeholder: str, text: str):
        """填写输入框"""
        self.log(f"✏️ 填写 [{placeholder}]: {text[:30]}...")
        self.page.get_by_placeholder(placeholder).fill(text)
        time.sleep(0.5)

    def extract_links(self) -> List[Dict]:
        """提取页面上所有链接"""
        links = self.page.eval_on_selector_all(
            "a[href]",
            "els => els.map(el => ({ text: el.innerText.trim(), href: el.href }))"
        )
        return [l for l in links if l["text"]][:20]

    # ═══════════════════════════════════════
    #  🖐️ 触觉 — PyAutoGUI 桌面操控
    # ═══════════════════════════════════════

    def desktop_click(self, x: int, y: int):
        """桌面坐标点击"""
        import pyautogui
        pyautogui.click(x, y)
        self.log(f"🖱️ 桌面点击 ({x}, {y})")

    def desktop_type(self, text: str):
        """桌面键盘输入"""
        import pyautogui
        pyautogui.typewrite(text, interval=0.02)
        self.log(f"⌨️ 输入: {text[:40]}")

    def desktop_screenshot(self) -> Path:
        """截取桌面"""
        import pyautogui
        DATA_DIR.mkdir(exist_ok=True)
        path = DATA_DIR / f"desktop_{datetime.now().strftime('%H%M%S')}.png"
        pyautogui.screenshot(str(path))
        self.log(f"📸 桌面截图: {path.name}")
        return path

    # ═══════════════════════════════════════
    #  🎯 实用技能组合
    # ═══════════════════════════════════════

    def check_github_repo(self, repo: str = "guduqingbai/github-learning-ai"):
        """检查GitHub仓库状态"""
        url = f"https://github.com/{repo}"
        self.navigate(url)
        time.sleep(2)

        info = {"repo": repo, "url": url}

        try:
            # 提取 Star 数
            star_el = self.page.query_selector("span[aria-label$='stars']")
            if star_el:
                info["stars"] = star_el.inner_text().strip()
        except Exception:
            info["stars"] = "?"

        try:
            info["description"] = self.page.query_selector("p.f4").inner_text().strip()[:100]
        except Exception:
            info["description"] = "?"

        try:
            info["title"] = self.page.query_selector("strong[itemprop='name']").inner_text().strip()
        except Exception:
            info["title"] = repo

        self.log(f"📊 {info.get('title', repo)} | ⭐ {info.get('stars', '?')}")
        return info

    def open_fiverr(self):
        """打开 Fiverr — 检查机会"""
        self.log("🌐 打开 Fiverr...")
        self.navigate("https://www.fiverr.com/")
        return self.screenshot("fiverr_home")

    def search_bing(self, query: str) -> List[Dict]:
        """Bing 搜索（国内可用）"""
        self.navigate(f"https://cn.bing.com/search?q={query}")
        time.sleep(2)

        results = self.page.eval_on_selector_all(
            "li.b_algo",
            "els => els.map(el => ({ title: el.querySelector('h2')?.innerText, snippet: el.querySelector('.b_caption p')?.innerText }))"
        )
        self.log(f"🔍 '{query}': 找到 {len(results)} 条结果")
        return [r for r in results if r.get("title")][:5]

    # ═══════════════════════════════════════
    #  ⚡ 一键行动
    # ═══════════════════════════════════════

    def run_task(self, task_type: str, **kwargs):
        """运行预定义任务"""
        tasks = {
            "check_repo": lambda: self.check_github_repo(**kwargs),
            "search": lambda: self.search_bing(kwargs.get("query", "")),
            "screenshot_web": lambda: self.navigate(kwargs["url"]) or self.screenshot("task"),
            "screenshot_desktop": lambda: self.desktop_screenshot(),
        }
        fn = tasks.get(task_type)
        if fn:
            return fn()
        self.log(f"⚠️ 未知任务: {task_type}")
        return None


def demo():
    """演示手眼系统"""
    print("\n" + "=" * 50)
    print("🤖 手眼系统 — 能看能动的AI")
    print("=" * 50)

    hands = HandsEngine()

    # 1. 启动浏览器
    hands.launch_browser(headless=False)  # 有头模式让你看到

    # 2. 检查自己的GitHub仓库
    info = hands.check_github_repo()
    print(f"\n📊 仓库状态:")
    for k, v in info.items():
        print(f"  {k}: {v}")

    # 3. 截屏
    path = hands.screenshot("repo")
    print(f"\n📸 截图保存: {path}")

    # 4. 搜索 — 找Fiverr机会
    results = hands.search_bing("Fiverr AI video creation services 2026")
    if results:
        print(f"\n🔍 搜索发现:")
        for r in results[:3]:
            print(f"  • {r.get('title', '')[:60]}")

    # 5. 看看桌面
    desktop = hands.desktop_screenshot()
    print(f"\n🖥️ 桌面截图: {desktop}")

    # 6. 关闭浏览器
    hands.close_browser()
    print(f"\n✅ 手眼系统演示完成")


if __name__ == "__main__":
    demo()
