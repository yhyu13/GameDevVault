"""L1 门禁与 L3 执行共用设施（pilot/physics 验证器）。

- BASE_DIR: pilot/base（fvector_stub 所在）
- load_module_from_path: 从任意路径加载解文件为独立模块
- l1_gate: 导入后 API 表面检查（函数存在、签名参数名与顺序、禁用模式扫描）
- smoke_call: 与 hidden tests 独立的最小输入，做返回类型表面检查
- L1 输出 (ok, reasons)：reasons 非空即 L1 FAIL
"""
import importlib.util
import inspect
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2] / "base"
KINDA_SMALL_NUMBER = 1e-4

# 确定性守卫：物理核不允许随机源/IO/动态执行（保证验证可复现、无 flakiness 来源）
BANNED_PATTERNS = [
    "import random", "import os", "import sys", "import numpy",
    "import io", "open(", "input(", "eval(", "exec(",
]


def load_module_from_path(name, path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def l1_gate(source, module, spec):
    """L1 门禁：API 表面检查。返回 (ok, reasons)。"""
    reasons = []
    for pat in BANNED_PATTERNS:
        if pat in source:
            reasons.append(f"禁用模式 '{pat}'")

    fn = getattr(module, spec["fn"], None)
    if not callable(fn):
        reasons.append(f"缺少可调用函数 {spec['fn']}")
        return False, reasons

    try:
        params = list(inspect.signature(fn).parameters)
    except (TypeError, ValueError):
        reasons.append("无法解析函数签名")
        return False, reasons
    if params != spec["params"]:
        reasons.append(f"签名不匹配：期望参数 {spec['params']}，实际 {params}")

    return (not reasons), reasons


def smoke_call(fn, spec):
    """L1 返回类型表面检查（输入与 hidden tests 无交集）。返回 (ok, why)。"""
    out = fn(*spec["smoke"]["args"])
    kind = spec["smoke"]["returns"]
    if kind == "vector_pair":
        ok = (
            isinstance(out, tuple) and len(out) == 2
            and all(hasattr(v, "x") and hasattr(v, "y") and hasattr(v, "z") for v in out)
        )
        return ok, "" if ok else "返回类型不是 (FVector, FVector)"
    if kind == "float_pair":
        ok = (
            isinstance(out, tuple) and len(out) == 2
            and all(isinstance(v, (int, float)) for v in out)
        )
        return ok, "" if ok else "返回类型不是 (float, float)"
    if kind == "float":
        ok = isinstance(out, (int, float))
        return ok, "" if ok else f"返回类型不是 float：{type(out).__name__}"
    return False, f"未知的返回类型规格 {kind}"
