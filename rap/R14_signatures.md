## 5. 고급·특수 기능 보충

### R-14. BDEF 고급 문법: deep 파라미터·selective 결과·key function·save action·필드 특성 전부 [작성] ★★★
<!-- covers: abstract BDEF, abstract;, with hierarchy, with hierarchy like entity, with control, mandatory : execute (field), mandatory : execute (association), root abstract entity, composition in abstract entity, association to parent without ON, deep parameter, deep table parameter, deep result, deep result selective, %param 계층 타입, %param-%control, FIELDS ( ... ) WITH deep parameter, result selective, REQUEST requested_fields, result [0..1], result [0..*], result entity, external 'Name', static action, static function, factory action [0..*], factory action [1..*], static factory action multiplicity, instance factory action, save ( finalize ) action, save ( adjustnumbers ) action, saver finalize, cleanup_finalize, with additional save, determine action, determination ( always ), validation on save { delete; }, determination on save { delete; }, field ( notrigger ), notrigger : warn, field ( suppress ), internal create (association), internal update, internal action, IN LOCAL MODE, BDEF alternative key, BDEF pure key, BDEF secondary key, RAP key function, mapping for corresponding, mapping for control, CORRESPONDING MAPPING FROM ENTITY, USING CONTROL, MAPPING TO ENTITY, type mapping constant, projection BDEF use action/use function, OData $metadata external name -->
**목표**

- 추상 BDEF(`abstract;` + `with hierarchy` + `with control` + `mandatory : execute`)로 **계층형(deep) 파라미터와 결과 타입**을 만들고, 액션·함수에서 `deep parameter`, `deep table parameter`, `deep result`를 받아 처리할 수 있습니다. 깊은 파라미터 안의 `%control`을 읽어 "보낸 필드만" 반영할 수 있습니다.
- 결과 선언의 모든 변형(`result selective`, `[0..1]`, `[0..*]`, `result entity 다른엔터티`)과 외부 이름(`external 'Name'`), 정적 액션, 다중 결과 팩토리 액션(`[0..*]`, `[1..*]`)을 구현할 수 있습니다.
- 저장 시퀀스 전용 **save action**(`save ( finalize )`, `save ( adjustnumbers )`)을 정의하고 세이버의 `finalize`에서 EML로 실행할 수 있습니다.
- `on save { delete; }` 검증·결정, `determination ( always )`가 들어간 determine action, `field ( notrigger )`/`notrigger : warn`, `field ( suppress )`, `internal create`/`internal update`를 쓰고, 왜 `IN LOCAL MODE`가 필요한지 설명할 수 있습니다.
- BDEF 대체 키(alternative key: pure key / secondary key)와 RAP key function의 의미를 알고, 확인된 문법만으로 같은 일을 하는 정적 함수도 만들 수 있습니다.
- 타입 매핑 변형(`corresponding`, `control`, `constant`)과 `CORRESPONDING ... MAPPING FROM ENTITY [USING CONTROL]`, `MAPPING TO ENTITY`를 쓸 수 있습니다.

**전제**

- R-02에서 만든 메시지 클래스 `ZRAP_MSG_###`과 예외 클래스 `ZCM_RAP_###`이 있습니다(001~015, R-03의 030~033 등 사용 중). 이 문제는 **140~146번**을 씁니다.
- 표준 데모 테이블 `/DMO/CUSTOMER`(고객 존재 확인)를 씁니다. BTP 트라이얼에 기본으로 들어 있습니다.
- 기존 Travel BO는 건드리지 않습니다. 이 문제는 **전용 작은 BO(견적 Quote + 품목 Item)**를 새로 만듭니다. draft는 일부러 쓰지 않습니다(고급 BDEF 문법에 집중하기 위해서입니다. draft는 R-01, R-02, R-07에서 다룹니다).
- 문법 대부분은 아래 표의 릴리스 이후에만 있습니다. BTP 트라이얼은 최신 릴리스이므로 모두 쓸 수 있어야 하지만, 로컬 예제에서 실제 코드를 찾지 못한 문법은 정답에 **(실제 시스템에서 확인 필요)**라고 표시했습니다. 그런 줄에서 문법 오류가 나면 ADT에서 그 자리에 커서를 두고 `Ctrl+Space`(코드 완성)와 `F1`(키워드 문서)로 정확한 형태를 확인하세요.

| 기능 | 문법 | 도입 릴리스(cheat sheet 33 릴리스 뉴스 기준) | 이 문제에서 확인 상태 |
|---|---|---|---|
| 추상 BDEF | `abstract;` | 7.83 (2102) | 공식 예제(Feature Showcase)로 확인 |
| 추상 BDEF `with control` | `define behavior for ... with control` | 7.85 (2108) | 공식 예제로 확인 |
| 필드 `mandatory : execute` | `field ( mandatory : execute ) f;` | 7.88 (2205) | 공식 예제로 확인 |
| 연관 `mandatory : execute` | 연관에 붙이는 형태 | 7.94 (2311) | **확인 필요** (붙이는 위치) |
| `with hierarchy like entity` | 추상 BDEF 헤더 | 9.12 (2408) | **확인 필요** |
| 추상 엔터티의 부모 연관(ON 생략) | `association to parent` | 7.85 (2108) | 릴리스 뉴스로 확인 |
| deep 파라미터/결과 | `deep parameter`, `deep table parameter`, `deep result` | 추상 BDEF와 함께(7.83~) | cheat sheet 36 + 공식 예제로 확인 |
| deep 결과의 `selective` | `deep result selective [1] ...` | 7.89 (2208) | cheat sheet 36으로 확인 |
| deep 파라미터의 `%control`을 `FIELDS ( ... ) WITH`로 | EML | 7.89 (2208) | 릴리스 뉴스로 확인, 구체 형태는 **확인 필요** |
| save action 단계 지정 | `save ( finalize )`, `save ( adjustnumbers )` | 7.89 (2208) | cheat sheet 36으로 확인 |
| `notrigger[:warn]` | `field ( notrigger ) f;` | 7.90 (2211) | 릴리스 뉴스로 확인 |
| managed `suppress` | `field ( suppress ) f;` | 7.88 (2205) | cheat sheet 36으로 확인 |
| 인스턴스 팩토리 액션(managed) | `factory action a [1];` | 7.86 (2111) | 기존 문제(R-02)에서 사용 |
| 팩토리 다중 결과 | `[0..*]`, `[1..*]` | 7.96 (2405) | 릴리스 뉴스 + cheat sheet 36으로 확인 |
| RAP key function | key function | 7.96 (2405) | **문법 확인 필요** |
| BDEF 대체 키(pure / secondary) | alternative key | 9.12 (2408) | **문법 확인 필요** |
| 타입 매핑 상수 | `constant` | 9.15 (2505) | **문법 확인 필요** |
| determine action | `determine action ... { determination ( always ) ...; }` | 7.81 (2008) | 공식 예제로 확인 |

**만들 객체**

| 순서 | 객체 유형 | 이름 | 역할 |
|---|---|---|---|
| 1 | 데이터베이스 테이블 | `ZRAP_QUOTE_###` | 견적 헤더(활성 데이터) |
| 2 | 데이터베이스 테이블 | `ZRAP_QITEM_###` | 견적 품목 |
| 3 | 클래스(콘솔) | `ZCL_RAP_R14_DATA_###` | 데모 데이터 3건 생성 |
| 4 | 메시지 클래스 / 예외 클래스 | `ZRAP_MSG_###` / `ZCM_RAP_###` | 140~146번 메시지 추가 |
| 5 | CDS 루트 뷰 엔터티 | `ZRAP_R_QUOTE_###` | 견적 BO 루트 |
| 6 | CDS 뷰 엔터티 | `ZRAP_R_QUOTEITEM_###` | 견적 BO 자식(품목) |
| 7 | CDS 추상 엔터티 + 추상 BDEF | `ZRAP_A_QIMPORT_###`, `ZRAP_A_QIMPITEM_###` | 가져오기용 계층 파라미터(헤더 + 품목 표) |
| 8 | CDS 추상 엔터티 + 추상 BDEF | `ZRAP_A_PRICESIM_###`, `ZRAP_A_PRICELINE_###` | 가격 시뮬레이션 계층 결과 |
| 9 | CDS 추상 엔터티(평면) | `ZRAP_A_QCREATE_###`, `ZRAP_A_QCHECK_###`, `ZRAP_A_QUOTENO_###` | 정적 팩토리 파라미터, 점검 결과, 견적 번호 파라미터 |
| 10 | 행동 정의(managed) | `ZRAP_R_QUOTE_###` | 이 문제의 핵심 |
| 11 | 행동 풀 | `ZBP_RAP_R_QUOTE_###` | 핸들러 `lhc_quote`, `lhc_item`, 세이버 `lsc_zrap_r_quote_###`, 버퍼 `lcl_buffer` |
| 12 | 클래스(콘솔) | `ZCL_RAP_R14_EML_###` | 단계별 EML 확인 |
| 13 | DDIC 구조 2개 | `ZRAP_S_QEXP_###`, `ZRAP_S_QEXPX_###` | 타입 매핑(`control`, `constant`) 실습용 내보내기 형식 |
| 14 | 프로젝션 뷰·BDEF, 서비스 | `ZRAP_C_QUOTE_###`, `ZRAP_C_QUOTEITEM_###`, `ZRAP_UI_QUOTE_###`, `ZRAP_UI_QUOTE_O4_###` | 외부 이름(`external`)을 OData 메타데이터에서 확인 |

#### 1단계. 견적 테이블 두 개와 데모 데이터

요구사항

1. 데이터베이스 테이블 `ZRAP_QUOTE_###`(설명 `R-14 quote header`)를 아래 표대로 만드세요. 키는 UUID(`quote_uuid`)이고, 사람이 읽는 견적 번호 `quote_no`는 **키가 아닌 대체 키**로 씁니다(저장 시점에 매김, 10단계).
2. `integrity_hash`는 BO 바깥(예: 배치)이 쓰는 기술 필드라고 가정합니다. 5단계에서 `suppress`로 RAP API에서 지웁니다.
3. 데이터베이스 테이블 `ZRAP_QITEM_###`(설명 `R-14 quote item`)를 만드세요. 품목 키도 UUID이고 `quote_uuid`로 헤더를 가리킵니다.
4. 금액 필드는 모두 `currency_code`를 참조합니다. 수량은 단위 없는 정수입니다.
5. 콘솔 클래스 `ZCL_RAP_R14_DATA_###`를 만드세요. 실행하면 두 테이블을 비우고, `/DMO/CUSTOMER`의 고객 번호 앞 3개로 아래 데모 견적 3건을 넣습니다.
   - `Q000000001`: 상태 `A`(수락됨), 유효일 오늘+30, 품목 1개(P-100, 3개 × 100.00), 합계·순액 300.00 EUR
   - `Q000000002`: 상태 `N`(신규), 유효일 **오늘−5**(만료 대상), 품목 없음
   - `Q000000003`: 상태 `N`, 유효일 오늘+14, 할인 10%, 품목 2개(P-200 1×120.00, P-300 2×40.00), 합계 200.00, **순액은 일부러 틀린 999.00**(6단계에서 determine action으로 고칩니다)

`ZRAP_QUOTE_###`

| 필드 | 키 | 데이터 엘리먼트(또는 내장 타입) | 타입 | 길이 | 소수 | 설명 |
|---|---|---|---|---|---|---|
| client | ✓ | (내장) abap.clnt | CLNT | 3 | 0 | 클라이언트 |
| quote_uuid | ✓ | sysuuid_x16 | RAW | 16 | 0 | 기술 키(managed numbering) |
| quote_no | | (내장) abap.char(10) | CHAR | 10 | 0 | 견적 번호 Q+9자리, 대체 키 |
| customer_id | | /dmo/customer_id | NUMC | 6 | 0 | 고객 |
| valid_to | | (내장) abap.dats | DATS | 8 | 0 | 유효일 |
| status | | (내장) abap.char(1) | CHAR | 1 | 0 | N 신규 / A 수락 / X 만료 |
| discount_pct | | (내장) abap.dec(5,2) | DEC | 5 | 2 | 할인율(%) |
| total_amount | | /dmo/total_price | CURR | 16 | 2 | 품목 합계 (참조: currency_code) |
| net_amount | | /dmo/total_price | CURR | 16 | 2 | 할인 후 순액 (참조: currency_code) |
| currency_code | | /dmo/currency_code | CUKY | 5 | 0 | 통화 |
| note | | (내장) abap.char(60) | CHAR | 60 | 0 | 메모(트리거에 쓰지 않는 필드) |
| integrity_hash | | (내장) abap.char(32) | CHAR | 32 | 0 | 외부 기술 필드(`suppress` 대상) |
| created_by | | abp_creation_user | CHAR | 12 | 0 | 생성자 |
| created_at | | abp_creation_tstmpl | DEC (TIMESTAMPL) | 21 | 7 | 생성 시각 |
| local_last_changed_by | | abp_locinst_lastchange_user | CHAR | 12 | 0 | 인스턴스 최종 변경자 |
| local_last_changed_at | | abp_locinst_lastchange_tstmpl | DEC (TIMESTAMPL) | 21 | 7 | 인스턴스 최종 변경 시각(ETag) |
| last_changed_at | | abp_lastchange_tstmpl | DEC (TIMESTAMPL) | 21 | 7 | 최종 변경 시각 |

`ZRAP_QITEM_###`

| 필드 | 키 | 데이터 엘리먼트(또는 내장 타입) | 타입 | 길이 | 소수 | 설명 |
|---|---|---|---|---|---|---|
| client | ✓ | (내장) abap.clnt | CLNT | 3 | 0 | 클라이언트 |
| item_uuid | ✓ | sysuuid_x16 | RAW | 16 | 0 | 기술 키(managed numbering) |
| quote_uuid | | sysuuid_x16 | RAW | 16 | 0 | 상위 견적 |
| item_no | | (내장) abap.numc(3) | NUMC | 3 | 0 | 품목 번호(견적 안에서 1부터) |
| product_id | | (내장) abap.char(10) | CHAR | 10 | 0 | 제품 코드 |
| quantity | | (내장) abap.int4 | INT4 | 10 | 0 | 수량 |
| unit_price | | /dmo/flight_price | CURR | 16 | 2 | 단가 (참조: currency_code) |
| line_amount | | /dmo/total_price | CURR | 16 | 2 | 줄 금액 = 수량 × 단가 (참조: currency_code) |
| currency_code | | /dmo/currency_code | CUKY | 5 | 0 | 통화 |
| local_last_changed_at | | abp_locinst_lastchange_tstmpl | DEC (TIMESTAMPL) | 21 | 7 | 인스턴스 최종 변경 시각(ETag) |

**직접 추가할 어노테이션**
- `@EndUserText.label` — 테이블 설명 문구.
- `@AbapCatalog.enhancement.category` — append로 확장할 수 있는지.
- `@AbapCatalog.tableCategory` — 테이블 종류(투명 테이블).
- `@AbapCatalog.deliveryClass` — 전달 클래스(애플리케이션 데이터).
- `@AbapCatalog.dataMaintenance` — 일반 유지 관리 도구로 직접 고칠 수 있는지.
- `@Semantics.amount.currencyCode` — 금액 필드가 어느 통화 필드를 따르는지.

**확인**
- 두 테이블이 활성화되고, 콘솔 클래스를 F9로 실행하면 `3 quotes, 3 items inserted`가 출력됩니다.
- 각 테이블에서 F8(Data Preview)을 누르면 견적 3줄, 품목 3줄이 보이고 `Q000000003`의 `net_amount`가 999.00입니다.

<details><summary>정답·해설</summary>

```cds
@EndUserText.label : 'R-14 quote header'                  // 테이블 설명
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE      // append 확장 불가
@AbapCatalog.tableCategory : #TRANSPARENT                // 투명 테이블
@AbapCatalog.deliveryClass : #A                          // 애플리케이션 데이터
@AbapCatalog.dataMaintenance : #RESTRICTED               // 직접 유지 관리 제한
define table zrap_quote_### {

  key client            : abap.clnt not null;
  key quote_uuid        : sysuuid_x16 not null;
  quote_no              : abap.char(10);
  customer_id           : /dmo/customer_id;
  valid_to              : abap.dats;
  status                : abap.char(1);
  discount_pct          : abap.dec(5,2);
  @Semantics.amount.currencyCode : 'zrap_quote_###.currency_code'   // 금액 → 통화 참조
  total_amount          : /dmo/total_price;
  @Semantics.amount.currencyCode : 'zrap_quote_###.currency_code'   // 금액 → 통화 참조
  net_amount            : /dmo/total_price;
  currency_code         : /dmo/currency_code;
  note                  : abap.char(60);
  integrity_hash        : abap.char(32);
  created_by            : abp_creation_user;
  created_at            : abp_creation_tstmpl;
  local_last_changed_by : abp_locinst_lastchange_user;
  local_last_changed_at : abp_locinst_lastchange_tstmpl;
  last_changed_at       : abp_lastchange_tstmpl;

}
```

```cds
@EndUserText.label : 'R-14 quote item'
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table zrap_qitem_### {

  key client            : abap.clnt not null;
  key item_uuid         : sysuuid_x16 not null;
  quote_uuid            : sysuuid_x16;
  item_no               : abap.numc(3);
  product_id            : abap.char(10);
  quantity              : abap.int4;
  @Semantics.amount.currencyCode : 'zrap_qitem_###.currency_code'   // 단가 → 통화 참조
  unit_price            : /dmo/flight_price;
  @Semantics.amount.currencyCode : 'zrap_qitem_###.currency_code'   // 줄 금액 → 통화 참조
  line_amount           : /dmo/total_price;
  currency_code         : /dmo/currency_code;
  local_last_changed_at : abp_locinst_lastchange_tstmpl;

}
```

데모 데이터 클래스:

```abap
CLASS zcl_rap_r14_data_### DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_oo_adt_classrun.
  PROTECTED SECTION.
  PRIVATE SECTION.
ENDCLASS.


CLASS zcl_rap_r14_data_### IMPLEMENTATION.

  METHOD if_oo_adt_classrun~main.
    DATA quotes TYPE STANDARD TABLE OF zrap_quote_### WITH EMPTY KEY.
    DATA items  TYPE STANDARD TABLE OF zrap_qitem_### WITH EMPTY KEY.
    DATA now    TYPE timestampl.

    "start from an empty BO
    DELETE FROM zrap_qitem_###.
    DELETE FROM zrap_quote_###.

    "three existing demo customers
    SELECT FROM /dmo/customer
      FIELDS customer_id
      ORDER BY customer_id
      INTO TABLE @DATA(customers)
      UP TO 3 ROWS.
    IF lines( customers ) < 3.
      out->write( `Not enough customers in /DMO/CUSTOMER - generate flight demo data first.` ).
      RETURN.
    ENDIF.

    GET TIME STAMP FIELD now.
    DATA(today) = cl_abap_context_info=>get_system_date( ).
    DATA(user)  = cl_abap_context_info=>get_user_technical_name( ).

    TRY.
        DATA(q1) = cl_system_uuid=>create_uuid_x16_static( ).
        DATA(q2) = cl_system_uuid=>create_uuid_x16_static( ).
        DATA(q3) = cl_system_uuid=>create_uuid_x16_static( ).
        DATA(i1) = cl_system_uuid=>create_uuid_x16_static( ).
        DATA(i2) = cl_system_uuid=>create_uuid_x16_static( ).
        DATA(i3) = cl_system_uuid=>create_uuid_x16_static( ).
      CATCH cx_uuid_error INTO DATA(uuid_error).
        out->write( uuid_error->get_text( ) ).
        RETURN.
    ENDTRY.

    quotes = VALUE #(
      created_by            = user
      created_at            = now
      local_last_changed_by = user
      local_last_changed_at = now
      last_changed_at       = now
      currency_code         = 'EUR'
      ( quote_uuid = q1 quote_no = 'Q000000001' customer_id = customers[ 1 ]-customer_id
        valid_to = today + 30 status = 'A' discount_pct = 0
        total_amount = '300.00' net_amount = '300.00' note = 'Accepted demo quote' )
      ( quote_uuid = q2 quote_no = 'Q000000002' customer_id = customers[ 2 ]-customer_id
        valid_to = today - 5 status = 'N' discount_pct = 0
        total_amount = 0 net_amount = 0 note = 'Expired demo quote' )
      ( quote_uuid = q3 quote_no = 'Q000000003' customer_id = customers[ 3 ]-customer_id
        valid_to = today + 14 status = 'N' discount_pct = 10
        total_amount = '200.00' net_amount = '999.00'          "wrong on purpose (step 6)
        note = 'Open demo quote' ) ).

    items = VALUE #(
      currency_code         = 'EUR'
      local_last_changed_at = now
      ( item_uuid = i1 quote_uuid = q1 item_no = 1 product_id = 'P-100'
        quantity = 3 unit_price = '100.00' line_amount = '300.00' )
      ( item_uuid = i2 quote_uuid = q3 item_no = 1 product_id = 'P-200'
        quantity = 1 unit_price = '120.00' line_amount = '120.00' )
      ( item_uuid = i3 quote_uuid = q3 item_no = 2 product_id = 'P-300'
        quantity = 2 unit_price = '40.00' line_amount = '80.00' ) ).

    INSERT zrap_quote_### FROM TABLE @quotes.
    INSERT zrap_qitem_### FROM TABLE @items.

    out->write( |{ lines( quotes ) } quotes, { lines( items ) } items inserted| ).
  ENDMETHOD.

ENDCLASS.
```

**왜 이렇게 쓰나**
- 키를 UUID로 두고(`numbering : managed`, 5단계) 사람이 읽는 번호는 별도 필드로 둡니다. 그래야 11단계의 **대체 키(alternative key)**와 key function이 의미를 가집니다. "기술 키로는 못 찾고, 업무 키(견적 번호)로 찾고 싶다"가 key function의 출발점입니다.
- `quote_no`는 저장 시점(save action, 10단계)에 매기므로 생성 직후에는 비어 있습니다. late numbering을 쓰지 않고도 "저장할 때 번호가 붙는" 동작을 만들 수 있다는 점을 비교해 보세요(late numbering은 R-04).
- `Q000000003`의 순액을 일부러 틀리게 넣은 이유: 결정(determination)은 **트리거 조건이 맞을 때만** 돕니다. 이미 DB에 있는 잘못된 값은 아무 필드도 바뀌지 않으면 고쳐지지 않습니다. 6단계에서 `determination ( always )`가 이 문제를 푸는 것을 봅니다.
- 콘솔 클래스에서 BO 테이블에 직접 `INSERT`하는 것은 **데모 데이터 준비용**일 뿐입니다. 업무 데이터 변경은 항상 EML로 합니다.

**자주 나는 오류와 해결**
- `customers[ 1 ]`에서 `CX_SY_ITAB_LINE_NOT_FOUND` 덤프 → `/DMO/CUSTOMER`가 비어 있는 경우입니다. 트라이얼의 Flight 데모 데이터 생성 클래스(`/DMO/CL_FLIGHT_DATA_GENERATOR`)를 먼저 실행하세요.
- 금액 필드에 `@Semantics.amount.currencyCode`를 빠뜨리면 테이블 활성화 오류가 납니다. 값은 `'테이블.필드'` 형식으로 적습니다.

</details>

#### 2단계. 메시지 140~146과 예외 클래스 확장

요구사항

1. 메시지 클래스 `ZRAP_MSG_###`에 아래 메시지를 추가하세요.

