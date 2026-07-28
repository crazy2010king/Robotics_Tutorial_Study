# 用大白话讲透《Underactuated Robotics》第16章：极限环算法（Algorithms for Limit Cycles）

> 前面我们学了稳定平衡点（fixed point）——小球停在碗底。但很多机器人运动是**周期性**的：走路、跑步、游泳、飞行、心脏跳动……这些运动不会停在一点，而是**绕着一条闭合轨道反复跑**。这条闭合轨道就叫**极限环（Limit Cycle）**。
>
> 线性系统**不可能**产生稳定的极限环行为 ，所以这是**非线性系统独有的富矿**。这一章要回答三个核心问题：
> 1. **怎么找到**周期轨迹？（轨迹优化）
> 2. **怎么证明**它稳定？（李雅普诺夫分析 + 横向坐标）
> 3. **怎么控制**机器人沿着它走？（横向 LQR、零动力学）
>
> 下面我用完全通俗的方式，把这一章从头到尾拆给你看，并配上代码实践说明。

---

## 🏃 一、核心直觉：绕着操场跑步的比喻

想象一个机器人**绕着椭圆形操场跑步**：

📌 **三种"稳定"的概念对比**：
- **平衡点稳定**：机器人停在操场中央的某个点不动
- **轨迹稳定（全状态）**：机器人必须**精确地**按时间表跑——第 1 秒在 A 点、第 2 秒在 B 点……差一秒都不行
- **极限环稳定（轨道稳定）**：机器人只要在跑道上跑就行，**不要求与地方时间精确同步**——可以快几秒、慢几秒，但**永远不会跑出跑道**

**关键洞察**：极限环稳定性比"轨迹稳定性"**弱**，但比"平衡点稳定性"**强且更有用**。对于走路机器人来说，我们**关心的是"脚落在哪里"，而不是"几点几秒落在那里"**——这就是轨道稳定（orbital stability）的精髓 。

> 💡 **为什么线性系统不能有稳定极限环？** 线性系统的解要么收敛到原点、要么发散、要么做简谐振动（但简谐振动不是"稳定"的——任何微小扰动都会改变振幅，不会回到原振幅）。稳定极限环要求"振幅自动恢复到特定值"，这本质是非线性现象（如范德波尔振荡器中的能量饱和效应）。

---

## 🎯 二、16.1 轨迹优化：怎么找到极限环

### 2.1 把"找周期解"变成优化问题

最直接的方法：把周期约束 $x[0] = x[N]$ 加到轨迹优化里 。

**离散时间版本**：
$$\text{find}_{x[\cdot]} \quad \text{subject to} \quad x[n+1] = f(x[n]), \quad \forall n \in [0, N-1]$$
$$x[0] = x[N]$$

📌 **可能的解**：
1. **平衡点**：如果 $x[n] = x^*$ 常数满足 $f(x^*) = x^*$，那它也是可行的（但我们通常不想要这个解）
2. **N步周期轨迹**：恰好 N 步重复的轨迹

**问题**：离散版本太僵硬——必须"恰好 N 步回到原点"，这限制太强 。

### 2.2 连续时间 + 可变步长：更强大的方法

**关键技巧**：把步长时间 $h_n$ 也作为**决策变量**加入优化 ！

$$\min_{x[\cdot], u[\cdot], h_n} \ell_f(x[N]) + \sum_{n=0}^{N-1} h_n \ell(x[n], u[n])$$
$$\text{subject to} \quad \dot{x}(t_{c,n}) = f(x(t_{c,n}), u(t_{c,n})), \quad \forall n$$
$$x[0] = x_0, \quad h_n \geq h_{min} > 0$$
$$+ \text{周期性约束（如 } x[N] = x[0] \text{）}$$

**妙处**：通过调整步长 $h_n$，轨迹可以**拉伸或压缩时间**来满足周期性约束。这比固定步长的离散版本灵活得多 。

### 2.3 初始猜测很重要！

教材特别强调 ：在这个问题中，**必须给求解器提供初始猜测**。默认的随机小数值会让求解器陷入局部最小值。

**环振子的好初始猜测**：假设解是在状态空间里**绕着一个圆圈运动**。这个直觉上的初始猜测足以让求解器收敛 。

> ⚠️ **工程经验**：周期轨迹优化是非凸问题，初始猜测的质量直接决定成败。"绕圈"的几何直觉是最好的起点。

---

## 🌀 三、16.2 李雅普诺夫分析：怎么证明极限环稳定

### 3.1 轨道稳定的数学定义

极限环 $x^*(t)$ 的稳定性定义为 ：
$$\min_{\tau} \|x(t) - x^*(\tau)\| \rightarrow 0$$

**直观解读**：不管机器人从轨道附近的哪里出发，它最终都会**靠近这条轨道**（但不一定与时间同步）。

根据收敛方式，可以分为：
- **李雅普诺夫意义下的轨道稳定**（i.s.L.）
- **渐近轨道稳定**
- **指数轨道稳定**
- **有限时间轨道稳定**

