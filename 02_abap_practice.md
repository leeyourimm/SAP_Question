# 02. ABAP 실무 (DDIC · 리포트 · 화면 · 인터페이스 · OOP · T-code)

레거시(클래식) ABAP 실무 전체를 주제별 단원으로 묶은 통합 문제집이다. 원본 371문항(클래식 ABAP, OOP·예외·ABAP Unit, 면접 빈출, T-code·용어, 손코딩 1~10단원, 모의고사 1회)의 사실·함정·코드 포인트를 빠짐없이 소문항과 해설에 담았다. 예제는 SFLIGHT 데이터 모델, ABAP 7.40 이상을 기준으로 한다.

## 시스템 기본·아키텍처

### B-001. 3계층 구조·work process·클라이언트 [개념] ★★
<!-- src: IB-001, IB-002, IB-003, IB-004, IB-005, TC-024, TC-093, TC-094, TC-036 -->
신입 개발자가 DEV 시스템(클라이언트 100, 500)에 처음 로그온했다. 선배가 시스템 구조를 설명해 준다.

(1) SAP NetWeaver AS ABAP의 3계층 이름과 역할을 쓰시오. ABAP 소스는 어디에 저장되고 어디서 실행되는가?
(2) 다음 구성 요소의 역할을 한 줄씩 쓰시오: Dispatcher, Work Process, Gateway, Message Server, ICM, Enqueue Server(Enqueue Replication).
(3) SM50에 보이는 work process 유형 약어 6가지와 각각 처리하는 일을 쓰시오.
(4) 다음 중 옳지 않은 것을 고르시오.
① 디스패처는 들어온 요청을 대기열에 넣고 비어 있는 work process에 배분한다. ② 게이트웨이는 RFC 통신을 담당한다. ③ 메시지 서버는 애플리케이션 서버 사이의 통신과 로그온 부하 분산을 담당한다. ④ ICM은 HTTP/HTTPS 요청을 처리한다. ⑤ 사용자가 로그온하면 dialog work process 하나가 로그오프할 때까지 고정 배정된다.
(5) 대화형 프로그램이 오래 걸리면 덤프 TIME_OUT이 나는 이유와 대책을 쓰시오. 또 dialog step마다 work process가 바뀌는 구조가 DB LUW·잠금 설계에 주는 결과를 쓰시오.
(6) 클라이언트란 무엇인가? 3-system landscape(DEV/QAS/PRD)의 역할, 표준 클라이언트 000·001(·066)의 의미, 클라이언트 목록 테이블 이름, 클라이언트 종속 테이블을 알아보는 방법(첫 키 필드 이름·데이터 엘리먼트·DDIC 타입)을 쓰시오.
(7) 클라이언트 종속 대상만 고른 것은? ㄱ. ABAP 프로그램 소스 ㄴ. MANDT가 첫 키인 테이블의 데이터 ㄷ. SPRO에서 저장한 판매 문서 유형 설정 ㄹ. 데이터 엘리먼트 정의 ㅁ. 사용자 마스터(SU01)
① ㄱ,ㄴ ② ㄴ,ㄷ,ㅁ ③ ㄷ,ㄹ ④ ㄱ,ㄹ,ㅁ ⑤ ㄴ,ㄷ,ㄹ
(8) 클라이언트 100에서 Z SAPscript 폼을 수정·활성화했다. 클라이언트 500에서는 어떻게 되는가? 옮기는 방법은? SmartForms였다면 어떻게 다른가? ABAP SQL로 다른 클라이언트 데이터를 읽는 방법도 쓰시오.

<details><summary>정답·해설</summary>

**(1)** 프레젠테이션 계층(SAP GUI, 웹 브라우저·Fiori Launchpad: 입력을 받아 애플리케이션 서버로 보내고 결과 표시) / 애플리케이션 계층(하나 이상의 애플리케이션 서버(인스턴스). 디스패처와 work process가 ABAP 프로그램을 실행) / 데이터베이스 계층(시스템당 하나의 중앙 DB, S/4HANA는 SAP HANA. 업무 데이터와 함께 ABAP 소스·DDIC 정의(Repository)도 저장). 저장은 DB, 실행은 애플리케이션 서버. 애플리케이션 서버는 여러 대로 늘릴 수 있지만(수평 확장) DB는 하나다. HANA에서는 코드 푸시다운으로 일부 계산을 DB 계층으로 옮긴다.
**(2)** Dispatcher: 사용자 요청을 받아 대기열에 넣고 빈 work process에 배분하는 큐 관리자. Work Process: ABAP 프로그램을 실제 실행하는 프로세스. Gateway: RFC 통신(다른 SAP 시스템·외부 프로그램). Message Server: 애플리케이션 서버 간 통신과 로드 밸런싱(로그온 그룹). ICM: HTTP(S)/SMTP 요청 처리(OData, Fiori, 웹 서비스 진입점). Enqueue Server: 시스템 전체의 잠금 테이블(SAP 잠금) 관리. 디스패처·게이트웨이·메시지 서버·ICM은 work process가 아니라 별도 프로세스다.
**(3)**

| 약어 | 이름 | 처리 |
|---|---|---|
| DIA | Dialog | 사용자 dialog step(화면 처리), RFC·HTTP 요청 |
| BTC(BGD) | Background | 배치 잡(SM36/SM37) |
| UPD | Update(V1) | `IN UPDATE TASK` 업데이트 모듈 중 V1(긴급) |
| UP2 | Update2(V2) | V2(비긴급, 통계 등) 업데이트 모듈 |
| ENQ | Enqueue | 잠금 테이블 관리(ENQUEUE/DEQUEUE). 최근에는 ASCS의 독립 Enqueue Server가 담당 |
| SPO | Spool | 출력 요청을 프린터·스풀로 보냄 |

**(4)** ⑤. dialog work process는 한 dialog step(화면 하나의 PAI~다음 PBO)마다 배정되고, 다음 step은 다른 work process가 처리할 수 있다. 사용자 문맥(roll area)은 step 사이에 roll-out/roll-in된다. 그래서 적은 수의 work process로 많은 사용자를 처리한다. ①~④는 맞다.
**(5)** dialog work process는 여러 사용자가 공유하는 자원이므로 한 dialog step이 허용 시간(프로필 파라미터 `rdisp/max_wprun_time`, 최신 커널은 `rdisp/scheduler/max_runtime`)을 넘기면 강제로 끊고 TIME_OUT 덤프를 낸다. 오래 걸리는 처리는 백그라운드 잡으로 돌린다. 결과: 화면에서 다음 화면으로 갈 때 work process가 바뀌므로 DB LUW가 암묵적으로 커밋되고, dialog step을 넘어 DB 잠금을 유지할 수 없다. 그래서 SAP 잠금(Enqueue)과 SAP LUW 개념이 필요하다.
**(6)** 클라이언트: 한 SAP 시스템 안에서 업무적으로 독립된 단위(3자리 번호, 예: 100). 각자 마스터·트랜잭션·대부분의 커스터마이징 데이터를 갖고, 로그온할 때 지정한다. 설정은 SCC4. DEV(개발·Customizing), QAS(품질: 통합 테스트·사용자 테스트), PRD(운영: 실제 업무). 000: SAP 참조 클라이언트(SAP 제공 기본 설정, 업그레이드 대상, 직접 사용 금지), 001: 000의 복사본(초기 설치 시 샘플 클라이언트), 066: 예전 EarlyWatch 클라이언트. 클라이언트 목록 테이블은 T000. 첫 번째 키 필드가 `MANDT`(데이터 엘리먼트 MANDT, DDIC 타입 CLNT 길이 3)이면 클라이언트 종속.
**(7)** ②. Repository 객체(프로그램, 클래스, DDIC 정의, CDS)는 클라이언트 독립이라 한 클라이언트에서 바꾸면 시스템 전체에 적용된다. 업무 데이터(SCARR, SFLIGHT, VBAK 등), 클라이언트 종속 Customizing, 사용자 마스터(USR02에 MANDT 있음), SAPscript 폼, 표준 텍스트(SO10)는 클라이언트별로 따로 있다. 독립: 프로그램, 클래스, DDIC 정의, SmartForms, 화면, 일부 시스템 테이블(T000 등).
**(8)** 클라이언트 500에는 반영되지 않는다. SAPscript 폼(레이아웃 셋)과 표준 텍스트는 클라이언트 종속이다. 클라이언트 간에는 SE71 → Utilities → Copy from Client 또는 전송 요청에 담아 SCC1로 복사한다(시스템 간은 전송). 500에서 다시 활성화한다고 반영되지는 않는다. SmartForms는 클라이언트 독립이라 한 클라이언트에서 바꾸면 그 시스템의 모든 클라이언트에 반영된다(SAPscript와 SmartForms 차이의 단골 포인트). ABAP SQL은 현재 로그온 클라이언트(sy-mandt)로 자동 필터링하며, 다른 클라이언트는 `USING CLIENT`(구 문법 `CLIENT SPECIFIED`)로 읽는다. 프로그램 변경은 모든 클라이언트에 즉시 보이지만 클라이언트 종속 데이터는 클라이언트 복사(SCC1)나 전송이 필요하다.

</details>

---

### B-002. 개발 객체·패키지·프로그램 유형·개발 T-code [개념] ★
<!-- src: IB-006, IB-007, IB-008, IB-009, IB-010, IB-016, TC-091, TC-039, TC-001, TC-002 -->
Z 프로젝트에서 RICEFW 개발 목록을 받았다. 개발을 시작하기 전에 패키지와 도구를 정리한다.

(1) RICEFW 각 글자의 개발 유형과 대표 기술을 쓰시오.
(2) 패키지(예전 이름 개발 클래스)의 역할, `$TMP`에 저장한 객체의 성격, 전송 계층의 의미를 쓰시오. 또 고객 객체 이름 규칙(시작 문자 2가지, 회사 예약 네임스페이스 형식), 패키지 유형 3가지, 패키지가 속하는 상위 단위와 고객 개발용 대표 값을 쓰시오.
(3) 다음 표의 T-code를 쓰시오.

| 기능 | T-code | 기능 | T-code |
|---|---|---|---|
| ABAP Dictionary | (a) | Menu Painter(GUI Status/Title) | (f) |
| ABAP Editor | (b) | 메시지 클래스 | (g) |
| Function Builder | (c) | 트랜잭션 코드 생성 | (h) |
| Class Builder | (d) | Object Navigator | (i) |
| Screen Painter | (e) | Data Browser | (j) |

(4) 다음 T-code의 기능을 한 줄씩 쓰시오: SE12, SE14, SE16N, SE39, SE84, SE21, SE32, SE63, SA38, SE36.
(5) 프로그램 속성 Type 코드 1, M, F, K, J, I, S, T의 유형을 쓰시오. 그리고 "F – 서브루틴 풀"이라는 설명이 왜 틀렸는지 쓰고, 각 유형이 어떻게 실행되는지 쓰시오.
(6) 텍스트 요소 3가지와 용도, 하드코딩 문자열 대신 텍스트 심볼을 쓰는 이유, `'Default'(001)`의 동작을 쓰시오.
(7) SAP Note(OSS Note)란 무엇이며, 코드 수정이 든 Note를 적용하는 T-code와 절차는?

<details><summary>정답·해설</summary>

**(1)**

| 글자 | 의미 | 대표 기술 |
|---|---|---|
| R | Reports | 클래식/인터랙티브 리포트, ALV, CDS 기반 분석 |
| I | Interfaces | RFC/BAPI, IDoc(ALE/EDI), 웹 서비스, OData |
| C | Conversions | 데이터 이관: BDC, LSMW, BAPI, Migration Cockpit |
| E | Enhancements | User/Customer Exit, BAdI, Enhancement Framework, BTE |
| F | Forms | SAPscript, SmartForms, Adobe Forms |
| W | Workflow | SAP Business Workflow(SWDD) |

면접에서는 "각 영역에서 직접 한 개발을 설명하라"로 이어지며, 기능 명세(Functional Spec)를 받아 기술 명세(Technical Spec)를 쓰는 흐름도 말할 수 있으면 좋다.
**(2)** 패키지: 개발 객체를 묶는 단위로 객체 소속, 전송 경로, 소프트웨어 컴포넌트를 정하고 패키지 인터페이스(Use Access)로 다른 패키지에서의 사용을 통제한다. SE21/SE80에서 만든다. `$TMP`(또는 `$`로 시작하는 패키지)는 로컬 객체가 되어 전송 요청에 들어가지 않는다(테스트·연습용). 나중에 전송하려면 객체 디렉터리 항목에서 패키지를 바꾼다. 전송 계층: 객체가 어느 경로(DEV → QAS → PRD)로 이동할지 정하는 계층, 고객 개발은 보통 Z 전송 계층(예: ZDEV). 이름 규칙: Z, Y 또는 등록된 네임스페이스 `/ABC/`. 패키지 유형: Development package(일반 개발), Main package(하위 패키지만 포함), Structure package(최상위 구조). 상위 단위는 Software Component, 고객 개발은 `HOME`(로컬 테스트는 `LOCAL`). ABAP Cloud에서는 Software Component가 git 저장소(gCTS/abapGit) 단위가 된다.
**(3)** (a) SE11 (b) SE38 (c) SE37 (d) SE24 (e) SE51 (f) SE41 (g) SE91 (h) SE93 (i) SE80 (j) SE16(새 화면 SE16N). SE80은 SE11/SE37/SE24/SE38/SE51/SE41을 한 트리에 모은 통합 도구로 패키지, 함수 그룹, 모듈 풀, BSP, Web Dynpro까지 관리한다. 함수 그룹은 SE80 또는 SE37(Goto → Function Groups)에서 만든다. SE11에서 Utilities → Table Contents로 SE16을 부를 수 있다. 테이블 유지보수는 SM30, 전송 요청은 SE09/SE10/SE01. CDS·BDEF 같은 신규 객체는 ADT(Eclipse)에서만 편집한다.
**(4)** SE12: DDIC 조회 전용. SE14: Database Utility(DDIC 정의와 DB 테이블 맞추기: Activate and adjust database, 변환, 삭제 후 재생성). SE16N: 새 형식 Data Browser(General Table Display). SE39: Split Screen Editor(두 프로그램 비교). SE84: Repository Information System(개발 객체 검색). SE21: Package Builder. SE32: 텍스트 요소 관리. SE63: 번역(짧은·긴 텍스트). SA38: 프로그램 실행만(편집 불가). SE36: Logical Database Builder. SE38에서도 F8 실행은 되지만 개발 권한(S_DEVELOP)이 필요하므로 업무 사용자에게는 SA38이나 별도 T-code를 준다. SE16H는 HANA용 확장 Data Browser(집계·그룹 조회).
**(5)** 1 실행 프로그램(Executable, 리포트), M 모듈 풀(대화 프로그램), F 함수 그룹(메인 프로그램 SAPL<그룹명>), K 클래스 풀(SE24 글로벌 클래스), J 인터페이스 풀, I Include, S 서브루틴 풀, T 타입 그룹. F는 함수 그룹이고 서브루틴 풀은 S이므로 틀렸다. F8로 단독 실행되는 것은 유형 1뿐이다. M은 SE93 Dialog transaction(트랜잭션 코드)으로, F는 함수 모듈 호출로, K/J는 클래스 사용으로만 실행된다. Include는 단독 실행·활성화 단위가 아니다(메인 프로그램 안에서 문법 검사). Type group은 이제 자동 로드되며(`TYPE-POOLS` 불필요) 새로 만들지 않는 것이 권장된다.
**(6)** Text Symbols(`TEXT-001` 또는 `'Default text'(001)`로 참조하는 문자열), Selection Texts(선택 화면 PARAMETERS/SELECT-OPTIONS 라벨, DDIC 참조 시 데이터 엘리먼트 라벨 사용 가능), List Headings(리스트 표준 페이지 헤더: 제목, 열 머리글). 텍스트 요소는 로그온 언어별로 번역(SE63 또는 Goto → Translation)되어 다국어 지원이 되지만 하드코딩 문자열은 번역되지 않는다. `'Default'(001)`은 텍스트 심볼 001이 현재 언어에 있으면 그것을, 없으면 리터럴을 쓴다. 텍스트 요소는 프로그램과 별도로 활성화해야 하고, 확장 프로그램 검사(SLIN)가 텍스트 심볼 누락을 찾아 준다.
**(7)** SAP이 지원 포털(SAP for Me / Support Portal)에 게시하는 문서로 버그 수정(correction instructions), 알려진 문제와 우회 방법, 컨설팅 정보, 선행 Note를 담는다. 적용은 SNOTE(Note Assistant): Note 다운로드 → 적용 가능 여부(릴리스·SP) 확인 → 선행 Note 함께 구현 → 수정 코드가 전송 요청에 기록 → 테스트 후 전송. 수동 단계(DDIC 변경 등)는 Note 안내대로 따로 수행. Note로 바뀐 표준 객체는 업그레이드 시 SPAU에서 정리되고, 지원 패키지(SP)를 올리면 해당 Note가 포함되어 "obsolete"로 표시된다.

</details>

---

### B-003. 기초 문법 함정: TABLES·아이콘·체인 문장·STATICS·짧은 손코딩 [코드] ★★
<!-- src: IB-014, IB-015, IB-017, IB-018, IB-019, IB-020 -->
다음 코드 조각과 질문에 답하시오.

```abap
REPORT zb003.
TABLES sflight.
____(가)____ <icon>.
DATA: a TYPE i VALUE 1,
      b TYPE i VALUE 2,
      c TYPE i.

START-OF-SELECTION.
  ADD 10 TO: a, b.
  c = a + b.
  WRITE: / a, / b, c.
  WRITE: / icon_green_light ____(나)____, 'Available'.
```

(1) 빈칸 (가)(나)를 채우고, 아이콘 목록을 보는 방법과 ALV에서 아이콘을 내는 방법을 쓰시오.
(2) 실행 후 a, b, c의 값과 체인 문장 부분이 출력하는 줄 수를 쓰고, 콜론이 어떻게 풀리는지 설명하시오.
(3) `TABLES sflight.`는 무엇을 선언하는가? 지금도 꼭 필요한 경우와 필요 없는 경우, 그리고 `SELECT * FROM sflight.`(INTO 없음)의 의미를 쓰시오.
(4) 옳지 않은 것을 고르시오. ① ABAP 키워드는 대소문자를 구분하지 않는다. ② 1열의 `*`는 줄 전체 주석, `"`는 그 뒤부터 줄 끝까지 주석이다. ③ STATICS 변수는 FORM이 끝나도 값이 유지된다. ④ STATICS는 정적 메서드 안에서만 쓸 수 있고 FORM이나 함수 모듈에서는 쓸 수 없다. ⑤ ABAP에는 고정 길이 타입(c, n, p 등)과 가변 길이 타입(string, xstring)이 있다.
(5) 정수 `a = 5`, `b = 9`를 세 번째 변수 없이 바꾸는 코드를 쓰고 주의점을 쓰시오.
(6) 선택 화면 문자열(최대 50자)이 공백과 대소문자를 무시하고 회문인지 판정해 "Palindrome"/"Not palindrome"을 출력하는 프로그램을 작성하시오. `condense`를 쓰면 안 되는 이유와 `LOWER CASE`의 효과, `reverse`가 없을 때의 방법도 쓰시오.

<details><summary>정답·해설</summary>

**(1)** (가) `INCLUDE` (나) `AS ICON`. 아이콘 상수(ICON_GREEN_LIGHT 등)는 include `<ICON>`(또는 obsolete인 `TYPE-POOLS icon`)에 있고 `WRITE ... AS ICON`으로 출력해야 아이콘으로 보인다. 목록은 테이블 ICON이나 프로그램 SHOWICON. ALV는 필드 카탈로그 `icon = 'X'`.
**(2)** a = 11, b = 12, c = 23, 2줄. `ADD 10 TO: a, b.`는 `ADD 10 TO a. ADD 10 TO b.`(콜론 앞부분이 각 문장에 반복). `WRITE: / a, / b, c.`는 `WRITE / a. WRITE / b. WRITE c.`가 되어 첫 줄에 a, 둘째 줄에 b와 c. `/`가 있는 WRITE만 새 줄을 시작한다(아이콘 줄은 별도의 셋째 줄).
**(3)** DDIC 구조 SFLIGHT와 같은 이름·타입의 테이블 작업 영역(interface work area)을 전역에 선언한다(DB 테이블 선언이 아님). 필요한 경우: 화면(Dynpro)에 DDIC 참조 필드(`SFLIGHT-CARRID`)를 두고 프로그램과 값을 자동 교환할 때, 논리 데이터베이스의 `GET` 노드. 필요 없는 경우: 일반 SELECT, 선택 화면(`SELECT-OPTIONS s_carr FOR sflight-carrid`는 `DATA gv_carrid TYPE s_carr_id.` + `FOR gv_carrid`로 대체). `SELECT * FROM sflight.`(INTO 없음)는 TABLES 작업 영역에 읽는 obsolete 문법이다.
**(4)** ④. STATICS는 서브루틴, 함수 모듈, 정적 메서드에서 쓸 수 있다(인스턴스 메서드에서는 불가, 대신 인스턴스 속성). STATICS 변수는 프로그램이 메모리에 있는 동안 값이 유지된다. 함수 모듈 안의 일반 DATA는 호출마다 초기화되지만 함수 그룹 TOP include 전역 데이터는 유지된다(B-020).
**(5)**
```abap
a = a + b.   " a = 14
b = a - b.   " b = 5
a = a - b.   " a = 9
```
주의: 값이 크면 `a + b`에서 정수 범위(i는 약 ±21억)를 넘어 CX_SY_ARITHMETIC_OVERFLOW. 실무에서는 임시 변수가 읽기 쉽다. 곱셈/나눗셈(0 문제), XOR(정수 타입에 직접 못 씀) 방법도 언급할 수 있다.
**(6)**
```abap
REPORT zib_palindrome.
PARAMETERS p_text TYPE c LENGTH 50 LOWER CASE.

START-OF-SELECTION.
  DATA(lv_s) = to_upper( replace( val  = CONV string( p_text )
                                  sub  = ` `
                                  with = ``
                                  occ  = 0 ) ).
  IF lv_s = reverse( lv_s ).
    WRITE / 'Palindrome'.
  ELSE.
    WRITE / 'Not palindrome'.
  ENDIF.
```
`replace( ... occ = 0 )`은 모든 공백을 지우지만 `condense`는 중간 공백을 하나로 줄일 뿐 없애지 않는다. `LOWER CASE`를 빼면 입력이 자동으로 대문자가 된다. `reverse( )`가 없던 시절에는 `strlen( )`으로 길이를 구하고 `lv_s+lv_i(1)`과 `lv_s+lv_j(1)`을 양 끝에서 비교하는 DO 루프를 썼다.

</details>

---

### B-004. 기타 기술: Web Dynpro·Workflow·SAP Query와 조회 도구 [개념] ★★
<!-- src: IB-153, IB-154, IB-155, TC-018, TC-008, TC-017 -->
유지보수 프로젝트에서 Web Dynpro 화면, 구매 요청 승인 워크플로, 현업이 쓰는 SAP Query를 함께 넘겨받았다.

(1) Web Dynpro ABAP 컴포넌트의 요소(컴포넌트 컨트롤러, 뷰, 윈도우, 플러그, 컨텍스트, 애플리케이션)를 설명하고 MVC와의 대응을 쓰시오.
(2) 구매 요청이 생성되면 팀장에게 승인 작업이 가는 워크플로에 필요한 구성 요소(이벤트, 이벤트 연결, 태스크, 에이전트, 템플릿)와 관련 T-code를 쓰시오.
(3) 워크플로 T-code 표를 채우시오: 워크플로 정의 / BOR 객체·BAPI 메서드 정의 / 사용자 수신함 / 이벤트 트레이스 조회 / 자동 기본 설정 / Work item 조회 / BAPI Explorer.
(4) SAP Query에 대한 설명으로 옳지 않은 것은? ① SQ03에서 사용자 그룹을 만들고 사용자를 할당한다. ② SQ02에서 InfoSet(예전 Functional Area)을 만든다. ③ InfoSet을 사용자 그룹에 할당해야 그 그룹이 쿼리를 만들 수 있다. ④ SQ01은 InfoSet을 만드는 트랜잭션이고 쿼리는 SQ02에서 만든다.
(5) 다음에 맞는 T-code를 쓰시오: 개인용 QuickViewer / 프로그램 실행 전용 / TVARVC 변수 관리. SQVI 결과를 전송하려면?
(6) TMG가 생성된 Customizing 테이블(Delivery Class C)에 업무 담당자가 데이터를 입력하고 전송 요청에 담으려 한다. ① SE11 ② SE16 ③ SM30 ④ SE14 ⑤ SE16N 중 가장 적절한 것과 이유를 쓰시오.

<details><summary>정답·해설</summary>

**(1)** 컴포넌트: 재사용 단위로 컴포넌트 컨트롤러(공통 로직·데이터), 인터페이스 컨트롤러(외부 공개)를 가진다. 뷰: 화면 레이아웃(UI 요소) + 뷰 컨트롤러(액션 처리 메서드) + 뷰 컨텍스트. 윈도우: 보여 줄 뷰와 뷰 사이 내비게이션 링크 정의, 애플리케이션은 윈도우의 인터페이스 뷰를 시작점으로 한다. 플러그: 아웃바운드 플러그 → 내비게이션 링크 → 인바운드 플러그, `wd_this->fire_to_detail_plg( )`로 이동. 컨텍스트: 노드·속성 계층의 데이터 저장소, UI 요소와 데이터 바인딩, 컨트롤러 간 컨텍스트 매핑으로 공유. 애플리케이션: 컴포넌트 + 윈도우 + 플러그를 URL로 실행할 수 있게 한 것(SICF 노드 생성). MVC: 모델 = 어시스턴스 클래스/BAPI 등 백엔드, 뷰 = 뷰 레이아웃, 컨트롤러 = 컴포넌트·뷰·윈도우 컨트롤러. SE80에서 개발하며 FPM, ALV 컴포넌트(SALV_WD_TABLE), Adobe Interactive Form 연동을 지원한다. 신규 UI는 Fiori/UI5가 표준이라 유지보수 질문 위주로 나온다.
**(2)** 비즈니스 객체와 이벤트: BOR 객체(SWO1) 또는 IF_WORKFLOW를 구현한 ABAP 클래스의 이벤트(예: CREATED). 표준 프로그램이 발생시키거나 `SWE_EVENT_CREATE`/`cl_swf_evt_event=>raise`로 발생. 이벤트 연결(SWE2): 이벤트가 오면 시작할 워크플로 연결. 태스크(PFTC): 단일 단계 작업(승인 결정, 메서드 실행). 에이전트: 조직 구조, 규칙(Rule, PFAC), 책임자 결정으로 지정. 템플릿(SWDD): 결정 단계·활동·조건·루프를 그래픽으로 정의, 컨테이너와 바인딩으로 데이터 전달. 사용자는 SBWP나 Fiori My Inbox, 관리자는 SWI1(작업 항목 조회), SWIA(관리), SWEL(이벤트 트레이스), 초기 설정은 SWU3. S/4HANA에는 Flexible Workflow(설정 기반)와 SAP Build Process Automation이 추가됐다.
**(3)** SWDD / SWO1 / SBWP / SWEL / SWU3 / SWI1 / BAPI. BAPI는 BOR 객체 유형(예: BUS2032 판매오더)의 메서드로 정의되고 구현은 RFC 가능 함수 모듈(예: `BAPI_SALESORDER_CREATEFROMDAT2`)이다. 이벤트 트레이스는 SWELS로 켜고 SWEL로 본다.
**(4)** ④. SQ01이 쿼리를 만들고 실행하는 트랜잭션이다(사용자 그룹 → InfoSet → 필드·출력 형식). 순서는 SQ03(사용자 그룹) → SQ02(InfoSet) → SQ01(쿼리). 정렬·합계가 있는 기본 리스트, 통계, 순위 리스트를 코딩 없이 만들며 내부적으로 ABAP 프로그램을 생성한다. 표준 영역(클라이언트 종속)과 전역 영역(클라이언트 독립, 전송 가능)의 구분이 있다. [교정: 원본 IB-155 해설은 표준 영역을 "클라이언트 독립, 전송 가능"이라 했으나, 실제로는 표준 영역이 클라이언트 종속이고 전역 영역이 클라이언트 독립·전송 대상이다.]
**(5)** SQVI / SA38 / STVARVC. SQVI는 사용자 개인 것이라 전송이 안 되며, 필요하면 SAP Query로 변환한다. TVARVC 변수는 배치 작업 변형의 선택 변수로 자주 쓴다.
**(6)** ③ SM30. TMG가 만든 유지보수 화면을 열고, Customizing 테이블이면 저장 시 Customizing 요청을 묻는다(SCC4 설정에 따라). SE16/SE16N은 원칙적으로 조회 도구이고 직접 수정은 감사 문제가 되어 금지된다. SE11은 정의, SE14는 DB 조정 도구다.

</details>

---

## DDIC

### B-005. 도메인·데이터 엘리먼트·타입 매핑·키 [개념] ★★
<!-- src: CL-001, TC-070, TC-071, IB-030, IB-023, IB-031 -->
항공 예약 Z 개발을 위해 DDIC 기본 객체를 정리한다.

(1) 도메인과 데이터 엘리먼트가 각각 정의하는 정보(기술적/의미적)를 구체적 항목으로 쓰시오. 고정값, Search Help, Parameter ID는 각각 어디(도메인/데이터 엘리먼트)에서 지정하는가?
(2) 도메인 고정값과 값 테이블(Value Table)의 역할 차이를 쓰고, 하나의 도메인을 여러 데이터 엘리먼트가 공유하는 예를 드시오. 데이터 엘리먼트를 도메인 없이 만들 수 있는가?
(3) DDIC 내장 타입에 대응하는 ABAP 타입(길이)을 쓰시오: CHAR n, NUMC n, DATS, TIMS, DEC n,m, CURR n,m, CUKY, UNIT, CLNT, LANG, INT4, FLTP, RAW n, STRING. LANG의 내부·화면 표현과 새 타입 몇 가지도 쓰시오.
(4) 표준 데이터 엘리먼트의 DDIC 타입·길이를 쓰시오(S/4HANA 기준): MATNR, KUNNR, BUKRS, WERKS_D, GJAHR, POSNR, WAERS, ERNAM, S_CARR_ID, S_CONN_ID, S_PRICE, S_BOOK_ID. KUNNR 같은 CHAR 10 번호가 DB에 어떻게 저장되는지도 쓰시오.
(5) DDIC 테이블과 구조체의 차이로 옳지 않은 것은? ① 구조체는 DB에 데이터를 저장하지 않는다. ② 테이블에는 기술 설정이 필요하지만 구조체에는 없다. ③ 구조체도 기본 키를 정의해야 활성화된다. ④ 구조체는 다른 테이블·구조체에 INCLUDE 또는 APPEND로 포함될 수 있다.
(6) 테이블 타입이 정의하는 세 가지 속성과, 범위 테이블 타입의 구조·용도를 쓰시오.
(7) 기본 키와 외래키의 차이, MANDT의 위치, `SELECT SINGLE`에 키 일부만 주었을 때의 동작과 권장 대안을 쓰시오.

<details><summary>정답·해설</summary>

**(1)** 도메인 = 기술적 속성(how): Data Type(CHAR, NUMC, DATS, CURR 등), 길이, 소수점, 출력 길이, 변환 루틴(Conversion Routine, 예: ALPHA), 소문자 허용 여부, 값 범위(고정값·값 테이블). 데이터 엘리먼트 = 의미적 속성(what): 도메인(또는 내장 타입)을 참조하고 필드 라벨(Short/Medium/Long/Heading), F1 문서, Search Help, Parameter ID(SET/GET PARAMETER용)를 정의한다. 테이블 필드는 데이터 엘리먼트를 참조한다. 고정값은 도메인, Search Help와 Parameter ID는 데이터 엘리먼트에서 지정한다(위치 차이를 자주 묻는다).
**(2)** 고정값: 도메인에 직접 적은 허용값 목록(예: 상태 'N','A','R'), 화면 입력 자동 검사와 F4 목록에 쓰인다. 값 테이블: 도메인에 지정한 "권장" 체크 테이블로 그 자체로 검사하지 않고, 이 도메인을 쓰는 필드에 외래키를 만들 때 체크 테이블로 제안된다. 예: 도메인 S_CARR_ID(CHAR 3)를 데이터 엘리먼트 S_CARR_ID(항공사)와 다른 의미의 데이터 엘리먼트들이 함께 참조한다(기술 형식은 같고 라벨·F1은 다름). 데이터 엘리먼트는 도메인 없이 내장 타입(Predefined Type)이나 참조 타입으로 직접 만들 수 있다.
**(3)** CHAR n → c(n), NUMC n → n(n), DATS → d(8, YYYYMMDD), TIMS → t(6, HHMMSS), DEC n,m → p(소수 m), CURR n,m → p(소수 m, 통화 키 참조 필수), CUKY → c(5), UNIT → c(3), CLNT → c(3), LANG → c(1), INT4 → i(4바이트), FLTP → f(8바이트), RAW n → x(n), STRING → string. CURR는 CUKY 필드를, QUAN(→ p)은 UNIT 필드를 Reference Field로 지정해야 활성화된다. LANG은 내부 1자리(E, 3 등)이고 화면에는 2자리 ISO 코드(EN, KO)로 변환되어 보인다. 새 타입: DATN/TIMN(HANA 날짜·시간), DECFLOAT16/34, INT8.
**(4)** MATNR CHAR 40(ECC는 18), KUNNR CHAR 10, BUKRS CHAR 4, WERKS_D CHAR 4, GJAHR NUMC 4, POSNR NUMC 6, WAERS CUKY 5, ERNAM CHAR 12, S_CARR_ID CHAR 3, S_CONN_ID NUMC 4, S_PRICE CURR 15,2, S_BOOK_ID NUMC 8. KUNNR·LIFNR·VBELN·EBELN·BELNR_D는 CHAR 10이며 숫자만 쓰면 ALPHA 변환 루틴으로 앞에 0이 채워져 저장된다(예: `0000001234`). 그밖에 EBELP NUMC 5, BUZEI NUMC 3, S_DATE DATS 8, S_CURRCODE CUKY 5, S_CUSTOMER NUMC 8.
**(5)** ③. 구조체에는 기본 키가 없다. 테이블은 최소 하나의 키 필드와 기술 설정, Delivery Class가 있어야 활성화된다. 구조체는 화면 필드, 함수 모듈 인터페이스, ALV 출력 구조, 테이블 타입의 행 타입 등에 쓴다.
**(6)** 테이블 타입: ① 행 타입(Line Type: 데이터 엘리먼트·구조체 등) ② 접근 방식(Standard / Sorted / Hashed / Index / Not specified) ③ 키(Standard key, 행 전체, 키 컴포넌트 지정, unique/non-unique, 2차 키). 범위 테이블 타입: 행이 `SIGN`, `OPTION`, `LOW`, `HIGH`인 테이블 타입. SE11에서 "Ranges Table Type"으로 만들고 LOW/HIGH의 데이터 엘리먼트를 지정한다. FM·메서드 파라미터로 SELECT-OPTIONS 같은 범위 조건을 넘기거나 `WHERE carrid IN @lt_range`에 쓴다. FM의 TABLES 파라미터 대신 테이블 타입 IMPORTING/EXPORTING이 권장되며, 프로그램 안에서는 `TYPE RANGE OF s_carr_id`로 바로 선언할 수 있다.
**(7)** 기본 키: 각 행을 유일하게 식별하는 필드 조합(중복·NULL 불가, DB가 기본 인덱스 자동 생성). 외래키: 필드 값이 다른 테이블(Check Table)의 기본 키 값 중 하나여야 한다는 관계로, SAP에서는 화면 입력 검사와 F4에 쓰이고 DB 레벨 제약으로 강제되지 않는다. MANDT는 클라이언트 종속 테이블의 첫 번째 키 필드. `SELECT SINGLE`에 키 일부만 주어도 문법 오류는 아니고 조건에 맞는 행 중 아무 한 행(정해지지 않음)을 읽으며, 확장 검사·ATC가 경고를 낸다. 키 전체를 모르면 `SELECT ... UP TO 1 ROWS` + `ORDER BY`로 원하는 행을 분명히 한다.

</details>

---

### B-006. Z 테이블 설계와 활성화 오류·표준 테이블 확장 [작성] ★★★
<!-- src: CL-008, CL-009, CL-010, MX-002, IB-024 -->
항공편 좌석 요청을 저장하는 클라이언트 종속 투명 테이블 `ZCL_FLREQ`를 설계한다. 요구사항: 요청 번호(10자리 숫자, 앞자리 0 채움)가 키, 항공사·노선·비행일·요청 좌석 수·좌석당 가격과 통화·상태(N=신규, A=승인, R=거절)·생성자·생성 시각(타임스탬프) 저장, 항공사는 SCARR 기준 화면 입력 검사, 가능한 한 SFLIGHT 표준 데이터 엘리먼트 사용.

(1) 다음 표를 완성하시오. 새로 만드는 데이터 엘리먼트/도메인은 이름과 정의를 함께 쓴다.

| 필드 | 키 | 데이터 엘리먼트 | Data Type | 길이 | 소수 | 참조 필드·검사 |
|---|---|---|---|---|---|---|
| | | | | | | |

(2) 테이블 설정값을 쓰시오: Delivery Class, Data Browser/Table View Maint., Enhancement Category, Data Class, Size Category, Buffering. 함께 만드는 것이 일반적인 객체는?
(3) 동료가 만든 `ZCL_BOOKREQ`(Delivery Class A, Enhancement Category 지정됨)가 활성화되지 않는다. 잘못된 곳을 모두 찾아 고치시오.

| 순서 | 필드 | 키 | 데이터 엘리먼트 | Data Type | 길이 | 소수 | 참조 필드 |
|---|---|---|---|---|---|---|---|
| 1 | MANDT | ✔ | MANDT | CLNT | 3 | 0 | |
| 2 | CARRID | ✔ | S_CARR_ID | CHAR | 3 | 0 | |
| 3 | PRICE | | S_PRICE | CURR | 15 | 2 | (없음) |
| 4 | CONNID | ✔ | S_CONN_ID | NUMC | 4 | 0 | |
| 5 | CURRENCY | | S_CURRCODE | CUKY | 5 | 0 | |
| 6 | QTY | | MENGE_D | QUAN | 13 | 3 | ZCL_BOOKREQ-CURRENCY |

(4) Z 테이블에 `PRICE`(S_PRICE, CURR 15,2)를 추가했더니 "reference field missing" 오류가 난다. 올바른 조치는? ① Currency/Quantity Fields 탭에서 참조 테이블 `ZMX_FLIGHT`, 참조 필드 `CURRENCY`(S_CURRCODE, CUKY 5) 지정 ② 참조 필드로 `CARRID`(S_CARR_ID, CHAR 3) 지정 ③ Delivery class를 A로 변경 ④ Enhancement category를 "Can be enhanced (deep)"로 변경. 참조 필드가 왜 필요한지, 다른 테이블 필드를 참조해도 되는지 쓰시오.
(5) Delivery Class·Enhancement Category에 대해 옳지 않은 것은? ① A는 마스터·트랜잭션 데이터를 담는 애플리케이션 테이블 ② C는 고객이 유지하는 커스터마이징 테이블로 데이터는 커스터마이징 요청으로 전송 ③ L은 임시 데이터용으로 납품 시 데이터 없이 전달 ④ "Cannot Be Enhanced"인 테이블에는 Append Structure를 추가할 수 없다 ⑤ A에서 C로 바꾸면 버퍼링 유형이 자동으로 Full로 바뀐다. 나머지 Delivery Class(G, E, S, W)의 의미도 쓰시오.
(6) 표준 테이블(예: VBAK)에 고객 필드를 추가하는 Append Structure와 Customizing Include를 비교하고, 고객 필드 이름 규칙과 업그레이드 시 장점, 새 필드를 화면에 보이게 하려면 추가로 필요한 것을 쓰시오.

<details><summary>정답·해설</summary>

**(1)**

| 필드 | 키 | 데이터 엘리먼트 | Data Type | 길이 | 소수 | 참조 필드·검사 |
|---|---|---|---|---|---|---|
| MANDT | ✔ | MANDT | CLNT | 3 | 0 | 클라이언트 |
| REQ_ID | ✔ | ZCL_REQ_ID(신규, 도메인 ZCL_REQ_ID: NUMC 10) | NUMC | 10 | 0 | NUMC라 앞자리 0 |
| CARRID | | S_CARR_ID | CHAR | 3 | 0 | 외래키 Check Table = SCARR |
| CONNID | | S_CONN_ID | NUMC | 4 | 0 | (선택) 외래키 SPFLI |
| FLDATE | | S_DATE | DATS | 8 | 0 | |
| SEATS | | S_SEATSOCC | INT4 | 10 | 0 | 요청 좌석 수 |
| PRICE | | S_PRICE | CURR | 15 | 2 | 참조 필드 ZCL_FLREQ-CURRENCY |
| CURRENCY | | S_CURRCODE | CUKY | 5 | 0 | 통화 키(외래키 TCURC는 선택) |
| STATUS | | ZCL_REQ_STATUS(신규, 도메인 ZCL_REQ_STATUS: CHAR 1, 고정값 N/A/R) | CHAR | 1 | 0 | 도메인 고정값으로 화면 검사 |
| CREATED_BY | | SYUNAME(또는 ERNAM) | CHAR | 12 | 0 | |
| CREATED_AT | | TIMESTAMPL | DEC | 21 | 7 | UTC 긴 타임스탬프 |

키 필드는 테이블 맨 앞에 연속으로 두고, 클라이언트 종속이므로 MANDT가 첫 키. 외래키는 화면 입력 검사와 F4에만 작동한다(B-008).
**(2)**

| 설정 | 값 |
|---|---|
| Delivery Class | A(애플리케이션 테이블, 마스터·트랜잭션 데이터) |
| Data Browser/Table View Maint. | Display/Maintenance Allowed(TMG를 쓸 경우) 또는 Allowed with Restrictions |
| Enhancement Category | Can be enhanced (character-type or numeric) 또는 Can be enhanced (deep). 확장 계획이 없으면 Cannot Be Enhanced. 반드시 지정 |
| Data Class | APPL1(트랜잭션 데이터) |
| Size Category | 0~1(예상 건수에 맞게) |
| Buffering | Not allowed(자주 바뀌는 업무 데이터, 금액·좌석에는 버퍼링을 쓰지 않음) |

Lock Object(EZCL_FLREQ, 키 MANDT+REQ_ID)도 함께 만든다. 채점 포인트: 키 구성, CURR↔CUKY 참조, 상태 도메인 고정값, Delivery Class, Enhancement Category.
**(3)** ① 키 필드 CONNID가 비키 필드 PRICE 뒤에 있다 → 키 필드는 앞쪽에 연속해야 하므로 CONNID를 CARRID 다음(3번)으로 옮긴다. ② CURR 필드 PRICE에 참조 필드가 없다 → Currency/Quantity Fields 탭에서 참조 테이블 ZCL_BOOKREQ, 참조 필드 CURRENCY(CUKY) 지정. ③ QUAN 필드 QTY가 CUKY 필드를 참조한다 → QUAN은 UNIT 필드를 참조해야 하므로 필드 `UNIT`(데이터 엘리먼트 MEINS, UNIT 3)을 추가하고 QTY의 참조 필드를 ZCL_BOOKREQ-UNIT로 바꾼다. Enhancement Category 미지정은 최신 릴리스에서 경고로 나온다.
**(4)** ①. CURR는 CUKY 필드를, QUAN은 UNIT 필드를 반드시 참조해야 한다. 통화 키에 따라 소수 자릿수가 달라지기 때문이다(예: JPY는 소수 0자리). 참조 필드는 출력 시 소수점 위치와 단위를 결정한다. 같은 테이블이든 다른 테이블(예: `SCARR-CURRCODE`)이든 되지만 타입이 각각 CUKY/UNIT이어야 한다. ②는 CHAR 필드라 안 되고 ③④는 이 오류와 무관하다.
**(5)** ⑤. Delivery Class는 데이터 소유와 전송·클라이언트 복사·업그레이드 시 동작을 정하고, 버퍼링은 기술 설정에서 따로 정한다. ①②③④는 맞다(Enhancement Category는 Append Structure/Customizing Include로 필드를 추가할 수 있는지, 어떤 타입(문자형·숫자형·deep)까지 허용하는지 정한다). G: 고객이 추가만 가능한 커스터마이징(SAP 업그레이드로부터 보호), E: SAP·고객 키 영역이 분리된 시스템 테이블, S: SAP 시스템 테이블, W: 시스템 테이블(별도 전송).
**(6)** Append Structure: 고객이 직접 만들어 표준 테이블 끝에 붙이는 구조체. 한 테이블에 여러 개를 붙일 수 있고 하나의 Append는 한 테이블에만 속한다. 표준 정의를 수정하지 않는다(수정 키 불필요). Customizing Include: SAP이 표준 테이블 안에 미리 넣어 둔 `CI_`로 시작하는 include 자리(예: 코딩 블록 CI_COBL). 고객은 그 include 구조체만 만들어 필드를 채운다. SAP이 자리를 마련한 테이블에서만 쓸 수 있고, 같은 include를 쓰는 여러 테이블에 한 번에 반영된다. 필드 이름은 `ZZ` 또는 `YY`로 시작해 SAP 필드와 충돌하지 않게 한다. 둘 다 수정(Modification)이 아니므로 업그레이드 때 새 정의를 가져와도 고객 필드가 자동으로 다시 붙는다(SPDD 조정 불필요). Enhancement Category가 "Cannot Be Enhanced"이면 Append를 붙일 수 없다. 새 필드를 화면에 보이거나 값을 채우려면 Screen Exit, BAdI 등 확장이 따로 필요하다.

</details>

---

### B-007. 기술 설정·테이블 종류·구조 변경·DD 시스템 테이블 [개념] ★★
<!-- src: CL-002, MX-001, TC-072, IB-021, IB-022, TC-069, IB-025, TC-003, TC-065 -->
운영 중인 Z 테이블과 표준 테이블을 다루며 생기는 질문들이다.

(1) 투명 테이블의 기술 설정 항목 5가지와 각각이 영향을 주는 것을 쓰시오. 기술 설정을 저장하지 않으면 어떻게 되는가?
(2) 다음 코드의 의미를 쓰시오: 데이터 클래스 APPL0, APPL1, APPL2 / Delivery Class A, C, L, G, E, S, W. Z 업무 데이터 테이블의 보통 조합은?
(3) 기술 설정·속성 설명 중 옳지 않은 것은? ① Data class는 테이블이 놓일 물리 저장 영역 ② Size category는 처음 확보할 저장 공간 크기 ③ 버퍼링을 허용하면 `BYPASSING BUFFER` 없이 읽어도 항상 DB 최신 값을 읽는다 ④ "Log data changes"와 rec/client가 설정돼 있으면 변경 이력이 DBTABLOG에 남는다 ⑤ Delivery class C는 고객 설정 데이터용이며 Customizing 요청에 기록된다.
(4) 투명·풀·클러스터 테이블을 DB 대응, 저장 방식, 예, 제약으로 비교하시오. ECC에서 클러스터에 속했던 표준 테이블 3개와 물리 클러스터 이름, S/4HANA에서의 변화를 쓰시오.
(5) "DDIC에 정의되어 있지만 DB에 물리적으로 없는 테이블"이 있을 수 있는가? 경우와 확인·조정 방법을 쓰시오. 반대 경우(DB에만 있음)는?
(6) 데이터 100만 건이 있는 Z 테이블에 대해 ① 끝에 비키 필드 추가 ② CHAR 10 필드를 CHAR 5로 줄임 ③ 키 필드 추가를 할 때 각각 무슨 일이 일어나고 어떤 도구로 처리하는가? 길이를 줄였을 때 쓰는 T-code를 ① SE11 ② SE14 ③ SE16N ④ SM30 ⑤ SE54 중 고르시오.
(7) DD·Repository 시스템 테이블 이름을 쓰시오: 테이블 정의 / 테이블 설명 / 필드 목록 / 데이터 엘리먼트 / 도메인 / 고정값·고정값 텍스트 / 객체 디렉터리 / 트랜잭션 코드·텍스트 / 함수 모듈 목록 / 메시지 / 전송 요청 헤더·객체 목록 / 프로그램 디렉터리. DD 테이블 이름 규칙도 쓰시오.

<details><summary>정답·해설</summary>

**(1)**

| 항목 | 의미 |
|---|---|
| Data Class(APPL0/1/2 등) | DB에서 테이블이 놓일 물리 영역(tablespace) |
| Size Category(0~9) | 예상 레코드 수, 최초 저장 공간(extent) 크기 |
| Buffering(허용 안 함 / 허용하지만 꺼짐 / 허용) | 애플리케이션 서버 테이블 버퍼 사용 여부 |
| Buffering Type(Single / Generic / Full) | 버퍼 단위: 단일 레코드, 일반 키 영역, 테이블 전체 |
| Log Data Changes | 변경 이력을 DBTABLOG에 기록(시스템 파라미터 rec/client와 함께 동작) |

Data Class·Size Category는 저장 공간, 버퍼링은 읽기 성능, 로그는 감사와 관련된다. 버퍼링은 자주 읽고 거의 안 바뀌는 작은 테이블(커스터마이징, 코드 테이블)에 쓴다. 기술 설정은 테이블 정의와 별도로 저장되며, 저장하지 않으면 테이블을 활성화할 수 없다.
**(2)** APPL0 마스터 데이터(변경 적음), APPL1 트랜잭션 데이터(자주 변경), APPL2 조직·Customizing 데이터. A 애플리케이션 테이블(업그레이드 시 SAP가 데이터를 건드리지 않음), C 고객 Customizing(고객만 유지, 클라이언트 종속 Customizing 요청), L 임시 데이터(전송 안 함), G SAP 업그레이드로부터 보호되는 Customizing(SAP는 새 항목 INSERT만 하고 기존 항목을 덮어쓰지 않음, 고객 키 범위는 TRESC), E 시스템 제어 테이블(SAP와 고객 모두 항목 보유), S SAP 시스템 테이블(SAP만 유지, 프로그램처럼 취급), W 시스템 테이블이지만 내용이 다른 객체의 일부로 전송. Z 업무 데이터는 보통 A + APPL0/APPL1.
**(3)** ③. 테이블 버퍼는 애플리케이션 서버마다 따로 있고 다른 서버의 변경은 동기화 간격이 지나야 반영되므로 버퍼 값은 잠깐 오래된 값일 수 있다. 최신 값이 꼭 필요하면 `BYPASSING BUFFER`를 쓰거나 자주 바뀌는 테이블은 버퍼링하지 않는다. ④ 변경 로그는 테이블 설정과 시스템 파라미터가 둘 다 켜져야 기록된다. ⑤ G는 고객 설정이지만 SAP가 일부 키 범위를 보호, S·E·W는 시스템 데이터.
**(4)**

| 항목 | 투명 | 풀 | 클러스터 |
|---|---|---|---|
| DB 대응 | DDIC 1개 = DB 1개(1:1) | 여러 DDIC → 테이블 풀 하나(N:1, 예: ATAB) | 여러 DDIC → 테이블 클러스터 하나(N:1) |
| 저장 | 필드가 그대로 DB 컬럼 | 테이블 이름 + 키(VARKEY) + 나머지를 한 필드(VARDATA)에 압축 | 키가 같은 여러 테이블의 행을 키 + 페이지 번호 + 압축 데이터로 묶음 |
| 예 | 마스터·트랜잭션 데이터 대부분 | 작은 커스터마이징·시스템 테이블(예전 조건 테이블 A0xx 일부) | BSEG(RFBLG), KONV(KOCLU), CDPOS(CDCLS) |
| 제약 | 없음 | 2차 인덱스·조인·뷰·네이티브 SQL 불가(예전 릴리스), 키로만 효율적 | 동일. 키 이외 조건·집계·정렬은 애플리케이션 서버에서 풀어서 처리해 느림, 버퍼링 불가 |

S/4HANA(및 HANA 위 NetWeaver 7.40 이상)에서 대부분 투명 테이블로 변환(depooling/declustering)되어 조인·집계가 가능해졌다. BSEG는 투명, KONV는 PRCD_ELEMENTS로 대체. 풀·클러스터 테이블은 DB에 같은 이름의 테이블이 없어 DB 도구로 직접 볼 수 없었다. 변환 후에는 키 순서로 정렬되어 나온다는 가정이 더 이상 성립하지 않는다.
**(5)** 있을 수 있다. ① 투명 테이블을 저장만 하고 활성화하지 않았거나 활성화 중 DB 테이블 생성이 실패 ② 풀·클러스터 테이블(DDIC에는 논리 테이블, DB에는 풀/클러스터만) ③ 전송 import 단계에서 DB 객체 생성 실패. SE14(Database Utility)에서 DB 객체 존재 여부를 보고 "Create database table" 또는 "Activate and adjust database" 실행. SE11 → Utilities → Database Object → Check로도 확인한다. DB에만 있고 DDIC에 없는 테이블은 ABAP SQL로 접근할 수 없다(네이티브 SQL만). 구조체는 애초에 DB 테이블이 없다.
**(6)** ① DB에 컬럼만 추가(ALTER TABLE), 데이터 유지, 새 필드는 초기값, SE11 활성화로 끝난다. ② 데이터 손실 가능 변경이라 테이블 변환(conversion) 필요: SE14 "Activate and adjust database"(Save data)로 임시 테이블(QCM 테이블)에 옮겨 새 구조로 다시 만든 뒤 되돌린다. 5자를 넘는 값은 잘린다. ③ 기본 키 정의가 바뀌므로 일반적으로 변환(또는 기본 인덱스 재생성) 필요, 기존 행의 새 키 필드는 초기값. 키 필드를 빼거나 키 길이를 줄이면 중복 키가 생겨 변환 실패·데이터 손실 가능. 객관식 정답 ② SE14(SE11은 정의 변경·활성화 도구이며 Utilities → Database Object → Database Utility로 SE14를 부름, SE16N은 조회, SM30은 TMG 화면 실행, SE54는 TMG 생성). 대용량 변환은 오래 걸리고 잠금을 유발하므로 운영 시간 외에 계획하고, import 중 실패하면 SE14 "Continue adjustment"로 재개한다. 키 변경은 기존 데이터 정합성 검토가 먼저다.
**(7)** DD02L / DD02T / DD03L / DD04L / DD01L / DD07L·DD07T / TADIR / TSTC·TSTCT / TFDIR / T100 / E070·E071 / TRDIR. 규칙: DD01 도메인, DD02 테이블, DD03 필드, DD04 데이터 엘리먼트, DD07 고정값, 끝 문자 L = 정의(활성 버전 AS4LOCAL = 'A'), T = 텍스트. 메시지 클래스 자체는 T100A, 함수 모듈 설명은 TFTIT, 프로그램 소스는 REPOSRC.

</details>

---

### B-008. 외래키·Search Help·뷰·테이블 유지보수(TMG) [작성] ★★
<!-- src: CL-003, CL-004, IB-026, CL-006, CL-007, IB-028, IB-029, TC-006, HC-023 -->
SFLIGHT-CARRID에 SCARR를 참조하는 외래키가 있다. 또 대기자 명단 Z 테이블 `ZHC_WAITLIST`(필드 ERNAM, ERDAT, ERZET, STATUS, 요청 좌석 수 SEATS 등)를 SM30으로 관리하려 한다.

(1) Check Table과 Foreign Key Table은 각각 어느 테이블인가? 외래키 검사는 언제 동작하며 ABAP의 `INSERT sflight FROM ...`에서도 검사되는가? Value Table과의 차이, 카디널리티 "1:CN"의 의미를 쓰시오.
(2) Elementary와 Collective Search Help의 차이, Append Search Help, Search Help를 화면 필드에 연결하는 방법의 우선순위(높은 순), IMP/EXP 플래그의 의미를 쓰시오.
(3) 옳은 것을 모두 고르시오. ① 매치코드는 Search Help의 전신으로 4.0 이후 대체됐다 ② DB 인덱스는 한 테이블의 필드로만 만들 수 있다 ③ Search Help는 여러 테이블을 조인한 뷰를 선택 방법으로 쓸 수 있다 ④ DB 인덱스를 만들면 해당 필드에 F4가 자동으로 생긴다.
(4) 클래식 DDIC 뷰 4가지(Database, Projection, Maintenance, Help)를 조인 방식, 테이블 수, 변경 가능 여부, 용도로 비교하시오.
(5) `ZHC_WAITLIST`의 TMG를 만드는 절차와 입력 항목(권한 그룹, 함수 그룹, 유지보수 유형, 화면 번호, 변경 기록)을 쓰고, 1단계와 2단계의 차이를 쓰시오. 업무 사용자에게 줄 트랜잭션은 어떻게 만드는가?
(6) SM30에서 새 항목을 만들 때 ERNAM·ERDAT·ERZET가 자동으로 채워지고 상태가 비어 있으면 W가 들어가게 하는 이벤트 번호와 FORM을 작성하시오. 이벤트 01, 02, 03, 05, 21, AA의 실행 시점도 쓰시오.
(7) 저장 직전에 요청 좌석 수가 1~9인지 검사하는 이벤트와, 그 FORM에서 오류를 낼 때 주의점을 쓰시오. 테이블 구조를 바꾼 뒤 TMG에서 해야 할 일은?
(8) 헤더 ZIB_HDR과 아이템 ZIB_ITM을 "헤더 선택 → 그 헤더의 아이템 편집" 순서로 유지보수하게 하려면 무엇을 만드는가(T-code 포함)? 유지보수 뷰와의 차이는? 다음 빈칸도 채우시오: TMG 생성 T-code ( ㉠ ), 유지보수 화면 실행 ( ㉡ ), View Cluster 실행 ( ㉢ ), TMG에서 반드시 지정하는 개발 객체 ( ㉣ )와 화면 번호, 업무 사용자용 트랜잭션 유형 ( ㉤ ).

<details><summary>정답·해설</summary>

**(1)** Check Table = SCARR(참조되는 쪽, 키 값 보유), Foreign Key Table = SFLIGHT(검사받는 필드가 있는 쪽). 화면(Dynpro) 입력 시에만 자동 검사된다(PAI 자동 입력 검사, 선택 화면 포함). ABAP SQL `INSERT/UPDATE/MODIFY`에는 DB 레벨 참조 무결성이 없어 검사되지 않으므로 프로그램에서는 직접 SELECT로 검사한다("외래키가 ABAP SQL에서도 막아 준다"는 흔한 오답). Value Table은 도메인에 지정, 검사하지 않고 외래키 정의 시 Check Table 후보로 "제안"될 뿐이며, Check Table은 필드 외래키에 지정된 실제 검사 대상이다. 1:CN: 왼쪽 "1"은 외래키 테이블 각 레코드에 Check Table 레코드가 정확히 하나, 오른쪽 "CN"은 Check Table 한 레코드에 외래키 테이블 레코드가 0개 이상. Check Table은 Search Help가 없을 때 F4 기본값으로도 쓰이며, 외래키 정의 시 Check Table의 키 필드(MANDT 포함)마다 대응 필드를 매핑한다.
**(2)** Elementary: 하나의 선택 방법(테이블 또는 뷰)과 다이얼로그 유형, 파라미터를 정의한 단일 Search Help. Collective: 여러 Elementary를 탭으로 묶은 것(사용자가 탭에서 검색 방법 선택). Append Search Help로 표준 Collective에 Z Elementary를 추가한다. 우선순위: ① 화면 필드 속성에 직접 지정 / POV(`PROCESS ON VALUE-REQUEST`) 또는 선택 화면 `AT SELECTION-SCREEN ON VALUE-REQUEST FOR`, 리포트의 `MATCHCODE OBJECT` ② 테이블(구조) 필드에 연결된 Search Help ③ 필드의 Check Table에 연결된 Search Help, 없으면 Check Table 키 값 목록 ④ 데이터 엘리먼트에 연결된 Search Help ⑤ 도메인 고정값, 날짜/시간 필드의 캘린더·시계. IMP: 화면 필드 값을 Search Help로 가져와 검색 조건으로 씀. EXP: 고른 값을 화면 필드로 돌려줌. POV 모듈은 Search Help보다 우선하며 `F4IF_INT_TABLE_VALUE_REQUEST`로 직접 F4 목록을 띄울 때 쓴다("왜 내가 만든 Search Help가 안 뜨는가"의 답).
**(3)** ①, ②, ③. ④ 인덱스는 검색 성능용 DB 객체로 F4와 무관하다. 매치코드는 여러 테이블 필드를 묶은 검색 도구였고 지금은 Elementary/Collective Search Help다. Selection method에는 테이블, DB 뷰, Help View, CDS 뷰를 쓸 수 있다.
**(4)**

| 뷰 | 조인 | 테이블 수 | 변경 | 용도 |
|---|---|---|---|---|
| Database View | Inner Join | 여러 개 | 단일 테이블 뷰일 때만 변경 가능(여러 테이블이면 읽기 전용) | DB에 실제 뷰 생성, ABAP SQL 조회 |
| Projection View | 없음 | 1개 | 가능 | 한 테이블의 일부 필드만 노출(Pooled/Cluster도 가능) |
| Maintenance View | Outer Join | 여러 개(외래키 연결) | 가능(SM30, TMG) | 묶인 여러 테이블을 한 화면에서 유지보수 |
| Help View | Outer Join | 여러 개(외래키 연결) | 불가 | Search Help의 선택 방법(SELECT 대상 아님) |

Database View만 DB에 실제 객체가 생기고, Maintenance/Help View는 ABAP 런타임에서만 해석된다. 신규 조회용은 CDS View가 권장된다.
**(5)** 절차: 테이블의 Delivery Class와 Data Browser/Table View Maint.를 "Display/Maintenance Allowed"로 → SE11 → Utilities → Table Maintenance Generator(또는 SE54) → 항목 입력 → Create. 입력 항목:

| 항목 | 값 |
|---|---|
| Authorization Group | `&NC&`(권한 그룹 없음) 또는 업무용 그룹(예: ZHC). S_TABU_DIS 검사용 |
| Function Group | `ZHC_WAITLIST_TMG`(유지보수 화면·FORM이 생성될 전용 함수 그룹), Package도 지정 |
| Maintenance Type | One step |
| Maint. Screen No. | Overview screen 0001(Find Scr. No.로 제안) |
| Recording Routine | Standard recording routine(변경을 전송 요청에 기록) 또는 no, or user, recording routine(전송 불필요한 고객 데이터) |

1단계: 개요 화면 하나에서 여러 행을 표 형태로 바로 편집. 2단계: 개요 화면에는 키 위주 목록, 행을 고르면 상세 화면(single screen)에서 한 건씩 편집(필드가 많을 때). 트랜잭션: SE93 파라미터 트랜잭션으로 `SM30`을 지정하고 `VIEWNAME=Z테이블`, `UPDATE=X` 기본값, 초기 화면 건너뛰기 체크. Delivery Class C 테이블은 커스터마이징 요청으로 전송된다. SM31은 예전 유지보수 T-code.
**(6)** 이벤트 05(Creating a new entry). TMG 화면 → Environment → Modification → Events에서 `05`와 FORM 이름을 등록한다.
```abap
FORM zhc_set_defaults.
  zhc_waitlist-ernam = sy-uname.
  zhc_waitlist-erdat = sy-datum.
  zhc_waitlist-erzet = sy-uzeit.
  IF zhc_waitlist-status IS INITIAL.
    zhc_waitlist-status = 'W'.
  ENDIF.
ENDFORM.
```
TMG 함수 그룹 TOP의 `TABLES zhc_waitlist` 작업 영역(화면 필드와 같은 이름)에 값을 넣으면 화면 행에 반영된다. 이벤트: 01 DB 저장 직전, 02 저장 직후, 03 삭제 직전, 05 새 항목 생성 시, 21 숨긴 필드 채우기, AA 직접 만든 루틴으로 표준 처리 대체. 생성자·생성일 같은 감사 필드는 01에서 채우는 방법도 대표적이다. 채점: TMG 항목 30점(항목당 6점), 이벤트 번호 20점 + FORM 30점(작업 영역이 테이블 이름과 같다는 점 포함), (7) 20점.
**(7)** 이벤트 01(Before saving the data in the database). FORM 안에서 `TOTAL` 내부 테이블을 돌며 새로 만든(`<action> = neuer_eintrag`) 행이나 바꾼(`<action> = aendern`) 행만 검사한다. 오류면 `MESSAGE ... TYPE 'S' DISPLAY LIKE 'E'`로 보여 주고 TMG 표준 플래그 `vim_abort_saving = 'X'`로 저장을 취소한다. `TYPE 'E'`를 바로 내면 유지보수 대화의 흐름이 끊겨 입력 내용을 잃을 수 있다. 필드 단위로 막으려면 TMG 화면 PAI에 `FIELD ... MODULE ...`을 추가할 수도 있지만 재생성 시 덮어쓰일 수 있다. 구조 변경 후에는 TMG를 재생성(Change → "New field/sec. table in structure")해야 새 필드가 나온다. 안 하면 SM30 화면이 옛 구조로 남거나 오류가 난다. 재생성하면 직접 고친 화면은 덮어쓰이지만 이벤트 FORM은 별도 include라 유지된다.
**(8)** 각 테이블(또는 유지보수 뷰)에 TMG를 만든 뒤 SE54에서 뷰 클러스터(View Cluster)를 만들어 헤더 → 아이템 계층(상위 객체, 키 연결)을 정의하고, 사용자는 SM34로 유지보수한다(필요하면 SE93 파라미터 트랜잭션으로 감쌈). 유지보수 뷰는 외래키로 연결된 여러 테이블을 1:1 또는 N:1로 합쳐 "한 화면의 한 행"처럼 유지보수(SM30)할 뿐 1:N 계층 탐색은 안 되고, 뷰 클러스터는 여러 유지보수 대상을 트리 구조(왼쪽 대화 구조 탐색)로 묶어 1:N 계층을 순서대로 유지보수한다. SPRO 커스터마이징 화면 다수가 뷰 클러스터이며, 뷰 클러스터에도 이벤트(SE54 → Events)를 둘 수 있다. 빈칸: ㉠ SE54 ㉡ SM30 ㉢ SM34 ㉣ 함수 그룹 ㉤ 파라미터 트랜잭션.

</details>

---

## 리포트·선택화면·리스트

### B-009. 리포트 이벤트 순서와 메시지 동작 [코드] ★★★
<!-- src: CL-011, MX-004, TC-105, TC-106, IB-012, TC-101, TC-102, TC-103, TC-104, MX-018, IB-039, MX-006, IB-040 -->
다음 두 프로그램을 보고 답하시오.

```abap
REPORT zcl_event_order.
PARAMETERS p_carr TYPE s_carr_id.
DATA gv_log TYPE string.

LOAD-OF-PROGRAM.
  gv_log = gv_log && 'L'.
INITIALIZATION.
  gv_log = gv_log && 'I'.
AT SELECTION-SCREEN OUTPUT.
  gv_log = gv_log && 'O'.
AT SELECTION-SCREEN ON p_carr.
  gv_log = gv_log && 'F'.
  IF p_carr IS INITIAL.
    MESSAGE 'Airline is required' TYPE 'E'.
  ENDIF.
AT SELECTION-SCREEN.
  gv_log = gv_log && 'A'.
START-OF-SELECTION.
  gv_log = gv_log && 'S'.
END-OF-SELECTION.
  gv_log = gv_log && 'E'.
  WRITE gv_log.
```

```abap
REPORT zmx_004 NO STANDARD PAGE HEADING.
DATA gv_cnt TYPE i.
INITIALIZATION.
  gv_cnt = 10.
START-OF-SELECTION.
  gv_cnt = gv_cnt + 1.
  WRITE / |S{ gv_cnt }|.
  NEW-PAGE.
  WRITE / 'S2'.
TOP-OF-PAGE.
  WRITE / |T{ sy-pagno }|.
END-OF-SELECTION.
  WRITE / 'E'.
```

(1) ZCL_EVENT_ORDER에서 gv_log 출력을 쓰시오. ① p_carr에 LH 입력 후 F8 한 번 ② 비운 채 F8 → 오류 후 LH 입력하고 F8 ③ LH 입력 후 Enter 한 번, 그다음 F8.
(2) ZMX_004를 선택 화면 없이 실행했을 때 리스트의 줄을 순서대로 쓰시오(페이지가 바뀌는 곳은 `(페이지 바뀜)`).
(3) 다음 용도의 이벤트를 쓰시오: 로드 시 한 번 / 선택 화면 표시 전 기본값 / 선택 화면 표시 때마다 속성 변경 / 실행 후 입력 전체 검증 / 주 처리 / 모든 처리 후 출력 / 페이지 머리글 / 행 더블클릭 상세 리스트. 이벤트 키워드 없이 쓴 문장은 어디에 속하는가?
(4) `AT SELECTION-SCREEN` 변형의 실행 시점을 쓰시오: OUTPUT, ON p_carr, ON BLOCK b1, ON RADIOBUTTON GROUP g1, ON VALUE-REQUEST FOR p_file, ON HELP-REQUEST FOR p_carr, ON END OF s_carr, ON EXIT-COMMAND, 추가 없음. PAI 처리 순서와 실행 버튼의 함수 코드도 쓰시오.
(5) 메시지 유형 A, E, I, S, W, X의 영문 이름과 대화 처리에서의 동작을 쓰시오. 다음 중 옳지 않은 것은? ① 실행 프로그램의 `AT SELECTION-SCREEN`에서 E를 보내면 선택 화면에 머물고 모든 입력 필드를 다시 입력할 수 있다 ② X는 MESSAGE_TYPE_X ③ S는 다음 화면 상태 표시줄, 처리 계속 ④ I는 팝업 후 현재 처리를 중단하고 이전 화면으로 돌아간다 ⑤ PAI 모듈에서 FIELD/CHAIN 없이 E를 보내면 화면은 다시 표시되지만 입력 필드가 모두 입력 불가가 된다.
(6) `AT SELECTION-SCREEN ON p_carr`에서 SCARR에 없으면 `MESSAGE e001(zflight) WITH p_carr.`를 보낸다. 없는 항공사로 F8을 누르면 어떻게 되는가? 빈칸도 채우시오: 메시지 클래스 T-code ( ㉠ ), 저장 테이블 ( ㉡ ), 번호 자릿수 ( ㉢ ), `MESSAGE e002(zflight) ( ㉣ ) p_carr p_conn.`, `MESSAGE s003(zflight) ( ㉤ ) 'E'.`, 함수 모듈에서 `MESSAGE e004(zflight) ( ㉥ ) not_found.`, 클래스 없이 `MESSAGE ( ㉦ ) TYPE 'I'.`
(7) 다음 리포트에서 잘못된 곳 3군데를 찾아 고치시오. 그리고 START-OF-SELECTION과 AT SELECTION-SCREEN에서 E 메시지 동작이 어떻게 다른지 쓰시오.
```abap
REPORT zmx_006.
DATA gv_carrid TYPE s_carr_id.
DATA gt_flight TYPE STANDARD TABLE OF sflight.
PARAMETERS p_date TYPE sy-datum OBLIGATORY.
SELECT-OPTIONS s_carr FOR gv_carrid.
INITIALIZATION.
  p_date = sy-datum - 30.
AT SELECTION-SCREEN.
  IF p_date > sy-datum.
    MESSAGE '미래 날짜는 입력할 수 없습니다' TYPE 'I'.
  ENDIF.
START-OF-SELECTION.
  SELECT * FROM sflight INTO TABLE gt_flight
    WHERE carrid = s_carr
      AND fldate >= p_date.
  IF sy-subrc <> 0.
    MESSAGE '데이터가 없습니다' TYPE 'E'.
  ENDIF.
```
(8) 문맥별 메시지 처리를 쓰시오: ① 백그라운드에서 I, S, W ② 백그라운드에서 E, A ③ `EXCEPTIONS error_message = 1`로 호출한 FM 안의 E, A ④ ③과 같은 호출에서 I, S, W ⑤ 어떤 문맥이든 X. 백그라운드 프로그램 설계에 주는 교훈은?
(9) END-OF-SELECTION은 언제 실행되며 원래 목적은? START-OF-SELECTION 안의 `STOP`과 루프 밖 `EXIT` 뒤에 END-OF-SELECTION이 실행되는지 각각 쓰시오. 논리 데이터베이스(LDB)란 무엇이며 LDB 리포트의 이벤트와 장단점은?

<details><summary>정답·해설</summary>

**(1)** ① `LIOFASE`: L → I → 선택 화면 PBO(O) → F8 → 선택 화면 PAI: ON p_carr(F) → AT SELECTION-SCREEN(A) → S → E(리스트 출력은 E에서). ② `LIOFOFASE`: ON p_carr의 E 메시지로 해당 필드만 입력 가능 상태로 선택 화면이 다시 뜨고 A는 실행되지 않는다. 다시 표시되므로 O가 또 실행되고 두 번째 F8에서 F → A → S → E. 전역 데이터는 같은 실행 안이라 유지된다. ③ `LIOFAOFASE`: Enter도 PAI를 일으켜 F, A가 실행되지만 실행 명령이 아니므로 선택 화면이 다시 표시(O)되고, F8에서 F → A → S → E.
**(2)**
```
T1
S11
(페이지 바뀜)
T2
S2
E
```
INITIALIZATION에서 10, START-OF-SELECTION에서 11. 첫 WRITE 직전에 새 페이지가 시작되어 TOP-OF-PAGE가 먼저 돈다(sy-pagno = 1 → `T1`), 그다음 `S11`. `NEW-PAGE`는 빈 페이지를 바로 만들지 않고 "다음 출력은 새 페이지에"라고 표시만 하므로 `WRITE 'S2'` 직전에 TOP-OF-PAGE가 다시 돌아 `T2`, 이어서 `S2`. END-OF-SELECTION의 `E`는 같은 2쪽에 이어진다. `NO STANDARD PAGE HEADING` 때문에 표준 제목줄은 없다. TOP-OF-PAGE는 이벤트 블록 위치와 상관없이 "페이지의 첫 출력 직전"에 실행된다는 것이 함정이다.
**(3)** LOAD-OF-PROGRAM(전역 데이터 초기화, 클래스 생성자 같은 역할) / INITIALIZATION(예: 날짜 기본값 = 이번 달 1일, 선택 화면 표시 전 한 번만) / AT SELECTION-SCREEN OUTPUT(LOOP AT SCREEN으로 필드 숨김·회색, 선택 화면 PBO라 Enter마다 다시 실행) / AT SELECTION-SCREEN / START-OF-SELECTION(DB 조회) / END-OF-SELECTION(LDB 사용 시 특히 의미) / TOP-OF-PAGE / AT LINE-SELECTION. 이벤트 키워드 없이 쓴 실행 문장은 START-OF-SELECTION에 속한다.
**(4)** OUTPUT: 선택 화면 PBO, 화면을 보내기 직전마다. ON p_carr: PAI에서 그 필드가 전달될 때(E 메시지 시 그 필드만 입력 가능). ON BLOCK b1: 블록의 모든 필드가 전달된 뒤(블록 단위 검증). ON RADIOBUTTON GROUP g1: 그룹이 전달될 때. ON VALUE-REQUEST FOR p_file: F4를 눌렀을 때(사용자 정의 입력 도움, 예: 파일 선택 대화 상자). ON HELP-REQUEST FOR p_carr: F1. ON END OF s_carr: 다중 선택(Multiple selection) 대화 상자에서 확인했을 때. ON EXIT-COMMAND: Back(F3), Exit(Shift+F3), Cancel(F12). 추가 없음: PAI의 마지막, 모든 필드 전달 후 전체 검증. 순서: ON 필드 → ON BLOCK → ON RADIOBUTTON GROUP → AT SELECTION-SCREEN. sy-ucomm(또는 `sscrfields-ucomm`)으로 버튼을 구분하며 실행 버튼은 `ONLI`. TOP-OF-PAGE는 첫 출력 문장에서, AT LINE-SELECTION은 리스트 더블클릭에서 발생한다.
**(5)** A Abort(Termination): 대화 상자 후 프로그램(트랜잭션) 종료. E Error: 상태 표시줄 빨간 오류, 처리 중단, PAI에서는 화면 재표시 후 FIELD/CHAIN 필드만 입력 가능. I Information: 대화 상자, Enter 후 다음 문장부터 계속. S Status(Success): 다음 화면 상태 표시줄, 계속. W Warning: 경고, Enter로 계속(PAI에서는 E처럼 재표시 후 Enter로 계속). X Exit: MESSAGE_TYPE_X 덤프. 객관식 정답 ④: I는 팝업을 닫으면 MESSAGE 다음 문장부터 계속 진행한다. ⑤가 FIELD/CHAIN 안에서 검사해야 하는 이유이며, 그 안에서 보낸 E/W는 해당 필드만 다시 열어 준다. 가이드라인은 A·X로 끝내지 말고 예외나 `ASSERT`를 쓰라고 권한다.
**(6)** 선택 화면이 다시 표시되고 p_carr만 입력 가능하며 START-OF-SELECTION은 실행되지 않는다(`AT SELECTION-SCREEN` 본 이벤트에서 보내면 모든 필드가 입력 가능). 고쳐서 다시 실행해야 넘어간다. W를 쓰면 Enter로 무시하고 진행할 수 있다. 빈칸: ㉠ SE91 ㉡ T100 ㉢ 3(000~999) ㉣ WITH ㉤ DISPLAY LIKE ㉥ RAISING ㉦ 텍스트 리터럴이나 문자 변수(예: `'처리 완료'`, `lv_text`, 번역 가능한 `TEXT-001`). 자리 표시자는 `&`(순서대로) 또는 `&1`~`&4`(위치 지정), 최대 4개. `MESSAGE ... RAISING exc`는 호출자가 `EXCEPTIONS exc = n`을 지정했으면 메시지 없이 sy-subrc = n과 sy-msg*만 설정하고, 지정하지 않았으면 메시지를 그대로 보낸다.
**(7)** ① `TYPE 'I'` → `TYPE 'E'`: I는 팝업만 띄우고 계속하므로 잘못된 날짜로 실행된다. ② `WHERE carrid = s_carr` → `WHERE carrid IN s_carr`: SELECT-OPTIONS는 SIGN/OPTION/LOW/HIGH 범위 테이블이라 IN으로 비교한다. ③ START-OF-SELECTION의 `TYPE 'E'` → `MESSAGE '데이터가 없습니다' TYPE 'S' DISPLAY LIKE 'E'.` + `LEAVE LIST-PROCESSING.` `AT SELECTION-SCREEN`의 E는 선택 화면을 다시 띄우고 입력을 다시 받지만, START-OF-SELECTION의 E는 메시지 후 프로그램이 끝나 선택 화면으로 돌아가지 못한다. `FOR gv_carrid`처럼 DATA 변수를 참조하는 것은 맞고(TABLES 불필요), `SELECT *` 대신 필요한 열만 읽으라는 지적은 가점 대상이다.
**(8)** ① 화면 없이 작업 로그(Job Log)에 기록하고 계속. ② 작업 로그에 기록되고 프로그램이 종료되어 작업 상태가 Canceled. ③ 메시지를 표시하지 않고 FM 처리를 끝내며 sy-subrc = 1, 메시지 정보는 sy-msgid/sy-msgty/sy-msgno/sy-msgv1~4에 남는다. ④ 무시되고 FM 처리를 계속. ⑤ 항상 MESSAGE_TYPE_X 덤프. 교훈: 백그라운드용 프로그램에서 E 메시지로 "건너뛰기"를 하면 작업 전체가 중단되므로 개별 오류는 로그(BAL)에 쌓고 계속 진행한다. 업데이트 모듈 안의 E/A 메시지는 업데이트 중단(SM13 Error, Express 메일)으로 이어진다.
**(9)** START-OF-SELECTION(및 LDB의 GET 이벤트)이 모두 끝난 뒤, 리스트 표시 전에 실행된다. LDB가 모든 데이터를 읽은 뒤 집계·출력을 한 번에 하기 위한 이벤트이며, LDB가 없으면 "조회는 START-OF-SELECTION, 출력은 END-OF-SELECTION"으로 나누는 데 쓴다. `STOP`: 현재 리포팅 이벤트를 끝내고 END-OF-SELECTION으로 분기(실행됨). 루프 밖 `EXIT`: 리포팅 처리를 끝내고 바로 리스트 표시(END-OF-SELECTION 실행 안 됨). STOP은 obsolete이고 리포팅 이벤트에서만 쓸 수 있으며, 새 코드는 메서드로 구조화하고 RETURN을 쓴다. LDB: 계층으로 연결된 여러 테이블을 읽어 주는 특수 프로그램(SE36). 실행 프로그램 속성에 LDB 이름(예: F1S 항공 데모, HR의 PNP/PNPCE)을 지정하면 선택 화면을 자동 생성하고 노드별로 데이터를 넘긴다. 이벤트: `GET node`(노드 한 건마다), `GET node LATE`(하위 노드를 모두 처리한 뒤), 그다음 END-OF-SELECTION. 노드는 `NODES` 또는 `TABLES`로 선언. 장점: 선택 화면·권한 검사·읽기 로직 재사용, 계층 처리 간단. 단점: 불필요한 데이터까지 읽어 느릴 수 있고 로직이 숨겨져 디버깅이 어렵다. obsolete이며 ABAP Cloud에서 쓸 수 없다. HR 리포트(PNP + `GET PERNR`, PROVIDE)에서 지금도 보이며, 다른 프로그램에서는 FM LDB_PROCESS로 쓴다.

</details>

---

### B-010. 선택 화면 선언·동적 변경·F4·변형 [작성] ★★
<!-- src: CL-012, CL-013, MX-005, IB-041, IB-042, IB-043, HC-002 -->
SFLIGHT 좌석 점유 리포트 `ZHC_SEATS`의 선택 화면을 만든다.

(1) 다음 요구에 맞게 빈칸을 채우시오: p_date 필수 / s_carr는 구간 칸 없이 단일 값만, 다중 선택 버튼 없음 / 라디오 버튼 2개와 테스트 체크박스 / s_carr-low에 직접 만든 F4 / 초기값으로 s_carr에 LH 한 줄.
```abap
DATA gv_carrid TYPE s_carr_id.
PARAMETERS p_date TYPE s_date ____(1)____.
SELECT-OPTIONS s_carr FOR gv_carrid ____(2)____ NO-EXTENSION.
PARAMETERS: p_list RADIOBUTTON GROUP ____(3)____ DEFAULT 'X',
            p_alv  RADIOBUTTON GROUP g1.
PARAMETERS p_test AS ____(4)____.
INITIALIZATION.
  APPEND VALUE #( sign = ____(5)____ option = 'EQ' low = 'LH' ) TO s_carr.
AT SELECTION-SCREEN ON ____(6)____ FOR s_carr-low.
  PERFORM f4_carrid.
```
(2) 범위 테이블 r_carr = { I EQ 'AA', I BT 'JL'~'LH', I CP 'U*', E EQ 'JL' }, 데이터 AA, AZ, JL, LH, QF, UA를 `IF lv_carr IN r_carr`로 거를 때 출력은? `CLEAR r_carr` 후에는 몇 개? `E EQ 'JL'` 한 줄만 있으면? 평가 규칙과 성능 함정을 쓰시오.
(3) 라디오 버튼으로 "PC 파일"이면 `p_pcfile`만, "서버 파일"이면 `p_asfile`만 즉시 보이게 하는 빈칸을 채우시오.
```abap
PARAMETERS: p_local RADIOBUTTON GROUP src DEFAULT 'X' ____(a)____ ucom,
            p_appl  RADIOBUTTON GROUP src.
PARAMETERS: p_pcfile TYPE string MODIF ID ____(b)____,
            p_asfile TYPE string MODIF ID app.
____(c)____.
  LOOP AT SCREEN.
    CASE screen-____(d)____.
      WHEN 'LOC'. screen-active = COND #( WHEN p_local = abap_true THEN '1' ELSE '0' ).
      WHEN 'APP'. screen-active = COND #( WHEN p_appl  = abap_true THEN '1' ELSE '0' ).
    ENDCASE.
    ____(e)____.
  ENDLOOP.
```
(4) p_carr F4에 SCARR 목록을 띄우고 고른 CARRID를 넣는 FM 호출의 빈칸을 채우시오: `CALL FUNCTION '(가)' EXPORTING retfield = '(나)' dynpprog = lv_repid dynpnr = lv_dynnr dynprofield = 'P_CARR' value_org = '(다)' TABLES value_tab = lt_f4`. sy-repid·sy-dynnr을 지역 변수로 복사하는 이유는?
(5) 변형(Variant)의 용도, 필드별 옵션, 배치 잡에서 "어제 날짜"를 자동으로 넣는 방법(선택 변수 유형 D와 T), 시스템 변형 이름 규칙과 일반 변형의 전송 방법을 쓰시오.
(6) `ZHC_SEATS` 전체를 작성하시오. 선택 화면: `s_carr`, `s_date`, 라디오 `p_sum`(요약, 기본)/`p_det`(상세), 상세일 때만 보이는 `p_pct`(TYPE i, 기본 80, 화면 그룹 DET, 즉시 전환, 0~100 검증). 요약: 항공사별 편수·최대 좌석 합·점유 좌석 합·평균 점유율(소수 1자리). 상세: 항공편마다 점유율, `p_pct` 이상이면 COL_NEGATIVE. 점유율 = SEATSOCC / SEATSMAX × 100, SEATSMAX = 0 제외.
(7) (6)에서 `seatsocc * 100 / seatsmax`를 그대로 쓰면 생기는 문제와 해결, `screen-active = '0'`과 `screen-invisible = '1'`의 차이를 쓰시오.

<details><summary>정답·해설</summary>

**(1)** (1) `OBLIGATORY` (2) `NO INTERVALS` (3) `g1` (4) `CHECKBOX` (5) `'I'` (6) `VALUE-REQUEST`. SELECT-OPTIONS는 헤더 라인이 있는 범위 테이블을 만든다. 행: `SIGN`(I 포함 / E 제외), `OPTION`(EQ, NE, BT, NB, CP, NP, GT, GE, LT, LE), `LOW`, `HIGH`. `NO INTERVALS`는 HIGH 칸을 숨기고 `NO-EXTENSION`은 다중 선택 버튼을 없앤다. 라디오 버튼 그룹 이름은 최대 4자, 같은 그룹 안에서 하나만 선택된다. `TYPE RANGE OF`로 같은 구조를 프로그램 안에서 만들 수 있다(옛 `RANGES`는 헤더 라인 포함, 비권장).
**(2)** `AA LH UA `. I 행들은 OR로 묶고 그 결과에서 E 행에 해당하는 값을 뺀다. AA: EQ 일치. AZ: 'JL'~'LH' 밖, 'U*' 불일치. JL: BT에 들지만 E로 제외. LH: BT 상한 포함(경계값 포함). QF: 어느 I에도 없음. UA: CP 'U*' 일치. CLEAR 후에는 6개 전부: 빈 범위 테이블의 `IN`은 항상 참이며 `WHERE carrid IN @r_carr`도 전체를 읽는다(빈 선택 조건 = 전체, "필수 조건이 비어 전 건 조회" 성능 사고의 원인). E 행만 있으면 "I 없음 = 전체"에서 JL만 빼서 AA, AZ, LH, QF, UA.
**(3)** (a) `USER-COMMAND` (b) `loc`(대소문자 무관, 화면 그룹 값은 대문자 `LOC`로 저장) (c) `AT SELECTION-SCREEN OUTPUT` (d) `group1` (e) `MODIFY SCREEN`. USER-COMMAND가 없으면 라디오 버튼을 눌러도 PAI가 일어나지 않아 Enter까지 화면이 안 바뀐다(그룹의 첫 버튼에만 붙인다). MODIF ID 3글자 값은 SCREEN 구조 `group1`에 대문자로 들어오며, SELECT-OPTIONS는 LOW·HIGH·텍스트·다중 선택 버튼이 모두 같은 그룹이라 한 번에 숨겨진다. 7.40 이후 `LOOP AT SCREEN INTO DATA(ls)` + `MODIFY SCREEN FROM ls`도 가능. 입력만 막으려면 `input = '0'`.
**(4)** (가) `F4IF_INT_TABLE_VALUE_REQUEST` (나) `CARRID` (다) `S`. retfield는 value_tab에서 돌려줄 열 이름(대문자). dynpprog/dynpnr/dynprofield를 주면 선택 값이 화면 필드에 바로 들어가고, 아니면 RETURN_TAB으로 받는다. value_org 'S'는 구조체 단위(한 행 = 한 줄), 'C'는 셀 단위로 한 열씩. 시스템 필드는 FM 안에서 값이 바뀔 수 있어(참조 전달) 지역 변수로 고정하는 것이 안전하다.
**(5)** 선택 화면 입력값을 이름 붙여 저장했다가 다시 불러오는 기능으로 반복 실행과 배치 잡 스텝(프로그램 + 변형)에 쓴다(SE38 → Goto → Variants 또는 선택 화면 저장 버튼). 필드별 옵션: Protect field, Hide field, Required field, Save field without values, Selection variable. 변형 자체 옵션: "Only for background processing", "Protect variant". 선택 변수 유형 D: 동적 날짜 계산(현재 날짜 - 1 등), 유형 T: 테이블 TVARVC(STVARV/STVARVC에서 유지) 값. 시스템 변형은 `CUS&` 또는 `SAP&`로 시작해 자동 전송되고, 일반 변형은 클라이언트 종속이라 SE38 → Utilities → Transport Variants로 전송한다.
**(6)**
```abap
REPORT zhc_seats NO STANDARD PAGE HEADING.
TABLES sflight.
SELECT-OPTIONS: s_carr FOR sflight-carrid,
                s_date FOR sflight-fldate.
PARAMETERS: p_sum RADIOBUTTON GROUP g1 DEFAULT 'X' USER-COMMAND rad,
            p_det RADIOBUTTON GROUP g1,
            p_pct TYPE i DEFAULT 80 MODIF ID det.

AT SELECTION-SCREEN OUTPUT.
  LOOP AT SCREEN.
    IF screen-group1 = 'DET'.
      screen-active = COND #( WHEN p_det = abap_true THEN '1' ELSE '0' ).
      MODIFY SCREEN.
    ENDIF.
  ENDLOOP.

AT SELECTION-SCREEN.
  IF p_det = abap_true AND ( p_pct < 0 OR p_pct > 100 ).
    MESSAGE '기준은 0~100 사이여야 합니다' TYPE 'E'.
  ENDIF.

START-OF-SELECTION.
  SELECT carrid, connid, fldate, seatsmax, seatsocc
    FROM sflight
    WHERE carrid IN @s_carr AND fldate IN @s_date AND seatsmax > 0
    ORDER BY carrid, connid, fldate
    INTO TABLE @DATA(lt_fl).
  IF lt_fl IS INITIAL.
    MESSAGE '데이터가 없습니다' TYPE 'S' DISPLAY LIKE 'E'.
    RETURN.
  ENDIF.

  IF p_sum = abap_true.
    WRITE: / 'ID', 8 '편수', 18 '최대좌석', 32 '점유좌석', 46 '평균점유율(%)'.
    ULINE.
    LOOP AT lt_fl INTO DATA(ls_fl)
         GROUP BY ls_fl-carrid ASCENDING INTO DATA(lv_carrid).
      DATA(lv_cnt) = 0.
      DATA(lv_max) = 0.
      DATA(lv_occ) = 0.
      LOOP AT GROUP lv_carrid INTO DATA(ls_m).
        lv_cnt += 1.
        lv_max += ls_m-seatsmax.
        lv_occ += ls_m-seatsocc.
      ENDLOOP.
      DATA(lv_avg) = CONV decfloat34( lv_occ ) * 100 / lv_max.
      WRITE: / lv_carrid, 8 lv_cnt, 18 lv_max, 32 lv_occ,
              46 |{ lv_avg DECIMALS = 1 }|.
    ENDLOOP.
  ELSE.
    WRITE: / 'ID', 6 '노선', 12 '비행일', 26 '점유율(%)'.
    ULINE.
    LOOP AT lt_fl INTO ls_fl.
      DATA(lv_pct) = CONV decfloat34( ls_fl-seatsocc ) * 100 / ls_fl-seatsmax.
      IF lv_pct >= p_pct.
        FORMAT COLOR COL_NEGATIVE.
      ELSE.
        FORMAT COLOR OFF.
      ENDIF.
      WRITE: / ls_fl-carrid, 6 ls_fl-connid, 12 ls_fl-fldate,
              26 |{ lv_pct DECIMALS = 1 }|.
    ENDLOOP.
    FORMAT RESET.
  ENDIF.
```
채점(100점): RADIOBUTTON GROUP + DEFAULT + USER-COMMAND 15 / MODIF ID + AT SELECTION-SCREEN OUTPUT의 LOOP AT SCREEN·MODIFY SCREEN 20 / 입력값 검증 5 / SELECT(SEATSMAX > 0) + 빈 결과 처리 15 / 요약 집계(GROUP BY, control break, SELECT 집계 중 아무거나) 20 / 상세 점유율(정수 나눗셈 함정 회피) + 조건부 색상 20 / 소수 1자리 5. 라디오 버튼에 USER-COMMAND가 없으면 `p_pct`가 F8 때까지 그대로 보이는 것이 핵심 감점 포인트다. 요약은 `SELECT carrid, COUNT(*), SUM( seatsmax ), SUM( seatsocc ) ... GROUP BY carrid`로 DB에서 집계해도 만점.
**(7)** 피연산자가 모두 정수형이면 계산형이 `i`라 나눗셈 결과가 정수로 반올림된다. 피연산자 하나를 `CONV decfloat34( ... )`로 바꾸면 계산형이 decfloat34가 되어 소수가 유지된다(계산형은 식의 피연산자 중 가장 "큰" 타입). `screen-active = '0'`은 필드를 숨기고 입력도 막지만, `screen-invisible = '1'`만 쓰면 입력은 가능한 채 "*"로 가려진다.

</details>

---

### B-011. 인터랙티브 리스트: HIDE·sy-lsind·READ LINE·페이지 이벤트 [코드] ★★★
<!-- src: IB-032, IB-033, IB-034, IB-035, IB-036, IB-037, IB-038, MX-007, TC-107, IB-046, HC-005 -->
다음 리포트는 항공사를 더블클릭하면 노선 목록을 보여 주려 한다. 테스트하니 (a) 클릭한 줄의 바로 윗줄 항공사 노선이 나오고, (b) 첫 줄이나 머리글을 누르면 빈 리스트 또는 엉뚱한 리스트가 나오며, (c) 상세 리스트 머리글이 안 보이고, (d) 상세 리스트를 계속 클릭하면 같은 리스트가 쌓이다가 덤프가 난다.

```abap
REPORT zhc_bug_inter NO STANDARD PAGE HEADING.
DATA gv_carrid TYPE scarr-carrid.

START-OF-SELECTION.
  SELECT carrid, carrname FROM scarr INTO TABLE @DATA(lt_carr).
  LOOP AT lt_carr INTO DATA(ls_carr).
    HIDE gv_carrid.
    gv_carrid = ls_carr-carrid.
    WRITE: / ls_carr-carrid, ls_carr-carrname.
  ENDLOOP.

AT LINE-SELECTION.
  SELECT connid, cityfrom, cityto FROM spfli
    WHERE carrid = @gv_carrid
    INTO TABLE @DATA(lt_conn).
  LOOP AT lt_conn INTO DATA(ls_conn).
    WRITE: / ls_conn-connid, ls_conn-cityfrom, ls_conn-cityto.
  ENDLOOP.

TOP-OF-PAGE.
  WRITE: / '노선 목록'.
  ULINE.
```

(1) 클래식 리포트와 인터랙티브 리포트의 차이, 드릴다운 리포트의 예를 쓰시오.
(2) 증상 (a)~(d)의 원인을 각각 쓰고 고친 코드를 쓰시오. 부가로 고칠 점도 쓰시오.
(3) 인터랙티브 리스트 이벤트 4가지와 발생 시점, 선택한 줄의 데이터를 얻는 세 방법(HIDE, READ LINE, GET CURSOR)을 비교하시오. 키 값 전달에 HIDE가 안전한 이유는?
(4) 아래 프로그램에서 (a) 기본 리스트 줄 더블클릭 (b) 새 리스트 첫 줄 더블클릭 (c) F3 한 번 (d) 보이는 리스트 첫 줄 더블클릭을 차례로 했다. (a)(b)(d)의 sy-lsind·sy-listi와 (c) 직후 보이는 리스트 번호를 쓰시오.
```abap
REPORT zib_lsind NO STANDARD PAGE HEADING.
START-OF-SELECTION.
  WRITE / 'Basic list'.
AT LINE-SELECTION.
  WRITE: / 'LSIND =', sy-lsind, 'LISTI =', sy-listi.
```
(5) SPFLI 노선 기본 리스트에서 더블클릭하면 SFLIGHT 세부 리스트를 보이는 코드의 빈칸과 물음에 답하시오.
```abap
  LOOP AT gt_spfli INTO gs_spfli.
    WRITE: / gs_spfli-carrid, gs_spfli-connid, gs_spfli-cityfrom, gs_spfli-cityto.
    ____(1)____: gs_spfli-carrid, gs_spfli-connid.
  ENDLOOP.
  CLEAR gs_spfli.
____(2)____.
  GET CURSOR ____(3)____ lv_fname.
  CHECK gs_spfli-carrid IS NOT INITIAL.
  CASE ____(4)____.
    WHEN 1. " SFLIGHT 조회·출력
    WHEN OTHERS. MESSAGE '더 이상 세부 리스트가 없습니다' TYPE 'S'.
  ENDCASE.
```
그리고 기본 리스트 아래로 만들 수 있는 세부 리스트는 최대 몇 단계인가?
(6) 옳지 않은 것은? ① 기본 리스트 번호는 0, 상세 리스트는 최대 20개 ② sy-listi는 이벤트가 발생한 리스트 번호, sy-lilli는 선택한 줄 번호 ③ sy-lisel에는 선택한 줄 내용이 문자열로 ④ 함수 코드 PICK은 AT LINE-SELECTION을 발생 ⑤ 상세 리스트의 페이지 헤더는 일반 TOP-OF-PAGE에서 출력.
(7) `REPORT zib_page LINE-SIZE 80 LINE-COUNT 65(3).`에 대해 옳지 않은 것은? ① 한 페이지 65줄 중 마지막 3줄이 END-OF-PAGE용 ② TOP-OF-PAGE는 새 페이지의 첫 출력 문장에서 발생 ③ `NO STANDARD PAGE HEADING`이면 표준 헤더가 없다 ④ 마지막 페이지가 다 차지 않았더라도 END-OF-PAGE가 반드시 한 번 실행된다 ⑤ `NEW-PAGE`는 END-OF-PAGE를 발생시키지 않는다. 바닥글 이벤트에 필요한 REPORT 문 지정은?
(8) 항공사 목록 각 줄 앞에 체크박스를 출력하고 버튼 PROC를 누르면 체크된 항공사만 출력하는 빈칸을 채우시오: `WRITE: / gv_chk (1), gv_carr. HIDE gv_carr.` / `AT USER-COMMAND. CASE (2). WHEN 'PROC'. ... DO. (3) gv_line FIELD VALUE gv_chk. IF sy-subrc <> 0. EXIT. ENDIF. ...`. 헤더가 있을 때 주의점과 체크 값을 리스트에 다시 반영하는 문장은?

<details><summary>정답·해설</summary>

**(1)** 클래식: 선택 화면 → 조회 → 기본 리스트(basic list) 하나를 출력하고 끝, 상호작용 이벤트 없음. 인터랙티브: 기본 리스트에서 더블클릭·버튼으로 AT LINE-SELECTION, AT USER-COMMAND가 발생해 상세 리스트(secondary list)를 최대 20단계까지 만든다. 드릴다운: 요약 → 상세. 예: SCARR → 더블클릭 → SPFLI → SFLIGHT → SBOOK, 전표 번호 더블클릭 → `CALL TRANSACTION 'FB03'`. ALV에서는 HOTSPOT 클릭이나 DOUBLE_CLICK 이벤트로 같은 동작을 구현한다. 리스트 기반은 레거시지만 클래식 필기에서 여전히 출제된다.
**(2)** (a) HIDE가 WRITE보다 먼저 실행되어 이전 줄에 값이 저장되고, 게다가 대입 전 값(이전 반복의 항공사)을 숨김 → 대입 → WRITE → HIDE 순서. (b) 첫 반복의 HIDE는 머리글 줄에 초기값을 저장하고, 리스트 생성 후 CLEAR가 없어 HIDE 없는 줄 클릭 시 마지막 값이 남음 → 루프 뒤 `CLEAR gv_carrid.`, 이벤트 처음 `CHECK gv_carrid IS NOT INITIAL.` (c) TOP-OF-PAGE는 기본 리스트에만 실행되고 '노선 목록'이 기본 리스트 머리글로 잘못 나옴 → 기본 리스트용 TOP-OF-PAGE와 `TOP-OF-PAGE DURING LINE-SELECTION` 분리. (d) sy-lsind 확인 없이 상세 리스트 줄을 클릭해도 같은 이벤트가 다시 돌고 gv_carrid가 남아 같은 리스트가 2, 3, ... 단계로 생성, 20단계를 넘으면 런타임 오류 → `CHECK sy-lsind = 1.`(또는 CASE sy-lsind) + 상세 리스트 후 CLEAR. 부가: SELECT에 ORDER BY 없음(순서 보장 안 됨), 노선이 없을 때 안내 없음.
```abap
REPORT zhc_bug_inter NO STANDARD PAGE HEADING.
DATA gv_carrid TYPE scarr-carrid.

START-OF-SELECTION.
  SELECT carrid, carrname FROM scarr ORDER BY carrid INTO TABLE @DATA(lt_carr).
  LOOP AT lt_carr INTO DATA(ls_carr).
    gv_carrid = ls_carr-carrid.
    WRITE: / ls_carr-carrid, ls_carr-carrname.
    HIDE gv_carrid.
  ENDLOOP.
  CLEAR gv_carrid.

TOP-OF-PAGE.
  WRITE / '항공사 목록'.
  ULINE.

AT LINE-SELECTION.
  CHECK sy-lsind = 1 AND gv_carrid IS NOT INITIAL.
  SELECT connid, cityfrom, cityto FROM spfli
    WHERE carrid = @gv_carrid ORDER BY connid
    INTO TABLE @DATA(lt_conn).
  IF lt_conn IS INITIAL.
    MESSAGE '노선이 없습니다' TYPE 'S'.
  ENDIF.
  LOOP AT lt_conn INTO DATA(ls_conn).
    WRITE: / ls_conn-connid, ls_conn-cityfrom, ls_conn-cityto.
  ENDLOOP.
  CLEAR gv_carrid.

TOP-OF-PAGE DURING LINE-SELECTION.
  WRITE: / gv_carrid, '노선 목록'.
  ULINE.
```
`TOP-OF-PAGE DURING LINE-SELECTION`은 상세 리스트의 첫 WRITE 때 실행되므로 그 시점의 gv_carrid(CLEAR 전)를 머리글에 쓸 수 있다. `CHECK sy-lsind = 1`이 거짓이면 이벤트를 빠져나가고 출력이 없어 새 리스트가 생기지 않는다. 채점: 원인 4개 각 20점, 수정 코드 20점.
**(3)** `AT LINE-SELECTION`: 함수 코드 PICK(더블클릭, F2). `AT USER-COMMAND`: GUI 상태의 사용자 함수 코드. `AT PFnn`: 기능 키(obsolete). `TOP-OF-PAGE DURING LINE-SELECTION`: 상세 리스트 새 페이지 헤더.

| 방법 | 동작 |
|---|---|
| `HIDE f` | WRITE 직후 현재 줄 번호와 f 값을 HIDE 영역에 저장, 줄을 고르면 f로 자동 복원. 화면에 안 보이는 키 값도 저장 가능 |
| `READ LINE n [FIELD VALUE f]` | n번째 줄에 출력된 값(체크박스 등 사용자가 바꾼 값 포함)을 변수에 읽음. HIDE 값도 복원. 여러 줄을 루프로 읽을 때 |
| `GET CURSOR FIELD name VALUE val` | 커서가 놓인 필드 이름과 출력 값. 같은 줄의 어느 열을 클릭했는지 구분 |

READ LINE·GET CURSOR는 편집 마스크·변환이 적용된 출력 문자열이라 화면 위치에 의존하므로 키 값은 HIDE가 안전하다. sy-lisel에는 선택한 줄 전체 내용이 있다.
**(4)** (a) LSIND = 1, LISTI = 0 (b) LSIND = 2, LISTI = 1 (c) 리스트 1 (d) LSIND = 2, LISTI = 1. 기본 리스트는 0, AT LINE-SELECTION이 시작될 때 sy-lsind는 "지금 만들 리스트 번호"로 1 증가하고 sy-listi는 "이벤트가 발생한 리스트 번호"다. F3은 한 단계 위로 돌아가며 리스트 2는 버려지고, (d)에서 리스트 1에서 다시 선택했으므로 리스트 2가 새로 만들어진다.
**(5)** (1) `HIDE` (2) `AT LINE-SELECTION` (3) `FIELD` (4) `sy-lsind`. 최대 20단계(sy-lsind 1~20). HIDE는 방금 출력한 줄 번호와 함께 값을 숨김 영역에 저장하고, 줄을 고르면 원래 변수에 다시 채운다. 루프 뒤 `CLEAR gs_spfli`가 없으면 헤더나 빈 줄을 눌렀을 때 마지막 행 값이 남아 엉뚱한 리스트가 나오므로 `CHECK ... IS NOT INITIAL`과 짝을 이룬다. `GET CURSOR FIELD`는 커서가 놓인 필드 이름을 돌려준다(`VALUE`로 값도). 단계별 처리는 `IF/CASE sy-lsind`로 나눈다.
**(6)** ⑤. 상세 리스트 헤더는 `TOP-OF-PAGE DURING LINE-SELECTION`. 20개 넘게 만들려 하면 런타임 오류. sy-ucomm에는 함수 코드가 들어 있다.
**(7)** ④. END-OF-PAGE는 페이지가 예약 영역까지 차서 넘어갈 때만 발생하고 마지막 페이지가 덜 차면 실행되지 않는다(바닥글이 마지막 페이지에 안 나오는 이유). LINE-COUNT에 괄호 숫자가 없으면 END-OF-PAGE는 아예 발생하지 않으므로 `LINE-COUNT 65(3)`처럼 예약 행 수를 지정해야 한다. LINE-SIZE는 한 줄 폭(열 수). 행을 선택하면 sy-lisel에 행 내용, sy-lilli에 행 번호가 들어온다.
**(8)** (1) `AS CHECKBOX` (2) `sy-ucomm` (3) `READ LINE`. `WRITE ... AS CHECKBOX`는 입력 가능한 체크박스를 출력하고, `READ LINE n FIELD VALUE f`는 n번째 줄에 출력된(사용자가 바꾼) 값을 읽으며 그 줄의 HIDE 값(gv_carr)도 복원한다. 줄이 없으면 sy-subrc ≠ 0이라 루프가 끝난다. `NO STANDARD PAGE HEADING`이라 1번 줄부터 데이터지만, 헤더가 있으면 헤더 줄 수만큼 건너뛰어야 한다. 체크 값을 리스트에 다시 반영하려면 `MODIFY LINE`.

</details>

---

### B-012. 컨트롤 브레이크 집계: AT NEW·AT END OF·SUM과 GROUP BY [작성] ★★★
<!-- src: TC-109, HC-006, HC-007, HC-008, MX-035, IB-045 -->
항공사·노선별 집계 리포트를 클래식 컨트롤 레벨과 GROUP BY 루프로 만든다.

(1) 다음 코드 실행 후 `out`을 쓰시오.
```abap
TYPES: BEGIN OF ty_row,
         carrid TYPE c LENGTH 3,
         connid TYPE n LENGTH 4,
         price  TYPE i,
       END OF ty_row.
DATA: itab TYPE STANDARD TABLE OF ty_row WITH EMPTY KEY,
      wa   TYPE ty_row,
      out  TYPE string.
itab = VALUE #( ( carrid = 'AA' connid = '0017' price = 100 )
                ( carrid = 'AA' connid = '0017' price = 200 )
                ( carrid = 'AA' connid = '0064' price = 50 )
                ( carrid = 'LH' connid = '0400' price = 300 ) ).
LOOP AT itab INTO wa.
  AT NEW carrid.      out = out && |[{ wa-carrid }]|.          ENDAT.
  AT END OF connid.   SUM. out = out && |{ wa-connid }:{ wa-price };|. ENDAT.
  AT LAST.            SUM. out = out && |T{ wa-price }|.        ENDAT.
ENDLOOP.
```
(2) 다음 코드는 항공사별 예약 금액 합계를 출력하려 한다. 잘못된 점을 6개 이상 찾고 고치시오.
```abap
TYPES: BEGIN OF ty_b,
         fldate    TYPE sbook-fldate,
         carrid    TYPE sbook-carrid,
         connid    TYPE sbook-connid,
         forcuram  TYPE sbook-forcuram,
         forcurkey TYPE sbook-forcurkey,
       END OF ty_b.
DATA: gt TYPE STANDARD TABLE OF ty_b, gs TYPE ty_b, gv_total TYPE sbook-forcuram.
START-OF-SELECTION.
  SELECT fldate, carrid, connid, forcuram, forcurkey FROM sbook
    WHERE carrid IN @s_carr INTO TABLE @gt.
  LOOP AT gt INTO gs WHERE forcuram > 0.
    AT NEW carrid.
      WRITE: / gs-carrid, gs-connid.
    ENDAT.
    gv_total = gv_total + gs-forcuram.
    AT END OF carrid.
      WRITE: / '합계', gv_total, gs-forcurkey.
    ENDAT.
  ENDLOOP.
```
(3) 리포트 `ZHC_CTRL_BREAK`를 작성하시오. SBOOK에서 취소되지 않은 예약을 읽어 항공사 머리글, 노선별 "예약 n건 금액 통화", 항공사 소계, 마지막에 전체 예약 건수(통화가 섞이므로 건수만)를 출력한다. 선택화면 `s_carr`, `s_date`. 금액은 LOCCURAM/LOCCURKEY. 반드시 AT NEW, AT END OF, AT LAST, SUM을 쓰고 건수는 별도 카운터 없이 SUM으로 구한다.
(4) (3)과 같은 출력을 control break 없이 `LOOP AT ... GROUP BY`(필요하면 `LOOP AT GROUP`, `REDUCE`)로 작성하시오(START-OF-SELECTION 이후만, 내부 테이블 정렬 금지).
(5) 시험형 작성: SFLIGHT에서 CARRID, CONNID, FLDATE, SEATSMAX, SEATSOCC를 읽어 항공편마다 노선·날짜·점유 좌석·점유율(%)을 출력하고, 노선 소계·항공사 소계·총계(점유 좌석 합)를 낸다. 데이터가 없으면 S 메시지를 오류처럼 보이고 선택 화면으로 돌아간다(4점 배점 기준 포함).
(6) EXTRACT 데이터셋이란 무엇인가? FIELD-GROUPS / INSERT / EXTRACT / SORT / LOOP 사용 순서와 제약, 현재 권장 대안을 쓰시오.

<details><summary>정답·해설</summary>

**(1)** `[AA]0017:300;0064:50;[LH]0400:300;T650`. 1행: carrid 새로 시작 → `[AA]`, 다음 행도 AA/0017이라 그룹 끝 아님. 2행: 다음 행 connid가 0064 → (AA, 0017) 끝, SUM 100 + 200 = 300. 3행: 다음 행에서 carrid가 바뀌므로(왼쪽 필드 변경도 그룹 종료) AT END OF connid → `0064:50;`. 4행: `[LH]`, 마지막 행이라 `0400:300;`, AT LAST 전체 합 650 → `T650`. AT NEW f / AT END OF f는 f 또는 f보다 왼쪽 컴포넌트가 바뀔 때 실행되므로 해당 필드 순서대로 정렬돼 있어야 한다. c 타입은 문자열 템플릿에서 뒤 공백이 빠지고 n 타입은 앞 0이 그대로 나온다.
**(2)**

| # | 문제 | 수정 |
|---|---|---|
| 1 | carrid 왼쪽에 fldate가 있어 날짜만 바뀌어도 AT NEW/AT END OF carrid 실행 | 구조를 carrid, connid, ... 순으로 |
| 2 | SORT 없음, 같은 항공사가 흩어지면 그룹이 여러 번 | `SORT gt BY carrid connid.` |
| 3 | LOOP에 WHERE 사용, 그룹 경계 행이 조건에서 빠지면 AT 블록이 실행되지 않음 | WHERE를 SELECT로 옮기거나 미리 DELETE |
| 4 | AT NEW carrid 안의 gs-connid는 제어 키 오른쪽이라 초기값 `0000` | 머리글에는 carrid만 |
| 5 | gv_total을 항공사마다 초기화하지 않아 누적 | SUM을 쓰거나 AT NEW에서 CLEAR |
| 6 | AT END OF 안의 gs-forcurkey는 `*`로 바뀜. FORCURAM은 예약별 결제 통화라 통화가 섞여 합산 무의미 | loccuram/loccurkey 사용, 통화는 AT 블록 밖에서 보관 |
| 7 | 취소 예약 포함 | `AND cancelled = @space` |
| 8 | 금액을 CURRENCY 없이 WRITE | `WRITE ... CURRENCY gv_curr` |

```abap
TYPES: BEGIN OF ty_b,
         carrid    TYPE sbook-carrid,
         connid    TYPE sbook-connid,
         fldate    TYPE sbook-fldate,
         loccuram  TYPE sbook-loccuram,
         loccurkey TYPE sbook-loccurkey,
       END OF ty_b.
DATA: gt TYPE STANDARD TABLE OF ty_b, gs TYPE ty_b, gv_curr TYPE sbook-loccurkey.
START-OF-SELECTION.
  SELECT carrid, connid, fldate, loccuram, loccurkey FROM sbook
    WHERE carrid IN @s_carr AND loccuram > 0 AND cancelled = @space
    INTO TABLE @gt.
  SORT gt BY carrid connid fldate.
  LOOP AT gt INTO gs.
    AT NEW carrid.
      WRITE: / gs-carrid.
    ENDAT.
    gv_curr = gs-loccurkey.
    AT END OF carrid.
      SUM.
      WRITE: / '합계', gs-loccuram CURRENCY gv_curr, gv_curr.
    ENDAT.
  ENDLOOP.
```
채점: 항목당 10점(최대 80) + 수정 코드 20. 키워드 문서는 WHERE에 대해 "조건과 무관하게 모든 행으로 그룹 변경을 판단하고, 그룹 변경 행이 조건 때문에 읽히지 않으면 해당 블록은 실행되지 않는다"고 설명한다. 면접 단골 "control break 주의점 세 가지"(정렬, 필드 순서, 오른쪽 필드 값 변화)가 모두 들어 있다.
**(3)**
```abap
REPORT zhc_ctrl_break NO STANDARD PAGE HEADING.
TABLES sbook.
SELECT-OPTIONS: s_carr FOR sbook-carrid,
                s_date FOR sbook-fldate.
TYPES: BEGIN OF ty_book,
         carrid    TYPE sbook-carrid,      " 제어 키를 맨 왼쪽부터
         connid    TYPE sbook-connid,
         fldate    TYPE sbook-fldate,
         loccuram  TYPE sbook-loccuram,    " SUM 대상
         cnt       TYPE i,                 " 건당 1 → SUM하면 건수
         loccurkey TYPE sbook-loccurkey,
       END OF ty_book.
DATA: gt_book TYPE STANDARD TABLE OF ty_book WITH EMPTY KEY,
      gs_book TYPE ty_book,
      gv_curr TYPE sbook-loccurkey.

START-OF-SELECTION.
  SELECT carrid, connid, fldate, loccuram, 1 AS cnt, loccurkey
    FROM sbook
    WHERE carrid IN @s_carr AND fldate IN @s_date AND cancelled = @space
    INTO TABLE @gt_book.
  IF gt_book IS INITIAL.
    MESSAGE '데이터가 없습니다' TYPE 'S' DISPLAY LIKE 'E'.
    RETURN.
  ENDIF.
  SORT gt_book BY carrid connid fldate.

  LOOP AT gt_book INTO gs_book.
    AT NEW carrid.
      FORMAT COLOR COL_GROUP.
      WRITE: / '항공사:', gs_book-carrid.
      FORMAT RESET.
    ENDAT.
    gv_curr = gs_book-loccurkey.           " AT 블록 밖에서 보관
    AT END OF connid.
      SUM.
      WRITE: /5 gs_book-connid, 17 '예약', gs_book-cnt, '건',
             35 gs_book-loccuram CURRENCY gv_curr, gv_curr.
    ENDAT.
    AT END OF carrid.
      SUM.
      FORMAT COLOR COL_TOTAL.
      WRITE: / '소계', 17 '예약', gs_book-cnt, '건',
             35 gs_book-loccuram CURRENCY gv_curr, gv_curr.
      FORMAT RESET.
      ULINE.
    ENDAT.
    AT LAST.
      SUM.
      WRITE: / '전체 예약 건수:', gs_book-cnt.
    ENDAT.
  ENDLOOP.
```
채점(100점): 제어 키를 왼쪽부터 15 / SELECT(취소 제외, 선택 조건) + 빈 결과 15 / 제어 키 순 SORT 15 / AT NEW 머리글 10 / AT END OF connid + SUM 15 / AT END OF carrid 소계 + SUM 10 / AT LAST 5 / 통화 처리(블록 밖 보관, CURRENCY) 10 / cnt = 1 필드로 건수 5. AT NEW/AT END OF 블록 안에서는 제어 키 오른쪽 컴포넌트가 문자형은 `*`, 나머지는 초기값으로 바뀌므로 오른쪽의 loccurkey를 블록 안에서 읽으면 안 되고, ENDAT을 지나면 현재 행 값이 돌아온다. SUM은 그룹 안 모든 숫자형 컴포넌트(i, p, f, decfloat)를 합해 작업 영역에 넣으며 CURR 필드는 내부적으로 p라 합산된다. `1 AS cnt` 리터럴은 7.40 SP08부터 가능하고, 낮으면 SELECT 후 `LOOP ... ASSIGNING`으로 1을 넣는다. control break와 LOOP WHERE는 같이 쓰지 않는다.
**(4)**
```abap
TYPES: BEGIN OF ty_book,
         carrid    TYPE sbook-carrid,
         connid    TYPE sbook-connid,
         fldate    TYPE sbook-fldate,
         loccuram  TYPE sbook-loccuram,
         loccurkey TYPE sbook-loccurkey,
       END OF ty_book.
DATA: gt_book  TYPE STANDARD TABLE OF ty_book WITH EMPTY KEY,
      gv_c_cnt TYPE i,
      gv_c_sum TYPE sbook-loccuram,
      gv_curr  TYPE sbook-loccurkey.

START-OF-SELECTION.
  SELECT carrid, connid, fldate, loccuram, loccurkey FROM sbook
    WHERE carrid IN @s_carr AND fldate IN @s_date AND cancelled = @space
    INTO TABLE @gt_book.

  LOOP AT gt_book INTO DATA(ls_book)
       GROUP BY ls_book-carrid ASCENDING
       INTO DATA(lv_carrid).
    WRITE: / '항공사:', lv_carrid.
    CLEAR: gv_c_cnt, gv_c_sum.
    LOOP AT GROUP lv_carrid INTO DATA(ls_mem)
         GROUP BY ( connid = ls_mem-connid
                    curr   = ls_mem-loccurkey
                    cnt    = GROUP SIZE )
         ASCENDING
         INTO DATA(ls_conn).
      DATA(lv_sum) = REDUCE sbook-loccuram(
                       INIT s = CONV sbook-loccuram( 0 )
                       FOR m IN GROUP ls_conn
                       NEXT s = s + m-loccuram ).
      WRITE: /5 ls_conn-connid, 17 '예약', ls_conn-cnt, '건',
             35 lv_sum CURRENCY ls_conn-curr, ls_conn-curr.
      gv_c_cnt += ls_conn-cnt.
      gv_c_sum += lv_sum.
      gv_curr   = ls_conn-curr.
    ENDLOOP.
    WRITE: / '소계', 17 '예약', gv_c_cnt, '건',
             35 gv_c_sum CURRENCY gv_curr, gv_curr.
    ULINE.
  ENDLOOP.
  DATA(lv_all) = lines( gt_book ).
  WRITE: / '전체 예약 건수:', lv_all.
```
채점(100점): 바깥 `LOOP AT ... GROUP BY ... ASCENDING INTO`(정렬 불필요 이해) 25 / 안쪽 `LOOP AT GROUP ... GROUP BY` 25 / `GROUP SIZE`(또는 카운터) 10 / `REDUCE ... FOR m IN GROUP`(또는 LOOP AT GROUP 합산) 20 / 소계 누적과 그룹마다 초기화 10 / 전체 건수 10. GROUP BY는 테이블 순서와 무관하게 같은 키를 묶고 ASCENDING이면 키 순으로 처리되어 SORT가 필요 없다(SORT 없이 control break를 쓰면 같은 키가 여러 그룹으로 쪼개지는 것과 대조). `INTO DATA(lv_carrid)`는 그룹 키 바인딩이라 본문에서 ls_book이 채워지지 않으므로 멤버는 LOOP AT GROUP으로 읽는다(대표 바인딩은 INTO 없이 GROUP BY만 쓰고 `LOOP AT GROUP ls_book`). 통화는 항공사마다 하나라 그룹 키에 넣어도 더 쪼개지지 않는다. `INIT s = 0`이면 s가 i라 소수가 잘리므로 `CONV sbook-loccuram( 0 )`.
**(5)**
```abap
REPORT zmx_035.
DATA gv_carrid TYPE s_carr_id.
SELECT-OPTIONS s_carr FOR gv_carrid.
TYPES: BEGIN OF ty_fl,
         carrid   TYPE s_carr_id,
         connid   TYPE s_conn_id,
         fldate   TYPE s_date,
         seatsmax TYPE s_seatsmax,
         seatsocc TYPE s_seatsocc,
       END OF ty_fl.
DATA: gt_fl  TYPE STANDARD TABLE OF ty_fl WITH EMPTY KEY,
      gs_fl  TYPE ty_fl,
      gv_pct TYPE p LENGTH 5 DECIMALS 1.

START-OF-SELECTION.
  SELECT carrid, connid, fldate, seatsmax, seatsocc FROM sflight
    WHERE carrid IN @s_carr
    ORDER BY carrid, connid, fldate
    INTO TABLE @gt_fl.
  IF sy-subrc <> 0.
    MESSAGE '데이터가 없습니다' TYPE 'S' DISPLAY LIKE 'E'.
    LEAVE LIST-PROCESSING.
  ENDIF.
  LOOP AT gt_fl INTO gs_fl.
    AT NEW carrid.
      WRITE: / '항공사', gs_fl-carrid.
    ENDAT.
    gv_pct = COND #( WHEN gs_fl-seatsmax > 0
                     THEN gs_fl-seatsocc * 100 / gs_fl-seatsmax ).
    WRITE: / gs_fl-connid, gs_fl-fldate, gs_fl-seatsocc, gv_pct, '%'.
    AT END OF connid.
      SUM.
      WRITE: / '  노선 소계', gs_fl-connid, gs_fl-seatsocc.
    ENDAT.
    AT END OF carrid.
      SUM.
      WRITE: / '항공사 소계', gs_fl-carrid, gs_fl-seatsocc.
      ULINE.
    ENDAT.
    AT LAST.
      SUM.
      WRITE: / '총계', gs_fl-seatsocc.
    ENDAT.
  ENDLOOP.
```
채점(4점): 선택 화면과 `IN s_carr`, 정렬(ORDER BY 또는 SORT) 1 / 구조가 carrid → connid로 시작하고 컨트롤 레벨 위치가 올바름 1 / SUM으로 소계·총계(SEATSMAX도 더해지지만 출력 안 하면 무방) 1 / 0으로 나누기 방지와 데이터 없음 처리 1. 점유율 계산은 AT 블록 밖에 둬야 원래 행 값으로 계산된다. GROUP BY 루프도 정답이지만 레거시 시험은 컨트롤 레벨을 기대한다.
**(6)** 프로그램당 하나뿐인 순차 데이터셋으로 서로 다른 구조의 레코드를 한 데이터셋에 쌓아 정렬·그룹 처리한다. 순서: ① `FIELD-GROUPS: header, flight.`(header는 정렬 키 역할의 특수 그룹) ② `INSERT sflight-carrid sflight-connid INTO header.` ③ 읽으며 `EXTRACT flight.` ④ `SORT.`(header 기준) ⑤ `LOOP. AT flight ... AT END OF carrid ... SUM ... ENDLOOP.` 첫 EXTRACT 이후에는 필드 그룹에 필드를 더 넣을 수 없다. obsolete이며 대안은 내부 테이블 + SORT + `LOOP AT ... GROUP BY` 또는 컨트롤 레벨 처리. 오래된 LDB 기반 리포트 유지보수에서 만나서 레거시 필기에 나온다.

</details>

---

### B-013. 리스트 리포트 손코딩: 조인·서식·코드 리뷰·3단계 드릴다운 [작성] ★★★
<!-- src: HC-001, HC-003, HC-004 -->
리스트 리포트 세 개를 쓰고 고친다.

(1) 실행 프로그램 `ZHC_CONN_LIST`(40~60줄)를 작성하시오. 선택화면: 항공사 `s_carr`(SPFLI-CARRID), 출발 도시 `s_from`(구간 없이 단일값 여러 개), 최대 비행시간 `p_maxft`(SPFLI-FLTIME, 기본 600, 필수, 0 이하이면 선택화면 오류). SPFLI와 SCARR을 조인해 코드·항공사명·노선·출발/도착 도시·비행시간·출발/도착 시각을 항공사·노선 순으로 읽고, 비행시간은 `h:mm`(125분 → `2:05`), TOP-OF-PAGE에 컬럼 제목과 밑줄, 데이터 줄은 번갈아 강조색, 마지막에 전체 건수. 데이터가 없으면 상태줄 메시지 후 리스트를 만들지 않는다.
(2) (1)에서 START-OF-SELECTION의 빈 결과에 `TYPE 'E'`를 쓰면 왜 감점인지, `NO STANDARD PAGE HEADING`을 빼면 어떻게 되는지, h:mm 변환의 다른 방법을 쓰시오.
(3) 다음 프로그램("선택한 항공사의 2026년 항공편 중 빈 좌석이 있는 편을 가격 내림차순으로")의 문법·런타임·논리·성능 문제를 6개 이상 찾아 고치시오.
```abap
REPORT zhc_bug_list.
PARAMETERS p_carr TYPE sflight-carrid.
SELECT-OPTIONS s_date FOR sflight-fldate.
DATA: gt_fl TYPE TABLE OF sflight,
      gs_fl TYPE sflight.
START-OF-SELECTION.
  SELECT * FROM sflight INTO TABLE gt_fl
    WHERE carrid = p_carr
      AND fldate BETWEEN '20260101' AND '20261231'.
  LOOP AT gt_fl INTO gs_fl.
    IF gs_fl-seatsocc >= gs_fl-seatsmax.
      DELETE gt_fl.
    ENDIF.
  ENDLOOP.
  SORT gt_fl BY price.
  LOOP AT gt_fl INTO gs_fl.
    SELECT SINGLE carrname FROM scarr INTO @DATA(lv_name)
      WHERE carrid = @gs_fl-carrid.
    WRITE: / gs_fl-carrid, lv_name, gs_fl-connid, gs_fl-fldate, gs_fl-price.
  ENDLOOP.
  IF sy-subrc <> 0.
    WRITE / '데이터 없음'.
  ENDIF.
```
(4) (3)의 첫 SELECT(구 문법)와 두 번째 SELECT(`@` 사용)가 섞인 것은 오류인가?
(5) 3단계 인터랙티브 리포트 `ZHC_DRILL`을 작성하시오. 기본 리스트: `s_carr`의 SCARR 코드(HOTSPOT)·이름 → 클릭 시 1단계: SPFLI 노선 → 클릭 시 2단계: SFLIGHT 항공편(비행일, 가격, 통화, 빈 좌석 수). 각 상세 머리글에 어느 항공사/노선인지 표시하고, 머리글·빈 줄 클릭 시 엉뚱한 리스트가 뜨지 않으며 2단계에서 클릭하면 아무 일도 없어야 한다.
(6) (5)에서 `WHEN OTHERS`에 `sy-lsind = 2`를 쓰는 이유, HIDE 대상이 전역 변수여야 하는 이유, HIDE 대신 sy-lisel·GET CURSOR를 쓰지 않는 이유를 쓰시오.

<details><summary>정답·해설</summary>

**(1)**
```abap
REPORT zhc_conn_list LINE-SIZE 110 NO STANDARD PAGE HEADING.
TABLES spfli.                                   " SELECT-OPTIONS FOR 용
TYPES: BEGIN OF ty_conn,
         carrid   TYPE spfli-carrid,
         carrname TYPE scarr-carrname,
         connid   TYPE spfli-connid,
         cityfrom TYPE spfli-cityfrom,
         cityto   TYPE spfli-cityto,
         fltime   TYPE spfli-fltime,
         deptime  TYPE spfli-deptime,
         arrtime  TYPE spfli-arrtime,
       END OF ty_conn.
DATA gt_conn TYPE STANDARD TABLE OF ty_conn WITH EMPTY KEY.

SELECTION-SCREEN BEGIN OF BLOCK b1 WITH FRAME TITLE TEXT-t01.
  SELECT-OPTIONS: s_carr FOR spfli-carrid,
                  s_from FOR spfli-cityfrom NO INTERVALS.
  PARAMETERS p_maxft TYPE spfli-fltime DEFAULT 600 OBLIGATORY.
SELECTION-SCREEN END OF BLOCK b1.

AT SELECTION-SCREEN ON p_maxft.
  IF p_maxft <= 0.
    MESSAGE '최대 비행시간은 0보다 커야 합니다' TYPE 'E'.
  ENDIF.

START-OF-SELECTION.
  SELECT s~carrid, c~carrname, s~connid, s~cityfrom, s~cityto,
         s~fltime, s~deptime, s~arrtime
    FROM spfli AS s
    INNER JOIN scarr AS c ON c~carrid = s~carrid
    WHERE s~carrid IN @s_carr AND s~cityfrom IN @s_from AND s~fltime <= @p_maxft
    ORDER BY s~carrid, s~connid
    INTO TABLE @gt_conn.
  IF gt_conn IS INITIAL.
    MESSAGE '데이터가 없습니다' TYPE 'S' DISPLAY LIKE 'E'.
    RETURN.                                   " 리스트를 만들지 않음
  ENDIF.
  DATA(lv_odd) = abap_true.
  LOOP AT gt_conn INTO DATA(ls_conn).
    DATA(lv_time) = |{ ls_conn-fltime DIV 60 }:{ ls_conn-fltime MOD 60 WIDTH = 2 ALIGN = RIGHT PAD = '0' }|.
    FORMAT COLOR COL_NORMAL INTENSIFIED = lv_odd.
    WRITE: / ls_conn-carrid, 6 ls_conn-carrname(20), 28 ls_conn-connid,
          34 ls_conn-cityfrom(15), 51 ls_conn-cityto(15),
          68 lv_time RIGHT-JUSTIFIED,
          78 ls_conn-deptime USING EDIT MASK '__:__',
          88 ls_conn-arrtime USING EDIT MASK '__:__'.
    lv_odd = xsdbool( lv_odd = abap_false ).
  ENDLOOP.
  FORMAT RESET.
  ULINE.
  DATA(lv_total) = lines( gt_conn ).
  WRITE: / '전체 건수:', lv_total.

TOP-OF-PAGE.
  FORMAT COLOR COL_HEADING.
  WRITE: / 'ID', 6 '항공사', 28 '노선', 34 '출발', 51 '도착',
          68 '비행시간', 78 '출발시각', 88 '도착시각'.
  FORMAT RESET.
  ULINE.
```
채점(100점): REPORT·타입·내부 테이블 10 / 선택화면 SELECT-OPTIONS 2개(NO INTERVALS)·PARAMETERS DEFAULT/OBLIGATORY 15 / AT SELECTION-SCREEN(ON 필드) E 검증 10 / JOIN + IN + ORDER BY + INTO TABLE 20 / 빈 결과(S 메시지 + 종료) 10 / h:mm(DIV/MOD, 두 자리 0 채움) 10 / WRITE·번갈아 강조색(FORMAT) 10 / TOP-OF-PAGE + ULINE 10 / 전체 건수 5. ON p_maxft의 E 메시지는 해당 필드만 입력 가능 상태로 다시 띄운다(일반 AT SELECTION-SCREEN도 인정). `INTENSIFIED = lv_odd`처럼 FORMAT 옵션에 변수를 줄 수 있다(비어 있으면 OFF).
**(2)** START-OF-SELECTION에서 `TYPE 'E'`를 쓰면 프로그램이 끝나 선택화면으로 돌아가지 않으므로 `TYPE 'S' DISPLAY LIKE 'E'` 뒤 `RETURN`(또는 `LEAVE LIST-PROCESSING`)으로 빈 리스트 화면을 막는다. `NO STANDARD PAGE HEADING`을 빼면 표준 머리글(프로그램 제목)이 TOP-OF-PAGE 출력 위에 따로 나온다. 문자열 템플릿의 `WIDTH/ALIGN/PAD`는 7.40부터이며, `lv_m = fltime MOD 60.` 후 `UNPACK`이나 `CONV numc2`를 써도 된다.
**(3)**

| # | 위치 | 문제 | 수정 |
|---|---|---|---|
| 1 | `FOR sflight-fldate` | TABLES sflight도 sflight 타입 데이터 객체도 없어 문법 오류 | `TABLES sflight.`(또는 `DATA gs_sel TYPE sflight.` 후 `FOR gs_sel-fldate`) |
| 2 | 고정 날짜 BETWEEN | 선택화면 s_date 무시(논리) | `AND fldate IN s_date`, 2026년은 s_date 기본값으로 |
| 3 | 루프 안 SELECT SINGLE scarr | 건수만큼 DB 접근(N+1, 성능) | JOIN 또는 루프 전에 SCARR을 HASHED 테이블로 |
| 4 | SELECT SINGLE 뒤 sy-subrc 미확인 | SCARR에 없으면 lv_name이 이전 값 그대로(논리) | `IF sy-subrc <> 0. CLEAR lv_name. ENDIF.` 또는 JOIN |
| 5 | 첫 루프 안 `DELETE gt_fl` | 현재 행 삭제는 허용되지만 비효율·가독성 나쁨 | WHERE에 `AND seatsocc < seatsmax`(컬럼끼리 비교 가능) 또는 `DELETE gt_fl WHERE seatsocc >= seatsmax.` |
| 6 | `SORT gt_fl BY price.` | 오름차순(요구는 내림차순) | `DESCENDING` 또는 `ORDER BY price DESCENDING` |
| 7 | 마지막 `IF sy-subrc <> 0` | LOOP 뒤 sy-subrc는 의미 불분명 | `IF gt_fl IS INITIAL. ... RETURN. ENDIF.`를 출력 루프 앞에 |
| 8 | p_carr | 필수가 아니어서 비우면 `carrid = ' '`로 결과 없음 | `OBLIGATORY` 또는 SELECT-OPTIONS |

```abap
REPORT zhc_bug_list.
TABLES sflight.
PARAMETERS p_carr TYPE sflight-carrid OBLIGATORY.
SELECT-OPTIONS s_date FOR sflight-fldate DEFAULT '20260101' TO '20261231'.

START-OF-SELECTION.
  SELECT f~carrid, c~carrname, f~connid, f~fldate, f~price, f~currency
    FROM sflight AS f
    INNER JOIN scarr AS c ON c~carrid = f~carrid
    WHERE f~carrid = @p_carr AND f~fldate IN @s_date AND f~seatsocc < f~seatsmax
    ORDER BY f~price DESCENDING
    INTO TABLE @DATA(gt_fl).
  IF gt_fl IS INITIAL.
    MESSAGE '데이터 없음' TYPE 'S' DISPLAY LIKE 'E'.
    RETURN.
  ENDIF.
  LOOP AT gt_fl INTO DATA(gs_fl).
    WRITE: / gs_fl-carrid, gs_fl-carrname, gs_fl-connid, gs_fl-fldate,
             gs_fl-price CURRENCY gs_fl-currency, gs_fl-currency.
  ENDLOOP.
```
채점: 항목당 10점(최대 80) + 완전한 수정본 20. 가격을 CURRENCY 없이 출력한 점(통화별 소수 자리) 지적은 가산점. 루프 안 SELECT SINGLE은 면접 성능 감점 1순위이며 JOIN, FOR ALL ENTRIES, SORTED/HASHED 룩업 중 하나로 바꾼다.
**(4)** 오류가 아니다. 엄격 모드는 문장 단위로 판단하므로 `@`나 인라인 선언을 쓴 문장 안에서만 모든 호스트 변수에 `@`가 필요하다. 그래도 새 문법으로 통일하고 INTO를 문장 끝에 두는 것이 권장된다.
**(5)**
```abap
REPORT zhc_drill NO STANDARD PAGE HEADING.
TABLES scarr.
SELECT-OPTIONS s_carr FOR scarr-carrid.
DATA: gv_carrid TYPE spfli-carrid,           " HIDE 대상은 전역 변수
      gv_connid TYPE spfli-connid.

START-OF-SELECTION.
  SELECT carrid, carrname FROM scarr
    WHERE carrid IN @s_carr ORDER BY carrid
    INTO TABLE @DATA(gt_carr).
  LOOP AT gt_carr INTO DATA(gs_carr).
    WRITE: / gs_carr-carrid HOTSPOT COLOR COL_KEY, gs_carr-carrname.
    gv_carrid = gs_carr-carrid.
    HIDE gv_carrid.                          " WRITE 다음에 HIDE
  ENDLOOP.
  CLEAR gv_carrid.

TOP-OF-PAGE.
  WRITE / '항공사 목록 (코드를 클릭하세요)'.
  ULINE.

AT LINE-SELECTION.
  CASE sy-lsind.
    WHEN 1.
      CHECK gv_carrid IS NOT INITIAL.
      SELECT connid, cityfrom, cityto FROM spfli
        WHERE carrid = @gv_carrid ORDER BY connid
        INTO TABLE @DATA(gt_conn).
      IF gt_conn IS INITIAL.
        MESSAGE '노선이 없습니다' TYPE 'S'.
        RETURN.
      ENDIF.
      LOOP AT gt_conn INTO DATA(gs_conn).
        WRITE: / gs_conn-connid HOTSPOT, gs_conn-cityfrom, gs_conn-cityto.
        gv_connid = gs_conn-connid.
        HIDE: gv_carrid, gv_connid.
      ENDLOOP.
      CLEAR: gv_carrid, gv_connid.
    WHEN 2.
      CHECK gv_carrid IS NOT INITIAL AND gv_connid IS NOT INITIAL.
      SELECT fldate, price, currency, seatsmax, seatsocc FROM sflight
        WHERE carrid = @gv_carrid AND connid = @gv_connid ORDER BY fldate
        INTO TABLE @DATA(gt_fl).
      LOOP AT gt_fl INTO DATA(gs_fl).
        DATA(lv_free) = gs_fl-seatsmax - gs_fl-seatsocc.
        WRITE: / gs_fl-fldate, gs_fl-price CURRENCY gs_fl-currency,
                 gs_fl-currency, lv_free.
      ENDLOOP.
      CLEAR: gv_carrid, gv_connid.
    WHEN OTHERS.
      sy-lsind = 2.                           " 3단계 이상은 만들지 않음
  ENDCASE.

TOP-OF-PAGE DURING LINE-SELECTION.
  CASE sy-lsind.
    WHEN 1. WRITE: / '항공사', gv_carrid, '의 노선'.
    WHEN 2. WRITE: / '노선', gv_carrid, gv_connid, '의 항공편'.
  ENDCASE.
  ULINE.
```
채점(100점): 기본 리스트 SELECT + WRITE HOTSPOT 10 / HIDE를 WRITE 뒤에, 값 대입 후 20 / 리스트 후 CLEAR + CHECK 15 / AT LINE-SELECTION + sy-lsind 분기 20 / 1단계에서 carrid·connid 둘 다 HIDE 10 / 2단계 SFLIGHT 출력(빈 좌석, CURRENCY) 10 / TOP-OF-PAGE DURING LINE-SELECTION 10 / 3단계 이상 처리 5.
**(6)** 상세 리스트에서 아무것도 WRITE하지 않으면 새 리스트가 만들어지지 않고 sy-lsind는 원래대로 돌아간다. `sy-lsind = 2`로 되돌리는 것은 "3단계로 쌓지 말고 2단계를 덮어쓰라"는 고전 기법이다(출력이 없으므로 WHEN OTHERS를 비워도 정답). 상세 리스트는 최대 20단계, 넘으면 런타임 오류. HIDE는 "방금 WRITE한 줄"에 변수 값을 숨기고, 줄을 고르면 같은 이름의 변수로 복원되므로 이벤트 블록에서도 보이는 전역 변수여야 한다. 숨긴 값이 없는 줄(머리글, ULINE, 빈 줄)을 클릭하면 변수는 현재 값 그대로라 CLEAR + CHECK가 필요하다. sy-lisel이나 GET CURSOR FIELD는 화면 위치·출력 형식에 의존하므로 HIDE가 표준 답이다.

</details>

---

## ALV

### B-014. ALV 방식 비교·필드 카탈로그·REUSE 함수 ALV [작성] ★★
<!-- src: CL-015, IB-047, IB-048, IB-049, IB-050, IB-051, TC-110, HC-011 -->
레거시 유지보수 과제로 함수 ALV 리포트 `ZHC_REUSE_ALV`를 받았다. ALV 기술 전반을 정리하면서 작성한다.

(1) `REUSE_ALV_GRID_DISPLAY`, `CL_GUI_ALV_GRID`, `CL_SALV_TABLE`을 형태, 화면/컨테이너 필요 여부, 편집, 이벤트 처리, 필드 카탈로그 측면에서 비교하시오. 신규 개발에서는 각각 언제 쓰는가?
(2) REUSE 기준 ALV 출력 형태 5가지(List, Grid, Hierarchical Sequential, Block, Tree)의 함수/클래스와 용도를 쓰시오.
(3) 필드 카탈로그(LVC_T_FCAT)의 자주 쓰는 필드와 의미, 필드 카탈로그를 만드는 방법 3가지 이상, `REUSE_ALV_FIELDCATALOG_MERGE`에 `i_internal_tabname`을 넘기는 방식의 단점을 쓰시오.
(4) 다음 이벤트/파라미터 이름 표를 채우시오.

| 기술 | 상황 | 이름 |
|---|---|---|
| CL_GUI_ALV_GRID | 행 더블클릭 / 핫스팟 클릭 / 툴바 버튼 추가 / 추가 버튼 처리 / 편집 셀 검증 | (a)~(e) |
| CL_SALV_TABLE | 행 더블클릭 / 링크 클릭 / 추가 기능 버튼 | (f)~(h) |
| REUSE | 사용자 명령 FORM 파라미터 / GUI Status FORM 파라미터 | (i)(j) |
| 공통 | 핸들러 등록 문장 | (k) |

(5) 다음 콜백 코드의 빈칸을 채우시오.
```abap
CALL FUNCTION 'REUSE_ALV_GRID_DISPLAY'
  EXPORTING i_callback_program       = lv_repid
            i_callback_pf_status_set = '____(1)____'
            i_callback_user_command  = 'USER_COMMAND'
            it_fieldcat = gt_fcat  i_save = 'A'
  TABLES    t_outtab = gt_flight.
FORM set_pf_status USING rt_extab TYPE slis_t_extab.
  SET PF-STATUS 'ZALV_STATUS' ____(2)____ rt_extab.
ENDFORM.
FORM user_command USING r_ucomm LIKE sy-ucomm rs_selfield TYPE ____(3)____.
  CASE r_ucomm.
    WHEN '&IC1'.
      READ TABLE gt_flight INTO DATA(ls_flight) INDEX rs_selfield-____(4)____.
  ENDCASE.
  rs_selfield-refresh = 'X'.
ENDFORM.
```
(6) CL_GUI_ALV_GRID에서 만석 항공편은 행 전체를 빨강, 가격 1000 초과면 PRICE 셀만 초록으로 하려 한다. 레이아웃 `ls_layo-(가) = 'ROWCOLOR'`, `ls_layo-(나) = 'CELLCOLOR'`, 셀 색 `APPEND VALUE #( fname = '(다)' color-col = 5 ) TO <ls_out>-cellcolor.`의 빈칸과, 행 색 값 `'C610'`의 의미('Cxyz')를 쓰시오. REUSE 레이아웃의 대응 필드는?
(7) 사용자별·공용 레이아웃을 모두 저장하게 하는 i_save 값은? ① `' '` ② `'X'` ③ `'U'` ④ `'A'`. 함께 넘겨야 하는 것과 기본 레이아웃 지정 방법도 쓰시오.
(8) `ZHC_REUSE_ALV`를 작성하시오. 선택화면 `s_carr`(SCARR-CARRID), SPFLI의 CARRID, CONNID, CITYFROM, CITYTO, FLTIME, DISTANCE, DISTID. 필드 카탈로그(`slis_t_fieldcat_alv`) 직접 작성: CARRID·CONNID 키, CARRID 핫스팟, FLTIME 제목 "비행시간(분)", DISTANCE는 DISTID 참조 + 합계. 레이아웃 줄무늬·폭 최적화, TOP_OF_PAGE에 제목과 실행일. 더블클릭(핫스팟)하면 그 노선의 SFLIGHT 전체 필드를 두 번째 함수 ALV로(구조명 사용).

<details><summary>정답·해설</summary>

**(1)**

| 구분 | REUSE_ALV_GRID_DISPLAY | CL_GUI_ALV_GRID | CL_SALV_TABLE |
|---|---|---|---|
| 형태 | 함수 모듈 | 클래스(컨트롤) | 클래스(OO 래퍼) |
| 화면/컨테이너 | 불필요(FM이 전체 화면) | 필요(사용자 화면 + Custom/Docking Container) | 불필요(전체 화면, 필요하면 컨테이너) |
| 편집 | 제한적(필드 카탈로그 EDIT) | 완전 지원(EDIT, DATA_CHANGED, check_changed_data) | 기본 미지원(표시용) |
| 이벤트 | USER_COMMAND, TOP_OF_PAGE 등 FORM 이름을 파라미터로 | 클래스 이벤트(DOUBLE_CLICK, HOTSPOT_CLICK, TOOLBAR, USER_COMMAND, DATA_CHANGED) + SET HANDLER | get_event( ) 객체에 SET HANDLER(DOUBLE_CLICK, LINK_CLICK, ADDED_FUNCTION) |
| 필드 카탈로그 | SLIS_T_FIELDCAT_ALV 또는 자동 | LVC_T_FCAT 또는 i_structure_name | 내부 테이블에서 자동, get_columns( )로 조정 |

신규 표시용은 CL_SALV_TABLE, 편집 화면은 CL_GUI_ALV_GRID. REUSE는 오래된 방식이지만 기존 코드에 많아 유지보수 질문으로 나온다.
**(2)**

| 형태 | 함수/클래스 | 용도 |
|---|---|---|
| Simple List | REUSE_ALV_LIST_DISPLAY | 문자 리스트, 인쇄·백그라운드 출력에 적합 |
| Grid | REUSE_ALV_GRID_DISPLAY, CL_GUI_ALV_GRID, CL_SALV_TABLE | 셀 단위 그리드, 편집·정렬·필터 |
| Hierarchical Sequential | REUSE_ALV_HIERSEQ_LIST_DISPLAY, CL_SALV_HIERSEQ_TABLE | 헤더·아이템 테이블을 키로 연결해 펼쳐 보임 |
| Block | REUSE_ALV_BLOCK_LIST_INIT / _APPEND / _DISPLAY | 다른 구조의 리스트 여러 개를 위아래로 |
| Tree | CL_GUI_ALV_TREE, CL_SALV_TREE | 계층 + 열 |

Grid는 GUI 컨트롤이라 백그라운드 잡에서는 리스트 형태로 스풀에 출력된다.
**(3)** `FIELDNAME`(내부 테이블 필드명), `COLTEXT`/`SCRTEXT_L/M/S`(열 제목), `OUTPUTLEN`, `NO_OUT`(숨김), `HOTSPOT`, `EDIT`, `KEY`(키 열 고정·색), `REF_TABLE`/`REF_FIELD`(DDIC 참조), `CFIELDNAME`/`QFIELDNAME`(통화/수량 참조), `DO_SUM`(합계), `CHECKBOX`, `ICON`. 레이아웃(LVC_S_LAYO)의 ZEBRA, CWIDTH_OPT, SEL_MODE, STYLEFNAME, INFO_FNAME도 자주 나온다. 만드는 방법: ① 수동(필드마다 fieldname, seltext/coltext, outputlen, ref_table/ref_field 채워 APPEND) ② DDIC 구조로 자동 생성(`LVC_FIELDCATALOG_MERGE` 또는 `REUSE_ALV_FIELDCATALOG_MERGE`의 i_structure_name) 후 수정 ③ 내부 테이블에서 생성(CL_SALV_TABLE을 만든 뒤 `cl_salv_controller_metadata=>get_lvc_fieldcatalog`, 또는 RTTS `cl_abap_structdescr`) ④ CL_SALV_TABLE은 카탈로그 없이 자동. 단점: `i_internal_tabname`을 넘기면 함수가 프로그램 소스를 읽어 선언을 해석하므로 필드를 `LIKE`(DDIC 참조)로 선언해야 하고, 한 줄 72자 제한·인라인 선언·TYPES 분리 등 현대 문법에서 제대로 동작하지 않는 경우가 많다.
**(4)** (a) DOUBLE_CLICK (b) HOTSPOT_CLICK (c) TOOLBAR (d) USER_COMMAND (e) DATA_CHANGED(완료 후는 DATA_CHANGED_FINISHED) (f) DOUBLE_CLICK (g) LINK_CLICK (h) ADDED_FUNCTION (i) I_CALLBACK_USER_COMMAND (j) I_CALLBACK_PF_STATUS_SET (k) SET HANDLER. 선언 예: `METHODS on_dbl FOR EVENT double_click OF cl_gui_alv_grid IMPORTING e_row e_column.`, 등록 `SET HANDLER lo_h->on_dbl FOR go_grid.` SALV는 `lo_alv->get_event( )`로 이벤트 객체를 얻어 `SET HANDLER ... FOR lo_events`. REUSE 콜백에는 `I_CALLBACK_PROGRAM = sy-repid`도 함께, 머리글은 `I_CALLBACK_TOP_OF_PAGE`. 편집 그리드의 DATA_CHANGED는 `register_edit_event( i_event_id = cl_gui_alv_grid=>mc_evt_modified )`(또는 mc_evt_enter)를 호출해야 즉시 발생한다.
**(5)** (1) `SET_PF_STATUS` (2) `EXCLUDING` (3) `slis_selfield` (4) `tabindex`. 콜백 FORM 이름은 대문자 문자열로 넘기며 ALV가 `PERFORM (name) IN PROGRAM (i_callback_program)`으로 부른다. 사용자 GUI 상태는 SE41에서 표준 상태 `STANDARD_FULLSCREEN`(프로그램 SAPLKKBL 또는 SAPLSLVC_FULLSCREEN)을 복사해 버튼을 추가한다. `EXCLUDING rt_extab`을 빼면 ALV가 숨기려던 기능 버튼이 그대로 보인다. `&IC1`은 더블클릭(또는 핫스팟) 함수 코드. rs_selfield에는 `tabindex`(행 번호), `fieldname`, `value`, `refresh`, `col_stable`/`row_stable`이 있다. 예제에서는 고른 행의 carrid를 `SET PARAMETER ID 'CAR'`로 넘길 수 있다.
**(6)** (가) `info_fname` (나) `ctab_fname` (다) `PRICE`. 행 색: 출력 테이블의 CHAR 4 필드 이름을 info_fname에 지정하고 `'Cxyz'`: x = 색 번호(1 파랑회색, 2 회색, 3 노랑, 4 파랑, 5 초록, 6 빨강, 7 주황), y = 강조(1/0), z = 반전(1/0). `'C610'`은 빨강·강조·반전 없음. 셀 색: LVC_T_SCOL 타입 필드 이름을 ctab_fname에 지정하고 열 이름(fname)과 색(color-col/int/inv)을 행마다 넣는다. REUSE(SLIS_LAYOUT_ALV)는 `info_fieldname`, `coltab_fieldname`. 셀 편집 가능/불가 스타일은 `stylefname`(LVC_T_STYL).
**(7)** ④ `'A'`. `' '` 저장 불가, `'X'` 공용(표준)만, `'U'` 사용자별만, `'A'` 둘 다(CL_SALV_TABLE은 `set_save_restriction`). 저장하려면 `is_variant-report = sy-repid`(그리드가 여러 개면 `handle`도)를 함께 넘기고, 기본 레이아웃은 `i_default = 'X'`.
**(8)**
```abap
REPORT zhc_reuse_alv.
TABLES scarr.
SELECT-OPTIONS s_carr FOR scarr-carrid.
TYPES: BEGIN OF ty_conn,
         carrid   TYPE spfli-carrid,
         connid   TYPE spfli-connid,
         cityfrom TYPE spfli-cityfrom,
         cityto   TYPE spfli-cityto,
         fltime   TYPE spfli-fltime,
         distance TYPE spfli-distance,
         distid   TYPE spfli-distid,
       END OF ty_conn.
DATA: gt_conn   TYPE STANDARD TABLE OF ty_conn WITH EMPTY KEY,
      gt_fcat   TYPE slis_t_fieldcat_alv,
      gs_layout TYPE slis_layout_alv.

START-OF-SELECTION.
  SELECT carrid, connid, cityfrom, cityto, fltime, distance, distid
    FROM spfli WHERE carrid IN @s_carr ORDER BY carrid, connid
    INTO TABLE @gt_conn.
  IF gt_conn IS INITIAL.
    MESSAGE '데이터가 없습니다' TYPE 'S' DISPLAY LIKE 'E'.
    RETURN.
  ENDIF.
  gt_fcat = VALUE #(
    ( fieldname = 'CARRID'   ref_tabname = 'SPFLI' key = 'X' hotspot = 'X' )
    ( fieldname = 'CONNID'   ref_tabname = 'SPFLI' key = 'X' )
    ( fieldname = 'CITYFROM' ref_tabname = 'SPFLI' )
    ( fieldname = 'CITYTO'   ref_tabname = 'SPFLI' )
    ( fieldname = 'FLTIME'   ref_tabname = 'SPFLI'
      seltext_s = '비행(분)' seltext_m = '비행시간(분)' seltext_l = '비행시간(분)' )
    ( fieldname = 'DISTANCE' ref_tabname = 'SPFLI' qfieldname = 'DISTID' do_sum = 'X' )
    ( fieldname = 'DISTID'   ref_tabname = 'SPFLI' ) ).
  gs_layout = VALUE #( zebra = 'X' colwidth_optimize = 'X' ).

  CALL FUNCTION 'REUSE_ALV_GRID_DISPLAY'
    EXPORTING
      i_callback_program      = sy-repid
      i_callback_user_command = 'USER_COMMAND'
      i_callback_top_of_page  = 'TOP_OF_PAGE'
      is_layout               = gs_layout
      it_fieldcat             = gt_fcat
    TABLES
      t_outtab                = gt_conn
    EXCEPTIONS
      program_error           = 1
      OTHERS                  = 2.
  IF sy-subrc <> 0.
    MESSAGE 'ALV 출력 오류' TYPE 'S' DISPLAY LIKE 'E'.
  ENDIF.

FORM user_command USING r_ucomm     TYPE sy-ucomm
                        rs_selfield TYPE slis_selfield.
  DATA lt_fl TYPE STANDARD TABLE OF sflight.
  CASE r_ucomm.
    WHEN '&IC1'.                               " 더블클릭·핫스팟
      READ TABLE gt_conn INTO DATA(ls_conn) INDEX rs_selfield-tabindex.
      CHECK sy-subrc = 0.
      SELECT * FROM sflight
        WHERE carrid = @ls_conn-carrid AND connid = @ls_conn-connid
        INTO TABLE @lt_fl.
      IF lt_fl IS INITIAL.
        MESSAGE '항공편이 없습니다' TYPE 'S'.
        RETURN.
      ENDIF.
      CALL FUNCTION 'REUSE_ALV_GRID_DISPLAY'
        EXPORTING  i_structure_name = 'SFLIGHT'
        TABLES     t_outtab         = lt_fl
        EXCEPTIONS OTHERS           = 1.
  ENDCASE.
ENDFORM.

FORM top_of_page.
  DATA(lt_header) = VALUE slis_t_listheader(
    ( typ = 'H' info = '노선 목록' )
    ( typ = 'S' key = '실행일' info = |{ sy-datum DATE = USER }| ) ).
  CALL FUNCTION 'REUSE_ALV_COMMENTARY_WRITE'
    EXPORTING it_list_commentary = lt_header.
ENDFORM.
```
채점(100점): SELECT + 빈 결과 10 / 필드 카탈로그(ref_tabname, key, hotspot, seltext, qfieldname, do_sum) 25 / 레이아웃 5 / REUSE 호출(callback program/user_command/top_of_page, TABLES t_outtab, EXCEPTIONS) 20 / FORM user_command 시그니처 + `&IC1` + tabindex 20 / 두 번째 ALV(i_structure_name) 10 / TOP_OF_PAGE + REUSE_ALV_COMMENTARY_WRITE 10. `i_callback_program = sy-repid`가 없으면 FORM을 찾지 못한다(회사 규칙에 따라 `DATA(lv_repid) = sy-repid.`로 받아 넘기기도 함). 폭 최적화 시 ALV는 폭에 맞춰 짧은/중간/긴 제목 중 하나를 고르므로 seltext_s/m/l을 모두 채운다(하나만 채우면 나머지는 DDIC 텍스트). 7.40 이상에서 `TYPE-POOLS slis`는 필요 없다.

</details>

---

### B-015. CL_SALV_TABLE: factory·열·정렬·소계·핫스팟 팝업 [작성] ★★★
<!-- src: CL-016, MX-021, IB-055, CL-014, HC-009 -->
SFLIGHT 좌석 현황을 SALV로 보여 주는 리포트를 단계별로 만든다.

(1) 다음 빈칸을 채우시오.
```abap
DATA: lo_alv TYPE REF TO cl_salv_table,
      lo_col TYPE REF TO cl_salv_column_table.
TRY.
    cl_salv_table=>____(1)____( IMPORTING r_salv_table = lo_alv
                                CHANGING  t_table      = gt_flight ).
  CATCH ____(2)____ INTO DATA(lx_msg).
    MESSAGE lx_msg->get_text( ) TYPE 'E'.
ENDTRY.
lo_alv->get_functions( )->____(3)____( abap_true ).
lo_alv->get_columns( )->set_optimize( abap_true ).
TRY.
    lo_col ____(4)____ lo_alv->get_columns( )->get_column( 'PRICE' ).
    lo_col->set_cell_type( if_salv_c_cell_type=>____(5)____ ).
    lo_col->set_long_text( '항공료' ).
    lo_alv->get_sorts( )->add_sort( columnname = 'CARRID' ____(6)____ = abap_true ).
    lo_alv->____(7)____( )->add_aggregation( columnname = 'PRICE' ).
  CATCH cx_salv_error.
ENDTRY.
SET HANDLER lcl_handler=>on_click FOR lo_alv->get_event( ).
lo_alv->____(8)____( ).
" CLASS-METHODS on_click FOR EVENT ____(9)____ OF cl_salv_events_table IMPORTING row column.
```
(2) (4)에서 다운캐스트가 필요한 이유, 각 메서드가 던지는 예외와 공통 상위 예외, add_aggregation의 기본 집계, 소계가 나오는 조건을 쓰시오. 열을 숨기려면?
(3) 리포트(약 25줄)를 작성하시오. 선택 화면: `s_carr`(SFLIGHT-CARRID 기준 참조 변수), 최대 건수 `p_max`(기본 100, 1~1000 아니면 선택 화면 오류). SFLIGHT의 CARRID, CONNID, FLDATE, PRICE, CURRENCY, SEATSMAX, SEATSOCC를 최대 p_max건 읽고, 없으면 S 메시지를 오류처럼 보이고 종료, SALV로 출력(표준 툴바 전부).
(4) (3)에서 `UP TO n ROWS`를 쓸 때 주의점과 채점 포인트를 쓰시오.
(5) 리포트 `ZHC_SALV`를 작성하시오. 컬럼: CARRID, CONNID, FLDATE, PRICE, CURRENCY, SEATSMAX, SEATSOCC, PAYMENTSUM, 계산 컬럼 `FREE`(SEATSMAX − SEATSOCC, 제목 "빈 좌석"). 표준 툴바, 줄무늬, 폭 최적화, 리스트 제목 "항공편 좌석 현황", CARRID 정렬 + 소계, PAYMENTSUM·FREE 합계, CONNID 핫스팟 클릭 시 그 항공편의 SBOOK(BOOKID, CUSTOMID, PASSNAME, CLASS, LOCCURAM, LOCCURKEY)을 팝업 SALV로, SALV 예외 처리.
(6) (5)에서 `get_event( )` 결과를 변수에 받는 이유, link_click의 row가 사용자 정렬 후에도 맞는 이유, 금액 합계와 통화, 팝업에서 지역 테이블을 써도 되는 이유를 쓰시오.

<details><summary>정답·해설</summary>

**(1)** (1) `factory` (2) `cx_salv_msg` (3) `set_all` (4) `?=` (5) `hotspot` (6) `subtotal` (7) `get_aggregations` (8) `display` (9) `link_click`.
**(2)** `get_column`은 상위 타입 `CL_SALV_COLUMN` 참조를 돌려주고, 핫스폿 같은 셀 유형 설정(`set_cell_type`)은 하위 `CL_SALV_COLUMN_TABLE`에만 있어서 `?=`(또는 `CAST cl_salv_column_table( ... )`)가 필요하다. factory는 CX_SALV_MSG, get_column은 열이 없으면 CX_SALV_NOT_FOUND, add_aggregation은 CX_SALV_DATA_ERROR/CX_SALV_EXISTING 등을 던지며 공통 상위는 CX_SALV_ERROR. 이들은 정적 검사 예외라 처리해야 한다. 기본 집계는 합계(`if_salv_c_aggregation=>total`). 소계는 정렬 기준 열에 `subtotal = abap_true` + 합계 대상 열의 aggregation 등록이 같이 있어야 나온다(집계가 없으면 소계 줄이 없다). 열 숨김은 `lo_col->set_visible( abap_false )`. 핫스팟 클릭은 `get_event( )`의 LINK_CLICK, 더블클릭은 `double_click`, 사용자 함수는 `added_function`. CL_SALV_TABLE은 t_table을 참조로 붙잡고 있으므로 display 전에 내부 테이블이 유효해야 한다.
**(3)**
```abap
REPORT zcl_flight_list.
DATA gv_carrid TYPE s_carr_id.
SELECT-OPTIONS s_carr FOR gv_carrid.
PARAMETERS p_max TYPE i DEFAULT 100.

AT SELECTION-SCREEN ON p_max.
  IF p_max < 1 OR p_max > 1000.
    MESSAGE 'p_max must be between 1 and 1000' TYPE 'E'.
  ENDIF.

START-OF-SELECTION.
  SELECT carrid, connid, fldate, price, currency, seatsmax, seatsocc
    FROM sflight
    WHERE carrid IN @s_carr
    ORDER BY carrid, connid, fldate
    INTO TABLE @DATA(gt_flight)
    UP TO @p_max ROWS.
  IF gt_flight IS INITIAL.
    MESSAGE 'No data found' TYPE 'S' DISPLAY LIKE 'E'.
    RETURN.
  ENDIF.
  TRY.
      cl_salv_table=>factory( IMPORTING r_salv_table = DATA(go_alv)
                              CHANGING  t_table      = gt_flight ).
      go_alv->get_functions( )->set_all( abap_true ).
      go_alv->display( ).
    CATCH cx_salv_msg INTO DATA(gx).
      MESSAGE gx->get_text( ) TYPE 'I'.
  ENDTRY.
```
**(4)** `UP TO n ROWS`는 ORDER BY와 함께 써야 어떤 행을 가져올지 결정적이고, 새 문법에서는 INTO 뒤에 쓴다. 검증은 AT SELECTION-SCREEN(또는 ON p_max)의 E 메시지로 해야 선택 화면에 머물고(START-OF-SELECTION의 E는 종료), "데이터 없음"은 `TYPE 'S' DISPLAY LIKE 'E'`가 관례. 채점 포인트: SELECT-OPTIONS FOR 참조 변수, AT SELECTION-SCREEN 검증, IN @s_carr, 빈 결과 처리, factory의 IMPORTING/CHANGING, 예외 처리.
**(5)**
```abap
REPORT zhc_salv.
TABLES sflight.
SELECT-OPTIONS s_carr FOR sflight-carrid.
TYPES: BEGIN OF ty_fl,
         carrid     TYPE sflight-carrid,
         connid     TYPE sflight-connid,
         fldate     TYPE sflight-fldate,
         price      TYPE sflight-price,
         currency   TYPE sflight-currency,
         seatsmax   TYPE sflight-seatsmax,
         seatsocc   TYPE sflight-seatsocc,
         paymentsum TYPE sflight-paymentsum,
         free       TYPE i,
       END OF ty_fl.
DATA gt_fl TYPE STANDARD TABLE OF ty_fl WITH EMPTY KEY.   " 전역: ALV가 참조

CLASS lcl_handler DEFINITION.
  PUBLIC SECTION.
    CLASS-METHODS on_link_click FOR EVENT link_click OF cl_salv_events_table
      IMPORTING row column.
ENDCLASS.
CLASS lcl_handler IMPLEMENTATION.
  METHOD on_link_click.
    CHECK column = 'CONNID'.
    READ TABLE gt_fl INTO DATA(ls_fl) INDEX row.
    CHECK sy-subrc = 0.
    SELECT bookid, customid, passname, class, loccuram, loccurkey FROM sbook
      WHERE carrid = @ls_fl-carrid AND connid = @ls_fl-connid AND fldate = @ls_fl-fldate
      ORDER BY bookid INTO TABLE @DATA(lt_book).
    IF lt_book IS INITIAL.
      MESSAGE '예약이 없습니다' TYPE 'S'.
      RETURN.
    ENDIF.
    TRY.
        cl_salv_table=>factory( IMPORTING r_salv_table = DATA(lo_pop)
                                CHANGING  t_table      = lt_book ).
        lo_pop->set_screen_popup( start_column = 10 end_column = 110
                                  start_line   = 3  end_line   = 20 ).
        lo_pop->display( ).
      CATCH cx_salv_msg INTO DATA(lx_msg).
        MESSAGE lx_msg TYPE 'S' DISPLAY LIKE 'E'.
    ENDTRY.
  ENDMETHOD.
ENDCLASS.

START-OF-SELECTION.
  SELECT carrid, connid, fldate, price, currency, seatsmax, seatsocc, paymentsum
    FROM sflight WHERE carrid IN @s_carr
    INTO CORRESPONDING FIELDS OF TABLE @gt_fl.
  IF gt_fl IS INITIAL.
    MESSAGE '데이터가 없습니다' TYPE 'S' DISPLAY LIKE 'E'.
    RETURN.
  ENDIF.
  LOOP AT gt_fl ASSIGNING FIELD-SYMBOL(<fl>).
    <fl>-free = <fl>-seatsmax - <fl>-seatsocc.
  ENDLOOP.
  TRY.
      cl_salv_table=>factory( IMPORTING r_salv_table = DATA(go_alv)
                              CHANGING  t_table      = gt_fl ).
      go_alv->get_functions( )->set_all( abap_true ).
      DATA(lo_disp) = go_alv->get_display_settings( ).
      lo_disp->set_striped_pattern( abap_true ).
      lo_disp->set_list_header( '항공편 좌석 현황' ).
      DATA(lo_cols) = go_alv->get_columns( ).
      lo_cols->set_optimize( abap_true ).
      DATA(lo_col) = CAST cl_salv_column_table( lo_cols->get_column( 'CONNID' ) ).
      lo_col->set_cell_type( if_salv_c_cell_type=>hotspot ).
      lo_col = CAST #( lo_cols->get_column( 'FREE' ) ).
      lo_col->set_short_text( '빈좌석' ).
      lo_col->set_medium_text( '빈 좌석' ).
      lo_col->set_long_text( '빈 좌석 수' ).
      go_alv->get_sorts( )->add_sort( columnname = 'CARRID' subtotal = abap_true ).
      DATA(lo_aggr) = go_alv->get_aggregations( ).
      lo_aggr->add_aggregation( columnname  = 'PAYMENTSUM'
                                aggregation = if_salv_c_aggregation=>total ).
      lo_aggr->add_aggregation( columnname  = 'FREE' ).
      DATA(lo_events) = go_alv->get_event( ).
      SET HANDLER lcl_handler=>on_link_click FOR lo_events.
      go_alv->display( ).
    CATCH cx_salv_error INTO DATA(lx_err).   " msg, not_found, existing, data_error의 상위
      MESSAGE lx_err TYPE 'S' DISPLAY LIKE 'E'.
  ENDTRY.
```
채점(100점): 전역 테이블 + 계산 컬럼 10 / factory + display 15 / 툴바·줄무늬·제목·최적화 10 / get_column + CAST + hotspot 15 / short/medium/long 제목 5 / add_sort(subtotal) + add_aggregation 15 / 핸들러 정의(FOR EVENT link_click OF cl_salv_events_table) + SET HANDLER 15 / 팝업(set_screen_popup) 10 / TRY/CATCH 5.
**(6)** `SET HANDLER ... FOR`에는 참조 변수를 써야 해서 `get_event( )` 결과를 먼저 변수에 받는다((1)처럼 직접 쓰는 형태보다 안전). link_click의 `row`는 출력 테이블 행 번호이며, 사용자 정렬은 SALV 내부 정렬 테이블로 처리되므로 원래 행 번호가 넘어온다. 금액 합계는 같은 통화끼리만 의미가 있고, SALV는 DDIC 참조(SFLIGHT-PAYMENTSUM → CURRENCY)를 읽어 통화별로 합계를 나눠 보여 준다. 팝업은 `display( )`가 끝날 때까지 모달이라 메서드 지역 테이블 `lt_book`을 써도 안전하다. 메인 출력 테이블은 ALV가 참조하므로 전역으로 둔다.

</details>

---

### B-016. CL_GUI_ALV_GRID: 컨테이너·이벤트·편집·툴바·2화면 프로그램 [작성] ★★★
<!-- src: CL-017, MX-022, IB-052, IB-053, IB-054, HC-010 -->
화면 0100(Custom Control `CC_ALV`, OK 필드 `OK_CODE`, GUI status `S100`: BACK, EXIT, CANC)과 0200(`CC_BOOK`, `S200`: BACK)으로 된 OO ALV 프로그램 `ZHC_ALV_GRID`를 만든다.

(1) `CL_GUI_ALV_GRID`에 대한 설명 중 옳지 않은 것은? ① Custom Control에 띄우려면 `CL_GUI_CUSTOM_CONTAINER`를 먼저 만들어 `i_parent`로 넘긴다 ② 처음은 `set_table_for_first_display`, 데이터를 바꾼 뒤는 `refresh_table_display` ③ 더블클릭은 `FOR EVENT double_click OF cl_gui_alv_grid` 핸들러 + `SET HANDLER` ④ 편집 그리드에서 바뀐 값은 즉시 내부 테이블에 반영되므로 저장 전에 `check_changed_data`가 필요 없다 ⑤ 필드 카탈로그 `hotspot = 'X'`와 `hotspot_click` 이벤트로 셀 클릭 처리.
(2) GUI 컨테이너에 대해 옳지 않은 것은? ① CUSTOM_CONTAINER는 Screen Painter에 Custom Control 영역이 필요 ② DOCKING_CONTAINER는 화면 요소 없이 가장자리에 붙어 선택 화면 위에도 띄울 수 있다 ③ SPLITTER_CONTAINER는 영역을 여러 셀로 나눈다 ④ CL_GUI_ALV_GRID는 배치 잡에서도 SAP GUI에 그리드를 띄운다. 컨트롤과 프런트엔드의 통신 방식도 쓰시오.
(3) 전역 `gt_flight`를 화면 0100에 출력하고 더블클릭한 행의 CARRID, CONNID, FLDATE를 정보 메시지로 보이는 핸들러 클래스와 PBO 모듈을 작성하시오. 그리드를 한 번만 만드는 처리를 포함한다.
(4) 편집 가능한 ALV에서 ① 셀을 편집 가능하게 하는 두 방법 ② Enter/셀 이동 시 바로 검사하는 설정과 이벤트, 오류 표시 방법 ③ 저장 버튼 전에 반드시 부를 메서드와 이유 ④ 저장 후 스크롤 위치 유지 갱신과 DB 반영 순서를 쓰시오.
(5) 툴바에 "승인" 버튼을 추가하고 선택 행을 처리하는 데 필요한 이벤트 두 개와 각 핸들러의 일, 버튼을 나타나게 하는 메서드, 선택 행을 얻는 메서드와 필요한 레이아웃 설정, 표준 버튼 제외 방법을 쓰시오.
(6) `ZHC_ALV_GRID`의 ABAP 코드와 두 화면의 흐름 로직을 작성하시오. 화면 100: `s_carr`의 SFLIGHT, 필드 카탈로그 직접 작성(CARRID·CONNID·FLDATE 키, PRICE, CURRENCY, SEATSMAX, SEATSOCC, PAYMENTSUM; SEATSOCC·PAYMENTSUM 합계), CARRID 정렬·소계, 줄무늬·폭 최적화·다중 행 선택. 행 더블클릭 → 그 항공편 SBOOK을 화면 200에 ALV로(DDIC 구조명), BACK하면 100으로, 다른 행을 더블클릭하면 새 데이터로.
(7) (6)에서 화면 200에 `refresh_table_display`를 빠뜨리면 생기는 일, `e_row-rowtype` 검사 이유, `ref_table`만 주고 `ref_field`를 비운 경우의 동작, 핸들러에서 바로 CALL SCREEN하는 대신 쓸 수 있는 방법, 컨트롤 해제를 쓰시오.

<details><summary>정답·해설</summary>

**(1)** ④. 그리드는 프런트엔드 컨트롤이라 사용자가 바꾼 값은 처음에 프런트엔드에만 있다. 저장 버튼 PAI에서 `check_changed_data`를 불러야 검증되고 내부 테이블로 넘어온다(data_changed 이벤트 발생). 빠뜨리면 마지막에 고친 셀이 저장되지 않는 버그가 흔하다.
**(2)** ④. 백그라운드에는 SAP GUI가 없어 컨트롤을 띄울 수 없고 리스트 형태로 스풀에 출력된다(`sy-batch`로 분기). 컨트롤은 프런트엔드와 자동화 큐로 통신하며 `cl_gui_cfw=>flush`로 큐를 강제로 보낼 수 있다.
**(3)**
```abap
DATA: gt_flight    TYPE STANDARD TABLE OF sflight,
      go_container TYPE REF TO cl_gui_custom_container,
      go_grid      TYPE REF TO cl_gui_alv_grid.

CLASS lcl_handler DEFINITION.
  PUBLIC SECTION.
    CLASS-METHODS on_double_click FOR EVENT double_click OF cl_gui_alv_grid
      IMPORTING e_row e_column.
ENDCLASS.
CLASS lcl_handler IMPLEMENTATION.
  METHOD on_double_click.
    READ TABLE gt_flight INTO DATA(ls_flight) INDEX e_row-index.
    IF sy-subrc = 0.
      MESSAGE |{ ls_flight-carrid } { ls_flight-connid } { ls_flight-fldate DATE = USER }| TYPE 'I'.
    ENDIF.
  ENDMETHOD.
ENDCLASS.

MODULE status_0100 OUTPUT.
  SET PF-STATUS 'S100'.
  IF go_container IS INITIAL.
    go_container = NEW #( container_name = 'CC_ALV' ).
    go_grid = NEW #( i_parent = go_container ).
    SET HANDLER lcl_handler=>on_double_click FOR go_grid.
    go_grid->set_table_for_first_display(
      EXPORTING i_structure_name = 'SFLIGHT'
      CHANGING  it_outtab        = gt_flight ).
  ELSE.
    go_grid->refresh_table_display( ).
  ENDIF.
ENDMODULE.
```
PBO는 화면이 다시 표시될 때마다 실행되므로 `IS INITIAL` 검사로 한 번만 만들고 두 번째부터 refresh. 핸들러는 `FOR EVENT ... OF cl_gui_alv_grid IMPORTING e_row e_column (es_row_no)`로 선언하고 SET HANDLER로 인스턴스에 등록하며, 등록 전에 일어난 이벤트는 처리되지 않는다. 핫스팟은 카탈로그 HOTSPOT = 'X' + HOTSPOT_CLICK(e_row_id, e_column_id). 채점: 핸들러 선언 문법, SET HANDLER, 한 번만 생성, e_row-index로 행 읽기.
**(4)** ① 필드 카탈로그 `edit = 'X'`(열 단위), 또는 레이아웃 `edit = 'X'`(전체) + 셀 스타일(`stylefname`, `cl_gui_alv_grid=>mc_style_enabled/disabled`)로 셀 단위 제어. ② `register_edit_event( i_event_id = cl_gui_alv_grid=>mc_evt_enter )`(또는 `mc_evt_modified`) 등록, `DATA_CHANGED` 핸들러에서 `er_data_changed->mt_good_cells`로 바뀐 셀 검사, 오류는 `er_data_changed->add_protocol_entry`, 반영 완료 후 처리는 `DATA_CHANGED_FINISHED`. ③ `check_changed_data( )`: 프런트엔드 값을 내부 테이블로 옮기고 DATA_CHANGED 검사를 실행한다. 안 부르면 마지막 입력 셀 값이 반영되지 않은 채 저장될 수 있다. ④ `refresh_table_display( is_stable = VALUE #( row = 'X' col = 'X' ) )`로 스크롤 유지, DB 반영은 잠금(ENQUEUE) → 변경 → COMMIT WORK.
**(5)** `TOOLBAR` 이벤트: `e_object->mt_toolbar`에 버튼(STB_BUTTON: `function = 'APPROVE'`, `icon`, `text`, `quickinfo`, `butn_type = 0`)을 APPEND. 그리드 표시 후 `set_toolbar_interactive( )`를 부르면 TOOLBAR가 다시 발생해 버튼이 나타난다. `USER_COMMAND` 이벤트: `e_ucomm = 'APPROVE'`일 때 처리. 선택 행: `get_selected_rows( IMPORTING et_index_rows = ... )`(또는 `et_row_no`), 레이아웃 `sel_mode = 'A'`(행 선택 버튼) 등이 필요. 등록은 `SET HANDLER lo_handler->on_toolbar lo_handler->on_user_command FOR go_grid.`를 `set_table_for_first_display` 전에. 표준 버튼 제외는 `it_toolbar_excluding`.
**(6)**
```abap
REPORT zhc_alv_grid.
TABLES sflight.
SELECT-OPTIONS s_carr FOR sflight-carrid.
DATA: gt_fl    TYPE STANDARD TABLE OF sflight WITH EMPTY KEY,
      gt_book  TYPE STANDARD TABLE OF sbook   WITH EMPTY KEY,
      go_cont1 TYPE REF TO cl_gui_custom_container,
      go_grid1 TYPE REF TO cl_gui_alv_grid,
      go_cont2 TYPE REF TO cl_gui_custom_container,
      go_grid2 TYPE REF TO cl_gui_alv_grid,
      ok_code  TYPE sy-ucomm.

CLASS lcl_events DEFINITION.
  PUBLIC SECTION.
    METHODS on_double_click FOR EVENT double_click OF cl_gui_alv_grid
      IMPORTING e_row e_column es_row_no.
ENDCLASS.
CLASS lcl_events IMPLEMENTATION.
  METHOD on_double_click.
    CHECK e_row-rowtype IS INITIAL.            " 소계·합계 행이면 무시
    READ TABLE gt_fl INTO DATA(ls_fl) INDEX e_row-index.
    CHECK sy-subrc = 0.
    SELECT * FROM sbook
      WHERE carrid = @ls_fl-carrid AND connid = @ls_fl-connid AND fldate = @ls_fl-fldate
      ORDER BY bookid INTO TABLE @gt_book.
    IF gt_book IS INITIAL.
      MESSAGE '예약이 없습니다' TYPE 'S'.
      RETURN.
    ENDIF.
    CALL SCREEN 200.
  ENDMETHOD.
ENDCLASS.
DATA go_events TYPE REF TO lcl_events.

START-OF-SELECTION.
  SELECT * FROM sflight WHERE carrid IN @s_carr INTO TABLE @gt_fl.
  IF gt_fl IS INITIAL.
    MESSAGE '데이터가 없습니다' TYPE 'S' DISPLAY LIKE 'E'.
    RETURN.
  ENDIF.
  CALL SCREEN 100.

MODULE status_0100 OUTPUT.
  SET PF-STATUS 'S100'.
  IF go_grid1 IS INITIAL.                      " 처음 한 번만 생성
    go_cont1 = NEW #( container_name = 'CC_ALV' ).
    go_grid1 = NEW #( i_parent = go_cont1 ).
    DATA(lt_fcat) = VALUE lvc_t_fcat(
      ( fieldname = 'CARRID'     ref_table = 'SFLIGHT' key = abap_true )
      ( fieldname = 'CONNID'     ref_table = 'SFLIGHT' key = abap_true )
      ( fieldname = 'FLDATE'     ref_table = 'SFLIGHT' key = abap_true )
      ( fieldname = 'PRICE'      ref_table = 'SFLIGHT' cfieldname = 'CURRENCY' )
      ( fieldname = 'CURRENCY'   ref_table = 'SFLIGHT' )
      ( fieldname = 'SEATSMAX'   ref_table = 'SFLIGHT' coltext = '최대 좌석' )
      ( fieldname = 'SEATSOCC'   ref_table = 'SFLIGHT' coltext = '점유 좌석' do_sum = abap_true )
      ( fieldname = 'PAYMENTSUM' ref_table = 'SFLIGHT' cfieldname = 'CURRENCY' do_sum = abap_true ) ).
    DATA(ls_layo) = VALUE lvc_s_layo( zebra = abap_true cwidth_opt = abap_true
                                      sel_mode = 'A' grid_title = '항공편 목록' ).
    DATA(lt_sort) = VALUE lvc_t_sort( ( spos = 1 fieldname = 'CARRID' up = abap_true subtot = abap_true ) ).
    go_events = NEW #( ).
    SET HANDLER go_events->on_double_click FOR go_grid1.
    go_grid1->set_table_for_first_display(
      EXPORTING  is_layout       = ls_layo
      CHANGING   it_outtab       = gt_fl
                 it_fieldcatalog = lt_fcat
                 it_sort         = lt_sort
      EXCEPTIONS OTHERS          = 1 ).
    IF sy-subrc <> 0.
      MESSAGE 'ALV 표시 오류' TYPE 'E'.
    ENDIF.
  ENDIF.
ENDMODULE.

MODULE user_command_0100 INPUT.
  DATA(lv_ok) = ok_code.
  CLEAR ok_code.
  CASE lv_ok.
    WHEN 'BACK' OR 'EXIT' OR 'CANC'.
      LEAVE TO SCREEN 0.
  ENDCASE.
ENDMODULE.

MODULE status_0200 OUTPUT.
  SET PF-STATUS 'S200'.
  IF go_grid2 IS INITIAL.
    go_cont2 = NEW #( container_name = 'CC_BOOK' ).
    go_grid2 = NEW #( i_parent = go_cont2 ).
    go_grid2->set_table_for_first_display(
      EXPORTING  i_structure_name = 'SBOOK'
                 is_layout        = VALUE lvc_s_layo( zebra = abap_true cwidth_opt = abap_true )
      CHANGING   it_outtab        = gt_book
      EXCEPTIONS OTHERS           = 1 ).
  ELSE.
    go_grid2->refresh_table_display( ).        " 두 번째부터는 새 데이터로 갱신
  ENDIF.
ENDMODULE.

MODULE user_command_0200 INPUT.
  lv_ok = ok_code.
  CLEAR ok_code.
  IF lv_ok = 'BACK'.
    LEAVE TO SCREEN 0.                         " CALL SCREEN 200 다음으로 복귀
  ENDIF.
ENDMODULE.
```
```abap
* 화면 0100
PROCESS BEFORE OUTPUT.
  MODULE status_0100.
PROCESS AFTER INPUT.
  MODULE user_command_0100.
* 화면 0200
PROCESS BEFORE OUTPUT.
  MODULE status_0200.
PROCESS AFTER INPUT.
  MODULE user_command_0200.
```
채점(100점): 전역 데이터 5 / PBO에서 IS INITIAL일 때만 생성 15 / 필드 카탈로그(ref_table, key, cfieldname, do_sum, coltext) 15 / 레이아웃(zebra, cwidth_opt, sel_mode) + lvc_t_sort 10 / set_table_for_first_display 10 / 핸들러(double_click, e_row) + SET HANDLER 15 / 화면 200: i_structure_name, refresh 15 / PAI: OK_CODE 백업·CLEAR, LEAVE TO SCREEN 0 10 / 흐름 로직 5.
**(7)** refresh를 빼면 첫 항공편의 예약이 계속 보인다. 그리드를 매번 새로 만들면 컨트롤이 겹쳐 쌓이므로 IS INITIAL 검사가 OO ALV 손코딩의 첫 채점 포인트다. `e_row-rowtype`이 비어 있지 않으면 소계·합계 행이며 `es_row_no-row_id`도 데이터 행 번호를 준다. `ref_field`를 비우면 fieldname과 같은 이름의 DDIC 필드를 참조해 제목·길이·통화 참조를 가져오며, 출력 테이블에 있어도 카탈로그에 없는 필드는 표시되지 않는다. 핸들러에서 `cl_gui_cfw=>set_new_ok_code( 'DETAIL' )`로 OK 코드를 넘기고 PAI에서 처리하는 방법도 정답. 화면이 열린 채 끝낼 때는 `go_cont1->free( )`로 해제하는 것이 정석이다(LEAVE PROGRAM 시 자동 정리되지만 명시하면 가산).

</details>

---

## 모듈풀(Dialog)

### B-017. 흐름 로직·입력 검사·화면 이동·OK_CODE [코드] ★★★
<!-- src: CL-018, CL-020, CL-021, MX-019, MX-020, TC-108, IB-059, CL-022 -->
좌석 요청 입력 트랜잭션(화면 0100에 필수 입력 필드, `GS_REQ-CARRID`, `GS_REQ-CONNID` 있음)을 만든다.

(1) PBO, PAI, POV, POH가 각각 언제 실행되며 주로 무엇을 하는지 쓰시오. POV/POH에서 화면에 아직 전달되지 않은 다른 필드 값이 필요하면?
(2) 흐름 로직 구문의 의미를 쓰시오: POV 아래 `FIELD f MODULE m.` / `MODULE exit AT EXIT-COMMAND.` / `FIELD f MODULE m ON INPUT.` / `ON REQUEST` / `CHAIN. FIELD: f1, f2. MODULE m ON CHAIN-REQUEST. ENDCHAIN.` / `MODULE m AT CURSOR-SELECTION.` / PAI의 `LOOP AT itab WITH CONTROL tc.` 또 `FIELD f MODULE m`과 `CHAIN`에서 E 메시지가 났을 때 화면 동작 차이, FIELD/CHAIN 없이 E를 보내면 어떻게 되는지 쓰시오.
(3) SE41 함수 유형과 의미의 연결이 옳지 않은 것은? ① `' '` 일반 함수, PAI 실행·OK_CODE 전달 ② `E` Exit command, AT EXIT-COMMAND가 입력 검사보다 먼저 ③ `T` 트랜잭션 호출 ④ `P` 탭스트립 로컬 탭 전환, PAI 없이 GUI에서 처리 ⑤ `S` 화면 입력 필드를 모두 지우는 클리어 함수.
(4) 필수 입력 필드가 있는 화면 100에서 "취소"를 누르면 "필수 항목을 입력하십시오"가 떠서 나갈 수 없다. 원인과 GUI status·흐름 로직·모듈 코드에서 할 일을 쓰시오.
(5) 화면 0100 PAI 코드에 대한 불만 (가) 저장 후 Enter만 눌렀는데 또 저장된다 (나) 필수 필드가 비면 CANC로 나갈 수 없다 (다) REFRESH를 몇 번 누른 뒤에는 BACK을 여러 번 눌러야 나간다. 원인과 고친 코드를 쓰시오.
```abap
MODULE user_command_0100 INPUT.
  CASE ok_code.
    WHEN 'SAVE'.      PERFORM save_data.
    WHEN 'REFRESH'.   PERFORM read_data.
                      CALL SCREEN 100.
    WHEN 'BACK' OR 'CANC'. LEAVE TO SCREEN 0.
  ENDCASE.
ENDMODULE.
```
(6) 각 화면 PBO는 PF-STATUS만 설정하고, 사용자는 화면마다 Enter를 한 번씩 누른다. 프로그램 종료 시 gv_log는?
```abap
START-OF-SELECTION.
  gv_log = gv_log && 'S'.
  CALL SCREEN 100.
  gv_log = gv_log && 'E'.
MODULE user_command_0100 INPUT.
  gv_log = gv_log && '1'.
  CALL SCREEN 200.
  gv_log = gv_log && '2'.
  SET SCREEN 0.
  LEAVE SCREEN.
  gv_log = gv_log && 'X'.
ENDMODULE.
MODULE user_command_0200 INPUT.
  gv_log = gv_log && '3'.
  LEAVE TO SCREEN 0.
  gv_log = gv_log && '4'.
ENDMODULE.
```
(7) 화면 이동 문장에 대한 설명으로 옳은 것은? ① 100의 PAI에서 `CALL SCREEN 200`, 200에서 `LEAVE TO SCREEN 0`이면 100의 PAI 중 CALL SCREEN 다음 문장으로 돌아온다 ② `SET SCREEN 200`을 실행하면 그 자리에서 PAI가 멈추고 200의 PBO로 간다 ③ `LEAVE TO SCREEN 200`은 호출 스택을 하나 더 쌓는다 ④ `CALL SCREEN 300 STARTING AT 10 5`로 팝업을 띄우려면 화면 300이 Normal이어야 한다.
(8) `GS_REQ-CARRID`, `GS_REQ-CONNID` 중 하나라도 바뀌면 SPFLI에 노선이 있는지 검사하고, 없으면 E 메시지로 두 필드를 모두 다시 입력 가능하게 하는 흐름 로직과 모듈을 작성하시오.

<details><summary>정답·해설</summary>

**(1)** PBO(Process Before Output): 화면 표시 직전, PF-STATUS·타이틀 설정, 필드 초기값, LOOP AT SCREEN 속성 변경, 컨트롤 생성. PAI(Process After Input): 사용자 동작(Enter, 버튼, 메뉴) 후, 입력 검사, OK_CODE 처리, 다음 화면 결정. POV(Process On Value-Request): F4, 직접 만든 입력 도움. POH(Process On Help-Request): F1, 직접 만든 도움말. POV/POH에서는 FIELD 문이 데이터 전송을 하지 않으므로 다른 필드 값은 `DYNP_VALUES_READ`로 읽는다.
**(2)** POV FIELD: f에서 F4를 누르면 m 실행. AT EXIT-COMMAND: 기능 코드 유형 E인 버튼에서 자동 필드 검사·다른 모듈보다 먼저 exit 실행. ON INPUT: f가 초기값이 아닐 때만. ON REQUEST: 이번 대화 단계에서 사용자가 f를 입력·변경했을 때만. CHAIN ... ON CHAIN-REQUEST: f1, f2 중 하나라도 변경되면 m 실행(`ON CHAIN-INPUT`은 하나라도 초기값이 아니면). AT CURSOR-SELECTION: 기능 코드가 CS(커서 선택: 더블클릭 등)일 때. LOOP AT itab WITH CONTROL tc: Table Control의 보이는 행마다 화면 값을 내부 테이블로(PBO에서도 같은 LOOP로 내부 테이블 → 화면). 화면 필드 값은 PAI에서 해당 FIELD 문을 만날 때 ABAP 변수로 전달된다. `FIELD f MODULE m`에서 E/W 메시지가 나면 그 필드 하나만, CHAIN 안 모듈에서 나면 체인에 속한 모든 필드가 다시 입력 가능해진다(관련 필드를 함께 수정). FIELD/CHAIN 없이 모듈에서 E를 보내면 모든 필드가 입력 불가로 화면이 다시 뜨므로 검증 모듈은 반드시 FIELD/CHAIN과 함께 쓴다. "CHAIN은 왜 쓰나"는 모듈풀 질문 단골이다.
**(3)** ⑤. `S`는 시스템 함수(인쇄·찾기 등 표준 시스템 기능)이며 입력 필드를 지우는 함수 유형은 없다. BACK/EXIT/CANC는 보통 E 유형으로 만들어 필수 입력 검사를 피하고 화면을 떠날 수 있게 한다.
**(4)** 원인: PAI가 시작되면 ABAP 모듈을 부르기 전에 자동 검사(필수 입력, 형식, 외래키/고정값)를 먼저 하므로 필수 필드가 비면 PAI 모듈까지 가지도 못한다. GUI status: 취소·뒤로·종료 기능 코드의 Function type을 `E`(Exit command)로. 흐름 로직: PAI 맨 앞에 `MODULE exit_0100 AT EXIT-COMMAND.`(E 유형 코드에서만 자동 검사를 건너뛰고 먼저 실행). 모듈:
```abap
MODULE exit_0100 INPUT.
  CASE ok_code.
    WHEN 'CANC' OR 'BACK' OR 'EXIT'.
      CLEAR ok_code.
      LEAVE TO SCREEN 0.      " 또는 LEAVE PROGRAM
  ENDCASE.
ENDMODULE.
```
채점(4점): 원인(자동 검사가 PAI 모듈보다 먼저) 1, Function type E 1, AT EXIT-COMMAND 모듈 1, 화면을 떠나는 코드(`LEAVE TO SCREEN 0`/`SET SCREEN 0. LEAVE SCREEN.`/`LEAVE PROGRAM`) 1.
**(5)** (가) OK 필드를 비우지 않았다. Enter는 빈 함수 코드라 OK 필드를 덮어쓰지 않아 'SAVE'가 남는다 → 보조 변수에 복사하고 비운 뒤 평가. (나) CANC가 일반 PAI 모듈에서 처리되어 자동 입력 검사가 먼저 실행된다 → CANC(와 BACK)를 기능 유형 'E'로, `AT EXIT-COMMAND` 모듈에서 처리. (다) 같은 화면에서 `CALL SCREEN 100`을 호출해 화면 시퀀스가 중첩된다 → CALL SCREEN을 지운다(PAI가 끝나면 같은 화면이 다시 표시됨, 필요하면 `LEAVE TO SCREEN 100`).
```abap
* PROCESS AFTER INPUT.
*   MODULE exit_0100 AT EXIT-COMMAND.
*   MODULE user_command_0100.
MODULE exit_0100 INPUT.
  CASE ok_code.
    WHEN 'BACK' OR 'CANC'.
      CLEAR ok_code.
      LEAVE TO SCREEN 0.
  ENDCASE.
ENDMODULE.
MODULE user_command_0100 INPUT.
  DATA(lv_code) = ok_code.
  CLEAR ok_code.
  CASE lv_code.
    WHEN 'SAVE'.    PERFORM save_data.
    WHEN 'REFRESH'. PERFORM read_data.
  ENDCASE.
ENDMODULE.
```
정석은 "복사 → CLEAR → 복사본으로 CASE"이며 sy-ucomm 대신 화면 OK 필드 변수를 쓰고 시스템 필드를 직접 바꾸지 않는다.
**(6)** `S132E`. 'S' → CALL SCREEN 100(새 시퀀스) → 0100 PAI '1' → CALL SCREEN 200(중첩 시퀀스) → 0200 PAI '3' → `LEAVE TO SCREEN 0`(= `SET SCREEN 0` + `LEAVE SCREEN`)으로 즉시 떠나 중첩 시퀀스 종료, '4' 실행 안 됨, CALL SCREEN 200 다음으로 복귀 → '2' → `SET SCREEN 0`(다음 화면만 지정) → `LEAVE SCREEN`(즉시 떠남), 'X' 실행 안 됨, 시퀀스 종료 → 'E'. CALL SCREEN은 새 시퀀스를 쌓고 끝나면 호출 지점으로 돌아온다(최대 50단계). SET SCREEN은 다음 화면만 바꾸고 PAI 끝까지 계속 실행, LEAVE SCREEN은 즉시 이동.
**(7)** ①. ② SET SCREEN은 다음 화면 번호만 바꾸며 현재 모듈과 PAI는 끝까지 실행된 뒤 이동한다(즉시 떠나려면 LEAVE SCREEN을 붙이거나 LEAVE TO SCREEN). ③ LEAVE TO SCREEN은 같은 시퀀스 안에서 화면만 바꾸며 스택을 쌓지 않는다. ④ 팝업은 Screen type이 Modal dialog box여야 한다.
**(8)**
```
PROCESS AFTER INPUT.
  MODULE exit_0100 AT EXIT-COMMAND.
  CHAIN.
    FIELD: gs_req-carrid, gs_req-connid.
    MODULE check_connection ON CHAIN-REQUEST.
  ENDCHAIN.
  MODULE user_command_0100.
```
```abap
MODULE check_connection INPUT.
  SELECT SINGLE @abap_true FROM spfli
    WHERE carrid = @gs_req-carrid AND connid = @gs_req-connid
    INTO @DATA(lv_exists).
  IF sy-subrc <> 0.
    MESSAGE |Connection { gs_req-carrid } { gs_req-connid } does not exist| TYPE 'E'.
  ENDIF.
ENDMODULE.
```
E 메시지가 나면 PAI가 멈추고 같은 화면이 다시 표시되며 CHAIN 안 필드만 입력 가능(나머지는 잠김). ON CHAIN-REQUEST로 변경이 있을 때만 DB를 읽고, 존재 확인은 `SELECT SINGLE @abap_true`처럼 필드를 최소화한다.

</details>

---

### B-018. Table Control·탭스트립·Subscreen·팝업·화면 속성 [코드] ★★
<!-- src: CL-019, IB-060, IB-061, IB-062, IB-063, IB-058 -->
항공편 유지보수 화면 0100에 Table Control `TC_FLIGHT`, subscreen 영역 `SUB1`, 저장 확인 팝업을 넣는다.

(1) 빈칸을 채우시오.
```abap
DATA: gt_flight TYPE STANDARD TABLE OF sflight, gs_flight TYPE sflight, ok_code TYPE sy-ucomm.
____(1)____ tc_flight TYPE TABLEVIEW USING SCREEN 0100.
MODULE status_0100 OUTPUT.
  SET PF-STATUS 'S100'.
  tc_flight-____(2)____ = lines( gt_flight ).
ENDMODULE.
MODULE fill_tc OUTPUT.
  READ TABLE gt_flight INTO gs_flight INDEX tc_flight-____(3)____.
  IF sy-subrc <> 0.
    EXIT FROM STEP-LOOP.
  ENDIF.
ENDMODULE.
```
```
PROCESS BEFORE OUTPUT.
  MODULE status_0100.
  LOOP WITH CONTROL tc_flight.
    MODULE fill_tc.
  ENDLOOP.
PROCESS AFTER INPUT.
  MODULE exit_0100 ____(4)____.
  LOOP WITH CONTROL tc_flight.
    CHAIN.
      FIELD: gs_flight-seatsmax, gs_flight-seatsocc.
      MODULE check_seats ____(5)____.
    ENDCHAIN.
    MODULE modify_tc.
  ENDLOOP.
  MODULE user_command_0100.
PROCESS ON ____(6)____.
  FIELD gs_flight-carrid MODULE f4_carrid.
```
(2) (1)에서 current_line의 계산, modify_tc의 코드, `lines`를 설정하지 않을 때의 문제를 쓰시오.
(3) 탭스트립의 GUI(로컬) 페이징과 서버 페이징을 subscreen 영역 개수, PBO 처리, 탭 클릭 시 PAI, 장단점으로 비교하고 선언문을 쓰시오.
(4) gv_dynnr(0110 또는 0120)에 따라 다른 subscreen을 보여 주는 흐름 로직의 빈칸을 채우고(`CALL SUBSCREEN sub1 (가) sy-repid gv_dynnr.` / PAI `CALL SUBSCREEN (나).`), PAI의 CALL SUBSCREEN을 빠뜨리면 어떻게 되는지, subscreen 화면에서 할 수 없는 것 두 가지 이상을 쓰시오.
(5) 조회 모드(gv_mode = 'D')일 때 그룹 EDT 필드를 입력 불가로 만들려 했으나 바뀌지 않는다. 두 가지 잘못을 고치시오. SCREEN 구조의 주요 필드도 쓰시오.
```abap
PROCESS BEFORE OUTPUT.
  MODULE status_0100.
PROCESS AFTER INPUT.
  MODULE user_command_0100.
  MODULE set_screen_attr.
MODULE set_screen_attr INPUT.
  LOOP AT SCREEN.
    IF screen-group1 = 'EDT' AND gv_mode = 'D'.
      screen-input = '0'.
    ENDIF.
  ENDLOOP.
ENDMODULE.
```
(6) 화면 0200(Modal dialog box)을 (10, 5)~(70, 15)에 띄우는 문장의 빈칸 `CALL SCREEN 0200 (가) 10 5 (나) 70 15.`과, POPUP_TO_CONFIRM에서 "예"일 때의 answer 값 및 다른 값의 의미, 팝업 화면을 닫는 방법을 쓰시오.
(7) 옳지 않은 것은? ① 실행형 프로그램의 기본 선택 화면 번호는 1000 ② 화면 유형에는 Normal, Subscreen, Modal dialog box가 있다 ③ Subscreen은 다른 화면의 subscreen 영역 안에 표시된다 ④ Modal dialog box는 반드시 전체 창 크기로 표시된다 ⑤ `SELECTION-SCREEN BEGIN OF SCREEN 500.`으로 추가 선택 화면을 정의하고 `CALL SELECTION-SCREEN 500`으로 띄울 수 있다.

<details><summary>정답·해설</summary>

**(1)** (1) `CONTROLS` (2) `lines` (3) `current_line` (4) `AT EXIT-COMMAND` (5) `ON CHAIN-REQUEST` (6) `VALUE-REQUEST`. Table Control은 `CONTROLS ... TYPE TABLEVIEW`로 선언하고 PBO와 PAI 양쪽에 `LOOP WITH CONTROL`(또는 `LOOP AT itab ... WITH CONTROL`)이 있어야 한다. 루프 한 번이 화면에 보이는 한 행이다.
**(2)** `current_line` = top_line + 루프 인덱스 − 1(현재 루프 행의 내부 테이블 인덱스). PBO에서 데이터가 끝나면 `EXIT FROM STEP-LOOP`. modify_tc: `MODIFY gt_flight FROM gs_flight INDEX tc_flight-current_line.` `lines`를 설정하지 않으면 스크롤 바가 내부 테이블 크기를 반영하지 않는다.
**(3)**

| 항목 | GUI(로컬) 페이징 | 서버 페이징 |
|---|---|---|
| subscreen 영역 | 탭마다 하나씩 | 모든 탭이 하나의 영역 공유 |
| PBO | 모든 탭의 subscreen을 한 번에 CALL SUBSCREEN | 활성 탭의 subscreen 하나만 |
| 탭 클릭 | PAI 없음(함수 유형 P) | PAI 발생 → `tab-activetab`과 subscreen 번호 변경 |
| 장점 | 탭 전환이 빠름 | 필요한 탭만 처리, 전환 시 검사 가능 |
| 단점 | 처음에 모든 탭 데이터를 보내 무거움, 전환 시 검사 불가 | 클릭마다 서버 왕복 |

선언: `CONTROLS tabs TYPE TABSTRIP.` Tabstrip Control Wizard가 기본 코드를 만들어 준다.
**(4)** (가) `INCLUDING` (나) `sub1`. PAI에도 CALL SUBSCREEN을 써야 subscreen의 PAI(필드 이동, 검사)가 실행되며, 빠뜨리면 subscreen 입력값이 프로그램으로 넘어오지 않는다. 할 수 없는 것: 자체 OK_CODE 필드를 가질 수 없다, `SET PF-STATUS`/`SET TITLEBAR` 불가, `MODULE ... AT EXIT-COMMAND` 불가, `SET SCREEN`/`LEAVE SCREEN`으로 흐름 변경 불가. 다른 프로그램의 subscreen을 넣으면 그 프로그램의 전역 데이터를 쓰므로 데이터 교환에 주의한다(Screen Exit).
**(5)** ① 화면 속성 변경은 PBO에서 해야 한다(PAI에서 바꿔도 화면을 다시 보내기 전에 PBO가 속성을 초기화) → `MODULE set_screen_attr OUTPUT.`으로 바꾸고 PBO에서 호출. ② `MODIFY SCREEN`이 없어 작업 영역만 바뀌었다.
```abap
PROCESS BEFORE OUTPUT.
  MODULE status_0100.
  MODULE set_screen_attr.
MODULE set_screen_attr OUTPUT.
  LOOP AT SCREEN.
    IF screen-group1 = 'EDT' AND gv_mode = 'D'.
      screen-input = '0'.
      MODIFY SCREEN.
    ENDIF.
  ENDLOOP.
ENDMODULE.
```
SCREEN 필드: name, group1~group4, required, input, output, intensified, invisible, active. 화면 필드 그룹은 Screen Painter 속성에서 지정한다(선택 화면은 MODIF ID).
**(6)** (가) `STARTING AT` (나) `ENDING AT`. answer `'1'`(첫 번째 버튼, 기본 "Yes"), `'2'`(두 번째 버튼, "No"), `'A'`(취소). 팝업을 닫을 때는 `LEAVE TO SCREEN 0` 또는 `SET SCREEN 0. LEAVE SCREEN.`으로 호출한 화면으로 돌아간다.
**(7)** ④. Modal dialog box는 `CALL SCREEN nnnn STARTING AT x y ENDING AT x2 y2`로 팝업 창 크기·위치를 지정한다. 선택 화면 번호 1000은 예약되어 일반 화면 번호로 쓰지 않는다.

</details>

---

### B-019. 모듈풀 실행·트랜잭션 유형·화면 용어 [개념] ★★
<!-- src: IB-056, IB-057, TC-011, TC-095 -->
모듈풀 프로그램 `SAPMZFLREQ`를 업무 사용자에게 배포한다.

(1) 리포트(유형 1)와 모듈풀(유형 M)의 차이를 실행 방법, 화면, 흐름 제어, 이름 규칙(include 포함) 측면에서 쓰시오.
(2) SE93에서 고르는 시작 객체(트랜잭션 유형) 5가지와 각각 무엇을 시작하는지 쓰시오.
(3) 특정 Z 테이블의 SM30 화면을 바로 여는 트랜잭션은 어떤 유형으로 어떻게 만드는가?
(4) T-code 정보가 저장되는 테이블, 트랜잭션 시작 시 검사하는 권한 객체, SE93에서 추가로 지정할 수 있는 것을 쓰시오.
(5) 용어를 쓰시오: 화면 레이아웃 + 흐름 로직의 화면 단위 / 메뉴 바·표준 툴바·애플리케이션 툴바·기능 키 묶음 / 기능 코드를 받는 OK 유형 필드의 관례적 이름 / 다른 화면 영역에 끼우는 화면 유형 / 팝업 화면 유형 / 표 형태 여러 행 입력 요소 / 탭으로 서브스크린을 전환하는 요소. 제목 설정 문장도 쓰시오.

<details><summary>정답·해설</summary>

**(1)**

| 항목 | 리포트(유형 1) | 모듈풀(유형 M) |
|---|---|---|
| 실행 | SE38에서 F8로 직접, SUBMIT | 직접 실행 불가. Dialog 트랜잭션(SE93: 프로그램 + 시작 화면 번호) 또는 CALL SCREEN |
| 화면 | 선택 화면(자동 생성, 1000) + 리스트/ALV | Screen Painter로 만든 여러 화면과 흐름 로직(PBO/PAI) |
| 흐름 제어 | 런타임이 이벤트(INITIALIZATION, START-OF-SELECTION...)를 순서대로 호출 | 화면 흐름(Next Screen, SET SCREEN, CALL SCREEN)을 개발자가 제어 |
| 이름 | Z... | 관례상 SAPMZ...(Include: MZ...TOP, MZ...O01, MZ...I01, MZ...F01) |

모듈풀은 여러 화면에 걸친 입력·변경 트랜잭션(VA01 같은)에 쓰며, S/4HANA 신규 개발은 Fiori/RAP로 대체되는 추세다.
**(2)** ① Program and screen(Dialog transaction): 모듈풀 + 시작 화면 번호 ② Program and selection screen(Report transaction): 실행 프로그램 + 선택 화면(기본 1000), 변형 지정 가능 ③ Method of a class(OO transaction): 글로벌 클래스 메서드(또는 ABAP Objects Services) ④ Transaction with variant(Variant transaction): 기존 트랜잭션 + 트랜잭션 변형(SHD0로 필드 숨김·기본값) ⑤ Transaction with parameters(Parameter transaction): 기존 트랜잭션 + 화면 필드 기본값, 초기 화면 건너뛰기.
**(3)** Parameter transaction: 트랜잭션 SM30, "Skip initial screen" 체크, 기본값 `VIEWNAME = ZIB_TABLE`(대상 테이블), `UPDATE = X`.
**(4)** TSTC(텍스트 TSTCT). 시작 시 S_TCODE를 검사하고, SE93에 지정한 추가 권한 객체도 검사할 수 있다. GUI 지원(SAP GUI for HTML/Windows) 플래그도 설정한다.
**(5)** Dynpro(Dynamic Program, 화면) / GUI Status / OK_CODE(ok_code) / Subscreen / Modal dialog box / Table Control / Tabstrip Control. 화면 유형은 Normal, Subscreen, Modal dialog box(그리고 선택 화면). 함수 코드 유형 `E` 버튼은 `MODULE ... AT EXIT-COMMAND`로 필드 검사 전에 처리된다. 제목은 GUI Title(`SET TITLEBAR`).

</details>

---

## 모듈화·함수 모듈

### B-020. 모듈화 기법·FORM 파라미터·함수 그룹 전역 데이터 [코드] ★★
<!-- src: CL-023, CL-024, IB-011, IB-064, IB-066, MX-016, IB-070 -->
함수 그룹 ZFG_CNT의 TOP include에 `DATA gv_cnt TYPE i.`가 있고 FM `Z_CNT_ADD`는 `gv_cnt = gv_cnt + 1. ev_cnt = gv_cnt.`(EXPORTING VALUE(ev_cnt) TYPE i)이다.

```abap
REPORT zp1.
DATA lv_cnt TYPE i.
START-OF-SELECTION.
  DO 3 TIMES.
    CALL FUNCTION 'Z_CNT_ADD' IMPORTING ev_cnt = lv_cnt.
  ENDDO.
  " ①
  SUBMIT zp2 AND RETURN.          " ZP2: CALL FUNCTION 'Z_CNT_ADD' 한 번 → ②
  CALL FUNCTION 'Z_CNT_ADD' IMPORTING ev_cnt = lv_cnt.
  " ③
```

(1) ZP1 실행 시 ①, ②, ③의 lv_cnt를 쓰고 이유를 설명하시오. 이 성질을 이용한 패턴과, RFC로 부를 때의 차이는?
(2) 다음 FORM을 실행했을 때 ①②의 gv_a_in·gv_d_in, PERFORM 후 a, b, c, d를 쓰시오. 같은 로직을 `METHODS calc IMPORTING p1 TYPE i ...`(VALUE 없이)로 옮겨 `p1 = p1 + 10.`을 쓰면?
```abap
DATA: a TYPE i VALUE 1, b TYPE i VALUE 1, c TYPE i VALUE 1, d TYPE i VALUE 1,
      gv_a_in TYPE i, gv_d_in TYPE i.
START-OF-SELECTION.
  PERFORM calc USING a b CHANGING c d.
FORM calc USING p1 TYPE i VALUE(p2) TYPE i
          CHANGING p3 TYPE i VALUE(p4) TYPE i.
  p1 = p1 + 10.  p2 = p2 + 10.  p3 = p3 + 10.  p4 = p4 + 10.
  gv_a_in = a.      " ①
  gv_d_in = d.      " ②
ENDFORM.
```
(3) ABAP 모듈화 기법을 소스 코드 모듈화와 프로시저로 나누어 쓰고 장점 3가지와 현재 권장 순서를 쓰시오.
(4) 매크로와 서브루틴(FORM)을 정의, 동작, 파라미터, 디버깅, 범위로 비교하시오.
(5) 함수 그룹이 필요한 이유, 함수 그룹 ZIB_FG를 만들면 생기는 메인 프로그램과 include 이름·역할, 같은 그룹의 FM A가 전역 변수를 바꾼 뒤 FM B에서 그 값이 보이는지 쓰시오.
(6) FM 파라미터에 대해 옳지 않은 것을 각각 고르시오.
[가] ① RFC 가능 FM의 파라미터는 모두 값 전달 ② 참조 전달 IMPORTING은 FM 안에서 바꿀 수 없다 ③ 같은 함수 그룹 FM들은 TOP 전역 데이터를 공유하고 같은 내부 세션에서 호출 사이에 유지된다 ④ CHANGING은 참조 전달만 가능하고 값 전달로 선언할 수 없다 ⑤ TABLES는 구식이며 테이블 타입 IMPORTING/EXPORTING/CHANGING을 권장한다.
[나] ① RFC FM 파라미터는 모두 값 전달 ② TABLES는 obsolete지만 RFC·BAPI에서는 흔하다 ③ 선택 IMPORTING이 전달됐는지 `IS SUPPLIED`로 확인 ④ CHANGING은 FM 안에서 읽을 수 없고 쓰기만 가능 ⑤ 값 전달 EXPORTING은 FM이 정상 종료될 때만 복사된다.

<details><summary>정답·해설</summary>

**(1)** ① 3, ② 1, ③ 4. 함수 그룹은 처음 호출될 때 호출한 프로그램의 내부 세션(internal session)에 로드되고 전역 데이터는 그 내부 세션이 끝날 때까지 유지되므로 1, 2, 3으로 누적된다. `SUBMIT ... AND RETURN`은 새 내부 세션을 열어 ZP2에서 함수 그룹이 새로 로드되고 gv_cnt가 0부터 시작(→ 1), ZP2가 끝나면 그 세션과 함께 사라진다. ZP1로 돌아오면 원래 세션의 3이 그대로라 4. 같은 그룹의 다른 FM들도 전역 데이터를 공유하므로 "SET FM으로 넣고 GET FM으로 꺼내는" 버퍼 패턴을 만든다. RFC로 원격 호출하면 원격 시스템의 별도 세션에서 실행된다.
**(2)** gv_a_in = 11, gv_d_in = 1. a = 11, b = 1, c = 11, d = 11. 메서드 IMPORTING(참조) 변경은 문법 오류.

| 형식 파라미터 | 전달 방식 | 실제 파라미터 반영 |
|---|---|---|
| USING p1 | 참조 | 즉시(같은 메모리) |
| USING VALUE(p2) | 값 | 반영 안 됨 |
| CHANGING p3 | 참조 | 즉시 |
| CHANGING VALUE(p4) | 값 + 결과 반환 | FORM이 정상 종료될 때 복사 |

①에서 p1은 a 자체라 a가 이미 11, ②에서 p4는 복사본이라 d는 아직 1. 메시지 등으로 비정상 종료되면 p4가 복사되지 않는다. FORM의 USING 참조 파라미터 변경은 기술적으로 가능하지만(확장 검사 경고) 바꿀 값은 CHANGING으로 받는다. 메서드에서 IMPORTING(참조)은 읽기 전용, EXPORTING/CHANGING/RETURNING으로 값을 돌려주고 RETURNING은 항상 값 전달이다. FORM은 obsolete이며 신규 개발은 메서드.
**(3)** 소스 코드 모듈화(호출 개념 없음): Include, 매크로. 프로시저(파라미터 인터페이스가 있는 호출 단위): 서브루틴(FORM), 함수 모듈, 메서드(로컬·글로벌). 장점: 재사용성, 가독성·유지보수성, 오류 범위 축소와 테스트 용이(단위 테스트), 개발 분담. 권장 순서: 메서드 > 함수 모듈(RFC·업데이트·BAPI처럼 FM만 가능한 경우) > FORM(obsolete). Include는 큰 프로그램을 나누는 용도이고 혼자 실행되지 않는다.
**(4)**

| 항목 | 매크로 | 서브루틴 |
|---|---|---|
| 정의 | `DEFINE name. ... END-OF-DEFINITION.` 사용 전에 먼저 정의 | `FORM ... ENDFORM.` 어디에 둬도 됨 |
| 동작 | 컴파일 시 텍스트 치환(`&1`~`&9`) | 런타임 호출(PERFORM), 스택 프레임 생성 |
| 파라미터 | 위치 치환, 타입 없음 | USING/CHANGING/TABLES, 타입 지정 |
| 디버깅 | 한 줄 단위로 들어가 볼 수 없음 | 단계별 가능 |
| 범위 | 정의한 프로그램 안(전역 매크로는 TRMAC 테이블) | 같은 프로그램, 외부 PERFORM으로 다른 프로그램에서도 |

매크로는 디버깅이 어렵고 가독성이 떨어져 권장하지 않으며(Clean ABAP), FORM도 obsolete다.
**(5)** FM은 독립 프로그램이 아니라 함수 그룹(프로그램 유형 F)에 속한 프로시저이고, 함수 그룹이 메모리 로드 단위이며 전역 데이터와 화면을 가진다. 메인 `SAPLZIB_FG`, 전역 데이터 `LZIB_FGTOP`, FM include 목록 `LZIB_FGUXX`(FM마다 `LZIB_FGU01`, `U02` ...), FORM용 `LZIB_FGF01`, PBO/PAI 모듈용 `LZIB_FGO01`/`I01`. 보인다: 같은 내부 세션 안에서 그룹은 한 번 로드되고 TOP 전역 데이터는 모든 FM이 공유하며 호출 사이에 유지된다. 한 FM을 호출하면 그룹 전체가 로드되므로 관련 없는 FM을 한 그룹에 몰지 않으며, 그룹 안 FM을 활성화할 때 그룹 전체 문법 오류가 영향을 준다.
**(6)** [가] ④: CHANGING도 "Pass Value"를 체크하면 값 전달(value and result)이 되며, 이때는 정상 종료 시에만 바뀐 값이 돌아가고 예외로 끝나면 돌아가지 않는다. ① RFC는 다른 시스템과 메모리를 공유할 수 없어 값 전달만 허용 ② 참조 전달 IMPORTING에 쓰면 문법 오류 ③ 전역 데이터는 같은 프로그램 안에서 계속 산다 ⑤ TABLES는 헤더 라인을 만들어 쓰지 않는 것이 좋다. [나] ④: CHANGING은 호출자의 값을 받아 읽고 바꾼 값을 돌려준다(입출력). ⑤ 값 전달 EXPORTING/CHANGING은 예외로 끝나면 복사되지 않고, 참조 전달은 FM 안에서 바꾸는 즉시 호출자 변수가 바뀐다.

</details>

---

### B-021. 함수 모듈 처리 유형·클래식 예외·PERFORM ON COMMIT [코드] ★★★
<!-- src: IB-065, TC-092, IB-067, IB-068, MX-017, IB-069 -->
SCARR에 'LH'는 있고 'XX'는 없다.

```abap
FUNCTION z_ib_check_carrier.
*"  IMPORTING VALUE(IV_CARRID) TYPE S_CARR_ID
*"  EXCEPTIONS NOT_FOUND INVALID_INPUT
  IF iv_carrid IS INITIAL.
    RAISE invalid_input.
  ENDIF.
  SELECT SINGLE @abap_true FROM scarr WHERE carrid = @iv_carrid INTO @DATA(lv_exists).
  IF sy-subrc <> 0.
    RAISE not_found.
  ENDIF.
ENDFUNCTION.

FUNCTION z_mx_div.
*"  IMPORTING VALUE(IV_A) TYPE I  VALUE(IV_B) TYPE I
*"  EXPORTING VALUE(EV_R) TYPE I
*"  EXCEPTIONS DIV_BY_ZERO
  ev_r = -1.
  IF iv_b = 0.
    RAISE div_by_zero.
  ENDIF.
  ev_r = iv_a DIV iv_b.
ENDFUNCTION.
```

(1) `Z_IB_CHECK_CARRIER`를 다음처럼 부를 때 sy-subrc(런타임 오류면 "런타임 오류")를 쓰시오. ① `iv_carrid = ''`, `EXCEPTIONS not_found = 1 OTHERS = 2` ② `'LH'`, `not_found = 1 invalid_input = 2` ③ `'XX'`, `not_found = 4 OTHERS = 8` ④ `'XX'`, `invalid_input = 1`.
(2) `DATA lv_r TYPE i VALUE 5.` 후 `Z_MX_DIV`를 `iv_a = 7 iv_b = 0`, `EXCEPTIONS div_by_zero = 3 OTHERS = 4`로 부르고 `WRITE: / sy-subrc, lv_r.`, 다시 `iv_b = 2`로 부르고 같은 출력을 할 때 결과를 쓰시오. 첫 호출에서 EXCEPTIONS 절을 빼면? EV_R이 참조 전달이었다면?
(3) 클래식 예외 발생 문장에 대해 옳은 것을 모두 고르시오. ① 호출자가 EXCEPTIONS에 지정했다면 `RAISE not_found.`는 FM을 끝내고 지정 값을 sy-subrc에 ② 처리하지 않으면(OTHERS도 없음) `RAISE`는 런타임 오류 RAISE_EXCEPTION ③ 처리하지 않으면 `MESSAGE e001(zib) RAISING not_found.`도 런타임 오류 ④ 처리하면 `MESSAGE ... RAISING`은 메시지를 표시하지 않고 sy-msgid, sy-msgno, sy-msgv1~4를 채운 채 돌아간다. 호출자가 FM의 메시지를 그대로 보여 주는 문장은?
(4) FM 처리 유형 3가지와 각각의 특징을 쓰시오.
(5) 업데이트 모듈의 시작 유형 4가지(Start immediately, Immediate start no restart, Start delayed, Collective run)를 V1/V2와 재시작 여부로 설명하고, 업데이트 모듈 파라미터 제약을 쓰시오.
(6) `PERFORM save_log ON COMMIT.`의 동작과 제약(실행 시점, 여러 번 등록, 파라미터, LEVEL, ROLLBACK), `PERFORM get_data IN PROGRAM zib_util IF FOUND.`의 의미와 위험을 쓰시오.

<details><summary>정답·해설</summary>

**(1)** ① 2: 빈 값 → INVALID_INPUT, 이름이 없으므로 OTHERS의 2. ② 0: 정상. ③ 4: NOT_FOUND, 지정 값 4(1부터 순서대로일 필요 없음). ④ 런타임 오류: NOT_FOUND가 났는데 EXCEPTIONS에 NOT_FOUND도 OTHERS도 없어 RAISE_EXCEPTION.
**(2)** 첫 출력 `3  5`, 둘째 `0  3`. RAISE로 끝나면 sy-subrc는 EXCEPTIONS에 지정한 3이고, EV_R이 값 전달이라 함수 안의 -1은 예외로 끝나 호출자에게 복사되지 않아 lv_r은 원래 5. 참조 전달이었다면 -1이 보였을 것이다. 두 번째는 7 DIV 2 = 3, 정상 종료라 0. EXCEPTIONS 절을 빼면 예외를 받을 곳이 없어 런타임 오류(덤프).
**(3)** ①, ②, ④. ③ MESSAGE ... RAISING은 호출자가 처리하지 않으면 런타임 오류 대신 일반 MESSAGE처럼 메시지를 보낸다(유형 E면 오류 메시지 표시). 처리하면 RAISE처럼 동작하며 sy-msg*를 채운다. 호출자는 `MESSAGE ID sy-msgid TYPE sy-msgty NUMBER sy-msgno WITH sy-msgv1 sy-msgv2 sy-msgv3 sy-msgv4.`로 FM이 준비한 메시지를 그대로 보여 준다. 새 개발에서는 클래스 기반 예외를 권장한다.
**(4)** Normal Function Module: 같은 시스템에서 일반 호출. Remote-Enabled Module: RFC로 다른 시스템에서 호출 가능, 파라미터는 값 전달·DDIC 참조 타입, BAPI도 이 유형. Update Module: `CALL FUNCTION ... IN UPDATE TASK`로 등록되어 COMMIT WORK 때 업데이트 work process에서 실행.
**(5)** Start immediately: V1, 오류 시 SM13에서 재시작 가능. Immediate start, no restart: V1, 재시작 불가. Start delayed: V2(모든 V1 완료 후, 통계·부가 데이터 등 비긴급). Collective run: V2이지만 RSM13005 등으로 모아서 일괄 실행. 업데이트 모듈은 나중에 다른 work process에서 실행되므로 EXPORTING·CHANGING(반환)을 가질 수 없고 IMPORTING/TABLES(값 전달)만 둔다.
**(6)** ON COMMIT: FORM을 바로 실행하지 않고 등록했다가 다음 `COMMIT WORK` 때 실행한다(업데이트 모듈 실행 전, 등록 순서대로, `LEVEL`로 순서 지정 가능). 같은 FORM을 여러 번 등록해도 한 번만 실행되며, 파라미터 인터페이스(USING/CHANGING)를 가질 수 없어 전역 데이터로 값을 전달한다. `ROLLBACK WORK`하면 등록이 취소되고 `ON ROLLBACK`으로 롤백 시 실행할 FORM도 등록할 수 있다. BAPI·업데이트 모듈과 함께 LUW 정리 작업에 쓰인다. IN PROGRAM ... IF FOUND: 외부 프로그램 ZIB_UTIL의 FORM get_data를 호출하며, 프로그램이나 FORM이 없으면 오류 없이 무시한다(IF FOUND가 없으면 런타임 오류). 외부 프로그램은 호출 프로그램의 프로그램 그룹에 로드되어 TABLES 작업 영역 등을 공유할 수 있다. 표준 프로그램 FORM을 외부 PERFORM으로 부르면 SAP이 내부 구현을 바꿀 때 깨지므로 피한다.

</details>

---

### B-022. 프로그램 호출·SUBMIT·SAP/ABAP 메모리 [코드] ★★
<!-- src: IB-013, IB-044, CL-036 -->
Parameter ID `CAR`는 데이터 엘리먼트 S_CARR_ID에 연결되어 있다.

```abap
REPORT zcl_mem_a.
DATA: gv TYPE i VALUE 10, lv_x TYPE i.
START-OF-SELECTION.
  EXPORT val = gv TO MEMORY ID 'ZCL_MEM'.
  SUBMIT zcl_mem_b AND RETURN.
  CLEAR gv.
  IMPORT val = gv FROM MEMORY ID 'ZCL_MEM'.       " ①
  IMPORT val = lv_x FROM MEMORY ID 'ZCL_NONE'.    " ②
  SET PARAMETER ID 'CAR' FIELD 'LH'.

REPORT zcl_mem_b.
DATA lv TYPE i.
START-OF-SELECTION.
  IMPORT val = lv FROM MEMORY ID 'ZCL_MEM'.
  lv = lv * 2.
  EXPORT val = lv TO MEMORY ID 'ZCL_MEM'.
```

(1) ① 직후 gv, ② 직후 sy-subrc와 lv_x를 쓰시오.
(2) A가 끝난 뒤 같은 로그온에서 새 창(새 외부 세션, /o)을 열어 `GET PARAMETER ID 'CAR' FIELD lv_c.`를 실행하면 lv_c는? 그 창에서 `IMPORT val = gv FROM MEMORY ID 'ZCL_MEM'.`의 sy-subrc는?
(3) SAP 메모리, ABAP 메모리, Shared Memory(Shared Objects)의 범위와 문법을 비교하시오. 함수 그룹 전역 데이터·클래스 정적 속성의 범위는?
(4) `CALL TRANSACTION`, `LEAVE TO TRANSACTION`, `SUBMIT ... AND RETURN`(및 AND RETURN 없음), `LEAVE PROGRAM`을 "새 내부 세션을 만드는가", "돌아오는가"로 비교하시오. CALL TRANSACTION의 첫 화면 건너뛰기와 권한 검사 옵션도 쓰시오.
(5) 리포트 ZIB_FLIGHT_LIST를 선택 조건과 함께 실행하고 출력 리스트를 메모리로 받는 빈칸을 채우시오.
```abap
SUBMIT zib_flight_list
  WITH p_carr = 'LH'
  WITH s_date ____(1)____ lr_date
  ____(2)____ LIST TO MEMORY
  AND RETURN.
CALL FUNCTION '____(3)____' TABLES listobject = lt_list EXCEPTIONS not_found = 1 OTHERS = 2.
```
(6) SUBMIT의 다른 추가 구문 4가지, 받은 리스트를 텍스트로 바꾸거나 출력하는 FM, ALV를 출력하는 리포트의 데이터를 가져오는 클래스를 쓰시오.

<details><summary>정답·해설</summary>

**(1)** gv = 20: B는 A와 같은 호출 체인이라 ABAP 메모리 'ZCL_MEM'을 공유하므로 10을 읽어 20으로 덮어쓴다. ②: 없는 ID를 IMPORT하면 sy-subrc = 4이고 lv_x는 바뀌지 않아 0.
**(2)** `LH`: SAP 메모리는 외부 세션 사이에서도 공유된다. sy-subrc = 4: ABAP 메모리는 외부 세션마다 따로라 새 창에는 없다.
**(3)**

| 구분 | 범위 | 문법 |
|---|---|---|
| SAP 메모리 | 사용자 로그온 세션 전체(모든 외부 세션 공유) | `SET/GET PARAMETER ID`, 화면 필드의 SPA/GPA |
| ABAP 메모리 | 하나의 외부 세션 안 호출 체인(SUBMIT AND RETURN, CALL TRANSACTION으로 이어진 내부 세션들) | `EXPORT ... TO MEMORY ID`, `IMPORT ... FROM MEMORY ID`, `FREE MEMORY ID` |
| Shared Memory | 애플리케이션 서버 전체(사용자 간 공유) | 영역 클래스(SHMA), `CREATE OBJECT ... AREA HANDLE`, attach_for_read/write |

함수 그룹 전역 데이터와 클래스 정적 속성은 내부 세션 범위다.
**(4)**

| 문장 | 새 내부 세션 | 돌아오는가 |
|---|---|---|
| `CALL TRANSACTION 'TC'` | 만든다(호출 스택에 쌓임) | 끝나면 다음 문장으로 |
| `LEAVE TO TRANSACTION 'TC'` | 현재 호출 순서를 모두 끝내고 새로 시작 | 안 돌아온다 |
| `SUBMIT prog AND RETURN` | 만든다 | 돌아온다. AND RETURN이 없으면 현재 내부 세션을 대체하고 안 돌아온다 |
| `LEAVE PROGRAM` | 없음 | 현재 프로그램(내부 세션)을 끝내고 호출한 곳으로 |

`AND SKIP FIRST SCREEN`은 SET PARAMETER로 채운 첫 화면을 건너뛴다. 새 내부 세션은 같은 외부 세션의 ABAP 메모리를 공유하므로 EXPORT/IMPORT TO MEMORY로 값을 넘길 수 있다. 새 트랜잭션 호출 시 S_TCODE 권한 검사가 있으며 `WITH AUTHORITY-CHECK`가 권장된다.
**(5)** (1) `IN` (2) `EXPORTING` (3) `LIST_FROM_MEMORY`. 범위 테이블은 `WITH sel IN rtab`, 단일 값은 `WITH p = val`.
**(6)** `VIA SELECTION-SCREEN`(선택 화면을 보여 줌), `USING SELECTION-SET 'VAR1'`(변형 사용), `TO SAP-SPOOL`(스풀로 출력), `VIA JOB ... NUMBER ...`(배치 잡 스텝 등록). 리스트는 `LIST_TO_ASCI`로 텍스트 변환, `WRITE_LIST`로 출력. ALV 리포트 데이터는 `CL_SALV_BS_RUNTIME_INFO`.

</details>

---

### B-023. 함수 모듈 작성·호출과 흔한 덤프·표준 FM [작성] ★★
<!-- src: HC-012, HC-013, TC-054 -->
함수 그룹 `ZHC_FG`에 `Z_HC_FLIGHT_SEATS`를 만든다. 요구: 항공사(필수), 노선(선택, 비우면 전체), 시작일(선택, 기본 오늘)을 받아 항공편 수와 빈 좌석 합계를 돌려주고, 항공편 목록을 TABLES 파라미터(SFLIGHT 구조)로 돌려준다. 항공사가 SCARR에 없으면 `CARRIER_NOT_FOUND`, 항공편이 없으면 `NO_FLIGHTS`.

(1) 파라미터 표(구분, 파라미터, 타입 지정, 참조 타입, 기본값, 선택, 값 전달)를 완성하고 처리 유형을 쓰시오.
(2) 함수 모듈 본문을 작성하시오.
(3) 선택화면 `p_carr`, `p_conn`으로 호출하고 건수·빈 좌석을 출력하며 예외별 메시지를 내는 프로그램을 작성하시오.
(4) 누군가 함수와 호출부를 아래처럼 바꿨다. 잘못된 곳을 모두 찾아 이유(문법/런타임/논리, 런타임 오류 이름 포함)와 함께 고치시오.
```abap
FUNCTION z_hc_flight_seats.
  SELECT * FROM sflight INTO TABLE et_flights
    WHERE carrid = iv_carrid AND fldate >= iv_date_from.
  ev_flights = sy-dbcnt.
  IF ev_flights = 0.
    MESSAGE '항공편 없음' TYPE 'E'.
  ENDIF.
  LOOP AT et_flights.
    ev_free_seats = et_flights-seatsmax - et_flights-seatsocc.
  ENDLOOP.
ENDFUNCTION.

REPORT zhc_call_bug.
PARAMETERS p_carr TYPE s_carr_id.
DATA: lv_cnt TYPE p LENGTH 8 DECIMALS 0,
      lt_fl  TYPE STANDARD TABLE OF spfli.
START-OF-SELECTION.
  CALL FUNCTION 'z_hc_flight_seats'
    IMPORTING iv_carrid  = p_carr
    EXPORTING ev_flights = lv_cnt
    TABLES    et_flights = lt_fl.
  WRITE: / lv_cnt.
```
(5) FM 호출 오류가 실행 시에야 드러나는 이유와 메서드와의 차이, 클래스 기반 예외와 EXCEPTIONS를 섞을 수 있는지, 새 FM에서 TABLES 대신 권장하는 방식을 쓰시오.
(6) 표준 FM 이름을 쓰시오: BAPI 커밋 / BAPI 롤백 / 앞 0 채우기 / 앞 0 제거 / 예·아니오 팝업 / 내부 테이블 F4 / SO10·긴 텍스트 읽기 / 번호 범위 채번 / Smart Form 함수 이름 얻기 / 클래식 ALV 그리드 / ALE Outbound IDoc 생성·분배 / 진행 표시줄.

<details><summary>정답·해설</summary>

**(1)**

| 구분 | 파라미터 | 타입 지정 | 참조 타입 | 기본값 | 선택 | 값 전달 |
|---|---|---|---|---|---|---|
| Import | IV_CARRID | TYPE | S_CARR_ID(CHAR 3) | | | ✓ |
| Import | IV_CONNID | TYPE | S_CONN_ID(NUMC 4) | | ✓ | ✓ |
| Import | IV_DATE_FROM | TYPE | S_DATE(DATS 8) | SY-DATUM | ✓ | ✓ |
| Export | EV_FLIGHTS | TYPE | I | | | ✓ |
| Export | EV_FREE_SEATS | TYPE | I | | | ✓ |
| Tables | ET_FLIGHTS | STRUCTURE(또는 LIKE) | SFLIGHT | | ✓ | (TABLES는 항상 참조) |
| Exceptions | CARRIER_NOT_FOUND, NO_FLIGHTS | | | | | |

처리 유형 Normal Function Module(원격 호출이 필요하면 Remote-Enabled: 모든 파라미터 값 전달, TABLES 허용).
**(2)**
```abap
FUNCTION z_hc_flight_seats.
*"  IMPORTING
*"     VALUE(IV_CARRID) TYPE  S_CARR_ID
*"     VALUE(IV_CONNID) TYPE  S_CONN_ID OPTIONAL
*"     VALUE(IV_DATE_FROM) TYPE  S_DATE DEFAULT SY-DATUM
*"  EXPORTING
*"     VALUE(EV_FLIGHTS) TYPE  I
*"     VALUE(EV_FREE_SEATS) TYPE  I
*"  TABLES
*"      ET_FLIGHTS STRUCTURE  SFLIGHT OPTIONAL
*"  EXCEPTIONS
*"      CARRIER_NOT_FOUND
*"      NO_FLIGHTS
  DATA: lr_connid TYPE RANGE OF s_conn_id,
        lt_fl     TYPE STANDARD TABLE OF sflight WITH EMPTY KEY.

  CLEAR: ev_flights, ev_free_seats.
  REFRESH et_flights.

  SELECT SINGLE carrid FROM scarr WHERE carrid = @iv_carrid INTO @DATA(lv_carrid).
  IF sy-subrc <> 0.
    RAISE carrier_not_found.
  ENDIF.
  IF iv_connid IS NOT INITIAL.
    lr_connid = VALUE #( ( sign = 'I' option = 'EQ' low = iv_connid ) ).
  ENDIF.
  SELECT * FROM sflight
    WHERE carrid = @iv_carrid
      AND connid IN @lr_connid               " 빈 RANGE면 조건 없음
      AND fldate >= @iv_date_from
    ORDER BY connid, fldate
    INTO TABLE @lt_fl.
  IF lt_fl IS INITIAL.
    MESSAGE e001(00) WITH '항공편 없음' RAISING no_flights.
  ENDIF.
  et_flights[]  = lt_fl.
  ev_flights    = lines( lt_fl ).
  ev_free_seats = REDUCE i( INIT n = 0 FOR ls IN lt_fl NEXT n = n + ls-seatsmax - ls-seatsocc ).
ENDFUNCTION.
```
**(3)**
```abap
REPORT zhc_call_fm.
PARAMETERS: p_carr TYPE s_carr_id OBLIGATORY,
            p_conn TYPE s_conn_id.
DATA: lt_fl TYPE STANDARD TABLE OF sflight, lv_cnt TYPE i, lv_free TYPE i.

START-OF-SELECTION.
  CALL FUNCTION 'Z_HC_FLIGHT_SEATS'
    EXPORTING  iv_carrid = p_carr  iv_connid = p_conn
    IMPORTING  ev_flights = lv_cnt  ev_free_seats = lv_free
    TABLES     et_flights = lt_fl
    EXCEPTIONS carrier_not_found = 1  no_flights = 2  OTHERS = 3.
  CASE sy-subrc.
    WHEN 0.
      WRITE: / '항공편 수:', lv_cnt, / '빈 좌석 합계:', lv_free.
      LOOP AT lt_fl INTO DATA(ls_fl).
        DATA(lv_seats) = ls_fl-seatsmax - ls_fl-seatsocc.
        WRITE: / ls_fl-connid, ls_fl-fldate, lv_seats.
      ENDLOOP.
    WHEN 1.
      MESSAGE |항공사 { p_carr }가 없습니다| TYPE 'S' DISPLAY LIKE 'E'.
    WHEN 2.
      MESSAGE ID sy-msgid TYPE 'S' NUMBER sy-msgno
              WITH sy-msgv1 sy-msgv2 sy-msgv3 sy-msgv4 DISPLAY LIKE 'E'.
    WHEN OTHERS.
      MESSAGE '알 수 없는 오류' TYPE 'S' DISPLAY LIKE 'E'.
  ENDCASE.
```
채점(100점): 파라미터 표(타입, OPTIONAL, DEFAULT, 값 전달, TABLES, EXCEPTIONS) 20 / 출력 초기화 5 / 존재 검사 + RAISE 15 / 선택 파라미터 처리(RANGE 또는 IS SUPPLIED/IS INITIAL) 15 / MESSAGE ... RAISING 또는 RAISE, 결과 계산 15 / 호출 방향과 OTHERS 20 / sy-subrc별 처리와 sy-msg 재사용 10. 호출 쪽 `EXPORTING`은 함수의 IMPORTING에 값을 보내는 것(방향이 반대)이 면접 최다 오답이다. 예외가 나면 값 전달 EXPORTING은 복사되지 않고 참조 전달과 TABLES는 이미 바뀐 내용이 남는다.
**(4)** 함수 본문: ① iv_connid 조건 무시 → RANGE를 만들어 `connid IN @lr_connid`. ② `MESSAGE ... TYPE 'E'`에 RAISING이 없어 호출자가 예외로 받을 수 없고 대화형에서는 오류 메시지로 멈춤(백그라운드·RFC에서는 실행 중단) → `RAISE no_flights.` 또는 `MESSAGE ... RAISING no_flights.` ③ 빈 좌석을 매 행 덮어써 마지막 값만 남음 → CLEAR 후 `ev_free_seats = ev_free_seats + ...`. ④ 출력 파라미터 초기화 없음(값 전달이라 문제는 작지만 TABLES는 호출자가 넘긴 기존 행 위에 덮어씀/유지) → `CLEAR: ev_flights, ev_free_seats. REFRESH et_flights.` 호출부: ⑤ 함수 이름이 소문자 리터럴, 이름은 대문자로 저장되므로 `CALL_FUNCTION_NOT_FOUND` → `'Z_HC_FLIGHT_SEATS'`. ⑥ IMPORTING/EXPORTING 방향이 반대 → `EXPORTING iv_carrid = p_carr IMPORTING ev_flights = lv_cnt`. ⑦ lv_cnt 타입 p가 함수의 TYPE i와 불일치 → `CALL_FUNCTION_CONFLICT_TYPE`, `DATA lv_cnt TYPE i.` ⑧ lt_fl이 SPFLI 행인데 TABLES는 `STRUCTURE sflight` → 구조 불일치 런타임 오류, `TYPE STANDARD TABLE OF sflight`. ⑨ EXCEPTIONS 절이 없어 `RAISE no_flights` 시 `RAISE_EXCEPTION` → `EXCEPTIONS carrier_not_found = 1 no_flights = 2 OTHERS = 3` 후 sy-subrc 처리. ⑩ p_carr가 필수가 아님 → `OBLIGATORY`. 채점: 항목당 10점(최대 100), ⑤~⑨는 런타임 오류 이름까지 쓰면 만점.
**(5)** FM은 이름을 문자열로 지정해 정적 호출 검사가 약하므로 철자·방향·타입 오류가 대부분 실행 시 덤프로 드러난다("CALL FUNCTION 할 때 흔한 덤프"). 메서드 호출은 이런 오류를 대부분 문법 검사에서 잡는다는 것이 OO를 권장하는 이유 중 하나다. 클래스 기반 예외(`RAISING zcx_...`)를 쓰는 FM은 EXCEPTIONS와 섞어 쓸 수 없다. TABLES는 구식(헤더 라인 있는 테이블)이지만 BAPI·RFC 때문에 시험에 나오며, 새 FM은 `EXPORTING VALUE(et_flights) TYPE flighttab` 같은 테이블 타입 파라미터를 권장한다.
**(6)** BAPI_TRANSACTION_COMMIT(`WAIT = 'X'`면 업데이트 완료까지 대기) / BAPI_TRANSACTION_ROLLBACK / CONVERSION_EXIT_ALPHA_INPUT / CONVERSION_EXIT_ALPHA_OUTPUT(문자열 템플릿 `|{ lv ALPHA = IN }|`/`ALPHA = OUT`으로도 가능) / POPUP_TO_CONFIRM / F4IF_INT_TABLE_VALUE_REQUEST / READ_TEXT / NUMBER_GET_NEXT / SSF_FUNCTION_MODULE_NAME / REUSE_ALV_GRID_DISPLAY / MASTER_IDOC_DISTRIBUTE / SAPGUI_PROGRESS_INDICATOR. ABAP Cloud에서는 대부분 쓸 수 없고 released API(예: `CL_NUMBERRANGE_RUNTIME`, EML)를 쓴다.

</details>

---

## LUW·업데이트·잠금

### B-024. Lock Object: 잠금 모드·ENQUEUE 결과·_SCOPE·잠금 순서 [코드] ★★★
<!-- src: CL-005, IB-027, HC-022 -->
SFLIGHT에 Lock Object `EZ_SFLIGHT`(키 MANDT, CARRID, CONNID, FLDATE)를 만들어 `ENQUEUE_EZ_SFLIGHT`/`DEQUEUE_EZ_SFLIGHT`가 생성되었다.

```abap
REPORT zcl_lock_test.
PARAMETERS p_mode TYPE enqmode DEFAULT 'E'.
DATA gv_log TYPE string.
START-OF-SELECTION.
  DO 2 TIMES.
    CALL FUNCTION 'ENQUEUE_EZ_SFLIGHT'
      EXPORTING  mode_sflight = p_mode  carrid = 'LH'  connid = '0400'  fldate = '20261020'
      EXCEPTIONS foreign_lock = 1  system_failure = 2  OTHERS = 3.
    gv_log = |{ gv_log }{ sy-subrc }|.
  ENDDO.
  WRITE gv_log.
```

(1) 다른 사용자의 잠금이 없을 때 `p_mode = 'E'`, `'X'`의 출력을 각각 쓰시오.
(2) 다른 사용자가 같은 키에 'E' 잠금을 걸고 있을 때 `p_mode = 'S'`의 첫 호출 sy-subrc와, 잠금 소유자 ID를 읽는 시스템 필드를 쓰시오. 잠금 모드 E, X, S, O의 특징을 정리하시오.
(3) 잠금은 어떤 성격의 잠금이며 어디서 확인하는가? ENQUEUE 없이 UPDATE하는 프로그램은 막을 수 있는가?
(4) ENQUEUE FM의 특수 파라미터 `_SCOPE`(1, 2, 3), `_WAIT`, `_COLLECT`의 의미와, 업데이트 태스크로 저장하는 프로그램에서 기본값 `_SCOPE = 2`의 의미를 쓰시오.
(5) 대기자를 확정(C)으로 바꾸는 다음 코드의 잘못을 모두 찾아 고치시오.
```abap
SELECT SINGLE * FROM zhc_waitlist
  WHERE carrid = @p_carr AND connid = @p_conn AND fldate = @p_date AND customid = @p_cust
  INTO @DATA(ls_wl).
ls_wl-status = 'C'.
CALL FUNCTION 'ENQUEUE_EZHC_WAITLIST'
  EXPORTING carrid = ls_wl-carrid connid = ls_wl-connid fldate = ls_wl-fldate customid = ls_wl-customid.
UPDATE zhc_waitlist FROM @ls_wl.
CALL FUNCTION 'DEQUEUE_EZHC_WAITLIST'
  EXPORTING carrid = ls_wl-carrid connid = ls_wl-connid fldate = ls_wl-fldate customid = ls_wl-customid.
COMMIT WORK.
```
(6) "lock object를 쓰는 올바른 순서"를 한 줄로 쓰시오.

<details><summary>정답·해설</summary>

**(1)** 'E' → `00`, 'X' → `01`. E(Exclusive, cumulative): 같은 소유자(같은 트랜잭션)는 같은 잠금을 여러 번 요청할 수 있어 두 번 모두 성공하며, 해제도 요청 횟수만큼 DEQUEUE해야 한다. X(Exclusive, non-cumulative): 같은 트랜잭션 안에서도 한 번만 걸 수 있어 두 번째는 FOREIGN_LOCK.
**(2)** sy-subrc = 1(FOREIGN_LOCK), 소유자 사용자명은 `sy-msgv1`. S(Shared)는 다른 사용자의 E 잠금과 충돌하고, S끼리는 여러 사용자가 동시에 가질 수 있다. O(Optimistic)도 있다.
**(3)** SAP의 논리적 잠금이며 SM12에서 확인·삭제한다. DB 갱신 자체를 막지 않으므로 ENQUEUE 없이 UPDATE하는 프로그램은 막지 못하고, 모든 프로그램이 같은 규칙(같은 잠금 객체)으로 ENQUEUE해야 의미가 있다.
**(4)** `_SCOPE = 1`: 잠금이 호출 프로그램(dialog)에만 속해 업데이트 태스크로 넘어가지 않고, DEQUEUE하거나 프로그램이 끝날 때 풀린다. `_SCOPE = 2`(기본): COMMIT WORK로 업데이트 요청을 등록하면 소유권이 업데이트 프로그램으로 넘어가 업데이트가 끝나면 자동 해제, 업데이트 요청이 없으면 프로그램 종료 시 해제. `_SCOPE = 3`: 프로그램과 업데이트 태스크 양쪽이 가져 둘 다 끝나야 풀림. `_WAIT = 'X'`: 충돌 시 즉시 FOREIGN_LOCK을 내지 않고 일정 시간(시스템 파라미터) 재시도. `_COLLECT = 'X'`: 로컬 잠금 컨테이너에 모았다가 `FLUSH_ENQUEUE`로 한 번에 보냄. 기본값 2의 의미: 화면에서 잠금 → 수정 → COMMIT WORK까지 유지되고 DB 반영이 끝나는 시점에 자동으로 풀려, 업데이트가 끝나기 전 다른 사용자가 같은 데이터를 바꾸는 것을 막는다.
**(5)**

| # | 문제 | 수정 |
|---|---|---|
| 1 | 잠그기 전에 읽음, 사이에 다른 사용자가 바꾼 내용을 덮어쓸 수 있음 | ENQUEUE → SELECT |
| 2 | SELECT SINGLE의 sy-subrc 미확인, 행이 없으면 빈 키로 ENQUEUE/UPDATE | `IF sy-subrc <> 0. ... RETURN.` |
| 3 | ENQUEUE에 EXCEPTIONS 없음, foreign_lock을 받을 곳이 없어 런타임 오류(RAISE_EXCEPTION) | `EXCEPTIONS foreign_lock = 1 system_failure = 2 OTHERS = 3`, sy-subrc 확인 |
| 4 | 현재 상태 확인 없음, 이미 취소(X)·확정된 행도 C로 바꿈 | `IF ls_wl-status <> 'W'.` 거부 |
| 5 | 전체 행 UPDATE, 읽은 뒤 다른 필드가 바뀌었으면 옛 값으로 덮어씀 | 잠근 뒤 읽기, 또는 `UPDATE ... SET status = 'C' WHERE ...` |
| 6 | UPDATE 결과 확인과 실패 시 ROLLBACK 없음 | `IF sy-subrc = 0. COMMIT WORK. ELSE. ROLLBACK WORK. ENDIF.` |
| 7 | COMMIT 전에 DEQUEUE, 해제와 커밋 사이에 다른 사용자가 잠금을 얻어 커밋 전 옛 데이터를 읽을 수 있음 | COMMIT 뒤 DEQUEUE(또는 업데이트 태스크 + `_scope = '2'`) |

```abap
CALL FUNCTION 'ENQUEUE_EZHC_WAITLIST'
  EXPORTING  carrid = p_carr  connid = p_conn  fldate = p_date  customid = p_cust
  EXCEPTIONS foreign_lock = 1  system_failure = 2  OTHERS = 3.
IF sy-subrc <> 0.
  MESSAGE |잠금 실패: { sy-msgv1 }| TYPE 'S' DISPLAY LIKE 'E'.
  RETURN.
ENDIF.
SELECT SINGLE status FROM zhc_waitlist
  WHERE carrid = @p_carr AND connid = @p_conn AND fldate = @p_date AND customid = @p_cust
  INTO @DATA(lv_status).
IF sy-subrc = 0 AND lv_status = 'W'.
  UPDATE zhc_waitlist SET status = 'C'
    WHERE carrid = @p_carr AND connid = @p_conn AND fldate = @p_date AND customid = @p_cust.
  IF sy-subrc = 0.
    COMMIT WORK.
  ELSE.
    ROLLBACK WORK.
  ENDIF.
ELSE.
  MESSAGE '확정할 대기 건이 없습니다' TYPE 'S' DISPLAY LIKE 'E'.
ENDIF.
CALL FUNCTION 'DEQUEUE_EZHC_WAITLIST'
  EXPORTING carrid = p_carr connid = p_conn fldate = p_date customid = p_cust.
```
채점: 항목당 13점(7개 91점) + 수정 코드 9점.
**(6)** ENQUEUE → 최신 데이터 읽기 → 검사·변경 → COMMIT(업데이트 태스크면 커밋이 잠금 해제까지 처리) → DEQUEUE.

</details>

---

### B-025. SAP LUW·업데이트 태스크·COMMIT 순서·번호 범위 [코드] ★★★
<!-- src: CL-025, CL-026, CL-027, MX-028, MX-032 -->
Z_UPD_X, Z_UPD_Z는 V1, Z_UPD_Y는 V2 업데이트 모듈이고 f_a, f_b는 FORM이다.

```abap
START-OF-SELECTION.
  PERFORM f_a ON COMMIT.
  CALL FUNCTION 'Z_UPD_X' IN UPDATE TASK EXPORTING iv_no = 1.
  PERFORM f_b ON COMMIT.
  CALL FUNCTION 'Z_UPD_Y' IN UPDATE TASK EXPORTING iv_no = 2.
  CALL FUNCTION 'Z_UPD_Z' IN UPDATE TASK EXPORTING iv_no = 3.
  PERFORM f_a ON COMMIT.
  COMMIT WORK.
```

(1) DB LUW와 SAP LUW의 차이를 설명하고, DB LUW가 암묵적으로 커밋되는 경우를 3가지 이상 쓰시오. 여러 화면에 걸친 변경을 `IN UPDATE TASK`로 저장하는 이유는?
(2) V1과 V2의 차이, `COMMIT WORK`와 `COMMIT WORK AND WAIT`의 차이, `SET UPDATE TASK LOCAL`의 효과, 업데이트 오류 확인 T-code를 쓰시오.
(3) 위 코드에서 COMMIT WORK 이후 실행 순서(f_a 횟수 포함)를 쓰시오. 마지막 줄이 `ROLLBACK WORK.`이면? COMMIT 후 Z_UPD_Z에서 런타임 오류가 나면 Z_UPD_X와 Z_UPD_Y의 변경은?
(4) 다음 업데이트 FM(V1)과 호출 코드의 문제를 모두 찾아 고치시오. 업데이트 FM에서 쓸 수 없는 문장도 쓰시오.
```abap
FUNCTION z_cl_upd_req.
*"  IMPORTING VALUE(is_req) TYPE zcl_flreq
*"  EXPORTING VALUE(ev_subrc) TYPE sysubrc
  INSERT zcl_flreq FROM is_req.
  ev_subrc = sy-subrc.
  COMMIT WORK.
ENDFUNCTION.

CALL FUNCTION 'Z_CL_UPD_REQ' IN UPDATE TASK
  EXPORTING is_req = ls_req
  IMPORTING ev_subrc = lv_subrc.
IF lv_subrc <> 0.
  MESSAGE 'Insert failed' TYPE 'E'.
ENDIF.
COMMIT WORK.
```
(5) 표준 트랜잭션(판매 오더 저장)의 BAdI 구현 안에서 `COMMIT WORK`를 쓰면 안 되는 이유와, BAdI 안에서 Z 테이블에 로그를 남기는 방법 2가지 이상을 쓰시오.
(6) 번호 범위에 대해 옳지 않은 것 2개를 고르시오(모두 맞혀야 득점). ① SNRO에서 정의하고 `NUMBER_GET_NEXT`로 다음 번호를 얻는다 ② 메인 메모리 버퍼링은 성능이 좋지만 빈 번호(gap)가 생길 수 있다 ③ 내부 번호 부여는 사용자가 직접 번호를 입력하는 방식이다 ④ `SELECT MAX( id )` + 1은 동시 실행에도 안전하므로 번호 범위 대신 권장된다 ⑤ 한 객체에 여러 구간(01, 02)을 두고 용도별로 쓸 수 있다.

<details><summary>정답·해설</summary>

**(1)** DB LUW: DB 입장에서 커밋/롤백되는 단위로, 한 다이얼로그 스텝(하나의 work process 점유 구간) 안에서 끝난다. SAP LUW: 업무적으로 함께 저장돼야 하는 변경 묶음으로 여러 화면(여러 DB LUW, 여러 work process)에 걸칠 수 있고 `COMMIT WORK`/`ROLLBACK WORK`로 끝난다. 암묵적 DB 커밋: 화면 전환(다이얼로그 스텝 종료), 동기/비동기 RFC 호출, `WAIT`, I/W/E 메시지 표시, HTTP 통신 등. 화면마다 DB에 바로 쓰면 화면 전환 때 암묵적 커밋으로 중간 상태가 저장되므로, 업데이트 FM을 IN UPDATE TASK로 "등록"만 해 두면 COMMIT WORK 때 업데이트 work process가 한 DB LUW로 몰아서 실행해 전부 성공 또는 전부 롤백된다. ROLLBACK WORK를 하면 등록이 모두 버려진다.
**(2)** V1: 시간이 중요한 주 업데이트(예: 주문 생성), 등록 순서대로 하나의 DB LUW에서 실행되고 실패하면 V1 전체 롤백, 재시작 가능/불가 옵션. V2: 부수 업데이트(예: 통계), 모든 V1이 성공적으로 끝난 뒤 별도 DB LUW에서 실행, V1이 실패하면 실행 안 됨, V2 실패는 V1에 영향 없음. `COMMIT WORK`: 업데이트를 비동기로 시작하고 바로 진행. `COMMIT WORK AND WAIT`: V1이 끝날 때까지 기다리고 결과에 따라 sy-subrc 설정, 저장 직후 같은 데이터를 다시 읽거나 후속 처리할 때 쓴다. `SET UPDATE TASK LOCAL`: 업데이트 FM이 업데이트 work process가 아니라 현재 work process에서 동기로 실행된다. ABAP Cloud(RAP)에서는 업데이트가 항상 로컬·동기다. 업데이트 오류는 SM13.
**(3)** f_a → f_b → Z_UPD_X → Z_UPD_Z → Z_UPD_Y, f_a는 한 번만. ON COMMIT FORM은 COMMIT 시 현재 work process에서 업데이트 FM보다 먼저 실행되고 같은 FORM을 여러 번 등록해도 한 번만 실행된다. 그다음 업데이트 work process에서 V1이 등록 순서대로(X, Z) 하나의 DB LUW로 실행되고, V1이 모두 성공해 커밋된 뒤 V2(Y)가 실행된다. ROLLBACK WORK면 아무것도 실행되지 않는다(IN UPDATE TASK, ON COMMIT 등록이 모두 삭제되고 `PERFORM ... ON ROLLBACK`으로 등록한 루틴만 실행). Z_UPD_Z 오류 시 Z_UPD_X 변경도 롤백되고(V1 전체 롤백) V2인 Z_UPD_Y는 실행되지 않으며 SM13에 오류 상태로 남는다.
**(4)** ① 업데이트 FM은 EXPORTING을 가질 수 없다(IMPORTING·TABLES만, IMPORTING은 값 전달). COMMIT 이후 다른 프로세스에서 실행되어 값을 돌려줄 수 없다 → ev_subrc와 호출 측 IMPORTING·lv_subrc 검사 삭제. ② 업데이트 FM 안의 `COMMIT WORK`는 금지(런타임 오류), 커밋은 프레임워크가 한다 → 삭제. ③ INSERT 실패를 무시 → 실패하면 `MESSAGE ... TYPE 'A'`(또는 X)로 업데이트를 중단시켜 SAP LUW 전체 롤백. ④ 호출 측에서 결과가 필요하면 `COMMIT WORK AND WAIT` 후 sy-subrc 확인(또는 COMMIT 전에 사전 검증).
```abap
FUNCTION z_cl_upd_req.
*"  IMPORTING VALUE(is_req) TYPE zcl_flreq
  INSERT zcl_flreq FROM is_req.
  IF sy-subrc <> 0.
    MESSAGE a001(zcl_msg) WITH is_req-req_id.   " 업데이트 중단, 롤백
  ENDIF.
ENDFUNCTION.

CALL FUNCTION 'Z_CL_UPD_REQ' IN UPDATE TASK EXPORTING is_req = ls_req.
COMMIT WORK AND WAIT.
IF sy-subrc <> 0.
  MESSAGE 'Update failed (see SM13)' TYPE 'E'.
ENDIF.
```
업데이트 FM에서는 COMMIT/ROLLBACK, CALL SCREEN, SUBMIT, 화면 출력도 쓸 수 없다. 키 중복 같은 오류는 COMMIT 전에 존재 여부를 검사하고 ENQUEUE로 동시 기록을 막는다.
**(5)** 이유: ① BAdI는 표준 프로그램의 SAP LUW 한가운데서 실행되므로 커밋하면 표준이 아직 다 처리하지 않은 데이터까지 중간에 확정되어 "전부 저장 아니면 전부 취소"가 깨지고, 이후 표준 처리에서 오류가 나도 앞부분을 되돌릴 수 없다. ② 등록돼 있던 업데이트 모듈(`IN UPDATE TASK`)과 `PERFORM ON COMMIT`이 너무 일찍 실행되고 잠금이 풀린다. ③ BAdI가 업데이트 태스크 안에서 불리는 경우 COMMIT WORK는 금지 문장이라 런타임 오류. 대안: ① `CALL FUNCTION 'Z_LOG_SAVE' IN UPDATE TASK`로 등록해 표준 COMMIT과 함께 저장 ② `PERFORM ... ON COMMIT`(클래스 기반이면 같은 효과의 COMMIT 시점 처리) ③ 표준과 독립적으로 남겨야 하면 `IN BACKGROUND TASK`(tRFC)·bgRFC나 별도 백그라운드 작업으로 커밋 뒤 처리. 동기 RFC 호출이나 대화상자 출력은 암시적 DB 커밋을 일으킬 수 있으므로 BAdI 안에서 조심한다. 채점(4점): LUW 무결성 2점(업데이트 태스크·잠금 언급 시 만점), 대안 2가지 각 1점.
**(6)** ③, ④. ③ 사용자가 직접 입력하는 것은 외부(external) 번호 부여이고 내부 번호 부여는 시스템이 매긴다. ④ 두 사용자가 같은 MAX를 읽어 같은 번호를 쓰면 키 중복이 생긴다. 번호 범위는 NRIV 테이블 잠금과 버퍼로 이를 막는다. ② 버퍼에 받아 둔 번호를 쓰지 못하고 서버가 재시작되면 버려진다. 법적으로 연속 번호가 필요하면 버퍼링을 끄거나 병렬 버퍼링을 쓴다.

</details>

---

### B-026. 잠금과 업데이트 태스크를 쓰는 저장 프로그램 작성 [작성] ★★★
<!-- src: CL-028, HC-021 -->
항공편 좌석 요청 테이블 `ZCL_FLREQ`(Lock Object `EZCL_FLREQ`, 키 MANDT, REQ_ID)와, 만석 항공편 대기자 명단 `ZHC_WAITLIST`를 다룬다.

(1) 업데이트 FM `Z_CL_UPD_STATUS`(IMPORTING `VALUE(iv_req_id)`, `VALUE(iv_status)`, 상태를 UPDATE)가 있다. 요청 번호 `iv_req_id`의 상태를 'A'(승인)로 바꾸는 메서드 본문을 작성하시오. 다른 사용자가 잠그고 있으면 그 사용자 이름을 넣은 메시지로 중단, 요청이 없거나 'N'이 아니면 잠금을 풀고 중단, 업데이트 태스크로 저장하고 결과 확인, 잠금 해제 시점을 주석으로 설명.
(2) 클라이언트 종속 투명 테이블 `ZHC_WAITLIST`를 설계하시오. 한 고객은 한 항공편에 한 번만 등록. 저장 정보: 항공사, 노선, 비행일, 고객번호, 요청 좌석 수(1~9), 좌석 등급, 대기 순번, 등록 당시 가격과 통화, 상태(W 대기/C 확정/X 취소), 등록자, 등록일, 등록 시각. 다음 표(필드별 키, 데이터 엘리먼트, Data Type, 길이, 소수, 참조 필드·외래 키)와 설정표(Delivery Class, Data Browser/Table View Maint., Enhancement Category, Data Class, Size Category, Buffering)를 채우시오.

| 필드 | 키 | 데이터 엘리먼트 | Data Type | 길이 | 소수 | 참조 필드·외래 키 |
|---|---|---|---|---|---|---|
| | | | | | | |

(3) 잠금 객체 `EZHC_WAITLIST`의 설정(기본 테이블, 모드, 파라미터)과 생성 FM 이름을 쓰시오.
(4) 선택화면에서 항공편·고객·좌석 수·등급을 받아 대기 등록하는 `ZHC_WAITLIST_ADD`를 작성하시오. 항공편이 없거나 빈 좌석이 있으면 등록하지 않고, 대기 순번은 그 항공편의 최대 순번 + 1(동시 등록에도 중복 없이), 이미 W로 등록된 고객이면 거부, 예전 X 기록이 있으면 덮어쓰기, 성공 시 커밋·실패 시 롤백, 마지막에 잠금 해제.
(5) (4)에서 CUSTOMID 없이 잠그는 이유(일반 잠금), 잠금과 DB 행 잠금의 차이, 업데이트 태스크를 쓸 때와 직접 DB 변경일 때 잠금 해제의 차이, 외래 키가 저장 시 검사되지 않는다는 점의 결과를 쓰시오.

<details><summary>정답·해설</summary>

**(1)**
```abap
METHOD approve.  " IMPORTING iv_req_id TYPE zcl_req_id
  CALL FUNCTION 'ENQUEUE_EZCL_FLREQ'
    EXPORTING
      mode_zcl_flreq = 'E'
      req_id         = iv_req_id
      _scope         = '2'          " 잠금을 업데이트 태스크로 넘김
    EXCEPTIONS
      foreign_lock   = 1
      system_failure = 2
      OTHERS         = 3.
  IF sy-subrc = 1.
    MESSAGE |Request is locked by { sy-msgv1 }| TYPE 'E'.
  ELSEIF sy-subrc <> 0.
    MESSAGE 'Lock error' TYPE 'E'.
  ENDIF.

  SELECT SINGLE status FROM zcl_flreq WHERE req_id = @iv_req_id INTO @DATA(lv_status).
  IF sy-subrc <> 0 OR lv_status <> 'N'.
    CALL FUNCTION 'DEQUEUE_EZCL_FLREQ' EXPORTING req_id = iv_req_id.
    MESSAGE 'Request not found or not new' TYPE 'E'.
  ENDIF.

  CALL FUNCTION 'Z_CL_UPD_STATUS' IN UPDATE TASK
    EXPORTING iv_req_id = iv_req_id  iv_status = 'A'.
  COMMIT WORK AND WAIT.
  " _scope = '2' 이므로 잠금은 업데이트 태스크가 끝날 때 자동 해제된다.
  IF sy-subrc <> 0.
    MESSAGE 'Update failed' TYPE 'E'.
  ENDIF.
ENDMETHOD.
```
순서: 잠금 → 최신 데이터 읽기·검사 → 변경 등록 → COMMIT → 잠금 해제(잠금 전에 읽은 데이터로 판단하면 동시성 문제). `_scope = '1'`이면 직접 DEQUEUE, `'2'`(기본)는 업데이트 종료 시 해제, `'3'`은 양쪽 모두. 메서드 안에서는 메시지 대신 예외를 던지는 설계도 좋다. 채점 포인트: FOREIGN_LOCK과 sy-msgv1, 실패 시 DEQUEUE, IN UPDATE TASK, COMMIT WORK (AND WAIT).
**(2)**

| 필드 | 키 | 데이터 엘리먼트 | Data Type | 길이 | 소수 | 참조 필드·외래 키 |
|---|---|---|---|---|---|---|
| MANDT | ✓ | MANDT | CLNT | 3 | 0 | 클라이언트 |
| CARRID | ✓ | S_CARR_ID | CHAR | 3 | 0 | 외래 키 → SCARR |
| CONNID | ✓ | S_CONN_ID | NUMC | 4 | 0 | 외래 키 → SPFLI |
| FLDATE | ✓ | S_DATE | DATS | 8 | 0 | 외래 키 → SFLIGHT(MANDT, CARRID, CONNID, FLDATE) |
| CUSTOMID | ✓ | S_CUSTOMER | NUMC | 8 | 0 | 외래 키 → SCUSTOM |
| SEATS_REQ | | ZHC_SEATS_REQ(신규, 도메인 ZHC_SEATS_REQ: INT1 3, 값 범위 1~9) | INT1 | 3 | 0 | |
| CLASS | | S_CLASS | CHAR | 1 | 0 | 도메인 고정값 F/C/Y |
| PRIORITY | | ZHC_PRIORITY(신규, 도메인 INT2 5) | INT2 | 5 | 0 | 대기 순번 |
| PRICE | | S_PRICE | CURR | 15 | 2 | 참조 필드 ZHC_WAITLIST-CURRENCY |
| CURRENCY | | S_CURRCODE | CUKY | 5 | 0 | 검사 테이블 TCURC |
| STATUS | | ZHC_WL_STATUS(신규, 도메인 CHAR 1, 고정값 W/C/X) | CHAR | 1 | 0 | |
| ERNAM | | ERNAM | CHAR | 12 | 0 | 등록자 |
| ERDAT | | ERDAT | DATS | 8 | 0 | 등록일 |
| ERZET | | ERZET | TIMS | 6 | 0 | 등록 시각 |

| 설정 | 값 |
|---|---|
| Delivery Class | A(애플리케이션 테이블, 업무 데이터) |
| Data Browser/Table View Maint. | Display/Maintenance Allowed(TMG를 만들 경우) |
| Enhancement Category | Can Be Enhanced (Deep) 또는 Cannot Be Enhanced 중 하나를 명시(미지정 시 활성화 경고) |
| Data Class | APPL1(트랜잭션 데이터, 자주 변경) |
| Size Category | 0(예상 건수 적음) |
| Buffering | Not allowed(자주 변경되고 최신 값 필요) |

활성화 필수: CURR 필드 PRICE에 CUKY 참조 필드 지정, 키 필드는 앞쪽에 연속, MANDT를 첫 키로.
**(3)** 이름은 E로 시작(`EZHC_WAITLIST`), 기본 테이블 ZHC_WAITLIST, 잠금 모드 E(쓰기 잠금, 누적 가능), 잠금 파라미터 MANDT, CARRID, CONNID, FLDATE, CUSTOMID(키 필드에서 자동 제안), 생성 FM `ENQUEUE_EZHC_WAITLIST`, `DEQUEUE_EZHC_WAITLIST`.
**(4)**
```abap
REPORT zhc_waitlist_add.
PARAMETERS: p_carr  TYPE s_carr_id     OBLIGATORY,
            p_conn  TYPE s_conn_id     OBLIGATORY,
            p_date  TYPE s_date        OBLIGATORY,
            p_cust  TYPE s_customer    OBLIGATORY,
            p_seats TYPE zhc_seats_req DEFAULT 1,
            p_class TYPE s_class       DEFAULT 'Y'.

AT SELECTION-SCREEN.
  IF p_seats < 1 OR p_seats > 9.
    MESSAGE '좌석 수는 1~9입니다' TYPE 'E'.
  ENDIF.
  IF p_class <> 'F' AND p_class <> 'C' AND p_class <> 'Y'.
    MESSAGE '등급은 F, C, Y 중 하나입니다' TYPE 'E'.
  ENDIF.

START-OF-SELECTION.
  " 1) 사전 검사
  SELECT SINGLE seatsmax, seatsocc, price, currency FROM sflight
    WHERE carrid = @p_carr AND connid = @p_conn AND fldate = @p_date
    INTO @DATA(ls_fl).
  IF sy-subrc <> 0.
    MESSAGE '항공편이 없습니다' TYPE 'S' DISPLAY LIKE 'E'.
    RETURN.
  ENDIF.
  IF ls_fl-seatsocc < ls_fl-seatsmax.
    MESSAGE '빈 좌석이 있어 대기 등록이 필요 없습니다' TYPE 'S' DISPLAY LIKE 'W'.
    RETURN.
  ENDIF.

  " 2) 항공편 단위 일반(generic) 잠금: CUSTOMID를 넘기지 않음
  CALL FUNCTION 'ENQUEUE_EZHC_WAITLIST'
    EXPORTING  mode_zhc_waitlist = 'E'  carrid = p_carr  connid = p_conn  fldate = p_date
    EXCEPTIONS foreign_lock = 1  system_failure = 2  OTHERS = 3.
  CASE sy-subrc.
    WHEN 0.
    WHEN 1.
      MESSAGE |{ sy-msgv1 } 사용자가 이 항공편 대기 명단을 처리 중입니다| TYPE 'S' DISPLAY LIKE 'E'.
      RETURN.
    WHEN OTHERS.
      MESSAGE '잠금 실패' TYPE 'S' DISPLAY LIKE 'E'.
      RETURN.
  ENDCASE.

  " 3) 잠근 뒤에 읽기 (read-after-lock)
  SELECT SINGLE status FROM zhc_waitlist
    WHERE carrid = @p_carr AND connid = @p_conn AND fldate = @p_date AND customid = @p_cust
    INTO @DATA(lv_status).
  IF sy-subrc = 0 AND lv_status = 'W'.
    MESSAGE '이미 대기 등록된 고객입니다' TYPE 'S' DISPLAY LIKE 'E'.
  ELSE.
    SELECT MAX( priority ) FROM zhc_waitlist
      WHERE carrid = @p_carr AND connid = @p_conn AND fldate = @p_date AND status = 'W'
      INTO @DATA(lv_max).
    DATA(ls_wl) = VALUE zhc_waitlist( carrid = p_carr  connid = p_conn  fldate = p_date
                                      customid = p_cust  seats_req = p_seats  class = p_class
                                      priority = lv_max + 1
                                      price = ls_fl-price  currency = ls_fl-currency
                                      status = 'W'  ernam = sy-uname  erdat = sy-datum  erzet = sy-uzeit ).
    MODIFY zhc_waitlist FROM @ls_wl.          " 없으면 INSERT, 취소 기록이면 UPDATE
    IF sy-subrc = 0.
      COMMIT WORK.
      MESSAGE |대기 순번 { ls_wl-priority }번으로 등록되었습니다| TYPE 'S'.
    ELSE.
      ROLLBACK WORK.
      MESSAGE '저장 실패' TYPE 'S' DISPLAY LIKE 'E'.
    ENDIF.
  ENDIF.

  " 4) 잠금 해제 (모든 경로에서)
  CALL FUNCTION 'DEQUEUE_EZHC_WAITLIST'
    EXPORTING mode_zhc_waitlist = 'E' carrid = p_carr connid = p_conn fldate = p_date.
```
채점(100점): (2) 키 구성·표준 DE·신규 DE/도메인 15 / (2) CURR-CUKY, Delivery Class, Enhancement Category, 기술 설정, 외래 키 15 / (3) 이름 규칙, 모드 E, 파라미터, FM 이름 10 / 선택화면 + 검증 5 / 항공편·만석 사전 검사 10 / ENQUEUE(EXCEPTIONS, foreign_lock 시 sy-msgv1) 15 / 잠금 후 읽기, 중복 검사, MAX + 1 10 / MODIFY + COMMIT/ROLLBACK 10 / 모든 경로에서 DEQUEUE 10.
**(5)** 잠금 파라미터를 넘기지 않으면(또는 초기값) 그 필드는 "모든 값"으로 잠긴다(일반 잠금). 순번을 MAX + 1로 매기려면 같은 항공편의 다른 고객 등록도 막아야 하므로 CUSTOMID를 생략해 항공편 전체를 잠근다. 고객 단위로만 잠그면 두 사람이 동시에 같은 MAX를 읽어 순번이 겹친다. 잠금은 논리적 약속이라 모든 프로그램이 같은 잠금 객체를 써야 하며, DB 행 잠금(SELECT SINGLE FOR UPDATE)과 달리 SAP LUW 전체(여러 화면, 업데이트 태스크)까지 유지할 수 있다. `foreign_lock`이면 sy-msgv1에 소유자 ID가 들어온다. 업데이트 태스크를 쓰면 `_scope = '2'`로 잠가 커밋 후 업데이트가 끝날 때 자동 해제되지만, 이 프로그램은 직접 DB를 바꾸므로 COMMIT 뒤 DEQUEUE를 명시한다. 외래 키는 화면 입력 검사와 F4에만 쓰이고 DB 제약이 아니어서 ABAP SQL 저장 시 검사되지 않으므로 프로그램에서 사전 검사를 한다.

</details>

---

## 출력 양식(SAPscript · SmartForms · Adobe Forms)

### B-027. SAPscript: 구성 요소·출력 프로그램·창·표준 텍스트·NACE·T-code [코드] ★★
<!-- src: IB-071, IB-072, IB-073, IB-080, IB-081, TC-007 -->
SAPscript 폼 ZIB_INVOICE를 출력하는 프로그램과 폼의 MAIN 창 텍스트다.

```abap
CALL FUNCTION '____(a)____'
  EXPORTING form = 'ZIB_INVOICE'  language = sy-langu  device = 'PRINTER'  dialog = 'X'.
LOOP AT gt_items INTO gs_item.
  CALL FUNCTION '____(b)____'
    EXPORTING element = 'ITEM_LINE'  window = '____(c)____'.
ENDLOOP.
CALL FUNCTION 'WRITE_FORM' EXPORTING element = 'TOTAL'  window = 'MAIN'.
CALL FUNCTION '____(d)____'.
```

```text
____(e)____  ITEM_LINE
*            &GS_ITEM-MATNR&,,&GS_ITEM-MENGE&
/E           TOTAL
*            Total: &GV_TOTAL&
```

(1) SAPscript 폼(Layout Set)의 구성 요소를 다섯 가지 이상 쓰고, 폼 밖에서 출력에 필요한 요소(프로그램, 텍스트, 설정)를 쓰시오.
(2) 빈칸 (a)~(e)를 채우고, START_FORM/END_FORM·CONTROL_FORM의 용도와 폼 텍스트의 `/E`, `/:`, `*`, `,,`, `&변수&`의 의미를 쓰시오.
(3) SAPscript 창 유형(MAIN, VAR, CONST)을 설명하고, 다음 중 옳지 **않은** 것을 고르시오.
① SAPscript의 MAIN 창 내용은 넘치면 다음 페이지 MAIN 창으로 이어진다. ② SmartForms 창 유형에는 Main, Secondary, Copies, Final window가 있다. ③ SmartForms Final window는 마지막에 처리되므로 전체 페이지 수를 첫 페이지에도 출력할 수 있다. ④ SmartForms Secondary window는 넘치면 다음 페이지로 자동으로 이어진다.
(4) SO10 표준 텍스트 ZIB_FOOTER를 `READ_TEXT`로 읽을 때 `id`, `object` 값과, SAPscript 폼에서 포함시키는 명령(`/: ____ ZIB_FOOTER OBJECT TEXT ID ST LANGUAGE EN`)을 쓰시오. 텍스트 저장 테이블, 저장·삭제 FM, 전송 방법은?
(5) 판매 오더 저장 시 Z 송장 폼이 자동 출력되도록 NACE에서 설정할 항목과, NAST 기반 출력 프로그램 진입 FORM의 형태를 쓰시오. 재출력 방법과 S/4HANA에서의 변화는?
(6) 다음 표에 T-code를 쓰시오.

| 번호 | 기능 | T-code |
|---|---|---|
| 1 | SAPscript Form Painter | |
| 2 | SAPscript 스타일 | |
| 3 | 글꼴·바코드(SAPscript font maintenance) | |
| 4 | 그래픽(로고 BMP) 업로드·관리 | |
| 5 | Standard Text 관리 | |
| 6 | Smart Forms 작성 | |
| 7 | Smart Styles 작성 | |
| 8 | Adobe Form(Interface/Form) 작성 | |
| 9 | Output Type과 출력 프로그램·양식 연결 | |
| 10 | 스풀 요청 조회·재출력(전체 / 내 스풀) | |
| 11 | SAPscript 번역 | |

<details><summary>정답·해설</summary>

**(1)** 폼 구성 요소: Header(관리 정보, 첫 페이지, 기본 문단 형식), Pages(페이지와 다음 페이지 지정), Windows(창 정의), Page Windows(페이지마다 창의 위치·크기), Paragraph Formats, Character Formats, Documentation. 폼 밖: **출력 프로그램(Print Program)**(데이터를 읽어 OPEN_FORM/WRITE_FORM으로 폼에 넘김), **표준 텍스트(SO10)** 등 텍스트 객체, 출력 결정(NACE)과 스타일(SE72). SAPscript는 클라이언트 종속이고 원본 언어로만 수정할 수 있다(번역은 SE63).
**(2)** (a) `OPEN_FORM` (b) `WRITE_FORM` (c) `MAIN` (d) `CLOSE_FORM` (e) `/E`. 순서는 OPEN_FORM → (START_FORM) → WRITE_FORM 반복 → (END_FORM) → CLOSE_FORM. START_FORM/END_FORM은 한 스풀 요청 안에서 여러 폼(예: 고객별 송장)을 출력할 때, CONTROL_FORM은 강제 페이지 넘김 등 제어 명령을 보낼 때 쓴다. `/E` 텍스트 요소(element) 시작, `/:` 제어 명령(IF, INCLUDE, PROTECT 등), `*` 기본 문단, `,,` 탭, `&변수&` 출력 프로그램의 전역 변수 값 출력.
**(3)** MAIN: 본문, 페이지를 넘어 이어지는 유일한 창(SAPscript에서 필수). VAR: 페이지마다 다시 서식화되는 가변 창. CONST: 한 번만 서식화되는 고정 창. (자료에 따라 그래픽용 GRAPH를 네 번째로 들기도 한다.) 옳지 않은 것은 **④**: 페이지를 넘어 이어지는 것은 Main window뿐이고 Secondary window는 고정 위치·크기의 창(헤더, 주소, 로고)이라 넘치면 잘린다. Copies window는 원본/사본 표시용, Final window는 모든 창 처리 후 마지막에 처리된다.
**(4)** `id = 'ST'`, `object = 'TEXT'`, 명령은 `INCLUDE`. 텍스트는 OBJECT + ID + NAME + 언어로 식별한다(판매 오더 헤더 텍스트는 OBJECT VBBK 등). 헤더는 STXH, 내용은 STXL에 저장된다. 저장 SAVE_TEXT, 삭제 DELETE_TEXT. SmartForms에서는 Text 노드 유형 "Include Text"로 넣는다. 표준 텍스트는 클라이언트 종속이라 프로그램 RSTXTRAN으로 전송 요청에 넣는다.
**(5)** NACE에서 애플리케이션(V1 판매 등) 선택 후: ① 출력 유형(예: ZIB1) 정의: 전송 매체(1 인쇄, 5 외부 송신 등), 시점(배치/즉시). ② Processing Routines: 매체별 **출력 프로그램**, **FORM 루틴 이름**(예: ENTRY), **폼 이름**(SAPscript/SmartForms/PDF). ③ 액세스 시퀀스·조건 테이블과 조건 레코드(VV11 등). ④ 출력 결정 절차에 출력 유형 할당.
```abap
FORM entry USING return_code TYPE i
                 us_screen   TYPE c.
  " 구조 NAST(출력 메시지 레코드)의 objky = 문서 번호
  " 데이터 조회 → 폼 호출 → 성공 시 return_code = 0
ENDFORM.
```
출력 상태는 NAST-VSTAT로 관리되고, 재출력은 문서 화면(VA02 → Output)이나 RSNAST00으로 한다. S/4HANA의 신규 Output Management는 BRF+ 기반(OPD)이라 NACE 대신 쓰이는 경우가 많다.
**(6)** 1 SE71, 2 SE72, 3 SE73, 4 SE78, 5 SO10, 6 SMARTFORMS, 7 SMARTSTYLES, 8 SFP, 9 NACE, 10 SP01 / SP02, 11 SE63. SmartForms는 활성화 시 생성되는 FM 이름을 `SSF_FUNCTION_MODULE_NAME`으로, Adobe Form은 `FP_FUNCTION_MODULE_NAME`으로 얻고 `FP_JOB_OPEN`/`FP_JOB_CLOSE`로 감싼다(B-028). SO10 텍스트는 `READ_TEXT`로 읽는다.

</details>

---

### B-028. SmartForms·Adobe Forms: 비교·호출·노드·페이지 보호·디버깅 [코드] ★★
<!-- src: IB-074, IB-075, IB-076, IB-077, IB-078, IB-079, MX-023, TC-100 -->
SmartForms 폼 ZIB_FLIGHT_SF를 미리보기로 출력하고 PDF 변환용 OTF도 받을 수 있게 하는 코드와, Adobe Form ZIB_FLIGHT_AF를 출력하는 코드다.

```abap
DATA: lv_fm TYPE rs38l_fnam, ls_ctrl TYPE ssfctrlop, ls_out TYPE ssfcompop, ls_info TYPE ssfcrescl.
CALL FUNCTION '____(a)____'
  EXPORTING  formname = 'ZIB_FLIGHT_SF'
  IMPORTING  fm_name  = lv_fm
  EXCEPTIONS no_form = 1  no_function_module = 2  OTHERS = 3.
IF sy-subrc <> 0. RETURN. ENDIF.
ls_ctrl-no_dialog   = 'X'.
ls_ctrl-preview     = 'X'.
ls_ctrl-____(c)____ = ' '.      " PDF가 필요하면 'X'
ls_out-tddest       = 'LP01'.
CALL FUNCTION ____(b)____
  EXPORTING  control_parameters = ls_ctrl  output_options = ls_out  user_settings = space
             is_carrid = p_carr
  IMPORTING  job_output_info = ls_info
  TABLES     it_flights = gt_flight
  EXCEPTIONS formatting_error = 1  internal_error = 2  send_error = 3  user_canceled = 4  OTHERS = 5.

DATA: ls_outpar TYPE sfpoutputparams, ls_docpar TYPE sfpdocparams,
      ls_formout TYPE fpformoutput, lv_afm TYPE funcname.
ls_outpar-preview = 'X'.
CALL FUNCTION '____(d)____' CHANGING ie_outputparams = ls_outpar EXCEPTIONS OTHERS = 1.
CALL FUNCTION '____(e)____' EXPORTING i_name = 'ZIB_FLIGHT_AF' IMPORTING e_funcname = lv_afm.
CALL FUNCTION lv_afm
  EXPORTING /1bcdwb/docparams = ls_docpar  is_carrid = p_carr
  IMPORTING /1bcdwb/formoutput = ls_formout
  EXCEPTIONS OTHERS = 1.
CALL FUNCTION '____(f)____' EXCEPTIONS OTHERS = 1.
```

(1) SAPscript와 SmartForms의 차이를 다섯 가지 이상 쓰시오(클라이언트, 실행 방식, MAIN 창, 페이지 형식, 디자인, 기타).
(2) 빈칸 (a)~(c)를 채우고, 생성 FM 이름(`/1BCDWB/SF00000123`)을 하드코딩하면 안 되는 이유, `getotf = 'X'`일 때 PDF를 만드는 방법, `user_settings = space`와 `is_carrid`의 의미를 쓰시오.
(3) 빈칸 (d)~(f)를 채우고, Adobe Form을 렌더링하는 서버 구성 요소, SFP에서 만드는 두 객체와 레이아웃 도구, PDF 바이너리를 받는 방법을 쓰시오.
(4) MAIN 창 없는 SmartForms를 만들 수 있는가? 그때의 제약은?
(5) SmartForms Template 노드와 Table 노드의 차이를 쓰고, 반복·조건 출력·ABAP 로직에 쓰는 노드를 쓰시오.
(6) 페이지 보호(Page Protection)가 무엇이고 SAPscript와 SmartForms에서 각각 어떻게 설정하는가?
(7) 옳은 것을 **모두** 고르시오. ① SAPscript는 SE71 → Utilities → Activate Debugger로 폼 디버거를 켠다. ② 프로그램 RSTXDBUG로도 SAPscript 디버거가 켜진다. ③ SmartForms는 생성 FM 코드에 중단점을 걸거나 Program Lines 노드에 BREAK-POINT를 넣어 디버깅한다. ④ SmartForms는 SE71 디버거로만 디버깅할 수 있다.
(8) 다음 용어를 쓰시오. ㉠ SAPscript 양식을 호출하는 프로그램 ㉡ Smart Form을 활성화하면 생성되는 객체 ㉢ SmartForms의 인터페이스 외 전역 정의 영역 ㉣ 클라이언트 종속 여부(SAPscript / Smart Forms / Adobe Forms)

<details><summary>정답·해설</summary>

**(1)**

| 항목 | SAPscript | SmartForms |
|---|---|---|
| 클라이언트 | 종속 | 독립 |
| 실행 방식 | 출력 프로그램이 OPEN_FORM/WRITE_FORM으로 텍스트 요소 호출 | 활성화 시 함수 모듈 생성, 출력 프로그램은 그 FM 호출(로직을 폼 안에 둘 수 있음) |
| MAIN 창 | 반드시 필요 | 없어도 됨 |
| 페이지 형식 | 한 폼에 하나의 페이지 형식(용지 방향 등) | 페이지마다 다른 형식 가능 |
| 디자인 | 텍스트 기반 편집기, 명령어 위주 | 그래픽 Form Builder(노드 트리, 테이블·템플릿), 스타일 SMARTSTYLES |
| 기타 | 라벨 출력에 많이 씀 | 웹 출력(XSF/HTML), 색상·배경 그래픽, SAPscript 마이그레이션 기능 |

둘 다 레거시이며 S/4HANA의 새 Output Management는 Adobe Forms(또는 Fragmented forms)를 기본으로 한다.
**(2)** (a) `SSF_FUNCTION_MODULE_NAME` (b) `lv_fm`(따옴표 없이 변수로 동적 호출) (c) `getotf`. 생성 FM 이름은 활성화할 때 시스템마다 따로 만들어져 개발·품질·운영에서 다를 수 있고 재생성하면 바뀔 수도 있으므로 폼 이름으로 실행 시점에 얻는다. `getotf = 'X'`이면 인쇄 대신 `job_output_info-otfdata`에 OTF가 담기고 `CONVERT_OTF`(format 'PDF')로 PDF로 바꿔 메일 첨부 등에 쓴다. `user_settings = space`여야 `output_options`의 프린터(`tddest`) 같은 값이 쓰인다. `is_carrid`는 폼 인터페이스에 정의한 임포트 파라미터 이름이다.
**(3)** (d) `FP_JOB_OPEN` (e) `FP_FUNCTION_MODULE_NAME` (f) `FP_JOB_CLOSE`. 렌더링 서버는 **ADS(Adobe Document Services)**: 예전에는 AS Java에 설치했고 최근에는 SAP BTP의 SAP Forms Service by Adobe도 쓸 수 있다. SFP에서 **Interface**(파라미터, 전역 데이터, 초기화 코드)와 **Form**(Context: 인터페이스 데이터 중 폼에 쓸 것 선택 + Layout)을 만들고, 레이아웃은 **Adobe LiveCycle Designer**로 그린다. `ls_outpar-getpdf = 'X'`이면 `ls_formout-pdf`로 PDF 바이너리를 받는다. 입력 가능한 Interactive Form도 만들 수 있다.
**(4)** 만들 수 있다. 다만 MAIN 창이 없으면 내용이 페이지를 넘어 이어지지 않으므로 한 페이지로 끝나는 고정 양식(라벨, 증명서 등)에만 적합하다. 여러 페이지에 걸친 항목 목록은 MAIN 창의 테이블로 출력해야 한다.
**(5)** **Template**: 행·열 수와 크기가 고정된 정적 표(머리글 박스 등), 페이지 넘김 없음. **Table**: 내부 테이블을 반복하며 행 수가 데이터에 따라 달라지는 동적 표, 헤더·본문·푸터 구역과 소계/합계를 지원하고 MAIN 창 안에서 페이지를 넘어 이어진다. 반복만 필요하면 Loop 노드, 조건 출력은 Alternative 노드나 각 노드의 Conditions 탭, ABAP 로직은 Program Lines 노드.
**(6)** 함께 출력되어야 하는 묶음(주소 블록, 한 항목의 여러 줄)이 두 페이지로 나뉘지 않게, 현재 페이지에 다 들어가지 않으면 묶음 전체를 다음 페이지로 넘기는 기능. SAPscript: `/: PROTECT` ... `/: ENDPROTECT`(문단 형식의 "Page protection" 속성도 있음). SmartForms: 텍스트 노드나 Folder 노드의 Output Options 탭에서 "Page Protection" 체크, 테이블 행 단위면 해당 행을 Folder로 묶는다. 페이지를 넘는 창(MAIN)에서만 의미가 있고 빈 공간이 생길 수 있다.
**(7)** ①, ②, ③. SmartForms는 SE71과 무관하며 생성 FM(SSF_FUNCTION_MODULE_NAME으로 이름 확인)에서 노드 이름으로 검색해 중단점을 건다. SAPscript 디버거는 텍스트 요소·명령 단위로 진행하며 심볼 값을 보여 준다.
**(8)** ㉠ 인쇄(드라이버, Print) 프로그램: OPEN_FORM, WRITE_FORM, CLOSE_FORM 호출. ㉡ 함수 모듈(/1BCDWB/SF…). ㉢ Global Definitions(전역 데이터·타입·필드 심볼·초기화 코드). 자주 쓰는 노드: Window, Text, Table, Loop, Program Lines. ㉣ SAPscript는 클라이언트 종속, Smart Forms·Adobe Forms는 클라이언트 독립.

</details>

---

## 인터페이스 1(RFC · BAPI)

### B-029. RFC: 방식·호출 구문·SM59 연결 유형·디버깅·T-code [코드] ★★
<!-- src: CL-030, MX-025, TC-056, IB-093, TC-044, IB-094, TC-043 -->
다음 코드를 보고 물음에 답하시오.

```abap
DATA lv_msg TYPE c LENGTH 255.
" 1) 동기 RFC
CALL FUNCTION 'Z_MX_GET_FLIGHTS'
  ____(a)____ 'ERP_PRD_100'
  EXPORTING  iv_carrid  = p_carr
  IMPORTING  et_flights = lt_flights
  EXCEPTIONS ____(b)____ = 1 MESSAGE lv_msg
             ____(c)____ = 2 MESSAGE lv_msg
             OTHERS      = 3.
" 2) 비동기 RFC: 끝나면 메서드 on_done 실행
CALL FUNCTION 'Z_MX_RECALC' ____(d)____ 'T1'
  DESTINATION 'ERP_PRD_100'
  CALLING on_done ON END OF TASK
  EXPORTING iv_carrid = p_carr.
" 3) 트랜잭션 RFC: COMMIT WORK 때 한 번만 실행
CALL FUNCTION 'Z_MX_LOG' IN ____(e)____ DESTINATION 'ERP_PRD_100'
  EXPORTING is_log = ls_log.
COMMIT WORK.
```

(1) 빈칸 (a)~(e)를 채우고, (b)·(c) 예외의 차이와 aRFC 결과를 받는 방법을 쓰시오.
(2) 다음 표를 채우시오.

| 약어 | 영문 이름 | CALL FUNCTION 구문 | 보장·특징 | 모니터 |
|---|---|---|---|---|
| sRFC | | | | |
| aRFC | | | | |
| tRFC | | | | |
| qRFC | | | | |
| bgRFC | | | | |

(3) RFC에 대한 설명 중 옳지 **않은** 것은? ① sRFC 호출자는 원격 FM이 끝날 때까지 기다린다. ② aRFC 결과는 콜백에서 `RECEIVE RESULTS FROM FUNCTION`으로 받는다. ③ tRFC는 COMMIT WORK 시 exactly once 실행된다. ④ qRFC는 같은 큐 안 LUW를 exactly once in order로 실행한다. ⑤ tRFC로 호출한 FM의 EXPORTING 값은 COMMIT WORK AND WAIT 후 호출자 변수에 채워진다.
(4) FM을 RFC로 호출할 수 있게 하는 조건(SE37 속성, 파라미터)을 쓰시오.
(5) SM59 연결 유형 3, G, H, T, L, I의 의미를 쓰고, 다음 중 옳지 **않은** 것을 고르시오. ① 3 – 다른 ABAP 시스템 ② T – TCP/IP(외부·등록 서버 프로그램) ③ G – 외부 서버 HTTP ④ H – ABAP 시스템 HTTP ⑤ L – 같은 시스템 안의 로컬 업데이트 전용 연결. 특수 destination NONE과 BACK, ABAP Cloud에서의 대체 수단도 쓰시오.
(6) 시스템 A의 프로그램이 호출하는 시스템 B의 RFC FM을 디버깅하는 방법을 두 가지 이상 쓰고 필요한 조건을 쓰시오.
(7) 다음 표에 T-code를 쓰시오: ① RFC Destination 정의·테스트 ② tRFC 오류·대기 목록 ③ qRFC 출력 큐 ④ qRFC 입력 큐 ⑤ bgRFC 모니터 ⑥ 웹 서비스(SOAP) 구성(Endpoint, Logical Port) ⑦ ABAP Proxy 생성 ⑧ PI/PO 메시지 모니터(Integration Engine)

<details><summary>정답·해설</summary>

**(1)** (a) `DESTINATION` (b) `system_failure` (c) `communication_failure` (d) `STARTING NEW TASK` (e) `BACKGROUND TASK`. `system_failure`는 상대 시스템에서의 덤프 등 실행 오류, `communication_failure`는 연결 실패이며 둘 다 RFC 전용 특수 예외로 `MESSAGE`에 오류 텍스트를 받는다. aRFC 결과는 콜백(`CALLING meth ON END OF TASK` 또는 `PERFORMING form ON END OF TASK`) 안에서 `RECEIVE RESULTS FROM FUNCTION`으로 받고, `WAIT FOR ASYNCHRONOUS TASKS UNTIL ...`으로 기다린다. 병렬 처리에 쓴다.
**(2)**

| 약어 | 영문 이름 | CALL FUNCTION 구문 | 보장·특징 | 모니터 |
|---|---|---|---|---|
| sRFC | Synchronous RFC | `CALL FUNCTION 'F' DESTINATION 'D'` | 동기, 호출자 대기 | – |
| aRFC | Asynchronous RFC | `... STARTING NEW TASK 'T' DESTINATION 'D' CALLING meth ON END OF TASK` | 비동기, 병렬 처리 | – |
| tRFC | Transactional RFC | `... IN BACKGROUND TASK DESTINATION 'D'` + `COMMIT WORK` | exactly once, 대상이 꺼져 있으면 나중에 재시도 | SM58 |
| qRFC | Queued RFC | `TRFC_SET_QUEUE_NAME` 호출 후 IN BACKGROUND TASK | exactly once in order | SMQ1(송신)/SMQ2(수신) |
| bgRFC | Background RFC | `... IN BACKGROUND UNIT lo_unit`(unit은 bgRFC destination에서 생성) | tRFC/qRFC의 후속, 성능·모니터링 개선 | SBGRFCMON |

순서까지 보장하려면 qRFC나 bgRFC를 쓴다.
**(3)** **⑤**. tRFC/qRFC는 나중에 비동기로 실행되므로 EXPORTING 값을 돌려받을 수 없다(호출 시 넘기는 파라미터만 전달).
**(4)** SE37 속성에서 Processing Type을 **Remote-Enabled Module**로 지정하고, 파라미터는 값 전달(pass by value), 일반 TYPE은 DDIC 타입이어야 한다.
**(5)** 3: ABAP Connection(다른 ABAP 시스템), G: HTTP Connection to External Server(REST·SOAP), H: HTTP Connection to ABAP System, T: TCP/IP Connection(외부 RFC 서버 프로그램, JCo/NCo), L: Logical Destination(다른 destination 참조 + 사용자 등 일부 설정만 변경), I: Internal Connection(같은 시스템의 인스턴스, 예: NONE). 옳지 않은 것은 **⑤**. destination에는 대상 호스트, 시스템 번호, 클라이언트, 로그온 사용자(또는 Trusted RFC/현재 사용자)를 지정하고 연결·권한 테스트를 할 수 있다. 코드에서는 `CALL FUNCTION 'Z_FM' DESTINATION 'QASCLNT100'`처럼 쓴다. `NONE`은 같은 시스템에서 새 세션으로 RFC 호출, `BACK`은 호출한 쪽으로 콜백. ABAP Cloud에서는 SM59 대신 Communication Arrangement/Communication System을 쓰고 `CL_HTTP_DESTINATION_PROVIDER`, `CL_RFC_DESTINATION_PROVIDER`로 destination을 얻는다.
**(6)** ① **외부(사용자) 중단점**: B에서 FM 코드에 RFC 로그온 사용자 기준으로 외부 중단점을 건다(편집기/ADT Debugger 설정에서 디버깅할 사용자를 RFC 사용자로 지정). A에서 호출하면 B 실행이 멈추고 디버거가 뜬다. ② 호출 사용자가 B의 대화 사용자이고 SAP GUI로 B에 로그온해 있으면 호출 문장에서 따라 들어가 원격 세션 디버거가 열린다(같은 시스템이면 destination을 'NONE'으로 바꿔 로컬 디버깅). ③ 테스트 시스템 한정으로 FM에 임시 무한 루프를 넣고 B의 SM50에서 해당 work process를 디버깅. 조건: RFC 사용자가 Dialog 유형이고 디버그 권한(S_DEVELOP, OBJTYPE DEBUG)이 있어야 한다. 시스템(Communication) 사용자는 GUI가 없어 디버거를 띄울 수 없다. OData·HTTP 호출 디버깅도 같은 원리(외부 중단점 + 서비스 사용자)이며 운영 시스템 디버깅은 보통 금지된다.
**(7)** ① SM59 ② SM58 ③ SMQ1 ④ SMQ2 ⑤ SBGRFCMON ⑥ SOAMANAGER ⑦ SPROXY ⑧ SXMB_MONI

</details>

---

### B-030. BAPI: 정의·규칙·BAPIRET2·커밋·원격 커밋·Z BAPI [개념] ★★★
<!-- src: IB-090, TC-055, CL-029, IB-092, IB-091 -->
항공 예약을 만드는 BAPI 호출 코드다.

```abap
DATA: ls_booking TYPE bapisbonew,
      lv_bookid  TYPE s_book_id,
      lt_return  TYPE STANDARD TABLE OF bapiret2 WITH EMPTY KEY.
CALL FUNCTION 'BAPI_FLBOOKING_CREATEFROMDATA'
  EXPORTING booking_data  = ls_booking
  IMPORTING bookingnumber = lv_bookid
  ____(a)____ return      = lt_return.
IF line_exists( lt_return[ type = 'E' ] ) OR line_exists( lt_return[ type = ____(b)____ ] ).
  CALL FUNCTION ____(c)____.
  LOOP AT lt_return INTO DATA(ls_ret) WHERE type CA 'EA'.
    MESSAGE ID ls_ret-id TYPE 'I' NUMBER ls_ret-____(d)____
            WITH ls_ret-message_v1 ls_ret-message_v2 ls_ret-message_v3 ls_ret-message_v4.
  ENDLOOP.
ELSE.
  CALL FUNCTION 'BAPI_TRANSACTION_COMMIT' EXPORTING ____(e)____ = abap_true.
ENDIF.
```

(1) 함수 모듈, RFC 함수 모듈, BAPI의 관계와 차이를 쓰시오. BAPI는 어디에 등록되고 어디서 찾는가? 이름 형식은?
(2) BAPI가 지켜야 하는 규칙을 네 가지 이상 쓰시오. 다음 중 옳지 **않은** 것은? ① BOR 비즈니스 객체 메서드로 정의된다. ② RFC 가능 FM으로 구현된다. ③ 오류를 EXCEPTIONS 대신 RETURN으로 돌려준다. ④ BAPI 안에서 COMMIT WORK를 직접 실행하므로 호출자는 커밋할 필요가 없다. ⑤ BAPI 목록은 T-code BAPI에서 볼 수 있다.
(3) 빈칸 (a)~(e)를 채우고, BAPIRET2의 주요 필드와 WAIT = 'X'의 의미를 쓰시오.
(4) 구매 오더 생성 BAPI를 로컬로 호출할 때와 `DESTINATION 'S4_PRD'`로 원격 호출할 때 커밋을 각각 어떻게 하는가? 원격에서 커밋이 반영되지 않는 흔한 실수는?
(5) Z 테이블의 항공편 요청을 외부에서 생성할 수 있도록 Z BAPI를 만드는 절차를 순서대로 쓰시오. 면접에서 꼭 묻는 "BAPI에 COMMIT을 넣지 않는 이유"도 쓰시오.
(6) 표준 기능을 프로그램에서 실행할 때 기술 선택의 우선순위는?

<details><summary>정답·해설</summary>

**(1)** 함수 모듈 ⊃ RFC 함수 모듈(Remote-Enabled) ⊃ BAPI. 모든 BAPI는 RFC FM이지만 모든 RFC FM이 BAPI는 아니다. RFC FM은 다른 시스템에서 호출할 수 있는 FM(통신 관점)이고, BAPI는 Business Object Repository(BOR, SWO1)에 등록된 **비즈니스 객체의 메서드**로 구현된 RFC FM(예: BusinessPartner.Create → BAPI_BUPA_CREATE_FROM_DATA)으로 SAP이 인터페이스 안정성을 보장하고 문서화한 공식 API다. 트랜잭션 BAPI(BAPI Explorer)에서 찾고 이름은 `BAPI_<객체>_<메서드>` 형식이다.
**(2)** ① 내부에서 COMMIT WORK 하지 않음(호출자가 BAPI_TRANSACTION_COMMIT) ② 화면·대화 상자·MESSAGE 출력 없음, 결과는 RETURN(BAPIRET2) ③ EXCEPTIONS를 쓰지 않음(덤프하지 않음) ④ 값 전달, 인터페이스 변경 시 하위 호환 유지 ⑤ 업데이트는 업데이트 태스크로. 옳지 않은 것은 **④**.
**(3)** (a) `TABLES` (b) `'A'` (c) `'BAPI_TRANSACTION_ROLLBACK'` (d) `number` (e) `wait`. BAPIRET2: TYPE, ID, NUMBER, MESSAGE, MESSAGE_V1~V4, PARAMETER, ROW, FIELD 등. `WAIT = 'X'`이면 COMMIT WORK AND WAIT로 업데이트가 끝날 때까지 기다린다. 여러 BAPI를 한 LUW로 묶을 수 있다.
**(4)** 로컬: `CALL FUNCTION 'BAPI_PO_CREATE1' ...` → RETURN에 E/A가 없으면 `BAPI_TRANSACTION_COMMIT`(wait = 'X'), 있으면 `BAPI_TRANSACTION_ROLLBACK`. 원격: `CALL FUNCTION 'BAPI_PO_CREATE1' DESTINATION 'S4_PRD' ...` 후 커밋도 **같은 destination으로** `CALL FUNCTION 'BAPI_TRANSACTION_COMMIT' DESTINATION 'S4_PRD' EXPORTING wait = 'X'.`. 같은 RFC 연결(원격의 같은 사용자 세션) 안에서 실행되어야 BAPI가 등록한 업데이트가 커밋된다. 끝나면 `RFC_CONNECTION_CLOSE`로 닫을 수 있다. 흔한 실수: 원격 BAPI 뒤에 로컬 `COMMIT WORK`나 destination 없는 BAPI_TRANSACTION_COMMIT 호출(로컬만 커밋), BAPI 호출과 커밋 사이에 연결이 닫힘(다른 destination 이름, 연결 종료) → 원격 세션이 끝나며 롤백. 원격 BAPI 세션은 RFC 연결이 열려 있는 동안 유지된다. 비동기로 보내려면 tRFC/qRFC/bgRFC를 쓰며 결과를 즉시 받을 수 없다.
**(5)** ① 파라미터용 DDIC 구조 생성(ZBAPI_IB_REQ 등, BAPI 구조 이름 규칙) ② 함수 그룹 후 FM 생성(예: `ZBAPI_IB_REQ_CREATE`): Remote-Enabled, 모든 파라미터 값 전달, RETURN(BAPIRET2) 정의, 예외 없음 ③ 로직: 입력 검사, 오류는 RETURN에(`BALW_BAPIRETURN_GET2` 등), DB 변경은 업데이트 태스크, COMMIT 없음, 화면·MESSAGE 없음, TESTRUN 플래그 지원 권장 ④ FM 릴리스(Function Module → Release) ⑤ SWO1에서 비즈니스 객체(서브타입 또는 Z 객체)에 메서드 추가 시 "API Function"으로 FM 연결, 객체·메서드 상태를 Released로 ⑥ 트랜잭션 BAPI에서 확인, 호출 측은 RETURN 검사 → BAPI_TRANSACTION_COMMIT. 실무에서는 BOR 등록 없이 "BAPI 규칙을 따르는 RFC FM"을 BAPI라 부르기도 한다. COMMIT을 넣지 않는 이유: 호출자가 여러 BAPI를 하나의 LUW로 묶어 전부 성공/전부 롤백할 수 있게 하기 위해.
**(6)** 릴리스된 API(BAPI/CDS/RAP) → BDC 순.

</details>

---

### B-031. BAPI 대량 호출: 예약 생성 리포트 작성과 루프 오류 [작성] ★★★
<!-- src: HC-014, HC-015 -->
SFLIGHT 데이터 모델의 BAPI `BAPI_FLBOOKING_CREATEFROMDATA` 인터페이스(일부)는 다음과 같다.

| 구분 | 파라미터 | 타입 |
|---|---|---|
| IMPORTING | BOOKING_DATA | BAPISBONEW (AIRLINEID, CONNECTID, FLIGHTDATE, CUSTOMERID, CLASS, COUNTER, AGENCYNUM, PASSNAME, PASSFORM, PASSBIRTH) |
| IMPORTING | TEST_RUN | BAPISFLAUX-TESTRUN (CHAR 1, 선택) |
| EXPORTING | AIRLINEID / BOOKINGNUMBER | BAPISBOKEY-AIRLINEID / BAPISBOKEY-BOOKINGID |
| EXPORTING | TICKET_PRICE | BAPISBOPRI (PRICE, TAX, CURR, CURR_ISO) |
| TABLES | RETURN | BAPIRET2 |

(1) 예약 1건을 만드는 리포트 `ZHC_BAPI_BOOK`을 작성하시오. 선택화면: 항공사, 노선, 비행일, 고객번호(필수), 좌석 등급(기본 Y), 판매 창구 번호, 여행사 번호, 승객 이름, "시뮬레이션만" 체크박스(기본 체크).
(2) RETURN에 E 또는 A가 있으면 롤백하고 모든 메시지를 출력하게 하시오.
(3) 시뮬레이션이면 저장하지 않고 "검증 성공"과 예상 가격만 출력하게 하시오.
(4) 실제 저장이면 커밋이 끝날 때까지 기다린 뒤 예약 번호와 가격을 출력하고, 커밋 결과도 확인하게 하시오.
(5) `sy-subrc`로 성공을 판단하면 안 되는 이유, W 메시지의 의미, ROLLBACK을 하는 이유, `COMMIT WORK` 대신 `BAPI_TRANSACTION_COMMIT`을 쓰는 이유를 쓰시오.
(6) 엑셀에서 올린 `gt_input`(행 타입 BAPISBONEW)을 한 건씩 등록하는 다음 코드의 문제점을 모두 찾아 고치시오.
```abap
DATA: lt_return TYPE STANDARD TABLE OF bapiret2,
      lv_bookid TYPE bapisbokey-bookingid.
LOOP AT gt_input INTO DATA(ls_input).
  CALL FUNCTION 'BAPI_FLBOOKING_CREATEFROMDATA'
    EXPORTING booking_data = ls_input
    TABLES    return       = lt_return.
  IF sy-subrc = 0.
    COMMIT WORK.
    WRITE: / '성공', lv_bookid.
  ENDIF.
ENDLOOP.
```
(7) 대량 처리에서 "건별 커밋"과 "전체 한 번 커밋"의 선택 기준은?

<details><summary>정답·해설</summary>

**(1)~(4)** 모범 답안:
```abap
REPORT zhc_bapi_book.

PARAMETERS: p_carr  TYPE s_carr_id  OBLIGATORY,
            p_conn  TYPE s_conn_id  OBLIGATORY,
            p_date  TYPE s_date     OBLIGATORY,
            p_cust  TYPE s_customer OBLIGATORY,
            p_class TYPE s_class    DEFAULT 'Y',
            p_cntr  TYPE s_countnum,
            p_agncy TYPE s_agncynum,
            p_pname TYPE s_passname,
            p_test  AS CHECKBOX DEFAULT 'X'.

DATA: ls_booking TYPE bapisbonew,
      lv_airline TYPE bapisbokey-airlineid,
      lv_bookid  TYPE bapisbokey-bookingid,
      ls_price   TYPE bapisbopri,
      lt_return  TYPE STANDARD TABLE OF bapiret2 WITH EMPTY KEY,
      ls_commit  TYPE bapiret2.

START-OF-SELECTION.
  ls_booking = VALUE #( airlineid  = p_carr
                        connectid  = p_conn
                        flightdate = p_date
                        customerid = p_cust
                        class      = p_class
                        counter    = p_cntr
                        agencynum  = p_agncy
                        passname   = p_pname ).

  CALL FUNCTION 'BAPI_FLBOOKING_CREATEFROMDATA'
    EXPORTING
      booking_data  = ls_booking
      test_run      = p_test
    IMPORTING
      airlineid     = lv_airline
      bookingnumber = lv_bookid
      ticket_price  = ls_price
    TABLES
      return        = lt_return.

  IF line_exists( lt_return[ type = 'E' ] ) OR line_exists( lt_return[ type = 'A' ] ).
    CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.
    WRITE / '예약 실패:' COLOR COL_NEGATIVE.
    LOOP AT lt_return INTO DATA(ls_ret).
      WRITE: / ls_ret-type, ls_ret-id, ls_ret-number, ls_ret-message.
    ENDLOOP.
    RETURN.
  ENDIF.

  IF p_test = abap_true.
    CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.         " 시뮬레이션: 버퍼 정리
    WRITE: / '검증 성공(저장 안 함). 예상 가격:',
             ls_price-price CURRENCY ls_price-curr, ls_price-curr.
    RETURN.
  ENDIF.

  CALL FUNCTION 'BAPI_TRANSACTION_COMMIT'
    EXPORTING
      wait   = abap_true
    IMPORTING
      return = ls_commit.
  IF ls_commit-type CA 'EA'.
    WRITE: / '커밋 실패:', ls_commit-message.
    RETURN.
  ENDIF.

  WRITE: / '예약 생성:', lv_airline, lv_bookid,
         / '가격:', ls_price-price CURRENCY ls_price-curr, ls_price-curr.
  LOOP AT lt_return INTO ls_ret WHERE type = 'S' OR type = 'W' OR type = 'I'.
    WRITE: / ls_ret-type, ls_ret-message.
  ENDLOOP.
```

채점 기준(100점, (1)~(4)):

| 항목 | 배점 |
|---|---|
| 선택화면(필수, 기본값, 체크박스) | 10 |
| BAPISBONEW 구조 채우기 | 10 |
| CALL FUNCTION 방향(EXPORTING/IMPORTING/TABLES) 정확 | 15 |
| RETURN에서 E·A 판정(line_exists 또는 LOOP) | 20 |
| 실패 시 BAPI_TRANSACTION_ROLLBACK + 메시지 출력 | 15 |
| 시뮬레이션 분기 | 10 |
| BAPI_TRANSACTION_COMMIT WAIT = 'X' + 커밋 RETURN 확인 | 15 |
| 결과 출력(CURRENCY) | 5 |

**(5)** BAPI는 클래식 EXCEPTIONS를 쓰지 않으므로 오류가 있어도 sy-subrc는 0이다. RETURN의 TYPE(`S`, `I`, `W`, `E`, `A`)을 봐야 하며 W는 실패가 아니다. BAPI는 스스로 커밋하지 않으므로(여러 BAPI를 한 LUW로 묶기 위해) 호출자가 커밋해야 DB에 반영된다. `WAIT = 'X'`는 `COMMIT WORK AND WAIT`로, 바로 결과를 읽거나 다음 BAPI가 그 데이터를 참조할 때 필요하다. `BAPI_TRANSACTION_ROLLBACK`은 BAPI가 버퍼에 남긴 내용을 지운다. 실패 후 롤백하지 않으면 다음 커밋 때 반쪽 데이터가 함께 저장될 수 있다. `BAPI_TRANSACTION_COMMIT`은 BAPI 내부 버퍼 초기화(`BUFFER_REFRESH_ALL`)까지 해 주고 RFC로 외부에서도 호출할 수 있다.
**(6)**

| # | 문제 | 수정 |
|---|---|---|
| 1 | `sy-subrc = 0`으로 성공 판단. BAPI는 예외를 올리지 않아 오류가 있어도 0 | RETURN에 type E/A가 있는지 확인 |
| 2 | 실패 건 롤백 없음, BAPI 버퍼가 다음 성공 건 커밋 때 함께 반영될 수 있음 | 실패 시 `BAPI_TRANSACTION_ROLLBACK` |
| 3 | `COMMIT WORK`(비동기), 이전 건이 아직 반영 안 됐을 수 있고 BAPI 버퍼도 초기화 안 됨 | `BAPI_TRANSACTION_COMMIT` + `wait = 'X'` |
| 4 | `lt_return`을 매 반복 초기화하지 않아 앞 건 오류가 뒤 건에 남음 | 호출 전 `CLEAR lt_return.` |
| 5 | 예약 번호를 받지 않음(`IMPORTING bookingnumber` 누락), `lv_bookid`는 항상 초기값 | `IMPORTING bookingnumber = lv_bookid` |
| 6 | 실패 건 메시지를 기록하지 않음 | 행 번호와 RETURN 메시지를 로그에 저장·출력 |

```abap
DATA: lt_return TYPE STANDARD TABLE OF bapiret2 WITH EMPTY KEY,
      lv_bookid TYPE bapisbokey-bookingid,
      lv_carr   TYPE bapisbokey-airlineid.

LOOP AT gt_input INTO DATA(ls_input).
  DATA(lv_row) = sy-tabix.
  CLEAR: lt_return, lv_bookid, lv_carr.

  CALL FUNCTION 'BAPI_FLBOOKING_CREATEFROMDATA'
    EXPORTING
      booking_data  = ls_input
    IMPORTING
      airlineid     = lv_carr
      bookingnumber = lv_bookid
    TABLES
      return        = lt_return.

  IF line_exists( lt_return[ type = 'E' ] ) OR line_exists( lt_return[ type = 'A' ] ).
    CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.
    LOOP AT lt_return INTO DATA(ls_ret) WHERE type CA 'EA'.
      WRITE: / lv_row, '실패:', ls_ret-message.
    ENDLOOP.
  ELSE.
    CALL FUNCTION 'BAPI_TRANSACTION_COMMIT'
      EXPORTING
        wait = abap_true.
    WRITE: / lv_row, '성공:', lv_carr, lv_bookid.
  ENDIF.
ENDLOOP.
```
채점 기준((6)): 항목당 15점(최대 90점) + 수정 코드 10점.
**(7)** 업무 요구에 달렸다. 건마다 독립 문서라면 건별 커밋 + 실패 건만 롤백이 일반적이고, 모두 성공해야 의미가 있으면 루프 후 한 번에 커밋하되 하나라도 실패하면 전체 롤백한다. 어느 쪽이든 판단 근거는 RETURN이다.

</details>

---

## 인터페이스 2(IDoc · 웹 서비스 · OData)

### B-032. IDoc/ALE: 레코드·유형·ALE vs EDI·설정 순서·변경 포인터·T-code [개념] ★★
<!-- src: CL-031, TC-048, IB-095, TC-049, TC-045, IB-096, TC-046 -->
(1) IDoc을 이루는 세 레코드의 내용과 저장 테이블, 함수 모듈에서 데이터 레코드를 다룰 때 쓰는 구조(및 파일 포트용 외부 형식)를 쓰시오.
(2) 메시지 유형(Message Type), 기본 유형(Basic Type), 확장(Extension)의 관계를 예와 함께 쓰시오.
(3) ALE와 EDI를 상대·표준·전송·예 측면에서 비교하고 공통점과 파트너 유형을 쓰시오. 다음 중 옳지 **않은** 것은? ① ALE는 주로 SAP 시스템 간 분산 처리에 쓴다. ② EDI는 외부 파트너와 EDIFACT, ANSI X12로 교환한다. ③ 둘 다 IDoc을 쓸 수 있다. ④ ALE는 tRFC 포트, EDI는 보통 파일 포트나 EDI 서브시스템을 쓴다. ⑤ EDI는 IDoc을 쓰지 않으므로 파트너 프로파일이 필요 없다.
(4) ALE 아웃바운드 IDoc을 보내기 위한 설정 순서를 쓰고, 프로그램에서 IDoc을 만드는 FM과 인바운드 처리 방식(Process Code, FM 이름 관례)을 쓰시오.
(5) 자재 마스터가 바뀔 때마다 바뀐 자재만 MATMAS로 자동 배포하려 한다. 변경 포인터 설정 단계와 IDoc 생성 프로그램을 쓰시오. 포인터 저장 테이블, 최초 전체 전송, 정리 방법은?
(6) ALE/IDoc 설정 T-code를 쓰시오.

| 번호 | 기능 | T-code |
|---|---|---|
| 1 | ALE Customizing 전체 메뉴 | |
| 2 | 논리 시스템 정의 | |
| 3 | 분산 모델 | |
| 4 | 파트너 프로파일 | |
| 5 | 포트 | |
| 6 | 세그먼트 생성 | |
| 7 | 기본 IDoc 유형·확장 | |
| 8 | 메시지 유형 생성 | |
| 9 | 메시지 유형과 IDoc 유형 연결 | |
| 10 | Inbound FM과 메시지/IDoc 유형 연결 | |
| 11 | Inbound FM 속성(입력 유형 등) | |
| 12 | Inbound / Outbound Process Code | |

(7) IDoc 모니터링·테스트 T-code를 쓰시오: ① IDoc 목록·상세 조회 ② 세그먼트 필드 값으로 검색 ③ 테스트 도구 ④ 오류 IDoc 재처리 ⑤ 대기 Outbound IDoc 전송(30 → 포트) ⑥ 대기 Inbound IDoc 전달(64 → 처리) ⑦ Change Pointer로 IDoc 생성 ⑧ 메시지 유형별 Change Pointer 활성화 ⑨ 자재/고객/공급업체 마스터 IDoc 전송 ⑩ IDoc 유형 문서 조회

<details><summary>정답·해설</summary>

**(1)** 제어 레코드(IDoc 번호, 방향, 메시지 유형, IDoc 유형, 송수신 파트너·포트, 현재 상태) → **EDIDC**. 데이터 레코드(세그먼트 이름과 데이터 SDATA, 최대 1000자) → **EDID4**(구 릴리스 EDID2). 상태 레코드(상태 코드, 메시지, 시간의 이력) → **EDIDS**. FM에서 데이터 레코드 구조는 **EDIDD**(제어 레코드 구조 EDIDC), 파일 포트용 외부 형식은 EDI_DC40/EDI_DD40.
**(2)** 메시지 유형은 업무 의미(MATMAS, ORDERS), 기본 유형은 세그먼트 구조(MATMAS05, ORDERS05). 한 메시지 유형에 여러 기본 유형 버전이 연결될 수 있다(WE82). 표준 기본 유형에 Z 세그먼트(WE31)를 추가하려면 확장(WE30)을 만들어 기본 유형 + 확장으로 쓴다.
**(3)**

| 항목 | ALE | EDI |
|---|---|---|
| 상대 | 같은 회사(그룹) 안의 SAP 시스템 간 | 다른 회사(고객, 공급업체) 간 |
| 표준 | SAP IDoc 형식 그대로 | ANSI X12, EDIFACT 등(변환 필요) |
| 전송 | tRFC 포트로 시스템 간 직접 | 파일·XML/HTTP 포트 → EDI 서브시스템/미들웨어(PI/PO, Integration Suite)가 변환 |
| 예 | 중앙 시스템이 MATMAS를 지역 시스템에 배포 | 고객 구매 주문(ORDERS) 수신, 송장(INVOIC) 발송 |

공통점: 둘 다 IDoc을 컨테이너로 쓰고 파트너 프로필(WE20), 포트(WE21), 모니터링(WE02/WE05, BD87)을 공유한다. 파트너 유형은 ALE가 LS(논리 시스템), EDI는 KU(고객), LI(공급업체). ALE는 분산 모델(BD64)로 어느 시스템이 어떤 메시지 유형을 주고받는지 정의하고, EDI Outbound는 보통 출력 관리(NAST, Process Code)로 IDoc을 만든다. 옳지 않은 것은 **⑤**.
**(4)** BD54 논리 시스템 → SCC4에서 클라이언트에 논리 시스템 할당 → SM59 RFC destination → WE21 포트(tRFC 포트는 RFC destination 지정) → BD64 분산 모델 → WE20 파트너 프로파일(Outbound: 메시지 유형·포트·IDoc 유형 / Inbound: 메시지 유형·Process Code). 사용자 정의 IDoc은 WE31 → WE30(해제) → WE81 → WE82. 프로그램에서는 `MASTER_IDOC_DISTRIBUTE`에 제어 레코드와 EDIDD 테이블을 넘겨 생성하고, 변경 포인터로 자동 생성도 가능하다. 인바운드는 파트너 프로필의 Process Code(WE42)가 인바운드 FM(관례 `IDOC_INPUT_<메시지유형>`, 예: IDOC_INPUT_ORDERS)을 호출한다. Z 인바운드 FM은 데이터 레코드를 세그먼트 이름별로 CASE 처리하고 상태 레코드를 채워 돌려준다.
**(5)** ① BD61 변경 포인터 전역 활성화 ② BD50 메시지 유형(MATMAS)별 활성화 ③ BD52 변경 포인터를 쓸 테이블·필드 지정 ④ BD64·WE20에 MATMAS 아웃바운드 설정 ⑤ **BD21(RBDMIDOC)** 을 배치 잡으로 주기 실행 → 미처리 포인터로 IDoc 생성, 처리됨 표시. 변경 포인터는 변경 문서(CDHDR/CDPOS)를 기반으로 BDCP2에 기록된다. 처음 전체 전송은 BD10, 오래된 포인터 정리는 BD22.
**(6)** 1 SALE, 2 BD54, 3 BD64, 4 WE20, 5 WE21, 6 WE31, 7 WE30, 8 WE81, 9 WE82, 10 WE57, 11 BD51, 12 WE42 / WE41
**(7)** ① WE02(또는 WE05) ② WE09 ③ WE19 ④ BD87 ⑤ WE14(RSEOUT00) ⑥ BD20(RBDAPP01) ⑦ BD21(RBDMIDOC) ⑧ BD50 ⑨ BD10(MATMAS) / BD12(DEBMAS) / BD14(CREMAS) ⑩ WE60

</details>

---

### B-033. IDoc 상태 코드·재처리·Z 세그먼트 확장·중복 방지 [개념] ★★★
<!-- src: TC-047, IB-097, MX-026, IB-098, IB-099 -->
(1) 다음 IDoc 상태 코드의 의미와 방향(Outbound/Inbound)을 쓰시오: 01, 02, 03, 12, 30, 50, 51, 53, 56, 64, 68. 방향을 가르는 번호 범위와 상태 레코드 테이블은?
(2) 옳지 **않은** 것을 고르시오. ① 30 – 발송 준비됨 ② 12 – 발송 완료 ③ 64 – 인바운드 IDoc이 애플리케이션 전달 준비됨 ④ 56 – 오류가 있는 IDoc 추가됨 ⑤ 68 – 애플리케이션 문서 전기 성공
(3) 옳지 **않은** 것을 고르시오. ① IDoc은 EDIDC, EDID4, EDIDS 레코드로 구성된다. ② Message type은 업무 의미, basic type은 세그먼트 구조를 나타낸다. ③ 아웃바운드 상태 03은 포트로 넘겨졌다는 뜻이다. ④ 인바운드 상태 51은 애플리케이션 문서가 정상 전기되었다는 뜻이다. ⑤ 파트너 프로파일은 WE20, 테스트 도구는 WE19, 재처리는 BD87이다.
(4) 51 오류 IDoc과 64에 머문 IDoc은 각각 어떻게 처리하는가? 데이터 자체를 고쳐야 할 때는?
(5) 고객이 보내는 ORDERS05 IDoc에 프로젝트 코드를 추가해 받아 판매 오더 헤더 Z 필드(VBAK-ZZPROJ)에 저장하려 한다. 개발·설정 단계를 순서대로 쓰시오. BAPI로 판매 오더를 만든다면?
(6) 외부 시스템이 네트워크 재시도로 같은 주문 IDoc을 두 번 보낸다. 중복 처리를 막는 방법을 세 가지 이상 쓰고, IDoc 번호로 판단하면 안 되는 이유를 쓰시오.

<details><summary>정답·해설</summary>

**(1)** 01 IDoc 생성됨(Out), 02 포트로 전달 중 오류(Out), 03 포트로 전달 성공(Out), 12 발송 성공 Dispatch OK(Out), 30 발송 준비 완료(파트너 프로파일이 "Collect IDocs"일 때 대기)(Out), 50 IDoc 추가됨(In), 51 애플리케이션 문서 미전기, 처리 오류(In), 53 애플리케이션 문서 전기 성공(In), 56 오류가 있는 IDoc 추가(파트너 프로파일 없음 등)(In), 64 애플리케이션 전달 준비 완료, 대기(In), 68 오류 – 추가 처리 없음(종료 상태)(In). 01~49는 Outbound, 50 이상은 Inbound. 상태 레코드는 EDIDS. 아웃바운드는 30 → 03 → 12 순서로 많이 본다.
**(2)** **⑤**. 68은 "Error - no further processing"이다. 인바운드 성공은 53, 실패는 51.
**(3)** **④**. 51은 문서가 전기되지 않은 오류이고 정상 전기는 53이다. IDoc 목록은 WE02/WE05, 확장 세그먼트는 WE30/WE31.
**(4)** 51은 원인(마스터 데이터 누락 등)을 고친 뒤 BD87로 재처리한다. 64는 파트너 프로필이 "백그라운드 처리"일 때 RBDAPP01(BD20) 배치 잡이 처리한다. 데이터를 고쳐야 하면 WE19로 복사본을 만들어 수정 처리하거나, WE02에서 세그먼트(데이터 레코드)를 편집한 뒤 BD87로 처리한다(원본은 상태 70으로 보존).
**(5)** ① VBAK에 Append Structure로 ZZPROJ 추가(필요하면 판매 오더 사용자 화면 확장) ② WE31 Z 세그먼트(예: Z1IB_PROJ, 필드 PROJ) 생성·릴리스 ③ WE30 ORDERS05 확장(예: ZORD05EXT)에서 부모 세그먼트 아래 Z 세그먼트 추가·릴리스 ④ WE82 ORDERS + ORDERS05 + ZORD05EXT 연결 ⑤ WE20 인바운드 파라미터는 기존 처리 코드(ORDE → IDOC_INPUT_ORDERS) 유지 ⑥ 인바운드 FM의 Customer Exit(SMOD VEDA0001, 예: EXIT_SAPLVEDA_001 등)이나 해당 BAdI에서 Z 세그먼트를 읽어 판매 오더 생성 데이터에 넘겨 VBAK-ZZPROJ가 채워지게 구현 ⑦ WE19로 테스트 IDoc → WE02에서 상태 53 확인. 면접관은 "세그먼트 → 확장 → 메시지 유형 연결 → Exit" 순서를 본다. BAPI(BAPI_SALESORDER_CREATEFROMDAT2)라면 EXTENSIONIN 파라미터와 BAPE_VBAK/BAPE_VBAKX 구조에 ZZ 필드를 append해 넘긴다.
**(6)** ① **업무 키 중복 검사**: 인바운드 처리 초기에 외부 참조 번호(고객 PO 번호 + 고객, VBAK-BSTNK/KUNNR)로 기존 문서를 확인하고, 있으면 IDoc을 오류(51) 등으로 처리해 문서를 만들지 않음 ② **처리 이력 테이블**: 외부 메시지 ID를 Z 테이블 키로 저장하고 같은 ID는 거부(잠금으로 동시 처리도 막음) ③ **전송 계층 보장**: tRFC/qRFC/bgRFC나 미들웨어의 exactly-once(EO)/exactly-once-in-order(EOIO)로 같은 트랜잭션 ID를 한 번만 처리 ④ **직렬화**: IDoc 직렬화 그룹이나 큐 처리로 순서·중복 통제 ⑤ 걸러진 IDoc을 알림(WE02 상태, 워크플로·메일)으로 모니터링. IDoc 번호는 수신 시스템이 새로 매기므로 중복 판단에 쓸 수 없고, 송신 측이 준 업무 키나 메시지 ID를 기준으로 해야 한다.

</details>

---

### B-034. 웹 서비스(SOAP)·REST HTTP 클라이언트·인터페이스 기술 선택 [코드] ★★
<!-- src: IB-100, IB-104, IB-105 -->
SM59의 HTTP destination ZIB_REST_API(유형 G)로 GET 요청을 보내고 JSON 응답을 받는 코드다.

```abap
DATA lo_client TYPE REF TO if_http_client.
cl_http_client=>____(a)____(
  EXPORTING destination = 'ZIB_REST_API'
  IMPORTING client      = lo_client
  EXCEPTIONS OTHERS     = 1 ).
lo_client->request->set_method( ____(b)____ ).
cl_http_utility=>set_request_uri( request = lo_client->request
                                  uri     = '/flights?carrier=LH' ).
lo_client->____(c)____( EXCEPTIONS OTHERS = 1 ).
lo_client->____(d)____( EXCEPTIONS OTHERS = 1 ).
lo_client->response->get_status( IMPORTING code = DATA(lv_code) ).
DATA(lv_json) = lo_client->response->get_cdata( ).
lo_client->close( ).
```

(1) 빈칸 (a)~(d)를 채우시오.
(2) URL을 직접 줄 때의 메서드와 SSL 인증서 관리 T-code, JSON을 ABAP 구조로 바꾸는 방법, 오류 원인 확인 메서드, ABAP Cloud에서의 HTTP 클라이언트 생성 방법을 쓰시오.
(3) 기존 RFC FM을 SOAP 웹 서비스로 외부에 제공하는 단계를 쓰시오.
(4) 외부 SOAP 웹 서비스를 ABAP에서 호출하는 단계를 쓰시오. PI/PO(ESR) 기반이면 프록시를 어디서 만드는가?
(5) 다음 요구사항에 적합한 인터페이스 기술과 이유를 쓰시오. ㉠ 다른 SAP ECC에서 S/4HANA 재고를 실시간 동기 조회 ㉡ 외부 웹/모바일 앱이 고객 데이터를 조회·수정(DB 직접 연결 금지) ㉢ 하루 수만 건 주문을 거래처에서 받아 순서대로 처리하고 수신 측이 잠시 꺼져도 유실되면 안 됨
(6) 동기/비동기 기술을 분류하고 판단 기준을 쓰시오. S/4HANA Cloud에서 우선하는 것은?

<details><summary>정답·해설</summary>

**(1)** (a) `create_by_destination` (b) `if_http_request=>co_request_method_get`(또는 `'GET'`) (c) `send` (d) `receive`
**(2)** URL 직접은 `create_by_url`, SSL 인증서는 STRUST. JSON은 `/ui2/cl_json=>deserialize` 또는 `xco_cp_json`으로 ABAP 구조에 넣는다. 오류는 `get_last_error`로 확인. ABAP Cloud에서는 `cl_web_http_client_manager=>create_by_http_destination( cl_http_destination_provider=>create_by_... )`.
**(3)** 제공자(Provider): SE37(Utilities → More Utilities → Create Web Service) 또는 SE80의 Enterprise Service 마법사로 RFC FM에서 **서비스 정의** 생성 → 전송 → **SOAMANAGER**에서 서비스 엔드포인트(바인딩: URL, 인증 방식) 구성 → WSDL URL을 외부에 제공.
**(4)** 소비자(Consumer): 외부 WSDL로 SE80(또는 ADT)에서 **Consumer Proxy**(프록시 클래스, 구조) 생성 → SOAMANAGER에서 **Logical Port**(엔드포인트 URL, 인증) 생성 → 프로그램에서 `NEW zco_xxx( logical_port_name = 'ZLP' )`로 프록시 객체를 만들어 메서드 호출, `cx_ai_system_fault` 등 예외 처리. PI/PO(ESR) 기반은 SPROXY에서 서비스 인터페이스로부터 프록시를 생성한다. REST/JSON은 HTTP 클라이언트나 OData를 쓴다.
**(5)** ㉠ **sRFC(BAPI/RFC FM 동기 호출)**: SAP 간 통신으로 설정이 간단하고 빠르며 결과를 즉시 받는다. ㉡ **OData(REST)**(RAP 또는 SEGW, 필요하면 API Management 경유): HTTP/JSON 표준이라 비SAP 클라이언트가 쓰기 쉽고 권한·CSRF·ETag 등 웹 표준 보안 적용. ㉢ **IDoc(EDI/ALE) 또는 qRFC/bgRFC 기반 비동기 메시징**(미들웨어 경유): 큐에 쌓여 순서 보장(EOIO)·재처리가 가능하고 수신 측 장애 시에도 유실되지 않는다.
**(6)** 동기 = RFC/OData/SOAP, 비동기 = tRFC/qRFC/IDoc/메시징. 판단 기준은 결합도·데이터량·보안·모니터링. S/4HANA Cloud에서는 공개 API(SAP Business Accelerator Hub)와 이벤트(Business Events)가 우선이다.

</details>

---

### B-035. SAP Gateway OData(SEGW): 생성 단계·런타임 클래스·DPC_EXT·T-code·Fiori T-code [개념] ★★
<!-- src: IB-101, TC-052, IB-102, IB-103, TC-050, TC-051 -->
SEGW 프로젝트 ZIB_FLIGHT의 DPC_EXT 클래스 정의다(엔티티 셋 FlightSet).

```abap
CLASS zcl_zib_flight_dpc_ext DEFINITION PUBLIC
  INHERITING FROM zcl_zib_flight_dpc CREATE PUBLIC.
  PUBLIC SECTION.
    " POST /FlightSet (헤더 + 하위 Booking 여러 건을 한 번에)
    METHODS /iwbep/if_mgw_appl_srv_runtime~____(c)____ REDEFINITION.
    " GET /FlightSet?$expand=ToBookings (한 번에 읽기)
    METHODS /iwbep/if_mgw_appl_srv_runtime~____(d)____ REDEFINITION.
  PROTECTED SECTION.
    " GET /FlightSet
    METHODS ____(a)____ REDEFINITION.
    " GET /FlightSet(Carrid='LH',Connid='0400',Fldate=datetime'...')
    METHODS flightset_get_entity REDEFINITION.
    " POST /FlightSet
    METHODS ____(b)____ REDEFINITION.
ENDCLASS.
```

(1) SEGW로 SFLIGHT 기반 OData V2 서비스를 만들어 브라우저에서 호출할 때까지의 단계를 순서대로 쓰시오. OData의 장점과 S/4HANA 신규 개발 권장 방식은?
(2) SEGW 프로젝트의 네 폴더와 Generate 시 생성되는 런타임 클래스 네 개를 쓰시오.
(3) 빈칸 (a)~(d)를 채우고, 엔티티 셋마다 생성되는 CRUD 메서드(PUT/MERGE, DELETE 포함)와 Function Import·$batch 처리용 메서드를 쓰시오. $expand를 재정의하지 않으면 어떻게 되는가?
(4) 코드를 DPC가 아니라 DPC_EXT에 작성하는 가장 중요한 이유는? ① DPC는 final이라 메서드를 추가할 수 없어서 ② Generate Runtime Objects를 다시 실행하면 DPC/MPC는 재생성되어 수정이 사라지지만 _EXT는 유지되어서 ③ DPC_EXT만 Gateway 허브에 전송되어서 ④ DPC_EXT는 OData V4만 지원해서. MPC_EXT로 할 수 있는 일은?
(5) 다음 T-code를 쓰시오: ① 프로젝트 생성 ② V2 서비스 등록·활성화 ③ 서비스 테스트 ④ 허브(프런트엔드) 오류 로그 ⑤ 백엔드 오류 로그 ⑥ 메타데이터 캐시 삭제(프런트/백엔드) ⑦ V4 서비스 그룹 게시·관리 ⑧ Gateway 트레이스. 네임스페이스 T-code 입력 방법과 RAP 서비스의 게시 방법은?
(6) 다음 Fiori T-code·리포트를 쓰시오: ① Launchpad 실행 ② Launchpad Designer 클라이언트 종속 ③ 클라이언트 독립 ④ Semantic Object 정의 ⑤ UI5 앱 BSP 저장소 업로드 리포트 ⑥ 앱 인덱스 재계산 리포트 ⑦ Intent Analysis ⑧ 카탈로그를 사용자에게 할당하는 역할 관리. 타일과 Target Mapping의 연결 방식, 최신 릴리스의 도구는?

<details><summary>정답·해설</summary>

**(1)** ① SEGW에서 프로젝트 생성(패키지 지정) ② Data Model: Entity Type(Flight, 키 Carrid/Connid/Fldate)과 Entity Set(FlightSet) 생성. DDIC 구조 import, RFC/BOR import, CDS 참조(Reference → Data Source) 가능, 필요하면 Association/Navigation ③ **Generate Runtime Objects**: MPC, MPC_EXT, DPC, DPC_EXT, 모델·서비스 등록 이름 생성 ④ DPC_EXT에서 `FLIGHTSET_GET_ENTITYSET`, `FLIGHTSET_GET_ENTITY` 등 재정의 ⑤ **/IWFND/MAINT_SERVICE**에서 서비스 추가(시스템 별칭) → ICF 노드 활성화 ⑥ **/IWFND/GW_CLIENT**(또는 브라우저)로 `/sap/opu/odata/sap/ZIB_FLIGHT_SRV/$metadata`, `/FlightSet` 테스트. 오류는 /IWFND/ERROR_LOG(허브), /IWBEP/ERROR_LOG(백엔드), 캐시 문제는 /IWFND/CACHE_CLEANUP. 장점: REST 기반 표준, $metadata로 자기 기술, $filter/$top/$expand 쿼리 옵션, Fiori/UI5와 바로 연동. S/4HANA 신규 개발은 SEGW 대신 RAP 서비스 바인딩을 권장한다.
**(2)** 폴더: Data Model(Entity Types, Associations, Entity Sets), Service Implementation, Runtime Artifacts, Service Maintenance. 클래스: `ZCL_<프로젝트>_MPC`(Model Provider 기본), `_MPC_EXT`, `ZCL_<프로젝트>_DPC`(Data Provider 기본), `_DPC_EXT`.
**(3)** (a) `flightset_get_entityset` (b) `flightset_create_entity` (c) `create_deep_entity` (d) `get_expanded_entityset`. 엔티티 셋마다 `_GET_ENTITYSET`(목록), `_GET_ENTITY`(단건), `_CREATE_ENTITY`(POST), `_UPDATE_ENTITY`(PUT/PATCH/MERGE), `_DELETE_ENTITY`(DELETE)가 생성된다(예: `TRAVELSET_GET_ENTITYSET`). 딥 인서트·$expand·Function Import(`EXECUTE_ACTION`)·$batch(`CHANGESET_BEGIN/END`)는 인터페이스 /IWBEP/IF_MGW_APPL_SRV_RUNTIME의 메서드를 재정의한다. $expand는 재정의하지 않아도 프레임워크가 내비게이션별로 GET_ENTITYSET을 반복 호출해 처리하지만 느리다.
**(4)** **②**. _EXT는 기본 클래스를 상속한 하위 클래스라 재정의(REDEFINITION)한 코드가 보존된다. MPC_EXT의 DEFINE 메서드를 재정의해 모델에 어노테이션이나 속성을 코드로 추가할 수 있다.
**(5)** ① SEGW ② /IWFND/MAINT_SERVICE ③ /IWFND/GW_CLIENT ④ /IWFND/ERROR_LOG ⑤ /IWBEP/ERROR_LOG ⑥ /IWFND/CACHE_CLEANUP / /IWBEP/CACHE_CLEANUP ⑦ /IWFND/V4_ADMIN ⑧ /IWFND/TRACES. 네임스페이스가 있으므로 명령 필드에 `/n/IWFND/MAINT_SERVICE`처럼 `/n`을 붙인다. RAP 서비스는 SEGW 없이 ADT의 Service Binding에서 Publish한다(V2는 내부적으로 /IWFND/MAINT_SERVICE에 등록). 메타데이터 변경이 안 보이면 캐시 삭제부터 한다.
**(6)** ① /UI2/FLP ② /UI2/FLPD_CUST ③ /UI2/FLPD_CONF ④ /UI2/SEMOBJ ⑤ /UI5/UI5_REPOSITORY_LOAD ⑥ /UI5/APP_INDEX_CALCULATE ⑦ /UI2/FLIA ⑧ PFCG. 타일은 Semantic Object + Action(Intent, 예: `#Travel-manage`)으로 Target Mapping과 연결된다. 최신 릴리스는 Launchpad Content Manager(/UI2/FLPCM_CUST, /UI2/FLPCM_CONF)와 Spaces/Pages를 쓰고, 앱 배포는 BAS/VS Code의 `npm run deploy`가 같은 저장소 업로드를 수행한다.

</details>

---

## 데이터 이관(BDC · LSMW · Migration Cockpit) · 파일 처리

### B-036. 데이터 이관 방법 비교와 BDC: BDCDATA·CALL TRANSACTION·세션·CTU_PARAMS·오류 처리 [코드] ★★★
<!-- src: IB-082, MX-024, IB-087, CL-032, TC-053, IB-083, IB-084, IB-085, IB-086 -->
트랜잭션 ZCL_REQ(프로그램 SAPMZCL_REQ, 화면 0100)에 BDC로 항공사를 입력·저장하는 코드와 배치 입력 세션 ZIB_SESS를 만드는 코드다.

```abap
DATA: lt_bdc TYPE STANDARD TABLE OF bdcdata WITH EMPTY KEY,
      lt_msg TYPE STANDARD TABLE OF bdcmsgcoll WITH EMPTY KEY.
lt_bdc = VALUE #(
  ( program = 'SAPMZCL_REQ' dynpro = '0100' ____(a)____ = 'X' )
  ( fnam = '____(b)____' fval = 'GS_REQ-CARRID' )
  ( fnam = 'GS_REQ-CARRID' fval = 'LH' )
  ( fnam = 'BDC_OKCODE'    fval = '=SAVE' ) ).
CALL TRANSACTION 'ZCL_REQ' ____(c)____ lt_bdc
     MODE ____(d)____          " 화면 표시 안 함
     UPDATE ____(e)____        " 동기 업데이트
     MESSAGES INTO lt_msg.

CALL FUNCTION '____(f)____'
  EXPORTING client = sy-mandt  group = 'ZIB_SESS'  user = sy-uname  keep = 'X'.
LOOP AT gt_data INTO gs_data.
  PERFORM fill_bdcdata USING gs_data.       " gt_bdcdata 작성
  CALL FUNCTION '____(g)____'
    EXPORTING tcode = 'ZIB_REQ'
    TABLES    dynprotab = gt_bdcdata.
ENDLOOP.
CALL FUNCTION '____(h)____'.
```

(1) 레거시 데이터 이관 방법 BDC, BAPI, Direct Input, IDoc, LSMW를 비교하고 S/4HANA 권장 도구를 쓰시오. 고객 5만 건을 옮길 때의 우선순위와 이유는? 좋은 이관 프로그램 설계에 들어갈 단계는?
(2) LSMW에 대한 설명 중 옳지 **않은** 것은? ① Import Method로 Standard/Batch Input(Direct Input 포함), Batch Input Recording, Business Object Method(BAPI), IDoc을 고른다. ② Project → Subproject → Object 단위로 관리한다. ③ 소스 구조·필드 정의, 구조 관계, 필드 매핑·변환 규칙, 파일 지정, 읽기, 변환 순서로 진행한다. ④ 변환 규칙에 ABAP 코드를 쓸 수 있다. ⑤ S/4HANA 이관의 표준 권장 도구는 LSMW다. LSMW 프로젝트를 옮기는 방법은?
(3) 빈칸 (a)~(e)를 채우고, BDCDATA 다섯 필드와 OK code·커서 행, MODE(A/E/N/P)와 UPDATE(S/A/L) 값의 의미를 쓰시오. 녹화 T-code와 BAPI 우선 원칙도 쓰시오.
(4) 빈칸 (f)~(h)를 채우고, 세션 처리 트랜잭션과 백그라운드 일괄 처리 프로그램, `keep`, `holddate`의 의미, BDC_OPEN_GROUP을 두 번 부를 때의 문제를 쓰시오.
(5) Call Transaction 방식과 Session 방식을 처리 시점, DB 업데이트, 오류 로그, 트랜잭션 수, 속도, sy-subrc 측면에서 비교하시오. 세션 처리 모드 세 가지와 대량 이관의 혼합 방식은?
(6) Call Transaction의 오류 메시지를 텍스트로 만드는 방법, 오류 건 재처리 방법, Session 방식 오류 확인 방법을 쓰시오. sy-subrc = 0만으로 성공을 판단하면 위험한 이유는?
(7) `OPTIONS FROM ls_ctu`의 CTU_PARAMS 주요 필드(DISMODE, UPDMODE, DEFSIZE, RACOMMIT, NOBINPT)를 쓰고, Table Control 화면에 여러 행을 BDC로 입력할 때의 문제와 해결 방법을 쓰시오.

<details><summary>정답·해설</summary>

**(1)**

| 방법 | 특징 |
|---|---|
| BDC(Batch Input) | 화면을 녹화(SHDB)해 사용자 입력을 흉내 냄. 모든 화면 검사가 수행되지만 느리고 화면 변경에 취약 |
| BAPI | 표준 비즈니스 객체 API. 화면 없이 빠르고 안정적, BAPIRET2 메시지가 명확, `BAPI_TRANSACTION_COMMIT`으로 커밋. 있으면 1순위 |
| Direct Input | SAP 제공 프로그램(RMDATIND 자재, RFBIBL00 회계)이 화면 없이 검사 후 직접 기록. 빠르지만 대상 제한 |
| IDoc | 인바운드 IDoc 처리 FM으로 기록. 대량·재처리(BD87)에 유리 |
| LSMW | 위 방법들을 감싸는 코딩 최소화 도구. 매핑·변환 규칙을 화면에서 정의 |

S/4HANA: **SAP S/4HANA Migration Cockpit**(Fiori 앱 "Migrate Your Data", 구 LTMC, 모델러 LTMOM). 스테이징 테이블 또는 SAP 시스템 직접 전송 방식이며 표준 이관 객체·템플릿·검증·매핑을 제공한다. LSMW는 S/4HANA에서 권장되지 않는다. 우선순위: Migration Cockpit 표준 이관 객체 → 없으면 BAPI 프로그램 → BAPI가 없을 때만 BDC(S/4HANA 고객은 Business Partner라 BP용 API를 쓴다). 설계 단계: 파일 형식 정의 → 검증·변환 → 시뮬레이션(BAPI의 TESTRUN) → 오류 로그 → 재처리 → 이관 후 조정(reconciliation).
**(2)** **⑤**. S/4HANA에서는 Migration Cockpit이 권장이고 LSMW는 "사용 가능하지만 권장하지 않음(일부 기능은 단순화로 맞지 않음)". LSMW 프로젝트는 전송 요청이 아니라 Export/Import 기능이나 전용 전송으로 옮긴다.
**(3)** (a) `dynbegin` (b) `BDC_CURSOR` (c) `USING` (d) `'N'` (e) `'S'`. BDCDATA: PROGRAM, DYNPRO, DYNBEGIN, FNAM, FVAL. 화면 시작 행은 PROGRAM, DYNPRO, DYNBEGIN = 'X', 필드 행은 FNAM(예 `VBAK-AUART`)/FVAL. OK code는 FNAM = `BDC_OKCODE`, 커서는 `BDC_CURSOR`. MODE: A 모든 화면 표시, E 오류 화면만, N 표시 안 함(백그라운드), P 표시 없이 실행하되 디버깅 가능. UPDATE: S 동기, A 비동기, L 로컬. 결과 메시지는 `MESSAGES INTO itab`(BDCMSGCOLL). 녹화는 SHDB. BAPI가 있으면 화면 변경에 영향받지 않는 BAPI가 우선이다.
**(4)** (f) `BDC_OPEN_GROUP` (g) `BDC_INSERT` (h) `BDC_CLOSE_GROUP`. 처리는 **SM35**, 백그라운드 일괄 처리는 RSBDCSUB. `keep = 'X'`면 처리 후에도 세션을 삭제하지 않고 남기고, `holddate`를 주면 그 날짜 전에는 처리할 수 없다. 한 번에 하나의 세션만 열 수 있어 CLOSE 없이 OPEN을 두 번 부르면 오류가 난다.
**(5)**

| 항목 | Call Transaction | Session |
|---|---|---|
| 처리 시점 | 실행 즉시(동기) | 세션을 만들어 두고 나중에 SM35에서(비동기) |
| DB 업데이트 | S/A/L 선택 | 동기 |
| 오류 로그 | 자동 로그 없음, MESSAGES INTO로 직접 처리 | SM35에 자동으로 남고 오류 건만 재처리 |
| 트랜잭션 수 | 호출 하나에 하나 | 한 세션에 여러 개 |
| 속도 | 빠름 | 느림 |
| sy-subrc | 바로 결과 확인 | 세션 생성 시점에는 결과 모름 |

세션 처리 모드: Process/Foreground, Display errors only, Background. 대량 이관은 Call Transaction으로 처리하고 실패 건만 세션으로 만들어 재처리하는 혼합 방식을 많이 쓴다.
**(6)** `MESSAGES INTO lt_msg`(BDCMSGCOLL)의 MSGID, MSGNR, MSGV1~4로 `FORMAT_MESSAGE`(또는 `MESSAGE ID ... TYPE ... NUMBER ... INTO lv_text WITH ...`)를 호출해 텍스트로 만들고, MSGTYP E/A를 오류로 본다(sy-subrc ≠ 0도 확인). 재처리: 오류 레코드를 로그 파일/테이블에 남기거나, 실패한 BDCDATA로 BDC_OPEN_GROUP/BDC_INSERT/BDC_CLOSE_GROUP 오류 세션을 만들어 SM35에서 다시 처리. Session: SM35에서 세션 선택 → Log에서 트랜잭션별 메시지 확인 → 오류 트랜잭션을 "Display errors only"로 다시 처리. sy-subrc = 0이어도 경고·정보 메시지가 있을 수 있으므로 생성 문서 번호 메시지(S 메시지의 MSGV1)로 성공을 확인하는 것이 안전하다.
**(7)** DISMODE: 화면 표시 모드(A/E/N). UPDMODE: 업데이트 모드(S/A/L). DEFSIZE = 'X': 화면을 기본 크기로 고정해 사용자 GUI 창 크기와 무관하게 Table Control의 보이는 행 수를 일정하게 함. RACOMMIT: COMMIT WORK가 있어도 BDC를 끝내지 않음. NOBINPT: sy-binpt를 설정하지 않음. Table Control 문제: 보이는 행 수가 화면 크기에 따라 달라 녹화 때의 `필드(01)`~`필드(nn)` 행 번호가 실행 환경과 맞지 않을 수 있다. 해결: DEFSIZE = 'X'로 고정, 보이는 행을 다 채우면 페이지 다운(`=P+`)이나 "새 항목 위치" 함수로 스크롤한 뒤 1번 행부터 다시 채운다. 필드 이름은 `RV45A-MABNR(01)`처럼 행 번호 2자리. 녹화는 SHDB에서 "Default size"를 켜고 한다. 가능하면 BAPI(BAPI_SALESORDER_CREATEFROMDAT2)로 대체한다.

</details>

---

### B-037. CALL TRANSACTION BDC 프로그램 작성(실패 건 세션) [작성] ★★★
<!-- src: HC-016 -->
Z 대화형 트랜잭션 `ZHC_CARR`(항공사 등록)를 SHDB로 녹화한 결과다.

| Program | Screen | Start | Field name | Field value |
|---|---|---|---|---|
| SAPMZHC_CARR | 0100 | X | | |
| | | | BDC_CURSOR | SCARR-CARRID |
| | | | BDC_OKCODE | =CREA |
| | | | SCARR-CARRID | ZZ |
| SAPMZHC_CARR | 0200 | X | | |
| | | | BDC_CURSOR | SCARR-URL |
| | | | SCARR-CARRNAME | Test Air |
| | | | SCARR-CURRCODE | KRW |
| | | | SCARR-URL | http://www.test.com |
| | | | BDC_OKCODE | =SAVE |

업로드된 데이터가 `gt_carr`(CARRID, CARRNAME, CURRCODE, URL)에 들어 있다.

(1) BDCDATA를 쌓는 FORM `bdc_dynpro`, `bdc_field`를 작성하시오.
(2) 한 건마다 녹화대로 BDCDATA를 만들어 `CALL TRANSACTION`으로 처리하시오. 화면 표시 모드는 선택화면 `p_mode`(기본 'N'), 업데이트는 동기, 화면 크기는 표준 크기.
(3) 메시지를 모아 건마다 성공/실패와 메시지 텍스트를 출력하시오.
(4) 실패 건은 SM35에서 재처리할 수 있도록 batch input 세션 `ZHC_CARR_ERR`로 만드시오(세션은 한 번만 연다).
(5) 날짜·숫자 필드를 BDC에 넣을 때의 주의점과 `defsize`를 주지 않을 때의 문제를 쓰시오.

<details><summary>정답·해설</summary>

**(1)~(4)** 모범 답안:
```abap
REPORT zhc_bdc_carr.

PARAMETERS p_mode TYPE ctu_params-dismode DEFAULT 'N'.

TYPES: BEGIN OF ty_carr,
         carrid   TYPE scarr-carrid,
         carrname TYPE scarr-carrname,
         currcode TYPE scarr-currcode,
         url      TYPE scarr-url,
       END OF ty_carr.

DATA: gt_carr  TYPE STANDARD TABLE OF ty_carr WITH EMPTY KEY,
      gt_bdc   TYPE STANDARD TABLE OF bdcdata WITH EMPTY KEY,
      gt_msg   TYPE STANDARD TABLE OF bdcmsgcoll WITH EMPTY KEY,
      gv_group TYPE abap_bool.                 " 세션을 열었는지

START-OF-SELECTION.
  PERFORM upload_file.                         " gt_carr 채움(문제 범위 밖)

  DATA(ls_opt) = VALUE ctu_params( dismode = p_mode
                                   updmode = 'S'
                                   defsize = abap_true ).

  LOOP AT gt_carr INTO DATA(ls_carr).
    CLEAR: gt_bdc, gt_msg.

    PERFORM bdc_dynpro USING 'SAPMZHC_CARR' '0100'.
    PERFORM bdc_field  USING 'BDC_CURSOR'   'SCARR-CARRID'.
    PERFORM bdc_field  USING 'BDC_OKCODE'   '=CREA'.
    PERFORM bdc_field  USING 'SCARR-CARRID' ls_carr-carrid.

    PERFORM bdc_dynpro USING 'SAPMZHC_CARR' '0200'.
    PERFORM bdc_field  USING 'SCARR-CARRNAME' ls_carr-carrname.
    PERFORM bdc_field  USING 'SCARR-CURRCODE' ls_carr-currcode.
    PERFORM bdc_field  USING 'SCARR-URL'      ls_carr-url.
    PERFORM bdc_field  USING 'BDC_OKCODE'     '=SAVE'.

    CALL TRANSACTION 'ZHC_CARR' USING gt_bdc
                     OPTIONS FROM ls_opt
                     MESSAGES INTO gt_msg.
    DATA(lv_subrc) = sy-subrc.

    " 결과 판정: sy-subrc 또는 메시지 중 E/A
    IF lv_subrc = 0 AND NOT line_exists( gt_msg[ msgtyp = 'E' ] )
                    AND NOT line_exists( gt_msg[ msgtyp = 'A' ] ).
      WRITE: / ls_carr-carrid, '성공' COLOR COL_POSITIVE.
    ELSE.
      WRITE: / ls_carr-carrid, '실패' COLOR COL_NEGATIVE.
      PERFORM add_to_session.
    ENDIF.

    LOOP AT gt_msg INTO DATA(ls_msg).
      MESSAGE ID ls_msg-msgid TYPE ls_msg-msgtyp NUMBER ls_msg-msgnr
              WITH ls_msg-msgv1 ls_msg-msgv2 ls_msg-msgv3 ls_msg-msgv4
              INTO DATA(lv_text).
      WRITE: /5 ls_msg-msgtyp, lv_text.
    ENDLOOP.
  ENDLOOP.

  IF gv_group = abap_true.
    CALL FUNCTION 'BDC_CLOSE_GROUP'.
    WRITE: / '실패 건은 SM35 세션 ZHC_CARR_ERR에서 재처리하십시오.'.
  ENDIF.

*----------------------------------------------------------------------
FORM bdc_dynpro USING iv_program TYPE clike
                      iv_dynpro  TYPE clike.
  APPEND VALUE #( program  = iv_program
                  dynpro   = iv_dynpro
                  dynbegin = abap_true ) TO gt_bdc.
ENDFORM.

FORM bdc_field USING iv_fnam TYPE clike
                     iv_fval TYPE clike.
  APPEND VALUE #( fnam = iv_fnam fval = iv_fval ) TO gt_bdc.
ENDFORM.

FORM add_to_session.
  IF gv_group = abap_false.
    CALL FUNCTION 'BDC_OPEN_GROUP'
      EXPORTING
        client = sy-mandt
        group  = 'ZHC_CARR_ERR'
        user   = sy-uname
        keep   = abap_true.
    gv_group = abap_true.
  ENDIF.
  CALL FUNCTION 'BDC_INSERT'
    EXPORTING
      tcode     = 'ZHC_CARR'
    TABLES
      dynprotab = gt_bdc.
ENDFORM.

FORM upload_file.
  " GUI_UPLOAD 등으로 gt_carr 채우기 (B-038 참조)
ENDFORM.
```

채점 기준(100점):

| 항목 | 배점 |
|---|---|
| BDCDATA 구조 이해(첫 줄 program/dynpro/dynbegin, 이후 fnam/fval) | 15 |
| 녹화대로 화면·필드·OK 코드(`=CREA`, `=SAVE`) 순서 | 15 |
| 건마다 gt_bdc/gt_msg 초기화 | 10 |
| CTU_PARAMS(dismode, updmode = 'S', defsize) + OPTIONS FROM | 15 |
| CALL TRANSACTION ... USING ... MESSAGES INTO | 15 |
| 성공/실패 판정 + MESSAGE ... INTO로 텍스트 변환 | 15 |
| 실패 건 세션(BDC_OPEN_GROUP 한 번, BDC_INSERT, BDC_CLOSE_GROUP) | 15 |

정석 FORM `bdc_dynpro`/`bdc_field`는 SHDB의 "프로그램 생성" 기능이 만들어 주는 구조와 같다. 대량 처리 결과를 바로 판정하려면 업데이트 모드 `S`를 쓴다. 최근에는 표준 BAPI·API가 있으면 BDC보다 그쪽을 우선한다.
**(5)** 날짜·숫자 필드는 화면에 입력하듯 **사용자 형식의 문자**로 넣어야 한다(예: `WRITE lv_date TO lv_char`). 내부 형식 `20261013`을 그대로 넣으면 사용자 날짜 형식 설정에 따라 오류가 난다. `defsize = 'X'`가 없으면 사용자 GUI 창 크기에 따라 테이블 컨트롤의 보이는 줄 수가 달라져 BDC가 깨질 수 있다.

</details>

---

### B-038. PC 파일 업로드·다운로드: GUI_UPLOAD/GUI_DOWNLOAD·검증·CSV [작성] ★★★
<!-- src: IB-088, TC-030, HC-017, HC-018 -->
(1) 옳지 **않은** 것을 고르시오. ① GUI_UPLOAD(또는 `cl_gui_frontend_services=>gui_upload`)는 사용자 PC(프레젠테이션 서버)의 파일을 읽는다. ② OPEN DATASET은 애플리케이션 서버 파일을 읽고 쓰며 AL11에서 볼 수 있다. ③ 배치 잡에서 PC 파일을 읽으려면 GUI_UPLOAD를 쓰면 된다. ④ 엑셀 파일은 탭 구분 텍스트로 저장해 읽거나 ALSM_EXCEL_TO_INTERNAL_TABLE·XCO/abap2xlsx 같은 별도 방법을 쓴다.
(2) 빈칸을 채우시오. ㉠ 서버 디렉터리·파일 조회 T-code ㉡ 서버 파일 → PC 다운로드 T-code ㉢ PC 파일 → 서버 업로드 T-code ㉣ 논리 파일 이름·경로 정의(클라이언트 독립) ㉤ 서버 파일 문장: ( ) / READ DATASET / TRANSFER / CLOSE DATASET ㉥ PC 파일을 읽는 메서드 CL_GUI_FRONTEND_SERVICES=>( )
(3) PC의 탭 구분 텍스트 파일(UTF-8, 첫 줄 제목 행, 형식 `CARRID<TAB>CONNID<TAB>FLDATE(YYYYMMDD)<TAB>PRICE<TAB>CURRENCY`)에서 항공편 가격 변경 데이터를 읽어 검증하는 `ZHC_UPLOAD`를 작성하시오. 요구사항: `p_file` F4로 파일 열기 대화 상자, `gui_upload`로 문자열 테이블에 읽기, 날짜 8자리·유효성, 가격 숫자(변환 예외), 항공사·노선 SPFLI 존재(DB 조회 한 번), 결과(줄 번호, 데이터, OK/ERR, 오류 내용)를 SALV로 출력, DB 변경 없음.
(4) (3)에서 `has_field_separator`로 바로 구조에 올리지 않는 이유, 탭 상수, 변환 예외 두 가지, 백그라운드 실행 시 대안, .xlsx 처리 방법을 쓰시오.
(5) 선택한 항공사의 SFLIGHT를 세미콜론 CSV로 PC에 저장하는 `ZHC_DOWNLOAD`를 작성하시오. 제목 행 `CARRID;CONNID;FLDATE;PRICE;CURRENCY;FREE_SEATS`, 날짜 `YYYY-MM-DD`, 가격은 `.` 소수 2자리·천 단위 구분 없음, "다른 이름으로 저장" 대화 상자로 위치를 받고 취소 시 조용히 종료, 엑셀 한글 깨짐 방지 UTF-8 BOM.
(6) (5)에서 문자열 템플릿 숫자 형식, `DATE = ISO`와 `WRITE ... TO`의 차이, `user_action` 비교 상수를 쓰시오.

<details><summary>정답·해설</summary>

**(1)** **③**. 배치 잡에는 SAP GUI가 연결되어 있지 않아 프런트엔드 서비스(GUI_UPLOAD/GUI_DOWNLOAD)를 쓸 수 없다. 대량·주기적 이관은 파일을 서버에 올리고(CG3Z 또는 별도 전송) OPEN DATASET으로 읽는 배치 프로그램으로 만들며, `sy-batch`로 분기해 경고할 수 있다.
**(2)** ㉠ AL11 ㉡ CG3Y ㉢ CG3Z ㉣ FILE ㉤ OPEN DATASET ㉥ GUI_UPLOAD. 함수 모듈 `GUI_UPLOAD`/`GUI_DOWNLOAD`도 같은 기능이다. 경로를 하드코딩하지 말고 FILE의 논리 파일명과 `FILE_GET_NAME`을 쓴다.
**(3)** 모범 답안:
```abap
REPORT zhc_upload.

PARAMETERS p_file TYPE localfile OBLIGATORY.

TYPES: BEGIN OF ty_result,
         line     TYPE i,
         carrid   TYPE sflight-carrid,
         connid   TYPE sflight-connid,
         fldate   TYPE sflight-fldate,
         price    TYPE sflight-price,
         currency TYPE sflight-currency,
         status   TYPE char3,
         msg      TYPE char80,
       END OF ty_result.

DATA gt_result TYPE STANDARD TABLE OF ty_result WITH EMPTY KEY.

AT SELECTION-SCREEN ON VALUE-REQUEST FOR p_file.
  DATA: lt_files TYPE filetable,
        lv_rc    TYPE i.
  cl_gui_frontend_services=>file_open_dialog(
    EXPORTING  window_title = '업로드 파일 선택'
               file_filter  = 'Text (*.txt)|*.txt'
    CHANGING   file_table   = lt_files
               rc           = lv_rc
    EXCEPTIONS OTHERS       = 1 ).
  IF sy-subrc = 0 AND lv_rc = 1.
    p_file = lt_files[ 1 ]-filename.
  ENDIF.

START-OF-SELECTION.
  DATA lt_lines TYPE STANDARD TABLE OF string WITH EMPTY KEY.

  cl_gui_frontend_services=>gui_upload(
    EXPORTING  filename = CONV #( p_file )
               filetype = 'ASC'
               codepage = '4110'                " UTF-8
    CHANGING   data_tab = lt_lines
    EXCEPTIONS OTHERS   = 1 ).
  IF sy-subrc <> 0.
    MESSAGE '파일을 읽을 수 없습니다' TYPE 'S' DISPLAY LIKE 'E'.
    RETURN.
  ENDIF.

  " 노선 마스터를 한 번만 읽어 해시 테이블로
  TYPES: BEGIN OF ty_key, carrid TYPE spfli-carrid, connid TYPE spfli-connid, END OF ty_key.
  DATA lt_conn TYPE HASHED TABLE OF ty_key WITH UNIQUE KEY carrid connid.
  SELECT carrid, connid FROM spfli INTO TABLE @lt_conn.

  LOOP AT lt_lines INTO DATA(lv_line) FROM 2.        " 1행은 제목
    DATA(ls_res) = VALUE ty_result( line = sy-tabix status = 'OK' ).
    SPLIT lv_line AT cl_abap_char_utilities=>horizontal_tab
          INTO DATA(lv_carr) DATA(lv_conn) DATA(lv_date)
               DATA(lv_price) DATA(lv_curr).

    ls_res-carrid   = to_upper( lv_carr ).
    ls_res-connid   = lv_conn.
    ls_res-currency = to_upper( lv_curr ).

    " 날짜 검사
    IF strlen( lv_date ) <> 8 OR lv_date CN '0123456789'.
      ls_res = VALUE #( BASE ls_res status = 'ERR' msg = '날짜 형식 오류' ).
    ELSE.
      ls_res-fldate = lv_date.
      CALL FUNCTION 'DATE_CHECK_PLAUSIBILITY'
        EXPORTING
          date                      = ls_res-fldate
        EXCEPTIONS
          plausibility_check_failed = 1
          OTHERS                    = 2.
      IF sy-subrc <> 0.
        ls_res = VALUE #( BASE ls_res status = 'ERR' msg = '존재하지 않는 날짜' ).
      ENDIF.
    ENDIF.

    " 가격 검사
    IF ls_res-status = 'OK'.
      TRY.
          ls_res-price = lv_price.
        CATCH cx_sy_conversion_no_number cx_sy_conversion_overflow.
          ls_res = VALUE #( BASE ls_res status = 'ERR' msg = '가격이 숫자가 아님' ).
      ENDTRY.
    ENDIF.

    " 노선 존재 검사
    IF ls_res-status = 'OK' AND
       NOT line_exists( lt_conn[ carrid = ls_res-carrid connid = ls_res-connid ] ).
      ls_res = VALUE #( BASE ls_res status = 'ERR' msg = '노선 없음' ).
    ENDIF.

    APPEND ls_res TO gt_result.
  ENDLOOP.

  IF gt_result IS INITIAL.
    MESSAGE '데이터 행이 없습니다' TYPE 'S' DISPLAY LIKE 'E'.
    RETURN.
  ENDIF.

  TRY.
      cl_salv_table=>factory( IMPORTING r_salv_table = DATA(lo_alv)
                              CHANGING  t_table      = gt_result ).
      lo_alv->get_functions( )->set_all( abap_true ).
      lo_alv->get_columns( )->set_optimize( abap_true ).
      lo_alv->display( ).
    CATCH cx_salv_msg.
      MESSAGE 'ALV 오류' TYPE 'S' DISPLAY LIKE 'E'.
  ENDTRY.
```

채점 기준(100점, (3)):

| 항목 | 배점 |
|---|---|
| F4: AT SELECTION-SCREEN ON VALUE-REQUEST + file_open_dialog + rc 확인 | 15 |
| gui_upload(filename, filetype ASC, codepage, data_tab) + 예외 처리 | 15 |
| 제목 행 건너뛰기, SPLIT AT 탭 문자 | 15 |
| 날짜 검증(형식 + 유효성) | 10 |
| 숫자 변환 TRY/CATCH | 15 |
| 마스터를 루프 밖에서 한 번 읽고 해시 룩업 | 15 |
| 결과 테이블 + SALV 출력 | 15 |

**(4)** `has_field_separator = abap_true`로 구조 테이블에 바로 올리면 숫자·날짜 필드의 잘못된 값 때문에 업로드가 실패하거나 엉뚱하게 변환된다. 문자열로 받아 직접 나눠 검증하는 쪽이 높게 평가된다. 탭 상수는 `cl_abap_char_utilities=>horizontal_tab`(CSV는 `','`/`';'`, 따옴표 안 쉼표까지 요구되면 별도 파싱). 문자 → 숫자(p) 변환 실패는 `cx_sy_conversion_no_number`, 자릿수 초과는 `cx_sy_conversion_overflow`. GUI 업로드는 SAP GUI가 필요해 백그라운드에서는 동작하지 않으므로 서버 파일 + OPEN DATASET을 쓴다. .xlsx는 `TEXT_CONVERT_XLS_TO_SAP` 함수나 `cl_fdt_xl_spreadsheet` 같은 클래스를 쓴다.
**(5)** 모범 답안:
```abap
REPORT zhc_download.

TABLES sflight.
SELECT-OPTIONS s_carr FOR sflight-carrid.

START-OF-SELECTION.
  SELECT carrid, connid, fldate, price, currency, seatsmax, seatsocc
    FROM sflight
    WHERE carrid IN @s_carr
    ORDER BY carrid, connid, fldate
    INTO TABLE @DATA(lt_fl).
  IF lt_fl IS INITIAL.
    MESSAGE '데이터가 없습니다' TYPE 'S' DISPLAY LIKE 'E'.
    RETURN.
  ENDIF.

  DATA lt_csv TYPE STANDARD TABLE OF string WITH EMPTY KEY.
  APPEND `CARRID;CONNID;FLDATE;PRICE;CURRENCY;FREE_SEATS` TO lt_csv.
  LOOP AT lt_fl INTO DATA(ls_fl).
    APPEND |{ ls_fl-carrid };{ ls_fl-connid };{ ls_fl-fldate DATE = ISO };| &&
           |{ ls_fl-price DECIMALS = 2 };{ ls_fl-currency };| &&
           |{ ls_fl-seatsmax - ls_fl-seatsocc }| TO lt_csv.
  ENDLOOP.

  DATA: lv_filename TYPE string,
        lv_path     TYPE string,
        lv_fullpath TYPE string,
        lv_action   TYPE i.

  cl_gui_frontend_services=>file_save_dialog(
    EXPORTING  window_title      = 'CSV 저장'
               default_extension = 'csv'
               default_file_name = |flights_{ sy-datum }.csv|
               file_filter       = 'CSV (*.csv)|*.csv'
    CHANGING   filename          = lv_filename
               path              = lv_path
               fullpath          = lv_fullpath
               user_action       = lv_action
    EXCEPTIONS OTHERS            = 1 ).
  IF sy-subrc <> 0 OR lv_action <> cl_gui_frontend_services=>action_ok.
    RETURN.                                      " 취소
  ENDIF.

  cl_gui_frontend_services=>gui_download(
    EXPORTING  filename  = lv_fullpath
               filetype  = 'ASC'
               codepage  = '4110'
               write_bom = abap_true
    CHANGING   data_tab  = lt_csv
    EXCEPTIONS OTHERS    = 1 ).
  IF sy-subrc = 0.
    MESSAGE |{ lines( lt_csv ) - 1 }건 저장: { lv_fullpath }| TYPE 'S'.
  ELSE.
    MESSAGE '파일 저장 실패' TYPE 'S' DISPLAY LIKE 'E'.
  ENDIF.
```

채점 기준(100점, (5)):

| 항목 | 배점 |
|---|---|
| SELECT + 빈 결과 처리 | 10 |
| 제목 행 + 데이터 행을 문자열 테이블로 구성 | 20 |
| 날짜(DATE = ISO)·숫자(DECIMALS, 구분 기호 없음) 형식 | 20 |
| file_save_dialog + user_action 확인 | 20 |
| gui_download(filename, ASC, codepage, BOM) + 결과 처리 | 20 |
| 빈 좌석 계산 | 10 |

구식 `GUI_DOWNLOAD` 함수, `WS_DOWNLOAD`(폐기)로 쓴 답도 부분 점수. 백그라운드 실행이 필요하면 OPEN DATASET으로 서버에 쓴다.
**(6)** 문자열 템플릿의 기본 숫자 형식은 천 단위 구분 없이 `.`을 소수점으로 써서 기계가 읽는 CSV에 알맞다(사용자 형식은 `NUMBER = USER`). `DATE = ISO`는 `YYYY-MM-DD`로 고정이고, `WRITE ... TO`는 사용자 설정에 따라 형식이 바뀌어 파일 교환용으로 부적합하다. `user_action`은 `cl_gui_frontend_services=>action_ok`, `action_cancel`과 비교한다.

</details>

---

### B-039. 애플리케이션 서버 파일: OPEN DATASET 읽기·쓰기와 오류 [작성] ★★
<!-- src: IB-089, HC-019, HC-020 -->
애플리케이션 서버의 텍스트 파일을 한 줄씩 읽는 코드다.

```abap
PARAMETERS p_file TYPE string LOWER CASE DEFAULT '/usr/sap/trans/data/flights.txt'.
DATA: lv_line TYPE string,
      lt_raw  TYPE STANDARD TABLE OF string WITH EMPTY KEY.
START-OF-SELECTION.
  OPEN DATASET p_file FOR ____(a)____ IN TEXT MODE ENCODING ____(b)____.
  IF sy-subrc <> 0.
    MESSAGE 'File cannot be opened' TYPE 'E'.
  ENDIF.
  DO.
    ____(c)____ DATASET p_file INTO lv_line.
    IF sy-subrc <> 0.
      EXIT.
    ENDIF.
    APPEND lv_line TO lt_raw.
  ENDDO.
  ____(d)____ DATASET p_file.
```

(1) 빈칸 (a)~(d)를 채우고, 쓰기용 OPEN 옵션 두 가지와 쓰기 문장, 파일 끝의 sy-subrc, 보안상 권장 방법을 쓰시오.
(2) 백그라운드 잡으로 실행되는 `ZHC_DATASET`을 작성하시오. 선택화면: 서버 경로 `p_file`(기본 `/usr/sap/trans/tmp/zhc_book.txt`, 소문자 유지), 항공사 `p_carr`. 그 항공사의 취소되지 않은 SBOOK을 `BOOKID;CUSTOMID;FLDATE;LOCCURAM;LOCCURKEY` 형식 UTF-8 텍스트로 쓰고, 닫은 뒤 다시 열어 건수와 금액 합계를 출력해 쓴 건수와 비교한다. 열 수 없으면 메시지 후 종료, 파일은 반드시 닫는다.
(3) (2)에서 ENCODING 필수 여부, 경로를 소문자로 받는 이유, 열기 실패의 두 가지 신호(sy-subrc, 예외 클래스), 마지막 줄에 줄바꿈이 없을 때의 주의, 서버 파일 확인 T-code를 쓰시오.
(4) 다음 코드의 문제를 모두 찾아 고치시오(문법 오류 포함).
```abap
DATA: gt_fl   TYPE STANDARD TABLE OF sflight,
      gs_fl   TYPE sflight,
      lv_line TYPE string,
      lt_line TYPE STANDARD TABLE OF string,
      lv_file TYPE string VALUE '/tmp/flights.txt'.
SELECT * FROM sflight INTO TABLE gt_fl.
OPEN DATASET lv_file FOR OUTPUT.
LOOP AT gt_fl INTO gs_fl.
  TRANSFER gs_fl TO lv_file.
ENDLOOP.
OPEN DATASET lv_file FOR INPUT IN TEXT MODE ENCODING DEFAULT.
WHILE sy-subrc = 0.
  READ DATASET lv_file INTO lv_line.
  APPEND lv_line TO lt_line.
ENDWHILE.
```
(5) 서면 시험에서 OPEN DATASET 문제의 고정 출제 포인트 세 가지는?

<details><summary>정답·해설</summary>

**(1)** (a) `INPUT` (b) `DEFAULT`(또는 `UTF-8`) (c) `READ` (d) `CLOSE`. 쓰기는 `FOR OUTPUT`(덮어쓰기)·`FOR APPENDING`, 그리고 `TRANSFER lv_line TO p_file.`. 파일 끝에서 READ DATASET은 sy-subrc = 4. 사용자 입력 경로를 그대로 열면 보안 문제가 있으므로 논리 파일명(FILE 트랜잭션, FILE_GET_NAME)과 권한 객체 S_DATASET 검사(`AUTHORITY_CHECK_DATASET`)를 쓴다.
**(2)** 모범 답안:
```abap
REPORT zhc_dataset.

PARAMETERS: p_file TYPE string LOWER CASE DEFAULT '/usr/sap/trans/tmp/zhc_book.txt',
            p_carr TYPE s_carr_id OBLIGATORY.

START-OF-SELECTION.
  SELECT bookid, customid, fldate, loccuram, loccurkey
    FROM sbook
    WHERE carrid = @p_carr
      AND cancelled = @space
    ORDER BY fldate, bookid
    INTO TABLE @DATA(lt_book).

  " 1) 쓰기
  TRY.
      OPEN DATASET p_file FOR OUTPUT IN TEXT MODE ENCODING UTF-8.
    CATCH cx_sy_file_open cx_sy_file_authority INTO DATA(lx_open).
      MESSAGE lx_open->get_text( ) TYPE 'S' DISPLAY LIKE 'E'.
      RETURN.
  ENDTRY.
  IF sy-subrc <> 0.
    MESSAGE |파일을 열 수 없습니다: { p_file }| TYPE 'S' DISPLAY LIKE 'E'.
    RETURN.
  ENDIF.

  LOOP AT lt_book INTO DATA(ls_book).
    DATA(lv_out) = |{ ls_book-bookid };{ ls_book-customid };{ ls_book-fldate };| &&
                   |{ ls_book-loccuram };{ ls_book-loccurkey }|.
    TRANSFER lv_out TO p_file.
  ENDLOOP.
  CLOSE DATASET p_file.
  DATA(lv_written) = lines( lt_book ).

  " 2) 다시 읽기
  DATA: lv_line  TYPE string,
        lv_count TYPE i,
        lv_sum   TYPE p LENGTH 15 DECIMALS 2.

  OPEN DATASET p_file FOR INPUT IN TEXT MODE ENCODING UTF-8.
  IF sy-subrc <> 0.
    MESSAGE '다시 읽기 실패' TYPE 'S' DISPLAY LIKE 'E'.
    RETURN.
  ENDIF.

  DO.
    READ DATASET p_file INTO lv_line.
    IF sy-subrc <> 0.
      EXIT.                                   " 파일 끝
    ENDIF.
    SPLIT lv_line AT ';' INTO DATA(lv_bookid) DATA(lv_cust)
                              DATA(lv_date) DATA(lv_amt) DATA(lv_curr).
    lv_count += 1.
    lv_sum   += CONV decfloat34( lv_amt ).
  ENDDO.
  CLOSE DATASET p_file.

  WRITE: / '쓴 건수:', lv_written,
         / '읽은 건수:', lv_count,
         / '금액 합계:', lv_sum.
  IF lv_written <> lv_count.
    WRITE / '건수 불일치!' COLOR COL_NEGATIVE.
  ENDIF.
```

채점 기준(100점, (2)):

| 항목 | 배점 |
|---|---|
| OPEN DATASET FOR OUTPUT IN TEXT MODE ENCODING UTF-8 | 15 |
| 열기 실패 처리(sy-subrc 및/또는 예외) | 15 |
| 한 줄 문자열 구성 + TRANSFER | 15 |
| CLOSE DATASET (쓰기 후, 읽기 후 둘 다) | 15 |
| FOR INPUT + DO/READ DATASET/sy-subrc로 EXIT | 20 |
| SPLIT과 금액 합계, 건수 비교 | 15 |
| 경로 PARAMETERS LOWER CASE | 5 |

**(3)** 유니코드 프로그램에서 `IN TEXT MODE`이면 `ENCODING`이 필수다(없으면 문법 오류). 이진 모드는 `IN BINARY MODE`. 유닉스 경로는 대소문자를 구분하는데 선택화면 파라미터는 기본적으로 대문자로 바뀌므로 `LOWER CASE`가 필요하다. 열기 실패는 sy-subrc(8)로, 권한 없음·이미 열린 파일은 `cx_sy_file_authority`, `cx_sy_file_open` 예외로 알려 준다. 실무에서는 논리 파일 이름(FILE, `FILE_GET_NAME`)과 `AUTHORITY_CHECK_DATASET`을 함께 쓴다(언급 시 가산). 마지막 줄에 줄바꿈이 없으면 그 줄을 읽으면서 sy-subrc = 4가 될 수 있어 `lv_line IS NOT INITIAL`이면 처리하는 보완이 가능하다(이 프로그램은 TRANSFER가 줄마다 줄바꿈을 붙이므로 해당 없음). 서버 파일은 SAP GUI 없이 접근 가능해 백그라운드 잡·외부 인터페이스에 쓰이며 AL11에서 확인한다.
**(4)**

| # | 문제 | 수정 |
|---|---|---|
| 1 | `FOR OUTPUT`에 모드와 인코딩이 없음 → 유니코드 프로그램에서 문법 오류 | `FOR OUTPUT IN TEXT MODE ENCODING UTF-8` |
| 2 | 텍스트 모드에서 숫자형(p, i) 컴포넌트가 있는 구조 `gs_fl`을 TRANSFER → 오류(텍스트 모드는 문자형만) | 문자열 템플릿이나 CONCATENATE로 한 줄 문자열을 만들어 TRANSFER |
| 3 | 쓰기 후 CLOSE 없이 같은 파일을 다시 OPEN → `cx_sy_file_open` | 쓰기 끝나면 `CLOSE DATASET lv_file.` |
| 4 | 쓰기와 읽기의 인코딩이 다를 수 있음(읽기는 DEFAULT) | 양쪽 모두 `ENCODING UTF-8` |
| 5 | `WHILE sy-subrc = 0`이 루프 전 OPEN 결과에 의존하고, READ 실패 뒤에도 APPEND가 실행되어 쓸모없는 행 추가 | `DO. READ ... IF sy-subrc <> 0. EXIT. ENDIF. APPEND ... ENDDO.` |
| 6 | 읽기 후 CLOSE 없음 | `CLOSE DATASET lv_file.` |
| 7 | OPEN 결과 확인 없음, 경로 하드코딩(`/tmp`) | sy-subrc 확인·예외 처리, 논리 파일 이름 |
| 8 | SFLIGHT 전체를 조건 없이 읽음 | 필요한 조건·필드만 SELECT |

```abap
SELECT carrid, connid, fldate, price, currency FROM sflight
  WHERE carrid IN @s_carr
  INTO TABLE @DATA(gt_fl).

OPEN DATASET lv_file FOR OUTPUT IN TEXT MODE ENCODING UTF-8.
IF sy-subrc <> 0.
  MESSAGE '열기 실패' TYPE 'E'.
ENDIF.
LOOP AT gt_fl INTO DATA(gs_fl).
  lv_line = |{ gs_fl-carrid };{ gs_fl-connid };{ gs_fl-fldate };{ gs_fl-price };{ gs_fl-currency }|.
  TRANSFER lv_line TO lv_file.
ENDLOOP.
CLOSE DATASET lv_file.

OPEN DATASET lv_file FOR INPUT IN TEXT MODE ENCODING UTF-8.
IF sy-subrc = 0.
  DO.
    READ DATASET lv_file INTO lv_line.
    IF sy-subrc <> 0.
      EXIT.
    ENDIF.
    APPEND lv_line TO lt_line.
  ENDDO.
  CLOSE DATASET lv_file.
ENDIF.
```
채점 기준((4)): 1~6 각 15점(최대 90점), 7·8 지적 시 각 5점.
**(5)** "ENCODING 필수", "CLOSE 누락", "EOF 판정".

</details>

---

## 확장(Enhancement)

### B-040. 확장 기법 비교: User/Customer Exit·Enhancement Point/Section·SPDD/SPAU·T-code [개념] ★★
<!-- src: CL-033, TC-099, MX-027, TC-005, IB-106, IB-107, IB-110, IB-112, TC-004 -->
(1) User Exit, Customer Exit, Classic BAdI, New BAdI, Enhancement Point/Section을 정의 방법(트랜잭션)과 구현 방법으로 비교하시오. 고려 우선순위와 S/4HANA Cloud에서의 제약은?
(2) 표준 프로그램에서 다음 단서를 발견했다. 각각 어떤 확장 기법인가? ㉠ include `MV45AFZZ`의 `FORM USEREXIT_SAVE_DOCUMENT_PREPARE.` ㉡ `CALL CUSTOMER-FUNCTION '001'` ㉢ `GET BADI lo_badi.` / `CALL BADI lo_badi->check ...` ㉣ `CALL METHOD cl_exithandler=>get_instance` ㉤ `ENHANCEMENT-POINT ep_01 SPOTS es_sales.` ㉥ `CALL FUNCTION 'OPEN_FI_PERFORM_00001025_E'` ㉦ 메서드·FORM·FM의 시작과 끝에 선언 없이 코드를 넣을 수 있는 위치
(3) Implicit와 Explicit Enhancement, Enhancement Point와 Section의 차이를 쓰시오. Implicit Enhancement로 코드를 추가할 수 **없는** 위치는? ① FORM·FM·메서드의 시작과 끝 ② include 끝, 구조체 정의 끝 ③ 글로벌 클래스 메서드의 Pre-/Post-/Overwrite ④ FM 인터페이스에 optional 파라미터 추가 ⑤ 표준 프로그램 IF 문 안의 임의의 줄. 편집기에서 위치를 표시하는 방법은?
(4) 옳지 **않은** 것을 고르시오. ① MV45AFZZ의 USEREXIT FORM 같은 user exit는 SAP 이름 공간 include를 고치므로 객체 등록 키가 필요하다. ② Customer exit는 SMOD에서 찾고 CMOD 프로젝트에서 구현·활성화한다. ③ 하나의 SMOD enhancement는 여러 CMOD 프로젝트에 동시에 할당해 각각 활성화할 수 있다. ④ Classic BAdI는 SE18에서 정의를 보고 SE19에서 구현하며 Multiple use면 여러 구현이 동시에 실행된다. ⑤ ZX로 시작하는 exit include는 고객 네임스페이스라 수정이 아니다.
(5) Customer Exit의 종류 네 가지와 표준 코드에서의 형태, 특정 트랜잭션의 Exit/BAdI를 찾는 방법, CMOD 구현 단계를 쓰시오.
(6) SAP 표준 화면에 Z 필드를 보여 주는 Screen Exit의 빈칸을 채우시오.
```abap
PROCESS BEFORE OUTPUT.
  CALL ____(a)____ cust_area INCLUDING 'SAPLXQQM' '0101'.
PROCESS AFTER INPUT.
  CALL ____(a)____ cust_area.
```
구현: CMOD에서 화면 SAPLXQQM ____(b)____ 를 유형 ____(c)____ 화면으로 만들고 Z 필드를 배치, 데이터 전달은 같은 Enhancement의 ____(d)____ (PBO용·PAI용)에서 함수 그룹 XQQM 전역 변수로, 프로젝트 활성화.
(7) 업그레이드 시 SPDD와 SPAU의 차이, 수정과 확장이 업그레이드에 미치는 영향을 비교하시오.
(8) 다음 T-code를 쓰시오: ① BAdI 정의 ② BAdI 구현 ③ Enhancement Spot ④ Customer Exit 정의 조회 ⑤ Customer Exit 프로젝트 ⑥ Modification Browser ⑦ 업그레이드 후 Repository 수정 조정 ⑧ 업그레이드 중 DDIC 수정 조정 ⑨ SAP Note 적용 ⑩ BTE ⑪ 확장 구현 조정

<details><summary>정답·해설</summary>

**(1)**

| 기법 | 정의 | 구현 |
|---|---|---|
| User Exit | SAP이 표준 include에 둔 빈 FORM(MV45AFZZ의 USEREXIT_SAVE_DOCUMENT 등) | 해당 FORM에 코드. SAP 네임스페이스 수정이라 액세스 키 필요(SD에서 주로) |
| Customer Exit | SMOD(Enhancement), `CALL CUSTOMER-FUNCTION '001'` | CMOD 프로젝트 → 함수 Exit의 Z include(ZX...)에 코드 → 활성화. 메뉴·화면 Exit도 있음 |
| Classic BAdI | SE18 정의(인터페이스), `CL_EXITHANDLER=>GET_INSTANCE`로 호출 | SE19 구현(클래스). 다중 사용·필터 |
| New BAdI | Enhancement Spot 안에 정의(SE18), `GET BADI`/`CALL BADI`(커널 기반, 빠름) | SE19 Enhancement Implementation + 구현 클래스. Fallback, 필터, 스위치 프레임워크 |
| Enhancement Point/Section | Enhancement Framework | 위치에 코드 추가(Point) 또는 대체(Section). 수정 키 불필요 |

수정(Modification)은 업그레이드 때 SPAU 조정이 필요하지만 BAdI·Enhancement는 표준 코드를 바꾸지 않아 안전하다. 우선순위는 보통 BAdI/BTE/Customer Exit → Enhancement Point → User Exit → (최후) 수정. S/4HANA Cloud/ABAP Cloud에서는 Released BAdI(Key User/Developer Extensibility)만 쓸 수 있다.
**(2)** ㉠ User Exit(수정 키가 필요한 SAP 네임스페이스 include의 빈 FORM) ㉡ Customer Exit(function exit, SMOD/CMOD) ㉢ New BAdI(커널 BAdI, Enhancement Spot, SE18/SE19) ㉣ Classic BAdI ㉤ Explicit Enhancement Point ㉥ BTE(FIBF) ㉦ Implicit Enhancement Point
**(3)** **Implicit**: SAP이 표시하지 않아도 모든 프로그램에 있는 위치(FORM·FM·메서드의 시작과 끝, include 끝, 구조체 끝, 로컬 클래스 섹션 끝, 메서드 pre/post/overwrite). **Explicit**: SAP이 `ENHANCEMENT-POINT` 또는 `ENHANCEMENT-SECTION ... END-ENHANCEMENT-SECTION`으로 명시한 위치. **Point**는 그 위치에 코드를 "추가", **Section**은 섹션 안 원래 코드를 "대체"(활성 구현 하나만 적용). 추가할 수 없는 위치는 **⑤**: 코드 중간 임의 위치는 SAP이 Explicit을 두지 않았다면 수정만 가능하다. 편집기 Edit → Enhancement Operations → Show Implicit Enhancement Options로 표시한다.
**(4)** **③**. SMOD enhancement 하나는 CMOD 프로젝트 **하나에만** 할당할 수 있어, 여러 팀이 같은 exit를 쓰려면 한 프로젝트 안에서 코드를 나눠야 한다. 이것이 여러 구현을 허용하는 BAdI가 나온 이유 중 하나다. `CALL CUSTOMER-FUNCTION '001'`은 FM `EXIT_<프로그램명>_001`을 부르고, FM 안 `INCLUDE ZXxxxU01.`을 더블클릭해 생성한다.
**(5)** Function Exit: `CALL CUSTOMER-FUNCTION '001'` → FM `EXIT_<프로그램>_001` 안 ZX include. Menu Exit: GUI 상태에 `+`로 시작하는 함수 코드(+CU1). Screen Exit: 흐름 로직의 `CALL CUSTOMER-SUBSCREEN`. Field Exit: 데이터 엘리먼트 단위 필드 검사(obsolete). 찾는 방법: ① 프로그램(System → Status) 소스에서 `CALL CUSTOMER-FUNCTION`, `GET BADI`, `CL_EXITHANDLER` 검색 후 FM 이름으로 SMOD Enhancement 찾기(테이블 MODSAP) ② 패키지를 확인해 SMOD/SE84에서 그 패키지로 Enhancement 검색, SPRO IMG 문서 ③ `CALL CUSTOMER-FUNCTION`/`CL_EXITHANDLER=>GET_INSTANCE`/`CALL BADI`에 중단점을 걸고 실행 ④ ST05 트레이스에서 BAdI 관련 테이블 접근 확인. CMOD: 프로젝트 생성 → Enhancement Assignments에 할당 → Components에서 Exit 구현(ZX include, 화면·메뉴 텍스트) → **활성화**. 프로젝트를 비활성화하면 Exit 코드가 실행되지 않아 운영 장애 시 빠른 차단 수단으로 쓰기도 한다.
**(6)** (a) `CUSTOMER-SUBSCREEN` (b) `0101` (c) Subscreen (d) Function Exit(EXIT_... FM). Screen Exit의 subscreen은 고객 함수 그룹(X로 시작, XQQM)에 속해 표준 프로그램 변수를 직접 볼 수 없으므로, SAP이 PBO 전에 데이터를 넘겨주는 Function Exit과 PAI 후 값을 돌려받는 Function Exit을 함께 제공한다. Z 필드 자체는 표준 테이블에 Append(또는 CI include)로 추가한다.
**(7)** **SPDD**: 수정한 **DDIC 객체**를 업그레이드 중 새 버전과 조정, 새 DDIC 활성화 전에 해야 데이터 손실(필드 삭제 등)을 막는다. **SPAU**: 수정한 **Repository 객체**(프로그램, 화면, 메뉴, Note 수정)를 업그레이드 후 조정, 고객 수정 유지 또는 표준 복귀 결정. Enhancement 구현은 SPAU_ENH에서 확인. SPDD가 먼저, SPAU가 나중. 수정은 표준 객체 자체를 바꿔 매번 조정이 생기고(수정 키 SSCR 필요), 확장(BAdI, Exit, Enhancement Point, Append)은 표준을 바꾸지 않아 조정이 거의 없다. S/4HANA의 Clean Core 원칙은 수정을 없애고 릴리스된 확장 지점만 쓰라는 것이다.
**(8)** ① SE18 ② SE19 ③ SE20 ④ SMOD ⑤ CMOD ⑥ SE95 ⑦ SPAU ⑧ SPDD ⑨ SNOTE ⑩ FIBF ⑪ SPAU_ENH. SMOD에서 Enhancement(예: V45A0002)의 구성요소(function, screen, menu exit)를 보고 CMOD에서 Z 프로젝트에 할당한다.

</details>

---

### B-041. BAdI(Classic/New·단일/다중·필터)·BTE·FI Validation/Substitution [코드] ★★
<!-- src: CL-034, CL-035, IB-111, IB-108, IB-109 -->
Enhancement Spot에 정의된 단일 사용 BAdI `ZBADI_CL_REQ_CHECK`(필터 `COUNTRY`)를 호출한다. 활성 구현도 Fallback 클래스도 없으면 검사를 건너뛴다.

```abap
DATA lo_badi TYPE REF TO zbadi_cl_req_check.
DATA lv_ok   TYPE abap_bool VALUE abap_true.
TRY.
    ____(a)____ lo_badi ____(b)____ country = 'DE'.
  CATCH ____(c)____.
    RETURN.
ENDTRY.
____(d)____ lo_badi->check( EXPORTING is_req = ls_req
                         CHANGING  cv_ok  = lv_ok ).
```

(1) 빈칸 (a)~(d)를 채우시오.
(2) 단일 사용 BAdI와 다중 사용 BAdI에서 구현이 없을 때, 둘 이상일 때의 동작을 쓰고, 다중 사용 BAdI 메서드가 EXPORTING/RETURNING을 가질 수 없는 이유를 쓰시오. Classic BAdI 호출 방법은?
(3) 옳지 **않은** 것을 고르시오. ① Classic BAdI는 SE18에서 정의하고 `CL_EXITHANDLER=>GET_INSTANCE`로 구현 객체를 얻는다. ② New BAdI는 Enhancement Spot 구성 요소이며 `GET BADI`/`CALL BADI`로 호출한다. ③ New BAdI는 Fallback 클래스로 활성 구현이 없을 때의 기본 동작을 정할 수 있다. ④ 다중 사용 BAdI 메서드에는 RETURNING을 정의할 수 없다. ⑤ New BAdI를 구현하려면 SAP 표준 객체를 수정하는 것이므로 액세스 키가 필요하다.
(4) 옳지 **않은** 것을 고르시오. ① 다중 사용 BAdI는 활성 구현이 여러 개면 모두 실행된다. ② 다중 사용 BAdI 구현의 실행 순서는 기본적으로 보장되지 않는다. ③ 필터로 국가·회사코드에 따라 다른 구현이 실행되게 할 수 있다. ④ 단일 사용 BAdI에 같은 필터 조건의 활성 구현이 두 개면 차례로 모두 실행된다. 순서를 꼭 정해야 하면?
(5) BTE가 무엇이며 주로 어느 모듈에서 쓰이는가? Publish & Subscribe와 Process 인터페이스의 차이, 구현 절차를 쓰시오.
(6) FI 전표 입력 시 ㉠ 특정 계정에는 원가센터가 반드시 있어야 하는 검사와 ㉡ 적요가 비면 자동으로 채우는 처리를 코딩 없이(최소 코딩) 구현하는 방법과 트랜잭션을 쓰시오. 규칙으로 표현하기 어려운 로직은?

<details><summary>정답·해설</summary>

**(1)** (a) `GET BADI` (b) `FILTERS` (c) `cx_badi_not_implemented` (d) `CALL BADI`
**(2)** 단일 사용: 조건에 맞는 활성 구현이 정확히 하나(또는 Fallback)여야 한다. 없으면 `GET BADI`가 CX_BADI_NOT_IMPLEMENTED, 둘 이상이면 CX_BADI_MULTIPLY_IMPLEMENTED. 다중 사용: 구현이 없어도 예외가 없고 `CALL BADI`가 아무 일도 하지 않으며, 여럿이면 모두 실행된다. 여러 구현의 결과를 하나로 정할 수 없으므로 다중 사용 BAdI 메서드는 EXPORTING/RETURNING을 가질 수 없고 위 예처럼 CHANGING을 쓴다. Classic BAdI: `CALL METHOD cl_exithandler=>get_instance CHANGING instance = lo_classic_badi.` 후 인터페이스 메서드를 직접 호출.
**(3)** **⑤**. BAdI 구현은 Enhancement Framework로 고객 네임스페이스의 Enhancement Implementation과 클래스를 만드는 것이라 수정 키가 필요 없고 SPAU 대상도 아니다(SPAU_ENH에서 확인만). 수정 키가 필요한 것은 User Exit include나 표준 소스 직접 수정이다.
**(4)** **④**. 단일 사용 BAdI에 활성 구현이 둘 이상이면 CX_BADI_MULTIPLY_IMPLEMENTED가 발생한다. 다중 사용 BAdI의 순서를 꼭 정해야 하면 정렬용 BAdI(BADI_SORTER)를 쓰지만 드물다. 순서에 의존하는 로직은 만들지 않는다.
**(5)** BTE: FI(및 일부 SD, CO) 표준 프로그램이 정해진 시점에 `OPEN_FI_PERFORM_<이벤트번호>_E`(P/S) 또는 `_P`(Process) FM을 호출하고, 그 이벤트에 등록된 고객 FM을 실행하는 확장 기법. 트랜잭션 **FIBF**. P/S 인터페이스: 정보 전달용, 표준 처리에 데이터를 돌려줄 수 없고 여러 구현이 동시에 실행 가능(예: 전표 전기 후 외부 알림). Process 인터페이스: 표준 로직을 대체·변경, 결과를 돌려줄 수 있고 조건(국가·애플리케이션)당 하나의 구현만 활성. 구현: FIBF → Environment → Info System에서 이벤트와 샘플 FM(`SAMPLE_INTERFACE_<번호>`/`SAMPLE_PROCESS_<번호>`) 확인 → Z FM으로 복사(인터페이스 유지)·코드 작성 → FIBF에서 고객 제품(Product) 생성·활성화 → 이벤트에 Z FM과 제품 등록. Enhancement Framework 이전부터 있던 기법이다.
**(6)** ㉠ **Validation**(GGB0): 시점(헤더/라인/전체 전표), 전제조건(계정 = X), 검사(원가센터 ≠ 공백), 실패 메시지 정의 → 회사코드에 할당·활성화 **OB28**. ㉡ **Substitution**(GGB1): 전제조건과 대체 규칙(필드 = 상수/필드/Exit) → 활성화 **OBBH**. 어려운 로직은 **사용자 Exit 폼 풀**(RGGBR000을 복사한 Z 프로그램, GCX2에서 등록)의 FORM에 ABAP으로 작성해 규칙에서 호출한다. 규칙은 클라이언트 종속 커스터마이징이고 Exit 폼 풀은 Repository 객체다. 설정 중심이라 기능 컨설턴트와 협업하는 경우가 많다.

</details>

---

## 성능

### B-042. SQL 성능 오류 고치기: 루프 안 SELECT·FOR ALL ENTRIES·BINARY SEARCH·병렬 커서 [코드] ★★★
<!-- src: CL-038, IB-113, MX-029, IB-114 -->
(1) 다음 코드(항공편별 예약 건수)의 문제를 찾고 하나의 SELECT로 고치시오.
```abap
SELECT * FROM sflight INTO TABLE @DATA(lt_flight) WHERE carrid IN @s_carr.
LOOP AT lt_flight INTO DATA(ls_flight).
  SELECT * FROM sbook INTO TABLE @DATA(lt_book)
    WHERE carrid = @ls_flight-carrid AND connid = @ls_flight-connid AND fldate = @ls_flight-fldate.
  ls_flight-seatsocc = lines( lt_book ).
  MODIFY lt_flight FROM ls_flight.
ENDLOOP.
```
(2) 다음 코드(항공편별 예약 금액 합계용)의 정확성 문제 두 가지를 찾아 고치고, FOR ALL ENTRIES의 3대 함정을 쓰시오.
```abap
SELECT carrid, connid, fldate, loccuram
  FROM sbook
  FOR ALL ENTRIES IN @lt_flight
  WHERE carrid = @lt_flight-carrid AND connid = @lt_flight-connid AND fldate = @lt_flight-fldate
  INTO TABLE @DATA(lt_amount).
```
(3) 다음 코드의 성능 문제 세 가지를 찾고 하나의 SELECT로 고치시오.
```abap
SELECT * FROM sbook INTO @DATA(ls_book).
  CHECK ls_book-cancelled = space.
  CHECK ls_book-fldate >= p_from.
  SELECT SINGLE carrname FROM scarr WHERE carrid = @ls_book-carrid INTO @ls_out-carrname.
  ls_out-bookid = ls_book-bookid.
  ls_out-carrid = ls_book-carrid.
  APPEND ls_out TO lt_out.
  SORT lt_out BY bookid.
ENDSELECT.
```
(4) 다음 코드에서 성능 문제와 논리 오류를 네 가지 이상 찾고 고친 코드를 쓰시오.
```abap
SELECT * FROM sbook INTO TABLE @DATA(lt_book) WHERE fldate >= @p_date.
SELECT * FROM scarr INTO TABLE @DATA(lt_carr).
LOOP AT lt_book INTO DATA(ls_book).
  SELECT SINGLE name FROM scustom INTO @DATA(lv_name) WHERE id = @ls_book-customid.
  READ TABLE lt_carr INTO DATA(ls_carr) WITH KEY carrid = ls_book-carrid BINARY SEARCH.
  APPEND VALUE #( bookid = ls_book-bookid carrname = ls_carr-carrname custname = lv_name ) TO gt_out.
ENDLOOP.
```
(5) 표준 테이블 lt_spfli(노선)와 lt_sflight(항공편, 수십만 건, 둘 다 키 carrid, connid)에서 노선마다 해당 항공편을 처리하는 중첩 루프를 병렬 커서 기법으로 작성하고, 비교 횟수 변화와 대안을 쓰시오.
(6) 면접에서 "성능 튜닝 경험"을 물으면 어떻게 답하는가?

<details><summary>정답·해설</summary>

**(1)** 문제: 루프 안 SELECT(N+1 문제)로 항공편 수만큼 DB 왕복, 건수만 필요한데 SBOOK 전체 열 읽기, SFLIGHT도 SELECT *.
```abap
SELECT f~carrid, f~connid, f~fldate, COUNT( b~bookid ) AS bookings
  FROM sflight AS f
  LEFT OUTER JOIN sbook AS b
    ON  b~carrid = f~carrid
    AND b~connid = f~connid
    AND b~fldate = f~fldate
  WHERE f~carrid IN @s_carr
  GROUP BY f~carrid, f~connid, f~fldate
  INTO TABLE @DATA(lt_count).
```
**(2)** ① lt_flight가 비어 있으면 WHERE 조건이 무시되어 SBOOK **전체**를 읽는다 → `IF lt_flight IS NOT INITIAL.`로 감싼다. ② FOR ALL ENTRIES 결과는 중복 행이 제거되는데 선택 열에 키(BOOKID)가 없어, 같은 항공편에 같은 금액 예약이 여러 건이면 한 건만 남아 합계가 틀린다 → 테이블 키 전체(`bookid` 포함)를 선택한다.
```abap
IF lt_flight IS NOT INITIAL.
  SELECT carrid, connid, fldate, bookid, loccuram
    FROM sbook
    FOR ALL ENTRIES IN @lt_flight
    WHERE carrid = @lt_flight-carrid
      AND connid = @lt_flight-connid
      AND fldate = @lt_flight-fldate
    INTO TABLE @DATA(lt_amount).
ENDIF.
```
3대 함정: 빈 드라이버 테이블 = 전체 조회, 결과 중복 제거, 드라이버 테이블 중복은 미리 제거(SORT + DELETE ADJACENT DUPLICATES). 집계가 목적이면 JOIN + GROUP BY로 DB에서 계산하는 편이 낫다.
**(3)** ① `SELECT * ... ENDSELECT` + `CHECK`: 모든 열·행을 가져와 ABAP에서 거름 → 조건은 WHERE로, 필요한 열만(전송량 감소, 인덱스 사용) ② 루프 안 `SELECT SINGLE`: 예약 건수만큼 DB 왕복 → JOIN(또는 FOR ALL ENTRIES, 버퍼링된 SCARR이면 덜하지만) ③ 루프 안 `SORT`: 행 추가마다 전체 정렬 → 끝에서 한 번 또는 ORDER BY.
```abap
SELECT b~bookid, b~carrid, c~carrname
  FROM sbook AS b
  INNER JOIN scarr AS c ON c~carrid = b~carrid
  WHERE b~cancelled = @space
    AND b~fldate   >= @p_from
  ORDER BY b~bookid
  INTO TABLE @DATA(lt_out).
```
**(4)** ① **SELECT \***: 필요한 열(bookid, carrid, customid)만 ② **루프 안 SELECT SINGLE**: JOIN이나 FOR ALL ENTRIES(빈 테이블 확인·중복 제거 포함)로 한 번에 ③ **정렬 안 된 테이블에 BINARY SEARCH**: lt_carr는 ORDER BY 없이 읽어 정렬이 보장되지 않아 결과가 틀릴 수 있다 → `SORT lt_carr BY carrid` 또는 SORTED/HASHED ④ **sy-subrc 미확인**: READ 실패 시 ls_carr에 **이전 행의 값**이 남아 다른 항공사 이름이 들어가고, SELECT SINGLE 실패 시 lv_name에 이전 고객 이름이 남는다.
```abap
SELECT b~bookid, c~carrname, s~name AS custname
  FROM sbook AS b
  INNER JOIN scarr AS c ON c~carrid = b~carrid
  LEFT OUTER JOIN scustom AS s ON s~id = b~customid
  WHERE b~fldate >= @p_date
  INTO CORRESPONDING FIELDS OF TABLE @gt_out.
```
JOIN을 쓰면 DB가 한 번에 결합해 왕복 횟수와 ABAP 코드가 줄고, 고객이 없을 수 있으면 LEFT OUTER JOIN으로 예약 행을 잃지 않는다. 채점: 4개를 찾으면 만점(3점), 개당 0.75점.
**(5)**
```abap
SORT lt_spfli   BY carrid connid.
SORT lt_sflight BY carrid connid.

LOOP AT lt_spfli INTO DATA(ls_spfli).
  READ TABLE lt_sflight TRANSPORTING NO FIELDS
       WITH KEY carrid = ls_spfli-carrid
                connid = ls_spfli-connid
       BINARY SEARCH.
  IF sy-subrc <> 0.
    CONTINUE.
  ENDIF.

  LOOP AT lt_sflight INTO DATA(ls_sflight) FROM sy-tabix.
    IF ls_sflight-carrid <> ls_spfli-carrid
    OR ls_sflight-connid <> ls_spfli-connid.
      EXIT.
    ENDIF.
    " ls_spfli + ls_sflight 처리
  ENDLOOP.
ENDLOOP.
```
두 테이블을 같은 키로 정렬하고, 안쪽 루프를 일치하는 첫 행(BINARY SEARCH는 일치 행이 여러 개면 가장 작은 인덱스를 돌려준다)부터 시작해 키가 바뀌면 EXIT한다. 비교 횟수가 N×M에서 대략 N log M + M으로 준다. `LOOP AT lt_sflight ... WHERE carrid = ... AND connid = ...`는 STANDARD 테이블이면 매번 전체를 훑어 느리다. 대안으로 lt_sflight를 SORTED TABLE(키 carrid, connid)로 선언하면 WHERE 루프가 키로 최적화된다.
**(6)** ST05로 동일 SQL 반복(Identical Selects)을 찾고, 위처럼 DB 왕복 수와 전송량을 줄인 사례를 측정 전후 수치와 함께 말한다.

</details>

---

### B-043. 인덱스·테이블 버퍼링·ABAP SQL vs Native SQL [개념] ★★
<!-- src: MX-014, IB-115, CL-039, IB-119 -->
(1) SBOOK에 `CUSTOMID` 보조 인덱스가 있다. 이 인덱스를 효율적으로 쓰기 **가장 어려운** 조건은? ① `customid = @lv_id` ② `customid IN @lr_ids`(I EQ 단일 값 10개) ③ `customid <> @lv_id` ④ `customid = @lv_id AND class = 'C'`. 인덱스를 잘 못 쓰는 조건 유형을 더 쓰시오.
(2) DB 인덱스에 대해 옳지 **않은** 것은? ① 인덱스 앞쪽 필드부터 `=` 조건을 주면 효과적이다. ② `<>`, `NOT`은 범위 검색에 잘 쓰이지 않는다. ③ `LIKE '%ABC'`는 범위 검색이 어렵다. ④ 클라이언트 종속 테이블의 2차 인덱스는 보통 MANDT를 첫 필드로 둔다. ⑤ 2차 인덱스를 많이 만들수록 SELECT뿐 아니라 INSERT/UPDATE도 빨라진다.
(3) 실제 인덱스 사용 여부는 어디서 확인하는가? HANA 컬럼 스토어에서 2차 인덱스의 의미는?
(4) 테이블 버퍼링에 대해 옳지 **않은** 것을 **모두** 고르시오. ① Single Record 버퍼 테이블은 전체 키를 지정한 `SELECT SINGLE`일 때 버퍼에서 읽는다. ② `SELECT ... FOR UPDATE`는 버퍼링된 테이블이면 버퍼에서 읽는다. ③ Generic 버퍼 테이블에서 generic key 필드를 WHERE에 모두 지정하지 않으면 DB를 읽는다. ④ `BYPASSING BUFFER`는 항상 DB에서 읽는다. ⑤ 버퍼링은 수시로 변경되는 대용량 트랜잭션 테이블에 적합하다.
(5) Full 버퍼링의 대상, Native SQL과 버퍼, 버퍼 상태와 테이블별 통계 T-code를 쓰시오.
(6) ABAP SQL(Open SQL)과 Native SQL의 차이를 다섯 가지 쓰고, Native SQL 실행 방법 두 가지와 주 용도를 쓰시오. HANA 전용 로직의 권장 방식은?

<details><summary>정답·해설</summary>

**(1)** **③**. 인덱스는 "같다/범위 안"처럼 범위를 좁히는 조건에 쓰인다. `<>`/`NOT`은 거의 전체 범위라 옵티마이저가 보통 전체 스캔을 고른다. 같은 이유로 `LIKE '%abc'`(앞 와일드카드), 열에 함수를 씌운 조건, 서로 다른 열을 `OR`로 묶은 조건도 인덱스를 잘 못 쓴다. ①②는 같음 조건, ④는 인덱스 열 같음 조건에 다른 조건이 더해진 것이라 쓸 수 있다.
**(2)** **⑤**. 인덱스가 많으면 데이터 변경 때마다 모든 인덱스를 갱신해야 해 쓰기 성능이 떨어지고 저장 공간이 늘며, 너무 많으면 옵티마이저가 잘못 고를 수도 있다.
**(3)** 최종 판단은 DB 옵티마이저가 하므로 ST05의 Explain(실행 계획)으로 확인한다. HANA(컬럼 스토어)에서는 2차 인덱스가 필요한 경우가 훨씬 적다.
**(4)** **②, ⑤**. ① 맞다(레코드 단위, 전체 키 조건일 때만). ② 틀리다: FOR UPDATE는 DB 행 잠금이 필요해 항상 DB를 읽는다. ③ 맞다: 일반 키 영역 단위로 올리므로 영역을 특정할 수 없으면 우회한다. ④ 맞다. ⑤ 틀리다: 버퍼는 애플리케이션 서버마다 있고 변경 시 다른 서버 버퍼는 동기화 주기 동안 옛 값을 가질 수 있다. 작고 자주 읽고 거의 바뀌지 않는 테이블(커스터마이징, 코드 테이블)에 적합하다.
**(5)** Full 버퍼링은 테이블 전체를 한 번에 올린다(작은 테이블). Native SQL은 버퍼를 쓰지 않는다. 버퍼 상태 ST02, 테이블별 통계 ST10.
**(6)**

| 항목 | ABAP SQL | Native SQL |
|---|---|---|
| DB 독립성 | 어떤 DB에서도 같은 문법 | 특정 DB 문법(HANA SQL 등) |
| 문법 검사 | 컴파일 시 | 실행 시에야 오류 확인 |
| 클라이언트 처리 | 현재 클라이언트 자동 적용 | 직접 MANDT 조건 작성 |
| 테이블 버퍼 | 사용 | 사용 안 함 |
| 대상 | DDIC에 정의된 객체 | DB의 모든 객체(DDIC에 없는 테이블도) |

실행: `EXEC SQL ... ENDEXEC.`(obsolete), **ADBC**(`cl_sql_statement`, `cl_sql_connection`)로 동적 실행. 전송 후 다른 DB 시스템에서 깨질 수 있어, 주로 다른 DB 연결(DBCO에 정의한 보조 DB)에 접근할 때 쓴다. HANA 전용 로직은 AMDP가 권장된다.

</details>

---

### B-044. 대용량 처리: PACKAGE SIZE·커서·병렬 처리·느린 배치 분석·500만 건 리포트 [코드] ★★★
<!-- src: IB-116, IB-117, IB-118, IB-120 -->
수백만 건의 SBOOK을 1만 건씩 나눠 처리하는 두 방법이다.

```abap
DATA lt_pkg TYPE STANDARD TABLE OF sbook WITH EMPTY KEY.
" 방법 A
SELECT * FROM sbook
  WHERE fldate >= @p_from
  INTO TABLE @lt_pkg ____(a)____ 10000.
  PERFORM process USING lt_pkg.
____(b)____.
" 방법 B (처리 중 COMMIT WORK가 있어도 커서 유지)
DATA lv_cur TYPE cursor.
OPEN CURSOR ____(d)____ @lv_cur FOR
  SELECT * FROM sbook WHERE fldate >= @p_from.
DO.
  ____(c)____ @lv_cur INTO TABLE @lt_pkg PACKAGE SIZE 10000.
  IF sy-subrc <> 0.
    EXIT.
  ENDIF.
  PERFORM process USING lt_pkg.
  COMMIT WORK.
ENDDO.
CLOSE CURSOR @lv_cur.
```

(1) 빈칸 (a)~(d)를 채우시오.
(2) PACKAGE SIZE 루프에서 테이블이 어떻게 채워지는가(INTO vs APPENDING)? SELECT 루프 안에서 COMMIT WORK를 하면? 메모리 부족 덤프 이름은?
(3) 수백만 건 배치를 병렬로 나누는 방법 두 가지 이상과 설계 시 주의점을 쓰시오. aRFC 태스크의 실행 시간 제한은?
(4) 평소 20분 걸리던 운영 배치 잡이 2시간 넘게 걸린다. 운영을 방해하지 않고 원인을 찾는 절차를 쓰시오.
(5) VBAP 500만 건을 읽어 집계하는 리포트가 느리고 메모리 덤프도 난다. 개선 방안을 DB 접근, 메모리, 실행 방식 관점에서 다섯 가지 이상 쓰시오.

<details><summary>정답·해설</summary>

**(1)** (a) `PACKAGE SIZE` (b) `ENDSELECT` (c) `FETCH NEXT CURSOR` (d) `WITH HOLD`
**(2)** `INTO TABLE ... PACKAGE SIZE n`은 SELECT 루프가 되어 매번 n건씩 테이블을 **덮어쓴다**(APPENDING TABLE이면 누적). SELECT 루프 안에서 COMMIT WORK를 하면 DB 커서가 닫혀 오류가 나므로, 커밋이 필요하면 `OPEN CURSOR WITH HOLD`로 연 커서를 FETCH한다. 메모리 부족 덤프는 TSV_TNEW_PAGE_ALLOC_FAILED.
**(3)** ① **aRFC**: `CALL FUNCTION 'Z_PROCESS_PACKAGE' STARTING NEW TASK lv_task DESTINATION IN GROUP 'parallel_generators' ... CALLING on_end ON END OF TASK`로 패키지마다 dialog work process를 써서 동시 실행, `WAIT FOR ASYNCHRONOUS TASKS UNTIL ...`로 대기(서버 그룹 RZ12) ② **잡 분할**: 키 범위(회사코드·문서번호)별로 여러 배치 잡 동시 실행 ③ 프레임워크: SPTA(SPTA_PARA_PROCESS_START_2), bgRFC, 애플리케이션 잡의 병렬 옵션, `CL_ABAP_PARALLEL`. 주의점: 패키지끼리 같은 데이터를 건드려 잠금 충돌이 나지 않게 분할 키 설계, 가용 work process 수 확인(RESOURCE_FAILURE 처리), 패키지별 LUW·오류 처리와 재시작 가능성, 결과 수집, 시스템 부하. aRFC는 dialog work process를 쓰므로 각 태스크도 dialog 실행 시간 제한을 받는다. 패키지 크기는 수천~수만 건으로 적당히 잡는다.
**(4)** ① **SM37**: 잡 로그, 실행 시간 추이, 같은 시간대 다른 잡과 겹침, 변형(선택 조건) 변경 확인 ② **SM50/SM66**: 실행 중 work process가 어떤 프로그램·테이블(SQL)을 처리하는지, 대기(잠금, 순차 읽기) 상태인지 ③ **STAD**: DB 시간, CPU 시간, 대기 시간 비율로 DB 문제인지 ABAP 문제인지 구분 ④ 실행 중 짧게 **ST05**(해당 사용자·work process 한정) 또는 **ST12/SAT**(실행 중 프로세스 지정)로 비싼 SQL·반복 SQL·내부 테이블 병목 확인 ⑤ 원인 후보 검토: 데이터량 증가(특히 중첩 루프, 정렬 안 된 READ 같은 비선형 알고리즘), 최근 전송된 코드 변경, DB 통계·인덱스 문제, 잠금 대기(SM12), 자원 부족 ⑥ 테스트 시스템에서 재현·수정 후 전송. 면접관은 "추측하지 않고 측정한다"는 순서를 본다. 월말에만 느리면 데이터량·동시 실행 잡을 먼저 의심한다.
**(5)** ① 필요한 열만, 선택 조건(판매조직, 생성일)을 WHERE에 넣어 행 수 축소, 기본 키(VBELN, POSNR)나 적절한 인덱스를 쓰는지 확인 ② 집계는 DB에서: `SUM( ) ... GROUP BY` 또는 CDS 뷰(코드 푸시다운) ③ VBAK·고객 등은 JOIN으로 한 번에, 루프 안 SELECT 금지 ④ 상세 데이터가 꼭 필요하면 `PACKAGE SIZE`/커서로 나눠 메모리 제한 ⑤ 룩업은 SORTED/HASHED, LOOP는 ASSIGNING으로 복사 줄이기 ⑥ 대화형 대신 백그라운드 잡, 필요하면 병렬 처리 ⑦ ST05/SAT로 개선 전후 측정. S/4HANA라면 표준 CDS 뷰(I_SalesDocumentItem 등)를 읽는 방식이 더 적합할 수 있다.

</details>

---

### B-045. 성능 분석 도구: ST05·SAT·ST12·SQLM·모니터 T-code와 SQL 원칙 [개념] ★★
<!-- src: CL-037, TC-026, TC-010, TC-009, TC-029 -->
(1) ST05, SAT, ST12가 각각 무엇을 분석하는지 쓰고 "느린 리포트" 분석 순서를 설명하시오.
(2) ST05로 SQL 성능을 분석하는 순서, 켤 수 있는 트레이스 종류(네 가지 이상), 결과 목록에서 확인할 것, 주의점을 쓰시오.
(3) "루프 안에서 같은 조건의 SELECT SINGLE이 수천 번 반복되는지" 확인하는 데 가장 적합한 도구는? ① SE30/SAT ② ST05 SQL Trace(Identical Selects / Summary) ③ ST22 ④ SM50 ⑤ SLIN. 나머지 도구의 용도도 쓰시오.
(4) 2차 인덱스를 만들기 전 고려할 점과 단점, ABAP SQL 성능 원칙 네 가지 이상을 쓰시오. S/4HANA의 기본 원칙은?
(5) 다음 표에 T-code를 쓰시오.

| 번호 | 기능 | T-code |
|---|---|---|
| 1 | Code Inspector | |
| 2 | ABAP Test Cockpit | |
| 3 | Extended Program Check | |
| 4 | ABAP Runtime Analysis(구 SE30) | |
| 5 | Performance Trace | |
| 6 | Single Transaction Analysis(ST05+SAT) | |
| 7 | SQL Monitor(운영계 SQL 누적 통계) | |
| 8 | SQL Performance Tuning Worklist | |
| 9 | SAP 버퍼 사용률·스왑(Tune Summary) | |
| 10 | 워크로드 분석(트랜잭션별 응답 시간) | |
| 11 | DB 성능 모니터 | |
| 12 | OS 모니터(CPU, 메모리, 디스크) | |
| 13 | 대화 단계별 통계 레코드 | |
| 14 | DB 공간·테이블 크기·누락 인덱스 | |
| 15 | ICM(HTTP 처리) 모니터 | |

(6) SAT와 ST05의 선택 기준, SQLM의 용도, ATC가 제공하는 검사를 쓰시오.

<details><summary>정답·해설</summary>

**(1)** **ST05**(Performance Trace): SQL 트레이스(실행 SQL, 시간, 건수, 실행 계획), 버퍼·Enqueue·RFC·HTTP 트레이스, Summarized/Identical SELECT로 반복 SELECT 찾기. **SAT**(Runtime Analysis, 구 SE30): ABAP 문장·메서드별 실행 시간과 호출 계층, Hit List, ABAP 대 DB 시간 비율. **ST12**: SAT와 ST05를 묶어 단일 트랜잭션 분석. 순서: STAD/ST03N으로 DB 시간과 ABAP 시간 비중 확인 → DB 시간이 크면 ST05로 비싼 SQL·실행 계획 → ABAP 시간이 크면 SAT로 비싼 루프·내부 테이블 처리 → 수정 후 재측정.
**(2)** ① 트레이스 종류 선택 후 Activate Trace(필요하면 사용자 지정) ② 다른 세션에서 프로그램 실행 ③ Deactivate Trace ④ Display Trace(기간·사용자 필터). 종류: SQL, Enqueue, RFC, Table Buffer, HTTP(그 밖에 Stack Trace 옵션). 확인: 실행 시간이 긴 문장, 반환 건수, 동일 문장 반복(Identical Selects), 인덱스 사용 여부(Explain), 버퍼 미사용, 루프 안 SELECT. 트레이스는 서버 단위로 기록되므로 사용자 필터를 걸고, 끝나면 반드시 끈다(켜 두면 성능 저하).
**(3)** **②**. Identical Selects로 똑같은 문장의 실행 횟수가 바로 보이고, Structure-identical statement summary로 문장별 횟수·시간을 합산한다. ① SAT도 DB 시간 비중은 보여 주지만 SQL 문장 단위는 ST05가 정확하다. ③ 덤프 분석 ④ 실행 중 work process 확인(오래 도는 프로그램의 현재 위치) ⑤ 정적 문법·규칙 검사.
**(4)** 고려: WHERE에 자주 쓰이고 선택도가 높은(결과가 적은) 필드 조합인지, 필드 순서(앞쪽 필드가 조건에 있어야 효율적), 기존 인덱스로 해결되지 않는지. 단점: INSERT/UPDATE/DELETE 때 인덱스도 갱신해 쓰기 성능 저하, 저장 공간, 너무 많으면 옵티마이저 오선택. HANA 컬럼 스토어에서는 필요한 경우가 적다. 인덱스는 SE11 Indexes에서 만들고 시스템별로 DB 생성 여부를 정할 수 있다. 원칙: 필요한 열만(SELECT * 지양), WHERE로 행 줄이기, 루프 안 SELECT 금지(JOIN·FOR ALL ENTRIES·한 번에 읽고 내부 테이블 검색), 집계·정렬은 DB에서(SUM, COUNT, GROUP BY), 작은 커스터마이징 테이블은 버퍼링, 키 필드로 접근. S/4HANA 기본 원칙은 "코드를 HANA로 내려라(Code-to-Data)".
**(5)** 1 SCI, 2 ATC, 3 SLIN, 4 SAT, 5 ST05, 6 ST12, 7 SQLM, 8 SWLT, 9 ST02, 10 ST03N(ST03), 11 ST04, 12 ST06(OS07N), 13 STAD, 14 DB02, 15 SMICM. 9~15는 Basis 관점 모니터지만 ST03N/STAD의 응답 시간 분해(CPU, DB, Wait, Roll)는 개발자도 읽을 줄 알아야 한다.
**(6)** SAT는 ABAP 처리 시간(메서드·서브루틴별 gross/net), ST05는 DB 접근. DB 시간이 작은데 느리면 SAT, SELECT가 많으면 ST05. SQLM은 운영계에서 상시 가볍게 수집해 간헐적 문제를 찾고 문제 SQL을 ST05로 상세 분석한다. ATC는 SCI 검사를 포함하며 HANA 준비 검사, ABAP Cloud 준비 검사, 전송 해제 시 자동 검사를 제공한다.

</details>

---

## 디버깅·덤프·개발 도구

### B-046. 디버깅: 중단점 종류·감시점·팝업/업데이트/배치/Fiori 디버깅·값 변경 [개념] ★★
<!-- src: IB-121, TC-014, IB-122, IB-123, TC-015, IB-129 -->
(1) ABAP 중단점 종류(정적, 세션, 외부, 디버거)를 설정 방법과 유효 범위로 비교하고, 그 밖의 중단점 유형과 감시점(watchpoint)을 설명하시오.
(2) Fiori 앱에서 버튼을 눌렀을 때 실행되는 OData/RAP 백엔드 코드를 디버깅하는 옳은 방법은? ① SAP GUI에서 `/h` 입력 후 브라우저 버튼 클릭 ② 세션 중단점 설정 ③ 요청을 보내는 사용자로 외부(external/user) 중단점 설정 ④ SM37에서 JDBG ⑤ SE30 측정 후 결과에서 코드 확인. 이유는?
(3) 옳지 **않은** 것을 고르시오. ① 팝업에서는 `/h` 명령을 담은 SAP GUI 바로가기 파일을 팝업 위에 끌어다 놓아 디버거를 켤 수 있다. ② 업데이트 모듈을 디버깅하려면 Update Debugging을 켜야 한다. ③ `/hs`는 시스템 프로그램까지 디버깅한다. ④ 일반 디버깅 중 COMMIT WORK를 지나면 설정 없이도 업데이트 모듈로 디버거가 자동으로 따라 들어간다.
(4) 다음 상황의 디버거 시작 방법을 쓰시오. ㉠ 팝업이 떠 있어 `/h`를 입력할 수 없음(바로가기 파일 내용 포함) ㉡ 이미 끝난(또는 예정된) 백그라운드 잡을 같은 조건으로 ㉢ 지금 실행 중인 백그라운드 잡 ㉣ `IN UPDATE TASK` 업데이트 FM ㉤ `IN BACKGROUND TASK` tRFC
(5) ㉡ 방식의 주의점 두 가지와, 재현용 무한 루프 기법을 쓰시오.
(6) 디버거에서 값을 바꾸는 것에 대해 옳은 것을 **모두** 고르시오. ① 디버그 권한 외에 변경 권한(S_DEVELOP, OBJTYPE DEBUG, ACTVT 02)이 필요하다. ② 값 변경 기록은 시스템 로그(SM21)에 남는다. ③ 운영 시스템에서도 결과가 같으면 디버거로 데이터를 고치는 것이 권장된다. ④ `sy-subrc` 같은 시스템 필드도 바꿔 분기를 테스트할 수 있다.

<details><summary>정답·해설</summary>

**(1)**

| 종류 | 설정 | 유효 범위 |
|---|---|---|
| 정적(Static) | 코드에 `BREAK-POINT.` 또는 `BREAK user.` | 코드가 있는 동안 항상(전자는 모든 사용자, 후자는 해당 사용자) |
| 세션(Session) | 편집기에서 설정 | 현재 SAP GUI 로그온 세션(같은 로그온의 모든 창) |
| 외부(External/User) | 편집기·ADT에서 설정 | 해당 사용자의 모든 세션, HTTP/RFC처럼 GUI 밖에서 들어온 요청 포함. 일정 시간(보통 2시간) 유효 |
| 디버거 중단점 | 디버거 안에서 설정 | 그 디버깅 세션 동안만 |

그 밖에 문장(MESSAGE, SELECT 등)·FM·메서드·예외 기준 중단점, 조건부 중단점이 있다. 감시점은 변수 값이 **바뀔 때**(또는 조건이 참이 될 때) 멈추게 하는 기능으로, 어디서 값이 바뀌는지 모를 때 쓰며 전역·지역 변수, 객체 속성에도 걸 수 있다. 운영 코드에 정적 중단점을 남기면 안 된다(ATC/SLIN 경고).
**(2)** **③**. HTTP/RFC 요청은 SAP GUI 세션과 다른 세션에서 실행되므로 외부 중단점(ADT의 중단점은 기본이 외부, SAP GUI에서는 External Breakpoint)이 필요하고, 그 사용자 이름으로 요청이 들어와야 걸린다. ① `/h`와 ② 세션 중단점은 GUI 세션 전용, ④ 백그라운드 잡 디버깅, ⑤ 측정 도구다.
**(3)** **④**. 업데이트 모듈은 COMMIT 후 별도 업데이트 work process에서 실행되므로 Update Debugging을 켜야 새 디버거 창이 열린다.
**(4)** ㉠ 내용이 `[FUNCTION] Command=/H Title=Debugger Type=SystemCommand`인 텍스트 파일(SAP GUI 바로가기)을 만들어 팝업 위로 드래그 앤 드롭. ㉡ **SM37**에서 잡을 선택하고 명령 필드에 **JDBG** 입력 → 같은 잡 스텝(프로그램 + 변형)이 대화 모드에서 디버거와 함께 다시 실행. ㉢ **SM50**(또는 SM66)에서 BTC work process 선택 → Program/Session → Program → Debugging으로 실행 중 프로세스에 디버거를 붙임. ㉣ 디버거 Settings에서 Update Debugging을 켜고 COMMIT WORK까지 진행하면 업데이트 태스크에서 새 디버거가 열림. ㉤ 디버거 설정의 "tRFC (In Background Task): Block Sending"(tRFC Debugging)을 켜고 SM58에서 처리.
**(5)** JDBG는 실제로 실행되므로 데이터 변경에 주의해야 하고, `sy-batch`가 공백일 수 있어 배치 전용 분기가 다르게 동작할 수 있다. 재현용으로 무한 루프(`WHILE lv_x IS INITIAL. ENDWHILE.`)를 테스트 시스템에만 넣고 SM50으로 붙는 방법도 쓴다.
**(6)** **①, ②, ④**. ③ 운영 데이터를 디버거로 고치는 것은 감사·통제 위반이며 업무 로직(검사, 변경 문서, 후속 처리)을 건너뛰어 정합성을 깨뜨린다. 데이터 수정은 표준 트랜잭션이나 승인된 수정 프로그램으로 한다. 디버깅 권한 자체는 ACTVT 03.

</details>

---

### B-047. 메시지 출처 찾기·체크포인트 그룹·편집기 단축키·ADT 전용 객체 [개념] ★★
<!-- src: IB-128, IB-127, TC-013, TC-016 -->
(1) 사용자가 VF03에서 알 수 없는 오류 메시지가 뜬다고 한다. 메시지를 내는 코드 위치를 찾아 원인을 분석하는 순서를 쓰시오. 운영에서 재현이 어려우면?
(2) 운영에는 영향이 없고 필요할 때만 켜는 검사·중단점·로그를 체크포인트 그룹 ZIB_CHK로 넣는다. 빈칸을 채우고 그룹을 만들고 켜는 트랜잭션을 쓰시오.
```abap
ASSERT ID zib_chk ____(a)____ lv_total >= 0.
____(b)____ ID zib_chk.
____(c)____ ID zib_chk SUBKEY ls_flight-carrid
            FIELDS ls_flight-price ls_flight-seatsocc.
```
(3) (2)의 그룹이 비활성/활성일 때 각 문장의 동작과, ID 없는 `ASSERT`의 동작을 쓰시오.
(4) SAP GUI ABAP Editor와 새 디버거의 키를 쓰시오: ① 문법 검사 ② 활성화 ③ 실행 ④ Pretty Printer ⑤ Single step ⑥ Execute ⑦ Return ⑧ Continue. ADT에서의 같은 키와 F3, F2, Ctrl+Shift+A, Ctrl+1, F9, Ctrl+Shift+F10의 기능은?
(5) SAP GUI(SE80 등)에서 만들거나 편집할 수 없고 ADT에서만 편집하는 객체를 다섯 가지 이상 쓰시오. SAP BTP ABAP Environment에서 SAP GUI 대신 쓰는 것은?

<details><summary>정답·해설</summary>

**(1)** ① 상태 표시줄 메시지 더블클릭 → Technical Information에서 메시지 클래스·번호(예: VF 123), 프로그램·화면 확인 ② SE91에서 Where-Used List(동적 호출이면 안 잡힐 수 있음) ③ `/h`로 디버거를 켜고 **Breakpoint at Statement MESSAGE**(또는 Breakpoint at Message: 클래스+번호)를 건 뒤 재현 → 멈추면 Call Stack으로 어느 Exit/BAdI/출력 루틴에서 왔는지 확인 ④ Z 코드(Enhancement, User Exit, 출력 프로그램)면 조건과 데이터를 확인해 수정, 표준이면 SAP Note 검색(SNOTE) ⑤ 데이터 문제면 관련 테이블(VBRK/VBRP)과 커스터마이징 확인. 재현이 어려우면 같은 데이터로 품질 시스템에서 재현하거나 SAT/ST05 트레이스를 쓴다.
**(2)** (a) `CONDITION` (b) `BREAK-POINT` (c) `LOG-POINT`. 트랜잭션 **SAAB**(그룹 생성, 사용자·서버별 활성화, 로그 조회).
**(3)** 비활성이면 ID가 붙은 문장은 아무 일도 하지 않는다. 활성화하면 ASSERT는 조건이 거짓일 때 덤프/로그/중단, BREAK-POINT는 디버거 진입, LOG-POINT는 필드 값을 SAAB 로그에 남긴다. ID 없는 `ASSERT`는 항상 활성이라 조건이 거짓이면 바로 덤프(ASSERTION_FAILED)가 난다.
**(4)** ① Ctrl+F2 ② Ctrl+F3 ③ F8 ④ Shift+F1 ⑤ F5 ⑥ F6 ⑦ F7 ⑧ F8. ADT에서도 Ctrl+F2(검사), Ctrl+F3(활성화), Shift+F1(포맷)이 같다. ADT의 F3은 정의로 이동, F2는 요소 정보, Ctrl+Shift+A는 객체 열기, Ctrl+1은 Quick Fix, F9는 콘솔 애플리케이션(`IF_OO_ADT_CLASSRUN`) 실행, Ctrl+Shift+F10은 ABAP Unit 실행.
**(5)** CDS 데이터 정의(DDLS: view entity, projection view, table function, custom entity, abstract entity), CDS 메타데이터 확장(DDLX), CDS 접근 제어(DCLS), Behavior Definition(BDEF), Service Definition(SRVD), Service Binding(SRVB), AMDP 메서드 본문(SQLScript), 그 밖에 Business Service 관련 객체와 ABAP for Cloud Development 언어 버전 클래스. DDIC 기반 CDS 뷰도 SE11에서는 생성된 SQL 뷰 조회만 되고 원본(DDL) 편집은 ADT에서만 한다. BTP ABAP Environment에는 SAP GUI가 없으므로 ADT와 관리용 Fiori 앱(Maintain Business Users, Communication Arrangements 등)을 쓰고, 트랜잭션 대신 F9(콘솔 실행), ABAP Unit, ATC를 쓴다.

</details>

---

### B-048. 런타임 오류(ST22) 유형과 정적 검사(SLIN·SCI·ATC) [개념] ★★
<!-- src: IB-124, TC-025, IB-126 -->
(1) 다음 런타임 오류의 원인을 쓰시오: CONVT_NO_NUMBER, COMPUTE_INT_ZERODIVIDE, ITAB_LINE_NOT_FOUND, TIME_OUT, SAPSQL_ARRAY_INSERT_DUPREC, MESSAGE_TYPE_X, OBJECTS_OBJREF_NOT_ASSIGNED, GETWA_NOT_ASSIGNED, TSV_TNEW_PAGE_ALLOC_FAILED, DYNPRO_SEND_IN_BACKGROUND, CALL_FUNCTION_NOT_FOUND, UNCAUGHT_EXCEPTION, ITAB_DUPLICATE_KEY
(2) 옳지 **않은** 연결은? ① TIME_OUT – dialog step이 허용 실행 시간을 넘김 ② TSV_TNEW_PAGE_ALLOC_FAILED – 내부 테이블 메모리 확보 실패 ③ CONVT_NO_NUMBER – 숫자로 해석할 수 없는 문자열을 숫자로 변환 ④ ITAB_DUPLICATE_KEY – unique 키 내부 테이블에 같은 키 행 추가 ⑤ MESSAGE_TYPE_X – 0으로 나눔
(3) (1) 중 TRY ... CATCH로 잡을 수 있는 것과 대응 예외 클래스(1, 2, 5, 7), 잡을 수 없는 것을 쓰시오. 단일 행 `INSERT dbtab FROM wa`의 키 중복은?
(4) ST22에서 볼 수 있는 정보와 덤프 보관 방법을 쓰시오.
(5) SLIN, SCI, ATC의 차이를 쓰시오.
(6) 검사 경고를 정당하게 억제하는 방법과 ATC의 실무 활용을 쓰시오.

<details><summary>정답·해설</summary>

**(1)** CONVT_NO_NUMBER: 숫자로 변환할 수 없는 문자열을 숫자 타입에 대입('ABC' → i). COMPUTE_INT_ZERODIVIDE: 정수를 0으로 나눔. ITAB_LINE_NOT_FOUND: 테이블 식 `itab[ ... ]`으로 찾은 행이 없음(CX_SY_ITAB_LINE_NOT_FOUND 미처리). TIME_OUT: 대화 단계 최대 실행 시간 초과. SAPSQL_ARRAY_INSERT_DUPREC: `INSERT dbtab FROM TABLE itab`에서 키 중복 행 삽입. MESSAGE_TYPE_X: `MESSAGE ... TYPE 'X'`로 의도적 종료. OBJECTS_OBJREF_NOT_ASSIGNED: 초기(NULL) 참조 변수로 메서드 호출·속성 접근. GETWA_NOT_ASSIGNED: 할당되지 않은 필드 심볼 사용. TSV_TNEW_PAGE_ALLOC_FAILED: 내부 테이블 메모리 확장 실패. DYNPRO_SEND_IN_BACKGROUND: 백그라운드 실행 중 화면(dynpro, 팝업) 전송. CALL_FUNCTION_NOT_FOUND: 존재하지 않는(또는 비활성) FM 호출. UNCAUGHT_EXCEPTION: TRY/CATCH도 RAISING 선언도 없이 전파된 클래스 기반 예외. ITAB_DUPLICATE_KEY: unique 키 내부 테이블에 같은 키 행을 넣음(예: 정렬 unique 테이블에 APPEND).
**(2)** **⑤**. 0으로 나누기는 COMPUTE_INT_ZERODIVIDE(CX_SY_ZERODIVIDE)다.
**(3)** 대부분 대응 예외 클래스가 있어 잡을 수 있다: CONVT_NO_NUMBER → CX_SY_CONVERSION_NO_NUMBER, COMPUTE_INT_ZERODIVIDE → CX_SY_ZERODIVIDE, SAPSQL_ARRAY_INSERT_DUPREC → CX_SY_OPEN_SQL_DB, OBJECTS_OBJREF_NOT_ASSIGNED → CX_SY_REF_IS_INITIAL. MESSAGE_TYPE_X, TSV_TNEW_PAGE_ALLOC_FAILED, TIME_OUT은 잡을 수 없다. 단일 행 `INSERT dbtab FROM wa`의 키 중복은 덤프가 아니라 sy-subrc = 4다.
**(4)** 오류 위치(프로그램·줄), 호출 스택, 변수 값, 원인 설명이 나오고 "Debugger" 버튼으로 당시 상태를 볼 수 있다. 덤프는 일정 기간 후 삭제되므로 보관하려면 Keep 표시를 한다.
**(5)** **SLIN(Extended Program Check)**: 프로그램 하나에 대해 문법 검사보다 넓은 정적 검사(도달 불가 코드, 미사용 변수, PERFORM/CALL FUNCTION 인터페이스 불일치, 메시지·텍스트 요소 누락). **SCI(Code Inspector)**: 검사 변형(Check Variant)으로 여러 객체(패키지, 요청)를 성능·보안·이름 규칙·견고성 기준으로 검사, SLIN 검사도 포함 가능. **ATC**: SCI 검사를 실행하는 중앙 품질 관리 프레임워크. 전송 요청 릴리스 시 자동 검사, 중앙 검사 시스템의 원격 검사, 결과 관리·예외(Exemption) 승인 흐름, S/4HANA readiness 검사, ABAP Cloud 준수 검사.
**(6)** 코드에 pragma(`##NEEDED`, `##NO_TEXT` 등)나 pseudo comment(`"#EC CI_NOWHERE` 등)를 붙이거나 ATC에서 예외를 신청·승인받는다. 실무에서는 "ATC 우선순위 1·2 오류가 있으면 전송 불가"처럼 품질 게이트로 쓴다.

</details>

---

### B-049. 운영 모니터링 T-code와 애플리케이션 로그(BAL) [개념] ★
<!-- src: TC-019, IB-125, MX-030, TC-020, TC-028, TC-023 -->
(1) 다음 T-code의 기능을 쓰시오: SM12, SM13, SM21, SM36, SM37, SM50, SM66, SM04, ST22, SM35, SM51, AL08, SM02
(2) 다음 상황에서 가장 먼저 볼 T-code를 쓰시오. ㉠ 퇴근한 사용자의 잠금 때문에 다른 사용자가 저장하지 못함 ㉡ 저장 메시지는 떴는데 DB에 반영되지 않음 / "Express 메일: 업데이트가 중단되었습니다" ㉢ 시스템 오류·경고 이력 ㉣ 지금 실행 중인 work process와 프로그램(인스턴스/전체) ㉤ 실패한 tRFC ㉥ BAL 로그 ㉦ 마지막 권한 검사 실패 ㉧ 서버 파일 목록 ㉨ 야간 배치 Canceled 로그 ㉩ 오류 화면 없이 짧은 덤프 ㉪ 프린터로 안 나온 출력 ㉫ Batch Input 세션 오류 트랜잭션
(3) 상황 (가) 리포트의 느린 SQL 문 확인 (나) 어젯밤 잡 런타임 오류의 원인 코드 위치 (다) 저장 메시지 후 데이터 없음 (라) "다른 사용자가 처리 중" 메시지에 맞는 짝은? ① ST05 – ST22 – SM13 – SM12 ② SAT – SM37 – SM12 – SM13 ③ ST05 – SM21 – SM50 – SM12 ④ ST22 – ST05 – SM13 – SM50
(4) 짝이 옳지 **않은** 것은? ① SM51 – 애플리케이션 서버 목록 ② SM66 – 전체 시스템 work process ③ AL08 – 모든 서버의 로그온 사용자 ④ SM02 – 시스템 메시지 작성 ⑤ SM04 – 백그라운드 작업 정의
(5) SM12에서 잠금을 지울 때 주의점, Express 메일이 오는 원리를 쓰시오.
(6) BAL의 정의/조회/삭제 T-code, 클래식 ABAP에서 로그를 만들어 저장·표시하는 FM, ABAP Cloud API를 쓰시오. 배치 프로그램에서 BAL을 쓰는 이점은?

<details><summary>정답·해설</summary>

**(1)** SM12: 잠금 항목 조회·삭제. SM13: 업데이트 요청 조회, 실패한 업데이트 재처리(오류 상태 ERR). SM21: 시스템 로그. SM36: 백그라운드 작업 정의(스케줄). SM37: 작업 조회(상태·로그·스풀). SM50: 현재 서버 work process. SM66: 시스템 전체 work process. SM04: 현재 서버 로그온 사용자(세션 수, 사용 중 트랜잭션). ST22: 런타임 오류(덤프) 분석. SM35: Batch Input 세션 조회·처리. SM51: 애플리케이션 서버(인스턴스) 목록. AL08: 모든 서버의 로그온 사용자. SM02: 시스템 메시지(전체 사용자 공지, 화면 팝업). 그 밖에 SP01(스풀), SMQ1/SMQ2(qRFC 큐), ST01/STAUTHTRACE(권한 트레이스), STAD(통계), ST05(SQL 트레이스)가 자주 나온다.
**(2)** ㉠ SM12 ㉡ SM13 ㉢ SM21 ㉣ SM50 / SM66 ㉤ SM58 ㉥ SLG1 ㉦ SU53 ㉧ AL11 ㉨ SM37 ㉩ ST22 ㉪ SP01 ㉫ SM35
**(3)** **①**. ST05는 SQL·버퍼·RFC 추적(실행 계획 포함), ST22는 덤프 분석, SM13은 업데이트 요청·오류, SM12는 잠금 조회·삭제. SAT는 ABAP 실행 시간, SM37은 작업 목록·로그(원인 코드 위치는 ST22), SM21은 시스템 로그, SM50은 work process 현황.
**(4)** **⑤**. SM04는 현재 서버 사용자 목록이고 작업 정의는 SM36이다.
**(5)** SM12 잠금 삭제는 잠금을 건 프로그램이 정말 비정상 종료된 경우에만 해야 한다. 실행 중인 처리의 잠금을 지우면 데이터 불일치가 생긴다. V1 업데이트 모듈이 실패하면 업데이트 레코드가 Error 상태로 남고 사용자에게 Express 메일이 간다. SM13에서 원인을 확인하고 ST22에서 해당 덤프를 함께 본다.
**(6)** SLG0: Object/Subobject 정의, SLG1: 조회(Object/Subobject로 검색), SLG2: 만료 로그 삭제. FM: `BAL_LOG_CREATE`(로그 핸들) → `BAL_LOG_MSG_ADD`(메시지 추가) → `BAL_DB_SAVE`(저장), 표시는 `BAL_DSP_LOG_DISPLAY`. ABAP Cloud: `CL_BALI_LOG`(로그), `CL_BALI_MESSAGE_SETTER`/`CL_BALI_FREE_TEXT_SETTER`(항목), `CL_BALI_LOG_DB`(저장), Application Log API(`IF_BALI_*`). 배치는 WRITE 리스트 대신 BAL에 결과를 남기면 SLG1에서 Object·날짜·사용자로 검색할 수 있다.

</details>

---

## 배치 잡 · 권한 · 전송 · 운영

### B-050. 백그라운드 잡: 상태·시작 조건·JOB_OPEN/CLOSE·배치 제약·이벤트·스풀 PDF [코드] ★★
<!-- src: IB-130, TC-021, TC-022, IB-131, IB-132, MX-031, IB-133, IB-134 -->
리포트 ZIB_FLIGHT_LIST를 배치 잡으로 즉시 실행하도록 등록하는 코드다.

```abap
DATA: lv_jobname  TYPE tbtcjob-jobname VALUE 'ZIB_FLIGHT_JOB',
      lv_jobcount TYPE tbtcjob-jobcount.
CALL FUNCTION '____(a)____'
  EXPORTING jobname  = lv_jobname
  IMPORTING jobcount = lv_jobcount
  EXCEPTIONS OTHERS  = 1.
SUBMIT zib_flight_list
  WITH p_carr = 'LH'
  VIA ____(b)____ lv_jobname NUMBER lv_jobcount
  AND RETURN.
CALL FUNCTION '____(c)____'
  EXPORTING jobcount    = lv_jobcount
            jobname     = lv_jobname
            ____(d)____ = 'X'
  EXCEPTIONS OTHERS     = 1.
```

(1) 잡 상태 Scheduled, Released, Ready, Active, Finished, Canceled의 의미를 쓰시오. 다음 중 옳지 **않은** 것을 모두 고르시오. ① Scheduled는 시작 조건이 지정되어 실행을 기다리는 상태, Released는 시작 조건 없이 저장만 된 상태다. ② Ready는 시작 시간이 되어 빈 배치 work process를 기다리는 상태다. ③ Canceled는 사용자가 실행 전에 잡을 삭제했다는 뜻이다. ④ 잡 클래스 A/B/C는 우선순위다.
(2) SM36에서 Step으로 지정할 수 있는 것 세 가지와 시작 조건 종류(다섯 가지 이상, 주기 설정 포함)를 쓰시오. 잡 정보가 저장되는 테이블은?
(3) 빈칸 (a)~(d)를 채우고, 다른 시작 조건 파라미터와 시작 조건 없이 JOB_CLOSE하면 어떻게 되는지 쓰시오.
(4) 배치 잡으로 실행되는 리포트에 대해 옳지 **않은** 것은? ① 실행 중 `sy-batch`는 'X'다. ② 유형 I, S 메시지는 잡 로그에 기록되고 처리는 계속된다. ③ 유형 E 메시지를 보내면 잡이 취소된다. ④ WRITE 리스트는 스풀 요청으로 저장된다. ⑤ GUI_DOWNLOAD로 사용자 PC에 결과 파일을 저장할 수 있다. 결과를 남기는 대안과 화면을 보낼 때의 덤프는?
(5) 외부 시스템이 파일을 서버에 올린 직후에만 처리 잡이 실행되게 하려 한다. 백그라운드 이벤트 정의, 잡 설정, 이벤트 발생 방법(세 가지)을 쓰시오.
(6) 스풀 요청과 출력 요청의 차이, 리스트 스풀을 PDF로 바꾸는 방법, 관련 트랜잭션을 쓰시오. 프로그램 안에서 리스트를 스풀로 보내는 방법과 스풀 번호 필드, 스풀 정보 테이블은?

<details><summary>정답·해설</summary>

**(1)** **Scheduled**: 정의됐지만 시작 조건이 없거나 릴리스되지 않아 실행 대상이 아님. **Released**: 시작 조건이 지정되어 그 시점을 기다림. **Ready**: 시작 시점이 되어 빈 배치 work process를 기다림. **Active**: 실행 중. **Finished**: 정상 종료. **Canceled**: 실행 중 비정상 종료(E/A 메시지, 런타임 오류, 관리자 강제 종료). 옳지 않은 것은 **①, ③**(①은 반대로 설명했고, 삭제된 잡은 목록에 나오지 않는다). Canceled는 Job Log의 마지막 메시지를 보고 덤프는 ST22에서 찾는다.
**(2)** Step: ABAP 프로그램(+변형), 외부 명령(External command, SM69에 정의), 외부 프로그램. 시작 조건: Immediate, Date/Time, After job(선행 잡 종료 후), After event(SM62 이벤트, SM64 또는 `BP_EVENT_RAISE`로 발생), At operation mode, 주기 설정(Periodic job: 시간·일·주·월 반복). 잡 헤더/상태는 TBTCO, 스텝은 TBTCP.
**(3)** (a) `JOB_OPEN` (b) `JOB` (c) `JOB_CLOSE` (d) `strtimmed`. JOB_OPEN으로 잡 생성(번호 받음) → `SUBMIT ... VIA JOB ... NUMBER ...`로 스텝 추가(여러 번 가능) → JOB_CLOSE로 시작 조건을 주어 릴리스. 다른 시작 조건: `sdlstrtdt`/`sdlstrttm`(날짜·시간), `event_id`(이벤트), `pred_jobname`(선행 잡). 시작 조건 없이 JOB_CLOSE하면 Scheduled 상태로 남는다.
**(4)** **⑤**. 배치에는 SAP GUI(프레젠테이션 서버)가 없어 프런트엔드 파일 처리(`GUI_DOWNLOAD`, `cl_gui_frontend_services`)와 대화 상자(POPUP 함수)를 쓸 수 없다. 결과는 서버 파일(`OPEN DATASET ... FOR OUTPUT`/`TRANSFER`/`CLOSE DATASET`, AL11 확인), 메일 첨부(CL_BCS), 스풀 등으로 남기고 `IF sy-batch = abap_true.`로 분기한다. 백그라운드에서 화면을 보내면 `DYNPRO_SEND_IN_BACKGROUND` 덤프가 난다.
**(5)** ① **SM62**에서 사용자 이벤트(예: ZIB_FILE_ARRIVED) 정의 ② SM36에서 시작 조건을 "After event" = ZIB_FILE_ARRIVED로 지정(반복하려면 Periodic job 체크) ③ 발생: ABAP에서 `CALL FUNCTION 'BP_EVENT_RAISE' EXPORTING eventid = 'ZIB_FILE_ARRIVED' eventparm = ...`, OS에서 `sapevt ZIB_FILE_ARRIVED`(외부 스케줄러·스크립트), SM64에서 수동 발생(테스트). 시간 기반 폴링보다 자원 낭비와 지연이 적고, 이벤트 파라미터로 잡을 구분할 수 있다.
**(6)** 스풀 요청: 출력할 데이터 자체(리스트·OTF)를 시스템에 저장한 것. 출력 요청: 스풀 요청을 특정 장치로 실제로 보내는 작업(한 스풀을 여러 번 출력하면 출력 요청이 여러 개). PDF: 프로그램 **RSTXPDFT4**(스풀 번호 → PDF 다운로드), 함수 **CONVERT_ABAPSPOOLJOB_2_PDF**(리스트 스풀) / **CONVERT_OTFSPOOLJOB_2_PDF**(SAPscript·SmartForms OTF 스풀), 결과를 CL_BCS로 메일 발송하기도 한다. 트랜잭션: SP01(스풀 조회·관리), SP02(내 스풀), SPAD(출력 장치·스풀 관리). 프로그램에서는 `NEW-PAGE PRINT ON PARAMETERS ... NO DIALOG`(GET_PRINT_PARAMETERS로 파라미터 생성)로 스풀에 보내고 번호는 `sy-spono`, 스풀 정보는 TSP01.

</details>

---

### B-051. 권한: AUTHORITY-CHECK·권한 개념 구성·표준 권한 객체·분석 도구·T-code [개념] ★★
<!-- src: IB-135, IB-136, IB-137, TC-038, TC-027, TC-037 -->
선택한 항공사에 대해 조회(03) 권한이 있는지 S_CARRID로 검사하는 코드다.

```abap
AUTHORITY-CHECK ____(a)____ 'S_CARRID'
  ID 'CARRID' ____(b)____ p_carr
  ID 'ACTVT'  FIELD '03'.
IF sy-subrc <> 0.
  MESSAGE e001(zib) WITH p_carr.     " 항공사 &1에 대한 권한 없음
ENDIF.
```

(1) 빈칸 (a), (b)를 채우고 sy-subrc 0, 4, 12의 의미를 쓰시오. 검사하지 않을 필드 처리, 커스텀 리포트에 직접 검사를 넣어야 하는 이유, 선택 화면 검사 위치, ACTVT 주요 값을 쓰시오.
(2) 권한 필드, 권한 객체, 권한 객체 클래스, 권한, 프로파일, 역할, 사용자의 관계와 관리 트랜잭션을 쓰시오. SU24의 역할은?
(3) 다음 권한 객체가 검사하는 대상을 쓰시오: S_TCODE, S_DEVELOP, S_TABU_DIS, S_TABU_NAM, S_PROGRAM, S_RFC, S_BTCH_JOB, S_SERVICE, S_CARRID, S_DATASET, S_USER_GRP
(4) 옳지 **않은** 연결은? ① S_TCODE – 트랜잭션 시작 ② S_TABU_DIS – 테이블 권한 그룹 기준 SM30/SE16 ③ S_PROGRAM – 프로그램 권한 그룹 기준 SUBMIT·변형 유지 ④ S_DEVELOP – 개발 객체 생성·변경, 디버깅 ⑤ S_RFC – 사용자 비밀번호 변경
(5) 사용자가 "권한이 없습니다" 오류를 받았다. SU53, ST01, STAUTHTRACE의 차이를 쓰시오.
(6) 다음 T-code를 쓰시오: ① 사용자 생성·변경·잠금 해제·비밀번호 초기화 ② 여러 사용자 일괄 변경 ③ 역할 관리·프로파일 생성 ④ 권한 객체·필드 정의 ⑤ 트랜잭션별 권한 객체 기본값(고객용) ⑥ 마지막 실패 권한 검사 ⑦ 사용자 정보 시스템 ⑧ 자기 사용자 정보(기본값, 날짜 형식, SET/GET 파라미터). 사용자-역할 할당과 로그온 정보 테이블, RAP·CDS에서의 권한 검사 방법은?

<details><summary>정답·해설</summary>

**(1)** (a) `OBJECT` (b) `FIELD`. 0 = 권한 있음, 4 = 객체 권한은 있지만 지정한 값에 대한 권한 없음, 12 = 이 객체에 대한 권한이 전혀 없음. 검사하지 않을 필드는 `ID 'ACTVT' DUMMY`(아무 값이나 허용). ABAP SQL SELECT는 권한을 자동 검사하지 않으므로 커스텀 리포트는 직접 AUTHORITY-CHECK를 넣어야 한다(CDS는 DCL로 자동 검사 가능). 선택 화면 검사는 `AT SELECTION-SCREEN`에서 해야 사용자가 바로 고칠 수 있다. ACTVT: 01 생성, 02 변경, 03 조회, 06 삭제.
**(2)** **권한 필드**(SU20): 검사 항목(CARRID, ACTVT). **권한 객체**(SU21): 최대 10개 권한 필드 묶음(S_CARRID), **권한 객체 클래스**로 분류(BC_C). **권한**: 필드에 허용 값을 채운 인스턴스(CARRID = LH, ACTVT = 03). **프로파일**: 권한 모음, 보통 역할에서 자동 생성. **역할**(PFCG): 메뉴(트랜잭션)와 권한 데이터 묶음, 생성하면 프로파일이 만들어져 사용자에게 할당. **사용자**(SU01): 역할을 할당받음. SU24는 트랜잭션별로 검사하는 권한 객체 제안값을 관리하고 PFCG가 이를 읽어 권한 데이터를 채운다. 트랜잭션 시작 시 S_TCODE 검사는 자동이고, 그 안의 업무 검사는 프로그램의 AUTHORITY-CHECK가 한다.
**(3)** S_TCODE: 트랜잭션 시작. S_DEVELOP: Workbench 개발 객체 생성·변경·조회·디버깅(객체 유형, 패키지, 활동). S_TABU_DIS: 테이블 권한 그룹 단위 조회·유지보수(SM30, SE16). S_TABU_NAM: 테이블 이름 단위 접근. S_PROGRAM: 프로그램 권한 그룹 단위 실행·변형 유지(SUBMIT, SA38). S_RFC: RFC 호출(함수 그룹·FM 단위). S_BTCH_JOB: 백그라운드 잡 작업(다른 사용자 잡의 해제·삭제·조회 등, 잡 그룹·JOBACTION 단위; 전체 관리자 권한은 S_BTCH_ADM). S_SERVICE: 외부 서비스 시작(OData, Fiori 앱의 HTTP 서비스). S_CARRID: Flight 모델 항공사와 활동(교육용). S_DATASET: 서버 파일 접근. S_USER_GRP: 사용자 그룹 단위 사용자 관리.
**(4)** **⑤**. S_RFC는 RFC 호출 권한이고 사용자 관리 권한은 S_USER_GRP 등이다.
**(5)** SU53: 해당 사용자의 마지막으로 실패한 권한 검사(객체, 필드 값), 오류 직후 같은 세션에서 실행해야 정확하다. ST01: System Trace, 권한 검사뿐 아니라 커널 함수·DB·RFC 등도 기록하며 성공·실패 모두 기록. STAUTHTRACE: 권한 검사 전용 트레이스, 시스템 전체(모든 서버)를 사용자 단위로 기록하고 중복 제거가 편하다. SU53은 "마지막 실패 한 건"만 보이므로 여러 검사가 실패하거나 프로그램이 sy-subrc를 보고 다르게 처리하면 트레이스로 전부 확인한다. 역할 수정은 PFCG.
**(6)** ① SU01 ② SU10 ③ PFCG ④ SU21 ⑤ SU24 ⑥ SU53 ⑦ SUIM ⑧ SU3. Fiori 카탈로그·그룹(또는 Space/Page)도 PFCG 역할 메뉴에 넣는다. 사용자-역할 할당은 AGR_USERS, 로그온 정보는 USR02. RAP·CDS에서는 DCL(`@AccessControl`)과 BDEF의 `authorization master`로 같은 권한 객체를 검사한다.

</details>

---

### B-052. 전송 요청: Workbench/Customizing·태스크·버전·복사 전송·테이블 데이터·E071 코드 [개념] ★★
<!-- src: CL-040, TC-032, TC-042, IB-141, IB-138, IB-139, IB-140, TC-033, TC-034 -->
(1) Workbench Request와 Customizing Request에 담기는 객체를 쓰고, 다음 중 Customizing 요청에 기록되는 것을 고르시오. ① SE38로 수정한 Z 프로그램 ② SE11로 추가한 Z 테이블 필드 ③ SPRO에서 저장한 판매 문서 유형 설정 ④ SE24로 만든 Z 클래스 ⑤ ADT로 만든 CDS 뷰 엔티티. $TMP 객체는?
(2) 요청과 태스크의 관계와 릴리스 순서, 릴리스 시 일어나는 일, 개발 → 품질 → 운영 전송 과정(트랜잭션, Transport Layer/Route)을 쓰시오. 요청 번호 `DEVK900123`의 DEV와 K, 요청 관련 테이블은?
(3) 옳지 **않은** 것을 고르시오. ① 한 객체는 동시에 하나의 수정 가능한 요청에만 잠겨 있을 수 있어 다른 개발자는 같은 요청에 태스크를 받아야 한다. ② `$TMP` 객체는 객체 디렉터리 항목에서 패키지를 바꾸면 전송 가능 객체가 된다. ③ 원본 시스템이 아닌 시스템에서 객체를 바꾸면 Repair로 기록된다. ④ 태스크가 하나라도 릴리스되지 않았어도 요청을 먼저 릴리스할 수 있다. ⑤ SE03에서 특정 객체가 들어 있는 요청을 검색할 수 있다. 릴리스 전 확인 사항과 import 순서 주의점은?
(4) ABAP 객체 버전은 언제 만들어지는가? 버전 관리로 할 수 있는 일과, 릴리스 없이 버전을 만들 수 있는지 쓰시오.
(5) 개발 중인 요청을 닫지 않고 품질 시스템에서 먼저 테스트하려 한다. 복사 전송(Transport of Copies)과 일반 요청의 차이를 쓰시오.
(6) Z 테이블 데이터(행)를 품질·운영으로 옮기려 한다. Delivery Class C와 A인 경우 각각의 방법, 같은 시스템 다른 클라이언트로 옮기는 방법을 쓰시오.
(7) E071의 PGMID에 대해 옳은 것은? ① R3TR은 서브 객체만 전송 ② LIMU는 객체 전체 전송 ③ `R3TR CLAS ZCL_A`는 클래스 ZCL_A 전체(모든 include)를 전송 ④ `LIMU METH`는 함수 모듈 하나 ⑤ CORR은 테이블 항목 키 목록. LIMU 예와 테이블 항목 키 저장 위치를 쓰시오.
(8) TADIR·E071 객체 유형 코드의 의미를 쓰시오: PROG, CLAS, INTF, FUGR, TABL, DTEL, DOMA, TTYP, DDLS, BDEF, SRVD, SRVB, DCLS, DDLX, MSAG, DEVC, TRAN, ENQU, SHLP, VIEW, SSFO, SFPF, NROB. TADIR의 키와 주요 필드는?

<details><summary>정답·해설</summary>

**(1)** Workbench: 클라이언트 독립 Repository 객체(프로그램, 클래스, DDIC, 화면, CDS)와 클라이언트 독립 커스터마이징. Customizing: 클라이언트 종속 커스터마이징(SPRO 설정, Delivery Class C 테이블 항목, `R3TR TABU`/`VDAT`/`CDAT`). 정답 **③**(나머지는 클라이언트 독립 Repository 객체라 Workbench 요청). 패키지가 $TMP(로컬 객체)이면 전송 요청 없이 저장되고 전송할 수 없다.
**(2)** 요청 하나 아래에 사용자별 태스크가 있고 객체 변경은 그 사용자의 태스크에 기록된다. 요청에 포함된 객체는 다른 요청에서 바꿀 수 없게 잠긴다. **태스크를 모두 릴리스한 뒤 요청을 릴리스**하면 데이터/코파일이 전송 디렉터리로 Export되어 다음 시스템 import queue에 들어간다. SE09/SE10에서 요청 생성·릴리스 → STMS에서 import queue를 보고 QAS, PRD 순서로 Import. 경로는 STMS의 Transport Layer(패키지에 지정)와 Transport Route(통합 경로 DEV→QAS, 배송 경로 QAS→PRD)로 결정된다. DEV는 원본 시스템 ID(SID), K는 일반 전송 요청 문자(번호 체계 SIDK9nnnnn). 요청 헤더 E070, 객체 목록 E071, 설명 E07T. 전송 로그는 SE09, import 이력은 STMS.
**(3)** **④**. 요청을 릴리스하려면 모든 태스크를 먼저 릴리스해야 하고, ATC 검사가 걸려 있으면 오류 시 릴리스가 막힐 수 있다. 릴리스 전 객체 활성화와 문법 검사, 의존 객체(새 데이터 엘리먼트를 쓰는 테이블 등)가 같이 가는지 확인해야 운영 Import 오류를 막는다. import 순서가 바뀌면 오래된 버전이 덮어쓸 수 있다.
**(4)** 전송 요청을 **릴리스할 때** 버전이 자동 저장되고, 편집기 Utilities → Versions → Generate Version으로 릴리스 없이 수동 생성할 수 있다. 할 수 있는 일: 이전 버전과 비교(차이 표시), 이전 버전으로 되돌리기(Retrieve), 다른 시스템과 원격 비교(Remote Comparison, RFC), 누가 언제 어느 요청으로 바꿨는지 확인. 운영 장애 시 최근 변경 확인에 쓴다. ADT에서는 Compare With → Revision History.
**(5)** SE01에서 만드는 요청 유형으로 객체의 현재 상태를 **복사해** 지정한 대상 시스템(QAS)으로만 보낸다. 원래 요청을 릴리스하지 않으므로 객체 잠금이 유지되어 개발을 계속할 수 있고, 전송 경로를 따르지 않고 대상을 직접 지정하며 운영까지 자동으로 이어지지 않는다. 릴리스해도 버전이 생기지 않는다. 최종 반영은 원래 요청을 릴리스해 정상 경로로 보낸다. 테스트 중 여러 번 고칠 때 QAS import 큐에 불필요한 요청이 쌓이지 않게 하며, 일부 회사는 ChaRM/SolMan 정책상 복사 전송만 QAS에 올리게 한다.
**(6)** **C**: TMG(SM30)에서 저장하면 Customizing 요청을 묻고 기록된다(Recording Routine을 Standard로 생성한 경우), 또는 SM30 → Table View → Transport로 선택 행을 넣는다. **A**: 보통 운영 데이터라 전송하지 않지만 필요하면 SE09/SE10에서 Workbench 요청 객체 목록에 `R3TR TABU <테이블>`을 직접 추가하고 Key(키 값 또는 `*`)를 지정한다(SM30 저장 시 자동 기록 안 됨). 같은 시스템 다른 클라이언트는 SCC1(요청 기준 클라이언트 복사). Delivery Class는 A 마스터·트랜잭션, C 고객 커스터마이징, L 임시, G·E·S·W SAP 관련이며 대량 데이터는 이관 도구를 쓴다.
**(7)** **③**. R3TR은 완전한 객체(TADIR 등록 단위), LIMU는 객체의 일부(`LIMU METH` 메서드 하나, `LIMU FUNC` 함수 모듈 하나, `LIMU REPS` 리포트 소스, `LIMU TABD` 테이블 정의). 테이블 항목 전송은 `R3TR TABU`이고 키는 E071K. CORR은 주석·관리용 항목이다.
**(8)** PROG 프로그램(리포트, 모듈 풀, include), CLAS 클래스, INTF 인터페이스, FUGR 함수 그룹, TABL 테이블·구조, DTEL 데이터 엘리먼트, DOMA 도메인, TTYP 테이블 타입, DDLS CDS 데이터 정의(DDL 소스), BDEF Behavior Definition, SRVD Service Definition, SRVB Service Binding, DCLS CDS 접근 제어, DDLX CDS 메타데이터 확장, MSAG 메시지 클래스, DEVC 패키지, TRAN 트랜잭션, ENQU 잠금 객체, SHLP 검색 도움말, VIEW DDIC 뷰, SSFO Smart Form, SFPF Adobe Form, NROB 번호 범위 객체. TADIR 키는 PGMID + OBJECT + OBJ_NAME이고 DEVCLASS(패키지), AUTHOR(생성자)를 가진다.

</details>

---

### B-053. 시스템 관리 T-code: 전송·클라이언트·SCC4·업그레이드·공통 기능·명령 필드 [개념] ★★
<!-- src: TC-031, TC-035, TC-040, TC-041, TC-012 -->
(1) 다음 T-code를 쓰시오: ① Workbench Organizer ② Customizing Organizer ③ Transport Organizer(확장) ④ Transport Organizer Tools ⑤ Transport Management System ⑥ System Change Option ⑦ 클라이언트 관리 ⑧ 요청 단위 클라이언트 간 Customizing 복사 ⑨ Support Package Manager ⑩ Add-on 설치 ⑪ 로컬 클라이언트 복사 / 원격 복사 / 복사 로그 / 클라이언트 삭제
(2) SCC4에서 클라이언트별로 지정하는 항목과 운영 클라이언트, 개발계 Customizing 클라이언트의 일반 설정을 쓰시오.
(3) 업그레이드·SP 적용 시 수정 객체 조정에 대해 옳은 것은? ① SPAU 먼저, SPDD 나중 ② SPDD는 Dictionary 객체를 다루며 Import 중에 수행해 데이터 손실을 막는다 ③ SPAU는 Dictionary 객체만 다룬다 ④ SNOTE로 적용한 노트는 SPAU 대상이 아니다 ⑤ Enhancement 구현은 SPDD에서 조정한다
(4) 다음 T-code를 쓰시오: ① IMG 실행 ② 번호 범위 객체·구간 ③ 변경 문서 객체 정의 ④ 트랜잭션 변형 ⑤ 프로파일 파라미터 관리 / 값 조회·동적 변경 ⑥ ICF 노드 활성화 ⑦ 트랜잭션 잠금 ⑧ Area Menu. 번호 채번 API, SCDO가 생성하는 FM, OData 404 시 먼저 볼 곳은?
(5) SAP GUI 명령 필드에 다음을 입력했을 때의 동작을 쓰시오: `/nSE38`, `/oSE80`, `/n`, `/nend`, `/nex`, `/h`, `/i`, `/o`, `/hs`, `/*SE38`. `/n` 없이 T-code만 입력하면?

<details><summary>정답·해설</summary>

**(1)** ① SE09 ② SE10 ③ SE01 ④ SE03 ⑤ STMS ⑥ SE06 ⑦ SCC4 ⑧ SCC1 ⑨ SPAM ⑩ SAINT ⑪ SCCL / SCC9 / SCC3 / SCC5. 최근 릴리스에서 SE09와 SE10은 같은 화면으로 두 요청을 함께 보여 준다. SCC1은 개발계 Customizing 클라이언트의 요청을 단위 테스트 클라이언트로 복사할 때 쓰고(같은 시스템), 다른 시스템으로는 STMS Import.
**(2)** Client role(Production, Test, Customizing, Demo, Training, SAP reference), Changes and Transports for Client-Specific Objects(자동 기록 / 기록 없이 변경 허용 / 변경 불가 / 자동 기록 불가), Cross-Client Object Changes(Repository·클라이언트 독립 Customizing 변경 허용 여부), 그 밖에 Protection(Client Copier and Comparison Tool), CATT/eCATT 허용, 논리 시스템 할당. 운영: Role = Production, 클라이언트 종속 변경 불가, Cross-Client 변경 불가, 덮어쓰기 금지 보호. 개발계 Customizing 클라이언트는 "Automatic recording of changes"로 두어 SPRO 변경이 반드시 요청에 기록되게 한다. 시스템 전체 수정 가능 여부는 SE06.
**(3)** **②**. SPDD → (나머지 Import) → SPAU 순서이고, SPDD를 놓치면 수정한 테이블 필드가 SAP 버전으로 돌아가 데이터가 사라질 수 있다. SPAU는 프로그램, 화면, 메뉴 등 Repository 객체와 SNOTE로 적용한 노트를 조정하고, 확장 구현은 SPAU_ENH에서 조정한다.
**(4)** ① SPRO ② SNRO ③ SCDO ④ SHD0 ⑤ RZ10 / RZ11 ⑥ SICF ⑦ SM01(최신 릴리스 SM01_DEV/SM01_CUS) ⑧ SE43. 채번은 `NUMBER_GET_NEXT`(클래식) 또는 `CL_NUMBERRANGE_RUNTIME=>NUMBER_GET`(ABAP Cloud 포함). SCDO에서 객체를 만들면 `<객체명>_WRITE_DOCUMENT` FM이 생성되고 이를 호출해 CDHDR/CDPOS에 변경 이력을 남긴다. OData·Fiori 서비스가 404면 SICF에서 노드가 비활성인지 먼저 본다.
**(5)** `/nSE38` 현재 트랜잭션 종료 후 같은 세션에서 SE38. `/oSE80` 새 세션(창)에서 SE80. `/n` 현재 트랜잭션 종료(SAP 메뉴로). `/nend` 로그오프(확인 팝업). `/nex` 확인 없이 즉시 로그오프(저장 안 된 데이터 손실). `/h` 디버깅 모드(다음 화면 동작부터). `/i` 현재 세션 닫기. `/o` 세션 목록(생성·종료 선택). `/hs` 시스템 디버깅(시스템 프로그램까지). `/*SE38` 초기 화면을 건너뛰고 실행. `/n` 없이 T-code만 입력하면 SAP 메뉴 화면에서만 실행된다.

</details>

---

## 객체지향(OOP) 1: 클래스·생성자

### B-054. 클래스 기초: 가시성·READ-ONLY·정적/인스턴스 속성·참조·싱글톤·CREATE 제한 [코드] ★★
<!-- src: OO-001, OO-002, MX-033, OO-003, MX-034 -->
다음 두 클래스를 보고 물음에 답하시오.

```abap
CLASS lcl_counter DEFINITION.
  PUBLIC SECTION.
    CLASS-DATA total TYPE i READ-ONLY.
    DATA own TYPE i READ-ONLY.
    METHODS add.
ENDCLASS.
CLASS lcl_counter IMPLEMENTATION.
  METHOD add.
    total = total + 1.
    own   = own + 1.
  ENDMETHOD.
ENDCLASS.

CLASS lcl_cnt DEFINITION.
  PUBLIC SECTION.
    DATA mv_val TYPE i VALUE 10.
    CLASS-DATA gv_calls TYPE i.
    METHODS run RETURNING VALUE(rv) TYPE i.
ENDCLASS.
CLASS lcl_cnt IMPLEMENTATION.
  METHOD run.
    DATA mv_val TYPE i VALUE 1.
    gv_calls = gv_calls + 1.
    mv_val = mv_val + 5.
    me->mv_val = me->mv_val + mv_val.
    rv = mv_val * gv_calls.
  ENDMETHOD.
ENDCLASS.

START-OF-SELECTION.
  DATA(o1) = NEW lcl_counter( ).
  DATA(o2) = NEW lcl_counter( ).
  o1->add( ).  o1->add( ).  o2->add( ).
  DATA(o3) = o1.
  o3->add( ).
  CLEAR o1.

  DATA: lo1 TYPE REF TO lcl_cnt, lo2 TYPE REF TO lcl_cnt,
        r1 TYPE i, r2 TYPE i, r3 TYPE i.
  CREATE OBJECT lo1.
  CREATE OBJECT lo2.
  r1 = lo1->run( ).
  r2 = lo1->run( ).
  r3 = lo2->run( ).
  WRITE: / r1, r2, r3, lo1->mv_val, lo2->mv_val, lcl_cnt=>gv_calls.
```

(1) PUBLIC, PROTECTED, PRIVATE SECTION 구성요소에 자기 클래스, 하위 클래스, 외부, FRIENDS가 접근할 수 있는지 표로 쓰시오. `DATA ... READ-ONLY`의 의미와 선언 위치, 인스턴스 속성과 정적 속성의 차이와 외부 접근 문법을 쓰시오.
(2) `lcl_counter=>total`, `o2->own`, `o3->own`, `o1 IS BOUND`의 값을 쓰고, 프로그램 끝에 `lcl_counter=>total = 0.`을 추가하면 어떻게 되는지 쓰시오. `CLEAR o1` 후 객체는?
(3) WRITE 문이 출력하는 값 6개를 순서대로 쓰고 이유를 설명하시오.
(4) 프로그램 안에서 인스턴스가 하나만 존재하는 설정 클래스의 빈칸을 채우시오. 클래스 외부에서 `DATA(lo) = NEW lcl_config( ).`를 쓰면?
```abap
CLASS lcl_config DEFINITION FINAL ____(a)____.
  PUBLIC SECTION.
    CLASS-METHODS get_instance RETURNING VALUE(ro_inst) TYPE REF TO lcl_config.
    METHODS get_currency RETURNING VALUE(rv) TYPE s_currcode.
  PRIVATE SECTION.
    ____(b)____ go_inst TYPE REF TO lcl_config.
ENDCLASS.
CLASS lcl_config IMPLEMENTATION.
  METHOD get_instance.
    IF go_inst IS ____(c)____.
      go_inst = ____(d)____.
    ENDIF.
    ro_inst = go_inst.
  ENDMETHOD.
  METHOD get_currency.
    rv = 'EUR'.
  ENDMETHOD.
ENDCLASS.
```
(5) 싱글톤의 세 요소와 FINAL을 붙이는 이유, 정적 속성의 범위를 쓰시오.
(6) 옳지 **않은** 것을 고르시오. ① `CREATE PRIVATE` 클래스는 자기 메서드(와 friend)에서만 인스턴스를 만들 수 있다. ② `CREATE PROTECTED` 클래스는 자신과 서브클래스(와 friend)에서 만들 수 있다. ③ `ABSTRACT` 클래스에도 인스턴스 생성자를 정의할 수 있고 서브클래스 생성자에서 `super->constructor( )`로 호출된다. ④ `CREATE PRIVATE` 클래스를 상속한 서브클래스는 자신을 `CREATE PUBLIC`으로 선언하면 어디서나 인스턴스를 만들 수 있다. ⑤ 정적 메서드는 서브클래스에서 재정의할 수 없다.

<details><summary>정답·해설</summary>

**(1)**

| 섹션 | 자기 클래스 | 하위 클래스 | 외부 | FRIENDS |
|---|---|---|---|---|
| PUBLIC | O | O | O | O |
| PROTECTED | O | O | X | O |
| PRIVATE | O | X | X | O |

READ-ONLY: 외부에서 읽기만 가능하고 변경은 클래스 자신(과 하위 클래스, FRIENDS)의 메서드에서만. PUBLIC SECTION에서만 의미가 있으며 getter 없이 상태를 노출할 때 쓴다. 인스턴스 속성은 객체마다 따로 있고 `oref->attr`로, 정적 속성은 클래스당 하나(같은 내부 세션의 모든 객체가 공유)이고 `class=>attr`로 접근한다. 정적 메서드에서는 인스턴스 속성에 접근할 수 없다. 캡슐화 원칙상 속성은 PRIVATE에 두고 메서드로 공개하는 것이 기본이며, 전역 클래스는 CREATE PUBLIC/PROTECTED/PRIVATE로 누가 인스턴스를 만들 수 있는지도 정한다.
**(2)** total = **4**(add 4번 호출, 공유 카운터), o2->own = **1**, o3->own = **3**(`o3 = o1`은 참조 복사라 같은 객체: o1→add 2번 + o3→add 1번), `o1 IS BOUND` = **거짓**. `lcl_counter=>total = 0.`은 **문법 오류**(READ-ONLY 속성은 외부에서 변경 불가). `CLEAR o1`은 참조 변수만 비우고 객체는 o3가 참조하므로 살아 있다(참조가 하나도 없을 때 가비지 컬렉터가 회수).
**(3)** `6  12  18  22  16  3`. 메서드 안 `DATA mv_val`은 같은 이름의 인스턴스 속성을 가려, 이름만 쓰면 지역 변수, `me->mv_val`이면 속성이다. 지역 변수는 호출마다 1로 다시 초기화된다.

| 호출 | gv_calls | 지역 mv_val | 속성 mv_val | rv |
|---|---|---|---|---|
| lo1 첫 번째 | 1 | 6 | lo1: 10+6 = 16 | 6×1 = 6 |
| lo1 두 번째 | 2 | 6 | lo1: 16+6 = 22 | 6×2 = 12 |
| lo2 첫 번째 | 3 | 6 | lo2: 10+6 = 16 | 6×3 = 18 |

`CLASS-DATA`는 모든 인스턴스가 공유해 lo2 호출 때 이어서 3이 되고, 인스턴스 속성은 객체마다 따로 있다.
**(4)** (a) `CREATE PRIVATE` (b) `CLASS-DATA` (c) `INITIAL`(또는 `NOT BOUND`) (d) `NEW #( )`. 외부에서 NEW하면 **문법 오류**: CREATE PRIVATE 클래스는 자기 자신(과 FRIENDS)만 인스턴스를 만들 수 있다.
**(5)** 외부 생성 금지(CREATE PRIVATE), 유일 인스턴스를 담는 정적 속성, 지연 생성(lazy) 정적 메서드. FINAL은 하위 클래스를 통한 우회를 막는다. 정적 속성은 내부 세션 범위이므로 "프로그램 실행 단위로 하나"이며, 사용자 간 공유가 필요하면 Shared Objects를 쓴다.
**(6)** **④**. 서브클래스 인스턴스를 만들려면 상위 클래스 생성자도 실행돼야 하는데, 상위가 `CREATE PRIVATE`이면 서브클래스는 상위의 friend가 아닌 한 인스턴스를 만들 수 없다. 그래서 `CREATE PRIVATE` 클래스는 보통 `FINAL`로도 선언한다. ③ 추상 클래스는 직접 `NEW`할 수 없을 뿐 생성자는 가질 수 있다. ⑤ 정적 메서드는 다형성 대상이 아니다.

</details>

---

### B-055. 생성자: 정적/인스턴스 생성자 호출 순서와 상속 규칙 위반 [코드] ★★★
<!-- src: OO-004, OO-005, OO-006 -->
(1) 다음 프로그램의 출력을 쓰고 순서를 설명하시오.
```abap
CLASS lcl_log DEFINITION.
  PUBLIC SECTION.
    CLASS-DATA text TYPE string.
    CLASS-METHODS add IMPORTING iv TYPE string.
ENDCLASS.
CLASS lcl_log IMPLEMENTATION.
  METHOD add.
    text = |{ text }{ iv } |.
  ENDMETHOD.
ENDCLASS.
CLASS lcl_a DEFINITION.
  PUBLIC SECTION.
    CLASS-METHODS class_constructor.
    METHODS constructor.
ENDCLASS.
CLASS lcl_a IMPLEMENTATION.
  METHOD class_constructor.
    lcl_log=>add( `Acc` ).
  ENDMETHOD.
  METHOD constructor.
    lcl_log=>add( `Ac` ).
  ENDMETHOD.
ENDCLASS.
CLASS lcl_b DEFINITION INHERITING FROM lcl_a.
  PUBLIC SECTION.
    CLASS-METHODS class_constructor.
    METHODS constructor.
ENDCLASS.
CLASS lcl_b IMPLEMENTATION.
  METHOD class_constructor.
    lcl_log=>add( `Bcc` ).
  ENDMETHOD.
  METHOD constructor.
    lcl_log=>add( `Bc1` ).
    super->constructor( ).
    lcl_log=>add( `Bc2` ).
  ENDMETHOD.
ENDCLASS.
START-OF-SELECTION.
  lcl_log=>add( `S` ).
  DATA(o1) = NEW lcl_b( ).
  DATA(o2) = NEW lcl_b( ).
  DATA(o3) = NEW lcl_a( ).
  WRITE lcl_log=>text.
```
(2) (1)의 lcl_b 생성자에서 `super->constructor( )` 호출 전에 쓸 수 있는 것과 없는 것은?
(3) 다음 코드의 문법 오류 (가)~(라)의 이유와 수정 방법을 쓰시오.
```abap
CLASS lcl_vehicle DEFINITION ABSTRACT.
  PUBLIC SECTION.
    METHODS constructor IMPORTING iv_id TYPE string.
    METHODS get_info RETURNING VALUE(rv) TYPE string.
    CLASS-METHODS get_count RETURNING VALUE(rv) TYPE i.
  PROTECTED SECTION.
    DATA mv_id TYPE string.
ENDCLASS.
CLASS lcl_vehicle IMPLEMENTATION.
  METHOD constructor.
    mv_id = iv_id.
  ENDMETHOD.
  METHOD get_info.
    rv = mv_id.
  ENDMETHOD.
  METHOD get_count.
    rv = 0.
  ENDMETHOD.
ENDCLASS.
CLASS lcl_car DEFINITION INHERITING FROM lcl_vehicle FINAL.
  PUBLIC SECTION.
    METHODS constructor IMPORTING iv_id TYPE string iv_seats TYPE i.
    METHODS get_info REDEFINITION.
    CLASS-METHODS get_count REDEFINITION.                 " (가)
  PRIVATE SECTION.
    DATA mv_seats TYPE i.
ENDCLASS.
CLASS lcl_car IMPLEMENTATION.
  METHOD constructor.
    mv_seats = iv_seats.                                  " (나)
    super->constructor( iv_id = iv_id ).
  ENDMETHOD.
  METHOD get_info.
    rv = |{ super->get_info( ) } / { mv_seats } seats|.
  ENDMETHOD.
  METHOD get_count.
    rv = 1.
  ENDMETHOD.
ENDCLASS.
CLASS lcl_sportscar DEFINITION INHERITING FROM lcl_car.    " (다)
ENDCLASS.
START-OF-SELECTION.
  DATA(lo_v) = NEW lcl_vehicle( iv_id = `V1` ).            " (라)
```
(4) lcl_car가 constructor를 다른 시그니처로 선언한 것은 오류인가? 인스턴스 생성자의 재정의·호출 규칙을 쓰시오.
(5) 옳지 **않은** 것을 고르시오. ① `class_constructor`는 파라미터를 가질 수 없다. ② 하위 클래스가 생성자를 선언하지 않으면 상위 클래스 생성자의 인터페이스가 쓰인다. ③ 정적 생성자는 그 클래스의 인스턴스가 만들어질 때마다 실행된다. ④ 하위 클래스가 생성자를 구현하면 `super->constructor( )`를 반드시 호출해야 한다. ⑤ 정적 생성자는 정적 속성에 처음 접근할 때도 실행된다(상수·타입 접근 제외).
(6) 정적 생성자가 실행되는 "첫 사용" 시점을 네 가지 쓰시오.

<details><summary>정답·해설</summary>

**(1)** `S Acc Bcc Bc1 Ac Bc2 Bc1 Ac Bc2 Ac `. ① `S`: lcl_a, lcl_b는 아직 사용되지 않아 정적 생성자도 실행 전. ② 첫 `NEW lcl_b( )`: 클래스 첫 사용이라 정적 생성자가 상속 트리 위에서부터 → `Acc`, `Bcc`, 그다음 lcl_b 인스턴스 생성자 `Bc1` → `super->constructor( )`로 `Ac` → `Bc2`. ③ 두 번째 `NEW lcl_b( )`: 정적 생성자는 내부 세션당 한 번만 → `Bc1 Ac Bc2`. ④ `NEW lcl_a( )`: lcl_a 정적 생성자는 이미 실행됨 → `Ac`만.
**(2)** `super->constructor( )` 호출 전에는 인스턴스 구성요소(me)에 접근할 수 없지만, 위처럼 정적 구성요소(lcl_log=>add)는 쓸 수 있다.
**(3)** (가) 정적 메서드는 재정의할 수 없다 → 줄을 지우고(구현의 get_count도 삭제) 필요하면 다른 이름의 정적 메서드를 선언, 다형성이 필요하면 인스턴스 메서드로. (나) `super->constructor( )` 호출 전에 인스턴스 속성 접근 불가 → `super->constructor( iv_id = iv_id ).`를 먼저 호출하고 `mv_seats = iv_seats.`. (다) FINAL 클래스 lcl_car는 상속할 수 없다 → lcl_car의 FINAL을 지우거나 lcl_vehicle을 상속. (라) ABSTRACT 클래스는 인스턴스를 만들 수 없다 → `NEW lcl_car( iv_id = `V1` iv_seats = 4 )`처럼 구체 클래스를 만들고 lcl_vehicle 타입 참조로 받는다.
**(4)** 오류가 아니다. 인스턴스 생성자는 재정의 대상이 아니라 클래스마다 따로 선언하며 시그니처를 바꿀 수 있다. 하위 클래스가 생성자를 선언하면 반드시 `super->constructor`를 호출해야 하고 상위 생성자의 필수 파라미터를 채워야 한다.
**(5)** **③**. 정적 생성자는 내부 세션에서 클래스를 처음 사용할 때 **한 번만** 실행된다. ① 자동 호출이라 파라미터를 넘길 방법이 없다. ② `NEW sub( iv_id = ... )`처럼 상위 생성자를 그대로 쓴다. ④ 상위 클래스가 생성자를 명시적으로 선언하지 않았어도 호출해야 한다.
**(6)** 첫 인스턴스 생성, 정적 속성 접근, 정적 메서드 호출, 이벤트 핸들러 등록.

</details>

---

## 객체지향(OOP) 2: 상속·인터페이스·이벤트·설계

### B-056. 상속: 재정의 규칙·me/super·다형성 결과·템플릿 메서드 작성 [작성] ★★
<!-- src: OO-007, OO-008, OO-009 -->
다음 클래스 계층을 보고 물음에 답하시오(lcl_animal ← lcl_dog ← lcl_puppy, lcl_animal ← lcl_cat).

```abap
CLASS lcl_animal DEFINITION.
  PUBLIC SECTION.
    METHODS speak    RETURNING VALUE(rv) TYPE string.
    METHODS describe RETURNING VALUE(rv) TYPE string.
ENDCLASS.
CLASS lcl_animal IMPLEMENTATION.
  METHOD speak.
    rv = `A`.
  ENDMETHOD.
  METHOD describe.
    rv = |[{ speak( ) }]|.
  ENDMETHOD.
ENDCLASS.
CLASS lcl_dog DEFINITION INHERITING FROM lcl_animal.
  PUBLIC SECTION.
    METHODS speak REDEFINITION.
ENDCLASS.
CLASS lcl_dog IMPLEMENTATION.
  METHOD speak.
    rv = |D{ super->speak( ) }|.
  ENDMETHOD.
ENDCLASS.
CLASS lcl_cat DEFINITION INHERITING FROM lcl_animal.
  PUBLIC SECTION.
    METHODS describe REDEFINITION.
ENDCLASS.
CLASS lcl_cat IMPLEMENTATION.
  METHOD describe.
    rv = |<{ speak( ) }>|.
  ENDMETHOD.
ENDCLASS.
CLASS lcl_puppy DEFINITION INHERITING FROM lcl_dog.
  PUBLIC SECTION.
    METHODS speak REDEFINITION.
ENDCLASS.
CLASS lcl_puppy IMPLEMENTATION.
  METHOD speak.
    rv = |P{ super->speak( ) }|.
  ENDMETHOD.
ENDCLASS.

START-OF-SELECTION.
  DATA lt_zoo TYPE STANDARD TABLE OF REF TO lcl_animal WITH EMPTY KEY.
  DATA lv_out TYPE string.
  lt_zoo = VALUE #( ( NEW lcl_animal( ) ) ( NEW lcl_dog( ) )
                    ( NEW lcl_cat( ) )    ( NEW lcl_puppy( ) ) ).
  LOOP AT lt_zoo INTO DATA(lo_animal).
    lv_out = |{ lv_out }{ lo_animal->describe( ) } |.
  ENDLOOP.
```

(1) 재정의할 수 있는 메서드와 없는 메서드를 구분하시오.
(2) 재정의할 때 바꿀 수 있는 것과 없는 것(시그니처, 가시성)과 선언 방법을 쓰시오.
(3) `me->meth( )`와 `super->meth( )`의 차이를 쓰시오.
(4) 클래스와 메서드에 붙는 ABSTRACT/FINAL의 의미를 각각 쓰시오. FINAL 클래스의 메서드는?
(5) lv_out의 최종 값을 쓰고 각 객체별로 설명하시오.
(6) 항공권 가격 계산 클래스를 작성하시오. 추상 클래스 `lcl_ticket`의 공개 메서드 `price`(RETURNING i)는 재정의할 수 없고 `base_fare( ) + surcharge( )`를 반환한다. `base_fare`는 보호 추상 메서드, `surcharge`는 보호 메서드로 기본 0. `lcl_economy`: 기본 운임 100. `lcl_business`: 기본 운임 300, 할증 50. 두 객체를 lcl_ticket 참조 테이블에 넣고 price 합계(450)를 구하는 코드도 쓰시오.
(7) (6)에서 쓴 설계 패턴의 이름과 원리, 재정의 위치의 규칙을 쓰시오.

<details><summary>정답·해설</summary>

**(1)** 가능: 상위 클래스의 PUBLIC/PROTECTED **인스턴스** 메서드 중 FINAL이 아닌 것. 불가: PRIVATE 메서드, 정적 메서드(CLASS-METHODS), 인스턴스·정적 생성자, FINAL 메서드.
**(2)** 시그니처(파라미터, 예외)와 가시성 섹션은 바꿀 수 없다. 원래 선언된 섹션에 `METHODS meth REDEFINITION.`으로 선언하고 구현만 바꾼다.
**(3)** `me->meth( )`는 객체의 동적 타입 기준으로 가장 아래의 재정의 구현을 호출한다(다형성). `super->meth( )`는 재정의한 메서드 안에서 바로 위 상위 클래스의 구현을 호출한다(정적으로 결정).
**(4)** 클래스 ABSTRACT: 인스턴스 생성 불가, 추상 메서드를 가질 수 있음. 클래스 FINAL: 상속 불가. 메서드 ABSTRACT: 구현 없음, 하위 클래스에서 반드시 재정의(추상 클래스 안에서만 선언). 메서드 FINAL: 재정의 불가. FINAL 클래스의 메서드는 모두 암묵적으로 FINAL이다.
**(5)** `[A] [DA] <A> [PDA] `. lcl_animal: describe → speak = `A` → `[A]`. lcl_dog: describe는 상속, 그 안의 `speak( )`는 동적 타입(lcl_dog) 구현 → `D` + super(`A`) = `DA` → `[DA]`. lcl_cat: describe 재정의, speak는 상속된 `A` → `<A>`. lcl_puppy: describe는 lcl_animal 구현, speak는 lcl_puppy 구현 → `P` + super(lcl_dog의 speak = `DA`) = `PDA` → `[PDA]`. 참조의 정적 타입은 모두 lcl_animal이지만 호출 구현은 동적 타입으로 정해지고, `super->`는 "바로 위 클래스의 구현"을 가리킨다. 상위 메서드 안에서 다른 메서드를 호출해도 동적 바인딩된다.
**(6)** 모범 답안:
```abap
CLASS lcl_ticket DEFINITION ABSTRACT.
  PUBLIC SECTION.
    METHODS price FINAL RETURNING VALUE(rv) TYPE i.
  PROTECTED SECTION.
    METHODS base_fare ABSTRACT RETURNING VALUE(rv) TYPE i.
    METHODS surcharge RETURNING VALUE(rv) TYPE i.
ENDCLASS.
CLASS lcl_ticket IMPLEMENTATION.
  METHOD price.
    rv = base_fare( ) + surcharge( ).
  ENDMETHOD.
  METHOD surcharge.
    rv = 0.
  ENDMETHOD.
ENDCLASS.

CLASS lcl_economy DEFINITION INHERITING FROM lcl_ticket.
  PROTECTED SECTION.
    METHODS base_fare REDEFINITION.
ENDCLASS.
CLASS lcl_economy IMPLEMENTATION.
  METHOD base_fare.
    rv = 100.
  ENDMETHOD.
ENDCLASS.

CLASS lcl_business DEFINITION INHERITING FROM lcl_ticket.
  PROTECTED SECTION.
    METHODS base_fare REDEFINITION.
    METHODS surcharge REDEFINITION.
ENDCLASS.
CLASS lcl_business IMPLEMENTATION.
  METHOD base_fare.
    rv = 300.
  ENDMETHOD.
  METHOD surcharge.
    rv = 50.
  ENDMETHOD.
ENDCLASS.

START-OF-SELECTION.
  DATA lt_tickets TYPE STANDARD TABLE OF REF TO lcl_ticket WITH EMPTY KEY.
  lt_tickets = VALUE #( ( NEW lcl_economy( ) ) ( NEW lcl_business( ) ) ).
  DATA(lv_total) = REDUCE i( INIT s = 0
                             FOR lo IN lt_tickets
                             NEXT s = s + lo->price( ) ).
  " lv_total = 450
```
REDUCE 대신 LOOP로 합산해도 된다.
**(7)** 템플릿 메서드 패턴: 알고리즘의 뼈대(price)는 상위 클래스에 FINAL로 고정하고, 달라지는 단계만 하위 클래스가 재정의한다. 재정의는 원래 선언된 섹션(여기서는 PROTECTED)에서 해야 한다.

</details>

---

### B-057. 인터페이스·추상 클래스·캐스팅: ALIASES·DEFAULT IGNORE/FAIL·업/다운캐스트·오류 찾기 [코드] ★★
<!-- src: OO-010, OO-011, OO-012, OO-014, HC-026 -->
(1) 추상 클래스와 인터페이스의 차이를 다섯 가지 이상 비교하고 각각 어떤 상황에서 쓰는지 쓰시오.
(2) 다음 코드 실행 후 lv_a1, lv_a2, lv_n, lv_msg 값을 쓰고 이유를 설명하시오.
```abap
INTERFACE lif_shape.
  METHODS area RETURNING VALUE(rv) TYPE i.
  METHODS name RETURNING VALUE(rv) TYPE string DEFAULT IGNORE.
  METHODS draw DEFAULT FAIL.
ENDINTERFACE.
CLASS lcl_square DEFINITION.
  PUBLIC SECTION.
    INTERFACES lif_shape.
    ALIASES area FOR lif_shape~area.
    METHODS constructor IMPORTING iv_side TYPE i.
  PRIVATE SECTION.
    DATA mv_side TYPE i.
ENDCLASS.
CLASS lcl_square IMPLEMENTATION.
  METHOD constructor.
    mv_side = iv_side.
  ENDMETHOD.
  METHOD lif_shape~area.
    rv = mv_side * mv_side.
  ENDMETHOD.
ENDCLASS.
START-OF-SELECTION.
  DATA lo_sq  TYPE REF TO lcl_square.
  DATA lo_if  TYPE REF TO lif_shape.
  DATA lv_msg TYPE string.
  lo_sq = NEW #( 3 ).
  lo_if = lo_sq.
  DATA(lv_a1) = lo_sq->area( ).
  DATA(lv_a2) = lo_if->area( ).
  DATA(lv_n)  = lo_if->name( ).
  TRY.
      lo_if->draw( ).
      lv_msg = `drawn`.
    CATCH cx_sy_dyn_call_illegal_method.
      lv_msg = `fail`.
  ENDTRY.
```
(3) 다음 코드의 문법 오류를 모두 찾아 고치시오. 구현을 하위 클래스로 미루는 방법은?
```abap
INTERFACE lif_payment.
  CONSTANTS c_max TYPE i VALUE 1000.
  METHODS pay    IMPORTING iv_amount TYPE i RETURNING VALUE(rv_ok) TYPE abap_bool.
  METHODS refund IMPORTING iv_amount TYPE i.
ENDINTERFACE.
CLASS lcl_card DEFINITION.
  PRIVATE SECTION.
    INTERFACES lif_payment.
ENDCLASS.
CLASS lcl_card IMPLEMENTATION.
  METHOD pay.
    rv_ok = xsdbool( iv_amount <= c_max ).
  ENDMETHOD.
ENDCLASS.
START-OF-SELECTION.
  DATA(lo_pay) = NEW lif_payment( ).
```
(4) B-056의 클래스(lcl_animal ← lcl_dog ← lcl_puppy)로 다음 코드를 실행한 뒤 lv_log 값을 쓰고 설명하시오.
```abap
DATA lo_a   TYPE REF TO lcl_animal.
DATA lo_d   TYPE REF TO lcl_dog.
DATA lv_log TYPE string.
lo_a = NEW lcl_dog( ).
IF lo_a IS INSTANCE OF lcl_dog.   lv_log = lv_log && `1`. ENDIF.
IF lo_a IS INSTANCE OF lcl_puppy. lv_log = lv_log && `2`. ENDIF.
TRY.
    DATA(lo_p) = CAST lcl_puppy( lo_a ).
    lv_log = lv_log && `3`.
  CATCH cx_sy_move_cast_error.
    lv_log = lv_log && `4`.
ENDTRY.
lo_d ?= lo_a.
lv_log = lv_log && `5`.
CLEAR lo_a.
IF lo_a IS INSTANCE OF lcl_animal. lv_log = lv_log && `6`. ENDIF.
TRY.
    lo_d ?= lo_a.
    lv_log = lv_log && `7`.
  CATCH cx_sy_move_cast_error.
    lv_log = lv_log && `8`.
ENDTRY.
IF lo_d IS BOUND. lv_log = lv_log && `9`. ENDIF.
```
(5) 다음 프로그램에서 문법 오류와 런타임 오류를 5개 이상 찾아 이유와 함께 고치시오.
```abap
REPORT zhc_bug_oo.
CLASS lcl_shape DEFINITION ABSTRACT.
  PUBLIC SECTION.
    METHODS constructor IMPORTING iv_name TYPE string.
    METHODS area ABSTRACT RETURNING VALUE(rv_area) TYPE f.
  PRIVATE SECTION.
    DATA mv_name TYPE string.
ENDCLASS.
CLASS lcl_shape IMPLEMENTATION.
  METHOD constructor.
    mv_name = iv_name.
  ENDMETHOD.
ENDCLASS.
CLASS lcl_circle DEFINITION INHERITING FROM lcl_shape.
  PUBLIC SECTION.
    METHODS constructor IMPORTING iv_r TYPE f.
    METHODS area RETURNING VALUE(rv_area) TYPE f.
  PRIVATE SECTION.
    DATA mv_r TYPE f.
ENDCLASS.
CLASS lcl_circle IMPLEMENTATION.
  METHOD constructor.
    mv_r = iv_r.
    super->constructor( iv_name = `Circle` ).
  ENDMETHOD.
  METHOD area.
    rv_area = '3.14159' * mv_r ** 2.
    WRITE: / mv_name, rv_area.
  ENDMETHOD.
ENDCLASS.
START-OF-SELECTION.
  DATA lo_shape  TYPE REF TO lcl_shape.
  DATA lo_circle TYPE REF TO lcl_circle.
  lo_shape  = NEW lcl_shape( iv_name = `X` ).
  lo_circle = lo_shape.
  DATA(lv_area) = lo_circle->area( ).
```

<details><summary>정답·해설</summary>

**(1)**

| 구분 | 추상 클래스 | 인터페이스 |
|---|---|---|
| 상속/구현 수 | 단일 상속 | 여러 인터페이스 구현 가능 |
| 구현 코드 | 일반 메서드 구현 포함 가능 | 선언만. DEFAULT IGNORE/FAIL로 선택 구현 지정 |
| 속성 | 인스턴스·정적 속성, 모든 가시성 | 모든 구성요소가 PUBLIC. 속성·상수·타입·이벤트 선언 |
| 생성자 | 가질 수 있음 | 없음 |
| 관계 의미 | "is-a"(공통 상태·동작 공유) | "can-do"(역할·계약) |
| 접근 | `oref->meth( )` | `oref->intf~meth( )`, 인터페이스 참조 `iref->meth( )`, ALIASES |

추상 클래스: 하위 클래스들이 공통 상태와 기본 구현을 공유하고 일부 단계만 다를 때(템플릿 메서드). 인터페이스: 관련 없는 클래스에 같은 계약을 부여할 때, 의존성 주입·테스트 더블로 교체할 때, 다중 역할이 필요할 때. "인터페이스에 의존하라(DIP)"는 ABAP Unit 테스트 더블과 바로 연결되고, RAP·BAdI도 인터페이스로 정의된다.
**(2)** lv_a1 = 9, lv_a2 = 9, lv_n = 빈 문자열(초기값), lv_msg = `fail`. `ALIASES`로 클래스 참조에서 `lo_sq->area( )`처럼 짧게 호출할 수 있고(원래는 `lo_sq->lif_shape~area( )`), 인터페이스 참조는 원래 이름으로 호출한다. `lo_if = lo_sq`는 업캐스트(항상 허용). `DEFAULT IGNORE` 메서드를 구현하지 않으면 빈 구현처럼 동작해 RETURNING은 초기값. `DEFAULT FAIL` 메서드를 구현하지 않고 호출하면 CX_SY_DYN_CALL_ILLEGAL_METHOD가 발생해 `drawn` 대입은 실행되지 않는다. DEFAULT 없는 메서드(area)는 반드시 구현해야 한다.
**(3)** ① `INTERFACES`는 PUBLIC SECTION에만 쓸 수 있다(구성요소가 모두 공개) ② 구현 메서드 이름은 `lif_payment~pay` ③ 인터페이스 상수는 `lif_payment=>c_max`(또는 ALIASES) ④ `refund` 구현 누락(DEFAULT IGNORE/FAIL이 아니면 모두 구현) ⑤ 인터페이스는 인스턴스를 만들 수 없다.
```abap
CLASS lcl_card DEFINITION.
  PUBLIC SECTION.
    INTERFACES lif_payment.
ENDCLASS.

CLASS lcl_card IMPLEMENTATION.
  METHOD lif_payment~pay.
    rv_ok = xsdbool( iv_amount <= lif_payment=>c_max ).
  ENDMETHOD.
  METHOD lif_payment~refund.
  ENDMETHOD.
ENDCLASS.

START-OF-SELECTION.
  DATA lo_pay TYPE REF TO lif_payment.
  lo_pay = NEW lcl_card( ).
```
쓰는 쪽은 구체 클래스를 몰라도 되도록 인터페이스 참조로 받는다. 구현을 하위 클래스에 미루려면 추상 클래스에서 `INTERFACES lif ABSTRACT METHODS refund.`를 쓴다.
**(4)** `14567`. `lo_a = NEW lcl_dog( )`는 업캐스트(정적 타입 lcl_animal, 동적 타입 lcl_dog). IS INSTANCE OF lcl_dog 참 → `1`, lcl_puppy 거짓. CAST lcl_puppy는 실행 시 동적 타입 검사에서 실패해 CX_SY_MOVE_CAST_ERROR → `4`. `lo_d ?= lo_a` 성공 → `5`. CLEAR 후 IS INSTANCE OF는 참조가 **초기값이면 정적 타입**(lcl_animal)으로 판단해 참 → `6`(초기 참조로 lcl_dog를 물으면 거짓). 초기 참조의 다운캐스트는 예외 없이 성공하고 대상도 초기값 → `7`, lo_d는 초기값이라 `9` 없음. `?=`와 `CAST type( )`는 같은 다운캐스트이며, 전에 `IS INSTANCE OF`나 `CASE TYPE OF`로 검사하면 예외를 피한다.
**(5)**

| # | 위치 | 문제 | 수정 |
|---|---|---|---|
| 1 | `lcl_circle`의 `METHODS area RETURNING ...` | 상속받은 메서드 재선언(문법 오류) | `METHODS area REDEFINITION.` |
| 2 | 하위 생성자의 `mv_r = iv_r.`가 super 호출 앞 | 상위 생성자 호출 전 인스턴스 컴포넌트 접근 불가(문법 오류) | `super->constructor( ... )`를 먼저 |
| 3 | `area`에서 `mv_name` | 상위의 PRIVATE 속성은 하위에서 보이지 않음(문법 오류) | PROTECTED로 옮기거나 getter |
| 4 | `NEW lcl_shape( ... )` | 추상 클래스 인스턴스화 불가(문법 오류) | `NEW lcl_circle( iv_r = 2 )` |
| 5 | `lo_circle = lo_shape.` | 다운캐스트는 `?=` 또는 `CAST` 필요(문법 오류), 실제 객체가 원이 아니면 실행 시 `CX_SY_MOVE_CAST_ERROR` | `lo_circle ?= lo_shape.`를 TRY/CATCH로, 또는 `IS INSTANCE OF` 확인 |
| 6 | `area` 안의 WRITE | 함수형 메서드에 출력 부작용(설계 문제, 감점) | 계산만 하고 출력은 호출부에서 |

```abap
CLASS lcl_shape DEFINITION ABSTRACT.
  PUBLIC SECTION.
    METHODS constructor IMPORTING iv_name TYPE string.
    METHODS area ABSTRACT RETURNING VALUE(rv_area) TYPE f.
    METHODS get_name RETURNING VALUE(rv_name) TYPE string.
  PROTECTED SECTION.
    DATA mv_name TYPE string.
ENDCLASS.

CLASS lcl_shape IMPLEMENTATION.
  METHOD constructor.
    mv_name = iv_name.
  ENDMETHOD.
  METHOD get_name.
    rv_name = mv_name.
  ENDMETHOD.
ENDCLASS.

CLASS lcl_circle DEFINITION INHERITING FROM lcl_shape.
  PUBLIC SECTION.
    METHODS constructor IMPORTING iv_r TYPE f.
    METHODS area REDEFINITION.
  PRIVATE SECTION.
    DATA mv_r TYPE f.
ENDCLASS.

CLASS lcl_circle IMPLEMENTATION.
  METHOD constructor.
    super->constructor( iv_name = `Circle` ).
    mv_r = iv_r.
  ENDMETHOD.
  METHOD area.
    rv_area = '3.14159' * mv_r ** 2.
  ENDMETHOD.
ENDCLASS.

START-OF-SELECTION.
  DATA lo_shape TYPE REF TO lcl_shape.
  lo_shape = NEW lcl_circle( iv_r = 2 ).            " 업캐스트
  IF lo_shape IS INSTANCE OF lcl_circle.
    DATA(lo_circle) = CAST lcl_circle( lo_shape ).   " 다운캐스트
  ENDIF.
  DATA(lv_area) = lo_shape->area( ).                " 다형 호출만으로 충분
  DATA(lv_name) = lo_shape->get_name( ).
  WRITE: / lv_name, lv_area.
```
채점 기준((5)): 1~5 각 18점, 6 지적 10점. "super 먼저", "다운캐스트는 `?=`/CAST", "추상 클래스 인스턴스화 불가", "private은 상속되어도 접근 불가"가 OO 손코딩 오류 문제의 단골이다.

</details>

---

### B-058. 이벤트(EVENTS·RAISE EVENT·SET HANDLER)와 FRIENDS [코드] ★★
<!-- src: OO-015, OO-016, OO-017 -->
남은 좌석이 3석 미만이 되면 이벤트를 발생시키고 모니터 객체가 처리하는 코드다.

```abap
CLASS lcl_flight DEFINITION.
  PUBLIC SECTION.
    ____(a)____ seats_low EXPORTING VALUE(ev_free) TYPE i.
    METHODS book IMPORTING iv_seats TYPE i.
  PRIVATE SECTION.
    DATA mv_free TYPE i VALUE 5.
ENDCLASS.
CLASS lcl_flight IMPLEMENTATION.
  METHOD book.
    mv_free = mv_free - iv_seats.
    IF mv_free < 3.
      ____(b)____ seats_low EXPORTING ev_free = mv_free.
    ENDIF.
  ENDMETHOD.
ENDCLASS.
CLASS lcl_monitor DEFINITION.
  PUBLIC SECTION.
    METHODS on_seats_low ____(c)____ seats_low OF lcl_flight
      IMPORTING ev_free ____(d)____.
ENDCLASS.
CLASS lcl_monitor IMPLEMENTATION.
  METHOD on_seats_low.
    MESSAGE |Only { ev_free } seats left| TYPE 'I'.
  ENDMETHOD.
ENDCLASS.
START-OF-SELECTION.
  DATA(lo_flight) = NEW lcl_flight( ).
  DATA(lo_mon)    = NEW lcl_monitor( ).
  ____(e)____ lo_mon->on_seats_low FOR lo_flight.
  lo_flight->book( 3 ).
```

(1) 빈칸 (a)~(e)를 채우시오. 이후 생성되는 lcl_flight 객체까지 모두 처리하려면 `FOR lo_flight`를 무엇으로 바꾸는가?
(2) 이벤트 파라미터의 제약, 암묵 파라미터 `sender`, 정적 이벤트의 선언·등록, 등록 해제 방법, 핸들러가 없을 때의 RAISE EVENT 동작을 쓰시오.
(3) 다음 코드에서 각 `fire` 호출 때 실행되는 핸들러(수신자 이름과 iv_no)를 쓰시오(한 fire 안의 실행 순서는 묻지 않음).
```abap
CLASS lcl_sender DEFINITION.
  PUBLIC SECTION.
    EVENTS ping EXPORTING VALUE(iv_no) TYPE i.
    METHODS fire IMPORTING iv_no TYPE i.
ENDCLASS.
CLASS lcl_sender IMPLEMENTATION.
  METHOD fire.
    RAISE EVENT ping EXPORTING iv_no = iv_no.
  ENDMETHOD.
ENDCLASS.
CLASS lcl_recv DEFINITION.
  PUBLIC SECTION.
    CLASS-DATA log TYPE string.
    METHODS constructor IMPORTING iv_name TYPE string.
    METHODS on_ping FOR EVENT ping OF lcl_sender IMPORTING iv_no.
  PRIVATE SECTION.
    DATA mv_name TYPE string.
ENDCLASS.
CLASS lcl_recv IMPLEMENTATION.
  METHOD constructor.
    mv_name = iv_name.
  ENDMETHOD.
  METHOD on_ping.
    log = |{ log }{ mv_name }:{ iv_no } |.
  ENDMETHOD.
ENDCLASS.
START-OF-SELECTION.
  DATA(s1) = NEW lcl_sender( ).
  DATA(s2) = NEW lcl_sender( ).
  DATA(r1) = NEW lcl_recv( `R1` ).
  DATA(r2) = NEW lcl_recv( `R2` ).
  SET HANDLER r1->on_ping FOR s1.
  SET HANDLER r2->on_ping FOR ALL INSTANCES.
  s1->fire( 1 ).                                    " (가)
  s2->fire( 2 ).                                    " (나)
  SET HANDLER r1->on_ping FOR s1 ACTIVATION abap_false.
  s1->fire( 3 ).                                    " (다)
  DATA(s3) = NEW lcl_sender( ).
  s3->fire( 4 ).                                    " (라)
```
(4) 특정 인스턴스에 핸들러를 등록했을 때 가비지 컬렉션과의 관계를 쓰시오.
(5) `CLASS a DEFINITION ... FRIENDS b.`의 의미를 쓰고, 다음이 맞는지 판단하시오. (가) a가 b에게 우정을 주면 b도 a에게 우정을 준다. (나) b의 하위 클래스도 a의 PRIVATE 구성요소에 접근할 수 있다. (다) a의 하위 클래스도 자동으로 b에게 우정을 준다.
(6) ABAP Unit에서 FRIENDS를 쓰는 대표적인 경우와, GLOBAL/LOCAL FRIENDS의 구분을 쓰시오.

<details><summary>정답·해설</summary>

**(1)** (a) `EVENTS` (b) `RAISE EVENT` (c) `FOR EVENT` (d) `sender` (e) `SET HANDLER`. 모든 인스턴스: `FOR ALL INSTANCES`.
**(2)** 이벤트 파라미터는 EXPORTING만 가능하고 반드시 값 전달(VALUE)이다. 핸들러는 IMPORTING으로 받고, 암묵 파라미터 `sender`로 이벤트를 발생시킨 객체의 참조를 받을 수 있다. 정적 이벤트는 `CLASS-EVENTS`로 선언하고 `SET HANDLER h`(FOR 없이)로 등록한다. 해제는 `SET HANDLER ... ACTIVATION abap_false`. 핸들러가 등록되지 않았으면 RAISE EVENT는 아무 일도 하지 않는다.
**(3)** (가) R1:1, R2:1 (나) R2:2 (다) R2:3 (라) R2:4. r1은 s1에만 등록되어 s1 이벤트만 받는다. r2는 `FOR ALL INSTANCES`로 등록 시점 이후 생성된 객체(s3)를 포함해 lcl_sender의 모든 인스턴스 이벤트를 받는다. `ACTIVATION abap_false`로 r1의 s1 등록을 해제해 (다)에서는 r2만 실행된다.
**(4)** 핸들러 테이블이 발신 객체를 참조하므로, 특정 인스턴스에 등록하면 등록이 남아 있는 동안 그 발신 객체는 가비지 컬렉션 대상이 아니다.
**(5)** a가 b(클래스 또는 인터페이스)에게 a의 PROTECTED·PRIVATE 구성요소 접근과, CREATE PRIVATE/PROTECTED여도 인스턴스 생성을 허용한다. (가) 틀림: 우정은 일방향. (나) 맞음: 친구 클래스의 하위 클래스도 친구가 된다(친구 인터페이스를 포함하는 인터페이스도). (다) 틀림: 우정을 "주는 것"은 상속되지 않아 a의 하위 클래스는 별도로 FRIENDS를 선언해야 한다.
**(6)** 전역 클래스의 테스트 include에서 `CLASS zcl_cut DEFINITION LOCAL FRIENDS ltc_test.`로 테스트 클래스가 PRIVATE 메서드·속성(의존 객체 교체, back-door injection)에 접근할 때. 전역 클래스는 `GLOBAL FRIENDS`, 로컬 클래스는 `FRIENDS`, 클래스 풀 안의 로컬 클래스에게는 `LOCAL FRIENDS`. 우정은 캡슐화를 깨므로 테스트·팩토리처럼 꼭 필요한 곳에만 쓴다.

</details>

---

### B-059. SOLID·디자인 패턴·팩토리와 항공권 요금 계산 종합 작성 [작성] ★★★
<!-- src: OO-018, OO-013, HC-024 -->
(1) SOLID 다섯 원칙을 각각 한 줄로 설명하고 ABAP 적용 예를 하나씩 드시오.
(2) 싱글톤, 팩토리, 전략(Strategy) 패턴을 ABAP 문법 요소(CREATE PRIVATE, 정적 메서드, 인터페이스)와 연결해 설명하시오.
(3) 인터페이스 `lif_discount`(메서드 `apply`: IMPORTING iv_price TYPE i, RETURNING i), 구현 클래스 `lcl_disc_none`(할인 없음)과 `lcl_disc_student`(20% 할인, DIV 사용), 팩토리 `lcl_disc_factory=>create`(IMPORTING iv_type TYPE string, RETURNING REF TO lif_discount: `STUDENT`면 학생 할인, 그 외 할인 없음)를 작성하고, 학생 할인으로 1000을 계산(800)하는 사용 예를 쓰시오.
(4) (3)이 개방-폐쇄 원칙을 지키는 이유와, `ro = NEW lcl_disc_student( )`가 허용되는 이유를 쓰시오.
(5) 실행 프로그램 `ZHC_OO_TICKET` 안에 로컬 클래스로 다음을 구현하시오. 인터페이스 `lif_priceable`: `get_price`(RETURNING TYPE s_price), `get_description`(RETURNING string). 추상 클래스 `lcl_ticket`: 인터페이스 구현, 생성자(`iv_base`, `iv_pass`), `get_price`는 추상, `get_description`은 "승객명: 등급명 가격"을 돌려주되 등급명은 보호 추상 메서드 `get_class_text`로 얻음(템플릿 메서드). 하위 클래스 `lcl_economy`(기본 운임), `lcl_business`(× 2 + 100), `lcl_first`(× 4). 정적 팩토리 `lcl_ticket=>create( iv_class iv_base iv_pass )`: Y/C/F, 그 외는 사용자 예외 `lcx_invalid_class`(정적 검사 예외, 잘못된 등급 값을 속성으로, 텍스트에 포함). 메인: (Y, 500, KIM), (C, 500, LEE), (X, 500, PARK), (F, 500, CHOI)를 처리해 성공한 설명과 합계, 실패는 예외 텍스트 출력.
(6) (5)의 출력 결과를 순서대로 쓰시오.
(7) (5)에서 하위 클래스가 생성자를 정의하지 않을 때의 NEW 문법, `INTERFACES ... ABSTRACT METHODS`의 용도, 예외 텍스트의 표준 방식, cx_static_check를 RAISING에 선언하지 않을 때를 쓰시오.

<details><summary>정답·해설</summary>

**(1)**

| 원칙 | 의미 | ABAP 예 |
|---|---|---|
| S 단일 책임 | 클래스는 하나의 변경 이유만 | DB 접근(DAO), 업무 규칙, 출력(ALV)을 다른 클래스로 |
| O 개방-폐쇄 | 확장에 열리고 수정에 닫힘 | 새 할인 유형은 새 구현 클래스 추가로, BAdI |
| L 리스코프 치환 | 하위 타입은 상위 타입 자리에 그대로 쓸 수 있어야 함 | 재정의 메서드가 상위의 계약(사전·사후 조건, 예외)을 깨지 않음 |
| I 인터페이스 분리 | 쓰지 않는 메서드에 의존하지 않게 작은 인터페이스로 | 읽기용 lif_reader와 쓰기용 lif_writer 분리 |
| D 의존성 역전 | 구체 클래스가 아닌 추상에 의존 | 서비스 클래스가 lif_flight_dao를 생성자로 주입받음(테스트 더블 교체 가능) |

**(2)** **싱글톤**: CREATE PRIVATE + 정적 속성 + get_instance 정적 메서드. **팩토리**: 정적 메서드(또는 팩토리 클래스)가 조건에 따라 구체 클래스를 생성해 인터페이스 참조로 반환, 생성자를 CREATE PRIVATE로 막고 팩토리만 허용하기도 한다. **전략**: 알고리즘을 인터페이스로 정의하고 실행 시 구현 객체를 바꿔 끼움(가격 계산 전략을 파라미터·생성자로 주입). 면접에서는 "DAO 분리와 인터페이스 주입으로 ABAP Unit 테스트가 가능해졌다"처럼 실무와 연결하면 좋다.
**(3)**
```abap
INTERFACE lif_discount.
  METHODS apply IMPORTING iv_price TYPE i RETURNING VALUE(rv) TYPE i.
ENDINTERFACE.

CLASS lcl_disc_none DEFINITION.
  PUBLIC SECTION.
    INTERFACES lif_discount.
ENDCLASS.
CLASS lcl_disc_none IMPLEMENTATION.
  METHOD lif_discount~apply.
    rv = iv_price.
  ENDMETHOD.
ENDCLASS.

CLASS lcl_disc_student DEFINITION.
  PUBLIC SECTION.
    INTERFACES lif_discount.
ENDCLASS.
CLASS lcl_disc_student IMPLEMENTATION.
  METHOD lif_discount~apply.
    rv = iv_price - iv_price * 20 DIV 100.
  ENDMETHOD.
ENDCLASS.

CLASS lcl_disc_factory DEFINITION.
  PUBLIC SECTION.
    CLASS-METHODS create IMPORTING iv_type TYPE string
                         RETURNING VALUE(ro) TYPE REF TO lif_discount.
ENDCLASS.
CLASS lcl_disc_factory IMPLEMENTATION.
  METHOD create.
    CASE iv_type.
      WHEN `STUDENT`.
        ro = NEW lcl_disc_student( ).
      WHEN OTHERS.
        ro = NEW lcl_disc_none( ).
    ENDCASE.
  ENDMETHOD.
ENDCLASS.

START-OF-SELECTION.
  DATA(lo_disc) = lcl_disc_factory=>create( `STUDENT` ).
  DATA(lv_price) = lo_disc->apply( 1000 ).     " 800
```
`iv_price * 20 DIV 100` = 20000 DIV 100 = 200.
**(4)** 호출자는 lif_discount만 알고 구체 클래스 선택은 팩토리가 맡으므로, 새 할인 유형을 추가해도 호출 코드를 바꾸지 않는다. `ro = NEW lcl_disc_student( )`는 구현 클래스 참조를 인터페이스 참조에 넣는 업캐스트라 항상 허용된다.
**(5)** 모범 답안:
```abap
REPORT zhc_oo_ticket.

*--- 사용자 예외 -------------------------------------------------------
CLASS lcx_invalid_class DEFINITION INHERITING FROM cx_static_check.
  PUBLIC SECTION.
    DATA mv_class TYPE s_class READ-ONLY.
    METHODS constructor
      IMPORTING iv_class  TYPE s_class OPTIONAL
                previous  LIKE previous OPTIONAL.
    METHODS if_message~get_text REDEFINITION.
ENDCLASS.

CLASS lcx_invalid_class IMPLEMENTATION.
  METHOD constructor.
    super->constructor( previous = previous ).
    mv_class = iv_class.
  ENDMETHOD.
  METHOD if_message~get_text.
    result = |좌석 등급 '{ mv_class }'은(는) 지원하지 않습니다|.
  ENDMETHOD.
ENDCLASS.

*--- 인터페이스 ---------------------------------------------------------
INTERFACE lif_priceable.
  METHODS get_price       RETURNING VALUE(rv_price) TYPE s_price.
  METHODS get_description RETURNING VALUE(rv_text)  TYPE string.
ENDINTERFACE.

*--- 추상 상위 클래스 ---------------------------------------------------
CLASS lcl_ticket DEFINITION ABSTRACT.
  PUBLIC SECTION.
    INTERFACES lif_priceable ABSTRACT METHODS get_price.
    ALIASES: get_price       FOR lif_priceable~get_price,
             get_description FOR lif_priceable~get_description.
    METHODS constructor
      IMPORTING iv_base TYPE s_price
                iv_pass TYPE s_passname.
    CLASS-METHODS create
      IMPORTING iv_class         TYPE s_class
                iv_base          TYPE s_price
                iv_pass          TYPE s_passname
      RETURNING VALUE(ro_ticket) TYPE REF TO lcl_ticket
      RAISING   lcx_invalid_class.
  PROTECTED SECTION.
    DATA: mv_base TYPE s_price,
          mv_pass TYPE s_passname.
    METHODS get_class_text ABSTRACT RETURNING VALUE(rv_text) TYPE string.
ENDCLASS.

CLASS lcl_economy DEFINITION INHERITING FROM lcl_ticket.
  PUBLIC SECTION.
    METHODS lif_priceable~get_price REDEFINITION.
  PROTECTED SECTION.
    METHODS get_class_text REDEFINITION.
ENDCLASS.

CLASS lcl_business DEFINITION INHERITING FROM lcl_ticket.
  PUBLIC SECTION.
    METHODS lif_priceable~get_price REDEFINITION.
  PROTECTED SECTION.
    METHODS get_class_text REDEFINITION.
ENDCLASS.

CLASS lcl_first DEFINITION INHERITING FROM lcl_ticket.
  PUBLIC SECTION.
    METHODS lif_priceable~get_price REDEFINITION.
  PROTECTED SECTION.
    METHODS get_class_text REDEFINITION.
ENDCLASS.

*--- 구현 ---------------------------------------------------------------
CLASS lcl_ticket IMPLEMENTATION.
  METHOD constructor.
    mv_base = iv_base.
    mv_pass = iv_pass.
  ENDMETHOD.

  METHOD create.
    CASE iv_class.
      WHEN 'Y'.
        ro_ticket = NEW lcl_economy( iv_base = iv_base iv_pass = iv_pass ).
      WHEN 'C'.
        ro_ticket = NEW lcl_business( iv_base = iv_base iv_pass = iv_pass ).
      WHEN 'F'.
        ro_ticket = NEW lcl_first( iv_base = iv_base iv_pass = iv_pass ).
      WHEN OTHERS.
        RAISE EXCEPTION NEW lcx_invalid_class( iv_class = iv_class ).
    ENDCASE.
  ENDMETHOD.

  METHOD lif_priceable~get_description.       " 템플릿 메서드
    rv_text = |{ mv_pass }: { get_class_text( ) } { get_price( ) }|.
  ENDMETHOD.
ENDCLASS.

CLASS lcl_economy IMPLEMENTATION.
  METHOD lif_priceable~get_price.
    rv_price = mv_base.
  ENDMETHOD.
  METHOD get_class_text.
    rv_text = `Economy`.
  ENDMETHOD.
ENDCLASS.

CLASS lcl_business IMPLEMENTATION.
  METHOD lif_priceable~get_price.
    rv_price = mv_base * 2 + 100.
  ENDMETHOD.
  METHOD get_class_text.
    rv_text = `Business`.
  ENDMETHOD.
ENDCLASS.

CLASS lcl_first IMPLEMENTATION.
  METHOD lif_priceable~get_price.
    rv_price = mv_base * 4.
  ENDMETHOD.
  METHOD get_class_text.
    rv_text = `First`.
  ENDMETHOD.
ENDCLASS.

*--- 메인 ---------------------------------------------------------------
TYPES: BEGIN OF ty_req,
         class TYPE s_class,
         base  TYPE s_price,
         pass  TYPE s_passname,
       END OF ty_req.

START-OF-SELECTION.
  DATA: lt_tickets TYPE STANDARD TABLE OF REF TO lif_priceable WITH EMPTY KEY,
        lv_total   TYPE s_price.

  DATA(lt_req) = VALUE STANDARD TABLE OF ty_req WITH EMPTY KEY(
                   ( class = 'Y' base = 500 pass = 'KIM' )
                   ( class = 'C' base = 500 pass = 'LEE' )
                   ( class = 'X' base = 500 pass = 'PARK' )
                   ( class = 'F' base = 500 pass = 'CHOI' ) ).

  LOOP AT lt_req INTO DATA(ls_req).
    TRY.
        DATA(lo_ticket) = lcl_ticket=>create( iv_class = ls_req-class
                                              iv_base  = ls_req-base
                                              iv_pass  = ls_req-pass ).
        APPEND lo_ticket TO lt_tickets.        " 업캐스트(lcl_ticket → lif_priceable)
      CATCH lcx_invalid_class INTO DATA(lx_class).
        DATA(lv_err) = lx_class->get_text( ).
        WRITE: / '오류:', lv_err.
    ENDTRY.
  ENDLOOP.

  LOOP AT lt_tickets INTO DATA(lo_item).
    DATA(lv_desc) = lo_item->get_description( ).   " 다형성
    WRITE / lv_desc.
    lv_total = lv_total + lo_item->get_price( ).
  ENDLOOP.
  ULINE.
  WRITE: / '합계:', lv_total.
```

채점 기준(100점, (5)):

| 항목 | 배점 |
|---|---|
| 예외 클래스(INHERITING FROM cx_static_check, 속성, 생성자 super 호출, 텍스트) | 15 |
| 인터페이스 정의 | 5 |
| 추상 클래스: INTERFACES ... ABSTRACT METHODS, ALIASES, 생성자, 보호 추상 메서드 | 20 |
| 하위 클래스: REDEFINITION 선언·구현 3개 | 15 |
| 정적 팩토리: CASE + NEW + RAISE EXCEPTION, RAISING 선언 | 15 |
| 템플릿 메서드 get_description | 10 |
| 메인: TRY/CATCH, 인터페이스 참조 테이블에 업캐스트, 다형 호출, 합계 | 20 |

**(6)** `오류: 좌석 등급 'X'은(는) 지원하지 않습니다` / `KIM: Economy 500.00` / `LEE: Business 1100.00` / `CHOI: First 2000.00` / 합계 3600.00. 문자열 템플릿에서 p 타입 가격은 `500.00`처럼 소수 2자리로 출력된다(s_price는 CURR 15,2).
**(7)** 하위 클래스가 생성자를 정의하지 않으면 상위 생성자 시그니처를 물려받아 `NEW lcl_economy( iv_base = ... iv_pass = ... )`가 된다. 추상 클래스에서 인터페이스 메서드를 구현하지 않고 넘기려면 `INTERFACES ... ABSTRACT METHODS`를 쓰고, 하위 클래스는 `METHODS lif_priceable~get_price REDEFINITION`으로 구현한다. 예외 텍스트는 여기서 `if_message~get_text`를 재정의했지만 실무 표준은 `IF_T100_MESSAGE`(메시지 클래스)나 `IF_T100_DYN_MSG` 구현이며 그렇게 써도 만점. `cx_static_check` 하위 예외는 처리하지도 RAISING에 선언하지도 않으면 문법 검사 경고가 나므로, 호출 측이 반드시 처리해야 하는 업무 오류에 알맞다.

</details>

---

## 예외 처리

### B-060. 예외 범주·TRY/CATCH/CLEANUP·RETRY/RESUME·클래식 예외 비교 [코드] ★★★
<!-- src: OO-019, OO-020, OO-021, OO-022, OO-027, OO-026 -->
(1) CX_STATIC_CHECK, CX_DYNAMIC_CHECK, CX_NO_CHECK를 컴파일 검사, RAISING 선언, 처리·선언하지 않았을 때 동작, 대표 예로 비교하시오. 업무 오류용 Z 예외 클래스는 보통 무엇을 상속하는가? 세 클래스의 공통 상위 클래스는?
(2) 다음 코드 실행 후 lv_log를 쓰시오. `lv_num` 초기값을 0으로 바꾸면? (원래 코드에서) 안쪽 `CATCH cx_sy_conversion_error`를 `CATCH cx_sy_zerodivide`로 바꾸면? (cx_sy_zerodivide는 cx_sy_arithmetic_error의 하위 클래스이고 cx_sy_conversion_error와는 관계없다.)
```abap
DATA: lv_num TYPE i VALUE 1, lv_zero TYPE i VALUE 0, lv_res TYPE i, lv_log TYPE string.
TRY.
    lv_log = lv_log && `1`.
    TRY.
        lv_log = lv_log && `2`.
        lv_res = lv_num / lv_zero.
        lv_log = lv_log && `3`.
      CATCH cx_sy_conversion_error.
        lv_log = lv_log && `4`.
      CLEANUP.
        lv_log = lv_log && `5`.
    ENDTRY.
    lv_log = lv_log && `6`.
  CATCH cx_sy_arithmetic_error INTO DATA(lx).
    lv_log = lv_log && `7`.
ENDTRY.
lv_log = lv_log && `8`.
```
(3) (가), (나)의 결과를 쓰고 RESUME의 조건을 쓰시오.
```abap
" (가)
DATA: lv_div TYPE i VALUE 0, lv_cnt TYPE i, lv_res TYPE i.
TRY.
    lv_cnt = lv_cnt + 1.
    lv_res = 12 / lv_div.
  CATCH cx_sy_zerodivide.
    lv_div = lv_div + 4.
    RETRY.
ENDTRY.
" lv_cnt, lv_res, lv_div 는?

" (나)
CLASS lcx_warn DEFINITION INHERITING FROM cx_static_check.
ENDCLASS.
CLASS lcx_warn IMPLEMENTATION.
ENDCLASS.
CLASS lcl_proc DEFINITION.
  PUBLIC SECTION.
    CLASS-DATA log TYPE string.
    CLASS-METHODS run RAISING RESUMABLE(lcx_warn).
ENDCLASS.
CLASS lcl_proc IMPLEMENTATION.
  METHOD run.
    log = log && `a`.
    RAISE RESUMABLE EXCEPTION TYPE lcx_warn.
    log = log && `b`.
  ENDMETHOD.
ENDCLASS.
START-OF-SELECTION.
  TRY.
      lcl_proc=>run( ).
      lcl_proc=>log = lcl_proc=>log && `c`.
    CATCH BEFORE UNWIND lcx_warn INTO DATA(lx).
      lcl_proc=>log = lcl_proc=>log && `d`.
      IF lx->is_resumable = abap_true.
        RESUME.
      ENDIF.
  ENDTRY.
  lcl_proc=>log = lcl_proc=>log && `e`.
  " lcl_proc=>log 는?
```
(4) 다음 코드에서 잘못된 곳 (가)~(라)의 이유를 쓰고 고치시오.
```abap
CLASS lcx_not_found DEFINITION INHERITING FROM cx_static_check.
ENDCLASS.
CLASS lcx_not_found IMPLEMENTATION.
ENDCLASS.
CLASS lcl_dao DEFINITION.
  PUBLIC SECTION.
    METHODS read_flight IMPORTING iv_carrid TYPE s_carr_id
                        RETURNING VALUE(rs) TYPE sflight
                        RAISING   lcx_not_found.
ENDCLASS.
CLASS lcl_dao IMPLEMENTATION.
  METHOD read_flight.
    SELECT SINGLE * FROM sflight WHERE carrid = @iv_carrid INTO @rs.
    IF sy-subrc <> 0.
      RAISE EXCEPTION NEW cx_static_check( ).                 " (가)
    ENDIF.
  ENDMETHOD.
ENDCLASS.
START-OF-SELECTION.
  DATA: lv_a TYPE i VALUE 10, lv_b TYPE i, lv_res TYPE i.
  DATA(lo_dao) = NEW lcl_dao( ).
  TRY.
      lv_res = lv_a / lv_b.
      DATA(ls_flight) = lo_dao->read_flight( 'LH' ).
    CATCH cx_root INTO DATA(lx_root).                         " (나)
      MESSAGE lx_root->get_text( ) TYPE 'I'.
    CATCH cx_sy_zerodivide.
      RETRY.                                                  " (다)
    CLEANUP.
      RETURN.                                                 " (라)
  ENDTRY.
```
(5) 옳지 **않은** 것을 고르시오. ① CLEANUP은 TRY에서 발생한 예외가 그 TRY에서 처리되지 않고 바깥 TRY에서 처리될 때 실행된다. ② RETRY는 CATCH 블록에서만 쓸 수 있으며 TRY 블록 전체를 다시 실행한다. ③ RESUME을 쓰려면 예외가 RESUMABLE로 발생하고 `CATCH BEFORE UNWIND`로 잡아야 한다. ④ CATCH가 여럿이면 위에서부터 처음 일치하는 하나만 실행된다. ⑤ CLEANUP 안에서는 `RETURN`으로 메서드를 바로 끝낼 수 있다.
(6) 클래식 예외(EXCEPTIONS)와 클래스 기반 예외(RAISING)를 발생, 처리, 전파, 정보, 상속 측면에서 비교하시오. 한 시그니처에 둘을 함께 선언할 수 있는가? `error_message`와 `CATCH SYSTEM-EXCEPTIONS`는?

<details><summary>정답·해설</summary>

**(1)**

| 범주 | 컴파일 검사 | RAISING 선언 | 처리·선언 안 했을 때 | 예 |
|---|---|---|---|---|
| CX_STATIC_CHECK | 함(처리도 선언도 안 하면 문법 검사 경고) | 처리하지 않으면 선언해야 함 | 선언 없이 밖으로 전파되면 CX_SY_NO_HANDLER | 업무 예외(데이터 없음, 검증 실패), CX_SALV_MSG |
| CX_DYNAMIC_CHECK | 안 함 | 전파하려면 선언해야 함(실행 시 검사) | 선언 없이 전파되면 CX_SY_NO_HANDLER | CX_SY_ZERODIVIDE, CX_SY_CONVERSION_NO_NUMBER, CX_SY_ITAB_LINE_NOT_FOUND 등 대부분의 CX_SY_ |
| CX_NO_CHECK | 안 함 | 불필요(모든 인터페이스에 암묵 선언) | 그대로 전파, 끝까지 안 잡히면 런타임 오류 | 메모리 부족 같은 시스템 상태 |

업무 오류용 Z 예외는 호출자가 처리를 잊지 않도록 **CX_STATIC_CHECK** 상속이 기본 권장이다. 세 클래스 모두 CX_ROOT의 하위 클래스이며 CX_ROOT를 직접 상속할 수는 없다. CX_SY_NO_HANDLER의 previous에 원래 예외가 들어 있다. CX_DYNAMIC_CHECK는 호출자가 사전 조건 검사로 피할 수 있는 오류(0으로 나누기 등)에 쓴다.
**(2)** `12578` / `12368` / `12468`. 원래 코드: 1 → 2 → 1/0에서 CX_SY_ZERODIVIDE, 안쪽 CATCH(conversion)는 해당 없음 → 예외가 안쪽 TRY를 벗어나 바깥에서 잡히므로 **벗어나기 전에 안쪽 CLEANUP**(5) → 바깥 CATCH arithmetic_error(7, 상위 클래스로 잡힘) → 8. 3과 6은 건너뜀. 피제수 0: ABAP 정수 나눗셈은 0/0이 예외 없이 0 → 1, 2, 3, 6, 8. zerodivide로 바꾸면 안쪽에서 직접 잡아 CLEANUP은 실행되지 않음(4) → 6 → 8. CLEANUP은 "현재 TRY에서 처리되지 않고 바깥으로 나가는 예외"일 때만 실행된다.
**(3)** (가) lv_cnt = 2, lv_res = 3, lv_div = 4: 1회차 12/0 → CATCH에서 div = 4, `RETRY`는 **TRY 블록 전체를 처음부터** 다시 실행 → 2회차 12/4 = 3. 원인을 없애지 않고 RETRY하면 무한 루프. (나) `adbce`: run에서 `a` → RAISE RESUMABLE → `CATCH BEFORE UNWIND`는 호출 스택을 풀기 전에 실행되어 run 문맥이 살아 있음 → `d` → `RESUME`은 예외 발생 다음 문장으로 → `b` → run 정상 종료 → `c` → `e`. RESUME 조건: `RAISE RESUMABLE EXCEPTION`(또는 `THROW RESUMABLE`)으로 발생, 시그니처에 `RAISING RESUMABLE(...)`, 처리 쪽은 `CATCH BEFORE UNWIND`. RESUME하면 CLEANUP은 실행되지 않고, 일반 `CATCH`에서는 RESUME할 수 없다.
**(4)** (가) CX_STATIC_CHECK는 추상 클래스라 인스턴스 불가(문법 오류)이고 선언한 예외를 던져야 함 → `RAISE EXCEPTION NEW lcx_not_found( ).` (나) CX_ROOT를 먼저 잡으면 아래 `CATCH cx_sy_zerodivide`에 도달할 수 없어 문법 오류 → 구체적인 하위 클래스를 먼저, CX_ROOT는 마지막(가능하면 필요한 예외만). (다) lv_b를 바꾸지 않고 RETRY하면 무한 루프 → 원인을 없앤 뒤 RETRY하거나 쓰지 않음. (라) CLEANUP은 끝까지 실행되어야 하며 RETURN으로 빠져나갈 수 없음 → 정리 코드만 둔다.
```abap
  TRY.
      lv_res = lv_a / lv_b.
      DATA(ls_flight) = lo_dao->read_flight( 'LH' ).
    CATCH cx_sy_zerodivide.
      lv_res = 0.
    CATCH lcx_not_found INTO DATA(lx_nf).
      MESSAGE lx_nf->get_text( ) TYPE 'I'.
  ENDTRY.
```
CATCH 한 줄에 여러 예외를 나열할 수 있고(`CATCH cx_a cx_b INTO DATA(lx).`) INTO 변수 타입은 공통 상위 클래스가 된다.
**(5)** **⑤**. CLEANUP은 정리 작업을 끝까지 해야 하므로 RETURN 등으로 빠져나갈 수 없고, 그 안에서 발생한 예외도 그 안에서 처리해야 한다. `CLEANUP INTO oref`로 예외 객체를 받을 수 있다.
**(6)**

| 구분 | 클래식 예외(EXCEPTIONS) | 클래스 기반 예외(RAISING) |
|---|---|---|
| 발생 | `RAISE not_found.` 또는 `MESSAGE e001(zmsg) RAISING not_found.` | `RAISE EXCEPTION TYPE/NEW cx...`, `THROW` |
| 처리 | `EXCEPTIONS not_found = 1 OTHERS = 2` 후 sy-subrc 검사 | `TRY ... CATCH ... ENDTRY` |
| 전파 | 직접 호출자에게만. 호출자가 EXCEPTIONS를 안 쓰면 런타임 오류(MESSAGE ... RAISING이면 메시지 출력) | 처리될 때까지 호출 스택을 따라 자동 전파(선언 규칙에 따라) |
| 정보 | 이름과 sy-subrc, sy-msg* 정도 | 객체: 속성, get_text, previous 체인, get_source_position |
| 상속 | 없음 | 상위 클래스 하나로 묶어 잡기 가능 |

한 메서드(또는 FM) 시그니처에 둘을 함께 선언할 수 없다. 클래식 FM 호출 시 `error_message = n`으로 FM 안의 E/A 메시지를 sy-subrc로 받을 수 있다. BAPI처럼 RFC로 호출되는 FM은 클래식 예외나 RETURN을, 새 클래스·메서드는 클래스 기반 예외를 쓴다. `CATCH SYSTEM-EXCEPTIONS`는 구식이며 CX_SY_ 예외를 TRY로 잡는다.

</details>

---

### B-061. 예외 클래스 작성: T100 메시지·previous 래핑·SWITCH/COND THROW [작성] ★★
<!-- src: OO-023, OO-024, OO-025 -->
메시지 클래스 ZCL_MSG의 001번이 "Airline &1 not found"이다. 이 메시지를 쓰는 예외 클래스와 사용 코드다.

```abap
CLASS zcx_flight DEFINITION PUBLIC
  INHERITING FROM ____(a)____ FINAL CREATE PUBLIC.
  PUBLIC SECTION.
    INTERFACES ____(b)____.
    DATA carrid TYPE s_carr_id READ-ONLY.
    METHODS constructor
      IMPORTING textid   LIKE if_t100_message=>t100key OPTIONAL
                previous LIKE previous OPTIONAL
                carrid   TYPE s_carr_id OPTIONAL.
ENDCLASS.
CLASS zcx_flight IMPLEMENTATION.
  METHOD constructor ##ADT_SUPPRESS_GENERATION.
    super->constructor( previous = previous ).
    me->carrid = carrid.
    CLEAR me->textid.
    IF textid IS INITIAL.
      if_t100_message~t100key = if_t100_message=>default_textid.
    ELSE.
      if_t100_message~t100key = textid.
    ENDIF.
  ENDMETHOD.
ENDCLASS.
" ---- 사용 ----
TRY.
    RAISE EXCEPTION TYPE zcx_flight
      ____(c)____ e001(zcl_msg) WITH lv_carrid
      EXPORTING carrid = lv_carrid.
  CATCH zcx_flight INTO DATA(lx).
    DATA(lv_text) = lx->____(d)____( ).        " "Airline XX not found"
    MESSAGE lx TYPE ____(e)____ DISPLAY LIKE 'E'.
ENDTRY.
```

(1) 빈칸 (a)~(e)를 채우시오.
(2) IF_T100_MESSAGE와 IF_T100_DYN_MSG의 차이, `MESSAGE oref TYPE ...`의 동작, 메시지 클래스 관리 위치를 쓰시오.
(3) CX_STATIC_CHECK를 상속하는 로컬 예외 클래스 `lcx_app_error`(READ-ONLY 속성 `mv_info`를 생성자 `iv_info`로 받고 textid, previous도 받음)를 작성하시오.
(4) 클래스 `lcl_parser`의 정적 메서드 `parse_seats`(IMPORTING iv_text TYPE string, RETURNING i, RAISING lcx_app_error)를 작성하시오. 변환 중 CX_SY_CONVERSION_ERROR 계열 예외가 나면 그것을 previous로 담아 lcx_app_error(`Invalid seat number`)로 다시 던진다.
(5) `parse_seats( `ABC` )`를 호출하고 lcx_app_error를 잡아 mv_info를 출력한 뒤 previous 체인을 따라가며 각 예외의 `get_text( )`를 출력하는 코드를 쓰시오. 이 래핑의 이점은?
(6) 로컬 예외 `lcx_invalid`(CX_STATIC_CHECK 상속)가 있을 때 `lcl_booking`에 본문이 대입문 하나인 정적 메서드 두 개를 작성하시오. ㉠ `class_text`(IMPORTING iv_class TYPE s_class, RETURNING string): Y → `Economy`, C → `Business`, F → `First`, 그 외 lcx_invalid, `SWITCH` 사용 ㉡ `bag_fee`(IMPORTING iv_bags TYPE i, RETURNING i): 음수면 lcx_invalid, 0~1개는 0, 그 이상은 (개수 − 1) × 30, `COND` 사용. bag_fee( 3 )은?
(7) THROW의 변형(RESUMABLE, MESSAGE, SHORTDUMP)과 RAISING 선언 필요 여부를 쓰시오.

<details><summary>정답·해설</summary>

**(1)** (a) `cx_static_check` (b) `if_t100_dyn_msg` (c) `MESSAGE` (d) `get_text` (e) `'S'`
**(2)** `IF_T100_MESSAGE`는 T100 메시지(메시지 클래스 + 번호 + 속성 이름 매핑 ATTR1~4)를 예외 텍스트로 쓰게 하고, 텍스트 ID 상수를 미리 정의해 `textid = zcx_flight=>not_found`처럼 넘긴다. `IF_T100_DYN_MSG`는 IF_T100_MESSAGE를 포함하며 `RAISE EXCEPTION ... MESSAGE ...` / `THROW ... MESSAGE`로 메시지와 WITH 값을 직접 지정할 수 있다(MSGV1~4 자동 설정, 현재 권장). `MESSAGE oref TYPE ...`는 IF_T100_MESSAGE를 구현한 예외 객체의 메시지를 그대로 출력하며, 업무 화면에서는 'S' + DISPLAY LIKE 'E'가 관례. 메시지 클래스는 SE91(ADT에서도 생성)에서 관리하고 `&1`~`&4`에 WITH 값이 들어간다.
**(3)~(5)** 모범 답안:
```abap
CLASS lcx_app_error DEFINITION INHERITING FROM cx_static_check.
  PUBLIC SECTION.
    DATA mv_info TYPE string READ-ONLY.
    METHODS constructor
      IMPORTING textid   LIKE textid   OPTIONAL
                previous LIKE previous OPTIONAL
                iv_info  TYPE string   OPTIONAL.
ENDCLASS.
CLASS lcx_app_error IMPLEMENTATION.
  METHOD constructor.
    super->constructor( textid = textid previous = previous ).
    mv_info = iv_info.
  ENDMETHOD.
ENDCLASS.

CLASS lcl_parser DEFINITION.
  PUBLIC SECTION.
    CLASS-METHODS parse_seats IMPORTING iv_text  TYPE string
                              RETURNING VALUE(rv) TYPE i
                              RAISING   lcx_app_error.
ENDCLASS.
CLASS lcl_parser IMPLEMENTATION.
  METHOD parse_seats.
    TRY.
        rv = CONV i( iv_text ).
      CATCH cx_sy_conversion_error INTO DATA(lx_conv).
        RAISE EXCEPTION NEW lcx_app_error( previous = lx_conv
                                           iv_info  = `Invalid seat number` ).
    ENDTRY.
  ENDMETHOD.
ENDCLASS.

START-OF-SELECTION.
  DATA lx_cur TYPE REF TO cx_root.
  TRY.
      DATA(lv_seats) = lcl_parser=>parse_seats( `ABC` ).
    CATCH lcx_app_error INTO DATA(lx_app).
      WRITE / lx_app->mv_info.
      lx_cur = lx_app->previous.
      WHILE lx_cur IS BOUND.
        WRITE / lx_cur->get_text( ).
        lx_cur = lx_cur->previous.
      ENDWHILE.
  ENDTRY.
```
`CONV i( `ABC` )`는 CX_SY_CONVERSION_NO_NUMBER(CX_SY_CONVERSION_ERROR의 하위)를 일으킨다. 업무 예외로 감싸되 previous로 원인을 보존하면 로그·디버깅에서 원인을 추적할 수 있다. 생성자 파라미터 `textid`, `previous`는 CX_ROOT 속성을 LIKE로 참조해 `super->constructor`에 넘기고, 체인은 CX_ROOT 참조로 WHILE을 돌며 따라간다. 채점 포인트: 예외 클래스 상속과 생성자, RAISING 선언, `previous = lx` 래핑, 체인 순회.
**(6)**
```abap
CLASS lcl_booking DEFINITION.
  PUBLIC SECTION.
    CLASS-METHODS class_text IMPORTING iv_class TYPE s_class
                             RETURNING VALUE(rv) TYPE string
                             RAISING   lcx_invalid.
    CLASS-METHODS bag_fee    IMPORTING iv_bags  TYPE i
                             RETURNING VALUE(rv) TYPE i
                             RAISING   lcx_invalid.
ENDCLASS.

CLASS lcl_booking IMPLEMENTATION.
  METHOD class_text.
    rv = SWITCH #( iv_class
                   WHEN 'Y' THEN `Economy`
                   WHEN 'C' THEN `Business`
                   WHEN 'F' THEN `First`
                   ELSE THROW lcx_invalid( ) ).
  ENDMETHOD.

  METHOD bag_fee.
    rv = COND #( WHEN iv_bags < 0  THEN THROW lcx_invalid( )
                 WHEN iv_bags <= 1 THEN 0
                 ELSE ( iv_bags - 1 ) * 30 ).
  ENDMETHOD.
ENDCLASS.
```
bag_fee( 3 ) = 60.
**(7)** `THROW cx_class( ... )`는 COND/SWITCH 결과 자리에서 `RAISE EXCEPTION TYPE`과 같은 효과이고 괄호 안에 생성자 파라미터를 넘길 수 있다. 변형: `THROW RESUMABLE`, `THROW cx( ) MESSAGE ...`(IF_T100_DYN_MSG 필요), `THROW SHORTDUMP`. 정적 검사 예외이므로 RAISING 선언이 필요하다.

</details>

---

### B-062. 예외·이벤트가 있는 계좌 클래스 작성 [작성] ★★
<!-- src: MX-036, HC-025 -->
(1) 예외 클래스 `lcx_no_funds`(`cx_static_check` 상속, 부족 금액 `mv_short` 읽기 전용)와 계좌 클래스 `lcl_account`(잔액은 외부에서 직접 변경 불가, 생성자에서 초기 잔액, `deposit`, `withdraw`(부족 시 `lcx_no_funds`), `get_balance`)를 작성하고, 잔액 100으로 만든 뒤 150을 출금해 예외를 잡아 부족 금액을 출력하는 호출부를 쓰시오.
(2) (1) 실행 후 출력되는 부족 금액과 잔액, 그 이유를 쓰시오.
(3) (1)을 확장해 로컬 클래스 `lcl_account`와 `lcl_monitor`(프로그램 `ZHC_BANK`)를 작성하시오. 계좌 번호는 생성 순서대로 1000, 1001, ...(정적 속성). `deposit( iv_amount )`: 0 이하면 표준 예외 `cx_parameter_invalid_range`. `withdraw( iv_amount )`: 잔액 부족이면 사용자 예외 `lcx_insufficient_funds`(잔액과 요청 금액 속성), 출금 후 잔액이 100 미만이면 이벤트 `low_balance`(잔액 전달). `transfer_to( io_target iv_amount )`: 출금 후 대상 계좌에 입금. `lcl_monitor->on_low_balance`는 모든 계좌의 `low_balance`를 받아 "계좌 번호, 잔액 부족 경고" 출력.
(4) 메인: 계좌 A(초기 500), B(초기 0) 생성 → A에서 B로 450 이체 → A에서 100 출금 시도(예외) → 결과 출력. 예상 출력을 쓰시오.
(5) `FOR ALL INSTANCES`와 `FOR lo_a`의 차이, `sender`의 의미를 쓰시오.
(6) `cx_parameter_invalid_range`(CX_DYNAMIC_CHECK 계열)를 deposit의 RAISING에 선언하지 않으면 메인의 `CATCH cx_parameter_invalid_range`로 잡을 수 있는가?

<details><summary>정답·해설</summary>

**(1)** 모범 답안:
```abap
TYPES ty_amt TYPE p LENGTH 15 DECIMALS 2.

CLASS lcx_no_funds DEFINITION INHERITING FROM cx_static_check.
  PUBLIC SECTION.
    DATA mv_short TYPE ty_amt READ-ONLY.
    METHODS constructor
      IMPORTING iv_short  TYPE ty_amt OPTIONAL
                previous  LIKE previous OPTIONAL.
ENDCLASS.

CLASS lcx_no_funds IMPLEMENTATION.
  METHOD constructor.
    super->constructor( previous = previous ).
    mv_short = iv_short.
  ENDMETHOD.
ENDCLASS.

CLASS lcl_account DEFINITION.
  PUBLIC SECTION.
    METHODS constructor IMPORTING iv_initial TYPE ty_amt.
    METHODS deposit     IMPORTING iv_amt TYPE ty_amt.
    METHODS withdraw    IMPORTING iv_amt TYPE ty_amt
                        RAISING   lcx_no_funds.
    METHODS get_balance RETURNING VALUE(rv_bal) TYPE ty_amt.
  PRIVATE SECTION.
    DATA mv_balance TYPE ty_amt.
ENDCLASS.

CLASS lcl_account IMPLEMENTATION.
  METHOD constructor.
    mv_balance = iv_initial.
  ENDMETHOD.
  METHOD deposit.
    IF iv_amt > 0.
      mv_balance = mv_balance + iv_amt.
    ENDIF.
  ENDMETHOD.
  METHOD withdraw.
    IF iv_amt > mv_balance.
      RAISE EXCEPTION TYPE lcx_no_funds
        EXPORTING iv_short = iv_amt - mv_balance.
    ENDIF.
    mv_balance = mv_balance - iv_amt.
  ENDMETHOD.
  METHOD get_balance.
    rv_bal = mv_balance.
  ENDMETHOD.
ENDCLASS.

START-OF-SELECTION.
  DATA: lo_acc  TYPE REF TO lcl_account,
        lv_init TYPE ty_amt VALUE 100,
        lv_out  TYPE ty_amt VALUE 150.
  CREATE OBJECT lo_acc EXPORTING iv_initial = lv_init.
  TRY.
      lo_acc->withdraw( lv_out ).
    CATCH lcx_no_funds INTO DATA(lx).
      WRITE: / '잔액 부족:', lx->mv_short.     " 50.00
  ENDTRY.
  DATA(lv_bal) = lo_acc->get_balance( ).
  WRITE: / '잔액:', lv_bal.                    " 100.00
```
채점 기준(4점): 예외 클래스의 상속·속성·생성자 `super->constructor` 1점, 잔액 캡슐화(PRIVATE)와 생성자 1점, `withdraw`의 `RAISING` 선언과 `RAISE EXCEPTION TYPE ... EXPORTING` 1점, 호출부 `TRY ... CATCH ... INTO`와 부족 금액 출력 1점.
**(2)** 부족 금액 50.00, 잔액 100.00. 예외가 나면 `mv_balance = ...` 줄은 실행되지 않는다. `cx_static_check` 하위 예외는 RAISING으로 선언해야 하며(안 하면 문법 검사 경고, 실행 시 `CX_SY_NO_HANDLER`), 메시지 클래스와 연결(`IF_T100_MESSAGE`)해 텍스트를 줄 수도 있다.
**(3)** 모범 답안(deposit·transfer_to의 RAISING에 동적 검사 예외도 선언):
```abap
REPORT zhc_bank.

TYPES ty_amount TYPE p LENGTH 15 DECIMALS 2.

CLASS lcx_insufficient_funds DEFINITION INHERITING FROM cx_static_check.
  PUBLIC SECTION.
    DATA: mv_balance TYPE ty_amount READ-ONLY,
          mv_amount  TYPE ty_amount READ-ONLY.
    METHODS constructor
      IMPORTING iv_balance TYPE ty_amount
                iv_amount  TYPE ty_amount.
    METHODS if_message~get_text REDEFINITION.
ENDCLASS.

CLASS lcx_insufficient_funds IMPLEMENTATION.
  METHOD constructor.
    super->constructor( ).
    mv_balance = iv_balance.
    mv_amount  = iv_amount.
  ENDMETHOD.
  METHOD if_message~get_text.
    result = |잔액 부족: 잔액 { mv_balance }, 요청 { mv_amount }|.
  ENDMETHOD.
ENDCLASS.

CLASS lcl_account DEFINITION.
  PUBLIC SECTION.
    EVENTS low_balance EXPORTING VALUE(ev_balance) TYPE ty_amount.
    METHODS constructor
      IMPORTING iv_owner   TYPE string
                iv_initial TYPE ty_amount DEFAULT 0.
    METHODS deposit
      IMPORTING iv_amount TYPE ty_amount
      RAISING   cx_parameter_invalid_range.
    METHODS withdraw
      IMPORTING iv_amount TYPE ty_amount
      RAISING   lcx_insufficient_funds.
    METHODS transfer_to
      IMPORTING io_target TYPE REF TO lcl_account
                iv_amount TYPE ty_amount
      RAISING   lcx_insufficient_funds cx_parameter_invalid_range.
    METHODS get_balance RETURNING VALUE(rv_balance) TYPE ty_amount.
    METHODS get_no      RETURNING VALUE(rv_no)      TYPE i.
  PRIVATE SECTION.
    CONSTANTS c_low_limit TYPE ty_amount VALUE 100.
    CLASS-DATA gv_next_no TYPE i VALUE 1000.
    DATA: mv_no      TYPE i,
          mv_owner   TYPE string,
          mv_balance TYPE ty_amount.
ENDCLASS.

CLASS lcl_account IMPLEMENTATION.
  METHOD constructor.
    mv_no      = gv_next_no.
    gv_next_no = gv_next_no + 1.
    mv_owner   = iv_owner.
    mv_balance = iv_initial.
  ENDMETHOD.

  METHOD deposit.
    IF iv_amount <= 0.
      RAISE EXCEPTION TYPE cx_parameter_invalid_range
        EXPORTING parameter = 'IV_AMOUNT'
                  value     = |{ iv_amount }|.
    ENDIF.
    mv_balance = mv_balance + iv_amount.
  ENDMETHOD.

  METHOD withdraw.
    IF iv_amount > mv_balance.
      RAISE EXCEPTION NEW lcx_insufficient_funds( iv_balance = mv_balance
                                                  iv_amount  = iv_amount ).
    ENDIF.
    mv_balance = mv_balance - iv_amount.
    IF mv_balance < c_low_limit.
      RAISE EVENT low_balance EXPORTING ev_balance = mv_balance.
    ENDIF.
  ENDMETHOD.

  METHOD transfer_to.
    withdraw( iv_amount ).                    " 예외면 여기서 중단, 입금 안 됨
    io_target->deposit( iv_amount ).
  ENDMETHOD.

  METHOD get_balance.
    rv_balance = mv_balance.
  ENDMETHOD.

  METHOD get_no.
    rv_no = mv_no.
  ENDMETHOD.
ENDCLASS.

CLASS lcl_monitor DEFINITION.
  PUBLIC SECTION.
    METHODS on_low_balance FOR EVENT low_balance OF lcl_account
      IMPORTING ev_balance sender.
ENDCLASS.

CLASS lcl_monitor IMPLEMENTATION.
  METHOD on_low_balance.
    DATA(lv_no) = sender->get_no( ).
    WRITE: / '경고: 계좌', lv_no, '잔액 부족', ev_balance.
  ENDMETHOD.
ENDCLASS.

START-OF-SELECTION.
  DATA(lo_mon) = NEW lcl_monitor( ).
  SET HANDLER lo_mon->on_low_balance FOR ALL INSTANCES.

  DATA(lo_a) = NEW lcl_account( iv_owner = `KIM` iv_initial = 500 ).
  DATA(lo_b) = NEW lcl_account( iv_owner = `LEE` ).

  TRY.
      lo_a->transfer_to( io_target = lo_b iv_amount = 450 ).   " A 잔액 50 → 이벤트
      lo_a->withdraw( 100 ).                                     " 예외
    CATCH lcx_insufficient_funds INTO DATA(lx_funds).
      DATA(lv_msg) = lx_funds->get_text( ).
      WRITE: / lv_msg.
    CATCH cx_parameter_invalid_range INTO DATA(lx_param).
      lv_msg = lx_param->get_text( ).
      WRITE: / lv_msg.
  ENDTRY.

  WRITE: / |A { lo_a->get_no( ) } { lo_a->get_balance( ) }|,
         / |B { lo_b->get_no( ) } { lo_b->get_balance( ) }|.
```

채점 기준(100점, (3)~(4)):

| 항목 | 배점 |
|---|---|
| 정적 속성으로 계좌 번호 자동 부여 | 10 |
| 사용자 예외 클래스(속성, 생성자, 텍스트) | 15 |
| deposit의 표준 예외 RAISE | 10 |
| withdraw의 사용자 예외 + RAISE EVENT | 20 |
| EVENTS 선언(EXPORTING VALUE) | 10 |
| 핸들러 정의(FOR EVENT ... OF, sender) + SET HANDLER FOR ALL INSTANCES | 20 |
| transfer_to에서 예외 전파 | 5 |
| 메인 TRY/CATCH, 결과 출력 | 10 |

**(4)** 경고(계좌 1000, 잔액 50.00) → 잔액 부족 예외 텍스트(잔액 50.00, 요청 100.00) → `A 1000 50.00` / `B 1001 450.00`. WRITE에는 메서드 결과를 변수로 받거나 문자열 템플릿 안에 넣어(`|{ lo_a->get_no( ) }|`) 출력하는 것이 어느 릴리스에서나 안전하다. 정적 속성 초기값은 `VALUE`로 주며 내부 세션 안에서 모든 인스턴스가 공유한다.
**(5)** 핸들러는 `SET HANDLER`로 등록해야 호출되고, `FOR ALL INSTANCES`는 이후 생성되는 인스턴스까지 포함하며 특정 객체만이면 `FOR lo_a`. `sender`는 모든 인스턴스 이벤트에 암묵적으로 있는 파라미터로 이벤트를 발생시킨 객체 참조다.
**(6)** 잡을 수 없다. CX_DYNAMIC_CHECK 계열은 컴파일 시 검사하지 않을 뿐, 메서드 밖으로 전파하려면 RAISING에 선언해야 한다. 선언 없이 전파되면 경계에서 `CX_SY_NO_HANDLER`로 바뀌어 `CATCH cx_parameter_invalid_range`에 걸리지 않는다. 그래서 위 모범 답안은 deposit과 transfer_to에 `RAISING cx_parameter_invalid_range`를 선언했다(이 메인 실행에서는 450 입금이 유효해 이 예외가 나지 않으므로 출력은 같다). [원문 해설의 "선언하지 않아도 호출 측은 여전히 잡을 수 있다"를 바로잡음]

</details>

---

## ABAP Unit

### B-063. ABAP Unit 기본: FOR TESTING·RISK LEVEL·DURATION·픽스처·assert·오류 찾기·테스트 작성 [작성] ★★
<!-- src: OO-028, OO-035, OO-029, OO-030, HC-027 -->
(1) 테스트 클래스 정의의 `FOR TESTING`, `RISK LEVEL`, `DURATION` 각각의 의미와 가능한 값을 쓰시오.
(2) 픽스처 메서드 setup, teardown, class_setup, class_teardown의 종류(정적/인스턴스)와 실행 시점을 쓰시오. 테스트 메서드의 형태와 실행 방법은?
(3) `cl_abap_unit_assert` 메서드를 다섯 가지 이상 쓰고 공통 파라미터 act, exp, msg, quit의 의미를 쓰시오.
(4) 옳지 **않은** 것을 고르시오. ① setup은 각 테스트 메서드 전, class_setup은 클래스당 한 번 실행된다. ② 테스트 메서드는 선언 순서대로 실행되는 것이 보장된다. ③ 허용 위험 수준보다 높은 RISK LEVEL의 테스트 클래스는 실행되지 않는다. ④ FOR TESTING 클래스는 운영 시스템에서 생성되지 않는다. ⑤ `cl_abap_unit_assert=>fail( )`은 기본적으로 현재 테스트 메서드를 실패로 처리하고 중단한다.
(5) 전역 클래스 ZCL_PRICE_CALC의 테스트 클래스 빈칸을 채우시오. PRIVATE 메서드도 테스트하려면 테스트 include 맨 앞에 무엇을 선언하는가(`CLASS zcl_price_calc DEFINITION ____ ltc_calc.`)?
```abap
CLASS ltc_calc DEFINITION FINAL ____(a)____
  RISK LEVEL ____(b)____
  DURATION ____(c)____.
  PRIVATE SECTION.
    DATA mo_cut TYPE REF TO zcl_price_calc.
    METHODS ____(d)____.
    METHODS discount_10_percent FOR TESTING.
ENDCLASS.
CLASS ltc_calc IMPLEMENTATION.
  METHOD setup.
    mo_cut = NEW #( ).
  ENDMETHOD.
  METHOD discount_10_percent.
    DATA(lv_act) = mo_cut->apply_discount( iv_price = 200 iv_pct = 10 ).
    cl_abap_unit_assert=>____(e)____( act = lv_act  exp = 180  msg = '10% discount failed' ).
  ENDMETHOD.
ENDCLASS.
```
(6) 다음 테스트 클래스의 문제 (가)~(마)를 찾아 고치시오(zcl_flight_stat은 SFLIGHT를 읽어 남은 좌석 수를 계산한다).
```abap
CLASS ltc_flight DEFINITION FOR TESTING RISK LEVEL HARMLESS DURATION SHORT.
  PRIVATE SECTION.
    DATA mo_cut TYPE REF TO zcl_flight_stat.
    METHODS class_setup.                                          " (가)
    METHODS teardown FOR TESTING.                                 " (나)
    METHODS test_free_seats IMPORTING iv_max TYPE i FOR TESTING.  " (다)
ENDCLASS.
CLASS ltc_flight IMPLEMENTATION.
  METHOD class_setup.
  ENDMETHOD.
  METHOD teardown.
  ENDMETHOD.
  METHOD test_free_seats.
    DELETE FROM sflight WHERE carrid = 'ZZ'.                      " (라)
    INSERT sflight FROM @( VALUE #( carrid = 'ZZ' connid = '0001' fldate = '20261020'
                                    seatsmax = 100 seatsocc = 90 ) ).
    mo_cut = NEW #( ).
    DATA(lv_free) = mo_cut->free_seats( iv_carrid = 'ZZ' iv_connid = '0001'
                                        iv_fldate = '20261020' ).
    cl_abap_unit_assert=>assert_equals( act = 10 exp = lv_free ).  " (마)
  ENDMETHOD.
ENDCLASS.
```
(7) 다음 운영 코드의 `calc_fare`를 주석 규칙대로 구현하고, 로컬 테스트 클래스 `ltc_fare_calculator`(HARMLESS, SHORT, setup에서 테스트 대상 생성, 테스트 6개: 이코노미 성인, 비즈니스 어린이, 퍼스트 경로우대, 나이 경계값 12세와 65세, 알 수 없는 등급 예외, 0 이하 운임 예외)를 작성하시오.
```abap
CLASS lcx_invalid_input DEFINITION INHERITING FROM cx_static_check.
ENDCLASS.
CLASS lcl_fare_calculator DEFINITION.
  PUBLIC SECTION.
    TYPES ty_amount TYPE p LENGTH 13 DECIMALS 2.
    "! Y = 기본×1, C = ×2, F = ×3 / 12세 미만 50% 할인, 65세 이상 20% 할인
    "! 기본 운임 0 이하 또는 알 수 없는 등급이면 lcx_invalid_input
    METHODS calc_fare
      IMPORTING iv_base        TYPE ty_amount
                iv_class       TYPE s_class
                iv_age         TYPE i
      RETURNING VALUE(rv_fare) TYPE ty_amount
      RAISING   lcx_invalid_input.
ENDCLASS.
```
(8) (7)의 예외 테스트에서 `fail`을 빠뜨리면? 정상 경로 테스트에 `RAISING cx_static_check`를 붙이는 이유, 기대값 타입을 맞추는 이유를 쓰시오.

<details><summary>정답·해설</summary>

**(1)** `FOR TESTING`: 테스트 클래스(또는 테스트 메서드, 테스트 더블) 표시, 운영 시스템에서는 생성·실행되지 않음. `RISK LEVEL`: HARMLESS(시스템 데이터 변경 없음), DANGEROUS(DB 데이터 변경 가능), CRITICAL(설정·커스터마이징 변경 가능, 기본값). 시스템 설정(SAUNIT_CLIENT_SETUP)에서 허용한 수준을 넘으면 실행되지 않는다. `DURATION`: SHORT(수 초), MEDIUM(약 1분), LONG(1분 초과), 설정 시간을 넘으면 중단.
**(2)**

| 메서드 | 종류 | 실행 시점 |
|---|---|---|
| class_setup | 정적(CLASS-METHODS) | 첫 테스트 전에 한 번 |
| setup | 인스턴스 | 각 테스트 메서드 전마다 |
| teardown | 인스턴스 | 각 테스트 메서드 후마다 |
| class_teardown | 정적 | 마지막 테스트 후 한 번 |

테스트 메서드는 파라미터가 없는 인스턴스 메서드이며 보통 PRIVATE SECTION에 둔다. 픽스처 메서드는 이름이 정해져 있고 FOR TESTING을 붙이지 않는다. 실행: ADT Ctrl+Shift+F10, SE80/SE38 Test → Unit Test, 대량 실행은 ATC.
**(3)** assert_equals, assert_differs, assert_true, assert_false, assert_initial, assert_not_initial, assert_bound, assert_not_bound, assert_subrc, assert_char_cp, assert_table_contains, assert_number_between, fail. `act` 실제 값, `exp` 기대 값, `msg` 실패 메시지, `quit` 실패 시 중단 범위(기본은 현재 테스트 메서드 중단, if_abap_unit_constant=>quit-no면 계속).
**(4)** **②**. 실행 순서는 보장되지 않으므로 각 테스트는 다른 테스트 결과에 의존하지 않도록(Independent) setup에서 상태를 새로 준비한다. ③ SAUNIT_CLIENT_SETUP의 허용 위험 수준·시간 제한이 적용된다. ④ 운영 시스템 프로파일 파라미터(abap/test_generation)에 따라 테스트 코드가 생성되지 않는다. ⑤ quit 기본값이 현재 메서드 중단이다.
**(5)** (a) `FOR TESTING` (b) `HARMLESS` (c) `SHORT` (d) `setup` (e) `assert_equals`. 선언: `LOCAL FRIENDS`(테스트 클래스가 아래에 정의되므로 앞에 `CLASS ltc_calc DEFINITION DEFERRED.`도 둔다). CUT(Class Under Test)는 setup에서 매번 새로 만들어 테스트 간 상태가 섞이지 않게 하고, 테스트 하나는 Given–When–Then 구조로 하나의 동작만 검증한다.
**(6)** (가) class_setup은 정적이어야 함 → `CLASS-METHODS class_setup.` (나) 픽스처 메서드에는 FOR TESTING 불가 → `METHODS teardown.` (다) 테스트 메서드는 파라미터 불가 → `METHODS test_free_seats FOR TESTING.`, 값은 메서드 안에서 준비. (라) HARMLESS인데 실제 DB를 변경(기존 데이터 손상 위험) → CL_OSQL_TEST_ENVIRONMENT로 SFLIGHT를 테스트 더블로 바꾸고 insert_test_data로 넣거나(B-064), DAO를 인터페이스로 분리해 테스트 더블 주입. (마) act와 exp가 바뀌어 실패 메시지가 거꾸로 나옴 → `act = lv_free exp = 10`. (가)~(다)는 문법 오류, (라)·(마)는 설계·논리 오류. 단위 테스트는 외부 상태(DB, 시간, 사용자)에 의존하지 않아야 반복 실행이 가능하다(FIRST: Fast, Independent, Repeatable, Self-validating, Timely).
**(7)** 구현:
```abap
CLASS lcl_fare_calculator IMPLEMENTATION.
  METHOD calc_fare.
    IF iv_base <= 0.
      RAISE EXCEPTION TYPE lcx_invalid_input.
    ENDIF.

    CASE iv_class.
      WHEN 'Y'. rv_fare = iv_base.
      WHEN 'C'. rv_fare = iv_base * 2.
      WHEN 'F'. rv_fare = iv_base * 3.
      WHEN OTHERS.
        RAISE EXCEPTION TYPE lcx_invalid_input.
    ENDCASE.

    IF iv_age < 12.
      rv_fare = rv_fare / 2.
    ELSEIF iv_age >= 65.
      rv_fare = rv_fare * 8 / 10.
    ENDIF.
  ENDMETHOD.
ENDCLASS.
```
테스트 클래스:
```abap
CLASS ltc_fare_calculator DEFINITION FINAL FOR TESTING
  RISK LEVEL HARMLESS
  DURATION SHORT.

  PRIVATE SECTION.
    DATA mo_cut TYPE REF TO lcl_fare_calculator.

    METHODS setup.
    METHODS economy_adult       FOR TESTING RAISING cx_static_check.
    METHODS business_child      FOR TESTING RAISING cx_static_check.
    METHODS first_senior        FOR TESTING RAISING cx_static_check.
    METHODS age_boundaries      FOR TESTING RAISING cx_static_check.
    METHODS unknown_class_fails FOR TESTING.
    METHODS zero_base_fails     FOR TESTING.
ENDCLASS.

CLASS ltc_fare_calculator IMPLEMENTATION.
  METHOD setup.
    mo_cut = NEW #( ).                     " 테스트 메서드마다 새 인스턴스
  ENDMETHOD.

  METHOD economy_adult.
    cl_abap_unit_assert=>assert_equals(
      act = mo_cut->calc_fare( iv_base = 100 iv_class = 'Y' iv_age = 30 )
      exp = CONV lcl_fare_calculator=>ty_amount( 100 )
      msg = '이코노미 성인은 기본 운임' ).
  ENDMETHOD.

  METHOD business_child.
    cl_abap_unit_assert=>assert_equals(
      act = mo_cut->calc_fare( iv_base = 100 iv_class = 'C' iv_age = 10 )
      exp = CONV lcl_fare_calculator=>ty_amount( 100 )
      msg = '비즈니스(200)의 50%' ).
  ENDMETHOD.

  METHOD first_senior.
    cl_abap_unit_assert=>assert_equals(
      act = mo_cut->calc_fare( iv_base = 100 iv_class = 'F' iv_age = 70 )
      exp = CONV lcl_fare_calculator=>ty_amount( 240 )
      msg = '퍼스트(300)의 80%' ).
  ENDMETHOD.

  METHOD age_boundaries.
    cl_abap_unit_assert=>assert_equals(
      act = mo_cut->calc_fare( iv_base = 100 iv_class = 'Y' iv_age = 12 )
      exp = CONV lcl_fare_calculator=>ty_amount( 100 )
      msg = '12세는 할인 없음' ).
    cl_abap_unit_assert=>assert_equals(
      act = mo_cut->calc_fare( iv_base = 100 iv_class = 'Y' iv_age = 11 )
      exp = CONV lcl_fare_calculator=>ty_amount( 50 )
      msg = '11세는 50% 할인' ).
    cl_abap_unit_assert=>assert_equals(
      act = mo_cut->calc_fare( iv_base = 100 iv_class = 'Y' iv_age = 65 )
      exp = CONV lcl_fare_calculator=>ty_amount( 80 )
      msg = '65세는 20% 할인' ).
  ENDMETHOD.

  METHOD unknown_class_fails.
    TRY.
        mo_cut->calc_fare( iv_base = 100 iv_class = 'X' iv_age = 30 ).
        cl_abap_unit_assert=>fail( msg = '예외가 발생해야 함' ).
      CATCH lcx_invalid_input.
        " 기대한 결과
    ENDTRY.
  ENDMETHOD.

  METHOD zero_base_fails.
    TRY.
        mo_cut->calc_fare( iv_base = 0 iv_class = 'Y' iv_age = 30 ).
        cl_abap_unit_assert=>fail( msg = '예외가 발생해야 함' ).
      CATCH lcx_invalid_input.
    ENDTRY.
  ENDMETHOD.
ENDCLASS.
```

채점 기준(100점, (7)):

| 항목 | 배점 |
|---|---|
| 구현: 입력 검사, 등급별 배수, 나이 할인(경계 `<` / `>=`) | 25 |
| `FOR TESTING`, `RISK LEVEL`, `DURATION` | 15 |
| setup에서 인스턴스 생성 | 10 |
| 정상 테스트 3개 assert_equals(act/exp/msg) | 20 |
| 경계값 테스트 | 10 |
| 예외 테스트: 호출 후 `fail`, CATCH로 성공 처리 | 20 |

**(8)** `fail`을 빠뜨리면 예외가 안 나도 테스트가 통과해 버린다(예외 속성까지 확인하려면 `CATCH ... INTO DATA(lx)` 후 assert). 정상 경로 테스트는 운영 코드가 정적 예외를 선언하므로 `RAISING cx_static_check`를 붙여 두고, 예외가 새어 나오면 프레임워크가 오류로 보고한다. `exp`에 정수 리터럴을 넣어도 대부분 통과하지만 `assert_equals`는 타입까지 비교하는 경우가 있어(문자열과 문자 등) 같은 타입으로 맞추는 것이 안전하다. 소수 계산을 `* '0.8'` 대신 정수 연산(`* 8 / 10`)으로 쓴 것은 의도를 분명히 하기 위함이다.

</details>

---

### B-064. 테스트 더블: 의존성 주입·TEST-SEAM·SQL 테스트 환경·기법 비교 [작성] ★★★
<!-- src: OO-031, OO-032, OO-033, OO-034, HC-028 -->
다음 운영 코드가 있다.

```abap
INTERFACE zif_flight_dao PUBLIC.
  METHODS get_seats IMPORTING iv_carrid   TYPE s_carr_id
                              iv_connid   TYPE s_conn_id
                              iv_fldate   TYPE s_date
                    EXPORTING ev_seatsmax TYPE s_seatsmax
                              ev_seatsocc TYPE s_seatsocc.
ENDINTERFACE.
CLASS zcl_flight_service DEFINITION PUBLIC CREATE PUBLIC.
  PUBLIC SECTION.
    METHODS constructor IMPORTING io_dao TYPE REF TO zif_flight_dao.
    METHODS is_bookable IMPORTING iv_carrid TYPE s_carr_id
                                  iv_connid TYPE s_conn_id
                                  iv_fldate TYPE s_date
                                  iv_seats  TYPE i
                        RETURNING VALUE(rv) TYPE abap_bool.
  PRIVATE SECTION.
    DATA mo_dao TYPE REF TO zif_flight_dao.
ENDCLASS.
" is_bookable: 남은 좌석(seatsmax - seatsocc) >= iv_seats 이면 abap_true
```

(1) 테스트 include에 zif_flight_dao를 구현하는 로컬 테스트 더블 `ltd_flight_dao`(좌석 정보를 속성으로 미리 정해 두고 돌려줌)와 테스트 클래스 `ltc_flight_service`(setup에서 더블을 생성자 주입, 남은 좌석 10에서 요청 5 → 참, 요청 11 → 거짓)를 작성하시오. 프레임워크 더블을 쓰는 대안은?
(2) 인터페이스로 분리하기 어려운 기존 코드의 SELECT를 테스트에서 대체하는 빈칸을 채우고, 동작 원리와 사용 제한을 쓰시오.
```abap
" 운영 코드 (zcl_carrier 의 메서드)
METHOD get_carrier_name.     " IMPORTING iv_carrid TYPE s_carr_id RETURNING VALUE(rv_name) TYPE s_carrname
  ____(a)____ read_carrier.
    SELECT SINGLE carrname FROM scarr WHERE carrid = @iv_carrid INTO @rv_name.
  ____(b)____.
ENDMETHOD.
" 테스트 클래스 (zcl_carrier 의 테스트 include)
METHOD name_is_returned.
  ____(c)____ read_carrier.
    rv_name = 'Test Air'.
  ____(d)____.
  cl_abap_unit_assert=>assert_equals(
    act = mo_cut->get_carrier_name( 'XX' )
    exp = CONV s_carrname( 'Test Air' ) ).
ENDMETHOD.
```
(3) zcl_flight_dao의 `count_by_carrier( iv_carrid ) RETURNING i`(SFLIGHT 행 수)를 DB와 무관하게 테스트하는 빈칸을 채우시오.
```abap
CLASS ltc_dao DEFINITION FINAL FOR TESTING RISK LEVEL HARMLESS DURATION SHORT.
  PRIVATE SECTION.
    CLASS-DATA go_env TYPE REF TO ____(e)____.
    DATA mo_cut TYPE REF TO zcl_flight_dao.
    CLASS-METHODS class_setup.
    CLASS-METHODS class_teardown.
    METHODS setup.
    METHODS count_lh FOR TESTING.
ENDCLASS.
CLASS ltc_dao IMPLEMENTATION.
  METHOD class_setup.
    go_env = cl_osql_test_environment=>____(f)____(
               i_dependency_list = VALUE #( ( 'SFLIGHT' ) ) ).
  ENDMETHOD.
  METHOD setup.
    go_env->____(g)____( ).
    mo_cut = NEW #( ).
  ENDMETHOD.
  METHOD count_lh.
    DATA lt_flight TYPE STANDARD TABLE OF sflight WITH EMPTY KEY.
    lt_flight = VALUE #( ( carrid = 'LH' connid = '0400' fldate = '20261020' )
                         ( carrid = 'LH' connid = '0402' fldate = '20261021' )
                         ( carrid = 'AA' connid = '0017' fldate = '20261020' ) ).
    go_env->____(h)____( lt_flight ).
    cl_abap_unit_assert=>assert_equals( act = mo_cut->count_by_carrier( 'LH' ) exp = 2 ).
  ENDMETHOD.
  METHOD class_teardown.
    go_env->____(i)____( ).
  ENDMETHOD.
ENDCLASS.
```
(4) 글로벌 클래스 `ZCL_HC_FLIGHT_STATS`의 다음 메서드를 ABAP SQL Test Double Framework로 테스트하는 로컬 테스트 클래스를 작성하시오. 테스트: (a) 항공사 AA의 두 항공편(180/135, 220/198)이면 67 (b) 데이터가 없는 XX면 0 (c) 다른 항공사 데이터는 무시. 환경은 클래스당 한 번 만들고 마지막에 없애며 테스트마다 더블 데이터를 비운다.
```abap
METHOD get_free_seats.        " IMPORTING iv_carrid TYPE s_carr_id RETURNING VALUE(rv_free) TYPE i
  SELECT seatsmax, seatsocc FROM sflight
    WHERE carrid = @iv_carrid
    INTO TABLE @DATA(lt_fl).
  rv_free = REDUCE i( INIT n = 0 FOR ls IN lt_fl NEXT n = n + ls-seatsmax - ls-seatsocc ).
ENDMETHOD.
```
(5) SQL 테스트 환경의 원리, create를 class_setup에 두는 이유, destroy를 빼면 생기는 일, CDS 뷰 의존 시 사용하는 클래스를 쓰시오.
(6) 의존 객체를 테스트 더블로 바꾸는 방법을 다섯 가지 이상 쓰고 장단점을 쓰시오. 직접 만든 더블의 네 가지 분류는?

<details><summary>정답·해설</summary>

**(1)**
```abap
CLASS ltd_flight_dao DEFINITION FOR TESTING.
  PUBLIC SECTION.
    INTERFACES zif_flight_dao.
    DATA mv_seatsmax TYPE s_seatsmax.
    DATA mv_seatsocc TYPE s_seatsocc.
ENDCLASS.

CLASS ltd_flight_dao IMPLEMENTATION.
  METHOD zif_flight_dao~get_seats.
    ev_seatsmax = mv_seatsmax.
    ev_seatsocc = mv_seatsocc.
  ENDMETHOD.
ENDCLASS.

CLASS ltc_flight_service DEFINITION FINAL FOR TESTING
  RISK LEVEL HARMLESS DURATION SHORT.
  PRIVATE SECTION.
    DATA mo_double TYPE REF TO ltd_flight_dao.
    DATA mo_cut    TYPE REF TO zcl_flight_service.
    METHODS setup.
    METHODS enough_seats  FOR TESTING.
    METHODS too_few_seats FOR TESTING.
ENDCLASS.

CLASS ltc_flight_service IMPLEMENTATION.
  METHOD setup.
    mo_double = NEW #( ).
    mo_double->mv_seatsmax = 100.
    mo_double->mv_seatsocc = 90.        " 남은 좌석 10
    mo_cut = NEW #( io_dao = mo_double ).
  ENDMETHOD.

  METHOD enough_seats.
    cl_abap_unit_assert=>assert_true(
      act = mo_cut->is_bookable( iv_carrid = 'LH' iv_connid = '0400'
                                 iv_fldate = '20261020' iv_seats = 5 )
      msg = '10 free seats should allow 5' ).
  ENDMETHOD.

  METHOD too_few_seats.
    cl_abap_unit_assert=>assert_false(
      act = mo_cut->is_bookable( iv_carrid = 'LH' iv_connid = '0400'
                                 iv_fldate = '20261020' iv_seats = 11 )
      msg = '10 free seats should not allow 11' ).
  ENDMETHOD.
ENDCLASS.
```
운영 클래스가 구체 DAO가 아니라 인터페이스에 의존하므로(DIP) DB 없이 원하는 상황을 만들 수 있다. 경계값(정확히 10석)도 테스트하면 좋다. 대안: `cl_abap_testdouble=>create( 'ZIF_FLIGHT_DAO' )`와 `configure_call( )->set_parameter( ... )`(전역 인터페이스·비 FINAL 클래스만). 채점 포인트: 더블의 인터페이스 구현, 생성자 주입, setup에서 CUT 생성, assert_true/false(또는 assert_equals).
**(2)** (a) `TEST-SEAM` (b) `END-TEST-SEAM` (c) `TEST-INJECTION` (d) `END-TEST-INJECTION`. 단위 테스트 실행 중에는 같은 이름의 seam 코드가 injection 코드로 바뀌고 일반 실행에서는 원래 코드가 실행된다. injection 코드는 seam 위치의 문맥(rv_name 같은 지역 변수)을 그대로 쓴다. injection은 해당 클래스(프로그램)의 테스트 include 안 테스트 클래스에서만 쓸 수 있고, 빈 seam을 만들어 테스트 때만 코드를 끼워 넣을 수도 있다. 운영 코드에 테스트 표시가 섞이므로 새 코드에서는 인터페이스 주입이나 SQL 테스트 더블을 우선하고 TEST-SEAM은 레거시에 제한적으로 쓴다.
**(3)** (e) `if_osql_test_environment` (f) `create` (g) `clear_doubles` (h) `insert_test_data` (i) `destroy`
**(4)** 모범 답안:
```abap
CLASS ltc_flight_stats DEFINITION FINAL FOR TESTING
  RISK LEVEL HARMLESS
  DURATION SHORT.

  PRIVATE SECTION.
    CLASS-DATA go_env TYPE REF TO if_osql_test_environment.
    DATA mo_cut TYPE REF TO zcl_hc_flight_stats.

    CLASS-METHODS class_setup.
    CLASS-METHODS class_teardown.
    METHODS setup.
    METHODS sum_for_carrier      FOR TESTING.
    METHODS unknown_carrier_zero FOR TESTING.
    METHODS other_carrier_ignored FOR TESTING.
ENDCLASS.

CLASS ltc_flight_stats IMPLEMENTATION.
  METHOD class_setup.
    go_env = cl_osql_test_environment=>create(
               i_dependency_list = VALUE #( ( 'SFLIGHT' ) ) ).
  ENDMETHOD.

  METHOD class_teardown.
    go_env->destroy( ).
  ENDMETHOD.

  METHOD setup.
    go_env->clear_doubles( ).
    mo_cut = NEW #( ).
  ENDMETHOD.

  METHOD sum_for_carrier.
    DATA lt_fl TYPE STANDARD TABLE OF sflight WITH EMPTY KEY.
    lt_fl = VALUE #(
      ( carrid = 'AA' connid = '0017' fldate = '20261201' seatsmax = 180 seatsocc = 135 )
      ( carrid = 'AA' connid = '0064' fldate = '20261202' seatsmax = 220 seatsocc = 198 ) ).
    go_env->insert_test_data( lt_fl ).

    cl_abap_unit_assert=>assert_equals(
      act = mo_cut->get_free_seats( 'AA' )
      exp = 67
      msg = '45 + 22 = 67' ).
  ENDMETHOD.

  METHOD unknown_carrier_zero.
    cl_abap_unit_assert=>assert_equals(
      act = mo_cut->get_free_seats( 'XX' )
      exp = 0
      msg = '데이터가 없으면 0' ).
  ENDMETHOD.

  METHOD other_carrier_ignored.
    DATA lt_fl TYPE STANDARD TABLE OF sflight WITH EMPTY KEY.
    lt_fl = VALUE #(
      ( carrid = 'AA' connid = '0017' fldate = '20261201' seatsmax = 100 seatsocc = 90 )
      ( carrid = 'LH' connid = '0400' fldate = '20261201' seatsmax = 300 seatsocc = 0 ) ).
    go_env->insert_test_data( lt_fl ).

    cl_abap_unit_assert=>assert_equals(
      act = mo_cut->get_free_seats( 'AA' )
      exp = 10
      msg = 'LH 좌석은 합산하지 않음' ).
  ENDMETHOD.
ENDCLASS.
```

채점 기준(100점, (4)):

| 항목 | 배점 |
|---|---|
| 테스트 클래스 선언(FOR TESTING, RISK LEVEL, DURATION) | 10 |
| class_setup에서 `cl_osql_test_environment=>create( i_dependency_list = ... )` | 25 |
| class_teardown에서 `destroy` | 10 |
| setup에서 `clear_doubles` + CUT 생성 | 15 |
| `insert_test_data`로 더블 데이터 준비 | 15 |
| 세 테스트의 assert_equals와 기대값 계산 | 25 |

DB 접근을 인터페이스 뒤로 숨기고 더블을 주입하는 방식도 같은 목적의 정답이다.
**(5)** create로 의존 테이블 목록을 넘기면 테스트 중 CUT의 `SELECT ... FROM sflight`가 실제 테이블 대신 더블(임시 테이블)로 리디렉트된다. 실제 DB를 건드리지 않아 RISK LEVEL HARMLESS가 정당해진다. create는 비용이 커서 class_setup에서 한 번 만들고 테스트마다 setup에서 clear_doubles로 비운 뒤 필요한 데이터만 넣는다. destroy를 빼면 리디렉트가 남을 수 있다. CDS 뷰 의존 시 `cl_cds_test_environment=>create( i_for_entity = '...' )`(IF_CDS_TEST_ENVIRONMENT).
**(6)**

| 방법 | 설명 | 장점 | 단점 |
|---|---|---|---|
| 생성자 주입 | 생성자 파라미터로 인터페이스 구현을 받음 | 의존성이 명시적, 가장 권장 | 기존 클래스는 시그니처 변경 필요 |
| 세터 주입 | set_dao( ) 같은 메서드로 교체 | 선택적 의존성에 적합 | 객체가 불완전한 상태일 수 있음 |
| 파라미터 주입 | 메서드의 선택적 IMPORTING으로 받음 | 범위가 좁음 | 시그니처가 지저분해짐 |
| Back-door 주입 | 테스트 클래스를 LOCAL FRIENDS로 선언해 PRIVATE 속성 직접 교체 | 운영 API 변경 없음 | 내부 구현에 결합 |
| 팩토리/인젝터 | 팩토리가 생성, 테스트 전용 인젝터(FRIENDS)가 반환값을 더블로 설정 | 대규모 코드에서 일관적 | 구조가 복잡 |
| TEST-SEAM | 운영 코드 일부를 테스트 때만 대체 | 레거시에 바로 적용 | 운영 코드에 테스트 표시가 섞임 |
| cl_abap_testdouble | 프레임워크가 인터페이스 더블 생성, configure_call로 반환값, verify_expectations로 호출 검증 | 더블 클래스 작성 불필요, 호출 검증 | 전역 인터페이스·비 FINAL 클래스만 |
| SQL/CDS 테스트 환경 | cl_osql_test_environment, cl_cds_test_environment | DB 접근 코드 그대로 테스트 | 셋업 비용 |

직접 만든 더블은 Stub(정해진 값 반환), Spy(호출 기록), Mock(기대 호출 검증), Fake(간단한 동작 구현)로 나눈다. 시험에서는 "DB 접근이 있는 메서드를 어떻게 단위 테스트하나"로 자주 나온다.

</details>

---

## 표준 테이블 · T-code · 용어

### B-065. 업무 모듈 표준 테이블: MM·SD·구매·FI·고객/공급업체와 키 필드 [개념] ★★
<!-- src: TC-057, TC-058, TC-059, TC-060, TC-061, TC-062 -->
(1) 자재(MM) 테이블을 쓰시오: ① 마스터 일반 ② 플랜트 ③ 저장 위치(재고) ④ 내역(언어별 이름) ⑤ 평가(가격) ⑥ 판매(판매 조직·유통 경로별) ⑦ 자재 문서 헤더 / 품목(ECC) ⑧ S/4HANA 자재 문서 통합 ⑨ 플랜트 ⑩ 저장 위치
(2) 판매(SD) 테이블을 쓰시오: ① 판매 문서 헤더 ② 품목 ③ 일정 라인 ④ 파트너 ⑤ 문서 흐름 ⑥ 출하 헤더 / 품목 ⑦ 청구 헤더 / 품목 ⑧ 가격 조건(ECC) / S/4HANA 가격 요소 ⑨ 헤더 상태 / 품목 상태(ECC). 판매 오더 → 출하 → 청구 추적 방법과 관련 T-code는?
(3) 구매 테이블을 쓰시오: ① 구매 요청 ② 구매 오더 헤더 ③ 품목 ④ 납품 일정 ⑤ 구매 오더 이력(입고·송장) ⑥ 구매 정보 레코드 일반 / 구매 조직별 ⑦ 공급원 목록. 관련 T-code는?
(4) 재무(FI) 테이블을 쓰시오: ① 회계 전표 헤더 ② 품목(ECC 클러스터) ③ S/4HANA Universal Journal ④ 고객 미결 / 반제 ⑤ 공급업체 미결 / 반제 ⑥ G/L 미결 / 반제 ⑦ G/L 계정(계정과목표 / 회사 코드 단위) ⑧ 회사 코드 ⑨ 코스트 센터. 미결·반제 테이블 이름의 규칙은?
(5) 고객·공급업체 테이블을 쓰시오: ① 고객 일반 ② 고객 회사 코드 ③ 고객 판매 영역 ④ 공급업체 일반 ⑤ 공급업체 회사 코드 ⑥ 공급업체 구매 조직 ⑦ 비즈니스 파트너 일반(S/4HANA) ⑧ 주소(BAS). S/4HANA에서 고객·공급업체 유지 방식은?
(6) 다음 테이블의 기본 키를 MANDT를 제외하고 순서대로 쓰시오: MARC, MARD, MAKT, VBAP, EKPO, BKPF, BSEG, KNVV, T100. 키를 앞에서부터 쓰는 이점은?

<details><summary>정답·해설</summary>

**(1)** ① MARA ② MARC ③ MARD ④ MAKT ⑤ MBEW ⑥ MVKE ⑦ MKPF / MSEG ⑧ MATDOC ⑨ T001W ⑩ T001L. 조회 화면 MM03. MARA는 MATNR만 키, MARC는 MATNR+WERKS, MARD는 MATNR+WERKS+LGORT. S/4HANA에서 MKPF/MSEG는 MATDOC 위의 호환 뷰로 남아 있다.
**(2)** ① VBAK ② VBAP ③ VBEP ④ VBPA ⑤ VBFA ⑥ LIKP / LIPS ⑦ VBRK / VBRP ⑧ KONV / PRCD_ELEMENTS ⑨ VBUK / VBUP. 연결은 VBFA(선행 문서 VBELV, 후속 문서 VBELN)로 추적한다. S/4HANA에서 VBUK/VBUP 상태 필드는 VBAK/VBAP(출하·청구는 LIKP/LIPS, VBRK/VBRP)로 옮겨졌다. T-code: 판매 오더 VA01/VA02/VA03, 출하 VL01N, 청구 VF01.
**(3)** ① EBAN ② EKKO ③ EKPO ④ EKET ⑤ EKBE ⑥ EINA / EINE ⑦ EORD. T-code: 구매 오더 ME21N/ME22N/ME23N, 구매 요청 ME51N, 입고 MIGO, 송장 검증 MIRO. EKPO 키는 EBELN + EBELP(NUMC 5).
**(4)** ① BKPF ② BSEG ③ ACDOCA ④ BSID / BSAD ⑤ BSIK / BSAK ⑥ BSIS / BSAS ⑦ SKA1 / SKB1 ⑧ T001 ⑨ CSKS. 규칙: 미결(Open, I) / 반제(Cleared, A) + 고객(D) / 공급업체(K) / G/L(S). S/4HANA에서 BSID 등은 ACDOCA 기반 호환 뷰가 된다. 전표 조회 FB03.
**(5)** ① KNA1 ② KNB1 ③ KNVV ④ LFA1 ⑤ LFB1 ⑥ LFM1 ⑦ BUT000 ⑧ ADRC. S/4HANA에서는 BP 트랜잭션으로 유지하고 CVI(Customer Vendor Integration)가 KNA1/LFA1 등을 동기화한다. KNA1-ADRNR이 ADRC-ADDRNUMBER를 가리킨다.
**(6)** MARC: MATNR, WERKS. MARD: MATNR, WERKS, LGORT. MAKT: MATNR, SPRAS. VBAP: VBELN, POSNR. EKPO: EBELN, EBELP. BKPF: BUKRS, BELNR, GJAHR. BSEG: BUKRS, BELNR, GJAHR, BUZEI. KNVV: KUNNR, VKORG, VTWEG, SPART. T100: SPRSL, ARBGB, MSGNR(T100에는 MANDT가 없다, 클라이언트 독립). 키를 모두 지정한 `SELECT SINGLE`이어야 한 건이 확정되고, FOR ALL ENTRIES나 조인 조건에도 키를 앞에서부터 쓰면 기본 키 인덱스를 탄다.

</details>

---

### B-066. Flight·/DMO/ 모델, 기술 테이블, S/4HANA 데이터 모델 변화, 화면 필드의 테이블 찾기 [개념] ★★
<!-- src: TC-063, TC-064, TC-066, TC-067, TC-068 -->
(1) Flight 데이터 모델 SCARR, SPFLI, SFLIGHT, SBOOK, SCUSTOM, SAPLANE의 내용과 키(MANDT 제외)를 쓰시오. 데이터 생성 프로그램과 그 밖의 테이블, 이 모델이 예제에 자주 쓰이는 이유는?
(2) ABAP Flight Reference Scenario 테이블과 내용의 짝으로 옳지 **않은** 것은? ① /DMO/TRAVEL – 여행(헤더) ② /DMO/BOOKING – 여행별 항공편 예약 ③ /DMO/BOOK_SUPPL – 예약별 부가 서비스 ④ /DMO/AGENCY – 여행 고객 ⑤ /DMO/CARRIER – 항공사. 그 밖의 테이블과 데이터 생성 방법은?
(3) 다음 기술 테이블을 쓰시오: ① 사용자 로그온 데이터 ② 역할-사용자 할당 ③ 백그라운드 작업 헤더 / 스텝 ④ 출력 메시지 상태 ⑤ 긴 텍스트 헤더 / 본문 ⑥ 변경 문서 헤더 / 항목 ⑦ 선택 변수(STVARVC) ⑧ 환율 / 통화 코드 ⑨ 측정 단위 / 국가 / 언어
(4) 변경 문서를 찾는 키와, TCURR의 날짜 필드를 직접 다룰 때 주의점을 쓰시오.
(5) ECC 대비 S/4HANA 테이블 변화로 옳지 **않은** 것은? ① 자재 문서는 MATDOC에 저장되고 MKPF/MSEG는 호환 뷰다. ② FI·CO 품목은 ACDOCA에 통합되었다. ③ VBUK/VBUP 필드는 VBAK/VBAP 등으로 옮겨졌다. ④ MATNR 최대 길이가 40자로 늘었다. ⑤ KNA1은 삭제되어 BUT000만 사용한다.
(6) VA03 화면의 필드가 어느 테이블·필드에 저장되는지 찾는 방법을 세 가지 이상 쓰시오.

<details><summary>정답·해설</summary>

**(1)** SCARR: 항공사 — CARRID. SPFLI: 운항 일정(노선, 출발·도착 도시와 공항) — CARRID, CONNID. SFLIGHT: 날짜별 항공편(가격, 좌석 수) — CARRID, CONNID, FLDATE. SBOOK: 예약 — CARRID, CONNID, FLDATE, BOOKID. SCUSTOM: 항공 고객 — ID. SAPLANE: 항공기 유형 — PLANETYPE. 데이터 생성은 SAPBC_DATA_GENERATOR(또는 SAPBC_DATAMODEL), 그 밖에 STRAVELAG(여행사), SCOUNTER(판매 창구). 키가 SCARR ⊂ SPFLI ⊂ SFLIGHT ⊂ SBOOK로 한 필드씩 늘어나 조인·외래키 예제에 자주 쓰인다.
**(2)** **④**. /DMO/AGENCY는 여행사, 고객은 /DMO/CUSTOMER. 그 밖에 /DMO/CONNECTION(노선), /DMO/FLIGHT(항공편), /DMO/SUPPLEMENT(부가 서비스 마스터). 데이터는 클래스 `/DMO/CL_FLIGHT_DATA_GENERATOR`를 F9로 실행해 만든다. 관리형 draft 예제는 /DMO/A_TRAVEL_D 같은 별도 테이블을 쓴다.
**(3)** ① USR02 ② AGR_USERS ③ TBTCO / TBTCP ④ NAST ⑤ STXH / STXL ⑥ CDHDR / CDPOS ⑦ TVARVC ⑧ TCURR / TCURC ⑨ T006 / T005 / T002
**(4)** 변경 문서는 OBJECTCLAS + OBJECTID로 찾는다(예: 자재 MATERIAL). TCURR의 GDATU는 역순 날짜(99999999 − 날짜) 형식이라 `CONVERT_TO_LOCAL_CURRENCY` 같은 함수를 쓰는 것이 안전하다.
**(5)** **⑤**. KNA1/LFA1은 그대로 있고, 유지보수가 BP로 통합되어 CVI가 BP(BUT000 등)와 고객/공급업체 테이블을 동기화한다. ④ ECC의 MATNR은 18자. 가격 조건은 KONV 대신 PRCD_ELEMENTS. 기존 코드가 깨지지 않도록 많은 테이블이 같은 이름의 CDS 호환 뷰(Compatibility View)로 대체되었다.
**(6)** ① 필드에서 F1 → Technical Information: 화면 필드 이름(`VBAK-AUART`), 데이터 엘리먼트, 프로그램·화면 번호(화면 구조 RV45A 등이면 실제 테이블은 따로 찾음) ② ST05 SQL 트레이스를 켜고 화면 저장·조회를 실행해 접근한 테이블 확인 ③ 데이터 엘리먼트로 SE11/SE84 where-used list를 조회하거나 DD03L에서 ROLLNAME으로 검색 ④ 디버거로 값을 채우는 SELECT 찾기. 업무 테이블 이름 규칙(VB 판매, EK 구매, BS/BK 재무, MA 자재)을 알면 범위를 빨리 좁힌다.

</details>

---

### B-067. 약어: 클래식 ABAP·최신 ABAP·화면/아키텍처·업무 모듈 [개념] ★
<!-- src: TC-087, TC-088, TC-089, TC-090 -->
(1) 다음 클래식 ABAP 약어의 영문 전체 이름을 쓰시오: ABAP, BAPI, BAdI, LUW, RFC, IDoc, ALE, EDI, BDC, LSMW, ALV, TMG, DDIC, FM, BOR, RTTS
(2) 다음 최신 ABAP·도구 약어의 영문 이름을 쓰시오: CDS, AMDP, RAP, EML, BDEF, OData, ADT, ATC, SCI, CTS, TMS, SEGW, DDLS, DCL, DDLX, SRVD/SRVB, DDL
(3) 다음 약어의 영문 이름과 한 줄 의미를 쓰시오: PBO, PAI, POH, POV, RICEFW, CBO(국내 용어), ECC, HANA, FLP, BTP, CAP, VDM. RICEFW의 C에서 흔한 오류는?
(4) 다음 업무 약어의 영문 이름을 쓰시오: SD, MM, FI, CO, PP, QM, PM, HCM, PR, PO, GR, GI, SO, BOM, MRP, EWM, IR
(5) 구매 P2P와 판매 O2C의 대표 흐름을 쓰시오.

<details><summary>정답·해설</summary>

**(1)** ABAP: Advanced Business Application Programming(원래 독일어 Allgemeiner Berichts-Aufbereitungs-Prozessor). BAPI: Business Application Programming Interface. BAdI: Business Add-In. LUW: Logical Unit of Work. RFC: Remote Function Call. IDoc: Intermediate Document. ALE: Application Link Enabling. EDI: Electronic Data Interchange. BDC: Batch Data Communication. LSMW: Legacy System Migration Workbench. ALV: ABAP List Viewer(현재 공식 명칭 SAP List Viewer). TMG: Table Maintenance Generator. DDIC: Data Dictionary. FM: Function Module. BOR: Business Object Repository. RTTS: Run Time Type Services(RTTI 타입 정보 + RTTC 타입 생성).
**(2)** CDS: Core Data Services. AMDP: ABAP Managed Database Procedures. RAP: ABAP RESTful Application Programming Model. EML: Entity Manipulation Language. BDEF: Behavior Definition. OData: Open Data Protocol. ADT: ABAP Development Tools(for Eclipse). ATC: ABAP Test Cockpit. SCI: SAP Code Inspector. CTS: Change and Transport System. TMS: Transport Management System. SEGW: SAP Gateway Service Builder(T-code 이름). DDLS: DDL Source. DCL: Data Control Language(접근 제어). DDLX: 메타데이터 확장. SRVD/SRVB: Service Definition/Binding. DDL: Data Definition Language.
**(3)** PBO: Process Before Output — 화면 표시 전 처리. PAI: Process After Input — 사용자 동작 후 처리. POH: Process On Help-Request — F1 이벤트. POV: Process On Value-Request — F4 이벤트. RICEFW: Reports, Interfaces, Conversions, Enhancements, Forms, Workflows — 개발 대상 분류. CBO: Customer Bolt-On — 고객이 추가 개발한 프로그램·객체(Z 개발), 국내에서 "CBO 개발", "CBO 테이블"처럼 쓴다. ECC: ERP Central Component — S/4HANA 이전 ERP 핵심. HANA: High-performance ANalytic Appliance — SAP 인메모리 컬럼 DB. FLP: Fiori Launchpad — Fiori 앱 진입 포털(타일). BTP: Business Technology Platform — SAP 클라우드 플랫폼(PaaS). CAP: Cloud Application Programming Model — BTP용 Node.js/Java 개발 모델. VDM: Virtual Data Model — S/4HANA 표준 CDS 뷰 계층 모델. RICEFW의 C는 Conversions(데이터 이관)인데 Extensions로 잘못 쓰는 자료가 있다.
**(4)** SD Sales and Distribution, MM Materials Management, FI Financial Accounting, CO Controlling, PP Production Planning, QM Quality Management, PM Plant Maintenance, HCM Human Capital Management, PR Purchase Requisition, PO Purchase Order, GR Goods Receipt, GI Goods Issue, SO Sales Order, BOM Bill of Materials, MRP Material Requirements Planning, EWM Extended Warehouse Management, IR Invoice Receipt.
**(5)** P2P(Procure to Pay): PR → PO → GR → IR → 지급. O2C(Order to Cash): SO → Delivery(GI) → Billing → 수금.

</details>

---

### B-068. RAP 용어·VDM 접두어·ABAP Cloud 용어 [개념] ★★
<!-- src: TC-096, TC-097, TC-098 -->
(1) 다음 설명에 해당하는 RAP 용어를 쓰시오. ㉠ 트리거(생성·필드 변경) 시 다른 필드 값을 자동 계산·설정 ㉡ 저장 전 일관성 검사, 오류면 저장 차단 ㉢ 표준 CRUD 외 사용자 정의 동작(승인 버튼) ㉣ 인스턴스 상태에 따라 필드·동작·편집 가능 여부를 동적으로 제어 ㉤ save 단계에서 최종 키 부여 ㉥ 편집 중 데이터를 임시 테이블에 보관 ㉦ 동시 변경 감지용 BDEF 필드 ㉧ 오류 키 응답 파라미터 / 메시지 파라미터 ㉨ 권한·feature 검사를 건너뛰고 BO 자신의 EML 실행 ㉩ 프레임워크가 CRUD·저장을 처리하는 유형 / 기존 코드로 직접 구현하는 유형
(2) 새 키 매핑 응답 파라미터, 핸들러·세이버 클래스 이름 관례와 상위 클래스, EML 문장 종류를 쓰시오.
(3) S/4HANA VDM CDS 뷰 접두어 `I_`, `C_`, `R_`, `P_`, `A_`, `E_`의 의미를 쓰시오. 고객 개발 관례는?
(4) ABAP Cloud 용어 설명으로 옳지 **않은** 것은? ① Released API는 SAP가 안정성을 약속하고 ABAP Cloud에서 허용한 객체다. ② C1은 "시스템 내부에서 ABAP Cloud 개발에 사용"이다. ③ C0는 "확장" 계약으로 확장 가능한 지점(필드 확장 include 등)의 안정성을 약속한다. ④ SAP BTP ABAP Environment는 흔히 "Steampunk"라 부른다. ⑤ ABAP Cloud 언어 버전에서는 dynpro와 WRITE 리스트를 쓸 수 있지만 SELECT는 금지된다.
(5) 해제 계약 C2, C3, C4의 의미와, Embedded Steampunk·3-Tier 확장 모델(최근 설명 방식 포함)을 쓰시오.

<details><summary>정답·해설</summary>

**(1)** ㉠ determination ㉡ validation ㉢ action ㉣ (dynamic) feature control ㉤ late numbering ㉥ draft ㉦ ETag(etag master) ㉧ failed / reported ㉨ IN LOCAL MODE ㉩ managed / unmanaged
**(2)** 생성 시 새 키 매핑은 `mapped`. 핸들러 클래스는 관례적으로 `lhc_<엔티티>`(local handler class, `CL_ABAP_BEHAVIOR_HANDLER` 상속), 세이버 클래스는 `lsc_<BO>`(`CL_ABAP_BEHAVIOR_SAVER` 상속). EML: READ ENTITIES, MODIFY ENTITIES, COMMIT ENTITIES, ROLLBACK ENTITIES, GET PERMISSIONS, SET LOCKS.
**(3)** I_: Interface view(Basic/Composite 계층, 재사용 가능한 기본 모델, 예 I_Product). C_: Consumption view(특정 앱·UI·분석용 최상위). R_: Restricted reuse view(RAP BO의 기반, 같은 BO 안에서만 재사용). P_: Private view(내부 보조용, 다른 곳에서 사용 금지). A_: Remote API view(OData API로 외부 공개, API_… 서비스). E_: Extension include view(필드 확장용). 고객 개발은 `ZI_`(인터페이스/기본), `ZC_`(프로젝션/소비), `ZR_`(RAP BO 루트)를 쓰며 /DMO/ 예제도 `/DMO/I_Travel_U`, `/DMO/C_Travel_U`처럼 같은 규칙이다.
**(4)** **⑤**. ABAP Cloud 언어 버전(ABAP for Cloud Development)에서는 dynpro, 선택 화면, WRITE 리스트 같은 SAP GUI 기술이 금지되고, SELECT는 허용되지만 released CDS 뷰·자기 테이블만 접근할 수 있다.
**(5)** C2: 원격 API로 사용, C3: 구성 콘텐츠 관리, C4: AMDP에서 사용. S/4HANA 안에서 ABAP Cloud로 개발하는 것을 "Embedded Steampunk"라 하고, 확장 전략을 Tier 1(ABAP Cloud)/Tier 2(래퍼로 미해제 API 사용)/Tier 3(클래식 ABAP)로 설명해 왔다(최근 SAP는 clean core 수준을 A~D 등급으로 설명한다).

</details>

---

## 출처

SAP 공식 문서·샘플
- SAP ABAP Cheat Sheets (GitHub, SAP-samples): https://github.com/SAP-samples/abap-cheat-sheets
- ABAP cheat sheets README (Selection Screens and Classic Lists, SAP LUW, Dynpro, Released Classes): https://raw.githubusercontent.com/SAP-samples/abap-cheat-sheets/main/README.md
- ABAP Cheat Sheets – SAP LUW: https://github.com/SAP-samples/abap-cheat-sheets/blob/main/17_SAP_LUW.md
- ABAP Cheat Sheets – Dynpro: https://github.com/SAP-samples/abap-cheat-sheets/blob/main/18_Dynpro.md
- ABAP Cheat Sheets – Selection Screens and Classic Lists: https://github.com/SAP-samples/abap-cheat-sheets/blob/main/20_Selection_Screens_Lists.md
- ABAP Cheat Sheets – ABAP Object Orientation: https://github.com/SAP-samples/abap-cheat-sheets/blob/main/04_ABAP_Object_Orientation.md
- ABAP Cheat Sheets – Exceptions and Runtime Errors: https://github.com/SAP-samples/abap-cheat-sheets/blob/main/27_Exceptions.md
- ABAP Cheat Sheets – ABAP Unit Tests (CL_OSQL_TEST_ENVIRONMENT 예제 포함): https://github.com/SAP-samples/abap-cheat-sheets/blob/main/14_ABAP_Unit_Tests.md
- ABAP Cheat Sheets – OO Design Patterns: https://github.com/SAP-samples/abap-cheat-sheets/blob/main/34_OO_Design_Patterns.md
- ABAP Keyword Documentation: https://help.sap.com/doc/abapdocu_latest_index_htm/latest/en-US/index.htm
- ABAP Keyword Documentation – METHODS DEFAULT IGNORE/FAIL: https://help.sap.com/docs/abap-cloud/abap-keyword/methods-default
- ABAP Keyword Documentation 7.52 – AT - itab (control level processing): https://help.sap.com/doc/abapdocu_752_index_htm/7.52/en-US/abapat_itab.htm
- ABAP 프로그래밍 가이드라인 – Messages: https://help.sap.com/doc/abapdocu_752_index_htm/7.52/en-US/abenmessages_guidl.htm
- SAP Help – ABAP Dictionary, Lock Objects, Table Buffering: https://help.sap.com/docs/SAP_NETWEAVER_750/
- SAP Certified Associate – Back-End Developer – ABAP Cloud (C_ABAPD): https://learning.sap.com/certifications/sap-certified-associate-back-end-developer-abap-cloud
- SAP Answers – BAdI vs User Exit 토론: https://answers.sap.com/questions/1034609/difference-between-badi-and-user-exits.html

BAPI·테이블·T-code 참고
- BAPI_FLBOOKING_CREATEFROMDATA 인터페이스: https://www.se80.co.uk/sap-function-modules/b/bapi/bapi_flbooking_createfromdata.htm
- BAPISBONEW / BAPISBOPRI 구조: https://www.se80.co.uk/saptables/b/bapi/bapisbonew.htm , https://www.se80.co.uk/saptables/b/bapi/bapisbopri.htm
- Pathlock – ABAP·Basis T-code 분류: https://pathlock.com/blog/transaction-codes-in-sap-abap/
- Cleverence – ABAP 개발 T-code 목록: https://www.cleverence.com/articles/sap-documentation/list-of-transaction-codes-abap-development-4827
- Cleverence – IDoc T-code (WE30/WE31/WE19/BD87/WE02/WE05/WE60): https://cleverence.com/articles/sap-documentation/list-of-important-transaction-codes-to-create-idocs-7483
- ABAP System Fields 표: https://developer.aliyun.com/article/359742
- 시스템 필드 면접 질문: https://onestopsap.com/interview-question/sap/3.asp
- SAP 표준·시스템 테이블 목록: https://www.testingbrain.com/sap/abap-tutorial/list-of-sap-system-tables.html
- ST05/SAT/SQLM 비교: https://aixsap.com/abap-performance-st05-sat-sqlm-bottlenecks/
- SAP PRESS 블로그 – SAP ECC vs SAP S/4HANA technical foundations: https://blog.sap-press.com/sap-ecc-vs-sap-s4hana-technical-foundations

면접 질문 모음
- InterviewBit: https://www.interviewbit.com/sap-abap-interview-questions/
- Guru99: https://www.guru99.com/sap-abap-interview-questions.html
- javatpoint: https://www.javatpoint.com/sap-abap-interview-questions
- Mindmajix: https://mindmajix.com/sap-abap-interview-questions
- igmGuru: https://www.igmguru.com/blog/sap-abap-interview-questions
- Final Round AI: https://www.finalroundai.com/blog/sap-abap-interview-questions
- Indeed India: https://in.indeed.com/career-advice/interviewing/sap-abap-interview-questions
- GeeksforGeeks: https://www.geeksforgeeks.org/sap-abap-interview-questions/
- Multisoft Systems: https://www.multisoftsystems.com/interview-questions/sap-abap-interview-questions-answers
- Tutorialspoint: https://www.tutorialspoint.com/sap_abap/sap_abap_interview_questions.htm
- UrbanPro – Enhancement/BAdI 질문: https://www.urbanpro.com/sap/what-are-the-real-time-interview-questions
- HackerEarth – How to hire SAP ABAP developer: https://www.hackerearth.com/recruit/resources/how-to-hire/sap-abap-developer/
- AmbitionBox – SAP ABAP Associate Consultant 면접 질문: https://www.ambitionbox.com/profiles/sap-abap-associate-consultant/interview-questions
- Accenture SAP ABAP 면접 질문 34개 (Telegram 공개 채널): https://t.me/s/codingsolution_IT/14817
- Exercism ABAP 트랙 연습 목록: https://github.com/exercism/abap

Glassdoor 면접 후기
- SAP 벵갈루루 2021 (필기 36문항/90분, ABAP OO): https://www.glassdoor.co.uk/Interview/SAP-Interview-E10471-RVW1341725.htm
- SAP ABAP Developer 면접 후기 (레거시 ABAP 36문항·90분): https://static.glassdoor.com.br/Interview/SAP-ABAP-Developer-Interview-Questions-EI_IE10471.0,3_KO4,18.htm
- SAP Labs 캠퍼스 채용 (2011, 적성 95문항·90분): https://www.glassdoor.ca/Interview/SAP-Interview-E10471-RVW1229349.htm
- SAP Labs (2011, 적성·고급 컴퓨터·영어 객관식): https://static.glassdoor.de/Interview/SAP-Interview-E10471-RVW1333180.htm
- SAP "SAP ABAP Developer" (2025~2026: DDIC~BTP, 대용량 SELECT, 싱글톤, OData CRUDQ): https://static-pc.glassdoor.de/Interview/SAP-SAP-ABAP-Developer-Interview-Questions-EI_IE10471.0,3_KO4,22.htm
- Capgemini (OO ABAP·BDC·ALV, BAdI 안 COMMIT WORK): https://www.glassdoor.co.nz/Interview/Capgemini-Interview-E3803-RVW16314151.htm
- Accenture SAP ABAP Developer (RICEFW, enhancement point/section): https://static-pc.glassdoor.de/Interview/Accenture-SAP-ABAP-Developer-Interview-Questions-EI_IE4138.0,9_KO10,28_IP3.htm
- Infosys (적성 → 기술, 메모장 코드 작성): https://www.glassdoor.sg/Interview/Infosys-Interview-E7927-RVW63485517.htm
- SAP ABAP 질문 목록 (Accenture: BDC 방식, SmartForms, 페이지 보호, Exit 찾기): https://static.glassdoor.de/Interview/sap-abap-interview-questions-SRCH_KO0,8_IP70.htm
- ABAP 질문 (Volkswagen, SAP: VF03 디버깅·변수 교환, ALSTOM: RFC/OData/ALE/CDS): https://static.glassdoor.fr/Interview/abap-interview-questions-SRCH_KO0,4_IP78.htm
- ABAP 질문 (Capgemini: CHAIN·RFC 디버깅, Deloitte: 데이터 전송·이관 설계): https://static.glassdoor.ch/Interview/abap-interview-questions-SRCH_KO0,4_IP37.htm
- SAP ABAP Developer 질문 (Infosys TMG 이벤트, Booking.com 스테이징 테이블·AMDP): https://static.glassdoor.it/Interview/sap-abap-developer-interview-questions-SRCH_KO0,18_IP46.htm
- SAP ABAP Developer 질문 (Accenture RICEF·Enhancement Point): https://static.glassdoor.it/Interview/sap-abap-developer-interview-questions-SRCH_KO0,18_IP69.htm
- SAP ABAP Developer 질문 (V3iT data/delivery class, OData): https://static.glassdoor.es/Interview/sap-abap-developer-interview-questions-SRCH_KO0,18_IP18.htm
- SAP ABAP Developer 질문 (공개 부분, Binary Search 등): https://static.glassdoor.fr/Interview/sap-abap-developer-interview-questions-SRCH_KO0,18_IP84.htm
- ABAP Developer 질문 (TCS 풀·클러스터 테이블, Brightspot ALV·모듈풀, SAP Fioneer 성능): https://static.glassdoor.fr/Interview/abap-developer-interview-questions-SRCH_KO0,14_IP44.htm
- ABAP Developer 후기 (TMG Events, Lock object): https://static.glassdoor.it/Interview/abap-developer-interview-questions-SRCH_KO0,14_IP21.htm
- SAP ABAP 기술 리드 질문 (TCS 잠금 유형·DDIC·IDoc): https://static.glassdoor.fr/Interview/sap-abap-developer-technical-lead-interview-questions-SRCH_KO0,33_IP10.htm
- SAP 개발자 면접 후기: https://static.glassdoor.fr/Interview/sap-developer-interview-questions-SRCH_KO0,13_IP742.htm
- "BAPI vs FM" 면접 후기: https://static.glassdoor.fr/Interview/abap-programmer-interview-questions-SRCH_KO0,15_IP66.htm

시험 형식 참고 (모의고사)
- iMocha SAP ABAP Test (10문항·20분): https://www.imocha.io/tests/online-abap-test
- WeCP SAP ABAP Developer Assessment (객관식 위주): https://www.wecreateproblems.com/tests/sap-abap-developer-assessment-test
- eursap – SAP 인증 시험 형식 해설 (80문항·180분, 부분 점수 없음): https://eursap.eu/blog/an-introduction-to-sap-certification-exams-how-to-make-the-most-of-your-sap-certification-attempt
- SAP Korea 뉴스 – SeSAC 클라우드 애플리케이션 개발자 과정: https://news.sap.com/korea/?p=7661
- 바이라인네트워크 – 같은 과정 6기 모집 (2026): https://byline.network/2026/05/18-579/
- 아이뉴스24 – SAP코리아 클라우드 인재 양성 과정 (2020): https://www.inews24.com/view/1254609
- 고려대 경영대 취업 후기 – SAP Sales Academy: https://biz.korea.ac.kr/cdc/board/review_view?no=18
- 코멘토 – SAP 컨설턴트 취업 준비 질문: https://comento.kr/job-questions/%EB%AA%A8%EB%93%A0%ED%9A%8C%EC%82%AC/%EB%AA%A8%EB%93%A0%EC%A7%81%EB%AC%B4/sap_%EC%BB%A8%EC%84%A4%ED%84%B4%ED%8A%B8%20%EC%B7%A8%EC%97%85%EC%A4%80%EB%B9%84-633865
