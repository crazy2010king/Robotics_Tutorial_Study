# 《欠驱动机器人学》第三章通俗全解：杂技机器人、小车倒立摆与四旋翼

> **说明**：以下内容是经过与PDF原文逐页逐节对照、查漏补缺后的**最终综合版本**。所有公式概念无遗漏，代码实践部分做了重点扩展，并配有大量生活化类比。

---

## 开篇：为什么研究这些"玩具系统"？

作者说：这些低维模型系统**抓住了问题的本质，又没有引入真实世界的全部复杂性**。

> 🎯 **类比**：就像医学生先在塑料模型上练习手术，而不是直接给真人开刀。Acrobot、Cart-Pole、Quadrotor就是机器人控制领域的"塑料模型"——它们只有2-4个自由度，却包含了欠驱动控制的所有核心难题。

---

## 3.1 杂技机器人（The Acrobot）

### 🤸 它是什么？

Acrobot是一个**平面双连杆机械臂**，在垂直平面内运动（对抗重力）：
- **肩部**：没有电机（自由关节，像人的肩膀挂在固定支点上）
- **肘部**：有电机（可以施加力矩 τ，像体操运动员的腰部发力）

它得名于"Acrobat（杂技演员）"——像一个体操运动员在单杠上，主要靠**腰部扭动**（肘部力矩）来控制全身摆动，而不是靠手腕（肩部）发力。

它的"兄弟"系统叫 **Pendubot**：肩部有电机，肘部没有。

### 🎯 核心任务：Swing-Up（摆起并平衡）

从两杆自然下垂的状态，只用肘部电机，把系统甩到**两杆都竖直向上**（$\theta_1=\pi, \theta_2=0$），然后停在那里保持平衡。

> 🎪 **类比**：想象你单手抓住单杠，身体下垂。规则是：你的**手腕不能用力**（肩部无驱动），只能通过**扭腰**（肘部驱动）把自己甩上去，最后倒立在单杠上。这就是Acrobot的核心挑战。

### 🔗 核心挑战：状态依赖的耦合

为了摆起和平衡整个系统，控制器必须**理解并利用**驱动自由度（肘部）与非驱动自由度（肩部）之间的**耦合**。这种耦合不是固定的，而是随状态（角度、速度）变化的。

> 🚴 **类比**：骑自行车时，你不能直接控制"倾斜角度"（无驱动），只能通过车把和前轮的转向（有驱动）来间接影响。而且转弯产生的离心力与当前速度、倾斜角都有关——这就是"状态依赖的耦合"。

### 📝 运动方程（操作器方程形式）

Acrobot的动力学可以写成标准的**操作器方程**：

$$M(q)\ddot{q} + C(q,\dot{q})\dot{q} = \tau_g(q) + Bu$$

其中：
- $q = [\theta_1, \theta_2]^T$：关节角度向量
- $M(q)$：质量矩阵（与位形有关，就像你伸懒腰时身体"感觉更重"）
- $C(q,\dot{q})$：科氏力和离心力项（快速运动时出现的"虚拟力"）
- $\tau_g(q)$：重力项
- $B = [0, 1]^T$：输入矩阵（只有第二个关节有输入）

> 💡 **通俗理解**：左边是"系统想怎么动"（惯性+速度效应），右边是"外界推了它什么"（重力+电机力矩）。

**不稳定平衡点**：$x = [\pi, 0, 0, 0]^T$（两杆都竖直向上，速度为零）。就像铅笔倒立在桌面上。

### 💻 代码实践：在Drake中实验Acrobot

```python
from pydrake.all import *
# 加载Acrobot模型
builder = DiagramBuilder()
plant, scene_graph = AddMultibodyPlantSceneGraph(builder, time_step=0.001)
# 使用Drake内置的Acrobot模型或自定义URDF
acrobot = builder.AddSystem(AcrobotPlant())
# 你可以在这里施加不同的控制力矩，观察相图变化
```

讲义中提到："You can experiment with the Acrobot dynamics in Drake using..."，你可以在Drake的示例库中找到完整的Acrobot仿真。

---

## 3.2 小车-摆杆系统（The Cart-Pole）

### 🚂 它是什么？

一个小车可以在水平轨道上左右移动，车上立着一个可以转动的摆杆。

- **小车**：受水平力 $f_x$ 驱动（有电机）
- **摆杆**：只在底部与小车连接，**没有直接驱动**（无电机）

### ⚠️ 角度定义的陷阱（非常重要！）

PDF中明确定义：
- **$x$**：小车的水平位置
- **$\theta$**：摆杆的逆时针角度
- **$\theta = 0$**：摆杆竖直**向下**（自然下垂）
- **$\theta = \pi$**：摆杆竖直**向上**（不稳定平衡点）

> 🎯 **任务**：稳定不稳定固定点 $x = [0, \pi, 0, 0]^T$（小车在原点，摆杆竖直向上，两者速度均为零）。

