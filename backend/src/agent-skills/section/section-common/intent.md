---
id: section-common
structureType: frame
version: 1.1.0
source: builtin
zhName: 通用截面设计
enName: Common Section Designer
zhDescription: 常规梁、框架、柱与标准型钢截面的补参与模型骨架生成
enDescription: Parameter clarification and model skeleton generation for common beams, frames, columns, and standard profiles
triggers: ["截面", "工字钢", "H型钢", "钢框架", "型钢", "section", "section design", "profile"]
stages: ["intent", "draft", "analysis", "design"]
capabilities: ["section.detect", "section.draft", "section.model", "section.validate"]
autoLoadByDefault: true
priority: 100
---
# 通用截面设计

- `zh`: 当用户要求标准工字钢、H 型钢、箱形、圆管、槽钢或矩形截面时使用。
- `en`: Use when the user asks for a standard I-beam, H-beam, box, pipe, channel, or rectangular section.
- `zh`: 如果没有更专门的 bridge / irregular skill 命中，这个 skill 负责先接住请求、补齐必要参数并给出默认建议。
- `en`: If no more specialized bridge or irregular skill matches, this skill catches the request, fills the missing parameters, and suggests defaults.