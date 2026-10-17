# 01. ABAP 기초 (문법 · 내부 테이블 · SQL)

데이터 타입·문자열·날짜, 제어문과 시스템 필드, 생성자 표현식, 필드 심볼·참조·구조체, 내부 테이블, ABAP SQL, 알고리즘 손코딩을 통합 문제로 묶었다. 한 문제 안의 소문항 (1)(2)…를 모두 풀면 원본 문제들이 묻던 내용을 빠짐없이 복습하게 된다. ABAP 7.40 SP08 이상 / ABAP Cloud 문법 기준, 예제 데이터는 SFLIGHT 계열(SCARR, SPFLI, SFLIGHT, SBOOK).

## 데이터 타입과 변수

### A-001. 기본 타입·선언 방식·p 타입·변수 수명 [개념] ★★
<!-- src: AB-001, AB-002, AB-003, MX-015 -->
신입 개발자가 금액 계산 리포트를 만들면서 변수 선언 규칙을 정리하고 있다. 다음 물음에 답하시오.

(1) 기본 타입 `c`, `n`, `i`, `p`, `d`, `t`, `string`, `xstring` 각각에 대해 고정/가변 길이, 초기값, `LENGTH`를 생략했을 때의 기본 길이를 표로 쓰시오. 또 `DATA x.`처럼 `TYPE`/`LIKE` 없이 선언하면 어떤 타입이 되는지, 선언 때 `LENGTH`/`DECIMALS`를 정해야 하는(generic 길이) 타입 네 가지를 쓰시오.

(2) `DATA ... TYPE`과 `DATA ... LIKE`의 차이, `TYPES`와 `DATA`의 차이를 쓰시오.

(3) 인라인 선언 `DATA(...)`와 `FINAL(...)`의 타입 결정 방식과 차이를 쓰고, 다음 인라인 변수의 타입(과 값)을 쓰시오.
```abap
DATA(a) = 'abc'.
DATA(b) = `abc`.
DATA(c) = 7 / 2.
SELECT * FROM scarr INTO TABLE @DATA(itab).   " itab의 테이블 종류와 키
```
루프 안에 인라인 선언을 쓰면 반복할 때마다 새로 선언되는가?

(4) `DATA lv_amt TYPE p LENGTH 8 DECIMALS 2.`의 저장 가능 자릿수, 정수부 자릿수, 최대값을 계산 근거와 함께 쓰시오.

(5) 금액 계산에 `f`가 아니라 `p`나 `decfloat34`를 쓰는 이유를 쓰고, DDIC `CURR`/`QUAN`/`DEC`가 ABAP에서 어떤 타입이 되는지, 대입 시와 계산 중 범위를 넘을 때 각각 발생하는 예외, 프로그램 속성 "Fixed point arithmetic"의 의미를 쓰시오.

(6) 다음 코드의 출력 세 줄을 쓰고 이유를 설명하시오(서식 무시).
```abap
START-OF-SELECTION.
  DO 3 TIMES.
    PERFORM count USING sy-index.
  ENDDO.

FORM count USING pv_idx TYPE i.
  STATICS sv_sum TYPE i.
  DATA lv_loc TYPE i VALUE 100.
  sv_sum = sv_sum + pv_idx.
  lv_loc = lv_loc + pv_idx.
  WRITE: / sv_sum, lv_loc.
ENDFORM.
```

<details><summary>정답·해설</summary>

**(1)**

| 타입 | 길이 | 초기값 | 기본 길이 |
|---|---|---|---|
| `c` | 고정 | 공백(blank) | 1자 |
| `n` | 고정 | 모두 `'0'` | 1자 |
| `i` | 고정(4바이트) | 0 | - (범위 −2,147,483,648 ~ 2,147,483,647, 약 ±21억) |
| `p` | 고정 | 0 | 8바이트(15자리), `DECIMALS` 생략 시 0 |
| `d` | 고정 8자 `YYYYMMDD` | `'00000000'` | 8 |
| `t` | 고정 6자 `HHMMSS` | `'000000'` | 6 |
| `string` | 가변 | 빈 문자열(길이 0) | - |
| `xstring` | 가변 | 빈 바이트열(길이 0) | - |

- `DATA x.` → `c LENGTH 1`.
- generic 길이 타입: `c`, `n`, `p`, `x`(`p`는 `DECIMALS`도). 나머지 기본 타입은 complete type.
- `n`은 숫자 문자(numeric text)로, 계산용이 아니라 우편번호·자재번호처럼 앞자리 0이 의미 있는 값에 쓴다.
- `d`, `t`는 문자형이면서 계산도 된다(날짜 − 날짜 = 일수, 시간 − 시간 = 초).
- `CLEAR`는 위 초기값으로 되돌리고 `IS INITIAL`도 이 값과 비교한다.

**(2)** `TYPE`은 데이터 타입(기본 타입, `TYPES`로 정의한 로컬 타입, DDIC 타입)을 참조하고, `LIKE`는 이미 존재하는 데이터 객체(변수)를 참조해 같은 타입으로 선언한다. `TYPES`는 메모리를 차지하지 않는 타입 정의일 뿐이고, `DATA`는 실제 메모리를 갖는 데이터 객체를 만든다.

**(3)** 인라인 선언은 오른쪽 피연산자(또는 문장의 결과 위치)의 정적 타입을 그대로 가져와 그 자리에서 변수를 선언한다. `DATA(x)`는 이후 값을 바꿀 수 있고, `FINAL(x)`는 한 번 대입한 뒤 바꿀 수 없는 불변 변수다(7.57 이상/ABAP Cloud).
- `a` → `c LENGTH 3`, `b` → `string`, `c` → `i`이고 값은 4(3.5 반올림).
- `itab` → empty key를 가진 standard table.
- 루프 안에 써도 한 번만 선언된다. 선언 위치 이후 같은 프로시저 전체에서 보인다.

**(4)** `p`는 1바이트에 2자리를 저장하고 마지막 반 바이트는 부호이므로 자릿수 = 2 × 8 − 1 = 15자리. 소수 2자리를 빼면 정수부 13자리, 최대값 9,999,999,999,999.99.

**(5)**
- `f`는 2진 부동소수점이라 0.1 같은 10진 소수를 정확히 표현하지 못해 반올림 오차가 생긴다. `p`(고정 소수점 10진수)와 `decfloat16/34`(10진 부동소수점)는 10진 값을 정확히 표현하므로 금액·수량에 적합하다.
- DDIC `CURR`, `QUAN`, `DEC` → ABAP `p`.
- 대입 시 범위 초과 → `CX_SY_CONVERSION_OVERFLOW`, 계산 중 초과 → `CX_SY_ARITHMETIC_OVERFLOW`.
- "Fixed point arithmetic"이 꺼져 있으면 `p`의 소수점이 무시되므로 반드시 켜 둔다(신규 프로그램/클래스는 기본으로 켜짐).

**(6)**
```
1  101
3  102
6  103
```
`STATICS` 변수는 FORM(또는 메서드)이 끝나도 값이 남아 다음 호출로 이어진다: 1 → 1+2 = 3 → 3+3 = 6. `DATA ... VALUE 100`은 호출할 때마다 새로 만들어져 100으로 초기화된다: 101, 102, 103. 메서드에서는 `STATICS` 대신 클래스 속성을 쓰는 것이 권장된다.

</details>

---

### A-002. 대입 변환·정수 나눗셈·수치 함수·변환 예외 [코드] ★★
<!-- src: AB-004, AB-005, AB-006, AB-007 -->
아래 코드를 보고 물음에 답하시오. (`c`는 끝 공백을 생략해서 써도 된다.)

```abap
DATA lv_c3 TYPE c LENGTH 3.
DATA lv_n5 TYPE n LENGTH 5.
DATA lv_i  TYPE i.
DATA lv_p  TYPE p LENGTH 8 DECIMALS 2.

lv_c3 = 'ABCDEF'.      " (a)
lv_n5 = '1234567'.     " (b)
lv_n5 = 42.            " (c)
lv_i  = '2.5'.         " (d)
lv_i  = ' '.           " (e)
lv_p  = '1.235'.       " (f)
lv_p  = 10 / 3.        " (g)

DATA(a) = 7 / 2.
DATA(b) = 7 DIV 2.
DATA(c) = 7 MOD 2.
DATA(d) = -7 DIV 2.
DATA(e) = -7 MOD 2.
DATA(f) = -7 / 2.
DATA(g) = 2 / 3 * 3.
DATA(h) = CONV decfloat34( 7 / 2 ).

DATA(r1) = round( val = CONV decfloat34( '2.345' ) dec = 2 ).
DATA(r2) = ceil( CONV decfloat34( '-2.5' ) ).
DATA(r3) = floor( CONV decfloat34( '-2.5' ) ).
DATA(r4) = trunc( CONV decfloat34( '-2.7' ) ).
DATA(r5) = abs( -7 ).
DATA(r6) = sign( -5 ).
DATA(r7) = ipow( base = 2 exp = 10 ).
DATA(r8) = nmax( val1 = 3 val2 = 9 val3 = 4 ).
```

(1) (a)~(g) 각 대입 직후 대상 변수의 값을 쓰고, 적용된 변환 규칙(어느 쪽이 잘리는지, 반올림 방식)을 한 줄씩 설명하시오. (g)에서 대상이 `i`였다면 값은?

(2) `a`~`h`의 값을 쓰시오. `DIV`/`MOD`의 결과가 결정되는 관계식과 `g`가 3이 되는 이유를 설명하시오.

(3) 자릿수 분해처럼 몫이 필요할 때 `/` 대신 무엇을 써야 하는지 쓰시오.

(4) `r1`~`r8`의 값을 쓰시오. `round`의 기본 반올림 모드와 바꾸는 방법, 소수부를 돌려주는 함수, `nmax`/`nmin`의 인수 개수 한도를 쓰시오.

(5) 다음 중 **옳지 않은** 것을 고르고 나머지가 옳은 이유를 쓰시오.
① `DATA lv_i TYPE i.`에 `'ABC'`를 대입하면 `CX_SY_CONVERSION_NO_NUMBER` 예외가 발생한다.
② `DATA lv_c TYPE c LENGTH 3.`에 `'ABCDE'`를 대입하면 `'ABC'`가 된다.
③ `DATA lv_p TYPE p LENGTH 3 DECIMALS 2.`에 1000을 대입하면 `CX_SY_CONVERSION_OVERFLOW` 예외가 발생한다.
④ 길이 5인 `c` 변수에 `'AB'`가 들어 있을 때 이를 `string` 변수에 대입하면 `strlen( )` 결과는 5이다.
⑤ `d` 타입 변수에 `'20240230'`처럼 존재하지 않는 날짜 문자열을 대입해도 대입 시점에는 예외가 나지 않는다.

<details><summary>정답·해설</summary>

**(1)** (a) `ABC` (b) `34567` (c) `00042` (d) `3` (e) `0` (f) `1.24` (g) `3.33`
- (a) `c` → `c`: 왼쪽부터 복사하고 넘치는 오른쪽이 잘린다.
- (b) `c` → `n`: 숫자만 오른쪽 정렬로 옮기고 대상이 짧으면 **왼쪽**이 잘린다(`12`가 사라짐).
- (c) `i` → `n`: 오른쪽 정렬, 남는 앞자리는 0.
- (d) 문자 → `i`: 상업적 반올림(0.5는 0에서 먼 쪽으로), 2.5 → 3.
- (e) 공백만 있는 문자는 0. 숫자가 아닌 문자(`'ABC'`)면 `CX_SY_CONVERSION_NO_NUMBER`.
- (f) 소수 3자리를 2자리로 상업적 반올림.
- (g) 대상이 `p`이므로 계산 타입(calculation type)이 `p`가 되어 3.333…을 소수 2자리로 반올림. 대상이 `i`였다면 3.

**(2)** a = 4, b = 3, c = 1, d = −4, e = 1, f = −4, g = 3, h = 3.5
- `a`: 피연산자가 모두 `i`라 계산 타입과 인라인 타입이 `i`, 3.5 → 4(흔한 오답 3).
- `DIV`는 정수 몫, `MOD`는 항상 0 이상인 나머지이며 `피제수 = 제수 × DIV + MOD`가 성립하도록 정해진다. −7 = 2 × (−4) + 1 → d = −4, e = 1.
- `f`: −3.5를 0에서 먼 쪽으로 반올림해 −4.
- `g`: 계산 타입 `i`에서는 나눗셈 중간 결과도 정수로 반올림된다. 2/3 = 0.67 → 1, 1 × 3 = 3.
- `h`: `CONV decfloat34( )` 안의 식은 계산 타입이 `decfloat34`라 3.5가 정확히 나온다.

**(3)** 반드시 `DIV`(나머지는 `MOD`)를 쓴다.

**(4)** r1 = 2.35, r2 = −2, r3 = −3, r4 = −2, r5 = 7, r6 = −1, r7 = 1024, r8 = 9
- `round`의 기본 모드는 `cl_abap_math=>round_half_up`, `mode` 파라미터로 half_even 등을 지정한다.
- `ceil`은 크거나 같은 가장 작은 정수, `floor`는 작거나 같은 가장 큰 정수, `trunc`는 정수부, `frac`는 소수부.
- `sign`은 −1/0/1, `ipow`는 거듭제곱, `nmax`/`nmin`은 최대 9개 인수 중 최대/최소.

**(5)** ④
- ④ 틀림: `c` → `string` 대입 시 끝 공백이 제거되어 `strlen` = 2.
- ① 숫자로 해석할 수 없는 문자열은 변환 예외. ② `c` → `c`는 오른쪽이 잘린다. ③ `p LENGTH 3`은 5자리, 소수 2자리면 최대 999.99라 1000은 overflow.
- ⑤ `c` → `d`는 문자를 그대로 복사할 뿐 유효성 검사를 하지 않는다. 유효성은 `cl_abap_datfm` 같은 클래스나 날짜 계산 결과로 따로 확인한다.

</details>

---

## 문자열 처리

### A-003. 리터럴·끝 공백·연결·SPLIT/FIND/REPLACE·CONDENSE·오프셋 [코드] ★★
<!-- src: AB-008, AB-009, AB-010, AB-011 -->
문자열 처리 코드를 추적한다.

```abap
" [블록 1]
DATA lv_c TYPE c LENGTH 10 VALUE 'SAP'.
DATA lv_s TYPE string.
DATA lv_r TYPE string.
lv_s = lv_c.
DATA(len1) = strlen( lv_c ).
DATA(len2) = strlen( lv_s ).
lv_r = lv_c && '-' && `ABAP `.
DATA(len3) = strlen( lv_r ).
CONCATENATE lv_c 'X' INTO lv_r SEPARATED BY space.
DATA(len4) = strlen( lv_r ).

" [블록 2]
DATA(lv_text) = `SAP,ABAP,,RAP`.
SPLIT lv_text AT `,` INTO TABLE DATA(lt_parts).
DATA(n1) = lines( lt_parts ).
FIND ALL OCCURRENCES OF `A` IN lv_text MATCH COUNT DATA(n2).
REPLACE ALL OCCURRENCES OF `AP` IN lv_text WITH `*`.
DATA(rc1) = sy-subrc.
FIND `,` IN lv_text MATCH OFFSET DATA(off).
FIND `XYZ` IN lv_text.
DATA(rc2) = sy-subrc.

" [블록 3]
DATA lv_c12 TYPE c LENGTH 12 VALUE '  hello  sap'.
CONDENSE lv_c12.
TRANSLATE lv_c12 TO UPPER CASE.
DATA(lv_b) = lv_c12(5).
DATA(lv_a) = lv_c12+6(3).
SHIFT lv_c12 BY 6 PLACES.
DATA(len) = strlen( lv_c12 ).
DATA(lv_d) = to_lower( substring( val = `ABAPCloud` off = 4 len = 5 ) ).
DATA(lv_e) = `a b  c`.
CONDENSE lv_e NO-GAPS.
```

(1) `'ABC'`, `` `ABC` ``, `|ABC|` 세 표기의 데이터 타입과 끝 공백 처리 차이를 쓰고, 공백 하나를 `&&`로 붙일 때 `' '` 대신 무엇을 써야 하는지와 그 이유(`space` 상수의 타입 포함)를 쓰시오. 문자열 템플릿에서 쓰는 이스케이프 예를 쓰시오.

(2) [블록 1]의 `len1`~`len4`와 마지막 `lv_r`을 쓰시오. `CONCATENATE`에서 끝 공백까지 살리려면 무엇을 붙이는가?

(3) [블록 2]의 `n1`, `n2`, 치환 후 `lv_text`, `rc1`, `off`, `rc2`를 쓰시오. `REPLACE`의 `sy-subrc` 값 0/2/4의 의미를 쓰시오.

(4) [블록 3]의 `lv_b`, `lv_a`, `len`, `lv_d`, `lv_e`를 쓰시오. `CONDENSE`와 `CONDENSE ... NO-GAPS`의 차이를 쓰시오.

<details><summary>정답·해설</summary>

**(1)**
- `'ABC'`: 텍스트 필드 리터럴, 타입 `c`(길이 = 문자 수). 대부분의 연산에서 끝 공백이 무시된다(`'AB  '`의 `strlen`은 2).
- `` `ABC` ``: 텍스트 문자열 리터럴, 타입 `string`, 끝 공백 유지.
- `|ABC|`: 문자열 템플릿, 결과 `string`. `{ }` 안에 변수·식·함수 호출과 포맷 옵션(`DATE`, `ALPHA`, `WIDTH` 등)을 넣는다. 이스케이프 `\n`, `\t`, `\{`, `\|`.
- `' '`는 `&&` 연결 시 끝 공백으로 취급되어 사라지므로 `` ` ` ``를 쓴다. `space` 상수도 `c` 타입이라 같은 문제가 있다.

**(2)** len1 = 3, len2 = 3, len3 = 9, len4 = 5, `lv_r` = `SAP X`
- `c`의 `strlen`은 끝 공백을 세지 않는다. `string`으로 대입할 때도 끝 공백이 빠진다.
- `&&`는 `c` 피연산자의 끝 공백을 무시: `SAP` + `-` + `ABAP `(string이라 공백 유지) = `SAP-ABAP `(9).
- `CONCATENATE`도 `c`의 끝 공백을 무시하고 구분자 `space`를 넣는다. 끝 공백을 살리려면 `RESPECTING BLANKS`.

**(3)** n1 = 4, n2 = 4, `lv_text` = `S*,AB*,,R*`, rc1 = 0, off = 2, rc2 = 4
- `SPLIT`: 연속 구분자(`,,`) 사이의 빈 문자열도 한 행 → `SAP`, `ABAP`, (빈 값), `RAP`.
- `A`: S**A**P,**A**B**A**P,,R**A**P → 4개.
- `AP`가 3번 치환된다. `REPLACE`의 `sy-subrc`: 0 = 하나 이상 치환, 2 = 치환했지만 대상이 잘림, 4 = 못 찾음.
- 치환 후 첫 `,`는 오프셋 2(0부터). `FIND` 실패는 `sy-subrc` = 4.

**(4)** lv_b = `HELLO`, lv_a = `SAP`, len = 3, lv_d = `cloud`, lv_e = `abc`
- `CONDENSE`: 앞 공백 제거, 중간 연속 공백을 하나로 → `hello sap` → 대문자 `HELLO SAP`. 오프셋: H(0)…O(4), 공백(5), S(6) A(7) P(8).
- `lv_c12(5)` = 처음 5자, `lv_c12+6(3)` = 오프셋 6부터 3자.
- `SHIFT ... BY 6 PLACES`(기본 LEFT) → `SAP` 뒤는 공백, `c`의 `strlen`은 3.
- `substring` 오프셋 4부터 5자 = `Cloud` → `cloud`.
- `NO-GAPS`는 모든 공백 제거.

</details>

---

### A-004. 비교 연산자·템플릿 포맷·ALPHA 변환·내장 함수·오류 수정 [코드] ★★
<!-- src: AB-012, AB-013, AB-014, AB-015, MX-003 -->
고객번호와 메시지 문자열을 다루는 코드를 검토한다. (`sy-datum`은 2026년 10월 13일)

(1) 각 `IF` 조건의 참/거짓과 주석 시점의 `sy-fdpos`를 쓰시오. `CS`/`CP`의 대소문자 구분 여부, `CP`의 `*`와 `+`의 의미를 쓰시오.
```abap
DATA(s) = `ABAP-2026`.
IF s CO `0123456789`.   " (a) 참/거짓, sy-fdpos
ENDIF.
IF s CA `0123456789`.   " (b) 참/거짓, sy-fdpos
ENDIF.
IF s CS `abap`.         " (c) 참/거짓, sy-fdpos
ENDIF.
IF s CP `*-2*`.         " (d) 참/거짓
ENDIF.
```

(2) 주석 결과가 나오도록 빈칸을 채우시오. `ALPHA = OUT`, `DATE = RAW`, `DATE = USER`의 의미도 쓰시오.
```abap
DATA lv_matnr TYPE c LENGTH 10 VALUE '1234'.
DATA(s1) = |{ lv_matnr ALPHA = ____①____ }|.                 " 0000001234
DATA(s2) = |{ sy-datum DATE = ____②____ }|.                  " 2026-10-13
DATA(s3) = |{ `abc` CASE = ____③____ }|.                     " ABC
DATA(s4) = |{ 7 WIDTH = 5 ALIGN = ____④____ PAD = '0' }|.    " 00007
DATA(s5) = |Key: ____⑤____LH\}|.                             " Key: {LH}
DATA(s6) = |Line1____⑥____Line2|.                            " 줄바꿈
```

(3) 도메인 `ZMX_CUSTNO`(CHAR 10)에 변환 루틴 ALPHA가 지정되어 있고 Z 테이블 고객번호 필드가 이 도메인을 쓴다. 다음 중 **옳지 않은** 것을 고르고 각 보기를 설명하시오.
① 화면 입력 필드에 `123`을 넣으면 DB에는 `0000000123`으로 저장된다.
② ABAP 코드에서 `WHERE custno = '123'`처럼 리터럴을 쓰면 변환이 자동 적용되지 않아 레코드를 못 찾을 수 있다.
③ `CONVERSION_EXIT_ALPHA_INPUT`에 `ABC`를 넣으면 `0000000ABC`가 된다.
④ 이 필드를 `WRITE`로 출력하면 OUTPUT 루틴이 적용되어 앞의 0 없이 `123`으로 보인다.

(4) 다음 중 **옳지 않은** 것을 고르시오. 대소문자를 구분해 포함 여부를 검사하려면 무엇을 쓰는가?
① ``strlen( `AB  ` )``의 결과는 4이다.
② ``condense( `  a   b ` )``의 결과는 `` `a b` ``이다.
③ ``substring_after( val = `a-b-c` sub = `-` )``의 결과는 `` `b-c` ``이다.
④ `` `abc` CS `B` ``의 결과는 거짓이다.
⑤ ``to_upper( `sap` ) && `!` ``의 결과는 `` `SAP!` ``이다.

(5) 다음 코드의 오류 3곳을 찾아 문법/런타임 오류 구분과 고친 코드를 쓰시오.
```abap
DATA lv_cnt TYPE i VALUE 5.
DATA lv_s   TYPE string VALUE `ABAP`.
DATA lv_msg TYPE string.
CONCATENATE 'Count:' lv_cnt INTO lv_msg SEPARATED BY space.   " (a)
to_upper( lv_s ).                                             " (b)
DATA(lv_part) = lv_s+2(5).                                    " (c)
```

<details><summary>정답·해설</summary>

**(1)** (a) 거짓, sy-fdpos = 0 (b) 참, sy-fdpos = 5 (c) 참, sy-fdpos = 0 (d) 참
- `CO`(contains only): 모든 문자가 집합에 있어야 참. 첫 문자 `A`가 숫자가 아니라 거짓, `sy-fdpos`는 집합에 없는 첫 문자의 오프셋 0.
- `CA`(contains any): 하나라도 있으면 참. 첫 숫자 `2`의 오프셋 5.
- `CS`(contains string)와 `CP`(covers pattern)는 **대소문자를 구분하지 않는다**. `abap`은 오프셋 0에서 일치.
- `CP`의 `*`는 임의 문자열, `+`는 임의 한 문자.

