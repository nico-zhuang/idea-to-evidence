# 固定资料包（评测用，不是当前实时验证）

供有/无 Skill 的 Agent 在**相同离线证据**下比较问题重构与结论，不得声称评测执行时重新打开这些链接。资料来源在此前会话由工具打开或独立研究 Agent 报告；原始事实可能随平台版本变化。给定资料之外的产品功能、权限与许可不能编造。

1. 【官方文档历史快照】[企业会议开始事件](https://open.feishu.cn/document/server-docs/vc-v1/meeting/events/all_meeting_started.md) 描述 `vc.meeting.all_meeting_started_v1`、`vc:meeting.all_meeting:readonly`，事件体含会议 ID、主题和时间等元数据；它**没有原始音频字段**。此项不证明平台所有接口都没有音频。
2. 【官方仓库文档历史快照，未运行】[larksuite/channel-sdk-python 的 meeting-channel](https://github.com/larksuite/channel-sdk-python/blob/main/docs/meeting-channel.md) 描述对**特定会议**的 follow_my_meeting 文字 transcript，以及 bot 入会的事件；涉及用户授权、bot 权限、会议允许 agent 等限制。文字转写不等于原始音频；特定会议不等于全租户。
3. 【官方产品介绍历史快照，未验租户】[飞书智能纪要说明](https://www.feishu.cn/content/article/7577317993749269689) 称可提取决策/待办及责任人、转为任务持续跟进。当前用户的租户是否可用、提取准确率、是否有跨会台账均未实测。
4. 【公开仓库历史核对，未运行】[meeting-processor](https://github.com/peachgreenti/meeting-processor) README 声称提取会议决策/待办并建飞书任务，[许可证文件](https://api.github.com/repos/peachgreenti/meeting-processor/license) 此前核为 MIT；依赖 Python、Node、lark-cli 和 AI API key，实际生产效果和权限未验证。
5. 【当前情境示例，不是真实用户数据】某企业负责人说“希望把全部会议内容自动汇总给老板”；团队可能还没有界定要覆盖每场会议的原始声音、纪要，还是仅需自己参会会议的行动项；会议中可能含个人/客户敏感信息。没有获得任一参会人或管理员授权，不能登录、监听或推送。
