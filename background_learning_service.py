#!/usr/bin/env python3
"""
🔄 后台持续学习服务 - 确保系统在用户不在线时也能主动学习
实现无人值守的持续学习能力
"""

import os
import sys
import time
import threading
import json
import signal
import atexit
from datetime import datetime, timedelta
from pathlib import Path
from continuous_learning import ContinuousLearningSystem
from system_state_manager import SystemStateManager


class BackgroundLearningService:
    """
    后台持续学习服务 - 确保系统在用户不在线时也能主动学习
    实现无人值守的持续学习能力
    """

    def __init__(self):
        """初始化后台学习服务"""
        print("🚀 初始化后台持续学习服务")
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)

        # 系统状态管理
        self.state_manager = SystemStateManager()

        # 持续学习系统
        self.learning_system = None

        # 服务状态
        self.is_running = False
        self.service_thread = None

        # 监控配置
        self.check_interval = 60  # 60秒检查一次
        self.max_learning_duration = 3600  # 单次学习最多1小时

        # 注册退出处理
        atexit.register(self._shutdown)
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        print("✅ 后台持续学习服务初始化完成")

    def _signal_handler(self, signum, frame):
        """信号处理"""
        print(f"\n📴 收到信号 {signum}，正在关闭服务...")
        self.stop()

    def _shutdown(self):
        """关闭服务"""
        if self.is_running:
            print("\n🛑 正在关闭后台持续学习服务...")
            self.stop()

    def is_user_offline(self) -> bool:
        """判断用户是否离线"""
        """
        判断用户是否离线的逻辑：
        - 如果最近5分钟内没有交互，则认为用户离线
        """
        try:
            active_state = self.state_manager.get_state("active")
            last_interaction = datetime.fromisoformat(active_state["last_interaction"])
            offline_seconds = (datetime.now() - last_interaction).total_seconds()

            # 5分钟（300秒）内没有交互视为离线
            return offline_seconds > 300

        except Exception as e:
            print(f"⚠️  检查用户状态失败: {e}")
            return True  # 默认假设用户离线

    def should_start_learning(self) -> bool:
        """判断是否应该启动学习"""
        """
        判断是否应该启动学习的逻辑：
        1. 用户离线
        2. 上次学习时间超过一定间隔
        3. 系统资源充足
        """
        try:
            # 1. 用户必须离线
            if not self.is_user_offline():
                return False

            # 2. 检查上次学习时间
            continuous_state = self.state_manager.get_state("continuous")
            last_learning_time = datetime.fromisoformat(continuous_state["last_learning_time"])
            time_since_last_learning = (datetime.now() - last_learning_time).total_seconds()

            # 如果超过30分钟没有学习，则应该开始学习
            if time_since_last_learning > 1800:  # 30分钟
                return True

            # 3. 检查学习频率设置
            search_frequency = continuous_state.get("search_frequency", "high")
            if search_frequency == "high":
                return time_since_last_learning > 600  # 10分钟
            elif search_frequency == "medium":
                return time_since_last_learning > 1800  # 30分钟
            else:
                return time_since_last_learning > 3600  # 1小时

        except Exception as e:
            print(f"⚠️  判断学习条件失败: {e}")
            return True  # 出错时默认应该学习

    def start(self):
        """启动后台学习服务"""
        if self.is_running:
            print("⚠️  后台学习服务已在运行")
            return False

        self.is_running = True
        self.service_thread = threading.Thread(target=self._service_loop)
        self.service_thread.daemon = True
        self.service_thread.start()

        print("✅ 后台持续学习服务启动成功")
        return True

    def _service_loop(self):
        """服务主循环"""
        while self.is_running:
            try:
                # 检查是否需要学习
                if self.should_start_learning():
                    self._start_learning_session()

                # 检查间隔
                for _ in range(self.check_interval):
                    if not self.is_running:
                        break
                    time.sleep(1)

            except Exception as e:
                print(f"⚠️  服务循环错误: {e}")
                time.sleep(60)

    def _start_learning_session(self):
        """启动学习会话"""
        print(f"🎓 用户离线，启动学习会话 ({datetime.now().strftime('%H:%M:%S')})")

        try:
            # 初始化持续学习系统
            self.learning_system = ContinuousLearningSystem()

            # 启动持续学习
            self.learning_system.start_continuous_learning()

            # 学习会话持续时间
            start_time = time.time()
            session_duration = 0

            print(f"🔄 持续学习系统启动成功，将持续学习...")

            # 持续学习直到：
            # 1. 用户上线
            # 2. 学习时间达到上限
            # 3. 服务被停止
            while self.is_running and session_duration < self.max_learning_duration:
                if self.is_user_offline():
                    session_duration = time.time() - start_time
                    time.sleep(30)  # 30秒检查一次
                else:
                    print("👤 用户已上线，停止学习会话")
                    break

            # 停止学习
            self.learning_system.stop_learning()
            print("🛑 学习会话结束")

            # 记录学习会话
            self._record_learning_session(session_duration)

        except Exception as e:
            print(f"⚠️  学习会话失败: {e}")
            import traceback
            print(f"错误详情: {traceback.format_exc()}")

    def _record_learning_session(self, duration_seconds):
        """记录学习会话"""
        try:
            print(f"📊 学习会话记录: {duration_seconds:.1f}秒")

            # 更新学习状态
            continuous_state = self.state_manager.get_state("continuous")

            # 更新学习统计
            continuous_state["learning_count"] += 1
            continuous_state["learning_duration"] += duration_seconds / 60
            continuous_state["last_learning_time"] = datetime.now().isoformat()

            self.state_manager.update_state("continuous", continuous_state)

            print(f"✅ 学习会话已记录")

        except Exception as e:
            print(f"⚠️  记录学习会话失败: {e}")

    def stop(self):
        """停止后台学习服务"""
        if not self.is_running:
            return False

        self.is_running = False

        # 停止学习系统
        if self.learning_system and hasattr(self.learning_system, 'stop_learning'):
            try:
                self.learning_system.stop_learning()
            except:
                pass

        # 等待线程结束
        if self.service_thread and self.service_thread.is_alive():
            self.service_thread.join(timeout=10)

        print("✅ 后台持续学习服务已停止")
        return True

    def get_service_status(self) -> dict:
        """获取服务状态"""
        status = {
            "service_running": self.is_running,
            "user_offline": self.is_user_offline(),
            "learning_system_active": self.learning_system is not None,
            "last_learning_time": "",
            "next_check_time": (datetime.now() + timedelta(seconds=self.check_interval)).strftime('%H:%M:%S')
        }

        try:
            continuous_state = self.state_manager.get_state("continuous")
            status["last_learning_time"] = continuous_state["last_learning_time"]

            # 计算下次学习时间
            last_learning = datetime.fromisoformat(status["last_learning_time"])
            time_since = (datetime.now() - last_learning).total_seconds()

            if status["user_offline"]:
                search_frequency = continuous_state.get("search_frequency", "high")
                if search_frequency == "high":
                    next_learning = 600 - time_since
                elif search_frequency == "medium":
                    next_learning = 1800 - time_since
                else:
                    next_learning = 3600 - time_since

                if next_learning > 0:
                    status["next_learning_time"] = (datetime.now() + timedelta(seconds=next_learning)).strftime('%H:%M:%S')
                else:
                    status["next_learning_time"] = "立即"

        except Exception as e:
            print(f"⚠️  获取服务状态失败: {e}")

        return status

    def start_immediately(self):
        """立即启动学习会话"""
        """用于强制启动学习，不检查用户状态"""
        if not self.is_running:
            print("❌ 服务未运行，请先启动服务")
            return False

        print("🚀 强制启动学习会话")
        threading.Thread(target=self._start_learning_session).start()
        return True