> ⚠️ **注意**：很多教材把 $\theta=0$ 定义为向上。但Tedrake教授的定义是 $\theta=0$ 向下！读代码和做题时一定要确认这个定义，否则所有符号都会反。

### 📝 运动方程

通过Lagrange方法推导，得到：

$$(m_c + m_p)\ddot{x} + m_p l \ddot{\theta}\cos\theta - m_p l \dot{\theta}^2 \sin\theta = f_x$$

$$m_p l \ddot{x}\cos\theta + m_p l^2 \ddot{\theta} + m_p g l \sin\theta = 0$$

写成操作器方程形式：
- $q = [x, \theta]^T$
- $u = f_x$

$$M(q)\ddot{q} + C(q,\dot{q})\dot{q} = \tau_g(q) + Bu$$

其中：
$$M(q) = \begin{bmatrix} m_c+m_p & m_p l \cos\theta \\ m_p l \cos\theta & m_p l^2 \end{bmatrix}$$

$$C(q,\dot{q}) = \begin{bmatrix} 0 & -m_p l \dot{\theta}\sin\theta \\ 0 & 0 \end{bmatrix}, \quad \tau_g(q) = \begin{bmatrix} 0 \\ -m_p g l \sin\theta \end{bmatrix}, \quad B = \begin{bmatrix} 1 \\ 0 \end{bmatrix}$$

### 🧮 显式解出加速度

PDF中给出了直接解出的形式（通过求 $M^{-1}$）：

$$\ddot{x} = \frac{1}{m_c + m_p \sin^2\theta}\left[f_x + m_p\sin\theta(l\dot{\theta}^2 + g\cos\theta)\right]$$

$$\ddot{\theta} = \frac{1}{l(m_c + m_p\sin^2\theta)}\left[-f_x\cos\theta - m_p l\dot{\theta}^2\cos\theta\sin\theta - (m_c+m_p)g\sin\theta\right]$$

> 🎪 **类比**：分母中的 $\sin^2\theta$ 就像一个"干扰因子"——当摆杆水平时（$\theta=\pi/2$），分母最大，小车的加速度响应最弱。就像你推一个购物车，车上挂着的重物横着甩时，推车最费劲。

### 🧮 简化版（所有常数设为1）

为了分析方便，讲义设 $m_c=m_p=l=g=1$，得到：

$$2\ddot{x} + \ddot{\theta}\cos\theta - \dot{\theta}^2\sin\theta = f_x$$

$$\ddot{x}\cos\theta + \ddot{\theta} + \sin\theta = 0$$

这是后续PFL推导的基础。

---

## 3.3 四旋翼（Quadrotors）

### 🚁 背景

四旋翼在过去十年爆发式增长，因为无刷电机变得强大、轻便、便宜。Tedrake教授最初以为固定翼飞机会更有优势（因为前飞效率更高），但他错了——四旋翼因为**更容易控制**，完全主导了商业无人机市场。

### 3.3.1 平面四旋翼（Planar Quadrotor）

把四旋翼限制在平面内运动，只需要**两个螺旋桨**（但习惯仍叫Quadrotor）：

$$m\ddot{x} = -(u_1+u_2)\sin\theta$$
$$I\ddot{\theta} = r(u_1-u_2)$$

- $u_1, u_2$：两个螺旋桨的推力
- $r$：螺旋桨到中心的距离
- 第一个方程：水平方向的力是总推力在水平方向的投影
- 第二个方程：两个螺旋桨的推力差产生旋转力矩

> 🎪 **类比**：就像你左右手各拿一个风扇。两个风扇一起加大马力，飞机上升；一个加大一个减小，飞机旋转。但你不能直接控制"水平移动"——必须通过倾斜机身（改变 $\theta$）让推力有水平分量。

### 3.3.2 完整3D四旋翼（Full 3D Quadrotor）

3D模型的复杂性主要来自**旋转的处理**。

**关键细节**：
- **螺旋桨旋转产生的力矩（gyroscopic effects）**：如果不包含这些力矩，系统在悬停状态线性化后实际上是**不可控的**！
- **四元数 vs RPY**：MultibodyPlant默认用四元数表示方向，但线性化时如果不处理单位范数约束，会导致不可控。讲义中手动添加了"roll-pitch-yaw"浮动基座来简化线性化，但这会在"gimbal lock（万向节锁死）"处引入奇点。

> 🎪 **类比**：万向节锁死就像你仰头看天时，突然分不清"左右转头"和"歪头"的区别——两个旋转轴对齐了，丢失了一个自由度。这就是为什么游戏开发者和航天工程师都讨厌欧拉角。

### 💻 代码实践：Drake中的四旋翼

讲义提到，你可以用两种方法实现：
1. **手写方程**：QuadrotorPlant示例
2. **MultibodyPlant**：更方便添加碰撞、悬挂负载等。只需手动将螺旋桨力接入Diagram（因为URDF/SDF还不原生支持Propeller概念）

