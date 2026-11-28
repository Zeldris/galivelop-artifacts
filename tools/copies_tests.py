"""Runs the test suite of each copy of the validator twice: as it is, and with gart's `check_schema` and `validate`.

Manual tool, like `copies_probe.py`: it needs the clones of the copies (two are private repos), so tests never import
it. The swap is a `sitecustomize` on `PYTHONPATH` with an import hook, so it also reaches the subprocesses the copies'
tests start. When the copy's schema module is imported, the hook replaces its `check_schema` and `validate` with
adapters over gart: same exception class and error type as the copy (for oi, `SchemaFailure` with `$.a[0]` paths), so
only behaviour differences fail. `load_schema`, `format_error` and the rest stay the copy's, and call the adapters.
Run (repo root):

    python3 -I tools/copies_tests.py --copy gdev=/path/galivelop-developer --copy oi=/path/galivelop-client-catcher \
        --copy gimg=/path/galivelop-image-generator --copy gvoice=/path/galivelop-voice-generator [--json]

It prints, per copy, the tests that fail only with gart (failures that already fail without it are left out).
"""
import json, os, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor

MODS = {"gdev": "gdev.schema", "oi": "opportunity_intel.schema", "gimg": "gimg.schema", "gvoice": "gvoice.schema"}
GART_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SITECUSTOMIZE = r'''
import importlib.abc, importlib.util, os, sys

_MOD, _ROOT = os.environ["GART_SWAP_MOD"], os.environ["GART_SWAP_ROOT"]


def _gart():
    sys.path.insert(0, _ROOT)
    try:
        import gart.schema as g
    finally:
        sys.path.remove(_ROOT)
    return g


def _oi_path(pointer):
    out = "$"
    for tok in pointer.split("/")[1:]:
        tok = tok.replace("~1", "/").replace("~0", "~")
        out += f"[{tok}]" if tok.isdigit() else f".{tok}"
    return out


def _patch(m):
    g = _gart()
    oi = hasattr(m, "SchemaFailure")

    def check_schema(schema, *args, **kwargs):
        try:
            g.check_schema(schema)
        except g.SchemaError as e:
            raise m.SchemaError(str(e)) from e

    def validate(instance, schema, *args, **kwargs):
        check_schema(schema)
        errs = g.validate(instance, schema)
        if oi:
            return [m.SchemaFailure(_oi_path(e.path), e.code, dict(e.params)) for e in errs]
        return [m.ValidationError(e.path, e.code, dict(e.params)) for e in errs]

    m.check_schema, m.validate = check_schema, validate
    m.__gart_swapped__ = True


class _Loader(importlib.abc.Loader):
    def __init__(self, inner):
        self.inner = inner

    def create_module(self, spec):
        return self.inner.create_module(spec)

    def exec_module(self, module):
        self.inner.exec_module(module)
        _patch(module)


class _Finder(importlib.abc.MetaPathFinder):
    def find_spec(self, name, path, target=None):
        if name != _MOD:
            return None
        sys.meta_path.remove(self)
        try:
            spec = importlib.util.find_spec(name)
        finally:
            sys.meta_path.insert(0, self)
        if spec is not None:
            spec.loader = _Loader(spec.loader)
        return spec


sys.meta_path.insert(0, _Finder())
'''

RUNNER = r'''
import json, sys, unittest
suite = unittest.defaultTestLoader.discover("tests", top_level_dir=".")
res = unittest.TextTestRunner(stream=open("/dev/null", "w"), verbosity=0).run(suite)
def why(tb):
    lines = tb.strip().splitlines()
    start = next((i for i, l in enumerate(lines) if l[:1].isalpha() and "Error" in l.split(":")[0]), len(lines) - 1)
    return "\n".join(lines[start:start + 12])[:1500]
bad = {t.id(): why(tb) for t, tb in res.failures + res.errors}
swapped = getattr(sys.modules.get(sys.argv[1]), "__gart_swapped__", False)
print(json.dumps({"ran": res.testsRun, "skipped": len(res.skipped), "bad": bad, "swapped": swapped}))
'''


def run(root, mod, swap, hookdir):
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    if swap:
        env.update(PYTHONPATH=hookdir, GART_SWAP_MOD=mod, GART_SWAP_ROOT=GART_ROOT)
    p = subprocess.run([sys.executable, "-c", RUNNER, mod], cwd=root, env=env, capture_output=True, text=True)
    lines = p.stdout.strip().splitlines()
    if not lines:
        raise SystemExit(f"{root}: the runner printed nothing\n{p.stderr[-2000:]}")
    return json.loads(lines[-1])


def main(argv):
    copies = {}
    for i, a in enumerate(argv):
        if a == "--copy":
            if i + 1 >= len(argv):
                raise SystemExit("--copy NAME=PATH")
            name, _, path = argv[i + 1].partition("=")
            if name not in MODS or not path:
                raise SystemExit("--copy NAME=PATH with NAME in " + ", ".join(MODS))
            copies[name] = path
    if not copies:
        raise SystemExit("give at least one --copy NAME=PATH (" + ", ".join(MODS) + ")")
    with tempfile.TemporaryDirectory() as hookdir:
        with open(os.path.join(hookdir, "sitecustomize.py"), "w") as f:
            f.write(SITECUSTOMIZE)
        jobs = [(n, s) for n in copies for s in (False, True)]
        with ThreadPoolExecutor(len(jobs)) as ex:
            out = dict(zip(jobs, ex.map(lambda j: run(copies[j[0]], MODS[j[0]], j[1], hookdir), jobs)))
    report = {}
    for n in copies:
        base, gart = out[(n, False)], out[(n, True)]
        if not gart["swapped"]:
            raise SystemExit(f"{n}: the swap did not reach {MODS[n]} in the runner")
        only = {k: v for k, v in sorted(gart["bad"].items()) if k not in base["bad"]}
        report[n] = {"ran": gart["ran"], "baseline_failing": len(base["bad"]), "only_with_gart": only}
    if "--json" in argv:
        print(json.dumps(report, indent=1, ensure_ascii=False))
        return
    for n, r in report.items():
        print(f"== {n}: {r['ran']} tests, {r['baseline_failing']} already failing, {len(r['only_with_gart'])} only with gart")
        for k, v in r["only_with_gart"].items():
            print(f"  {k}\n      " + v.replace("\n", "\n      "))


if __name__ == "__main__":
    main(sys.argv[1:])
