## 1. 관리형(Managed) BO와 Draft

### R-03. 동시성 제어·기능 제어·권한·인터페이스 계층 [작성] ★★★
<!-- covers: etag master, total etag, lock master, lock dependent by, etag dependent by, use etag, lock : none, exclusive lock phase, optimistic lock phase, SET LOCKS, features : instance, features : global, get_instance_features, get_global_features, %features, %field, %action, %assoc, fc-o-disabled, fc-f-read_only, authorization master ( global, instance ), authorization dependent by, authorization : update, get_global_authorizations, get_instance_authorizations, AUTHORITY-CHECK OBJECT /DMO/TRVL, precheck, precheck_create, precheck_update, with privileged mode disabling, define authorization context, define own authorization context, PRIVILEGED, cl_abap_behv_aux, GET PERMISSIONS, @AccessControl.authorizationCheck, define role, @MappingRole, inheriting conditions from entity, aspect pfcg_auth, draft query view, transactional_interface, interface BDEF, use draft, Web API, OData V4 Web API, release contract C1 -->
**목표**
- ETag(낙관적 잠금)와 잠금(비관적 잠금)이 BDEF의 어느 줄에서 켜지는지 알고, 충돌을 브라우저 두 개와 EML 콘솔 클래스로 직접 일으켜 볼 수 있습니다.
- 인스턴스 기능 제어(필드·update/delete·액션·Edit·하위 생성)와 전역 기능 제어(create, static action)를 구현할 수 있습니다.
- 전역/인스턴스 권한, 권한 위임(`authorization : update`), precheck, privileged mode를 BDEF와 행동 구현에서 모두 다룰 수 있습니다.
- CDS 접근 제어(DCL)와 draft 쿼리 뷰로 "읽기" 권한을 거는 방법을 압니다.
- 인터페이스 계층(`transactional_interface` 프로젝션 + 인터페이스 BDEF)을 만들고 OData V4 Web API로 내보낼 수 있습니다.

**전제**
- R-01에서 만든 draft + late numbering Travel/Booking BO(`ZRAP_R_TRAVEL_###`, `ZRAP_R_BOOKING_###`, `ZRAP_C_TRAVEL_###`, `ZRAP_C_BOOKING_###`, 서비스 `ZRAP_UI_TRAVEL_O4_###`)가 활성화되어 있고 Fiori 미리보기가 동작합니다.
- R-02에서 만든 메시지 클래스 `ZRAP_MSG_###`(001~015 사용 중), 예외 클래스 `ZCM_RAP_###`(생성자 파라미터 `textid`, `severity`, `previous`, `travel_id`, `booking_id`, `customer_id`, `agency_id`, `begin_date`, `end_date`, `carrier_id`, `connection_id`, `flight_date`, `status` / 속성 `mv_...`), 액션 `acceptTravel`, `rejectTravel`, `deductDiscount`, `copyTravel`, `createTravel`, `addServiceFee`, 함수 `getOpenTravelCount`, `getDaysToFlight`, determine action `checkDates`가 있습니다. R-02까지는 `authorization master ( global )`입니다.
- R-01의 R 뷰 별칭은 `TravelID, AgencyID, CustomerID, BeginDate, EndDate, BookingFee, TotalPrice, CurrencyCode, Description, OverallStatus, Attachment, MimeType, FileName, CreatedBy, CreatedAt, LocalLastChangedBy, LocalLastChangedAt, LastChangedAt` / Booking은 `TravelID, BookingID, BookingDate, CustomerID, CarrierID, ConnectionID, FlightDate, FlightPrice, CurrencyCode, BookingStatus, LocalLastChangedAt` 라고 가정합니다. 이름이 다르면 R-01 쪽 이름으로 바꿔 쓰세요.
- 표준 객체: `/DMO/I_Agency`(대행사 국가 `CountryCode`), 권한 객체 `/DMO/TRVL`(필드 `/DMO/CNTRY`, `ACTVT`).

**만들 객체**

| 순서 | 객체 유형 | 이름 | 역할 |
|---|---|---|---|
| 1 | 데이터베이스 테이블 | `ZRAP_CTRL_###` | 실습용 스위치(생성 마감, 일요일 마감, 권한 거부 국가) |
| 2 | 클래스(콘솔) | `ZCL_RAP_R03_CTRL_###` | 스위치 값 설정 |
| 3 | 메시지·예외 클래스 확장 | `ZRAP_MSG_###` 030~033, `ZCM_RAP_###` | 권한·마감·알림 메시지 |
| 4 | 클래스(콘솔) 2개 | `ZCL_RAP_R03_LOCK_A_###`, `ZCL_RAP_R03_LOCK_B_###` | 잠금 충돌 관찰 |
| 5 | BDEF 변경 | `ZRAP_R_TRAVEL_###`, `ZRAP_C_TRAVEL_###` | etag/lock/features/authorization/precheck/privileged |
| 6 | 행동 풀 변경 | `ZBP_RAP_R_TRAVEL_###` | 기능 제어·권한·precheck 메서드 |
| 7 | 접근 제어(DCL) | `ZRAP_R_TRAVEL_###`, `ZRAP_C_TRAVEL_###`, `ZRAP_I_TRAVEL_###`, `ZRAP_R_BOOKING_###`, `ZRAP_C_BOOKING_###`, `ZRAP_I_BOOKING_###`, `ZRAP_R_TRAVELDRAFT_###` | CDS 읽기 권한 |
| 8 | 데이터 정의 | `ZRAP_R_TRAVELDRAFT_###` | Travel draft 쿼리 뷰 |
| 9 | 데이터 정의 2개 | `ZRAP_I_TRAVEL_###`, `ZRAP_I_BOOKING_###` | 인터페이스 프로젝션 |
| 10 | BDEF | `ZRAP_I_TRAVEL_###` | 인터페이스 BDEF |
| 11 | 데이터 정의 2개 + BDEF | `ZRAP_W_TRAVEL_###`, `ZRAP_W_BOOKING_###` | Web API용 프로젝션(I 뷰 위, `transactional_query`) |
| 12 | 서비스 정의 / 바인딩 | `ZRAP_API_TRAVEL_###` / `ZRAP_API_TRAVEL_O4_###` | OData V4 Web API |
| 13 | 클래스(콘솔) | `ZCL_RAP_R03_EML_###` | 기능 제어·권한·privileged EML 확인 |

#### 1단계. 실습용 스위치 테이블과 메시지 준비

트라이얼에서는 권한 역할을 마음대로 줄 수 없고, "마감일"도 기다릴 수 없습니다. 그래서 동작을 켜고 끌 수 있는 작은 스위치 테이블을 먼저 만듭니다.

1. 데이터베이스 테이블 `ZRAP_CTRL_###`를 만드세요(설명 `R-03 control switches`). 필드는 아래 표와 같습니다.

| 필드 | 키 | 데이터 엘리먼트(또는 내장 타입) | 타입 | 길이 | 소수 | 설명 |
|---|---|---|---|---|---|---|
| client | X | abap.clnt | CLNT | 3 | 0 | 클라이언트 |
| ctrl_id | X | abap.char(10) | CHAR | 10 | 0 | 스위치 묶음 ID(항상 `TRAVEL`) |
| create_closed |  | abap_boolean | CHAR | 1 | 0 | `X`면 Travel 생성 마감 |
| sunday_closed |  | abap_boolean | CHAR | 1 | 0 | `X`면 일요일에 생성 마감 |
| deny_country |  | land1 | CHAR | 3 | 0 | 이 국가 대행사의 Travel은 권한 없음으로 시뮬레이션 |

2. 콘솔 클래스 `ZCL_RAP_R03_CTRL_###`(`if_oo_adt_classrun`)를 만드세요. 클래스 상단 상수 세 개(`c_create_closed`, `c_sunday_closed`, `c_deny_country`)를 바꾸고 F9로 실행하면 `ctrl_id = 'TRAVEL'` 줄이 그 값으로 덮어써져야 합니다. 그리고 현재 Travel 데이터에 쓰인 대행사 국가별 건수를 출력해서, 어떤 국가를 거부 국가로 고를지 보여 주세요.
3. 메시지 클래스 `ZRAP_MSG_###`에 아래 메시지를 추가하세요.
   - 030 `Creating travels is closed at the moment.`
   - 031 `You are not authorized for this operation.`
   - 032 `No authorization for agency &1 (country &2).`
   - 033 `Reminder for travel &1 was sent to customer &2.`
4. R-02의 예외 클래스 `ZCM_RAP_###`를 확장하세요. 텍스트 ID 상수 `create_closed`, `not_authorized`, `not_authorized_country`, `reminder_sent`, 속성 `mv_country_code`(TYPE land1), 생성자 선택 파라미터 `country_code`를 추가합니다. 메시지 변수는 032가 `MV_AGENCY_ID`, `MV_COUNTRY_CODE`, 033이 `MV_TRAVEL_ID`, `MV_CUSTOMER_ID`입니다.

**확인**
- 테이블과 두 클래스가 활성화됩니다.
- 콘솔 클래스를 실행하면 `CTRL_ID = TRAVEL` 한 줄과 국가별 Travel 건수가 출력됩니다. Data Preview(F8)로 `ZRAP_CTRL_###`를 열어도 같은 값이 보입니다.

<details><summary>정답·해설</summary>

```abap
@EndUserText.label : 'R-03 control switches'
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table zrap_ctrl_### {
  key client    : abap.clnt not null;
  key ctrl_id   : abap.char(10) not null;
  create_closed : abap_boolean;
  sunday_closed : abap_boolean;
  deny_country  : land1;
}
```

```abap
CLASS zcl_rap_r03_ctrl_### DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_oo_adt_classrun.

    "Change these three values and run the class again (F9)
    CONSTANTS c_create_closed TYPE abap_boolean VALUE abap_false.
    CONSTANTS c_sunday_closed TYPE abap_boolean VALUE abap_true.
    CONSTANTS c_deny_country  TYPE land1        VALUE ''.

  PRIVATE SECTION.
    CONSTANTS c_ctrl_id TYPE c LENGTH 10 VALUE 'TRAVEL'.
ENDCLASS.


CLASS zcl_rap_r03_ctrl_### IMPLEMENTATION.

  METHOD if_oo_adt_classrun~main.

    "Write the switch row (insert or overwrite)
    MODIFY zrap_ctrl_### FROM @( VALUE zrap_ctrl_###( ctrl_id       = c_ctrl_id
                                                      create_closed = c_create_closed
                                                      sunday_closed = c_sunday_closed
                                                      deny_country  = c_deny_country ) ).

    SELECT SINGLE FROM zrap_ctrl_###
      FIELDS ctrl_id, create_closed, sunday_closed, deny_country
      WHERE ctrl_id = @c_ctrl_id
      INTO @DATA(ctrl).
    out->write( data = ctrl name = `Current switches` ).

    "Which agency countries are used by the saved travels?
    SELECT FROM zrap_atrav_### AS travel
      INNER JOIN /dmo/i_agency AS agency ON travel~agency_id = agency~AgencyID
      FIELDS agency~CountryCode, COUNT( * ) AS travel_count
      GROUP BY agency~CountryCode
      ORDER BY agency~CountryCode
      INTO TABLE @DATA(countries).
    out->write( data = countries name = `Travels per agency country` ).

  ENDMETHOD.

ENDCLASS.
```

`ZCM_RAP_###`에 추가할 부분(R-02 클래스의 PUBLIC SECTION과 생성자에 넣습니다):

```abap
    "--- R-03: new text IDs ---------------------------------------
    CONSTANTS:
      BEGIN OF create_closed,
        msgid TYPE symsgid VALUE 'ZRAP_MSG_###',
        msgno TYPE symsgno VALUE '030',
        attr1 TYPE scx_attrname VALUE '',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF create_closed,
      BEGIN OF not_authorized,
        msgid TYPE symsgid VALUE 'ZRAP_MSG_###',
        msgno TYPE symsgno VALUE '031',
        attr1 TYPE scx_attrname VALUE '',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF not_authorized,
      BEGIN OF not_authorized_country,
        msgid TYPE symsgid VALUE 'ZRAP_MSG_###',
        msgno TYPE symsgno VALUE '032',
        attr1 TYPE scx_attrname VALUE 'MV_AGENCY_ID',
        attr2 TYPE scx_attrname VALUE 'MV_COUNTRY_CODE',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF not_authorized_country,
      BEGIN OF reminder_sent,
        msgid TYPE symsgid VALUE 'ZRAP_MSG_###',
        msgno TYPE symsgno VALUE '033',
        attr1 TYPE scx_attrname VALUE 'MV_TRAVEL_ID',
        attr2 TYPE scx_attrname VALUE 'MV_CUSTOMER_ID',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF reminder_sent.

    "--- R-03: new attribute -------------------------------------
    DATA mv_country_code TYPE land1 READ-ONLY.

    "--- 생성자 선언(METHODS constructor IMPORTING …)의 맨 끝을 이렇게 바꿈 ---
    "        status        TYPE /dmo/booking_status OPTIONAL      ← 마침표를 지우고
    "        country_code  TYPE land1 OPTIONAL.                   ← 이 줄 추가
```

생성자 구현(`METHOD constructor`)에도 `mv_status = status.` 아래에 한 줄을 추가하세요. 이걸 빠뜨리면 행동 풀에서 `country_code = …`를 넘길 때 "The formal parameter COUNTRY_CODE does not exist" 오류가 납니다.

```abap
    mv_country_code = country_code.
```

해설
- 스위치 테이블은 "운영 데이터"가 아니라 실습 장치입니다. 실제 시스템이라면 전역 기능 제어는 회사 달력 API나 Business Configuration 앱으로, 권한은 IAM 비즈니스 역할로 해결합니다.
- `deliveryClass #A`로 두었습니다. 고객 설정 성격이라면 `#C`를 쓰는 것이 일반적이지만, 트라이얼 실습에서는 차이가 드러나지 않습니다.
- 콘솔 클래스는 RAP 트랜잭션 밖에서 실행되므로 `MODIFY`로 바로 써도 됩니다. 이 클래스를 행동 구현(핸들러) 안에서 부르면 안 됩니다. 인터랙션 단계의 DB 변경은 금지되어 있습니다(R-04 1단계).
- 메시지 변수는 R-02 클래스처럼 `MV_...` 속성 이름을 `attr1~4`에 적습니다. `IF_T100_DYN_MSG`가 이 속성 값을 `&1~&4`에 넣어 줍니다.

자주 나는 오류
- `land1`을 못 찾는다는 오류가 나면 내장 타입 `abap.char(3)`으로 바꿔도 실습에는 지장이 없습니다.

</details>

#### 2단계. 동시성 제어 설정 점검: ETag·total ETag·잠금

R-01에서 이미 넣었을 수도 있는 설정을, 의미를 알고 다시 점검하는 단계입니다.

1. `ZRAP_R_TRAVEL_###` 뷰의 관리 필드 다섯 개에 시스템 필드 어노테이션이 붙어 있는지 확인하세요. 없으면 추가합니다. Booking 뷰의 `LocalLastChangedAt`도 같습니다.
2. BDEF `ZRAP_R_TRAVEL_###`의 Travel 정의 머리에 다음 의미의 줄이 있는지 확인하세요.
   - Travel 한 건의 변경을 추적하는 ETag 필드는 `LocalLastChangedAt`
   - Travel이 잠금의 주인(root)이고, draft의 "다시 이어서 편집 가능 여부"를 판단할 total ETag는 `LastChangedAt`
3. Booking 정의에는 "잠금은 부모 Travel을 따라간다"는 줄과 "Booking 자체 ETag는 `LocalLastChangedAt`"이라는 줄이 있어야 합니다.
4. 프로젝션 BDEF `ZRAP_C_TRAVEL_###`의 두 엔터티가 모두 ETag를 OData로 내보내도록 되어 있는지 확인하세요.
5. 주석으로, Booking이 자기 ETag 필드 없이 부모 ETag를 쓰는 다른 방법(`etag dependent by`)을 한 줄 적어 두세요(실제로 켜지는 않습니다).

**직접 추가할 어노테이션**
- `@Semantics.user.createdBy` — 생성자 사용자를 framework가 자동으로 채우게 함
- `@Semantics.systemDateTime.createdAt` — 생성 시각 자동 기록
- `@Semantics.user.localInstanceLastChangedBy` — 이 인스턴스를 마지막으로 바꾼 사용자 자동 기록
- `@Semantics.systemDateTime.localInstanceLastChangedAt` — 인스턴스 단위 ETag로 쓸 시각 자동 기록
- `@Semantics.systemDateTime.lastChangedAt` — BO 전체(하위 포함) 변경 시각, total ETag로 사용

**확인**
- 뷰와 두 BDEF가 경고 없이 활성화됩니다.
- Fiori 미리보기에서 Travel 하나를 Edit → 설명 변경 → Save 한 뒤 Data Preview로 `ZRAP_ATRAV_###`를 보면 `LOCAL_LAST_CHANGED_AT`, `LAST_CHANGED_AT`이 방금 시각으로 바뀌어 있습니다. 그 Travel의 Booking 하나만 바꿔 저장해도 Travel의 `LAST_CHANGED_AT`이 바뀌는지 관찰해 보세요.

<details><summary>정답·해설</summary>

R 뷰 전체(R-01 정답과 같고, ★ 표시한 첫 줄만 `#CHECK`로 바뀝니다. 관리 필드 다섯 개의 어노테이션을 확인하세요):

```cds
@AccessControl.authorizationCheck: #CHECK          // ★ R-03: DCL이 없으면 경고 (8단계에서 DCL 생성) (→ 어노테이션 탭: @AccessControl.authorizationCheck)
@Metadata.allowExtensions: true                    // MDE 허용 (→ 어노테이션 탭: @Metadata.allowExtensions)
@EndUserText.label: 'Travel - base BO view'        // 설명 (→ 어노테이션 탭: @EndUserText.label)
define root view entity ZRAP_R_TRAVEL_###
  as select from zrap_atrav_### as Travel

  composition [0..*] of ZRAP_R_BOOKING_###       as _Booking

  association [0..1] to /DMO/I_Agency            as _Agency        on $projection.AgencyID      = _Agency.AgencyID
  association [0..1] to /DMO/I_Customer          as _Customer      on $projection.CustomerID    = _Customer.CustomerID
  association [1..1] to /DMO/I_Overall_Status_VH as _OverallStatus on $projection.OverallStatus = _OverallStatus.OverallStatus
  association [0..1] to I_Currency               as _Currency      on $projection.CurrencyCode  = _Currency.Currency
{
  key travel_id             as TravelID,
      agency_id             as AgencyID,
      customer_id           as CustomerID,
      begin_date            as BeginDate,
      end_date              as EndDate,
      @Semantics.amount.currencyCode: 'CurrencyCode'          // 금액 → 통화 요소 (→ 어노테이션 탭: @Semantics.amount.currencyCode)
      booking_fee           as BookingFee,
      @Semantics.amount.currencyCode: 'CurrencyCode'
      total_price           as TotalPrice,
      currency_code         as CurrencyCode,
      description           as Description,
      overall_status        as OverallStatus,
      @Semantics.largeObject: { mimeType: 'MimeType',         // MIME 타입 요소(대소문자 구분) (→ 어노테이션 탭: @Semantics.largeObject)
                                fileName: 'FileName',         // 파일 이름 요소
                                contentDispositionPreference: #ATTACHMENT } // 브라우저에서 내려받기
      attachment            as Attachment,
      @Semantics.mimeType: true                               // MIME 타입 요소 (→ 어노테이션 탭: @Semantics.mimeType)
      mime_type             as MimeType,
      file_name             as FileName,
      @Semantics.user.createdBy: true                         // 생성자 자동 기입 (→ 어노테이션 탭: @Semantics.user.createdBy)
      created_by            as CreatedBy,
      @Semantics.systemDateTime.createdAt: true               // 생성 시각 자동 기입 (→ 어노테이션 탭: @Semantics.systemDateTime.createdAt)
      created_at            as CreatedAt,
      @Semantics.user.localInstanceLastChangedBy: true        // 인스턴스 변경자 자동 기입 (→ 어노테이션 탭: @Semantics.user.localInstanceLastChangedBy)
      local_last_changed_by as LocalLastChangedBy,
      @Semantics.systemDateTime.localInstanceLastChangedAt: true // 인스턴스 ETag (→ 어노테이션 탭: @Semantics.systemDateTime.localInstanceLastChangedAt)
      local_last_changed_at as LocalLastChangedAt,
      @Semantics.systemDateTime.lastChangedAt: true           // total ETag (→ 어노테이션 탭: @Semantics.systemDateTime.lastChangedAt)
      last_changed_at       as LastChangedAt,

      // exposed associations
      _Booking,
      _Agency,
      _Customer,
      _OverallStatus,
      _Currency
}
```

Booking 뷰의 해당 필드:

```cds
      @Semantics.systemDateTime.localInstanceLastChangedAt: true // Booking 인스턴스 ETag 값 (→ 어노테이션 탭: @Semantics.systemDateTime.localInstanceLastChangedAt)
      booking.local_last_changed_at as LocalLastChangedAt,
```

R BDEF의 동시성 관련 줄(두 엔터티의 **머리 부분**입니다. `{` 이후 본문은 R-02 상태 그대로이며, 10단계 정답에 BDEF 전체가 있습니다):

```bdef
define behavior for ZRAP_R_TRAVEL_### alias Travel
persistent table zrap_atrav_###
draft table zrap_dtrav_###
etag master LocalLastChangedAt          // 낙관적 잠금: Travel 인스턴스 ETag
lock master total etag LastChangedAt    // 비관적 잠금의 주인 + draft 재개 판단용 total ETag
authorization master ( global )         // (6단계에서 global, instance 로 바뀜)
late numbering
```

```bdef
define behavior for ZRAP_R_BOOKING_### alias Booking
implementation in class zbp_rap_r_booking_### unique
persistent table zrap_abook_###
draft table zrap_dbook_###
etag master LocalLastChangedAt          // Booking 자체 ETag
// etag dependent by _Travel            // (대안) 자기 ETag 필드 없이 부모 Travel의 ETag를 사용
lock dependent by _Travel               // 잠금은 루트 Travel이 대신 건다
authorization dependent by _Travel      // 권한은 루트 Travel을 따라감 (R-02에서 이미 있음)
late numbering
```

프로젝션 BDEF `ZRAP_C_TRAVEL_###`에서 ETag를 내보내는 줄(두 엔터티의 머리 부분):

```bdef
define behavior for ZRAP_C_TRAVEL_### alias Travel
use etag            // R의 etag master 값을 OData ETag(If-Match)로 내보냄
```

```bdef
define behavior for ZRAP_C_BOOKING_### alias Booking
use etag
```

왜 이렇게 쓰나
- **낙관적 잠금(ETag)**: 읽을 때 받은 ETag 값을 수정 요청에 함께 보내고(OData `If-Match`), 서버의 현재 값과 다르면 거절합니다. 잠금을 오래 잡지 않으므로 웹에 맞습니다. managed BO는 `@Semantics.systemDateTime.localInstanceLastChangedAt` 필드가 있으면 값 갱신과 비교를 framework가 해 줍니다.
- **비관적 잠금(lock)**: 수정 직전에 잠금 테이블(enqueue)에 항목을 넣어 다른 세션의 수정을 막습니다. `lock master`는 루트에만, 자식은 `lock dependent by`로 루트를 따라갑니다. managed에서는 update, delete, create-by-association, 액션 실행 전에 framework가 자동으로 잠급니다.
- **total ETag**: draft BO에서 필수입니다. Edit를 누르면 활성 인스턴스가 **배타 잠금 단계**(exclusive lock phase)에 들어가고, 이 잠금은 ABAP 세션이 끝나도 정해진 시간 동안 유지됩니다. 시간이 지나면 **낙관적 잠금 단계**(optimistic lock phase)가 됩니다. 이때 사용자가 draft를 다시 고치면 `Resume`이 자동 실행되는데, draft에 저장해 둔 total ETag와 활성 인스턴스의 total ETag가 같을 때만 이어서 편집할 수 있습니다. 그동안 다른 사람이 활성 인스턴스를 바꿨다면 재개가 거절됩니다.
- `etag master`와 `total etag`에는 서로 다른 필드를 쓰는 것이 권장됩니다. Booking만 바뀌어도 Travel의 `LastChangedAt`이 바뀌는 이유는 total ETag가 "BO 전체"의 변경 시각이기 때문입니다(실제 갱신 동작은 실제 시스템에서 확인 필요).
- `etag dependent by _Travel`은 자식에 ETag 필드가 없을 때 쓰는 방법입니다. 이 경우 자식을 바꿀 때도 부모 ETag로 충돌을 판단합니다. 이 문제에서는 Booking에 `LocalLastChangedAt`이 있으므로 `etag master`를 씁니다.

자주 나는 오류
- `total etag`를 `lock master` 앞에 쓰면 문법 오류가 납니다. `lock master total etag LastChangedAt`처럼 `lock master` 뒤에 씁니다.

</details>

#### 3단계. 충돌을 직접 일으켜 보기: ETag 충돌, 잠금 충돌, `lock : none`

1. **ETag 충돌(브라우저 두 개)**: 서비스 바인딩 `ZRAP_UI_TRAVEL_O4_###`에서 Fiori 미리보기를 두 탭(A, B)으로 여세요. 두 탭에서 **같은 Open 상태 Travel**의 Object Page(활성 버전, Edit 누르지 않음)를 띄웁니다. B에서 `Accept Travel`을 누르고, A에서는 새로 고침 없이 `Reject Travel`을 누릅니다. A에 무슨 메시지가 뜨는지, 브라우저 개발자 도구(F12) → Network에서 `$batch` 요청 안의 `If-Match` 헤더 값을 확인하세요.
2. **잠금 충돌(EML 콘솔 두 개)**: 클래스 `ZCL_RAP_R03_LOCK_A_###`는 Open 상태 Travel 하나의 활성 인스턴스를 `MODIFY ENTITIES ... UPDATE`(Description 변경)로 수정만 하고 COMMIT하지 않은 채 멈춰 있어야 합니다(디버거 중단점용 `ASSERT 1 = 1.` 줄). 클래스 `ZCL_RAP_R03_LOCK_B_###`는 같은 Travel을 수정하고, `FAILED`의 `%fail-cause`와 `REPORTED` 메시지를 출력해야 합니다. A를 중단점에 세워 둔 채로 B를 실행하세요.
3. **draft 잠금 관찰**: 탭 A에서 그 Travel을 Edit(draft 생성)한 상태로 두고, `ZCL_RAP_R03_LOCK_B_###`를 다시 실행해 결과를 비교하세요.
4. **`lock : none` 액션**: Travel에 `sendReminder` 액션을 추가하세요.
   - 잠금을 걸지 않음, 권한은 update 권한에 위임, 결과는 `$self` 1건
   - 구현: 데이터를 바꾸지 않고, 성공 메시지 033(`Reminder for travel &1 was sent to customer &2.`)만 `reported`에 넣습니다.
   - 프로젝션 BDEF에 `use action`을, MDE에서 R-02가 액션 버튼을 둔 `TravelID` 요소의 lineItem/identification 배열에 버튼을 추가하세요(라벨 `Send Reminder`).
