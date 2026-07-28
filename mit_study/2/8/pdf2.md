# 第 8 章 机械臂控制（Manipulator Control）—— 完全通俗讲解（含嵌入式可跑代码、逐条核查与增补）

> **先校准一件事**：你上传的这份 `Ch. 8 - Manipulator Control.pdf`，是 Russ Tedrake 的**《机器人操作》（Robotic Manipulation）** 笔记的第 8 章，**不是**《欠驱动机器人》那本的第 8 章（那本第 8 章讲 LQR）。这两本是姐妹篇，同一作者、同一套 Drake 软件。这一章的主题是：**前面几章我们让机械臂"想好了怎么动"（感知、规划、运动学都搞定了），但真正让电机去执行时，还有一层"低层控制"的活儿没干——而且这一层还要面对一个前面一直躲着的东西：接触力。** 这一章就是补这块。它没有花哨的公式推导，重点是**理解几种低层控制器各干啥、为什么这么设计、仿真时怎么 faithfully 模拟真实硬件**。我照例做三件事：① 每个概念配生活类比；② PDF 的**每一节、每个 Example（8.2–8.8）、每个框图、每道练习（8.1–8.4）、每篇参考文献**都覆盖；③ 文末做**逐条核查 + 通俗性增补 + 代码实践增补**（PDF 这一章几乎没有内联代码，Example 全指向 notebook，所以代码增补是重中之重，我会把 PID、反射惯量仿真、HardwareStation 骨架等全补上）。最终你拿到的是一份**已过二次打磨的完整讲义**。

---

## 0. 开篇：从"想好怎么动"到"让电机真的动起来"

### 0.1 一句话概括

> **前面我们让机械臂"在脑子里"规划好了轨迹，但真正驱动电机去执行时，还需要一层"低层控制器"把"期望位置/速度/力"翻译成"电机电流"。这一层看似琐碎，却藏着仿真与真实之间的鸿沟（齿轮、摩擦、刹车），还要面对一个前面躲着的东西——接触力。本章逐一讲清 Drake 提供的几种低层控制器，并诚实告诉你仿真时哪些坑。**

### 0.2 引言逐句翻译

> 前面几章我们开发了感知、规划、运动学的工具箱。但要执行轨迹，控制策略需要更精细。回忆 bin picking demo，微分逆运动学（基本忽略关节角）有时会让机器人自己折叠（fold in on itself）。本章引入考虑接触力的控制技术。

> 还要提**非抓取操作（non-prehensile manipulation）**：推一把太大的椅子、人类经常用的滑动和环境接触，即使抓取时也常用。本章要补上"力"的思考。希望读完你同意：我们有相当令人满意的方法来翻起那个盒子！

**类比（"想好了"和"做出来"之间隔着一层肌肉，全章总纲）**：
- 前面几章 = **大脑想好了"手要伸到这儿、抓这个"**。
- 本章 = **脊髓和肌肉**：把"伸到这儿"翻译成"肱二头肌收缩多少、肘关节使多大劲"。
- 这层看似低级，但**它直接和物理世界接触**——齿轮会卡、摩擦会咬、刹车会咬死、碰东西会反弹。**这层搞不好，大脑想得再美，手也会抽风（自己折叠）**。

---

## 1. 对应 8.1：机械臂控制工具箱（THE MANIPULATOR-CONTROL TOOLBOX）

### 1.1 这一节在讲什么

> 本章讨论的"manipulator control" = 接收**稍高层命令**（期望关节位置/速度，或空间力），转换成**电机命令**的控制器。这些控制器**本身不足以完成任何有意义任务**——它们只推理机器人本身，不推理环境物体。但它们通过提供**高层抽象**，方便编写其余控制系统。

> 通常低层控制器实现在**固件**里（机器人臂或控制柜）。为使用硬件，理解它们如何工作、如何设参数很重要。仿真中我们需要**自己实现**这些控制器来建模机器人。

> Drake 提供若干实现，本章逐一讲最相关的，对应四个框图：

```
estimated_state, desired_state            → PidController            → actuation
estimated_state, desired_state,
  desired_acceleration                    → InverseDynamicsController → generalized_force
estimated_state, desired_spatial_force    → SpatialForceController   → actuation
estimated_state, desired_state,
  desired_pose, desired_spatial_velocity,
  secondary_task                          → SpatialStiffnessController → actuation
```

**类比（四种"翻译官"，必懂）**：把"大脑的命令"翻译成"肌肉电流"，有四种翻译官，各吃不同输入：
- **PidController** = "**你说'关节转到 30 度'，我盯着当前角度，差多少补多少**"（最朴素，PID）。
- **InverseDynamicsController** = "**你说'关节转到 30 度、还要这个加速度'，我连重力、惯性一起算清楚该使多大劲**"（更懂物理）。
- **SpatialForceController** = "**你说'手要往下压 10 牛'，我算电机该使多大劲**"（力控）。
- **SpatialStiffnessController** = "**你说'手要摆这个姿势、还要这个刚度'，我让手像弹簧一样顶回去**"（阻抗控制，最全能）。

**人话**：**这四种控制器是"由简到繁"的工具箱**，本章逐一讲它们吃啥、吐啥、啥时候用。

---

## 2. 对应 8.2：先假设你的机器人是个质点（ASSUME YOUR ROBOT IS A POINT MASS）

### 2.1 为什么先简化

> 作为对抗复杂性的战斗，先找尽可能简单的设置。提出 **box-flipping（翻盒子）** 例子。先限制所有运动到 2D 平面（切掉 bin 两边方便看，也减少自由度）。可以用完整夹爪，但更简单用"**point finger**"（一个点手指）。可视化为小球，建模两个控制输入直接提供点质量的力。

> **Figure 8.4**：简单模型——point finger、cracker box、bin 都在 2D。绿箭头是接触力。

> 即使这个简单模型，本章我们关心**两个动力学模型**：
> 1. **完整模型**（用于仿真）：含 finger、box、bin，共 **5 自由度**（box 3 + finger 2）。
> 2. **控制器用的机器人模型**：只有 finger 的 2 自由度，经历**未建模的接触力**。设计上第二个模型方程特别简单：

$$\begin{bmatrix} m & 0 \\ 0 & m \end{bmatrix} \dot v = \begin{bmatrix} 0 \\ -mg \end{bmatrix} + \begin{bmatrix} u_x \\ u_z \end{bmatrix} + F_c$$

> 其中 $m$ 是质量，重力"扭矩"这里就是 $[0,-mg]$，$u$ 是控制输入向量，$F_c$ 是施加在 finger 上的笛卡尔接触力。

**类比（两个模型 = "上帝视角"和"机器人自己视角"，必懂）**：
- **完整模型** = **上帝视角**：上帝知道手指、盒子、箱子所有东西怎么动，用来**仿真**（看真实世界会发生啥）。
- **控制器模型** = **机器人自己视角**：机器人**只知道自己手指**，盒子碰它产生的力它**当作"外界未知力 $F_c$"**——它不知道盒子多重、摩擦多大，只知道"有个力顶着我"。
- **所以控制器模型方程特别简单**：就是 $m\dot v = $ 重力 + 我使的力 $u$ + 外界顶我的力 $F_c$。**简单到就是个质点牛顿第二定律**。

### 2.2 空间力记号（spatial force notation）

> 本章大量用空间力记号。为清楚，用 $F^{name}_{Bp,C}$ 表示**施加在 body $B$ 的点 $p$、在 frame $C$ 表达的命名空间力**。Drake 中带括号形式更受欢迎但太冗长。名字可选，expressed-in frame 若未指定则是 world frame。对力特别推荐在点 $p$ 的符号中包含 body $B$，因为常有等大反向的力。代码中写 `Fname_Bp_C`。

**类比（力的"完整地址"，必懂）**：一个力要写清楚三件事——**作用在谁身上（body B）、作用在哪个点（p）、用哪把尺子读（frame C）**。就像寄快递要写"收件人+门牌号+用哪种坐标系描述门牌号"。**带括号的形式太啰嗦，所以代码里用下划线简写 `Fname_Bp_C`**。

---

### 2.3 对应 8.2.1：轨迹跟踪（Trajectory tracking）—— PID 登场

> 在让 finger 接触 box 之前，先确保知道如何让 finger 在空中移动。假设做了运动规划，得到期望轨迹 $q_d(t)$。用 **PID 控制**跟踪：

$$\tau = k_p(q_d - q) + k_d(\dot q_d - \dot q) + k_i \int (q_d - q)\,dt$$

