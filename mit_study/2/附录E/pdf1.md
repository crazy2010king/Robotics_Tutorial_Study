# 用大白话讲透《Underactuated Robotics》附录E：杂项（Miscellaneous）

> 如果说前面的附录 A、B、C、D 都是"硬核技术 appendix"——讲多体动力学、优化数学、优化锦囊——那**附录 E 就是这门课的"后勤与社区手册"**。
>
> 它不包含新的机器人方程，也不推导新算法，但它告诉你**三件极其重要的事**：
> 1. 你怎么**引用**这本书（写论文、写报告时）
> 2. 你怎么**参与**这本书的共建（纠错、讨论的礼仪）
> 3. 历届学生用这门课的工具做出了**多么酷的项目**（灵感宝库）
>
> Russ Tedrake 在开篇就说：这些是"working notes"——**活着的、不断更新的讲义**。所以附录 E 本质是"你与这份活文档之间的接口"。

下面我用最通俗的方式，把附录 E 从头到尾拆给你看，配上生活类比，并对"代码实践"做重点补充。

---

## 📜 一、E.1 如何引用这份讲义（How to Cite These Notes）

### 1.1 为什么要专门讲"怎么引用"？

**生活类比**：想象你做了一道招牌菜，别人在你的菜谱基础上改良并发表了新菜谱——他们必须在开头写明"原菜谱来自 XXX 的《招牌菜大全》"。这既是**学术规范**，也是对原创者的**尊重**。

Russ Tedrake 花了几十年写这份讲义，他希望你在学术论文、技术报告、博客中引用它时，格式正确。

### 1.2 推荐的引用格式

**BibTeX 格式**（写 LaTeX 论文时用）：

```bibtex
@book{underactuated,
  title = "Underactuated Robotics",
  subtitle = "Algorithms for Walking, Running, Swimming, Flying, and Manipulation",
  howpublished = "Course Notes for MIT 6.832",
  author = "Tedrake, Russ",
  year = 2023,
  url = "https://underactuated.csail.mit.edu",
}
```

**纯文本格式**（写报告、网页时用）：

> Russ Tedrake. Underactuated Robotics: Algorithms for Walking, Running, Swimming, Flying, and Manipulation (Course Notes for MIT 6.832). Downloaded on [日期] from https://underactuated.csail.mit.edu/

### 1.3 关键细节解读

| 要素 | 含义 |
|---|---|
| **作者** | Russ Tedrake（MIT 教授，机器人领域泰斗）|
| **年份 2023** | 讲义的"版本年"——即使你 2024、2025 年下载，引用年份仍写 2023 |
| **Downloaded on [date]** | 你必须填上自己下载的具体日期——因为这讲义**不断更新**，不同日期下载的内容可能不同 |
| **URL** | 必须用 `https://underactuated.csail.mit.edu`（当前最新地址）|

> 💡 **重要提醒**：这份讲义是"living document"——Russ 会在每学期持续修正。所以引用时一定要写"Downloaded on [你的下载日期]"，读者才能追溯到你引用的那个版本。

---

## 💬 二、E.2 注释工具礼仪（Annotation Tool Etiquette）

### 2.1 为什么要讲"礼仪"？

这份讲义有一个**网页注释功能**——读者可以选中任意一段文字，在旁边写评论：可以提问、可以讨论、也可以指出错别字。

**生活类比**：想象你在图书馆的一本书上做批注。如果书是"活的"（网页版），你的批注会一直挂在原文旁边。**问题来了**：如果你批注"这里有个错别字"，Russ 看到后把错别字改了——但你的批注还挂在那里，说"这里有错字"，可实际上已经没错字了！这就变成了**误导后来读者的"脏数据"**。

### 2.2 Russ 提出的两个解决方案

**方案一：公开编辑评论 + 承诺删除**
- 你可以公开发布编辑性评论（指出错别字、语法问题）
- **但你必须承诺**：一旦问题被修复，你就删除这条评论

