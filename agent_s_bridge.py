"""
🤖 Agent-S 桥接模块 — 让自我思考系统能动手操作电脑
包装 simular-ai/Agent-S，提供简单的任务执行接口
"""

import io
import logging
import os
import platform
import time
from typing import Dict, Any, Optional

logger = logging.getLogger("agent_s_bridge")


class AgentSBridge:
    """Agent-S 桥接器：初始化 → 执行任务 → 返回结果"""

    def __init__(self, engine_params: Optional[Dict] = None, use_ollama: bool = False):
        """__init__"""
        self._agent = None
        self._grounding_agent = None
        self._ui_element = None
        self._use_ollama = use_ollama
        if use_ollama:
            os.environ.setdefault("OPENAI_API_KEY", "ollama")
            os.environ.setdefault("OPENAI_BASE_URL", "http://localhost:11434/v1")
            self._engine_params = engine_params or {
                "engine_type": "openai",
                "model": "qwen3:8b",
            }
        else:
            self._engine_params = engine_params or {
                "engine_type": "openai",
                "model": "gpt-4o",
            }
        self._platform = self._detect_platform()
        self._initialized = False

    def _detect_platform(self) -> str:
        """_detect_platform"""
        system = platform.system()
        if system == "Windows":
            return "windows"
        elif system == "Darwin":
            return "macos"
        elif system == "Linux":
            return "ubuntu"
        return "windows"

    def initialize(self) -> bool:
        """初始化 Agent-S（延迟初始化）"""
        if self._initialized:
            return True

        try:
            if self._platform == "windows":
                from gui_agents.aci.WindowsOSACI import WindowsACI, UIElement
                self._grounding_agent = WindowsACI()
            elif self._platform == "macos":
                from gui_agents.aci.MacOSACI import MacOSACI, UIElement
                self._grounding_agent = MacOSACI()
            else:
                from gui_agents.aci.LinuxOSACI import LinuxACI, UIElement
                self._grounding_agent = LinuxACI()
            self._ui_element = UIElement

            from gui_agents.core.AgentS import GraphSearchAgent

            self._agent = GraphSearchAgent(
                engine_params=self._engine_params,
                grounding_agent=self._grounding_agent,
                platform=self._platform,
                action_space="pyautogui",
                observation_type="a11y_tree" if self._use_ollama else "mixed",
            )
            self._initialized = True
            logger.info(f"Agent-S 初始化完成 (platform={self._platform})")
            return True
        except Exception as e:
            logger.error(f"Agent-S 初始化失败: {e}")
            return False

    @property
    def is_ready(self) -> bool:
        """is_ready"""
        return self._initialized and self._agent is not None

    def _capture_observation(self) -> Dict:
        """捕获当前屏幕状态 — 匹配 Agent-S 官方格式"""
        import pyautogui

        screenshot = pyautogui.screenshot()
        buf = io.BytesIO()
        screenshot.save(buf, format="PNG")

        obs = {
            "accessibility_tree": self._ui_element.systemWideElement(),
        }

        # 纯文本模型不传截图（否则 base64 编码会撑爆 prompt）
        if not self._use_ollama:
            obs["screenshot"] = buf.getvalue()

        return obs

    def execute(self, instruction: str, max_steps: int = 10) -> Dict[str, Any]:
        """执行一条电脑操作指令（多步循环直到完成）"""
        if not self._initialized:
            ok = self.initialize()
            if not ok:
                return {"success": False, "error": "Agent-S 初始化失败"}

        traj = "Task:\n" + instruction
        subtask_traj = ""
        all_results = []

        try:
            for step in range(max_steps):
                obs = self._capture_observation()

                info, code = self._agent.predict(
                    instruction=instruction,
                    observation=obs,
                )

                action_str = code[0] if code else ""
                logger.info(f"步骤 {step + 1}: {action_str[:100]}")

                if "done" in action_str.lower() or "fail" in action_str.lower():
                    self._agent.update_narrative_memory(traj)
                    result = {
                        "step": step + 1,
                        "action": action_str,
                        "status": "completed" if "done" in action_str.lower() else "failed",
                    }
                    all_results.append(result)
                    break

                if "next" in action_str.lower():
                    all_results.append({"step": step + 1, "action": "next", "status": "skip"})
                    continue

                if "wait" in action_str.lower():
                    time.sleep(3)
                    all_results.append({"step": step + 1, "action": "wait", "status": "wait"})
                    continue

                # 执行 Agent-S 生成的 Python 代码
                try:
                    exec(action_str)
                    result = {"step": step + 1, "action": action_str, "status": "executed"}
                except Exception as e:
                    result = {"step": step + 1, "action": action_str, "status": "error", "error": str(e)}

                all_results.append(result)

                traj += (
                    "\n\nReflection:\n"
                    + str(info.get("reflection", ""))
                    + "\n\n----------------------\n\nPlan:\n"
                    + info.get("executor_plan", "")
                )
                subtask_traj = self._agent.update_episodic_memory(info, subtask_traj)

                time.sleep(1.0)

            return {
                "success": True,
                "instruction": instruction,
                "steps_taken": len(all_results),
                "details": all_results,
                "agent_info": info,
            }
        except Exception as e:
            logger.error(f"Agent-S 执行失败: {e}")
            return {"success": False, "error": str(e)}

    def close(self):
        """清理资源"""
        self._initialized = False
        self._agent = None
        self._grounding_agent = None
        self._ui_element = None