5. 탭 A에서 Travel을 Edit 해 둔 채, 탭 B에서 같은 Travel의 `Send Reminder`와 `Accept Travel`을 각각 눌러 결과를 비교하세요.

**직접 추가할 어노테이션**
- `@UI.lineItem` (type `#FOR_ACTION`) — 목록 표에 액션 버튼을 놓음
- `@UI.identification` (type `#FOR_ACTION`) — Object Page 머리에 액션 버튼을 놓음

**확인**
- 1번: A에서 "다른 사용자가 데이터를 변경했다"는 취지의 오류가 뜹니다(HTTP 412 Precondition Failed). 문구는 UI5 버전에 따라 다를 수 있습니다.
- 2번: B의 출력에 `%fail-cause`가 잠금(`if_abap_behv=>cause-locked`)으로 나오고, 사용자 이름이 들어간 잠금 메시지가 보입니다.
- 4~5번: draft 편집 중이어도 `Send Reminder`는 성공 메시지를 보여 주고, `Accept Travel`은 잠금(또는 draft 존재) 오류로 거절됩니다. 같은 사용자가 두 탭을 쓰면 Fiori가 활성 문서 대신 draft로 안내할 수도 있으므로, 이때는 `ZCL_RAP_R03_LOCK_B_###`를 `acceptTravel` 실행으로 바꿔 비교해도 됩니다(동작은 실제 시스템에서 확인 필요).

<details><summary>정답·해설</summary>

```abap
CLASS zcl_rap_r03_lock_a_### DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_oo_adt_classrun.
ENDCLASS.


CLASS zcl_rap_r03_lock_a_### IMPLEMENTATION.

  METHOD if_oo_adt_classrun~main.

    "Pick one open travel (smallest ID) - class B picks the same one
    SELECT FROM zrap_atrav_###
      FIELDS MIN( travel_id )
      WHERE overall_status = 'O'
      INTO @DATA(travel_id).
    IF travel_id IS INITIAL.
      out->write( `No open travel found.` ).
      RETURN.
    ENDIF.

    "Modify the ACTIVE instance; the framework locks it (lock master)
    MODIFY ENTITIES OF zrap_r_travel_###
      ENTITY Travel
        UPDATE FIELDS ( Description )
        WITH VALUE #( ( %is_draft   = if_abap_behv=>mk-off
                        TravelID    = travel_id
                        Description = |Locked by class A at { utclong_current( ) }| ) )
      FAILED DATA(failed)
      REPORTED DATA(reported).

    out->write( |Travel { travel_id } modified, failed lines: { lines( failed-travel ) }| ).

    "Set a breakpoint here and keep the debugger open -> lock stays
    ASSERT 1 = 1.

    "Nothing is saved: leave the RAP transaction without commit
    ROLLBACK ENTITIES.

  ENDMETHOD.

ENDCLASS.
```

```abap
CLASS zcl_rap_r03_lock_b_### DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_oo_adt_classrun.
ENDCLASS.


CLASS zcl_rap_r03_lock_b_### IMPLEMENTATION.

  METHOD if_oo_adt_classrun~main.

    SELECT FROM zrap_atrav_###
      FIELDS MIN( travel_id )
      WHERE overall_status = 'O'
      INTO @DATA(travel_id).
    IF travel_id IS INITIAL.
      out->write( `No open travel found.` ).
      RETURN.
    ENDIF.

    MODIFY ENTITIES OF zrap_r_travel_###
      ENTITY Travel
        UPDATE FIELDS ( Description )
        WITH VALUE #( ( %is_draft   = if_abap_behv=>mk-off
                        TravelID    = travel_id
                        Description = `Changed by class B` ) )
      FAILED DATA(failed)
      REPORTED DATA(reported).

    IF failed-travel IS INITIAL.
      out->write( |Travel { travel_id }: no conflict, update accepted in the buffer.| ).
    ENDIF.

    LOOP AT failed-travel INTO DATA(failed_line).
      out->write( |Travel { failed_line-TravelID }: fail-cause = { failed_line-%fail-cause }| ).
      IF failed_line-%fail-cause = if_abap_behv=>cause-locked.
        out->write( `-> cause-locked: another session holds the lock` ).
      ENDIF.
    ENDLOOP.

    LOOP AT reported-travel INTO DATA(reported_line) WHERE %msg IS BOUND.
      out->write( reported_line-%msg->if_message~get_text( ) ).
    ENDLOOP.

    "Demo only - do not save anything
    ROLLBACK ENTITIES.

  ENDMETHOD.

ENDCLASS.
```

BDEF(Travel 본문에 추가):

```bdef
  action ( lock : none, authorization : update ) sendReminder result [1] $self;  // 잠금 없이 실행, 권한은 update에 위임
```

프로젝션 BDEF(Travel 본문에 추가):

```bdef
  use action sendReminder;
```

MDE `ZRAP_C_TRAVEL_###`의 `TravelID` 요소(R-02에서 액션 버튼을 둔 곳)에 ★ 두 줄을 추가합니다:

```cds
  @UI.lineItem: [
    { position: 10, importance: #HIGH },
    { type: #FOR_ACTION, dataAction: 'acceptTravel',   label: 'Accept Travel' },
    { type: #FOR_ACTION, dataAction: 'rejectTravel',   label: 'Reject Travel' },
    { type: #FOR_ACTION, dataAction: 'deductDiscount', label: 'Deduct Discount',
      invocationGrouping: #CHANGE_SET },
    { type: #FOR_ACTION, dataAction: 'copyTravel',     label: 'Copy Travel' },
    { type: #FOR_ACTION, dataAction: 'addServiceFee',  label: 'Add Service Fee' },
    { type: #FOR_ACTION, dataAction: 'sendReminder',   label: 'Send Reminder' } ]   // ★ 목록 표 버튼 (→ 어노테이션 탭: @UI.lineItem)
  @UI.identification: [
    { position: 10 },
    { type: #FOR_ACTION, dataAction: 'acceptTravel',   label: 'Accept Travel' },
    { type: #FOR_ACTION, dataAction: 'rejectTravel',   label: 'Reject Travel' },
    { type: #FOR_ACTION, dataAction: 'deductDiscount', label: 'Deduct Discount' },
    { type: #FOR_ACTION, dataAction: 'addServiceFee',  label: 'Add Service Fee' },
    { type: #FOR_ACTION, dataAction: 'sendReminder',   label: 'Send Reminder' },     // ★ Object Page 머리 버튼 (→ 어노테이션 탭: @UI.identification)
    { type: #FOR_ACTION, dataAction: 'acceptTravel',   label: 'Accept', determining: true } ]
  @UI.selectionField: [ { position: 10 } ]
  TravelID;
```

행동 풀 `ZBP_RAP_R_TRAVEL_###`의 `lhc_travel` 정의부에 선언 추가:

```abap
    METHODS sendReminder FOR MODIFY
      IMPORTING keys FOR ACTION Travel~sendReminder RESULT result.
```

구현:

```abap
  METHOD sendReminder.

    "Action result is $self -> all fields are needed for %param
    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        ALL FIELDS WITH CORRESPONDING #( keys )
      RESULT DATA(travels)
      FAILED failed.

    LOOP AT travels INTO DATA(travel).
      "Here a real implementation would e.g. trigger an e-mail in the save phase.
      "This demo only returns a success message and changes nothing.
      APPEND VALUE #( %tky = travel-%tky
                      %msg = NEW zcm_rap_###( textid      = zcm_rap_###=>reminder_sent
                                              severity    = if_abap_behv_message=>severity-success
                                              travel_id   = travel-TravelID
                                              customer_id = travel-CustomerID ) )
        TO reported-travel.
    ENDLOOP.

    result = VALUE #( FOR t IN travels ( %tky   = t-%tky
                                         %param = t ) ).

  ENDMETHOD.
```

해설
- ETag 충돌은 OData가 보내는 `If-Match` 값과 서버의 `LocalLastChangedAt`이 달라서 생깁니다. EML에서 직접 MODIFY할 때는 ETag 비교가 없습니다(ETag는 OData 같은 소비자가 보내는 값을 비교하는 장치). 그래서 EML로는 **잠금 충돌**을 관찰합니다.
- A가 중단점에 서 있는 동안은 RAP 트랜잭션이 끝나지 않았으므로 잠금이 유지됩니다(ABAP cheat sheet의 SET LOCKS 예제와 같은 원리). `SET LOCKS ENTITY ... FROM ...`으로 수정 없이 잠금만 걸 수도 있습니다.
- draft가 있는 활성 인스턴스를 B가 직접 수정하면, draft의 배타 잠금 때문에 거절됩니다. 이때 `%fail-cause`가 `locked`인지 다른 값(`conflict` 등)인지는 실제 시스템에서 확인해 보세요(실제 시스템에서 확인 필요).
- `lock : none`은 데이터를 바꾸지 않는 액션(알림, 계산 결과 반환 등)에 씁니다. 잠금을 걸지 않으므로 다른 사람이 편집 중이어도 실행됩니다. 이 액션 안에서 MODIFY를 하면 잠금 없이 데이터를 바꾸게 되므로 하지 마세요.
- `severity-success` 메시지는 Fiori에서 토스트(잠깐 뜨는 알림)로 보입니다.

클래스 구조 해설
- `sendReminder`의 시그니처(`IMPORTING keys FOR ACTION Travel~sendReminder RESULT result`)는 BDEF의 `action ... sendReminder result [1] $self;` 줄에서 생깁니다. `result`의 타입은 `TABLE FOR ACTION RESULT`이며 `%param`에 Travel 전체 구조가 들어갑니다.
- 인터랙션 단계에서 소비자가 액션을 호출할 때 framework가 (잠금 단계를 건너뛰고) 권한 → 기능 제어 확인 뒤 이 메서드를 부릅니다.

</details>

#### 4단계. 동적(인스턴스) 기능 제어 완성

Travel 상태에 따라 UI 버튼과 필드가 켜지고 꺼지게 합니다. R-02에서 이미 `update`/`delete`/액션/`Edit`/Booking 생성에 `features : instance`를 선언하고 `get_instance_features`를 만들었습니다. 이번 단계는 그 메서드에 **필드 제어**를 더하고, 규칙 하나(deductDiscount)를 바꾼 뒤 전체를 다시 정리하는 단계입니다. R-02 메서드를 아래 정답 코드로 **교체**하세요.

1. BDEF에서 필드 `BookingFee`를 인스턴스 기능 제어 대상으로 선언하세요. 다음 항목은 R-02에서 이미 선언되어 있는지 확인만 합니다: `update`, `delete`, 액션 `acceptTravel`, `rejectTravel`, `deductDiscount`, draft 액션 `Edit`, Booking 생성(create-by-association).
2. 규칙(상태 O=Open, A=Accepted, X=Rejected)

| 대상 | A(Accepted) | X(Rejected) | O(Open) |
|---|---|---|---|
| `BookingFee` | 읽기 전용 | 읽기 전용 | 입력 가능 |
| update / Edit | 불가 | 가능 | 가능 |
| delete | 불가 | 가능 | 가능 |
| acceptTravel | 불가 | 가능 | 가능 |
| rejectTravel | 가능 | 불가 | 가능 |
| deductDiscount | 불가 | 불가 (R-02에서는 가능 → 이번에 변경) | 가능 |
| Booking 생성 | 가능 | 불가 | 가능 |

3. 상태는 `IN LOCAL MODE`로 `OverallStatus`만 읽고(`FIELDS`), 결과는 `%tky` 기준으로 채웁니다. draft 인스턴스는 draft 값으로 판단되어야 합니다.

**확인**
- Accepted Travel의 Object Page에서 Edit·Delete·Accept 버튼이 비활성(회색)입니다.
- Rejected Travel을 Edit하면 Booking Fee가 읽기 전용이고, Booking 표의 Create 버튼이 비활성입니다.
- 10단계의 EML 클래스에서 Accepted Travel에 `acceptTravel`을 실행하면 `%fail-cause = if_abap_behv=>cause-disabled`가 나옵니다.

<details><summary>정답·해설</summary>

BDEF에서 관련된 줄(Travel 본문, ★ 줄만 새로 추가하고 나머지는 R-02에 이미 있습니다):

```bdef
  field ( features : instance ) BookingFee;                       // ★ 필드 단위 동적 제어

  update ( features : instance );                                  // update 가능 여부를 인스턴스마다 판단
  delete ( features : instance );                                  // delete 가능 여부를 인스턴스마다 판단

  association _Booking { create ( features : instance ); with draft; }   // Booking 생성 버튼 제어 (%assoc)

  action ( features : instance ) acceptTravel result [1] $self;
  action ( features : instance ) rejectTravel result [1] $self;
  action ( features : instance ) deductDiscount parameter ZRAP_A_DISCOUNT_### result [1] $self
    { default function GetDefaultsFordeductDiscount; }

  draft action ( features : instance ) Edit;
```

(6~7단계에서 이 줄들에 `authorization : update`, `precheck`가 더해집니다. 최종 형태는 10단계 BDEF 전체를 보세요.)

`lhc_travel` 정의부(R-02에 이미 있으므로 그대로 둡니다):

```abap
    METHODS get_instance_features FOR INSTANCE FEATURES
      IMPORTING keys REQUEST requested_features FOR Travel RESULT result.
```

구현:

```abap
  METHOD get_instance_features.

    "Only the status is needed; %tky contains %is_draft, so a draft
    "instance is evaluated with its draft values
    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        FIELDS ( OverallStatus )
        WITH CORRESPONDING #( keys )
      RESULT DATA(travels)
      FAILED failed.

    result = VALUE #(
      FOR travel IN travels
      LET is_accepted = xsdbool( travel-OverallStatus = travel_status-accepted )
          is_rejected = xsdbool( travel-OverallStatus = travel_status-rejected )
      IN
      ( %tky                   = travel-%tky

        "field: read-only once the travel is decided
        %field-BookingFee      = COND #( WHEN is_accepted = abap_true OR is_rejected = abap_true
                                         THEN if_abap_behv=>fc-f-read_only
                                         ELSE if_abap_behv=>fc-f-unrestricted )

        "standard operations
        %features-%update      = COND #( WHEN is_accepted = abap_true
                                         THEN if_abap_behv=>fc-o-disabled
                                         ELSE if_abap_behv=>fc-o-enabled )
        %features-%delete      = COND #( WHEN is_accepted = abap_true
                                         THEN if_abap_behv=>fc-o-disabled
                                         ELSE if_abap_behv=>fc-o-enabled )

        "draft action Edit follows update
        %action-Edit           = COND #( WHEN is_accepted = abap_true
                                         THEN if_abap_behv=>fc-o-disabled
                                         ELSE if_abap_behv=>fc-o-enabled )

        "actions
        %action-acceptTravel   = COND #( WHEN is_accepted = abap_true
                                         THEN if_abap_behv=>fc-o-disabled
                                         ELSE if_abap_behv=>fc-o-enabled )
        %action-rejectTravel   = COND #( WHEN is_rejected = abap_true
                                         THEN if_abap_behv=>fc-o-disabled
                                         ELSE if_abap_behv=>fc-o-enabled )
        %action-deductDiscount = COND #( WHEN is_accepted = abap_true OR is_rejected = abap_true
                                         THEN if_abap_behv=>fc-o-disabled
                                         ELSE if_abap_behv=>fc-o-enabled )

        "create-by-association of bookings
        %assoc-_Booking        = COND #( WHEN is_rejected = abap_true
                                         THEN if_abap_behv=>fc-o-disabled
                                         ELSE if_abap_behv=>fc-o-enabled ) ) ).

  ENDMETHOD.
```

(`travel_status`는 R-02에서 `lhc_travel`에 만든 상수 구조 `BEGIN OF travel_status, open, accepted, rejected`입니다.)

해설
- `%field-필드`에는 `fc-f-...` 상수(`read_only`, `unrestricted` 등)를, 연산·액션·연관에는 `fc-o-enabled/disabled`를 넣습니다. 필드를 동적으로 필수 입력으로 만드는 `fc-f-mandatory` 계열 상수도 있습니다(상수 이름은 실제 시스템에서 F2로 확인 필요).
- `%features-%update`처럼 `%features` 묶음으로 써도 되고, `%update`처럼 바로 써도 됩니다(RAP110은 앞의 형태, 참조 시나리오 carrier 예제는 뒤의 형태).
- 액션 구현(acceptTravel 등)은 `IN LOCAL MODE`로 MODIFY하므로 기능 제어를 무시합니다. 그래서 update를 막아도 액션은 상태를 바꿀 수 있습니다.
- `FAILED failed`를 그대로 넘기면, 읽지 못한(존재하지 않는) 키가 `failed`에 `not_found`로 들어갑니다.
- 정적 기능 제어(`field ( readonly )`)는 늘 같은 제약, `features : instance`는 데이터에 따라 바뀌는 제약입니다.

클래스 구조 해설
- 시그니처의 `REQUEST requested_features`는 소비자가 어떤 항목의 상태를 물었는지 표시합니다. 이 구현은 모든 항목을 항상 채웁니다(값이 작아 그렇게 해도 됩니다).
- `result`의 컴포넌트(`%field-BookingFee`, `%action-acceptTravel`, `%assoc-_Booking`…)는 BDEF에서 `features : instance`를 붙인 항목에서만 생깁니다. BDEF에 없는 항목을 쓰면 구문 오류가 납니다.
- Fiori가 Object Page를 그릴 때, 그리고 EML 소비자가 MODIFY를 보낼 때(IN LOCAL MODE 제외) framework가 이 메서드를 부릅니다.

자주 나는 오류
- `%action-Edit`에 오류가 나면 BDEF의 `draft action ( features : instance ) Edit;`가 빠진 것입니다.

</details>

#### 5단계. 전역 기능 제어: 마감일에는 Travel 생성 금지

인스턴스와 상관없이, 시스템 상황(날짜·스위치)만 보고 생성 기능을 끕니다.

1. BDEF에서 `create`와 static factory 액션 `createTravel`에 전역 기능 제어를 선언하세요.
2. `lhc_travel`에 `get_global_features`를 구현하세요.
   - 도우미 메서드 `is_create_closed`가 `abap_true`를 돌려주면 `%create`, `%action-createTravel`을 disabled로 합니다.
   - `is_create_closed`: `ZRAP_CTRL_###`의 `create_closed = 'X'`이면 마감. `sunday_closed = 'X'`이고 오늘이 일요일이면 마감. 오늘 날짜는 릴리스된 API `cl_abap_context_info=>get_system_date( )`로 얻고, 요일은 1900-01-01(월요일)부터 지난 일수를 7로 나눈 나머지로 계산합니다(나머지 6 = 일요일).
3. 스위치 클래스로 `c_create_closed = abap_true`를 넣고 실행한 뒤 앱을 새로 고치세요. 확인이 끝나면 다시 `abap_false`로 돌려 놓으세요.

**확인**
- 목록 화면의 Create 버튼과 `createTravel` 버튼이 비활성이 됩니다.
- EML로 `CREATE`를 보내면 `failed-travel`에 `cause-disabled`가 들어갑니다(10단계 클래스에서 확인).
- 스위치를 끄면 버튼이 다시 활성화됩니다.

<details><summary>정답·해설</summary>

BDEF(Travel 본문):

```bdef
  create ( features : global ) { default function GetDefaultsForCreate; }            // 생성 가능 여부를 전역으로 판단 (기본값 함수는 R-02)
  static default factory action ( features : global ) createTravel
    parameter ZRAP_A_CREATE_TRAVEL_### [1];                                            // static 액션도 전역 제어
```

`lhc_travel` 정의부:

```abap
    CONSTANTS c_ctrl_id TYPE c LENGTH 10 VALUE 'TRAVEL'.

    METHODS get_global_features FOR GLOBAL FEATURES
      IMPORTING REQUEST requested_features FOR Travel RESULT result.

    METHODS is_create_closed
      RETURNING VALUE(closed) TYPE abap_bool.
```

구현:

```abap
  METHOD get_global_features.

    DATA(closed) = is_create_closed( ).

    IF requested_features-%create = if_abap_behv=>mk-on.
      result-%create = COND #( WHEN closed = abap_true
                               THEN if_abap_behv=>fc-o-disabled
                               ELSE if_abap_behv=>fc-o-enabled ).
    ENDIF.

    IF requested_features-%action-createTravel = if_abap_behv=>mk-on.
      result-%action-createTravel = COND #( WHEN closed = abap_true
                                            THEN if_abap_behv=>fc-o-disabled
                                            ELSE if_abap_behv=>fc-o-enabled ).
    ENDIF.

  ENDMETHOD.


  METHOD is_create_closed.

    closed = abap_false.

    SELECT SINGLE FROM zrap_ctrl_###
      FIELDS create_closed, sunday_closed
      WHERE ctrl_id = @c_ctrl_id
      INTO @DATA(ctrl).
    IF sy-subrc <> 0.
      RETURN.                          "no switch row -> never closed
    ENDIF.

    IF ctrl-create_closed = abap_true.
      closed = abap_true.
      RETURN.
    ENDIF.

    IF ctrl-sunday_closed = abap_true.
      "1900-01-01 was a Monday: remainder 0 = Monday ... 6 = Sunday
      DATA(today)       = cl_abap_context_info=>get_system_date( ).
      DATA(monday_1900) = CONV d( '19000101' ).
      closed = xsdbool( ( today - monday_1900 ) MOD 7 = 6 ).
    ENDIF.

  ENDMETHOD.
```

해설
- 전역 기능 제어는 **키가 없습니다**. 그래서 `keys`가 없고 `result`도 표가 아니라 구조입니다. "지금 이 시스템에서 이 기능이 열려 있는가"만 답합니다.
- `create`에는 `features : instance`를 쓸 수 없습니다(아직 인스턴스가 없으므로). 생성 제한은 전역 기능 제어, 전역 권한, precheck로 합니다.
- `cl_abap_context_info`는 ABAP Cloud에서 쓸 수 있는 릴리스된 클래스입니다. 실제 업무라면 공장 달력(factory calendar) API를 쓰겠지만, 트라이얼에서 쓸 수 있는 릴리스 달력 API는 확인하지 못해 요일 계산으로 대신했습니다.
- `static default factory action ( features : global ) createTravel ...`에서 괄호의 위치는 액션 키워드 바로 뒤입니다. 이 조합이 활성화되지 않으면 `( features : global )`을 빼고 `%create`만 제어하세요(실제 시스템에서 확인 필요).
- 같은 테이블을 매 호출마다 SELECT SINGLE 하지만, 호출당 한 번이므로 루프 안 SELECT가 아닙니다.

클래스 구조 해설
- `FOR GLOBAL FEATURES` 시그니처는 BDEF에 `features : global`이 하나라도 있을 때 생깁니다. `requested_features`/`result`에는 `features : global`을 붙인 연산·액션만 컴포넌트로 들어 있습니다.
- Fiori가 목록 화면을 열 때, EML 소비자가 CREATE/`createTravel`을 보낼 때 framework가 호출합니다.

</details>

#### 6단계. 권한 제어: 전역 + 인스턴스 권한, 권한 위임

1. Travel의 권한 마스터를 전역과 인스턴스 둘 다로 바꾸세요. Booking은 이미 `authorization dependent by _Travel`입니다(R-02).
2. 다음 연산은 별도 권한 검사 대신 **update 권한에 위임**하세요: `acceptTravel`, `rejectTravel`, `deductDiscount`, `addServiceFee`, `sendReminder`, determine action `checkDates`, Booking 생성(create-by-association).
3. `copyTravel`(인스턴스 factory 액션)은 위임하지 말고, 인스턴스 권한 결과에 `%action-copyTravel`을 직접 채우세요. 규칙: 원본 Travel 대행사 국가에 대한 **생성** 권한이 있어야 복사할 수 있습니다.
4. `get_global_authorizations`: `%create`, `%update`(와 `%action-Edit`), `%delete`, `%action-createTravel`을 판단하고, 거부할 때는 메시지 031(`not_authorized`)을 `%global = mk-on`으로 `reported`에 넣습니다.
5. `get_instance_authorizations`:
   - Travel의 `AgencyID`만 읽고(IN LOCAL MODE), 활성 테이블 `ZRAP_ATRAV_###`와 `/DMO/I_Agency`를 조인해 **저장된 인스턴스의 대행사 국가**를 한 번의 SELECT(FOR ALL ENTRIES)로 가져옵니다.
   - 활성 인스턴스가 있으면 그 국가로 update/delete/copy 권한을 검사, 없으면(아직 저장 안 된 새 draft) 국가 없이 create 권한으로 판단합니다.
   - 거부 시 메시지 032(`not_authorized_country`, 대행사·국가 표시, `%element-AgencyID`)를 넣습니다.
6. 도우미 메서드 `is_create_granted`, `is_update_granted`, `is_delete_granted`(선택 파라미터 `country_code TYPE land1`)는 `AUTHORITY-CHECK OBJECT '/DMO/TRVL'`을 `ACTVT` 01/02/06으로 수행합니다. 국가가 없으면 `/DMO/CNTRY`는 `DUMMY`로 검사합니다.
7. 트라이얼 시뮬레이션: `simulate_authorization` 메서드를 만들어, 상수 `c_use_real_auth = abap_false`인 동안은 AUTHORITY-CHECK 결과 대신 **스위치 테이블의 `deny_country`와 같은 국가만 거부**하게 하세요. privileged 모드(10단계)에서는 거부하지 않습니다.

