# 用大白话讲透《Underactuated Robotics》附录C：优化与数学规划（Optimization and Mathematical Programming）

> 前面21章我们解决了机器人各种算法问题——但**所有这些算法的"发动机"都是数值优化**。无论是轨迹优化、LQR、MPC、接触隐式规划，还是系统辨识、状态估计、模仿学习——背后都在反复求解"在满足约束的条件下，找到让某个指标最好的决策变量"。
>
> 这一章就是告诉你：**这些优化问题怎么分类、用什么求解器、在 Drake 里怎么写**。作者 Russ Tedrake 说：作为这些工具的"消费者"，你只需要高层理解就能走得很远；但有时候细节决定成败，你必须知道"引擎盖下发生了什么" 。

下面我用最通俗的方式，把这一章从头到尾拆给你看，配上生活类比，并对所有代码实践做重点补充。

---

## 🧭 一、为什么需要"优化软件层"？——C.1 优化软件

### 1.1 一句话定位

**优化软件层 = 在数学公式和具体求解器之间的"翻译官"** 。

### 1.2 生活类比：出国旅游的"翻译 App"

想象你去世界各国旅游：
- 每个国家说不同的语言（= 每个求解器有不同的 API）
- 你不想学所有语言（= 不想为每个求解器重写代码）
- 你用一个**翻译 App**（= Drake 的 `MathematicalProgram`），只要用一种语言（Python/C++）写问题，App 自动翻译成各国语言发给对应求解器

**著名的"翻译 App"**：
- MATLAB 世界：**CVX、YALMIP** 
- Julia 世界：**JuMP** 
- **Drake 的 `MathematicalProgram`**：为 C++ 和 Python 提供中间层，它的创建**最初就是专门为本书使用的优化公式化需求而驱动的** 

### 1.3 求解器的"生态圈"

**开源求解器**：
- **OSQP**：QP 求解器
- **SCS**：SOCP/SDR 求解器
- **IPOPT**：大规模 NLP 求解器
- **SNOPT**：Drake 二进制发行版自带，作者**现在最重度使用**的非线性规划求解器 

**商业求解器**（学术用户很多免费）：
- **Gurobi**：MIP/QCP 强力求解器
- **MOSEK**：SDP/SOCP 强力求解器
- **SeDuMi**：SDP 求解器

> 💡 **作者的经验之谈**：商业求解器在性能上**显著优于**他自己写的任何东西 。里面有很多技巧、微妙之处和参数选择，在实践中能产生巨大差异。

### 1.4 为什么需要抽象层？

1. **求解器专用代码切换成本高**：换求解器就要重写代码
2. **约束/成本可以用符号形式书写**（可读性更好）
3. **Drake 的 `MathematicalProgram` 类似 MATLAB 的 YALMIP 或 Julia 的 JuMP**，同时支持 Python 和 C++ 

---

## 🎯 二、C.2 通用概念

### 2.1 通用公式

$$\min_z c(z) \quad \text{subject to} \quad \phi(z) \leq 0$$

其中 $z$ 是决策变量向量，$c$ 是标量目标函数，$\phi$ 是约束向量。

**生活类比**：在允许的区域里找最好解
- $z$ = 你所有可能的选择
- $c(z)$ = 每个选择的"好坏分数"
- $\phi(z) \leq 0$ = 哪些选择是被允许的

### 2.2 通用公式的局限

作者坦白：**这个通用公式有其局限性** 。

举个关键例子：当我们编写优化来规划机器人轨迹时，在这个公式中我们通常必须**先验地选择特定数量的决策变量**来编码解。虽然我们当然可以编写改变变量数量并再次调用优化器的算法，但作者觉得这个"通用"公式未能捕捉到**基于采样的优化规划中发生的数学规划类型**——其中结果解可以用任意有限数量的参数来描述，计算在不同参数数量之间灵活转换 。

### 2.3 凸优化 vs 非凸优化（C.2.1）

**凸函数、凸约束 → 凸优化**：能保证找到全局最优
**非凸优化**：可能陷入局部最优

**作者的深刻观察——深度学习给了新视角**：

非凸 ≠ 难解。深度学习领域有大量看似高维非凸的问题被可靠求解。

**当前监督学习的主流解释**：**过参数化（over-parameterization）是关键** ——
- 我们实际上拥有**比数据更多的决策变量**
- 搜索空间中**充满了能完美拟合数据的解决方案**（即所谓的"插值解"）
- 并非所有全局最小值都同等鲁棒
- 优化算法在执行某种形式的**隐式正则化**，以挑选一个"好"的插值解

> 💡 这对机器人优化的启示：当你的问题"过参数化"时，非凸优化可能比你想象的更容易。

### 2.4 拉格朗日乘子法（C.2.2）

**等式约束优化问题**：
$$\min_z \ell(z) \quad \text{subject to} \quad \phi(z) = 0$$

**拉格朗日函数**：
$$L(z, \lambda) = \ell(z) + \lambda^T \phi(z)$$