| 번호 | 텍스트 | 쓰는 곳 | severity |
|---|---|---|---|
| 140 | Quote &1 is accepted and cannot be deleted. | `validateBeforeDelete` (삭제 시 검증) | 오류 |
| 141 | Save the quote first. Only a numbered quote can be accepted. | `acceptQuote` | 오류 |
| 142 | Quote &1 has been accepted. | `acceptQuote` | 성공 |
| 143 | Import line &1: enter a product and a quantity greater than zero. | `importItems` (deep 파라미터) | 오류 |
| 144 | The quote has no items. Nothing to split. | `splitByItem` (`[1..*]` 팩토리) | 오류 |
| 145 | Quote number &1 has been assigned. | `assignQuoteNo` (save action) | 성공 |
| 146 | Quote &1 has expired and cannot be accepted. | `acceptQuote` | 오류 |

2. 예외 클래스 `ZCM_RAP_###`을 확장하세요.
   - 텍스트 상수: `quote_not_deletable`(140), `quote_not_saved`(141), `quote_accepted`(142), `import_line_invalid`(143), `quote_no_items`(144), `quote_no_assigned`(145), `quote_expired`(146)
   - 속성: `mv_quote_no`(`TYPE c LENGTH 10`), `mv_line_no`(`TYPE i`)
   - 생성자 끝에 선택 파라미터 `quote_no`, `line_no`를 추가하고 속성에 넣으세요.
   - `&1` 연결: 140·142·145·146 → `MV_QUOTE_NO`, 143 → `MV_LINE_NO`

**확인** 예외 클래스가 활성화되고, R-02~R-13에서 쓰던 기존 호출(`NEW zcm_rap_###( textid = ... travel_id = ... )`)이 그대로 문법 오류 없이 남아 있습니다(파라미터를 **끝에 OPTIONAL로** 추가했기 때문).

<details><summary>정답·해설</summary>

R-02의 클래스에 아래 부분만 **추가**합니다(기존 코드는 그대로 둡니다).

```abap
    "=== R-14 : quote texts (add to PUBLIC SECTION, after the existing CONSTANTS) ===
    CONSTANTS:
      BEGIN OF quote_not_deletable,
        msgid TYPE symsgid VALUE 'ZRAP_MSG_###',
        msgno TYPE symsgno VALUE '140',
        attr1 TYPE scx_attrname VALUE 'MV_QUOTE_NO',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF quote_not_deletable,
      BEGIN OF quote_not_saved,
        msgid TYPE symsgid VALUE 'ZRAP_MSG_###',
        msgno TYPE symsgno VALUE '141',
        attr1 TYPE scx_attrname VALUE '',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF quote_not_saved,
      BEGIN OF quote_accepted,
        msgid TYPE symsgid VALUE 'ZRAP_MSG_###',
        msgno TYPE symsgno VALUE '142',
        attr1 TYPE scx_attrname VALUE 'MV_QUOTE_NO',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF quote_accepted,
      BEGIN OF import_line_invalid,
        msgid TYPE symsgid VALUE 'ZRAP_MSG_###',
        msgno TYPE symsgno VALUE '143',
        attr1 TYPE scx_attrname VALUE 'MV_LINE_NO',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF import_line_invalid,
      BEGIN OF quote_no_items,
        msgid TYPE symsgid VALUE 'ZRAP_MSG_###',
        msgno TYPE symsgno VALUE '144',
        attr1 TYPE scx_attrname VALUE '',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF quote_no_items,
      BEGIN OF quote_no_assigned,
        msgid TYPE symsgid VALUE 'ZRAP_MSG_###',
        msgno TYPE symsgno VALUE '145',
        attr1 TYPE scx_attrname VALUE 'MV_QUOTE_NO',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF quote_no_assigned,
      BEGIN OF quote_expired,
        msgid TYPE symsgid VALUE 'ZRAP_MSG_###',
        msgno TYPE symsgno VALUE '146',
        attr1 TYPE scx_attrname VALUE 'MV_QUOTE_NO',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF quote_expired.

    "=== R-14 : placeholder attributes (add next to the other mv_ attributes) ===
    DATA mv_quote_no TYPE c LENGTH 10 READ-ONLY.
    DATA mv_line_no  TYPE i READ-ONLY.

```

생성자 정의의 마지막 파라미터 뒤에 이렇게 붙입니다(앞부분은 R-02, R-03에서 만든 그대로).

```abap
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
        status        TYPE /dmo/booking_status OPTIONAL
        "... parameters added by R-03 and later problems stay here ...
        quote_no      TYPE zrap_quote_###-quote_no OPTIONAL   "R-14
        line_no       TYPE i OPTIONAL.                        "R-14
```

생성자 구현의 다른 대입문 옆에 두 줄을 추가합니다.

```abap
    mv_quote_no = quote_no.
    mv_line_no  = line_no.
```

**왜 이렇게 쓰나**
- 파라미터 타입을 `zrap_quote_###-quote_no`(테이블 필드 참조)로 두면 호출하는 쪽에서 견적 번호 필드를 그대로 넘길 수 있습니다. 1단계 테이블을 먼저 활성화해야 하는 이유입니다.
- 140번(삭제 거부)은 **전이 메시지(transition message)**로 씁니다. 삭제된 인스턴스는 더 이상 버퍼에 없으므로 `%state_area`로 "고칠 때까지 남는 상태 메시지"를 붙일 대상이 없습니다(6단계).
- 다른 보충 문제(R-15 이후)도 이 클래스를 확장할 수 있습니다. 번호대를 문제별로 나눠(R-14는 140번대) 충돌을 피합니다.

**자주 나는 오류와 해결**
- 기존 호출에서 "Formal parameter ... is not optional" 오류 → 새 파라미터에 `OPTIONAL`을 빠뜨렸습니다.
- 메시지에 `&1`이 그대로 보임 → `attr1` 값이 `'MV_QUOTE_NO'`처럼 **대문자 속성 이름**인지 확인하세요.

</details>

#### 3단계. 견적 BO 뷰 두 개

요구사항

1. 루트 뷰 엔터티 `ZRAP_R_QUOTE_###`를 `zrap_quote_###` 위에 만드세요. 필드 이름은 CamelCase 별칭(`QuoteUUID`, `QuoteNo`, `CustomerID`, `ValidTo`, `Status`, `DiscountPct`, `TotalAmount`, `NetAmount`, `CurrencyCode`, `Note`, `IntegrityHash`, `CreatedBy`, `CreatedAt`, `LocalLastChangedBy`, `LocalLastChangedAt`, `LastChangedAt`)으로 하고, 자식으로 가는 composition `_Items`를 노출합니다.
2. 자식 뷰 엔터티 `ZRAP_R_QUOTEITEM_###`를 `zrap_qitem_###` 위에 만드세요(`ItemUUID`, `QuoteUUID`, `ItemNo`, `ProductID`, `Quantity`, `UnitPrice`, `LineAmount`, `CurrencyCode`, `LocalLastChangedAt`, 부모 연관 `_Quote`).
3. 관리 필드는 프레임워크가 자동으로 채우도록 의미 어노테이션을 붙이세요. 루트의 업무 키는 `QuoteNo`라고 알려 주세요.

**직접 추가할 어노테이션**
- `@AccessControl.authorizationCheck` — 이 실습 뷰에 접근 제어(DCL)가 필요 없음을 표시.
- `@EndUserText.label` — 뷰 설명.
- `@ObjectModel.semanticKey` — 사람이 보는 업무 키(견적 번호)가 무엇인지.
- `@Semantics.amount.currencyCode` — 금액 요소가 따르는 통화 요소.
- `@Semantics.user.createdBy`, `@Semantics.systemDateTime.createdAt` — 생성자·생성 시각 자동 채우기.
- `@Semantics.user.localInstanceLastChangedBy`, `@Semantics.systemDateTime.localInstanceLastChangedAt` — 인스턴스 변경자·변경 시각(ETag) 자동 채우기.
- `@Semantics.systemDateTime.lastChangedAt` — 최종 변경 시각 자동 채우기.

**확인**
- 두 뷰가 활성화됩니다(자식을 먼저 저장하고, 둘을 함께 활성화하세요. 서로 참조하므로 하나씩 활성화하면 오류가 납니다).
- 루트 뷰에서 F8을 누르면 3건이 보이고, 한 줄을 골라 오른쪽 클릭 → Follow Association → `_Items`로 품목이 보입니다.

<details><summary>정답·해설</summary>

```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED          // 실습용: DCL 없음 (→ 어노테이션 탭: @AccessControl.authorizationCheck)
@EndUserText.label: 'R-14 Quote'                           // 뷰 설명
@ObjectModel.semanticKey: [ 'QuoteNo' ]                    // 업무 키 = 견적 번호 (→ 어노테이션 탭: @ObjectModel.semanticKey)
define root view entity ZRAP_R_QUOTE_###
  as select from zrap_quote_###
  composition [0..*] of ZRAP_R_QUOTEITEM_### as _Items     // 자식(품목) 구성
{
  key quote_uuid            as QuoteUUID,
      quote_no              as QuoteNo,
      customer_id           as CustomerID,
      valid_to              as ValidTo,
      status                as Status,
      discount_pct          as DiscountPct,
      @Semantics.amount.currencyCode: 'CurrencyCode'       // 금액 → 통화 (→ 어노테이션 탭: @Semantics.amount.currencyCode)
      total_amount          as TotalAmount,
      @Semantics.amount.currencyCode: 'CurrencyCode'
      net_amount            as NetAmount,
      currency_code         as CurrencyCode,
      note                  as Note,
      integrity_hash        as IntegrityHash,
      @Semantics.user.createdBy: true                      // 생성자 자동
      created_by            as CreatedBy,
      @Semantics.systemDateTime.createdAt: true            // 생성 시각 자동
      created_at            as CreatedAt,
      @Semantics.user.localInstanceLastChangedBy: true     // 인스턴스 변경자 자동
      local_last_changed_by as LocalLastChangedBy,
      @Semantics.systemDateTime.localInstanceLastChangedAt: true  // ETag 필드 자동
      local_last_changed_at as LocalLastChangedAt,
      @Semantics.systemDateTime.lastChangedAt: true        // 최종 변경 시각 자동
      last_changed_at       as LastChangedAt,

      _Items
}
```

```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'R-14 Quote Item'
define view entity ZRAP_R_QUOTEITEM_###
  as select from zrap_qitem_###
  association to parent ZRAP_R_QUOTE_### as _Quote         // 부모 연관 (composition의 짝)
    on $projection.QuoteUUID = _Quote.QuoteUUID
{
  key item_uuid             as ItemUUID,
      quote_uuid            as QuoteUUID,
      item_no               as ItemNo,
      product_id            as ProductID,
      quantity              as Quantity,
      @Semantics.amount.currencyCode: 'CurrencyCode'
      unit_price            as UnitPrice,
      @Semantics.amount.currencyCode: 'CurrencyCode'
      line_amount           as LineAmount,
      currency_code         as CurrencyCode,
      @Semantics.systemDateTime.localInstanceLastChangedAt: true  // 품목 ETag
      local_last_changed_at as LocalLastChangedAt,

      _Quote
}
```

**왜 이렇게 쓰나**
- `IntegrityHash`도 뷰에는 그대로 둡니다. `suppress`는 CDS가 아니라 **BDEF의 필드 특성**이며, CDS 요소는 남겨 둔 채 RAP API(EML 파생 타입, OData)에서만 지웁니다(5단계).
- 품목에도 `localInstanceLastChangedAt`을 두어 품목을 독립된 ETag 마스터로 씁니다. 이 BO는 draft가 없으므로 total ETag(`lastChangedAt`)는 쓰지 않지만, 필드는 다른 문제와 같은 모양을 유지하려고 둡니다.

**자주 나는 오류와 해결**
- "Association _Items: target ... is not a child" 류의 오류 → 자식 뷰의 `association to parent`와 루트의 `composition`이 서로를 가리키는지, 두 뷰를 **함께** 활성화했는지 확인하세요.

</details>

#### 4단계. 추상 엔터티와 추상 BDEF: `with hierarchy`, `with control`, `mandatory : execute`

요구사항

1. **가져오기 파라미터(입력용, 계층형)**
   - 루트 추상 엔터티 `ZRAP_A_QIMPORT_###`: `ValidTo`(abap.dats), `Note`(abap.char(60)), 자식으로 가는 composition `_Items`.
   - 자식 추상 엔터티 `ZRAP_A_QIMPITEM_###`: `ProductID`(abap.char(10)), `Quantity`(abap.int4), `UnitPrice`(abap.dec(15,2)), 부모 연관 `_Header`(ON 조건 없이).
   - 추상 BDEF `ZRAP_A_QIMPORT_###`: `abstract;`, `strict ( 2 );`, `with hierarchy;`. 두 엔터티 모두 `with control`. 품목의 `ProductID`, `Quantity`는 `mandatory : execute`. 루트의 `_Items` 연관도 `mandatory : execute`(품목 표를 반드시 보내야 함).
2. **가격 시뮬레이션 결과(출력용, 계층형)**
   - 루트 추상 엔터티 `ZRAP_A_PRICESIM_###`: `TotalAmount`, `NetAmount`(abap.dec(15,2)), `DiscountPct`(abap.dec(5,2)), `CurrencyCode`(/dmo/currency_code), composition `_Lines`.
   - 자식 추상 엔터티 `ZRAP_A_PRICELINE_###`: `ItemNo`(abap.numc(3)), `ProductID`, `LineAmount`, `LineDiscount`, `LineNet`(abap.dec(15,2)), 부모 연관 `_Sim`.
   - 추상 BDEF `ZRAP_A_PRICESIM_###`: `with hierarchy;`만 쓰고 **`with control`은 쓰지 마세요**(출력 전용이므로 필요 없음).
3. **평면 추상 엔터티 3개** (BDEF 없음)
   - `ZRAP_A_QCREATE_###`: `CustomerID`(/dmo/customer_id), `NumberOfQuotes`(abap.int1), `ValidTo`(abap.dats)
   - `ZRAP_A_QCHECK_###`: `EntryIndex`, `ItemIndex`(abap.int4), `IsValid`(abap_boolean), `MessageText`(abap.char(80))
   - `ZRAP_A_QUOTENO_###`: `QuoteNo`(abap.char(10))
4. 해설을 읽고 `with hierarchy like entity`가 무엇을 더 검사하는지 한 줄로 주석에 적으세요.

**직접 추가할 어노테이션**
- `@EndUserText.label` — 추상 엔터티와 각 요소의 라벨(액션 파라미터 대화 상자·OData 메타데이터에 보이는 이름).

**확인**
- 추상 엔터티 7개와 추상 BDEF 2개가 활성화됩니다.
- 추상 BDEF는 행동 풀이 없습니다. 활성화 후 BDEF 편집기에 "implementation class" 관련 경고가 없어야 합니다.
- 추상 BDEF `ZRAP_A_QIMPORT_###`에서 `with control`을 잠시 지우고 활성화한 뒤, 7단계 코드의 `%param-%control-ValidTo`가 문법 오류가 되는 것을 나중에 확인할 수 있습니다(`with control`이 `%control`을 만든다는 증거).

<details><summary>정답·해설</summary>

추상 엔터티는 ADT에서 **New > Other ABAP Repository Object > Core Data Services > Data Definition**을 고르고 템플릿 "Define Abstract Entity"로 만듭니다. 추상 BDEF는 루트 추상 엔터티를 오른쪽 클릭 → **New Behavior Definition**으로 만들고, 구현 유형(Implementation Type)으로 **Abstract**를 고릅니다(이름은 루트 추상 엔터티와 같아야 합니다).

```cds
@EndUserText.label: 'R-14 quote import (header)'
define root abstract entity ZRAP_A_QIMPORT_###              // 계층의 루트 → root
{
  @EndUserText.label: 'Valid To'
  ValidTo : abap.dats;
  @EndUserText.label: 'Note'
  Note    : abap.char(60);
  _Items  : composition [0..*] of ZRAP_A_QIMPITEM_###;        // 자식 = 품목 표
}
```

```cds
@EndUserText.label: 'R-14 quote import (item)'
define abstract entity ZRAP_A_QIMPITEM_###
{
  @EndUserText.label: 'Product'
  ProductID : abap.char(10);
  @EndUserText.label: 'Quantity'
  Quantity  : abap.int4;
  @EndUserText.label: 'Unit Price'
  UnitPrice : abap.dec(15,2);
  _Header   : association to parent ZRAP_A_QIMPORT_###;       // 추상 엔터티끼리는 ON 조건 생략 가능(7.85~)
}
```

```bdef
abstract;                 // 추상 BDEF: 구현 없음, 타입(계층형 파생 타입)만 만든다
strict ( 2 );
with hierarchy;           // composition 트리를 따라 "깊은" 파생 타입을 만든다 → deep parameter/result 용

define behavior for ZRAP_A_QIMPORT_### with control      // with control → %param 안에 %control 이 생김
{
  association _Items { mandatory : execute; }             // 연관 필수: %control-_Items 가 켜져야 함 (7.94~, 위치·형태 실제 시스템에서 확인 필요)
}

define behavior for ZRAP_A_QIMPITEM_### with control     // 품목 줄마다 %control
{
  field ( mandatory : execute ) ProductID, Quantity;      // 실행(액션/함수 호출) 시 값 필수 (7.88~)
}
```

```cds
@EndUserText.label: 'R-14 price simulation (header)'
define root abstract entity ZRAP_A_PRICESIM_###
{
  TotalAmount  : abap.dec(15,2);
  DiscountPct  : abap.dec(5,2);
  NetAmount    : abap.dec(15,2);
  CurrencyCode : /dmo/currency_code;
  _Lines       : composition [0..*] of ZRAP_A_PRICELINE_###;
}
```

```cds
@EndUserText.label: 'R-14 price simulation (line)'
define abstract entity ZRAP_A_PRICELINE_###
{
  ItemNo       : abap.numc(3);
  ProductID    : abap.char(10);
  LineAmount   : abap.dec(15,2);
  LineDiscount : abap.dec(15,2);
  LineNet      : abap.dec(15,2);
  _Sim         : association to parent ZRAP_A_PRICESIM_###;
}
```

```bdef
abstract;
strict ( 2 );
with hierarchy;
// 변형(9.12~): with hierarchy like entity;
//   → 계층형 파생 타입이 CDS 추상 엔터티의 구조 타입과 "같은 모양"인지 더 엄격히 검사 (실제 시스템에서 확인 필요)

define behavior for ZRAP_A_PRICESIM_###                   // 출력 전용 → with control 없음
{
  association _Lines;                                     // 계층에 포함할 자식 연관
}

define behavior for ZRAP_A_PRICELINE_###
{
}
```

평면 추상 엔터티 3개:

```cds
@EndUserText.label: 'R-14 create quotes for customer'
define abstract entity ZRAP_A_QCREATE_###
{
  @EndUserText.label: 'Customer'
  CustomerID     : /dmo/customer_id;
  @EndUserText.label: 'Number of Quotes'
  NumberOfQuotes : abap.int1;
  @EndUserText.label: 'Valid To'
  ValidTo        : abap.dats;
}
```

```cds
@EndUserText.label: 'R-14 import check result'
define abstract entity ZRAP_A_QCHECK_###
{
  EntryIndex  : abap.int4;
  ItemIndex   : abap.int4;
  IsValid     : abap_boolean;
  MessageText : abap.char(80);
}
```

```cds
@EndUserText.label: 'R-14 quote number parameter'
define abstract entity ZRAP_A_QUOTENO_###
{
  @EndUserText.label: 'Quote Number'
  QuoteNo : abap.char(10);
}
```

**왜 이렇게 쓰나**
- **평면 파라미터**(`parameter ZRAP_A_...`)는 추상 엔터티 하나면 됩니다(R-02). 그런데 "헤더 + 품목 여러 줄"처럼 **표가 들어간 파라미터**는 추상 엔터티만으로는 만들 수 없고, 추상 BDEF의 `with hierarchy`가 composition 트리를 따라 **계층형(deep) 파생 타입**을 만들어 줘야 합니다. cheat sheet 36: "For deep parameters (structures or tables), SOME_ENTITY represents an abstract BDEF defined with `with hierarchy`."
- 계층형 타입에서 자식 표의 컴포넌트 이름은 **연관 이름**입니다. 그래서 7단계에서 `%param-_Items`로 품목 표를 읽습니다.
- `with control`: 파생 타입에 `%control`을 추가합니다(릴리스 7.85). 호출자가 어떤 필드를 "보냈는지" 알 수 있습니다. 예를 들어 단가 0을 보낸 것(무상 품목)과 단가를 아예 안 보낸 것(기본 단가 사용)을 구별할 수 있습니다. 출력 전용인 `ZRAP_A_PRICESIM_###`에는 필요 없습니다.
- `mandatory : execute`: 이 계층형 타입이 **액션·함수의 입력 파라미터로 쓰일 때** 값(연관이면 `%control` 플래그)을 반드시 줘야 한다는 표시입니다(필드 7.88, 연관 7.94). 공식 Feature Showcase의 `/DMO/FSA_D_OverwriteTimezoneP`가 `field (mandatory:execute) sap_timezone;`를 씁니다.
- Feature Showcase의 추상 BDEF도 `abstract; strict ( 2 ); with hierarchy;` + `define behavior for ... with control` 구조이고, 루트는 `define root abstract entity`입니다. 이 문제의 형태는 그 예제를 자식 노드까지 넓힌 것입니다.
- `ZRAP_A_QCHECK_###`처럼 **결과**로만 쓰는 평면 타입도 추상 엔터티로 만듭니다(함수의 `result [0..*] ZRAP_A_QCHECK_###`).
- 추상 엔터티의 금액은 통화 참조가 필요 없도록 `abap.dec`로 두었습니다. 행동 풀에서 BO 필드(CURR)로 옮길 때는 숫자끼리 그대로 대입됩니다.

**자주 나는 오류와 해결**
- 추상 BDEF 생성 마법사에 "Abstract"가 안 보임 → 루트 추상 엔터티(`define root abstract entity`)에서 시작했는지 확인하세요. `root`가 없으면 계층의 루트가 될 수 없습니다.
- `association _Items { mandatory : execute; }` 줄에서 문법 오류 → 연관용 `mandatory : execute`의 정확한 위치를 로컬 예제로 확인하지 못했습니다. `association _Items` 뒤에서 `Ctrl+Space`로 허용되는 추가 문구를 확인하세요. 끝내 안 되면 그 줄을 `association _Items;`로 두고, 7단계 핸들러에서 `%control-_Items`가 꺼져 있으면 직접 오류를 내는 방식으로 대신합니다(실제 시스템에서 확인 필요).
- 자식 BDEF에 `association _Header;`를 적어야 하는지 → 공식 예제가 단일 노드라 확인하지 못했습니다. 위 정답처럼 루트에 자식 연관만 적어 활성화되면 그대로 두세요(실제 시스템에서 확인 필요).

</details>

#### 5단계. 행동 정의 전체: 고급 연산 선언과 필드 특성(`suppress`·`notrigger`·`internal`)

요구사항

