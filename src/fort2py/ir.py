from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Tuple, Literal, Any


Intent = Literal["in", "out", "inout"]


@dataclass
class UseStmt:
    module: str
    only_list: Optional[List[str]] = None


@dataclass
class VarDecl:
    type_spec: str  # "real", "integer", "logical", "character"
    kind: Optional[int]
    name: str
    dims: Optional[Tuple[int, ...]] = None
    intent: Optional[Intent] = None
    optional: bool = False
    allocatable: bool = False
    pointer: bool = False
    save: bool = False
    initial: Optional[Any] = None


@dataclass
class Argument:
    name: str
    intent: Optional[Intent] = None
    optional: bool = False
    byref: bool = False  # For OUT/INOUT scalars, we enforce wrapper
    type_spec: Optional[str] = None
    kind: Optional[int] = None
    dims: Optional[Tuple[int, ...]] = None


@dataclass
class Subroutine:
    name: str
    args: List[Argument]
    body: List[str]  # raw lines for MVP; codegen transforms with context
    declarations: List[VarDecl] = field(default_factory=list)
    uses: List[UseStmt] = field(default_factory=list)
    contains: List[Any] = field(default_factory=list)
    is_recursive: bool = False
    is_elemental: bool = False
    is_pure: bool = False
    parent_module: Optional[str] = None
    path: Optional[Path] = None


@dataclass
class Function:
    name: str
    args: List[Argument]
    return_name: str
    body: List[str]
    declarations: List[VarDecl] = field(default_factory=list)
    uses: List[UseStmt] = field(default_factory=list)
    contains: List[Any] = field(default_factory=list)
    is_recursive: bool = False
    is_elemental: bool = False
    is_pure: bool = False
    return_type: Optional[str] = None
    return_kind: Optional[int] = None
    return_dims: Optional[Tuple[int, ...]] = None
    parent_module: Optional[str] = None
    path: Optional[Path] = None


@dataclass
class DerivedType:
    name: str
    components: List[VarDecl]


@dataclass
class Module:
    name: str
    uses: List[UseStmt] = field(default_factory=list)
    subroutines: List[Subroutine] = field(default_factory=list)
    functions: List[Function] = field(default_factory=list)
    types: List[DerivedType] = field(default_factory=list)
    path: Optional[Path] = None


@dataclass
class Program:
    name: str
    uses: List[UseStmt] = field(default_factory=list)
    body: List[str] = field(default_factory=list)
    declarations: List[VarDecl] = field(default_factory=list)
    path: Optional[Path] = None


@dataclass
class ProjectIR:
    modules: Dict[str, Module] = field(default_factory=dict)
    programs: Dict[str, Program] = field(default_factory=dict)
    sources: List[Path] = field(default_factory=list)
    # Symbol tables, interfaces, etc. can be added as needed
