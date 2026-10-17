## 5. 고급·특수 기능 보충

### R-17. 프로젝션·인터페이스 계층 고급과 EML 심화: augmentation, 프로젝션 전용 액션, instance filter, FORWARDING PRIVILEGED, WITH CHANGES, RTTS [작성] ★★★
<!-- covers: multiple projections of one BO, processor projection, approver projection, non-draft projection of draft BO, use create, use update, use delete, use action, use function, use association, field ( readonly ) in projection, field ( suppress ), field ( modify ), augmented field, projection implementation in class unique, projection behavior pool, projection-specific action, projection-specific function, projection authorization, get_global_authorizations in projection, augment, use create ( augment, precheck ), use update ( augment, precheck ), FOR MODIFY augment, MODIFY AUGMENTING ENTITIES, RELATING TO BY, abp_behv_relating_tab, projection precheck, FOR PRECHECK, with managed instance filter, transactional query WHERE, deep parameter (redefined parameter), deep result, abstract BDEF with hierarchy, deep mapping for, with privileged mode (projection), PRIVILEGED, FORWARDING PRIVILEGED, READ ENTITY IN LOCAL MODE WITH CHANGES, TYPE TABLE FOR READ CHANGES, %chg, if_abap_behv=>cop, typekind-result_chg, cl_abap_behv_aux=>get_current_phase, get_current_context, get_current_handler_kind, cl_abap_tabledescr=>get_bdef_derived_type, cl_abap_structdescr=>get_bdef_derived_type, abp_bdef_derived_type, get_base_type, applies_to_data, custom secondary table key on BDEF derived type, KEY entity, KEY cid, KEY draft, KEY pid, KEY id, contract check, BEHAVIOR_BAD_HANDLER_RESPONSE, EML read not allowed in late save, virtual element in projection, if_sadl_exit_calc_element_read -->

**목표**
- 하나의 기본 BO(`ZRAP_R_TRAVEL_###`) 위에 역할이 다른 프로젝션 BO 두 개(승인자·처리자)를 만들고, 프로젝션마다 노출 연산·필드 제어·UI를 다르게 설계할 수 있습니다.
- 프로젝션 BDEF 안에서 **새 액션·함수를 정의하고 프로젝션 행동 풀에서 구현**하며, 그 권한을 프로젝션에서 제어할 수 있습니다.
- `augment`(+ `precheck`)로 들어오는 요청을 프로젝션 계층에서 보강하고, `field ( modify )`로 프로젝션에만 있는 필드를 기본 BO 필드로 옮겨 쓸 수 있습니다.
- `with managed instance filter`, `field ( suppress )`, 재정의 파라미터(`deep parameter`), 프로젝션의 `with privileged mode`가 무엇을 바꾸는지 EML로 직접 확인할 수 있습니다.
- `PRIVILEGED`와 `FORWARDING PRIVILEGED`의 차이, `READ ... WITH CHANGES`, `cl_abap_behv_aux`의 단계·문맥 정보, RTTS의 `get_bdef_derived_type`, 사용자 정의 보조 키, 계약 검사(`BEHAVIOR_BAD_HANDLER_RESPONSE`)와 late save 읽기 금지를 실험으로 이해합니다.

**전제**
- R-01 ~ R-04가 끝난 관리형 Travel BO가 활성화되어 있습니다: `ZRAP_R_TRAVEL_###`(draft, late numbering, `with privileged mode disabling NoCheckWhenPrivileged`, 인스턴스 권한 시뮬레이션), 행동 풀 `ZBP_RAP_R_TRAVEL_###`(핸들러 `lhc_travel`, 세이버 `lsc_zrap_r_travel_###`, `save_modified` 구현), 스위치 테이블 `ZRAP_CTRL_###`(R-03, `deny_country`), 메시지 클래스 `ZRAP_MSG_###`, 예외 클래스 `ZCM_RAP_###`, 추상 엔터티 `ZRAP_A_DISCOUNT_###`.
- R-12(EML 기초, 동적 EML, `AUGMENTING` 개념)를 풀었으면 좋습니다. 이 문제는 R-12 8단계에서 "개념만" 다룬 augmentation과 프로젝션 계층을 실제로 만듭니다.
- 기존 앱(`ZRAP_C_TRAVEL_###`, `ZRAP_UI_TRAVEL_O4_###`)은 **건드리지 않습니다.** 새 프로젝션 두 개를 옆에 추가합니다. 기본 BO는 10단계에서 실험용 검증 하나와 세이버 실험 코드(스위치로 꺼 둠)만 추가합니다.
- 데이터: `ZRAP_ATRAV_###`에 통화 `EUR`인 Travel과 `EUR`가 아닌 Travel이 각각 하나 이상 있어야 합니다(R-01 데이터 생성 클래스는 /DMO 데이터를 복사하므로 보통 섞여 있습니다. 없으면 기존 앱에서 하나 만드세요).

**만들 객체**

| 순서 | 객체 유형 | 이름 | 역할 |
|---|---|---|---|
| 1 | 메시지/예외 클래스(확장) | `ZRAP_MSG_###` 170~173, `ZCM_RAP_###` | R-17 메시지 |
| 2 | 추상 엔터티 | `ZRAP_A_REVISION_###` | 승인자 액션 `requestRevision` 입력 |
| 3 | 추상 엔터티 | `ZRAP_A_APPR_INFO_###` | 승인자 함수 `getApprovalInfo` 결과 |
| 4 | 클래스 | `ZCL_RAP_R17_TRACE_###` | 핸들러 안의 정보를 콘솔로 넘기는 실험용 추적 클래스 |
| 5 | 프로젝션 뷰 | `ZRAP_C_TRAVEL_APPR_###`, `ZRAP_C_BOOKING_APPR_###` | 승인자용 프로젝션(EUR만) |
| 6 | 접근 제어(DCL) | `ZRAP_C_TRAVEL_APPR_###`, `ZRAP_C_BOOKING_APPR_###` | R 뷰 조건 상속 |
| 7 | 메타데이터 확장 | `ZRAP_C_TRAVEL_APPR_###`, `ZRAP_C_BOOKING_APPR_###` | 승인자 UI |
| 8 | 프로젝션 BDEF | `ZRAP_C_TRAVEL_APPR_###` | 승인자 행동: update, accept/reject, 새 액션·함수 |
| 9 | 행동 풀 | `ZBP_RAP_C_TRAVEL_APPR_###` | 승인자 전용 액션·함수·권한 구현 |
| 10 | (선택) 추상 엔터티 + 추상 BDEF | `ZRAP_A_DISCOUNT_APPR_###` | 재정의 파라미터(`deep parameter`) |
| 11 | 프로젝션 뷰 | `ZRAP_C_TRAVEL_PROC_###`, `ZRAP_C_BOOKING_PROC_###` | 처리자용 프로젝션(가상 요소 `ShortNote`) |
| 12 | 클래스 | `ZCL_RAP_R17_VE_###` | `ShortNote` 계산 |
| 13 | DCL / MDE | `ZRAP_C_TRAVEL_PROC_###`, `ZRAP_C_BOOKING_PROC_###` | 처리자 접근 제어·UI |
| 14 | 프로젝션 BDEF | `ZRAP_C_TRAVEL_PROC_###` | 처리자 행동: CUD + augment/precheck |
| 15 | 행동 풀 | `ZBP_RAP_C_TRAVEL_PROC_###` | augment, precheck 구현 |
| 16 | 서비스 정의/바인딩 | `ZRAP_UI_TRAVEL_APPR_###` / `ZRAP_UI_TRAVEL_APPR_O4_###`, `ZRAP_UI_TRAVEL_PROC_###` / `ZRAP_UI_TRAVEL_PROC_O4_###` | 두 앱 |
| 17 | 콘솔 클래스 | `ZCL_RAP_R17_EML_###` | 모든 실험 실행 |
| 18 | 기본 BDEF/행동 풀(수정) | `ZRAP_R_TRAVEL_###`, `ZBP_RAP_R_TRAVEL_###` | `r17TraceChanges` 검증, late save 실험 |

> 이 문제의 문법 중 여러 개는 최신 릴리스 기능이라 로컬 SAP 샘플에 예제가 없습니다. 각 단계 정답에 근거(SAP 샘플 / 치트시트 / 커뮤니티 예제)와 도입 릴리스를 적었고, 근거가 약한 줄은 "(실제 시스템에서 확인 필요)"로 표시했습니다. 표시된 줄에서 구문 오류가 나면 ADT의 F1(키워드 문서)과 Quick Fix(Ctrl+1)로 정확한 형태를 찾으세요.

#### 1단계. 설계와 준비: 메시지, 추상 엔터티, 추적 클래스

요구사항
1. 먼저 두 프로젝션의 역할을 표로 정리하세요(정답의 설계 표와 비교).
   - **승인자(Approver)**: EUR Travel만 봅니다. 생성·삭제 불가, 수정은 예약 수수료(`BookingFee`)만. `acceptTravel`, `rejectTravel`, `deductDiscount` 사용. 승인자 전용 액션 `requestRevision`(수정 요청: 사유를 받아 설명 앞에 `[REVISION] 사유`를 붙임)과 함수 `getApprovalInfo`(출발까지 남은 일수, Booking 수, 권고 문구)를 새로 정의합니다. Booking은 읽기만.
   - **처리자(Processor)**: 모든 Travel. 생성·수정·삭제, Booking 생성. 화면 전용 입력 필드 `ShortNote`(20자)를 입력하면 기본 BO의 `Description`이 `[P] <ShortNote>`로 채워집니다(augmentation). 생성 시 `BookingFee`를 입력하지 않으면 20(입력한 통화)으로 보강합니다. 설명이 `!`로 시작하면 프로젝션 precheck에서 거부합니다.
2. 메시지 클래스 `ZRAP_MSG_###`에 메시지를 추가하세요.
   - 170 `Revision for travel &1 requested: &2`
   - 171 `Only open travels can be sent back for revision (travel &1).`
   - 172 `Description must not start with "!" in the processor app.`
   - 173 `You are not allowed to request revisions.`
3. `ZCM_RAP_###`에 텍스트 ID 상수 `revision_requested`, `revision_not_open`, `proc_description_invalid`, `revision_not_allowed`, 속성 `mv_note`(TYPE c LENGTH 50), 생성자 선택 파라미터 `note`를 추가하세요.
4. 추상 엔터티 두 개를 만드세요.
   - `ZRAP_A_REVISION_###`: `revision_note` (char 50) — 팝업 라벨 "Reason for revision"
   - `ZRAP_A_APPR_INFO_###`: `travel_id`(/dmo/travel_id), `days_to_start`(int4), `booking_count`(int4), `total_price`(/dmo/total_price), `currency_code`(/dmo/currency_code), `recommendation`(char 40). 금액-통화 연결 필요.
5. 실험용 추적 클래스 `ZCL_RAP_R17_TRACE_###`를 만드세요. 정적 문자열 표 `gt_log`(READ-ONLY), 정적 메서드 `add( iv_text )`, `reset( )`, 정적 스위치 `gv_trace_on`(abap_boolean), `gv_provoke_late_read`(abap_boolean), `gv_bad_response`(c 1자리: 공백/`S`/`F`). 행동 구현이 이 클래스에 기록하면, 같은 세션에서 EML을 실행한 콘솔 클래스가 그 기록을 출력합니다.

**직접 추가할 어노테이션**
- `@EndUserText.label` — 추상 엔터티 설명과 팝업 입력 필드 라벨
- `@Semantics.amount.currencyCode` — 함수 결과의 금액 필드가 어느 통화 필드를 따르는지

**확인**
- 메시지 클래스, 예외 클래스, 추상 엔터티 2개, 추적 클래스가 오류 없이 활성화됩니다.
- 추상 엔터티를 Data Preview할 수는 없습니다(데이터가 없는 타입 정의). 대신 ADT에서 엔터티 이름 위에 F2를 눌러 필드 목록을 확인하세요.

<details><summary>정답·해설</summary>

설계 표

| 항목 | 기본 BO `ZRAP_R_TRAVEL_###` | 기존 앱 `ZRAP_C_TRAVEL_###` | 승인자 `ZRAP_C_TRAVEL_APPR_###` | 처리자 `ZRAP_C_TRAVEL_PROC_###` |
|---|---|---|---|---|
| draft | 있음 | `use draft` | 사용 안 함(활성 데이터 직접 수정) | 사용 안 함 |
| 보이는 Travel | 전체 | 전체 | `CurrencyCode = 'EUR'`만 (managed instance filter) | 전체 |
| create / delete | 있음 | 노출 | 없음 | 노출 + `augment, precheck` |
| update | 있음 | 노출 | 노출(BookingFee만 수정 가능) | 노출 + `augment, precheck` |
| 액션 | accept, reject, discount, … | 전부 | accept, reject, discount + **새 액션 `requestRevision`** | 없음 |
| 함수 | getOpenTravelCount … | 전부 | **새 함수 `getApprovalInfo`** | 없음 |
| 전용 필드 | – | `OverallStatusCriticality`(가상) | `CreatedBy`, `CreatedAt` suppress | `ShortNote`(가상, `field ( modify )`) |
| 행동 풀 | `ZBP_RAP_R_TRAVEL_###` | 없음 | `ZBP_RAP_C_TRAVEL_APPR_###` | `ZBP_RAP_C_TRAVEL_PROC_###` |

메시지(ADT에서 `ZRAP_MSG_###` 열고 행 추가):

| 번호 | 메시지 텍스트 |
|---|---|
| 170 | `Revision for travel &1 requested: &2` |
| 171 | `Only open travels can be sent back for revision (travel &1).` |
| 172 | `Description must not start with "!" in the processor app.` |
| 173 | `You are not allowed to request revisions.` |

`ZCM_RAP_###`에 추가할 부분(R-02/R-03에서 만든 클래스에 넣습니다):

```abap
    "--- R-17: new text IDs -------------------------------------
    CONSTANTS:
      BEGIN OF revision_requested,
        msgid TYPE symsgid VALUE 'ZRAP_MSG_###',
        msgno TYPE symsgno VALUE '170',
        attr1 TYPE scx_attrname VALUE 'MV_TRAVEL_ID',
        attr2 TYPE scx_attrname VALUE 'MV_NOTE',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF revision_requested,
      BEGIN OF revision_not_open,
        msgid TYPE symsgid VALUE 'ZRAP_MSG_###',
        msgno TYPE symsgno VALUE '171',
        attr1 TYPE scx_attrname VALUE 'MV_TRAVEL_ID',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF revision_not_open,
      BEGIN OF proc_description_invalid,
        msgid TYPE symsgid VALUE 'ZRAP_MSG_###',
        msgno TYPE symsgno VALUE '172',
        attr1 TYPE scx_attrname VALUE '',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF proc_description_invalid,
      BEGIN OF revision_not_allowed,
        msgid TYPE symsgid VALUE 'ZRAP_MSG_###',
        msgno TYPE symsgno VALUE '173',
        attr1 TYPE scx_attrname VALUE '',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF revision_not_allowed.

    "--- R-17: new attribute (message variable &2 of 170) ---------
    DATA mv_note TYPE c LENGTH 50 READ-ONLY.

    "--- constructor: add one OPTIONAL parameter at the end -------
    "    note TYPE c LENGTH 50 OPTIONAL      (signature: note TYPE csequence OPTIONAL also works)
    "--- constructor implementation: add one line -----------------
    "    mv_note = note.
```

> 생성자 파라미터에 `TYPE c LENGTH 50`처럼 길이를 직접 쓸 수 없으면(파라미터 타입은 완전한 타입이어야 함) 클래스 PUBLIC SECTION에 `TYPES ty_note TYPE c LENGTH 50.`을 두고 `note TYPE ty_note OPTIONAL`, `DATA mv_note TYPE ty_note READ-ONLY.`로 쓰세요.

추상 엔터티:

```cds
@EndUserText.label: 'Parameter: request revision'              // (→ 어노테이션 탭: @EndUserText.label)
define abstract entity ZRAP_A_REVISION_###
{
  @EndUserText.label: 'Reason for revision'                    // 액션 팝업 입력 필드 라벨
  revision_note : abap.char(50);
}
```

```cds
@EndUserText.label: 'Result: approval information'
define abstract entity ZRAP_A_APPR_INFO_###
{
  travel_id      : /dmo/travel_id;
  days_to_start  : abap.int4;
  booking_count  : abap.int4;
  @Semantics.amount.currencyCode: 'currency_code'              // (→ 어노테이션 탭: @Semantics.amount.currencyCode)
  total_price    : /dmo/total_price;
  currency_code  : /dmo/currency_code;
  recommendation : abap.char(40);
}
```

추적 클래스:

```abap
CLASS zcl_rap_r17_trace_### DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    "lines written by behavior implementations, read by the console class
    CLASS-DATA gt_log TYPE string_table READ-ONLY.

    "switches set by the console class before an EML call
    CLASS-DATA gv_trace_on          TYPE abap_boolean.
    CLASS-DATA gv_provoke_late_read TYPE abap_boolean.
    CLASS-DATA gv_bad_response      TYPE c LENGTH 1.   "' ' = off, 'S' = state area, 'F' = foreign failed key

    CLASS-METHODS add
      IMPORTING iv_text TYPE string.

    CLASS-METHODS reset.

ENDCLASS.


CLASS zcl_rap_r17_trace_### IMPLEMENTATION.

  METHOD add.
    APPEND iv_text TO gt_log.
  ENDMETHOD.

  METHOD reset.
    CLEAR: gt_log, gv_trace_on, gv_provoke_late_read, gv_bad_response.
  ENDMETHOD.

ENDCLASS.
```

해설
- **왜 프로젝션을 여러 개 두나**: 기본 BO는 "업무 규칙 전체", 프로젝션은 "누가 무엇을 하게 할지"입니다. 참조 시나리오도 같은 BO `/DMO/I_Travel_M` 위에 처리자 `/DMO/C_Travel_Processor_M`(create/update/delete, copy, Booking 생성)과 승인자 `/DMO/C_Travel_Approver_M`(update, accept/reject만, `field ( readonly ) BeginDate, EndDate, TotalPrice, CustomerID`)을 따로 둡니다. draft 시나리오에도 draft 없는 승인자 프로젝션 `/DMO/C_Travel_A_D`가 draft BO `/DMO/R_Travel_D` 위에 있습니다. 이 문제의 승인자·처리자도 이 구조를 따릅니다.
- **추적 클래스를 쓰는 이유**: 핸들러·세이버 메서드는 콘솔에 직접 쓸 수 없습니다. 콘솔에서 EML을 실행하면 RAP 핸들러도 같은 내부 세션에서 돌기 때문에, 정적 속성에 남긴 기록을 콘솔이 나중에 읽을 수 있습니다. OData(Fiori) 요청은 별도 세션이라 이 기록이 보이지 않습니다. 실습 장치일 뿐이고, 실제 BO에서는 애플리케이션 로그(BALI) 등을 씁니다.
- 기능별 도입 릴리스(33 Release News 치트시트 기준, 괄호는 분기 릴리스):