**方案二：加入"编辑组"发评论**
- 加入 Russ 的 "editorial" group
- 在这个组的"scope"下发布编辑性评论
- 这样评论与主线讨论分离，便于管理

**Russ 的期望**：
> "理想情况下，一旦我把某条评论标记为 'done'（已完成），希望你能够删除那条评论。"

### 2.3 为什么这套礼仪很重要？

Russ 明确说 ：
- 他的**主要目标**：注释工具是用来承载"对文本内容完全开放的对话"的
- **意外发现**：它也成了指出错别字和语法瑕疵的便捷途径
- **痛点**：如果你高亮了一个错别字，而他在 10 分钟后修复了，你的高亮会**永远残留**——最终污染了注释内容

> 💡 **社区共建的精神**：Russ 高度重视讨论和纠错。他说"Please keep them coming"（请继续提出来）。这套礼仪不是为了"限制你"，而是为了让所有人的贡献都能**干净地沉淀**下来。

---

## 🏆 三、E.3 一些优秀的期末项目（Some Great Final Projects）

这是**整个附录 E 最激动人心的部分**——历届 MIT 6.832 学生用这门课的工具做出的炫酷项目。

### 3.1 为什么这部分重要？

**生活类比**：你看一本烹饪书，光看理论没感觉。但当你看到" previous 学员用这本书的方法做出了米其林三星菜品"——你立刻明白这本烹饪书的威力。

这些项目证明了：**附录 A-D 的数学工具 + Drake 仿真器 = 能做出真正的前沿机器人系统**。

### 3.2 🌟 Spring 2024 杰出项目奖（Outstanding Project Awards）

这是最新的、最高荣誉的一批 ：

1. **《密集障碍场中基于凸集图的加速度约束四旋翼轨迹优化》**
   - 作者：Michael Tibbs
   - 关键词：Quadrotor（四旋翼）、Acceleration Constrained（加速度约束）、Dense Obstacle Fields（密集障碍场）、Graphs of Convex Sets（凸集图，即 GCS——我们在附录 C.5.3 学的革命性框架）

2. **《使用凸集图控制的固定翼无人机无障碍轨迹优化》**
   - 作者：Steve Nomeny
   - 关键词：Fixed-Wing UAV（固定翼无人机）、Collision Free（无障碍）、GCS

3. **《协同视觉运动策略学习》**
   - 作者：Abhinav Agarwal and Adam Wei
   - 关键词：Co-training（协同训练）、Visuomotor Policy Learning（视觉运动策略学习）——这是连接"传统优化控制"与"现代深度学习"的桥梁

4. **《Spot 机器人上的凸集图轨迹优化》**
   - 作者：Johannes Ihle, Aileen Liao, and Lukas Molnar
   - 关键词：Spot（Boston Dynamics 的四足机器人）、GCS for Trajectory Optimization

5. **《基于半定规划的卫星姿态规划》**
   - 作者：Brandon Eickert and Shreeyam Kacker
   - 关键词：Satellite Attitude Planning（卫星姿态规划）、Semidefinite Programming（SDP——附录 C.3.2 学的工具！）

> 💡 **观察**：2024 年的杰出项目里，**GCS（凸集图）出现了 3 次**！这印证了我们在附录 C 学到的——GCS 是当下机器人轨迹优化最火的框架。

### 3.3 Spring 2023 项目精选

- **《多链路 Cart-Pole 的摆动上升轨迹优化》** by Siro Corsi
  - 是我们学过的 Cart-Pole 的"升级版"——多链路！
- **《SalmonBot》** by Erick Fuentes
  - 鲑鱼机器人——模拟鲑鱼游动
- **《四旋翼协同共享负载搬运》** by Seiji Shaw and Tommy Cohn
  - 多机器人协同搬运——这是"underactuated"的典型应用场景
- **《飞行鸟机器人》** by Quang Kieu
  - 扑翼飞行机器人
