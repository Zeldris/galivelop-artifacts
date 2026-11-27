"""Run a consumer repo's tests/test_schema.py with its schema module replaced by gart.schema.
usage: python3 -I harness.py <repo> <pkg> <module-name-in-pkg> [--own]   (repo = absolute path)
Output: one line per non-passing test: STATUS<TAB>id<TAB>first line of the cause; then a summary line."""
import importlib, sys, types, unittest

repo, pkg, mod = sys.argv[1:4]
own = "--own" in sys.argv or "--diff" in sys.argv
diff = "--diff" in sys.argv  # DIFFERENTIAL: run the copy itself, but compare every validate/check_schema call with gart
diag = "--diag" in sys.argv   # DIAGNOSTIC ONLY: unmask hidden differences (see notes)
GART = "/home/user/galivelop-artifacts"
sys.path[:0] = [repo, GART]

class MissingAPI(Exception):
    pass

if not own:
    from gart import schema as G
    shim = types.ModuleType(f"{pkg}.{mod}")
    for k, v in vars(G).items():
        if not k.startswith("__"):
            setattr(shim, k, v)
    def missing(name):
        def stub(*a, **k):
            raise MissingAPI(f"missing API: {name}")
        stub.__name__ = name
        return stub
    if pkg == "opportunity_intel":
        # ALIAS 1: oi SchemaFailure.keyword == gart ValidationError.code (rename of the field only)
        class SchemaFailure:
            __slots__ = ("path", "keyword", "params")
            def __init__(s, path, keyword, params=None):
                s.path, s.keyword, s.params = path, keyword, params or {}
            def __iter__(s):
                return iter((s.path, s.keyword, s.params))
            def message(s, lang="en"):
                raise MissingAPI("missing API: SchemaFailure.message (i18n)")
        # ALIAS 2: validate returns gart's errors wrapped in the renamed record (no value change)
        def validate(value, schema):
            return [SchemaFailure(e.path, e.code, e.params) for e in G.validate(value, schema)]
        shim.SchemaFailure = SchemaFailure
        shim.validate = validate
        # ALIAS 3: oi SchemaError subclasses ValueError, gart's subclasses Exception -> NOT aliased (behaviour)
        # STUBS (missing in gart): KEYWORDS, ValidationError(exception), check, load_schema
        shim.KEYWORDS = G.ANNOTATIONS | G.VALIDATING   # ALIAS 4: oi KEYWORDS (all accepted keys) = gart ANNOTATIONS|VALIDATING
        shim.ValidationError = type("ValidationError", (ValueError,), {"__init__": lambda s, *a, **k: (_ for _ in ()).throw(MissingAPI("missing API: ValidationError"))})
        shim.check = missing("check")
        shim.load_schema = missing("load_schema")
    else:
        # STUBS only, they raise MissingAPI when called (never emulate): format_error, load_schema, (gdev) load_def/load_grammar
        for n in ("format_error", "load_schema", "load_def", "load_grammar"):
            setattr(shim, n, missing(n))
        shim.__getattr__ = lambda n: (_ for _ in ()).throw(AttributeError(f"missing API: {n}"))
    importlib.import_module(pkg)
    if diag:
        import importlib.util
        spec = importlib.util.spec_from_file_location("_orig_schema", f"{repo}/{pkg}/{mod}.py", submodule_search_locations=None)
        orig = importlib.util.module_from_spec(spec); orig.__package__ = pkg
        sys.modules["_orig_schema"] = orig; spec.loader.exec_module(orig)
        if pkg == "opportunity_intel":
            def _oi_path(ptr, inst):
                out, node = "$", inst
                for t in ([] if ptr == "" else ptr[1:].split("/")):
                    t = t.replace("~1", "/").replace("~0", "~")
                    if isinstance(node, list):
                        out += f"[{t}]"; node = node[int(t)]
                    else:
                        out += f".{t}"; node = node.get(t) if isinstance(node, dict) else None
                return out
            _ren = {"required": {"name": "property"}, "additionalProperties": {"name": "property"}}
            def validate(value, schema):  # DIAG: path converted to oi format, params renamed where gart names differ
                return [SchemaFailure(_oi_path(e.path, value), e.code,
                        {_ren.get(e.code, {}).get(k, k): v for k, v in e.params.items()}) for e in G.validate(value, schema)]
            shim.validate = validate
        else:
            for n in ("format_error", "load_schema", "load_def", "load_grammar", "_SCHEMAS", "_loaded", "_error"):
                if hasattr(orig, n): setattr(shim, n, getattr(orig, n))
            shim.__getattr__ = lambda n: (_ for _ in ()).throw(AttributeError(f"missing API: {n}"))
    sys.modules[f"{pkg}.{mod}"] = shim
    setattr(sys.modules[pkg], mod, shim)

