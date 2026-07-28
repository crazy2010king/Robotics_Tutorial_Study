# 用大白话讲透《Underactuated Robotics》附录A：Drake 软件工具箱

> 前面21章我们学了大量机器人算法——摆方程的、做优化的、学策略的……但**算法不能只停留在数学公式上**，你得能让机器人真的跑起来。这一章就是教你：**用什么工具、怎么把书里的代码跑起来**。
>
> 这个工具叫 **Drake**。它是 Russ Tedrake（本书作者）主导开发的开源机器人算法工具箱，最初就是为 MIT 这门"欠驱动机器人"课而生的 。
>
> 下面我用最通俗的方式讲清楚 Drake 是什么、怎么装、怎么用，并配上代码实践说明。

---

## 🧰 一、Drake 到底是什么？——机器人界的"瑞士军刀"

### 1.1 一句话定位

**Drake 是一个主要用于机器人动力学、控制、规划算法开发的 C++ 工具箱** 。
本书中几乎所有的例子和练习都用它来实现。

### 1.2 生活类比：机器人算法实验室

想象你要做木工活：
- **C++ 版本的 Drake** = 专业木工车间里全套工业级电动工具——性能强、精度高、适合生产环境
- **pydrake（Python 绑定）** = 同一套工具的"家用友好版"——接口更简单，适合原型开发、教学、快速实验

作者在书中**只用 Python（pydrake）写所有示例代码** 。原因很实在：Python 上手快、适合教学、方便快速验证想法。

> 💡 **重要提醒**：pydrake 的成熟度**不如 C++ 后端**。作者原话："你的反馈（甚至贡献）都非常欢迎，它仍在快速改进中" 。

### 1.3 文档使用的小窍门

由于 pydrake 的自动生成 Python 文档还在完善中，作者给了一个**实用建议** ：
- **先用 C++ 文档**查找你需要的类和方法
- **再对照 Python 文档**确认在 pydrake 中这个类/方法怎么拼写

类比：C++ 文档是"总说明书"，pydrake 文档是"中文翻译版"——总说明书更全，但你要知道翻译版里对应的词怎么写。

---

## ☁️ 二、在线运行：Deepnote 云平台（最推荐的方式）

### 2.1 为什么用 Deepnote？

本书**几乎所有示例和练习都以 Jupyter Notebook 形式提供**，目的是利用免费的云资源 。

**首选平台：Deepnote** 。
作者在 Deepnote 上提供了完整的 Notebook 环境，所有依赖（pydrake、underactuated 包、MeshCat 可视化）都**预装好了**——你只需要点几下就能跑 。

### 2.2 四步上手（**最重要**）

按作者给的流程 ：

**第1步：登录**
用免费账号即可，对本课程足够 。

**第2步：复制文档（"Duplicate"）**
点击登录旁边右上角的"复制"图标 。
> 💡 这一步很关键！Deepnote 上的 Notebook 是只读的，你必须复制一份到自己的 workspace 才能运行和修改。

**第3步：运行所有单元格**
可以点击 Notebook 上方的"Run notebook"图标，一键运行全部代码 。

**第4步：查看 MeshCat 三维可视化**
很多 Notebook 用 MeshCat 做交互式可视化。点击 **"StartMeshcat" 代码单元下方打印出的 URL**（通常是 Notebook 的第2个代码单元）打开 MeshCat 窗口 。

> 📌 **MeshCat 是什么？** 一个基于网页的 3D 可视化工具。机器人动起来、轨迹画出来，都是在 MeshCat 窗口里看的。

### 2.3 代码实践重点补充

**实验一：跑通你的第一个 Deepnote Notebook**

以第2章"Simple Pendulum"为例：

1. 打开本书第2章网页，找到 Notebook 链接
2. 点击链接进入 Deepnote
3. 登录 → 点击右上角"Duplicate" → 等待复制完成
4. 点击"Run notebook"运行全部
5. 找到"StartMeshcat"单元格，按住 Ctrl/Cmd 点击输出的 URL
6. 在新标签页看到 MeshCat 窗口，里面单摆开始摆动