- **《带机械臂的 Spot 的 QP 逆动力学》** by Namir Jawdat
  - QP（二次规划——附录 C.3 学的）用于 Spot 狗 + 机械臂
- **《使用轨迹优化的舞棍运动》** by Shruti Garg
  - 杂技动作——舞棍（staff spinning）
- **《GCS 作为策略》** by Savva Morozov
  - 把 GCS 用作控制策略（policy），而不仅是轨迹优化

### 3.4 Spring 2022 项目精选

- **《用轨迹优化打保龄球全中》** by Benjamin Qi
  - 用轨迹优化让机器人打保龄球——既实用又有趣
- **《通过约束轨迹优化的量子控制》** by Shantanu Jha and Shoumik Chowdhury
  - 把机器人优化工具用到**量子系统**——跨学科的典范
- **《通过接触的简单滑板技巧轨迹优化》** by Michael Burgess
  - 滑板动作涉及"接触"（落地、蹬地）——我们用附录 B.3 学的接触动力学
- **《通过交替优化的接触感知控制器设计》** by Richard Li and Timur Garipov
- **《磁驱动卫星的稳定性认证》** by Alex Meredith
  - 用 SOS 优化（附录 C.3.3）做稳定性证明
- **《随机风扰下的四旋翼轨迹优化》** by Mason Darveaux
  - 引入随机性——连接第 21 章的随机控制
- **《通过 SOS 规划的收缩度量稳定性分析》** by Sunbochen Tang
  - SOS + 收缩度量——深度技术
- **《摆荡运动（Brachiation）轨迹优化》** by Kaleb Blake and John Flynn
  - 模拟猴子在树枝间摆荡——这是"接触隐式优化"的经典问题

### 3.5 Spring 2021 项目精选

- **《运动学自行车模型的线性化 MPC》** by Mike Schoder（附代码）
- **《使用引力辅助的星际旅行轨迹优化》**
  - 用行星引力做"弹弓加速"——这是航天器轨迹优化的圣杯问题
- **《四旋翼的差分平坦轨迹稳定》** by Charles Vorbach
  - 差分平坦性——第 18 章的内容
- **《随机环境中四旋翼的轨迹规划》** by Susan Ni, Christian Schillinger, and Max Thomsen

### 3.6 Spring 2020 项目精选

- **《使用凸安全区域的四旋翼无障碍混合整数规划》** by Bernhard Paus Græsdal
  - 混合整数规划（MIP——附录 C.5）+ 凸安全区域
- **《通过轨迹优化翻煎饼》** by Charles Dawson
  - 翻煎饼——看似简单，实则是"接触 + 旋转 + 轨迹优化"的综合挑战
- **《动态滑翔》** by Lukas Lao Beyer
  - 无人机的"动态滑翔"——利用气流免费获取能量
- **《特技人形机器人》** by Matt Chignoli and AJ Miller
  - 人形机器人做特技——Mini Cheetah 团队的前身
- **《Furuta 倒立摆的轨迹优化》** by Samuel Cherna and Philip Murzynowski
  - Furuta Pendulum 是旋转倒立摆——比 Cart-Pole 更复杂

### 3.7 走向正式发表的项目

Russ 特别提到，有些课堂项目**最终变成了正式的学术论文** ：

1. **《Pusher-Slider 系统的反馈控制：混合与欠驱动接触动力学的故事》**
2. **《利用结构进行基于价值的规划与强化学习》**
3. **《Mini Cheetah 的后空翻》**——著名的 Mini Cheetah 平台
   - 这个项目**最初就是 6.832 的期末项目**！
   - 后来发展成了 Mini Cheetah: A Platform for Pushing the Limits of Dynamic Quadruped Control
   - 这是**课程项目孵化出世界级研究成果**的最佳例证

> 💡 **深刻启示**：这份讲义不只是"教材"——它是**前沿研究的发射台**。你今天学的工具，明天就能做出发表级的工作。