def test_background_learning_service():
    """测试后台学习服务"""
    print("🎯 测试后台持续学习服务")
    print("=" * 60)

    try:
        service = BackgroundLearningService()

        print("\n📊 服务状态检查:")
        status = service.get_service_status()
        print(f"服务运行: {status['service_running']}")
        print(f"用户离线: {status['user_offline']}")
        print(f"学习系统活动: {status['learning_system_active']}")

        print("\n🚀 启动后台学习服务...")
        service.start()

        # 测试运行30秒
        time.sleep(30)

        print("\n📊 服务运行状态:")
        status = service.get_service_status()
        print(f"服务运行: {status['service_running']}")

        if 'next_learning_time' in status:
            print(f"下次学习时间: {status['next_learning_time']}")

        print("\n🛑 停止后台学习服务...")
        service.stop()

        print("✅ 测试完成")
        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        print(traceback.format_exc())
        return False


def start_background_service():
    """启动后台学习服务"""
    print("🎯 启动后台持续学习服务")
    print("=" * 60)

    try:
        service = BackgroundLearningService()
        service.start()

        print("📊 服务状态:")
        status = service.get_service_status()
        print(f"用户状态: {'离线' if status['user_offline'] else '在线'}")
        if status['user_offline']:
            print(f"上次学习: {status['last_learning_time']}")
            if 'next_learning_time' in status:
                print(f"下次学习: {status['next_learning_time']}")

        # 保持服务运行
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            print("\n📴 用户中断")
            service.stop()

        return True

    except Exception as e:
        print(f"\n❌ 启动服务失败: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            test_background_learning_service()
        else:
            print("🚀 启动后台持续学习服务")
            start_background_service()
    else:
        start_background_service()