1. 행동 정의 `ZRAP_R_QUOTE_###`(managed)을 만드세요. 헤더: `managed with additional save`, 구현 클래스 `zbp_rap_r_quote_###`, `strict ( 2 )`. draft 없음.
2. **Quote**(`alias Quote`): 영구 테이블 `zrap_quote_###`, `lock master`, `authorization master ( global )`, `etag master LocalLastChangedAt`.
   - 표준 연산: `create; update; delete;`, 품목 생성은 **내부 전용** create-by-association(`internal create`)
   - 필드: `QuoteUUID`는 `readonly` + `numbering : managed`, 읽기 전용 `QuoteNo, Status, TotalAmount, NetAmount` + 관리 필드, 필수 `CustomerID`, **`Note`는 `notrigger`**, **`IntegrityHash`는 `suppress`**
   - 결정·검증: `setDefaults`(on modify, create), `calcNetAmount`(on save, create + 필드 `DiscountPct`, `TotalAmount`), `validateCustomer`(on save, create + 필드 `CustomerID`), **`validateBeforeDelete`(on save, delete)**
   - **determine action** `refreshQuote`: `calcNetAmount`를 **`( always )`**로, `validateCustomer`는 그냥
   - 액션: `acceptQuote`(외부 이름 `'Accept'`, `result [1] $self`), `importItems`(**deep parameter** `ZRAP_A_QIMPORT_###`, `result [1] $self`), `recalcPrices`(**`result selective [1] $self`**), 내부 액션 `recalcTotal`, 인스턴스 팩토리 `splitByItem [1..*]`, 정적 팩토리 `createForCustomer`(파라미터 `ZRAP_A_QCREATE_###`, `[0..*]`), 정적 액션 `closeExpired`(`result [0..*] $self`), **save action** `assignQuoteNo`(`finalize` 단계)
   - 함수: `simulatePricing`(**deep result** `[1] ZRAP_A_PRICESIM_###`), `getCheapestItem`(`result [0..1] entity ZRAP_R_QUOTEITEM_###`), 정적 함수 `checkImport`(**deep table parameter** `ZRAP_A_QIMPORT_###`, `result [0..*] ZRAP_A_QCHECK_###`), 정적 함수 `findByQuoteNo`(파라미터 `ZRAP_A_QUOTENO_###`, `result [0..1] $self`)
   - 타입 매핑: `mapping for zrap_quote_### corresponding { ... }`
3. **Item**(`alias Item`): 영구 테이블 `zrap_qitem_###`, `lock dependent by _Quote`, `authorization dependent by _Quote`, `etag master LocalLastChangedAt`.
   - 연산: **`internal update;`**, `delete;`(외부 허용), `association _Quote;`
   - 필드: `ItemUUID` `readonly` + `numbering : managed`, 읽기 전용 `QuoteUUID, ItemNo, LineAmount, CurrencyCode, LocalLastChangedAt`
   - 결정: `calcLineAmount`(on modify, create + 필드 `Quantity`, `UnitPrice`), **`recalcAfterDelete`(on save, delete)**
   - 타입 매핑: `mapping for zrap_qitem_### corresponding { ... }`
4. 퀵픽스로 행동 풀 `ZBP_RAP_R_QUOTE_###`를 만들고, 로컬 클래스를 정답 골격으로 바꾸세요(메서드 본문은 6~11단계에서 채웁니다. 이번 단계에서는 비어 있어도 됩니다).
5. 콘솔 클래스 `ZCL_RAP_R14_EML_###` 골격을 만드세요. 상수 `c_step`(5~12)을 바꿔 F9로 실행하면 그 단계의 확인 메서드가 실행되게 합니다. 이번 단계의 메서드 `s05_types`는 Quote의 **읽기 결과 파생 타입 컴포넌트 이름**을 모두 출력합니다.
6. 실험 세 가지를 하고 결과를 주석에 적으세요.
   - (a) `calcNetAmount`의 트리거에 `field Note`를 넣고 활성화 → 오류 확인 → `field ( notrigger ) Note;`를 `field ( notrigger : warn ) Note;`로 바꾸고 다시 활성화 → 오류가 경고로 바뀌는지 확인 → 원래대로 되돌리기
   - (b) `s05_types` 출력에 `IntegrityHash`가 없는지 확인. 콘솔에서 `quote-IntegrityHash`를 쓰는 줄의 주석을 풀면 문법 오류가 나는지 확인
   - (c) 콘솔에서 `ENTITY Item UPDATE ...`(내부 연산)를 쓰는 줄의 주석을 풀면 문법 오류가 나는지 확인

**확인**
- BDEF, 행동 풀, 콘솔 클래스가 모두 활성화됩니다(행동 풀 메서드가 비어 있어도 활성화됩니다).
- `c_step = 5`로 실행하면 `QUOTEUUID`, `QUOTENO`, `CUSTOMERID` … 처럼 컴포넌트 이름이 출력되고, **`INTEGRITYHASH`는 없습니다**(`get_included_view`는 `%tky` 같은 이름 있는 include 그룹을 펼쳐서 보여 줍니다).
- 실험 (a)에서 `notrigger` 필드를 트리거에 쓰면 활성화가 막히고, `notrigger : warn`이면 경고만 남습니다.

<details><summary>정답·해설</summary>

```bdef
managed with additional save                              // 세이버 클래스(finalize, save_modified)를 쓰기 위해
implementation in class zbp_rap_r_quote_### unique;
strict ( 2 );

define behavior for ZRAP_R_QUOTE_### alias Quote
persistent table zrap_quote_###
lock master
authorization master ( global )
etag master LocalLastChangedAt
{
  create;
  update;
  delete;

  association _Items { internal create; }                 // 품목은 BO 안(IN LOCAL MODE)에서만 생성 (실제 시스템에서 확인 필요: 연관의 internal create)

  //--- 필드 특성 -------------------------------------------------------------
  field ( readonly, numbering : managed ) QuoteUUID;      // UUID 키 자동 부여
  field ( readonly ) QuoteNo, Status, TotalAmount, NetAmount,
                     CreatedBy, CreatedAt, LocalLastChangedBy, LocalLastChangedAt, LastChangedAt;
  field ( mandatory ) CustomerID;
  field ( notrigger ) Note;                               // 트리거 조건에 쓰면 오류 (7.90~)
  field ( suppress ) IntegrityHash;                       // 파생 타입·모든 RAP API에서 제거 (managed 7.88~)

  //--- 결정·검증 -------------------------------------------------------------
  determination setDefaults on modify { create; }
  determination calcNetAmount on save { create; field DiscountPct, TotalAmount; }
  validation validateCustomer on save { create; field CustomerID; }
  validation validateBeforeDelete on save { delete; }     // 삭제가 저장될 때 실행

  determine action refreshQuote                           // 요청 시 결정·검증 실행
  {
    determination ( always ) calcNetAmount;                // 트리거 조건과 상관없이 항상
    validation validateCustomer;                           // 트리거 조건이 맞을 때만
  }

  //--- 액션 ------------------------------------------------------------------
  action acceptQuote external 'Accept' result [1] $self;  // OData 에는 'Accept' 로 노출
  action importItems deep parameter ZRAP_A_QIMPORT_### result [1] $self;
  action recalcPrices result selective [1] $self;         // 요청된 필드만 결과로 (REQUEST 파라미터)
  internal action recalcTotal;                            // BO 안에서만
  factory action splitByItem [1..*];                      // 인스턴스 팩토리, 1개 이상 생성
  static factory action createForCustomer parameter ZRAP_A_QCREATE_### [0..*];  // 0개 이상 생성
  static action closeExpired result [0..*] $self;         // 정적(인스턴스 없음), 비팩토리
  save ( finalize ) action assignQuoteNo;                 // 저장 시퀀스 finalize 에서만 실행 가능

  //--- 함수 ------------------------------------------------------------------
  function simulatePricing deep result [1] ZRAP_A_PRICESIM_###;
  function getCheapestItem result [0..1] entity ZRAP_R_QUOTEITEM_###;   // 다른 엔터티 타입 결과, 0 또는 1
  static function checkImport deep table parameter ZRAP_A_QIMPORT_### result [0..*] ZRAP_A_QCHECK_###;
  static function findByQuoteNo parameter ZRAP_A_QUOTENO_### result [0..1] $self;

  //--- 타입 매핑 -------------------------------------------------------------
  mapping for zrap_quote_### corresponding                // 이름이 같은 필드는 자동, 다른 것만 나열
  {
    QuoteUUID          = quote_uuid;
    QuoteNo            = quote_no;
    CustomerID         = customer_id;
    ValidTo            = valid_to;
    Status             = status;
    DiscountPct        = discount_pct;
    TotalAmount        = total_amount;
    NetAmount          = net_amount;
    CurrencyCode       = currency_code;
    Note               = note;
    CreatedBy          = created_by;
    CreatedAt          = created_at;
    LocalLastChangedBy = local_last_changed_by;
    LocalLastChangedAt = local_last_changed_at;
    LastChangedAt      = last_changed_at;
  }
}

define behavior for ZRAP_R_QUOTEITEM_### alias Item
persistent table zrap_qitem_###
lock dependent by _Quote
authorization dependent by _Quote
etag master LocalLastChangedAt
{
  internal update;                                        // 값 변경은 BO 안에서만
  delete;                                                 // 삭제는 외부에서도

  association _Quote;

  field ( readonly, numbering : managed ) ItemUUID;
  field ( readonly ) QuoteUUID, ItemNo, LineAmount, CurrencyCode, LocalLastChangedAt;

  determination calcLineAmount on modify { create; field Quantity, UnitPrice; }
  determination recalcAfterDelete on save { delete; }     // 품목 삭제가 저장될 때 헤더 합계 재계산

  mapping for zrap_qitem_### corresponding
  {
    ItemUUID           = item_uuid;
    QuoteUUID          = quote_uuid;
    ItemNo             = item_no;
    ProductID          = product_id;
    Quantity           = quantity;
    UnitPrice          = unit_price;
    LineAmount         = line_amount;
    CurrencyCode       = currency_code;
    LocalLastChangedAt = local_last_changed_at;
  }
}
```

행동 풀 전역 클래스(퀵픽스가 만든 그대로):

```abap
CLASS zbp_rap_r_quote_### DEFINITION PUBLIC ABSTRACT FINAL FOR BEHAVIOR OF zrap_r_quote_###.
ENDCLASS.

CLASS zbp_rap_r_quote_### IMPLEMENTATION.
ENDCLASS.
```

로컬 타입(Local Types) 탭 전체 골격:

```abap
*"* R-14 behavior pool: handlers lhc_quote / lhc_item, saver lsc_zrap_r_quote_###

"----------------------------------------------------------------------
" transaction-wide buffer shared by handlers and saver
"----------------------------------------------------------------------
CLASS lcl_buffer DEFINITION FINAL.
  PUBLIC SECTION.
    "UUIDs of quotes created in the current RAP transaction
    "(filled by setDefaults, used by the saver's finalize -> save action)
    CLASS-DATA new_quotes TYPE SORTED TABLE OF sysuuid_x16 WITH UNIQUE KEY table_line.
    CLASS-METHODS clear.
ENDCLASS.

CLASS lcl_buffer IMPLEMENTATION.
  METHOD clear.
    CLEAR new_quotes.
  ENDMETHOD.
ENDCLASS.

"----------------------------------------------------------------------
" Quote handler
"----------------------------------------------------------------------
CLASS lhc_quote DEFINITION INHERITING FROM cl_abap_behavior_handler.
  PRIVATE SECTION.
    CONSTANTS:
      BEGIN OF quote_status,
        new      TYPE c LENGTH 1 VALUE 'N',
        accepted TYPE c LENGTH 1 VALUE 'A',
        expired  TYPE c LENGTH 1 VALUE 'X',
      END OF quote_status,
      c_default_currency TYPE /dmo/currency_code VALUE 'EUR',
      c_default_price    TYPE /dmo/flight_price VALUE '100.00',
      c_max_new_quotes   TYPE i VALUE 10.

    METHODS get_global_authorizations FOR GLOBAL AUTHORIZATION
      IMPORTING REQUEST requested_authorizations FOR Quote RESULT result.

    "determinations / validations (step 6)
    METHODS setDefaults FOR DETERMINE ON MODIFY
      IMPORTING keys FOR Quote~setDefaults.
    METHODS calcNetAmount FOR DETERMINE ON SAVE
      IMPORTING keys FOR Quote~calcNetAmount.
    METHODS validateCustomer FOR VALIDATE ON SAVE
      IMPORTING keys FOR Quote~validateCustomer.
    METHODS validateBeforeDelete FOR VALIDATE ON SAVE
      IMPORTING keys FOR Quote~validateBeforeDelete.
    METHODS recalcTotal FOR MODIFY
      IMPORTING keys FOR ACTION Quote~recalcTotal.

    "deep parameter / deep result / deep table parameter (step 7)
    METHODS importItems FOR MODIFY
      IMPORTING keys FOR ACTION Quote~importItems RESULT result.
    METHODS simulatePricing FOR READ
      IMPORTING keys FOR FUNCTION Quote~simulatePricing RESULT result.
    METHODS checkImport FOR READ
      IMPORTING keys FOR FUNCTION Quote~checkImport RESULT result.

    "result variants and external name (step 8)
    METHODS recalcPrices FOR MODIFY
      IMPORTING keys REQUEST requested_fields FOR ACTION Quote~recalcPrices RESULT result.
    METHODS getCheapestItem FOR READ
      IMPORTING keys FOR FUNCTION Quote~getCheapestItem RESULT result.
    METHODS closeExpired FOR MODIFY
      IMPORTING keys FOR ACTION Quote~closeExpired RESULT result.
    METHODS acceptQuote FOR MODIFY
      IMPORTING keys FOR ACTION Quote~acceptQuote RESULT result.

    "factory actions with multiplicity (step 9)
    METHODS createForCustomer FOR MODIFY
      IMPORTING keys FOR ACTION Quote~createForCustomer.
    METHODS splitByItem FOR MODIFY
      IMPORTING keys FOR ACTION Quote~splitByItem.

    "save action (step 10)
    METHODS assignQuoteNo FOR MODIFY
      IMPORTING keys FOR ACTION Quote~assignQuoteNo.

    "lookup by alternative key (step 11)
    METHODS findByQuoteNo FOR READ
      IMPORTING keys FOR FUNCTION Quote~findByQuoteNo RESULT result.
ENDCLASS.

CLASS lhc_quote IMPLEMENTATION.

  METHOD get_global_authorizations.
    "R-14 focuses on BDEF syntax: allow everything (real checks: see R-03)
    result = VALUE #( %create = if_abap_behv=>auth-allowed
                      %update = if_abap_behv=>auth-allowed
                      %delete = if_abap_behv=>auth-allowed ).
  ENDMETHOD.

  METHOD setDefaults.          "-> step 6
  ENDMETHOD.

  METHOD calcNetAmount.        "-> step 6
  ENDMETHOD.

  METHOD validateCustomer.     "-> step 6
  ENDMETHOD.

  METHOD validateBeforeDelete. "-> step 6
  ENDMETHOD.

  METHOD recalcTotal.          "-> step 6
  ENDMETHOD.

  METHOD importItems.          "-> step 7
  ENDMETHOD.

  METHOD simulatePricing.      "-> step 7
  ENDMETHOD.

  METHOD checkImport.          "-> step 7
  ENDMETHOD.

  METHOD recalcPrices.         "-> step 8
  ENDMETHOD.

  METHOD getCheapestItem.      "-> step 8
  ENDMETHOD.

  METHOD closeExpired.         "-> step 8
  ENDMETHOD.

  METHOD acceptQuote.          "-> step 8
  ENDMETHOD.

  METHOD createForCustomer.    "-> step 9
  ENDMETHOD.

  METHOD splitByItem.          "-> step 9
  ENDMETHOD.

  METHOD assignQuoteNo.        "-> step 10
  ENDMETHOD.

  METHOD findByQuoteNo.        "-> step 11
  ENDMETHOD.

ENDCLASS.

"----------------------------------------------------------------------
" Item handler
"----------------------------------------------------------------------
CLASS lhc_item DEFINITION INHERITING FROM cl_abap_behavior_handler.
  PRIVATE SECTION.
    METHODS calcLineAmount FOR DETERMINE ON MODIFY
      IMPORTING keys FOR Item~calcLineAmount.
    METHODS recalcAfterDelete FOR DETERMINE ON SAVE
      IMPORTING keys FOR Item~recalcAfterDelete.
ENDCLASS.

CLASS lhc_item IMPLEMENTATION.

  METHOD calcLineAmount.       "-> step 6
  ENDMETHOD.

  METHOD recalcAfterDelete.    "-> step 6
  ENDMETHOD.

ENDCLASS.

"----------------------------------------------------------------------
" Saver
"----------------------------------------------------------------------
CLASS lsc_zrap_r_quote_### DEFINITION INHERITING FROM cl_abap_behavior_saver.
  PROTECTED SECTION.
    METHODS finalize         REDEFINITION.   "-> step 10 (calls the save action)
    METHODS save_modified    REDEFINITION.   "required by 'with additional save'
    METHODS cleanup_finalize REDEFINITION.
ENDCLASS.

CLASS lsc_zrap_r_quote_### IMPLEMENTATION.

  METHOD finalize.             "-> step 10
  ENDMETHOD.

  METHOD save_modified.        "-> step 10
  ENDMETHOD.

  METHOD cleanup_finalize.     "-> step 10
  ENDMETHOD.

ENDCLASS.
```

콘솔 클래스 골격과 5단계 메서드:

```abap
CLASS zcl_rap_r14_eml_### DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_oo_adt_classrun.

  PROTECTED SECTION.
  PRIVATE SECTION.
    "change and press F9: 5 .. 12
    CONSTANTS c_step TYPE i VALUE 5.

    TYPES ty_reported      TYPE RESPONSE FOR REPORTED EARLY zrap_r_quote_###.
    TYPES ty_reported_late TYPE RESPONSE FOR REPORTED LATE zrap_r_quote_###.
    TYPES ty_failed        TYPE RESPONSE FOR FAILED EARLY zrap_r_quote_###.

    DATA out TYPE REF TO if_oo_adt_classrun_out.

    METHODS s05_types.
    METHODS s06_triggers.
    METHODS s07_deep.
    METHODS s08_results.
    METHODS s09_factory.
    METHODS s10_save_action.
    METHODS s11_key.
    METHODS s12_mapping.

    METHODS uuid_of
      IMPORTING quote_no    TYPE zrap_quote_###-quote_no
      RETURNING VALUE(uuid) TYPE sysuuid_x16.
    METHODS print_reported
      IMPORTING title    TYPE string
                reported TYPE ty_reported.
    METHODS print_reported_late
      IMPORTING title    TYPE string
                reported TYPE ty_reported_late.
    METHODS print_failed
      IMPORTING title  TYPE string
                failed TYPE ty_failed.
ENDCLASS.


CLASS zcl_rap_r14_eml_### IMPLEMENTATION.

  METHOD if_oo_adt_classrun~main.
    me->out = out.
    CASE c_step.
      WHEN 5.  s05_types( ).
      WHEN 6.  s06_triggers( ).
      WHEN 7.  s07_deep( ).
      WHEN 8.  s08_results( ).
      WHEN 9.  s09_factory( ).
      WHEN 10. s10_save_action( ).
      WHEN 11. s11_key( ).
      WHEN 12. s12_mapping( ).
    ENDCASE.
  ENDMETHOD.


  METHOD s05_types.
    "(b) suppress: the derived type has no IntegrityHash component
    DATA quote TYPE STRUCTURE FOR READ RESULT zrap_r_quote_###\\Quote.
    DATA(descr) = CAST cl_abap_structdescr( cl_abap_typedescr=>describe_by_data( quote ) ).
    LOOP AT descr->get_included_view( ) INTO DATA(comp).   "includes (%tky, %key ...) expanded
      out->write( comp-name ).
    ENDLOOP.

    "uncomment -> syntax error: component INTEGRITYHASH does not exist
    "quote-IntegrityHash = 'X'.

    "(c) internal update: not callable outside the BO
    "uncomment -> syntax error (operation is internal)
    "MODIFY ENTITIES OF zrap_r_quote_###
    "  ENTITY Item UPDATE FIELDS ( Quantity ) WITH VALUE #( ( ItemUUID = '00' Quantity = 1 ) ).
  ENDMETHOD.


  METHOD s06_triggers.     "-> step 6
  ENDMETHOD.

  METHOD s07_deep.         "-> step 7
  ENDMETHOD.

  METHOD s08_results.      "-> step 8
  ENDMETHOD.

  METHOD s09_factory.      "-> step 9
  ENDMETHOD.

  METHOD s10_save_action.  "-> step 10
  ENDMETHOD.

  METHOD s11_key.          "-> step 11
  ENDMETHOD.

  METHOD s12_mapping.      "-> step 12
  ENDMETHOD.


  METHOD uuid_of.
    SELECT SINGLE FROM zrap_quote_### FIELDS quote_uuid
      WHERE quote_no = @quote_no
      INTO @uuid.
  ENDMETHOD.


  METHOD print_reported.
    LOOP AT reported-quote INTO DATA(rq).
      CHECK rq-%msg IS BOUND.
      out->write( |  { title } Quote: { rq-%msg->if_message~get_text( ) }| ).
    ENDLOOP.
    LOOP AT reported-item INTO DATA(ri).
      CHECK ri-%msg IS BOUND.
      out->write( |  { title } Item: { ri-%msg->if_message~get_text( ) }| ).
    ENDLOOP.
  ENDMETHOD.


  METHOD print_reported_late.
    LOOP AT reported-quote INTO DATA(rq).
      CHECK rq-%msg IS BOUND.
      out->write( |  { title } (save) Quote: { rq-%msg->if_message~get_text( ) }| ).
    ENDLOOP.
    LOOP AT reported-item INTO DATA(ri).
      CHECK ri-%msg IS BOUND.
      out->write( |  { title } (save) Item: { ri-%msg->if_message~get_text( ) }| ).
    ENDLOOP.
  ENDMETHOD.


  METHOD print_failed.
    LOOP AT failed-quote INTO DATA(fq).
      out->write( |  { title } failed Quote { fq-QuoteUUID } cause { fq-%fail-cause }| ).
    ENDLOOP.
    LOOP AT failed-item INTO DATA(fi).
      out->write( |  { title } failed Item { fi-ItemUUID } cause { fi-%fail-cause }| ).
    ENDLOOP.
  ENDMETHOD.

ENDCLASS.
```

실험 결과 주석(정답 예):

```bdef
// (a) determination calcNetAmount on save { create; field DiscountPct, TotalAmount, Note; }
//     + field ( notrigger ) Note;       → 활성화 오류 (notrigger 필드는 트리거에 쓸 수 없음)
//     + field ( notrigger : warn ) Note; → 활성화는 되고 경고만 남음
//     → 실험 후 calcNetAmount 트리거에서 Note 를 빼고 notrigger 로 되돌림
```

**왜 이렇게 쓰나 — 문법별 정리**