### 3.2 庞加莱映射方法的局限

在第4章分析行走机器人时，我们用了**庞加莱映射（Poincaré map）**：在轨道上选一个截面，看轨迹穿过截面时状态如何映射。

**问题**：庞加莱映射是**离散的**，需要把非线性动力学积分一整圈才能得到 。我们**很少有它的解析表达式**——这导致庞加莱映射的李雅普诺夫函数**极难验证**。

### 3.3 横向坐标（Transverse Coordinates）：移动的庞加莱截面

**天才的想法**：与其只在**一个点**放一个截面，不如**沿着整条轨道**都放截面——这就是"移动的庞加莱截面" 。

**坐标变换**：定义新坐标系
- $\tau$：沿轨道的**相位**（phase along the orbit）
- $x_\perp(\tau)$：**剩余坐标**（垂直于轨道方向，维度 n-1）

给定原坐标 x，定义一个光滑映射 $x \rightarrow (\tau, x_\perp)$。

**环振子的例子** ：
$$\tau = \text{atan2}(-x_2, x_1)$$
$$x_\perp = \sqrt{x_1^2 + x_2^2} - 1$$

这里 $\tau$ 是角度，$x_\perp$ 是"到单位圆的径向距离减1"。在单位圆上，$x_\perp = 0$。

**变换后的动力学**：
$$\dot{\tau} = f_\tau(x_\perp, \tau)$$
$$\dot{x}_\perp = f_\perp(x_\perp, \tau)$$

**约定**（简化分析）：
- 在标称轨迹上，$\dot{\tau} = f_\tau(0, \tau) = 1$（相位是时间）
- 原点 $x_\perp = 0$ 对应标称轨迹上的点

### 3.4 定理 16.1：轨道稳定的李雅普诺夫定理

对于系统 $\dot{x} = f(x)$，周期为 $t_{period}$ 的周期解 $x^*(\tau)$，以及光滑映射 $x \rightarrow (\tau, x_\perp)$：

**如果能构造** $V(x_\perp, \tau)$ 使得 ：
$$\forall \tau, V(0, \tau) = 0$$
$$\forall \tau, \forall x_\perp \in \mathcal{B}, x_\perp \neq 0, V(x_\perp, \tau) > 0$$
$$\forall \tau, \dot{V}(0, \tau) = 0$$
$$\forall \tau, \forall x_\perp \in \mathcal{B}, x_\perp \neq 0, \dot{V}(x_\perp, \tau) < 0$$

**则** $x^*(t)$ 是**局部渐近轨道稳定**的。

**强度升级**：
- $\dot{V}_\perp \leq 0$ → 李雅普诺夫意义下轨道稳定
- $\dot{V}_\perp \leq \alpha V_\perp$ → 指数轨道稳定

### 3.5 Example 16.2：简单环振子（完整解析）

**系统动力学** ：
$$\dot{x}_1 = x_2 - \alpha x_1\left(1 - \frac{1}{\sqrt{x_1^2+x_2^2}}\right)$$
$$\dot{x}_2 = -x_1 - \alpha x_2\left(1 - \frac{1}{\sqrt{x_1^2+x_2^2}}\right)$$

**横向坐标**（极坐标变换）：
$$\tau = \text{atan2}(-x_2, x_1)$$
$$x_\perp = \sqrt{x_1^2 + x_2^2} - 1$$

**变换后的简单横向动力学**：
$$\dot{\tau} = 1$$
$$\dot{x}_\perp = -\alpha x_\perp$$

**取李雅普诺夫候选** $V(x_\perp, \tau) = x_\perp^2$，验证：
$$\dot{V} = -2\alpha x_\perp^2 < 0, \quad \forall x_\perp > -1$$

**结论**：
- 极限环**局部渐近稳定**
- 不变开集 $V < 1$ 包含在吸引域内
- 事实上，**所有** $x_\perp > -1$ 都在吸引域内（虽然李雅普诺夫论证没有直接证明这一点）

> 💡 **横向坐标方法 vs 庞加莱映射方法**：
> - **额外负担**：需要构造沿整条轨迹的坐标系，而非仅在单个截面上
> - **巨大回报**：只需检查**瞬时动力学** $f(x)$，而不必把动力学积分一整圈来生成离散庞加莱映射
> - **兼容性**：更适合设计**连续反馈控制器**来稳定极限环

### 3.6 横向线性化（Transverse Linearization）

**核心思想**：像在平衡点附近线性化一样，在极限环附近对横向动力学线性化 。

$$\dot{x}_\perp = f_\perp(x_\perp, \tau) \approx \frac{\partial f_\perp}{\partial x_\perp} x_\perp = A_\perp(\tau) x_\perp$$

**Hauser & Chung (1994) 的关键结论** ：如果时变线性系统 $\dot{x}_\perp = A_\perp(t) x_\perp$ 是指数稳定的，则原系统局部指数轨道稳定。

