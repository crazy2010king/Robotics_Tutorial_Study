# 《欠驱动机器人》第3章：Acrobot、倒立摆与四旋翼——完全通俗讲解

---

## 开篇：这一章到底在讲什么？

### 一句话概括

这一章讲的是：**当你手里的"遥控器按钮"比"需要控制的东西"少的时候，你该怎么办？**

### 生活类比

想象你在开一辆车：
- **全驱动（Fully Actuated）**：你有一个方向盘控制左右，一个油门控制前后，一个升降按钮控制上下。你想去哪就去哪，每个方向都有"按钮"。
- **欠驱动（Underactuated）**：你只有油门和刹车，没有方向盘。车只能沿直线走，但你可以通过巧妙利用惯性、摩擦力、地形，让车最终到达你想去的地方。

**欠驱动系统 = 控制输入的数量 < 自由度的数量**

这一章用三个经典例子来研究这个问题：
1. **Acrobot（双连杆摆）**：像体操运动员在单杠上摆动
2. **Cart-Pole（小车倒立摆）**：像用手掌平衡一根棍子
3. **Quadrotor（四旋翼）**：像无人机

---

## 3.1 Acrobot（双连杆摆）

### 3.1.1 它是什么？

**Acrobot = 一个两节手臂，只有肘关节有电机，肩关节没有电机。**

#### 生活类比

想象一个体操运动员挂在单杠上：
- **肩关节**（连接单杠的地方）= 没有电机，自由转动
- **肘关节**（两节手臂之间）= 有电机，可以施加力矩

运动员只能通过"收腹/展腹"（控制肘关节）来让自己从悬挂状态摆到倒立状态。这就是Acrobot的核心任务：**Swing-up（摆起）+ Balance（平衡）**。

#### 为什么叫"Acrobot"？

Acrobat（杂技演员）+ Robot（机器人）= Acrobot。因为它看起来就像一个杂技演员在单杠上做动作。

#### 它的"兄弟"：Pendubot

如果把电机从肘关节移到肩关节，就变成了Pendubot（Pendulum + Robot）。

#### 为什么Acrobot重要？

> "Acrobot代表了欠驱动机器人的核心挑战：控制器必须理解并利用**有电机关节**和**没电机关节**之间的**状态依赖耦合**。"

**通俗翻译**：你只能通过控制肘关节来间接影响肩关节。就像你坐在秋千上，只能通过身体前后摆动（肘关节动作）来让秋千越荡越高（肩关节运动）。你不能直接推秋千（没有肩关节电机），但你可以利用身体摆动的时机来"借力"。

#### 为什么它和行走机器人有关？

> "它也非常重要，因为我们将看到，它非常类似于行走机器人最简单的模型之一。"

**类比**：人走路时，支撑腿着地的那一刻，就像Acrobot的肩关节——地面反作用力通过脚传递，但你不能直接控制地面给你的力。你只能通过髋关节和膝关节的力矩来间接影响整体运动。

### 3.1.2 Acrobot的运动方程

#### 参数定义

```
θ₁ = 肩关节角度（从正下方量起）
θ₂ = 肘关节角度（相对角度）
q = [θ₁, θ₂]ᵀ = 广义坐标

m₁, m₂ = 两节连杆的质量
l₁ = 第一节连杆长度
lc₁, lc₂ = 各连杆质心到关节的距离
I₁, I₂ = 各连杆绕关节的转动惯量
g = 重力加速度
```

**零位配置**：两节连杆都垂直朝下（像钟摆自然悬挂）。

**目标**：稳定在不稳定平衡点 x = [π, 0, 0, 0]ᵀ（两节连杆都垂直朝上，像倒立）。

#### 用拉格朗日方法推导运动方程

**什么是拉格朗日方法？**

**类比**：牛顿力学是"逐个分析每个力"（像记账，每笔收支都要记）。拉格朗日方法是"只看总能量"（像看银行余额，不管每笔交易细节）。

- **动能 T**：系统因为运动而具有的能量
- **势能 U**：系统因为位置（高度）而具有的能量
- **拉格朗日量 L = T - U**

然后通过欧拉-拉格朗日方程：

$$\frac{d}{dt}\frac{\partial L}{\partial \dot{q}} - \frac{\partial L}{\partial q} = \tau$$

就能得到运动方程。

#### 具体推导

**质心位置（运动学）**：

第一节连杆质心：
$$p_{c1} = \begin{bmatrix} l_{c1}\sin\theta_1 \\ -l_{c1}\cos\theta_1 \end{bmatrix}$$

第二节连杆质心：
$$p_{c2} = \begin{bmatrix} l_1\sin\theta_1 + l_{c2}\sin(\theta_1+\theta_2) \\ -l_1\cos\theta_1 - l_{c2}\cos(\theta_1+\theta_2) \end{bmatrix}$$

**类比**：就像你伸出手臂，肘关节的位置取决于肩关节角度，手腕的位置取决于肩关节+肘关节角度。

**动能**：

$$T = T_1 + T_2$$

$$T_1 = \frac{1}{2}I_1\dot{q}_1^2$$

$$T_2 = \frac{1}{2}(m_2 l_1^2 + I_2 + 2m_2 l_1 l_{c2}\cos\theta_2)\dot{q}_1^2 + \frac{1}{2}I_2\dot{q}_2^2 + (I_2 + m_2 l_1 l_{c2}\cos\theta_2)\dot{q}_1\dot{q}_2$$

**通俗理解**：
- $T_1$：第一节连杆绕肩关节转动的动能
- $T_2$：第二节连杆的动能，包括：
  - 跟着第一节一起转的部分（$m_2 l_1^2$项）
  - 自己绕肘关节转的部分（$I_2$项）
  - 两者之间的**耦合项**（$\dot{q}_1\dot{q}_2$项）——这就是"状态依赖耦合"的数学体现

**势能**：

$$U = -m_1 g l_{c1}\cos\theta_1 - m_2 g(l_1\cos\theta_1 + l_{c2}\cos(\theta_1+\theta_2))$$

**通俗理解**：质心越高，势能越大。$\cos\theta$在θ=0（朝下）时最大，所以朝下时势能最小（最稳定）。

#### 最终运动方程（标准机械臂形式）

$$M(q)\ddot{q} + C(q,\dot{q})\dot{q} = \tau_g(q) + Bu$$

其中：

$$M(q) = \begin{bmatrix} I_1+I_2+m_2l_1^2+2m_2l_1l_{c2}\cos\theta_2 & I_2+m_2l_1l_{c2}\cos\theta_2 \\ I_2+m_2l_1l_{c2}\cos\theta_2 & I_2 \end{bmatrix}$$

$$C(q,\dot{q}) = \begin{bmatrix} -2m_2l_1l_{c2}\sin\theta_2\dot{q}_2 & -m_2l_1l_{c2}\sin\theta_2\dot{q}_2 \\ m_2l_1l_{c2}\sin\theta_2\dot{q}_1 & 0 \end{bmatrix}$$

$$\tau_g(q) = \begin{bmatrix} -m_1gl_{c1}\sin\theta_1 - m_2g(l_1\sin\theta_1+l_{c2}\sin(\theta_1+\theta_2)) \\ -m_2gl_{c2}\sin(\theta_1+\theta_2) \end{bmatrix}$$

