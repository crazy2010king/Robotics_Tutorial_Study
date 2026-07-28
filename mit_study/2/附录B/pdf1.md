# 用大白话讲透《Underactuated Robotics》附录B：多体动力学（Multi-Body Dynamics）

> 前面21章我们一直在用"现成的机器人方程"做算法——倒立摆、Acrobot、Cart-Pole、四足机器人……但**这些方程从哪儿来？** 这一章就是回答这个问题的：**怎么从"一堆连杆+关节+电机"推导出机器人运动的数学方程**。
>
> 作者 Russ Tedrake 说：这一章是整门课的"机械基础" 。掌握了它，你就能给**任何**机器人——从机械臂到人形机器人、从四足到飞行器——写出动力学方程，然后用 Drake 仿真、用前面学的控制算法去驾驭它。

下面我用最通俗的方式，把这一章从头到尾拆给你看，配上生活类比，并对所有可实验的地方做重点补充。

---

## 🌊 一、B.1 推导运动方程：拉格朗日法（Lagrangian Mechanics）

### 1.1 核心公式——拉格朗日方程

**这是整个多体动力学的"母公式"** ：

$$\frac{d}{dt}\frac{\partial L}{\partial\dot{q}_{i}}-\frac{\partial L}{\partial q_{i}}=\tau_{i}$$

其中：
- $L = T - U$（拉格朗日量 = 动能 - 势能）
- $q_i$ 是广义坐标（关节角度等）
- $\tau_i$ 是对应 $q_i$ 的广义力

### 1.2 生活类比：滑雪者找最速降线

想象一个滑雪者从山顶滑到山脚。**自然界总是选择"作用量"（action）取极值的路径**——这就像滑雪者本能地走最省力、最陡的路线。

拉格朗日方程就是这个"最省力原理"的数学表达：
- **$T$（动能）** 代表滑雪者的"运动能量"
- **$U$（势能）** 代表滑雪者在山坡上的"高度能量"
- **$L = T - U$** 代表"净能量"
- 滑雪者的真实轨迹，就是让 $\int L \, dt$（作用量）取极值的那条路

**与牛顿定律的关系**：
对于质点，$T=\frac{1}{2}m\dot{x}^{2}$，代入拉格朗日方程就得到 $f = ma$ ——**这就是牛顿第二定律**！

> 💡 **拉格朗日法的威力**：牛顿法在非笛卡尔坐标系（如关节角度）和带约束的运动中会变得极其繁琐，而拉格朗日法**天生就能处理广义坐标和约束**。

### 1.3 实战推导：双摆的完整方程（**本章最核心的例子**）

教材手把手推导了双摆 ——这是理解所有机器人动力学原语的"Hello World"。

#### 步骤1：定义运动学

两个质点 $p_1, p_2$，关节角度 $q=[\theta_1, \theta_2]^T$：

$$\begin{align}
p_1 &= l_1\begin{bmatrix}\sin\theta_1\\-\cos\theta_1\end{bmatrix}\\
p_2 &= p_1 + l_2\begin{bmatrix}\sin(\theta_1+\theta_2)\\-\cos(\theta_1+\theta_2)\end{bmatrix}
\end{align}$$

**生活类比**：想象你的手臂——大臂角度 $\theta_1$，小臂相对大臂的角度 $\theta_2$。手腕的位置 $p_2$ 就是这两个角度的叠加。

#### 步骤2：计算速度和能量

$$\begin{align}
T &= \frac{1}{2}(m_1+m_2)l_1^2\dot{\theta}_1^2 + \frac{1}{2}m_2l_2^2(\dot{\theta}_1+\dot{\theta}_2)^2 + m_2l_1l_2\dot{\theta}_1(\dot{\theta}_1+\dot{\theta}_2)\cos\theta_2\\
U &= -(m_1+m_2)gl_1\cos\theta_1 - m_2gl_2\cos(\theta_1+\theta_2)
\end{align}$$

#### 步骤3：代入拉格朗日方程

经过一长串求导（教材完整展示了每一步 ），得到：

$$\begin{align}
(m_1+m_2)l_1^2\ddot{\theta}_1 &+ m_2l_2^2(\ddot{\theta}_1+\ddot{\theta}_2) + m_2l_1l_2(2\ddot{\theta}_1+\ddot{\theta}_2)\cos\theta_2 \\
&- m_2l_1l_2(2\dot{\theta}_1+\dot{\theta}_2)\dot{\theta}_2\sin\theta_2 + (m_1+m_2)l_1g\sin\theta_1 + m_2gl_2\sin(\theta_1+\theta_2) = \tau_1\\
m_2l_2^2(\ddot{\theta}_1+\ddot{\theta}_2) &+ m_2l_1l_2\ddot{\theta}_1\cos\theta_2 + m_2l_1l_2\dot{\theta}_1^2\sin\theta_2 + m_2gl_2\sin(\theta_1+\theta_2) = \tau_2
\end{align}$$