> $k_p, k_d, k_i$ 是位置、速度、积分增益。PID 有丰富理论和增益选择知识宝库，不复述。但注意：**仿真位置控制机器人时常常需要对物理机器人和仿真用不同增益**。这是由于传动动力学，也因为硬件 PID 通常输出**电压命令（通过 PWM）** 而非电流命令。弥合这个建模差距传统上不是仿真优先——有足够多其他细节主导 sim-to-real 差距——但怀疑随着领域成熟，主流仿真器最终会捕捉这个。

> 有些人想"我能训练神经网络建模任何东西，不怕难建模的传动！"确实有理由乐观，有初步演示 [1]。这不如"能从描述文件少数参数泛化到新执行器的第一性原理模型"有用，但可能很有成效。

**类比（PID = "看着误差调油门"，必懂）**：
- **P（比例）** = "**差多少补多少**"：差 10 度补 10 份力。
- **D（微分）** = "**眼看要冲过头就提前松**"：看误差变化趋势，提前踩刹车，防抖。
- **I（积分）** = "**差一点点迟迟不消，就慢慢累积加力**"：消除"差一丢丢永远差一丢丢"的稳态误差。
- **为什么仿真和真机增益不同**？真机的 PID 输出的是**电压**（经 PWM），不是电流；传动还有摩擦、齿隙。**仿真里若按"理想电流"建模，增益就对不上真机**。

**旁白：神经网络建模传动** = "**与其用公式描那个不听话的齿轮箱，不如让神经网络看数据学它的脾气**"。可能 work，但不如"第一性原理模型能从少数参数泛化"有用。

**旁白：带传动的连杆动力学（reflected inertia，反射惯量，本章唯一硬推导，重点）**

> 可能令人惊讶：尽管机械臂关节动力学高度耦合并状态依赖，**PID 增益常常对每个关节独立选择，且常数**（非增益调度）。难道不期望全伸展拿牛奶壶的电机命令与无负载垂直悬挂的不同吗？令人惊讶的是，所需增益/命令**可能没你想的那么不同**。

> 电机在高速最高效（常 >100 或 1000 rpm）。我们可能不希望机器人动那么快即使能！所以几乎所有电动机器人都有**相当大的齿轮减速**，常 100:1 量级；传动输出转一圈对应电机转 100 圈，输出扭矩是电机扭矩 100 倍。对齿轮比 $n$，驱动关节，有：

$$q_{motor} = n\,q,\quad \dot q_{motor} = n\,\dot q,\quad \ddot q_{motor} = n\,\ddot q,\quad \tau_{motor} = \tfrac{1}{n}\tau$$

> 有趣的是，这对结果动力学有相当深远影响（即使单关节）。写关节扭矩和关节加速度关系（还没电机），旋转坐标可写 $I_{arm}\ddot q = \tau_{gravity} + \tau$，其中 $I_{arm}$ 是转动惯量。例如简单摆，可能有 $ml^2\ddot q = -mgl\sin q + \tau$。

> 但施加的关节扭矩 $\tau$ 实际来自电机——若用电机坐标写：

> ⚠️ **PDF 此处中间一行 OCR/排版有误**（写成了 $I_{arm}\ddot q_{motor}=\tau_{gravity}+n\tau_{motor}$，缺了电机惯量项且重力项系数不对）。**正确推导如下**：关节方程 $I_{arm}\ddot q = \tau_{gravity} + \tau_{joint}$，其中传动输出扭矩 $\tau_{joint}=n\,\tau_{motor}$；代入 $\ddot q=\ddot q_{motor}/n$ 并整理到**关节坐标**得 $(I_{arm}+n^2 I_{motor})\ddot q = \tau_{gravity}+n\,\tau_{motor}$（电机转子惯量 $I_{motor}$ 反射到关节侧放大 $n^2$）。再换到**电机坐标**（$\ddot q_{motor}=n\ddot q$）即得 PDF 的最终正确公式：

$$(I_{motor} + I_{arm}/n^2)\,\ddot q_{motor} = \tau_{gravity}/n + \tau_{motor}$$

> 若两边除以 $n$，并考虑电机本身有惯量（如来自大旋转磁铁）不受齿轮比影响，则得上式。

> 有趣的是，即使电机质量可能只占机器人总质量小比例，对高齿轮比机器人它们在关节动力学中起**显著作用**。用"**reflected inertia（反射惯量）**"表示由于传动缩放效应在传动另一侧感受到的惯性负载。**臂在电机处的反射惯量被齿轮比平方削减；或电机在臂处的反射惯量被齿轮比平方放大**。这有有趣后果——多连杆情况，$I_{arm}$ 是状态依赖函数，捕捉被驱动连杆惯量及机械臂其他关节的惯性耦合。$I_{motor}$ 另一方面是常数，只影响局部关节。**对大齿轮比，$I_{motor}$ 项主导其他项**，有两个重要效应：1）**有效对角化**机械臂方程（惯性耦合项相对小），2）动力学在整个工作空间**相对常数**（状态依赖项相对小）。这些效应使**相对容易为每个关节独立调常数反馈增益在所有构型表现良好**。

**类比（反射惯量 = "齿轮把对面的重量'缩放'过来"，必懂，这是本章最该懂的物理）**：
- 想象电机和关节之间隔着一个 **100:1 的齿轮箱**。
- **从电机往关节看**：关节那边挂的重物（$I_{arm}$），反射到电机这边**缩小 10000 倍**（$n^2$）——电机觉得"对面轻飘飘"。
- **从关节往电机看**：电机转子的惯量 $I_{motor}$ 反射到关节这边**放大 10000 倍**——关节觉得"电机那头沉得要命"。
- **后果**：对大齿轮比，**关节感受到的惯量主要是"电机反射过来的常数 $n^2 I_{motor}$"**，而"手臂姿态带来的变化 $I_{arm}$"被 $/n^2$ 压得微不足道。
- **所以**：① 各关节之间的"互相牵连"（耦合）被压没 → **方程近似对角化**；② 姿态变化带来的惯量变化被压没 → **动力学处处差不多**。
- **于是**：**每个关节可以独立调一套常数 PID 增益，在所有姿势都好使**——**这就是那个"令人惊讶"的事实的根**！

> 这就是为什么"全伸展拿牛奶壶"和"空载悬挂"用**同一套增益**也还行——**因为电机那头反射过来的"常数大惯量"主导了一切，手臂姿势的变化被齿轮比平方压成了噪声**。

### 🧪 代码 1：反射惯量仿真对比（numpy，可跑，对应 Exercise 8.1）

> 这段对比**直接驱动**（$n=1$）和**高齿轮比**（$n=100$）的简单摆，在**同一套 PD 增益**下的表现——**亲眼见高齿轮比让"姿态/负载变化"变得无所谓**。

```python
import numpy as np
import matplotlib.pyplot as plt

def sim_pendulum(n, kp, kd, m=1.0, l=1.0, g=9.81, I_motor=0.01,
                 payload=0.0, dt=1e-3, T=4.0):
    """n=齿轮比; payload 加到 I_arm 模拟'拿牛奶壶'负载"""
    I_arm = m*l**2 + payload            # 关节侧惯量(含负载)
    # 关节坐标方程: (I_arm + n^2 I_motor) q̈ = -mgl sin q + n*τ_motor
    # 电机侧 PD: τ_motor = kp*(qd-q)/n + kd*(q̇d-q̇)/n  (电机坐标误差)
    I_eff = I_arm + n**2 * I_motor
    q, qd = 1.0, 0.0                    # 从 1 rad 释放, 目标 qd=0
    hist = []
    for _ in range(int(T/dt)):
        tau_motor = kp*(0 - q)/n + kd*(0 - qd)/n     # 电机坐标 PD
        tau_gravity = -m*g*l*np.sin(q)
        qdd = (tau_gravity + n*tau_motor) / I_eff     # 关节坐标加速度
        qd += qdd*dt; q += qd*dt; hist.append(q)
    return np.array(hist)

kp, kd = 50.0, 10.0
t = np.linspace(0,4,int(4/1e-3))
for n, lab in [(1,"直接驱动 n=1"), (100,"高齿轮比 n=100")]:
    for pay, ls in [(0.0,'-'), (3.0,'--')]:     # 0=空载, 3=拿重物
        q = sim_pendulum(n, kp, kd, payload=pay)
        plt.plot(t, q, ls, label=f"{lab} 负载={pay}")
plt.axhline(0,color='k',lw=.5); plt.legend(); plt.grid(alpha=.3)
plt.xlabel('时间'); plt.ylabel('关节角 q'); 
plt.title('反射惯量: 高齿轮比下, 加负载几乎不影响响应(线重合)'); plt.show()
```

