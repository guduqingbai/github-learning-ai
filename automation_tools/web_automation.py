#!/usr/bin/env python3
"""Web自动化工具 - 基于Selenium"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class WebAutomation:
    """Web自动化类"""

    def __init__(self):
        self.driver = None

    def start_browser(self):
        """启动浏览器"""
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )

        self.driver.implicitly_wait(5)
        return True

    def create_github_repo(self, repo_name, repo_desc):
        """创建GitHub仓库"""
        if not self.driver:
            self.start_browser()

        # 打开GitHub
        self.driver.get('https://github.com')

        # 点击New按钮（实际根据页面结构调整）
        new_button = self.driver.find_element(By.XPATH, "//a[contains(text(), 'New')]")
        new_button.click()

        # 填写表单
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'repository[name]'))
        )

        self.driver.find_element(By.NAME, 'repository[name]').send_keys(repo_name)
        self.driver.find_element(By.NAME, 'repository[description]').send_keys(repo_desc)

        # 选择Public
        self.driver.find_element(By.XPATH, "//input[@name='repository[visibility]'][@value='public']").click()

        # 创建仓库
        self.driver.find_element(By.XPATH, "//button[contains(text(), 'Create')]").click()

        return True