```python
# 使用MultibodyPlant构建带螺旋桨的四旋翼
builder = DiagramBuilder()
plant, scene_graph = AddMultibodyPlantSceneGraph(builder, 0.001)
# 加载URDF/SDF
parser = Parser(plant)
parser.AddModelFromFile("quadrotor.urdf")
# 手动添加Propeller力
propeller = builder.AddSystem(Propeller(plant, ...))
builder.Connect(propeller.get_output_port(), plant.get_applied_spatial_force_input_port())
```

---

## 3.4 平衡控制（Balancing）

对于Acrobot和Cart-Pole，第一步是设计一个**线性控制器**，在不稳定固定点附近保持平衡。

**标准流程**：线性化 → 检查能控性 → LQR设计反馈控制器。

### 3.4.1 线性化操作器方程

在固定点 $(x^*, u^*)$ 附近做Taylor展开：

$$\dot{x} = f(x,u) \approx f(x^*,u^*) + \left[\frac{\partial f}{\partial x}\right](x-x^*) + \left[\frac{\partial f}{\partial u}\right](u-u^*)$$

在固定点处 $f(x^*,u^*) = 0$，定义 $\bar{x} = x-x^*, \bar{u} = u-u^*$，得到：

$$\dot{\bar{x}} = A_{lin}\bar{x} + B_{lin}\bar{u}$$

对于操作器方程，线性化后的分块矩阵形式非常简洁：

$$A_{lin} = \begin{bmatrix} 0 & I \\ M^{-1}\frac{\partial \tau_g}{\partial q} + \sum_j M^{-1}\frac{\partial B_j}{\partial q}u_j & 0 \end{bmatrix}_{x=x^*,u=u^*}$$

$$B_{lin} = \begin{bmatrix} 0 \\ M^{-1}B \end{bmatrix}_{x=x^*,u=u^*}$$

**为什么这么简单？**
- 固定点处速度为零 $\Rightarrow$ 科氏力项 $C(q,\dot{q})\dot{q}$ 消失
- 固定点处 $\tau_g + Bu = 0$（力平衡）
- 很多情况下 $B$ 是常数矩阵 $\Rightarrow$ $\frac{\partial B}{\partial q}$ 项消失

**线性化与稳定性的关系**：
- **严格稳定**的线性化 $\Rightarrow$ 非线性系统**局部指数稳定**
- **不稳定**的线性化 $\Rightarrow$ 非线性系统**局部不稳定**
- **边缘稳定**（特征值实部为零）$\Rightarrow$ **无法得出结论**（可能是稳定、不稳定或Lyapunov稳定）

> 🎪 **类比**：线性化就像用放大镜看地图。严格稳定意味着"你确实站在一个坑里"（会回去）；不稳定意味着"你确实站在山顶"（会滚下去）；边缘稳定意味着"你站在平地上"——放大镜看不出你是会停住还是会慢慢滑走。

### 3.4.2 能控性：欠驱动 ≠ 不可控

**定义**：如果存在无约束输入 $u(t)$，能在有限时间内将系统从任意初态转移到任意终态，则系统是能控的。

**特征值分析直觉（非重复特征值情况）**：

将系统转换到**模态坐标** $r = V^{-1}x$（$V$ 是特征向量矩阵），动力学对角化为：

$$\dot{r}_i = \lambda_i r_i + \sum_j \beta_{ij} u_j$$

> 🎹 **类比**：想象一个房间有多个共振频率（模态）。每个输入 $u_j$ 就像在不同位置敲鼓。如果对于每个共振频率，至少有一个敲击位置能激起它（$\beta_{ij} \neq 0$），那么这个系统就是能控的。

**惊人结论**：Acrobot和Cart-Pole在倒立点线性化后，**都是能控的！**

> 🤯 **为什么惊人？** 它们都是欠驱动的（执行器比自由度少）。但这**不意味着**不可控！
> 
> **关键区分**：
> - **欠驱动** = 不能跟踪**任意轨迹**（不能随心所欲地规定每毫秒的位置）
> - **不可控** = 不能到达**任意状态点**（有些地方永远去不了）
> 
> 欠驱动系统虽然不能走任意路径，但**可以**通过巧妙 maneuvering 到达目标状态。就像你不能让自行车直线横着走，但你可以通过蛇形最终到达任何位置。

**能稳性（Stabilizability）**：

比能控性**更弱**。只要求系统能渐近收敛到原点（允许无限长时间），不要求有限时间到达。

如果系统的**不可控子空间**本身是稳定的（比如某些模态自然衰减），那么系统是能稳的。

**Brockett的著名结果**：对于非线性系统，能控性**不一定**意味着可以用**光滑控制律**稳定。这比线性系统微妙得多。

### 3.4.3 LQR反馈控制

**问题**：能控性只告诉我们"存在一条路"，但没告诉我们"走哪条路最好"。

**LQR（线性二次调节器）** 解决了这个问题。它最小化代价函数：

$$J(x_0) = \int_0^\infty \left[x^T(t)Qx(t) + u^T(t)Ru(t)\right] dt$$

- $Q$：状态偏差惩罚（你有多讨厌偏离目标）
- $R$：控制 effort 惩罚（你有多讨厌用力）

