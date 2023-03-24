import os

# This script is used to generate the index.mdx files for the reference section of the docs
# it generates relative to the index.mdx file

# get the file names of all the files in a given relative path
files_discord = os.listdir(os.path.join(os.getcwd(), "discord"))

files_telegram = os.listdir(os.path.join(os.getcwd(), "telegram"))

# remove last entry in a list cause it is not needed
files_discord.pop()
files_telegram.pop()
# remove index.md from the list

# create discord reference top level ref card
with open(os.path.join(os.getcwd(), "discord", "index.mdx"), "w") as f:
    f.write(
        '# OpenBB Discord Reference\n\nimport ReferenceCard from "@site/src/components/General/ReferenceCard";\n\n<ul className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 -ml-6"> \n'
    )
    for x in files_discord:
        desc_text = []
        # if x is index.mdx or index.md then skip
        if x == "index.md" or x == "index.mdx":
            pass
        else:
            description = os.listdir(os.path.join(os.getcwd(), "discord", x))
            for xx in description:
                if xx == "index.md" or xx == "index.mdx":
                    pass
                else:
                    desc_text.append(os.path.splitext(xx)[0])

            f.write(
                '<ReferenceCard title="{}" description="{}" url="/bot/reference/discord/{}" />\n'.format(
                    x, ", ".join(desc_text), x
                )
            )
    f.write("</ul>")

# create telegram reference top level ref card
with open(os.path.join(os.getcwd(), "telegram", "index.mdx"), "w") as f:
    f.write(
        '# OpenBB Telegram Reference\n\nimport ReferenceCard from "@site/src/components/General/ReferenceCard";\n\n<ul className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 -ml-6"> \n'
    )
    for x in files_telegram:
        desc_text = []
        # if x is index.mdx or index.md then skip
        if x == "index.md" or x == "index.mdx":
            pass
        else:
            description = os.listdir(os.path.join(os.getcwd(), "telegram", x))
            for xx in description:
                if xx == "index.md" or xx == "index.mdx":
                    pass
                else:
                    desc_text.append(os.path.splitext(xx)[0])
            f.write(
                '<ReferenceCard title="{}" description="{}" url="/bot/reference/telegram/{}" />\n'.format(
                    x, ", ".join(desc_text), x
                )
            )
    f.write("</ul>")


# create submenu discord reference cards
for x in files_discord:
    # if x is index.mdx or index.md then skip
    if x == "index.md" or x == "index.mdx":
        pass
    else:
        print(x)
        desc_text = []
        description = os.listdir(os.path.join(os.getcwd(), "discord", x))
        print(description)
        for xx in description:
            if xx == "index.md" or xx == "index.mdx":
                pass
            else:
                try:
                    with open(os.path.join(os.getcwd(), "discord", x, xx), "r") as f:
                        for line in f:
                            find = "# " + xx.replace(".md", "")
                            if find in line:
                                for line in f:  # now you are at the lines you want
                                    if "\n" in line:
                                        for line in f:
                                            print(line)
                                            top_text = line
                                            break
                                    break
                        # import adfasdf

                    desc_text.append(os.path.splitext(xx)[0] + " | " + top_text)
                except:
                    # Need to handle the ones that are embedded here
                    pass

        with open(os.path.join(os.getcwd(), "discord", x, "index.mdx"), "w") as f:
            f.write(
                '# {}\n\nimport ReferenceCard from "@site/src/components/General/ReferenceCard";\n\n<ul className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 -ml-6"> \n'.format(
                    x
                )
            )
            for w in desc_text:
                f.write(
                    '<ReferenceCard title="{}" description="{}" url="/bot/reference/discord/{}/{}" />\n'.format(
                        w.split("|")[0], w.split("|")[1], x, w.split("|")[0]
                    )
                )
            f.write("</ul>")

# create submenu telegram reference cards
for x in files_telegram:
    # if x is index.mdx or index.md then skip
    if x == "index.md" or x == "index.mdx":
        pass
    else:
        print(x)
        desc_text = []
        description = os.listdir(os.path.join(os.getcwd(), "telegram", x))
        print(description)
        for xx in description:
            if xx == "index.md" or xx == "index.mdx":
                pass
            else:
                try:
                    with open(os.path.join(os.getcwd(), "telegram", x, xx), "r") as f:
                        for line in f:
                            find = "# " + xx.replace(".md", "")
                            if find in line:
                                for line in f:  # now you are at the lines you want
                                    if "\n" in line:
                                        for line in f:
                                            print(line)
                                            top_text = line
                                            break
                                    break
                        # import adfasdf

                    desc_text.append(os.path.splitext(xx)[0] + " | " + top_text)
                except:
                    # Need to handle the ones that are embedded here
                    pass

        with open(os.path.join(os.getcwd(), "telegram", x, "index.mdx"), "w") as f:
            f.write(
                '# {}\n\nimport ReferenceCard from "@site/src/components/General/ReferenceCard";\n\n<ul className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 -ml-6"> \n'.format(
                    x
                )
            )
            for w in desc_text:
                f.write(
                    '<ReferenceCard title="{}" description="{}" url="/bot/reference/telegram/{}/{}" />\n'.format(
                        w.split("|")[0], w.split("|")[1], x, w.split("|")[0]
                    )
                )
            f.write("</ul>")
