# 私有平台兼容与工具分流

2026-10-27 对照当前 ifeishu MCP 工具描述与 conventions；以下是此部署的已知约束，不是飞书公有云或未来版本的通用能力保证。

| 对象/问题 | 当前做法与边界 |
| --- | --- |
| 任意资源链接、Wiki 包装 | 先 inspect，使用 canonical 类型/token；Wiki node 偶发 131005，不反复猜 node/space ID |
| Docx 正文 | doc_read、doc_create、doc_update；当前写入 v1 Markdown，不能从公有云 XML/块接口推定真表格等能力 |
| Base | base_query 列表/字段/记录、base_write 批量记录；不能枚举所有 Base，真实链接定位。底层 bitable/v1 不代表所有公有云 Base 功能可用 |
| Drive 文件 | drive 暴露上传/下载/导出/移动/建目录/删除；当前没有列目录动作。复制、公有分享、权限治理等不因旧技能有命令就自动可用 |
| Sheets | sheet 的 create/sheets/read/write/append；先列 sheets 得 sheet_id，range 用 ID 而非标题，二维数组，检查 updatedCells 与回读。图表、格式、透视等须看是否真实暴露工具 |
| Task | task 的 my/create/update；任务不是审批/日程，不能凭公有云路由调用不存在的能力 |
| Markdown 普通文件 | 与 Docx 区分；历史 patch/overwrite 为 no version returned，不反复重试，不默认删后重建 |
| 搜索 | 索引弱，空结果不代表不存在；优先已知链接+inspect，不以空列表推断权限 |
| IM、审批、邮箱、会议、日历、妙搭 | 未由本次工具集确认可用。保留能力缺口，不能继续调用已退役框架、套用公有云命令或自动扩权 |

## 错误解释

- 91402：检查资源与权限；自检的占位 Base token 失败不代表整条链路断开。真实业务目标先 inspect，不把该错误永远归为正常。
- 1254045：字段名不符；先 list_fields。1254066 等人员/类型转换失败，确认字段类型及 ID 命名空间。
- 99991672：scope；99991668/1770032：资源或身份权限。按实际 hint 与当前授权检查，不主动公开资源、不默认扩大权限。
- 232025：此部署 Bot IM 未开通；不重复重试，不依赖已退役 Gateway。
- 9499：核对参数层级与工具公共契约；不要拿内部 batch_delete 示例直接调用 MCP。

分享范围遵守当前租户规范，仅租户范围可读/可编辑；无相应 MCP 能力时说明缺口，不另开直连通道。历史字段创建、Lookup/公式限制可作为维护线索，当前业务工具未暴露建字段动作，不据旧矩阵声称能执行。
