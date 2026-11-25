# Changelog

## [1.4.1] - 2026-11-25
- 修复版本一致性：plugin.json / README / 本地安装目录 / marketplace.json 统一为 1.4.1
- 评测集修复：5 份 fixtures 重建为互相关联的干净制造业数据（外键全有效）
- 场景 05 由零售改为制造业售后质量，与 fixtures 及 README 一致
- RAG 技能接通：agent MD 声明 ontology-rag 并内置「深度咨询先检索再作答」指引
- SKILL.md 重写为中文调用契约，补齐 ontology_rag_integration.py
- 向量库重建为 43 块（清除污染数据与旧零售场景），GitHub 发布 v1.4.1

## [1.4.0] - 2026-11-21
- 版本号升级至 1.4.0，README badges 与类型行同步
- CHANGELOG 新增 1.4.0 条目，重新打包 dist/ontology-navigator.zip
- GitHub 推送 a0ce385（本次 1.4.1 补齐了原本占位式的条目描述）

## [1.3.1] - 2026-11-21
- 新增 ontology-rag 技能（本地向量库+TF-IDF 检索，零依赖实现）
- 新增 SKILL.md 并规范 ontology-rag 技能目录结构
- 更新 plugin.json：版本 1.3.1、description 双语、新增 ontology-rag 技能路径
- README 添加 Shields.io badges（版本/许可/类型/类别）
- 构建 v1.3.1 包并推送至 GitHub

## [1.3.0] - 2026-11-12
- 补齐作者信息与 keywords/homepage 元数据
- 新增 references/palantir-ontology-methodology.md 进阶方法论文档（反模式/Action 细则/身份解析/AIP grounding/采纳度量）
- 注意事项补充"不适用范围"边界约束
- maxTurns 50 -> 80

## [1.2.0] - 2026-11-12
- 重写包内 README.md，消除全部 [TODO] 占位符
- 新增 ontology-toolkit skill（三层建模表/90天路线图/诊断问卷模板）
- Agent MD 补充零售、金融服务行业示例锚

## [1.1.0] - 2026-11-12
- 新增首轮响应铁律：先交货后提问、假设显式化、提问限流
- 内置示例建模锚作为输出质量基准
- 重写 quickPrompts 为自带场景细节版本

## [1.0.0] - 2026-11-12
- 初始版本：本体领航员 Ontology Navigator 专家（基于 Palantir Foundry Ontology 方法论）