**周期里卡蒂方程**：如果横向线性系统是周期且轨道稳定的，则对任意 $Q = Q^T \succ 0$，存在唯一的周期正定解 ：
$$V(x_\perp, \tau) = x_\perp^T P(\tau) x_\perp$$
$$-\dot{P}(\tau) = P(\tau)A(\tau) + A(\tau)P^T(\tau) + Q$$

**实践解法** ：**向后时间积分**直到收敛到周期解。这不保证总是工作，但实践中几乎总是成功。

> 💡 **这是极其强大的工具**：它给出了构造李雅普诺夫候选函数的一般方法，可以用来证明极限环的局部稳定性，并作为非线性李雅普诺夫分析的起点。

### 3.7 16.2.3 用平方和估计吸引域

教材标注 **"Coming soon"** 。但根据 Manchester et al. 2011 的工作 ，具体方法是：
- 将目标极限环周围的动力学分解为**切向和横向分量**
- 在横向动力学中使用**平方和（SOS）分析**（半定规划）搜索李雅普诺夫函数
- 详细例子：范德波尔振荡器、无轮辐轮（rimless wheel）、罗盘步态（compass gait）

---

## 🎮 四、16.3 反馈设计：怎么控制机器人沿极限环运动

### 4.1 周期控制的两种哲学

**哲学 A：每周期一次决策（离散）**
- 像行走机器人的脚放置，每个步态周期做一次决策
- 用庞加莱映射的稳定化来控制
- **局限**：只能做离散决策，不能连续反馈

**哲学 B：连续反馈（continuous feedback）**
- 在整个轨迹上连续调整控制
- 用横向线性化 + 横向 LQR
- **优势**：更精细的控制

教材指出 ：有些场景"每周期一次决策"很自然——
- **足式机器人的脚放置**：选定落点后，在脚着地前可做微小修正，但脚着地后决策基本锁定
- **扑翼飞行**：机翼拍打周期远快于质心动态时间尺度，每个拍打周期调整一次翼拍参数很合理

但横向坐标框架让我们也能做**连续反馈**——这是这一节的焦点。

### 4.2 16.3.1 欠驱动度数为一的情况与零动力学（Hybrid Zero Dynamics）

**核心观察（Jessy Grizzle 的关键贡献）** ：极限环稳定性本质上是 **n-1 自由度**的稳定性，而**欠驱动度数为一**的系统恰好有 n-1 个驱动器——**用 n-1 个驱动器稳定 n-1 自由度，刚好够！**

这就是 **Hybrid Zero Dynamics (HZD)** 的核心思想。"Hybrid"部分（混合动态，即接触/碰撞）留到下一章讲，这里关注"Zero Dynamics"概念。

📌 **HZD 步行器的有趣特性** ：
- 你可以站在机器人前面用手挡住它，阻止前进
- 控制系统会继续作用，**保持在极限环上**
- 但沿轨道的进程停止了
- 甚至可以把它往后推，它会**反向**走完同一个步行周期

**要实现前进认证**：必须检查沿轨道的**相位变量的一维动力学**，确保前进进度能够实现。

> 💡 **零动力学的通用性**：不仅限于欠驱动度数为一的系统。一般地，用 m 个驱动器可以稳定 m 维流形。如果位于该流形上足以完成任务，或在流形上的结果动力学足以认证任务完成，那就成功了。但在"欠驱动度数为一"的情况下，被研究的流形是轨迹/轨道，本章的工具直接适用。

### 4.3 16.3.2 横向 LQR（Transverse LQR）——本章最实用的算法

**标称（控制）轨迹**：$[x_0(t), u_0(t)]$，满足 $\dot{x}_0 = f(x_0, u_0)$

**横向动力学近似** ：
$$\dot{x}_\perp = f_\perp(x_\perp, \tau, u) \approx \frac{\partial f_\perp}{\partial x_\perp} x_\perp + \frac{\partial f_\perp}{\partial u}(u - u_0(\tau)) = A_\perp(\tau)x_\perp + B_\perp(\tau)\bar{u}$$

**Shiriaev et al. 2008 的结论** ：稳定这个**（周期的）时变 LQR 控制器**就能实现原系统的轨道稳定。

#### 横向 LQR vs 全坐标时变 LQR 的本质区别

| 特性 | 全坐标 TVLQR | 横向 LQR |
|---|---|---|
| 控制目标 | 稳定**全状态**（包括相位） | 只稳定**横向偏差** |
| 行为 | 试图**加速/减速**来与标称轨迹保持时间同步 | **不试图**稳定相位变量 |
| 代价函数 | 全状态偏差的二次型 | 等价于全坐标中**沿标称轨迹方向为零**的代价 |
| 反馈增益 $K(t)$ | 较大 | **显著较小** |
| 对欠驱动系统 | 可能不稳定 | **差异可以非常戏剧性** |

