#!/usr/bin/env python3
"""图像识别工具 - 基于OpenCV和Tesseract"""

import cv2
import pytesseract
from PIL import ImageGrab
import pyautogui
import time
import numpy as np


class ImageRecognition:
    """图像识别类"""

    def __init__(self, tesseract_path=None):
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path

    def find_image(self, target_image, confidence=0.8):
        """在屏幕上找到目标图像"""
        screenshot = ImageGrab.grab()
        screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        target = cv2.imread(target_image)

        result = cv2.matchTemplate(screenshot_cv, target, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= confidence)

        if locations[0].size > 0:
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            return max_loc

        return None

    def click_image(self, target_image, confidence=0.8):
        """点击屏幕上的目标图像"""
        location = self.find_image(target_image, confidence)

        if location:
            target = cv2.imread(target_image)
            center_x = location[0] + target.shape[1] // 2
            center_y = location[1] + target.shape[0] // 2

            pyautogui.click(center_x, center_y)
            return True

        return False

    def read_text(self, region=None):
        """读取屏幕文字"""
        if region:
            x, y, w, h = region
            screenshot = ImageGrab.grab(bbox=(x, y, x+w, y+h))
        else:
            screenshot = ImageGrab.grab()

        screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
        _, thresh = cv2.threshold(screenshot_cv, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        text = pytesseract.image_to_string(thresh, lang='chi_sim+eng')
        return text.strip()