> 🎛️ **类比**：$Q$ 和 $R$ 就像音响的调音台。
> - $Q$ 调大 = "对误差零容忍"（机器人会拼命纠正，可能震荡）
> - $R$ 调大 = "省电模式"（机器人懒得用力，收敛慢但平稳）

**Drake中的LQR（一行代码搞定）**：

```python
# 自动在平衡点线性化并设计LQR控制器
controller = LinearQuadraticRegulator(system, context, Q, R)
```

Drake会自动：
1. 找到平衡点
2. 计算Jacobian得到 $A_{lin}, B_{lin}$
3. 求解Riccati方程得到最优反馈矩阵 $K$
4. 返回控制器 $u = -K(x - x^*)$

**重要性质**：
- 如果线性化系统**能稳**，对任意 $Q \geq 0, R > 0$，LQR都能给出**稳定**的控制器
- 如果系统**不能稳**，LQR会告诉你：**不存在线性稳定控制器**

### 💻 代码实践：LQR调参实验

讲义提供了两个Deepnote链接（Acrobot和Cart-Pole），你可以：

```python
import numpy as np
from pydrake.all import LinearQuadraticRegulator

# 定义Q和R矩阵
Q = np.diag([10, 10, 1, 1])  # 重视位置，轻视速度
R = np.diag([1])             # 中等控制代价

# 设计控制器
controller = LinearQuadraticRegulator(plant, context, Q, R)

# 仿真闭环响应
simulator = Simulator(plant)
# 观察：有时状态必须先远离原点，才能最终到达原点！
```

> 🎪 **观察现象**：在仿真中你会发现，有时小车需要先往**反方向**跑一下，才能把摆杆甩上去。这就像你倒车入库——想最终停到正确位置，有时必须先远离一下。

**非最小相位（Non-minimum phase）**：

Acrobot线性化后有**3个右半平面零点**，Cart-Pole有**1个**。这意味着系统存在"逆动态响应"：你命令它往左，它一开始会先往右。这是欠驱动系统的固有特性。

---

## 3.5 部分反馈线性化（Partial Feedback Linearization, PFL）

欠驱动系统**不能完全反馈线性化**（不能变成 $\ddot{q} = u$ 这种简单形式）。但我们可以线性化**一部分**动力学。

### 3.5.1 小车-摆杆的PFL

#### Collocated PFL（共位）：控制小车，间接影响摆杆

从简化方程出发，设计控制律：

$$f_x = (2-\cos^2\theta)\ddot{x}_d - \sin\theta\cos\theta - \dot{\theta}^2\sin\theta$$

结果是：
$$\ddot{x} = \ddot{x}_d$$
$$\ddot{\theta} = -\ddot{x}_d\cos\theta - \sin\theta$$

> 🎪 **类比**：这就像你推购物车（直接控制小车加速度），而车上的摆杆被动响应。神奇的是，摆杆的方程退化为**简单单摆**的形式，只是"重力"被 $\ddot{x}_d$ 调制了。

**控制权威的限制**：当 $\theta = \pm\pi/2$（摆杆水平）时，$\cos\theta = 0$，你对摆杆的"间接控制力矩"为零。就像你水平举着一根长杆，推车对杆的转动没有影响。

#### Non-collocated PFL（非共位）：直接控制摆杆！

更令人惊讶：我们可以通过控制小车，**直接指定摆杆的加速度**！

设计控制律：

$$f_x = \left(\cos\theta - \frac{2}{\cos\theta}\right)\ddot{\theta}_d - 2\tan\theta - \dot{\theta}^2\sin\theta$$

结果是：
$$\ddot{\theta} = \ddot{\theta}_d$$
$$\ddot{x} = -\frac{1}{\cos\theta}\ddot{\theta}_d - \tan\theta$$

> 🤯 **类比**：这就像你站在地上，通过推拉一根绳子（小车）来精确控制绳另一端的铃铛（摆杆）的角度。理论上可行，但——

**严重限制**：
- 只在 $\cos\theta \neq 0$ 时有效（摆杆不能水平）
- 当 $\theta \to \pm\pi/2$ 时，控制器会**blow-up**（要求无穷大的力）！
- **实际建议**：在硬件或仿真中实现时，**一定要对指令做饱和处理（saturation）**！

讲义还指出：$\left|\cos\theta - \frac{2}{\cos\theta}\right| \geq 1$，这至少给了我们一个下界保证。

### 3.5.2 一般形式

将关节分为：
- $q_1 \in \mathbb{R}^l$：被动关节（无驱动）
- $q_2 \in \mathbb{R}^m$：主动关节（有驱动）
- $l = n - m$（欠驱动度）

操作器方程分块：

$$M_{11}\ddot{q}_1 + M_{12}\ddot{q}_2 = \tau_1$$
$$M_{21}\ddot{q}_1 + M_{22}\ddot{q}_2 = \tau_2 + u$$

#### Collocated线性化（控制主动关节）