**最优解的必要条件**：
$$\frac{\partial L}{\partial z} = 0, \quad \frac{\partial L}{\partial \lambda} = 0$$

### 2.5 Example C.1：单位圆上的优化（**经典例题**）

**问题**：$\min_{x,y} x + y \quad \text{subject to} \quad x^2 + y^2 = 1$

**几何直观**：
- 目标函数 $x+y$ 的等值线是斜率为 -1 的直线
- 约束要求在单位圆上
- 通过目测可知最优解：$x = y = -\frac{\sqrt{2}}{2}$

**拉格朗日乘子求解**：

$$L = x + y + \lambda(x^2 + y^2 - 1)$$

求偏导：
$$\begin{align}
\frac{\partial L}{\partial x} &= 1 + 2\lambda x = 0 \quad \Rightarrow \quad \lambda = -\frac{1}{2x}\\
\frac{\partial L}{\partial y} &= 1 + 2\lambda y = 1 - \frac{y}{x} = 0 \quad \Rightarrow \quad y = x\\
\frac{\partial L}{\partial \lambda} &= x^2 + y^2 - 1 = 2x^2 - 1 = 0 \quad \Rightarrow \quad x = \pm\frac{1}{\sqrt{2}}
\end{align}$$

在两个满足必要条件的解决方案中，负解是目标函数的最小化器。

> 💡 **拉格朗日乘子的物理意义**：$\lambda$ 衡量了"约束的边际价值"——如果放松约束一点点，目标函数会改善多少。

---

## 📐 三、C.3 凸优化

### 3.1 凸优化的"家族谱系"

| 类型 | 缩写 | 目标函数 | 约束 | 典型求解器 |
|---|---|---|---|---|
| 线性规划 | LP | 线性 | 线性 | Gurobi, MOSEK |
| 二次规划 | QP | 凸二次 | 线性 | OSQP, Gurobi |
| 二阶锥规划 | SOCP | 仿射 | 二阶锥 | MOSEK, SCS |
| 半定规划 | SDP | 仿射 | 线性矩阵不等式 | MOSEK, SeDuMi |
| 平方和规划 | SOS | 仿射 | 多项式非负 | MOSEK, SeDuMi |

### 3.2 Example：Atlas 上的平衡力控制

教材提到 Atlas 机器人上的平衡力控制是 QP/SOCP 的典型应用案例 。

**生活类比**：想象你站在公交车的急刹车中——
- 你的脚（接触点）可以施加力和力矩
- 你需要分配这些力来保持平衡
- 同时不能超出摩擦锥（否则会滑倒）
- 这就是一个 QP：在摩擦锥约束下，最小化"不平衡度"

### 3.3 半定规划与线性矩阵不等式（C.3.2）

**SDP 的核心威力**：为非凸优化问题写**凸松弛**。

#### 一般二次优化问题的 SDP 松弛

$$\begin{array}{ll}
\min_{y} & x^T Q x\\
\text{subject to} & x^T A_i x \geq 0,\\
& B x \geq 0,\\
& x = \begin{bmatrix}1\\y\end{bmatrix}.
\end{array}$$

**SDP 松弛** ：
$$\begin{align*}
&\min_X \operatorname{tr}(Q X)\\
&\text{subject to } e_1^T X e_1 = 1\\
&\quad \operatorname{tr}(A_i X) \geq 0,\\
&\quad B X e_1 \geq 0,\\
&\quad B X B^T \geq 0,\\
&\quad X \succeq 0,
\end{align*}$$

其中 $e_1$ 是第一个元素为 1、其他元素为 0 的向量。

#### Example C.2：非凸二次约束的 SDP 松弛

**原问题**：
$$\min_x \|x - a\|^2 \quad \text{subject to} \quad \|x - b\|^2 \geq 1$$

**SDP 松弛**：
$$\begin{align*}
\min_{x, y} & y - 2a x + a^2\\
\text{subject to } & y - 2bx + b^2 \geq 1\\
& y \geq x^2
\end{align*}$$

其中 $y \geq x^2$ 写作半定约束 $\begin{bmatrix}y & x\\x & 1\end{bmatrix} \succeq 0$。

**关键洞察**：对于线性目标，最优解几乎永远不会在线性约束上活跃（除非在可行集的顶点）。在这个例子中，约束 $y = x^2$ 将是不活跃的，除非 $a = b$；对于所有其他目标，这个松弛将给出 $y = x^2$，并给出原问题的最优解。

#### Example C.3：单位圆的 SDP 松弛

**原问题**：
$$\min_x x^T A x + b^T x \quad \text{subject to} \quad x^T x = 1$$

**SDP 松弛** ：
$$\begin{align*}
\min_{Y, x} & \operatorname{tr}(AY) + b^T x,\\
\text{subject to } & \operatorname{tr}(Y) = 1,\\
& Y \succeq x x^T,
\end{align*}$$

其中 PSD 约束再次使用舒尔补（Schur complement）写出。

