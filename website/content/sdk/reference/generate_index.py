import os

# This script is used to generate the index.mdx files for the sdk reference
# section of the docs Copy paste the output of the
# .txt file into the section it generates relative to the index.mdx file

# get the file names of all the files in a given relative path
files_sdk = os.listdir(os.path.join(os.getcwd()))
print(files_sdk)

# remove last entry in a list cause it is not needed
files_sdk.pop()

print(files_sdk)


# create discord reference card
with open(os.path.join(os.getcwd(), "sdk.txt"), "w") as f:
    for x in files_sdk:
        desc_text = []
        # if x is index.mdx or index.md then skip
        if x == "index.md" or x == "index.mdx" or x == "generate_index.py":
            pass
        else:
            try:
                description = os.listdir(os.path.join(os.getcwd(), x))
                for xx in description:
                    if (
                        xx == "index.md"
                        or xx == "index.mdx"
                        or xx == "generate_index.py"
                    ):
                        pass
                    else:
                        desc_text.append(os.path.splitext(xx)[0])
                f.write(
                    '<ReferenceCard title="{}" description="{}" url="/sdk/reference/{}" />\n'.format(
                        x, ", ".join(desc_text), x
                    )
                )
            except Exception as ex:
                print(ex)
                print("must be md file not in a folder - so adding a ref card")
                f.write(
                    '<ReferenceCard title="{}" description="{}" url="/sdk/reference/{}" />\n'.format(
                        x, x, x
                    )
                )
