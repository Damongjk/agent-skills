# Base 附件限制

从原 ifeishu-base-attachment 提炼。普通 Drive 上传得到的 file_token 不等于 Base 专属附件，旧错误 1254303 表示附件不属于目标 Base。当前 MCP 的 doc_media 用于文档媒体，不能借此填 Base 附件。

按当前 conventions 和工具描述，此部署的 Base 附件上传需用户在 Web UI 完成。不要为绕行上传调用未暴露的端点、伪造 parent_type 或混用媒体 token。

可按任务从已有彩页、PPT 或文档提取封面素材供用户上传；只在用户需要时做，不改变原文件和现有附件。未来若维护服务补齐专用能力，单独按真实接口与目标 Base 验证后更新此参考。