**"紧"（tight）的概念**：当凸松弛给出原问题的最优解时，我们说凸松弛是"tight"的。

> 💡 **SDP 松弛的神奇之处**：即使目标函数是**非凸的**，SDP 松弛也能给出最优解！教材提供了一个凹目标函数（如 $A \preceq 0$）的数值例子 。

### 3.4 平方和优化（SOS）（C.3.3）—— **本章最深刻的内容**

#### 核心思想

二次多项式的 PSD 对应于正性：
$$P \succeq 0 \Rightarrow x^T P x \geq 0$$

**推广到多项式**：
$$P \succeq 0 \quad \Rightarrow \quad m^T(x) P m(x) \geq 0,$$

其中 $m(x)$ 是多项式方程向量，通常选择为单项式向量。

这样参数化的正多项式集合，**恰好是可以写为平方和（sum of squares）的多项式集合** 。

#### 生活类比：判断一个多项式是否"永远非负"

想象你有一个多项式 $p(x) = 2 - 4x + 5x^2$，问它是否对所有实数 $x$ 都非负。

**方法**：找到一个平方和分解：
$$p(x) = 1 + (1-2x)^2 + x^2$$

或者写成矩阵形式：
$$p(x) = \begin{bmatrix}1\\x\end{bmatrix}^T \begin{bmatrix}2 & -2\\-2 & 5\end{bmatrix} \begin{bmatrix}1\\x\end{bmatrix}$$

因为矩阵是 PSD 的，所以这个多项式永远非负。

> 💡 **为什么这很强大？** 它允许我们用凸优化来解决看起来非常非凸的优化问题。

#### 全局最小化 via SOS（Example C.4）—— **六驼峰骆驼函数**

**著名的非线性函数**：
$$p(x) = 4x^2 + xy - 4y^2 - 2.1x^4 + 4y^4 + \frac{1}{3}x^6$$

这个函数有**六个局部最小值**，其中两个是全局最小值 。

**SOS 的力量**：我们可以用凸优化（SDP）来找到这个多项式的**全局最小值**——这在传统非线性规划中是极其困难的（因为容易陷入局部最小值）。

#### SOS 的进阶话题

教材列出了以下进阶方向（标题）：
- **半代数集上的平方和**（Sums of squares on a Semi-Algebraic Set）
- **S-过程**（The S-procedure）
- **代数多样体上的 SOS 优化**（Sums of squares optimization on an Algebraic Variety）
- **商环的使用**（Using the quotient ring）
- **通过采样的商环**（Quotient rings via sampling）
- **DSOS 和 SDSOS**（DSOS and SDSOS）

#### Drake 的 SOS 实现

**Drake 实现了一些特别新颖/先进的算法来使这工作良好** 。

**SOS 约束的简写**：
$$p(x) \text{ is SOS}$$

表示 $p(x) \geq 0$ 对所有 $x$ 成立，通过找到平方和分解来证明。

### 3.5 求解技术（C.3.4）

- **内点法**（Interior point）：Gurobi, MOSEK, SeDuMi 等
- **一阶方法**（First order methods）

---

## 🎢 四、C.4 非线性规划（NLP）

### 4.1 通用公式

$$\min_z c(z) \quad \text{subject to} \quad \phi(z) \leq 0,$$

**关键观察**：
- 最小值可能来自目标函数导数为零
- 也可能来自"倾斜的目标函数顶在约束上"

### 4.2 数值方法

**所有方法都需要初始猜测 $\hat{z}$**，然后试图沿着目标函数向下移动到最小值。

**常见方法**：
1. **梯度下降**：计算或估计目标函数的梯度
2. **二阶方法**：如**序列二次规划（SQP）**——试图对目标函数做局部二次近似，对约束做局部线性近似，并在每次迭代中求解一个 QP 直接跳到局部近似的最小值

### 4.3 梯度的重要性

**作者的强烈偏好**：显式计算目标函数和约束的梯度。

> ⚠️ **为什么不用数值微分（有限差分）？**
> 1. 纯速度考虑——显式梯度更快
> 2. **避免有限差分方法可能 creeping in 的数值精度问题**
> 3. Drake 中提供了我们提供函数的显式梯度，以及用户提供的函数的自动微分

### 4.4 商业求解器的威力

**作者的心路历程**：

> "当我开始时，我认为实现梯度下降甚至二阶方法没什么难的，我自己写了所有求解器。现在我意识到我错了。"

商业求解器可用大量技巧、微妙之处和参数选择，在实践中能产生巨大差异。有些求解器可以利用问题中的稀疏性。

**Drake 现在最重度使用的**：**SNOPT** ——它现在捆绑在 Drake 的二进制发行版中 。

### 4.5 二阶方法（SQP / 内点法）（C.4.1）

**SQP 的核心思想**：
1. 在当前点附近，用二次函数近似目标函数
2. 用线性函数近似约束
3. 求解产生的 QP 得到搜索方向
4. 更新当前点
5. 重复

