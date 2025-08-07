# 개요
logger 커스텀 패키지의 사용법을 안내드립니다.

# 사용법
## 일반적인 사용법
1. logger 패키지에서 logger를 import합니다.
```python
from logger import Logger
```
2. logger 인스턴스를 생성합니다. 기본적으로 파일("_logs/latest.log_")에 출력하는 handler를 가지고 있기에 **그대로 사용하시면 파일에 로그가 출력됩니다**.
```python
logger = Logger()
logger.print("TestShellApp.read()", "메세지메세지메세지")
```
## **(강추!)** 간단 사용법
trace 데코레이터를 활용해서 자동적으로 함수의 시그니처 등을 출력합니다.
```python
from logger import Logger
from decorators import trace
logger = Logger()

@trace(logger)
def read():
...
```
```log
[25.08.07 15:33] TestShellApp.read(): 호출됨 - args: ('2',), kwargs: {}
```

## 로그 Format을 바꾸고 싶어요!
1. 로그 포맷을 바꾸고 싶으면 Formatter 클래스를 활용합니다.
```python
from logger import Logger, Formatter
logger = Logger()
formatter = Formatter(fmt="[{time}] [{level}] {message}")
logger.set_formatter(Formatter)
```