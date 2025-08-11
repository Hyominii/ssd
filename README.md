# ssd
즐거운 프로젝트😁

이 프로젝트는 Code Review Agent 교육 과정

**BestReviewer팀**의 SSD 프로젝트를 위한 레포지토리입니다.



## 🛠️ 요구사항
### 기본 기능
#### SSD
- **가상 SSD 구현**
- **명령어**
  - `W [LBA] [Value]` : 지정 LBA에 값 저장 (0x00000000 ~ 0xFFFFFFFF).
  - `R [LBA]` : 지정 LBA 값 읽기.
- **저장 구조**
  - `ssd_nand.txt` : SSD 데이터 저장 파일.
  - `ssd_output.txt` : 마지막 Read 결과 저장.
- **유효성 검사**
  - LBA 범위(0~99), Value 형식(0x + 8 HEX) 확인.
  - 범위/형식 오류 시 `ssd_output.txt`에 `"ERROR"` 기록.

#### Test Shell
- **기능**: SSD 동작 검증용 CLI.
- **명령어**
  - `write [LBA] [Value]`
  - `read [LBA]`
  - `fullwrite [Value]` : 전체 LBA Write.
  - `fullread` : 전체 LBA Read.
  - `help` / `exit`
- **Test Script**
  - `1_FullWriteAndReadCompare`
  - `2_PartialLBAWrite`
  - `3_WriteReadAging`
  - ReadCompare로 PASS/FAIL 판단.

### 확장 기능
#### Erase 기능
- SSD 명령어: `E [LBA] [SIZE]`  
  특정 LBA부터 SIZE칸 삭제 (`0x00000000` 초기화).  
  최대 SIZE=10, 범위 오류 시 `"ERROR"` 기록, `size=0` 허용(동작 없음).
- Shell 명령어:
  - `erase [LBA] [SIZE]`
  - `erase_range [Start_LBA] [End_LBA]` (순서 무관)

#### Logger 기능
- **로그 관리**
  - `latest.log`에 기록, 10KB 초과 시 `until_날짜_시간.log`로 변경.
  - 로그 파일 2개 이상 시 오래된 파일 `.zip` 압축(파일명 변경만).

#### Runner 기능
- 스크립트 목록(txt)에 적힌 Test Script를 순차 실행.
- 실행 중 FAIL 발생 시 즉시 종료, PASS면 다음 스크립트 실행.
- CLI 실행 시 runner 모드 선택 가능.

#### Command Buffer 기능
- Write/Erase 명령을 최대 5개까지 Buffer에 저장 후 일괄 처리(Flush).
- SSD 명령어: `F`, Shell 명령어: `flush`
- **최적화 알고리즘**
  1. **Ignore Command**: 같은 LBA에 중복 명령 제거.
  2. **Merge Erase**: 인접 Erase 범위 병합 (SIZE ≤ 10).
  3. **Fast Read**: Read 시 Buffer 먼저 조회, 최신 값 반환.



## 🧑‍💻 기여

기여 시 아래 문서를 참고해주세요:

- [브랜치 네이밍 규칙](./docs/branch-convention.md)
- [커밋 메시지 작성 규칙](./docs/commit-convention.md)
- [PR 템플릿](./.github/PULL_REQUEST_TEMPLATE.md)
- [팀 리뷰 전략](./docs/review-strategy.md)