**(2)** ① `IN` ② `ISO` ③ `UPPER` ④ `RIGHT` ⑤ `\{` ⑥ `\n`
- `ALPHA = IN`은 앞에 0을 채워 내부 형식으로, `ALPHA = OUT`은 앞의 0을 지워 외부 형식으로(클래식 `CONVERSION_EXIT_ALPHA_INPUT/OUTPUT`과 같은 역할).
- `DATE = ISO`는 `YYYY-MM-DD`, `RAW`는 `YYYYMMDD`, `USER`는 사용자 설정 형식.
- 템플릿 안에서 `{ } | \`는 특수 문자라 글자 그대로 쓰려면 `\`로 이스케이프.

**(3)** ③
- ③ 틀림: ALPHA 입력 변환은 값이 **숫자로만** 이루어졌을 때만 오른쪽 정렬하고 앞을 0으로 채운다. `ABC`는 왼쪽 정렬 그대로 `ABC`.
- ① 화면 필드는 도메인의 변환 루틴을 자동으로 거친다.
- ② ABAP 코드의 리터럴·변수에는 자동 변환이 없다. `CONVERSION_EXIT_ALPHA_INPUT`을 직접 부르거나 `|{ lv ALPHA = IN }|`를 쓴다.
- ④ `WRITE`는 변환 루틴이 있는 필드에 OUTPUT 함수를 적용한다.

**(4)** ④ — `CS`는 대소문자를 구분하지 않으므로 참이다. 대소문자 구분이 필요하면 `find( val = ... sub = ... case = abap_true )` 같은 함수를 쓴다.
- ① `string`은 끝 공백 유지 → 4. ② `condense` 함수는 앞뒤 공백 제거와 중간 공백 축약. ③ 첫 `-` 뒤 나머지 전체. ⑤ 옳다.

**(5)**
- (a) 문법 오류: `CONCATENATE`의 피연산자는 문자형(또는 바이트형)이어야 하는데 `lv_cnt`가 `i`. → `lv_msg = |Count: { lv_cnt }|.`
- (b) 문법 오류: 내장 함수는 단독 문장으로 쓸 수 없다. → `lv_s = to_upper( lv_s ).` 또는 `TRANSLATE lv_s TO UPPER CASE.`
- (c) 런타임 오류: 길이 4인데 오프셋 2부터 5자를 요구. → `lv_s+2(2)` 또는 `substring( val = lv_s off = 2 )`(len 생략 시 끝까지).
- `string`의 오프셋/길이 접근이 실제 길이를 넘으면 런타임 오류, `substring` 함수도 범위를 넘으면 `CX_SY_RANGE_OUT_OF_BOUNDS`. 가변 길이 값은 `strlen`으로 먼저 확인하거나 `len`을 생략한다.

</details>

---

## 날짜·시간

### A-005. 날짜·시간 산술과 월말 구하기 [코드] ★★
<!-- src: AB-017, AB-020 -->
다음 코드를 보고 물음에 답하시오.

```abap
DATA lv_d1   TYPE d VALUE '20240228'.
DATA lv_d2   TYPE d.
DATA lv_d3   TYPE d VALUE '20240101'.
DATA lv_d4   TYPE d VALUE '20240315'.
DATA lv_diff TYPE i.
DATA lv_t    TYPE t VALUE '235930'.
DATA lv_t3   TYPE t VALUE '080000'.
DATA lv_t4   TYPE t VALUE '073000'.
DATA lv_sec  TYPE i.

lv_d2   = lv_d1 + 2.
lv_diff = lv_d2 - lv_d3.
lv_d4+6(2) = '01'.
lv_d4 = lv_d4 - 1.
lv_t   = lv_t + 60.
lv_sec = lv_t3 - lv_t4.
```

(1) `lv_d2`, `lv_diff`의 값을 쓰고 계산 근거를 쓰시오.

(2) `lv_d4`의 최종 값을 쓰고, 이 두 줄이 어떤 실무 패턴인지 쓰시오.

(3) `lv_t`와 `lv_sec`의 최종 값을 초 단위 계산과 함께 쓰시오. `t` 타입에서 자정을 넘으면 어떻게 되는가?

(4) `d` 타입 `lv_date`가 주어질 때 그 달의 마지막 날짜를 `lv_last`에 구하는 코드를 함수 모듈·클래스 없이 날짜 산술만으로 작성하시오(`20240210` → `20240229`, `20241231` → `20241231`). 이 방법이 윤년과 12월을 자동으로 처리하는 이유를 쓰시오.

<details><summary>정답·해설</summary>

**(1)** lv_d2 = `20240301`, lv_diff = 60. 2024년은 윤년이라 2/28 + 2일 = 2/29 → 3/1. 날짜 − 날짜 = 일수: 1월 31일 + 2월 29일 = 60.

**(2)** lv_d4 = `20240229`. 일자를 `01`로 바꾸면 3월 1일, 하루 빼면 전월 말일. "전월 말일 구하기"의 정석 패턴.

**(3)** lv_t = `000030`, lv_sec = 1800. 23:59:30 = 86,370초 + 60 = 86,430초 → `t`에 대입할 때 86,400으로 나눈 나머지 30초(자정을 넘어 순환). 시간 − 시간 = 초: 28,800 − 27,000 = 1,800.

**(4)**
```abap
DATA lv_date TYPE d VALUE '20240210'.
DATA lv_tmp  TYPE d.
DATA lv_last TYPE d.

lv_tmp = lv_date.
lv_tmp+6(2) = '01'.        " 이번 달 1일
lv_tmp = lv_tmp + 31.      " 1일 + 31일은 반드시 다음 달 안
lv_tmp+6(2) = '01'.        " 다음 달 1일
lv_last = lv_tmp - 1.      " 하루 전 = 이번 달 말일
```
어느 달이든 1일에 31을 더하면 다음 달 1~4일 사이가 된다. 다시 1일로 맞추고 하루를 빼면 윤년까지 자동 처리되고, 12월이면 다음 해 1월 1일 − 1 = 12월 31일로 연도 넘김도 자동 처리된다.

</details>

---

### A-006. 시스템 날짜·시간대·UTC 타임스탬프 [개념] ★★
<!-- src: AB-018, AB-019, TC-079 -->
여러 나라 사용자가 쓰는 시스템에서 주문 생성 시각을 저장하는 기능을 만든다.

(1) `sy-datum`/`sy-uzeit`와 `sy-datlo`/`sy-timlo`의 기준 시간대 차이를 쓰고, 사용자 시간대를 담는 시스템 필드와 `sy-uzeit`의 정밀도를 쓰시오.

(2) 시점을 저장할 때 UTC 타임스탬프를 쓰는 이유와 사용하는 타입(두 가지)을 쓰시오.

(3) ABAP Cloud에서 시스템 날짜·시간·사용자 이름을 얻는 권장 방법과 `sy-` 필드를 직접 쓰면 어떻게 되는지 쓰시오.

(4) 빈칸을 채우시오.
```abap
DATA(lv_today) = cl_abap_context_info=>____①____( ).   " ABAP Cloud 시스템 날짜
DATA(lv_now) = ____②____( ).                           " 현재 UTC 시점(utclong)
DATA lv_ts TYPE timestampl.
GET ____③____ FIELD lv_ts.                              " timestampl 현재 UTC
DATA lv_tz   TYPE timezone.
DATA lv_date TYPE d.
DATA lv_time TYPE t.
lv_tz = cl_abap_context_info=>____⑤____( ).
CONVERT TIME STAMP lv_ts ____④____ lv_tz
        INTO DATE lv_date TIME lv_time.
```
⑤의 메서드를 호출할 때 주의할 점과 반대 방향(날짜·시간 → 타임스탬프) 변환 문장을 쓰시오.

(5) `GET TIME`과 `GET TIME STAMP FIELD`의 차이를 쓰고, 날짜·시간을 사용자 설정 형식으로 표시하는 템플릿 옵션을 쓰시오.

<details><summary>정답·해설</summary>

**(1)** `sy-datum`/`sy-uzeit`는 애플리케이션 서버의 시스템 시간대 기준, `sy-datlo`/`sy-timlo`는 사용자 시간대(로컬) 기준이다. 사용자 시간대는 `sy-zonlo`. `sy-uzeit`는 HHMMSS(초 단위)로 마이크로초가 없다.

**(2)** 서버·사용자 시간대가 다르면 로컬 날짜·시간만으로는 같은 시점을 비교·정렬할 수 없다. UTC 타임스탬프(`timestampl`(또는 `timestamp`), `utclong`)로 저장하고 표시할 때 사용자 시간대로 변환(`CONVERT TIME STAMP`)하면 일관성이 유지된다. RAP의 생성·변경 시각 필드도 UTC 타임스탬프다.

**(3)** `cl_abap_context_info=>get_system_date( )`, `get_system_time( )`, `get_user_technical_name( )`, 그리고 `utclong_current( )`. `sy-datum`/`sy-uzeit` 등을 직접 쓰면 ATC가 경고한다.

**(4)** ① `get_system_date` ② `utclong_current` ③ `TIME STAMP` ④ `TIME ZONE` ⑤ `get_user_time_zone`
- `get_user_time_zone`은 `cx_abap_context_info_error`를 던질 수 있으므로 `TRY ... CATCH`로 감싼다.
- 반대 방향: `CONVERT DATE lv_date TIME lv_time INTO TIME STAMP lv_ts TIME ZONE lv_tz.`

**(5)** `GET TIME`은 `sy-datum`/`sy-uzeit`를 새로 고칠 뿐이고, `GET TIME STAMP FIELD`는 항상 UTC 타임스탬프(TIMESTAMP/TIMESTAMPL)를 돌려준다. 표시 형식은 `DATE = USER`, `TIMESTAMP = USER`.

</details>

---

## 제어문과 시스템 필드

### A-007. 루프 제어·sy-index·술어 표현식 [코드] ★★
<!-- src: AB-021, AB-022, AB-023, TC-076, TC-083 -->
다음 코드를 보고 물음에 답하시오.

```abap
" [블록 1]
DATA lv_sum TYPE i.
DO 10 TIMES.
  IF sy-index MOD 2 = 0.
    CONTINUE.
  ENDIF.
  IF sy-index > 7.
    EXIT.
  ENDIF.
  lv_sum = lv_sum + sy-index.
ENDDO.

" [블록 2]
DATA lv_cnt TYPE i.
DATA lv_str TYPE string.
WHILE lv_cnt < 5.
  lv_cnt = lv_cnt + 1.
  CHECK lv_cnt <> 3.
  lv_str = |{ lv_str }{ lv_cnt }|.
ENDWHILE.

" [블록 3]
DATA lv TYPE string.
DO 3 TIMES.
  DO 2 TIMES.
    lv = lv && |{ sy-index }|.
  ENDDO.
  lv = lv && |({ sy-index })|.
ENDDO.
```

(1) [블록 1]의 `lv_sum` 최종 값과 `EXIT`가 실행될 때의 `sy-index`를 쓰시오.

(2) [블록 2]의 `lv_str`과 `WHILE` 본문 실행 횟수를 쓰시오. `CHECK`가 루프 안에서 거짓일 때와 루프 밖(메서드 등)에서 거짓일 때의 동작 차이를 쓰시오.

(3) [블록 3]의 `lv`를 쓰고, 안쪽 루프가 끝난 뒤 `sy-index`가 어떻게 되는지 설명하시오.

(4) 다음 중 **옳지 않은** 것을 모두 고르고 이유를 쓰시오.
① `LOOP AT`(standard/sorted 테이블) 안에서 `sy-tabix`는 현재 행의 인덱스이다.
② `DO`나 `WHILE` 루프 안에서 `sy-index`는 1부터 시작하는 반복 횟수이다.
③ 메서드 안에서 루프 밖에 있는 `CHECK` 조건이 거짓이면 메서드 처리가 끝난다.
④ 중첩 루프의 안쪽 루프에서 `EXIT`를 실행하면 바깥 루프까지 모두 종료된다.
⑤ `LOOP AT` 대상 테이블이 비어 한 번도 처리하지 않으면 루프 후 `sy-subrc`는 4이다.
⑥ `SELECT ... ENDSELECT`는 `sy-dbcnt`를 설정한다.
⑦ `LOOP AT itab`은 `sy-index`를 설정한다.

(5) 주석의 의미가 되도록 빈칸을 채우시오.
```abap
IF <ls_line> IS ____①____.                   " 필드 심볼이 메모리에 할당되어 있으면
ENDIF.
IF lr_data IS ____②____.                     " 참조 변수가 유효한 대상을 가리키면
ENDIF.
IF lv_fldate ____③____ lv_from AND lv_to.    " lv_from 이상 lv_to 이하이면
ENDIF.
IF lv_carrid ____④____ lr_carrid.            " range 테이블 조건에 맞으면
ENDIF.
DATA(lv_big) = ____⑤____( lv_amount > 1000 ).  " abap_true/abap_false인 c(1)
```
⑤에 `boolc`를 쓰면 안 되는 이유, range 테이블이 비어 있을 때 `IN` 조건의 결과, 그 밖의 술어 세 가지를 쓰시오.

<details><summary>정답·해설</summary>

**(1)** `lv_sum` = 16, `EXIT` 시점 `sy-index` = 9. 짝수는 `CONTINUE`로 건너뛰고 홀수 1, 3, 5, 7을 더해 16. 8은 짝수라 `CONTINUE`, 9에서 `9 > 7`이 참이라 `EXIT`.

**(2)** `lv_str` = `1245`, 본문 5회. `lv_cnt`가 1~5까지 증가하며 본문이 5번 실행되고, 루프 안의 `CHECK`가 거짓이면 `CONTINUE`처럼 나머지를 건너뛰므로 3만 빠진다. 루프 밖의 `CHECK`가 거짓이면 현재 처리 블록(메서드, 서브루틴 등) 전체를 빠져나간다.

**(3)** `12(1)12(2)12(3)`. `sy-index`는 항상 현재(가장 안쪽에서 실행 중인) 루프의 반복 횟수이고, 안쪽 루프를 벗어나면 바깥 루프 값이 복원된다.

**(4)** ④, ⑦
- ④ `EXIT`는 자신을 직접 감싸는 루프 하나만 끝낸다. 바깥까지 끝내려면 플래그를 두거나 메서드에서 `RETURN`.
- ⑦ `LOOP AT`은 `sy-tabix`(인덱스 테이블의 현재 행)와 루프 종료 후 `sy-subrc`(한 번도 안 돌면 4)를 설정하고 `sy-index`는 바꾸지 않는다. 그래서 LOOP 안에서 `sy-index`를 쓰면 바깥 DO의 값이나 의미 없는 값이 나온다.
- ① ② ⑤ ⑥ 옳다(단, hashed 테이블을 primary key로 `LOOP`하면 `sy-tabix` = 0). ③ 옳다. DO·WHILE은 `sy-index`를 설정한다.

**(5)** ① `ASSIGNED` ② `BOUND` ③ `BETWEEN` ④ `IN` ⑤ `xsdbool`
- `xsdbool`은 `abap_bool`(c 길이 1)을 돌려줘 `abap_true`/`abap_false`와 안전하게 비교된다. `boolc`는 `string`을 돌려줘 거짓일 때 공백 하나짜리 문자열이 되어 `abap_false`와 비교하면 의도와 다른 결과가 날 수 있다.
- range 테이블이 비어 있으면 `IN` 조건은 항상 참.
- 그 밖의 술어: `IS INITIAL`, `IS SUPPLIED`(선택 파라미터 전달 여부), `IS INSTANCE OF`.

</details>

---

### A-008. 시스템 필드 총정리(의미·리스트·화면·실행 환경) [개념] ★★
<!-- src: TC-073, TC-074, TC-081, TC-082, TC-085, TC-086 -->
시스템 필드는 서면 시험에서 표 채우기로 자주 나온다.

(1) 다음 표의 빈칸(의미 또는 필드 이름)을 채우시오.

| 번호 | 필드 | 의미 |
|---|---|---|
| a | sy-subrc | |
| b | sy-tabix | |
| c | sy-index | |
| d | sy-dbcnt | |
| e | sy-fdpos | |
| f | sy-datum / sy-uzeit | |
| g | sy-uname | |
| h | sy-mandt | |
| i | sy-langu | |
| j | sy-tcode | |
| k | sy-repid | |
| l | | 실행 중인 메인 프로그램 이름(include·외부 서브루틴 호출 시 호출한 메인 프로그램) |
| m | | 시스템 ID(예: DEV) |
| n | | 사용자 시간대 기준 현재 날짜 / 시간 |
| o | | 사용자 시간대 |
| p | | 실행에 사용한 선택 화면 변형 이름 |
| q | sy-host / sy-saprl / sy-dbsys | |

(2) 화면(Dynpro) 관련: 다음 표를 채우시오. 모듈 풀에서 `sy-ucomm`을 직접 쓰지 않는 이유, Table Control PAI에서 내부 테이블 인덱스를 계산하는 식, `sy-datar`의 활용 예를 쓰시오.

| 필드 | 의미 | 필드 | 의미 |
|---|---|---|---|
| | 화면에서 누른 버튼·메뉴의 기능 코드(PAI를 발생시킨 코드) | sy-dyngr | |
| | 현재 화면 번호 | sy-stepl | |
| | 현재 GUI Status 이름 | sy-loopc | |
| sy-title | | sy-datar | |

(3) 클래식 리스트 관련: `sy-lsind`, `sy-lisel`, `sy-lilli`, `sy-pagno`, `sy-linno`, `sy-linsz`, `sy-linct`, `sy-colno`, `sy-curow`/`sy-cucol`, `sy-vline`, `sy-uline`의 의미를 쓰시오. 이 중 프로그램에서 값을 써도 의미가 있는 필드와 그 용도를 쓰시오.

(4) 실행 환경 분기: 다음 상황에서 어떤 시스템 필드로 분기하는지와 이유를 쓰시오.
- a. 같은 리포트를 온라인에서는 ALV로, 백그라운드 작업에서는 스풀/로그로 출력
- b. 확인 팝업(POPUP_TO_CONFIRM)을 Batch Input 처리 중에는 띄우지 않음
- c. 다른 트랜잭션에서 CALL TRANSACTION으로 호출되었을 때 "뒤로" 처리 방식을 바꿈

백그라운드에서 화면을 보내면 나는 런타임 오류 이름과, ABAP Cloud에서 백그라운드 처리를 하는 방식을 쓰시오.

(5) 다음 중 **옳지 않은** 것을 고르고 이유를 쓰시오.
① 시스템 필드는 ABAP Dictionary 구조 SYST로 정의되어 있다.
② 메서드·함수 모듈의 파라미터로 시스템 필드를 직접 넘기면 호출된 쪽에서 값이 바뀌어 의도와 다를 수 있으므로 지역 변수에 복사해 넘기는 것이 좋다.
③ sy-repid는 include 안에서도 include 이름이 아니라 그 include가 속한 프로그램 이름을 갖는다.
④ 프로그램에서 sy-subrc에 값을 대입하는 것은 문법 오류다.
⑤ RFC로 호출된 함수 모듈 안의 sy-uname은 RFC destination에 지정된 로그온 사용자다.

<details><summary>정답·해설</summary>

**(1)**
- a 직전 문장의 반환 코드(0 = 성공) / b 내부 테이블의 현재 행 인덱스(LOOP, READ TABLE, APPEND 등) / c DO·WHILE의 현재 반복 횟수 / d DB 문장으로 처리(읽기·변경)된 행 수 / e 문자열 비교·검색에서 찾은 위치(오프셋) / f 애플리케이션 서버의 현재 날짜(YYYYMMDD) / 시간(HHMMSS) / g 로그온 사용자 ID / h 로그온 클라이언트 / i 로그온 언어(1자리 내부 코드) / j 현재 트랜잭션 코드 / k 현재 실행 중인 프로그램 이름
- l sy-cprog / m sy-sysid / n sy-datlo / sy-timlo / o sy-zonlo / p sy-slset
- q 애플리케이션 서버 이름 / 릴리스 / DB 시스템
- 시스템 필드는 DDIC 구조 SYST로 정의되고 프로그램에서는 `sy`(또는 `syst`)로 접근한다. 읽기 전용으로 취급한다.

**(2)**

| 필드 | 의미 | 필드 | 의미 |
|---|---|---|---|
| sy-ucomm | 기능 코드 | sy-dyngr | 현재 화면의 화면 그룹 |
| sy-dynnr | 현재 화면 번호 | sy-stepl | Table Control·Step Loop의 현재 화면 행(보이는 영역 기준 1부터) |
| sy-pfkey | 현재 GUI Status | sy-loopc | Table Control·Step Loop에서 현재 보이는 행 수 |
| sy-title | 현재 제목 표시줄 텍스트 | sy-datar | 화면에서 사용자가 값을 입력·변경했으면 'X' |

- 모듈 풀에서는 화면 요소 목록의 OK 필드(ok_code)에 받아 사용·초기화한다.
- 인덱스 = `tc-top_line + sy-stepl - 1`(`LOOP WITH CONTROL` 사용 시 `tc-current_line`으로도 얻는다).
- `sy-datar`는 "변경 사항을 저장하시겠습니까?" 팝업 여부 판단에 쓴다.

**(3)**
- sy-lsind 현재 생성 중인 리스트 레벨(0 기본 리스트, 상세 리스트 1~20) / sy-lisel 선택(더블클릭)된 리스트 행의 내용 / sy-lilli 선택된 행의 리스트 내 절대 행 번호 / sy-pagno 현재 페이지 번호 / sy-linno 현재 페이지에서 출력 위치의 행 번호 / sy-linsz 리스트 폭(LINE-SIZE) / sy-linct 페이지당 행 수(LINE-COUNT, 0이면 무한) / sy-colno 현재 출력 위치의 열 번호 / sy-curow·sy-cucol 화면에서 커서가 있는 행·열 / sy-vline 세로선 문자 `|` / sy-uline 가로선(`WRITE sy-uline` 또는 `ULINE`)
- 쓰기가 의미 있는 필드: `sy-lsind`. 상세 리스트에서 `sy-lsind = sy-lsind - 1`처럼 줄이면 이전 레벨 리스트를 덮어쓸 수 있다.

**(4)**
- a. `sy-batch = 'X'`: 백그라운드에는 GUI가 없어 팝업·GUI 컨트롤(컨테이너 ALV), PC 파일 처리를 할 수 없다. 리스트(WRITE/SALV 전체 화면)는 스풀로 저장된다.
- b. `sy-binpt = 'X'`: Batch Input(BDC 세션 또는 CALL TRANSACTION)은 녹화된 화면 순서대로 값을 넣으므로 예상하지 않은 팝업이 끼면 처리가 어긋난다.
- c. `sy-calld = 'X'`: 호출된 트랜잭션에서 LEAVE PROGRAM/LEAVE TO SCREEN 0으로 호출자에게 돌아가게 한다.
- 백그라운드에서 화면을 보내면 `DYNPRO_SEND_IN_BACKGROUND`. ABAP Cloud에서는 Application Job으로 처리하며 이런 GUI 분기가 필요 없다.

**(5)** ④ — 문법상 대입은 가능하다(함수 모듈이나 메서드 끝에서 sy-subrc를 명시적으로 세팅하는 코드도 있다). 다만 읽기 전용으로 취급하는 것이 원칙이고, 쓰기가 의미 있는 대표 예가 sy-lsind다. ② 시스템 필드는 실행 중 계속 바뀌므로 복사본을 넘기라는 것이 가이드라인이다. ⑤ 그래서 RFC 사용자가 공용 계정이면 변경자 기록에 주의한다.

</details>

---

### A-009. sy-subrc·sy-tabix·sy-dbcnt·메시지 필드 추적 [코드] ★★★
<!-- src: AB-024, TC-075, TC-077, TC-078, TC-080, TC-084 -->
반환 코드와 관련 시스템 필드를 추적한다.

(1) 다음 코드 실행 후 r1~r8의 값을 쓰시오.
```abap
DATA itab   TYPE STANDARD TABLE OF i WITH EMPTY KEY.
DATA hashed TYPE HASHED TABLE OF i WITH UNIQUE KEY table_line.
DATA r6     TYPE string.

APPEND 10 TO itab.  DATA(r1) = sy-tabix.
APPEND 20 TO itab.  DATA(r2) = sy-tabix.
APPEND 30 TO itab.
READ TABLE itab WITH KEY table_line = 30 TRANSPORTING NO FIELDS.
DATA(r3) = sy-tabix.
DATA(r4) = sy-subrc.
READ TABLE itab WITH KEY table_line = 99 TRANSPORTING NO FIELDS.
DATA(r5) = sy-subrc.
LOOP AT itab INTO DATA(v) WHERE table_line >= 20.
  r6 = r6 && |{ sy-tabix }|.
