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
        print(f"팀명: BestReviewer")
        print(f"팀장: 이장희 / 팀원: 김대용, 최도현, 박윤상, 최동희, 안효민, 김동훈")
        print("사용 가능한 명령어:")
        print("  write <LBA> <Value>      : 특정 LBA에 값 저장")
        print("  read <LBA>               : 특정 LBA 값 읽기")
        print("  fullwrite <Value>        : 전체 LBA에 동일 값 저장")
        print("  fullread                 : 전체 LBA 읽기 및 출력")
        print("  help                     : 도움말 출력")
        print("  exit                     : 종료")

    def run(self):
        pass


if __name__ == "__main__":
    app = TestShellApp()
    app.run()
    app.help()
