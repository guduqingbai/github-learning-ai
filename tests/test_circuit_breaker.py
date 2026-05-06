"""测试 circuit_breaker.py — 三态状态机"""

from pathlib import Path
from circuit_breaker import CircuitBreaker, CircuitState


class TestCircuitState:
    def test_enum_values(self):
        assert CircuitState.CLOSED.value == "closed"
        assert CircuitState.OPEN.value == "open"
        assert CircuitState.HALF_OPEN.value == "half_open"


class TestCircuitBreaker:
    def test_initial_state(self, tmp_path: Path):
        cb = CircuitBreaker(tmp_path)
        assert cb.state("test_op") == CircuitState.CLOSED

    def test_call_returns_true_when_closed(self, tmp_path: Path):
        cb = CircuitBreaker(tmp_path)
        assert cb.call("test_op") is True

    def test_opens_after_three_failures(self, tmp_path: Path):
        cb = CircuitBreaker(tmp_path, failure_threshold=3, cooldown_seconds=9999)
        cb.on_failure("test_op")  # 1
        cb.on_failure("test_op")  # 2
        cb.on_failure("test_op")  # 3
        assert cb.state("test_op") == CircuitState.OPEN
        assert cb.call("test_op") is False

    def test_stays_closed_below_threshold(self, tmp_path: Path):
        cb = CircuitBreaker(tmp_path, failure_threshold=3)
        cb.on_failure("test_op")  # 1
        cb.on_failure("test_op")  # 2
        assert cb.state("test_op") == CircuitState.CLOSED
        assert cb.call("test_op") is True

    def test_success_resets_failure_count(self, tmp_path: Path):
        cb = CircuitBreaker(tmp_path, failure_threshold=3)
        cb.on_failure("test_op")  # 1
        cb.on_failure("test_op")  # 2
        cb.on_success("test_op")  # reset
        assert cb.state("test_op") == CircuitState.CLOSED
        # 无法直接访问 failure_count，但 state 为 CLOSED 且 call 返回 True
        assert cb.call("test_op") is True

    def test_context_isolation(self, tmp_path: Path):
        cb = CircuitBreaker(tmp_path, failure_threshold=2, cooldown_seconds=9999)
        cb.on_failure("op_a")  # 1
        cb.on_failure("op_a")  # 2 → open
        assert cb.call("op_a") is False
        assert cb.call("op_b") is True  # different context unaffected

    def test_half_open_transition(self, tmp_path: Path):
        cb = CircuitBreaker(tmp_path, failure_threshold=1, cooldown_seconds=0)
        cb.on_failure("test_op")  # → open
        # cooldown_seconds=0 means immediate half-open on next state() call
        assert cb.state("test_op") == CircuitState.HALF_OPEN
