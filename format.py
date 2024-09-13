import subprocess


def main():
    subprocess.run(
        [
            "poetry",
            "run",
            "autoflake",
            "--remove-duplicate-keys",
            "--remove-all-unused-imports",
            "--ignore-init-module-import",
            "--remove-unused-variables",
            "--in-place",
            "--recursive",
            ".",
        ],
        check=True,
    )
    subprocess.run(["poetry", "run", "black", ".", "--line-length", "100"], check=True)


if __name__ == "__main__":
    main()
