# A1 烘焙技术样区

此目录是通过Blender MCP实际制作和导出的样区资产，不是设计终稿，也尚未替换主页面资产。

- pilot-baked.blend：必要幕墙、叶簇、AO贴图已打包的工程。
- pilot.glb：含5个烘焙接收对象和独立UV2；AO内嵌，不另加载ao.png。
- ao.png：AO留档与后续制作输入。
- indirect.png：无底色、无直射光的线性间接光网页图，1024×1024、8位；Three.js按NoColorSpace、UV通道1读取。
- manifest.json：实际文件哈希；高精度EXR仅保留在work，不随网页传输。

运行项目根目录HTTP服务后访问checks/bake-pilot-v25.html，可切换实时基线、AO、AO＋间接光。该工具用于技术验证，模型与终稿仍有显著差异，详见docs/bake-pilot-v25.md。