| 기능 | 릴리스 |
|---|---|
| 프로젝션 BDEF `augment` | 7.82 (2011) |
| 프로젝션 BDEF 새 액션·함수, 그 권한 개념, augmented 필드의 필드 특성, `field ( suppress )` | 7.84 (2105) |
| 프로젝션 BO용 `with privileged mode` | 7.85 (2108) |
| `cl_abap_behv_aux=>get_current_phase` | 7.92 (2305) |
| `with managed instance filter`, 재정의 파라미터(`deep parameter` / `deep result`) | 7.93 (2308) |
| `FORWARDING PRIVILEGED`, late save에서 EML 읽기 금지 | 9.12 (2408) |
| `get_bdef_derived_type`(RTTS), 파생 타입 사용자 정의 보조 키, 새 계약 검사 | 9.14 (2502) |
| `READ ... WITH CHANGES` | 9.17 (2511) |

BTP ABAP 환경(트라이얼)은 최신 분기 릴리스를 따르므로 모두 쓸 수 있어야 하지만, 트라이얼의 실제 릴리스는 ADT의 About 또는 시스템 정보에서 확인하세요.

</details>

#### 2단계. 승인자 프로젝션 뷰: WHERE 조건, 접근 제어, UI

요구사항
1. `ZRAP_C_TRAVEL_APPR_###`(root)를 `ZRAP_R_TRAVEL_###` 위의 트랜잭션 쿼리 프로젝션으로 만드세요.
   - 필드: `TravelID`, `AgencyID`(+ `AgencyName`), `CustomerID`(+ `CustomerName`), `BeginDate`, `EndDate`, `BookingFee`, `TotalPrice`, `CurrencyCode`, `Description`, `OverallStatus`(+ 로그온 언어 텍스트 `OverallStatusText`), `CreatedBy`, `CreatedAt`, `LocalLastChangedAt`, `LastChangedAt`. 첨부 필드는 넣지 않습니다.
   - 조건: 통화가 `EUR`인 Travel만 (뷰 끝에 WHERE).
   - 연관: `_Booking`은 승인자 Booking 뷰로 재지정, `_Agency`, `_Customer`, `_OverallStatus`, `_Currency`.
2. `ZRAP_C_BOOKING_APPR_###`를 `ZRAP_R_BOOKING_###` 위에 만드세요. R 뷰 필드 전부, `_Travel`은 부모 재지정, `_Customer`, `_Carrier`.
3. 두 뷰에 접근 제어(DCL)를 만드세요. 조건은 R 뷰에서 상속합니다.
4. 메타데이터 확장 두 개를 만드세요. Travel 목록: Travel ID, Agency, Customer, Total Price, Status, 버튼 Accept / Reject / Request Revision. 상세: 일반 정보 섹션 + Booking 표 섹션. 필터: Agency, Customer, Status.

**직접 추가할 어노테이션**
- `@AccessControl.authorizationCheck` — DCL 검사 여부
- `@Metadata.allowExtensions` — MDE를 붙일 수 있게 함
- `@EndUserText.label` — 뷰 설명
- `@ObjectModel.semanticKey` — 화면에서 사용자에게 보여 줄 업무 키
- `@Search.searchable` / `@Search.defaultSearchElement` — 검색창 대상
- `@Consumption.valueHelpDefinition` — 필터 F4
- `@ObjectModel.text.element` — 코드 옆에 이름 표시
- `@Metadata.layer` — MDE 레이어
- `@UI.headerInfo` — 상세 화면 제목
- `@UI.facet` — 상세 화면 섹션 구성
- `@UI.lineItem` — 목록 열과 목록 위 액션 버튼(`#FOR_ACTION`)
- `@UI.identification` — 상세 화면 필드와 상세 화면 액션 버튼
- `@UI.selectionField` — 필터 바
- `@UI.hidden` — 텍스트 전용 필드 숨김

**확인**
- 네 개 CDS 객체가 활성화됩니다.
- `ZRAP_C_TRAVEL_APPR_###`를 Data Preview(F8)로 열면 `CurrencyCode`가 모두 `EUR`입니다. 같은 Data Preview로 `ZRAP_C_TRAVEL_###`를 열어 건수를 비교하세요.
- 아직 BDEF가 없으므로 서비스는 만들지 않습니다(8단계).

<details><summary>정답·해설</summary>

```cds
@AccessControl.authorizationCheck: #CHECK                    // DCL로 행 수준 권한 (→ 어노테이션 탭: @AccessControl.authorizationCheck)
@Metadata.allowExtensions: true                              // MDE 허용 (→ 어노테이션 탭: @Metadata.allowExtensions)
@EndUserText.label: 'Travel - approver projection'           // (→ 어노테이션 탭: @EndUserText.label)
@ObjectModel.semanticKey: [ 'TravelID' ]                     // (→ 어노테이션 탭: @ObjectModel.semanticKey)
@Search.searchable: true                                     // (→ 어노테이션 탭: @Search.searchable)
define root view entity ZRAP_C_TRAVEL_APPR_###
  provider contract transactional_query                      // UI 서비스용 프로젝션
  as projection on ZRAP_R_TRAVEL_###
{
      @Search.defaultSearchElement: true                     // (→ 어노테이션 탭: @Search.defaultSearchElement)
  key TravelID,

      @Consumption.valueHelpDefinition: [ { entity: { name: '/DMO/I_Agency_StdVH', element: 'AgencyID' } } ]   // (→ 어노테이션 탭: @Consumption.valueHelpDefinition)
      @ObjectModel.text.element: [ 'AgencyName' ]            // (→ 어노테이션 탭: @ObjectModel.text.element)
      AgencyID,
      _Agency.Name              as AgencyName,

      @Search.defaultSearchElement: true
      @Consumption.valueHelpDefinition: [ { entity: { name: '/DMO/I_Customer_StdVH', element: 'CustomerID' } } ]
      @ObjectModel.text.element: [ 'CustomerName' ]
      CustomerID,
      _Customer.LastName        as CustomerName,

      BeginDate,
      EndDate,
      BookingFee,
      TotalPrice,
      CurrencyCode,
      Description,

      @Consumption.valueHelpDefinition: [ { entity: { name: '/DMO/I_Overall_Status_VH', element: 'OverallStatus' } } ]
      @ObjectModel.text.element: [ 'OverallStatusText' ]
      OverallStatus,
      _OverallStatus._Text.Text as OverallStatusText : localized,

      CreatedBy,
      CreatedAt,
      LocalLastChangedAt,
      LastChangedAt,

      /* Associations */
      _Booking : redirected to composition child ZRAP_C_BOOKING_APPR_###,
      _Agency,
      _Customer,
      _OverallStatus,
      _Currency
}
where CurrencyCode = 'EUR'                                   // 승인자 담당 범위: EUR Travel만
```

```cds
@AccessControl.authorizationCheck: #CHECK
@Metadata.allowExtensions: true
@EndUserText.label: 'Booking - approver projection'
@ObjectModel.semanticKey: [ 'BookingID' ]
define view entity ZRAP_C_BOOKING_APPR_###
  as projection on ZRAP_R_BOOKING_###
{
  key TravelID,
  key BookingID,
      BookingDate,
      CustomerID,
      CarrierID,
      ConnectionID,
      FlightDate,
      FlightPrice,
      CurrencyCode,
      BookingStatus,
      LocalLastChangedAt,

      /* Associations */
      _Travel : redirected to parent ZRAP_C_TRAVEL_APPR_###,
      _Customer,
      _Carrier
}
```

```cds
@EndUserText.label: 'Access control for ZRAP_C_TRAVEL_APPR_###'
@MappingRole: true
define role ZRAP_C_TRAVEL_APPR_### {
  grant
    select
      on
        ZRAP_C_TRAVEL_APPR_###
          where
            inheriting conditions from entity ZRAP_R_TRAVEL_###;
}
```

```cds
@EndUserText.label: 'Access control for ZRAP_C_BOOKING_APPR_###'
@MappingRole: true
define role ZRAP_C_BOOKING_APPR_### {
  grant
    select
      on
        ZRAP_C_BOOKING_APPR_###
          where
            inheriting conditions from entity ZRAP_R_BOOKING_###;
}
```

MDE(Travel):

```cds
@Metadata.layer: #CORE                                        // (→ 어노테이션 탭: @Metadata.layer)
@UI.headerInfo: { typeName: 'Travel to approve',              // (→ 어노테이션 탭: @UI.headerInfo)
                  typeNamePlural: 'Travels to approve',
                  title: { type: #STANDARD, value: 'TravelID' },
                  description: { value: 'Description' } }
annotate entity ZRAP_C_TRAVEL_APPR_### with
{
  @UI.facet: [ { id: 'Travel', purpose: #STANDARD, type: #IDENTIFICATION_REFERENCE,   // (→ 어노테이션 탭: @UI.facet)
                 label: 'Travel', position: 10 },
               { id: 'Booking', purpose: #STANDARD, type: #LINEITEM_REFERENCE,
                 label: 'Bookings', position: 20, targetElement: '_Booking' } ]
  @UI.lineItem: [ { position: 10, importance: #HIGH },                               // (→ 어노테이션 탭: @UI.lineItem)
                  { type: #FOR_ACTION, dataAction: 'acceptTravel', label: 'Accept' },
                  { type: #FOR_ACTION, dataAction: 'rejectTravel', label: 'Reject' },
                  { type: #FOR_ACTION, dataAction: 'requestRevision', label: 'Request Revision' } ]
  @UI.identification: [ { position: 10 },                                            // (→ 어노테이션 탭: @UI.identification)
                        { type: #FOR_ACTION, dataAction: 'acceptTravel', label: 'Accept' },
                        { type: #FOR_ACTION, dataAction: 'rejectTravel', label: 'Reject' },
                        { type: #FOR_ACTION, dataAction: 'deductDiscount', label: 'Deduct Discount' },
                        { type: #FOR_ACTION, dataAction: 'requestRevision', label: 'Request Revision' } ]
  TravelID;

  @UI.lineItem: [ { position: 20, importance: #HIGH } ]
  @UI.identification: [ { position: 20 } ]
  @UI.selectionField: [ { position: 10 } ]                                           // (→ 어노테이션 탭: @UI.selectionField)
  AgencyID;

  @UI.lineItem: [ { position: 30, importance: #HIGH } ]
  @UI.identification: [ { position: 30 } ]
  @UI.selectionField: [ { position: 20 } ]
  CustomerID;

  @UI.identification: [ { position: 40 } ]
  BeginDate;

  @UI.identification: [ { position: 50 } ]
  EndDate;

  @UI.identification: [ { position: 60 } ]
  BookingFee;

  @UI.lineItem: [ { position: 40, importance: #HIGH } ]
  @UI.identification: [ { position: 70 } ]
  TotalPrice;

  @UI.identification: [ { position: 80 } ]
  Description;

  @UI.lineItem: [ { position: 50, importance: #HIGH } ]
  @UI.identification: [ { position: 90 } ]
  @UI.selectionField: [ { position: 30 } ]
  OverallStatus;

  @UI.hidden: true                                                                   // (→ 어노테이션 탭: @UI.hidden)
  OverallStatusText;

  @UI.hidden: true
  LocalLastChangedAt;

  @UI.hidden: true
  LastChangedAt;
}
```

MDE(Booking):

```cds
@Metadata.layer: #CORE
@UI.headerInfo: { typeName: 'Booking', typeNamePlural: 'Bookings',
                  title: { type: #STANDARD, value: 'BookingID' } }
annotate entity ZRAP_C_BOOKING_APPR_### with
{
  @UI.facet: [ { id: 'Booking', purpose: #STANDARD, type: #IDENTIFICATION_REFERENCE,
                 label: 'Booking', position: 10 } ]
  @UI.lineItem: [ { position: 10 } ]
  @UI.identification: [ { position: 10 } ]
  BookingID;

  @UI.lineItem: [ { position: 20 } ]
  @UI.identification: [ { position: 20 } ]
  CarrierID;

  @UI.lineItem: [ { position: 30 } ]
  @UI.identification: [ { position: 30 } ]
  ConnectionID;

  @UI.lineItem: [ { position: 40 } ]
  @UI.identification: [ { position: 40 } ]
  FlightDate;

  @UI.lineItem: [ { position: 50 } ]
  @UI.identification: [ { position: 50 } ]
  FlightPrice;

  @UI.lineItem: [ { position: 60 } ]
  @UI.identification: [ { position: 60 } ]
  BookingStatus;

  @UI.hidden: true
  LocalLastChangedAt;
}
```

왜 이렇게 쓰나
- 금액 필드의 `@Semantics.amount.currencyCode`는 R 뷰에서 프로젝션으로 전파되므로 다시 쓰지 않았습니다(기존 `ZRAP_C_TRAVEL_###`와 같은 방식).
- **WHERE만으로는 부족합니다.** 트랜잭션 쿼리의 WHERE는 기본적으로 "목록 조회(쿼리)"에만 적용됩니다. 키를 아는 사람이 EML이나 OData로 `TravelID`를 직접 지정해 읽거나 액션을 실행하면, WHERE 밖의 USD Travel에도 닿을 수 있습니다. 이 구멍을 막는 것이 3단계의 `with managed instance filter`입니다(9단계에서 직접 비교합니다).
- DCL과의 차이: DCL은 **사용자 권한**(누가 어떤 행을 볼 수 있나)이고, 프로젝션 WHERE + instance filter는 **앱의 업무 범위**(이 앱은 어떤 행을 다루나)입니다. 둘은 함께 적용됩니다.
- `requestRevision` 버튼은 3단계 BDEF가 생기기 전에는 의미가 없지만, MDE의 `dataAction`은 문자열이라 미리 써 두어도 활성화됩니다.

</details>

#### 3단계. 승인자 프로젝션 BDEF: `use` 고르기, 새 액션·함수, 권한, suppress, instance filter, privileged mode

요구사항
1. `ZRAP_C_TRAVEL_APPR_###`에서 우클릭 → New Behavior Definition으로 프로젝션 BDEF를 만드세요. 프로젝션 자신의 행동 풀 `ZBP_RAP_C_TRAVEL_APPR_###`를 쓴다고 머리에 선언합니다.
2. 머리에 다음을 넣으세요.
   - 프로젝션 WHERE를 EML·OData 요청에도 적용
   - 이 프로젝션 BO를 `PRIVILEGED` EML로 부를 수 있게 허용
   - draft는 노출하지 않음(`use draft` 없음)
3. Travel 행동:
   - ETag 사용
   - `AgencyID`, `CustomerID`, `BeginDate`, `EndDate`, `CurrencyCode`, `Description`은 이 앱에서 읽기 전용
   - `CreatedBy`, `CreatedAt`은 이 프로젝션의 모든 RAP API(파생 타입, EML, OData)에서 아예 제거
   - `use update`, `use action acceptTravel`, `rejectTravel`, `deductDiscount`, `use function GetDefaultsFordeductDiscount`
   - 새 인스턴스 액션 `requestRevision`(입력 `ZRAP_A_REVISION_###`, 결과 `$self` 1건)
   - 새 인스턴스 함수 `getApprovalInfo`(결과 `ZRAP_A_APPR_INFO_###` 1건)
   - 새 액션은 프로젝션 자체의 **전역 권한**으로 제어
   - `_Booking`은 읽기만(생성 불가)
4. Booking 행동: ETag, `_Travel` 연관 읽기만.
5. 아직 행동 풀이 없으므로 ADT Quick Fix(BDEF 첫 줄의 클래스 이름에 Ctrl+1)로 행동 풀을 생성만 해 두세요. 구현은 4단계에서 합니다.

**확인**
- BDEF가 활성화됩니다(행동 풀 생성 후). 활성화가 안 되는 줄이 있으면 정답 해설의 "확인 필요" 항목을 보세요.
- 행동 풀 `ZBP_RAP_C_TRAVEL_APPR_###`의 Local Types에 `requestRevision`, `getApprovalInfo`, `get_global_authorizations` 메서드 선언이 생성됩니다.

<details><summary>정답·해설</summary>

```bdef
projection implementation in class zbp_rap_c_travel_appr_### unique;  // 프로젝션 전용 행동 풀(새 액션·함수·권한 구현용)
strict ( 2 );
with managed instance filter;   // 프로젝션 뷰의 WHERE를 EML·OData(키 접근, 액션)에도 적용
with privileged mode;           // 이 프로젝션 BO를 PRIVILEGED EML로 호출 허용 (실제 시스템에서 확인 필요)

define behavior for ZRAP_C_TRAVEL_APPR_### alias TravelAppr
use etag
authorization master ( global )  // 프로젝션에서 새로 정의한 액션·함수용 권한 (실제 시스템에서 확인 필요)
{
  // 이 앱에서만 읽기 전용 (기본 BO보다 더 좁힐 수만 있음)
  field ( readonly ) AgencyID, CustomerID, BeginDate, EndDate, CurrencyCode, Description;

  // 파생 타입·EML·OData에서 완전히 제거
  field ( suppress ) CreatedBy, CreatedAt;

  // 기본 BO에서 골라 쓰는 연산 (create, delete 없음)
  use update;

  use action acceptTravel;
  use action rejectTravel;
  use action deductDiscount;
  use function GetDefaultsFordeductDiscount;

  // 프로젝션에서 새로 정의하는 액션·함수 → 프로젝션 행동 풀에서 구현
  action requestRevision parameter ZRAP_A_REVISION_### result [1] $self;
  function getApprovalInfo result [1] ZRAP_A_APPR_INFO_###;

  use association _Booking;        // 읽기만 (create 없음)
}

define behavior for ZRAP_C_BOOKING_APPR_### alias BookingAppr
use etag
{
  use association _Travel;
}
```

행동 풀 전역 클래스(Quick Fix가 만들어 주는 모양):

```abap
CLASS zbp_rap_c_travel_appr_### DEFINITION PUBLIC ABSTRACT FINAL FOR BEHAVIOR OF zrap_c_travel_appr_###.
ENDCLASS.

CLASS zbp_rap_c_travel_appr_### IMPLEMENTATION.
ENDCLASS.
```