**확인**
- 스위치 클래스로 `c_deny_country`를 1단계에서 본 국가 중 하나(예: 출력에 나온 첫 국가)로 설정하고 실행하세요.
- 앱에서 그 국가 대행사의 활성 Travel을 열면 Edit·Delete·Accept·Reject·Deduct Discount·Send Reminder 버튼이 비활성이고, 다른 국가 Travel은 그대로입니다.
- 스위치를 다시 비우면(`''`) 원래대로 돌아옵니다.

<details><summary>정답·해설</summary>

BDEF에서 바뀌는 줄(Travel). 머리의 한 줄:

```bdef
authorization master ( global, instance )              // 전역 + 인스턴스 권한 검사 메서드가 둘 다 필요
```

본문에서 바뀌는 줄(각 줄을 같은 이름의 기존 줄과 바꾸고, `sendReminder`는 3단계 줄을 이 줄로 둡니다):

```bdef
  association _Booking { create ( features : instance, authorization : update ); with draft; }  // Booking 생성 = Travel update 권한

  action ( features : instance, authorization : update ) acceptTravel result [1] $self;
  action ( features : instance, authorization : update ) rejectTravel result [1] $self;
  action ( features : instance, authorization : update ) deductDiscount parameter ZRAP_A_DISCOUNT_### result [1] $self
    { default function GetDefaultsFordeductDiscount; }
  repeatable action ( authorization : update ) addServiceFee result [1] $self;
  action ( lock : none, authorization : update ) sendReminder result [1] $self;
  factory action copyTravel [1];                         // 위임 없음 -> 인스턴스 권한 결과에 %action-copyTravel
  determine action ( authorization : update ) checkDates { validation validateDates; }
```

`lhc_travel` 정의부에 추가:

```abap
    "simulation switch: abap_true = use the real AUTHORITY-CHECK result
    CONSTANTS c_use_real_auth TYPE abap_bool VALUE abap_false.

    METHODS get_global_authorizations FOR GLOBAL AUTHORIZATION
      IMPORTING REQUEST requested_authorizations FOR Travel RESULT result.

    METHODS get_instance_authorizations FOR INSTANCE AUTHORIZATION
      IMPORTING keys REQUEST requested_authorizations FOR Travel RESULT result.

    METHODS is_create_granted
      IMPORTING country_code   TYPE land1 OPTIONAL
      RETURNING VALUE(granted) TYPE abap_bool.

    METHODS is_update_granted
      IMPORTING country_code   TYPE land1 OPTIONAL
      RETURNING VALUE(granted) TYPE abap_bool.

    METHODS is_delete_granted
      IMPORTING country_code   TYPE land1 OPTIONAL
      RETURNING VALUE(granted) TYPE abap_bool.

    METHODS simulate_authorization
      IMPORTING check_result   TYPE abap_bool
                country_code   TYPE land1
      RETURNING VALUE(granted) TYPE abap_bool.
```

(R-02에 `get_global_authorizations`가 이미 있으면 그 선언은 그대로 두고 구현만 교체합니다.)

구현:

```abap
  METHOD get_global_authorizations.

    "create and the static factory action createTravel need create authorization
    IF requested_authorizations-%create = if_abap_behv=>mk-on
    OR requested_authorizations-%action-createTravel = if_abap_behv=>mk-on.
      DATA(create_granted) = is_create_granted( ).
      result-%create              = COND #( WHEN create_granted = abap_true
                                            THEN if_abap_behv=>auth-allowed
                                            ELSE if_abap_behv=>auth-unauthorized ).
      result-%action-createTravel = result-%create.
      IF create_granted = abap_false.
        APPEND VALUE #( %msg    = NEW zcm_rap_###( textid   = zcm_rap_###=>not_authorized
                                                   severity = if_abap_behv_message=>severity-error )
                        %global = if_abap_behv=>mk-on ) TO reported-travel.
      ENDIF.
    ENDIF.

    "Edit is treated like update
    IF requested_authorizations-%update      = if_abap_behv=>mk-on
    OR requested_authorizations-%action-Edit = if_abap_behv=>mk-on.
      IF is_update_granted( ) = abap_true.
        result-%update      = if_abap_behv=>auth-allowed.
        result-%action-Edit = if_abap_behv=>auth-allowed.
      ELSE.
        result-%update      = if_abap_behv=>auth-unauthorized.
        result-%action-Edit = if_abap_behv=>auth-unauthorized.
        APPEND VALUE #( %msg    = NEW zcm_rap_###( textid   = zcm_rap_###=>not_authorized
                                                   severity = if_abap_behv_message=>severity-error )
                        %global = if_abap_behv=>mk-on ) TO reported-travel.
      ENDIF.
    ENDIF.

    IF requested_authorizations-%delete = if_abap_behv=>mk-on.
      IF is_delete_granted( ) = abap_true.
        result-%delete = if_abap_behv=>auth-allowed.
      ELSE.
        result-%delete = if_abap_behv=>auth-unauthorized.
        APPEND VALUE #( %msg    = NEW zcm_rap_###( textid   = zcm_rap_###=>not_authorized
                                                   severity = if_abap_behv_message=>severity-error )
                        %global = if_abap_behv=>mk-on ) TO reported-travel.
      ENDIF.
    ENDIF.

  ENDMETHOD.


  METHOD get_instance_authorizations.

    DATA update_granted TYPE abap_bool.
    DATA delete_granted TYPE abap_bool.
    DATA copy_granted   TYPE abap_bool.

    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        FIELDS ( AgencyID )
        WITH CORRESPONDING #( keys )
      RESULT DATA(travels)
      FAILED failed.

    CHECK travels IS NOT INITIAL.

    "Authorization is checked against the SAVED (active) instance:
    "one SELECT for all keys, no SELECT inside the loop
    SELECT FROM zrap_atrav_### AS travel
      INNER JOIN /dmo/i_agency AS agency ON travel~agency_id = agency~AgencyID
      FIELDS travel~travel_id, agency~AgencyID, agency~CountryCode
      FOR ALL ENTRIES IN @travels
      WHERE travel~travel_id = @travels-TravelID
      INTO TABLE @DATA(active_agencies).
    SORT active_agencies BY travel_id.

    DATA(update_requested) = xsdbool( requested_authorizations-%update      = if_abap_behv=>mk-on
                                   OR requested_authorizations-%action-Edit = if_abap_behv=>mk-on ).
    DATA(delete_requested) = xsdbool( requested_authorizations-%delete = if_abap_behv=>mk-on ).
    DATA(copy_requested)   = xsdbool( requested_authorizations-%action-copyTravel = if_abap_behv=>mk-on ).

    LOOP AT travels INTO DATA(travel).

      update_granted = abap_true.
      delete_granted = abap_true.
      copy_granted   = abap_true.

      READ TABLE active_agencies WITH KEY travel_id = travel-TravelID
           BINARY SEARCH INTO DATA(active).

      IF sy-subrc = 0 AND travel-TravelID IS NOT INITIAL.
        "instance exists on the database -> check with the agency country
        IF update_requested = abap_true.
          update_granted = is_update_granted( active-countrycode ).
        ENDIF.
        IF delete_requested = abap_true.
          delete_granted = is_delete_granted( active-countrycode ).
        ENDIF.
        IF copy_requested = abap_true.
          copy_granted = is_create_granted( active-countrycode ).
        ENDIF.

        IF update_granted = abap_false OR delete_granted = abap_false OR copy_granted = abap_false.
          APPEND VALUE #( %tky              = travel-%tky
                          %msg              = NEW zcm_rap_###( textid       = zcm_rap_###=>not_authorized_country
                                                               severity     = if_abap_behv_message=>severity-error
                                                               agency_id    = active-agencyid
                                                               country_code = active-countrycode )
                          %element-AgencyID = if_abap_behv=>mk-on ) TO reported-travel.
        ENDIF.

      ELSE.
        "new draft (late numbering: TravelID still initial) -> create authorization decides
        update_granted = is_create_granted( ).
        delete_granted = update_granted.
        copy_granted   = update_granted.
        IF update_granted = abap_false.
          APPEND VALUE #( %tky = travel-%tky
                          %msg = NEW zcm_rap_###( textid   = zcm_rap_###=>not_authorized
                                                  severity = if_abap_behv_message=>severity-error ) )
            TO reported-travel.
        ENDIF.
      ENDIF.

      APPEND VALUE #( LET upd_auth  = COND #( WHEN update_granted = abap_true
                                              THEN if_abap_behv=>auth-allowed
                                              ELSE if_abap_behv=>auth-unauthorized )
                          del_auth  = COND #( WHEN delete_granted = abap_true
                                              THEN if_abap_behv=>auth-allowed
                                              ELSE if_abap_behv=>auth-unauthorized )
                          copy_auth = COND #( WHEN copy_granted = abap_true
                                              THEN if_abap_behv=>auth-allowed
                                              ELSE if_abap_behv=>auth-unauthorized )
                      IN
                      %tky               = travel-%tky
                      %update            = upd_auth
                      %action-Edit       = upd_auth
                      %delete            = del_auth
                      %action-copyTravel = copy_auth ) TO result.
    ENDLOOP.

  ENDMETHOD.


  METHOD is_create_granted.
    IF country_code IS SUPPLIED.
      AUTHORITY-CHECK OBJECT '/DMO/TRVL'
        ID '/DMO/CNTRY' FIELD country_code
        ID 'ACTVT'      FIELD '01'.
    ELSE.
      AUTHORITY-CHECK OBJECT '/DMO/TRVL'
        ID '/DMO/CNTRY' DUMMY
        ID 'ACTVT'      FIELD '01'.
    ENDIF.
    granted = simulate_authorization( check_result = xsdbool( sy-subrc = 0 )
                                      country_code = country_code ).
  ENDMETHOD.


  METHOD is_update_granted.
    IF country_code IS SUPPLIED.
      AUTHORITY-CHECK OBJECT '/DMO/TRVL'
        ID '/DMO/CNTRY' FIELD country_code
        ID 'ACTVT'      FIELD '02'.
    ELSE.
      AUTHORITY-CHECK OBJECT '/DMO/TRVL'
        ID '/DMO/CNTRY' DUMMY
        ID 'ACTVT'      FIELD '02'.
    ENDIF.
    granted = simulate_authorization( check_result = xsdbool( sy-subrc = 0 )
                                      country_code = country_code ).
  ENDMETHOD.


  METHOD is_delete_granted.
    IF country_code IS SUPPLIED.
      AUTHORITY-CHECK OBJECT '/DMO/TRVL'
        ID '/DMO/CNTRY' FIELD country_code
        ID 'ACTVT'      FIELD '06'.
    ELSE.
      AUTHORITY-CHECK OBJECT '/DMO/TRVL'
        ID '/DMO/CNTRY' DUMMY
        ID 'ACTVT'      FIELD '06'.
    ENDIF.
    granted = simulate_authorization( check_result = xsdbool( sy-subrc = 0 )
                                      country_code = country_code ).
  ENDMETHOD.


  METHOD simulate_authorization.
    "!!! Training only - remove in productive code !!!
    IF c_use_real_auth = abap_true.
      granted = check_result.
      RETURN.
    ENDIF.

    granted = abap_true.
    IF country_code IS INITIAL.
      RETURN.                           "global check: always allowed in the simulation
    ENDIF.

    "In privileged mode the real AUTHORITY-CHECK on /DMO/TRVL is skipped
    "(authorization context NoCheckWhenPrivileged) - the simulation does the same
    cl_abap_behv_aux=>get_current_context( IMPORTING privileged = DATA(privileged) ).
    IF privileged = abap_true.
      RETURN.
    ENDIF.

    SELECT SINGLE FROM zrap_ctrl_###
      FIELDS deny_country
      WHERE ctrl_id = @c_ctrl_id
      INTO @DATA(deny_country).
    IF sy-subrc = 0 AND deny_country IS NOT INITIAL AND deny_country = country_code.
      granted = abap_false.
    ENDIF.
  ENDMETHOD.
```

해설
- **전역 권한**은 인스턴스와 무관하게 "이 사용자가 이 BO를 만들/바꿀/지울 수 있나"를 봅니다. create는 인스턴스가 없으므로 전역 권한으로만 검사합니다. **인스턴스 권한**은 데이터(대행사 국가)에 따라 판단합니다.
- 권한은 **저장된 상태(활성 테이블)** 기준으로 판단합니다. 그렇지 않으면 사용자가 draft에서 대행사를 허용된 국가로 바꿔 권한을 피해 갈 수 있습니다. 바뀐 값 자체는 7단계 precheck가 막습니다. 이 설계는 참조 시나리오 `/DMO/BP_TRAVEL_D`와 같습니다.
- late numbering이라 새 draft의 `TravelID`는 아직 비어 있습니다. 그래서 `TravelID IS NOT INITIAL` 조건을 같이 봅니다.
- `authorization : update`로 위임된 연산은 결과 구조에 따로 나오지 않고 `%update` 결과를 따릅니다. `authorization dependent by _Travel`인 Booking도 Travel의 결과를 따릅니다.
- `AUTHORITY-CHECK`의 객체 이름은 ABAP Cloud에서 반드시 리터럴이어야 합니다. `DUMMY`는 그 필드를 검사하지 않는다는 뜻입니다. `sy-subrc = 0`이면 허용입니다.
- **트라이얼의 한계**: `/DMO/TRVL` 권한을 사용자에게 주려면 IAM 앱 → 비즈니스 카탈로그 → 비즈니스 역할 → 사용자 할당이 필요합니다. 트라이얼 계정에서는 보통 이런 관리 앱(비즈니스 역할 관리)을 쓸 수 없어 직접 확인이 어렵습니다(실제 시스템에서 확인 필요). 그래서 `simulate_authorization`이 실제 결과를 덮어씁니다. 참조 시나리오도 `"Simulation for full authorization"` 주석과 함께 결과를 `abap_true`로 덮어쓰는 같은 방식을 씁니다.
- 테스트 클래스(R-12)에서는 `lhc_travel`에 `FRIENDS ltc_travel`을 주고 `simulate_authorization` 대신 스위치 테이블 값을 바꾸거나, privileged 모드를 이용해 거부/허용을 모두 검사할 수 있습니다.
- `cl_abap_behv_aux=>get_current_context`는 ABAP cheat sheet에 나온 RAP 보조 클래스입니다. `IMPORTING`의 다른 파라미터를 생략해도 되는지는 실제 시스템에서 확인하세요(실제 시스템에서 확인 필요).
- `%action-createTravel`을 전역 권한 결과에 넣었습니다. static 액션은 인스턴스가 없으므로 전역 권한 대상입니다. 활성화 시 이 컴포넌트가 없다는 오류가 나면 그 줄을 지우세요(실제 시스템에서 확인 필요).
- `repeatable action ( authorization : update ) addServiceFee`에서 `repeatable`과 괄호의 순서가 문법에 맞지 않으면 ADT의 코드 완성(Ctrl+Space)이 제안하는 순서를 따르세요(실제 시스템에서 확인 필요).

클래스 구조 해설
- `FOR GLOBAL AUTHORIZATION` 메서드는 `authorization master ( global ... )`에서, `FOR INSTANCE AUTHORIZATION` 메서드는 `( ... instance )`에서 생깁니다. `requested_authorizations`/`result`의 `%action-...` 컴포넌트는 위임하지 않은(`authorization : update`가 없는) 액션만 가집니다.
- framework는 소비자 요청마다 먼저 전역 권한, 그다음 인스턴스 권한을 부르고, 거부되면 `failed`에 `cause-unauthorized`를 넣고 핸들러를 부르지 않습니다. `IN LOCAL MODE` 호출은 권한 검사를 하지 않습니다.

</details>

#### 7단계. precheck: 버퍼에 들어가기 전에 막기

권한은 "저장된 데이터" 기준이므로, 사용자가 **새로 입력하는** 대행사가 권한 없는 국가인 경우는 막지 못합니다. 이것을 precheck로 막습니다.

1. BDEF의 `create`, `update`에 `precheck`를 추가하세요.
2. `precheck_create`, `precheck_update`는 공통 메서드 `precheck_auth`를 부릅니다.
   - `%control-AgencyID`가 켜진(=대행사를 입력/변경한) 요청만 검사합니다.
   - 입력된 대행사 ID들을 중복 없이 모아 `/DMO/I_Agency`에서 국가를 한 번에 읽습니다.
   - create면 `is_create_granted( 국가 )`, update면 `is_update_granted( 국가 )`가 거짓일 때 `failed`(`%fail-cause = cause-unauthorized`)와 메시지 032를 넣습니다. create는 `%cid`, update는 `%tky`로 인스턴스를 가리킵니다.
   - 존재하지 않는 대행사는 precheck에서 건드리지 않고 R-02의 `validateAgency`에 맡깁니다.
3. (도전) R-02의 `Resume` 추가 구현에서, 다시 이어서 편집하는 draft의 대행사도 `precheck_auth`로 검사하세요.

**확인**
- 스위치의 `deny_country`를 설정한 뒤 새 Travel(draft)을 만들고 그 국가의 대행사를 입력하면, 입력하자마자(필드를 벗어나는 순간) 메시지 032가 대행사 필드에 붙고 값이 반영되지 않습니다.
- 다른 국가 대행사는 정상 입력됩니다.

<details><summary>정답·해설</summary>

BDEF(Travel):

```bdef
  create ( features : global, precheck ) { default function GetDefaultsForCreate; }  // 버퍼 반영 전 검사
  update ( features : instance, precheck );                                          // 버퍼 반영 전 검사
```

`lhc_travel` 정의부에 추가:

```abap
    TYPES t_entities_create TYPE TABLE FOR CREATE zrap_r_travel_###\\Travel.
    TYPES t_entities_update TYPE TABLE FOR UPDATE zrap_r_travel_###\\Travel.
    TYPES t_failed_travel   TYPE TABLE FOR FAILED EARLY zrap_r_travel_###\\Travel.
    TYPES t_reported_travel TYPE TABLE FOR REPORTED EARLY zrap_r_travel_###\\Travel.

    METHODS precheck_create FOR PRECHECK
      IMPORTING entities FOR CREATE Travel.

    METHODS precheck_update FOR PRECHECK
      IMPORTING entities FOR UPDATE Travel.

    METHODS precheck_auth
      IMPORTING entities_create TYPE t_entities_create OPTIONAL
                entities_update TYPE t_entities_update OPTIONAL
      CHANGING  failed          TYPE t_failed_travel
                reported        TYPE t_reported_travel.
```

구현:

```abap
  METHOD precheck_create.
    precheck_auth( EXPORTING entities_create = entities
                   CHANGING  failed          = failed-travel
                             reported        = reported-travel ).
  ENDMETHOD.


  METHOD precheck_update.
    precheck_auth( EXPORTING entities_update = entities
                   CHANGING  failed          = failed-travel
                             reported        = reported-travel ).
  ENDMETHOD.


  METHOD precheck_auth.

    DATA entities  TYPE t_entities_update.
    DATA operation TYPE if_abap_behv=>t_char01.
    DATA agencies  TYPE SORTED TABLE OF /dmo/i_agency WITH UNIQUE KEY AgencyID.

    "exactly one of the two tables is filled
    ASSERT NOT ( entities_create IS INITIAL EQUIV entities_update IS INITIAL ).

    IF entities_create IS NOT INITIAL.
      "same row structure for both cases: keep the %cid in %cid_ref
      entities  = CORRESPONDING #( entities_create MAPPING %cid_ref = %cid ).
      operation = if_abap_behv=>op-m-create.
    ELSE.
      entities  = entities_update.
      operation = if_abap_behv=>op-m-update.
    ENDIF.

    "only requests that set/change the agency are relevant
    DELETE entities WHERE %control-AgencyID = if_abap_behv=>mk-off.

    agencies = CORRESPONDING #( entities DISCARDING DUPLICATES MAPPING AgencyID = AgencyID EXCEPT * ).
    CHECK agencies IS NOT INITIAL.

    SELECT FROM /dmo/i_agency
      FIELDS AgencyID, CountryCode
      FOR ALL ENTRIES IN @agencies
      WHERE AgencyID = @agencies-AgencyID
      INTO TABLE @DATA(agency_countries).
    SORT agency_countries BY AgencyID.

    LOOP AT entities INTO DATA(entity).

      READ TABLE agency_countries WITH KEY AgencyID = entity-AgencyID
           BINARY SEARCH INTO DATA(agency_country).
      IF sy-subrc <> 0.
        CONTINUE.                       "unknown agency -> validateAgency reports it
      ENDIF.

      DATA(is_granted) = COND abap_bool(
        WHEN operation = if_abap_behv=>op-m-create THEN is_create_granted( agency_country-countrycode )
        ELSE is_update_granted( agency_country-countrycode ) ).

      IF is_granted = abap_false.
        APPEND VALUE #( %cid       = COND #( WHEN operation = if_abap_behv=>op-m-create THEN entity-%cid_ref )
                        %tky       = entity-%tky
                        %fail-cause = if_abap_behv=>cause-unauthorized ) TO failed.

        APPEND VALUE #( %cid              = COND #( WHEN operation = if_abap_behv=>op-m-create THEN entity-%cid_ref )
                        %tky              = entity-%tky
                        %msg              = NEW zcm_rap_###( textid       = zcm_rap_###=>not_authorized_country
                                                             severity     = if_abap_behv_message=>severity-error
                                                             agency_id    = entity-AgencyID
                                                             country_code = agency_country-countrycode )
                        %element-AgencyID = if_abap_behv=>mk-on ) TO reported.
      ENDIF.
    ENDLOOP.

  ENDMETHOD.
```

(도전) R-02의 `resume` 메서드 끝에 추가:

```abap
    "Resume: check the agency of the draft that is continued
    READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
      ENTITY Travel
        FIELDS ( AgencyID )
        WITH VALUE #( FOR key IN keys ( %key      = key-%key
                                        %is_draft = if_abap_behv=>mk-on ) )
      RESULT DATA(resumed_travels).

    "CHANGING CONTROL sets %control-AgencyID for filled fields
    DATA(entities_for_check) = CORRESPONDING t_entities_update( resumed_travels CHANGING CONTROL ).
    IF entities_for_check IS NOT INITIAL.
      precheck_auth( EXPORTING entities_update = entities_for_check
                     CHANGING  failed          = failed-travel
                               reported        = reported-travel ).
    ENDIF.
```

해설
- precheck는 요청이 **트랜잭션 버퍼에 들어가기 전에** 불립니다. 여기서 실패하면 버퍼가 바뀌지 않습니다. 반면 validation은 저장할 때(early save) 버퍼 전체를 검사합니다. "입력 자체를 막을 것인가(precheck)", "저장할 때 모아서 알려 줄 것인가(validation)"로 나눠 쓰세요.
- precheck의 `entities`에는 **요청에 들어온 값만** 있습니다. `%control`로 어떤 필드가 들어왔는지 판단합니다. 버퍼의 현재 값이 필요하면 `READ ENTITIES ... IN LOCAL MODE`로 읽어야 합니다.
- create와 update 행 구조를 하나로 다루기 위해 `CORRESPONDING ... MAPPING %cid_ref = %cid`를 씁니다(참조 시나리오와 같은 기법). draft에서 Fiori의 필드 입력은 draft 인스턴스에 대한 UPDATE로 오므로 precheck_update가 바로 반응합니다.
- R-02에서 `AgencyID`가 `mandatory : create, readonly : update`이므로 활성 인스턴스의 대행사는 바꿀 수 없습니다. 하지만 새 draft에서는 입력할 수 있으므로 update precheck가 여전히 필요합니다.
- precheck에는 `IN LOCAL MODE` 요청이 오지 않습니다(local mode는 precheck를 건너뜁니다).

클래스 구조 해설
- `FOR PRECHECK ... FOR CREATE Travel` / `FOR UPDATE Travel` 시그니처는 `create ( precheck )`, `update ( precheck )`에서 생깁니다. `failed`, `reported`는 `EARLY` 응답 타입이며 `mapped`는 없습니다.
- 호출 순서(인터랙션 단계): 권한 → 기능 제어 → precheck → 버퍼 반영(managed) → on modify determination.

</details>

#### 8단계. CDS 접근 제어(DCL)와 draft 쿼리 뷰

BO 권한(6단계)은 "수정"을 막고, **읽기**는 CDS 접근 제어가 막습니다.

1. R/C 뷰(Travel, Booking)의 접근 제어 검사를 "DCL이 없으면 경고" 수준으로 두세요(2단계 R 뷰에서 이미 설정).
2. R 뷰는 R-01에서 `#NOT_REQUIRED`였으므로 2단계에서 `#CHECK`로 바꿨는지 확인하고, Booking R 뷰와 두 C 뷰도 `#CHECK`로 바꾸세요. 그다음 접근 제어 `ZRAP_R_TRAVEL_###`를 만드세요(ADT: 뷰에서 우클릭 → New Access Control). 기본은 모든 행 허용입니다. 아래 두 실험용 조건을 주석으로 함께 적어 두세요.
   - 실험 A(리터럴 조건): 거절된 Travel(`OverallStatus = 'X'`)을 숨김
   - 실험 B(PFCG 조건): `/DMO/TRVL` 권한의 `/DMO/CNTRY` 값과 대행사 국가(`_Agency.CountryCode`)를 비교, 활동 `03`
3. 접근 제어 `ZRAP_C_TRAVEL_###`는 R 뷰의 조건을 **상속**하게 만드세요(템플릿 "Define Role with inherited Conditions").
4. Booking도 `ZRAP_R_BOOKING_###`(모두 허용), `ZRAP_C_BOOKING_###`(상속)을 만드세요.
5. Travel draft 테이블을 읽는 **draft 쿼리 뷰** `ZRAP_R_TRAVELDRAFT_###`를 만들고(draft 테이블의 모든 필드 + draft 관리 필드), 접근 제어 `ZRAP_R_TRAVELDRAFT_###`는 `ZRAP_R_TRAVEL_###`의 조건을 상속하게 하세요. BDEF의 `draft table` 줄에 이 뷰를 연결합니다.
6. 실험 A를 켜고 앱과 Data Preview를 확인한 뒤, 다시 `true`로 되돌리세요. 실험 B는 켜 보기만 하고(데이터가 모두 사라질 수 있음) 되돌리세요.

