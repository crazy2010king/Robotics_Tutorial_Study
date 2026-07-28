下面给你一份**最终整合版**的通俗讲解。我会先把 PDF《Chapter 11: Reinforcement Learning》从头到尾、按顺序、逐段讲清楚；讲完后，再逐项和 PDF 对照，检查有没有遗漏、哪里不够通俗；然后重点补充代码/实验实践部分；最后再整体综合成一个完整版本。

---

# 一、全文总览：这一章到底在讲什么？

这一章标题是：

> **Chapter 11: Reinforcement Learning**  
> 强化学习

如果用一句最通俗的话概括：

> 这一章讲的是：如何让机器人不是靠人一步步写规则，而是通过“尝试—犯错—得分—改进”的方式，自己学会一套动作策略。

我们可以把强化学习想象成训练小狗：

1. 小狗做动作；
2. 做对了给零食；
3. 做错了不给零食；
4. 小狗慢慢学会哪些动作能拿到零食。

在机器人里：

1. 机器人看见当前状态，比如箱子角度、手指位置；
2. 机器人发出动作，比如手指移动；
3. 环境变化，比如箱子被推动或翻起；
4. 系统给奖励，比如“箱子更接近翻正了，加分”；
5. 机器人调整策略，下次做得更好。

这一章在整本讲义中的位置也很关键：

- 前面章节讲感知、规划、控制；
- 强化学习则提供了一种“从数据中学控制策略”的方法；
- 它特别适合那些很难手工设计控制规则的任务，比如接触丰富、环境多样、感知复杂的操作任务。

---

# 二、文档开头信息：这是 MIT 课程讲义，不是正式教科书

PDF 开头包含课程讲义信息，我们也不能遗漏。

## 1. 书名与作者

文档属于：

> **ROBOTIC MANIPULATION**  
> Perception, Planning, and Control  
> Russ Tedrake

翻译：

> 机器人操作：感知、规划与控制  
> 作者：Russ Tedrake

通俗理解：

- **机器人操作**：让机器人用手、夹爪、手指去移动、抓取、翻转物体。
- **感知**：机器人“看见”和“理解”环境。
- **规划**：机器人决定“该怎么动”。
- **控制**：机器人真正执行动作。

---

## 2. 版权与修改时间

PDF 中写：

> © Russ Tedrake, 2020-2024  
> Last modified 2025-11-12.

意思是：

- 讲义版权从 2020 到 2024；
- 最后修改时间是 2025 年 11 月 12 日。

---

## 3. 引用、注解和反馈

PDF 中写：

> How to cite these notes, use annotations, and give feedback.

意思是：

- 如果引用这些讲义，需要按建议方式引用；
- 可以使用在线注解功能；
- 可以给作者反馈。

---

## 4. 这是 MIT 课程的工作笔记

PDF 中写：

> Note: These are working notes used for a course being taught at MIT.  
> They will be updated throughout the Fall 2024 semester.

通俗解释：

这不是正式出版教材，而是 MIT 课程的“活讲义”。

可以理解为：

> 老师一边上课一边更新，内容会持续变化。

---

## 5. 页面导航

PDF 中有：

> Previous Chapter  
> Table of contents  
> Next Chapter

这是网页版讲义的导航：

- 上一章；
- 目录；
- 下一章。

---

# 三、章节引言：为什么机器人操作是强化学习的好试验场？

这一章开头先说：

> 现在强化学习非常热门，文献也很多。  
> 强化学习算法的范围也扩大了很多。  
> 经典且仍然最好的入门书是 Sutton and Barto。  
> 如果想看更理论化的内容，可以看其他参考文献。  
> 还有一些很好的在线课程：Stanford CS234、Berkeley CS285、DeepMind x UCL。

这段话的作用是告诉读者：

> 强化学习领域很大，作者不会在这里写成一本完整教材，而是只讲和机器人操作最相关的部分。

---

## 1. 作者的目标

原文大意：

> 我的目标是提供足够的基础知识，让大家站在同一起跑线上。  
> 但重点是那些与操作 manipulation 特别相关的强化学习思想和例子。

通俗解释：

作者不是要讲所有强化学习，而是要回答：

> 强化学习怎么帮助机器人完成操作任务？

---

## 2. 为什么操作任务是强化学习的好试验场？

原文说：

> manipulation is a great playground for RL, due to the need for rich perception, for operating in diverse environments, and potentially with rich contact mechanics.

意思是：

> 机器人操作是强化学习的绝佳试验场，因为它需要丰富感知、在多样环境中运行，并且可能涉及丰富接触力学。

我们可以把“操作任务”想象成：

- 抓取杯子；
- 翻转盒子；
- 推动物体；
- 拧螺丝；
- 打开抽屉；
- 把物体放进盒子。

这些任务有几个难点：

### 难点一：感知复杂

机器人不是只处理一个数字，而可能面对：

- RGB 图像；
- 深度图；
- 点云；
- 物体遮挡；
- 光照变化；
- 杂乱场景。

### 难点二：环境多样

同一个任务可能发生在：

- 不同桌子；
- 不同光照；
- 不同物体摆放；
- 不同摩擦条件；
- 不同相机视角。

### 难点三：接触力学复杂

机器人操作经常涉及：

- 碰撞；
- 摩擦；
- 滑动；
- 推挤；
- 翻转；
- 夹持。

这些接触行为很难完全用简单公式写清楚。

---

## 3. 很多核心强化学习研究成果来自操作任务

原文还说：

> Many of the core applied research results have been motivated by and demonstrated on manipulation examples!

意思是：

> 很多强化学习的重要应用研究成果，都是由操作任务推动并在操作任务上展示的。

比如：

- 机械手翻箱子；
- 机器人抓放物体；
- 灵巧手操作魔方；
- 推动物体到目标位置。

所以作者选择操作任务作为强化学习的主要例子。

---

# 四、11.1 RL SOFTWARE：强化学习软件工具

这一节讲：

> 做强化学习时，我们用什么软件接口和算法库？

---

## 4.1 强化学习工具箱很多，但 Gymnasium 成了标准接口

原文说：

> There are now a huge variety of RL toolboxes available online, with widely varying levels of quality and sophistication.  
> But there is one standard that has clearly won out as the default interface... the Gymnasium, which is often still called “Gym” for short.

意思是：

> 现在网上有非常多强化学习工具箱，质量参差不齐。  
> 但有一个标准明显胜出，成为默认接口，那就是 Gymnasium，通常仍简称 Gym。

### 通俗理解

强化学习领域有很多工具，但大家都逐渐接受了一个“通用插头标准”：

> Gymnasium / Gym

它的作用不是实现所有算法，而是定义：

> 环境应该怎么和强化学习算法交互。

---

## 4.2 Gymnasium 环境接口 vs Drake System 接口

原文说：

> It’s worth taking a minute to appreciate the difference in the Gymnasium Environments interface and the Drake System interface; I think it is very telling.

意思是：

> 值得花一分钟理解 Gymnasium 环境接口和 Drake System 接口的区别。  
> 作者认为这很能说明问题。

---

### 1. Drake 的目标：表达和优化复杂动力系统

原文说：

> My goal in Drake is to present you with a rich and beautiful interface to express and optimize dynamical systems, to expose and exploit all possible structure in the governing equations.

通俗解释：

Drake 是一个很强的机器人动力学/控制工具。

它的目标是：

- 精确表达系统；
- 利用系统结构；
- 做模型优化；
- 做控制设计；
- 处理动力学方程。

可以理解为：

> Drake 像一套高级工程建模工具，尽量把系统内部结构暴露出来，让你利用物理规律。

---

### 2. Gym 的目标：极简通用接口

原文说：

> The goal in Gym is to expose the absolute minimal details, so that it’s possible to easily wrap every possible system under the same common interface.

通俗解释：

Gym 的目标正好相反：

> 尽量少暴露细节，让任何系统都能套进同一个接口。

它不关心你里面是：

- 机器人；
- Atari 游戏；
- 编译器；
- 控制系统；
- 模拟器。

只要你能按照 Gym 的方式提供：

```text
reset()
step()
render()
```

它就能被强化学习算法使用。

---

## 4.3 类比：Drake 像专业厨房，Gym 像快餐标准接口

可以这样理解：

### Drake 像专业厨房

专业厨房里：

- 有各种刀具；
- 有烤箱；
- 有温控设备；
- 有精确配方；
- 厨师可以利用食材特性做复杂菜。

这像 Drake：

> 暴露很多系统结构和物理细节。

### Gym 像快餐店标准流程

快餐店不关心你怎么做菜，只要求：

```text
输入订单
输出汉堡
```

接口统一、简单、通用。

这像 Gym：

> 不管内部多复杂，对外只提供统一接口。

---

## 4.4 任何 Drake 系统都可以包装成 Gym 环境

原文说：

> Almost by definition, you can wrap any Drake system as a Gym environment.

意思是：

> 几乎从定义上说，任何 Drake 系统都可以包装成 Gym 环境。

这是因为 Gym 接口非常通用。

只要你能：

1. 重置环境；
2. 给定动作推进一步；
3. 返回观测和奖励；

就可以包装成 Gym。

---

# 五、Example 11.1：把 Drake 仿真包装成 Gym 环境

这是本章第一个重要实践例子。

---

## 5.1 Gym 环境接口非常简单

