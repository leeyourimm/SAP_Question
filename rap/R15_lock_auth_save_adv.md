## 5. 고급·특수 기능 보충

### R-15. 잠금·권한·저장 고급: unmanaged lock, 액션별 권한, 보조 클래스, BDEF friends, 변경 문서, late save 실패 처리 [작성] ★★★
<!-- covers: lock master unmanaged, FOR LOCK, 잠금 객체, cl_abap_lock_object_factory, cx_abap_foreign_lock, cx_abap_lock_failure, RAISE SHORTDUMP, if_abap_behv=>cause-locked, SET LOCKS, authorization master ( global, instance ), authorization : global, authorization : instance, authorization : none, subentity authorization master, create ( authorization : global, authorization : instance ), %assoc, %action, %action-Edit, %global, internal action, auxiliary class, FOR BEHAVIOR OF, TABLE FOR READ IMPORT, TABLE FOR READ RESULT, IN LOCAL MODE in auxiliary class, extensible with friends, BDEF extension, extend behavior for, extension implementation in class, extension behavior pool, changedocuments master, changedocuments dependent by, changedocuments ( create : key, update : data, delete : ... ), change document object, Change Document Logging, cl_chdo_read_tools, cx_chdo_read_error, ZCL_..._CHDO=>write, with additional save, save_modified, CL_ABAP_BEHAVIOR_SAVER_FAILED, failed/reported late, COMMIT ENTITIES RESPONSE OF, RESPONSE FOR FAILED LATE, sy-subrc 8, ROLLBACK ENTITIES, define table entity, @ClientHandling.type, CDS table entity as persistent table, draft action Edit, %param-preserve_changes, numbering : managed -->

**목표**
- managed BO에서 `lock master unmanaged`로 잠금을 직접 구현하고(자체 잠금 객체 + `FOR LOCK` 핸들러), 다른 사용자의 잠금을 `%fail-cause = locked`와 메시지로 돌려줄 수 있습니다.
- 권한을 연산 단위로 세분할 수 있습니다: 액션마다 `authorization : global` / `instance` / `none`, 자식 엔터티를 별도 `authorization master`로, 자식 생성(create-by-association)에 별도 권한(`create ( authorization : global, authorization : instance )`).
- 행동 풀의 공통 로직(읽기·메시지 생성)을 **ABP 보조 클래스**(`auxiliary class`)로 빼고, 보조 클래스 안에서 `IN LOCAL MODE`로 BO를 읽을 수 있습니다.
- BDEF 확장을 **BDEF friend**(`with friends`)로 선언해, 확장에서 원래 BO의 internal action을 `IN LOCAL MODE`로 호출할 수 있습니다.
- **RAP 변경 문서**(`changedocuments master` / `dependent`)로 코드 없이 변경 이력을 남기고 `CL_CHDO_READ_TOOLS`로 읽을 수 있습니다.
- 저장 후반(late save)에 실패할 수 있는 Z 레거시 API를 부를 때 `CL_ABAP_BEHAVIOR_SAVER_FAILED`로 `failed`/`reported`를 채우고, 소비자 쪽에서 `sy-subrc = 8` → `ROLLBACK ENTITIES`로 처리할 수 있습니다. 덤으로 CDS table entity와 draft `Edit`의 `preserve_changes`도 다룹니다.

**전제**
- 패키지 `ZRAP_###`, ADT 연결(BTP ABAP Environment 트라이얼, 언어 버전 ABAP for Cloud Development).
- `/DMO/CUSTOMER` 데이터(Flight Reference Scenario 기본 데이터. R-01에서 이미 썼습니다).
- R-01~R-04를 끝냈으면 이해가 빠르지만, 이 문제는 **전용 작은 BO(기자재 대여)**를 새로 만들므로 기존 Travel BO를 건드리지 않습니다. 메시지 클래스·예외 클래스도 이 BO 전용으로 따로 만듭니다(다른 문제의 `ZCM_RAP_###` 번호와 겹치지 않게).
- 일부 기능은 최신 릴리스에서만 됩니다. 각 단계 해설에 릴리스(클라우드 버전 번호)를 적었습니다. BTP 트라이얼은 항상 최신 클라우드 릴리스이므로 대부분 그대로 됩니다.

**만들 객체**

| 순서 | 객체 유형 | 이름 | 역할 |
|---|---|---|---|
| 1 | 데이터 엘리먼트 3개 | `ZRAP_LOAN_STATUS_###`, `ZRAP_EQUIP_ID_###`, `ZRAP_LOAN_QTY_###` | 변경 문서 대상 필드(Change Document Logging 표시) |
| 2 | DB 테이블 | `ZRAP_LOAN_###` | 대여(헤더) 활성 테이블 |
| 3 | DB 테이블 | `ZRAP_LOANI_###` | 대여 품목 활성 테이블 |
| 4 | CDS table entity | `ZRAP_ASSET_###` | "레거시" 자산 마스터(재고·차단 여부) |
| 5 | DB 테이블 | `ZRAP_LOANSW_###` | 실습용 권한 스위치 |
| 6 | 클래스 | `ZCL_RAP_ASSET_API_###` | 늦게 실패할 수 있는 Z 레거시 출고 API |
| 7 | 메시지 클래스 / 예외 클래스 | `ZRAP_LMSG_###` / `ZCM_RAP_LOAN_###` | 이 BO 전용 메시지 |
| 8 | 잠금 객체 | `EZRAP_LOAN_###` | unmanaged lock에 쓸 자체 잠금 객체 |
| 9 | CDS 뷰 엔터티 | `ZRAP_R_LOAN_###`, `ZRAP_R_LOANITEM_###` | BO 데이터 모델 |
| 10 | DB 테이블 | `ZRAP_LOAN_D_###`, `ZRAP_LOANI_D_###` | draft 테이블 |
| 11 | 클래스 | `ZCL_RAP_LOAN_GEN_###` | 데모 데이터·스위치 설정 |
| 12 | BDEF | `ZRAP_R_LOAN_###` | managed + draft + unmanaged lock + 세분 권한 + 보조 클래스 + 변경 문서 + friends |
| 13 | 클래스 | `ZCL_RAP_LOAN_AUX_###` | ABP 보조 클래스 |
| 14 | 클래스(행동 풀) | `ZBP_RAP_R_LOAN_###` | 핸들러 `lhc_loan`, `lhc_item`, 세이버 `lsc_zrap_r_loan_###` |
| 15 | 변경 문서 객체 / 클래스 | `ZRAPLOAN###` / `ZCL_RAP_LOAN_CHDOC_###` | RAP 변경 문서 저장소, 변경 문서 읽기 콘솔 |
| 16 | BDEF 확장 / 확장 행동 풀 | `ZRAP_X_LOAN_###` / `ZBP_RAP_X_LOAN_###` | BDEF friend |
| 17 | 프로젝션 뷰·MDE·BDEF | `ZRAP_C_LOAN_###`, `ZRAP_C_LOANITEM_###` | UI용 프로젝션 |
| 18 | 서비스 정의 / 바인딩 | `ZRAP_UI_LOAN_###` / `ZRAP_UI_LOAN_O4_###` | Fiori 미리보기 |
| 19 | 클래스 | `ZCL_RAP_LOAN_TEST_###`, `ZCL_RAP_LOAN_LOCKHOLD_###` | 종합 EML 확인, 잠금 붙잡기 |

#### 1단계. 변경 문서용 데이터 엘리먼트와 활성 테이블 두 개

요구사항

1. 데이터 엘리먼트 세 개를 만드세요(ADT: New → Other ABAP Repository Object → Dictionary → Data Element). 셋 다 **Additional Properties 탭에서 "Change Document Logging"을 켭니다.** 10단계의 RAP 변경 문서는 이 표시가 있는 필드만 값(이전/이후)을 기록합니다.

| 이름 | 타입 | 길이 | 라벨(Medium) | 값 |
|---|---|---|---|---|
| `ZRAP_LOAN_STATUS_###` | CHAR | 1 | Loan Status | N=New, A=Approved, L=Lent, R=Returned |
| `ZRAP_EQUIP_ID_###` | CHAR | 10 | Equipment | 예: `EQ-LAPTOP` |
| `ZRAP_LOAN_QTY_###` | INT4 | 10 | Quantity | 대여 수량 |

2. 대여 헤더 활성 테이블 `ZRAP_LOAN_###`를 만드세요.

| 필드 | 키 | 데이터 엘리먼트(또는 내장 타입) | 타입 | 길이 | 소수 | 설명 |
|---|---|---|---|---|---|---|
| client | X | abap.clnt | CLNT | 3 | 0 | 클라이언트 |
| loan_uuid | X | sysuuid_x16 | RAW | 16 | 0 | 대여 UUID(managed numbering) |
| borrower_id | | /dmo/customer_id | NUMC | 6 | 0 | 빌리는 사람(고객) |
| begin_date | | /dmo/begin_date | DATS | 8 | 0 | 대여 시작일 |
| end_date | | /dmo/end_date | DATS | 8 | 0 | 반납 예정일 |
| status | | zrap_loan_status_### | CHAR | 1 | 0 | 상태(N/A/L/R), 변경 문서 대상 |
| description | | /dmo/description | CHAR | 1024 | 0 | 설명 |
| approved_by | | abap.char(12) | CHAR | 12 | 0 | 승인한 사용자 |
| reminder_count | | abap.int1 | INT1 | 3 | 0 | 독촉 횟수 |
| created_by | | abp_creation_user | CHAR | 12 | 0 | 생성자 |
| created_at | | abp_creation_tstmpl | DEC | 21 | 7 | 생성 시각 |
| local_last_changed_by | | abp_locinst_lastchange_user | CHAR | 12 | 0 | 인스턴스 최종 변경자 |
| local_last_changed_at | | abp_locinst_lastchange_tstmpl | DEC | 21 | 7 | 인스턴스 최종 변경(ETag) |
| last_changed_at | | abp_lastchange_tstmpl | DEC | 21 | 7 | 최종 변경(total ETag) |

3. 대여 품목 활성 테이블 `ZRAP_LOANI_###`를 만드세요.

| 필드 | 키 | 데이터 엘리먼트(또는 내장 타입) | 타입 | 길이 | 소수 | 설명 |
|---|---|---|---|---|---|---|
| client | X | abap.clnt | CLNT | 3 | 0 | 클라이언트 |
| item_uuid | X | sysuuid_x16 | RAW | 16 | 0 | 품목 UUID |
| loan_uuid | | sysuuid_x16 | RAW | 16 | 0 | 부모 대여 UUID |
| equipment_id | | zrap_equip_id_### | CHAR | 10 | 0 | 기자재 번호, 변경 문서 대상 |
| quantity | | zrap_loan_qty_### | INT4 | 10 | 0 | 수량, 변경 문서 대상 |
| item_note | | /dmo/description | CHAR | 1024 | 0 | 메모 |
| local_last_changed_at | | abp_locinst_lastchange_tstmpl | DEC | 21 | 7 | 품목 ETag |

**확인** 세 데이터 엘리먼트와 두 테이블이 활성화됩니다. 데이터 엘리먼트를 다시 열어 Additional Properties 탭의 Change Document Logging이 체크되어 있는지 확인하세요. Data Preview는 아직 비어 있습니다.

<details><summary>정답·해설</summary>

데이터 엘리먼트는 폼 편집기로 만듭니다. Type Category를 **Predefined Type**으로 두고 Data Type/Length를 넣은 뒤, Field Labels(Short/Medium/Long/Heading)를 채우고 **Additional Properties** 탭의 **Change Document Logging** 체크박스를 켭니다. SAP 공식 샘플(abap-platform-reuse-services)도 "합계 금액·상태 데이터 엘리먼트의 Additional Properties에서 change document logging 플래그를 켰다"고 설명합니다.

| 데이터 엘리먼트 | Type Category | Data Type | Length | Short / Medium 라벨 | Change Document Logging |
|---|---|---|---|---|---|
| `ZRAP_LOAN_STATUS_###` | Predefined Type | CHAR | 1 | Status / Loan Status | 켬 |
| `ZRAP_EQUIP_ID_###` | Predefined Type | CHAR | 10 | Equipment / Equipment | 켬 |
| `ZRAP_LOAN_QTY_###` | Predefined Type | INT4 | 10 | Quantity / Quantity | 켬 |

헤더 테이블:

```cds
@EndUserText.label : 'Equipment loan ### (active)'
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table zrap_loan_### {

  key client            : abap.clnt not null;
  key loan_uuid         : sysuuid_x16 not null;
  borrower_id           : /dmo/customer_id;
  begin_date            : /dmo/begin_date;
  end_date              : /dmo/end_date;
  status                : zrap_loan_status_###;   // change document relevant (data element flag)
  description           : /dmo/description;
  approved_by           : abap.char(12);
  reminder_count        : abap.int1;
  created_by            : abp_creation_user;
  created_at            : abp_creation_tstmpl;
  local_last_changed_by : abp_locinst_lastchange_user;
  local_last_changed_at : abp_locinst_lastchange_tstmpl;
  last_changed_at       : abp_lastchange_tstmpl;

}
```

품목 테이블:

```cds
@EndUserText.label : 'Equipment loan item ### (active)'
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table zrap_loani_### {

  key client            : abap.clnt not null;
  key item_uuid         : sysuuid_x16 not null;
  loan_uuid             : sysuuid_x16;
  equipment_id          : zrap_equip_id_###;      // change document relevant
  quantity              : zrap_loan_qty_###;      // change document relevant
  item_note             : /dmo/description;
  local_last_changed_at : abp_locinst_lastchange_tstmpl;

}
```

왜 이렇게 쓰나

- **변경 문서 대상은 필드 단위로 고릅니다.** RAP 변경 문서는 CDS 엔터티 필드의 메타데이터를 보고, "데이터 엘리먼트(또는 CDS simple type)에 변경 문서 표시가 있는 필드"만 값을 기록합니다(ABAP 키워드 문서 `changedocuments, Options`). 그래서 `/DMO/...` 데이터 엘리먼트를 쓰는 필드(설명, 날짜)는 기록되지 않고, 직접 만든 세 엘리먼트를 쓰는 상태·기자재·수량만 기록됩니다. CDS simple type을 쓸 때는 `@AbapCatalog.typeSpec.changeDocumentRelevant: true`가 같은 역할입니다.
- 키는 UUID(`sysuuid_x16`)로 두었습니다. BDEF에서 `numbering : managed`로 프레임워크가 채우게 하면 이 문제의 주제(잠금·권한·저장)에 집중할 수 있습니다. late numbering은 R-04에서 다뤘습니다.
- 금액·수량 참조 필드가 없는 이유: `quantity`는 단위 없는 정수(INT4)라서 `@Semantics.quantity.unitOfMeasure` 참조가 필요 없습니다.

자주 나는 오류와 해결

- Additional Properties 탭이 안 보이면 데이터 엘리먼트 편집기 아래쪽 탭 줄을 확인하세요(General / Additional Properties). 표시를 빠뜨리면 10단계에서 변경 문서에 키만 남고 값이 안 남습니다.

</details>

#### 2단계. 레거시 쪽 준비: 자산 CDS table entity, 스위치 테이블, 늦게 실패하는 Z API

요구사항

1. "레거시 자산 마스터"를 **CDS table entity** `ZRAP_ASSET_###`로 만드세요(ADT: New → Other → Core Data Services → Data Definition, 템플릿 없이 `define table entity`를 직접 씀). 클라이언트 종속, 키 `EquipmentID`.

| 요소 | 키 | 데이터 엘리먼트(또는 내장 타입) | 타입 | 길이 | 소수 | 설명 |
|---|---|---|---|---|---|---|
| (클라이언트) | X | (자동) | CLNT | 3 | 0 | `@ClientHandling.type`로 자동 생성, 직접 선언 금지 |
| EquipmentID | X | zrap_equip_id_### | CHAR | 10 | 0 | 기자재 번호 |
| EquipmentName | | abap.char(40) | CHAR | 40 | 0 | 기자재 이름 |
| Stock | | abap.int4 | INT4 | 10 | 0 | 재고 수량 |
| IsBlocked | | abap_boolean | CHAR | 1 | 0 | 레거시 내부 차단 표시 |
| LastPostedAt | | abp_lastchange_tstmpl | DEC | 21 | 7 | 마지막 출고 시각 |

2. 실습용 권한 스위치 테이블 `ZRAP_LOANSW_###`(DDIC)를 만드세요. 실제 권한 객체·IAM 앱을 만들지 않고도 권한 거부를 재현하기 위한 테이블입니다.

| 필드 | 키 | 데이터 엘리먼트(또는 내장 타입) | 타입 | 길이 | 소수 | 설명 |
|---|---|---|---|---|---|---|
| client | X | abap.clnt | CLNT | 3 | 0 | 클라이언트 |
| switch_id | X | abap.char(30) | CHAR | 30 | 0 | 스위치 이름(예: `DENY_APPROVE`) |
| switch_value | | abap.char(20) | CHAR | 20 | 0 | 값(`X`, 고객 번호, 기자재 번호 등) |

3. 레거시 API 클래스 `ZCL_RAP_ASSET_API_###`를 만드세요.
   - 타입: 출고 요청 `ty_posting`(`equipment_id`, `quantity`)과 테이블 `tt_postings`, 오류 `ty_error`(`equipment_id`, `text` string)와 `tt_errors`.
   - 메서드 `post_issue( postings ) RETURNING errors`: **확인과 저장을 한 번에** 하는 API입니다. 같은 기자재는 수량을 합산하고, 자산이 없거나(`unknown equipment`), `IsBlocked`이거나(`blocked in legacy system`), 재고가 모자라면(`only <n> in stock`) 오류를 돌려줍니다. 오류가 하나라도 있으면 **아무것도 바꾸지 않고**(전부 아니면 전무), 없으면 재고를 줄이고 `LastPostedAt`을 기록합니다.
   - 이 API는 `COMMIT WORK`를 하지 않습니다(호출자의 LUW 안에서만 씀).

**직접 추가할 어노테이션** (table entity)
- `@EndUserText.label` — 객체 설명.
- `@ClientHandling.type` — 테이블을 클라이언트 종속으로 만들지 정함(클라이언트 필드를 직접 쓰지 않는 대신).
- `@AbapCatalog.deliveryClass` — 어떤 종류의 데이터(업무 데이터)를 담는 테이블인지.
- `@AccessControl.authorizationCheck` — CDS 접근 제어(DCL) 검사가 필요한지.

**확인** table entity, 스위치 테이블, 클래스가 활성화됩니다. table entity를 F8(Data Preview)로 열면 빈 테이블이 보이고, 열 목록에 클라이언트 열은 보이지 않습니다.

<details><summary>정답·해설</summary>

CDS table entity:

```cds
@EndUserText.label: 'Legacy asset master ###'          // 설명
@ClientHandling.type: #CLIENT_DEPENDENT               // 클라이언트 열을 DB에 자동 생성, ABAP SQL이 현재 클라이언트로 자동 필터
@AbapCatalog.deliveryClass: #APPLICATION_DATA         // 업무 데이터 (DDIC 테이블의 #A에 해당)
@AccessControl.authorizationCheck: #NOT_REQUIRED      // DCL 검사 안 함
define table entity ZRAP_ASSET_###
{
  key EquipmentID   : zrap_equip_id_###;
      EquipmentName : abap.char(40);
      Stock         : abap.int4;
      IsBlocked     : abap_boolean;
      LastPostedAt  : abp_lastchange_tstmpl;
}
```

(→ 어노테이션 탭: @ClientHandling.type, @AbapCatalog.deliveryClass, @AccessControl.authorizationCheck)

스위치 테이블:

```cds
@EndUserText.label : 'Loan ### authorization switches (exercise)'
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table zrap_loansw_### {

  key client   : abap.clnt not null;
  key switch_id : abap.char(30) not null;
  switch_value : abap.char(20);

}
```

레거시 API 클래스:

```abap
"! Legacy asset API (simulated). Check and posting happen in ONE call -
"! there is no separate check method that RAP could call early.
CLASS zcl_rap_asset_api_### DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    TYPES:
      BEGIN OF ty_posting,
        equipment_id TYPE zrap_equip_id_###,
        quantity     TYPE zrap_loan_qty_###,
      END OF ty_posting,
      tt_postings TYPE STANDARD TABLE OF ty_posting WITH EMPTY KEY,
      BEGIN OF ty_error,
        equipment_id TYPE zrap_equip_id_###,
        text         TYPE string,
      END OF ty_error,
      tt_errors TYPE STANDARD TABLE OF ty_error WITH EMPTY KEY.

    "! Goods issue for lent equipment. All or nothing.
    "! Never commits - the caller's LUW decides.
    METHODS post_issue
      IMPORTING postings      TYPE tt_postings
      RETURNING VALUE(errors) TYPE tt_errors.

  PROTECTED SECTION.
  PRIVATE SECTION.
ENDCLASS.

CLASS zcl_rap_asset_api_### IMPLEMENTATION.

  METHOD post_issue.

    IF postings IS INITIAL.
      RETURN.
    ENDIF.

    "1) sum up quantities per equipment
    DATA totals TYPE SORTED TABLE OF ty_posting WITH UNIQUE KEY equipment_id.
    LOOP AT postings INTO DATA(posting).
      READ TABLE totals ASSIGNING FIELD-SYMBOL(<total>)
           WITH TABLE KEY equipment_id = posting-equipment_id.
      IF sy-subrc = 0.
        <total>-quantity += posting-quantity.
      ELSE.
        INSERT posting INTO TABLE totals.
      ENDIF.
    ENDLOOP.

    "2) read all affected assets with one SELECT
    SELECT * FROM zrap_asset_###
      FOR ALL ENTRIES IN @totals
      WHERE EquipmentID = @totals-equipment_id
      INTO TABLE @DATA(assets).

    "3) legacy-internal checks (blocked flag is only known inside the legacy system)
    LOOP AT totals INTO DATA(total).
      READ TABLE assets INTO DATA(asset) WITH KEY EquipmentID = total-equipment_id.
      IF sy-subrc <> 0.
        APPEND VALUE #( equipment_id = total-equipment_id
                        text         = `unknown equipment` ) TO errors.
      ELSEIF asset-IsBlocked = abap_true.
        APPEND VALUE #( equipment_id = total-equipment_id
                        text         = `blocked in legacy system` ) TO errors.
      ELSEIF asset-Stock < total-quantity.
        APPEND VALUE #( equipment_id = total-equipment_id
                        text         = |only { asset-Stock } in stock| ) TO errors.
      ENDIF.
    ENDLOOP.

    "4) all or nothing
    IF errors IS NOT INITIAL.
      RETURN.
    ENDIF.

    DATA(now) = cl_abap_tstmp=>utclong2tstmp( utclong_current( ) ).
    DATA changed_assets LIKE assets.
    LOOP AT totals INTO total.
      READ TABLE assets INTO asset WITH KEY EquipmentID = total-equipment_id.
      asset-Stock        = asset-Stock - total-quantity.
      asset-LastPostedAt = now.
      APPEND asset TO changed_assets.
    ENDLOOP.

    "database change only - no COMMIT WORK here
    UPDATE zrap_asset_### FROM TABLE @changed_assets.

  ENDMETHOD.

ENDCLASS.
```

왜 이렇게 쓰나

