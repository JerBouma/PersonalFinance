import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="personal_finance",
    version="1.0.0",
    license="MIT",
    description="Easily track your personal finance",
    author="JerBouma",
    author_email="jer.bouma@gmail.com",
    url="https://github.com/JerBouma/PersonalFinance",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=["finance", "personal"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "tqdm==4.62.3",
        "gspread_dataframe==3.2.2",
        "oauth2client==4.1.3",
    ],
    scripts=["./personal_finance"]
)