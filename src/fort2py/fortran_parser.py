from __future__ import annotations
import re
from pathlib import Path
from typing import List, Optional

from .ir import ProjectIR, Module, Subroutine, Function, Program, Argument, VarDecl, UseStmt


# A light, line-oriented parser for MVP.
# Only supports a safe subset; will raise NotImplementedError for complex forms.
# This is intentional to avoid silent mis-parsing.

_re_comment = re.compile(r"!\s.*$")
_re_ws = re.compile(r"^\s+")
_re_module = re.compile(r"^\s*module\s+(\w+)", re.I)
_re_end_module = re.compile(r"^\s*end\s+module\b", re.I)
_re_subroutine = re.compile(r"^\s*(recursive\s+)?subroutine\s+(\w+)\s*\(([^)]*)\)", re.I)
_re_function = re.compile(r"^\s*(recursive\s+)?(pure\s+|elemental\s+|)\s*function\s+(\w+)\s*\(([^)]*)\)", re.I)
_re_end_sub = re.compile(r"^\s*end\s+subroutine\b", re.I)
_re_end_fun = re.compile(r"^\s*end\s+function\b", re.I)
_re_program = re.compile(r"^\s*program\s+(\w+)", re.I)
_re_end_program = re.compile(r"^\s*end\s+program\b", re.I)
_re_use = re.compile(r"^\s*use\s+(\w+)(\s*,\s*only\s*:\s*(.*))?", re.I)
_re_implicit_none = re.compile(r"^\s*implicit\s+none", re.I)
_re_decl = re.compile(
    r"^\s*(real|integer|logical|character)\s*(\(\s*kind\s*=\s*(\w+)\s*\))?(\s*,\s*(.*))?\s*::\s*(.*)$",
    re.I,
)
_re_attr_intent = re.compile(r"intent\s*\(\s*(in|out|inout)\s*\)", re.I)
_re_attr_optional = re.compile(r"\boptional\b", re.I)
_re_attr_alloc = re.compile(r"\ballocatable\b", re.I)
_re_attr_ptr = re.compile(r"\bpointer\b", re.I)
_re_attr_save = re.compile(r"\bsave\b", re.I)
_re_dims = re.compile(r"\(([^)]*)\)")
_re_contains = re.compile(r"^\s*contains\b", re.I)


def strip_comment(line: str) -> str:
    return _re_comment.sub("", line).rstrip()


def parse_args(arglist: str) -> List[Argument]:
    args: List[Argument] = []
    tokens = [a.strip() for a in arglist.split(",")] if arglist.strip() else []
    for t in tokens:
        if not t:
            continue
        # Intents/etc. are in separate declarations; MVP stores names here.
        args.append(Argument(name=t))
    return args


def parse_use(line: str) -> Optional[UseStmt]:
    m = _re_use.match(line)
    if not m:
        return None
    mod = m.group(1)
    only = m.group(3)
    only_list = [x.strip() for x in only.split(",")] if only else None
    return UseStmt(module=mod, only_list=only_list)


def parse_decl(line: str) -> Optional[List[VarDecl]]:
    m = _re_decl.match(line)
    if not m:
        return None
    type_spec = m.group(1).lower()
    kindtok = m.group(3)
    kind = None
    if kindtok:
        try:
            kind = int(kindtok)
        except ValueError:
            # Could be selected_real_kind or a named kind parameter; unsupported in MVP
            raise NotImplementedError(f"Non-literal kind not supported in MVP: {kindtok}")

    attrs = m.group(5) or ""
    names = m.group(6)
    intent = None
    if _re_attr_intent.search(attrs):
        intent = _re_attr_intent.search(attrs).group(1).lower()
    optional = _re_attr_optional.search(attrs) is not None
    alloc = _re_attr_alloc.search(attrs) is not None
    ptr = _re_attr_ptr.search(attrs) is not None
    save = _re_attr_save.search(attrs) is not None

    decls: List[VarDecl] = []
    for raw in names.split(","):
        tok = raw.strip()
        if not tok:
            continue
        nm = tok
        dims = None
        initial = None
        dm = _re_dims.search(tok)
        if dm:
            dimtxt = dm.group(1)
            # Only handle literal extents for MVP
            dims_list = []
            for d in dimtxt.split(","):
                d = d.strip()
                if d == ":":
                    raise NotImplementedError("Assumed-shape arrays require interface; not in MVP")
                try:
                    dims_list.append(int(d))
                except ValueError:
                    raise NotImplementedError(f"Non-literal dimension not supported: {d}")
            dims = tuple(dims_list)
            nm = tok[: tok.find("(")].strip()
        decls.append(
            VarDecl(
                type_spec=type_spec,
                kind=kind,
                name=nm,
                dims=dims,
                intent=intent,  # applies per-line; For per-symbol overrides not in MVP
                optional=optional,
                allocatable=alloc,
                pointer=ptr,
                save=save,
                initial=initial,
            )
        )
    return decls


