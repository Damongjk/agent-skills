# agent-skills

Damon 的个人私有技能版本库。主力使用 Codex 和 WorkBuddy，AStudio 读取通用技能；Agent 专用技能单独隔离。

## 收录边界

- 只维护为 Damon 编写并经内容审核的个人规范、可复用业务流程和个人维护技能。
- 第三方 Skill 由用户通过 CC Switch 关联原作者仓库并检查、安装更新，不复制、镜像或纳入本仓库同步；使用或本地适配不改变这条边界。
- 个人偏好保留为独立的个人技能，不默认维护第三方技能的定制分叉。
- 第三方技能退出本仓库维护时，只移除仓库副本、目录登记和个人同步记录，保留本机安装及应用入口；卸载须有用户明确要求。

## 当前同步方式

- 本机主副本：`~/.cc-switch/skills/<name>`。
- 通用技能：软链接到 `~/.agents/skills` 与 `~/.workbuddy/skills`。
- Codex 专用：只链接到 `~/.codex/skills`；WorkBuddy 专用：只链接到 `~/.workbuddy/skills`。
- 发布版本：本库的 `skills/common` 或 `skills/agents/<agent>`，通过 Git 安全登录读写。
- 创建或迭代个人专用技能后，执行一次显式维护流程：检查归属、内容与冲突、登记 CC Switch、建立链接、提交本次技能变更。没有后台双向复制服务。

本库为私有仓库，读取和推送都使用本机已有 Git 登录和仓库权限。`tools/skill_sync.py` 协调 Git 仓库与 CC Switch 本机主副本，并自动检查已有代理连接；无需将仓库改为公开。GitHub 插件使用独立授权，插件访问成功不替代本机 Git 同步验证。

CC Switch 已登记为 `Damongjk/agent-skills` 的技能可直接同步，保留来源、分支、文档链接和已有应用启用开关。其他仓库或来源不完整的记录仍会被拦截，不清空来源来绕过检查。新技能登记采用有备份、检查字段结构的本地适配，CC Switch 升级后应重新验证。

CC Switch 4.0.33 的内置技能下载仍使用未认证的 GitHub ZIP 请求，因此其“检查更新/更新”不能代替本私有库的同步工具。个人技能使用下方 `pull` / `checkpoint`，第三方技能继续通过 CC Switch 关联原作者并更新。保留个人仓库来源记录，不修改应用二进制或把凭据写入配置。依据：[该版本下载实现](https://github.com/farion1231/cc-switch/blob/v4.0.33/src-tauri/src/services/skill.rs#L4200)。

## 常用操作

在本仓库目录运行（使用已安装的 Python）：

```text
python tools/skill_sync.py status
python tools/skill_sync.py install skill-maintenance skill-sync-probe
python tools/skill_sync.py adopt <个人专用技能文件夹> --scope common
python tools/skill_sync.py checkpoint <技能名> --message "说明本次变更"
python tools/skill_sync.py pull
```

日常通过应用目录中的软链接修改，内容会立即回到 CC Switch 主副本；GitHub 在 `checkpoint` 推送成功后才更新。新的个人专用技能通过 `adopt` 进入主副本并建立链接。文件两端都变更时会停止，保留双方，不按时间覆盖、不强制推送。

用户已授权将个人技能的创建和迭代同步至此私有仓库，每次仍须审核具体改动；未经用户要求不更改仓库可见性。此授权不包括上传客户资料、密钥、项目数据或内部资源清单。经用户确认，6 项核心技能已统一并纳入：`ppt-layout-spec`、`pptx-text-rewrite`、`feishu-doc-quality`、`ifeishu-crm-ops`、`iflytek-base-solution-update`、`ifeishu-mcp-ops`。另保留维护流程和无业务数据的验证技能。

PPT Master、Frontend Slides、Archify 等第三方技能均由用户通过 CC Switch 关联上游并管理更新，本仓库不收录、定制或同步这些技能。独立的 `ppt-layout-spec` 个人排版规范继续保留。

内部 Base、表、文件夹和人员 ID 保留在每台电脑本机的 `~/.cc-switch/local-context/ifeishu-resources.json`，不进入技能 Git 包。换设备时可经用户批准的内部渠道传递该索引，再验证访问权限；认证凭据始终另行配置。

Lark 公有云技能的可复用流程已提炼入私有云核心技能，不保留公有云 CLI 入口。普通 i讯飞任务只走 ifeishu MCP；不以底层实现内部使用 CLI 为理由绕过 MCP。Mac 实机、完整办公软件兼容和真实业务写入不因本次本地校验而视为已验证。

## 新设备

1. 安装并初始化 CC Switch，主副本位置选择 CC Switch 目录。
2. 使用本机 Git 的安全登录和已授予的私有仓库权限，克隆本库到 `~/Documents/Codex/agent-skills`。GitHub 插件连接不会自动登录另一台设备的 Git。
3. 执行 `python tools/skill_sync.py pull`，或先 `install` 指定技能。
4. Windows 需要系统允许创建符号链接；遇到权限错误停止，不自动更改系统设置。

各设备需分别验证登录、连接和应用加载；一台设备的同步成功不代表其他设备已验证。读取旧版应用独立副本时发现分叉会停止，不会覆盖。

## 本地测试

```text
python -m unittest discover -s tests -v
```

测试使用隔离目录和临时 CC Switch 表，覆盖共享链接回写、新技能登记、Agent 专用隔离、冲突保护及敏感值阻断。它们不等同于真实 Agent 已重新加载或 Mac 实机验证。