**직접 추가할 어노테이션**
- `@AccessControl.authorizationCheck` — 이 뷰를 SQL로 읽을 때 DCL 검사를 할지(#CHECK, #MANDATORY, #NOT_REQUIRED, #NOT_ALLOWED)
- `@MappingRole` — DCL 역할을 모든 사용자에게 자동 적용
- `@EndUserText.label` — DCL/뷰 설명
- `@Metadata.ignorePropagatedAnnotations` — draft 쿼리 뷰가 아래 테이블 어노테이션을 물려받지 않게 함
- `@Semantics.amount.currencyCode` — draft 쿼리 뷰의 금액 필드 통화 연결

**확인**
- 실험 A를 켜면 앱 목록과 `ZRAP_C_TRAVEL_###` Data Preview에서 Rejected Travel이 사라지고, 끄면 다시 나타납니다(C 뷰는 상속이므로 C 쪽을 고칠 필요가 없음).
- 실험 B를 켜면(트라이얼 사용자에게 `/DMO/TRVL` 권한이 없으므로) 목록이 비는 것이 정상입니다.
- 모든 DCL과 draft 쿼리 뷰, BDEF가 활성화됩니다.

<details><summary>정답·해설</summary>

```cds
@EndUserText.label: 'Access control for ZRAP_R_TRAVEL_###'   // DCL 설명 (→ 어노테이션 탭: @EndUserText.label)
@MappingRole: true                                           // 모든 사용자에게 적용되는 역할 (→ 어노테이션 탭: @MappingRole)
define role ZRAP_R_TRAVEL_### {
  grant
    select
      on
        ZRAP_R_TRAVEL_###
          where
            true;
//  Experiment A - literal condition (hide rejected travels):
//          OverallStatus <> 'X';
//  Experiment B - PFCG condition (agency country vs. /DMO/TRVL, activity 03 = display):
//          ( _Agency.CountryCode ) = aspect pfcg_auth( '/DMO/TRVL', '/DMO/CNTRY', ACTVT = '03' );
}
```

```cds
@EndUserText.label: 'Access control for ZRAP_C_TRAVEL_###'
@MappingRole: true
define role ZRAP_C_TRAVEL_### {
  grant
    select
      on
        ZRAP_C_TRAVEL_###
          where
            inheriting conditions from entity ZRAP_R_TRAVEL_###;   // R 뷰의 조건을 그대로 상속
}
```

```cds
@EndUserText.label: 'Access control for ZRAP_R_BOOKING_###'
@MappingRole: true
define role ZRAP_R_BOOKING_### {
  grant
    select
      on
        ZRAP_R_BOOKING_###
          where
            true;
}
```

```cds
@EndUserText.label: 'Access control for ZRAP_C_BOOKING_###'
@MappingRole: true
define role ZRAP_C_BOOKING_### {
  grant
    select
      on
        ZRAP_C_BOOKING_###
          where
            inheriting conditions from entity ZRAP_R_BOOKING_###;
}
```

C 뷰(Travel, Booking) 머리 어노테이션 확인:

```cds
@AccessControl.authorizationCheck: #CHECK     // DCL이 없으면 경고 (→ 어노테이션 탭: @AccessControl.authorizationCheck)
```

draft 쿼리 뷰:

```cds
@AccessControl.authorizationCheck: #MANDATORY                 // DCL이 반드시 있어야 함 (→ 어노테이션 탭: @AccessControl.authorizationCheck)
@EndUserText.label: 'Travel - draft query view'               // (→ 어노테이션 탭: @EndUserText.label)
@Metadata.ignorePropagatedAnnotations: true                   // 하위 객체의 어노테이션을 물려받지 않음 (→ 어노테이션 탭: @Metadata.ignorePropagatedAnnotations)
define root view entity ZRAP_R_TRAVELDRAFT_###
  as select from zrap_dtrav_###
{
  key travelid                      as TravelID,
  key draftuuid                     as DraftUUID,
      agencyid                      as AgencyID,
      customerid                    as CustomerID,
      begindate                     as BeginDate,
      enddate                       as EndDate,
      @Semantics.amount.currencyCode: 'CurrencyCode'          // (→ 어노테이션 탭: @Semantics.amount.currencyCode)
      bookingfee                    as BookingFee,
      @Semantics.amount.currencyCode: 'CurrencyCode'
      totalprice                    as TotalPrice,
      currencycode                  as CurrencyCode,
      description                   as Description,
      overallstatus                 as OverallStatus,
      attachment                    as Attachment,
      mimetype                      as MimeType,
      filename                      as FileName,
      createdby                     as CreatedBy,
      createdat                     as CreatedAt,
      locallastchangedby            as LocalLastChangedBy,
      locallastchangedat            as LocalLastChangedAt,
      lastchangedat                 as LastChangedAt,
      /* draft administrative fields (include sych_bdl_draft_admin_inc) */
      draftentitycreationdatetime   as draftentitycreationdatetime,
      draftentitylastchangedatetime as draftentitylastchangedatetime,
      draftadministrativedatauuid   as draftadministrativedatauuid,
      draftentityoperationcode      as draftentityoperationcode,
      hasactiveentity               as hasactiveentity,
      draftfieldchanges             as draftfieldchanges
}
```

```cds
@EndUserText.label: 'Access control for ZRAP_R_TRAVELDRAFT_###'
@MappingRole: true
define role ZRAP_R_TRAVELDRAFT_### {
  grant
    select
      on
        ZRAP_R_TRAVELDRAFT_###
          where
            inheriting conditions from entity ZRAP_R_TRAVEL_###;   // 활성 데이터와 같은 조건을 draft에도
}
```

BDEF(Travel 머리):

```bdef
draft table zrap_dtrav_### query ZRAP_R_TRAVELDRAFT_###     // draft 데이터를 읽을 때 이 뷰(와 그 DCL)를 사용
```

해설
- `#NOT_REQUIRED`: 검사 안 함. `#CHECK`: DCL이 없으면 구문 경고. `#MANDATORY`: DCL이 반드시 있어야 함. `#NOT_ALLOWED`: DCL이 있어도 무시.
- DCL은 **엔터티마다 따로** 만들어야 하며 자동으로 물려받지 않습니다. 그래서 C 뷰에도 `inheriting conditions from entity`로 R 뷰 조건을 상속하는 역할을 둡니다. R 쪽만 고치면 C·I·draft가 모두 따라옵니다.
- `aspect pfcg_auth( 권한객체, 권한필드, ACTVT = '03' )`는 "사용자의 권한 값과 왼쪽 요소가 일치하는 행만" 보여 줍니다. ABAP cheat sheet와 openSAP 예제는 `aspect pfcg_auth(zauth_obj, zauth_ctry, ACTVT = '03')`처럼 따옴표 없이 씁니다. `/DMO/TRVL`처럼 `/`가 들어간 이름을 따옴표로 써야 하는지는 확인하지 못했습니다. 활성화 오류가 나면 따옴표를 빼 보세요(실제 시스템에서 확인 필요). 또 R 뷰에 `_Agency` 연관이 있어야 합니다(2단계).
- openSAP 과정도 트라이얼에서 같은 이유로 PFCG 조건을 주석 처리하고 `true;`로 되돌리는 우회 방법을 씁니다.
- **draft 쿼리 뷰를 두는 이유**: draft 데이터는 활성 테이블이 아니라 draft 테이블에서 읽힙니다. 활성 데이터에만 DCL이 걸려 있으면 draft 쪽은 다른 기준으로 보이게 됩니다. `draft table ... query <뷰>`로 draft 읽기에도 DCL을 걸 수 있습니다(참조 시나리오 colldraft의 `/DMO/R_TravelDraft_CD`, xbo의 `/DMO/R_TRAVELDRAFT_XBO`와 같은 구성).
- 참조 시나리오에서는 draft 쿼리 뷰의 필드 이름이 R 뷰 요소 이름과 같습니다. 상속 조건에 쓰인 요소(`OverallStatus` 등)가 draft 쿼리 뷰에도 같은 이름으로 있어야 하기 때문입니다.
- late numbering이라 우리 draft 테이블의 키는 `travelid` + `draftuuid`입니다. 참조 시나리오(UUID 키)와 달라, draft 쿼리 뷰의 키를 이렇게 두 개로 잡는 것이 맞는지는 확인하지 못했습니다. 활성화 오류가 나면 ADT 오류 문구를 따라 키를 조정하세요(실제 시스템에서 확인 필요).
- Booking draft에도 같은 방식으로 `ZRAP_R_BOOKINGDRAFT_###`를 둘 수 있습니다. 이 문제에서는 Booking DCL이 `true`라서 생략합니다.

</details>

#### 9단계. 인터페이스 계층과 OData V4 Web API

다른 개발자나 외부 시스템이 쓰는 **안정된 계약(API)** 을 따로 만듭니다. UI용 C 계층과 분리하는 것이 핵심입니다.

1. 인터페이스 프로젝션 뷰 `ZRAP_I_TRAVEL_###`(root), `ZRAP_I_BOOKING_###`를 R 뷰 위에 만드세요. provider contract는 인터페이스용으로 **루트 `ZRAP_I_TRAVEL_###`에만** 쓰고(자식 `ZRAP_I_BOOKING_###`에는 쓰지 않음), 필드는 R 뷰 전부, 연관은 `_Booking`(→ I Booking), `_Travel`(→ I Travel)만 재지정합니다. UI 어노테이션은 넣지 않습니다.
2. 두 뷰의 접근 제어는 R 뷰 조건 상속으로 만드세요(`ZRAP_I_TRAVEL_###`, `ZRAP_I_BOOKING_###`).
3. 인터페이스 BDEF `ZRAP_I_TRAVEL_###`를 만드세요(뷰에서 우클릭 → New Behavior Definition, 구현 유형 interface).
   - draft와 side effects를 사용하고, privileged 호출을 허용합니다(10단계에서 사용). privileged 허용은 R BDEF에 privileged mode가 켜져 있어야 활성화되므로, 10단계 1번의 R BDEF 머리 세 줄을 먼저 추가하세요.
   - Travel: ETag 사용, CUD, 액션 `acceptTravel`, `rejectTravel`, `deductDiscount`, `addServiceFee`, `copyTravel`, `createTravel`, `checkDates`, 함수 `GetDefaultsFordeductDiscount`, `getOpenTravelCount`, draft 액션 5개, Booking 생성. `sendReminder`는 API에 내보내지 않습니다.
   - Booking: ETag, update, delete, 함수 `getDaysToFlight`, `_Travel` 연관.
4. `transactional_interface` 뷰는 서비스 정의에 바로 노출할 수 없습니다. I 뷰 위에 Web API용 프로젝션 뷰 `ZRAP_W_TRAVEL_###`(root, provider contract `transactional_query`), `ZRAP_W_BOOKING_###`와 프로젝션 BDEF `ZRAP_W_TRAVEL_###`(I BDEF와 같은 연산을 `use`)를 만드세요.
5. 서비스 정의 `ZRAP_API_TRAVEL_###`에 W 뷰 두 개를 `Travel`, `Booking`으로 노출하고, 서비스 바인딩 `ZRAP_API_TRAVEL_O4_###`를 **OData V4 - Web API** 유형으로 만들어 Publish하세요.
6. API 상태(release contract C1) 개념을 정리하세요. ADT에서 I 뷰나 BDEF를 열고 Properties → API State 탭을 확인합니다.

**직접 추가할 어노테이션**
- `@AccessControl.authorizationCheck` — 인터페이스 뷰도 DCL 검사 대상
- `@EndUserText.label` — 뷰/서비스 설명
- `@Metadata.ignorePropagatedAnnotations` — R 뷰의 어노테이션을 물려받지 않게 함(필요한 의미 어노테이션만 다시 적음)
- `@Semantics.amount.currencyCode` — 금액-통화 연결
- `@Semantics.systemDateTime.localInstanceLastChangedAt` — ETag 필드 의미(인터페이스 계층에서도 유지)
- `@Semantics.largeObject` / `@Semantics.mimeType` — 첨부 파일 필드 의미

**확인**
- 뷰·BDEF·SRVD가 활성화되고, SRVB에서 Publish 후 Entity Set `Travel`, `Booking`이 보입니다.
- Web API 바인딩에는 Fiori Preview 버튼이 없습니다. 서비스 URL 뒤에 `$metadata`를 붙여 브라우저로 열면(로그인 필요) `Travel`, `Booking`, 액션 이름이 메타데이터에 있습니다. `UI.` 어노테이션은 없습니다.

<details><summary>정답·해설</summary>

```cds
@AccessControl.authorizationCheck: #CHECK                     // (→ 어노테이션 탭: @AccessControl.authorizationCheck)
@EndUserText.label: 'Travel - interface projection'           // (→ 어노테이션 탭: @EndUserText.label)
@Metadata.ignorePropagatedAnnotations: true                   // (→ 어노테이션 탭: @Metadata.ignorePropagatedAnnotations)
define root view entity ZRAP_I_TRAVEL_###
  provider contract transactional_interface                    // 인터페이스 계층(재사용 API)용 프로젝션
  as projection on ZRAP_R_TRAVEL_###
{
  key TravelID,
      AgencyID,
      CustomerID,
      BeginDate,
      EndDate,
      @Semantics.amount.currencyCode: 'CurrencyCode'          // (→ 어노테이션 탭: @Semantics.amount.currencyCode)
      BookingFee,
      @Semantics.amount.currencyCode: 'CurrencyCode'
      TotalPrice,
      CurrencyCode,
      Description,
      OverallStatus,
      @Semantics.largeObject: { mimeType: 'MimeType',          // (→ 어노테이션 탭: @Semantics.largeObject)
                                fileName: 'FileName',
                                contentDispositionPreference: #ATTACHMENT }
      Attachment,
      @Semantics.mimeType: true                                // (→ 어노테이션 탭: @Semantics.mimeType)
      MimeType,
      FileName,
      CreatedBy,
      CreatedAt,
      LocalLastChangedBy,
      @Semantics.systemDateTime.localInstanceLastChangedAt: true // (→ 어노테이션 탭: @Semantics.systemDateTime.localInstanceLastChangedAt)
      LocalLastChangedAt,
      LastChangedAt,
      /* Associations */
      _Booking : redirected to composition child ZRAP_I_BOOKING_###,
      _Agency,
      _Customer,
      _OverallStatus,
      _Currency
}
```

```cds
@AccessControl.authorizationCheck: #CHECK
@EndUserText.label: 'Booking - interface projection'
@Metadata.ignorePropagatedAnnotations: true
define view entity ZRAP_I_BOOKING_###
  as projection on ZRAP_R_BOOKING_###
{
  key TravelID,
  key BookingID,
      BookingDate,
      CustomerID,
      CarrierID,
      ConnectionID,
      FlightDate,
      @Semantics.amount.currencyCode: 'CurrencyCode'
      FlightPrice,
      CurrencyCode,
      BookingStatus,
      @Semantics.systemDateTime.localInstanceLastChangedAt: true
      LocalLastChangedAt,
      /* Associations */
      _Travel : redirected to parent ZRAP_I_TRAVEL_###
}
```

```cds
@EndUserText.label: 'Access control for ZRAP_I_TRAVEL_###'
@MappingRole: true
define role ZRAP_I_TRAVEL_### {
  grant
    select
      on
        ZRAP_I_TRAVEL_###
          where
            inheriting conditions from entity ZRAP_R_TRAVEL_###;
}
```

```cds
@EndUserText.label: 'Access control for ZRAP_I_BOOKING_###'
@MappingRole: true
define role ZRAP_I_BOOKING_### {
  grant
    select
      on
        ZRAP_I_BOOKING_###
          where
            inheriting conditions from entity ZRAP_R_BOOKING_###;
}
```

인터페이스 BDEF:

```bdef
interface;                 // 인터페이스 BDEF: 아래 BO의 연산을 골라 재사용 계약으로 노출
use draft;                 // draft 연산도 노출
use side effects;          // R BDEF의 side effects를 소비자에게 전달
with privileged mode;      // 소비자가 PRIVILEGED EML로 호출할 수 있음

define behavior for ZRAP_I_TRAVEL_### alias Travel
use etag
{
  use create;
  use update;
  use delete;

  use action acceptTravel;
  use action rejectTravel;
  use action deductDiscount;
  use function GetDefaultsFordeductDiscount;
  use action addServiceFee;
  use action copyTravel;
  use action createTravel;
  use function getOpenTravelCount;
  use action checkDates;

  use action Edit;
  use action Activate;
  use action Discard;
  use action Resume;
  use action Prepare;

  use association _Booking { create; with draft; }
}

define behavior for ZRAP_I_BOOKING_### alias Booking
use etag
{
  use update;
  use delete;

  use function getDaysToFlight;

  use association _Travel { with draft; }
}
```

Web API용 프로젝션 뷰(I 뷰 위):

```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Travel - Web API projection'
@Metadata.ignorePropagatedAnnotations: true
define root view entity ZRAP_W_TRAVEL_###
  provider contract transactional_query                        // 서비스 노출용 계약 (I 뷰는 노출 불가)
  as projection on ZRAP_I_TRAVEL_###                           // I 뷰 위에 올림
{
  key TravelID,
      AgencyID,
      CustomerID,
      BeginDate,
      EndDate,
      @Semantics.amount.currencyCode: 'CurrencyCode'
      BookingFee,
      @Semantics.amount.currencyCode: 'CurrencyCode'
      TotalPrice,
      CurrencyCode,
      Description,
      OverallStatus,
      LocalLastChangedAt,
      LastChangedAt,
      _Booking : redirected to composition child ZRAP_W_BOOKING_###
}
```

```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Booking - Web API projection'
@Metadata.ignorePropagatedAnnotations: true
define view entity ZRAP_W_BOOKING_###
  as projection on ZRAP_I_BOOKING_###                          // 자식에는 provider contract 없음
{
  key TravelID,
  key BookingID,
      BookingDate,
      CustomerID,
      CarrierID,
      ConnectionID,
      FlightDate,
      @Semantics.amount.currencyCode: 'CurrencyCode'
      FlightPrice,
      CurrencyCode,
      BookingStatus,
      LocalLastChangedAt,
      _Travel : redirected to parent ZRAP_W_TRAVEL_###
}
```

프로젝션 BDEF `ZRAP_W_TRAVEL_###`:

```bdef
projection;
strict ( 2 );
use draft;
use side effects;

define behavior for ZRAP_W_TRAVEL_### alias Travel
use etag
{
  use create;
  use update;
  use delete;

  use action acceptTravel;
  use action rejectTravel;
  use action deductDiscount;
  use function GetDefaultsFordeductDiscount;
  use action addServiceFee;
  use action copyTravel;
  use action createTravel;
  use function getOpenTravelCount;
  use action checkDates;

  use action Edit;
  use action Activate;
  use action Discard;
  use action Resume;
  use action Prepare;

  use association _Booking { create; with draft; }
}

define behavior for ZRAP_W_BOOKING_### alias Booking
use etag
{
  use update;
  use delete;
  use function getDaysToFlight;
  use association _Travel { with draft; }
}
```

서비스 정의:

```cds
@EndUserText.label: 'Travel Web API'
define service ZRAP_API_TRAVEL_### {
  expose ZRAP_W_TRAVEL_###  as Travel;
  expose ZRAP_W_BOOKING_### as Booking;
}
```

서비스 바인딩: New → Service Binding, 이름 `ZRAP_API_TRAVEL_O4_###`, Binding Type `OData V4 - Web API`, Service Definition `ZRAP_API_TRAVEL_###` → 활성화 → Publish.

해설
- **3계층 구조**: R(기본 BO, 모든 로직) → C(`transactional_query`, 특정 UI용) / I(`transactional_interface`, 재사용 API용). I 계층은 UI 어노테이션 없이 안정된 이름과 연산만 노출하고, 다른 BO가 EML로 씁니다.
- **I 뷰는 서비스에 바로 못 올림**: OData 서비스(UI든 Web API든)에 노출하는 엔터티는 `transactional_query` 프로젝션이어야 합니다. 그래서 Web API는 I 뷰 위에 `transactional_query` 프로젝션(W 뷰)을 하나 더 올려 노출합니다. I 계층은 그대로 두고 10단계 EML에서 씁니다. W 뷰를 I 뷰 대신 R 뷰 위에 올려도 서비스는 동작하지만, 그러면 I 계층(안정 계약)을 거치지 않습니다.
- 인터페이스 BDEF는 `projection;`이 아니라 `interface;`로 시작합니다. 새 로직은 넣을 수 없고 `use`로 고르기만 합니다(참조 시나리오 `/DMO/I_Travel_D`와 같은 형태).
- **Web API** 바인딩은 UI 메타데이터 없이 OData 서비스만 제공합니다. 실제 외부 공개는 통신 시나리오·통신 약정(Communication Arrangement)으로 하는데, 트라이얼에서 이 구성까지 해 볼 수 있는지는 확인하지 못했습니다(실제 시스템에서 확인 필요).
- 인터페이스에 `use draft`를 넣었습니다(참조 시나리오와 동일). API 소비자에게 draft를 노출하지 않으려면 draft 액션을 빼는 설계도 가능한데, draft BO에서 `use draft` 없이 활성화되는지는 확인하지 못했습니다(실제 시스템에서 확인 필요).
- **릴리스 계약 C1**: "시스템 내부/클라우드 개발에서 사용 가능(Use System-Internally / Use in Cloud Development)" 계약입니다. 릴리스하면 그 객체는 호환되지 않는 변경(필드 삭제, 이름 변경)을 할 수 없게 되고, 다른 소프트웨어 컴포넌트에서 쓸 수 있습니다. ADT의 API State 탭에서 상태를 추가합니다. 참조 시나리오의 서비스 바인딩 메타데이터에도 `C1` 계약 표시가 있습니다. 트라이얼 공유 시스템에서 릴리스까지 해 볼 수 있는지는 확인하지 못했습니다(실제 시스템에서 확인 필요).
- `GetDefaultsForCreate`(R-02의 create 기본값 함수)는 `use create;`로 함께 노출되는지, 따로 적어야 하는지 확인하지 못했습니다. 활성화 경고가 나면 ADT 제안을 따르세요(실제 시스템에서 확인 필요).

자주 나는 오류
- 서비스 바인딩 생성 시 `Prov. contract "transactional_interface" must not be used (Entity: ZRAP_I_BOOKING_###)`: I 뷰를 서비스 정의에 바로 노출해서입니다. I 뷰 위에 `transactional_query` 프로젝션(W 뷰)을 만들고 서비스 정의에서 그 뷰를 노출하세요.
- I 뷰 활성화 시 `_Booking` 재지정 대상이 아직 없다는 오류: 두 뷰를 함께 선택해 한꺼번에 활성화(Ctrl+Shift+F3)하세요.
- 인터페이스 BDEF의 `with privileged mode;` 줄에 `"ZRAP_R_TRAVEL_###" is not defined with "with privileged mode"` 오류: R BDEF에 privileged mode가 아직 없어서입니다. 10단계 1번(R BDEF 머리의 `with privileged mode disabling …`, `define authorization context …`, `define own authorization context by privileged mode;`)을 먼저 하고 R BDEF → 인터페이스 BDEF 순서로 활성화하세요. 또는 이 줄을 주석 처리했다가 10단계에서 푸세요.

</details>

#### 10단계. privileged mode와 EML로 전체 확인

1. R BDEF 머리에 privileged mode를 켜고, 이 모드에서 꺼질 권한 컨텍스트(`/DMO/TRVL`)를 정의하세요. BO 자신의 권한 컨텍스트는 "privileged mode 컨텍스트와 같다"고 선언합니다.
2. 콘솔 클래스 `ZCL_RAP_R03_EML_###`를 만드세요. 메서드 세 개로 나눕니다.
   - `check_instance_features`: Accepted Travel 하나에 `acceptTravel`을 실행해 `%fail-cause`를 출력하고 ROLLBACK
   - `check_global_permissions`: `GET PERMISSIONS ONLY GLOBAL`로 `%create` 상태를 출력
   - `check_privileged`: Open Travel 하나의 대행사 국가를 스위치 `deny_country`에 넣고(COMMIT WORK), 인터페이스 BO `ZRAP_I_TRAVEL_###`로 Description을 (1) 일반 EML, (2) `PRIVILEGED` EML로 수정해 결과를 비교. (2)는 `COMMIT ENTITIES`로 저장하고, 마지막에 스위치를 원래 값으로 되돌림
3. 최종 BDEF 전체를 정리하세요.

**확인**
- `check_instance_features`: `fail-cause` 값이 `if_abap_behv=>cause-disabled`와 같다고 출력됩니다.
- `check_global_permissions`: 스위치 `create_closed`가 켜져 있으면 `%create`가 disabled 값으로 나옵니다.
- `check_privileged`: (1)은 `cause-unauthorized`와 메시지 032, (2)는 실패 없이 저장되고 Data Preview에서 Description이 바뀌어 있습니다.

<details><summary>정답·해설</summary>

R-03 최종 BDEF `ZRAP_R_TRAVEL_###` 전체:

```bdef
managed implementation in class zbp_rap_r_travel_### unique;
strict ( 2 );
with draft;
with privileged mode disabling NoCheckWhenPrivileged;              // PRIVILEGED 호출 시 아래 컨텍스트의 권한 검사를 끔
define authorization context NoCheckWhenPrivileged { '/DMO/TRVL'; } // 끌 권한 객체 목록
define own authorization context by privileged mode;               // 이 BO 자신의 권한 컨텍스트 = privileged mode 컨텍스트

define behavior for ZRAP_R_TRAVEL_### alias Travel
persistent table zrap_atrav_###
draft table zrap_dtrav_### query ZRAP_R_TRAVELDRAFT_###
etag master LocalLastChangedAt
lock master total etag LastChangedAt
authorization master ( global, instance )
late numbering
{
  // 표준 작업 (+ 전역/인스턴스 기능 제어, precheck)
  create ( features : global, precheck ) { default function GetDefaultsForCreate; }
  update ( features : instance, precheck );
  delete ( features : instance );
  association _Booking { create ( features : instance, authorization : update ); with draft; }

  // 정적 필드 제어
  field ( readonly ) TravelID, TotalPrice, OverallStatus,
                     CreatedBy, CreatedAt, LocalLastChangedBy, LocalLastChangedAt, LastChangedAt;
  field ( mandatory ) CustomerID, BeginDate, EndDate, CurrencyCode;
  field ( mandatory : create, readonly : update ) AgencyID;
  // 동적 필드 제어
  field ( features : instance ) BookingFee;

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
  action ( features : instance, authorization : update ) acceptTravel result [1] $self;
  action ( features : instance, authorization : update ) rejectTravel result [1] $self;
  action ( features : instance, authorization : update ) deductDiscount parameter ZRAP_A_DISCOUNT_### result [1] $self
    { default function GetDefaultsFordeductDiscount; }
  repeatable action ( authorization : update ) addServiceFee result [1] $self;
  action ( lock : none, authorization : update ) sendReminder result [1] $self;
  factory action copyTravel [1];
  static default factory action ( features : global ) createTravel parameter ZRAP_A_CREATE_TRAVEL_### [1];

  // 함수
  static function getOpenTravelCount result [1] ZRAP_A_TRAVEL_STAT_###;

  // determine action
  determine action ( authorization : update ) checkDates { validation validateDates; }

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

EML 콘솔 클래스:

```abap
CLASS zcl_rap_r03_eml_### DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_oo_adt_classrun.

  PRIVATE SECTION.
    CONSTANTS c_ctrl_id TYPE c LENGTH 10 VALUE 'TRAVEL'.

    METHODS check_instance_features
      IMPORTING out TYPE REF TO if_oo_adt_classrun_out.
    METHODS check_global_permissions
      IMPORTING out TYPE REF TO if_oo_adt_classrun_out.
    METHODS check_privileged
      IMPORTING out TYPE REF TO if_oo_adt_classrun_out.
ENDCLASS.


CLASS zcl_rap_r03_eml_### IMPLEMENTATION.

  METHOD if_oo_adt_classrun~main.
    check_instance_features( out ).
    check_global_permissions( out ).
    check_privileged( out ).
  ENDMETHOD.


  METHOD check_instance_features.

    out->write( `--- 1) instance feature control ---` ).

    SELECT FROM zrap_atrav_###
      FIELDS MIN( travel_id )
      WHERE overall_status = 'A'
      INTO @DATA(accepted_id).
    IF accepted_id IS INITIAL.
      out->write( `No accepted travel - accept one in the app first.` ).
      RETURN.
    ENDIF.

    MODIFY ENTITIES OF zrap_r_travel_###
      ENTITY Travel
        EXECUTE acceptTravel
        FROM VALUE #( ( %is_draft = if_abap_behv=>mk-off
                        TravelID  = accepted_id ) )
      FAILED DATA(failed)
      REPORTED DATA(reported).

    LOOP AT failed-travel INTO DATA(failed_line).
      out->write( |Travel { failed_line-TravelID }: fail-cause = { failed_line-%fail-cause }| ).
      IF failed_line-%fail-cause = if_abap_behv=>cause-disabled.
        out->write( `-> cause-disabled: blocked by get_instance_features` ).
      ENDIF.
    ENDLOOP.

    ROLLBACK ENTITIES.

  ENDMETHOD.


  METHOD check_global_permissions.

    out->write( `--- 2) global feature control / global authorization ---` ).

    DATA request TYPE STRUCTURE FOR PERMISSIONS REQUEST zrap_r_travel_###.
    request = VALUE #( %create = if_abap_behv=>mk-on ).

    GET PERMISSIONS ONLY GLOBAL ENTITY zrap_r_travel_###
      REQUEST request
      RESULT DATA(permissions)
      FAILED DATA(failed)
      REPORTED DATA(reported).

    out->write( data = permissions name = `GET PERMISSIONS result` ).

  ENDMETHOD.


  METHOD check_privileged.

    out->write( `--- 3) privileged mode ---` ).

    "an open travel and its agency country
    SELECT FROM zrap_atrav_### AS travel
      INNER JOIN /dmo/i_agency AS agency ON travel~agency_id = agency~AgencyID
      FIELDS travel~travel_id, agency~CountryCode
      WHERE travel~overall_status = 'O'
      ORDER BY travel~travel_id
      INTO TABLE @DATA(open_travels)
      UP TO 1 ROWS.
    IF open_travels IS INITIAL.
      out->write( `No open travel found.` ).
      RETURN.
    ENDIF.
    DATA(open_travel) = open_travels[ 1 ].

    "remember the switch and deny this country (outside of any RAP transaction)
    SELECT SINGLE FROM zrap_ctrl_###
      FIELDS deny_country
      WHERE ctrl_id = @c_ctrl_id
      INTO @DATA(old_deny_country).
    IF sy-subrc <> 0.
      out->write( `Run ZCL_RAP_R03_CTRL_### first.` ).
      RETURN.
    ENDIF.
    UPDATE zrap_ctrl_### SET deny_country = @open_travel-countrycode WHERE ctrl_id = @c_ctrl_id.
    COMMIT WORK.

    "(1) normal call -> instance authorization denies
    MODIFY ENTITIES OF zrap_i_travel_###
      ENTITY Travel
        UPDATE FIELDS ( Description )
        WITH VALUE #( ( %is_draft   = if_abap_behv=>mk-off
                        TravelID    = open_travel-travel_id
                        Description = `Changed without privilege` ) )
      FAILED DATA(failed_normal)
      REPORTED DATA(reported_normal).

    LOOP AT failed_normal-travel INTO DATA(f1).
      out->write( |(1) normal: fail-cause = { f1-%fail-cause }| ).
    ENDLOOP.
    LOOP AT reported_normal-travel INTO DATA(r1) WHERE %msg IS BOUND.
      out->write( |(1) message: { r1-%msg->if_message~get_text( ) }| ).
    ENDLOOP.
    ROLLBACK ENTITIES.

    "(2) privileged call -> authorization context NoCheckWhenPrivileged is switched off
    MODIFY ENTITIES OF zrap_i_travel_### PRIVILEGED
      ENTITY Travel
        UPDATE FIELDS ( Description )
        WITH VALUE #( ( %is_draft   = if_abap_behv=>mk-off
                        TravelID    = open_travel-travel_id
                        Description = `Changed in privileged mode` ) )
      FAILED DATA(failed_priv)
      REPORTED DATA(reported_priv).

    IF failed_priv-travel IS INITIAL.
      COMMIT ENTITIES RESPONSE OF zrap_i_travel_###
        FAILED DATA(commit_failed)
        REPORTED DATA(commit_reported).
      out->write( |(2) privileged: COMMIT ENTITIES sy-subrc = { sy-subrc }| ).
    ELSE.
      out->write( `(2) privileged: still failed - check the BDEF header` ).
      ROLLBACK ENTITIES.
    ENDIF.

    "restore the switch
    UPDATE zrap_ctrl_### SET deny_country = @old_deny_country WHERE ctrl_id = @c_ctrl_id.
    COMMIT WORK.

  ENDMETHOD.