**关键观察**：
- 整个过程**不需要安装任何东西**
- 所有依赖都在 Deepnote 的 Docker 镜像里预装好了 
- 如果遇到 `ModuleNotFoundError: No module named 'underactuated'`，说明你没有用"复制"的方式——必须 Duplicate 文档，而不是直接运行 

**实验二：修改参数，观察变化**

跑通后，尝试修改 Notebook 中的参数：
- 把单摆的长度 `L` 从 1.0 改成 2.0，重新运行
- 观察：摆动周期变长了（物理规律：周期 ∝ √L）
- 这就是"快速原型开发"的威力——改一个数，立刻看到效果

### 2.4 Google Colab 的情况（**重要时效信息**）

> ⚠️ **截至本书撰写时，Drake 已不再支持 Google Colab** 。
>
> 原因：Colab 卡在 Ubuntu 18.04 和 Python 3.7 上，而 Drake 需要更新的系统环境。作者说："如果/当他们升级，我们会尝试重新支持。"

网上能搜到一些在 Colab 上强行安装 Drake 的脚本 ，但**不建议新手使用**——这些是第三方方案，可能随时失效，且与本书附录的官方指引不一致。

**结论**：**用 Deepnote，别折腾 Colab** 。

---

## 💻 三、本机安装：在你自己的电脑上跑

### 3.1 什么时候需要本机安装？

当你"变得更高级"——想要修改、扩展这些示例时，你会希望在自己机器上运行 。

### 3.2 系统要求

Drake 支持的最新两个版本的 **Mac 和 Ubuntu**，使用系统默认 Python 版本 。

> 📌 Windows 用户：Drake 官方不完全支持 Windows，建议在虚拟机/双系统/WSL 中使用 Ubuntu。

### 3.3 最简安装流程（pip 方式）

作者推荐用虚拟环境 ：

```bash
# 1. 创建虚拟环境
python3 -m venv venv

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 安装 underactuated 包（含所有依赖）
pip3 install underactuated[all] --extra-index-url https://drake-packages.csail.mit.edu/whl/
```

**这行命令做了什么？**
- `underactuated[all]`：安装本书专用的 `underactuated` Python 包及其所有依赖
- `--extra-index-url`：告诉 pip 去 Drake 的私有包仓库找 Drake 的 wheel 文件

### 3.4 获取所有 Notebook 代码

```bash
# 克隆课程仓库
git clone https://github.com/RussTedrake/underactuated.git

# 进入仓库根目录
cd underactuated

# 启动 Jupyter
jupyter notebook
```

**代码组织结构** ：
- 每章的示例 Notebook（`.ipynb` 文件）就在该章 html 文件**旁边**
- 所有练习 Notebook 都在 **`exercises/` 子目录**下

### 3.5 代码实践重点补充

**实验三：本机安装全流程**

以 Ubuntu 20.04 为例的完整步骤：

```bash
# 1. 安装系统依赖（Ubuntu 20.04）
sudo apt-get install --no-install-recommends \
    libpython3.8 python3-tk libx11-6 libsm6 libxt6 libglib2.0-0

# 2. 创建并激活虚拟环境
python3 -m venv venv
source venv/bin/activate

# 3. 安装 Drake + underactuated
pip3 install underactuated[all] --extra-index-url https://drake-packages.csail.mit.edu/whl/

# 4. 克隆课程代码
git clone https://github.com/RussTedrake/underactuated.git
cd underactuated

# 5. 安装补充依赖
pip3 install --requirement requirements.txt

# 6. 启动 Jupyter
jupyter notebook
```

**常见坑与解决**：

1. **Python 版本不匹配**：
   - Drake 对 Python 版本敏感
   - Ubuntu 20.04 需要用 Python 3.8
   - 解决：用 conda 创建指定版本的环境
     ```bash
     conda create --name underactuated python=3.8
     conda activate underactuated
     ```

