import os

# This script is used to generate the index.mdx files for the reference section of the
# docs Copy paste the output of the .txt file into the section
# it generates relative to the index.mdx file

# get the file names of all the files in a given relative path
files_discord = os.listdir(os.path.join(os.getcwd(), "discord"))

files_telegram = os.listdir(os.path.join(os.getcwd(), "telegram"))

# remove last entry in a list cause it is not needed
files_discord.pop()
files_telegram.pop()
# remove index.md from the list

# create discord reference card
with open(os.path.join(os.getcwd(), "discord", "discord.txt"), "w") as f:
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

# create telegram reference card
with open(os.path.join(os.getcwd(), "telegram", "telegram.txt"), "w") as f:
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