**你会看到**：**直接驱动（n=1）时，加负载（虚线）和空载（实线）响应差很多**（同一套增益扛不住负载变化）；**高齿轮比（n=100）时，加负载和空载的线几乎重合**——**亲眼见反射惯量让"负载/姿态变化"变得无所谓**，**验证了"常数增益处处好使"的物理根**。

### 🧪 代码 2：PID 控制器（Drake LeafSystem 骨架 + numpy 演示，对应 8.2.1 / Exercise 8.4）

```python
import numpy as np
# --- numpy 演示 PID ---
def pid_step(q, qd, qd_des, qd_des_dot, integral, kp, kd, ki, dt):
    err = qd_des - q
    integral += err*dt
    tau = kp*err + kd*(qd_des_dot - qd) + ki*integral
    return tau, integral

# --- Drake 骨架: 自己写一个 PidController 风格的 LeafSystem ---
# from pydrake.all import LeafSystem, BasicVector
# class MyPidController(LeafSystem):
#     def __init__(self, n, kp, kd, ki=0.0):
#         super().__init__()
#         self.kp, self.kd, self.ki = kp, kd, ki
#         self.DeclareVectorInputPort("estimated_state", BasicVector(2*n))
#         self.DeclareVectorInputPort("desired_state", BasicVector(2*n))
#         self.DeclareVectorOutputPort("actuation", BasicVector(n), self.CalcTau)
#         self.integral = self.DeclareDiscreteState(n)   # 积分项状态
#         self.DeclarePeriodicDiscreteUpdateEvent(dt=0.001, offset=0.0, update=self.UpdateIntegral)
#     def CalcTau(self, ctx, out):
#         s = ctx.get_input_port(0).Eval(ctx); d = ctx.get_input_port(1).Eval(ctx)
#         q, qd = s[:n], s[n:]; qd_d = d[n:]
#         integ = ctx.get_discrete_state(0).get_value()
#         out.SetFromVector(self.kp*(qd_d-q) + self.kd*(d[n:]-qd) + self.ki*integ)  # 简化
# 注: Drake 已自带 PidController, 这里只为让你看懂内部; Exercise 8.4 要你从零写 PD 再扩 PID
```

**人话**：**Drake 自带 `PidController`，但 Exercise 8.4 要你从零写一遍**——**因为懂了内部，你才知道"为什么仿真和真机增益不同"（PWM 电压 vs 电流）**。**a 写 PD（去掉积分项），b 加上积分状态和 $k_i$ 项**。

---

### 2.4 对应 8.2.2：扭矩控制机器人（Torque-controlled robots）

> 虽然不常见，有一些机器人确实支持直接控制关节扭矩。有几种实现方式：

1. **小齿轮减速（如 10:1）的电机**，摩擦可忽略。过去这些"**direct-drive robots**" [2] 有巨大电机和有限负载。最近，像 **Barrett WAM** 臂用 **cable drives** 通过把大电机放在基座保持臂轻。最近几年，高扭矩 outrunner 和 frameless 电机进步带来新一代低成本"**quasi-direct-drive**"机器人：如 **MIT Cheetah** [3]、Berkeley Blue、Halodi Eve。

2. **液压执行器**：另一种产生大扭矩无需大传动的方案。**Sarcos** 有一系列扭矩控制臂（和人形），**Boston Dynamics** 许多最著名机器人基于液压（虽有向电机转变趋势）。这些机器人通常有单个中央泵，每个执行器有轻量阀可分流流体通过执行器或旁路；执行器两端压差至少近似正比于产生的力/扭矩。

3. **保持大齿轮比电机，但加传感器直接测量关节侧扭矩**。这是 **Kuka iiwa** 使用的方法；iiwa 执行器有集成到传动的**应变片**。但**传动刚度和力/扭矩测量精度之间有 trade-off** [4]——iiwa 传动包含显式"**Flex Spline**"，刚度约 5000 Nm/rad [5]。把这个想法推到极端，**Gill Pratt** 提出"**series elastic actuators（串联弹性执行器，SEA）**"，传动中有更低刚度弹簧，提出测量传动电机侧和关节侧的关节位置估计施加扭矩 [6]。例如 Rethink 的 **Baxter** 和 **Sawyer** 用 SEA；我不认为他们公布过弹簧刚度值，但类似动机的 **HEBI robotics** SEA 接近 100 Nm/rad。即使对 iiwa 执行器，关节弹性显著到低层控制器煞费苦心显式考虑它以实现高性能控制 [7]。我们将在力控制章讨论细节。

**类比（四种"产生扭矩"的办法，必懂）**：
1. **直驱** = "**电机直接拽关节，中间没齿轮**"——扭矩=电流×常数，干净！但电机得**巨大**才有力。
2. **cable drive** = "**大电机放基座，用钢丝绳把力传到关节**"——臂轻了。
3. **液压** = "**高压油推活塞**"——力大，压差≈力，但系统重、复杂。
4. **应变片/SEA** = "**在齿轮箱里塞个'弹簧秤'**"——齿轮箱稍软，形变就能换算成扭矩。**iiwa 用应变片（刚度 5000 Nm/rad），Baxter 用串联弹簧（更软，~100 Nm/rad）**。**弹簧越软，扭矩测得越准，但关节越"软绵绵"**——**这就是 trade-off**。

**类比（为什么"软"反而好测力）**：硬弹簧形变小，测形变误差大；**软弹簧形变大，测得准**——**就像用软弹簧秤称东西比用硬铁杆准**。代价是关节变"软"，控制要更小心。

### 2.5 对应 8.2.3：硬件的激增（A proliferation of hardware）

> 低成本扭矩控制臂只是机器人臂大规模激增的开始。疫情期间我看到许多人在家用便宜机器人如 **xArm**。随着需求增加，成本会继续下降。

> 相比腿式机器人（几十年我们在楼下机加工车间用研究生（偶尔教授！）建实验室原型做研究），**专业工程化、高质量、高正常运行时间硬件的可用性是绝对享受**。这也意味着我们可以在一个实验室测试算法，让另一个实验室（也许在另一个大学）在几乎相同硬件上测试；这促进了以前不可能的**可重复性和共享**水平。价格下降意味着更多类似机器人在更多实验室/环境，这是我对领域未来几年如此乐观的大原因之一。

> **现在是做 manipulation 的好时候！**

**类比（从"手工作坊"到"流水线"，必懂）**：以前做机器人像**手工作坊**——每个实验室自己车床铣原型，互相没法比；现在像**流水线**——大家买同一款 xArm/iiwa，**算法可直接复现、共享**。**这是领域成熟的标志**。

### 2.6 对应 8.2.4：仿真 Kuka iiwa（Simulating the Kuka iiwa）

> 是时候仿真我们选的机器人臂了。第一步是获得机器人描述文件（通常 URDF 或 SDF）。为方便，Drake 随附几个机器人模型，包括 iiwa。若想仿真不同机器人，可在网上找到描述大多数商用机器人的 URDF 或 SDF。但**警告**：这些模型质量可能 wildly 不同。我们见过甚至**运动学**（连杆长度、几何等）都有惊人错误，但**动力学属性**（惯量、摩擦等）特别常常完全不准确。有时甚至**数学上不一致**（如可能在 URDF/SDF 中指定任何刚体都无法物理实现的惯性矩阵）。**Drake 会抱怨**若你要求加载有这种违规的文件；我们宁愿早点提醒你而非开始生成虚假仿真。也有越来越好的支持从 CAD 软件如 Solidworks 直接导出到机器人格式。

> 现在必须把这个机器人描述文件导入物理引擎。在 Drake 中，物理引擎叫 **MultibodyPlant**。"**plant**"这个词可能奇怪但普遍；它是控制文献中表示**要被控制的物理系统**的词，起源于**化工厂控制**。这个与控制理论的联系对我非常重要。世界上没多少物理引擎像 Drake 那样煞费苦心使物理引擎与控制理论设计和分析兼容。

> MultibodyPlant 有类接口，有丰富方法库处理机器人运动学和动力学。若需计算质心位置、运动学 Jacobian 或任何类似查询，用这个类接口。MultibodyPlant 也实现接口作为 Drake 系统框架中的 **System**，带输入输出端口。为仿真或分析 MultibodyPlant 与其他系统（如感知、规划、控制系统）的组合，我们将组装**框图**。

```
applied_generalized_force ─┐
applied_spatial_force ─────┤
model_instance_name[i]_actuation ─┤→ MultibodyPlant → continuous_state
geometry_query ────────────┤                       → body_poses
                                                   → body_spatial_velocities
                                                   → body_spatial_accelerations
                                                   → generalized_acceleration
                                                   → reaction_forces
                                                   → contact_results
                                                   → model_instance_name[i]_continuous_state
                                                   → model_instance_name[i]_generalized_acceleration
                                                   → model_instance_name[i]_generalized_contact_force
                                                   → geometry_pose
```

