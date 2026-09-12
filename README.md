<p align="center">
  <h1 align="center">🌳 Skill Forest</h1>
  <p align="center"><strong>AI 驱动的技能学习与岗位匹配系统</strong></p>
  <p align="center">
    <img src="https://img.shields.io/badge/python-3.8+-blue" alt="Python">
    <img src="https://img.shields.io/badge/node-20.19+-green" alt="Node">
    <img src="https://img.shields.io/badge/react-18-61dafb" alt="React">
    <img src="https://img.shields.io/badge/fastapi-0.100+-009688" alt="FastAPI">
    <img src="https://img.shields.io/badge/antd-5-1677ff" alt="Ant Design">
    <img src="https://img.shields.io/badge/AI-DeepSeek_v4-6366f1" alt="DeepSeek">
  </p>
</p>

---

## 📖 这是什么？

**Skill Forest** 解决一个每个程序员都遇到的问题：*岗位 JD 写了一堆技术要求，我到底该学什么？怎么学？学到什么程度才算够？*

它的工作方式很简单：

1. **粘贴岗位 JD** → AI 自动拆解成技能树（大类→中类→小类），判断每个技能的掌握程度要求
2. **生成学习任务** → 每个岗位对应一组可执行的任务，关联到技能树
3. **追踪进度** → 标记每个技能的学习状态（认识→熟悉→熟练→完全掌握）
4. **深入学习** → 点击任意任务进入学习模式：AI 生成教程、对话答疑、出题测评
5. **全局总览** → 仪表盘展示各领域完成度，自动计算你最适合哪个岗位

你输入越多的岗位 JD，系统就越了解整个行业的要求，技能树越完整，合并重复项，帮你看到技术领域的全景图。

---

## 🎯 核心功能

### 📋 智能岗位分析

粘贴任意岗位的 JD 原文（支持复制自 Boss 直聘、猎聘、LinkedIn 等），AI 自动完成：

- **技能提取**：识别 JD 中提到的所有技术能力
- **三级分类**：大类（如 AI/机器学习）→ 中类（如 机器学习框架）→ 小类（如 PyTorch）
- **程度判定**：根据 JD 措辞判断要求程度（了解→认识、熟悉→熟悉、精通→熟练、专家→完全掌握）
- **合并去重**：与已有技能对比，相似度 ≥ 80% 自动建议合并
- **任务生成**：针对每个技能生成 5-10 个可执行的学习任务

```
输入：「熟练掌握Linux环境下的C/C++、Python；熟悉PyTorch框架...」
  ↓ AI 分析
输出：
  🌳 编程语言
    ├── C/C++ [熟练]     → 任务：用 C++ 实现一个内存池
    └── Python [熟练]    → 任务：用 Python 写一个异步爬虫
  🌳 AI/机器学习
    └── 机器学习框架
        └── PyTorch [熟悉] → 任务：用 PyTorch 训练一个 CNN 分类器
```

### 🌳 技能树管理

- **三级层次树**：大类 / 中类 / 小类 / 具体技能，无限展开
- **跨岗位共享**：同一个技能被多个岗位要求时自动关联，不会重复
- **掌握程度追踪**：四级标准（认识→熟悉→熟练→完全掌握）
- **学习状态**：未开始 / 进行中 / 已完成
- **来源追溯**：每个技能可以看到来自哪些岗位的要求

### ✅ 工作任务面板

- 按岗位组织，支持按状态、岗位筛选
- 一键切换完成状态（勾选即完成）
- 每个任务展示关联的技能和要求的掌握程度
- **「开始学习」按钮** → 进入深度学习模式

### 📖 AI 教程生成

点击任意任务的「开始学习」，AI 自动生成一份**零基础入门教程**：

- 从最基础的概念开始，假设没有先验知识
- 用类比和生活例子解释抽象概念
- Markdown 格式，带标题层次、代码块、列表
- 包含「常见疑问」小节，预判初学者的困惑
- 教程缓存到本地，秒开；支持重新生成

### 💬 多会话 AI 对话

仿 DeepSeek 官网风格的对话界面：

- **多会话管理**：每个任务可以创建多个对话，切换自如
- **深度思考模式**：开关控制是否展示 AI 的推理过程（可折叠）
- **上下文注入**：每次对话自动附带任务的技能信息 + 教程全文作为参考资料
- **历史管理**：消息持久化，20 对滑动窗口
- **Markdown 渲染**：AI 回复支持完整的 Markdown 格式

### 📝 智能测评系统

学完后点击「测评」，AI 自动出一套完整试卷：

- **选择题**：15 道，覆盖关键知识点
- **大题**：3 道简答/论述，考察理解深度
- **名词解释**：5 道，检验概念掌握
- **自动评分**：提交后 AI 逐题评分，给出详细解析
- **分数统计**：圆环图展示得分率

