# 设备接入

当前 Windows 的 Codex 配置是 `~/.codex/config.toml` 的 `[mcp_servers.ifeishu]`。已知本机服务项目为 `D:\Hermes\ifeishu-mcp`；名称虽含 Hermes，仍服务主力 Agent，不能随 Hermes 用户数据清理删除。

旧运行环境 `~/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe` 仍可能承载 MCP 依赖。先读取实际配置核实，不把系统 Python 或另一托管环境当成可直接替换。WorkBuddy/AStudio 使用各自当前 MCP 配置，避免复制凭据到 Agent 文件。

Mac：使用可用且含 MCP 依赖的 Python、可用的私有云适配器和该设备自己的安全认证方式。Windows 的 D 盘、exe 和注册表不能复制即运行。本次只验证 Windows，不声称 Mac 服务已部署。公司网络限制下，不自动下载依赖或启用内网穿透。

个人业务索引保存在 `~/.cc-switch/local-context/ifeishu-resources.json`，包含内部资源/人员坐标，没有认证凭据；与技能 Git 包分离。换设备需要时通过用户批准的内部渠道传递该文件并验证权限；不要随技能推送外部仓库，也不要把缺失索引当作资源不存在。