| 문법 | 이 BO에서의 뜻 | 핸들러/파생 타입에 생기는 것 |
|---|---|---|
| `association _Items { internal create; }` | 품목은 액션(`importItems`, `splitByItem`) 안에서만 만들어짐 | EML 바깥 소비자는 `CREATE BY \_Items` 불가, BO 안에서는 `IN LOCAL MODE`로 가능 |
| `internal update;` (Item) | 줄 금액·수량은 결정/액션만 바꿈 | 바깥 `UPDATE` 불가(실험 c) |
| `field ( suppress ) IntegrityHash;` | 기술 필드를 RAP API에서 완전히 제거 | 모든 파생 타입에서 컴포넌트가 사라짐(실험 b), OData에도 없음 |
| `field ( notrigger ) Note;` | 이 필드는 결정·검증 트리거에 쓰지 않겠다는 선언 | 트리거에 쓰면 활성화 오류, `notrigger : warn`이면 경고 |
| `validation ... on save { delete; }` | 삭제가 저장될 때 검사 | 키는 **삭제된 인스턴스** → 버퍼에서 READ 불가(6단계) |
| `determination ( always )` | determine action 실행 시 트리거와 무관하게 실행 | 핸들러 추가 없음(determine action은 구현 메서드가 없음) |
| `external 'Accept'` | OData 이름만 바뀜 | EML·핸들러는 여전히 `acceptQuote` |
| `result selective [1] $self` | 소비자가 원하는 필드만 결과로 | 핸들러 시그니처에 `REQUEST requested_fields` |
| `deep parameter` / `deep table parameter` | 계층형 `%param` (구조 / 표) | `%param-_Items` 표, `%param-%control` |
| `deep result [1] ZRAP_A_PRICESIM_###` | 계층형 결과 | `result-%param-_Lines` 표 |
| `result [0..1] entity ZRAP_R_QUOTEITEM_###` | 품목 타입 결과, 없을 수도 있음 | `result-%param`이 품목 구조 |
| `factory action ... [1..*]`, `static factory action ... [0..*]` | 한 번 호출로 여러 인스턴스 생성 | `mapped-quote`에 같은 `%cid`로 여러 줄 |
| `save ( finalize ) action` | 저장 시퀀스의 `finalize`에서만 실행 | 핸들러는 일반 액션과 같은 모양, 호출은 세이버에서 |

- **클래스 구조 해설**: 핸들러 메서드 시그니처는 모두 BDEF 한 줄에서 나옵니다. `action X ... result` → `FOR MODIFY IMPORTING keys FOR ACTION Quote~X RESULT result`, `function` → `FOR READ ... FOR FUNCTION`, `result selective` → 추가로 `REQUEST requested_fields`, `determination ... on modify/on save` → `FOR DETERMINE ON MODIFY/ON SAVE`, `validation` → `FOR VALIDATE ON SAVE`. `determine action refreshQuote`와 `save ( finalize ) action`의 **실행 시점**은 다르지만 save action도 **일반 액션과 같은 핸들러 메서드**를 가집니다. 메서드 이름 앞에 커서를 두고 F2를 누르면 `keys`, `result`, `requested_fields`의 실제 파생 타입을 볼 수 있습니다. 이 문제 내내 **새 문법을 만나면 F2로 파생 타입을 먼저 열어 보는 습관**을 들이세요.
- `managed with additional save`로 둔 이유: 10단계에서 세이버의 `finalize`를 재정의해 save action을 실행하기 위해서입니다. 로컬 자료에는 managed 세이버에서 `finalize`를 재정의한 예제가 없었습니다(R-04 해설 참고). 활성화 시 `finalize` 재정의가 거부되면 10단계 해설의 대안을 쓰세요(실제 시스템에서 확인 필요).
- `numbering : managed` UUID 키 + `readonly`: 소비자는 키를 보내지 않고 프레임워크가 UUID를 넣습니다(cheat sheet 36 "Managed internal numbering").

**자주 나는 오류와 해결**
- `deep parameter ZRAP_A_QIMPORT_###`에서 "is not an abstract behavior definition with hierarchy" 류의 오류 → 4단계 추상 BDEF가 활성화됐는지, 헤더에 `with hierarchy;`가 있는지 확인하세요.
- `result [0..1] entity ZRAP_R_QUOTEITEM_###`에서 오류 → `entity` 다음에는 별칭(`Item`)이 아니라 **CDS 엔터티 이름**을 씁니다.
- 행동 풀 활성화 시 "method ... is not implemented" 경고 → 이번 단계에서는 정상입니다. 단, 메서드 **정의**는 BDEF와 정확히 맞아야 활성화됩니다. 퀵픽스("Add missing method")로 만든 정의와 위 골격을 비교해 보세요.
- `save ( finalize ) action` 줄에서 오류 → `save` 다음 괄호 안에는 `finalize`, `adjustnumbers` 또는 둘 다만 올 수 있습니다(cheat sheet 36). 괄호 앞뒤 공백 차이는 문제 되지 않습니다.

</details>

#### 6단계. 트리거 고급: `on save { delete; }`, `determination ( always )`, 내부 연산과 `IN LOCAL MODE`

요구사항

1. `setDefaults`(on modify, create): 새 견적의 `Status`가 비면 `N`, `ValidTo`가 비면 오늘+30일, `CurrencyCode`가 비면 `EUR`. 그리고 새 견적의 UUID를 `lcl_buffer=>new_quotes`에 기록합니다(10단계 save action이 씁니다).
2. `calcNetAmount`(on save): `NetAmount = TotalAmount − TotalAmount × DiscountPct / 100`. 값이 이미 같으면 변경하지 않습니다.
3. `validateCustomer`(on save): 고객이 비었으면 001, `/DMO/CUSTOMER`에 없으면 002(R-02 메시지 재사용). `%state_area = 'VALIDATE_CUSTOMER'`로 먼저 지우고, 오류면 `failed` + `%element-CustomerID`.
4. `validateBeforeDelete`(on save **{ delete; }**): 삭제하려는 견적이 DB에서 상태 `A`(수락됨)이면 삭제 저장을 거부하고 140번 메시지. **삭제된 인스턴스는 버퍼에서 읽을 수 없다**는 점을 고려해 구현하세요.
5. 내부 액션 `recalcTotal`: 품목 `LineAmount` 합계를 헤더 `TotalAmount`에 넣습니다.
6. 품목 `calcLineAmount`(on modify): `LineAmount = Quantity × UnitPrice`(내부 update), 그리고 부모마다 `recalcTotal` 실행. 둘 다 내부 연산이므로 `IN LOCAL MODE`가 필수입니다.
7. 품목 `recalcAfterDelete`(on save **{ delete; }**): 삭제된 품목의 부모 견적을 찾아 `recalcTotal` 실행. 부모도 같은 트랜잭션에서 삭제됐다면 건너뜁니다.
8. 콘솔 `s06_triggers`: (1) 견적 생성·커밋 후 기본값 확인, (2) 없는 고객으로 생성 → 커밋 실패 메시지 출력 후 `ROLLBACK ENTITIES`, (3) `Q000000001`(수락됨) 삭제 → 커밋 실패, 140번 출력 후 롤백, (4) `Q000000003`에 determine action `refreshQuote` 실행·커밋 → 순액 999.00이 180.00으로 고쳐짐, (5) `Q000000003`의 마지막 품목 삭제·커밋 → 합계 120.00, 순액 108.00.

**확인**
- `c_step = 6` 실행 결과(데모 데이터 생성 클래스를 먼저 다시 실행하세요):
  - `(1) created: Status=N ValidTo=<오늘+30> Currency=EUR QuoteNo=''` (번호는 10단계 이후에 붙습니다)
  - `(2)`에 `Customer 999999 does not exist.`
  - `(3) delete accepted quote: sy-subrc=4`와 `Quote Q000000001 is accepted and cannot be deleted.`
  - `(4) ... total=200.00 net=180.00`
  - `(5) ... total=120.00 net=108.00`
- BDEF에서 `determination ( always ) calcNetAmount;`의 `( always )`를 지우고 데모 데이터를 다시 만든 뒤 실행하면 (4)의 순액이 **999.00 그대로** 남습니다. 확인 후 원래대로 되돌리세요.

<details><summary>정답·해설</summary>

`lhc_quote` 구현부의 해당 메서드:

```abap
  METHOD setDefaults.
    READ ENTITIES OF zrap_r_quote_### IN LOCAL MODE
      ENTITY Quote
        FIELDS ( Status ValidTo CurrencyCode ) WITH CORRESPONDING #( keys )
      RESULT DATA(quotes).

    "remember new quotes: the saver calls the save action assignQuoteNo for them (step 10)
    LOOP AT quotes INTO DATA(quote).
      INSERT quote-QuoteUUID INTO TABLE lcl_buffer=>new_quotes.
    ENDLOOP.

    DELETE quotes WHERE Status IS NOT INITIAL
                    AND ValidTo IS NOT INITIAL
                    AND CurrencyCode IS NOT INITIAL.
    CHECK quotes IS NOT INITIAL.

    DATA(today) = cl_abap_context_info=>get_system_date( ).

    MODIFY ENTITIES OF zrap_r_quote_### IN LOCAL MODE        "Status is read-only -> local mode
      ENTITY Quote
        UPDATE FIELDS ( Status ValidTo CurrencyCode )
        WITH VALUE #( FOR q IN quotes
                      ( %tky         = q-%tky
                        Status       = COND #( WHEN q-Status IS INITIAL THEN quote_status-new ELSE q-Status )
                        ValidTo      = COND #( WHEN q-ValidTo IS INITIAL THEN today + 30 ELSE q-ValidTo )
                        CurrencyCode = COND #( WHEN q-CurrencyCode IS INITIAL THEN c_default_currency
                                               ELSE q-CurrencyCode ) ) )
      REPORTED DATA(upd_reported).

    reported = CORRESPONDING #( DEEP upd_reported ).
  ENDMETHOD.


  METHOD calcNetAmount.
    READ ENTITIES OF zrap_r_quote_### IN LOCAL MODE
      ENTITY Quote
        FIELDS ( TotalAmount DiscountPct NetAmount ) WITH CORRESPONDING #( keys )
      RESULT DATA(quotes).

    DATA quote_upd TYPE TABLE FOR UPDATE zrap_r_quote_###\\Quote.
    LOOP AT quotes INTO DATA(quote).
      DATA(net) = CONV /dmo/total_price( quote-TotalAmount - quote-TotalAmount * quote-DiscountPct / 100 ).
      IF net <> quote-NetAmount.
        APPEND VALUE #( %tky = quote-%tky NetAmount = net ) TO quote_upd.
      ENDIF.
    ENDLOOP.
    CHECK quote_upd IS NOT INITIAL.

    MODIFY ENTITIES OF zrap_r_quote_### IN LOCAL MODE
      ENTITY Quote
        UPDATE FIELDS ( NetAmount ) WITH quote_upd
      REPORTED DATA(upd_reported).

    reported = CORRESPONDING #( DEEP upd_reported ).
  ENDMETHOD.


  METHOD validateCustomer.
    READ ENTITIES OF zrap_r_quote_### IN LOCAL MODE
      ENTITY Quote
        FIELDS ( CustomerID ) WITH CORRESPONDING #( keys )
      RESULT DATA(quotes).
    CHECK quotes IS NOT INITIAL.

    "one SELECT for all instances (no SELECT in the loop)
    SELECT FROM /dmo/customer
      FIELDS customer_id
      FOR ALL ENTRIES IN @quotes
      WHERE customer_id = @quotes-CustomerID
      INTO TABLE @DATA(valid_customers).

    LOOP AT quotes INTO DATA(quote).
      "clear old state messages of this validation first
      APPEND VALUE #( %tky = quote-%tky %state_area = 'VALIDATE_CUSTOMER' ) TO reported-quote.

      IF quote-CustomerID IS INITIAL.
        APPEND VALUE #( %tky = quote-%tky ) TO failed-quote.
        APPEND VALUE #( %tky                = quote-%tky
                        %state_area         = 'VALIDATE_CUSTOMER'
                        %msg                = NEW zcm_rap_###( textid = zcm_rap_###=>enter_customer_id )
                        %element-CustomerID = if_abap_behv=>mk-on ) TO reported-quote.
      ELSEIF NOT line_exists( valid_customers[ customer_id = quote-CustomerID ] ).
        APPEND VALUE #( %tky = quote-%tky ) TO failed-quote.
        APPEND VALUE #( %tky                = quote-%tky
                        %state_area         = 'VALIDATE_CUSTOMER'
                        %msg                = NEW zcm_rap_###( textid      = zcm_rap_###=>customer_unknown
                                                               customer_id = quote-CustomerID )
                        %element-CustomerID = if_abap_behv=>mk-on ) TO reported-quote.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.


  METHOD validateBeforeDelete.
    "keys = instances whose DELETE is about to be saved.
    "They are already gone from the transactional buffer: READ ENTITIES would return them in FAILED.
    "-> check the persisted state (the DB still has the old row until the late save)
    CHECK keys IS NOT INITIAL.

    SELECT FROM zrap_quote_###
      FIELDS quote_uuid, quote_no, status
      FOR ALL ENTRIES IN @keys
      WHERE quote_uuid = @keys-QuoteUUID
      INTO TABLE @DATA(db_quotes).

    LOOP AT db_quotes INTO DATA(db_quote) WHERE status = quote_status-accepted.
      APPEND VALUE #( QuoteUUID = db_quote-quote_uuid ) TO failed-quote.
      "transition message (no %state_area: the instance no longer exists)
      APPEND VALUE #( QuoteUUID = db_quote-quote_uuid
                      %msg      = NEW zcm_rap_###( textid   = zcm_rap_###=>quote_not_deletable
                                                   quote_no = db_quote-quote_no ) ) TO reported-quote.
    ENDLOOP.
  ENDMETHOD.


  METHOD recalcTotal.
    READ ENTITIES OF zrap_r_quote_### IN LOCAL MODE
      ENTITY Quote BY \_Items
        FIELDS ( QuoteUUID LineAmount ) WITH CORRESPONDING #( keys )
      RESULT DATA(items).

    DATA quote_upd TYPE TABLE FOR UPDATE zrap_r_quote_###\\Quote.
    LOOP AT keys INTO DATA(key).
      DATA(total) = REDUCE /dmo/total_price( INIT sum = CONV /dmo/total_price( 0 )
                                             FOR item IN items WHERE ( QuoteUUID = key-QuoteUUID )
                                             NEXT sum = sum + item-LineAmount ).
      APPEND VALUE #( %tky = key-%tky TotalAmount = total ) TO quote_upd.
    ENDLOOP.

    MODIFY ENTITIES OF zrap_r_quote_### IN LOCAL MODE        "TotalAmount is read-only -> local mode
      ENTITY Quote
        UPDATE FIELDS ( TotalAmount ) WITH quote_upd
      FAILED DATA(upd_failed)
      REPORTED DATA(upd_reported).

    failed   = CORRESPONDING #( DEEP upd_failed ).
    reported = CORRESPONDING #( DEEP upd_reported ).
  ENDMETHOD.
```

`lhc_item` 구현부:

```abap
  METHOD calcLineAmount.
    READ ENTITIES OF zrap_r_quote_### IN LOCAL MODE
      ENTITY Item
        FIELDS ( QuoteUUID Quantity UnitPrice LineAmount ) WITH CORRESPONDING #( keys )
      RESULT DATA(items).

    DATA item_upd TYPE TABLE FOR UPDATE zrap_r_quote_###\\Item.
    DATA parents  TYPE SORTED TABLE OF sysuuid_x16 WITH UNIQUE KEY table_line.

    LOOP AT items INTO DATA(item).
      INSERT item-QuoteUUID INTO TABLE parents.            "duplicates are ignored (sy-subrc = 4)
      DATA(amount) = CONV /dmo/total_price( item-Quantity * item-UnitPrice ).
      IF amount <> item-LineAmount.
        APPEND VALUE #( %tky = item-%tky LineAmount = amount ) TO item_upd.
      ENDIF.
    ENDLOOP.

    "internal update (Item) + internal action (Quote): both only reachable IN LOCAL MODE
    MODIFY ENTITIES OF zrap_r_quote_### IN LOCAL MODE
      ENTITY Item
        UPDATE FIELDS ( LineAmount ) WITH item_upd
      ENTITY Quote
        EXECUTE recalcTotal FROM VALUE #( FOR p IN parents ( QuoteUUID = p ) )
      REPORTED DATA(upd_reported).

    reported = CORRESPONDING #( DEEP upd_reported ).
  ENDMETHOD.


  METHOD recalcAfterDelete.
    "deleted items cannot be read from the buffer -> find their parents in the DB
    CHECK keys IS NOT INITIAL.
    SELECT FROM zrap_qitem_###
      FIELDS quote_uuid
      FOR ALL ENTRIES IN @keys
      WHERE item_uuid = @keys-ItemUUID
      INTO TABLE @DATA(parent_rows).                       "FOR ALL ENTRIES removes duplicates
    CHECK parent_rows IS NOT INITIAL.

    "parents deleted in the same transaction (cascading delete) are not found -> skipped
    READ ENTITIES OF zrap_r_quote_### IN LOCAL MODE
      ENTITY Quote
        FIELDS ( QuoteUUID ) WITH VALUE #( FOR row IN parent_rows ( QuoteUUID = row-quote_uuid ) )
      RESULT DATA(parents).
    CHECK parents IS NOT INITIAL.

    MODIFY ENTITIES OF zrap_r_quote_### IN LOCAL MODE
      ENTITY Quote
        EXECUTE recalcTotal FROM VALUE #( FOR parent IN parents ( %tky = parent-%tky ) )
      REPORTED DATA(exec_reported).

    reported = CORRESPONDING #( DEEP exec_reported ).
  ENDMETHOD.
```

콘솔 `s06_triggers`:

```abap
  METHOD s06_triggers.
    SELECT SINGLE FROM /dmo/customer FIELDS customer_id INTO @DATA(customer_id).

    "(1) create -> setDefaults (on modify { create; })
    MODIFY ENTITIES OF zrap_r_quote_###
      ENTITY Quote
        CREATE FIELDS ( CustomerID DiscountPct Note )
        WITH VALUE #( ( %cid = 'Q1' CustomerID = customer_id DiscountPct = 5 Note = 'created in step 6' ) )
      MAPPED DATA(mapped1)
      FAILED DATA(failed1)
      REPORTED DATA(reported1).
    print_failed( title = '(1)' failed = failed1 ).
    COMMIT ENTITIES RESPONSE OF zrap_r_quote_### FAILED DATA(c_failed1) REPORTED DATA(c_reported1).
    print_reported_late( title = '(1)' reported = c_reported1 ).

    IF mapped1-quote IS NOT INITIAL.
      READ ENTITIES OF zrap_r_quote_###
        ENTITY Quote ALL FIELDS WITH VALUE #( ( QuoteUUID = mapped1-quote[ 1 ]-QuoteUUID ) )
        RESULT DATA(created).
      IF created IS NOT INITIAL.
        out->write( |(1) created: Status={ created[ 1 ]-Status } ValidTo={ created[ 1 ]-ValidTo DATE = ISO } | &&
                    |Currency={ created[ 1 ]-CurrencyCode } QuoteNo='{ created[ 1 ]-QuoteNo }'| ).
      ENDIF.
    ENDIF.

    "(2) unknown customer -> validation on save fails, the whole save is rejected
    MODIFY ENTITIES OF zrap_r_quote_###
      ENTITY Quote
        CREATE FIELDS ( CustomerID ) WITH VALUE #( ( %cid = 'Q2' CustomerID = '999999' ) ).
    COMMIT ENTITIES RESPONSE OF zrap_r_quote_### FAILED DATA(c_failed2) REPORTED DATA(c_reported2).
    out->write( |(2) commit sy-subrc={ sy-subrc }| ).
    print_reported_late( title = '(2)' reported = c_reported2 ).
    ROLLBACK ENTITIES.                                      "throw away the rejected buffer

    "(3) delete an accepted quote -> validation on save { delete; }
    DATA(accepted_uuid) = uuid_of( 'Q000000001' ).
    MODIFY ENTITIES OF zrap_r_quote_###
      ENTITY Quote
        DELETE FROM VALUE #( ( QuoteUUID = accepted_uuid ) ).
    COMMIT ENTITIES RESPONSE OF zrap_r_quote_### FAILED DATA(c_failed3) REPORTED DATA(c_reported3).
    out->write( |(3) delete accepted quote: sy-subrc={ sy-subrc }| ).
    print_reported_late( title = '(3)' reported = c_reported3 ).
    ROLLBACK ENTITIES.

    "(4) determine action: determination ( always ) runs although no trigger field changed
    DATA(q3_uuid) = uuid_of( 'Q000000003' ).
    MODIFY ENTITIES OF zrap_r_quote_###
      ENTITY Quote
        EXECUTE refreshQuote FROM VALUE #( ( QuoteUUID = q3_uuid ) )
      FAILED DATA(failed4)
      REPORTED DATA(reported4).
    print_failed( title = '(4)' failed = failed4 ).
    print_reported( title = '(4)' reported = reported4 ).
    COMMIT ENTITIES.
    SELECT SINGLE FROM zrap_quote_### FIELDS total_amount, net_amount
      WHERE quote_uuid = @q3_uuid INTO @DATA(q3_after_refresh).
    out->write( |(4) Q000000003 after refreshQuote: total={ q3_after_refresh-total_amount } | &&
                |net={ q3_after_refresh-net_amount } (expected 180.00)| ).

    "(5) delete one item -> determination on save { delete; } recalculates the header
    READ ENTITIES OF zrap_r_quote_###
      ENTITY Quote BY \_Items
        FIELDS ( ItemNo ) WITH VALUE #( ( QuoteUUID = q3_uuid ) )
      RESULT DATA(q3_items).
    SORT q3_items BY ItemNo DESCENDING.
    IF q3_items IS NOT INITIAL.
      MODIFY ENTITIES OF zrap_r_quote_###
        ENTITY Item
          DELETE FROM VALUE #( ( ItemUUID = q3_items[ 1 ]-ItemUUID ) ).
      COMMIT ENTITIES.
    ENDIF.
    SELECT SINGLE FROM zrap_quote_### FIELDS total_amount, net_amount
      WHERE quote_uuid = @q3_uuid INTO @DATA(q3_after_delete).
    out->write( |(5) Q000000003 after item delete: total={ q3_after_delete-total_amount } | &&
                |net={ q3_after_delete-net_amount } (expected 120.00 / 108.00)| ).
  ENDMETHOD.
```

**왜 이렇게 쓰나**
- **`on save { delete; }`의 핵심**: `keys`에 들어오는 인스턴스는 이미 버퍼에서 "삭제됨" 상태입니다. 그래서 `READ ENTITIES`로는 읽을 수 없고(결과 없음, `failed`에 not found), 저장 전 **DB에 남은 옛 값**을 `SELECT`로 봐야 합니다. 같은 트랜잭션에서 만들고 바로 지운 인스턴스는 DB에도 없으니 검사할 것도 없습니다. 저장이 아직 안 된 시점이므로 DB 값 = "삭제 직전의 영구 상태"입니다.
- 검증이 삭제를 거부하면 **저장 전체가 거부**됩니다(cheat sheet 36: all-or-nothing). 삭제 요청은 버퍼에 남아 있으므로 소비자는 `ROLLBACK ENTITIES`로 버리거나 다른 방법으로 고쳐야 합니다. 그래서 콘솔에서 (2), (3) 뒤에 `ROLLBACK ENTITIES`를 씁니다.
- 삭제 거부 메시지는 `%state_area` 없이 **전이 메시지**로 냅니다. 상태 메시지는 "고칠 때까지 인스턴스에 붙어 있는" 메시지인데, 삭제된 인스턴스에는 붙일 곳이 없습니다.
- **`determination ( always )`**: 결정은 원래 트리거 조건(생성, 지정 필드 변경)이 맞을 때만 실행됩니다. determine action에서 `( always )`를 붙이면 조건을 무시하고 실행됩니다(cheat sheet 36 "Determine actions"). 공식 Feature Showcase의 `determine action updateTimes { determination ( always ) updateTimesChildCreated; }`와 같은 쓰임입니다. "규칙이 바뀌어서 전부 다시 계산" 같은 재계산 버튼에 좋습니다. determine action에는 핸들러 메서드가 없습니다. 프레임워크가 지정된 결정·검증을 순서대로(결정 먼저, 그다음 검증) 부릅니다.
- **`internal` 연산과 `IN LOCAL MODE`**: `internal update`, `internal create`(연관), `internal action`은 BO 바깥에는 아예 없는 연산입니다. BO 안에서도 `IN LOCAL MODE` 없이 부르면 "외부 소비자"처럼 취급되어 쓸 수 없습니다. `IN LOCAL MODE`는 기능 제어·권한 검사도 건너뛰므로 읽기 전용 필드(`Status`, `TotalAmount`)를 핸들러가 직접 바꿀 수 있습니다.
- 결정 연쇄: 품목 삭제 → `recalcAfterDelete`(on save) → `recalcTotal`이 `TotalAmount` 변경 → `calcNetAmount`(on save, 트리거 `field TotalAmount`) 실행. 저장 시퀀스의 finalize 단계에서 on save 결정이 다른 on save 결정을 다시 일으킬 수 있다는 것을 (5)에서 확인합니다(실행 순서는 보장되지 않으므로 서로 순서에 기대는 로직은 피하세요).
- **클래스 구조 해설**: `validation validateBeforeDelete on save { delete; }` 한 줄에서 `FOR VALIDATE ON SAVE IMPORTING keys FOR Quote~validateBeforeDelete`가 생기고, 이 메서드의 `keys`는 삭제 대상 키, `failed`/`reported`는 저장 단계(early save)의 응답입니다. 프레임워크는 `COMMIT ENTITIES` 때 finalize 단계에서 on save 결정을, check_before_save 단계에서 검증을 부릅니다.

