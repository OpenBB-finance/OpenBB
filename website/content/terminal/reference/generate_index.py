import os

# This script is used to generate the index.mdx files for the terminal
# reference section of the docs Copy paste the output of the
# .txt file into the section it generates relative to the index.mdx file -
# TODO - we need to make Terminal behave like the other 2 menus - so we can use this

# get the file names of all the files in a given relative path
files_terminal = os.listdir(os.path.join(os.getcwd()))
print(files_terminal)

# remove last entry in a list cause it is not needed - category.json file
files_terminal.pop()

print(files_terminal)


# create discord reference card
with open(os.path.join(os.getcwd(), "terminal.txt"), "w") as f:
    for x in files_terminal:
        desc_text = []
        # if x is index.mdx or index.md then skip
        if x == "index.md" or x == "index.mdx" or x == "generate_index.py":
            pass
        else:
            description = os.listdir(os.path.join(os.getcwd(), x))
            for xx in description:
                if (
                    xx == "index.md"
                    or xx == "index.mdx"
                    or xx == "generate_index.py"
                    or xx == "_category_.json"
                ):
                    pass
                else:
                    desc_text.append(os.path.splitext(xx)[0])
            f.write(
                '<ReferenceCard title="{}" description="{}" url="/terminal/reference/{}" />\n'.format(
                    x, ", ".join(desc_text), x
                )
            )