### 📕 错题本

- 测评中的错题自动入库，永久保留
- 展示：你的答案 vs 正确答案 vs AI 解析
- 按技能筛选，按复习状态分类
- 标记「已复习」追踪进度
- 统计面板：总错题数、未复习数

### 📊 仪表盘总览

- **总体完成度**：环形图展示技能完成率
- **各领域进度**：按大类（编程语言 / AI / 系统...）展示完成度柱状图
- **最佳匹配岗位**：自动计算你最适合投哪个岗位
- **最深入领域**：展示你掌握程度最高的技术方向
- **待办提醒**：还有多少任务未完成

---

## 🏗️ 架构设计

```
┌──────────────────────────────────────────────────────────┐
│                      浏览器 (React 18)                     │
│  ┌─────────┐ ┌─────────┐ ┌──────────┐ ┌──────────────┐  │
│  │ 仪表盘   │ │ 技能树   │ │ 岗位管理  │ │  学习页面     │  │
│  │ Dashboard│ │SkillTree │ │  Jobs    │ │  Learning    │  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └──────┬───────┘  │
│       └─────────────┴────────────┴──────────────┘          │
│                         │ HTTP / JSON                      │
└─────────────────────────┼──────────────────────────────────┘
                          │
┌─────────────────────────┼──────────────────────────────────┐
│                   FastAPI (Python)                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────────┐  │
│  │ Skills   │ │  Jobs    │ │  Todos   │ │  Learning   │  │
│  │ Router   │ │  Router  │ │  Router  │ │  Router     │  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └──────┬──────┘  │
│       └─────────────┴────────────┴──────────────┘          │
│                          │                                  │
│  ┌──────────────────────────────────────────────────────┐ │
│  │              DeepSeek Service                         │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐  │ │
│  │  │ JD 分析  │ │ 教程生成  │ │ 聊天对话  │ │出题评分│  │ │
│  │  └──────────┘ └──────────┘ └──────────┘ └────────┘  │ │
│  └──────────────────────────────────────────────────────┘ │
│                          │                                  │
│                    ┌─────┴─────┐                           │
│                    │  SQLite   │                           │
│                    └───────────┘                           │
└──────────────────────────────────────────────────────────┘
                          │
                    ┌─────┴─────┐
                    │ DeepSeek   │
                    │ API (v4)   │
                    └───────────┘
```

### 数据模型

```
skills ──M:N── skill_jobs ──M:N── jobs
  │                                    │
  │ M:N                                │ 1:N
  │                                    │
  └── todo_skills ──M:N── todo_items ──┘
                               │
                               │ 1:1
                               ├── learning_modules (教程缓存)
                               │
                               │ 1:N
                               ├── chat_sessions ── 1:N ── chat_messages
                               │
                               │ 1:N
                               ├── quiz_attempts
                               │
                               └── error_book
```

**两张核心表完全独立**：技能表不依赖岗位，任务表属于岗位但关联技能。这意味着：
- 同一个技能被多个岗位要求时，只存在一条技能记录
- 你在学「Python」时，同时为多个岗位的匹配度加分
- 删除岗位不会删除共享的技能

---

## 🚀 快速开始

### 前提条件

