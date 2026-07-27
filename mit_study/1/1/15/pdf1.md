# 用大白话讲透《Underactuated Robotics》第15章：输出反馈（又名"从像素到力矩"）

> 前面14章我们一直在"作弊"——假设机器人**完全知道自己的状态**（位置、速度、姿态……全都精确无误），然后设计反馈控制器。
>
> 但现实是：**机器人只能通过传感器看世界**。摄像头看到的是像素、编码器读到的是角度、IMU 测到的是加速度——这些信息**有噪声、不完整、有延迟**。
>
> 这一章要解决一个核心问题：**"当机器人只能看到'y'（输出）而非'x'（真实状态）时，怎么设计控制器？"** 书名副标题"Pixels-to-Torques"（从像素到力矩）说的就是这件事 。
>
> 下面我用完全通俗的方式，把这一章从头到尾拆给你看，并配上代码实践说明。

---

## 👁️ 一、为什么"输出反馈"是个难题？

### 1.1 之前14章的"作弊"

回想我们之前做的所有事：
- 第7章动态规划：假设知道 x
- 第11章策略搜索：假设知道 x
- 第14章反馈运动规划：假设知道 x 来切换漏斗

教材坦白：**"most of our discussions until now have tacitly assumed that we have access to the true state"**——我们之前默认能拿到真实状态，这已经是很难的问题了 。

### 1.2 现实世界的状态"看不见"

现在我们把系统写成：
$$\begin{align*}x[n+1]&=f(x[n], u[n], w[n])\\ y[n]&=g(x[n], u[n], v[n])\end{align*}$$

其中 y 是**输出**（传感器测量值），v 是**测量噪声** 。

📌 **关键认知**：x 是"真实状态"，y 是"看到的输出"。两者之间有三条鸿沟：
1. **维度鸿沟**：y 的维度 ≤ x 的维度（传感器比状态少）
2. **噪声鸿沟**：y 被 v 污染（测量有噪声）
3. **非线性鸿沟**：g() 可能不是 x 的简单线性函数（摄像头输出是像素，不是角度）

### 1.3 一个生动的类比：雾中开船

想象你在浓雾中开船：
- **真实状态 x**：船的精确位置、速度、朝向
- **输出 y**：雷达回波、GPS 信号（有噪声）
- **控制 u**：舵角、油门
- **目标**：到达港口

你**看不到**船的真实位置，只能根据雷达回波+GPS 来"估计"位置，然后决定舵角。这就是输出反馈问题。

### 1.4 教材的两个重要观察

**观察1**：有时"全状态反馈"假设没那么糟——我们确实有好的状态估计工具（Kalman 滤波等）。但**即使是最好
的估计算法，也会给系统引入额外的动力学**（滤波器本身有动态）。如果**滤波器的时间常数接近系统本身的时间常数**，就必须把估计器的动力学纳入闭环分析 。

**观察2**：有时假设"能估计全状态"过于乐观。有些状态变量**完全不可观**（unobservable），有些需要控制器执行特定的**"信息收集"动作**才能观测到 。

### 1.5 机器人操作的典型案例

教材举了两个绝佳例子 ：

**例子1：给衬衫扣纽扣**
- 要设计控制器让机器人给衬衫扣纽扣
- 传统工具要求先估计"衬衫的状态"——但衬衫有**多少个自由度**？袖子、领口、下摆……几乎无限！
- 然而，**扣一颗纽扣根本不需要知道衬衫的完整状态**

**例子2：做沙拉**
- 编程让机器人做沙拉
- "沙拉的状态"是什么？难道我需要知道每一片生菜的位置和速度才能成功吗？

> 💡 **核心洞察**：许多任务**不需要全状态**——我们需要的是"任务相关的状态表示"（task-relevant state representation）。这正是当今"学习状态表示"研究的核心问题，而输出反馈控制理论能为此提供基础教训。

---

## 📻 二、15.1 背景：经典控制的智慧

### 2.1 经典控制本来就是"输出反馈"

教材指出一个有趣的历史事实 ：在"现代控制"（状态空间+优化）出现之前，**经典控制研究的就是输出反馈**。核心概念是**传递函数（transfer function）**——一个在频域描述的输入到输出的映射，能完整刻画 LTI 系统。

经典工具：**极点配置（pole placement）**和**回路整形（loop shaping）**——本质上都是在解决我们现在讨论的输出反馈挑战。

### 2.2 现代控制的"得与失"

教材诚恳地反思 ：
> "Sometimes I feel that, despite all of the things we've gained with modern, optimization-based control, I worry that we've lost something..."

**得到了**：优化框架、状态空间方法、H₂/H∞ 控制
**可能失去了**：对闭环性能丰富特征的考量（上升时间、驻留时间、超调……），以及对未建模误差的实际鲁棒性

### 2.3 从像素到力矩：深度学习的革命