ENDLOOP.
INSERT 7 INTO TABLE hashed.
INSERT 7 INTO TABLE hashed.
DATA(r7) = sy-subrc.
LOOP AT hashed INTO DATA(h).
  DATA(r8) = sy-tabix.
ENDLOOP.
```

(2) 다음 문장 실행 뒤 `sy-subrc` 값의 의미를 쓰시오.
- a. `SELECT SINGLE` — 0, 4
- b. `READ TABLE ... BINARY SEARCH` — 0, 4, 8 (각각의 `sy-tabix` 포함)
- c. `AUTHORITY-CHECK OBJECT` — 0, 4, 12
- d. `INSERT dbtab FROM wa` — 0, 4
- e. `CALL FUNCTION ... EXCEPTIONS not_found = 1 OTHERS = 2` — 1, 2
- f. `CALL FUNCTION 'ENQUEUE_EZ_FLIGHT' EXCEPTIONS foreign_lock = 1 system_failure = 2` — 1 (잠금 사용자는 어디에?)
- g. `MODIFY dbtab FROM wa` — 0
- h. `ASSIGN COMPONENT 'X' OF STRUCTURE ls TO <fs>` — 4 (필드 심볼 상태는?)

(3) `sy-dbcnt`에 대한 설명 중 **옳지 않은** 것을 고르시오. 그 경우 삭제 건수는 어떻게 구하는가?
① `UPDATE zflight SET price = 100 WHERE carrid = 'LH'.` 후 변경된 행 수가 들어 있다.
② `SELECT ... INTO TABLE` 후 읽은 행 수가 들어 있다.
③ `SELECT ... ENDSELECT` 루프 안에서는 지금까지 읽은 행 수(현재 행 번호)가 들어 있다.
④ `DELETE FROM zflight WHERE ...` 후 삭제된 행 수가 들어 있다.
⑤ 내부 테이블에 대한 `DELETE itab WHERE ...` 후 삭제된 행 수가 들어 있다.

(4) 다음 코드는 항공편이 내부 테이블에 없을 때만 DB에서 읽으려는 의도다. 잘못된 곳을 찾아 고치시오. `sy-subrc`를 언제 확인해야 하는지, `sy-subrc`를 설정하지 않는 문법(예: table expression, `line_exists( )`, 생성자 표현식, 함수형 메서드 호출)이 있다는 점이 왜 중요한지, sy-subrc에 의존하지 않는 대안 두 가지를 쓰시오.
```abap
READ TABLE gt_flight INTO DATA(ls_flight)
     WITH KEY carrid = p_carr connid = p_conn.
SELECT SINGLE carrname FROM scarr
  WHERE carrid = @p_carr
  INTO @DATA(lv_name).
IF sy-subrc <> 0.
  SELECT SINGLE * FROM sflight
    WHERE carrid = @p_carr AND connid = @p_conn
    INTO @ls_flight.
ENDIF.
```

(5) 함수 모듈이 E 메시지로 끝나거나 BAPI가 오류를 돌려줄 때 같은 메시지를 다시 표시하는 코드다. 빈칸을 채우고 `EXCEPTIONS error_message = n`의 효과, BAPIRET2의 주요 필드, `MESSAGE ... INTO`의 동작을 쓰시오.
```abap
CALL FUNCTION 'Z_CHECK_FLIGHT'
  EXPORTING
    iv_carrid     = 'LH'
  EXCEPTIONS
    error_message = 1
    OTHERS        = 2.
IF sy-subrc <> 0.
  MESSAGE ID ____①____ TYPE ____②____ NUMBER ____③____
          WITH sy-msgv1 sy-msgv2 sy-msgv3 sy-msgv4.
ENDIF.

DATA lt_return TYPE STANDARD TABLE OF bapiret2.
" ... BAPI 호출 ...
LOOP AT lt_return INTO DATA(ls_ret) WHERE type CA 'EA'.
  MESSAGE ID ls_ret-____④____ TYPE 'I' NUMBER ls_ret-____⑤____
          WITH ls_ret-message_v1 ls_ret-message_v2
               ls_ret-message_v3 ls_ret-message_v4
          ____⑥____ DATA(lv_text).        " 표시하지 않고 텍스트만 받기
ENDLOOP.
```

<details><summary>정답·해설</summary>

**(1)** r1 = 1, r2 = 2, r3 = 3, r4 = 0, r5 = 4, r6 = `23`, r7 = 4, r8 = 0
- APPEND는 `sy-tabix`에 추가된 행의 인덱스를 넣는다.
- 99는 없음 → 4(선형 검색에서 못 찾으면 4. 8은 BINARY SEARCH/정렬 키 검색에서 끝을 넘어설 때).
- LOOP ... WHERE의 `sy-tabix`는 조건에 맞는 행의 원래 인덱스(2, 3)다.
- 유일 키 중복 `INSERT ... INTO TABLE`은 오류 없이 무시되고 sy-subrc = 4.
- 해시 테이블은 인덱스가 없어 `sy-tabix` = 0. `DATA(r8)`은 루프 안에 있어도 프로그램(메서드) 전체에서 유효하다.

**(2)**
- a. 0 한 건 읽음 / 4 해당 행 없음
- b. 0 찾음(그 행 인덱스) / 4 못 찾음(`sy-tabix` = 삽입될 위치) / 8 못 찾음, 키가 모든 행보다 커서 끝에 추가될 위치(`sy-tabix` = 행 수 + 1)
- c. 0 권한 있음 / 4 해당 값에 대한 권한 없음 / 12 그 권한 객체에 대한 권한 자체가 없음
- d. 0 삽입 성공 / 4 같은 기본 키 행이 이미 있어 삽입 안 됨
- e. 1 함수 모듈이 `RAISE not_found` 실행 / 2 선언하지 않은 다른 예외
- f. 1 다른 사용자가 잠금 보유 중(잠금 사용자는 `sy-msgv1`)
- g. 0 삽입 또는 갱신 성공(없으면 INSERT, 있으면 UPDATE)
- h. 4 해당 이름의 컴포넌트가 없어 할당 실패(필드 심볼은 이전 상태 유지)
- 0은 성공, 그 외 값은 문장마다 의미가 다르다(예: `READ TABLE` 4/8, 단일 행 `INSERT` 4).

**(3)** ⑤ — `sy-dbcnt`는 ABAP SQL(DB) 문장만 설정한다. 내부 테이블 DELETE는 sy-subrc만 설정하므로 삭제 건수는 `lines( )`의 전후 차이로 구한다. 변경 대상이 없으면 UPDATE/DELETE는 sy-subrc = 4, sy-dbcnt = 0.

**(4)** READ TABLE 결과를 검사해야 하는데 그 사이의 `SELECT SINGLE ... FROM scarr`가 sy-subrc를 덮어써서 IF가 SCARR 조회 결과를 검사한다.
```abap
READ TABLE gt_flight INTO DATA(ls_flight)
     WITH KEY carrid = p_carr connid = p_conn.
DATA(lv_found) = xsdbool( sy-subrc = 0 ).

SELECT SINGLE carrname FROM scarr
  WHERE carrid = @p_carr
  INTO @DATA(lv_name).

IF lv_found = abap_false.
  SELECT SINGLE * FROM sflight
    WHERE carrid = @p_carr AND connid = @p_conn
    INTO @ls_flight.
ENDIF.
```
- `sy-subrc`는 해당 문장 직후에 확인한다. 사이에 다른 문장(`READ TABLE`, `SELECT`, `ASSIGN`, `FIND` 등)이 실행되면 덮어써진다. 나중에 쓸 거라면 `DATA(lv_rc) = sy-subrc.`로 바로 저장한다.
- table expression `itab[ ... ]`, `line_exists( )`, 생성자 표현식, 함수형 메서드 호출은 sy-subrc를 바꾸지 않고 실패를 예외(`CX_SY_ITAB_LINE_NOT_FOUND`)나 반환값으로 알린다. 이전 문장의 sy-subrc가 그대로 남아 있으므로 그 값을 보고 판단하면 잘못된 분기가 된다.
- 대안: `IF NOT line_exists( gt_flight[ carrid = p_carr connid = p_conn ] ).` 또는 `DATA(ls_f) = VALUE #( gt_flight[ carrid = p_carr connid = p_conn ] OPTIONAL ).` 후 `IF ls_f IS INITIAL.`
- 클래식 함수 모듈의 `EXCEPTIONS`는 sy-subrc로 결과를 돌려주고, 클래스 기반 예외는 `TRY ... CATCH`로 처리한다. ABAP Cloud와 최신 문법에서는 예외 클래스나 술어 함수로 대신하는 경우가 많다.

**(5)** ① `sy-msgid` ② `sy-msgty` ③ `sy-msgno` ④ `id` ⑤ `number` ⑥ `INTO`
- `EXCEPTIONS error_message = n`을 지정하면 함수 모듈 안의 E/A 메시지가 화면에 뜨지 않고 sy-subrc = n이 되며 메시지 정보가 sy-msgid, sy-msgty, sy-msgno, sy-msgv1~4에 남는다.
- BAPIRET2: TYPE, ID, NUMBER, MESSAGE(완성된 텍스트), MESSAGE_V1~V4, LOG_NO, PARAMETER, ROW, FIELD.
- `MESSAGE ... INTO`는 메시지를 표시하지 않고 텍스트를 변수에 넣으며 sy-msg* 필드도 설정한다.

</details>

---

## 생성자 표현식

### A-010. VALUE·BASE·CORRESPONDING·MOVE-CORRESPONDING과 `#` [코드] ★★★
<!-- src: AB-026, AB-027, AB-031 -->
다음 코드를 보고 물음에 답하시오.

```abap
TYPES: BEGIN OF ty_s,
         a TYPE i,
         b TYPE c LENGTH 3,
       END OF ty_s,
       ty_t TYPE STANDARD TABLE OF ty_s WITH EMPTY KEY.
DATA ls TYPE ty_s.
DATA lt TYPE ty_t.

ls = VALUE #( a = 1 b = 'X' ).
ls = VALUE #( b = 'Y' ).
ls = VALUE #( BASE ls a = 5 ).
lt = VALUE #( ( a = 1 ) ( a = 2 b = 'Q' ) ).
lt = VALUE #( BASE lt ( ls ) ).
DATA(lv_n1) = lines( lt ).
lt = VALUE #( ( a = 9 ) ).
DATA(lv_n2) = lines( lt ).

TYPES: BEGIN OF ty_src,
         carrid TYPE c LENGTH 3,
         connid TYPE n LENGTH 4,
         price  TYPE i,
       END OF ty_src,
       BEGIN OF ty_dst,
         carrid TYPE c LENGTH 3,
         flight TYPE n LENGTH 4,
         price  TYPE i,
         memo   TYPE c LENGTH 5,
       END OF ty_dst.
DATA(ls_src) = VALUE ty_src( carrid = 'LH' connid = '0400' price = 500 ).
DATA(ls_dst) = VALUE ty_dst( carrid = 'AA' flight = '0017' price = 100 memo = 'OLD' ).
DATA(ls_1) = CORRESPONDING ty_dst( ls_src ).
DATA(ls_2) = CORRESPONDING ty_dst( ls_src MAPPING flight = connid ).
DATA(ls_3) = CORRESPONDING ty_dst( BASE ( ls_dst ) ls_src EXCEPT price ).
DATA(ls_4) = ls_dst.
MOVE-CORRESPONDING ls_src TO ls_4.
ls_dst = CORRESPONDING #( ls_src ).
```

(1) `ls`의 최종 값을 쓰시오. 두 번째 대입 후 `a`의 값과 그 이유(흔한 오답 포함)를 쓰시오.

(2) `lv_n1`과 그 시점의 `lt` 내용, `lv_n2`를 쓰시오. 테이블에서 `BASE`가 있을 때와 없을 때 차이를 쓰시오.

(3) `ls_1`, `ls_2`, `ls_3`, `ls_4`, 마지막 `ls_dst`의 carrid/flight/price/memo를 표로 쓰시오.

(4) `MAPPING`, `EXCEPT`의 역할과 `MOVE-CORRESPONDING` 문장과 `CORRESPONDING #( )` 대입의 가장 큰 차이를 쓰시오.

(5) `VALUE #( )`, `CORRESPONDING #( )`, `COND #( )`의 `#`가 의미하는 것을 쓰고, `#`를 쓸 수 없거나 조심해야 하는 경우 네 가지를 쓰시오.

<details><summary>정답·해설</summary>

**(1)** `ls`: a = 5, b = `Y`. `VALUE`는 `BASE`가 없으면 대상을 먼저 초기화하므로 두 번째 줄에서 a = 0(흔한 오답: a = 1). `BASE ls`는 기존 값을 유지한 채 지정한 컴포넌트만 바꾼다 → (5, Y).

**(2)** `lv_n1` = 3, `lt` = (1, 공백), (2, `Q`), (5, `Y`). `lv_n2` = 1. `BASE lt`가 있으면 기존 행 뒤에 추가되고, 없으면 기존 행이 모두 사라진다.

**(3)**

| 변수 | carrid | flight | price | memo |
|---|---|---|---|---|
| ls_1 | LH | 0000 | 500 | (공백) |
| ls_2 | LH | 0400 | 500 | (공백) |
| ls_3 | LH | 0017 | 100 | OLD |
| ls_4 | LH | 0017 | 500 | OLD |
| ls_dst | LH | 0000 | 500 | (공백) |

**(4)** `CORRESPONDING`은 이름이 같은 컴포넌트만 옮기고 `BASE`가 없으면 초기값에서 시작한다(그래서 flight `0000`, memo 공백). `MAPPING 대상 = 원본`으로 이름이 다른 컴포넌트를 연결하고, `EXCEPT`로 지정한 컴포넌트는 옮기지 않는다(ls_3의 price 100 유지). `MOVE-CORRESPONDING` 문장은 대상의 기존 값을 유지하고 같은 이름만 덮어쓴다.

**(5)** `#`는 결과 타입을 문맥(대입 대상, 메서드 파라미터 타입 등)에서 추론하라는 뜻이다.
1. 인라인 선언 `DATA(x) = VALUE #( ... )`처럼 대상 타입을 알 수 없으면 `VALUE #`, `CORRESPONDING #`, `NEW #`는 문법 오류 → 타입 명시.
2. generic 타입 파라미터(`TYPE any`, `TYPE data` 등)에 넘길 때도 추론 불가.
3. `COND #`, `SWITCH #`는 문맥 타입이 없으면 첫 번째 `THEN` 피연산자의 타입을 써서 길이가 잘릴 수 있다(A-011).
4. `CONV #`를 문맥이 이미 같은 타입인 곳에 쓰면 불필요한 변환 경고.
- 대상 타입이 멀리 떨어져 있으면 가독성을 위해 타입 이름을 명시하는 편이 좋다.

</details>

---

### A-011. COND·SWITCH·REDUCE·FOR·FILTER·CONV·NEW·REF·LET [코드] ★★★
<!-- src: AB-028, AB-029, AB-030 -->
다음 코드를 보고 물음에 답하시오.

```abap
DATA(lv_score) = 85.
DATA(lv_grade) = COND string( WHEN lv_score >= 90 THEN `A`
                              WHEN lv_score >= 80 THEN `B`
                              ELSE `C` ).
DATA(lv_day) = 3.
DATA(lv_name) = SWITCH string( lv_day WHEN 1 THEN `Mon`
                                      WHEN 2 THEN `Tue` ).
DATA(lv_x) = COND #( WHEN lv_score > 90 THEN 'NO'
                     ELSE 'YES' ).

TYPES ty_nums TYPE STANDARD TABLE OF i WITH EMPTY KEY.
DATA(lt_num) = VALUE ty_nums( ( 3 ) ( 8 ) ( 5 ) ( 10 ) ).
DATA(lv_sum) = REDUCE i( INIT s = 0
                         FOR n IN lt_num WHERE ( table_line > 4 )
                         NEXT s = s + n ).
DATA(lv_max) = REDUCE i( INIT m = 0
                         FOR n IN lt_num
                         NEXT m = COND #( WHEN n > m THEN n ELSE m ) ).
DATA(lt_dbl) = VALUE ty_nums( FOR n IN lt_num INDEX INTO idx
                              WHERE ( table_line MOD 2 = 0 )
                              ( n * idx ) ).
DATA(lt_sq) = VALUE ty_nums( FOR j = 1 UNTIL j > 3 ( j * j ) ).
```

(1) `lv_grade`, `lv_name`, `lv_x`의 값과 `lv_x`의 타입을 쓰시오. `SWITCH`에 일치하는 `WHEN`도 `ELSE`도 없을 때의 결과, `lv_x`가 그렇게 되는 규칙과 해결책을 쓰시오.

(2) `lv_sum`, `lv_max`, `lt_dbl`, `lt_sq`를 쓰시오. `REDUCE`의 `INIT` 규칙, `INDEX INTO`가 돌려주는 값, 숫자형 반복 변수의 증가와 `UNTIL` 검사 시점을 설명하시오. 반복 표현식의 디버깅상 단점도 쓰시오.

(3) 주석의 의미가 되도록 빈칸을 채우시오.
```abap
TYPES ty_flights TYPE SORTED TABLE OF sflight WITH NON-UNIQUE KEY carrid.
DATA lt_flights TYPE ty_flights.
DATA lv_x2 TYPE i VALUE 7.
DATA(lt_lh) = ____①____ #( lt_flights WHERE carrid = 'LH' ).              " LH 행만
DATA(lt_not_lh) = FILTER #( lt_flights ____②____ WHERE carrid = 'LH' ).   " LH가 아닌 행만
DATA(lv_dec) = ____③____ decfloat34( 1 / 4 ).                             " 0.25
DATA(lr_new) = ____④____ i( 42 ).                                         " 값 42인 익명 객체 참조
DATA(lr_x) = ____⑤____ #( lv_x2 ).                                        " 기존 변수 참조
DATA(lt_names) = VALUE string_table( ____⑥____ pre = `Mr. ` IN            " 표현식 지역 변수
                                     ( pre && `Kim` )
                                     ( pre && `Lee` ) ).
```

(4) `FILTER`를 쓰기 위한 원본 테이블 조건, hashed 키일 때 조건 제약을 쓰시오. `CONV` 대신 `VALUE`로 기본 타입 값을 만들 수 있는가? ③에서 `CONV`가 없으면 결과는? `NEW`와 `REF`의 차이를 쓰시오.

<details><summary>정답·해설</summary>

**(1)** lv_grade = `B`, lv_name = 빈 문자열, lv_x = `YE`(타입 `c LENGTH 2`)
- `COND`는 위에서부터 처음 참인 `WHEN`의 값을 쓴다.
- `SWITCH`에 일치하는 `WHEN`도 `ELSE`도 없으면 결과 타입의 초기값(빈 문자열), 예외는 없다.
- `#`의 타입을 문맥에서 알 수 없으면 **첫 번째 `THEN` 뒤 피연산자의 타입**이 결과 타입이 된다. `'NO'`가 `c LENGTH 2`라 `'YES'`가 `YE`로 잘린다. 해결책: `COND string( ... )`처럼 타입 명시.

**(2)** lv_sum = 23, lv_max = 10, lt_dbl = (16, 40), lt_sq = (1, 4, 9)
- `lv_sum`: 4보다 큰 8, 5, 10의 합. `INIT`는 필수이고 첫 번째 `INIT` 변수가 결과가 된다.
- `lv_max`: 3 → 8 → 8 → 10.
- `INDEX INTO`는 `WHERE`로 거른 뒤의 순번이 아니라 원본 테이블의 행 인덱스다. 8(인덱스 2) → 16, 10(인덱스 4) → 40.
- 숫자형 반복 변수는 `THEN`을 생략하면 1씩 증가하고, `UNTIL`은 매 반복 후 검사하므로 j = 1, 2, 3에서 값을 만들고 j = 4에서 끝난다.
- 반복 표현식은 디버거에서 한 줄씩 따라갈 수 없다.

**(3)** ① `FILTER` ② `EXCEPT` ③ `CONV` ④ `NEW` ⑤ `REF` ⑥ `LET`

**(4)**
- `FILTER`는 원본 테이블에 sorted 또는 hashed 키(primary 또는 secondary)가 있어야 하고 그 키 필드로 `WHERE`를 쓴다. hashed 키는 `=`만, 조건 결합은 `AND`만 허용.
- `VALUE`로는 기본 타입 값을 만들 수 없고 `CONV`를 쓴다. `CONV decfloat34( )` 안에서는 계산 타입도 decfloat34가 되어 0.25가 나온다(없으면 `i` 계산으로 0).
- `NEW`는 새 데이터 객체(또는 인스턴스)를 만들고 참조를 돌려주고, `REF`는 기존 데이터 객체의 참조를 돌려준다.

</details>

---

### A-012. 생성자 표현식 오류 찾기와 한 문장 작성 [작성] ★★★
<!-- src: AB-032, AB-033 -->
`sflight` 데이터를 생성자 표현식으로 처리한다.

(1) 다음 코드의 잘못된 곳 4곳을 찾아 문법/런타임/논리 오류 중 무엇인지 쓰고 고치시오.
```abap
TYPES ty_tab TYPE STANDARD TABLE OF sflight WITH EMPTY KEY.
DATA lt_all TYPE ty_tab.
SELECT * FROM sflight INTO TABLE @lt_all.

DATA(lt_lh)    = FILTER #( lt_all WHERE carrid = 'LH' ).                      " (a)
DATA(lv_text)  = COND #( WHEN lines( lt_all ) > 0 THEN 'Y' ELSE 'EMPTY' ).    " (b)
DATA(lv_seats) = REDUCE i( FOR ls IN lt_all NEXT s = s + ls-seatsocc ).       " (c)
DATA(lv_price) = lt_all[ carrid = 'XX' ]-price.                               " (d)
```

(2) `DATA lt_sflight TYPE STANDARD TABLE OF sflight WITH EMPTY KEY.`에 데이터가 들어 있다. 다음을 각각 **한 문장**(대입문 하나)으로 쓰시오.
- a. carrid가 `'LH'`인 행의 `seatsocc` 합계를 `lv_total`(인라인, 타입 i)에.
- b. price가 500 이상인 행의 `connid`만 모은 `lt_conn`(타입 `ty_conn_tab` = `STANDARD TABLE OF s_conn_id WITH EMPTY KEY`).
- c. 아래 `ty_out_tab`으로 옮기되 `carrier`에 carrid, `flight`에 connid, `price`에 price가 들어가는 `lt_out`.
```abap
TYPES: BEGIN OF ty_out,
         carrier TYPE s_carr_id,
         flight  TYPE s_conn_id,
         price   TYPE s_price,
       END OF ty_out,
       ty_out_tab TYPE STANDARD TABLE OF ty_out WITH EMPTY KEY.
```

(3) (2)-c에서 `price`를 `MAPPING`에 쓰지 않아도 되는 이유와, 나머지 sflight 컴포넌트는 어떻게 되는지, 반복 변수 이름 `ls`를 문장마다 다시 써도 되는 이유를 쓰시오.

<details><summary>정답·해설</summary>

**(1)**
- (a) 문법 오류: `FILTER`는 sorted/hashed 키가 필요한데 `lt_all`은 empty key의 standard table. → `ty_tab`에 `WITH NON-UNIQUE SORTED KEY k_carr COMPONENTS carrid`를 추가하고 `FILTER #( lt_all USING KEY k_carr WHERE carrid = 'LH' )`. 또는 `VALUE ty_tab( FOR ls IN lt_all WHERE ( carrid = 'LH' ) ( ls ) )`.
- (b) 논리 오류: 결과 타입이 첫 `THEN`의 `'Y'`(c 길이 1)로 정해져 `'EMPTY'`가 `'E'`로 잘린다. → `COND string( ... )`.
- (c) 문법 오류: `REDUCE`에는 `INIT`가 필수. → `REDUCE i( INIT s = 0 FOR ls IN lt_all NEXT s = s + ls-seatsocc )`.
- (d) 런타임 오류: 행이 없으면 `CX_SY_ITAB_LINE_NOT_FOUND`. → `TRY ... CATCH cx_sy_itab_line_not_found`, `line_exists( )`로 먼저 확인, 또는 `VALUE #( lt_all[ carrid = 'XX' ] OPTIONAL )`로 행을 받은 뒤 price를 읽는다.
- 생성자 표현식은 짧지만 결과 타입 결정, 필수 요소, 예외를 알고 써야 한다.

