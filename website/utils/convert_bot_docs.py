import os

# small utility to move bot files to their respective folders


def main():
    os.chdir("bot")
    files = os.listdir()
    for file in files:
        file_name = file.split(".")[0]
        if os.path.isfile(file):
            if "telegram" in file:
                os.rename(file, f"telegram/{file_name}.mdx")
            elif "discord" in file:
                os.rename(file, f"discord/{file_name}.mdx")


if __name__ == "__main__":
    main()
