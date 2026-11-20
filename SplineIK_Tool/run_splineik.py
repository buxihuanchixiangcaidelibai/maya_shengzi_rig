# -*- coding: utf-8 -*-
"""
SplineIK 曲线骨骼插件（独立版）一键启动脚本

可直接拖入 Maya 脚本编辑器执行，或绑定到 Shelf：
    execfile(r"C:\\ZY\\AAAGongzuo\\CJ\\Mking_Tool\\scripts\\SplineIK_Tool\\run_splineik.py")

若需要在任意 Maya 版本运行，请按需修改下面的 TOOL_DIR。
"""
import os as _os
import sys as _sys

# 正常导入时以本文件所在目录为准；execfile 下 __file__ 可能缺失，使用备用路径
try:
    _TOOL_DIR = _os.path.dirname(_os.path.abspath(__file__))
except NameError:
    _TOOL_DIR = r"C:\ZY\AAAGongzuo\CJ\Mking_Tool\scripts\SplineIK_Tool"

if _TOOL_DIR in _sys.path:
    _sys.path.remove(_TOOL_DIR)
_sys.path.insert(0, _TOOL_DIR)

try:
    reload
except NameError:
    import builtins as _builtins
    from importlib import reload as _reload
    _builtins.reload = _reload

# 确保始终使用本独立目录内的副本，而不是 Mking_Tool 已加载的同名模块
for _name in ("kxj_ik_dy305", "kxj_ik_UI_14"):
    _sys.modules.pop(_name, None)

import kxj_ik_UI_14 as _ui
reload(_ui)
_ui.ik_UI()