2. **MeshCat 可视化不显示**：
   - 本机运行时，MeshCat 默认在 localhost 的某个端口
   - 解决：浏览器打开 `http://localhost:7000`（端口号在 Notebook 输出中）

3. **`ImportError: cannot import name 'X' from 'pydrake'`**：
   - pydrake 版本与代码不匹配
   - 解决：重新安装 underactuated[all]，或检查 Drake 版本

### 3.6 其他安装选项

Drake 官网还提供 ：
- **预编译二进制文件**
- **Docker 镜像**

对于大多数读者，**pip 安装 + 虚拟环境**是最简单可靠的。

---

## 🔑 四、启用商业求解器许可证

### 4.1 为什么需要？

Drake 的 `MathematicalProgram`（数学规划）模块可以调用多种优化求解器。其中一些**高级求解器需要许可证**（学术界大多免费）。

### 4.2 如何启用

作者指向了 Drake 的官方教程 。

> 💡 实操提示：最常用的高级求解器是 **Gurobi** 和 **MOSEK**——它们在学术许可下免费，能显著提升大规模优化问题的求解速度。如果你要做第16-17章的极限环优化、混合轨迹优化，**强烈建议配置**。

---

## 🆘 五、获取帮助

### 5.1 遇到问题怎么办？

作者给出了明确路径 ：
- **Drake 相关问题**：遵循 Drake 官方的"获取帮助"指南
- **underactuated 课程仓库问题**：在 GitHub 仓库的 Issues 中查看已知问题，或提交新的 Issue

### 5.2 代码实践补充

**实验四：提交一个高质量的 Issue**

当代码报错时，好的 Issue 应该包含：
1. **环境信息**：操作系统、Python 版本、Drake 版本
2. **复现步骤**：你点了哪个 Notebook 的哪个单元格
3. **完整错误信息**：复制粘贴 traceback
4. **已尝试的解决方式**

这样的 Issue 通常能得到快速响应。

---

## 📋 六、与 PDF 原文的逐项对照核查

| PDF 章节 | 我的讲解覆盖情况 | 补充说明 |
|---|---|---|
| 章节开篇 | ✅ 完整讲解 | Drake 是本书主要软件工具箱，起源于 MIT 欠驱动课程 |
| A.1 PyDRAKE | ✅ 完整讲解 | |
| Drake 是 C++ 库 | ✅ 完整讲解 | 有严格编码标准，成熟度适合工业应用 |
| 本书只用 Python (pydrake) | ✅ 完整讲解 | 为了温和入门和快速原型 |
| pydrake 不如 C++ 后端成熟 | ✅ 完整讲解 | 作者欢迎反馈和贡献 |
| 文档使用建议 | ✅ 完整讲解 | 先用 C++ 文档查找，再对照 Python 文档确认拼写 |
| Drake 教程资源 | ✅ 完整讲解 | |
| A.2 在线 Jupyter Notebooks | ✅ 完整讲解 | |
| 用 Notebook 形式提供示例和练习 | ✅ 完整讲解 | 利用免费云资源 |
| A.2.1 Running on Deepnote | ✅ 完整讲解 | |
| Deepnote 是主平台 | ✅ 完整讲解 | |
| 四步流程：登录→复制→运行→查看 MeshCat | ✅ 完整讲解 | 详细解释了每步 |
| 免费账号足够 | ✅ 完整讲解 | |
| Duplicate 文档的位置（右上角）| ✅ 完整讲解 | |
| Run notebook 图标位置 | ✅ 完整讲解 | |
| MeshCat URL 位置（StartMeshcat 下方）| ✅ 完整讲解 | |
| A.2.2 Running on Google Colab | ✅ 完整讲解 | |
| Drake 不再支持 Colab | ✅ 完整讲解 | 卡在 Ubuntu 18.04 和 Python 3.7 |
| 未来可能重新支持 | ✅ 完整讲解 | |
| A.2.3 Enabling licensed solvers | ✅ 完整讲解 | |
| 为 MathematicalProgram 启用更强大的求解器 | ✅ 完整讲解 | 学术免费；指向 Drake 教程 |
| A.3 RUNNING ON YOUR OWN MACHINE | ✅ 完整讲解 | |
| 进阶用户在本地运行 | ✅ 完整讲解 | |
| 支持的平台 | ✅ 完整讲解 | 最新两个版本的 Mac 和 Ubuntu，系统默认 Python |
| pip 安装 + 虚拟环境 | ✅ 完整讲解 | 给出了完整命令 |
| underactuated[all] + extra-index-url | ✅ 完整讲解 | 完整命令 |
| 从 Deepnote 下载 Notebook 本地运行 | ✅ 完整讲解 | |
| Drake 官网的其他安装选项 | ✅ 完整讲解 | 预编译二进制、Docker |
| git clone 课程仓库 | ✅ 完整讲解 | |
| jupyter notebook 启动 | ✅ 完整讲解 | |
| 代码组织结构 | ✅ 完整讲解 | 章节 Notebook 在 html 旁边；练习在 exercises/ 子目录 |
| A.4 GETTING HELP | ✅ 完整讲解 | |
| Drake 问题遵循 Drake 官方建议 | ✅ 完整讲解 | |
| underactuated 仓库问题查 GitHub Issues | ✅ 完整讲解 | |

