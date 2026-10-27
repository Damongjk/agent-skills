# agent-skills

Damon 的私有技能版本库。主力使用 Codex 和 WorkBuddy，AStudio 读取通用技能；Agent 专用技能单独隔离。

## 当前同步方式

- 本机主副本：`~/.cc-switch/skills/<name>`。
- 通用技能：软链接到 `~/.agents/skills` 与 `~/.workbuddy/skills`。
- Codex 专用：只链接到 `~/.codex/skills`；WorkBuddy 专用：只链接到 `~/.workbuddy/skills`。
- 发布版本：本库的 `skills/common` 或 `skills/agents/<agent>`，通过 Git 安全登录读写。
- 创建或迭代技能后，执行一次显式维护流程：检查内容与冲突、登记 CC Switch、建立链接、提交本次技能变更。没有后台双向复制服务。

CC Switch 4.0.20 原生技能下载器不能直接使用这里的 Git 登录读取私有仓库。本方案使用 `tools/skill_sync.py` 桥接私有 Git 仓库和 CC Switch 本机主副本；不是宣称 CC Switch 原生支持私有仓库。新技能登记采用有备份、检查字段结构的本地适配，CC Switch 升级后应重新验证。CC Switch 界面可能需要刷新才能显示新增项。

## 常用操作

在本仓库目录运行（使用已安装的 Python）：

```text
python tools/skill_sync.py status
python tools/skill_sync.py install skill-maintenance skill-sync-probe
python tools/skill_sync.py adopt <新技能文件夹> --scope common
python tools/skill_sync.py checkpoint <技能名> --message "说明本次变更"
python tools/skill_sync.py pull
```

日常通过应用目录中的软链接修改，内容会立即回到 CC Switch 主副本；GitHub 在 `checkpoint` 推送成功后才更新。新技能通过 `adopt` 进入主副本并建立链接。文件两端都变更时会停止，保留双方，不按时间覆盖、不强制推送。

创建和迭代技能的授权不包括上传客户资料、密钥、项目数据或内部资源清单。当前只发布维护流程和无业务数据的验证技能；现有业务技能须完成版本统一与内容审查后逐项纳入。

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