通过Schur补（Schur complement）条件，矩阵 $(M_{22} - M_{21}M_{11}^{-1}M_{12})$ 可逆，得到：

$$\ddot{q}_2 = u_{cmd}$$

这在**全局**有效。

#### Non-collocated线性化（控制被动关节）

使用Moore-Penrose伪逆：

$$\ddot{q}_1 = \ddot{q}_1^d \Rightarrow \ddot{q}_2 = M_{12}^+[\tau_1 - M_{11}\ddot{q}_1^d]$$

**关键条件——强惯性耦合（Strong Inertial Coupling）**：

要求 $\text{rank}(M_{12}) = l$（被动自由度的数量）。在Cart-Pole中，$M_{12} = \cos\theta$，在 $\theta=\pm\pi/2$ 时秩降为0。

**全局强惯性耦合**：在每个状态都满足强惯性耦合。这是一个很强的条件。

### 🎯 任务空间PFL（Task-Space PFL）

更一般地，我们可能不想控制某个关节，而是控制某个**任务空间**的输出：

$$y = h(q)$$

**定理3.1**：如果定义 $\bar{H} = H_2 - H_1 M_{11}^{-1} M_{12}$，且 $\text{rank}(\bar{H}) = p$（任务空间维度），那么通过控制主动关节：

$$\ddot{q}_2 = \bar{H}^+[\ddot{y}_d - \dot{H}\dot{q} - H_1 M_{11}^{-1}\tau_1]$$

可以实现 $\ddot{y} = \ddot{y}_d$。

> 🎪 **类比**：任务空间就像"指哪打哪"。你不是在控制"肘关节角度"，而是在控制"手的位置"。定理3.1告诉你：只要任务空间与主动关节之间有足够的"惯性耦合"，你就能直接控制任务空间加速度。

**示例3.7**：Cart-Pole末端执行器的竖直位置跟踪

定义 $y = h(q) = -l\cos\theta$（摆杆末端的竖直高度），可以跟踪期望轨迹如：

$$y_d(t) = \frac{l}{2} + \frac{l}{4}\sin(t)$$

---

## 3.6 摆起控制（Swing-Up Control）

### 3.6.1 能量整形（Energy Shaping）

回忆上一章：给单摆"泵能量"直到它荡到顶部。这个思想可以推广到Acrobot和Cart-Pole。

**核心洞察**：只需**一个**执行器，就能改变系统的**总能量**。

### 3.6.2 Cart-Pole的能量整形（详细推导）

**步骤1**：使用Collocated PFL简化动力学

设所有参数为1，得到：
$$\ddot{x} = u$$
$$\ddot{\theta} = -u\cos\theta - \sin\theta$$

第二个方程恰好是**简单单摆**的形式，只是"输入"变成了 $u\cos\theta$。

**步骤2**：定义摆杆能量

单摆（单位质量、单位长度、单位重力）的能量：
$$E(x) = \frac{1}{2}\dot{\theta}^2 - \cos\theta$$

期望能量（倒立点的能量）：
$$E_d = 1$$

定义能量误差：
$$\tilde{E}(x) = E(x) - E_d$$

**步骤3**：设计控制器

计算能量变化率：
$$\dot{\tilde{E}} = \dot{E} = \dot{\theta}\ddot{\theta} + \dot{\theta}\sin\theta = \dot{\theta}[-u\cos\theta - \sin\theta] + \dot{\theta}\sin\theta = -u\dot{\theta}\cos\theta$$

设计：
$$u = k\dot{\theta}\cos\theta\tilde{E}, \quad k > 0$$

代入得：
$$\dot{\tilde{E}} = -k\dot{\theta}^2\cos^2\theta\tilde{E}$$

**分析**：
- $\dot{\tilde{E}}$ 总是与 $\tilde{E}$ 符号相反（当 $\tilde{E} > 0$ 时减小，当 $\tilde{E} < 0$ 时增大）
- 因此 $\tilde{E}$ 会趋向于0（能量趋向期望值）
- 但严格证明需要 **LaSalle不变集原理**（排除平凡固定点轨迹）

**步骤4**：回到完整系统，加入小车调节

实际不能只用能量控制器，否则小车会跑得无影无踪。需要加入PD项把小车拉回原点：

$$\ddot{x}_d = k_E \dot{\theta}\cos\theta\tilde{E} - k_p x - k_d \dot{x}$$

> 🎪 **类比**：这就像你荡秋千想荡到最高点，但脚下必须站在一块小垫子上。你不仅要泵能量让秋千越来越高（能量整形），还要不断调整脚下位置防止垫子滑走（PD调节）。

**步骤5**：切换到LQR平衡

当摆杆接近竖直向上（在LQR的吸引域内）时，**切换**到LQR控制器进行精细平衡。

**图3.4的相图**：展示了摆杆子系统的相轨迹。控制器将系统驱动到**同宿轨道（homoclinic orbit）**——一条刚好能到达山顶并停住的临界轨道。

