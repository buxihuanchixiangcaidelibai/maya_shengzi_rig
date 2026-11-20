# -*- coding: utf-8 -*-
"""Independent local-curve deformation, without IK or live arc-length redistribution."""
import json
import math
import re
import maya.cmds as mc
import maya.api.OpenMaya as om


def curve_fn(curve):
    selection = om.MSelectionList()
    selection.add(curve)
    dag = selection.getDagPath(0)
    if dag.apiType() == om.MFn.kTransform:
        dag.extendToShape()
    return om.MFnNurbsCurve(dag)


def shape_of(curve):
    if mc.nodeType(curve) == 'nurbsCurve':
        return curve
    shapes = mc.listRelatives(curve, s=True, ni=True, f=True, type='nurbsCurve') or []
    if len(shapes) != 1:
        raise ValueError('Select a transform with one visible NURBS curve.')
    return shapes[0]


def validate(name, curve, controls, joints, aim, up):
    if not re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', name):
        raise ValueError('Use a unique name containing letters, digits and underscores.')
    if mc.objExists(name + '_spline_rig_grp') or mc.objExists(name + '_local_system'):
        raise ValueError('A rig already exists: ' + name)
    shape = shape_of(curve)
    if mc.getAttr(shape + '.form') != 0 or curve_fn(shape).length() <= 1e-6:
        raise ValueError('Local mode requires a non-zero open NURBS curve.')
    if int(controls) < 4 or int(joints) < 4:
        raise ValueError('Local mode requires at least four controls and four joints.')
    if aim not in 'xyz' or up not in 'xyz' or aim == up:
        raise ValueError('Aim and up axes must be different.')
    if not mc.undoInfo(q=True, state=True):
        raise ValueError('Enable Maya undo before building a local rig.')


def prepare(name, curve, controls=8, joints=33, aim='x', up='y'):
    validate(name, curve, controls, joints, aim, up)
    old = name + '_local_preview_grp'
    if mc.objExists(old):
        mc.delete(old)
    group = mc.group(em=True, n=old)
    fn = curve_fn(curve)
    for i in range(int(controls)):
        param = fn.findParamFromLength(fn.length() * i / float(int(controls) - 1))
        point = fn.getPointAtParam(param, om.MSpace.kWorld)
        loc = mc.spaceLocator(n='%s_local_preview_%02d' % (name, i + 1))[0]
        mc.xform(loc, ws=True, t=(point.x, point.y, point.z))
        mc.parent(loc, group)
    mc.select(group, r=True)
    return group


def system_of(node):
    node = node.split('.', 1)[0]
    if not mc.objExists(node):
        return None
    if mc.nodeType(node) == 'nurbsCurve':
        node = (mc.listRelatives(node, p=True, f=True) or [node])[0]
    if mc.objExists(node + '.localRopeSystem'):
        linked = mc.listConnections(node + '.localRopeSystem', s=True, d=False) or []
        return linked[0] if linked else None
    return None


def selected_systems():
    return sorted(set(s for s in (system_of(n) for n in (mc.ls(sl=True, long=True) or [])) if s))


def members(system, attribute):
    result = []
    if not mc.objExists(system + '.' + attribute):
        return result
    for index in mc.getAttr(system + '.' + attribute, multiIndices=True) or []:
        nodes = mc.listConnections('%s.%s[%d]' % (system, attribute, index),
                                   s=True, d=False, shapes=True) or []
        result.extend(nodes)
    return result


def animation_controls(system):
    return members(system, 'controllers') + members(system, 'secondaryControls') + members(system, 'globalControls')


def animation_attributes(control):
    if mc.objExists(control + '.Pin_Start') and mc.objExists(control + '.Pin_End'):
        attributes = ('Pin_Start', 'Pin_End')
    else:
        attributes = ('tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz',
                      'Twist', 'Influence_Range', 'Influence_Falloff')
    return [a for a in attributes if mc.objExists(control + '.' + a)
            and not mc.getAttr(control + '.' + a, lock=True)]


def project_weights(shape, values, cv_index, influences):
    """Keep smoothed skin weights inside the original longitudinal support mask."""
    curve = (mc.listRelatives(shape, p=True, f=True) or [shape])[0]
    data = json.loads(mc.getAttr(curve + '.localSupportData'))
    allowed = data['allowed'][cv_index]
    names = [n.split('|')[-1] for n in influences]
    base = names.index(data['base'])
    projected = [max(0.0, value) if names[i] in allowed else 0.0
                 for i, value in enumerate(values)]
    if not allowed or allowed == [data['base']]:
        return [1.0 if i == base else 0.0 for i in range(len(values))]
    total = sum(projected)
    if total <= 1e-12:
        projected[base] = 1.0
    else:
        projected = [v / total for v in projected]
    return projected


