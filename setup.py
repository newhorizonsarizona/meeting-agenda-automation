from setuptools import setup

setup(
    name="meeting-agenda-automation",
    version="1.0.0",
    description="Executable to package into azure function",
    long_description=open("README.md").read().strip(),
    entry_points={"console_scripts": ["meeting-agenda-automation=cli"]},
    author="Anand Vijayan",
    author_email="avijaychandran@newhorizonsarizona.org",
    url="https://github.com/newhorizonsarizona/meeting-agenda-automation/tree/main",
    py_modules=["o365"],
    install_requires=[],
    license="Proprietary",
    zip_safe=False,
    keywords="NHTM",
    classifiers=["Packages", "Boilerplate"],
)