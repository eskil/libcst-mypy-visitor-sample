import libcst
from mypy import api as mypy_api
import json
import subprocess
import tempfile
import os
from libcst_mypy import MypyTypeInferenceProvider
from pathlib import Path
import builtins
import importlib
import sys

def class_module_from_fqdn(s: str) -> str:
    p = s.split('.')
    m = p[:-1]
    c = p[-1]
    return ('.'.join(m), c)

class FunctionCallCollector(libcst.CSTVisitor):
    METADATA_DEPENDENCIES = (libcst.metadata.PositionProvider,MypyTypeInferenceProvider)

    def visit_Call(self, node: libcst.Call) -> None:
        # Collect each call and its position
        print("=NODE ========================================")
        print(node)
        pos = self.get_metadata(libcst.metadata.PositionProvider, node)
        print(f"pos = {pos}")
        try:
            tipo = self.get_metadata(MypyTypeInferenceProvider, node.func.value)
            # What comes out of mypy? Note that printing this invokes this [1] and it's not a string.
            # [1] https://github.com/Kludex/libcst-mypy/blob/14e0901a784e5ec96f70211bca70400f535d42a1/libcst_mypy/utils.py#L46
            print(f"tipo = {tipo}")
            # What things exist on this beyond a normal object?
            print(f"tipo dir = {[e for e in dir(tipo) if not e.startswith('__')]}")
            # What's the full name? Since this includes the path, it can be used to
            # infer things since "service" or "model" could be in the path.
            print(f"tipo fulln = {tipo.fullname}")
            # Examine the type of the metadata.
            print(f"tipo mipitipi = {tipo.mypy_type}")
            print(f"tipo class = {tipo.__class__}")
            print(f"tipo de tipo = {type(tipo)}")

            # makescope
            if True:
                (tipo_module_name, tipo_class_name) = class_module_from_fqdn(tipo.fullname)
                print(f"tipo module name {tipo_module_name}")
                print(f"tipo class name {tipo_class_name}")
                tipo_module = importlib.import_module(tipo_module_name)
                print(f"tipo module {sys.modules[tipo_module_name]}")
                print(f"tipo module {dir(sys.modules[tipo_module_name])}")
                print(f"tipo attr {getattr(sys.modules[tipo_module_name], tipo_class_name)}")
                tipo_klass = getattr(sys.modules[tipo_module_name], tipo_class_name)
                print(f"tipo attr {tipo_klass}")
                if tipo_klass:
                    parents = ['.'.join([c.__module__, c.__name__]) for c in tipo_klass.__bases__]
                    print(f"tipo attr bases {parents}")
                    code = (
                        libcst.Module([]).code_for_node(node).replace("\n", "").replace(",", "")
                    )

                    print(f"This call '{code}' calls a '{tipo.fullname}' which inherits from {parents}")
        except KeyError:
            print(f"tipo = None")
            pass

print("==============================================")
source_path = Path(__file__).parent / "fake_django" / "code.py"
file = str(source_path)
repo_root = Path(__file__).parent
cache = MypyTypeInferenceProvider.gen_cache(repo_root, [file])
wrapper = libcst.MetadataWrapper(
    libcst.parse_module(source_path.read_text()),
    cache={MypyTypeInferenceProvider: cache[file]},
)

print("----------------------------------------------")
print("-CACHE ---------------------------------------")
print(cache)
print("-MYPY NODES-----------------------------------")
mypy_nodes = wrapper.resolve(MypyTypeInferenceProvider)
print(mypy_nodes)
print("----------------------------------------------")
visitor = FunctionCallCollector()
wrapper.visit(visitor)