class LocalRig(object):
    def __init__(self, name, curve, controls=8, joints=33, aim='x', up='y',
                 support='standard', pin_start=False, pin_end=False, twist=True):
        self.name, self.source = name, curve
        self.control_count, self.joint_count = int(controls), int(joints)
        self.aim, self.up = aim, up
        self.support = support
        self.pin_start, self.pin_end, self.twist = bool(pin_start), bool(pin_end), bool(twist)
        self.nodes = []
        self.controls, self.drivers, self.joints = [], [], []
        self.secondary_controls = []

    def node(self, kind, suffix):
        return self.track(mc.createNode(kind, n=self.name + suffix))

    def track(self, node):
        mc.connectAttr(node + '.message', '%s.splineikOwnedNodes[%d]' % (self.root, len(self.nodes)))
        self.nodes.append(node)
        return node

    def group(self, suffix, parent):
        return self.track(mc.group(em=True, n=self.name + suffix, p=parent))

    def link(self, node, attribute=None):
        if not mc.objExists(node + '.localRopeSystem'):
            mc.addAttr(node, ln='localRopeSystem', at='message')
            mc.connectAttr(self.system + '.message', node + '.localRopeSystem')
        if attribute:
            index = len(mc.getAttr(self.system + '.' + attribute, multiIndices=True) or [])
            mc.connectAttr(node + '.message', '%s.%s[%d]' % (self.system, attribute, index))
        if not mc.objExists(node + '.delete_' + self.name):
            mc.addAttr(node, ln='delete_' + self.name, at='bool')

    def control_shape(self, name, secondary=False, scale=1.0, color=17):
        import kxj_ik_dy305 as core
        factory = core.ik()
        ctrl = self.track(factory.cross_shape(name) if secondary else factory.square_shape(name))
        shape = mc.listRelatives(ctrl, s=True, f=True)[0]
        if scale != 1.0:
            mc.scale(scale, scale, scale, shape + '.cv[*]', relative=True, objectSpace=True)
        mc.setAttr(shape + '.overrideEnabled', 1)
        mc.setAttr(shape + '.overrideColor', color)
        return ctrl

    def build(self):
        validate(self.name, self.source, self.control_count, self.joint_count, self.aim, self.up)
        if self.support not in ('narrow', 'standard', 'wide'):
            raise ValueError('Invalid local influence preset.')
        selected = mc.ls(sl=True, long=True) or []
        mc.undoInfo(openChunk=True, chunkName='BuildLocalRope')
        error = None
        try:
            self.root = mc.group(em=True, n=self.name + '_spline_rig_grp')
            mc.addAttr(self.root, ln='splineikOwnedNodes', at='message', multi=True)
            self.system = self.node('network', '_local_system')
            for attribute in ('controllers', 'secondaryControls', 'globalControls', 'joints', 'curves', 'modelSkins'):
                mc.addAttr(self.system, ln=attribute, at='message', multi=True)
            mc.addAttr(self.system, ln='rigMode', dt='string')
            mc.setAttr(self.system + '.rigMode', 'localCurve', type='string')
            mc.addAttr(self.system, ln='bakeConnections', dt='string')
            mc.setAttr(self.system + '.bakeConnections', '{}', type='string')
            self.link(self.root)
            global_ctrl = self.control_shape(self.name + '_Global_Ctrl', scale=2.0, color=13)
            mc.parent(global_ctrl, self.root, relative=True)
            self.global_ctrl = global_ctrl
            self.link(global_ctrl, 'globalControls')
            mc.addAttr(global_ctrl, ln='bendback_vis', at='double', min=0, max=1, dv=0, k=True)
            mc.addAttr(global_ctrl, ln='Pin_Start', nn=u'固定起点位置', at='bool', dv=self.pin_start, k=True)
            mc.addAttr(global_ctrl, ln='Pin_End', nn=u'固定终点位置', at='bool', dv=self.pin_end, k=True)
            control_group = self.group('_local_controls_grp', global_ctrl)
            technical = self.group('_local_technical_grp', global_ctrl)
            mc.setAttr(technical + '.visibility', 0)
            driver_group = self.group('_local_driver_space', technical)
            mc.setAttr(driver_group + '.inheritsTransform', 0, lock=True)
            joint_group = self.group('_local_joints_grp', global_ctrl)
            mc.setAttr(joint_group + '.visibility', 0)
            curve = self.track(mc.duplicate(self.source, rr=True, n=self.name + '_local_fk_crv')[0])
            mc.delete(curve, constructionHistory=True)
            mc.parent(curve, world=True) if mc.listRelatives(curve, p=True) else None
            for attribute in ('translate', 'rotate', 'scale'):
                for axis in 'XYZ':
                    mc.setAttr(curve + '.' + attribute + axis, lock=False)
            mc.makeIdentity(curve, apply=True, t=True, r=True, s=True)
            mc.rebuildCurve(curve, ch=False, rpo=True, rt=0, end=1, kr=0, kep=True,
                            kcp=False, s=max(16, (self.control_count - 1) * 4), d=3, tol=0.001)
            mc.parent(curve, technical)
            self.curve = curve
            self.link(curve)
            fn = curve_fn(curve)
            length = fn.length()
            control_params = [fn.findParamFromLength(length * i / float(self.control_count - 1))
                              for i in range(self.control_count)]
            radius = max(length / self.control_count * 0.18, 0.02)
            mc.scale(radius, radius, radius, shape_of(global_ctrl) + '.cv[*]',
                     relative=True, objectSpace=True)
            previous = None
            for i, param in enumerate(control_params):
                point = fn.getPointAtParam(param, om.MSpace.kObject)
                offset = self.group('_local_ctrl_%02d_OffGrp' % (i + 1), control_group)
                mc.setAttr(offset + '.translate', point.x, point.y, point.z)
                if previous:
                    mc.parent(offset, previous)
                ctrl = self.control_shape('%s_%d' % (self.name, i + 1),
                                          scale=radius, color=13 if i == 0 else 17)
                mc.parent(ctrl, offset, relative=True)
                self.link(ctrl, 'controllers')
                sub_group = self.group('_%d_bendback_grp' % (i + 1), ctrl)
                sub = self.control_shape(ctrl + '_bendback', secondary=True, scale=radius, color=21)
                mc.parent(sub, sub_group, relative=True)
                self.link(sub, 'secondaryControls')
                for control, role in ((ctrl, 'FK'), (sub, 'localSecondary')):
                    mc.addAttr(control, ln='localControlRole', dt='string')
                    mc.setAttr(control + '.localControlRole', role, type='string', lock=True)
                    if self.twist:
                        mc.addAttr(control, ln='Twist', at='double', dv=0, k=True)
                    mc.setAttr(control + '.visibility', lock=True, k=False)
                    for axis in 'XYZ':
                        mc.setAttr(control + '.scale' + axis, lock=control == ctrl, k=control == sub)
                sub_shape = mc.listRelatives(sub, s=True, f=True)[0]
                mc.connectAttr(global_ctrl + '.bendback_vis', sub_shape + '.visibility')
                mc.select(cl=True)
                driver = self.track(mc.joint(n='%s_local_driver_%02d' % (self.name, i + 1)))
                mc.parent(driver, driver_group, relative=True)
                relative = self.node('multMatrix', '_local_driver_matrix_%02d' % i)
                mc.connectAttr(ctrl + '.worldMatrix[0]', relative + '.matrixIn[0]')
                mc.connectAttr(global_ctrl + '.worldInverseMatrix[0]', relative + '.matrixIn[1]')
                decomp = self.node('decomposeMatrix', '_local_driver_pose_%02d' % i)
                mc.connectAttr(relative + '.matrixSum', decomp + '.inputMatrix')
                mc.connectAttr(decomp + '.outputTranslate', driver + '.translate')
                mc.connectAttr(decomp + '.outputRotate', driver + '.rotate')
                mc.setAttr(driver + '.drawStyle', 2)
                self.controls.append(ctrl)
                self.secondary_controls.append(sub)
                self.drivers.append(driver)
                previous = ctrl
            base = self.node('joint', '_local_static_driver')
            mc.parent(base, driver_group, relative=True)
            mc.setAttr(base + '.drawStyle', 2)
            skin = self.track(mc.skinCluster(self.drivers + [base], curve, tsb=True,
                                             mi=self.control_count + 1, sm=0,
                                             n=self.name + '_local_curve_skin')[0])
            sources = mc.listConnections(skin + '.geomMatrix', s=True, d=False, plugs=True) or []
            for plug in sources:
                mc.disconnectAttr(plug, skin + '.geomMatrix')
            mc.setAttr(skin + '.geomMatrix', 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, type='matrix')
            for pose in mc.listConnections(skin + '.bindPose', s=True, d=False) or []:
                self.track(pose)
            fn = curve_fn(curve)
            shape = shape_of(curve)
            allowed = []
            self.cv_positions = []
            support_scale = {'narrow': 0.8, 'standard': 1.25, 'wide': 2.0}[self.support]
            knots = list(fn.knots())
            full_knots = [knots[0]] + knots + [knots[-1]]
            for index in range(fn.numCVs):
                param = sum(full_knots[index + 1:index + fn.degree + 1]) / float(fn.degree)
                position = fn.findLengthFromParam(param) / length
                self.cv_positions.append(position)
                weights = self.weights(position, support_scale)
                remainder = max(0.0, 1.0 - sum(weights))
                total = sum(weights) + remainder
                pairs = [(j, w / total) for j, w in zip(self.drivers, weights)] + [(base, remainder / total)]
                mc.skinPercent(skin, '%s.cv[%d]' % (curve, index), tv=pairs, normalize=True)
                names = [j for j, w in zip(self.drivers, weights) if w > 0]
                allowed.append(names + [base])
            mc.addAttr(curve, ln='localSupportData', dt='string')
            mc.setAttr(curve + '.localSupportData', json.dumps({'allowed': allowed, 'base': base}), type='string')
            self.make_secondary_deformers(global_ctrl, technical, support_scale)
            fn = curve_fn(self.curve)
            shape = shape_of(self.curve)
            self.sample_params = [fn.findParamFromLength(length * i / float(self.joint_count - 1))
                                  for i in range(self.joint_count)]
            for i, param in enumerate(self.sample_params):
                self.make_sample(i, param, fn, shape, joint_group, support_scale)
            mc.addAttr(self.system, ln='restCurveData', dt='string')
            data = {'points': [[p.x, p.y, p.z] for p in fn.cvPositions(om.MSpace.kObject)],
                    'knots': list(fn.knots()), 'degree': fn.degree,
                    'length': length, 'params': self.sample_params}
            mc.setAttr(self.system + '.restCurveData', json.dumps(data), type='string')
            mc.select(global_ctrl, r=True)
        except Exception as exc:
            error = exc
        finally:
            mc.undoInfo(closeChunk=True)
        if error:
            mc.undo()
            if selected:
                mc.select([n for n in selected if mc.objExists(n)], r=True)
            raise RuntimeError('Local rig creation rolled back: %s' % error)
        preview = self.name + '_local_preview_grp'
        if mc.objExists(preview):
            mc.delete(preview)
        return self.system

    def weights(self, position, scale):
        radius = scale / float(self.control_count - 1)
        values = []
        for i in range(self.control_count):
            distance = abs(position - i / float(self.control_count - 1)) / radius
            value = (1 - distance) ** 2 * (1 + 2 * distance) if distance < 1 else 0.0
            values.append(value)
        return values

    def secondary_weight(self, control_index, position, prefix):
        sub = self.secondary_controls[control_index]
        distance = abs(position * (self.control_count - 1) - control_index)
        ramp = self.node('remapValue', prefix + '_range')
        mc.setAttr(ramp + '.inputValue', distance)
        mc.connectAttr(sub + '.Influence_Range', ramp + '.inputMax')
        for index, value in ((0, 1.0), (1, 0.0)):
            mc.setAttr('%s.value[%d].value_Position' % (ramp, index), index)
            mc.setAttr('%s.value[%d].value_FloatValue' % (ramp, index), value)
            mc.setAttr('%s.value[%d].value_Interp' % (ramp, index), 2)
        falloff = self.node('multiplyDivide', prefix + '_falloff')
        mc.setAttr(falloff + '.operation', 3)
        mc.connectAttr(ramp + '.outValue', falloff + '.input1X')
        mc.connectAttr(sub + '.Influence_Falloff', falloff + '.input2X')
        return falloff + '.outputX'

    def make_secondary_deformers(self, global_ctrl, technical, support_scale):
        fk_curve = self.curve
        fn = curve_fn(fk_curve)
        points = [(p.x, p.y, p.z) for p in fn.cvPositions(om.MSpace.kObject)]
        output = self.track(mc.curve(d=fn.degree, p=points, k=list(fn.knots()),
                                     n=self.name + '_drv_crv'))
        mc.parent(output, technical, relative=True)
        self.curve = output
        self.link(output, 'curves')
        for node, attribute, source in ((output, 'localFkCurve', fk_curve),
                                        (fk_curve, 'localCurveOutput', output)):
            mc.addAttr(node, ln=attribute, at='message')
            mc.connectAttr(source + '.message', node + '.' + attribute)
        mc.addAttr(output, ln='localSupportData', dt='string')
        mc.setAttr(output + '.localSupportData', mc.getAttr(fk_curve + '.localSupportData'), type='string')
        info = self.node('curveInfo', '_local_fk_points')
        mc.connectAttr(shape_of(fk_curve) + '.local', info + '.inputCurve')
        shape = shape_of(output)
        sums = []
        for cv_index in range(len(self.cv_positions)):
            total = self.node('plusMinusAverage', '_local_cv_%03d_sum' % cv_index)
            mc.connectAttr('%s.controlPoints[%d]' % (info, cv_index), total + '.input3D[0]')
            point = total + '.output3D'
            if cv_index in (0, len(self.cv_positions) - 1):
                start = cv_index == 0
                endpoint = self.secondary_controls[0 if start else -1]
                pin = global_ctrl + ('.Pin_Start' if start else '.Pin_End')
                prefix = '_local_pin_start' if start else '_local_pin_end'
                relative = self.node('multMatrix', prefix + '_matrix')
                mc.connectAttr(endpoint + '.worldMatrix[0]', relative + '.matrixIn[0]')
                mc.connectAttr(global_ctrl + '.worldInverseMatrix[0]', relative + '.matrixIn[1]')
                pose = self.node('decomposeMatrix', prefix + '_pose')
                mc.connectAttr(relative + '.matrixSum', pose + '.inputMatrix')
                select = self.node('choice', prefix + '_position')
                mc.connectAttr(pin, select + '.selector')
                mc.connectAttr(point, select + '.input[0]')
                mc.connectAttr(pose + '.outputTranslate', select + '.input[1]')
                point = select + '.output'
            mc.connectAttr(point, '%s.controlPoints[%d]' % (shape, cv_index))
            sums.append(total)
        for i, (ctrl, sub) in enumerate(zip(self.controls, self.secondary_controls)):
            mc.addAttr(sub, ln='Influence_Range', nn=u'影响范围', at='double',
                       min=0.01, max=self.control_count, dv=support_scale, k=True)
            mc.addAttr(sub, ln='Influence_Falloff', nn=u'衰减曲线', at='double',
                       min=0.1, max=8.0, dv=1.0, k=True)
            prefix = '_local_secondary_%02d' % (i + 1)
            pose = self.node('multMatrix', prefix + '_pose')
            mc.connectAttr(global_ctrl + '.worldMatrix[0]', pose + '.matrixIn[0]')
            mc.connectAttr(ctrl + '.worldInverseMatrix[0]', pose + '.matrixIn[1]')
            mc.connectAttr(sub + '.worldMatrix[0]', pose + '.matrixIn[2]')
            mc.connectAttr(global_ctrl + '.worldInverseMatrix[0]', pose + '.matrixIn[3]')
            for cv_index, position in enumerate(self.cv_positions):
                cv_prefix = prefix + '_cv_%03d' % cv_index
                point = '%s.controlPoints[%d]' % (info, cv_index)
                transformed = self.node('pointMatrixMult', cv_prefix + '_point')
                mc.connectAttr(point, transformed + '.inPoint')
                mc.connectAttr(pose + '.matrixSum', transformed + '.inMatrix')
                delta = self.node('plusMinusAverage', cv_prefix + '_delta')
                mc.setAttr(delta + '.operation', 2)
                mc.connectAttr(transformed + '.output', delta + '.input3D[0]')
                mc.connectAttr(point, delta + '.input3D[1]')
                weight = self.secondary_weight(i, position, cv_prefix)
                weighted = self.node('multiplyDivide', cv_prefix + '_weighted')
                mc.connectAttr(delta + '.output3D', weighted + '.input1')
                for axis in 'XYZ':
                    mc.connectAttr(weight, weighted + '.input2' + axis)
                mc.connectAttr(weighted + '.output', '%s.input3D[%d]' % (sums[cv_index], i + 1))

    def make_sample(self, index, param, fn, shape, parent, support_scale):
        prefix = '_local_sample_%03d' % (index + 1)
        poi = self.node('pointOnCurveInfo', prefix + '_point')
        mc.connectAttr(shape + '.local', poi + '.inputCurve')
        mc.setAttr(poi + '.turnOnPercentage', 0)
        mc.setAttr(poi + '.parameter', param)
        tangent = fn.tangent(param, om.MSpace.kObject).normal()
        reference = om.MVector(*[1.0 if axis == self.up else 0.0 for axis in 'xyz'])
        if abs(tangent * reference) > 0.95:
            reference = om.MVector(0, 0, 1) if self.up != 'z' else om.MVector(0, 1, 0)
        up = (reference - tangent * (tangent * reference)).normal()
        alternative = (tangent ^ up).normal()
        dot = self.node('vectorProduct', prefix + '_dot')
        mc.setAttr(dot + '.operation', 1)
        mc.connectAttr(poi + '.normalizedTangent', dot + '.input1')
        mc.setAttr(dot + '.input2', up.x, up.y, up.z)
        square = self.node('multiplyDivide', prefix + '_parallel')
        mc.connectAttr(dot + '.outputX', square + '.input1X')
        mc.connectAttr(dot + '.outputX', square + '.input2X')
        choice = self.node('condition', prefix + '_up')
        mc.setAttr(choice + '.operation', 2)
        mc.setAttr(choice + '.secondTerm', 0.98)
        mc.connectAttr(square + '.outputX', choice + '.firstTerm')
        mc.setAttr(choice + '.colorIfTrue', alternative.x, alternative.y, alternative.z)
        mc.setAttr(choice + '.colorIfFalse', up.x, up.y, up.z)
        side = self.node('vectorProduct', prefix + '_side')
        corrected = self.node('vectorProduct', prefix + '_normal')
        for node in (side, corrected):
            mc.setAttr(node + '.operation', 2)
            mc.setAttr(node + '.normalizeOutput', 1)
        mc.connectAttr(poi + '.normalizedTangent', side + '.input1')
        mc.connectAttr(choice + '.outColor', side + '.input2')
        mc.connectAttr(side + '.output', corrected + '.input1')
        mc.connectAttr(poi + '.normalizedTangent', corrected + '.input2')
        axes = {'xyz': (poi + '.normalizedTangent', corrected + '.output', side + '.output'),
                'xzy': (poi + '.normalizedTangent', None, corrected + '.output'),
                'yxz': (corrected + '.output', poi + '.normalizedTangent', None),
                'yzx': (side + '.output', poi + '.normalizedTangent', corrected + '.output'),
                'zxy': (corrected + '.output', side + '.output', poi + '.normalizedTangent'),
                'zyx': (None, corrected + '.output', poi + '.normalizedTangent')}
        other = next(a for a in 'xyz' if a not in (self.aim, self.up))
        rows = list(axes[self.aim + self.up + other])
        if None in rows:
            negate = self.node('multiplyDivide', prefix + '_negative')
            mc.connectAttr(side + '.output', negate + '.input1')
            mc.setAttr(negate + '.input2', -1, -1, -1)
            rows[rows.index(None)] = negate + '.output'
        matrix = self.node('fourByFourMatrix', prefix + '_frame')
        for row, vector in enumerate(rows):
            for column, axis in enumerate('XYZ'):
                mc.connectAttr(vector + axis, '%s.in%d%d' % (matrix, row, column))
        for column, axis in enumerate('XYZ'):
            mc.connectAttr(poi + '.position' + axis, '%s.in3%d' % (matrix, column))
        mc.setAttr(matrix + '.in33', 1)
        output = matrix + '.output'
        if self.twist:
            total = self.node('plusMinusAverage', prefix + '_twist')
            weights = self.weights(index / float(self.joint_count - 1), support_scale)
            norm = max(1.0, sum(weights))
            endpoint_pin = None
            if index in (0, self.joint_count - 1):
                endpoint_pin = self.global_ctrl + ('.Pin_Start' if index == 0 else '.Pin_End')
            for i, weight in enumerate(weights):
                if weight > 0:
                    multiply = self.node('multDoubleLinear', prefix + '_fkTwist_%02d' % (i + 1))
                    mc.connectAttr(self.controls[i] + '.Twist', multiply + '.input1')
                    mc.setAttr(multiply + '.input2', weight / norm)
                    mc.connectAttr(multiply + '.output', '%s.input1D[%d]' % (total, i))
                local_weight = self.secondary_weight(i, index / float(self.joint_count - 1),
                                                     prefix + '_secondary_%02d' % (i + 1))
                if endpoint_pin:
                    gate = self.node('condition', prefix + '_pinTwist_%02d' % (i + 1))
                    mc.connectAttr(endpoint_pin, gate + '.firstTerm')
                    mc.setAttr(gate + '.secondTerm', 1)
                    endpoint_index = 0 if index == 0 else self.control_count - 1
                    mc.setAttr(gate + '.colorIfTrueR', 1 if i == endpoint_index else 0)
                    mc.connectAttr(local_weight, gate + '.colorIfFalseR')
                    local_weight = gate + '.outColorR'
                multiply = self.node('multDoubleLinear', prefix + '_secondaryTwist_%02d' % (i + 1))
                mc.connectAttr(self.secondary_controls[i] + '.Twist', multiply + '.input1')
                mc.connectAttr(local_weight, multiply + '.input2')
                mc.connectAttr(multiply + '.output', '%s.input1D[%d]' % (total, self.control_count + i))
            compose = self.node('composeMatrix', prefix + '_roll')
            mc.connectAttr(total + '.output1D', compose + '.inputRotate' + self.aim.upper())
            mult = self.node('multMatrix', prefix + '_rolledFrame')
            mc.connectAttr(compose + '.outputMatrix', mult + '.matrixIn[0]')
            mc.connectAttr(output, mult + '.matrixIn[1]')
            output = mult + '.matrixSum'
        decomp = self.node('decomposeMatrix', prefix + '_decomp')
        mc.connectAttr(output, decomp + '.inputMatrix')
        mc.select(cl=True)
        joint = self.track(mc.joint(n='%s_jnt_%d' % (self.name, index + 1)))
        mc.parent(joint, parent, relative=True)
        mc.connectAttr(decomp + '.outputTranslate', joint + '.translate')
        mc.connectAttr(decomp + '.outputRotate', joint + '.rotate')
        mc.setAttr(joint + '.radius', 0.15)
        self.joints.append(joint)
        self.link(joint, 'joints')