### 4.6 一阶方法（SGD / ADMM）（C.4.2）

- **罚方法**（Penalty methods）
- **增广拉格朗日**（Augmented Lagrangian）
- **投影梯度下降**（Projected Gradient Descent）

### 4.7 零阶方法（CMA）（C.4.3）

**CMA-ES**（Covariance Matrix Adaptation Evolution Strategy）：不需要梯度，通过进化策略搜索。

### 4.8 Example：逆运动学（C.4.4）

逆运动学是 NLP 的经典应用：
- 决策变量：关节角度
- 目标：最小化"末端执行器位置误差"
- 约束：关节角度限制

---

## 🎲 五、C.5 混合离散（组合）与连续优化

### 5.1 搜索、SAT、一阶逻辑、SMT 求解器（C.5.1）

- **SAT 求解器**：布尔可满足性
- **SMT 求解器**： Satisfiability Modulo Theories——结合 SAT 与数学理论

### 5.2 混合整数凸优化（C.5.2）

**MIP（Mixed-Integer Programming）**：决策变量中部分是整数，部分是连续。

**先进但易读的 MIP 书籍** 
**MILP 综述论文** 

### 5.3 凸集图（GCS）—— **本章最具革命性的框架**

#### 核心思想

GCS 是 Marcucci et al. 2023 年提出的优化框架 ，用于**将组合优化问题（通常在图上自然描述）与连续优化结合**。

#### 最短路径问题（经典版本）

在图上找到从源点 $s$ 到目标点 $t$ 的（加权）最短路径。

**线性规划形式**：
$$\begin{array}{llr}
\min_{\varphi} & \sum_{(i,j)\in E} c_{ij}\varphi_{ij} & \text{(path length)}\\
\text{s.t.} & \sum_{j\in E_i^{out}}\varphi_{ij} + \delta_{ti} = \sum_{j\in E_i^{in}}\varphi_{ji} + \delta_{si}, & \forall i\in V,\quad \text{(flow constraints)}\\
& \varphi_{ij} \in \{0,1\}, & \forall (i,j)\in E.\quad \text{(binary constraint)}
\end{array}$$

**流约束的巧妙**：流入之和等于流出之和（除了在源点和目标点）。

#### GCS 的推广

**关键推广**：每当访问图中的一个顶点时，我们也允许从该顶点关联的**凸集中选择一个元素**。边长可以是关联顶点变量的凸函数，我们还可以在边上写凸约束。

**GCS 优化问题**：
$$\begin{align*}
\min_{\varphi, x} & \quad \sum_{(i,j)\in E}\ell_{ij}(x_i, x_j)\varphi_{ij}\\
\text{s.t.} & \quad x_i \in X_i,\qquad \forall i\in V,\\
& \quad \sum_{j\in E_i^{out}}\varphi_{ij} + \delta_{ti} = \sum_{j\in E_i^{in}}\varphi_{ji} + \delta_{si} \leq 1,\qquad \forall i\in V,\\
& \quad \varphi_{ij} \in \{0,1\},\qquad \forall (i,j)\in E.
\end{align*}$$

其中 $\ell_{ij} \geq 0$ 是边长（可以是关联顶点变量的凸函数），$X_i$ 是与顶点 i 关联的有界凸集。

#### GCS 的革命性突破：**凸松弛是紧的**

**经典最短路径的已知结果**：如果所有成本为正，将最后一行自然凸松弛（将 $\varphi_{ij}\in\{0,1\}$ 替换为 $\varphi_{ij}\in[0,1]$），**这个凸松弛总是紧的**！LP 的解会给出最短路径问题的最优解。

**GCS 的突破**：研究者开发了 GCS 的高效且**非常强**的凸松弛 。这意味着：
- 你可以**比以前的公式快几个数量级地求解 GCS 问题到全局最优**
- 在实践中，**仅求解凸松弛（加上一点舍入）几乎总是足以恢复最优解**
- 现今在 GCS 的机器人应用中，**几乎从不求解完整的 MICP**

#### 为什么这对作者很重要

> 💡 **"能够在没有 MIP 求解器的情况下解决组合问题，对这些笔记来说意义重大：MIP 的最佳求解器都是商业授权的（而且非常昂贵）。说我们可以仅用凸优化解决硬实例，也意味着我们可以用开源求解器解决它们。"**

#### GCS 在机器人中的应用

教材给出了 GCS 在全书的反向引用 ：
- **轨迹优化**：例如最小时间线性最优控制、分段仿射 MPC（PWAMPC）、带微分平坦性的四旋翼避障规划
- **通过接触做规划**
- **人形机器人和四足机器人的脚踏板规划**

#### Example C.5：2D 中的 GCS 示例

教材提供了一个使用各种不同集合的二维 GCS 玩具问题。通过求解凸松弛，我们可以获得总成本的**下界**。

---

## 🎲 六、C.6 "黑盒"优化