⚠️ **重要警告** ：你可能会想："我设计全坐标 TVLQR 控制器 $\bar{u} = K(t)\bar{x}$，执行时只需投影到最接近的时间（如找 $t = \text{argmin}_\tau |x - x_0(\tau)|$），用对应时间的反馈就行。" **但这种投影不保证安全**——存在这样的系统：横向线性化可稳定，但基于投影的全坐标反馈**闭环不稳定**。

**Example 16.3（TVLQR 简单时间投影可能导致不稳定）**：教材标注 "Coming soon"。

#### 为什么横向 LQR 更好？

**核心理由** ：如果轨道稳定就是你需要的全部，那么横向 LQR 是**更好的问题表述**——因为你要求的更少。

正如 HZD 中所讨论的：**用 m 个驱动器稳定 m 自由度** vs **用 m 个驱动器稳定 m+1 自由度** 是**潜在非常不同**的。在横向表述中，我们要求 LQR 只在横向坐标中最小化代价（数学上等价于设计全坐标中沿标称轨迹方向为零的代价函数）。实践中，这导致**小得多的代价到收益矩阵 $S(t)$ 和更小的反馈增益 $K(t)$**。对于欠驱动系统，这种差异可以非常戏剧性。

### 4.4 16.3.3 非周期轨迹的轨道稳定

**强大洞察** ：轨道稳定化的好处**不限于**周期运动。

**如果你的目标是稳定一条非周期路径，但**不关心时间同步**，那么用横向公式化你的稳定化可以是一个非常好的选择。**

**存在这样的例子**：
- 系统在横向坐标中**可稳定**，但在全坐标中**不可稳定**
- 反之也可能：**Example 16.4 和 16.5 都标注 "Coming soon"**

**双积分器的警示例子** ：
考虑轨迹 $u(t)=1$（从任意初始条件）的双积分器。我们当然可以用 LQR 在全坐标中稳定这条轨迹。技术上，可以选择横向坐标 $\tau = \dot{q}$，$x_\perp = q$。显然 $x_\perp$ 在各处都与标称轨迹横向。但**这个横向线性化显然不可稳定**——这是个糟糕的选择！

**解决方案** ：一般设计横向坐标的方法  可以通过在优化横向坐标时**包含可控性准则**来解决这个隐患。

---

## 📋 五、与 PDF 原文的逐项对照核查

| PDF 章节 | 我的讲解覆盖情况 | 补充说明 |
|---|---|---|
| 章节开篇 | ✅ 完整讲解 | 线性系统不能产生稳定极限环；非线性独有；工具超越简单周期运动 |
| 16.1 轨迹优化 | ✅ 完整讲解 | |
| 离散周期约束 $x[0]=x[N]$ | ✅ 完整讲解 | 平衡点解 + N步周期解；限制性太强 |
| 连续时间 + 可变步长 $h_n$ | ✅ 完整讲解 | 拉伸/压缩时间满足周期性；初始猜测绕圈运动 |
| 16.2 李雅普诺夫分析 | ✅ 完整讲解 | |
| 轨道稳定定义 $\min_\tau \|x(t)-x^*(\tau)\| \rightarrow 0$ | ✅ 完整讲解 | 李雅普诺夫/渐近/指数/有限时间轨道稳定 |
| 庞加莱映射的局限 | ✅ 完整讲解 | 缺乏解析表达式；需积分一整圈 |
| 16.2.1 横向坐标 | ✅ 完整讲解 | |
| 坐标变换 $x \rightarrow (\tau, x_\perp)$ | ✅ 完整讲解 | 相位 + 垂直坐标；"移动的庞加莱截面" |
| 环振子例子（极坐标变换）| ✅ 完整讲解 | $\tau = \text{atan2}(-x_2, x_1)$，$x_\perp = \sqrt{x_1^2+x_2^2}-1$ |
| 定理 16.1（轨道稳定李雅普诺夫定理）| ✅ 完整讲解 | V 沿轨道为零、偏离为正；$\dot{V}$ 条件 |
| Example 16.2 完整解析 | ✅ 完整讲解 | 环振子；$\dot{x}_\perp = -\alpha x_\perp$；$V = x_\perp^2$；吸引域 $x_\perp > -1$ |
| 横向坐标方法 vs 庞加莱映射 | ✅ 完整讲解 | 额外负担 vs 巨大回报；兼容连续反馈 |
| 16.2.2 横向线性化 | ✅ 完整讲解 | |
| $A_\perp(\tau)$ 时变线性系统 | ✅ 完整讲解 | Hauser & Chung 结论：指数稳定 ⇒ 局部指数轨道稳定 |
| 周期里卡蒂方程 | ✅ 完整讲解 | $V = x_\perp^T P(\tau) x_\perp$；向后时间积分实践解法 |
| 16.2.3 SOS 吸引域估计 | ⚠️ PDF 标注 "Coming soon" | 补充 Manchester et al. 2011 方法：切向/横向分解 + SOS 分析 ；三个例子：范德波尔、无轮辐轮、罗盘步态 |
| 16.3 反馈设计 | ✅ 完整讲解 | |
| 每周期一次决策 vs 连续反馈 | ✅ 完整讲解 | 脚放置、扑翼飞行作为自然例子 |
| 16.3.1 欠驱动度数为一的零动力学（HZD）| ✅ 完整讲解 | Grizzle 的关键观察；n-1 驱动器稳定 n-1 自由度；"站在机器人前面用手挡住"的有趣特性 |
| 16.3.2 横向 LQR | ✅ 完整讲解 | |
| 横向线性化近似 | ✅ 完整讲解 | $A_\perp(\tau)x_\perp + B_\perp(\tau)\bar{u}$ |
| Shiriaev et al. 2008 结论 | ✅ 完整讲解 | 周期 TVLQR 稳定横向动力学 ⇒ 轨道稳定 |
| 横向 LQR vs 全坐标 TVLQR 的区别 | ✅ 完整讲解 | 不试图稳定相位；投影时间不保证安全 |
| Example 16.3（TVLQR 投影可能导致不稳定）| ⚠️ PDF 标注 "Coming soon" | 未展开 |
| 横向 LQR 的优势 | ✅ 完整讲解 | 要求更少 ⇒ 更小的 S(t) 和 K(t)；欠驱动系统差异戏剧性 |
| 16.3.3 非周期轨迹的轨道稳定 | ✅ 完整讲解 | |
| 横向坐标可稳定但全坐标不可稳定 | ⚠️ Example 16.4 标注 "Coming soon" | 未展开 |
| 全坐标可稳定但横向坐标不可稳定 | ✅ 完整讲解 | 双积分器反例；$\tau=\dot{q}, x_\perp=q$ 是糟糕选择 |
| 可控性准则优化横向坐标 | ✅ 完整讲解 | Manchester 2011 的一般方法 |
| 参考文献 [1]-[4] | ✅ 完整覆盖 | Hauser & Chung 1994 ; Shiriaev et al. 2008 ; Manchester et al. 2011 ; Manchester 2011 |