$$B = \begin{bmatrix} 0 \\ 1 \end{bmatrix}$$

**各部分的物理意义**：

| 符号 | 名称 | 通俗含义 |
|------|------|---------|
| M(q) | 质量/惯量矩阵 | "推动这个东西有多难"——随姿态变化 |
| C(q,q̇)q̇ | 科里奥利力+离心力 | "旋转时产生的'假力'"——像旋转木马上感觉被甩出去 |
| τ_g(q) | 重力力矩 | "重力想把你拉下来"——像钟摆总是想回到最低点 |
| B | 输入矩阵 | "电机装在哪里"——B=[0,1]ᵀ表示只有第二个关节（肘）有电机 |

**关键观察**：B矩阵第一行是0！这意味着**没有直接的力矩作用在肩关节上**。这就是"欠驱动"的数学表达。

### 3.1.3 Drake代码实践

```python
# 在Drake中实验Acrobot动力学
# 文件路径：underactuated/acrobot.html

from pydrake.all import *
import numpy as np

# 创建Acrobot系统
acrobot = AcrobotPlant()
context = acrobot.CreateDefaultContext()

# 设置初始状态 [θ₁, θ₂, θ̇₁, θ̇₂]
acrobot.get_input_port().FixValue(context, [0.0])  # 无输入
context.SetContinuousState([0.1, 0.2, 0.0, 0.0])  # 初始偏离平衡

# 仿真
simulator = Simulator(acrobot, context)
simulator.AdvanceTo(5.0)  # 仿真5秒

# 观察：没有输入时，Acrobot就像自由摆动的双摆
```

**实验要点**：
- 试试不同的初始条件，观察双摆的混沌运动
- 施加不同的肘关节力矩，观察如何影响肩关节运动
- 体会"耦合"：肘关节的动作如何间接影响肩关节

---

## 3.2 Cart-Pole系统（小车倒立摆）

### 3.2.1 它是什么？

**Cart-Pole = 一个小车上竖着一根棍子，你只能水平推小车，目标是让棍子不倒。**

#### 生活类比

**最经典的类比**：你把手掌伸平，上面竖着一根扫帚。你只能通过水平移动手掌来保持扫帚不倒。

- **小车（Cart）**= 你的手掌（只能水平移动）
- **摆（Pole）**= 扫帚（会倒）
- **控制输入**= 你水平推小车的力
- **目标**= 让摆保持在垂直朝上的不稳定平衡点

#### 为什么重要？

> "平衡Cart-Pole系统被用在许多控制入门课程中，包括MIT的6.003，因为它可以用简单的线性控制（如极点配置）来完成。"

**但是**：这一章考虑的是**完整的摆起+平衡问题**，需要完整的非线性控制处理。

### 3.2.2 参数定义

```
x = 小车水平位置
θ = 摆的角度（逆时针为正，0=垂直朝下）
q = [x, θ]ᵀ

mc = 小车质量
mp = 摆的质量
l = 摆的长度（到质心）
g = 重力加速度
```

**目标**：稳定不稳定平衡点 x = [0, π, 0, 0]ᵀ（小车在原点，摆垂直朝上）。

### 3.2.3 运动方程推导

**运动学**：

摆的质心位置：
$$x_1 = \begin{bmatrix} x \\ 0 \end{bmatrix}, \quad x_2 = \begin{bmatrix} x + l\sin\theta \\ -l\cos\theta \end{bmatrix}$$

**类比**：小车在x位置，摆的质心在小车位置加上摆的偏移。当θ=0（朝下），质心在小车正下方；当θ=π（朝上），质心在小车正上方。

**动能**：

$$T = \frac{1}{2}(m_c+m_p)\dot{x}^2 + m_p\dot{x}\dot{\theta}l\cos\theta + \frac{1}{2}m_pl^2\dot{\theta}^2$$

**通俗理解**：
- 第一项：小车和摆一起水平移动的动能
- 第二项：**耦合项**——小车速度和摆角速度的交互（当摆倾斜时，小车移动会带动摆）
- 第三项：摆绕铰接点旋转的动能

**势能**：

$$U = -m_pgl\cos\theta$$

**运动方程**：

$$(m_c+m_p)\ddot{x} + m_pl\ddot{\theta}\cos\theta - m_pl\dot{\theta}^2\sin\theta = f_x$$

$$m_pl\ddot{x}\cos\theta + m_pl^2\ddot{\theta} + m_pgl\sin\theta = 0$$

**标准机械臂形式**：

$$M(q) = \begin{bmatrix} m_c+m_p & m_pl\cos\theta \\ m_pl\cos\theta & m_pl^2 \end{bmatrix}$$

$$C(q,\dot{q}) = \begin{bmatrix} 0 & -m_pl\dot{\theta}\sin\theta \\ 0 & 0 \end{bmatrix}$$

$$\tau_g(q) = \begin{bmatrix} 0 \\ -m_pgl\sin\theta \end{bmatrix}$$

$$B = \begin{bmatrix} 1 \\ 0 \end{bmatrix}$$

**关键观察**：B = [1, 0]ᵀ，表示力只作用在小车上（第一个自由度），摆（第二个自由度）没有直接力矩。

### 3.2.4 简化形式（所有常数设为1）

为了分析方便，设所有常数=1：

$$2\ddot{x} + \ddot{\theta}\cos\theta - \dot{\theta}^2\sin\theta = f_x$$

$$\ddot{x}\cos\theta + \ddot{\theta} + \sin\theta = 0$$

**为什么这样做？** 就像物理课上先忽略空气阻力、摩擦力，抓住核心物理。具体数值可以后面再代入。

### 3.2.5 直接求解加速度

Cart-Pole的一个好处是可以**显式解出加速度**：

$$\ddot{x} = \frac{1}{m_c+m_p\sin^2\theta}[f_x + m_p\sin\theta(l\dot{\theta}^2 + g\cos\theta)]$$

$$\ddot{\theta} = \frac{1}{l(m_c+m_p\sin^2\theta)}[-f_x\cos\theta - m_pl\dot{\theta}^2\cos\theta\sin\theta - (m_c+m_p)g\sin\theta]$$

**通俗理解**：
- 小车的加速度取决于：你推的力 + 摆的离心效应 + 重力的水平分量
- 摆的角加速度取决于：你推的力的力矩效应 + 离心力 + 重力

**注意分母中的 $\sin^2\theta$**：当θ=0或π（摆垂直）时，分母最小，系统最"敏感"。

### 3.2.6 Drake代码实践

```python
# 在Drake中实验Cart-Pole动力学
from pydrake.all import *

# 创建Cart-Pole系统
cart_pole = CartPolePlant()
context = cart_pole.CreateDefaultContext()

# 设置初始状态 [x, θ, ẋ, θ̇]
# 从接近倒立的位置开始
cart_pole.get_input_port().FixValue(context, [0.0])
context.SetContinuousState([0.0, np.pi - 0.1, 0.0, 0.0])

# 仿真 - 观察摆倒下
simulator = Simulator(cart_pole, context)
simulator.AdvanceTo(5.0)

# 实验：尝试不同的初始角度，观察系统行为
# θ = π（完美倒立）→ 不稳定平衡，任何微小扰动都会倒
# θ = π - 0.01 → 非常缓慢地倒下
# θ = π - 0.5 → 快速倒下
```

