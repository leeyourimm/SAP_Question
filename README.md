# SAP 서면(필기) 시험 문제집 · ABAP · RAP · SAPUI5

웹페이지: https://leeyourimm.github.io/sap_question/

SAP 개발자 서면 시험 대비 문제집입니다. 4개 단원에 통합 문제 185개가 있고, 문제마다 소문항 (1)(2)…와 정답·해설이 들어 있습니다.

| 파일 | 소주제 | 문제 수 |
|---|---|---|
| [01_abap_basics.md](01_abap_basics.md) | 데이터 타입 · 문자열 · 날짜 · 제어문 · 생성자 표현식 · 필드 심볼 · 내부 테이블 · ABAP SQL · 알고리즘 | 29 |
| [02_abap_practice.md](02_abap_practice.md) | DDIC · 리포트 · ALV · 모듈풀 · LUW · 인터페이스 · 확장 · 성능 · OOP · 예외 · ABAP Unit · T-code | 68 |
| [03_s4_cds_rap.md](03_s4_cds_rap.md) | ABAP on HANA · CDS · AMDP · ABAP Cloud · RAP · OData · Fiori Elements 연결 | 49 |
| [04_ui5_fiori.md](04_ui5_fiori.md) | Fiori · manifest · MVC · 바인딩 · OData V2/V4 · 라우팅 · Fiori Elements · JavaScript | 39 |

유형: 개념(서술·객관식·표) · 코드(결과·빈칸·오류) · 작성(코드 직접 쓰기). 난이도 ★1~★3.

웹페이지 기능: 단원·유형·난이도 필터, 검색, 내 답 메모(브라우저에만 저장), 무작위 10문제 모의고사.

> 실제 SAP 시스템에서 실행해 검증하지는 않았습니다(ABAP 7.40 SP08 이상, ABAP Cloud 기준).

## 페이지 다시 만들기

```bash
pip install markdown pygments
LC_ALL=C.UTF-8 python3 _web/gen.py   # abap-drill.html 생성
```
`gen.py`는 `abap-drill.html`을 만듭니다. 이 저장소에서는 그 결과를 `index.html`로 둡니다.
