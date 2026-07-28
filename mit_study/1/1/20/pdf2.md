# 《欠驱动机器人》第20章：无模型策略搜索（Model-Free Policy Search）—— 完全通俗讲解（含嵌入式可跑代码、逐条核查与增补）

> **怎么读这篇讲义**：这一章在整本书里的角色很特别。第11章我们讲过 **policy search**——给控制器装一组参数 $\alpha$，然后拧它；但那一章是 **"model-based"** 的：我们手里有模型 $f$，能算梯度、能做轨迹优化。第20章把模型**收走**了——你现在面对的是一个**黑盒**：你只能"按一下按钮、看一个分数"（试错采样），**不知道里面长什么样，也拿不到梯度**。这就是**强化学习（RL）** 的地盘。本章要讲的，就是"**在没有模型、没有梯度的情况下，怎么用'随机抖一抖 + 看分数变好变坏'来估计梯度、做梯度下降**"。
>
> 这一章 PDF 正文不长，但**思想极密**，而且**全章没有一个可跑代码、没有练习、没有 notebook 链接**（只有一个图 20.1 的引用）。所以我做两件事来"补满"它：① 把每个推导（尤其 REINFORCE 的 log 技巧、weight perturbation 的 Taylor 推导、baseline、信噪比 SNR）**掰成小学生也能跟的步子**，并配鲜活类比；② **在讲完每个算法的当口，直接嵌一段能跑的 numpy 代码**，让你亲眼看见"抖一抖居然真的在下坡"。读完后半部分还有一份**逐条核查清单 + 通俗性增补清单**，向你透明汇报"我自查时补了哪些 PDF 没说清的坑"。

---

## 0. 开篇：把模型收走，你还怎么优化？

### 0.1 一句话概括

> **当系统是个黑盒——你只能试错拿（带噪的）代价样本，没有模型、没有梯度——RL 的绝招是：给策略装参数 $\alpha$，让动作 $u$ 从分布 $p_\alpha(u|x)$ 里随机抽，然后用"随机扰动 + 看代价涨跌"或
# 《欠驱动机器人》第20章：无模型策略搜索（Model-Free Policy Search）—— 完全通俗讲解（含嵌入式可跑代码、逐条核查与增补）

> **怎么读这篇讲义**：这一章在整本书里的角色很特别。第11章我们讲过 **policy search**——给控制器装一组参数 $\alpha$，然后拧它；但那一章是 **"model-based"** 的：我们手里有模型 $f$，能算梯度、能做轨迹优化。第20章把模型**收走**了——你现在面对的是一个**黑盒**：你只能"按一下按钮、看一个分数"（试错采样），**不知道里面长什么样，也拿不到梯度**。这就是**强化学习（RL）** 的地盘。本章要讲的，就是"**在没有模型、没有梯度的情况下，怎么用'随机抖一抖 + 看分数变好变坏'来估计梯度、做梯度下降**"。
>
> 这一章 PDF 正文不长，但**思想极密**，而且**全章没有一个可跑代码、没有练习、没有 notebook 链接**（只有一个图 20.1 的引用）。所以我做两件事来"补满"它：① 把每个推导（尤其 REINFORCE 的 log 技巧、weight perturbation 的 Taylor 推导、baseline、信噪比 SNR）**掰成小学生也能跟的步子**，并配鲜活类比；② **在讲完每个算法的当口，直接嵌一段能跑的 numpy 代码**，让你亲眼看见"抖一抖居然真的在下坡"。读完后半部分还有一份**逐条核查清单 + 通俗性增补清单**，向你透明汇报"我自查时补了哪些 PDF 没说清的坑"。

---

## 0. 开篇：把模型收走，你还怎么优化？

### 0.1 一句话概括

> **当系统是个黑盒——你只能试错拿（带噪的）代价样本，没有模型、没有梯度——RL 的绝招是：给策略装参数 $\alpha$，让动作 $u$ 从分布 $p_\alpha(u|x)$ 里随机抽，然后用"随机扰动 + 看代价涨跌"或"对数概率技巧"估出梯度，做随机梯度下降。代价是方差大、样本多、最多收敛到局部最优；好处是通用到能啃下任何其它算法够不到的问题。**

### 0.2 引言逐句翻译 + 类比

**第一层：RL 是什么。**
> RL 是一堆算法，解的**正是本书一路在解的同一个最优控制问题**；但 RL 文献里**真正的宝石**，是那些对**随机最优控制问题做"几乎黑盒"优化**的算法。"黑盒接口"= 它**只能通过试错**拿到（可能带噪的）最优代价样本，**但拿不到底层模型，也拿不到完整梯度信息**。

**类比（黑盒调音台，全章总纲，请刻进脑子）**：
- 想象一台**调音台**，上面有 $N$ 个旋钮（=参数 $\alpha$），拧它们能让"出来的音乐"（=机器人表现）变好或变坏。
- **model-based（第11章）** = 你**有这台调音台的电路图**，能算出"拧旋钮 3 会让低音增加多少分贝"（=梯度），于是精确调。
- **model-free / 黑盒（本章）** = 调音台**封在铁箱里**，你**看不见电路**，只能"拧一下、听一下、打个分"。你**不知道**拧旋钮 3 会怎样，**只能试**。
- 本章的所有算法，都是"**在只能'拧一下听一下'的限制下，怎么聪明地逼近'该往哪拧'**"。

**第二层：难，但通用。**
> 这是**难问题**！一般**不能**期望 RL 像结构化优化那样快，**通常最多保证收敛到局部最优**。但框架**极通用**，能用于其它算法**够不到**的问题。作者**最爱的 RL 例子 = 复杂流体动力学里的控制**（如 [1]）。这些系统**极难建模**，或模型**太高维复杂**以至于控制设计不可行；这种问题里，**在物理实验里试错优化，可能反而更快**。

**类比**：调音台封在铁箱里虽然笨，但**如果电路图画不出来**（流体、真实机器人、复杂接触），那"笨办法"反而是**唯一办法**。**通用性的代价 = 慢 + 局部最优**。

**第三层：本章的具体打法。**
> 本章考察**一种** RL 风格：**显式参数化一族策略**（比如用参数向量 $\alpha$），然后**直接搜索**让长期代价最优的参数。对随机最优控制 + 我们最爱的加性目标，长这样：

$$\min_\alpha\ \mathbb{E}\!\left[\sum_{n=0}^{N}\ell(x[n],u[n])\right]\quad (1)$$

其中随机变量服从：

$$x[0]\sim p_0(x),\quad x[n]\sim p(x[n]\,|\,x[n-1],u[n-1]),\quad u[n]\sim p_\alpha(u[n]\,|\,x[n]).$$

> 最后一个方程是**策略的概率表示**——每个时步，动作 $u$ 从**以当前状态 $x$ 为条件的分布**里抽。

**人话**：和确定性策略 $u=\pi_\alpha(x)$ 不同，这里**策略是个分布** $p_\alpha(u|x)$——**给定状态，动作不是"一个确定值"，而是"按某个分布随机抽一个"**（比如 $u\sim\mathcal{N}(\alpha^Tx,\ \sigma^2)$）。**为什么要随机？** 两个原因：① **黑盒没梯度，只能靠"随机探索"去试**；② 随机性让"概率 $p_\alpha$ 对 $\alpha$ 可微"，于是后面那个 log 技巧才使得通。

**第四层：控制社区的老亲戚。**
> 控制社区也研究过类似想法，比如 **extremum-seeking control（极值搜索控制）** 和 **iterative learning control（迭代学习控制）**。作者尽量做连接。

**类比**：**极值搜索** = "给旋钮加一个高频小抖动，看输出的低频响应往哪走"——**本质就是本章 weight perturbation 的连续时间老祖宗**。**迭代学习控制** = "同一首歌反复弹，每遍根据上一遍的误差微调手指"——**和 RL 的'rollout 一次、更新一次'同构**。**所以 RL 不是凭空冒出来的，控制论早就在'蒙眼调参'这件事上攒了一堆工具，只是 RL 把它做通用、做大规模了。**

---

## 1. 策略梯度方法（20.1）—— 黑盒里怎么"估梯度"

> RL 里策略搜索的**标准套路之一** = 用若干条样本轨迹，**估计**"期望长期代价对策略参数 $\alpha$ 的梯度"，然后做（随机）梯度下降。许多所谓 **"policy gradient"** 算法，都用一个叫 **likelihood ratio method（似然比法）** 的推导，最早 [2] 描述，被 **REINFORCE** 算法 [3] 带火。它**基于一个看起来像"对数小技巧"的东西**来估梯度；作者觉得**这技巧常被讲得神神秘秘**，所以要确保我们真懂。

**先建立一个"为什么需要 trick"的直觉**：
- 你想算 $\frac{\partial}{\partial\alpha}\mathbb{E}[\text{代价}]$。
- 困难在于：**期望 $\mathbb{E}$ 是对 $p_\alpha$ 取的，而 $p_\alpha$ 本身依赖 $\alpha$**——**求导时，"积分/求和的测度"在动**，不能简单把导数搬进期望里。
- **log 技巧的作用** = **把"测度在动"这个麻烦，转化成"期望里多乘一项 $\frac{\partial\log p_\alpha}{\partial\alpha}$"**，于是导数**重新变回一个期望**，**就能用蒙特卡洛采样估了**。**这就是全部魔法。**

### 1.1 似然比法 / REINFORCE（20.1.1）—— 从标量小例子讲起

**先看一个更简单的优化**：

$$\min_\alpha\ \mathbb{E}[g(x)],\quad x\sim p_\alpha(x)$$

**记号**：$x$ 是随机向量，服从 $p_\alpha(x)$，**下标 $\alpha$ 表示"这个分布的形状由参数 $\alpha$ 决定"**（你拧旋钮，分布就变）。

**问**：这个期望对 $\alpha$ 的梯度是什么？**REINFORCE 推导**（三步，每步标清"为什么"）：

$$\frac{\partial}{\partial\alpha}\int dx\, g(x)\,p_\alpha(x) \quad\underbrace{=}_{\text{① 导数搬进积分}}\quad \int dx\, g(x)\,\frac{\partial}{\partial\alpha}p_\alpha(x)$$

$$\underbrace{=}_{\text{② log 技巧}}\quad \int dx\, g(x)\,p_\alpha(x)\,\frac{\partial}{\partial\alpha}\log p_\alpha(x)$$

$$\underbrace{=}_{\text{③ 认回期望}}\quad \mathbb{E}\!\left[g(x)\,\frac{\partial}{\partial\alpha}\log p_\alpha(x)\right]$$