**자주 나는 오류와 해결**
- (3)에서 삭제가 그냥 성공함 → `validation ... on save { delete; }` 대신 `{ create; }`만 적었거나, `SELECT`에서 상태 비교 값이 `'A'`가 아닌지 확인하세요. 데모 데이터 클래스를 다시 실행해 `Q000000001`의 상태를 `A`로 돌려놓으세요.
- `calcLineAmount`에서 "operation UPDATE is not allowed" 류의 런타임 오류 → `IN LOCAL MODE`를 빠뜨렸습니다. `internal update`는 local mode에서만 허용됩니다.
- 같은 콘솔을 여러 번 돌리면 (4), (5)의 기대값이 달라집니다(품목이 계속 줄어듦). 매번 `ZCL_RAP_R14_DATA_###`부터 다시 실행하세요.

</details>

#### 7단계. deep 파라미터·deep table 파라미터·deep 결과와 `%control`

요구사항

1. 액션 `importItems`(**deep parameter**)를 구현하세요.
   - `%param`의 헤더 필드(`ValidTo`, `Note`)는 **호출자가 보낸 것만**(`%param-%control-필드 = mk-on`) 견적에 반영합니다.
   - `%param-_Items`의 각 줄에 대해: `ProductID`가 비었거나 `Quantity <= 0`이면 그 견적은 실패(`failed`) + 143번 메시지(줄 번호), 그 견적의 품목은 하나도 만들지 않습니다.
   - 단가는 **보냈으면 그 값(0 포함), 안 보냈으면(`%control-UnitPrice = mk-off`) 기본 단가 100.00**을 씁니다.
   - 품목 번호는 기존 최대 번호 다음부터. 통화는 견적 통화. 품목 생성은 내부 연산 `CREATE BY \_Items`(local mode).
   - 결과는 변경 후 견적 전체(`result [1] $self`).
2. 정적 함수 `checkImport`(**deep table parameter**): `%param`이 **표**입니다. 각 항목(헤더)의 각 품목을 검사해 줄마다 `ZRAP_A_QCHECK_###` 한 줄(`EntryIndex`, `ItemIndex`, `IsValid`, `MessageText`)을 돌려줍니다. 품목이 없는 항목은 `ItemIndex = 0`, `IsValid = false`. `ValidTo`가 과거인 항목의 품목은 모두 invalid.
3. 함수 `simulatePricing`(**deep result**): 견적의 품목별 할인·순액 줄(`_Lines`)과 헤더 합계를 계층형 결과로 돌려줍니다. DB나 버퍼는 바꾸지 않습니다.
4. 콘솔 `s07_deep`: (1) `Q000000003`에 품목 2줄 가져오기(한 줄은 단가 생략) → 커밋 → 품목·합계 출력, (2) `ProductID`의 `%control`을 끈 줄이 있는 호출 → `mandatory : execute` 때문에 실패하는지 출력, (3) `checkImport`에 항목 2개(정상 1, 품목 없는 것 1) → 결과 줄 출력, (4) `simulatePricing` 결과(헤더 + 줄) 출력.

**확인**
- (1) 후 `Q000000003` 품목에 `P-400`(단가 50.00), `P-500`(단가 **100.00**, 기본값)이 추가되고, 합계·순액이 다시 계산됩니다(데모 데이터를 새로 만든 직후라면 합계 200 + 2×50 + 1×100 = 400.00, 순액 360.00). `ValidTo`는 바뀌고 `Note`는 그대로입니다.
- (2)는 `failed`에 견적이 들어오거나(프레임워크의 `mandatory : execute` 검사) 런타임 메시지가 나옵니다. 어떤 형태로 거부되는지 실제 출력으로 확인해 주석에 적으세요(실제 시스템에서 확인 필요).
- (3) 출력 예: `entry 1 item 1 valid=X OK`, `entry 1 item 2 valid=  Product and quantity > 0 required`, `entry 2 item 0 valid=  No items`.
- (4) 출력 예: `total=400.00 discount=10.00 net=360.00`와 줄마다 `item 001 P-200 120.00 -12.00 = 108.00` …

<details><summary>정답·해설</summary>

`lhc_quote` 구현부:

```abap
  METHOD importItems.
    "current state: currency + existing item numbers
    READ ENTITIES OF zrap_r_quote_### IN LOCAL MODE
      ENTITY Quote
        FIELDS ( CurrencyCode ) WITH CORRESPONDING #( keys )
      RESULT DATA(quotes)
      ENTITY Quote BY \_Items
        FIELDS ( QuoteUUID ItemNo ) WITH CORRESPONDING #( keys )
      RESULT DATA(existing_items).

    DATA quote_upd TYPE TABLE FOR UPDATE zrap_r_quote_###\\Quote.
    DATA item_cba  TYPE TABLE FOR CREATE zrap_r_quote_###\\Quote\_Items.
    DATA cba_line  LIKE LINE OF item_cba.
    DATA cid_no    TYPE i.

    LOOP AT keys INTO DATA(key).
      READ TABLE quotes WITH KEY id COMPONENTS %tky = key-%tky INTO DATA(quote).
      IF sy-subrc <> 0.
        APPEND VALUE #( %tky = key-%tky %fail-cause = if_abap_behv=>cause-not_found ) TO failed-quote.
        CONTINUE.
      ENDIF.

      "(a) check all lines first: one bad line rejects the whole import for this quote
      DATA(line_ok) = abap_true.
      LOOP AT key-%param-_Items INTO DATA(line).
        DATA(line_no) = sy-tabix.
        IF line-ProductID IS INITIAL OR line-Quantity <= 0.
          line_ok = abap_false.
          APPEND VALUE #( %tky = key-%tky
                          %msg = NEW zcm_rap_###( textid  = zcm_rap_###=>import_line_invalid
                                                  line_no = line_no ) ) TO reported-quote.
        ENDIF.
      ENDLOOP.
      IF line_ok = abap_false.
        APPEND VALUE #( %tky = key-%tky ) TO failed-quote.
        CONTINUE.
      ENDIF.

      "(b) header: take over only the fields the caller really sent (%control of the deep parameter)
      IF key-%param-%control-ValidTo = if_abap_behv=>mk-on
      OR key-%param-%control-Note    = if_abap_behv=>mk-on.
        APPEND VALUE #( %tky             = key-%tky
                        ValidTo          = key-%param-ValidTo
                        Note             = key-%param-Note
                        %control-ValidTo = key-%param-%control-ValidTo
                        %control-Note    = key-%param-%control-Note ) TO quote_upd.
      ENDIF.

      "(c) items: next item number, default price when UnitPrice was not sent
      DATA(next_no) = REDUCE i( INIT max = 0
                                FOR existing IN existing_items WHERE ( QuoteUUID = key-QuoteUUID )
                                NEXT max = nmax( val1 = max val2 = CONV i( existing-ItemNo ) ) ).
      CLEAR cba_line.
      cba_line-%tky = key-%tky.
      LOOP AT key-%param-_Items INTO line.
        next_no += 1.
        cid_no  += 1.
        APPEND VALUE #( %cid         = |IMP{ cid_no }|
                        ItemNo       = next_no
                        ProductID    = line-ProductID
                        Quantity     = line-Quantity
                        UnitPrice    = COND #( WHEN line-%control-UnitPrice = if_abap_behv=>mk-on
                                               THEN line-UnitPrice
                                               ELSE c_default_price )
                        CurrencyCode = quote-CurrencyCode ) TO cba_line-%target.
      ENDLOOP.
      APPEND cba_line TO item_cba.
    ENDLOOP.

    "header update (FROM: %control already set above) + internal create-by-association
    MODIFY ENTITIES OF zrap_r_quote_### IN LOCAL MODE
      ENTITY Quote
        UPDATE FROM quote_upd
        CREATE BY \_Items
          FIELDS ( ItemNo ProductID Quantity UnitPrice CurrencyCode ) WITH item_cba
      FAILED DATA(mod_failed)
      REPORTED DATA(mod_reported).

    LOOP AT mod_failed-quote INTO DATA(mf).
      APPEND VALUE #( %tky = mf-%tky %fail-cause = mf-%fail-cause ) TO failed-quote.
    ENDLOOP.
    LOOP AT mod_reported-item INTO DATA(mr).
      APPEND VALUE #( %tky = mr-%tky %msg = mr-%msg ) TO reported-item.
    ENDLOOP.

    "result [1] $self: the quote after the import (only successful ones)
    READ ENTITIES OF zrap_r_quote_### IN LOCAL MODE
      ENTITY Quote
        ALL FIELDS WITH CORRESPONDING #( keys )
      RESULT DATA(after).
    LOOP AT after INTO DATA(a).
      CHECK NOT line_exists( failed-quote[ %tky = a-%tky ] ).
      APPEND VALUE #( %tky = a-%tky %param = CORRESPONDING #( a ) ) TO result.
    ENDLOOP.
  ENDMETHOD.


  METHOD checkImport.
    "static function + deep TABLE parameter: %param is a table of hierarchical entries
    DATA(today) = cl_abap_context_info=>get_system_date( ).

    LOOP AT keys INTO DATA(key).
      LOOP AT key-%param INTO DATA(entry).
        DATA(entry_index) = sy-tabix.

        IF entry-_Items IS INITIAL.
          APPEND VALUE #( %cid   = key-%cid
                          %param = VALUE #( EntryIndex  = entry_index
                                            ItemIndex   = 0
                                            IsValid     = abap_false
                                            MessageText = 'No items' ) ) TO result.
          CONTINUE.
        ENDIF.

        DATA(entry_date_ok) = xsdbool( entry-ValidTo IS INITIAL OR entry-ValidTo >= today ).

        LOOP AT entry-_Items INTO DATA(item).
          DATA(item_index) = sy-tabix.
          DATA(ok) = xsdbool( entry_date_ok = abap_true
                              AND item-ProductID IS NOT INITIAL
                              AND item-Quantity > 0
                              AND item-UnitPrice >= 0 ).
          APPEND VALUE #( %cid   = key-%cid                 "[0..*]: many result lines for one call
                          %param = VALUE #( EntryIndex  = entry_index
                                            ItemIndex   = item_index
                                            IsValid     = ok
                                            MessageText = COND #( WHEN ok = abap_true THEN 'OK'
                                                                  WHEN entry_date_ok = abap_false THEN 'Valid-to date is in the past'
                                                                  ELSE 'Product and quantity > 0 required' ) ) ) TO result.
        ENDLOOP.
      ENDLOOP.
    ENDLOOP.
  ENDMETHOD.


  METHOD simulatePricing.
    READ ENTITIES OF zrap_r_quote_### IN LOCAL MODE
      ENTITY Quote
        FIELDS ( DiscountPct CurrencyCode ) WITH CORRESPONDING #( keys )
      RESULT DATA(quotes)
      ENTITY Quote BY \_Items
        FIELDS ( QuoteUUID ItemNo ProductID LineAmount ) WITH CORRESPONDING #( keys )
      RESULT DATA(items).

    SORT items BY QuoteUUID ItemNo.

    LOOP AT quotes INTO DATA(quote).
      "deep result: header fields + table _Lines (component name = association name)
      APPEND VALUE #( %tky   = quote-%tky
                      %param = VALUE #( DiscountPct  = quote-DiscountPct
                                        CurrencyCode = quote-CurrencyCode
                                        _Lines       = VALUE #( FOR item IN items WHERE ( QuoteUUID = quote-QuoteUUID )
                                                                ( ItemNo       = item-ItemNo
                                                                  ProductID    = item-ProductID
                                                                  LineAmount   = item-LineAmount
                                                                  LineDiscount = item-LineAmount * quote-DiscountPct / 100
                                                                  LineNet      = item-LineAmount
                                                                                 - item-LineAmount * quote-DiscountPct / 100 ) ) ) )
             TO result ASSIGNING FIELD-SYMBOL(<sim>).

      LOOP AT <sim>-%param-_Lines INTO DATA(sim_line).
        <sim>-%param-TotalAmount += sim_line-LineAmount.
        <sim>-%param-NetAmount   += sim_line-LineNet.
      ENDLOOP.
    ENDLOOP.
  ENDMETHOD.
```

콘솔 `s07_deep`:

```abap
  METHOD s07_deep.
    DATA(q3_uuid) = uuid_of( 'Q000000003' ).
    DATA(today)   = cl_abap_context_info=>get_system_date( ).

    "(1) deep parameter with explicit %control (FROM):
    "    header: ValidTo sent, Note NOT sent / items: 2nd line without UnitPrice
    MODIFY ENTITIES OF zrap_r_quote_###
      ENTITY Quote
        EXECUTE importItems
        FROM VALUE #( ( QuoteUUID = q3_uuid
                        %param    = VALUE #( ValidTo          = today + 60
                                             Note             = 'must be ignored'
                                             %control-ValidTo = if_abap_behv=>mk-on
                                             %control-Note    = if_abap_behv=>mk-off
                                             %control-_Items  = if_abap_behv=>mk-on    "association flag (실제 시스템에서 확인 필요)
                                             _Items = VALUE #(
                                               ( ProductID = 'P-400' Quantity = 2 UnitPrice = '50.00'
                                                 %control-ProductID = if_abap_behv=>mk-on
                                                 %control-Quantity  = if_abap_behv=>mk-on
                                                 %control-UnitPrice = if_abap_behv=>mk-on )
                                               ( ProductID = 'P-500' Quantity = 1
                                                 %control-ProductID = if_abap_behv=>mk-on
                                                 %control-Quantity  = if_abap_behv=>mk-on
                                                 %control-UnitPrice = if_abap_behv=>mk-off ) ) ) ) )
      RESULT DATA(import_result)
      FAILED DATA(failed1)
      REPORTED DATA(reported1).
    print_failed( title = '(1)' failed = failed1 ).
    print_reported( title = '(1)' reported = reported1 ).
    COMMIT ENTITIES.

    READ ENTITIES OF zrap_r_quote_###
      ENTITY Quote
        FIELDS ( ValidTo Note TotalAmount NetAmount ) WITH VALUE #( ( QuoteUUID = q3_uuid ) )
      RESULT DATA(q3)
      ENTITY Quote BY \_Items
        FIELDS ( ItemNo ProductID Quantity UnitPrice LineAmount ) WITH VALUE #( ( QuoteUUID = q3_uuid ) )
      RESULT DATA(q3_items).
    IF q3 IS NOT INITIAL.
      out->write( |(1) ValidTo={ q3[ 1 ]-ValidTo DATE = ISO } Note={ q3[ 1 ]-Note } | &&
                  |total={ q3[ 1 ]-TotalAmount } net={ q3[ 1 ]-NetAmount }| ).
    ENDIF.
    SORT q3_items BY ItemNo.
    LOOP AT q3_items INTO DATA(it).
      out->write( |    { it-ItemNo } { it-ProductID } { it-Quantity } x { it-UnitPrice } = { it-LineAmount }| ).
    ENDLOOP.

    "(2) mandatory : execute -> ProductID flag is off
    MODIFY ENTITIES OF zrap_r_quote_###
      ENTITY Quote
        EXECUTE importItems
        FROM VALUE #( ( QuoteUUID = q3_uuid
                        %param    = VALUE #( %control-_Items = if_abap_behv=>mk-on
                                             _Items = VALUE #( ( ProductID = 'P-600' Quantity = 1
                                                                 %control-ProductID = if_abap_behv=>mk-off
                                                                 %control-Quantity  = if_abap_behv=>mk-on ) ) ) ) )
      FAILED DATA(failed2)
      REPORTED DATA(reported2).
    out->write( |(2) failed lines: { lines( failed2-quote ) }| ).
    print_reported( title = '(2)' reported = reported2 ).
    ROLLBACK ENTITIES.

    "(3) static function with deep TABLE parameter
    READ ENTITIES OF zrap_r_quote_###
      ENTITY Quote
        EXECUTE checkImport
        FROM VALUE #( ( %cid   = 'CHK'
                        %param = VALUE #(
                          ( ValidTo = today + 10
                            %control-ValidTo = if_abap_behv=>mk-on
                            %control-_Items  = if_abap_behv=>mk-on
                            _Items = VALUE #( ( ProductID = 'P-700' Quantity = 1 UnitPrice = 10
                                                %control-ProductID = if_abap_behv=>mk-on
                                                %control-Quantity  = if_abap_behv=>mk-on
                                                %control-UnitPrice = if_abap_behv=>mk-on )
                                              ( ProductID = 'P-800' Quantity = 0
                                                %control-ProductID = if_abap_behv=>mk-on
                                                %control-Quantity  = if_abap_behv=>mk-on ) ) )
                          ( Note = 'entry without items'
                            %control-Note   = if_abap_behv=>mk-on
                            %control-_Items = if_abap_behv=>mk-on ) ) ) )
      RESULT DATA(check_result).
    LOOP AT check_result INTO DATA(chk).
      out->write( |(3) entry { chk-%param-EntryIndex } item { chk-%param-ItemIndex } | &&
                  |valid={ chk-%param-IsValid } { chk-%param-MessageText }| ).
    ENDLOOP.

    "(4) deep result
    READ ENTITIES OF zrap_r_quote_###
      ENTITY Quote
        EXECUTE simulatePricing FROM VALUE #( ( QuoteUUID = q3_uuid ) )
      RESULT DATA(sim_result).
    LOOP AT sim_result INTO DATA(sim).
      out->write( |(4) total={ sim-%param-TotalAmount } discount={ sim-%param-DiscountPct } | &&
                  |net={ sim-%param-NetAmount } { sim-%param-CurrencyCode }| ).
      LOOP AT sim-%param-_Lines INTO DATA(sl).
        out->write( |    item { sl-ItemNo } { sl-ProductID } { sl-LineAmount } -{ sl-LineDiscount } = { sl-LineNet }| ).
      ENDLOOP.
    ENDLOOP.
  ENDMETHOD.
```

`FIELDS ( ... ) WITH`로 deep 파라미터의 `%control`을 채우는 변형(릴리스 7.89 뉴스: "The FIELDS ( ... ) WITH addition for READ and MODIFY supports the setting of %control regarding components in deep input parameters"). 정확한 필드 목록 형태(헤더 필드와 자식 연관을 함께 적는지, 자식 줄의 필드를 어떻게 지정하는지)는 로컬 예제로 확인하지 못했습니다(실제 시스템에서 확인 필요). ADT에서 `EXECUTE importItems` 다음에 `FIELDS`를 입력하고 `Ctrl+Space`, `F1`로 확인해 보세요. 예상 형태:

```abap
    "(실제 시스템에서 확인 필요) - %control is derived from the field list instead of being set by hand
    MODIFY ENTITIES OF zrap_r_quote_###
      ENTITY Quote
        EXECUTE importItems
        FIELDS ( ValidTo _Items ) WITH VALUE #( ( QuoteUUID = q3_uuid
                                                 %param = VALUE #( ValidTo = today + 60
                                                                   _Items  = VALUE #( ( ProductID = 'P-900' Quantity = 1 ) ) ) ) )
      FAILED DATA(failed_fields).
```

**왜 이렇게 쓰나**
- **deep parameter의 모양**: `keys`의 한 줄 = `%tky`(대상 견적) + `%param`(계층형 구조). `%param`에는 헤더 필드, `%control`(with control이므로), 그리고 자식 표 `_Items`가 있습니다. `_Items`의 각 줄에도 자기 `%control`이 있습니다. F2로 `keys`를 열면 이 중첩 구조가 그대로 보입니다.
- **deep table parameter**: `%param` 자체가 **표**입니다(계층형 구조의 표). 그래서 `LOOP AT key-%param INTO entry` → `LOOP AT entry-_Items` 이중 루프가 됩니다. 이 문제는 같은 추상 BDEF `ZRAP_A_QIMPORT_###`를 `deep parameter`(구조 하나)와 `deep table parameter`(표) 양쪽에 재사용합니다.
- **deep result**: `result-%param`이 계층형 구조이고 자식 표 컴포넌트 이름은 연관 이름(`_Lines`)입니다. 결과용 추상 BDEF에는 `with control`이 없어도 됩니다. 변형으로 `deep result selective [1] ZRAP_A_PRICESIM_###`(cheat sheet 36의 `act16`, 7.89)를 쓰면 8단계처럼 `REQUEST` 파라미터로 요청된 부분만 채울 수 있습니다.
- **`%control`을 읽는 이유**: 평면 파라미터는 "값이 0/공백인 것"과 "보내지 않은 것"을 구별할 수 없습니다. `with control`이 있으면 `%control-UnitPrice = mk-off`로 "보내지 않음"을 알 수 있어, 단가 0(무상)과 단가 미지정(기본 단가)을 다르게 처리할 수 있습니다. 헤더도 같은 원리로 `UPDATE FROM`에 `%control`을 그대로 넘겨 "보낸 필드만" 갱신합니다.
- **`mandatory : execute`**: 호출 시 값이 필수인 필드입니다. 이 검사가 프레임워크에서 언제 어떤 응답으로 되는지는 로컬 예제로 확인하지 못했습니다. 그래서 핸들러에서도 같은 조건(`ProductID` 비었음)을 직접 다시 검사해 143번 메시지를 냅니다(이중 안전장치).
- **함수는 읽기 연산**: `simulatePricing`, `checkImport`는 `READ ENTITIES ... EXECUTE`로 부르고, 버퍼를 바꾸지 않으며 잠금도 걸지 않습니다. 결과를 계산해 돌려주기만 합니다.
- **클래스 구조 해설**: `deep parameter ZRAP_A_QIMPORT_###` 한 줄이 `keys`의 `%param` 타입을 추상 BDEF의 계층형 파생 타입으로 바꿉니다. 메서드 시그니처 자체(`FOR MODIFY IMPORTING keys FOR ACTION Quote~importItems RESULT result`)는 평면 파라미터 액션과 같습니다. 다른 것은 `%param`의 모양뿐입니다.