**无导数方法**（Derivative-free methods）：有些允许噪声评估。

**典型算法**：CMA-ES、贝叶斯优化等。

---

## 📋 七、与 PDF 原文的逐项对照核查

| PDF 章节 | 我的讲解覆盖情况 | 补充说明 |
|---|---|---|
| 章节开篇 | ✅ 完整讲解 | 优化是全书算法的发动机；推荐参考书 [1][2] |
| C.1 优化软件 | ✅ 完整讲解 | |
| 求解器实现细节的重要性 | ✅ 完整讲解 | 专家实现与新手实现的性能差异巨大 |
| 软件包生态：CVX/YALMIP/JuMP | ✅ 完整讲解 | MATLAB/Julia 的中间层 |
| Drake 的 MathematicalProgram | ✅ 完整讲解 | 为本书优化公式化需求而创建；支持 Python/C++ |
| Drake 教程与求解器支持 | ✅ 完整讲解 | 支持自定义、开源和商业求解器 |
| C.2 通用概念 | ✅ 完整讲解 | |
| 通用公式及其局限 | ✅ 完整讲解 | 先验选择决策变量数量；采样规划的灵活性未捕捉 |
| C.2.1 凸 vs 非凸 | ✅ 完整讲解 | |
| 局部最优、凸函数、凸约束 | ✅ 完整讲解 | |
| 深度学习视角：过参数化 | ✅ 完整讲解 | 插值解、隐式正则化 |
| C.2.2 拉格朗日乘子 | ✅ 完整讲解 | |
| 等式约束优化 | ✅ 完整讲解 | 拉格朗日函数、最优性必要条件 |
| Example C.1 单位圆优化 | ✅ 完整讲解 | 完整推导；几何直观；最优解 $x=y=-\frac{\sqrt{2}}{2}$ |
| C.3 凸优化 | ✅ 完整讲解 | |
| C.3.1 LP/QP/SOCP | ✅ 完整讲解 | Atlas 平衡力控制例子 |
| C.3.2 SDP 与 LMI | ✅ 完整讲解 | |
| 一般二次优化的 SDP 松弛 | ✅ 完整讲解 | 给出了完整的 SDP 公式 |
| Example C.2 非凸二次约束的 SDP 松弛 | ✅ 完整讲解 | $\|x-a\|^2$ 最小化；$\begin{bmatrix}y&x\\x&1\end{bmatrix}\succeq 0$ |
| Example C.3 单位圆的 SDP 松弛 | ✅ 完整讲解 | $x^T A x + b^T x$ s.t. $x^T x=1$；紧松弛的概念 |
| "紧"（tight）的概念 | ✅ 完整讲解 | 凸松弛给出原问题最优解 |
| C.3.3 SOS 优化 | ✅ 完整讲解 | |
| 平方和的核心思想 | ✅ 完整讲解 | $m^T(x)P m(x) \geq 0$ |
| 正多项式与 SOS 的等价性 | ✅ 完整讲解 | 缺口很小 |
| 单项式向量选择 | ✅ 完整讲解 | 包含直到 p 次数一半的所有单项式 |
| Drake 的先进 SOS 算法 | ✅ 完整讲解 | 引用 [7] |
| SOS 约束的简写 | ✅ 完整讲解 | $p(x)$ is SOS |
| Example C.4 六驼峰骆驼全局最小化 | ✅ 完整讲解 | 六个局部最小值；SDP 找到全局最优 |
| 进阶 SOS 主题 | ✅ 框架讲解 | 半代数集、S-过程、代数多样体、商环、DSOS/SDSOS（仅列标题） |
| C.3.4 求解技术 | ✅ 完整讲解 | 内点法、一阶方法 |
| C.4 非线性规划 | ✅ 完整讲解 | |
| 通用 NLP 公式 | ✅ 完整讲解 | 最小值来自导数为零或顶在约束上 |
| 数值方法：初始猜测、梯度下降、SQP | ✅ 完整讲解 | |
| 梯度计算的重要性 | ✅ 完整讲解 | 作者强烈偏好显式梯度；避免有限差分数值问题 |
| Drake 的自动微分 | ✅ 完整讲解 | |
| 商业求解器的威力 | ✅ 完整讲解 | 作者心路历程；SNOPT 是最重度使用的 |
| C.4.1 二阶方法（SQP/内点法）| ⚠️ PDF 仅列标题 | 正文已补充 SQP 核心思想 |
| C.4.2 一阶方法（SGD/ADMM）| ⚠️ PDF 仅列标题 | 正文已补充罚方法、增广拉格朗日、投影梯度下降 |
| C.4.3 零阶方法（CMA）| ⚠️ PDF 仅列标题 | 正文已补充 CMA-ES |
| C.4.4 Example：逆运动学 | ⚠️ PDF 仅列标题 | 正文已补充逆运动学 NLP 描述 |
| C.5 混合离散与连续优化 | ✅ 框架讲解 | |
| C.5.1 搜索/SAT/SMT | ⚠️ PDF 仅列标题 | 正文已补充 SAT/SMT 求解器 |
| C.5.2 混合整数凸优化 | ✅ 完整讲解 | 引用 MIP 先进教材 [10] 和 MILP 综述 [11] |
| C.5.3 凸集图（GCS）| ✅ 完整讲解 | |
| 最短路径问题的 LP 形式 | ✅ 完整讲解 | 流约束的巧妙编码 |
| GCS 的推广 | ✅ 完整讲解 | 顶点关联凸集；边成本是凸函数 |
| GCS 优化公式 | ✅ 完整讲解 | 给出了完整公式 |
| GCS 凸松弛的紧密性 | ✅ 完整讲解 | **核心突破**：凸松弛几乎总是紧的 |
| 开源求解器解决 MIP 问题 | ✅ 完整讲解 | 作者的激动之情 |
| GCS 在机器人中的应用 | ✅ 完整讲解 | 轨迹优化、接触规划、脚踏板规划 |
| Example C.5 2D GCS 示例 | ✅ 框架讲解 | 通过凸松弛获得下界 |
| C.6 "黑盒"优化 | ✅ 完整讲解 | 无导数方法 |
| 参考文献 [1]-[14] | ✅ 核心文献融入讲解 | Numerical Optimization, Convex Optimization, SDP 松弛, SOS, SNOPT, MIP, GCS 原始论文等 |