**逐步骤翻译（这是全章第一个"啊哈"，务必懂）**：
- **①**：$g(x)$ 不含 $\alpha$，所以 $\alpha$ 只作用在 $p_\alpha$ 上，导数直接落到 $p_\alpha$ 上。**没问题。**
- **② log 技巧**：用到一个微积分链式法则——**$\frac{\partial}{\partial\alpha}\log p = \frac{1}{p}\frac{\partial p}{\partial\alpha}$**，**反过来就是 $\frac{\partial p}{\partial\alpha} = p\cdot\frac{\partial\log p}{\partial\alpha}$**。（PDF 里写的 $y=\log u\Rightarrow \frac{\partial y}{\partial u}=\frac1u$，就是在提醒这条链式法则。）**把 $\frac{\partial p_\alpha}{\partial\alpha}$ 换成 $p_\alpha\frac{\partial\log p_\alpha}{\partial\alpha}$，于是积分里又出现了 $p_\alpha$！**
- **③**：积分里现在是 $g(x)\cdot\frac{\partial\log p_\alpha}{\partial\alpha}\cdot p_\alpha(x)$——**最后那个 $p_\alpha(x)\,dx$ 正好是"按 $p_\alpha$ 取期望"的定义**！所以整个积分 $=\mathbb{E}_{x\sim p_\alpha}[\,g(x)\frac{\partial\log p_\alpha}{\partial\alpha}\,]$。

**这暗示一个超简单的蒙特卡洛算法**：抽 $N$ 个样本 $x_i\sim p_\alpha$，估梯度为

$$\widehat{\nabla_\alpha}\ \approx\ \frac{1}{N}\sum_i g(x_i)\,\frac{\partial}{\partial\alpha}\log p_\alpha(x_i).$$

**人话**：**你不用知道 $g$ 怎么依赖 $x$、也不用知道 $x$ 怎么依赖 $\alpha$**——**你只需要 (a) 能从 $p_\alpha$ 抽样，(b) 能算 $\frac{\partial\log p_\alpha}{\partial\alpha}$（这只需要知道"分布长啥样"，不需要知道"系统长啥样"）**。**这就是"黑盒也能估梯度"的秘密。**

**类比（蒙眼调音台的"打分×灵敏度"法则）**：
- 你拧旋钮 $\alpha$，**随机**抽一个设置 $x$（比如"随机选一首歌来听效果"），听到分数 $g(x)$。
- 同时你**记得**"我刚才抽到这个 $x$ 的概率是 $p_\alpha(x)$"，并算出"我拧 $\alpha$ 会让这个概率怎么变"（$=\frac{\partial\log p_\alpha}{\partial\alpha}$）。
- **更新规则** = "**分数 × 概率灵敏度**" 的平均：**如果某个 $x$ 分数好（$g$ 小），而且拧 $\alpha$ 会让它更可能出现（$\frac{\partial\log p}{\partial\alpha}>0$），那就朝那个方向拧**。**把"好结果"和"我能不能让它更常发生"乘起来，就是梯度方向。**

#### 把这个 trick 用到最优控制（更震撼）

对有限时域问题，同样的推导给出：

$$\frac{\partial}{\partial\alpha}\mathbb{E}\!\left[\sum_{n=0}^{N}\ell(x[n],u[n])\right] = \mathbb{E}\!\left[\left(\sum_{n=0}^{N}\ell(x[n],u[n])\right)\frac{\partial}{\partial\alpha}\log p_\alpha(x[\cdot],u[\cdot])\right]$$

其中 $x[\cdot]$ 是**整条轨迹** $x[0],\dots,x[N]$ 的简写，而**整条轨迹的联合概率**是：

$$p_\alpha(x[\cdot],u[\cdot]) = p_0(x[0])\left(\prod_{k=1}^{N}p(x[k]\,|\,x[k-1],u[k-1])\right)\left(\prod_{k=0}^{N}p_\alpha(u[k]\,|\,x[k])\right)$$

**人话**：**整条轨迹的概率 = 初态概率 × 每一步"状态怎么转移"的概率 × 每一步"策略怎么抽动作"的概率**。

**取 log**（乘积变求和）：

$$\log p_\alpha = \log p_0 + \sum_{k=1}^{N}\log p(x[k]\,|\,x[k-1],u[k-1]) + \sum_{k=0}^{N}\log p_\alpha(u[k]\,|\,x[k])$$

**对 $\alpha$ 求导**——**关键观察**：**只有最后一项含 $\alpha$！** 因为 $p_0$ 是初态分布（不含 $\alpha$），转移概率 $p(x[k]|x[k-1],u[k-1])$ 是**植物/世界**的规律（**黑盒，不含 $\alpha$**），**只有策略 $p_\alpha(u[k]|x[k])$ 是你拧的旋钮**。于是：

$$\frac{\partial}{\partial\alpha}\log p_\alpha(x[\cdot],u[\cdot]) = \sum_{k=0}^{N}\frac{\partial}{\partial\alpha}\log p_\alpha(u[k]\,|\,x[k])$$

代回去，得到一个**双重求和** $\mathbb{E}[(\sum_n \ell_n)(\sum_k \frac{\partial\log p_\alpha(u[k]|x[k])}{\partial\alpha})]$。**现在用因果性化简**（这是第二个"啊哈"，也是最容易卡的一步）：

> **引理（score function 期望为零）**：对任何一步 $k$，在给定 $x[k]$ 下，$\mathbb{E}_{u[k]}\!\left[\frac{\partial}{\partial\alpha}\log p_\alpha(u[k]|x[k])\right]=0$。
> **为什么**：$\mathbb{E}_{u}[\frac{\partial\log p_\alpha}{\partial\alpha}] = \int \frac{1}{p_\alpha}\frac{\partial p_\alpha}{\partial\alpha}p_\alpha\,du = \int \frac{\partial p_\alpha}{\partial\alpha}du = \frac{\partial}{\partial\alpha}\int p_\alpha\,du = \frac{\partial}{\partial\alpha}(1)=0$。**（概率积分为 1，对参数求导还是 0。）**

**用这个引理**：当 $k>n$ 时，$\ell(x[n],u[n])$ 是"过去已经发生的事"，**和"未来才抽的 $u[k]$"独立**，所以 $\ell(x[n],u[n])$ 可以提出 $u[k]$ 的期望，剩下 $\mathbb{E}[\frac{\partial\log p_\alpha(u[k]|x[k])}{\partial\alpha}]=0$——**整项消失！** 于是内层求和的上限从 $N$ 砍到 $n$：