**자주 나는 오류와 해결**
- `key-%param-%control-ValidTo`에서 "component %CONTROL does not exist" → 추상 BDEF에 `with control`이 없습니다(4단계).
- `key-%param-_Items`에서 "component _ITEMS does not exist" → 추상 BDEF 헤더의 `with hierarchy;` 또는 루트 BDEF의 `association _Items;`가 빠졌습니다.
- `%control-_Items`에서 문법 오류 → 연관용 `%control` 컴포넌트 이름은 로컬 예제로 확인하지 못했습니다. F2로 `%param-%control`의 컴포넌트를 확인하세요. 없다면 그 줄만 지우면 됩니다(실제 시스템에서 확인 필요).
- `READ TABLE quotes WITH KEY id COMPONENTS %tky = ...`에서 오류 → 읽기 결과 표의 보조 키 `id`(= `%tky`)는 BDEF 파생 타입이 자동으로 만들어 줍니다. 오타가 없는지, `%tky`를 썼는지 확인하세요.

</details>

#### 8단계. 결과 변형: `result selective`·`[0..1] entity`·정적 액션 `[0..*]`·외부 이름

요구사항

1. 액션 `recalcPrices`(`result selective [1] $self`): 모든 품목의 `LineAmount`를 다시 계산하고(내부 update) `recalcTotal`을 실행한 뒤, **`requested_fields`가 표시한 필드만** 결과에 채웁니다.
2. 함수 `getCheapestItem`(`result [0..1] entity ZRAP_R_QUOTEITEM_###`): 단가가 가장 낮은 품목 하나를 돌려줍니다. 품목이 없으면 **결과 줄이 없습니다**.
3. 정적 액션 `closeExpired`(`result [0..*] $self`): DB에서 유효일이 지난 `N` 상태 견적을 찾아 상태를 `X`로 바꾸고, 바뀐 견적 전부를 결과로 돌려줍니다. 호출 한 번(`%cid` 하나)에 결과 여러 줄입니다.
4. 액션 `acceptQuote`(외부 이름 `'Accept'`, `result [1] $self`): 번호 없는 견적은 141, 만료(`X` 또는 유효일 지남)는 146으로 거부. 성공하면 상태 `A`와 성공 메시지 142.
5. 콘솔 `s08_results`: (1) `recalcPrices` 결과 출력, (2) `getCheapestItem`을 품목 있는 견적과 없는 견적(`Q000000002`)에 함께 실행해 결과 줄 수 출력, (3) `closeExpired` 실행·커밋, (4) `acceptQuote`를 `Q000000003`, `Q000000002`에 실행·커밋.

**확인**
- (2) `getCheapestItem for 2 quotes -> 1 line(s)` — `[0..1]`이므로 품목 없는 견적은 줄이 없습니다.
- (3) `closeExpired closed 1 quote(s)`와 `Q000000002 status X` (데모 데이터 직후 기준).
- (4) `Quote Q000000003 has been accepted.`와 `Quote Q000000002 has expired and cannot be accepted.`, `failed`에 `Q000000002` 한 줄.
- (1)의 출력에서 어떤 필드가 채워지고 어떤 필드가 비어 있는지 보고, `requested_fields`를 F2로 열어 타입을 주석에 적으세요.

<details><summary>정답·해설</summary>

```abap
  METHOD recalcPrices.
    "1) line amounts (internal update) + header total (internal action)
    READ ENTITIES OF zrap_r_quote_### IN LOCAL MODE
      ENTITY Quote BY \_Items
        FIELDS ( Quantity UnitPrice LineAmount ) WITH CORRESPONDING #( keys )
      RESULT DATA(items).

    DATA item_upd TYPE TABLE FOR UPDATE zrap_r_quote_###\\Item.
    LOOP AT items INTO DATA(item).
      DATA(amount) = CONV /dmo/total_price( item-Quantity * item-UnitPrice ).
      IF amount <> item-LineAmount.
        APPEND VALUE #( %tky = item-%tky LineAmount = amount ) TO item_upd.
      ENDIF.
    ENDLOOP.

    MODIFY ENTITIES OF zrap_r_quote_### IN LOCAL MODE
      ENTITY Item
        UPDATE FIELDS ( LineAmount ) WITH item_upd
      ENTITY Quote
        EXECUTE recalcTotal FROM CORRESPONDING #( keys )
      FAILED DATA(mod_failed)
      REPORTED DATA(mod_reported).

    failed   = CORRESPONDING #( DEEP mod_failed ).
    reported = CORRESPONDING #( DEEP mod_reported ).

    "2) result selective: read and return only what the consumer asked for.
    "   requested_fields flags the requested result fields like a %control structure
    "   (exact component path: F2 on requested_fields - 실제 시스템에서 확인 필요)
    READ ENTITIES OF zrap_r_quote_### IN LOCAL MODE
      ENTITY Quote
        FROM VALUE #( FOR key IN keys
                      ( %tky     = key-%tky
                        %control = CORRESPONDING #( requested_fields ) ) )
      RESULT DATA(quotes).

    result = VALUE #( FOR quote IN quotes ( %tky = quote-%tky %param = CORRESPONDING #( quote ) ) ).
  ENDMETHOD.


  METHOD getCheapestItem.
    READ ENTITIES OF zrap_r_quote_### IN LOCAL MODE
      ENTITY Quote BY \_Items
        ALL FIELDS WITH CORRESPONDING #( keys )
      RESULT DATA(items).

    SORT items BY QuoteUUID UnitPrice.

    LOOP AT keys INTO DATA(key).
      LOOP AT items INTO DATA(item) WHERE QuoteUUID = key-QuoteUUID.
        "result entity ZRAP_R_QUOTEITEM_### : %param has the ITEM structure
        APPEND VALUE #( %tky = key-%tky %param = CORRESPONDING #( item ) ) TO result.
        EXIT.                                             "[0..1]: at most one line per quote
      ENDLOOP.
    ENDLOOP.
  ENDMETHOD.


  METHOD closeExpired.
    "static action: keys contain only %cid (no instance) -> find the instances ourselves
    DATA(today) = cl_abap_context_info=>get_system_date( ).

    SELECT FROM zrap_quote_###
      FIELDS quote_uuid
      WHERE valid_to < @today
        AND status   = @quote_status-new
      INTO TABLE @DATA(expired).
    CHECK expired IS NOT INITIAL.                         "[0..*]: an empty result is valid

    MODIFY ENTITIES OF zrap_r_quote_### IN LOCAL MODE
      ENTITY Quote
        UPDATE FIELDS ( Status )
        WITH VALUE #( FOR e IN expired ( QuoteUUID = e-quote_uuid Status = quote_status-expired ) )
      FAILED DATA(upd_failed)
      REPORTED DATA(upd_reported).

    reported = CORRESPONDING #( DEEP upd_reported ).

    READ ENTITIES OF zrap_r_quote_### IN LOCAL MODE
      ENTITY Quote
        ALL FIELDS WITH VALUE #( FOR e IN expired ( QuoteUUID = e-quote_uuid ) )
      RESULT DATA(closed).

    "one call (%cid) -> many result lines
    LOOP AT keys INTO DATA(key).
      LOOP AT closed INTO DATA(quote) WHERE Status = quote_status-expired.
        APPEND VALUE #( %cid = key-%cid %param = CORRESPONDING #( quote ) ) TO result.
      ENDLOOP.
    ENDLOOP.
  ENDMETHOD.


  METHOD acceptQuote.
    READ ENTITIES OF zrap_r_quote_### IN LOCAL MODE
      ENTITY Quote
        FIELDS ( QuoteNo Status ValidTo ) WITH CORRESPONDING #( keys )
      RESULT DATA(quotes).

    DATA(today) = cl_abap_context_info=>get_system_date( ).
    DATA quote_upd TYPE TABLE FOR UPDATE zrap_r_quote_###\\Quote.

    LOOP AT quotes INTO DATA(quote).
      IF quote-QuoteNo IS INITIAL.
        APPEND VALUE #( %tky = quote-%tky ) TO failed-quote.
        APPEND VALUE #( %tky = quote-%tky
                        %msg = NEW zcm_rap_###( textid = zcm_rap_###=>quote_not_saved ) ) TO reported-quote.
        CONTINUE.
      ENDIF.
      IF quote-Status = quote_status-expired OR quote-ValidTo < today.
        APPEND VALUE #( %tky = quote-%tky ) TO failed-quote.
        APPEND VALUE #( %tky = quote-%tky
                        %msg = NEW zcm_rap_###( textid   = zcm_rap_###=>quote_expired
                                                quote_no = quote-QuoteNo ) ) TO reported-quote.
        CONTINUE.
      ENDIF.

      APPEND VALUE #( %tky = quote-%tky Status = quote_status-accepted ) TO quote_upd.
      APPEND VALUE #( %tky = quote-%tky
                      %msg = NEW zcm_rap_###( textid   = zcm_rap_###=>quote_accepted
                                              quote_no = quote-QuoteNo
                                              severity = if_abap_behv_message=>severity-success ) ) TO reported-quote.
    ENDLOOP.

    CHECK quote_upd IS NOT INITIAL.

    MODIFY ENTITIES OF zrap_r_quote_### IN LOCAL MODE
      ENTITY Quote
        UPDATE FIELDS ( Status ) WITH quote_upd
      FAILED DATA(upd_failed).

    READ ENTITIES OF zrap_r_quote_### IN LOCAL MODE
      ENTITY Quote
        ALL FIELDS WITH CORRESPONDING #( quote_upd )
      RESULT DATA(after).

    result = VALUE #( FOR a IN after ( %tky = a-%tky %param = CORRESPONDING #( a ) ) ).
  ENDMETHOD.
```

콘솔 `s08_results`:

```abap
  METHOD s08_results.
    DATA(q3_uuid) = uuid_of( 'Q000000003' ).
    DATA(q2_uuid) = uuid_of( 'Q000000002' ).

    "(1) result selective
    MODIFY ENTITIES OF zrap_r_quote_###
      ENTITY Quote
        EXECUTE recalcPrices FROM VALUE #( ( QuoteUUID = q3_uuid ) )
      RESULT DATA(recalc_result)
      FAILED DATA(failed1).
    print_failed( title = '(1)' failed = failed1 ).
    LOOP AT recalc_result INTO DATA(rr).
      out->write( |(1) recalcPrices: QuoteNo='{ rr-%param-QuoteNo }' total='{ rr-%param-TotalAmount }' | &&
                  |customer='{ rr-%param-CustomerID }'| ).
    ENDLOOP.
    COMMIT ENTITIES.

    "(2) result [0..1] entity: 1 line for a quote with items, 0 lines without items
    READ ENTITIES OF zrap_r_quote_###
      ENTITY Quote
        EXECUTE getCheapestItem FROM VALUE #( ( QuoteUUID = q3_uuid ) ( QuoteUUID = q2_uuid ) )
      RESULT DATA(cheapest).
    out->write( |(2) getCheapestItem for 2 quotes -> { lines( cheapest ) } line(s)| ).
    LOOP AT cheapest INTO DATA(ch).
      out->write( |    { ch-%param-ItemNo } { ch-%param-ProductID } unit price { ch-%param-UnitPrice }| ).
    ENDLOOP.

    "(3) static (non-factory) action with result [0..*] $self
    MODIFY ENTITIES OF zrap_r_quote_###
      ENTITY Quote
        EXECUTE closeExpired FROM VALUE #( ( %cid = 'CLOSE' ) )
      RESULT DATA(closed)
      FAILED DATA(failed3).
    print_failed( title = '(3)' failed = failed3 ).
    out->write( |(3) closeExpired closed { lines( closed ) } quote(s)| ).
    LOOP AT closed INTO DATA(cl).
      out->write( |    { cl-%param-QuoteNo } status { cl-%param-Status }| ).
    ENDLOOP.
    COMMIT ENTITIES.

    "(4) external 'Accept' only renames the OData action - EML uses acceptQuote
    MODIFY ENTITIES OF zrap_r_quote_###
      ENTITY Quote
        EXECUTE acceptQuote FROM VALUE #( ( QuoteUUID = q3_uuid ) ( QuoteUUID = q2_uuid ) )
      RESULT DATA(accepted)
      FAILED DATA(failed4)
      REPORTED DATA(reported4).
    out->write( |(4) accepted: { lines( accepted ) }| ).
    print_failed( title = '(4)' failed = failed4 ).
    print_reported( title = '(4)' reported = reported4 ).
    COMMIT ENTITIES.
  ENDMETHOD.
```

**왜 이렇게 쓰나**
- **`result selective`**: 결과 엔터티가 크고 소비자가 일부(예: 키나 합계)만 필요할 때, 제공자가 필요한 필드만 계산·읽도록 하는 표시입니다. cheat sheet 36: "`selective`: Returns only parts of the result, such as just the keys. When used, the corresponding handler method includes the input parameter `REQUEST ...` to mark the desired fields." 그래서 이 메서드에만 `REQUEST requested_fields`가 붙습니다. 위 코드는 그 표시를 `%control`로 넘겨 **요청된 필드만 읽는** 가장 짧은 구현입니다. OData에서는 액션 결과에 대한 `$select`가 이 요청으로 들어옵니다(일반적인 OData 동작, 실제 시스템에서 확인 필요). EML 소비자가 결과 필드를 지정하는 방법은 로컬 자료에 없어 다루지 않았습니다. 지정하지 않았을 때 `requested_fields`가 "전부"인지 "키만"인지 (1) 출력으로 확인하세요.
- **결과 카디널리티**: `[1]` 인스턴스마다 정확히 한 줄, `[0..1]` 없거나 한 줄, `[0..*]` 몇 줄이든, `[1..*]` 한 줄 이상. 인스턴스 연산은 `%tky`로, 정적 연산은 `%cid`로 결과 줄을 호출 줄과 연결합니다.
- **`result entity 다른엔터티`**: 결과 타입이 자기 엔터티(`$self`)가 아니라 다른 엔터티입니다. `%param`이 품목 구조이므로 `%param-ProductID`처럼 씁니다. cheat sheet 36: "`entity some_entity`: Specifies that the result type corresponds to another CDS view entity."
- **정적 비팩토리 액션**: 인스턴스가 없는 연산이라 `keys`에 `%tky`가 없고 `%cid`만 있습니다. 대상은 핸들러가 직접 찾습니다(여기서는 DB SELECT). 따라서 **아직 저장되지 않은 버퍼 속 견적은 찾지 못합니다**. 이것이 의도와 맞는지 늘 따져 보세요. 새 인스턴스를 만들지 않으므로 `factory`가 아니고 `mapped`를 채우지 않습니다.
- **`external 'Accept'`**: 외부(OData) 이름만 바꿉니다. 핸들러, EML, 기능 제어(`%action-acceptQuote`)는 모두 내부 이름을 씁니다. 12단계에서 서비스 메타데이터에 `Accept`가 보이는 것을 확인합니다. Feature Showcase의 `default function GetDefaultsForChild external 'GetDefaultsForCreateByAssociation'`도 같은 기능입니다.
- **클래스 구조 해설**: `action recalcPrices result selective [1] $self` → `FOR MODIFY IMPORTING keys REQUEST requested_fields FOR ACTION Quote~recalcPrices RESULT result`. `function getCheapestItem result [0..1] entity ...` → `FOR READ ... FOR FUNCTION ... RESULT result`(결과 `%param` 타입 = 품목). `static action closeExpired result [0..*] $self` → `keys`의 줄 타입에 `%cid`만 있고 `%tky`가 없습니다.

**자주 나는 오류와 해결**
- `%control = CORRESPONDING #( requested_fields )`에서 문법 오류 → `requested_fields`의 컴포넌트가 다른 경로(예: 한 단계 더 안쪽)에 있는 경우입니다. F2로 타입을 열고 `%control`에 대응하는 하위 구조를 `CORRESPONDING`의 원본으로 쓰세요(실제 시스템에서 확인 필요). 정 안 되면 `ALL FIELDS`로 읽고 그대로 돌려줘도 계약 위반은 아닙니다(요청보다 많이 주는 것일 뿐).
- (3)이 0건 → 데모 데이터를 다시 만들지 않아 `Q000000002`가 이미 `X`입니다.
- (4)에서 `Q000000003`이 141(번호 없음)로 거부 → 데모 데이터 견적은 번호가 있으므로 정상이라면 나오지 않습니다. 6·7단계에서 만든 **새 견적**은 10단계 전까지 번호가 없어 141이 나옵니다.

</details>

#### 9단계. 다중 결과 팩토리 액션: 정적 `[0..*]`, 인스턴스 `[1..*]`

요구사항

1. 정적 팩토리 액션 `createForCustomer`(`parameter ZRAP_A_QCREATE_###`, `[0..*]`): 파라미터의 `NumberOfQuotes`만큼 같은 고객의 빈 견적을 만듭니다. 0이면 아무것도 만들지 않고 **오류도 아닙니다**. 10을 넘으면 그 호출은 `failed`(`cause-unspecific`).
2. 인스턴스 팩토리 액션 `splitByItem`(`[1..*]`): 원본 견적의 **품목마다 새 견적 하나**를 만들고(고객·유효일·할인·통화 복사), 그 품목 하나를 새 견적의 품목 1번으로 복사합니다. 품목이 없으면 `failed` + 144번(`[1..*]`이므로 0개 생성은 계약 위반).
3. 두 액션 모두 내부적으로 만든 인스턴스를 `mapped-quote`에 **호출자의 `%cid`**로 돌려줍니다(한 `%cid`에 여러 줄).
4. 콘솔 `s09_factory`: (1) `createForCustomer`를 `NumberOfQuotes = 3`(`%cid = 'NEW3'`)과 `0`(`%cid = 'NEW0'`)으로 한 번에 호출해 `%cid`별 `mapped` 줄 수 출력·커밋, (2) `splitByItem`을 `Q000000003`과 (1)에서 만든 빈 견적에 실행해 `mapped`/`failed` 출력·커밋.

**확인**
- (1) `NEW3 -> 3 mapped, NEW0 -> 0 mapped, failed 0`
- (2) `SPLIT_Q3 -> n mapped`(n = `Q000000003`의 현재 품목 수), `SPLIT_EMPTY`는 `failed`와 `The quote has no items. Nothing to split.`
- Data Preview로 `zrap_quote_###`를 보면 새 견적들이 생겼고, 새로 생긴 견적마다 품목이 정확히 1개입니다.

<details><summary>정답·해설</summary>

```abap
  METHOD createForCustomer.
    TYPES: BEGIN OF ty_cid_map,
             inner TYPE abp_behv_cid,
             outer TYPE abp_behv_cid,
           END OF ty_cid_map.
    DATA cid_map TYPE HASHED TABLE OF ty_cid_map WITH UNIQUE KEY inner.
    DATA creates TYPE TABLE FOR CREATE zrap_r_quote_###\\Quote.
    DATA counter TYPE i.

    DATA(today) = cl_abap_context_info=>get_system_date( ).

    LOOP AT keys INTO DATA(key).
      IF key-%param-NumberOfQuotes > c_max_new_quotes.
        APPEND VALUE #( %cid = key-%cid %fail-cause = if_abap_behv=>cause-unspecific ) TO failed-quote.
        CONTINUE.
      ENDIF.
      "NumberOfQuotes = 0 -> nothing to do, allowed by [0..*]
      DO key-%param-NumberOfQuotes TIMES.
        counter += 1.
        DATA(inner_cid) = CONV abp_behv_cid( |CFC{ counter }| ).
        INSERT VALUE #( inner = inner_cid outer = key-%cid ) INTO TABLE cid_map.
        APPEND VALUE #( %cid       = inner_cid
                        CustomerID = key-%param-CustomerID
                        ValidTo    = COND #( WHEN key-%param-ValidTo IS INITIAL THEN today + 30
                                             ELSE key-%param-ValidTo ) ) TO creates.
      ENDDO.
    ENDLOOP.
    CHECK creates IS NOT INITIAL.

    MODIFY ENTITIES OF zrap_r_quote_### IN LOCAL MODE
      ENTITY Quote
        CREATE FIELDS ( CustomerID ValidTo ) WITH creates
      MAPPED DATA(create_mapped)
      FAILED DATA(create_failed)
      REPORTED DATA(create_reported).

    "map every created instance back to the CALLER's %cid -> several lines per %cid
    LOOP AT create_mapped-quote INTO DATA(created).
      READ TABLE cid_map WITH TABLE KEY inner = created-%cid INTO DATA(map).
      IF sy-subrc = 0.
        APPEND VALUE #( %cid = map-outer %key = created-%key ) TO mapped-quote.
      ENDIF.
    ENDLOOP.

    LOOP AT create_failed-quote INTO DATA(cf).
      READ TABLE cid_map WITH TABLE KEY inner = cf-%cid INTO map.
      IF sy-subrc = 0.
        APPEND VALUE #( %cid = map-outer %fail-cause = cf-%fail-cause ) TO failed-quote.
      ENDIF.
    ENDLOOP.
    reported = CORRESPONDING #( DEEP create_reported ).
  ENDMETHOD.


  METHOD splitByItem.
    TYPES: BEGIN OF ty_cid_map,
             inner TYPE abp_behv_cid,
             outer TYPE abp_behv_cid,
           END OF ty_cid_map.
    DATA cid_map TYPE HASHED TABLE OF ty_cid_map WITH UNIQUE KEY inner.
    DATA creates TYPE TABLE FOR CREATE zrap_r_quote_###\\Quote.
    DATA cbas    TYPE TABLE FOR CREATE zrap_r_quote_###\\Quote\_Items.
    DATA counter TYPE i.

    READ ENTITIES OF zrap_r_quote_### IN LOCAL MODE
      ENTITY Quote
        FIELDS ( CustomerID ValidTo DiscountPct CurrencyCode ) WITH CORRESPONDING #( keys )
      RESULT DATA(quotes)
      ENTITY Quote BY \_Items
        FIELDS ( QuoteUUID ProductID Quantity UnitPrice CurrencyCode ) WITH CORRESPONDING #( keys )
      RESULT DATA(items).

    LOOP AT keys INTO DATA(key).
      READ TABLE quotes WITH KEY id COMPONENTS %tky = key-%tky INTO DATA(source).
      IF sy-subrc <> 0.
        APPEND VALUE #( %tky = key-%tky %fail-cause = if_abap_behv=>cause-not_found ) TO failed-quote.
        CONTINUE.
      ENDIF.

      "[1..*]: creating nothing would break the contract -> fail with a message
      IF NOT line_exists( items[ QuoteUUID = key-QuoteUUID ] ).
        APPEND VALUE #( %tky = key-%tky %fail-cause = if_abap_behv=>cause-unspecific ) TO failed-quote.
        APPEND VALUE #( %tky = key-%tky
                        %msg = NEW zcm_rap_###( textid = zcm_rap_###=>quote_no_items ) ) TO reported-quote.
        CONTINUE.
      ENDIF.

      LOOP AT items INTO DATA(item) WHERE QuoteUUID = key-QuoteUUID.
        counter += 1.
        DATA(inner_cid) = CONV abp_behv_cid( |SPL{ counter }| ).
        INSERT VALUE #( inner = inner_cid outer = key-%cid ) INTO TABLE cid_map.

        APPEND VALUE #( %cid         = inner_cid
                        CustomerID   = source-CustomerID
                        ValidTo      = source-ValidTo
                        DiscountPct  = source-DiscountPct
                        CurrencyCode = source-CurrencyCode ) TO creates.

        APPEND VALUE #( %cid_ref = inner_cid                 "parent created in the same request
                        %target  = VALUE #( ( %cid         = |{ inner_cid }I|
                                              ItemNo       = 1
                                              ProductID    = item-ProductID
                                              Quantity     = item-Quantity
                                              UnitPrice    = item-UnitPrice
                                              CurrencyCode = item-CurrencyCode ) ) ) TO cbas.
      ENDLOOP.
    ENDLOOP.
    CHECK creates IS NOT INITIAL.

    "create + internal create-by-association in one local-mode request
    MODIFY ENTITIES OF zrap_r_quote_### IN LOCAL MODE
      ENTITY Quote
        CREATE FIELDS ( CustomerID ValidTo DiscountPct CurrencyCode ) WITH creates
        CREATE BY \_Items
          FIELDS ( ItemNo ProductID Quantity UnitPrice CurrencyCode ) WITH cbas
      MAPPED DATA(create_mapped)
      FAILED DATA(create_failed)
      REPORTED DATA(create_reported).

    LOOP AT create_mapped-quote INTO DATA(created).
      READ TABLE cid_map WITH TABLE KEY inner = created-%cid INTO DATA(map).
      IF sy-subrc = 0.
        APPEND VALUE #( %cid = map-outer %key = created-%key ) TO mapped-quote.
      ENDIF.
    ENDLOOP.
    reported = CORRESPONDING #( DEEP create_reported ).
  ENDMETHOD.
```