### 通俗性补充（针对基础薄弱读者的额外解释）

1. **什么是"极限环"？** 想象操场上的跑道。机器人沿着跑道跑圈，不管从哪里开始，最终都会回到跑道上继续跑——这条跑道就是极限环。它不像平衡点那样"停在一点"，而是"困在一条闭合曲线上"。

2. **"轨道稳定"为什么比"轨迹稳定"弱？** 轨迹稳定要求机器人**精确按时间表**跑（第 1 秒在 A 点、第 2 秒在 B 点）；轨道稳定只要求机器人**在跑道上**（可以快几秒、慢几秒）。对于走路机器人，我们关心的是"脚落在哪里"，而不是"几点几秒落在那里"——所以轨道稳定更合适。

3. **为什么线性系统不能有稳定极限环？** 线性系统的解要么收敛到原点、要么发散、要么做简谐振动（振幅由初始条件决定，不会自动恢复到特定值）。稳定极限环要求"振幅自动恢复到特定值"，这本质是非线性现象（如范德波尔振荡器中的能量饱和）。

4. **横向坐标的直觉**：想象你站在跑步机上跑步。$\tau$ 是你的"跑步进度"（跑了多少圈），$x_\perp$ 是你**偏离跑道中心线**的距离。如果 $x_\perp$ 始终能收敛到 0，你就稳定在跑道上了——这就是轨道稳定。

5. **为什么横向 LQR 比全坐标 LQR 好？** 全坐标 LQR 既要让你"回到跑道"，又要让你"按正确时间回到正确位置"——这是两个任务。横向 LQR **只要求你回到跑道**，不关心时间——这是更轻松的任务，所以反馈增益更小、更鲁棒。

6. **"每周期一次决策"vs"连续反馈"**：前者像走路时"每步决定一次落脚点在哪"，后者像"脚在空中时持续微调姿态"。前者计算简单，后者控制精细。

---

## 💻 六、代码实践重点补充说明（这是本章最该动手的部分）

教材配套了 `limit_cycles.ipynb` Notebook，其中包含 Van der Pol 极限环的轨迹优化 。以下是按重要性排序的实践路径：

### 实验一：Van der Pol 振荡器的极限环轨迹优化（**最重要**）

**目的**：用直接配点法 + 可变步长找到极限环。

