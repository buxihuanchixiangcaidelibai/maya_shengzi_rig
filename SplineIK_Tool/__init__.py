# -*- coding: utf-8 -*-
"""
SplineIK 曲线骨骼插件（独立版）

从 Mking_Tool 中剥离，仅依赖 Maya 自带模块
（maya.cmds / maya.mel / maya.OpenMaya，point 模式额外用到 pymel.core）。

用法：在 Maya Python 脚本编辑器中执行
    import sys
    sys.path.append(r"C:\\ZY\\AAAGongzuo\\CJ\\Mking_Tool\\scripts")  # 本目录的父目录
    import SplineIK_Tool
    SplineIK_Tool.show()
"""
import os as _os
import sys as _sys

_TOOL_DIR = _os.path.dirname(_os.path.abspath(__file__))
if _TOOL_DIR in _sys.path:
    _sys.path.remove(_TOOL_DIR)
_sys.path.insert(0, _TOOL_DIR)

# 原插件使用 Python 2 内建 reload()，这里为 Python 3（Maya 2020+）补齐
try:
    reload
except NameError:
    import builtins as _builtins
    from importlib import reload as _reload
    _builtins.reload = _reload

__all__ = ["show", "main"]


def show():
    """打开 spline IK 插件界面"""
    if _TOOL_DIR in _sys.path:
        _sys.path.remove(_TOOL_DIR)
    _sys.path.insert(0, _TOOL_DIR)
    # 确保始终使用本独立目录内的副本，而不是 Mking_Tool 已加载的同名模块
    for _name in ("kxj_ik_dy305", "kxj_ik_UI_14"):
        _sys.modules.pop(_name, None)
    import kxj_ik_UI_14 as _ui
    reload(_ui)
    return _ui.ik_UI()


def main():
    show()
