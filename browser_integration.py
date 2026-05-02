#!/usr/bin/env python3
"""
🎯 浏览器集成模块
提供与Tabbit浏览器及其他浏览器的集成接口
"""

import os
import sys
import time
import json
import requests
import subprocess
from datetime import datetime
from pathlib import Path
from utils import measure_performance

class BrowserIntegration:
    """浏览器集成类"""

    def __init__(self):
        """初始化浏览器集成模块"""
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)

        self.browser_config_path = self.data_dir / "browser_config.json"
        self._config_cache = None
        self._init_browser_config()

        # 检测可用的浏览器
        self.available_browsers = self._detect_browsers()

    def _get_config(self):
        """获取配置（带缓存）"""
        if self._config_cache is not None:
            return self._config_cache
        with open(self.browser_config_path, "r", encoding="utf-8") as f:
            self._config_cache = json.load(f)
        return self._config_cache

    def _invalidate_cache(self):
        """使配置缓存失效"""
        self._config_cache = None

    def _init_browser_config(self):
        """初始化浏览器配置"""
        default_config = {
            "default_browser": "tabbit",
            "browsers": {
                "tabbit": {
                    "name": "Tabbit Browser",
                    "executable": "tabbit",
                    "api_url": "http://localhost:8080/api",
                    "extension_id": None,
                    "enabled": False
                },
                "chrome": {
                    "name": "Google Chrome",
                    "executable": "chrome",
                    "api_url": "http://localhost:9222/json",
                    "extension_id": None,
                    "enabled": False
                },
                "firefox": {
                    "name": "Mozilla Firefox",
                    "executable": "firefox",
                    "api_url": "http://localhost:6000/api",
                    "extension_id": None,
                    "enabled": False
                }
            },
            "integration": {
                "enabled": False,
                "learning_data_collection": True,
                "content_analysis": True,
                "browser_sync": False
            }
        }

        if not self.browser_config_path.exists():
            with open(self.browser_config_path, "w", encoding="utf-8") as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)

    def _detect_browsers(self):
        """检测可用的浏览器"""
        available = []

        # 检查Tabbit浏览器
        if self._check_browser_available("tabbit"):
            available.append("tabbit")

        # 检查其他常见浏览器
        browsers_to_check = ["chrome", "firefox", "edge"]
        for browser in browsers_to_check:
            if self._check_browser_available(browser):
                available.append(browser)

        return available

    def _check_browser_available(self, browser_name):
        """检查浏览器是否可用"""
        try:
            config = self._get_config()

            if browser_name not in config["browsers"]:
                return False

            browser_config = config["browsers"][browser_name]

            # 检查配置
            if not browser_config.get("enabled", False):
                return False

            # 对于Chrome浏览器，检查是否可以通过API访问
            if browser_name == "chrome":
                # 尝试多个可能的Chrome调试端口
                possible_ports = [9222, 9223, 9224, 9225]
                for port in possible_ports:
                    try:
                        response = requests.get(f"http://localhost:{port}/json", timeout=2)
                        if response.status_code == 200:
                            # 更新配置中的API URL
                            self.set_browser_config(browser_name, {"api_url": f"http://localhost:{port}/json"})
                            return True
                    except requests.exceptions.ConnectTimeout:
                        continue
                    except requests.exceptions.ConnectionError:
                        continue
                    except Exception as e:
                        print(f"⚠️  Chrome API访问失败: {e}")
                        continue

                # 尝试通过系统命令检测Chrome是否安装
                if self._is_chrome_installed():
                    print("⚠️  Chrome浏览器已安装但未以远程调试模式启动")
                    return False
                else:
                    print("⚠️  未检测到Chrome浏览器")
                    return False

            # 对于其他浏览器，使用API连接检查，并添加重试机制
            if "api_url" in browser_config and browser_config["api_url"]:
                # 最大重试次数
                max_retries = 5
                for attempt in range(max_retries):
                    try:
                        response = requests.get(browser_config["api_url"], timeout=3)
                        if response.status_code == 200:
                            return True
                    except Exception:
                        if attempt < max_retries - 1:
                            time.sleep(1)
                            continue
                        else:
                            return False

            # 对于无法通过API检查的浏览器，尝试通过其他方式检测
            if browser_name in ["firefox", "edge"]:
                # 尝试通过系统命令检测浏览器是否安装
                try:
                    if browser_name == "firefox":
                        # 检查Firefox浏览器是否安装
                        if sys.platform.startswith('win'):
                            import winreg
                            try:
                                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Mozilla\Mozilla Firefox")
                                winreg.CloseKey(key)
                                return True
                            except FileNotFoundError:
                                return False
                        elif sys.platform.startswith('darwin'):
                            return os.path.exists("/Applications/Firefox.app")
                        else:
                            return os.path.exists("/usr/bin/firefox") or os.path.exists("/usr/local/bin/firefox")

                    elif browser_name == "edge":
                        # 检查Edge浏览器是否安装
                        if sys.platform.startswith('win'):
                            import winreg
                            try:
                                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Edge")
                                winreg.CloseKey(key)
                                return True
                            except FileNotFoundError:
                                return False
                        elif sys.platform.startswith('darwin'):
                            return os.path.exists("/Applications/Microsoft Edge.app")
                        else:
                            return os.path.exists("/usr/bin/microsoft-edge") or os.path.exists("/usr/local/bin/microsoft-edge")

                except Exception as e:
                    print(f"⚠️  检测{browser_name}浏览器失败: {e}")
                    return False

            return False

        except Exception as e:
            print(f"⚠️  浏览器检测失败: {e}")
            return False

    def get_browser_config(self, browser_name=None):
        """获取浏览器配置"""
        try:
            config = self._get_config()

            if browser_name:
                return config["browsers"].get(browser_name)
            else:
                return config

        except Exception as e:
            print(f"⚠️  读取浏览器配置失败: {e}")
            return None

    def set_browser_config(self, browser_name, config_updates):
        """更新浏览器配置"""
        try:
            config = self._get_config()

            if browser_name not in config["browsers"]:
                config["browsers"][browser_name] = config_updates
            else:
                config["browsers"][browser_name].update(config_updates)

            with open(self.browser_config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)

            self._invalidate_cache()
            return True

        except Exception as e:
            print(f"⚠️  更新浏览器配置失败: {e}")
            return False

    def toggle_browser_integration(self, enabled=True):
        """启用或禁用浏览器集成"""
        try:
            config = self._get_config()

            config["integration"]["enabled"] = enabled

            with open(self.browser_config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)

            self._invalidate_cache()
            return True

        except Exception as e:
            print(f"⚠️  浏览器集成配置失败: {e}")
            return False

    def collect_browser_data(self):
        """收集浏览器数据"""
        if not self.is_integration_enabled():
            return None

        browser_data = {
            "timestamp": datetime.now().isoformat(),
            "browsers": {},
            "learning_activity": [],
            "content_analysis": []
        }

        for browser in self.available_browsers:
            browser_data["browsers"][browser] = self._collect_browser_specific_data(browser)

        return browser_data

    def _collect_browser_specific_data(self, browser_name):
        """收集特定浏览器的数据"""
        browser_data = {
            "active": False,
            "tabs": [],
            "history": [],
            "content": []
        }

        try:
            config = self.get_browser_config(browser_name)

            if not config or not config.get("enabled", False):
                return browser_data

            # 尝试获取浏览器数据
            if config.get("api_url"):
                try:
                    response = requests.get(config["api_url"], timeout=3)
                    if response.status_code == 200:
                        browser_data["active"] = True
                        data = response.json()

                        if "tabs" in data:
                            browser_data["tabs"] = data["tabs"]
                        if "history" in data:
                            browser_data["history"] = data["history"]
                        if "content" in data:
                            browser_data["content"] = data["content"]

                except Exception as e:
                    print(f"⚠️  获取{config['name']}数据失败: {e}")

        except Exception as e:
            print(f"⚠️  浏览器数据收集失败: {e}")

        return browser_data

    def analyze_browser_content(self):
        """分析浏览器内容"""
        if not self.is_integration_enabled():
            return None

        analysis_data = []

        for browser in self.available_browsers:
            browser_data = self._collect_browser_specific_data(browser)

            if browser_data["active"]:
                # 分析浏览器内容
                for content in browser_data["content"]:
                    analysis = self._analyze_content(content)
                    if analysis:
                        analysis_data.append({
                            "browser": browser,
                            "timestamp": datetime.now().isoformat(),
                            "analysis": analysis
                        })

        # 如果浏览器分析数据为空，尝试分析本地学习内容
        if not analysis_data:
            analysis_data = self._analyze_local_learning_content()

        return analysis_data

    def _analyze_local_learning_content(self):
        """分析本地学习内容"""
        analysis_data = []

        # 检查是否有本地学习内容文件
        local_content_files = [
            "learning_notes.txt",
            "study_materials.md",
            "course_notes.txt"
        ]

        for filename in local_content_files:
            if os.path.exists(filename):
                try:
                    with open(filename, "r", encoding="utf-8") as f:
                        content = f.read()

                    # 分析本地内容
                    analysis = self._analyze_content({"text": content})
                    if analysis:
                        analysis_data.append({
                            "browser": "local",
                            "timestamp": datetime.now().isoformat(),
                            "analysis": analysis,
                            "source": filename
                        })

                except Exception as e:
                    print(f"⚠️  分析本地内容文件失败: {e}")

        return analysis_data

    def _is_chrome_installed(self):
        """检查Chrome浏览器是否安装"""
        try:
            if sys.platform.startswith('win'):
                import winreg
                try:
                    # 检查Chrome浏览器是否在注册表中
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Google\Chrome")
                    winreg.CloseKey(key)
                    return True
                except FileNotFoundError:
                    try:
                        # 检查Chrome浏览器的安装路径
                        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
                        return os.path.exists(chrome_path)
                    except Exception:
                        return False
            elif sys.platform.startswith('darwin'):
                # macOS系统检查Chrome是否安装
                chrome_path = "/Applications/Google Chrome.app"
                return os.path.exists(chrome_path)
            else:
                # Linux系统检查Chrome是否安装
                try:
                    result = subprocess.run(["which", "google-chrome"], capture_output=True, text=True)
                    return result.returncode == 0
                except Exception:
                    try:
                        result = subprocess.run(["which", "chrome"], capture_output=True, text=True)
                        return result.returncode == 0
                    except Exception:
                        return False
        except Exception as e:
            print(f"⚠️  检测Chrome浏览器安装状态失败: {e}")
            return False

    def _analyze_content(self, content):
        """分析内容与学习的相关性"""
        learning_keywords = [
            "学习", "教程", "文档", "编程", "课程", "视频", "笔记",
            "项目", "代码", "开发", "研究", "论文", "资料"
        ]

        analysis = {
            "title": "",
            "relevant": False,
            "relevance": 0.0,
            "keywords": [],
            "content_type": None,
            "learning_score": 0.0
        }

        if isinstance(content, str):
            text = content.lower()
            analysis["title"] = content[:80]
        elif "text" in content:
            text = content["text"].lower()
            analysis["title"] = content.get("title", content["text"][:80])
        else:
            text = str(content).lower()
            analysis["title"] = str(content)[:80]

        matched_keywords = []

        for keyword in learning_keywords:
            if keyword in text:
                matched_keywords.append(keyword)

        if matched_keywords:
            analysis["relevant"] = True
            analysis["keywords"] = matched_keywords
            analysis["learning_score"] = len(matched_keywords) * 0.1
            analysis["relevance"] = min(1.0, analysis["learning_score"])

        return analysis if analysis["relevant"] else None

    def is_integration_enabled(self):
        """检查浏览器集成是否启用"""
        try:
            config = self._get_config()
            return config["integration"]["enabled"]

        except Exception as e:
            print(f"⚠️  读取集成配置失败: {e}")
            return False

    def test_browser_connection(self, browser_name):
        """测试浏览器连接"""
        try:
            config = self.get_browser_config(browser_name)

            if not config or not config.get("api_url"):
                return False, "没有配置API"

            response = requests.get(config["api_url"], timeout=5)
            if response.status_code == 200:
                return True, "连接成功"
            else:
                return False, f"连接失败: {response.status_code}"

        except requests.exceptions.ConnectionError:
            return False, "无法连接到浏览器API"
        except Exception as e:
            return False, f"错误: {e}"

    @measure_performance
    def enable_browser_integration(self, browser_name):
        """启用特定浏览器的集成"""
        try:
            # 检查浏览器是否已配置
            config = self.get_browser_config(browser_name)
            if not config:
                return False, "浏览器未配置"

            # 测试连接
            is_connected, message = self.test_browser_connection(browser_name)

            if not is_connected:
                print(f"⚠️  浏览器连接测试失败: {message}")

            # 启用集成
            self.set_browser_config(browser_name, {"enabled": True})

            # 更新集成配置
            config = self._get_config()

            config["integration"]["enabled"] = True

            with open(self.browser_config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)

            self._invalidate_cache()

            return True, "浏览器集成已启用"

        except Exception as e:
            return False, f"启用失败: {e}"

    def start_learning_content_analysis(self):
        """启动学习内容分析"""
        if not self.is_integration_enabled():
            return False, "浏览器集成未启用"

        print("🎯 开始浏览器内容分析...")

        try:
            analysis_data = self.analyze_browser_content()

            if analysis_data:
                print(f"✅ 分析完成: 找到 {len(analysis_data)} 个学习相关内容")

                # 将分析结果保存到学习系统
                analysis_file = self.data_dir / "browser_analysis.json"
                with open(analysis_file, "w", encoding="utf-8") as f:
                    json.dump(analysis_data, f, ensure_ascii=False, indent=2)

                return True, f"成功分析了 {len(analysis_data)} 个学习相关内容"

            else:
                return False, "未找到学习相关内容"

        except Exception as e:
            return False, f"分析失败: {e}"

    def get_available_browsers(self):
        """获取可用浏览器列表"""
        return self.available_browsers

    def get_browser_integration_status(self):
        """获取浏览器集成状态"""
        try:
            config = self._get_config()

            status = {
                "enabled": config["integration"]["enabled"],
                "available_browsers": self.available_browsers,
                "config": config
            }

            return status

        except Exception as e:
            print(f"⚠️  获取集成状态失败: {e}")
            return None

