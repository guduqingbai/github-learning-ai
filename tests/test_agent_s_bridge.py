"""测试 agent_s_bridge.py — 结构校验"""

from agent_s_bridge import AgentSBridge


class TestAgentSBridge:
    def test_import_and_create(self):
        bridge = AgentSBridge()
        assert bridge is not None
        assert bridge._engine_params is not None

    def test_detect_platform(self):
        bridge = AgentSBridge()
        platform = bridge._detect_platform()
        assert platform in ("windows", "macos", "ubuntu")

    def test_is_ready_false_before_init(self):
        bridge = AgentSBridge()
        assert bridge.is_ready is False

    def test_close_does_not_crash(self):
        bridge = AgentSBridge()
        bridge.close()
        assert bridge.is_ready is False
