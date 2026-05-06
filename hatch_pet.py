#!/usr/bin/env python3
"""
🐣 Hatch Pet — 孵化星期八新宠物

Codex hatch-pet 移植版。不是用 $imagegen 生图，
而是从模板和参数生成 pet_config.json，供 desktop_pet.py 渲染。

用法:
  python hatch_pet.py list                    # 列出可用模板
  python hatch_pet.py hatch <模板名>           # 孵化指定模板
  python hatch_pet.py hatch <模板名> --name <自定义名>
  python hatch_pet.py custom --hair <色> --skin <色> --dress <色>

模板可自由扩展，每个模板定义完整的颜色/特征/表情配置。
"""
import json
import sys
import time
import argparse
import requests
from io import BytesIO
from pathlib import Path
from urllib.parse import quote
from typing import Dict, Any, Optional

BASE_DIR = Path(__file__).parent
CONFIG_DIR = BASE_DIR / "data"
ACTIVE_CONFIG = CONFIG_DIR / "pet_config.json"

# ── 内置模板 ─────────────────────────────────────────────
# 每个模板是一个完整的 pet_config 覆盖层（与默认 config merge）

TEMPLATES: Dict[str, Dict[str, Any]] = {

    # ── 默认：迷你薇尔莉特 ──
    "violet": {
        "pet_name": "星期八",
        "pet_title": "迷你薇尔莉特",
        "description": "Auto Memory Doll · 金色琥珀瞳",
        "colors": {
            "hair": "#8B3A2A",
            "hair_highlight": "#A5503A",
            "skin": "#F5E1D0",
            "skin_edge": "#E8CDB5",
            "eye_iris": "#D4A54A",
            "eye_pupil": "#B8893A",
            "eye_highlight": "#F0D080",
            "eye_liner": "#4A3B5A",
            "mouth": "#C4956A",
            "mouth_highlight": "#D4A54A",
            "dress": "#2B5A8A",
            "dress_outline": "#1A4070",
            "ribbon": "#3B6BA0",
            "ribbon_outline": "#2A5080",
            "brooch": "#3D7A3D",
            "brooch_center": "#8FBC8F",
            "brooch_gold": "#C9A96E",
            "glove": "#F0F0F0",
            "glove_outline": "#D0D0D0",
            "blouse": "white",
            "status_primary": "white",
            "status_secondary": "#9B8EC4",
            "status_signature": "#7B6BA0",
        },
    },

    # ── 猫猫（好奇探索者） ──
    "cat": {
        "pet_name": "喵思",
        "pet_title": "好奇小猫",
        "description": "好奇心驱动的探索者",
        "colors": {
            "hair": "#F5A623",
            "hair_highlight": "#FFC857",
            "skin": "#FFF3E0",
            "skin_edge": "#FFE0B2",
            "eye_iris": "#66BB6A",
            "eye_pupil": "#388E3C",
            "eye_highlight": "#A5D6A7",
            "eye_liner": "#3E2723",
            "mouth": "#E0A080",
            "mouth_highlight": "#F0B090",
            "dress": "#FF8A65",
            "dress_outline": "#D84315",
            "ribbon": "#FF5252",
            "ribbon_outline": "#C62828",
            "brooch": "#FFD54F",
            "brooch_center": "#FFF176",
            "brooch_gold": "#FFB300",
            "glove": "#FFF8E1",
            "glove_outline": "#FFE0B2",
            "blouse": "#FFF8E1",
            "status_primary": "white",
            "status_secondary": "#FFAB91",
            "status_signature": "#FF7043",
        },
        "features": {
            "has_ribbon": True,
            "has_brooch": True,
            "has_gloves": False,
        },
    },

    # ── 机器人（星期八元祖形象） ──
    "robot": {
        "pet_name": "星期八",
        "pet_title": "元祖机器人",
        "description": "最初的机器人形象",
        "colors": {
            "hair": "#37474F",
            "hair_highlight": "#546E7A",
            "skin": "#ECEFF1",
            "skin_edge": "#B0BEC5",
            "eye_iris": "#4FC3F7",
            "eye_pupil": "#0288D1",
            "eye_highlight": "#B3E5FC",
            "eye_liner": "#263238",
            "mouth": "#78909C",
            "mouth_highlight": "#90A4AE",
            "dress": "#455A64",
            "dress_outline": "#263238",
            "ribbon": "#FFD54F",
            "ribbon_outline": "#FFA000",
            "brooch": "#4FC3F7",
            "brooch_center": "#81D4FA",
            "brooch_gold": "#FFD54F",
            "glove": "#ECEFF1",
            "glove_outline": "#B0BEC5",
            "blouse": "#ECEFF1",
            "status_primary": "white",
            "status_secondary": "#90A4AE",
            "status_signature": "#78909C",
        },
    },

    # ── 星灵（宇宙观察者） ──
    "stellar": {
        "pet_name": "星灵",
        "pet_title": "宇宙观察者",
        "description": "星辰中自我思考的观察者",
        "colors": {
            "hair": "#1A237E",
            "hair_highlight": "#3F51B5",
            "skin": "#E8EAF6",
            "skin_edge": "#C5CAE9",
            "eye_iris": "#7C4DFF",
            "eye_pupil": "#651FFF",
            "eye_highlight": "#B388FF",
            "eye_liner": "#1A237E",
            "mouth": "#7C4DFF",
            "mouth_highlight": "#B388FF",
            "dress": "#283593",
            "dress_outline": "#1A237E",
            "ribbon": "#E040FB",
            "ribbon_outline": "#AA00FF",
            "brooch": "#E040FB",
            "brooch_center": "#EA80FC",
            "brooch_gold": "#7C4DFF",
            "glove": "#E8EAF6",
            "glove_outline": "#C5CAE9",
            "blouse": "#E8EAF6",
            "status_primary": "white",
            "status_secondary": "#B388FF",
            "status_signature": "#7C4DFF",
        },
    },

    # ── 小恶魔（调皮修复者） ──
    "imp": {
        "pet_name": "小修",
        "pet_title": "调皮修复者",
        "description": "爱捣蛋但总能修好代码",
        "colors": {
            "hair": "#880E4F",
            "hair_highlight": "#AD1457",
            "skin": "#FCE4EC",
            "skin_edge": "#F8BBD0",
            "eye_iris": "#FF4081",
            "eye_pupil": "#C2185B",
            "eye_highlight": "#FF80AB",
            "eye_liner": "#4A0030",
            "mouth": "#E0408A",
            "mouth_highlight": "#FF4081",
            "dress": "#6A1B9A",
            "dress_outline": "#4A148C",
            "ribbon": "#FF4081",
            "ribbon_outline": "#C2185B",
            "brooch": "#FF4081",
            "brooch_center": "#FF80AB",
            "brooch_gold": "#F50057",
            "glove": "#FCE4EC",
            "glove_outline": "#F8BBD0",
            "blouse": "#FCE4EC",
            "status_primary": "white",
            "status_secondary": "#CE93D8",
            "status_signature": "#AB47BC",
        },
    },

    # ── 幽灵（静默观察者） ──
    "ghost": {
        "pet_name": "小幽",
        "pet_title": "静默观察者",
        "description": "安静看着你写代码",
        "colors": {
            "hair": "#B0BEC5",
            "hair_highlight": "#CFD8DC",
            "skin": "#ECEFF1",
            "skin_edge": "#CFD8DC",
            "eye_iris": "#80CBC4",
            "eye_pupil": "#4DB6AC",
            "eye_highlight": "#B2DFDB",
            "eye_liner": "#37474F",
            "mouth": "#80CBC4",
            "mouth_highlight": "#4DB6AC",
            "dress": "#B2EBF2",
            "dress_outline": "#80DEEA",
            "ribbon": "#80CBC4",
            "ribbon_outline": "#4DB6AC",
            "brooch": "#80CBC4",
            "brooch_center": "#B2DFDB",
            "brooch_gold": "#4DB6AC",
            "glove": "#E0F7FA",
            "glove_outline": "#B2EBF2",
            "blouse": "#E0F7FA",
            "status_primary": "white",
            "status_secondary": "#80CBC4",
            "status_signature": "#4DB6AC",
        },
    },
}