> 🎢 **类比**：同宿轨道就像过山车"刚好到达最高点，速度降为零"。能量少一点就到不了顶，多一点就会翻过去。能量整形的目标就是把系统精确地"泵"到这个临界能量状态。

### 3.6.3 Acrobot的摆起

类似的方法：
1. 使用Collocated PFL
2. 能量整形（系统总能量 = 动能 + 势能）
3. 加入额外PD项防止关节漂移
4. 接近目标时切换到LQR

讲义提到Spong的多个参考文献提供了不同变体。

### 3.6.4 讨论：技巧的局限

能量整形控制器是**非线性欠驱动控制**的典型代表：
- 需要巧妙的坐标变换抵消非线性项
- 需要巧妙的Lyapunov函数证明稳定性
- PFL用于简化方程

> ⚠️ **重要转折**：作者指出，这些"技巧"有**根本局限性**。书中后续内容将强调**更通用的计算方法**（如轨迹优化、微分平坦性、强化学习等）。

**微分平坦性（Differential Flatness）**：一种更现代的轨迹规划方法，在某些系统中可以比PFL更方便地生成动态轨迹。

---

## 3.7 其他模型系统

讲义列举了其他常用的欠驱动模型系统：

| 系统 | 描述 |
|------|------|
| **Pendubot** | Acrobot的"兄弟"：肩部有驱动，肘部无驱动 |
| **Inertia Wheel Pendulum** | 惯性轮摆：底部有旋转飞轮的单摆，通过飞轮转动产生力矩 |
| **Furuta Pendulum** | 古田摆：水平旋转臂+垂直摆杆，经典控制实验装置 |
| **Hovercraft** | 气垫船：侧向无推力，只能前后推进和旋转 |

---

## 3.8 练习详解与代码指南

### 📓 Exercise 3.1：Cart-Pole线性化与平衡

**目标**：在notebook中完成以下任务：

**a. 推导状态空间动力学**
- 从操作器方程出发，定义状态 $x = [q, \dot{q}]^T = [x, \theta, \dot{x}, \dot{\theta}]^T$
- 写出 $\dot{x} = f(x, u)$ 的显式形式（利用 $M^{-1}$）

**b. 在不稳定平衡点线性化**
- 平衡点：$x^* = [0, \pi, 0, 0]^T, u^* = 0$
- 计算Jacobian矩阵 $A = \frac{\partial f}{\partial x}|_{x^*}, B = \frac{\partial f}{\partial u}|_{x^*}$

**c. 分析线性化误差**
- 比较真实非线性动力学 $f(x,u)$ 与线性近似 $A(x-x^*) + B(u-u^*)$ 在不同状态下的差异
- 远离平衡点时，误差会增大

**d. 识别LQR稳定的状态**
- 运行LQR控制器，观察哪些状态分量被成功调节到零
- 注意：LQR只在局部有效，远离平衡点时可能失效

```python
# 典型代码框架
import numpy as np
from pydrake.all import *

# 构建Cart-Pole系统
builder = DiagramBuilder()
plant, scene_graph = AddMultibodyPlantSceneGraph(builder, 0.001)
# ... 加载URDF或手写动力学

# 找到平衡点
context = plant.CreateDefaultContext()
plant.SetPositions(context, [0, np.pi])  # θ=π（向上）
plant.SetVelocities(context, [0, 0])

# 线性化
linearized_plant = Linearize(plant, context)

# 设计LQR
Q = np.diag([10, 10, 1, 1])
R = np.diag([1])
controller = LinearQuadraticRegulator(linearized_plant.A(), linearized_plant.B(), Q, R)
```

---

### 📓 Exercise 3.2：编写URDF与双摆Cart-Pole

**a. 单摆杆Cart-Pole的URDF**

URDF（Unified Robot Description Format）是描述机器人结构的XML文件。

```xml
<?xml version="1.0"?>
<robot name="cart_pole">
  <!-- 小车（滑动关节） -->
  <link name="cart">
    <inertial>
      <mass value="1.0"/>
      <inertia ixx="0.1" ixy="0" ixz="0" iyy="0.1" iyz="0" izz="0.1"/>
    </inertial>
    <visual>
      <geometry><box size="0.5 0.3 0.2"/></geometry>
    </visual>
  </link>
  
  <!-- 摆杆（旋转关节） -->
  <link name="pole">
    <inertial>
      <mass value="1.0"/>
      <inertia ixx="0.01" ixy="0" ixz="0" iyy="0.01" iyz="0" izz="0"/>
    </inertial>
    <visual>
      <geometry><cylinder radius="0.02" length="1.0"/></geometry>
    </visual>
  </link>
  
  <!-- 滑动关节：cart沿x轴 -->
  <joint name="slider" type="prismatic">
    <parent link="world"/>
    <child link="cart"/>
    <axis xyz="1 0 0"/>
    <limit lower="-10" upper="10"/>
  </joint>
  
  <!-- 旋转关节：pole绕y轴 -->
  <joint name="pin" type="continuous">
    <parent link="cart"/>
    <child link="pole"/>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
  </joint>
</robot>
```

