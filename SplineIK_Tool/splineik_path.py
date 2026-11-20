# -*- coding: utf-8 -*-
"""Long FK path, skinned ribbon and multi-controller travel for SplineIK_Tool."""
import math
import maya.cmds as mc


def _curve_shape(node):
    if not node or not mc.objExists(node):
        return None
    if mc.nodeType(node) == 'nurbsCurve':
        return node
    return next((s for s in (mc.listRelatives(node, s=True, ni=True, f=True) or [])
                 if mc.nodeType(s) == 'nurbsCurve'), None)


def _subtract(a, b):
    return [a[i] - b[i] for i in range(3)]


def _length(v):
    return math.sqrt(sum(x * x for x in v))


def _cross(a, b):
    return [a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0]]


def _unit(v):
    length = _length(v)
    if length <= 1e-8:
        raise ValueError('Cannot construct a path from coincident endpoints.')
    return [x / length for x in v]


def _domain(shape, axis):
    return mc.getAttr(shape + '.minMaxRange' + axis)[0]


def _normalized(value, bounds):
    low, high = bounds
    if high - low <= 1e-8:
        raise ValueError('Invalid surface parameter domain.')
    return max(0.0, min(1.0, (value - low) / float(high - low)))


def cleanup(name, main_ctrl=None):
    """Delete only the nodes registered to this path, including non-DAG nodes."""
    metadata = name + '_path_system'
    if main_ctrl and mc.objExists(main_ctrl + '.splineikPathSystem'):
        found = mc.listConnections(main_ctrl + '.splineikPathSystem', s=True, d=False) or []
        if found:
            metadata = found[0]
    if not mc.objExists(metadata):
        return False
    nodes = mc.listConnections(metadata + '.members', s=True, d=False) or []
    owners = mc.listConnections(metadata + '.owner', s=True, d=False) or []
    constraints = [n for n in nodes if mc.objExists(n) and mc.nodeType(n) == 'parentConstraint']
    if constraints:
        mc.delete(constraints)
    dependencies = [n for n in nodes if mc.objExists(n) and not mc.objectType(n, isAType='dagNode')]
    if dependencies:
        mc.delete(dependencies)
    remaining = [n for n in nodes if mc.objExists(n)]
    if remaining:
        mc.delete(remaining)
    for owner in owners:
        for attribute in ('Path_Ctrl_Vis', 'Travel', 'splineikPathSystem'):
            if mc.objExists(owner + '.' + attribute):
                mc.deleteAttr(owner + '.' + attribute)
    if mc.objExists(metadata):
        mc.delete(metadata)
    return True


