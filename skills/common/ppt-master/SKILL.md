---
name: ppt-master
description: 从文档或主题生成原生可编辑 PPTX，制作可复用品牌/布局模板，填充已有 PPTX，或为成稿增加过渡、备注与旁白。适合方案演示、咨询报告和数据展示；单纯文本转换使用 pptx-text-rewrite。
license: MIT
metadata:
  upstream: https://github.com/hugohe3/ppt-master
  upstream-version: 4.1.0
  adaptation: Codex-WorkBuddy-common
---

# PPT Master

基于 Hugo He 的 [PPT Master](https://github.com/hugohe3/ppt-master)，保留本包 scripts、workflows、references 和 templates。通用入口适用于 Codex/WorkBuddy/AStudio；不要求 Hermes 工具、固定模型或另一项已停用技能。

## 任务入口

先用共同安装的 `ppt-layout-spec` 读取个人规范；设计前和验收前均检查。若其缺失，说明依赖缺失并按用户已给要求处理，不能声称完成个人规范验收。

阅读 [路由](workflows/routing.md)，选与目标相符的一个主流程，再按需读取支持资料：

| 目标 | 工作流 |
| --- | --- |
| 新建 PPTX 或按素材重做 | [Generate](workflows/generate-pptx.md) |
| 建立可复用模板 | [Create Template](workflows/create-template.md) |
| 用原生 PPTX 模板填内容 | [Fill Native PPTX](workflows/template-fill-pptx.md) |
| 保持可见页面并添加原生效果 | [Enhance](workflows/native-enhance-pptx.md) |

输出必须符合用户要求的可编辑程度。整页图片嵌入不能冒充原生可编辑页面。模板填充、保持文案的美化和重新创作的边界以任务为准。

## 本地约定优先

- PPT 默认浅色（白/浅灰）；内部材料也不自动深色。用户明确指定深色才启用。
- 对外材料默认英文单语，中文/双语依用户要求。个人排版规则覆盖包内与其冲突的默认设计偏好。
- 使用当前客户端已有的演示文稿、图片和文件能力；支持文档中的工具名称、模型、命令是实现参考，不要求当前客户端拥有同名能力。缺少能力时说明缺口，不自动下载安装或改系统配置。
- 用户已经给定素材、范围或确认方向时沿用，不机械重复提问。工作流中的确认门在确实缺少信息/授权时才阻塞；已有授权可以继续。
- 根据实际 Python 环境执行脚本；Windows 可能使用 `python`，Mac 按已有解释器。不要绑定某台设备绝对路径。
- 更新技能只走个人 CC Switch/版本库维护流程，不在普通 PPT 任务中 git fetch/pull 或自行更新上游。

## WPS 与原生兼容性

旧环境曾出现备注缺少 notesMaster 的打开问题，以及图表/动画的显示差异；这些是历史兼容性经验，不是所有版本都必然失败。默认优先已验证的形状/SVG 转换路径；用户需要原生图表、备注或动画时检查完整关系、字体并在目标软件验证。不把“支持 PPTX”当作 WPS/PowerPoint 跨版本无差异保证。

涉及原文件编辑、锁定、OOXML 和品牌参考时读取 [安全操作与品牌参考](references/personal-operations.md)。客户项目内容不固化进通用模板。交付前检查页面、对象可编辑性、换行、裁切、文件关系及成品渲染；无法在目标办公软件打开验证时说明限制。