原文说：

> A Gym environment is an incredibly simple wrapper around simulators which offers a very basic interface, most notably consisting of reset(), step(), render().

意思是：

> Gym 环境是仿真器的一个极其简单的包装器，提供最基本接口，最重要的是 reset()、step()、render()。

---

## 5.2 reset()：重置环境

`reset()` 的作用是：

> 把环境恢复到初始状态。

比如：

- 箱子回到初始角度；
- 手指回到初始位置；
- 物体重新摆放；
- 时间归零。

### 类比：游戏重新开始

就像玩游戏时按下：

```text
重新开始
```

角色回到出生点，分数清零，敌人重新刷新。

---

## 5.3 step()：执行一步动作

`step()` 的作用是：

> 给环境一个动作，让它向前推进一步。

比如：

```text
动作：手指向右移动 1 cm
```

环境会：

1. 执行动作；
2. 物理仿真前进一小步；
3. 返回新的观测；
4. 返回奖励；
5. 返回是否结束等信息。

原文说：

> The step() method returns the current observations and the one-step reward, as well as some additional termination conditions.

意思是：

> step() 返回当前观测、单步奖励，以及一些额外的终止条件。

---

### 类比：下棋走一步

你下棋时：

```text
你走一步
↓
棋盘变化
↓
裁判判断局势
↓
告诉你是不是赢了、输了、还没结束
```

强化学习里的 `step()` 类似：

```text
机器人动作
↓
环境变化
↓
得到观测和奖励
↓
判断是否结束
```

---

## 5.4 render()：可视化

`render()` 的作用是：

> 显示当前环境画面。

比如：

- 显示仿真窗口；
- 输出图像；
- 绘制机器人和物体。

通俗理解：

> 让人类看到机器人在干什么。

---

## 5.5 用 DrakeGymEnv 包装 Drake 仿真

原文说：

> You can wrap any Drake simulation in an OpenAI gym environment, using  
> from pydrake.gym import DrakeGymEnv

意思是：

可以使用 Drake 提供的：

```python
from pydrake.gym import DrakeGymEnv
```

把 Drake 仿真包装成 Gym 环境。

---

## 5.6 DrakeGymEnv 构造函数需要什么？

原文说：

> The DrakeGymEnv constructor takes a Simulator as well as an input port to associate with the actions, an output port to associate with the observations, etc.

意思是：

`DrakeGymEnv` 构造时需要：

1. 一个 `Simulator`；
2. 一个输入端口，用来接收动作 actions；
3. 一个输出端口，用来提供观测 observations；
4. 其他配置。

---

### 1. Simulator：仿真器

Simulator 负责推进物理仿真。

通俗理解：

> 它是时间推进器。

它让机器人、物体、接触、重力等按照物理规律演化。

---

### 2. action input port：动作输入端口

动作输入端口接收强化学习算法给出的控制命令。

比如：

```text
目标手指位置
关节力矩
夹爪开合命令
```

---

### 3. observation output port：观测输出端口

观测输出端口提供环境状态。

比如：

```text
箱子角度
箱子角速度
手指位置
手指速度
物体位置
```

---

## 5.7 reward：奖励函数如何实现？

原文说：

> For the reward, you can implement it as a simple function of the Simulator Context, or as another output port.

意思是：

奖励可以有两种实现方式：

### 方式一：写成 Simulator Context 的函数

也就是根据当前仿真状态直接计算奖励。

比如：

```python
reward = -abs(box_angle - target_angle)
```

### 方式二：作为另一个输出端口

也就是把奖励作为系统的一个输出。

---

## 5.8 为什么 DrakeGymEnv 围绕 Simulator，而不是只围绕 System？

原文说：

> DrakeGymEnv is built around a Simulator, not just a System, or a function that produces a random Simulator...

意思是：

`DrakeGymEnv` 不只是包装一个 System，而是包装一个 Simulator，或者一个能生成 Simulator 的函数。

---

### 为什么这样设计？

因为强化学习经常需要随机化环境。

比如每一次 rollout，也就是每一次完整仿真轨迹，可能希望：

- 同一个机器人；
- 但不同环境；
- 不同物体数量；
- 不同物体位置；
- 不同摩擦；
- 不同相机；
- 不同积分器参数。

这可能导致底层 System 的状态数或端口数不同。

所以用一个“Simulator 工厂”更灵活。

---

## 5.9 SimulatorFactory：仿真器工厂

原文说：

> The notion of a function that can produce simulators, referred to as a SimulatorFactory, is core to the stochastic system modeling framework in Drake.

意思是：

> 一个能生成仿真器的函数，叫做 SimulatorFactory，是 Drake 随机系统建模框架的核心。

### 通俗理解

SimulatorFactory 就像：

> 每次训练时随机生成一个新场景的“场景生成器”。

比如：

```text
第 1 次训练：箱子在左边，摩擦高
第 2 次训练：箱子在右边，摩擦低
第 3 次训练：箱子角度随机，手指位置随机
```

这样可以训练出更鲁棒的策略。

---

## 5.10 也可以在 Drake 中使用任何 Gym 环境

原文说：

> You can also use any Gym environment in the Drake ecosystem; you just won’t be able to apply some of the more advanced algorithms that Drake provides.

意思是：

> 你也可以在 Drake 生态中使用任何 Gym 环境，只是无法使用 Drake 提供的一些更高级算法。

通俗理解：

```text
Gym 环境 → 可以接入 Drake
但可能用不了 Drake 的高级模型工具
```

---

## 5.11 作者为什么推荐 Drake？

原文说：

> Of course, I think that you should use Drake for your work in RL, too, because it provides a rich library of dynamical systems that are rigorously authored and tested, including a great physics engine for dealing with contact, and leaves open the option to put RL approaches head-to-head against more model-based alternatives.  
> I admit I might be a little biased.

意思是：

> 作者认为你也应该在强化学习研究中使用 Drake。  
> 因为 Drake 提供严格编写和测试的动力系统库，包括很好的接触物理引擎，并且允许把强化学习和基于模型的方法直接对比。  
> 作者承认自己可能有点偏袒。

---

### Drake 的优势

1. 动力系统库丰富；
2. 代码经过严格测试；
3. 物理引擎适合处理接触；
4. 可以把强化学习和模型控制方法公平比较。

### 类比：Drake 是带物理实验室的机器人训练场

普通 Gym 环境可能像一个黑箱游戏：

```text
输入动作 → 输出结果
```

Drake 更像一个物理实验室：

```text
你知道里面有力、质量、摩擦、接触、动力学方程
```

这对机器人研究很重要。

---

## 5.12 建模越仔细，会不会 sim2real 差距越大？

原文说：

> Some people might argue that the more thoughtfully you model your system, the more assumptions you have baked in, making yourself susceptible to “sim2real” gaps; but I think that’s simply not the case.

意思是：

> 有人可能认为，建模越仔细，假设越多，越容易出现仿真到现实的差距。  
> 但作者认为并非如此。

---

### 什么是 sim2real gap？

sim2real gap 是：

> simulation to reality gap  
> 仿真与现实之间的差距。

比如：

- 仿真里的摩擦太理想；
- 仿真里的相机没有噪声；
- 仿真里的物体材质太均匀；
- 仿真里的接触模型不完美。

这些会导致：

```text
仿真里学得好
真实机器人上表现差
```

---

### 作者的观点：仔细建模包括建立不确定性模型

原文说：

> Thoughtful modeling includes making uncertainty models that can account for as narrow or broad of a class of systems as we aim to explore.

意思是：

> 仔细建模不只是把系统写死，而是包含不确定性模型。  
> 这些不确定性模型可以覆盖我们想探索的系统范围。

通俗理解：

不是说：

```text
我认为摩擦一定是 0.3
```

而是说：

```text
摩擦可能在 0.2 到 0.6 之间随机
```

这样训练出来的策略更 robust。

---

### 类比：学开车不能只在完美晴天学

如果你只在：

- 晴天；
- 干燥路面；
- 没有行人；
- 没有堵车；

的环境下学车，真实上路会不适应。

更好的训练是：

- 雨天；
- 夜晚；
- 堵车；
- 路面打滑；
- 行人突然出现。

这就是不确定性建模和随机化的意义。

---

## 5.13 强化学习和控制交叉的核心挑战

原文说：

> I think one of the most fundamental challenges waiting for us at the intersection of reinforcement learning and control is a deeper understanding of the class of models that is rich enough to describe the diversity and richness of problems we are exploring in manipulation, while providing somewhat more structure that we can exploit with stronger algorithms.

意思是：

> 作者认为强化学习和控制交叉领域的一个根本挑战是：  
> 找到一类模型，既足够丰富，能描述操作问题的多样性，又具备一定结构，让我们能用更强算法去利用它。

通俗解释：

我们希望模型：

```text
足够灵活：能描述复杂真实世界
足够有结构：能被算法有效利用
```

这两个目标经常冲突。

太灵活：

```text
什么都能表示，但难以优化
```

太有结构：

```text
容易优化，但可能描述不了真实复杂性
```

这是强化学习用于机器人操作的核心难题之一。

---

## 5.14 模型应该随着数据不断改进

原文还说：

> Importantly, these models should continually expand and improve with data.

意思是：

> 重要的是，这些模型应该能随着数据不断扩展和改进。

