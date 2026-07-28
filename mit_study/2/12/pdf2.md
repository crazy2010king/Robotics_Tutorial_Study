下面给你一份**最终整合版**的通俗讲解。我会先把 PDF《Chapter 12: Soft Robots and Tactile Sensing》从头到尾、按顺序、逐段讲清楚；讲完后，再逐项和 PDF 对照，检查有没有遗漏、哪里不够通俗；然后重点补充代码/实验实践部分；最后再整体综合成一个完整版本。

---

# 一、全文总览：这一章到底在讲什么？

这一章标题是：

> **Chapter 12: Soft Robots and Tactile Sensing**  
> 软体机器人与触觉感知

如果用一句最通俗的话概括：

> 这一章讲的是：机器人不能只靠“眼睛”和“关节角度传感器”，还应该学会“触摸”；同时，机器人本体也不一定非要硬邦邦，软体机器人可能更适合接触、抓取和操作。

我们可以把这一章理解成两个主题：

1. **触觉 sensing / touch**  
   机器人怎么知道自己碰到了什么？碰在哪里？力度多大？物体是不是要滑走？

2. **软体机器人 soft robots**  
   机器人身体、手指、皮肤如果更柔软，会不会更容易安全地接触环境、感知接触、完成操作？

这两个主题看起来像两件事，但作者把它们放在一章，因为：

> 软体结构天然适合触觉感知；  
> 触觉感知也常常是软体机器人最自然的传感方式。

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
- **感知**：机器人“看见”和“感觉”环境。
- **规划**：机器人决定“该怎么动”。
- **控制**：机器人真正执行动作。

---

## 2. 版权与修改时间

PDF 中写：

> © Russ Tedrake, 2020-2024  
> Last modified 2025-8-26.

意思是：

- 讲义版权从 2020 到 2024；
- 最后修改时间是 2025 年 8 月 26 日。

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

# 三、章节引言：为什么机器人需要“触觉”和“软体身体”？

这一章开头先回顾了前面的假设。

原文大意：

> 到目前为止，我们一直假设相机和本体感受，比如关节传感，是机器人获取世界信息的主要来源。  
> 但还有另一个显然必须讨论的传感模态——触觉。  
> 本章第一个目标是探索传感硬件的最新进展，以及能够利用这些信息的计算框架。

---

## 1. 之前机器人主要靠什么感知？

在前面章节中，机器人主要依赖：

### 1. 相机 cameras

相机像机器人的“眼睛”。

它提供：

- RGB 图像；
- 深度图；
- 点云；
- 物体位置；
- 物体类别；
- 物体掩码。

### 2. 本体感受 proprioceptive sensing

本体感受是机器人感知自己身体状态的能力。

比如：

- 关节角度；
- 关节速度；
- 关节力矩；
- 夹爪开合程度；
- 手指位置。

通俗理解：

> 相机让机器人知道“外面是什么样”；  
> 本体感受让机器人知道“自己身体是什么样”。

---

## 2. 但还缺少一种关键感觉：触觉

原文说：

> There is another obvious sensor modality that we must discuss — the sense of touch.

意思是：

> 还有另一种显然必须讨论的传感模态——触觉。

触觉回答的问题是：

```text
我碰到了吗？
碰到了哪里？
碰到了什么？
力有多大？
物体是不是在滑动？
物体是硬还是软？
抓稳了吗？
```

这些很多时候相机看不清楚，关节传感器也推断不够。

---

## 3. 类比：人类拿杯子不只靠眼睛

你拿起一个杯子时，不只是用眼睛看。

你还靠触觉知道：

- 杯子是不是太滑；
- 有没有抓紧；
- 力度是不是太大；
- 杯子是不是在往下滑；
- 杯子里有没有水；
- 杯子是不是热的。

如果只靠眼睛：

```text
看见杯子 → 伸手 → 抓住
```

一旦：

- 杯子透明；
- 光线不好；
- 杯子被手挡住；
- 杯中有液体；
- 杯子很滑；

只靠视觉就容易失败。

机器人也一样。

---

## 4. 听觉也可能重要，但目前研究较少

原文还提到：

> Hearing, the sense that enables the perception of sound, is likely the next most important sensing modality for humans in manipulation, but so far this field is relatively unexplored.

意思是：

> 听觉，也就是感知声音的能力，可能是人类操作中第二重要的传感模态。  
> 但目前在机器人领域，这个方向还相对未被充分探索。

通俗理解：

人类操作物体时也会听：

- 拧瓶盖时有没有咔哒声；
- 敲击物体判断材质；
- 听电机声音判断是否卡住；
- 听物体掉落声音判断是否成功。

但机器人领域目前对听觉研究还比较少。

---

## 5. 另一个趋势：软体机器人

原文说：

> Another important trend in manipulation research is the design and fabrication of robots that are fundamentally soft.

意思是：

> 操作研究中的另一个重要趋势，是设计和制造本质上柔软的机器人。

---

### 为什么需要软体机器人？

原文说：

> Manipulation requires rich contact interactions with the environment.  
> Most of the robots we’ve discussed so far are relatively very rigid; but they do always have something like rubber pads in the finger tips.

意思是：

> 操作任务需要与环境发生丰富接触。  
> 我们之前讨论的大多数机器人都相对非常刚硬；  
> 但它们指尖通常还是会有一些类似橡胶垫的东西。

通俗理解：

机器人操作离不开接触：

- 抓；
- 推；
- 捏；
- 按；
- 摩擦；
- 碰撞。

传统机器人本体很硬，但指尖往往会贴一层软垫。

这说明：

> 即使在传统刚性机器人上，人们也承认“柔软接触面”是有用的。

---

### 类比：为什么锤子手柄要包橡胶？

锤子本身是硬的，但手柄常常包橡胶。

因为：

- 更防滑；
- 更减震；
- 更舒适；
- 更好控制。

机器人指尖加橡胶垫也是类似道理：

```text
硬机器人 + 软指尖
```

