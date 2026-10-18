# 高新区数字楼宇 · B方案可运行评审版

武汉东湖高新区（光谷）产业背景，虚构示范园区，招商展示与领导汇报用途。范围已扩展为区域总览 → 园区总览 → 重点楼宇，1920×1080设计画布等比例适配。经营指标、建筑形体和坐标均为演示设定，页面持续标明“示范园区 · 演示数据”。

已实现脚本生成的八栋可交互三维模型、选择与高亮、A1下钻/返回、空间利用面板、缺失数据态、旋转/缩放/复位、巡览与全屏。两层使用同一GLB；A1为3层退台裙房+21层塔楼，总24层。八栋均有明确标注的逐栋演示指标，左侧和选中卡片读取同一快照，汇总为24万㎡、84%出租率与216家企业。

当前交付是**可运行评审版**，不等于用户已验收最终视觉。当前使用透明叶簇、幕墙图集和浅色简化远景；仍有贴图重复与静帧真实感差异，已在对照中如实记录，不承诺像素级一致。原概念图片与确认记录均保留，未重新开展调研或检索完整大屏案例。

## 当前评审版 v22

连续城市中景与远景已补充，普通道路按完整路面避让水体；18辆车包含轿车、SUV、轻型货车及黑白红灰车漆。产业、配套和楼宇浮层统一为浅色展陈卡，跟随对象自动选位，避开标签、导航、操作区和当前楼宇包络。详情及已知差异见 docs/iteration-v21.md，逐层并排对照见 checks/review-v21.html。园区进入动画已按确认分镜实现：首次约2.8秒、再次约1.1秒、A1返回约0.6秒，支持中断与加载失败重试。最新实拍预览与三层对照见 checks/review-v22.html，复验见 docs/iteration-v22.md。

## 城市还原修正版 v14（视觉待复核）

用户指出v13与设计稿差距较大，本次重开城市层还原：移除可见矩形底板，按原图平面控制点对齐区域/湖岸/园区，补青白发光边界、三色分区、岛屿、连续楼群与景观。实景对照见 checks/city-restoration-v14.html；五项问题与未关闭差异见 docs/city-review-v14.md。工程检查通过不等于视觉验收，建筑细部、水面层次与街区自然度仍待复核。

当前预览 http://127.0.0.1:4175/ ，校准模块 scripts/city_layout.py 的哈希已锁进唯一规划入口；不要手改其派生的runtime或GLB。

## 三层区域扩展 v13

默认进入区域概念沙盘，点击示范园区可进入园区，再进入A1；三层导航和缺失态贯通。区域模型3.79MB，经营指标仍属于虚构园区。当前预览 http://127.0.0.1:4175/ 。最终三层对照见 checks/comparison-v13-final.html，完整验证见 docs/verification-v13.md，城市制作规格见 docs/city-production-spec-v13-final.md。

城市轮廓、道路与点位均为示意，不能用作真实武汉地理依据。城市装饰楼群不纳入经营统计。

## 车辆动画更新 v12

18辆演示车辆已沿外围双向车道循环行驶，约28.8km/h，支持平滑转弯和跨层连续。当前预览使用 http://127.0.0.1:4175/ 。修复、实际采样、测试与重建见 docs/traffic-review-v12.md 和 checks/comparison-v12.html；v11记录保留为历史验证。

## 直接运行

在本目录启动已有生产构建，无需安装npm依赖：

```sh
python3 -m http.server 4174 --bind 127.0.0.1 --directory app/dist
```

浏览器打开 http://127.0.0.1:4174/ 。必须通过HTTP服务加载，不能双击HTML。端口已被当前预览占用时，使用其他空闲端口。

开发或重新编译网页：

```sh
cd app
npm ci --legacy-peer-deps --no-audit --no-fund --cache ../work/npm-cache
npm test
npm run build
npm run dev
```