def parse_file(path: Path, ir: ProjectIR):
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    lines = [strip_comment(l) for l in lines]
    i = 0
    cur_mod: Optional[Module] = None
    cur_sub: Optional[Subroutine] = None
    cur_fun: Optional[Function] = None
    cur_prog: Optional[Program] = None
    in_spec = False

    while i < len(lines):
        line = lines[i]
        i += 1
        if not line.strip():
            continue
        if _re_module.match(line):
            m = _re_module.match(line)
            cur_mod = Module(name=m.group(1), path=path)
            ir.modules[cur_mod.name.lower()] = cur_mod
            in_spec = True
            continue
        if _re_end_module.match(line):
            cur_mod = None
            in_spec = False
            continue
        if _re_program.match(line):
            m = _re_program.match(line)
            cur_prog = Program(name=m.group(1), path=path)
            ir.programs[cur_prog.name.lower()] = cur_prog
            in_spec = True
            continue
        if _re_end_program.match(line):
            cur_prog = None
            in_spec = False
            continue
        if _re_subroutine.match(line):
            m = _re_subroutine.match(line)
            sub = Subroutine(
                name=m.group(2),
                args=parse_args(m.group(3)),
                body=[],
                path=path,
                parent_module=cur_mod.name if cur_mod else None,
                is_recursive=bool(m.group(1)),
            )
            cur_sub = sub
            if cur_mod:
                cur_mod.subroutines.append(sub)
            else:
                # Free subroutine at file scope; unsupported in MVP for module scoping clarity
                raise NotImplementedError("File-scope subroutines (not in a module) not supported in MVP")
            in_spec = True
            continue
        if _re_end_sub.match(line):
            cur_sub = None
            in_spec = False
            continue
        if _re_function.match(line):
            m = _re_function.match(line)
            fun = Function(
                name=m.group(3),
                args=parse_args(m.group(4)),
                return_name=m.group(3),
                body=[],
                path=path,
                parent_module=cur_mod.name if cur_mod else None,
                is_recursive=bool(m.group(1)),
                is_elemental="elemental" in line.lower(),
                is_pure="pure" in line.lower(),
            )
            cur_fun = fun
            if cur_mod:
                cur_mod.functions.append(fun)
            else:
                raise NotImplementedError("File-scope functions (not in a module) not supported in MVP")
            in_spec = True
            continue
        if _re_end_fun.match(line):
            cur_fun = None
            in_spec = False
            continue
        if _re_contains.match(line):
            in_spec = False
            continue
        if _re_use.match(line):
            use = parse_use(line)
            if cur_sub:
                cur_sub.uses.append(use)
            elif cur_fun:
                cur_fun.uses.append(use)
            elif cur_mod:
                cur_mod.uses.append(use)
            elif cur_prog:
                cur_prog.uses.append(use)
            continue
        if _re_implicit_none.match(line):
            # tracked implicitly; semantics phase can verify enforcement
            continue
        decl = parse_decl(line)
        if decl:
            if cur_sub:
                cur_sub.declarations.extend(decl)
            elif cur_fun:
                cur_fun.declarations.extend(decl)
            elif cur_prog:
                cur_prog.declarations.extend(decl)
            else:
                # Top-level declarations at module spec?
                if cur_mod:
                    # For MVP, module variables unsupported (global SAVE). Explicitly fail.
                    raise NotImplementedError("Module variables not supported in MVP to avoid global state.")
                else:
                    raise NotImplementedError("Top-level declarations not tied to module/subroutine unsupported.")
            continue

        # Otherwise, treat as executable line if inside body
        if cur_sub is not None:
            cur_sub.body.append(line)
        elif cur_fun is not None:
            cur_fun.body.append(line)
        elif cur_prog is not None:
            cur_prog.body.append(line)
        else:
            # Non-empty outside any context
            # Accept preprocessor lines silently? Safer to fail for MVP.
            if line.strip().startswith("#"):
                raise NotImplementedError("Preprocessor directives not supported in MVP.")
            raise NotImplementedError(f"Unrecognized or unsupported line outside any scope: {line}")

    return ir


def parse_sources(sources: List[Path]) -> ProjectIR:
    ir = ProjectIR(sources=sources)
    for p in sources:
        parse_file(p, ir)
    return ir