- **CDS table entity**(`define table entity`)는 ABAP Cloud에서 DDIC 데이터베이스 테이블의 후속으로 소개된 새 CDS 엔터티입니다(릴리스 뉴스: 클라우드 2502 / 버전 914). 클라이언트 필드를 직접 선언하지 않고 `@ClientHandling.type: #CLIENT_DEPENDENT`로 정하면 DB에 클라이언트 열이 자동으로 생기고, ABAP SQL 읽기/쓰기에서 현재 클라이언트가 자동으로 적용됩니다. `abap.clnt` 타입이나 `CLIENT`라는 요소 이름은 오히려 금지입니다. 이름은 최대 25자입니다.
- 여기서는 "레거시 데이터"를 table entity로 만들어 ABAP SQL(`SELECT`, `UPDATE ... FROM TABLE`)로 다루는 것까지 확실한 범위에서 연습합니다.
- **RAP 활성 저장소로 table entity 쓰기**: BDL 치트 시트는 `persistent table` 설명에 "DDIC 데이터베이스 테이블(또는 CDS table entity)"이라고 적고, SAP 도움말 "using table entities as active persistence"를 가리킵니다. 즉 BDEF에서 `persistent table ZRAP_LOAN_TE_###`처럼 table entity 이름을 쓰는 방식입니다. 이 실습은 안정성을 위해 DDIC 테이블을 쓰지만, 같은 필드로 table entity를 만들고 `persistent table`만 바꿔 보는 변형을 해 볼 수 있습니다(실제 시스템에서 확인 필요: 릴리스 2502 이상, draft 테이블도 table entity로 만들 수 있는지 등). 커뮤니티 예제 중에는 BDEF를 아예 `define root table entity` 위에 정의하는 형태도 있지만, SAP 공식 문서에서 확인하지 못했으므로 이 문제에서는 쓰지 않습니다.
- **API가 "확인 + 저장"을 한 번에 하는 이유**: 9단계의 핵심 상황을 흉내 내기 위해서입니다. RAP 규칙은 "실패는 early save(검증·`check_before_save`)에서 찾고, late save는 실패하지 않는다"입니다. 그런데 이 API처럼 사전 점검 기능이 없고 내부 규칙(`IsBlocked`)이 바깥에 공개되지 않은 레거시는 저장하는 순간에만 실패를 알 수 있습니다. 그때가 `CL_ABAP_BEHAVIOR_SAVER_FAILED`가 필요한 예외 상황입니다.
- 루프 안 SELECT를 피하려고 `FOR ALL ENTRIES` 한 번, 쓰기도 `UPDATE ... FROM TABLE` 한 번으로 했습니다.

자주 나는 오류와 해결

- table entity에 `key client : abap.clnt` 를 적으면 활성화 오류가 납니다. 클라이언트는 `@ClientHandling.type`으로만 정합니다.
- 트라이얼에서 `define table entity` 템플릿이 메뉴에 없으면 아무 템플릿으로 Data Definition을 만든 뒤 내용을 통째로 바꾸세요.

</details>

#### 3단계. 메시지 클래스, 예외 클래스, 잠금 객체

요구사항

1. 메시지 클래스 `ZRAP_LMSG_###`(설명 "Equipment loan messages")에 아래 메시지를 등록하세요.

| 번호 | 텍스트 | 상수 이름 | 쓰는 곳 |
|---|---|---|---|
| 001 | Loan of borrower &1 is locked by user &2. | `loan_locked` | `FOR LOCK` |
| 002 | You are not authorized to create loans. | `no_auth_create` | 전역 권한 |
| 003 | You are not authorized to approve loans. | `no_auth_approve` | 액션 전역 권한 |
| 004 | You are not authorized to lend equipment to borrower &1. | `no_auth_lend` | 액션 인스턴스 권한 |
| 005 | Only the creator &1 may change this loan. | `only_creator` | 인스턴스 권한 |
| 006 | You are not authorized to change items for equipment &1. | `no_auth_item` | 자식 권한 마스터 |
| 007 | You are not authorized to add items to loans. | `no_auth_add_item` | cba 권한 |
| 008 | Loan of borrower &1 has been approved. | `loan_approved` | 액션 성공 |
| 009 | Loan of borrower &1 has been lent out. | `loan_lent` | 액션 성공 |
| 010 | Reminder no. &2 sent to borrower &1. | `reminder_sent` | 액션 성공 |
| 011 | Equipment &1 could not be posted: &2 | `posting_failed` | late save 실패 |
| 012 | Enter a borrower. | `enter_borrower` | 검증 |
| 013 | Borrower &1 does not exist. | `borrower_unknown` | 검증 |
| 014 | Equipment &1 does not exist. | `equipment_unknown` | 검증 |
| 015 | Only &2 pieces of equipment &1 are in stock. | `stock_too_low` | 검증 |
| 016 | The action is not possible in status &1. | `wrong_status` | 액션 |
| 017 | Loan of borrower &1 was returned. | `loan_returned` | friend 확장 |

2. 예외 클래스 `ZCM_RAP_LOAN_###`를 만드세요(R-02의 `ZCM_RAP_###`와 같은 구조): `CX_STATIC_CHECK` 상속, `IF_T100_MESSAGE`·`IF_T100_DYN_MSG`·`IF_ABAP_BEHV_MESSAGE` 구현, 메시지마다 상수, 속성 `mv_borrower`, `mv_user_name`, `mv_equipment`, `mv_text`, `mv_count`, `mv_status`, 생성자 파라미터 `textid`, `severity`(기본 오류), `previous`, `borrower`, `user_name`, `equipment`, `text`, `count`(정수), `status`.
3. 잠금 객체 `EZRAP_LOAN_###`를 만드세요(ADT: New → Other → Dictionary → Lock Object). 기본 테이블 `ZRAP_LOAN_###`, 잠금 모드 Write Lock(E), 보조 테이블 `ZRAP_LOANI_###`(E), 잠금 파라미터 `LOAN_UUID`.

**확인** 메시지 클래스 저장, 예외 클래스와 잠금 객체가 활성화됩니다. 잠금 객체 개요에 파라미터 `CLIENT`, `LOAN_UUID`가 보입니다.

<details><summary>정답·해설</summary>

예외 클래스 전체 코드:

```abap
CLASS zcm_rap_loan_### DEFINITION
  PUBLIC
  INHERITING FROM cx_static_check
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_t100_message.
    INTERFACES if_t100_dyn_msg.
    INTERFACES if_abap_behv_message.

    CONSTANTS:
      BEGIN OF loan_locked,
        msgid TYPE symsgid VALUE 'ZRAP_LMSG_###',
        msgno TYPE symsgno VALUE '001',
        attr1 TYPE scx_attrname VALUE 'MV_BORROWER',
        attr2 TYPE scx_attrname VALUE 'MV_USER_NAME',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF loan_locked,
      BEGIN OF no_auth_create,
        msgid TYPE symsgid VALUE 'ZRAP_LMSG_###',
        msgno TYPE symsgno VALUE '002',
        attr1 TYPE scx_attrname VALUE '',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF no_auth_create,
      BEGIN OF no_auth_approve,
        msgid TYPE symsgid VALUE 'ZRAP_LMSG_###',
        msgno TYPE symsgno VALUE '003',
        attr1 TYPE scx_attrname VALUE '',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF no_auth_approve,
      BEGIN OF no_auth_lend,
        msgid TYPE symsgid VALUE 'ZRAP_LMSG_###',
        msgno TYPE symsgno VALUE '004',
        attr1 TYPE scx_attrname VALUE 'MV_BORROWER',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF no_auth_lend,
      BEGIN OF only_creator,
        msgid TYPE symsgid VALUE 'ZRAP_LMSG_###',
        msgno TYPE symsgno VALUE '005',
        attr1 TYPE scx_attrname VALUE 'MV_USER_NAME',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF only_creator,
      BEGIN OF no_auth_item,
        msgid TYPE symsgid VALUE 'ZRAP_LMSG_###',
        msgno TYPE symsgno VALUE '006',
        attr1 TYPE scx_attrname VALUE 'MV_EQUIPMENT',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF no_auth_item,
      BEGIN OF no_auth_add_item,
        msgid TYPE symsgid VALUE 'ZRAP_LMSG_###',
        msgno TYPE symsgno VALUE '007',
        attr1 TYPE scx_attrname VALUE '',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF no_auth_add_item,
      BEGIN OF loan_approved,
        msgid TYPE symsgid VALUE 'ZRAP_LMSG_###',
        msgno TYPE symsgno VALUE '008',
        attr1 TYPE scx_attrname VALUE 'MV_BORROWER',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF loan_approved,
      BEGIN OF loan_lent,
        msgid TYPE symsgid VALUE 'ZRAP_LMSG_###',
        msgno TYPE symsgno VALUE '009',
        attr1 TYPE scx_attrname VALUE 'MV_BORROWER',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF loan_lent,
      BEGIN OF reminder_sent,
        msgid TYPE symsgid VALUE 'ZRAP_LMSG_###',
        msgno TYPE symsgno VALUE '010',
        attr1 TYPE scx_attrname VALUE 'MV_BORROWER',
        attr2 TYPE scx_attrname VALUE 'MV_COUNT',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF reminder_sent,
      BEGIN OF posting_failed,
        msgid TYPE symsgid VALUE 'ZRAP_LMSG_###',
        msgno TYPE symsgno VALUE '011',
        attr1 TYPE scx_attrname VALUE 'MV_EQUIPMENT',
        attr2 TYPE scx_attrname VALUE 'MV_TEXT',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF posting_failed,
      BEGIN OF enter_borrower,
        msgid TYPE symsgid VALUE 'ZRAP_LMSG_###',
        msgno TYPE symsgno VALUE '012',
        attr1 TYPE scx_attrname VALUE '',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF enter_borrower,
      BEGIN OF borrower_unknown,
        msgid TYPE symsgid VALUE 'ZRAP_LMSG_###',
        msgno TYPE symsgno VALUE '013',
        attr1 TYPE scx_attrname VALUE 'MV_BORROWER',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF borrower_unknown,
      BEGIN OF equipment_unknown,
        msgid TYPE symsgid VALUE 'ZRAP_LMSG_###',
        msgno TYPE symsgno VALUE '014',
        attr1 TYPE scx_attrname VALUE 'MV_EQUIPMENT',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF equipment_unknown,
      BEGIN OF stock_too_low,
        msgid TYPE symsgid VALUE 'ZRAP_LMSG_###',
        msgno TYPE symsgno VALUE '015',
        attr1 TYPE scx_attrname VALUE 'MV_EQUIPMENT',
        attr2 TYPE scx_attrname VALUE 'MV_COUNT',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF stock_too_low,
      BEGIN OF wrong_status,
        msgid TYPE symsgid VALUE 'ZRAP_LMSG_###',
        msgno TYPE symsgno VALUE '016',
        attr1 TYPE scx_attrname VALUE 'MV_STATUS',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF wrong_status,
      BEGIN OF loan_returned,
        msgid TYPE symsgid VALUE 'ZRAP_LMSG_###',
        msgno TYPE symsgno VALUE '017',
        attr1 TYPE scx_attrname VALUE 'MV_BORROWER',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF loan_returned.

    METHODS constructor
      IMPORTING
        textid    LIKE if_t100_message=>t100key OPTIONAL
        severity  TYPE if_abap_behv_message=>t_severity OPTIONAL
        previous  LIKE previous OPTIONAL
        borrower  TYPE /dmo/customer_id OPTIONAL
        user_name TYPE abp_creation_user OPTIONAL
        equipment TYPE zrap_equip_id_### OPTIONAL
        text      TYPE string OPTIONAL
        count     TYPE i OPTIONAL
        status    TYPE zrap_loan_status_### OPTIONAL.

    " values for &1..&4 - the constants' attr1..attr4 point to these names
    DATA mv_borrower  TYPE /dmo/customer_id READ-ONLY.
    DATA mv_user_name TYPE abp_creation_user READ-ONLY.
    DATA mv_equipment TYPE zrap_equip_id_### READ-ONLY.
    DATA mv_text      TYPE c LENGTH 50 READ-ONLY.
    DATA mv_count     TYPE c LENGTH 10 READ-ONLY.
    DATA mv_status    TYPE zrap_loan_status_### READ-ONLY.

  PROTECTED SECTION.
  PRIVATE SECTION.
ENDCLASS.

CLASS zcm_rap_loan_### IMPLEMENTATION.

  METHOD constructor ##ADT_SUPPRESS_GENERATION.
    super->constructor( previous = previous ).

    mv_borrower  = borrower.
    mv_user_name = user_name.
    mv_equipment = equipment.
    mv_text      = text.
    mv_count     = condense( CONV string( count ) ).
    mv_status    = status.

    " no severity given -> error
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

잠금 객체 설정:

| 항목 | 값 |
|---|---|
| Name / Description | `EZRAP_LOAN_###` / Lock equipment loan ### |
| Primary Table / Lock Mode | `ZRAP_LOAN_###` / Write Lock |
| Secondary Table / Lock Mode | `ZRAP_LOANI_###` / Write Lock (외래 키 없이 `loan_uuid`로 연결되면 그대로 둠) |
| Lock Parameters | `CLIENT`, `LOAN_UUID` |

왜 이렇게 쓰나

- **이 BO 전용 메시지 클래스를 둔 이유**: 다른 문제들이 `ZCM_RAP_###`에 번호를 계속 덧붙이므로, 이 문제는 독립 실습이 되도록 `ZRAP_LMSG_###`/`ZCM_RAP_LOAN_###`를 따로 만들었습니다. 구조는 R-02와 같습니다. 5단계의 보조 클래스가 이 예외 객체를 만들어 주는 "메시지 공장" 역할을 합니다.
- `mv_count`를 문자로 둔 이유: T100 자리표시자 치환은 속성 값을 문자로 바꿔 넣습니다. 정수로 두어도 대체로 되지만, 길이와 공백을 확실히 하려고 생성자에서 문자로 바꿉니다.
- **잠금 객체**: managed BO의 기본 잠금(`lock master`)은 프레임워크가 활성 테이블 기준으로 알아서 잠급니다. `lock master unmanaged`를 쓰면 그 일을 우리가 직접 하므로, 직접 잠금 객체를 만들어야 합니다. ABAP Cloud에서는 `ENQUEUE_...` 함수 모듈 대신 `CL_ABAP_LOCK_OBJECT_FACTORY`로 잠금 객체를 씁니다(6단계).

자주 나는 오류와 해결

- 메시지 텍스트에 `&1`이 그대로 보이면 상수의 `attr1` 값(속성 이름)을 대문자로 정확히 적었는지 확인하세요.
- 잠금 객체 생성 마법사에서 Primary Table을 지정하지 않으면 다음 화면으로 넘어가지 않습니다. 보조 테이블은 선택 사항입니다.

</details>

#### 4단계. CDS 데이터 모델, draft 테이블, 데이터 생성 클래스

요구사항

1. 루트 뷰 `ZRAP_R_LOAN_###`: `zrap_loan_###`에서 select, 모든 필드를 CamelCase 별칭으로(`LoanUUID`, `BorrowerID`, `BeginDate`, `EndDate`, `Status`, `Description`, `ApprovedBy`, `ReminderCount`, `CreatedBy`, `CreatedAt`, `LocalLastChangedBy`, `LocalLastChangedAt`, `LastChangedAt`), 자식으로의 composition `_Item`.
2. 자식 뷰 `ZRAP_R_LOANITEM_###`: `zrap_loani_###`에서 select(`ItemUUID`, `LoanUUID`, `EquipmentID`, `Quantity`, `ItemNote`, `LocalLastChangedAt`), 부모로의 `association to parent ... as _Loan`.
3. draft 테이블 `ZRAP_LOAN_D_###`, `ZRAP_LOANI_D_###`: 필드 이름은 CDS 별칭을 소문자로, `"%admin" : include sych_bdl_draft_admin_inc`. (5단계 BDEF의 퀵픽스로 만들어도 됩니다. 아래 코드와 같은지 비교하세요.)
4. 데이터 생성 클래스 `ZCL_RAP_LOAN_GEN_###`(`if_oo_adt_classrun`):
   - 정적 메서드 `reset_data`: 활성·draft 테이블 4개, 자산, 스위치를 지우고 데모 데이터를 넣습니다.
   - 정적 메서드 `set_switch( switch_id, value )`: 값이 비어 있으면 스위치 행을 지우고, 아니면 넣거나 바꿉니다.
   - 상수 `c_other_user = 'OTHERUSER'`(다른 사람이 만든 대여를 흉내).
   - 자산 4개: `EQ-BEAMER`(Beamer, 재고 3), `EQ-LAPTOP`(Laptop, 5), `EQ-CAMERA`(Camera, 1), `EQ-TRIPOD`(Tripod, 4), 모두 차단 아님.
   - 대여 3건(생성자는 현재 사용자, 단 L3만 `OTHERUSER`): L1 고객 `000001` 상태 N "Beamer for workshop", 품목 EQ-BEAMER 1개 / L2 고객 `000002` 상태 A(승인자 현재 사용자) "Laptops for trainees", 품목 EQ-LAPTOP 2개, EQ-CAMERA 1개 / L3 고객 `000003` 상태 N "Tripods (other user)", 품목 EQ-TRIPOD 2개.

**직접 추가할 어노테이션**
- `@AccessControl.authorizationCheck` — 두 뷰 모두 DCL 검사가 필요한지.
- `@EndUserText.label` — 뷰 설명.
- `@Semantics.user.createdBy`, `@Semantics.systemDateTime.createdAt` — 생성자/생성 시각을 managed 프레임워크가 자동으로 채우게 함.
- `@Semantics.user.localInstanceLastChangedBy`, `@Semantics.systemDateTime.localInstanceLastChangedAt` — 인스턴스 변경자와 ETag 시각을 자동으로 채우게 함(품목에도 ETag 필드에 필요).
- `@Semantics.systemDateTime.lastChangedAt` — total ETag 시각을 자동으로 채우게 함.

**확인** 두 뷰, 두 draft 테이블, 클래스가 활성화됩니다(뷰 두 개는 서로를 참조하므로 함께 활성화: Ctrl+Shift+F3). 생성 클래스를 F9로 실행하면 콘솔에 `Assets: 4, Loans: 3, Items: 4`가 나오고, `ZRAP_R_LOAN_###` Data Preview에 3건이 보입니다.

<details><summary>정답·해설</summary>

루트 뷰:

```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED          // DCL 없음
@EndUserText.label: 'Equipment loan ###'
define root view entity ZRAP_R_LOAN_###
  as select from zrap_loan_###
  composition [0..*] of ZRAP_R_LOANITEM_### as _Item     // 자식: 대여 품목
{
  key loan_uuid             as LoanUUID,
      borrower_id           as BorrowerID,
      begin_date            as BeginDate,
      end_date              as EndDate,
      status                as Status,
      description           as Description,
      approved_by           as ApprovedBy,
      reminder_count        as ReminderCount,
      @Semantics.user.createdBy: true                      // 생성 시 사용자 자동 기입
      created_by            as CreatedBy,
      @Semantics.systemDateTime.createdAt: true            // 생성 시각 자동 기입
      created_at            as CreatedAt,
      @Semantics.user.localInstanceLastChangedBy: true     // 인스턴스 변경자 자동 기입
      local_last_changed_by as LocalLastChangedBy,
      @Semantics.systemDateTime.localInstanceLastChangedAt: true  // ETag 필드 자동 갱신
      local_last_changed_at as LocalLastChangedAt,
      @Semantics.systemDateTime.lastChangedAt: true        // total ETag 필드 자동 갱신
      last_changed_at       as LastChangedAt,

      _Item
}
```

자식 뷰:

```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Equipment loan item ###'
define view entity ZRAP_R_LOANITEM_###
  as select from zrap_loani_###
  association to parent ZRAP_R_LOAN_### as _Loan on $projection.LoanUUID = _Loan.LoanUUID
{
  key item_uuid             as ItemUUID,
      loan_uuid             as LoanUUID,
      equipment_id          as EquipmentID,
      quantity              as Quantity,
      item_note             as ItemNote,
      @Semantics.systemDateTime.localInstanceLastChangedAt: true  // 품목 ETag
      local_last_changed_at as LocalLastChangedAt,

      _Loan
}
```

(→ 어노테이션 탭: @Semantics.user.createdBy, @Semantics.systemDateTime.localInstanceLastChangedAt, @Semantics.systemDateTime.lastChangedAt)

draft 테이블 두 개:

```cds
@EndUserText.label : 'Draft table for entity ZRAP_R_LOAN_###'
@AbapCatalog.enhancement.category : #EXTENSIBLE_ANY
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table zrap_loan_d_### {

  key mandt          : mandt not null;
  key loanuuid       : sysuuid_x16 not null;
  borrowerid         : /dmo/customer_id;
  begindate          : /dmo/begin_date;
  enddate            : /dmo/end_date;
  status             : zrap_loan_status_###;
  description        : /dmo/description;
  approvedby         : abap.char(12);
  remindercount      : abap.int1;
  createdby          : abp_creation_user;
  createdat          : abp_creation_tstmpl;
  locallastchangedby : abp_locinst_lastchange_user;
  locallastchangedat : abp_locinst_lastchange_tstmpl;
  lastchangedat      : abp_lastchange_tstmpl;
  "%admin"           : include sych_bdl_draft_admin_inc;

}
```

```cds
@EndUserText.label : 'Draft table for entity ZRAP_R_LOANITEM_###'
@AbapCatalog.enhancement.category : #EXTENSIBLE_ANY
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table zrap_loani_d_### {

  key mandt          : mandt not null;
  key itemuuid       : sysuuid_x16 not null;
  loanuuid           : sysuuid_x16;
  equipmentid        : zrap_equip_id_###;
  quantity           : zrap_loan_qty_###;
  itemnote           : /dmo/description;
  locallastchangedat : abp_locinst_lastchange_tstmpl;
  "%admin"           : include sych_bdl_draft_admin_inc;

}
```

| draft 테이블 | 필드 | 키 | 데이터 엘리먼트 | 설명 |
|---|---|---|---|---|
| `ZRAP_LOAN_D_###` | mandt | X | mandt | 클라이언트 |
| | loanuuid | X | sysuuid_x16 | CDS 별칭 `LoanUUID`와 같은 이름 |
| | borrowerid ~ lastchangedat | | 활성 테이블과 같음 | CDS 별칭과 같은 이름(소문자) |
| | "%admin" | | sych_bdl_draft_admin_inc | draft 관리 필드(include) |
| `ZRAP_LOANI_D_###` | mandt / itemuuid | X | mandt / sysuuid_x16 | |
| | loanuuid ~ locallastchangedat | | 활성 테이블과 같음 | |
| | "%admin" | | sych_bdl_draft_admin_inc | |

데이터 생성 클래스:

```abap
CLASS zcl_rap_loan_gen_### DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_oo_adt_classrun.

    CONSTANTS c_other_user TYPE abp_creation_user VALUE 'OTHERUSER'.

    "! Deletes all exercise data and creates the demo data again
    CLASS-METHODS reset_data.

    "! Sets (or with an empty value: deletes) an authorization switch
    CLASS-METHODS set_switch
      IMPORTING switch_id TYPE zrap_loansw_###-switch_id
                value     TYPE zrap_loansw_###-switch_value OPTIONAL.

  PROTECTED SECTION.
  PRIVATE SECTION.
    CLASS-METHODS new_uuid
      RETURNING VALUE(uuid) TYPE sysuuid_x16.
ENDCLASS.

CLASS zcl_rap_loan_gen_### IMPLEMENTATION.

  METHOD if_oo_adt_classrun~main.
    reset_data( ).

    SELECT COUNT( * ) FROM zrap_asset_### INTO @DATA(asset_count).
    SELECT COUNT( * ) FROM zrap_loan_###  INTO @DATA(loan_count).
    SELECT COUNT( * ) FROM zrap_loani_### INTO @DATA(item_count).
    out->write( |Assets: { asset_count }, Loans: { loan_count }, Items: { item_count }| ).
  ENDMETHOD.

  METHOD reset_data.
    DELETE FROM zrap_loani_d_###.
    DELETE FROM zrap_loan_d_###.
    DELETE FROM zrap_loani_###.
    DELETE FROM zrap_loan_###.
    DELETE FROM zrap_asset_###.
    DELETE FROM zrap_loansw_###.

    "legacy assets
    INSERT zrap_asset_### FROM TABLE @( VALUE #(
      ( EquipmentID = 'EQ-BEAMER' EquipmentName = 'Beamer' Stock = 3 IsBlocked = abap_false )
      ( EquipmentID = 'EQ-LAPTOP' EquipmentName = 'Laptop' Stock = 5 IsBlocked = abap_false )
      ( EquipmentID = 'EQ-CAMERA' EquipmentName = 'Camera' Stock = 1 IsBlocked = abap_false )
      ( EquipmentID = 'EQ-TRIPOD' EquipmentName = 'Tripod' Stock = 4 IsBlocked = abap_false ) ) ).

    DATA(me_user) = CONV abp_creation_user( cl_abap_context_info=>get_user_technical_name( ) ).
    DATA(now)     = cl_abap_tstmp=>utclong2tstmp( utclong_current( ) ).
    DATA(today)   = cl_abap_context_info=>get_system_date( ).

    DATA(l1) = new_uuid( ).
    DATA(l2) = new_uuid( ).
    DATA(l3) = new_uuid( ).

    INSERT zrap_loan_### FROM TABLE @( VALUE #(
      ( loan_uuid = l1 borrower_id = '000001' begin_date = today end_date = today + 7
        status = 'N' description = 'Beamer for workshop'
        created_by = me_user created_at = now local_last_changed_by = me_user
        local_last_changed_at = now last_changed_at = now )
      ( loan_uuid = l2 borrower_id = '000002' begin_date = today end_date = today + 14
        status = 'A' approved_by = me_user description = 'Laptops for trainees'
        created_by = me_user created_at = now local_last_changed_by = me_user
        local_last_changed_at = now last_changed_at = now )
      ( loan_uuid = l3 borrower_id = '000003' begin_date = today end_date = today + 3
        status = 'N' description = 'Tripods (other user)'
        created_by = c_other_user created_at = now local_last_changed_by = c_other_user
        local_last_changed_at = now last_changed_at = now ) ) ).

    INSERT zrap_loani_### FROM TABLE @( VALUE #(
      ( item_uuid = new_uuid( ) loan_uuid = l1 equipment_id = 'EQ-BEAMER' quantity = 1 local_last_changed_at = now )
      ( item_uuid = new_uuid( ) loan_uuid = l2 equipment_id = 'EQ-LAPTOP' quantity = 2 local_last_changed_at = now )
      ( item_uuid = new_uuid( ) loan_uuid = l2 equipment_id = 'EQ-CAMERA' quantity = 1 local_last_changed_at = now )
      ( item_uuid = new_uuid( ) loan_uuid = l3 equipment_id = 'EQ-TRIPOD' quantity = 2 local_last_changed_at = now ) ) ).
  ENDMETHOD.

  METHOD set_switch.
    IF value IS INITIAL.
      DELETE FROM zrap_loansw_### WHERE switch_id = @switch_id.
    ELSE.
      MODIFY zrap_loansw_### FROM @( VALUE #( switch_id = switch_id switch_value = value ) ).
    ENDIF.
  ENDMETHOD.

  METHOD new_uuid.
    TRY.
        uuid = cl_system_uuid=>create_uuid_x16_static( ).
      CATCH cx_uuid_error INTO DATA(uuid_error).
        RAISE SHORTDUMP uuid_error.
    ENDTRY.
  ENDMETHOD.

ENDCLASS.
```

왜 이렇게 쓰나

- draft 테이블 필드 이름은 CDS 별칭과 같아야 프레임워크가 자동 매핑합니다(R-01과 같은 규칙). UUID 키라서 R-01처럼 `DRAFTUUID` 키가 필요 없습니다(그건 late numbering 때문이었습니다).
- `set_switch`는 콘솔 클래스(RAP 바깥)에서만 부르므로 DB를 바로 바꿔도 됩니다. 12단계 테스트 클래스는 스위치를 바꾼 뒤 `COMMIT WORK`로 확정한 다음 RAP 요청을 보냅니다.
- L3의 생성자를 일부러 다른 사용자로 넣어 두면, 7단계의 "생성자만 수정 가능" 인스턴스 권한을 한 사람이 시험할 수 있습니다.

자주 나는 오류와 해결

- `ZRAP_R_LOAN_###`만 먼저 활성화하면 "ZRAP_R_LOANITEM_### does not exist"가 납니다. 두 뷰를 함께 활성화하세요.
- `begin_date`/`end_date`에 넣는 값은 날짜형(`d`)이어야 합니다. `cl_abap_context_info=>get_system_date( )`는 날짜형을 돌려주므로 `today + 7`은 7일 뒤 날짜가 됩니다.
- 생성 클래스를 5단계 BDEF보다 먼저 실행해도 됩니다. 이 클래스는 RAP를 거치지 않고 ABAP SQL로 바로 씁니다.

</details>

#### 5단계. BDEF: unmanaged lock, 세분 권한, 자식 권한 마스터, ABP 보조 클래스

요구사항

1. BDEF `ZRAP_R_LOAN_###`(루트 뷰에서 New → Behavior Definition)를 만드세요. 머리 부분:
   - managed, **BO 전체에 추가 저장**(9단계 세이버의 `save_modified`), 행동 풀 `ZBP_RAP_R_LOAN_###`, strict 모드 2, draft 사용.
   - **ABP 보조 클래스** `ZCL_RAP_LOAN_AUX_###` 선언.
2. 루트 `Loan`(별칭):
   - 활성/draft 테이블 지정, **잠금은 직접 구현하는 lock master**(+ total ETag `LastChangedAt`), ETag `LocalLastChangedAt`, 권한 마스터는 전역 + 인스턴스.
   - CUD, `LoanUUID`는 managed numbering + 읽기 전용, 상태·승인자·독촉 횟수·관리 필드는 읽기 전용, `BorrowerID` 필수.
   - 자식 생성(`_Item` create-by-association)은 **루트 update 권한에 맡기지 말고 별도의 전역 + 인스턴스 권한**으로 검사합니다.
   - 액션 `approveLoan`(결과 `$self`): **전역 권한만** 검사(승인자 역할 여부는 인스턴스와 무관).
   - 액션 `lendOut`(결과 `$self`): **인스턴스 권한만** 검사(빌리는 사람별 차단).
   - 액션 `sendReminder`(결과 `$self`): **권한 검사 없음**(누구나 독촉 가능).
   - 내부 액션 `forceReturn`(11단계 friend 확장이 호출).
   - 결정 `setInitialStatus`(create 시, on modify), 검증 `validateBorrower`(on save, create + `BorrowerID`).
   - draft 액션 Edit / Activate optimized / Discard / Resume, `Prepare`에 `validateBorrower`와 품목의 `validateEquipment` 등록.
   - 테이블 매핑(`corresponding` + 필드 대응).
3. 자식 `Item`:
   - 활성/draft 테이블, 잠금은 `_Loan`에 종속, **권한은 자식 스스로 권한 마스터(인스턴스)**, ETag `LocalLastChangedAt`.
   - update/delete, `ItemUUID` managed numbering + 읽기 전용, `LoanUUID`·ETag 읽기 전용, `EquipmentID`·`Quantity` 필수.
   - 검증 `validateEquipment`(on save, create + `EquipmentID`, `Quantity`), `_Loan` 연관(with draft), 매핑.
4. 보조 클래스 `ZCL_RAP_LOAN_AUX_###`를 만드세요(`FOR BEHAVIOR OF zrap_r_loan_###`).
   - 타입: Loan/Item의 READ IMPORT·READ RESULT 테이블 타입.
   - 상수: 상태(`new`/`approved`/`lent`/`returned`), 스위치 이름(`DENY_CREATE`, `DENY_APPROVE`, `DENY_ADD_ITEM`, `OWNER_ONLY`, `DENY_LEND_BORROWER`, `DENY_ITEM_EQUIP`).
   - 정적 메서드: `read_loans`(BorrowerID, Status, CreatedBy, ReminderCount만 `IN LOCAL MODE`로 읽음), `read_loans_all`(모든 필드, 액션 결과용), `read_items`(LoanUUID, EquipmentID, Quantity), `get_switch`, `is_switch_on`, `current_user`, `new_message`(예외 객체를 만들어 `REF TO if_abap_behv_message`로 돌려줌).
5. 활성화 순서: BDEF를 저장 → 보조 클래스를 만들고 → 둘을 함께 활성화(Ctrl+Shift+F3). 행동 풀이 없다는 경고는 6단계에서 해결합니다.

**확인** BDEF와 보조 클래스가 활성화되고, 남은 것은 "구현 클래스 `ZBP_RAP_R_LOAN_###`가 없다"는 메시지뿐입니다. 보조 클래스에서 `TYPE TABLE FOR READ RESULT zrap_r_loan_###\\loan`에 F2를 누르면 `%tky`, `%is_draft`, `LoanUUID`, `BorrowerID` 등이 보입니다.

<details><summary>정답·해설</summary>

BDEF(5단계 시점. 10·11단계에서 몇 줄이 더 붙습니다):

```bdef
managed with additional save implementation in class zbp_rap_r_loan_### unique;  // BO 전체 추가 저장 -> 세이버의 save_modified
strict ( 2 );
with draft;
auxiliary class zcl_rap_loan_aux_###;                    // ABP 보조 클래스: IN LOCAL MODE 등 행동 풀과 같은 권한

define behavior for ZRAP_R_LOAN_### alias Loan
persistent table zrap_loan_###
draft table zrap_loan_d_###
lock master unmanaged total etag LastChangedAt           // 잠금을 FOR LOCK 핸들러로 직접 구현
etag master LocalLastChangedAt
authorization master ( global, instance )                // 이 엔터티의 기본 권한 방식
{
  create;
  update;
  delete;

  field ( numbering : managed, readonly ) LoanUUID;
  field ( readonly ) Status, ApprovedBy, ReminderCount,
                     CreatedBy, CreatedAt, LocalLastChangedBy, LocalLastChangedAt, LastChangedAt;
  field ( mandatory ) BorrowerID;

  // create-by-association: 루트 update 권한 대신 별도의 전역+인스턴스 권한
  association _Item { create ( authorization : global, authorization : instance ); with draft; }

  action ( authorization : global ) approveLoan result [1] $self;    // 전역 권한만
  action ( authorization : instance ) lendOut result [1] $self;      // 인스턴스 권한만
  action ( authorization : none ) sendReminder result [1] $self;     // 권한 검사 없음
  internal action forceReturn;                                       // 행동 풀(과 friend)만 호출 가능

  determination setInitialStatus on modify { create; }
  validation validateBorrower on save { create; field BorrowerID; }

  draft action Edit;
  draft action Activate optimized;
  draft action Discard;
  draft action Resume;
  draft determine action Prepare
  {
    validation validateBorrower;
    validation Item~validateEquipment;
  }

  mapping for zrap_loan_### corresponding
  {
    LoanUUID           = loan_uuid;
    BorrowerID         = borrower_id;
    BeginDate          = begin_date;
    EndDate            = end_date;
    Status             = status;
    Description        = description;
    ApprovedBy         = approved_by;
    ReminderCount      = reminder_count;
    CreatedBy          = created_by;
    CreatedAt          = created_at;
    LocalLastChangedBy = local_last_changed_by;
    LocalLastChangedAt = local_last_changed_at;
    LastChangedAt      = last_changed_at;
  }
}

define behavior for ZRAP_R_LOANITEM_### alias Item
persistent table zrap_loani_###
draft table zrap_loani_d_###
lock dependent by _Loan
authorization master ( instance )                        // 루트가 아닌 엔터티가 스스로 권한 마스터
etag master LocalLastChangedAt
{
  update;
  delete;

  field ( numbering : managed, readonly ) ItemUUID;
  field ( readonly ) LoanUUID, LocalLastChangedAt;
  field ( mandatory ) EquipmentID, Quantity;

  validation validateEquipment on save { create; field EquipmentID, Quantity; }

  association _Loan { with draft; }

  mapping for zrap_loani_### corresponding
  {
    ItemUUID           = item_uuid;
    LoanUUID           = loan_uuid;
    EquipmentID        = equipment_id;
    Quantity           = quantity;
    ItemNote           = item_note;
    LocalLastChangedAt = local_last_changed_at;
  }
}
```

보조 클래스:

```abap
"! ABP auxiliary class of ZRAP_R_LOAN_###: reusable reads and messages.
"! Declared in the BDEF header with 'auxiliary class' - therefore it may use
"! IN LOCAL MODE and the BDEF derived types like the behavior pool itself.
CLASS zcl_rap_loan_aux_### DEFINITION
  PUBLIC
  FOR BEHAVIOR OF zrap_r_loan_###.

  PUBLIC SECTION.
    TYPES tt_loan_keys    TYPE TABLE FOR READ IMPORT zrap_r_loan_###\\loan.
    TYPES tt_loans        TYPE TABLE FOR READ RESULT zrap_r_loan_###\\loan.
    TYPES tt_item_keys    TYPE TABLE FOR READ IMPORT zrap_r_loan_###\\item.
    TYPES tt_items        TYPE TABLE FOR READ RESULT zrap_r_loan_###\\item.
    TYPES ty_switch_id    TYPE zrap_loansw_###-switch_id.
    TYPES ty_switch_value TYPE zrap_loansw_###-switch_value.

    CONSTANTS:
      BEGIN OF status,
        new      TYPE zrap_loan_status_### VALUE 'N',
        approved TYPE zrap_loan_status_### VALUE 'A',
        lent     TYPE zrap_loan_status_### VALUE 'L',
        returned TYPE zrap_loan_status_### VALUE 'R',
      END OF status,
      BEGIN OF switch,
        deny_create        TYPE ty_switch_id VALUE 'DENY_CREATE',
        deny_approve       TYPE ty_switch_id VALUE 'DENY_APPROVE',
        deny_add_item      TYPE ty_switch_id VALUE 'DENY_ADD_ITEM',
        owner_only         TYPE ty_switch_id VALUE 'OWNER_ONLY',
        deny_lend_borrower TYPE ty_switch_id VALUE 'DENY_LEND_BORROWER',
        deny_item_equip    TYPE ty_switch_id VALUE 'DENY_ITEM_EQUIP',
      END OF switch.

    "! Fields needed by authorization checks and actions
    CLASS-METHODS read_loans
      IMPORTING keys         TYPE tt_loan_keys
      RETURNING VALUE(loans) TYPE tt_loans.

    "! All fields - for action results ($self)
    CLASS-METHODS read_loans_all
      IMPORTING keys         TYPE tt_loan_keys
      RETURNING VALUE(loans) TYPE tt_loans.

    CLASS-METHODS read_items
      IMPORTING keys         TYPE tt_item_keys
      RETURNING VALUE(items) TYPE tt_items.

    CLASS-METHODS get_switch
      IMPORTING switch_id    TYPE ty_switch_id
      RETURNING VALUE(value) TYPE ty_switch_value.

    CLASS-METHODS is_switch_on
      IMPORTING switch_id TYPE ty_switch_id
      RETURNING VALUE(on) TYPE abap_bool.

    CLASS-METHODS current_user
      RETURNING VALUE(user) TYPE abp_creation_user.

    "! Message factory: one place that knows the exception class
    CLASS-METHODS new_message
      IMPORTING textid         LIKE if_t100_message=>t100key
                severity       TYPE if_abap_behv_message=>t_severity DEFAULT if_abap_behv_message=>severity-error
                borrower       TYPE /dmo/customer_id OPTIONAL
                user_name      TYPE abp_creation_user OPTIONAL
                equipment      TYPE zrap_equip_id_### OPTIONAL
                text           TYPE string OPTIONAL
                count          TYPE i OPTIONAL
                status         TYPE zrap_loan_status_### OPTIONAL
      RETURNING VALUE(message) TYPE REF TO if_abap_behv_message.

  PROTECTED SECTION.
  PRIVATE SECTION.
ENDCLASS.

CLASS zcl_rap_loan_aux_### IMPLEMENTATION.

  METHOD read_loans.
    READ ENTITIES OF zrap_r_loan_### IN LOCAL MODE
      ENTITY Loan
        FIELDS ( BorrowerID Status CreatedBy ReminderCount )
        WITH keys
      RESULT loans.
  ENDMETHOD.

  METHOD read_loans_all.
    READ ENTITIES OF zrap_r_loan_### IN LOCAL MODE
      ENTITY Loan
        ALL FIELDS
        WITH keys
      RESULT loans.
  ENDMETHOD.

  METHOD read_items.
    READ ENTITIES OF zrap_r_loan_### IN LOCAL MODE
      ENTITY Item
        FIELDS ( LoanUUID EquipmentID Quantity )
        WITH keys
      RESULT items.
  ENDMETHOD.

  METHOD get_switch.
    SELECT SINGLE switch_value FROM zrap_loansw_###
      WHERE switch_id = @switch_id
      INTO @value.
  ENDMETHOD.

  METHOD is_switch_on.
    on = xsdbool( get_switch( switch_id ) IS NOT INITIAL ).
  ENDMETHOD.

  METHOD current_user.
    user = CONV #( cl_abap_context_info=>get_user_technical_name( ) ).
  ENDMETHOD.

  METHOD new_message.
    message = NEW zcm_rap_loan_###( textid    = textid
                                    severity  = severity
                                    borrower  = borrower
                                    user_name = user_name
                                    equipment = equipment
                                    text      = text
                                    count     = count
                                    status    = status ).
  ENDMETHOD.

ENDCLASS.
```

왜 이렇게 쓰나

- **`lock master unmanaged`** (릴리스 뉴스: 7.55 / 클라우드 2005): managed BO인데 잠금만 직접 구현합니다. 그러면 프레임워크는 update·delete·create-by-association·액션 직전에 우리 `FOR LOCK` 핸들러를 부릅니다(키워드 문서 `lock master [unmanaged]`). 쓰는 경우: 기존 레거시 프로그램과 **같은 잠금 객체를 공유**해야 할 때(레거시 트랜잭션과 RAP 앱이 서로를 막아야 함), 잠금 단위가 테이블 키와 다를 때(예: 기자재 단위로 잠가야 함), 잠금과 함께 다른 자원도 잠가야 할 때입니다. 자식은 `lock dependent by _Loan`이므로 품목 변경도 루트 잠금 요청으로 바뀌어 같은 핸들러가 불립니다.
- **권한을 연산마다 바꾸는 규칙** (키워드 문서 `authorization`):
  - `authorization master ( global, instance )`는 이 엔터티의 **기본값**입니다. 별도 표시가 없는 연산(update, delete, Edit)은 이 기본값대로 두 핸들러 모두 검사됩니다.
  - `action ( authorization : global )`은 기본값을 **전역 검사로 대체**합니다. 인스턴스 핸들러에는 `approveLoan`이 요청되지 않습니다. 정적 액션은 원래 인스턴스 검사를 할 수 없으므로 이런 액션에 특히 씁니다.
  - `action ( authorization : instance )`는 **인스턴스 검사로 대체**합니다(정적 연산에는 못 씀).
  - `action ( authorization : none )`은 검사하지 않습니다. 다만 CDS 읽기 권한(DCL)과 잠금·기능 제어는 그대로입니다.
  - 액션 수준 `global`/`instance`는 릴리스 뉴스 기준 7.58 / 클라우드 2305에 생겼습니다. R-03에서는 `authorization : update`(update 권한에 위임)를 썼으니 비교해 보세요.
- **자식 생성의 별도 권한** `association _Item { create ( authorization : global, authorization : instance ); }` (릴리스 뉴스: 클라우드 2508 / 9.16 "Dedicated Authorizations for Create-by-Association Operations"): 원래 create-by-association은 "부모 update 권한"으로 검사됩니다. 이제 to-child 연관이면 별도 전역/인스턴스 권한을 줄 수 있고, 핸들러 결과의 `%assoc-_Item`로 판단합니다. 두 추가 문구를 같이 쓰면 두 핸들러가 모두 불립니다.
- **루트가 아닌 엔터티를 권한 마스터로** (릴리스 뉴스: 7.58 / 클라우드 2405 "Subentities as Authorization Master"): 품목을 `authorization dependent by _Loan`이 아니라 `authorization master ( instance )`로 두면, 품목 update/delete는 **품목 자신의 `FOR INSTANCE AUTHORIZATION` 핸들러**가 판단합니다. 같은 대여 안에서도 기자재별로 권한이 다를 때 씁니다. 루트는 반드시 권한 마스터여야 하고, 나머지는 마스터와 dependent 중 고를 수 있습니다.
- **ABP 보조 클래스** (릴리스 뉴스: 클라우드 2408 / 9.12, 온프레미스 8.16): 행동 풀이 커지면 여러 사람이 동시에 고치기 어렵습니다. `auxiliary class`로 선언된 클래스는 `FOR BEHAVIOR OF`를 붙여 만들며, 행동 풀과 같은 권리를 받아 `IN LOCAL MODE`/`PRIVILEGED` EML, BDEF 파생 타입, 내부 연산, `RAISE ENTITY EVENT`를 쓸 수 있습니다. 하지만 **핸들러·세이버 메서드 자체는 반드시 행동 풀에** 있어야 하고, 보조 클래스는 그 메서드가 호출하는 도우미만 가집니다. 보조 클래스는 한 BO에만 속하고(재사용 금지), 암묵적으로 FINAL이며, 정적·인스턴스 메서드 모두 가질 수 있습니다. 비슷한 목적의 `group`(구현 그룹)은 핸들러 자체를 여러 행동 풀로 나누는 기능이라는 점이 다릅니다.
- `read_loans`는 권한·액션에 필요한 필드만 읽고, 액션 결과(`$self`)에는 전체 필드가 필요하므로 `read_loans_all`을 따로 두었습니다. `get_switch`는 핸들러마다 루프 **밖에서** 한 번만 부르도록 쓸 예정입니다.
- 파생 타입 이름의 `zrap_r_loan_###\\loan`은 "BDEF `zrap_r_loan_###` 안의 엔터티 `loan`(별칭)"이라는 뜻입니다. 공식 cheat sheet 예제 `zcl_demo_abap_abp_aux_cl96`도 같은 형태(`TYPE TABLE FOR READ RESULT zr_demo_abap96\\demo_abap`)를 씁니다.

자주 나는 오류와 해결

