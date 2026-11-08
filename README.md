# 想法深化 · idea-to-evidence

把零散想法推进为有来源、有反证、可选择下一步的判断，而不是直接生成 PRD 或默认自建。中文触发语：**「帮我把这个想法深化一下」**。

> **状态：实验性 Skill。** 已做结构测试和若干有／无 Skill 对照；目前没有证明它能在不同案例中稳定改变最终推荐路线。公开仓库里的合成/历史评测样例不是实时研究或生产验证。

## 安装到其他设备

在支持 Agent Skills 的设备上，使用 [Skills CLI](https://skills.sh/)：

```bash
npx skills add nico-zhuang/idea-to-evidence -g -y
```

该命令会按 Skills CLI 的规则安装到该设备支持的 Agent 工具。完成后在新对话中说：

> 帮我把这个想法深化一下：我想让三个仓库中新贴上 `needs-triage` 标签的 Issue 自动进入同一个待审看板。先查现有办法，不要写代码。

本机 DeepSeek Harness 的手工安装备选（macOS/Linux，**仅在目标目录不存在时**执行）：

```bash
mkdir -p ~/.agents/skills
git clone https://github.com/nico-zhuang/idea-to-evidence.git ~/.agents/skills/idea-to-evidence
```

若是按上面的 `git clone` 安装的，日后在该设备更新：

```bash
git -C ~/.agents/skills/idea-to-evidence pull --ff-only
```

Codex、HanaAgent 等工具的个人 Skill 目录可能不同，应使用其自身的 Skills CLI 集成或安装目录；不要覆盖已安装的同名 Skill 而不先备份。安装后是否在现有会话立刻更新技能目录，取决于宿主；若没有出现新 Skill，可开启新会话检查。

## 使用与可选依赖

- 主文件：[SKILL.md](SKILL.md)。Agent 先按当前决策难度选择对话、快速试验、有界比较或决策级研究，再区分用户原话、推断与未知。只求一项便宜可逆试验时可暂缓 GitHub 对照并明示未完成；完整路线比较或自建建议仍须核验 GitHub 候选的实际 LICENSE、运行前提与权限。已明确的执行任务不插入想法研究。分流是待行为评测的设计，不代表速度或准确率已实测提升。
- 条件式专家关口 G1/G2 依赖**另行安装的 `ask-five-pro`**，本仓库**不包含**该 Skill，也不会自动安装它。缺失时按[关口说明](references/ask-five-gates.md)记录议会未执行，继续仅凭可核证事实做有限研究；不得虚构专家意见。高利害议题须尊重专家名单确认暂停，不能把匹配名单、读取说明当成已经开会。
- [决策结构审计脚本](scripts/decision_audit.py)仅使用 Python 标准库，按需运行，**只查字段和自洽约束，不验来源事实**；不需要执行候选仓库代码。
- [evals/](evals/) 包含合成题、历史快照和早期基线文件，供理解/测试，不等于当前文档、许可证或用户账户权限的证据。部分评测题卡引用未随本独立仓库发布的旧工作区资料；这类题不能单凭本仓库完整复现。核心 Skill 的运行不依赖这些题卡。

可在仓库根目录运行本地结构测试：

```bash
python3 -m unittest discover -s tests -q
```

## 发布与许可边界

本仓库公开可见，当前**未附开放源代码 LICENSE**；公开可读与作者自行在其他设备安装，不等于已向第三方授予修改、再发布的许可。参考材料注明的第三方项目许可只适用于各自项目，不自动适用于本仓库。
