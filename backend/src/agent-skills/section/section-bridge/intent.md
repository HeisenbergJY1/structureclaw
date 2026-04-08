---
id: section-bridge
structureType: beam
version: 1.0.0
source: builtin
zhName: 桥梁截面设计
enName: Bridge Section Designer
zhDescription: 桥梁主梁、箱梁、工字梁、桥面宽度与梁间距相关的截面补参与骨架生成
enDescription: Parameter clarification and model skeleton generation for bridge girders, box girders, deck width, and girder spacing
triggers: ["桥梁", "桥梁截面", "钢箱梁", "箱梁", "桥面", "主梁", "girder", "bridge", "bridge girder", "plate girder", "box girder"]
stages: ["intent", "draft", "analysis", "design"]
capabilities: ["section.detect", "section.bridge-model", "section.draft", "section.validate", "section.analysis-handoff"]
autoLoadByDefault: true
priority: 180
---
# 桥梁截面设计

- `zh`: 当用户在讨论桥梁主梁、箱梁、板梁、工字梁、桥面宽度或主梁间距时使用。
- `en`: Use when the user is discussing bridge girders, box girders, plate girders, I-girders, deck width, or girder spacing.
- `zh`: 如果请求里还没有明确跨径，优先补跨径、桥面宽度和主梁数量；这些信息决定桥梁截面的默认建议。
- `en`: If the span is missing, prioritize span, deck width, and girder count; those parameters drive the default bridge section recommendations.
- `zh`: 对于钢桥、混凝土桥和组合桥，都要保留桥梁骨架与后续补参入口。
- `en`: Keep a bridge skeleton and follow-up clarification path for steel, concrete, and composite bridges alike.