def bind_selected_models():
    systems = selected_systems()
    if len(systems) != 1:
        raise ValueError('Select one local rope controller and the meshes to bind.')
    system = systems[0]
    joints = members(system, 'joints')
    controls = members(system, 'controllers') + members(system, 'secondaryControls')
    for ctrl in controls:
        if any(abs(v) > 1e-6 for attr in ('translate', 'rotate') for v in mc.getAttr(ctrl + '.' + attr)[0]):
            raise ValueError('Return FK and secondary translations/rotations to zero before binding meshes.')
        if any(abs(v - 1.0) > 1e-6 for v in mc.getAttr(ctrl + '.scale')[0]):
            raise ValueError('Return secondary scales to one before binding meshes.')
        if mc.objExists(ctrl + '.Twist') and abs(mc.getAttr(ctrl + '.Twist')) > 1e-6:
            raise ValueError('Return Twist to zero before binding meshes.')
    if json.loads(mc.getAttr(system + '.bakeConnections')):
        raise ValueError('Restore the sampled joint drive with Delete Joint Animation before binding meshes.')
    meshes = []
    for node in mc.ls(sl=True, long=True) or []:
        if mc.nodeType(node) == 'mesh':
            node = mc.listRelatives(node, p=True, f=True)[0]
        shapes = mc.listRelatives(node, s=True, ni=True, f=True, type='mesh') or []
        if len(shapes) == 1 and node not in meshes:
            if mc.ls(mc.listHistory(shapes[0]) or [], type='skinCluster'):
                raise ValueError('Mesh is already skinned; existing weights will not be overwritten: ' + node)
            meshes.append(node)
    if not meshes:
        raise ValueError('Also select the unskinned rope mesh.')
    data = json.loads(mc.getAttr(system + '.restCurveData'))
    curve = members(system, 'curves')[0]
    global_ctrl = mc.listRelatives(mc.listRelatives(curve, p=True, f=True)[0], p=True, f=True)[0]
    inverse = om.MMatrix(mc.xform(global_ctrl, q=True, ws=True, matrix=True)).inverse()
    root = system[:-len('_local_system')] + '_spline_rig_grp'
    mc.undoInfo(openChunk=True, chunkName='BindLocalRopeMesh')
    error = None
    try:
        rest = mc.curve(d=data['degree'], p=data['points'], k=data['knots'])
        fn = curve_fn(rest)
        for mesh in meshes:
            skin = mc.skinCluster(joints, mesh, tsb=True, mi=2, sm=0)[0]
            index = len(mc.getAttr(system + '.modelSkins', multiIndices=True) or [])
            mc.connectAttr(skin + '.message', '%s.modelSkins[%d]' % (system, index))
            for node in [skin] + (mc.listConnections(skin + '.bindPose', s=True, d=False) or []):
                slot = len(mc.getAttr(root + '.splineikOwnedNodes', multiIndices=True) or [])
                mc.connectAttr(node + '.message', '%s.splineikOwnedNodes[%d]' % (root, slot))
            for vertex in mc.ls(mesh + '.vtx[*]', fl=True) or []:
                pos = om.MPoint(*mc.pointPosition(vertex, world=True)) * inverse
                param = fn.closestPoint(pos, space=om.MSpace.kObject)[1]
                t = max(0.0, min(1.0, fn.findLengthFromParam(param) / data['length'])) * (len(joints) - 1)
                left = min(int(t), len(joints) - 1)
                right = min(left + 1, len(joints) - 1)
                weights = [0.0] * len(joints)
                weights[left] = 1.0 - (t - left)
                weights[right] += t - left
                mc.skinPercent(skin, vertex, tv=list(zip(joints, weights)), normalize=True)
        mc.delete(rest)
    except Exception as exc:
        error = exc
    finally:
        mc.undoInfo(closeChunk=True)
    if error:
        mc.undo()
        raise RuntimeError('Mesh binding rolled back: %s' % error)
    return meshes