---

## 3.3 四旋翼（Quadrotors）

### 3.3.1 背景故事

> "四旋翼在过去几年变得极其流行——来自航模社区的外转子电机使它们强大、轻便且便宜！"

**Tedrake教授的预测（和错误）**：

> "当四旋翼革命开始时，我预测固定翼飞行器会很快在大多数应用中胜出。螺旋桨在产生推力方面几乎是最优效率的——使四旋翼在悬停时非常高效——但要在前飞中高效，你可能需要翼型。翅膀是个好主意！但我错了——四旋翼完全主导了商用无人机。"

**为什么四旋翼赢了？**

> "也许只是因为它们更容易控制？我怀疑随着领域成熟，实现核心功能不再是主要障碍，人们最终会重新关注效率。"

**类比**：就像SUV vs 轿车。SUV更实用、更容易上手，虽然油耗更高。四旋翼就像SUV——控制简单、能悬停、机动性好，虽然效率不如固定翼。

### 3.3.2 平面四旋翼（2D）

**简化模型**：把四旋翼限制在平面内，只需要两个螺旋桨。

**运动方程**（极其简单，因为只有一个刚体）：

$$m\ddot{x} = -(u_1+u_2)\sin\theta$$

$$m\ddot{y} = (u_1+u_2)\cos\theta - mg$$

$$I\ddot{\theta} = r(u_1-u_2)$$

**通俗理解**：
- **x方向**：两个螺旋桨的总推力在水平方向的分量
- **y方向**：总推力在竖直方向的分量 - 重力
- **旋转**：两个螺旋桨推力差 × 力臂 = 旋转力矩

**类比**：想象你双手各拿一个吹风机，站在滑板上：
- 两个吹风机都朝下吹 → 你上升
- 左手吹风机更强 → 你向右倾斜并旋转
- 倾斜后，推力有水平分量 → 你水平移动

**关键洞察**：四旋翼是欠驱动的！
- 3个自由度（x, y, θ）
- 2个控制输入（u₁, u₂）
- 你不能独立控制x、y和θ

### 3.3.3 完整3D四旋翼

> "3D四旋翼的动力学类似。唯一的复杂性来自处理3D旋转。"

**关键细节**：

1. **螺旋桨反扭矩**：
> "最有趣的特性是我们包含了旋转螺旋桨产生的力矩。有趣的是，如果没有这些力矩，系统在悬停配置附近线性化后实际上是**不可控的**。"

**类比**：就像直升机尾桨——主旋翼旋转会产生反扭矩，需要尾桨来抵消。四旋翼通过让相邻螺旋桨反向旋转来抵消反扭矩，但这个反扭矩效应本身对可控性是必要的。

2. **四元数问题**：
> "默认情况下，MultibodyPlant中每个浮动体的姿态用单位四元数表示。如果你试图用四元数表示来线性化模型，而不考虑单位范数约束，线性化后的模型也是不可控的。"

**通俗解释**：四元数用4个数表示3D旋转，但有一个约束（长度必须为1）。如果你忽略这个约束直接线性化，数学上会多出一个"虚假自由度"，导致系统看起来不可控。

3. **解决方案**：
> "为了避免这个问题，我手动添加了一个'roll-pitch-yaw'浮动基座。这使线性化简单，但引入了'万向锁'奇异性。"

**类比**：就像用经度、纬度、海拔表示地球上的位置——在极点处经度失去意义（万向锁）。四元数没有这个问题，但数学处理更复杂。

### 3.3.4 Drake代码实践

```python
# 平面四旋翼
from pydrake.examples import QuadrotorPlant

# 创建平面四旋翼
quad2d = QuadrotorPlant()  # 2D版本
context = quad2d.CreateDefaultContext()

# 设置初始状态 [x, y, θ, ẋ, ẏ, θ̇]
context.SetContinuousState([0, 0, 0, 0, 0, 0])

# 设置输入 [u1, u2]（两个螺旋桨推力）
quad2d.get_input_port().FixValue(context, [mg/2, mg/2])  # 悬停

# 3D四旋翼
quad3d = QuadrotorPlant()  # 3D版本
# 注意：3D版本有4个输入（4个螺旋桨）
# 状态包括位置和姿态（四元数或RPY）

# 使用MultibodyPlant添加碰撞、悬挂载荷等
# 这比手写方程方便得多
```

**实验建议**：
- 让两个螺旋桨推力不等，观察旋转
- 先倾斜再增加推力，观察水平移动
- 体会欠驱动：你不能直接命令"向右移动"，必须先倾斜

---

## 3.4 平衡控制（Balancing）

### 3.4.1 总体策略

> "对于Acrobot和Cart-Pole系统，我们首先设计一个线性控制器，当系统从**不稳定平衡点附近**开始时能平衡系统。"

**三步走**：
1. **线性化**：在平衡点附近把非线性方程近似为线性方程
2. **检查可控性**：确认线性系统是否能被控制
3. **设计LQR控制器**：用最优控制理论设计反馈控制器

**类比**：就像学骑自行车：
1. 先在平坦路面上（线性化=小角度近似）
2. 确认你确实能控制方向（可控性）
3. 找到最佳的平衡策略（LQR）

### 3.4.2 线性化机械臂方程

**什么是线性化？**

**类比**：地球表面是弯曲的（非线性），但在一个小区域内，你可以把它当作平面（线性）。线性化就是"在平衡点附近把弯曲的动力学当作直线来处理"。

**数学方法：泰勒展开**

$$\dot{x} = f(x,u) \approx f(x^*,u^*) + \frac{\partial f}{\partial x}\bigg|_{x^*,u^*}(x-x^*) + \frac{\partial f}{\partial u}\bigg|_{x^*,u^*}(u-u^*)$$

**通俗理解**：
- $f(x^*,u^*)$：平衡点处的值（=0，因为平衡点不动）
- $\frac{\partial f}{\partial x}$：状态变化对动力学的影响（"灵敏度"）
- $\frac{\partial f}{\partial u}$：输入变化对动力学的影响（"控制效力"）

**对于机械臂方程的特殊简化**：

在平衡点处：
- $\dot{q}^* = 0$（速度为零）
- 所有包含$\dot{q}$的项消失（科里奥利力、离心力为零）
- 如果B是常数，$\frac{\partial B}{\partial q}$项也消失

**最终得到极其简洁的形式**：

$$\dot{\bar{x}} = A_{lin}\bar{x} + B_{lin}\bar{u}$$

其中：

$$A_{lin} = \begin{bmatrix} 0 & I \\ M^{-1}\frac{\partial\tau_g}{\partial q} & 0 \end{bmatrix}, \quad B_{lin} = \begin{bmatrix} 0 \\ M^{-1}B \end{bmatrix}$$

**通俗理解**：
- 上半部分：位置的变化率 = 速度（定义）
- 下半部分：速度的变化率 = 重力梯度/惯量 × 位置偏差 + 控制输入/惯量

#### Acrobot的线性化

在不稳定直立点线性化：

$$\frac{\partial\tau_g}{\partial q}\bigg|_{x^*} = \begin{bmatrix} g(m_1l_{c1}+m_2l_1+m_2l_{c2}) & m_2gl_{c2} \\ m_2gl_{c2} & m_2gl_{c2} \end{bmatrix}$$