通俗理解：

机器人不能只靠初始模型。

它应该：

```text
收集数据
↓
改进模型
↓
改进策略
↓
再收集数据
```

形成持续学习循环。

---

## 5.15 Gymnasium 只提供接口，不提供算法实现

原文说：

> Gymnasium provides an interface for RL environments, but doesn’t provide the implementation of the actual RL algorithms.

意思是：

> Gymnasium 提供强化学习环境接口，但不提供具体强化学习算法实现。

也就是说：

```text
Gymnasium：环境接口
算法库：训练智能体
```

---

## 5.16 推荐算法库：Stable Baselines3

原文说：

> As of this writing, I would recommend Stable Baselines3: it provides a very nice and thoughtfully-documented set of implementations in PyTorch.

意思是：

> 在作者写作时，推荐 Stable Baselines3。  
> 它提供了一套很好、文档很完善的 PyTorch 实现。

### 通俗理解

如果你想快速使用常见强化学习算法，比如：

- PPO；
- SAC；
- DQN；
- A2C；

Stable Baselines3 是一个很实用的库。

---

## 5.17 黑箱优化工具：Nevergrad

原文说：

> One other class of algorithms that is very relevant to RL but not specifically designed for RL is algorithms for black-box optimization.  
> I quite like Nevergrad, and will also use that here.

意思是：

> 另一类与强化学习很相关、但不是专门为强化学习设计的算法，是黑箱优化算法。  
> 作者很喜欢 Nevergrad，也会在这里使用它。

---

### 什么是黑箱优化？

黑箱优化是：

> 你不知道函数内部结构，只能输入参数、观察输出结果，然后想办法优化。

比如：

```text
输入策略参数
↓
运行仿真
↓
得到总奖励
↓
调整参数，让总奖励更高
```

你不需要知道：

```text
奖励对参数的精确梯度
```

这就是黑箱优化。

### 类比：调收音机旋钮

你不知道内部电路怎么工作。

你只知道：

```text
左转一点，声音更清楚
右转一点，噪声更大
```

于是你慢慢调到最佳位置。

这就是黑箱优化。

---

# 六、11.2 POLICY-GRADIENT METHODS：策略梯度方法

这一节开始讲强化学习算法。

标题：

> 11.2 POLICY-GRADIENT METHODS  
> 策略梯度方法

---

## 6.1 什么是 policy？策略？

在强化学习中，policy 是：

> 从观测到动作的映射。

通俗理解：

策略就是机器人的“行为规则”。

比如：

```text
如果箱子快倒了，就把手指往左移
如果箱子已经翻正，就停止动作
```

在深度强化学习中，policy 通常是一个神经网络：

```text
输入：观测
输出：动作
```

---

## 6.2 什么是策略梯度？

策略梯度方法直接优化策略参数。

也就是说：

```text
不是先学价值再推导动作
而是直接调整策略，让奖励更高
```

类比：

你不是先背一本“局势评估手册”，而是直接练习“怎么出招更容易赢”。

---

# 七、11.2.1 Black-box optimization：黑箱优化

这一小节标题：

> 11.2.1 Black-box optimization  
> 黑箱优化

---

## 7.1 Example 11.2：黑箱优化示例

原文：

> Example 11.2 Black-box optimization.  
> Coming to deepnote soon. The example is available in rl/black_box.ipynb.

意思是：

> 例 11.2 是黑箱优化示例。  
> 即将上线 deepnote。  
> 示例文件在 `rl/black_box.ipynb`。

---

## 7.2 黑箱优化和强化学习的关系

在强化学习中，如果我们把整个仿真环境看成一个黑箱：

```text
策略参数 θ
↓
运行仿真
↓
得到回报 J(θ)
```

我们的目标是找到让回报最大的 θ：

```text
maximize J(θ)
```

如果我们不能或不想计算梯度，就可以用黑箱优化。

---

## 7.3 通俗例子：调参数让机器人翻箱子

假设策略只有几个参数。

我们不断尝试：

```text
参数组合 A：总奖励 10
参数组合 B：总奖励 25
参数组合 C：总奖励 18
```

然后黑箱优化算法会猜测：

```text
也许 B 附近更好
```

于是继续在 B 附近搜索。

---

# 八、11.2.2 Stochastic optimal control：随机最优控制

这一小节标题：

> 11.2.2 Stochastic optimal control  
> 随机最优控制

PDF 中这一节只有标题，没有展开。

我们不能假装它有正文，但也不能遗漏。

---

## 8.1 这一节在 PDF 中未展开

它可能是后续补充内容。

---

## 8.2 补充解释：什么是随机最优控制？

随机最优控制研究的是：

> 在存在随机性的情况下，如何选择控制动作，使长期代价最优。

比如：

- 物体滑动有随机性；
- 传感器有噪声；
- 摩擦不确定；
- 初始状态随机。

系统不是完全确定的：

```text
同样动作，不一定得到完全相同结果
```

所以控制策略要考虑不确定性。

---

### 类比：雨天开车

晴天开车：

```text
踩刹车 → 减速
```

雨天开车：

```text
踩刹车 → 可能打滑
```

所以你需要更保守、更考虑不确定性的控制策略。

这就是随机最优控制要处理的问题。

---

# 九、11.2.3 Using gradients of the policy, but not the environment：使用策略梯度，但不使用环境梯度

这一小节标题：

> 11.2.3 Using gradients of the policy, but not the environment

PDF 中说：

> You can find more details on the derivation and some basic analysis of these algorithms here.

意思是：

> 这些算法的推导和基本分析可以在别处找到更多细节。

---

## 9.1 这句话是什么意思？

策略梯度方法中，我们通常需要：

```text
奖励对策略参数的梯度
```

但我们不一定需要：

```text
环境动力学对动作的梯度
```

也就是说：

```text
我们只需要知道策略怎么改变动作概率
不一定要知道环境内部物理方程的梯度
```

---

## 9.2 为什么这很重要？

机器人环境很复杂：

- 接触；
- 碰撞；
- 摩擦；
- 离散事件；
- 仿真器不可微。

如果要求环境可微，很多真实任务就很难处理。

策略梯度方法的优势是：

```text
环境可以是黑箱
只要能得到奖励和轨迹
就可以优化策略
```

---

## 9.3 类比：学投篮

你不需要精确知道：

- 空气动力学；
- 肌肉力学；
- 篮球材料弹性。

你只需要：

```text
投出去
看进没进
调整姿势
```

这就是“使用策略梯度，但不使用环境梯度”的直观感觉。

---

# 十、11.2.4 REINFORCE, PPO, TRPO

这一小节标题：

> 11.2.4 REINFORCE, PPO, TRPO

这些都是著名的策略梯度算法。

---

## 10.1 REINFORCE

REINFORCE 是最经典的策略梯度算法之一。

它的思想非常直接：

```text
如果某个动作带来了高回报，就增加这个动作出现的概率；
如果某个动作带来了低回报，就减少这个动作出现的概率。
```

### 类比：考试后总结经验

你考试做了几道题：

- 某题用了方法 A，得分高；
- 某题用了方法 B，得分低。

下次你会更倾向用方法 A。

REINFORCE 类似：

```text
高回报动作 → 加强
低回报动作 → 削弱
```

---

## 10.2 PPO

PPO 是：

> Proximal Policy Optimization  
> 近端策略优化

它是目前非常常用的策略梯度算法。

PPO 的核心思想是：

```text
每次更新策略时，不要更新得太猛。
```

### 为什么不能更新太猛？

如果一次更新太大，策略可能突然变差。

比如机器人本来已经学会轻轻推箱子。

一次过大更新后，可能变成：

```text
用力过猛，把箱子推飞
```

PPO 通过 clipping，也就是裁剪机制，限制每次更新幅度。

---

### 类比：学游泳不要一次改太多动作

如果你一次把换气、划手、打腿全部改掉，可能反而不会游了。

更好的方式是：

```text
每次只小幅调整
稳定进步
```

PPO 就是这种“小步改进”的策略优化方法。

---

## 10.3 TRPO

TRPO 是：

> Trust Region Policy Optimization  
> 信赖域策略优化

它和 PPO 思想类似，也是限制策略更新幅度。

区别是：

- TRPO 更理论、更复杂；
- PPO 更实用、更容易实现。

可以理解为：

```text
TRPO：严格限制更新范围
PPO：用更简单方法近似达到类似效果
```

---

# 十一、Example 11.3：把箱子翻起来

这是本章第二个重要实践例子。

原文：

> Example 11.3 Flipping up the box.  
> Coming to deepnote soon. The example is available in rl/box_flipup.ipynb.

意思是：

> 例 11.3：把箱子翻起来。  
> 即将上线 deepnote。  
> 示例文件在 `rl/box_flipup.ipynb`。

---

## 11.1 任务描述

这个任务可以想象成：

```text
有一个箱子立在或倒在平面上
有一个简单的手指
目标是用手指把箱子翻到指定姿态
```

后面练习 11.3 中进一步说明：

- 机器人是一个简单的 point finger，点状手指；
- 目标是 flip over the box，把箱子翻过去；
- 使用 PPO 训练策略；
- 训练 3,000,000 步；
- 这是一个 2D 箱子翻转例子；
- 奖励是 dense reward，稠密奖励。

---

## 11.2 为什么这个例子重要？

