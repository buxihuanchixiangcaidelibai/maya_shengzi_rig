# -*- coding: utf-8 -*-
"""Creation-mode policy and local-mode routing, without a simulation page."""
import maya.cmds as mc
import splineik_local as local


class ModeUI(object):
    def __init__(self, owner):
        self.owner = owner
        self.old_settings = None
        self.pending = None
        self.menu = mc.optionMenu(label=u'绑定类型', cc=self.changed)
        mc.menuItem(label=u'Spline IK')
        mc.menuItem(label=u'局部曲线（FK＋局部次级）')
        self.range = mc.optionMenu(label=u'局部影响范围')
        for text in (u'窄', u'标准', u'宽'):
            mc.menuItem(label=text)
        mc.optionMenu(self.range, e=True, sl=2)
        self.twist = mc.checkBox(label=u'局部扭转', v=True)
        self.mesh = mc.button(label=u'局部模式：绑定所选模型', c=self.bind_mesh,
                              ann=u'同时选择一个局部绳索控制器和未蒙皮模型；控制器需归零')
        self.info = mc.text(label=u'方盒 FK 链式联动；飞镖次级支持移动、旋转和缩放\n次级 Influence_Range 调范围，Influence_Falloff 调衰减\n全局控制器：bendback_vis 显示次级，Pin_Start / Pin_End 固定端点\n固定端点跟随自身 FK 和次级，不受其他控制器局部影响', align='left')

    def is_local(self):
        return mc.optionMenu(self.menu, q=True, sl=True) == 2

    def settings(self):
        ui = self.owner
        return {'controls': int(mc.floatSliderGrp(ui.s6, q=True, v=True)),
                'joints': int(mc.floatSliderGrp(ui.s7, q=True, v=True)),
                'aim': mc.optionMenu(ui.s8, q=True, v=True),
                'up': mc.optionMenu(ui.s9, q=True, v=True),
                'support': ('narrow', 'standard', 'wide')[mc.optionMenu(self.range, q=True, sl=True) - 1],
                'twist': mc.checkBox(self.twist, q=True, v=True)}

    def changed(self, *args):
        ui = self.owner
        if self.is_local() and self.old_settings is None:
            self.old_settings = {
                'dynamic': mc.checkBoxGrp(ui.s10, q=True, v1=True),
                'merge': mc.checkBoxGrp(ui.s10, q=True, v2=True),
                'stretch': mc.checkBox(ui.stretchingBox, q=True, v=True),
                'slide': mc.checkBox(ui.ss2, q=True, v=True),
                'algorithm': mc.optionMenu(ui.add1, q=True, sl=True),
                'path': mc.checkBox(ui.path_handles['check'], q=True, v=True),
                'controls': mc.floatSliderGrp(ui.s6, q=True, v=True),
                'joints': mc.floatSliderGrp(ui.s7, q=True, v=True)}
            mc.floatSliderGrp(ui.s6, e=True, v=8)
            mc.floatSliderGrp(ui.s7, e=True, v=33)
        elif not self.is_local() and self.old_settings is not None:
            saved = self.old_settings
            mc.checkBoxGrp(ui.s10, e=True, v1=saved['dynamic'], v2=saved['merge'])
            mc.checkBox(ui.stretchingBox, e=True, v=saved['stretch'])
            mc.checkBox(ui.ss2, e=True, v=saved['slide'])
            mc.optionMenu(ui.add1, e=True, sl=saved['algorithm'])
            mc.checkBox(ui.path_handles['check'], e=True, v=saved['path'])
            mc.floatSliderGrp(ui.s6, e=True, v=saved['controls'])
            mc.floatSliderGrp(ui.s7, e=True, v=saved['joints'])
            self.old_settings = None
        self.pending = None
        self.owner.reference_mode=None
        self.apply()

    def apply(self):
        ui = self.owner
        enabled = not self.is_local()
        mc.checkBoxGrp(ui.s10, e=True, en=enabled)
        if not enabled:
            mc.checkBoxGrp(ui.s10, e=True, v1=False, v2=False)
            for field in (ui.stretchingBox, ui.ss2, ui.path_handles['check']):
                mc.checkBox(field, e=True, v=False)
        mc.checkBoxGrp(ui.s10, e=True, en2=enabled and bool(mc.checkBoxGrp(ui.s10, q=True, v1=True)))
        for field in (ui.stretchingBox, ui.ss2, ui.path_handles['check']):
            mc.checkBox(field, e=True, en=enabled)
        mc.optionMenu(ui.add1, e=True, en=enabled)
        mc.floatSliderGrp(ui.ss1, e=True, en=enabled and bool(mc.checkBox(ui.ss2, q=True, v=True)))
        mc.intSliderGrp(ui.path_handles['count'], e=True,
                        en=enabled and bool(mc.checkBox(ui.path_handles['check'], q=True, v=True)))
        for button in (ui.s18, ui.s19, ui.d5, ui.d6, ui.d7):
            mc.button(button, e=True, en=enabled)
        mc.textFieldButtonGrp(ui.s13, e=True, label=u'3.创建局部位置预览' if not enabled else u'3.创建控制器校轴参考物体')
        mc.optionMenu(self.range, e=True, en=not enabled)
        mc.checkBox(self.twist, e=True, en=not enabled)
        mc.button(self.mesh, e=True, en=not enabled)

    def prepare(self):
        name = mc.textFieldGrp(self.owner.s5, q=True, tx=True).strip().replace(' ', '_')
        curves = mc.ls(sl=True, long=True, objectsOnly=True) or []
        if not curves:
            raise ValueError('Select one or more open NURBS curves.')
        config = self.settings()
        builds = [(name + ('_%d' % (i + 1) if len(curves) > 1 else ''), curve)
                  for i, curve in enumerate(curves)]
        for prefix, curve in builds:
            local.validate(prefix, curve, config['controls'], config['joints'], config['aim'], config['up'])
        for prefix, curve in builds:
            local.prepare(prefix, curve, config['controls'], config['joints'], config['aim'], config['up'])
        self.pending = (builds, config)
        self.owner.cur = curves

    def create(self):
        if self.pending is None:
            raise ValueError('Create the local preview first after changing the binding mode.')
        builds, prepared = self.pending
        config = self.settings()
        for key in ('controls', 'joints', 'aim', 'up'):
            if prepared[key] != config[key]:
                raise ValueError('Control/joint counts or axes changed; recreate the local preview.')
        for name, curve in builds:
            local.validate(name, curve, config['controls'], config['joints'], config['aim'], config['up'])
        for name, curve in builds:
            local.LocalRig(name, curve, **config).build()
        self.pending = None

    def bind_mesh(self, *args):
        try:
            local.bind_selected_models()
        except Exception as exc:
            mc.warning(str(exc))


def bake(owner, kind):
    if not local.selected_systems():
        return False
    if mc.checkBox(owner.d10, q=True, v=True):
        start, end = mc.playbackOptions(q=True, min=True), mc.playbackOptions(q=True, max=True)
    else:
        start = float(mc.textFieldGrp(owner.d8, q=True, tx=True))
        end = float(mc.textFieldGrp(owner.d9, q=True, tx=True))
    return local.bake_selected(start, end, kind)


def clear_animation(kind):
    return local.clear_animation(kind)