- 보조 클래스만 먼저 활성화하면 "BDEF에 auxiliary class로 선언되지 않았다"는 취지의 오류가, BDEF만 먼저 활성화하면 "클래스가 없다"는 오류가 날 수 있습니다. 둘을 함께 활성화하세요(정확한 문구는 실제 시스템에서 확인 필요).
- `create ( authorization : global, authorization : instance )`에서 문법 오류가 나면 시스템 릴리스가 2508보다 낮은 것입니다. 그 줄을 `create ( authorization : update )`로 바꾸고 7단계의 `%assoc-_Item` 처리 부분을 빼면 나머지는 그대로 진행할 수 있습니다.
- `authorization : instance`를 정적 액션에 붙이면 오류입니다(정적 연산은 인스턴스가 없음).

</details>

#### 6단계. 행동 풀 골격과 unmanaged lock (`FOR LOCK`)

요구사항

1. BDEF의 퀵픽스(Ctrl+1)로 행동 풀 `ZBP_RAP_R_LOAN_###`를 만들고, Local Types에 아래 세 로컬 클래스를 정의하세요.
   - `lhc_loan`: 전역/인스턴스 권한, `lock`, 액션 4개(`approveLoan`, `lendOut`, `sendReminder`, `forceReturn`), 결정 `setInitialStatus`, 검증 `validateBorrower`.
   - `lhc_item`: 인스턴스 권한, 검증 `validateEquipment`.
   - `lsc_zrap_r_loan_###`: 일단 `CL_ABAP_BEHAVIOR_SAVER` 상속, `save_modified`, `cleanup_finalize`(9단계에서 상위 클래스를 바꿉니다).
2. 이 단계에서는 `lock`만 구현하고 나머지는 빈 메서드로 둡니다(7·8·9단계에서 채움).
3. `lock` 구현:
   - `cl_abap_lock_object_factory=>get_instance( 'EZRAP_LOAN_###' )`. 잠금 객체를 못 얻는 기술 오류(`cx_abap_lock_failure`)는 `RAISE SHORTDUMP`.
   - 메시지에 쓸 빌리는 사람 번호를 활성 테이블에서 한 번에(`FOR ALL ENTRIES`) 읽습니다.
   - 키마다 `enqueue( it_parameter = ( name = 'LOAN_UUID' ... ) )`. 다른 사용자가 잠갔으면(`cx_abap_foreign_lock`) `failed-loan`에 `%fail-cause = locked`, `reported-loan`에 메시지 001(빌리는 사람, 잠근 사용자 = 예외의 `user_name`).

**확인** 행동 풀이 활성화됩니다. 잠금 충돌 자체는 12단계에서 확인합니다. 지금은 `lock` 메서드에 중단점을 걸고, 정답의 짧은 EML 코드(L1 설명 변경)를 아무 콘솔 클래스에 붙여 F9로 실행하세요. 디버거가 `lock`에서 멈추고 `keys`에 L1의 UUID 한 줄이 보이면 성공입니다.

<details><summary>정답·해설</summary>

글로벌 클래스(퀵픽스가 만든 그대로):

```abap
CLASS zbp_rap_r_loan_### DEFINITION PUBLIC ABSTRACT FINAL FOR BEHAVIOR OF zrap_r_loan_###.
ENDCLASS.

CLASS zbp_rap_r_loan_### IMPLEMENTATION.
ENDCLASS.
```

Local Types(CCIMP) 전체 — 6단계 시점:

```abap
CLASS lhc_loan DEFINITION INHERITING FROM cl_abap_behavior_handler.
  PRIVATE SECTION.

    METHODS get_global_authorizations FOR GLOBAL AUTHORIZATION
      IMPORTING REQUEST requested_authorizations FOR Loan RESULT result.

    METHODS get_instance_authorizations FOR INSTANCE AUTHORIZATION
      IMPORTING keys REQUEST requested_authorizations FOR Loan RESULT result.

    METHODS lock FOR LOCK
      IMPORTING keys FOR LOCK Loan.

    METHODS approveLoan FOR MODIFY
      IMPORTING keys FOR ACTION Loan~approveLoan RESULT result.

    METHODS lendOut FOR MODIFY
      IMPORTING keys FOR ACTION Loan~lendOut RESULT result.

    METHODS sendReminder FOR MODIFY
      IMPORTING keys FOR ACTION Loan~sendReminder RESULT result.

    METHODS forceReturn FOR MODIFY
      IMPORTING keys FOR ACTION Loan~forceReturn.

    METHODS setInitialStatus FOR DETERMINE ON MODIFY
      IMPORTING keys FOR Loan~setInitialStatus.

    METHODS validateBorrower FOR VALIDATE ON SAVE
      IMPORTING keys FOR Loan~validateBorrower.

ENDCLASS.

CLASS lhc_loan IMPLEMENTATION.

  METHOD get_global_authorizations.
    "step 7
  ENDMETHOD.

  METHOD get_instance_authorizations.
    "step 7
  ENDMETHOD.

  METHOD lock.

    "1) lock object - a technical failure here is a programming/system error
    TRY.
        DATA(lock_object) = cl_abap_lock_object_factory=>get_instance( iv_name = 'EZRAP_LOAN_###' ).
      CATCH cx_abap_lock_failure INTO DATA(lock_failure).
        RAISE SHORTDUMP lock_failure.
    ENDTRY.

    "2) borrower IDs for the message text - one SELECT for all keys
    "   (only active instances are locked, so the active table is the right source)
    SELECT FROM zrap_loan_###
      FIELDS loan_uuid, borrower_id
      FOR ALL ENTRIES IN @keys
      WHERE loan_uuid = @keys-LoanUUID
      INTO TABLE @DATA(borrowers).

    "3) enqueue each instance; a foreign lock is a normal business situation
    LOOP AT keys ASSIGNING FIELD-SYMBOL(<key>).
      TRY.
          lock_object->enqueue(
            it_parameter = VALUE #( ( name  = 'LOAN_UUID'
                                      value = REF #( <key>-LoanUUID ) ) ) ).

        CATCH cx_abap_foreign_lock INTO DATA(foreign_lock).
          APPEND VALUE #( LoanUUID    = <key>-LoanUUID
                          %fail-cause = if_abap_behv=>cause-locked ) TO failed-loan.
          APPEND VALUE #( LoanUUID = <key>-LoanUUID
                          %msg     = zcl_rap_loan_aux_###=>new_message(
                                       textid    = zcm_rap_loan_###=>loan_locked
                                       borrower  = VALUE #( borrowers[ loan_uuid = <key>-LoanUUID ]-borrower_id OPTIONAL )
                                       user_name = CONV #( foreign_lock->user_name ) ) ) TO reported-loan.

        CATCH cx_abap_lock_failure INTO lock_failure.
          RAISE SHORTDUMP lock_failure.
      ENDTRY.
    ENDLOOP.

  ENDMETHOD.

  METHOD approveLoan.
    "step 8
  ENDMETHOD.

  METHOD lendOut.
    "step 8
  ENDMETHOD.

  METHOD sendReminder.
    "step 8
  ENDMETHOD.

  METHOD forceReturn.
    "step 8
  ENDMETHOD.

  METHOD setInitialStatus.
    "step 8
  ENDMETHOD.

  METHOD validateBorrower.
    "step 8
  ENDMETHOD.

ENDCLASS.

CLASS lhc_item DEFINITION INHERITING FROM cl_abap_behavior_handler.
  PRIVATE SECTION.

    METHODS get_instance_authorizations FOR INSTANCE AUTHORIZATION
      IMPORTING keys REQUEST requested_authorizations FOR Item RESULT result.

    METHODS validateEquipment FOR VALIDATE ON SAVE
      IMPORTING keys FOR Item~validateEquipment.

ENDCLASS.

CLASS lhc_item IMPLEMENTATION.

  METHOD get_instance_authorizations.
    "step 7
  ENDMETHOD.

  METHOD validateEquipment.
    "step 8
  ENDMETHOD.

ENDCLASS.

CLASS lsc_zrap_r_loan_### DEFINITION INHERITING FROM cl_abap_behavior_saver.
  PROTECTED SECTION.
    METHODS save_modified REDEFINITION.
    METHODS cleanup_finalize REDEFINITION.
ENDCLASS.

CLASS lsc_zrap_r_loan_### IMPLEMENTATION.

  METHOD save_modified.
    "step 9
  ENDMETHOD.

  METHOD cleanup_finalize.
  ENDMETHOD.

ENDCLASS.
```

중단점 확인용 짧은 EML(아무 콘솔 클래스의 `main`에 붙여 실행):

```abap
SELECT SINGLE loan_uuid FROM zrap_loan_### WHERE borrower_id = '000001' INTO @DATA(l1).
MODIFY ENTITIES OF zrap_r_loan_###
  ENTITY Loan
    UPDATE FIELDS ( Description )
    WITH VALUE #( ( LoanUUID = l1 Description = 'lock test' ) )   " %is_draft initial = active instance
  FAILED DATA(failed)
  REPORTED DATA(reported).
ROLLBACK ENTITIES.
out->write( |failed lines: { lines( failed-loan ) }| ).
```

클래스 구조 해설

- `METHODS lock FOR LOCK IMPORTING keys FOR LOCK Loan`: BDEF의 `lock master unmanaged` 줄 때문에 생기는 메서드입니다(키워드 문서 `FOR LOCK`). `keys`는 `TABLE FOR LOCK` 타입으로 잠글 인스턴스의 키만 들어 있고, `failed`/`reported`는 암묵적인 CHANGING 파라미터입니다. 이름(`lock`)은 자유입니다.
- 언제 불리나: update, delete, create-by-association(품목 추가), 액션 실행 직전에 프레임워크가 부릅니다. 품목(`lock dependent by _Loan`) 변경은 루트 키로 바뀌어 이 메서드가 불립니다. draft BO에서는 활성 인스턴스에 대해 `Edit`(draft 생성)과 `Resume` 때도 불립니다. EML `SET LOCKS`도 이 메서드로 옵니다.
- `failed-loan`에 `LoanUUID`만 넣고 `%tky`를 쓰지 않은 이유: 잠금은 활성 인스턴스에만 걸리므로 `%is_draft`는 초기값(= 활성)이어야 합니다. 키 필드를 직접 넣으면 그대로 그렇게 됩니다.

왜 이렇게 쓰나

- 공식 Flight Reference Scenario의 unmanaged Travel(`/DMO/BP_TRAVEL_U`의 `lock`)과 같은 구조입니다: 잠금 객체 인스턴스를 얻고, 키마다 `enqueue`, `cx_abap_foreign_lock`은 업무 메시지로, `cx_abap_lock_failure`는 `RAISE SHORTDUMP`.
- `cx_abap_foreign_lock`의 `user_name`으로 "누가 잡고 있는지"를 보여 주면 사용자가 연락할 수 있습니다.
- 잠금은 RAP 트랜잭션(SAP LUW)이 끝날 때(`COMMIT ENTITIES`/`ROLLBACK ENTITIES` 또는 세션 종료) 풀립니다. 그래서 직접 `dequeue`하지 않습니다.
- **draft와 unmanaged lock** (주의): draft BO는 Edit 뒤 일정 시간 "배타 잠금 단계"를 유지합니다. 프레임워크가 이것을 우리 잠금과 어떻게 연결하는지(OData 요청이 끝나도 잠금이 남는지)는 문서에서 확인하지 못했습니다. Fiori에서 두 사용자로 동시에 Edit해 보는 시험은 실제 시스템에서 확인 필요입니다. 이 문제는 결정적인 EML 시나리오(12단계)로 확인합니다.

자주 나는 오류와 해결

- `LOAN_UUID`를 소문자로 쓰거나 잠금 객체에 없는 이름을 주면 `cx_abap_lock_failure`가 나서 덤프가 됩니다. 파라미터 이름은 잠금 객체 개요에 보이는 대로(대문자) 쓰세요.
- `FOR ALL ENTRIES IN @keys`에서 `keys`가 비어 있으면 전체 테이블을 읽지만, 프레임워크는 빈 `keys`로 `lock`을 부르지 않습니다.

</details>

#### 7단계. 권한 구현: 전역·인스턴스·액션별·자식 권한 마스터·cba 별도 권한

요구사항

1. `lhc_loan->get_global_authorizations`(스위치는 루프 밖에서 한 번씩 읽기):
   - `%create`: `DENY_CREATE`가 켜져 있으면 거부, 메시지 002(`%global`).
   - `%update`, `%action-Edit`, `%delete`: 전역 제한 없음(허용). 실제 판단은 인스턴스 핸들러.
   - `%action-approveLoan`: `DENY_APPROVE`가 켜져 있으면 거부, 메시지 003.
   - `%assoc-_Item`(품목 추가의 전역 부분): `DENY_ADD_ITEM`이 켜져 있으면 거부, 메시지 007.
2. `lhc_loan->get_instance_authorizations`:
   - 보조 클래스 `read_loans`로 `BorrowerID`, `CreatedBy`를 읽습니다.
   - 규칙 A(`OWNER_ONLY` 켜짐): 생성자가 현재 사용자가 아니면 `%update`, `%action-Edit`, `%delete`, `%assoc-_Item` 거부, 메시지 005(생성자 표시).
   - 규칙 B(`DENY_LEND_BORROWER` = 고객 번호): 그 고객의 대여면 `%action-lendOut` 거부, 메시지 004.
   - 요청되지 않은 항목의 메시지는 넣지 않습니다.
3. `lhc_item->get_instance_authorizations`: `DENY_ITEM_EQUIP` = 기자재 번호이면 그 기자재 품목의 `%update`, `%delete` 거부, 메시지 006(`%element-EquipmentID`, `%path`로 부모 지정).
4. `approveLoan`(global 전용), `lendOut`(instance 전용), `sendReminder`(none)가 각각 어느 핸들러에서 요청되는지 주석으로 적으세요.

**확인** 행동 풀이 활성화됩니다. 12단계 테스트에서 `DENY_APPROVE`를 켜면 `approveLoan`이 `unauthorized`로 실패하고, `OWNER_ONLY`를 켜도 L3의 `sendReminder`는 성공하는 것을 봅니다. 지금 확인하려면 F2로 `requested_authorizations`의 타입을 열어 `%action-approveLoan`은 전역 요청 타입에만, `%action-lendOut`은 인스턴스 요청 타입에만, `%action-sendReminder`는 어느 쪽에도 없는지 보세요.

<details><summary>정답·해설</summary>

`lhc_loan`의 두 메서드:

```abap
  METHOD get_global_authorizations.

    "switches read once, outside of any loop
    DATA(deny_create)   = zcl_rap_loan_aux_###=>is_switch_on( zcl_rap_loan_aux_###=>switch-deny_create ).
    DATA(deny_approve)  = zcl_rap_loan_aux_###=>is_switch_on( zcl_rap_loan_aux_###=>switch-deny_approve ).
    DATA(deny_add_item) = zcl_rap_loan_aux_###=>is_switch_on( zcl_rap_loan_aux_###=>switch-deny_add_item ).

    "create (create is always checked globally - there is no instance yet)
    IF requested_authorizations-%create = if_abap_behv=>mk-on.
      IF deny_create = abap_true.
        result-%create = if_abap_behv=>auth-unauthorized.
        APPEND VALUE #( %global = if_abap_behv=>mk-on
                        %msg    = zcl_rap_loan_aux_###=>new_message( textid = zcm_rap_loan_###=>no_auth_create ) )
               TO reported-loan.
      ELSE.
        result-%create = if_abap_behv=>auth-allowed.
      ENDIF.
    ENDIF.

    "update / Edit / delete: no global restriction - the instance check decides
    IF requested_authorizations-%update      = if_abap_behv=>mk-on
    OR requested_authorizations-%action-Edit = if_abap_behv=>mk-on.
      result-%update      = if_abap_behv=>auth-allowed.
      result-%action-Edit = if_abap_behv=>auth-allowed.
    ENDIF.
    IF requested_authorizations-%delete = if_abap_behv=>mk-on.
      result-%delete = if_abap_behv=>auth-allowed.
    ENDIF.

    "action ( authorization : global ) approveLoan -> requested ONLY here
    IF requested_authorizations-%action-approveLoan = if_abap_behv=>mk-on.
      IF deny_approve = abap_true.
        result-%action-approveLoan = if_abap_behv=>auth-unauthorized.
        APPEND VALUE #( %global = if_abap_behv=>mk-on
                        %msg    = zcl_rap_loan_aux_###=>new_message( textid = zcm_rap_loan_###=>no_auth_approve ) )
               TO reported-loan.
      ELSE.
        result-%action-approveLoan = if_abap_behv=>auth-allowed.
      ENDIF.
    ENDIF.

    "create-by-association with its own authorization (global part)
    IF requested_authorizations-%assoc-_Item = if_abap_behv=>mk-on.
      IF deny_add_item = abap_true.
        result-%assoc-_Item = if_abap_behv=>auth-unauthorized.
        APPEND VALUE #( %global = if_abap_behv=>mk-on
                        %msg    = zcl_rap_loan_aux_###=>new_message( textid = zcm_rap_loan_###=>no_auth_add_item ) )
               TO reported-loan.
      ELSE.
        result-%assoc-_Item = if_abap_behv=>auth-allowed.
      ENDIF.
    ENDIF.

    "sendReminder ( authorization : none ) is never requested.

  ENDMETHOD.

  METHOD get_instance_authorizations.

    DATA(loans)         = zcl_rap_loan_aux_###=>read_loans( CORRESPONDING #( keys ) ).
    DATA(owner_only)    = zcl_rap_loan_aux_###=>is_switch_on( zcl_rap_loan_aux_###=>switch-owner_only ).
    DATA(deny_borrower) = zcl_rap_loan_aux_###=>get_switch( zcl_rap_loan_aux_###=>switch-deny_lend_borrower ).
    DATA(me_user)       = zcl_rap_loan_aux_###=>current_user( ).

    "which requests need a message?
    DATA(change_requested) = xsdbool( requested_authorizations-%update      = if_abap_behv=>mk-on
                                   OR requested_authorizations-%action-Edit = if_abap_behv=>mk-on
                                   OR requested_authorizations-%delete      = if_abap_behv=>mk-on
                                   OR requested_authorizations-%assoc-_Item = if_abap_behv=>mk-on ).
    DATA(lend_requested)   = xsdbool( requested_authorizations-%action-lendOut = if_abap_behv=>mk-on ).

    LOOP AT loans INTO DATA(loan).

      "rule A: only the creator may change (new drafts have no other creator yet)
      DATA(change_allowed) = xsdbool( owner_only = abap_false
                                   OR loan-CreatedBy IS INITIAL
                                   OR loan-CreatedBy = me_user ).

      "rule B: action ( authorization : instance ) lendOut -> requested ONLY here
      DATA(lend_allowed) = xsdbool( deny_borrower IS INITIAL
                                 OR loan-BorrowerID <> CONV /dmo/customer_id( deny_borrower ) ).

      DATA(change_auth) = COND #( WHEN change_allowed = abap_true
                                  THEN if_abap_behv=>auth-allowed
                                  ELSE if_abap_behv=>auth-unauthorized ).

      APPEND VALUE #( %tky            = loan-%tky
                      %update         = change_auth
                      %action-Edit    = change_auth
                      %delete         = change_auth
                      %assoc-_Item    = change_auth
                      %action-lendOut = COND #( WHEN lend_allowed = abap_true
                                                THEN if_abap_behv=>auth-allowed
                                                ELSE if_abap_behv=>auth-unauthorized ) ) TO result.

      IF change_allowed = abap_false AND change_requested = abap_true.
        APPEND VALUE #( %tky = loan-%tky
                        %msg = zcl_rap_loan_aux_###=>new_message( textid    = zcm_rap_loan_###=>only_creator
                                                                  user_name = loan-CreatedBy ) ) TO reported-loan.
      ENDIF.

      IF lend_allowed = abap_false AND lend_requested = abap_true.
        APPEND VALUE #( %tky = loan-%tky
                        %msg = zcl_rap_loan_aux_###=>new_message( textid   = zcm_rap_loan_###=>no_auth_lend
                                                                  borrower = loan-BorrowerID ) ) TO reported-loan.
      ENDIF.

    ENDLOOP.

  ENDMETHOD.
```

`lhc_item`의 권한 메서드:

```abap
  METHOD get_instance_authorizations.

    DATA(items)            = zcl_rap_loan_aux_###=>read_items( CORRESPONDING #( keys ) ).
    DATA(denied_equipment) = CONV zrap_equip_id_###(
                               zcl_rap_loan_aux_###=>get_switch( zcl_rap_loan_aux_###=>switch-deny_item_equip ) ).

    LOOP AT items INTO DATA(item).

      DATA(allowed) = xsdbool( denied_equipment IS INITIAL
                            OR item-EquipmentID <> denied_equipment ).
      DATA(auth)    = COND #( WHEN allowed = abap_true
                              THEN if_abap_behv=>auth-allowed
                              ELSE if_abap_behv=>auth-unauthorized ).

      "Item is its own authorization master: update/delete are decided HERE,
      "not by the update authorization of the loan
      APPEND VALUE #( %tky    = item-%tky
                      %update = auth
                      %delete = auth ) TO result.

      IF allowed = abap_false.
        APPEND VALUE #( %tky                 = item-%tky
                        %path                = VALUE #( loan-%is_draft = item-%is_draft
                                                        loan-LoanUUID  = item-LoanUUID )
                        %element-EquipmentID = if_abap_behv=>mk-on
                        %msg                 = zcl_rap_loan_aux_###=>new_message(
                                                 textid    = zcm_rap_loan_###=>no_auth_item
                                                 equipment = item-EquipmentID ) ) TO reported-item.
      ENDIF.

    ENDLOOP.

  ENDMETHOD.
```

클래스 구조 해설

- `FOR GLOBAL AUTHORIZATION ... REQUEST requested_authorizations FOR Loan RESULT result`: `authorization master ( global, ... )`(또는 어떤 연산에 `authorization : global`)이 있으면 생깁니다. `requested_authorizations`와 `result`는 **구조**(인스턴스 없음)이고, 구성 요소는 BDEF에서 전역 검사 대상이 된 연산만 생깁니다: `%create`, `%update`, `%delete`, `%action-Edit`, `%action-approveLoan`, `%assoc-_Item`.
- `FOR INSTANCE AUTHORIZATION ... keys REQUEST requested_authorizations FOR Loan RESULT result`: `instance`가 있으면 생기고 `result`는 **테이블**(인스턴스마다 한 줄, `%tky` 포함)입니다. 구성 요소는 `%update`, `%delete`, `%action-Edit`, `%action-lendOut`, `%assoc-_Item`입니다. `approveLoan`(global 전용)과 `sendReminder`(none)는 여기에 없습니다. 이것이 `authorization : global / instance / none`의 실제 효과입니다(F2로 확인하세요. 구성 요소 이름이 다르면 그에 맞게 고치세요).
- `lhc_item`의 `FOR INSTANCE AUTHORIZATION ... FOR Item`: 품목이 `authorization master ( instance )`이기 때문에 생깁니다. 품목이 dependent였다면 이 메서드는 없고 루트의 `%update`로 판단했을 것입니다.
- 언제 불리나: 전역 핸들러는 Fiori가 버튼 표시 여부를 정할 때(권한 정보 요청)와 연산 직전에, 인스턴스 핸들러는 인스턴스 연산 직전에 불립니다. `IN LOCAL MODE` EML(행동 풀·보조 클래스·friend 안)에서는 권한 검사가 건너뛰어집니다.