因为它展示了：

1. 强化学习可以处理接触丰富任务；
2. 即使简单任务也可能训练很久；
3. 奖励函数设计非常关键；
4. PPO 比 REINFORCE 更稳定；
5. 操作任务中稀疏奖励会更难。

---

# 十二、11.2.5 Control for manipulation should be easy：操作控制应该会变得更容易

这一小节标题：

> 11.2.5 Control for manipulation should be easy

意思是：

> 操作控制应该会变得容易。

---

## 12.1 现在是理论 RL + 控制的好时代

原文说：

> This is a great time for theoretical RL + controls, with experts from controls embracing new techniques and insights from machine learning, and vice versa.

意思是：

> 现在是理论强化学习和控制结合的好时代。  
> 控制专家正在吸收机器学习的新技术和洞察，机器学习专家也在吸收控制理论。

通俗理解：

以前：

```text
控制理论：偏模型、稳定性、严谨
机器学习：偏数据、学习、灵活
```

现在两者越来越融合。

---

## 12.2 一个简单例子：LQR 的非凸问题也能用梯度下降

原文说：

> As a simple example, we’ve increasingly come to understand that, even though the cost landscape for many classical control problems, like the linear quadratic regulator, is not convex in the typical policy parameters, we now understand that gradient descent still works for these problems, there are no local minima.

意思是：

> 以线性二次调节器 LQR 为例，虽然代价函数在常见策略参数下不是凸的，但我们现在知道梯度下降仍然有效，没有局部最小值。

---

### 什么叫“不是凸”？

凸优化像碗底：

```text
无论从哪里开始，都能滑到最低点
```

非凸优化像山地：

```text
有很多坑，可能卡住
```

传统上，非凸问题让人担心：

```text
梯度下降会不会卡在局部最优？
```

但研究发现，对于某些控制问题，比如 LQR，虽然形式上非凸，但梯度下降仍然可以找到全局最优。

---

### 类比：看起来有很多小山包，其实没有陷阱

有些山路看起来起伏不平，你以为会卡住。

但实际地形保证：

```text
只要一直下坡，最终能到谷底
```

这就是这类控制问题的新理论认识。

---

## 12.3 这类可证明的问题范围正在扩大

原文还说：

> the class of problems/parameterizations for which we can make statements like this is growing rapidly.

意思是：

> 可以做出类似结论的问题和参数化范围正在快速扩大。

也就是说：

```text
越来越多控制问题可以被证明：
梯度方法是有效的
```

这给了人们信心：

> 强化学习和控制结合会越来越强。

---

# 十三、11.3 VALUE-BASED METHODS：基于价值的方法

PDF 中这一节只有标题：

> 11.3 VALUE-BASED METHODS

没有展开。

---

## 13.1 这一节在 PDF 中未展开

我们不能遗漏，需要说明：

> 当前 PDF 只有标题，没有正文。

---

## 13.2 补充解释：什么是 value-based methods？

基于价值的方法不是直接学策略，而是先学价值函数。

价值函数回答：

> 在某个状态下，未来大概能拿多少总奖励？

或者：

> 在某个状态下做某个动作，未来大概能拿多少总奖励？

常见算法包括：

- Q-learning；
- DQN；
- SARSA。

---

### 类比：先评估局势，再决定动作

下棋时：

```text
这个局面值 80 分
那个局面值 30 分
```

你会选择走向高分局面。

基于价值的方法就是：

```text
先学会给局面打分
再根据分数选动作
```

---

# 十四、11.4 MODEL-BASED RL：基于模型的强化学习

PDF 中这一节只有标题：

> 11.4 MODEL-BASED RL

没有展开。

---

## 14.1 这一节在 PDF 中未展开

同样需要说明：

> 当前 PDF 只有标题。

---

## 14.2 补充解释：什么是 model-based RL？

基于模型的强化学习会尝试学习环境模型。

也就是：

```text
给定当前状态和动作，预测下一个状态和奖励
```

然后可以利用模型进行：

- 规划；
- 想象未来；
- 生成虚拟经验；
- 优化控制。

---

### 类比：下棋时在脑中预演

基于模型的方法像：

```text
我走这一步，对手可能那样走；
然后我再这样走；
最后局势会怎样？
```

它在脑中模拟未来。

---

### 与 policy-based 的区别

策略梯度方法：

```text
直接学怎么行动
```

基于价值方法：

```text
先学局势好坏
```

基于模型方法：

```text
先学世界如何变化
```

---

# 十五、11.5 EXERCISES：练习题

这一章有三个练习。

---

# 十五 A、Exercise 11.1：Stochastic Optimization，随机优化

原文：

> Exercise 11.1 Stochastic Optimization  
> For this exercise, you will implement a stochastic optimization scheme that does not require exact analytical gradients.  
> You will work exclusively in this notebook.  
> You will be asked to complete the following steps:

意思是：

> 练习 11.1：随机优化。  
> 你将实现一种不需要精确解析梯度的随机优化方案。  
> 你将在指定 notebook 中完成。  
> 需要完成以下步骤。

---

## a. 实现带精确解析梯度的梯度下降

原文：

> Implement gradient descent with exact analytical gradients.

意思是：

先实现普通梯度下降。

假设你知道损失函数：

```text
L(θ)
```

也知道梯度：

```text
∇L(θ)
```

那么更新规则是：

```text
θ ← θ - α ∇L(θ)
```

其中 α 是学习率。

---

### 类比：知道山坡方向，直接往下走

如果你知道哪边是下坡，就可以直接走。

这就是解析梯度下降。

---

## b. 实现用近似梯度的随机梯度下降

原文：

> Implement stochastic gradient descent with approximated gradients.

意思是：

如果你不知道精确梯度，就用随机采样来估计梯度。

比如：

```text
采样一些扰动
观察损失变化
用这些变化估计梯度方向
```

---

### 类比：不知道山坡方向，只能撒沙子试探

你看不见山坡，只能：

```text
往前试探一下
往左试探一下
往右试探一下
```

然后估计哪边更低。

---

## c. 证明随机更新的期望值不因 baseline 改变

原文：

> Prove that the expected value of the stochastic update does not change with baselines.

意思是：

证明加入 baseline 后，随机更新的期望不变。

---

### 什么是 baseline？

baseline 是一个基准值，用来减少方差。

比如奖励是：

```text
100, 102, 98, 101
```

如果直接学习，波动可能较大。

减去 baseline 100：

```text
0, 2, -2, 1
```

相对好坏更清楚。

---

### 为什么 baseline 不改变期望？

因为 baseline 通常与采样动作无关，或者在期望意义下不会引入偏差。

它只是把奖励整体平移：

```text
R → R - b
```

期望更新方向不变，但方差可能降低。

---

### 类比：考试排名看相对分，不看绝对分

如果全班都加 10 分：

```text
原来 80，现在 90
原来 70，现在 80
```

相对排名没变。

baseline 类似：

> 去掉共同背景分，只看谁表现更好。

---

## d. 实现带 baseline 的随机梯度下降

原文：

> Implement stochastic gradient descent with baselines.

意思是：

在随机梯度估计中加入 baseline，以降低方差。

概念上：

```text
梯度估计 ≈ (reward - baseline) × 策略对数概率梯度
```

baseline 让学习更稳定。

---

# 十五 B、Exercise 11.2：REINFORCE

原文：

> Exercise 11.2 REINFORCE  
> For this exercise, you will implement the vanilla REINFORCE algorithm on a box pushing task.

意思是：

> 练习 11.2：REINFORCE。  
> 你将在一个箱子推动任务上实现标准 REINFORCE 算法。

---

## 任务背景

箱子推动任务可能是：

```text
用手指推动箱子
让箱子到达目标位置或姿态
```

---

## a. 实现策略损失函数

原文：

> Implement the policy loss function.

REINFORCE 的策略损失通常形式是：

```text
loss = - E[ log π(a|s) × advantage ]
```

通俗解释：

- `π(a|s)`：在状态 s 下选择动作 a 的概率；
- `advantage`：这个动作相对平均水平有多好；
- 如果 advantage 高，就增加该动作概率；
- 如果 advantage 低，就减少该动作概率。

---

### 类比：好动作要多做，坏动作要少做

如果某个动作让你得分高：

```text
增加它出现概率
```

如果某个动作让你得分低：

```text
减少它出现概率
```

---

## b. 实现价值损失函数

原文：

> Implement the value loss function.

价值函数通常用来估计：

```text
某个状态未来能拿多少奖励
```

价值损失通常是预测价值和实际回报之间的均方误差：

```text
value_loss = (V(s) - return)^2
```

---

### 类比：预测考试分数

你预测这次能考 85 分。

实际考了 78 分。

误差是：

```text
85 - 78 = 7
```

价值函数训练就是让预测越来越准。

---

## c. 实现优势函数

原文：

> Implement the advantage function.

优势函数 advantage 通常表示：

```text
实际回报比预期好多少
```

常见形式：

```text
A(s, a) = Q(s, a) - V(s)
```

或者用回报减去价值估计：

```text
A ≈ return - V(s)
```

---

### 类比：超出预期的表现

如果老师预期你考 80 分，你考了 90 分：

```text
advantage = +10
```

如果考了 70 分：

```text
advantage = -10
```

优势函数告诉策略：

```text
这个动作比平均水平好还是差
```

