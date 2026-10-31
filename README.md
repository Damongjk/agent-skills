# agent-skills

Damon 的私有技能版本库。主力使用 Codex 和 WorkBuddy，AStudio 读取通用技能；Agent 专用技能单独隔离。

## 收录边界

- 只维护为 Damon 编写的个人规范、业务流程和私有维护技能。
- 第三方 Skill 由用户通过 CC Switch 关联原作者仓库并检查、安装更新，不复制、镜像或纳入本仓库同步；使用或本地适配不改变这条边界。
- 个人偏好保留为独立的个人技能，不默认维护第三方技能的定制分叉。
- 第三方技能退出本仓库维护时，只移除仓库副本、目录登记和个人同步记录，保留本机安装及应用入口；卸载须有用户明确要求。

## 当前同步方式

- 本机主副本：`~/.cc-switch/skills/<name>`。
- 通用技能：软链接到 `~/.agents/skills` 与 `~/.workbuddy/skills`。
- Codex 专用：只链接到 `~/.codex/skills`；WorkBuddy 专用：只链接到 `~/.workbuddy/skills`。
- 发布版本：本库的 `skills/common` 或 `skills/agents/<agent>`，通过 Git 安全登录读写。
- 创建或迭代个人专用技能后，执行一次显式维护流程：检查归属、内容与冲突、登记 CC Switch、建立链接、提交本次技能变更。没有后台双向复制服务。

CC Switch 4.0.20 原生技能下载器不能直接使用这里的 Git 登录读取私有仓库。本方案使用 `tools/skill_sync.py` 桥接私有 Git 仓库和 CC Switch 本机主副本；不是宣称 CC Switch 原生支持私有仓库。新技能登记采用有备份、检查字段结构的本地适配，CC Switch 升级后应重新验证。CC Switch 界面可能需要刷新才能显示新增项。

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

创建和迭代技能的授权不包括上传客户资料、密钥、项目数据或内部资源清单。经用户确认，6 项核心技能已统一并纳入：`ppt-layout-spec`、`pptx-text-rewrite`、`feishu-doc-quality`、`ifeishu-crm-ops`、`iflytek-base-solution-update`、`ifeishu-mcp-ops`。另保留维护流程和无业务数据的验证技能。

PPT Master、Frontend Slides、Archify 等第三方技能均由用户通过 CC Switch 关联上游并管理更新，本仓库不收录、定制或同步这些技能。独立的 `ppt-layout-spec` 个人排版规范继续保留。

内部 Base、表、文件夹和人员 ID 保留在每台电脑本机的 `~/.cc-switch/local-context/ifeishu-resources.json`，不进入技能 Git 包。换设备时可经用户批准的内部渠道传递该索引，再验证访问权限；认证凭据始终另行配置。

Lark 公有云技能的可复用流程已提炼入私有云核心技能，不保留公有云 CLI 入口。普通 i讯飞任务只走 ifeishu MCP；不以底层实现内部使用 CLI 为理由绕过 MCP。Mac 实机、完整办公软件兼容和真实业务写入不因本次本地校验而视为已验证。

## 新设备

1. 安装并初始化 CC Switch，主副本位置选择 CC Switch 目录。
2. 用本机 Git 的安全登录访问此私有库，然后克隆到 `~/Documents/Codex/agent-skills`。
3. 执行 `python tools/skill_sync.py pull`，或先 `install` 指定技能。
4. Windows 需要系统允许创建符号链接；遇到权限错误停止，不自动更改系统设置。

Windows 已进行文件级验证；Mac 仍需在实际设备验证。读取旧版应用独立副本时发现分叉会停止，不会覆盖。

## 本地测试

```text
python -m unittest discover -s tests -v
```

测试使用隔离目录和临时 CC Switch 表，覆盖共享链接回写、新技能登记、Agent 专用隔离、冲突保护及敏感值阻断。它们不等同于真实 Agent 已重新加载或 Mac 实机验证。