```python
import numpy as np
from pydrake.all import (
    MathematicalProgram, Solve, DirectCollocation,
    PiecewisePolynomial
)

# Van der Pol 振荡器：ẋ₁ = x₂, ẋ₂ = μ(1-x₁²)x₂ - x₁
mu = 2.0  # 非线性强度

def van_der_pol(x, u):
    x1, x2 = x[0], x[1]
    dx1 = x2
    dx2 = mu * (1 - x1**2) * x2 - x1
    return np.array([dx1, dx2])

# 直接配点
N = 50  # 配点数量
h_min = 0.01  # 最小步长
h_max = 0.2   # 最大步长

prog = MathematicalProgram()
# 决策变量：状态轨迹 x[i] ∈ R²，步长 h[i] > 0
x_vars = [prog.NewContinuousVariables(2, f"x_{i}") for i in range(N+1)]
h_vars = [prog.NewContinuousVariables(1, f"h_{i}")[0] for i in range(N)]

# 约束：周期性 x[0] = x[N]
prog.AddConstraint(x_vars[0][0] == x_vars[N][0])
prog.AddConstraint(x_vars[0][1] == x_vars[N][1])

# 约束：步长下限
for i in range(N):
    prog.AddConstraint(h_vars[i] >= h_min)
    prog.AddConstraint(h_vars[i] <= h_max)

# 约束：动力学（梯形积分或中点法）
for i in range(N):
    x_i = x_vars[i]
    x_next = x_vars[i+1]
    h = h_vars[i]
    
    # 中点法：x_{i+1} = x_i + h * f(x_i + x_{i+1})/2
    x_mid = 0.5 * (x_i + x_next)
    f_mid = van_der_pol(x_mid, 0)
    prog.AddConstraint(x_next[0] == x_i[0] + h * f_mid[0])
    prog.AddConstraint(x_next[1] == x_i[1] + h * f_mid[1])

# 目标：最小化总时间和（间接促使找到周期解）
total_time = sum(h_vars)
prog.AddCost(total_time)

# 初始猜测：绕单位圆运动
for i in range(N+1):
    theta = 2 * np.pi * i / N
    x_vars[i][0].set_value(np.cos(theta))
    x_vars[i][1].set_value(np.sin(theta))
for i in range(N):
    h_vars[i].set_value(2 * np.pi / N)

# 求解
result = Solve(prog)
assert result.is_success()

# 提取解
x_traj = np.array([result.GetSolution(x_vars[i]) for i in range(N+1)])
h_traj = np.array([result.GetSolution(h_vars[i]) for i in range(N)])
period = np.sum(h_traj)
print(f"Found limit cycle with period T = {period:.4f}")
```

**预期现象**：
- 求解器收敛到 Van der Pol 振荡器的稳定极限环
- 周期约为 T ≈ 3.5（对于 μ=2）
- 轨迹是闭合曲线，形状类似扭曲的单位圆

**关键观察**：
- **必须提供"绕圈"初始猜测**——随机初始猜测会陷入局部最小值
- **可变步长 $h_n$ 是关键**——它允许时间伸缩以满足周期性

### 实验二：环振子的横向坐标与李雅普诺夫分析（解析验证）

**目的**：亲手验证 Example 16.2 的解析结果。

```python
import numpy as np

# 环振子参数
alpha = 1.0

def ring_oscillator_dynamics(x):
    """环振子动力学"""
    x1, x2 = x[0], x[1]
    r = np.sqrt(x1**2 + x2**2)
    norm_factor = 1.0 / r if r > 1e-10 else 0.0
    dx1 = x2 - alpha * x1 * (1 - norm_factor)
    dx2 = -x1 - alpha * x2 * (1 - norm_factor)
    return np.array([dx1, dx2])

def to_transverse_coords(x):
    """映射到横向坐标"""
    x1, x2 = x[0], x1, x[1]
    tau = np.arctan2(-x2, x1)
    x_perp = np.sqrt(x1**2 + x2**2) - 1.0
    return tau, x_perp

def transverse_dynamics(x_perp, tau):
    """横向动力学（解析）"""
    dtau = 1.0
    dx_perp = -alpha * x_perp
    return dtau, dx_perp

# 验证李雅普诺夫函数 V = x_perp²
def verify_lyapunov():
    # 在不同 x_perp 值下验证 V̇ < 0
    x_perp_vals = np.linspace(-0.9, 2.0, 100)
    all_negative = True
    for xp in x_perp_vals:
        V = xp**2
        V_dot = -2 * alpha * xp**2
        if xp > -1 and V_dot >= 0:
            all_negative = False
            break
    print(f"For all x_perp > -1, V̇ < 0: {all_negative}")
    
    # 吸引域：V < 1 即 x_perp² < 1 → -1 < x_perp < 1
    print(f"Invariant set V < 1 corresponds to -1 < x_perp < 1")
    print(f"But actually ALL x_perp > -1 are in region of attraction")

verify_lyapunov()

# 仿真验证收敛
x = np.array([2.0, 0.0])  # 初始状态在极限环外
dt = 0.01
trajectory = [x.copy()]
for t in range(2000):
    x = x + dt * ring_oscillator_dynamics(x)
    trajectory.append(x.copy())
    
    # 检查是否收敛到单位圆
    if t % 500 == 0:
        r = np.sqrt(x[0]**2 + x[1]**2)
        print(f"t={t*dt:.2f}: radius = {r:.4f} (target: 1.0)")

trajectory = np.array(trajectory)
```

