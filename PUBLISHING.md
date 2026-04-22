# GitHub 发布说明 & 安装指南

---

## 一、发布到 GitHub

### 1. 初始化仓库（本地）

```bash
cd juicebro-content-hub

# 初始化 git
git init

# 配置作者信息（若尚未配置）
git config user.name "yourname"
git config user.email "you@example.com"
```

### 2. 首次提交

```bash
# 添加所有文件
git add .

# 查看将要提交的文件（确认无误）
git status

# 创建首次提交
git commit -m "feat: init juicebro-content-hub skill v0.1.0

- 完整账号矩阵（12个平台）
- 6种查询意图路由
- 12个平台适配器说明
- NormalizedPost / NormalizedResult JSON Schema
- 5个可复用提示模板
- 4个骨架辅助脚本（含类型标注和扩展点）
- 完整示例输出和安全声明"
```

### 3. 创建 GitHub 仓库并推送

在 GitHub 网页创建新仓库 `juicebro-content-hub`，然后：

```bash
# 关联远程仓库
git remote add origin https://github.com/Juicebro-star/juicebro-content-hub.git

# 设置主分支并推送
git branch -M main
git push -u origin main
```

### 4. 添加 GitHub Topics（建议）

在仓库页面 About 部分添加以下 Topics：
```
agent-skill  content-aggregation  juicebro  chinese-social-media
multi-platform  claude-code  openclaw  hermes
```

### 5. 设置 Release（可选）

```bash
# 创建 v0.1.0 tag
git tag -a v0.1.0 -m "Release v0.1.0 - 声明式中台 Skill 首版"
git push origin v0.1.0
```

在 GitHub Releases 页面基于该 tag 创建 Release。

---

## 二、安装说明

### 方式一：Claude Code（npx skills）

```bash
# 全局安装（推荐，所有项目可用）
npx skills add Juicebro-star/juicebro-content-hub --skill juicebro-content-hub -g -y

# 验证安装
npx skills list

# 卸载
npx skills remove juicebro-content-hub -g
```

安装后，在 Claude Code 对话中直接使用：
```
果汁哥今天发了什么
果汁哥最近关于比特币发了什么
把果汁哥今天更新做成日报
```

### 方式二：OpenClaw

在 OpenClaw 配置文件中添加（`~/.openclaw/config.yaml`）：

```yaml
skills:
  - source: github
    repo: Juicebro-star/juicebro-content-hub
    skill: juicebro-content-hub
    version: main
    auto_load: true
```

或在交互界面中：
```
/skill load github:Juicebro-star/juicebro-content-hub#juicebro-content-hub
```

### 方式三：Hermes

告知 Hermes：
```
这是一个 GitHub 可安装 Skill，请加载并使用它：
- 仓库：https://github.com/Juicebro-star/juicebro-content-hub
- Skill 入口：skills/juicebro-content-hub/SKILL.md
- Skill 名称：juicebro-content-hub
- 用途：查询"果汁哥"全平台公开内容
```

Hermes 会读取 SKILL.md 中的 YAML frontmatter，自动注册。

### 方式四：本地开发

```bash
git clone https://github.com/Juicebro-star/juicebro-content-hub.git

# 测试辅助脚本
cd juicebro-content-hub
python scripts/topic_classifier.py
python scripts/normalize_results.py
python scripts/optional_fetcher.py

# 本地引用
npx skills add ./skills/juicebro-content-hub --local
```

---

## 三、维护指南

### 更新账号信息

若果汁哥账号有变更，更新以下文件：
1. `skills/juicebro-content-hub/data/accounts.json`
2. 对应平台的 `skills/juicebro-content-hub/adapters/*.md`
3. `README.md` 中的账号矩阵表格

```bash
git add skills/juicebro-content-hub/data/accounts.json
git commit -m "data: update weibo account name"
git push
```

### 添加新主题关键词

编辑 `skills/juicebro-content-hub/data/topic_keywords.json` 和 `scripts/topic_classifier.py` 中的内联关键词表（保持同步）。

### 发布新版本

```bash
# 更新 SKILL.md 中的 version 字段
# 更新 README.md 的 Badge

git add .
git commit -m "release: v0.1.1 - 新增更多主题关键词"
git tag -a v0.1.1 -m "v0.1.1"
git push && git push --tags
```