ENDCLASS.
```

해설
- **privileged mode**는 "믿을 수 있는 호출자(다른 BO, 백그라운드 처리)가 사용자 권한과 무관하게 BO를 쓰게" 하는 장치입니다. `with privileged mode disabling NoCheckWhenPrivileged;`는 PRIVILEGED EML로 들어온 요청에서 `NoCheckWhenPrivileged` 컨텍스트에 있는 권한 객체(`/DMO/TRVL`)의 `AUTHORITY-CHECK`를 하지 않게(성공으로) 합니다. 핸들러 메서드 자체는 그대로 불립니다.
- `define own authorization context`는 이 BO가 스스로 검사하는 권한 객체의 목록입니다. 참조 시나리오 colldraft처럼 `define own authorization context { '/DMO/TR_CD'; }`로 직접 나열할 수도 있고, draft 시나리오처럼 `by privileged mode`로 "privileged mode 컨텍스트와 같다"고 줄여 쓸 수도 있습니다(문법은 `/DMO/R_Travel_D`와 동일).
- 인터페이스 BDEF의 `with privileged mode;`가 있어야 소비자가 그 BDEF로 `PRIVILEGED`를 쓸 수 있습니다(`/DMO/I_Travel_D`와 동일).
- 우리 시뮬레이션은 실제 AUTHORITY-CHECK 결과를 쓰지 않으므로, `simulate_authorization`에서 `cl_abap_behv_aux=>get_current_context`의 `privileged` 값을 직접 확인해 같은 효과를 냅니다.
- `MODIFY ENTITIES OF ... PRIVILEGED ENTITY ...`에서 `PRIVILEGED`의 위치는 ABAP 키워드 문서의 "ABAP EML - PRIVILEGED" 항목을 기준으로 적었지만 로컬 자료에 실제 문장 예제가 없어 확인하지 못했습니다. 구문 오류가 나면 F1 도움말로 위치를 확인하세요(실제 시스템에서 확인 필요).
- 콘솔 클래스는 RAP 트랜잭션의 **소비자**이므로 `COMMIT WORK`, `COMMIT ENTITIES`, `ROLLBACK ENTITIES`를 쓸 수 있습니다. 같은 문장을 행동 구현 안에서 쓰면 안 됩니다(R-04 1단계).
- 스위치 UPDATE 뒤에 `COMMIT WORK`를 바로 하는 이유: 이후의 `ROLLBACK ENTITIES`가 `ROLLBACK WORK`를 함께 하므로, 커밋하지 않으면 스위치 변경도 되돌려집니다.
- `GET PERMISSIONS` 결과 구조의 정확한 컴포넌트 이름은 cheat sheet에 나오지 않아 구조 전체를 출력합니다. 디버거로 `permissions`를 열어 `%create` 값을 찾아보세요(실제 시스템에서 확인 필요).

클래스 구조 해설
- 이 클래스는 행동 풀이 아니라 일반 소비자입니다. 일반 EML(`IN LOCAL MODE` 없음)을 쓰므로 권한·기능 제어·precheck가 모두 동작합니다.
- 실행 흐름: `MODIFY` → (framework) 전역 권한 → 인스턴스 권한 → 기능 제어 → precheck → 버퍼 반영. `COMMIT ENTITIES` → 저장 시퀀스(R-04).

</details>

### R-04. 저장 시퀀스 완전 정복: late numbering·추가 저장·비즈니스 이벤트·unmanaged save [작성] ★★★
<!-- covers: RAP transaction, interaction phase, early save phase, late save phase, point of no return, finalize, check_before_save, cleanup_finalize, adjust_numbers, save, save_modified, cleanup, COMMIT ENTITIES, COMMIT ENTITIES BEGIN END, CONVERT KEY, IN SIMULATION MODE, ROLLBACK ENTITIES, controlled SAP LUW, cl_abap_tx, BEHAVIOR_ILLEGAL_STMT_IN_CALL, late numbering, %pid, %tmp, %pre, DRAFTUUID, PARENTDRAFTUUID, number range object, cl_numberrange_runtime, READ BY association LINK, with additional save, with full data, REQUEST FOR CHANGE, %control, RTTI, change log, business event, event parameter, RAISE ENTITY EVENT, FOR EVENTS OF, cl_abap_behavior_event_handler, FOR ENTITY EVENT, event binding, SAP Event Mesh, managed event, event for side effects, with unmanaged save, and cleanup, MAPPING FROM ENTITY, INDICATORS SET STRUCTURE -->
**목표**
- RAP 트랜잭션의 단계(인터랙션 → early save → late save)와 각 saver 메서드가 불리는 순서를 설명하고, 단계마다 금지된 문장을 압니다.
- late numbering을 번호 범위 객체로 구현하고, 자식(Booking) 번호를 부모별로 매길 수 있습니다.
- `with additional save with full data`로 변경 로그를 남기고, 비즈니스 이벤트를 발생시켜 로컬 이벤트 핸들러로 받을 수 있습니다.
- `with unmanaged save`로 저장을 직접 구현해 보고, additional save와 언제 나눠 쓰는지 판단할 수 있습니다.

**전제**
- R-03까지 끝난 Travel/Booking BO(`ZRAP_R_TRAVEL_###`, 행동 풀 `ZBP_RAP_R_TRAVEL_###`, 스위치 테이블 `ZRAP_CTRL_###`)가 활성화되어 있습니다.
- R-01에서 late numbering용 `adjust_numbers`를 임시로(예: SELECT MAX) 구현해 두었고, 세이버 클래스가 `ZBP_RAP_R_TRAVEL_###`의 Local Types에 있습니다. 이 문제에서 그 세이버 클래스를 **완성본으로 교체**합니다. 세이버 클래스 이름은 `lsc_zrap_r_travel_###`라고 가정합니다(R-01 이름이 다르면 그 이름을 쓰세요).
- R-02 액션 `acceptTravel`, `rejectTravel`이 `OverallStatus`를 `A`/`X`로 바꿉니다.
- 표준 뷰: `/DMO/I_Agency`, `/DMO/I_Customer`, `/DMO/I_Flight`(AirlineID, ConnectionID, FlightDate, Price, CurrencyCode).

**만들 객체**

| 순서 | 객체 유형 | 이름 | 역할 |
|---|---|---|---|
| 1 | 클래스(콘솔) | `ZCL_RAP_R04_SEQ_###` | 저장 시퀀스·late numbering 관찰 |
| 2 | 번호 범위 객체 | `ZRAP_NR_###` | Travel ID 번호 |
| 3 | 클래스(콘솔) | `ZCL_RAP_R04_NR_###` | 번호 범위 구간(interval) 만들기 |
| 4 | BDEF 변경 | `ZRAP_R_TRAVEL_###` | additional save, 이벤트, (변형) unmanaged save |
| 5 | 행동 풀 변경 | `ZBP_RAP_R_TRAVEL_###` | 세이버 클래스 완성 |
| 6 | 데이터베이스 테이블 | `ZRAP_TLOG_###` | 변경 로그 |
| 7 | 데이터 정의(추상 엔터티) | `ZRAP_A_TRAVEL_EVT_###` | 이벤트 파라미터 |
| 8 | 데이터베이스 테이블 | `ZRAP_EVLOG_###` | 이벤트 수신 로그 |
| 9 | 클래스(이벤트 핸들러) | `ZCL_RAP_TRAV_EVT_###` | 로컬 이벤트 소비 |

#### 1단계. 저장 시퀀스 지도 그리기와 금지 문장 실험

1. 아래 빈칸 표를 채우세요. (답은 정답에 있습니다.)

| 단계 | 하위 단계 | 메서드/처리 | managed에서 자동으로 하는 일 | DB 변경 가능? |
|---|---|---|---|---|
| 인터랙션 | | 핸들러 메서드(create/update/action…) | | |
| 저장 시퀀스 | early save | ① ② ③ | | |
| | (point of no return) | | | |
| | late save | ④ ⑤ ⑥ | | |

2. 콘솔 클래스 `ZCL_RAP_R04_SEQ_###`의 첫 메서드 `show_early_save_failure`를 만드세요.
   - 존재하지 않는 고객 `999999`로 활성 Travel을 EML CREATE(필수 필드는 모두 채움) 하고 `COMMIT ENTITIES RESPONSE OF ...`를 실행합니다.
   - `sy-subrc`, `FAILED`/`REPORTED`(validation `validateCustomer`의 메시지)를 출력하고 `ROLLBACK ENTITIES` 합니다.
   - 같은 CREATE를 `COMMIT ENTITIES IN SIMULATION MODE`로 한 번 더 실행해 `sy-subrc`를 비교합니다.
3. (실험 후 반드시 원복) R-03의 `sendReminder` 구현 맨 앞에 `MODIFY zrap_ctrl_### FROM ...` 한 줄을 임시로 넣고 앱에서 Send Reminder를 눌러 어떤 오류가 나는지 확인하세요. 확인 후 그 줄을 지우세요.

**확인**
- 2번: 일반 COMMIT과 시뮬레이션 COMMIT 모두 `sy-subrc = 4`, `failed-travel`에 한 줄, 고객 관련 메시지(R-02 메시지 002)가 출력됩니다.
- 3번: 런타임 오류(덤프)가 나고, ADT의 Feed Reader 또는 ABAP Runtime Errors에서 `BEHAVIOR_ILLEGAL_STMT_IN_CALL` 같은 이름을 볼 수 있습니다(이름은 실제 시스템에서 확인).

<details><summary>정답·해설</summary>

| 단계 | 하위 단계 | 메서드/처리 | managed에서 자동으로 하는 일 | DB 변경 가능? |
|---|---|---|---|---|
| 인터랙션 | – | 핸들러 메서드(권한, 기능 제어, precheck, create/update/delete/action, on modify determination) | 버퍼 관리, 잠금, ETag 비교, 관리 필드 채우기 | 불가 |
| 저장 시퀀스 | early save | ① `finalize` | on save determination 실행 | 불가 |
| | | ② `check_before_save` | on save validation 실행 | 불가 |
| | | ③ `cleanup_finalize` | ①② 중 실패가 있을 때만 호출, 인터랙션 단계로 되돌아감 | 불가 |
| | point of no return | – | early save가 성공하면 더는 되돌아갈 수 없음 | – |
| | late save | ④ `adjust_numbers` | late numbering일 때만. 최종 키 부여 | 기술적으로는 late save라 가능하지만, 여기서는 키 부여만 하고 저장은 ⑤에서 |
| | | ⑤ `save` / `save_modified` | managed: 버퍼를 persistent table에 씀. additional/unmanaged save면 `save_modified` 호출 | **가능** |
| | | ⑥ `cleanup` | 버퍼 비우기, 끝에 암시적 `COMMIT WORK` | – |

```abap
CLASS zcl_rap_r04_seq_### DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_oo_adt_classrun.

  PRIVATE SECTION.
    METHODS show_early_save_failure
      IMPORTING out TYPE REF TO if_oo_adt_classrun_out.
ENDCLASS.


CLASS zcl_rap_r04_seq_### IMPLEMENTATION.

  METHOD if_oo_adt_classrun~main.
    show_early_save_failure( out ).
  ENDMETHOD.


  METHOD show_early_save_failure.

    out->write( `--- early save failure ---` ).

    SELECT SINGLE FROM /dmo/i_agency FIELDS AgencyID INTO @DATA(agency_id).
    DATA(today) = cl_abap_context_info=>get_system_date( ).

    DO 2 TIMES.
      MODIFY ENTITIES OF zrap_r_travel_###
        ENTITY Travel
          CREATE FIELDS ( AgencyID CustomerID BeginDate EndDate CurrencyCode Description )
          WITH VALUE #( ( %cid         = 'T1'
                          %is_draft    = if_abap_behv=>mk-off
                          AgencyID     = agency_id
                          CustomerID   = '999999'          "does not exist
                          BeginDate    = today + 10
                          EndDate      = today + 20
                          CurrencyCode = 'EUR'
                          Description  = 'R-04 early save test' ) )
        MAPPED DATA(mapped)
        FAILED DATA(failed)
        REPORTED DATA(reported).

      out->write( |Interaction phase: failed lines = { lines( failed-travel ) }| ).

      IF sy-index = 1.
        COMMIT ENTITIES RESPONSE OF zrap_r_travel_###
          FAILED DATA(commit_failed)
          REPORTED DATA(commit_reported).
        out->write( |COMMIT ENTITIES: sy-subrc = { sy-subrc }| ).
      ELSE.
        COMMIT ENTITIES IN SIMULATION MODE RESPONSE OF zrap_r_travel_###
          FAILED commit_failed
          REPORTED commit_reported.
        out->write( |COMMIT ENTITIES IN SIMULATION MODE: sy-subrc = { sy-subrc }| ).
      ENDIF.

      out->write( |Early save: failed lines = { lines( commit_failed-travel ) }| ).
      LOOP AT commit_reported-travel INTO DATA(message) WHERE %msg IS BOUND.
        out->write( message-%msg->if_message~get_text( ) ).
      ENDLOOP.

      "back in the interaction phase - discard the buffer
      ROLLBACK ENTITIES.
    ENDDO.

  ENDMETHOD.

ENDCLASS.
```

실험 3에서 임시로 넣는 줄(확인 후 삭제):

```abap
    "!!! forbidden: database change in the interaction phase - remove after the test !!!
    MODIFY zrap_ctrl_### FROM @( VALUE zrap_ctrl_###( ctrl_id = 'DUMMY' ) ).
```

해설
- **인터랙션 단계**에서는 데이터가 버퍼에만 있고 일시적으로 일관성이 없어도 됩니다. **early save**(`finalize` → `check_before_save`)에서 일관성을 확인하고, 실패하면 `cleanup_finalize`를 거쳐 인터랙션 단계로 돌아갑니다. 이때 `COMMIT ENTITIES` 뒤 `sy-subrc = 4`입니다.
- early save를 통과하면 **point of no return**입니다. late save(`adjust_numbers` → `save`/`save_modified` → `cleanup`)에서는 실패하면 안 됩니다. 실패하면 되돌아갈 수 없고 런타임 오류가 납니다. 그래서 모든 검사는 early save까지 끝내야 합니다(BAPI처럼 late save에서 실패할 수 있는 특수한 경우는 `CL_ABAP_BEHAVIOR_SAVER_FAILED`를 쓰지만 이 문제집 범위 밖입니다).
- managed BO에서 `finalize`/`check_before_save`에 해당하는 일은 on save determination과 validation이 맡습니다. managed 세이버 클래스에서 `finalize`, `check_before_save`를 직접 재정의할 수 있는지는 로컬 자료에서 확인하지 못했습니다. 재정의하지 말고 determination/validation을 쓰세요(실제 시스템에서 확인 필요).
- BDL에는 저장 단계에서만 부를 수 있는 **save action**(`save ( finalize ) action ...`, `save ( adjustnumbers ) action ...`)도 있습니다(cheat sheet 36의 `save(...) action act21;`). 이 문제에서는 쓰지 않습니다.
- `COMMIT ENTITIES IN SIMULATION MODE`는 early save까지만 실행하고 실제로 저장하지 않습니다. 저장 전에 "이대로 저장하면 통과하는가"를 확인할 때 씁니다.
- **금지 문장**(행동 구현 안): `COMMIT WORK`, `ROLLBACK WORK`, `COMMIT ENTITIES`, 인터랙션/early save 단계의 DB 변경(`INSERT/UPDATE/MODIFY/DELETE`), `RAISE EXCEPTION`으로 트랜잭션 빠져나가기, `CALL TRANSACTION`, `SUBMIT`, 화면 처리(`MESSAGE` without INTO, `WRITE` 등). 암시적 커밋을 일으키는 동작(예: 표준 커넥션에서 원격 호출, `WAIT`)도 피해야 합니다. 번호 범위·애플리케이션 로그처럼 **보조 DB 커넥션**을 쓰는 인프라 기능은 예외로 허용됩니다.
- **controlled SAP LUW**: RAP 핸들러 안은 암묵적으로 `modify` 트랜잭션 단계, late save는 `save` 단계입니다. `modify` 단계의 DB 변경은 위반으로 감지되어 런타임 오류(ABAP Cloud에서 `BEHAVIOR_ILLEGAL_STMT_IN_CALL`, cheat sheet 17)가 납니다. RAP 밖(백그라운드 처리, 이벤트 핸들러)에서는 `cl_abap_tx=>modify( )`, `cl_abap_tx=>save( )`로 단계를 직접 엽니다(9단계).

</details>

#### 2단계. BDEF를 additional save로 바꾸고 세이버 클래스 뼈대 만들기

1. BDEF 머리를 "기본 저장은 framework가 하고, 그 뒤에 내 저장 로직을 추가로 실행하며, `save_modified`에 키뿐 아니라 **모든 필드 값**을 넘겨 달라"는 뜻으로 바꾸세요.
2. 세이버 클래스 `lsc_zrap_r_travel_###`의 정의부를 완성하세요: 상속, 상수 `travel_status`, 재정의 메서드 `adjust_numbers`, `save_modified`, `cleanup_finalize`. 구현은 이번 단계에서는 빈 껍데기(단, `adjust_numbers`는 R-01 코드 유지)로 둡니다.
3. 활성화 후 앱에서 Travel 하나를 수정·저장해 기존 동작이 그대로인지 확인하세요.

**확인**
- BDEF와 행동 풀이 활성화됩니다. `save_modified`를 재정의하지 않으면 "with additional save에는 save_modified 구현이 필요하다"는 취지의 구문 오류가 납니다(문구는 실제 시스템에서 확인).
- 앱 저장이 기존처럼 동작합니다.

<details><summary>정답·해설</summary>

BDEF 머리(R-03 머리의 첫 줄만 바뀝니다):

```bdef
managed with additional save with full data
implementation in class zbp_rap_r_travel_### unique;   // 기본 저장 + 내 저장(save_modified), 전체 필드 값 전달
strict ( 2 );
with draft;
with privileged mode disabling NoCheckWhenPrivileged;
define authorization context NoCheckWhenPrivileged { '/DMO/TRVL'; }
define own authorization context by privileged mode;
```

세이버 클래스(Local Types, 핸들러 클래스들보다 위나 아래 어디든 됩니다):

```abap
CLASS lsc_zrap_r_travel_### DEFINITION INHERITING FROM cl_abap_behavior_saver.

  PROTECTED SECTION.

    CONSTANTS:
      BEGIN OF travel_status,
        open     TYPE c LENGTH 1 VALUE 'O', "Open
        accepted TYPE c LENGTH 1 VALUE 'A', "Accepted
        rejected TYPE c LENGTH 1 VALUE 'X', "Rejected
      END OF travel_status.

    "late save: final keys for late numbering
    METHODS adjust_numbers REDEFINITION.

    "late save: called after the managed save (with additional save)
    METHODS save_modified REDEFINITION.

    "early save failed: undo own changes from finalize (nothing to undo here)
    METHODS cleanup_finalize REDEFINITION.

ENDCLASS.


CLASS lsc_zrap_r_travel_### IMPLEMENTATION.

  METHOD adjust_numbers.
    "keep the R-01 implementation for now - replaced in steps 3 and 4
  ENDMETHOD.

  METHOD save_modified.
    "implemented in step 7
  ENDMETHOD.

  METHOD cleanup_finalize.
    "no own buffer in this BO - nothing to reset
  ENDMETHOD.

ENDCLASS.
```

