import libcst
from mypy import api as mypy_api
from libcst_mypy import MypyTypeInferenceProvider
from pathlib import Path
import importlib
import sys
import logging
import argparse

logger = logging.getLogger(__name__)

class FunctionCallCollector(libcst.CSTVisitor):
    METADATA_DEPENDENCIES = (libcst.metadata.PositionProvider, MypyTypeInferenceProvider)

    def __init__(self, fname: str):
        self.fname = fname

    def visit_Call(self, node: libcst.Call) -> None:
        # Collect each call and its position
        logger.debug("= NODE =======================================")
        logger.debug(node)

        # Create a 1 line string version of the code.
        code = libcst.Module([]).code_for_node(node).replace("\n", "").replace(",", "")

        logger.debug(f"code = {code}")
        pos = self.get_metadata(libcst.metadata.PositionProvider, node)
        logger.debug(f"position = {pos}")

        try:
            mypy_type = self.get_metadata(MypyTypeInferenceProvider, node.func.value)
        except KeyError:
            logger.warning(f"Call at {self.fname}#L{pos.start.line}:{pos.start.column}, '{code}' has no type signature")
            return

        ################################
        ## All of this is just to get an idea of what comes out of libcst-mypy.
        ## This code does nothing useful, only gives some insight into what's what.
        if True:
            logger.debug("----------------------------------------------")
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
        # Import the module and find the class there. So we'll need the module and class
        logger.debug("----------------------------------------------")
        module_name, class_name = mypy_type.fullname.rsplit('.', 1)
        logger.debug(f"mypy_type module name {module_name}")
        logger.debug(f"mypy_type class name {class_name}")

        mypy_type_module = importlib.import_module(module_name)
        logger.debug(f"mypy_type module {sys.modules[module_name]}")
        logger.debug(f"mypy_type module dir {dir(sys.modules[module_name])}")

        # Reach in to the module for the class (not fqdn) by name
        mypy_type_klass = getattr(sys.modules[module_name], class_name)
        logger.debug(f"mypy_type getattr {mypy_type_klass}")
        if mypy_type_klass:
            # Stringify the base class names.
            parents = ['.'.join([c.__module__, c.__name__]) for c in mypy_type_klass.__bases__]
            logger.debug(f"mypy_type attr bases {parents}")
            logger.warning(f"Call at {self.fname}#L{pos.start.line}:{pos.start.column}, '{code}' calls a '{mypy_type.fullname}' which inherits from {parents} with arguments {[f"{arg.star}{arg.value.value}" for arg in node.args]}")
            # Our sample lint; no **kwargs to db models
            if 'fake_django.bases.BaseModel' in parents and any([arg.star == '**' for arg in node.args]):
                logger.error(f"Call at {self.fname}#L{pos.start.line}:{pos.start.column}, '{code}' calls a BaseModel with **kwargs")

        # Nah, let the GC do it's thing
        # del(mypy_type_module)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "-v", "--verbose", action="count", default=0, help="Log debug info"
    )
    parser.add_argument(
        "paths",
        action="append",
        type=str,
        help="Paths to files to process",
        nargs="*",
    )
    args = parser.parse_args()

    if args.verbose > 1:
        logging.basicConfig(level=logging.DEBUG)
    elif args.verbose > 0:
        logging.basicConfig(level=logging.INFO)

    logger.info(f"args: {args}")

    for fname in args.paths[0]:
        root = Path(__file__).parent
        path = root / fname
        logger.debug(f"root = {root}")
        logger.debug(f"file = {path}")
        cache = MypyTypeInferenceProvider.gen_cache(root, [str(path)])
        wrapper = libcst.MetadataWrapper(
            libcst.parse_module(path.read_text()),
            cache={MypyTypeInferenceProvider: cache[str(path)]},
        )

        logger.debug("-MYPY CACHE ----------------------------------")
        logger.debug(cache)
        logger.debug("-MYPY NODES-----------------------------------")
        mypy_nodes = wrapper.resolve(MypyTypeInferenceProvider)
        logger.debug(mypy_nodes)
        logger.debug("----------------------------------------------")
        visitor = FunctionCallCollector(fname)
        wrapper.visit(visitor)
