from inspect import getmembers, isfunction

from openbb_terminal import api
import time


def test_no_bad_parameters():
    pre_modules = []
    for module in dir(api):
        if "module" in str(type(getattr(api, module))):
            pre_modules.append(module)
    modules = [(x, api) for x in pre_modules]
    i = 0
    while len(modules) >= i:
        item, parent = modules[i]
        print(f"{item}: {type(getattr(parent,item))}")
        if str(item)[0] == "_":
            continue
        if "module" in str(type(getattr(parent, item))):
            new_parent = getattr(parent, item)
            if "api" not in str(new_parent):
                continue
            for sub_item in dir(new_parent):
                if str(sub_item)[0] == "_":
                    continue
                print(sub_item)
                if "module" in str(type(getattr(new_parent, sub_item))):
                    modules.append((sub_item, new_parent))
                elif "function" in str(type(getattr(new_parent, sub_item))):
                    print(f"Func: {item}")
        print(i)
        i += 1
        time.sleep(0.5)