(위 `adjust_numbers`의 주석은 "R-01 코드를 지우지 말라"는 뜻입니다. R-01 코드를 그대로 두세요.)

해설
- 저장 옵션은 BO 전체에 적용됩니다. `define behavior for ... with additional save`처럼 엔터티별로 줄 수도 있습니다(cheat sheet 36).
- `with full data`가 없으면 `save_modified`에는 키와 **바뀐 필드**만 들어옵니다. 로그·이벤트에 다른 필드(대행사, 고객 등)가 필요하므로 `with full data`를 씁니다. 이때도 `%control`은 "실제로 바뀐 필드"를 표시하므로 변경 필드만 고를 수 있습니다(RAP110이 `%control-OverallStatus`로 이렇게 사용).
- 세이버 클래스는 `CL_ABAP_BEHAVIOR_SAVER`를 상속하고, 메서드는 모두 `REDEFINITION`입니다. 이름이 정해져 있으므로 이름을 바꾸면 안 됩니다. 세이버는 프로젝션당 하나가 아니라 **BO당 하나**(루트의 행동 풀)입니다.

클래스 구조 해설
- 세이버 메서드에는 인스턴스 데이터가 import로 오지 않습니다(예외: `save_modified`의 `create`/`update`/`delete`, `adjust_numbers`의 `mapped`). 나머지는 `READ ENTITIES ... IN LOCAL MODE`로 버퍼를 읽습니다.
- `save_modified`의 파라미터 타입: `create`, `update`는 `REQUEST FOR CHANGE`, `delete`는 `REQUEST FOR DELETE`. 엔터티별 표(`create-travel`, `create-booking` …)가 들어 있습니다.

</details>

#### 3단계. 번호 범위 객체로 Travel 번호 매기기

1. 번호 범위 객체 `ZRAP_NR_###`를 만드세요(ADT: New → Other ABAP Repository Object → 검색어 `Number Range`). 번호 길이 도메인은 `/DMO/TRAVEL_ID`, 버퍼링 허용, 설명 `Travel ID ###`.
2. 콘솔 클래스 `ZCL_RAP_R04_NR_###`로 구간 `01`을 만드세요. 시작 번호는 현재 `ZRAP_ATRAV_###`의 최대 `travel_id + 1`, 끝 번호 `99999999`입니다.
3. 세이버의 `adjust_numbers`에서 Travel 부분을 구현하세요.
   - `mapped-travel`의 줄 수만큼 `cl_numberrange_runtime=>number_get`(`nr_range_nr = '01'`, `object = 'ZRAP_NR_###'`, `quantity`)으로 한 번에 받습니다. 받은 마지막 번호에서 거꾸로 계산해 각 줄의 `TravelID`에 넣습니다.
   - 번호 범위를 쓸 수 없을 때를 위한 대체 경로(상수 `c_use_number_range = abap_false`이거나 `cx_number_ranges` 예외)를 둡니다: 활성 테이블의 `MAX( travel_id )` + 1부터 순서대로.
4. 대체 경로의 동시성 위험을 해설에 적어 보세요.

**확인**
- 콘솔 클래스 실행 시 구간 생성 결과(오류 없음)가 출력됩니다.
- 앱에서 새 Travel을 만들고 저장하면, 저장 전(draft)에는 Travel ID가 비어 있다가 저장 후 번호가 붙습니다. 연속해서 두 건을 저장하면 번호가 1씩 늘어납니다.

<details><summary>정답·해설</summary>

번호 범위 구간 생성 클래스:

```abap
CLASS zcl_rap_r04_nr_### DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_oo_adt_classrun.
ENDCLASS.


CLASS zcl_rap_r04_nr_### IMPLEMENTATION.

  METHOD if_oo_adt_classrun~main.

    "start behind the highest existing travel ID
    SELECT FROM zrap_atrav_### FIELDS MAX( travel_id ) INTO @DATA(max_travel_id).
    DATA(from_number) = CONV /dmo/travel_id( max_travel_id + 1 ).

    TRY.
        cl_numberrange_intervals=>create(
          EXPORTING
            interval  = VALUE #( ( nrrangenr  = '01'
                                   fromnumber = from_number
                                   tonumber   = '99999999'
                                   procind    = 'I' ) )
            object    = 'ZRAP_NR_###'
          IMPORTING
            error     = DATA(error)
            error_inf = DATA(error_inf)
            error_iv  = DATA(error_iv)
            warning   = DATA(warning) ).
        out->write( |Interval 01 from { from_number }: error = { error }, warning = { warning }| ).
        out->write( error_iv ).
      CATCH cx_number_ranges INTO DATA(nr_error).
        out->write( nr_error->get_text( ) ).
    ENDTRY.

  ENDMETHOD.

ENDCLASS.
```

`adjust_numbers`(Travel 부분, Booking 부분은 4단계에서 이어 붙입니다):

```abap
  METHOD adjust_numbers.

    "======== Root entity: Travel =================================
    IF mapped-travel IS NOT INITIAL.

      DATA travel_id_max TYPE /dmo/travel_id.
      DATA number_ok     TYPE abap_bool.

      IF c_use_number_range = abap_true.
        TRY.
            cl_numberrange_runtime=>number_get(
              EXPORTING
                nr_range_nr       = '01'
                object            = 'ZRAP_NR_###'
                quantity          = CONV #( lines( mapped-travel ) )
              IMPORTING
                number            = DATA(number_range_key)
                returncode        = DATA(number_range_return_code)
                returned_quantity = DATA(number_range_returned_quantity) ).
            IF number_range_returned_quantity = lines( mapped-travel ).
              "number = last number drawn -> step back to the first one
              travel_id_max = number_range_key - number_range_returned_quantity.
              number_ok = abap_true.
            ENDIF.
          CATCH cx_number_ranges.
            number_ok = abap_false.
        ENDTRY.
      ENDIF.

      IF number_ok = abap_false.
        "Fallback (training only): not safe under parallel saves, see explanation
        SELECT FROM zrap_atrav_### FIELDS MAX( travel_id ) INTO @travel_id_max.
      ENDIF.

      LOOP AT mapped-travel ASSIGNING FIELD-SYMBOL(<travel>).
        travel_id_max += 1.
        <travel>-TravelID = travel_id_max.
      ENDLOOP.
    ENDIF.

  ENDMETHOD.
```

세이버 정의부에 상수 추가:

```abap
    "abap_false = always use the SELECT MAX fallback (e.g. no number range object available)
    CONSTANTS c_use_number_range TYPE abap_bool VALUE abap_true.
```

해설
- **late numbering**은 키를 저장 직전(`adjust_numbers`)에 매깁니다. 그래서 저장이 실패한 draft·버퍼 인스턴스가 번호를 낭비하지 않고, "번호에 빈틈이 없어야 하는" 업무에 맞습니다. 그 전까지 인스턴스는 `%pid`(임시 ID)와 draft 키 `DRAFTUUID`로 구분됩니다(5단계에서 관찰).
- `mapped-travel`에는 이번 저장에서 새로 만들어진 Travel만 들어 있습니다. 여기서 `%key`(최종 키, 여기서는 `TravelID`)를 채워 돌려주면 framework가 `%pre`(= `%pid` + `%tmp`)와 최종 키를 연결합니다.
- `number_get`의 `number`는 받은 번호 중 **마지막** 번호입니다. 그래서 `number - quantity`에서 시작해 1씩 더합니다(RAP110 ex04와 같은 계산).
- 번호 범위는 보조 DB 커넥션으로 처리되므로 late save에서 써도 SAP LUW를 깨지 않습니다(cheat sheet 08의 허용/금지 표: "number ranges"는 보조 커넥션 용도).
- **대체 경로의 위험**: 두 사용자가 동시에 저장하면 둘 다 같은 `MAX`를 읽고 같은 번호를 매길 수 있습니다. 그러면 나중 사람의 INSERT가 키 중복으로 실패하는데, late save에서는 실패를 처리할 수 없어 런타임 오류가 납니다. 실습용으로만 쓰고, 운영에서는 번호 범위(또는 UUID 키)를 써야 합니다.
- 번호 범위 객체를 ADT에서 만들 수 있는지, 트라이얼에서 `cl_numberrange_intervals=>create`가 허용되는지와 그 파라미터 이름은 로컬 자료로 확인하지 못했습니다. RAP110 저장소에는 번호 범위 객체(`ZRAP110SOL`, 도메인 `/DMO/TRAVEL_ID`)가 들어 있으므로 객체 자체는 만들 수 있는 것으로 보입니다. 안 되면 `c_use_number_range = abap_false`로 두고 진행하세요(실제 시스템에서 확인 필요). RAP110은 대체로 표준 객체 `/DMO/TRV_M`를 제안합니다.
- RAP110 원본은 `cx_number_ranges`를 잡아 `RAISE SHORTDUMP` 합니다(late save에서는 실패를 돌려줄 길이 없으므로). 이 정답은 학습 편의를 위해 대체 경로로 넘어갑니다.

클래스 구조 해설
- `adjust_numbers`는 BDEF에 `late numbering`이 있을 때만 재정의할 수 있습니다. 파라미터는 `mapped`(CHANGING 성격)이며, framework가 late save 첫 단계에서 한 번 부릅니다.

</details>

#### 4단계. Booking 번호: 부모 Travel별로 매기기

1. `adjust_numbers`의 Booking 부분을 이어서 구현하세요.
   - `mapped-booking` 중 `%tmp-TravelID`가 빈 줄(= 이번에 함께 만들어진 새 Travel의 Booking)은 `READ ENTITIES ... IN LOCAL MODE ENTITY Booking BY \_Travel ... LINK`로 부모의 `%pid`를 찾고, 3단계에서 정한 `mapped-travel`의 `TravelID`를 넣습니다.
   - 이미 있던 Travel에 추가된 Booking은 `%tmp-TravelID`를 그대로 씁니다.
   - Travel별 현재 최대 `booking_id`를 **한 번의 SELECT**(range + GROUP BY)로 읽고, Travel별로 10씩 늘려 `BookingID`를 매깁니다.
2. 루프 안에 SELECT를 두지 마세요(RAP110 원본은 GROUP 루프 안에서 SELECT MAX를 합니다. 이를 개선합니다).

**확인**
- 새 Travel에 Booking 세 건을 만들어 저장하면 Booking ID가 10, 20, 30이 됩니다.
- Booking이 30까지 있는 기존 Travel에 두 건을 더 만들고 저장하면 40, 50이 됩니다.

<details><summary>정답·해설</summary>

`adjust_numbers` 전체(Travel 부분 + Booking 부분):

```abap
  METHOD adjust_numbers.

    "======== Root entity: Travel =================================
    IF mapped-travel IS NOT INITIAL.

      DATA travel_id_max TYPE /dmo/travel_id.
      DATA number_ok     TYPE abap_bool.

      IF c_use_number_range = abap_true.
        TRY.
            cl_numberrange_runtime=>number_get(
              EXPORTING
                nr_range_nr       = '01'
                object            = 'ZRAP_NR_###'
                quantity          = CONV #( lines( mapped-travel ) )
              IMPORTING
                number            = DATA(number_range_key)
                returncode        = DATA(number_range_return_code)
                returned_quantity = DATA(number_range_returned_quantity) ).
            IF number_range_returned_quantity = lines( mapped-travel ).
              travel_id_max = number_range_key - number_range_returned_quantity.
              number_ok = abap_true.
            ENDIF.
          CATCH cx_number_ranges.
            number_ok = abap_false.
        ENDTRY.
      ENDIF.

      IF number_ok = abap_false.
        SELECT FROM zrap_atrav_### FIELDS MAX( travel_id ) INTO @travel_id_max.
      ENDIF.

      LOOP AT mapped-travel ASSIGNING FIELD-SYMBOL(<travel>).
        travel_id_max += 1.
        <travel>-TravelID = travel_id_max.
      ENDLOOP.
    ENDIF.

    "======== Child entity: Booking ===============================
    IF mapped-booking IS NOT INITIAL.

      "1) parent of bookings whose travel is new in this save: follow the link by %pid
      READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
        ENTITY Booking BY \_Travel
          FROM VALUE #( FOR booking IN mapped-booking WHERE ( %tmp-TravelID IS INITIAL )
                        ( %pid = booking-%pid
                          %key = booking-%tmp ) )
        LINK DATA(booking_to_travel_links).

      LOOP AT mapped-booking ASSIGNING FIELD-SYMBOL(<booking>).
        <booking>-TravelID =
          COND #( WHEN <booking>-%tmp-TravelID IS INITIAL
                  THEN mapped-travel[ %pid = booking_to_travel_links[ source-%pid = <booking>-%pid ]-target-%pid ]-TravelID
                  ELSE <booking>-%tmp-TravelID ).
      ENDLOOP.

      "2) current highest booking number per travel - ONE select for all travels
      DATA travel_range TYPE RANGE OF /dmo/travel_id.
      travel_range = VALUE #( FOR GROUPS travel_group OF b IN mapped-booking GROUP BY b-TravelID
                              ( sign = 'I' option = 'EQ' low = travel_group ) ).

      SELECT FROM zrap_abook_###
        FIELDS travel_id, MAX( booking_id ) AS max_booking_id
        WHERE travel_id IN @travel_range
        GROUP BY travel_id
        INTO TABLE @DATA(max_booking_ids).
      SORT max_booking_ids BY travel_id.

      "3) number the bookings per travel
      LOOP AT mapped-booking INTO DATA(mapped_booking) GROUP BY mapped_booking-TravelID INTO DATA(booking_group).
        READ TABLE max_booking_ids WITH KEY travel_id = booking_group BINARY SEARCH INTO DATA(max_line).
        DATA(max_booking_id) = COND /dmo/booking_id( WHEN sy-subrc = 0 THEN max_line-max_booking_id ELSE 0 ).
        LOOP AT GROUP booking_group ASSIGNING <booking>.
          max_booking_id += 10.
          <booking>-BookingID = max_booking_id.
        ENDLOOP.
      ENDLOOP.
    ENDIF.

  ENDMETHOD.
```

해설
- adjust_numbers 시점에 `%key`는 최종 키 자리이고, 인터랙션 단계에서 쓰던 임시 키 값은 `%tmp`로 옮겨져 있습니다. `%tmp-TravelID`가 비어 있으면 부모 Travel도 이번에 새로 만들어진 것입니다(late numbering이라 아직 번호가 없음).
- `READ ... BY \_Travel ... LINK`는 Booking 인스턴스(`%pid`)와 부모 인스턴스(`%pid`)의 연결만 돌려줍니다. 부모의 `%pid`로 `mapped-travel`을 찾아 방금 매긴 `TravelID`를 가져옵니다(RAP110 ex04와 같은 방식).
- 원본 RAP110은 `GROUP BY` 루프 안에서 Travel마다 `SELECT MAX`를 실행합니다. 여기서는 range 테이블로 한 번에 읽어 루프 안 SELECT를 없앴습니다.
- `FOR GROUPS ... GROUP BY`로 중복 없는 Travel ID 목록을 만듭니다. `COND /dmo/booking_id( ... ELSE 0 )`는 해당 Travel에 저장된 Booking이 없을 때 0부터 시작하게 합니다.
- draft로 만든 Booking의 draft 테이블 `ZRAP_DBOOK_###`에는 `PARENTDRAFTUUID`가 있어, 번호가 없는 동안에도 어느 draft Travel에 속하는지 알 수 있습니다.

</details>

#### 5단계. late numbering을 EML과 draft 테이블로 관찰하기

1. `ZCL_RAP_R04_SEQ_###`에 메서드 `show_late_numbering`을 추가하세요.
   - `/DMO/I_Flight`에서 오늘+10일 이후의 항공편 하나, `/DMO/I_Agency`, `/DMO/I_Customer`에서 각각 하나를 읽습니다.
   - Travel 1건(활성, `%cid = 'T1'`)과 그 Booking 2건(`CREATE BY \_Booking`, `%cid_ref = 'T1'`)을 한 번의 MODIFY로 만듭니다. Travel 기간은 항공편 날짜 −1일 ~ +1일.
   - `MAPPED`의 `%pid`와 `TravelID`(아직 비어 있음)를 출력합니다.
   - `COMMIT ENTITIES BEGIN RESPONSE OF ...` → `CONVERT KEY OF ... FROM ... TO ...`로 최종 Travel ID와 Booking 키를 얻어 출력 → `COMMIT ENTITIES END`.
2. 앱에서 새 Travel(draft)을 만들고 저장하지 않은 상태로 `ZRAP_DTRAV_###`, `ZRAP_DBOOK_###`를 Data Preview로 열어 `TRAVELID`, `DRAFTUUID`, `PARENTDRAFTUUID` 값을 확인하세요.

**확인**
- 콘솔: MODIFY 직후 TravelID가 비어 있고 `%pid`만 있으며, CONVERT KEY 뒤에는 최종 Travel ID와 Booking ID 10, 20이 출력됩니다.
- Data Preview: draft Travel의 `TRAVELID`는 초기값(00000000), `DRAFTUUID`는 값이 있습니다. draft Booking의 `PARENTDRAFTUUID`는 그 Travel의 `DRAFTUUID`와 같습니다.

<details><summary>정답·해설</summary>

`ZCL_RAP_R04_SEQ_###` 전체(1단계 메서드 포함):

```abap
CLASS zcl_rap_r04_seq_### DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_oo_adt_classrun.

  PRIVATE SECTION.
    METHODS show_early_save_failure
      IMPORTING out TYPE REF TO if_oo_adt_classrun_out.
    METHODS show_late_numbering
      IMPORTING out TYPE REF TO if_oo_adt_classrun_out.
ENDCLASS.


CLASS zcl_rap_r04_seq_### IMPLEMENTATION.

  METHOD if_oo_adt_classrun~main.
    show_early_save_failure( out ).
    show_late_numbering( out ).
  ENDMETHOD.


  METHOD show_early_save_failure.

    out->write( `--- early save failure ---` ).

    SELECT SINGLE FROM /dmo/i_agency FIELDS AgencyID INTO @DATA(agency_id).
    DATA(today) = cl_abap_context_info=>get_system_date( ).

    DO 2 TIMES.
      MODIFY ENTITIES OF zrap_r_travel_###
        ENTITY Travel
          CREATE FIELDS ( AgencyID CustomerID BeginDate EndDate CurrencyCode Description )
          WITH VALUE #( ( %cid         = 'T1'
                          %is_draft    = if_abap_behv=>mk-off
                          AgencyID     = agency_id
                          CustomerID   = '999999'
                          BeginDate    = today + 10
                          EndDate      = today + 20
                          CurrencyCode = 'EUR'
                          Description  = 'R-04 early save test' ) )
        MAPPED DATA(mapped)
        FAILED DATA(failed)
        REPORTED DATA(reported).

      out->write( |Interaction phase: failed lines = { lines( failed-travel ) }| ).

      IF sy-index = 1.
        COMMIT ENTITIES RESPONSE OF zrap_r_travel_###
          FAILED DATA(commit_failed)
          REPORTED DATA(commit_reported).
        out->write( |COMMIT ENTITIES: sy-subrc = { sy-subrc }| ).
      ELSE.
        COMMIT ENTITIES IN SIMULATION MODE RESPONSE OF zrap_r_travel_###
          FAILED commit_failed
          REPORTED commit_reported.
        out->write( |COMMIT ENTITIES IN SIMULATION MODE: sy-subrc = { sy-subrc }| ).
      ENDIF.

      out->write( |Early save: failed lines = { lines( commit_failed-travel ) }| ).
      LOOP AT commit_reported-travel INTO DATA(message) WHERE %msg IS BOUND.
        out->write( message-%msg->if_message~get_text( ) ).
      ENDLOOP.

      ROLLBACK ENTITIES.
    ENDDO.

  ENDMETHOD.


  METHOD show_late_numbering.

    out->write( `--- late numbering ---` ).

    DATA(today) = cl_abap_context_info=>get_system_date( ).
    DATA(min_date) = CONV d( today + 10 ).

    SELECT FROM /dmo/i_flight
      FIELDS AirlineID, ConnectionID, FlightDate, Price, CurrencyCode
      WHERE FlightDate > @min_date
      ORDER BY FlightDate, AirlineID, ConnectionID
      INTO TABLE @DATA(flights)
      UP TO 1 ROWS.
    SELECT SINGLE FROM /dmo/i_agency   FIELDS AgencyID   INTO @DATA(agency_id).
    SELECT SINGLE FROM /dmo/i_customer FIELDS CustomerID INTO @DATA(customer_id).
    IF flights IS INITIAL OR agency_id IS INITIAL OR customer_id IS INITIAL.
      out->write( `Demo data missing (/DMO flight data).` ).
      RETURN.
    ENDIF.
    DATA(flight) = flights[ 1 ].

    MODIFY ENTITIES OF zrap_r_travel_###
      ENTITY Travel
        CREATE FIELDS ( AgencyID CustomerID BeginDate EndDate CurrencyCode Description )
        WITH VALUE #( ( %cid         = 'T1'
                        %is_draft    = if_abap_behv=>mk-off
                        AgencyID     = agency_id
                        CustomerID   = customer_id
                        BeginDate    = flight-FlightDate - 1
                        EndDate      = flight-FlightDate + 1
                        CurrencyCode = flight-CurrencyCode
                        Description  = 'R-04 late numbering' ) )
        CREATE BY \_Booking
        FIELDS ( CustomerID CarrierID ConnectionID FlightDate FlightPrice CurrencyCode )
        WITH VALUE #( ( %cid_ref  = 'T1'
                        %is_draft = if_abap_behv=>mk-off
                        %target   = VALUE #( ( %cid         = 'B1'
                                               %is_draft    = if_abap_behv=>mk-off
                                               CustomerID   = customer_id
                                               CarrierID    = flight-AirlineID
                                               ConnectionID = flight-ConnectionID
                                               FlightDate   = flight-FlightDate
                                               FlightPrice  = flight-Price
                                               CurrencyCode = flight-CurrencyCode )
                                             ( %cid         = 'B2'
                                               %is_draft    = if_abap_behv=>mk-off
                                               CustomerID   = customer_id
                                               CarrierID    = flight-AirlineID
                                               ConnectionID = flight-ConnectionID
                                               FlightDate   = flight-FlightDate
                                               FlightPrice  = flight-Price
                                               CurrencyCode = flight-CurrencyCode ) ) ) )
      MAPPED DATA(mapped)
      FAILED DATA(failed)
      REPORTED DATA(reported).

    IF failed IS NOT INITIAL.
      out->write( `Create failed in the interaction phase.` ).
      ROLLBACK ENTITIES.
      RETURN.
    ENDIF.

    "before the save: only preliminary IDs
    LOOP AT mapped-travel INTO DATA(mapped_travel).
      out->write( |Before save: %cid { mapped_travel-%cid }, TravelID '{ mapped_travel-TravelID }', %pid filled: { xsdbool( mapped_travel-%pid IS NOT INITIAL ) }| ).
    ENDLOOP.

    "commit scope: convert the preliminary keys into the final keys
    COMMIT ENTITIES BEGIN RESPONSE OF zrap_r_travel_###
      FAILED DATA(commit_failed)
      REPORTED DATA(commit_reported).

    IF sy-subrc = 0.
      LOOP AT mapped-travel INTO mapped_travel.
        CONVERT KEY OF zrap_r_travel_### FROM mapped_travel-%pid TO DATA(travel_key).
        out->write( |After save: Travel %cid { mapped_travel-%cid } -> TravelID { travel_key-TravelID }| ).
      ENDLOOP.
      LOOP AT mapped-booking INTO DATA(mapped_booking).
        CONVERT KEY OF zrap_r_booking_### FROM mapped_booking-%pid TO DATA(booking_key).
        out->write( |After save: Booking %cid { mapped_booking-%cid } -> { booking_key-TravelID }/{ booking_key-BookingID }| ).
      ENDLOOP.
    ELSE.
      out->write( |Save failed: sy-subrc = { sy-subrc }| ).
      LOOP AT commit_reported-travel INTO DATA(message) WHERE %msg IS BOUND.
        out->write( message-%msg->if_message~get_text( ) ).
      ENDLOOP.
    ENDIF.

    COMMIT ENTITIES END.

  ENDMETHOD.

ENDCLASS.
```

해설
- late numbering BO에서 MODIFY 직후 `mapped`에는 최종 키가 없고 `%pid`(preliminary ID)가 들어 있습니다. 최종 키는 저장이 끝나야 생기므로, `COMMIT ENTITIES BEGIN ... END` 사이에서만 `CONVERT KEY`로 `%pid` → 최종 키를 얻을 수 있습니다(cheat sheet 08의 commit scope).
- `CONVERT KEY OF <엔터티> FROM <%pid> TO <키>`의 대상 키 타입은 엔터티의 키 구조입니다. 자식은 자식 엔터티 이름(`zrap_r_booking_###`)을 씁니다. 결과 구조의 컴포넌트 이름(`TravelID` 등)은 실제 시스템에서 F2로 확인하세요(실제 시스템에서 확인 필요).
- draft 테이블에서 late numbering BO의 키는 `TravelID`(아직 초기값) + `DRAFTUUID`입니다. 키 값이 아직 없는 draft도 `DRAFTUUID`로 구분되고, 자식은 `PARENTDRAFTUUID`로 부모 draft를 가리킵니다(RAP110 ex03이 draft 테이블 재생성을 요구하는 이유).
- 이 테스트는 실제로 데이터를 저장합니다. 필요하면 앱에서 지우세요.

자주 나는 오류
- 오늘이 일요일이고 R-03 스위치 `sunday_closed`가 켜져 있거나 `create_closed`가 켜져 있으면 CREATE가 인터랙션 단계에서 `cause-disabled`로 거절됩니다. 스위치를 끄고 실행하세요. `deny_country`가 대행사 국가와 같아도 precheck에서 거절됩니다.
- 기간 validation(R-02 006 시작일이 과거)에 걸리면 `min_date`를 더 뒤로 옮기세요. 항공편이 Travel 기간 밖이라는 메시지(R-02 014)는 경고라 저장을 막지 않습니다.

</details>

#### 6단계. 변경 로그 테이블 만들기