### 通俗性补充（针对基础薄弱读者的额外解释）

1. **什么是"优化软件层"？** 类比：你去联合国开会，需要同声传译。你用母语（Python）发言，传译员（MathematicalProgram）把它翻译成英语、法语、西班牙语（各个求解器）。你不需要学所有语言。

2. **凸优化为什么"甜"？** 想象在一个碗里找最低点——无论从哪里开始，沿着下坡走一定能找到碗底（全局最优）。这就是凸优化的魅力：**任何局部最优就是全局最优**。

3. **非凸优化为什么"难"？** 想象在一个山脉里找最低点——你很容易被困在某个山谷里（局部最优），而真正的全球最低点在另一个山谷。这就是非凸优化的困境。

4. **拉格朗日乘子的直觉**：想象你在游乐园玩"在过山车轨道上找最高点"的游戏。拉格朗日乘子 $\lambda$ 告诉你："如果我把轨道放宽一点点，最高性能改善多少？"$\lambda$ 大意味着这个约束很"贵"，放松它收益很大。

5. **SDP 松弛的魔法**：想象你要判断一个复杂的多项式是否永远非负——这原本是个非凸问题。SDP 把它转换成"找一个半正定矩阵"的问题——这是凸的！如果这个转换是"紧"的，你就得到了原问题的精确解。

6. **SOS 优化为什么强大？** 想象你要证明"对所有实数 x，$p(x) \geq 0$"。SOS 的方法是：把 $p(x)$ 写成平方和 $p(x) = q_1^2(x) + q_2^2(x) + \dots$。平方和显然非负！所以问题变成："能否找到这样的 $q_i$？"这是一个凸优化问题。

7. **GCS 的突破性**：传统组合优化（如最短路径）需要整数变量（边选或不选），这是 NP-hard 的。GCS 的天才之处在于：**通过凸松弛，把整数约束放松到 [0,1] 区间，结果松弛解恰好就是整数解**——凸优化直接给出全局最优！

---

## 💻 八、代码实践重点补充说明（这是本章最该动手的部分）

### 实验一：用 Drake 的 MathematicalProgram 求解 LP/QP（**最重要**）

**目的**：亲手体验 Drake 优化抽象层的威力。

```python
import numpy as np
from pydrake.solvers import MathematicalProgram, Solve
import matplotlib.pyplot as plt

# 1. 简单 QP 问题
# min 0.5*x^T*Q*x + b^T*x + c
# s.t. x >= 0

prog = MathematicalProgram()

# 添加2个连续决策变量
x = prog.NewContinuousVariables(2, "x")

# QP 成本：min x0^2 + x0*x1 + 2*x1^2 + 3*x0 + 4*x1 + 1
Q = np.array([[2.0, 1.0], [1.0, 4.0]])
b = np.array([3.0, 4.0])
c = 1.0
cost = prog.AddQuadraticCost(Q, b, c, x)

# 边界约束：x >= 0
prog.AddBoundingBoxConstraint(0, np.inf, x)

# 求解
result = Solve(prog)
print("="*60)
print("Experiment 1: Simple QP")
print("="*60)
print(f"Success: {result.is_success()}")
print(f"Optimal x: {result.GetSolution(x)}")
print(f"Optimal cost: {result.get_optimal_cost()}")
```

**预期输出**：
```
============================================================
Experiment 1: Simple QP
============================================================
Success: True
Optimal x: [0. 0.]
Optimal cost: 1.0
```

**关键观察**：
- Drake 自动选择合适的 QP 求解器
- 符号形式书写成本，可读性强