DIVS = []
if diff:
    import json
    from gart import schema as G
    om = importlib.import_module(f"{pkg}.{mod}")
    def caller():
        f = sys._getframe(2)
        while f:
            if f.f_code.co_filename.endswith("tests/test_schema.py"):
                return f"{f.f_code.co_name}:{f.f_lineno}"
            f = f.f_back
        return "?(indirect)"
    def short(x): return json.dumps(x, default=str, sort_keys=True)[:200]
    oi = pkg == "opportunity_intel"
    def norm_own(errs):
        return [(e.path, e.keyword if oi else e.code) for e in errs] if True else None
    def oi_path(ptr, inst):
        out, node = "$", inst
        for t in ([] if ptr == "" else ptr[1:].split("/")):
            t = t.replace("~1", "/").replace("~0", "~")
            if isinstance(node, list): out += f"[{t}]"; node = node[int(t)]
            else: out += f".{t}"; node = node.get(t) if isinstance(node, dict) else None
        return out
    ov, oc = om.validate, om.check_schema
    def validate(inst, sch):
        try: mine = ov(inst, sch); mine_exc = None
        except Exception as e: mine, mine_exc = None, e
        try: g = G.validate(inst, sch); gexc = None
        except G.SchemaError as e: g, gexc = None, e
        if mine_exc is None and gexc is not None:
            DIVS.append((caller(), "gart-SchemaError-but-copy-ok", short(sch), str(gexc)[:120]))
        elif mine_exc is not None and gexc is None:
            DIVS.append((caller(), "copy-raises-gart-validates", short(sch), f"{type(mine_exc).__name__}: {str(mine_exc)[:80]}; gart={[tuple(e[:2]) for e in g]}"))
        elif mine_exc is None:
            a = [(e.path, e.keyword if oi else e.code) for e in mine]
            b = [(oi_path(e.path, inst) if oi else e.path, e.code) for e in g]
            if sorted(a) != sorted(b):
                kind = "gart-LOOSER" if len(b) < len(a) and set(b) <= set(a) else ("gart-stricter" if len(b) > len(a) and set(a) <= set(b) else "differs")
                DIVS.append((caller(), kind, f"inst={short(inst)} sch={short(sch)}", f"copy={a} gart={b}"))
            else:
                pa = [dict(e.params) if not oi else dict(e.params) for e in mine]
                pb = [e.params for e in g]
                if [sorted(x) for x in pa] != [sorted(x) for x in pb] and False: pass
                ka = sorted((tuple(sorted(x.keys())) for x in pa)); kb = sorted((tuple(sorted(x.keys())) for x in pb))
                if ka == kb and not oi and sorted(map(short, pa)) != sorted(map(short, pb)):
                    DIVS.append((caller(), "param-values", f"inst={short(inst)} sch={short(sch)}", f"copy={pa} gart={pb}"))
                if ka != kb:
                    DIVS.append((caller(), "param-names", f"inst={short(inst)} sch={short(sch)}", f"copy={ka} gart={kb}"))
        if mine_exc: raise mine_exc
        return mine
    def check_schema(sch, *a, **k):
        try: oc(sch, *a, **k); mexc = None
        except Exception as e: mexc = e
        try: G.check_schema(sch); gexc = None
        except G.SchemaError as e: gexc = e
        if (mexc is None) != (gexc is None):
            DIVS.append((caller(), "check_schema-copy-" + ("ok" if mexc is None else "rejects") + "-gart-" + ("rejects" if gexc else "ok"), short(sch), f"copy={mexc!s:.90} gart={gexc!s:.90}"))
        if mexc: raise mexc
    om.validate, om.check_schema = validate, check_schema

suite = unittest.defaultTestLoader.loadTestsFromName("tests.test_schema")
class R(unittest.TextTestResult):
    rows = []
    def _row(s, st, t, err):
        lines = [l for l in s._exc_info_to_string(err, t).strip().splitlines()]
        s.rows.append((st, t.id(), " | ".join(lines[-3:])[:400]))
    def addFailure(s, t, e): super().addFailure(t, e); s._row("FAIL", t, e)
    def addError(s, t, e): super().addError(t, e); s._row("ERROR", t, e)
    def addSubTest(s, t, sub, e):
        super().addSubTest(t, sub, e)
        if e: s._row("SUBFAIL" if e[0] and issubclass(e[0], AssertionError) else "SUBERROR", sub, e)
import os
res = unittest.TextTestRunner(resultclass=R, stream=open(os.devnull, "w")).run(suite)
for st, i, m in R.rows:
    print(f"{st}\t{i}\t{m}")
seen = set()
for d in DIVS:
    if d in seen: continue
    seen.add(d); print("DIV\t" + "\t".join(d))
print(f"SUMMARY run={res.testsRun} failures={len(res.failures)} errors={len(res.errors)} subtest-failures={len([r for r in R.rows if r[0].startswith('SUB')])}")