> 如你所料对像物理引擎这样复杂通用的东西，它有许多输入输出端口；大多数可选。

**类比（MultibodyPlant = "物理世界的模拟器内核"，必懂）**：
- **MultibodyPlant** = 一个"**物理计算器**"：你给它"机器人长啥样（URDF）+ 此刻使多大劲"，它算出"下一秒每个关节怎么动、哪里碰撞、碰撞力多大"。
- **"plant"** = 控制论老词，指"**被控制的那个物理对象**"（化工厂里被控制的反应釜叫 plant，沿用下来）。
- **它有一堆"插口"（端口）**：你往里塞"力/扭矩/几何查询"，它往外吐"位置/速度/加速度/接触力"。**大多数插口可选**。

**Example 8.2（Simulating the passive iiwa）**：值得花几分钟看这个例子，它应帮你理解不仅物理引擎，还有 Drake 中仿真的基本机制。可视化物理引擎结果最好用 2D 或 3D 可视化器。为此，需添加策展场景几何的系统；在 Drake 中叫 **SceneGraph**。一旦有 SceneGraph，有许多不同可视化器和传感器可加到系统实际渲染场景。

```
source_pose{0} ─┐
...            ─┤→ SceneGraph → lcm_visualization
source_pose{N-1}─┘              → query
```

**Example 8.3（Visualizing the scene）**：这个例子看起来有趣多了。现在我们有 3D 可视化！你可能想知道为什么 MultibodyPlant 不也处理场景几何。嗯，有许多应用我们想渲染复杂场景、用复杂传感器，但提供自定义动力学而非用默认物理引擎。**自动驾驶是好例子**；那种情况我们想用所有车辆和环境几何填充 SceneGraph，但常常想用非常简单车辆模型仿真车辆，远不到把轮胎力学加进物理引擎。我们在 Underactuated Robotics 课程也有许多这种工作流例子，大量使用"简单模型"。

**类比（为什么物理和几何分开，必懂）**：**MultibodyPlant 管"东西怎么动"，SceneGraph 管"东西长啥样、谁挨着谁"**。**自动驾驶想渲染逼真城市（SceneGraph 忙），但车本身用简单模型（MultibodyPlant 闲）**——**分开才能各取所需**。

> 我们现在有 iiwa 的基本仿真，但已有一些微妙之处出现。物理引擎需要被告知在关节施加什么扭矩。在我们的例子中，**施加零扭矩，机器人倒下**。**现实中，那从不发生**；事实上几乎从没有物理 iiwa 机器人在关节经历零扭矩的情况，即使控制器关闭。像许多成熟工业机器人臂，**iiwa 在每个关节有机械刹车**，每当控制器关闭时啮合。为仿真控制器关闭的机器人，需告诉物理引擎这些刹车产生的扭矩。

> 事实上，即使控制器开启，尽管它是扭矩控制机器人，**我们从不实际能发送零扭矩到电机**。iiwa 软件接口接受"**feedforward torque**"命令，但它总把这些作为**额外扭矩**加到低层控制器，**低层控制器补偿重力和电机/传动力学**。这常常令人沮丧，但可能我们实际不想陷入仿真驱动力学细节。

> 结果，我们能提供的 iiwa 最简单合理仿真**必须包含 Kuka 低层控制器的仿真**。我们将用 iiwa 的"**joint impedance control**"模式，一旦它们对让机器人表现更好变得重要时描述细节。现在，可当作给定，产生我们最简单合理 iiwa 仿真。

**Example 8.4（Adding the iiwa low-level controller）**：这个例子添加 iiwa 控制器并设期望位置（不再是期望扭矩）为机器人当前状态。它是真实机器人更忠实的仿真。抱歉它又无聊了！

> 作为最后注记，你可能认为仿真机器人动力学是 overkill，若我们唯一目标是仿真机器人只相对慢移动的 manipulation 任务，质量、惯量和力的效应可能不如机器人（和物体）在空间占据的位置重要。我实际同意你。但**令人惊讶地棘手的是让运动学仿真尊重交互的基本规则**；如知道物体何时被捡起或何时没有（见例如 [8]）。目前在 Drake 中，我们主要用完整物理引擎仿真，但常常用更简单模型做 manipulation 规划和控制。

**类比（为什么"发零扭矩机器人就倒"是仿真的坑，必懂）**：
- 仿真里你发"零扭矩"，物理引擎老老实实让机器人**瘫倒**（没力撑着当然倒）。
- 但**真 iiwa 从不瘫**——**它关机有刹车咬死，开机低层控制器一直在补偿重力**。
- **所以"忠实仿真"必须把 Kuka 低层控制器也建进去**——**否则仿真和真机对不上**。
- **"运动学仿真"为什么不够**？因为它**不知道物体何时被捡起**（运动学不管力，没法判断"抓没抓住"）——**所以 Drake 主要用完整物理引擎**。

### 🧪 代码 3：MultibodyPlant + SceneGraph 仿真 iiwa 骨架（对应 Example 8.2, 8.3, 8.4）

```python
from pydrake.all import (DiagramBuilder, Simulator, Parser,
                         AddMultibodyPlantSceneGraph, MeshcatVisualizer, StartMeshcat)
builder = DiagramBuilder()
plant, scene_graph = AddMultibodyPlantSceneGraph(builder, time_step=0.001)
Parser(plant).AddModelsFromUrl(
    "package://drake/manipulation/models/iiwa_description/urdf/"
    "iiwa14_spheres_dense_elbow_collision.urdf")
plant.WeldFrames(plant.world_frame(), plant.GetFrameByName("iiwa_link_0"))  # 焊在地上
plant.Finalize()
meshcat = StartMeshcat()
MeshcatVisualizer.AddToBuilder(builder, scene_graph, meshcat)
# Example 8.2: 此时若给关节加 0 扭矩输入, iiwa 会瘫倒(真实iiwa不会, 因有刹车+低层控制器)
# Example 8.4: 加 iiwa 低层阻抗控制器, 设 desired_position = 当前状态 -> 更忠实仿真
diagram = builder.Build()
sim = Simulator(diagram); sim.set_target_realtime_rate(1.0); sim.AdvanceTo(3.0)
```

**人话**：**这段搭出"iiwa + 3D 可视化"**。**Example 8.2 给零扭矩会瘫**；**Example 8.4 加低层阻抗控制器才忠实**。**这就是 8.2.4 的核心教训**。

---

## 3. 对应 8.3：手（HANDS）

> 你可能注意到 iiwa 模型实际没有附带手；机器人附带安装板让你可安装你选的"**end-effector**"（和一些访问端口选项让你可连接 end-effector 到计算机而不用线沿机器人外面跑）。所以现在我们有另一个决定：用什么手？

**Example 8.5（Robot hands）**：我们可以用和臂相同接口在 Drake 中探索不同手模型，虽然我这里还没那么多手模型。让我知道你最喜欢的手不在列表上！

> 有趣的是，当谈到机器人 end effectors，manipulation 研究者倾向于**分成几个不同阵营**。

### 3.1 对应 8.3.1：灵巧手（Dexterous hands）

> **Figure 8.3**：灵巧手。左：Shadow Dexterous Hand。右：Allegro Hand。

> 当然，我们对手手的迷恋有充分理由，我们梦想建造和人手一样灵巧和传感器丰富的机器人手。但现实是我们还没到那。有些人选择追求这个梦想，用市场上最好的灵巧手工作，并挣扎于随之而来的**复杂性和缺乏鲁棒性**。OpenAI 著名的"**learning dexterity**"项目用 Shadow 手玩魔方，为支持耐力学习实验必须投入到手的工作绝对是故事的一部分。有可能新制造技术真能颠覆这个空间——像 **FLLEX v2** 这样的视频看起来惊人 [9]——我非常乐观我们在不远将来会有更能力和鲁棒的灵巧手。

**类比（灵巧手 = "仿人五指"，必懂）**：**能力天花板最高**，但**手指多=坏的地方多=娇贵**。OpenAI 转魔方背后"为手做的工程"是巨大故事。

### 3.2 对应 8.3.2：简单夹爪（Simple grippers）

> [视频：Keenan Wyrobek, Robot Cleans a Room (8x Speed Up)]
> **Figure 8.4**：Ken Salisbury 组 PR1 遥操作视频现在是经典例子，展示用非常简单手做惊人有用事情。看他们网站更多视频，包括扫地、拿啤酒、卸洗碗机。

> 另一个阵营指出灵巧手不必要——我可以给你一个玩具店简单夹爪，你仍能完成家里惊人有用任务。上面 PR1 视频是这点的伟大演示。

