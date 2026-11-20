#coding:utf-8


import maya.cmds as mc
import maya.mel as mel
import maya.OpenMaya as om

class ik(object):
    # 复制所选曲线修改的名字
    def copy_curve_Name(self,name,cur):
        self.copy_cur_name=name+'_drv_crv'
        return self.copy_cur_name        
    # 创建蒙皮骨骼名字
    def joint_Name(self,name,cur,jnt):
        self.jnt_Name=[]
        for i in range(int(jnt)):
            self.jnt_Name.append(name+'_jnt_%s'%str(i+1))
        return self.jnt_Name
    # 创建蒙皮骨骼名字2
    def joint_Name2(self,name,cur,jnt):
        self.jnt_Name2=[]
        for i in range(int(jnt)):
            self.jnt_Name2.append(name+'_jnt_rig_%s'%str(i+1))
    # 创建蒙皮路径节点名字
    def motionpath_Name(self,name,cur,jnt):
        self.path_Name=[]
        for i in range(int(jnt)):
            self.path_Name.append(name+'_path_%s'%str(i+1))
        return self.path_Name
    # 创建蒙皮测距节点名字
    def distanceBetween_Name(self,name,cur,jnt):
        self.distance_Name=[]
        for i in range(int(jnt-1)):
            self.distance_Name.append(name+'_distance_%s'%str(i+1))
        return self.distance_Name
    # 创建测距的乘除节点的名字
    def multiplyDivide_distanceBetween_Name(self,name,cur,jnt):
        self.md_distance_Name=[]
        for i in range(int(jnt-1)):
            self.md_distance_Name.append(name+'_md_distance_%s'%str(i+1))
    # 创建测距的乘除节点
    def multiplyDivide_distanceBetween(self,name,cur,jnt):
        self.multiplyDivide_distanceBetween_Name(name,cur,jnt)
        for i in self.md_distance_Name:
            mc.createNode('multiplyDivide',n=i)
    # 创建缩放倍率的节点
    def scale_(self,name,cur,jnt):
        self.scale_cur_Name=name+'_scale_crv'
        mc.duplicate(cur,rr=1,n=self.scale_cur_Name,)
        for i in mc.listAttr(self.scale_cur_Name,k=1):
                mc.setAttr(self.scale_cur_Name+'.%s'%i,l=0)
        mc.makeIdentity(self.scale_cur_Name,apply=1,t=1,r=1,s=1,n=0)
        self.scale_info_Name=name+'_cur_scale_info'
        mc.createNode('curveInfo',n=self.scale_info_Name)
        scale_curshape=mc.listRelatives(self.scale_cur_Name,s=1)
        mc.connectAttr(scale_curshape[0]+'.worldSpace[0]',self.scale_info_Name+'.inputCurve',f=1)
        self.scale_md_Name=name+'_cur_scale_md'
        mc.createNode('multiplyDivide',n=self.scale_md_Name)
        mc.setAttr(self.scale_md_Name+'.operation',2)
        mc.connectAttr(self.scale_info_Name+'.arcLength',self.scale_md_Name+'.input2X',f=1)
        input1X=mc.getAttr(self.scale_info_Name+'.arcLength')
        mc.setAttr(self.scale_md_Name+'.input1X',input1X)
        mc.setAttr(self.scale_cur_Name+'.inheritsTransform',l=1)   
    # 创建拉伸节点的名字
    def name_stretch(self,name,jnt):
        self.stretch_name=[]
        for i  in range(int(jnt-1)):
            self.stretch_name.append(name+'_stretch_%s'%str(i+1))
    # 创建拉伸节点
    def stretch(self,name,jnt):
        self.name_stretch(name,jnt)
        for i in self.stretch_name:
            mc.createNode('setRange',n=i)
    # 创建控制器校轴参考物体的名字
    def defined_loc_Name(self,name,quantity):
        self.defined_lc_Name=[]
        for i in range(int(quantity)):
            self.defined_lc_Name.append(name+'_defined_lc_%s'%str(i+1))
        return self.defined_lc_Name
    # 创建控制器校轴参考物体模板的名字
    def defined_loc_mould_Name(self):
        return 'defined_lc'
    # 创建自定义loc模板
    def defined_loc_mould(self):
        name=self.defined_loc_mould_Name() 
        mc.curve(d=1,p=[(1,0,0),(2.8,0,0),(2.8,0.5,0),(3.8,0,0),
                 (2.8,-0.5,0),(2.8,0,0),(2.8,0,0.5),
                 (3.8,0,0),(2.8,0,-0.5),(2.8,0,0)],n="lc_x")
        shape=mc.listRelatives("lc_x",s=1)
        mc.rename(shape,"lc_x"+"shape")
        mc.setAttr("lc_xshape.overrideEnabled",1)
        mc.setAttr("lc_xshape.overrideColor",13)
        mc.duplicate("lc_x",rr=1,n="lc_y")
        mc.setAttr('lc_y.rz',90)
        mc.setAttr("lc_yshape.overrideEnabled",1)
        mc.setAttr("lc_yshape.overrideColor",14)
        mc.duplicate("lc_x",rr=1,n="lc_z")
        mc.setAttr('lc_z.ry',-90)
        mc.setAttr("lc_zshape.overrideEnabled",1)
        mc.setAttr("lc_zshape.overrideColor",6)
        mc.makeIdentity('lc_y',apply=1,t=1,r=1,s=1,n=0)
        mc.makeIdentity('lc_z',apply=1,t=1,r=1,s=1,n=0)
        mc.curve(d=1,p=[(0.0,1,0), (0,0,1), (0,0,0),(1,0,0),
                (0,1,0),(0,0,0),(0,0,1),(1,0,0)],n=name)
        shape=mc.listRelatives(name,s=1)
        mc.rename(shape,name+"shape")
        mc.setAttr(name+"shape.overrideEnabled",1)
        mc.setAttr(name+"shape.overrideColor",16)
        mc.parent('lc_xshape','lc_yshape','lc_zshape',name,add=1,s=1)
        mc.delete('lc_x','lc_y','lc_z')
    # 控制器名字
    def regulator_Name(self,name,quantity):
        self.sa_regulator=[]
        
        for i in range(int(quantity)):
            self.sa_regulator.append(name+'_%s'%(i+1))
        return self.sa_regulator
    # 创建 dynamic控制器
    def dynamic(self,name):
        self.dynamic_name=name+'_dyn'
        mc.textCurves(t=self.dynamic_name,f='Courier',n=name+'_dyn_grp')
        mc.setAttr(name+'_dyn_grpShape.sx',0.3)
        mc.setAttr(name+'_dyn_grpShape.sy',0.3)
        mc.setAttr(name+'_dyn_grpShape.sz',0.3)
        grpShape=mc.listRelatives(name+'_dyn_grpShape')
        dycur=[]
        dycurshape=[]
        for i in grpShape:
            mc.listRelatives(i)
            for i2 in mc.listRelatives(i):
                dycur.append(i2)
                dycurshape.append(mc.listRelatives(i2)[0])
        mc.parent(dycur,w=1)
        mc.makeIdentity(dycur,apply=1,t=1,r=1,s=1,n=0)
        mc.select(dycur)
        mc.DeleteHistory()
        mc.parent(dycurshape[1:],dycur[0],add=1,s=1)
        mc.delete(name+'_dyn_grpShape',dycur[1:])
        mc.rename(dycur[0],self.dynamic_name)
        newshape=mc.listRelatives(self.dynamic_name,s=1)
        for i in newshape:
            mc.setAttr(i+'.overrideEnabled',1)
            mc.setAttr(i+'.overrideColor',17)
        for i in range(len(newshape)):
            mc.rename(newshape[i],self.dynamic_name+'_Shape')
        mc.addAttr(self.dynamic_name,dt='string',ln='Category')
        mc.setAttr(self.dynamic_name+'.Category',l=1)
        mc.addAttr(self.dynamic_name,ln='simulationMethod',at='enum',en='off:Static:Dynamic Follicles Only:All Follicles:',k=1,dv=1)
        mc.addAttr(self.dynamic_name,ln='stiffness',at='double',k=1,dv=0.15)
        mc.addAttr(self.dynamic_name,ln='damp',at='double',k=1,dv=0.0)
        mc.addAttr(self.dynamic_name,ln='drag',at='double',k=1,dv=0.1)
        mc.addAttr(self.dynamic_name,ln='friction',at='double',k=1,dv=0.1)
        mc.addAttr(self.dynamic_name,ln='mass',at='double',k=1,dv=1)
        mc.addAttr(self.dynamic_name,ln='startCurveAttract',at='double',k=1,dv=0.5)
        mc.addAttr(self.dynamic_name,ln='gravity',at='double',k=1,dv=0.98)
        mc.addAttr(self.dynamic_name,ln='startFrame',at='double',k=1,dv=1)
        mc.addAttr(self.dynamic_name,ln='iterations',at='double',k=1,dv=5)
        mc.addAttr(self.dynamic_name,ln='dynamic',at='double',k=0,dv=0)
    # 创建方形控制器形状
    def square_shape(self,name):
        square_cur_name=mc.curve(d=1,p=[(-1.0, 1.0, 1.0), (-1.0, 1.0, -1.0), (1.0, 1.0, -1.0), 
                                 (1.0, 1.0, 1.0), (-1.0, 1.0, 1.0), (-1.0, -1.0, 1.0), 
                                 (-1.0, -1.0, -1.0), (-1.0, 1.0, -1.0), (-1.0, 1.0, 1.0), 
                                 (-1.0, -1.0, 1.0), (1.0, -1.0, 1.0), (1.0, 1.0, 1.0), 
                                 (1.0, 1.0, -1.0), (1.0, -1.0, -1.0), (1.0, -1.0, 1.0), 
                                 (1.0, -1.0, -1.0), (-1.0, -1.0, -1.0)],n=name)
        square_cur_name_shape=mc.listRelatives(square_cur_name,s=1)[0]
        mc.rename(square_cur_name_shape,square_cur_name+'Shape')
        mc.addAttr(square_cur_name,dt='string',ln='Category')
        mc.setAttr(square_cur_name+'.Category',l=1)
        return square_cur_name
    # 创建飞镖形控制器
    def cross_shape(self,name):
        cross_cur_name=mc.curve(d=1,p=[(0,0,0),(-0.38,0.38,0),(0,2,0),(0.38,0.38,0),(0,0,0),
                                (0.38,0.38,0),(2,0,0),(0.38,-0.38,0),(0,0,0),
                                (0.38,-0.38,0),(0,-2,0),(-0.38,-0.38,0),(0,0,0),
                                (-0.38,-0.38,0),(-2,0,0),(-0.38,0.38,0),(0,0,0),
                                (0,0.38,0.38),(0,2,0),(0,0.38,-0.38),(0,0,0),
                                (0,0.38,-0.38),(0,0,-2),(0,-0.38,-0.38),(0,0,0),
                                (0,-0.38,-0.38),(0,-2,0),(0,-0.38,0.38),(0,0,0),
                                (0,-0.38,0.38),(0,0,2),(0,0.38,0.38)],n=name)
        shape=mc.listRelatives(cross_cur_name,s=1)[0]
        mc.setAttr(shape+'.overrideEnabled',1)
        mc.setAttr(shape+'.overrideColor',21)
        mc.rename(shape,cross_cur_name+'Shape')
        mc.addAttr(cross_cur_name,dt='string',ln='Category')
        mc.setAttr(cross_cur_name+'.Category',l=1)
        return cross_cur_name
    # 创建BAKE控制器
    def bake_shape(self,name):
        bake_cur_name=mc.curve(d=1,p=[(0,1,0),(0,-1,0),(0,0,0),(0,0,1),(0,0,-1),
                               (0,0,0),(1,0,0),(-1,0,0)],n=name)
        shape=mc.listRelatives(bake_cur_name,s=1)[0]
        mc.setAttr(shape+'.overrideEnabled',1)
        mc.setAttr(shape+'.overrideColor',25)
        mc.rename(shape,bake_cur_name+'Shape')
        return bake_cur_name
               
    # 创建控制器
    def regulator(self,name,quantity):
        sacv=self.regulator_Name(name,quantity)
        self.regulator_bake=[]
        self.regulator_cross=[]
        for i in sacv:
            bake_cur=i+'_bake'
            self.regulator_bake.append(bake_cur)
            bake_cur_s=bake_cur+'_s'
            self.bake_shape(bake_cur_s)
            mc.select(cl=1)
            mc.joint(n=bake_cur,p=(0,0,0))
            sa=mc.listRelatives(bake_cur_s,s=1)
            mc.parent(sa[0],bake_cur,add=1,s=1)
            sb=mc.listRelatives(bake_cur,s=1)
            mc.rename(sb,bake_cur+"Shape")
            mc.delete(bake_cur_s)
            mc.setAttr(bake_cur+'.drawStyle',2)
            bake_cur_grp=mc.group(bake_cur,n=bake_cur+'_grp')
            mc.setAttr(bake_cur+'.radi',0,l=1,k=0,channelBox=0)

            
            cross_cur=i+'_bendback'
            self.cross_shape(cross_cur)
            cross_cur_grp=mc.group(cross_cur,n=cross_cur+'_grp')
            mc.parent(bake_cur_grp,cross_cur)
            self.regulator_cross.append(cross_cur)
            
            square_cur=i
            self.square_shape(square_cur)
            square_cur_grp=mc.group(square_cur,n=square_cur+'_grp')
            mc.parent(cross_cur_grp,square_cur)
            
            mc.addAttr(i,ln='follow',k=1,min=0,max=1)
            mc.setAttr(i+'.sx',l=1,k=0)
            mc.setAttr(i+'.sy',l=1,k=0)
            mc.setAttr(i+'.sz',l=1,k=0)
            mc.setAttr(i+'.v',l=1,k=0)
            #mc.setAttr(i+'.radi',0,l=1,k=0,channelBox=0)
            mc.addAttr(i,ln='order',at='enum',k=1,en='xyz:yzx:zxy:xyz:yxz:zyx:',dv=1)
            mc.connectAttr(i+'.order',i+'.rotateOrder')
            
            mc.connectAttr(i+'.order',bake_cur+'.rotateOrder')
            mc.connectAttr(i+'.order',bake_cur_grp+'.rotateOrder')
            mc.connectAttr(i+'.order',cross_cur+'.rotateOrder')
            mc.connectAttr(i+'.order',cross_cur_grp+'.rotateOrder')

            mc.group(square_cur_grp,n='Totality_'+i)
            
            #mc.select(cl=1)
            #mc.group(n=i+'_rotate',em=1)
            #mc.parent(i+'_rotate','Totality_'+i)
            #mc.orientConstraint(i,i+'_rotate',w=1,mo=1)                  
    # 复制所选曲线__dynamic创建
    def copy_cur(self,name,cur,dyopen):
        sa_copy_cur=self.copy_curve_Name(name,cur)
        if int(dyopen)==0:
            mc.duplicate(cur,n=sa_copy_cur)
            for i in mc.listAttr(sa_copy_cur,k=1):
                mc.setAttr(sa_copy_cur+'.%s'%i,l=0)
            mc.makeIdentity(sa_copy_cur,apply=1,t=1,r=1,s=1,n=0)
            self.spikcur=sa_copy_cur
        else:
            mc.duplicate(cur,n=sa_copy_cur)
            for i in mc.listAttr(sa_copy_cur,k=1):
                mc.setAttr(sa_copy_cur+'.%s'%i,l=0)
            mc.makeIdentity(sa_copy_cur,apply=1,t=1,r=1,s=1,n=0)
            mc.select(sa_copy_cur)
            mel.eval('makeCurvesDynamicHairs 1 0 1')
            hairshape=mc.ls(sl=1)[0]
            self.newhairName=name+'_hair'
            mc.rename(mc.listRelatives(hairshape,p=1),self.newhairName)
            list=mc.listHistory(mc.listRelatives(self.newhairName,s=1)[0],f=1)
            for i in list:
                if 'nucleus' in i:
                    mc.setAttr(i+'.enable',0)
                    mc.setAttr(mc.listRelatives(self.newhairName,s=1)[0]+'.active',0)
                    mc.delete(i)
                    list.remove(i)
            for i in list:
                if mc.objectType(i)=='nurbsCurve':
                    mc.rename(mc.listRelatives(i,p=1),name+'_ouputCrv')
                    list.remove(i)
            for i in list:
                if 'foll' in i:
                    mc.rename(mc.listRelatives(i,p=1),name+'_fol')
            hair_grp=mc.listRelatives(name+'_fol',p=1)
            mc.setAttr(mc.listRelatives(name+'_fol',s=1)[0]+'.pointLock',1)
            folgrp=mc.listRelatives(name+'_fol',ap=1)
            curgrp=mc.listRelatives(name+'_ouputCrv',ap=1)
            mc.parent(name+'_fol',name+'_ouputCrv',w=1)
            try:
                mc.delete(hair_grp,curgrp)
            except:
                mc.delete(curgrp)
            self.dyn_hair_grp=name+'_dyn_hair_grp'            
            mc.group(name+'_hair',name+'_fol',name+'_ouputCrv',n=self.dyn_hair_grp)            
            self.dynamic(name)
            hairShape_name=mc.listRelatives(self.newhairName,s=1)[0]
            mc.connectAttr(self.dynamic_name+'.simulationMethod',hairShape_name+'.simulationMethod',f=1)
            mc.connectAttr(self.dynamic_name+'.stiffness',hairShape_name+'.stiffness',f=1)
            mc.connectAttr(self.dynamic_name+'.damp',hairShape_name+'.damp',f=1)
            mc.connectAttr(self.dynamic_name+'.drag',hairShape_name+'.drag',f=1)
            mc.connectAttr(self.dynamic_name+'.friction',hairShape_name+'.friction',f=1)
            mc.connectAttr(self.dynamic_name+'.mass',hairShape_name+'.mass',f=1)
            mc.connectAttr(self.dynamic_name+'.startCurveAttract',hairShape_name+'.startCurveAttract',f=1)
            mc.connectAttr(self.dynamic_name+'.gravity',hairShape_name+'.gravity',f=1)
            mc.connectAttr(self.dynamic_name+'.startFrame',hairShape_name+'.startFrame',f=1)
            mc.connectAttr(self.dynamic_name+'.iterations',hairShape_name+'.iterations',f=1)
            mc.setAttr(hairShape_name+'.stiffnessScale[1].stiffnessScale_Position',1)
            mc.setAttr(hairShape_name+'.stiffnessScale[1].stiffnessScale_FloatValue',0.2)
            mc.addAttr(self.dynamic_name,ln=self.dynamic_name+'_'+hairShape_name,at='double',k=0,dv=0)
            mc.setAttr(self.newhairName+'.inheritsTransform',0)
            mc.setAttr(self.newhairName+'.inheritsTransform',l=1)
            mc.setAttr(name+'_fol'+'.inheritsTransform',0)
            mc.setAttr(name+'_fol'+'.inheritsTransform',l=1)
            mc.setAttr(name+'_ouputCrv'+'.inheritsTransform',0)
            mc.setAttr(name+'_ouputCrv'+'.inheritsTransform',l=1)
    # 计算参考物体的缩放大小
    def defined_loc_scale(self,cur):
        a=mc.createNode('curveInfo',n=cur+'_info')
        shape=mc.listRelatives(cur,s=1)[0]
        mc.connectAttr(shape+'.worldSpace',cur+'_info.inputCurve')
        self.loc_scale=mc.getAttr(cur+'_info.arcLength')*0.03
        mc.delete(cur+'_info')
        
    # 创建控制器校轴参考物体
    def connect_defined_loc_curve(self,name,cur,jnt,x,y,quantity):
        self.defined_loc_scale(cur)
        defined_path_Name=[]
        for i in range(int(quantity)):
            defined_path_Name.append(name+'_defined_path_%s'%str(i+1))
        xyz=['x','y','z']
        fa=xyz.index(x)
        ua=xyz.index(y)
        for i in range(int(quantity)):
            mc.createNode('motionPath',n=defined_path_Name[i])
            mc.setAttr(defined_path_Name[i]+'.uValue',1/(quantity-1.0)*i)
            mc.setAttr(defined_path_Name[i]+'.fractionMode',1)
            mc.setAttr(defined_path_Name[i]+'.frontAxis',fa)
            mc.setAttr(defined_path_Name[i]+'.upAxis',ua)
        shapes=mc.listRelatives(cur,s=1)
        for i in defined_path_Name:
            mc.connectAttr(shapes[0]+".worldSpace",i+'.geometryPath',f=1)
        self.defined_loc_mould()
        sa_defined_loc=self.defined_loc_Name(name,quantity)
        sa_defined_lc_Name=self.defined_loc_mould_Name()
        for i in sa_defined_loc:
            mc.duplicate(sa_defined_lc_Name,n=i)
            i_shape=mc.listRelatives(i,s=1)
            mc.rename(i+'|'+i_shape[1],i+'_lc_xshape')
            mc.rename(i+'|'+i_shape[2],i+'_lc_yshape')
            mc.rename(i+'|'+i_shape[3],i+'_lc_zshape')         
        for i in range(int(quantity)):
            mc.connectAttr(defined_path_Name[i]+'.allCoordinates',sa_defined_loc[i]+'.translate')
            mc.connectAttr(defined_path_Name[i]+'.rotate',sa_defined_loc[i]+'.rotate')
            mc.disconnectAttr(defined_path_Name[i]+'.allCoordinates',sa_defined_loc[i]+'.translate')
            mc.disconnectAttr(defined_path_Name[i]+'.rotate',sa_defined_loc[i]+'.rotate')
        mc.delete(defined_path_Name,sa_defined_lc_Name)
        for i in sa_defined_loc:
            mc.setAttr(i+'.sx',self.loc_scale)
            mc.setAttr(i+'.sy',self.loc_scale)
            mc.setAttr(i+'.sz',self.loc_scale)            
        self.jnt_reference_loc(name,cur,jnt,x,y,quantity)
    # 创建骨骼参考物体和path的名字
    def jnt_reference_loc_name_path(self,name,cur,jnt):
        self.jnt_reference_loc_name=[]
        self.jnt_reference_loc_name_grp=name+'_jnt_reference_grp'
        self.jnt_reference_loc_path=[]
        for i in range(int(jnt)):
            self.jnt_reference_loc_name.append(name+'_jnt_reference_%s'%str(i+1))
            self.jnt_reference_loc_path.append(name+'_jnt_reference_path%s'%str(i+1))
        
    # 创建骨骼参考物体
    def jnt_reference_loc(self,name,cur,jnt,x,y,quantity):
        self.jnt_reference_loc_name_path(name,cur,jnt)
        for i in range(int(jnt)):
            mc.spaceLocator(p=[0,0,0],n=self.jnt_reference_loc_name[i])
            mc.addAttr(self.jnt_reference_loc_name[i],ln='Position',at='double',k=1)
            mc.addAttr(self.jnt_reference_loc_name[i],ln='oldPosition',at='double',k=1)
        mc.group(self.jnt_reference_loc_name,n=self.jnt_reference_loc_name_grp)
        xyz=['x','y','z']
        fa=xyz.index(x)
        ua=xyz.index(y)
        for i in range(int(jnt)):
            mc.createNode('motionPath',n=self.jnt_reference_loc_path[i])
            mc.setAttr(self.jnt_reference_loc_path[i]+'.uValue',1/(jnt-1.0)*i)
            mc.setAttr(self.jnt_reference_loc_path[i]+'.fractionMode',1)
            mc.setAttr(self.jnt_reference_loc_path[i]+'.frontAxis',fa)
            mc.setAttr(self.jnt_reference_loc_path[i]+'.upAxis',ua)
        shapes=mc.listRelatives(cur,s=1)
        for i in self.jnt_reference_loc_path:
            mc.connectAttr(shapes[0]+".worldSpace",i+'.geometryPath',f=1)
        for i in range(int(jnt)):
            mc.connectAttr(self.jnt_reference_loc_path[i]+'.allCoordinates',self.jnt_reference_loc_name[i]+'.translate')
            mc.connectAttr(self.jnt_reference_loc_path[i]+'.rotate',self.jnt_reference_loc_name[i]+'.rotate')
            mc.setAttr(self.jnt_reference_loc_name[i]+'.localScaleX',self.loc_scale)
            mc.setAttr(self.jnt_reference_loc_name[i]+'.localScaleY',self.loc_scale)
            mc.setAttr(self.jnt_reference_loc_name[i]+'.localScaleZ',self.loc_scale)
            pos=mc.getAttr(self.jnt_reference_loc_path[i]+'.uValue')
            mc.setAttr(self.jnt_reference_loc_name[i]+'.Position',pos)
            mc.setAttr(self.jnt_reference_loc_name[i]+'.oldPosition',pos)
            mc.setAttr(self.jnt_reference_loc_name[i]+'.oldPosition',l=1)
            mc.connectAttr(self.jnt_reference_loc_name[i]+'.Position',self.jnt_reference_loc_path[i]+'.uValue')
    # 创建splineik和骨骼连
    def splineik(self,name,cur,jnt,x,y,dyopen,object_scale):
        self.copy_cur(name,cur,dyopen)
        if int(dyopen)==0:
            sa_copy_cur=self.copy_curve_Name(name,cur)
        else:
            sa_copy_cur=name+'_ouputCrv'
        sa_jnt=self.joint_Name(name,cur,jnt)
        mc.curve(d=1,p=[(0,0,0),(1,0,0)],n=name+'_jnt_cur')
        mc.createNode('motionPath',n=name+'_jnt_path')
        shapes=mc.listRelatives(sa_copy_cur,s=1)
        mc.connectAttr(shapes[0]+".worldSpace",name+'_jnt_path'+'.geometryPath',f=1)
        xyz=['x','y','z']
        fa=xyz.index(x)
        ua=xyz.index(y)
        mc.setAttr(name+'_jnt_path.frontAxis',fa)
        mc.setAttr(name+'_jnt_path.upAxis',ua)                
        mc.select(cl=1)
        for i in range(len(sa_jnt)):
            mc.select(cl=1)
            mc.joint(p=(0,0,0),n=sa_jnt[i])
            mc.connectAttr(name+'_jnt_path.rotate',sa_jnt[i]+'.rotate',f=1)
        mc.delete(name+'_jnt_cur',name+'_jnt_path')
        for i in range(len(sa_jnt)-1):
            mc.parent(sa_jnt[i+1],sa_jnt[i])
        self.ikHandleName=name+"_ikHandle"
        mc.makeIdentity(sa_jnt[0],apply=1,r=1)
        ik_Handle=mc.ikHandle(sj=sa_jnt[0],ee=sa_jnt[-1],
                              sol="ikSplineSolver",ccv=0,pcv=0,roc=1,cra=0,snc=0,
                              curve=sa_copy_cur,n=self.ikHandleName)
        mc.rename(ik_Handle[1],name+'_effector')
        if object_scale!=0:
            self.splineik_jnt2(name,cur,jnt)
        else:
            for i in sa_jnt:
                mc.addAttr(i,ln='Position',at='double',k=1)
                mc.addAttr(i,ln='oldPosition',at='double',k=1)
                mc.setAttr(i+'.Position',k=0,channelBox=1)
    # 创建骨骼链2
    def splineik_jnt2(self,name,cur,jnt):
        self.joint_Name2(name,cur,jnt)
        self.joint_Name2_grp=[]
        for i in range(len(self.jnt_Name2)):
            mc.select(cl=1)
            mc.joint(p=(0,0,0),n=self.jnt_Name2[i])
            mc.group(self.jnt_Name2[i],n=self.jnt_Name2[i]+'_grp')
            mc.parentConstraint(self.jnt_Name[i],self.jnt_Name2[i]+'_grp',w=1,mo=0)
            self.joint_Name2_grp.append(self.jnt_Name2[i]+'_grp')
            mc.addAttr(self.jnt_Name2[i],ln='Position',at='double',k=1)
            mc.addAttr(self.jnt_Name2[i],ln='oldPosition',at='double',k=1)   
    # 创建蒙皮路径节点
    def motionpathik(self,name,cur,jnt,dyopen,category):
        sa_copy_cur=self.copy_curve_Name(name,cur)
        sa_path=self.motionpath_Name(name,cur,jnt)
        self.jnt_reference_loc_name_path(name,cur,jnt)
        if int(dyopen)==0:
            shapes=mc.listRelatives(sa_copy_cur,s=1)
        else:
            shapes=mc.listRelatives(name+'_ouputCrv',s=1)
        if category==1:
            for i in range(int(jnt)):
                mc.createNode('motionPath',n=sa_path[i])
                pos=mc.getAttr(self.jnt_reference_loc_name[i]+'.Position')
                mc.setAttr(sa_path[i]+'.uValue',pos)
                mc.setAttr(sa_path[i]+'.fractionMode',1)
            for i in sa_path:
                mc.connectAttr(shapes[0]+".worldSpace",i+'.geometryPath',f=1)
        else :
            import pymel.core as pm
            node = pm.PyNode(shapes[0])
            self.sa_path_parameter=[]
            for i in range(int(jnt)):
                pos=mc.xform(self.jnt_reference_loc_name[i],q=1,ws=1,t=1)
                closet=node.closestPoint(pos)
                closet_parameter=node.getParamAtPoint(closet)
                mc.createNode('pointOnCurveInfo',n=sa_path[i])
                mc.connectAttr(shapes[0]+'.worldSpace',sa_path[i]+'.inputCurve',f=1)
                mc.setAttr(sa_path[i]+'.turnOnPercentage',0)
                mc.setAttr(sa_path[i]+'.parameter',closet_parameter)
                
                
                
                

    # 创建蒙皮测距节点
    def distanceBetween(self,name,cur,jnt):
        sa_distance=self.distanceBetween_Name(name,cur,jnt)
        for i in sa_distance:
            mc.createNode('distanceBetween',n=i)
    # 关联蒙皮路径节点,测距节点
    def connect_path_distance(self,name,cur,jnt,dyopen,category):
        self.sa_motionpath=self.motionpath_Name(name,cur,jnt)
        self.sa_distance=self.distanceBetween_Name(name,cur,jnt)        
        self.motionpathik(name,cur,jnt,dyopen,category)        
        self.distanceBetween(name,cur,jnt)
        if category==1:                
            for i in range(int(jnt-1)):
                mc.connectAttr(self.sa_motionpath[i]+'.allCoordinates',self.sa_distance[i]+'.point1',f=1)
                mc.connectAttr(self.sa_motionpath[i+1]+'.allCoordinates',self.sa_distance[i]+'.point2',f=1)
        else:
            for i in range(int(jnt-1)):
                mc.connectAttr(self.sa_motionpath[i]+'.position',self.sa_distance[i]+'.point1',f=1)
                mc.connectAttr(self.sa_motionpath[i+1]+'.position',self.sa_distance[i]+'.point2',f=1)
    # 关联测距节点，拉伸节点
    def connect_distance_stretch(self,name,cur,jnt,dyopen,category):
        self.connect_path_distance(name,cur,jnt,dyopen,category)
        self.stretch(name,jnt)
        for i in range(int(jnt-1)):
            mc.connectAttr(self.sa_distance[i]+'.distance',self.stretch_name[i]+'.maxX',f=1)
            pos=mc.getAttr(self.sa_distance[i]+'.distance')
            mc.setAttr(self.stretch_name[i]+'.minX',pos)
            mc.setAttr(self.stretch_name[i]+'.oldMinX',0)
            mc.setAttr(self.stretch_name[i]+'.oldMaxX',10)             
    # 关联测距节点的缩放值
    def connect_distance_scale(self,name,cur,jnt,dyopen,category):
        self.connect_distance_stretch(name,cur,jnt,dyopen,category)
        self.multiplyDivide_distanceBetween(name,cur,jnt)
        self.scale_(name,cur,jnt)
        for i in range(len(self.md_distance_Name)):
            mc.connectAttr(self.scale_md_Name+'.outputX',self.md_distance_Name[i]+'.input1X')
            mc.connectAttr(self.stretch_name[i]+'.outValueX',self.md_distance_Name[i]+'.input2X')                                
    # 关联蒙皮测距节点，骨骼连
    def connect_joint(self,name,cur,jnt,x,y,dyopen,category,object_scale):
        self.splineik(name,cur,jnt,x,y,dyopen,object_scale)
        self.connect_distance_scale(name,cur,jnt,dyopen,category)
        sa_jnt=self.joint_Name(name,cur,jnt)
        sa_distance=self.distanceBetween_Name(name,cur,jnt)      
        for i in range(int(jnt-1)):
            mc.addAttr(sa_jnt[i+1],ln='distaince_%s'%x,at='double',k=1)
            mc.setAttr(sa_jnt[i+1]+'.distaince_%s'%x,k=1,channelBox=1)
            mc.connectAttr(self.md_distance_Name[i]+'.outputX',sa_jnt[i+1]+'.distaince_%s'%x)
            mc.connectAttr(sa_jnt[i+1]+'.distaince_%s'%x,sa_jnt[i+1]+'.t'+x)
            #mc.connectAttr(self.md_distance_Name[i]+'.outputX',sa_jnt[i+1]+'.t'+x,f=1)
        self.connect_stretch(name,jnt,x)
    # 关联拉伸节点的缩放
    def connect_stretch(self,name,jnt,x):
        sacle_info=name+'_cur_scale_info'
        jnt_name=[]
        stretch_name=[]
        for i in range(int(jnt)):
            jnt_name.append(name+'_jnt_%s'%str(i+1))
            stretch_name.append(name+'_stretch_%s'%str(i+1))
        mp1=mc.createNode('multiplyDivide',n=name+'_stretch_mp')
        mc.setAttr(mp1+'.operation',2)
        length=mc.getAttr(sacle_info+'.arcLength')
        mc.setAttr(mp1+'.input2X',length)
        mc.connectAttr(sacle_info+'.arcLength',mp1+'.input1X')
        for i in range(int(jnt-1)):
            mp2=mc.createNode('multiplyDivide',n=jnt_name[i]+'_stretch_scale_mp')
            mc.connectAttr(mp1+'.outputX',mp2+'.input1X')
            pos=mc.getAttr(jnt_name[i+1]+'.t'+x)
            mc.setAttr(mp2+'.input2X',pos)
            mc.connectAttr(mp2+'.outputX',stretch_name[i]+'.minX')
    
    # 骨骼关联测距节点
    def connect_jont_distance(self,name,cur,jnt,category,object_scale):
        sa_path=self.motionpath_Name(name,cur,jnt)
        sa_jnt=self.joint_Name(name,cur,jnt)
        self.joint_Name2(name,cur,jnt)
        if object_scale!=0:
            sa_jnt=self.jnt_Name2
        else:
            sa_jnt=self.joint_Name(name,cur,jnt)
        if category==1:
            for i in range(len(self.path_Name)):
                pos=mc.getAttr(sa_path[i]+'.uValue')
                mc.setAttr(sa_jnt[i]+'.Position',pos)
                mc.setAttr(sa_jnt[i]+'.oldPosition',pos)
                mc.setAttr(sa_jnt[i]+'.oldPosition',l=1)
                mc.connectAttr(sa_jnt[i]+'.Position',sa_path[i]+'.uValue',f=1)
        else:
            for i in range(len(self.path_Name)):
                pos=mc.getAttr(sa_path[i]+'.parameter')
                mc.setAttr(sa_jnt[i]+'.Position',pos)
                mc.setAttr(sa_jnt[i]+'.oldPosition',pos)
                mc.setAttr(sa_jnt[i]+'.oldPosition',l=1)
                mc.connectAttr(sa_jnt[i]+'.Position',sa_path[i]+'.parameter',f=1)
    # 建立层级构架
    def spline_rig_grp(self,name,cur,jnt,x,y,quantity,dyopen,object_scale,figure,category,stretching,path_open=0,path_count=50):
        owned_before=set(mc.ls(uuid=True))
        self.regulator(name,quantity)
        self.defined_loc_Name(name,quantity)
        self.regulator_Name(name,quantity)
        self.jnt_reference_loc_name_path(name,cur,jnt)
        self.sa_regulator_grp_scale=mc.getAttr(self.defined_lc_Name[0]+'.sx')
        for i in self.sa_regulator:
            mc.setAttr(i+'.sx',l=0,k=1)
            mc.setAttr(i+'.sy',l=0,k=1)
            mc.setAttr(i+'.sz',l=0,k=1)
            mc.setAttr(i+'.sx',self.sa_regulator_grp_scale)
            mc.setAttr(i+'.sy',self.sa_regulator_grp_scale)
            mc.setAttr(i+'.sz',self.sa_regulator_grp_scale)
            mc.makeIdentity(i,apply=1,t=0,r=0,s=1,n=0)
            mc.setAttr(i+'.sx',l=1,k=0)
            mc.setAttr(i+'.sy',l=1,k=0)
            mc.setAttr(i+'.sz',l=1,k=0)
        self.sa_regulator_grp=[]
        for i in self.sa_regulator:
            self.sa_regulator_grp.append('Totality_'+i)   
        self.sa_regulator_rotate=[]
        for i in self.sa_regulator:
            self.sa_regulator_rotate.append(i+'_rotate')
        for i in range(int(quantity)):
            mc.parentConstraint(self.defined_lc_Name[i],self.sa_regulator_grp[i],w=1,mo=0)
            mc.parentConstraint(self.defined_lc_Name[i],self.sa_regulator_grp[i],remove=1)
        for i in range(int(quantity-1)):
            #mc.parent(self.sa_regulator_grp[i+1],self.sa_regulator_rotate[i])
            mc.parent(self.sa_regulator_grp[i+1],self.sa_regulator[i])
        mc.group(n=name+'_spline_rig_grp',em=1)
        mc.group(n=name+'_world_grp',em=1)
        mc.setAttr(name+'_world_grp.v',0)
        mc.group(n=name+'_class_grp',em=1)
        mc.group(n=name+'_spIK_grp',em=1)
        mc.setAttr(name+'_spIK_grp.v',0)
        mc.group(n=name+'_skin_joint_grp',em=1)
        if object_scale!=0:
            mc.setAttr(name+'_skin_joint_grp.v',0)
            mc.group(n=name+'_jnt_rig_grp',em=1)
            mc.group(name+'_skin_joint_grp',name+'_jnt_rig_grp',n=name+'_joint_grp')
        else:
            mc.group(name+'_skin_joint_grp',n=name+'_joint_grp')
        mc.parent(name+'_world_grp',name+'_class_grp',name+'_spIK_grp',name+'_joint_grp',name+'_spline_rig_grp')
        mc.parentConstraint(self.defined_lc_Name[0],name+'_spline_rig_grp',w=1,mo=0)
        mc.parentConstraint(self.defined_lc_Name[0],name+'_spline_rig_grp',remove=1)
        mc.parent(self.sa_regulator_grp[0],name+'_class_grp')
        for i in self.sa_regulator:
            mc.group(n=i+'_world',em=1)
        for i in range(int(quantity)):
            mc.parentConstraint(self.defined_lc_Name[i],self.sa_regulator[i]+'_world',w=1,mo=0)
            mc.delete(self.sa_regulator[i]+'_world_parentConstraint1')
            mc.parent(self.sa_regulator[i]+'_world',name+'_world_grp')
            mc.parentConstraint(self.sa_regulator[i]+'_world',self.sa_regulator_grp[i],w=1,mo=1)
            mc.connectAttr(self.sa_regulator[i]+'.follow',self.sa_regulator_grp[i]+'_parentConstraint1.'+self.sa_regulator[i]+'_world'+'W0')
        for i in self.sa_regulator:
            mc.setAttr(i+'.overrideEnabled',1)
            mc.setAttr(i+'.overrideColor',17)
        mc.setAttr(self.sa_regulator[0]+'.overrideColor',13)
        self.connect_joint(name,cur,jnt,x,y,dyopen,category,object_scale)
        mc.group(self.copy_cur_name,n=self.copy_cur_name+'_grp')
        mc.setAttr(self.copy_cur_name+'.inheritsTransform',l=0)
        mc.setAttr(self.copy_cur_name+'.inheritsTransform',0)
        mc.setAttr(self.copy_cur_name+'.inheritsTransform',l=1)
        if int(dyopen)==0:
            mc.parent(self.scale_cur_Name,self.copy_cur_name+'_grp',self.ikHandleName,name+'_spIK_grp') 
            mc.makeIdentity(self.scale_cur_Name,apply=1,t=1,r=1,s=1,n=0)   
        else:
            mc.parent(self.scale_cur_Name,self.dyn_hair_grp,self.ikHandleName,name+'_spIK_grp')
            mc.makeIdentity(self.scale_cur_Name,apply=1,t=1,r=1,s=1,n=0)           
        mc.parent(self.jnt_Name[0],name+'_skin_joint_grp')
        mc.makeIdentity(self.jnt_Name[0],apply=1,r=1)
        if object_scale!=0:
            mc.parent(self.joint_Name2_grp,name+'_jnt_rig_grp')
        else:
            pass
        mc.skinCluster(self.regulator_bake,self.copy_cur_name)
        mc.createNode('plusMinusAverage',n=name+'_ikHandle_twist')
        self.sa_regulator_g=[]
        for i in self.sa_regulator[1:]:
            self.sa_regulator_g.append(i+'_grp')
        for i in range(len(self.sa_regulator[1:]+self.sa_regulator_g)):
            mc.setAttr(name+'_ikHandle_twist.input3D[%s]'%str(i),0,0,0)
            mc.connectAttr((self.sa_regulator[1:]+self.sa_regulator_g)[i]+'.rotate',name+'_ikHandle_twist.input3D[%s]'%str(i),f=1)
        mc.createNode('multiplyDivide',n=name+'_ikHandle_twist_dm')
        mc.connectAttr(name+'_ikHandle_twist.output3D.output3D'+x,name+'_ikHandle_twist_dm.input1.input1X',f=1)
        mc.addAttr(self.sa_regulator[0],ln='stretch',at='double',dv=10,k=1,min=0,max=10)
        for i in self.stretch_name:
            mc.connectAttr(self.sa_regulator[0]+'.stretch',i+'.valueX')
        # Maintain_Length: 0 = follow curve stretch, 1 = keep original length
        ml_ctrl=self.sa_regulator[0]
        mc.addAttr(ml_ctrl,ln='Maintain_Length',at='double',dv=0,k=1,min=0,max=1)
        ml_sub=mc.createNode('plusMinusAverage',n=name+'_maintainLength_sub')
        mc.setAttr(ml_sub+'.operation',2)
        mc.setAttr(ml_sub+'.input1D[0]',1)
        mc.connectAttr(ml_ctrl+'.Maintain_Length',ml_sub+'.input1D[1]')
        ml_mul=mc.createNode('multiplyDivide',n=name+'_maintainLength_mul')
        mc.setAttr(ml_mul+'.operation',1)
        mc.connectAttr(ml_ctrl+'.stretch',ml_mul+'.input1X')
        mc.connectAttr(ml_sub+'.output1D',ml_mul+'.input2X')
        for i in self.stretch_name:
            mc.disconnectAttr(ml_ctrl+'.stretch',i+'.valueX')
            mc.connectAttr(ml_mul+'.outputX',i+'.valueX')
        mc.addAttr(self.sa_regulator[0],ln='bendback_vis',at='double',dv=0,k=1,min=0,max=1)
        mc.addAttr(self.sa_regulator[0],ln='bake_vis',at='double',dv=0,k=1,min=0,max=1)
        
        
        for i in range(len(self.regulator_bake)):
            mc.connectAttr(self.sa_regulator[0]+'.bake_vis',mc.listRelatives(self.regulator_bake[i],s=1)[0]+'.visibility')
            mc.connectAttr(self.sa_regulator[0]+'.bendback_vis',mc.listRelatives(self.regulator_cross[i],s=1)[0]+'.visibility')
        mc.addAttr(self.sa_regulator[0],ln='twist_mode',at='enum',en="off:on:dTwist:",dv=1,k=1)
        mc.setAttr(self.sa_regulator[0]+'.twist_mode',keyable=0,channelBox=1)
        ikHandle_twist_cd=mc.createNode('condition',n=name+'_ikHandle_twist_cd')
        mc.setAttr(ikHandle_twist_cd+'.secondTerm',2)
        mc.setAttr(ikHandle_twist_cd+'.operation',0)
        mc.setAttr(ikHandle_twist_cd+'.colorIfTrueR',0)
        mc.setAttr(ikHandle_twist_cd+'.colorIfTrueG',1)
        mc.setAttr(ikHandle_twist_cd+'.colorIfFalseG',0)
        mc.connectAttr(self.sa_regulator[0]+'.twist_mode',ikHandle_twist_cd+'.firstTerm')
        mc.connectAttr(self.sa_regulator[0]+'.twist_mode',ikHandle_twist_cd+'.colorIfFalseR')
        mc.connectAttr(ikHandle_twist_cd+'.outColorR',name+'_ikHandle_twist_dm.input2.input2X',f=1)
        mc.connectAttr(name+'_ikHandle_twist_dm.output.outputX',name+"_ikHandle.twist",f=1)
        mc.connectAttr(ikHandle_twist_cd+'.outColorG',name+"_ikHandle.dTwistControlEnable")
        mc.setAttr(name+"_ikHandle.dWorldUpType",4)
        mc.connectAttr(self.sa_regulator[-1]+'.worldMatrix[0]',name+"_ikHandle.dWorldUpMatrixEnd")
        mc.connectAttr(self.sa_regulator[0]+'.worldMatrix[0]',name+"_ikHandle.dWorldUpMatrix")
        mc.setAttr(name+"_ikHandle.dWorldUpVectorX",1)
        mc.setAttr(name+"_ikHandle.dWorldUpVectorY",0)
        mc.parentConstraint(self.sa_regulator[0],name+'_skin_joint_grp',w=1,mo=1)
        mc.addAttr(self.sa_regulator[0],ln='delete_'+name+'_drv_crv',at='double',k=1,dv=0)
        mc.setAttr(self.sa_regulator[0]+'.delete_'+name+'_drv_crv',l=1,k=0)
        mc.addAttr(self.sa_regulator[0],ln='delete_'+name+'_jnt_',at='double',k=1,dv=jnt)
        mc.setAttr(self.sa_regulator[0]+'.delete_'+name+'_jnt_',l=1,k=0)
        mc.addAttr(self.sa_regulator[0],ln='delete_'+name+'_path_',at='double',k=1,dv=jnt)
        mc.setAttr(self.sa_regulator[0]+'.delete_'+name+'_path_',l=1,k=0)
        mc.addAttr(self.sa_regulator[0],ln='delete_'+name+'_distance_',at='double',k=1,dv=jnt-1)
        mc.setAttr(self.sa_regulator[0]+'.delete_'+name+'_distance_',l=1,k=0)
        mc.addAttr(self.sa_regulator[0],ln='delete_'+name+'_',at='double',k=1,dv=quantity)
        mc.setAttr(self.sa_regulator[0]+'.delete_'+name+'_',l=1,k=0)
        mc.addAttr(self.sa_regulator[0],ln='delete_'+name+'_md_distance_',at='double',k=1,dv=jnt-1)  
        mc.setAttr(self.sa_regulator[0]+'.delete_'+name+'_md_distance_',l=1,k=0)
        mc.addAttr(self.sa_regulator[0],ln='delete_'+name+'_cur_scale_info',at='double',k=1,dv=0) 
        mc.setAttr(self.sa_regulator[0]+'.delete_'+name+'_cur_scale_info',l=1,k=0)
        mc.addAttr(self.sa_regulator[0],ln='delete_'+name+'_cur_scale_md',at='double',k=1,dv=0)
        mc.setAttr(self.sa_regulator[0]+'.delete_'+name+'_cur_scale_md',l=1,k=0)
        mc.addAttr(self.sa_regulator[0],ln='delete_'+name+'_ikHandle_twist_dm',at='double',k=1,dv=0)
        mc.setAttr(self.sa_regulator[0]+'.delete_'+name+'_ikHandle_twist_dm',l=1,k=0)
        mc.addAttr(self.sa_regulator[0],ln='delete_'+name+'_ikHandle_twist',at='double',k=1,dv=0)
        mc.setAttr(self.sa_regulator[0]+'.delete_'+name+'_ikHandle_twist',l=1,k=0)
        mc.addAttr(self.sa_regulator[0],ln='delete_'+name,at='double',k=1,dv=0)
        mc.setAttr(self.sa_regulator[0]+'.delete_'+name,l=1,k=0)
        mc.delete(self.defined_lc_Name,self.jnt_reference_loc_path,self.jnt_reference_loc_name_grp)
        if int(dyopen)==0:
            pass
        else:
            mc.group(self.dynamic_name,n=self.dynamic_name+'_grp')
            mc.parent(self.dynamic_name+'_grp',name+'_spline_rig_grp')
            mc.parentConstraint(self.sa_regulator[0],self.dynamic_name+'_grp',w=1,mo=0)        
        if object_scale==0:
            pass
        else:
            self.slither_scale(name,figure,x,dyopen,category)
        self.connect_jont_distance(name,cur,jnt,category,object_scale)
        if stretching==0: 
            mc.delete(self.path_Name,self.distance_Name,self.md_distance_Name)  
        else:
            pass
        if int(path_open)==1:
            try:
                import splineik_path as _path_mod
                reload(_path_mod)
                _path_mod.PathSystem(name,cur,self.sa_regulator[0],path_count,
                                     controls=self.sa_regulator,
                                     references=[c+'_world' for c in self.sa_regulator],
                                     rig_group=name+'_spline_rig_grp').build()
            except Exception as exc:
                mc.warning('Path build failed; the spline was preserved: %s'%exc)
        rig_node=name+'_spline_rig_grp'
        mc.addAttr(rig_node,ln='splineikOwnedNodes',at='message',multi=True)
        owned_index=0
        for uid in sorted(set(mc.ls(uuid=True))-owned_before):
            owned_node=(mc.ls(uid,long=True) or [None])[0]
            if not owned_node or owned_node.split('|')[-1]==rig_node:
                continue
            if 'ikSolver' in mc.nodeType(owned_node,inherited=True) or mc.nodeType(owned_node)=='hikSolver':
                continue
            parents=mc.listRelatives(owned_node,p=True,f=True) or [] if mc.objectType(owned_node,isAType='dagNode') else []
            if parents and set(mc.ls(parents,uuid=True)) & owned_before:
                continue
            mc.connectAttr(owned_node+'.message',rig_node+'.splineikOwnedNodes[%d]'%owned_index)
            owned_index+=1
    #自动合并dy
    def automatic_combine_dy(self,name,oldname):
        dyn_name=[]
        hair_name=[]
        fol_name=[]
        for i in range(len(name)):
            dyn_name.append(name[i]+'_dyn')
            hair_name.append(list(set(mc.listConnections(name[i]+'_dyn',sh=1)))[0])
        for i in hair_name:
            fol_s=mc.listHistory(i,lv=1)
            for i2 in fol_s:
                if mc.objectType(i2)=='follicle':
                    fol_name.append(i2)
        dyn_name_grp=[]
        for i in dyn_name:
            dyn_name_grp.append(i+'_grp')
        mc.delete(dyn_name_grp,hair_name[1:])       
        for i in range(len(name))[1:]:
            mc.connectAttr(fol_name[i]+'.outHair',hair_name[0]+'.inputHair[%s]'%i,f=1)
            mc.connectAttr(hair_name[0]+'.outputHair[%s]'%i,fol_name[i]+'.currentPosition',f=1)
        self.dynamic(oldname)
        mc.connectAttr(self.dynamic_name+'.simulationMethod',hair_name[0]+'.simulationMethod',f=1)
        mc.connectAttr(self.dynamic_name+'.stiffness',hair_name[0]+'.stiffness',f=1)
        mc.connectAttr(self.dynamic_name+'.damp',hair_name[0]+'.damp',f=1)
        mc.connectAttr(self.dynamic_name+'.drag',hair_name[0]+'.drag',f=1)
        mc.connectAttr(self.dynamic_name+'.friction',hair_name[0]+'.friction',f=1)
        mc.connectAttr(self.dynamic_name+'.mass',hair_name[0]+'.mass',f=1)
        mc.connectAttr(self.dynamic_name+'.startCurveAttract',hair_name[0]+'.startCurveAttract',f=1)
        mc.connectAttr(self.dynamic_name+'.gravity',hair_name[0]+'.gravity',f=1)
        mc.connectAttr(self.dynamic_name+'.startFrame',hair_name[0]+'.startFrame',f=1)
        mc.connectAttr(self.dynamic_name+'.iterations',hair_name[0]+'.iterations',f=1)
        mc.setAttr(hair_name[0]+'.stiffnessScale[1].stiffnessScale_Position',1)
        mc.setAttr(hair_name[0]+'.stiffnessScale[1].stiffnessScale_FloatValue',0.2)
        spline_grp=[]
        for i in name:
            spline_grp.append(i+'_spline_rig_grp')        
        mc.group(spline_grp,self.dynamic_name,n=oldname+'_spline_rig_grp')
        mc.addAttr(self.dynamic_name,ln=self.dynamic_name+'_hair',at='double',k=0,dv=0)      
    # 合并新建立的dy
    def combine_newdy(self):
        sacv=mc.ls(sl=1)
        newdyn_name=[]
        for i in sacv:
            if mc.listAttr(i,st=i+'_*')==None:
                newdyn_name=i
        newdyn_names=[newdyn_name]
        if len(newdyn_names)!=1:
            mc.window(title=u"错误",wh=(150,50))
            mc.columnLayout( adjustableColumn=True )
            mc.text(l=u'请选择一个新创建的dy控制器',h=50)
            mc.showWindow()
        else:
            sacv.remove(newdyn_name)
            hair_shape_name=[]
            for i in sacv:
                hair_shape_name.append(mc.listConnections(i,sh=1)[0])
            hair_name=[]
            fol_name=[]
            for i in hair_shape_name:
                hair_name.append(mc.listRelatives(i,p=1)[0])
                fol_s=mc.listHistory(i,lv=1)
                for i2 in fol_s:
                    if mc.objectType(i2)=='follicle':
                        fol_name.append(i2)            
            mc.delete(hair_name,sacv)
            newhair_shape=newdyn_name+'_hairshape'
            nwehair_name=newdyn_name+'_hair'
            mc.createNode('hairSystem',n=newhair_shape)
            mc.rename(mc.listRelatives(newhair_shape,p=1)[0],nwehair_name)
            for i in range(len(fol_name)):
                mc.connectAttr(fol_name[i]+'.outHair',newhair_shape+'.inputHair[%s]'%str(i),f=1)
                mc.connectAttr(newhair_shape+'.outputHair[%s]'%str(i),fol_name[i]+'.currentPosition',f=1)
            mc.connectAttr('time1.outTime',newhair_shape+'.currentTime',f=1)
            mc.parent(nwehair_name,newdyn_name)
            mc.setAttr(nwehair_name+'.inheritsTransform',0)    
            mc.connectAttr(newdyn_name+'.simulationMethod',newhair_shape+'.simulationMethod',f=1)
            mc.connectAttr(newdyn_name+'.stiffness',newhair_shape+'.stiffness',f=1)
            mc.connectAttr(newdyn_name+'.damp',newhair_shape+'.damp',f=1)
            mc.connectAttr(newdyn_name+'.drag',newhair_shape+'.drag',f=1)
            mc.connectAttr(newdyn_name+'.friction',newhair_shape+'.friction',f=1)
            mc.connectAttr(newdyn_name+'.mass',newhair_shape+'.mass',f=1)
            mc.connectAttr(newdyn_name+'.startCurveAttract',newhair_shape+'.startCurveAttract',f=1)
            mc.connectAttr(newdyn_name+'.gravity',newhair_shape+'.gravity',f=1)
            mc.connectAttr(newdyn_name+'.startFrame',newhair_shape+'.startFrame',f=1)
            mc.connectAttr(newdyn_name+'.iterations',newhair_shape+'.iterations',f=1)
            mc.setAttr(newhair_shape+'.stiffnessScale[1].stiffnessScale_Position',1)
            mc.setAttr(newhair_shape+'.stiffnessScale[1].stiffnessScale_FloatValue',0.2)
            mc.addAttr(newdyn_name,ln=newdyn_name+'_hair',at='double',k=0,dv=0)        
    # 添加dy碰撞体
    def createCollider(self,form):
        sacv=mc.ls(sl=1)
        hairshape_s=mc.listConnections(sacv[0])
        hairshape=list(set(hairshape_s))[0]
        foll_s=mc.listHistory(hairshape,f=1,lv=1)
        foll=[]
        for i in foll_s:
            if mc.objectType(i)=='follicle':
                foll.append(i)
        mc.select(foll)
        mel.eval('createHairConstraint %s '%form)
        sacv2=mc.ls(sl=1)
        hairConstraint=mc.listRelatives(sacv2[0],p=1)
        mc.parentConstraint(sacv[0],hairConstraint[0],w=1,mo=0)
        mc.parentConstraint(sacv[0],hairConstraint[0],rm=1) 
    # 删除
    def delete_s(self):
        sacv=mc.ls(sl=1)
        for ii in sacv:
            if not mc.objExists(ii):
                continue
            sacv2=mc.listAttr(ii,st='delete_*')
            registered_rig=None
            for marker in (sacv2 or []):
                candidate=marker[len('delete_'):]+'_spline_rig_grp'
                if mc.objExists(candidate+'.splineikOwnedNodes'):
                    registered_rig=candidate
                    break
            if registered_rig:
                if mc.objExists(ii+'.localRopeSystem'):
                    import splineik_local as _local_mod
                    local_system=_local_mod.system_of(ii)
                    if local_system:
                        _local_mod.freeze_for_delete(local_system)
                import splineik_path as _path_mod
                _path_mod.cleanup(registered_rig[:-len('_spline_rig_grp')],ii)
                owned_nodes=mc.listConnections(registered_rig+'.splineikOwnedNodes',s=True,d=False,shapes=True) or []
                dependencies=[n for n in owned_nodes if mc.objExists(n) and not mc.objectType(n,isAType='dagNode')]
                if dependencies:
                    mc.delete(dependencies)
                mc.delete([n for n in owned_nodes if mc.objExists(n)]+[registered_rig])
                continue
            if sacv2==None:
                mc.window(title=u"错误",wh=(150,50))
                mc.columnLayout( adjustableColumn=True )
                mc.text(l=u'请选择spline第一节控制器',h=50)
                mc.showWindow()
            else:               
                sacv21=[]
                for i in sacv2:
                    sacv21.append(i.replace('delete_',''))
                sacv3=[]
                for i in sacv2:
                    sacv3.append(mc.getAttr(ii+'.'+i))
                path=[]
                for i in range(sacv3[1]):
                    path.append(sacv21[2]+str(i+1))
                skincluster=mc.listConnections(ii,type='skinCluster')
                skin=list(set(skincluster))[0]
                regulator=mc.skinCluster(skin,q=1,inf=1)
                skins=mc.listHistory(skin,f=1)
                distance=[]
                for i in range(sacv3[3]):
                    distance.append(sacv21[3]+str(i+1))
                mc_distance=[]
                for i in range(sacv3[5]):
                    mc_distance.append(sacv21[5]+str(i+1))
                sacle_info=sacv21[6]
                scale_md=sacv21[7]
                twist=sacv21[8]
                twist_md=sacv21[9]
                name_rig=sacv21[-1]+'_spline_rig_grp'
                import splineik_path as _path_mod
                _path_mod.cleanup(sacv21[-1],ii)
                ml_nodes=[]
                for suffix in ('_maintainLength_sub','_maintainLength_mul'):
                    ml_node=sacv21[-1]+suffix
                    if mc.objExists(ml_node):
                        ml_nodes.append(ml_node)
                if ml_nodes:
                    mc.delete(ml_nodes)
                for i in regulator:
                    mc.cutKey(i,clear=1,hi='none')
                mc.delete(regulator,path,distance,mc_distance,sacle_info,scale_md,twist,twist_md)
                mc.delete(name_rig)
    # bake动画
    def bake(self,mintime,maxtime,remove_ctrl):
        mc.currentTime(mintime)
        sacv=mc.ls(sl=1)
        foll=[]
        for i in sacv:
            mc.setAttr(i+'.simulationMethod',2)
            hairshape_s=mc.listRelatives(i,s=1)
            hairSystem=mc.listConnections(i+'.mass',p=1)[0].split('.')[0]
            foll_s=mc.listHistory(hairSystem,f=1,lv=1)
            s_foll=[]
            close_cur_out_joints=[]
            for i2 in foll_s:
                if mc.objectType(i2)=='follicle':
                    s_foll.append(i2)
            if len(s_foll)>1:
                for i3 in s_foll:
                    foll.append(i3)
            else:
                foll.append(s_foll[0])
        all_controller_joint=[]
        close_cur_out_joints=[]
        bake_locs=[]
        bake_locs_grp=[]
        for i in foll:
            A=mc.listConnections(i)
            obj_A=[]
            for x in A:
                obj_A.append(mc.objectType(x))
            obj_B=['rebuildCurve']
            obj_C=list(set(obj_A) & set(obj_B))
            
            Curves=mc.listConnections(i,t='nurbsCurve')
            for i2 in Curves:
                 cc=mc.listHistory(i2,lv=1)
                 for i3 in cc:
                     if 'skin' in i3:
                         cur_drv=i2 
            if len(obj_C)==0:
                Curves.remove(cur_drv)       
                cur_out=Curves[0]
            else:
                reb=A[obj_A.index('rebuildCurve')]
                cur_out=mc.listConnections(reb,t='nurbsCurve')[0]
                
                
            joints=mc.skinCluster(cur_drv,q=1,inf=1)
            ikhandle=[]
            cur_out_joints=[]
            for i2 in mc.listHistory(cur_out,f=1):
                if mc.objectType(i2)=='ikHandle':
                    ikhandle=i2
                if mc.objectType(i2)=='joint':
                    cur_out_joints.append(i2)
            cur_out_joint=[]
            for i2 in mc.listHistory(ikhandle,lv=1):
                if mc.objectType(i2)=='joint':
                    cur_out_joint=[i2]
            for i2 in cur_out_joints:
                cur_out_joint.append(i2)
            close_cur_out_joint=[]
            for i2 in joints:
                length=[]
                for i3 in cur_out_joint:
                    jointsPos=mc.xform(i2,q=1,ws=1,t=1)
                    cur_out_jointPos=mc.xform(i3,q=1,ws=1,t=1)
                    jointsVector=om.MVector (jointsPos[0], jointsPos[1], jointsPos[2])
                    cur_out_jointVector=om.MVector(cur_out_jointPos[0], cur_out_jointPos[1], cur_out_jointPos[2])
                    directionVector =jointsVector-cur_out_jointVector
                    length.append(directionVector.length())
                close_cur_out_joint.append(cur_out_joint[length.index(min(length))])
            controller_joint=[]
            for i2 in range(len(joints)):
                controller_joint.append(joints[i2])
            if len(remove_ctrl)==0:
                pass
            else:
                for i2 in remove_ctrl:
                    controller_joint.remove(i2)
            bake_loc=[]
            bake_loc_grp=[]   
            for i2 in range(len(close_cur_out_joint)):
                #loc=mc.spaceLocator(p=(0,0,0),n=close_cur_out_joint[i]+'_bake_loc')
                loc=mc.spaceLocator(p=(0,0,0))
                loc_grp=mc.group(loc[0])
                bake_loc_grp.append(loc_grp)
                ro=mc.getAttr(controller_joint[i2]+'.rotateOrder')
                mc.setAttr(loc[0]+'.rotateOrder',ro)
                mc.setAttr(loc_grp+'.rotateOrder',ro)
                controller_joint_grp=mc.listRelatives(controller_joint[i2],p=1)[0]
                mc.parent(loc_grp,controller_joint_grp)
                delete_p1=mc.parentConstraint(controller_joint[i2],loc_grp,w=1,mo=0)
                mc.delete(delete_p1)
                delete_p2=mc.pointConstraint(close_cur_out_joint[i2],loc_grp,w=1,mo=0)
                mc.delete(delete_p2)
                bake_parent=mc.parentConstraint(close_cur_out_joint[i2],loc[0],w=1,mo=1)
                mc.setAttr(bake_parent[0]+'.interpType',2)
                bake_loc.append(loc[0])
            for i2 in range(len(joints)):
                bake_locs.append(bake_loc[i2])
                bake_locs_grp.append(bake_loc_grp[i2])
                close_cur_out_joints.append(close_cur_out_joint[i2])
            for i2 in controller_joint:
                all_controller_joint.append(i2)

        mc.bakeResults(bake_locs,t=(mintime,maxtime),simulation=1,sb=1,pok=1)
        for i in range(len(bake_locs)):
            mc.copyKey(bake_locs[i],time=(mintime,maxtime))
            mc.pasteKey(all_controller_joint[i])
        for i in sacv:
            mc.setAttr(i+'.simulationMethod',1) 
        for i in range(len(bake_locs)):
              mc.delete(mc.listRelatives(bake_locs[i],typ='parentConstraint'))
        mc.delete(bake_locs_grp) 
        
    # bake骨骼动画
    def bake_jnt_Fun(self,mintime,maxtime,remove_ctrl):
        mc.currentTime(mintime)
        sacv=mc.ls(sl=1)
        foll=[]
        for i in sacv:
            mc.setAttr(i+'.simulationMethod',2)
            hairshape_s=mc.listRelatives(i,s=1)
            hairSystem=mc.listConnections(i+'.mass',p=1)[0].split('.')[0]
            foll_s=mc.listHistory(hairSystem,f=1,lv=1)
            s_foll=[]
            close_cur_out_joints=[]
            for i2 in foll_s:
                if mc.objectType(i2)=='follicle':
                    s_foll.append(i2)
            if len(s_foll)>1:
                for i3 in s_foll:
                    foll.append(i3)
            else:
                foll.append(s_foll[0])
        bake_jnt=[]
        for i in foll:
            A=mc.listConnections(i)
            obj_A=[]
            for x in A:
                obj_A.append(mc.objectType(x))
            obj_B=['rebuildCurve']
            obj_C=list(set(obj_A) & set(obj_B))
            
            Curves=mc.listConnections(i,t='nurbsCurve')
            for i2 in Curves:
                 cc=mc.listHistory(i2,lv=1)
                 for i3 in cc:
                     if 'skin' in i3:
                         cur_drv=i2 
            if len(obj_C)==0:
                Curves.remove(cur_drv)       
                cur_out=Curves[0]
            else:
                reb=A[obj_A.index('rebuildCurve')]
                cur_out=mc.listConnections(reb,t='nurbsCurve')[0]
            cur_out_joints=[]
            ikhandle=[]
            for i2 in mc.listHistory(cur_out,f=1):
                if mc.objectType(i2)=='joint':
                    cur_out_joints.append(i2)
                if mc.objectType(i2)=='ikHandle':
                    ikhandle=i2
                    for i3 in mc.listHistory(ikhandle,lv=1):
                        if mc.objectType(i3)=='joint':
                            cur_out_joints.append(i3)
            for i2 in cur_out_joints:
                bake_jnt.append(i2)
        mc.bakeResults(bake_jnt,t=(mintime,maxtime),simulation=1,sb=1,pok=1)
        for i in sacv:
            mc.setAttr(i+'.simulationMethod',1) 



    # 创建滑动缩放控制器名字
    def slither_scale_name(self,name,figure):
        self.slither_scale_name=[]
        self.slither_scale_name_grp=[]
        for i in range(figure):
            self.slither_scale_name.append(name+'_slither_scale_'+str(i+1))   
            self.slither_scale_name_grp.append(name+'_slither_scale_'+str(i+1)+'_grp')
    # 创建滑动缩放控制器
    def slither_scale_control(self,name,figure,dyopen,category):
        self.slither_scale_name(name,figure)
        if int(dyopen)==0:
            shapes=mc.listRelatives(self.copy_cur_name,s=1)
        else:
            shapes=mc.listRelatives(name+'_ouputCrv',s=1)
        for i in self.slither_scale_name:
            mc.curve(d=1,p=[(0,1,0),(0,0.707,0.707),(0,0,1),(0,-0.707,0.707),(0,-1,0),(0,-0.707,-0.707),(0,0,-1),
                     (0,0.707,-0.707),(0,1,0),(0.707,0.707,0),(1,0,0),(0.707,-0.707,0),(0,-1,0),(-0.707,-0.707,0),
                     (-1,0,0),(-0.707,0.707,0),(0,1,0),(0,0.707,-0.707),(0,0,-1),(-0.707,0,-0.707),(-1,0,0),
                     (-0.707,0,0.707),(0,0,1),(0.707,0,0.707),(1,0,0),(0.707,0,-0.707),(0,0,-1)],n=i)
            mc.addAttr(i,dt='string',ln='Category')
            mc.setAttr(i+'.Category',l=1)
            mc.setAttr(i+'.sx',self.sa_regulator_grp_scale)
            mc.setAttr(i+'.sy',self.sa_regulator_grp_scale)
            mc.setAttr(i+'.sz',self.sa_regulator_grp_scale)
            mc.makeIdentity(i,apply=1,t=0,r=0,s=1,n=0)
            mc.rename(mc.listRelatives(i,s=1),i+'shape')       
            mc.setAttr(i+'.overrideEnabled',1)
            mc.setAttr(i+'.overrideColor',16)
            mc.addAttr(i,ln='position',at='double',min=0,max=1,k=1)
            mc.addAttr(i,ln='front_falloff',at='double',min=0.01,max=2,k=1,dv=0.1)
            mc.addAttr(i,ln='back_falloff',at='double',min=0.01,max=2,k=1,dv=0.1)
            mc.addAttr(i,ln='slither_scale',at='double',k=1,dv=1)            
            mc.connectAttr(i+'.slither_scale',i+'.sx',f=1)
            mc.connectAttr(i+'.slither_scale',i+'.sy',f=1)
            mc.connectAttr(i+'.slither_scale',i+'.sz',f=1)
            mc.group(i,n=i+'_grp')    
    # 滑动缩放
    def slither_scale(self,name,figure,x,dyopen,category):
        self.slither_scale_control(name,figure,dyopen,category)
        if x=='x':
            y='y'
            z='z'
        elif x=='y':
            y='x'
            z='z'
        elif x=='z':
            y='x'
            z='y'
        jnt_name=self.jnt_Name2
        aa=range(len(self.jnt_Name2))
        for x in range(figure):
            CTRL_name=self.slither_scale_name[x]
            jnt_name_grp=[]
            for i in aa:
                jnt_name_grp.append(self.jnt_Name2[i]+'_slither_sacle_%s_grp'%str(x+1))
                mc.group(self.jnt_Name2[i],n=self.jnt_Name2[i]+'_slither_sacle_%s_grp'%str(x+1))
            for i in aa:
                mp_m_name=mc.createNode('plusMinusAverage',n=name+'_pm_m_%s'%str(i+1))
                mc.setAttr(mp_m_name+'.input3D[0]',0,0,0)
                mc.setAttr(mp_m_name+'.input3D[1]',0,0,0)
                mc.connectAttr(jnt_name[i]+'.Position',mp_m_name+'.input3D[0].input3Dx')
                mc.connectAttr(CTRL_name+'.front_falloff',mp_m_name+'.input3D[1].input3Dx')
                mc.setAttr(mp_m_name+'.operation',2)
                
                remapValue_front_name=mc.createNode('remapValue',n=name+'_front_rv_%s'%str(i+1))
                mc.setAttr(remapValue_front_name+'.value[0].value_Interp',2)
                mc.connectAttr(CTRL_name+'.position',remapValue_front_name+'.inputValue')
                mc.connectAttr(mp_m_name+'.output3Dx',remapValue_front_name+'.inputMin')
                mc.connectAttr(jnt_name[i]+'.Position',remapValue_front_name+'.inputMax')
                mc.setAttr(remapValue_front_name+'.outputMin',1)
                mc.connectAttr(CTRL_name+'.slither_scale',remapValue_front_name+'.outputMax')
                
                mp_p_name=mc.createNode('plusMinusAverage',n=name+'_pm_p_%s'%str(i+1))
                mc.setAttr(mp_p_name+'.input3D[0]',0,0,0)
                mc.setAttr(mp_p_name+'.input3D[0]',0,0,0)
                mc.connectAttr(jnt_name[i]+'.Position',mp_p_name+'.input3D[0].input3Dx')
                mc.connectAttr(CTRL_name+'.back_falloff',mp_p_name+'.input3D[1].input3Dx')
                
                remapValue_back_name=mc.createNode('remapValue',n=name+'_back_rv_%s'%str(i+1))
                mc.setAttr(remapValue_back_name+'.value[0].value_Interp',2)
                mc.connectAttr(CTRL_name+'.position',remapValue_back_name+'.inputValue')
                mc.connectAttr(jnt_name[i]+'.Position',remapValue_back_name+'.inputMin')
                mc.connectAttr(mp_p_name+'.output3Dx',remapValue_back_name+'.inputMax')
                mc.setAttr(remapValue_back_name+'.outputMin',1)
                mc.connectAttr(CTRL_name+'.slither_scale',remapValue_back_name+'.outputMax')
                mc.setAttr(remapValue_back_name+'.value[0].value_FloatValue',1)
                mc.setAttr(remapValue_back_name+'.value[1].value_FloatValue',0)
                
                condition_name=mc.createNode('condition',n=name+'_condition_%s'%str(i+1))
                mc.connectAttr(CTRL_name+'.position',condition_name+'.firstTerm')
                mc.connectAttr(jnt_name[i]+'.Position',condition_name+'.secondTerm')
                mc.setAttr(condition_name+'.operation',4)
                mc.connectAttr(remapValue_front_name+'.outValue',condition_name+'.colorIfTrueR')
                mc.connectAttr(remapValue_back_name+'.outValue',condition_name+'.colorIfFalseR')
                
                mc.connectAttr(condition_name+'.outColorR',jnt_name_grp[i]+'.s'+y)
                mc.connectAttr(condition_name+'.outColorR',jnt_name_grp[i]+'.s'+z)
        if category==1:                        
            for i in self.slither_scale_name:
                mc.createNode('motionPath',n=i+'_motionPath')
                mc.setAttr(i+'_motionPath'+'.fractionMode',1)
        else:
            for i in self.slither_scale_name:
                mc.createNode('pointOnCurveInfo',n=i+'_motionPath')
                mc.setAttr(i+'_motionPath'+'.turnOnPercentage',1)
        if int(dyopen)==0:
            shapes=mc.listRelatives(self.copy_cur_name,s=1)
        else:
            shapes=mc.listRelatives(name+'_ouputCrv',s=1)
        if category==1:            
            for i in self.slither_scale_name:
                mc.connectAttr(shapes[0]+".worldSpace",i+'_motionPath'+'.geometryPath',f=1)
                mc.connectAttr(i+'_motionPath.allCoordinates',i+'_grp'+'.translate',f=1)
                mc.connectAttr(i+'.position',i+'_motionPath.uValue',f=1)
        else :
            for i in self.slither_scale_name:
                mc.connectAttr(shapes[0]+".worldSpace",i+'_motionPath'+'.inputCurve',f=1)
                mc.connectAttr(i+'_motionPath.position',i+'_grp'+'.translate',f=1)
                mc.connectAttr(i+'.position',i+'_motionPath.parameter',f=1)       
        mc.group(self.slither_scale_name_grp,n=name+'_slither_scale_grp')
        for i in self.slither_scale_name_grp:
            mc.setAttr(i+'.inheritsTransform',0)
        mc.parent(name+'_slither_scale_grp',name+'_spline_rig_grp')            
      
        for i in self.slither_scale_name:
            mc.setAttr(i+'.tx',l=1,k=0)
            mc.setAttr(i+'.ty',l=1,k=0)
            mc.setAttr(i+'.tz',l=1,k=0)
            mc.setAttr(i+'.rx',l=1,k=0)
            mc.setAttr(i+'.ry',l=1,k=0)
            mc.setAttr(i+'.rz',l=1,k=0)
            mc.setAttr(i+'.sx',l=1,k=0)
            mc.setAttr(i+'.sy',l=1,k=0)
            mc.setAttr(i+'.sz',l=1,k=0)
            mc.setAttr(i+'.v',l=1,k=0)
        self.slither_scale_sacle(name)
    # 滑动缩放的缩放倍率
    def slither_scale_sacle(self,name):
        mc.createNode('multiplyDivide',n=name+'_slither_scale_dm')
        mc.connectAttr(self.scale_info_Name+'.arcLength',name+'_slither_scale_dm'+'.input1X',f=1)
        input2X=mc.getAttr(self.scale_info_Name+'.arcLength')
        mc.setAttr(name+'_slither_scale_dm'+'.input2X',input2X)
        mc.setAttr(name+'_slither_scale_dm'+'.operation',2)
        for i in self.slither_scale_name_grp:            
            mc.connectAttr(name+'_slither_scale_dm.outputX',i+'.sx')
            mc.connectAttr(name+'_slither_scale_dm.outputX',i+'.sy')
            mc.connectAttr(name+'_slither_scale_dm.outputX',i+'.sz')
            mc.setAttr(i+'.tx',l=1,k=0)
            mc.setAttr(i+'.ty',l=1,k=0)
            mc.setAttr(i+'.tz',l=1,k=0)
            mc.setAttr(i+'.rx',l=1,k=0)
            mc.setAttr(i+'.ry',l=1,k=0)
            mc.setAttr(i+'.rz',l=1,k=0)
            mc.setAttr(i+'.sx',l=1,k=0)
            mc.setAttr(i+'.sy',l=1,k=0)
            mc.setAttr(i+'.sz',l=1,k=0)
            mc.setAttr(i+'.v',l=1,k=0)
    # 删除动画
    def delete_key(self):
        sacv=mc.ls(sl=1)
        for i in sacv:
            if mc.objExists (i+'.bake_vis ')==1:
                bake=mc.listConnections(i+'.bake_vis',d=1)
                for i2 in bake:
                    mc.cutKey(i2)
                    mc.setAttr(i2+'.tx',0)
                    mc.setAttr(i2+'.ty',0)
                    mc.setAttr(i2+'.tz',0)
                    mc.setAttr(i2+'.rx',0)
                    mc.setAttr(i2+'.ry',0)
                    mc.setAttr(i2+'.rz',0)
            elif mc.objExists (i+'.simulationMethod ')==1:
                hairShape=mc.listConnections(i+'.simulationMethod',c=1)[1]
                hairShape_His=mc.listHistory (hairShape,lv=1)
                folShape=[]
                for x in hairShape_His:
                    if mc.objectType(x)=='follicle':
                        folShape.append(x)
                    else:
                        pass
                all_joint=[]
                for x in folShape:
                    for i2 in mc.listHistory (x,lv=1):
                        if mc.objectType(i2)=='nurbsCurve':
                            curbulit=i2
                        else:
                            pass
                    for i2 in mc.listHistory(curbulit,ha=1):
                        if mc.objectType(i2)=='joint':
                            all_joint.append(i2)
                        else:
                            pass
                for i2 in all_joint:
                    mc.cutKey(i2)
                    mc.setAttr(i2+'.tx',0)
                    mc.setAttr(i2+'.ty',0)
                    mc.setAttr(i2+'.tz',0)
                    mc.setAttr(i2+'.rx',0)
                    mc.setAttr(i2+'.ry',0)
                    mc.setAttr(i2+'.rz',0)
    # 删除动画
    def delete_jnt_key(self):
        sacv=mc.ls(sl=1)
        foll=[]
        for i in sacv:
            mc.setAttr(i+'.simulationMethod',1)
            hairshape_s=mc.listRelatives(i,s=1)
            hairSystem=mc.listConnections(i+'.mass',p=1)[0].split('.')[0]
            foll_s=mc.listHistory(hairSystem,f=1,lv=1)
            s_foll=[]
            close_cur_out_joints=[]
            for i2 in foll_s:
                if mc.objectType(i2)=='follicle':
                    s_foll.append(i2)
            if len(s_foll)>1:
                for i3 in s_foll:
                    foll.append(i3)
            else:
                foll.append(s_foll[0])
        bake_jnt=[]
        jnt_one=[]
        ik_Hand=[]
        for i in foll:
            A=mc.listConnections(i)
            obj_A=[]
            for x in A:
                obj_A.append(mc.objectType(x))
            obj_B=['rebuildCurve']
            obj_C=list(set(obj_A) & set(obj_B))
            
            Curves=mc.listConnections(i,t='nurbsCurve')
            for i2 in Curves:
                 cc=mc.listHistory(i2,lv=1)
                 for i3 in cc:
                     if 'skin' in i3:
                         cur_drv=i2 
            if len(obj_C)==0:
                Curves.remove(cur_drv)       
                cur_out=Curves[0]
            else:
                reb=A[obj_A.index('rebuildCurve')]
                cur_out=mc.listConnections(reb,t='nurbsCurve')[0]
            cur_out_joints=[]
            ikhandle=[]
            for i2 in mc.listHistory(cur_out,f=1):
                if mc.objectType(i2)=='joint':
                    cur_out_joints.append(i2)
                if mc.objectType(i2)=='ikHandle':
                    ikhandle=i2
                    ik_Hand.append(i2)
                    for i3 in mc.listHistory(ikhandle,lv=1):
                        if mc.objectType(i3)=='joint':
                            jnt_one.append(i3)
            for i2 in cur_out_joints:
                bake_jnt.append(i2)
        mc.cutKey(bake_jnt+jnt_one)


        for i in ik_Hand:
            mc.setAttr(i+'.ikBlend',1)
        for i in bake_jnt:
            pos=mc.getAttr(i+'.Position')
            for i2 in mc.listAttr(i,ud=1):
                if 'distaince' in i2:
                    dis=i2
                    mc.connectAttr(i+'.%s'%dis,i+'.t%s'%(i2[-1]),f=1)
            mc.setAttr(i+'.Position',pos)
                



'''
ik().delete_key()
'''