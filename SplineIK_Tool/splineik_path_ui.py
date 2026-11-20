# -*- coding: utf-8 -*-
"""路径页 UI 构建与参数读取，供 cp936 主 UI 以纯 ASCII 调用。"""
import maya.cmds as mc

_HANDLES = {}


def _toggle(enabled):
    mc.intSliderGrp(_HANDLES['count'], edit=True, enable=bool(enabled))


def build():
    mc.text(l=u'路径控制器 / Path Controls', h=22, fn='boldLabelFont')
    mc.text(l=u'沿起终点方向生成 10 倍长路径，Travel 驱动整条绳索', h=20)
    _HANDLES['check'] = mc.checkBox(l=u'启用路径控制器', v=0, cc=_toggle)
    _HANDLES['count'] = mc.intSliderGrp(label=u'路径控制器数量', field=True,
                                        min=4, max=100, fmn=4, fmx=200, v=50,
                                        enable=False, cw3=[90, 40, 130])
    return _HANDLES


def read():
    """返回 (是否启用, 数量)"""
    try:
        enabled = bool(mc.checkBox(_HANDLES['check'], q=1, v=1))
        count = int(mc.intSliderGrp(_HANDLES['count'], q=1, v=True))
    except Exception:
        return 0, 50
    return (1 if enabled else 0), count