- **Python** ≥ 3.8
- **Node.js** ≥ 20.19（Vite 8 的要求，`^20.19.0 || >=22.12.0`）
- **DeepSeek API Key**（[免费注册获取](https://platform.deepseek.com/api_keys)，新用户有赠送额度）

### 安装

```bash
# 1. 克隆或下载项目
git clone <your-repo-url>
cd Skill-Forest

# 2. 配置 API Key
cp .env.example .env                # Windows 用 copy .env.example .env
# 编辑 .env，填入你的 DEEPSEEK_API_KEY

# 3. 安装依赖
pip install -r requirements.txt   # Python 后端
npm install                       # 前端

# 4. 启动
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8765 &
npx vite --host --port 5173
```

浏览器打开 **http://localhost:5173**

> 💡 Windows 用户也可以直接双击 `start.bat`

### 配置 API Key

三种方式任选其一（推荐方式 1）：

```bash
# 方式 1：.env 文件（推荐）
cp .env.example .env      # 然后编辑 .env，填入密钥

# 方式 2：环境变量
export DEEPSEEK_API_KEY="sk-你的密钥"     # Linux/Mac
set DEEPSEEK_API_KEY=sk-你的密钥         # Windows

# 方式 3：直接改 backend/config.py 里 os.environ.get("DEEPSEEK_API_KEY", ...) 的默认值
```

---

## 📚 使用指南

### 第一步：添加第一个岗位

1. 点击左侧导航「💼 岗位」
2. 点击「+ 新岗位」
3. 粘贴一份岗位 JD（可以从招聘网站直接复制）
4. 可选填岗位名称、公司、原始链接
5. 点击「开始分析」
6. 等待 AI 分析完成（通常 10-30 秒）
7. 检查技能分类和合并建议，确认保存

### 第二步：查看技能树

1. 点击左侧「🌳 技能树」
2. 左侧面板展示三级分类层次
3. 点击任意技能查看详情
4. 在右侧修改掌握程度和学习状态

### 第三步：开始学习

1. 点击左侧「✅ 工作任务」
2. 找到想学的任务，点击「开始学习」
3. **教程 Tab**：阅读 AI 生成的入门教程
4. **对话 Tab**：向 AI 提问，深入理解
5. **测评 Tab**：生成试卷，检验学习成果

### 第四步：追踪进度

1. 在技能树中更新每个技能的掌握程度
2. 在任务列表中勾选完成的任务
3. 回到仪表盘查看全局进度

---

## 🛠️ 技术栈

| 分类 | 技术 | 说明 |
|------|------|------|
| 前端框架 | React 18 + TypeScript | 组件化 UI |
| 构建工具 | Vite 8 | 极速 HMR |
| UI 组件库 | Ant Design 5 | 企业级组件（Tree, Table, Card 等） |
| 状态管理 | Zustand 4 | 轻量、TS 原生 |
| 路由 | React Router 6 | SPA 路由 |
| Markdown | react-markdown + remark-gfm | 教程 & 对话渲染 |
| 后端框架 | FastAPI | 异步 Python Web 框架 |
| ORM | SQLAlchemy 2.0 | 数据库抽象 |
| 数据库 | SQLite | 零配置，单文件存储 |
| 数据校验 | Pydantic 2 | 请求/响应模式校验 |
| AI 模型 | DeepSeek V4 Pro / Flash | 分析、生成、对话、评分 |
| API 协议 | OpenAI-compatible SDK | 标准化的 LLM 调用 |

### 为什么选这些技术？

- **FastAPI 而不是 Express**：Python 生态有更好的 AI/LLM SDK 支持（openai 库），且字符串处理（diff 相似度计算）更方便
- **SQLite 而不是 PostgreSQL**：单用户桌面应用，零配置是最佳选择
- **React + Ant Design 而不是 Vue + Element**：Ant Design 的 Tree 组件对三级树形结构支持极好
- **Zustand 而不是 Redux**：对于这种规模的应用，Zustand 的零样板代码优势明显
- **放弃 Electron**：不打包 150MB+ 的桌面壳，浏览器同样体验，且前后端分离更容易调试

---

## 📁 项目结构

```
skill-forest/
├── backend/                        # Python 后端
│   ├── main.py                     # FastAPI 入口，CORS，路由注册
│   ├── config.py                   # API Key、数据库路径等配置
│   ├── database.py                 # SQLAlchemy 引擎 + Session 管理
│   │
│   ├── models/                     # ORM 模型（SQLite 表定义）
│   │   ├── skill.py                # 技能表
│   │   ├── job.py                  # 岗位表
│   │   ├── todo_item.py            # 任务表
│   │   ├── associations.py         # 多对多关联表
│   │   └── learning.py             # 学习模块（教程/聊天/测评/错题）
│   │
│   ├── schemas/                    # Pydantic 请求/响应校验
│   │   ├── skill.py, job.py, todo.py
│   │   ├── analysis.py             # DeepSeek 分析相关
│   │   ├── dashboard.py            # 仪表盘统计
│   │   └── learning.py             # 学习模块
│   │
│   ├── services/                   # 业务逻辑层
│   │   ├── deepseek_service.py     # DeepSeek API 客户端（重试/恢复）
│   │   ├── skill_service.py        # 技能 CRUD + 合并
│   │   ├── job_service.py          # 岗位 CRUD + 分析保存
│   │   ├── todo_service.py         # 任务 CRUD
│   │   ├── dashboard_service.py    # 聚合统计
│   │   └── learning_service.py     # 教程/聊天/测评/错题本
│   │
│   ├── routers/                    # FastAPI 路由（33 个端点）
│   ├── prompts/                    # AI 系统提示词
│   └── utils/                      # 工具（相似度计算、树构建）
│
├── src/                            # React 前端
│   ├── main.tsx                    # 入口
│   ├── App.tsx                     # 路由定义
│   │
│   ├── components/
│   │   ├── layout/                 # AppLayout, Sidebar
│   │   ├── dashboard/              # 仪表盘
│   │   ├── skills/                 # 技能树 + 详情面板
│   │   ├── jobs/                   # 岗位列表 + 输入弹窗 + 详情
│   │   ├── todos/                  # 任务列表
│   │   ├── analysis/               # 分析进度 + 合并预览
│   │   ├── learning/               # 学习页面（教程/聊天/测评/错题本）
│   │   └── common/                 # 通用组件
│   │
│   ├── store/                      # Zustand 状态管理（5 个 store）
│   ├── types/                      # TypeScript 类型定义（6 个文件）
│   ├── services/                   # API 客户端（fetch 封装）
│   ├── hooks/                      # 自定义 hooks
│   └── styles/                     # 全局样式
│
├── data/                           # SQLite 数据库文件（自动创建）
├── start.bat                       # 一键启动
├── requirements.txt                # Python 依赖
├── package.json                    # npm 依赖
└── README.md
```

---

## 🔌 API 文档

后端启动后可访问 **http://127.0.0.1:8765/docs** 查看自动生成的 Swagger 文档。

### 端点总览（33 个）

| 模块 | 端点 | 说明 |
|------|------|------|
| Dashboard | `GET /api/dashboard` | 仪表盘聚合统计 |
| Skills | `GET /api/skills` | 技能列表 |
| | `GET /api/skills/tree` | 技能树（嵌套结构） |
| | `GET /api/skills/:id` | 技能详情 |
| | `POST /api/skills` | 创建技能 |
| | `PUT /api/skills/:id` | 更新技能 |
| | `DELETE /api/skills/:id` | 删除技能 |
| | `POST /api/skills/merge` | 合并两个技能 |
| Jobs | `GET /api/jobs` | 岗位列表 |
| | `GET /api/jobs/:id` | 岗位详情 |
| | `POST /api/jobs` | 保存分析结果 |
| | `DELETE /api/jobs/:id` | 删除岗位 |
| Todos | `GET /api/todos` | 任务列表 |
| | `GET /api/todos/:id` | 任务详情 |
| | `PUT /api/todos/:id` | 更新任务 |
| | `POST /api/todos` | 创建任务 |
| Analysis | `POST /api/analysis/preview` | JD 分析预览 |
| Learning | `POST /api/learning/tutorial/generate` | 生成教程 |
| | `GET /api/learning/tutorial/:todo_id` | 获取教程 |
| | `POST /api/learning/chat/sessions` | 创建对话会话 |
| | `GET /api/learning/chat/sessions` | 会话列表 |
| | `GET /api/learning/chat/sessions/:id` | 会话详情 |
| | `PATCH /api/learning/chat/sessions/:id` | 更新会话 |
| | `DELETE /api/learning/chat/sessions/:id` | 删除会话 |
| | `POST /api/learning/chat/send` | 发送消息 |
| | `POST /api/learning/quiz/generate` | 生成测评 |
| | `GET /api/learning/quiz/attempts` | 测评记录列表 |
| | `GET /api/learning/quiz/attempts/:id` | 测评记录详情 |
| | `POST /api/learning/quiz/submit` | 提交评分 |
| | `GET /api/learning/errors` | 错题列表 |
| | `GET /api/learning/errors/stats` | 错题统计 |
| | `PATCH /api/learning/errors/:id` | 标记已复习 |
| | `DELETE /api/learning/errors/:id` | 删除错题 |

---

## 🧠 设计决策

### 为什么两张表分开？
技能表和任务表是独立的。技能是跨岗位共享的知识单元，任务是某个岗位下的学习动作。同一个「Python」技能可能被 5 个岗位要求，但只有一个技能记录。你在技能树上把 Python 标记为「熟练」，所有关联岗位的匹配度同时提升。

### 为什么合并阈值是 80%？
经过实际测试，80% 是一个合理的平衡点：
- 太低（60%）：本不相关的技能被错误合并（如「Python」和「Python 测试框架」）
- 太高（95%）：几乎不会触发合并（如「PyTorch」和「Pytorch」）

### 两层合并校验
1. **AI 判断**：DeepSeek 在分析时比较所有现有技能，回传 `merge_confidence`
2. **本地校验**：对不确定的情况（0.75-0.85），用 `difflib.SequenceMatcher` 二次计算（名称 70% + 描述 30% 加权）

### 上下文窗口管理
AI 对话每次发送消息时，system message 始终包含：任务目的 + 技能水平 + 教程全文。消息历史保留最近 20 对（约 5K-10K token），超出部分截断并加提示。

---

## 🤝 贡献

欢迎提交 Issue 和 PR。

### 本地开发

```bash
# 后端热重载
python -m uvicorn backend.main:app --reload --port 8765

# 前端热重载
npx vite --host --port 5173
```

### 代码规范

- Python：遵循 PEP 8
- TypeScript：`tsc --noEmit` 零错误
- 导入风格：后端使用 `backend.xxx` 绝对导入，前端使用 `@/` 路径别名

---

## 📄 License

MIT License

---

<p align="center">
  <sub>Built with ❤️ using React, FastAPI, SQLite, and DeepSeek AI</sub>
</p>