> 支持简单手的另一个重要论点是**减少复杂性带来的优雅和清晰**。若清楚思考简单夹爪帮我们更深理解为什么我们需要更灵巧手（我认为会），那很好。对这些笔记的大多数，**简单两指夹爪**最能服务于我们的教学目的。特别地，我选了 **Schunk WSG 050**，我们在过去几年研究中大量使用。

> 要明确：**手简单（少自由度）不意味着它低质量**。相反，**Schunk WSG 是非常高质量夹爪**，在其单自由度上有力控制和力测量，**超过 Kuka 的保真度**。在多关节灵巧手中很难达到同样。

**类比（简单夹爪 = "老虎钳"，必懂）**：**简单≠劣质**。Schunk WSG 单自由度上的力控/力测精度**比灵巧手每个手指还高**。**教学上，简单夹爪让你"想清楚本质"**。

### 3.3 对应 8.3.3：软/欠驱动手（Soft/underactuated hands）

> 最后，第三个和最新阵营在推广手的巧妙机械设计，常叫"**underactuated hands**"。基本想法是，对许多任务，你可能不需要手中和关节一样多的执行器。许多欠驱动手用 **cable-drive** 机制闭合手指，单根肌腱能让手指多个关节弯曲。设计正确时，这些机制能让手指**被动顺应**被抓物体形状而执行器命令不变（c.f. [10]）。cable 不是这个概念工作的必需；用巧妙刚性机械连杆也能达到定性类似行为。

> **Figure 8.5**：欠驱动手。左：RightHand Robotics Reflex2 是 i-HY 手 [10] 的后代。右：Robotiq 三指夹爪。
> **Figure 8.6**：巧妙机械连杆让欠驱动 Robotiq 三指夹爪顺应被抓物体。

> 把欠驱动和被动顺应想法推到极端，最近几年也看到一些手（或至少手指）**完全软**。"**soft robotics community**"在机器人制造方面快速改变现状，附肢、执行器、传感器甚至电源可完全软。这些技术有望提高耐用性、降低成本，并可能对在人周围操作更安全。

> **Figure 8.7**：欠驱动手。左：哈佛 3D 打印软手（Image credit: Ryan Truby）。右：RBO Hand 2（Image credit: Disney Research Zurich）。

> 欠驱动手可以是机械设计减少执行器/控制系统负担的极好例子。常常这些手在某范围任务上惊人好（最常"**enveloping grasps**"），但不那么通用。很难用其中一个，例如，扣我衬衫。它们正变得越来越灵巧；看下面视频！[视频：Robotics and Biology Lab (RBO), Surprisingly Robust In-Hand Manipulation]

**类比（欠驱动手 = "会自己'包'住东西的手套"，必懂）**：
- 普通手 = 每个关节一个电机，**你指挥每个关节怎么弯**。
- 欠驱动手 = "**一根线拉，所有指节自动弯，碰到东西就'顺势包住'**"——**不用指挥每个关节，物体形状自己'告诉'手指怎么弯**。
- **优点**：皮实、便宜、抓不规则物体好（enveloping grasp）。**缺点**：不通用——**扣扣子这种精细活干不了**。

### 3.4 对应 8.3.4：其他 end effectors（Other end effectors）

> 不是所有 end effectors 需要像灵巧或简化人手那样操作。许多工业应用这些天用 **vacuum grippers**（也叫 **suction-cup grippers**）做某种形式 pick and place manipulation。suction cups 在许多但非所有物体上工作极好。有些物体太软或多孔无法有效吸住。有些物体太脆弱或太重无法从真空在物体顶部提起，必须从下面支撑。有些手在手掌有吸力实现初始 pick，但仍用更传统手指稳定 grasp。

> 有许多其他巧妙夹爪技术。我最喜欢之一是 **jamming gripper**。这些夹爪由装满咖啡渣或其他颗粒介质的气球制成；把气球压到物体周围让颗粒介质流过物体，但对气球施加真空让颗粒介质"**jam**"，快速硬化围绕物体做稳定 grasp [11]。[视频：Cornell CCSL, Universal robotic gripper based on the...]

> 这是另一个巧妙设计，指尖有驱动滚轮帮助 in-hand reorientation。

> 最后，反对灵巧手的合理论点是即使人类常常不直接用手做最有趣 manipulation，而是**通过工具**。我特别喜欢 **Matt Mason**（多年来简单夹爪主要倡导者之一）在我们一次机器人研讨会结束时对一个问题的回答：他认为厨房里有用的机器人可能有**可快速更换的专用工具**。在灵巧手主要工作是换工具的应用中，我们可能通过直接在机器人上安装"**tool changer**"并使用 tool-changer-compatible 工具跳过复杂性。

**类比（jamming gripper = "装满咖啡豆的气球"，必懂）**：把气球按在物体上，咖啡豆流过去包住物体，**一抽真空，咖啡豆冻成硬块，把物体'焊'住**——**什么形状都能抓**！**Matt Mason 的观点**更妙：**与其造万能手，不如给机器人一个'快换工具接口'，像换螺丝刀头一样换专用工具**——**人类干活也是这么干的**。

### 3.5 对应 8.3.5：If you haven't seen it...

> 有一次我参加一个活动，注册表问我们"你最喜欢的机器人是什么，真实或虚构"。这对爱机器人的人是难题！但我给的答案是 **Ishikawa 组**的超酷"**high-speed multifingered hand**"；一个 2004 年开始产出惊人结果的项目！他们"**overclocked**"手——发送比任何更长应用合理的更多电流短时间——也用高速相机实现这些结果。他们也有魔方 demo，2017。[视频：Hizook, High-Speed Robot Hand] 太好了！

**类比（超频手 = "给手超频"，必懂）**：**短时间给电机灌超大电流**（会烧，所以只能短时），配合**高速相机**（看得够快才能控制得够快），实现**快到肉眼看不清的抓取/转魔方**。

---

## 4. 对应 8.4：传感器（SENSORS）

> 我还没说太多传感器。事实上，传感器将是我们的主要主题，当我们到带（深度）相机的感知，和当我们思考触觉传感。但我会推迟那些主题直到我们需要它们。

> 现在，让我们聚焦机器人上的**关节传感器**。iiwa 和 Schunk WSG 都提供关节反馈——iiwa 驱动给"**measured position**"、"**estimated velocity**"和"**measured torque**"在其七个关节每个；**记住关节加速度通常被认为太噪声而不可靠**。类似地 Schunk WSG 输出"**measured state**"（位置+速度）和"**measured force**"。我们可以使所有这些作为框图中的端口可用。

**类比（关节传感器 = "关节上的仪表盘"，必懂）**：
- iiwa 每个关节告诉你：**位置（测的，准）、速度（估的）、扭矩（测的）**。
- **加速度为什么不给**？因为加速度是"位置微分两次"，**噪声被放大两次**，**太脏不可靠**——**和第6章/第10章讲的一致**。
- Schunk 夹爪给：**位置+速度、夹持力**。

---

## 5. 对应 8.5：把它们全装起来（PUTTING IT ALL TOGETHER）

> 若你做过这些例子，你已看到机器人的正确仿真不止是物理引擎——它需要组装物理、执行器和传感器模型、低层机器人控制器到共同框架。实践中，在 Drake 中，那意味着我们组装越来越复杂的框图。

### 5.1 对应 8.5.1：HardwareStation

> 框图建模范式最好的事情之一是**抽象和封装的力量**。我们可以组装包含仿真我们硬件平台及其环境所需所有组件的 Diagram，我们将亲切称为"**Hardware Station**"。**MakeHardwareStation** 方法接受场景和机器人硬件的 YAML 描述。对描述 iiwa+WSG 和一些相机的 yaml 文件，结果 HardwareStation 系统看起来像这样：

```
iiwa.position (optional when not in position_only mode) ─┐
iiwa.torque (optional when not in torque_only mode) ─────┤
wsg.position ────────────────────────────────────────────┤→ HardwareStation
wsg.force_limit (optional) ──────────────────────────────┘
   → iiwa.position_commanded / position_measured / velocity_estimated / state_estimated
   → iiwa.torque_commanded / torque_measured / torque_external
   → wsg.state_measured / force_measured
   → camera_[NAME].rgb_image / depth_image / label_image  (×多个相机)
   → query_object / contact_results / plant_continuous_state / body_poses
```

> 上面框图中标**橙色**的输出端口是"**cheat ports**"——它们在仿真中可用，但运行真实机器人时不可用（因为它们假设 ground-truth 知识）。