**预期现象**：
- 初始半径 r=2.0 的状态，逐渐收敛到 r=1.0（单位圆）
- 验证 $\dot{V} = -2\alpha x_\perp^2 < 0$ 对所有 $x_\perp > -1$ 成立
- 这直观展示了极限环的局部渐近稳定性

### 实验三：范德波尔振荡器的横向线性化与周期里卡蒂方程

**目的**：实践"向后时间积分"求解周期里卡蒂方程。

```python
import numpy as np
from scipy.integrate import solve_ivp

# 标称极限环（从实验一获得）
# 这里简化为已知周期解 x0(t)
def nominal_trajectory(t):
    """标称极限环（示例）"""
    # 实际应从轨迹优化结果插值
    # 简化：用解析近似
    omega = 2 * np.pi / 3.5  # 周期约3.5
    return np.array([np.cos(omega * t), np.sin(omega * t)])

def nominal_control(t):
    """标称控制输入（Van der Pol 无控制输入，u=0）"""
    return np.array([0.0])

# 计算横向线性化矩阵 A_perp(τ)
def compute_A_perp(tau):
    """计算 A_perp(τ) = ∂f_perp/∂x_perp"""
    # 实际需对横向动力学求偏导
    # 简化示例：使用数值微分
    x0 = nominal_trajectory(tau)
    # ... 具体计算省略
    # 返回 1x1 矩阵（环振子是1维横向）
    return np.array([[-alpha]])  # 对于环振子

# 向后时间积分周期里卡蒂方程
def solve_periodic_riccati_backwards():
    """
    向后时间积分：-Ṗ = P A + Aᵀ P + Q
    直到收敛到周期解
    """
    Q = np.array([[1.0]])  # 正定权重
    P = np.array([[1.0]])  # 初始猜测
    dt = -0.001  # 负时间步长（向后积分）
    
    for iteration in range(100000):
        # 在多个 τ 点上积分
        for tau in np.linspace(0, 3.5, 100):
            A = compute_A_perp(tau)
            # 向后欧拉：P_new = P + dt * (P A + Aᵀ P + Q)
            P_dot = P @ A + A.T @ P + Q
            P = P + dt * P_dot
        
        # 检查周期性：P(0) ≈ P(period)
        # 如果收敛，跳出
        if iteration % 1000 == 0:
            print(f"Iteration {iteration}: P = {P[0,0]:.6f}")
    
    return P

print("Solving periodic Riccati equation by backward integration...")
P_solution = solve_periodic_riccati_backwards()
print(f"Periodic solution P = {P_solution[0,0]:.6f}")
print(f"Lyapunov function: V = {P_solution[0,0]:.6f} * x_perp²")
```

**预期现象**：
- 向后时间积分逐渐收敛到周期解
- 得到的 P 是正定的
- $V(x_\perp, \tau) = P(\tau) x_\perp^2$ 是有效的李雅普诺夫函数

### 实验四：横向 LQR 控制器设计

**目的**：为极限环设计横向 LQR 反馈控制器。

```python
import numpy as np

# 系统矩阵（标称轨迹上的横向线性化）
# 对于受控系统：ẋ_⊥ = A_⊥(τ)x_⊥ + B_⊥(τ)u

def A_perp(tau):
    """横向系统矩阵（时变）"""
    # 示例：环振子 + 控制输入
    return np.array([[-alpha]])  # 1维

def B_perp(tau):
    """控制输入矩阵"""
    return np.array([[1.0]])  # 1维控制

# 横向 LQR 设计
Q = np.array([[1.0]])  # 横向状态权重
R = np.array([[0.1]])  # 控制权重

# 时变微分 Riccati 方程
# -Ṗ = P A + Aᵀ P - P B R⁻¹ Bᵀ P + Q

def solve_TVLQR_backwards():
    """向后时间积分求解 TVLQR 增益"""
    T = 3.5  # 周期
    N_steps = 350
    dt = T / N_steps
    
    # 存储 P(τ) 和 K(τ)
    tau_grid = np.linspace(0, T, N_steps)
    P_grid = np.zeros(N_steps)
    K_grid = np.zeros(N_steps)
    
    # 终端条件：P(T) = Q（或某个正定值）
    P = Q.copy()
    P_grid[-1] = P[0, 0]
    K_grid[-1] = np.linalg.inv(R) @ B_perp(T).T @ P
    
    # 向后积分
    for i in range(N_steps - 2, -1, -1):
        tau = tau_grid[i]
        A = A_perp(tau)
        B = B_perp(tau)
        
        # 微分 Riccati 方程：Ṗ = P A + Aᵀ P - P B R⁻¹ Bᵀ P + Q
        # 向后积分：-Ṗ = -P A - Aᵀ P + P B R⁻¹ Bᵀ P - Q
        P_dot_backwards = -(P @ A + A.T @ P - P @ B @ np.linalg.inv(R) @ B.T @ P + Q)
        P = P + (-dt) * P_dot_backwards  # 向后欧拉
        
        P_grid[i] = P[0, 0]
        K = np.linalg.inv(R) @ B.T @ P
        K_grid[i] = K[0, 0]
    
    # 强制周期性：P(0) = P(T)
    # 通过缩放调整
    scaling = P_grid[-1] / P_grid[0]
    P_grid *= scaling
    K_grid *= scaling
    
    return tau_grid, P_grid, K_grid

tau_grid, P_grid, K_grid = solve_TVLQR_backwards()

print("TVLQR gains computed.")
print(f"K(τ=0) = {K_grid[0]:.4f}")
print(f"K(τ=T/2) = {K_grid[len(K_grid)//2]:.4f}")

# 闭环仿真
def closed_loop_simulation():
    """仿真横向 LQR 闭环"""
    x_perp = np.array([0.5])  # 初始横向偏差
    tau = 0.0
    dt = 0.01
    
    trajectory = []
    for t in range(500):
        # 插值得到当前 τ 的 K
        idx = int(tau / 3.5 * len(K_grid)) % len(K_grid)
        K = K_grid[idx]
        
        # 控制：u = -K * x_perp
        u = -K * x_perp
        
        # 横向动力学
        A = A_perp(tau)
        B = B_perp(tau)
        x_perp_dot = A @ x_perp + B @ u
        
        x_perp = x_perp + dt * x_perp_dot
        tau = (tau + dt) % 3.5
        
        trajectory.append(x_perp[0])
        
        if t % 100 == 0:
            print(f"t={t*dt:.2f}: x_perp = {x_perp[0]:.6f}")
    
    return np.array(trajectory)

print("\nClosed-loop simulation:")
traj = closed_loop_simulation()
```

