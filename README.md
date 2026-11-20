# Maya 绳索绑定工具 — SplineIK_Tool

从 Mking_Tool 中剥离的独立 Spline IK 工具，包含曲线绑定、动力学动画、曲线蒙皮权重平滑，以及多点附着的长路径绑定。

## 环境要求

- 在 Autodesk Maya 内运行，不能作为普通 Python 桌面程序运行。
- 路径功能已在 Maya 2020、2024、2025 中通过回归测试。
- 使用 Maya 自带的 `maya.cmds`、`maya.mel`、`maya.OpenMaya`。
- rigging 页的 `point` 模式额外依赖 `pymel.core`；若环境未安装 PyMEL，优先使用 `path` 模式。
- 不需要安装原始 Mking_Tool。

## 安装

下载仓库 ZIP 并解压，或执行：

```bash
git clone https://github.com/buxihuanchixiangcaidelibai/maya_shengzi_rig.git
```

保持目录结构，不要只复制某个核心文件：

```text
maya_shengzi_rig/
├── README.md
├── launch_splineik.py
└── SplineIK_Tool/
    ├── __init__.py
    ├── run_splineik.py
    ├── kxj_ik_UI_14.py
    ├── kxj_ik_dy305.py
    ├── splineik_weight.py
    ├── splineik_path.py
    └── splineik_path_ui.py
```

## 启动代码

### 推荐：Maya Python 脚本编辑器 / Shelf

假设仓库解压在 `D:\maya_shengzi_rig`。将下面的路径替换为自己的**仓库根目录**，它应包含 `SplineIK_Tool` 文件夹。

```python
import sys
repo_dir = r"D:\maya_shengzi_rig"
if repo_dir not in sys.path:
    sys.path.insert(0, repo_dir)
import SplineIK_Tool
SplineIK_Tool.show()
```

Maya 2020 的 Python 2 与 Maya 2024/2025 的 Python 3 均可使用此方式。添加 Shelf 按钮时，命令语言选择 **Python**，粘贴同一段代码。

### 拖放启动

将仓库根目录的 `launch_splineik.py` 拖入 Maya 视口。该脚本提供 `onMayaDroppedPythonFile` 入口，会根据自身文件位置找到工具，无需修改本机路径。

### 从指定文件启动（Python 2 / 3 通用）

在 Maya Python 脚本编辑器运行：

```python
script_path = r"D:\maya_shengzi_rig\launch_splineik.py"
with open(script_path, "rb") as stream:
    source = stream.read()
exec(compile(source, script_path, "exec"),
     {"__file__": script_path, "__name__": "__main__"})
```

请勿在 Python 3 Maya 中直接使用 `execfile()`；该函数只存在于 Python 2。直接执行文件时推荐上面的通用代码。

## 界面与基本操作

窗口有三个标签：`rigging`、`animation`、`weight`。

### 1. rigging — 创建绑定

1. 在 Maya 中绘制并选择一条 NURBS 曲线。
2. 填写唯一的绑定名字，例如 `shengzi`。建议使用字母、数字及下划线，避免空格和同名绑定。
3. 设置控制器数量、骨骼数量、基本朝向与向上朝向。两个朝向不能使用同一轴。
4. 按需勾选“动力学”“拉伸”；首次使用建议选择默认 `path` 模式。
5. 如需长路径绑定，在创建前勾选“启用路径控制器”，设置路径控制器数量。
6. 点击“3.创建控制器校轴参考物体”，检查并调整参考物体。
7. 点击“4.创建spline”，生成控制器和骨骼。

这里的 `path / point` 模式是原有控制器定位方式，与“启用路径控制器”复选框不是同一个开关。

第一节绳索控制器（例如 `shengzi_1`）上的常用属性：

| 属性 | 作用 |
| --- | --- |
| `stretch` | 原有拉伸幅度，范围 0～10；10 完全跟随拉伸，0 保持初始长度 |
| `Maintain_Length` | 保持长度混合，范围 0～1；0 保留 stretch 效果，1 将有效拉伸降为 0 |
| `Path_Ctrl_Vis` | 仅在创建路径系统后存在，控制路径控制器的可见性 |
| `Travel` | 仅在创建路径系统后存在，范围 0～10，驱动整条绳索沿路径移动 |

`Maintain_Length` 与 `stretch` 共同生效。有效拉伸值为 `stretch × (1 − Maintain_Length)`。需要完整路径塑形效果时，请检查拉伸设置。

### 2. 长路径绑定

- 创建条件：**开放 NURBS 曲线**，起点和终点不能重合；Maya Undo 必须开启。
- 根据源曲线起点到终点的方向生成直线路径，长度固定为起终点距离的 **10 倍**。
- 路径控制器默认 **50** 个，最少 **4** 个；勾选路径选项后才可编辑数量。
- 路径由控制器组成 FK 链，每节包含 `OffGrp / SdkGrp / Ctrl / Sub_Ctrl` 结构。
- 每个绳索驱动控制器有独立 follicle，驱动其 `*_world` 参考组；创建后各节 `follow` 自动设为 1。
- 路径曲面、关节和 follicle 放在技术组中并隐藏，不需要手动显示。

操作流程：

