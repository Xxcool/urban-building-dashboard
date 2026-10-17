# 区域制作规格 v13-city

唯一规划SHA-256：b8fc99610edca0cf7251b499cfd0fccb6051d29d31bd30f6ddfffb49e35a63a3

尺寸、相机与湖泊道路均为概念视觉估计，无真实地理对应。区域布局沿用已确认B-city-v1，原8栋规格从同一production.geometryById复用。城市LOD不计入区域楼宇运营总数。

```json
{
  "coordinateBasis": "局部米制视觉估计；Blender XYZ同园区，Three [x,z,-y]；无真实地理对应",
  "seed": 318,
  "extentM": [
    4200,
    3100
  ],
  "outline": [
    [
      -1550,
      -700
    ],
    [
      -1430,
      -970
    ],
    [
      -1120,
      -1040
    ],
    [
      -950,
      -1180
    ],
    [
      -500,
      -1080
    ],
    [
      -230,
      -1190
    ],
    [
      130,
      -1050
    ],
    [
      380,
      -1150
    ],
    [
      800,
      -930
    ],
    [
      1200,
      -880
    ],
    [
      1450,
      -600
    ],
    [
      1570,
      -300
    ],
    [
      1450,
      20
    ],
    [
      1510,
      350
    ],
    [
      1300,
      540
    ],
    [
      980,
      600
    ],
    [
      860,
      850
    ],
    [
      580,
      990
    ],
    [
      250,
      830
    ],
    [
      -50,
      1030
    ],
    [
      -400,
      970
    ],
    [
      -530,
      740
    ],
    [
      -840,
      790
    ],
    [
      -1020,
      520
    ],
    [
      -1390,
      430
    ],
    [
      -1570,
      190
    ],
    [
      -1460,
      -120
    ],
    [
      -1620,
      -390
    ]
  ],
  "lakes": [
    {
      "center": [
        -820,
        1080
      ],
      "radii": [
        980,
        390
      ],
      "phase": 0.3
    },
    {
      "center": [
        380,
        1020
      ],
      "radii": [
        530,
        310
      ],
      "phase": 1.4
    },
    {
      "center": [
        -320,
        390
      ],
      "radii": [
        420,
        230
      ],
      "phase": 0.9
    },
    {
      "center": [
        -250,
        -650
      ],
      "radii": [
        470,
        220
      ],
      "phase": 1.8
    },
    {
      "center": [
        1180,
        -1180
      ],
      "radii": [
        820,
        280
      ],
      "phase": 0.7
    }
  ],
  "roads": {
    "widthM": 20,
    "spacingM": 260,
    "rotationDeg": -9,
    "originM": [
      50,
      20
    ],
    "laneMarkM": 2
  },
  "campusPositionM": [
    430,
    -120,
    0
  ],
  "campusScale": 1,
  "poi": [
    {
      "id": "PARK-DEMO",
      "label": "光谷示范园区",
      "position": [
        430,
        -120,
        120
      ],
      "action": "enter-campus"
    },
    {
      "id": "INDUSTRY-DEMO",
      "label": "产业楼宇",
      "position": [
        -880,
        170,
        85
      ],
      "action": null
    },
    {
      "id": "SERVICE-DEMO",
      "label": "配套服务",
      "position": [
        1220,
        -440,
        70
      ],
      "action": null
    }
  ],
  "camera": {
    "eye": [
      1100,
      -2720,
      2800
    ],
    "target": [
      0,
      0,
      0
    ],
    "fov": 42,
    "near": 3,
    "far": 15000
  },
  "layoutAnchors": {
    "regionFillWidthRange": [
      0.72,
      0.98
    ],
    "regionFillHeightRange": [
      0.55,
      0.9
    ],
    "campusWithinSceneXRange": [
      0.45,
      0.8
    ],
    "campusWithinSceneYRange": [
      0.35,
      0.75
    ]
  },
  "assets": {
    "scene": "app/public/assets/city.glb",
    "grayScene": "app/public/assets/city-gray.glb",
    "blend": "assets/city.blend"
  },
  "budget": {
    "glbMegabytes": 8,
    "triangles": 200000,
    "drawCalls": 90
  },
  "buildings": {
    "gridM": 54,
    "jitterM": 9,
    "widthM": [
      18,
      34
    ],
    "depthM": [
      18,
      34
    ],
    "heightM": [
      12,
      66
    ]
  },
  "trees": {
    "count": 6000,
    "heightM": [
      14,
      24
    ],
    "radiusM": [
      7,
      11
    ]
  },
  "palette": {
    "ground": "#e5e2d3",
    "grass": "#a8b897",
    "water": "#8bc5d8",
    "road": "#b1b6b2",
    "marking": "#f5f3e9",
    "building": "#e4e8e5",
    "buildingWarm": "#dce1da",
    "roof": "#d4dcd7",
    "trunk": "#867c63",
    "leaf": "#789567",
    "leafLight": "#92a77a",
    "boundary": "#208b96",
    "boundaryRim": "#effdfb",
    "campus": "#d3b171",
    "glass": "#7299a9",
    "bronze": "#a88655"
  },
  "render": {
    "background": "#e6ede8",
    "exposure": 0.95,
    "sunIntensity": 2.5,
    "hemisphereIntensity": 1.2,
    "shadowMapSize": 2048,
    "pixelRatioCap": 1.6
  },
  "grayGate": "简化区域边界、水系、8栋园区和3个锚点先网页核对；通过后再生成城市楼群与景观，不将简化模型当定稿"
}
```

画布1920×1080，左28%面板、右72%场景。简化构图门槛checks/city-gray-gate-v3.md在细化前完成；锚点与区域轮廓实际投影见city-gray-target-v3.json。后续仅增加装饰楼群、树冠与材质，未改变通过的相机和主要锚点。无数据态园区入口保持可用，指标只读取demoDesign.campus；缺失值不归零。

资产：独立city.glb，园区/楼宇共用campus.glb；所有脚本和版本由构建清单核对。初版9.59MB及第二版8.26MB超预算，已优化道路平面及树冠共享顶点；当前实际体积和三角形见city-assets-contract-v13.json。