---

# 十五 C、Exercise 11.3：Analyzing Box Flipping with RL：分析 RL 翻箱子

原文：

> Exercise 11.3 Analyzing Box Flipping with RL  
> In this exercise, you will analyze the behavior of a PPO policy trained to flip over a box.

意思是：

> 练习 11.3：分析用强化学习训练出来的翻箱子 PPO 策略。  
> 你将分析一个用 PPO 训练、用来翻箱子的策略行为。

---

## 1. PPO 与 REINFORCE 的关系

原文说：

> Like REINFORCE, PPO is a policy-gradient method that directly optimizes the policy parameters to maximize the value function.

意思是：

> 和 REINFORCE 一样，PPO 也是策略梯度方法。  
> 它直接优化策略参数，以最大化价值函数。

---

## 2. 为什么用箱子翻转任务？

原文说：

> In order to have an easier problem to analyze, we’ll use the box flipup example from Chapter 8.  
> Our robot will be a simple point finger and the goal will be to flip over the box.

意思是：

> 为了更容易分析，我们使用第 8 章的箱子翻起例子。  
> 机器人是一个简单点状手指，目标是把箱子翻过去。

---

## 3. 变量说明

练习中提到：

- θ：箱子相对竖直方向的角度；
- θdot：箱子的角速度；
- qf：观测到的手指位置；
- qfdot：手指速度；
- uf：手指命令位置。

PDF 原文中符号因 OCR 有些缺失，但根据上下文可理解为：

```text
θ     箱子角度
θdot  箱子角速度
qf    手指位置观测
qfdot 手指速度
uf    手指命令位置
```

---

## a. 写出奖励函数，并解释每一项

原文要求：

> What is the reward function used here to train the policy? Write it down mathematically, use the modulo operator to handle the wrap-around of the angle.  
> What do the individual terms in the reward function represent? Why do they make sense?

意思是：

> 训练策略所用的奖励函数是什么？请用数学形式写出来，并使用取模运算处理角度环绕。  
> 奖励函数中各项代表什么？为什么它们合理？

---

### 奖励函数设计思想

虽然 PDF 没有直接给出完整公式，但根据任务目标可以推断，奖励函数通常包括：

1. 箱子角度接近目标角度；
2. 箱子角速度不要太大；
3. 手指动作不要过猛；
4. 可能鼓励手指接近接触点；
5. 可能惩罚控制量过大。

一个典型的稠密奖励可能类似：

```text
r =
  - angle_error(θ, θ_target)
  - c1 * θdot^2
  - c2 * uf^2
  + c3 * contact_or_progress_term
```

其中角度误差要用 modulo 处理，因为角度有环绕。

比如 359° 和 0° 其实只差 1°，不能直接算成差 359°。

角度环绕误差可以写成类似：

```text
angle_error = ((θ - θ_target + π) mod 2π) - π
```

这样误差会落在：

```text
[-π, π]
```

---

### 各项含义

#### 1. 角度误差项

```text
- angle_error^2
```

含义：

> 箱子越接近目标姿态，奖励越高。

这是主要目标。

---

#### 2. 角速度惩罚项

```text
- θdot^2
```

含义：

> 箱子不要转得太猛。

如果角速度太大，可能：

- 翻过头；
- 不稳定；
- 撞击过强。

---

#### 3. 控制量惩罚项

```text
- uf^2
```

含义：

> 手指命令不要太大。

这鼓励：

- 动作平滑；
- 节能；
- 避免暴力推箱。

---

#### 4. 进度或接触项

可能还有：

```text
+ progress_term
```

含义：

> 鼓励箱子朝目标方向转动，或者鼓励手指与箱子产生有效接触。

---

### 为什么这些项合理？

因为任务目标不是单纯“碰到箱子”，而是：

```text
稳定、可控、准确地把箱子翻到目标姿态
```

所以奖励要同时反映：

- 目标达成；
- 过程稳定；
- 控制合理。

---

## b. 解释 PPO 为什么比 REINFORCE 更稳定、更样本高效

原文说：

> Although we will not go into the exact details of how PPO works here, it works quite similarly to REINFORCE but using both  
> i) a learned value function to reduce variance, and  
> ii) an approximate objective, along with a trust-region constraint by clipping the per-sample loss to ensure that the policy is not updated too much at each step.

意思是：

> 虽然这里不详细讲 PPO 细节，但它和 REINFORCE 很相似。  
> 它使用：  
> 1. 学习到的价值函数来减少方差；  
> 2. 一个近似目标，并通过裁剪每个样本损失来施加信赖域约束，确保策略每次不会更新太多。

---

### PPO 比 REINFORCE 更稳定的原因

#### 原因一：使用价值函数减少方差

REINFORCE 直接使用总回报，波动可能很大。

比如两次尝试：

```text
第一次奖励 100
第二次奖励 0
```

梯度估计会非常不稳定。

PPO 用价值函数估计 baseline：

```text
advantage = return - V(s)
```

这样关注的是：

```text
比预期好多少
```

而不是绝对奖励。

---

#### 原因二：裁剪限制更新幅度

PPO 会限制策略概率比变化：

```text
ratio = π_new(a|s) / π_old(a|s)
```

如果 ratio 太大或太小，就裁剪。

这避免策略一次变化过大。

---

### 类比：学车时教练不让你猛打方向盘

REINFORCE 可能：

```text
这次失败很惨
下次策略大改
```

PPO 则像教练：

```text
可以调整，但每次只调一点
```

所以更稳定。

---

## c. 如果 clipping 太小或太大会怎样？

原文要求：

> how you might expect PPO to perform on the box flipping task if the clipping limits are set to be too small or too large.

意思是：

> 如果裁剪限制设置得太小或太大，PPO 在翻箱子任务上会怎样？

---

### 1. clipping 太小

如果裁剪范围太小：

```text
策略每次只能变化一点点
```

优点：

- 很稳定；
- 不容易突然变差。

缺点：

- 学习很慢；
- 可能训练很久都没明显进步；
- 样本效率低。

类比：

```text
走路步子太小，半天到不了终点
```

---

### 2. clipping 太大

如果裁剪范围太大：

```text
策略每次可以变化很多
```

优点：

- 初期可能进步快。

缺点：

- 不稳定；
- 策略可能突然变差；
- 训练震荡；
- 可能难以收敛。

类比：

```text
学车时猛打方向盘，容易失控
```

---

## d. 训练 3,000,000 步后策略如何变化？

原文说：

> We’ve trained a PPO-based policy to flip the box for 3,000,000 steps.  
> How does the policy perform as the number of steps increases?  
> Write qualitatively how the policy changes over time and which parts of the reward function are having the greatest effect at each step.

意思是：

> 我们训练了一个基于 PPO 的翻箱策略，共 3,000,000 步。  
> 随着步数增加，策略表现如何？  
> 请定性描述策略随时间如何变化，以及奖励函数中哪些部分在每个阶段影响最大。

---

### 典型训练阶段

虽然 PDF 没有给出具体曲线，但根据强化学习训练规律，可以定性描述为几个阶段。

---

#### 阶段一：早期随机探索

策略刚开始几乎是随机的。

表现：

```text
手指乱动
箱子偶尔动一下
很少成功翻起
奖励低且波动大
```

此时影响最大的是：

```text
探索
```

奖励函数中：

- 任何微小进度项；
- 接触项；
- 角度变化项；

会帮助策略发现“碰箱子有用”。

---

#### 阶段二：学会接触箱子

策略开始知道：

```text
手指要靠近并接触箱子
```

表现：

```text
手指会主动推向箱子
箱子开始被推动或倾斜
但经常失败或翻过头
```

此时影响最大的是：

```text
接触/进度奖励
```

---

#### 阶段三：学会推动方向

策略开始理解：

```text
要在正确方向施力
```

表现：

```text
箱子角度逐渐接近目标
但速度和力度控制不好
```

此时影响最大的是：

```text
角度误差项
```

---

#### 阶段四：学会稳定翻转

策略开始变得更平滑。

表现：

```text
箱子能翻起
但有时不稳定
```

此时影响最大的是：

```text
角速度惩罚
控制量惩罚
```

它们促使动作更柔和。

---

#### 阶段五：策略成熟

策略能够较稳定地翻箱。

表现：

```text
手指接近箱子
施加合适推力
箱子翻到目标姿态
动作较平滑
```

此时奖励函数整体共同作用：

```text
角度误差小
角速度适中
控制量合理
```

---

# 十六、练习后面那段重要讨论：强化学习在操作任务中难在哪里？

PDF 在练习 11.3 后面有一段非常重要的总结。

---

## 16.1 即使简单操作任务，训练也可能很慢

原文说：

> Notice how much time it takes to train a working policy, even for a simple manipulation problem like the 2D box flipping example with a point finger and a dense reward.

意思是：

> 注意训练出一个可用策略需要多少时间，即使只是一个简单的 2D 翻箱任务，机器人只是点状手指，而且奖励还是稠密的。

通俗理解：

这个任务已经很简单了：

- 2D；
- 一个手指；
- 一个箱子；
- 稠密奖励。

但训练仍然需要 3,000,000 步。

这说明：

> 强化学习训练机器人并不轻松。

---

## 16.2 更难的操作任务会非常困难

原文说：

