import argparse
import setuptools


class LibHelper:
    LUSYA = "lusya"
    LUCYFER = "lucyfer"

    library_to_requirements_names = {
        LUSYA: ['base', 'django'],
        LUCYFER: ['base', 'django', 'elastic'],
    }

    library_to_description = {
        LUSYA: "Lucene search for DRF",
        LUCYFER: "Lucene search for DRF and elasticsearch-dsl",
    }


class SetupCommand(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_argument('--lib', choices=[LibHelper.LUCYFER, LibHelper.LUSYA])
        self.add_argument('--version')

        args = self.parse_args()
        self.lib = args.lib
        self.version = args.version

    def setup(self):
        kwargs = self._get_base_kwargs()

        package_dir = self._get_package_dir()

        kwargs.update(dict(
            description=LibHelper.library_to_description[self.lib],
            install_requires=self._get_requirements(),
            name=self.lib,
            packages=package_dir.keys(),
            package_dir=package_dir,
            version=self.version))

        setuptools.setup(**kwargs)

    def _get_base_kwargs(self):
        with open("README.md", "r") as fh:
            long_description = fh.read()

        return dict(
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

    def _get_package_dir(self):
        included_dirs = ["{}/" + req for req in LibHelper.library_to_requirements_names[self.lib]] + ["{}"]
        return {_dir.format(self.lib): _dir.format("src") for _dir in included_dirs}

    def _get_requirements(self):
        requirements = []

        for req_name in LibHelper.library_to_requirements_names[self.lib]:
            with open("requirements/{}.txt".format(req_name), "r") as fh:
                req = fh.readlines()
            requirements.extend((r for r in req if r != "\n"))

        return requirements


if __name__ == "__main__":
    parser = SetupCommand()
    parser.setup()