def bake_selected(start, end, kind):
    systems = selected_systems()
    if not systems:
        return False
    if end < start or int(start) != start or int(end) != end:
        raise ValueError('Use integer start/end frames with start <= end.')
    if kind not in ('ctrl', 'jnt'):
        raise ValueError('Invalid local bake target.')
    if kind == 'jnt' and any(json.loads(mc.getAttr(s + '.bakeConnections')) for s in systems):
        raise ValueError('Restore the sampled joint drive with Delete Joint Animation before baking again.')
    targets = [n for system in systems for n in (animation_controls(system) if kind == 'ctrl' else members(system, 'joints'))]
    saved_time = mc.currentTime(q=True)
    mc.undoInfo(openChunk=True, chunkName='BakeLocalRope')
    error = None
    try:
        if kind == 'ctrl':
            for node in targets:
                attrs = animation_attributes(node)
                if attrs:
                    mc.bakeResults(node, t=(start, end), at=attrs, simulation=True, sampleBy=1,
                                   preserveOutsideKeys=True)
        else:
            samples = []
            for frame in range(int(math.floor(start)), int(math.ceil(end)) + 1):
                mc.currentTime(frame, update=True)
                samples.append((frame, [(mc.getAttr(n + '.translate')[0], mc.getAttr(n + '.rotate')[0]) for n in targets]))
            for system in systems:
                connections = json.loads(mc.getAttr(system + '.bakeConnections'))
                for joint in members(system, 'joints'):
                    for attribute in ('translate', 'rotate'):
                        dest = joint + '.' + attribute
                        sources = mc.listConnections(dest, s=True, d=False, plugs=True) or []
                        if sources:
                            connections[dest] = sources[0]
                            mc.disconnectAttr(sources[0], dest)
                mc.setAttr(system + '.bakeConnections', json.dumps(connections), type='string')
            for frame, values in samples:
                for node, (translate, rotate) in zip(targets, values):
                    for prefix, vector in (('t', translate), ('r', rotate)):
                        for axis, value in zip('xyz', vector):
                            mc.setKeyframe(node, at=prefix + axis, t=frame, v=value)
            mc.filterCurve([n + '.rotate' + a for n in targets for a in 'XYZ'])
    except Exception as exc:
        error = exc
    finally:
        mc.currentTime(saved_time, update=True)
        mc.undoInfo(closeChunk=True)
    if error:
        mc.undo()
        raise RuntimeError('Local bake rolled back: %s' % error)
    return True


