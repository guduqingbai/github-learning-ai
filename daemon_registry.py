"""
🗂️ 守护进程注册中心 — 打破 self_thinking_agent ↔ thinking_daemon 循环依赖

持有 ThinkingDaemon 全局单例引用，供各模块通过 get_daemon() 获取。
thinking_daemon.py 启动时调用 register_daemon(self) 注册自身。
"""

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from thinking_daemon import ThinkingDaemon

_daemon_instance: Optional["ThinkingDaemon"] = None


def register_daemon(daemon: "ThinkingDaemon") -> None:
    """注册守护进程实例（由 thinking_daemon.py 在 __init__ 末尾调用）"""
    global _daemon_instance
    _daemon_instance = daemon


def get_daemon():
    """获取全局守护进程实例（首次调用时自动创建）"""
    global _daemon_instance
    if _daemon_instance is None:
        from thinking_daemon import ThinkingDaemon
        _daemon_instance = ThinkingDaemon()
    return _daemon_instance