而软体机器人则更进一步：

```text
整个手指、手掌、皮肤、甚至身体都可能是软的
```

---

## 6. 本章第二个目标：软体机器人硬件和计算框架

原文说：

> My second goal for this chapter is to explore advances in soft robot hardware, but also in the computational frameworks that can deal with soft robots.

意思是：

> 本章第二个目标是探索软体机器人硬件的进展，以及能够处理软体机器人的计算框架。

也就是说，这一章不仅关心：

- 软体机器人怎么做出来；

还关心：

- 怎么仿真；
- 怎么建模；
- 怎么控制；
- 怎么感知。

---

## 7. 为什么把“软体机器人”和“触觉”放在一章？

原文说：

> These seem to be two separable ideas; so why am I putting them together into a single chapter?  
> It turns out that being soft can enable tactile sensing.  
> One might even argue that it’s required for the richest forms of tactile sensing.  
> Conversely, one could even argue that tactile sensing becomes the natural sensing modality for soft-skinned robots — the natural extension of proprioception.  
> So these two topics are intimately connected!

意思是：

> 这两个主题看起来可以分开，那为什么放在一章？  
> 因为柔软可以促成触觉感知。  
> 甚至可以说，最丰富的触觉感知需要柔软结构。  
> 反过来，也可以说触觉是软皮机器人最自然的传感模态，是本体感受的自然扩展。  
> 所以这两个主题紧密相连。

---

### 通俗理解

软体和触觉的关系可以这样看：

#### 刚性机器人

传统机器人像金属骨架：

```text
关节角度 → 知道手臂在哪
```

但如果手臂碰到障碍物，可能只能靠关节力矩间接猜测。

#### 软体机器人

软体机器人像有皮肤和肌肉：

```text
皮肤变形 → 知道哪里被碰到
压力分布 → 知道接触力
```

所以：

```text
软体结构天然能产生丰富触觉信号
```

---

### 类比：人手 vs 铁夹子

铁夹子：

```text
只能知道夹爪开合角度
碰到东西后靠电机电流猜力
```

人手：

```text
皮肤到处都有感受器
轻轻一碰就知道位置、压力、滑动、纹理
```

这就是作者想说的：

> 软体和触觉不是两个孤立话题，而是互相成就。

---

# 四、12.1 WHY SOFT?：为什么要软？

PDF 中这一节只有标题：

> 12.1 WHY SOFT?

没有展开正文。

我们不能假装它有正文，但也不能遗漏。

---

## 4.1 这一节在 PDF 中未展开

它可能是后续补充内容。

---

## 4.2 补充解释：为什么要软？

软体机器人可能有以下优势：

---

### 1. 更安全

刚性机器人如果撞到人类或易碎物体，可能造成伤害。

软体机器人更柔顺：

```text
碰撞时能变形吸能
```

类比：

```text
被铁棍碰到很疼
被海绵碰到不疼
```

---

### 2. 更容易适应物体形状

软手指可以包裹物体。

比如抓一个不规则水果：

```text
硬夹爪：只有几个接触点
软手指：可以贴合表面
```

这会增加接触面积，提高抓取稳定性。

---

### 3. 更适合接触丰富任务

操作任务经常涉及：

- 推；
- 挤；
- 捏；
- 翻；
- 包裹；
- 摩擦。

软体结构可以更自然地处理这些接触。

---

### 4. 更容易实现全身触觉

如果机器人表面是软的，并嵌入传感器，就可以形成“皮肤”。

这样机器人不仅指尖能感觉，手臂、手掌、身体也能感觉。

---

### 5. 被动智能

软体结构可以通过自身变形“自动适应”环境。

比如软手指碰到物体后自然弯曲包裹，不一定需要复杂控制。

这叫做：

> morphological computation  
> 形态计算

通俗理解：

```text
身体结构本身就帮你完成了一部分计算和控制
```

---

# 五、12.2 SOFT ROBOT HARDWARE：软体机器人硬件

PDF 中这一节只有标题：

> 12.2 SOFT ROBOT HARDWARE

没有展开正文。

---

## 5.1 这一节在 PDF 中未展开

需要说明：

> 当前 PDF 只有标题，没有正文。

---

## 5.2 补充解释：软体机器人硬件通常包括什么？

虽然 PDF 没展开，但为了帮助理解，可以补充常见软体机器人硬件形式。

---

### 1. 气动软体手指

通过充气让软体结构弯曲。

比如：

```text
气囊充气 → 手指弯曲
气囊放气 → 手指伸直
```

类比：

> 像气球做成的小手指。

---

### 2. 硅胶软体结构

很多软体机器人用硅胶浇铸。

优点：

- 柔软；
- 可塑形；
- 可嵌入传感器；
- 可制作复杂腔体。

---

### 3. 线缆驱动

用电机拉线，让软体结构弯曲。

类比：

> 像提线木偶的线。

---

### 4. 智能材料

比如：

- 形状记忆合金；
- 电活性聚合物；
- 介电弹性体；
- 水凝胶。

这些材料可以在电、热、化学刺激下变形。

---

### 5. 触觉皮肤

软体外层可以嵌入：

- 压力传感器；
- 应变传感器；
- 触觉阵列；
- 视觉触觉传感器；
- 温度传感器。

---

# 六、12.3 SOFT-BODY SIMULATION：软体仿真

这一节有正文，非常重要。

标题：

> 12.3 SOFT-BODY SIMULATION  
> 软体仿真

PDF 中写：

> FEM, MPM,...

意思是：

> 有限元方法 FEM、物质点法 MPM 等。

---

## 6.1 为什么软体仿真很难？

刚性机器人仿真相对简单。

因为刚体可以假设：

```text
物体不变形
```

只需要跟踪：

- 位置；
- 姿态；
- 速度；
- 角速度；
- 接触力。

但软体机器人会变形：

```text
每个点都可能移动
每个局部都可能拉伸、压缩、弯曲
```