**注意**：所有元素都是正的！这意味着在倒立位置，任何微小偏离都会被重力放大（不稳定）。

#### Cart-Pole的线性化

$$\frac{\partial\tau_g}{\partial q}\bigg|_{x^*} = \begin{bmatrix} 0 & 0 \\ 0 & m_pgl \end{bmatrix}$$

**注意**：只有(2,2)元素非零。这意味着只有摆的角度偏离会产生重力恢复力矩（但方向是让它继续倒，不是恢复）。

### 3.4.3 线性系统的可控性

#### 定义

> "如果可能构造一个无约束的输入信号u(t)，将系统从**任何初始状态**移动到**任何最终状态**，在有限时间间隔内，则系统是可控的。"

**类比**：
- **可控**：你有一辆有方向盘和油门的车，可以到达停车场任何位置。
- **不可控**：你有一辆只能前进后退、没有方向盘的车，只能沿一条直线移动。

#### 特征值分析（无重根情况）

**步骤**：

1. 对系统矩阵A做特征值分解：$Av_i = \lambda_i v_i$
2. 转换到模态坐标：$x = Vr$，其中V是特征向量矩阵
3. 在模态坐标中，动力学变成：$\dot{r}_i = \lambda_i r_i + \sum_j \beta_{ij}u_j$

**关键结论**：

> "输入u能影响模态坐标$r_i$的动力学，当且仅当$\beta_{ij} \neq 0$。"

**通俗理解**：

**类比**：想象一个音响系统有多个扬声器（模态），你有几个旋钮（输入）。如果某个旋钮和某个扬声器之间没有连接（$\beta_{ij}=0$），你就无法通过那个旋钮控制那个扬声器。

**可控性条件**：对每个模态i，至少存在一个输入j使得$\beta_{ij} \neq 0$。

#### 可控性 vs 欠驱动

> "Acrobot和Cart-Pole系统的可控性分析揭示了一个极其重要的观点：**欠驱动系统不一定是不可控系统。**"

**这是本章最重要的洞察之一！**

**类比**：
- 你只有油门没有方向盘（欠驱动）
- 但如果你可以利用墙壁反弹、利用坡度、利用惯性，你仍然可以到达任何位置（可控）
- 只是路径可能非常复杂

> "欠驱动系统不能跟踪任意轨迹，但这不意味着它们不能到达状态空间中的任意点。然而，将系统置于特定状态所需的轨迹可能任意复杂。"

**生活类比**：
- 你只能控制肘关节（Acrobot），但通过巧妙的摆动，你可以让肩关节到达任何角度
- 你只能水平推小车（Cart-Pole），但通过巧妙的推拉，你可以让摆到达任何角度
- 只是你不能"直接命令"它去那里，必须走一条"弯路"

#### 可稳定性（Stabilizability）

> "可稳定性是比可控性严格更弱的条件。"

**区别**：
- **可控**：能在**有限时间**内到达原点
- **可稳定**：允许**渐近收敛**（可以花无限长时间）

**类比**：
- 可控 = 你能在10秒内把球推到任何位置
- 可稳定 = 你可以慢慢把球滚到原点，即使某些方向你推不动，但那些方向球会自己滚回来

> "本质上，如果不可控的子空间是自然稳定的，系统仍然可以是可稳定的。"

#### Brockett定理（非线性系统的微妙之处）

> "对于非线性系统，可稳定性和可控性的关系更加微妙。Roger Brockett的一个著名结果表明，非线性可控性不一定意味着可通过可微控制策略实现可稳定性。"

**通俗理解**：在线性世界里，"能控制"≈"能稳定"。但在非线性世界里，即使你能到达任何点，也可能找不到一个"平滑的"控制律来稳定它。这是非线性控制的一个深层困难。

### 3.4.4 LQR反馈控制

#### 什么是LQR？

**LQR = Linear Quadratic Regulator（线性二次调节器）**

**类比**：你开车回家，想找到一条"最优"路径。"最优"的定义是：
- 偏离路线越少越好（状态误差小）
- 方向盘打得越少越好（控制 effort小）
- 这两个目标之间有个权衡

LQR就是数学上精确求解这个"最优权衡"的工具。

#### 数学公式

最小化代价函数：

$$J(x_0) = \int_0^\infty [x^T(t)Qx(t) + u^T(t)Ru(t)]dt$$

其中：
- **Q矩阵**：惩罚状态偏差（"偏离平衡点有多严重"）
- **R矩阵**：惩罚控制输入（"用多大力有多贵"）

**最优控制律**：

$$u(t) = -Kx(t)$$

其中K是通过求解Riccati方程得到的最优增益矩阵。

#### Drake代码实践

```python
from pydrake.all import *
import numpy as np

# 方法1：直接对线性系统使用LQR
# 先获取线性化后的A, B矩阵
A = ...  # 从线性化得到
B = ...  # 从线性化得到

# 定义Q和R矩阵
Q = np.diag([10, 10, 1, 1])  # 状态权重：角度偏差比速度偏差更重要
R = np.diag([1])              # 输入权重：控制力不要太猛

# 计算LQR增益
K = LinearQuadraticRegulator(A, B, Q, R)

# 方法2：直接对非线性系统使用（Drake自动线性化）
controller = LinearQuadraticRegulator(system, context, Q, R)

# 实验：调整Q和R
# Q大、R小 → 快速回到平衡，但控制力大（"激进"）
# Q小、R大 → 慢慢回到平衡，控制力小（"温和"）
```

#### 实验观察

> "闭环响应的仿真表明任务确实完成了——而且以令人印象深刻的方式。通常，系统状态必须**剧烈地远离原点**才能最终到达原点。"

**类比**：就像荡秋千——你想让秋千停下来（到达原点），但你必须先用力推它让它荡得更高（远离原点），然后在正确的时机施加制动力。

> "进一步检查发现，（线性化的）闭环动力学实际上是**非最小相位**的（Acrobot有3个右半平面零点，Cart-Pole有1个）。"

**通俗理解**：非最小相位 = "反直觉的初始响应"。就像你推购物车，车先向后退再向前进。对于倒立摆，你想让它向右，它可能先向左倾斜再向右。

#### 四旋翼的LQR

> "LQR对四旋翼基本上开箱即用，只要在标称平衡点（螺旋桨非零推力平衡重力）附近线性化。"

**注意**：
> "LQR虽然对线性化系统是最优的，但不一定是最大化平衡点吸引域的最佳线性控制方案。鲁棒控制理论（显式考虑线性化模型和非线性模型之间的差异）会产生在这方面优于LQR的控制器。"

**类比**：LQR就像在平坦路面上调好的自行车平衡策略。但真实路面有坑洼（非线性），鲁棒控制就像在考虑了各种路面情况后调出的更"抗造"的策略。

---

## 3.5 部分反馈线性化（Partial Feedback Linearization, PFL）

### 3.5.1 核心思想

> "欠驱动系统不能通过反馈等价于 $\ddot{q} = u$。虽然我们不能总是简化系统的全部动力学，但仍然可以线性化系统动力学的**一部分**。"

**类比**：