**(2)**
```abap
" a
DATA(lv_total) = REDUCE i( INIT s = 0
                           FOR ls IN lt_sflight WHERE ( carrid = 'LH' )
                           NEXT s = s + ls-seatsocc ).
" b
DATA(lt_conn) = VALUE ty_conn_tab( FOR ls IN lt_sflight WHERE ( price >= 500 )
                                   ( ls-connid ) ).
" c
DATA(lt_out) = CORRESPONDING ty_out_tab( lt_sflight
                                         MAPPING carrier = carrid
                                                 flight  = connid ).
```

**(3)** `price`는 이름이 같아 자동으로 옮겨진다. 나머지 sflight 컴포넌트는 대상에 없으므로 무시된다. 반복 변수 `ls`는 각 표현식 안에서만 유효하므로 문장마다 다시 써도 된다.

</details>

---

## 필드 심볼·데이터 참조·구조체

### A-013. INTO·ASSIGNING·REFERENCE INTO와 필드 심볼 vs 참조, 런타임 오류 [코드] ★★
<!-- src: AB-034, AB-035, AB-038 -->
다음 두 코드를 보고 물음에 답하시오.

```abap
" [코드 A]
TYPES ty_nums TYPE STANDARD TABLE OF i WITH EMPTY KEY.
DATA(lt) = VALUE ty_nums( ( 1 ) ( 2 ) ( 3 ) ).
LOOP AT lt INTO DATA(lv_wa).
  lv_wa = lv_wa * 10.
ENDLOOP.
LOOP AT lt ASSIGNING FIELD-SYMBOL(<lv_fs>).
  <lv_fs> = <lv_fs> + 1.
ENDLOOP.
LOOP AT lt REFERENCE INTO DATA(lr_line).
  lr_line->* = lr_line->* * 2.
ENDLOOP.

TYPES: BEGIN OF ty_s,
         a TYPE i,
         b TYPE c LENGTH 1,
       END OF ty_s.
DATA(ls) = VALUE ty_s( a = 1 b = 'X' ).
ASSIGN COMPONENT 'B' OF STRUCTURE ls TO FIELD-SYMBOL(<lv_comp>).
<lv_comp> = 'Z'.
ASSIGN COMPONENT 'C' OF STRUCTURE ls TO <lv_comp>.
DATA(lv_rc) = sy-subrc.

" [코드 B]
DATA lt_sflight TYPE SORTED TABLE OF sflight WITH UNIQUE KEY carrid connid fldate.
FIELD-SYMBOLS <ls_f> TYPE sflight.
DATA lr_f TYPE REF TO sflight.
SELECT * FROM sflight INTO TABLE @lt_sflight.
READ TABLE lt_sflight ASSIGNING <ls_f> WITH KEY carrid = 'ZZ'.
<ls_f>-price = 0.                                   " (a)
LOOP AT lt_sflight ASSIGNING <ls_f>.
  <ls_f>-carrid = 'LH'.                             " (b)
ENDLOOP.
lr_f->price = 100.                                  " (c)
```

(1) [코드 A]의 세 루프가 끝난 뒤 `lt`의 내용을 쓰고 각 루프 방식이 테이블에 미치는 영향을 설명하시오. 넓은 행을 수정·조회할 때 유리한 방식은?

(2) [코드 A]의 `ls-b`와 `lv_rc`를 쓰시오. 없는 컴포넌트 할당 시 예외가 나는가?

(3) 필드 심볼과 데이터 참조 변수(`TYPE REF TO`)의 차이를 성격, 상태 확인, 저장, 생성, 오류 측면에서 쓰고 공통점을 쓰시오.

(4) [코드 B]에서 런타임 오류가 날 수 있는 곳 (a)(b)(c)의 이유(오류 이름 포함)와 고친 코드를 쓰시오.

<details><summary>정답·해설</summary>

**(1)** `lt` = (4, 6, 8)
- `INTO`는 작업 영역에 복사본을 만들 뿐이라 테이블은 (1, 2, 3) 그대로.
- `ASSIGNING`은 필드 심볼이 행 자체를 가리켜 (2, 3, 4).
- `REFERENCE INTO`도 행을 직접 가리키는 참조라 `->*`로 바꾸면 반영 → (4, 6, 8).
- 복사가 없는 `ASSIGNING`/`REFERENCE INTO`가 유리하다.

**(2)** `ls-b` = `Z`, `lv_rc` = 4. 할당된 필드 심볼을 통해 `ls-b`가 바뀐다. 없는 컴포넌트 `C`는 할당에 실패해 sy-subrc = 4이고 예외는 나지 않는다.

**(3)**
1. 성격: 필드 심볼은 다른 데이터 객체의 별칭(alias)이라 이름을 쓰면 곧바로 그 메모리를 읽고 쓴다. 데이터 참조는 주소를 값으로 담는 변수라 `->*`(구조 컴포넌트는 `->comp`)로 역참조한다.
2. 상태 확인: 필드 심볼 `IS ASSIGNED`/`UNASSIGN`, 참조 `IS BOUND`/`CLEAR`.
3. 저장: 참조는 값이므로 내부 테이블 컴포넌트나 클래스 속성에 담아 전달·보관할 수 있다. 필드 심볼은 테이블에 넣을 수 없다.
4. 생성: 참조는 `NEW`/`CREATE DATA`로 익명 데이터 객체를 만들어 가리킬 수 있다. 필드 심볼은 기존 객체(또는 역참조 결과)에 할당만 된다.
5. 오류: 할당되지 않은 필드 심볼 접근은 `GETWA_NOT_ASSIGNED`, 초기 참조 역참조는 `CX_SY_REF_IS_INITIAL`.
6. 공통점: 둘 다 generic 타입(`any`, `data`, `any table`)을 써 동적 프로그래밍에 쓰인다. 루프에서 행을 직접 수정하는 용도로 둘 다 쓰이며 성능 차이는 거의 없다. 참조는 더 이상 참조되지 않으면 가비지 컬렉터가 정리한다.

**(4)**
- (a) `'ZZ'` 행이 없으면 `<ls_f>`가 할당되지 않아 접근 시 `GETWA_NOT_ASSIGNED`. → `IF sy-subrc = 0.`(또는 `IF <ls_f> IS ASSIGNED.`) 안에서만 수정.
- (b) sorted 테이블의 키 필드(carrid)는 읽기 전용이라 필드 심볼로 바꾸면 런타임 오류. 키를 바꾸려면 행을 `DELETE` 후 새 키로 `INSERT`. 키가 아닌 필드(price 등)는 수정 가능.
- (c) `lr_f`는 초기 참조라 역참조하면 `CX_SY_REF_IS_INITIAL`. → `lr_f = NEW #( ).` 또는 `READ TABLE ... REFERENCE INTO lr_f` 후 `IF lr_f IS BOUND.`
- 필드 심볼/참조는 가리키는 대상이 있는지 항상 먼저 확인한다.

</details>

---

### A-014. generic 타입과 동적 프로그래밍 [작성] ★★★
<!-- src: AB-036, AB-037, AB-039 -->
실행 중에 정해지는 테이블을 처리하는 유틸리티를 만든다.

(1) generic 타입이 무엇이고 어디에 쓸 수 있는지(`DATA` 선언에 쓸 수 있는가) 쓰시오. 다음 generic 타입이 포함하는 타입을 쓰시오: `any`, `simple`, `clike`, `csequence`, `numeric`, `any table`, `index table`.

(2) `TYPE any`와 `TYPE REF TO data`의 쓰임 차이를 쓰고, generic 파라미터를 너무 넓게 쓰면 생기는 단점과 권장 방식을 쓰시오.

(3) 빈칸을 채우시오. 동적 이름에 사용자 입력이 들어갈 때 위험과 대책, 존재하지 않는 타입 이름일 때 예외를 쓰시오.
```abap
DATA lv_tabname TYPE tabname VALUE 'SCARR'.
DATA lr_data    TYPE REF TO data.
FIELD-SYMBOLS <lt_any> TYPE ____①____.
CREATE DATA lr_data TYPE STANDARD TABLE OF ____②____.
ASSIGN lr_data____③____ TO <lt_any>.
IF <lt_any> IS ____④____.
  SELECT * FROM (lv_tabname) INTO TABLE @<lt_any> UP TO 10 ROWS.
  DATA(lv_cnt) = ____⑤____( <lt_any> ).
ENDIF.
```

(4) 임의의 flat 구조 변수 `ls_data`(예: SCARR 한 행)의 모든 컴포넌트 값을 순서대로 `|`로 연결한 `lv_text`를 만드는 코드를 작성하시오. 컴포넌트 이름은 쓰지 말고 `ASSIGN COMPONENT`와 `DO` 루프를 사용한다(예: `LH|Lufthansa|EUR|http://www.lufthansa.com`). 클라이언트 필드를 빼려면, 컴포넌트 이름까지 필요하면 어떻게 하는지도 쓰시오.

<details><summary>정답·해설</summary>

**(1)** generic 타입은 일부 속성(길이, 구체 타입, 테이블 종류 등)을 열어 둔 타입이다. 필드 심볼이나 메서드 파라미터의 타입에만 쓸 수 있고 `DATA` 선언에는 쓸 수 없다(`TYPE REF TO data` 같은 참조는 예외).
- `any`: 모든 타입 / `simple`: 기본 타입과 flat 문자형 구조 / `clike`: `c`, `n`, `d`, `t`, `string`, flat 문자형 구조 / `csequence`: `c`, `string` / `numeric`: `i`, `int8`, `p`, `decfloat`, `f` 등 / `any table`: 모든 테이블 종류 / `index table`: standard·sorted(인덱스 접근 가능). 그 밖에 `data`도 모든 타입.

**(2)** `TYPE any`는 파라미터나 필드 심볼이 전달된 실제 데이터에 바로 연결된다. `TYPE REF TO data`는 임의 타입 데이터의 **참조**를 담는 변수라 `CREATE DATA`로 실행 중에 타입을 정해 객체를 만들고 보관하는 데 쓴다. generic 파라미터는 정적 검사가 약해지므로 필요한 만큼만 넓힌다(예: 문자열만 받으면 `csequence`).

**(3)** ① `STANDARD TABLE`(또는 `ANY TABLE`) ② `(lv_tabname)` ③ `->*` ④ `ASSIGNED` ⑤ `lines`
- 동적 타입 이름은 괄호로 감싼다(`FROM (lv_tabname)`도 같다). `CREATE DATA`로 만든 익명 객체는 `->*`로 역참조해 필드 심볼에 할당한다.
- 사용자 입력이 들어가면 SQL injection 위험이 있으므로 `cl_abap_dyn_prg`로 검증한다. 존재하지 않는 타입 이름이면 `CX_SY_CREATE_DATA_ERROR`.

**(4)**
```abap
DATA ls_data TYPE scarr.
DATA lt_vals TYPE string_table.

SELECT SINGLE * FROM scarr WHERE carrid = 'LH' INTO @ls_data.

DO.
  ASSIGN COMPONENT sy-index OF STRUCTURE ls_data TO FIELD-SYMBOL(<lv_comp>).
  IF sy-subrc <> 0.
    EXIT.                       " 더 이상 컴포넌트가 없으면 종료
  ENDIF.
  APPEND |{ <lv_comp> }| TO lt_vals.
ENDDO.

DATA(lv_text) = concat_lines_of( table = lt_vals sep = `|` ).
```
- `ASSIGN COMPONENT`에 숫자를 주면 위치, 문자를 주면 이름(대문자)으로 찾는다. 무한 `DO`는 `sy-subrc <> 0`일 때 반드시 `EXIT`.
- mandt도 첫 컴포넌트로 포함되므로 빼려면 `sy-index = 1`을 건너뛴다. 이름까지 필요하면 RTTS(`cl_abap_structdescr`)를 쓴다.

</details>

---

### A-015. flat·nested·deep 구조와 INCLUDE [개념] ★★
<!-- src: AB-040, AB-041 -->
다음 타입 정의를 보고 물음에 답하시오.

```abap
TYPES: BEGIN OF ty_addr,
         city   TYPE c LENGTH 20,
         street TYPE c LENGTH 30,
       END OF ty_addr.

TYPES: ____①____ ty_person,
         name TYPE c LENGTH 30,
         addr TYPE ty_addr,
       END OF ty_person.

TYPES BEGIN OF ty_emp.
  INCLUDE TYPE ty_person ____②____ pers.
TYPES   empno TYPE n LENGTH 8.
TYPES END OF ty_emp.

TYPES: BEGIN OF ty_team,
         leader  TYPE ty_emp,
         members TYPE ____③____ TABLE OF ty_emp WITH EMPTY KEY,
       END OF ty_team.

DATA ls_emp TYPE ty_emp.
ls_emp-name = 'KIM'.
ls_emp-addr-city = 'SEOUL'.
" ls_emp-name 과 같은 컴포넌트:  ls_emp-____④____-name
```

(1) 빈칸 ①~④를 채우시오. `INCLUDE TYPE ... AS`로 포함했을 때의 접근 방식과, 같은 구조를 두 번 포함할 때 이름 충돌을 피하는 방법을 쓰시오.

(2) flat, nested, deep 구조를 정의하고 `ty_addr`, `ty_person`, `ty_team`이 각각 무엇에 해당하는지 쓰시오. nested이면서 flat일 수 있는가?

(3) deep 구조의 실제 데이터는 메모리에 어떻게 저장되는가? deep 구조의 제약 세 가지를 쓰시오.

(4) deep 구조를 대입할 때 비용 측면의 주의점과, 하위 테이블까지 이름 기반으로 복사하는 방법을 쓰시오.

<details><summary>정답·해설</summary>

**(1)** ① `BEGIN OF` ② `AS` ③ `STANDARD` ④ `pers`. `AS 그룹명`으로 포함하면 컴포넌트를 직접(`ls_emp-name`)도, 그룹명을 거쳐(`ls_emp-pers-name`)도 접근할 수 있다. 같은 구조를 두 번 포함할 때는 `RENAMING WITH SUFFIX`.

**(2)**
- flat: 컴포넌트가 모두 고정 길이 기본 타입(또는 flat 하위 구조), 메모리가 연속된 고정 길이.
- nested: 컴포넌트 중에 다른 구조가 있다(`ls-addr-city`). 하위 구조가 모두 flat이면 nested이면서 flat일 수 있다.
- deep: `string`, `xstring`, 내부 테이블, 참조 같은 deep 컴포넌트가 하나라도 있다.
- `ty_addr` flat, `ty_person` nested(그리고 flat), `ty_team` 내부 테이블 컴포넌트가 있어 deep.

**(3)** 실제 데이터는 별도 메모리에 있고 구조에는 내부 참조만 있다. 제약:
1. 문자형 구조처럼 오프셋/길이로 통째로 접근하거나 `c` 필드와 서로 대입할 수 없다.
2. DB 테이블의 행 타입이나 `SELECT` 대상 구조로 그대로 쓸 수 없다(내부 테이블 컴포넌트는 DB 컬럼이 될 수 없음).
3. 클래식 리스트 `WRITE`로 구조 전체를 통째로 출력할 수 없다.

**(4)** 대입 시 내부 테이블 컴포넌트까지 복사되므로 크기가 크면 비용이 크다. 구조 간 이름 기반 복사는 `CORRESPONDING`, 하위 테이블까지 이름 기반으로 복사하려면 `CORRESPONDING ... DEEP`.

</details>

---

## 내부 테이블

### A-016. 테이블 종류·키·hashed·READ TABLE vs table expression [개념] ★★
<!-- src: IS-001, IS-002, IS-012, IS-013 -->
내부 테이블 설계를 검토한다.

(1) STANDARD / SORTED / HASHED 테이블을 키 유일성, 키 접근 방식과 성능, 인덱스 접근 가능 여부, 알맞은 사용 상황으로 비교하는 표를 쓰시오. sorted 테이블에 행을 넣을 때 권장 문장, hashed 테이블이 해시 접근을 하기 위한 조건을 쓰시오.

(2) 키를 지정하지 않은 `DATA lt TYPE STANDARD TABLE OF sflight.`의 기본 키(standard key)는 무엇이고(행이 구조일 때와 기본 타입일 때) 왜 문제가 되는가? `WITH EMPTY KEY`의 의미와 그때 `SORT itab.`의 결과를 쓰시오.

(3) secondary key를 정의·사용하는 문법(정의 2가지, 사용 3가지)과 주의점(자동 선택 여부, 갱신 시점, 비용)을 쓰시오.

(4) hashed 테이블에 대한 설명 중 **옳지 않은** 것을 고르시오.
① `READ TABLE ... INDEX 1`처럼 인덱스로 접근할 수 없다.
② primary key는 반드시 `UNIQUE`로 정의해야 한다.
③ `APPEND` 문으로 행을 추가할 수 없다.
④ 전체 키로 `READ TABLE ... WITH TABLE KEY` 하면 이진 탐색이 수행되어 O(log n) 시간이 걸린다.
⑤ primary key로 `LOOP AT` 할 때 `sy-tabix`는 0이다.

(5) `READ TABLE`과 table expression `itab[ ... ]`을 결과 확인 방법, 사용 위치, 성능 측면에서 비교하시오. `ASSIGN itab[ ... ] TO <fs>`의 예외적 동작, `BINARY SEARCH`를 쓸 수 있는 쪽, 존재 확인만 할 때 권장 방법도 쓰시오.

<details><summary>정답·해설</summary>

**(1)**

| 구분 | STANDARD | SORTED | HASHED |
|---|---|---|---|
| 키 유일성 | 항상 NON-UNIQUE (empty key 가능) | UNIQUE / NON-UNIQUE | 항상 UNIQUE |
| 키 접근 | 선형 탐색 O(n) (`BINARY SEARCH` 직접 지정 시 O(log n)) | 이진 탐색 O(log n) | 해시 O(1) |
| 인덱스 접근 | 가능 | 가능 | 불가 |
| 사용 상황 | 순서대로 쌓고 인덱스로 처리, 작은 테이블 | 키 범위·부분 키 조회, 정렬 상태 유지 | 큰 테이블을 전체 키로 반복 조회(룩업) |

- sorted 테이블은 삽입·삭제 때 자동으로 정렬 상태를 유지한다. `APPEND`는 정렬 순서를 지킬 때만 가능하므로 `INSERT ... INTO TABLE`을 쓴다.
- hashed는 전체 키를 모두 지정해야 해시 접근이 된다. 부분 키로는 빨라지지 않는다.
- standard 테이블은 다양한 키로 조회할 때 secondary key로 보완한다.

**(2)** `WITH DEFAULT KEY`(키 생략 시도 동일)는 행이 구조이면 **문자형·바이트형 컴포넌트 전부**(숫자형 제외), 기본 타입 행이면 행 전체(`table_line`)가 키다. 키가 의도치 않게 매우 길어져 `SORT`, `DELETE ADJACENT DUPLICATES`, `COLLECT`, `READ TABLE ... FROM wa`가 예상과 다르게 동작하거나 느려진다. `WITH EMPTY KEY`는 키가 없다는 뜻(standard만 가능)이고, 키 없이 `SORT itab.`을 쓰면 아무 정렬도 일어나지 않으므로 항상 `BY`를 지정한다. `SELECT ... INTO TABLE @DATA(itab)`의 결과도 empty key standard 테이블이다.

**(3)** 정의: `WITH NON-UNIQUE SORTED KEY k_name COMPONENTS ...` 또는 `WITH UNIQUE HASHED KEY ...`. 사용: `READ TABLE ... WITH KEY k_name COMPONENTS ...`, `LOOP AT ... USING KEY k_name WHERE ...`, `itab[ KEY k_name ... ]`. 주의: secondary key는 자동으로 선택되지 않아 명시해야 하고, 메모리와 갱신 비용이 든다(unique는 즉시, non-unique는 처음 사용할 때 갱신). 자주 조회하는 큰 테이블에만 쓴다.

**(4)** ④ — hashed 테이블은 해시 함수로 접근해 행 수와 상관없이 거의 일정한 시간(O(1))이 걸린다. 이진 탐색은 sorted 테이블의 방식이다. ① ③ 인덱스가 없으므로 인덱스 접근과 `APPEND`(인덱스 테이블 전용)는 문법 오류, `INSERT ... INTO TABLE`을 쓴다. ② hashed 키는 항상 유일. ⑤ 옳다.

**(5)**
- 결과 확인: `READ TABLE`은 `sy-subrc`/`sy-tabix`를 설정하고 못 찾아도 예외가 없다. table expression은 `sy-subrc`를 설정하지 않고 못 찾으면 `CX_SY_ITAB_LINE_NOT_FOUND`(`OPTIONAL`/`DEFAULT`, `line_exists( )`로 회피). 예외적으로 `ASSIGN itab[ ... ] TO <fs>`는 예외 대신 `sy-subrc`를 설정한다.
- 사용 위치: table expression은 식이 오는 모든 곳(메서드 인수, 계산식, 조건, 체이닝 `itab[ 1 ]-comp`, 중첩 `itab[ 1 ]-sub[ 2 ]`). `READ TABLE`은 독립 문장.
- 성능: 한 번 쓰면 차이가 없지만 같은 table expression을 여러 번 쓰면 그때마다 탐색한다. 여러 번 쓸 행은 `ASSIGN`이나 `READ TABLE ... ASSIGNING`으로 한 번만 찾는다. 결과는 기본적으로 복사(읽기)이고 쓰기 위치에 놓으면 행을 직접 바꾼다.
- `BINARY SEARCH`는 `READ TABLE`에만 있다. table expression에서는 sorted/hashed 키(`KEY` 지정)를 쓴다.
- 존재 확인만 할 때는 `READ TABLE ... TRANSPORTING NO FIELDS` 대신 `line_exists( )`가 의도가 분명하다.

</details>

---

### A-017. INSERT·APPEND·READ BINARY SEARCH·table expression 추적 [코드] ★★★
<!-- src: IS-003, IS-004, IS-005, MX-009 -->
내부 테이블 연산을 추적한다.

(1) 실행 후 `lt_sort`, `lt_std`의 행 순서(id, name), `rc1`, `rc2`, `lines( lt_hash )`를 쓰시오.
```abap
TYPES: BEGIN OF ty_s,
         id   TYPE i,
         name TYPE c LENGTH 5,
       END OF ty_s.
DATA lt_std  TYPE STANDARD TABLE OF ty_s WITH EMPTY KEY.
DATA lt_sort TYPE SORTED TABLE OF ty_s WITH UNIQUE KEY id.
DATA lt_hash TYPE HASHED TABLE OF ty_s WITH UNIQUE KEY id.

INSERT VALUE #( id = 3 name = 'C' ) INTO TABLE lt_sort.
INSERT VALUE #( id = 1 name = 'A' ) INTO TABLE lt_sort.
INSERT VALUE #( id = 3 name = 'X' ) INTO TABLE lt_sort.
DATA(rc1) = sy-subrc.
INSERT VALUE #( id = 2 name = 'B' ) INTO TABLE lt_sort.
APPEND VALUE #( id = 2 name = 'B' ) TO lt_std.
APPEND VALUE #( id = 1 name = 'A' ) TO lt_std.
INSERT VALUE #( id = 9 name = 'Z' ) INTO lt_std INDEX 1.
INSERT VALUE #( id = 5 name = 'E' ) INTO TABLE lt_hash.
INSERT VALUE #( id = 5 name = 'F' ) INTO TABLE lt_hash.
DATA(rc2) = sy-subrc.
```
중복 키 행이 있는 테이블 전체를 유일 키 테이블에 대입하거나 `INSERT LINES OF`로 넣으면 어떻게 되는가?

(2) 각 `READ TABLE` 직후의 `sy-subrc`와 `sy-tabix`를 쓰시오((e)는 `sy-subrc`만). 이진 탐색이 실패했을 때 `sy-tabix`의 의미와 이를 활용하는 방법, `BINARY SEARCH`의 전제 조건을 쓰시오.
```abap
TYPES ty_nums TYPE STANDARD TABLE OF i WITH EMPTY KEY.
DATA(lt) = VALUE ty_nums( ( 10 ) ( 20 ) ( 30 ) ( 40 ) ).
READ TABLE lt WITH KEY table_line = 30 BINARY SEARCH TRANSPORTING NO FIELDS.  " (a)
READ TABLE lt WITH KEY table_line = 25 BINARY SEARCH TRANSPORTING NO FIELDS.  " (b)
READ TABLE lt WITH KEY table_line = 5  BINARY SEARCH TRANSPORTING NO FIELDS.  " (c)
READ TABLE lt WITH KEY table_line = 50 BINARY SEARCH TRANSPORTING NO FIELDS.  " (d)
READ TABLE lt INDEX 7 INTO DATA(lv_val).                                       " (e)
```

