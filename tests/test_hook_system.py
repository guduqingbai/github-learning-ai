"""Test hook_system.py — 纯数据类，零依赖"""

from hook_system import HookEvent, Hook, ContentBlock, CycleMessage, build_cycle_messages


class TestHookEvent:
    def test_constants_are_strings(self):
        assert HookEvent.CYCLE_START == "cycle_start"
        assert HookEvent.CYCLE_END == "cycle_end"
        assert HookEvent.PRE_SCAN == "pre_scan"
        assert HookEvent.POST_SCAN == "post_scan"
        assert HookEvent.PRE_STUDY == "pre_study"
        assert HookEvent.POST_REFLECT == "post_reflect"

    def test_all_events_have_pre_and_post(self):
        events = {"scan", "study", "evaluate", "awareness",
                  "consolidate", "reflect", "questions", "explore"}
        for e in events:
            assert getattr(HookEvent, f"PRE_{e.upper()}") == f"pre_{e}"
            assert getattr(HookEvent, f"POST_{e.upper()}") == f"post_{e}"


class TestHook:
    def test_create_hook(self):
        def handler():
            pass
        h = Hook("test_event", handler, name="test_hook", priority=5)
        assert h.event == "test_event"
        assert h.handler is handler
        assert h.name == "test_hook"
        assert h.priority == 5

    def test_repr(self):
        h = Hook("scan", lambda: None, name="myscan")
        assert "Hook(" in repr(h)
        assert "myscan" in repr(h)

    def test_default_name_from_function(self):
        def my_handler():
            pass
        h = Hook("test", my_handler)
        assert h.name == "my_handler"


class TestContentBlock:
    def test_create(self):
        cb = ContentBlock(type="observation", data={"key": "val"})
        assert cb.type == "observation"
        assert cb.data == {"key": "val"}

    def test_default_data(self):
        cb = ContentBlock(type="test")
        assert cb.data == {}


class TestCycleMessage:
    def test_create(self):
        cb = ContentBlock(type="phase", data={"phase": "test"})
        msg = CycleMessage(role="system", blocks=[cb], timestamp="now")
        assert msg.role == "system"
        assert len(msg.blocks) == 1
        assert msg.blocks[0].type == "phase"

    def test_defaults(self):
        msg = CycleMessage(role="tool")
        assert msg.blocks == []
        assert msg.timestamp == ""


class TestBuildCycleMessages:
    def test_minimal(self):
        msgs = build_cycle_messages(phase="test")
        assert len(msgs) == 1
        assert msgs[0].role == "system"

    def test_with_scan_data(self):
        msgs = build_cycle_messages(phase="scan", scan_data={"files": 10})
        assert len(msgs) == 1
        assert msgs[0].blocks[1].type == "scan"

    def test_with_errors(self):
        msgs = build_cycle_messages(phase="test", errors=["err1"])
        assert len(msgs) == 2
        assert msgs[1].role == "tool"
        assert msgs[1].blocks[0].data["errors"] == ["err1"]