想象你在开一辆手动挡车：
- **完全反馈线性化**（全驱动）：你踩油门，车就精确地以你要求的加速度加速。
- **部分反馈线性化**（欠驱动）：你不能直接控制发动机的每个气缸，但你可以：
  - **同位PFL**：让油门精确控制车轮转速（控制有执行器的部分）
  - **非同位PFL**：通过巧妙控制油门，间接控制变速箱的换挡时机（控制没有执行器的部分）

### 3.5.2 Cart-Pole的同位PFL

**目标**：线性化小车（有执行器的部分）的动力学。

从运动方程出发：
$$\ddot{x}(2-\cos^2\theta) - \sin\theta\cos\theta\ddot{\theta} - \dot{\theta}^2\sin\theta = f_x$$

设计控制律：
$$f_x = (2-\cos^2\theta)\ddot{x}_d - \sin\theta\cos\theta\ddot{\theta} - \dot{\theta}^2\sin\theta$$

结果：
$$\ddot{x} = \ddot{x}_d$$（小车精确跟踪期望加速度！）

**但更有趣的是摆的方程变成了**：
$$\ddot{\theta} = -\ddot{x}_d\cos\theta - \sin\theta$$

**通俗理解**：摆的方程变成了**简单摆**的方程！只不过"力矩输入"变成了$-\ddot{x}_d\cos\theta$而不是直接的力矩。

**关键限制**：$\cos\theta$项！当摆水平时（θ=π/2），$\cos\theta=0$，你的控制权威消失。

**类比**：就像你用手掌平衡棍子——当棍子完全水平时，无论你怎么移动手掌，都无法产生让棍子转动的力矩。你必须先让棍子稍微倾斜，才能重新获得控制。

### 3.5.3 Cart-Pole的非同位PFL

**目标**：线性化摆（没有执行器的部分）的动力学。

设计控制律：
$$f_x = \frac{(c - \frac{2}{c})\ddot{\theta}_d - 2\tan\theta - \dot{\theta}^2 s}{1}$$

结果：
$$\ddot{\theta} = \ddot{\theta}_d$$（摆精确跟踪期望角加速度！）

**但代价是**：
$$\ddot{x} = -\frac{1}{\cos\theta}\ddot{\theta}_d - \tan\theta$$

**关键限制**：当$\cos\theta = 0$（摆水平）时，控制器会"爆炸"——要求无穷大的力！

> "这个表达式只在$\cos\theta \neq 0$时有效。一旦$\cos\theta = 0$，控制器会'爆炸'——在$\cos\theta = 0$时请求无穷大的力；所以在硬件上实现之前一定要饱和命令。"

**但有个好消息**：$|c - 2/c| \geq 1$永远成立，所以分母不会为零。

### 3.5.4 一般形式

对于一般的欠驱动系统：

$$M_{11}\ddot{q}_1 + M_{12}\ddot{q}_2 = \tau_1$$（无执行器关节）
$$M_{21}\ddot{q}_1 + M_{22}\ddot{q}_2 = \tau_2 + u$$（有执行器关节）

**同位线性化**：

$$(M_{22} - M_{21}M_{11}^{-1}M_{12})\ddot{q}_2 - \tau_2 + M_{21}M_{11}^{-1}\tau_1 = u$$

**全局有效**（因为$M_{22} - M_{21}M_{11}^{-1}M_{12}$总是可逆的）。

**非共位线性化**：

需要$M_{12}$的秩条件——称为**"强惯性耦合"（Strong Inertial Coupling）**。

**通俗理解**：强惯性耦合 = "有电机的关节和无电机的关节之间必须有足够强的动力学联系"。如果两个关节完全解耦（$M_{12}=0$），你就无法通过控制一个来影响另一个。

### 3.5.5 任务空间PFL

**定理3.1**：定义任务空间输出$y = h(q)$，如果：

$$\ddot{q}_2 = \bar{H}^+[\ddot{y}_d - \dot{H}\dot{q} - H_1M_{11}^{-1}\tau_1]$$

其中$\bar{H} = H_2 - H_1M_{11}^{-1}M_{12}$，则$\ddot{y} = \ddot{y}_d$。

**通俗理解**：你不需要控制每个关节的角度，你只需要控制"末端执行器的轨迹"。PFL帮你算出需要给每个关节什么加速度。

#### 例3.7：Cart-Pole末端轨迹跟踪

**任务**：让摆的末端在垂直方向跟踪一个正弦轨迹。

$$y = h(q) = -l\cos\theta$$（末端垂直位置）

期望轨迹：
$$y_d(t) = \frac{l}{2} + \frac{l}{4}\sin(t)$$

**通俗理解**：就像你用手掌让棍子的顶端画一个上下波动的轨迹。你只能水平移动手掌，但通过PFL，你可以计算出需要怎么移动才能让顶端跟踪目标。

### 3.5.6 Drake代码实践

```python
# PFL实现示例（Cart-Pole）
import numpy as np

def collocated_pfl(state, xdd_desired):
    """同位PFL：让小车跟踪期望加速度"""
    x, theta, xdot, thetadot = state
    
    # 计算所需的力
    # f_x = (2 - cos²θ)ẍ_d - sinθcosθθ̈ - θ̇²sinθ
    # 但θ̈需要从动力学中获取...
    
    c = np.cos(theta)
    s = np.sin(theta)
    
    # 简化版本（所有参数=1）
    fx = (2 - c**2) * xdd_desired - s*c*0 - thetadot**2 * s
    # 注意：这里θ̈=0是简化假设，实际需要完整计算
    
    return fx

def noncollocated_pfl(state, thetadd_desired):
    """非共位PFL：让摆跟踪期望角加速度"""
    x, theta, xdot, thetadot = state
    
    c = np.cos(theta)
    s = np.sin(theta)
    
    # 检查奇异性
    if abs(c) < 0.01:
        print("警告：接近奇异点！")
        return 0  # 饱和处理
    
    fx = (c - 2/c) * thetadd_desired - 2*np.tan(theta) - thetadot**2 * s
    return fx

# 实验：比较两种PFL的效果
# 1. 同位PFL：小车精确跟踪，摆自然运动
# 2. 非共位PFL：摆精确跟踪，小车被动运动
# 3. 观察非共位PFL在θ≈π/2时的"爆炸"行为
```

---

## 3.6 摆起控制（Swing-Up Control）

### 3.6.1 能量整形（Energy Shaping）

**核心思想**：不直接控制位置，而是控制系统的**总能量**。

**类比**：

想象你在荡秋千：
- 你不会想"我要让秋千在3秒内到达最高点"
- 你会想"我要在正确的时机推一下，让秋千越荡越高"
- 你控制的是**能量输入**，而不是位置

**关键洞察**：
> "只需要一个执行器就能改变系统的总能量。"

这就是为什么Acrobot（只有肘关节电机）和Cart-Pole（只有小车推力）都能完成摆起任务。

### 3.6.2 Cart-Pole的摆起控制

**策略**：
1. 用同位PFL简化动力学
2. 用能量整形把摆调节到**同宿轨道**（homoclinic orbit）
3. 加PD控制器让小车留在原点附近

**为什么用同位PFL而不是非共位？**

> "这有点令人惊讶...如果我们想控制摆，不应该用非共位版本吗？实际上，我们最终想控制小车和摆两者，而且同位版本避免了反转可能变为零的$\cos\theta$项。"

**能量计算**：

摆的能量（单位质量、单位长度、单位重力）：
$$E(x) = \frac{1}{2}\dot{\theta}^2 - \cos\theta$$