(3) `r1`, `r2`, `r3`, `ls_opt`, `ls_def`, `lv_msg`의 값을 쓰시오(흔한 오답 포함). `line_exists`와 `line_index`의 반환값을 쓰시오.
```abap
TYPES: BEGIN OF ty_c,
         carrid TYPE c LENGTH 3,
         name   TYPE c LENGTH 20,
       END OF ty_c.
DATA lt_c TYPE SORTED TABLE OF ty_c WITH UNIQUE KEY carrid.
DATA ls_opt TYPE ty_c.
DATA ls_def TYPE ty_c.
DATA lv_msg TYPE string.
lt_c = VALUE #( ( carrid = 'LH' name = 'Lufthansa' )
                ( carrid = 'AA' name = 'American' )
                ( carrid = 'UA' name = 'United' ) ).
DATA(r1) = lt_c[ 2 ]-carrid.
DATA(r2) = line_index( lt_c[ carrid = 'UA' ] ).
DATA(r3) = xsdbool( line_exists( lt_c[ carrid = 'SQ' ] ) ).
ls_opt = VALUE #( lt_c[ carrid = 'SQ' ] OPTIONAL ).
ls_def = VALUE #( lt_c[ carrid = 'SQ' ] DEFAULT VALUE #( carrid = '??' name = 'Unknown' ) ).
TRY.
    lv_msg = lt_c[ carrid = 'SQ' ]-name.
  CATCH cx_sy_itab_line_not_found.
    lv_msg = `not found`.
ENDTRY.
```

(4) 다음 코드 실행 후 `lv_tabix`, `lv_subrc`, itab의 최종 내용을 단계별 표와 함께 쓰시오. `SORT`에 `BY table_line`을 쓴 이유도 쓰시오.
```abap
DATA itab TYPE STANDARD TABLE OF i WITH DEFAULT KEY.
DATA lv_9 TYPE i VALUE 9.
itab = VALUE #( ( 5 ) ( 3 ) ( 8 ) ( 3 ) ( 1 ) ).
INSERT 7 INTO itab INDEX 2.
DELETE itab WHERE table_line = 3.
APPEND 3 TO itab.
SORT itab BY table_line DESCENDING.
READ TABLE itab TRANSPORTING NO FIELDS WITH KEY table_line = 5.
DATA(lv_tabix) = sy-tabix.
DATA(lv_subrc) = sy-subrc.
DELETE itab INDEX 1.
MODIFY itab FROM lv_9 INDEX 2.
```

<details><summary>정답·해설</summary>

**(1)** `lt_sort`: (1, A), (2, B), (3, C) / `lt_std`: (9, Z), (2, B), (1, A) / rc1 = 4, rc2 = 4, `lines( lt_hash )` = 1
- sorted 테이블은 `INSERT ... INTO TABLE` 시 키 순서 위치에 들어간다. 유일 키 3이 이미 있어 (3, X)는 들어가지 않고 sy-subrc = 4(예외 아님), 기존 (3, C) 유지.
- `APPEND`는 끝에, `INSERT ... INDEX 1`은 맨 앞에.
- hashed도 중복 키 단일 행 `INSERT`는 sy-subrc = 4.
- 중복 키가 있는 테이블 전체를 유일 키 테이블에 대입하거나 `INSERT LINES OF`로 넣으면 런타임 오류.

**(2)** (a) 0, 3 (b) 4, 3 (c) 4, 1 (d) 8, 5 (e) sy-subrc = 4
- 이진 탐색 실패 시 `sy-tabix`는 그 값을 넣는다면 들어갈 위치(그 행 앞에 삽입될 인덱스): 25는 30(인덱스 3) 앞, 5는 10(인덱스 1) 앞. 모든 행보다 크면 sy-subrc = 8, sy-tabix = 행 수 + 1.
- 정렬된 standard 테이블에 `INSERT ... INDEX sy-tabix`로 정렬을 유지하며 넣을 수 있다.
- 테이블이 그 키로 오름차순 정렬되어 있어야 한다. 아니면 오류 없이 엉뚱한 결과가 나온다.
- 존재하지 않는 인덱스는 sy-subrc = 4.

**(3)** r1 = `LH`, r2 = 3, r3 = 공백(abap_false), ls_opt = 초기값(carrid·name 모두 공백), ls_def = (`??`, `Unknown`), lv_msg = `not found`
- sorted 테이블이라 넣은 순서와 상관없이 AA, LH, UA 순서. 인덱스 2 = LH(흔한 오답: AA).
- `line_exists`는 참/거짓, `line_index`는 인덱스(없으면 0). 둘 다 sy-subrc를 바꾸지 않는다.
- 행이 없을 때 table expression은 `CX_SY_ITAB_LINE_NOT_FOUND`, `OPTIONAL`은 초기 행, `DEFAULT`는 지정 값을 돌려준다.

**(4)** lv_tabix = 3, lv_subrc = 0, itab = 7, 9, 3, 1

| 문장 | itab |
|---|---|
| VALUE | 5 3 8 3 1 |
| INSERT 7 INDEX 2 | 5 7 3 8 3 1 |
| DELETE WHERE = 3 | 5 7 8 1 |
| APPEND 3 | 5 7 8 1 3 |
| SORT DESCENDING | 8 7 5 3 1 |
| READ ... = 5 | 3번째 행 → sy-tabix 3, sy-subrc 0 |
| DELETE INDEX 1 | 7 5 3 1 |
| MODIFY INDEX 2 | 7 9 3 1 |

- `DELETE ... WHERE`는 조건에 맞는 행을 **모두** 지운다.
- EMPTY KEY 테이블에 `SORT itab`만 쓰면 정렬되지 않으므로 `BY`를 쓰는 습관을 들인다. 여기는 DEFAULT KEY라 `SORT itab DESCENDING`만 써도 결과는 같다.

</details>

---

### A-018. COLLECT·MODIFY·DELETE·LOOP WHERE·중복 제거·헤더 라인 [코드] ★★★
<!-- src: IS-006, IS-007, IS-009, MX-008 -->
내부 테이블 변경 문장을 추적한다.

(1) 주석 (A) 시점과 마지막 시점의 `lt_sum`, `rc1`, `rc2`를 쓰시오.
```abap
TYPES: BEGIN OF ty_sum,
         carrid TYPE c LENGTH 3,
         seats  TYPE i,
       END OF ty_sum.
DATA lt_sum TYPE STANDARD TABLE OF ty_sum WITH NON-UNIQUE KEY carrid.
DATA ls     TYPE ty_sum.
ls = VALUE #( carrid = 'LH' seats = 10 ). COLLECT ls INTO lt_sum.
ls = VALUE #( carrid = 'AA' seats = 5 ).  COLLECT ls INTO lt_sum.
ls = VALUE #( carrid = 'LH' seats = 7 ).  COLLECT ls INTO lt_sum.
ls = VALUE #( carrid = 'UA' seats = 3 ).  COLLECT ls INTO lt_sum.
ls = VALUE #( carrid = 'AA' seats = 1 ).  COLLECT ls INTO lt_sum.
" (A)
ls = VALUE #( carrid = 'AA' seats = 100 ).
MODIFY lt_sum FROM ls TRANSPORTING seats WHERE carrid = 'AA'.
DELETE lt_sum WHERE seats < 10.
ls = VALUE #( carrid = 'SQ' seats = 1 ).
MODIFY TABLE lt_sum FROM ls.
DATA(rc1) = sy-subrc.
DELETE lt_sum INDEX 5.
DATA(rc2) = sy-subrc.
```
`COLLECT`의 동작과 행 타입 조건, `MODIFY ... WHERE`에 필수인 추가어, 내부 테이블 `MODIFY TABLE`과 DB `MODIFY`의 차이를 쓰시오.

(2) `lv_str`, `rc1`, `rc2`를 쓰시오. standard 테이블 `WHERE` 루프의 성능 문제와 대책을 쓰시오.
```abap
TYPES ty_nums TYPE STANDARD TABLE OF i WITH EMPTY KEY.
DATA(lt) = VALUE ty_nums( ( 5 ) ( 12 ) ( 7 ) ( 20 ) ( 3 ) ).
DATA lv_str TYPE string.
LOOP AT lt INTO DATA(n) WHERE table_line > 6.
  lv_str = |{ lv_str }[{ sy-tabix }:{ n }]|.
ENDLOOP.
DATA(rc1) = sy-subrc.
LOOP AT lt INTO n WHERE table_line > 100.
ENDLOOP.
DATA(rc2) = sy-subrc.
```

(3) `lines( lt_a )`, `rc_a`, `lt_b`의 내용, `lines( lt_c )`를 쓰시오. `lt_c`에서 어떤 connid 행이 남는지 정해지는가? `COMPARING`을 생략하면?
```abap
TYPES: BEGIN OF ty_r,
         carrid TYPE c LENGTH 3,
         connid TYPE n LENGTH 4,
       END OF ty_r.
TYPES ty_t TYPE STANDARD TABLE OF ty_r WITH EMPTY KEY.
DATA(lt0) = VALUE ty_t( ( carrid = 'LH' connid = '0400' )
                        ( carrid = 'AA' connid = '0017' )
                        ( carrid = 'LH' connid = '0402' )
                        ( carrid = 'AA' connid = '0017' )
                        ( carrid = 'LH' connid = '0400' ) ).
DATA(lt_a) = lt0.
DELETE ADJACENT DUPLICATES FROM lt_a COMPARING carrid.
DATA(rc_a) = sy-subrc.
DATA(lt_b) = lt0.
SORT lt_b BY carrid connid.
DELETE ADJACENT DUPLICATES FROM lt_b COMPARING carrid connid.
DATA(lt_c) = lt0.
SORT lt_c BY carrid.
DELETE ADJACENT DUPLICATES FROM lt_c COMPARING carrid.
```

(4) (레거시 필기 단골) `WRITE`가 출력하는 세 값을 쓰고 단계별로 설명하시오. 헤더 라인 테이블에서 본문을 지우는 방법 세 가지와 헤더 라인을 쓰지 말아야 하는 이유를 쓰시오.
```abap
DATA: itab TYPE STANDARD TABLE OF i WITH HEADER LINE,
      lv1  TYPE i,
      lv2  TYPE i.
itab = 1. APPEND itab.
itab = 2. APPEND itab.
CLEAR itab.
APPEND itab.
DESCRIBE TABLE itab LINES lv1.
READ TABLE itab INDEX 2.
REFRESH itab.
DESCRIBE TABLE itab LINES lv2.
WRITE: / lv1, itab, lv2.
```

<details><summary>정답·해설</summary>

**(1)** (A): (LH, 17), (AA, 6), (UA, 3) / 마지막: (LH, 17), (AA, 100) / rc1 = 4, rc2 = 4
- `COLLECT`는 같은 키(carrid)의 행이 있으면 키가 아닌 숫자 필드를 더하고 없으면 새 행을 추가한다. 키가 아닌 컴포넌트는 모두 숫자형이어야 한다.
- `MODIFY ... WHERE`는 `TRANSPORTING`이 필수이고 조건에 맞는 모든 행의 지정 필드만 바꾼다 → AA = 100. `DELETE ... WHERE seats < 10` → UA 삭제.
- `MODIFY TABLE`은 키로 행을 찾아 바꾸는 문장이라 SQ 행이 없으면 추가하지 않고 sy-subrc = 4(DB의 `MODIFY`는 없으면 INSERT하는 UPSERT).
- 행이 2개뿐이라 `INDEX 5` 삭제는 sy-subrc = 4.

**(2)** `lv_str` = `[2:12][3:7][4:20]`, rc1 = 0, rc2 = 4
- `WHERE`로 걸러도 `sy-tabix`는 원래 테이블의 행 인덱스. 한 행이라도 처리하면 루프 후 sy-subrc = 0, 하나도 없으면 4.
- standard 테이블의 `WHERE`는 전체를 훑는다. 큰 테이블에서는 sorted 테이블이나 sorted secondary key를 써서 키 필드 `=` 조건으로 걸러야 최적화된다.

**(3)** `lines( lt_a )` = 5, `rc_a` = 4, `lt_b` = (AA 0017), (LH 0400), (LH 0402), `lines( lt_c )` = 2
- `DELETE ADJACENT DUPLICATES`는 **바로 이웃한** 행끼리만 비교한다. 정렬 전 lt_a는 LH, AA, LH, AA, LH라 지워지는 행이 없고 sy-subrc = 4.
- 정렬 후에는 중복이 붙어 carrid+connid 기준 3행.
- lt_c는 AA, LH 2행. 어떤 connid 행이 남는지는 `SORT`가 안정 정렬이 아니라 정해지지 않는다(`SORT ... STABLE`이나 `BY carrid connid`로 정렬하면 정해진다).
- `COMPARING`을 생략하면 primary key로 비교하는데 empty key이면 의미가 없으니 항상 명시한다.

**(4)** `3  2  0`
1. 헤더 라인에 1 → APPEND → [1]. 2 → APPEND → [1, 2].
2. `CLEAR itab`은 헤더 라인이 있는 테이블에서 **헤더 라인만** 지운다(0). 본문은 그대로.
3. `APPEND itab` → [1, 2, 0], lv1 = 3.
4. `READ TABLE itab INDEX 2` → 결과가 헤더 라인으로 들어와 헤더 = 2.
5. `REFRESH itab`은 **본문만** 비운다. 헤더는 2로 남고 lv2 = 0.
- 본문 지우기: `CLEAR itab[]` / `REFRESH itab` / `FREE itab`(메모리 해제까지). 헤더 라인은 이름 하나가 두 대상을 가리켜 헷갈리므로 클래스 안에서는 금지되고 새 코드에서도 쓰지 않는다.

</details>

---

### A-019. 컨트롤 레벨 처리(AT NEW/END OF/SUM/LAST)와 LOOP AT GROUP BY [코드] ★★★
<!-- src: IS-008, IS-010, MX-010 -->
항공사·노선별 집계를 두 방식으로 만든다.

(1) 다음 코드의 출력을 순서대로 쓰시오(서식 무시).
```abap
TYPES: BEGIN OF ty_s,
         carrid TYPE s_carr_id,
         connid TYPE s_conn_id,
         seats  TYPE i,
       END OF ty_s.
DATA: lt TYPE STANDARD TABLE OF ty_s WITH EMPTY KEY,
      ls TYPE ty_s.
lt = VALUE #( ( carrid = 'AA' connid = '0017' seats = 10 )
              ( carrid = 'AA' connid = '0064' seats = 20 )
              ( carrid = 'LH' connid = '0400' seats = 5 )
              ( carrid = 'LH' connid = '0400' seats = 7 ) ).
LOOP AT lt INTO ls.
  AT NEW carrid.
    WRITE: / 'NEW', ls-carrid.
  ENDAT.
  AT END OF connid.
    SUM.
    WRITE: / 'SUB', ls-connid, ls-seats.
  ENDAT.
  AT LAST.
    SUM.
    WRITE: / 'TOT', ls-seats.
  ENDAT.
ENDLOOP.
```

(2) (A)의 `lv_out`, `lv_cnt_a`와 (B)의 `lv_cnt_b`를 쓰시오. (B)가 그렇게 되는 이유를 설명하시오.
```abap
" (A)
TYPES: BEGIN OF ty_a,
         carrid TYPE c LENGTH 3,
         connid TYPE n LENGTH 4,
         price  TYPE i,
       END OF ty_a.
DATA lt_a TYPE STANDARD TABLE OF ty_a WITH EMPTY KEY.
DATA lv_out   TYPE string.
DATA lv_cnt_a TYPE i.
lt_a = VALUE #( ( carrid = 'LH' connid = '0400' price = 100 )
                ( carrid = 'AA' connid = '0017' price = 200 )
                ( carrid = 'LH' connid = '0402' price = 300 )
                ( carrid = 'AA' connid = '0064' price = 50 ) ).
SORT lt_a BY carrid connid.
LOOP AT lt_a INTO DATA(ls_a).
  AT NEW carrid.
    lv_cnt_a = lv_cnt_a + 1.
  ENDAT.
  AT END OF carrid.
    SUM.
    lv_out = |{ lv_out }{ ls_a-carrid }={ ls_a-price };|.
  ENDAT.
ENDLOOP.

" (B) 컴포넌트 순서만 다르다
TYPES: BEGIN OF ty_b,
         connid TYPE n LENGTH 4,
         carrid TYPE c LENGTH 3,
         price  TYPE i,
       END OF ty_b.
DATA lt_b TYPE STANDARD TABLE OF ty_b WITH EMPTY KEY.
DATA lv_cnt_b TYPE i.
lt_b = CORRESPONDING #( lt_a ).
SORT lt_b BY carrid connid.
LOOP AT lt_b INTO DATA(ls_b).
  AT NEW carrid.
    lv_cnt_b = lv_cnt_b + 1.
  ENDAT.
ENDLOOP.
```

(3) 컨트롤 레벨 처리를 올바르게 쓰기 위한 조건 세 가지와, `AT` 블록 안에서 작업 영역 값에 대한 주의점을 쓰시오.

(4) 같은 집계를 `LOOP AT ... GROUP BY`로 바꾼 코드다. 빈칸을 채우고, 그룹 키에 넣을 수 있는 정보, 멤버 처리 방법, `AT NEW`보다 안전한 이유를 쓰시오.
```abap
DATA lv_sum TYPE i.
LOOP AT lt_sflight INTO DATA(ls_f)
     ____①____ ( carrid = ls_f-carrid
                 size   = ____②____ )
     ASCENDING
     ASSIGNING FIELD-SYMBOL(<ls_grp>).
  CLEAR lv_sum.
  LOOP AT ____③____ <ls_grp> INTO DATA(ls_member).
    lv_sum = lv_sum + ls_member-seatsocc.
  ENDLOOP.
  DATA(lv_sum2) = REDUCE i( INIT s = 0
                            FOR m IN ____④____ <ls_grp>
                            NEXT s = s + m-seatsocc ).
  APPEND |{ <ls_grp>-carrid }: { <ls_grp>-size } rows, { lv_sum } seats| TO lt_log.
ENDLOOP.
" 그룹 키만 필요하고 멤버 루프가 필요 없을 때 붙이는 추가어: ____⑤____
```

<details><summary>정답·해설</summary>

**(1)**
```
NEW AA
SUB 0017 10
SUB 0064 20
NEW LH
SUB 0400 12
TOT 42
```
`AT END OF connid`의 기준은 connid **와 그 왼쪽 필드 전부**(carrid+connid). 3·4행은 LH/0400으로 같아 4행에서 한 번만 실행되고 SUM = 5+7 = 12. `AT LAST`의 SUM은 전체 합 42.

**(2)** (A) `lv_out` = `AA=250;LH=400;`, `lv_cnt_a` = 2 / (B) `lv_cnt_b` = 4
- (A) 정렬 결과 AA 0017 200, AA 0064 50, LH 0400 100, LH 0402 300. `AT NEW carrid` 2번, `AT END OF carrid`의 `SUM`은 그룹의 숫자 필드 합을 작업 영역에 넣는다 → AA 250, LH 400.
- (B) 제어 수준은 **지정한 필드와 그 왼쪽의 모든 필드**가 바뀌는지를 본다. ty_b는 connid가 carrid 왼쪽에 있고 4행의 connid가 모두 달라 `AT NEW carrid`가 매 행 실행된다.

**(3)** (1) 그룹 필드를 구조의 앞쪽(맨 왼쪽부터)에 두고 (2) 그 순서대로 정렬하고 (3) `LOOP`에 `WHERE`를 쓰지 않는다. `AT` 블록 안에서 기준 필드보다 오른쪽 컴포넌트는 원래 행의 값이 아니다(초기화되거나 `SUM` 결과). 그래서 `AT NEW carrid` 안에서 connid·seats를 출력하면 원래 값이 나오지 않는다.

**(4)** ① `GROUP BY` ② `GROUP SIZE` ③ `GROUP` ④ `GROUP` ⑤ `WITHOUT MEMBERS`
- 그룹 키를 구조로 쓰면 `<ls_grp>-carrid`처럼 접근한다. `GROUP SIZE`(행 수), `GROUP INDEX`(그룹 번호)를 넣을 수 있다.
- 바깥 루프는 그룹당 한 번 돈다. 멤버는 `LOOP AT GROUP` 또는 `FOR ... IN GROUP`.
- 정렬이 필요 없고 필드 순서에 의존하지 않으므로 (2)(B)의 함정이 없다. 최신 코드에서는 GROUP BY가 더 안전하다.

</details>

---

### A-020. 내부 테이블 오류 수정·secondary key·룩업 테이블 작성 [작성] ★★★
<!-- src: IS-011, IS-014, IS-015 -->
SFLIGHT/SBOOK 데이터를 내부 테이블로 처리하는 코드를 고치고 작성한다.

(1) 다음 코드의 문제 4곳을 찾아 오류 종류(문법/런타임/논리), 이유, 고친 코드를 쓰시오.
```abap
DATA lt_sort TYPE SORTED TABLE OF sflight WITH UNIQUE KEY carrid connid fldate.
DATA lt_std  TYPE STANDARD TABLE OF sflight WITH EMPTY KEY.
DATA ls      TYPE sflight.
SELECT * FROM sflight INTO TABLE @lt_std.
LOOP AT lt_std INTO ls.
  APPEND ls TO lt_sort.                                         " (a)
ENDLOOP.
SORT lt_sort BY price.                                          " (b)
READ TABLE lt_std INTO ls WITH KEY carrid = 'LH' BINARY SEARCH. " (c)
LOOP AT lt_std INTO ls.                                         " (d)
  ls-price = ls-price * '1.1'.
ENDLOOP.
```

(2) 다음을 만족하는 코드를 작성하시오.
- a. SFLIGHT 행을 담는 standard 테이블 타입 `ty_flights`를 empty primary key로 정의하고, `carrid`와 `fldate`로 된 non-unique sorted secondary key `k_date`를 추가한다.
- b. 이 타입의 `lt_flights`에 SFLIGHT 전체를 읽는다.
- c. secondary key로 carrid = `'LH'`, fldate = `'20241015'`인 첫 행을 `READ TABLE`로 읽는다.
- d. secondary key로 carrid = `'LH'`인 행만 루프를 돌며 seatsocc 합계를 구한다.

(3) (2)에서 키 이름을 지정하지 않고 `WITH KEY carrid = ...`만 쓰면 어떻게 되는가? 앞쪽 컴포넌트만으로 조회할 때와 `USING KEY` 루프의 `sy-tabix`에 대해 쓰시오.

(4) `lt_booking`(컴포넌트: carrid, connid, fldate, bookid, carrname)의 각 행에 SCARR의 `carrname`을 채우는 코드를 작성하시오. `LOOP` 안 `SELECT`나 standard 테이블 중첩 `LOOP` 없이 키 접근이 O(1)인 방식을 쓰고, 찾지 못하면 carrname을 비운다. 채점 포인트, 더 나은 방법, table expression을 쓸 때 주의점을 쓰시오.

<details><summary>정답·해설</summary>

**(1)**
- (a) 런타임 오류: sorted 테이블에 `APPEND`하면서 정렬 순서가 어긋나면 `ITAB_ILLEGAL_SORT_ORDER`, 중복 키면 역시 런타임 오류. → `INSERT ls INTO TABLE lt_sort.`(중복은 sy-subrc 4) 또는 루프 없이 `lt_sort = CORRESPONDING #( lt_std DISCARDING DUPLICATES ).`
- (b) 문법 오류: sorted 테이블은 `SORT`할 수 없다. price 순서가 필요하면 standard 테이블에 복사해 정렬하거나 price에 sorted secondary key를 둔다.
- (c) 논리 오류: `lt_std`가 carrid로 정렬되어 있지 않아 `BINARY SEARCH` 결과를 믿을 수 없다. → 먼저 `SORT lt_std BY carrid.`(또는 `SELECT ... ORDER BY carrid`로 DB에서 정렬)
- (d) 논리 오류: `INTO`는 복사본이라 테이블이 바뀌지 않는다. → `LOOP AT lt_std ASSIGNING FIELD-SYMBOL(<ls>). <ls>-price = <ls>-price * '1.1'. ENDLOOP.`(또는 루프 안 `MODIFY lt_std FROM ls.`)