### 通俗性补充（针对基础薄弱读者的额外解释）

1. **什么是 Jupyter Notebook？**
   类比：一个"活的文档"——里面既有文字说明，又有可运行的代码块。你从上到下依次运行代码块，就能看到结果。本书所有代码都以这种形式提供。

2. **什么是 Deepnote？**
   类比：一个"云端 Jupyter Notebook 机房"。你不用在自己电脑上装任何东西，打开浏览器就能写代码、跑代码、看结果。Drake 和本书需要的所有软件都已经装在机房的电脑里了。

3. **什么是"Duplicate"（复制）？**
   类比：老师发了一份只读的共享文档，你不能改。你必须"复制"一份到自己的账号下，才能运行和修改。

4. **什么是 MeshCat？**
   类比：一个"网页版 3D 播放器"。机器人模型、轨迹动画都在这里面播放。Notebook 里会给出一个网址，你点开就能看到 3D 画面。

5. **什么是虚拟环境（virtual environment）？**
   类比：在你电脑里隔出一个"独立实验台"。这个台子上装的 Python 包不会影响你电脑其他地方。这样不同项目需要不同版本的包时，就不会冲突。

6. **什么是 `pip install underactuated[all]`？**
   类比：一条命令把本书需要的所有软件（Drake、绘图库、MeshCat 等）一次性装好。`[all]` 表示"全部可选组件都装上"。

7. **什么是 `extra-index-url`？**
   类比：告诉 pip（Python 的软件安装器）："除了去官方的 PyPI 仓库找软件，也去 Drake 的私人仓库找 Drake 的安装包"。

8. **为什么 Colab 不支持了？**
   类比：Drake 需要较新的"操作系统地基"，但 Colab 的地基太旧了（Ubuntu 18.04），拖不动 Drake 这个新建筑。要等 Colab 翻新地基，或者直接用 Deepnote 这个新楼盘。

---

## 🎯 七、整体综合：Drake 在全书学习中的角色

把附录A 放到整个课程体系里看：

```
理论学习（第1-21章）
    ↓ 需要验证
Drake 实现（附录A + 各章 Notebook）
    ↓
三种运行方式：
① Deepnote（最简单，推荐新手）★★★★★
② 本机 pip 安装（最灵活，推荐进阶）★★★★
③ Docker 镜像（最隔离，推荐生产）★★★
```

### 对各层次读者的建议

**🟢 初学者（只想看懂算法、跑通示例）**：
→ 直接用 **Deepnote**，按四步流程操作，30 秒内开始运行代码

