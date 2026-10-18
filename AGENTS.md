# 当前项目约束

- 视觉、UI与建模唯一依据是 `design/final/city.png`、`campus.png`、`building.png`；用户确认及哈希见该目录。不要使用旧截图、历史概念或参考案例覆盖终稿。
- `planning/project.json` 是唯一规划/模型/数据事实源。三张终稿是视觉输入，模型、运行配置与指标从规划源派生；不得手改GLB、runtime.json或dist。
- 当前模型和网页尚未完全对齐终稿；先读 `docs/implementation-status.md`，不能把终稿确认当成实现验收。
- `assets/materials/` 仅存重建必需的幕墙与树叶贴图，不是整屏设计参考。
- `docs/history/`、`checks/`旧版本证据、`state.json`历史字段及 `work/archive/` 不作为当前设计与建模依据；除非明确查证历史，不主动读取。
- 修改终稿必须先展示新图并取得用户确认；候选草稿放 `work/`，确认后替换当前终稿，不在design中堆积并列版本。
- 每版在实际浏览器用相同相机、画布和数据与终稿逐层对照；结构测试不能替代视觉和性能验收。