**(2)**
```abap
TYPES ty_flights TYPE STANDARD TABLE OF sflight
                 WITH EMPTY KEY
                 WITH NON-UNIQUE SORTED KEY k_date COMPONENTS carrid fldate.
DATA lt_flights TYPE ty_flights.
DATA lv_sum     TYPE i.

SELECT * FROM sflight INTO TABLE @lt_flights.

READ TABLE lt_flights INTO DATA(ls_flight)
     WITH KEY k_date COMPONENTS carrid = 'LH' fldate = '20241015'.
IF sy-subrc = 0.
  " ls_flight 사용
ENDIF.

LOOP AT lt_flights INTO DATA(ls_f) USING KEY k_date WHERE carrid = 'LH'.
  lv_sum = lv_sum + ls_f-seatsocc.
ENDLOOP.
```

**(3)** 키 이름을 지정하지 않으면 secondary key는 쓰이지 않고 primary key 기준 선형 탐색이 된다. sorted key는 앞쪽 컴포넌트(carrid)만으로도 최적화된 부분 키 조회가 된다. `USING KEY`로 루프를 돌면 `sy-tabix`는 secondary key 기준 순번이다.

**(4)**
```abap
DATA lt_scarr TYPE HASHED TABLE OF scarr WITH UNIQUE KEY carrid.

SELECT * FROM scarr INTO TABLE @lt_scarr.

LOOP AT lt_booking ASSIGNING FIELD-SYMBOL(<ls_b>).
  READ TABLE lt_scarr INTO DATA(ls_c) WITH TABLE KEY carrid = <ls_b>-carrid.
  IF sy-subrc = 0.
    <ls_b>-carrname = ls_c-carrname.
  ELSE.
    CLEAR <ls_b>-carrname.
  ENDIF.
ENDLOOP.
```
- 채점 포인트: hashed(또는 sorted) 테이블, 루프 밖 1회 `SELECT`, `ASSIGNING`으로 직접 수정, 미존재 처리.
- 더 나은 방법: 처음부터 SBOOK과 SCARR을 `JOIN`해서 읽는다(코드 푸시다운).
- table expression을 쓴다면 `IF line_exists( lt_scarr[ carrid = <ls_b>-carrid ] ).`로 먼저 확인하거나 `TRY ... CATCH`로 감싼다.

</details>

---

## ABAP SQL

### A-021. 신규 SQL 문법·SELECT SINGLE vs UP TO·INTO vs APPENDING [코드] ★★
<!-- src: IS-016, IS-017, IS-018, MX-011 -->
클래식 Open SQL로 쓰인 리포트를 신규 문법으로 바꾼다.

(1) 7.40 SP05 이후의 신규(strict) ABAP SQL 문법이 클래식 Open SQL과 다른 점을 5가지 이상 쓰시오. 테이블 별칭 선택자와 ABAP 구조 컴포넌트 선택자도 구분하시오.

(2) 빈칸을 채우시오. `INTO`를 마지막 절로 쓸 때 `UP TO n ROWS`의 위치, `@( ... )`의 이름과 의미를 쓰시오.
```abap
DATA lv_carrid TYPE s_carr_id VALUE 'LH'.
DATA lv_price  TYPE s_price   VALUE 300.

SELECT carrid, connid, fldate, price            " 최근 날짜부터 10건
  FROM sflight
  WHERE carrid = ____①____lv_carrid
  ORDER BY fldate ____②____
  INTO TABLE ____③____(lt_flights)
  UP TO 10 ROWS.

SELECT SINGLE FROM scarr                        " FROM을 먼저 쓰는 형식
  ____④____ carrname, currcode
  WHERE carrid = @lv_carrid
  INTO @DATA(ls_carr).

SELECT carrid, connid, fldate                   " ABAP 식을 조건에
  FROM sflight
  WHERE price > ____⑤____( lv_price * 2 )
  INTO TABLE @DATA(lt_expensive).
```

(3) `SELECT SINGLE`과 `SELECT ... UP TO 1 ROWS`의 차이와 각각 언제 쓰는지 쓰시오. 존재 여부만 확인하는 SQL과, 둘의 성공/실패 시 `sy-subrc`·`sy-dbcnt`를 쓰시오.

(4) SCARR에는 carrid가 `AA`, `LH`, `UA`인 행만 있다. (A)~(D)에서 `sy-subrc`, `sy-dbcnt`, `lines( lt_carr )`를 표로 쓰고 이유를 설명하시오.
```abap
DATA lt_carr TYPE STANDARD TABLE OF s_carr_id WITH DEFAULT KEY.
lt_carr = VALUE #( ( 'ZZ' ) ( 'YY' ) ).
SELECT carrid FROM scarr WHERE carrid = 'XX'
  INTO TABLE @lt_carr.
" (A)
SELECT carrid FROM scarr WHERE carrid IN ( 'AA', 'LH' )
  APPENDING TABLE @lt_carr.
" (B)
SELECT carrid FROM scarr WHERE carrid = 'UA'
  APPENDING TABLE @lt_carr.
" (C)
SELECT carrid FROM scarr WHERE carrid = 'QQ'
  APPENDING TABLE @lt_carr.
" (D)
```

<details><summary>정답·해설</summary>

**(1)**
1. 호스트 변수(ABAP 변수)는 `@`를 붙인다(`WHERE carrid = @lv_carrid`, `INTO TABLE @lt`). ABAP 식은 `@( ... )`.
2. SELECT 목록의 컬럼은 콤마로 구분한다.
3. `INTO` 절은 다른 절 뒤(맨 끝)에 둔다. `FIELDS` 추가어로 `SELECT FROM tab FIELDS ...`처럼 `FROM`을 먼저 쓸 수 있다.
4. `INTO @DATA(...)`, `INTO TABLE @DATA(...)` 인라인 선언.
5. SQL 식(`CASE`, `COALESCE`, `CAST`, 산술, 문자열 함수), 집계, `UNION`, 서브쿼리, `FROM @itab` 등 DB 계산 기능 확장.
6. 신규 문법 요소를 하나라도 쓰면 strict mode로 검사되어 옛 문법과 섞어 쓸 수 없다. ABAP Cloud는 strict 문법만 허용.
- 테이블 별칭 컬럼 선택자는 `~`(`c~carrid`), `-`는 ABAP 구조 컴포넌트에만 쓴다.

**(2)** ① `@` ② `DESCENDING` ③ `@DATA` ④ `FIELDS` ⑤ `@`. `INTO`를 마지막 절로 쓸 때 `UP TO n ROWS`는 그 뒤에 둔다. `@( ... )`는 host expression으로 ABAP 쪽에서 계산한 값을 넘긴다. `SELECT SINGLE`은 primary key 전체로 조건을 줄 때 의미가 분명하다.

**(3)**
- `SELECT SINGLE`: 한 행을 구조로 받는 단일 행 조회. primary key 전체를 `WHERE`에 지정해 "그 한 건"을 읽을 때 쓴다. key 전체가 아니면 어느 행이 올지 정해지지 않고 문법 검사 경고가 나온다. `ORDER BY`를 쓸 수 없다.
- `UP TO 1 ROWS`: 여러 행 조회에 행 수 제한. `ORDER BY`와 함께 "가장 최근 1건", "가장 비싼 1건"처럼 기준을 정해 첫 행을 가져올 때 쓴다. `INTO TABLE`로 받거나, 구조로 받으면 `SELECT ... ENDSELECT` 루프가 된다.
- 존재 확인: `SELECT SINGLE @abap_true FROM ... WHERE ... INTO @DATA(lv_exists).`
- 둘 다 찾으면 sy-subrc = 0, sy-dbcnt = 1, 못 찾으면 sy-subrc = 4.

**(4)**

| 지점 | sy-subrc | sy-dbcnt | lines |
|---|---|---|---|
| A | 4 | 0 | 0 |
| B | 0 | 2 | 2 |
| C | 0 | 1 | 3 |
| D | 4 | 0 | 3 |

- `INTO TABLE`은 결과를 넣기 전에 대상 테이블을 비운다. 읽은 행이 없어도 비워지므로 (A)에서 ZZ·YY가 사라진다.
- `APPENDING TABLE`은 기존 행 뒤에 붙이고, 읽은 행이 없으면 테이블은 그대로(D).
- sy-dbcnt는 **이번 문장이** 읽은 행 수(누적 아님).

</details>

---

### A-022. JOIN·집계·HAVING·SQL 식·UNION·서브쿼리 [코드] ★★★
<!-- src: IS-019, IS-020, IS-024, IS-025, IS-026 -->
SFLIGHT 데이터 분석용 SQL을 검토한다. 각 소문항의 DB 데이터는 소문항에 적힌 것만 있다고 가정한다.

(1) SCARR에는 carrid AA, LH, SQ 3행, SPFLI에는 (AA, 0017), (LH, 0400), (LH, 0402) 3행만 있다. 질문에 답하시오.
```abap
SELECT c~carrid, p~connid                                       " (a) 행 수
  FROM scarr AS c INNER JOIN spfli AS p ON p~carrid = c~carrid
  INTO TABLE @DATA(lt_inner).
SELECT c~carrid, p~connid                                       " (b) 행 수, SQ 행의 connid
  FROM scarr AS c LEFT OUTER JOIN spfli AS p ON p~carrid = c~carrid
  INTO TABLE @DATA(lt_left).
SELECT c~carrid, COUNT( DISTINCT p~connid ) AS cnt, COUNT( * ) AS cnt_all   " (c) 항공사별 cnt, cnt_all
  FROM scarr AS c LEFT OUTER JOIN spfli AS p ON p~carrid = c~carrid
  GROUP BY c~carrid
  INTO TABLE @DATA(lt_cnt).
```

(2) SFLIGHT에 (carrid, connid, fldate, price, seatsocc) = (LH, 0400, 20241001, 500, 100), (LH, 0400, 20241002, 600, 150), (LH, 0402, 20241001, 300, 50), (AA, 0017, 20241001, 400, 100), (AA, 0017, 20241002, 400, 100) 5행만 있다. `lt_res`의 내용과 `sy-dbcnt`를 쓰시오. `WHERE`와 `HAVING`의 차이, `GROUP BY` 사용 시 SELECT 목록 규칙을 쓰시오.
```abap
SELECT carrid,
       COUNT( * )      AS cnt,
       SUM( seatsocc ) AS seats,
       MAX( price )    AS max_price
  FROM sflight
  GROUP BY carrid
  HAVING SUM( seatsocc ) > 250
  ORDER BY carrid
  INTO TABLE @DATA(lt_res).
```

(3) 빈칸을 채우시오. SQL `CASE`에 `ELSE`가 없을 때 결과, `division`/`div`/`mod`/`/`의 차이를 쓰시오.
```abap
SELECT FROM sflight
  FIELDS carrid, connid, fldate,
         ____①____ WHEN seatsocc >= seatsmax THEN 'FULL'
                   WHEN seatsocc = 0         THEN 'EMPTY'
                   ELSE 'OPEN'
         ____②____ AS status,
         ____③____( seatsocc, seatsmax, 2 ) AS occ_ratio,
         ____④____( price AS DEC( 17, 2 ) ) AS price_dec
  INTO TABLE @DATA(lt_status).
SELECT FROM scarr AS c
       LEFT OUTER JOIN spfli AS p ON p~carrid = c~carrid
  FIELDS c~carrid,
         ____⑤____( p~cityfrom, 'N/A' ) AS cityfrom     " 노선 없는 항공사는 'N/A'
  INTO TABLE @DATA(lt_city).
```

(4) SCARR (carrid, currcode) = (AA, USD), (LH, EUR), (AF, EUR), (UA, USD), SPFLI (carrid, connid, countryfr) = (AA, 0017, US), (AA, 0064, US), (LH, 0400, DE), (LH, 0401, US), (UA, 0941, US)일 때 각 결과의 행 수와 (c)(d)의 carrid를 쓰시오.
```abap
SELECT carrid FROM scarr WHERE currcode = 'EUR'          " (a)
UNION
SELECT carrid FROM spfli WHERE countryfr = 'US'
INTO TABLE @DATA(lt_union).
SELECT carrid FROM scarr WHERE currcode = 'EUR'          " (b)
UNION ALL
SELECT carrid FROM spfli WHERE countryfr = 'US'
INTO TABLE @DATA(lt_union_all).
SELECT carrid FROM scarr AS c                            " (c)
  WHERE NOT EXISTS ( SELECT carrid FROM spfli WHERE carrid = c~carrid )
  INTO TABLE @DATA(lt_no_conn).
SELECT carrid FROM scarr                                 " (d)
  WHERE carrid IN ( SELECT carrid FROM spfli WHERE countryfr = 'DE' )
  INTO TABLE @DATA(lt_de).
```

(5) 다음 중 **옳지 않은** 것을 고르고 이유를 쓰시오.
① `SELECT ... INTO TABLE` 후 `sy-dbcnt`는 읽은 행 수이고, 한 행도 없으면 `sy-subrc`는 4이다.
② `FOR ALL ENTRIES IN @itab`에서 itab이 비어 있으면 WHERE 조건이 무시되어 모든 행을 읽는다.
③ primary key 전체를 지정하지 않은 `SELECT SINGLE`은 조건에 맞는 여러 행 중 어느 행이 올지 보장되지 않는다.
④ LEFT OUTER JOIN에서 오른쪽 테이블 컬럼 조건을 `WHERE` 절에 쓰든 `ON` 절에 쓰든 결과는 항상 같다.
⑤ `FROM @itab`으로 내부 테이블을 데이터 소스로 쓸 때는 별칭(`AS`)을 지정해야 한다.

<details><summary>정답·해설</summary>

**(1)** (a) 3행 (b) 4행, SQ 행의 connid = `0000`(초기값) (c) AA: cnt 1, cnt_all 1 / LH: cnt 2, cnt_all 2 / SQ: cnt 0, cnt_all 1
- INNER JOIN은 양쪽에 짝이 있는 행만: AA-0017, LH-0400, LH-0402.
- LEFT OUTER JOIN은 왼쪽(SCARR) 행을 모두 남기고 짝이 없으면 오른쪽 컬럼이 DB에서 NULL이 된다. ABAP 대상 변수에는 NULL이 없으므로 타입 초기값(`n`이면 `0000`)이 들어간다.
- `COUNT( DISTINCT 컬럼 )`은 NULL을 세지 않고 `COUNT( * )`는 행 자체를 세므로 SQ도 1. 짝 없는 그룹을 0으로 세려면 컬럼 기준으로 센다.

**(2)** `lt_res` = 1행: carrid `LH`, cnt 3, seats 300, max_price 600 / `sy-dbcnt` = 1
- LH 3행, 좌석 100 + 150 + 50 = 300, 최대 가격 600. AA 2행, 좌석 200 → `HAVING`에서 탈락.
- 행 단위 조건은 `WHERE`, 그룹 집계 결과 조건은 `HAVING`.
- `GROUP BY`를 쓰면 SELECT 목록의 집계 함수가 아닌 컬럼은 모두 `GROUP BY`에 있어야 한다. `SELECT ... INTO TABLE` 후 `sy-dbcnt`는 읽은 행 수.

**(3)** ① `CASE` ② `END` ③ `division` ④ `CAST` ⑤ `coalesce`
- SQL의 `CASE ... END`는 ABAP `COND`와 비슷하고 `ELSE`가 없으면 결과는 NULL.
- `division( a, b, 소수자리 )`는 소수 결과 나눗셈, `div( a, b )`는 정수 나눗셈, `mod( a, b )`는 나머지. SQL의 `/`는 부동소수점 피연산자용.
- `coalesce( a, b )`는 a가 NULL이면 b(OUTER JOIN의 NULL 처리에 자주 쓴다). `CAST`로 DB 타입을 바꾼다.

**(4)** (a) 4행 (AA, AF, LH, UA) (b) 6행 (c) 1행, AF (d) 1행, LH
- 첫 SELECT: LH, AF(2행). 두 번째: AA, AA, LH, UA(4행).
- `UNION`(= `UNION DISTINCT`)은 중복 제거 → 4행. `UNION ALL`은 중복 유지 → 2 + 4 = 6행.
- `NOT EXISTS` 상관 서브쿼리: 노선이 없는 항공사는 AF뿐. `IN ( 서브쿼리 )`: 독일 출발 노선이 있는 항공사는 LH.
- `UNION` 결과 순서는 `ORDER BY`가 없으면 정해지지 않는다.

**(5)** ④ — `ON`에 쓴 오른쪽 조건은 "짝을 찾는 조건"이라 왼쪽 행은 모두 남는다. `WHERE`에 쓰면 조인 후 결과를 거르므로 NULL이 된 왼쪽 행이 빠져 사실상 INNER JOIN이 된다. ① ② ③ ⑤ 옳다.

</details>

---

### A-023. DB 변경 문의 sy-subrc·sy-dbcnt와 FOR ALL ENTRIES 함정 [코드] ★★★
<!-- src: IS-021, IS-023 -->
SCARR과 같은 구조의 Z 테이블 `ZSCARR`(primary key: mandt, carrid)에 처음에 AA(currcode `USD`)와 LH(currcode `USD`) 두 행만 있다.

```abap
DATA ls     TYPE zscarr.
DATA lt_new TYPE STANDARD TABLE OF zscarr WITH EMPTY KEY.

ls = VALUE #( carrid = 'LH' carrname = 'Lufthansa' currcode = 'EUR' ).
INSERT zscarr FROM @ls.                                          " (a)
lt_new = VALUE #( ( carrid = 'SQ' carrname = 'Singapore' currcode = 'SGD' )
                  ( carrid = 'LH' carrname = 'Lufthansa' currcode = 'EUR' ) ).
INSERT zscarr FROM TABLE @lt_new ACCEPTING DUPLICATE KEYS.       " (b)
UPDATE zscarr SET currcode = 'EUR' WHERE carrid = 'LH'.          " (c)
ls = VALUE #( carrid = 'XX' carrname = 'Nobody' currcode = 'USD' ).
UPDATE zscarr FROM @ls.                                          " (d)
ls = VALUE #( carrid = 'UA' carrname = 'United' currcode = 'USD' ).
MODIFY zscarr FROM @ls.                                          " (e)
DELETE FROM zscarr WHERE currcode = 'KRW'.                       " (f)
```

(1) (a)~(f) 각 문장 직후의 `sy-subrc`와 `sy-dbcnt`를 쓰시오. (b) 실행 후 테이블의 carrid 목록도 쓰시오.

(2) (b)에서 `ACCEPTING DUPLICATE KEYS`가 없었다면 어떻게 되는가? DB `MODIFY`의 동작, 변경이 확정되는 시점, mandt 필드 처리를 쓰시오.

(3) 출발 도시 `lv_city`의 노선에 대해 좌석 점유 합계를 구하려는 아래 코드의 문제점 2가지를 찾아 왜 잘못된 결과가 나오는지 설명하고 고치시오.
```abap
SELECT carrid, connid
  FROM spfli
  WHERE cityfrom = @lv_city
  INTO TABLE @DATA(lt_spfli).

SELECT carrid, connid, seatsocc
  FROM sflight
  FOR ALL ENTRIES IN @lt_spfli
  WHERE carrid = @lt_spfli-carrid
    AND connid = @lt_spfli-connid
  INTO TABLE @DATA(lt_flights).

DATA(lv_total) = REDUCE i( INIT s = 0 FOR f IN lt_flights NEXT s = s + f-seatsocc ).
```

(4) (3)을 JOIN 한 번으로 해결하는 SQL을 쓰고, `FOR ALL ENTRIES`의 내부 테이블에 중복이 많을 때 DB 부하를 줄이는 방법을 쓰시오.

<details><summary>정답·해설</summary>

**(1)**
- (a) 4, 0 — 같은 키가 있으면 단일 행 `INSERT`는 넣지 않고 sy-subrc = 4.
- (b) 4, 1 / carrid: AA, LH, SQ — 중복 행만 버리고 나머지(SQ)를 넣으며 sy-subrc = 4, sy-dbcnt = 실제로 넣은 행 수.
- (c) 0, 1 — 조건에 맞는 1행 변경.
- (d) 4, 0 — 작업 영역 기반 `UPDATE`는 키로 행을 찾는데 XX가 없다.
- (e) 0, 1 — UA 추가.
- (f) 4, 0 — 삭제 대상 없음.

**(2)** `FROM TABLE`에 중복 키가 섞이면 원래는 예외 `CX_SY_OPEN_SQL_DB`(처리하지 않으면 런타임 오류)가 난다. DB의 `MODIFY`는 없으면 INSERT, 있으면 UPDATE(UPSERT). 변경은 `COMMIT WORK` 전까지 확정되지 않는다. client 필드 mandt는 자동으로 현재 클라이언트가 들어간다.

**(3)**
1. `lt_spfli`가 비어 있으면(해당 도시 노선 없음) `FOR ALL ENTRIES`의 WHERE 조건이 무시되어 SFLIGHT **전체**를 읽는다. → `IF lt_spfli IS NOT INITIAL.`로 감싼다.
2. `FOR ALL ENTRIES` 결과는 중복 행이 자동 제거된다. SELECT 목록에 키(fldate)가 없어서 같은 노선에 seatsocc가 같은 날짜가 여러 개면 한 행만 남아 합계가 작게 나온다. → primary key 전체(`carrid, connid, fldate`)를 SELECT 목록에 넣는다.
```abap
IF lt_spfli IS NOT INITIAL.
  SELECT carrid, connid, fldate, seatsocc
    FROM sflight
    FOR ALL ENTRIES IN @lt_spfli
    WHERE carrid = @lt_spfli-carrid
      AND connid = @lt_spfli-connid
    INTO TABLE @DATA(lt_flights).
ENDIF.
```

**(4)**
```abap
SELECT FROM sflight AS f
       INNER JOIN spfli AS p ON f~carrid = p~carrid AND f~connid = p~connid
  FIELDS SUM( f~seatsocc )
  WHERE p~cityfrom = @lv_city
  INTO @DATA(lv_total).
```
중복이 많으면 미리 `SORT` + `DELETE ADJACENT DUPLICATES`로 줄인다.

</details>

---

### A-024. SQL 성능: LOOP 안 SELECT·대용량 SELECT·커서 패키지 처리 [개념] ★★★
<!-- src: IS-022, MX-012, MX-013 -->
야간 배치가 느리고 가끔 메모리 부족으로 덤프가 난다.

(1) `LOOP AT` 안에서 행마다 `SELECT SINGLE`을 실행하는 코드가 왜 성능 문제를 일으키는지 설명하고 대안을 4가지 쓰시오. 집계가 목적일 때의 원칙과 SAP HANA 시대의 성능 원칙 세 가지를 쓰시오.

(2) SELECT 결과가 너무 커서 메모리 부족 덤프(TSV_TNEW_PAGE_ALLOC_FAILED 등)가 난다. 대처 방법을 5가지 이상 쓰시오. 메모리 파라미터를 늘리는 방법은 어떤 위치인가?

(3) SBOOK을 1만 건씩 읽어 처리하는 코드다. 빈칸 ①~④를 채우시오.
```abap
DATA: lv_cursor TYPE cursor,
      lt_pkg    TYPE STANDARD TABLE OF sbook.

____①____ @lv_cursor FOR
  SELECT * FROM sbook WHERE fldate >= @p_date.
DO.
  ____②____ @lv_cursor INTO TABLE @lt_pkg ____③____ 10000.
  IF sy-subrc <> 0.
    EXIT.
  ENDIF.
  PERFORM process_package USING lt_pkg.
ENDDO.
____④____ @lv_cursor.
```

(4) (3)에서 `FETCH ... INTO TABLE`과 `APPENDING TABLE`의 차이, 더 읽을 행이 없을 때 `sy-subrc`를 쓰시오. `process_package` 안에서 패키지마다 DB 커밋을 해야 한다면 ①에 무엇을 덧붙이고 커밋은 어떻게 해야 하는지, `SELECT ... PACKAGE SIZE ... ENDSELECT` 루프 안에서 커밋하면 어떻게 되는지 쓰시오.

<details><summary>정답·해설</summary>

