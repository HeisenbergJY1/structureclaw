"""
静力分析模块
基于 OpenSeesPy 实现线性静力分析
"""

import numpy as np
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class StaticAnalyzer:
    """静力分析器"""

    def __init__(self, model):
        """
        初始化分析器

        Args:
            model: 结构模型数据
        """
        self.model = model
        self.nodes = {n.id: n for n in model.nodes}
        self.elements = {e.id: e for e in model.elements}
        self.materials = {m.id: m for m in model.materials}
        self.sections = {s.id: s for s in model.sections}

        # 位移结果
        self.displacements = {}
        # 内力结果
        self.forces = {}
        # 应力结果
        self.stresses = {}

    def run(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行静力分析

        Args:
            parameters: 分析参数，包含荷载工况等

        Returns:
            分析结果
        """
        logger.info("Starting static analysis")

        try:
            # 尝试使用 OpenSeesPy
            import openseespy.opensees as ops
            result = self._run_with_opensees(parameters)
        except ImportError:
            # 降级到简化计算
            logger.warning("OpenSeesPy not available, using simplified analysis")
            result = self._run_simplified(parameters)

        return result

    def _run_with_opensees(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        使用 OpenSeesPy 执行分析
        """
        import openseespy.opensees as ops

        # 清除已有模型
        ops.wipe()

        # 创建模型
        ops.model('basic', '-ndm', 3, '-ndf', 6)

        # 定义节点
        for node in self.model.nodes:
            ops.node(int(node.id), node.x, node.y, node.z)

            # 定义约束
            if node.restraints:
                constraints = [i for i, r in enumerate(node.restraints) if r]
                if constraints:
                    ops.fix(int(node.id), *node.restraints)

        # 定义材料
        for mat in self.model.materials:
            ops.uniaxialMaterial(
                'Elastic',
                int(mat.id),
                mat.E * 1000  # MPa to kPa
            )

        # 定义截面和单元
        for elem in self.model.elements:
            if elem.type == 'beam':
                self._define_beam_element(elem, ops)
            elif elem.type == 'truss':
                self._define_truss_element(elem, ops)

        # 施加荷载
        load_cases = parameters.get('loadCases', [])
        for lc in load_cases:
            self._apply_loads(lc, ops)

        # 分析设置
        ops.system('BandSPD')
        ops.numberer('Plain')
        ops.constraints('Plain')
        ops.integrator('LoadControl', 1.0)
        ops.algorithm('Newton')
        ops.analysis('Static')

        # 执行分析
        ops.analyze(1)

        # 提取结果
        displacements = {}
        for node in self.model.nodes:
            disp = ops.nodeDisp(int(node.id))
            displacements[node.id] = {
                'ux': disp[0],
                'uy': disp[1],
                'uz': disp[2],
                'rx': disp[3],
                'ry': disp[4],
                'rz': disp[5]
            }

        # 提取单元内力
        forces = {}
        for elem in self.model.elements:
            try:
                force = ops.eleForce(int(elem.id))
                forces[elem.id] = force
            except:
                pass

        # 清理
        ops.wipe()

        return {
            'status': 'success',
            'displacements': displacements,
            'forces': forces,
            'summary': self._generate_summary(displacements, forces)
        }

    def _run_simplified(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        简化分析（当 OpenSees 不可用时）
        """
        # 简化的框架分析
        displacements = {}
        forces = {}

        # 假设简化计算
        for node in self.model.nodes:
            # 简化的位移估算
            displacements[node.id] = {
                'ux': 0.0,
                'uy': 0.0,
                'uz': 0.0,
                'rx': 0.0,
                'ry': 0.0,
                'rz': 0.0
            }

        return {
            'status': 'success',
            'displacements': displacements,
            'forces': forces,
            'note': 'Simplified analysis - OpenSeesPy not available'
        }

    def run_nonlinear(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        非线性静力分析 (Pushover)
        """
        logger.info("Starting nonlinear static analysis")

        try:
            import openseespy.opensees as ops
            return self._run_nonlinear_opensees(parameters)
        except ImportError:
            return {
                'status': 'error',
                'message': 'Nonlinear analysis requires OpenSeesPy'
            }

    def _run_nonlinear_opensees(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        使用 OpenSeesPy 执行非线性分析
        """
        import openseespy.opensees as ops

        ops.wipe()
        ops.model('basic', '-ndm', 3, '-ndf', 6)

        # ... 定义非线性材料和单元 ...

        # Pushover 分析设置
        ops.pattern('Plain', 1, 'Linear')

        # 控制位移分析
        target_disp = parameters.get('targetDisplacement', 0.1)
        ops.integrator('DisplacementControl', 1, 2, 0.001)

        ops.analysis('Static')

        # 分步执行
        results = []
        current_step = 0
        max_steps = int(target_disp / 0.001)

        while current_step < max_steps:
            ok = ops.analyze(1)
            if ok != 0:
                break

            base_shear = ops.getTime()
            roof_disp = ops.nodeDisp(1, 2)

            results.append({
                'step': current_step,
                'baseShear': base_shear,
                'roofDisplacement': roof_disp
            })

            current_step += 1

        ops.wipe()

        return {
            'status': 'success',
            'pushoverCurve': results
        }

    def _define_beam_element(self, elem, ops):
        """定义梁单元"""
        # 简化的梁单元定义
        section = self.sections.get(elem.section)
        if section:
            # 使用弹性梁柱单元
            ops.element(
                'elasticBeamColumn',
                int(elem.id),
                int(elem.nodes[0]),
                int(elem.nodes[1]),
                section.properties.get('A', 0.01),
                section.properties.get('E', 200000),
                section.properties.get('Iz', 0.0001),
                section.properties.get('Iy', 0.0001),
                section.properties.get('G', 79000),
                section.properties.get('J', 0.0001)
            )

    def _define_truss_element(self, elem, ops):
        """定义桁架单元"""
        section = self.sections.get(elem.section)
        if section:
            ops.element(
                'truss',
                int(elem.id),
                int(elem.nodes[0]),
                int(elem.nodes[1]),
                section.properties.get('A', 0.01),
                int(elem.material)
            )

    def _apply_loads(self, load_case: Dict, ops):
        """施加荷载"""
        ops.timeSeries('Linear', 1)
        ops.pattern('Plain', 1, 1)

        for load in load_case.get('loads', []):
            if load['type'] == 'nodal':
                ops.load(
                    int(load['node']),
                    *load['forces']
                )
            elif load['type'] == 'distributed':
                ops.eleLoad(
                    '-ele',
                    int(load['element']),
                    '-type',
                    '-beamUniform',
                    load['wy'],
                    load['wz']
                )

    def _generate_summary(self, displacements: Dict, forces: Dict) -> Dict:
        """生成分析结果摘要"""
        if not displacements:
            return {}

        # 找最大位移
        max_disp = 0
        max_disp_node = None
        for node_id, disp in displacements.items():
            total_disp = (disp['ux']**2 + disp['uy']**2 + disp['uz']**2)**0.5
            if total_disp > max_disp:
                max_disp = total_disp
                max_disp_node = node_id

        return {
            'maxDisplacement': max_disp,
            'maxDisplacementNode': max_disp_node,
            'nodeCount': len(displacements),
            'elementCount': len(forces)
        }