所以需要更复杂的连续介质力学模型。

---

### 类比：仿真砖头 vs 仿真面团

仿真砖头：

```text
砖头就是砖头
位置变了，形状没变
```

仿真面团：

```text
面团会被压扁、拉长、回弹、黏附、折叠
```

显然面团更难仿真。

---

## 6.2 FEM：有限元方法

FEM 是：

> Finite Element Method  
> 有限元方法

通俗理解：

把一个连续软体切成很多小块，叫“单元”。

比如：

```text
一个软体手指
↓
切成成千上万个小四面体/六面体
↓
对每个小块建立力学方程
↓
合起来模拟整体变形
```

---

### 类比：用很多小弹簧模拟果冻

你可以把果冻想象成：

```text
很多小质点
+
很多小弹簧
```

当你按压果冻：

- 质点移动；
- 弹簧拉伸或压缩；
- 整体变形。

FEM 就是更严格、更工程化的版本。

---

## 6.3 MPM：物质点法

MPM 是：

> Material Point Method  
> 物质点法

通俗理解：

用很多“物质点”表示软体材料。

这些点带着：

- 质量；
- 速度；
- 应力；
- 应变；
- 材料属性。

它特别适合：

- 大变形；
- 碰撞；
- 流体状材料；
- 雪、沙、泥、软组织等。

---

### FEM vs MPM 简单类比

FEM 像：

```text
把果冻切成网格
```

MPM 像：

```text
用很多小颗粒代表果冻
```

FEM 在工程中很成熟，但大变形时网格可能扭曲。

MPM 对大变形更友好，但计算和实现也复杂。

---

## 6.4 Drake 中的高性能软体仿真

PDF 原文说：

> Here is the video from a recent paper describing some of the recent advances enabling high-performance, reliable FEM soft-body simulation in Drake (including interactions with rigid bodies) [1].

意思是：

> 这里有一个来自近期论文的视频，描述了 Drake 中实现高性能、可靠 FEM 软体仿真的一些进展，包括软体和刚体之间的交互。

---

### 1. Drake 是什么？

Drake 是 Russ Tedrake 团队长期开发的机器人建模、仿真、控制和优化工具。

它强调：

- 动力系统；
- 物理仿真；
- 接触力学；
- 优化控制；
- 严格数学建模。

---

### 2. 软体和刚体交互

机器人场景中常常同时有：

- 刚性物体：杯子、罐头、工具；
- 软性物体：软手指、橡胶、布料、食物；
- 刚性机器人臂；
- 软体夹爪。

所以仿真器必须能处理：

```text
软体碰刚体
刚体碰软体
软体碰软体
```

---

## 6.5 关键细节：每一步都把接触问题求解到收敛

PDF 原文说：

> There is a subtle comment in the narration mentioning that the contact problem is solved to convergence on every time step — this is in fairly stark contrast to game-engine-quality physics which cut many computational corners for the sake of performance.

意思是：

> 视频解说中有一个微妙的评论：接触问题在每个时间步都被求解到收敛。  
> 这与游戏引擎级别的物理仿真形成鲜明对比。  
> 游戏引擎为了性能，通常会走很多计算捷径。

---

### 什么叫“求解到收敛”？

在仿真中，接触问题很复杂：

```text
两个物体是否接触？
接触点在哪？
法向力多大？
摩擦力多大？
是否滑动？
```

“求解到收敛”意思是：

> 数值算法反复迭代，直到结果满足误差标准。

不是粗略估计一下就过去。

---

### 类比：认真算账 vs 大概估账

游戏引擎像：

```text
大概算一下，看起来差不多就行
```

Drake 这类严肃仿真像：

```text
每一笔账都要算平，误差要小
```

---

## 6.6 为什么游戏引擎物理不够？

游戏引擎追求：

```text
实时
好看
稳定
便宜
```

它可能允许：

- 轻微穿模；
- 不精确摩擦；
- 近似接触；
- 视觉合理但物理不严谨。

但机器人研究需要：

- 可靠接触力；
- 可重复实验；
- 可用于控制设计；
- 可用于优化；
- 尽可能接近真实物理。

所以游戏引擎物理虽然快，但不一定适合机器人研究。

---

## 6.7 惊人之处：单 CPU 核也能实时

PDF 原文说：

> Amazingly we can now do this at real-time rates on a single CPU core.

意思是：

> 令人惊讶的是，现在可以在单个 CPU 核上以实时速率完成这些。

---

### 为什么这很重要？

软体仿真通常很贵。

如果每一步都要严格求解接触，计算量很大。

但现在 Drake 的进展让它能在单核 CPU 上实时运行，这意味着：

- 可用于实时控制；
- 可用于硬件在环；
- 可用于强化学习训练；
- 可用于模型预测控制；
- 可用于机器人实验。

---

### 类比：以前需要工厂级计算机，现在笔记本就能跑

以前软体仿真像：

```text
大型工程计算
需要高性能集群
```

现在可能变成：

```text
普通电脑也能实时跑
```

这对机器人研究意义很大。

---

# 七、12.4 TACTILE SENSING：触觉感知

标题：

> 12.4 TACTILE SENSING  
> 触觉感知

下面有几个小节。

---

# 八、12.4.1 What information do we want/need?：我们需要什么触觉信息？

PDF 中这一节只有标题：

> 12.4.1 What information do we want/need?

没有展开。

---

## 8.1 这一节在 PDF 中未展开

需要说明：

> 当前 PDF 只有标题。

---

## 8.2 补充解释：触觉到底要测什么？

触觉传感器可能想获得以下信息：

---

### 1. 是否接触

最基本问题：

```text
碰到了吗？
```

---

### 2. 接触位置

```text
碰在手指哪里？
碰在手掌哪里？
碰在手臂哪里？
```

---

### 3. 接触力大小

```text
轻轻碰到？
用力压？
快要捏碎物体？
```

---

### 4. 力方向

不只是多大，还要知道：

```text
力从哪个方向来？
```