**观察这个公式**：
- 每一项都有清晰的物理意义
- 包含 $\ddot{\theta}$（加速度）、$\dot{\theta}^2$（离心力）、$\dot{\theta}_1\dot{\theta}_2$（科氏力）、$\sin\theta$（重力）
- 这就是机器人动力学的"全貌"

> 💡 教材坦言：如果对这些推导不舒服，**任何一本好的刚体力学教材都能帮你补上** 。[1] 是机器人运动学/动力学的优秀实践指南，[2]（Lanczos 的《力学的变分原理》）是作者**最爱的力学书** 。

---

## 🦾 二、B.2 操作臂方程（The Manipulator Equations）——机器人动力学的"标准形式"

### 2.1 发现规律

如果你对几个简单的机器人操作臂"crank through"拉格朗日动力学，会发现**所有结果都有相同的特征形式** 。

**关键观察**：机器人的动能**总是**可以写成 ：

$$T = \frac{1}{2}\dot{q}^T M(q) \dot{q}$$

其中 $M(q)$ 是**依赖于构型的惯性矩阵（质量矩阵）**。

### 2.2 操作臂方程的标准形式

**这是全书最重要的方程之一** ：

$$M(q)\ddot{q} + C(q,\dot{q})\dot{q} = \tau_g(q) + B u$$

各项含义：
- **$M(q)$**：惯性矩阵（正定、对称）
- **$C(q,\dot{q})\dot{q}$**：科氏力和离心力（$C$ 的选择不唯一）
- **$\tau_g(q)$**：重力向量
- **$B u$**：执行器输入的广义力

**生活类比**：
- $M\ddot{q}$ 就像"推动家具的惯性"——质量越大越难加速
- $C\dot{q}$ 就像"旋转时甩出去的力"——洗衣机甩干时的那种力
- $\tau_g$ 就像"重力把你往下拉"
- $Bu$ 就像"你施加的推力"

**作者金句**：每当看到这个方程，他就看到 "$ma = f$" 。

### 2.3 双摆的操作臂方程形式（Example B.2）

教材把双摆方程浓缩成矩阵形式 ：

$$\begin{align}
M(q) &= \begin{bmatrix}
(m_1+m_2)l_1^2+m_2l_2^2+2m_2l_1l_2\cos\theta_2 & m_2l_2^2+m_2l_1l_2\cos\theta_2\\
m_2l_2^2+m_2l_1l_2\cos\theta_2 & m_2l_2^2
\end{bmatrix}\\
C(q,\dot{q}) &= \begin{bmatrix}
0 & -m_2l_1l_2(2\dot{\theta}_1+\dot{\theta}_2)\sin\theta_2\\
\frac{1}{2}m_2l_1l_2(2\dot{\theta}_1+\dot{\theta}_2)\sin\theta_2 & -\frac{1}{2}m_2l_1l_2\dot{\theta}_1\sin\theta_2
\end{bmatrix}\\
\tau_g(q) &= -g\begin{bmatrix}
(m_1+m_2)l_1\sin\theta_1+m_2l_2\sin(\theta_1+\theta_2)\\
m_2l_2\sin(\theta_1+\theta_2)
\end{bmatrix},\quad
B = \begin{bmatrix}1 & 0\\0 & 1\end{bmatrix}
\end{align*}$$

**观察 $M$ 矩阵**：
- 对角线上 $(m_1+m_2)l_1^2$ 是第一关节的等效惯量——**第二个关节的质量也会增加第一关节的惯量**（通过 $2m_2l_1l_2\cos\theta_2$ 项）
- 这就像你手里拿着重物伸直手臂 vs 弯曲手臂——伸直时转动惯量大得多

### 2.4 操作臂方程的重要性质

1. **$\ddot{q}$ 与 $u$ 是（状态依赖的）线性关系** ——这证明了全书使用的"控制仿射形式"是合理的
2. **$C\dot{q}$ 的每一项都是 $\dot{q}$ 的二次函数**：
$$[C\dot{q}]_i = \dot{q}^T \bar{C}_i \dot{q}$$
其中 $\bar{C}_{i;j,k} = \frac{1}{2}\left[\frac{\partial M_{ij}}{\partial q_k} + \frac{\partial M_{ik}}{\partial q_j} - \frac{\partial M_{jk}}{\partial q_i}\right]$
3. **$\dot{M} - 2C$ 是反对称的** ——这是能量守恒的数学表达

### 2.5 三维旋转的痛点：为什么需要更一般的记号

教材揭示了一个**重要限制** ：二阶系统记号 $(\dot{q}, \ddot{q})$ 无法用"最小坐标"描述三维旋转而不引入奇点（如著名的"万向锁" gimbal lock）。

**解决方案**：Drake 使用更一般的记号：

$$M(q)\dot{v} + C(q,v)v = \tau_g(q) + Bu$$

其中 $v$ 是速度向量，$\dot{q} = N(q)v$。$v$ 和 $\dot{q}$ 的长度可以不同（例如四元数表示旋转需要4个参数，但速度只需3个）。