**类比（HardwareStation = "把整台机器打包成一个黑盒"，必懂）**：
- **HardwareStation** = 把"物理 + 几何 + 低层控制器 + 相机"**全打包成一个黑盒**，对外只露一堆插口。
- **cheat ports（橙色）** = "**上帝视角插口**"：仿真里能直接读"物体真实位置"，**真机读不到**（真机只有相机图像）。**用它们调试可以，但别依赖它们做算法**，否则上真机就废。

**Example 8.6（Hardware station in the teleop demo）**：第一章 teleop notebook 用 MakeHardwareStation 接口设置仿真。现在你对那个子系统内部发生什么有更好感觉！

**Example 8.7（A bimanual manipulation station）**：通过向 YAML 文件加几行，我们可以用相同 MakeHardwareStation 方法构造**双臂站**。若有其他你想仿真的机器人/驱动，你可以直接在 manipulation 仓库的 station.py 文件做本地修改，或只问我，我可能能快速加它们。

### 5.2 对应 8.5.2：HardwareStationInterface

> 如你在例子中所见，HardwareStation diagram 本身旨在作为额外 diagrams 中的 System 使用，可包括我们的感知、规划和更高层控制系统。这个模型也定义**仿真和真实硬件之间的抽象**。通过简单传 `hardware=True` 进 MakeHardwareStation 方法，我们反而构造几乎相同系统，**HardwareStationInterface**。

```
iiwa.position ─────────────┐
iiwa.feedforward_torque ───┤
wsg.position ──────────────┤→ HardwareStationInterface
wsg.force_limit (optional) ┘
   → iiwa.position_commanded / position_measured / velocity_estimated
   → iiwa.torque_commanded / torque_measured / torque_external
   → wsg.state_measured / force_measured
   → camera_[NAME].rgb_image / depth_image  (×多个相机)
```

> HardwareStationInterface 也是 diagram，但而非由像 MultibodyPlant 和 SceneGraph 的仿真组件组成，它由**执行网络消息传递**以与和各个硬件驱动对话的小可执行文件接口的系统组成。若你深挖，会看到我们用 **LCM** 而非 ROS 消息做这个，主要因为 LCM 对我们公共仓库是更轻量依赖（也因为 **multicast UDP 对驱动层接口是比 TCP/IP 更好选择**）。但许多 Drake 开发者/用户在 ROS/ROS2 生态中用 Drake。

> 若你确实有自己的类似机器人硬件可用，想在你的机器上运行硬件接口，我已在附录开始整理驱动和物料清单列表。

**类比（仿真 vs 真机 = "同一台机器的两种皮肤"，必懂）**：
- `hardware=False` → 里面是**仿真组件**（MultibodyPlant 等），还带 cheat ports。
- `hardware=True` → 里面换成**网络通信组件**（LCM 消息），和真机驱动对话，**没有 cheat ports**。
- **外面看，插口几乎一样**——**所以你的控制/感知/规划代码不用改**，**换个参数就从仿真切到真机**。**这是 Drake 设计的精髓**。
- **为什么 LCM 不用 ROS**？LCM 更轻（公共仓库依赖少），且 **multicast UDP 比 TCP 更适合驱动层**（低延迟、不阻塞）。

### 5.3 对应 8.5.3：HardwareStation stand-alone simulation

> 用 HardwareStation 工作流，从仿真开发过渡到真实机器人运行很容易。一个额外工具支持这个工作流是 **stand-alone hardware_sim 可执行文件**。这个 python 脚本接受和输入相同的 YAML 文件（通过命令行），并在**单独进程**启动仿真，行为就像真实机器人硬件应该的……发送和接收硬件侧消息。这可有价值地用于测试你所有逻辑在消息传递层加一些延迟和非确定性时仍工作，而我们在开发初期用 `MakeHardwareStation(..., hardware=False)` 时巧妙避免了这些。

```bash
python3 drake/examples/hardware_sim/hardware_sim.py --scenario_file=station.yaml --scenario_name=Name
```

**类比（stand-alone sim = "用仿真假扮真机，测试'网线'会不会卡"，必懂）**：直接 `hardware=False` 时，仿真组件之间是"内存直连"，**没有网络延迟/丢包**——太理想。`hardware_sim` 把仿真**放在单独进程，走真正的消息传递**，**模拟真机的网络延迟/抖动**——**让你在上真机前，先测"我的代码扛不扛得住网络卡顿"**。

### 5.4 对应 8.6：更多 HardwareStation 例子

> 我喜欢学生为这门课组装的项目。为帮助实现那些项目（和你未来项目，我希望），我将在这里收集一些为不同硬件配置设置 HardwareStation 的更多例子。期望这个列表随时间增长！

**Example 8.8（The iiwa with an Allegro hand）**：这里是仿真 iiwa 附带 Allegro 手而非 Schunk WSG 夹爪的简单例子。（注意 Allegro 手有左手和右手版本可用。）

### 🧪 代码 4：HardwareStation + 探查端口 + 直接关节 teleop 骨架（对应 Example 8.6/8.7 + Exercise 8.2/8.3）

```python
from pydrake.all import (MakeHardwareStation, Simulator, StartMeshcat,
                         DiagramBuilder, LeafSystem, BasicVector)
import yaml

# --- Example 8.6/8.7: 用 YAML 一键搭 HardwareStation ---
scenario_yaml = """
plant_config: {time_step: 0.001}
model_directives:
  - add_model: {name: iiwa, model_package: package://drake/manipulation/models/iiwa_description}
  - add_weld: {parent: world, child: iiwa::iiwa_link_0}
  - add_model: {name: wsg, model_package: package://drake/manipulation/models/wsg_50_description/sdf}
  - add_weld: {parent: iiwa::iiwa_link_7, child: wsg::body}
cameras: {camera0: {X_PB: {translation: [1,0,1]}, width: 640, height: 480}}
"""
scenario = yaml.safe_load(scenario_yaml)
station = MakeHardwareStation(scenario, hardware=False)   # hardware=True 即切真机(8.5.2)
# meshcat = StartMeshcat(); ... 可视化 ...

# --- Exercise 8.2: 探查端口 ---
print("输入端口:"); [print("  ", i, station.get_input_port(i).get_name()) for i in range(station.num_input_ports())]
print("输出端口:"); [print("  ", i, station.get_output_port(i).get_name()) for i in range(station.num_output_ports())]
# 评估某端口: val = station.GetOutputPort("iiwa.position_measured").Eval(ctx)

# --- Exercise 8.3: 直接关节 teleop (替换第1章末端 teleop) ---
# 第1章 teleop 控制末端位姿; 这里换成直接给关节位置:
# 把 slider 输出连到 station 的 "iiwa.position" 输入端口即可直接控关节
```

**人话**：**`MakeHardwareStation` 用 YAML 一键搭整台机器**；**`hardware=True` 切真机**；**Exercise 8.2 探查端口**（看每个插口叫啥、读它的值）；**Exercise 8.3 把第1章"控末端"的 teleop 换成"直接控关节"**（把滑块连到 `iiwa.position` 端口）。

---

## 6. 对应 8.7：练习（EXERCISES）

**Exercise 8.1（Role of Reflected Inertia）**：调查反射惯量对机器人关节空间动力学的影响，以及它如何影响简单位置控制律。专门在 notebook 工作。步骤：
a. 推导带电机和齿轮箱的简单摆的一阶状态空间动力学。
b. 比较直接驱动简单摆和带高齿轮比齿轮箱的简单摆在相同位置控制律下的行为。
**→ 见代码 1**（已实现 b 的对比；a 的推导见 2.3 旁白的正确推导，一阶状态空间即令状态 $=[q,\dot q]$，$\dot q$ 方程用 $(I_{motor}+I_{arm}/n^2)\ddot q_{motor}=\tau_{gravity}/n+\tau_{motor}$ 写）。

**Exercise 8.2（Input and Output Ports on the Manipulation Station）**：调查 manipulation station 如何在 Drake 系统级框架中抽象。步骤：
a. 学习如何探查 manipulation station 的输入输出端口并评估它们的内容。
b. 通过探查它们的值探索不同端口对应什么。
**→ 见代码 4**（探查端口部分）。

**Exercise 8.3（Direct Joint Teleop in Drake）**：在 Drake 中实现控制机器人关节的方法。用第1章 example notebook 作参考。步骤：
a. 用允许直接控制机器人关节的不同 Drake 函数替换第1章例子中的 teleop 接口。
**→ 见代码 4**（直接关节 teleop 部分）。

**Exercise 8.4（PID Control in Drake）**：在机器人关节实现 PID 控制器。步骤：
a. 为机器人关节实现 PD 控制器。
b. 扩展 PD 控制器到完整 PID 控制器。
**→ 见代码 2**（PD 去掉积分项，PID 加积分状态和 $k_i$ 项）。

