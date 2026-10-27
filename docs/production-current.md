# 制作规格 v27-final-polish

由 scripts/render_specs.py 从 planning/project.json 派生。规划SHA-256：952b7727eaa7496f30b67cc3f7b7e637c871cfc8eb2cbec42408a568823e1651。

尺寸依据：全部为虚构示范的制作估计，不是实测；由同一几何解释两层投影，网页构图不通过则改源。坐标约定：{"unit": "m", "blender": "X向右、Y向园区后排、Z向上，原点为园区地面中心", "threeConversion": "[x,y,z] -> [x,z,-y]，GLB默认Y向上导出", "modelOrigin": [0, 0, 0]}。

## 对象参数

| 稳定ID | 制作参数 |
| --- | --- |
| A1 | `{"position": [-125, 70, 0], "podiumSizes": [[70, 58], [62, 50], [54, 42]], "towerSize": [36, 40], "towerOffset": [0, 5], "bronzeFace": "positiveX", "podiumFloorHeightM": 7.2, "towerFloorHeightM": 3.8}` |
| B1 | `{"position": [-6, 78, 0], "size": [43, 34, 84]}` |
| B2 | `{"position": [104, 76, 0], "size": [43, 34, 76]}` |
| A2 | `{"position": [-147, -5, 0], "size": [59, 43, 21]}` |
| B3 | `{"position": [170, -5, 0], "size": [59, 43, 21]}` |
| C1 | `{"position": [-50, -98, 0], "size": [62, 44, 21]}` |
| C2 | `{"position": [55, -100, 0], "size": [62, 44, 21]}` |
| C3 | `{"position": [160, -98, 0], "size": [62, 44, 21]}` |

A1层数只读demoDesign.focusBuilding.floorsDefinition；裙房层高7.2m，塔楼层高3.8m。其他建筑高度仅是视觉建模估计，不转写为未定义业务指标。

## 相机与构图

{
  "campus": {
    "type": "perspective",
    "eye": [
      200,
      -440,
      340
    ],
    "target": [
      8,
      0,
      24
    ],
    "fov": 36,
    "near": 2,
    "far": 2200
  },
  "building": {
    "type": "perspective",
    "eye": [
      10,
      -225,
      48
    ],
    "target": [
      -112,
      70,
      49
    ],
    "fov": 26.8,
    "near": 2,
    "far": 1800
  }
}

UI占位与安全边界：{"railFraction": 0.28, "sceneFraction": 0.72, "paddingPx": 40, "kpiColumns": 2, "baseViewport": "project.viewport", "safeBottomPx": 28}。先在实际网页按三张终稿验证相机、空间锚点和UI占位，再深化；现有坐标仅为待校准制作估计，不冒充已匹配终稿。

初始相机是待校准估计，不能宣称已拟合AI图。以同一空间锚点验证两层，无法同时解释时修订制作估计；改变已确认视觉方向则重新确认。灰盒只作构图检查，不作概念稿或最终模型交付。

## 资产、材质与性能

{
  "scene": "public/assets/campus.glb",
  "sourceBlend": "assets/scene.blend",
  "grayScene": "public/assets/campus-gray.glb",
  "businessNodePrefix": "building_",
  "loading": "单包一次加载，两层复用，同一业务根节点下按材质合批；不复制全场景"
}

渲染配置：{"lighting": "中性日光，环境反射与单主光；静态几何不烘入动态状态", "sunPosition": [-180, -220, 240], "exposure": 1.1, "shadowMapSize": 2048, "maxPixelRatio": 1.6, "fogNear": 1000, "fogFar": 2400, "baking": "v27：园区静态地面完整色彩/阴影烘焙，建筑与设施保留AO/间接光，玻璃与动态对象实时渲染", "hemisphereIntensity": 0.5, "sunIntensity": 3.6, "environmentIntensity": 0.75, "selectionStyle": "由同一制作规格派生轻量轮廓线与标签，不执行全场景多次描边渲染", "ambientOcclusion": {"radius": 3, "thickness": 2, "scale": 0.65, "blendIntensity": 0.3, "samples": 8}, "shadowUpdate": "静态几何与光源在模型载入后更新一次，巡览与数据模式不修改阴影", "skyTopRgb": [80, 154, 222], "skyHorizonRgb": [156, 209, 241], "transmissionResolutionScale": 0.5, "fillLight": {"positionM": [180, -100, 160], "color": "#ffe9c4", "intensity": 1.4, "purpose": "补充金属竖梃和窗后空间的柔和暖色侧光，不叠加地面阴影"}}。

预算：{"status": "待实测目标，非承诺目标硬件结果", "triangles": 500000, "drawCalls": 350, "glbMegabytes": 25, "frameTimeP95Ms": 40, "resourceCycles": 12}。实际浏览器另记录draw calls、三角形、帧时间、重复进入退出和资源释放。未测目标硬件或长时运行不报通过。

## 生成与复验

规划源 + 三张唯一终稿 → Blender MCP修改并保存工程 → MCP制作UV、AO/间接光并导出GLB → 核对后发布资产 → 从规划派生runtime → 实际浏览器同相机对照。MCP操作记录在assets/mcp-operations/v26；不使用终端Blender生成器，不手改GLB。两层共用模型与业务ID映射，标签、拾取和面板读取同一状态。

每层每版保存设计/实际对照，注明版本、视口、相机和状态；先处理构图与几何，再处理材质、UI、数据和交互。未通过项保留ID、原因假设、源修改、重建产物和下一步。
