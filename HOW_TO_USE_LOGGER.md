# 개요
logger 커스텀 패키지의 사용법을 안내드립니다.

# 사용법
1. logger 패키지에서 logger를 import합니다.
```python
from logger import Logger
```
2. logger 인스턴스를 생성합니다. 기본적으로 stdout에 출력하는 handler를 가지고 있기에 **그대로 사용하시면 화면에 로그가 출력됩니다**.
```python
logger = Logger()
```
3. File에 로그를 작성하고 싶으시면 FileHandler를 추가합니다.
```python
from logger import Logger, FileHandler
logger = Logger()
file_handler = FileHandler()
logger.add_handler(file_handler)
```
4. 로그 포맷을 바꾸고 싶으면 Formatter 클래스를 활용합니다.
```python
from logger import Logger, Formatter
logger = Logger()
formatter = Formatter(fmt="[{time}] [{level}] {message}")
logger.set_formatter(Formatter)
```