해설: 줄마다 근거와 의미
- `projection implementation in class ... unique;` — 프로젝션 BDEF도 자기 행동 풀을 가질 수 있습니다. 참조 시나리오 `/DMO/C_Supplement`(augment 구현), `/DMO/C_TravelTP_CD`, SAP 샘플 `abap-partner-reference-application`의 `ZPRA_MF_C_MusicFestivalTP`가 이 머리를 씁니다. 엔터티별로 `define behavior for ... implementation in class ... unique`로 쓸 수도 있습니다(커뮤니티 예제 `ZC_PRU_UNUM_ORDER_PROJ`).
- `with managed instance filter;` — 릴리스 7.93. "프로젝션 BDEF와 인터페이스 BDEF에서 쓸 수 있고, 지정하면 CDS 트랜잭션 쿼리/인터페이스의 WHERE 조건을 ABAP EML과 OData 요청에서도 평가한다"(33 Release News). 위치는 머리, `strict` 다음(커뮤니티 예제 두 곳에서 같은 위치 확인). WHERE가 없는 뷰에 쓰면 의미가 없습니다.
- `with privileged mode;` — 릴리스 7.85 "BDEF Privileged Mode for RAP Projection BOs: a new syntax variant of with privileged mode". 로컬 예제에서는 인터페이스 BDEF `/DMO/I_Travel_D`의 `with privileged mode;`만 확인했고, 프로젝션도 같은 형태라고 보고 썼습니다(실제 시스템에서 확인 필요). 기본 BO의 `with privileged mode disabling NoCheckWhenPrivileged`가 실제로 무엇을 끌지 정하고, 프로젝션·인터페이스는 "소비자가 PRIVILEGED를 붙여도 된다"는 허용만 합니다.
- `authorization master ( global )` — 7.84 "Projection BDEF, Authorization Concept: 프로젝션 BDEF에서 새로 정의한 액션·함수의 접근을 제어하는 권한 개념을 정의할 수 있다". 정확한 키워드를 로컬·GitHub 예제에서 찾지 못했습니다(실제 시스템에서 확인 필요). 이 줄에서 오류가 나면 F1로 "projection BDEF authorization"을 확인하고, 그래도 안 되면 이 줄을 지우고 4단계의 전역 권한 메서드 대신 `requestRevision` 구현 첫 부분에서 같은 검사를 하세요(실패 시 `%fail-cause = if_abap_behv=>cause-unauthorized`). 재사용(`use`)한 연산의 권한은 언제나 기본 BO가 검사합니다. 프로젝션 권한은 **새 연산에만** 적용됩니다.
- `field ( readonly )` — 프로젝션은 기본 BO의 필드 제어를 **더 엄격하게만** 할 수 있습니다(참조 시나리오 승인자 `field ( readonly ) BeginDate, EndDate, TotalPrice, CustomerID;`). 기본 BO에서 읽기 전용인 필드를 프로젝션에서 수정 가능하게 바꿀 수는 없습니다.
- `field ( suppress )` — 7.84. "필드를 BDEF 파생 타입과 모든 RAP API에서 제거"(36 BDL 치트시트, 33 Release News). CDS 뷰에는 필드가 남아 있어 Data Preview에는 보이지만, `TYPE TABLE FOR ... zrap_c_travel_appr_###`에는 `CreatedBy`가 없고, EML에서 `FIELDS ( CreatedBy )`라고 쓰면 구문 오류가 납니다(11단계 RTTS로 확인). 키, ETag 필드처럼 BO가 꼭 써야 하는 필드에는 쓰지 마세요. OData 메타데이터에서도 사라지는지는 확인하지 못했습니다(실제 시스템에서 확인 필요).
- `action requestRevision ...` / `function getApprovalInfo ...` — `use` 없이 쓰면 **프로젝션 전용** 연산입니다(7.84). 기본 BO에는 없고, 다른 프로젝션(기존 앱, 처리자)에서도 보이지 않습니다. 커뮤니티 예제 `Zpru_PurcOrderHdr_ODATA_Proj`의 `action sendToIDOC parameter ...;`, `static function calculateOpenOrderValue ...`와 같은 형태입니다.
- `use association _Booking;` — 중괄호 없이 쓰면 읽기(연관 따라가기)만 됩니다(참조 시나리오 `use association _Travel;`). 생성까지 허용하려면 `{ create; }`.
- **인터페이스 BDEF에도 같은 문법**: `with managed instance filter`와 재정의 파라미터(`deep parameter`/`deep result`)는 Release News상 프로젝션 BDEF와 인터페이스 BDEF 모두에 쓸 수 있고, `field ( suppress )`는 Release News에 managed·unmanaged·프로젝션 BDEF로 적혀 있으며 인터페이스 BDEF 사용은 커뮤니티 예제로만 확인했습니다. 커뮤니티 예제의 인터페이스 BDEF `Zpru_PurcOrderHdr_ODATA_Int`는 `interface; extensible; with managed instance filter; use draft;` 머리와 `field ( suppress ) controlTimestamp;`를 씁니다. R-03의 `ZRAP_I_TRAVEL_###`에 적용하면 "API 소비자에게는 내부 관리 필드를 아예 보이지 않게" 하는 계약을 만들 수 있습니다. 단, 인터페이스 BDEF에는 새 액션·함수·augment를 정의할 수 없습니다(인터페이스는 `use`로 고르기만 함, R-03 9단계).
- draft BO 위의 draft 없는 프로젝션: `/DMO/C_Travel_A_D`가 바로 이 형태입니다. 이 프로젝션으로 하는 수정은 활성 인스턴스에 바로 적용되고, 같은 Travel에 다른 사용자의 draft가 있으면 잠금 충돌이 납니다.

클래스 구조 해설
- 프로젝션 BDEF의 `use ...` 줄은 **행동 풀 메서드를 만들지 않습니다.** 프레임워크가 요청을 기본 BO로 그대로 넘기고, 기본 BO의 핸들러가 실행됩니다.
- 새 액션·함수·권한 줄만 프로젝션 행동 풀에 메서드를 요구합니다(`FOR MODIFY ... FOR ACTION TravelAppr~requestRevision`, `FOR READ ... FOR FUNCTION TravelAppr~getApprovalInfo`, `FOR GLOBAL AUTHORIZATION`). 파생 타입 이름에는 프로젝션 엔터티(`TravelAppr`)가 들어갑니다.

</details>

#### 4단계. 승인자 행동 풀: 새 액션·함수·권한 구현과 FORWARDING PRIVILEGED

요구사항
1. `lhc_travelappr` 핸들러 클래스를 완성하세요. 상수 `travel_status`(O/A/X)와, 실습용 상수 `c_revision_allowed`(abap_true면 허용)를 둡니다.
2. `get_global_authorizations`: `requestRevision`이 요청되었을 때 `c_revision_allowed`에 따라 허용/거부를 돌려줍니다. 거부일 때 메시지 173을 `reported`에 넣습니다.
3. `requestRevision`:
   - 기본 BO `ZRAP_R_TRAVEL_###`에서 대상 Travel의 `OverallStatus`, `Description`을 읽습니다. 이때 **호출자가 privileged로 불렀으면 그 특권을 그대로 이어받도록** 합니다.
   - 상태가 O가 아니면 `failed`(원인 `cause-disabled`)와 메시지 171(`%element-OverallStatus`)을 넣습니다.
   - O이면 기본 BO에 `Description = |[REVISION] { 사유 } { 기존 설명 }|`(최대 길이에서 잘림)을 UPDATE합니다. 이것도 특권을 이어받습니다.
   - 기본 BO의 `failed`/`reported`를 프로젝션의 `failed-travelappr`/`reported-travelappr`로 옮깁니다(키와 원인, 메시지).
   - 성공한 Travel은 성공 메시지 170을 넣고, 기본 BO를 다시 읽어 `result`(`%param` = 프로젝션 인스턴스)를 채웁니다.
4. `getApprovalInfo`: 기본 BO에서 Travel(`BeginDate`, `TotalPrice`, `CurrencyCode`)과 Booking(`_Booking`의 `BookingID`)을 **한 번씩** 읽고, Travel마다 결과를 만듭니다.
   - `days_to_start` = 시작일 − 오늘(`cl_abap_context_info=>get_system_date( )`)
   - `recommendation`: 금액 5000 초과면 `Check budget`, 아니고 7일 미만이면 `Urgent - decide today`, 아니면 `OK`
   - 없는 Travel은 `failed`(원인 `cause-not_found`)
5. 두 메서드 모두 처음에 `cl_abap_behv_aux=>get_current_context`의 `privileged`, `from_projection` 값을 추적 클래스에 기록하세요(`gv_trace_on`일 때만).

**확인**
- 행동 풀이 활성화됩니다. 동작 확인은 9단계 콘솔에서 합니다.

<details><summary>정답·해설</summary>

Local Types(`ZBP_RAP_C_TRAVEL_APPR_###` → Local Types 탭) 전체:

```abap
CLASS lhc_travelappr DEFINITION INHERITING FROM cl_abap_behavior_handler.
  PRIVATE SECTION.

    CONSTANTS:
      BEGIN OF travel_status,
        open     TYPE c LENGTH 1 VALUE 'O',
        accepted TYPE c LENGTH 1 VALUE 'A',
        rejected TYPE c LENGTH 1 VALUE 'X',
      END OF travel_status.

    "trial switch: set to abap_false and activate to see the projection authorization deny the action
    CONSTANTS c_revision_allowed TYPE abap_boolean VALUE abap_true.

    "from: authorization master ( global )  (projection BDEF)
    METHODS get_global_authorizations FOR GLOBAL AUTHORIZATION
      IMPORTING REQUEST requested_authorizations FOR TravelAppr RESULT result.

    "from: action requestRevision parameter ZRAP_A_REVISION_### result [1] $self;
    METHODS requestRevision FOR MODIFY
      IMPORTING keys FOR ACTION TravelAppr~requestRevision RESULT result.

    "from: function getApprovalInfo result [1] ZRAP_A_APPR_INFO_###;
    METHODS getApprovalInfo FOR READ
      IMPORTING keys FOR FUNCTION TravelAppr~getApprovalInfo RESULT result.

    METHODS trace_context
      IMPORTING iv_method TYPE string.

ENDCLASS.


CLASS lhc_travelappr IMPLEMENTATION.

  METHOD trace_context.
    CHECK zcl_rap_r17_trace_###=>gv_trace_on = abap_true.
    cl_abap_behv_aux=>get_current_context( IMPORTING privileged      = FINAL(priv)
                                                     from_projection = FINAL(fr_proj)
                                                     from_interface  = FINAL(fr_int)
                                                     in_local_mode   = FINAL(loc_mode) ).
    zcl_rap_r17_trace_###=>add( |[APPR { iv_method }] privileged={ priv } from_projection={ fr_proj } | &&
                                |from_interface={ fr_int } in_local_mode={ loc_mode }| ).
  ENDMETHOD.


  METHOD get_global_authorizations.
    IF requested_authorizations-%action-requestRevision = if_abap_behv=>mk-on.
      IF c_revision_allowed = abap_true.
        result-%action-requestRevision = if_abap_behv=>auth-allowed.
      ELSE.
        result-%action-requestRevision = if_abap_behv=>auth-unauthorized.
        APPEND VALUE #( %msg    = NEW zcm_rap_###( textid   = zcm_rap_###=>revision_not_allowed
                                                   severity = if_abap_behv_message=>severity-error )
                        %global = if_abap_behv=>mk-on ) TO reported-travelappr.
      ENDIF.
    ENDIF.
  ENDMETHOD.


  METHOD requestRevision.
    DATA travel_update TYPE TABLE FOR UPDATE zrap_r_travel_###\\Travel.
    DATA ok_keys       TYPE TABLE FOR READ IMPORT zrap_r_travel_###\\Travel.

    trace_context( `requestRevision` ).

    "(1) read the base BO - FORWARDING PRIVILEGED: privileged only if our caller was privileged
    READ ENTITIES OF zrap_r_travel_### FORWARDING PRIVILEGED
      ENTITY Travel
        FIELDS ( OverallStatus Description )
        WITH VALUE #( FOR k IN keys ( %tky = CORRESPONDING #( k-%tky ) ) )
      RESULT DATA(travels)
      FAILED DATA(read_failed).

    LOOP AT read_failed-travel INTO DATA(rf).
      APPEND VALUE #( %tky        = CORRESPONDING #( rf-%tky )
                      %fail-cause = rf-%fail-cause ) TO failed-travelappr.
    ENDLOOP.

    "(2) check status, build the base update
    LOOP AT keys INTO DATA(key).
      LOOP AT travels INTO DATA(travel) WHERE TravelID = key-TravelID.
        IF travel-OverallStatus <> travel_status-open.
          APPEND VALUE #( %tky        = key-%tky
                          %fail-cause = if_abap_behv=>cause-disabled ) TO failed-travelappr.
          APPEND VALUE #( %tky                   = key-%tky
                          %msg                   = NEW zcm_rap_###( textid    = zcm_rap_###=>revision_not_open
                                                                    severity  = if_abap_behv_message=>severity-error
                                                                    travel_id = key-TravelID )
                          %element-OverallStatus = if_abap_behv=>mk-on ) TO reported-travelappr.
        ELSE.
          APPEND VALUE #( %tky                 = travel-%tky
                          Description          = |[REVISION] { key-%param-revision_note } { travel-Description }|
                          %control-Description = if_abap_behv=>mk-on ) TO travel_update.
        ENDIF.
      ENDLOOP.
    ENDLOOP.

    IF travel_update IS INITIAL.
      RETURN.
    ENDIF.

    "(3) modify the base BO - again forwarding the caller's privileged context
    MODIFY ENTITIES OF zrap_r_travel_### FORWARDING PRIVILEGED
      ENTITY Travel
        UPDATE FROM travel_update
      FAILED DATA(upd_failed)
      REPORTED DATA(upd_reported).

    "(4) map base responses to the projection responses
    LOOP AT upd_failed-travel INTO DATA(uf).
      APPEND VALUE #( %tky        = CORRESPONDING #( uf-%tky )
                      %fail-cause = uf-%fail-cause ) TO failed-travelappr.
    ENDLOOP.
    LOOP AT upd_reported-travel INTO DATA(ur).
      APPEND VALUE #( %tky = CORRESPONDING #( ur-%tky )
                      %msg = ur-%msg ) TO reported-travelappr.
    ENDLOOP.

    "(5) success messages + result for the instances that were really updated
    LOOP AT travel_update INTO DATA(upd).
      CHECK NOT line_exists( upd_failed-travel[ TravelID = upd-TravelID ] ).
      APPEND VALUE #( %tky = upd-%tky ) TO ok_keys.
      APPEND VALUE #( %tky = CORRESPONDING #( upd-%tky )
                      %msg = NEW zcm_rap_###( textid    = zcm_rap_###=>revision_requested
                                              severity  = if_abap_behv_message=>severity-success
                                              travel_id = upd-TravelID
                                              note      = keys[ TravelID = upd-TravelID ]-%param-revision_note ) )
             TO reported-travelappr.
    ENDLOOP.

    IF ok_keys IS INITIAL.
      RETURN.
    ENDIF.

    READ ENTITIES OF zrap_r_travel_### FORWARDING PRIVILEGED
      ENTITY Travel
        ALL FIELDS WITH ok_keys            "result $self needs the complete projection instance
      RESULT DATA(updated).

    result = VALUE #( FOR u IN updated ( %tky   = CORRESPONDING #( u-%tky )
                                         %param = CORRESPONDING #( u ) ) ).

    "--- 11단계 계약 검사 실험용 블록 (11단계에서 추가) ---
  ENDMETHOD.


  METHOD getApprovalInfo.
    trace_context( `getApprovalInfo` ).

    DATA(today) = cl_abap_context_info=>get_system_date( ).

    READ ENTITIES OF zrap_r_travel_### FORWARDING PRIVILEGED
      ENTITY Travel
        FIELDS ( BeginDate TotalPrice CurrencyCode )
        WITH VALUE #( FOR k IN keys ( %tky = CORRESPONDING #( k-%tky ) ) )
        RESULT DATA(travels)
      ENTITY Travel BY \_Booking
        FIELDS ( BookingID )
        WITH VALUE #( FOR k IN keys ( %tky = CORRESPONDING #( k-%tky ) ) )
        RESULT DATA(bookings)
      FAILED DATA(read_failed).

    LOOP AT read_failed-travel INTO DATA(rf).
      APPEND VALUE #( %tky        = CORRESPONDING #( rf-%tky )
                      %fail-cause = if_abap_behv=>cause-not_found ) TO failed-travelappr.
    ENDLOOP.

    LOOP AT keys INTO DATA(key).
      LOOP AT travels INTO DATA(travel) WHERE TravelID = key-TravelID.
        DATA(days) = CONV i( travel-BeginDate - today ).
        APPEND VALUE #( %tky   = key-%tky
                        %param = VALUE #( travel_id      = travel-TravelID
                                          days_to_start  = days
                                          booking_count  = REDUCE i( INIT n = 0
                                                                     FOR b IN bookings WHERE ( TravelID = travel-TravelID )
                                                                     NEXT n = n + 1 )
                                          total_price    = travel-TotalPrice
                                          currency_code  = travel-CurrencyCode
                                          recommendation = COND #( WHEN travel-TotalPrice > 5000 THEN 'Check budget'
                                                                   WHEN days < 7                 THEN 'Urgent - decide today'
                                                                   ELSE 'OK' ) ) )
               TO result.
      ENDLOOP.
    ENDLOOP.
  ENDMETHOD.

ENDCLASS.
```

왜 이렇게 쓰나
- **프로젝션 행동 풀은 기본 BO의 소비자입니다.** 기본 BO의 버퍼·핸들러에 직접 손댈 수 없고 EML로 부탁합니다. 그래서 `IN LOCAL MODE`를 쓰지 않고(기본 BO의 권한·기능 제어가 그대로 적용되어야 함), 기본 BO의 `failed`/`reported`를 자기 응답으로 옮겨 줍니다. 커뮤니티 예제 `ZBP_PRU_PURCORDERHDR_ODATA_PRO`의 `sendToIDOC`, `calculateOpenOrderValue`도 `READ ENTITIES OF <기본 BO>`로 구현합니다.
- **FORWARDING PRIVILEGED**(9.12): "READ, MODIFY, GET PERMISSIONS에서 privileged 문맥을 이어지는 EML 요청에 넘긴다". 위치는 `IN LOCAL MODE`와 같은 자리(`READ ENTITIES OF bdef FORWARDING PRIVILEGED ENTITY ...`, 커뮤니티 EML 템플릿·실사용 코드에서 확인).
  - 콘솔이 `MODIFY ENTITIES OF zrap_c_travel_appr_### PRIVILEGED ...`로 부르면 → 이 핸들러 안의 기본 BO 호출도 privileged → R-03의 `deny_country` 시뮬레이션(권한 컨텍스트 `NoCheckWhenPrivileged`)이 꺼집니다.
  - 콘솔이 그냥 부르면 → 기본 BO 호출도 일반 호출 → 권한 검사가 그대로.
  - 여기서 `PRIVILEGED`(FORWARDING 없이)를 쓰면 **누가 부르든 항상 권한을 우회**하게 되어, 승인자 앱 사용자가 권한 없는 Travel까지 고칠 수 있는 구멍이 생깁니다. 이것이 FORWARDING이 생긴 이유입니다.
- `%tky = CORRESPONDING #( k-%tky )`: 승인자 프로젝션은 draft가 없어서 `%tky`에 `%is_draft`가 없고, 기본 BO(draft)의 `%tky`에는 있습니다. `CORRESPONDING`이 이름이 같은 `%pid`, `TravelID`만 옮기고 `%is_draft`는 초기값(= `if_abap_behv=>mk-off`, 활성 인스턴스)으로 둡니다. 반대 방향(기본 → 프로젝션)도 같은 원리입니다(참조 시나리오 `/DMO/BP_C_SUPPLEMENT`가 같은 방식으로 `%tky`를 옮김).
- `requestRevision`의 결과는 `result [1] $self`이므로 프로젝션 인스턴스 전체를 돌려줘야 합니다. 그래서 마지막 읽기만 `ALL FIELDS`를 썼습니다. suppress한 `CreatedBy`, `CreatedAt`은 프로젝션 결과 타입에 없으므로 `CORRESPONDING`이 알아서 빼 줍니다.
- 루프 안 EML/SELECT 없이, 읽기 1회 → 메모리에서 판정 → 수정 1회 → 결과 읽기 1회로 구성했습니다.
- 결과 행을 키로 찾을 때 `LOOP ... WHERE`를 썼습니다. 파생 타입 표는 기본 키가 비어 있어 `travels[ TravelID = ... ]` 같은 표 식은 "보조 키를 명시하라"는 구문 경고가 납니다(08 치트시트). 11단계에서 보조 키를 직접 다룹니다.