> 💡 这就是为什么 Drake 的 MultibodyPlant 用 $v$ 而不是 $\dot{q}$——它是处理三维旋转的**无奇点方案**。

### 2.6 递归动力学算法（B.2.1）

机器人关节一多，方程就变得极其复杂。但对于**树状运动学结构**的机器人，有非常高效的**递归算法** ：

- **Featherstone 算法** ：经典之作
- **Articulated Body Method** ：另一种流行方法
- **Drake 的实现** ：基于 Jain 的方法 

**类比**：计算100个关节的机器人的动力学，如果"暴力"组装整个 $M$ 矩阵是 $O(n^3)$，而递归算法只需 $O(n)$——这是质的飞跃。

### 2.7 代码实践重点补充（**最重要**）

**实验一：用 Drake 计算双摆的操作臂方程**

```python
import numpy as np
from pydrake.all import (
    MultibodyPlant, Parser, AddMultibodyPlant,
    DiagramBuilder, Simulator, SceneGraph
)
import pydot

# 1. 创建双摆 URDF（或直接在代码中构建）
# 为简洁，这里用 Drake 的解析方式
builder = DiagramBuilder()
plant, scene_graph = AddMultibodyPlant(0.001, builder)

# 2. 用代码添加两个连杆
# 第一连杆
l1 = 1.0
l2 = 1.0
m1 = 1.0
m2 = 1.0

# 实际中会从 URDF 加载，这里展示概念
# parser = Parser(plant)
# parser.AddModels("double_pendulum.urdf")

# 3. 数值验证操作臂方程的各项
def compute_manipulator_terms(plant, q, qd):
    """计算 M, C, tau_g, B"""
    context = plant.CreateDefaultContext()
    plant.SetPositions(context, q)
    plant.SetVelocities(context, qd)
    
    # M 矩阵
    M = plant.CalcMassMatrix(context)  # 对应 M(q)
    
    # 科氏力项 C(q,qd) * qd
    C_qd = plant.CalcBiasTerm(context)  # 对应 C(q,qd)qd
    
    # 重力项
    tau_g = plant.CalcGravityGeneralizedForces(context)  # 对应 τ_g(q)
    
    return M, C_qd, tau_g

# 测试：验证 M 的正定性
q_test = np.array([0.5, 0.3])
qd_test = np.array([0.1, -0.2])
M, C_qd, tau_g = compute_manipulator_terms(plant, q_test, qd_test)

print("Mass matrix M(q):")
print(M)
print(f"\nM is symmetric: {np.allclose(M, M.T)}")
print(f"M is positive definite: {np.all(np.linalg.eigvals(M) > 0)}")
print(f"\nCoriolis term C(q,qd)qd: {C_qd}")
print(f"Gravity term tau_g(q): {tau_g}")
```

**预期现象**：
- $M$ 矩阵对称且正定
- 科氏力项非零，体现旋转耦合效应
- 重力项与关节角度相关

**深刻教训**：
> Drake 的 `MultibodyPlant` **自动计算**操作臂方程的所有项——你不需要手动推导双摆公式！这就是为什么现代机器人学用 Drake 而不是直接手写方程。

---

## 🔗 三、B.2.2 双侧位置约束（Bilateral Position Constraints）

### 3.1 问题：闭环运动学

如果机器人有**闭环运动学链**（如四连杆机构），状态向量 $q$ 就**不是最小坐标**——每个运动学环路都添加一个（至少）约束，应该去除（至少）一个自由度 。

### 3.2 约束方程

考虑约束：
$$h(q) = 0$$

时间导数：
$$\dot{h} = H v = 0$$
$$\ddot{h} = H \dot{v} + \dot{H} v = 0$$

其中 $H(q) = \frac{\partial h}{\partial q}N(q)$ 是"相对于 $v$ 的雅可比矩阵"。

### 3.3 带约束的操作臂方程

$$M(q)\dot{v} + C(q,v)v = \tau_g(q) + Bu + H^T(q)\lambda$$

其中 $\lambda$ 是**约束反力**（拉格朗日乘子）。

### 3.4 显式求解约束反力

将动力学代入 $\ddot{h}=0$：
$$\lambda = -(HM^{-1}H^T)^+(HM^{-1}\tau + \dot{H}v)$$

其中 $+$ 表示 Moore-Penrose 伪逆。

### 3.5 Baumgarte 稳定化：防止约束漂移

数值积分中约束会"漂移"。**Baumgarte 技术** 通过修改目标来加恢复力：

$$\ddot{h} = H\dot{v} + \dot{H}v = -2\alpha\dot{h} - \alpha^2 h$$

得到：
$$\lambda = -(HM^{-1}H^T)^+\left(HM^{-1}\tau + \dot{H}v + 2\alpha Hv + \alpha^2 h\right)$$

**生活类比**：想象一个橡皮筋把偏离约束的状态"拉回来"——$\alpha$ 就是橡皮筋的刚度。

### 3.6 高斯最小约束原理（Gauss's Principle of Least Constraint）

**这是本章最美的数学洞察** ：