def main():
    """测试函数"""
    browser_integration = BrowserIntegration()

    print("🎯 浏览器集成模块测试")
    print("=" * 50)

    # 打印浏览器配置
    config = browser_integration.get_browser_config()
    print(f"🌐 配置的浏览器: {list(config['browsers'].keys())}")
    print(f"✅ 可用的浏览器: {browser_integration.available_browsers}")

    if config["integration"]["enabled"]:
        print("🔗 浏览器集成: 已启用")
    else:
        print("🔗 浏览器集成: 已禁用")

    # 测试浏览器连接
    for browser in config["browsers"]:
        if config["browsers"][browser]["enabled"]:
            is_connected, message = browser_integration.test_browser_connection(browser)
            print(f"   {config['browsers'][browser]['name']}: {'✅' if is_connected else '❌'} {message}")

    if browser_integration.available_browsers:
        # 测试数据收集
        print("\n📊 测试浏览器数据收集:")
        browser_data = browser_integration.collect_browser_data()
        if browser_data:
            print(f"   成功收集数据")
        else:
            print(f"   数据收集失败")

        # 测试内容分析
        print("\n🎯 测试内容分析:")
        analysis = browser_integration.start_learning_content_analysis()
        print(f"   {analysis}")

    print("\n✅ 浏览器集成模块测试完成")

if __name__ == "__main__":
    main()