자주 나는 오류와 해결
- `zrap_r_travel_###\\Travel`의 백슬래시는 두 개입니다(BDEF 이름\\엔터티 별칭).
- `note = keys[ TravelID = ... ]`에서 구문 경고가 나면 `VALUE #( keys[ KEY entity TravelID = upd-TravelID ]-%param-revision_note OPTIONAL )`처럼 `KEY entity`를 붙이세요. 액션 import 표에 `entity` 키가 있는지는 F2로 확인하세요.
- `get_current_context`의 IMPORTING 파라미터 이름은 08/22 치트시트 예제 그대로입니다. 시스템 릴리스에 따라 일부 파라미터가 없으면 그 줄만 빼세요.

클래스 구조 해설
- `FOR GLOBAL AUTHORIZATION ... RESULT result`: `result-%action-requestRevision`처럼 **프로젝션에서 새로 만든 연산만** 컴포넌트로 가집니다. `%update`, `%action-acceptTravel`은 기본 BO의 권한 메서드가 담당합니다.
- `FOR MODIFY ... FOR ACTION TravelAppr~requestRevision RESULT result`: `keys`는 `TYPE TABLE FOR ACTION IMPORT zrap_c_travel_appr_###~requestRevision`, `%param`은 `ZRAP_A_REVISION_###` 구조. 액션이 실행될 때(Fiori 버튼, EML `EXECUTE`) 호출됩니다.
- `FOR READ ... FOR FUNCTION`: 함수는 읽기 연산이라 `FOR READ`입니다. 데이터를 바꾸면 안 됩니다.

</details>

#### 5단계. (선택) 재정의 파라미터: 프로젝션 전용 `deep parameter`

이 단계는 선택입니다. 기본 BO의 액션 파라미터 구조를 바꿔야 하고, 확인하지 못한 부분이 있어 실패하면 되돌리세요(되돌리는 방법은 정답 끝에 있습니다).

요구사항
1. 승인자 화면에서는 `deductDiscount`의 입력 필드 이름을 `discount_percent` 대신 `ApproverDiscount`로 보이게 하고 싶습니다. 기본 BO의 액션은 그대로 두고, **승인자 프로젝션에서만** 파라미터 구조를 바꾸세요.
2. 프로젝션 전용 구조 `ZRAP_A_DISCOUNT_APPR_###`(root 추상 엔터티, 필드 `ApproverDiscount` int1)를 만들고, 추상 BDEF(계층 지원)로 기본 파라미터 구조와 필드를 서로 매핑하세요.
3. 매핑이 되려면 기본 파라미터 `ZRAP_A_DISCOUNT_###`도 root 추상 엔터티 + 추상 BDEF(반대 방향 매핑)여야 합니다. `define abstract entity`를 `define root abstract entity`로 바꾸고 추상 BDEF를 만드세요.
4. 승인자 BDEF의 `use action deductDiscount;` 줄을 재정의 파라미터를 쓰는 형태로 바꾸세요.

**직접 추가할 어노테이션**
- `@EndUserText.label` — 추상 엔터티 설명과 팝업 라벨

**확인**
- 네 객체(추상 엔터티 2개, 추상 BDEF 2개)와 승인자 BDEF가 활성화됩니다. 기본 BO `ZRAP_R_TRAVEL_###`와 기존 앱이 그대로 활성 상태인지(빨간 표시 없음) Project Explorer에서 확인하세요.
- 9단계 콘솔에서 `TYPE TABLE FOR ACTION IMPORT zrap_c_travel_appr_###~deductDiscount`의 `%param`에 `ApproverDiscount`가 있는지 F2로 확인합니다.

<details><summary>정답·해설</summary>

```cds
@EndUserText.label: 'Parameter: discount (base)'
define root abstract entity ZRAP_A_DISCOUNT_###      // root 로 변경 (추상 BDEF 를 붙이기 위해)
{
  @EndUserText.label: 'Discount (%)'
  discount_percent : abap.int1;
}
```

```bdef
abstract;
strict ( 2 );
with hierarchy;                                      // deep parameter 로 쓰려면 계층 추상 BDEF 필요

define behavior for ZRAP_A_DISCOUNT_### alias Discount
{
  deep mapping for ZRAP_A_DISCOUNT_APPR_### corresponding   // 프로젝션 구조 → 기본 구조
  {
    discount_percent = ApproverDiscount;
  }
}
```

```cds
@EndUserText.label: 'Parameter: discount (approver)'
define root abstract entity ZRAP_A_DISCOUNT_APPR_###
{
  @EndUserText.label: 'Approver discount (%)'
  ApproverDiscount : abap.int1;
}
```

```bdef
abstract;
strict ( 2 );
with hierarchy;

define behavior for ZRAP_A_DISCOUNT_APPR_### alias DiscountAppr
{
  deep mapping for ZRAP_A_DISCOUNT_### corresponding        // 기본 구조 → 프로젝션 구조
  {
    ApproverDiscount = discount_percent;
  }
}
```

승인자 BDEF에서 바꿀 줄:

```bdef
  use action deductDiscount deep parameter ZRAP_A_DISCOUNT_APPR_###;   // 프로젝션 전용 입력 구조 (실제 시스템에서 확인 필요)
  use function GetDefaultsFordeductDiscount;
```

해설
- 7.93 Release News: "프로젝션 BDEF나 인터페이스 BDEF에서 재사용한 액션·함수·비즈니스 이벤트의 입력/출력 파라미터를 `deep parameter` 또는 `deep result`로 자기만의 구조로 바꿀 수 있다". 함수 결과를 바꾸면 `use function f deep result <구조>;`입니다.
- 형태의 근거는 커뮤니티 예제(`abap-rap-example`)입니다: 인터페이스·프로젝션 BDEF의 `use action ( precheck ) ChangeStatus deep parameter Zpru_D_New_Status_Redefine1;`, `use function getStatusHistory deep result ZPRU_D_HistoryRoot_Redefine1;`, 그리고 두 추상 BDEF(`abstract; strict ( 2 ); with hierarchy;`)가 서로 `deep mapping for ... corresponding { 대상필드 = 원본필드; }`를 가지는 구조. 그 예제는 `extensible`이라 `corresponding extensible`을 썼고, 여기서는 확장 불필요라 `corresponding`만 썼습니다.
- 확인하지 못한 점: (1) 그 예제는 기본 BO 액션도 `deep parameter`로 정의되어 있습니다. 우리 기본 BO는 평면 `parameter ZRAP_A_DISCOUNT_###`인데, 평면 파라미터를 프로젝션에서 `deep parameter`로 재정의할 수 있는지 확인하지 못했습니다. (2) 기본 액션에 붙은 `default function GetDefaultsFordeductDiscount`의 결과 타입이 재정의 구조를 따라가는지 모릅니다. 활성화 오류가 나면 승인자 BDEF에서 `use function GetDefaultsFordeductDiscount;`를 먼저 빼 보세요(실제 시스템에서 확인 필요).
- 되돌리기: 승인자 BDEF를 `use action deductDiscount;`로 되돌리고, 두 추상 BDEF와 `ZRAP_A_DISCOUNT_APPR_###`를 삭제한 뒤, `ZRAP_A_DISCOUNT_###`를 `define abstract entity`로 되돌려 기본 BO와 함께 활성화하세요.
- 언제 쓰나: 같은 기본 액션을 API(인터페이스 BO)에는 안정된 이름으로, UI(프로젝션)에는 화면 친화적 이름·구조로 내보내고 싶을 때. 기본 BO 코드를 건드리지 않고 매핑만으로 해결합니다.

</details>

#### 6단계. 처리자 프로젝션 뷰: 가상 요소 `ShortNote`

요구사항
1. `ZRAP_C_TRAVEL_PROC_###`(root, 트랜잭션 쿼리 프로젝션, WHERE 없음)를 만드세요. 필드는 기존 `ZRAP_C_TRAVEL_###`와 같되 첨부 필드와 `OverallStatusCriticality`는 빼고, 가상 요소 `ShortNote`(char 20, 라벨 "Short note")를 추가합니다.
2. `ShortNote` 계산 클래스 `ZCL_RAP_R17_VE_###`를 만드세요. 읽을 때 `Description`에서 앞의 `[P] `를 뗀 값을 넣습니다(20자에서 잘림). 계산에 필요한 원래 필드는 `DESCRIPTION`입니다.
3. `ZRAP_C_BOOKING_PROC_###`를 만드세요(승인자 Booking과 같은 필드, `_Travel`은 처리자 Travel로 재지정).
4. 두 뷰의 DCL과 MDE를 만드세요. Travel 목록: Travel ID, Agency, Customer, Begin/End Date, Total Price, Status. 상세: 모든 입력 필드 + Short note + Booking 표. 액션 버튼은 두지 않습니다.

**직접 추가할 어노테이션**
- `@ObjectModel.virtualElementCalculatedBy` — 가상 요소를 계산할 ABAP 클래스
- `@EndUserText.label` — 가상 요소 라벨
- `@Consumption.valueHelpDefinition` (+ `useForValidation`) — 입력 필드 F4와 입력값 검증
- `@ObjectModel.text.element`, `@Search.*`, `@AccessControl.authorizationCheck`, `@Metadata.allowExtensions`, `@ObjectModel.semanticKey`
- MDE: `@Metadata.layer`, `@UI.headerInfo`, `@UI.facet`, `@UI.lineItem`, `@UI.identification`, `@UI.selectionField`, `@UI.hidden`

**확인**
- 뷰·클래스·DCL·MDE가 활성화됩니다.
- Data Preview에서는 가상 요소가 계산되지 않습니다(SADL을 거치지 않음). `ShortNote` 값은 8단계 Fiori 미리보기에서 확인합니다.

<details><summary>정답·해설</summary>

```cds
@AccessControl.authorizationCheck: #CHECK
@Metadata.allowExtensions: true
@EndUserText.label: 'Travel - processor projection'
@ObjectModel.semanticKey: [ 'TravelID' ]
@Search.searchable: true
define root view entity ZRAP_C_TRAVEL_PROC_###
  provider contract transactional_query
  as projection on ZRAP_R_TRAVEL_###
{
      @Search.defaultSearchElement: true
  key TravelID,

      @Consumption.valueHelpDefinition: [ { entity: { name: '/DMO/I_Agency_StdVH', element: 'AgencyID' },
                                            useForValidation: true } ]      // (→ 어노테이션 탭: @Consumption.valueHelpDefinition.useForValidation)
      @ObjectModel.text.element: [ 'AgencyName' ]
      AgencyID,
      _Agency.Name              as AgencyName,

      @Search.defaultSearchElement: true
      @Consumption.valueHelpDefinition: [ { entity: { name: '/DMO/I_Customer_StdVH', element: 'CustomerID' },
                                            useForValidation: true } ]
      @ObjectModel.text.element: [ 'CustomerName' ]
      CustomerID,
      _Customer.LastName        as CustomerName,

      BeginDate,
      EndDate,
      BookingFee,
      TotalPrice,

      @Consumption.valueHelpDefinition: [ { entity: { name: 'I_CurrencyStdVH', element: 'Currency' },
                                            useForValidation: true } ]
      CurrencyCode,

      Description,

      @ObjectModel.virtualElementCalculatedBy: 'ABAP:ZCL_RAP_R17_VE_###'  // 읽을 때 계산 (→ 어노테이션 탭: @ObjectModel.virtualElementCalculatedBy)
      @EndUserText.label: 'Short note'
      virtual ShortNote : abap.char(20),                                   // 프로젝션에만 있는 필드 → 7단계에서 augment 로 기본 BO에 반영

      @Consumption.valueHelpDefinition: [ { entity: { name: '/DMO/I_Overall_Status_VH', element: 'OverallStatus' } } ]
      @ObjectModel.text.element: [ 'OverallStatusText' ]
      OverallStatus,
      _OverallStatus._Text.Text as OverallStatusText : localized,

      CreatedBy,
      CreatedAt,
      LocalLastChangedBy,
      LocalLastChangedAt,
      LastChangedAt,

      /* Associations */
      _Booking : redirected to composition child ZRAP_C_BOOKING_PROC_###,
      _Agency,
      _Customer,
      _OverallStatus,
      _Currency
}
```

```cds
@AccessControl.authorizationCheck: #CHECK
@Metadata.allowExtensions: true
@EndUserText.label: 'Booking - processor projection'
@ObjectModel.semanticKey: [ 'BookingID' ]
define view entity ZRAP_C_BOOKING_PROC_###
  as projection on ZRAP_R_BOOKING_###
{
  key TravelID,
  key BookingID,
      BookingDate,
      @Consumption.valueHelpDefinition: [ { entity: { name: '/DMO/I_Customer_StdVH', element: 'CustomerID' },
                                            useForValidation: true } ]
      CustomerID,
      @Consumption.valueHelpDefinition: [ { entity: { name: '/DMO/I_Flight_StdVH', element: 'AirlineID' },
                                            additionalBinding: [ { localElement: 'ConnectionID', element: 'ConnectionID' },
                                                                 { localElement: 'FlightDate',   element: 'FlightDate' },
                                                                 { localElement: 'FlightPrice',  element: 'Price' },
                                                                 { localElement: 'CurrencyCode', element: 'CurrencyCode' } ] } ]
      CarrierID,
      ConnectionID,
      FlightDate,
      FlightPrice,
      CurrencyCode,
      BookingStatus,
      LocalLastChangedAt,

      /* Associations */
      _Travel : redirected to parent ZRAP_C_TRAVEL_PROC_###,
      _Customer,
      _Carrier
}
```

```cds
@EndUserText.label: 'Access control for ZRAP_C_TRAVEL_PROC_###'
@MappingRole: true
define role ZRAP_C_TRAVEL_PROC_### {
  grant
    select
      on
        ZRAP_C_TRAVEL_PROC_###
          where
            inheriting conditions from entity ZRAP_R_TRAVEL_###;
}
```

```cds
@EndUserText.label: 'Access control for ZRAP_C_BOOKING_PROC_###'
@MappingRole: true
define role ZRAP_C_BOOKING_PROC_### {
  grant
    select
      on
        ZRAP_C_BOOKING_PROC_###
          where
            inheriting conditions from entity ZRAP_R_BOOKING_###;
}
```

MDE(Travel):

```cds
@Metadata.layer: #CORE
@UI.headerInfo: { typeName: 'Travel', typeNamePlural: 'Travels (processor)',
                  title: { type: #STANDARD, value: 'TravelID' },
                  description: { value: 'Description' } }
annotate entity ZRAP_C_TRAVEL_PROC_### with
{
  @UI.facet: [ { id: 'Travel', purpose: #STANDARD, type: #IDENTIFICATION_REFERENCE,
                 label: 'Travel', position: 10 },
               { id: 'Booking', purpose: #STANDARD, type: #LINEITEM_REFERENCE,
                 label: 'Bookings', position: 20, targetElement: '_Booking' } ]
  @UI.lineItem: [ { position: 10, importance: #HIGH } ]
  @UI.identification: [ { position: 10 } ]
  TravelID;

  @UI.lineItem: [ { position: 20, importance: #HIGH } ]
  @UI.identification: [ { position: 20 } ]
  @UI.selectionField: [ { position: 10 } ]
  AgencyID;

  @UI.lineItem: [ { position: 30, importance: #HIGH } ]
  @UI.identification: [ { position: 30 } ]
  @UI.selectionField: [ { position: 20 } ]
  CustomerID;

  @UI.lineItem: [ { position: 40 } ]
  @UI.identification: [ { position: 40 } ]
  BeginDate;

  @UI.lineItem: [ { position: 50 } ]
  @UI.identification: [ { position: 50 } ]
  EndDate;

  @UI.identification: [ { position: 60 } ]
  BookingFee;

  @UI.lineItem: [ { position: 60 } ]
  @UI.identification: [ { position: 70 } ]
  TotalPrice;

  @UI.identification: [ { position: 80 } ]
  CurrencyCode;

  @UI.identification: [ { position: 90 } ]
  ShortNote;

  @UI.identification: [ { position: 100 } ]
  Description;

  @UI.lineItem: [ { position: 70, importance: #HIGH } ]
  @UI.identification: [ { position: 110 } ]
  @UI.selectionField: [ { position: 30 } ]
  OverallStatus;

  @UI.hidden: true
  OverallStatusText;

  @UI.hidden: true
  LocalLastChangedAt;

  @UI.hidden: true
  LastChangedAt;
}
```

MDE(Booking): 2단계의 `ZRAP_C_BOOKING_APPR_###` MDE와 같고 `annotate entity ZRAP_C_BOOKING_PROC_### with`만 다릅니다(같은 내용을 복사해 엔터티 이름만 바꾸세요).

계산 클래스:

```abap
CLASS zcl_rap_r17_ve_### DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_sadl_exit_calc_element_read.

  PRIVATE SECTION.
    CONSTANTS c_entity_proc   TYPE string VALUE `ZRAP_C_TRAVEL_PROC_###`.
    CONSTANTS c_ve_short_note TYPE string VALUE `SHORTNOTE`.
    CONSTANTS c_prefix        TYPE string VALUE `[P] `.

ENDCLASS.


CLASS zcl_rap_r17_ve_### IMPLEMENTATION.

  METHOD if_sadl_exit_calc_element_read~get_calculation_info.
    "before the DB read: which real fields do we need?
    IF iv_entity <> c_entity_proc.
      RETURN.
    ENDIF.
    IF line_exists( it_requested_calc_elements[ table_line = c_ve_short_note ] ).
      APPEND 'DESCRIPTION' TO et_requested_orig_elements.
    ENDIF.
  ENDMETHOD.


  METHOD if_sadl_exit_calc_element_read~calculate.
    "after the DB read: fill ShortNote per row
    IF NOT line_exists( it_requested_calc_elements[ table_line = c_ve_short_note ] ).
      RETURN.
    ENDIF.

    DATA travels TYPE STANDARD TABLE OF zrap_c_travel_proc_### WITH DEFAULT KEY.
    travels = CORRESPONDING #( it_original_data ).

    LOOP AT travels ASSIGNING FIELD-SYMBOL(<travel>).
      DATA(text) = CONV string( <travel>-Description ).
      IF strlen( text ) >= strlen( c_prefix ) AND substring( val = text len = strlen( c_prefix ) ) = c_prefix.
        text = substring( val = text off = strlen( c_prefix ) ).
      ENDIF.
      <travel>-ShortNote = text.             "truncated to 20 characters
    ENDLOOP.

    ct_calculated_data = CORRESPONDING #( travels ).
  ENDMETHOD.

