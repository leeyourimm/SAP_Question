## 1. 관리형(Managed) BO와 Draft

### R-02. 행동 전부 구현하기: 결정·검증·액션·함수·사이드 이펙트·Draft [작성] ★★★
<!-- covers: 메시지 클래스, 예외 클래스, IF_ABAP_BEHV_MESSAGE, IF_T100_DYN_MSG, severity, state message, %state_area, %element, %path, 정적 필드 제어, readonly, readonly:update, mandatory, mandatory:create, suppress, strict(2), determination on modify, determination on save, 트리거 조건, internal action, validation, draft determine action Prepare, instance action, result $self, action parameter, abstract entity, default function, GetDefaultsForCreate, repeatable action, factory action, %cid, %cid_ref, mapped, static default factory action, instance function, static function, FOR READ, determine action, side effects, affects messages, affects permissions, use side effects, dynamic feature control, Edit features instance, Activate optimized, Discard, Resume with additional implementation, total etag, @UI.lineItem FOR_ACTION, @UI.identification, invocationGrouping, @Consumption.valueHelpDefinition, @EndUserText.label, projection BDEF use action, use function -->
**목표**

1. RAP 메시지를 예외 클래스(`ZCM_RAP_###`)로 만들고, 오류·경고·성공 메시지를 상황에 맞는 severity로 돌려줄 수 있습니다.
2. 정적 필드 제어, on modify/on save 결정, 검증(state message)을 직접 정의·구현하고 Draft의 `Prepare`에 연결할 수 있습니다.
3. 인스턴스 액션, 파라미터 액션(+기본값 함수), 반복 가능 액션, 내부 액션, 인스턴스/정적 팩토리 액션, 인스턴스/정적 함수를 모두 만들고 핸들러 시그니처가 BDEF 어느 줄에서 생기는지 설명할 수 있습니다.
4. determine action과 사이드 이펙트(field / permissions / messages)로 Fiori 화면을 즉시 갱신시킬 수 있습니다.
5. Draft 액션(Edit·Activate·Discard·Resume·Prepare)의 동작과 `Resume with additional implementation`, total etag를 설명하고 구현할 수 있습니다.
6. 프로젝션 BDEF와 메타데이터 확장(MDE)으로 모든 액션을 Fiori 앱에 노출하고 직접 눌러 확인할 수 있습니다.

**전제**

- R-01을 끝내 Travel/Booking 관리형 Draft BO가 활성화되어 있고, Fiori Preview(`ZRAP_UI_TRAVEL_O4_###`)에서 Travel을 만들고 Booking을 추가할 수 있어야 합니다.
- 표준 데모 객체: `/DMO/CUSTOMER`, `/DMO/AGENCY`, `/DMO/FLIGHT` 테이블, `/DMO/I_Customer_StdVH`, `/DMO/I_Agency_StdVH`, `/DMO/I_Flight_StdVH` 값 도움말 뷰, `/DMO/CL_FLIGHT_AMDP`(통화 환산). BTP 트라이얼에는 Flight Reference Scenario(/DMO)가 기본 설치되어 있습니다.

**R-01에서 만든 것** R-01에서는 테이블 `ZRAP_ATRAV_###`/`ZRAP_ABOOK_###`와 draft 테이블 `ZRAP_DTRAV_###`/`ZRAP_DBOOK_###`(late numbering 때문에 `DRAFTUUID`/`PARENTDRAFTUUID` 포함), 루트 뷰 `ZRAP_R_TRAVEL_###`와 자식 `ZRAP_R_BOOKING_###`, 관리형 BDEF(`managed implementation in class ZBP_RAP_R_TRAVEL_### unique; strict ( 2 ); with draft;`, `late numbering`, `lock master total etag LastChangedAt`, `etag master LocalLastChangedAt`, `authorization master ( global )`, create/update/delete, `association _Booking { create; with draft; }`, Draft 액션 다섯 개(Prepare는 비어 있음)), 행동 풀 `ZBP_RAP_R_TRAVEL_###`(핸들러 `lhc_travel`의 `get_global_authorizations`, 세이버 `lsc_zrap_r_travel_###`의 `adjust_numbers`), 프로젝션 뷰 `ZRAP_C_TRAVEL_###`/`ZRAP_C_BOOKING_###`(AgencyName, CustomerName, OverallStatusText, 가상 요소 OverallStatusCriticality 포함), 프로젝션 BDEF, MDE, 서비스 정의·바인딩을 만들었습니다. 이 문제에서는 그 BO에 "행동"을 전부 붙입니다. Booking 엔터티에는 아직 구현 클래스가 없으므로 이 문제에서 `implementation in class ZBP_RAP_R_BOOKING_### unique`를 추가합니다.

**만들 객체**

| 순서 | 객체 유형 | 이름 | 역할 |
|---|---|---|---|
| 1 | 메시지 클래스 | `ZRAP_MSG_###` | 이 BO(및 이후 문제)가 쓰는 메시지 텍스트 |
| 2 | ABAP 클래스(예외) | `ZCM_RAP_###` | RAP 메시지 객체(`%msg`)를 만드는 예외 클래스 |
| 3 | 행동 정의(수정) | `ZRAP_R_TRAVEL_###` | 필드 제어·결정·검증·액션·함수·사이드 이펙트·Draft 액션 |
| 4 | 행동 풀(수정) | `ZBP_RAP_R_TRAVEL_###` | Travel 핸들러 `lhc_travel` + 세이버 `lsc_zrap_r_travel_###` |
| 5 | 행동 풀(신규) | `ZBP_RAP_R_BOOKING_###` | Booking 핸들러 `lhc_booking` |
| 6 | 추상 엔터티 | `ZRAP_A_DISCOUNT_###` | `deductDiscount` 액션 입력 파라미터 |
| 7 | 추상 엔터티 | `ZRAP_A_CREATE_TRAVEL_###` | `createTravel` 정적 팩토리 액션 입력 파라미터 |
| 8 | 추상 엔터티 | `ZRAP_A_DAYS_TO_FLIGHT_###` | `getDaysToFlight` 함수 결과 |
| 9 | 추상 엔터티 | `ZRAP_A_TRAVEL_STAT_###` | `getOpenTravelCount` 정적 함수 결과 |
| 10 | 행동 정의(수정) | `ZRAP_C_TRAVEL_###` | 프로젝션 BDEF: `use action` / `use function` / `use side effects` |
| 11 | 메타데이터 확장(수정) | `ZRAP_C_TRAVEL_###` | 액션 버튼(`#FOR_ACTION`) |
| 12 | ABAP 클래스(콘솔) | `ZCL_RAP_R02_CHECK_###` | 함수·반복 액션을 EML로 확인 |

> 진행 방법: 각 단계마다 BDEF에 줄을 추가하면 ADT가 "구현 메서드가 없다"는 경고/오류를 냅니다. BDEF에서 새 이름에 커서를 두고 **Ctrl+1 → Add missing method(s)** 를 쓰면 핸들러 선언과 빈 메서드가 생성됩니다. 생성된 선언(F2로 시그니처 확인)을 보면서 정답 코드와 비교하세요. 12단계에 최종 BDEF와 두 행동 풀의 **전체 코드**가 있습니다.

#### 1단계. 메시지 클래스 ZRAP_MSG_###와 예외 클래스 ZCM_RAP_### 만들기

요구사항

1. 패키지 `ZRAP_###`에 메시지 클래스 `ZRAP_MSG_###`(설명: "RAP Travel messages")를 만들고 아래 메시지를 등록하세요(텍스트는 영어로, `&1`~`&3`은 자리표시자).

| 번호 | 텍스트 | 쓰는 곳 | severity |
|---|---|---|---|
| 001 | Enter a customer ID. | validateCustomer | 오류 |
| 002 | Customer &1 does not exist. | validateCustomer | 오류 |
| 003 | Enter an agency ID. | validateAgency | 오류 |
| 004 | Agency &1 does not exist. | validateAgency | 오류 |
| 005 | Begin date &1 must not be after end date &2. | validateDates | 오류 |
| 006 | Begin date &1 must be on or after today. | validateDates | 오류 |
| 007 | Enter a begin date and an end date. | validateDates | 오류 |
| 008 | Enter a discount between 1 and 100 percent. | deductDiscount | 오류 |
| 009 | Travel &1 has been accepted. | acceptTravel | 성공 |
| 010 | Travel &1 has been rejected. | rejectTravel | 성공 |
| 011 | Enter airline, connection and flight date. | Booking validateConnection | 오류 |
| 012 | Flight &1 &2 on &3 does not exist. | Booking validateConnection | 오류 |
| 013 | Booking status &1 is not valid. | Booking validateStatus | 오류 |
| 014 | Flight date &1 is outside the travel period. | Booking validateConnection | 경고 |
| 015 | Travel &1 was accepted in the meantime. Discard your draft. | Resume | 오류 |

2. 예외 클래스 `ZCM_RAP_###`을 만드세요.
   - `CX_STATIC_CHECK` 상속, `FINAL`, `CREATE PUBLIC`.
   - 인터페이스 `IF_T100_MESSAGE`, `IF_T100_DYN_MSG`, `IF_ABAP_BEHV_MESSAGE` 구현.
   - 메시지마다 상수 구조(`msgid`, `msgno`, `attr1`~`attr4`) 하나: 이름은 `enter_customer_id`, `customer_unknown`, `enter_agency_id`, `agency_unknown`, `begin_date_after_end_date`, `begin_date_in_past`, `enter_dates`, `discount_invalid`, `travel_accepted`, `travel_rejected`, `enter_flight`, `flight_unknown`, `booking_status_invalid`, `flight_outside_travel`, `travel_accepted_meanwhile`.
   - 자리표시자용 공개 속성: `mv_travel_id`, `mv_booking_id`, `mv_customer_id`, `mv_agency_id`, `mv_begin_date`, `mv_end_date`, `mv_carrier_id`, `mv_connection_id`, `mv_flight_date`, `mv_status`. 상수의 `attr1`~`attr4`에 이 속성 이름(대문자)을 적어 `&1`~`&4`와 연결합니다.
   - 생성자 파라미터: `textid`, `severity`, `previous`, 그리고 위 속성과 같은 이름의 값들(`travel_id` 등). 모두 OPTIONAL. `severity`를 넘기지 않으면 오류(`E`)로 처리합니다.
3. 이후 R-03, R-04 등 다른 문제도 이 클래스를 확장해 씁니다(030번 이후 번호 사용).

**확인**

- 메시지 클래스 편집기에서 15개 메시지가 보이고, 클래스 `ZCM_RAP_###`이 오류 없이 활성화됩니다.
- 아직 BO에서 쓰지 않으므로 화면 변화는 없습니다. 4단계 이후 Fiori 메시지 팝오버에 이 텍스트가 나타납니다.

<details><summary>정답·해설</summary>

메시지 클래스는 ADT에서 **New → Other ABAP Repository Object → Texts → Message Class** 로 만들고, 편집기 표에 번호와 텍스트를 입력한 뒤 저장합니다(메시지 클래스는 활성화 대상이 아니라 저장만 합니다).

예외 클래스 전체 코드 (`ZCM_RAP_###`, 공식 예제 `/DMO/CM_FLIGHT_MESSAGES`와 같은 구조):

```abap
CLASS zcm_rap_### DEFINITION
  PUBLIC
  INHERITING FROM cx_static_check   " 정적 예외: 메시지 '그릇'으로만 쓰고 RAISE 하지 않음
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_t100_message.      " T100 메시지(메시지 클래스+번호)를 가리키는 t100key
    INTERFACES if_t100_dyn_msg.      " 속성 → &1~&4 치환, msgty 지원
    INTERFACES if_abap_behv_message. " RAP 메시지: m_severity 속성 제공 → %msg에 넣을 수 있음

    CONSTANTS:
      gc_msgid TYPE symsgid VALUE 'ZRAP_MSG_###',

      BEGIN OF enter_customer_id,
        msgid TYPE symsgid VALUE 'ZRAP_MSG_###',
        msgno TYPE symsgno VALUE '001',
        attr1 TYPE scx_attrname VALUE '',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF enter_customer_id,

      BEGIN OF customer_unknown,
        msgid TYPE symsgid VALUE 'ZRAP_MSG_###',
        msgno TYPE symsgno VALUE '002',
        attr1 TYPE scx_attrname VALUE 'MV_CUSTOMER_ID',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF customer_unknown,

      BEGIN OF enter_agency_id,
        msgid TYPE symsgid VALUE 'ZRAP_MSG_###',
        msgno TYPE symsgno VALUE '003',
        attr1 TYPE scx_attrname VALUE '',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF enter_agency_id,

      BEGIN OF agency_unknown,
        msgid TYPE symsgid VALUE 'ZRAP_MSG_###',
        msgno TYPE symsgno VALUE '004',
        attr1 TYPE scx_attrname VALUE 'MV_AGENCY_ID',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF agency_unknown,

      BEGIN OF begin_date_after_end_date,
        msgid TYPE symsgid VALUE 'ZRAP_MSG_###',
        msgno TYPE symsgno VALUE '005',
        attr1 TYPE scx_attrname VALUE 'MV_BEGIN_DATE',
        attr2 TYPE scx_attrname VALUE 'MV_END_DATE',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF begin_date_after_end_date,

      BEGIN OF begin_date_in_past,
        msgid TYPE symsgid VALUE 'ZRAP_MSG_###',
        msgno TYPE symsgno VALUE '006',
        attr1 TYPE scx_attrname VALUE 'MV_BEGIN_DATE',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF begin_date_in_past,

      BEGIN OF enter_dates,
        msgid TYPE symsgid VALUE 'ZRAP_MSG_###',
        msgno TYPE symsgno VALUE '007',
        attr1 TYPE scx_attrname VALUE '',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF enter_dates,

      BEGIN OF discount_invalid,
        msgid TYPE symsgid VALUE 'ZRAP_MSG_###',
        msgno TYPE symsgno VALUE '008',
        attr1 TYPE scx_attrname VALUE '',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF discount_invalid,

      BEGIN OF travel_accepted,
        msgid TYPE symsgid VALUE 'ZRAP_MSG_###',
        msgno TYPE symsgno VALUE '009',
        attr1 TYPE scx_attrname VALUE 'MV_TRAVEL_ID',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF travel_accepted,

      BEGIN OF travel_rejected,
        msgid TYPE symsgid VALUE 'ZRAP_MSG_###',
        msgno TYPE symsgno VALUE '010',
        attr1 TYPE scx_attrname VALUE 'MV_TRAVEL_ID',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF travel_rejected,

      BEGIN OF enter_flight,
        msgid TYPE symsgid VALUE 'ZRAP_MSG_###',
        msgno TYPE symsgno VALUE '011',
        attr1 TYPE scx_attrname VALUE '',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF enter_flight,

      BEGIN OF flight_unknown,
        msgid TYPE symsgid VALUE 'ZRAP_MSG_###',
        msgno TYPE symsgno VALUE '012',
        attr1 TYPE scx_attrname VALUE 'MV_CARRIER_ID',
        attr2 TYPE scx_attrname VALUE 'MV_CONNECTION_ID',
        attr3 TYPE scx_attrname VALUE 'MV_FLIGHT_DATE',
        attr4 TYPE scx_attrname VALUE '',
      END OF flight_unknown,

      BEGIN OF booking_status_invalid,
        msgid TYPE symsgid VALUE 'ZRAP_MSG_###',
        msgno TYPE symsgno VALUE '013',
        attr1 TYPE scx_attrname VALUE 'MV_STATUS',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF booking_status_invalid,

      BEGIN OF flight_outside_travel,
        msgid TYPE symsgid VALUE 'ZRAP_MSG_###',
        msgno TYPE symsgno VALUE '014',
        attr1 TYPE scx_attrname VALUE 'MV_FLIGHT_DATE',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF flight_outside_travel,

      BEGIN OF travel_accepted_meanwhile,
        msgid TYPE symsgid VALUE 'ZRAP_MSG_###',
        msgno TYPE symsgno VALUE '015',
        attr1 TYPE scx_attrname VALUE 'MV_TRAVEL_ID',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF travel_accepted_meanwhile.

    METHODS constructor
      IMPORTING
        textid        LIKE if_t100_message=>t100key OPTIONAL
        severity      TYPE if_abap_behv_message=>t_severity OPTIONAL
        previous      LIKE previous OPTIONAL
        travel_id     TYPE /dmo/travel_id OPTIONAL
        booking_id    TYPE /dmo/booking_id OPTIONAL
        customer_id   TYPE /dmo/customer_id OPTIONAL
        agency_id     TYPE /dmo/agency_id OPTIONAL
        begin_date    TYPE /dmo/begin_date OPTIONAL
        end_date      TYPE /dmo/end_date OPTIONAL
        carrier_id    TYPE /dmo/carrier_id OPTIONAL
        connection_id TYPE /dmo/connection_id OPTIONAL
        flight_date   TYPE /dmo/flight_date OPTIONAL
        status        TYPE /dmo/booking_status OPTIONAL.

    " &1~&4 자리에 들어갈 값. 상수의 attr1~attr4가 이 이름을 가리킴
    DATA mv_travel_id     TYPE /dmo/travel_id READ-ONLY.
    DATA mv_booking_id    TYPE /dmo/booking_id READ-ONLY.
    DATA mv_customer_id   TYPE /dmo/customer_id READ-ONLY.
    DATA mv_agency_id     TYPE /dmo/agency_id READ-ONLY.
    DATA mv_begin_date    TYPE /dmo/begin_date READ-ONLY.
    DATA mv_end_date      TYPE /dmo/end_date READ-ONLY.
    DATA mv_carrier_id    TYPE /dmo/carrier_id READ-ONLY.
    DATA mv_connection_id TYPE /dmo/connection_id READ-ONLY.
    DATA mv_flight_date   TYPE /dmo/flight_date READ-ONLY.
    DATA mv_status        TYPE /dmo/booking_status READ-ONLY.

  PROTECTED SECTION.
  PRIVATE SECTION.
ENDCLASS.


CLASS zcm_rap_### IMPLEMENTATION.

  METHOD constructor ##ADT_SUPPRESS_GENERATION.
    super->constructor( previous = previous ).

    mv_travel_id     = travel_id.
    mv_booking_id    = booking_id.
    mv_customer_id   = customer_id.
    mv_agency_id     = agency_id.
    mv_begin_date    = begin_date.
    mv_end_date      = end_date.
    mv_carrier_id    = carrier_id.
    mv_connection_id = connection_id.
    mv_flight_date   = flight_date.
    mv_status        = status.

    " severity를 안 넘기면 오류로 취급
    if_abap_behv_message~m_severity = COND #( WHEN severity IS INITIAL
                                              THEN if_abap_behv_message=>severity-error
                                              ELSE severity ).

    CLEAR me->textid.
    IF textid IS INITIAL.
      if_t100_message~t100key = if_t100_message=>default_textid.
    ELSE.
      if_t100_message~t100key = textid.
    ENDIF.
  ENDMETHOD.

ENDCLASS.
```

쓰는 법(4단계 이후 반복해서 나옵니다):

```abap
APPEND VALUE #( %tky        = travel-%tky
                %state_area = 'VALIDATE_CUSTOMER'
                %msg        = NEW zcm_rap_###( textid      = zcm_rap_###=>customer_unknown
                                               customer_id = travel-CustomerID
                                               severity    = if_abap_behv_message=>severity-error )
                %element-CustomerID = if_abap_behv=>mk-on ) TO reported-travel.
```

**왜 예외 클래스인가**

- RAP 응답 파라미터 `reported`의 `%msg` 컴포넌트 타입은 `REF TO if_abap_behv_message`입니다. 즉 "메시지"는 문자열이 아니라 **이 인터페이스를 구현한 객체**여야 합니다. 이 인터페이스는 `IF_T100_DYN_MSG`(→ `IF_T100_MESSAGE`)를 포함하고 있어, 메시지 클래스·번호·자리표시자 값과 severity를 한 객체에 담습니다.
- 표준 클래스 `CX_STATIC_CHECK`를 상속하는 이유는 T100 예외 텍스트 메커니즘(`textid`, `attr1~4` → 속성 값 치환)을 그대로 쓰기 위해서입니다. 이 객체는 `RAISE` 하지 않고 `NEW`로 만들어 `%msg`에 넣기만 합니다.
- 메시지 텍스트가 메시지 클래스에 있으므로 번역(로그온 언어별 텍스트)이 자동으로 됩니다. 문자열을 하드코딩한 `new_message_with_text( )`(핸들러의 상속 메서드)보다 운영 품질이 좋습니다.
- 공식 예제에서는 `IF_T100_MESSAGE`를 따로 적지 않아도 `IF_T100_DYN_MSG`에 포함되어 있지만, `/DMO/CM_FLIGHT_MESSAGES`처럼 명시해도 문제없습니다.

**severity 정리** (`if_abap_behv_message=>severity-…`)

| 값 | 의미 | Fiori에서 | `failed`와 함께? |
|---|---|---|---|
| `error` | 저장(활성화)을 막는 오류 | 빨간 아이콘, 필드 강조 | 예: 검증에서 오류면 `failed`에도 키 추가 |
| `warning` | 저장은 되지만 주의 | 노란 아이콘 | 아니요 (`failed`에 넣지 않음) |
| `information` | 정보 | 파란 아이콘 | 아니요 |
| `success` | 작업 성공 알림 (액션 뒤 토스트) | 성공 메시지 토스트 | 아니요 |
| `none` | 심각도 없음 | | |

**자주 나는 오류와 해결**

