---
id: yjk-static
zhName: YJK 静力分析
enName: YJK Static Analysis
zhDescription: 使用 YJK (盈建科) 引擎执行静力分析的 skill（需安装 YJK）。
enDescription: Skill for static analysis using the YJK engine (requires YJK installation).
software: yjk
analysisType: static
engineId: builtin-yjk
adapterKey: builtin-yjk
priority: 125
triggers: ["YJK 静力分析", "YJK 计算", "盈建科", "yjk static", "yjk analysis"]
stages: ["analysis"]
capabilities: ["analysis-policy", "analysis-execution"]
supportedModelFamilies: ["frame", "generic"]
autoLoadByDefault: false
runtimeRelativePath: runtime.py
---
# YJK Static Analysis

- `zh`: 当用户要求使用 YJK（盈建科）进行结构静力计算、设计验算时使用。需要已安装 YJK 并配置 `YJK_PATH` 环境变量。
- `en`: Use when the request asks for YJK-based structural static analysis or design checks. Requires YJK installation and the `YJK_PATH` environment variable.
- Runtime: `analysis/yjk-static/runtime.py`