ENDCLASS.
```

해설
- 가상 요소는 DB에 없는 필드라서 **읽기**는 계산 클래스가 맡고, **쓰기**는 원래 불가능합니다. 7단계에서 BDEF의 `field ( modify ) ShortNote;`로 이 필드를 입력 가능하게 열고, augment가 입력값을 기본 BO의 `Description`으로 옮깁니다. 이렇게 "프로젝션에만 있는 입력 필드 → 기본 BO의 실제 필드"가 augmentation의 대표 용도입니다.
- 참조 시나리오 `/DMO/C_Supplement`는 같은 기법을 **연관 경로 필드**에 씁니다: `_SupplementText.Description as SupplementDescription : localized`를 `field ( modify ) SupplementDescription;`으로 입력 가능하게 하고, augment가 로그온 언어의 텍스트 자식(`_SupplementText`)을 생성/수정합니다. 다국어 텍스트가 있는 BO라면 그 방식이 더 일반적입니다.
- 계산 클래스 코드 형태는 R-01의 `ZCL_RAP_TRAV_VE_###`와 같습니다(`get_calculation_info` → `calculate`, 이름은 대문자).
- `/DMO/I_Flight_StdVH`의 요소 이름(`AirlineID`, `Price` 등)은 R-01 Booking 프로젝션과 같은 것을 썼습니다. R-01에서 다른 값 도움말을 썼다면 그것을 그대로 쓰세요.

</details>

#### 7단계. 처리자 BDEF와 augment·precheck 구현

요구사항
1. 처리자 프로젝션 BDEF `ZRAP_C_TRAVEL_PROC_###`를 만드세요. 자기 행동 풀 `ZBP_RAP_C_TRAVEL_PROC_###`를 씁니다. draft는 노출하지 않습니다.
   - Travel: ETag, `ShortNote`를 입력 가능하게, `use create`와 `use update`에 보강(augment)과 사전 검사(precheck)를 붙임, `use delete`, Booking 생성 허용
   - Booking: ETag, `use update`, `use delete`, `_Travel` 읽기
2. 핸들러 `lhc_travelproc`를 구현하세요.
   - `augment`(생성·수정 요청 하나의 메서드):
     - 생성 요청에서 `ShortNote`가 들어왔으면 → 같은 인스턴스(`%cid_ref`)의 `Description`을 `[P] <ShortNote>`로 보강
     - 생성 요청에 `BookingFee`가 없고(`%control` 꺼짐) 통화가 있으면 → `BookingFee = 20` 보강
     - 수정 요청에서 `ShortNote`가 들어왔으면 → 그 인스턴스(`%tky`, `%cid_ref`)의 `Description`을 보강
     - 보강은 한 번의 `MODIFY AUGMENTING` 문으로 기본 BO에 보냅니다.
   - `precheck_create`, `precheck_update`: 요청의 `Description`(`%control` 켜짐)이 `!`로 시작하면 거부, 메시지 172를 `%element-Description`에.
3. 추적 스위치가 켜져 있으면 augment가 받은 생성/수정 건수와 보강 건수를 추적 클래스에 기록하세요.

**확인**
- BDEF·행동 풀이 활성화됩니다.
- 행동 풀의 메서드 선언이 `FOR MODIFY IMPORTING entities_create FOR CREATE TravelProc entities_update FOR UPDATE TravelProc` 형태임을 확인하세요(ADT Quick Fix가 만들어 줌).

<details><summary>정답·해설</summary>

```bdef
projection implementation in class zbp_rap_c_travel_proc_### unique;
strict ( 2 );

define behavior for ZRAP_C_TRAVEL_PROC_### alias TravelProc
use etag
{
  field ( modify ) ShortNote;            // 가상 요소를 입력 가능하게 (augmented field) (실제 시스템에서 확인 필요)

  use create ( augment, precheck );      // 기본 BO 에 넘기기 전 보강 + 프로젝션 사전 검사
  use update ( augment, precheck );
  use delete;

  use association _Booking { create; }   // draft 없는 프로젝션이라 with draft 없음
}

define behavior for ZRAP_C_BOOKING_PROC_### alias BookingProc
use etag
{
  use update;
  use delete;

  use association _Travel;
}
```

```abap
CLASS zbp_rap_c_travel_proc_### DEFINITION PUBLIC ABSTRACT FINAL FOR BEHAVIOR OF zrap_c_travel_proc_###.
ENDCLASS.

CLASS zbp_rap_c_travel_proc_### IMPLEMENTATION.
ENDCLASS.
```

Local Types 전체:

```abap
CLASS lhc_travelproc DEFINITION INHERITING FROM cl_abap_behavior_handler.
  PRIVATE SECTION.

    CONSTANTS c_default_fee TYPE /dmo/booking_fee VALUE 20.
    CONSTANTS c_note_prefix TYPE string VALUE `[P] `.

    "from: use create ( augment ) + use update ( augment ) -> ONE method for both
    METHODS augment FOR MODIFY
      IMPORTING entities_create FOR CREATE TravelProc
                entities_update FOR UPDATE TravelProc.

    "from: use create ( precheck )
    METHODS precheck_create FOR PRECHECK
      IMPORTING entities FOR CREATE TravelProc.

    "from: use update ( precheck )
    METHODS precheck_update FOR PRECHECK
      IMPORTING entities FOR UPDATE TravelProc.

ENDCLASS.


CLASS lhc_travelproc IMPLEMENTATION.

  METHOD augment.
    DATA travel_update TYPE TABLE FOR UPDATE zrap_r_travel_###\\Travel.
    DATA upd_line      LIKE LINE OF travel_update.

    "--- create requests: augment the instance that is being created (%cid_ref = %cid)
    LOOP AT entities_create INTO DATA(create).
      CLEAR upd_line.
      upd_line-%cid_ref = create-%cid.

      IF create-%control-ShortNote = if_abap_behv=>mk-on AND create-ShortNote IS NOT INITIAL.
        upd_line-Description          = |{ c_note_prefix }{ create-ShortNote }|.
        upd_line-%control-Description = if_abap_behv=>mk-on.
      ENDIF.

      IF create-%control-BookingFee <> if_abap_behv=>mk-on AND create-CurrencyCode IS NOT INITIAL.
        upd_line-BookingFee          = c_default_fee.
        upd_line-%control-BookingFee = if_abap_behv=>mk-on.
      ENDIF.

      IF upd_line-%control IS NOT INITIAL.
        APPEND upd_line TO travel_update.
      ENDIF.
    ENDLOOP.

    "--- update requests: only when the projection-only field was sent
    LOOP AT entities_update INTO DATA(update) WHERE %control-ShortNote = if_abap_behv=>mk-on.
      APPEND VALUE #( %tky                 = CORRESPONDING #( update-%tky )
                      %cid_ref             = update-%cid_ref
                      Description          = |{ c_note_prefix }{ update-ShortNote }|
                      %control-Description = if_abap_behv=>mk-on ) TO travel_update.
    ENDLOOP.

    IF zcl_rap_r17_trace_###=>gv_trace_on = abap_true.
      zcl_rap_r17_trace_###=>add( |[PROC augment] create={ lines( entities_create ) } | &&
                                  |update={ lines( entities_update ) } augmented={ lines( travel_update ) }| ).
    ENDIF.

    IF travel_update IS INITIAL.
      RETURN.
    ENDIF.

    "--- one augmenting request to the base BO; no response parameters allowed here
    MODIFY AUGMENTING ENTITIES OF zrap_r_travel_###
      ENTITY Travel
        UPDATE FROM travel_update.
  ENDMETHOD.


  METHOD precheck_create.
    LOOP AT entities INTO DATA(entity) WHERE %control-Description = if_abap_behv=>mk-on.
      CHECK entity-Description IS NOT INITIAL AND entity-Description(1) = '!'.
      APPEND VALUE #( %cid = entity-%cid ) TO failed-travelproc.
      APPEND VALUE #( %cid                 = entity-%cid
                      %msg                 = NEW zcm_rap_###( textid   = zcm_rap_###=>proc_description_invalid
                                                              severity = if_abap_behv_message=>severity-error )
                      %element-Description = if_abap_behv=>mk-on ) TO reported-travelproc.
    ENDLOOP.
  ENDMETHOD.


  METHOD precheck_update.
    LOOP AT entities INTO DATA(entity) WHERE %control-Description = if_abap_behv=>mk-on.
      CHECK entity-Description IS NOT INITIAL AND entity-Description(1) = '!'.
      APPEND VALUE #( %tky = entity-%tky ) TO failed-travelproc.
      APPEND VALUE #( %tky                 = entity-%tky
                      %msg                 = NEW zcm_rap_###( textid   = zcm_rap_###=>proc_description_invalid
                                                              severity = if_abap_behv_message=>severity-error )
                      %element-Description = if_abap_behv=>mk-on ) TO reported-travelproc.
    ENDLOOP.
  ENDMETHOD.

ENDCLASS.
```

왜 이렇게 쓰나
- **augment의 실행 시점**: 소비자 요청(Fiori, EML)이 프로젝션에 들어오면 → 프로젝션 precheck → 프로젝션 augment → 원래 요청 + 보강 요청이 **함께** 기본 BO로 넘어갑니다(기본 BO의 precheck, 기능 제어, 권한, 결정이 보강분에도 그대로 적용). 그래서 보강한 `BookingFee`에 대해서도 기본 BO의 `calculateTotalPrice` 결정이 돌아 총액이 바뀝니다.
- **메서드 하나**: 참조 시나리오 `/DMO/BP_C_SUPPLEMENT`처럼 `use create ( augment )`와 `use update ( augment )`의 import 파라미터가 한 메서드에 함께 옵니다(`entities_create FOR CREATE ...`, `entities_update FOR UPDATE ...`). 연관 생성의 augment는 따로(`FOR CREATE TravelProc\_Booking`, 커뮤니티 예제 `augment_cba_Items_tp`).
- **`MODIFY AUGMENTING ENTITIES OF <기본 BO>`**: 응답 파라미터(`FAILED`, `REPORTED`, `MAPPED`)를 쓸 수 없습니다(08 치트시트). 보강분에서 난 오류는 원래 요청의 인스턴스 응답으로 소비자에게 돌아갑니다.
- **`RELATING TO ... BY`는 왜 안 썼나**: 보강 요청이 원래 요청에 **없던 인스턴스**를 만들거나 바꿀 때(예: `/DMO/C_Supplement`가 Supplement 생성 요청을 받아 **텍스트 자식**을 새로 만듦) `abp_behv_relating_tab`에 "이 보강 줄은 원래 요청의 몇 번째 줄에서 나왔다"를 적어, 보강분의 실패가 원래 인스턴스로 연결되게 합니다. 여기서는 **같은 인스턴스**를 `%cid_ref`/`%tky`로 고치므로 관계표가 필요 없습니다. 자식을 보강한다면 이렇게 씁니다(참조 시나리오 형태):

```abap
    "example only: augment by creating children that were not in the original request
    "MODIFY AUGMENTING ENTITIES OF zrap_r_travel_###
    "  ENTITY Travel
    "    CREATE BY \_Booking FROM booking_cba
    "    RELATING TO entities_create BY relates_create.   "relates_create TYPE abp_behv_relating_tab (one index per line of booking_cba)
```

- **생성과 같은 요청의 수정**: `entities_update`에는 같은 요청에서 방금 만든 인스턴스(`%cid_ref`만 있음)가 올 수 있어, `%tky`와 `%cid_ref`를 둘 다 옮겼습니다(참조 시나리오도 둘 다 사용).
- **`field ( modify )`**: 7.84 "augmented 필드에 필드 특성을 지정할 수 있다". 참조 시나리오 `/DMO/C_Supplement`의 `field ( modify ) SupplementDescription;`(연관 경로 텍스트 필드)과 커뮤니티 예제의 `field ( modify ) orderDescription; // augment operation for virtual element (updatable virtual element)`가 근거입니다. 가상 요소에 쓰는 형태는 커뮤니티 예제로만 확인했습니다(실제 시스템에서 확인 필요). augmented 필드에 `mandatory` 등 다른 특성도 줄 수 있는지는 확인하지 못했습니다.
- **프로젝션 precheck**: 커뮤니티 예제 `use create ( augment, precheck ); // augment and precheck must be implemented ABP for projection`. 이 앱에서만 적용하고 싶은 입력 규칙(다른 앱·API에는 적용 안 함)을 넣는 곳입니다. 업무 규칙이면 기본 BO에 두세요.

자주 나는 오류와 해결
- `MODIFY AUGMENTING`을 프로젝션 행동 풀 밖(콘솔 등)에서 쓰면 구문 오류입니다. RAP BO 제공자(프로젝션 구현) 안에서만 허용됩니다.
- augment 안에서 `entities_create`를 직접 고치려 하면 안 됩니다(IMPORTING). 보강은 항상 별도 요청으로 보냅니다.
- `field ( modify )` 줄에서 오류가 나면 그 줄과 `ShortNote` 관련 코드를 빼고 BookingFee 보강만으로 진행하세요.

클래스 구조 해설
- `FOR MODIFY ... FOR CREATE TravelProc`: `entities_create`는 `TYPE TABLE FOR CREATE zrap_c_travel_proc_###`(프로젝션 파생 타입)이라 `ShortNote`와 `%control-ShortNote`가 있습니다. 기본 BO 파생 타입(`travel_update`)에는 `ShortNote`가 없습니다. 이 차이를 잇는 것이 augment입니다.
- `FOR PRECHECK`: 응답은 `failed`, `reported`만 있습니다. 프레임워크가 augment보다 먼저, 버퍼에 아무것도 쓰기 전에 부릅니다.

</details>

#### 8단계. 서비스 두 개와 Fiori 앱 비교

요구사항
1. 서비스 정의 `ZRAP_UI_TRAVEL_APPR_###`: 승인자 Travel/Booking을 `Travel`, `Booking`으로, 값 도움말 뷰(Agency, Customer, Overall Status)를 노출하세요.
2. 서비스 정의 `ZRAP_UI_TRAVEL_PROC_###`: 처리자 Travel/Booking과 값 도움말 뷰(Agency, Customer, Currency, Flight, Overall Status, Booking Status)를 노출하세요.
3. 서비스 바인딩 `ZRAP_UI_TRAVEL_APPR_O4_###`, `ZRAP_UI_TRAVEL_PROC_O4_###`(OData V4 - UI)를 만들고 Publish하세요.
4. 세 앱(기존, 승인자, 처리자)을 Preview로 열어 비교표를 채우세요: 보이는 건수, Create/Delete 버튼, Edit 동작(draft 여부), 액션 버튼, 편집 가능한 필드, `ShortNote`.
5. 처리자 앱에서 Travel을 하나 만들면서 Short note에 `From processor app`을 넣고 Booking Fee는 비워 두세요. 저장 후 Description과 Booking Fee를 확인합니다. Description을 `!test`로 바꿔 저장해 보세요.
6. 승인자 앱에서 Open 상태 Travel에 Request Revision을 실행하세요(사유 `Please check dates`).

**직접 추가할 어노테이션**
- `@EndUserText.label` — 서비스 정의 설명

**확인**
- 승인자 앱: EUR Travel만 보이고, Create/Delete 버튼이 없으며, Edit을 누르면 draft 없이 바로 편집(저장 버튼 Save)됩니다. Booking Fee만 입력 가능합니다. Accept / Reject / Request Revision 버튼이 보입니다.
- 처리자 앱: 모든 Travel, Create/Delete 있음, 액션 버튼 없음, Short note 입력 가능. 5번 결과: Description = `[P] From processor app`, Booking Fee = 20, 총액에 20이 반영. `!test` 저장은 메시지 172로 거부되고 Description 필드가 빨갛게 표시됩니다.
- 6번: 성공 토스트 "Revision for travel … requested: Please check dates", Description 앞에 `[REVISION] Please check dates`. 기존 앱에서도 같은 값이 보입니다(같은 기본 BO).

<details><summary>정답·해설</summary>

```cds
@EndUserText.label: 'Travel approval (R-17)'
define service ZRAP_UI_TRAVEL_APPR_### {
  expose ZRAP_C_TRAVEL_APPR_###   as Travel;
  expose ZRAP_C_BOOKING_APPR_###  as Booking;
  expose /DMO/I_Agency_StdVH      as Agency;
  expose /DMO/I_Customer_StdVH    as Customer;
  expose /DMO/I_Overall_Status_VH as OverallStatus;
}
```

```cds
@EndUserText.label: 'Travel processing (R-17)'
define service ZRAP_UI_TRAVEL_PROC_### {
  expose ZRAP_C_TRAVEL_PROC_###   as Travel;
  expose ZRAP_C_BOOKING_PROC_###  as Booking;
  expose /DMO/I_Agency_StdVH      as Agency;
  expose /DMO/I_Customer_StdVH    as Customer;
  expose I_CurrencyStdVH          as Currency;
  expose /DMO/I_Flight_StdVH      as Flight;
  expose /DMO/I_Overall_Status_VH as OverallStatus;
  expose /DMO/I_Booking_Status_VH as BookingStatus;
}
```

바인딩: New → Service Binding → 이름 `ZRAP_UI_TRAVEL_APPR_O4_###`, Binding Type `OData V4 - UI`, Service Definition `ZRAP_UI_TRAVEL_APPR_###` → 활성화 → Publish. 처리자도 같은 방법.

비교표(예상)

| 항목 | 기존 `ZRAP_UI_TRAVEL_O4_###` | 승인자 | 처리자 |
|---|---|---|---|
| 목록 건수 | 전체 | EUR만 | 전체 |
| Create / Delete | 있음 | 없음 | 있음 |
| Edit | draft(Discard Draft, 자동 저장) | draft 없음, Save/Cancel | draft 없음, Save/Cancel |
| 액션 | Accept, Reject, Deduct, Copy … | Accept, Reject, Deduct, Request Revision | 없음 |
| 편집 가능 필드 | 기본 BO 규칙대로 | Booking Fee만(+ 기본 BO의 동적 제어) | 기본 BO 규칙 + Short note |
| Booking 추가 | 있음 | 없음 | 있음 |

해설
- 같은 데이터, 같은 업무 규칙(검증, 결정, 기능 제어, 권한)인데 **화면 능력만** 다릅니다. 모두 기본 BO의 트랜잭션 버퍼와 세이버를 공유하므로, 한 앱에서 바꾼 값이 다른 앱에 바로 보입니다.
- 승인자 앱에서 Accept 후 그 Travel이 목록에서 사라지지 않는 이유: WHERE가 상태가 아니라 통화 조건이기 때문입니다. 만약 WHERE를 `OverallStatus = 'O'`로 두었다면, Accept 직후 결과 읽기(`result [1] $self`)가 instance filter에 걸려 실패할 수 있습니다. instance filter를 쓸 때는 **액션으로 바뀌는 필드를 필터 조건에 넣지 않는 것**이 안전합니다(설계 판단이며, 실제 동작은 실제 시스템에서 확인 필요).
- 처리자 앱의 Short note는 저장 후 다시 읽을 때 6단계 계산 클래스가 Description에서 `[P] `를 떼어 보여 줍니다. Fiori가 Short note를 다시 보내지 않는 한 Description은 바뀌지 않습니다.
- `!test` 거부는 프로젝션 precheck에서 일어나므로, **기존 앱**에서는 같은 값을 저장할 수 있습니다. 앱별 입력 규칙의 예입니다.

</details>

#### 9단계. EML 콘솔 (1): 프로젝션별 EML — instance filter, 새 액션·함수, augment, PRIVILEGED와 FORWARDING PRIVILEGED