**(1)** 행 수만큼 DB 왕복(round trip)이 생긴다. 1만 행이면 1만 번 요청·응답이 오가고 매번 SQL 처리·네트워크 비용이 든다. DB가 한 번에 집합으로 처리하면 훨씬 빠르다.
1. JOIN으로 한 번에 읽는다(또는 연관을 가진 CDS 뷰).
2. 키 목록을 모아 `FOR ALL ENTRIES` 한 번으로 읽은 뒤 hashed/sorted 테이블로 룩업.
3. 7.52 이상이면 `FROM @itab`/`JOIN @itab`으로 내부 테이블을 SQL에 넘겨 DB에서 조인.
4. 마스터 데이터처럼 작은 테이블은 루프 전에 한 번 전부 읽어 hashed 테이블에 둔다(테이블 버퍼링도 고려).
- 집계는 ABAP에서 더하지 말고 `SUM`/`GROUP BY`로 DB에서 계산(코드 푸시다운).
- 원칙: 전송 데이터 최소화(필요한 컬럼만, `SELECT *` 지양), 왕복 횟수 최소화, 계산은 DB로.

**(2)**
1. 나눠 읽기: `PACKAGE SIZE`나 `OPEN CURSOR`/`FETCH`로 패키지 단위로 읽고 처리한 패키지는 `FREE`로 비운다.
2. 덜 읽기: 필요한 열만, WHERE 조건을 DB에서 최대한 걸러지게(인덱스 활용).
3. DB에서 계산: `SUM`/`COUNT`/`GROUP BY`나 CDS 뷰로 집계해 결과 행 수를 줄인다(코드 푸시다운).
4. 복사 줄이기: `LOOP ... INTO` 대신 `ASSIGNING`/`REFERENCE INTO`, 같은 데이터를 담은 내부 테이블을 여러 개 만들지 않는다.
5. 범위 분할·병렬 처리: 키 범위(날짜·회사 코드)로 나눠 백그라운드 잡이나 aRFC(SPTA 프레임워크)로 병렬 처리.
6. 결과를 화면에 한 번에 띄우지 말고 파일·후속 테이블로 흘려보낸다.
- 메모리 파라미터(ztta/roll_extension 등)를 늘리는 것은 마지막 수단이다(채점 시 이것만 쓰면 부분 점수).

**(3)** ① `OPEN CURSOR` ② `FETCH NEXT CURSOR` ③ `PACKAGE SIZE` ④ `CLOSE CURSOR`

**(4)** `FETCH ... INTO TABLE`은 매번 테이블 내용을 새 패키지로 **바꾸고**, 누적하려면 `APPENDING TABLE`. 더 읽을 행이 없으면 sy-subrc = 4. 커밋이 필요하면 `OPEN CURSOR WITH HOLD`로 열고 `CALL FUNCTION 'DB_COMMIT'`(또는 Native SQL 커밋)으로 커밋한다. `COMMIT WORK`/`ROLLBACK WORK`나 암시적 DB 커밋은 WITH HOLD 커서도 닫아 버린다. `SELECT ... PACKAGE SIZE n ... ENDSELECT`도 같은 효과를 내지만 루프 안에서 커밋하면 커서가 닫혀 덤프가 난다.

</details>

---

### A-025. 집계 SQL과 내부 테이블 JOIN 작성 [작성] ★★★
<!-- src: IS-027, IS-028 -->
예약 분석 리포트의 SQL을 직접 작성한다.

(1) SBOOK과 SCARR을 이용해 2024년 비행(fldate가 2024년)의 예약 중 취소되지 않은(cancelled가 `'X'`가 아닌) 예약을 항공사별로 집계하는 ABAP SQL을 작성하시오. 결과 컬럼은 carrid, carrname, 예약 건수 `bookings`, 현지 통화 금액 합계 `revenue`(loccuram 합계), 통화 `loccurkey`이다. 예약 건수가 100건 넘는 항공사만, 금액 합계 내림차순으로 `lt_result`에 담는다.

(2) (1)의 채점 포인트 다섯 가지와, 통화 키로도 그룹을 나누는 이유, 날짜 리터럴 표기법을 쓰시오.

(3) `lt_keys`(컴포넌트 carrid, connid; 중복 없음)에 들어 있는 노선의 SFLIGHT 행(carrid, connid, fldate, seatsocc)을 `FOR ALL ENTRIES` 없이 내부 테이블과의 JOIN으로 읽는 코드를 작성하시오(`lt_keys`의 타입 선언 포함).

(4) (3) 방식의 필수 문법, 데이터 처리 위치, `FOR ALL ENTRIES` 대비 장점 두 가지, 제약을 쓰시오.

<details><summary>정답·해설</summary>

**(1)**
```abap
SELECT FROM sbook AS b
       INNER JOIN scarr AS c ON c~carrid = b~carrid
  FIELDS b~carrid,
         c~carrname,
         COUNT( * )        AS bookings,
         SUM( b~loccuram ) AS revenue,
         b~loccurkey
  WHERE b~fldate BETWEEN '20240101' AND '20241231'
    AND b~cancelled <> 'X'
  GROUP BY b~carrid, c~carrname, b~loccurkey
  HAVING COUNT( * ) > 100
  ORDER BY revenue DESCENDING
  INTO TABLE @DATA(lt_result).
```

**(2)** 콤마·`~`·`@` 신규 문법, `WHERE`(행 조건)와 `HAVING`(그룹 조건) 구분, 집계하지 않는 컬럼 모두 `GROUP BY`에 포함, `ORDER BY`에 별칭 사용, `INTO` 맨 끝. 금액은 통화가 다르면 더하면 안 되므로 통화 키로도 그룹을 나눈다. 날짜 리터럴은 문자 리터럴 `'YYYYMMDD'`(또는 호스트 변수).

**(3)**
```abap
TYPES: BEGIN OF ty_key,
         carrid TYPE s_carr_id,
         connid TYPE s_conn_id,
       END OF ty_key.
DATA lt_keys TYPE SORTED TABLE OF ty_key WITH UNIQUE KEY carrid connid.

SELECT f~carrid, f~connid, f~fldate, f~seatsocc
  FROM sflight AS f
  INNER JOIN @lt_keys AS k
    ON  f~carrid = k~carrid
    AND f~connid = k~connid
  INTO TABLE @DATA(lt_result).
```

**(4)** `@itab`은 반드시 별칭을 둔다. 내부 테이블 데이터가 DB로 전송되어 DB에서 조인한다. 장점: itab이 비면 INNER JOIN 결과도 비므로 "전체 읽기" 함정이 없고, 집계·`ORDER BY` 등 다른 SQL 기능과 자유롭게 조합할 수 있다. 제약: 지원 DB(HANA 등)에서만 동작하는 기능이라 다른 DB에서는 문법 검사 경고가 난다.

</details>

---

## 알고리즘 손코딩

### A-026. 텍스트 분석 클래스: 회문·단어 수·최장 단어·단어 빈도 [작성] ★★★
<!-- src: HC-029, AB-016, HC-032 -->
회사 코딩 테스트 단골 문자열 문제를 로컬 클래스 하나로 작성한다.

(1) 정적 메서드 `is_palindrome_a`, `is_palindrome_b`(`IMPORTING iv_text TYPE string RETURNING VALUE(rv) TYPE abap_bool`)를 작성하시오. 대소문자와 영숫자 이외의 문자(공백, 구두점)는 무시한다. A는 내장 함수(`to_upper`, `reverse` 등)로, B는 `reverse` 없이 양 끝에서 한 글자씩 비교(두 포인터)한다. 정규화는 private 메서드로 공통화한다.

(2) `A man, a plan, a canal: Panama`, `ABAP`, `Was it a car or a cat I saw?`, 빈 문자열에 대한 두 메서드의 결과를 출력하는 메인을 쓰고 출력 결과를 쓰시오.

(3) `string` 변수 `lv_text`(예: `` `ABAP is fun and   powerful` ``, 단어 사이 공백이 여러 개일 수 있음)의 단어 수 `lv_count`와 가장 긴 단어 `lv_longest`(같은 길이면 먼저 나온 단어)를 구하는 코드를 쓰고 결과를 쓰시오.

(4) 문장 하나(선택화면 `p_text`, 기본값 `The cat and the hat, and THE bat!`)를 받아 단어별 출현 횟수를 세어 횟수 내림차순(같으면 단어 오름차순)으로 상위 3개를 출력하는 프로그램을 쓰시오. 대소문자 무시(소문자로), 쉼표·마침표·느낌표·물음표 제거, 연속 공백은 한 칸. 방법 1은 `GROUP BY`, 방법 2는 HASHED 테이블 갱신으로 세고, 출력 결과를 쓰시오.

(5) 다음에 답하시오: `xsdbool`과 `boolc`의 차이, POSIX `REGEX`의 최신 대안, 정규식 없이 영숫자를 거르는 방법, 숫자 회문(12321) 변형의 풀이, `ASSIGN itab[ ... ] TO <fs>`가 "있으면 증가, 없으면 삽입"에 알맞은 이유, `COLLECT` 방식으로 세는 법, `LOOP AT ... TO 3`의 의미와 정렬에 동률 기준이 필요한 이유.

<details><summary>정답·해설</summary>

**(1)(2)**
```abap
REPORT zhc_palindrome.

CLASS lcl_text DEFINITION.
  PUBLIC SECTION.
    CLASS-METHODS is_palindrome_a IMPORTING iv_text TYPE string
                                  RETURNING VALUE(rv) TYPE abap_bool.
    CLASS-METHODS is_palindrome_b IMPORTING iv_text TYPE string
                                  RETURNING VALUE(rv) TYPE abap_bool.
  PRIVATE SECTION.
    CLASS-METHODS normalize IMPORTING iv_text TYPE string
                            RETURNING VALUE(rv) TYPE string.
ENDCLASS.

CLASS lcl_text IMPLEMENTATION.
  METHOD normalize.
    rv = to_upper( iv_text ).
    REPLACE ALL OCCURRENCES OF REGEX '[^A-Z0-9]' IN rv WITH ''.
  ENDMETHOD.

  METHOD is_palindrome_a.
    DATA(lv) = normalize( iv_text ).
    rv = xsdbool( lv = reverse( lv ) ).
  ENDMETHOD.

  METHOD is_palindrome_b.
    DATA(lv) = normalize( iv_text ).
    DATA(lv_i) = 0.
    DATA(lv_j) = strlen( lv ) - 1.
    WHILE lv_i < lv_j.
      IF lv+lv_i(1) <> lv+lv_j(1).
        rv = abap_false.
        RETURN.
      ENDIF.
      lv_i += 1.
      lv_j -= 1.
    ENDWHILE.
    rv = abap_true.
  ENDMETHOD.
ENDCLASS.

START-OF-SELECTION.
  DATA(lt_words) = VALUE string_table( ( `A man, a plan, a canal: Panama` )
                                       ( `ABAP` )
                                       ( `Was it a car or a cat I saw?` )
                                       ( `` ) ).
  LOOP AT lt_words INTO DATA(lv_word).
    WRITE: / |"{ lv_word }" A={ lcl_text=>is_palindrome_a( lv_word ) } | &&
             |B={ lcl_text=>is_palindrome_b( lv_word ) }|.
  ENDLOOP.
```
출력: Panama 문장 `A=X B=X`, `ABAP` `A= B=`(거짓은 공백), 자동차 문장 `A=X B=X`, 빈 문자열 `A=X B=X`(빈 문자열은 회문으로 본다).

채점(100점): 정규화(대문자 + 영숫자 외 제거) 25 / 방법 A: reverse 비교, xsdbool 20 / 방법 B: 두 포인터 루프, 불일치 시 조기 종료 35 / 빈 문자열·한 글자 처리(루프 조건 `<`) 10 / 메인 출력 10. 부분 문자열은 `lv+off(len)` 대신 `substring( val = lv off = lv_i len = 1 )`도 정답.

**(3)**
```abap
DATA(lv_text) = `ABAP is fun and   powerful`.
DATA lv_longest TYPE string.

SPLIT lv_text AT space INTO TABLE DATA(lt_words).
DELETE lt_words WHERE table_line IS INITIAL.   " 연속 공백으로 생긴 빈 행 제거
DATA(lv_count) = lines( lt_words ).

LOOP AT lt_words INTO DATA(lv_word).
  IF strlen( lv_word ) > strlen( lv_longest ).
    lv_longest = lv_word.
  ENDIF.
ENDLOOP.
" lv_count = 5, lv_longest = powerful
```
채점 포인트: `SPLIT ... INTO TABLE`, 빈 행 제거(또는 먼저 `CONDENSE lv_text.` → `DELETE` 불필요), `lines( )`, 엄격한 `>` 비교로 먼저 나온 단어 유지.

**(4)**
```abap
REPORT zhc_word_count.

PARAMETERS p_text TYPE c LENGTH 200 LOWER CASE
           DEFAULT 'The cat and the hat, and THE bat!'.

TYPES: BEGIN OF ty_freq,
         word TYPE string,
         cnt  TYPE i,
       END OF ty_freq,
       tt_freq TYPE STANDARD TABLE OF ty_freq WITH EMPTY KEY.

START-OF-SELECTION.
  " 전처리
  DATA(lv_text) = to_lower( CONV string( p_text ) ).
  REPLACE ALL OCCURRENCES OF REGEX '[,.!?]' IN lv_text WITH ''.
  CONDENSE lv_text.
  SPLIT lv_text AT space INTO TABLE DATA(lt_words).

  " 방법 1: GROUP BY
  DATA(lt_freq1) = VALUE tt_freq(
    FOR GROUPS grp OF w IN lt_words
        GROUP BY w
    ( word = grp
      cnt  = REDUCE i( INIT n = 0 FOR m IN GROUP grp NEXT n = n + 1 ) ) ).

  " 방법 2: HASHED 테이블 갱신
  DATA lt_hash TYPE HASHED TABLE OF ty_freq WITH UNIQUE KEY word.
  LOOP AT lt_words INTO DATA(lv_word).
    ASSIGN lt_hash[ word = lv_word ] TO FIELD-SYMBOL(<f>).
    IF sy-subrc = 0.
      <f>-cnt += 1.
    ELSE.
      INSERT VALUE #( word = lv_word cnt = 1 ) INTO TABLE lt_hash.
    ENDIF.
  ENDLOOP.
  DATA(lt_freq2) = CORRESPONDING tt_freq( lt_hash ).

  " 정렬 후 상위 3개
  SORT lt_freq1 BY cnt DESCENDING word ASCENDING.
  LOOP AT lt_freq1 INTO DATA(ls_f) TO 3.
    WRITE: / ls_f-word, ls_f-cnt.
  ENDLOOP.
```
출력: `the 3` / `and 2` / `bat 1`

채점(100점): 소문자 변환·구두점 제거·CONDENSE 20 / SPLIT ... INTO TABLE 15 / 방법 1: GROUP BY + 개수(REDUCE, GROUP SIZE, LOOP AT GROUP 등) 25 / 방법 2: 해시 룩업 후 증가 또는 삽입(또는 COLLECT) 25 / 정렬(두 키) + 상위 3개 15.

**(5)**
- `xsdbool( 조건 )`은 참이면 `'X'`, 거짓이면 `' '`(c 1자리). `boolc`는 string을 돌려줘 비교 시 함정이 있어 `xsdbool`이 권장된다.
- POSIX 정규식(`REGEX`)은 7.55 이후 폐기 예정 경고가 나므로 `PCRE '[^A-Z0-9]'`를 쓴다. 정규식 없이 `IF lv_char CA sy-abcde OR lv_char CA '0123456789'`로 한 글자씩 걸러도 된다.
- 숫자 회문: 숫자를 `|{ n }|`로 문자열로 바꾸거나, `MOD 10`/`DIV 10`으로 뒤집은 수를 만들어 비교한다(A-027 (1)).
- `CONDENSE`로 앞뒤 공백을 지우고 연속 공백을 한 칸으로 만들어야 SPLIT 결과에 빈 단어가 생기지 않는다.
- `ASSIGN itab[ ... ] TO <fs>`는 행이 없으면 예외 대신 sy-subrc = 4를 준다.
- COLLECT 방식: 행 타입을 `word TYPE c LENGTH 30, cnt TYPE i`로 두고 `COLLECT VALUE ty_freq_c( word = lv_word cnt = 1 ) INTO lt_tab.` 비숫자 컴포넌트가 키가 되어 같은 단어면 cnt가 더해진다.
- `LOOP AT ... TO 3`은 인덱스 1~3행만 처리한다. 동률 기준(단어 오름차순)을 정렬에 넣어야 결과가 하나로 정해진다(bat, cat, hat 중 bat). `GROUP BY w`의 그룹 키는 단어 자체이고 `FOR GROUPS ... OF`는 그룹마다 한 번 반복한다.

</details>

---

### A-027. 숫자 알고리즘: 자릿수·소수·피보나치·진법 변환 [작성] ★★★
<!-- src: AB-025, HC-030, HC-031, HC-037 -->
숫자 처리 손코딩 문제를 모았다.

(1) 양의 정수 `lv_num`(예: 12345)의 자릿수 합 `lv_sum`(15)과 자릿수를 뒤집은 수 `lv_rev`(54321)를 `WHILE` 루프로 구하시오(문자열 변환 금지). `lv_num = lv_num / 10`이라고 쓰면 어떻게 되는가?

(2) 선택화면 `p_n`(TYPE i, 기본 50)을 받아 다음을 하는 프로그램을 작성하시오.
- `is_prime( iv_n ) RETURNING abap_bool` — √n까지만 나눠 보는 방식
- 에라토스테네스의 체로 2부터 p_n까지의 소수를 한 줄에 10개씩 출력하고 개수 출력
- `p_n`이 2 미만이거나 100,000 초과면 선택화면 오류

p_n = 50일 때 출력을 쓰고, √n까지만 검사하는 이유, 두 방법의 시간 복잡도, 체에서 i*i부터 지우는 이유를 쓰시오.

(3) 선택화면 `p_n`을 받아 피보나치 수열의 처음 `p_n`개(0, 1, 1, 2, 3, ...)를 한 줄에 출력하는 프로그램을 반복문으로 작성하시오. 값 타입은 i, i 범위를 넘는 n은 선택화면에서 막는다(몇 번째 항부터 넘치는지 근거와 함께). 넘치면 어떤 오류가 나는가?

(4) F(0) = 0, F(1) = 1인 피보나치 n번째 항을 구하는 재귀 메서드를 쓰고 시간 복잡도와 개선 방법을 쓰시오. 50번째 항까지 출력하려면 무엇을 바꿔야 하는지 쓰시오.

(5) 로컬 클래스 `lcl_algo`에 정적 메서드 두 개를 작성하시오.
- `to_binary( iv_n TYPE i ) RETURNING string` — 0 이상의 10진수를 2진 문자열로(0 → `0`, 10 → `1010`)
- `from_binary( iv_bin TYPE string ) RETURNING i` — 2진 문자열을 10진수로, `0`/`1` 이외 문자가 있거나 비어 있으면 `cx_sy_conversion_no_number`를 던진다

<details><summary>정답·해설</summary>

**(1)**
```abap
DATA(lv_num) = 12345.
DATA lv_sum TYPE i.
DATA lv_rev TYPE i.

WHILE lv_num > 0.
  DATA(lv_digit) = lv_num MOD 10.
  lv_sum = lv_sum + lv_digit.
  lv_rev = lv_rev * 10 + lv_digit.
  lv_num = lv_num DIV 10.
ENDWHILE.
```
`/`를 쓰면 12345 / 10 = 1234.5가 반올림되어 1235가 되므로 결과가 틀어진다(A-002 참고). 핵심은 `DIV`.

**(2)**
```abap
REPORT zhc_prime.

PARAMETERS p_n TYPE i DEFAULT 50.

CLASS lcl_prime DEFINITION.
  PUBLIC SECTION.
    CLASS-METHODS is_prime IMPORTING iv_n TYPE i
                           RETURNING VALUE(rv) TYPE abap_bool.
    CLASS-METHODS sieve IMPORTING iv_max TYPE i
                        RETURNING VALUE(rt) TYPE int4_table.
ENDCLASS.

CLASS lcl_prime IMPLEMENTATION.
  METHOD is_prime.
    IF iv_n < 2.
      RETURN.                                   " rv = 초기값(거짓)
    ENDIF.
    DATA(lv_d) = 2.
    WHILE lv_d * lv_d <= iv_n.
      IF iv_n MOD lv_d = 0.
        RETURN.
      ENDIF.
      lv_d += 1.
    ENDWHILE.
    rv = abap_true.
  ENDMETHOD.

  METHOD sieve.
    DATA lt_flag TYPE STANDARD TABLE OF abap_bool WITH EMPTY KEY.
    DO iv_max TIMES.                            " 인덱스 = 숫자
      APPEND abap_true TO lt_flag.
    ENDDO.
    lt_flag[ 1 ] = abap_false.                  " 1은 소수 아님

    DATA(lv_i) = 2.
    WHILE lv_i * lv_i <= iv_max.
      IF lt_flag[ lv_i ] = abap_true.
        DATA(lv_j) = lv_i * lv_i.
        WHILE lv_j <= iv_max.
          lt_flag[ lv_j ] = abap_false.
          lv_j += lv_i.
        ENDWHILE.
      ENDIF.
      lv_i += 1.
    ENDWHILE.

    LOOP AT lt_flag INTO DATA(lv_flag).
      IF lv_flag = abap_true.
        APPEND sy-tabix TO rt.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.
ENDCLASS.

AT SELECTION-SCREEN.
  IF p_n < 2 OR p_n > 100000.
    MESSAGE 'N은 2 ~ 100000 사이여야 합니다' TYPE 'E'.
  ENDIF.

START-OF-SELECTION.
  DATA(lt_primes) = lcl_prime=>sieve( p_n ).
  LOOP AT lt_primes INTO DATA(lv_p).
    IF ( sy-tabix - 1 ) MOD 10 = 0.
      NEW-LINE.
    ENDIF.
    WRITE lv_p.
  ENDLOOP.
  DATA(lv_cnt) = lines( lt_primes ).
  WRITE: / '소수 개수:', lv_cnt.

  " 두 방법 결과 대조
  DATA(lv_check) = REDUCE i( INIT c = 0 FOR k = 2 UNTIL k > p_n
                             NEXT c = c + COND i( WHEN lcl_prime=>is_prime( k ) = abap_true THEN 1 ELSE 0 ) ).
  WRITE: / '나눗셈 검사 결과 개수:', lv_check.
```
p_n = 50: `2 3 5 7 11 13 17 19 23 29` / `31 37 41 43 47`, 개수 15.
- n = a × b이면 a, b 중 하나는 √n 이하라 √n까지만 본다. 나눗셈 검사 O(√n), 체 O(n log log n).
- i*i 미만의 배수는 더 작은 소수가 이미 지웠기 때문에 i*i부터 시작한다.
- `int4_table`은 i 행 타입의 DDIC 표준 테이블 타입(로컬 `TYPES tt_int TYPE STANDARD TABLE OF i WITH EMPTY KEY.`도 가능). `lt_flag[ lv_j ] = abap_false.`처럼 테이블 식을 쓰기 위치에 쓸 수 있다(행이 없으면 `CX_SY_ITAB_LINE_NOT_FOUND`).
- 채점(100점): is_prime(2 미만 처리, `d * d <= n`, MOD 판정) 30 / 체 초기화·1 제외 15 / i*i부터 i 간격 지우기, i*i <= max까지 25 / 결과 수집·10개씩 줄바꿈·개수 20 / 선택화면 검증 10.

**(3)**
```abap
REPORT zhc_fibonacci.

PARAMETERS p_n TYPE i DEFAULT 10.

AT SELECTION-SCREEN.
  IF p_n < 1 OR p_n > 47.                 " F(0)~F(46)까지 47개가 i 범위
    MESSAGE '1 ~ 47 사이로 입력하십시오' TYPE 'E'.
  ENDIF.

START-OF-SELECTION.
  DATA: lv_a TYPE i VALUE 0,
        lv_b TYPE i VALUE 1,
        lv_next TYPE i,
        lv_out TYPE string.

  DO p_n TIMES.
    lv_out = |{ lv_out }{ lv_a } |.
    IF sy-index < p_n.                    " 마지막 반복 뒤에는 다음 항 계산 안 함
      lv_next = lv_a + lv_b.
      lv_a = lv_b.
      lv_b = lv_next.
    ENDIF.
  ENDDO.
  WRITE / lv_out.
```
`p_n = 10` → `0 1 1 2 3 5 8 13 21 34`. i 최댓값 2,147,483,647: F(46) = 1,836,311,903은 들어가고 F(47) = 2,971,215,073은 넘친다 → 처음 47개(F(0)~F(46))까지. 위 코드는 마지막 반복에서 다음 항을 계산하지 않으므로 p_n = 47에서도 F(47)을 계산하지 않는다. 정수 오버플로는 조용히 값이 바뀌지 않고 catchable 런타임 오류 `CX_SY_ARITHMETIC_OVERFLOW`가 난다.