> Harder problems in manipulation, such as pick and place, can become extremely challenging to train naively with Reinforcement Learning, especially with sparse rewards such as in typical pick and place tasks where you only receive a reward when the object has been picked or placed in the right location.

意思是：

> 更复杂的操作问题，比如抓取并放置，如果天真地用强化学习训练，会极其困难。  
> 尤其是稀疏奖励情况下。  
> 典型 pick and place 任务中，只有物体被抓起或放到正确位置时才有奖励。

---

### 什么是 sparse reward？稀疏奖励？

稀疏奖励是：

> 大部分时间没有奖励，只有最后成功才有奖励。

比如：

```text
抓杯子：
- 移动中：0 分
- 靠近杯子：0 分
- 碰到杯子：0 分
- 成功抓起：+1 分
```

这会导致学习非常慢。

因为机器人一开始随机乱动，可能很久都得不到 +1 分。

---

### 类比：迷宫只有走到出口才给分

如果迷宫每走一步都不给反馈，只有到出口才给 100 分。

学习者很难知道：

```text
刚才哪一步是对的
```

这就是稀疏奖励问题。

---

## 16.3 稠密奖励更容易学

稠密奖励是：

> 每一步都有反馈。

比如翻箱子任务：

```text
箱子角度更接近目标：+分
角速度太大：-分
控制太猛：-分
```

这样策略更容易知道该怎么改进。

---

## 16.4 强化学习在接触丰富任务中可能表现很好

原文说：

> On the other hand, reinforcement learning can work well in contact-rich settings, as in the box flipping example.

意思是：

> 另一方面，强化学习在接触丰富的场景中可能表现很好，比如翻箱子例子。

接触丰富任务包括：

- 推；
- 翻；
- 挤；
- 摩擦；
- 碰撞；
- 灵巧操作。

这些任务很难用简单控制规则写清楚，但强化学习可以从试错中学。

---

## 16.5 例子：RL 解魔方

原文说：

> see RL solving a rubik’s cube with one hand for an example of RL being used to solve a contact-rich manipulation task.

意思是：

> 可以看“用一只手解魔方”的强化学习例子，它是接触丰富操作任务。

但作者也提醒：

> note this also depended heavily on things like domain randomization, curriculum learning, large scale compute, etc.

意思是：

> 这个成功也严重依赖域随机化、课程学习、大规模计算等。

---

### 1. domain randomization：域随机化

随机化：

- 摩擦；
- 质量；
- 光照；
- 相机；
- 物体尺寸；
- 控制延迟。

让策略更 robust。

---

### 2. curriculum learning：课程学习

先学简单任务，再学难任务。

比如：

```text
先学抓住魔方
再学转动一面
最后学完整还原
```

---

### 3. large scale compute：大规模计算

训练需要大量仿真和计算资源。

---

## 16.6 locomotion 和 manipulation 的故事不同

原文说：

> The story in locomotion, on the other hand, seems to be quite different, perhaps because it is easier to design dense rewards and to automate resets in simulation.

意思是：

> 另一方面，运动控制 locomotion 的情况似乎很不同。  
> 也许是因为在仿真中更容易设计稠密奖励，也更容易自动重置。

---

### locomotion 是什么？

locomotion 是移动运动，比如：

- 四足机器人走路；
- 双足机器人行走；
- 机器狗跑跳。

为什么 RL 在 locomotion 中常常更容易？

因为：

1. 奖励容易设计：
   - 前进速度；
   - 保持直立；
   - 节能；
   - 步态平滑。

2. 重置容易：
   - 摔倒了就重新站好；
   - 仿真里可以批量并行；
   - 不需要复杂场景复位。

而操作任务常常需要：

- 精确目标；
- 物体摆放；
- 接触细节；
- 抓取成功判定；
- 场景复位更复杂。

---

# 十七、REFERENCES：参考文献通俗导读

PDF 最后列了 3 篇参考文献。

---

## 参考文献 1

> Richard S. Sutton and Andrew G. Barto, “Reinforcement Learning: An Introduction”, MIT Press, 2018.

作用：

- 强化学习经典入门书；
- 作者称它是经典且仍然最好的 RL 入门书；
- 适合建立基础概念。

---

## 参考文献 2

> Alekh Agarwal and Nan Jiang and Sham M. Kakade and Wen Sun, “Reinforcement Learning: Theory and Algorithms”, Online Draft, 2020.

作用：

- 更偏理论；
- 适合想深入理解 RL 算法和理论保证的人。

---

## 参考文献 3

> Csaba Szepesvari, “Algorithms for Reinforcement Learning”, Morgan and Claypool Publishers, 2010.

作用：

- 也是偏理论和算法的 RL 参考书；
- 适合补充理论基础。

---

# 十八、文档末尾信息

PDF 最后有：

> Previous Chapter  
> Table of contents  
> Next Chapter  
> Accessibility  
> © Russ Tedrake, 2024

这些是：

- 上一章；
- 目录；
- 下一章；
- 无障碍声明；
- 版权信息。

---

# 十九、代码与实验实践重点补充

这部分是你特别强调的重点。

PDF 这一章的代码实践没有完全展开，很多例子写着：

> Coming to deepnote soon.

但已经给出了文件名和方向。

下面我把实践部分重点补充。

---

## 19.1 实验一：用 Gymnasium 包装 Drake 环境

对应 PDF：

> Example 11.1 Using a Drake simulation as a Gym environment

---

### 19.1.1 实验目标

把一个 Drake 仿真环境包装成 Gym 环境，使强化学习算法可以：

```text
reset()
step(action)
得到 observation, reward, terminated, truncated, info
```

---

### 19.1.2 概念流程

```text
建立 Drake System
↓
指定 action input port
↓
指定 observation output port
↓
定义 reward
↓
用 DrakeGymEnv 包装
↓
交给 Stable Baselines3 训练
```

---

### 19.1.3 伪代码示例

下面不是 PDF 原文代码，而是帮助理解的伪代码：

```python
from pydrake.gym import DrakeGymEnv
from stable_baselines3 import PPO

def make_simulator():
    # 创建 Drake 系统和仿真器
    system = build_robot_system()
    simulator = Simulator(system)
    return simulator

env = DrakeGymEnv(
    simulator_factory=make_simulator,
    time_step=0.01,
    obs_output_port=observation_port,
    action_input_port=action_port,
    reward=reward_function,
)

model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=1_000_000)
```

---

### 19.1.4 reward_function 示例

比如翻箱子任务：

```python
import numpy as np

def angle_wrap(a):
    return (a + np.pi) % (2 * np.pi) - np.pi

def reward_function(context):
    theta = get_box_angle(context)
    theta_dot = get_box_angular_velocity(context)
    uf = get_finger_command(context)

    target_theta = 0.0

    angle_error = angle_wrap(theta - target_theta)

    r = (
        -10.0 * angle_error**2
        -0.1 * theta_dot**2
        -0.01 * uf**2
    )

    return r
```

---

### 19.1.5 实践注意点

#### 1. observation 要包含足够信息

比如：

```text
箱子角度
箱子角速度
手指位置
手指速度
```

如果观测不足，策略可能学不会。

比如只给手指位置，不给箱子角度，机器人不知道箱子状态。

---

#### 2. action 范围要合理

如果动作范围太大：

```text
手指命令可能暴力冲撞
```

如果太小：

```text
可能无法翻动箱子
```

通常需要对 action space 做归一化或限幅。

---

#### 3. reward 要稠密

如果只有成功才给奖励：

```text
reward = 1 if success else 0
```

学习会非常慢。

更好是加入过程奖励：

```text
角度接近目标
角速度合理
控制平滑
```

---

#### 4. 每次 reset 要随机化

为了训练鲁棒策略，可以随机化：

```text
箱子初始角度
箱子位置
手指初始位置
摩擦系数
物体质量
```

---

## 19.2 实验二：黑箱优化训练策略

对应 PDF：

> Example 11.2 Black-box optimization  
> rl/black_box.ipynb

---

### 19.2.1 实验目标

不使用梯度，直接通过运行仿真评估策略参数，然后优化参数。

---

### 19.2.2 概念流程

```text
给定策略参数 θ
↓
运行多次仿真
↓
每次得到总回报 J(θ)
↓
黑箱优化算法根据 J(θ) 更新 θ
```

---

### 19.2.3 伪代码示例

```python
import nevergrad as ng

def evaluate_policy(theta):
    total_reward = 0.0

    for episode in range(num_episodes):
        obs = env.reset()
        done = False

        while not done:
            action = policy(obs, theta)
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            total_reward += reward

    return total_reward / num_episodes

def objective(theta):
    # Nevergrad 通常最小化，所以取负号
    return -evaluate_policy(theta)

param = ng.p.Array(shape=(num_params,))
optimizer = ng.optimizers.NGO(parametrization=param, budget=200)

recommendation = optimizer.minimize(objective)
best_theta = recommendation.value
```

---

### 19.2.4 实践注意点

#### 1. 黑箱优化通常需要很多次仿真

因为每次评估都要运行完整 episode。

所以：

```text
仿真成本高
训练慢
```

---

#### 2. 多次评估取平均

由于环境随机，单次评估不可靠。

应该：

```text
同一个 θ 跑多个 episode
取平均回报
```

---

#### 3. 参数维度不要太高

黑箱优化适合：

```text
低维参数
```

