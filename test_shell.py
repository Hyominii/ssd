class TestShellApp:
    def read(self, address: int):
        pass

    def full_read(self):
        pass

    def write(self, address: int, value: str):
        pass

    def full_write(self, value: str):
        pass

    def exit(self):
        pass

    def help(self):
        pass

    def run(self):
        pass


if __name__ == "__main__":
    app = TestShellApp()
    app.run()
