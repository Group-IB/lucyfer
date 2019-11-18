import os

import setuptools


class LucyferSetup:
    _version = None

    def setup(self):
        setuptools.setup(**self._get_kwargs())

    @property
    def lib(self):
        return "lucyfer"

    @property
    def version(self):
        if self._version is None:
            with open("setup/lucyfer") as fp:
                self._version = fp.readline()
        return self._version

    def _get_kwargs(self):
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
            description="Lucene search for DRF and elasticsearch-dsl",
            tests_require=self._get_requirements(name="test"),
            install_requires=self._get_requirements(name="base"),
            extras_require=dict(full=self._get_requirements(name="extra")),
            name=self.lib,
            packages=self._get_package_dir(self.lib),
            version=self.version
        )

    def _get_package_dir(self, path):
        top_level_dirs = os.listdir(path)

        current_paths = [path]

        for p in top_level_dirs:
            if p != "__pycache__":
                full_path = os.path.join(path, p)

                if os.path.isdir(full_path):
                    current_paths.append(full_path)
                    paths = self._get_package_dir(full_path)
                    current_paths.extend(paths)

        return list(set(current_paths))

    def _get_requirements(self, name):
        requirements = []

        with open("requirements/{}.txt".format(name), "r") as fh:
            req = fh.readlines()
        requirements.extend((r for r in req if r != "\n"))

        return requirements


if __name__ == "__main__":
    parser = LucyferSetup()
    parser.setup()