---

# 第二部分：逐条对照 PDF 核查 + 通俗性增补 + 代码实践增补

## 核查清单（逐项打勾）

| PDF 元素 | 覆盖 | 处理 |
|---|---|---|
| 引言：前面开发感知规划运动学/执行需更精细/微分IK让机器人折叠/引入接触力控制/非抓取操作(推椅子/滑动环境接触)/补力的思考/翻盒子 | ✅ | §0.2 |
| 8.1 TOOLBOX：稍高层命令转电机命令/本身不足以完成任务只推理机器人/提供高层抽象/低层在固件/仿真需自己实现/Drake 若干实现/四框图(PidController/InverseDynamicsController/SpatialForceController/SpatialStiffnessController 各自输入输出) | ✅ | §1.1 |
| 8.2 point mass：对抗复杂先简单/box-flipping/限2D/完整夹爪或point finger/小球两控制输入/Figure 8.4/两个动力学模型(完整5dof仿真/控制器2dof未建模接触力)/方程 m v̇=[0;-mg]+u+Fc/空间力记号 Fname_Bp_C/Drake带括号冗长/名字可选/expressed-in默认world/力推荐含body B/代码 Fname_Bp_C | ✅ | §2.1-2.2 |
| 8.2.1 Trajectory tracking：接触前先空中移动/期望轨迹qd(t)/PID τ=kp(qd-q)+kd(q̇d-q̇)+ki∫/增益宝库不复述/仿真真机不同增益/传动+PWM电压非电流/sim-to-real/神经网络建模传动旁白[1]/reflected inertia旁白/PID常数非增益调度惊讶/电机高速高效/齿轮减速100:1/q_motor=nq等四式/I_arm q̈=τ_gravity+τ/摆 ml²q̈=-mgl sinq+τ/电机坐标方程(OCR误,已纠正)/除n+电机惯量/(I_motor+I_arm/n²)q̈_motor=τ_gravity/n+τ_motor/反射惯量定义/臂处反射被n²削减or电机处被n²放大/多连杆I_arm状态依赖耦合/I_motor常数局部/大n时I_motor主导两效应(对角化+工作空间常数)/独立常数增益各构型好 | ✅ | §2.3 + 代码1 |
| 8.2.2 Torque-controlled：几种实现/小减速10:1摩擦忽略/direct-drive[2]巨大电机有限负载/Barrett WAM cable drives大电机基座/outrunner frameless quasi-direct-drive MIT Cheetah[3] Berkeley Blue Halodi Eve/液压 Sarcos BD中央泵阀压差≈力/大齿轮比加传感器测关节侧扭矩 iiwa应变片/刚度vs精度tradeoff[4]/Flex Spline 5000Nm/rad[5]/Gill Pratt SEA测两侧位置估扭矩[6]/Baxter Sawyer SEA/HEBI 100Nm/rad/iiwa弹性低层显式考虑[7]/力控制章 | ✅ | §2.4 |
| 8.2.3 proliferation：xArm疫情家用/需求成本降/对比腿式机加工车间研究生教授/专业高质量高uptime享受/跨实验室可重复共享/价格降更多机器人/乐观/好时候 | ✅ | §2.5 |
| 8.2.4 Simulating iiwa：URDF/SDF/Drake随附iiwa/网上模型质量wildly不同/运动学错误/动力学不准/数学不一致惯性矩阵/Drake抱怨/早提醒/CAD Solidworks导出/导入物理引擎MultibodyPlant/plant词源化工厂/与控制理论兼容/类接口方法库质心Jacobian/System输入输出端口/组装框图/MultibodyPlant框图(输入4输出多)/大多可选/Example 8.2 passive iiwa/可视化2D3D/SceneGraph/SceneGraph框图/Example 8.3 visualizing/为何MBP不处理几何/自动驾驶简单车模/underactuated简单模型/iiwa基本仿真微妙/零扭矩倒下/现实从不/机械刹车控制器关啮合/仿真需告诉刹车扭矩/控制器开也不发零扭矩/feedforward torque加额外/低层补偿重力传动/沮丧但不想陷驱动细节/最简单合理仿真必含Kuka低层/joint impedance mode/Example 8.4加低层控制器设期望位置=当前状态/更忠实/又无聊/最后注记运动学仿真overkill同意/棘手让运动学仿真尊重交互规则/知物体何时捡起[8]/Drake主要完整物理引擎/简单模型做规划控制 | ✅ | §2.6 + 代码3 |
| 8.3 HANDS：iiwa无手/安装板end-effector/访问端口/另一决定用什么手/Example 8.5 Robot hands/相同接口/研究者分阵营 | ✅ | §3 |
| 8.3.1 Dexterous：Figure 8.3 Shadow Allegro/迷恋人手/没到那/追求梦想挣扎复杂鲁棒/OpenAI learning dexterity Shadow魔方/耐力学习投入/FLLEX v2[9]/乐观 | ✅ | §3.1 |
| 8.3.2 Simple grippers：PR1视频扫地拿啤酒卸洗碗机/另一阵营灵巧不必要玩具店夹爪/PR1演示/减少复杂优雅清晰/简单两指Schunk WSG 050/简单≠低质量/SGW力控力测超Kuka保真/多关节灵巧难 | ✅ | §3.2 |
| 8.3.3 Soft/underactuated：第三最新阵营巧妙机械设计underactuated hands/不需执行器=关节/cable-drive单肌腱多关节弯/被动顺应[10]/刚性连杆也行/Figure 8.5 Reflex2 i-HY Robotiq三指/Figure 8.6 Robotiq连杆顺应/极端完全软/soft robotics附肢执行器传感器电源全软/耐用成本安全/Figure 8.7哈佛软手RBO Hand2/减少负担极好例子/enveloping grasps好但不通用/难扣衬衫/越来越灵巧RBO视频 | ✅ | §3.3 |
| 8.3.4 Other end effectors：vacuum suction-cup grippers pick place/许多非所有/太软多孔/太脆弱重从下支撑/手掌吸力初始pick+传统手指稳定/jamming gripper咖啡渣气球真空jam硬化[11]/Cornell视频/驱动滚轮in-hand reorientation/反对灵巧=人类用工具/Matt Mason厨房快换专用工具/tool changer跳过复杂 | ✅ | §3.4 |
| 8.3.5 high-speed：活动最喜欢机器人/Ishikawa high-speed multifingered hand 2004/overclocked更多电流短时间/高速相机/魔方demo2017/Hizook视频/太好了 | ✅ | §3.5 |
| 8.4 SENSORS：没说太多/主要主题推迟/现在聚焦关节传感器/iiwa measured position estimated velocity measured torque七关节/关节加速度太噪声不可靠/Schunk measured state+measured force/作框图端口 | ✅ | §4 |
| 8.5 PUTTING TOGETHER：正确仿真不止物理引擎/组装物理执行器传感器低层控制器/Drake组装复杂框图 | ✅ | §5 |
| 8.5.1 HardwareStation：抽象封装力量/组装Diagram含所有组件/MakeHardwareStation接受YAML/iiwa+WSG+相机yaml/HardwareStation框图(输入4输出多)/橙色cheat ports仿真可用真机不可(ground-truth)/Example 8.6 teleop demo/Example 8.7 bimanual加几行YAML/其他机器人station.py本地修改或问 | ✅ | §5.1 + 代码4 |
| 8.5.2 HardwareStationInterface：HardwareStation作额外diagrams的System/含感知规划高层/定义仿真真机抽象/hardware=True构造HardwareStationInterface/HardwareStationInterface框图/网络消息传递小可执行文件/LCM非ROS轻量+multicast UDP比TCP好/ROS ROS2生态/附录驱动物料清单 | ✅ | §5.2 |
| 8.5.3 stand-alone sim：过渡真机容易/hardware_sim可执行文件/python脚本同YAML命令行/单独进程仿真像真机/测试消息层延迟非确定性/开发初期hardware=False避免/命令行 | ✅ | §5.3 |
| 8.6 MORE EXAMPLES：学生项目/收集更多例子/列表增长/Example 8.8 iiwa Allegro hand(左右手版本) | ✅ | §5.4 |
| 8.7 EXERCISES 8.1 reflected inertia a,b / 8.2 ports a,b / 8.3 direct joint teleop a / 8.4 PID a,b | ✅ | §6 + 代码1,2,4 |
| REFERENCES 1-11 | ✅ | 各处 |
| Figure 8.3-8.7 + 所有框图 | ✅ | 对应小节 |