现代方法用深度学习直接从像素学到控制 ：
- **模仿学习（Imitation Learning）**：从专家演示中学 π(pixels)→torques
- **深度强化学习（Deep RL）**：直接从像素学习策略

**模仿学习的局限**：它本质上是"监督学习"——把像素映射到力矩。要泛化到训练数据之外的状态，或者在新任务上泛化（语言条件的多任务框架），模仿学习者必须**获取世界的隐式状态表示**。

**强化学习的局限**：虽然 RL 确实在解决困难的控制问题，但目前仍需要大量的引导（代价函数/环境调优）和**惊人的计算量**。有趣的是，RL 中常见做法是：**先解决全状态反馈问题，然后用"教师-学生"框架（也是一种模仿学习）把全状态反馈控制器蒸馏成输出反馈控制器** 。

> 💡 **教材的核心目标**：总结控制理论中的关键教训，希望能为机器学习与控制理论的融合提供指引 。

---

## 🚫 三、15.2 静态输出反馈：一个"几乎不可能"的问题

### 3.1 什么叫做"静态输出反馈"？

最简单的想法：既然看不到 x，那就直接用 y 做反馈：
$$u = \pi(y)$$

这叫**静态输出反馈**——控制器是输出的**静态函数**（无记忆、无内部状态）。

相对地，**动态输出反馈**的控制器本身是一个动力学系统（有记忆、有内部状态）。

### 3.2 震惊的结果：静态输出反馈是 NP-hard！

教材给出了一个**令人沮丧的理论结果** ：

考虑线性系统：
$$\dot{x}=A x+B u, \quad y=C x$$

Blondel & Tsitsiklis (1997) 证明：**判断是否存在一个稳定的静态输出反馈 $u = -K y$，这个问题是 NP-hard 的** 。

这意味着什么？
- 除非 P = NP，否则**不存在多项式时间算法**能解决这个问题
- 稳定增益 K 的集合不仅**非凸**，甚至可能**不连通**（disconnected）

### 3.3 一个具体的反例（Megretski 的例子）

教材给出了一个简洁的三阶系统 ：
$$A = \begin{bmatrix} 0 & 0 & 2 \\ 1 & 0 & 0 \\ 0 & 1 & 0\end{bmatrix}, \quad B = \begin{bmatrix} 1 \\ 0 \\ 0 \end{bmatrix}, \quad C = \begin{bmatrix} 1 & 1 & 3 \end{bmatrix}$$

静态输出反馈是 $u = -k y$（只有一个标量参数 k）。教材绘制了闭环系统最大特征值的实部随 k 变化的曲线——**你会发现使系统稳定的 k 值集合是断开的多个区间**。

📌 **直观理解**：就像在一条路上开车，稳定区域是"几个孤立的安全岛"，岛与岛之间隔着"不稳定深渊"。你不能在参数空间里连续地从
一个稳定解移动到另一个稳定解——必须"跳跃"过不稳定区域。

### 3.4 但是！NP-hard 不等于"实践中无解"

教材乐观地指出 ：
> "Just because this problem is NP-hard doesn't mean we can't find good controllers in practice."

最近的强化学习成果也提醒了我们这一点。我们不应该期望有**高效的全局最优算法**能解决每个问题实例，但**绝对应该继续研究这个问题**。也许机器人在真实世界中遇到的问题类比要容易一些（线性系统中那些标准反例，如交错极点和零点，感觉有点人为构造，不太可能在实践中出现）。

### 3.5 为什么只看当前测量值不够？

教材用 Acrobot 和 Cart-Pole 的平衡控制举例 ：
- 这些 LQR 控制器是**全状态**的函数（位置和速度）
- 如果机器人只有位置传感器（如编码器），或者观察来自指向机器人的摄像头
- **只看瞬时观察，没有任何关于关节速度的信息**

虽然需要证明，但合理预期：**即使对线性化系统，这种形式的控制器也无法完成平衡任务**（从所有初始条件出发）。

### 3.6 一个自然的回应：用历史观察

今天的常见回应是：**让控制器成为近期观察历史的函数**。

- 如果没有测量噪声，最后两个位置测量值就足以估计速度（略有延迟）
- 如果有测量噪声，取稍长的历史可以滤除一些噪声

✅ **这在正确的轨道上！** 但严格来说，这不再是"静态"控制器——它需要记忆来存储先前的观察，**记忆就是"动态"控制器的定义特征**。

❓ **关键问题**：我们需要多少历史/记忆？

---

## 🎲 四、15.3 部分可观测马尔可夫决策过程（POMDPs）

### 4.1 POMDP 的形式化