---

### 5. 滑动

非常关键：

```text
物体是不是正在从手里滑走？
```

如果检测到滑动，机器人可以加大夹持力。

---

### 6. 接触几何

比如：

```text
接触面有多大？
接触形状是什么？
物体边缘在哪里？
```

---

### 7. 材质

可能判断：

```text
硬还是软？
光滑还是粗糙？
金属、塑料、布料？
```

---

### 8. 温度

对于家庭机器人或服务机器人，温度也有用：

```text
杯子是不是烫？
物体是不是冰冷？
```

---

### 9. 振动

接触过程中的振动可以帮助判断：

- 滑动；
- 纹理；
- 碰撞；
- 摩擦状态。

---

# 九、12.4.2 Visuotactile sensing：视觉触觉感知

PDF 中这一节只有标题：

> 12.4.2 Visuotactile sensing

没有展开。

---

## 9.1 这一节在 PDF 中未展开

需要说明：

> 当前 PDF 只有标题。

---

## 9.2 补充解释：什么是 visuotactile sensing？

Visuotactile sensing 可以翻译为：

> 视觉触觉传感

它通常指：

> 用摄像头观察软体接触面的变形，从而推断触觉信息。

---

### 典型原理

一个视觉触觉传感器可能包括：

```text
透明或半透明软皮肤
内部有摄像头
皮肤上有标记点或图案
```

当皮肤碰到物体：

```text
软皮肤变形
标记点移动
摄像头拍到变化
算法推断接触力、位置、滑动
```

---

### 类比：给软垫里面装一个微型相机

你按一个软垫。

软垫表面凹陷。

里面的相机看到：

```text
图案移动了
颜色变化了
阴影变化了
```

于是系统知道：

```text
哪里被按了
按得多深
有没有滑动
```

---

### 常见视觉触觉传感器

虽然 PDF 没列，但领域常见例子包括：

- GelSight；
- DIGIT；
- GelSlim；
- 其他基于弹性体和摄像头的触觉传感器。

它们的核心思想都是：

```text
用视觉测量弹性体变形
```

---

# 十、12.4.3 Whole-body sensing：全身触觉感知

这一节有正文。

标题：

> 12.4.3 Whole-body sensing  
> 全身感知

---

## 10.1 全身触觉皮肤的一个强理由：接触估计

原文说：

> One of the strongest cases in favor of whole-body tactile skins comes from the field of contact estimation.

意思是：

> 支持全身触觉皮肤的最有力理由之一，来自接触估计领域。

---

### 什么是 contact estimation？

contact estimation 是：

> 估计机器人在哪里发生了接触。

比如机器人手臂碰到桌子：

```text
碰在肘部？
碰在前臂？
碰在手腕？
碰在手指？
```

机器人需要知道接触位置，才能：

- 避免碰撞；
- 调整动作；
- 安全交互；
- 利用接触完成任务。

---

## 10.2 关节力矩传感可以估计接触，但有局限

原文说：

> From a series of nice work, we understand fairly well how to use joint-torque sensing to extract an estimate of the location on a robot arm where contact was made.

意思是：

> 通过一系列优秀工作，我们已经相当清楚如何使用关节力矩传感来估计机器人手臂上发生接触的位置。

---

### 什么是 joint-torque sensing？

joint-torque sensing 是：

> 通过测量关节力矩来推断外部接触。

比如机器人手臂在运动。

如果手臂某处碰到障碍物：

```text
电机电流变化
关节力矩变化
动力学模型出现偏差
```

算法可以根据这些变化估计：

```text
大概哪里碰到了东西
```

---

### 类比：通过手腕感觉推门

你闭着眼睛用手推门。

即使皮肤没有直接碰到门，你也可以通过手腕和手臂受力，大概判断：

```text
手前端碰到了门
```

关节力矩传感有点像这种间接感觉。

---

## 10.3 但问题是 ill-posed：不适定

原文说：

> But the problem is ill-posed.

意思是：

> 但这个问题是不适定的。

---

### 什么叫 ill-posed？

ill-posed 是数学/工程里的说法。

通俗理解：

> 信息不够，答案不唯一，或者对噪声非常敏感。

比如你知道关节力矩变了，但可能有多个接触情况都能解释同样的力矩变化。

---

### 类比：听声音猜敲击位置

你敲一根长杆。

如果只在一个地方测量振动，可能很难准确判断敲击点。

因为不同位置、不同力度的敲击，可能产生相似测量。

---

## 10.4 多接触点时，关节力矩传感尤其不够

原文说：

> Particularly in the case of multiple points of contact, joint-torque sensing alone seems woefully inadequate as a sensor.

意思是：

> 尤其是在多个接触点的情况下，仅靠关节力矩传感作为传感器显得非常不足。

---

### 为什么多接触点更难？

如果机器人手臂同时碰到：

- 桌子；
- 物体；
- 墙壁；
- 自己的另一只手；

关节力矩只能给你一个总体效果：

```text
总力和总力矩
```

但很难区分：

```text
哪个接触点贡献了多少力
```

---

### 类比：多人推一张桌子

如果几个人同时推一张桌子，你只知道桌子整体怎么动。

但很难仅从桌子运动判断：

```text
每个人站在哪
每个人用了多大力
```

如果有皮肤传感器，就能直接知道每个接触点。

---

## 10.5 全身触觉皮肤的价值

所以全身触觉皮肤可以解决关节力矩传感的不足。

它能提供：

```text
每个接触点的位置
每个接触点的压力
接触分布
接触面积
滑动情况
```

这对：

- 安全交互；
- 人机协作；
- 复杂抓取；
- 接触丰富操作；
- 软体机器人控制；

都非常重要。

---

# 十一、12.4.4 Simulating tactile sensors：仿真触觉传感器

PDF 中这一节只有标题：

> 12.4.4 Simulating tactile sensors

没有展开。

---

## 11.1 这一节在 PDF 中未展开

需要说明：