- 메시지 텍스트가 "&1"처럼 치환되지 않고 나옴 → 상수의 `attr1` 값이 속성 이름과 다르거나 소문자로 적은 경우입니다. 속성 이름을 **대문자**(`'MV_CUSTOMER_ID'`)로 적으세요.
- 메시지가 아예 안 뜸 → `msgid`를 메시지 클래스 이름과 다르게 적었는지 확인하세요(### 치환 누락이 흔합니다).

</details>

#### 2단계. 정적 필드 제어와 strict(2) 규칙

요구사항

1. Travel(`ZRAP_R_TRAVEL_###`)
   - `TravelID`(late numbering), `TotalPrice`(계산값), `OverallStatus`(액션으로만 변경), 관리 필드 5개(`CreatedBy`, `CreatedAt`, `LocalLastChangedBy`, `LocalLastChangedAt`, `LastChangedAt`)는 **항상 읽기 전용**.
   - `CustomerID`, `BeginDate`, `EndDate`, `CurrencyCode`는 **필수**.
   - `AgencyID`는 **만들 때는 필수, 만든 뒤에는 변경 불가**.
2. Booking(`ZRAP_R_BOOKING_###`)
   - `TravelID`, `BookingID`, `BookingDate`(결정으로 채움), `LocalLastChangedAt`은 읽기 전용.
   - `CustomerID`, `CarrierID`, `ConnectionID`, `FlightDate`는 필수.
   - Booking 헤더에 `implementation in class zbp_rap_r_booking_### unique`를 추가하고, 행동 풀 `ZBP_RAP_R_BOOKING_###`을 만드세요(아직 빈 클래스).
3. `suppress`는 쓰지 말고, 이 BO의 어떤 필드에 쓰면 어떤 일이 생기는지 설명만 적으세요.
4. `strict ( 2 )`가 이 BDEF에 요구하는 것을 세 가지 이상 적으세요.

**확인**

- BDEF 활성화 성공.
- Fiori Preview에서 새 Travel을 만들면 Customer, Begin Date, End Date, Currency, Agency 라벨 옆에 `*`(필수 표시)가 보이고, Total Price·Status 필드는 입력할 수 없습니다.
- 기존 Travel을 **Edit** 하면 Agency 필드가 읽기 전용으로 바뀝니다.

<details><summary>정답·해설</summary>

Travel 정의 블록 안(기존 `create; update; delete;` 아래)에 추가:

```bdef
  // ── 정적 필드 제어 ──
  // readonly: 소비자(UI, EML 외부 호출)는 절대 값을 넣을 수 없음. IN LOCAL MODE(행동 풀 안)에서는 변경 가능
  field ( readonly ) TravelID, TotalPrice, OverallStatus,
                     CreatedBy, CreatedAt, LocalLastChangedBy, LocalLastChangedAt, LastChangedAt;
  // mandatory: 저장 전에 값이 있어야 함 → UI에 * 표시
  field ( mandatory ) CustomerID, BeginDate, EndDate, CurrencyCode;
  // mandatory : create → 생성 시 필수 / readonly : update → 생성 후엔 변경 불가
  field ( mandatory : create, readonly : update ) AgencyID;
```

Booking 헤더와 필드 제어:

```bdef
define behavior for ZRAP_R_BOOKING_### alias Booking
implementation in class zbp_rap_r_booking_### unique   // ← 추가: Booking 전용 행동 풀
persistent table zrap_abook_###
draft table zrap_dbook_###
etag master LocalLastChangedAt
lock dependent by _Travel
authorization dependent by _Travel
late numbering
{
  update;
  delete;
  association _Travel { with draft; }

  field ( readonly ) TravelID, BookingID, BookingDate, LocalLastChangedAt;
  field ( mandatory ) CustomerID, CarrierID, ConnectionID, FlightDate;
  // (mapping은 R-01 그대로)
```

Booking 행동 풀(글로벌 클래스 부분, 처음엔 로컬 타입 탭이 비어 있음):

```abap
CLASS zbp_rap_r_booking_### DEFINITION
  PUBLIC
  ABSTRACT
  FINAL
  FOR BEHAVIOR OF zrap_r_travel_###.   " 루트 BDEF 이름을 적음 (Booking 이름이 아님)
ENDCLASS.

CLASS zbp_rap_r_booking_### IMPLEMENTATION.
ENDCLASS.
```

BDEF에서 `zbp_rap_r_booking_###`에 커서를 두고 Ctrl+1 → **Create behavior implementation class** 를 쓰면 위 골격이 생깁니다.

**필드 특성 정리**

| 특성 | 의미 | 이 BO에서 |
|---|---|---|
| `readonly` | 소비자가 create/update 모두 못 넣음. 행동 풀의 `IN LOCAL MODE` EML은 바꿀 수 있음 | 키, 계산값, 상태, 관리 필드 |
| `readonly : update` | 생성 때만 입력, 이후 변경 불가 | AgencyID |
| `readonly : create` | 생성 때는 못 넣고, 이후엔 변경 가능 | (사용 안 함) |
| `mandatory` | 값 필수 → Fiori `*`. 백엔드 일관성은 검증으로도 보장해야 함 | 고객, 날짜, 통화 |
| `mandatory : create` | 생성 시에만 필수 | AgencyID |
| `suppress` | 필드를 BDEF 파생 타입과 모든 RAP API에서 **제거** | 쓰지 않음 |
| `features : instance` | 인스턴스 상태에 따라 동적으로 결정 (R-03) | |

- `suppress` 예: `field ( suppress ) Attachment;`라고 쓰면 `Attachment`는 EML 타입(`TABLE FOR CREATE` 등)에 아예 없어져 EML로 읽거나 쓸 수 없고 OData에도 나오지 않습니다. 첨부 파일 기능(R-11 등)이 깨지므로 이 BO에는 맞지 않습니다. 기술 필드를 API에서 완전히 숨길 때 씁니다.
- `readonly` 필드라도 행동 풀에서 `MODIFY ENTITIES ... IN LOCAL MODE`로는 변경할 수 있습니다. 3단계 결정이 `OverallStatus`, `TotalPrice`를 채울 수 있는 이유입니다.
- `mandatory`는 Fiori가 필수 표시와 프런트 검사를 하게 만듭니다. EML 같은 다른 경로로 들어오는 데이터까지 막으려면 4단계처럼 검증을 반드시 함께 둡니다(RAP110 ex03 설명: "backend validations are a MUST").

**strict ( 2 )가 요구하는 것 (대표적인 예)**

- 권한 제어 선언 필수: 루트에 `authorization master ( ... )`, 자식에 `authorization dependent by ...`.
- Draft BO는 Draft 액션(`Edit`, `Activate`, `Discard`, `Resume`, `Prepare`)을 **명시적으로** 선언해야 하고, `total etag`가 있어야 합니다.
- 이전 버전에서 경고였던 것(예: 매핑되지 않은 필드, 쓰이지 않는 선언)이 오류로 바뀌고, 폐기 예정 문법을 쓸 수 없습니다.
- strict(2)는 strict(1)의 규칙을 모두 포함하고 더 엄격합니다. 정확한 규칙 목록은 ADT에서 `strict`에 커서를 두고 F1(ABAP 키워드 문서)로 확인하세요. 위 목록 외 세부 규칙은 (실제 시스템에서 확인 필요).

**클래스 구조 해설** 이 단계는 행동 풀 메서드를 만들지 않습니다. 정적 필드 제어는 프레임워크가 요청을 받을 때 스스로 검사합니다(소비자가 readonly 필드를 보내면 프레임워크가 거부). 반면 `implementation in class` 줄은 "이 엔터티의 핸들러는 이 클래스의 로컬 클래스에 있다"는 연결이며, 이후 Booking에 결정·검증·함수를 추가하면 그 메서드는 `ZBP_RAP_R_BOOKING_###`의 `lhc_booking`에 둡니다.

**자주 나는 오류와 해결**

- `readonly`와 `mandatory`를 같은 필드에 동시에 주면 모순이라 활성화 오류가 납니다. `mandatory : create, readonly : update`처럼 작업별로 나눠야 합니다.
- Booking에 `implementation in class`를 추가했는데 클래스가 없으면 BDEF 활성화가 실패합니다. 위처럼 클래스를 먼저 만드세요.

</details>

#### 3단계. 결정(Determination): on modify, on save, 내부 액션으로 총액 계산

요구사항

1. Travel
   - `setInitialValues` **on modify { create; }**: 비어 있으면 `OverallStatus = 'O'`, `BeginDate = 오늘+1`, `EndDate = 오늘+15`, `CurrencyCode = 'EUR'`. 이미 값이 있는 필드는 덮어쓰지 않습니다.
   - `calculateTotalPrice` **on modify { create; field BookingFee, CurrencyCode; }**: 직접 계산하지 말고 내부 액션 `reCalcTotalPrice`를 실행합니다.
   - `internal action reCalcTotalPrice`: `TotalPrice = BookingFee + 모든 Booking의 FlightPrice`. 통화가 다르면 `/DMO/CL_FLIGHT_AMDP=>CONVERT_CURRENCY`로 Travel 통화로 환산합니다.
   - `setDefaultDescription` **on save { create; }**: 설명이 비어 있으면 `Trip of customer <고객번호> from <시작일>`을 넣습니다.
2. Booking
   - `setInitialBookingValues` **on modify { create; }**: 비어 있으면 `BookingDate = 오늘`, `CustomerID = 부모 Travel의 CustomerID`, `BookingStatus = 'N'`.
   - `calculateTotalPrice` **on modify { create; field FlightPrice, CurrencyCode; }**: 부모 Travel의 `reCalcTotalPrice`를 실행합니다.
3. 'O', 'A', 'X', 'N', 'EUR' 같은 고정값은 코드에 바로 쓰지 말고 `lhc_travel`의 **PRIVATE SECTION 맨 위에 상수(CONSTANTS)로 먼저 선언**하세요. 상태 묶음 `travel_status`(open/accepted/rejected), `booking_status`(new), `c_default_currency`, `c_service_fee`를 둡니다. 3단계 이후 단계들도 이 상수를 씁니다. Booking 핸들러(`lhc_booking`)에서도 쓰려면 그 클래스에도 따로 선언하세요.
4. 모든 read는 `IN LOCAL MODE` + `FIELDS ( … )`, 변경은 `%control` 또는 `UPDATE FIELDS ( … )`로 바뀐 필드만 표시하세요.
5. 트리거 조건 `{ create; update; delete; field … }`의 차이와 결정 실행 순서에 대해 해설에 적으세요.

**확인**

- Fiori에서 **Create**(2단계 이후 7단계 전까지는 표준 create 화면) → Status가 Open, 날짜·통화가 미리 채워짐.
- Booking Fee에 100 입력 후 다른 필드로 이동, 저장(Save) → Total Price 100. Booking을 추가해 Flight Price 500 입력 후 저장 → Total Price 600.
- Description을 비우고 저장 → 활성 Travel에 "Trip of customer …" 설명이 들어감.

<details><summary>정답·해설</summary>

BDEF 추가 (Travel):

```bdef
  // ── 결정 ──
  // on modify: 트랜잭션 버퍼가 바뀐 직후 실행 → 결과가 화면(draft)에 바로 보임
  determination setInitialValues on modify { create; }
  determination calculateTotalPrice on modify { create; field BookingFee, CurrencyCode; }
  // on save: 저장 순서(save sequence) 안에서 실행 (Draft에서는 Prepare/Activate 때)
  determination setDefaultDescription on save { create; }

  // ── 내부 액션: BO 안에서만 호출 가능 (OData/외부 EML에 노출되지 않음) ──
  internal action reCalcTotalPrice;
```

BDEF 추가 (Booking):

```bdef
  determination setInitialBookingValues on modify { create; }
  determination calculateTotalPrice on modify { create; field FlightPrice, CurrencyCode; }
```

`ZBP_RAP_R_TRAVEL_###` 로컬 타입의 `lhc_travel`에 선언 추가:

```abap
    METHODS setInitialValues FOR DETERMINE ON MODIFY
      IMPORTING keys FOR Travel~setInitialValues.

    METHODS calculateTotalPrice FOR DETERMINE ON MODIFY
      IMPORTING keys FOR Travel~calculateTotalPrice.

    METHODS setDefaultDescription FOR DETERMINE ON SAVE
      IMPORTING keys FOR Travel~setDefaultDescription.

    METHODS reCalcTotalPrice FOR MODIFY
      IMPORTING keys FOR ACTION Travel~reCalcTotalPrice.
```

상수(`lhc_travel` PRIVATE SECTION 맨 위, 12단계 전체 코드 참고):

```abap
    CONSTANTS:
      BEGIN OF travel_status,
        open     TYPE /dmo/overall_status VALUE 'O', "Open
        accepted TYPE /dmo/overall_status VALUE 'A', "Accepted
        rejected TYPE /dmo/overall_status VALUE 'X', "Rejected
      END OF travel_status,
      BEGIN OF booking_status,
        new TYPE /dmo/booking_status VALUE 'N', "New
      END OF booking_status,
      c_default_currency TYPE /dmo/currency_code VALUE 'EUR',
      c_service_fee      TYPE /dmo/booking_fee   VALUE '10.00',
      BEGIN OF state_area,
        customer TYPE string VALUE 'VALIDATE_CUSTOMER',
        agency   TYPE string VALUE 'VALIDATE_AGENCY',
        dates    TYPE string VALUE 'VALIDATE_DATES',
      END OF state_area.
```

구현 (`lhc_travel`):

```abap
  METHOD setInitialValues.
    " 방금 생성된 Travel들의 현재 값을 읽어 옴 (keys = 프레임워크가 넘겨준 '생성된 인스턴스 키 목록')
    " IN LOCAL MODE = 권한·기능 제어 검사 없이 BO 내부에서 읽기
    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        FIELDS ( BeginDate EndDate CurrencyCode OverallStatus )   " 이 4개 필드만 읽음
        WITH CORRESPONDING #( keys )                              " keys를 READ용 키 형식으로 변환
      RESULT DATA(travels).                                       " 읽은 결과가 travels 테이블에 담김

    " 4개 필드가 이미 다 채워진 Travel은 할 일이 없으니 목록에서 뺌
    " (팩토리 액션·EML로 값을 넣어서 만든 경우)
    DELETE travels WHERE BeginDate     IS NOT INITIAL
                     AND EndDate       IS NOT INITIAL
                     AND CurrencyCode  IS NOT INITIAL
                     AND OverallStatus IS NOT INITIAL.
    CHECK travels IS NOT INITIAL.          " 남은 게 없으면 메서드 종료

    DATA(today) = cl_abap_context_info=>get_system_date( ).   " 오늘 날짜 (클라우드에서는 sy-datum 대신 이걸 씀)
    DATA travels_upd TYPE TABLE FOR UPDATE zrap_r_travel_###\\Travel.   " UPDATE에 넘길 행을 모을 테이블 (BDEF 파생 타입)

    LOOP AT travels INTO DATA(travel).
      " 업데이트할 행 하나를 만들고 키(%tky)만 먼저 채움. <upd>로 그 행을 직접 가리킴
      APPEND VALUE #( %tky = travel-%tky ) TO travels_upd ASSIGNING FIELD-SYMBOL(<upd>).
      IF travel-BeginDate IS INITIAL.                         " 시작일이 비어 있으면
        <upd>-BeginDate          = today + 1.                 "   내일로 채우고
        <upd>-%control-BeginDate = if_abap_behv=>mk-on.       "   '이 필드를 바꾼다'고 표시 (표시 안 하면 무시됨)
      ENDIF.
      IF travel-EndDate IS INITIAL.                           " 종료일이 비어 있으면 15일 뒤로
        <upd>-EndDate          = today + 15.
        <upd>-%control-EndDate = if_abap_behv=>mk-on.
      ENDIF.
      IF travel-CurrencyCode IS INITIAL.                      " 통화가 비어 있으면 상수 'EUR'로
        <upd>-CurrencyCode          = c_default_currency.
        <upd>-%control-CurrencyCode = if_abap_behv=>mk-on.
      ENDIF.
      IF travel-OverallStatus IS INITIAL.                     " 상태가 비어 있으면 'O'(Open)로
        <upd>-OverallStatus          = travel_status-open.
        <upd>-%control-OverallStatus = if_abap_behv=>mk-on.
      ENDIF.
    ENDLOOP.

    " 모은 값을 BO에 실제로 반영. %control이 켜진 필드만 바뀌므로 사용자가 넣은 값은 안전함
    MODIFY ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        UPDATE FROM travels_upd.
  ENDMETHOD.

  METHOD calculateTotalPrice.
    " 계산은 여기서 하지 않고, 바뀐 Travel들에 대해 내부 액션 reCalcTotalPrice를 실행만 함
    " (Booking 쪽 결정도 같은 액션을 부르므로 계산 로직이 한 곳에만 있게 됨)
    MODIFY ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        EXECUTE reCalcTotalPrice             " 액션 실행
        FROM CORRESPONDING #( keys ).        " 대상 = 이 결정을 일으킨 Travel들
  ENDMETHOD.

  METHOD setDefaultDescription.
    " 저장 직전, 새 Travel들의 설명·고객번호·시작일을 읽음
    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        FIELDS ( Description CustomerID BeginDate )
        WITH CORRESPONDING #( keys )
      RESULT DATA(travels).

    DELETE travels WHERE Description IS NOT INITIAL.   " 사용자가 설명을 쓴 Travel은 제외
    CHECK travels IS NOT INITIAL.                      " 남은 게 없으면 종료

    " 남은 Travel마다 설명을 만들어 넣음. UPDATE FIELDS ( … )로 Description만 바꾼다고 지정
    MODIFY ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        UPDATE FIELDS ( Description )
        WITH VALUE #( FOR travel IN travels                 " travels 한 줄마다 업데이트 행 하나
                      ( %tky        = travel-%tky
                        " 예: 'Trip of customer 42 from 2026-10-18'
                        " ALPHA = OUT: 앞자리 0 제거, DATE = ISO: 날짜를 YYYY-MM-DD로
                        Description = |Trip of customer { travel-CustomerID ALPHA = OUT } from { travel-BeginDate DATE = ISO }| ) ).
  ENDMETHOD.

  METHOD reCalcTotalPrice.
    " 통화별 금액을 모을 작은 표 (금액, 통화)
    TYPES: BEGIN OF ty_amount_per_currency,
             amount        TYPE /dmo/total_price,
             currency_code TYPE /dmo/currency_code,
           END OF ty_amount_per_currency.
    DATA amounts_per_currency TYPE STANDARD TABLE OF ty_amount_per_currency.

    " 1) 대상 Travel들의 예약 수수료와 통화를 읽음
    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        FIELDS ( BookingFee CurrencyCode )
        WITH CORRESPONDING #( keys )
      RESULT DATA(travels).

    DELETE travels WHERE CurrencyCode IS INITIAL.   " 통화가 없으면 합계를 낼 기준이 없으니 제외
    CHECK travels IS NOT INITIAL.

    " 2) 그 Travel들에 딸린 Booking 전부의 항공권 가격과 통화를 읽음 (BY \_Booking = 연관 따라 자식 읽기)
    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel BY \_Booking
        FIELDS ( FlightPrice CurrencyCode )
        WITH CORRESPONDING #( travels )
      LINK DATA(booking_links)        " 어느 Travel(source)에 어느 Booking(target)이 붙어 있는지 짝 목록
      RESULT DATA(bookings).          " Booking 데이터 자체

    DATA(today) = cl_abap_context_info=>get_system_date( ).   " 환율 기준일

    LOOP AT travels ASSIGNING FIELD-SYMBOL(<travel>).          " Travel 하나씩 계산 (<travel>을 고치면 travels가 바로 바뀜)
      " 3) 먼저 예약 수수료를 Travel 통화로 넣어 둠
      amounts_per_currency = VALUE #( ( amount        = <travel>-BookingFee
                                        currency_code = <travel>-CurrencyCode ) ).

      " 4) 이 Travel에 붙은 Booking만 골라서 가격을 통화별로 더함
      LOOP AT booking_links INTO DATA(booking_link) USING KEY id WHERE source-%tky = <travel>-%tky.
        DATA(booking) = bookings[ KEY id %tky = booking_link-target-%tky ].   " 짝 목록의 target 키로 Booking 찾기
        " COLLECT: 같은 통화 줄이 있으면 금액을 더하고, 없으면 새 줄 추가
        COLLECT VALUE ty_amount_per_currency( amount        = booking-FlightPrice
                                              currency_code = booking-CurrencyCode ) INTO amounts_per_currency.
      ENDLOOP.

      DELETE amounts_per_currency WHERE currency_code IS INITIAL.   " 통화 없는 금액은 환산할 수 없으니 버림

      " 5) 통화별 금액을 Travel 통화로 맞춰 하나로 합침
      CLEAR <travel>-TotalPrice.                                     " 0부터 다시 계산
      LOOP AT amounts_per_currency INTO DATA(amount_per_currency).
        IF amount_per_currency-currency_code = <travel>-CurrencyCode.
          <travel>-TotalPrice += amount_per_currency-amount.         " 같은 통화면 그대로 더함
        ELSE.
          " 다른 통화면 SAP 데모 환율 함수로 Travel 통화로 바꾼 뒤 더함
          /dmo/cl_flight_amdp=>convert_currency(
            EXPORTING
              iv_amount               = amount_per_currency-amount        " 바꿀 금액
              iv_currency_code_source = amount_per_currency-currency_code " 원래 통화
              iv_currency_code_target = <travel>-CurrencyCode             " 바꿀 통화
              iv_exchange_rate_date   = today                             " 환율 기준일
            IMPORTING
              ev_amount               = DATA(converted_amount) ).         " 바뀐 금액
          <travel>-TotalPrice += converted_amount.
        ENDIF.
      ENDLOOP.
    ENDLOOP.

    " 6) 계산한 총액을 BO에 반영 (TotalPrice 필드만 바꿈)
    MODIFY ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        UPDATE FIELDS ( TotalPrice )
        WITH CORRESPONDING #( travels ).
  ENDMETHOD.
```

`ZBP_RAP_R_BOOKING_###` 로컬 타입(`lhc_booking`) — 선언과 상수:

```abap
CLASS lhc_booking DEFINITION INHERITING FROM cl_abap_behavior_handler.
  PRIVATE SECTION.
    CONSTANTS:
      BEGIN OF booking_status,
        new       TYPE /dmo/booking_status VALUE 'N', "New
        booked    TYPE /dmo/booking_status VALUE 'B', "Booked
        cancelled TYPE /dmo/booking_status VALUE 'X', "Cancelled
      END OF booking_status,
      BEGIN OF state_area,
        connection TYPE string VALUE 'VALIDATE_CONNECTION',
        status     TYPE string VALUE 'VALIDATE_STATUS',
      END OF state_area.

    METHODS setInitialBookingValues FOR DETERMINE ON MODIFY
      IMPORTING keys FOR Booking~setInitialBookingValues.

    METHODS calculateTotalPrice FOR DETERMINE ON MODIFY
      IMPORTING keys FOR Booking~calculateTotalPrice.
ENDCLASS.
```

구현 (`lhc_booking`):

```abap
  METHOD setInitialBookingValues.
    " 부모 Travel의 고객 번호 (같은 Travel의 Booking이 여러 개여도 Travel은 한 번만 옴)
    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Booking BY \_Travel
        FIELDS ( CustomerID )
        WITH CORRESPONDING #( keys )
      RESULT DATA(travels)
      LINK DATA(booking_to_travel).

    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Booking
        FIELDS ( CustomerID BookingDate BookingStatus )
        WITH CORRESPONDING #( keys )
      RESULT DATA(bookings).

    DELETE bookings WHERE CustomerID    IS NOT INITIAL
                      AND BookingDate   IS NOT INITIAL
                      AND BookingStatus IS NOT INITIAL.
    CHECK bookings IS NOT INITIAL.

    DATA(today) = cl_abap_context_info=>get_system_date( ).
    DATA bookings_upd TYPE TABLE FOR UPDATE zrap_r_travel_###\\Booking.

    LOOP AT bookings INTO DATA(booking).
      APPEND VALUE #( %tky = booking-%tky ) TO bookings_upd ASSIGNING FIELD-SYMBOL(<upd>).
      IF booking-CustomerID IS INITIAL.
        <upd>-CustomerID = VALUE #( travels[ KEY id %tky = booking_to_travel[ KEY id source-%tky = booking-%tky ]-target-%tky ]-CustomerID OPTIONAL ).
        <upd>-%control-CustomerID = if_abap_behv=>mk-on.
      ENDIF.
      IF booking-BookingDate IS INITIAL.
        <upd>-BookingDate          = today.
        <upd>-%control-BookingDate = if_abap_behv=>mk-on.
      ENDIF.
      IF booking-BookingStatus IS INITIAL.
        <upd>-BookingStatus          = booking_status-new.
        <upd>-%control-BookingStatus = if_abap_behv=>mk-on.
      ENDIF.
    ENDLOOP.

    MODIFY ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Booking
        UPDATE FROM bookings_upd.
  ENDMETHOD.

  METHOD calculateTotalPrice.
    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Booking BY \_Travel
        FIELDS ( TravelID )
        WITH CORRESPONDING #( keys )
      RESULT DATA(travels).

    MODIFY ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        EXECUTE reCalcTotalPrice
        FROM CORRESPONDING #( travels ).
  ENDMETHOD.
```

**왜 이렇게 쓰나**

- **on modify vs on save**: `on modify` 결정은 create/update가 버퍼에 들어간 즉시 돌아서 Fiori draft 화면에 바로 반영됩니다(기본값, 계산값). `on save` 결정은 저장 순서의 `finalize` 단계에서 돌고, Draft BO에서는 `Prepare`(=Activate 직전)에 등록해야 draft 상태에서도 실행됩니다(10단계). 그래서 "화면에 즉시 보여야 하는 값"은 on modify, "저장 직전 확정 값"은 on save에 둡니다.
- **트리거 조건**:
  - `create;` 인스턴스가 만들어질 때.
  - `update;` 업데이트될 때. 단 `on save`에서는 `create`와 함께만 쓸 수 있습니다(치트시트 36).
  - `delete;` 삭제될 때(삭제된 인스턴스는 다시 읽을 수 없으니 키만 씁니다).
  - `field A, B;` 해당 필드가 create 또는 update로 **바뀌었을 때**. 여러 조건이 있으면 하나만 만족해도 실행됩니다.
  - 그래서 `calculateTotalPrice`는 `{ create; field BookingFee, CurrencyCode; }`: 생성 때 한 번, 그 뒤엔 수수료나 통화가 바뀔 때만 돕니다. Description을 바꿔도 돌지 않습니다.
- **실행 순서는 정해져 있지 않습니다.** 여러 결정이 같은 시점에 트리거되면 순서는 임의입니다(치트시트 36: "the execution order of multiple specified determinations is arbitrary"). 그래서 `calculateTotalPrice`가 `setInitialValues`보다 먼저 돌 수도 있습니다. `reCalcTotalPrice`가 `CurrencyCode`가 빈 Travel을 건너뛰는(`DELETE travels WHERE CurrencyCode IS INITIAL`) 이유이고, `setInitialValues`가 통화를 채우면 그 변경이 다시 `field CurrencyCode` 트리거를 만족시켜 총액이 계산됩니다. 결정이 다른 결정을 연쇄로 트리거할 수 있으므로 **같은 값을 매번 다시 쓰지 않게**(이미 값이 있으면 건너뛰기) 작성해야 무한 반복을 피합니다.
- **내부 액션으로 공통 로직 공유**: 총액 계산은 Travel 쪽(수수료·통화 변경)과 Booking 쪽(항공료 변경) 두 곳에서 필요합니다. 계산을 `internal action reCalcTotalPrice` 하나에 두고 양쪽 결정이 `EXECUTE reCalcTotalPrice`로 부릅니다(RAP110 ex07). `internal`이라 Fiori나 외부 EML에서는 호출할 수 없습니다.
- `UPDATE FROM travels_upd` + `%control-필드 = mk-on`: `%control`이 켜진 필드만 바뀝니다. `UPDATE FIELDS ( … ) WITH …`는 나열한 필드의 `%control`을 자동으로 켜 주는 축약형입니다.
- 결정 안에서는 `failed`가 없고 `reported`만 있습니다(결정은 실패할 수 없고, 데이터를 고칠 뿐입니다).

**클래스 구조 해설**

- `determination X on modify` 한 줄 → `METHODS X FOR DETERMINE ON MODIFY IMPORTING keys FOR Travel~X.` `keys`의 타입은 `TABLE FOR DETERMINATION zrap_r_travel_###\\Travel~X`이며 `%tky`(draft면 `%is_draft` 포함)만 들어 있습니다. 그래서 항상 READ로 필요한 필드를 먼저 읽습니다.
- `internal action reCalcTotalPrice` → `METHODS reCalcTotalPrice FOR MODIFY IMPORTING keys FOR ACTION Travel~reCalcTotalPrice.` 결과가 없으므로 `RESULT`가 없습니다.
- 호출 시점: on modify는 같은 EML/OData 요청 처리 중 수정 직후, on save는 `COMMIT ENTITIES`/Activate의 save sequence 안(`check_before_save` 이전 finalize 단계)입니다.
- Booking 결정이 Travel 액션을 실행해도 됩니다. 같은 BO 안의 `IN LOCAL MODE` 호출이라 잠금·권한 검사를 다시 하지 않습니다.

**자주 나는 오류와 해결**

- `The field "TotalPrice" is read-only` 류의 오류(EML 결과의 `failed`)가 나면 `IN LOCAL MODE`를 빠뜨린 경우입니다.
- 총액이 0으로 남음 → Travel의 `CurrencyCode`가 비어 있거나 Booking 통화가 비어 있는지 확인하세요(빈 통화는 계산에서 제외).

</details>

#### 4단계. 검증(Validation)과 state message, Prepare 등록

요구사항

1. Travel 검증 (모두 **on save**):
   - `validateCustomer { create; field CustomerID; }`: 비어 있으면 메시지 001, `/DMO/CUSTOMER`에 없으면 002.
   - `validateAgency { create; field AgencyID; }`: 비어 있으면 003, `/DMO/AGENCY`에 없으면 004.
   - `validateDates { create; field BeginDate, EndDate; }`: 둘 중 하나라도 비면 007, 시작 > 종료면 005, 시작 < 오늘이면 006.
2. Booking 검증:
   - `validateConnection { create; field CarrierID, ConnectionID, FlightDate; }`: 셋 중 하나라도 비면 011, `/DMO/FLIGHT`에 없으면 012, 있지만 비행일이 부모 Travel의 기간 밖이면 **경고** 014(저장은 허용).
   - `validateStatus { create; field BookingStatus; }`: N/B/X가 아니면 013.
3. 메시지 규칙
   - 검증마다 고유한 `%state_area`(예: `'VALIDATE_CUSTOMER'`)를 쓰고, 검사하는 **모든** 인스턴스에 대해 먼저 "빈 메시지(%state_area만)"를 넣어 이전 메시지를 지운 뒤, 오류일 때만 메시지를 추가합니다.
   - 오류 필드는 `%element-필드 = if_abap_behv=>mk-on`으로 표시합니다.
   - Booking 메시지에는 `%path`로 부모 Travel 키를 넣습니다.
   - 오류면 `failed-…`에도 키를 넣고, 경고는 넣지 않습니다.
   - DB 조회는 반드시 한 번에(`FOR ALL ENTRIES`, 정렬 테이블로 중복 제거). 루프 안 SELECT 금지.
4. 위 검증 다섯 개를 Travel의 `draft determine action Prepare`에 모두 등록하세요(Booking 것은 `Booking~이름`).

**확인**

- Fiori: 새 Travel에서 Customer에 999999 입력 → **Save** → 오류 팝오버 "Customer 999999 does not exist.", Customer 필드가 빨갛게 표시, 저장(활성화) 안 됨. 올바른 고객으로 고치고 Save → 이전 메시지가 사라지고 저장 성공.
- Booking의 Flight Date를 여행 기간 밖의 실제 항공편 날짜로 → Save → 노란 경고만 뜨고 저장은 성공.
- Booking의 Connection을 존재하지 않는 번호로 → Save → 오류 메시지를 누르면 해당 Booking 줄로 이동(%path 덕분).

<details><summary>정답·해설</summary>

BDEF (Travel):

```bdef
  // ── 검증: 항상 on save. 트리거가 만족된 인스턴스만 keys로 들어옴 ──
  validation validateCustomer on save { create; field CustomerID; }
  validation validateAgency on save { create; field AgencyID; }
  validation validateDates on save { create; field BeginDate, EndDate; }

  // R-01에서 비어 있던 Prepare를 아래로 교체 (setDefaultDescription은 3단계의 on save 결정)
  draft determine action Prepare
  {
    determination setDefaultDescription;
    validation validateCustomer;
    validation validateAgency;
    validation validateDates;
    validation Booking~validateConnection;
    validation Booking~validateStatus;
  }
```

BDEF (Booking):

```bdef
  validation validateConnection on save { create; field CarrierID, ConnectionID, FlightDate; }
  validation validateStatus on save { create; field BookingStatus; }
```

`lhc_travel` 선언:

```abap
    METHODS validateCustomer FOR VALIDATE ON SAVE
      IMPORTING keys FOR Travel~validateCustomer.

    METHODS validateAgency FOR VALIDATE ON SAVE
      IMPORTING keys FOR Travel~validateAgency.

    METHODS validateDates FOR VALIDATE ON SAVE
      IMPORTING keys FOR Travel~validateDates.
```

`lhc_travel` 구현:

```abap
  METHOD validateCustomer.
    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        FIELDS ( CustomerID )
        WITH CORRESPONDING #( keys )
      RESULT DATA(travels).

    " 중복 없는 고객 번호만 모아 한 번에 SELECT
    DATA customers TYPE SORTED TABLE OF /dmo/customer WITH UNIQUE KEY customer_id.
    customers = CORRESPONDING #( travels DISCARDING DUPLICATES MAPPING customer_id = CustomerID EXCEPT * ).
    DELETE customers WHERE customer_id IS INITIAL.

    IF customers IS NOT INITIAL.
      SELECT FROM /dmo/customer
        FIELDS customer_id
        FOR ALL ENTRIES IN @customers
        WHERE customer_id = @customers-customer_id
        INTO TABLE @DATA(valid_customers).
    ENDIF.

    LOOP AT travels INTO DATA(travel).
      " 1) 이 검증이 예전에 남긴 메시지를 먼저 지움 (state message)
      APPEND VALUE #( %tky        = travel-%tky
                      %state_area = state_area-customer ) TO reported-travel.

      IF travel-CustomerID IS INITIAL.
        APPEND VALUE #( %tky = travel-%tky ) TO failed-travel.
        APPEND VALUE #( %tky                = travel-%tky
                        %state_area         = state_area-customer
                        %msg                = NEW zcm_rap_###( textid   = zcm_rap_###=>enter_customer_id
                                                               severity = if_abap_behv_message=>severity-error )
                        %element-CustomerID = if_abap_behv=>mk-on ) TO reported-travel.

      ELSEIF NOT line_exists( valid_customers[ customer_id = travel-CustomerID ] ).
        APPEND VALUE #( %tky = travel-%tky ) TO failed-travel.
        APPEND VALUE #( %tky                = travel-%tky
                        %state_area         = state_area-customer
                        %msg                = NEW zcm_rap_###( textid      = zcm_rap_###=>customer_unknown
                                                               customer_id = travel-CustomerID
                                                               severity    = if_abap_behv_message=>severity-error )
                        %element-CustomerID = if_abap_behv=>mk-on ) TO reported-travel.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

  METHOD validateAgency.
    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        FIELDS ( AgencyID )
        WITH CORRESPONDING #( keys )
      RESULT DATA(travels).

    DATA agencies TYPE SORTED TABLE OF /dmo/agency WITH UNIQUE KEY agency_id.
    agencies = CORRESPONDING #( travels DISCARDING DUPLICATES MAPPING agency_id = AgencyID EXCEPT * ).
    DELETE agencies WHERE agency_id IS INITIAL.

    IF agencies IS NOT INITIAL.
      SELECT FROM /dmo/agency
        FIELDS agency_id
        FOR ALL ENTRIES IN @agencies
        WHERE agency_id = @agencies-agency_id
        INTO TABLE @DATA(valid_agencies).
    ENDIF.

    LOOP AT travels INTO DATA(travel).
      APPEND VALUE #( %tky        = travel-%tky
                      %state_area = state_area-agency ) TO reported-travel.

      IF travel-AgencyID IS INITIAL.
        APPEND VALUE #( %tky = travel-%tky ) TO failed-travel.
        APPEND VALUE #( %tky              = travel-%tky
                        %state_area       = state_area-agency
                        %msg              = NEW zcm_rap_###( textid   = zcm_rap_###=>enter_agency_id
                                                             severity = if_abap_behv_message=>severity-error )
                        %element-AgencyID = if_abap_behv=>mk-on ) TO reported-travel.

      ELSEIF NOT line_exists( valid_agencies[ agency_id = travel-AgencyID ] ).
        APPEND VALUE #( %tky = travel-%tky ) TO failed-travel.
        APPEND VALUE #( %tky              = travel-%tky
                        %state_area       = state_area-agency
                        %msg              = NEW zcm_rap_###( textid    = zcm_rap_###=>agency_unknown
                                                             agency_id = travel-AgencyID
                                                             severity  = if_abap_behv_message=>severity-error )
                        %element-AgencyID = if_abap_behv=>mk-on ) TO reported-travel.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

  METHOD validateDates.
    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        FIELDS ( TravelID BeginDate EndDate )
        WITH CORRESPONDING #( keys )
      RESULT DATA(travels).

    DATA(today) = cl_abap_context_info=>get_system_date( ).

    LOOP AT travels INTO DATA(travel).
      APPEND VALUE #( %tky        = travel-%tky
                      %state_area = state_area-dates ) TO reported-travel.

      IF travel-BeginDate IS INITIAL OR travel-EndDate IS INITIAL.
        APPEND VALUE #( %tky = travel-%tky ) TO failed-travel.
        APPEND VALUE #( %tky               = travel-%tky
                        %state_area        = state_area-dates
                        %msg               = NEW zcm_rap_###( textid   = zcm_rap_###=>enter_dates
                                                              severity = if_abap_behv_message=>severity-error )
                        %element-BeginDate = if_abap_behv=>mk-on
                        %element-EndDate   = if_abap_behv=>mk-on ) TO reported-travel.

      ELSEIF travel-EndDate < travel-BeginDate.
        APPEND VALUE #( %tky = travel-%tky ) TO failed-travel.
        APPEND VALUE #( %tky               = travel-%tky
                        %state_area        = state_area-dates
                        %msg               = NEW zcm_rap_###( textid     = zcm_rap_###=>begin_date_after_end_date
                                                              begin_date = travel-BeginDate
                                                              end_date   = travel-EndDate
                                                              severity   = if_abap_behv_message=>severity-error )
                        %element-BeginDate = if_abap_behv=>mk-on
                        %element-EndDate   = if_abap_behv=>mk-on ) TO reported-travel.

      ELSEIF travel-BeginDate < today.
        APPEND VALUE #( %tky = travel-%tky ) TO failed-travel.
        APPEND VALUE #( %tky               = travel-%tky
                        %state_area        = state_area-dates
                        %msg               = NEW zcm_rap_###( textid     = zcm_rap_###=>begin_date_in_past
                                                              begin_date = travel-BeginDate
                                                              severity   = if_abap_behv_message=>severity-error )
                        %element-BeginDate = if_abap_behv=>mk-on ) TO reported-travel.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.
```

`lhc_booking` 선언 추가:

```abap
    METHODS validateConnection FOR VALIDATE ON SAVE
      IMPORTING keys FOR Booking~validateConnection.

    METHODS validateStatus FOR VALIDATE ON SAVE
      IMPORTING keys FOR Booking~validateStatus.
```

`lhc_booking` 구현:

```abap
  METHOD validateConnection.
    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Booking
        FIELDS ( BookingID CarrierID ConnectionID FlightDate )
        WITH CORRESPONDING #( keys )
      RESULT DATA(bookings).

    " 부모 Travel (메시지의 %path, 여행 기간 확인용)
    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Booking BY \_Travel
        FIELDS ( BeginDate EndDate )
        WITH CORRESPONDING #( bookings )
      RESULT DATA(travels)
      LINK DATA(booking_to_travel).

    " 존재 확인은 한 번의 SELECT로
    DATA flights_req TYPE SORTED TABLE OF /dmo/flight WITH UNIQUE KEY carrier_id connection_id flight_date.
    DATA flights_db  TYPE SORTED TABLE OF /dmo/flight WITH UNIQUE KEY carrier_id connection_id flight_date.
    flights_req = CORRESPONDING #( bookings DISCARDING DUPLICATES
                                   MAPPING carrier_id    = CarrierID
                                           connection_id = ConnectionID
                                           flight_date   = FlightDate EXCEPT * ).
    DELETE flights_req WHERE carrier_id IS INITIAL OR connection_id IS INITIAL OR flight_date IS INITIAL.

    IF flights_req IS NOT INITIAL.
      SELECT FROM /dmo/flight
        FIELDS *
        FOR ALL ENTRIES IN @flights_req
        WHERE carrier_id    = @flights_req-carrier_id
          AND connection_id = @flights_req-connection_id
          AND flight_date   = @flights_req-flight_date
        INTO TABLE @flights_db.
    ENDIF.

    LOOP AT bookings INTO DATA(booking).
      DATA(travel_tky) = booking_to_travel[ KEY id source-%tky = booking-%tky ]-target-%tky.

      APPEND VALUE #( %tky        = booking-%tky
                      %state_area = state_area-connection ) TO reported-booking.

      IF booking-CarrierID IS INITIAL OR booking-ConnectionID IS INITIAL OR booking-FlightDate IS INITIAL.
        APPEND VALUE #( %tky = booking-%tky ) TO failed-booking.
        APPEND VALUE #( %tky                  = booking-%tky
                        %state_area           = state_area-connection
                        %msg                  = NEW zcm_rap_###( textid   = zcm_rap_###=>enter_flight
                                                                 severity = if_abap_behv_message=>severity-error )
                        %path                 = VALUE #( travel-%tky = travel_tky )
                        %element-CarrierID    = if_abap_behv=>mk-on
                        %element-ConnectionID = if_abap_behv=>mk-on
                        %element-FlightDate   = if_abap_behv=>mk-on ) TO reported-booking.

      ELSEIF NOT line_exists( flights_db[ carrier_id    = booking-CarrierID
                                          connection_id = booking-ConnectionID
                                          flight_date   = booking-FlightDate ] ).
        APPEND VALUE #( %tky = booking-%tky ) TO failed-booking.
        APPEND VALUE #( %tky                  = booking-%tky
                        %state_area           = state_area-connection
                        %msg                  = NEW zcm_rap_###( textid        = zcm_rap_###=>flight_unknown
                                                                 carrier_id    = booking-CarrierID
                                                                 connection_id = booking-ConnectionID
                                                                 flight_date   = booking-FlightDate
                                                                 severity      = if_abap_behv_message=>severity-error )
                        %path                 = VALUE #( travel-%tky = travel_tky )
                        %element-ConnectionID = if_abap_behv=>mk-on
                        %element-FlightDate   = if_abap_behv=>mk-on ) TO reported-booking.

      ELSE.
        " 경고: 저장은 막지 않음 → failed에 넣지 않음
        DATA(travel) = travels[ KEY id %tky = travel_tky ].
        IF booking-FlightDate < travel-BeginDate OR booking-FlightDate > travel-EndDate.
          APPEND VALUE #( %tky                = booking-%tky
                          %state_area         = state_area-connection
                          %msg                = NEW zcm_rap_###( textid      = zcm_rap_###=>flight_outside_travel
                                                                 flight_date = booking-FlightDate
                                                                 severity    = if_abap_behv_message=>severity-warning )
                          %path               = VALUE #( travel-%tky = travel_tky )
                          %element-FlightDate = if_abap_behv=>mk-on ) TO reported-booking.
        ENDIF.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

  METHOD validateStatus.
    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Booking
        FIELDS ( BookingStatus )
        WITH CORRESPONDING #( keys )
      RESULT DATA(bookings).

    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Booking BY \_Travel
        FROM CORRESPONDING #( bookings )
      LINK DATA(booking_to_travel).

    LOOP AT bookings INTO DATA(booking).
      APPEND VALUE #( %tky        = booking-%tky
                      %state_area = state_area-status ) TO reported-booking.

      IF booking-BookingStatus <> booking_status-new
     AND booking-BookingStatus <> booking_status-booked
     AND booking-BookingStatus <> booking_status-cancelled.
        APPEND VALUE #( %tky = booking-%tky ) TO failed-booking.
        APPEND VALUE #( %tky                   = booking-%tky
                        %state_area            = state_area-status
                        %msg                   = NEW zcm_rap_###( textid   = zcm_rap_###=>booking_status_invalid
                                                                  status   = booking-BookingStatus
                                                                  severity = if_abap_behv_message=>severity-error )
                        %path                  = VALUE #( travel-%tky = booking_to_travel[ KEY id source-%tky = booking-%tky ]-target-%tky )
                        %element-BookingStatus = if_abap_behv=>mk-on ) TO reported-booking.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.
```

**왜 이렇게 쓰나**

- **state message vs transition message**: `%state_area`가 있는 메시지는 "인스턴스 상태에 붙은 메시지"로 draft에 남아 있다가, 같은 state area로 다시 보고될 때 교체됩니다. 그래서 검증 시작 때 **빈 메시지(%tky + %state_area)** 를 넣으면 "이 검증이 예전에 낸 메시지를 지워라"는 뜻이 됩니다. 고친 뒤에도 옛 오류가 남는 문제를 막습니다. `%state_area`가 없는 메시지(6단계 acceptTravel의 성공 메시지)는 한 번 보여 주고 끝나는 transition message입니다.
- **%element**: 어느 필드가 문제인지 표시 → Fiori가 그 입력 필드를 빨갛게 강조하고 메시지에서 필드로 이동시킵니다.
- **%path**: 자식(Booking) 메시지는 부모 키를 알아야 Fiori가 Object Page의 Booking 표 안 위치를 찾습니다. `%path-travel-%tky`에 부모 `%tky`를 넣고, 부모 키는 `BY \_Travel ... LINK`로 얻습니다(Flight Reference Scenario `/DMO/BP_BOOKING_D`와 같은 방식).
- **failed + reported**: 오류면 `failed`에 키를 넣어야 저장 순서가 중단됩니다(검증 하나라도 실패하면 버퍼 전체가 저장되지 않음 — all or nothing). 메시지만 넣고 `failed`를 빠뜨리면 메시지는 뜨는데 저장이 되어 버립니다. 경고(014)는 일부러 `failed`에 넣지 않았습니다.
- **트리거 `{ create; field … }`**: 검증은 "새로 만들었거나 관련 필드가 바뀐 인스턴스"만 다시 검사합니다. Description만 바꾼 Travel은 `validateCustomer`를 돌지 않아 성능이 좋습니다. 검증에서 `update`는 `create`와 함께만 쓸 수 있고(`{ create; update; }`), `delete` 트리거도 가능합니다.
- **Prepare 등록이 왜 필요한가**: Draft BO에서 사용자가 **Save**를 누르면 `Activate`가 실행되고, Activate는 먼저 `Prepare`를 호출해 거기 등록된 검증/결정만 draft 데이터에 대해 실행합니다. Prepare에 없는 검증은 draft 단계에서 실행되지 않아 메시지가 화면에 안 나타납니다(활성 데이터 저장 때는 여전히 실행). 자식 검증도 루트의 Prepare에 `Booking~validateConnection`처럼 적어야 합니다.
- **대량 처리**: 고객/여행사/항공편 존재 확인은 `CORRESPONDING … DISCARDING DUPLICATES`로 중복 없는 키를 만든 뒤 `FOR ALL ENTRIES` 한 번으로 조회합니다. `FOR ALL ENTRIES`는 키 테이블이 비면 전체를 읽으므로 반드시 `IF … IS NOT INITIAL`로 감쌉니다.

**클래스 구조 해설**

- `validation X on save { … }` → `METHODS X FOR VALIDATE ON SAVE IMPORTING keys FOR Travel~X.` 암시적 응답 파라미터 `failed`, `reported`가 있습니다(`mapped` 없음).
- 호출 시점: `COMMIT ENTITIES`(비draft) 또는 Draft의 `Prepare`/`Activate` 때 save sequence의 `check_before_save` 단계. 상호작용 단계(필드 입력 중)에는 돌지 않습니다. 입력 즉시 검사를 원하면 9단계의 determine action + side effect를 씁니다.

**자주 나는 오류와 해결**

- 고쳤는데 오류 메시지가 계속 남음 → 루프 시작의 "빈 state 메시지" APPEND를 빠뜨렸거나, 삭제용과 추가용의 `%state_area` 문자열이 다릅니다(상수로 통일하세요).
- Booking 오류를 눌러도 해당 줄로 안 감 → `%path`를 빠뜨렸습니다.
- Prepare에 `validation Booking~validateConnection;`을 적었더니 "unknown" 오류 → Booking BDEF에 검증을 먼저 정의하고 함께 활성화하세요.

</details>

#### 5단계. 추상 엔터티 네 개: 액션 파라미터와 함수 결과 타입

요구사항

추상 엔터티(`define abstract entity`)는 DB에 아무것도 만들지 않는 "구조 정의"입니다. 액션의 입력 파라미터(`parameter`)와 함수의 결과(`result`) 타입으로 씁니다. ADT: **New → Other → Core Data Services → Data Definition**, 템플릿 **Define Abstract Entity**.

1. `ZRAP_A_DISCOUNT_###` (라벨 "Parameter: deduct discount")
   - `discount_percent` : `abap.int1` — 팝업에 "Discount (%)"로 보이게.
2. `ZRAP_A_CREATE_TRAVEL_###` (라벨 "Parameter: create travel")
   - `customer_id` : `/dmo/customer_id` — 라벨 "Customer", 값 도움말 `/DMO/I_Customer_StdVH`(요소 `CustomerID`).
   - `agency_id` : `/dmo/agency_id` — 라벨 "Agency", 값 도움말 `/DMO/I_Agency_StdVH`(요소 `AgencyID`).
   - `carrier_id` : `/dmo/carrier_id`, `connection_id` : `/dmo/connection_id`, `flight_date` : `/dmo/flight_date` — 세 필드 모두 값 도움말 `/DMO/I_Flight_StdVH`. 하나를 고르면 나머지 두 필드도 채워지도록(결과 바인딩), 항공사를 먼저 고르면 그 항공사 항공편만 보이도록(필터 바인딩).
3. `ZRAP_A_DAYS_TO_FLIGHT_###` (라벨 "Result: days to flight")
   - `initial_days_to_flight`, `remaining_days_to_flight`, `days_to_flight_indicator` : 모두 `abap.int4`.
4. `ZRAP_A_TRAVEL_STAT_###` (라벨 "Result: travel statistics")
   - `open_count`, `accepted_count`, `rejected_count` : 모두 `abap.int4`.

**직접 추가할 어노테이션**

- `@EndUserText.label` (엔터티 머리) — 객체 설명. 추상 엔터티에는 `@AccessControl`이 필요 없습니다.
- `@EndUserText.label` (요소) — 액션 팝업에서 입력 필드 라벨로 보일 텍스트.
- `@Consumption.valueHelpDefinition` — 파라미터 입력 필드에 값 도움말(F4)을 붙임. `entity`의 `name`/`element`로 대상 뷰와 연결 요소 지정.
- `@Consumption.valueHelpDefinition`의 `additionalBinding` (`localElement`, `element`, `usage`) — 값 도움말에서 고른 행의 다른 열을 다른 파라미터에 채우거나(#RESULT), 다른 파라미터 값으로 목록을 거름(#FILTER, #FILTER_AND_RESULT).

**확인**

- 네 개 모두 활성화 성공(Data Preview는 추상 엔터티에 없습니다).
- 6단계·7단계에서 액션 팝업을 열었을 때 라벨과 값 도움말이 보이면 성공.

<details><summary>정답·해설</summary>

```cds
@EndUserText.label: 'Parameter: deduct discount'   // 객체 설명 (→ 어노테이션 탭: @EndUserText.label)
define abstract entity ZRAP_A_DISCOUNT_###
{
  @EndUserText.label: 'Discount (%)'               // 팝업 입력 필드 라벨 (→ 어노테이션 탭: @EndUserText.label)
  discount_percent : abap.int1;
}
```

```cds
@EndUserText.label: 'Parameter: create travel'
define abstract entity ZRAP_A_CREATE_TRAVEL_###
{
  @EndUserText.label: 'Customer'
  @Consumption.valueHelpDefinition: [ {                         // 입력 필드에 F4 (→ 어노테이션 탭: @Consumption.valueHelpDefinition)
    entity: { name: '/DMO/I_Customer_StdVH', element: 'CustomerID' } } ]
  customer_id   : /dmo/customer_id;

  @EndUserText.label: 'Agency'
  @Consumption.valueHelpDefinition: [ {
    entity: { name: '/DMO/I_Agency_StdVH', element: 'AgencyID' } } ]
  agency_id     : /dmo/agency_id;

  @EndUserText.label: 'Airline'
  @Consumption.valueHelpDefinition: [ {
    entity: { name: '/DMO/I_Flight_StdVH', element: 'AirlineID' },
    additionalBinding: [                                        // 고른 행의 다른 열을 다른 파라미터에 (→ 어노테이션 탭: @Consumption.valueHelpDefinition.additionalBinding)
      { localElement: 'connection_id', element: 'ConnectionID', usage: #RESULT },
      { localElement: 'flight_date',   element: 'FlightDate',   usage: #RESULT } ] } ]
  carrier_id    : /dmo/carrier_id;

  @EndUserText.label: 'Connection'
  @Consumption.valueHelpDefinition: [ {
    entity: { name: '/DMO/I_Flight_StdVH', element: 'ConnectionID' },
    additionalBinding: [
      { localElement: 'carrier_id',  element: 'AirlineID',  usage: #FILTER_AND_RESULT }, // 항공사로 거르고 결과도 채움
      { localElement: 'flight_date', element: 'FlightDate', usage: #RESULT } ] } ]
  connection_id : /dmo/connection_id;

  @EndUserText.label: 'Flight Date'
  @Consumption.valueHelpDefinition: [ {
    entity: { name: '/DMO/I_Flight_StdVH', element: 'FlightDate' },
    additionalBinding: [
      { localElement: 'carrier_id',    element: 'AirlineID',    usage: #FILTER_AND_RESULT },
      { localElement: 'connection_id', element: 'ConnectionID', usage: #FILTER_AND_RESULT } ] } ]
  flight_date   : /dmo/flight_date;
}
```

```cds
@EndUserText.label: 'Result: days to flight'
define abstract entity ZRAP_A_DAYS_TO_FLIGHT_###
{
  initial_days_to_flight   : abap.int4;   // 예약일 → 비행일 일수
  remaining_days_to_flight : abap.int4;   // 오늘 → 비행일 일수
  days_to_flight_indicator : abap.int4;   // 1 빨강 / 2 주황 / 3 초록 / 0 지남
}
```

```cds
@EndUserText.label: 'Result: travel statistics'
define abstract entity ZRAP_A_TRAVEL_STAT_###
{
  open_count     : abap.int4;
  accepted_count : abap.int4;
  rejected_count : abap.int4;
}
```

**왜 이렇게 쓰나**

- 액션 파라미터는 BDEF의 `parameter`에, 함수 결과는 `result [1] 이름`에 이 엔터티 이름을 적습니다. 행동 풀에서는 `keys[ … ]-%param-discount_percent`, `result-%param-open_count`처럼 `%param` 아래에 이 요소들이 보입니다.
- 요소 이름을 소문자+밑줄(`discount_percent`)로 둔 것은 RAP110·Flight Reference Scenario 예제와 같은 관례입니다. 이 이름이 그대로 `%param`의 컴포넌트 이름이 됩니다.
- 값 도움말 정의는 RAP110 `ZRAP110_A_CREATE_TRAVEL_SOL`을 따랐고, 여기에 여행사 파라미터를 추가했습니다. `/DMO/I_Flight_StdVH`의 키 요소 이름은 `AirlineID`, `ConnectionID`, `FlightDate`입니다.
- 추상 엔터티에는 데이터 소스와 키가 없고, 권한 검사(`@AccessControl.authorizationCheck`)도 의미가 없습니다.

**클래스 구조 해설** 추상 엔터티는 파생 타입의 `%param` 구조를 결정합니다. 예: `TABLE FOR ACTION IMPORT zrap_r_travel_###\\Travel~deductDiscount`의 한 줄 = `%cid_ref`, `%tky`, `%param`(= `ZRAP_A_DISCOUNT_###` 구조). 추상 엔터티를 바꾸면 BDEF와 행동 풀을 다시 활성화해야 할 수 있습니다.

**자주 나는 오류와 해결**

- `additionalBinding`의 `localElement`에 존재하지 않는 요소 이름을 적어도 활성화는 될 수 있지만 UI에서 바인딩이 동작하지 않습니다. 요소 이름(소문자)을 정확히 맞추세요.

</details>

#### 6단계. 인스턴스 액션: accept/reject, 파라미터 액션 + 기본값 함수, 반복 가능 액션

요구사항

1. `acceptTravel`, `rejectTravel`: 인스턴스 액션, `features : instance`, 결과 `[1] $self`. 상태를 A/X로 바꾸고 변경 후 데이터를 결과로 돌려주며, 성공 메시지(009/010, severity success)를 냅니다.
2. `deductDiscount`: 파라미터 `ZRAP_A_DISCOUNT_###`, 결과 `[1] $self`, `features : instance`. `BookingFee`를 `discount_percent`만큼 깎습니다. 0 또는 100 초과면 메시지 008 오류(`%op-%action-deductDiscount` 표시)로 실패.
   - 기본값 함수 `GetDefaultsFordeductDiscount`: 총액이 5000 이상이면 20, 아니면 10을 팝업 기본값으로 제안.
3. `addServiceFee`: **repeatable** 액션, 결과 `[1] $self`. 실행할 때마다 BookingFee에 10을 더합니다. 한 요청에서 같은 Travel에 두 번 실행하면 20이 더해져야 합니다.
4. 동적 기능 제어 `get_instance_features`: 승인(A)이면 accept·deductDiscount·update·delete·Edit 비활성, 거절(X)이면 reject와 Booking 추가(`%assoc-_Booking`) 비활성. (BDEF의 `update`, `delete`, `association _Booking { create … }`, 그리고 draft 액션 `Edit`에도 `features : instance`를 붙입니다. `Edit`에 붙이지 않으면 `%action-Edit` 컴포넌트가 없어서 "No component exists with the name EDIT" 오류가 납니다.)
5. `result [1] $self`인 액션은 결과를 반드시 **MODIFY 후 다시 READ**해서 채우세요.

**확인**

- 아직 프로젝션/MDE에 노출하지 않았으므로 12단계에서 Fiori로 확인합니다. 지금은 BDEF·행동 풀 활성화 성공까지.
- 8단계의 확인 클래스에서 `addServiceFee`를 같은 Travel에 두 번 실행하면 BookingFee가 20 증가합니다.

<details><summary>정답·해설</summary>

BDEF (Travel) — 표준 작업 줄을 아래로 교체하고 액션 추가:

```bdef
  create;
  update ( features : instance );                                 // 상태에 따라 수정 가능/불가
  delete ( features : instance );
  association _Booking { create ( features : instance ); with draft; }

  // 기존 draft action Edit; 줄을 이렇게 교체 → get_instance_features 결과에 %action-Edit 이 생김
  draft action ( features : instance ) Edit;

  // result [1] $self: 결과는 같은 엔터티 인스턴스 1건 → Fiori가 화면을 그 값으로 갱신
  action ( features : instance ) acceptTravel result [1] $self;
  action ( features : instance ) rejectTravel result [1] $self;

  // parameter: 팝업 입력값. { default function … }: 팝업 기본값을 채우는 함수
  action ( features : instance ) deductDiscount parameter ZRAP_A_DISCOUNT_### result [1] $self
    { default function GetDefaultsFordeductDiscount; }

  // repeatable: 한 요청에서 같은 인스턴스에 여러 번 실행 가능 (키 타입에 %cid가 생김)
  repeatable action addServiceFee result [1] $self;
```

`lhc_travel` 선언:

```abap
    METHODS get_instance_features FOR INSTANCE FEATURES
      IMPORTING keys REQUEST requested_features FOR Travel RESULT result.

    METHODS acceptTravel FOR MODIFY
      IMPORTING keys FOR ACTION Travel~acceptTravel RESULT result.

    METHODS rejectTravel FOR MODIFY
      IMPORTING keys FOR ACTION Travel~rejectTravel RESULT result.

    METHODS deductDiscount FOR MODIFY
      IMPORTING keys FOR ACTION Travel~deductDiscount RESULT result.

    METHODS GetDefaultsFordeductDiscount FOR READ
      IMPORTING keys FOR FUNCTION Travel~GetDefaultsFordeductDiscount RESULT result.

    METHODS addServiceFee FOR MODIFY
      IMPORTING keys FOR ACTION Travel~addServiceFee RESULT result.
```

구현:

```abap
  METHOD get_instance_features.
    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        FIELDS ( OverallStatus )
        WITH CORRESPONDING #( keys )
      RESULT DATA(travels)
      FAILED failed.

    result = VALUE #(
      FOR travel IN travels
      ( %tky                   = travel-%tky
        %features-%update      = COND #( WHEN travel-OverallStatus = travel_status-accepted
                                         THEN if_abap_behv=>fc-o-disabled
                                         ELSE if_abap_behv=>fc-o-enabled )
        %features-%delete      = COND #( WHEN travel-OverallStatus = travel_status-accepted
                                         THEN if_abap_behv=>fc-o-disabled
                                         ELSE if_abap_behv=>fc-o-enabled )
        %action-Edit           = COND #( WHEN travel-OverallStatus = travel_status-accepted
                                         THEN if_abap_behv=>fc-o-disabled
                                         ELSE if_abap_behv=>fc-o-enabled )
        %action-acceptTravel   = COND #( WHEN travel-OverallStatus = travel_status-accepted
                                         THEN if_abap_behv=>fc-o-disabled
                                         ELSE if_abap_behv=>fc-o-enabled )
        %action-rejectTravel   = COND #( WHEN travel-OverallStatus = travel_status-rejected
                                         THEN if_abap_behv=>fc-o-disabled
                                         ELSE if_abap_behv=>fc-o-enabled )
        %action-deductDiscount = COND #( WHEN travel-OverallStatus = travel_status-accepted
                                         THEN if_abap_behv=>fc-o-disabled
                                         ELSE if_abap_behv=>fc-o-enabled )
        %assoc-_Booking        = COND #( WHEN travel-OverallStatus = travel_status-rejected
                                         THEN if_abap_behv=>fc-o-disabled
                                         ELSE if_abap_behv=>fc-o-enabled ) ) ).
  ENDMETHOD.

  METHOD acceptTravel.
    MODIFY ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        UPDATE FIELDS ( OverallStatus )
        WITH VALUE #( FOR key IN keys ( %tky          = key-%tky
                                        OverallStatus = travel_status-accepted ) )
      FAILED failed
      REPORTED reported.

    " 결과는 반드시 변경 후 상태를 다시 읽어 채움
    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        ALL FIELDS WITH CORRESPONDING #( keys )
      RESULT DATA(travels).

    result = VALUE #( FOR travel IN travels ( %tky   = travel-%tky
                                              %param = travel ) ).

    " 성공 메시지 (state area 없음 = 일회성 transition message)
    LOOP AT travels INTO DATA(accepted).
      APPEND VALUE #( %tky = accepted-%tky
                      %msg = NEW zcm_rap_###( textid    = zcm_rap_###=>travel_accepted
                                              travel_id = accepted-TravelID
                                              severity  = if_abap_behv_message=>severity-success ) )
        TO reported-travel.
    ENDLOOP.
  ENDMETHOD.

  METHOD rejectTravel.
    MODIFY ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        UPDATE FIELDS ( OverallStatus )
        WITH VALUE #( FOR key IN keys ( %tky          = key-%tky
                                        OverallStatus = travel_status-rejected ) )
      FAILED failed
      REPORTED reported.

    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        ALL FIELDS WITH CORRESPONDING #( keys )
      RESULT DATA(travels).

    result = VALUE #( FOR travel IN travels ( %tky   = travel-%tky
                                              %param = travel ) ).

    LOOP AT travels INTO DATA(rejected).
      APPEND VALUE #( %tky = rejected-%tky
                      %msg = NEW zcm_rap_###( textid    = zcm_rap_###=>travel_rejected
                                              travel_id = rejected-TravelID
                                              severity  = if_abap_behv_message=>severity-success ) )
        TO reported-travel.
    ENDLOOP.
  ENDMETHOD.

  METHOD deductDiscount.
    DATA travels_for_update TYPE TABLE FOR UPDATE zrap_r_travel_###\\Travel.
    DATA(valid_keys) = keys.

    " 1) 파라미터 검사: 1~100 이 아니면 실패
    LOOP AT valid_keys ASSIGNING FIELD-SYMBOL(<key>) WHERE %param-discount_percent IS INITIAL
                                                        OR %param-discount_percent > 100.
      APPEND VALUE #( %tky = <key>-%tky ) TO failed-travel.
      APPEND VALUE #( %tky                       = <key>-%tky
                      %msg                       = NEW zcm_rap_###( textid   = zcm_rap_###=>discount_invalid
                                                                    severity = if_abap_behv_message=>severity-error )
                      %element-BookingFee        = if_abap_behv=>mk-on
                      %op-%action-deductDiscount = if_abap_behv=>mk-on ) TO reported-travel.
      DELETE valid_keys.
    ENDLOOP.
    CHECK valid_keys IS NOT INITIAL.

    " 2) 현재 수수료 읽기
    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        FIELDS ( BookingFee )
        WITH CORRESPONDING #( valid_keys )
      RESULT DATA(travels).

    " 3) 할인 계산 (decfloat16 변수에 대입해야 정수 나눗셈이 되지 않음)
    DATA percentage TYPE decfloat16.
    LOOP AT travels INTO DATA(travel).
      DATA(discount_percent) = valid_keys[ KEY id %tky = travel-%tky ]-%param-discount_percent.
      percentage = discount_percent / 100.
      APPEND VALUE #( %tky       = travel-%tky
                      BookingFee = travel-BookingFee * ( 1 - percentage ) ) TO travels_for_update.
    ENDLOOP.

    " 4) 변경 (→ calculateTotalPrice 결정이 BookingFee 변경으로 다시 실행됨)
    MODIFY ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        UPDATE FIELDS ( BookingFee )
        WITH travels_for_update.

    " 5) 결과
    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        ALL FIELDS WITH CORRESPONDING #( travels )
      RESULT DATA(travels_with_discount).

    result = VALUE #( FOR discounted IN travels_with_discount ( %tky   = discounted-%tky
                                                               %param = discounted ) ).
  ENDMETHOD.

  METHOD GetDefaultsFordeductDiscount.
    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        FIELDS ( TotalPrice )
        WITH CORRESPONDING #( keys )
      RESULT DATA(travels)
      FAILED failed.

    result = VALUE #( FOR travel IN travels
                      ( %tky                    = travel-%tky
                        %param-discount_percent = COND #( WHEN travel-TotalPrice >= 5000 THEN 20
                                                          ELSE 10 ) ) ).
  ENDMETHOD.

  METHOD addServiceFee.
    " keys에 같은 인스턴스가 여러 줄 올 수 있으므로 읽기용 키는 중복 제거
    DATA read_keys TYPE TABLE FOR READ IMPORT zrap_r_travel_###\\Travel.
    LOOP AT keys INTO DATA(key).
      IF NOT line_exists( read_keys[ %tky = key-%tky ] ).
        APPEND VALUE #( %tky = key-%tky ) TO read_keys.
      ENDIF.
    ENDLOOP.

    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        FIELDS ( BookingFee )
        WITH read_keys
      RESULT DATA(travels)
      FAILED failed.

    " 실행 횟수만큼 수수료 누적
    LOOP AT keys INTO key.
      ASSIGN travels[ KEY id %tky = key-%tky ] TO FIELD-SYMBOL(<travel>).
      IF sy-subrc = 0.
        <travel>-BookingFee += c_service_fee.
      ENDIF.
    ENDLOOP.

    MODIFY ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        UPDATE FIELDS ( BookingFee )
        WITH CORRESPONDING #( travels ).

    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        ALL FIELDS WITH read_keys
      RESULT DATA(travels_new).

    " 결과는 실행(키 줄) 하나당 한 줄. 반복 가능 액션은 %cid로 실행을 구분
    LOOP AT keys INTO key.
      READ TABLE travels_new WITH KEY id COMPONENTS %tky = key-%tky INTO DATA(travel_new).
      IF sy-subrc = 0.
        APPEND VALUE #( %cid   = key-%cid
                        %tky   = key-%tky
                        %param = travel_new ) TO result.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.
```

**왜 이렇게 쓰나**

- **결과를 다시 읽는 이유**: `result [1] $self`는 "액션이 끝난 뒤의 인스턴스"를 돌려준다는 약속입니다. `keys`에는 키만 있으므로, MODIFY 후 `ALL FIELDS`로 다시 읽어 `%param`에 넣어야 Fiori가 바뀐 상태를 즉시 보여 줍니다.
- **기본값 함수(default function)**: `deductDiscount { default function GetDefaultsFordeductDiscount; }`로 선언하면 Fiori가 팝업을 열기 전에 이 함수를 호출해 입력란을 미리 채웁니다. 구현은 `FOR READ … FOR FUNCTION` 메서드이고, 결과 `%param`이 파라미터 엔터티 구조입니다(Flight Reference Scenario `/DMO/BP_TRAVEL_D`와 같은 방식).
- **`%op-%action-deductDiscount`**: 메시지가 "이 액션 실행 때문"임을 표시합니다. 필드(`%element`)가 아니라 작업(operation)에 붙는 메시지입니다.
- **할인 계산**: `percentage`를 `decfloat16` 변수로 두고 대입해야 `int1 / 100`이 정수 나눗셈으로 0이 되지 않습니다. BookingFee가 바뀌면 3단계 `calculateTotalPrice` 결정이 다시 돌아 총액도 갱신됩니다.
- **repeatable action**: 일반 액션은 한 요청 안에서 같은 인스턴스에 두 번 실행하면 거부됩니다. `repeatable`을 붙이면 허용되고, 파생 타입에 `%cid`가 추가되어 실행 하나하나를 구분합니다(치트시트 33 릴리스 노트). 그래서 구현은 ① 읽기 키를 중복 제거하고 ② `keys`를 한 줄씩 돌며 누적하고 ③ 결과를 **실행(키 줄)마다 한 줄** 만듭니다. 결과 줄에 `%cid`를 넣는 부분은 결과 파생 타입에 `%cid`가 있다는 전제입니다. 활성화 때 "%CID is not a component" 오류가 나면 그 한 줄을 지우세요 (실제 시스템에서 확인 필요).
- **동적 기능 제어**: `features : instance`를 붙인 작업마다 `get_instance_features`의 결과에 `%features-%update`, `%action-acceptTravel`, `%assoc-_Booking` 같은 컴포넌트가 생깁니다. 값은 `if_abap_behv=>fc-o-enabled/disabled`(작업), 필드는 `fc-f-read_only/unrestricted/mandatory`. Fiori는 이 결과로 버튼을 회색 처리하고, 프레임워크는 비활성 작업 요청을 거부합니다.

**클래스 구조 해설**

| BDEF 줄 | 생기는 메서드 | 파생 타입(keys 한 줄) | 응답 |
|---|---|---|---|
| `action … acceptTravel result [1] $self` | `FOR MODIFY … FOR ACTION Travel~acceptTravel RESULT result` | `%cid_ref`, `%tky` | `result`(`%tky`, `%param`=Travel 전체), `failed`, `reported`, `mapped` |
| `action … deductDiscount parameter X result [1] $self` | 위와 같음 | `%tky`, `%param-discount_percent` | 위와 같음 |
| `{ default function GetDefaultsFordeductDiscount; }` | `FOR READ … FOR FUNCTION Travel~GetDefaultsFordeductDiscount RESULT result` | `%tky` | `result-%param`(파라미터 구조) |
| `repeatable action addServiceFee result [1] $self` | `FOR MODIFY … FOR ACTION Travel~addServiceFee RESULT result` | `%cid`, `%tky` | `result` |
| `update ( features : instance )` 등 | `FOR INSTANCE FEATURES … RESULT result` | `%tky` | `result`(`%features`, `%action`, `%assoc`) |

- 호출 시점: 액션은 소비자가 실행할 때(Fiori 버튼, `MODIFY ENTITIES … EXECUTE`). 프레임워크가 먼저 잠금(`lock master`)과 권한, 기능 제어를 확인한 뒤 호출합니다. `get_instance_features`는 Fiori가 화면을 읽을 때와 작업 실행 전에 호출됩니다.

**자주 나는 오류와 해결**

- 액션 실행 후 화면이 갱신되지 않음 → `result`를 채우지 않았습니다.
- 할인 후 BookingFee가 0이 됨 → 정수 나눗셈. `decfloat16` 변수를 쓰세요.

</details>

#### 7단계. 팩토리 액션: copyTravel, static default factory createTravel, create 기본값 함수

요구사항

1. `copyTravel`: **인스턴스 팩토리 액션** `[1]`. 선택한 Travel을 복사해 새 Travel을 만들고, 그 Travel의 Booking도 모두 복사합니다.
   - 새 Travel: Agency/Customer/BookingFee/Currency 복사, 날짜는 오늘+1~오늘+15, 설명 `Copy of <원본번호>`. TravelID·TotalPrice·OverallStatus는 넘기지 않음(late numbering, 결정이 채움).
   - 새 Booking: Customer/Carrier/Connection/FlightDate/FlightPrice/Currency 복사, 상태 N.
   - 호출자의 `%cid`로 새 Travel을 만들고, Booking은 `%cid_ref`로 그 Travel을 가리켜 `CREATE BY \_Booking`. `%param-%is_draft`를 그대로 넘겨 draft/활성 어느 쪽으로 만들지 따릅니다. 결과는 `MAPPED mapped`.
2. `createTravel`: `static default factory action … parameter ZRAP_A_CREATE_TRAVEL_### [1]`. 파라미터의 고객·여행사·항공편으로 Travel 1건 + Booking 1건을 만듭니다. 항공료와 통화는 `/DMO/FLIGHT`에서 한 번에 조회합니다. 시작·종료일은 비행일로.
3. `create { default function GetDefaultsForCreate; }`: 표준 create의 기본값 함수. 내가 마지막으로 만든 Travel의 여행사, 통화 EUR, 오늘+7~오늘+14를 제안합니다.

**확인**

- 활성화 성공.
- (12단계 후) Fiori 목록에서 Travel 하나를 선택하고 **Copy Travel** → 새 draft Object Page가 열리고 Booking까지 복사되어 있음.
- (12단계 후) 목록의 **Create** → 이제 표준 빈 화면 대신 `createTravel` 파라미터 팝업(고객, 여행사, 항공사, 연결편, 비행일)이 뜸 → 확인하면 Booking 1건이 든 Travel draft가 열림.

<details><summary>정답·해설</summary>

BDEF (Travel):

```bdef
  // create의 기본값 함수 (기존 'create;'를 교체)
  create { default function GetDefaultsForCreate; }

  // 인스턴스 팩토리 액션: 결과는 result가 아니라 mapped. 카디널리티 [1]
  factory action copyTravel [1];

  // 정적(인스턴스 없음) + default: Fiori의 '만들기'가 표준 create 대신 이 액션을 호출
  static default factory action createTravel parameter ZRAP_A_CREATE_TRAVEL_### [1];
```

`lhc_travel` 선언:

```abap
    METHODS copyTravel FOR MODIFY
      IMPORTING keys FOR ACTION Travel~copyTravel.

    METHODS createTravel FOR MODIFY
      IMPORTING keys FOR ACTION Travel~createTravel.

    METHODS GetDefaultsForCreate FOR READ
      IMPORTING keys FOR FUNCTION Travel~GetDefaultsForCreate RESULT result.
```

구현:

```abap
  METHOD copyTravel.
    DATA travels_cba TYPE TABLE FOR CREATE zrap_r_travel_###\\Travel.
    DATA bookings_cba TYPE TABLE FOR CREATE zrap_r_travel_###\\Travel\_Booking.

    " 팩토리 액션은 호출자가 %cid를 반드시 줘야 함 (mapped로 돌려줄 연결 고리)
    ASSERT NOT line_exists( keys[ %cid = '' ] ).

    " 원본 Travel
    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        ALL FIELDS WITH CORRESPONDING #( keys )
      RESULT DATA(travels).

    " 원본 Booking + 어떤 Travel의 것인지 링크
    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel BY \_Booking
        ALL FIELDS WITH CORRESPONDING #( travels )
      LINK DATA(booking_links)
      RESULT DATA(bookings).

    DATA(today) = cl_abap_context_info=>get_system_date( ).

    LOOP AT travels INTO DATA(travel).
      DATA(key) = keys[ KEY id %tky = travel-%tky ].

      " 새 Travel: 키(TravelID)는 late numbering이 채우므로 넘기지 않음
      APPEND VALUE #( %cid      = key-%cid
                      %is_draft = key-%param-%is_draft
                      %data     = CORRESPONDING #( travel EXCEPT TravelID TotalPrice OverallStatus ) )
        TO travels_cba ASSIGNING FIELD-SYMBOL(<new_travel>).
      <new_travel>-BeginDate   = today + 1.
      <new_travel>-EndDate     = today + 15.
      <new_travel>-Description = |Copy of { travel-TravelID ALPHA = OUT }|.

      " 새 Booking들: 부모는 %cid_ref로 '방금 만든 Travel'을 가리킴
      APPEND VALUE #( %cid_ref  = key-%cid
                      %is_draft = key-%param-%is_draft ) TO bookings_cba ASSIGNING FIELD-SYMBOL(<cba>).
      LOOP AT booking_links INTO DATA(link) USING KEY id WHERE source-%tky = travel-%tky.
        DATA(booking) = bookings[ KEY id %tky = link-target-%tky ].
        APPEND VALUE #( %cid          = |{ key-%cid }_{ booking-BookingID }|
                        %is_draft     = key-%param-%is_draft
                        CustomerID    = booking-CustomerID
                        CarrierID     = booking-CarrierID
                        ConnectionID  = booking-ConnectionID
                        FlightDate    = booking-FlightDate
                        FlightPrice   = booking-FlightPrice
                        CurrencyCode  = booking-CurrencyCode
                        BookingStatus = booking_status-new ) TO <cba>-%target.
      ENDLOOP.
    ENDLOOP.

    MODIFY ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        CREATE FIELDS ( AgencyID CustomerID BeginDate EndDate BookingFee CurrencyCode Description )
          WITH travels_cba
        CREATE BY \_Booking
          FIELDS ( CustomerID CarrierID ConnectionID FlightDate FlightPrice CurrencyCode BookingStatus )
          WITH bookings_cba
      MAPPED mapped      " %cid ↔ 새 인스턴스(%pid) 연결을 호출자에게 돌려줌
      FAILED failed
      REPORTED reported.
  ENDMETHOD.

  METHOD createTravel.
    CHECK keys IS NOT INITIAL.

    " 항공편 가격/통화를 한 번에 조회
    SELECT FROM /dmo/flight
      FIELDS carrier_id, connection_id, flight_date, price, currency_code
      FOR ALL ENTRIES IN @keys
      WHERE carrier_id    = @keys-%param-carrier_id
        AND connection_id = @keys-%param-connection_id
        AND flight_date   = @keys-%param-flight_date
      INTO TABLE @DATA(flights).

    MODIFY ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        CREATE FIELDS ( CustomerID AgencyID BeginDate EndDate Description )
          WITH VALUE #( FOR key IN keys
                        ( %cid        = key-%cid
                          %is_draft   = key-%param-%is_draft
                          CustomerID  = key-%param-customer_id
                          AgencyID    = key-%param-agency_id
                          BeginDate   = key-%param-flight_date
                          EndDate     = key-%param-flight_date
                          Description = 'Created with createTravel' ) )
        CREATE BY \_Booking
          FIELDS ( CustomerID CarrierID ConnectionID FlightDate FlightPrice CurrencyCode )
          WITH VALUE #( FOR key IN keys INDEX INTO i
                        ( %cid_ref  = key-%cid
                          %is_draft = key-%param-%is_draft
                          %target   = VALUE #( ( %cid         = |CBA_{ i }|
                                                     %is_draft    = key-%param-%is_draft
                                                     CustomerID   = key-%param-customer_id
                                                     CarrierID    = key-%param-carrier_id
                                                     ConnectionID = key-%param-connection_id
                                                     FlightDate   = key-%param-flight_date
                                                     FlightPrice  = VALUE #( flights[ carrier_id    = key-%param-carrier_id
                                                                                      connection_id = key-%param-connection_id
                                                                                      flight_date   = key-%param-flight_date ]-price OPTIONAL )
                                                     CurrencyCode = VALUE #( flights[ carrier_id    = key-%param-carrier_id
                                                                                      connection_id = key-%param-connection_id
                                                                                      flight_date   = key-%param-flight_date ]-currency_code OPTIONAL ) ) ) ) )
      MAPPED mapped
      FAILED failed
      REPORTED reported.
  ENDMETHOD.

  METHOD GetDefaultsForCreate.
    " 내가 마지막으로 만든 Travel의 여행사를 제안
    SELECT FROM zrap_atrav_###
      FIELDS agency_id
      WHERE created_by = @( cl_abap_context_info=>get_user_technical_name( ) )
      ORDER BY created_at DESCENDING
      INTO TABLE @DATA(last_agencies)
      UP TO 1 ROWS.

    DATA(today) = cl_abap_context_info=>get_system_date( ).

    result = VALUE #( FOR key IN keys
                      ( %cid                = key-%cid
                        %param-AgencyID     = VALUE #( last_agencies[ 1 ]-agency_id OPTIONAL )
                        %param-CurrencyCode = c_default_currency
                        %param-BeginDate    = today + 7
                        %param-EndDate      = today + 14 ) ).
  ENDMETHOD.
```

**왜 이렇게 쓰나**

- **팩토리 액션은 `RESULT`가 없고 `mapped`로 답합니다.** 소비자가 준 `%cid`와 새로 생긴 인스턴스(late numbering에서는 임시 키 `%pid`)의 짝을 `mapped-travel`에 돌려줘야 Fiori가 새 Object Page로 이동할 수 있습니다. 그래서 `MODIFY … MAPPED mapped`로 프레임워크가 만든 매핑을 그대로 넘깁니다. 호출자가 `%cid`를 안 주면 연결할 수 없으므로 RAP100처럼 `ASSERT`로 막았습니다.
- **`%cid` / `%cid_ref`**: 한 MODIFY 안에서 "방금 CREATE한 Travel"에 Booking을 붙이려면 아직 키가 없으므로, Travel의 `%cid`를 Booking 생성 쪽 `%cid_ref`에 적어 참조합니다. Booking 자신의 `%cid`도 요청 안에서 유일해야 해서 `원본cid_예약번호`로 만들었습니다.
- **`%param-%is_draft`**: 팩토리 액션의 파라미터에는 `%is_draft`가 자동으로 들어 있습니다. Fiori는 draft로 만들라고(`mk-on`) 보내고, EML 호출자는 활성으로 만들 수도 있습니다. 이 값을 새 인스턴스의 `%is_draft`에 그대로 넘깁니다.
- **static default factory action**: `default`는 엔터티당 하나의 정적 팩토리 액션에만 붙일 수 있고, OData/Fiori가 "만들기"의 기본 동작으로 씁니다(RAP110 ex07). 그래서 이 단계 후 Fiori의 Create는 파라미터 팝업을 띄웁니다. 결과적으로 `GetDefaultsForCreate`(표준 create의 기본값)는 Fiori Create 버튼에서는 보이지 않게 됩니다. 표준 create 기본값을 화면에서 보고 싶으면 `createTravel`에서 `default`를 잠시 빼고 확인하세요.
- **create 기본값 함수**: 문법 `create { default function GetDefaultsForCreate; }`는 BDL 치트시트(36)에 있는 형식입니다. 구현 메서드의 `keys`/`result` 구조(정적이라 `%cid`, 결과 `%param`이 엔터티 필드 구조라는 부분)는 공식 예제 코드를 찾지 못했습니다. BDEF에서 Ctrl+1로 메서드를 생성한 뒤 F2로 `result` 타입을 확인하고 맞추세요 (실제 시스템에서 확인 필요).
- 생성된 Travel/Booking에는 3단계 결정이 그대로 돌아 상태 O, 예약일, 총액이 채워집니다. 팩토리 액션에서 그 값을 직접 넣지 않는 이유입니다.

**클래스 구조 해설**

- `factory action copyTravel [1]` → `FOR MODIFY … FOR ACTION Travel~copyTravel` (RESULT 없음). keys 한 줄: `%cid`, `%tky`, `%param-%is_draft`. 응답: `mapped`, `failed`, `reported`.
- `static default factory action createTravel parameter X [1]` → keys 한 줄: `%cid`, `%param`(X의 요소 + `%is_draft`). 인스턴스가 없으므로 `%tky`가 없습니다.
- `default function GetDefaultsForCreate` → `FOR READ … FOR FUNCTION Travel~GetDefaultsForCreate RESULT result`.
- 호출 시점: Fiori 버튼(Copy/Create) 또는 EML `MODIFY ENTITIES … EXECUTE copyTravel FROM VALUE #( ( %cid = '…' %tky = … ) ) MAPPED …`. late numbering이라 최종 TravelID는 저장 시 `adjust_numbers`에서 정해집니다.

**자주 나는 오류와 해결**

- Copy 후 Object Page로 이동하지 않음 → `mapped`를 채우지 않았거나 `%cid`를 소비자 값과 다르게 넣었습니다.
- "Only one default factory action is allowed" 류의 오류 → `default`를 두 액션에 붙였습니다.

</details>

#### 8단계. 함수: 인스턴스 함수 getDaysToFlight, 정적 함수 getOpenTravelCount, EML로 확인

요구사항

1. Booking에 인스턴스 함수 `getDaysToFlight result [1] ZRAP_A_DAYS_TO_FLIGHT_###`.
   - `initial_days_to_flight = FlightDate - BookingDate`(음수면 0), `remaining_days_to_flight = FlightDate - 오늘`(음수면 0), `days_to_flight_indicator`: 남은 일수 6 이상 3, 3~5는 2, 0~2는 1, 지났으면 0.
2. Travel에 정적 함수 `getOpenTravelCount result [1] ZRAP_A_TRAVEL_STAT_###`: 활성 Travel의 상태별 건수(O/A/X). DB 집계 SELECT 한 번.
3. 함수는 데이터를 바꾸지 않습니다(`FOR READ`). 잠금도 하지 않습니다.
4. 콘솔 클래스 `ZCL_RAP_R02_CHECK_###`(`if_oo_adt_classrun`)를 만들어 다음을 출력하세요.
   - `getOpenTravelCount` 결과.
   - 최근 Booking 3건의 `getDaysToFlight` 결과.
   - 가장 최근 Travel 하나에 `addServiceFee`를 `%cid` 두 개로 **한 요청에서 두 번** 실행하고, 결과 BookingFee 두 줄을 출력한 뒤 `ROLLBACK ENTITIES`(저장하지 않음).

**확인**

- F9 실행 → 콘솔에 "Open: n / Accepted: n / Rejected: n", Booking별 남은 일수, addServiceFee 결과 두 줄(같은 Travel, 수수료가 원래+20)이 출력됩니다.
- 해당 Travel에 draft가 열려 있으면 addServiceFee는 잠금 때문에 실패하고 failed가 출력됩니다(정상 동작).

<details><summary>정답·해설</summary>

BDEF:

```bdef
  // Travel: 정적 함수 (인스턴스 없음)
  static function getOpenTravelCount result [1] ZRAP_A_TRAVEL_STAT_###;
```

```bdef
  // Booking: 인스턴스 함수
  function getDaysToFlight result [1] ZRAP_A_DAYS_TO_FLIGHT_###;
```

`lhc_travel` 선언과 구현:

```abap
    METHODS getOpenTravelCount FOR READ
      IMPORTING keys FOR FUNCTION Travel~getOpenTravelCount RESULT result.
```

```abap
  METHOD getOpenTravelCount.
    SELECT FROM zrap_atrav_###
      FIELDS overall_status, COUNT( * ) AS cnt
      GROUP BY overall_status
      INTO TABLE @DATA(counts).

    result = VALUE #( FOR key IN keys
                      ( %cid                  = key-%cid
                        %param-open_count     = VALUE #( counts[ overall_status = travel_status-open ]-cnt OPTIONAL )
                        %param-accepted_count = VALUE #( counts[ overall_status = travel_status-accepted ]-cnt OPTIONAL )
                        %param-rejected_count = VALUE #( counts[ overall_status = travel_status-rejected ]-cnt OPTIONAL ) ) ).
  ENDMETHOD.
```

`lhc_booking` 선언과 구현:

```abap
    METHODS getDaysToFlight FOR READ
      IMPORTING keys FOR FUNCTION Booking~getDaysToFlight RESULT result.
```

```abap
  METHOD getDaysToFlight.
    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Booking
        FIELDS ( BookingDate FlightDate )
        WITH CORRESPONDING #( keys )
      RESULT DATA(bookings)
      FAILED failed.

    DATA(today) = cl_abap_context_info=>get_system_date( ).

    LOOP AT bookings INTO DATA(booking).
      DATA(initial_days)   = COND i( WHEN booking-FlightDate IS INITIAL OR booking-BookingDate IS INITIAL THEN 0
                                     ELSE booking-FlightDate - booking-BookingDate ).
      DATA(remaining_days) = COND i( WHEN booking-FlightDate IS INITIAL THEN -1
                                     ELSE booking-FlightDate - today ).

      APPEND VALUE #( %tky                            = booking-%tky
                      %param-initial_days_to_flight   = nmax( val1 = initial_days val2 = 0 )
                      %param-remaining_days_to_flight = nmax( val1 = remaining_days val2 = 0 )
                      " 1 = 빨강(0~2일), 2 = 주황(3~5일), 3 = 초록(6일 이상), 0 = 지남/모름
                      %param-days_to_flight_indicator = COND #( WHEN remaining_days >= 6 THEN 3
                                                                WHEN remaining_days >= 3 THEN 2
                                                                WHEN remaining_days >= 0 THEN 1
                                                                ELSE 0 ) ) TO result.
    ENDLOOP.
  ENDMETHOD.
```

확인용 콘솔 클래스:

```abap
CLASS zcl_rap_r02_check_### DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_oo_adt_classrun.
ENDCLASS.


CLASS zcl_rap_r02_check_### IMPLEMENTATION.

  METHOD if_oo_adt_classrun~main.

    "--- 1) 정적 함수: 인스턴스 키 대신 %cid만 줌
    READ ENTITIES OF zrap_r_travel_###
      ENTITY Travel
        EXECUTE getOpenTravelCount
        FROM VALUE #( ( %cid = 'STAT' ) )
      RESULT DATA(stats)
      FAILED DATA(stat_failed).

    LOOP AT stats INTO DATA(stat).
      out->write( |Open: { stat-%param-open_count } / Accepted: { stat-%param-accepted_count } / Rejected: { stat-%param-rejected_count }| ).
    ENDLOOP.

    "--- 2) 인스턴스 함수: 최근 Booking 3건
    SELECT FROM zrap_abook_###
      FIELDS travel_id, booking_id
      ORDER BY travel_id DESCENDING, booking_id DESCENDING
      INTO TABLE @DATA(last_bookings)
      UP TO 3 ROWS.

    IF last_bookings IS NOT INITIAL.
      READ ENTITIES OF zrap_r_travel_###
        ENTITY Booking
          EXECUTE getDaysToFlight
          FROM VALUE #( FOR b IN last_bookings ( %is_draft         = if_abap_behv=>mk-off
                                                 %key-TravelID     = b-travel_id
                                                 %key-BookingID    = b-booking_id ) )
        RESULT DATA(days)
        FAILED DATA(days_failed).

      LOOP AT days INTO DATA(day).
        out->write( |Travel { day-TravelID } / Booking { day-BookingID }: | &&
                    |initial { day-%param-initial_days_to_flight }, remaining { day-%param-remaining_days_to_flight }, | &&
                    |indicator { day-%param-days_to_flight_indicator }| ).
      ENDLOOP.
    ENDIF.

    "--- 3) 반복 가능 액션: 같은 Travel에 두 번 (%cid로 실행 구분)
    SELECT SINGLE FROM zrap_atrav_### FIELDS MAX( travel_id ) INTO @DATA(last_travel_id).
    IF last_travel_id IS NOT INITIAL.
      MODIFY ENTITIES OF zrap_r_travel_###
        ENTITY Travel
          EXECUTE addServiceFee
          FROM VALUE #( ( %cid = 'FEE_1' %is_draft = if_abap_behv=>mk-off %key-TravelID = last_travel_id )
                        ( %cid = 'FEE_2' %is_draft = if_abap_behv=>mk-off %key-TravelID = last_travel_id ) )
        RESULT DATA(fee_result)
        FAILED DATA(fee_failed)
        REPORTED DATA(fee_reported).

      IF fee_failed IS NOT INITIAL.
        out->write( |addServiceFee failed for travel { last_travel_id } (draft lock?)| ).
      ENDIF.
      LOOP AT fee_result INTO DATA(fee).
        out->write( |addServiceFee: travel { fee-TravelID } booking fee now { fee-%param-BookingFee }| ).
      ENDLOOP.

      " 확인만 하고 저장하지 않음
      ROLLBACK ENTITIES.
    ENDIF.

  ENDMETHOD.

ENDCLASS.
```

**왜 이렇게 쓰나**

- **함수 vs 액션**: 함수는 값을 계산해 돌려주기만 하고 데이터를 바꾸지 않으므로 `FOR READ` 메서드이고 EML도 `READ ENTITIES … EXECUTE`입니다. 프레임워크는 함수에 잠금을 걸지 않습니다. 반대로 액션은 `FOR MODIFY`, `MODIFY ENTITIES … EXECUTE`.
- **인스턴스 함수 `getDaysToFlight`**: RAP110 ex10과 같은 이름·목적입니다. RAP110은 가상 요소 계산 클래스를 함수 안에서 재사용하지만 여기서는 계산을 메서드 안에 직접 넣었습니다(가상 요소는 R-01의 `ZCL_RAP_TRAV_VE_###`가 담당).
- **정적 함수 `getOpenTravelCount`**: 인스턴스가 없으니 `keys`에는 `%cid`만 있습니다. 집계는 RAP 버퍼가 아니라 DB의 활성 데이터 기준입니다(draft나 아직 저장 안 한 변경은 포함되지 않음 — 함수 목적에 맞는 선택). 정적 함수의 keys/result에 `%cid`가 있다는 부분은 정적 액션 규칙과 같다고 보고 작성했습니다 (실제 시스템에서 확인 필요).
- **repeatable 확인**: 같은 `%key`에 `%cid`만 다른 두 줄을 한 MODIFY로 보냅니다. `repeatable`이 없었다면 두 번째 줄이 거부됩니다.
- `ROLLBACK ENTITIES`로 트랜잭션 버퍼를 비워 실제 저장을 하지 않습니다.

**클래스 구조 해설**

- `function getDaysToFlight result [1] X` → `METHODS … FOR READ IMPORTING keys FOR FUNCTION Booking~getDaysToFlight RESULT result`. keys 한 줄 `%tky`, 결과 한 줄 `%tky` + `%param`(X 구조). 응답은 `failed`, `reported`.
- `static function getOpenTravelCount result [1] X` → 같은 형태, keys에 `%tky` 대신 `%cid`.
- 함수 결과는 OData에서 바운드/언바운드 함수로 노출됩니다(12단계 `use function`).

**자주 나는 오류와 해결**

- `EXECUTE`를 `MODIFY ENTITIES`에 썼더니 오류 → 함수는 `READ ENTITIES … EXECUTE`입니다.
- getDaysToFlight 결과가 비어 있음 → 활성 인스턴스를 읽을 때 `%is_draft = if_abap_behv=>mk-off`를 주세요(draft BO에서 `%is_draft`는 키의 일부).

</details>

#### 9단계. determine action과 사이드 이펙트

요구사항

1. Travel에 `determine action checkDates { validation validateDates; }`를 정의하세요. 구현 메서드는 필요 없습니다.
2. Travel 사이드 이펙트:
   - `BookingFee`나 `CurrencyCode`가 바뀌면 `TotalPrice`를 다시 읽게.
   - `BeginDate`, `EndDate`가 바뀌면 `checkDates`를 실행하고 **메시지**를 다시 읽게(저장 전에 날짜 오류가 바로 뜸).
   - `acceptTravel`, `rejectTravel` 실행 후에는 세 액션(accept, reject, deductDiscount)의 **권한/기능 제어(permissions)** 와 메시지를 다시 읽게.
   - `addServiceFee`, `deductDiscount` 실행 후 `TotalPrice`를 다시 읽게.
3. Booking 사이드 이펙트: `FlightPrice`, `CurrencyCode`가 바뀌면 부모 Travel의 `TotalPrice`(`_Travel.TotalPrice`)를 다시 읽게.
4. 해설에 사이드 이펙트 **대상(target)** 의 종류 다섯 가지(field, entity, permissions, messages, $self)를 표로 정리하세요.
5. 사이드 이펙트는 프로젝션 BDEF에 `use side effects;`가 있어야 서비스에 나갑니다(12단계).

**확인** (12단계에서 노출 후)

- Draft에서 Booking Fee를 바꾸고 다른 필드로 이동하면 **저장하지 않아도** Total Price가 즉시 바뀝니다.
- Begin Date를 어제로 바꾸고 이동하면 저장 전에 바로 메시지 006이 뜨고 필드가 빨갛게 됩니다. 고치면 메시지가 사라집니다.
- Booking의 Flight Price를 바꾸면 헤더의 Total Price가 즉시 바뀝니다.
- Accept Travel 후 Accept/Deduct Discount 버튼이 바로 비활성화됩니다.

<details><summary>정답·해설</summary>

BDEF (Travel):

```bdef
  // 검증을 '필요할 때' 실행시키는 액션. on save 검증/결정만 넣을 수 있음
  determine action checkDates { validation validateDates; }

  side effects
  {
    // 필드 → 필드
    field BookingFee affects field TotalPrice;
    field CurrencyCode affects field TotalPrice;
    // 필드 변경 시 determine action 실행 → 메시지 다시 읽기
    determine action checkDates executed on field BeginDate, field EndDate affects messages;
    // 액션 → 기능 제어(버튼 상태) + 메시지 다시 읽기
    action acceptTravel affects permissions ( action acceptTravel, action rejectTravel, action deductDiscount ), messages;
    action rejectTravel affects permissions ( action acceptTravel, action rejectTravel, action deductDiscount ), messages;
    // 액션 → 필드
    action addServiceFee affects field TotalPrice;
    action deductDiscount affects field TotalPrice;
  }
```

BDEF (Booking):

```bdef
  side effects
  {
    // 대상이 다른 엔터티의 필드: 연관 경로로 지정
    field FlightPrice affects field _Travel.TotalPrice;
    field CurrencyCode affects field _Travel.TotalPrice;
  }
```

행동 풀 변경은 없습니다. determine action은 프레임워크가 등록된 검증(`validateDates`)을 대신 호출하고, 사이드 이펙트는 순수하게 UI(OData 메타데이터)용 선언입니다.

**왜 이렇게 쓰나**

- **determine action**: 검증·결정은 원래 저장 때만 돌기 때문에, 사용자는 Save를 눌러야 날짜 오류를 봅니다. `determine action checkDates`는 "지금 이 검증을 실행하라"는 액션이고, 사이드 이펙트 `determine action checkDates executed on field BeginDate, field EndDate affects messages`가 날짜 필드가 바뀔 때 Fiori가 이 액션을 자동 호출하고 메시지를 다시 읽게 만듭니다(RAP110 ex09, Flight Reference Scenario의 `validateDateRange`). determine action에는 `on save` 결정·검증만 넣을 수 있고, 결정이 먼저, 검증이 나중에 실행됩니다. 트리거 조건이 맞을 때만 실행되며 `determination ( always ) X;`로 강제할 수 있습니다(치트시트 36).
- **사이드 이펙트**: Fiori Elements는 필드 하나를 바꿔도 기본적으로 그 필드만 서버에 보내고 나머지는 다시 읽지 않습니다. 서버의 결정이 `TotalPrice`를 바꿔도 화면은 옛 값 그대로입니다. 사이드 이펙트는 "A가 바뀌면 B를 다시 읽어라"를 OData 메타데이터로 알려 줍니다. 구현 코드는 필요 없습니다.
- **permissions 대상**: accept 후 상태가 A가 되면 `get_instance_features` 결과가 바뀌지만, Fiori는 버튼 상태를 다시 묻지 않으면 모릅니다. `affects permissions ( action … )`가 기능 제어·권한을 다시 읽게 합니다. 괄호 안에 여러 대상을 쉼표로 나열한 형식은 치트시트의 단일 대상 예(`permissions(action act2)`)를 확장한 것입니다. 활성화 오류가 나면 액션마다 한 대상씩 줄여 쓰세요 (실제 시스템에서 확인 필요).
- `acceptTravel`은 `result [1] $self`라 인스턴스 데이터 자체는 결과로 갱신됩니다. 그래서 필드 대상은 생략하고 permissions·messages만 지정했습니다.

**사이드 이펙트 대상 정리** (치트시트 36 기준)

| 대상 | 쓰는 형식(예) | 다시 읽는 것 | 이 BO에서 |
|---|---|---|---|
| field | `affects field TotalPrice`, `field _Travel.TotalPrice`, `field *` | 지정 필드(연관 경로로 다른 엔터티 필드도), `*`는 같은 인스턴스 전체 필드 | 총액 |
| entity | `affects entity _Booking` | 연관된 엔터티(자식 표 등) 전체 | 사용 안 함. 예: 헤더 액션이 모든 Booking 상태를 바꾸면 `action X affects entity _Booking` |
| permissions | `affects permissions ( action acceptTravel )`, `permissions ( field X )`, `permissions ( create _Booking )` | 기능 제어·권한 결과(버튼/필드 활성 여부) | accept/reject 후 버튼 |
| messages | `affects messages` | 보고된 메시지 전체 | 날짜 검증 |
| $self | 대상으로 쓰면 자기 엔터티 전체 다시 읽기. 트리거로 쓰면(`$self affects …`) 이 엔터티에 CUD가 일어날 때 | 자기 엔터티 | 사용 안 함. 예: Booking에서 `$self affects field _Travel.TotalPrice`(Booking 생성·삭제 시 부모 총액 다시 읽기). 정확한 대상 문법은 (실제 시스템에서 확인 필요) |

트리거(왼쪽) 종류: `field …`, `action …`, `determine action … executed on …`, `$self`, `event …`(business event for side effects).

**클래스 구조 해설** determine action은 파생 타입 `TABLE FOR ACTION IMPORT … ~checkDates`를 가진 액션이라 EML로도 실행할 수 있지만(`MODIFY ENTITIES … EXECUTE checkDates`), 행동 풀에는 메서드가 생기지 않습니다. 실행되면 프레임워크가 `validateDates` 메서드를 호출하고, 그 결과(`failed`/`reported`)가 액션의 응답이 됩니다.

**자주 나는 오류와 해결**

- 사이드 이펙트가 동작하지 않음 → 프로젝션 BDEF에 `use side effects;`를 빠뜨렸거나, 브라우저가 옛 메타데이터를 캐시하고 있습니다. Preview를 새로 열고 Ctrl+F5.
- `determine action`에 `on modify` 결정을 넣으면 활성화 오류 → on save만 가능합니다.

</details>

#### 10단계. Draft 심화: Edit(기능 제어), Activate optimized, Discard, Resume(추가 구현), Prepare, total etag

요구사항

1. Draft 액션 선언을 다음처럼 바꾸세요.
   - `Edit`의 `features : instance`는 6단계에서 이미 붙였습니다(승인된 Travel은 Edit 불가). 여기서는 그대로 둡니다.
   - `Activate optimized`, `Discard`는 그대로.
   - `Resume with additional implementation` → 잠금이 만료된 draft를 다시 편집할 때, 그 사이 **활성 Travel이 승인(A)되었으면** 실패시키고 메시지 015를 냅니다.
   - `Prepare`는 4단계에서 채운 그대로.
2. 각 Draft 액션이 언제 실행되고 무엇을 하는지, `%is_draft`가 키에 왜 있는지, `total etag`가 왜 필요한지 해설에 적으세요.

**확인**

- 승인된 Travel을 열면 **Edit** 버튼이 비활성입니다.
- Resume 확인(시간이 걸림): Travel A를 Edit해 draft를 만든 뒤 브라우저를 닫습니다. draft 잠금이 만료될 때까지 기다린 다음(시스템 설정에 따라 수 분~), 8단계 콘솔 클래스처럼 EML로 **활성** Travel A에 `acceptTravel`을 실행하고 `COMMIT ENTITIES`합니다. 다시 Fiori에서 A의 draft를 열어 필드를 바꾸면 Resume이 호출되어 메시지 015가 뜹니다. 이 시나리오는 잠금 만료 시간 때문에 트라이얼에서 재현이 어려울 수 있습니다 (실제 시스템에서 확인 필요).

<details><summary>정답·해설</summary>

BDEF (Travel) — R-01의 Draft 액션 줄을 아래로 교체:

```bdef
  draft action ( features : instance ) Edit;            // 동적 기능 제어 대상
  draft action Activate optimized;                       // 필요한 결정/검증만 실행 (성능)
  draft action Discard;
  draft action Resume with additional implementation;    // 프레임워크 동작 + 내 코드
  draft determine action Prepare
  {
    determination setDefaultDescription;
    validation validateCustomer;
    validation validateAgency;
    validation validateDates;
    validation Booking~validateConnection;
    validation Booking~validateStatus;
  }
```

`lhc_travel` 선언과 구현:

```abap
    METHODS Resume FOR MODIFY
      IMPORTING keys FOR ACTION Travel~Resume.
```

```abap
  METHOD Resume.
    " 아직 활성화된 적 없는 새 draft는 TravelID가 비어 있음 → 확인 대상 아님
    DATA active_keys TYPE TABLE FOR READ IMPORT zrap_r_travel_###\\Travel.
    active_keys = VALUE #( FOR key IN keys WHERE ( TravelID IS NOT INITIAL )
                           ( %is_draft = if_abap_behv=>mk-off
                             %key      = key-%key ) ).
    CHECK active_keys IS NOT INITIAL.

    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        FIELDS ( TravelID OverallStatus )
        WITH active_keys
      RESULT DATA(active_travels).

    LOOP AT active_travels INTO DATA(active) WHERE OverallStatus = travel_status-accepted.
      APPEND VALUE #( %is_draft = if_abap_behv=>mk-on
                      %key      = active-%key
                      %fail     = VALUE #( cause = if_abap_behv=>cause-disabled ) ) TO failed-travel.
      APPEND VALUE #( %is_draft = if_abap_behv=>mk-on
                      %key      = active-%key
                      %msg      = NEW zcm_rap_###( textid    = zcm_rap_###=>travel_accepted_meanwhile
                                                   travel_id = active-TravelID
                                                   severity  = if_abap_behv_message=>severity-error ) )
        TO reported-travel.
    ENDLOOP.
  ENDMETHOD.
```

**Draft 액션 정리**

| 액션 | 언제 | 하는 일 |
|---|---|---|
| `Edit` | 활성 인스턴스에서 **Edit** 버튼 | 활성 데이터를 draft 테이블로 복사하고, 활성 인스턴스에 배타 잠금(exclusive lock)을 겁니다. `features : instance`면 `get_instance_features`의 `%action-Edit`로 막을 수 있습니다. |
| `Activate` | draft에서 **Save** | 먼저 `Prepare`를 실행하고, 오류가 없으면 draft 내용을 활성 테이블에 저장(save sequence, late numbering이면 `adjust_numbers`)한 뒤 draft를 지웁니다. `optimized`는 draft 단계에서 이미 돈 결정·검증을 다시 돌리지 않아 빠릅니다(치트시트 36). |
| `Discard` | draft에서 **Discard Draft** | draft 행을 지우고 잠금을 풉니다. 활성 데이터는 그대로. |
| `Resume` | 잠금이 만료된 draft를 다시 수정할 때 자동 | 활성 인스턴스 잠금을 다시 겁니다. `with additional implementation`이면 그 뒤 내 메서드가 호출되어 추가 검사를 할 수 있습니다. |
| `Prepare` | Activate 직전(또는 소비자가 직접) | 등록된 on save 결정과 검증을 draft 데이터에 실행합니다. 여기 없는 검증은 draft 단계에서 돌지 않습니다. |

**왜 이렇게 쓰나**

- **%is_draft**: Draft BO에서는 같은 키(TravelID)에 활성/draft 두 인스턴스가 있을 수 있어서, 모든 파생 타입의 "전송 키" `%tky`에 `%is_draft`가 들어갑니다. 그래서 정답 코드 전체가 `%key`가 아니라 `%tky`를 씁니다. late numbering BO에서는 새 draft에 아직 TravelID가 없으므로 임시 키 `%pid`(draft 테이블의 `DRAFTUUID`)도 `%tky`에 포함되어 인스턴스를 구분합니다.
- **total etag**: 활성 인스턴스용 etag(`etag master LocalLastChangedAt`)는 "draft 안에서 바꾸는 동안"의 충돌을 봅니다. `total etag LastChangedAt`은 "draft를 만든 뒤 활성 데이터가 다른 경로로 바뀌었는가"를 Activate/Resume 때 비교하는 값입니다. Draft BO에서 strict 모드가 요구하며, `LastChangedAt` 필드는 활성 데이터가 바뀔 때마다 갱신되어야 합니다(R-01에서 `@Semantics.systemDateTime.lastChangedAt`).
- **Resume 추가 구현의 의미**: 잠금이 만료된 사이 다른 경로(EML, Web API 바인딩 `ZRAP_API_TRAVEL_O4_###` 등)로 활성 Travel이 승인되었을 수 있습니다. 그 상태로 draft 편집을 이어 가면 승인된 여행을 덮어쓰게 되므로 Resume에서 막고 "draft를 버리라"는 메시지를 줍니다. 코드는 Flight Reference Scenario `/DMO/BP_TRAVEL_D`의 `resume`처럼 `%is_draft`를 바꿔 활성 인스턴스를 읽는 방식을 따랐습니다. 아직 한 번도 활성화되지 않은 새 draft는 TravelID가 비어 있으므로 건너뜁니다.
- `%fail-cause = if_abap_behv=>cause-disabled`: "작업을 지금 할 수 없음"을 뜻하는 원인 코드입니다. 원인 코드를 채우면 소비자(OData)가 실패 이유를 HTTP 상태로 구분할 수 있습니다.
- Draft 쿼리(목록에서 draft만 거르기 등)는 `ZRAP_C_TRAVEL_###`의 프로젝션 BDEF `use draft;`로 자동 제공되므로 이 문제에서 따로 구현하지 않습니다.

**클래스 구조 해설**

- `draft action Resume with additional implementation` → `METHODS Resume FOR MODIFY IMPORTING keys FOR ACTION Travel~Resume.` (결과 없음, 응답 `failed`/`reported`/`mapped`). `with additional implementation`이 없으면 메서드를 만들 수 없습니다.
- `draft action ( features : instance ) Edit` → 메서드는 생기지 않고, `get_instance_features` 결과에 `%action-Edit` 컴포넌트가 생깁니다.
- Draft 액션 `Edit/Activate/Discard/Resume/Prepare`의 본 동작은 프레임워크가 구현합니다.

**자주 나는 오류와 해결**

- `Activate optimized`인데 on modify 결정 결과가 이상함 → `optimized`는 이미 실행된 것을 생략할 뿐입니다. draft 단계에서 결정이 실제로 돌았는지(필드 트리거) 확인하세요.
- Resume 메서드에서 draft 키로 읽었더니 활성 상태를 못 봄 → `%is_draft = if_abap_behv=>mk-off`로 **활성** 인스턴스를 읽어야 합니다.

</details>

#### 11단계. UI 어노테이션: 액션 버튼, 그룹 실행, 결정(determining) 버튼

요구사항

메타데이터 확장 `ZRAP_C_TRAVEL_###`(R-01에서 만든 것)을 수정해 다음 버튼이 보이게 하세요.

1. 목록(List Report) 표 위 버튼: Accept Travel, Reject Travel, Deduct Discount(여러 줄 선택 시 **한 변경 세트**로 실행), Copy Travel, Add Service Fee.
2. Object Page 머리글 버튼: Accept Travel, Reject Travel, Deduct Discount, Add Service Fee.
3. Object Page 하단(footer)에 Accept Travel을 **결정(determining) 버튼**으로 하나 더.
4. 버튼은 요소 하나(관례상 `TravelID`)의 `@UI.lineItem`/`@UI.identification` 배열에 넣습니다.
5. `createTravel`(default factory)은 Create 버튼이 자동으로 쓰므로 버튼 어노테이션이 필요 없습니다. `getOpenTravelCount` 같은 함수와 내부 액션은 버튼으로 만들지 않습니다.

**직접 추가할 어노테이션**

- `@UI.lineItem` 의 `type: #FOR_ACTION` — 목록 표에 열 대신 **액션 버튼**을 만듦.
- `dataAction` — 버튼이 호출할 BO 액션 이름(BDEF의 이름 그대로).
- `label` — 버튼 텍스트.
- `invocationGrouping` — 여러 행을 선택했을 때 한 번에(변경 세트로) 실행할지, 행마다 따로 실행할지.
- `@UI.identification` 의 `type: #FOR_ACTION` — Object Page 머리글에 액션 버튼.
- `determining` — Object Page 하단의 결정 버튼(주요 동작)으로 표시.
- `criticality` — 상태 필드 색 (R-01의 가상 요소 `OverallStatusCriticality` 사용).

**확인**

- 활성화 성공. 12단계에서 프로젝션 BDEF에 `use action`을 추가해야 버튼이 실제로 나타납니다(노출되지 않은 액션을 가리키는 버튼은 보이지 않습니다).

<details><summary>정답·해설</summary>

R-01의 MDE를 아래 전체 코드로 바꾸세요(필드 배치는 R-01과 같고, `TravelID`의 버튼 정의가 추가되었습니다).

```cds
@Metadata.layer: #CUSTOMER                                   // 고객 레이어 (→ 어노테이션 탭: @Metadata.layer)
@UI: {
  headerInfo: { typeName: 'Travel',                          // Object Page 제목 (→ 어노테이션 탭: @UI.headerInfo)
                typeNamePlural: 'Travels',
                title: { type: #STANDARD, value: 'TravelID' },
                description: { type: #STANDARD, value: 'Description' } },
  presentationVariant: [ { sortOrder: [ { by: 'TravelID', direction: #DESC } ],   // 기본 정렬 (→ 어노테이션 탭: @UI.presentationVariant)
                           visualizations: [ { type: #AS_LINEITEM } ] } ]
}
annotate view ZRAP_C_TRAVEL_### with
{
  @UI.facet: [ { id: 'idTravel',                             // Object Page 구역 (→ 어노테이션 탭: @UI.facet)
                 purpose: #STANDARD,
                 type: #IDENTIFICATION_REFERENCE,
                 label: 'Travel',
                 position: 10 },
               { id: 'idBooking',
                 purpose: #STANDARD,
                 type: #LINEITEM_REFERENCE,
                 label: 'Bookings',
                 position: 20,
                 targetElement: '_Booking' } ]

  @UI.lineItem: [
    { position: 10, importance: #HIGH },
    // ── 목록 표 위 액션 버튼 (→ 어노테이션 탭: @UI.lineItem) ──
    { type: #FOR_ACTION, dataAction: 'acceptTravel',   label: 'Accept Travel' },
    { type: #FOR_ACTION, dataAction: 'rejectTravel',   label: 'Reject Travel' },
    { type: #FOR_ACTION, dataAction: 'deductDiscount', label: 'Deduct Discount',
      invocationGrouping: #CHANGE_SET },                     // 여러 행을 한 변경 세트로 (→ 어노테이션 탭: @UI.lineItem.invocationGrouping)
    { type: #FOR_ACTION, dataAction: 'copyTravel',     label: 'Copy Travel' },
    { type: #FOR_ACTION, dataAction: 'addServiceFee',  label: 'Add Service Fee' } ]
  @UI.identification: [
    { position: 10 },
    // ── Object Page 머리글 버튼 (→ 어노테이션 탭: @UI.identification) ──
    { type: #FOR_ACTION, dataAction: 'acceptTravel',   label: 'Accept Travel' },
    { type: #FOR_ACTION, dataAction: 'rejectTravel',   label: 'Reject Travel' },
    { type: #FOR_ACTION, dataAction: 'deductDiscount', label: 'Deduct Discount' },
    { type: #FOR_ACTION, dataAction: 'addServiceFee',  label: 'Add Service Fee' },
    // ── 하단(footer) 결정 버튼 (→ 어노테이션 탭: @UI.identification.determining) ──
    { type: #FOR_ACTION, dataAction: 'acceptTravel',   label: 'Accept', determining: true } ]
  @UI.selectionField: [ { position: 10 } ]                   // 필터 바 (→ 어노테이션 탭: @UI.selectionField)
  TravelID;

  @UI.lineItem:       [ { position: 20, importance: #HIGH } ]
  @UI.identification: [ { position: 20 } ]
  @UI.selectionField: [ { position: 20 } ]
  AgencyID;

  @UI.lineItem:       [ { position: 30, importance: #HIGH } ]
  @UI.identification: [ { position: 30 } ]
  @UI.selectionField: [ { position: 30 } ]
  CustomerID;

  @UI.lineItem:       [ { position: 40, importance: #MEDIUM } ]
  @UI.identification: [ { position: 40 } ]
  BeginDate;

  @UI.lineItem:       [ { position: 50, importance: #MEDIUM } ]
  @UI.identification: [ { position: 50 } ]
  EndDate;

  @UI.identification: [ { position: 60 } ]
  BookingFee;

  @UI.lineItem:       [ { position: 70, importance: #MEDIUM } ]
  @UI.identification: [ { position: 70 } ]
  TotalPrice;

  @UI.identification: [ { position: 80 } ]
  Description;

  @UI.lineItem:       [ { position: 90, importance: #HIGH, criticality: 'OverallStatusCriticality' } ]  // 상태 색 (→ 어노테이션 탭: @UI.lineItem.criticality)
  @UI.identification: [ { position: 90, criticality: 'OverallStatusCriticality' } ]
  @UI.selectionField: [ { position: 40 } ]
  @UI.textArrangement: #TEXT_ONLY                            // 코드 대신 텍스트만 (→ 어노테이션 탭: @UI.textArrangement)
  OverallStatus;

  @UI.identification: [ { position: 100, label: 'Attachment' } ]
  Attachment;

  @UI.hidden: true                                           // 화면에 숨김 (→ 어노테이션 탭: @UI.hidden)
  MimeType;

  @UI.hidden: true
  FileName;

  @UI.hidden: true
  OverallStatusCriticality;

  @UI.hidden: true
  LocalLastChangedAt;
}
```

**왜 이렇게 쓰나**

- `#FOR_ACTION` 항목은 `position` 없이 배열 어디에 두어도 됩니다. 위치가 아니라 "이 엔터티에 어떤 액션 버튼이 있는가"를 뜻하므로, 관례적으로 첫 요소(TravelID)에 몰아 둡니다(RAP110 ex05, RAP100 ex06).
- `@UI.lineItem`의 버튼은 목록 표 툴바에, `@UI.identification`의 버튼은 Object Page 머리글에 나옵니다. `copyTravel`은 목록에서만 쓰도록 `lineItem`에만 넣었습니다(RAP100과 같음).
- `invocationGrouping: #CHANGE_SET`: 여러 행을 선택해 실행할 때 한 OData 변경 세트로 묶어, 하나라도 실패하면 모두 실패시킵니다. `#ISOLATED`는 행마다 따로 실행합니다. Flight Reference Scenario의 `deductDiscount` 버튼이 `#CHANGE_SET`을 씁니다.
- `determining: true`: Object Page 하단 바에 주요 동작 버튼으로 놓습니다. 이 속성은 로컬 공식 예제에서 직접 확인하지 못했습니다 (실제 시스템에서 확인 필요). 활성화 오류가 나면 그 줄을 지워도 나머지는 동작합니다.
- 파라미터가 있는 `deductDiscount`는 버튼을 누르면 `ZRAP_A_DISCOUNT_###`의 `@EndUserText.label`("Discount (%)")로 된 팝업이 뜨고, 기본값 함수가 10 또는 20을 미리 채웁니다.
- 버튼의 활성/비활성은 어노테이션이 아니라 6단계 동적 기능 제어가 결정합니다.

**자주 나는 오류와 해결**

- 버튼이 안 보임 → ① 프로젝션 BDEF에 `use action` 누락 ② `dataAction` 철자(대소문자 포함) 불일치 ③ 브라우저 캐시. 
- MDE 활성화 시 "element … not found" → R-01 C 뷰에 그 요소가 없습니다(예: `OverallStatusCriticality`를 다른 이름으로 만들었다면 그 이름으로).

</details>

#### 12단계. 프로젝션 BDEF, 전체 코드 조립, Fiori에서 모든 행동 검증

요구사항

1. 프로젝션 BDEF `ZRAP_C_TRAVEL_###`에 다음을 노출하세요: `use side effects;`(헤더), 모든 공개 액션(`acceptTravel`, `rejectTravel`, `deductDiscount`, `addServiceFee`, `copyTravel`, `createTravel`, `checkDates`), 기본값 함수 두 개, 정적 함수 `getOpenTravelCount`, Draft 액션 다섯 개. Booking에는 `getDaysToFlight`. 내부 액션 `reCalcTotalPrice`는 노출하지 마세요(할 수도 없습니다).
2. 최종 기본 BDEF, Travel/Booking 행동 풀 전체 코드를 한 번에 정리해 활성화하세요.
3. 서비스 바인딩 `ZRAP_UI_TRAVEL_O4_###`에서 Preview를 열어 아래 시나리오를 모두 확인하세요.

**확인** (Fiori Preview 시나리오)

1. **Create** → `createTravel` 팝업. Customer/Agency/Airline 값 도움말 사용, Airline을 고르면 Connection·Flight Date가 함께 채워짐 → OK → Booking 1건이 든 draft Object Page. Status Open, Total Price = 항공료.
2. Booking Fee 50 입력 후 탭 이동 → Total Price 즉시 +50 (사이드 이펙트).
3. Begin Date를 어제로 → 즉시 오류 메시지(determine action). 원래대로 고치면 메시지 사라짐.
4. **Save** → 활성화, TravelID가 번호로 바뀜(late numbering). Description 자동 채움(on save 결정).
5. 목록에서 행 선택 → **Deduct Discount** → 팝업에 10(또는 20) 기본값 → OK → Booking Fee 감소, Total Price 갱신. 0 입력 → 오류 008.
6. **Add Service Fee** → Booking Fee +10.
7. **Copy Travel** → 새 draft Object Page, Booking 복사됨. Discard Draft로 버리기.
8. **Accept Travel** → 성공 토스트 "Travel … has been accepted.", Status 초록(A), Accept/Deduct/Edit/Delete 버튼 비활성.
9. 다른 Travel에서 **Reject Travel** → Booking 추가(+) 비활성.
10. Edit → Booking의 Connection을 없는 번호로 → Save → Booking 줄을 가리키는 오류. 비행일을 여행 기간 밖으로 → 경고만, 저장 성공.

<details><summary>정답·해설</summary>

**프로젝션 BDEF** `ZRAP_C_TRAVEL_###` 전체:

```bdef
projection;
strict ( 2 );
use draft;           // Draft 동작을 서비스에 노출
use side effects;    // 기본 BDEF의 사이드 이펙트를 서비스에 노출

define behavior for ZRAP_C_TRAVEL_### alias Travel
use etag
{
  use create;
  use update;
  use delete;

  // 액션
  use action acceptTravel;
  use action rejectTravel;
  use action deductDiscount;
  use action addServiceFee;
  use action copyTravel;
  use action createTravel;
  use action checkDates;          // determine action도 노출해야 사이드 이펙트에서 호출 가능

  // 함수 (기본값 함수 포함)
  use function GetDefaultsFordeductDiscount;
  use function GetDefaultsForCreate;
  use function getOpenTravelCount;

  // Draft 액션
  use action Edit;
  use action Activate;
  use action Discard;
  use action Resume;
  use action Prepare;

  use association _Booking { create; with draft; }
}

define behavior for ZRAP_C_BOOKING_### alias Booking
use etag
{
  use update;
  use delete;

  use function getDaysToFlight;

  use association _Travel { with draft; }
}
```

**최종 기본 BDEF** `ZRAP_R_TRAVEL_###` 전체:

```bdef
managed implementation in class zbp_rap_r_travel_### unique;
strict ( 2 );
with draft;

define behavior for ZRAP_R_TRAVEL_### alias Travel
persistent table zrap_atrav_###
draft table zrap_dtrav_###
etag master LocalLastChangedAt
lock master total etag LastChangedAt
authorization master ( global )
late numbering
{
  // 표준 작업 (+ create 기본값 함수, 동적 기능 제어)
  create { default function GetDefaultsForCreate; }
  update ( features : instance );
  delete ( features : instance );
  association _Booking { create ( features : instance ); with draft; }

  // 정적 필드 제어
  field ( readonly ) TravelID, TotalPrice, OverallStatus,
                     CreatedBy, CreatedAt, LocalLastChangedBy, LocalLastChangedAt, LastChangedAt;
  field ( mandatory ) CustomerID, BeginDate, EndDate, CurrencyCode;
  field ( mandatory : create, readonly : update ) AgencyID;

  // 결정
  determination setInitialValues on modify { create; }
  determination calculateTotalPrice on modify { create; field BookingFee, CurrencyCode; }
  determination setDefaultDescription on save { create; }

  // 검증
  validation validateCustomer on save { create; field CustomerID; }
  validation validateAgency on save { create; field AgencyID; }
  validation validateDates on save { create; field BeginDate, EndDate; }

  // 액션
  internal action reCalcTotalPrice;
  action ( features : instance ) acceptTravel result [1] $self;
  action ( features : instance ) rejectTravel result [1] $self;
  action ( features : instance ) deductDiscount parameter ZRAP_A_DISCOUNT_### result [1] $self
    { default function GetDefaultsFordeductDiscount; }
  repeatable action addServiceFee result [1] $self;
  factory action copyTravel [1];
  static default factory action createTravel parameter ZRAP_A_CREATE_TRAVEL_### [1];

  // 함수
  static function getOpenTravelCount result [1] ZRAP_A_TRAVEL_STAT_###;

  // determine action
  determine action checkDates { validation validateDates; }

  // 사이드 이펙트
  side effects
  {
    field BookingFee affects field TotalPrice;
    field CurrencyCode affects field TotalPrice;
    determine action checkDates executed on field BeginDate, field EndDate affects messages;
    action acceptTravel affects permissions ( action acceptTravel, action rejectTravel, action deductDiscount ), messages;
    action rejectTravel affects permissions ( action acceptTravel, action rejectTravel, action deductDiscount ), messages;
    action addServiceFee affects field TotalPrice;
    action deductDiscount affects field TotalPrice;
  }

  // Draft 액션
  draft action ( features : instance ) Edit;
  draft action Activate optimized;
  draft action Discard;
  draft action Resume with additional implementation;
  draft determine action Prepare
  {
    determination setDefaultDescription;
    validation validateCustomer;
    validation validateAgency;
    validation validateDates;
    validation Booking~validateConnection;
    validation Booking~validateStatus;
  }

  mapping for zrap_atrav_###
    {
      TravelID           = travel_id;
      AgencyID           = agency_id;
      CustomerID         = customer_id;
      BeginDate          = begin_date;
      EndDate            = end_date;
      BookingFee         = booking_fee;
      TotalPrice         = total_price;
      CurrencyCode       = currency_code;
      Description        = description;
      OverallStatus      = overall_status;
      Attachment         = attachment;
      MimeType           = mime_type;
      FileName           = file_name;
      CreatedBy          = created_by;
      CreatedAt          = created_at;
      LocalLastChangedBy = local_last_changed_by;
      LocalLastChangedAt = local_last_changed_at;
      LastChangedAt      = last_changed_at;
    }
}

define behavior for ZRAP_R_BOOKING_### alias Booking
implementation in class zbp_rap_r_booking_### unique
persistent table zrap_abook_###
draft table zrap_dbook_###
etag master LocalLastChangedAt
lock dependent by _Travel
authorization dependent by _Travel
late numbering
{
  update;
  delete;
  association _Travel { with draft; }

  // 정적 필드 제어
  field ( readonly ) TravelID, BookingID, BookingDate, LocalLastChangedAt;
  field ( mandatory ) CustomerID, CarrierID, ConnectionID, FlightDate;

  // 결정
  determination setInitialBookingValues on modify { create; }
  determination calculateTotalPrice on modify { create; field FlightPrice, CurrencyCode; }

  // 검증
  validation validateConnection on save { create; field CarrierID, ConnectionID, FlightDate; }
  validation validateStatus on save { create; field BookingStatus; }

  // 함수
  function getDaysToFlight result [1] ZRAP_A_DAYS_TO_FLIGHT_###;

  // 사이드 이펙트 (대상이 부모 엔터티 필드)
  side effects
  {
    field FlightPrice affects field _Travel.TotalPrice;
    field CurrencyCode affects field _Travel.TotalPrice;
  }

  mapping for zrap_abook_###
    {
      TravelID           = travel_id;
      BookingID          = booking_id;
      BookingDate        = booking_date;
      CustomerID         = customer_id;
      CarrierID          = carrier_id;
      ConnectionID       = connection_id;
      FlightDate         = flight_date;
      FlightPrice        = flight_price;
      CurrencyCode       = currency_code;
      BookingStatus      = booking_status;
      LocalLastChangedAt = local_last_changed_at;
    }
}
```

**행동 풀 `ZBP_RAP_R_TRAVEL_###`** — 글로벌 클래스(R-01 그대로):

```abap
CLASS zbp_rap_r_travel_### DEFINITION
  PUBLIC
  ABSTRACT
  FINAL
  FOR BEHAVIOR OF zrap_r_travel_###.
ENDCLASS.

CLASS zbp_rap_r_travel_### IMPLEMENTATION.
ENDCLASS.
```

로컬 타입(Local Types) 탭 전체:

```abap
**********************************************************************
* 핸들러: Travel 엔터티 (상호작용 단계 - 트랜잭션 버퍼 변경)
**********************************************************************
CLASS lhc_travel DEFINITION INHERITING FROM cl_abap_behavior_handler.
  PRIVATE SECTION.

    CONSTANTS:
      BEGIN OF travel_status,
        open     TYPE /dmo/overall_status VALUE 'O', "Open
        accepted TYPE /dmo/overall_status VALUE 'A', "Accepted
        rejected TYPE /dmo/overall_status VALUE 'X', "Rejected
      END OF travel_status,
      BEGIN OF booking_status,
        new TYPE /dmo/booking_status VALUE 'N', "New
      END OF booking_status,
      c_default_currency TYPE /dmo/currency_code VALUE 'EUR',
      c_service_fee      TYPE /dmo/booking_fee   VALUE '10.00',
      BEGIN OF state_area,
        customer TYPE string VALUE 'VALIDATE_CUSTOMER',
        agency   TYPE string VALUE 'VALIDATE_AGENCY',
        dates    TYPE string VALUE 'VALIDATE_DATES',
      END OF state_area.

    "--- 권한 / 기능 제어 ------------------------------------------------
    METHODS get_global_authorizations FOR GLOBAL AUTHORIZATION
      IMPORTING REQUEST requested_authorizations FOR Travel RESULT result.

    METHODS get_instance_features FOR INSTANCE FEATURES
      IMPORTING keys REQUEST requested_features FOR Travel RESULT result.

    "--- 결정 -------------------------------------------------------------
    METHODS setInitialValues FOR DETERMINE ON MODIFY
      IMPORTING keys FOR Travel~setInitialValues.

    METHODS calculateTotalPrice FOR DETERMINE ON MODIFY
      IMPORTING keys FOR Travel~calculateTotalPrice.

    METHODS setDefaultDescription FOR DETERMINE ON SAVE
      IMPORTING keys FOR Travel~setDefaultDescription.

    "--- 검증 -------------------------------------------------------------
    METHODS validateCustomer FOR VALIDATE ON SAVE
      IMPORTING keys FOR Travel~validateCustomer.

    METHODS validateAgency FOR VALIDATE ON SAVE
      IMPORTING keys FOR Travel~validateAgency.

    METHODS validateDates FOR VALIDATE ON SAVE
      IMPORTING keys FOR Travel~validateDates.

    "--- 액션 -------------------------------------------------------------
    METHODS reCalcTotalPrice FOR MODIFY
      IMPORTING keys FOR ACTION Travel~reCalcTotalPrice.

    METHODS acceptTravel FOR MODIFY
      IMPORTING keys FOR ACTION Travel~acceptTravel RESULT result.

    METHODS rejectTravel FOR MODIFY
      IMPORTING keys FOR ACTION Travel~rejectTravel RESULT result.

    METHODS deductDiscount FOR MODIFY
      IMPORTING keys FOR ACTION Travel~deductDiscount RESULT result.

    METHODS GetDefaultsFordeductDiscount FOR READ
      IMPORTING keys FOR FUNCTION Travel~GetDefaultsFordeductDiscount RESULT result.

    METHODS addServiceFee FOR MODIFY
      IMPORTING keys FOR ACTION Travel~addServiceFee RESULT result.

    METHODS copyTravel FOR MODIFY
      IMPORTING keys FOR ACTION Travel~copyTravel.

    METHODS createTravel FOR MODIFY
      IMPORTING keys FOR ACTION Travel~createTravel.

    METHODS GetDefaultsForCreate FOR READ
      IMPORTING keys FOR FUNCTION Travel~GetDefaultsForCreate RESULT result.

    "--- 함수 -------------------------------------------------------------
    METHODS getOpenTravelCount FOR READ
      IMPORTING keys FOR FUNCTION Travel~getOpenTravelCount RESULT result.

    "--- Draft ------------------------------------------------------------
    METHODS Resume FOR MODIFY
      IMPORTING keys FOR ACTION Travel~Resume.

ENDCLASS.


CLASS lhc_travel IMPLEMENTATION.

**********************************************************************
* 전역 권한 (R-01과 동일: 학습용으로 모두 허용, 실제 검사는 R-03)
**********************************************************************
  METHOD get_global_authorizations.
    result = VALUE #( %create      = if_abap_behv=>auth-allowed
                      %update      = if_abap_behv=>auth-allowed
                      %delete      = if_abap_behv=>auth-allowed
                      %action-Edit = if_abap_behv=>auth-allowed ).
  ENDMETHOD.

**********************************************************************
* 동적 기능 제어: 상태에 따라 버튼/작업 활성·비활성
**********************************************************************
  METHOD get_instance_features.
    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        FIELDS ( OverallStatus )
        WITH CORRESPONDING #( keys )
      RESULT DATA(travels)
      FAILED failed.

    result = VALUE #(
      FOR travel IN travels
      ( %tky                   = travel-%tky
        %features-%update      = COND #( WHEN travel-OverallStatus = travel_status-accepted
                                         THEN if_abap_behv=>fc-o-disabled
                                         ELSE if_abap_behv=>fc-o-enabled )
        %features-%delete      = COND #( WHEN travel-OverallStatus = travel_status-accepted
                                         THEN if_abap_behv=>fc-o-disabled
                                         ELSE if_abap_behv=>fc-o-enabled )
        %action-Edit           = COND #( WHEN travel-OverallStatus = travel_status-accepted
                                         THEN if_abap_behv=>fc-o-disabled
                                         ELSE if_abap_behv=>fc-o-enabled )
        %action-acceptTravel   = COND #( WHEN travel-OverallStatus = travel_status-accepted
                                         THEN if_abap_behv=>fc-o-disabled
                                         ELSE if_abap_behv=>fc-o-enabled )
        %action-rejectTravel   = COND #( WHEN travel-OverallStatus = travel_status-rejected
                                         THEN if_abap_behv=>fc-o-disabled
                                         ELSE if_abap_behv=>fc-o-enabled )
        %action-deductDiscount = COND #( WHEN travel-OverallStatus = travel_status-accepted
                                         THEN if_abap_behv=>fc-o-disabled
                                         ELSE if_abap_behv=>fc-o-enabled )
        %assoc-_Booking        = COND #( WHEN travel-OverallStatus = travel_status-rejected
                                         THEN if_abap_behv=>fc-o-disabled
                                         ELSE if_abap_behv=>fc-o-enabled ) ) ).
  ENDMETHOD.

**********************************************************************
* 결정 on modify { create; }: 초기값 (상태 O, 날짜, 통화)
**********************************************************************
  METHOD setInitialValues.
    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        FIELDS ( BeginDate EndDate CurrencyCode OverallStatus )
        WITH CORRESPONDING #( keys )
      RESULT DATA(travels).

    " 이미 다 채워진 인스턴스는 건드리지 않음 (factory action 등에서 값이 온 경우)
    DELETE travels WHERE BeginDate     IS NOT INITIAL
                     AND EndDate       IS NOT INITIAL
                     AND CurrencyCode  IS NOT INITIAL
                     AND OverallStatus IS NOT INITIAL.
    CHECK travels IS NOT INITIAL.

    DATA(today) = cl_abap_context_info=>get_system_date( ).
    DATA travels_upd TYPE TABLE FOR UPDATE zrap_r_travel_###\\Travel.

    LOOP AT travels INTO DATA(travel).
      APPEND VALUE #( %tky = travel-%tky ) TO travels_upd ASSIGNING FIELD-SYMBOL(<upd>).
      IF travel-BeginDate IS INITIAL.
        <upd>-BeginDate          = today + 1.
        <upd>-%control-BeginDate = if_abap_behv=>mk-on.
      ENDIF.
      IF travel-EndDate IS INITIAL.
        <upd>-EndDate          = today + 15.
        <upd>-%control-EndDate = if_abap_behv=>mk-on.
      ENDIF.
      IF travel-CurrencyCode IS INITIAL.
        <upd>-CurrencyCode          = c_default_currency.
        <upd>-%control-CurrencyCode = if_abap_behv=>mk-on.
      ENDIF.
      IF travel-OverallStatus IS INITIAL.
        <upd>-OverallStatus          = travel_status-open.
        <upd>-%control-OverallStatus = if_abap_behv=>mk-on.
      ENDIF.
    ENDLOOP.

    " %control로 표시한 필드만 바뀜 (UPDATE FROM)
    MODIFY ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        UPDATE FROM travels_upd.
  ENDMETHOD.

**********************************************************************
* 결정 on modify { create; field BookingFee, CurrencyCode; }
* → 계산은 내부 액션 reCalcTotalPrice에 위임 (Booking에서도 호출)
**********************************************************************
  METHOD calculateTotalPrice.
    MODIFY ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        EXECUTE reCalcTotalPrice
        FROM CORRESPONDING #( keys ).
  ENDMETHOD.

**********************************************************************
* 결정 on save { create; }: 설명이 비어 있으면 기본 설명
**********************************************************************
  METHOD setDefaultDescription.
    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        FIELDS ( Description CustomerID BeginDate )
        WITH CORRESPONDING #( keys )
      RESULT DATA(travels).

    DELETE travels WHERE Description IS NOT INITIAL.
    CHECK travels IS NOT INITIAL.

    MODIFY ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        UPDATE FIELDS ( Description )
        WITH VALUE #( FOR travel IN travels
                      ( %tky        = travel-%tky
                        Description = |Trip of customer { travel-CustomerID ALPHA = OUT } from { travel-BeginDate DATE = ISO }| ) ).
  ENDMETHOD.

**********************************************************************
* 검증: 고객 존재 여부
**********************************************************************
  METHOD validateCustomer.
    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        FIELDS ( CustomerID )
        WITH CORRESPONDING #( keys )
      RESULT DATA(travels).

    " 중복 없는 고객 번호만 모아 한 번에 SELECT
    DATA customers TYPE SORTED TABLE OF /dmo/customer WITH UNIQUE KEY customer_id.
    customers = CORRESPONDING #( travels DISCARDING DUPLICATES MAPPING customer_id = CustomerID EXCEPT * ).
    DELETE customers WHERE customer_id IS INITIAL.

    IF customers IS NOT INITIAL.
      SELECT FROM /dmo/customer
        FIELDS customer_id
        FOR ALL ENTRIES IN @customers
        WHERE customer_id = @customers-customer_id
        INTO TABLE @DATA(valid_customers).
    ENDIF.

    LOOP AT travels INTO DATA(travel).
      " 1) 이 검증이 예전에 남긴 메시지를 먼저 지움 (state message)
      APPEND VALUE #( %tky        = travel-%tky
                      %state_area = state_area-customer ) TO reported-travel.

      IF travel-CustomerID IS INITIAL.
        APPEND VALUE #( %tky = travel-%tky ) TO failed-travel.
        APPEND VALUE #( %tky                = travel-%tky
                        %state_area         = state_area-customer
                        %msg                = NEW zcm_rap_###( textid   = zcm_rap_###=>enter_customer_id
                                                               severity = if_abap_behv_message=>severity-error )
                        %element-CustomerID = if_abap_behv=>mk-on ) TO reported-travel.

      ELSEIF NOT line_exists( valid_customers[ customer_id = travel-CustomerID ] ).
        APPEND VALUE #( %tky = travel-%tky ) TO failed-travel.
        APPEND VALUE #( %tky                = travel-%tky
                        %state_area         = state_area-customer
                        %msg                = NEW zcm_rap_###( textid      = zcm_rap_###=>customer_unknown
                                                               customer_id = travel-CustomerID
                                                               severity    = if_abap_behv_message=>severity-error )
                        %element-CustomerID = if_abap_behv=>mk-on ) TO reported-travel.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

**********************************************************************
* 검증: 여행사 존재 여부
**********************************************************************
  METHOD validateAgency.
    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        FIELDS ( AgencyID )
        WITH CORRESPONDING #( keys )
      RESULT DATA(travels).

    DATA agencies TYPE SORTED TABLE OF /dmo/agency WITH UNIQUE KEY agency_id.
    agencies = CORRESPONDING #( travels DISCARDING DUPLICATES MAPPING agency_id = AgencyID EXCEPT * ).
    DELETE agencies WHERE agency_id IS INITIAL.

    IF agencies IS NOT INITIAL.
      SELECT FROM /dmo/agency
        FIELDS agency_id
        FOR ALL ENTRIES IN @agencies
        WHERE agency_id = @agencies-agency_id
        INTO TABLE @DATA(valid_agencies).
    ENDIF.

    LOOP AT travels INTO DATA(travel).
      APPEND VALUE #( %tky        = travel-%tky
                      %state_area = state_area-agency ) TO reported-travel.

      IF travel-AgencyID IS INITIAL.
        APPEND VALUE #( %tky = travel-%tky ) TO failed-travel.
        APPEND VALUE #( %tky              = travel-%tky
                        %state_area       = state_area-agency
                        %msg              = NEW zcm_rap_###( textid   = zcm_rap_###=>enter_agency_id
                                                             severity = if_abap_behv_message=>severity-error )
                        %element-AgencyID = if_abap_behv=>mk-on ) TO reported-travel.

      ELSEIF NOT line_exists( valid_agencies[ agency_id = travel-AgencyID ] ).
        APPEND VALUE #( %tky = travel-%tky ) TO failed-travel.
        APPEND VALUE #( %tky              = travel-%tky
                        %state_area       = state_area-agency
                        %msg              = NEW zcm_rap_###( textid    = zcm_rap_###=>agency_unknown
                                                             agency_id = travel-AgencyID
                                                             severity  = if_abap_behv_message=>severity-error )
                        %element-AgencyID = if_abap_behv=>mk-on ) TO reported-travel.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

**********************************************************************
* 검증: 날짜 (필수, 시작 <= 종료, 시작 >= 오늘)
**********************************************************************
  METHOD validateDates.
    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        FIELDS ( TravelID BeginDate EndDate )
        WITH CORRESPONDING #( keys )
      RESULT DATA(travels).

    DATA(today) = cl_abap_context_info=>get_system_date( ).

    LOOP AT travels INTO DATA(travel).
      APPEND VALUE #( %tky        = travel-%tky
                      %state_area = state_area-dates ) TO reported-travel.

      IF travel-BeginDate IS INITIAL OR travel-EndDate IS INITIAL.
        APPEND VALUE #( %tky = travel-%tky ) TO failed-travel.
        APPEND VALUE #( %tky               = travel-%tky
                        %state_area        = state_area-dates
                        %msg               = NEW zcm_rap_###( textid   = zcm_rap_###=>enter_dates
                                                              severity = if_abap_behv_message=>severity-error )
                        %element-BeginDate = if_abap_behv=>mk-on
                        %element-EndDate   = if_abap_behv=>mk-on ) TO reported-travel.

      ELSEIF travel-EndDate < travel-BeginDate.
        APPEND VALUE #( %tky = travel-%tky ) TO failed-travel.
        APPEND VALUE #( %tky               = travel-%tky
                        %state_area        = state_area-dates
                        %msg               = NEW zcm_rap_###( textid     = zcm_rap_###=>begin_date_after_end_date
                                                              begin_date = travel-BeginDate
                                                              end_date   = travel-EndDate
                                                              severity   = if_abap_behv_message=>severity-error )
                        %element-BeginDate = if_abap_behv=>mk-on
                        %element-EndDate   = if_abap_behv=>mk-on ) TO reported-travel.

      ELSEIF travel-BeginDate < today.
        APPEND VALUE #( %tky = travel-%tky ) TO failed-travel.
        APPEND VALUE #( %tky               = travel-%tky
                        %state_area        = state_area-dates
                        %msg               = NEW zcm_rap_###( textid     = zcm_rap_###=>begin_date_in_past
                                                              begin_date = travel-BeginDate
                                                              severity   = if_abap_behv_message=>severity-error )
                        %element-BeginDate = if_abap_behv=>mk-on ) TO reported-travel.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

**********************************************************************
* 내부 액션: 총액 = 예약 수수료 + 모든 Booking 항공료 (통화 환산 포함)
**********************************************************************
  METHOD reCalcTotalPrice.
    TYPES: BEGIN OF ty_amount_per_currency,
             amount        TYPE /dmo/total_price,
             currency_code TYPE /dmo/currency_code,
           END OF ty_amount_per_currency.
    DATA amounts_per_currency TYPE STANDARD TABLE OF ty_amount_per_currency.

    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        FIELDS ( BookingFee CurrencyCode )
        WITH CORRESPONDING #( keys )
      RESULT DATA(travels).

    DELETE travels WHERE CurrencyCode IS INITIAL.
    CHECK travels IS NOT INITIAL.

    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel BY \_Booking
        FIELDS ( FlightPrice CurrencyCode )
        WITH CORRESPONDING #( travels )
      LINK DATA(booking_links)
      RESULT DATA(bookings).

    DATA(today) = cl_abap_context_info=>get_system_date( ).

    LOOP AT travels ASSIGNING FIELD-SYMBOL(<travel>).
      amounts_per_currency = VALUE #( ( amount        = <travel>-BookingFee
                                        currency_code = <travel>-CurrencyCode ) ).

      LOOP AT booking_links INTO DATA(booking_link) USING KEY id WHERE source-%tky = <travel>-%tky.
        DATA(booking) = bookings[ KEY id %tky = booking_link-target-%tky ].
        COLLECT VALUE ty_amount_per_currency( amount        = booking-FlightPrice
                                              currency_code = booking-CurrencyCode ) INTO amounts_per_currency.
      ENDLOOP.

      DELETE amounts_per_currency WHERE currency_code IS INITIAL.

      CLEAR <travel>-TotalPrice.
      LOOP AT amounts_per_currency INTO DATA(amount_per_currency).
        IF amount_per_currency-currency_code = <travel>-CurrencyCode.
          <travel>-TotalPrice += amount_per_currency-amount.
        ELSE.
          /dmo/cl_flight_amdp=>convert_currency(
            EXPORTING
              iv_amount               = amount_per_currency-amount
              iv_currency_code_source = amount_per_currency-currency_code
              iv_currency_code_target = <travel>-CurrencyCode
              iv_exchange_rate_date   = today
            IMPORTING
              ev_amount               = DATA(converted_amount) ).
          <travel>-TotalPrice += converted_amount.
        ENDIF.
      ENDLOOP.
    ENDLOOP.

    MODIFY ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        UPDATE FIELDS ( TotalPrice )
        WITH CORRESPONDING #( travels ).
  ENDMETHOD.

**********************************************************************
* 인스턴스 액션: 승인 (result [1] $self)
**********************************************************************
  METHOD acceptTravel.
    MODIFY ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        UPDATE FIELDS ( OverallStatus )
        WITH VALUE #( FOR key IN keys ( %tky          = key-%tky
                                        OverallStatus = travel_status-accepted ) )
      FAILED failed
      REPORTED reported.

    " 결과는 반드시 변경 후 상태를 다시 읽어 채움
    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        ALL FIELDS WITH CORRESPONDING #( keys )
      RESULT DATA(travels).

    result = VALUE #( FOR travel IN travels ( %tky   = travel-%tky
                                              %param = travel ) ).

    " 성공 메시지 (state area 없음 = 일회성 transition message)
    LOOP AT travels INTO DATA(accepted).
      APPEND VALUE #( %tky = accepted-%tky
                      %msg = NEW zcm_rap_###( textid    = zcm_rap_###=>travel_accepted
                                              travel_id = accepted-TravelID
                                              severity  = if_abap_behv_message=>severity-success ) )
        TO reported-travel.
    ENDLOOP.
  ENDMETHOD.

**********************************************************************
* 인스턴스 액션: 거절
**********************************************************************
  METHOD rejectTravel.
    MODIFY ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        UPDATE FIELDS ( OverallStatus )
        WITH VALUE #( FOR key IN keys ( %tky          = key-%tky
                                        OverallStatus = travel_status-rejected ) )
      FAILED failed
      REPORTED reported.

    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        ALL FIELDS WITH CORRESPONDING #( keys )
      RESULT DATA(travels).

    result = VALUE #( FOR travel IN travels ( %tky   = travel-%tky
                                              %param = travel ) ).

    LOOP AT travels INTO DATA(rejected).
      APPEND VALUE #( %tky = rejected-%tky
                      %msg = NEW zcm_rap_###( textid    = zcm_rap_###=>travel_rejected
                                              travel_id = rejected-TravelID
                                              severity  = if_abap_behv_message=>severity-success ) )
        TO reported-travel.
    ENDLOOP.
  ENDMETHOD.

**********************************************************************
* 파라미터 액션: 예약 수수료 할인 (parameter ZRAP_A_DISCOUNT_###)
**********************************************************************
  METHOD deductDiscount.
    DATA travels_for_update TYPE TABLE FOR UPDATE zrap_r_travel_###\\Travel.
    DATA(valid_keys) = keys.

    " 1) 파라미터 검사: 1~100 이 아니면 실패
    LOOP AT valid_keys ASSIGNING FIELD-SYMBOL(<key>) WHERE %param-discount_percent IS INITIAL
                                                        OR %param-discount_percent > 100.
      APPEND VALUE #( %tky = <key>-%tky ) TO failed-travel.
      APPEND VALUE #( %tky                       = <key>-%tky
                      %msg                       = NEW zcm_rap_###( textid   = zcm_rap_###=>discount_invalid
                                                                    severity = if_abap_behv_message=>severity-error )
                      %element-BookingFee        = if_abap_behv=>mk-on
                      %op-%action-deductDiscount = if_abap_behv=>mk-on ) TO reported-travel.
      DELETE valid_keys.
    ENDLOOP.
    CHECK valid_keys IS NOT INITIAL.

    " 2) 현재 수수료 읽기
    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        FIELDS ( BookingFee )
        WITH CORRESPONDING #( valid_keys )
      RESULT DATA(travels).

    " 3) 할인 계산 (decfloat16 변수에 대입해야 정수 나눗셈이 되지 않음)
    DATA percentage TYPE decfloat16.
    LOOP AT travels INTO DATA(travel).
      DATA(discount_percent) = valid_keys[ KEY id %tky = travel-%tky ]-%param-discount_percent.
      percentage = discount_percent / 100.
      APPEND VALUE #( %tky       = travel-%tky
                      BookingFee = travel-BookingFee * ( 1 - percentage ) ) TO travels_for_update.
    ENDLOOP.

    " 4) 변경 (→ calculateTotalPrice 결정이 BookingFee 변경으로 다시 실행됨)
    MODIFY ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        UPDATE FIELDS ( BookingFee )
        WITH travels_for_update.

    " 5) 결과
    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        ALL FIELDS WITH CORRESPONDING #( travels )
      RESULT DATA(travels_with_discount).

    result = VALUE #( FOR discounted IN travels_with_discount ( %tky   = discounted-%tky
                                                               %param = discounted ) ).
  ENDMETHOD.

**********************************************************************
* 기본값 함수: deductDiscount 팝업의 할인율 기본값
**********************************************************************
  METHOD GetDefaultsFordeductDiscount.
    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        FIELDS ( TotalPrice )
        WITH CORRESPONDING #( keys )
      RESULT DATA(travels)
      FAILED failed.

    result = VALUE #( FOR travel IN travels
                      ( %tky                    = travel-%tky
                        %param-discount_percent = COND #( WHEN travel-TotalPrice >= 5000 THEN 20
                                                          ELSE 10 ) ) ).
  ENDMETHOD.

**********************************************************************
* 반복 가능 액션: 한 요청에서 같은 인스턴스에 여러 번 실행 가능
**********************************************************************
  METHOD addServiceFee.
    " keys에 같은 인스턴스가 여러 줄 올 수 있으므로 읽기용 키는 중복 제거
    DATA read_keys TYPE TABLE FOR READ IMPORT zrap_r_travel_###\\Travel.
    LOOP AT keys INTO DATA(key).
      IF NOT line_exists( read_keys[ %tky = key-%tky ] ).
        APPEND VALUE #( %tky = key-%tky ) TO read_keys.
      ENDIF.
    ENDLOOP.

    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        FIELDS ( BookingFee )
        WITH read_keys
      RESULT DATA(travels)
      FAILED failed.

    " 실행 횟수만큼 수수료 누적
    LOOP AT keys INTO key.
      ASSIGN travels[ KEY id %tky = key-%tky ] TO FIELD-SYMBOL(<travel>).
      IF sy-subrc = 0.
        <travel>-BookingFee += c_service_fee.
      ENDIF.
    ENDLOOP.

    MODIFY ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        UPDATE FIELDS ( BookingFee )
        WITH CORRESPONDING #( travels ).

    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        ALL FIELDS WITH read_keys
      RESULT DATA(travels_new).

    " 결과는 실행(키 줄) 하나당 한 줄. 반복 가능 액션은 %cid로 실행을 구분
    LOOP AT keys INTO key.
      READ TABLE travels_new WITH KEY id COMPONENTS %tky = key-%tky INTO DATA(travel_new).
      IF sy-subrc = 0.
        APPEND VALUE #( %cid   = key-%cid
                        %tky   = key-%tky
                        %param = travel_new ) TO result.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

**********************************************************************
* 인스턴스 팩토리 액션: Travel + Booking 복사
**********************************************************************
  METHOD copyTravel.
    DATA travels_cba TYPE TABLE FOR CREATE zrap_r_travel_###\\Travel.
    DATA bookings_cba TYPE TABLE FOR CREATE zrap_r_travel_###\\Travel\_Booking.

    " 팩토리 액션은 호출자가 %cid를 반드시 줘야 함 (mapped로 돌려줄 연결 고리)
    ASSERT NOT line_exists( keys[ %cid = '' ] ).

    " 원본 Travel
    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        ALL FIELDS WITH CORRESPONDING #( keys )
      RESULT DATA(travels).

    " 원본 Booking + 어떤 Travel의 것인지 링크
    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel BY \_Booking
        ALL FIELDS WITH CORRESPONDING #( travels )
      LINK DATA(booking_links)
      RESULT DATA(bookings).

    DATA(today) = cl_abap_context_info=>get_system_date( ).

    LOOP AT travels INTO DATA(travel).
      DATA(key) = keys[ KEY id %tky = travel-%tky ].

      " 새 Travel: 키(TravelID)는 late numbering이 채우므로 넘기지 않음
      APPEND VALUE #( %cid      = key-%cid
                      %is_draft = key-%param-%is_draft
                      %data     = CORRESPONDING #( travel EXCEPT TravelID TotalPrice OverallStatus ) )
        TO travels_cba ASSIGNING FIELD-SYMBOL(<new_travel>).
      <new_travel>-BeginDate   = today + 1.
      <new_travel>-EndDate     = today + 15.
      <new_travel>-Description = |Copy of { travel-TravelID ALPHA = OUT }|.

      " 새 Booking들: 부모는 %cid_ref로 '방금 만든 Travel'을 가리킴
      APPEND VALUE #( %cid_ref  = key-%cid
                      %is_draft = key-%param-%is_draft ) TO bookings_cba ASSIGNING FIELD-SYMBOL(<cba>).
      LOOP AT booking_links INTO DATA(link) USING KEY id WHERE source-%tky = travel-%tky.
        DATA(booking) = bookings[ KEY id %tky = link-target-%tky ].
        APPEND VALUE #( %cid          = |{ key-%cid }_{ booking-BookingID }|
                        %is_draft     = key-%param-%is_draft
                        CustomerID    = booking-CustomerID
                        CarrierID     = booking-CarrierID
                        ConnectionID  = booking-ConnectionID
                        FlightDate    = booking-FlightDate
                        FlightPrice   = booking-FlightPrice
                        CurrencyCode  = booking-CurrencyCode
                        BookingStatus = booking_status-new ) TO <cba>-%target.
      ENDLOOP.
    ENDLOOP.

    MODIFY ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        CREATE FIELDS ( AgencyID CustomerID BeginDate EndDate BookingFee CurrencyCode Description )
          WITH travels_cba
        CREATE BY \_Booking
          FIELDS ( CustomerID CarrierID ConnectionID FlightDate FlightPrice CurrencyCode BookingStatus )
          WITH bookings_cba
      MAPPED mapped      " %cid ↔ 새 인스턴스(%pid) 연결을 호출자에게 돌려줌
      FAILED failed
      REPORTED reported.
  ENDMETHOD.

**********************************************************************
* 정적 기본 팩토리 액션: Fiori '만들기' 버튼 → Travel + 첫 Booking 생성
**********************************************************************
  METHOD createTravel.
    CHECK keys IS NOT INITIAL.

    " 항공편 가격/통화를 한 번에 조회
    SELECT FROM /dmo/flight
      FIELDS carrier_id, connection_id, flight_date, price, currency_code
      FOR ALL ENTRIES IN @keys
      WHERE carrier_id    = @keys-%param-carrier_id
        AND connection_id = @keys-%param-connection_id
        AND flight_date   = @keys-%param-flight_date
      INTO TABLE @DATA(flights).

    MODIFY ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        CREATE FIELDS ( CustomerID AgencyID BeginDate EndDate Description )
          WITH VALUE #( FOR key IN keys
                        ( %cid        = key-%cid
                          %is_draft   = key-%param-%is_draft
                          CustomerID  = key-%param-customer_id
                          AgencyID    = key-%param-agency_id
                          BeginDate   = key-%param-flight_date
                          EndDate     = key-%param-flight_date
                          Description = 'Created with createTravel' ) )
        CREATE BY \_Booking
          FIELDS ( CustomerID CarrierID ConnectionID FlightDate FlightPrice CurrencyCode )
          WITH VALUE #( FOR key IN keys INDEX INTO i
                        ( %cid_ref  = key-%cid
                          %is_draft = key-%param-%is_draft
                          %target   = VALUE #( ( %cid         = |CBA_{ i }|
                                                     %is_draft    = key-%param-%is_draft
                                                     CustomerID   = key-%param-customer_id
                                                     CarrierID    = key-%param-carrier_id
                                                     ConnectionID = key-%param-connection_id
                                                     FlightDate   = key-%param-flight_date
                                                     FlightPrice  = VALUE #( flights[ carrier_id    = key-%param-carrier_id
                                                                                      connection_id = key-%param-connection_id
                                                                                      flight_date   = key-%param-flight_date ]-price OPTIONAL )
                                                     CurrencyCode = VALUE #( flights[ carrier_id    = key-%param-carrier_id
                                                                                      connection_id = key-%param-connection_id
                                                                                      flight_date   = key-%param-flight_date ]-currency_code OPTIONAL ) ) ) ) )
      MAPPED mapped
      FAILED failed
      REPORTED reported.
  ENDMETHOD.

**********************************************************************
* create 기본값 함수: 새 Travel 화면의 초기값 제안
**********************************************************************
  METHOD GetDefaultsForCreate.
    " 내가 마지막으로 만든 Travel의 여행사를 제안
    SELECT FROM zrap_atrav_###
      FIELDS agency_id
      WHERE created_by = @( cl_abap_context_info=>get_user_technical_name( ) )
      ORDER BY created_at DESCENDING
      INTO TABLE @DATA(last_agencies)
      UP TO 1 ROWS.

    DATA(today) = cl_abap_context_info=>get_system_date( ).

    result = VALUE #( FOR key IN keys
                      ( %cid                = key-%cid
                        %param-AgencyID     = VALUE #( last_agencies[ 1 ]-agency_id OPTIONAL )
                        %param-CurrencyCode = c_default_currency
                        %param-BeginDate    = today + 7
                        %param-EndDate      = today + 14 ) ).
  ENDMETHOD.

**********************************************************************
* 정적 함수: 상태별 Travel 건수 (활성 데이터 기준)
**********************************************************************
  METHOD getOpenTravelCount.
    SELECT FROM zrap_atrav_###
      FIELDS overall_status, COUNT( * ) AS cnt
      GROUP BY overall_status
      INTO TABLE @DATA(counts).

    result = VALUE #( FOR key IN keys
                      ( %cid                  = key-%cid
                        %param-open_count     = VALUE #( counts[ overall_status = travel_status-open ]-cnt OPTIONAL )
                        %param-accepted_count = VALUE #( counts[ overall_status = travel_status-accepted ]-cnt OPTIONAL )
                        %param-rejected_count = VALUE #( counts[ overall_status = travel_status-rejected ]-cnt OPTIONAL ) ) ).
  ENDMETHOD.

**********************************************************************
* Resume (with additional implementation):
* 잠금이 만료된 draft를 다시 편집할 때, 그 사이 활성 데이터가 승인됐으면 막음
**********************************************************************
  METHOD Resume.
    " 아직 활성화된 적 없는 새 draft는 TravelID가 비어 있음 → 확인 대상 아님
    DATA active_keys TYPE TABLE FOR READ IMPORT zrap_r_travel_###\\Travel.
    active_keys = VALUE #( FOR key IN keys WHERE ( TravelID IS NOT INITIAL )
                           ( %is_draft = if_abap_behv=>mk-off
                             %key      = key-%key ) ).
    CHECK active_keys IS NOT INITIAL.

    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        FIELDS ( TravelID OverallStatus )
        WITH active_keys
      RESULT DATA(active_travels).

    LOOP AT active_travels INTO DATA(active) WHERE OverallStatus = travel_status-accepted.
      APPEND VALUE #( %is_draft = if_abap_behv=>mk-on
                      %key      = active-%key
                      %fail     = VALUE #( cause = if_abap_behv=>cause-disabled ) ) TO failed-travel.
      APPEND VALUE #( %is_draft = if_abap_behv=>mk-on
                      %key      = active-%key
                      %msg      = NEW zcm_rap_###( textid    = zcm_rap_###=>travel_accepted_meanwhile
                                                   travel_id = active-TravelID
                                                   severity  = if_abap_behv_message=>severity-error ) )
        TO reported-travel.
    ENDLOOP.
  ENDMETHOD.

ENDCLASS.


**********************************************************************
* 세이버: 저장 단계 (R-01의 adjust_numbers 그대로)
**********************************************************************
CLASS lsc_zrap_r_travel_### DEFINITION INHERITING FROM cl_abap_behavior_saver.
  PROTECTED SECTION.
    METHODS adjust_numbers REDEFINITION.
  PRIVATE SECTION.
    TYPES: BEGIN OF ty_max_booking,
             travel_id      TYPE /dmo/travel_id,
             max_booking_id TYPE /dmo/booking_id,
           END OF ty_max_booking.
ENDCLASS.


CLASS lsc_zrap_r_travel_### IMPLEMENTATION.

  METHOD adjust_numbers.
    "--- Travel: SELECT MAX + 1 (number range object 없이)
    IF mapped-travel IS NOT INITIAL.
      SELECT SINGLE FROM zrap_atrav_### FIELDS MAX( travel_id ) INTO @DATA(max_travel_id).
      LOOP AT mapped-travel ASSIGNING FIELD-SYMBOL(<travel>).
        max_travel_id += 1.
        <travel>-TravelID = max_travel_id.
      ENDLOOP.
    ENDIF.

    "--- Booking: 부모 TravelID 결정 후 Travel별 MAX + 10
    IF mapped-booking IS NOT INITIAL.
      READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
        ENTITY Booking BY \_Travel
          FROM VALUE #( FOR booking IN mapped-booking WHERE ( %tmp-TravelID IS INITIAL )
                        ( %pid = booking-%pid
                          %key = booking-%tmp ) )
        LINK DATA(booking_to_travel_links).

      LOOP AT mapped-booking ASSIGNING FIELD-SYMBOL(<booking>).
        <booking>-TravelID = COND #( WHEN <booking>-%tmp-TravelID IS INITIAL
                                     THEN mapped-travel[ %pid = booking_to_travel_links[ source-%pid = <booking>-%pid ]-target-%pid ]-TravelID
                                     ELSE <booking>-%tmp-TravelID ).
      ENDLOOP.

      DATA travel_id_range TYPE RANGE OF /dmo/travel_id.
      travel_id_range = VALUE #( FOR GROUPS grp OF b IN mapped-booking GROUP BY b-TravelID
                                 ( sign = 'I' option = 'EQ' low = grp ) ).

      DATA max_bookings TYPE HASHED TABLE OF ty_max_booking WITH UNIQUE KEY travel_id.
      SELECT FROM zrap_abook_###
        FIELDS travel_id, MAX( booking_id ) AS max_booking_id
        WHERE travel_id IN @travel_id_range
        GROUP BY travel_id
        INTO TABLE @max_bookings.

      LOOP AT mapped-booking ASSIGNING <booking> GROUP BY <booking>-TravelID INTO DATA(travel_group).
        DATA(max_booking_id) = VALUE /dmo/booking_id( max_bookings[ travel_id = travel_group ]-max_booking_id OPTIONAL ).
        LOOP AT GROUP travel_group ASSIGNING FIELD-SYMBOL(<booking_in_group>).
          max_booking_id += 10.
          <booking_in_group>-BookingID = max_booking_id.
        ENDLOOP.
      ENDLOOP.
    ENDIF.
  ENDMETHOD.

ENDCLASS.
```

**행동 풀 `ZBP_RAP_R_BOOKING_###`** — 글로벌 클래스는 2단계 그대로, 로컬 타입 탭 전체:

```abap
**********************************************************************
* 핸들러: Booking 엔터티
**********************************************************************
CLASS lhc_booking DEFINITION INHERITING FROM cl_abap_behavior_handler.
  PRIVATE SECTION.

    CONSTANTS:
      BEGIN OF booking_status,
        new       TYPE /dmo/booking_status VALUE 'N', "New
        booked    TYPE /dmo/booking_status VALUE 'B', "Booked
        cancelled TYPE /dmo/booking_status VALUE 'X', "Cancelled
      END OF booking_status,
      BEGIN OF state_area,
        connection TYPE string VALUE 'VALIDATE_CONNECTION',
        status     TYPE string VALUE 'VALIDATE_STATUS',
      END OF state_area.

    METHODS setInitialBookingValues FOR DETERMINE ON MODIFY
      IMPORTING keys FOR Booking~setInitialBookingValues.

    METHODS calculateTotalPrice FOR DETERMINE ON MODIFY
      IMPORTING keys FOR Booking~calculateTotalPrice.

    METHODS validateConnection FOR VALIDATE ON SAVE
      IMPORTING keys FOR Booking~validateConnection.

    METHODS validateStatus FOR VALIDATE ON SAVE
      IMPORTING keys FOR Booking~validateStatus.

    METHODS getDaysToFlight FOR READ
      IMPORTING keys FOR FUNCTION Booking~getDaysToFlight RESULT result.

ENDCLASS.


CLASS lhc_booking IMPLEMENTATION.

**********************************************************************
* 결정 on modify { create; }: 예약일, 고객(부모에서 복사), 상태 N
**********************************************************************
  METHOD setInitialBookingValues.
    " 부모 Travel의 고객 번호 (같은 Travel의 Booking이 여러 개여도 Travel은 한 번만 옴)
    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Booking BY \_Travel
        FIELDS ( CustomerID )
        WITH CORRESPONDING #( keys )
      RESULT DATA(travels)
      LINK DATA(booking_to_travel).

    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Booking
        FIELDS ( CustomerID BookingDate BookingStatus )
        WITH CORRESPONDING #( keys )
      RESULT DATA(bookings).

    DELETE bookings WHERE CustomerID    IS NOT INITIAL
                      AND BookingDate   IS NOT INITIAL
                      AND BookingStatus IS NOT INITIAL.
    CHECK bookings IS NOT INITIAL.

    DATA(today) = cl_abap_context_info=>get_system_date( ).
    DATA bookings_upd TYPE TABLE FOR UPDATE zrap_r_travel_###\\Booking.

    LOOP AT bookings INTO DATA(booking).
      APPEND VALUE #( %tky = booking-%tky ) TO bookings_upd ASSIGNING FIELD-SYMBOL(<upd>).
      IF booking-CustomerID IS INITIAL.
        <upd>-CustomerID = VALUE #( travels[ KEY id %tky = booking_to_travel[ KEY id source-%tky = booking-%tky ]-target-%tky ]-CustomerID OPTIONAL ).
        <upd>-%control-CustomerID = if_abap_behv=>mk-on.
      ENDIF.
      IF booking-BookingDate IS INITIAL.
        <upd>-BookingDate          = today.
        <upd>-%control-BookingDate = if_abap_behv=>mk-on.
      ENDIF.
      IF booking-BookingStatus IS INITIAL.
        <upd>-BookingStatus          = booking_status-new.
        <upd>-%control-BookingStatus = if_abap_behv=>mk-on.
      ENDIF.
    ENDLOOP.

    MODIFY ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Booking
        UPDATE FROM bookings_upd.
  ENDMETHOD.

**********************************************************************
* 결정 on modify { create; field FlightPrice, CurrencyCode; }
* → 부모의 내부 액션 reCalcTotalPrice 실행
**********************************************************************
  METHOD calculateTotalPrice.
    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Booking BY \_Travel
        FIELDS ( TravelID )
        WITH CORRESPONDING #( keys )
      RESULT DATA(travels).

    MODIFY ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        EXECUTE reCalcTotalPrice
        FROM CORRESPONDING #( travels ).
  ENDMETHOD.

**********************************************************************
* 검증: 항공편 존재 + 여행 기간 안인지(경고)
**********************************************************************
  METHOD validateConnection.
    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Booking
        FIELDS ( BookingID CarrierID ConnectionID FlightDate )
        WITH CORRESPONDING #( keys )
      RESULT DATA(bookings).

    " 부모 Travel (메시지의 %path, 여행 기간 확인용)
    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Booking BY \_Travel
        FIELDS ( BeginDate EndDate )
        WITH CORRESPONDING #( bookings )
      RESULT DATA(travels)
      LINK DATA(booking_to_travel).

    " 존재 확인은 한 번의 SELECT로
    DATA flights_req TYPE SORTED TABLE OF /dmo/flight WITH UNIQUE KEY carrier_id connection_id flight_date.
    DATA flights_db  TYPE SORTED TABLE OF /dmo/flight WITH UNIQUE KEY carrier_id connection_id flight_date.
    flights_req = CORRESPONDING #( bookings DISCARDING DUPLICATES
                                   MAPPING carrier_id    = CarrierID
                                           connection_id = ConnectionID
                                           flight_date   = FlightDate EXCEPT * ).
    DELETE flights_req WHERE carrier_id IS INITIAL OR connection_id IS INITIAL OR flight_date IS INITIAL.

    IF flights_req IS NOT INITIAL.
      SELECT FROM /dmo/flight
        FIELDS *
        FOR ALL ENTRIES IN @flights_req
        WHERE carrier_id    = @flights_req-carrier_id
          AND connection_id = @flights_req-connection_id
          AND flight_date   = @flights_req-flight_date
        INTO TABLE @flights_db.
    ENDIF.

    LOOP AT bookings INTO DATA(booking).
      DATA(travel_tky) = booking_to_travel[ KEY id source-%tky = booking-%tky ]-target-%tky.

      APPEND VALUE #( %tky        = booking-%tky
                      %state_area = state_area-connection ) TO reported-booking.

      IF booking-CarrierID IS INITIAL OR booking-ConnectionID IS INITIAL OR booking-FlightDate IS INITIAL.
        APPEND VALUE #( %tky = booking-%tky ) TO failed-booking.
        APPEND VALUE #( %tky                  = booking-%tky
                        %state_area           = state_area-connection
                        %msg                  = NEW zcm_rap_###( textid   = zcm_rap_###=>enter_flight
                                                                 severity = if_abap_behv_message=>severity-error )
                        %path                 = VALUE #( travel-%tky = travel_tky )
                        %element-CarrierID    = if_abap_behv=>mk-on
                        %element-ConnectionID = if_abap_behv=>mk-on
                        %element-FlightDate   = if_abap_behv=>mk-on ) TO reported-booking.

      ELSEIF NOT line_exists( flights_db[ carrier_id    = booking-CarrierID
                                          connection_id = booking-ConnectionID
                                          flight_date   = booking-FlightDate ] ).
        APPEND VALUE #( %tky = booking-%tky ) TO failed-booking.
        APPEND VALUE #( %tky                  = booking-%tky
                        %state_area           = state_area-connection
                        %msg                  = NEW zcm_rap_###( textid        = zcm_rap_###=>flight_unknown
                                                                 carrier_id    = booking-CarrierID
                                                                 connection_id = booking-ConnectionID
                                                                 flight_date   = booking-FlightDate
                                                                 severity      = if_abap_behv_message=>severity-error )
                        %path                 = VALUE #( travel-%tky = travel_tky )
                        %element-ConnectionID = if_abap_behv=>mk-on
                        %element-FlightDate   = if_abap_behv=>mk-on ) TO reported-booking.

      ELSE.
        " 경고: 저장은 막지 않음 → failed에 넣지 않음
        DATA(travel) = travels[ KEY id %tky = travel_tky ].
        IF booking-FlightDate < travel-BeginDate OR booking-FlightDate > travel-EndDate.
          APPEND VALUE #( %tky                = booking-%tky
                          %state_area         = state_area-connection
                          %msg                = NEW zcm_rap_###( textid      = zcm_rap_###=>flight_outside_travel
                                                                 flight_date = booking-FlightDate
                                                                 severity    = if_abap_behv_message=>severity-warning )
                          %path               = VALUE #( travel-%tky = travel_tky )
                          %element-FlightDate = if_abap_behv=>mk-on ) TO reported-booking.
        ENDIF.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

**********************************************************************
* 검증: 예약 상태 N/B/X
**********************************************************************
  METHOD validateStatus.
    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Booking
        FIELDS ( BookingStatus )
        WITH CORRESPONDING #( keys )
      RESULT DATA(bookings).

    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Booking BY \_Travel
        FROM CORRESPONDING #( bookings )
      LINK DATA(booking_to_travel).

    LOOP AT bookings INTO DATA(booking).
      APPEND VALUE #( %tky        = booking-%tky
                      %state_area = state_area-status ) TO reported-booking.

      IF booking-BookingStatus <> booking_status-new
     AND booking-BookingStatus <> booking_status-booked
     AND booking-BookingStatus <> booking_status-cancelled.
        APPEND VALUE #( %tky = booking-%tky ) TO failed-booking.
        APPEND VALUE #( %tky                   = booking-%tky
                        %state_area            = state_area-status
                        %msg                   = NEW zcm_rap_###( textid   = zcm_rap_###=>booking_status_invalid
                                                                  status   = booking-BookingStatus
                                                                  severity = if_abap_behv_message=>severity-error )
                        %path                  = VALUE #( travel-%tky = booking_to_travel[ KEY id source-%tky = booking-%tky ]-target-%tky )
                        %element-BookingStatus = if_abap_behv=>mk-on ) TO reported-booking.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

**********************************************************************
* 인스턴스 함수: 비행까지 남은 일수 (데이터 변경 없음, 잠금 없음)
**********************************************************************
  METHOD getDaysToFlight.
    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Booking
        FIELDS ( BookingDate FlightDate )
        WITH CORRESPONDING #( keys )
      RESULT DATA(bookings)
      FAILED failed.

    DATA(today) = cl_abap_context_info=>get_system_date( ).

    LOOP AT bookings INTO DATA(booking).
      DATA(initial_days)   = COND i( WHEN booking-FlightDate IS INITIAL OR booking-BookingDate IS INITIAL THEN 0
                                     ELSE booking-FlightDate - booking-BookingDate ).
      DATA(remaining_days) = COND i( WHEN booking-FlightDate IS INITIAL THEN -1
                                     ELSE booking-FlightDate - today ).

      APPEND VALUE #( %tky                            = booking-%tky
                      %param-initial_days_to_flight   = nmax( val1 = initial_days val2 = 0 )
                      %param-remaining_days_to_flight = nmax( val1 = remaining_days val2 = 0 )
                      " 1 = 빨강(0~2일), 2 = 주황(3~5일), 3 = 초록(6일 이상), 0 = 지남/모름
                      %param-days_to_flight_indicator = COND #( WHEN remaining_days >= 6 THEN 3
                                                                WHEN remaining_days >= 3 THEN 2
                                                                WHEN remaining_days >= 0 THEN 1
                                                                ELSE 0 ) ) TO result.
    ENDLOOP.
  ENDMETHOD.

ENDCLASS.
```

**왜 이렇게 쓰나**

- **프로젝션 BDEF는 "공개 목록"** 입니다. 기본 BDEF에 정의한 것이라도 `use`로 적지 않으면 OData 서비스에 나가지 않습니다. 같은 BO로 UI 서비스와 Web API 서비스에 서로 다른 액션을 공개할 수 있는 이유입니다.
- **기본값 함수도 `use function`** 으로 노출합니다(Flight Reference Scenario `/DMO/C_Travel_D_D`의 `use function GetDefaultsFordeductDiscount;`). `GetDefaultsForCreate`를 같은 방식으로 노출하는 부분은 공식 예제에서 확인하지 못했습니다. 활성화 시 오류가 나면 해당 줄의 필요 여부를 ADT 오류 메시지로 확인하세요 (실제 시스템에서 확인 필요).
- `use action checkDates;`: 사이드 이펙트가 Fiori에서 determine action을 호출하므로 프로젝션에 공개되어 있어야 합니다(RAP110 프로젝션 BDEF와 같음).
- `use side effects;`는 헤더(전체)에 한 번. 프로젝션 BDEF 안에 별도의 `side effects { … }`를 정의할 수도 있습니다(RAP110은 Booking 프로젝션에서 가상 요소용 사이드 이펙트를 정의).
- 내부 액션 `reCalcTotalPrice`는 `use`할 수 없습니다. BO 밖에서는 존재하지 않는 것처럼 동작합니다.

**클래스 구조 해설 (전체 요약)**

| BDEF 줄 | 메서드(핸들러) | 호출 시점 |
|---|---|---|
| `update/delete/association create ( features : instance )`, `Edit ( features : instance )`, `action ( features : instance )` | `get_instance_features` FOR INSTANCE FEATURES | UI가 화면을 읽을 때, 작업 실행 직전 |
| `authorization master ( global )` | `get_global_authorizations` | 작업 실행 전, UI 버튼 상태 결정 |
| `determination … on modify` | FOR DETERMINE ON MODIFY | 버퍼 변경 직후 |
| `determination … on save` | FOR DETERMINE ON SAVE | save sequence / Prepare |
| `validation … on save` | FOR VALIDATE ON SAVE | save sequence / Prepare / determine action |
| `action`, `internal action`, `factory action`, `static … factory action`, `repeatable action` | FOR MODIFY … FOR ACTION | EXECUTE 시 |
| `function`, `static function`, `default function` | FOR READ … FOR FUNCTION | READ … EXECUTE 시, 팝업/화면 열 때(기본값) |
| `draft action Resume with additional implementation` | FOR MODIFY … FOR ACTION Travel~Resume | 잠금 만료 draft 재수정 시 |
| `late numbering` | 세이버 `adjust_numbers` | save sequence 끝(번호 확정) |
| `determine action`, `side effects`, `draft action Edit/Activate/Discard/Prepare` | 없음(프레임워크) | |

- 핸들러(`lhc_*`)는 상호작용 단계(트랜잭션 버퍼)를, 세이버(`lsc_*`)는 저장 단계를 담당합니다. 이 문제의 모든 행동은 핸들러에 있고, 세이버는 R-01의 번호 부여만 합니다. 이후 문제에서 `with additional save`나 이벤트를 다룰 때 세이버를 확장합니다.
- Booking 핸들러는 다른 행동 풀에 있지만 같은 BO(`FOR BEHAVIOR OF zrap_r_travel_###`)이므로 `IN LOCAL MODE`로 Travel의 내부 액션을 실행할 수 있습니다.

**자주 나는 오류와 해결**

- 프로젝션 BDEF 활성화 오류 "action … is not defined in base" → 기본 BDEF를 먼저 활성화하세요(기본 → 행동 풀 → 프로젝션 → MDE 순서).
- Preview에서 버튼은 보이는데 누르면 "Action not found" → 서비스 바인딩을 다시 Publish하거나(Unpublish/Publish) 브라우저 캐시를 지우세요.
- 활성화 순서상 서로 의존해 오류가 반복되면, 기본 BDEF와 두 행동 풀을 함께 선택해 **Activate All**(Ctrl+Shift+F3)로 한 번에 활성화하세요.

</details>

## 출처

- SAP-samples/abap-cheat-sheets — 36_RAP_Behavior_Definition_Language.md (필드 특성, 작업·액션·함수·팩토리·repeatable·default function, Draft 액션, 결정·검증·determine action, 사이드 이펙트 대상): https://github.com/SAP-samples/abap-cheat-sheets/blob/main/36_RAP_Behavior_Definition_Language.md
- SAP-samples/abap-cheat-sheets — 08_EML_ABAP_for_RAP.md (`%cid`/`%cid_ref`, 핸들러 시그니처): https://github.com/SAP-samples/abap-cheat-sheets/blob/main/08_EML_ABAP_for_RAP.md
- SAP-samples/abap-cheat-sheets — 33_ABAP_Release_News.md (repeatable 액션·함수의 `%cid`, static default factory action, default values function): https://github.com/SAP-samples/abap-cheat-sheets/blob/main/33_ABAP_Release_News.md
- SAP-samples/abap-platform-rap110 — `zrap110_r_traveltp_sol`/`zrap110_c_traveltp_sol` BDEF, `zrap110_bp_traveltp_sol`/`zrap110_bp_bookingtp_sol` 행동 풀, 추상 엔터티 `zrap110_a_create_travel_sol`/`zrap110_a_daystoflight_sol`, MDE `zrap110_c_traveltp_sol`, `zrap110_calc_book_elem_sol`: https://github.com/SAP-samples/abap-platform-rap110/tree/main/src
- SAP-samples/abap-platform-rap110 — exercises ex03, ex05, ex07, ex09, ex10 README: https://github.com/SAP-samples/abap-platform-rap110/tree/main/exercises
- SAP-samples/abap-platform-refscen-flight (ABAP-platform-cloud) — `draft/`: `/DMO/R_Travel_D` BDEF, `/DMO/C_Travel_D_D` 프로젝션 BDEF·MDE, `/DMO/BP_TRAVEL_D`(deductDiscount, GetDefaultsFordeductDiscount, get_instance_features, resume), `/DMO/BP_BOOKING_D`(validateConnection의 %path), `/DMO/A_Travel_Discount`: https://github.com/SAP-samples/abap-platform-refscen-flight/tree/ABAP-platform-cloud/src/draft
- SAP-samples/abap-platform-refscen-flight — `reuse/`: `/DMO/CM_FLIGHT_MESSAGES` 예외 클래스, `/DMO/CM_FLIGHT` 메시지 클래스, 값 도움말 뷰 `/DMO/I_Flight_StdVH`·`/DMO/I_Agency_StdVH`·`/DMO/I_Customer_StdVH`: https://github.com/SAP-samples/abap-platform-refscen-flight/tree/ABAP-platform-cloud/src/reuse
- SAP-samples/abap-platform-rap100 — exercises/ex06 README (deductDiscount, copyTravel 팩토리 액션과 UI 노출): https://github.com/SAP-samples/abap-platform-rap100/tree/main/exercises/ex06