### 3.8 项目主题的"技术地图"

把这些项目按使用的核心技术分类，你会发现**与前面附录的完美对应**：

| 核心技术 | 对应附录 | 项目例子 |
|---|---|---|
| **GCS（凸集图）** | C.5.3 | 2024 年 3 个项目、Spot 轨迹优化、固定翼无人机 |
| **SDP/SOS** | C.3.2/C.3.3 | 卫星姿态规划、稳定性认证、收缩度量分析 |
| **MIP** | C.5.2 | 四旋翼混合整数规划、协同搬运 |
| **接触动力学** | B.3 | 滑板技巧、摆荡运动、翻煎饼 |
| **QP 逆动力学** | C.3.1 | 带臂 Spot 的控制 |
| **轨迹优化** | 第 18 章 | 几乎所有项目 |

**这张表就是"学以致用"的路线图**。

---

## 📣 四、E.4 请给我反馈（Please Give Me Feedback!）

### 4.1 Russ 的诚恳请求

Russ 写道 ：
> "我非常感兴趣听取你的反馈。注释工具是一种机制，但你也可以直接在 YouTube 讲座下评论，甚至可以在托管这些讲义的 GitHub 仓库中提出 issue。我还创建了这份简单的调查问卷来收集你的总体意见/反馈。"

### 4.2 反馈的三种渠道

1. **网页注释工具**（annotation tool）——针对具体文本段落的讨论或纠错
2. **YouTube 讲座评论**——针对视频内容的反馈
3. **GitHub 仓库 Issue**——针对代码、技术错误的反馈
4. **简单调查问卷**（simple survey）——收集总体意见建议

### 4.3 为什么反馈如此重要？

Russ 在 preface 里说过 ：这份讲义是"working notes"——**活着的文档**。它之所以能从一个学期进化到下一个学期，靠的就是读者的反馈。

**生活类比**：这就像一款开源软件。用户 bug report 越多，软件进化越快。Russ 把这份讲义当成"开源项目"在运营——你是用户，也是贡献者。

---

## 📋 五、与 PDF 原文的逐项对照核查

| PDF 章节 | 我的讲解覆盖情况 | 补充说明 |
|---|---|---|
| 章节标题 | ✅ 完整讲解 | APPENDIX E Miscellaneous |
| 版本信息 | ✅ 完整讲解 | ©Russ Tedrake,2024，Last modified 2024-5-30 |
| 引用方式提示 | ✅ 完整讲解 | "How to cite these notes, use annotations, and give feedback" |
| 课程性质说明 | ✅ 完整讲解 | "working notes used for a course being taught at MIT" |
| YouTube 讲座视频可用 | ✅ 完整讲解 | "Lecture videos are available on YouTube" |
| **E.1 如何引用** | ✅ 完整讲解 | |
| 感谢引用 | ✅ 完整讲解 | "Thank you for citing these notes in your work" |
| BibTeX 格式 | ✅ 完整讲解 | 完整 @book 条目，year=2023 |
| 纯文本引用格式 | ✅ 完整讲解 | "Downloaded on [date] from https://underactuated.csail.mit.edu/" |
| **E.2 注释工具礼仪** | ✅ 完整讲解 | |
| 注释工具的主要目标 | ✅ 完整讲解 | "host a completely open dialogue on the intellectual content" |
| 意外用途：指出错别字 | ✅ 完整讲解 | "it's a convenient way to point out my miscellaneous typos" |
| 问题：修复后高亮残留 | ✅ 完整讲解 | "your highlight will persist forevermore... pollutes the annotation content" |
| 解决方案1：公开编辑评论+承诺删除 | ✅ 完整讲解 | |
| 解决方案2：加入 editorial group | ✅ 完整讲解 | "post your editorial comments using this group 'scope'" |
| 期望：标记 done 后删除评论 | ✅ 完整讲解 | |
| 重视讨论和纠错 | ✅ 完整讲解 | "I highly value both the discussions and the corrections" |
| **E.3 优秀期末项目** | ✅ 完整讲解 | |
| Spring 2024 杰出项目奖（6个） | ✅ 完整讲解 | 全部列出并解读 |
| 2024 项目播放列表 | ✅ 完整讲解 | "playlist containing all of the public projects" |
| Spring 2023 项目（7个） | ✅ 完整讲解 | 全部列出 |
| Spring 2022 项目（8个） | ✅ 完整讲解 | 全部列出 |
| Spring 2021 项目（4个） | ✅ 完整讲解 | 全部列出，含 [code] 标记 |
| Spring 2020 项目（5个） | ✅ 完整讲解 | 全部列出 |
| 走向发表的项目（3个） | ✅ 完整讲解 | 含 Mini Cheetah 后空翻故事 |
| **E.4 反馈渠道** | ✅ 完整讲解 | |
| 注释工具 | ✅ 完整讲解 | |
| YouTube 评论 | ✅ 完整讲解 | |
| GitHub issue | ✅ 完整讲解 | "github repo that hosts these course notes" |
| 简单调查问卷 | ✅ 完整讲解 | "simple survey to collect your general comments/feedback" |
| 版权信息 | ✅ 完整讲解 | "©Russ Tedrake,2024" |
| 可访问性声明 | ✅ 完整讲解 | "Accessibility" |

