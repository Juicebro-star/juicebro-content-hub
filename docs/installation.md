# 安装与接入指南

本文档介绍如何在不同 Agent 环境中安装和使用 `juicebro-content-hub` Skill。

> **说明**：以下各方式均为参考接入示例，各 Agent 平台的 CLI 命令和配置格式可能随版本更新变化，请结合当前 Agent 文档做调整。

---

## 方式一：Claude Code（npx skills）

### 前置条件

- Node.js >= 16
- Claude Code CLI 已安装（参考 [Claude Code 官方文档](https://docs.anthropic.com/claude-code)）

### 全局安装（参考命令）

```bash
npx skills add Juicebro-star/juicebro-content-hub --skill juicebro-content-hub -g -y
```

参数含义参考：
- `Juicebro-star/juicebro-content-hub`：GitHub 仓库路径
- `--skill juicebro-content-hub`：指定 Skill 目录名
- `-g`：全局安装，所有项目可用
- `-y`：自动确认，跳过交互提示

### 项目级安装

```bash
cd your-project
npx skills add Juicebro-star/juicebro-content-hub --skill juicebro-content-hub
```

### 验证安装

```bash
npx skills list
```

输出中应包含 `juicebro-content-hub`。

### 在 Claude Code 中使用

安装后，在对话中直接输入自然语言即可：

```
果汁哥今天发了什么
果汁哥最近关于比特币发了什么
把果汁哥今天更新做成日报
```

---

## 方式二：OpenClaw

### 配置文件接入（参考格式）

在 OpenClaw 的配置文件中（通常为 `~/.openclaw/config.yaml` 或项目根目录的 `.openclaw.yaml`）添加以下配置（请按当前 OpenClaw 版本的实际配置格式调整）：

```yaml
skills:
  - source: github
    repo: Juicebro-star/juicebro-content-hub
    skill: juicebro-content-hub
    version: main        # 或指定 tag，如 v0.1.1
    auto_load: true
```

保存后重启 OpenClaw，Skill 将自动加载。

### 手动激活（参考命令）

```
/skill load github:Juicebro-star/juicebro-content-hub#juicebro-content-hub
```

### 验证

```
/skill list
```

---

## 方式三：Hermes

Hermes 支持将 GitHub 仓库作为 Skill 源接入。可参考以下方式告知 Hermes：

```
这是一个 GitHub 可安装 Skill：
- 仓库：https://github.com/Juicebro-star/juicebro-content-hub
- Skill 入口：skills/juicebro-content-hub/SKILL.md
- Skill 名称：juicebro-content-hub
```

Hermes 读取 `SKILL.md` 中的 YAML frontmatter 和提示说明，完成 Skill 识别与注册。具体接入步骤请参考当前 Hermes 版本文档。

---

## 方式四：兼容 AgentSkills 生态的通用接入

对于支持 `SKILL.md` 格式的 Agent 框架，直接将本仓库克隆到本地：

```bash
git clone https://github.com/Juicebro-star/juicebro-content-hub.git
```

然后将 `skills/juicebro-content-hub/` 目录注册到你的 Agent 框架的 Skill 搜索路径中。

Skill 入口文件：`skills/juicebro-content-hub/SKILL.md`

---

## 方式五：本地开发调试

```bash
# 克隆仓库
git clone https://github.com/Juicebro-star/juicebro-content-hub.git
cd juicebro-content-hub

# 安装可选的 Python 依赖（用于辅助脚本，非核心功能）
# pip install requests feedparser jieba  # V2 阶段所需依赖

# 直接引用本地 Skill（参考命令，请按实际 CLI 版本调整）
npx skills add ./skills/juicebro-content-hub --local
```

---

## 环境变量（可选）

以下环境变量为可选配置，仅用于辅助脚本（不影响 Skill 核心功能）：

| 变量名 | 用途 | 默认值 |
|--------|------|--------|
| `JUICEBRO_CACHE_DIR` | 本地缓存目录路径 | `~/.juicebro-cache` |
| `JUICEBRO_LOG_LEVEL` | 日志级别（DEBUG/INFO/WARNING） | `INFO` |
| `JUICEBRO_MAX_POSTS` | 单次查询最大返回条数 | `50` |

**注意**：本 Skill 不需要也不应设置任何平台 API 密钥。核心功能依赖 Agent 的公开内容访问能力，不要求额外凭证。

---

## 卸载

```bash
# Claude Code 全局卸载（参考命令）
npx skills remove juicebro-content-hub -g

# Claude Code 项目级卸载
npx skills remove juicebro-content-hub
```

---

## 常见问题

**Q: 安装后 Agent 没有响应相关查询？**

A: 确认 Skill 已正确加载（`npx skills list` 或 `/skill list`）。有些框架需要重启后 Skill 才生效。

**Q: 查询某个平台时返回"无法访问"？**

A: 该平台可能需要登录或存在公开访问限制。本 Skill 遵循安全原则，不绕过登录，会明确说明原因。详见 [`docs/safety.md`](./safety.md)。

**Q: 如何更新到最新版本？**

```bash
npx skills update juicebro-content-hub -g
```

**Q: 可以同时安装多个版本吗？**

A: 不建议。请使用 `npx skills update` 升级到最新版。

**Q: 辅助脚本需要额外依赖吗？**

A: `scripts/` 目录下的脚本为 V1 骨架实现，当前无外部依赖。V2 引入真实数据接入后将按需添加 `requests`、`feedparser` 等依赖，届时会提供 `requirements.txt`。