1. 데이터베이스 테이블 `ZRAP_TLOG_###`(설명 `Travel change log`)를 아래 필드로 만드세요. 한 줄은 "어느 인스턴스의 어느 필드가 어떤 값으로 바뀌었나" 하나입니다. 삭제는 필드 이름 `*`로 한 줄만 남깁니다.

| 필드 | 키 | 데이터 엘리먼트(또는 내장 타입) | 타입 | 길이 | 소수 | 설명 |
|---|---|---|---|---|---|---|
| client | X | abap.clnt | CLNT | 3 | 0 | 클라이언트 |
| log_uuid | X | sysuuid_x16 | RAW | 16 | 0 | 로그 줄 키 |
| travel_id |  | /dmo/travel_id | NUMC | 8 | 0 | Travel ID |
| booking_id |  | /dmo/booking_id | NUMC | 4 | 0 | Booking ID(Travel 줄이면 0) |
| entity_name |  | abap.char(10) | CHAR | 10 | 0 | `TRAVEL` / `BOOKING` |
| operation |  | abap.char(1) | CHAR | 1 | 0 | `C` 생성, `U` 변경, `D` 삭제 |
| field_name |  | abap.char(30) | CHAR | 30 | 0 | 바뀐 필드(CDS 요소 이름) |
| new_value |  | abap.char(100) | CHAR | 100 | 0 | 새 값(문자열로 변환) |
| changed_by |  | abp_creation_user | CHAR | 12 | 0 | 변경 사용자 |
| changed_at |  | abp_creation_tstmpl | DEC | 21 | 7 | 변경 시각 |

2. 세이버 클래스에서 쓸 내부 테이블 타입 `tt_log`(이 테이블의 표준 테이블)를 세이버 클래스 PRIVATE SECTION에 선언하세요.

**확인**
- 테이블이 활성화되고 Data Preview가 빈 표를 보여 줍니다.

<details><summary>정답·해설</summary>

```abap
@EndUserText.label : 'Travel change log'
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table zrap_tlog_### {
  key client   : abap.clnt not null;
  key log_uuid : sysuuid_x16 not null;
  travel_id    : /dmo/travel_id;
  booking_id   : /dmo/booking_id;
  entity_name  : abap.char(10);
  operation    : abap.char(1);
  field_name   : abap.char(30);
  new_value    : abap.char(100);
  changed_by   : abp_creation_user;
  changed_at   : abp_creation_tstmpl;
}
```

세이버 클래스 PRIVATE SECTION에 추가:

```abap
    TYPES tt_log TYPE STANDARD TABLE OF zrap_tlog_### WITH EMPTY KEY.
```

해설
- 키는 UUID 하나로 둡니다. 같은 필드가 한 번의 저장에서 여러 번 기록될 수 있어 업무 키로는 유일성이 보장되지 않기 때문입니다.
- 첨부 파일(`Attachment`, xstring)은 로그에 남기지 않습니다(7단계에서 제외).
- 실제 업무에서는 RAP의 변경 문서 기능(BDEF `changedocuments`, cheat sheet 36 참고)을 쓸 수 있습니다. 이 단계는 additional save의 원리를 익히기 위한 직접 구현입니다.

</details>

#### 7단계. `save_modified`에서 변경 필드만 로그 남기기

1. `save_modified`에서 `create`, `update`, `delete`의 Travel과 Booking 줄을 모두 로그로 바꿔 `ZRAP_TLOG_###`에 **한 번에** INSERT 하세요.
2. 공통 메서드 `add_log_lines`(PRIVATE)를 만드세요.
   - 입력: 엔터티 이름, 작업(C/U/D), `travel_id`, `booking_id`(선택), 인스턴스 한 줄(`TYPE any`, 선택)
   - 생성/변경: 인스턴스의 `%control` 구조를 RTTI(`cl_abap_structdescr`)로 훑어 `mk-on`인 필드만 한 줄씩 기록합니다. `Attachment`와 관리 필드(`CreatedBy`, `CreatedAt`, `LocalLastChangedBy`, `LocalLastChangedAt`, `LastChangedAt`)는 제외합니다.
   - 삭제: `field_name = '*'` 한 줄만
   - 사용자는 `cl_abap_context_info=>get_user_technical_name( )`, 시각은 `utclong_current( )`를 `cl_abap_tstmp=>utclong2tstmp`로 변환해 넣습니다.
3. 앱에서 Travel의 Description만 바꿔 저장하고, Booking 하나를 추가하고, 다른 Booking 하나를 지운 뒤 로그를 확인하세요.

**확인**
- Description만 바꾸면 `U / TRAVEL / DESCRIPTION` 한 줄(+ determination이 바꾼 필드가 있으면 그 필드)만 생깁니다.
- 새 Booking은 `C / BOOKING` 여러 줄, 지운 Booking은 `D / BOOKING / *` 한 줄입니다.
- draft에서 편집하는 동안(저장 전)에는 로그가 생기지 않습니다.

<details><summary>정답·해설</summary>

세이버 클래스 정의부(최종형, 8단계까지 그대로 씁니다):

```abap
CLASS lsc_zrap_r_travel_### DEFINITION INHERITING FROM cl_abap_behavior_saver.

  PROTECTED SECTION.

    CONSTANTS:
      BEGIN OF travel_status,
        open     TYPE c LENGTH 1 VALUE 'O', "Open
        accepted TYPE c LENGTH 1 VALUE 'A', "Accepted
        rejected TYPE c LENGTH 1 VALUE 'X', "Rejected
      END OF travel_status.

    "abap_false = always use the SELECT MAX fallback
    CONSTANTS c_use_number_range TYPE abap_bool VALUE abap_true.

    METHODS adjust_numbers REDEFINITION.
    METHODS save_modified REDEFINITION.
    METHODS cleanup_finalize REDEFINITION.

  PRIVATE SECTION.

    TYPES tt_log TYPE STANDARD TABLE OF zrap_tlog_### WITH EMPTY KEY.

    METHODS add_log_lines
      IMPORTING entity_name TYPE zrap_tlog_###-entity_name
                operation   TYPE zrap_tlog_###-operation
                travel_id   TYPE /dmo/travel_id
                booking_id  TYPE /dmo/booking_id OPTIONAL
                instance    TYPE any OPTIONAL
      CHANGING  log         TYPE tt_log.

ENDCLASS.
```

구현(`adjust_numbers`는 4단계 코드 그대로):

```abap
  METHOD save_modified.

    DATA log TYPE tt_log.

    "---- Travel ---------------------------------------------------
    LOOP AT create-travel INTO DATA(created_travel).
      add_log_lines( EXPORTING entity_name = 'TRAVEL'
                               operation   = 'C'
                               travel_id   = created_travel-TravelID
                               instance    = created_travel
                     CHANGING  log         = log ).
    ENDLOOP.

    LOOP AT update-travel INTO DATA(updated_travel).
      add_log_lines( EXPORTING entity_name = 'TRAVEL'
                               operation   = 'U'
                               travel_id   = updated_travel-TravelID
                               instance    = updated_travel
                     CHANGING  log         = log ).
    ENDLOOP.

    LOOP AT delete-travel INTO DATA(deleted_travel).
      add_log_lines( EXPORTING entity_name = 'TRAVEL'
                               operation   = 'D'
                               travel_id   = deleted_travel-TravelID
                     CHANGING  log         = log ).
    ENDLOOP.

    "---- Booking --------------------------------------------------
    LOOP AT create-booking INTO DATA(created_booking).
      add_log_lines( EXPORTING entity_name = 'BOOKING'
                               operation   = 'C'
                               travel_id   = created_booking-TravelID
                               booking_id  = created_booking-BookingID
                               instance    = created_booking
                     CHANGING  log         = log ).
    ENDLOOP.

    LOOP AT update-booking INTO DATA(updated_booking).
      add_log_lines( EXPORTING entity_name = 'BOOKING'
                               operation   = 'U'
                               travel_id   = updated_booking-TravelID
                               booking_id  = updated_booking-BookingID
                               instance    = updated_booking
                     CHANGING  log         = log ).
    ENDLOOP.

    LOOP AT delete-booking INTO DATA(deleted_booking).
      add_log_lines( EXPORTING entity_name = 'BOOKING'
                               operation   = 'D'
                               travel_id   = deleted_booking-TravelID
                               booking_id  = deleted_booking-BookingID
                     CHANGING  log         = log ).
    ENDLOOP.

    "late save: database changes are allowed here - one INSERT for all lines
    IF log IS NOT INITIAL.
      INSERT zrap_tlog_### FROM TABLE @log.
    ENDIF.

  ENDMETHOD.


  METHOD cleanup_finalize.
    "no own buffer in this BO - nothing to reset
  ENDMETHOD.


  METHOD add_log_lines.

    DATA(changed_by) = CONV abp_creation_user( cl_abap_context_info=>get_user_technical_name( ) ).
    DATA(changed_at) = cl_abap_tstmp=>utclong2tstmp( utclong_current( ) ).

    TRY.
        "delete (or no instance data): one line with '*'
        IF operation = 'D' OR instance IS NOT SUPPLIED.
          APPEND VALUE #( log_uuid    = cl_system_uuid=>create_uuid_x16_static( )
                          travel_id   = travel_id
                          booking_id  = booking_id
                          entity_name = entity_name
                          operation   = operation
                          field_name  = '*'
                          changed_by  = changed_by
                          changed_at  = changed_at ) TO log.
          RETURN.
        ENDIF.

        "create/update: walk through %control and log every field marked as changed
        ASSIGN COMPONENT '%CONTROL' OF STRUCTURE instance TO FIELD-SYMBOL(<control>).
        IF sy-subrc <> 0.
          RETURN.
        ENDIF.

        DATA(control_type) = CAST cl_abap_structdescr( cl_abap_typedescr=>describe_by_data( <control> ) ).

        LOOP AT control_type->components INTO DATA(component).

          ASSIGN COMPONENT component-name OF STRUCTURE <control> TO FIELD-SYMBOL(<flag>).
          IF sy-subrc <> 0 OR <flag> <> if_abap_behv=>mk-on.
            CONTINUE.
          ENDIF.

          "no binary content and no administrative fields
          IF component-name = 'ATTACHMENT'
          OR component-name = 'CREATEDBY'
          OR component-name = 'CREATEDAT'
          OR component-name = 'LOCALLASTCHANGEDBY'
          OR component-name = 'LOCALLASTCHANGEDAT'
          OR component-name = 'LASTCHANGEDAT'.
            CONTINUE.
          ENDIF.

          ASSIGN COMPONENT component-name OF STRUCTURE instance TO FIELD-SYMBOL(<value>).
          IF sy-subrc <> 0.
            CONTINUE.
          ENDIF.

          APPEND VALUE #( log_uuid    = cl_system_uuid=>create_uuid_x16_static( )
                          travel_id   = travel_id
                          booking_id  = booking_id
                          entity_name = entity_name
                          operation   = operation
                          field_name  = component-name
                          new_value   = |{ <value> }|
                          changed_by  = changed_by
                          changed_at  = changed_at ) TO log.
        ENDLOOP.

      CATCH cx_uuid_error.
        "late save must not fail: skip the log line instead of dumping
        RETURN.
    ENDTRY.

  ENDMETHOD.
```

해설
- `save_modified`는 managed framework가 persistent table에 쓴 **뒤**(같은 LUW 안)에 불립니다. 여기는 late save라 DB 변경이 허용됩니다. framework가 끝에 `COMMIT WORK`를 하므로 직접 커밋하면 안 됩니다.
- `with full data`라서 `update-travel` 줄에 모든 필드 값이 있지만, **어느 필드가 바뀌었는지**는 `%control`이 알려 줍니다. 그래서 `%control`의 컴포넌트를 RTTI로 훑으면 필드 목록을 하드코딩하지 않아도 됩니다. `%control`의 컴포넌트 이름은 CDS 요소 이름(대문자)입니다.
- create의 `%control`에는 소비자가 넘긴 필드와 determination이 채운 필드가 표시됩니다. 정확히 어떤 필드가 켜지는지는 실행해서 관찰해 보세요(실제 시스템에서 확인 필요).
- draft 편집 중 저장(draft 테이블 쓰기)은 framework가 처리하며 `save_modified`를 부르지 않습니다. 활성 데이터가 바뀌는 순간(Activate, 활성 인스턴스에 대한 액션·EML)에만 불립니다. 그래서 로그는 "확정된 변경"만 남습니다(실제 동작은 실제 시스템에서 확인 필요).
- Travel을 삭제하면 composition으로 Booking도 지워집니다. 이때 `delete-booking`에도 줄이 들어오는지 관찰해 보세요.
- UUID 생성 실패(`cx_uuid_error`)로 late save가 덤프되지 않도록 잡습니다. late save에서는 오류를 소비자에게 돌려줄 수 없습니다.

클래스 구조 해설
- `save_modified`의 `create`/`update`(타입 `REQUEST FOR CHANGE zrap_r_travel_###`)와 `delete`(`REQUEST FOR DELETE`)는 엔터티 별칭(`travel`, `booking`)을 컴포넌트로 가진 깊은 구조입니다. 이 시점에는 late numbering이 끝났으므로 `TravelID`, `BookingID`가 최종 값입니다.
- 호출 순서: `adjust_numbers` → (managed 저장) → `save_modified` → `cleanup`.

</details>

#### 8단계. 비즈니스 이벤트 정의하고 발생시키기

1. 이벤트 파라미터용 추상 엔터티 `ZRAP_A_TRAVEL_EVT_###`를 만드세요. 필드: `travel_id`, `agency_id`, `customer_id`, `overall_status`, `description`, `total_price`, `currency_code`, `begin_date`, `end_date`(모두 /DMO 데이터 엘리먼트).
2. BDEF Travel 본문에 이벤트 두 개를 정의하세요.
   - `travel_accepted`: 파라미터 `ZRAP_A_TRAVEL_EVT_###`
   - `travel_rejected`: 파라미터 없음(키만 전달)
3. `save_modified` 끝에서, `update-travel` 중 `%control-OverallStatus`가 켜져 있고 상태가 `A`인 줄은 `travel_accepted`, `X`인 줄은 `travel_rejected`로 `RAISE ENTITY EVENT` 하세요.
4. 다음 두 개념을 BDEF에 **주석으로만** 적어 두세요(활성화하지 않음).
   - 파생 이벤트(managed event): `travel_accepted`가 일어나면 자동으로 함께 발생하고, 파라미터만 다른 이벤트
   - side effects용 이벤트: 이벤트가 일어나면 UI의 특정 필드를 다시 읽게 하는 이벤트

**직접 추가할 어노테이션**
- `@EndUserText.label` — 추상 엔터티 설명
- `@Semantics.amount.currencyCode` — `total_price`가 `currency_code`를 따른다는 표시

**확인**
- 추상 엔터티, BDEF, 행동 풀이 활성화됩니다.
- 9단계 핸들러를 만들기 전에는 겉으로 보이는 변화가 없습니다. 디버거로 `save_modified`에 중단점을 두고 Accept Travel을 누르면 `RAISE ENTITY EVENT`에 도달합니다.

<details><summary>정답·해설</summary>

```cds
@EndUserText.label: 'Travel event parameter'                  // (→ 어노테이션 탭: @EndUserText.label)
define abstract entity ZRAP_A_TRAVEL_EVT_###
{
  travel_id      : /dmo/travel_id;
  agency_id      : /dmo/agency_id;
  customer_id    : /dmo/customer_id;
  overall_status : /dmo/overall_status;
  description    : /dmo/description;
  @Semantics.amount.currencyCode: 'currency_code'             // 금액-통화 연결 (→ 어노테이션 탭: @Semantics.amount.currencyCode)
  total_price    : /dmo/total_price;
  currency_code  : /dmo/currency_code;
  begin_date     : /dmo/begin_date;
  end_date       : /dmo/end_date;
}
```

BDEF Travel 본문(액션 아래 아무 곳):

```bdef
  // 비즈니스 이벤트
  event travel_accepted parameter ZRAP_A_TRAVEL_EVT_###;    // 파라미터(payload) 있는 이벤트
  event travel_rejected;                                    // 키만 전달

  // (개념) 파생 이벤트: travel_accepted가 발생하면 자동 발생, payload만 다름
  // managed event travel_accepted_short on travel_accepted parameter ZRAP_A_TRAVEL_EVT_SHORT_###;
  // (개념) side effects 전용 이벤트 + side effects 블록 안의 트리거
  // event travel_changed_remote for side effects;
  // side effects { event travel_changed_remote affects field OverallStatus; }
```

`save_modified` 끝(INSERT 로그 뒤)에 추가:

```abap
    "---- Business events (late save is the recommended place) -------
    IF update-travel IS NOT INITIAL.

      RAISE ENTITY EVENT zrap_r_travel_###~travel_accepted
        FROM VALUE #( FOR travel IN update-travel
                      WHERE ( %control-OverallStatus = if_abap_behv=>mk-on
                          AND OverallStatus          = travel_status-accepted )
                      ( %key   = travel-%key
                        %param = VALUE #( travel_id      = travel-TravelID
                                          agency_id      = travel-AgencyID
                                          customer_id    = travel-CustomerID
                                          overall_status = travel-OverallStatus
                                          description    = travel-Description
                                          total_price    = travel-TotalPrice
                                          currency_code  = travel-CurrencyCode
                                          begin_date     = travel-BeginDate
                                          end_date       = travel-EndDate ) ) ).

      RAISE ENTITY EVENT zrap_r_travel_###~travel_rejected
        FROM VALUE #( FOR travel IN update-travel
                      WHERE ( %control-OverallStatus = if_abap_behv=>mk-on
                          AND OverallStatus          = travel_status-rejected )
                      ( %key = travel-%key ) ).
    ENDIF.
```

해설
- 비즈니스 이벤트는 "무슨 일이 확정되었다"를 다른 곳에 **비동기로** 알리는 장치입니다. 확정은 저장이 끝나야 하므로 late save(`save`/`save_modified`)에서 발생시키는 것이 권장되며, 인터랙션·early save 단계에서는 `RAISE ENTITY EVENT`가 허용되지 않습니다(cheat sheet 08의 허용/금지 표). managed BO에 additional save를 붙이는 이유 중 하나가 바로 이것입니다.
- 파라미터는 추상 엔터티로 정의하고, 이벤트 표의 각 줄은 `%key` + `%param`으로 채웁니다. `with full data`이므로 `update-travel`에서 바로 값을 꺼낼 수 있습니다.
- RAP110 원본은 `%param =` 없이 파라미터 필드를 줄에 바로 적습니다. cheat sheet는 `%param = VALUE #( ... )`로 적습니다. 여기서는 구조가 드러나는 cheat sheet 방식을 썼습니다.
- `managed event ... on ...`(파생 이벤트)는 원래 이벤트가 발생할 때 framework가 자동으로 발생시키며, 다른 payload를 줄 수 있습니다. `event ... for side effects`는 RAP side effect를 일으키는 용도로만 씁니다(문법은 cheat sheet 36). 이 문제에서는 개념만 다룹니다.

</details>

#### 9단계. 로컬 이벤트 소비: 이벤트 핸들러 클래스

1. 이벤트 수신 로그 테이블 `ZRAP_EVLOG_###`를 만드세요.

| 필드 | 키 | 데이터 엘리먼트(또는 내장 타입) | 타입 | 길이 | 소수 | 설명 |
|---|---|---|---|---|---|---|
| client | X | abap.clnt | CLNT | 3 | 0 | 클라이언트 |
| event_uuid | X | sysuuid_x16 | RAW | 16 | 0 | 수신 줄 키 |
| travel_id |  | /dmo/travel_id | NUMC | 8 | 0 | Travel ID |
| event_name |  | abap.char(30) | CHAR | 30 | 0 | `TRAVEL_ACCEPTED` / `TRAVEL_REJECTED` |
| agency_id |  | /dmo/agency_id | NUMC | 6 | 0 | 대행사(accepted만) |
| customer_id |  | /dmo/customer_id | NUMC | 6 | 0 | 고객(accepted만) |
| total_price |  | /dmo/total_price | CURR | 16 | 2 | 총액, 참조 필드 `currency_code` |
| currency_code |  | /dmo/currency_code | CUKY | 5 | 0 | 통화 |
| received_at |  | abap.utclong | UTCL | – | – | 수신 시각 |

2. 전역 클래스 `ZCL_RAP_TRAV_EVT_###`를 "이 BO의 이벤트 핸들러 클래스"로 선언하세요(클래스 정의에 `FOR EVENTS OF`).
3. 그 클래스의 Local Types에 `lhe_travel`(`cl_abap_behavior_event_handler` 상속)을 만들고, `travel_accepted`, `travel_rejected`를 각각 받는 메서드를 구현하세요.
   - DB에 쓰기 전에 `cl_abap_tx=>save( )`로 save 단계를 엽니다.
   - 받은 이벤트 줄을 모두 모아 `ZRAP_EVLOG_###`에 한 번에 INSERT 합니다.
4. 원격 소비(Event Binding, SAP Event Mesh)는 개념으로 정리하세요.

**확인**
- 앱에서 Travel 하나를 Accept, 다른 하나를 Reject 한 뒤 몇 초 기다려 `ZRAP_EVLOG_###` Data Preview를 새로 고치면 두 줄이 보입니다. Accepted 줄에는 대행사·고객·총액이 채워져 있습니다.
- `ZRAP_TLOG_###`에도 `OVERALLSTATUS` 변경 줄이 함께 생깁니다.

<details><summary>정답·해설</summary>

```abap
@EndUserText.label : 'Travel event log'
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table zrap_evlog_### {
  key client     : abap.clnt not null;
  key event_uuid : sysuuid_x16 not null;
  travel_id      : /dmo/travel_id;
  event_name     : abap.char(30);
  agency_id      : /dmo/agency_id;
  customer_id    : /dmo/customer_id;
  @Semantics.amount.currencyCode : 'zrap_evlog_###.currency_code'
  total_price    : /dmo/total_price;
  currency_code  : /dmo/currency_code;
  received_at    : abap.utclong;
}
```

전역 클래스(Global Class 탭):

```abap
CLASS zcl_rap_trav_evt_### DEFINITION
  PUBLIC
  ABSTRACT
  FINAL
  FOR EVENTS OF zrap_r_travel_###.

  PUBLIC SECTION.
  PROTECTED SECTION.
  PRIVATE SECTION.
ENDCLASS.


CLASS zcl_rap_trav_evt_### IMPLEMENTATION.
ENDCLASS.
```

Local Types 탭:

```abap
CLASS lhe_travel DEFINITION INHERITING FROM cl_abap_behavior_event_handler.

  PRIVATE SECTION.

    TYPES tt_evlog TYPE STANDARD TABLE OF zrap_evlog_### WITH EMPTY KEY.

    METHODS on_travel_accepted FOR ENTITY EVENT
      accepted FOR Travel~travel_accepted.

    METHODS on_travel_rejected FOR ENTITY EVENT
      rejected FOR Travel~travel_rejected.

ENDCLASS.


CLASS lhe_travel IMPLEMENTATION.

  METHOD on_travel_accepted.

    "event handlers start in the MODIFY phase -> open the SAVE phase before DB changes
    cl_abap_tx=>save( ).

    DATA evlog TYPE tt_evlog.

    LOOP AT accepted INTO DATA(event).
      TRY.
          APPEND VALUE #( event_uuid    = cl_system_uuid=>create_uuid_x16_static( )
                          travel_id     = event-%key-TravelID
                          event_name    = 'TRAVEL_ACCEPTED'
                          agency_id     = event-%param-agency_id
                          customer_id   = event-%param-customer_id
                          total_price   = event-%param-total_price
                          currency_code = event-%param-currency_code
                          received_at   = utclong_current( ) ) TO evlog.
        CATCH cx_uuid_error.
          CONTINUE.
      ENDTRY.
    ENDLOOP.

    IF evlog IS NOT INITIAL.
      INSERT zrap_evlog_### FROM TABLE @evlog.
    ENDIF.

  ENDMETHOD.


  METHOD on_travel_rejected.

    cl_abap_tx=>save( ).

    DATA evlog TYPE tt_evlog.

    LOOP AT rejected INTO DATA(event).
      TRY.
          APPEND VALUE #( event_uuid  = cl_system_uuid=>create_uuid_x16_static( )
                          travel_id   = event-%key-TravelID
                          event_name  = 'TRAVEL_REJECTED'
                          received_at = utclong_current( ) ) TO evlog.
        CATCH cx_uuid_error.
          CONTINUE.
      ENDTRY.
    ENDLOOP.

    IF evlog IS NOT INITIAL.
      INSERT zrap_evlog_### FROM TABLE @evlog.
    ENDIF.

  ENDMETHOD.

ENDCLASS.
```

해설
- `FOR EVENTS OF <루트 엔터티>`가 붙은 전역 클래스가 **이벤트 핸들러 클래스 풀**입니다. 실제 처리는 Local Types의 `cl_abap_behavior_event_handler` 상속 클래스가 합니다(행동 풀이 `FOR BEHAVIOR OF` + 로컬 핸들러인 것과 같은 구조).
- 메서드 시그니처 `FOR ENTITY EVENT <파라미터> FOR <엔터티 별칭>~<이벤트>`에서 파라미터는 `TABLE FOR EVENT` 타입이며 `%key`와(파라미터가 있으면) `%param`을 가집니다. 응답 파라미터(failed, reported)는 없습니다.
- 한 이벤트는 한 핸들러 클래스 안에서 메서드 하나만 받을 수 있지만, 여러 핸들러 클래스가 같은 이벤트를 받을 수는 있습니다(RAP110 ex11 설명).
- 이벤트 핸들러는 저장이 끝난 뒤 **비동기로**, 별도 트랜잭션에서 `modify` 단계로 시작합니다. DB에 쓰려면 먼저 `cl_abap_tx=>save( )`로 save 단계를 열어야 합니다. 그렇지 않으면 controlled SAP LUW 위반으로 런타임 오류가 납니다(cheat sheet 17). 커밋은 framework가 하므로 `COMMIT WORK`를 쓰지 않습니다.
- **원격 소비**: 다른 시스템이 받게 하려면 ADT에서 **Event Binding**(이벤트 바인딩) 객체를 만들어 BDEF 이벤트(엔터티 + 이벤트 이름)를 외부 이벤트 유형(네임스페이스, 비즈니스 객체, 작업, 버전)에 연결하고, SAP Event Mesh 등과의 통신 약정을 구성해야 합니다. RAP110 핸즈온에서는 SAP 팀이 Event Mesh 연결을 미리 구성해 두었습니다. 트라이얼에서 이 구성을 직접 할 수 있는지는 확인하지 못했습니다(실제 시스템에서 확인 필요). 로컬 소비는 이벤트 바인딩 없이도 동작합니다(RAP110 ex11이 로컬 소비만 구현).

