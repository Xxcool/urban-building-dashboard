# 当前城市制作规格

唯一规划SHA-256：15616177c7084908378f3be02d0cdb0c39490084f7fa99b4a021f4b981b46769

唯一视觉终稿：../design/final/city.png，用户确认见../design/final/approval.md。

v26已按唯一终稿重新标注边界、南部完整水系、道路与园区控制点，经Blender MCP制作并烘焙地面AO；重标控制点不等于写实程度已通过视觉验收。湖泊、路网与坐标均为虚构概念，不是测绘资料。

城市独立使用city.glb；园区和楼宇共用campus.glb，业务楼宇身份与指标仍从唯一规划读取。后续先验证新终稿下的投影、区域包含关系与界面占位，再深化材质与建筑。

```json
{
  "coordinateBasis": "局部米制视觉估计；Blender XYZ同园区，Three [x,z,-y]；无真实地理对应",
  "seed": 318,
  "extentM": [
    4200,
    3100
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
  "campusScale": 1.35,
  "poi": [
    {
      "id": "PARK-DEMO",
      "label": "光谷示范园区",
      "action": "enter-campus",
      "heightM": 120,
      "content": {
        "eyebrow": "园区配套",
        "description": "展示服务园区的公共配套方向，具体设施位置与服务能力待真实资料接入后核定。"
      }
    },
    {
      "id": "INDUSTRY-DEMO",
      "label": "产业楼宇",
      "action": "show-info",
      "heightM": 85,
      "content": {
        "eyebrow": "产业空间",
        "description": "围绕示范园区组织的产业楼宇展示，点击园区可进一步查看逐栋空间与入驻指标。"
      }
    },
    {
      "id": "SERVICE-DEMO",
      "label": "配套服务",
      "action": "show-info",
      "heightM": 70,
      "content": {
        "eyebrow": "园区配套",
        "description": "展示服务园区的公共配套方向，具体设施位置与服务能力待真实资料接入后核定。"
      }
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
    "near": 20,
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
    "glbMegabytes": 25,
    "triangles": 550000,
    "drawCalls": 130
  },
  "buildings": {
    "gridM": 72,
    "jitterM": 9,
    "widthM": [
      30,
      52
    ],
    "depthM": [
      35,
      65
    ],
    "heightM": [
      20,
      85
    ],
    "blockRows": 2,
    "blockColumns": 3,
    "pitchM": 64,
    "lakeBufferM": 22
  },
  "trees": {
    "count": 7200,
    "heightM": [
      15,
      30
    ],
    "radiusM": [
      12,
      21
    ]
  },
  "palette": {
    "ground": "#b9cba2",
    "grass": "#b1c69b",
    "water": "#3c96b5",
    "road": "#8e9b9d",
    "marking": "#f5f3e9",
    "building": "#d5dddb",
    "buildingWarm": "#ede3cf",
    "roof": "#aebec4",
    "trunk": "#867c63",
    "leaf": "#638246",
    "leafLight": "#91a868",
    "boundary": "#208b96",
    "boundaryRim": "#effdfb",
    "campus": "#d3b171",
    "glass": "#7299a9",
    "bronze": "#a88655",
    "waterDeep": "#2b809f",
    "shore": "#bacb9d",
    "zoneGreen": "#aec19a",
    "zoneCyan": "#a6ccc7",
    "zoneGold": "#dfc38e"
  },
  "render": {
    "background": "#e6ede8",
    "exposure": 1.05,
    "sunIntensity": 3.6,
    "hemisphereIntensity": 0.48,
    "shadowMapSize": 4096,
    "pixelRatioCap": 1.6,
    "bloom": {
      "strength": 0.85,
      "radius": 0.18,
      "threshold": 0.4
    },
    "ambientOcclusion": {
      "radius": 7,
      "thickness": 4,
      "scale": 0.75,
      "samples": 4,
      "resolutionScale": 0.45,
      "blendIntensity": 0.35
    }
  },
  "grayGate": "简化区域边界、水系、8栋园区和3个锚点先网页核对；通过后再生成城市楼群与景观，不将简化模型当定稿",
  "alignment": {
    "imageSize": [
      1672,
      941
    ],
    "generator": "scripts/city_layout.py",
    "generatorSha256": "60f1f6cfd13fe07c2a9f31c6f54276e49afd54d30f49c17ca8e97a28de0b0c57",
    "outlinePixels": [
      [
        500,
        405
      ],
      [
        535,
        375
      ],
      [
        590,
        355
      ],
      [
        640,
        334
      ],
      [
        690,
        315
      ],
      [
        735,
        300
      ],
      [
        785,
        280
      ],
      [
        816,
        257
      ],
      [
        825,
        230
      ],
      [
        838,
        209
      ],
      [
        854,
        193
      ],
      [
        859,
        177
      ],
      [
        890,
        167
      ],
      [
        915,
        171
      ],
      [
        940,
        181
      ],
      [
        972,
        185
      ],
      [
        1008,
        196
      ],
      [
        1030,
        220
      ],
      [
        1080,
        233
      ],
      [
        1125,
        239
      ],
      [
        1150,
        260
      ],
      [
        1165,
        293
      ],
      [
        1210,
        320
      ],
      [
        1250,
        345
      ],
      [
        1260,
        370
      ],
      [
        1325,
        398
      ],
      [
        1360,
        425
      ],
      [
        1410,
        450
      ],
      [
        1450,
        470
      ],
      [
        1480,
        490
      ],
      [
        1540,
        505
      ],
      [
        1580,
        530
      ],
      [
        1620,
        550
      ],
      [
        1610,
        600
      ],
      [
        1620,
        650
      ],
      [
        1580,
        675
      ],
      [
        1565,
        710
      ],
      [
        1505,
        736
      ],
      [
        1485,
        775
      ],
      [
        1435,
        796
      ],
      [
        1420,
        820
      ],
      [
        1375,
        844
      ],
      [
        1320,
        850
      ],
      [
        1250,
        840
      ],
      [
        1190,
        831
      ],
      [
        1130,
        802
      ],
      [
        1080,
        792
      ],
      [
        1030,
        769
      ],
      [
        1000,
        745
      ],
      [
        960,
        730
      ],
      [
        930,
        712
      ],
      [
        891,
        693
      ],
      [
        840,
        687
      ],
      [
        797,
        664
      ],
      [
        760,
        640
      ],
      [
        720,
        624
      ],
      [
        687,
        612
      ],
      [
        675,
        586
      ],
      [
        687,
        550
      ],
      [
        697,
        525
      ],
      [
        680,
        510
      ],
      [
        652,
        505
      ],
      [
        620,
        497
      ],
      [
        603,
        475
      ],
      [
        580,
        466
      ],
      [
        554,
        449
      ],
      [
        530,
        441
      ],
      [
        510,
        430
      ]
    ],
    "waterPixels": [
      [
        [
          350,
          -200
        ],
        [
          900,
          -200
        ],
        [
          935,
          10
        ],
        [
          905,
          44
        ],
        [
          862,
          89
        ],
        [
          886,
          129
        ],
        [
          842,
          154
        ],
        [
          833,
          196
        ],
        [
          798,
          232
        ],
        [
          713,
          258
        ],
        [
          659,
          244
        ],
        [
          646,
          212
        ],
        [
          570,
          215
        ],
        [
          526,
          184
        ],
        [
          350,
          193
        ]
      ],
      [
        [
          1000,
          -80
        ],
        [
          1280,
          -80
        ],
        [
          1300,
          78
        ],
        [
          1393,
          81
        ],
        [
          1450,
          145
        ],
        [
          1422,
          201
        ],
        [
          1356,
          220
        ],
        [
          1318,
          196
        ],
        [
          1200,
          175
        ],
        [
          1153,
          199
        ],
        [
          1060,
          175
        ],
        [
          1027,
          127
        ],
        [
          1001,
          102
        ]
      ],
      [
        [
          922,
          237
        ],
        [
          971,
          234
        ],
        [
          1001,
          260
        ],
        [
          1060,
          267
        ],
        [
          1090,
          296
        ],
        [
          1044,
          315
        ],
        [
          1014,
          348
        ],
        [
          948,
          350
        ],
        [
          911,
          321
        ],
        [
          917,
          282
        ]
      ],
      [
        [
          813,
          575
        ],
        [
          870,
          570
        ],
        [
          920,
          591
        ],
        [
          978,
          600
        ],
        [
          1003,
          633
        ],
        [
          997,
          665
        ],
        [
          949,
          679
        ],
        [
          904,
          674
        ],
        [
          865,
          666
        ],
        [
          820,
          647
        ],
        [
          800,
          623
        ]
      ],
      [
        [
          1499,
          358
        ],
        [
          1750,
          355
        ],
        [
          1850,
          490
        ],
        [
          1620,
          489
        ],
        [
          1563,
          440
        ],
        [
          1541,
          395
        ]
      ],
      [
        [
          1486,
          714
        ],
        [
          1553,
          692
        ],
        [
          1850,
          699
        ],
        [
          1850,
          855
        ],
        [
          1574,
          820
        ],
        [
          1522,
          780
        ]
      ],
      [
        [
          980,
          630
        ],
        [
          1030,
          640
        ],
        [
          1074,
          648
        ],
        [
          1095,
          671
        ],
        [
          1165,
          655
        ],
        [
          1240,
          679
        ],
        [
          1335,
          697
        ],
        [
          1400,
          743
        ],
        [
          1373,
          782
        ],
        [
          1321,
          807
        ],
        [
          1240,
          807
        ],
        [
          1193,
          790
        ],
        [
          1120,
          778
        ],
        [
          1071,
          741
        ],
        [
          1034,
          719
        ],
        [
          1010,
          689
        ],
        [
          987,
          670
        ]
      ]
    ],
    "zones": [
      {
        "id": "REGION-TINT",
        "material": "zoneGreen",
        "pixels": [
          [
            490,
            392
          ],
          [
            735,
            287
          ],
          [
            896,
            154
          ],
          [
            1046,
            177
          ],
          [
            1263,
            281
          ],
          [
            1434,
            418
          ],
          [
            1628,
            539
          ],
          [
            1582,
            671
          ],
          [
            1251,
            826
          ],
          [
            881,
            714
          ],
          [
            679,
            592
          ],
          [
            568,
            478
          ]
        ]
      },
      {
        "id": "CYAN-SECTOR",
        "material": "zoneCyan",
        "pixels": [
          [
            850,
            201
          ],
          [
            955,
            163
          ],
          [
            1045,
            189
          ],
          [
            1165,
            243
          ],
          [
            1260,
            297
          ],
          [
            1332,
            377
          ],
          [
            1392,
            420
          ],
          [
            1340,
            477
          ],
          [
            1210,
            405
          ],
          [
            1035,
            403
          ],
          [
            956,
            320
          ],
          [
            877,
            287
          ]
        ]
      },
      {
        "id": "DEMO-SECTOR",
        "material": "zoneGold",
        "pixels": [
          [
            1035,
            403
          ],
          [
            1210,
            405
          ],
          [
            1358,
            490
          ],
          [
            1398,
            591
          ],
          [
            1276,
            679
          ],
          [
            1120,
            621
          ],
          [
            1010,
            559
          ],
          [
            956,
            469
          ]
        ]
      }
    ],
    "islands": [
      [
        554,
        114,
        45,
        16
      ],
      [
        637,
        91,
        37,
        14
      ],
      [
        717,
        147,
        48,
        19
      ],
      [
        801,
        119,
        23,
        14
      ],
      [
        751,
        67,
        37,
        12
      ],
      [
        858,
        67,
        22,
        9
      ],
      [
        944,
        287,
        18,
        10
      ],
      [
        992,
        301,
        22,
        9
      ],
      [
        1080,
        714,
        18,
        10
      ],
      [
        1208,
        749,
        25,
        12
      ],
      [
        1534,
        737,
        26,
        11
      ],
      [
        1650,
        752,
        39,
        20
      ],
      [
        1292,
        752,
        14,
        8
      ]
    ],
    "roads": [
      {
        "pixels": [
          [
            350,
            390
          ],
          [
            660,
            302
          ],
          [
            900,
            240
          ],
          [
            1090,
            250
          ],
          [
            1300,
            310
          ],
          [
            1740,
            460
          ]
        ],
        "width": 28
      },
      {
        "pixels": [
          [
            500,
            1030
          ],
          [
            720,
            620
          ],
          [
            870,
            450
          ],
          [
            990,
            220
          ],
          [
            1060,
            -120
          ]
        ],
        "width": 28,
        "bridge": true
      },
      {
        "pixels": [
          [
            450,
            470
          ],
          [
            900,
            520
          ],
          [
            1190,
            610
          ],
          [
            1470,
            715
          ],
          [
            1760,
            800
          ]
        ],
        "width": 24
      },
      {
        "pixels": [
          [
            990,
            1030
          ],
          [
            1120,
            800
          ],
          [
            1280,
            540
          ],
          [
            1450,
            300
          ],
          [
            1580,
            40
          ]
        ],
        "width": 26,
        "bridge": true
      },
      {
        "pixels": [
          [
            480,
            720
          ],
          [
            780,
            800
          ],
          [
            1060,
            920
          ],
          [
            1690,
            1000
          ]
        ],
        "width": 28
      }
    ],
    "campusPixel": [
      1082,
      520
    ],
    "poiPixels": {
      "PARK-DEMO": [
        1152,
        430
      ],
      "INDUSTRY-DEMO": [
        818,
        346
      ],
      "SERVICE-DEMO": [
        1440,
        540
      ]
    },
    "containedWaterIndices": [
      3,
      6
    ],
    "buildingGridPx": [
      64,
      68
    ],
    "greenPixels": [
      [
        [
          701,
          555
        ],
        [
          810,
          561
        ],
        [
          1030,
          640
        ],
        [
          1030,
          710
        ],
        [
          880,
          701
        ],
        [
          730,
          630
        ]
      ],
      [
        [
          1005,
          661
        ],
        [
          1090,
          653
        ],
        [
          1350,
          702
        ],
        [
          1428,
          756
        ],
        [
          1355,
          807
        ],
        [
          1155,
          786
        ],
        [
          1010,
          733
        ]
      ],
      [
        [
          525,
          376
        ],
        [
          675,
          332
        ],
        [
          752,
          361
        ],
        [
          735,
          418
        ],
        [
          630,
          466
        ],
        [
          528,
          434
        ]
      ],
      [
        [
          819,
          332
        ],
        [
          950,
          316
        ],
        [
          1070,
          365
        ],
        [
          1015,
          432
        ],
        [
          874,
          400
        ]
      ],
      [
        [
          889,
          163
        ],
        [
          1027,
          169
        ],
        [
          1081,
          217
        ],
        [
          970,
          245
        ],
        [
          884,
          220
        ]
      ],
      [
        [
          552,
          676
        ],
        [
          673,
          700
        ],
        [
          733,
          765
        ],
        [
          660,
          839
        ],
        [
          522,
          810
        ]
      ]
    ],
    "localRoadPixels": [
      [
        [
          470,
          490
        ],
        [
          650,
          450
        ],
        [
          870,
          460
        ],
        [
          1035,
          403
        ]
      ],
      [
        [
          710,
          670
        ],
        [
          838,
          560
        ],
        [
          920,
          488
        ]
      ],
      [
        [
          920,
          488
        ],
        [
          956,
          400
        ],
        [
          1070,
          365
        ],
        [
          1250,
          309
        ]
      ],
      [
        [
          866,
          428
        ],
        [
          760,
          385
        ],
        [
          650,
          305
        ]
      ],
      [
        [
          1160,
          566
        ],
        [
          1210,
          405
        ],
        [
          1332,
          377
        ],
        [
          1410,
          351
        ]
      ],
      [
        [
          1280,
          563
        ],
        [
          1435,
          555
        ],
        [
          1600,
          570
        ]
      ],
      [
        [
          1134,
          805
        ],
        [
          1040,
          780
        ],
        [
          945,
          730
        ],
        [
          710,
          670
        ]
      ],
      [
        [
          1490,
          681
        ],
        [
          1560,
          620
        ],
        [
          1600,
          570
        ]
      ]
    ],
    "designTarget": {
      "path": "design/final/city.png",
      "sha256": "9dd4553d0742a27cd7934201aa6949cdd014b652fe35e2b999451cf439aa593a",
      "decisionId": "D024"
    },
    "calibrationStatus": "final-v26-control-points",
    "coordinateProvenance": "从唯一城市终稿重新标注边界、南部完整水系、主路和示范园区锚点，平面反投影仍为示范制作估计"
  },
  "geometryBudgetReason": "用户指出v13明显未还原设计；扩展连续城市覆盖并增加自然岸线、岛屿、分组楼宇与叶簇。预算随实际场景范围重新制定，仍须实测。",
  "boundary": {
    "bloomMix": 0.28,
    "layers": [
      {
        "radius": 30,
        "color": "#2aa7c1",
        "opacity": 0.025,
        "order": 1
      },
      {
        "radius": 20,
        "color": "#2aa7c1",
        "opacity": 0.045,
        "order": 2
      },
      {
        "radius": 11,
        "color": "#46bdd0",
        "opacity": 0.1,
        "order": 3
      },
      {
        "radius": 4.4,
        "color": "#e7ffff",
        "opacity": 0.95,
        "order": 4
      },
      {
        "radius": 2.6,
        "color": "#078eac",
        "opacity": 1,
        "order": 5
      },
      {
        "radius": 3.1,
        "color": "#4fd6e6",
        "opacity": 0.7,
        "emission": 1.5,
        "glow": true,
        "order": 4
      }
    ]
  },
  "context": {
    "radiusM": 13000,
    "districtPitchM": 1250,
    "buildingsPerDistrict": 6,
    "seed": 20201017,
    "fogNearDistanceFactor": 1.5,
    "fogDepthM": 11000,
    "innerRadiusM": 1800,
    "middleRadiusM": 6000,
    "middleBuildingsPerDistrict": 24,
    "middleTreesPerDistrict": 12
  },
  "restoration": {
    "version": "v26",
    "windowBandSpacingM": 4.8,
    "glassPalette": [
      "#8daab7",
      "#b3c6cb",
      "#d4dedc"
    ],
    "shoreGrassContrast": 0.8,
    "scope": "按城市终稿增加建筑立面层次；不引入真实地理数据"
  },
  "bakedLighting": {
    "enabled": true,
    "aoStrength": 0.65,
    "aoResolution": 2048,
    "aoSamples": 8,
    "aoDistanceM": 55,
    "marginPx": 12,
    "uvChannel": 1,
    "receivers": [
      "regional_terrain_zoneGreen",
      "regional_terrain_zoneCyan",
      "regional_terrain_zoneGold",
      "regional_terrain_grass",
      "regional_terrain_shore",
      "regional_campus_campus"
    ],
    "scope": "静态区域地表AO；水面、边界、车辆不烘入"
  },
  "restorationV27": {
    "foliageCardsPerTree": 3,
    "atlasKinds": [
      "green",
      "gold",
      "camphor"
    ],
    "goldRatio": 0.12,
    "trunkHeightRatio": 0.38,
    "crownCenterHeightRatio": 0.67,
    "crownHeightRatio": 0.75,
    "seed": 2718,
    "understoryCount": 2400,
    "understoryHeightM": [
      10,
      19
    ],
    "understoryRadiusM": [
      9,
      16
    ],
    "terrainTextureSize": 256,
    "terrainTextureRepeatM": 900,
    "terrainVariation": 0.065
  }
}
```