$$\min_{\dot{v}} \frac{1}{2}(\dot{v} - \dot{v}_{uc})^T M (\dot{v} - \dot{v}_{uc})$$
$$\text{subject to } \ddot{h}(q,v,\dot{v}) = H\dot{v} + \dot{H}v = 0$$

其中 $\dot{v}_{uc} = M^{-1}\tau$ 是"无约束加速度"。

**直觉**：真实加速度是"在无约束加速度的基础上，做最小的修正以满足约束"。就像你在冰面上滑行，想转弯但被护栏约束——你做的是"最小修正"。

**对偶形式**：
$$\min_{\lambda} \frac{1}{2}\lambda^T HM^{-1}H^T\lambda - \lambda^T \ddot{h}_{uc}$$

** primal 用加速度做决策变量，dual 用约束力做决策变量**——这个对偶性在我们后面讨论接触力时极其重要。

### 3.7 代码实践补充

**实验二：四连杆机构的约束动力学**

参考 Drake 官方示例 ：

```python
# Drake 有专门的 four_bar 示例
# 源码：drake/examples/multibody/four_bar
# 它展示了如何用 penalty forces 建模闭环拓扑

# 关键思路：
# 1. 用 MultibodyPlant 建立树状结构的连杆
# 2. 用约束（revolute joint 等）连接
# 3. Drake 自动处理约束动力学
```

---

## 🎯 四、B.2.3 双侧速度约束（Bilateral Velocity Constraints）

### 4.1 问题场景

速度约束出现在"关节被驱动以预设运动"等情况：

$$h_v(q,v) = 0$$

其中 $\frac{\partial h_v}{\partial v} \neq 0$。

### 4.2 关节锁定（Example B.3）——最重要的特例

**"锁定"一个关节**（让它像焊接在当前构型）：

$$h_v(q,v) = v_i = 0$$

**操作**：从操作臂动力学中**删除与 $v_i$ 相关的项**，并设置 $\dot{v}_i = 0$。

**生活类比**：就像自行车的脚撑——撑起来后，后轮就被"锁定"不能转了。

### 4.3 显式求解

$$\lambda = -\left(\frac{\partial h_v}{\partial v}M^{-1}\frac{\partial h_v}{\partial v}\right)^+
\left[\frac{\partial h_v}{\partial v}M^{-1}\tau + \frac{\partial h_v}{\partial q}N(q)v\right]$$

Baumgarte 稳定化版本：$\dot{h}_v = -\alpha h_v$。

---

## 🔄 五、B.2.4 通过约束力建立混合模型（Hybrid Models via Constraint Forces）

### 5.1 接触模式的数学描述

对于接触的混合模型，在**浮动基坐标**中描述动力学，并求解在每个模式中实施约束的接触力是很有用的 。

**定义一个模式**：通过一对对接触几何体的列表，甚至定义每个接触是"粘滞接触"（切向相对速度为零）还是"滑动接触"。

### 5.2 粘滞接触：双侧位置约束

对于每个粘滞接触：
$$h_{A,B}(q) = {}^{W}p_{C_a}^{C_a} - {}^{W}p_{C_a}^{C_b} = 0$$

将所有这些约束组装成单个双侧约束向量 $h(q) = 0$。

### 5.3 滑动接触：标量约束 + 最大耗散

$$h_{A,B}(q) = {}^{W}p_{C_a;z}^{C_a} - {}^{W}p_{C_a;z}^{C_b} = 0$$

加上库伦摩擦的最大耗散约束：
$$\lambda_{C_a;x,y}^{C_a} = -\mu\lambda_{C_a;z}^{C_a}\frac{{}^{W}v_{C_a;x,y}^{C_a}}{|{}^{W}v_{C_a;x,y}^{C_a}|}$$

> 💡 这是第17章"通过接触做规划与控制"的数学基础——把接触建模为约束+约束力。

---

## 💥 六、B.3 接触动力学（The Dynamics of Contact）

### 6.1 三种接触建模方法

教材明确指出 ：

1. **柔顺接触模型**：用刚性弹簧（和阻尼器）近似刚性接触
2. **事件检测的刚接触**：碰撞事件检测 + 脉冲重置映射 + 碰撞事件间的连续（约束）动力学
3. **时间步进近似**：用时间平均力（冲量）在时步进方案中近似刚性接触

### 6.2 符号约定

- $\phi(q)$：两个刚体之间的相对（有符号）距离
- **单侧约束**：$\phi(q) \geq 0$（非穿透）
- $n = \frac{\partial\phi}{\partial q}$：接触法向
- $t_1, t_2$：切向基
- **接触雅可比**：$J(q) = \begin{bmatrix}n\\t_1\\t_2\end{bmatrix}$
- 接触广义力：$J^T\lambda$，其中 $\lambda = [f_n, f_{t1}, f_{t2}]^T$

带接触的操作臂方程 ：
$$M(q)\dot{v} + C(q,v)v = \tau_g(q) + Bu + J^T(q)\lambda$$

---