1. 选第一节绳索控制器，将 `Path_Ctrl_Vis` 设为 1。
2. 调整路径控制器的旋转来塑形；某一节控制器会带动其后面的路径链。
3. 如需局部微调，打开对应路径控制器的 `Sub_Ctrl_Vis`，操作子控制器。
4. 在第一节绳索控制器上调节 `Travel`，或给它设置关键帧。
5. `Travel=0` 保持初始附着位置，`Travel=10` 让最靠近路径终点的附着点到达终点。
6. 关闭 `Path_Ctrl_Vis` 可以隐藏路径控制器，不会停止驱动。

注意事项：

- `Travel` 让所有附着点增加相同的 V 参数偏移；路径弯曲后不保证世界空间的实际距离恒定。
- 路径模式下建议保持各绳索控制器 `follow=1`，否则该节会退出路径跟随。
- 两个路径属性仍挂在绳索首节控制器上，当前没有新增独立全局控制器。
- 路径系统在创建 spline 时生成；旧绑定不会自动升级，需要备份场景后重建。
- 路径创建失败会回滚此次路径创建，并显示警告，保留已经创建的 spline。

### 3. animation — 动力学与烘焙

1. 在创建绑定时启用动力学，按需使用“创建Dynamic控制器”“合并Dynamic”。
2. 到 animation 页点击“刷新”，选择动力学曲线。
3. 使用“开启动力学 / 关闭动力学”控制模拟，并按需创建碰撞体。
4. “自动”勾选时使用时间轴范围；取消勾选可手动指定 bake 起止帧。
5. 按需执行“bake动画到控制器”或“bake动画到骨骼”。

路径与动力学组合的具体动画效果应在自己的场景中检查，建议先验证普通路径绑定再叠加模拟。

### 4. weight — 曲线蒙皮权重

此页操作的是曲线 `skinCluster` 蒙皮权重，不是模型网格权重或曲线自身的 NURBS 权值。通常选择绑定生成的 `shengzi_drv_crv`。

**整条平滑：**

1. 点击“刷新曲线列表”，选择带蒙皮的驱动曲线；列表未选中时也可以直接在视口选曲线。
2. 设置平滑次数（默认 3）和强度（默认 0.5）。
3. 点击“一键平滑整条曲线权重”。

**选点平滑：**

1. 在视口切换到曲线 CV 组件选择模式，选中需要处理的 CV。
2. 点击“平滑所选点的权重”；只有选中的 CV 被写入新权重，其他点不修改。

也可以在 Maya Python 编辑器选择范围后点击该按钮：

```python
import maya.cmds as cmds
cmds.select("shengzi_drv_crv.cv[8:9]", replace=True)
```

“按位置重排权重（线性化）”会重写整条曲线权重，并按蒙皮影响对象的查询顺序进行线性分配；它不是普通平滑，使用前建议保存场景。权重操作支持 Undo。

## 删除绑定与更新

- 选择带删除标记的绳索控制器，点击 rigging 页的“删除spline”。
- 新版绑定登记了自身节点，删除时会清理路径控制器、曲面、约束、动画与依赖节点。
- 删除功能会保留原始输入曲线，不删除其他绑定的路径系统。
- 操作前保存场景；旧版本创建的绑定仍使用兼容清理逻辑。
- 更新仓库后关闭工具窗口并重新执行启动代码。已生成的场景节点不会自动迁移。

## 常见问题

| 问题 | 检查方式 |
| --- | --- |
| `No module named SplineIK_Tool` | 添加到 `sys.path` 的应是仓库根目录，而不是 `SplineIK_Tool` 文件夹本身 |
| Maya 中仍显示旧界面 | 关闭旧窗口后重新启动，确认仓库路径和加载版本 |
| `No module named pymel` | 优先使用 rigging 页的 `path` 模式，或为当前 Maya 安装兼容 PyMEL |
| 找不到曲线蒙皮权重 | 选择带 skinCluster 的驱动曲线；选点时必须选 CV，不是编辑点 EP |
| 找不到路径控制器 | 选首节绳索控制器，将 `Path_Ctrl_Vis` 设为 1 |
| Travel 只驱动部分控制器 | 检查各节 `follow=1`，并确认绑定是新版多点路径系统 |
| 路径创建失败 | 检查曲线开放、起终点不重合、名字无冲突、Undo 开启，并查看 Maya 警告 |

## 文件说明

| 文件 | 作用 |
| --- | --- |
| `launch_splineik.py` | 仓库级可移植启动入口，支持 Maya 拖放 |
| `SplineIK_Tool/__init__.py` | 包入口，提供 `show()` |
| `SplineIK_Tool/run_splineik.py` | 原有启动脚本；内含原开发目录的备用路径，优先使用仓库级新入口 |
| `SplineIK_Tool/kxj_ik_UI_14.py` | 三标签主界面 |
| `SplineIK_Tool/kxj_ik_dy305.py` | 原有绑定、动力学与删除核心 |
| `SplineIK_Tool/splineik_weight.py` | 曲线权重平滑 |
| `SplineIK_Tool/splineik_path.py` | 长路径、控制器、曲面、多点附着和清理 |
| `SplineIK_Tool/splineik_path_ui.py` | 创建时的路径勾选框与数量设置 |

原始绑定核心来源于 Mking_Tool 的牙签 spline 工具；路径功能参照 Curve_Rigger 的路径绑定机制适配。请保留现有源码署名和注释。