왜 이렇게 쓰나

- **Edit도 update로 취급**: 공식 draft 예제 `/DMO/BP_TRAVEL_D`는 "edit is treated like update"라는 주석과 함께 `%action-Edit`를 `%update`와 같이 판단합니다. 같은 방식입니다. (키워드 문서에는 "draft 액션 Edit과 Resume에는 create 권한 검사가 적용된다"는 설명도 있으니, 실제로 어떤 요청이 오는지 디버거로 `requested_authorizations`를 보며 확인해 보세요.)
- 결과에 요청되지 않은 구성 요소까지 채워도 됩니다(공식 예제도 그렇게 함). 다만 **메시지는 요청된 경우에만** 넣어야 엉뚱한 화면에서 권한 메시지가 뜨지 않습니다.
- 전역 메시지는 `%global = mk-on`, 인스턴스 메시지는 `%tky`, 자식 메시지는 `%path`로 부모를 알려 줍니다(Fiori 메시지 팝오버의 위치).
- 실제 운영에서는 스위치 대신 `AUTHORITY-CHECK OBJECT ...`(R-03)나 직접 만든 권한 객체 + IAM 앱으로 판단합니다. 공식 cheat sheet 예제 `ZR_DEMO_ABAP96`은 권한 필드·권한 객체·IAM 앱·비즈니스 카탈로그·비즈니스 역할을 직접 만드는 절차를 보여 줍니다. 트라이얼에서 역할 할당 권한이 없을 수 있어 이 문제는 스위치로 흉내 냅니다.

자주 나는 오류와 해결

- `result-%action-approveLoan`을 인스턴스 핸들러에 쓰면 "구성 요소 없음" 문법 오류가 납니다. global 전용 액션이기 때문입니다(반대로 `lendOut`을 전역 핸들러에 써도 같음).
- `result-%assoc-_Item`이 없다고 나오면 5단계 BDEF의 cba 권한 줄이 2508 이전 문법(`authorization : update`)으로 되어 있는 것입니다.
- 품목 메시지의 `%path` 구성 요소 이름(`loan`)은 루트 별칭입니다. 별칭을 바꿨다면 같이 바꾸세요.

</details>

#### 8단계. 액션·결정·검증·내부 액션: 보조 클래스로 짧게 쓰기

요구사항

1. 모든 핸들러는 데이터를 **보조 클래스**(`read_loans`, `read_loans_all`, `read_items`)로 읽고, 메시지는 `new_message`로 만듭니다. 행동 풀 안에서 `READ ENTITIES`를 직접 쓰지 마세요(변경은 행동 풀에서 `MODIFY ENTITIES ... IN LOCAL MODE`).
2. `approveLoan`: 상태가 N이 아니면 `failed`(`unspecific`) + 메시지 016(현재 상태). 맞으면 상태 A, `ApprovedBy` = 현재 사용자, 성공 메시지 008. 결과 `$self`는 전체 필드.
3. `lendOut`: 상태가 A가 아니면 016. 맞으면 상태 L, 성공 메시지 009. **재고 출고는 여기서 하지 않습니다**(9단계 세이버에서 레거시 API 호출).
4. `sendReminder`: `ReminderCount` + 1, 성공 메시지 010(빌리는 사람, 새 횟수).
5. `forceReturn`(internal): 상태 R, 성공 메시지 017.
6. `setInitialStatus`: 상태가 비어 있는 새 인스턴스만 N으로.
7. `validateBorrower`: state area `VALIDATE_BORROWER`를 먼저 비우고, 비었으면 012, `/DMO/CUSTOMER`에 없으면 013(`%element-BorrowerID`). 고객 확인은 SELECT 한 번(FOR ALL ENTRIES).
8. `lhc_item->validateEquipment`: state area `VALIDATE_EQUIPMENT`, 자산이 없으면 014(`%element-EquipmentID`), 품목 수량이 재고보다 많으면 015(`%element-Quantity`, 재고 수 표시). 자식 메시지에는 `%path`. 차단(`IsBlocked`)은 **여기서 검사하지 않습니다**(레거시 내부 규칙이라 RAP가 알 수 없다고 가정).

**확인** 행동 풀이 활성화됩니다. 12단계 전이라도, 6단계의 짧은 EML 코드에서 `UPDATE` 대신 `EXECUTE approveLoan FROM VALUE #( ( LoanUUID = l1 ) )` 후 `COMMIT ENTITIES`를 실행하면 `ZRAP_LOAN_###` Data Preview에서 L1의 상태가 A, `approved_by`가 내 사용자로 바뀝니다. 다시 실행하면 016 메시지로 실패합니다.

<details><summary>정답·해설</summary>

`lhc_loan`의 나머지 메서드:

```abap
  METHOD approveLoan.

    DATA(loans)   = zcl_rap_loan_aux_###=>read_loans( CORRESPONDING #( keys ) ).
    DATA(me_user) = zcl_rap_loan_aux_###=>current_user( ).
    DATA updates TYPE TABLE FOR UPDATE zrap_r_loan_###\\loan.

    LOOP AT loans INTO DATA(loan).
      IF loan-Status <> zcl_rap_loan_aux_###=>status-new.
        APPEND VALUE #( %tky        = loan-%tky
                        %fail-cause = if_abap_behv=>cause-unspecific ) TO failed-loan.
        APPEND VALUE #( %tky = loan-%tky
                        %msg = zcl_rap_loan_aux_###=>new_message( textid = zcm_rap_loan_###=>wrong_status
                                                                  status = loan-Status ) ) TO reported-loan.
        CONTINUE.
      ENDIF.

      APPEND VALUE #( %tky       = loan-%tky
                      Status     = zcl_rap_loan_aux_###=>status-approved
                      ApprovedBy = me_user ) TO updates.
      APPEND VALUE #( %tky = loan-%tky
                      %msg = zcl_rap_loan_aux_###=>new_message( textid   = zcm_rap_loan_###=>loan_approved
                                                                severity = if_abap_behv_message=>severity-success
                                                                borrower = loan-BorrowerID ) ) TO reported-loan.
    ENDLOOP.

    MODIFY ENTITIES OF zrap_r_loan_### IN LOCAL MODE
      ENTITY Loan
        UPDATE FIELDS ( Status ApprovedBy )
        WITH updates.

    "result $self: only the successfully processed instances, all fields
    result = VALUE #( FOR updated IN zcl_rap_loan_aux_###=>read_loans_all( CORRESPONDING #( updates ) )
                      ( %tky = updated-%tky %param = updated ) ).

  ENDMETHOD.

  METHOD lendOut.

    DATA(loans) = zcl_rap_loan_aux_###=>read_loans( CORRESPONDING #( keys ) ).
    DATA updates TYPE TABLE FOR UPDATE zrap_r_loan_###\\loan.

    LOOP AT loans INTO DATA(loan).
      IF loan-Status <> zcl_rap_loan_aux_###=>status-approved.
        APPEND VALUE #( %tky        = loan-%tky
                        %fail-cause = if_abap_behv=>cause-unspecific ) TO failed-loan.
        APPEND VALUE #( %tky = loan-%tky
                        %msg = zcl_rap_loan_aux_###=>new_message( textid = zcm_rap_loan_###=>wrong_status
                                                                  status = loan-Status ) ) TO reported-loan.
        CONTINUE.
      ENDIF.

      "only the status changes now - the goods issue is posted in the save sequence (step 9)
      APPEND VALUE #( %tky   = loan-%tky
                      Status = zcl_rap_loan_aux_###=>status-lent ) TO updates.
      APPEND VALUE #( %tky = loan-%tky
                      %msg = zcl_rap_loan_aux_###=>new_message( textid   = zcm_rap_loan_###=>loan_lent
                                                                severity = if_abap_behv_message=>severity-success
                                                                borrower = loan-BorrowerID ) ) TO reported-loan.
    ENDLOOP.

    MODIFY ENTITIES OF zrap_r_loan_### IN LOCAL MODE
      ENTITY Loan
        UPDATE FIELDS ( Status )
        WITH updates.

    result = VALUE #( FOR updated IN zcl_rap_loan_aux_###=>read_loans_all( CORRESPONDING #( updates ) )
                      ( %tky = updated-%tky %param = updated ) ).

  ENDMETHOD.

  METHOD sendReminder.

    DATA(loans) = zcl_rap_loan_aux_###=>read_loans( CORRESPONDING #( keys ) ).

    MODIFY ENTITIES OF zrap_r_loan_### IN LOCAL MODE
      ENTITY Loan
        UPDATE FIELDS ( ReminderCount )
        WITH VALUE #( FOR loan IN loans ( %tky          = loan-%tky
                                          ReminderCount = loan-ReminderCount + 1 ) ).

    reported-loan = VALUE #( BASE reported-loan
                             FOR loan IN loans
                             ( %tky = loan-%tky
                               %msg = zcl_rap_loan_aux_###=>new_message(
                                        textid   = zcm_rap_loan_###=>reminder_sent
                                        severity = if_abap_behv_message=>severity-success
                                        borrower = loan-BorrowerID
                                        count    = loan-ReminderCount + 1 ) ) ).

    result = VALUE #( FOR updated IN zcl_rap_loan_aux_###=>read_loans_all( CORRESPONDING #( keys ) )
                      ( %tky = updated-%tky %param = updated ) ).

  ENDMETHOD.

  METHOD forceReturn.

    "internal action: no authorization check, no feature control - callable only
    "from this behavior pool, the auxiliary class and BDEF friends (step 11)
    DATA(loans) = zcl_rap_loan_aux_###=>read_loans( CORRESPONDING #( keys ) ).

    MODIFY ENTITIES OF zrap_r_loan_### IN LOCAL MODE
      ENTITY Loan
        UPDATE FIELDS ( Status )
        WITH VALUE #( FOR loan IN loans ( %tky   = loan-%tky
                                          Status = zcl_rap_loan_aux_###=>status-returned ) ).

    reported-loan = VALUE #( BASE reported-loan
                             FOR loan IN loans
                             ( %tky = loan-%tky
                               %msg = zcl_rap_loan_aux_###=>new_message(
                                        textid   = zcm_rap_loan_###=>loan_returned
                                        severity = if_abap_behv_message=>severity-success
                                        borrower = loan-BorrowerID ) ) ).

  ENDMETHOD.

  METHOD setInitialStatus.

    DATA(loans) = zcl_rap_loan_aux_###=>read_loans( CORRESPONDING #( keys ) ).
    DELETE loans WHERE Status IS NOT INITIAL.
    IF loans IS INITIAL.
      RETURN.
    ENDIF.

    MODIFY ENTITIES OF zrap_r_loan_### IN LOCAL MODE
      ENTITY Loan
        UPDATE FIELDS ( Status )
        WITH VALUE #( FOR loan IN loans ( %tky   = loan-%tky
                                          Status = zcl_rap_loan_aux_###=>status-new ) ).

  ENDMETHOD.

  METHOD validateBorrower.

    DATA(loans) = zcl_rap_loan_aux_###=>read_loans( CORRESPONDING #( keys ) ).

    "existing customers - one SELECT for all instances
    DATA customers TYPE SORTED TABLE OF /dmo/customer_id WITH UNIQUE KEY table_line.
    IF loans IS NOT INITIAL.
      SELECT FROM /dmo/customer
        FIELDS customer_id
        FOR ALL ENTRIES IN @loans
        WHERE customer_id = @loans-BorrowerID
        INTO TABLE @customers.
    ENDIF.

    LOOP AT loans INTO DATA(loan).

      "clear old state messages of this validation first
      APPEND VALUE #( %tky        = loan-%tky
                      %state_area = 'VALIDATE_BORROWER' ) TO reported-loan.

      IF loan-BorrowerID IS INITIAL.
        APPEND VALUE #( %tky = loan-%tky ) TO failed-loan.
        APPEND VALUE #( %tky                = loan-%tky
                        %state_area         = 'VALIDATE_BORROWER'
                        %element-BorrowerID = if_abap_behv=>mk-on
                        %msg                = zcl_rap_loan_aux_###=>new_message(
                                                textid = zcm_rap_loan_###=>enter_borrower ) ) TO reported-loan.
      ELSEIF NOT line_exists( customers[ table_line = loan-BorrowerID ] ).
        APPEND VALUE #( %tky = loan-%tky ) TO failed-loan.
        APPEND VALUE #( %tky                = loan-%tky
                        %state_area         = 'VALIDATE_BORROWER'
                        %element-BorrowerID = if_abap_behv=>mk-on
                        %msg                = zcl_rap_loan_aux_###=>new_message(
                                                textid   = zcm_rap_loan_###=>borrower_unknown
                                                borrower = loan-BorrowerID ) ) TO reported-loan.
      ENDIF.

    ENDLOOP.

  ENDMETHOD.
```

`lhc_item`의 검증(자식 메시지 줄은 `STRUCTURE FOR REPORTED EARLY` 타입 변수 하나로 만들어 재사용):

```abap
  METHOD validateEquipment.

    DATA(items) = zcl_rap_loan_aux_###=>read_items( CORRESPONDING #( keys ) ).

    IF items IS NOT INITIAL.
      SELECT FROM zrap_asset_###
        FIELDS EquipmentID, Stock
        FOR ALL ENTRIES IN @items
        WHERE EquipmentID = @items-EquipmentID
        INTO TABLE @DATA(assets).
    ENDIF.

    DATA message_line TYPE STRUCTURE FOR REPORTED EARLY zrap_r_loan_###\\item.

    LOOP AT items INTO DATA(item).

      "%path tells Fiori under which parent the item message belongs
      message_line = VALUE #( %tky        = item-%tky
                              %state_area = 'VALIDATE_EQUIPMENT'
                              %path       = VALUE #( loan-%is_draft = item-%is_draft
                                                     loan-LoanUUID  = item-LoanUUID ) ).
      APPEND message_line TO reported-item.            "clear old state messages

      READ TABLE assets INTO DATA(asset) WITH KEY EquipmentID = item-EquipmentID.
      IF sy-subrc <> 0.
        APPEND VALUE #( %tky = item-%tky ) TO failed-item.
        message_line-%element-EquipmentID = if_abap_behv=>mk-on.
        message_line-%msg = zcl_rap_loan_aux_###=>new_message( textid    = zcm_rap_loan_###=>equipment_unknown
                                                               equipment = item-EquipmentID ).
        APPEND message_line TO reported-item.
      ELSEIF asset-Stock < item-Quantity.
        APPEND VALUE #( %tky = item-%tky ) TO failed-item.
        message_line-%element-Quantity = if_abap_behv=>mk-on.
        message_line-%msg = zcl_rap_loan_aux_###=>new_message( textid    = zcm_rap_loan_###=>stock_too_low
                                                               equipment = item-EquipmentID
                                                               count     = asset-Stock ).
        APPEND message_line TO reported-item.
      ENDIF.

    ENDLOOP.

  ENDMETHOD.
```

클래스 구조 해설

- `FOR ACTION Loan~approveLoan RESULT result`: `action ... approveLoan result [1] $self` 줄에서 생깁니다. `keys`는 `TABLE FOR ACTION IMPORT`, `result`는 `TABLE FOR ACTION RESULT`(`%tky` + `%param` = 엔터티 전체 구조)입니다.
- `forceReturn`은 `internal action`이라 결과가 없고, 외부 소비자(Fiori, 일반 EML)는 부를 수 없습니다. 이 행동 풀 안(`IN LOCAL MODE`), 보조 클래스, 11단계의 BDEF friend만 부를 수 있습니다.
- `FOR DETERMINE ON MODIFY`(결정)와 `FOR VALIDATE ON SAVE`(검증)는 `failed`/`reported`가 암묵 파라미터입니다. 검증은 draft의 `Prepare`(Fiori 저장 직전)와 활성 저장(`COMMIT ENTITIES`)의 early save에서 불립니다.
- 프레임워크 호출 순서(액션 하나): 권한(전역/인스턴스, 액션별 규칙에 따라) → `lock` → 액션 메서드. `IN LOCAL MODE`로 보조 클래스가 다시 읽을 때는 권한·잠금이 다시 불리지 않습니다.

왜 이렇게 쓰나

- **보조 클래스로 얻은 것**: 다섯 핸들러가 같은 `read_loans`를 쓰므로 "어떤 필드를 읽나"가 한곳에 모였고, 메시지 생성도 `new_message` 한 줄이 되었습니다. 반대로 핸들러 메서드 자체를 보조 클래스로 통째로 옮기면 파생 타입 파라미터를 또 선언해야 해서 오히려 복잡해진다고 키워드 문서가 경고합니다. 도우미만 옮기세요.
- `lendOut`에서 재고를 바로 줄이지 않는 이유: 상호작용 단계(interaction phase)에서는 DB를 바꾸면 안 됩니다(사용자가 나중에 취소할 수도 있음). DB 변경은 late save의 `save_modified`에서만 합니다. 그래서 "실패도 거기서 늦게" 날 수 있고, 9단계가 그 처리입니다.
- 재고 검사는 품목 하나 기준이라 같은 기자재를 여러 줄에 나눠 넣으면 통과할 수 있습니다. 그 경우는 레거시 API가 합산해 다시 막습니다(늦은 실패의 또 다른 예).
- 상태 확인을 동적 기능 제어(`features : instance`)로 하면 버튼이 회색이 되어 더 친절합니다. 이 문제는 권한과 저장에 집중하려고 액션 안에서만 검사했습니다(기능 제어는 R-03 참고).

자주 나는 오류와 해결

- `TABLE FOR UPDATE zrap_r_loan_###\\loan`에서 오류가 나면 별칭을 대문자로 썼는지보다 BDEF 이름 철자를 확인하세요(ABAP은 대소문자 무관).
- `count = loan-ReminderCount + 1`에서 타입 오류가 나면 `CONV i( loan-ReminderCount + 1 )`처럼 바꾸세요.

</details>

#### 9단계. late save 실패 처리: `CL_ABAP_BEHAVIOR_SAVER_FAILED`

요구사항

1. 세이버 클래스의 상위 클래스를 `CL_ABAP_BEHAVIOR_SAVER_FAILED`로 바꾸세요.
2. `save_modified`:
   - `update-loan`에서 이번 저장에 **상태가 L로 바뀐**(`%control-Status` 켜짐) 대여의 키를 모읍니다. 없으면 바로 끝.
   - 그 대여들의 품목(`EquipmentID`, `Quantity`)을 `READ ENTITIES ... IN LOCAL MODE ... BY \_Item`으로 한 번에 읽습니다.
   - 레거시 API `post_issue`를 **한 번** 호출합니다.
   - 오류가 있으면 그 대여들을 모두 `failed-loan`(`%fail-cause = unspecific`)에 넣고, 오류마다 `reported-loan`에 메시지 011(기자재, 오류 텍스트)을 넣습니다.
3. 이 방식이 "언제 허용되는지"를 주석으로 적으세요.

**확인** 행동 풀이 활성화됩니다. `save_modified`의 파라미터에 F2를 누르면 `CL_ABAP_BEHAVIOR_SAVER`일 때 없던 `failed`, `reported`가 보입니다. 동작 확인은 12단계(차단된 기자재로 lendOut → `COMMIT ENTITIES` 후 `sy-subrc = 8`)에서 합니다.

<details><summary>정답·해설</summary>

세이버 클래스 정의와 구현(6단계 코드를 교체):

```abap
"CL_ABAP_BEHAVIOR_SAVER_FAILED instead of CL_ABAP_BEHAVIOR_SAVER:
"the late saver methods (adjust_numbers, save, save_modified) get the response
"parameters FAILED and REPORTED. Use only in exceptional cases.
CLASS lsc_zrap_r_loan_### DEFINITION INHERITING FROM cl_abap_behavior_saver_failed.
  PROTECTED SECTION.
    METHODS save_modified REDEFINITION.
    METHODS cleanup_finalize REDEFINITION.
ENDCLASS.

CLASS lsc_zrap_r_loan_### IMPLEMENTATION.

  METHOD save_modified.

    "Why a late failure is acceptable here:
    "- ZCL_RAP_ASSET_API_### checks AND posts in one call, it has no check-only API
    "- its 'blocked' rule is internal to the legacy system, RAP cannot check it early
    "- so the error can only be detected while saving -> report it instead of dumping

    "1) loans whose status was changed to 'lent' in this transaction
    DATA lent_keys TYPE TABLE FOR READ IMPORT zrap_r_loan_###\\loan.
    LOOP AT update-loan INTO DATA(loan)
         WHERE %control-Status = if_abap_behv=>mk-on
           AND Status          = zcl_rap_loan_aux_###=>status-lent.
      APPEND VALUE #( LoanUUID = loan-LoanUUID ) TO lent_keys.
    ENDLOOP.
    IF lent_keys IS INITIAL.
      RETURN.
    ENDIF.

    "2) their items - one read
    READ ENTITIES OF zrap_r_loan_### IN LOCAL MODE
      ENTITY Loan BY \_Item
        FIELDS ( LoanUUID EquipmentID Quantity )
        WITH CORRESPONDING #( lent_keys )
      RESULT DATA(items).

    "3) one call of the legacy API (all or nothing)
    DATA(postings) = VALUE zcl_rap_asset_api_###=>tt_postings(
                       FOR item IN items ( equipment_id = item-EquipmentID
                                           quantity     = item-Quantity ) ).
    DATA(errors) = NEW zcl_rap_asset_api_###( )->post_issue( postings ).
    IF errors IS INITIAL.
      RETURN.
    ENDIF.

    "4) late failure: tell the consumer instead of a runtime error
    LOOP AT lent_keys INTO DATA(lent_key).
      APPEND VALUE #( %key-LoanUUID = lent_key-LoanUUID
                      %fail-cause   = if_abap_behv=>cause-unspecific ) TO failed-loan.
      LOOP AT errors INTO DATA(error).
        CHECK line_exists( items[ LoanUUID = lent_key-LoanUUID EquipmentID = error-equipment_id ] ).
        APPEND VALUE #( %key-LoanUUID = lent_key-LoanUUID
                        %msg          = zcl_rap_loan_aux_###=>new_message(
                                          textid    = zcm_rap_loan_###=>posting_failed
                                          equipment = error-equipment_id
                                          text      = error-text ) ) TO reported-loan.
      ENDLOOP.
    ENDLOOP.

  ENDMETHOD.

  METHOD cleanup_finalize.
    "nothing buffered in this saver
  ENDMETHOD.

ENDCLASS.
```

클래스 구조 해설

