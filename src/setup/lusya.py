from setup import SetupCommand, LibHelper


class LibCommand(SetupCommand):
    @property
    def lib(self):
        return LibHelper.LUSYA


if __name__ == "__main__":
    parser = LibCommand()
    parser.setup()