**核查结论**：PDF 全部小节（8.1–8.7 含 8.2.1–8.2.4、8.3.1–8.3.5、8.5.1–8.5.3）、全部 Example（8.2–8.8）、全部框图（4 控制器、MultibodyPlant、SceneGraph、HardwareStation、HardwareStationInterface）、全部练习（8.1–8.4）、全部 11 篇参考文献均已覆盖。**reflected inertia 推导 PDF 中间一行 OCR 有误，已给正确推导（关节坐标 $(I_{arm}+n^2I_{motor})\ddot q=\tau_{gravity}+n\tau_{motor}$，电机坐标即 PDF 最终式）并诚实标注**。**PDF 这一章几乎无内联代码，已补 4 段代码**（反射惯量仿真、PID、MultibodyPlant 仿真、HardwareStation+探查+teleop）。

## 增补一：把"还不够通俗"的 5 个点再各加一个类比

1. **为什么"关节加速度太噪声"**？加速度 = 位置微分两次，**每次微分把测量噪声放大**，两次后噪声可能比信号还大——**和第6章/第10章"数值微分噪声"一致**。所以 iiwa 只给"estimated velocity"（估一次，已经够噪），**干脆不给加速度**。
2. **cheat ports 为什么危险**？仿真里你能直接读"杯子真实坐标"，算法可能**偷懒直接用**，上真机没这个端口就**立刻瞎**。**所以调试可以用，但算法逻辑绝不能依赖**——**就像考试能用答案，但平时练习不能抄**。
3. **为什么 LCM 用 multicast UDP 不用 TCP**？驱动层要**低延迟、一对多广播**（一个传感器数据发给多个订阅者），**UDP 广播快、不阻塞**；**TCP 要握手、保证送达，慢**——**驱动层宁可丢一帧旧的，也不要等**。
4. **为什么"运动学仿真"判断不了"抓没抓住"**？运动学只管"几何位置"，**不管力**——**它不知道手指夹住盒子后盒子会跟着动**（那需要力/接触模型）。**所以"抓没抓住"必须靠完整物理引擎**。
5. **jamming gripper 为什么"什么形状都能抓"**？颗粒介质（咖啡渣）**能流动**，所以**能贴合任何形状**；**一抽真空颗粒锁死**，**就把任意形状"焊"住**——**不需要事先知道物体形状**，**这是它比灵巧手"通用"的地方**（灵巧手要靠感知+规划去适应形状）。

## 增补二：代码实践集中说明

这一章 PDF 几乎没有内联代码（除 hardware_sim 命令行和框图），Example 全指向 notebook。我补的 4 段代码定位：

| 代码 | 对应 | 能跑？ | 演示什么 |
|---|---|---|---|
| 代码 1 | 8.2.1 旁白 / Exercise 8.1 | ✅ numpy | 反射惯量：高齿轮比下加负载响应不变 |
| 代码 2 | 8.2.1 / Exercise 8.4 | numpy + Drake 骨架 | PID 内部（PD→加积分） |
| 代码 3 | Example 8.2/8.3/8.4 | Drake 骨架 | MultibodyPlant+SceneGraph 仿真 iiwa |
| 代码 4 | Example 8.6/8.7 + Exercise 8.2/8.3 | Drake 骨架 | HardwareStation+探查端口+直接关节 teleop |

**上手顺序**：**代码 1**（反射惯量，本章唯一硬物理，先懂"为什么常数增益好使"）→ **代码 2**（PID 内部，懂"为什么仿真真机增益不同"）→ **代码 3**（搭 iiwa 仿真，懂"零扭矩会瘫、要加低层控制器"）→ **代码 4**（HardwareStation 一键搭+探查端口+teleop，懂"仿真真机同一套代码"）。

**诚实提醒**：代码 3、4 依赖 Drake 模型包路径和版本，**端口名/包路径可能微调**；**核心结构（`AddMultibodyPlantSceneGraph`、`MakeHardwareStation`、`get_input_port`）稳定**。**代码 1、2 的 numpy 部分完全自包含可直接跑**。

---

## 知识地图：第 8 章在全书的位置

```
前面章节: 感知(看物体) + 规划(想怎么动) + 运动学(关节↔末端)
        │  但"想好了"和"电机真动"之间隔着一层肌肉+接触
        ▼
第8章 Manipulator Control = 低层控制 + 接触力 + 硬件仿真
   8.1 四种翻译官: PidController / InverseDynamics / SpatialForce / SpatialStiffness
   8.2 先简化成质点(box-flipping): 完整模型(仿真5dof) vs 控制器模型(2dof+未知Fc)
        8.2.1 PID跟踪 + 反射惯量(齿轮把对面重量缩放n²->常数增益处处好使)
        8.2.2 扭矩控制四路线: 直驱/cable/液压/应变片iiwa+SEA
        8.2.3 硬件激增(xArm, 可重复共享)
        8.2.4 仿真iiwa: MultibodyPlant+SceneGraph; 零扭矩会瘫(真机有刹车+低层)
   8.3 手三阵营: 灵巧(Shadow/Allegro) / 简单(Schunk WSG) / 软欠驱动(Reflex/Robotiq/软手)
        + 吸盘/jamming/tool changer(Matt Mason)
   8.4 关节传感器: 位置(测)速度(估)扭矩(测), 加速度太噪不给
   8.5 全装起来: HardwareStation(YAML一键, cheat ports) / HardwareStationInterface(hardware=True切真机, LCM)
        / hardware_sim(测消息层延迟)
        │
        ▼
   呼应: 第3章微分IK(本章低层执行它) / 第6章bin picking(本章补力) / 第9章感知(相机触觉推迟)
        第13章力控制(串联弹性/阻抗控制细节)
```

**和前后章的呼应**：
- **第3章微分逆运动学** = 本章低层控制器**执行**它；本章还补了"它有时让机器人折叠"的坑的解药（考虑关节角/力）。
- **第6章 bin picking** = 本章补上它缺的"力"的思考。
- **第9章感知** = 相机/触觉**推迟**到那里；本章只聚焦关节传感器。
- **第13章力控制** = 串联弹性/阻抗控制的**细节**在那里展开。

---

## 给初学者的"本章通关三句话"

1. **本章补的是"想好了"和"电机真动"之间那层肌肉**：Drake 提供四种低层控制器（PID / 逆动力学 / 空间力 / 空间刚度），各吃不同输入（期望位置/加速度/力/刚度），把高层命令翻译成电机电流；它们本身不管环境物体，只提供抽象。
2. **仿真和真机之间有道鸿沟，反射惯量是钥匙**：真 iiwa 发零扭矩也不瘫（有刹车+低层补偿重力），仿真必须把低层控制器建进去才忠实；而"为什么每个关节用同一套常数 PID 增益在所有姿势都好使"的秘密是**反射惯量**——齿轮比 $n$ 把电机惯量反射到关节侧放大 $n^2$，压没了"姿态/负载带来的变化"，于是方程近似对角、处处差不多。
3. **手分三阵营，仿真靠 HardwareStation 一键切真机**：灵巧手（天花板高但娇贵）、简单夹爪（简单≠劣质，Schunk 力测超 Kuka）、软/欠驱动手（被动顺应、皮实，jamming 什么形状都能抓）；而 `MakeHardwareStation` 用 YAML 把"物理+几何+低层+相机"打包成黑盒，`hardware=True` 就切真机（LCM 消息），cheat ports 调试可用但算法绝不能依赖。

> 最后送你一句动手箴言：这一章 PDF 几乎没内联代码，但**所有"坑"都会在你跑通那 4 段代码后变成"显然"**。**尤其代码 1（看高齿轮比下加负载响应不变，懂反射惯量）、代码 3（看零扭矩 iiwa 瘫倒、加低层控制器才站住，懂仿真真机的鸿沟）、代码 4（用 YAML 一键搭 HardwareStation、`hardware=True` 切真机，懂"同一套代码两种皮肤"）这三段**——做完它们，"PID/反射惯量/串联弹性/HardwareStation/cheat ports"这些最像黑话的词，就会像骑自行车一样长进肌肉记忆。**这一章的精髓不是某个公式，而是那个"从想好到做到"的诚实——大脑想得再美，手也得靠齿轮、摩擦、刹车、接触力去执行；而仿真与真实之间的鸿沟，正是由这些"不完美"填出来的。反射惯量告诉我们"不完美有时反而是恩赐"（让常数增益好使），cheat ports 告诉我们"仿真给的便利别贪"，HardwareStation 告诉我们"把不完美封装好，仿真和真机就能用同一套代码"——于是机器人从"脑子里的完美轨迹"，真正落地成"在真实世界里，带着齿轮的咔哒和接触的反弹，稳稳抓起那个盒子"。** 🦾⚙️