> 当前 PDF 只有标题。

---

## 11.2 补充解释：为什么要仿真触觉传感器？

触觉传感器很复杂，真实实验成本高。

仿真可以：

1. 生成大量触觉数据；
2. 训练感知模型；
3. 测试控制策略；
4. 设计传感器结构；
5. 研究接触物理。

---

### 触觉仿真通常需要什么？

可能需要仿真：

```text
软体变形
接触力
摩擦
传感器响应
摄像头图像
标记点位移
噪声
```

---

### 视觉触觉仿真示例

如果传感器是视觉触觉类型，可以仿真：

```text
弹性体表面变形
↓
表面标记点移动
↓
生成相机图像
↓
输入神经网络估计力/位置
```

---

# 十二、12.5 PERCEPTION WITH TACTILE SENSORS：用触觉传感器做感知

PDF 中这一节只有标题：

> 12.5 PERCEPTION WITH TACTILE SENSORS

没有展开。

---

## 12.1 这一节在 PDF 中未展开

需要说明：

> 当前 PDF 只有标题。

---

## 12.2 补充解释：触觉能感知什么？

触觉可以帮助机器人感知很多视觉难以获得的信息。

---

### 1. 物体形状

通过触摸可以推断：

```text
物体边缘
曲率
厚度
局部几何
```

比如闭着眼睛摸钥匙，你大概能知道它的形状。

---

### 2. 物体位姿

如果机器人抓住物体，触觉可以帮助判断：

```text
物体在手里的位置
物体是否倾斜
物体是否移动
```

---

### 3. 物体材质

触觉可以帮助区分：

```text
金属 vs 塑料
硬 vs 软
光滑 vs 粗糙
```

---

### 4. 抓取是否成功

如果手指感觉到稳定压力分布，说明可能抓稳了。

如果感觉到滑动，说明可能快掉了。

---

### 5. 接触状态

比如：

```text
单点接触
多点接触
面接触
边缘接触
```

这些对控制很重要。

---

# 十三、12.6 CONTROL WITH TACTILE SENSORS：用触觉传感器做控制

PDF 中这一节只有标题：

> 12.6 CONTROL WITH TACTILE SENSORS

没有展开。

---

## 13.1 这一节在 PDF 中未展开

需要说明：

> 当前 PDF 只有标题。

---

## 13.2 补充解释：触觉如何用于控制？

触觉不仅用于感知，还可以直接反馈给控制器。

---

### 1. 力控制

如果触觉测到力太大：

```text
减小夹持力
```

如果力太小：

```text
增加夹持力
```

---

### 2. 滑动控制

如果检测到物体滑动：

```text
立即加大夹持力
或调整手指姿态
```

---

### 3. 接触引导

比如插插头时：

```text
触觉告诉机器人哪里卡住
机器人微调位置
```

这比只靠视觉更精细。

---

### 4. 柔顺控制

软体机器人可以通过触觉实现柔顺交互：

```text
碰到人 → 降低刚度
碰到障碍 → 绕开
```

---

### 5. 全身安全控制

如果全身皮肤检测到碰撞：

```text
机器人立刻停止或后退
```

这对人机协作非常重要。

---

# 十四、REFERENCES：参考文献通俗导读

PDF 最后列了 2 篇参考文献。

---

## 参考文献 1

> Xuchen Han and Joseph Masterjohn and Alejandro Castro, “A Convex Formulation of Frictional Contact between Rigid and Deformable Bodies”, arXiv preprint arXiv:2303.08912, 2023.

作用：

- 对应 12.3 软体仿真；
- 描述 Drake 中高性能、可靠 FEM 软体仿真的进展；
- 涉及刚体和可变形体之间的摩擦接触；
- 强调接触问题的严格数值求解。

通俗理解：

> 这篇文献支持“Drake 可以在单 CPU 核上实时做可靠软体接触仿真”的说法。

---

## 参考文献 2

> Tao Pang and Jack Umenberger and Russ Tedrake, “Identifying External Contacts from Joint Torque Measurements on Serial Robotic Arms and Its Limitations”, Under Review., May, 2021.

作用：

- 对应 12.4.3 全身触觉感知；
- 讨论如何通过关节力矩测量识别外部接触；
- 也指出这种方法的局限性；
- 说明为什么仅靠关节力矩在多接触情况下不足。

通俗理解：

> 这篇文献支持“关节力矩可以估计接触，但问题不适定，尤其多接触时不够”的说法。

---

# 十五、文档末尾信息

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

# 十六、代码与实验实践重点补充

这一章 PDF 本身没有给出明确代码或实验步骤，但它多次提到：

- Drake 软体仿真；
- FEM；
- 刚体-软体接触；
- 触觉传感器仿真；
- 接触估计；
- 全身触觉。

因此下面我把这些方向补充成可实践的路线。

---

## 16.1 实验一：在 Drake 中体验软体-刚体接触仿真

对应 PDF：

> 12.3 SOFT-BODY SIMULATION  
> FEM, MPM,...  
> Drake FEM soft-body simulation

---

### 16.1.1 实验目标

观察软体物体与刚性物体接触时的变形和接触力。

例如：

```text
一个软球落到刚性地面
```

或者：

```text
软手指按压刚性方块
```

---

### 16.1.2 概念流程

```text
建立刚体环境
↓
建立软体几何
↓
设置材料参数
↓
设置接触参数
↓
仿真
↓
观察变形、接触力、穿透情况
```

---

### 16.1.3 伪代码示例

下面不是 PDF 原文代码，而是帮助理解的伪代码：

```python
from pydrake.all import (
    DiagramBuilder,
    Simulator,
    AddMultibodyPlantSceneGraph,
)

builder = DiagramBuilder()

# 1. 创建物理系统和场景几何
plant, scene_graph = AddMultibodyPlantSceneGraph(builder, time_step=0.001)

# 2. 加载刚体地面
AddRigidGround(plant)

# 3. 添加软体对象，例如软球
soft_body = AddSoftSphere(
    plant,
    radius=0.05,
    young_modulus=50_000,   # 弹性模量
    damping=1.0,
)

# 4. 设置初始高度
soft_body.SetInitialPosition([0, 0, 0.2])

# 5. 完成系统
diagram = builder.Build()
simulator = Simulator(diagram)

# 6. 仿真
simulator.AdvanceTo(5.0)
```