## 🌸 七、B.3.1 柔顺接触模型（Compliant Contact Models）

### 7.1 核心思想

用**刚性弹簧（和阻尼器）**产生抵抗穿透的力（并粗略建模碰撞和/或摩擦的耗散）。

**法向力**（分段线性弹簧定律）：
$$f_n = \begin{cases}
k\phi + d\dot{\phi} & \text{if } \phi < 0\\
0 & \text{if } \phi \geq 0
\end{cases}$$

**库伦摩擦**：
- 静摩擦：产生抵抗运动的力，上限 $\mu_{static} f_n$
- 动摩擦：滑动时产生恒定阻力 $|\mathbf{f}_t| = \mu_{dynamic} f_n$，方向与运动相反

### 7.2 生活类比：弹簧鞋垫

想象你穿了一双**带弹簧的鞋垫**走在地上：
- 脚刚接触地面时，鞋垫开始压缩（弹簧储能）
- 压缩越深，反弹力越大
- 这就是"柔顺接触"——用弹簧近似刚性接触

### 7.3 数值挑战

**致命问题**：为了紧密近似"近乎刚性"的接触，弹簧刚度 $k$ 必须**非常高** 。

**后果**：
1. **刚性微分方程**（stiff ODE）——名字不是巧合
2. 需要特殊的数值积分方法
3. 在轨迹优化/反馈优化中难以使用

**第二个挑战**：稳健计算穿透深度。当两物体碰撞时，$\phi(q)$ 的符号距离函数容易**不连续地改变法向向量方向**——导致数值爆炸（机器人"爆炸飞出地面"）。

### 7.4 柔顺模型的优缺点

**优点**：
1. 易于实现（至少对简单几何）
2. 作为连续时间模型，可以用误差控制积分器仿真
3. 近似"刚性"的程度可由直观参数控制

**缺点**：
1. 数值挑战巨大（刚性ODE、穿透法向不连续）
2. 难以用于实时优化

> ⚠️ 如果你曾在机器人仿真器中看到机器人"踏步后爆炸飞出地面"——这就是柔顺接触模型的数值失败 。

---

## ⚡ 八、B.3.2 事件检测的刚性接触（Rigid Contact with Event Detection）

### 8.1 脉冲碰撞（Impulsive Collisions）

碰撞事件由 $\phi$ 的**零交叉**（从正到负）描述 。

**无摩擦碰撞**：
$$M\dot{v} = \tau + \lambda n^T$$

对碰撞的瞬时区间 $[t_c^-, t_c^+]$ 积分：

$$M v^+ - M v^- = n^T \int_{t_c^-}^{t_c^+}\lambda dt$$

**恢复系数 $e$**（0 ≤ e ≤ 1）：
$$\dot{\phi}^+ = -e\dot{\phi}^-$$