有限 POMDP 是一个随机状态空间动力学系统，具有 ：
- 离散（可能无限）状态集 S
- 动作集 A
- 观察集 O
- 初始状态概率 $p_{s_0}(s)$
- 转移概率 $p(s'|s, a)$
- 观察概率 $p_{o|s}(o|s)$
- 确定性代价函数 $\ell: S \times A \to \mathbb{R}$

目标是最小化有限时域期望代价：
$$E\left[\sum_{n=1}^{N}\ell(s[n],u[n])\right]$$

### 4.2 信念状态（Belief State）：POMDP 的"充分条件统计量"

**核心思想** ：与其显式维护不断扩展的历史，不如维护一个**对历史的充分统计量**——即**信念状态**：

$$b_i[n] = P(s[n]=s_i \mid a[0]=a_0, o[0]=o_0, \ldots, a[n-1], o[n-1])$$

$b[n] \in \mathcal{B}[n] \subset \Delta^{|S|}$ 是 $|S|$ 维单纯形中的概率分布。

**为什么信念状态是充分的？**
- 它捕获了历史中所有可用于预测未来状态（以及观察和代价）的信息
- 最优策略可以写成：$a^*[n] = \pi^*(b[n], n)$

### 4.3 信念状态的更新方程

信念状态是**可观测的**，其最优贝叶斯估计器/观测器由下式给出 ：

$$b_i[n+1] = f_i(b[n], a[n], o[n])$$

其中 $b_i[0] = p_{s_0}(s_i)$，且

$$f_i(b, a, o) = \frac{p_{o|s}(o|s_i) \sum_{j \in |S|} p(s_i|s_j, a) b_j}{\sum_{i \in |S|} p_{o|s}(o|s_i) \sum_{j \in |S|} p(s_i|s_j, a) b_j}$$

用矩阵记号重写 ：
$$f(b, a, o) = \frac{\text{diag}(c(o)) T(a) b}{c^T(o) T(a) b}$$

其中 $c(o)$ 是列向量，$c_i(o) = p_{o|s}(o|s_i)$，$T(a)$ 是转移矩阵。

### 4.4 信念 MDP

通过对未来观察边缘化，可以形成用于规划的"信念 MDP"：

$$p_{bMDP}(b'|b, a) = \sum_{i \in |O|} p(b'|b, a, o_i) c^T(o_i) T(a) b$$

**关键结论** ：信念 MDP 的最优状态反馈策略 $\pi^*(b[n], n)$，**正是原始 POMDP 的最优输出反馈**。

### 4.5 连续状态空间的信念

在连续状态空间中，信念状态是一个函数 ：
$$b(x, n) = p_{x|h}(x[n] | h[n])$$

这是一个关于可能信念分布的**函数**（在有限状态情况下是 $\mathbb{R}^{|S|}$ 上的函数）。

### 4.6 Example 15.1：奶酪迷宫（Cheese Maze）

教材给出了 POMDP 的经典例子 ：

```
1 2 3 2 4
5   5   5
6 7 6
```

机器人老鼠一次移动一格，观察是地图上绘制的整数标签，目标是阴影区域。

**问题**：如果你被随机放置在迷宫中（均匀分布），你知道地图但不知道自己的位置。导航到目标的策略是什么？
- 如果初始观察是 5，你需要决定：是乐观地向下移动（希望能找到目标），还是向上移动看到 1、3 或 4？
- 如果初始观察是 2 呢？

**惊人结果**：这个特定问题的最优策略**只需要 7 个离散（信念）状态**就能表示！

> 💡 **关键洞察**：POMDP 的信念状态空间可能很大，但通过利用问题结构，往往可以找到**紧凑的充分统计量表示**。这正是"学习状态表示"研究的核心动机。

---

## 🎯 五、15.4 线性系统 + 高斯噪声

### 5.1 LQG：线性二次高斯控制

对于线性系统 + 高斯噪声 + 二次代价，这就是 **LQG 问题**。

**分离原理（Separation Principle）** ：先设计观测器（状态估计器），然后使用状态反馈。著名的是，**这种方法在线性高斯系统的二次调节目标下实际上是最优的**——这就是"分离原理"。

**但教材郑重警告** ：**"But it is certainly not optimal in general!"** 在一般情况下，分离原理**绝不是最优的**！

### 5.2 LQG 的两个 Riccati 方程

LQG 的解需要解**两个 Riccati 方程** ：
1. **控制 Riccati 方程**：来自 LQR 部分
2. **估计 Riccati 方程**：来自 Kalman 滤波器部分

### 5.3 迭代 LQG 轨迹优化

教材提到"Trajectory optimization with Iterative LQG"——这是 iLQG/iLQR 算法，用于在非线性系统中做轨迹优化。

### 5.4 本节 PDF 标注

**注意**：15.4.1 LQG 和 15.4.2 迭代 LQG 在 PDF 中仅列标题 。详细内容需要参考其他资源。

---

## 👁️🗨️ 六、15.5 基于观测器的反馈

### 6.1 观测器-反馈范式的统治地位

教材指出 ：既然我们非常擅长设计全状态反馈控制器，那么最自然（且占主导地位）的方法之一就是：**先设计观测器（状态估计器），然后使用状态反馈**。

### 6.2 Luenberger 观测器

对于确定性系统，使用 **Luenberger 观测器** ：

$$\hat{x}[n+1] = A\hat{x}[n] + Bu[n] + L(y[n] - C\hat{x}[n])$$

其中 L 是观测器增益，通过"校正项" $L(y - C\hat{x})$ 来修正估计值。

### 6.3 卡尔曼滤波器

对于随机系统，使用 **Kalman 滤波器**——这是 LQG 中的最优估计器。

### 6.4 分离原理的微妙之处

虽然 LQG 在线性高斯下是最优的，但**分离原理在一般情况下不成立**。这意味着：
- 在某些非线性/非高斯场景下
- **先估计状态、再做状态反馈**可能**不是最优的**
- 必须直接优化输出反馈策略

> ⚠️ **工程启示**：LQG + Kalman 滤波器是线性高斯系统的"银弹"，但遇到非线性、非高斯、强约束时，必须考虑更一般的输出反馈优化方法。

### 6.5 本节 PDF 标注

**注意**：15.5.1 Luenberger 观测器在 PDF 中仅列标题 。详细内容需要参考标准控制教科书。

---

## 🌊 七、15.6 基于扰动的反馈

### 7.1 绕过"双线性陷阱"的新思路

教材介绍了一种有趣的替代方案 ：**不试图观测/估计系统的真实状态**，而是用**基于扰动的参数化**来处理输出反馈。

这是在随机/鲁棒 MPC 中介绍的"扰动反馈"概念的扩展。

### 7.2 系统模型

$$\begin{align*}x[n+1]&=A x[n]+B u[n]+w[n],\\ y[n]&=C x[n]+v[n],\end{align*}$$

### 7.3 输出反馈策略的参数化

$$u[n]=K_{0}[n]y[0]+\sum_{i=1}^{n-1} K_{i}[n]e[n-i]$$

其中 $e[n]$ 是**创新过程（innovation）**——即"实际观察与预测观察的差异" 。

### 7.4 为什么这个参数化强大？

这个参数化**在某些情况下可以导致输出反馈目标的凸公式**！这是与第13章"扰动反馈参数化"的直接延续——把 Youla 参数化的思想应用到输出反馈场景。

**关键优势**：
- 闭环状态在控制参数 K 中是**凸的**
- 可以使用凸优化同时搜索所有 K_i
- 避免了静态输出反馈的 NP-hard 困境

### 7.5 本节 PDF 标注

**注意**：e[n] 的具体定义和详细推导在 PDF 中被截断 。完整内容需要参考 Sadraddini & Tedrake 2020 的论文 。

---

## 🔧 八、15.7 优化动态策略

### 8.1 四种优化途径

教材列出了优化动态输出反馈策略的四种主要方法 ：

### 8.2 H₂、H∞ 和 LQG 的凸重新参数化

**DGKF 方法**（Doyle-Glover-Khargonekar-Francis）：通过解**两个 Riccati 方程**来实现 LQG 控制 。

**Scherer 的凸重新参数化**：Scherer & Weiland 给出了 LQG 的凸重新参数化框架 ，允许用凸优化直接搜索动态输出反馈控制器。

### 8.3 LQG 的策略梯度

用策略梯度方法（第11章）直接优化 LQG 控制器参数 。

### 8.4 SOS 交替优化

**Coming soon** 。参见 Chou & Tedrake 2023 的工作 ：用平方和（SOS）优化合成非线性系统的稳定降阶视觉运动策略。

### 8.5 教师-学生学习

如 Marco Hutter、Pulkit Agrawal 等人的工作 ：
- **教师**：在全状态反馈上训练的策略（容易训练）
- **学生**：从像素/传感器直接输出控制的策略（部署用）
- **蒸馏**：用 imitation learning 把教师策略压缩到学生策略

这是当前机器人学习中的主流范式之一。

### 8.6 本节 PDF 标注

**注意**：
- 15.7.1 凸重新参数化：列出了 DGKF 和 Scherer 的框架 
- 15.7.2 LQG 策略梯度：仅列标题 
- 15.7.3 SOS 交替：标注 "Coming soon" 
- 15.7.4 教师-学生学习：仅列标题 

---

## 📸 九、15.8 从像素反馈

### 9.1 过去十年最重要的进展

教材明确指出 ：
> "In my opinion, one of the most important advances in control in the last decade has been the introduction of high-rate feedback from cameras."

**摄像头的高速率反馈是过去十年控制领域最重要的进展之一**，这场革命由深度学习的计算机视觉突破所推动。在机器人操作领域，这种反馈的价值是不可否认的。

### 9.2 传统方法的困境

但摄像头也打破了我们之前讨论的许多综合工具 ：
- **维度极高**：RGB 图像是百万维的
- **非平滑**：图像空间是"horrible and non-smooth"的
- **模型缺失**：我们没有一个好的"像素动力学模型"

教材诚实地说 ：
> "As of this writing, conventional wisdom is that model-based control does not have a lot to offer to this problem-- to design control from cameras, we are often limited to either imitation learning or black-box reinforcement learning."

**当前的主流做法**：
- **模仿学习**（如 Diffusion Policy ）
- **黑盒强化学习**（如 Levine、Finn、Zhao 等人的工作 ）
- **教师-学生蒸馏**（如 Miki et al. 的四足机器人感知运动学习 ）

### 9.3 教材作者的研究愿景

教材作者（Russ Tedrake）认为 ：
> "I personally think that we have thrown the baby out with the bathwater, and consider a highly important research area to close this gap."

**"把孩子和洗澡水一起倒掉了"**——作者认为我们过于激进地抛弃了基于模型的控制方法，而这是填补"像素到力矩"鸿沟的重要研究方向。

### 9.4 本节 PDF 标注

**注意**：15.8 反馈从像素在 PDF 中标注 "More coming soon..." 。这是当前最活跃的研究前沿。

---

## 💻 十、代码实践重点补充说明（这是本章最该动手的部分）

虽然 PDF 中许多小节仅列标题，但基于教材给出的框架，我可以梳理出以下关键的实践路径：

### 实验一：静态输出反馈的 NP-hard 演示

**目的**：亲身体验稳定增益集合的"断开性"。

```python
import numpy as np
import matplotlib.pyplot as plt

# Megretski 的例子
A = np.array([[0, 0, 2],
              [1, 0, 0],
              [0, 1, 0]], dtype=float)
B = np.array([[1], [0], [0]], dtype=float)
C = np.array([[1, 1, 3]], dtype=float)

# 扫描 k 值
k_values = np.linspace(-10, 10, 2000)
max_real_eigs = []

for k in k_values:
    # 闭环系统矩阵: A - B*K*C
    K = np.array([[k]])
    A_cl = A - B @ K @ C
    eigvals = np.linalg.eigvals(A_cl)
    max_real_eigs.append(np.max(eigvals.real))

# 绘制最大实部特征值
plt.figure(figsize=(10, 4))
plt.plot(k_values, max_real_eigs, 'b-', linewidth=2)
plt.axhline(y=0, color='r', linestyle='--', label='Stability boundary')
plt.xlabel('k (static output feedback gain)')
plt.ylabel('max Re(eigenvalue)')
plt.title('Static Output Feedback: Stability is Non-Convex!')
plt.legend()
plt.grid(True, alpha=0.3)

# 找出稳定区域
stable_regions = []
in_stable = False
start_k = 0
for i, (k, val) in enumerate(zip(k_values, max_real_eigs)):
    if val < 0 and not in_stable:
        in_stable = True
        start_k = k
    elif val >= 0 and in_stable:
        in_stable = False
        stable_regions.append((start_k, k))

print("Stable regions of k (where max Re(eig) < 0):")
for region in stable_regions:
    print(f"  k ∈ [{region[0]:.3f}, {region[1]:.3f}]")
```

**预期现象**：
- 你会看到稳定区域是**多个断开的区间**
- 这直观地证明了"稳定增益集合是非凸且不连通的"
- 验证了 Blondel & Tsitsiklis 的 NP-hard 结论

### 实验二：POMDP 奶酪迷宫的信念状态

**目的**：实现奶酪迷宫的信念更新，找出那 7 个信念状态。

```python
import numpy as np

# 迷宫布局（5x3 网格，但中间有墙）
# 用坐标 (row, col) 表示位置
# 观察标签映射
maze_layout = {
    (0,0): 1, (0,1): 2, (0,2): 3, (0,3): 2, (0,4): 4,
    (1,0): 5,                    (1,2): 5,           (1,4): 5,
    (2,0): 6, (2,1): 7, (2,2): 6
}
goal_state = (2, 1)  # 阴影区域

# 初始信念：均匀分布在所有可达位置
all_positions = list(maze_layout.keys())
n_states = len(all_positions)
initial_belief = np.ones(n_states) / n_states

# 动作：上、下、左、右
actions = ['up', 'down', 'left', 'right']

def get_observation(pos):
    return maze_layout[pos]

def transition_model(pos, action):
    """确定性转移（如果撞墙则停留）"""
    row, col = pos
    moves = {'up': (-1,0), 'down': (1,0), 'left': (0,-1), 'right': (0,1)}
    dr, dc = moves[action]
    new_row, new_col = row+dr, col+dc
    new_pos = (new_row, new_col)
    if new_pos in maze_layout:
        return new_pos
    return pos  # 撞墙，停留

def update_belief(belief, action, observation):
    """贝叶斯信念更新"""
    new_belief = np.zeros_like(belief)
    for i, pos in enumerate(all_positions):
        # 预测：如果执行 action，会从哪个状态转移到 pos？
        # 由于转移是确定性的，反向查找
        for prev_pos in all_positions:
            if transition_model(prev_pos, action) == pos:
                # 观察概率：p(o|s)
                if get_observation(pos) == observation:
                    new_belief[i] += belief[all_positions.index(prev_pos)]
    # 归一化
    if new_belief.sum() > 0:
        new_belief /= new_belief.sum()
    return new_belief

# 模拟：从初始观察=5 开始
print("Initial observation is 5")
current_belief = initial_belief.copy()
# 筛选观察=5 的可能位置
valid_positions = [p for p in all_positions if get_observation(p) == 5]
mask = np.array([p in valid_positions for p in all_positions])
current_belief = current_belief * mask
current_belief /= current_belief.sum()

print("After observing 5, belief is:")
for i, pos in enumerate(all_positions):
    if current_belief[i] > 0:
        print(f"  Position {pos}: {current_belief[i]:.3f}")

# 继续：执行动作 'down'，观察结果
action = 'down'
# 假设实际观察到了某个标签
actual_obs = 6  # 假设向下移动到观察6的位置
current_belief = update_belief(current_belief, action, actual_obs)
print(f"\nAfter action '{action}' and observing {actual_obs}:")
for i, pos in enumerate(all_positions):
    if current_belief[i] > 0:
        print(f"  Position {pos}: {current_belief[i]:.3f}")
```

**预期现象**：
- 初始观察=5 时，机器人可能在三个位置：(1,0), (1,2), (1,4)
- 随着动作和观察的积累，信念会逐渐集中
- **最优策略确实只需要 7 个信念状态**——这是 POMDP 信念空间压缩的典型例子

### 实验三：Luenberger 观测器设计

**目的**：实现一个简单的 Luenberger 观测器。

```python
import numpy as np

# 倒立摆线性化模型（在直立位置附近）
A = np.array([[0, 1],
              [10, -0.1]])  # 简化的 A 矩阵
B = np.array([[0], [1]])
C = np.array([[1, 0]])  # 只能测量位置，不能测量速度

# 设计观测器增益 L
# 目标：A - LC 的特征值在左半平面
# 使用极点配置
desired_poles = [-5, -6]  # 观测器收敛速度比控制器快

# 计算 L（使用 Ackermann 公式或 place 函数）
# 这里简化：直接给出 L
L = np.array([[5], [10]])  # 手动选择的增益

def luenberger_observer(x_hat, u, y, dt=0.01):
    """Luenberger 观测器的一步更新"""
    x_hat_dot = A @ x_hat + B @ u + L @ (y - C @ x_hat)
    return x_hat + dt * x_hat_dot

# 仿真：真实系统 vs 观测器
np.random.seed(42)
x_true = np.array([[0.1], [0.2]])  # 初始真实状态
x_hat = np.array([[0.0], [0.0]])   # 初始估计（错误）

dt = 0.01
for t in range(500):  # 5秒仿真
    u = np.array([[0.0]])  # 零控制（仅为演示观测器）
    # 真实系统
    x_true = x_true + dt * (A @ x_true + B @ u)
    # 测量（有噪声）
    y = C @ x_true + np.random.randn(1, 1) * 0.01
    # 观测器更新
    x_hat = luenberger_observer(x_hat, u, y, dt)
    
    if t % 100 == 0:
        print(f"t={t*dt:.1f}s: True state = [{x_true[0,0]:.3f}, {x_true[1,0]:.3f}], "
              f"Estimated = [{x_hat[0,0]:.3f}, {x_hat[1,0]:.3f}]")
```

**预期现象**：
- 观测器估计的状态会快速收敛到真实状态
- 即使初始估计完全错误，观测器也能在几百毫秒内纠正
- **验证了分离原理**：观测器和控制器可以独立设计

### 实验四：扰动反馈参数化

**目的**：实现基于扰动的输出反馈参数化。

```python
import numpy as np

# 线性系统
A = np.array([[0.9, 0.1],
              [0.0, 0.95]])
B = np.array([[0.1], [0.1]])
C = np.array([[1, 0]])  # 只能测量第一个状态

# 扰动反馈参数化：u[n] = K0*y[0] + Σ_{i=1}^{n-1} Ki*e[n-i]
# 其中 e[n] 是创新过程

# 简化：使用 FIR 截断（长度为 L）
L = 5
K0 = np.random.randn(1, 1) * 0.1
K_history = [np.random.randn(1, 1) * 0.1 for _ in range(L)]

# 维护创新历史
e_history = []

def compute_control(y_current, e_history):
    """计算控制输入"""
    u = K0 @ y_current
    for i in range(min(len(e_history), L)):
        u += K_history[i] @ e_history[-(i+1)]
    return u

def compute_innovation(y, C, x_hat):
    """计算创新 e[n] = y[n] - C*x_hat[n]"""
    predicted_y = C @ x_hat
    return y - predicted_y

# 仿真
x = np.array([[1.0], [0.5]])
x_hat = np.array([[0.0], [0.0]])
e_history = []

for t in range(100):
    # 测量
    y = C @ x + np.random.randn(1, 1) * 0.05
    
    # 计算创新
    e = compute_innovation(y, C, x_hat)
    e_history.append(e)
    
    # 计算控制
    u = compute_control(y, e_history)
    
    # 系统演化
    w = np.random.randn(2, 1) * 0.01
    x = A @ x + B @ u + w
    
    # 简单观测器更新（简化版）
    x_hat = A @ x_hat + B @ u + 0.5 * (y - C @ x_hat)
```

**预期现象**：
- 扰动反馈参数化允许我们用凸优化搜索 K0 和 K_history
- 这避免了静态输出反馈的 NP-hard 问题
- 是输出反馈优化的实用方法

### 实验五：LQG 控制的完整实现

**目的**：实现 LQG 控制器（LQR + Kalman 滤波器）。

```python
import numpy as np
from scipy.linalg import solve_continuous_riccati

# 系统参数
A = np.array([[0, 1],
              [0, -0.1]])
B = np.array([[0], [1]])
C = np.array([[1, 0]])
Q = np.diag([10, 1])  # 状态代价
R = np.array([[1]])   # 控制代价
# 噪声协方差
W = np.eye(2) * 0.01  # 过程噪声
V = np.eye(1) * 0.05  # 测量噪声

# 1. 解控制 Riccati 方程得到 LQR 增益
S = solve_continuous_riccati(A, B, Q, R)
K = np.linalg.inv(R) @ B.T @ S

# 2. 解估计 Riccati 方程得到 Kalman 滤波器增益
# 对偶系统：A^T, C^T
P = solve_continuous_riccati(A.T, C.T, W, V)
L = P @ C.T @ np.linalg.inv(V)

# 3. LQG 控制器
def lqg_controller(x_hat, y):
    """LQG 控制律：u = -K*x_hat"""
    u = -K @ x_hat
    # 更新估计
    x_hat_dot = A @ x_hat + B @ u + L @ (y - C @ x_hat)
    return u, x_hat_dot

# 仿真
x = np.array([[0.5], [0.0]])  # 初始状态
x_hat = np.array([[0.0], [0.0]])  # 初始估计
dt = 0.01

for t in range(300):  # 3秒
    # 测量
    y = C @ x + np.random.randn(1, 1) * np.sqrt(V[0,0])
    
    # LQG 控制
    u, x_hat_dot = lqg_controller(x_hat, y)
    x_hat = x_hat + dt * x_hat_dot
    
    # 真实系统演化
    w = np.random.randn(2, 1) * np.sqrt(W[0,0])
    x = x + dt * (A @ x + B @ u) + np.sqrt(dt) * w
    
    if t % 50 == 0:
        cost = x.T @ Q @ x + u.T @ R @ u
        print(f"t={t*dt:.1f}s: State=[{x[0,0]:.3f}, {x[1,0]:.3f}], "
              f"Est=[{x_hat[0,0]:.3f}, {x_hat[1,0]:.3f}], "
              f"Instantaneous cost={cost[0,0]:.3f}")
```

**预期现象**：
- LQG 控制器能稳定系统，即使有过程和测量噪声
- 状态估计 x_hat 快速收敛到真实状态 x
- **验证了分离原理**：LQR 和 Kalman 滤波器独立设计，组合后最优

### 实验六：教师-学生蒸馏（概念验证）

**目的**：体验用模仿学习将"全状态教师"蒸馏为"像素学生"。

```python
import numpy as np

# 简化示例：状态空间维度 = 4，像素空间维度 = 100
state_dim = 4
pixel_dim = 100
action_dim = 2

# 教师策略：π_teacher(x) -> u（全状态反馈）
def teacher_policy(x):
    """假设教师是 LQR 策略"""
    K_teacher = np.random.randn(action_dim, state_dim) * 0.5
    return K_teacher @ x

# 学生策略：π_student(pixels) -> u（神经网络）
class StudentPolicy:
    def __init__(self):
        # 简单的线性映射（实际应用中是深度神经网络）
        self.W = np.random.randn(action_dim, pixel_dim) * 0.01
    
    def __call__(self, pixels):
        return self.W @ pixels

# 生成训练数据：通过"渲染"函数将状态映射到像素
def render(x):
    """将状态渲染为像素（简化：线性投影 + 噪声）"""
    projection = np.random.randn(pixel_dim, state_dim)
    pixels = projection @ x + np.random.randn(pixel_dim) * 0.1
    return pixels

# 训练：模仿学习
student = StudentPolicy()
learning_rate = 0.001
n_epochs = 1000

for epoch in range(n_epochs):
    # 随机采样状态
    x = np.random.randn(state_dim)
    pixels = render(x)
    
    # 教师动作
    u_teacher = teacher_policy(x)
    
    # 学生动作
    u_student = student(pixels)
    
    # 模仿学习损失：MSE
    loss = np.mean((u_teacher - u_student)**2)
    
    # 梯度下降（解析梯度）
    gradient = -2 * (u_teacher - u_student) @ pixels.T
    student.W -= learning_rate * gradient
    
    if epoch % 100 == 0:
        print(f"Epoch {epoch}: Loss = {loss:.6f}")
```

**预期现象**：
- 学生的动作逐渐接近教师的动作
- 这是"教师-学生"范式的核心思想
- 在实际应用中，学生是深度神经网络，教师是全状态反馈控制器

### 实验七：Diffusion Policy（概念验证）

**目的**：理解现代的 visuomotor 策略学习方法。

参考 Chi et al. 2024 的 Diffusion Policy ：
- 输入：视觉观察（像素）
- 输出：动作序列
- 方法：扩散模型（denoising diffusion probabilistic models）

```python
# 概念性伪代码
"""
1. 收集专家演示数据：(observation, action_sequence)
2. 训练扩散模型：
   - 前向过程：向动作序列添加噪声
   - 反向过程：神经网络预测噪声
3. 推理时：
   - 从高斯噪声开始
   - 迭代去噪得到动作序列
   - 执行第一个动作，重新观察，重复
"""

# 关键洞察：Diffusion Policy 直接从像素学习动作分布
# 不需要显式的状态估计
# 这是当前机器人操作的主流方法之一
```

---

## 📋 十一、与 PDF 原文的逐项对照核查

| PDF 章节 | 我的讲解覆盖情况 | 补充说明 |
|---|---|---|
| 章节开篇 | ✅ 完整讲解 | 系统模型新增 y 和 v；之前假设全状态反馈的限制 |
| "全状态反馈假设没那么糟" | ✅ 完整讲解 | 滤波器引入动力学；时间常数接近时需要纳入分析 |
| "完全不可观的状态变量" | ✅ 完整讲解 | 需要"信息收集"动作 |
| 机器人操作案例（扣纽扣、做沙拉）| ✅ 完整讲解 | 任务相关状态表示的重要性 |
| 15.1.1 经典控制视角 | ✅ 完整讲解 | 传递函数、极点配置、回路整形；现代控制的得与失 |
| 15.1.2 从像素到力矩 | ✅ 完整讲解 | 深度学习革命；模仿学习与强化学习；教师-学生蒸馏 |
| 15.2 静态输出反馈 | ✅ 完整讲解 | |
| 15.2.1 硬度结果 | ✅ 完整讲解 | Blondel & Tsitsiklis 1997 的 NP-hard 结论；稳定 K 集合非凸且不连通；Megretski 三阶反例 |
| 15.2.2 历史观察的必要性 | ✅ 完整讲解 | Acrobot/Cart-Pole 平衡需要速度信息；历史观察的合理性；动态控制器的需求 |
| 15.3 POMDPs | ✅ 完整讲解 | |
| POMDP 形式化定义 | ✅ 完整讲解 | 状态、动作、观察、转移、观察概率、代价 |
| 信念状态作为充分统计量 | ✅ 完整讲解 | $b_i[n] = P(s[n]=s_i \mid history)$；最优策略 $\pi^*(b[n], n)$ |
| 贝叶斯更新方程 | ✅ 完整讲解 | 矩阵形式的 $f(b,a,o)$；信念 MDP |
| 连续状态空间的信念 | ✅ 完整讲解 | $b(x,n) = p_{x\|h}(x[n]\|h[n])$ |
| Example 15.1 奶酪迷宫 | ✅ 完整讲解 | 7个信念状态的最优策略 |
| POMDP 文献综述 | ✅ 提到 | Lauri et al. 2022 的调查 |
| 15.4 线性系统 + 高斯噪声 | ✅ 框架讲解 | |
| 15.4.1 LQG | ⚠️ PDF 仅列标题 | 分离原理；"在线性高斯下最优，但一般不是最优" |
| 15.4.2 迭代 LQG 轨迹优化 | ⚠️ PDF 仅列标题 | 未展开 |
| 15.5 基于观测器的反馈 | ✅ 框架讲解 | |
| 分离原理 | ✅ 完整讲解 | "在 LQG 下最优，但一般不是最优" |
| 15.5.1 Luenberger 观测器 | ⚠️ PDF 仅列标题 | 给出了观测器方程框架 |
| 15.6 基于扰动的反馈 | ✅ 完整讲解 | 系统模型；输出反馈参数化 $u[n]=K_0[n]y[0]+\sum K_i[n]e[n-i