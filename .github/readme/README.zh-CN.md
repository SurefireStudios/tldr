<p align="center">
  <img src="../../assets/logo.svg" alt="tldr" width="150" />
</p>

<h1 align="center">tldr</h1>

<p align="center">
  <strong>太长不看 —— 写给 AI 编程助手。</strong>
</p>

<p align="center">
  你的编程助手把答案埋在四段废话里。<br/>
  这个技能让它先给三行结论，其余内容折叠在下面。<br/>
  <em>降级，而不是删除。</em>
</p>

<p align="center">
  <a href="../../README.md" title="English">🇬🇧</a> ·
  <strong title="简体中文">🇨🇳</strong> ·
  <a href="README.es.md" title="Español">🇪🇸</a> ·
  <a href="README.pt-BR.md" title="Português (Brasil)">🇧🇷</a> ·
  <a href="README.ja.md" title="日本語">🇯🇵</a>
</p>

---

## 安装

把这句话粘贴给你的助手即可。Claude Code、Cursor、Codex、Gemini CLI 等全部适用：

```text
Install the tldr skill from https://github.com/SurefireStudios/tldr — read the repo's AGENTS.md for instructions.
```

Claude Code 也可以直接用命令：

```bash
claude plugin marketplace add SurefireStudios/tldr
claude plugin install tldr@tldr
```

其他助手请看 🔗 **[INSTALL.md](../../INSTALL.md)**。

然后输入 `/tldr`。

## 它解决什么问题

其实是两个问题。

**助手对你说得太多。** 你问了一个是非题，得到四段话、一个编号方案、一段边界情况说明，最后还有一句「希望对你有帮助！」。答案就埋在里面某处。

**助手之间也说得太多。** 一个子智能体跑完搜索，向编排者返回 4000 个 token 的叙述，而编排者只需要三行。这笔钱你付了两次：一次是生成，一次是它在后续每一轮里继续占着上下文。

多数「请简洁一点」的提示词是靠**删掉信息**来解决第一个问题的。一旦你在做代码审查、安全审计，或者任何需要负责的工作，这个代价就太大了。

## 降级，而不是删除

`tldr` 不是让助手少说，而是让它**先说重点**，其余内容原封不动地放在紧接着的下面。

什么都不会丢。深度由你决定。

```markdown
**TL;DR**
- `listOrders` 每行都查一次客户表：渲染一页要 241 次数据库往返。
- 修复：在 `src/orders/repository.ts:88` 传入 `include: { customer: true }`，并删掉它下面的循环。
- 约 10 分钟。订单基准测试已经覆盖这条路径。

<details>
<summary>完整内容</summary>

……助手本来会写的全部内容，一字不少……

</details>
```

在不渲染 HTML 的终端里，它会自动换成 `--- detail ---` 分隔线。技能本身知道这个区别。

## 深度档位

上半部分显示多少，由你决定。

| 命令 | 效果 |
| --- | --- |
| `/tldr 0` | 只有一行结论，不带详情 |
| `/tldr 1` | 一行 + 详情 |
| `/tldr 3` | **默认。** 三行 + 详情 |
| `/tldr 5` | 五行 + 详情 |
| `/tldr full` | 关闭，恢复正常 |

档位只改变摘要的长度，永远不会削减详情。

## `/tldr` 也是一个动词

可以当模式开着，也可以只对某个东西用一次：

```text
/tldr this file
/tldr that stack trace
/tldr the last 20 commits
/tldr your last answer
```

一次性生效，不改变当前模式。

## 智能体之间：省钱的地方

这是同类输出风格技能没有覆盖的一半。

当输出是给**另一个智能体**而不是给人看时，`tldr` 会切换成可解析的结构块——子智能体报告、任务结果、交接说明、提交信息、PR 描述：

````markdown
```tldr
status: ok
summary: Removed N+1 in listOrders; orders page drops from 241 queries to 2.
changed:
  - src/orders/repository.ts:88-104
next: none
risk: low — changes row ordering when a customer record is null
full: docs/reports/orders-n1.md
```
````

三条规则起作用：

1. **返回结构块然后停止。** 编排者要的是结果，不是过程。
2. **长内容写进文件，只回传路径。** 不要让它流经上下文窗口。
3. **调用方需要逐字原文的部分绝不压缩** —— 精确的报错、精确的 diff、精确的路径。

## 永不压缩的内容

压缩对散文是安全的，对后果不是。以下内容始终完整显示在折叠之上：

- 破坏性操作 —— `rm -rf`、强制推送、删表、数据库迁移
- 安全问题 —— 被折叠的漏洞等于没有报告的漏洞
- 不可逆操作与数据丢失
- 费用、配额与限流
- 你需要复制或搜索的逐字报错原文
- 正在修改的代码 diff —— 压缩过的 diff 是谎言
- 法律、医疗与安全边界
- 任何你明确要求看完整版的内容

技能里的原话是：**只读 TL;DR 的人，不应该得出错误的结论。**

## 它真的有效吗？

[`evals/`](../../evals/) 里有一套可复现的评测框架，同时测量两件事：

- **质量** —— 正确性、保真度、可执行性、安全性，对照基线盲测打分。
- **Token** —— 实际输出 token 数，因为压缩的意义就在于成本。

16 个用例 × 3 次试验，对照无技能基线盲测（`claude-sonnet-5`）：

| | 基线 | 启用 tldr | |
| --- | ---: | ---: | --- |
| 平均输出 token | 370 | **283** | −24% |
| 中位数 | 322 | **175** | −46% |
| 智能体之间 | 208 | **101** | −51% |
| 可执行性 | 4.375 | **4.688** | +0.312 |
| 保真度 | 4.667 | **4.542** | **−0.125** |

**发布门槛目前显示 FAILED**（5 条规则中 2 条未通过）。保真度差 0.025 未达标，这个失败被原样保留而不是调参绕过——保真度这一维度存在的意义，就是抓住「只因为删了东西而看起来更好」的回答，而它现在正抓住了这个技能本身。

只报其中一个，正是压缩类claim 容易误导人的地方。方法论与发布门槛见 [`evals/RESULTS.md`](../../evals/RESULTS.md)，结果无论是否好看都会公布。

## 支持的助手

Claude Code、Cursor、Codex、Gemini CLI、GitHub Copilot、OpenCode、Zed、Windsurf、Cline、Roo Code、Aider、Amp、Qwen Code、Kimi Code CLI、Pi、Oh My Pi、Antigravity —— 完整安装说明见 [INSTALL.md](../../INSTALL.md)。

技能本身就是纯 markdown、零运行时，所以任何能接受自定义指令的工具都能用。

## 许可

MIT。

---

<p align="center">
  <strong>TL;DR：点个 Star。⭐</strong><br/>
  <sub>你刚刚把一篇讲「别读长文」的 README 从头读到了尾。<br/>
  最后这一下，就别偷懒了。</sub>
</p>