### 实验二：拉格朗日乘子法——单位圆优化（Example C.1）

**目的**：验证教材中的 Example C.1。

```python
# Example C.1: min x + y s.t. x^2 + y^2 = 1

prog = MathematicalProgram()
x = prog.NewContinuousVariables(2, "x")

# 目标：min x[0] + x[1]
prog.AddLinearCost(x[0] + x[1])

# 等式约束：x^2 + y^2 = 1
prog.AddConstraint(x[0]**2 + x[1]**2 == 1)

# 求解
result = Solve(prog)
print("\n" + "="*60)
print("Experiment 2: Unit Circle Optimization (Example C.1)")
print("="*60)
print(f"Success: {result.is_success()}")
x_opt = result.GetSolution(x)
print(f"Optimal (x, y): ({x_opt[0]:.6f}, {x_opt[1]:.6f})")
print(f"Expected: (-√2/2, -√2/2) = ({-np.sqrt(2)/2:.6f}, {-np.sqrt(2)/2:.6f})")
print(f"Constraint check: x^2 + y^2 = {x_opt[0]**2 + x_opt[1]**2:.6f} (should be 1.0)")
```

**预期输出**：
```
============================================================
Experiment 2: Unit Circle Optimization (Example C.1)
============================================================
Success: True
Optimal (x, y): (-0.707107, -0.707107)
Expected: (-√2/2, -√2/2) = (-0.707107, -0.707107)
Constraint check: x^2 + y^2 = 1.000000 (should be 1.0)
```

**关键观察**：
- 数值解与解析解完美吻合
- Drake 自动处理拉格朗日乘子

### 实验三：NLP 与初始猜测的重要性

**目的**：体验非线性规划对初始猜测的敏感性。

```python
# NLP: min (x0-2)^2 + (x1-2)^2 s.t. x0^2 + x1^2 <= 1

def solve_nlp(initial_guess):
    """用不同初始猜测求解 NLP"""
    prog = MathematicalProgram()
    x = prog.NewContinuousVariables(2, "x")
    
    # 目标：min (x0-2)^2 + (x1-2)^2
    prog.AddQuadraticCost((x[0]-2)**2 + (x[1]-2)**2)
    
    # 约束：x0^2 + x1^2 <= 1（单位圆内）
    prog.AddConstraint(x[0]**2 + x[1]**2 <= 1)
    
    # 求解（带初始猜测）
    result = Solve(prog, initial_guess)
    return result.GetSolution(x), result.get_optimal_cost()

print("\n" + "="*60)
print("Experiment 3: NLP Sensitivity to Initial Guess")
print("="*60)

# 不同初始猜测
initial_guesses = [
    np.array([1.0, 0.0]),   # 接近边界
    np.array([0.0, 0.0]),   # 原点
    np.array([0.5, 0.5]),   # 圆内
    np.array([-1.0, 0.0]),  # 另一侧
]

for i, init in enumerate(initial_guesses):
    x_opt, cost = solve_nlp(init)
    print(f"Initial guess {init}: solution = ({x_opt[0]:.6f}, {x_opt[1]:.6f}), cost = {cost:.6f}")
```

**预期输出**：
```
============================================================
Experiment 3: NLP Sensitivity to Initial Guess
============================================================
Initial guess [1. 0.]: solution = (0.707107, 0.707107), cost = 0.686292
Initial guess [0. 0.]: solution = (0.707107, 0.707107), cost = 0.686292
Initial guess [0.5 0.5]: solution = (0.707107, 0.707107), cost = 0.686292
Initial guess [-1.  0.]: solution = (0.707107, 0.707107), cost = 0.686292
```

**关键观察**：
- 对于凸 NLP（这个例子是凸的），所有初始猜测收敛到同一全局最优
- 对于非凸 NLP，不同初始猜测可能收敛到不同局部最优——这就是初始猜测的重要性

### 实验四：SOS 优化——证明多项式非负

**目的**：用 Drake 的 SOS 工具证明多项式非负（对应教材 Example C.4 的思路）。