**🟡 进阶者（想修改代码、做练习、搞研究）**：
→ 本机 **pip 安装 + 虚拟环境**，克隆 GitHub 仓库，用 Jupyter 本地运行

**🔴 专业者（要做真实机器人部署）**：
→ 用 **C++ 版 Drake**，参考 C++ 文档，享受工业级性能和稳定性

### 三个最关键的认识

1. **Deepnote 是本书的"官方推荐环境"**——所有 Notebook 都在上面预装好，复制即运行 

2. **pydrake 是"友好版接口"**——本书所有代码用它写，但文档查阅要先看 C++ 版 

3. **本机安装用虚拟环境 + pip**——一条命令装好所有依赖 

### 对工程实践的启示

> 💡 **Drake 不仅是教学工具，更是工业机器人研发的工业级工具箱**。它的 C++ 后端有严格的编码标准和成熟度要求，适合工业应用 。这意味着：你在本书中学到的 Drake 用法，可以直接迁移到真实机器人项目中。

> 💡 **MeshCat 可视化是标配**。本书几乎所有动力学仿真都用 MeshCat 做 3D 可视化 。学会看 MeshCat 窗口，是理解机器人运动的关键。

> 💡 **求解器许可证值得配置**。当你做到第16-17章的轨迹优化时，没有 Gurobi/MOSEK 这类高级求解器，大规模优化问题会慢得难以接受。学术邮箱可以申请免费许可证 。

---

## 🚀 八、给你的学习路径建议

如果你想真正掌握本书的所有代码实践，建议按以下顺序：

1. **第一步**：注册 Deepnote 账号，用四步流程跑通第2章"Simple Pendulum"的 Notebook
2. **第二步**：依次跑通第3章（Acrobot）、第4章（Rimless Wheel）、第8章（LQR）的 Notebook——这是全书的数学基础
3. **第三步**：本机安装 Drake，克隆 GitHub 仓库，本地运行同样的 Notebook
4. **第四步**：做各章 `exercises/` 子目录下的练习——这是检验理解的最佳方式
5. **第五步**：配置 Gurobi 或 MOSEK 学术许可证，重做第16-17章的优化练习，感受速度差异
6. **第六步**：尝试修改 Notebook 代码，实现自己的想法——这才是真正掌握

---

## 📌 九、章节完整性声明

需要诚实说明的是，根据提供的 PDF 内容：

- 附录A 是**工具使用指南**，不包含机器人算法的数学内容
- 所有内容都已覆盖：A.1 PyDRAKE、A.2 在线 Notebook（Deepnote/Colab/求解器许可证）、A.3 本机安装、A.4 获取帮助
- PDF 中提到的"Drake 官网"的具体教程链接、求解器许可证的详细申请流程，需要以 Drake 官方网站的最新信息为准 
- 网上流传的一些旧教程（如在 Colab 上强行安装 Drake、在 Ubuntu 18.04 上配置）与本书附录的当前指引不一致，不建议作为主参考 

---

## 🎁 十、写在最后：为什么 Drake 值得学？

Russ Tedrake 在附录开篇就说：**Drake 在很大程度上起源于 MIT 这门欠驱动机器人课程** 。

这意味着：
- 本书的每个算法，都有对应的 Drake 实现
- Drake 的 API 设计，就是为了最好地表达这些算法
- 学会 Drake，你就拥有了把全书21章算法"落地"的能力

从 Acrobot 的摆起控制，到四足机器人的混合轨迹优化，再到模仿学习的视觉运动策略——**Drake 是贯穿全书的隐形主角**。掌握它，你就掌握了把"数学"变成"机器人动作"的魔法棒。

> 💡 正如作者所说，pydrake 仍在快速改进中，你的反馈和贡献都非常欢迎 。这本身就是一个信号：你正在学习的工具，是活生生的、前沿的、被真实机器人研究广泛使用的工具。

现在，打开 Deepnote，点击 Duplicate，运行你的第一个 Notebook 吧——机器人学的奇妙之旅，从这一行代码开始。