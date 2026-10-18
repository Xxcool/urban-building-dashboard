# 制作规格 v1

由 scripts/render_specs.py 从 planning/project.json 派生。规划SHA-256：7a8d612858f99aba501f336ed27804ee63e2cde071c771ac849329a417e4a3a6。

尺寸依据：全部为虚构示范的制作估计，不是实测；由同一几何解释两层投影，网页构图不通过则改源。坐标约定：{"unit": "m", "blender": "X向右、Y向园区后排、Z向上，原点为园区地面中心", "threeConversion": "[x,y,z] -> [x,z,-y]，GLB默认Y向上导出", "modelOrigin": [0, 0, 0]}。

## 对象参数

| 稳定ID | 制作参数 |
| --- | --- |
| A1 | `{"position": [-95, 70, 0], "podiumSizes": [[70, 58], [62, 50], [54, 42]], "towerSize": [30, 36], "towerOffset": [0, 5], "bronzeFace": "positiveX"}` |
| B1 | `{"position": [8, 78, 0], "size": [43, 34, 72]}` |
| B2 | `{"position": [112, 76, 0], "size": [43, 34, 65]}` |
| A2 | `{"position": [-147, -5, 0], "size": [59, 43, 18]}` |
| B3 | `{"position": [148, -5, 0], "size": [59, 43, 18]}` |
| C1 | `{"position": [-112, -98, 0], "size": [62, 44, 18]}` |
| C2 | `{"position": [0, -100, 0], "size": [62, 44, 18]}` |
| C3 | `{"position": [112, -98, 0], "size": [62, 44, 18]}` |

A1层数只读demoDesign.focusBuilding.floorsDefinition；层高为3.6m。其他建筑高度仅是视觉建模估计，不转写为未定义业务指标。

## 相机与构图

{
  "campus": {
    "type": "perspective",
    "eye": [
      310,
      -470,
      350
    ],
    "target": [
      0,
      0,
      22
    ],
    "fov": 32,
    "near": 0.5,
    "far": 2200
  },
  "building": {
    "type": "perspective",
    "eye": [
      36,
      -86,
      100
    ],
    "target": [
      -95,
      70,
      42
    ],
    "fov": 30,
    "near": 0.2,
    "far": 1800
  }
}

UI占位与安全边界：{"railFraction": 0.28, "sceneFraction": 0.72, "paddingPx": 40, "kpiColumns": 2, "baseViewport": "project.viewport", "safeBottomPx": 28}。网页目标1920×1080与缩小视口，核对八栋ID、A1全高、UI占位、标签与已知锚点；灰盒未通过前不深化。

初始相机是待校准估计，不能宣称已拟合AI图。以同一空间锚点验证两层，无法同时解释时修订制作估计；改变已确认视觉方向则重新确认。灰盒只作构图检查，不作概念稿或最终模型交付。

## 资产、材质与性能

{
  "scene": "app/public/assets/campus.glb",
  "sourceBlend": "assets/scene.blend",
  "grayScene": "app/public/assets/campus-gray.glb",
  "businessNodePrefix": "building_",
  "loading": "单包一次加载，两层复用，同一业务根节点下按材质合批；不复制全场景"
}

渲染配置：{"lighting": "中性日光，环境反射与单主光；静态几何不烘入动态状态", "sunPosition": [-160, -120, 280], "exposure": 1.05, "shadowMapSize": 2048, "maxPixelRatio": 1.6, "fogNear": 650, "fogFar": 1900, "baking": "本版不烘焙，先验证实时材质；如测得收益再评估静态光照贴图"}。

预算：{"status": "待实测目标，非承诺目标硬件结果", "triangles": 500000, "drawCalls": 350, "glbMegabytes": 25, "frameTimeP95Ms": 40, "resourceCycles": 12}。实际浏览器另记录draw calls、三角形、帧时间、重复进入退出和资源释放。未测目标硬件或长时运行不报通过。

## 生成与复验

规划源 → scripts/build_scene.py --gray → 简化GLB/网页构图证据 → 改源复验 → scripts/build_scene.py → .blend、GLB → 网页材质/绑定检查 → 正式面板与场景联动。脚本指定输出目录，记录版本与哈希；禁止修补GLB和模型。两层共用模型与业务ID映射，标签、拾取和面板读取同一状态。

每层每版保存设计/实际对照，注明版本、视口、相机和状态；先处理构图与几何，再处理材质、UI、数据和交互。未通过项保留ID、原因假设、源修改、重建产物和下一步。
