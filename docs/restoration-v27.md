# v27 制作与实际验证

视觉输入保持 `design/final/city.png`、`campus.png`、`building.png`；本轮没有更换终稿。工程参数和演示指标从 `planning/project.json` 派生。

## 本轮修正

| 项目 | 原因与修改 | 真实产物／复验 |
| --- | --- | --- |
| 树种色彩与轮廓 | 改用统一透明四树种图集，绿色、浅金黄、近白樱花粉与深绿香樟按面UV取样 | `assets/materials/foliage-atlas-v27.png`；园区与城市实际截图 |
| 园区铺装光照 | MCP 中执行 Cycles COMBINED 烘焙；平面UV导致重叠后，改为联合无重叠UV并重烘焙 | `checks/mcp-campus-ground-fixed-v27.json`；`checks/v27-campus.png` |
| 楼宇幕墙 | 在同一八栋业务根节点内增加楼板、墙面、隔断和灯带；窗后墙面使用固定办公图集，不整面覆盖外幕墙，移除随机旧亮片；保留24层的 A1、三级裙房和经营口径 | `assets/mcp-operations/v27/campus-polish.json`、`campus-glass.json` |
| AO／间接光 | A1石材、框架、竖梃、屋面与静态设施使用UV2；城市静态地表AO重新烘焙 | `campus-ao.json`、`campus-indirect.json`、`city-ao.json` |
| 城市地表 | 保持湖岸和道路拓扑，统一树冠材质，补2400组低矮植被；地表改用低对比无方向斑驳，移除初版周期条纹 | `city-detail.json`、`city-tone.json`；普通道路水域交叉为0 |
| 天空和边缘 | 天空纹理使用线性过滤并提高分辨率；加入SMAA；补暖色侧光表现竖梃 | `app/src/daylight-environment.js`、`SceneView.js` |
| 性能 | 园区总览不重复绘制窗后结构与折射；仅A1近景启用室内与半分辨率折射缓冲 | 实际页面指标、重复切层记录 |
| 文档展示 | README使用实际网页截图，AI设计图仍独立保存在唯一终稿目录 | `docs/images/` |

南侧两条步行出口延续 v26 的修复：终点Y=-159.5m，车行道内缘Y=-160m，保留0.5m净距。绿色、金黄与浅粉树种、园区南／西／东侧办公背景、行人、喷泉、廊架与座椅保留。经营指标没有因建模变动重新编造。

## MCP 与重建

实际制作工具链：MCP stdio → Blender MCP → 本机 Blender 插件 → Blender 5.2.2。代码片段通过 MCP 的执行工具运行；终端客户端不导入 bpy、不直接生成模型。

当前工程：`assets/scene.blend` 与 `assets/city.blend`，所需图像均已打包；GLB中的对象身份、米制尺寸、UV和内嵌贴图通过实际结构核对。间接光图单独位于 `app/public/assets/campus-indirect-v27.png`。

操作记录在 `assets/mcp-operations/v27/`。它们是带前置工程状态的逐次操作，不能简单从头对任意场景运行。完整工程是本版本重导入口，v25／v26记录保留制作沿革。

连接已启动的 Blender MCP 后，可使用：

```sh
python3 scripts/rebuild.py --dest work/rebuilt-check
```

`--dest` 必须是不存在的新目录；需要本机 `uvx`、Blender MCP、Node.js 与 npm。脚本将工程复制到独立目录，通过真实MCP分别加载和重导，再从规划源生成配置、安装锁定依赖并构建网页。可用 `--uvx /absolute/path/to/uvx` 指定客户端，`--cache /path/to/npm-cache` 指定依赖缓存。

本轮真实结果见 `checks/rebuild-v27-delivered.json`：两份工程均成功重新加载、导出，GLB与原资产的哈希完全相同；runtime也相同。该验证覆盖保存工程的重导和前端重建，不冒充从空白场景自动重演全部历史建模。

## 测试与网页证据

- 16项Node契约测试；3项景观净空测试；3项道路避水测试。
- 实际资产、楼层横梁、车型包络、业务ID、规划／模型／runtime版本和三张终稿哈希检查。
- 1920×1080实际生产页面：三层切换、C1数据同步、两类城市浮卡、无数据状态、交通与喷泉动态、12次重复切层及运行资源记录。
- `checks/v27-comparison.html` 完整并排呈现三层设计与实际截图，不以像素分数替代视觉判断。

本机生产构建（1920×1080）连续12次园区／楼宇往返后，几何235、纹理32保持稳定；循环采样帧间隔P95约34.3ms。切镜过程中draw calls采样259–354，瞬时高于350的制作目标，记录为性能余量限制；不称为展厅硬件认证。

## 还原差异与边界

当前完成本轮工程修复与可运行交付，不能将其称为用户已经验收终稿写实程度。城市街区分布仍为概念布局；树冠使用透明卡片，玻璃采用运行时环境反射，建筑室内为展示用层次，不是完整室内模型。AI终稿中的精细植物、自然湖岸和建筑摄影质感仍有差异，继续保留三层还原问题记录。

目标展厅硬件、数小时持续运行、完整跨浏览器矩阵和真实接口接入未验证。构建仍提示Three.js公共分包较大，不将该警告描述为构建失败或已完成进一步压缩。
