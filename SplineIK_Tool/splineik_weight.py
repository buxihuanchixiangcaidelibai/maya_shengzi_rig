# coding: utf-8
"""
SplineIK 独立工具 —— 曲线权重平滑模块

对 spline 驱动曲线（*_drv_crv）上的 skinCluster 蒙皮权重做邻域平滑：
  1) 一键平滑整条曲线的所有 CV 权重
  2) 只平滑在视窗中选中的 CV 的权重

不依赖 Mking_Tool，仅使用 maya.cmds。
"""
import maya.cmds as mc

_UI = {}


# ---------------------------------------------------------------- 基础查询
def curve_shape(curve):
    """取曲线 transform 下的 nurbsCurve shape（跳过 intermediate）"""
    if not curve:
        return None
    if mc.nodeType(curve) == 'nurbsCurve':
        return curve
    shapes = mc.listRelatives(curve, s=True, ni=True, f=True) or []
    for shape in shapes:
        if mc.nodeType(shape) == 'nurbsCurve':
            return shape
    return None


def skin_of(shape):
    """取 shape 上的 skinCluster"""
    if not shape:
        return None
    found = mc.listConnections(shape, type='skinCluster') or []
    return found[0] if found else None


def list_skinned_curves():
    """列出场景中所有带蒙皮权重的曲线，返回 [(transform, skinCluster)]"""
    result = []
    seen = set()
    for shape in (mc.ls(type='nurbsCurve', long=True) or []):
        try:
            if mc.getAttr(shape + '.intermediateObject'):
                continue
        except Exception:
            continue
        skin = skin_of(shape)
        if not skin:
            continue
        parents = mc.listRelatives(shape, p=True, f=True) or []
        transform = parents[0] if parents else shape
        if transform in seen:
            continue
        seen.add(transform)
        result.append((transform, skin))
    return result


def _transform_from_component(component):
    """从组件路径解析所属 transform（ls 返回的是 transform.cv[N]）"""
    prefix = component.split('.', 1)[0]
    if mc.nodeType(prefix) == 'transform':
        return prefix
    parents = mc.listRelatives(prefix, p=True, f=True) or []
    return parents[0] if parents else prefix


def selected_cvs():
    """解析视窗中选择的 CV，返回 {transform: [cv索引]}"""
    result = {}
    for item in (mc.ls(sl=True, fl=True, long=True) or []):
        if '.cv[' not in item:
            continue
        try:
            comp = item.split('.', 1)[1]
            index = int(comp[comp.index('[') + 1:comp.index(']')])
        except (ValueError, IndexError):
            continue
        transform = _transform_from_component(item)
        result.setdefault(transform, []).append(index)
    return result


# ---------------------------------------------------------------- 核心算法
def smooth_weights(curve, indices=None, iterations=3, strength=0.5):
    """
    平滑曲线蒙皮权重。

    curve      : 曲线 transform / shape
    indices    : 要平滑的 CV 索引列表；None 表示整条曲线
    iterations : 迭代次数
    strength   : 每次迭代向邻居均值靠拢的比例 0~1
    返回 True/False
    """
    shape = curve_shape(curve)
    skin = skin_of(shape)
    if not skin:
        return False

    influences = mc.skinCluster(skin, q=True, influence=True) or []
    cvs = mc.ls(shape + '.cv[*]', fl=True) or []
    count = len(cvs)
    if not influences or count < 2:
        return False

    if indices is None:
        targets = list(range(count))
    else:
        size = count
        targets = sorted(set(int(i) for i in indices if 0 <= int(i) < size))
    if not targets:
        return False

    strength = max(0.0, min(1.0, float(strength)))
    iterations = max(1, int(iterations))

    try:
        closed = mc.getAttr(shape + '.form') in (1, 2)
    except Exception:
        closed = False

    weights = []
    for cv in cvs:
        try:
            values = mc.skinPercent(skin, cv, q=True, v=True) or []
        except Exception:
            return False
        values = [float(v) for v in values]
        if len(values) != len(influences):
            return False
        weights.append(values)

    for _ in range(iterations):
        updated = [list(w) for w in weights]
        for i in targets:
            if closed:
                left, right = (i - 1) % count, (i + 1) % count
            else:
                left, right = max(0, i - 1), min(count - 1, i + 1)
            neighbours = [weights[left]] if left == right else [weights[left], weights[right]]
            average = [sum(x) / float(len(neighbours)) for x in zip(*neighbours)]
            current = weights[i]
            merged = [current[k] * (1.0 - strength) + average[k] * strength
                      for k in range(len(current))]
            total = sum(merged)
            if total <= 0:
                merged = [1.0 / len(merged)] * len(merged)
            else:
                merged = [x / total for x in merged]
            updated[i] = merged
        weights = updated

    mc.undoInfo(openChunk=True)
    try:
        for i in targets:
            pairs = [(influences[k], weights[i][k]) for k in range(len(influences))]
            mc.skinPercent(skin, cvs[i], transformValue=pairs, normalize=1)
    finally:
        mc.undoInfo(closeChunk=True)
    return True


