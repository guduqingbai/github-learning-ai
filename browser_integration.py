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

        self.browser_config = self.data_dir / "browser_config.json"
        self._init_browser_config()

        # 检测可用的浏览器
        self.available_browsers = self._detect_browsers()

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

        if not self.browser_config.exists():
            with open(self.browser_config, "w", encoding="utf-8") as f:
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
            with open(self.browser_config, "r", encoding="utf-8") as f:
                config = json.load(f)

            if browser_name not in config["browsers"]:
                return False

            browser_config = config["browsers"][browser_name]

            # 检查配置
            if not browser_config.get("enabled", False):
                return False

            # 对于Chrome浏览器，检查是否可以通过API访问
            if browser_name == "chrome":
                try:
                    response = requests.get("http://localhost:9222/json", timeout=2)
                    if response.status_code == 200:
                        return True
                    else:
                        # Chrome浏览器已安装但未以远程调试模式启动
                        print("⚠️  Chrome浏览器已安装但未以远程调试模式启动")
                        return False
                except requests.exceptions.ConnectTimeout:
                    print("⚠️  Chrome API连接超时")
                    return False
                except requests.exceptions.ConnectionError:
                    print("⚠️  Chrome浏览器未启动或未以远程调试模式运行")
                    return False
                except Exception as e:
                    print(f"⚠️  Chrome API访问失败: {e}")
                    return False

            # 对于其他浏览器，使用API连接检查，并添加重试机制
            if "api_url" in browser_config and browser_config["api_url"]:
                # 最大重试次数
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        response = requests.get(browser_config["api_url"], timeout=2)
                        if response.status_code == 200:
                            return True
                    except Exception:
                        if attempt < max_retries - 1:
                            import time
                            time.sleep(0.5)
                            continue
                        else:
                            return False

            return False

        except Exception as e:
            print(f"⚠️  浏览器检测失败: {e}")
            return False

    def get_browser_config(self, browser_name=None):
        """获取浏览器配置"""
        try:
            with open(self.browser_config, "r", encoding="utf-8") as f:
                config = json.load(f)

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
            with open(self.browser_config, "r", encoding="utf-8") as f:
                config = json.load(f)

            if browser_name not in config["browsers"]:
                config["browsers"][browser_name] = config_updates
            else:
                config["browsers"][browser_name].update(config_updates)

            with open(self.browser_config, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)

            return True

        except Exception as e:
            print(f"⚠️  更新浏览器配置失败: {e}")
            return False

    def toggle_browser_integration(self, enabled=True):
        """启用或禁用浏览器集成"""
        try:
            with open(self.browser_config, "r", encoding="utf-8") as f:
                config = json.load(f)

            config["integration"]["enabled"] = enabled

            with open(self.browser_config, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)

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

        return analysis_data

    def _analyze_content(self, content):
        """分析内容与学习的相关性"""
        learning_keywords = [
            "学习", "教程", "文档", "编程", "课程", "视频", "笔记",
            "项目", "代码", "开发", "研究", "论文", "资料"
        ]

        analysis = {
            "relevant": False,
            "keywords": [],
            "content_type": None,
            "learning_score": 0.0
        }

        if "text" in content:
            text = content["text"].lower()
            matched_keywords = []

            for keyword in learning_keywords:
                if keyword in text:
                    matched_keywords.append(keyword)

            if matched_keywords:
                analysis["relevant"] = True
                analysis["keywords"] = matched_keywords
                analysis["learning_score"] = len(matched_keywords) * 0.1

        return analysis if analysis["relevant"] else None

    def sync_browser_data(self):
        """同步浏览器数据到学习系统"""
        browser_data = self.collect_browser_data()

        if browser_data:
            data_file = self.data_dir / "browser_data.json"

            if data_file.exists():
                with open(data_file, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
            else:
                existing_data = {"records": []}

            existing_data["records"].append(browser_data)

            with open(data_file, "w", encoding="utf-8") as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)

            return True

        return False

    def is_integration_enabled(self):
        """检查浏览器集成是否启用"""
        try:
            with open(self.browser_config, "r", encoding="utf-8") as f:
                config = json.load(f)
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
            with open(self.browser_config, "r", encoding="utf-8") as f:
                config = json.load(f)

            config["integration"]["enabled"] = True

            with open(self.browser_config, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)

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

    def get_browser_integration_status(self):
        """获取浏览器集成状态"""
        try:
            with open(self.browser_config, "r", encoding="utf-8") as f:
                config = json.load(f)

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