콘솔 `s09_factory`:

```abap
  METHOD s09_factory.
    SELECT SINGLE FROM /dmo/customer FIELDS customer_id INTO @DATA(customer_id).

    "(1) static factory action [0..*]
    MODIFY ENTITIES OF zrap_r_quote_###
      ENTITY Quote
        EXECUTE createForCustomer
        FROM VALUE #( ( %cid = 'NEW3' %param-CustomerID = customer_id %param-NumberOfQuotes = 3 )
                      ( %cid = 'NEW0' %param-CustomerID = customer_id %param-NumberOfQuotes = 0 ) )
      MAPPED DATA(mapped1)
      FAILED DATA(failed1)
      REPORTED DATA(reported1).

    DATA(n3) = REDUCE i( INIT n = 0 FOR m IN mapped1-quote WHERE ( %cid = 'NEW3' ) NEXT n = n + 1 ).
    DATA(n0) = REDUCE i( INIT n = 0 FOR m IN mapped1-quote WHERE ( %cid = 'NEW0' ) NEXT n = n + 1 ).
    out->write( |(1) NEW3 -> { n3 } mapped, NEW0 -> { n0 } mapped, failed { lines( failed1-quote ) }| ).

    DATA empty_uuid TYPE sysuuid_x16.
    IF mapped1-quote IS NOT INITIAL.
      empty_uuid = mapped1-quote[ 1 ]-QuoteUUID.            "a new quote without items
    ENDIF.
    COMMIT ENTITIES.

    "(2) instance factory action [1..*]
    DATA(q3_uuid) = uuid_of( 'Q000000003' ).
    MODIFY ENTITIES OF zrap_r_quote_###
      ENTITY Quote
        EXECUTE splitByItem
        FROM VALUE #( ( %cid = 'SPLIT_Q3'    QuoteUUID = q3_uuid )
                      ( %cid = 'SPLIT_EMPTY' QuoteUUID = empty_uuid ) )
      MAPPED DATA(mapped2)
      FAILED DATA(failed2)
      REPORTED DATA(reported2).

    DATA(n_split) = REDUCE i( INIT n = 0 FOR m IN mapped2-quote WHERE ( %cid = 'SPLIT_Q3' ) NEXT n = n + 1 ).
    out->write( |(2) SPLIT_Q3 -> { n_split } mapped| ).
    print_failed( title = '(2)' failed = failed2 ).
    print_reported( title = '(2)' reported = reported2 ).
    COMMIT ENTITIES.
  ENDMETHOD.
```

**왜 이렇게 쓰나**
- **다중 결과 팩토리**(릴리스 7.96, 2405): 예전 팩토리 액션은 `[1]`만 가능했습니다. 이제 `[0..*]`(0개 이상), `[1..*]`(1개 이상)로 한 번의 호출로 여러 인스턴스를 만들 수 있습니다. cheat sheet 36: "`[0..*]` (creates none or any number of instances), `[1..*]` (creates any number of instances, but at least one)." 팩토리 액션에는 `result`를 쓸 수 없고, 만든 인스턴스는 `mapped`로만 알려 줍니다.
- **`%cid` 두 겹**: 핸들러 안에서 실제 생성(`MODIFY ... IN LOCAL MODE ... CREATE`)에 쓰는 `%cid`(`CFC1`, `SPL1` …)는 핸들러가 지어낸 내부 값입니다. 소비자는 자기가 보낸 `%cid`(`NEW3`)로 결과를 찾으므로, `cid_map`으로 **내부 → 호출자 `%cid`**를 바꿔 `mapped-quote`에 넣습니다. 같은 `%cid`에 여러 줄이 들어가는 것이 다중 결과 팩토리의 모양입니다.
- **`[0..*]`와 `[1..*]`의 차이를 코드로**: `createForCustomer`는 0개를 만들어도 정상 종료합니다. `splitByItem`은 품목이 없으면 0개가 되므로 `failed`로 거부해 계약(`1..*`)을 지킵니다.
- **`%cid_ref`**: 같은 요청에서 방금 만든 부모(`inner_cid`)에 자식을 붙일 때 씁니다(R-12 deep create와 같은 원리). 품목 생성은 `internal create`이므로 local mode가 필수입니다.
- 새 견적에도 `setDefaults`(on modify)가 돌아 상태 `N`이 들어가고, 품목 생성으로 `calcLineAmount` → `recalcTotal`이 이어집니다. 팩토리 액션도 일반 생성과 똑같이 결정을 일으킵니다.
- **클래스 구조 해설**: 팩토리 액션 메서드에는 `RESULT`가 없고 대신 암시적 `mapped` 응답이 있습니다. 정적 팩토리(`static factory action`)의 `keys`에는 `%cid`와 `%param`만, 인스턴스 팩토리(`factory action`)의 `keys`에는 `%cid`와 `%tky`가 있습니다.

**자주 나는 오류와 해결**
- `abp_behv_cid`를 모른다는 오류 → `%cid` 컴포넌트의 타입 이름입니다. 없다고 나오면 `TYPE string`으로 바꾸고 `CONV`를 지우세요(실제 시스템에서 확인 필요).
- 소비자 쪽 `mapped1-quote`가 비었는데 DB에는 견적이 생김 → `mapped-quote`에 넣을 때 내부 `%cid`를 그대로 넣었습니다. 호출자 `%cid`로 바꿔야 합니다.
- (2)에서 `SPLIT_EMPTY`가 `failed`에 없음 → (1)이 0건을 만들어 `empty_uuid`가 비었거나, 품목이 있는 견적을 골랐습니다.

</details>

#### 10단계. save action: `save ( finalize )`로 저장할 때 견적 번호 매기기, `save ( adjustnumbers )`

요구사항

1. save action `assignQuoteNo`를 구현하세요. 대상 견적 중 `QuoteNo`가 빈 것에 `Q` + 9자리 연속 번호(DB의 최댓값 다음부터)를 넣고, 각 견적에 145번 성공 메시지를 붙입니다.
2. 세이버 `finalize`에서 `lcl_buffer=>new_quotes`에 기록된 견적 중 **아직 버퍼에 있는 것만** 골라 `assignQuoteNo`를 EML(`IN LOCAL MODE`)로 실행하세요.
3. `save_modified`(additional save)는 추가로 쓸 것이 없으므로 버퍼만 비웁니다. `cleanup_finalize`는 저장이 거부되어 상호작용 단계로 돌아갈 때 불립니다. 이때 버퍼를 비우면 안 되는 이유를 주석에 쓰세요.
4. 콘솔 `s10_save_action`: (1) 견적을 만들고 `COMMIT ENTITIES RESPONSE OF ... REPORTED`로 145번 메시지 출력 → 다시 읽어 `QuoteNo` 출력, (2) 같은 save action을 상호작용 단계에서 직접 부르는 줄을 주석으로 넣고, 주석을 풀었을 때 무슨 일이 생기는지 확인해 적으세요.
5. 해설의 `save ( adjustnumbers )` 내용을 읽고, late numbering BO에서 어디에 무엇을 쓸지 답하세요(이 BO에서는 활성화하지 않습니다).

**확인**
- (1) `Quote number Q000000004 has been assigned.`(데모 3건 뒤 첫 번호. 앞 단계에서 만든 견적이 있으면 더 큰 번호)와 `QuoteNo=Q00000000n`.
- Data Preview에서 이 단계 이전에 만든 견적(번호 빈 것)은 여전히 비어 있고, 이 단계 이후 만든 견적만 번호가 있습니다. (이전 견적에도 번호를 주려면 그 견적을 아무 필드나 바꿔 저장해도 **안 됩니다**. `setDefaults`는 create에서만 기록하기 때문입니다. 왜 그런지 설명할 수 있어야 합니다.)
- (2) 주석을 풀면 활성화 단계 또는 실행 단계에서 거부됩니다(정확한 형태는 실제 시스템에서 확인 필요).

<details><summary>정답·해설</summary>

```abap
  METHOD assignQuoteNo.
    "save action: only callable during the saver method named in the BDEF (finalize)
    READ ENTITIES OF zrap_r_quote_### IN LOCAL MODE
      ENTITY Quote
        FIELDS ( QuoteNo ) WITH CORRESPONDING #( keys )
      RESULT DATA(quotes).
    DELETE quotes WHERE QuoteNo IS NOT INITIAL.
    CHECK quotes IS NOT INITIAL.

    "simplified numbering: highest number in the DB + 1 (production: number range object, see R-04)
    SELECT SINGLE FROM zrap_quote_###
      FIELDS MAX( quote_no )
      INTO @DATA(max_no).
    DATA(last_no) = COND i( WHEN max_no IS INITIAL THEN 0 ELSE CONV i( max_no+1(9) ) ).

    DATA quote_upd TYPE TABLE FOR UPDATE zrap_r_quote_###\\Quote.
    LOOP AT quotes INTO DATA(quote).
      last_no += 1.
      DATA(new_no) = CONV zrap_quote_###-quote_no( |Q{ last_no WIDTH = 9 ALIGN = RIGHT PAD = '0' }| ).
      APPEND VALUE #( %tky = quote-%tky QuoteNo = new_no ) TO quote_upd.
      APPEND VALUE #( %tky = quote-%tky
                      %msg = NEW zcm_rap_###( textid   = zcm_rap_###=>quote_no_assigned
                                              quote_no = new_no
                                              severity = if_abap_behv_message=>severity-success ) ) TO reported-quote.
    ENDLOOP.

    MODIFY ENTITIES OF zrap_r_quote_### IN LOCAL MODE        "QuoteNo is read-only -> local mode
      ENTITY Quote
        UPDATE FIELDS ( QuoteNo ) WITH quote_upd
      FAILED DATA(upd_failed).

    failed = CORRESPONDING #( DEEP upd_failed ).
  ENDMETHOD.
```

세이버:

```abap
CLASS lsc_zrap_r_quote_### IMPLEMENTATION.

  METHOD finalize.
    "early save phase: modifications of the BO are still allowed here
    CHECK lcl_buffer=>new_quotes IS NOT INITIAL.

    "only quotes that still exist (created and deleted again / rolled back -> not found)
    READ ENTITIES OF zrap_r_quote_### IN LOCAL MODE
      ENTITY Quote
        FIELDS ( QuoteNo ) WITH VALUE #( FOR uuid IN lcl_buffer=>new_quotes ( QuoteUUID = uuid ) )
      RESULT DATA(quotes).
    CHECK quotes IS NOT INITIAL.

    "the save action is executed like any other action - but only allowed in finalize
    MODIFY ENTITIES OF zrap_r_quote_### IN LOCAL MODE
      ENTITY Quote
        EXECUTE assignQuoteNo FROM VALUE #( FOR q IN quotes ( %tky = q-%tky ) )
      FAILED DATA(exec_failed)
      REPORTED DATA(exec_reported).

    failed   = CORRESPONDING #( DEEP exec_failed ).
    reported = CORRESPONDING #( DEEP exec_reported ).
  ENDMETHOD.


  METHOD save_modified.
    "nothing extra to persist: 'with additional save' is used here only to get a saver
    "whose finalize runs our save action. The transaction is finished -> reset the buffer.
    lcl_buffer=>clear( ).
  ENDMETHOD.


  METHOD cleanup_finalize.
    "finalize/check_before_save failed -> back to the interaction phase.
    "Do NOT clear lcl_buffer=>new_quotes: the quotes are still new and must get
    "their number on the next successful COMMIT ENTITIES.
  ENDMETHOD.

ENDCLASS.
```

콘솔 `s10_save_action`:

```abap
  METHOD s10_save_action.
    SELECT SINGLE FROM /dmo/customer FIELDS customer_id INTO @DATA(customer_id).

    "(1) create -> COMMIT -> saver finalize -> save action assignQuoteNo
    MODIFY ENTITIES OF zrap_r_quote_###
      ENTITY Quote
        CREATE FIELDS ( CustomerID ) WITH VALUE #( ( %cid = 'S1' CustomerID = customer_id ) )
      MAPPED DATA(mapped1).
    COMMIT ENTITIES RESPONSE OF zrap_r_quote_### FAILED DATA(c_failed1) REPORTED DATA(c_reported1).
    print_reported_late( title = '(1)' reported = c_reported1 ).

    IF mapped1-quote IS NOT INITIAL.
      READ ENTITIES OF zrap_r_quote_###
        ENTITY Quote
          FIELDS ( QuoteNo ) WITH VALUE #( ( QuoteUUID = mapped1-quote[ 1 ]-QuoteUUID ) )
        RESULT DATA(saved).
      IF saved IS NOT INITIAL.
        out->write( |(1) QuoteNo={ saved[ 1 ]-QuoteNo }| ).
      ENDIF.
    ENDIF.

    "(2) a save action is not available in the interaction phase.
    "uncomment and observe (activation error or runtime rejection - 실제 시스템에서 확인 필요)
    "MODIFY ENTITIES OF zrap_r_quote_###
    "  ENTITY Quote
    "    EXECUTE assignQuoteNo FROM VALUE #( ( QuoteUUID = mapped1-quote[ 1 ]-QuoteUUID ) )
    "  FAILED DATA(failed2).
  ENDMETHOD.
```

**`save ( adjustnumbers )` — late numbering BO에서 쓰는 형태(이 BO에는 넣지 않음)**

```bdef
// late numbering BO (예: R-01/R-04 의 Travel) 에서만 의미가 있음
//   save ( adjustnumbers ) action stampNumbers;          // adjust_numbers 세이버 메서드에서만 실행 가능
//   save ( finalize, adjustnumbers ) action doBoth;      // 두 단계 모두에서 실행 가능
```

```abap
  "saver of a late-numbering BO (sketch, 실제 시스템에서 확인 필요)
  METHOD adjust_numbers.
    "1) assign the final keys and fill MAPPED (%pre -> %key), see R-04
    "2) then execute the save action that needs the final numbers, e.g.
    "MODIFY ENTITIES OF zrap_r_travel_### IN LOCAL MODE
    "  ENTITY Travel
    "    EXECUTE stampNumbers FROM VALUE #( FOR m IN mapped-travel ( %pky = m-%pre ) ).
  ENDMETHOD.
```

**왜 이렇게 쓰나**
- **save action이란**: cheat sheet 36의 정의는 "Defines save actions callable only during specific RAP saver methods. The parentheses can include `finalize` and/or `adjustnumbers`."입니다. 단계 지정은 릴리스 7.89(2208) 뉴스 "RAP save actions can now specify one or both of the RAP saver methods finalize or adjustnumbers in brackets to indicate the RAP saver method during which the action can be executed."에 나옵니다. 즉 **세이버의 그 메서드 안에서 EML로만 실행**할 수 있고, 소비자(Fiori, EML)는 상호작용 단계에서 부를 수 없습니다.
- **일반 결정(on save)과 무엇이 다른가**: on save 결정은 트리거 조건으로 프레임워크가 알아서 부르고, 여러 결정의 순서가 정해져 있지 않습니다(cheat sheet 36 "the execution order of multiple specified determinations is arbitrary"). save action은 **세이버가 원하는 시점에 명시적으로** 부릅니다. "번호는 저장이 확정될 때 한 번만, 정해진 자리에서" 같은 규칙에 맞습니다. 단, 대상 인스턴스는 핸들러가 직접 정해야 하므로 `lcl_buffer`처럼 "이번 트랜잭션에서 무엇이 새로 생겼는지"를 기록해 둘 장치가 필요합니다.
- **왜 late numbering을 쓰지 않았나**: 키는 UUID(managed numbering)로 바로 정해지고, 사람이 읽는 번호만 저장 시점에 붙입니다. late numbering(R-04)은 **키 자체**를 늦게 정해야 할 때 씁니다. `save ( adjustnumbers )`는 그런 BO의 `adjust_numbers`에서 "최종 키가 정해진 뒤에 해야 하는 일"을 액션으로 분리할 때 씁니다. 이 BO에는 `adjust_numbers` 메서드가 없으므로 넣으면 의미가 없습니다.
- **`cleanup_finalize`에서 버퍼를 지우지 않는 이유**: 검증 오류로 저장이 거부되면 인스턴스는 버퍼에 남고 소비자가 고친 뒤 다시 `COMMIT`합니다. 그때도 번호가 붙어야 하므로 기록을 남겨 둡니다. `ROLLBACK ENTITIES`로 버려진 인스턴스의 UUID가 남아도 `finalize`의 `READ`가 걸러 냅니다.
- **MAX+1 번호의 한계**: 동시에 두 사용자가 저장하면 같은 번호가 나올 수 있습니다. 실무에서는 번호 범위 객체(`cl_numberrange_runtime`, R-04)를 쓰세요. 여기서는 save action 문법에 집중하려고 단순화했습니다.
- **클래스 구조 해설**: `save ( finalize ) action assignQuoteNo;`에서 생기는 핸들러 메서드는 일반 액션과 같은 `FOR MODIFY IMPORTING keys FOR ACTION Quote~assignQuoteNo`입니다. 다른 것은 **누가, 언제 부르느냐**뿐입니다. 프레임워크는 `COMMIT ENTITIES` → `finalize`(세이버) → 그 안의 EML → `assignQuoteNo`(핸들러) 순서로 부릅니다.

**자주 나는 오류와 해결**
- `finalize REDEFINITION`이 거부됨("method cannot be redefined" 류) → managed BO 세이버에서 `finalize` 재정의가 허용되는지는 로컬 예제로 확인하지 못했습니다(R-04 해설도 같은 내용). 거부되면 대안으로 `determination assignNumber on save { create; }`를 만들고 그 안에서 `assignQuoteNo`와 같은 로직을 실행하세요. 이 경우 save action 자체는 시연할 수 없으므로 BDEF에 정의만 남겨 두고, 어떤 오류가 났는지 기록해 두세요(실제 시스템에서 확인 필요).
- (1)에 145번 메시지가 안 보임 → 성공 메시지가 저장 응답에 실리는지는 시스템 동작에 따라 다를 수 있습니다. 번호(`QuoteNo`)가 들어갔다면 save action은 정상 실행된 것입니다.
- 번호가 비어 있음 → `setDefaults`에서 `lcl_buffer=>new_quotes`에 넣는 줄이 빠졌거나, 세이버 클래스 이름이 BDEF의 행동 풀과 다른 파일에 있습니다(세이버는 행동 풀 **로컬 클래스**여야 합니다).

</details>

#### 11단계. 대체 키(alternative key)와 key function

요구사항

1. **확인된 문법으로 먼저**: 정적 함수 `findByQuoteNo`(파라미터 `ZRAP_A_QUOTENO_###`, `result [0..1] $self`)를 구현하세요. 견적 번호(대체 키)로 견적을 찾아 돌려주고, 없으면 결과 줄이 없습니다. DB에서 UUID를 찾은 뒤 **BO를 통해**(`READ ENTITIES IN LOCAL MODE`) 읽어 버퍼의 최신 상태를 돌려줍니다.
2. **최신 문법으로 다시**: 해설을 읽고 BDEF에 대체 키(pure key `QuoteNoKey` = `QuoteNo`, secondary key `CustomerStatusKey` = `CustomerID` + `Status`)와 key function `GetByQuoteNo`를 추가해 보세요. 이 부분의 문법은 로컬 자료로 확인하지 못했습니다. ADT의 코드 완성과 F1로 정확한 형태를 찾아 맞추는 것이 이 요구사항의 일부입니다. 활성화하지 못하면 그 줄을 주석으로 남기고 어떤 오류가 났는지 적으세요.
3. 콘솔 `s11_key`: `findByQuoteNo`를 `Q000000001`(`%cid = 'K1'`)과 없는 번호 `Q999999999`(`%cid = 'K2'`)로 한 번에 실행하고 결과를 출력하세요.

**확인**
- `K1 -> Q000000001 customer <번호> status A`, `K2 found: ` (빈 값 = 없음)
- (2를 해냈다면) key function도 같은 결과를 냅니다.

<details><summary>정답·해설</summary>

```abap
  METHOD findByQuoteNo.
    "lookup by the alternative key QuoteNo (confirmed syntax: static function with a parameter)
    DATA quote_nos TYPE SORTED TABLE OF zrap_quote_###-quote_no WITH NON-UNIQUE KEY table_line.
    quote_nos = VALUE #( FOR k IN keys WHERE ( %param-QuoteNo IS NOT INITIAL ) ( k-%param-QuoteNo ) ).
    CHECK quote_nos IS NOT INITIAL.

    SELECT FROM zrap_quote_###
      FIELDS quote_uuid
      FOR ALL ENTRIES IN @quote_nos
      WHERE quote_no = @quote_nos-table_line
      INTO TABLE @DATA(hits).
    CHECK hits IS NOT INITIAL.

    "read through the BO: the transactional buffer state wins over the DB
    READ ENTITIES OF zrap_r_quote_### IN LOCAL MODE
      ENTITY Quote
        ALL FIELDS WITH VALUE #( FOR h IN hits ( QuoteUUID = h-quote_uuid ) )
      RESULT DATA(quotes).

    LOOP AT keys INTO DATA(key).
      LOOP AT quotes INTO DATA(quote) WHERE QuoteNo = key-%param-QuoteNo.
        APPEND VALUE #( %cid = key-%cid %param = CORRESPONDING #( quote ) ) TO result.
        EXIT.                                             "[0..1]
      ENDLOOP.
    ENDLOOP.
  ENDMETHOD.
```

콘솔 `s11_key`:

```abap
  METHOD s11_key.
    READ ENTITIES OF zrap_r_quote_###
      ENTITY Quote
        EXECUTE findByQuoteNo
        FROM VALUE #( ( %cid = 'K1' %param-QuoteNo = 'Q000000001' )
                      ( %cid = 'K2' %param-QuoteNo = 'Q999999999' ) )
      RESULT DATA(found).

    LOOP AT found INTO DATA(f).
      out->write( |{ f-%cid } -> { f-%param-QuoteNo } customer { f-%param-CustomerID } status { f-%param-Status }| ).
    ENDLOOP.
    out->write( |K2 found: { xsdbool( line_exists( found[ %cid = 'K2' ] ) ) }| ).

    "key function variant (only after step 11-2 activated; 실제 시스템에서 확인 필요)
    "READ ENTITIES OF zrap_r_quote_###
    "  ENTITY Quote
    "    EXECUTE GetByQuoteNo FROM VALUE #( ( %cid = 'KF1' %param-QuoteNo = 'Q000000001' ) )
    "  RESULT DATA(found_kf).
  ENDMETHOD.
```

대체 키와 key function — **형태 추정, 실제 시스템에서 확인 필요**(로컬 예제·cheat sheet에 BDL 코드가 없습니다):