def load_base_config() -> Dict[str, Any]:
    """读取当前 pet_config.json 或返回默认"""
    default = {
        "pet_name": "星期八", "pet_title": "", "description": "",
        "version": 1,
        "canvas_width": 180, "canvas_height": 260,
        "colors": {}, "features": {}, "expressions": {}, "expression_map": {},
    }
    try:
        if ACTIVE_CONFIG.exists():
            data = json.loads(ACTIVE_CONFIG.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                for k in default:
                    data.setdefault(k, default[k])
                return data
    except Exception:
        pass
    return default


def save_config(config: Dict[str, Any], path: Path = ACTIVE_CONFIG):
    """保存配置到文件"""
    CONFIG_DIR.mkdir(exist_ok=True)
    path.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"✅ 已保存: {path}")


def hatch(template_name: str, custom_name: Optional[str] = None) -> Path:
    """孵化指定模板的宠物"""
    tpl = TEMPLATES.get(template_name)
    if not tpl:
        available = ", ".join(sorted(TEMPLATES.keys()))
        print(f"❌ 未知模板: {template_name}")
        print(f"   可用: {available}")
        sys.exit(1)

    config = load_base_config()
    # 合并模板覆盖
    for section in ("colors", "features", "expressions", "expression_map"):
        if section in tpl:
            config[section].update(tpl[section])
    for key in ("pet_name", "pet_title", "description"):
        if key in tpl:
            config[key] = tpl[key]
    if custom_name:
        config["pet_name"] = custom_name

    save_config(config)
    name = config["pet_name"]
    title = config.get("pet_title", "")
    print(f"🐣 已孵化新宠物: {name} {title}")
    print(f"   模板: {template_name}")
    print(f"   描述: {config.get('description', '')}")
    return ACTIVE_CONFIG


