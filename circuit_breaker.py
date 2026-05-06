"""
⚡ 熔断器 — 三态故障隔离
受 Phoenix Immortal circuit_breaker.py 启发
CLOSED → OPEN（连续失败达阈值）→ HALF_OPEN（冷却后试探）→ CLOSED/OPEN
"""

import json
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, Any, Optional, List


class CircuitState(str, Enum):
    CLOSED = "closed"         # 正常
    OPEN = "open"             # 熔断中，快速拒绝
    HALF_OPEN = "half_open"   # 半开，试探性允许


class CircuitBreaker:
    """熔断器：按操作隔离故障，防连锁崩溃"""

    def __init__(
        self,
        data_dir: Path,
        failure_threshold: int = 3,
        cooldown_seconds: int = 120,
        half_open_max_calls: int = 1,
    ):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._state_file = self.data_dir / "circuit_breaker.json"

        # 配置
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self.half_open_max_calls = half_open_max_calls

        # 运行时状态（key → breaker state）
        self._breakers: Dict[str, dict] = {}

        self._load()
        self._bootstrap_defaults()

    def _bootstrap_defaults(self):
        """确保常用操作有初始条目"""
        defaults = [
            "antibody:add_docstring",
            "antibody:fix_bare_except",
            "cycle:thinking",
        ]
        for key in defaults:
            if key not in self._breakers:
                self._breakers[key] = {
                    "state": CircuitState.CLOSED.value,
                    "failure_count": 0,
                    "last_failure_time": 0,
                    "half_open_calls": 0,
                    "total_successes": 0,
                    "total_failures": 0,
                    "last_state_change": 0,
                }

    # ── 持久化 ──

    def _load(self):
        if self._state_file.exists():
            try:
                data = json.loads(self._state_file.read_text(encoding="utf-8"))
                self._breakers = data.get("breakers", {})
                # 确保时间戳为 float
                for v in self._breakers.values():
                    for field in ["last_failure_time", "last_state_change"]:
                        if field in v and isinstance(v[field], str):
                            try:
                                v[field] = float(datetime.fromisoformat(v[field]).timestamp())
                            except Exception:
                                v[field] = 0
            except (json.JSONDecodeError, Exception):
                self._breakers = {}

    def _save(self):
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            self._state_file.write_text(
                json.dumps({"breakers": self._breakers}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception:
            pass

    # ── 核心接口 ──

    def _get(self, key: str) -> dict:
        if key not in self._breakers:
            self._breakers[key] = {
                "state": CircuitState.CLOSED.value,
                "failure_count": 0,
                "last_failure_time": 0,
                "half_open_calls": 0,
                "total_successes": 0,
                "total_failures": 0,
                "last_state_change": 0,
            }
        return self._breakers[key]

    def state(self, key: str) -> CircuitState:
        """获取当前状态（自动处理超时转换）"""
        b = self._get(key)
        now = time.time()

        if b["state"] == CircuitState.OPEN.value:
            elapsed = now - b["last_failure_time"]
            if elapsed >= self.cooldown_seconds:
                self._transition(key, CircuitState.HALF_OPEN)
                b["half_open_calls"] = 0
                self._save()

        return CircuitState(b["state"])

    def call(self, key: str) -> bool:
        """询问断路器是否允许本次调用。返回 True = 允许"""
        s = self.state(key)
        if s == CircuitState.OPEN:
            return False  # 快速拒绝

        b = self._get(key)
        if s == CircuitState.HALF_OPEN and b["half_open_calls"] >= self.half_open_max_calls:
            return False  # 半开状态已用完试探配额

        return True

    def on_success(self, key: str):
        """记录成功"""
        b = self._get(key)
        b["total_successes"] += 1
        b["failure_count"] = 0

        if b["state"] == CircuitState.HALF_OPEN.value:
            self._transition(key, CircuitState.CLOSED)

        self._save()

    def on_failure(self, key: str):
        """记录失败"""
        b = self._get(key)
        b["total_failures"] += 1
        b["failure_count"] += 1
        b["last_failure_time"] = time.time()

        if b["state"] == CircuitState.CLOSED.value:
            if b["failure_count"] >= self.failure_threshold:
                self._transition(key, CircuitState.OPEN)
        elif b["state"] == CircuitState.HALF_OPEN.value:
            self._transition(key, CircuitState.OPEN)

        self._save()

    def _transition(self, key: str, to: CircuitState):
        """状态转换"""
        b = self._get(key)
        b["state"] = to.value
        b["last_state_change"] = time.time()
        if to == CircuitState.CLOSED:
            b["failure_count"] = 0
            b["half_open_calls"] = 0

    # ── 管理接口 ──

    def reset(self, key: str):
        """手动重置某个操作的熔断器"""
        if key in self._breakers:
            del self._breakers[key]
        self._save()

    def reset_all(self):
        """重置所有熔断器"""
        self._breakers = {}
        self._bootstrap_defaults()
        self._save()

    def get_info(self, key: str) -> Dict[str, Any]:
        """获取某个操作的熔断状态详情"""
        b = self._get(key)
        now = time.time()
        remaining = max(0, self.cooldown_seconds - (now - b["last_failure_time"])) \
            if b["state"] == CircuitState.OPEN.value else 0
        return {
            "key": key,
            "state": b["state"],
            "failure_count": b["failure_count"],
            "total_successes": b["total_successes"],
            "total_failures": b["total_failures"],
            "success_rate": round(
                b["total_successes"] / max(1, b["total_successes"] + b["total_failures"]) * 100, 1
            ),
            "cooldown_remaining_s": round(remaining, 1),
            "threshold": self.failure_threshold,
            "half_open_max_calls": self.half_open_max_calls,
        }

    def get_all_info(self) -> List[Dict]:
        """获取所有操作的熔断状态"""
        return [self.get_info(k) for k in sorted(self._breakers.keys())]

    def get_summary(self) -> str:
        lines = ["⚡ 熔断器状态:"]
        for info in self.get_all_info():
            icon = {"closed": "✅", "open": "🔴", "half_open": "⚠️"}.get(info["state"], "❓")
            lines.append(
                f"  {icon} {info['key']}: {info['state']} "
                f"(失败 {info['failure_count']}/{info['threshold']}, "
                f"总成功率 {info['success_rate']}%)"
                + (f" 冷却剩余 {info['cooldown_remaining_s']}s" if info['state'] == 'open' else "")
            )
        return "\n".join(lines)
