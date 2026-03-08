"""
StructureClaw Core - 结构分析引擎
基于 OpenSees 和 Pynite 的有限元分析引擎
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import logging

from fem.static_analysis import StaticAnalyzer
from fem.dynamic_analysis import DynamicAnalyzer
from fem.seismic_analysis import SeismicAnalyzer
from design.concrete import ConcreteDesigner
from design.steel import SteelDesigner
from design.code_check import CodeChecker

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="StructureClaw Analysis Engine",
    description="建筑结构有限元分析引擎",
    version="0.1.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ 数据模型 ============

class Node(BaseModel):
    id: str
    x: float
    y: float
    z: float
    restraints: Optional[List[bool]] = None  # [ux, uy, uz, rx, ry, rz]


class Element(BaseModel):
    id: str
    type: str  # beam, truss, shell, solid
    nodes: List[str]
    material: str
    section: str


class Material(BaseModel):
    id: str
    name: str
    E: float  # 弹性模量 (MPa)
    nu: float  # 泊松比
    rho: float  # 密度 (kg/m³)
    fy: Optional[float] = None  # 屈服强度 (MPa)


class Section(BaseModel):
    id: str
    name: str
    type: str
    properties: Dict[str, Any]


class StructuralModel(BaseModel):
    nodes: List[Node]
    elements: List[Element]
    materials: List[Material]
    sections: List[Section]


class LoadCase(BaseModel):
    name: str
    type: str  # dead, live, wind, seismic
    loads: List[Dict[str, Any]]


class AnalysisRequest(BaseModel):
    type: str  # static, dynamic, seismic, nonlinear
    model: StructuralModel
    parameters: Dict[str, Any]


class CodeCheckRequest(BaseModel):
    model_id: str
    code: str  # GB50010, GB50017, etc.
    elements: List[str]


# ============ API 端点 ============

@app.get("/")
async def root():
    """服务状态"""
    return {
        "name": "StructureClaw Analysis Engine",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


@app.post("/analyze")
async def analyze(request: AnalysisRequest):
    """
    执行结构分析
    """
    try:
        logger.info(f"Starting {request.type} analysis")

        if request.type == "static":
            analyzer = StaticAnalyzer(request.model)
            result = analyzer.run(request.parameters)

        elif request.type == "dynamic":
            analyzer = DynamicAnalyzer(request.model)
            result = analyzer.run(request.parameters)

        elif request.type == "seismic":
            analyzer = SeismicAnalyzer(request.model)
            result = analyzer.run(request.parameters)

        elif request.type == "nonlinear":
            analyzer = StaticAnalyzer(request.model)
            result = analyzer.run_nonlinear(request.parameters)

        else:
            raise HTTPException(status_code=400, detail=f"Unknown analysis type: {request.type}")

        logger.info(f"Analysis completed successfully")
        return result

    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/code-check")
async def code_check(request: CodeCheckRequest):
    """
    规范校核
    """
    try:
        checker = CodeChecker(request.code)
        result = checker.check(request.model_id, request.elements)
        return result

    except Exception as e:
        logger.error(f"Code check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/design/beam")
async def design_beam(params: Dict[str, Any]):
    """
    梁截面设计
    """
    try:
        designer = ConcreteDesigner()
        result = designer.design_beam(params)
        return result

    except Exception as e:
        logger.error(f"Beam design failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/design/column")
async def design_column(params: Dict[str, Any]):
    """
    柱截面设计
    """
    try:
        designer = ConcreteDesigner()
        result = designer.design_column(params)
        return result

    except Exception as e:
        logger.error(f"Column design failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ 启动服务 ============

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