**(4)**
```abap
CLASS lcl_fib DEFINITION.
  PUBLIC SECTION.
    CLASS-METHODS fib IMPORTING iv_n TYPE i
                      RETURNING VALUE(rv) TYPE i.
ENDCLASS.

CLASS lcl_fib IMPLEMENTATION.
  METHOD fib.
    rv = COND #( WHEN iv_n < 2 THEN iv_n
                 ELSE fib( iv_n - 1 ) + fib( iv_n - 2 ) ).
  ENDMETHOD.
ENDCLASS.
```
- O(2ⁿ)(정확히는 약 1.6ⁿ): 같은 항을 반복해서 다시 계산한다. 개선: 메모이제이션(해시 테이블 `n → F(n)`, O(n)) 또는 (3)처럼 반복문(O(n), 메모리 O(1)).
- 50번째 항: 값 타입을 `int8`(7.50 이상, 약 9.2×10¹⁸, F(92)까지), `p LENGTH 16 DECIMALS 0`(31자리), `decfloat34`로 바꾸고 선택화면 상한도 맞춘다.
- 채점(100점): (3) 두 변수 교대 갱신·첫 두 항 30, 출력 형식 10, 오버플로 경계(47개/F(46)) + 선택화면 검증 20 / (4) 재귀(기저 조건) 20, 복잡도·개선 10, 타입 변경 10.

**(5)**
```abap
CLASS lcl_algo DEFINITION.
  PUBLIC SECTION.
    CLASS-METHODS to_binary   IMPORTING iv_n TYPE i
                              RETURNING VALUE(rv) TYPE string.
    CLASS-METHODS from_binary IMPORTING iv_bin TYPE string
                              RETURNING VALUE(rv) TYPE i
                              RAISING   cx_sy_conversion_no_number.
ENDCLASS.

CLASS lcl_algo IMPLEMENTATION.
  METHOD to_binary.
    IF iv_n = 0.
      rv = `0`.
      RETURN.
    ENDIF.
    DATA(lv_n) = iv_n.
    WHILE lv_n > 0.
      rv = |{ lv_n MOD 2 }{ rv }|.           " 나머지를 앞에 붙임
      lv_n = lv_n DIV 2.
    ENDWHILE.
  ENDMETHOD.

  METHOD from_binary.
    IF iv_bin IS INITIAL OR iv_bin CN '01'.
      RAISE EXCEPTION TYPE cx_sy_conversion_no_number
        EXPORTING value = iv_bin.
    ENDIF.
    DO strlen( iv_bin ) TIMES.
      DATA(lv_off) = sy-index - 1.
      rv = rv * 2 + CONV i( iv_bin+lv_off(1) ).
    ENDDO.
  ENDMETHOD.
ENDCLASS.
```
`to_binary( 10 )` = `1010`, `from_binary( `1010` )` = 10. `CN`(contains not only)은 왼쪽에 오른쪽에 없는 문자가 하나라도 있으면 참이다. `cx_sy_conversion_no_number`는 생성자에 `value`를 받을 수 있다. 채점: to_binary(0 처리, MOD/DIV 반복, 앞에 붙이기) 30 / from_binary(입력 검사 `CN '01'` + 예외, 누적 `rv * 2 + 비트`) 30.

</details>

---

### A-028. 내부 테이블 알고리즘: 순서 유지 중복 제거·정렬 구현·이진 탐색 [작성] ★★★
<!-- src: HC-033, HC-034, HC-037 -->
`SORT`나 `READ TABLE ... BINARY SEARCH` 같은 내장 기능 없이 테이블 알고리즘을 직접 구현한다.

(1) 정수 내부 테이블 `lt_in = [3, 1, 3, 2, 1, 5, 2]`에서 처음 나온 순서를 유지하며 중복을 제거해 `[3, 1, 2, 5]`를 만드시오(`SORT`, `DELETE ADJACENT DUPLICATES` 금지). 같은 테이블을 `SORT` + `DELETE ADJACENT DUPLICATES`로 처리하면 결과가 어떻게 다른지, 정렬 없이 `DELETE ADJACENT DUPLICATES`만 쓰면 어떻게 되는지 쓰시오.

(2) 문자열 `programming`에서 중복 문자를 제거해 `progamin`을 만드는 코드를 쓰시오. SFLIGHT를 읽은 내부 테이블에서 CARRID·CONNID 조합이 같은 행을 하나만 남기는 코드를 쓰시오(정렬 순서 무관).

(3) `SORT` 없이 정수 테이블을 오름차순 정렬하는 메서드 `bubble_sort( CHANGING ct_tab TYPE int4_table )`(한 바퀴 동안 교환이 없으면 조기 종료)와 `selection_sort( CHANGING ct_tab TYPE int4_table )`를 작성하시오. `[5, 2, 9, 1, 5, 6]`의 결과와 두 알고리즘의 시간 복잡도(최선/최악), 안정 정렬 여부를 쓰시오.

(4) `binary_search( it_tab TYPE int4_table iv_key TYPE i ) RETURNING i` — 오름차순 정렬된 테이블에서 키의 인덱스를, 없으면 0을 돌려주는 메서드를 작성하시오. `[1,3,5,7,9]`에서 7과 4의 결과, 시간 복잡도, `mid` 계산의 오버플로 주의점을 쓰시오.

(5) 다음에 답하시오: 유일 키 테이블에 중복 `INSERT ... INTO TABLE`할 때의 동작과 이를 이용한 중복 판정의 복잡도(standard 테이블 `line_exists` 반복과 비교), `NS` 연산자의 의미와 대소문자 구분 대안, 중첩 `DO`에서 바깥 반복 번호를 따로 저장해야 하는 이유, `DO 0 TIMES`의 동작, ABAP `SORT`의 안정성.

<details><summary>정답·해설</summary>

**(1)(2)**
```abap
REPORT zhc_dedup.

START-OF-SELECTION.
  " (1) 순서 유지 중복 제거
  DATA(lt_in) = VALUE int4_table( ( 3 ) ( 1 ) ( 3 ) ( 2 ) ( 1 ) ( 5 ) ( 2 ) ).
  DATA: lt_out  TYPE int4_table,
        lt_seen TYPE HASHED TABLE OF i WITH UNIQUE KEY table_line.

  LOOP AT lt_in INTO DATA(lv_n).
    INSERT lv_n INTO TABLE lt_seen.
    IF sy-subrc = 0.                     " 처음 본 값이면 삽입 성공
      APPEND lv_n TO lt_out.
    ENDIF.
  ENDLOOP.
  " lt_out = 3, 1, 2, 5

  " (2) 문자열 중복 문자 제거
  DATA(lv_text)   = `programming`.
  DATA(lv_result) = ``.
  DO strlen( lv_text ) TIMES.
    DATA(lv_off) = sy-index - 1.
    DATA(lv_ch)  = lv_text+lv_off(1).
    IF lv_result NS lv_ch.               " 아직 결과에 없는 문자
      lv_result = lv_result && lv_ch.
    ENDIF.
  ENDDO.
  " lv_result = progamin

  " (2) 키 조합 중복 제거
  SELECT carrid, connid, fldate FROM sflight INTO TABLE @DATA(lt_fl).
  SORT lt_fl BY carrid connid.
  DELETE ADJACENT DUPLICATES FROM lt_fl COMPARING carrid connid.
```
- `SORT` 후 `DELETE ADJACENT DUPLICATES`는 `[1, 2, 3, 5]`: 중복은 제거되지만 원래 등장 순서(3, 1, 2, 5)가 사라진다. **인접한** 같은 행만 지우므로 정렬 없이 쓰면 `[3, 1, 3, 2, 1, 5, 2]` 그대로.
- `COMPARING`을 생략하면 행 전체(또는 테이블 키)가 같은 경우에만 지운다. 7.40 신문법으로는 `VALUE #( FOR GROUPS g OF r IN lt_fl GROUP BY ( c = r-carrid n = r-connid ) ( ... ) )`도 가능.
- 채점(100점): 본 값 기록용 해시(또는 정렬) 테이블 + 순서 유지 30 / INSERT의 sy-subrc(4 = 중복) 또는 line_exists 10 / 결과 차이와 "인접" 조건 20 / 문자 단위 반복과 포함 검사(NS/CS/find) 25 / SORT + DELETE ADJACENT DUPLICATES COMPARING 15.

**(3)**
```abap
REPORT zhc_sort.

CLASS lcl_sort DEFINITION.
  PUBLIC SECTION.
    CLASS-METHODS bubble_sort    CHANGING ct_tab TYPE int4_table.
    CLASS-METHODS selection_sort CHANGING ct_tab TYPE int4_table.
  PRIVATE SECTION.
    CLASS-METHODS swap IMPORTING iv_i TYPE i iv_j TYPE i
                       CHANGING  ct_tab TYPE int4_table.
ENDCLASS.

CLASS lcl_sort IMPLEMENTATION.
  METHOD swap.
    DATA(lv_tmp) = ct_tab[ iv_i ].
    ct_tab[ iv_i ] = ct_tab[ iv_j ].
    ct_tab[ iv_j ] = lv_tmp.
  ENDMETHOD.

  METHOD bubble_sort.
    DATA(lv_n) = lines( ct_tab ).
    DO lv_n - 1 TIMES.
      DATA(lv_pass)    = sy-index.
      DATA(lv_swapped) = abap_false.
      DO lv_n - lv_pass TIMES.                 " 뒤쪽 pass개는 이미 확정
        DATA(lv_j) = sy-index.
        IF ct_tab[ lv_j ] > ct_tab[ lv_j + 1 ].
          swap( EXPORTING iv_i = lv_j iv_j = lv_j + 1 CHANGING ct_tab = ct_tab ).
          lv_swapped = abap_true.
        ENDIF.
      ENDDO.
      IF lv_swapped = abap_false.
        EXIT.                                  " 이미 정렬됨
      ENDIF.
    ENDDO.
  ENDMETHOD.

  METHOD selection_sort.
    DATA(lv_n) = lines( ct_tab ).
    DO lv_n - 1 TIMES.
      DATA(lv_i)   = sy-index.
      DATA(lv_min) = lv_i.
      DATA(lv_k)   = lv_i + 1.
      WHILE lv_k <= lv_n.
        IF ct_tab[ lv_k ] < ct_tab[ lv_min ].
          lv_min = lv_k.
        ENDIF.
        lv_k += 1.
      ENDWHILE.
      IF lv_min <> lv_i.
        swap( EXPORTING iv_i = lv_i iv_j = lv_min CHANGING ct_tab = ct_tab ).
      ENDIF.
    ENDDO.
  ENDMETHOD.
ENDCLASS.

START-OF-SELECTION.
  DATA(lt_a) = VALUE int4_table( ( 5 ) ( 2 ) ( 9 ) ( 1 ) ( 5 ) ( 6 ) ).
  DATA(lt_b) = lt_a.
  lcl_sort=>bubble_sort( CHANGING ct_tab = lt_a ).
  lcl_sort=>selection_sort( CHANGING ct_tab = lt_b ).
  LOOP AT lt_a INTO DATA(lv_v).
    WRITE lv_v.
  ENDLOOP.
```
결과: `1 2 5 5 6 9`(두 방법 같음)

| 알고리즘 | 최선 | 최악/평균 | 안정성 |
|---|---|---|---|
| 버블(조기 종료) | O(n) (이미 정렬됨) | O(n²) | 안정(인접한 큰 값만 교환) |
| 선택 | O(n²) | O(n²) | 불안정(멀리 떨어진 값과 교환) |

채점(100점): 교환 로직(임시 변수) 10 / 버블: 이중 반복, 범위(n − pass), 인접 비교 25 / 버블 조기 종료 10 / 선택: 최솟값 위치 + 한 번 교환 25 / 결과·복잡도·안정성 20 / 경계(빈 테이블, 1행) 10.

**(4)**
```abap
CLASS lcl_search DEFINITION.
  PUBLIC SECTION.
    CLASS-METHODS binary_search IMPORTING it_tab TYPE int4_table
                                          iv_key TYPE i
                                RETURNING VALUE(rv) TYPE i.
ENDCLASS.

CLASS lcl_search IMPLEMENTATION.
  METHOD binary_search.
    DATA(lv_lo) = 1.
    DATA(lv_hi) = lines( it_tab ).
    WHILE lv_lo <= lv_hi.
      DATA(lv_mid) = ( lv_lo + lv_hi ) DIV 2.
      DATA(lv_val) = it_tab[ lv_mid ].
      IF lv_val = iv_key.
        rv = lv_mid.
        RETURN.
      ELSEIF lv_val < iv_key.
        lv_lo = lv_mid + 1.
      ELSE.
        lv_hi = lv_mid - 1.
      ENDIF.
    ENDWHILE.
    rv = 0.
  ENDMETHOD.
ENDCLASS.
```
- 7 → 4, 4 → 0. O(log n). `READ TABLE ... BINARY SEARCH`도 같은 원리라 테이블이 그 키로 정렬돼 있지 않으면 결과가 틀린다(면접 단골). SORTED 테이블은 키 접근 시 자동으로 이진 탐색을 쓴다.
- `mid = (lo + hi) DIV 2`는 i 범위 근처에서 오버플로할 수 있어 `lo + (hi - lo) DIV 2`를 권장(가산 포인트).
- 채점: lo/hi/mid, 경계 갱신(mid ± 1), 종료 조건 `lo <= hi` 30 / 없을 때 0, 빈 테이블(hi = 0이면 루프 미실행) 10.

**(5)**
- 유일 키 테이블에 중복 키를 `INSERT ... INTO TABLE`하면 런타임 오류 없이 sy-subrc = 4(APPEND와 다름). 이를 "이미 본 값" 판정에 쓰면 O(n). standard 테이블에서 `line_exists`로 매번 찾으면 O(n²).
- `NS`(contains no string)는 왼쪽에 오른쪽 문자열이 없으면 참. 대소문자를 구분하지 않으므로 구분이 필요하면 `find( val = lv_result sub = lv_ch ) = -1`.
- 바깥 `DO` 안에서 안쪽 `DO`를 쓰면 `sy-index`가 안쪽 값으로 바뀌므로 바깥 반복 번호를 `lv_pass`에 먼저 저장한다(손코딩에서 자주 틀리는 부분).
- `DO 0 TIMES`나 `DO -1 TIMES`는 한 번도 실행되지 않아 빈 테이블과 1행 테이블도 안전하다.
- ABAP의 `SORT`는 기본적으로 안정 정렬이 아니며 순서 보존이 필요하면 `SORT ... STABLE`(면접 보너스 질문).

</details>

---

### A-029. 출력·변환 손코딩: 구구단·별 피라미드·금액 한글 변환 [작성] ★★★
<!-- src: HC-036, HC-035 -->
출력 형식을 직접 조립하는 문제다.

(1) 2단부터 9단까지 `2 x 1 = 2` 형식으로, 각 단을 한 블록씩(단 사이에 빈 줄) 출력하는 코드를 작성하시오.

(2) 선택화면 높이 `p_h`(기본 5)를 받아 가운데 정렬된 별 피라미드를 출력하시오. 높이 3이면 다음과 같다. 줄마다 앞 공백 수와 별 수의 공식을 쓰시오.
```
  *
 ***
*****
```

(3) 0 이상 정수 금액(최대 16자리)을 한글 금액 문자열로 바꾸는 정적 메서드 `to_korean( iv_amount ) RETURNING VALUE(rv) TYPE string`을 작성하시오.
- 숫자: 일 이 삼 사 오 육 칠 팔 구, 작은 단위: 십 백 천, 큰 단위(4자리마다): 만 억 조
- 0인 자리는 읽지 않고, 네 자리 묶음 전체가 0이면 그 큰 단위도 붙이지 않는다.
- 자릿값 1도 "일"을 붙인다(10 → 일십, 1000 → 일천).
- 끝에 "원", 0은 "영원".
- 예: `12345` → `일만이천삼백사십오원`, `100000000` → `일억원`, `1010` → `일천일십원`, `2000500` → `이백만오백원`

(4) (3)에서 `2000500`을 자리별로 추적하시오. 가장 흔한 오답과 그 원인, "10은 십으로(일 생략)" 변형 규칙을 처리하는 방법을 쓰시오.

<details><summary>정답·해설</summary>

**(1)(2)**
```abap
REPORT zhc_gugudan NO STANDARD PAGE HEADING.

PARAMETERS p_h TYPE i DEFAULT 5.

START-OF-SELECTION.
  " (1) 구구단
  DO 8 TIMES.
    DATA(lv_dan) = sy-index + 1.             " 2 ~ 9
    DO 9 TIMES.
      DATA(lv_k) = sy-index.
      DATA(lv_line) = |{ lv_dan } x { lv_k } = { lv_dan * lv_k }|.
      WRITE / lv_line.
    ENDDO.
    SKIP.
  ENDDO.

  " (2) 별 피라미드
  DO p_h TIMES.
    DATA(lv_row)   = sy-index.
    DATA(lv_col)   = p_h - lv_row + 1.        " 시작 열(앞 공백 = p_h - row)
    DATA(lv_stars) = repeat( val = `*` occ = 2 * lv_row - 1 ).
    WRITE AT /lv_col lv_stars.
  ENDDO.
```
- i번째 줄: 앞 공백 h − i개, 별 2i − 1개.
- 안쪽 `DO`가 `sy-index`를 덮어쓰므로 단 번호를 `lv_dan`에 먼저 저장한다.
- `WRITE AT /col 값`은 새 줄의 col번째 열부터 출력한다. 콘솔 클래스(`out->write`)라면 앞 공백을 `repeat( val = ` ` occ = n )`으로 만들어 붙인다. `repeat`는 7.02+ 내장 함수이고, 없던 시절에는 `DO n TIMES. CONCATENATE lv lv_star INTO lv. ENDDO.`
- 채점(100점): (1) 이중 반복 20, 바깥 반복 번호 보관 15, 출력 형식·빈 줄 15 / (2) 공백 수(h − i)·별 수(2i − 1) 공식 30, 위치 지정 출력 또는 공백 문자열 결합 20.

**(3)**
```abap
CLASS lcl_won DEFINITION.
  PUBLIC SECTION.
    TYPES ty_amount TYPE p LENGTH 16 DECIMALS 0.
    CLASS-METHODS to_korean IMPORTING iv_amount TYPE ty_amount
                            RETURNING VALUE(rv) TYPE string.
ENDCLASS.

CLASS lcl_won IMPLEMENTATION.
  METHOD to_korean.
    CONSTANTS c_digits TYPE string VALUE `영일이삼사오육칠팔구`.
    DATA(lt_small) = VALUE string_table( ( `` ) ( `십` ) ( `백` ) ( `천` ) ).
    DATA(lt_big)   = VALUE string_table( ( `` ) ( `만` ) ( `억` ) ( `조` ) ).

    IF iv_amount <= 0.
      rv = `영원`.
      RETURN.
    ENDIF.

    DATA(lv_num) = |{ iv_amount }|.           " 예: '12345'
    DATA(lv_len) = strlen( lv_num ).
    DATA(lv_has) = abap_false.                " 현재 4자리 묶음에 0 아닌 숫자가 있었나

    DO lv_len TIMES.
      DATA(lv_off)   = sy-index - 1.          " 왼쪽부터 위치
      DATA(lv_place) = lv_len - sy-index.     " 오른쪽에서 몇 번째 자리(0부터)
      DATA(lv_d)     = CONV i( lv_num+lv_off(1) ).

      IF lv_d > 0.
        rv = rv && substring( val = c_digits off = lv_d len = 1 )
                && lt_small[ lv_place MOD 4 + 1 ].
        lv_has = abap_true.
      ENDIF.

      IF lv_place MOD 4 = 0.                  " 묶음의 끝(일·만·억·조 자리)
        IF lv_has = abap_true.
          rv = rv && lt_big[ lv_place DIV 4 + 1 ].
        ENDIF.
        lv_has = abap_false.
      ENDIF.
    ENDDO.

    rv = rv && `원`.
  ENDMETHOD.
ENDCLASS.

START-OF-SELECTION.
  DATA(lt_test) = VALUE string_table( ( lcl_won=>to_korean( 12345 ) )
                                      ( lcl_won=>to_korean( 100000000 ) )
                                      ( lcl_won=>to_korean( 1010 ) )
                                      ( lcl_won=>to_korean( 2000500 ) )
                                      ( lcl_won=>to_korean( 0 ) ) ).
  LOOP AT lt_test INTO DATA(lv_t).
    WRITE / lv_t.
  ENDLOOP.
```
- 핵심은 "자릿값 = 오른쪽에서 몇 번째인가": `place MOD 4`가 십·백·천, `place DIV 4`가 만·억·조를 정한다.
- 유니코드 시스템에서 한글 한 글자는 문자 하나라 `substring( ... len = 1 )`로 꺼낼 수 있다.
- 채점(100점): 숫자·작은 단위·큰 단위 매핑 15 / 자리 위치 계산(왼쪽 오프셋 ↔ 오른쪽 자릿값) 20 / 0 자리 생략 15 / 묶음 끝에서 큰 단위, 묶음 전체 0이면 생략 25 / 0 처리·"원" 10 / 예시 4개 정확 15.

**(4)** lv_num = `2000500`, 길이 7.
- place 6: 2 → `이` + 작은 단위[6 MOD 4 = 2 → 백] = `이백`
- place 5, 4: 0 → 생략. place 4는 묶음 끝 → 묶음에 숫자가 있었으므로 `만` → `이백만`
- place 3: 0, place 2: 5 → `오백`, place 1·0: 0 → place 0 묶음 끝, 숫자 있었음 → 큰 단위 `''`
- 결과 `이백만오백원`
- 흔한 오답: `100000000`을 `일억만원`으로 출력. 만 자리 묶음(place 4~7)이 모두 0이면 `만`을 붙이지 않아야 한다(`lv_has` 플래그).
- "10은 십으로" 변형: `lv_d = 1 AND lv_place MOD 4 > 0`일 때 숫자를 생략한다. 금액 앞에 "금", 뒤에 "정"을 붙이는 수표 형식 변형도 자주 나온다.

</details>

---

## 출처

- SAP-samples ABAP cheat sheets: https://github.com/SAP-samples/abap-cheat-sheets
  - Internal tables: https://github.com/SAP-samples/abap-cheat-sheets/blob/main/01_Internal_Tables.md
  - ABAP SQL: https://github.com/SAP-samples/abap-cheat-sheets/blob/main/03_ABAP_SQL.md
  - Constructor expressions: https://github.com/SAP-samples/abap-cheat-sheets/blob/main/05_Constructor_Expressions.md
  - String processing: https://github.com/SAP-samples/abap-cheat-sheets/blob/main/07_String_Processing.md
  - Data types and data objects: https://github.com/SAP-samples/abap-cheat-sheets/blob/main/16_Data_Types_and_Objects.md
- SAP Certified Associate – Back-End Developer – ABAP Cloud (C_ABAPD): https://training.sap.com/certification/C_ABAPD_2309 , https://learning.sap.com/certifications/sap-certified-associate-back-end-developer-abap-cloud
- SAP Learning Journey "Acquire Core ABAP Skills": https://learning.sap.com/learning-journeys/acquire-core-abap-skills
- ABAP Keyword Documentation: https://help.sap.com/doc/abapdocu_latest_index_htm/latest/en-US/index.htm
- ABAP Keyword Documentation 7.52, AT - itab(control level processing): https://help.sap.com/doc/abapdocu_752_index_htm/7.52/en-US/abapat_itab.htm
- SAP ABAP 면접 질문 모음(Guru99): https://www.guru99.com/sap-abap-interview-questions.html
- Exercism ABAP 트랙(reverse-string, word-count, nth-prime, prime-factors, binary-search): https://github.com/exercism/abap
- Glassdoor ABAP 개발자 면접 질문("Do you know what Binary Search is?"): https://static.glassdoor.fr/Interview/sap-abap-developer-interview-questions-SRCH_KO0,18_IP84.htm
- Glassdoor – SAP ABAP Developer 면접 후기(레거시 ABAP 36문항·90분): https://static.glassdoor.com.br/Interview/SAP-ABAP-Developer-Interview-Questions-EI_IE10471.0,3_KO4,18.htm
- Glassdoor – SAP "SAP ABAP Developer" 후기(대용량 SELECT 등): https://static-pc.glassdoor.de/Interview/SAP-SAP-ABAP-Developer-Interview-Questions-EI_IE10471.0,3_KO4,22.htm