- `save_modified`는 BDEF 머리의 `with additional save` 때문에 있습니다. 파라미터 `create`/`update`/`delete`는 `REQUEST FOR CHANGE`/`REQUEST FOR DELETE` 타입으로, 기본적으로 키와 **바뀐 필드만** 들어 있고 `%control`로 어떤 필드가 바뀌었는지 알 수 있습니다(R-04 참고).
- 상위 클래스를 `CL_ABAP_BEHAVIOR_SAVER_FAILED`로 바꾸면 `adjust_numbers`, `save`, `save_modified`에 **`failed`와 `reported`(late 응답 타입)**가 생깁니다(키워드 문서 `CL_ABAP_BEHAVIOR_SAVER_FAILED`). ADT 퀵픽스는 항상 `CL_ABAP_BEHAVIOR_SAVER`로 만들기 때문에 직접 바꿔야 합니다. 세이버 클래스는 BO당 하나입니다.
- late 응답 타입(`RESPONSE FOR FAILED LATE`)의 키 구성 요소는 early와 다를 수 있습니다. 여기서는 `%key-LoanUUID`를 썼습니다(키워드 문서의 `CL_ABAP_BEHAVIOR_SAVER_FAILED` 예제도 late 응답에서 `%key-...`를 씁니다). F2로 `failed-loan`의 줄 타입을 열어 `%tky`가 있는지, `%key`만 있는지 확인하고 맞추세요(실제 시스템에서 확인 필요).

왜 이렇게 쓰나

- **기본 규칙**: late save(`adjust_numbers`, `save`/`save_modified`)는 실패하면 안 됩니다. 모든 실패는 early save(검증, `finalize`, `check_before_save`)에서 찾아야 합니다. `CL_ABAP_BEHAVIOR_SAVER`를 쓰는 세이버에서 late 단계에 문제가 생기면 돌려줄 통로가 없어 런타임 오류로 끝납니다.
- **예외가 허용되는 경우**: 확인과 저장을 한 번에 하는 기존 API(SAP 문서는 BAPI를 예로 들지만, 이 문제는 BAPI 대신 Z 레거시 API)를 late save에서 부를 수밖에 없고, 그 API의 검사를 early에서 똑같이 재현할 수 없을 때입니다. 그래도 **할 수 있는 검사는 early에 둡니다**(8단계의 재고 검사). 여러 BO가 한 트랜잭션에 있을 때 데이터 불일치 위험이 있으므로 "예외적인 경우에만" 쓰라고 문서가 강조합니다.
- **소비자 쪽 결과**(키워드 문서와 cheat sheet 08): late 단계 실패 뒤 `COMMIT ENTITIES`의 `sy-subrc`는 **8**입니다(early 실패는 4). 응답은 `COMMIT ENTITIES RESPONSE OF ... FAILED ... REPORTED ...`(긴 형식)으로 받습니다. 이 트랜잭션은 일관성이 깨진 상태이므로 소비자가 계속 EML을 쓰려면 **반드시 `ROLLBACK ENTITIES`**를 먼저 해야 하고, 그러지 않으면 다음 EML에서 `CX_SADL_DUMP_APPL_MODEL_ERROR` 런타임 오류가 납니다.
- **late numbering과 함께라면**: 최종 키를 `adjust_numbers`에서 돌려줘야 하므로, 키를 만들어 주는 레거시 저장 호출 자체를 `adjust_numbers`로 옮기라고 문서가 안내합니다(이 BO는 UUID라 해당 없음).
- 레거시 API를 한 번만 부르고 "전부 아니면 전무"로 만든 이유: 일부만 출고되고 일부는 실패하면 RAP 쪽 롤백과 레거시 쪽 결과가 어긋납니다. 이 API는 DB 변경만 하고 COMMIT은 하지 않으므로, 소비자의 `ROLLBACK ENTITIES`가 같은 LUW의 변경을 함께 되돌립니다(12단계에서 재고가 그대로인지 확인).
- `READ ENTITIES ... IN LOCAL MODE`를 `save_modified`에서 쓰는 것은 읽기라서 허용됩니다(DB 변경 금지 규칙과 무관). 품목이 같은 트랜잭션에서 새로 생겼어도 버퍼에서 읽힙니다.

자주 나는 오류와 해결

- 상위 클래스만 바꾸고 `failed-loan`을 쓰면 "구성 요소 없음"이 나는 경우: BO가 `with additional save`/`with unmanaged save`가 아니면 `save_modified`가 없습니다. 5단계 머리 줄을 확인하세요.
- `LOOP ... WHERE %control-Status = ...`에서 오류가 나면 `LOOP AT update-loan INTO DATA(loan). IF loan-%control-Status <> if_abap_behv=>mk-on OR loan-Status <> ... CONTINUE. ENDIF.`로 바꾸세요.

</details>

#### 10단계. RAP 변경 문서: `changedocuments master` / `dependent`

요구사항

1. 변경 문서 객체 `ZRAPLOAN###`를 만드세요(ADT: New → Other ABAP Repository Object → "Change Document Object" 검색). 설명 "Loan ### change documents", 테이블 `ZRAP_LOAN_###`, `ZRAP_LOANI_###` 추가, 저장·활성화. (BDEF에서 `changedocuments master ( ZRAPLOAN### )`를 먼저 쓰고 퀵픽스로 만들어도 됩니다.)
2. BDEF를 바꾸세요.
   - 루트: 변경 문서 **마스터**(객체 `ZRAPLOAN###`), 본문에 기록 옵션 — 생성은 키만, 변경은 값(이전/이후), 삭제는 키만.
   - 품목: 변경 문서 **dependent**(`_Loan` 경유), 본문에 옵션 — 생성·변경·삭제 모두 값.
3. 콘솔 클래스 `ZCL_RAP_LOAN_CHDOC_###`:
   - 공개 정적 메서드 `print_change_documents( out )`: `CL_CHDO_READ_TOOLS=>CHANGEDOCUMENT_READ`로 객체 `ZRAPLOAN###`의 변경 문서를 읽어 건수와 내용을 출력(`CX_CHDO_READ_ERROR` 처리).
   - `main`: L1 품목 수량을 1 → 2로 바꾸고 L1을 승인(`approveLoan`)한 뒤 `COMMIT ENTITIES`, 그다음 `print_change_documents`.

**확인** 생성 클래스로 데이터를 초기화한 뒤 `ZCL_RAP_LOAN_CHDOC_###`를 실행하면, 변경 문서에 `ZRAP_LOANI_###`의 `QUANTITY`(1 → 2)와 `ZRAP_LOAN_###`의 `STATUS`(N → A) 줄이 보입니다. `DESCRIPTION`처럼 표시 없는 필드는 바꿔도 나오지 않습니다.

<details><summary>정답·해설</summary>

BDEF 전체(10단계 시점):

```bdef
managed with additional save implementation in class zbp_rap_r_loan_### unique;
strict ( 2 );                                             // 변경 문서의 전제: strict 모드
with draft;
auxiliary class zcl_rap_loan_aux_###;

define behavior for ZRAP_R_LOAN_### alias Loan
persistent table zrap_loan_###                            // 변경 문서의 전제: persistent table
draft table zrap_loan_d_###
lock master unmanaged total etag LastChangedAt
etag master LocalLastChangedAt
authorization master ( global, instance )
changedocuments master ( ZRAPLOAN### )                   // 이 엔터티가 변경 문서 마스터, 저장할 객체
{
  changedocuments ( create : key, update : data, delete : key );   // 연산별 기록 수준

  create;
  update;
  delete;

  field ( numbering : managed, readonly ) LoanUUID;
  field ( readonly ) Status, ApprovedBy, ReminderCount,
                     CreatedBy, CreatedAt, LocalLastChangedBy, LocalLastChangedAt, LastChangedAt;
  field ( mandatory ) BorrowerID;

  association _Item { create ( authorization : global, authorization : instance ); with draft; }

  action ( authorization : global ) approveLoan result [1] $self;
  action ( authorization : instance ) lendOut result [1] $self;
  action ( authorization : none ) sendReminder result [1] $self;
  internal action forceReturn;

  determination setInitialStatus on modify { create; }
  validation validateBorrower on save { create; field BorrowerID; }

  draft action Edit;
  draft action Activate optimized;
  draft action Discard;
  draft action Resume;
  draft determine action Prepare
  {
    validation validateBorrower;
    validation Item~validateEquipment;
  }

  mapping for zrap_loan_### corresponding
  {
    LoanUUID           = loan_uuid;
    BorrowerID         = borrower_id;
    BeginDate          = begin_date;
    EndDate            = end_date;
    Status             = status;
    Description        = description;
    ApprovedBy         = approved_by;
    ReminderCount      = reminder_count;
    CreatedBy          = created_by;
    CreatedAt          = created_at;
    LocalLastChangedBy = local_last_changed_by;
    LocalLastChangedAt = local_last_changed_at;
    LastChangedAt      = last_changed_at;
  }
}

define behavior for ZRAP_R_LOANITEM_### alias Item
persistent table zrap_loani_###
draft table zrap_loani_d_###
lock dependent by _Loan
authorization master ( instance )
etag master LocalLastChangedAt
changedocuments dependent by _Loan                       // 마스터(Loan)의 변경 문서 객체에 함께 기록
{
  changedocuments ( create : data, update : data, delete : data );

  update;
  delete;

  field ( numbering : managed, readonly ) ItemUUID;
  field ( readonly ) LoanUUID, LocalLastChangedAt;
  field ( mandatory ) EquipmentID, Quantity;

  validation validateEquipment on save { create; field EquipmentID, Quantity; }

  association _Loan { with draft; }

  mapping for zrap_loani_### corresponding
  {
    ItemUUID           = item_uuid;
    LoanUUID           = loan_uuid;
    EquipmentID        = equipment_id;
    Quantity           = quantity;
    ItemNote           = item_note;
    LocalLastChangedAt = local_last_changed_at;
  }
}
```

읽기 콘솔 클래스:

```abap
CLASS zcl_rap_loan_chdoc_### DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_oo_adt_classrun.

    CLASS-METHODS print_change_documents
      IMPORTING out TYPE REF TO if_oo_adt_classrun_out.

  PROTECTED SECTION.
  PRIVATE SECTION.
ENDCLASS.

CLASS zcl_rap_loan_chdoc_### IMPLEMENTATION.

  METHOD if_oo_adt_classrun~main.

    SELECT SINGLE loan_uuid FROM zrap_loan_### WHERE borrower_id = '000001' INTO @DATA(l1).
    SELECT SINGLE item_uuid FROM zrap_loani_### WHERE loan_uuid = @l1 INTO @DATA(i1).

    "two changes on active instances: item quantity and loan status
    MODIFY ENTITIES OF zrap_r_loan_###
      ENTITY Item
        UPDATE FIELDS ( Quantity )
        WITH VALUE #( ( ItemUUID = i1 Quantity = 2 ) )
      ENTITY Loan
        EXECUTE approveLoan
        FROM VALUE #( ( LoanUUID = l1 ) )
      FAILED DATA(failed)
      REPORTED DATA(reported).

    IF failed IS NOT INITIAL.
      out->write( `Modify failed - run ZCL_RAP_LOAN_GEN_### first (L1 must be in status N).` ).
      ROLLBACK ENTITIES.
      RETURN.
    ENDIF.

    COMMIT ENTITIES.
    out->write( |COMMIT ENTITIES sy-subrc: { sy-subrc }| ).

    print_change_documents( out ).

  ENDMETHOD.

  METHOD print_change_documents.

    DATA change_documents TYPE cl_chdo_read_tools=>tt_cdredadd_tab.

    TRY.
        cl_chdo_read_tools=>changedocument_read(
          EXPORTING
            i_objectclass   = 'ZRAPLOAN###'          " change document object
          IMPORTING
            et_cdredadd_tab = change_documents ).
      CATCH cx_chdo_read_error INTO DATA(read_error).
        out->write( |Change document read error: { read_error->get_text( ) }| ).
        RETURN.
    ENDTRY.

    out->write( |Change document lines: { lines( change_documents ) }| ).
    out->write( change_documents ).

  ENDMETHOD.

ENDCLASS.
```

왜 이렇게 쓰나

- **RAP 변경 문서**(릴리스 뉴스: 7.58 / 클라우드 2508, 9.16)는 BDEF 선언만으로 동작하고 **행동 풀 구현이 필요 없습니다**(키워드 문서 `changedocuments`). 규칙:
  - `changedocuments master ( 객체 )`는 BO당 **하나**뿐이고, 보통 루트입니다. 그 아래 composition 트리의 엔터티는 `changedocuments dependent [by _Assoc]`로 같은 객체에 기록합니다(`by`를 빼면 조상 연관을 자동으로 씀). 변경 문서 대상 엔터티들은 트리를 이루어야 합니다.
  - 전제: strict 모드, `persistent table`. managed BO에서만(온프레미스에서는 Standard ABAP 언어 버전에서만) 됩니다. BDEF 확장에서는 마스터를 정의할 수 없습니다.
  - 추가 옵션: `changedocuments master asynchronous ( ... )`(변경 문서 쓰기를 bgPF로 비동기), `utc`(시각을 UTC로). 문법 순서는 `changedocuments master [asynchronous] [utc] ( 객체 )`입니다.
- **본문 옵션** `changedocuments ( create : ..., update : ..., delete : ... )`: `none`(기록 안 함), `key`(키만), `data`(변경 문서 대상 필드의 값). `update`에는 `none`/`data`만 됩니다. 아무것도 안 적으면 `create : key, update : data, delete : key`가 기본입니다. 액션처럼 표준이 아닌 연산의 변경도 결국 표준 연산 조합이므로 같은 옵션으로 기록됩니다(그래서 `approveLoan`의 상태 변경이 기록됨).
- **변경 문서 객체의 자체 옵션은 무시됩니다.** RAP에서는 객체 이름(결과의 키 역할)만 의미가 있고 기록 방식은 BDEF가 정합니다.
- 기록은 CDS 엔터티 수준에서 필드 메타데이터를 보고 하므로, 1단계에서 데이터 엘리먼트에 변경 문서 표시를 한 필드만 값이 남습니다.
- draft는 기록되지 않고 활성 저장(persistent table 변경)만 기록됩니다. 프로젝션 BDEF나 인터페이스 BDEF로 바꾼 것도 기반 BO의 변경 문서로 자동 기록됩니다.
- 읽기: `CL_CHDO_READ_TOOLS=>CHANGEDOCUMENT_READ`는 SAP 공식 샘플(abap-platform-reuse-services의 `ZREUSECL_GET_CHANGE_DOCS_002`)에서 확인한 사용법입니다. `it_objectid`(객체 ID 범위), 날짜·사용자 조건도 줄 수 있습니다. RAP 변경 문서의 객체 ID가 키로 어떻게 만들어지는지는 문서에서 확인하지 못해 객체 클래스 전체를 읽었습니다(실제 시스템에서 확인 필요). 출력된 `OBJECTID` 열을 보고 필터 값을 정해 보세요.
- **2508 이전 시스템이거나 BDEF 문법이 안 될 때의 대안**: 변경 문서 객체를 만들면 ADT가 `ZCL_<객체>_CHDO` 클래스를 생성합니다. SAP 샘플(reuse services)은 `with additional save`의 `save_modified`에서 DB의 이전 값을 읽고 `zcl_zreuse_so_002_chdo=>write( objectid = ... o_<테이블> = 이전 n_<테이블> = 이후 upd_<테이블> = 'U' ... IMPORTING changenumber = ... )`를 부르고 `cx_chdo_write_error`를 잡습니다. 이 방식은 직접 구현이 필요하고, DB에 쓰기 **전에** 호출해야 차이를 계산한다는 점(샘플 주석 "Data must NOT be saved before change doc API is called")에 주의하세요. 이 BO에 적용하는 코드는 생성되는 클래스의 파라미터 이름에 달려 있으므로 실제 시스템에서 확인 필요입니다.

자주 나는 오류와 해결

- "change document object does not exist": 1번 단계를 건너뛰었거나 이름이 다릅니다. BDEF 줄에서 Ctrl+1 퀵픽스로 만들 수 있습니다.
- 변경 문서에 상태 줄이 없고 키 줄만 있으면: 데이터 엘리먼트의 Change Document Logging 표시를 확인하세요(1단계).
- 변경 문서 객체 가져오기(abapGit)에 실패한다는 알려진 문제가 SAP 샘플 README에 있습니다. 그 경우에도 이 문제처럼 직접 만들면 됩니다.

</details>

#### 11단계. BDEF friends: 확장에서 internal action 부르기

요구사항

1. 기반 BDEF `ZRAP_R_LOAN_###`를 확장 가능하게 바꾸세요.
   - 머리: `with draft;` 다음 줄에 확장 허용 키워드를 넣습니다(friends는 4번에서 추가).
   - `Loan` 엔터티 특성: `changedocuments master ( ... )` 다음 줄에 같은 키워드를 넣습니다. `Item`은 확장하지 않습니다.
2. BDEF 확장 `ZRAP_X_LOAN_###`를 만드세요(프로젝트 탐색기에서 `ZRAP_R_LOAN_###` 우클릭 → New Behavior Extension).
   - 머리: 확장 구현 클래스 `ZBP_RAP_X_LOAN_###`(unique).
   - `Loan`을 확장해 인스턴스 액션 `zzForceReturn`을 추가합니다. 결과는 없고, **권한 검사는 하지 않는다**고 명시하세요(관리자용 데모 액션).
3. 확장 행동 풀 `ZBP_RAP_X_LOAN_###`(퀵픽스로 생성)의 로컬 핸들러 `lhc_loan`에서 `zzForceReturn`을 구현하세요. 기반 BO의 internal action `forceReturn`을 `IN LOCAL MODE`로 실행하고, `failed`/`reported`를 그대로 돌려줍니다.
4. 기반 BDEF 머리의 확장 키워드 뒤에 `ZRAP_X_LOAN_###`를 **friend**로 선언하고 다시 활성화하세요.

**확인** 네 객체(기반 BDEF, 확장 BDEF, 확장 행동 풀, 기반 행동 풀)가 모두 활성화됩니다. 동작은 12단계 테스트 클래스(`zzForceReturn` 후 L2 상태가 R)에서 봅니다. 4번을 하기 전에 같은 EML을 실행하면 런타임 오류가 나는 것도 확인해 보세요(선택).

<details><summary>정답·해설</summary>

활성화 순서: ① 기반 BDEF에 `extensible`만 넣어 활성화 → ② 확장 BDEF 생성·활성화 → ③ 확장 행동 풀 구현·활성화 → ④ 기반 BDEF에 `with friends` 추가·활성화. `with friends` 뒤의 이름은 **현재 BDEF의 확장**이어야 하므로(키워드 문서 `with friends`) 확장이 먼저 있어야 깔끔합니다.

기반 BDEF 전체(최종):

```bdef
managed with additional save implementation in class zbp_rap_r_loan_### unique;
strict ( 2 );
with draft;
extensible with friends zrap_x_loan_###;                  // 확장 허용 + 이 확장은 friend
auxiliary class zcl_rap_loan_aux_###;

define behavior for ZRAP_R_LOAN_### alias Loan
persistent table zrap_loan_###
draft table zrap_loan_d_###
lock master unmanaged total etag LastChangedAt
etag master LocalLastChangedAt
authorization master ( global, instance )
changedocuments master ( ZRAPLOAN### )
extensible                                                // 이 엔터티는 확장 가능
{
  changedocuments ( create : key, update : data, delete : key );

  create;
  update;
  delete;

  field ( numbering : managed, readonly ) LoanUUID;
  field ( readonly ) Status, ApprovedBy, ReminderCount,
                     CreatedBy, CreatedAt, LocalLastChangedBy, LocalLastChangedAt, LastChangedAt;
  field ( mandatory ) BorrowerID;

  association _Item { create ( authorization : global, authorization : instance ); with draft; }

  action ( authorization : global ) approveLoan result [1] $self;
  action ( authorization : instance ) lendOut result [1] $self;
  action ( authorization : none ) sendReminder result [1] $self;
  internal action forceReturn;

  determination setInitialStatus on modify { create; }
  validation validateBorrower on save { create; field BorrowerID; }

  draft action Edit;
  draft action Activate optimized;
  draft action Discard;
  draft action Resume;
  draft determine action Prepare
  {
    validation validateBorrower;
    validation Item~validateEquipment;
  }

  mapping for zrap_loan_### corresponding
  {
    LoanUUID           = loan_uuid;
    BorrowerID         = borrower_id;
    BeginDate          = begin_date;
    EndDate            = end_date;
    Status             = status;
    Description        = description;
    ApprovedBy         = approved_by;
    ReminderCount      = reminder_count;
    CreatedBy          = created_by;
    CreatedAt          = created_at;
    LocalLastChangedBy = local_last_changed_by;
    LocalLastChangedAt = local_last_changed_at;
    LastChangedAt      = last_changed_at;
  }
}

define behavior for ZRAP_R_LOANITEM_### alias Item
persistent table zrap_loani_###
draft table zrap_loani_d_###
lock dependent by _Loan
authorization master ( instance )
etag master LocalLastChangedAt
changedocuments dependent by _Loan
{
  changedocuments ( create : data, update : data, delete : data );

  update;
  delete;

  field ( numbering : managed, readonly ) ItemUUID;
  field ( readonly ) LoanUUID, LocalLastChangedAt;
  field ( mandatory ) EquipmentID, Quantity;

  validation validateEquipment on save { create; field EquipmentID, Quantity; }

  association _Loan { with draft; }

  mapping for zrap_loani_### corresponding
  {
    ItemUUID           = item_uuid;
    LoanUUID           = loan_uuid;
    EquipmentID        = equipment_id;
    Quantity           = quantity;
    ItemNote           = item_note;
    LocalLastChangedAt = local_last_changed_at;
  }
}
```

BDEF 확장 `ZRAP_X_LOAN_###`:

```bdef
extension implementation in class zbp_rap_x_loan_### unique;

extend behavior for Loan
{
  action ( authorization : none ) zzForceReturn;          // 확장 액션: 권한 처리를 반드시 명시
}
```

확장 행동 풀 — 글로벌 클래스(퀵픽스가 만든 그대로):

```abap
CLASS zbp_rap_x_loan_### DEFINITION PUBLIC ABSTRACT FINAL FOR BEHAVIOR OF zrap_r_loan_###.
ENDCLASS.

CLASS zbp_rap_x_loan_### IMPLEMENTATION.
ENDCLASS.
```

Local Types:

```abap
CLASS lhc_loan DEFINITION INHERITING FROM cl_abap_behavior_handler.
  PRIVATE SECTION.
    METHODS zzForceReturn FOR MODIFY
      IMPORTING keys FOR ACTION Loan~zzForceReturn.
ENDCLASS.

CLASS lhc_loan IMPLEMENTATION.

  METHOD zzForceReturn.

    "forceReturn is an INTERNAL action of the base BO.
    "Only the base behavior pool and BDEF friends may execute it (IN LOCAL MODE).
    MODIFY ENTITIES OF zrap_r_loan_### IN LOCAL MODE
      ENTITY Loan
        EXECUTE forceReturn
        FROM CORRESPONDING #( keys )
      FAILED DATA(base_failed)
      REPORTED DATA(base_reported).

    failed   = CORRESPONDING #( DEEP base_failed ).
    reported = CORRESPONDING #( DEEP base_reported ).

  ENDMETHOD.

ENDCLASS.
```

클래스 구조 해설