요구사항
1. 콘솔 클래스 `ZCL_RAP_R17_EML_###`(`if_oo_adt_classrun`)를 만드세요. `main`은 샘플 찾기 → 추적 켜기 → 아래 메서드들을 차례로 실행하고, 각 메서드 끝에서 추적 기록을 출력합니다.
2. `find_samples`: `ZRAP_ATRAV_###`에서 상태 O인 EUR Travel 하나(`mv_eur_id`, 대행사 `mv_eur_agency`)와 EUR가 아닌 Travel 하나(`mv_other_id`)를 고릅니다. 없으면 안내 후 종료.
3. `m09_instance_filter`:
   - 두 Travel을 **승인자** BO로 읽기 → EUR만 결과, 다른 하나는 `FAILED`(원인 출력)
   - 같은 두 Travel을 **기존 앱** BO(`ZRAP_C_TRAVEL_###`)로 읽기 → 둘 다 결과
   - 승인자 BO로 EUR가 아닌 Travel의 `BookingFee` 수정 → 실패 확인 → `ROLLBACK ENTITIES`
   - 승인자 BO로 CREATE, `FIELDS ( CreatedBy )` 읽기를 주석으로 써 두고 왜 구문 오류인지 적기
4. `m09_projection_ops`:
   - 승인자 함수 `getApprovalInfo`를 EUR Travel에 실행해 `%param` 출력
   - 승인자 액션 `requestRevision`(사유 `Check dates (EML)`) 실행 → 결과의 `Description`과 메시지 출력 → `ROLLBACK ENTITIES`
   - 같은 함수를 기본 BO 이름으로 부르는 코드를 주석으로 써 두고 왜 안 되는지 적기
5. `m09_augment`:
   - 처리자 BO로 Travel 생성(대행사 070001, 고객 000001, 시작 오늘+30, 끝 오늘+40, 통화 EUR, `ShortNote = 'EML augment'`, BookingFee 미지정) → `MAPPED`의 `%pid`로 **기본 BO**를 읽어 `Description`, `BookingFee`, `TotalPrice` 출력
   - `Description = '!bad'`로 하나 더 생성 → precheck 실패와 메시지 출력
   - `ROLLBACK ENTITIES`
6. `m09_privileged`:
   - 스위치 테이블 `ZRAP_CTRL_###`의 `deny_country`를 EUR Travel 대행사의 국가로 바꾸고 `COMMIT WORK`(원래 값 기억)
   - (a) 승인자 `requestRevision`을 **일반** EML로 실행 → 실패 원인·메시지 출력 → `ROLLBACK ENTITIES`
   - (b) 같은 호출을 `PRIVILEGED`로 실행 → 성공 → `COMMIT ENTITIES`
   - 스위치를 원래 값으로 되돌림
   - 추적 기록에서 승인자 핸들러가 본 `privileged` 값이 (a)와 (b)에서 어떻게 다른지 확인

**확인**
- 실행(F9) 결과 예시와 비슷하게 나옵니다. 특히:
  - instance filter: 승인자 읽기 결과 1건, 실패 1건(`not_found`), 기존 앱 읽기 결과 2건
  - augment: 기본 BO에서 `Description = [P] EML augment`, `BookingFee = 20`, 추적 `[PROC augment] create=1 update=0 augmented=1`
  - privileged: (a) `fail-cause`가 unauthorized 값, (b) 실패 0건, 추적 (a) `privileged=` 공백, (b) `privileged=X`
- (b) 후 Data Preview에서 EUR Travel의 Description이 `[REVISION] Privileged revision …`으로 시작합니다.

<details><summary>정답·해설</summary>

```abap
CLASS zcl_rap_r17_eml_### DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_oo_adt_classrun.

  PRIVATE SECTION.
    DATA mv_eur_id     TYPE /dmo/travel_id.
    DATA mv_eur_agency TYPE /dmo/agency_id.
    DATA mv_other_id   TYPE /dmo/travel_id.

    METHODS find_samples
      IMPORTING out             TYPE REF TO if_oo_adt_classrun_out
      RETURNING VALUE(rv_found) TYPE abap_boolean.

    METHODS print_trace
      IMPORTING out TYPE REF TO if_oo_adt_classrun_out.

    METHODS m09_instance_filter IMPORTING out TYPE REF TO if_oo_adt_classrun_out.
    METHODS m09_projection_ops  IMPORTING out TYPE REF TO if_oo_adt_classrun_out.
    METHODS m09_augment         IMPORTING out TYPE REF TO if_oo_adt_classrun_out.
    METHODS m09_privileged      IMPORTING out TYPE REF TO if_oo_adt_classrun_out.

ENDCLASS.


CLASS zcl_rap_r17_eml_### IMPLEMENTATION.

  METHOD if_oo_adt_classrun~main.
    IF find_samples( out ) = abap_false.
      RETURN.
    ENDIF.

    zcl_rap_r17_trace_###=>reset( ).
    zcl_rap_r17_trace_###=>gv_trace_on = abap_true.

    m09_instance_filter( out ).
    m09_projection_ops( out ).
    m09_augment( out ).
    m09_privileged( out ).
    "steps 10 and 11 add their calls here
  ENDMETHOD.


  METHOD find_samples.
    SELECT FROM zrap_atrav_###
      FIELDS travel_id, agency_id
      WHERE currency_code = 'EUR'
        AND overall_status = 'O'
      ORDER BY travel_id
      INTO @DATA(eur)
      UP TO 1 ROWS.
    ENDSELECT.

    SELECT FROM zrap_atrav_###
      FIELDS travel_id
      WHERE currency_code <> 'EUR'
      ORDER BY travel_id
      INTO @mv_other_id
      UP TO 1 ROWS.
    ENDSELECT.

    mv_eur_id     = eur-travel_id.
    mv_eur_agency = eur-agency_id.

    IF mv_eur_id IS INITIAL OR mv_other_id IS INITIAL.
      out->write( `Need one open EUR travel and one non-EUR travel in ZRAP_ATRAV_###.` ).
      rv_found = abap_false.
      RETURN.
    ENDIF.

    out->write( |EUR travel { mv_eur_id } (agency { mv_eur_agency }), other travel { mv_other_id }| ).
    rv_found = abap_true.
  ENDMETHOD.


  METHOD print_trace.
    LOOP AT zcl_rap_r17_trace_###=>gt_log INTO DATA(line).
      out->write( |  trace: { line }| ).
    ENDLOOP.
    DATA(keep_on) = zcl_rap_r17_trace_###=>gv_trace_on.
    zcl_rap_r17_trace_###=>reset( ).
    zcl_rap_r17_trace_###=>gv_trace_on = keep_on.
  ENDMETHOD.


  METHOD m09_instance_filter.
    out->write( `=== 9-1 managed instance filter ===` ).

    "(1) approver projection: WHERE CurrencyCode = 'EUR' + with managed instance filter
    READ ENTITIES OF zrap_c_travel_appr_###
      ENTITY TravelAppr
        FIELDS ( TravelID CurrencyCode )
        WITH VALUE #( ( TravelID = mv_eur_id ) ( TravelID = mv_other_id ) )
      RESULT DATA(appr_result)
      FAILED DATA(appr_failed).
    out->write( |approver read: result { lines( appr_result ) }, failed { lines( appr_failed-travelappr ) }| ).
    LOOP AT appr_failed-travelappr INTO DATA(af).
      out->write( |  failed { af-TravelID } cause { af-%fail-cause } (not_found = { if_abap_behv=>cause-not_found })| ).
    ENDLOOP.

    "(2) the existing app projection has no WHERE -> both instances
    READ ENTITIES OF zrap_c_travel_###
      ENTITY Travel
        FIELDS ( TravelID CurrencyCode )
        WITH VALUE #( ( TravelID = mv_eur_id ) ( TravelID = mv_other_id ) )
      RESULT DATA(c_result).
    out->write( |existing app read: result { lines( c_result ) }| ).

    "(3) modify through the approver: the filtered instance cannot be reached
    MODIFY ENTITIES OF zrap_c_travel_appr_###
      ENTITY TravelAppr
        UPDATE FIELDS ( BookingFee )
        WITH VALUE #( ( TravelID = mv_other_id BookingFee = 1 ) )
      FAILED DATA(upd_failed).
    out->write( |approver update of non-EUR travel: failed { lines( upd_failed-travelappr ) }| ).
    ROLLBACK ENTITIES.

    "(4) syntax errors on purpose (keep commented):
    "    no 'use create' in the approver projection -> CREATE does not exist for TravelAppr
    "MODIFY ENTITIES OF zrap_c_travel_appr_### ENTITY TravelAppr CREATE FIELDS ( AgencyID ) WITH VALUE #( ( %cid = 'X' AgencyID = '070001' ) ).
    "    field ( suppress ) CreatedBy -> the component does not exist in the derived types
    "READ ENTITIES OF zrap_c_travel_appr_### ENTITY TravelAppr FIELDS ( CreatedBy ) WITH VALUE #( ( TravelID = mv_eur_id ) ) RESULT DATA(x).

    print_trace( out ).
  ENDMETHOD.


  METHOD m09_projection_ops.
    out->write( `=== 9-2 projection-only function and action ===` ).

    "(1) projection-only function
    READ ENTITIES OF zrap_c_travel_appr_###
      ENTITY TravelAppr
        EXECUTE getApprovalInfo
        FROM VALUE #( ( TravelID = mv_eur_id ) )
      RESULT DATA(info)
      FAILED DATA(info_failed).
    LOOP AT info INTO DATA(i).
      out->write( |getApprovalInfo { i-%param-travel_id }: days { i-%param-days_to_start }, | &&
                  |bookings { i-%param-booking_count }, { i-%param-total_price } { i-%param-currency_code }, | &&
                  |"{ i-%param-recommendation }"| ).
    ENDLOOP.
    out->write( |failed { lines( info_failed-travelappr ) }| ).

    "(2) projection-only action
    MODIFY ENTITIES OF zrap_c_travel_appr_###
      ENTITY TravelAppr
        EXECUTE requestRevision
        FROM VALUE #( ( TravelID = mv_eur_id  %param-revision_note = 'Check dates (EML)' ) )
      RESULT DATA(rev_result)
      FAILED DATA(rev_failed)
      REPORTED DATA(rev_reported).
    LOOP AT rev_result INTO DATA(rr).
      out->write( |requestRevision result: "{ rr-%param-Description }"| ).
    ENDLOOP.
    out->write( |failed { lines( rev_failed-travelappr ) }| ).
    LOOP AT rev_reported-travelappr INTO DATA(rm).
      out->write( |  message: { rm-%msg->if_message~get_text( ) }| ).
    ENDLOOP.
    ROLLBACK ENTITIES.          "do not keep it - step 9-4 saves a privileged revision

    "(3) syntax error on purpose: the base BO does not know the projection-only function
    "READ ENTITIES OF zrap_r_travel_### ENTITY Travel EXECUTE getApprovalInfo FROM VALUE #( ( TravelID = mv_eur_id ) ) RESULT DATA(y).

    print_trace( out ).
  ENDMETHOD.


  METHOD m09_augment.
    out->write( `=== 9-3 augment and precheck (processor projection) ===` ).
    DATA(today) = cl_abap_context_info=>get_system_date( ).

    "(1) create with the projection-only field ShortNote and without BookingFee
    MODIFY ENTITIES OF zrap_c_travel_proc_###
      ENTITY TravelProc
        CREATE FIELDS ( AgencyID CustomerID BeginDate EndDate CurrencyCode ShortNote )
        WITH VALUE #( ( %cid         = 'PROC1'
                        AgencyID     = '070001'
                        CustomerID   = '000001'
                        BeginDate    = today + 30
                        EndDate      = today + 40
                        CurrencyCode = 'EUR'
                        ShortNote    = 'EML augment' ) )
      MAPPED DATA(mapped)
      FAILED DATA(failed)
      REPORTED DATA(reported).
    out->write( |create: mapped { lines( mapped-travelproc ) }, failed { lines( failed-travelproc ) }| ).

    "read the BASE BO with the preliminary key (%pid, late numbering)
    IF mapped-travelproc IS NOT INITIAL.
      READ ENTITIES OF zrap_r_travel_###
        ENTITY Travel
          FIELDS ( Description BookingFee TotalPrice CurrencyCode )
          WITH VALUE #( FOR m IN mapped-travelproc ( %pid = m-%pid ) )
        RESULT DATA(base_travels).
      LOOP AT base_travels INTO DATA(bt).
        out->write( |base BO: Description "{ bt-Description }", BookingFee { bt-BookingFee }, | &&
                    |TotalPrice { bt-TotalPrice } { bt-CurrencyCode }| ).
      ENDLOOP.
    ENDIF.

    "(2) projection precheck rejects '!'
    MODIFY ENTITIES OF zrap_c_travel_proc_###
      ENTITY TravelProc
        CREATE FIELDS ( AgencyID CustomerID BeginDate EndDate CurrencyCode Description )
        WITH VALUE #( ( %cid         = 'PROC2'
                        AgencyID     = '070001'
                        CustomerID   = '000001'
                        BeginDate    = today + 30
                        EndDate      = today + 40
                        CurrencyCode = 'EUR'
                        Description  = '!bad' ) )
      FAILED DATA(pre_failed)
      REPORTED DATA(pre_reported).
    out->write( |precheck: failed { lines( pre_failed-travelproc ) }| ).
    LOOP AT pre_reported-travelproc INTO DATA(pm).
      out->write( |  message: { pm-%msg->if_message~get_text( ) }| ).
    ENDLOOP.

    ROLLBACK ENTITIES.
    print_trace( out ).
  ENDMETHOD.


  METHOD m09_privileged.
    out->write( `=== 9-4 PRIVILEGED and FORWARDING PRIVILEGED ===` ).

    "deny the agency country of the EUR travel (R-03 simulation of /DMO/TRVL)
    SELECT SINGLE FROM /dmo/i_agency FIELDS CountryCode WHERE AgencyID = @mv_eur_agency INTO @DATA(country).
    SELECT SINGLE FROM zrap_ctrl_### FIELDS * WHERE ctrl_id = 'TRAVEL' INTO @DATA(ctrl_old).
    ctrl_old-ctrl_id = 'TRAVEL'.                 "row may not exist yet -> restore writes an empty switch row
    DATA(ctrl_new) = ctrl_old.
    ctrl_new-deny_country = country.
    MODIFY zrap_ctrl_### FROM @ctrl_new.
    COMMIT WORK.
    out->write( |deny_country = { country }| ).

    "(a) normal call: the projection handler forwards 'not privileged' -> base update is unauthorized
    MODIFY ENTITIES OF zrap_c_travel_appr_###
      ENTITY TravelAppr
        EXECUTE requestRevision
        FROM VALUE #( ( TravelID = mv_eur_id  %param-revision_note = 'Normal revision' ) )
      FAILED DATA(failed_a)
      REPORTED DATA(reported_a).
    LOOP AT failed_a-travelappr INTO DATA(fa).
      out->write( |(a) failed cause { fa-%fail-cause } (unauthorized = { if_abap_behv=>cause-unauthorized })| ).
    ENDLOOP.
    LOOP AT reported_a-travelappr INTO DATA(ra).
      out->write( |(a) message: { ra-%msg->if_message~get_text( ) }| ).
    ENDLOOP.
    ROLLBACK ENTITIES.
    print_trace( out ).

    "(b) privileged call: allowed because the approver BDEF says 'with privileged mode'
    MODIFY ENTITIES OF zrap_c_travel_appr_### PRIVILEGED
      ENTITY TravelAppr
        EXECUTE requestRevision
        FROM VALUE #( ( TravelID = mv_eur_id  %param-revision_note = 'Privileged revision' ) )
      RESULT DATA(result_b)
      FAILED DATA(failed_b).
    out->write( |(b) failed { lines( failed_b-travelappr ) }, result "{ VALUE #( result_b[ 1 ]-%param-Description OPTIONAL ) }"| ).

    COMMIT ENTITIES RESPONSE OF zrap_c_travel_appr_### FAILED DATA(commit_failed).
    out->write( |(b) commit sy-subrc = { sy-subrc }| ).
    print_trace( out ).

    "restore the switch
    MODIFY zrap_ctrl_### FROM @ctrl_old.
    COMMIT WORK.
  ENDMETHOD.

ENDCLASS.
```

콘솔 출력 예시(번호·날짜는 다름)

```
EUR travel 00000004 (agency 070012), other travel 00000001
=== 9-1 managed instance filter ===
approver read: result 1, failed 1
  failed 00000001 cause 1 (not_found = 1)
existing app read: result 2
approver update of non-EUR travel: failed 1
=== 9-2 projection-only function and action ===
getApprovalInfo 00000004: days 45, bookings 3, 2210.00 EUR, "OK"
failed 0
requestRevision result: "[REVISION] Check dates (EML) Business trip"
failed 0
  message: Revision for travel 00000004 requested: Check dates (EML)
  trace: [APPR getApprovalInfo] privileged= from_projection=... from_interface= in_local_mode=
  trace: [APPR requestRevision] privileged= from_projection=... from_interface= in_local_mode=
=== 9-3 augment and precheck (processor projection) ===
create: mapped 1, failed 0
base BO: Description "[P] EML augment", BookingFee 20.00, TotalPrice 20.00 EUR
precheck: failed 1
  message: Description must not start with "!" in the processor app.
  trace: [PROC augment] create=1 update=0 augmented=1
=== 9-4 PRIVILEGED and FORWARDING PRIVILEGED ===
deny_country = DE
(a) failed cause 3 (unauthorized = 3)
(a) message: No authorization for agency 070012 (country DE).
  trace: [APPR requestRevision] privileged= ...
(b) failed 0, result "[REVISION] Privileged revision Business trip"
(b) commit sy-subrc = 0
  trace: [APPR requestRevision] privileged=X ...