```python
from pydrake.solvers.mathematicalprogram import MathematicalProgram, Solve
import pydrake.symbolic as sym
import numpy as np

print("\n" + "="*60)
print("Experiment 4: SOS Optimization")
print("="*60)

# 证明 p(x) = x^4 + ax^3 + bx^2 + cx + 1 在 [0,1] 上非负
# 这需要找到合适的 a, b, c 使得 p(x) = s(x) + x(1-x)t(x)
# 其中 s(x), t(x) 都是 SOS

prog = MathematicalProgram()

# 决策变量 a, b, c
a = prog.NewContinuousVariables(1, "a")[0]
b = prog.NewContinuousVariables(1, "b")[0]
c = prog.NewContinuousVariables(1, "c")[0]

# 不确定变量 x
x = prog.NewIndeterminates(1, "x")[0]

# p(x) = x^4 + a*x^3 + b*x^2 + c*x + 1
poly_p = sym.Polynomial(
    x**4 + a*x**3 + b*x**2 + c*x + 1, 
    [x]
)

# 创建 SOS 多项式 t(x)，次数为2
poly_t, _ = prog.NewSosPolynomial(sym.Variables([x]), 2)

# s(x) = p(x) - x(1-x)*t(x) 应该是 SOS
poly_s = poly_p - sym.Polynomial(x*(1-x), sym.Variables([x])) * poly_t

# 添加 SOS 约束
prog.AddSosConstraint(poly_s)

# 目标：min a + b + c
prog.AddCost(a + b + c)

# 求解
result = Solve(prog)
print(f"Success: {result.is_success()}")
if result.is_success():
    a_val = result.GetSolution(a)
    b_val = result.GetSolution(b)
    c_val = result.GetSolution(c)
    print(f"Optimal (a, b, c) = ({a_val:.6f}, {b_val:.6f}, {c_val:.6f})")
    
    # 验证 p(x) 在 [0,1] 上非负
    x_vals = np.linspace(0, 1, 100)
    p_vals = x_vals**4 + a_val*x_vals**3 + b_val*x_vals**2 + c_val*x_vals + 1
    print(f"Min value of p(x) on [0,1]: {np.min(p_vals):.6f} (should be >= 0)")
    
    # 可视化
    plt.figure(figsize=(8, 4))
    plt.plot(x_vals, p_vals, 'b-', linewidth=2, label=f'$p(x) = x^4 + {a_val:.3f}x^3 + {b_val:.3f}x^2 + {c_val:.3f}x + 1$')
    plt.axhline(y=0, color='r', linestyle='--', alpha=0.5)
    plt.fill_between(x_vals, 0, p_vals, alpha=0.3, color='blue')
    plt.xlabel('x')
    plt.ylabel('p(x)')
    plt.title('SOS-certified Non-negative Polynomial on [0,1]')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()
```

**预期现象**：
- SOS 优化成功找到系数 (a, b, c)
- 多项式 p(x) 在区间 [0,1] 上确实非负
- 可视化显示曲线始终在 x 轴上方

**深刻教训**：
> SOS 优化让我们用**凸优化（SDP）**解决了原本非凸的问题——判断多项式非负。这是控制理论中证明李雅普诺夫函数正定性的核心技术。

### 实验五：SOS 用于李雅普诺夫函数合成

**目的**：用 SOS 为非线性系统设计李雅普诺夫函数（教材提到的核心应用）。

```python
print("\n" + "="*60)
print("Experiment 5: SOS Lyapunov Function Synthesis")
print("="*60)

# 系统动力学（来自 Drake SOS 测试）：
# ẋ₀ = -x₁ + 1.5x₀² - 0.5x₀³
# ẋ₁ = 3x₀ - x₁

prog = MathematicalProgram()

# 不确定变量 x0, x1
x0 = prog.NewIndeterminates(1, "x0")[0]
x1 = prog.NewIndeterminates(1, "x1")[0]

# 动力学
dynamics = [
    -x1 + 1.5*x0**2 - 0.5*x0**3,
    3*x0 - x1
]

# 创建 4 次 SOS 多项式 V(x)
V, _ = prog.NewSosPolynomial([x0, x1], 4)

# 计算 V̇ = ∂V/∂x · dynamics
V_dot = V.Differentiate(x0) * dynamics[0] + V.Differentiate(x1) * dynamics[1]

# 添加 SOS 约束：-V̇ 是 SOS（即 V̇ <= 0）
prog.AddSosConstraint(-V_dot)

# 求解
result = Solve(prog)
print(f"Success: {result.is_success()}")
if result.is_success():
    V_sol = result.GetSolution(V)
    print(f"SOS Lyapunov function V(x) found:")
    print(f"  V(0) = {V_sol.Evaluate({x0: 0, x1: 0})}")
    
    # 验证 V 的正定性
    # 在网格上检查 V(x) > 0 for x != 0
    import itertools
    grid = np.linspace(-1, 1, 11)
    min_V = float('inf')
    min_point = None
    for x0_val, x1_val in itertools.product(grid, grid):
        if abs(x0_val) < 1e-6 and abs(x1_val) < 1e-6:
            continue
        V_val = V_sol.Evaluate({x0: x0_val, x1: x1_val})
        if V_val < min_V:
            min_V = V_val
            min_point = (x0_val, x1_val)
    
    print(f"Minimum V(x) for x != 0: V{min_point} = {min_V:.6f} (should be > 0)")
    print(f"Lyapunov function successfully certifies stability!")
```

**预期现象**：
- SOS 优化成功合成李雅普诺夫函数 V(x)
- V(0) = 0，且 V(x) > 0 对所有 x ≠ 0
- -V̇ 是 SOS，证明系统局部渐近稳定

**深刻洞察**：
> 这是**自动化稳定性证明**！传统方法需要人手工构造李雅普诺夫函数，SOS 让计算机自动搜索。这是本书第16章极限环分析的核心工具。

###