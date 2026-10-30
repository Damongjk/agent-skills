# 进度、基线与映射

本机索引：`~/.cc-switch/local-context/ifeishu-resources.json` 的 shelf。
素材/字段基线：由索引中的文件路径定位；与技能包分离，不推送到技能仓库。

## 映射可信度

- resource：由用户链接 + inspect 验证，保存原租户 URL 与 canonical token。
- record_mappings：记录 ID、表 ID、名称和素材根目录；名称用于识别，ID用于操作。共享目录显式标记。
- material_bindings：由当前富文本真实 link 与已扫描文件目标逐项核对形成，保留 record_id、field、实际 URL、源文件 token、快捷方式 target、目录 token。
- category_candidates：从目录语义生成、尚未与既有字段链接证实的候选。不能把候选写成已验证映射，不能仅凭候选新增记录或更新人员/关联。
- 若当前表、目录或记录与索引不符，重新读取确认并增量修正索引；不重建全部映射、不猜失效记录。

## 扫描调用

start 使用已验证 roots=[{token,name}]、exclude_folder_tokens 和同范围 baseline_scan_id。
工具返回 scan_id 后立即保存为 active_scan_id；后续仅 resume(scan_id)，不要重复 start。若客户端中断未保存 scan_id，用 drive_scan(action=list) 找回本机任务。
每次最多数页，返回进度摘要；status 不读取云端。只有显式 retry_failed 才重试失败页。
complete=false 或 errors 非空时，不可宣称扫描完整，不可用于完整差异或基线提升。
results(result_kind=changes) 在完整结束后返回 added/modified/not_observed；按 next_offset 读完。
results(result_kind=entries) 可查看已读条目；partial=true 表示仍不完整。

扫描器逐页原子保存本机状态，跨 MCP 重启可续读；同一 scan_id 不并发执行。异常退出若遗留锁，先确认进程已停止再维护清理，不能自动抢锁。
按文件夹 token 防环、不自动跟随快捷方式指向的外部文件夹。扫描没有平台快照隔离；期间目录发生变化时，核对相关目录，不对“未发现”做删除结论。

## 基线与待处理项

完整扫描基线只说明当时可访问的目录状态，不说明所有变化已写入货架。
分别维护 last_complete_scan_id、last_applied_scan_id、active_scan_id 和 pending_items。
对同一 token 的改名、URL/真实目标变化、修改时间变化保留差异；不同 token 的同名文件视为不同对象。

保存最新验证过的字段原始值和指纹。指纹只覆盖本次目标字段，附件临时下载 URL/版本参数不作为业务变更。
写前指纹不是服务器原子锁；写后必须回读。部分成功只更新成功项的应用状态；未知结果先核对。
暂缓项保存原因、目标字段及来源 URL，不因下一次扫描无变化而遗忘。用户已修改/清空的字段若与上次写入基线不同，应当视为新的当前状态，不能机械恢复旧值。

首次导入历史扫描时注明来源、覆盖范围和历史时间，不能伪装成新实时扫描；只有具备逐目录完成证据的历史快照才可作基线。