### 通俗性补充（针对基础薄弱读者的额外解释）

1. **什么是"working notes"？**
   类比：这不是一本"盖棺定论"的教科书，而是 Russ 一边教课一边写的"活笔记"。每学期都会修订、补充、修正。所以你下载的版本和别人下载的版本可能略有不同——这也是为什么引用时必须写"Downloaded on [日期]"。

2. **为什么"注释礼仪"值得专门写一节？**
   因为这份讲义是**网页版**，任何人都能选中文字写评论。如果没有礼仪规范，纠错评论会在错误修复后变成"幽灵评论"，误导后来的读者。这就像维基百科的编辑规范——看似琐碎，实则是社区健康的基石。

3. **期末项目列表的真正价值是什么？**
   它不是"荣誉榜"，而是**"可能性地图"**。每一个项目名都是一道门——推开它，你就能看到"原来 GCS 可以做四旋翼避障"、"原来 SOS 可以证明卫星稳定性"、"原来轨迹优化可以翻煎饼"。这是激发你自己项目灵感的宝库。

4. **为什么 Russ 如此渴望反馈？**
   因为他把这份讲义当成开源软件在运营。每一次反馈都是一次"bug report"或"feature request"，推动这份讲义不断进化。从 2009 年的第一版到 2024 年的版本，跨度 15 年——这就是持续反馈的力量。

---

## 💻 六、代码实践重点补充说明（这是本章最该动手的部分）

附录 E 本身没有公式推导，但**它列出的期末项目就是最好的"实践课题库"**。我为你挑选 3 个**可以从 GitHub 获取代码**的真实项目，让你亲手体验"用这门课的工具做出酷东西"。

### 实验一：复现"四旋翼无障碍混合整数规划"

**对应项目**：Spring 2020 的《Collision Free Mixed Integer Planning for Quadrotors Using Convex Safe Regions》by Bernhard Paus Græsdal 

**代码仓库**：`bernhardpg/collision-free-mixed-integer-planning-for-uavs`

**实践步骤**：

```bash
# 1. 克隆仓库
git clone https://github.com/bernhardpg/collision-free-mixed-integer-planning-for-uavs
cd collision-free-mixed-integer-planning-for-uavs

# 2. 安装 Drake（这门课的标准仿真器）
# 参考官方安装指南：https://underactuated.csail.mit.edu/drake.html

# 3. 阅读 report.pdf 理解问题设置
# 核心思想：
# - 用凸集（ Convex Safe Regions）近似无障碍空间
# - 用混合整数规划（MIP）求解路径
# - 对应我们学的附录 C.5.2 和 C.5.3

# 4. 运行仿真
# 查看 src/ 目录下的 C++ 代码
# 这是用 Drake 的 MathematicalProgram 构建 MIP 的真实案例
```