def linearize_weights(curve):
    """把整条曲线的权重按 CV 位置线性重排（首尾 1 -> 0，中间平滑过渡）"""
    shape = curve_shape(curve)
    skin = skin_of(shape)
    if not skin:
        return False
    influences = mc.skinCluster(skin, q=True, influence=True) or []
    cvs = mc.ls(shape + '.cv[*]', fl=True) or []
    count = len(cvs)
    total = len(influences)
    if not total or count < 2:
        return False

    mc.undoInfo(openChunk=True)
    try:
        for i, cv in enumerate(cvs):
            position = i / float(count - 1) * (total - 1)
            base = min(int(position), total - 1)
            frac = position - base
            pairs = [(influences[k], 0.0) for k in range(total)]
            if base >= total - 1:
                pairs[total - 1] = (influences[total - 1], 1.0)
            else:
                pairs[base] = (influences[base], 1.0 - frac)
                pairs[base + 1] = (influences[base + 1], frac)
            mc.skinPercent(skin, cv, transformValue=pairs, normalize=1)
    finally:
        mc.undoInfo(closeChunk=True)
    return True


# ---------------------------------------------------------------- UI 辅助
def _set_info(text):
    field = _UI.get('info')
    if field:
        mc.text(field, e=True, l=text)


def _error(text):
    window = mc.window(title=u'提示', wh=(240, 80))
    mc.columnLayout(adjustableColumn=True)
    mc.text(l=text, h=42, align='center')
    mc.button(l=u'确定', h=26, c=lambda *args: mc.deleteUI(window))
    mc.showWindow(window)


def _params():
    iteration = 3
    strength = 0.5
    if _UI.get('iter'):
        iteration = int(mc.intSliderGrp(_UI['iter'], q=True, v=True))
    if _UI.get('strength'):
        strength = float(mc.floatSliderGrp(_UI['strength'], q=True, v=True))
    return iteration, strength


def refresh_list(*args):
    """刷新带蒙皮权重的曲线列表"""
    field = _UI.get('list')
    if not field:
        return
    mc.textScrollList(field, e=True, ra=True)
    curves = list_skinned_curves()
    _UI['curves'] = curves
    mc.textScrollList(field, e=True, a=[c.split('|')[-1] for c, s in curves])
    _set_info(u'找到 %d 条带蒙皮权重的曲线' % len(curves))


def _pick_curve(silent=False):
    """优先取列表选中项，其次取视窗选中的曲线/CV 所属曲线"""
    field = _UI.get('list')
    if field:
        selected = mc.textScrollList(field, q=True, si=True) or []
        curves = _UI.get('curves', [])
        if selected:
            wanted = selected[0].split('|')[-1]
            for curve, skin in curves:
                if curve.split('|')[-1] == wanted:
                    return curve
    for item in (mc.ls(sl=True, long=True) or []):
        candidate = _transform_from_component(item) if '.cv[' in item else item
        if skin_of(curve_shape(candidate)):
            return candidate
    if not silent:
        _error(u'请先在列表中选择曲线，或在视窗中选中曲线 / 曲线上的点')
    return None


def smooth_all(*args):
    """一键平滑整条曲线的全部权重"""
    curve = _pick_curve()
    if not curve:
        return
    iteration, strength = _params()
    if smooth_weights(curve, None, iteration, strength):
        _set_info(u'已平滑整条曲线：%s（%d 次，强度 %.2f）'
                  % (curve.split('|')[-1], iteration, strength))
    else:
        _error(u'该曲线没有可用的蒙皮权重')


def smooth_selected(*args):
    """只平滑视窗中选中 CV 的权重"""
    picked = _pick_curve(silent=True)
    groups = selected_cvs()
    if picked and picked in groups:
        groups = {picked: groups[picked]}
    if not groups:
        _error(u'请先在视窗中选择曲线上的点（CV）')
        return
    iteration, strength = _params()
    done = 0
    for curve, indices in groups.items():
        if smooth_weights(curve, indices, iteration, strength):
            done += 1
    if done:
        _set_info(u'已平滑 %d 条曲线上选中的点（%d 次，强度 %.2f）'
                  % (done, iteration, strength))
    else:
        _error(u'所选点所属曲线没有可用的蒙皮权重')


def linearize(*args):
    """按位置重排整条曲线的权重"""
    curve = _pick_curve()
    if not curve:
        return
    if linearize_weights(curve):
        _set_info(u'已线性化权重：%s' % curve.split('|')[-1])
    else:
        _error(u'该曲线没有可用的蒙皮权重')


def build_weight_ui():
    """在当前父布局下构建权重页内容"""
    mc.text(l=u'曲线权重平滑  ·  spline 驱动曲线', h=26, fn='boldLabelFont')
    mc.separator(style='in', h=6)
    mc.text(l=u'1. 选择曲线（列表或视窗）', h=22)
    _UI['list'] = mc.textScrollList(numberOfRows=7, allowMultiSelection=False,
                                    sc=lambda *args: None)
    mc.button(l=u'刷新曲线列表', h=24, c=refresh_list)
    mc.separator(style='in', h=6)
    mc.text(l=u'2. 平滑参数', h=22)
    _UI['iter'] = mc.intSliderGrp(label=u'平滑次数', field=True,
                                  min=1, max=20, fmn=1, fmx=100, v=3,
                                  cw3=[70, 40, 150])
    _UI['strength'] = mc.floatSliderGrp(label=u'平滑强度', field=True,
                                        min=0.0, max=1.0, fmn=0.0, fmx=1.0,
                                        pre=2, v=0.5, cw3=[70, 40, 150])
    mc.separator(style='in', h=6)
    mc.text(l=u'3. 执行', h=22)
    mc.button(l=u'一键平滑整条曲线权重', h=28, c=smooth_all)
    mc.button(l=u'平滑所选点的权重', h=28, c=smooth_selected)
    mc.button(l=u'按位置重排权重（线性化）', h=24, c=linearize)
    mc.separator(style='in', h=6)
    _UI['info'] = mc.text(l=u'就绪', h=40, align='left', w=300)
    refresh_list()
