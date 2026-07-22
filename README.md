# OI.SKILL

一个通用 AgentSkill，让任何 Agent 都能以苏格拉底式引导法辅助 OI（信息学竞赛）解题，并具备跨 session 记忆与 self-improve 能力。

## 核心理念

- **不直接给答案**：通过层层递进的问题引导学生独立思考。
- **先核解题解**：在引导前优先访问题解站，避免把错误思路当成正解。
- **跨 session 记忆**：自动维护 `~/.oi-skill/USER.md`，记录每个学生的优点与薄弱点。
- **自我改进**：根据每次解题和上传的思维过程静默更新认知画像。

## 目录结构

```
oi-skill/
├── SKILL.md                        # 核心系统提示与强制流程
├── README.md                       # 本文件
├── .gitignore
├── scripts/
│   └── duipai.py                   # 本地对拍 / 样例测试脚本
├── references/
│   ├── user-profile-template.md    # USER.md 模板
│   └── raw-thinking-template.md    # 原始思维过程文件模板
└── assets/
    └── oi-skill-ascii.txt          # 激活时 ASCII 字符画
```

## 安装

### 通用安装

将 `oi-skill` 目录复制或软链到你的 Agent 的 skills 目录。不同 Agent 加载 skill 的方式不同，通常只需让 Agent 能读取 `SKILL.md` 即可。

例如：

```bash
# 以 Kimi Code CLI 的 user skills 为例
ln -s /path/to/oi-skill ~/.agents/skills/oi-skill
```

### 运行时目录

首次使用时，Agent 会自动在用户家目录创建：

```
~/.oi-skill/
├── USER.md                         # 用户认知画像
└── raw/                            # 原始思维过程
```

**注意**：`USER.md` 和 `raw/` 不存放在 skill 目录内，而是放在用户家目录下，以实现真正的跨 session、跨设备记忆隔离。

## 使用方式

### 1. 激活 Skill

向 Agent 说明使用 OI.SKILL，Agent 会先输出 ASCII 字符画，然后等待你的输入。

### 2. 提供题目

你可以：

- 粘贴纯文本题面
- 提供洛谷 / Codeforces / AtCoder 等题目链接
- 上传图片或 PDF（Agent 会尝试 OCR）

### 3. 苏格拉底式引导

Agent 会：

1. 先访问题解站交叉核对思路。
2. 从基础概念开始，每次只提一个问题。
3. 根据你的回答调整后续问题。
4. 在关键节点提示你手写代码。

### 4. 本地验证

#### 样例测试

```bash
python3 /path/to/oi-skill/scripts/duipai.py \
  --solution student.cpp \
  --sample sample.in \
  --expected sample.out
```

#### 对拍

```bash
python3 /path/to/oi-skill/scripts/duipai.py \
  --solution student.cpp \
  --brute brute.cpp \
  --generator gen.py \
  --runs 100 \
  --timeout 2
```

### 5. AC 后复盘

当你告诉 Agent 已经 AC 后，Agent 会要求你写一份"类似题解"的思考记录，并据此诊断你是否真正掌握了本题思路。

### 6. 上传思维过程

比赛中或平时的草稿、文字思考过程，可以直接发给 Agent。Agent 会将其存入 `~/.oi-skill/raw/`，并用于更新你的认知画像。

## 支持的编程语言

`scripts/duipai.py` 目前支持：

- C++（`.cpp` / `.cc` / `.cxx`）
- Python（`.py`）
- Java（`.java`）

## 硬规则

这些规则写入 `SKILL.md`，用于强制 Agent 行为：

1. 每次只提一个问题。
2. 绝不直接给出最终答案（连续两次强烈要求除外）。
3. 基于学生回答动态调整。
4. 学生回答错误时不直接纠正，而是引导发现矛盾。
5. 卡住时降级到更基础的问题。
6. 先访问题解站交叉核对。
7. 代码验证分层：片段看逻辑，最终代码跑样例/对拍。

## 自定义与扩展

- 修改 `SKILL.md` 中的规则即可调整 Agent 行为。
- 修改 `references/user-profile-template.md` 可调整 USER.md 的结构。
- 修改 `scripts/duipai.py` 可扩展支持更多语言或判题功能。

## License

MIT