期望能量（在倒立平衡点）：
$$E_d = 1$$

能量误差：
$$\tilde{E}(x) = E(x) - E_d$$

**能量变化率**：
$$\dot{\tilde{E}} = -u\dot{\theta}\cos\theta$$

**控制律设计**：
$$u = k\dot{\theta}\cos\theta\tilde{E}, \quad k > 0$$

**结果**：
$$\dot{\tilde{E}} = -k\dot{\theta}^2\cos^2\theta\tilde{E}$$

**通俗理解**：
- 如果能量太低（$\tilde{E}<0$），且摆正在向上运动（$\dot{\theta}>0$），则施加正力（加速）
- 如果能量太高（$\tilde{E}>0$），且摆正在向上运动，则施加负力（减速）
- $\cos\theta$项确保在摆水平时不施加力（因为那时力对能量没影响）

**收敛条件**（LaSalle定理）：

只要$\int_0^t \dot{\theta}^2\cos^2\theta \, dt' \to \infty$，能量误差就会趋于零。

**通俗理解**：只要摆不是一直停在水平位置（$\cos\theta=0$）或垂直位置（$\dot{\theta}=0$），能量就会收敛。

**完整控制器**（加上小车控制）：

$$\ddot{x}_d = k\tilde{E}\dot{\theta}\cos\theta - k_p x - k_d\dot{x}$$

**类比**：就像你一边荡秋千（能量控制），一边确保自己不要荡出太远（PD控制小车位置）。

### 3.6.3 Acrobot的摆起控制

> "Acrobot的摆起控制可以用非常类似的方式完成。"

使用同位PFL，然后能量整形。

**参考文献方法**：
- [14] Spong 1994：泵入能量
- [20] Spong 1995：用arctan代替sat（更平滑）
- [19] Spong 1996：最清晰的表述

### 3.6.4 讨论

> "这里展示的摆起能量整形控制器是非线性欠驱动控制领域的一个相当忠实的代表。通常这些控制推导需要一些**巧妙的技巧**来简化或消除非线性方程中的项，然后需要一些**巧妙的Lyapunov函数**来证明稳定性。"

**但是**：

> "这些控制器是重要的、有代表性的、相关的。但**非线性方程的巧妙技巧似乎是根本有限的**。本书其余大部分材料将强调更通用的**计算方法**来表述和求解这些及其他控制问题。"

**这是Tedrake教授的核心哲学**：
- 经典非线性控制 = 巧妙的数学技巧（每个问题需要不同的"灵感"）
- 现代计算控制 = 通用的优化方法（一个框架解决所有问题）

**类比**：
- 经典方法像手工裁缝——每件衣服都需要独特的设计和技巧
- 计算方法像3D打印——输入参数，机器自动产出

---

## 3.7 其他模型系统

除了Acrobot和Cart-Pole，欠驱动控制研究中常用的模型系统还有：

| 系统 | 描述 | 类比 |
|------|------|------|
| **Pendubot** | 肩关节有电机，肘关节没有 | Acrobot的"兄弟" |
| **惯性轮摆** | 摆的末端有一个旋转飞轮 | 像陀螺仪稳定器 |
| **Furuta摆** | 水平旋转+垂直摆 | 像旋转的钟摆 |
| **气垫船** | 平面运动，推力有限 | 像冰面上的物体 |

---

## 3.8 习题详解

### 习题3.1：Cart-Pole线性化和平衡

**任务**：
a. 推导Cart-Pole的状态空间动力学
b. 在不稳定平衡点线性化
c. 分析不同状态和控制值下的线性化误差
d. 找出哪些状态能被LQR控制器稳定

**实践指导**：

```python
# 在Drake notebook中完成
# 步骤a：推导状态空间
# x = [x, θ, ẋ, θ̇]
# ẋ = [ẋ, θ̇, ẍ, θ̈]
# 其中ẍ和θ̈从运动方程解出

# 步骤b：线性化
# 在 x* = [0, π, 0, 0] 处
# 使用Drake的Linearize功能或手动Taylor展开

# 步骤c：线性化误差
# 比较非线性仿真和线性仿真的轨迹
# 对于小偏差（θ = π ± 0.01），误差很小
# 对于大偏差（θ = π ± 0.5），误差很大

# 步骤d：LQR稳定域
# 从不同初始条件出发，看LQR能否稳定
# 通常：|θ - π| < 0.3 左右可以稳定
```

### 习题3.2：写URDF和LQR平衡

**任务**：
a. 构建单摆Cart-Pole的URDF
b. 扩展为双摆Cart-Pole，测试LQR

**URDF示例**：

```xml
<robot name="cart_pole">
  <!-- 小车 -->
  <link name="cart">
    <inertial>
      <mass value="1.0"/>
      <inertia ixx="0" iyy="0" izz="0" ixy="0" ixz="0" iyz="0"/>
    </inertial>
  </link>
  
  <!-- 摆 -->
  <link name="pole">
    <inertial>
      <mass value="0.1"/>
      <origin xyz="0 0 -0.5"/>  <!-- 质心在中间 -->
      <inertia ixx="0.0083" iyy="0.0083" izz="0" ixy="0" ixz="0" iyz="0"/>
    </inertial>
  </link>
  
  <!-- 关节：小车-摆（旋转关节） -->
  <joint name="pole_joint" type="revolute">
    <parent link="cart"/>
    <child link="pole"/>
    <axis xyz="0 1 0"/>
    <limit lower="-3.14" upper="3.14" effort="0" velocity="0"/>
  </joint>
  
  <!-- 关节：世界-小车（滑动关节） -->
  <joint name="cart_joint" type="prismatic">
    <parent link="world"/>
    <child link="cart"/>
    <axis xyz="1 0 0"/>
  </joint>
</robot>
```

**双摆扩展**：添加第二个摆和第二个旋转关节，测试LQR是否仍能控制（答案：是的，因为线性化后仍然可控）。

### 习题3.3：离散和连续LTI系统的可控性

**核心概念**：

**离散双积分器**：
$$x[n+1] = \begin{bmatrix} 1 & 1 \\ 0 & 1 \end{bmatrix}x[n] + \begin{bmatrix} 0 \\ 1 \end{bmatrix}u[n]$$

**类比**：就像在网格纸上移动一个棋子：
- 每步，位置增加当前速度
- 每步，速度增加控制输入（-1, 0, 或+1）

**关键问题**：从(0,0)出发，最少需要几步到达任何满足条件的状态？

**答案思路**：
- 第1步：只能到达(0,-1), (0,0), (0,1)
- 第2步：可以到达更多点
- 需要分析可达集的增长

### 习题3.4：非线性系统稳定性与线性化的比较

**核心问题**：线性化能告诉我们什么？不能告诉我们什么？

**无阻尼摆（b=0）**：

在θ=0（朝下）：
- 非线性：稳定（但不是渐近稳定，因为无阻尼，会永远振荡）
- 线性化：特征值纯虚数 → 边际稳定
- **结论一致**：都是"稳定但不收敛"

在θ=π（朝上）：
- 非线性：不稳定
- 线性化：一个正特征值 → 不稳定
- **结论一致**：都不稳定

**有阻尼摆（b=1）**：

