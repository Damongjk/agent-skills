---
name: ifeishu-mcp-ops
description: 排查 i讯飞 MCP 连接、认证、权限、字段和平台兼容性问题，或在单独维护任务中扩展服务；维护跨 Agent 唯一入口与防重复写入边界。不把普通业务操作转成底层 CLI/API 调用。
---

# i讯飞 MCP 接入与排障

Codex、WorkBuddy、AStudio 的 i讯飞操作统一使用 ifeishu MCP。当前工具定义、`ifeishu_conventions` 与实际服务代码优先于旧文档快照；不固定宣称有多少工具或永久可用能力。

## 排障顺序

1. 会话未发现工具：检查当前应用的 MCP 连接和已有配置，重新加载会话；Codex 的 `[mcp_servers.ifeishu]` 不得在清理中删除。不要直接用 CLI 绕行。
2. 已发现但调用失败：先 `ifeishu_selftest(quick=True)` 诊断连通性；按需完整自检。自检是只读诊断，不能代替目标资源权限验证。
3. 链接先 inspect，再核对目标类型/token。权限、字段、参数错误按 hint 修正；仅暂态网络/限流的读取适合有限退避。写入结果不确定先读现状，不能盲目重试创建、追加或删除。
4. 对照 [平台兼容与工具分流](references/platform-compatibility.md)；附件问题看 [Base 附件](references/base-attachments.md)。明确能力缺口，普通业务任务到此说明，只有单独维护任务才修改服务。

## 维护时按需读取

- [架构与工程约束](references/architecture.md)：stdout 协议、认证边界、批量参数、错误和重试。
- [设备接入](references/deployment.md)：当前 Windows 依赖与 Mac 实机验证边界。
- [公有云经验提炼](references/reusable-workflows.md)：保留的通用经验、未迁入的公有云功能。

维护前确认改动范围，优先本地单元检查和只读自检。真实创建/清理云端测试资源需要明确限定目标的授权；不要把技能中的冒烟说明当作授权。技能不保存凭据，不默认下载安装/升级依赖，不修改现有认证或 MCP 服务代码。
