# tool_loader.py
import os
import importlib.util
import logging

logger = logging.getLogger("ToolLoader")

def load_tools(tools_dir: str):
    registry = {}

    if not os.path.exists(tools_dir):
        logger.warning(f"Tools directory not found: {tools_dir}")
        os.makedirs(tools_dir, exist_ok=True)
        return registry

    for file in os.listdir(tools_dir):
        if not file.endswith(".py"):
            continue

        path = os.path.join(tools_dir, file)
        mod_name = file[:-3]

        try:
            spec = importlib.util.spec_from_file_location(mod_name, path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            tool_name = getattr(module, "TOOL_NAME", mod_name)
            tool_desc = getattr(module, "TOOL_DESCRIPTION", "")
            tool_schema = getattr(module, "TOOL_INPUT_SCHEMA", {})
            tool_fn = getattr(module, "execute", None)

            if callable(tool_fn):
                registry[tool_name] = {
                    "name": tool_name,
                    "description": tool_desc,
                    "inputSchema": tool_schema,
                    "execute": tool_fn
                }
                logger.info(f"Loaded tool: {tool_name}")
            else:
                logger.warning(f"{file} missing execute()")

        except Exception as e:
            logger.error(f"Failed to load tool {file}: {e}")

    return registry