---

### 16.1.4 实践注意点

#### 1. 时间步长要小

软体接触仿真通常需要较小时间步：

```text
0.001 s 或更小
```

如果时间步太大：

- 接触不稳定；
- 可能穿透；
- 数值震荡。

---

#### 2. 材料参数很关键

软体材料通常包括：

- Young’s modulus：弹性模量；
- damping：阻尼；
- Poisson ratio：泊松比；
- density：密度。

弹性模量太小：

```text
像果冻，容易大变形
```

弹性模量太大：

```text
接近刚体
```

---

#### 3. 接触参数影响很大

包括：

- 摩擦系数；
- 接触刚度；
- 阻尼；
- 穿透惩罚参数。

如果仿真看起来“弹得太厉害”或“粘住不动”，通常需要调这些参数。

---

## 16.2 实验二：比较刚体手指和软体手指抓取

对应 PDF：

> WHY SOFT?  
> SOFT ROBOT HARDWARE

---

### 16.2.1 实验目标

比较：

```text
刚性平行夹爪
vs
软体手指夹爪
```

在抓取不规则物体时的表现。

---

### 16.2.2 实验设计

可以测试不同物体：

- 方块；
- 球；
- 圆柱；
- 不规则物体；
- 易滑物体；
- 易碎物体。

评价指标：

```text
成功率
最大承载重量
接触面积
所需夹持力
是否损伤物体
```

---

### 16.2.3 概念伪代码

```python
def test_grasp(gripper, object):
    reset_scene(object)
    gripper.close()
    lift_up()

    if object_still_in_gripper():
        return True
    else:
        return False
```

---

### 16.2.4 预期现象

刚性夹爪：

```text
接触点少
需要精确对准
对形状敏感
```

软体手指：

```text
接触面积大
能包裹物体
容错性更好
```

---

## 16.3 实验三：视觉触觉传感器仿真

对应 PDF：

> 12.4.2 Visuotactile sensing  
> 12.4.4 Simulating tactile sensors

---

### 16.3.1 实验目标

仿真一个视觉触觉传感器：

```text
软皮肤 + 内部相机 + 表面标记点
```

通过观察标记点位移估计接触。

---

### 16.3.2 概念流程

```text
软皮肤受压变形
↓
表面标记点移动
↓
相机图像变化
↓
算法估计接触位置/力
```

---

### 16.3.3 简化实验示例

如果暂时没有真实传感器，可以先用 2D 模拟：

```python
import numpy as np

def simulate_touch(force, position):
    # 简单假设：力越大，标记点位移越大
    displacement = force * 0.001

    # 生成标记点网格
    grid_x, grid_y = np.meshgrid(np.arange(10), np.arange(10))

    # 接触点附近产生位移
    dx = displacement * np.exp(-((grid_x - position[0])**2 +
                                 (grid_y - position[1])**2) / 5.0)
    dy = dx.copy()

    image = np.sqrt(dx**2 + dy**2)
    return image
```

然后用这个图像训练一个简单网络：

```text
输入：触觉图像
输出：接触位置、力大小
```

---

### 16.3.4 实践注意点

#### 1. 标记点图案要稳定可追踪

常见做法：

- 规则点阵；
- 随机斑点；
- 彩色标记；
- 高对比度图案。

---

#### 2. 光照要稳定

视觉触觉传感器内部光照变化会严重影响图像。

所以真实传感器通常要：

- 均匀 LED；
- 避免外部光；
- 固定曝光。

---

#### 3. 需要标定

要建立：

```text
图像变形 → 力/位置
```

的映射。

常用方法：

- 已知力加载实验；
- 机器人压头实验；
- 力传感器真值；
- 神经网络回归。

---

## 16.4 实验四：用关节力矩估计外部接触

对应 PDF：

> 12.4.3 Whole-body sensing  
> contact estimation  
> joint-torque sensing

---

### 16.4.1 实验目标

仅使用关节力矩测量，估计机器人手臂外部接触位置。

---

### 16.4.2 基本思想

机器人动力学可以写成类似：

```text
M(q) qddot + C(q, qdot) + g(q) = tau + J^T F_ext
```

其中：

- `q`：关节角度；
- `qdot`：关节速度；
- `qddot`：关节加速度；
- `tau`：关节力矩；
- `F_ext`：外部接触力；
- `J`：接触点雅可比。

如果没有外部接触：

```text
模型预测力矩 ≈ 实际测量力矩
```

如果有外部接触：

```text
实际测量力矩 - 模型预测力矩 = 残差
```

残差可以用来估计外部接触。

---

### 16.4.3 简化伪代码

```python
def estimate_contact_residual(q, qdot, qddot, tau_measured):
    tau_model = inverse_dynamics(q, qdot, qddot)
    residual = tau_measured - tau_model
    return residual
```

如果残差超过阈值：

```text
可能发生了外部接触
```

进一步可以优化：

```text
接触位置 p
接触力 f
```

使得：

```text
J(p)^T f ≈ residual
```

---

### 16.4.4 实践注意点

#### 1. 模型误差会造成误报

如果动力学模型不准：

- 摩擦估计不准；
- 质量估计不准；
- 惯量估计不准；

残差可能不是接触造成，而是模型误差造成。

---

#### 2. 多接触时不可辨识

PDF 特别强调：

```text
多接触点时，仅靠关节力矩非常不足
```

因为多个接触力可能产生相同关节力矩残差。

---

#### 3. 需要滤波

实际测量有噪声，可以用：

- 低通滤波；
- 卡尔曼滤波；
- 动量观测器；
- 阈值检测。