如果策略是大型神经网络，参数上万，黑箱优化通常很难。

这时更适合策略梯度方法。

---

## 19.3 实验三：REINFORCE 实现

对应 PDF：

> Exercise 11.2 REINFORCE

---

### 19.3.1 实验目标

在箱子推动任务中实现：

```text
policy loss
value loss
advantage
```

---

### 19.3.2 REINFORCE 基本训练循环

```python
for episode in range(num_episodes):
    obs = env.reset()
    done = False

    log_probs = []
    rewards = []
    values = []

    while not done:
        action, log_prob, value = policy(obs)
        next_obs, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated

        log_probs.append(log_prob)
        rewards.append(reward)
        values.append(value)

        obs = next_obs

    returns = compute_returns(rewards)
    values = torch.stack(values)
    advantages = returns - values

    policy_loss = -(torch.stack(log_probs) * advantages).mean()
    value_loss = ((returns - values) ** 2).mean()

    loss = policy_loss + value_loss

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
```

---

### 19.3.3 compute_returns 示例

```python
def compute_returns(rewards, gamma=0.99):
    returns = []
    G = 0.0

    for r in reversed(rewards):
        G = r + gamma * G
        returns.insert(0, G)

    return torch.tensor(returns)
```

---

### 19.3.4 实践注意点

#### 1. 奖励要归一化

如果奖励范围很大，训练不稳定。

可以：

```text
标准化 returns
```

---

#### 2. 使用 baseline

直接用 returns 方差大。

使用：

```text
advantages = returns - values
```

会更稳定。

---

#### 3. 策略网络输出要合理

如果动作连续，通常输出：

```text
均值 mean
标准差 std
```

然后从正态分布采样动作。

---

## 19.4 实验四：PPO 训练翻箱子策略

对应 PDF：

> Example 11.3 Flipping up the box  
> Exercise 11.3 Analyzing Box Flipping with RL

---

### 19.4.1 实验目标

使用 PPO 训练一个策略，让点状手指把箱子翻到目标姿态。

---

### 19.4.2 使用 Stable Baselines3 的简化流程

```python
from stable_baselines3 import PPO

env = make_box_flipup_env()

model = PPO(
    policy="MlpPolicy",
    env=env,
    learning_rate=3e-4,
    n_steps=2048,
    batch_size=64,
    gamma=0.99,
    clip_range=0.2,
    verbose=1
)

model.learn(total_timesteps=3_000_000)

model.save("ppo_box_flipup")
```

---

### 19.4.3 关键超参数解释

#### 1. clip_range

PPO 的裁剪范围。

常见值：

```text
0.1 到 0.3
```

太小：

```text
学习慢
```

太大：

```text
不稳定
```

---

#### 2. gamma

折扣因子。

接近 1：

```text
更重视长期奖励
```

太小：

```text
只看眼前奖励
```

---

#### 3. n_steps

每次收集多少步经验。

太小：

```text
估计不稳定
```

太大：

```text
内存和计算成本增加
```

---

## 19.5 实验五：奖励函数实验

这是操作任务中最重要的实践之一。

---

### 19.5.1 对比稀疏奖励和稠密奖励

#### 稀疏奖励版本

```python
def sparse_reward(context):
    if box_is_flipped(context):
        return 1.0
    else:
        return 0.0
```

问题：

```text
很难学到
```

---

#### 稠密奖励版本

```python
def dense_reward(context):
    theta = get_box_angle(context)
    theta_dot = get_box_angular_velocity(context)
    uf = get_finger_command(context)

    angle_error = angle_wrap(theta - target_theta)

    return (
        -10.0 * angle_error**2
        -0.1 * theta_dot**2
        -0.01 * uf**2
    )
```

优点：

```text
每一步都有反馈
学习更容易
```

---

### 19.5.2 奖励函数调试建议

#### 1. 先可视化奖励

不要只看训练曲线。

要手动检查：

```text
成功状态奖励是否高？
失败状态奖励是否低？
中间过程是否合理？
```

---

#### 2. 避免奖励 hacking

比如如果你只奖励“手指移动距离”，策略可能学会：

```text
手指疯狂乱动
但不翻箱子
```

所以奖励必须和真实目标一致。

---

#### 3. 各项权重要平衡

如果控制惩罚太大：

```text
机器人不敢动
```

如果角度奖励太大：

```text
可能暴力翻箱
```

需要反复调整权重。

---

## 19.6 实验六：SimulatorFactory 和域随机化

对应 PDF：

> SimulatorFactory is core to the stochastic system modeling framework in Drake.

---

### 19.6.1 实验目标

每次 reset 时生成不同环境，提高策略鲁棒性。

---

### 19.6.2 伪代码示例

```python
import random

def make_simulator():
    system = build_box_finger_system()

    # 随机化参数
    friction = random.uniform(0.3, 0.9)
    box_mass = random.uniform(0.5, 2.0)
    initial_angle = random.uniform(-np.pi, np.pi)

    set_friction(system, friction)
    set_box_mass(system, box_mass)
    set_initial_box_angle(system, initial_angle)

    simulator = Simulator(system)
    return simulator
```

---

### 19.6.3 实践注意点

#### 1. 随机化不能太离谱

如果随机化范围太大：

```text
有些环境根本不可能成功
```

策略会很难学。

---

#### 2. 随机化要贴近真实不确定性

比如：

- 摩擦不确定；
- 质量不确定；
- 初始位置不确定；
- 控制延迟；
- 传感器噪声。

---

# 二十、与 PDF 逐项对照检查

下面我按 PDF 内容逐项检查，确认是否遗漏，并补充说明。

| PDF 位置 | 内容要点 | 是否已讲解 | 补充说明 |
|---|---|---:|---|
| 文档标题 | Robotic Manipulation: Perception, Planning, and Control | 已讲解 | 解释了感知、规划、控制 |
| 作者 | Russ Tedrake | 已讲解 | 已说明 |
| 版权 | © Russ Tedrake, 2020-2024 | 已讲解 | 已说明 |
| 修改时间 | Last modified 2025-11-12 | 已讲解 | 已说明 |
| 引用反馈 | How to cite, annotations, feedback | 已讲解 | 已说明 |
| 工作笔记 | MIT course working notes, Fall 2024 | 已讲解 | 已说明 |
| 导航 | Previous/TOC/Next | 已讲解 | 已说明 |
| 章节标题 | Chapter 11 Reinforcement Learning | 已讲解 | 已解释强化学习 |
| 引言 1 | RL 很热门，文献多，范围广 | 已讲解 | 已说明 |
| 引言 2 | Sutton and Barto 是经典入门 | 已讲解 | 已列入参考文献 |
| 引言 3 | 理论参考 [2,3] | 已讲解 | 已列入参考文献 |
| 引言 4 | 在线课程 Stanford CS234, Berkeley CS285, DeepMind x UCL | 已讲解 | 已提及 |
| 作者目标 | 提供基础，聚焦 manipulation 相关 RL | 已讲解 | 已解释 |
| manipulation 是 RL playground | rich perception, diverse environments, contact mechanics | 已讲解 | 已举例 |
| 核心研究成果来自 manipulation | 已讲解 | 已举例 |
| 11.1 RL SOFTWARE | RL 工具箱多，Gymnasium 是标准 | 已讲解 | 已解释 |
| Gymnasium 简称 Gym | 已讲解 | 已说明 |
| Gym vs Drake 接口 | 已讲解 | 用专业厨房/快餐接口类比 |
| Drake 目标 | 表达和优化动力系统，利用结构 | 已讲解 | 已解释 |
| Gym 目标 | 最小细节，统一接口 | 已讲解 | 已解释 |
| 任何 Drake system 可包装成 Gym | 已讲解 | 已说明 |
| Example 11.1 | Drake simulation as Gym environment | 已讲解 | 已重点补充 |
| reset/step/render | 已讲解 | 已逐个解释 |
| step 返回 observation/reward/termination | 已讲解 | 已解释 |
| DrakeGymEnv import | from pydrake.gym import DrakeGymEnv | 已讲解 | 已列出 |
| DrakeGymEnv constructor | Simulator, action port, observation port | 已讲解 | 已解释 |
| reward 实现 | Context 函数或 output port | 已讲解 | 已解释 |
| Simulator vs System | DrakeGymEnv built around Simulator | 已讲解 | 已解释 |
| SimulatorFactory | 生成随机 Simulator | 已讲解 | 已重点解释 |
| Gym env in Drake ecosystem | 可以用，但少一些高级算法 | 已讲解 | 已说明 |
| 推荐 Drake | 动力系统库、物理引擎、对比 model-based | 已讲解 | 已解释 |
| 作者 bias | 承认偏袒 Drake | 已讲解 | 已提及 |
| sim2real 争论 | 建模仔细不一定更差 | 已讲解 | 已解释 |
| uncertainty models | 不确定性模型很重要 | 已讲解 | 已举例 |
| RL+control 挑战 | 模型既要丰富又要有结构 | 已讲解 | 已解释 |
| 模型随数据改进 | continually expand and improve with data | 已讲解 | 已说明 |
| Gymnasium 不提供算法 | 只提供环境接口 | 已讲解 | 已说明 |
| Stable Baselines3 | 推荐 PyTorch 算法库 | 已讲解 | 已说明 |
| black-box optimization | Nevergrad | 已讲解 | 已解释 |
| 11.2 POLICY-GRADIENT METHODS | 策略梯度方法 | 已讲解 | 已解释 |
| 11.2.1 Black-box optimization | 黑箱优化 | 已讲解 | 已补充 |
| Example 11.2 | rl/black_box.ipynb | 已讲解 | 已补充伪代码 |
| 11.2.2 Stochastic optimal control | 标题未展开 | 已讲解 | 已补充概念 |
| 11.2.3 Using gradients of policy, not environment | 已讲解 | 已解释 |
| 更多推导见链接 | 已讲解 | 已说明 |
| 11.2.4 REINFORCE, PPO, TRPO | 已讲解 | 已分别解释 |
| Example 11.3 | Flipping up the box, rl/box_flipup.ipynb | 已讲解 | 已解释 |
| 11.2.5 Control for manipulation should be easy | 已讲解 | 已解释 |
| RL+controls 好时代 | 已讲解 | 已说明 |
| LQR 非凸但梯度下降有效 | 已讲解 | 用山地/碗底类比 |
| no local minima | 已讲解 | 已解释 |
| 问题范围扩大 | 已讲解 | 已说明 |
| 11.3 VALUE-BASED METHODS | 标题未展开 | 已讲解 | 已补充概念 |
| 11.4 MODEL-BASED RL | 标题未展开 | 已讲解 | 已补充概念 |
| 11.5 EXERCISES | 三个练习 | 已讲解 | 已逐项解释 |
| Exercise 11.1 | Stochastic Optimization | 已讲解 | 已逐项解释 |
| 11.1.a | exact analytical gradients | 已讲解 | 已解释 |
| 11.1.b | approximated gradients | 已讲解 | 已解释 |
| 11.1.c | baseline 不改变期望 | 已讲解 | 已解释 |
| 11.1.d | SGD with baselines | 已讲解 | 已解释 |
| Exercise 11.2 | REINFORCE | 已讲解 | 已逐项解释 |
| 11.2.a | policy loss | 已讲解 | 已解释 |
| 11.2.b | value loss | 已讲解 | 已解释 |
| 11.2.c | advantage function | 已讲解 | 已解释 |
| Exercise 11.3 | Analyzing Box Flipping with RL | 已讲解 | 已详细解释 |
| PPO 类似 REINFORCE | 已讲解 | 已解释 |
| 使用 value function 降方差 | 已讲解 | 已解释 |
| clipping trust region | 已讲解 | 已解释 |
| 奖励函数数学形式 | 已讲解 | 已补充可能形式和角度 wrap |
| clipping 太小/太大 | 已讲解 | 已解释 |
| 3,000,000 steps 训练变化 | 已讲解 | 已分阶段描述 |
| 简单任务也训练久 | 已讲解 | 已强调 |
| pick and place 难 | 已讲解 | 已解释 |
| sparse rewards 难 | 已讲解 | 已用迷宫类比 |
| contact-rich RL 可有效 | 已讲解 | 已解释 |
| Rubik’s cube 例子 | 已讲解 | 已提及 |
| domain randomization | 已讲解 | 已解释 |
| curriculum learning | 已讲解 | 已解释 |
| large scale compute | 已讲解 | 已解释 |
| locomotion 不同 | 已讲解 | 已解释 |
| dense rewards/automatic resets | 已讲解 | 已解释 |
| References 1-3 | 已讲解 | 已逐条说明 |
| 末尾导航/Accessibility/copyright | 已讲解 | 已说明 |