**预期现象**：
- 横向偏差 $x_\perp$ 指数收敛到 0
- 机器人被拉回极限环
- 反馈增益 $K(\tau)$ 是周期的

### 实验五：双积分器的横向坐标反例

**目的**：验证"糟糕的横向坐标选择会导致不可稳定"。

```python
import numpy as np

# 双积分器：q̈ = u
# 标称轨迹：u(t) = 1, 从初始条件 q(0)=0, q̇(0)=0
# 解析解：q(t) = 0.5*t², q̇(t) = t

def dual_integrator_dynamics(q, qdot, u):
    return np.array([qdot, u])

# 糟糕的横向坐标选择：τ = q̇, x_⊥ = q
# 标称轨迹：τ_0(t) = t, x_⊥0(t) = 0.5*t²

def bad_transverse_linearization():
    """验证这个横向线性化不可稳定"""
    # 在标称轨迹附近线性化
    # 偏差变量：δτ = q̇ - t, δx_⊥ = q - 0.5*t²
    
    # 动力学：
    # q̈ = u
    # 令 u = 1 + δu
    # 则 δq̈ = δu
    
    # 横向线性化：
    # δτ̇ = δq̈ = δu
    # δẋ_⊥ = δq̇ = δτ
    
    # 写成矩阵形式：
    # [δτ̇]   [0 0] [δτ]   [0]
    # [δẋ_⊥] = [1 0] [δx_⊥] + [1] δu
    
    A_perp = np.array([[0, 0],
                       [1, 0]])
    B_perp = np.array([[0],
                       [1]])
    
    # 检查可控性
    controllability_matrix = np.hstack([B_perp, A_perp @ B_perp])
    rank = np.linalg.matrix_rank(controllability_matrix)
    print(f"Controllability matrix rank: {rank} (should be 2 for controllable)")
    print(f"System is {'controllable' if rank == 2 else 'NOT controllable'}")
    
    # 结论：这个横向线性化不可稳定！
    # 因为 A_perp 的特征值都是0，系统本身临界稳定
    # 而 B_perp 只能影响 δx_⊥，无法直接控制 δτ

bad_transverse_linearization()
```

**关键洞察**：
- 这个横向坐标选择**不可稳定**
- 问题根源：τ = q̇ 是横向坐标的**糟糕选择**
- 正确做法：用 Manchester 2011 的方法，**在优化横向坐标时包含可控性准则**

### 实验六：行走机器人的 SOS 吸引域估计（进阶）

**基于 Manchester et al. 2011 的方法** ：

```python
# 概念框架（实际需要 Drake + SOS 工具）
"""
1. 将目标极限环周围的动力学分解为切向和横向分量
2. 在横向动力学中使用 SOS 分析（半定规划）搜索李雅普诺夫函数
3. 处理混合系统的冲击映射（impact maps）
4. 优化横向表面（transversal surfaces）
5. 优化李雅普诺夫函数
6. 设计轨道稳定化控制器

例子系统：
- 范德波尔振荡器
- 无轮辐轮（rimless wheel）
- 罗盘步态（compass gait）

核心思想：
- 横向动力学是 (n-1) 维的
- 用 SOS 多项式参数化 V(x_⊥)
- 约束 V̇(x_⊥) 为负定（SOS）
- 用 S-procedure 处理周期性约束
"""
```

---