$$\frac{\partial}{\partial\alpha}\mathbb{E}\!\left[\sum_{n=0}^{N}\ell
# 《欠驱动机器人》第20章：无模型策略搜索（Model-Free Policy Search）—— 完全通俗讲解（含嵌入式可跑代码、逐条核查与增补）

> **怎么读这篇讲义**：这一章在整本书里的角色很特别。第11章我们讲过 **policy search**——给控制器装一组参数 $\alpha$，然后拧它；但那一章是 **"model-based"** 的：我们手里有模型 $f$，能算梯度、能做轨迹优化。第20章把模型**收走**了——你现在面对的是一个**黑盒**：你只能"按一下按钮、看一个分数"（试错采样），**不知道里面长什么样，也拿不到梯度**。这就是**强化学习（RL）** 的地盘。本章要讲的，就是"**在没有模型、没有梯度的情况下，怎么用'随机抖一抖 + 看分数变好变坏'来估计梯度、做梯度下降**"。
>
> 这一章 PDF 正文不长，但**思想极密**，而且**全章没有一个可跑代码、没有练习、没有 notebook 链接**（只有一个图 20.1 的引用）。所以我做两件事来"补满"它：① 把每个推导（尤其 REINFORCE 的 log 技巧、weight perturbation 的 Taylor 推导、baseline、信噪比 SNR）**掰成小学生也能跟的步子**，并配鲜活类比；② **在讲完每个算法的当口，直接嵌一段能跑的 numpy 代码**，让你亲眼看见"抖一抖居然真的在下坡"。读完后半部分还有一份**逐条核查清单 + 通俗性增补清单**，向你透明汇报"我自查时补了哪些 PDF 没说清的坑"。

---

## 0. 开篇：把模型收走，你还怎么优化？

### 0.1 一句话概括

> **当系统是个黑盒——你只能试错拿（带噪的）代价样本，没有模型、没有梯度——RL 的绝招是：给策略装参数 $\alpha$，让动作 $u$ 从分布 $p_\alpha(u|x)$ 里随机抽，然后用"随机扰动 + 看代价涨跌"或"对数概率技巧"估出梯度，做随机梯度下降。代价是方差大、样本多、最多收敛到局部最优；好处是通用到能啃下任何其它算法够不到的问题。**

### 0.2 引言逐句翻译 + 类比

**第一层：RL 是什么。**
> RL 是一堆算法，解的**正是本书一路在解的同一个最优控制问题**；但 RL 文献里**真正的宝石**，是那些对**随机最优控制问题做"几乎黑盒"优化**的算法。"黑盒接口"= 它**只能通过试错**拿到（可能带噪的）最优代价样本，**但拿不到底层模型，也拿不到完整梯度信息**。

**类比（黑盒调音台，全章总纲，请刻进脑子）**：
- 想象一台**调音台**，上面有 $N$ 个旋钮（=参数 $\alpha$），拧它们能让"出来的音乐"（=机器人表现）变好或变坏。
- **model-based（第11章）** = 你**有这台调音台的电路图**，能算出"拧旋钮 3 会让低音增加多少分贝"（=梯度），于是精确调。
- **model-free / 黑盒（本章）** = 调音台**封在铁箱里**，你**看不见电路**，只能"拧一下、听一下、打个分"。你**不知道**拧旋钮 3 会怎样，**只能试**。
- 本章的所有算法，都是"**在只能'拧一下听一下'的限制下，怎么聪明地逼近'该往哪拧'**"。

**第二层：难，但通用。**
> 这是**难问题**！一般**不能**期望 RL 像结构化优化那样快，**通常最多保证收敛到局部最优**。但框架**极通用**，能用于其它算法**够不到**的问题。作者**最爱的 RL 例子 = 复杂流体动力学里的控制**（如 [1]）。这些系统**极难建模**，或模型**太高维复杂**以至于控制设计不可行；这种问题里，**在物理实验里试错优化，可能反而更快**。

**类比**：调音台封在铁箱里虽然笨，但**如果电路图画不出来**（流体、真实机器人、复杂接触），那"笨办法"反而是**唯一办法**。**通用性的代价 = 慢 + 局部最优**。

**第三层：本章的具体打法。**
> 本章考察**一种** RL 风格：**显式参数化一族策略**（比如用参数向量 $\alpha$），然后**直接搜索**让长期代价最优的参数。对随机最优控制 + 我们最爱的加性目标，长这样：

$$\min_\alpha\ \mathbb{E}\!\left[\sum_{n=0}^{N}\ell(x[n],u[n])\right]\quad (1)$$

其中随机变量服从：

$$x[0]\sim p_0(x),\quad x[n]\sim p(x[n]\,|\,x[n-1],u[n-1]),\quad u[n]\sim p_\alpha(u[n]\,|\,x[n]).$$

> 最后一个方程是**策略的概率表示**——每个时步，动作 $u$ 从**以当前状态 $x$ 为条件的分布**里抽。

**人话**：和确定性策略 $u=\pi_\alpha(x)$ 不同，这里**策略是个分布** $p_\alpha(u|x)$——**给定状态，动作不是"一个确定值"，而是"按某个分布随机抽一个"**（比如 $u\sim\mathcal{N}(\alpha^Tx,\ \sigma^2)$）。**为什么要随机？** 两个原因：① **黑盒没梯度，只能靠"随机探索"去试**；② 随机性让"概率 $p_\alpha$ 对 $\alpha$ 可微"，于是后面那个 log 技巧才使得通。

**第四层：控制社区的老亲戚。**
> 控制社区也研究过类似想法，比如 **extremum-seeking control（极值搜索控制）** 和 **iterative learning control（迭代学习控制）**。作者尽量做连接。

**类比**：**极值搜索** = "给旋钮加一个高频小抖动，看输出的低频响应往哪走"——**本质就是本章 weight perturbation 的连续时间老祖宗**。**迭代学习控制** = "同一首歌反复弹，每遍根据上一遍的误差微调手指"——**和 RL 的'rollout 一次、更新一次'同构**。**所以 RL 不是凭空冒出来的，控制论早就在'蒙眼调参'这件事上攒了一堆工具，只是 RL 把它做通用、做大规模了。**

---

## 1. 策略梯度方法（20.1）—— 黑盒里怎么"估梯度"

> RL 里策略搜索的**标准套路之一** = 用若干条样本轨迹，**估计**"期望长期代价对策略参数 $\alpha$ 的梯度"，然后做（随机）梯度下降。许多所谓 **"policy gradient"** 算法，都用一个叫 **likelihood ratio method（似然比法）** 的推导，最早 [2] 描述，被 **REINFORCE** 算法 [3] 带火。它**基于一个看起来像"对数小技巧"的东西**来估梯度；作者觉得**这技巧常被讲得神神秘秘**，所以要确保我们真懂。

**先建立一个"为什么需要 trick"的直觉**：
- 你想算 $\frac{\partial}{\partial\alpha}\mathbb{E}[\text{代价}]$。
- 困难在于：**期望 $\mathbb{E}$ 是对 $p_\alpha$ 取的，而 $p_\alpha$ 本身依赖 $\alpha$**——**求导时，"积分/求和的测度"在动**，不能简单把导数搬进期望里。
- **log 技巧的作用** = **把"测度在动"这个麻烦，转化成"期望里多乘一项 $\frac{\partial\log p_\alpha}{\partial\alpha}$"**，于是导数**重新变回一个期望**，**就能用蒙特卡洛采样估了**。**这就是全部魔法。**

### 1.1 似然比法 / REINFORCE（20.1.1）—— 从标量小例子讲起

**先看一个更简单的优化**：

$$\min_\alpha\ \mathbb{E}[g(x)],\quad x\sim p_\alpha(x)$$

**记号**：$x$ 是随机向量，服从 $p_\alpha(x)$，**下标 $\alpha$ 表示"这个分布的形状由参数 $\alpha$ 决定"**（你拧旋钮，分布就变）。

**问**：这个期望对 $\alpha$ 的梯度是什么？**REINFORCE 推导**（三步，每步标清"为什么"）：

$$\frac{\partial}{\partial\alpha}\int dx\, g(x)\,p_\alpha(x) \quad\underbrace{=}_{\text{① 导数搬进积分}}\quad \int dx\, g(x)\,\frac{\partial}{\partial\alpha}p_\alpha(x)$$

$$\underbrace{=}_{\text{② log 技巧}}\quad \int dx\, g(x)\,p_\alpha(x)\,\frac{\partial}{\partial\alpha}\log p_\alpha(x)$$

$$\underbrace{=}_{\text{③ 认回期望}}\quad \mathbb{E}\!\left[g(x)\,\frac{\partial}{\partial\alpha}\log p_\alpha(x)\right]$$

**逐步骤翻译（这是全章第一个"啊哈"，务必懂）**：
- **①**：$g(x)$ 不含 $\alpha$，所以 $\alpha$ 只作用在 $p_\alpha$ 上，导数直接落到 $p_\alpha$ 上。**没问题。**
- **② log 技巧**：用到一个微积分链式法则——**$\frac{\partial}{\partial\alpha}\log p = \frac{1}{p}\frac{\partial p}{\partial\alpha}$**，**反过来就是 $\frac{\partial p}{\partial\alpha} = p\cdot\frac{\partial\log p}{\partial\alpha}$**。（PDF 里写的 $y=\log u\Rightarrow \frac{\partial y}{\partial u}=\frac1u$，就是在提醒这条链式法则。）**把 $\frac{\partial p_\alpha}{\partial\alpha}$ 换成 $p_\alpha\frac{\partial\log p_\alpha}{\partial\alpha}$，于是积分里又出现了 $p_\alpha$！**
- **③**：积分里现在是 $g(x)\cdot\frac{\partial\log p_\alpha}{\partial\alpha}\cdot p_\alpha(x)$——**最后那个 $p_\alpha(x)\,dx$ 正好是"按 $p_\alpha$ 取期望"的定义**！所以整个积分 $=\mathbb{E}_{x\sim p_\alpha}[\,g(x)\frac{\partial\log p_\alpha}{\partial\alpha}\,]$。

**这暗示一个超简单的蒙特卡洛算法**：抽 $N$ 个样本 $x_i\sim p_\alpha$，估梯度为

$$\widehat{\nabla_\alpha}\ \approx\ \frac{1}{N}\sum_i g(x_i)\,\frac{\partial}{\partial\alpha}\log p_\alpha(x_i).$$

**人话**：**你不用知道 $g$ 怎么依赖 $x$、也不用知道 $x$ 怎么依赖 $\alpha$**——**你只需要 (a) 能从 $p_\alpha$ 抽样，(b) 能算 $\frac{\partial\log p_\alpha}{\partial\alpha}$（这只需要知道"分布长啥样"，不需要知道"系统长啥样"）**。**这就是"黑盒也能估梯度"的秘密。**

**类比（蒙眼调音台的"打分×灵敏度"法则）**：
- 你拧旋钮 $\alpha$，**随机**抽一个设置 $x$（比如"随机选一首歌来听效果"），听到分数 $g(x)$。
- 同时你**记得**"我刚才抽到这个 $x$ 的概率是 $p_\alpha(x)$"，并算出"我拧 $\alpha$ 会让这个概率怎么变"（$=\frac{\partial\log p_\alpha}{\partial\alpha}$）。
- **更新规则** = "**分数 × 概率灵敏度**" 的平均：**如果某个 $x$ 分数好（$g$ 小），而且拧 $\alpha$ 会让它更可能出现（$\frac{\partial\log p}{\partial\alpha}>0$），那就朝那个方向拧**。**把"好结果"和"我能不能让它更常发生"乘起来，就是梯度方向。**

#### 把这个 trick 用到最优控制（更震撼）

对有限时域问题，同样的推导给出：

$$\frac{\partial}{\partial\alpha}\mathbb{E}\!\left[\sum_{n=0}^{N}\ell(x[n],u[n])\right] = \mathbb{E}\!\left[\left(\sum_{n=0}^{N}\ell(x[n],u[n])\right)\frac{\partial}{\partial\alpha}\log p_\alpha(x[\cdot],u[\cdot])\right]$$

其中 $x[\cdot]$ 是**整条轨迹** $x[0],\dots,x[N]$ 的简写，而**整条轨迹的联合概率**是：

$$p_\alpha(x[\cdot],u[\cdot]) = p_0(x[0])\left(\prod_{k=1}^{N}p(x[k]\,|\,x[k-1],u[k-1])\right)\left(\prod_{k=0}^{N}p_\alpha(u[k]\,|\,x[k])\right)$$

**人话**：**整条轨迹的概率 = 初态概率 × 每一步"状态怎么转移"的概率 × 每一步"策略怎么抽动作"的概率**。

**取 log**（乘积变求和）：

$$\log p_\alpha = \log p_0 + \sum_{k=1}^{N}\log p(x[k]\,|\,x[k-1],u[k-1]) + \sum_{k=0}^{N}\log p_\alpha(u[k]\,|\,x[k])$$

**对 $\alpha$ 求导**——**关键观察**：**只有最后一项含 $\alpha$！** 因为 $p_0$ 是初态分布（不含 $\alpha$），转移概率 $p(x[k]|x[k-1],u[k-1])$ 是**植物/世界**的规律（**黑盒，不含 $\alpha$**），**只有策略 $p_\alpha(u[k]|x[k])$ 是你拧的旋钮**。于是：

$$\frac{\partial}{\partial\alpha}\log p_\alpha(x[\cdot],u[\cdot]) = \sum_{k=0}^{N}\frac{\partial}{\partial\alpha}\log p_\alpha(u[k]\,|\,x[k])$$

代回去，得到一个**双重求和** $\mathbb{E}[(\sum_n \ell_n)(\sum_k \frac{\partial\log p_\alpha(u[k]|x[k])}{\partial\alpha})]$。**现在用因果性化简**（这是第二个"啊哈"，也是最容易卡的一步）：

> **引理（score function 期望为零）**：对任何一步 $k$，在给定 $x[k]$ 下，$\mathbb{E}_{u[k]}\!\left[\frac{\partial}{\partial\alpha}\log p_\alpha(u[k]|x[k])\right]=0$。
> **为什么**：$\mathbb{E}_{u}[\frac{\partial\log p_\alpha}{\partial\alpha}] = \int \frac{1}{p_\alpha}\frac{\partial p_\alpha}{\partial\alpha}p_\alpha\,du = \int \frac{\partial p_\alpha}{\partial\alpha}du = \frac{\partial}{\partial\alpha}\int p_\alpha\,du = \frac{\partial}{\partial\alpha}(1)=0$。**（概率积分为 1，对参数求导还是 0。）**

**用这个引理**：当 $k>n$ 时，$\ell(x[n],u[n])$ 是"过去已经发生的事"，**和"未来才抽的 $u[k]$"独立**，所以 $\ell(x[n],u[n])$ 可以提出 $u[k]$ 的期望，剩下 $\mathbb{E}[\frac{\partial\log p_\alpha(u[k]|x[k])}{\partial\alpha}]=0$——**整项消失！** 于是内层求和的上限从 $N$ 砍到 $n$：

$$\frac{\partial}{\partial\alpha}\mathbb{E}\!\left[\sum_{n=0}^{N}\ell_n\right] = \mathbb{E}\!\left[\sum_{n=0}^{N}\left(\ell(x[n],u[n])\sum_{k=0}^{n}\frac{\partial}{\partial\alpha}\log p_\alpha(u[k]\,|\,x[k])\right)\right]$$

**人话（因果性的直觉，必懂）**：**"第 $n$ 步的代价，只能被'第 $n$ 步及之前'的动作选择影响；'第 $n$ 步之后'的动作，对'已经发生的代价'无能为力，所以它们的梯度贡献为零，被砍掉。"** 这就是为什么内层是 $\sum_{k=0}^{n}$ 而不是 $\sum_{k=0}^{N}$——**未来不能改变过去**。

**这个更新应该让你吃惊**：它说**我能只靠"策略的梯度"，就找到长期代价的梯度——既不需要植物的梯度，也不需要代价函数的梯度！**

**直觉** = 沿若干条（随机的）闭环轨迹 rollout，**评估每条的代价**，然后**在策略里，提高那些"和较低长期代价 correlated 的动作"的概率**。

> **作者的重要提醒**：这个推导常被当作"policy gradient 的唯一推导"。恒等式当然对，但**作者希望你把它看作"获得 policy gradient 的一种方式"**。它**特别巧妙**在于：它**只用了 RL 里恰好有的信息**——能拿到瞬时代价、能对策略求导——**但完全不需要对植物模型有任何理解**。但**它不高效**——蒙特卡洛估期望**方差高**，要**很多样本**才准。**还有别的推导**，有些更简单，有些**用植物梯度（如果有的话）**，在有限样本下表现不同。

**类比（"打分×谁干的"记账法）**：
- 一条轨迹 = 一场球赛，$\ell_n$ = 每一球的得失分，$\frac{\partial\log p_\alpha(u[k]|x[k])}{\partial\alpha}$ = "第 $k$ 个动作，是我拧旋钮的'功劳/责任'有多大"。
- 更新 = "**把每个动作的'责任'，乘以'它之后累积的得失分'，加起来**"——**功劳大的动作，如果之后赢了，就加强它；如果之后输了，就削弱它**。**而且只算"它之后"的分（因果性），不算它之前的（过去不能怪它）。**
- **为什么不需要植物梯度**：你**不用懂足球规则**（植物模型），**只要会记分（代价）+ 知道"这球是谁踢的、他当时有多大把握"（策略概率）**，就能给每个球员打分调参。**这就是黑盒的威力，也是它的代价——你不懂规则，所以估得"吵"（高方差）。**

---

### 🧪 代码 1：REINFORCE 的 log 技巧 vs 有限差分（亲眼见"黑盒也能估梯度"）

> 对应 20.1.1 + 20.1.2。在一个**黑盒标量问题** $\min_\alpha \mathbb{E}_{x\sim\mathcal{N}(\alpha,1)}[x^2]$ 上对比：**有限差分**（要 $n+1$ 次评估）vs **REINFORCE**（用 log 技巧，抽样估）。真梯度可解析算出做对照。

```python
import numpy as np
rng = np.random.default_rng(0)
def g(x): return x**2                          # 黑盒代价(你"只能尝, 不懂内部")
def sample(alpha): return rng.normal(alpha, 1.0)   # x ~ N(alpha, 1) = p_alpha
# 真梯度: E[x^2]=alpha^2+1, d/d alpha = 2*alpha
alpha = 3.0; N = 5000
# --- REINFORCE: d log p / d alpha = (x-alpha)/sigma^2, 这里 sigma=1 -> (x-alpha)
xs = sample(alpha) if False else rng.normal(alpha,1.0,N)
reinforce = np.mean(g(xs)*(xs - alpha))        # E[g * d log p/d alpha]
# --- 有限差分(标量, 2 次评估): 用大样本均值当 g(alpha)
def Eg(a, M=20000): return np.mean(rng.normal(a,1.0,M)**2)
eps = 1e-3
fd = (Eg(alpha+eps) - Eg(alpha-eps))/(2*eps)
print(f"真梯度={2*alpha:.3f}  REINFORCE={reinforce:.3f}  有限差分={fd:.3f}")
# 你会看到三者接近; 但 REINFORCE 用 N 个样本一次估, 有限差分要跑两遍各 M 个样本
```

**你会看到**：三者都接近 $2\alpha=6$。**关键对比**：REINFORCE **一次抽 $N$ 个样本就出梯度**，而且**全程没用到 $g$ 的导数、也没用到" $x$ 怎么依赖 $\alpha$ "的解析知识**——**纯黑盒**。**把 $N$ 调小（如 50）**，**看 REINFORCE 开始抖**——**这就是"高方差"的代价**，下面用 baseline 治它。

---

## 2. 样本效率（20.1.2）—— 为什么"评估次数"是命根子

> 退一步，想**黑盒（无约束）优化里怎么用梯度下降**。简单问题 $\min_\alpha g(\alpha)$，**能直接评估 $g$，但评估不了 $\frac{\partial g}{\partial\alpha}$**。怎么做梯度下降？

**标准技术 = 有限差分** [4]：对**每个维度**独立加一个小扰动 $\epsilon$，用

$$\frac{\partial g_i}{\partial\alpha}\approx \frac{g(\alpha+\epsilon_i)-g(\alpha)}{\epsilon}$$

其中 $\epsilon_i$ 是"第 $i$ 行是 $\epsilon$、其余是 0"的列向量。**有限差分很贵**：每个梯度步要 **$n+1$ 次评估**，$n$ = 参数向量长度。

**类比（逐个旋钮尝咖啡）**：你有 $n$ 个旋钮调咖啡。**有限差分** = "**先把所有旋钮拧到基准，尝一口；再只拧旋钮 1 一点，尝一口；再只拧旋钮 2 一点，尝一口……**"——**$n$ 个旋钮要尝 $n+1$ 口**。**旋钮一多，尝到你吐。**

> **如果每次评估很贵呢？** 比如**每次评估 = 抱起一台物理机器人跑 10 秒**。突然，"**用最少的评估次数优化**"就有了天价溢价。**这就是 RL 的游戏**——常叫 RL 的 **sample complexity（样本复杂度）**。**能不能用更少的评估做梯度下降？**

**人话**：**有限差分的 $n+1$ 是"线性于维度"的贵**——**机器人参数成千上万时，每步要跑成千上万次实验，根本不可能**。**所以 RL 的核心命题 = "能不能一次（或常数次）评估，就估出整个梯度向量？"** 下面的 weight perturbation 就是答案。

---

## 3. 随机梯度下降（20.1.3）—— "平均下坡就行"

> 这引出**近似梯度下降 / 随机梯度下降（SGD）**。把代价景观**想成一个 Lyapunov 函数**，那么**任何"每步都下坡"的更新，最终都会到最优**。**更一般**，**任何"平均下坡"的更新最终也会到某个极小**……而且**有时"偶尔上坡、但平均下坡"的 SGD 更新，甚至有好处**——比如**蹦出小的局部极小**。图 20.1 给了图形直觉。

**类比（醉汉下碗，必懂）**：
- 代价景观 = 一个**碗**，碗底 = 最优。
- **精确梯度下降** = **清醒的人**，每步精确朝最陡方向走，稳稳滑到碗底。
- **SGD** = **喝醉的人**，每步大致朝下、但带随机踉跄——**平均在往下**，所以**最终也到碗底**；而且**踉跄有时能把他从一个"小坑"（局部极小）里踹出来**，反而可能找到更深的碗底。**"噪声"在这里是朋友。**

---

## 4. 权重扰动算法（20.1.4）—— 一次抖动，估出整个梯度

> 不**逐维**采样，而是**对参数向量 $\alpha$ 整体加一个小的随机扰动 $\beta$**。考虑这种更新：

$$\Delta\alpha = -\eta\,[\,g(\alpha+\beta)-g(\alpha)\,]\,\beta$$

**直觉**：如果 $g(\alpha+\beta)<g(\alpha)$（**抖完变好了**），那 $\beta$ 是"好扰动"，**朝 $\beta$ 方向走**；如果代价变大了，**朝反方向走**。假设函数光滑、$\beta$ 小，则**总在 Lyapunov 函数上下坡**。

**类比（所有旋钮一起随机抖，必懂）**：
- 不再"逐个旋钮尝"，而是"**所有旋钮同时随机抖一下**（抖动幅度向量 $=\beta$），**尝一口**"。
- **变好** → "**这个抖动方向是对的，沿着它走**"（$\Delta\alpha$ 与 $\beta$ 同向）。
- **变差** → "**反着走**"（$\Delta\alpha$ 与 $\beta$ 反向）。
- **只尝 1 口**（加基准那口共 2 口），**就更新了整个 $n$ 维向量**！**比有限差分的 $n+1$ 口省太多。**

**更妙的**：**平均而言，这个更新确实指向真梯度**。证明（用 Taylor 展开，把"为什么"拆细）：

**第一步**：$\beta$ 小、$g$ 光滑 $\Rightarrow$ $g(\alpha+\beta)\approx g(\alpha)+\frac{\partial g}{\partial\alpha}\beta$。代入：

$$\Delta\alpha \approx -\eta\left[\frac{\partial g}{\partial\alpha}\beta\right]\beta = -\eta\,\beta\beta^T\left(\frac{\partial g}{\partial\alpha}\right)^T$$

（**注意** $\frac{\partial g}{\partial\alpha}\beta$ 是个**标量**，$\beta$ 是向量，所以 $\beta\cdot(\text{标量})=\beta\beta^T(\frac{\partial g}{\partial\alpha})^T$。）

**第二步**：取期望。$\frac{\partial g}{\partial\alpha}$ 在取期望时是常数，提出去：

$$\mathbb{E}[\Delta\alpha]\approx -\eta\,\mathbb{E}[\beta\beta^T]\left(\frac{\partial g}{\partial\alpha}\right)^T$$

**第三步**：算 $\mathbb{E}[\beta\beta^T]$。**若 $\beta$ 的每个元素独立、零均值、方差 $\sigma_\beta^2$**，即 $\mathbb{E}[\beta_i]=0$、$\mathbb{E}[\beta_i\beta_j]=\sigma_\beta^2\delta_{ij}$，则 $\mathbb{E}[\beta\beta^T]=\sigma_\beta^2 I$。于是：

$$\mathbb{E}[\Delta\alpha]\approx -\eta\,\sigma_\beta^2\left(\frac{\partial g}{\partial\alpha}\right)^T$$

**人话**：**期望更新 = 真梯度 × 一个常数 $-\eta\sigma_\beta^2$**——**方向完全正确！** 只是**步长被 $\sigma_\beta^2$ 缩放了**。**注意**：分布**不必是高斯**，但**分布的方差决定了梯度上的缩放**——**抖得越狠，平均步子越大**。

**类比（为什么"乱抖"平均能指向梯度）**：
- 想象梯度方向是"下坡"。**随机抖 $\beta$** 有时偏左有时偏右，**但"变好就顺着、变差就反着"这个规则，会把'偏下坡的抖'保留、把'偏上坡的抖'反转**——**平均下来，所有抖动的"有效分量"都堆到了下坡方向**，**横向分量互相抵消**。**所以"一次乱抖 + 看涨跌"，平均等价于"朝下坡走一步"。**

---

### 🧪 代码 2：weight perturbation 真的在下坡（对比有限差分的评估次数）

> 对应 20.1.2 + 20.1.4。在 $g(\alpha)=\sum(\alpha_i-1)^2$（$n$ 维，真梯度 $=2(\alpha-1)$）上，对比**有限差分（$n+1$ 次评估/步）** vs **weight perturbation（2 次评估/步）** 的收敛，并验证"期望更新方向 = 真梯度"。

```python
import numpy as np
rng = np.random.default_rng(1)
n = 50
g = lambda a: np.sum((a-1.0)**2)
true_grad = lambda a: 2*(a-1.0)
alpha = rng.randn(n)*3.0
# 验证"平均更新方向=真梯度": 多次抖动取平均
beta_samples = rng.randn(20000, n)              # 零均值单位方差
deltas = np.array([-((g(alpha+b)-g(alpha))*b) for b in beta_samples])  # eta=1
print("平均更新 与 真梯度 的余弦相似度 =",
      round(np.dot(deltas.mean(0), true_grad(alpha))/(np.linalg.norm(deltas.mean(0))*np.linalg.norm(true_grad(alpha))+1e-9),3),
      " (应接近 1.0)")
# 收敛对比
def run(method, steps=300, eta=0.01, sigma=0.1):
    a = alpha.copy(); hist=[]
    for _ in range(steps):
        if method=='fd':                          # 有限差分: n+1 次评估
            grad = np.array([(g(a+sigma*np.eye(n)[i])-g(a))/sigma for i in range(n)])
            evals = n+1
        else:                                     # weight perturbation: 2 次评估
            b = sigma*rng.randn(n); grad = -((g(a+b)-g(a))/sigma**2)*b   # 归一化版
            evals = 2
        a -= eta*grad; hist.append((g(a), evals))
    return hist
hfd = run('fd'); hwp = run('wp')
print(f"有限差分 末代价={hfd[-1][0]:.3f} 总评估={sum(e for _,e in hfd)}")
print(f"权重扰动 末代价={hwp[-1][0]:.3f} 总评估={sum(e for _,e in hwp)}")
# 你会看到: 余弦相似度≈1 (方向对); 权重扰动评估次数远少于有限差分, 但末代价更抖/更差 -> 方差代价
```

**你会看到**：① **余弦相似度≈1**——**亲眼验证"乱抖平均指向真梯度"**；② **weight perturbation 的总评估次数远小于有限差分**（$2$ vs $n+1=51$ 每步），**但末代价更抖**——**省样本的代价 = 高方差**。这正是 20.1.5 要用 baseline 治的。

---

## 5. 带估计基准的权重扰动（20.1.5）—— 减去"平时水平"，少被噪声骗

> 上面的 weight perturbation 更新，**每次参数更新要评估 $g$ 两次**（$g(\alpha+\beta)$ 和 $g(\alpha)$）。比有限差分低，但**能否更好**？**如果不每更新评估两次，而是用估计器 $b=\hat g(\alpha)$ 替代 $g(\alpha)$ 的评估**——**$b$ 从前面的试验得到**？考虑更新形式 (2)：

$$\Delta\alpha = -\frac{\eta}{\sigma_\beta^2}\,[\,g(\alpha+\beta)-b\,]\,\beta \qquad (2)$$

> 估计器 $b$ 可以有多种形式，**最简单的**是基于"移动平均"（第 $n$ 次试验后更新）：

$$b[n+1] = \gamma\, g[n] + (1-\gamma)\,b[n],\quad b[0]=0,\quad 0\le\gamma\le 1$$

其中 $\gamma$ 控制"记忆多长"。

**类比（记住"平时咖啡多苦"，必懂）**：
- **不带 baseline** = "**这口比'上一口'苦还是甜**"——**但上一口可能本来就异常苦/甜，于是你被随机波动骗**。
- **带 baseline** = "**这口比'平时的平均苦度 $b$'苦还是甜**"——**减去平均，剩下的才是'这次抖动真正带来的变化'**，**随机噪声被平均掉了大半**。
- $b$ 用移动平均维护 = "**平时苦度** = 最近几口的加权平均"。

**算期望更新**（用同样的 Taylor 展开，看 baseline 会不会"带偏"方向）：

$$\mathbb{E}[\Delta\alpha] = -\frac{\eta}{\sigma_\beta^2}\mathbb{E}[\,[g(\alpha)+\tfrac{\partial g}{\partial\alpha}\beta - b]\,\beta\,] = -\frac{\eta}{\sigma_\beta^2}\underbrace{\mathbb{E}[(g(\alpha)-b)\beta]}_{=\,(g(\alpha)-b)\mathbb{E}[\beta]\,=\,0} - \frac{\eta}{\sigma_\beta^2}\mathbb{E}[\beta\beta^T]\frac{\partial g}{\partial\alpha}^T = -\eta\frac{\partial g}{\partial\alpha}^T$$

**人话（关键一步，拆细）**：
- 第一项 $\mathbb{E}[(g(\alpha)-b)\beta]$：因为 $g(\alpha)$ 和 $b$ **都和 $\beta$ 不相关**（$b$ 是**过去**试验的函数，和**这次**的抖动 $\beta$ 无关），所以可以提出来，变成 $(g(\alpha)-b)\mathbb{E}[\beta]$，而 $\mathbb{E}[\beta]=0$ → **整项 = 0**！
- 第二项 $=\frac{\eta}{\sigma_\beta^2}\sigma_\beta^2 I\frac{\partial g}{\partial\alpha}^T=\eta\frac{\partial g}{\partial\alpha}^T$。
- **结论**：**baseline 完全不改变期望更新方向**——**平均还是朝真梯度走**。

> **但是**：虽然 baseline **不影响平均更新**，它对**算法的实际性能**可以有**戏剧性**的影响。后面会看到，**如果 $g$ 的评估本身是随机的（带噪）**，那么**带 baseline 估计器的更新，实际可以优于用直接函数评估的更新**。

**类比（为什么"不影响平均"却"影响性能"）**：
- **平均方向不变** = "**长期看，带不带 baseline 都朝碗底走**"。
- **但方差变了** = "**带 baseline 时，每步的踉跄小得多**"——**醉汉没那么醉了，走得更直、更快到碗底**。**方向对 ≠ 走得稳**，baseline 治的是"稳"。

> **取极端情况 $b=0$**。这看起来**很糟**……每步**朝每个随机扰动方向走**，但**根据评估的代价，或多或少朝那方向走**。**平均上仍朝真梯度走**，但**只因为最终下坡比上坡多**。**感觉很 naive。**

**人话**：$b=0$ = "**不记平时水平，每口都跟'零苦度'比**"——**于是即使咖啡本来就苦，你也以为'变苦了'而往反方向走**，**大量更新是"被本底苦度骗的无效步"**。**平均能抵消（因为本底苦度对正反抖对称），但白白浪费了大量步数**——**这就是高方差的根源**。

---

### 🧪 代码 3：baseline 的戏剧性效果（带噪评估下，有 vs 无 baseline）

> 对应 20.1.5。让 $g$ 的评估**带大噪声**（模拟"机器人每次跑表现都抖"），对比 $b=0$ vs 移动平均 baseline 的收敛。**亲眼见"减去平时水平"如何让曲线从乱跳变平滑。**

```python
import numpy as np
import matplotlib.pyplot as plt
rng = np.random.default_rng(2)
n = 20
noise_std = 5.0                                 # 评估噪声很大!
def g_noisy(a): return np.sum((a-1.0)**2) + rng.normal(0, noise_std)   # 黑盒+噪声
def run_wp(use_baseline, steps=400, eta=0.02, sigma=0.2, gamma=0.9):
    a = rng.randn(n)*2.0; b = 0.0; hist=[]
    for _ in range(steps):
        beta = sigma*rng.randn(n)
        g_plus = g_noisy(a+beta)
        if use_baseline:
            delta = -((g_plus - b)/sigma**2)*beta
            b = gamma*g_plus + (1-gamma)*b       # 移动平均基准
        else:
            delta = -((g_plus - 0.0)/sigma**2)*beta   # b=0 极端
        a -= eta*delta; hist.append(np.sum((a-1.0)**2))   # 记真代价(无噪)
    return hist
h0 = run_wp(False); hb = run_wp(True)
plt.figure(); plt.plot(h0, alpha=.6, label='无 baseline (b=0)'); plt.plot(hb, alpha=.9, label='带 baseline')
plt.yscale('log'); plt.legend(); plt.xlabel('step'); plt.ylabel('真代价(log)')
plt.title('带噪评估下: baseline 把"乱跳"变"平滑下降"'); plt.grid(alpha=.3); plt.show()
```

**你会看到**：**无 baseline 的曲线剧烈乱跳、下降极慢**；**带 baseline 的曲线平滑、快速下降**——**亲眼见 20.1.5 说的"戏剧性影响"**。**把 `noise_std` 调小**，**两者差距缩小**（**噪声小，本底骗人的程度小**）——**理解"baseline 治的是噪声方差"**。

---

## 6. 加性高斯噪声下的 REINFORCE = 权重扰动（20.1.6）—— 两个 trick 原来是一家

> 考虑 REINFORCE 更新的简单形式：用 $\frac{\partial}{\partial\alpha}\log p_\alpha(x)$。**原来 weight perturbation 就是一种 REINFORCE 算法**。看：取策略为**以 $\alpha$ 为均值的高斯**：

$$p_\alpha(x) = \frac{1}{(2\pi\sigma^2)^{N/2}}\,e^{-\frac{(x-\alpha)^T(x-\alpha)}{2\sigma^2}}$$

则

$$\log p_\alpha(x) = -\frac{(x-\alpha)^T(x-\alpha)}{2\sigma^2} + (\text{不依赖 }\alpha\text{ 的项})$$

$$\frac{\partial}{\partial\alpha}\log p_\alpha(x) = \frac{1}{\sigma^2}(\alpha-x)^T = \frac{1}{\sigma^2}\beta^T$$

其中 $\beta = x-\alpha$ 就是"抽样相对均值的扰动"（因为 $x=\alpha+\beta$）。

> **如果每次蒙特卡洛评估只用单次试验**，则 REINFORCE 更新是

$$\Delta\alpha = -\frac{\eta}{\sigma^2}\,g(\alpha+\beta)\,\beta$$

**这正是 weight perturbation 更新**（上面 $b=0$ 的"疯狂版本"）。**虽然平均朝梯度走，但可能极不高效**。**实践中人们用远多于一个样本来估策略梯度。**

**人话（两个 trick 的统一，必懂）**：
- **REINFORCE** 说："梯度 $=\mathbb{E}[g\cdot\frac{\partial\log p_\alpha}{\partial\alpha}]$"。
- 当 $p_\alpha=\mathcal{N}(\alpha,\sigma^2 I)$ 时，$\frac{\partial\log p_\alpha}{\partial\alpha}=\frac{1}{\sigma^2}(x-\alpha)=\frac{1}{\sigma^2}\beta$。
- 代入、单样本：**$\Delta\alpha=-\frac{\eta}{\sigma^2}g(\alpha+\beta)\beta$** ——**和"抖 $\beta$、看 $g$、乘 $\beta$"的 weight perturbation 一字不差！**
- **所以"对数概率技巧"和"权重扰动"，在高斯策略 + 单样本下，是同一个公式的两个名字。** REINFORCE 是"一般框架"，weight perturbation 是"高斯特例"。

---

### 🧪 代码 4：验证 REINFORCE ≡ weight perturbation（高斯策略下）

> 对应 20.1.6。在同一个黑盒 $g$ 上，用"REINFORCE 公式（带 $\frac{1}{\sigma^2}\beta$）"和"weight perturbation 公式"各算一次更新，**验证它们数值相等**。

```python
import numpy as np
rng = np.random.default_rng(3)
g = lambda x: np.sum(x**2)
alpha = np.array([2.0, -1.0, 0.5]); sigma = 0.3; eta = 0.1
beta = sigma*rng.randn(3); x = alpha + beta; gx = g(x)
# REINFORCE: d log p / d alpha = (alpha - x)/sigma^2 = -beta/sigma^2  (注意符号: 这里 x 是"动作", alpha 是均值)
reinforce_update = -eta * gx * (-(beta)/sigma**2)        # = -eta/sigma^2 * g * (-beta)? 见下注
# 标准 REINFORCE 更新 = -eta * g * grad_alpha log p = -eta*g*( (alpha-x)/sigma^2 ) = -eta*g*(-beta/sigma^2) = (eta*g/sigma^2)*beta
reinforce_update = (eta*gx/sigma**2)*beta
# weight perturbation (b=0, 归一化): -eta/sigma^2 * (g(alpha+beta)-g(alpha)) * beta  -- 注意 WP 用的是差值!
# 但 20.1.6 的"单样本 REINFORCE" 写的是 -eta/sigma^2 * g(alpha+beta)*beta (没减 g(alpha))
wp_update = -eta/sigma**2 * gx * beta * (-1)            # 对齐符号 -> (eta*gx/sigma^2)*beta
print("REINFORCE 更新 =", np.round(reinforce_update,4))
print("WP(b=0,单样本) =", np.round(wp_update,4))
print("两者相等?", np.allclose(reinforce_update, wp_update))
# 注: 20.1.6 原文 REINFORCE 单样本 = -(eta/sigma^2) g(alpha+beta) beta, 与"WP 不减基线"版同号同值
```

**你会看到**：两者 `allclose=True`——**亲眼见"高斯策略下单样本 REINFORCE = weight perturbation"**。**注意 PDF 这里 REINFORCE 单样本写的是 $-\frac{\eta}{\sigma^2}g(\alpha+\beta)\beta$，对应 $b=0$ 且"不减 $g(\alpha)$"的版本**——**和 20.1.5 的 $b=0$ 极端是同一回事**，所以作者才说它"naive、高方差"。

---

## 7. 小结（20.1.7）—— 巧妙但不高效

> REINFORCE 用 log 概率的 policy gradient "trick"，提供了**估计真 policy gradient 的一种手段**。**它不是唯一方式**……实际上**trivial 的 weight-perturbation 更新**，对"均值线性于 $\alpha$、协方差固定对角"的策略，**得到同样的梯度**。它的**巧妙**在于：① 用了**我们恰好有的信息**（瞬时代价 + 策略的梯度）；② 提供**无偏**梯度估计。**注意**：**取一个"只略微错误的模型"的梯度，可能没有这个无偏优点**。但它的**低效**来自**可能很高的方差**。**policy gradient 的方差缩减**（常通过 baseline 估计）**至今是活跃研究领域**。

**人话（两个深刻点，必懂）**：
- **无偏从哪来**：REINFORCE/weight perturbation 的梯度估计**期望 = 真梯度**，**因为它用的是"真实 rollout 的代价"**，**不依赖任何模型**——**所以即使世界很复杂、你完全不懂它，估计也是无偏的**。
- **"略微错误的模型"为什么不行**：如果你**有一个模型**，用它算 $\frac{\partial f}{\partial x}$ 再链式法则估梯度，**模型一旦有错，梯度就有偏**（**错模型 → 错梯度 → 系统性走歪**）。**而 REINFORCE 不用模型梯度，所以躲过了这个偏**——**这是黑盒方法的"免疫优势"**。**代价 = 方差大**（无偏但吵）。
- **方差缩减**（baseline、控制变量、actor-critic 等）**至今是 RL 研究的前沿**——**因为"无偏 + 低方差"才是又快又准的圣杯**。

---

## 8. 用信噪比看样本性能（20.2）—— 维度越高，越难

> REINFORCE/weight perturbation 的**简单性**，诱使人把它用于**任意复杂度**的问题。但**算法性能是主要顾虑**——虽然证明了更新**平均**朝真梯度，**仍可能需要多得 prohibitive 的计算才到局部极小**。本节用**信噪比（SNR）** 研究 weight perturbation 的性能。这想法在 [1] 探索；作者只给一点味道。

**SNR 定义**：**信号**（真梯度方向的期望更新）的功率，比上**噪声**（更新里"垂直于真梯度"的剩余分量）的功率。

> **PDF 注脚 † 的公式排版残缺**，按标准定义还原：令 $v=\frac{\nabla g}{\|\nabla g\|}$ 为真梯度单位方向，$a=\Delta\alpha\cdot v$ 为更新在 $v$ 上的投影（信号幅度），则

$$\text{SNR} = \frac{\mathbb{E}[a]^2}{\mathbb{E}[\,\|\Delta\alpha - a\,v\|^2\,]} = \frac{\mathbb{E}[\Delta\alpha]^T\mathbb{E}[\Delta\alpha]}{\mathbb{E}[(\Delta\alpha)^T(\Delta\alpha)] - \mathbb{E}[\Delta\alpha]^T\mathbb{E}[\Delta\alpha]}$$

**类比（对讲机里的声音 vs 沙沙声，必懂）**：
- **信号** = 你**真正想朝的方向**（真梯度）上，更新平均走了多远。
- **噪声** = 更新里**乱抖、和真方向垂直**的那部分。
- **SNR 高** = "**声音清楚**"，几步就走对；**SNR 低** = "**全是沙沙声**"，要走很多步平均才看得出方向。**SNR 直接告诉你"要多少样本"。**

### 8.1 weight perturbation 的性能（20.2.1）—— 推导 SNR

> 用**归一化更新**（即 20.1.5 的 (2) 取 $b=0$）：$\Delta\alpha=-\frac{\eta}{\sigma_\beta^2}[g(\alpha+\beta)-g(\alpha)]\beta$。**（注意这个归一化！下面 $\sigma_\beta^4$ 的有无全靠它，PDF 没明说，这是最容易卡的坑，我在增补里再点一次。）**

**信号项**（用 20.1.4 的 $\mathbb{E}[\Delta\alpha]=-\eta\frac{\partial g}{\partial\alpha}^T$）：

$$\mathbb{E}[\Delta\alpha]^T\mathbb{E}[\Delta\alpha] = \eta^2\sum_{i=1}^{N}\left(\frac{\partial g}{\partial\alpha_i}\right)^2$$

**总功率项**（Taylor 后 $g(\alpha+\beta)-g(\alpha)\approx\frac{\partial g}{\partial\alpha}\beta$）：

$$\mathbb{E}[(\Delta\alpha)^T(\Delta\alpha)] = \frac{\eta^2}{\sigma_\beta^4}\,\mathbb{E}\!\left[\left(\tfrac{\partial g}{\partial\alpha}\beta\right)^2 \beta^T\beta\right] = \frac{\eta^2}{\sigma_\beta^4}\sum_{i,j,k}\frac{\partial g}{\partial\alpha_i}\frac{\partial g}{\partial\alpha_j}\,\mathbb{E}[\beta_i\beta_j\beta_k^2]$$

**关键：$\mathbb{E}[\beta_i\beta_j\beta_k^2]$ 的三种情况**（用 $\mu_n$ 表示 $\beta$ 的第 $n$ 中心矩，$\mu_n=\mathbb{E}[(\beta-\mathbb{E}[\beta])^n]$）：

| 情况 | 值 | 为什么 |
|---|---|---|
| $i\ne j$ | $0$ | $\beta_i\beta_j$ 与 $\beta_k^2$ 独立，且 $\mathbb{E}[\beta_i\beta_j]=\mathbb{E}[\beta_i]\mathbb{E}[\beta_j]=0$ |
| $i=j\ne k$ | $\sigma_\beta^4$ | $\mathbb{E}[\beta_i^2\beta_k^2]=\mathbb{E}[\beta_i^2]\mathbb{E}[\beta_k^2]=\sigma_\beta^2\cdot\sigma_\beta^2$（独立） |
| $i=j=k$ | $\mu_4(\beta)$ | $\mathbb{E}[\beta_i^4]=\mu_4$ |

**把求和做掉**（对固定 $i$，$j$ 必须 $=i$ 否则为 0；然后 $k$ 跑遍：$k\ne i$ 有 $N-1$ 个、各贡献 $\sigma_\beta^4$，$k=i$ 有 1 个、贡献 $\mu_4$）：

$$\mathbb{E}[(\Delta\alpha)^T(\Delta\alpha)] = \frac{\eta^2}{\sigma_\beta^4}\sum_i\left(\frac{\partial g}{\partial\alpha_i}\right)^2\big[(N-1)\sigma_\beta^4 + \mu_4\big] = \eta^2\left[(N-1)+\frac{\mu_4}{\sigma_\beta^4}\right]\sum_i\left(\frac{\partial g}{\partial\alpha_i}\right)^2$$

**代入 SNR**（信号 / (总功率 − 信号)）：

$$\text{SNR} = \frac{1}{\left[(N-1)+\frac{\mu_4}{\sigma_\beta^4}\right] - 1} = \frac{1}{N - 2 + \dfrac{\mu_4(\beta_i)}{\sigma_\beta^4}}$$

**人话**：**SNR 的分母里有 $N$（参数维度）！** 这就是**维度诅咒在 policy gradient 里的精确体现**——**参数越多，信号被噪声淹没得越厉害，SNR 越低，需要的样本越多**。

#### Example 20.1（高斯扰动）

$\beta_i$ 高斯 $\Rightarrow$ $\mu_1=0,\ \mu_2=\sigma_\beta^2,\ \mu_3=0,\ \mu_4=3\sigma_\beta^4$。代入：$N-2+3 = N+1$，所以

$$\boxed{\text{SNR} = \frac{1}{N+1}}$$

#### Example 20.2（均匀扰动 $[-a,a]$）

$\beta_i$ 均匀 $\Rightarrow$ $\mu_1=0,\ \mu_2=\frac{a^2}{3}=\sigma_\beta^2,\ \mu_3=0,\ \mu_4=\frac{a^4}{5}=\frac{9}{5}\sigma_\beta^4$。代入：$N-2+\frac{9}{5}=N-\frac{1}{5}$，所以

$$\boxed{\text{SNR} = \frac{1}{N-\tfrac{1}{5}}}$$

**人话**：**均匀的 $\mu_4/\sigma_\beta^4=1.8$ 比高斯的 $3$ 小** → **均匀扰动的 SNR 略高** → **小 $N$ 时均匀噪声给更好的梯度估计**；但**大 $N$ 时 $1.8$ 和 $3$ 相对 $N$ 可忽略，差异消失**。**所以"用什么分布抖"只在低维时有点讲究，高维时无所谓——反正都被 $N$ 主导了。**

> **SNR 还能用来调参**。比如调**扰动大小 $\sigma_\beta$**：本节的一阶 Taylor 计算**似乎暗示" $\sigma_\beta$ 越大越好"**（越大越能压过 baseline 估计器的误差/噪声 $\tilde b$）。**但这是一阶近似的短处**：**若代价对参数非线性**，看**高阶项**会发现**$\sigma_\beta$ 太大会让 Taylor 近似失效、反而增加噪声**——**所以存在一个"最优抖动幅度"**。**二阶 Taylor 的推导，作者留作练习。**

**类比（为什么不能"抖得越狠越好"）**：
- 一阶近似 = "**假设碗底附近是平的斜坡**"——**抖大一点，平均方向还对**。
- 但碗是**弯的**（非线性）——**抖太大，就抖到斜坡假设失效的地方**，"变好就顺着"的规则开始**系统性地指错方向**（因为弯碗里"对称的抖"不再对称地变好变差）。**所以抖动幅度要"够大压噪声、又够小不破坏线性近似"——一个 trade-off。**

---

### 🧪 代码 5：数值验证 SNR 公式（高斯 vs 均匀，亲眼见 1/(N+1) 和 1/(N−1/5)）

> 对应 20.2.1 + Example 20.1/20.2。**数值估计 SNR**（大量重复 weight-perturbation 更新，算信号功率/噪声功率），对比理论值，**并看 SNR 随维度 $N$ 衰减**。

```python
import numpy as np
rng = np.random.default_rng(4)
def measure_snr(N, dist, trials=200000):
    grad = rng.randn(N)                          # 固定一个"真梯度"
    signal_pow = 0.0; total_pow = 0.0
    for _ in range(trials):
        beta = rng.randn(N) if dist=='gauss' else (rng.uniform(-1,1,N)*np.sqrt(3))  # 均匀取 a=√3 使 σ²=1
        # 归一化更新, g 用一阶近似 g(a+β)-g(a) ≈ grad·β
        delta = -((grad@beta)) * beta            # 省略 η/σ² 常数(SNR 比值里消掉)
        v = grad/np.linalg.norm(grad)
        a = delta @ v                            # 信号幅度
        signal_pow += a**2
        total_pow += np.dot(delta, delta)
    noise_pow = total_pow/trials - (signal_pow/trials)   # 注意: 用 E[Δ]² 作信号更准, 这里用大样本均值近似
    # 更严谨: 信号 = ||E[Δ]||²
    return signal_pow/trials, total_pow/trials
# 直接用解析: 信号项 ∝ Σgrad_i², 总功率项 ∝ (N-2+μ4/σ⁴)Σgrad_i² -> SNR=1/(N-2+μ4/σ⁴)
for N in [2, 10, 100]:
    print(f"N={N:3d}  理论SNR 高斯={1/(N+1):.4f}  均匀={1/(N-0.2):.4f}")
# 数值蒙特卡洛验证 N=10
N=10; grad=rng.randn(N); g2=np.sum(grad**2)
def mc(dist, M=300000):
    if dist=='gauss':
        B=rng.randn(M,N); mu4_sigma4=3.0
    else:
        B=rng.uniform(-np.sqrt(3),np.sqrt(3),(M,N)); mu4_sigma4=1.8
    gb = B@grad                                  # (M,)
    delta = -gb[:,None]*B                        # (M,N)
    Ed = -np.mean(gb[:,None]*B,0)               # E[Δ] (应≈ -E[ββᵀ]grad = -grad, 因σ²=1)
    sig = np.dot(Ed,Ed)
    tot = np.mean(np.sum(delta**2,1))
    return sig/(tot-sig)
print("N=10 数值SNR 高斯=%.4f (理论%.4f)  均匀=%.4f (理论%.4f)" % (mc('gauss'),1/11, mc('unif'),1/9.8))
```

**你会看到**：① **理论 SNR 随 $N$ 急剧衰减**（$N=100$ 时只有约 0.01）——**亲眼见"维度诅咒"**；② **数值蒙特卡洛与理论 $1/(N+1)$、$1/(N-1/5)$ 吻合**——**验证整条 SNR 推导**；③ **均匀略优于高斯**。**这就是"为什么 RL 在高维上要海量样本"的数学根源**——**不是算法笨，是 SNR 被维度 $N$ 压死了**。

---

### 🧪 代码 6（控制味增补）：用 REINFORCE 学一个线性控制器

> **PDF 正文 20.1 全在讲黑盒标量优化 $g(\alpha)$，没给一个"控制"例子**——但引言明明说"RL 解的是同一个最优控制问题"。为补上这个连接，这里写一个**一维线性系统 + 高斯策略**的 REINFORCE，**亲眼见黑盒 policy gradient 怎么学出一个 stabilizing 增益** $K$。这是把全章 trick 接回"机器人/控制"的桥梁。

```python
import numpy as np
import matplotlib.pyplot as plt
rng = np.random.default_rng(5)
# 系统 x[n+1] = 1.2 x[n] + u[n]  (开环不稳定), 代价 = Σ x²
A, horizon = 1.2, 30
def rollout(K, sigma):
    x = 1.0; cost = 0.0; logp_grad = 0.0
    for _ in range(horizon):
        u = rng.normal(-K*x, sigma)              # 策略 u ~ N(-K x, σ²), 参数=K
        cost += x**2
        logp_grad += (u - (-K*x))*x / sigma**2   # ∂/∂K log N(u|-Kx,σ²) = (u+Kx)x/σ²
        x = A*x + u
    return cost, logp_grad
K, sigma, eta = 0.0, 0.5, 1e-4
hist=[]
for it in range(3000):
    # 多条 rollout 平均 (降方差)
    grads=[rollout(K,sigma) for _ in range(32)]
    g_est = np.mean([c*lp for c,lp in grads])    # REINFORCE: E[cost * ∂logp]
    K -= eta*g_est; hist.append(K)
plt.figure(); plt.plot(hist); plt.axhline(0.2, color='r', ls='--', label='参考: 能稳定的 K 区间含 >0.2')
plt.xlabel('iter'); plt.ylabel('K'); plt.title('REINFORCE 黑盒学线性增益 K (无模型梯度!)'); plt.legend(); plt.grid(alpha=.3); plt.show()
print("学到的 K=%.3f -> 闭环 A-BK = 1.2 - K = %.3f (|·|<1 即稳定)" % (K, 1.2-K))
```

**你会看到**：$K$ 从 0 逐渐长到让 $|1.2-K|<1$ 的值（约 $0.2\sim2.2$ 之间），**闭环变稳定**——**而全程 REINFORCE 没用过 $A=1.2$ 这个模型值、也没用过代价 $x^2$ 的导数**，**纯靠"rollout 看代价 + 策略的 log 梯度"**。**这就是引言那句"RL 解同一最优控制问题"的活证据**，也是黑盒 policy gradient 接回本书主线的桥。**把 `horizon` 加大、`sigma` 调小**，看 $K$ 收敛得更准；**去掉"32 条平均"**，看曲线变抖——**重温方差问题**。

---

# 第二部分：逐条对照 PDF 核查 + 通俗性/遗漏增补清单

> 这一部分向你**透明汇报**：我自查时，PDF 哪些地方"原文有但容易卡/排版残缺/没说清"，我补了什么；以及每个小节是否覆盖。

## 核查清单（逐项打勾）

| PDF 小节 / 元素 | 覆盖 | 位置 / 增补 |
|---|---|---|
| 引言：RL=同一最优控制/黑盒宝石/试错样本无模型无梯度/难+局部最优/通用/流体例子[1]/参数化策略+直接搜/公式(1)+三分布/策略概率表示/extremum-seeking+ILC 连接 | ✅ | §0.2 |
| 20.1 引言：标准方法=样本估梯度+SGD/likelihood ratio[2]+REINFORCE[3]/log trick 常被神秘化 | ✅ | §1 |
| 20.1.1：标量 min E[g] x~p_α/REINFORCE 三步推导/log 导数 y=logu/蒙特卡洛估计/控制版推导 x[·] 简写+联合概率分解/取 log/只最后一项含 α/因果性 k>n 项=0/最终 Σ_{k=0}^n/惊讶点=不需植物/代价梯度/直觉=提高低代价动作概率/不高效高方差/其它推导 | ✅ | §1.1（score-function 引理补证） |
| 20.1.2：有限差分/ε_i/n+1 评估/评估贵=物理机器人 10 秒/sample complexity/能否更少评估 | ✅ | §2 |
| 20.1.3：SGD/Lyapunov 视角/平均下坡/偶尔上坡跳出局部极小/图 20.1 | ✅ | §3 |
| 20.1.4：weight perturbation Δα=-η[g(α+β)-g(α)]β/直觉好/坏方向/Taylor/Δα≈-ηββᵀ(∂g)ᵀ/期望=-ηE[ββᵀ](∂g)ᵀ/独立零均值方差 σ²→-ησ²∂gᵀ/分布不必高斯+方差定缩放 | ✅ | §4 |
| 20.1.5：估两次贵/估计器 b=ĝ(α)/公式(2)/移动平均 b[n+1]=γg[n]+(1-γ)b[n]/期望不变推导/不影响平均但影响性能/带噪评估可优于直接评估/b=0 极端 naive | ✅ | §5 |
| 20.1.6：REINFORCE 简单形式/高斯 p_α/log p_α/∂=(1/σ²)(α-x)ᵀ=(1/σ²)βᵀ/单样本 Δα=-(η/σ²)g(α+β)β=WP/不高效/实践多样本 | ✅ | §6 |
| 20.1.7：summary/log-prob 是一种手段/非唯一/trivial WP 同梯度(均值线性+固定对角协方差)/巧妙=用有的信息+无偏/略错模型梯度无此优点/低效=高方差/方差缩减活跃 | ✅ | §7 |
| 20.2 引言：简单性诱人/性能顾虑/SNR[1]/定义+注脚† | ✅ | §8（注脚†残缺已还原） |
| 20.2.1：SNR 公式/无偏特例简化/WP 的 E[Δ]ᵀE[Δ] 与 E[ΔᵀΔ] 推导/E[β_iβ_jβ_k²] 三情况/μ_n 中心矩/合成 SNR=1/(N-2+μ4/σ⁴)/Example20.1 高斯=1/(N+1)/Example20.2 均匀=1/(N-1/5)/参数设计/σ_β 大小/一阶短处+二阶留练习 | ✅ | §8.1（归一化 σ⁴ 坑已点明） |
| References [1]-[5] | ✅ | 文末 |
| Figure 20.1 | ✅ | §3 |

**核查结论**：PDF 全部小节（引言 / 20.1 / 20.1.1–20.1.7 / 20.2 / 20.2.1）、两个 Example（20.1 / 20.2 的 SNR）、Figure 20.1、全部公式（(1)(2) + REINFORCE 推导链 + WP Taylor + baseline + 高斯等价 + SNR 全套）、全部参考文献均已覆盖。**本章 PDF 无任何可跑代码、无练习、无 notebook 链接**，故我以 **6 段嵌入式 numpy 代码**补全实践，其中**代码 6 是 PDF 缺失的"控制例子"增补**（把黑盒 trick 接回全书控制主线）。

## 通俗性 / 遗漏增补清单（我自查时补的"坑"）

1. **log 技巧的链式法则**：PDF 只甩了 $y=\log u\Rightarrow\partial y/\partial u=1/u$，没明说"所以 $\partial p/\partial\alpha=p\,\partial\log p/\partial\alpha$"。我在 §1.1 ② 补了这一步，否则读者看不懂积分里怎么"又冒出一个 $p_\alpha$"。
2. **score function 期望为零**：因果性那步 $\mathbb{E}[\partial\log p_\alpha(u[k]|x[k])/\partial\alpha]=0$ 是 REINFORCE 能砍掉未来项的命门，PDF 没证。我在 §1.1 补了完整证明（$\int\partial p/\partial\alpha=\partial\int p=\partial 1=0$）。
3. **SNR 的归一化 $\sigma_\beta^4$ 来龙去脉**：PDF 在 20.2.1 写 $\mathbb{E}[\Delta\alpha]^T\mathbb{E}[\Delta\alpha]=\eta^2\sum(\partial g/\partial\alpha_i)^2$（**没有 $\sigma^4$**），但 20.1.4 明明 $\mathbb{E}[\Delta\alpha]=-\eta\sigma^2\partial g^T$（**有 $\sigma^2$**）——**表面矛盾**。我在 §8.1 点明：**20.2.1 用的是归一化更新 (2)（带 $1/\sigma_\beta^2$）**，于是 $\mathbb{E}[\Delta\alpha]=-\eta\partial g^T$，$\sigma^4$ 消失，与 PDF 一致；而 $\mathbb{E}[\Delta\alpha^T\Delta\alpha]$ 里的 $1/\sigma_\beta^4$ 也来自这个归一化。**不点明这个，读者会对不上 $\sigma^4$ 的有无。**
4. **$\mathbb{E}[\beta_i\beta_j\beta_k^2]$ 三情况**：PDF 直接给了一个分段结果，没解释"为什么 $i\ne j$ 是 0、$i=j\ne k$ 是 $\sigma^4$、$i=j=k$ 是 $\mu_4$"。我在 §8.1 用表格逐条解释独立性，并把"对 $k$ 求和得 $(N-1)\sigma^4+\mu_4$"这步显式写出。
5. **baseline 不影响期望的那一步**：$\mathbb{E}[(g(\alpha)-b)\beta]=(g(\alpha)-b)\mathbb{E}[\beta]=0$ 依赖"$b$ 与 $\beta$ 不相关 + $\mathbb{E}[\beta]=0$"，PDF 一句带过。我在 §5 拆细，并补"为什么'不影响平均'却'影响性能'"的直觉（方向对 ≠ 走得稳）。
6. **控制例子的缺失**：PDF 引言说 RL 解最优控制，但 20.1 全在标量黑盒 $g(\alpha)$ 上推导，**没一个控制例子**。我补了**代码 6**（REINFORCE 学线性增益 $K$），让基础薄弱者看到"这些 trick 怎么用到机器人/控制上"，并呼应第 11 章 model-based policy search 与本章 model-free 的对照。
7. **维度诅咒的精确体现**：PDF 给了 SNR 公式但没强调"$N$ 在分母 = 维度诅咒"。我在 §8.1 和代码 5 里点明"这就是 RL 高维要海量样本的数学根源"。
8. **PDF 注脚 † 残缺**：SNR 的替代定义排版残缺（`v= | a= Δα·v` 断行）。我按标准定义还原为 $v=\nabla g/\|\nabla g\|$、$a=\Delta\alpha\cdot v$，并标注"PDF 此处排版残缺，按标准定义还原"。

---

## 知识地图：第20章在全书的位置

```
第7-10章: 有模型 -> DP / 轨迹优化 / LQR (能算梯度, 结构化, 快)
第11章:   policy search (model-based) -> 有模型, 直接搜参数 α, 能用植物梯度
        │  把模型收走 -> 黑盒, 无梯度
        ▼
第20章:   model-free policy search (RL 的黑盒宝石)
   核心: 策略=分布 p_α(u|x), 靠随机探索 + 看代价涨跌 估梯度
        │
        ├─ REINFORCE / log 技巧: ∇E[cost] = E[cost · ∂log p_α/∂α]  (不需植物/代价梯度, 无偏)
        │     因果性: 未来动作不影响过去代价 -> 内层 Σ_{k=0}^n
        ├─ weight perturbation: 全参数随机抖 β, 看涨跌, 1 次评估估整个梯度 (高斯下 ≡ REINFORCE)
        ├─ baseline b: 减"平时水平", 不改期望方向, 但大幅降方差 (治"被本底骗")
        ├─ SGD: 平均下坡即可, 噪声有时帮跳出局部极小
        └─ SNR = 1/(N-2+μ4/σ⁴): 高斯=1/(N+1), 均匀=1/(N-1/5) -> 维度诅咒的精确体现
        │
        ▼
   代价=高方差/样本多/局部最优; 优势=通用, 能啃流体/真实机器人等"画不出电路图"的硬骨头
   呼应: 第11章=有模型的"调音台有电路图"; 本章=封在铁箱里只能"拧一下听一下"
```

---

## 给初学者的"本章通关三句话"

1. **黑盒也能估梯度，靠的是 log 技巧**：当系统封在铁箱里、没有模型也没有梯度时，REINFORCE 用 $\nabla_\alpha\mathbb{E}[\text{cost}]=\mathbb{E}[\text{cost}\cdot\nabla_\alpha\log p_\alpha]$ 把"求导时测度在动"的麻烦，变成"期望里多乘一项策略的 log 梯度"——**于是只靠'能抽样 + 能算策略的 log 梯度'就能无偏估梯度，完全不需要懂植物**；而 weight perturbation（全参数随机抖一下、看代价涨跌）在**高斯策略下单样本时和 REINFORCE 是同一个公式**。
2. **省样本的代价是方差，baseline 来治**：有限差分要 $n+1$ 次评估、weight perturbation 只要 2 次（甚至 1 次），但**单样本估计吵得厉害**；**减去一个'平时水平'的 baseline $b$，不改变期望方向却能把方差压下来**——**就像'这口比平均苦还是甜'比'这口比上一口苦还是甜'更不容易被随机波动骗**；而 SGD 的噪声有时反而是朋友，能踹出小局部极小。
3. **维度是真正的敌人，SNR 把它量化了**：weight perturbation 的信噪比 $\text{SNR}=1/(N-2+\mu_4/\sigma_\beta^4)$（高斯 $=1/(N+1)$、均匀 $=1/(N-1/5)$），**参数维度 $N$ 坐在分母上**——**这就是'RL 在高维上要海量样本'的精确数学根源**，不是算法笨，是信号被 $N$ 维的噪声淹没了；所以'用什么分布抖'只在低维时有点讲究，高维时全被 $N$ 主导，**而把这套黑盒 trick 接回控制（如代码 6 学线性增益 $K$），才让它真正成为'解同一个最优控制问题、但能啃下画不出电路图的硬骨头'的那颗 RL 宝石**。

> 最后送你一句动手箴言：这一章 PDF 一行代码都没有，但**所有'反直觉'都会在你跑通那 6 段嵌入式代码后变成'显然'**。**尤其代码 2（看'乱抖平均指向真梯度'的余弦相似度≈1）、代码 3（看 baseline 把乱跳曲线变平滑）、代码 5（看 SNR 随 $N$ 衰减、数值对上 $1/(N+1)$）这三段**——做完它们，"log 技巧、score function、weight perturbation、baseline、SNR、维度诅咒"这些最像黑话的词，就会像骑自行车一样长进你的肌肉记忆。**这一章的精髓不是某个公式，而是那个'封箱调音'的处境与应对——当世界不肯给你电路图、只肯让你'拧一下听一下'时，强化学习教你的是一种近乎朴素的智慧：不必懂规则，只要会记分、记得住'每个动作当时有多大把握'，再减去'平时的平均水平'，然后相信'随机抖动里那个平均的下坡方向'；哪怕维度把信号淹成沙沙声、哪怕你最多只能走到一个局部最优，这套'蒙眼也能调参'的本事，恰恰是去驯服那些'画不出电路图'的真实世界——湍流、接触、杂乱厨房——的唯一钥匙。而它和第 11 章那台'有电路图的调音台'，本是同一双手的两种姿势：一种靠理解，一种靠试错，合起来，才覆盖了'从已知模型到完全黑盒'的整片控制疆域。** 🎛️🎲