得到碰撞后的速度：
$$v^+ = \left[I - (1+e)M^{-1}n^T[nM^{-1}n^T]^\# n\right]v^-$$

### 8.2 生活类比：篮球撞地

想象篮球从高处落下：
- **碰撞瞬间**：速度从向下 $v^-$ 瞬间变成向上 $v^+$
- **恢复系数 $e$**：决定球能弹多高（$e=1$ 完全弹性，$e=0$ 完全非弹性）
- 这就是"脉冲碰撞"——瞬间改变速度，位置不变

### 8.3 带摩擦的碰撞

扩展 $n$ 为矩阵 $J = \begin{bmatrix}n\\t_1\\t_2\end{bmatrix}$，$\lambda$ 变成接触冲量向量：

$$v^+ = \left[I - M^{-1}J^T\text{diag}(1+e, 1, 1)[JM^{-1}J^T]^\# J\right]v^-$$

### 8.4 旋转球撞地（Example B.4）——精彩实例

**系统**：平面内的球（空心球），质量 $m$，半径 $r$，构型 $q = [x, z, \theta]^T$。

**运动方程**：
$$M(q)\ddot{q} = \begin{bmatrix}m & 0 & 0\\0 & m & 0\\0 & 0 & \frac{2}{3}mr^2\end{bmatrix}\ddot{q} = \begin{bmatrix}0\\-g\\0\end{bmatrix} + \begin{bmatrix}0 & 1\\1 & 0\\0 & r\end{bmatrix}\begin{bmatrix}\lambda_z\\\lambda_x\end{bmatrix}$$

**碰撞后速度**（恢复系数 $e$）：
$$\dot{q}^+ = \begin{bmatrix}
\frac{3}{5} & 0 & -\frac{2}{5}r\\
0 & -e & 0\\
-\frac{3}{5r} & 0 & \frac{2}{5}
\end{bmatrix}\dot{q}^-$$

**观察这个矩阵**：
- $\dot{x}^+$ 受到 $\dot{\theta}^-$ 的影响（通过 $-\frac{2}{5}r\dot{\theta}^-$）——**旋转会影响平动**！
- $\dot{\theta}^+$ 受到 $\dot{x}^-$ 的影响（通过 $-\frac{3}{5r}\dot{x}^-$）——**平动也会影响旋转**！
- 这就是"摩擦碰撞"的耦合效应

### 8.5 混合模型组装

将双侧约束方程和脉冲碰撞方程组合，实现单侧约束 $\phi(q) \geq 0$ 的混合模型：

**守卫（Guards）**：
- 非活动约束 → 活动约束：$\phi_i > 0 \rightarrow \phi_i = 0$
- 活动约束 → 非活动约束：$\lambda_i > 0 \rightarrow \lambda_i = 0$ 且 $\dot{\phi}_i > 0$

> 💡 这正好是我们在第17章学的"混合系统"的数学细节！

---

## ⏱️ 九、B.3.3 刚性接触的时间步进近似（Time-stepping Approximations）

### 9.1 核心思想

**最受欢迎且可扩展的方法**：在每个仿真时间步直接构造数学程序来求解不等式约束 。

**优势**：允许用**更大且更一致的时间步**做稳定仿真。

### 9.2 互补问题（Complementarity Formulations）

最普遍的转录是**线性互补问题（LCP）** ：

$$\text{find}_{w,z} \quad \text{subject to} \quad w = q + Mz,\quad w \geq 0, z \geq 0, w^Tz = 0$$

简写为：
$$\text{find}_z \quad \text{subject to} \quad 0 \leq (q+Mz) \perp z \geq 0$$

### 9.3 时间步进 LCP：法向力（Example B.5）——**最经典的例子**

**系统**：受水平力驱动的质量块，但有墙壁阻止位置取负值（非穿透约束 $q \geq 0$）。

**半隐式欧拉离散化**：
$$\begin{align}
q[n+1] &= q[n] + h v[n+1]\\
v[n+1] &= v[n] + \frac{h}{m}(u[n] + f[n])
\end{align}$$

**LCP 形式**：
$$\begin{align}
q[n+1] &= \left[q[n] + hv[n] + \frac{h^2}{m}u[n]\right] + \frac{h^2}{m}f[n]\\
q[n+1] &\geq 0,\quad f[n] \geq 0,\quad q[n+1]\cdot f[n] = 0
\end{align*}$$

**互补约束 $q[n+1]\cdot f[n] = 0$ 的含义**：
- "要么位置为零，要么力为零"（或两者都为零）
- 这就是"no force at a distance"约束
- 它是**非凸的**

### 9.4 LCP 与凸优化的等价性

**关键洞察**：无摩擦接触动力学的 LCP **正是**以下凸二次规划的**最优性条件** ：

$$\begin{array}{ll}
\min_{v'} & \frac{1}{2}(v'-v^-)^T M(v'-v^-)\\
\text{subject to} & \frac{1}{h}\phi(q') \geq 0
\end{array}$$

其中 $v^- = v + hM^{-1}\tau$ 是"接触冲量施加前会发生的下一时刻速度"。

**对偶形式**：
$$\min_{\lambda \geq 0} \frac{1}{2}\lambda^T JM^{-1}J^T\lambda - \lambda^T \ddot{h}_{uc}$$

> 💡 primal 用加速度做决策变量，dual 用约束力做决策变量——和第B.2.2节的高斯最小约束原理完全一致！

### 9.5 时间步进 LCP：库伦摩擦（Example B.6）

引入松弛变量处理摩擦：

$$\begin{array}{ccc}
\text{find}_{v_{abs}, f^+, f^-} & \text{subject to}\\
0 \leq v_{abs} + v[n+1] & \perp & f^+ \geq 0,\\
0 \leq v_{abs} - v[n+1] & \perp & f^- \geq 0,\\
0 \leq \mu mg - f^+ - f^- & \perp & v_{abs} \geq 0,
\end{array}$$

其中 $f[n] = f^+ - f^-$。

### 9.6 Anitescu 的凸公式

**突破性的简化** ：放弃最大耗散不等式，允许摩擦锥内的任何力：

$$\begin{array}{ll}
\min_{v'} & \frac{1}{2}(v'-v^-)^T M(v'-v^-)\\
\text{subject to} & \frac{1}{h}\phi(q') + \mu d_i v' \geq 0,\quad \forall i
\end{array}$$

其中 $d_i$ 是摩擦锥多面体近似的切向行向量。

**这是一个 QP（二次规划）**！对偶形式：
$$\min_{\beta \geq 0} \frac{1}{2}\beta^T J_\beta M^{-1}J_\beta^T\beta + \frac{1}{h}\phi(q)\sum_i\beta_i + \beta^T J_\beta v^-$$

### 9.7 Todorov 的正则化（MuJoCo 的公式）

**MuJoCo 使用的变体** ：

$$\begin{array}{ll}
\min_{\lambda} & \frac{1}{2}\lambda^T JM^{-1}J^T\lambda + \frac{1}{h}\lambda^T(Jv^- - \dot{x}^d)\\
\text{subject to} & \lambda \in \mathcal{FC}(q)
\end{array}$$

其中 $\dot{x}^d = Jv - h\mathcal{B}Jv - h\mathcal{K}[\phi(q),0,0]^T$ 带有稳定化增益 $\mathcal{B}$ 和 $\mathcal{K}$。

**摩擦锥的圆锥描述**：
$$\mathcal{FC}(q) = \{\lambda = [f_n,f_{t1},f_{t2}]^T \mid f_n \geq 0, \sqrt{f_{t1}^2+f_{t2}^2} \leq \mu f_n\}$$

**对偶优化是 SOCP（二阶锥规划）**。

### 9.8 SAP 求解器（Semi-Analytic Primal）

**Drake 使用的接触求解器**进一步扩展和改进了这一系列工作 。

### 9.9 超越点接触

**点接触的局限**：
- 无法捕捉扭转摩擦等效应
- 在简单情况下表现糟糕（如盒子放在桌上）

**解决方案**：在机器人脚的四个角落放置"点接触"（零半径球体）——这是腿式机器人仿真中**非常常见的技巧** 。

**Drake 的水弹性模型（Hydroelastic model）** ：更先进的接触建模方法。

### 9.10 代码实践重点补充（**极其重要**）

**实验三：LCP vs 松弛接触对比**

课程仓库提供了 `App-b-multibody/multibody.ipynb` ——LCP vs relaxed contact 的对比实验 。

**实验四：用 Drake 做水弹性接触仿真**

参考 Drake 官方教程 ：

```python
from pydrake.all import (
    MultibodyPlantConfig, AddMultibodyPlant, Parser,
    DiagramBuilder, Simulator, SceneGraph, AddDefaultVisualization,
    StartMeshcat, VectorLogSink, ApplySimulatorConfig, SimulatorConfig,
    PrintSimulatorStatistics
)
import numpy as np

def run_hydroelastic_simulation():
    # 1. 配置 MultibodyPlant
    config = MultibodyPlantConfig(
        time_step=0.001,
        contact_model="hydroelastic_with_fallback",  # 或 "point"
        contact_surface_representation="polygon"
    )
    
    # 2. 构建场景
    builder = DiagramBuilder()
    plant, scene_graph = AddMultibodyPlant(config, builder)
    parser = Parser(plant)
    
    # 3. 加载柔顺水弹性球和桨
    ball_sdf = "package://drake/examples/hydroelastic/python_ball_paddle/ball.sdf"
    paddle_sdf = "package://drake/examples/hydroelastic/python_ball_paddle/paddle.sdf"
    
    parser.AddModels(url=ball_sdf)
    paddle = parser.AddModels(url=paddle_sdf)[0]
    
    # 4. 焊接桨到世界
    plant.WeldFrames(plant.world_frame(), 
                    plant.GetFrameByName("paddle", paddle),
                    RigidTransform(RollPitchYaw(0, 0, 0), 
                                 np.array([0, 0, -0.01])))
    
    plant.Finalize()
    
    # 5. 添加可视化和状态记录
    AddDefaultVisualization(builder=builder)
    nx = plant.num_positions() + plant.num_velocities()
    state_logger = builder.AddSystem(VectorLogSink(nx))
    builder.Connect(plant.get_state_output_port(), 
                   state_logger.get_input_port())
    
    diagram = builder.Build()
    
    # 6. 设置初始条件并仿真
    simulator = Simulator(diagram)
    simulator_config = SimulatorConfig(target_realtime_rate=1.0,
                                     publish_every_time_step=True)
    ApplySimulatorConfig(simulator_config, simulator)
    
    context = diagram.GetSubsystemContext(plant, simulator.get_context())
    plant.SetPositionsAndVelocities(context, 
        np.concatenate([np.array([1,0,0,0, 0,0,0.5]),  # 位置和姿态
                        np.zeros(3),  # 角速度
                        np.array([0,0,0])]))  # 线速度
    
    simulator.Initialize()
    simulator.AdvanceTo(0.5)
    
    PrintSimulatorStatistics(simulator)
    
    return state_logger.sample_times(), state_logger.data()

# 运行
times, states = run_hydroelastic_simulation()
print(f"Simulation completed: {len(times)} time steps")
```

**预期现象**：
- 柔顺水弹性球落到桨边缘并弹起
- 接触力通过水弹性压力场计算
- 在 MeshCat 窗口中可以看到球和桨的接触变形

**实验五：对比不同接触模型**

修改 `contact_model` 参数：
- `"point"`：点接触模型
- `"hydroelastic"`：纯水弹性模型
- `"hydroelastic_with_fallback"`：混合模型

**观察**：
- 点接触：计算快但精度低
- 水弹性：精度高但计算慢
- 混合：平衡方案

---

## 🎓 十、B.4 变分力学（Variational Mechanics）

### 10.1 虚功原理（Virtual Work）

**平衡条件**：系统处于平衡时，所有力（包括重力）的总和为零：
$$\sum_i f_i = 0$$

**更好的方法**：考虑这些力做的**虚功**（virtual work）：
$$\delta w = \sum_i \tau_i^T \delta q = 0$$

**关键优势**：
1. 虚功是标量，与坐标系选择无关
2. 内力不做功，可以忽略
3. 广义力 $\tau_i = J_i^T(q)f_i$

**重力势能**：$U_g(q)$，则 $\tau_g = -\frac{\partial U_g(q)}{\partial q}^T$

**平衡 ⇔ 势能驻定**：$\delta U(q) = 0$。稳定平衡要求 $q$ 是势能的**最小值**。

> 💡 这是力学和优化之间的**第一个重要连接**！

### 10.2 达朗贝尔原理与惯性力（D'Alembert's Principle）

**核心思想**：把动力学问题转化为静力学问题，只需加上"惯性力"：
$$\tau_{inertia} = -M(q)\ddot{q} - C(q,\dot{q})\dot{q}$$

**生活类比**：你坐在加速的汽车里，感到被"压"在座椅上——这就是惯性力。达朗贝尔原理说：如果加上这个惯性力，动力学问题就变成了静力学问题。

**惯性力的来源**：对动能 $T$ 取变分：
$$\tau_{inertia} = -\frac{\partial T}{\partial q}^T + \frac{d}{dt}\frac{\partial T}{\partial\dot{q}}^T$$

这正是我们熟悉的操作臂方程左侧的负值！

### 10.3 驻作用量原理（Principle of Stationary Action）

**作用量**（Action）：
$$A = \int_{t_0}^{t_1} L(q,\dot{q}) dt$$

**驻作用量原理**：真实轨迹使作用量取驻值（$\delta A = 0$）。

**Susskind 的名言** ：
> 最小作用量原理——实际上是驻作用量原理——是经典物理定律最紧凑的形式。这个简单的规则（可以用一行写完）总结了所有！不仅是经典力学原理，还有电磁学、广义相对论、量子力学、所有已知的化学知识——一直到物质的基本组成，基本粒子。

### 10.4 哈密顿力学（Hamiltonian Mechanics）

用 $(q, p)$ 代替 $(q, \dot{q})$，其中 $p = \frac{\partial L}{\partial\dot{q}}^T = M\dot{q}$：

$$\begin{align}
M(q)\dot{q} &= p\\
\dot{p} &= c_H(q,p) + \tau_g(q) + Bu
\end{align}$$

其中 $c_H(q,p) = \frac{1}{2}\left(\frac{\partial[\dot{q}^T M(q)\dot{q}]}{\partial q}\right)^T$。

**哈密顿量**：$H(p,q) = p^T\dot{q} - L(q,\dot{q})$，运动方程：
$$\dot{q} = \frac{\partial H}{\partial p}^T,\quad \dot{p} = -\frac{\partial H}{\partial q}^T$$

---

## 📋 十一、B.5 练习（Exercises）

### Exercise B.1：方块碰撞的时间步进 LCP 动力学

**问题**：两个宽度均为1的方块 A 和 B，在无摩擦表面上相互作用。
- 方块 A 初始：位置 $q_x = -2$，速度 $\dot{q}_x = 3$
- 方块 B 初始：位置 $q_x = 0$，速度 $\dot{q}_x = 0$
- 时间步 $h = 1.0$，质量 $m_1 = m_2 = 1$

**子问题**：
a. 推导时间步 1, 2, 3 的位置、速度和接触力（使用**隐式欧拉积分**）
b. 为什么方块 B 静止时，我们可能期望 $q_{1,x}^{(A)} = -1$，但实际不是？
c. 对于完全非弹性碰撞，连续时间物理中动量守恒会给出什么碰撞后速度？与时间步进速度相比如何？

**代码实践**：这是验证 LCP 时间步进方法的绝佳练习。

```python
import numpy as np

def implicit_euler_lcp_block_collision():
    """隐式欧拉 + LCP 求解两个方块碰撞"""
    h = 1.0
    m1 = m2 = 1.0
    
    # 初始状态
    qA, qB = -2.0, 0.0
    vA, vB = 3.0, 0.0
    
    results = [(0, qA, qB, vA, vB, 0.0)]  # (step, qA, qB, vA, vB, contact_force)
    
    for step in range(1, 4):
        # LCP 决策变量：下一时刻速度 vA', vB' 和接触力 f
        # 隐式欧拉：
        # qA' = qA + h*vA'
        # qB' = qB + h*vB'
        # vA' = vA + (h/m1)*(-f)  # A 受到向左的接触力
        # vB' = vB + (h/m2)*(f)   # B 受到向右的接触力
        
        # 互补约束：
        # 1. 非穿透：qB' - (qA' + 1) >= 0  (B 的左边界 >= A 的右边界)
        # 2. f >= 0
        # 3. 互补：f * (qB' - qA' - 1) = 0
        
        # 解析求解（参考教材 Example B.5）
        # 对于完全非弹性碰撞，穿透深度为 0
        # qB' - qA' = 1
        
        # 求解线性系统
        # 从隐式欧拉：vA' = vA - (h/m1)*f, vB' = vB + (h/m2)*f
        # 从非穿透：qB + h*vB' - (qA + h*vA') = 1