- 확장 행동 풀은 **확장 BDEF에 적힌 것만** 반영합니다. 그래서 `lhc_loan`에는 `zzForceReturn` 하나만 있고, 기반 행동 풀의 `lhc_loan`과 이름이 같아도 서로 다른 클래스입니다(각 행동 풀의 로컬 클래스).
- 핸들러의 암묵 파라미터 `failed`/`reported`는 확장 쪽 타입이고, `MODIFY ENTITIES`의 응답은 BO 전체 타입이라 `CORRESPONDING #( DEEP ... )`로 옮겼습니다. 키워드 문서의 friends 예제처럼 응답을 받지 않고 `FROM CORRESPONDING #( keys )`만 써도 동작합니다(메시지가 소비자에게 가지 않을 뿐). 두 타입이 같은 구조로 보이면 `failed = base_failed.`로도 됩니다(실제 시스템에서 확인 필요).
- 호출 흐름(키워드 문서의 예): 소비자가 `zzForceReturn` 실행 → 확장의 권한 제어(여기서는 `none`이라 없음) → 기반 BO의 `lock`(액션은 인스턴스를 바꾸므로 6단계 unmanaged lock이 불림) → `zzForceReturn` → `forceReturn`. `forceReturn`에 대해서는 **기반 BO의 권한 제어가 다시 불리지 않습니다**(friend + `IN LOCAL MODE`).

왜 이렇게 쓰나

- **friend가 얻는 권리**(키워드 문서 `with friends`, 릴리스 뉴스: 7.95 / 클라우드 2402): ① internal 연산 접근, ② `IN LOCAL MODE` 사용, ③ 원래 BO 필드 접근. friend가 **아닌** 확장이 같은 코드(`IN LOCAL MODE ... EXECUTE forceReturn`)를 실행하면 런타임 오류가 납니다. friend 관계는 전이되지 않습니다(friend의 friend는 friend 아님).
- **언제 쓰나**: 큰 BO를 여러 개발 객체로 나눠 개발할 때(모듈화)입니다. 원래 BO의 내부 로직은 숨긴 채(internal) "같은 팀의 확장"에게만 열어 줄 수 있습니다. 외부 소비자(Fiori, 다른 팀 EML)는 여전히 `forceReturn`을 부를 수 없습니다.
- **확장 액션의 권한**: 확장의 액션·함수 등은 권한 처리를 명시해야 하며, `authorization : none`도 허용됩니다(키워드 문서의 friends 예제는 `authorization : instance`). 여기서는 데모라 `none`으로 두었지만, 실무에서는 `instance`로 두고 확장 행동 풀에 권한 메서드를 구현하세요. 이 경우 키워드 문서 설명대로 "확장의 권한 제어"가 먼저 불립니다.
- **확장 허용 조건**(키워드 문서 `extensible`, 확장성 활성화): strict 모드 필수, 머리와 엔터티 특성 **두 곳**에 `extensible`. 확장에 검증·결정·추가 저장을 넣으려면 머리에서 `extensible { with validations on save; ... }`로 따로 허용해야 합니다. 이 문제의 확장은 액션만 추가하므로 필요 없습니다. 키워드 문서의 draft 예제(`with draft; extensible { ... }`)처럼 draft BO도 확장할 수 있습니다.
- 같은 소프트웨어 컴포넌트 안의 확장이라 기반 BDEF를 C0로 릴리스할 필요가 없다고 보았습니다. 다른 소프트웨어 컴포넌트에서 확장하려면 C0 릴리스와 확장 포함 규칙(필드 이름 접두어, draft 쿼리 뷰 등)이 추가로 필요합니다(실제 시스템에서 확인 필요).

자주 나는 오류와 해결

- 확장 BDEF 활성화 시 "BDEF ZRAP_R_LOAN_### is not extensible": 머리 또는 `Loan` 엔터티 특성 중 한 곳에 `extensible`이 빠졌습니다.
- 기반 BDEF 활성화 시 `with friends`의 이름이 확장이 아니라는 경고/오류: ②를 먼저 하세요(문서상 확장이 아니면 효과가 없습니다).
- 12단계에서 `zzForceReturn` 실행 시 런타임 오류: `with friends`를 넣은 기반 BDEF를 활성화했는지 확인하세요. friend가 아니면 internal action 접근이 금지됩니다.

</details>

#### 12단계. 프로젝션·서비스와 EML 종합 테스트(잠금 충돌, 권한, preserve_changes, late 실패)

요구사항

1. 프로젝션 뷰 두 개(`provider contract transactional_query`, 메타데이터 확장 허용).
   - `ZRAP_C_LOAN_###`: 루트 뷰의 모든 필드 + `_Item`을 자식 프로젝션으로 리다이렉트.
   - `ZRAP_C_LOANITEM_###`: 품목 뷰의 모든 필드 + `_Loan`을 부모 프로젝션으로 리다이렉트.
2. 메타데이터 확장(최소한).
   - `ZRAP_C_LOAN_###`: 헤더 정보(제목: 빌리는 사람, 설명: 상태), facet 두 개(식별 정보, 품목 테이블), 목록·식별 영역에 필드와 **액션 버튼 3개**(`approveLoan`, `lendOut`, `sendReminder`), UUID는 숨김.
   - `ZRAP_C_LOANITEM_###`: 목록에 기자재·수량·메모, 식별 facet 하나.
   - (→ 어노테이션 탭: `@UI.headerInfo`, `@UI.facet`의 `#IDENTIFICATION_REFERENCE` / `#LINEITEM_REFERENCE` + `targetElement`, `@UI.lineItem`·`@UI.identification`의 `type: #FOR_ACTION` + `dataAction`, `@UI.hidden`)
3. 프로젝션 BDEF `ZRAP_C_LOAN_###`: draft 사용, 표준 연산, 세 액션, draft 액션 다섯 개(`Edit`, `Activate`, `Discard`, `Resume`, `Prepare`), `_Item` 생성(draft 포함), 품목의 수정·삭제와 `_Loan`. `forceReturn`과 `zzForceReturn`은 노출하지 않습니다.
4. 서비스 정의 `ZRAP_UI_LOAN_###`(엔터티 `Loan`, `Item`)와 서비스 바인딩 `ZRAP_UI_LOAN_O4_###`(OData V4 - UI). 게시 후 Preview로 L1~L3이 보이는지 확인.
5. 잠금 붙잡기 클래스 `ZCL_RAP_LOAN_LOCKHOLD_###`: L1을 `SET LOCKS`로 잠그고, 결과를 출력한 다음 줄에서 멈출 수 있게 합니다(중단점 위치를 주석으로).
6. 종합 테스트 클래스 `ZCL_RAP_LOAN_TEST_###`(콘솔). 상수 `c_mode`가 `'ALL'`이면 아래 4~7을, `'LOCK'`이면 잠금 시나리오만 실행합니다. 모든 응답은 공용 출력 메서드(실패 원인 이름 + 메시지 텍스트)로 출력합니다.
   - (ALL-0) `reset_data` 후 `COMMIT WORK`.
   - (ALL-1 권한) 스위치를 켜고 `COMMIT WORK` 후 요청, 확인 뒤 `ROLLBACK ENTITIES`, 스위치 끄기:
     - `DENY_APPROVE` → L1 `approveLoan` 실패(unauthorized).
     - `OWNER_ONLY` → L3 `Description` 변경 실패(unauthorized), 그러나 L3 `sendReminder`는 성공.
     - `DENY_ITEM_EQUIP` = `EQ-TRIPOD` → L3 품목 수량 변경 실패(unauthorized).
     - `DENY_ADD_ITEM` → L1에 `CREATE BY \_Item` 실패(unauthorized).
   - (ALL-2 preserve_changes) L1 `Edit`(preserve_changes = false) + draft의 `Description` 변경 → `COMMIT ENTITIES`. 다시 `Edit`(true) → 실패. `Edit`(false) → 성공, draft를 다시 읽어 설명이 활성 값으로 돌아왔는지 출력 → `COMMIT ENTITIES`. 마지막에 `Discard` → `COMMIT ENTITIES`.
   - (ALL-3 late 실패) `EQ-CAMERA`를 차단(`IsBlocked`)하고 `COMMIT WORK`. L2 `lendOut` → `COMMIT ENTITIES RESPONSE OF ...`(late 응답 타입 변수) → `sy-subrc`가 8인지, late failed/reported 출력, `ROLLBACK ENTITIES`. DB에서 L2 상태(A 그대로)와 재고(그대로) 확인. 차단 해제 후 다시 `lendOut` → `sy-subrc` 0, 상태 L, 재고 감소 확인.
   - (ALL-4 friend + 변경 문서) L2에 `zzForceReturn` → `COMMIT ENTITIES` → 상태 R 확인 → `zcl_rap_loan_chdoc_###=>print_change_documents( out )`.
   - (LOCK) L1 `Description` 변경 → 실패 원인 `locked`와 메시지 001 확인 → `ROLLBACK ENTITIES`.

**확인**
- Fiori 미리보기: 목록에 버튼 3개가 보입니다. 다른 사람이 만든 L3을 열어 `Edit`을 누르면 `OWNER_ONLY`가 꺼져 있을 때는 되고, 켜면(생성 클래스로 `set_switch`) 메시지 005와 함께 거부됩니다. `sendReminder`는 언제나 됩니다.
- 테스트 클래스 `'ALL'` 출력 예(요지):

| 시나리오 | 기대 결과 |
|---|---|
| DENY_APPROVE / approveLoan L1 | failed Loan: unauthorized, 메시지 003 |
| OWNER_ONLY / update L3 | failed Loan: unauthorized, 메시지 005 |
| OWNER_ONLY / sendReminder L3 | 실패 없음, 성공 메시지 010 |
| DENY_ITEM_EQUIP / update L3 item | failed Item: unauthorized, 메시지 006 |
| DENY_ADD_ITEM / create by \_Item L1 | failed: unauthorized, 메시지 007 |
| Edit preserve_changes = true | failed Loan(원인은 시스템이 정함), draft가 이미 있다는 메시지 |
| Edit preserve_changes = false | 성공, draft 설명이 `Beamer for workshop`로 복귀 |
| lendOut L2, EQ-CAMERA 차단 | `COMMIT ENTITIES sy-subrc: 8`, late failed Loan: unspecific, 메시지 011 |
| 롤백 후 DB | L2 상태 A, LAPTOP 재고 5, CAMERA 재고 1 |
| 차단 해제 후 lendOut L2 | `sy-subrc: 0`, 상태 L, LAPTOP 3, CAMERA 0 |
| zzForceReturn L2 | 상태 R, 메시지 017 |
| 변경 문서 | L2 `STATUS` A→L, L→R 줄(이전 실행분 포함) |

- 잠금 시나리오: 아래 "잠금 충돌 재현 방법"대로 하면 `failed Loan: locked`, 메시지 001(잠근 사용자 = 내 사용자 이름)이 나옵니다.

<details><summary>정답·해설</summary>

프로젝션 뷰:

```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Equipment loan ### - projection'
@Metadata.allowExtensions: true
define root view entity ZRAP_C_LOAN_###
  provider contract transactional_query
  as projection on ZRAP_R_LOAN_###
{
  key LoanUUID,
      BorrowerID,
      BeginDate,
      EndDate,
      Status,
      Description,
      ApprovedBy,
      ReminderCount,
      CreatedBy,
      CreatedAt,
      LocalLastChangedBy,
      LocalLastChangedAt,
      LastChangedAt,

      _Item : redirected to composition child ZRAP_C_LOANITEM_###
}
```

```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Equipment loan item ### - projection'
@Metadata.allowExtensions: true
define view entity ZRAP_C_LOANITEM_###
  as projection on ZRAP_R_LOANITEM_###
{
  key ItemUUID,
      LoanUUID,
      EquipmentID,
      Quantity,
      ItemNote,
      LocalLastChangedAt,

      _Loan : redirected to parent ZRAP_C_LOAN_###
}
```

메타데이터 확장:

```cds
@Metadata.layer: #CORE
@UI.headerInfo: { typeName: 'Loan', typeNamePlural: 'Loans',
                  title: { value: 'BorrowerID' }, description: { value: 'Status' } }
annotate entity ZRAP_C_LOAN_### with
{
  @UI.facet: [ { id: 'Loan',  purpose: #STANDARD, type: #IDENTIFICATION_REFERENCE, label: 'Loan',  position: 10 },
               { id: 'Items', purpose: #STANDARD, type: #LINEITEM_REFERENCE,       label: 'Items', position: 20,
                 targetElement: '_Item' } ]
  @UI.hidden: true
  LoanUUID;

  @UI: { lineItem:       [ { position: 10, importance: #HIGH },
                           { type: #FOR_ACTION, dataAction: 'approveLoan',  label: 'Approve' },
                           { type: #FOR_ACTION, dataAction: 'lendOut',      label: 'Lend out' },
                           { type: #FOR_ACTION, dataAction: 'sendReminder', label: 'Send reminder' } ],
         identification: [ { position: 10 },
                           { type: #FOR_ACTION, dataAction: 'approveLoan',  label: 'Approve' },
                           { type: #FOR_ACTION, dataAction: 'lendOut',      label: 'Lend out' },
                           { type: #FOR_ACTION, dataAction: 'sendReminder', label: 'Send reminder' } ],
         selectionField: [ { position: 10 } ] }
  BorrowerID;

  @UI: { lineItem: [ { position: 20 } ], identification: [ { position: 20 } ] }
  BeginDate;

  @UI: { lineItem: [ { position: 30 } ], identification: [ { position: 30 } ] }
  EndDate;

  @UI: { lineItem: [ { position: 40, importance: #HIGH } ], identification: [ { position: 40 } ],
         selectionField: [ { position: 20 } ] }
  Status;

  @UI: { lineItem: [ { position: 50 } ], identification: [ { position: 50 } ] }
  Description;

  @UI: { lineItem: [ { position: 60 } ], identification: [ { position: 60 } ] }
  ApprovedBy;

  @UI: { lineItem: [ { position: 70 } ], identification: [ { position: 70 } ] }
  ReminderCount;

  @UI: { lineItem: [ { position: 80 } ], identification: [ { position: 80 } ] }
  CreatedBy;

  @UI.hidden: true
  LocalLastChangedAt;

  @UI.hidden: true
  LastChangedAt;
}
```

```cds
@Metadata.layer: #CORE
@UI.headerInfo: { typeName: 'Item', typeNamePlural: 'Items', title: { value: 'EquipmentID' } }
annotate entity ZRAP_C_LOANITEM_### with
{
  @UI.facet: [ { id: 'Item', purpose: #STANDARD, type: #IDENTIFICATION_REFERENCE, label: 'Item', position: 10 } ]
  @UI.hidden: true
  ItemUUID;

  @UI.hidden: true
  LoanUUID;

  @UI: { lineItem: [ { position: 10, importance: #HIGH } ], identification: [ { position: 10 } ] }
  EquipmentID;

  @UI: { lineItem: [ { position: 20 } ], identification: [ { position: 20 } ] }
  Quantity;

  @UI: { lineItem: [ { position: 30 } ], identification: [ { position: 30 } ] }
  ItemNote;

  @UI.hidden: true
  LocalLastChangedAt;
}
```

프로젝션 BDEF:

```bdef
projection;
strict ( 2 );
use draft;

define behavior for ZRAP_C_LOAN_### alias Loan
use etag
{
  use create;
  use update;
  use delete;

  use action approveLoan;
  use action lendOut;
  use action sendReminder;

  use action Edit;
  use action Activate;
  use action Discard;
  use action Resume;
  use action Prepare;

  use association _Item { create; with draft; }
}

define behavior for ZRAP_C_LOANITEM_### alias Item
use etag
{
  use update;
  use delete;

  use association _Loan { with draft; }
}
```

서비스 정의:

```cds
@EndUserText.label: 'Equipment loan ### - UI service'
define service ZRAP_UI_LOAN_### {
  expose ZRAP_C_LOAN_###     as Loan;
  expose ZRAP_C_LOANITEM_### as Item;
}
```

서비스 바인딩은 ADT 마법사로 만듭니다(Binding Type: OData V4 - UI, 서비스 정의 `ZRAP_UI_LOAN_###`) → Activate → Publish → `Loan` 선택 → Preview.

잠금 붙잡기 클래스:

```abap
CLASS zcl_rap_loan_lockhold_### DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_oo_adt_classrun.
  PROTECTED SECTION.
  PRIVATE SECTION.
ENDCLASS.

CLASS zcl_rap_loan_lockhold_### IMPLEMENTATION.

  METHOD if_oo_adt_classrun~main.

    SELECT SINGLE loan_uuid FROM zrap_loan_### WHERE borrower_id = '000001' INTO @DATA(l1).

    "calls the FOR LOCK handler of step 6 -> enqueue EZRAP_LOAN_###
    SET LOCKS ENTITY zrap_r_loan_###
      FROM VALUE #( ( LoanUUID = l1 ) )
      FAILED DATA(failed)
      REPORTED DATA(reported).

    IF failed IS NOT INITIAL.
      out->write( `L1 could not be locked - is another session holding it?` ).
      RETURN.
    ENDIF.

    "SET A BREAKPOINT ON THE NEXT LINE and keep the debugger open:
    "the lock lives until this RAP transaction ends (end of this program)
    out->write( `L1 is locked. Lock released when this program ends.` ).

  ENDMETHOD.

ENDCLASS.
```

종합 테스트 클래스:

```abap
CLASS zcl_rap_loan_test_### DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_oo_adt_classrun.

  PROTECTED SECTION.
  PRIVATE SECTION.
    "'ALL' = scenarios 0-4, 'LOCK' = lock conflict only (start ZCL_RAP_LOAN_LOCKHOLD_### first)
    CONSTANTS c_mode TYPE string VALUE 'ALL'.

    TYPES ty_failed   TYPE RESPONSE FOR FAILED EARLY zrap_r_loan_###.
    TYPES ty_reported TYPE RESPONSE FOR REPORTED EARLY zrap_r_loan_###.

    DATA out TYPE REF TO if_oo_adt_classrun_out.
    DATA l1  TYPE sysuuid_x16.
    DATA l2  TYPE sysuuid_x16.
    DATA l3  TYPE sysuuid_x16.

    METHODS read_keys.
    METHODS test_authorizations.
    METHODS test_preserve_changes.
    METHODS test_late_failure.
    METHODS test_friend_and_change_docs.
    METHODS test_lock_conflict.

    METHODS switch_on
      IMPORTING switch_id TYPE zrap_loansw_###-switch_id
                value     TYPE zrap_loansw_###-switch_value DEFAULT 'X'.
    METHODS switch_off
      IMPORTING switch_id TYPE zrap_loansw_###-switch_id.

    METHODS print_early
      IMPORTING title    TYPE string
                failed   TYPE ty_failed
                reported TYPE ty_reported.
    METHODS print_db
      IMPORTING title TYPE string.
    METHODS cause_text
      IMPORTING cause       TYPE if_abap_behv=>t_fail_cause
      RETURNING VALUE(text) TYPE string.
ENDCLASS.

CLASS zcl_rap_loan_test_### IMPLEMENTATION.

  METHOD if_oo_adt_classrun~main.

    me->out = out.

    IF c_mode = 'LOCK'.
      read_keys( ).
      test_lock_conflict( ).
      RETURN.
    ENDIF.

    "ALL-0: fresh demo data
    zcl_rap_loan_gen_###=>reset_data( ).
    COMMIT WORK.
    read_keys( ).

    test_authorizations( ).
    test_preserve_changes( ).
    test_late_failure( ).
    test_friend_and_change_docs( ).

  ENDMETHOD.

  METHOD read_keys.
    SELECT SINGLE loan_uuid FROM zrap_loan_### WHERE borrower_id = '000001' INTO @l1.
    SELECT SINGLE loan_uuid FROM zrap_loan_### WHERE borrower_id = '000002' INTO @l2.
    SELECT SINGLE loan_uuid FROM zrap_loan_### WHERE borrower_id = '000003' INTO @l3.
  ENDMETHOD.

  METHOD test_authorizations.

    out->write( `===== ALL-1 authorizations =====` ).

    "global authorization of one action
    switch_on( zcl_rap_loan_aux_###=>switch-deny_approve ).
    MODIFY ENTITIES OF zrap_r_loan_###
      ENTITY Loan
        EXECUTE approveLoan FROM VALUE #( ( LoanUUID = l1 ) )
      FAILED DATA(failed1)
      REPORTED DATA(reported1).
    print_early( title = `DENY_APPROVE / approveLoan L1` failed = failed1 reported = reported1 ).
    ROLLBACK ENTITIES.
    switch_off( zcl_rap_loan_aux_###=>switch-deny_approve ).

    "instance authorization: update denied, but sendReminder (authorization : none) works
    switch_on( zcl_rap_loan_aux_###=>switch-owner_only ).
    MODIFY ENTITIES OF zrap_r_loan_###
      ENTITY Loan
        UPDATE FIELDS ( Description )
        WITH VALUE #( ( LoanUUID = l3 Description = 'Changed by someone else' ) )
      FAILED DATA(failed2)
      REPORTED DATA(reported2).
    print_early( title = `OWNER_ONLY / update L3` failed = failed2 reported = reported2 ).

    MODIFY ENTITIES OF zrap_r_loan_###
      ENTITY Loan
        EXECUTE sendReminder FROM VALUE #( ( LoanUUID = l3 ) )
      FAILED DATA(failed3)
      REPORTED DATA(reported3).
    print_early( title = `OWNER_ONLY / sendReminder L3` failed = failed3 reported = reported3 ).
    ROLLBACK ENTITIES.
    switch_off( zcl_rap_loan_aux_###=>switch-owner_only ).

    "child entity as authorization master
    SELECT SINGLE item_uuid FROM zrap_loani_### WHERE loan_uuid = @l3 INTO @DATA(l3_item).
    switch_on( switch_id = zcl_rap_loan_aux_###=>switch-deny_item_equip value = 'EQ-TRIPOD' ).
    MODIFY ENTITIES OF zrap_r_loan_###
      ENTITY Item
        UPDATE FIELDS ( Quantity )
        WITH VALUE #( ( ItemUUID = l3_item Quantity = 1 ) )
      FAILED DATA(failed4)
      REPORTED DATA(reported4).
    print_early( title = `DENY_ITEM_EQUIP / update L3 item` failed = failed4 reported = reported4 ).
    ROLLBACK ENTITIES.
    switch_off( zcl_rap_loan_aux_###=>switch-deny_item_equip ).

    "dedicated authorization of create-by-association
    switch_on( zcl_rap_loan_aux_###=>switch-deny_add_item ).
    MODIFY ENTITIES OF zrap_r_loan_###
      ENTITY Loan
        CREATE BY \_Item
        FIELDS ( EquipmentID Quantity )
        WITH VALUE #( ( LoanUUID = l1
                        %target  = VALUE #( ( %cid        = 'NEW_ITEM'
                                              EquipmentID = 'EQ-TRIPOD'
                                              Quantity    = 1 ) ) ) )
      FAILED DATA(failed5)
      REPORTED DATA(reported5).
    print_early( title = `DENY_ADD_ITEM / create by _Item L1` failed = failed5 reported = reported5 ).
    ROLLBACK ENTITIES.
    switch_off( zcl_rap_loan_aux_###=>switch-deny_add_item ).

  ENDMETHOD.

  METHOD test_preserve_changes.

    out->write( `===== ALL-2 draft Edit with preserve_changes =====` ).

    "1) create a draft of L1 and change it
    MODIFY ENTITIES OF zrap_r_loan_###
      ENTITY Loan
        EXECUTE Edit
        FROM VALUE #( ( LoanUUID = l1 %param-preserve_changes = abap_false ) )
      ENTITY Loan
        UPDATE FIELDS ( Description )
        WITH VALUE #( ( %is_draft = if_abap_behv=>mk-on LoanUUID = l1 Description = 'Changed in draft' ) )
      FAILED DATA(failed1)
      REPORTED DATA(reported1).
    print_early( title = `Edit (false) + update draft L1` failed = failed1 reported = reported1 ).
    COMMIT ENTITIES.
    out->write( |COMMIT ENTITIES sy-subrc: { sy-subrc }| ).

    "2) a draft exists -> preserve_changes = true must be rejected
    MODIFY ENTITIES OF zrap_r_loan_###
      ENTITY Loan
        EXECUTE Edit
        FROM VALUE #( ( LoanUUID = l1 %param-preserve_changes = abap_true ) )
      FAILED DATA(failed2)
      REPORTED DATA(reported2).
    print_early( title = `Edit (preserve_changes = true) L1` failed = failed2 reported = reported2 ).
    ROLLBACK ENTITIES.

    "3) preserve_changes = false -> the existing draft is overwritten by the active data
    MODIFY ENTITIES OF zrap_r_loan_###
      ENTITY Loan
        EXECUTE Edit
        FROM VALUE #( ( LoanUUID = l1 %param-preserve_changes = abap_false ) )
      FAILED DATA(failed3)
      REPORTED DATA(reported3).
    print_early( title = `Edit (preserve_changes = false) L1` failed = failed3 reported = reported3 ).

    READ ENTITIES OF zrap_r_loan_###
      ENTITY Loan
        FIELDS ( Description )
        WITH VALUE #( ( %is_draft = if_abap_behv=>mk-on LoanUUID = l1 ) )
      RESULT DATA(drafts).
    out->write( |Draft description now: { VALUE #( drafts[ 1 ]-Description OPTIONAL ) }| ).
    COMMIT ENTITIES.

    "4) clean up: discard the draft
    MODIFY ENTITIES OF zrap_r_loan_###
      ENTITY Loan
        EXECUTE Discard
        FROM VALUE #( ( %is_draft = if_abap_behv=>mk-on LoanUUID = l1 ) )
      FAILED DATA(failed4)
      REPORTED DATA(reported4).
    print_early( title = `Discard draft L1` failed = failed4 reported = reported4 ).
    COMMIT ENTITIES.

  ENDMETHOD.

  METHOD test_late_failure.

    DATA failed_late   TYPE RESPONSE FOR FAILED LATE zrap_r_loan_###.
    DATA reported_late TYPE RESPONSE FOR REPORTED LATE zrap_r_loan_###.

    out->write( `===== ALL-3 late save failure =====` ).

    "the legacy system blocks the camera - RAP cannot know this early
    UPDATE zrap_asset_### SET IsBlocked = @abap_true WHERE EquipmentID = 'EQ-CAMERA'.
    COMMIT WORK.

    MODIFY ENTITIES OF zrap_r_loan_###
      ENTITY Loan
        EXECUTE lendOut FROM VALUE #( ( LoanUUID = l2 ) )
      FAILED DATA(failed1)
      REPORTED DATA(reported1).
    print_early( title = `lendOut L2 (interaction phase)` failed = failed1 reported = reported1 ).

    COMMIT ENTITIES RESPONSE OF zrap_r_loan_###
      FAILED   failed_late
      REPORTED reported_late.
    DATA(subrc) = sy-subrc.
    out->write( |COMMIT ENTITIES sy-subrc: { subrc } (4 = early, 8 = late failure)| ).

    LOOP AT failed_late-loan INTO DATA(failed_line).
      out->write( |  late failed Loan { failed_line-%key-LoanUUID }, cause: { cause_text( failed_line-%fail-cause ) }| ).
    ENDLOOP.
    LOOP AT reported_late-loan INTO DATA(reported_line).
      IF reported_line-%msg IS BOUND.
        out->write( |  late message: { reported_line-%msg->if_message~get_text( ) }| ).
      ENDIF.
    ENDLOOP.

    IF subrc <> 0.
      "mandatory after a late failure, otherwise the next EML statement dumps
      ROLLBACK ENTITIES.
    ENDIF.
    print_db( `After rollback (expected: L2 = A, stock unchanged)` ).

    "unblock and try again
    UPDATE zrap_asset_### SET IsBlocked = @abap_false WHERE EquipmentID = 'EQ-CAMERA'.
    COMMIT WORK.

    MODIFY ENTITIES OF zrap_r_loan_###
      ENTITY Loan
        EXECUTE lendOut FROM VALUE #( ( LoanUUID = l2 ) )
      FAILED DATA(failed2)
      REPORTED DATA(reported2).
    print_early( title = `lendOut L2 again` failed = failed2 reported = reported2 ).

    COMMIT ENTITIES RESPONSE OF zrap_r_loan_###
      FAILED   failed_late
      REPORTED reported_late.
    out->write( |COMMIT ENTITIES sy-subrc: { sy-subrc }| ).
    IF sy-subrc <> 0.
      ROLLBACK ENTITIES.
    ENDIF.
    print_db( `After successful lendOut (expected: L2 = L, LAPTOP 3, CAMERA 0)` ).

  ENDMETHOD.

  METHOD test_friend_and_change_docs.

    out->write( `===== ALL-4 BDEF friend + change documents =====` ).

    "extension action of the friend ZRAP_X_LOAN_### -> internal action forceReturn
    MODIFY ENTITIES OF zrap_r_loan_###
      ENTITY Loan
        EXECUTE zzForceReturn FROM VALUE #( ( LoanUUID = l2 ) )
      FAILED DATA(failed1)
      REPORTED DATA(reported1).
    print_early( title = `zzForceReturn L2` failed = failed1 reported = reported1 ).
    COMMIT ENTITIES.
    out->write( |COMMIT ENTITIES sy-subrc: { sy-subrc }| ).
    print_db( `After zzForceReturn (expected: L2 = R)` ).

    zcl_rap_loan_chdoc_###=>print_change_documents( out ).

  ENDMETHOD.

  METHOD test_lock_conflict.

    out->write( `===== LOCK conflict (ZCL_RAP_LOAN_LOCKHOLD_### must hold L1) =====` ).

    MODIFY ENTITIES OF zrap_r_loan_###
      ENTITY Loan
        UPDATE FIELDS ( Description )
        WITH VALUE #( ( LoanUUID = l1 Description = 'Who has the lock?' ) )
      FAILED DATA(failed1)
      REPORTED DATA(reported1).
    print_early( title = `update L1 while locked` failed = failed1 reported = reported1 ).
    ROLLBACK ENTITIES.

  ENDMETHOD.

  METHOD switch_on.
    zcl_rap_loan_gen_###=>set_switch( switch_id = switch_id value = value ).
    "commit, so that ROLLBACK ENTITIES (implicit ROLLBACK WORK) does not undo the switch
    COMMIT WORK.
  ENDMETHOD.

  METHOD switch_off.
    zcl_rap_loan_gen_###=>set_switch( switch_id ).
    COMMIT WORK.
  ENDMETHOD.

  METHOD print_early.

    out->write( |--- { title }| ).
    IF failed IS INITIAL.
      out->write( `  no failed entries` ).
    ENDIF.

    LOOP AT failed-loan INTO DATA(failed_loan).
      out->write( |  failed Loan, cause: { cause_text( failed_loan-%fail-cause ) }| ).
    ENDLOOP.
    LOOP AT failed-item INTO DATA(failed_item).
      out->write( |  failed Item, cause: { cause_text( failed_item-%fail-cause ) }| ).
    ENDLOOP.

    LOOP AT reported-loan INTO DATA(reported_loan).
      IF reported_loan-%msg IS BOUND.
        out->write( |  Loan message: { reported_loan-%msg->if_message~get_text( ) }| ).
      ENDIF.
    ENDLOOP.
    LOOP AT reported-item INTO DATA(reported_item).
      IF reported_item-%msg IS BOUND.
        out->write( |  Item message: { reported_item-%msg->if_message~get_text( ) }| ).
      ENDIF.
    ENDLOOP.

  ENDMETHOD.

  METHOD print_db.
    out->write( |--- { title }| ).
    SELECT SINGLE status FROM zrap_loan_### WHERE loan_uuid = @l2 INTO @DATA(l2_status).
    out->write( |  L2 status: { l2_status }| ).
    SELECT FROM zrap_asset_###
      FIELDS EquipmentID, Stock, IsBlocked
      ORDER BY EquipmentID
      INTO TABLE @DATA(assets).
    out->write( assets ).
  ENDMETHOD.

  METHOD cause_text.
    text = SWITCH #( cause
                     WHEN if_abap_behv=>cause-unauthorized THEN `unauthorized`
                     WHEN if_abap_behv=>cause-locked       THEN `locked`
                     WHEN if_abap_behv=>cause-not_found    THEN `not_found`
                     WHEN if_abap_behv=>cause-conflict     THEN `conflict`
                     WHEN if_abap_behv=>cause-unspecific   THEN `unspecific`
                     ELSE |other ({ cause })| ).
  ENDMETHOD.

ENDCLASS.
```

잠금 충돌 재현 방법(한 사용자로)

1. `ZCL_RAP_LOAN_LOCKHOLD_###`의 마지막 `out->write` 줄에 중단점을 걸고 F9로 실행합니다. 디버거가 멈추면 **그대로 둡니다**(L1 잠금 유지).
2. 테스트 클래스의 `c_mode`를 `'LOCK'`으로 바꿔 활성화하고 다른 창에서 F9로 실행합니다. 같은 사용자라도 다른 세션이므로 enqueue 잠금이 충돌해 6단계 `lock` 메서드가 `cx_abap_foreign_lock`을 잡습니다.
3. 결과 `failed Loan, cause: locked`와 메시지 001을 확인한 뒤 디버거를 끝내고 `c_mode`를 `'ALL'`로 되돌리세요.

클래스 구조 해설

- 테스트 클래스는 **RAP 소비자**입니다. 그래서 `COMMIT ENTITIES`/`ROLLBACK ENTITIES`를 쓸 수 있고(행동 풀 안에서는 금지), 스위치 테이블처럼 RAP 바깥 데이터는 `COMMIT WORK`로 따로 확정합니다. `ROLLBACK ENTITIES`는 BO가 변경 요청을 받았으면 암묵적으로 `ROLLBACK WORK`를 하므로(키워드 문서), 스위치를 커밋하지 않으면 함께 사라집니다.
- `ty_failed`/`ty_reported`는 `RESPONSE FOR FAILED EARLY`/`REPORTED EARLY` 파생 타입입니다. `MODIFY ENTITIES ... FAILED DATA(...)`의 인라인 선언도 같은 타입이라 그대로 넘길 수 있습니다. late 응답은 `RESPONSE FOR FAILED LATE`/`REPORTED LATE`로 따로 선언하고, `COMMIT ENTITIES RESPONSE OF bdef` **긴 형식**으로만 받을 수 있습니다(키워드 문서 예제 `CL_ABAP_BEHAVIOR_SAVER_FAILED`도 같은 형식).
- late 응답 줄에서는 `%key-LoanUUID`를 읽었습니다. 키워드 문서의 `CL_ABAP_BEHAVIOR_SAVER_FAILED` 예제도 late 응답에서 `%key-...`를 읽습니다.
- `print_early`는 실패 원인 이름과 `%msg->if_message~get_text( )`를 출력하는 공용 메서드입니다. `%msg`가 없는 줄(state area를 비우는 줄 등)은 건너뜁니다.

왜 이렇게 쓰나

- **권한 결과가 다른 이유**: `approveLoan`은 `authorization : global`이라 전역 권한 메서드에서만, `lendOut`은 `instance`라 인스턴스 메서드에서만 검사됩니다. `sendReminder`는 `none`이라 `OWNER_ONLY`(인스턴스 권한)가 켜져도 실행됩니다. 품목 수정은 `Item`이 자체 `authorization master`라 **`lhc_item`의 권한 메서드**가 판단합니다(부모 권한이 아님). 품목 추가(`CREATE BY \_Item`)는 부모 쪽 `association _Item { create ( authorization : global, authorization : instance ); }` 때문에 `%assoc-_Item`으로 따로 판단됩니다. 실패 줄이 부모(`failed-loan`)에 나오는지 자식(`failed-item`)에 나오는지는 출력으로 확인하세요(공용 출력 메서드가 둘 다 찍는 이유).
- **preserve_changes**: `Edit`의 `%param-preserve_changes = abap_true`는 "이미 draft가 있으면 Edit을 거부"하라는 뜻입니다(cheat sheet 및 키워드 문서 draft 액션). `abap_false`(기본)는 기존 draft를 활성 데이터로 덮어씁니다. Fiori에서 다른 탭에 열어 둔 draft를 실수로 날리지 않게 하려면 `true`를 씁니다. 거부될 때의 `%fail-cause` 값은 시스템이 정하므로 출력으로 확인하세요.
- **late 실패의 순서**: 상호작용 단계(`lendOut`)는 성공하고, early save(검증)도 통과한 뒤, `save_modified`에서 레거시 API가 차단을 발견합니다. 그래서 `sy-subrc = 8`이고, `ROLLBACK ENTITIES`가 필수입니다. 레거시 API는 COMMIT하지 않으므로 이 롤백이 같은 LUW의 DB 변경까지 되돌려 재고가 그대로 남습니다.
- **잠금과 draft**: `Edit`도 활성 인스턴스를 잠그므로 6단계 `lock`이 불립니다. draft가 남아 있는 동안 다른 사용자가 활성 데이터를 바꾸지 못하게 하는 "지속 잠금"은 draft 인프라가 관리하는데, unmanaged lock과 함께 쓸 때 이 잠금이 어떻게 이어지는지는 문서에서 확인하지 못했습니다(실제 시스템에서 확인 필요). 이 테스트가 마지막에 `Discard`를 하는 이유이기도 합니다.
- **변경 문서**: ALL-3과 ALL-4의 상태 변경(A→L, L→R)이 기록됩니다. `reset_data`는 업무 테이블만 지우므로, 10단계에서 만든 변경 문서도 함께 출력됩니다. `forceReturn`은 재고를 되돌리지 않습니다(데모 단순화). 실제라면 `save_modified`에 반납 API 호출을 추가하세요.

자주 나는 오류와 해결

- `CX_SADL_DUMP_APPL_MODEL_ERROR` 런타임 오류: late 실패(`sy-subrc = 8`) 뒤 `ROLLBACK ENTITIES` 없이 EML을 이어서 썼습니다.
- `zzForceReturn`이 "unknown"으로 문법 오류: 11단계 확장 BDEF가 비활성 상태입니다.
- `if_abap_behv=>t_fail_cause`를 찾지 못하면 F2로 `failed-loan`의 `%fail-cause` 타입을 확인해 그 타입으로 바꾸세요(실제 시스템에서 확인 필요).
- ALL-2에서 첫 `Edit`이 실패하면: 이전 실행에서 남은 draft가 있을 수 있습니다. `reset_data`가 draft 테이블도 지우므로 처음부터 다시 실행하세요.
- 잠금 시나리오에서 `locked`가 아니라 실패가 없다면: 잠금 붙잡기 클래스가 이미 끝났습니다(디버거를 닫으면 RAP 트랜잭션이 끝나 잠금이 풀림).
- Fiori Preview에서 액션 버튼이 안 보이면: 프로젝션 BDEF에 `use action`이 있는지, MDE의 `dataAction` 철자가 BDEF 액션 이름과 같은지 확인하세요.

</details>

## 출처

- SAP-samples/abap-cheat-sheets(main): [36_RAP_Behavior_Definition_Language.md](https://github.com/SAP-samples/abap-cheat-sheets/blob/main/36_RAP_Behavior_Definition_Language.md), [08_EML_ABAP_for_RAP.md](https://github.com/SAP-samples/abap-cheat-sheets/blob/main/08_EML_ABAP_for_RAP.md), [33_ABAP_for_Cloud_Development.md](https://github.com/SAP-samples/abap-cheat-sheets/blob/main/33_ABAP_for_Cloud_Development.md), [22_Misc_ABAP_Classes.md](https://github.com/SAP-samples/abap-cheat-sheets/blob/main/22_Misc_ABAP_Classes.md), [03_ABAP_SQL.md](https://github.com/SAP-samples/abap-cheat-sheets/blob/main/03_ABAP_SQL.md), [files/abap_release_news_viewer.html](https://github.com/SAP-samples/abap-cheat-sheets/blob/main/files/abap_release_news_viewer.html)
- SAP-samples/abap-cheat-sheets(rap 브랜치): [src/zr_demo_abap96.bdef.asbdef](https://github.com/SAP-samples/abap-cheat-sheets/blob/rap/src/zr_demo_abap96.bdef.asbdef), [src/zcl_demo_abap_abp_aux_cl96.clas.abap](https://github.com/SAP-samples/abap-cheat-sheets/blob/rap/src/zcl_demo_abap_abp_aux_cl96.clas.abap), [src/zbp_r_demo_abap96.clas.locals_imp.abap](https://github.com/SAP-samples/abap-cheat-sheets/blob/rap/src/zbp_r_demo_abap96.clas.locals_imp.abap)
- SAP-samples/abap-platform-refscen-flight(ABAP-platform-cloud 브랜치): [/DMO/BP_TRAVEL_U locals_imp](https://github.com/SAP-samples/abap-platform-refscen-flight/blob/ABAP-platform-cloud/src/%23dmo%23bp_travel_u.clas.locals_imp.abap), [/DMO/BP_TRAVEL_D locals_imp](https://github.com/SAP-samples/abap-platform-refscen-flight/blob/ABAP-platform-cloud/src/%23dmo%23bp_travel_d.clas.locals_imp.abap)
- SAP-samples/abap-platform-reuse-services: [README.md](https://github.com/SAP-samples/abap-platform-reuse-services/blob/main/README.md), [zreuser_salesordertp_002.bdef.asbdef](https://github.com/SAP-samples/abap-platform-reuse-services/blob/main/src/zreuser_salesordertp_002.bdef.asbdef), [zreusebp_r_salesordertp_002.clas.locals_imp.abap](https://github.com/SAP-samples/abap-platform-reuse-services/blob/main/src/zreusebp_r_salesordertp_002.clas.locals_imp.abap), [zcl_zreuse_so_002_chdo.clas.abap](https://github.com/SAP-samples/abap-platform-reuse-services/blob/main/src/zcl_zreuse_so_002_chdo.clas.abap), [zreusecl_get_change_docs_002.clas.abap](https://github.com/SAP-samples/abap-platform-reuse-services/blob/main/src/zreusecl_get_change_docs_002.clas.abap)
- ABAP 키워드 문서(클라우드판)의 GitHub 미러 marianfoo/abap-docs(`docs/cloud/md/`): [ABENBDL_CHANGE_DOCUMENTS](https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABENBDL_CHANGE_DOCUMENTS.md), [ABENBDL_CHANGEDOCS_OPTIONS](https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABENBDL_CHANGEDOCS_OPTIONS.md), [ABENBDL_WITH_FRIENDS](https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABENBDL_WITH_FRIENDS.md), [ABENBDL_EXTENSIBLE](https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABENBDL_EXTENSIBLE.md), [ABENBDL_EXTENSIBILITY_ENABLING_M_U](https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABENBDL_EXTENSIBILITY_ENABLING_M_U.md), [ABENBDL_EXTEND_BEH](https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABENBDL_EXTEND_BEH.md), [ABENBDL_AUXILIARY_CLASS](https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABENBDL_AUXILIARY_CLASS.md), [ABAPRAP_AUXILIARY_CLASS](https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABAPRAP_AUXILIARY_CLASS.md), [ABENABP_AUX_CL_ABEXA](https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABENABP_AUX_CL_ABEXA.md), [ABAPCLASS_FOR_BEHAVIOR_OF](https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABAPCLASS_FOR_BEHAVIOR_OF.md), [ABENABP_CL_ABAP_BEH_SAVER_FAILED](https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABENABP_CL_ABAP_BEH_SAVER_FAILED.md), [ABENCL_ABAP_BEH_SAVER_FAILED_ABEXA](https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABENCL_ABAP_BEH_SAVER_FAILED_ABEXA.md), [ABAPDERIVED_TYPES_PARAM](https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABAPDERIVED_TYPES_PARAM.md), [ABENBDL_LOCKING](https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABENBDL_LOCKING.md), [ABENBDL_LOCK_MASTER](https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABENBDL_LOCK_MASTER.md), [ABAPHANDLER_METH_LOCK](https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABAPHANDLER_METH_LOCK.md), [ABENBDL_PERSISTENT_TABLE](https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABENBDL_PERSISTENT_TABLE.md), [ABENBDL_AUTHORIZATION](https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABENBDL_AUTHORIZATION.md), [ABENBDL_AUTH_MASTER](https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABENBDL_AUTH_MASTER.md), [ABENBDL_ACTIONS_AUTH_GLOBAL](https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABENBDL_ACTIONS_AUTH_GLOBAL.md), [ABENBDL_ACTIONS_AUTH_INSTANCE](https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABENBDL_ACTIONS_AUTH_INSTANCE.md), [ABENBDL_ACTIONS_AUTH_UPDATE](https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABENBDL_ACTIONS_AUTH_UPDATE.md), [ABENBDL_ASSOCIATION](https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABENBDL_ASSOCIATION.md), [ABENBDL_DRAFT_ACTION](https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABENBDL_DRAFT_ACTION.md), [ABENBDL_DRAFT_TABLE](https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABENBDL_DRAFT_TABLE.md), [ABENCDS_DEFINE_TABLE_ENTITY](https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABENCDS_DEFINE_TABLE_ENTITY.md), [ABENCDS_TABLE_ENTITY_CLIENT](https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABENCDS_TABLE_ENTITY_CLIENT.md), [ABENNEWS-916-CDS_BDL](https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABENNEWS-916-CDS_BDL.md), [ABENNEWS-914-CDS_BDL](https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABENNEWS-914-CDS_BDL.md), [ABAPROLLBACK_ENTITIES](https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABAPROLLBACK_ENTITIES.md), [ABAPCOMMIT_ENTITIES](https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABAPCOMMIT_ENTITIES.md), [ABAPSET_LOCKS](https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABAPSET_LOCKS.md)
- 커뮤니티 예제(참고): Xexer/abap_rap_blog — [zbs_r_sasale.bdef.asbdef](https://github.com/Xexer/abap_rap_blog/blob/main/src/zbs_demo_rap_sales/zbs_r_sasale.bdef.asbdef)(변경 문서·보조 클래스), [zbs_t_cdspatterninvoice.ddls.asddls](https://github.com/Xexer/abap_rap_blog/blob/main/src/zbs_demo_rap_pattern/zbs_demo_rap_pattern_cds/zbs_t_cdspatterninvoice.ddls.asddls), [zbs_t_cdspatterninvoice.bdef.asbdef](https://github.com/Xexer/abap_rap_blog/blob/main/src/zbs_demo_rap_pattern/zbs_demo_rap_pattern_cds/zbs_t_cdspatterninvoice.bdef.asbdef)(table entity를 persistent table로), gfcarlson/cds_book [Chapter11/BDEF_ZR_SalesOrderTP.txt](https://github.com/gfcarlson/cds_book/blob/master/Chapter11/BDEF_ZR_SalesOrderTP.txt)(`lock master unmanaged`)