**预期现象**：
- 四旋翼在 3D 障碍物场中找到一条碰撞自由轨迹
- 轨迹通过 MIP 求解器（Gurobi/MOSEK）计算

**深刻教训**：
> 这是**MIP + 凸集**在真实机器人上的完整实现。你能看到附录 C.5 的理论如何变成 C++ 代码。

### 实验二：复现"腿式机器人的优化运动规划"

**对应项目**：Spring 2021 的《Optimization-based Motion Planning Methods for Legged Robots》by William Chen and Alex Cuellar 

**代码仓库**：`verityw/underactuated-final-project`

**实践步骤**：

```bash
# 1. 克隆仓库
git clone https://github.com/verityw/underactuated-final-project
cd underactuated-final-project

# 2. 在 Google Colab 中打开 underactuated_final_project_clean.ipynb
# 这个 notebook 直接使用 PyDrake

# 3. 理解两种方法：
# 方法A：NLP + 硬编码接触模式序列
#   - 使用非线性规划求解器
#   - 对应附录 C.4
#
# 方法B：MIQP + 线性凸近似
#   - 使用混合整数二次规划
#   - 对应附录 C.5.2

# 4. 运行 Walking Gait 和 Running Gait 两种步态
```

**预期现象**：
- 仿真平面 LittleDog 机器人行走和奔跑
- 两种优化方法产生不同的步态模式

**深刻教训**：
> 这是**接触模式选择（MIP）vs 固定模式（NLP）**的直接对比。你能看到附录 B.3（接触动力学）和附录 C（优化）如何协同工作。

### 实验三：复现"立方体机器人的摆动上升与稳定"

**对应项目**：6.832 Final Project by Ethan Weber 

**代码仓库**：`ethanweber/cube`

**实践步骤**：

```bash
# 1. 克隆仓库
git clone https://github.com/ethanweber/cube
cd cube

# 2. 安装 Drake 和 Meshcat
# 参考：https://underactuated.csail.mit.edu/drake.html

# 3. 打开 Jupyter Notebooks：
# - SwingUpAndStabilize.ipynb：摆动上升 + LQR 稳定
# - LimitCycle.ipynb：极限环分析
# - MBlockExample.ipynb：M-Block 例子

# 4. 运行 SwingUpAndStabilize.ipynb
```

**预期现象**：
- 立方体机器人从静止摆动上升到倒立稳定
- 使用能量整形（energy shaping）+ LQR

**深刻教训**：
> 这是**第 3 章 Acrobot/Cart-Pole 摆动上升**的"立方体版本"。你能看到课本的基础算法如何扩展到新机器人形态。

### 实验四：自己的期末项目——从"模仿"到"创新"

**推荐路径**：

1. **第一周**：复现上述 3 个项目中的 1 个（建议从实验三开始，最简单）
2. **第二周**：修改参数——换机器人尺寸、换环境、换优化求解器
3. **第三周**：组合创新——例如把实验一的"四旋翼 MIP"与实验二的"腿式 MIQP"结合
4. **第四周**：原创项目——参考 Spring 2024 杰出项目，提出你自己的 GCS 应用

**GCS 项目模板**（基于 2024 年杰出项目的共同模式）：