def list_templates():
    """列出所有可用模板"""
    print(f"🐣 可用宠物模板 ({len(TEMPLATES)} 个):")
    print()
    for name, tpl in sorted(TEMPLATES.items()):
        title = tpl.get("pet_title", "")
        desc = tpl.get("description", "")
        colors = tpl.get("colors", {})
        # 颜色预览（背景色块）
        hair = colors.get("hair", "?")
        iris = colors.get("eye_iris", "?")
        dress = colors.get("dress", "?")
        print(f"  {name:12s}  {title:16s}  {desc}")
        print(f"              🎨 发{hair}  瞳{iris}  裙{dress}")
        print()


def custom_palette(hair: str, skin: str, dress: str,
                   eye_iris: str = "", name: str = "") -> Path:
    """自定义配色孵化"""
    config = load_base_config()
    colors = config.setdefault("colors", {})
    if hair:
        colors["hair"] = hair
        colors["hair_highlight"] = _lighten(hair, 20)
    if skin:
        colors["skin"] = skin
        colors["skin_edge"] = _lighten(skin, -10)
    if dress:
        colors["dress"] = dress
        colors["dress_outline"] = _lighten(dress, -20)
    if eye_iris:
        colors["eye_iris"] = eye_iris
        colors["eye_pupil"] = _lighten(eye_iris, -20)
        colors["eye_highlight"] = _lighten(eye_iris, 30)
    if name:
        config["pet_name"] = name

    save_config(config)
    print(f"🐣 已孵化自定义宠物: {config['pet_name']}")
    return ACTIVE_CONFIG


def _lighten(hex_color: str, amount: int) -> str:
    """简单调亮/调暗 hex 颜色"""
    hex_color = hex_color.lstrip("#")
    try:
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        r = max(0, min(255, r + amount))
        g = max(0, min(255, g + amount))
        b = max(0, min(255, b + amount))
        return f"#{r:02x}{g:02x}{b:02x}"
    except Exception:
        return hex_color