**b. 双摆杆Cart-Pole**

修改URDF，在第一个摆杆末端再添加一个连杆和旋转关节：
- 在`pole` link末端添加`pole2` link
- 添加第二个`pin2`关节
- 测试LQR是否能控制这个更复杂的系统（提示：可能需要重新调参或更高级的控制器）

---

### 📓 Exercise 3.3：离散与连续LTI系统的能控性

**第一部分：离散时间双积分器**

系统：
$$x[n+1] = \begin{bmatrix} x_1[n] + x_2[n] \\ x_2[n] + u[n] \end{bmatrix}, \quad x_1, x_2, u \in \mathbb{Z}$$

**1. 画状态转移图**

在3×3网格上（$x_1, x_2 \in \{0,1,2\}$），对 $u = -1, 0, 1$ 画出状态转移边。

```python
import matplotlib.pyplot as plt
import numpy as np

# 绘制离散状态转移图
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
for idx, u in enumerate([-1, 0, 1]):
    ax = axes[idx]
    for x1 in range(3):
        for x2 in range(3):
            # 计算下一状态
            x1_next = x1 + x2
            x2_next = x2 + u
            ax.arrow(x1, x2, (x1_next-x1)*0.3, (x2_next-x2)*0.3, 
                     head_width=0.1, color='blue', alpha=0.7)
            ax.plot(x1, x2, 'ko', markersize=10)
            ax.text(x1, x2-0.2, f's_{x1},{x2}', ha='center')
    ax.set_title(f'u = {u}')
    ax.set_xlim(-0.5, 2.5)
    ax.set_ylim(-0.5, 2.5)
    ax.grid(True)
plt.show()
```

**2. 从 $s_{0,0}$ 到 $s_{i,j}$（$j > i > 0$）的最少步数**

分析：$x_2$ 是"速度"，$x_1$ 是"位置"。要增加 $x_1$，需要先增加 $x_2$（加速），再保持。最少步数可以通过递推或BFS计算。

**3. 从任意初态到任意终态的最少步数**

利用系统的结构特性：双积分器在整数格点上的能控性。

**第二部分：连续系统能控性判断**

判断以下系统是否能控：

$$A_1 = \begin{bmatrix} 1 & 0 \\ 0 & 1 \end{bmatrix}, B_1 = \begin{bmatrix} 0 \\ 1 \end{bmatrix}$$

$$A_2 = \begin{bmatrix} 1 & 0 \\ 0 & 1 \end{bmatrix}, B_2 = \begin{bmatrix} 1 \\ 1 \end{bmatrix}$$

$$A_3 = \begin{bmatrix} 0 & 1 \\ 0 & 0 \end{bmatrix}, B_3 = \begin{bmatrix} 0 \\ 1 \end{bmatrix}$$

$$A_4 = \begin{bmatrix} 0 & 0 & 1 & 0 \\ 0 & 0 & 0 & 1 \\ 0 & 1 & 0 & 0 \\ 0 & 2 & 0 & 0 \end{bmatrix}, B_4 = \begin{bmatrix} 0 \\ 0 \\ 1 \\ 1 \end{bmatrix}$$

**方法**：计算能控性矩阵 $\mathcal{C} = [B, AB, A^2B, \ldots]$ 的秩。

```python
import numpy as np

def controllability_matrix(A, B):
    n = A.shape[0]
    C = B
    for i in range(1, n):
        C = np.hstack([C, np.linalg.matrix_power(A, i) @ B])
    return C

# 检查A4, B4
A4 = np.array([[0,0,1,0],[0,0,0,1],[0,1,0,0],[0,2,0,0]])
B4 = np.array([[0],[0],[1],[1]])
C4 = controllability_matrix(A4, B4)
print(f"Rank of C4: {np.linalg.matrix_rank(C4)}")
```

**欠驱动判断**：

对于 $(A_3, B_3)$ 和 $(A_4, B_4)$，注意欠驱动的定义要求系统被解释为**二阶系统**（即 $x = [q, \dot{q}]^T$）。检查 $B$ 矩阵是否对应"某些自由度没有直接驱动"。

---

### 📓 Exercise 3.4：非线性系统与线性化的稳定性比较

**参数**：$m=1, l=1, g=9.81$

**目标**：完成表格，比较非线性系统和其线性化在各种情况下的稳定性。

**a. 无阻尼单摆（$b=0$）**

**1. 画相图并判断非线性系统稳定性**

```python
import numpy as np
import matplotlib.pyplot as plt

def pendulum_dynamics(x):
    theta, theta_dot = x
    theta_ddot = -9.81 * np.sin(theta)
    return np.array([theta_dot, theta_ddot])

# 画相图
theta = np.linspace(-np.pi, np.pi, 20)
theta_dot = np.linspace(-10, 10, 20)
THETA, THETA_DOT = np.meshgrid(theta, theta_dot)

U = THETA_DOT
V = -9.81 * np.sin(THETA)

plt.figure(figsize=(10, 6))
plt.quiver(THETA, THETA_DOT, U, V, alpha=0.6)
plt.xlabel('θ')
plt.ylabel('θ̇')
plt.title('Undamped Pendulum Phase Portrait')
plt.axhline(0, color='k', linewidth=0.5)
plt.axvline(0, color='k', linewidth=0.5)
plt.plot(0, 0, 'ro', markersize=10, label='Stable (center)')
plt.plot(np.pi, 0, 'bo', markersize=10, label='Unstable (saddle)')
plt.legend()
plt.grid(True)
plt.show()
```

