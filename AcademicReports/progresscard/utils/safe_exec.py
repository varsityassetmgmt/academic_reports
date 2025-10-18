# safe_exec.py (in utils)
def exec_template_script(script_text, context):
    """
    VERY LIMITED execution: provide only `context` and safe helpers.
    The script should mutate `context` dict or return it.
    DO NOT allow importing OS/network/db unless you control scripts.
    """
    safe_globals = {
        "__builtins__": {
            "min": min, "max": max, "sum": sum, "len": len, "float": float, "int": int, "str": str, "sorted": sorted, "round": round,
        }
    }
    local = {"context": context}
    exec(script_text, safe_globals, local)
    # expect script to update local['context'] or return something
    return local.get("context", context)
