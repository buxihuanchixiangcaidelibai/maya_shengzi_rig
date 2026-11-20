#!/usr/bin/env python
# -*- coding: cp936 -*-
import maya.cmds as mc
import kxj_ik_dy305 as kxj_ik
reload(kxj_ik)
import splineik_weight as weight
reload(weight)
import splineik_path_ui as pathui
reload(pathui)
class ik_UI(object):
    def __init__(self):
        self.UI()
    def UI(self):
        if mc.window("splineik",exists=1):
           mc.deleteUI("splineik")
        #
        a=mc.window("splineik",title=u"牙签__spline_v2.0")
        ##################################################
        form = mc.formLayout()
        tabs = mc.tabLayout(imw=5, imh=5)
        mc.formLayout( form, edit=True, attachForm=((tabs, 'top', 0), (tabs, 'left', 0), (tabs, 'bottom', 0), (tabs, 'right', 0)) )
        ###################################################
        child1=mc.scrollLayout(horizontalScrollBarThickness=16,verticalScrollBarThickness=16,cr=1)
        mc.columnLayout(adj=1,rs=1)
        self.s1=mc.separator(vis = 1,style='in',w = 300,h=5) 
        mc.setParent('..')
        mc.columnLayout(adj=0,rs=1)
        self.s2=mc.text(l=u'1.先画一条Nurbs曲线',h=30)
        mc.setParent('..')
        mc.columnLayout(adj=1,rs=1)
        self.s3=mc.separator(vis = 1,style='in',w = 300,h=5)
        mc.setParent('..')
        mc.columnLayout(adj=0,rs=1)
        self.s4=mc.text(l=u'2.spline参数设置',h=30)
        mc.setParent('..')
        mc.columnLayout(adj=1,rs=3)
        self.s5=mc.textFieldGrp(l=u'名字:          ',cw2=[80,200],adj=2)
        self.s6=mc.floatSliderGrp( label=u'控制器数量:    ', field=True,cw3=[80,40,155],min=0, max=10,fmn=0,fmx=1000,pre=0,v=2,cc=lambda *args:self.Slider())
        self.s7=mc.floatSliderGrp( label=u'骨骼数量:      ', field=True,cw3=[80,40,155],min=0, max=50,fmn=0,fmx=1000,pre=0,v=5)
        mc.setParent('..')
        mc.paneLayout(configuration='vertical2')
        self.s8=mc.optionMenu( label=u'     基本朝向:     ',cc=lambda *args:self.ui_xyz())
        self.s8_1=mc.menuItem( label='x' )
        self.s8_2=mc.menuItem( label='y')
        self.s8_3=mc.menuItem( label='z' )
        self.s9=mc.optionMenu( label=u'    向上朝向:     ')
        self.s9_1=mc.menuItem( label='x' ,en=0)
        self.s9_2=mc.menuItem( label='y' )
        self.s9_3=mc.menuItem( label='z' )
        mc.optionMenu(self.s9,e=1,sl=2)  
        mc.setParent('..')
        mc.paneLayout(configuration='vertical3')
        self.s10=mc.checkBoxGrp( ncb=2, label=u'    属性：        ', labelArray2=[u'动力学', u'自动合并'],cw3=[80,60,50],en2=0,cc1=lambda *args:self.check() )
        self.stretchingBox=mc.checkBox( label=u'拉伸' ,v=1)
        self.add1=mc.optionMenu( label=u'模式')
        self.add1_1=mc.menuItem( label=u'path' )
        self.add1_2=mc.menuItem( label=u'point' )
        mc.optionMenu(self.add1,e=1,sl=1)
        mc.setParent('..')
        mc.columnLayout(adj=1,rs=3)
        mc.paneLayout(configuration='vertical2',swp=2)
        self.ss1=mc.floatSliderGrp(label=u'滑动缩放:      ',field=True,cw3=[78,40,125],min=1, max=10,fmn=1,fmx=1000,pre=0,v=1,en=0)
        self.ss2=mc.checkBox(v=0,l='',cc=lambda *args:self.slither_scale())  
        mc.setParent('..')
        pathui.build()
        self.s11=mc.separator(vis = 1,style='in',w = 300,h=5) 
        self.s13=mc.textFieldButtonGrp( label='3.创建控制器校轴参考物体      ',buttonLabel='创建',cw3=(150,0,50),adj=3,bc=lambda *args:self.establish_loc())
        #self.s12=mc.text(l=u'3.创建控制器校轴参考物体:')
        #self.s13=mc.button(l=u'创建',w=100,h=20,c=lambda *args:self.establish_loc())
        self.s14=mc.separator(vis = 1,style='in',w = 300,h=5)
        self.s16=mc.textFieldButtonGrp( label='4.创建spline:                            ',buttonLabel='创建',cw3=(150,0,50),adj=3,bc=lambda *args:self.establish_spline())
        #self.s15=mc.text(l=u'4.创建spline:')
        #self.s16=mc.button(l=u'创建',w=100,h=20,c=lambda *args:self.establish_spline())
        mc.setParent('..')
        self.s17=mc.separator(vis = 1,style='in',w = 300,h=5)
        mc.paneLayout(configuration='vertical2')
        self.s18=mc.button(l=u'创建Dynamic控制器',h=20,c=lambda *args:self.new_dy())
        self.s19=mc.button(l=u'合并Dynamic',h=20,c=lambda *args:self.combine_dy())
        mc.setParent('..')
        mc.columnLayout(adj=1,rs=3)
        mc.separator(vis = 1,style='in',w = 300,h=5)
        self.s20=mc.button(l=u'删除spline',h=20,c=lambda *args:self.deltet_ss())
        mc.separator(vis = 1,style='in',w = 300,h=5)
        mc.setParent('..')

        mc.setParent('..')
        ###################################################
        child2=mc.scrollLayout(horizontalScrollBarThickness=16,verticalScrollBarThickness=16,cr=1)
        mc.paneLayout(configuration='vertical2',w=300)
        mc.columnLayout(adj=1,rs=8)
        mc.paneLayout(configuration='vertical2')
        mc.columnLayout(adj=1,rs=8)
        self.d1=mc.text(l=u'动力学')
        self.d2=mc.textScrollList( numberOfRows=12, allowMultiSelection=True,
                                  showIndexedItem=4,sc=lambda *args:self.dyn_select())
        mc.setParent('..')
        mc.columnLayout(adj=1,rs=8)
        self.d3=mc.text(l=u'状态')
        self.d4=mc.textScrollList( numberOfRows=12, allowMultiSelection=True,
                                    showIndexedItem=4,w=50)
        mc.setParent('..')
        mc.setParent('..')
        self.d13=mc.button(l=u'刷新',w=150,c=lambda *args:self.dyn_tabulation())
        self.d131=mc.button(l=u'选着所有动力学曲线',w=150,c=lambda *args:self.select_allDyn_Fun())
        mc.setParent('..')
        mc.columnLayout(adj=1,rs=8)
        self.d5=mc.button(l=u'开启动力学',c=lambda *args:self.Color(),bgc=[0,1,0.7])
        self.d6=mc.button(l=u'创建方形碰撞体',w=130,c=lambda *args:self.dy_createCollider(6))
        self.d7=mc.button(l=u'创建圆形碰撞体',w=130,c=lambda *args:self.dy_createCollider(5))
        self.d8=mc.textFieldGrp( label=u'bake起始帧',cw2=[60,30] ,en=0)
        self.d9=mc.textFieldGrp( label=u'bake结束帧',cw2=[60,30] ,en=0)
        self.d10=mc.checkBox( label=u'自动',v=1 ,cc=lambda *args:self.bake_automatic()) 
        self.d11=mc.button(l=u'bake动画到控制器',w=130,c=lambda *args:self.bake(None,'ctrl'))
        self.d12=mc.button(l=u'删除控制器动画',w=130,c=lambda *args:kxj_ik.ik().delete_key())
        self.d13=mc.button(l=u'bake动画到骨骼',w=130,c=lambda *args:self.bake(None,'jnt'))
        self.d14=mc.button(l=u'删除骨骼动画',w=130,c=lambda *args:kxj_ik.ik().delete_jnt_key())
        mc.setParent('..')
        
        mc.setParent('..')
        #
        mc.setParent('..')
        
        ###################################################
        child3=mc.scrollLayout(horizontalScrollBarThickness=16,verticalScrollBarThickness=16,cr=1)
        mc.columnLayout(adj=1,rs=3)
        weight.build_weight_ui()
        mc.setParent('..')
        mc.setParent('..')
        ###################################################
        mc.tabLayout( tabs, edit=True, tabLabel=((child1, u'rigging'),(child2, u'animation'),(child3, u'weight')) )
        mc.window("splineik",e=1,wh=(400,400))
        mc.showWindow(a)
        self.dyn_tabulation()
    def ui_xyz(self):
        sacv=mc.optionMenu(self.s8,q=1,sl=1)
        if sacv==1:
            mc.optionMenu(self.s9,e=1,sl=2)
            mc.menuItem(self.s9_1,e=1,en=0)
            mc.menuItem(self.s9_2,e=1,en=1)
            mc.menuItem(self.s9_3,e=1,en=1)
        elif sacv==2:
            mc.optionMenu(self.s9,e=1,sl=1)
            mc.menuItem(self.s9_2,e=1,en=0)
            mc.menuItem(self.s9_1,e=1,en=1)
            mc.menuItem(self.s9_3,e=1,en=1)
        elif sacv==3:
            mc.optionMenu(self.s9,e=1,sl=1)
            mc.menuItem(self.s9_3,e=1,en=0)
            mc.menuItem(self.s9_1,e=1,en=1)
            mc.menuItem(self.s9_2,e=1,en=1)
    def Slider(self):
        sacv=mc.floatSliderGrp(self.s6,q=1,v=1)
        #mc.floatSliderGrp(self.s7,e=1,v=sacv*4)
        mc.floatSliderGrp(self.s7,e=1,v=(sacv-1)*4+1)
    def check(self):
        sacv=mc.checkBoxGrp(self.s10,q=1,v1=1)
        if sacv==1:
            mc.checkBoxGrp(self.s10,e=1,en2=1)
        else:
            mc.checkBoxGrp(self.s10,e=1,en2=0)
            mc.checkBoxGrp(self.s10,e=1,v2=0)
    def establish_loc(self):
        self.cur=mc.ls(sl=1)
        jnt=mc.floatSliderGrp(self.s7,q=1,v=1)        
        x=mc.optionMenu(self.s8,q=1,v=1)
        y=mc.optionMenu(self.s9,q=1,v=1)
        quantity=mc.floatSliderGrp(self.s6,q=1,v=1)
        if len(self.cur)==0:
            mc.window(title=u"错误",wh=(150,50))
            mc.columnLayout( adjustableColumn=True )
            mc.text(l=u'请选择曲线',h=50)
            mc.showWindow()
        elif len(self.cur)==1:
            cur=mc.ls(sl=1)[0]
            name_f=mc.textFieldGrp(self.s5,q=1,tx=1)
            if ' ' in name_f:
                name=name_f.replace(' ','_')
            else:
                name=mc.textFieldGrp(self.s5,q=1,tx=1)
            kxj_ik.ik().connect_defined_loc_curve(name,cur,int(jnt),x,y,int(quantity))
        elif len(self.cur)>1:
            for i in range(len(self.cur)):
                curs=self.cur[i]
                name_f=mc.textFieldGrp(self.s5,q=1,tx=1)+'_'+str(i+1)
                if ' ' in name_f:
                    name=name_f.replace(' ','_')
                else:
                    name=mc.textFieldGrp(self.s5,q=1,tx=1)+'_'+str(i+1)
                kxj_ik.ik().connect_defined_loc_curve(name,curs,int(jnt),x,y,int(quantity))
    def establish_spline(self):
        jnt=mc.floatSliderGrp(self.s7,q=1,v=1)        
        x=mc.optionMenu(self.s8,q=1,v=1)
        y=mc.optionMenu(self.s9,q=1,v=1)
        quantity=mc.floatSliderGrp(self.s6,q=1,v=1)
        dyopen=mc.checkBoxGrp(self.s10,q=1,v1=1)
        category=mc.optionMenu(self.add1,q=1,sl=1)
        stretching=mc.checkBox(self.stretchingBox,v=1,q=1)
        object_scale=[]
        if mc.checkBox(self.ss2,q=1,v=1)==0:
            object_scale=0
        else:
            object_scale=1
        figure=mc.floatSliderGrp(self.ss1,q=1,v=1)
        
        
        if len(self.cur)==1:
            name_f=mc.textFieldGrp(self.s5,q=1,tx=1)
            if ' ' in name_f:
                name=name_f.replace(' ','_')
            else:
                name=mc.textFieldGrp(self.s5,q=1,tx=1)
            kxj_ik.ik().spline_rig_grp(name,self.cur[0],int(jnt),x,y,int(quantity),dyopen,object_scale,int(figure),category,stretching,pathui.read()[0],pathui.read()[1])
        elif len(self.cur)>1:
            for i in range(len(self.cur)):
                curs=self.cur[i]
                name_f=mc.textFieldGrp(self.s5,q=1,tx=1)+'_'+str(i+1)
                if ' ' in name_f:
                    name=name_f.replace(' ','_')
                else:
                    name=mc.textFieldGrp(self.s5,q=1,tx=1)+'_'+str(i+1)
                kxj_ik.ik().spline_rig_grp(name,curs,jnt,x,y,quantity,dyopen,object_scale,figure,category,stretching,pathui.read()[0],pathui.read()[1])
        combine_dy=mc.checkBoxGrp(self.s10,q=1,v2=1)
        
        if int(combine_dy)==1:
            if len(self.cur)>1:
                newname=[]
                for i in range(len(self.cur)):
                    newname.append(mc.textFieldGrp(self.s5,q=1,tx=1)+'_'+str(i+1))
                oldname=mc.textFieldGrp(self.s5,q=1,tx=1)
                kxj_ik.ik().automatic_combine_dy(newname,oldname)
            else:
                pass
        if dyopen==1:
            self.dyn_tabulation()
        else:
            pass
        #print [name,self.cur[0],jnt,x,y,quantity,dyopen,object_scale,figure,category]
        self.dyn_tabulation()

            
    # 创建一个新的dy控制器
    def new_dy(self):
        name_f=mc.textFieldGrp(self.s5,q=1,tx=1)
        if ' ' in name_f:
            name=name_f.replace(' ','_')
        else:
            name=mc.textFieldGrp(self.s5,q=1,tx=1)
        kxj_ik.ik().dynamic(name)
    # 合并dy控制器
    def combine_dy(self):
        kxj_ik.ik().combine_newdy()
        
    # 创建dy碰撞体
    def dy_createCollider(self,form):
        sacv=mc.ls(sl=1)
        sacv2=mc.listAttr(sacv[0],st='dynamic')
        if sacv2==None:
            mc.window(title=u"错误",wh=(150,50))
            mc.columnLayout( adjustableColumn=True )
            mc.text(l=u'请选择dyn控制器',h=50)
            mc.showWindow()
        else:
            kxj_ik.ik().createCollider(form)
                
                
                
    def deltet_ss(self):
        kxj_ik.ik().delete_s()
    
    # 自动bake起始结束帧
    def bake_automatic(self):
        if mc.checkBox(self.d10,q=1,v=1)==1:
            mc.textFieldGrp(self.d8,e=1,en=0)
            mc.textFieldGrp(self.d9,e=1,en=0)
        else:
            mc.textFieldGrp(self.d8,e=1,en=1)
            mc.textFieldGrp(self.d9,e=1,en=1)
    # bake动画
    def bake(self,a,ctrl_jnt):
        #items=mc.textScrollList(a,q=1,ai=1)
        items=[]
        if items==None:
            items=[]
        else:
            pass
        if mc.checkBox(self.d10,q=1,v=1)==1:
            mintime=mc.playbackOptions(q=1,min=1)
            maxtime=mc.playbackOptions(q=1,max=1)
            if ctrl_jnt=='ctrl':
                kxj_ik.ik().bake(mintime,maxtime,items)
            else:
                kxj_ik.ik().bake_jnt_Fun(mintime,maxtime,items)
        else:
            mintime=int(mc.textFieldGrp(self.d8,q=1,tx=1))
            maxtime=int(mc.textFieldGrp(self.d9,q=1,tx=1))
            if mintime>maxtime:
                mc.window(title=u"错误",wh=(150,50))
                mc.columnLayout( adjustableColumn=True )
                mc.text(l=u'起始帧不能大于结束帧错误',h=50)
                mc.showWindow()
            elif mintime=='':
                mc.window(title=u"错误",wh=(150,50))
                mc.columnLayout( adjustableColumn=True )
                mc.text(l=u'起始帧不能为空',h=50)
                mc.showWindow()
            elif maxtime=='':
                mc.window(title=u"错误",wh=(150,50))
                mc.columnLayout( adjustableColumn=True )
                mc.text(l=u'结束帧不能为空',h=50)
                mc.showWindow()
            else:
                if ctrl_jnt=='ctrl':
                    kxj_ik.ik().bake(mintime,maxtime,items)
                else:
                    kxj_ik.ik().bake_jnt_Fun(mintime,maxtime,items)
        self.dyn_tabulation()
    
    
    
    # 滑动缩放
    def slither_scale(self):
        if mc.checkBox(self.ss2,q=1,v=1)==0:
            mc.floatSliderGrp(self.ss1,e=1,en=0)
        else:
            mc.floatSliderGrp(self.ss1,e=1,en=1)
    # 动力学开关显示
    def Color(self):
        label=mc.button(self.d5,q=1,l=1)
        if label==u'开启动力学':
            mc.button(self.d5,e=1,l=u'关闭动力学',bgc=[1,0,0.5])
        else :
            mc.button(self.d5,e=1,l=u'开启动力学',bgc=[0,1,0.7])
        self.dyn_openclose()
    # 刷新动力学列表
    def dyn_tabulation(self):
        mc.textScrollList(self.d2,e=1,ra=1)
        sacv=mc.ls(type='nurbsCurve',l=1)
        transforms=[mc.listRelatives(s, p=1, type='transform',f=1)[0] for s in sacv]
        sacv2=[]
        for i in transforms:
            if mc.attributeQuery('simulationMethod',node=i,ex=1)==1:
                sacv2.append(i)       
        mc.textScrollList(self.d2,e=1,a=list(set(sacv2)))
        self.dyn_switch()
    # 选着全部动力学曲线
    def select_allDyn_Fun(self):
        all_Dyn=mc.textScrollList(self.d2,q=1,ai=1)
        mc.select(all_Dyn)
    # 动力学状态列表
    def dyn_switch(self):
        mc.textScrollList(self.d4,e=1,ra=1)
        sacv=mc.textScrollList(self.d2,q=1,ai=1)
        if sacv==None:
            pass
        else :
            sacv2=[]
            for i in sacv:
                a=mc.getAttr(i+'.simulationMethod')
                if a==0 or a==1:
                    sa='off'
                else:
                    sa='on'
                sacv2.append(sa)
            mc.textScrollList(self.d4,e=1,a=sacv2)
    def dyn_select(self):
        mc.select( mc.textScrollList(self.d2,q=1,si=1))
        
    # 动力学开启/关闭
    def dyn_openclose(self):
        label=mc.button(self.d5,q=1,l=1)
        if label==u'开启动力学':
            openclose=1
        else :
            openclose=0
            
        sacv=mc.ls(sl=1)
        for i in sacv:
            if mc.attributeQuery('simulationMethod',node=i,ex=1)==0:
                mc.window(title=u"错误",wh=(150,50))
                mc.columnLayout( adjustableColumn=True )
                mc.text(l=u'请选择动力学控制器',h=50)
                mc.showWindow()
            else:
                if openclose==1:
                    mc.setAttr(i+'.simulationMethod',1)
                else :
                    mc.setAttr(i+'.simulationMethod',2)
                self.dyn_switch()
                
    # 去除要结算控制器 添加
    def add_remove_ctrl(self,a):
        sacv=mc.ls(sl=1,fl=1)
        if sacv != None:
            items=mc.textScrollList(a,q=1,ai=1)
            if items != None:
                aditem = [x for x in sacv if x not in items ]
                mc.textScrollList(a,e=1,append=aditem)
            else:
                mc.textScrollList(a,e=1,append=sacv)
    # 去除要结算控制器 清空
    def delete_remove_ctrl(self,a):
        mc.textScrollList(a,e=1,ra=1)
        
    # 选择列表内物体_函数
    def select_remove_ctrl(self,a):
          object=mc.textScrollList(a,q=1,ai=1)
          mc.select(object)