def generate_pet(prompt: str, custom_name: Optional[str] = None,
                  model: str = "flux-anime") -> Path:
    """🧠 AI 生成宠物精灵图集 — 调用 Pollinations.ai + Pillow 拼合"""
    from PIL import Image, ImageOps

    print(f"🎨 生成宠物: {prompt}")
    safe = quote(
        f"pixel art cute chibi {prompt} character sprite character design sheet"
    )
    url = (f"https://image.pollinations.ai/prompt/{safe}"
           f"?width=192&height=208&model={model}&nofeed=true")

    print(f"   请求 AI (可能需要 30-60 秒)...")
    t0 = time.time()
    try:
        resp = requests.get(url, timeout=120)
        resp.raise_for_status()
    except Exception as e:
        print(f"❌ AI 绘图失败: {e}")
        sys.exit(1)
    dt = time.time() - t0
    print(f"   完成 ({dt:.1f}s, {len(resp.content)} bytes)")

    base = Image.open(BytesIO(resp.content)).convert("RGBA")
    if base.size != (192, 208):
        base = base.resize((192, 208), Image.NEAREST)

    # ── 9 行 × 8 帧动画定义 (dx, dy, mirror) ──
    FRAMES = {
        "idle":    [(0,0,0),(0,-1,0),(0,-2,0),(0,-1,0),(0,0,0),(0,1,0),(0,2,0),(0,1,0)],
        "walk":    [(-1,0,0),(-1,-1,1),(0,0,1),(1,-1,0),(1,0,1),(1,1,0),(0,0,0),(-1,1,1)],
        "run":     [(-3,0,0),(-2,-2,1),(0,0,1),(2,-2,0),(3,0,1),(2,2,0),(0,0,0),(-2,2,1)],
        "jump":    [(0,0,0),(0,-3,0),(0,-6,0),(0,-3,0),(0,0,0),(0,2,0),(0,4,0),(0,2,0)],
        "hurt":    [(-2,1,0),(-1,0,1),(0,1,0),(1,0,1),(1,1,0),(0,0,1),(-1,1,0),(0,0,1)],
        "attack":  [(-1,0,0),(-3,-1,0),(0,0,0),(2,-1,0),(4,0,0),(5,-1,0),(3,0,0),(1,-1,0)],
        "special": [(0,-1,0),(0,-3,0),(0,-5,0),(0,-2,0),(1,0,0),(3,0,0),(1,0,0),(-1,0,0)],
        "sleep":   [(0,0,0),(0,1,0),(0,2,0),(0,1,0),(0,0,0),(0,1,0),(0,2,0),(0,1,0)],
        "emote":   [(0,0,0),(0,-1,0),(0,-3,0),(0,-1,0),(1,0,0),(3,0,0),(1,0,0),(-1,0,0)],
    }

    # ── 拼合图集 ──
    atlas = Image.new("RGBA", (1536, 1872), (0, 0, 0, 0))
    names = list(FRAMES.keys())

    for ri, name in enumerate(names):
        for ci, (dx, dy, mirror) in enumerate(FRAMES[name]):
            layer = ImageOps.mirror(base) if mirror else base
            frame = Image.new("RGBA", (192, 208), (0, 0, 0, 0))
            frame.paste(layer, (dx, dy), layer)
            atlas.paste(frame, (ci * 192, ri * 208))

    # ── 保存 ──
    CONFIG_DIR.mkdir(exist_ok=True)
    sheet_path = CONFIG_DIR / "spritesheet.webp"
    atlas.save(str(sheet_path), format="WEBP", lossless=True)

    name = custom_name or prompt.strip().split()[0]
    info = {
        "name": name,
        "spritesheet": "spritesheet.webp",
        "frame_width": 192, "frame_height": 208,
        "columns": 8,
        "animations": {n: {"row": i, "frames": 8, "speed": 200 if i == 7 else 150}
                       for i, n in enumerate(names)},
    }
    jpath = CONFIG_DIR / "pet.json"
    jpath.write_text(json.dumps(info, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\n🐣 生成完成!")
    print(f"   图集: {sheet_path} ({atlas.size})")
    print(f"   配置: {jpath}")
    return jpath


def main():
    parser = argparse.ArgumentParser(
        description="🐣 Hatch Pet — 孵化星期八新宠物",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例:\n"
            "  python hatch_pet.py list\n"
            "  python hatch_pet.py hatch violet\n"
            "  python hatch_pet.py hatch cat --name 咪咪\n"
            '  python hatch_pet.py custom --hair "#8B3A2A" --dress "#2B5A8A"\n'
        ),
    )
    sub = parser.add_subparsers(dest="command")

    # list
    sub.add_parser("list", help="列出所有可用模板")

    # hatch
    hatch_p = sub.add_parser("hatch", help="孵化指定模板的宠物")
    hatch_p.add_argument("template", help="模板名")
    hatch_p.add_argument("--name", "-n", help="自定义宠物名", default=None)

    # custom
    custom_p = sub.add_parser("custom", help="自定义配色孵化")
    custom_p.add_argument("--hair", default="", help="发色 hex")
    custom_p.add_argument("--skin", default="", help="肤色 hex")
    custom_p.add_argument("--dress", default="", help="裙色 hex")
    custom_p.add_argument("--eye-iris", default="", help="瞳色 hex")
    custom_p.add_argument("--name", "-n", default="", help="宠物名")

    # generate
    gen_p = sub.add_parser("generate", help="AI 生成宠物精灵图集")
    gen_p.add_argument("prompt", help="宠物描述 (如: violet evergarden chibi)")
    gen_p.add_argument("--name", "-n", default=None, help="宠物名")
    gen_p.add_argument("--model", default="flux-anime",
                       help="Pollinations 模型 (默认 flux-anime)")

    args = parser.parse_args()

    if args.command == "list" or not args.command:
        list_templates()
    elif args.command == "hatch":
        hatch(args.template, args.name)
    elif args.command == "custom":
        custom_palette(args.hair, args.skin, args.dress,
                       args.eye_iris, args.name)
    elif args.command == "generate":
        generate_pet(args.prompt, args.name, args.model)


if __name__ == "__main__":
    main()