```python
from pydrake.all import *
from drake.examples.graph_of_convex_sets import *

# 1. 定义图：顶点 = 凸集，边 = 运动学约束
vertices = {
    "start": ConvexSet(start_region),
    "obstacle_1_left": ConvexSet(left_region),
    "obstacle_1_right": ConvexSet(right_region),
    "goal": ConvexSet(goal_region)
}

edges = [
    ("start", "obstacle_1_left"),
    ("start", "obstacle_1_right"),
    ("obstacle_1_left", "goal"),
    ("obstacle_1_right", "goal")
]

# 2. 构建 GCS 优化问题
gcs = GraphOfConvexSets(vertices, edges)

# 3. 添加边成本（如时间、能量）
for edge in edges:
    gcs.AddEdgeCost(edge, time_cost_function)

# 4. 求解（用开源求解器！）
result = Solve(gcs.OptimizationProgram())

# 5. 提取轨迹
trajectory = gcs.GetSolutionPath(result)
```

**这就是 2024 年 Michael Tibbs、Steve Nomeny、Johannes Ihle 等人项目的核心架构**！

---

## 🎯 七、整体综合：附录 E 的真正地位

把附录 E 放到整个课程体系里看：

```
附录 A: 机器人动力学基础
附录 B: 多体动力学（如何推导方程）
附录 C: 优化与数学规划（求解器）
附录 D: 优化锦囊（问题重构技巧）
附录 E: 社区与资源 ← 你在这里
    ↓
这不是终点，而是起点：
- 引用格式 → 让你能正确使用这份知识
- 注释礼仪 → 让你能参与共建这份知识
- 期末项目 → 让你能看到知识的力量
- 反馈渠道 → 让你能推动知识的进化
```

### 四个关键认识

1. **这份讲义是"活的"**：从 2009 年到 2024 年，15 年持续进化。你今天读到的内容，包含了 15 年来 MIT 6.832 所有学生的集体智慧。

2. **项目列表是"能力证明"**：当你学完 21 章正文 + 4 个附录，你应该能做 Spring 2024 杰出项目奖级别的工作。这不是"未来才能做的事"，而是"现在就能开始做的事"。

3. **GCS 是当下的王者**：2024 年 6 个杰出项目中 3 个用了 GCS。如果你时间有限，优先深入学习附录 C.5.3。

4. **从复现到创新**：实验一到实验三是"站在巨人肩膀上"，实验四是"成为下一个巨人"。MIT 6.832 的传奇项目（Mini Cheetah 后空翻）就是这样诞生的。

---

## 🚀 八、给你的学习路径建议

基于附录 E 的内容，我建议你按以下顺序走完这段旅程：

1. **现在**：精读附录 E，特别是 E.3 的项目列表——找到让你心跳加速的那个项目
2. **本周**：从 GitHub 克隆实验三（立方体机器人），跑通 SwingUpAndStabilize.ipynb
3. **本月**：复现实验一（四旋翼 MIP）或实验二（腿式 MIQP）
4. **本学期**：基于 GCS 做你自己的期末项目——目标是达到 Spring 2024 杰出项目奖的水平
5. **长期**：像 Mini Cheetah 团队一样，把课程项目发展成正式研究

---

## 📌 九、写在最后：你也是这份讲义的"合著者"

Russ 在 E.2 中说："I highly value both the discussions and the corrections. Please keep them coming."

这句话的分量很重。**这份讲义不是 Russ 一个人的作品，而是整个社区的作品**。每一个通过注释工具指出的错别字、每一次在 GitHub 提交的 issue、每一份期末项目——都在塑造这份讲义的下一个版本。

当你将来引用这份讲义时，BibTeX 里的 `year = 2023` 只是一个时间戳。但真正让这份讲义"活着"的，是**像你一样的读者**——学习它、使用它、批判它、扩展它。

附录 E 告诉我们：**你不是这份知识的被动消费者，而是主动的共同建构者**。

现在，合上这份附录，打开 Drake，从那个让你兴奋的项目开始吧。也许明年 Spring 2025 的"Outstanding Project Awards"名单上，就会出现你的名字。

> 💡 **最后一个小贴士**：如果你做出了酷项目，别忘了按照 E.1 的格式引用这份讲义——这是对 Russ 15 年持续付出的最好的致敬方式。