class PathSystem(object):
    def __init__(self, name, curve, main_ctrl, count=50, width=1.0,
                 extension=10.0, controls=None, references=None, rig_group=None):
        self.name = name
        self.curve = curve
        self.main_ctrl = main_ctrl
        self.count = int(count)
        self.width = float(width)
        self.extension = float(extension)
        self.controls = list(controls or [main_ctrl])
        self.references = list(references or [c + '_world' for c in self.controls])
        self.rig_group = rig_group or name + '_spline_rig_grp'
        self.nodes = []
        self.metadata = None
        self.follicles = []
        self.controllers = []
        self.joints = []
        self.surface = None

    def _register(self, nodes):
        if isinstance(nodes, (str, type(u''))):
            nodes = [nodes]
        for node in nodes:
            if node not in self.nodes:
                mc.connectAttr(node + '.message', '%s.members[%d]' % (self.metadata, len(self.nodes)))
                self.nodes.append(node)
        return nodes[0] if len(nodes) == 1 else nodes

    def _group(self, suffix, parent):
        return self._register(mc.group(em=True, n=self.name + suffix, p=parent))

    def _validate(self):
        shape = _curve_shape(self.curve)
        if not shape or mc.getAttr(shape + '.form') != 0:
            raise ValueError('Path creation requires an open NURBS curve.')
        if self.count < 4 or self.width <= 0 or self.extension < 1:
            raise ValueError('Path count must be >= 4, width > 0 and extension >= 1.')
        if not mc.objExists(self.rig_group) or len(self.controls) != len(self.references):
            raise ValueError('Missing rig group or mismatched controller/reference lists.')
        for control, reference in zip(self.controls, self.references):
            if not mc.objExists(control) or not mc.objExists(reference):
                raise ValueError('Missing controller/reference: %s / %s' % (control, reference))
            if not mc.objExists(control + '.follow'):
                raise ValueError('Missing follow attribute: ' + control)
            if mc.listConnections(reference + '.translate', s=True, d=False):
                raise ValueError('Reference is already driven: ' + reference)
        for suffix in ('_path_grp', '_path_system'):
            if mc.objExists(self.name + suffix):
                raise ValueError('A path already exists for ' + self.name)
        for attribute in ('Travel', 'Path_Ctrl_Vis', 'splineikPathSystem'):
            if mc.objExists(self.main_ctrl + '.' + attribute):
                raise ValueError('Remove the existing path before rebuilding: ' + attribute)
        bounds = mc.getAttr(shape + '.minMaxValue')[0]
        start = mc.pointOnCurve(self.curve, pr=bounds[0], p=True)
        end = mc.pointOnCurve(self.curve, pr=bounds[1], p=True)
        direction = _unit(_subtract(end, start))
        length = _length(_subtract(end, start)) * self.extension
        return start, direction, length

    def build(self):
        """Build atomically; preserve the original spline if the path fails."""
        start, direction, length = self._validate()
        if not mc.undoInfo(q=True, state=True):
            raise RuntimeError('Enable Maya undo before creating a path system.')
        selection = mc.ls(sl=True, long=True) or []
        mc.undoInfo(openChunk=True, chunkName='SplineIKPathBuild')
        error = None
        try:
            self.metadata = mc.createNode('network', n=self.name + '_path_system')
            mc.addAttr(self.metadata, ln='members', at='message', multi=True)
            mc.addAttr(self.metadata, ln='owner', at='message')
            mc.connectAttr(self.main_ctrl + '.message', self.metadata + '.owner')
            mc.addAttr(self.main_ctrl, ln='splineikPathSystem', at='message')
            mc.connectAttr(self.metadata + '.message', self.main_ctrl + '.splineikPathSystem')
            root = self._group('_path_grp', self.rig_group)
            control_group = self._group('_path_controls_grp', root)
            technical = self._group('_path_technical_grp', root)
            mc.setAttr(technical + '.inheritsTransform', 0, lock=True)
            mc.setAttr(technical + '.visibility', 0)
            fol_group = self._group('_path_follicles_grp', technical)
            self.scale_node = self._register(mc.createNode('decomposeMatrix',
                                                          n=self.name + '_path_globalScale'))
            mc.connectAttr(self.rig_group + '.worldMatrix[0]', self.scale_node + '.inputMatrix')
            reference_up = [0.0, 1.0, 0.0]
            if abs(sum(direction[i] * reference_up[i] for i in range(3))) > 0.99:
                reference_up = [0.0, 0.0, 1.0]
            side = _unit(_cross(direction, reference_up))
            up = _unit(_cross(side, direction))
            positions = [[start[k] + direction[k] * length * i / float(self.count - 1)
                          for k in range(3)] for i in range(self.count)]
            self._build_controls(positions, direction, up, side, control_group)
            self.surface = self._build_surface(positions, side, technical)
            surface_shape = mc.listRelatives(self.surface, s=True, ni=True, f=True)[0]
            initial_v = []
            for index, reference in enumerate(self.references):
                fol, fshape, v = self._attach(surface_shape, reference, fol_group, index)
                self.follicles.append(fshape)
                initial_v.append(v)
            delta = 1.0 - max(initial_v)
            if delta <= 1e-6:
                raise ValueError('No travel space remains; increase the path extension.')
            mc.addAttr(self.main_ctrl, ln='Travel', at='double', min=0, max=10, dv=0, k=True)
            mc.addAttr(self.main_ctrl, ln='Path_Ctrl_Vis', at='bool', dv=0, k=True)
            mc.connectAttr(self.main_ctrl + '.Path_Ctrl_Vis', control_group + '.visibility')
            for fshape, v in zip(self.follicles, initial_v):
                mc.addAttr(fshape, ln='pathStartV', at='double', dv=v)
                mc.setAttr(fshape + '.pathStartV', lock=True)
                for driver, value in ((0, v), (10, v + delta)):
                    mc.setDrivenKeyframe(fshape, at='parameterV', cd=self.main_ctrl + '.Travel',
                                         dv=driver, v=value, itt='linear', ott='linear')
                self._register(mc.listConnections(fshape + '.parameterV', s=True, d=False) or [])
            for control in self.controls:
                mc.setAttr(control + '.follow', 1)
            if selection:
                mc.select(selection, r=True)
            else:
                mc.select(cl=True)
        except Exception as exc:
            error = exc
        finally:
            mc.undoInfo(closeChunk=True)
        if error is not None:
            mc.undo()
            self.nodes = []
            raise RuntimeError('Path creation rolled back: %s' % error)
        return True

    def _build_controls(self, positions, direction, up, side, control_group):
        previous = control_group
        radius = self.width * 0.6
        for index, position in enumerate(positions):
            prefix = '%s_path_ctrl_%02d' % (self.name, index + 1)
            off = self._register(mc.group(em=True, n=prefix + '_OffGrp'))
            matrix = direction + [0.0] + up + [0.0] + side + [0.0] + position + [1.0]
            mc.xform(off, ws=True, matrix=matrix)
            mc.parent(off, previous)
            sdk = self._register(mc.group(em=True, n=prefix + '_SdkGrp', p=off))
            ctrl = self._register(mc.circle(ch=False, n=prefix, r=radius, nr=(1, 0, 0))[0])
            mc.parent(ctrl, sdk, relative=True)
            sub_off = self._register(mc.group(em=True, n=prefix + '_Sub_Ctrl_OffGrp', p=ctrl))
            sub_sdk = self._register(mc.group(em=True, n=prefix + '_Sub_Ctrl_SdkGrp', p=sub_off))
            sub = self._register(mc.circle(ch=False, n=prefix + '_Sub_Ctrl',
                                            r=radius * 0.65, nr=(1, 0, 0))[0])
            mc.parent(sub, sub_sdk, relative=True)
            for node, color in ((ctrl, 13), (sub, 17)):
                shape = mc.listRelatives(node, s=True)[0]
                mc.setAttr(shape + '.overrideEnabled', 1)
                mc.setAttr(shape + '.overrideColor', color)
            mc.addAttr(ctrl, ln='Sub_Ctrl_Vis', at='bool', dv=0, k=True)
            mc.connectAttr(ctrl + '.Sub_Ctrl_Vis', sub_off + '.visibility')
            mc.select(cl=True)
            joint = self._register(mc.joint(n='%s_path_jnt_%02d' % (self.name, index + 1)))
            mc.parent(joint, sub, relative=True)
            mc.setAttr(joint + '.drawStyle', 2)
            self.controllers.append(ctrl)
            self.joints.append(joint)
            previous = ctrl

    def _build_surface(self, positions, side, technical):
        rails = []
        for sign in (-1.0, 1.0):
            points = [[p[k] + side[k] * self.width * 0.5 * sign for k in range(3)]
                      for p in positions]
            spans = self.count - 3
            knots = [0.0] * 3 + [i / float(spans) for i in range(1, spans)] + [1.0] * 3
            rail = mc.curve(d=3, p=points, k=knots, n=self.name + '_path_temporary_crv')
            rails.append(rail)
        try:
            surface = self._register(mc.loft(rails[0], rails[1], ch=False, d=1, u=True,
                                             ar=False, n=self.name + '_path_surface')[0])
            mc.delete(surface, constructionHistory=True)
        finally:
            mc.delete([r for r in rails if mc.objExists(r)])
        shape = mc.listRelatives(surface, s=True, ni=True, f=True)[0]
        ub, vb = _domain(shape, 'U'), _domain(shape, 'V')
        corner = mc.pointOnSurface(surface, u=ub[0], v=vb[0], p=True)
        u_edge = mc.pointOnSurface(surface, u=ub[1], v=vb[0], p=True)
        v_edge = mc.pointOnSurface(surface, u=ub[0], v=vb[1], p=True)
        if _length(_subtract(u_edge, corner)) > _length(_subtract(v_edge, corner)):
            mc.reverseSurface(surface, d=3, ch=False, rpo=True)
        mc.parent(surface, technical)
        skin = self._register(mc.skinCluster(self.joints, surface, tsb=True, mi=2,
                                             n=self.name + '_path_skinCluster')[0])
        self._register(mc.listConnections(skin + '.bindPose', s=True, d=False) or [])
        shape = mc.listRelatives(surface, s=True, ni=True, f=True)[0]
        nu = mc.getAttr(shape + '.spansU') + mc.getAttr(shape + '.degreeU')
        nv = mc.getAttr(shape + '.spansV') + mc.getAttr(shape + '.degreeV')
        start = positions[0]
        axis = _unit(_subtract(positions[-1], start))
        total = _length(_subtract(positions[-1], start))
        for u_index in range(nu):
            for v_index in range(nv):
                cv = '%s.cv[%d][%d]' % (surface, u_index, v_index)
                pos = mc.pointPosition(cv, world=True)
                fraction = max(0.0, min(1.0, sum((pos[k] - start[k]) * axis[k]
                                                for k in range(3)) / total))
                value = fraction * (self.count - 1)
                left = min(int(value), self.count - 1)
                right = min(left + 1, self.count - 1)
                weights = [0.0] * self.count
                weights[left] = 1.0 - (value - left)
                weights[right] += value - left
                mc.skinPercent(skin, cv, tv=list(zip(self.joints, weights)), normalize=True)
        return surface

    def _attach(self, shape, reference, parent, index):
        nearest = mc.createNode('closestPointOnSurface')
        try:
            mc.connectAttr(shape + '.worldSpace[0]', nearest + '.inputSurface')
            position = mc.xform(reference, q=True, ws=True, t=True)
            mc.setAttr(nearest + '.inPosition', *position)
            raw_u = mc.getAttr(nearest + '.parameterU')
            raw_v = mc.getAttr(nearest + '.parameterV')
            u = _normalized(raw_u, _domain(shape, 'U'))
            v = _normalized(raw_v, _domain(shape, 'V'))
        finally:
            mc.delete(nearest)
        prefix = '%s_path_fol_%02d' % (self.name, index + 1)
        fshape = mc.createNode('follicle', n=prefix + 'Shape')
        fol = mc.listRelatives(fshape, p=True)[0]
        fol = mc.rename(fol, prefix)
        self._register(fol)
        mc.parent(fol, parent)
        mc.connectAttr(shape + '.local', fshape + '.inputSurface')
        mc.connectAttr(shape + '.worldMatrix[0]', fshape + '.inputWorldMatrix')
        mc.setAttr(fshape + '.simulationMethod', 0)
        mc.setAttr(fshape + '.parameterU', u)
        mc.setAttr(fshape + '.parameterV', v)
        mc.connectAttr(fshape + '.outTranslate', fol + '.translate')
        mc.connectAttr(fshape + '.outRotate', fol + '.rotate')
        mc.connectAttr(self.scale_node + '.outputScale', fol + '.scale')
        self._register(mc.parentConstraint(fol, reference, mo=True,
                                            n=prefix + '_attachConstraint'))
        return fol, fshape, v