```bdef
  // ---- inside define behavior for ZRAP_R_QUOTE_### alias Quote { ... } -----------------
  // BDEF alternative keys (managed/unmanaged: 9.12 / 2408)          (실제 시스템에서 확인 필요)
  //   pure key      : only defines the signature of a key function
  //   secondary key : additionally becomes a secondary table key of the BDEF derived types
  // key ( pure )      QuoteNoKey        { QuoteNo; }
  // key ( secondary ) CustomerStatusKey { CustomerID; Status; }
  //
  // RAP key function (7.96 / 2405): input = values of an alternative key, output = matching instances
  // key function GetByQuoteNo key QuoteNoKey result [0..1] $self;
```

```abap
    "handler for the key function - signature as generated by ADT (실제 시스템에서 확인 필요)
    "METHODS GetByQuoteNo FOR READ
    "  IMPORTING keys FOR FUNCTION Quote~GetByQuoteNo RESULT result.
    "Implementation: same logic as findByQuoteNo (lookup by QuoteNo, read IN LOCAL MODE, fill result).
```

**왜 이렇게 쓰나**
- **대체 키**: 기본 키(여기서는 UUID) 말고도 인스턴스를 하나로 가리킬 수 있는 필드 묶음입니다. 사용자는 UUID를 모르고 견적 번호를 압니다. 릴리스 뉴스 9.12: "BDEF pure keys and BDEF secondary keys are now available. They define the signature of a RAP key function." 즉 대체 키를 BDEF에 선언하는 목적은 **key function의 입력 모양을 정하는 것**입니다. secondary key는 이름 그대로 파생 타입에 보조 테이블 키로도 생긴다는 뜻으로 읽힙니다(9.14 뉴스 "Using Custom Secondary Table Keys in BDEF Derived Types"와 함께 실제 시스템에서 확인 필요).
- **key function**: 릴리스 뉴스 7.96: "A RAP key function is defined with reference to a BDEF alternative key and it returns the entity instances with matching values." cheat sheet 36: "These functions are commonly used in cross-BO association contexts." R-11의 cross-BO 연관에서 다른 BO가 이 BO를 업무 키로 찾을 때 쓰는 표준 입구가 됩니다.
- **왜 정적 함수 대용을 먼저 만드나**: 같은 일(업무 키 → 인스턴스)을 **확인된 문법**(`static function ... parameter ... result [0..1] $self`)으로 할 수 있기 때문입니다. key function은 프레임워크가 그 의미("이 함수는 대체 키 조회다")를 알 수 있다는 점이 다릅니다. 시스템에서 key function 문법을 확인하면 구현은 그대로 옮기면 됩니다.
- **DB 조회 + BO 읽기**: 견적 번호는 저장 시점(10단계)에 붙으므로 버퍼에만 있는 새 견적에는 번호가 없습니다. 그래서 번호로 찾는 대상은 항상 DB에 있는 견적이고, 찾은 뒤에는 BO를 통해 읽어 같은 트랜잭션에서 바뀐 값(예: 방금 수락)을 반영합니다.
- **대체 키의 유일성**: BDEF 선언이 DB에 유일 인덱스를 만들어 주지는 않습니다(실제 시스템에서 확인 필요). 이 BO는 save action이 번호를 하나씩 늘려 매기므로 겹치지 않는다고 가정했습니다.
- **클래스 구조 해설**: `static function findByQuoteNo parameter ... result [0..1] $self` → `FOR READ IMPORTING keys FOR FUNCTION Quote~findByQuoteNo RESULT result`. 정적이므로 `keys`에는 `%cid`와 `%param-QuoteNo`만 있고, 결과는 `%cid`로 호출 줄과 연결됩니다.

**자주 나는 오류와 해결**
- key function 줄에서 문법 오류 → 위 BDL은 추정 형태입니다. `define behavior` 본문에서 `key`를 입력하고 `Ctrl+Space`로 제안되는 형태, 그리고 F1 "RAP - key function"/"BDEF alternative key" 문서의 예제를 따르세요. 문서에 나온 실제 형태를 이 해설 옆에 적어 두세요.
- `found[ %cid = 'K2' ]`에서 문법 오류 → `line_exists`는 표 식이 필요합니다. 위 코드처럼 `line_exists( found[ %cid = 'K2' ] )`로 감싸세요.

</details>

#### 12단계. 타입 매핑 변형(`corresponding`·`control`·`constant`)과 프로젝션·서비스에서 외부 이름 확인

요구사항

1. DDIC 구조 `ZRAP_S_QEXP_###`(외부 내보내기 형식)과 `ZRAP_S_QEXPX_###`(그 플래그 구조)를 아래 표대로 만드세요.
2. Quote의 BDEF에 `mapping for zrap_s_qexp_### control zrap_s_qexpx_### { ... }` 블록을 추가하세요. 그리고 `doc_category`에는 **항상 `'Q'`**가 들어가도록 `constant` 매핑(9.15, 2505)을 시도하세요(문법 확인 필요).
3. 콘솔 `s12_mapping`: (1) 읽은 견적 → `CORRESPONDING zrap_s_qexp_###( ... MAPPING FROM ENTITY )`, (2) `%control` → X 구조, (3) `USING CONTROL`로 플래그 켜진 필드만 복사, (4) 내보내기 구조 → 엔터티(`MAPPING TO ENTITY`).
4. 프로젝션 뷰 `ZRAP_C_QUOTE_###`(`provider contract transactional_query`), `ZRAP_C_QUOTEITEM_###`, 프로젝션 BDEF, 서비스 정의 `ZRAP_UI_QUOTE_###`, 서비스 바인딩 `ZRAP_UI_QUOTE_O4_###`(OData V4 - UI)를 만드세요. 프로젝션 BDEF에는 바깥에 공개할 수 있는 연산만 `use` 하세요. `IntegrityHash`는 프로젝션 뷰에 넣지 마세요.
5. 서비스 메타데이터(`$metadata`)에서 액션 이름 `Accept`, deep 파라미터의 복합 타입, `recalcTotal`·`assignQuoteNo`가 **없는 것**을 확인하세요.

`ZRAP_S_QEXP_###`

| 필드 | 키 | 데이터 엘리먼트(또는 내장 타입) | 타입 | 길이 | 소수 | 설명 |
|---|---|---|---|---|---|---|
| doc_category | | (내장) abap.char(1) | CHAR | 1 | 0 | 문서 종류(견적은 항상 Q) |
| quote_no | | (내장) abap.char(10) | CHAR | 10 | 0 | 견적 번호 |
| customer | | /dmo/customer_id | NUMC | 6 | 0 | 고객 |
| valid_until | | (내장) abap.dats | DATS | 8 | 0 | 유효일 |
| net_value | | /dmo/total_price | CURR | 16 | 2 | 순액 (참조: currency) |
| currency | | /dmo/currency_code | CUKY | 5 | 0 | 통화 |

`ZRAP_S_QEXPX_###`

| 필드 | 키 | 데이터 엘리먼트(또는 내장 타입) | 타입 | 길이 | 소수 | 설명 |
|---|---|---|---|---|---|---|
| quote_no | | xsdboolean | CHAR | 1 | 0 | 변경 표시 |
| customer | | xsdboolean | CHAR | 1 | 0 | 변경 표시 |
| valid_until | | xsdboolean | CHAR | 1 | 0 | 변경 표시 |
| net_value | | xsdboolean | CHAR | 1 | 0 | 변경 표시 |
| currency | | xsdboolean | CHAR | 1 | 0 | 변경 표시 |

**직접 추가할 어노테이션**
- (구조) `@EndUserText.label`, `@AbapCatalog.enhancement.category` — 구조 설명, 확장 가능 여부.
- (구조) `@Semantics.amount.currencyCode` — `net_value`가 따르는 통화 필드.
- (프로젝션 뷰) `@AccessControl.authorizationCheck`, `@EndUserText.label` — 접근 제어 필요 여부, 설명.
- (프로젝션 뷰) `@ObjectModel.semanticKey` — 목록에서 굵게 보일 업무 키.
- (서비스 정의) `@EndUserText.label` — 서비스 설명.

**확인**
- `c_step = 12` 출력 예: `(1) Q Q000000001 customer=… until=… net=300.00 EUR`, `(2) flags: quote_no=  valid_until=X net_value= `, `(3) partial: quote_no='' valid_until=20301231`, `(4) back: QuoteNo=Q000000001 …`
- `constant` 줄을 활성화하지 못했다면 (1)의 첫 글자는 공백입니다. 활성화했다면 `Q`입니다.
- 서비스 바인딩을 Publish하고 Service URL 뒤에 `/$metadata`를 붙여 열면 `Name="Accept"`인 액션이 보이고, `acceptQuote`, `recalcTotal`, `assignQuoteNo`라는 이름은 없습니다. `importItems`의 파라미터 타입은 품목 컬렉션을 가진 복합 타입입니다.
- Fiori Elements 미리보기(Quote)에서 목록이 열리고 견적 번호가 보입니다(이 BO는 draft가 없고 UI 어노테이션도 넣지 않았으므로 화면은 최소한입니다. UI는 R-01, R-02를 참고하세요).

<details><summary>정답·해설</summary>

```cds
@EndUserText.label : 'R-14 quote export format'
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE
define structure zrap_s_qexp_### {
  doc_category : abap.char(1);
  quote_no     : abap.char(10);
  customer     : /dmo/customer_id;
  valid_until  : abap.dats;
  @Semantics.amount.currencyCode : 'zrap_s_qexp_###.currency'
  net_value    : /dmo/total_price;
  currency     : /dmo/currency_code;
}
```

```cds
@EndUserText.label : 'R-14 quote export flags'
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE
define structure zrap_s_qexpx_### {
  quote_no    : xsdboolean;
  customer    : xsdboolean;
  valid_until : xsdboolean;
  net_value   : xsdboolean;
  currency    : xsdboolean;
}
```

Quote의 BDEF(`mapping for zrap_quote_### corresponding { ... }` 블록 아래)에 추가:

```bdef
  mapping for zrap_s_qexp_### control zrap_s_qexpx_###   // 값 매핑 + %control ↔ X 구조 매핑
  {
    QuoteNo      = quote_no;
    CustomerID   = customer;
    ValidTo      = valid_until;
    NetAmount    = net_value;
    CurrencyCode = currency;
    constant 'Q' = doc_category;                          // 왼쪽(엔터티 쪽)에 고정값 (9.15~, 실제 시스템에서 확인 필요)
  }
```

콘솔 `s12_mapping`:

```abap
  METHOD s12_mapping.
    DATA(q1_uuid) = uuid_of( 'Q000000001' ).
    READ ENTITIES OF zrap_r_quote_###
      ENTITY Quote ALL FIELDS WITH VALUE #( ( QuoteUUID = q1_uuid ) )
      RESULT DATA(quotes).
    CHECK quotes IS NOT INITIAL.
    DATA(quote) = quotes[ 1 ].

    "(1) entity -> DDIC structure: field names translated by 'mapping for zrap_s_qexp_###'
    DATA(export) = CORRESPONDING zrap_s_qexp_###( quote MAPPING FROM ENTITY ).
    out->write( |(1) { export-doc_category } { export-quote_no } customer={ export-customer } | &&
                |until={ export-valid_until } net={ export-net_value } { export-currency }| ).

    "(2) %control -> X structure: uses the 'control zrap_s_qexpx_###' part of the mapping
    DATA upd TYPE STRUCTURE FOR UPDATE zrap_r_quote_###\\Quote.
    upd = VALUE #( QuoteUUID        = q1_uuid
                   ValidTo          = '20301231'
                   %control-ValidTo = if_abap_behv=>mk-on ).
    DATA(flags) = CORRESPONDING zrap_s_qexpx_###( upd MAPPING FROM ENTITY ).
    out->write( |(2) flags: quote_no={ flags-quote_no } valid_until={ flags-valid_until } net_value={ flags-net_value }| ).

    "(3) USING CONTROL: copy only fields whose %control flag is on
    DATA(partial) = CORRESPONDING zrap_s_qexp_###( upd MAPPING FROM ENTITY USING CONTROL ).
    out->write( |(3) partial: quote_no='{ partial-quote_no }' valid_until={ partial-valid_until }| ).

    "(4) DDIC structure -> entity
    DATA back TYPE STRUCTURE FOR READ RESULT zrap_r_quote_###\\Quote.
    back = CORRESPONDING #( export MAPPING TO ENTITY ).
    out->write( |(4) back: QuoteNo={ back-QuoteNo } CustomerID={ back-CustomerID } NetAmount={ back-NetAmount }| ).
  ENDMETHOD.
```

프로젝션 뷰:

```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED          // (→ 어노테이션 탭: @AccessControl.authorizationCheck)
@EndUserText.label: 'R-14 Quote (projection)'
@ObjectModel.semanticKey: [ 'QuoteNo' ]                    // 목록에서 업무 키 강조 (→ 어노테이션 탭: @ObjectModel.semanticKey)
define root view entity ZRAP_C_QUOTE_###
  provider contract transactional_query                   // 트랜잭션 UI/API 서비스용 프로젝션
  as projection on ZRAP_R_QUOTE_###
{
  key QuoteUUID,
      QuoteNo,
      CustomerID,
      ValidTo,
      Status,
      DiscountPct,
      TotalAmount,
      NetAmount,
      CurrencyCode,
      Note,
      LocalLastChangedAt,
      // IntegrityHash: suppressed in the BDEF -> not exposed
      _Items : redirected to composition child ZRAP_C_QUOTEITEM_###
}
```

```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'R-14 Quote Item (projection)'
define view entity ZRAP_C_QUOTEITEM_###
  as projection on ZRAP_R_QUOTEITEM_###
{
  key ItemUUID,
      QuoteUUID,
      ItemNo,
      ProductID,
      Quantity,
      UnitPrice,
      LineAmount,
      CurrencyCode,
      LocalLastChangedAt,
      _Quote : redirected to parent ZRAP_C_QUOTE_###
}
```

프로젝션 BDEF `ZRAP_C_QUOTE_###`:

```bdef
projection;
strict ( 2 );

define behavior for ZRAP_C_QUOTE_### alias Quote
use etag
{
  use create;
  use update;
  use delete;

  use action acceptQuote;          // OData 이름은 기본 BDEF 의 external 'Accept'
  use action importItems;          // deep parameter: 추상 BDEF 계층 타입이 그대로 노출
  use action recalcPrices;
  use action splitByItem;
  use action createForCustomer;
  use action closeExpired;
  use action refreshQuote;         // determine action 도 use 가능

  use function simulatePricing;
  use function getCheapestItem;    // 결과 엔터티가 R 뷰 타입 → 프로젝션 타입으로 바꿔야 하면 활성화 메시지를 따르세요 (실제 시스템에서 확인 필요)
  use function checkImport;
  use function findByQuoteNo;

  use association _Items;          // internal create 이므로 { create; } 없음

  // 넣을 수 없는 것: internal action recalcTotal, save action assignQuoteNo,
  //                Item 의 internal update, association _Items 의 internal create
}

define behavior for ZRAP_C_QUOTEITEM_### alias Item
use etag
{
  use delete;
  use association _Quote;
}
```

서비스 정의:

```cds
@EndUserText.label: 'R-14 Quote service'
define service ZRAP_UI_QUOTE_### {
  expose ZRAP_C_QUOTE_###     as Quote;
  expose ZRAP_C_QUOTEITEM_### as QuoteItem;
}
```

서비스 바인딩 `ZRAP_UI_QUOTE_O4_###`: 바인딩 유형 **OData V4 - UI**, 서비스 정의 `ZRAP_UI_QUOTE_###` → 활성화 → **Publish**.

**왜 이렇게 쓰나**
- **`mapping for X corresponding { ... }`**: 이름이 같은 필드는 자동으로 짝짓고, 다른 것만 적습니다. Flight 참조 시나리오의 managed Travel(`/DMO/I_Travel_M`)은 이름이 모두 같아 `mapping for /dmo/travel_m corresponding;` 한 줄만 씁니다. 이 문제는 DB가 snake_case라 거의 모든 필드를 적었습니다.
- **`control 구조`**: 값 구조와 같은 이름 대응을 `%control` ↔ X 구조(필드별 `X`)에도 적용합니다. 레거시 API의 "어느 필드를 바꿀지" 플래그 구조와 RAP `%control`을 한 줄로 바꿀 때 씁니다(R-06에서 unmanaged BO에 본격적으로 사용. 참조 시나리오 `/DMO/I_Travel_U`의 `mapping for /dmo/travel control /dmo/s_travel_intx`와 같은 형태).
- **`USING CONTROL`**: `%control`이 켜진 필드만 복사하고 나머지는 대상의 초기값으로 둡니다. "보낸 필드만 반영"을 매핑 수준에서 하는 방법입니다.
- **`constant`**(9.15, 2505): 릴리스 뉴스는 "It is now possible to specify a fixed value on the left side of a RAP type mapping using the syntax constant. This can be useful, for example, in scenarios where different entities are mapped to the same underlying RAP persistent table."라고만 설명합니다. 예를 들어 견적과 주문 엔터티가 같은 테이블을 쓰고 `doc_category`로 구분할 때, 엔터티에 그 필드가 없어도 매핑이 항상 `'Q'`를 넣게 할 수 있습니다. 정확한 줄 형태는 확인하지 못했으므로 위 코드는 추정입니다.
- **`suppress`와 프로젝션**: `IntegrityHash`는 기본 BDEF에서 이미 RAP API 밖으로 빠졌습니다. 프로젝션 뷰에 넣어도 OData에는 나오지 않겠지만, 혼동을 막으려고 아예 빼는 것이 깔끔합니다.
- **프로젝션 BDEF가 거르는 것**: `internal` 연산과 save action은 프로젝션에서 `use` 할 수 없습니다. 즉 바깥(OData)에는 처음부터 존재하지 않습니다. 메타데이터에서 `recalcTotal`, `assignQuoteNo`가 보이지 않는 것이 그 결과입니다.
- **external 이름**: `$metadata`의 액션 이름은 `Accept`입니다. Fiori 어노테이션(`@UI.lineItem`의 `dataAction`)에서도 OData 이름이 아니라 **BDEF 내부 이름**(`acceptQuote`)을 적는다는 점을 R-02 어노테이션과 비교해 보세요(실제 시스템에서 확인 필요).

**R-14 전체 정리: 어떤 문법을 어디서 썼나**

| 문법 | 단계 | 한 줄 요약 |
|---|---|---|
| `abstract;` `with hierarchy;` `with control` | 4 | 계층형 파라미터·결과 타입, `%control` 포함 |
| `mandatory : execute` (필드/연관) | 4, 7 | 액션·함수 호출 시 필수 |
| `with hierarchy like entity` | 4 | 계층 타입과 CDS 구조의 일치를 엄격히 검사 |
| `deep parameter` / `deep table parameter` / `deep result` | 7 | `%param`이 계층형 구조 / 표 / 결과 |
| `result selective` + `REQUEST requested_fields` | 8 | 요청된 결과 필드만 |
| `result [0..1] entity X`, `result [0..*] $self` | 8 | 다른 엔터티 타입 결과, 여러 줄 결과 |
| `static action` | 8 | 인스턴스 없는 비팩토리 액션, `%cid`만 |
| `external 'Accept'` | 8, 12 | OData 이름만 바꿈 |
| `factory action [1..*]`, `static factory action [0..*]` | 9 | 한 호출로 여러 인스턴스, `mapped`에 같은 `%cid` 여러 줄 |
| `save ( finalize )`, `save ( adjustnumbers )` | 10 | 세이버 메서드에서만 실행되는 액션 |
| `validation/determination ... on save { delete; }` | 6 | 삭제 저장 시 실행, 버퍼에서 못 읽음 → DB |
| `determination ( always )` | 6 | determine action에서 트리거 무시 |
| `field ( notrigger )`, `notrigger : warn` | 5 | 트리거에 쓰면 오류/경고 |
| `field ( suppress )` | 5 | 파생 타입·RAP API에서 제거 |
| `internal create`(연관), `internal update`, `internal action` | 5, 6, 7, 9 | BO 안 `IN LOCAL MODE`에서만 |
| 대체 키, key function | 11 | 업무 키로 인스턴스 찾기 |
| `mapping for ... corresponding` / `control` / `constant` | 5, 12 | 이름 매핑, 플래그 매핑, 고정값 |

**자주 나는 오류와 해결**
- `mapping for zrap_s_qexp_### control ...` 활성화 시 "field ... not found" → 매핑 오른쪽은 DDIC 구조의 필드 이름(소문자 그대로), 왼쪽은 CDS 요소 이름입니다. X 구조에는 같은 필드 이름이 있어야 합니다.
- `constant 'Q' = doc_category;`에서 문법 오류 → 형태가 다른 것입니다. 줄을 지우고 나머지를 활성화한 뒤 F1 "RAP - type mapping" 문서의 `constant` 예제를 찾아 맞추세요(실제 시스템에서 확인 필요).
- 프로젝션 BDEF에서 `use function getCheapestItem;` 오류 → 결과 엔터티가 기본 BO의 R 뷰라서 프로젝션 계층에 맞지 않는다는 뜻일 수 있습니다. 오류 메시지가 제안하는 형태(결과 엔터티를 프로젝션 엔터티로 다시 지정)로 고치거나, 이 함수를 `use`에서 빼세요(실제 시스템에서 확인 필요).
- 서비스 바인딩에서 "Service ... contains actions with deep parameters" 류의 경고 → UI 바인딩에서 deep 파라미터 액션은 화면 버튼으로 쓰기 어렵습니다. Web API 바인딩(OData V4 - Web API)으로 하나 더 만들어 메타데이터를 비교해 보세요.

</details>

## 출처

- SAP-samples/abap-cheat-sheets — RAP BDL: https://github.com/SAP-samples/abap-cheat-sheets/blob/main/36_RAP_Behavior_Definition_Language.md
- SAP-samples/abap-cheat-sheets — ABAP EML: https://github.com/SAP-samples/abap-cheat-sheets/blob/main/08_EML_ABAP_for_RAP.md
- SAP-samples/abap-cheat-sheets — ABAP Release News: https://github.com/SAP-samples/abap-cheat-sheets/blob/main/33_ABAP_Release_News.md
- SAP-samples/abap-cheat-sheets — `rap` 브랜치 README(예제 RAP BO 목록): https://github.com/SAP-samples/abap-cheat-sheets/blob/rap/README.md
- SAP-samples/abap-cheat-sheets — `zdemo_abap_rap_ro_m_as` BDEF와 행동 풀(additional save 세이버 구조): https://github.com/SAP-samples/abap-cheat-sheets/tree/main/src
- SAP-samples/abap-platform-fiori-feature-showcase (ABAP-platform-cloud 브랜치) — 추상 BDEF `/DMO/FSA_D_OverwriteTimezoneP`(abstract, with hierarchy, with control, mandatory:execute), 루트 BDEF `/DMO/FSA_R_RootTP`(deep parameter, determination ( always ), external, static action), 행동 풀 `/DMO/FSA_BP_R_RootTP`: https://github.com/SAP-samples/abap-platform-fiori-feature-showcase/tree/ABAP-platform-cloud/src
- SAP-samples/abap-platform-refscen-flight (ABAP-platform-cloud 브랜치) — `/DMO/I_Travel_M`(mapping corresponding), `/DMO/I_Travel_U`(mapping control), 행동 풀의 `READ TABLE ... WITH KEY id COMPONENTS %tky`: https://github.com/SAP-samples/abap-platform-refscen-flight/tree/ABAP-platform-cloud/src