**结论**：
- $x^* = [0, 0]^T$（向下）：**Lyapunov稳定**（i.s.L.）但不是渐近稳定（无阻尼，永远摆动）
- $x^* = [\pi, 0]^T$（向上）：**不稳定**

**2. 线性化并计算特征值**

在 $[0,0]$ 处：$\sin\theta \approx \theta$，方程变为 $\ddot{\theta} + 9.81\theta = 0$

Jacobian：
$$A = \begin{bmatrix} 0 & 1 \\ -g\cos\theta & 0 \end{bmatrix}$$

在 $[0,0]$：$A = \begin{bmatrix} 0 & 1 \\ -9.81 & 0 \end{bmatrix}$，特征值 $\lambda = \pm i\sqrt{9.81}$（纯虚数）

**3. 线性化系统稳定性**
- 特征值实部为0 $\Rightarrow$ **边缘稳定**
- 线性化无法判断非线性系统的稳定性（恰好是讲义中提到的微妙情况！）

在 $[\pi,0]$：令 $\phi = \theta - \pi$，$\sin\theta = -\sin\phi \approx -\phi$

$A = \begin{bmatrix} 0 & 1 \\ 9.81 & 0 \end{bmatrix}$，特征值 $\lambda = \pm\sqrt{9.81}$（一正一负）

**不稳定**（鞍点）。

**b. 有阻尼单摆（$b=1$）**

方程：$\ddot{\theta} + \dot{\theta} + 9.81\sin\theta = 0$

**1. 相图分析**

添加阻尼项后，相图上的轨迹会**螺旋向内**。

- $[0,0]$：**渐近稳定**（甚至指数稳定，因为阻尼使能量耗散）
- $[\pi,0]$：**不稳定**

**2. 线性化特征值**

在 $[0,0]$：
$$A = \begin{bmatrix} 0 & 1 \\ -9.81 & -1 \end{bmatrix}$$

特征值：$\lambda = \frac{-1 \pm \sqrt{1 - 39.24}}{2} = -0.5 \pm i\sqrt{9.56}$

实部为负 $\Rightarrow$ **严格稳定** $\Rightarrow$ 非线性系统**局部指数稳定**。

在 $[\pi,0]$：
$$A = \begin{bmatrix} 0 & 1 \\ 9.81 & -1 \end{bmatrix}$$

特征值：一正一负 $\Rightarrow$ **不稳定**。

**完整表格**：

| 系统 | 平衡点 | Re(λ₁) | Re(λ₂) | 非线性稳定性 | 线性化稳定性 |
|------|--------|--------|--------|-------------|-------------|
| b=0 | [0,0] | 0 | 0 | i.s.L. | 边缘稳定 |
| b=0 | [π,0] | + | - | 不稳定 | 不稳定 |
| b=1 | [0,0] | - | - | 渐近/指数稳定 | 指数稳定 |
| b=1 | [π,0] | + | - | 不稳定 | 不稳定 |

> 💡 **核心教训**：当线性化是**边缘稳定**时（无阻尼情况），我们不能从线性化推断非线性系统的稳定性。这就是为什么需要相图、Lyapunov函数等更强大的工具。

---

## 总结：第三章教给我们的六件事

| 核心概念 | 通俗理解 | 实践意义 |
|---------|---------|---------|
| **欠驱动 ≠ 不可控** | 自行车不能横着走，但能到任何地方 | 别因为执行器少就放弃，要巧妙利用耦合 |
| **线性化是局部放大镜** | 只能在平衡点附近信任 | 远离平衡点时必须用非线性方法 |
| **LQR是万能起点** | 调两个旋钮（Q/R）就能出稳定控制器 | Drake中一行代码搞定，但要懂调参 |
| **PFL是化繁为简** | 把复杂系统的一部分变简单 | Collocated安全，Non-collocated强大但有奇点 |
| **能量整形是物理直觉** | 像荡秋千一样"泵能量" | Swing-up任务的自然解决方案 |
| **混合策略最实用** | 能量整形甩上去 + LQR稳住 | 真实机器人控制的标准范式 |

---

**参考文献提示**：本章引用了Spong、Murray、Hauser、Khalil、Slotine等控制学大师的经典著作。如果你想深入，推荐阅读Slotine & Li的《Applied Nonlinear Control》和Khalil的《Nonlinear Systems》。

*本讲义配套代码和视频可在MIT 6.832课程主页和YouTube频道找到。建议配合Drake仿真环境动手实验每一个概念。*