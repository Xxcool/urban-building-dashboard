# 制作阶段待办复验 v11

本文件更新历史production-open-items.md的后续结果，不修改历史证据。

- P-01：先完成简化模型相机与UI占位检查（checks/gray-composition-review-v2.md），之后以v9构图修订、v11最终两层实际截图和assets-contract-v11.json复验。八根节点、同一A1、3+21总24层、三级退台与标签绑定明确；工程模型不能从AI视觉数层推断。
- P-02：八栋实体网格拾取均通过，见checks/mesh-picking-v11-final.json；叶簇在独立渲染层，不参与楼宇射线拾取。
- P-03：当前环境1920×1080同实例12轮切换已测，见checks/runtime-verification-v11-verified.json；104几何、17纹理保持稳定，末次P95为32.4ms。未测试指定展厅硬件和长时运行，不承诺该范围。

制作规格见production-spec-v11-landscape.md，实际模型assets/scene.blend与app/public/assets/campus.glb；材料输入和提示词在design/。最终视觉差异及全部验证见verification-v11.md与checks/comparison-v11-final.html。用户概念确认不作为最终工程验收。