def freeze_for_delete(system):
    """Detach deformation outputs before deleting upstream curve nodes."""
    skins = members(system, 'modelSkins')
    if skins:
        mc.delete([n for n in skins if mc.objExists(n)])
    for joint in members(system, 'joints'):
        for attribute in ('translate', 'rotate'):
            dest = joint + '.' + attribute
            value = mc.getAttr(dest)[0]
            sources = mc.listConnections(dest, s=True, d=False, plugs=True) or []
            if len(sources) == 1 and mc.isConnected(sources[0], dest):
                mc.disconnectAttr(sources[0], dest)
                mc.setAttr(dest, *value)
    root = system[:-len('_local_system')] + '_spline_rig_grp'
    prefix = system[:-len('_local_system')] + '_local_sample_'
    for node in reversed(members(root, 'splineikOwnedNodes')):
        if node.split('|')[-1].startswith(prefix) and mc.objExists(node):
            mc.delete(node)


def clear_animation(kind):
    systems = selected_systems()
    if not systems:
        return False
    mc.undoInfo(openChunk=True, chunkName='ClearLocalRopeAnimation')
    try:
        for system in systems:
            if kind == 'ctrl':
                for ctrl in animation_controls(system):
                    for attr in animation_attributes(ctrl):
                        mc.cutKey(ctrl, at=attr, clear=True)
                        default = mc.attributeQuery(attr, node=ctrl, listDefault=True)[0]
                        mc.setAttr(ctrl + '.' + attr, default)
            else:
                connections = json.loads(mc.getAttr(system + '.bakeConnections'))
                for dest, source in connections.items():
                    mc.cutKey(dest, clear=True)
                    mc.connectAttr(source, dest, f=True)
                mc.setAttr(system + '.bakeConnections', '{}', type='string')
    finally:
        mc.undoInfo(closeChunk=True)
    return True