已验证工具链：Node 20.20.2、npm 10.8.2、Blender 5.2.2 LTS；Vue、Three.js与Vite版本在package-lock.json中锁定。依赖安装需要npm registry；现有生产构建不引用CDN、远程字体或在线模型。

## 规划、生成与重建

唯一规划入口为 planning/project.json。几何、坐标、相机、业务值、单位、状态与对象身份从这里派生；不要直接修改GLB、blend、runtime.json或dist。规划变更后须同时重建模型与网页配置，网页会核对规划哈希和实际模型SHA-256，防止版本混用。

从全新输出目录验证完整重建：

```sh
python3 scripts/rebuild.py --dest work/my-fresh-build --cache work/npm-cache --blender /Applications/Blender.app/Contents/MacOS/Blender --report checks/my-rebuild.json
```

目标目录必须不存在。脚本只复制规划、生成脚本、固定图片与前端源码，重新生成blend、GLB、runtime，安装锁定依赖、运行测试与生产构建，并比对GLB和runtime哈希。当前macOS沙箱内Blender图形初始化可能失败，需要在正常本机终端运行。其他系统可用 --blender 指定已安装的Blender可执行文件。

单独生成流程，从本目录运行：

```sh
python3 scripts/prepare_runtime.py
/Applications/Blender.app/Contents/MacOS/Blender -b --python scripts/build_scene.py
/Applications/Blender.app/Contents/MacOS/Blender -b --python scripts/build_city.py
python3 scripts/verify_city.py --report checks/my-city-assets.json
python3 scripts/verify_assets.py --report checks/my-assets-contract.json
npm --prefix app run build
```

--gray 只用于简化模型构图测试，会切换加载清单；正式交付前重新执行完整模型生成。历史scene-gray与manifest-gray保留作构图过程资料，正式页面只加载build-info.json指定的细化campus.glb。

已确认概念图、无数据整屏稿和幕墙材质是固定输入。相同提示词不能保证生成相同图片，重建直接复用锁定文件及哈希，不要求生图服务或API密钥。AI调用、提示词和来源见 design/concepts/、design/screens/generation-requests-v1.json 与 design/material-generation-v1.json、design/foliage-generation-v1.json。幕墙使用内置image_gen生成的表面图集，窗内画面和反射是材质细节，不是可下钻室内空间或实时室内灯光。

## 评审入口与交付目录

- checks/comparison-v11-final.html：两层AI整屏基准与实际网页并排，记录差异、原因、修改与复验证据。
- checks/gray-composition-review-v2.md：深化前的相机、锚点与UI占位验证。早期错误截图保留并标明不可作为最终证据。
- docs/production-spec-v11-landscape.md：从规划源派生的当前制作规格。
- docs/verification-v11.md：本轮实际验证、重建结果与未覆盖项。
- assets/scene.blend、app/public/assets/campus.glb、assets/manifest.json：当前模型源、实际网页模型与构建清单。
- scripts/、app/src/、app/tests/：可维护源码与必要契约检查。
- design/：原A/B概念、已确认B两层图片、整屏状态稿、固定材质输入及生成记录。
- docs/B-concept-approval.md：真实用户“可以”对两层B修订概念的确认范围，不冒充最终页面验收。
- state.json：三层v13流程审计，旧完整流程已归档到checks/workflow-v11-history.json；车辆局部修复记录仍在checks/traffic-repair-v12.json。状态记录不认证审美或用户身份。

work/、app/node_modules/、缓存和历史网络参考GIF不进入交付压缩包。依赖许可见 THIRD_PARTY_NOTICES.txt。既有研究文档与图片保留，不据此将虚构场景描述成真实测绘或真实经营数据。

当前浏览器和目标画布的测量只代表本轮执行环境；未测指定展厅硬件、长时连续运行、跨浏览器矩阵、真实接口和设备控制。卸载代码已取消加载/动画/监听并释放几何、材质、纹理及后处理资源；完整卸载后的GPU内存回收未做独立显存分析，不将层级切换稳定性替代此项。