클래스 구조 해설
- `accepted`, `rejected`라는 이름은 메서드 선언에서 정한 import 파라미터 이름입니다. 타입은 BDEF의 `event travel_accepted parameter ...` 줄에서 생깁니다.
- 호출 시점: 원래 트랜잭션의 COMMIT이 성공한 뒤. 원래 트랜잭션이 롤백되면 호출되지 않습니다.

</details>

#### 10단계. 변형: `with unmanaged save`로 저장 직접 구현하기

managed BO의 기본 저장을 끄고 저장을 직접 하는 방식을 **실험**합니다. 끝나면 7~8단계 상태(additional save)로 되돌리세요. 시작 전에 BDEF와 행동 풀 Local Types 전체를 메모장에 복사해 두세요.

1. BDEF 머리를 "기본 저장 대신 내 저장(unmanaged save), 정리 단계(cleanup) 구현 포함, 전체 데이터 전달"로 바꾸세요.
2. Travel과 Booking 정의에서 `persistent table` 줄을 지우세요. `mapping for` 블록은 남깁니다.
3. `save_modified`에서 `ZRAP_ATRAV_###`, `ZRAP_ABOOK_###`에 직접 INSERT/UPDATE/DELETE 하세요.
   - create: `MAPPING FROM ENTITY`로 CDS 요소 이름 → DB 필드 이름 변환
   - update: 바뀐 필드만 쓰도록 `INDICATORS SET STRUCTURE %control`
   - delete: Travel 삭제 시 그 Travel의 Booking도 함께 삭제
   - 7~8단계의 로그·이벤트도 그대로 유지
4. `cleanup` 메서드를 재정의하세요(이 BO에는 비울 자체 버퍼가 없으므로 주석으로 역할만 설명).
5. 앱에서 생성·수정·삭제를 해 보고 DB와 로그를 확인한 뒤, 백업으로 되돌리세요.

**확인**
- unmanaged save 상태에서도 생성·수정·삭제 결과가 `ZRAP_ATRAV_###`/`ZRAP_ABOOK_###`에 그대로 반영됩니다.
- `save_modified`의 UPDATE 문을 주석 처리해 보면, 앱에서는 저장 성공으로 보이지만 DB가 바뀌지 않습니다(= 저장 책임이 완전히 내 코드로 넘어왔다는 증거). 확인 후 주석을 푸세요.

<details><summary>정답·해설</summary>

BDEF 머리와 엔터티 머리(본문은 R-03 10단계 + 8단계 이벤트 그대로):

```bdef
managed with unmanaged save and cleanup with full data
implementation in class zbp_rap_r_travel_### unique;      // 기본 저장 대신 save_modified, cleanup 재정의 필요
strict ( 2 );
with draft;
with privileged mode disabling NoCheckWhenPrivileged;
define authorization context NoCheckWhenPrivileged { '/DMO/TRVL'; }
define own authorization context by privileged mode;

define behavior for ZRAP_R_TRAVEL_### alias Travel
// persistent table zrap_atrav_###          <- unmanaged save: must be removed
draft table zrap_dtrav_### query ZRAP_R_TRAVELDRAFT_###
etag master LocalLastChangedAt
lock master total etag LastChangedAt
authorization master ( global, instance )
late numbering

define behavior for ZRAP_R_BOOKING_### alias Booking
implementation in class zbp_rap_r_booking_### unique
// persistent table zrap_abook_###          <- removed as well
draft table zrap_dbook_###
etag master LocalLastChangedAt
lock dependent by _Travel
authorization dependent by _Travel
late numbering
```

세이버 클래스 전체(unmanaged save 변형):

```abap
CLASS lsc_zrap_r_travel_### DEFINITION INHERITING FROM cl_abap_behavior_saver.

  PROTECTED SECTION.

    CONSTANTS:
      BEGIN OF travel_status,
        open     TYPE c LENGTH 1 VALUE 'O', "Open
        accepted TYPE c LENGTH 1 VALUE 'A', "Accepted
        rejected TYPE c LENGTH 1 VALUE 'X', "Rejected
      END OF travel_status.

    CONSTANTS c_use_number_range TYPE abap_bool VALUE abap_true.

    METHODS adjust_numbers REDEFINITION.
    METHODS save_modified REDEFINITION.
    METHODS cleanup REDEFINITION.
    METHODS cleanup_finalize REDEFINITION.

  PRIVATE SECTION.

    TYPES tt_log TYPE STANDARD TABLE OF zrap_tlog_### WITH EMPTY KEY.

    METHODS write_travel_data
      IMPORTING create TYPE REQUEST FOR CHANGE zrap_r_travel_###
                update TYPE REQUEST FOR CHANGE zrap_r_travel_###
                delete TYPE REQUEST FOR DELETE zrap_r_travel_###.

    METHODS add_log_lines
      IMPORTING entity_name TYPE zrap_tlog_###-entity_name
                operation   TYPE zrap_tlog_###-operation
                travel_id   TYPE /dmo/travel_id
                booking_id  TYPE /dmo/booking_id OPTIONAL
                instance    TYPE any OPTIONAL
      CHANGING  log         TYPE tt_log.

ENDCLASS.


CLASS lsc_zrap_r_travel_### IMPLEMENTATION.

  METHOD adjust_numbers.

    "======== Root entity: Travel =================================
    IF mapped-travel IS NOT INITIAL.

      DATA travel_id_max TYPE /dmo/travel_id.
      DATA number_ok     TYPE abap_bool.

      IF c_use_number_range = abap_true.
        TRY.
            cl_numberrange_runtime=>number_get(
              EXPORTING
                nr_range_nr       = '01'
                object            = 'ZRAP_NR_###'
                quantity          = CONV #( lines( mapped-travel ) )
              IMPORTING
                number            = DATA(number_range_key)
                returncode        = DATA(number_range_return_code)
                returned_quantity = DATA(number_range_returned_quantity) ).
            IF number_range_returned_quantity = lines( mapped-travel ).
              travel_id_max = number_range_key - number_range_returned_quantity.
              number_ok = abap_true.
            ENDIF.
          CATCH cx_number_ranges.
            number_ok = abap_false.
        ENDTRY.
      ENDIF.

      IF number_ok = abap_false.
        SELECT FROM zrap_atrav_### FIELDS MAX( travel_id ) INTO @travel_id_max.
      ENDIF.

      LOOP AT mapped-travel ASSIGNING FIELD-SYMBOL(<travel>).
        travel_id_max += 1.
        <travel>-TravelID = travel_id_max.
      ENDLOOP.
    ENDIF.

    "======== Child entity: Booking ===============================
    IF mapped-booking IS NOT INITIAL.

      READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
        ENTITY Booking BY \_Travel
          FROM VALUE #( FOR booking IN mapped-booking WHERE ( %tmp-TravelID IS INITIAL )
                        ( %pid = booking-%pid
                          %key = booking-%tmp ) )
        LINK DATA(booking_to_travel_links).

      LOOP AT mapped-booking ASSIGNING FIELD-SYMBOL(<booking>).
        <booking>-TravelID =
          COND #( WHEN <booking>-%tmp-TravelID IS INITIAL
                  THEN mapped-travel[ %pid = booking_to_travel_links[ source-%pid = <booking>-%pid ]-target-%pid ]-TravelID
                  ELSE <booking>-%tmp-TravelID ).
      ENDLOOP.

      DATA travel_range TYPE RANGE OF /dmo/travel_id.
      travel_range = VALUE #( FOR GROUPS travel_group OF b IN mapped-booking GROUP BY b-TravelID
                              ( sign = 'I' option = 'EQ' low = travel_group ) ).

      SELECT FROM zrap_abook_###
        FIELDS travel_id, MAX( booking_id ) AS max_booking_id
        WHERE travel_id IN @travel_range
        GROUP BY travel_id
        INTO TABLE @DATA(max_booking_ids).
      SORT max_booking_ids BY travel_id.

      LOOP AT mapped-booking INTO DATA(mapped_booking) GROUP BY mapped_booking-TravelID INTO DATA(booking_group).
        READ TABLE max_booking_ids WITH KEY travel_id = booking_group BINARY SEARCH INTO DATA(max_line).
        DATA(max_booking_id) = COND /dmo/booking_id( WHEN sy-subrc = 0 THEN max_line-max_booking_id ELSE 0 ).
        LOOP AT GROUP booking_group ASSIGNING <booking>.
          max_booking_id += 10.
          <booking>-BookingID = max_booking_id.
        ENDLOOP.
      ENDLOOP.
    ENDIF.

  ENDMETHOD.


  METHOD save_modified.

    "1) own persistence (replaces the managed save)
    write_travel_data( create = create
                       update = update
                       delete = delete ).

    "2) change log (same as step 7)
    DATA log TYPE tt_log.

    LOOP AT create-travel INTO DATA(created_travel).
      add_log_lines( EXPORTING entity_name = 'TRAVEL' operation = 'C'
                               travel_id   = created_travel-TravelID
                               instance    = created_travel
                     CHANGING  log         = log ).
    ENDLOOP.
    LOOP AT update-travel INTO DATA(updated_travel).
      add_log_lines( EXPORTING entity_name = 'TRAVEL' operation = 'U'
                               travel_id   = updated_travel-TravelID
                               instance    = updated_travel
                     CHANGING  log         = log ).
    ENDLOOP.
    LOOP AT delete-travel INTO DATA(deleted_travel).
      add_log_lines( EXPORTING entity_name = 'TRAVEL' operation = 'D'
                               travel_id   = deleted_travel-TravelID
                     CHANGING  log         = log ).
    ENDLOOP.
    LOOP AT create-booking INTO DATA(created_booking).
      add_log_lines( EXPORTING entity_name = 'BOOKING' operation = 'C'
                               travel_id   = created_booking-TravelID
                               booking_id  = created_booking-BookingID
                               instance    = created_booking
                     CHANGING  log         = log ).
    ENDLOOP.
    LOOP AT update-booking INTO DATA(updated_booking).
      add_log_lines( EXPORTING entity_name = 'BOOKING' operation = 'U'
                               travel_id   = updated_booking-TravelID
                               booking_id  = updated_booking-BookingID
                               instance    = updated_booking
                     CHANGING  log         = log ).
    ENDLOOP.
    LOOP AT delete-booking INTO DATA(deleted_booking).
      add_log_lines( EXPORTING entity_name = 'BOOKING' operation = 'D'
                               travel_id   = deleted_booking-TravelID
                               booking_id  = deleted_booking-BookingID
                     CHANGING  log         = log ).
    ENDLOOP.
    IF log IS NOT INITIAL.
      INSERT zrap_tlog_### FROM TABLE @log.
    ENDIF.

    "3) business events (same as step 8)
    IF update-travel IS NOT INITIAL.
      RAISE ENTITY EVENT zrap_r_travel_###~travel_accepted
        FROM VALUE #( FOR travel IN update-travel
                      WHERE ( %control-OverallStatus = if_abap_behv=>mk-on
                          AND OverallStatus          = travel_status-accepted )
                      ( %key   = travel-%key
                        %param = VALUE #( travel_id      = travel-TravelID
                                          agency_id      = travel-AgencyID
                                          customer_id    = travel-CustomerID
                                          overall_status = travel-OverallStatus
                                          description    = travel-Description
                                          total_price    = travel-TotalPrice
                                          currency_code  = travel-CurrencyCode
                                          begin_date     = travel-BeginDate
                                          end_date       = travel-EndDate ) ) ).

      RAISE ENTITY EVENT zrap_r_travel_###~travel_rejected
        FROM VALUE #( FOR travel IN update-travel
                      WHERE ( %control-OverallStatus = if_abap_behv=>mk-on
                          AND OverallStatus          = travel_status-rejected )
                      ( %key = travel-%key ) ).
    ENDIF.

  ENDMETHOD.


  METHOD write_travel_data.

    "---- Travel ---------------------------------------------------
    IF create-travel IS NOT INITIAL.
      "CDS element names -> table field names via the BDEF 'mapping for'
      INSERT zrap_atrav_### FROM TABLE @create-travel MAPPING FROM ENTITY.
    ENDIF.

    IF update-travel IS NOT INITIAL.
      "only columns whose %control flag is set are written
      UPDATE zrap_atrav_### FROM TABLE @update-travel
        INDICATORS SET STRUCTURE %control MAPPING FROM ENTITY.
    ENDIF.

    IF delete-travel IS NOT INITIAL.
      DELETE zrap_atrav_### FROM TABLE @delete-travel MAPPING FROM ENTITY.

      "bookings of deleted travels (composition) - one statement
      DATA deleted_travels TYPE RANGE OF /dmo/travel_id.
      deleted_travels = VALUE #( FOR t IN delete-travel ( sign = 'I' option = 'EQ' low = t-TravelID ) ).
      DELETE FROM zrap_abook_### WHERE travel_id IN @deleted_travels.
    ENDIF.

    "---- Booking --------------------------------------------------
    IF create-booking IS NOT INITIAL.
      INSERT zrap_abook_### FROM TABLE @create-booking MAPPING FROM ENTITY.
    ENDIF.

    IF update-booking IS NOT INITIAL.
      UPDATE zrap_abook_### FROM TABLE @update-booking
        INDICATORS SET STRUCTURE %control MAPPING FROM ENTITY.
    ENDIF.

    IF delete-booking IS NOT INITIAL.
      DELETE zrap_abook_### FROM TABLE @delete-booking MAPPING FROM ENTITY.
    ENDIF.

  ENDMETHOD.


  METHOD cleanup.
    "Called after the save (and on ROLLBACK ENTITIES).
    "A BO with its own buffer (e.g. collected e-mails, legacy API buffer)
    "would clear that buffer here. This BO keeps no own buffer.
  ENDMETHOD.


  METHOD cleanup_finalize.
    "no own buffer in this BO - nothing to reset
  ENDMETHOD.


  METHOD add_log_lines.

    DATA(changed_by) = CONV abp_creation_user( cl_abap_context_info=>get_user_technical_name( ) ).
    DATA(changed_at) = cl_abap_tstmp=>utclong2tstmp( utclong_current( ) ).

    TRY.
        IF operation = 'D' OR instance IS NOT SUPPLIED.
          APPEND VALUE #( log_uuid    = cl_system_uuid=>create_uuid_x16_static( )
                          travel_id   = travel_id
                          booking_id  = booking_id
                          entity_name = entity_name
                          operation   = operation
                          field_name  = '*'
                          changed_by  = changed_by
                          changed_at  = changed_at ) TO log.
          RETURN.
        ENDIF.

        ASSIGN COMPONENT '%CONTROL' OF STRUCTURE instance TO FIELD-SYMBOL(<control>).
        IF sy-subrc <> 0.
          RETURN.
        ENDIF.

        DATA(control_type) = CAST cl_abap_structdescr( cl_abap_typedescr=>describe_by_data( <control> ) ).

        LOOP AT control_type->components INTO DATA(component).
          ASSIGN COMPONENT component-name OF STRUCTURE <control> TO FIELD-SYMBOL(<flag>).
          IF sy-subrc <> 0 OR <flag> <> if_abap_behv=>mk-on.
            CONTINUE.
          ENDIF.
          IF component-name = 'ATTACHMENT'
          OR component-name = 'CREATEDBY'
          OR component-name = 'CREATEDAT'
          OR component-name = 'LOCALLASTCHANGEDBY'
          OR component-name = 'LOCALLASTCHANGEDAT'
          OR component-name = 'LASTCHANGEDAT'.
            CONTINUE.
          ENDIF.
          ASSIGN COMPONENT component-name OF STRUCTURE instance TO FIELD-SYMBOL(<value>).
          IF sy-subrc <> 0.
            CONTINUE.
          ENDIF.
          APPEND VALUE #( log_uuid    = cl_system_uuid=>create_uuid_x16_static( )
                          travel_id   = travel_id
                          booking_id  = booking_id
                          entity_name = entity_name
                          operation   = operation
                          field_name  = component-name
                          new_value   = |{ <value> }|
                          changed_by  = changed_by
                          changed_at  = changed_at ) TO log.
        ENDLOOP.

      CATCH cx_uuid_error.
        RETURN.
    ENDTRY.

  ENDMETHOD.

ENDCLASS.
```

additional save와 unmanaged save 비교

| 구분 | `with additional save` | `with unmanaged save` |
|---|---|---|
| persistent table | 그대로 둠, framework가 저장 | **지워야 함**, 저장은 내 코드 |
| `save_modified`의 역할 | 저장 **뒤에** 추가 작업(로그, 이벤트, 외부 알림) | 저장 **그 자체** + 추가 작업 |
| 맞는 경우 | 테이블이 BO 구조와 1:1, 부가 작업만 필요 | 저장 대상이 BO 구조와 다름(여러 테이블로 쪼개기, 기존 업데이트 API·레거시 저장 로직 재사용, CDS 테이블 엔터티 외 저장소) |
| 위험 | 적음 | 저장 누락·필드 매핑 실수를 framework가 막아 주지 않음 |
| draft | framework | framework(draft 테이블은 그대로 관리됨) |

해설
- `with unmanaged save`에서는 managed의 인터랙션 단계(버퍼, 잠금, ETag, determination/validation, draft)는 그대로 framework가 하고, **마지막 DB 쓰기만** 내가 합니다. 완전한 unmanaged BO(R-05~R-07)와 달리 버퍼를 직접 만들 필요가 없습니다.
- `persistent table`을 지워야 하는 이유: 그 줄은 "framework가 이 테이블에 저장한다"는 선언이라 unmanaged save와 모순되기 때문입니다(cheat sheet 36: "you cannot specify the persistent table in this case"). 참조 시나리오의 carrier singleton(`/DMO/I_CarriersLockSingleton_S`)이 `with unmanaged save` + persistent table 없음의 예입니다.
- `mapping for`는 남겨야 `MAPPING FROM ENTITY`가 CDS 요소 이름(`TravelID`)을 테이블 필드(`travel_id`)로 바꿔 줍니다. `INDICATORS SET STRUCTURE %control`은 `%control`이 켜진 열만 UPDATE 합니다(cheat sheet 08). cheat sheet 예제는 한 줄(`FROM @structure`)에 대한 것이며, `FROM TABLE @...`과 함께 쓰는 형태는 실제 시스템에서 확인하세요. 안 되면 `LOOP AT ... INTO`로 한 줄씩 같은 문장을 실행하면 됩니다(실제 시스템에서 확인 필요).
- 머리 문법 `managed with unmanaged save and cleanup with full data`에서 `and cleanup`과 `with full data`의 순서는 cheat sheet에 "함께 쓸 수 있다"고만 되어 있어 확인하지 못했습니다. 활성화 오류가 나면 순서를 바꿔 보세요(실제 시스템에서 확인 필요). `and cleanup`을 쓰면 `cleanup` 재정의가 필요합니다.
- persistent table이 없을 때 framework가 활성 데이터를 어디서 읽는지(CDS 뷰를 통해 읽는 것으로 보임)는 실제 시스템에서 확인하세요(실제 시스템에서 확인 필요).
- 실험이 끝나면 BDEF 머리를 `managed with additional save with full data`로, `persistent table` 두 줄을 복구하고, 세이버 클래스를 7~8단계 형태(= 위 코드에서 `write_travel_data` 호출·메서드와 `cleanup` 재정의를 뺀 것)로 되돌리세요. R-11, R-12는 additional save 상태를 전제로 합니다.

클래스 구조 해설
- `write_travel_data`의 파라미터 타입 `REQUEST FOR CHANGE zrap_r_travel_###`/`REQUEST FOR DELETE zrap_r_travel_###`는 `save_modified`의 파라미터와 같은 BDEF 파생 타입이라 그대로 넘길 수 있습니다(cheat sheet 08 BDEF 파생 타입 표).
- 호출 순서(unmanaged save): `adjust_numbers` → `save_modified`(내 저장) → `cleanup`. `cleanup`은 `ROLLBACK ENTITIES` 때도 불립니다.

</details>

## 출처
- SAP-samples/abap-cheat-sheets
  - https://github.com/SAP-samples/abap-cheat-sheets/blob/main/36_RAP_Behavior_Definition_Language.md
  - https://github.com/SAP-samples/abap-cheat-sheets/blob/main/08_EML_ABAP_for_RAP.md
  - https://github.com/SAP-samples/abap-cheat-sheets/blob/main/25_Authorization_Checks.md
  - https://github.com/SAP-samples/abap-cheat-sheets/blob/main/17_SAP_LUW.md
  - https://github.com/SAP-samples/abap-cheat-sheets/blob/main/src/zdemo_abap_rap_ro_m_as.bdef.asbdef
  - https://github.com/SAP-samples/abap-cheat-sheets/blob/main/src/zbp_demo_abap_rap_ro_m_as.clas.locals_imp.abap
  - https://github.com/SAP-samples/abap-cheat-sheets/blob/main/src/zcl_demo_abap_rap_evt_handler.clas.abap
  - https://github.com/SAP-samples/abap-cheat-sheets/blob/main/src/zcl_demo_abap_rap_evt_handler.clas.locals_imp.abap
- SAP-samples/abap-platform-refscen-flight (ABAP-platform-cloud 브랜치)
  - https://github.com/SAP-samples/abap-platform-refscen-flight/blob/ABAP-platform-cloud/src/draft/%23dmo%23r_travel_d.bdef.asbdef
  - https://github.com/SAP-samples/abap-platform-refscen-flight/blob/ABAP-platform-cloud/src/draft/%23dmo%23bp_travel_d.clas.locals_imp.abap
  - https://github.com/SAP-samples/abap-platform-refscen-flight/blob/ABAP-platform-cloud/src/draft/%23dmo%23i_travel_d.bdef.asbdef
  - https://github.com/SAP-samples/abap-platform-refscen-flight/blob/ABAP-platform-cloud/src/draft/%23dmo%23i_travel_d.ddls.asddls
  - https://github.com/SAP-samples/abap-platform-refscen-flight/blob/ABAP-platform-cloud/src/draft/%23dmo%23c_travel_a_d.bdef.asbdef
  - https://github.com/SAP-samples/abap-platform-refscen-flight/blob/ABAP-platform-cloud/src/draft/%23dmo%23ui_travel_d_d_o4.srvb.xml
  - https://github.com/SAP-samples/abap-platform-refscen-flight/blob/ABAP-platform-cloud/src/colldraft/%23dmo%23r_traveltp_cd.bdef.asbdef
  - https://github.com/SAP-samples/abap-platform-refscen-flight/blob/ABAP-platform-cloud/src/colldraft/%23dmo%23r_traveldraft_cd.ddls.asddls
  - https://github.com/SAP-samples/abap-platform-refscen-flight/blob/ABAP-platform-cloud/src/colldraft/%23dmo%23r_traveldraft_cd.dcls.asdcls
  - https://github.com/SAP-samples/abap-platform-refscen-flight/blob/ABAP-platform-cloud/src/colldraft/%23dmo%23r_traveltp_cd.dcls.asdcls
  - https://github.com/SAP-samples/abap-platform-refscen-flight/blob/ABAP-platform-cloud/src/colldraft/%23dmo%23c_traveltp_cd.dcls.asdcls
  - https://github.com/SAP-samples/abap-platform-refscen-flight/blob/ABAP-platform-cloud/src/xbo/%23dmo%23r_traveldraft_xbo.dcls.asdcls
  - https://github.com/SAP-samples/abap-platform-refscen-flight/blob/ABAP-platform-cloud/src/reuse/carrier/%23dmo%23i_carrierslocksingleton_s.bdef.asbdef
  - https://github.com/SAP-samples/abap-platform-refscen-flight/blob/ABAP-platform-cloud/src/reuse/carrier/%23dmo%23bp_i_carrierslocksingle_s.clas.locals_imp.abap
  - https://github.com/SAP-samples/abap-platform-refscen-flight/blob/ABAP-platform-cloud/src/reuse/agency/%23dmo%23i_agencytp.bdef.asbdef
- SAP-samples/abap-platform-rap110
  - https://github.com/SAP-samples/abap-platform-rap110/blob/main/src/zrap110_r_traveltp_sol.bdef.asbdef
  - https://github.com/SAP-samples/abap-platform-rap110/blob/main/src/zrap110_c_traveltp_sol.bdef.asbdef
  - https://github.com/SAP-samples/abap-platform-rap110/blob/main/src/zrap110_bp_traveltp_sol.clas.locals_imp.abap
  - https://github.com/SAP-samples/abap-platform-rap110/blob/main/src/zrap110_travel_event_handl_sol.clas.abap
  - https://github.com/SAP-samples/abap-platform-rap110/blob/main/src/zrap110_travel_event_handl_sol.clas.locals_imp.abap
  - https://github.com/SAP-samples/abap-platform-rap110/blob/main/src/zrap110_a_travel_sol.ddls.asddls
  - https://github.com/SAP-samples/abap-platform-rap110/blob/main/src/zrap110sol.nrob.xml
  - https://github.com/SAP-samples/abap-platform-rap110/blob/main/exercises/ex03/README.md
  - https://github.com/SAP-samples/abap-platform-rap110/blob/main/exercises/ex04/README.md
  - https://github.com/SAP-samples/abap-platform-rap110/blob/main/exercises/ex11/README.md
- SAP-samples/abap-platform-rap-opensap
  - https://github.com/SAP-samples/abap-platform-rap-opensap/blob/main/week2/unit7.md
  - https://github.com/SAP-samples/abap-platform-rap-opensap/blob/main/week2/sources/W2U7_DCLS_ZI_RAP_TRAVEL.txt
  - https://github.com/SAP-samples/abap-platform-rap-opensap/blob/main/week2/sources/W2U7_DCLS_ZI_RAP_TRAVEL_Adjusted.txt
  - https://github.com/SAP-samples/abap-platform-rap-opensap/blob/main/week3/sources/W3U6_CLAS_ZCM_RAP.txt
