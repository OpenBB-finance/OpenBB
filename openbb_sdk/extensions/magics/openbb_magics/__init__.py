from IPython.core.magic import register_cell_magic, needs_local_scope


def register_todf_magic():
    @register_cell_magic
    def todf(line, cell):

        lines = list(filter(None, cell.split("\n")))
        # Get the nb namespace
        namespace = get_ipython().user_ns

        for nb_line in lines:
            if "=" not in nb_line:
                # If I have a line in a nb that doesnt assign, do nothing.
                # Can check if the last line doesnt assign and then return, but this is just an idea
                continue
            try:
                # if my line is df = obb.stocks.load("AAPL"), we change to evaluate
                # df = {}.to_dataframe()
                to_eval = nb_line.strip().replace(" ", "")
                exec(to_eval + ".to_dataframe()", namespace)
            except Exception:
                # If this is not dataframable or something else goes wrong, lets assign the
                # OBBject.  We can do better handling if desired
                exec(to_eval, namespace)


try:
    # This will only work if we can reach IPython.
    ipython = get_ipython()
    register_todf_magic()
except NameError:
    pass  # Not in IPython environment