---

# 二十一、检查后发现的“需要更通俗或补充”的地方

虽然上面已经覆盖 PDF 内容，但为了响应你的要求，我再单独指出哪些地方原本可能不够直观，并已经补充。

---

## 21.1 “Gym 接口”需要更生活化解释

PDF 原文只说：

> reset(), step(), render()

补充：

可以把 Gym 环境理解成一个游戏机：

```text
reset()：重新开始
step(action)：按手柄走一步
render()：显示画面
```

强化学习算法只需要会按手柄，不需要知道游戏机内部电路。

---

## 21.2 “Drake System vs Gym Env”需要更清楚

PDF 原文比较抽象。

补充：

Drake：

```text
我知道系统内部物理结构
```

Gym：

```text
我不管内部，只要能交互
```

这就是两者最大区别。

---

## 21.3 “SimulatorFactory”需要例子

PDF 原文：

> a function that can produce simulators

补充：

它就像场景生成器：

```text
每次 reset 都生成一个新随机场景
```

例如：

```text
场景 1：箱子轻，摩擦高
场景 2：箱子重，摩擦低
场景 3：初始角度随机
```

---

## 21.4 “黑箱优化”需要例子

PDF 只给标题。

补充：

黑箱优化像调收音机旋钮：

```text
不知道内部电路
只知道声音好不好
靠反复试调出最佳位置
```

---

## 21.5 “策略梯度”需要例子

补充：

策略梯度像直接调整运动员动作：

```text
投进了 → 这个姿势多一点
投丢了 → 这个姿势少一点
```

而不是先给局势打分。

---

## 21.6 “PPO clipping”需要例子

补充：

PPO clipping 像教练限制你：

```text
每次只允许改一点点动作
不允许一次大改
```

这样不容易学崩。

---

## 21.7 “稀疏奖励”需要强例子

PDF 提到 pick and place。

补充：

稀疏奖励像走迷宫只有到出口才给分。

大部分动作都是 0 分，学习者很难知道哪步有用。

---

## 21.8 “稠密奖励”需要例子

补充：

翻箱子稠密奖励：

```text
箱子角度更接近目标：加分
角速度太大：扣分
控制太猛：扣分
```

这样每一步都有反馈。

---

## 21.9 “locomotion 为什么更容易”需要例子

补充：

机器狗走路奖励很容易设计：

```text
向前走：加分
摔倒：扣分
能量小：加分
```

而且摔倒了仿真里可以马上重置。

操作任务则经常需要精确摆放物体，重置更麻烦。

---

# 二十二、最终综合版总结：这一章的完整故事

把所有内容压缩成一个完整故事。

---

## 22.1 强化学习是什么？

强化学习是让机器人通过试错学习：

```text
状态 → 动作 → 奖励 → 更新策略
```

它不需要人手写所有控制规则，而是让机器人从经验中学。

---

## 22.2 为什么机器人操作适合强化学习？

因为操作任务有：

1. 丰富感知；
2. 多样环境；
3. 复杂接触；
4. 难以手工设计规则。

比如：

- 翻箱子；
- 推物体；
- 抓取；
- 放置；
- 灵巧手操作。

---

## 22.3 软件接口：Gymnasium 和 Drake

强化学习常用接口是：

```text
Gymnasium
```

它提供：

```text
reset()
step()
render()
```

Drake 提供：

```text
精确动力系统建模
接触物理仿真
控制算法工具
```

两者可以结合：

```text
Drake 仿真 → DrakeGymEnv → Gym 接口 → RL 算法
```

---

## 22.4 算法路线

本章提到几类方法：

### 1. 黑箱优化

```text
不需要梯度
直接试参数
适合低维问题
```

代表工具：

```text
Nevergrad
```

---

### 2. 策略梯度方法

```text
直接优化策略
适合连续控制
```

代表算法：

```text
REINFORCE
TRPO
PPO
```

---

### 3. 基于价值的方法

```text
先学价值函数
再选择动作
```

PDF 未展开，但常见算法有：

```text
DQN
Q-learning
SARSA
```

---

### 4. 基于模型的强化学习

```text
学习环境如何变化
用模型预测未来
```

PDF 未展开，但思想是：

```text
在脑中模拟未来，再决策
```

---

## 22.5 实践主线

本章实践可以概括为：

```text
建立 Drake 仿真环境
↓
用 DrakeGymEnv 包装成 Gym 环境
↓
定义 observation、action、reward
↓
使用黑箱优化或策略梯度算法训练
↓
分析策略行为
↓
调整奖励函数和超参数
↓
提高鲁棒性和成功率
```

---

## 22.6 关键经验

这一章还传递了几个重要经验：

### 1. 奖励函数非常关键

稠密奖励比稀疏奖励更容易学。

---

### 2. PPO 比 REINFORCE 更稳定

因为 PPO：

- 使用价值函数减少方差；
- 使用 clipping 限制更新幅度。

---

### 3. 即使简单任务也可能训练很久

一个 2D 点状手指翻箱任务都可能需要 3,000,000 步。

---

### 4. 接触丰富任务可能适合 RL

比如翻箱、推物、灵巧操作。

---

### 5. pick and place 等稀疏奖励任务很难

如果只有成功抓取或放置才有奖励，训练会非常困难。

---

### 6. 成功的大规模 RL 往往依赖额外技巧

比如：

- domain randomization；
- curriculum learning；
- large scale compute；
- 精心奖励设计；
- 仿真并行化。

---

## 22.7 最终一句话总结

这一章的核心是：

> 强化学习为机器人操作提供了一种“从试错中学控制策略”的方法。  
> 它特别适合感知复杂、环境多样、接触丰富的任务。  
> 但在实践中，它非常依赖环境接口、奖励函数设计、仿真随机化、算法稳定性和大量训练计算。  
> 对机器人操作来说，强化学习很有潜力，但绝不是“简单训练一下就能成功”的方法。