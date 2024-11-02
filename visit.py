import libcst
from mypy import api as mypy_api
from libcst_mypy import MypyTypeInferenceProvider
from pathlib import Path
import importlib
import sys
import logging
import argparse

logger = logging.getLogger(__name__)

def class_module_from_fqdn(s: str) -> str:
    p = s.split('.')
    m = p[:-1]
    c = p[-1]
    return ('.'.join(m), c)

class FunctionCallCollector(libcst.CSTVisitor):
    METADATA_DEPENDENCIES = (libcst.metadata.PositionProvider,MypyTypeInferenceProvider)

    def visit_Call(self, node: libcst.Call) -> None:
        # Collect each call and its position
        logger.info("=NODE ========================================")
        code = (
            libcst.Module([]).code_for_node(node).replace("\n", "").replace(",", "")
        )
        logger.debug(node)
        logger.warning(f"code = {code}")
        pos = self.get_metadata(libcst.metadata.PositionProvider, node)
        logger.debug(f"position metadata = {pos}")
        try:
            mypy_type = self.get_metadata(MypyTypeInferenceProvider, node.func.value)
        except KeyError:
            logger.warning(f"mypy type = None for '{node.func.value}'")
            return

        # What comes out of mypy? Note that printing this invokes this [1] and it's not a string.
        # [1] https://github.com/Kludex/libcst-mypy/blob/14e0901a784e5ec96f70211bca70400f535d42a1/libcst_mypy/utils.py#L46
        logger.debug(f"mypy type = {mypy_type}")
        # What things exist on this beyond a normal object?
        logger.debug(f"mypy type dir = {[e for e in dir(mypy_type) if not e.startswith('__')]}")
        # What's the full name? Since this includes the path, it can be used to
        # infer things since "service" or "model" could be in the path.
        logger.debug(f"mypy type fulln = {mypy_type.fullname}")
        # Examine the type of the metadata.
        logger.debug(f"mypy type mypy_type = {mypy_type.mypy_type}")
        logger.debug(f"mypy type class = {mypy_type.__class__}")
        logger.debug(f"mypy type of mypy_type = {type(mypy_type)}")

        # Let's look for parent class
        if True:
            # Import the module and find the class there. So we'll need the module and class
            (mypy_type_module_name, mypy_type_class_name) = class_module_from_fqdn(mypy_type.fullname)
            logger.debug(f"mypy_type module name {mypy_type_module_name}")
            logger.debug(f"mypy_type class name {mypy_type_class_name}")

            mypy_type_module = importlib.import_module(mypy_type_module_name)
            logger.debug(f"mypy_type module {sys.modules[mypy_type_module_name]}")
            logger.debug(f"mypy_type module {dir(sys.modules[mypy_type_module_name])}")
            logger.debug(f"mypy_type attr {getattr(sys.modules[mypy_type_module_name], mypy_type_class_name)}")

            # Reach in to the module for the class (not fqdn) by name
            mypy_type_klass = getattr(sys.modules[mypy_type_module_name], mypy_type_class_name)
            logger.debug(f"mypy_type attr {mypy_type_klass}")
            if mypy_type_klass:
                # Stringify the base class names.
                parents = ['.'.join([c.__module__, c.__name__]) for c in mypy_type_klass.__bases__]
                logger.debug(f"mypy_type attr bases {parents}")
                logger.warning(f"This call '{code}' calls a '{mypy_type.fullname}' which inherits from {parents} with {[f"{arg.star} {arg.value.value}" for arg in node.args]}")

            # Nah, let the GC do it's thing
            # del(mypy_type_module)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--rollback", action="store_true", help="Rollback to origin/main"
    )
    parser.add_argument(
        "-v", "--verbose", action="count", default=0, help="Log debug info"
    )
    args = parser.parse_args()

    if args.verbose > 1:
        logging.basicConfig(level=logging.DEBUG)
    elif args.verbose > 0:
        logging.basicConfig(level=logging.INFO)

    logger.info(f"args: {args}")

    logger.info("==============================================")
    source_path = Path(__file__).parent / "fake_django" / "code.py"
    file = str(source_path)
    repo_root = Path(__file__).parent
    cache = MypyTypeInferenceProvider.gen_cache(repo_root, [file])
    wrapper = libcst.MetadataWrapper(
        libcst.parse_module(source_path.read_text()),
        cache={MypyTypeInferenceProvider: cache[file]},
    )

    logger.debug("----------------------------------------------")
    logger.debug("-CACHE ---------------------------------------")
    logger.debug(cache)
    logger.debug("-MYPY NODES-----------------------------------")
    mypy_nodes = wrapper.resolve(MypyTypeInferenceProvider)
    logger.debug(mypy_nodes)
    logger.debug("----------------------------------------------")
    visitor = FunctionCallCollector()
    wrapper.visit(visitor)
