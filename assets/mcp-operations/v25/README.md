# Blender MCP 制作操作记录

当前调用入口：scripts/blender_mcp_client.py。通过真实MCP stdio连接本机服务，使用其execute_blender_code在Blender中执行；不能在终端直接执行这些代码。`__PROJECT_ROOT__`由客户端替换为当前项目根目录。

已确认方案：先A1、裙房和广场验证AO／间接光，再按终稿扩大范围。规划参数只读planning/project.json → production.bakingPilot。主页面尚未启用样区。

- 初次样区已在MCP内完成几何生成、UV2与准备，prepare.json记录UV2及烘焙准备，当前工程为assets/baking-pilot/v25/pilot-baked.blend；原始调用证据见checks/mcp-model-build-v25.json和checks/mcp-bake-prepare-v25.json。
- AO最终调用ao-clean.json；间接光最终调用indirect-clean.json；export.json保存打包工程并导出GLB。恢复这些操作前应先通过MCP打开对应工程，不能在未知场景运行。
- indirect-recover.json及optimize-web.json是图像缓冲修复和网页转存记录，不是每次都要执行的步骤。
- load-campus/load-city与对应main-export-*用于读取既有主工程，在work临时导出并核对：几何二进制和业务JSON必须相同，只允许忽略已知MCP连接状态。不会覆盖主GLB或工程。
- inspect-current.json只读检查当前工程路径、业务对象与几何数量。

技术样区已核对5个接收对象的UV2与AO绑定。当前模型与终稿仍有幕墙、构图和周边环境差异，不能把调用或导出成功当成整屏还原完成。