---

## 16.5 实验五：全身触觉皮肤 + 接触定位

对应 PDF：

> whole-body tactile skins

---

### 16.5.1 实验目标

如果机器人表面有触觉阵列，可以直接检测接触点。

---

### 16.5.2 概念流程

```text
皮肤传感器阵列
↓
每个 taxel 输出压力值
↓
压力分布图
↓
估计接触区域和力
```

其中 taxel 是：

> tactile pixel  
> 触觉像素

类比图像像素：

```text
图像有 pixel
触觉皮肤有 taxel
```

---

### 16.5.3 简化示例

```python
import numpy as np

def locate_contact(taxel_grid):
    # taxel_grid 是压力矩阵
    threshold = 0.1
    ys, xs = np.where(taxel_grid > threshold)

    if len(xs) == 0:
        return None

    pressures = taxel_grid[ys, xs]

    # 压力加权中心
    cx = np.sum(xs * pressures) / np.sum(pressures)
    cy = np.sum(ys * pressures) / np.sum(pressures)

    total_force = np.sum(pressures)

    return cx, cy, total_force
```

---

### 16.5.4 与关节力矩融合

更好的方式是：

```text
皮肤触觉：局部、直接，但覆盖和分辨率有限
关节力矩：全局、间接，但能估计整体外力
```

融合后可以提高接触估计能力。

---

## 16.6 实验六：触觉反馈控制抓取

对应 PDF：

> 12.6 CONTROL WITH TACTILE SENSORS

---

### 16.6.1 实验目标

利用触觉反馈调整夹持力。

---

### 16.6.2 控制逻辑示例

```python
def tactile_grasp_controller(tactile_force, slip_detected):
    target_force = 5.0

    if slip_detected:
        target_force += 2.0

    if tactile_force > 20.0:
        target_force -= 5.0

    command_gripper_force(target_force)
```

---

### 16.6.3 更完整的状态机

```text
1. 张开夹爪
2. 接近物体
3. 闭合夹爪
4. 检测触觉力
5. 如果力太小且滑动 → 加力
6. 如果力太大 → 减力
7. 抬起物体
8. 检测是否仍在手中
9. 放置
```

---

### 16.6.4 实践注意点

#### 1. 滑动检测很难

常用信号：

- 高频振动；
- 触觉图像局部剪切；
- 标记点快速移动；
- 力突变。

---

#### 2. 控制频率要足够高

如果滑动发生很快，而控制太慢，物体已经掉了。

触觉控制通常需要：

```text
几百 Hz 到几千 Hz
```

---

#### 3. 安全阈值很重要

对于易碎物体：

```text
最大力限制
```

对于重物：

```text
最小力限制
```

---

# 十七、与 PDF 逐项对照检查

下面我按 PDF 内容逐项检查，确认是否遗漏，并补充说明。

| PDF 位置 | 内容要点 | 是否已讲解 | 补充说明 |
|---|---|---:|---|
| 文档标题 | Robotic Manipulation: Perception, Planning, and Control | 已讲解 | 解释了感知、规划、控制 |
| 作者 | Russ Tedrake | 已讲解 | 已说明 |
| 版权 | © Russ Tedrake, 2020-2024 | 已讲解 | 已说明 |
| 修改时间 | Last modified 2025-8-26 | 已讲解 | 已说明 |
| 引用反馈 | How to cite, annotations, feedback | 已讲解 | 已说明 |
| 工作笔记 | MIT course working notes, Fall 2024 | 已讲解 | 已说明 |
| 导航 | Previous/TOC/Next | 已讲解 | 已说明 |
| 章节标题 | Chapter 12 Soft Robots and Tactile Sensing | 已讲解 | 已解释主题 |
| 引言 1 | 之前主要靠相机和 proprioceptive sensing | 已讲解 | 已解释 |
| 引言 2 | 必须讨论触觉 | 已讲解 | 已解释 |
| 引言 3 | 第一个目标：传感硬件和计算框架 | 已讲解 | 已说明 |
| 引言 4 | 听觉可能重要但未充分探索 | 已讲解 | 已说明 |
| 引言 5 | 软体机器人是重要趋势 | 已讲解 | 已说明 |
| 引言 6 | 操作需要丰富接触 | 已讲解 | 已举例 |
| 引言 7 | 传统机器人刚性，但指尖有橡胶垫 | 已讲解 | 已解释 |
| 引言 8 | 第二个目标：软体硬件和计算框架 | 已讲解 | 已说明 |
| 引言 9 | 为什么软体和触觉放一章 | 已讲解 | 已重点解释 |
| 引言 10 | 软体可促成触觉，甚至最丰富触觉需要软体 | 已讲解 | 已解释 |
| 引言 11 | 触觉是软皮机器人自然传感模态 | 已讲解 | 已解释 |
| 引言 12 | 触觉是本体感受自然扩展 | 已讲解 | 已解释 |
| 12.1 WHY SOFT? | 标题未展开 | 已讲解 | 已补充软体优势 |
| 12.2 SOFT ROBOT HARDWARE | 标题未展开 | 已讲解 | 已补充硬件类型 |
| 12.3 SOFT-BODY SIMULATION | FEM, MPM,... | 已讲解 | 已解释 FEM/MPM |
| Drake 软体仿真视频 | 高性能可靠 FEM，含刚体交互 | 已讲解 | 已解释 |
| 接触问题每步求解到收敛 | 与游戏引擎物理对比 | 已讲解 | 已重点解释 |
| 游戏引擎走计算捷径 | 已讲解 | 已解释 |
| 单 CPU 核实时 | 已讲解 | 已解释意义 |
| 12.4 TACTILE SENSING | 触觉感知总节 | 已讲解 | 已解释 |
| 12.4.1 What information do we want/need? | 标题未展开 | 已讲解 | 已补充触觉信息类型 |
| 12.4.2 Visuotactile sensing | 标题未展开 | 已讲解 | 已补充视觉触觉原理 |
| 12.4.3 Whole-body sensing | 有正文 | 已讲解 | 已详细解释 |
| contact estimation | 全身皮肤支持接触估计 | 已讲解 | 已解释 |
| joint-torque sensing | 可估计接触位置 | 已讲解 | 已解释 |
| ill-posed | 问题不适定 | 已讲解 | 已用类比解释 |
| multiple contacts | 多接触时关节力矩不足 | 已讲解 | 已重点解释 |
| 12.4.4 Simulating tactile sensors | 标题未展开 | 已讲解 | 已补充仿真思路 |
| 12.5 PERCEPTION WITH TACTILE SENSORS | 标题未展开 | 已讲解 | 已补充触觉感知任务 |
| 12.6 CONTROL WITH TACTILE SENSORS | 标题未展开 | 已讲解 | 已补充触觉控制 |
| References 1 | Han et al. convex formulation frictional contact | 已讲解 | 已说明作用 |
| References 2 | Pang et al. identifying external contacts | 已讲解 | 已说明作用 |
| 末尾导航/Accessibility/copyright | 已讲解 | 已说明 |