```

(`%fail-cause`의 숫자 값은 예시입니다. 비교용으로 상수 값도 같이 출력했습니다. `from_projection` 값은 프로젝션 자신의 핸들러에서 무엇이 나오는지 확인하지 못해 `...`로 두었습니다.)

왜 이렇게 쓰나
- **instance filter 효과**: `with managed instance filter`가 있으면 키로 직접 접근해도 WHERE 밖 인스턴스는 "없는 것"처럼 처리됩니다(그래서 원인이 `not_found`라고 예상했습니다. 실제 원인 값은 실행해서 확인하세요). BDEF 머리에서 이 줄을 주석 처리하고 다시 실행하면 승인자 읽기 결과가 2건이 되는 것을 비교해 보세요. 이것이 "WHERE는 목록용, instance filter는 트랜잭션 접근까지"라는 차이입니다.
- **프로젝션 전용 연산은 그 프로젝션 이름으로만** 부를 수 있습니다. 기본 BO, 기존 앱, 처리자 앱에는 `requestRevision`이 없습니다.
- **augment 확인은 기본 BO로**: 처리자 BO로 읽으면 `ShortNote`가 계산 클래스 값이 아니라(EML 읽기는 SADL 가상 요소 계산을 거치지 않음) 비어 있을 수 있습니다. 보강 결과는 기본 BO의 `Description`, `BookingFee`로 확인하는 것이 정확합니다.
- **PRIVILEGED의 세 가지 조건**: (1) 기본 BO가 `with privileged mode disabling <컨텍스트>`로 무엇을 끌지 정의, (2) 호출 대상 BDEF(여기서는 승인자 프로젝션)가 `with privileged mode`로 허용, (3) 소비자가 `PRIVILEGED`를 붙여 호출. 그리고 중간 계층(프로젝션 행동 풀)이 기본 BO를 다시 부를 때 `FORWARDING PRIVILEGED`를 써야 특권이 **이어집니다**. 4단계 코드에서 `FORWARDING PRIVILEGED`를 지우고 다시 실행하면 (b)도 실패하는 것을 확인해 보세요(특권이 끊김).
- `COMMIT ENTITIES RESPONSE OF zrap_c_travel_appr_###`: 프로젝션 이름으로도 응답을 받을 수 있습니다. "기본 BO의 저장 시퀀스에서 실패한 인스턴스는 프로젝션 소비자에게 돌려주고, failed의 메시지는 프로젝션으로 자동 매핑된다"(Release News "Commits in the Context of RAP Projections").
- 스위치 테이블을 콘솔에서 `MODIFY` + `COMMIT WORK`한 것은 R-03 10단계와 같은 방식입니다(RAP 트랜잭션 밖이므로 허용).

자주 나는 오류와 해결
- `SELECT ... UP TO 1 ROWS ... ENDSELECT` 대신 `SELECT SINGLE`을 쓰면 `ORDER BY`를 쓸 수 없다는 경고가 납니다. 위처럼 쓰거나 `INTO TABLE` 후 첫 줄을 쓰세요.
- `mapped-travelproc`의 `%pid`가 없다는 오류: late numbering이 아니라면 `%key`로 읽으세요. 이 BO는 R-01부터 late numbering이라 `%pid`가 있습니다.
- (b)가 lock 오류로 실패하면 같은 Travel에 다른 사용자(또는 당신의 Fiori 탭)의 draft가 있는지 확인하고 Discard하세요.

</details>

#### 10단계. 기본 BO 안쪽 들여다보기: `WITH CHANGES`, 현재 단계·문맥, late save 읽기 금지

요구사항
1. 기본 BDEF `ZRAP_R_TRAVEL_###`의 Travel 행동에 실험용 검증 `r17TraceChanges`(생성·수정·삭제 시 저장 전 실행)를 추가하고, `draft determine action Prepare`에도 넣으세요.
2. `lhc_travel`에 `r17TraceChanges`를 구현하세요(추적 스위치가 꺼져 있으면 즉시 종료).
   - `cl_abap_behv_aux=>get_current_phase( )`, `get_current_handler_kind( )`, `get_current_context( )`(`from_projection`, `from_interface`, `privileged`, `draft_activate`)를 추적에 기록
   - `READ ENTITY IN LOCAL MODE ... WITH CHANGES`로 `Description`, `BookingFee`, `OverallStatus`를 읽어 인스턴스마다 `%chg`(누적 변경 종류)와 필드별 `%control`(바뀐 필드인지)을 기록
   - 실패를 보고하지 않습니다(관찰만).
3. 세이버 `lsc_zrap_r_travel_###`의 `save_modified` 맨 앞에, `gv_provoke_late_read`가 켜져 있을 때만 `READ ENTITIES ... IN LOCAL MODE`를 실행하는 실험 코드를 넣으세요.
4. 콘솔에 `m10_with_changes`를 추가하세요: 처리자 BO로 Travel 하나 생성 + EUR 아닌 Travel의 `BookingFee` 수정(기존 값 + 1) → `COMMIT ENTITIES IN SIMULATION MODE`(DB 저장 없이 early save만) → 추적 출력 → `ROLLBACK ENTITIES`.
5. 콘솔에 `m10_late_save_read`를 추가하되 `main`에서는 **주석 처리된 호출**로 두세요: 스위치를 켜고 처리자 BO로 BookingFee를 수정해 실제 `COMMIT ENTITIES` → 덤프가 나는지 확인하는 용도입니다.

**확인**
- 기본 BDEF·행동 풀이 활성화되고, 기존 앱이 그대로 동작합니다(추적 스위치는 콘솔에서만 켜지므로 Fiori에는 영향 없음).
- `m10_with_changes` 출력에 단계 `EARLY_SAVE`에 해당하는 값, 새 Travel의 `%chg`가 create, 수정한 Travel의 `%chg`가 update이고 `BookingFee changed = X`, `Description changed`는 공백으로 나옵니다.
- `m10_late_save_read` 호출 주석을 풀고 실행하면 런타임 오류가 납니다. ADT의 ABAP Runtime Errors 뷰(또는 Feed Reader)에서 오류 이름과 "late save 단계에서 허용되지 않는 문장"이라는 취지의 설명을 확인한 뒤 다시 주석 처리하세요.

<details><summary>정답·해설</summary>

기본 BDEF `ZRAP_R_TRAVEL_###`에 추가(Travel 행동 블록 안, 기존 검증 아래):

```bdef
  // R-17 experiment: observe accumulated changes in the early save phase (does nothing unless the console switches it on)
  validation r17TraceChanges on save { create; update; delete; }
```

`draft determine action Prepare { ... }` 안에 한 줄 추가:

```bdef
    validation r17TraceChanges;
```

`lhc_travel` 정의부에 추가:

```abap
    "from: validation r17TraceChanges on save { create; update; delete; }
    METHODS r17TraceChanges FOR VALIDATE ON SAVE
      IMPORTING keys FOR Travel~r17TraceChanges.
```

`lhc_travel` 구현부에 추가:

```abap
  METHOD r17TraceChanges.
    CHECK zcl_rap_r17_trace_###=>gv_trace_on = abap_true.

    "--- where am I? ------------------------------------------------
    DATA root_entity TYPE abp_root_entity_name.
    FINAL(phase)        = cl_abap_behv_aux=>get_current_phase( ).
    FINAL(handler_kind) = cl_abap_behv_aux=>get_current_handler_kind( IMPORTING root_entity = root_entity ).
    cl_abap_behv_aux=>get_current_context( IMPORTING from_projection = FINAL(fr_proj)
                                                     from_interface  = FINAL(fr_int)
                                                     privileged      = FINAL(priv)
                                                     draft_activate  = FINAL(dr_act) ).
    zcl_rap_r17_trace_###=>add( |[BASE r17TraceChanges] phase={ phase } handler_kind={ handler_kind } root={ root_entity } | &&
                                |from_projection={ fr_proj } from_interface={ fr_int } privileged={ priv } draft_activate={ dr_act }| ).

    "--- what happened to these instances in this transaction? ------
    DATA changes TYPE TABLE FOR READ CHANGES zrap_r_travel_###.

    READ ENTITY IN LOCAL MODE zrap_r_travel_###
      WITH CHANGES
      FIELDS ( Description BookingFee OverallStatus ) WITH CORRESPONDING #( keys )
      RESULT changes
      FAILED DATA(changes_failed).

    LOOP AT changes INTO DATA(chg).
      DATA(kind) = SWITCH string( chg-%chg
                                  WHEN if_abap_behv=>cop-create   THEN `create`
                                  WHEN if_abap_behv=>cop-update   THEN `update`
                                  WHEN if_abap_behv=>cop-recreate THEN `recreate`
                                  ELSE |other({ chg-%chg })| ).
      zcl_rap_r17_trace_###=>add( |  TravelID={ chg-TravelID } pid?={ xsdbool( chg-%pid IS NOT INITIAL ) } %chg={ kind } | &&
                                  |Description changed={ xsdbool( chg-%control-Description = if_abap_behv=>mk-on ) } | &&
                                  |BookingFee changed={ xsdbool( chg-%control-BookingFee = if_abap_behv=>mk-on ) } | &&
                                  |BookingFee={ chg-BookingFee }| ).
    ENDLOOP.
    zcl_rap_r17_trace_###=>add( |  WITH CHANGES failed: { lines( changes_failed-travel ) }| ).
  ENDMETHOD.
```

세이버 `save_modified` 맨 앞에 추가(R-04 7단계 구현 위):

```abap
    "--- R-17 experiment: EML READ in the late save phase is NOT allowed (switched off by default)
    IF zcl_rap_r17_trace_###=>gv_provoke_late_read = abap_true.
      READ ENTITIES OF zrap_r_travel_### IN LOCAL MODE
        ENTITY Travel
          FIELDS ( Description )
          WITH VALUE #( FOR u IN update-travel ( TravelID = u-TravelID ) )
        RESULT DATA(late_read).
    ENDIF.
```

콘솔 정의부에 추가:

```abap
    METHODS m10_with_changes   IMPORTING out TYPE REF TO if_oo_adt_classrun_out.
    METHODS m10_late_save_read IMPORTING out TYPE REF TO if_oo_adt_classrun_out.
```

`main`에 추가:

```abap
    m10_with_changes( out ).
    "m10_late_save_read( out ).   "dumps on purpose - run once, then comment again
```

콘솔 구현부에 추가:

```abap
  METHOD m10_with_changes.
    out->write( `=== 10 WITH CHANGES and current phase (early save, simulation) ===` ).
    DATA(today) = cl_abap_context_info=>get_system_date( ).

    SELECT SINGLE FROM zrap_atrav_### FIELDS booking_fee WHERE travel_id = @mv_other_id INTO @DATA(old_fee).

    MODIFY ENTITIES OF zrap_c_travel_proc_###
      ENTITY TravelProc
        CREATE FIELDS ( AgencyID CustomerID BeginDate EndDate CurrencyCode ShortNote )
        WITH VALUE #( ( %cid = 'CHG1' AgencyID = '070001' CustomerID = '000001'
                        BeginDate = today + 30 EndDate = today + 40 CurrencyCode = 'EUR'
                        ShortNote = 'with changes' ) )
        UPDATE FIELDS ( BookingFee )
        WITH VALUE #( ( TravelID = mv_other_id BookingFee = old_fee + 1 ) )
      FAILED DATA(failed).
    out->write( |modify failed { lines( failed-travelproc ) }| ).

    "interaction phase is over -> early save runs validations (incl. r17TraceChanges), nothing is written
    COMMIT ENTITIES IN SIMULATION MODE RESPONSE OF zrap_r_travel_### FAILED DATA(sim_failed).
    out->write( |simulation sy-subrc = { sy-subrc }| ).

    print_trace( out ).
    ROLLBACK ENTITIES.
  ENDMETHOD.


  METHOD m10_late_save_read.
    out->write( `=== 10 EML read in late save (expect a runtime error) ===` ).
    SELECT SINGLE FROM zrap_atrav_### FIELDS booking_fee WHERE travel_id = @mv_other_id INTO @DATA(old_fee).

    MODIFY ENTITIES OF zrap_c_travel_proc_###
      ENTITY TravelProc
        UPDATE FIELDS ( BookingFee )
        WITH VALUE #( ( TravelID = mv_other_id BookingFee = old_fee ) )
      FAILED DATA(failed).

    zcl_rap_r17_trace_###=>gv_provoke_late_read = abap_true.
    COMMIT ENTITIES.                                   "save_modified -> READ ENTITIES -> runtime error
    zcl_rap_r17_trace_###=>gv_provoke_late_read = abap_false.
    out->write( |not reached? sy-subrc = { sy-subrc }| ).
  ENDMETHOD.
```

출력 예시

```
=== 10 WITH CHANGES and current phase (early save, simulation) ===
modify failed 0
simulation sy-subrc = 0
  trace: [PROC augment] create=1 update=0 augmented=1
  trace: [BASE r17TraceChanges] phase=EARLY_SAVE handler_kind=... root=ZRAP_R_TRAVEL_### from_projection=... privileged= draft_activate=
  trace:   TravelID= pid?=X %chg=create Description changed=X BookingFee changed=X BookingFee=20.00
  trace:   TravelID=00000001 pid?= %chg=update Description changed= BookingFee changed=X BookingFee=31.00
  trace:   WITH CHANGES failed: 0
```

해설
- **`WITH CHANGES`**(9.17): 결과 타입은 `TYPE TABLE FOR READ CHANGES`, 추가 컴포넌트 `%chg`가 이 트랜잭션에서 누적된 연산(`if_abap_behv=>cop-create / update / recreate …`)을 알려 줍니다. `%control`은 `%chg`가 create/update/recreate일 때만 "바뀐 필드"를 표시합니다. 제약: managed BO만, 구현 클래스 안에서만, 반드시 `IN LOCAL MODE`와 함께, 연관 읽기·함수에는 불가(08 치트시트). 그래서 콘솔이나 프로젝션 행동 풀이 아니라 **기본 BO의 핸들러** 안에 넣었습니다. 동적 EML에서는 `full = if_abap_behv=>typekind-result_chg`로 같은 정보를 받습니다.
- 쓰임새: R-04의 `save_modified`(+ `with full data`)는 저장 순간 바뀐 필드를 알려 주지만 late save라 무엇을 거부할 수 없습니다. `WITH CHANGES`는 early save(검증·결정)에서 "이 인스턴스가 이번에 새로 생겼나, 어떤 필드가 바뀌었나"를 보고 판단할 수 있게 합니다. 예: "생성 후 상태를 바꾼 경우에만 승인자 지정 필수".
- 새 Travel의 `BookingFee changed = X`인 이유: 사용자는 보내지 않았지만 처리자 augment가 보강했기 때문입니다. augment분도 기본 BO 입장에서는 그냥 변경입니다.
- 삭제된 인스턴스의 `%chg` 값 상수 이름(`cop-delete`)은 치트시트에 나오지 않아 `ELSE` 가지로 숫자를 출력하게 했습니다(실제 시스템에서 F2로 `if_abap_behv=>cop` 확인).
- `FIELDS ( ... )`와 `WITH CHANGES`의 조합은 치트시트 예제가 `ALL FIELDS`만 보여 줘서 확인하지 못했습니다. 구문 오류가 나면 `ALL FIELDS`로 바꾸세요(실제 시스템에서 확인 필요).
- **`get_current_phase`**(7.92): 22 치트시트 예제처럼 "INTERACTION, EARLY_SAVE 등"을 돌려줍니다. 같은 헬퍼 메서드를 핸들러(인터랙션)와 검증(early save) 양쪽에서 부를 때, 단계에 따라 금지 문장을 피하는 데 씁니다. `get_current_context`는 "누가 어떤 방식으로 불렀나"(로컬 모드, 프로젝션·인터페이스 경유, privileged, draft 활성화 중 등), `get_current_handler_kind`는 현재 메서드 종류(읽기·수정 등, 고정값은 `abp_behv_kind`)와 루트 엔터티 이름입니다.
- **late save 읽기 금지**(9.12): late save(`adjust_numbers`, `save`, `save_modified`)는 버퍼가 이미 확정되어 DB로 내려가는 단계라 EML 읽기 자체가 금지됩니다. 필요한 데이터는 `with full data`로 받거나 early save에서 미리 준비하세요. 위반이 구문 검사에서 걸리는지 런타임 오류로만 걸리는지, 그리고 런타임 오류 이름은 확인하지 못했습니다(R-04 1단계의 `BEHAVIOR_ILLEGAL_STMT_IN_CALL` 계열로 예상, 실제 시스템에서 확인 필요).
- 검증은 실패를 넣지 않으므로 업무에 영향이 없고, 추적 스위치가 꺼진 평소에는 `CHECK`에서 바로 끝납니다. 실습 후 지우고 싶으면 BDEF 두 줄과 메서드를 함께 지우세요.

클래스 구조 해설
- `FOR VALIDATE ON SAVE`: early save의 `check_before_save` 시점에 프레임워크가 부르며, `keys`에는 트리거(create/update/delete)에 해당한 인스턴스만 옵니다. draft BO라 `keys`에 `%is_draft`가 있고, `Prepare`에 넣었으므로 draft의 Prepare/Activate 때도 실행됩니다.
- `TYPE TABLE FOR READ CHANGES zrap_r_travel_###`: 일반 `READ RESULT` 타입 + `%chg` + `%control`.

</details>

#### 11단계. 파생 타입 심화와 계약 검사: RTTS, 보조 키, `BEHAVIOR_BAD_HANDLER_RESPONSE`

요구사항
1. 콘솔에 `m11_rtts`를 추가하세요.
   - `cl_abap_tabledescr=>get_bdef_derived_type`으로 처리자 프로젝션의 CREATE 표 타입을 엔터티 이름 문자열만으로 만들고, 정적 타입 `TYPE TABLE FOR CREATE zrap_c_travel_proc_###`와 호환되는지 확인하세요.
   - 그 타입의 줄 구조 컴포넌트 이름을 출력하고 `SHORTNOTE`가 있는지 보세요(field ( modify )).
   - 같은 방법으로 승인자 프로젝션의 UPDATE 표 타입을 만들어 `CREATEDBY`가 없는지(suppress), 기본 BO UPDATE 타입에는 있는지 비교하세요.
   - `get_base_type`으로 "파생 타입을 다시 이름 붙인 타입"의 원래 BDEF 파생 타입 이름을 출력하세요.
   - 동적으로 만든 CREATE 표에 한 줄을 채워 `MODIFY ENTITIES OPERATIONS`로 처리자 BO에 생성 요청을 보내고(augment가 도는지 추적으로 확인), `ROLLBACK ENTITIES`.
2. 콘솔에 `m11_secondary_keys`를 추가하세요.
   - 미리 정의된 보조 키: `TYPE TABLE FOR CREATE` 표에서 `KEY cid`로 `%cid` 찾기
   - 사용자 정의 보조 키: `TYPE TABLE FOR READ RESULT zrap_r_travel_###`에 `OverallStatus` 보조 키를 붙인 타입을 선언하고, 그 표로 EML 결과를 받은 뒤 `USING KEY`로 상태 O만 반복
3. 승인자 `requestRevision`의 "11단계 블록" 자리에 계약 위반 실험 코드를 넣으세요(`gv_bad_response`가 `S`면 액션 응답에 `%state_area`를 넣은 메시지, `F`면 요청에 없던 키를 `failed`에 넣음). 콘솔에 `m11_contract_check( iv_mode )`를 추가하고 `main`에는 주석 처리된 호출로 두세요.

**확인**
- `m11_rtts`: 호환 `X`, 처리자 CREATE 컴포넌트에 `SHORTNOTE`, 승인자 UPDATE에 `CREATEDBY` 없음(`abap_false`), 기본 BO UPDATE에 있음(`X`), 기본 타입 이름 출력, 동적 생성 `failed 0` + 추적 `[PROC augment] create=1 …`.
- `m11_secondary_keys`: `KEY cid`로 찾은 줄의 `AgencyID`, 상태 O인 Travel만 출력.
- 계약 실험: 호출 주석을 풀고 `S`로 실행 → 런타임 오류 `BEHAVIOR_BAD_HANDLER_RESPONSE`(Runtime Errors 뷰에서 확인). `F`도 같은 방식으로 확인. 확인 후 다시 주석 처리합니다.

<details><summary>정답·해설</summary>

승인자 `requestRevision`의 마지막 주석(`"--- 11단계 계약 검사 실험용 블록 ...`)을 다음으로 바꿉니다:

```abap
    "--- R-17 step 11: contract check experiments (off unless the console sets the switch) ---
    CASE zcl_rap_r17_trace_###=>gv_bad_response.
      WHEN 'S'.
        "state messages (%state_area) belong to validations / determine actions, not to an action response
        APPEND VALUE #( %tky        = keys[ 1 ]-%tky
                        %state_area = 'R17'
                        %msg        = NEW zcm_rap_###( textid    = zcm_rap_###=>revision_requested
                                                       severity  = if_abap_behv_message=>severity-information
                                                       travel_id = keys[ 1 ]-TravelID ) ) TO reported-travelappr.
      WHEN 'F'.
        "failed entry for an instance that was not in the request
        APPEND VALUE #( TravelID    = '99999999'
                        %fail-cause = if_abap_behv=>cause-unspecific ) TO failed-travelappr.
    ENDCASE.
```

콘솔 정의부에 추가:

```abap
    METHODS m11_rtts           IMPORTING out TYPE REF TO if_oo_adt_classrun_out.
    METHODS m11_secondary_keys IMPORTING out TYPE REF TO if_oo_adt_classrun_out.
    METHODS m11_contract_check IMPORTING out     TYPE REF TO if_oo_adt_classrun_out
                                         iv_mode TYPE c.
```

`main`에 추가:

```abap
    m11_rtts( out ).
    m11_secondary_keys( out ).
    "m11_contract_check( out = out iv_mode = 'S' ).   "dumps on purpose
    "m11_contract_check( out = out iv_mode = 'F' ).   "dumps on purpose
```

콘솔 구현부에 추가:

```abap
  METHOD m11_rtts.
    out->write( `=== 11-1 RTTS: get_bdef_derived_type ===` ).

    "(1) processor CREATE table type from the entity name only
    DATA static_create TYPE TABLE FOR CREATE zrap_c_travel_proc_###.
    DATA dref_create   TYPE REF TO data.

    DATA(tdo_proc_create) = cl_abap_tabledescr=>get_bdef_derived_type(
                              p_entity = 'ZRAP_C_TRAVEL_PROC_###'
                              p_kind   = abp_bdef_derived_type-create ).
    CREATE DATA dref_create TYPE HANDLE tdo_proc_create.
    out->write( |processor CREATE compatible with static type: { tdo_proc_create->applies_to_data( static_create ) }| ).

    DATA(proc_line) = CAST cl_abap_structdescr( tdo_proc_create->get_table_line_type( ) ).
    DATA(proc_components) = proc_line->get_components( ).
    LOOP AT proc_components INTO DATA(comp).
      out->write( |  component { comp-name }{ COND string( WHEN comp-as_include = abap_true THEN ` (group/include)` ) }| ).
    ENDLOOP.
    out->write( |processor CREATE has SHORTNOTE: { xsdbool( line_exists( proc_line->components[ name = 'SHORTNOTE' ] ) ) }| ).

    "(2) suppress: approver UPDATE vs base UPDATE   (abp_bdef_derived_type-update: 실제 시스템에서 확인 필요)
    DATA(appr_line) = CAST cl_abap_structdescr(
                        cl_abap_tabledescr=>get_bdef_derived_type( p_entity = 'ZRAP_C_TRAVEL_APPR_###'
                                                                   p_kind   = abp_bdef_derived_type-update
                                                                 )->get_table_line_type( ) ).
    DATA(base_line) = CAST cl_abap_structdescr(
                        cl_abap_tabledescr=>get_bdef_derived_type( p_entity = 'ZRAP_R_TRAVEL_###'
                                                                   p_kind   = abp_bdef_derived_type-update
                                                                 )->get_table_line_type( ) ).
    out->write( |approver UPDATE has CREATEDBY: { xsdbool( line_exists( appr_line->components[ name = 'CREATEDBY' ] ) ) }| ).
    out->write( |base     UPDATE has CREATEDBY: { xsdbool( line_exists( base_line->components[ name = 'CREATEDBY' ] ) ) }| ).

    "(3) get_base_type: from an alias type back to the BDEF derived type
    TYPES ty_proc_create    TYPE TABLE FOR CREATE zrap_c_travel_proc_###.
    TYPES ty_my_proc_create TYPE ty_proc_create.
    DATA(tdo_alias) = CAST cl_abap_datadescr( cl_abap_typedescr=>describe_by_name( 'TY_MY_PROC_CREATE' ) ).
    out->write( |alias type { tdo_alias->absolute_name } -> base type { tdo_alias->get_base_type( )->absolute_name }| ).

    "(4) use the dynamically created table in dynamic EML (the processor augment runs, too)
    FIELD-SYMBOLS <create_tab> TYPE STANDARD TABLE.
    ASSIGN dref_create->* TO <create_tab>.
    APPEND INITIAL LINE TO <create_tab> ASSIGNING FIELD-SYMBOL(<line>).

    DATA(today) = cl_abap_context_info=>get_system_date( ).
    TYPES: BEGIN OF ty_value,
             name  TYPE string,
             value TYPE string,
           END OF ty_value.
    DATA values TYPE STANDARD TABLE OF ty_value WITH EMPTY KEY.
    values = VALUE #( ( name = `AGENCYID`     value = `070001` )
                      ( name = `CUSTOMERID`   value = `000001` )
                      ( name = `BEGINDATE`    value = CONV string( today + 30 ) )
                      ( name = `ENDDATE`      value = CONV string( today + 40 ) )
                      ( name = `CURRENCYCODE` value = `EUR` )
                      ( name = `SHORTNOTE`    value = `dynamic RTTS` ) ).

    ASSIGN COMPONENT '%CID' OF STRUCTURE <line> TO FIELD-SYMBOL(<cid>).
    <cid> = 'DYN1'.
    ASSIGN COMPONENT '%CONTROL' OF STRUCTURE <line> TO FIELD-SYMBOL(<control>).
    LOOP AT values INTO DATA(v).
      ASSIGN COMPONENT v-name OF STRUCTURE <line> TO FIELD-SYMBOL(<field>).
      <field> = v-value.
      ASSIGN COMPONENT v-name OF STRUCTURE <control> TO FIELD-SYMBOL(<flag>).
      <flag> = if_abap_behv=>mk-on.
    ENDLOOP.

    DATA op_modify TYPE abp_behv_changes_tab.
    op_modify = VALUE #( ( op          = if_abap_behv=>op-m-create
                           entity_name = 'ZRAP_C_TRAVEL_PROC_###'
                           instances   = dref_create ) ).
    MODIFY ENTITIES OPERATIONS op_modify
      MAPPED DATA(dyn_mapped)
      FAILED DATA(dyn_failed)
      REPORTED DATA(dyn_reported).
    out->write( |dynamic create via processor projection: failed { lines( dyn_failed ) }| ).

    ROLLBACK ENTITIES.
    print_trace( out ).
  ENDMETHOD.


  METHOD m11_secondary_keys.
    out->write( `=== 11-2 secondary table keys of BDEF derived types ===` ).

    "(1) predefined keys: cid, entity, draft, pid (alias id) - see F2 on the type
    DATA create_tab TYPE TABLE FOR CREATE zrap_c_travel_proc_###.
    create_tab = VALUE #( ( %cid = 'K1' AgencyID = '070001' )
                          ( %cid = 'K2' AgencyID = '070002' ) ).
    DATA(by_cid) = create_tab[ KEY cid COMPONENTS %cid = 'K2' ].
    out->write( |KEY cid 'K2' -> AgencyID { by_cid-AgencyID }| ).

    "(2) own secondary key on a BDEF derived type (release 9.14; 실제 시스템에서 확인 필요)
    TYPES ty_travels TYPE TABLE FOR READ RESULT zrap_r_travel_###
                     WITH NON-UNIQUE SORTED KEY by_status COMPONENTS OverallStatus.
    DATA travels TYPE ty_travels.

    READ ENTITIES OF zrap_r_travel_###
      ENTITY Travel
        FIELDS ( OverallStatus TotalPrice CurrencyCode )
        WITH VALUE #( ( TravelID = mv_eur_id ) ( TravelID = mv_other_id ) )
      RESULT travels.

    LOOP AT travels INTO DATA(t) USING KEY by_status WHERE OverallStatus = 'O'.
      out->write( |open travel { t-TravelID }: { t-TotalPrice } { t-CurrencyCode }| ).
    ENDLOOP.
  ENDMETHOD.


  METHOD m11_contract_check.
    out->write( |=== 11-3 contract check, mode { iv_mode } (expect BEHAVIOR_BAD_HANDLER_RESPONSE) ===| ).
    zcl_rap_r17_trace_###=>gv_bad_response = iv_mode.

    MODIFY ENTITIES OF zrap_c_travel_appr_###
      ENTITY TravelAppr
        EXECUTE requestRevision
        FROM VALUE #( ( TravelID = mv_eur_id  %param-revision_note = 'Contract check' ) )
      FAILED DATA(failed)
      REPORTED DATA(reported).

    zcl_rap_r17_trace_###=>gv_bad_response = ' '.
    out->write( |not reached? failed { lines( failed-travelappr ) }| ).
    ROLLBACK ENTITIES.
  ENDMETHOD.
```

출력 예시(일부)

```
=== 11-1 RTTS: get_bdef_derived_type ===
processor CREATE compatible with static type: X
  component %CID
  component %KEY (group/include)
  component %DATA (group/include)
  component %CONTROL
  ...
processor CREATE has SHORTNOTE: X
approver UPDATE has CREATEDBY:
base     UPDATE has CREATEDBY: X
alias type \TYPE=TY_MY_PROC_CREATE... -> base type \BDEF=ZRAP_C_TRAVEL_PROC_###\TYPE=CREATE...
dynamic create via processor projection: failed 0
  trace: [PROC augment] create=1 update=0 augmented=1
=== 11-2 secondary table keys of BDEF derived types ===
KEY cid 'K2' -> AgencyID 070002
open travel 00000004: 2210.00 EUR
```

(컴포넌트 이름, 절대 타입 이름의 정확한 모양은 시스템이 만든 대로 나옵니다. 위는 모양을 보여 주는 예시입니다.)

해설
- **`get_bdef_derived_type`**(9.14): `cl_abap_tabledescr`(표 타입)와 `cl_abap_structdescr`(구조 타입)에 있고, `p_entity`(엔터티 이름 대문자)와 `p_kind`(`abp_bdef_derived_type-create` 등)를 받습니다(08·06 치트시트). R-12 9단계는 기본 BO에 대해 호환성만 확인했고, 여기서는 **프로젝션마다 파생 타입이 다르다**는 것을 눈으로 확인합니다: `field ( modify )`로 연 가상 요소는 처리자 타입에 생기고, `field ( suppress )`한 필드는 승인자 타입에서 사라집니다. `-update` 외의 다른 `p_kind` 상수 이름은 F2로 `abp_bdef_derived_type`을 열어 확인하세요(치트시트는 `-create`만 보여 줌).
- `get_components( )`는 묶음(`%key`, `%data` 같은 그룹)을 한 줄로 보여 주고, `components` 속성은 펼친 이름 목록을 줍니다. 그래서 존재 여부는 `components`로 검사했습니다(그룹이 include로 펼쳐진다고 보고 쓴 코드입니다. 결과가 다르면 `get_components`를 재귀로 따라가세요).
- **`get_base_type`**: 08 치트시트 예제처럼 파생 타입을 다른 이름으로 다시 선언한 타입에서 원래의 BDEF 파생 타입(또는 DDIC 타입)을 돌려줍니다. 공통 유틸리티가 "이 표가 어느 BO의 어떤 연산 타입인가"를 판단할 때 씁니다.
- **동적 EML + RTTS**: 엔터티 이름만 알고 정적 타입을 쓸 수 없는 범용 코드(예: 업로드 도구)에서, 타입 생성(RTTS) → 값 채우기(ASSIGN COMPONENT) → 실행(OPERATIONS)으로 연결됩니다. 프로젝션 이름으로 보냈으므로 처리자 augment도 똑같이 실행됩니다.
- **보조 키**: 파생 타입 표는 기본 키가 비어 있는 표준 표이고, `entity`, `cid`, `draft`, `pid`(별칭 `id`) 같은 정렬 보조 키가 미리 붙어 있습니다(08 치트시트). 키를 지정하지 않은 표 식은 구문 경고가 납니다. 9.14부터는 **자기 보조 키**를 붙일 수 있다고 Release News에 있으나, 정확한 선언 문법 예제는 찾지 못했습니다. 위 `TYPES ... TYPE TABLE FOR READ RESULT ... WITH NON-UNIQUE SORTED KEY ...`는 일반 표 타입의 보조 키 문법을 그대로 붙인 형태입니다(실제 시스템에서 확인 필요). 오류가 나면 F1에서 "BDEF derived types secondary key"를 찾아보세요.
- `KEY cid COMPONENTS %cid = 'K2'`: 정렬 키는 앞쪽 컴포넌트만 지정해도 찾을 수 있습니다. 이 타입의 `cid` 키에 다른 컴포넌트(`%key`, `%pid`)도 들어 있다면 08 치트시트 예제처럼 함께 지정해도 됩니다.
- **계약 검사**(9.14 새 검사): 핸들러가 RAP BO 계약에 맞지 않는 응답을 돌려주면 런타임 오류 `BEHAVIOR_BAD_HANDLER_RESPONSE`가 납니다. Release News에 적힌 경우는 (1) `failed`에 허용되지 않는 항목, (2) `failed`에 잘못된 실패 원인, (3) 여러 문맥에서 `reported`에 비어 있지 않은 `%state_area`. 실험 `S`는 (3), 실험 `F`는 (1)에 해당한다고 보고 만들었습니다. 정확히 어떤 항목이 (1)·(2)로 판정되는지와, 계약 검사가 어떤 실행 환경에서 켜지는지는 확인하지 못했습니다(실제 시스템에서 확인 필요). 7.94부터는 ABAP Unit 테스트 중 계약 위반이 테스트 실패로 드러난다고 합니다(R-13 테스트로도 재현해 볼 수 있습니다).
- 계약을 지키는 법(정답 코드 전체에서 지킨 규칙): `failed`/`reported`에는 **요청에 들어온 인스턴스만**(`%tky`, `%cid`로 지정) 넣기, 실패 원인은 상황에 맞게(없음 → `not_found`, 기능 제어 → `disabled`, 권한 → `unauthorized`, 잠금 → `locked`), `%state_area`는 검증·determine action에서만.

</details>

## 출처

- SAP-samples/abap-cheat-sheets — 08_EML_ABAP_for_RAP.md (WITH CHANGES, AUGMENTING, Secondary Table Keys of BDEF Derived Types, RAP-Related System Classes: `cl_abap_behv_aux`, `get_bdef_derived_type`, `get_base_type`): https://github.com/SAP-samples/abap-cheat-sheets/blob/main/08_EML_ABAP_for_RAP.md
- SAP-samples/abap-cheat-sheets — 33_ABAP_Release_News.md (기능별 도입 릴리스): https://github.com/SAP-samples/abap-cheat-sheets/blob/main/33_ABAP_Release_News.md
- SAP-samples/abap-cheat-sheets — 36_RAP_Behavior_Definition_Language.md (`field ( suppress )`, `deep parameter` / `deep result`, 검증 트리거): https://github.com/SAP-samples/abap-cheat-sheets/blob/main/36_RAP_Behavior_Definition_Language.md
- SAP-samples/abap-cheat-sheets — 22_Released_ABAP_Classes.md (`CL_ABAP_BEHV_AUX`: `get_current_context`, `get_current_handler_kind`, `get_current_phase`): https://github.com/SAP-samples/abap-cheat-sheets/blob/main/22_Released_ABAP_Classes.md
- SAP-samples/abap-cheat-sheets — 06_Dynamic_Programming.md (`get_bdef_derived_type`): https://github.com/SAP-samples/abap-cheat-sheets/blob/main/06_Dynamic_Programming.md
- SAP-samples/abap-platform-refscen-flight (ABAP-platform-cloud) — managed 처리자/승인자 프로젝션 `/DMO/C_Travel_Processor_M`, `/DMO/C_Travel_Approver_M`(BDEF, CDS): https://github.com/SAP-samples/abap-platform-refscen-flight/tree/ABAP-platform-cloud/src/managed
- SAP-samples/abap-platform-refscen-flight (ABAP-platform-cloud) — draft BO `/DMO/R_Travel_D`, 인터페이스 `/DMO/I_Travel_D`(`with privileged mode`), draft 없는 승인자 프로젝션 `/DMO/C_Travel_A_D`, `/DMO/C_Travel_D_D`: https://github.com/SAP-samples/abap-platform-refscen-flight/tree/ABAP-platform-cloud/src/draft
- SAP-samples/abap-platform-refscen-flight (ABAP-platform-cloud) — augment 예제 `/DMO/C_Supplement`(BDEF `use create ( augment )`, `field ( modify )`), `/DMO/BP_C_SUPPLEMENT`(`augment FOR MODIFY`, `MODIFY AUGMENTING ENTITIES ... RELATING TO ... BY`): https://github.com/SAP-samples/abap-platform-refscen-flight/tree/ABAP-platform-cloud/src/reuse/supplement
- SAP-samples/abap-platform-refscen-flight (ABAP-platform-cloud) — `/DMO/C_TravelTP_CD`(`projection implementation in class`): https://github.com/SAP-samples/abap-platform-refscen-flight/tree/ABAP-platform-cloud/src/colldraft
- SAP-samples/abap-partner-reference-application — `ZPRA_MF_C_MusicFestivalTP`, `ZPRA_MF_C_VisitorTP` 프로젝션 BDEF(`projection implementation in class ... unique`): https://github.com/SAP-samples/abap-partner-reference-application
- SAP-samples/teched2025-DT266 — `ZC_DT266_CARR_000` 프로젝션 BDEF: https://github.com/SAP-samples/teched2025-DT266
- SAP-samples/abap-platform-rap-transactional-outbox-with-bgpf — `ZC_ORDER000` 프로젝션 BDEF: https://github.com/SAP-samples/abap-platform-rap-transactional-outbox-with-bgpf
- (커뮤니티, SAP 공식 아님) IlyaPrusakou/abap-rap-example — 프로젝션·인터페이스 BDEF의 `with managed instance filter`, `use create ( augment, precheck )`, 프로젝션 전용 `action`/`static function`, `deep parameter`/`deep result` 재정의, `field ( suppress )`, 추상 BDEF `deep mapping for`, 프로젝션 행동 풀(augment, precheck, 새 액션·함수 구현): https://github.com/IlyaPrusakou/abap-rap-example
- (커뮤니티) mainakaich/YMAINAK — 프로젝션 BDEF `with managed instance filter;`와 프로젝션 뷰 WHERE: https://github.com/mainakaich/YMAINAK
- (커뮤니티) IlyaPrusakou/abap-rap-eml-templates — `FORWARDING PRIVILEGED`의 문장 내 위치: https://github.com/IlyaPrusakou/abap-rap-eml-templates
- (커뮤니티) pallavar/ROCHEAUX_ZCUSTOMDEV — `MODIFY ENTITIES OF ... FORWARDING PRIVILEGED` 실사용 예: https://github.com/pallavar/ROCHEAUX_ZCUSTOMDEV
