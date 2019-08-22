import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

requirements = []

requirements_names = ['base', 'django', 'elastic']

for req_name in requirements_names:
    with open("requirements/{}.txt".format(req_name), "r") as fh:
        req = fh.readlines()

    requirements.extend((r for r in req if r != "\n"))

name = "lucyfer"
included_dirs = ['{}/django', '{}/base', '{}', '{}/elastic']

package_dir = {_dir.format(name): _dir.format("src") for _dir in included_dirs}
packages = package_dir.keys()

kwargs = dict(
    author="N Copiy",
    author_email="ncopiy@ya.ru",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ncopiy/django_lucy",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)

kwargs.update(dict(
    description="Lucene search for DRF and elasticsearch-dls",
    install_requires=requirements,
    name=name,
    packages=packages,
    package_dir=package_dir,
    version="0.1.0"))

setuptools.setup(**kwargs)