---

# 十八、检查后发现的“需要更通俗或补充”的地方

虽然上面已经覆盖 PDF 内容，但为了响应你的要求，我再单独指出哪些地方原本可能不够直观，并已经补充。

---

## 18.1 “proprioception”需要更生活化解释

PDF 原文：

> proprioceptive (e.g. joint) sensing

补充：

本体感受就是机器人知道“自己身体状态”。

比如：

```text
我的手张开多大？
我的胳膊举到多高？
我的关节转了多少？
```

人类也有本体感受。

你闭上眼睛也能大概摸到鼻子，就是靠本体感受。

---

## 18.2 “soft can enable tactile sensing”需要例子

PDF 原文：

> being soft can enable tactile sensing

补充例子：

硬金属手指碰到物体：

```text
只有大概力矩变化
```

软皮肤手指碰到物体：

```text
皮肤局部变形
可以测到具体接触位置和压力分布
```

所以软体结构让触觉更丰富。

---

## 18.3 “FEM/MPM”需要更直观

PDF 原文：

> FEM, MPM,...

补充：

FEM：

```text
把软体切成很多小单元
```

MPM：

```text
用很多物质点表示材料
```

类比：

```text
FEM 像网格果冻
MPM 像颗粒面团
```

---

## 18.4 “contact problem solved to convergence”需要例子

PDF 原文：

> contact problem is solved to convergence on every time step

补充：

游戏引擎可能：

```text
看起来没穿模就行
```

Drake 严肃仿真：

```text
接触力、摩擦、穿透误差都要算到满足标准
```

这对机器人控制很重要。

---

## 18.5 “ill-posed”需要强类比

PDF 原文：

> the problem is ill-posed

补充：

就像：

```text
只知道总账单是 100 元
不知道每个人点了什么
```

你无法唯一推出每个人消费。

关节力矩估计多接触也类似：

```text
总力矩已知
多个接触点未知
答案不唯一
```

---

## 18.6 “whole-body tactile skins”需要例子

补充：

如果机器人手臂有皮肤：

```text
哪里被碰到，皮肤直接报告
```

如果只有关节力矩：

```text
只能猜
```

多接触时猜不准。

---

## 18.7 “visuotactile sensing”需要实验感

补充：

视觉触觉传感器像：

```text
软垫里装相机
按下去后看图案怎么变形
```

通过变形推断：

```text
接触位置
力大小
滑动
```

---

# 十九、最终综合版总结：这一章的完整故事

把所有内容压缩成一个完整故事。

---

## 19.1 这一章的核心问题

机器人操作不能只靠：

```text
相机看
关节角度知道自己状态
```

还需要：

```text
触觉
```

因为操作任务本质上是接触任务。

---

## 19.2 为什么软体和触觉要一起讲？

因为：

```text
软体结构容易产生丰富触觉信号
触觉是软体机器人最自然的感知方式
```

软体让机器人更像“有皮肤的身体”，而不是“冷冰冰的金属杆”。

---

## 19.3 软体机器人的意义

软体机器人可能带来：

1. 更安全的人机交互；
2. 更好的物体适应性；
3. 更自然的接触行为；
4. 更丰富的触觉感知；
5. 更适合抓取柔软、易碎、不规则物体。

---

## 19.4 软体仿真的挑战

软体仿真比刚体仿真难得多。

因为要处理：

- 大变形；
- 材料非线性；
- 接触；
- 摩擦；
- 软-刚体交互；
- 实时性。

PDF 特别强调 Drake 中 FEM 软体仿真的进展：

```text
每个时间步严格求解接触
并且能在单 CPU 核上实时运行
```

这很重要。

---

## 19.5 触觉感知的意义

触觉可以回答视觉和关节传感难以回答的问题：

```text
碰到了吗？
碰在哪里？
力多大？
是否滑动？
抓稳了吗？
物体材质如何？
```

---

## 19.6 关节力矩传感的局限

PDF 特别指出：

```text
关节力矩可以用于接触估计
但问题不适定
多接触时尤其不够
```

所以需要全身触觉皮肤或局部触觉传感器。

---

## 19.7 实践路线总结

虽然 PDF 没有给出完整代码，但实践上可以围绕以下方向做实验：

```text
1. Drake 软体-刚体接触仿真
2. 刚体手指 vs 软体手指抓取比较
3. 视觉触觉传感器仿真
4. 关节力矩残差接触检测
5. 全身触觉皮肤接触定位
6. 触觉反馈夹持控制
```

---

## 19.8 最终一句话总结

这一章的核心是：

> 机器人操作不仅需要“看见”，还需要“触摸”；  
> 而软体机器人不仅是一种新的身体形态，更是实现丰富触觉感知和安全接触操作的重要基础。  
> 要让机器人真正擅长抓取、操作和与人协作，软体结构与触觉传感很可能是不可分割的一对关键技术。