在θ=0（朝下）：
- 非线性：渐近稳定（阻尼消耗能量，最终停在最低点）
- 线性化：特征值实部为负 → 指数稳定
- **结论一致**：都稳定且收敛

**关键教训**：
> "严格稳定的线性化意味着非线性系统的局部指数稳定。但边际稳定的线性化不能告诉我们非线性系统是渐近稳定、稳定还是不稳定。"

**类比**：线性化就像用放大镜看曲面——如果曲面在放大镜下是"向下弯的"（稳定），那原始曲面也是。但如果放大镜下是"平的"（边际），你看不出原始曲面是微微向上还是微微向下弯。

---

## 3.9 参考文献要点

本章引用了20篇关键文献，核心包括：

| 编号 | 作者/年份 | 贡献 |
|------|----------|------|
| [1] | Murray & Hauser, 1991 | Acrobot的近似线性化 |
| [2] | Spong, 1997 | 欠驱动机械系统综述 |
| [8] | Brockett, 1983 | 非线性可稳定性条件 |
| [10] | Spong, 1994 | 部分反馈线性化 |
| [14] | Spong, 1994 | Acrobot摆起控制 |
| [18] | Chung & Hauser, 1995 | 摆动摆的非线性控制 |
| [19] | Spong, 1996 | 基于能量的欠驱动控制 |

---

## 对照检查与补充

### 遗漏检查

经过逐一对照PDF，以下是需要补充的内容：

#### 补充1：Acrobot的Drake代码细节

PDF中提到：
> "You can experiment with the Acrobot dynamics in DRAKE using, e.g."

**补充实践**：

```python
# 完整的Acrobot实验
from pydrake.all import *
import numpy as np
import matplotlib.pyplot as plt

# 1. 创建系统
plant = AcrobotPlant()
context = plant.CreateDefaultContext()

# 2. 设置初始条件（从悬挂位置开始）
# 状态：[θ₁, θ₂, θ̇₁, θ̇₂]
initial_state = [0.1, 0.2, 0.0, 0.0]  # 稍微偏离垂直
context.SetContinuousState(initial_state)

# 3. 无输入仿真（自由摆动）
plant.get_input_port().FixValue(context, [0.0])
simulator = Simulator(plant, context)
simulator.AdvanceTo(10.0)

# 4. 有输入仿真（施加肘关节力矩）
context.SetTime(0)
context.SetContinuousState(initial_state)
plant.get_input_port().FixValue(context, [1.0])  # 1 Nm肘关节力矩
simulator = Simulator(plant, context)
simulator.AdvanceTo(10.0)

# 5. 观察耦合效应
# 注意：即使只有肘关节力矩，肩关节也会运动！
# 这就是"状态依赖耦合"
```

#### 补充2：Cart-Pole的Drake代码细节

```python
# 完整的Cart-Pole实验
from pydrake.all import *

# 1. 创建系统
plant = CartPolePlant()
context = plant.CreateDefaultContext()

# 2. 从接近倒立位置开始
# 状态：[x, θ, ẋ, θ̇]
near_upright = [0.0, np.pi - 0.05, 0.0, 0.0]
context.SetContinuousState(near_upright)

# 3. 无控制 - 观察倒下
plant.get_input_port().FixValue(context, [0.0])
simulator = Simulator(plant, context)
simulator.AdvanceTo(5.0)
# 结果：摆缓慢倒下（因为初始偏离很小）

# 4. LQR平衡
# 获取线性化
linearizer = Linearize(plant, context)
A = linearizer.A()
B = linearizer.B()

# 设计LQR
Q = np.diag([1, 10, 1, 1])  # θ的权重最大
R = np.diag([1])
K = LinearQuadraticRegulator(A, B, Q, R)

# 闭环仿真
# u = -K(x - x*)
```

#### 补充3：四旋翼的螺旋桨反扭矩

PDF中特别强调：
> "Interestingly, without these moments, the system linearized about the hovering configuration is actually not controllable."

**补充解释**：

```python
# 为什么螺旋桨反扭矩对可控性必要？
# 
# 没有反扭矩时：
# - 4个螺旋桨产生4个推力
# - 但只能产生3个力矩（roll, pitch, yaw中的2个）
# - yaw轴没有控制力矩 → 不可控
#
# 有反扭矩时：
# - 每个螺旋桨除了推力，还产生反扭矩
# - 相邻螺旋桨反向旋转，反扭矩可以差动
# - yaw轴有了控制力矩 → 可控
#
# 类比：就像直升机
# - 主旋翼产生升力和反扭矩
# - 尾桨抵消反扭矩并提供yaw控制
# - 没有尾桨 → 直升机无法控制方向
```

#### 补充4：四元数线性化问题

```python
# 四元数线性化的陷阱
# 
# 四元数 q = [w, x, y, z]，约束：w²+x²+y²+z² = 1
# 
# 如果直接线性化（忽略约束）：
# - 状态空间是4维的
# - 但实际只有3个旋转自由度
# - 多出的1维是"虚假"的
# - 导致线性化系统看起来不可控
#
# 解决方案1：使用RPY（roll-pitch-yaw）
# - 只有3个参数，没有约束
# - 但有万向锁奇异性
#
# 解决方案2：使用四元数但考虑约束
# - 在切空间上线性化
# - 数学上更复杂但无奇异性
#
# Drake中的处理：
# "I have manually added a 'roll-pitch-yaw' floating base"
```

#### 补充5：能量整形的LaSalle定理

PDF中提到：
> "This condition, a version of LaSalle's theorem that we will develop in our notes on Lyapunov methods, is satisfied for all but the trivial constant trajectories at fixed points."

**补充通俗解释**：

```
LaSalle定理的直觉：

想象一个球在一个碗里滚动（有摩擦）：
- 碗的形状 = Lyapunov函数（能量）
- 摩擦力 = 能量耗散
- 球最终会停在哪里？

LaSalle定理说：
- 如果能量一直在减少（或不变）
- 球最终会停在"能量不再变化"的集合上
- 对于Cart-Pole：这个集合就是同宿轨道（能量=Ed的轨道）

例外情况：
- 如果球一开始就在碗底（平衡点），它永远不会动
- 如果球在碗沿上完全静止，它也不会动
- 这些是"trivial constant trajectories"
```

#### 补充6：PFL的奇异性处理

```python
# 非共位PFL的奇异性处理
# 
# 问题：当 cos(θ) ≈ 0 时，控制力趋向无穷大
# 
# 实际解决方案：
def safe_noncollocated_pfl(state, thetadd_desired, max_force=100):
    x, theta, xdot, thetadot = state
    c = np.cos(theta)
    s = np.sin(theta)
    
    # 奇异性检查
    if abs(c) < 0.1:  # 接近水平
        # 方案1：饱和
        fx = np.clip(computed_fx, -max_force, max_force)
        # 方案2：切换到同位PFL
        fx = collocated_pfl(state, 0)  # 至少保持小车稳定
        # 方案3：使用混合策略
        alpha = abs(c) / 0.1  # 0到1的混合系数
        fx = alpha * noncollocated_fx + (1-alpha) * collocated_fx
    
    return fx

# 实际硬件上的注意事项：
# 1. 永远不要发送未饱和的命令到电机
# 2. 在奇异点附近切换控制策略
# 3. 添加速度限制和加速度限制
```

#### 补充7：LQR的Q和R矩阵调参指南

```python
# LQR调参的实用指南
# 
# Q = diag([q_x, q_theta, q_xdot, q_thetadot])
# R = [r_f]
#
# 物理意义：
# q_x：小车位置偏差的惩罚（"偏离中心有多严重"）
# q_theta：摆角度偏差的惩罚（"摆倾斜有多严重"）
# q_xdot：小车速度偏差的惩罚（"小车移动太快有多严重"）
# q_thetadot：摆角速度偏差的惩罚（"摆转太快有多严重"）
# r_f：控制力的惩罚（"用多大力有多贵"）
#
# 调参经验：
# 1. 想让摆快速稳定？增大 q_theta
# 2. 想让小车少动？增大 q_x
# 3. 想省能量？增大 r_f
# 4. 想让动作平滑？增大 q_xdot, q_thetadot
#
# 典型值（Cart-Pole）：
Q_aggressive = np.diag([1, 100, 1, 1])   # 摆优先
R_aggressive = np.diag([0.1])             # 允许大力
K_aggressive = LinearQuadraticRegulator(A, B, Q_aggressive, R_aggressive)

Q_gentle = np.diag([10, 10, 1, 1])       # 平衡
R_gentle = np.diag([10])                  # 限制力
K_gentle = LinearQuadraticRegulator(A, B, Q_gentle, R_gentle)
```

#### 补充8：Swing-Up到Balance的切换

```python
# 完整的Swing-Up + Balance控制器
def swing_up_and_balance(state, params):
    x, theta, xdot, thetadot = state
    
    # 计算与倒立位置的角度差
    angle_error = theta - np.pi
    # 归一化到 [-π, π]
    angle_error = np.arctan2(np.sin(angle_error), np.cos(angle_error))
    
    # 切换条件：接近倒立位置
    if abs(angle_error) < 0.3 and abs(thetadot) < 1.0:
        # 切换到LQR平衡
        u = -K @ (state - upright_state)
    else:
        # 能量整形摆起
        E = 0.5 * thetadot**2 - np.cos(theta)  # 当前能量
        Ed = 1.0  # 目标能量（倒立位置）
        E_tilde = E - Ed
        
        # 能量控制 + 小车PD
        k_energy = 1.0
        kp_cart = 5.0
        kd_cart = 2.0
        
        u = k_energy * E_tilde * thetadot * np.cos(theta) \
            - kp_cart * x - kd_cart * xdot
    
    # 饱和
    u = np.clip(u, -params['max_force'], params['max_force'])
    
    return u

# 关键设计考虑：
# 1. 切换不能太早（否则LQR无法稳定）
# 2. 切换不能太晚（否则摆已经过了倒立点）
# 3. 切换时可能有"跳跃"（不连续），需要平滑过渡
# 4. 实际中通常使用"混合"策略而非硬切换
```

#### 补充9：可控性的PBH测试（一般解法）

PDF中提到了"一般解"但折叠了。补充关键内容：

```python
# 可控性的一般判据：Kalman秩条件
# 
# 系统 ẋ = Ax + Bu 可控
# 当且仅当：
# rank([B, AB, A²B, ..., A^(n-1)B]) = n
#
# 其中n是状态维度

import numpy as np

def check_controllability(A, B):
    n = A.shape[0]
    # 构建可控性矩阵
    C = B.copy()
    AB = B.copy()
    for i in range(1, n):
        AB = A @ AB
        C = np.hstack([C, AB])
    
    rank = np.linalg.matrix_rank(C)
    return rank == n, rank

# 对Acrobot测试
# A_lin = [[0, 0, 1, 0],
#           [0, 0, 0, 1],
#           [...],
#           [...]]
# B_lin = [[0], [0], [...], [...]]

# 对Cart-Pole测试
# 结果：两者在倒立点附近都是可控的！
# 即使它们是欠驱动的！

# PBH测试（等价条件）：
# 对A的每个特征值λ：
# rank([A-λI, B]) = n
# 如果存在某个λ使得rank < n，则不可控
```

#### 补充10：非最小相位的实际影响

```python
# 非最小相位系统的实际影响
# 
# Cart-Pole有1个右半平面零点
# Acrobot有3个右半平面零点
#
# 实际意义：
# 1. 初始反向响应
#    - 你想让摆向右，它先向左
#    - 你想让Acrobot向上，它先向下
#
# 2. 控制带宽限制
#    - 不能太"激进"，否则系统会不稳定
#    - 响应速度有物理上限
#
# 3. 过冲不可避免
#    - 无论怎么调参，都会有过冲
#
# 类比：
# 就像倒车入库：
# - 你想让车尾向右，必须先向左打方向盘
# - 这个"反向"是物理约束，无法消除
# - 但熟练的司机可以最小化这个效应
#
# 在Drake中观察：
# 1. 对Cart-Pole施加阶跃响应
# 2. 观察摆的初始运动方向
# 3. 与期望方向相反 → 非最小相位
```

---

## 最终综合总结

### 本章的核心知识图谱

```
欠驱动系统（控制输入 < 自由度）
│
├── 建模
│   ├── 拉格朗日方法（能量法）
│   ├── 标准机械臂形式：M(q)q̈ + C(q,q̇)q̇ = τ_g(q) + Bu
│   └── 关键：B矩阵揭示哪些关节有执行器
│
├── 平衡（局部）
│   ├── 线性化（Taylor展开）
│   ├── 可控性分析（Kalman秩条件）
│   ├── 可稳定性（比可控性弱）
│   └── LQR设计（最优线性反馈）
│
├── 部分反馈线性化（全局）
│   ├── 同位PFL（控制有执行器的关节）→ 全局有效
│   ├── 非共位PFL（控制无执行器的关节）→ 有奇异性
│   └── 任务空间PFL（控制末端轨迹）
│
├── 摆起（全局）
│   ├── 能量整形（控制总能量）
│   ├── 同宿轨道（能量=目标能量的轨道）
│   └── LaSalle定理（收敛性证明）
│
└── 核心洞察
    ├── 欠驱动 ≠ 不可控
    ├── 耦合是核心（有电机↔无电机）
    ├── 巧妙技巧有局限 → 计算方法更通用
    └── 能量是统一的视角
```

### 给初学者的学习建议

1. **先玩Drake仿真**：不要急着推导公式，先在Drake中运行Acrobot和Cart-Pole，观察行为
2. **理解物理直觉**：每个数学项都有物理意义（惯量、科里奥利力、重力）
3. **从简单到复杂**：先理解Cart-Pole（更直观），再理解Acrobot（更抽象）
4. **动手调参**：修改LQR的Q和R矩阵，观察行为变化
5. **思考"为什么"**：为什么欠驱动系统可以可控？为什么能量整形有效？为什么非共位PFL有奇异性？

### 这一章在整个课程中的位置

> "这些模型系统捕捉了问题的本质，而没有引入所有真实世界例子中的复杂性。"

**后续章节将**：
- 用**轨迹优化**替代巧妙的能量整形
- 用**Lyapunov方法**替代特定的稳定性证明
- 用**强化学习**替代手动设计的控制律
- 从2D模型扩展到**3D行走机器人**

**但本章的基础概念（欠驱动、耦合、PFL、能量整形、LQR）将贯穿整个课程。**