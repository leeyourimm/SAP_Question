## 5. 고급·특수 기능 보충

### R-18. RAP 도구와 연동: 생성기, 외부 OData 소비, Fiori 앱 배포, 백그라운드 작업 [작성] ★★★
<!-- covers: Generate ABAP Repository Objects, OData UI Service 생성기, ##GENERATED, 생성 코드 읽기, Service Consumption Model, OData 클라이언트 프록시, /iwbep/cl_cp_factory_remote, create_v2_remote_proxy, cl_web_odata_client_factory, cl_http_destination_provider create_by_url, create_by_comm_arrangement, create_by_cloud_destination, cl_web_http_client_manager, communication scenario, communication system, communication arrangement, outbound service, /iwbep/if_cp_request_read_list, filter factory create_by_range, set_top, set_skip, request_count, custom entity 원격 데이터, if_rap_query_provider, value help custom entity, Application Log Object, cl_bali_log, cl_bali_header_setter, cl_bali_free_text_setter, cl_bali_log_db, cl_bali_log_filter, with additional save, save_modified, bgPF, cl_bgmc_process_factory, if_bgmc_op_single, if_serializable_object, controlled SAP LUW, application job, if_apj_rt_run, if_apj_dt_exec_object, if_apj_rt_exec_object, Application Job Catalog Entry, Application Job Template, cl_apj_rt_api schedule_job, get_job_status, cl_apj_dt_create_content, EML in background, COMMIT ENTITIES RESPONSE OF, %fail-cause locked, SAP Business Application Studio, Fiori elements List Report 생성, npm run deploy, IAM App, Business Catalog, Business Role, Fiori launchpad, 트라이얼 제약 -->

**목표**
- ADT의 **Generate ABAP Repository Objects** 생성기로 테이블 하나에서 OData V4 UI 서비스 전체(기본 뷰, 프로젝션 뷰, 메타데이터 확장, BDEF, 행동 풀, draft 테이블, 서비스 정의·바인딩)를 만들고, 생성된 코드를 R-01에서 손으로 만든 코드와 줄 단위로 비교해 읽을 수 있습니다.
- **Service Consumption Model**로 원격 OData 서비스의 클라이언트 프록시를 만들고, HTTP 목적지(destination)·통신 시나리오·통신 시스템·통신 약정(arrangement)이 각각 무슨 역할인지 설명하고, 원격 데이터를 custom entity로 감싸 Fiori 값 도움말로 쓸 수 있습니다.
- 애플리케이션 로그(`cl_bali_log`)를 `with additional save`의 `save_modified`에서 쓰고, 백그라운드 처리 프레임워크(bgPF, `cl_bgmc_process_factory`)로 **커밋이 끝난 뒤** 무거운 일을 비동기로 돌릴 수 있습니다.
- 애플리케이션 잡(Application Job) 클래스에서 EML + `COMMIT ENTITIES`로 RAP BO를 바꾸고, 잡 카탈로그·템플릿을 만들어 `cl_apj_rt_api`로 예약하고 결과를 로그로 확인할 수 있습니다.
- SAP Business Application Studio(BAS)에서 Fiori elements 앱을 만들어 ABAP 환경에 배포하고 런치패드에 올리는 전체 흐름(IAM 앱, 비즈니스 카탈로그, 비즈니스 역할)을 설명하고, 트라이얼에서 어디까지 되는지 구분할 수 있습니다.

**전제**
- SAP BTP ABAP Environment(Trial), ADT, 패키지 `ZRAP_###`. R-01(수작업 Travel BO)과 R-08(custom entity, `if_rap_query_provider`)을 먼저 풀어 두면 비교가 쉽습니다. R-04에서 `with additional save`와 `save_modified`를 이미 다뤘습니다.
- 기존 Travel BO를 건드리지 않도록 이 문제는 **전용 작은 BO "작업(Task)"** 을 생성기로 만듭니다. 이름은 `ZRAP_..._GTASK_###`(G = Generated) 계열입니다.
- 원격 OData는 SAP 공개 데모 시스템 ES5의 인증 없는 서비스 `ZAGENCYCDS_SRV`(여행사 목록)를 씁니다. openSAP RAP 과정과 RAP620 워크숍이 트라이얼용으로 쓴 서비스입니다. ES5가 응답하지 않으면 4~6단계는 "읽고 구조만 따라 하기"로 진행하세요.
- 트라이얼은 **공유 시스템**이고 사용자에게 관리자(Administrator) 역할이 없습니다. 그래서 통신 약정·비즈니스 역할처럼 Fiori 관리 앱이 필요한 작업은 대부분 직접 못 합니다. 각 단계에 "트라이얼 제약"을 따로 적었습니다.

**만들 객체**

| 순서 | 객체 유형 | 이름 | 역할 |
|---|---|---|---|
| 1 | 데이터베이스 테이블 | `ZRAP_GTASK_###` | 작업(Task) 활성 데이터 |
| 2 | ABAP 클래스 | `ZCL_RAP_GTASK_DATA_###` | 데모 데이터 콘솔 클래스 |
| 3 | (생성기) CDS 뷰 엔터티 + BDEF | `ZRAP_R_GTASK_###` | 기본 BO 루트 엔터티 `Task` |
| 4 | (생성기) draft 테이블 | `ZRAP_DGTASK_###` | draft 데이터 |
| 5 | (생성기) 행동 풀 | `ZBP_RAP_R_GTASK_###` | 권한 → 이후 액션·세이버 추가 |
| 6 | (생성기) 프로젝션 뷰 + BDEF + MDE | `ZRAP_C_GTASK_###` | UI용 프로젝션, UI 어노테이션 |
| 7 | (생성기, 버전에 따라) 프로젝션 행동 풀 | `ZBP_RAP_C_GTASK_###` | 프로젝션 구현(대개 비어 있음) |
| 8 | (생성기) 서비스 정의 / 바인딩 | `ZRAP_UI_GTASK_###` / `ZRAP_UI_GTASK_O4_###` | OData V4 - UI |
| 9 | Service Consumption Model (+ 생성 클래스) | `ZRAP_SC_AGENCY_###` | ES5 OData V2 클라이언트 프록시 |
| 10 | ABAP 클래스 | `ZCL_RAP_CE_AGENCY_###` | 원격 호출 + custom entity 쿼리 구현 |
| 11 | CDS custom entity | `ZRAP_CE_AGENCY_###` | 원격 여행사 목록 엔터티 |
| 12 | Application Log Object | `ZRAP_GTASK_###` (하위 객체 `STATUS`, `JOB`) | 애플리케이션 로그 분류 |
| 13 | ABAP 클래스 | `ZCL_RAP_GTASK_LOG_###` | 로그 읽기 콘솔 클래스 |
| 14 | ABAP 클래스 | `ZCL_RAP_GTASK_BGPF_###` | bgPF 작업(operation) |
| 15 | ABAP 클래스 | `ZCL_RAP_GTASK_JOB_###` | 애플리케이션 잡 실행 클래스 |
| 16 | Application Job Catalog Entry / Template | `ZRAP_GTASK_JC_###` / `ZRAP_GTASK_JT_###` | 잡 정의 / 기본 파라미터 |
| 17 | ABAP 클래스 | `ZCL_RAP_GTASK_SCHED_###` | 잡 예약 콘솔 클래스 |
| 18 | (BAS) Fiori elements 앱, IAM 앱, 비즈니스 카탈로그 | `ztask###`, `ZRAP_GTASK_BC_###` | 배포·런치패드 등록 |

#### 1단계. 전용 테이블과 데모 데이터

요구사항
1. 패키지 `ZRAP_###`에 테이블 `ZRAP_GTASK_###`(설명 `Generated task data`)를 만드세요. 아래 필드 표를 따르세요. 키는 `client`, `task_id`이며, `task_id`는 사용자가 생성할 때 직접 입력합니다(외부 번호 매김, 생성기가 이 경우 어떤 BDEF를 만드는지 3단계에서 봅니다).
2. 헤더 어노테이션: 확장 불가, 투명 테이블, 전달 클래스 A, 데이터 유지 관리 제한.
3. 콘솔 클래스 `ZCL_RAP_GTASK_DATA_###`(인터페이스 `IF_OO_ADT_CLASSRUN`)를 만들어 아래 다섯 건을 넣으세요. 날짜는 실행일 기준 상대값입니다(오늘 = `cl_abap_context_info=>get_system_date( )`).
   - 00000001 `Check hotel contract`, 여행사 070001, 기한 오늘-10일, 상태 O
   - 00000002 `Confirm bus transfer`, 070005, 오늘-1일, O
   - 00000003 `Send visa documents`, 070010, 오늘+5일, O
   - 00000004 `Collect feedback`, 070015, 오늘+30일, O
   - 00000005 `Archive old offers`, 070020, 오늘-3일, D
4. 생성자·변경자 필드는 현재 사용자, 시각 필드는 현재 타임스탬프로 채우고, 실행할 때마다 기존 데이터를 지우고 다시 넣으세요. 마지막에 넣은 건수를 콘솔에 출력하세요.

상태 값: `O` = Open(열림), `D` = Done(완료), `X` = Overdue(기한 초과). 확인 상태(`check_status`): 공백 = 요청 없음, `R` = 백그라운드 확인 요청됨, `F` = 확인 끝남.

`ZRAP_GTASK_###`

| 필드 | 키 | 데이터 엘리먼트 | 타입 | 길이 | 소수 | 설명 |
|---|---|---|---|---|---|---|
| client | ✓ | (내장) abap.clnt | CLNT | 3 | 0 | 클라이언트 |
| task_id | ✓ | (내장) abap.numc | NUMC | 8 | 0 | 작업 번호 (외부 입력) |
| title | | (내장) abap.char | CHAR | 60 | 0 | 작업 제목 |
| agency_id | | /dmo/agency_id | NUMC | 6 | 0 | 여행사 (ES5 원격 여행사 번호와 같은 형식) |
| due_date | | (내장) abap.dats | DATS | 8 | 0 | 기한 |
| status | | (내장) abap.char | CHAR | 1 | 0 | 상태 O/D/X |
| check_status | | (내장) abap.char | CHAR | 1 | 0 | 백그라운드 확인 상태 ' '/R/F |
| remark | | (내장) abap.char | CHAR | 120 | 0 | 비고 (백그라운드 처리 결과) |
| created_by | | abp_creation_user | CHAR | 12 | 0 | 생성자 |
| created_at | | abp_creation_tstmpl | DEC (TIMESTAMPL) | 21 | 7 | 생성 시각 |
| local_last_changed_by | | abp_locinst_lastchange_user | CHAR | 12 | 0 | 인스턴스 최종 변경자 |
| local_last_changed_at | | abp_locinst_lastchange_tstmpl | DEC (TIMESTAMPL) | 21 | 7 | 인스턴스 최종 변경 시각 (ETag) |
| last_changed_at | | abp_lastchange_tstmpl | DEC (TIMESTAMPL) | 21 | 7 | 최종 변경 시각 (total ETag) |

**직접 추가할 어노테이션**
- `@EndUserText.label` — 테이블 설명 문구.
- `@AbapCatalog.enhancement.category` — append로 확장할 수 있는지.
- `@AbapCatalog.tableCategory` — 테이블 종류(투명 테이블).
- `@AbapCatalog.deliveryClass` — 전달 클래스(애플리케이션 데이터).
- `@AbapCatalog.dataMaintenance` — 일반 유지 관리 도구에서 직접 수정할 수 있는지.

**확인**
- 테이블이 활성화되고, 클래스를 F9로 실행하면 콘솔에 `5 tasks inserted.`가 나옵니다.
- 테이블에서 F8(Data Preview)을 누르면 다섯 행이 보이고, 00000001·00000002는 기한이 이미 지났습니다.

<details><summary>정답·해설</summary>

```cds
@EndUserText.label : 'Generated task data'               // 테이블 설명
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE      // append 확장 불가
@AbapCatalog.tableCategory : #TRANSPARENT                // 투명 테이블
@AbapCatalog.deliveryClass : #A                          // 애플리케이션 데이터
@AbapCatalog.dataMaintenance : #RESTRICTED               // 직접 유지 관리 제한
define table zrap_gtask_### {

  key client            : abap.clnt not null;
  key task_id           : abap.numc(8) not null;
  title                 : abap.char(60);
  agency_id             : /dmo/agency_id;
  due_date              : abap.dats;
  status                : abap.char(1);
  check_status          : abap.char(1);
  remark                : abap.char(120);
  created_by            : abp_creation_user;
  created_at            : abp_creation_tstmpl;
  local_last_changed_by : abp_locinst_lastchange_user;
  local_last_changed_at : abp_locinst_lastchange_tstmpl;
  last_changed_at       : abp_lastchange_tstmpl;

}
```

```abap
CLASS zcl_rap_gtask_data_### DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_oo_adt_classrun.
ENDCLASS.


CLASS zcl_rap_gtask_data_### IMPLEMENTATION.

  METHOD if_oo_adt_classrun~main.
    DATA tasks TYPE STANDARD TABLE OF zrap_gtask_### WITH EMPTY KEY.
    DATA now   TYPE timestampl.

    DATA(today) = cl_abap_context_info=>get_system_date( ).
    DATA(user)  = cl_abap_context_info=>get_user_technical_name( ).
    GET TIME STAMP FIELD now.

    tasks = VALUE #(
      ( task_id = '00000001' title = 'Check hotel contract' agency_id = '070001' due_date = today - 10 status = 'O' )
      ( task_id = '00000002' title = 'Confirm bus transfer' agency_id = '070005' due_date = today - 1  status = 'O' )
      ( task_id = '00000003' title = 'Send visa documents'  agency_id = '070010' due_date = today + 5  status = 'O' )
      ( task_id = '00000004' title = 'Collect feedback'     agency_id = '070015' due_date = today + 30 status = 'O' )
      ( task_id = '00000005' title = 'Archive old offers'   agency_id = '070020' due_date = today - 3  status = 'D' ) ).

    LOOP AT tasks ASSIGNING FIELD-SYMBOL(<task>).
      <task>-created_by            = user.
      <task>-created_at            = now.
      <task>-local_last_changed_by = user.
      <task>-local_last_changed_at = now.
      <task>-last_changed_at       = now.
    ENDLOOP.

    DELETE FROM zrap_gtask_###.
    INSERT zrap_gtask_### FROM TABLE @tasks.

    out->write( |{ lines( tasks ) } tasks inserted.| ).
  ENDMETHOD.

ENDCLASS.
```

**왜 이렇게 쓰나**
- 키를 UUID가 아니라 사람이 읽는 번호(`NUMC 8`)로 둔 이유: RAP100 워크숍이 같은 형태의 테이블로 생성기를 돌렸고, 그 결과(키 필드에 `mandatory : create` + `readonly : update`)를 공식 문서로 확인할 수 있기 때문입니다. 생성기가 만든 결과를 "근거 있는 모습"과 비교하려는 목적입니다.
- `agency_id`를 `/dmo/agency_id`(NUMC 6)로 둔 것은 ES5 원격 서비스의 `AgencyId`(최대 6자리 숫자 문자열)와 형식을 맞춰 6단계에서 원격 값 도움말을 붙이기 위해서입니다.
- 관리 필드 `abp_*`는 R-01과 같습니다. 생성기는 이 데이터 엘리먼트를 보고 `@Semantics.user.createdBy` 등 관리 필드 어노테이션과 `etag master`/`total etag`를 자동으로 붙입니다(3단계에서 확인).
- 데모 데이터 클래스는 draft 테이블을 지우지 않습니다. 생성기를 돌린 뒤 다시 실행할 때 남은 draft가 문제를 일으키면 Fiori에서 draft를 버리거나(Discard) draft 테이블 `ZRAP_DGTASK_###`도 `DELETE FROM`으로 지우세요.

</details>

#### 2단계. ADT 생성기로 OData UI 서비스 만들기

요구사항
1. Project Explorer에서 테이블 `ZRAP_GTASK_###`를 우클릭하고 **Generate ABAP Repository Objects**를 고르세요.
2. 생성기 종류로 **OData UI Service**를 고르고 **Next >**, 패키지를 확인하고 **Next >** 하세요(클라우드 시스템 화면 기준).
3. **Configure Generator** 화면의 트리(Business Object > Data Model / Behavior, Service Projection > Service Projection Entity / Service Projection Behavior, Business Service > Service Definition / Service Binding)를 하나씩 눌러 아래 이름으로 **모두 바꾸세요**. 제안값을 그대로 두면 이후 정답 코드와 이름이 달라집니다.

| 계층 | 항목 | 입력값 |
|---|---|---|
| Business Object | Data Model – CDS Entity Name | `ZRAP_R_GTASK_###` |
| | Data Model – CDS Entity Name Alias | `Task` |
| | Behavior – Implementation Behavior Class | `ZBP_RAP_R_GTASK_###` |
| | Behavior – Draft Table Name | `ZRAP_DGTASK_###` |
| Service Projection | Service Projection Entity – CDS Entity Name | `ZRAP_C_GTASK_###` |
| | Service Projection Behavior – Behavior Implementation Class | `ZBP_RAP_C_GTASK_###` |
| Business Service | Service Definition Name | `ZRAP_UI_GTASK_###` |
| | Service Binding Name | `ZRAP_UI_GTASK_O4_###` |
| | Binding Type | `OData V4 - UI` |

4. **Next >** 로 생성될 객체 목록을 확인하고, 전송 요청을 고른 뒤 **Finish** 하세요.
5. 생성이 끝나 서비스 바인딩이 열리면 **Publish**를 누르고, 엔터티 `Task`를 더블클릭해 Fiori elements 미리보기를 여세요.

**확인**
- 패키지에 표의 객체가 모두 생겼습니다(행동 정의 2개, 데이터 정의 2개, 메타데이터 확장 1개, 테이블 1개(draft), 클래스 1~2개, 서비스 정의·바인딩).
- 미리보기에서 **Go**를 누르면 1단계 데이터 다섯 건이 목록에 보이고, 한 건을 열어 **Edit → 값 변경 → Save**가 됩니다. **Create**를 누르면 Task ID를 직접 입력해야 합니다.

<details><summary>정답·해설</summary>

정답 "코드"는 생성기가 만듭니다. 이 단계의 핵심은 **무엇이 어떤 이름으로 생기는지**와 **생성기 화면에서 어디를 바꿔야 하는지**입니다. 생성되는 객체와 역할(RAP100 워크숍 연습 1.4의 설명 표를 이 문제 이름으로 옮김):

| 계층 | 객체 | 역할 |
|---|---|---|
| 기본 BO | 데이터 정의 `ZRAP_R_GTASK_###` | 테이블 위의 루트 뷰 엔터티. 필드 별칭을 CamelCase로 만들고 관리 필드에 `@Semantics` 어노테이션을 붙임 |
| | 행동 정의 `ZRAP_R_GTASK_###` | `managed` + `strict ( 2 )` + `with draft`. CRUD와 draft 액션, `mapping for` |
| | 테이블 `ZRAP_DGTASK_###` | draft 테이블. 런타임에 프레임워크가 관리 |
| | 클래스 `ZBP_RAP_R_GTASK_###` | 행동 풀. 전역 권한 메서드 뼈대만 있음 |
| BO 프로젝션 | 데이터 정의 `ZRAP_C_GTASK_###` | `provider contract transactional_query` 프로젝션 뷰, `@Metadata.allowExtensions: true` |
| | 행동 정의 `ZRAP_C_GTASK_###` | `projection;` + `use draft;` + `use create/update/delete/action ...` |
| | 메타데이터 확장 `ZRAP_C_GTASK_###` | `@UI` 어노테이션(헤더, facet, 목록, 상세, 필터) |
| 비즈니스 서비스 | 서비스 정의 `ZRAP_UI_GTASK_###` | `expose ZRAP_C_GTASK_### as Task;` |
| | 서비스 바인딩 `ZRAP_UI_GTASK_O4_###` | OData V4 - UI로 노출 |

**생성기 종류**: 같은 메뉴 아래에 OData UI Service 외에도 버전에 따라 Web API 서비스, Business Configuration Maintenance Object(R-09 10단계) 같은 다른 생성기가 함께 나옵니다. 또 RAP630 워크숍은 테이블이 아니라 **릴리스된 BO 인터페이스**(`I_BankTP`)를 우클릭해 같은 메뉴로 UI 서비스를 만드는 방법을 보여 줍니다. 즉 "테이블에서 BO 전체" 또는 "기존 BO 위에 프로젝션·서비스만" 두 가지 출발점이 있습니다.

**온프레미스와의 차이**: RAP100 문서는 생성기 화면이 클라우드 시스템과 온프레미스(2022 이하)에서 다르다고 적고 있습니다. 온프레미스 화면에서는 "ABAP RESTful Application Programming Model: UI Service"를 고릅니다. 이 문제는 클라우드(트라이얼) 화면 기준입니다.

**또 다른 생성 방식**: RAP110 워크숍은 ADT 마법사 대신 **콘솔 실행 생성 클래스**(`ZDMO_GEN_RAP110_SINGLE`)로 패키지와 BO 전체를 만들고, RAP630 README는 오픈소스 RAP Generator(SAP-samples/cloud-abap-rap)가 트라이얼에 이미 들어 있다고 안내합니다. 반복 생성·여러 엔터티 생성이 필요할 때 쓰는 방식이며, 이 문제에서는 ADT 마법사만 씁니다.

**자주 나는 오류와 해결**
- 이름 제안을 그대로 두고 Finish 한 경우: 생성된 객체를 지우고 다시 생성하는 편이 이름을 하나씩 바꾸는 것보다 빠릅니다. 지우는 순서는 서비스 바인딩 → 서비스 정의 → 프로젝션 BDEF → MDE → 프로젝션 뷰 → 기본 BDEF → 행동 풀 → 기본 뷰 → draft 테이블입니다(사용처가 남아 있으면 삭제가 거부됩니다).
- RAP100 문서는 특정 ADT 버전에서 "Invalid XML format of the response" 오류가 났고 ADT 업데이트로 해결됐다고 적습니다. 생성기 오류가 나면 먼저 ADT를 최신으로 올리세요.

</details>

#### 3단계. 생성된 코드 읽기: R-01 수작업과 비교하고 조금 손보기

요구사항
1. 생성된 객체를 하나씩 열고(Shift+F1로 서식 정리), 아래 질문에 답을 적으세요.
   - 기본 뷰: 관리 필드 5개에 붙은 `@Semantics` 어노테이션 이름은 각각 무엇인가요? `@EndUserText.label`에 붙은 `##GENERATED`는 무엇을 뜻하나요?
   - 기본 BDEF: `TaskID`에 붙은 필드 특성은 무엇이고 왜 그런가요? `etag master`와 `total etag`는 어느 필드인가요? draft 액션은 몇 개인가요?
   - 프로젝션 뷰: 관리 필드 중 어떤 것이 노출됐나요? `@ObjectModel.semanticKey`는 무엇인가요?
   - 메타데이터 확장: 어떤 필드에 `selectionField`가 붙었나요?
   - 행동 풀: 어떤 메서드가 생겼고, 구현은 무엇인가요?
2. R-01 수작업 Travel BO와 비교해 "생성기가 해 주는 것 / 해 주지 않는 것" 표를 완성하세요(번호 매김, 자식 엔터티, 값 도움말, 텍스트, 검색, 가상 요소, 권한 구현, 검증·결정·액션).
3. 프로젝션 뷰를 손보세요: 검색 가능하게 만들고 `Title`을 기본 검색 대상으로 지정하세요.
4. 메타데이터 확장을 손보세요: `Remark`, `CheckStatus`의 필터 칸(`selectionField`)을 지우고, 헤더 제목을 `Title`로 바꾸세요. 기술 필드 `LocalLastChangedAt`는 화면에 보이지 않아야 합니다.

**직접 추가할 어노테이션**
- `@Search.searchable` — 이 프로젝션 뷰에 자유 텍스트 검색 칸을 켬.
- `@Search.defaultSearchElement` — 검색어를 어느 필드에서 찾을지.
- `@UI.headerInfo` 의 `title` — Object Page 머리글에 어떤 필드 값을 크게 보여 줄지.
- `@UI.hidden` — 필드를 UI에서 숨김(생성기가 이미 붙였는지 확인).

**확인**
- 미리보기 목록 위에 검색 칸이 생기고 `visa`를 입력하면 00000003만 남습니다.
- 필터 영역에 Remark·CheckStatus가 없고, Object Page 머리글에 작업 제목이 보입니다.

<details><summary>정답·해설</summary>

아래는 **RAP100 워크숍의 공식 솔루션 코드(같은 생성기로 만든 뒤 연습에서 고친 것)와 연습 문서의 설명**에서, 연습에서 추가한 부분을 빼고 이 문제 이름으로 옮긴 "생성 직후의 예상 모습"입니다. 생성기 버전에 따라 줄 순서·주석·노출 필드가 조금 다를 수 있으니 **자기 시스템에 생성된 코드를 기준**으로 읽으세요(실제 시스템에서 확인 필요).

기본 뷰 (생성 직후 예상)

```cds
@AccessControl.authorizationCheck: #CHECK                 // 접근 제어(DCL)를 검사하도록 생성됨 → DCL이 없으면 경고
@EndUserText.label: '##GENERATED ZRAP_GTASK_###'          // ##GENERATED: 생성기가 만든 텍스트라는 표시(번역 검사 등에서 구분)
define root view entity ZRAP_R_GTASK_###
  as select from zrap_gtask_### as Task
{
  key task_id               as TaskID,                    // snake_case → CamelCase 별칭, id → ID
      title                 as Title,
      agency_id             as AgencyID,
      due_date              as DueDate,
      status                as Status,
      check_status          as CheckStatus,
      remark                as Remark,
      @Semantics.user.createdBy: true                     // 생성자 자동 기록
      created_by            as CreatedBy,
      @Semantics.systemDateTime.createdAt: true           // 생성 시각 자동 기록
      created_at            as CreatedAt,
      @Semantics.user.localInstanceLastChangedBy: true    // 인스턴스 최종 변경자
      local_last_changed_by as LocalLastChangedBy,
      @Semantics.systemDateTime.localInstanceLastChangedAt: true   // 인스턴스 ETag
      local_last_changed_at as LocalLastChangedAt,
      @Semantics.systemDateTime.lastChangedAt: true       // total ETag
      last_changed_at       as LastChangedAt
}
```

기본 BDEF (생성 직후 예상)

```bdef
managed implementation in class ZBP_RAP_R_GTASK_### unique;
strict ( 2 );
with draft;
define behavior for ZRAP_R_GTASK_### alias Task
persistent table zrap_gtask_###
draft table zrap_dgtask_###
etag master LocalLastChangedAt
lock master total etag LastChangedAt
authorization master ( global )
{
  field ( readonly )
  CreatedAt,
  CreatedBy,
  LastChangedAt,
  LocalLastChangedAt,
  LocalLastChangedBy;

  field ( mandatory : create, readonly : update )
  TaskID;

  create;
  update;
  delete;

  draft action Activate optimized;
  draft action Discard;
  draft action Edit;
  draft action Resume;
  draft determine action Prepare;

  mapping for zrap_gtask_###
    {
      TaskID             = task_id;
      Title              = title;
      AgencyID           = agency_id;
      DueDate            = due_date;
      Status             = status;
      CheckStatus        = check_status;
      Remark             = remark;
      CreatedBy          = created_by;
      CreatedAt          = created_at;
      LocalLastChangedBy = local_last_changed_by;
      LocalLastChangedAt = local_last_changed_at;
      LastChangedAt      = last_changed_at;
    }
}
```

- RAP100 연습 3 문서에 따르면 생성기는 키가 숫자일 때 키 필드를 `field ( mandatory : create )`와 `field ( readonly : update )`로 만듭니다(외부 번호 매김: 생성 때만 입력, 이후 수정 불가). 위에서는 한 줄로 합쳐 적었는데, 생성 결과는 두 문장으로 나뉘어 있을 수 있습니다. 둘은 같은 뜻입니다(BDL cheat sheet: 특성을 괄호 안에 함께 적을 수 있음).
- 관리 필드는 `field ( readonly )`로 묶여 생성됩니다. 값은 `@Semantics` 어노테이션 덕분에 프레임워크가 채웁니다.

draft 테이블 (생성 직후 예상, R-01 8단계와 같은 형태)

```cds
@EndUserText.label : 'Draft table for entity ZRAP_R_GTASK_###'
@AbapCatalog.enhancement.category : #EXTENSIBLE_ANY
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table zrap_dgtask_### {

  key mandt          : mandt not null;
  key taskid         : abap.numc(8) not null;
  title              : abap.char(60);
  agencyid           : /dmo/agency_id;
  duedate            : abap.dats;
  status             : abap.char(1);
  checkstatus        : abap.char(1);
  remark             : abap.char(120);
  createdby          : abp_creation_user;
  createdat          : abp_creation_tstmpl;
  locallastchangedby : abp_locinst_lastchange_user;
  locallastchangedat : abp_locinst_lastchange_tstmpl;
  lastchangedat      : abp_lastchange_tstmpl;
  "%admin"           : include sych_bdl_draft_admin_inc;   // draft 관리 정보

}
```

draft 테이블의 헤더 어노테이션 값(`#EXTENSIBLE_ANY` 등)과 클라이언트 필드 이름은 생성 결과를 그대로 두세요. 직접 고치지 말고, 기본 뷰에 필드를 추가했다면 BDEF의 `draft table` 줄에서 퀵 픽스(Ctrl+1)로 **다시 생성**하는 것이 원칙입니다.

행동 풀 (생성 직후 예상)

```abap
CLASS zbp_rap_r_gtask_### DEFINITION
  PUBLIC
  ABSTRACT
  FINAL
  FOR BEHAVIOR OF zrap_r_gtask_###.
ENDCLASS.

CLASS zbp_rap_r_gtask_### IMPLEMENTATION.
ENDCLASS.
```

```abap
CLASS lhc_task DEFINITION INHERITING FROM cl_abap_behavior_handler.
  PRIVATE SECTION.
    METHODS get_global_authorizations FOR GLOBAL AUTHORIZATION
      IMPORTING REQUEST requested_authorizations FOR Task RESULT result.
ENDCLASS.

CLASS lhc_task IMPLEMENTATION.
  METHOD get_global_authorizations.
  ENDMETHOD.
ENDCLASS.
```

`get_global_authorizations`가 비어 있으면 `result`에 "금지" 표시가 하나도 없으므로 **모든 작업이 허용**됩니다. 생성기는 권한 **뼈대만** 만들고 판단 로직은 개발자 몫으로 남깁니다(R-02/R-03에서 다룬 권한 구현이 여기에 들어갑니다).

프로젝션 뷰 (3번 요구사항 반영 후)

```cds
@AccessControl.authorizationCheck: #CHECK
@Metadata.allowExtensions: true                         // UI 어노테이션은 메타데이터 확장에 둠
@EndUserText.label: '##GENERATED ZRAP_GTASK_###'
@Search.searchable: true                                // [추가] 자유 텍스트 검색 켜기
@ObjectModel.semanticKey: [ 'TaskID' ]                  // 사람이 읽는 키: UI가 굵게 표시하고 draft 표시와 함께 씀
define root view entity ZRAP_C_GTASK_###
  provider contract transactional_query                 // 트랜잭션 UI 서비스용 프로젝션
  as projection on ZRAP_R_GTASK_###
{
  key TaskID,
      @Search.defaultSearchElement: true                // [추가] 검색어를 이 필드에서 찾음
      Title,
      AgencyID,
      DueDate,
      Status,
      CheckStatus,
      Remark,
      LocalLastChangedAt
}
```

RAP100 솔루션의 프로젝션 뷰를 보면 관리 필드 중 `LocalLastChangedAt`(ETag)만 남아 있습니다. 생성 결과에 `CreatedBy` 등이 더 있어도 상관없습니다.

메타데이터 확장 (4번 요구사항 반영 후)

```cds
@Metadata.layer: #CUSTOMER                               // 고객 계층(가장 우선)
@UI: {
  headerInfo: {
    typeName: 'Task',
    typeNamePlural: 'Tasks',
    title: { type: #STANDARD, value: 'Title' },          // [변경] 머리글 제목
    description: { type: #STANDARD, value: 'TaskID' }
  }
}
annotate view ZRAP_C_GTASK_### with
{
  @UI.facet: [ {
    id: 'idIdentification',
    type: #IDENTIFICATION_REFERENCE,                     // identification 필드 묶음을 한 섹션으로
    label: 'Task',
    position: 10
  } ]

  @UI: {
    lineItem:       [ { position: 10, importance: #HIGH } ],
    identification: [ { position: 10 } ],
    selectionField: [ { position: 10 } ]
  }
  TaskID;

  @UI: {
    lineItem:       [ { position: 20, importance: #HIGH } ],
    identification: [ { position: 20 } ],
    selectionField: [ { position: 20 } ]
  }
  Title;

  @UI: {
    lineItem:       [ { position: 30, importance: #HIGH } ],
    identification: [ { position: 30 } ],
    selectionField: [ { position: 30 } ]
  }
  AgencyID;

  @UI: {
    lineItem:       [ { position: 40, importance: #HIGH } ],
    identification: [ { position: 40 } ],
    selectionField: [ { position: 40 } ]
  }
  DueDate;

  @UI: {
    lineItem:       [ { position: 50, importance: #HIGH } ],
    identification: [ { position: 50 } ],
    selectionField: [ { position: 50 } ]
  }
  Status;

  @UI: {
    lineItem:       [ { position: 60, importance: #MEDIUM } ],
    identification: [ { position: 60 } ]
  }
  CheckStatus;                                           // [변경] selectionField 삭제

  @UI: {
    lineItem:       [ { position: 70, importance: #LOW } ],
    identification: [ { position: 70 } ]
  }
  Remark;                                                // [변경] selectionField 삭제

  @UI.hidden: true                                       // 기술 필드 숨김
  LocalLastChangedAt;
}
```

(→ 어노테이션 탭: @UI.headerInfo, @UI.facet, @UI.lineItem, @UI.identification, @UI.selectionField, @UI.hidden, @Search.searchable, @ObjectModel.semanticKey)

프로젝션 BDEF (생성 직후 예상)

```bdef
projection;
strict ( 2 );
use draft;

define behavior for ZRAP_C_GTASK_### alias Task
use etag
{
  use create;
  use update;
  use delete;

  use action Edit;
  use action Activate;
  use action Discard;
  use action Resume;
  use action Prepare;
}
```

생성기 화면에 "Service Projection Behavior – Behavior Implementation Class"가 있으므로 버전에 따라 첫 줄이 `projection implementation in class ZBP_RAP_C_GTASK_### unique;`이고 빈 클래스가 함께 생길 수 있습니다(RAP100 솔루션 BDEF는 `projection;`만 있음, 실제 시스템에서 확인 필요).

서비스 정의 (생성 직후 예상)

```cds
@EndUserText.label: 'Service definition for ZRAP_C_GTASK_###'
define service ZRAP_UI_GTASK_### {
  expose ZRAP_C_GTASK_### as Task;
}
```

**R-01 수작업과 비교표**

| 항목 | 생성기 | R-01 수작업 |
|---|---|---|
| 엔터티 수 | 테이블 1개 → 루트 1개 | Travel + Booking(composition) |
| 키 번호 매김 | 숫자 키 → 외부 입력(`mandatory : create, readonly : update`) | late numbering + `adjust_numbers` |
| draft | `with draft` + draft 테이블 + draft 액션 5개 자동 | 직접 선언, 퀵 픽스로 draft 테이블 |
| ETag / 잠금 | 관리 필드 데이터 엘리먼트로 `etag master`/`total etag` 자동 | 직접 선언 |
| 관리 필드 `@Semantics` | 자동 | 직접 |
| 권한 | `authorization master ( global )` + 빈 메서드 | 전역 권한 구현 |
| 접근 제어 | `#CHECK`만 붙이고 DCL 없음(경고) | 문제 설계에 따름 |
| 값 도움말·텍스트·연관 | 없음 | `/DMO/I_*_StdVH`, `_Agency` 등 직접 |
| 검색 | 없음(3단계에서 추가) | 직접 |
| UI | 모든 필드 lineItem/identification/selectionField 일괄 | 필드 그룹·데이터 포인트·criticality 등 설계 |
| 가상 요소, 검증·결정·액션, 사이드 이펙트 | 없음 | R-01~R-02에서 직접 |

결론: 생성기는 **"표준 CRUD + draft가 돌아가는 뼈대"** 를 1분 만에 만들어 주고, 업무 의미가 들어가는 부분(번호 규칙, 연관, 값 도움말, 검증, 액션, 권한 판단)은 하나도 만들지 않습니다. 실무에서는 생성기로 뼈대를 만든 뒤 R-01~R-04에서 배운 것을 덧붙이는 흐름이 일반적입니다(RAP100 워크숍 전체가 이 흐름입니다).

**자주 나는 오류와 해결**
- RAP100 문서: 생성된 MDE에서 `RAWSTRING`(첨부 파일) 필드의 `selectionField`는 허용되지 않으므로 지워야 한다고 안내합니다. 이 문제 테이블에는 LOB 필드가 없어 해당 없지만, 다른 테이블로 생성할 때 기억하세요.
- `@AccessControl.authorizationCheck: #CHECK`인데 DCL이 없다는 경고는 RAP100도 "무시하거나 `#NOT_REQUIRED`로 바꿔도 된다"고 안내합니다.

</details>

#### 4단계. Service Consumption Model: 원격 OData 메타데이터로 프록시 만들기

요구사항
1. 브라우저로 `https://sapes5.sapdevcenter.com/sap/opu/odata/sap/ZAGENCYCDS_SRV/$metadata` 를 열어 XML 파일로 저장하세요. 인증서·로그인 창이 뜨면 **Cancel** 하세요(인증 없는 서비스). 파일 안에서 엔터티 타입 이름, 엔터티 셋 이름, 키, 속성 8개를 찾아 적으세요.
2. 패키지에서 **New > Other ABAP Repository Object > Service Consumption Model**을 고르고 이름 `ZRAP_SC_AGENCY_###`, 설명 `Agencies from ES5`, **Remote Consumption Mode = OData** 로 만드세요.
3. 저장한 `$metadata` 파일을 **Browse** 로 고르고, 클래스 이름은 제안값(`ZRAP_SC_AGENCY_###`)을 그대로 두세요. 엔터티 셋 목록·ETag 지원 화면은 기본값으로 넘기고 Finish 한 뒤, Service Consumption Model을 **활성화**하세요.
4. Service Consumption Model 편집기에서 엔터티 셋을 고르고 연산(Read List, Read, Create, Update, Delete)별로 제공되는 **예제 코드**를 확인하세요. Read List 예제를 클립보드로 복사해 5단계에 씁니다.
5. 생성된 클래스 `ZRAP_SC_AGENCY_###`의 PUBLIC SECTION에서 엔터티 타입 구조(`tys_...`)와 테이블 타입(`tyt_...`)의 **정확한 이름**, 그리고 각 속성의 ABAP 컴포넌트 이름을 적으세요(5·6단계 코드의 타입 이름을 이것으로 바꿉니다).

**확인**
- 패키지에 Service Consumption Model과 같은 이름의 클래스가 생기고 활성화됩니다.
- 생성 클래스에서 `AgencyId` 속성이 `agency_id`, `PostalCode`가 `postal_code`처럼 snake_case 컴포넌트로 바뀐 것을 확인합니다.

<details><summary>정답·해설</summary>

`$metadata`에서 찾은 내용(openSAP RAP 과정 5주차에 실린 파일 기준)

| 항목 | 값 |
|---|---|
| OData 버전 | V2 (`m:DataServiceVersion="2.0"`) |
| 엔터티 타입 | `Z_TRAVEL_AGENCY_ES5Type`, 키 `AgencyId` |
| 엔터티 셋 | `Z_TRAVEL_AGENCY_ES5` (`sap:creatable/updatable/deletable="false"` → 읽기 전용) |
| 속성 | `AgencyId`(6), `Name`(31), `Street`(30), `PostalCode`(10), `City`(25), `Country`(3), `PhoneNumber`(30), `WebAddress`(255) — 모두 `Edm.String` |

**무엇이 생성되나: 두 세대의 생성기**

| | 예전 마법사(openSAP 5주차, 2020년 무렵) | 현재 마법사(RAP620 워크숍) |
|---|---|---|
| 생성물 | Service Consumption Model + **서비스 정의 + 추상 엔터티**(`<접두어>Z_TRAVEL_AGENCY_ES5`) | Service Consumption Model + **같은 이름의 클래스** |
| 결과 타입 | 추상 엔터티(`TYPE TABLE OF <추상 엔터티>`) | 클래스 안의 `tys_<엔터티 타입>` / `tyt_<엔터티 타입>` |
| 프록시 생성 API | `cl_web_odata_client_factory=>create_v2_remote_proxy( iv_service_definition_name = ... )` | `/iwbep/cl_cp_factory_remote=>create_v2_remote_proxy( is_proxy_model_key = VALUE #( repository_id = 'DEFAULT' proxy_model_id = '<SCM 이름>' proxy_model_version = '0001' ) ... )` |

RAP620 문서에서 생성 클래스는 `/iwbep/cl_v4_abs_pm_model_prov`를 상속하고, 엔터티 타입 `SEPMRA_I_Product_EType`이 `tys_sepmra_i_product_etype` 구조(컴포넌트 `product`, `product_category`, `created_by_user` ...)로 생성됐습니다. 같은 규칙이면 이 문제의 타입은 `tys_z_travel_agency_es5type`/`tyt_z_travel_agency_es5type` 근처의 이름이 됩니다. 숫자와 대문자가 붙은 부분(`ES5Type`)을 어떻게 나누는지는 확인하지 못했으므로, **5번 요구사항에서 적은 실제 이름으로 바꿔 쓰세요**(실제 시스템에서 확인 필요).

**트라이얼 제약**
- RAP620 문서에는 "트라이얼에서 Service Consumption Model 생성이 실패하며 핫픽스로 고칠 예정"이라는 (당시) 주의문이 있습니다. 지금도 실패하면 이 단계와 5·6단계는 코드를 읽는 것으로 대신하세요.
- 공식 예제들이 ES5를 쓰는 이유는 "트라이얼은 공유 시스템이라 인증 없는 공개 서비스만 쓸 수 있기 때문"이라고 RAP620 문서가 설명합니다.

**자기 OData V4 Web API를 소비하려면**
- R-01~R-04의 `ZRAP_API_TRAVEL_O4_###`(OData V4 Web API 바인딩)도 같은 방식으로 소비할 수 있습니다. 서비스 바인딩에서 서비스 URL 뒤에 `$metadata`를 붙여 파일을 받고, Service Consumption Model을 만들면 OData V4 프록시가 생깁니다.
- 다만 자기 서비스는 **인증이 필요**합니다. `create_by_url`로 만든 목적지에는 사용자·암호가 없으므로 401이 납니다. 정식 방법은 5단계의 통신 시나리오·약정(인바운드 쪽에도 통신 사용자 필요)이고, 트라이얼에서는 이 관리 앱을 쓸 수 없어 **사실상 시험이 어렵습니다**(실제 시스템에서 확인 필요). V4 프록시는 `/iwbep/cl_cp_factory_remote=>create_v4_remote_proxy`로 만드는 것으로 알려져 있으나 공식 예제 코드로 확인하지 못했습니다(실제 시스템에서 확인 필요).

</details>

#### 5단계. 콘솔 클래스로 원격 OData 읽기 (목적지·통신 약정 이해)

요구사항
1. 클래스 `ZCL_RAP_CE_AGENCY_###`(인터페이스 `IF_OO_ADT_CLASSRUN`)를 만드세요. 6단계에서 같은 클래스에 custom entity 쿼리 구현을 더합니다.
2. 공개 메서드 `get_agencies`를 만드세요.
   - 입력: 필터(`if_rap_query_filter=>tt_name_range_pairs`, 원격 속성 이름 기준), `top`, `skip`, 데이터 요청 여부, 건수 요청 여부
   - 출력: 원격 결과 테이블(4단계 생성 클래스의 `tyt_...` 타입), 전체 건수(`int8`)
   - 예외: `/iwbep/cx_cp_remote`, `/iwbep/cx_gateway`, `cx_web_http_client_error`, `cx_http_dest_provider_error`
3. 구현 순서: `cl_http_destination_provider=>create_by_url`로 ES5 루트 URL 목적지 → `cl_web_http_client_manager=>create_by_http_destination`으로 HTTP 클라이언트 → `/iwbep/cl_cp_factory_remote=>create_v2_remote_proxy`로 프록시(서비스 루트 `/sap/opu/odata/sap/ZAGENCYCDS_SRV/`) → 엔터티 셋 리소스의 읽기 요청 → 필터 팩토리로 range 필터 트리(AND) → top/skip/count → 실행 → 결과·건수 받기.
4. `main`에서 여행사 번호 `>= 070015` 조건, 1건 건너뛰고 3건, 건수 포함으로 호출해 건수와 결과를 출력하세요. 오류는 메시지 긴 텍스트를 출력하세요.
5. 정답 해설의 "정식 시스템에서의 목적지" 부분을 읽고, 통신 시나리오·통신 시스템·통신 약정·아웃바운드 서비스가 각각 무엇을 담는지 한 줄씩 적으세요.

**확인**
- F9 실행 시 `Total number of records = N`(N은 ES5 데이터에 따라 다름)과 여행사 3건이 출력됩니다.
- ES5에 접속할 수 없으면 HTTP 클라이언트 또는 원격 예외 메시지가 출력됩니다(이 경우 코드가 잘못된 것이 아닙니다).

<details><summary>정답·해설</summary>

```abap
CLASS zcl_rap_ce_agency_### DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_oo_adt_classrun.

    " 4단계 생성 클래스의 테이블 타입 이름으로 바꾸세요 (실제 시스템에서 확인 필요)
    TYPES t_remote_agencies TYPE zrap_sc_agency_###=>tyt_z_travel_agency_es5type.

    METHODS get_agencies
      IMPORTING
        filter_cond        TYPE if_rap_query_filter=>tt_name_range_pairs OPTIONAL
        top                TYPE i OPTIONAL
        skip               TYPE i OPTIONAL
        is_data_requested  TYPE abap_bool
        is_count_requested TYPE abap_bool
      EXPORTING
        remote_agencies    TYPE t_remote_agencies
        count              TYPE int8
      RAISING
        /iwbep/cx_cp_remote
        /iwbep/cx_gateway
        cx_web_http_client_error
        cx_http_dest_provider_error.

  PRIVATE SECTION.
    CONSTANTS es5_host     TYPE string VALUE `https://sapes5.sapdevcenter.com`.
    CONSTANTS service_root TYPE string VALUE `/sap/opu/odata/sap/ZAGENCYCDS_SRV/`.
    CONSTANTS entity_set   TYPE string VALUE `Z_TRAVEL_AGENCY_ES5`.
ENDCLASS.


CLASS zcl_rap_ce_agency_### IMPLEMENTATION.

  METHOD if_oo_adt_classrun~main.
    DATA remote_agencies TYPE t_remote_agencies.
    DATA count           TYPE int8.

    DATA(ranges) = VALUE if_rap_query_filter=>tt_range_option(
                     ( sign = 'I' option = 'GE' low = '070015' ) ).
    " 필터 이름 = 원격 속성의 내부 이름(생성 클래스 기준, 실제 시스템에서 확인 필요)
    DATA(filter) = VALUE if_rap_query_filter=>tt_name_range_pairs(
                     ( name = 'AGENCY_ID' range = ranges ) ).

    TRY.
        get_agencies(
          EXPORTING
            filter_cond        = filter
            top                = 3
            skip               = 1
            is_data_requested  = abap_true
            is_count_requested = abap_true
          IMPORTING
            remote_agencies    = remote_agencies
            count              = count ).

        out->write( |Total number of records = { count }| ).
        out->write( remote_agencies ).

      CATCH cx_root INTO DATA(error).
        out->write( cl_message_helper=>get_latest_t100_exception( error )->if_message~get_longtext( ) ).
    ENDTRY.
  ENDMETHOD.


  METHOD get_agencies.
    DATA root_filter_node TYPE REF TO /iwbep/if_cp_filter_node.

    CLEAR: remote_agencies, count.

    " 1) HTTP 목적지: 트라이얼에서는 URL로 직접 만든다 (인증 없는 공개 서비스만)
    DATA(http_destination) = cl_http_destination_provider=>create_by_url( i_url = es5_host ).

    " 2) HTTP 클라이언트
    DATA(http_client) = cl_web_http_client_manager=>create_by_http_destination(
                          i_destination = http_destination ).

    " 3) OData V2 클라이언트 프록시: Service Consumption Model을 proxy_model_id로 지정
    DATA(odata_client_proxy) = /iwbep/cl_cp_factory_remote=>create_v2_remote_proxy(
      EXPORTING
        is_proxy_model_key       = VALUE #( repository_id       = 'DEFAULT'
                                            proxy_model_id      = 'ZRAP_SC_AGENCY_###'
                                            proxy_model_version = '0001' )
        io_http_client           = http_client
        iv_relative_service_root = service_root ).

    " 4) 엔터티 셋 리소스 → 목록 읽기 요청
    DATA(read_list_request) = odata_client_proxy->create_resource_for_entity_set( entity_set
                                )->create_request_for_read( ).

    " 5) range 필터를 AND로 묶은 필터 트리
    DATA(filter_factory) = read_list_request->create_filter_factory( ).
    LOOP AT filter_cond INTO DATA(filter_condition).
      DATA(filter_node) = filter_factory->create_by_range( iv_property_path = filter_condition-name
                                                           it_range         = filter_condition-range ).
      IF root_filter_node IS INITIAL.
        root_filter_node = filter_node.
      ELSE.
        root_filter_node = root_filter_node->and( filter_node ).
      ENDIF.
    ENDLOOP.
    IF root_filter_node IS NOT INITIAL.
      read_list_request->set_filter( root_filter_node ).
    ENDIF.

    " 6) 페이징과 건수
    IF is_data_requested = abap_true.
      read_list_request->set_skip( skip ).
      IF top > 0.
        read_list_request->set_top( top ).
      ENDIF.
    ENDIF.
    IF is_count_requested = abap_true.
      read_list_request->request_count( ).
    ENDIF.
    IF is_data_requested = abap_false.
      read_list_request->request_no_business_data( ).
    ENDIF.

    " 7) 실행과 결과
    DATA(read_list_response) = read_list_request->execute( ).
    IF is_data_requested = abap_true.
      read_list_response->get_business_data( IMPORTING et_business_data = remote_agencies ).
    ENDIF.
    IF is_count_requested = abap_true.
      count = read_list_response->get_count( ).
    ENDIF.
  ENDMETHOD.

ENDCLASS.
```

**왜 이렇게 쓰나**
- 구조는 openSAP 5주차 `get_agencies`(데이터·건수 분리 요청)와 RAP620의 현재 프록시 생성 방식(`/iwbep/cl_cp_factory_remote`, `is_proxy_model_key`)을 합친 것입니다. 변수 선언을 인라인으로 바꾼 것 외에는 메서드 호출과 매개변수 이름이 두 공식 예제와 같습니다.
- 서비스 루트(`/sap/opu/odata/sap/ZAGENCYCDS_SRV/`)는 목적지가 아니라 프록시에 줍니다. 목적지는 **호스트**까지만 담고, 하나의 목적지로 같은 호스트의 여러 서비스를 부를 수 있게 하려는 설계입니다.
- 필터 이름: openSAP 예전 프록시는 `'AGENCYID'`, RAP620의 현재 프록시는 `Product` 속성에 `'PRODUCT'`를 썼습니다. 즉 **생성된 ABAP 컴포넌트 이름의 대문자**가 속성 경로로 쓰이는 것으로 보이며, 그러면 `AgencyId`는 `'AGENCY_ID'`입니다. 필터가 무시되거나 "property not found" 류 예외가 나면 4단계에서 적은 컴포넌트 이름 대문자로 바꾸세요(실제 시스템에서 확인 필요).
- `cl_message_helper=>get_latest_t100_exception`은 두 공식 예제가 쓰는 오류 텍스트 추출 방식입니다.

**정식 시스템(트라이얼이 아닌 곳)에서의 목적지**

트라이얼은 RAP620 문서 표현대로 "목적지 서비스를 쓸 수 없어" `create_by_url`을 씁니다. 운영 시스템에서는 URL·인증 정보를 코드에 넣지 않고 아래 객체로 분리합니다.

| 객체 | 어디서 만드나 | 담는 것 |
|---|---|---|
| 아웃바운드 서비스(Outbound Service, HTTP 유형) | ADT (개발자) | "이 소프트웨어가 바깥의 어떤 HTTP 서비스를 부른다"는 선언(서비스 ID) |
| 통신 시나리오(Communication Scenario) | ADT (개발자) | 아웃바운드/인바운드 서비스 묶음. 전송 가능한 개발 객체 |
| 통신 시스템(Communication System) | Fiori 관리 앱 (관리자) | 상대 시스템 호스트, 포트, 아웃바운드 사용자·인증 방식 |
| 통신 약정(Communication Arrangement) | Fiori 관리 앱 (관리자) | "이 시나리오를 이 시스템과 연결"하는 실제 설정 |

코드는 약정을 이름으로 찾기만 합니다(매개변수 이름은 공식 예제로 확인하지 못함, 실제 시스템에서 확인 필요):

```abap
" 운영 시스템 예시 (트라이얼에서는 관리 앱이 없어 시험 불가)
DATA(http_destination) = cl_http_destination_provider=>create_by_comm_arrangement(
                           comm_scenario  = 'ZRAP_GTASK_CS_###'          " 통신 시나리오
                           service_id     = 'ZRAP_GTASK_OB_###_REST'     " 아웃바운드 서비스 ID
                           comm_system_id = 'ES5' ).                     " 통신 시스템 (선택)
```

RAP620 문서는 또 하나의 방법으로 BTP Cloud Foundry 목적지 서비스를 쓰는 `cl_http_destination_provider=>create_by_cloud_destination`을 언급합니다(매개변수는 문서에 없음, 실제 시스템에서 확인 필요). 정리하면 목적지를 얻는 방법은 **URL 직접(테스트·공개 서비스)**, **통신 약정(ABAP 환경 표준)**, **BTP 목적지 서비스** 세 가지이고, 그 뒤의 HTTP 클라이언트·프록시 코드는 셋 모두 같습니다. 이것이 `get_agencies`에서 목적지 생성 한 줄만 바꾸면 되도록 분리해 둔 이유입니다.

**자주 나는 오류와 해결**
- `cx_http_dest_provider_error`: URL 형식 오류 또는(운영) 약정을 찾지 못함.
- `cx_web_http_client_error` / `/iwbep/cx_cp_remote`: 상대 시스템 응답 오류(ES5 중단, 401, 404). 404면 서비스 루트 끝의 `/`와 대소문자를 확인하세요.
- 타입 오류 "`TYT_...` is unknown": 4단계 5번에서 적은 실제 타입 이름으로 바꾸세요.

</details>

#### 6단계. 원격 데이터를 custom entity로 감싸 Fiori 값 도움말로 쓰기

요구사항
1. 데이터 정의 `ZRAP_CE_AGENCY_###`(설명 `Agencies from ES5 (remote)`)를 만드세요. 템플릿 선택 화면까지 가려면 전송 요청 화면에서 **Finish가 아니라 Next**를 눌러야 합니다. 템플릿 "Define Custom Entity with Parameters"를 고른 뒤 `with parameters ...` 부분을 지우세요.
2. 루트 custom entity로 정의하고, 요소는 `AgencyId`(키, NUMC 6), `Name`(31), `Street`(30), `PostalCode`(10), `City`(25), `Country`(3), `PhoneNumber`(30), `WebAddress`(255)로 하세요. 조회 구현 클래스는 `ZCL_RAP_CE_AGENCY_###`입니다.
3. 목록 화면용으로 `AgencyId`, `Name`, `City`, `Country`에 목록 위치를, `AgencyId`, `City`에 필터 칸을 주세요.
4. 클래스 `ZCL_RAP_CE_AGENCY_###`에 `IF_RAP_QUERY_PROVIDER`를 추가하고 `select`를 구현하세요.
   - 페이징(`get_page_size`, `get_offset`), 데이터/건수 요청 여부, 필터(`get_as_ranges`)를 읽어 `get_agencies`를 부르세요.
   - 필터 이름은 custom entity 요소 이름(대문자)으로 들어오므로 원격 속성 이름으로 바꾸는 비공개 메서드를 두세요.
   - 원격 결과를 custom entity 타입으로 매핑(`CORRESPONDING ... MAPPING`)해 `set_data`, 건수는 `set_total_number_of_records`로 돌려주세요.
   - 필터를 range로 바꿀 수 없으면(`cx_rap_query_filter_no_range`) 필터 없이 진행하세요.
5. 생성기가 만든 서비스 정의 `ZRAP_UI_GTASK_###`에 custom entity를 `RemoteAgency`로 노출하고, 프로젝션 뷰 `ZRAP_C_GTASK_###`의 `AgencyID`에 이 엔터티를 값 도움말로 붙이세요.

**직접 추가할 어노테이션**
- `@EndUserText.label` — custom entity 설명.
- `@ObjectModel.query.implementedBy` — 데이터를 돌려줄 ABAP 클래스(`ABAP:` 접두어).
- `@UI.headerInfo` — 원격 여행사를 열었을 때 머리글 이름.
- `@UI.lineItem` — 목록(그리고 값 도움말 결과 표)에 보일 열.
- `@UI.selectionField` — 필터 칸.
- `@Consumption.valueHelpDefinition` — Task의 AgencyID 입력칸에 어떤 엔터티를 값 도움말로 쓸지.

**확인**
- 서비스 바인딩에 엔터티 셋 `RemoteAgency`가 보이고, 미리보기하면 ES5 여행사 목록이 나옵니다. City 필터, 페이지 넘김이 동작합니다.
- Task를 Edit 해서 Agency ID 입력칸의 값 도움말 버튼을 누르면 원격 여행사 목록이 뜨고, 고른 번호가 입력됩니다.

<details><summary>정답·해설</summary>

```cds
@EndUserText.label: 'Agencies from ES5 (remote)'
@ObjectModel.query.implementedBy: 'ABAP:ZCL_RAP_CE_AGENCY_###'   // DB 대신 이 클래스의 select가 데이터를 줌
@UI.headerInfo: { typeName: 'Agency', typeNamePlural: 'Agencies',
                  title: { type: #STANDARD, value: 'Name' } }
define root custom entity ZRAP_CE_AGENCY_###
{
      @UI.lineItem: [ { position: 10 } ]
      @UI.selectionField: [ { position: 10 } ]
  key AgencyId    : abap.numc( 6 );
      @UI.lineItem: [ { position: 20 } ]
      Name        : abap.char( 31 );
      Street      : abap.char( 30 );
      PostalCode  : abap.char( 10 );
      @UI.lineItem: [ { position: 30 } ]
      @UI.selectionField: [ { position: 20 } ]
      City        : abap.char( 25 );
      @UI.lineItem: [ { position: 40 } ]
      Country     : abap.char( 3 );
      PhoneNumber : abap.char( 30 );
      WebAddress  : abap.char( 255 );
}
```

(→ 어노테이션 탭: @ObjectModel.query.implementedBy, @UI.headerInfo, @UI.lineItem, @UI.selectionField)

```abap
CLASS zcl_rap_ce_agency_### DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_oo_adt_classrun.
    INTERFACES if_rap_query_provider.

    " 4단계 생성 클래스의 테이블 타입 이름으로 바꾸세요 (실제 시스템에서 확인 필요)
    TYPES t_remote_agencies TYPE zrap_sc_agency_###=>tyt_z_travel_agency_es5type.
    TYPES t_agencies        TYPE STANDARD TABLE OF zrap_ce_agency_### WITH EMPTY KEY.

    METHODS get_agencies
      IMPORTING
        filter_cond        TYPE if_rap_query_filter=>tt_name_range_pairs OPTIONAL
        top                TYPE i OPTIONAL
        skip               TYPE i OPTIONAL
        is_data_requested  TYPE abap_bool
        is_count_requested TYPE abap_bool
      EXPORTING
        remote_agencies    TYPE t_remote_agencies
        count              TYPE int8
      RAISING
        /iwbep/cx_cp_remote
        /iwbep/cx_gateway
        cx_web_http_client_error
        cx_http_dest_provider_error.

  PRIVATE SECTION.
    CONSTANTS es5_host     TYPE string VALUE `https://sapes5.sapdevcenter.com`.
    CONSTANTS service_root TYPE string VALUE `/sap/opu/odata/sap/ZAGENCYCDS_SRV/`.
    CONSTANTS entity_set   TYPE string VALUE `Z_TRAVEL_AGENCY_ES5`.

    "! custom entity 요소 이름(대문자) → 원격 속성 경로
    METHODS to_remote_property
      IMPORTING element         TYPE string
      RETURNING VALUE(property) TYPE string.
ENDCLASS.


CLASS zcl_rap_ce_agency_### IMPLEMENTATION.

  METHOD if_oo_adt_classrun~main.
    DATA remote_agencies TYPE t_remote_agencies.
    DATA count           TYPE int8.

    DATA(ranges) = VALUE if_rap_query_filter=>tt_range_option(
                     ( sign = 'I' option = 'GE' low = '070015' ) ).
    DATA(filter) = VALUE if_rap_query_filter=>tt_name_range_pairs(
                     ( name = to_remote_property( `AGENCYID` ) range = ranges ) ).

    TRY.
        get_agencies(
          EXPORTING
            filter_cond        = filter
            top                = 3
            skip               = 1
            is_data_requested  = abap_true
            is_count_requested = abap_true
          IMPORTING
            remote_agencies    = remote_agencies
            count              = count ).

        out->write( |Total number of records = { count }| ).
        out->write( remote_agencies ).

      CATCH cx_root INTO DATA(error).
        out->write( cl_message_helper=>get_latest_t100_exception( error )->if_message~get_longtext( ) ).
    ENDTRY.
  ENDMETHOD.


  METHOD if_rap_query_provider~select.
    DATA remote_agencies TYPE t_remote_agencies.
    DATA agencies        TYPE t_agencies.
    DATA count           TYPE int8.
    DATA remote_filter   TYPE if_rap_query_filter=>tt_name_range_pairs.

    " 페이징: page_size가 -1(무제한)이면 top을 주지 않는다
    DATA(page_size) = io_request->get_paging( )->get_page_size( ).
    DATA(offset)    = io_request->get_paging( )->get_offset( ).
    DATA(top)       = COND i( WHEN page_size = if_rap_query_paging=>page_size_unlimited THEN 0
                              ELSE CONV i( page_size ) ).

    " 필터: 요소 이름 → 원격 속성 이름
    TRY.
        DATA(entity_filter) = io_request->get_filter( )->get_as_ranges( ).
        remote_filter = VALUE #( FOR pair IN entity_filter
                                 ( name  = to_remote_property( CONV #( pair-name ) )
                                   range = pair-range ) ).
      CATCH cx_rap_query_filter_no_range.
        CLEAR remote_filter.   " range로 표현 못 하는 필터는 원격에 넘기지 않음
    ENDTRY.

    TRY.
        get_agencies(
          EXPORTING
            filter_cond        = remote_filter
            top                = top
            skip               = CONV i( offset )
            is_data_requested  = io_request->is_data_requested( )
            is_count_requested = io_request->is_total_numb_of_rec_requested( )
          IMPORTING
            remote_agencies    = remote_agencies
            count              = count ).

      CATCH /iwbep/cx_cp_remote /iwbep/cx_gateway
            cx_web_http_client_error cx_http_dest_provider_error.
        " 원격 오류: 빈 결과로 응답 (해설 참고)
        CLEAR: remote_agencies, count.
    ENDTRY.

    IF io_request->is_data_requested( ).
      agencies = CORRESPONDING #( remote_agencies
                                  MAPPING AgencyId    = agency_id
                                          PostalCode  = postal_code
                                          PhoneNumber = phone_number
                                          WebAddress  = web_address ).
      io_response->set_data( agencies ).
    ENDIF.
    IF io_request->is_total_numb_of_rec_requested( ).
      io_response->set_total_number_of_records( count ).
    ENDIF.
  ENDMETHOD.


  METHOD to_remote_property.
    " 생성 클래스의 컴포넌트 이름(대문자) 기준 (실제 시스템에서 확인 필요)
    property = SWITCH #( to_upper( element )
                 WHEN `AGENCYID`    THEN `AGENCY_ID`
                 WHEN `POSTALCODE`  THEN `POSTAL_CODE`
                 WHEN `PHONENUMBER` THEN `PHONE_NUMBER`
                 WHEN `WEBADDRESS`  THEN `WEB_ADDRESS`
                 ELSE to_upper( element ) ).          " NAME, STREET, CITY, COUNTRY는 같음
  ENDMETHOD.


  METHOD get_agencies.
    DATA root_filter_node TYPE REF TO /iwbep/if_cp_filter_node.

    CLEAR: remote_agencies, count.

    DATA(http_destination) = cl_http_destination_provider=>create_by_url( i_url = es5_host ).
    DATA(http_client) = cl_web_http_client_manager=>create_by_http_destination(
                          i_destination = http_destination ).

    DATA(odata_client_proxy) = /iwbep/cl_cp_factory_remote=>create_v2_remote_proxy(
      EXPORTING
        is_proxy_model_key       = VALUE #( repository_id       = 'DEFAULT'
                                            proxy_model_id      = 'ZRAP_SC_AGENCY_###'
                                            proxy_model_version = '0001' )
        io_http_client           = http_client
        iv_relative_service_root = service_root ).

    DATA(read_list_request) = odata_client_proxy->create_resource_for_entity_set( entity_set
                                )->create_request_for_read( ).

    DATA(filter_factory) = read_list_request->create_filter_factory( ).
    LOOP AT filter_cond INTO DATA(filter_condition).
      DATA(filter_node) = filter_factory->create_by_range( iv_property_path = filter_condition-name
                                                           it_range         = filter_condition-range ).
      IF root_filter_node IS INITIAL.
        root_filter_node = filter_node.
      ELSE.
        root_filter_node = root_filter_node->and( filter_node ).
      ENDIF.
    ENDLOOP.
    IF root_filter_node IS NOT INITIAL.
      read_list_request->set_filter( root_filter_node ).
    ENDIF.

    IF is_data_requested = abap_true.
      read_list_request->set_skip( skip ).
      IF top > 0.
        read_list_request->set_top( top ).
      ENDIF.
    ENDIF.
    IF is_count_requested = abap_true.
      read_list_request->request_count( ).
    ENDIF.
    IF is_data_requested = abap_false.
      read_list_request->request_no_business_data( ).
    ENDIF.

    DATA(read_list_response) = read_list_request->execute( ).
    IF is_data_requested = abap_true.
      read_list_response->get_business_data( IMPORTING et_business_data = remote_agencies ).
    ENDIF.
    IF is_count_requested = abap_true.
      count = read_list_response->get_count( ).
    ENDIF.
  ENDMETHOD.

ENDCLASS.
```

서비스 정의(추가 줄)와 프로젝션 뷰(`AgencyID` 부분만)

```cds
@EndUserText.label: 'Service definition for ZRAP_C_GTASK_###'
define service ZRAP_UI_GTASK_### {
  expose ZRAP_C_GTASK_###   as Task;
  expose ZRAP_CE_AGENCY_### as RemoteAgency;      // 원격 여행사 엔터티 셋
}
```

```cds
      @Consumption.valueHelpDefinition: [ { entity: { name: 'ZRAP_CE_AGENCY_###', element: 'AgencyId' } } ]   // 원격 값 도움말
      AgencyID,
```

(→ 어노테이션 탭: @Consumption.valueHelpDefinition)

**왜 이렇게 쓰나**
- openSAP 5주차는 정확히 이 구성(ES5 여행사 → custom entity → 서비스 정의에 `expose` → Travel 프로젝션의 `AgencyID`에 `@Consumption.valueHelpDefinition`)을 씁니다. 이 문제는 그 구성을 생성기로 만든 BO에 붙인 것입니다.
- custom entity와 클래스는 서로를 참조합니다(엔터티 → `implementedBy`, 클래스 → `TYPE ... zrap_ce_agency_###`). 엔터티를 먼저 활성화하면 "클래스가 아직 `IF_RAP_QUERY_PROVIDER`를 구현하지 않았다"는 경고가 나지만 활성화되고, 클래스를 활성화하면 사라집니다(RAP620 문서가 같은 경고를 설명).
- **매핑이 필요한 이유**: 원격 타입 컴포넌트는 `agency_id`처럼 snake_case이고 custom entity 요소는 `AgencyId`입니다. `CORRESPONDING`은 이름을 대소문자 구분 없이 맞추므로 `Name`/`name`, `City`/`city`는 자동이고, 밑줄이 다른 네 개만 `MAPPING`에 적었습니다(RAP620이 `ProductCategory = product_category`로 같은 처리를 함).
- **원격 오류 처리**: 공식 예제들은 `CATCH cx_root` 후 아무것도 하지 않습니다. 여기서는 빈 결과로 응답해 화면이 깨지지 않게 했습니다. 사용자에게 오류를 보여 주려면 `cx_rap_query_provider` 계열 예외를 던지는 방법이 있는데, 이 예외 클래스를 직접 생성할 수 있는지는 확인하지 못했습니다(실제 시스템에서 확인 필요).
- **정렬·검색**: 이 구현은 `get_sort_elements( )`와 검색어를 원격에 넘기지 않습니다. 원격 프록시에 정렬을 넘기는 API는 공식 예제에서 확인하지 못했습니다. R-08처럼 로컬에서 정렬하려면 "원격에서 전부 받고 로컬에서 정렬·페이징"으로 바꿔야 하는데, 원격 데이터가 많으면 비쌉니다. 이 트레이드오프가 원격 custom entity 설계의 핵심 판단입니다.
- **원격 값으로 검증하기**: openSAP 5주차 5단원은 Travel 검증(`validateAgency`)에서 `NEW zcl_ce_rap_agency_####( )->get_agencies( ... )`를 불러, 입력한 여행사가 원격에 있는지 확인합니다(원격 오류 시 `failed` + 메시지). Task BO에 같은 검증을 붙이는 것은 연습으로 남깁니다. 단, **검증은 저장 때마다 원격 호출**을 하므로 응답 시간과 원격 장애를 함께 고려해야 합니다.

**클래스 구조 해설**
- `select`는 BDEF에서 생기는 메서드가 아니라 인터페이스 `IF_RAP_QUERY_PROVIDER`에 고정된 시그니처입니다(R-08과 같음). 목록 조회, 값 도움말 조회, `$count`, Object Page 단건 조회가 모두 이 메서드로 들어옵니다.
- 값 도움말 대화 상자는 보통 **건수와 첫 페이지**를 함께 요청합니다. 그래서 `is_total_numb_of_rec_requested`를 무시하면 값 도움말이 오류를 냅니다.

</details>

#### 7단계. 애플리케이션 로그: 로그 객체와 `with additional save`에서 로그 쓰기

요구사항
1. 패키지에서 **New > Other ABAP Repository Object > Application Log Object**로 로그 객체 `ZRAP_GTASK_###`(설명 `Task BO logs`)를 만들고, 하위 객체 `STATUS`(상태 변경 기록), `JOB`(잡 실행 기록)을 추가해 저장·활성화하세요. (메뉴 이름은 실제 시스템에서 확인)
2. 기본 BDEF `ZRAP_R_GTASK_###`의 첫 줄을 `managed with additional save ...`로 바꾸세요(전체 데이터 옵션은 쓰지 않음).
3. 행동 풀에 세이버 클래스 `lsc_zrap_r_gtask_###`를 추가하고 `save_modified`를 재정의하세요.
   - 생성된 Task: `Task 00000006 created`
   - 상태(`Status`)가 바뀐 Task: `Task 00000001: status -> X` (변경 필드만 넘어오므로 `%control-Status`로 판단)
   - 삭제된 Task: `Task 00000006 deleted`
   - 위 문장들을 모아 **로그 하나**에 자유 텍스트 항목으로 넣고 저장하세요. 헤더: 객체 `ZRAP_GTASK_###`, 하위 객체 `STATUS`, 외부 ID `GTASK`.
   - 로그 저장 실패가 업무 데이터 저장을 막으면 안 됩니다.
4. 콘솔 클래스 `ZCL_RAP_GTASK_LOG_###`를 만들어, 최근 24시간 동안 하위 객체 `STATUS`와 `JOB`에 쌓인 로그 항목을 하위 객체·항목 번호·메시지 텍스트로 출력하세요.

**확인**
- Fiori 미리보기에서 Task 하나의 상태를 `O` → `D`로 바꿔 저장하고, 새 Task를 하나 만들었다가 지운 뒤, `ZCL_RAP_GTASK_LOG_###`를 F9로 실행하면 세 줄(상태 변경, 생성, 삭제)이 `STATUS` 아래 보입니다.
- draft로 편집만 하고 저장하지 않은 변경은 로그에 **나오지 않습니다**(활성 데이터가 저장될 때만 `save_modified`가 불림).

<details><summary>정답·해설</summary>

BDEF 머리 부분(나머지는 3단계와 같음, 최종 전체는 8단계)

```bdef
managed with additional save implementation in class ZBP_RAP_R_GTASK_### unique;
strict ( 2 );
with draft;
```

행동 풀 로컬 클래스 중 세이버 부분(핸들러는 3단계 그대로, 최종 전체는 8단계)

```abap
CLASS lsc_zrap_r_gtask_### DEFINITION INHERITING FROM cl_abap_behavior_saver.
  PROTECTED SECTION.
    METHODS save_modified REDEFINITION.

  PRIVATE SECTION.
    CONSTANTS log_object    TYPE cl_bali_header_setter=>ty_object      VALUE 'ZRAP_GTASK_###'.
    CONSTANTS log_subobject TYPE cl_bali_header_setter=>ty_subobject   VALUE 'STATUS'.
    CONSTANTS log_ext_id    TYPE cl_bali_header_setter=>ty_external_id VALUE 'GTASK'.

    METHODS write_log IMPORTING texts TYPE string_table.
ENDCLASS.

CLASS lsc_zrap_r_gtask_### IMPLEMENTATION.

  METHOD save_modified.
    DATA texts TYPE string_table.

    LOOP AT create-task INTO DATA(created).
      APPEND |Task { created-TaskID } created| TO texts.
    ENDLOOP.

    LOOP AT update-task INTO DATA(updated).
      IF updated-%control-Status = if_abap_behv=>mk-on.        " 이번 저장에서 Status가 바뀜
        APPEND |Task { updated-TaskID }: status -> { updated-Status }| TO texts.
      ENDIF.
    ENDLOOP.

    LOOP AT delete-task INTO DATA(deleted).
      APPEND |Task { deleted-TaskID } deleted| TO texts.
    ENDLOOP.

    IF texts IS NOT INITIAL.
      write_log( texts ).
    ENDIF.
  ENDMETHOD.

  METHOD write_log.
    TRY.
        DATA(log) = cl_bali_log=>create( ).
        log->set_header( header = cl_bali_header_setter=>create( object      = log_object
                                                                 subobject   = log_subobject
                                                                 external_id = log_ext_id ) ).
        LOOP AT texts INTO DATA(text).
          " severity 값은 cheat sheet 예제와 같은 상수 (해설 참고)
          log->add_item( item = cl_bali_free_text_setter=>create( severity = if_bali_constants=>c_category_free_text
                                                                  text     = CONV #( text ) ) ).
        ENDLOOP.
        " late save 단계: DB 쓰기 허용 → 업무 데이터와 같은 LUW로 커밋됨
        cl_bali_log_db=>get_instance( )->save_log( log = log ).
      CATCH cx_bali_runtime.
        " 로그 실패는 무시: late save에서는 저장을 되돌릴 수 없고, 되돌려서도 안 됨
    ENDTRY.
  ENDMETHOD.

ENDCLASS.
```

로그 읽기 콘솔 클래스

```abap
CLASS zcl_rap_gtask_log_### DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_oo_adt_classrun.

  PRIVATE SECTION.
    CONSTANTS log_object TYPE cl_bali_header_setter=>ty_object      VALUE 'ZRAP_GTASK_###'.
    CONSTANTS log_ext_id TYPE cl_bali_header_setter=>ty_external_id VALUE 'GTASK'.
ENDCLASS.


CLASS zcl_rap_gtask_log_### IMPLEMENTATION.

  METHOD if_oo_adt_classrun~main.
    DATA subobjects TYPE STANDARD TABLE OF cl_bali_header_setter=>ty_subobject WITH EMPTY KEY.

    subobjects = VALUE #( ( 'STATUS' ) ( 'JOB' ) ).
    DATA(now)       = utclong_current( ).
    DATA(yesterday) = utclong_add( val = now hours = -24 ).

    LOOP AT subobjects INTO DATA(subobject).
      TRY.
          DATA(filter) = cl_bali_log_filter=>create( ).
          filter->set_descriptor( object      = log_object
                                  subobject   = subobject
                                  external_id = log_ext_id
                )->set_time_interval( start_time = yesterday
                                      end_time   = now ).

          DATA(logs) = cl_bali_log_db=>get_instance( )->load_logs_w_items_via_filter( filter = filter ).
          out->write( |--- { subobject }: { lines( logs ) } log(s)| ).

          LOOP AT logs INTO DATA(log).
            DATA(items) = log->get_all_items( ).
            LOOP AT items INTO DATA(item).
              out->write( |{ subobject } #{ item-log_item_number }: { item-item->get_message_text( ) }| ).
            ENDLOOP.
          ENDLOOP.

        CATCH cx_bali_runtime INTO DATA(error).
          out->write( |{ subobject }: { error->get_text( ) }| ).
      ENDTRY.
    ENDLOOP.
  ENDMETHOD.

ENDCLASS.
```

**왜 이렇게 쓰나**
- **어디서 로그를 쓰나**: EML cheat sheet의 "트랜잭션 단계별 허용 작업" 표에서 **DB 변경은 late save에서만** 허용됩니다. `cl_bali_log_db->save_log`는 로그 테이블에 쓰므로 결정(determination, 상호작용 단계)·검증(early save)에서 부르면 안 되고, `save_modified`(late save)가 맞는 자리입니다. 같은 cheat sheet는 `with additional save`의 대표 용도로 "변경 문서, 애플리케이션 로그 쓰기"를 듭니다.
- **결정에서 로그를 남기고 싶다면**: 결정 안에서는 문장만 만들어 두고(예: 행동 풀의 클래스 정적 버퍼) `save_modified`에서 한꺼번에 저장하거나, 로그를 업무 트랜잭션과 분리해 2차 DB 연결로 저장하는 방법이 있습니다. cheat sheet 표는 "2차 연결 커밋은 모든 단계에서 허용되며 애플리케이션 로그 같은 인프라 데이터용"이라고 적고 있습니다. `save_log`에 2차 연결을 쓰게 하는 매개변수가 있는 것으로 알려져 있으나 공식 예제로 확인하지 못했습니다(실제 시스템에서 확인 필요).
- **`%control-Status`로 판단하는 이유**: `with full data`가 없으면 `update`에는 키와 **바뀐 필드만** 들어옵니다(cheat sheet). `Status` 값 자체가 비어 있지 않은지가 아니라 `%control`이 켜졌는지를 봐야 "이번에 바뀌었는지"를 알 수 있습니다. R-04의 변경 로그와 같은 원리입니다.
- **severity 값**: cheat sheet 예제가 자유 텍스트 항목에 `if_bali_constants=>c_category_free_text`를 넘기므로 그대로 따랐습니다. 오류·경고 수준을 나누려면 `if_bali_constants`의 다른 상수를 Ctrl+Space로 확인하세요(실제 시스템에서 확인 필요). T100 메시지를 넣는 `cl_bali_message_setter`, 예외를 넣는 `cl_bali_exception_setter`(cheat sheet에 예제 있음)도 있습니다.
- **XCO 대안**: cheat sheet는 같은 일을 `xco_cp_bal=>for->database( )->log->create( iv_object = ... )`, `log->add_text( ... )`로 하는 XCO API도 보여 줍니다. 이 문제는 `cl_bali_*`로 통일했습니다.

**트라이얼 제약**
- cheat sheet는 로그 쓰기에 권한 객체 `S_APPL_LOG`가 필요하다고 적습니다. 트라이얼 개발 사용자에게 이 권한이 있는지, 그리고 ADT에서 Application Log Object를 만들 수 있는지는 확인하지 못했습니다. 로그가 안 보이면 `write_log`의 `CATCH`에 `out` 대신 디버거 중단점을 걸고 예외 텍스트를 확인하세요(실제 시스템에서 확인 필요).
- 운영 시스템에서는 로그를 보는 Fiori 관리 앱(애플리케이션 로그 표시 앱)을 쓰지만, 트라이얼에서는 관리 앱 접근이 제한되므로 위 콘솔 클래스로 읽습니다.

**클래스 구조 해설**
- `save_modified`의 `create`, `update`, `delete`는 BDEF의 `with additional save`에서 생기는 파생 타입 `REQUEST FOR CHANGE` / `REQUEST FOR DELETE`이며, 컴포넌트 이름은 엔터티 별칭(`task`)입니다.
- 관리형 BO는 `save_modified`를 **프레임워크의 기본 저장 다음에** 부릅니다. draft 저장(Edit 중 자동 저장)에서는 불리지 않고, Activate나 draft 없는 직접 저장(EML) 때만 불립니다.

</details>

#### 8단계. bgPF: 커밋이 끝난 뒤 백그라운드로 일 시키기

요구사항
1. 기본 BDEF에 두 액션을 추가하세요.
   - `requestCheck`: 결과 `[1] $self`. `CheckStatus`를 `R`, `Remark`를 `Check requested`로 바꿉니다. UI에 노출합니다.
   - `completeCheck`: 결과 없음. 기한이 지난 열린 작업이면 `Status`를 `X`로, 아니면 그대로 두고, `CheckStatus`를 `F`, `Remark`를 `Checked in background at <시각>`으로 바꿉니다. **UI에는 노출하지 않고** bgPF 작업이 EML로만 부릅니다.
   - `CheckStatus`, `Remark`는 읽기 전용 필드로 바꾸세요.
2. bgPF 작업 클래스 `ZCL_RAP_GTASK_BGPF_###`를 만드세요. 인터페이스 `IF_SERIALIZABLE_OBJECT`, `IF_BGMC_OPERATION`, `IF_BGMC_OP_SINGLE`. 생성자로 Task ID를 받고, `execute`에서 해당 활성 Task에 `completeCheck`를 EML로 실행하세요. 데모로 실행 처음에 5초 기다리세요(오래 걸리는 일 흉내). **`COMMIT ENTITIES`를 쓰지 마세요.**
3. 세이버 `save_modified`에서, 이번 저장에 `CheckStatus`가 `R`로 바뀐 Task마다 bgPF 프로세스를 만들어(`cl_bgmc_process_factory=>get_default( )->create( )`, 이름 `Task check <ID>`, `set_operation`) `save_for_execution` 하세요. bgPF 오류(`cx_bgmc`)는 로그 문장으로 남기세요. 7단계의 상태 로그는 그대로 둡니다.
4. 프로젝션 BDEF에 `use action requestCheck;`를 추가하고, 메타데이터 확장에서 목록과 상세 화면에 `Check in background` 버튼을 만드세요.

**직접 추가할 어노테이션**
- `@UI.lineItem` 의 `type: #FOR_ACTION`, `dataAction` — 목록 표 위에 액션 버튼을 만듦.
- `@UI.identification` 의 `type: #FOR_ACTION`, `dataAction` — Object Page 머리글에 액션 버튼을 만듦.

**확인**
- 미리보기 목록에서 00000002(기한 하루 지남)를 고르고 **Check in background**를 누르면 즉시 CheckStatus = R, Remark = Check requested가 보입니다.
- 5~10초 뒤 목록을 새로고침하면 CheckStatus = F, Status = X, Remark = Checked in background at ... 로 바뀌어 있습니다. 00000004(기한 남음)는 Status가 O로 남습니다.
- `ZCL_RAP_GTASK_LOG_###` 실행 시 `Task 00000002: status -> X`가 보입니다(bgPF가 한 변경도 `save_modified`를 거쳤다는 증거).

<details><summary>정답·해설</summary>

기본 BDEF (최종)

```bdef
managed with additional save implementation in class ZBP_RAP_R_GTASK_### unique;
strict ( 2 );
with draft;
define behavior for ZRAP_R_GTASK_### alias Task
persistent table zrap_gtask_###
draft table zrap_dgtask_###
etag master LocalLastChangedAt
lock master total etag LastChangedAt
authorization master ( global )
{
  field ( readonly )
  CreatedAt,
  CreatedBy,
  LastChangedAt,
  LocalLastChangedAt,
  LocalLastChangedBy;

  field ( readonly )
  CheckStatus,
  Remark;

  field ( mandatory : create, readonly : update )
  TaskID;

  create;
  update;
  delete;

  action requestCheck result [1] $self;     // UI 버튼: 확인 요청 표시
  action completeCheck;                     // bgPF 작업이 EML로 호출 (프로젝션에서 use 안 함)

  draft action Activate optimized;
  draft action Discard;
  draft action Edit;
  draft action Resume;
  draft determine action Prepare;

  mapping for zrap_gtask_###
    {
      TaskID             = task_id;
      Title              = title;
      AgencyID           = agency_id;
      DueDate            = due_date;
      Status             = status;
      CheckStatus        = check_status;
      Remark             = remark;
      CreatedBy          = created_by;
      CreatedAt          = created_at;
      LocalLastChangedBy = local_last_changed_by;
      LocalLastChangedAt = local_last_changed_at;
      LastChangedAt      = last_changed_at;
    }
}
```

프로젝션 BDEF (최종)

```bdef
projection;
strict ( 2 );
use draft;

define behavior for ZRAP_C_GTASK_### alias Task
use etag
{
  use create;
  use update;
  use delete;

  use action requestCheck;

  use action Edit;
  use action Activate;
  use action Discard;
  use action Resume;
  use action Prepare;
}
```

메타데이터 확장에서 `TaskID` 부분만 바꿈

```cds
  @UI: {
    lineItem:       [ { position: 10, importance: #HIGH },
                      { type: #FOR_ACTION, dataAction: 'requestCheck', label: 'Check in background' } ],   // 목록 버튼
    identification: [ { position: 10 },
                      { type: #FOR_ACTION, dataAction: 'requestCheck', label: 'Check in background' } ],   // 상세 버튼
    selectionField: [ { position: 10 } ]
  }
  TaskID;
```

(→ 어노테이션 탭: @UI.lineItem, @UI.identification)

bgPF 작업 클래스

```abap
CLASS zcl_rap_gtask_bgpf_### DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_serializable_object.   " 프로세스와 함께 저장됐다가 나중에 복원됨
    INTERFACES if_bgmc_operation.
    INTERFACES if_bgmc_op_single.         " 트랜잭션 제어(controlled SAP LUW) 작업

    METHODS constructor
      IMPORTING i_task_id TYPE zrap_r_gtask_###-TaskID.

  PRIVATE SECTION.
    CONSTANTS wait_seconds TYPE i VALUE 5.
    DATA task_id TYPE zrap_r_gtask_###-TaskID.
ENDCLASS.


CLASS zcl_rap_gtask_bgpf_### IMPLEMENTATION.

  METHOD constructor.
    task_id = i_task_id.
  ENDMETHOD.

  METHOD if_bgmc_op_single~execute.
    " 오래 걸리는 계산 흉내
    WAIT UP TO wait_seconds SECONDS.

    " 활성 인스턴스에 내부용 액션 실행 (IN LOCAL MODE 아님: 바깥 소비자)
    MODIFY ENTITIES OF zrap_r_gtask_###
      ENTITY Task
        EXECUTE completeCheck
        FROM VALUE #( ( %is_draft = if_abap_behv=>mk-off
                        TaskID    = task_id ) )
      FAILED DATA(failed)
      REPORTED DATA(reported).

    " COMMIT ENTITIES / COMMIT WORK 금지: bgPF가 이 작업 뒤에 커밋하고,
    " 그 커밋이 RAP 저장 순서(save_modified 포함)를 실행한다.
  ENDMETHOD.

ENDCLASS.
```

행동 풀 로컬 클래스 전체 (최종)

```abap
CLASS lhc_task DEFINITION INHERITING FROM cl_abap_behavior_handler.
  PUBLIC SECTION.
    CONSTANTS:
      BEGIN OF task_status,
        open    TYPE c LENGTH 1 VALUE 'O',
        done    TYPE c LENGTH 1 VALUE 'D',
        overdue TYPE c LENGTH 1 VALUE 'X',
      END OF task_status,
      BEGIN OF check_status,
        none      TYPE c LENGTH 1 VALUE ' ',
        requested TYPE c LENGTH 1 VALUE 'R',
        finished  TYPE c LENGTH 1 VALUE 'F',
      END OF check_status.

  PRIVATE SECTION.
    METHODS get_global_authorizations FOR GLOBAL AUTHORIZATION
      IMPORTING REQUEST requested_authorizations FOR Task RESULT result.

    METHODS requestCheck FOR MODIFY
      IMPORTING keys FOR ACTION Task~requestCheck RESULT result.

    METHODS completeCheck FOR MODIFY
      IMPORTING keys FOR ACTION Task~completeCheck.
ENDCLASS.

CLASS lhc_task IMPLEMENTATION.

  METHOD get_global_authorizations.
    " 생성기 뼈대 그대로: 아무것도 막지 않음 (권한 설계는 R-02/R-03)
  ENDMETHOD.

  METHOD requestCheck.
    MODIFY ENTITIES OF zrap_r_gtask_### IN LOCAL MODE
      ENTITY Task
        UPDATE FIELDS ( CheckStatus Remark )
        WITH VALUE #( FOR key IN keys
                      ( %tky        = key-%tky
                        CheckStatus = check_status-requested
                        Remark      = `Check requested` ) ).

    " result [1] $self: 바뀐 인스턴스를 그대로 돌려줌
    READ ENTITIES OF zrap_r_gtask_### IN LOCAL MODE
      ENTITY Task
        ALL FIELDS WITH CORRESPONDING #( keys )
      RESULT DATA(tasks).

    result = VALUE #( FOR task IN tasks
                      ( %tky   = task-%tky
                        %param = task ) ).
  ENDMETHOD.

  METHOD completeCheck.
    READ ENTITIES OF zrap_r_gtask_### IN LOCAL MODE
      ENTITY Task
        FIELDS ( DueDate Status ) WITH CORRESPONDING #( keys )
      RESULT DATA(tasks).

    DATA(today) = cl_abap_context_info=>get_system_date( ).

    MODIFY ENTITIES OF zrap_r_gtask_### IN LOCAL MODE
      ENTITY Task
        UPDATE FIELDS ( Status CheckStatus Remark )
        WITH VALUE #( FOR task IN tasks
                      ( %tky        = task-%tky
                        Status      = COND #( WHEN task-Status = task_status-open AND task-DueDate < today
                                              THEN task_status-overdue
                                              ELSE task-Status )
                        CheckStatus = check_status-finished
                        Remark      = |Checked in background at { utclong_current( ) }| ) ).
  ENDMETHOD.

ENDCLASS.


CLASS lsc_zrap_r_gtask_### DEFINITION INHERITING FROM cl_abap_behavior_saver.
  PROTECTED SECTION.
    METHODS save_modified REDEFINITION.

  PRIVATE SECTION.
    CONSTANTS log_object    TYPE cl_bali_header_setter=>ty_object      VALUE 'ZRAP_GTASK_###'.
    CONSTANTS log_subobject TYPE cl_bali_header_setter=>ty_subobject   VALUE 'STATUS'.
    CONSTANTS log_ext_id    TYPE cl_bali_header_setter=>ty_external_id VALUE 'GTASK'.

    METHODS write_log IMPORTING texts TYPE string_table.
ENDCLASS.

CLASS lsc_zrap_r_gtask_### IMPLEMENTATION.

  METHOD save_modified.
    DATA texts TYPE string_table.

    LOOP AT create-task INTO DATA(created).
      APPEND |Task { created-TaskID } created| TO texts.
    ENDLOOP.

    LOOP AT update-task INTO DATA(updated).
      IF updated-%control-Status = if_abap_behv=>mk-on.
        APPEND |Task { updated-TaskID }: status -> { updated-Status }| TO texts.
      ENDIF.
    ENDLOOP.

    LOOP AT delete-task INTO DATA(deleted).
      APPEND |Task { deleted-TaskID } deleted| TO texts.
    ENDLOOP.

    " 커밋 후 실행될 bgPF 프로세스 등록
    LOOP AT update-task INTO DATA(check_request).
      IF check_request-%control-CheckStatus = if_abap_behv=>mk-on
         AND check_request-CheckStatus = lhc_task=>check_status-requested.
        TRY.
            cl_bgmc_process_factory=>get_default( )->create(
              )->set_name( |Task check { check_request-TaskID }|
              )->set_operation( NEW zcl_rap_gtask_bgpf_###( i_task_id = check_request-TaskID )
              )->save_for_execution( ).
            APPEND |Task { check_request-TaskID }: background check registered| TO texts.
          CATCH cx_bgmc INTO DATA(bgmc_error).
            APPEND |Task { check_request-TaskID }: bgPF error { bgmc_error->get_text( ) }| TO texts.
        ENDTRY.
      ENDIF.
    ENDLOOP.

    IF texts IS NOT INITIAL.
      write_log( texts ).
    ENDIF.
  ENDMETHOD.

  METHOD write_log.
    TRY.
        DATA(log) = cl_bali_log=>create( ).
        log->set_header( header = cl_bali_header_setter=>create( object      = log_object
                                                                 subobject   = log_subobject
                                                                 external_id = log_ext_id ) ).
        LOOP AT texts INTO DATA(text).
          log->add_item( item = cl_bali_free_text_setter=>create( severity = if_bali_constants=>c_category_free_text
                                                                  text     = CONV #( text ) ) ).
        ENDLOOP.
        cl_bali_log_db=>get_instance( )->save_log( log = log ).
      CATCH cx_bali_runtime.
        " 로그 실패는 업무 저장을 막지 않음
    ENDTRY.
  ENDMETHOD.

ENDCLASS.
```


**왜 이렇게 쓰나**
- 이 구조는 SAP 공식 예제 `abap-platform-bgpf-appl-log-events-side-effects`와 같습니다. 그 예제도 (1) 액션이 상태 필드 하나만 바꾸고, (2) `save_modified`에서 그 필드의 `%control`을 보고 `cl_bgmc_process_factory=>get_default( )->create( )->set_name( )->set_operation( )->save_for_execution( )`을 부르고, (3) 작업 클래스(`if_serializable_object`, `if_bgmc_operation`, `if_bgmc_op_single`)의 `execute`에서 `READ/MODIFY ENTITIES`로 BO를 다시 바꾸며 **`COMMIT ENTITIES`를 쓰지 않습니다**. 예제 README는 "백그라운드 프로세스는 RAP 프레임워크가 `COMMIT WORK`를 수행한 직후 등록·실행된다"고 설명합니다.
- **왜 `save_modified`에서 등록하나**: bgPF 프로세스는 등록한 트랜잭션이 **커밋될 때** 실제로 시작됩니다. 액션 안(상호작용 단계)에서 등록하면 사용자가 draft를 버리거나 저장이 실패한 경우에도 남을 수 있습니다. late save에서 등록하면 "업무 데이터가 저장된 경우에만" 백그라운드 일이 시작됩니다.
- **왜 `COMMIT ENTITIES`를 쓰지 않나**: cheat sheet는 `if_bgmc_op_single`(트랜잭션 제어 있는 bgPF)에서 "RAP 맥락이면 COMMIT/ROLLBACK을 구현할 필요가 없으며 RAP 프레임워크가 처리한다"고 하고, EML cheat sheet 표도 bgPF 맥락에서 commit/rollback 문은 허용되지 않는다고 적습니다. 대신 `if_bgmc_op_single_tx_uncontr`(트랜잭션 제어 없음)를 구현하면 직접 `COMMIT WORK`를 해야 합니다.
- **왜 `completeCheck`를 따로 두나**: `CheckStatus`, `Remark`는 읽기 전용이라 바깥 소비자(bgPF 작업)의 `UPDATE`는 거부됩니다. 바깥에서는 **액션만 부르고**, 액션 구현이 `IN LOCAL MODE`로 읽기 전용 필드를 바꾸는 구조입니다. 프로젝션에서 `use`하지 않았으므로 OData(Fiori)로는 부를 수 없습니다.
- **bgPF가 바꾼 것도 로그에 남는 이유**: 작업이 끝난 뒤 bgPF가 커밋하면 RAP 저장 순서가 다시 돌아 `save_modified`가 불리고, `%control-Status`가 켜져 있으므로 상태 로그가 남습니다. 이때 `CheckStatus`는 `F`이므로 bgPF가 다시 등록되지 않습니다(무한 반복 방지 조건).
- **화면 자동 새로고침**: 공식 예제는 여기서 한 걸음 더 나아가, `save_modified`에서 `Quantity`가 바뀌면 `RAISE ENTITY EVENT`로 **side effects용 이벤트**(`event QuantityUpdated for side effects;`, `side effects { event QuantityUpdated affects field ( Quantity ); }`, 프로젝션에 `use side effects;`와 `use event QuantityUpdated;`)를 발생시켜 UI가 스스로 값을 다시 읽게 합니다. 이 구문은 R-04에서 다뤘으므로 Task BO에 붙이는 것은 연습으로 남깁니다. 예제 README는 이벤트 기반 사이드 이펙트가 **SAP BTP ABAP Environment와 S/4HANA Cloud Public Edition에서만** 가능하다고 적습니다.

**트라이얼 제약**
- 공식 예제 README: bgPF는 BTP ABAP Environment에서 쓸 수 있고, 온프레미스·Private Cloud는 2023 릴리스부터입니다. 트라이얼에서 bgPF 실행에 별도 설정이 필요한지는 확인하지 못했습니다. 5~10초 뒤에도 CheckStatus가 R로 남으면 `STATUS` 로그에 `background check registered`가 있는지, `bgPF error`가 있는지 보세요(실제 시스템에서 확인 필요).
- bgPF 프로세스 모니터링: `save_for_execution`은 프로세스 모니터 객체를 돌려주며 공식 예제는 `->to_string( )`으로 문자열을 받아 필드에 저장합니다. cheat sheet는 실행 흐름 확인에 ABAP Cross Trace를 쓸 수 있다고 안내합니다.

**자주 나는 오류와 해결**
- 런타임 오류 `BEHAVIOR_ILLEGAL_STMT_IN_CALL`: 트랜잭션 단계에 맞지 않는 문(예: `execute` 안의 `COMMIT WORK`, 상호작용 단계의 DB 쓰기)을 썼을 때 납니다(cheat sheet `cl_abap_tx` 설명).
- 사용자가 그 Task를 Edit 중(draft 존재)이면 활성 인스턴스가 잠겨 `completeCheck`가 `failed`(잠금)로 끝나고, CheckStatus가 R로 남습니다. 이 작업은 실패를 사용자에게 알릴 화면이 없으므로, 운영 코드라면 `failed`를 애플리케이션 로그에 남기세요(9단계 잡 클래스가 그 방법을 보여 줍니다).

**클래스 구조 해설**
- `requestCheck`, `completeCheck`의 시그니처는 BDEF의 `action` 줄에서 생깁니다. `result [1] $self`가 있으면 `RESULT result`가 붙고 행 타입에 `%param`(엔터티 전체 구조)이 생깁니다.
- `lhc_task=>check_status`처럼 세이버에서 핸들러 상수를 쓰려고 상수를 핸들러의 PUBLIC SECTION에 두었습니다(같은 로컬 include 안이므로 접근 가능).
- `if_bgmc_op_single~execute`는 bgPF가 새 작업 프로세스에서 **역직렬화한 객체**에 대해 부릅니다. 그래서 생성자에서 받은 `task_id`(인스턴스 속성)가 직렬화 대상이 되도록 `if_serializable_object`가 필요합니다.

</details>

#### 9단계. 애플리케이션 잡 클래스: 잡 안에서 EML과 `COMMIT ENTITIES`

요구사항
1. 클래스 `ZCL_RAP_GTASK_JOB_###`를 만들고 `IF_APJ_RT_RUN`(잡 실행)과 `IF_OO_ADT_CLASSRUN`(콘솔 시험)을 구현하세요.
2. 잡 파라미터 하나를 **공개 속성** `simulate`(`abap_boolean`)로 두세요. `X`이면 아무것도 바꾸지 않고 대상만 로그에 남깁니다.
3. 실행 로직(비공개 메서드 `run`):
   - 기본 뷰 `ZRAP_R_GTASK_###`에서 상태 `O`이고 기한이 오늘보다 이전인 Task를 읽으세요.
   - `simulate`가 아니면 EML로 활성 인스턴스의 `Status`를 `X`로 바꾸고 `COMMIT ENTITIES RESPONSE OF ...`로 저장하세요.
   - 실패(`failed-task`, 원인 `%fail-cause`)와 커밋 결과를 문장으로 모으세요.
   - 모은 문장을 애플리케이션 로그(하위 객체 `JOB`, 외부 ID `GTASK`)에 저장하고, 잡으로 실행 중이면 로그를 **현재 잡에 연결**하세요.
4. 콘솔 실행(F9)은 `simulate = abap_true`로 돌려 문장을 화면에 출력하세요.

**확인**
- 1단계 데이터를 다시 넣은 뒤 F9: `2 overdue task(s), simulate = X`와 00000001, 00000002가 출력되고 데이터는 바뀌지 않습니다.
- Fiori에서 00000001을 Edit 상태로 둔(저장하지 않은) 채로 10단계에서 잡을 돌리면, 00000001은 잠금으로 실패하고 00000002만 X가 됩니다.

<details><summary>정답·해설</summary>

```abap
CLASS zcl_rap_gtask_job_### DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_apj_rt_run.         " 애플리케이션 잡이 부르는 execute
    INTERFACES if_oo_adt_classrun.    " F9 시험용

    "! 잡 파라미터 (잡 템플릿·예약에서 이름 SIMULATE로 값 전달)
    DATA simulate TYPE abap_boolean.

  PRIVATE SECTION.
    CONSTANTS:
      BEGIN OF task_status,
        open    TYPE c LENGTH 1 VALUE 'O',
        overdue TYPE c LENGTH 1 VALUE 'X',
      END OF task_status.
    CONSTANTS log_object    TYPE cl_bali_header_setter=>ty_object      VALUE 'ZRAP_GTASK_###'.
    CONSTANTS log_subobject TYPE cl_bali_header_setter=>ty_subobject   VALUE 'JOB'.
    CONSTANTS log_ext_id    TYPE cl_bali_header_setter=>ty_external_id VALUE 'GTASK'.

    METHODS run
      IMPORTING in_job          TYPE abap_boolean
      RETURNING VALUE(messages) TYPE string_table.

    METHODS save_log
      IMPORTING messages TYPE string_table
                in_job   TYPE abap_boolean.
ENDCLASS.


CLASS zcl_rap_gtask_job_### IMPLEMENTATION.

  METHOD if_apj_rt_run~execute.
    " 잡 프레임워크가 공개 속성 simulate를 채운 뒤 호출
    run( in_job = abap_true ).
  ENDMETHOD.


  METHOD if_oo_adt_classrun~main.
    simulate = abap_true.                       " 콘솔에서는 바꾸지 않고 보기만
    out->write( run( in_job = abap_false ) ).
  ENDMETHOD.


  METHOD run.
    DATA(today) = cl_abap_context_info=>get_system_date( ).

    SELECT FROM zrap_r_gtask_###
      FIELDS TaskID, DueDate
      WHERE Status  = @task_status-open
        AND DueDate < @today
      ORDER BY TaskID
      INTO TABLE @DATA(overdue_tasks).

    APPEND |Run at { utclong_current( ) }: { lines( overdue_tasks ) } overdue task(s), simulate = { simulate }|
      TO messages.

    IF overdue_tasks IS INITIAL OR simulate = abap_true.
      LOOP AT overdue_tasks INTO DATA(candidate).
        APPEND |  candidate { candidate-TaskID } (due { candidate-DueDate DATE = ISO })| TO messages.
      ENDLOOP.
      save_log( messages = messages in_job = in_job ).
      RETURN.
    ENDIF.

    " 바깥 소비자로서 EML: 권한·기능 제어·잠금이 모두 적용됨
    MODIFY ENTITIES OF zrap_r_gtask_###
      ENTITY Task
        UPDATE FIELDS ( Status )
        WITH VALUE #( FOR row IN overdue_tasks
                      ( %is_draft = if_abap_behv=>mk-off     " 활성 인스턴스
                        TaskID    = row-TaskID
                        Status    = task_status-overdue ) )
      FAILED DATA(failed)
      REPORTED DATA(reported).

    LOOP AT failed-task INTO DATA(failed_line).
      APPEND |  { failed_line-TaskID }: update failed, cause { failed_line-%fail-cause }| TO messages.
    ENDLOOP.

    " 잡은 RAP 바깥의 트랜잭션 소유자 → 직접 저장을 요청
    COMMIT ENTITIES
      RESPONSE OF zrap_r_gtask_###
      FAILED DATA(failed_commit)
      REPORTED DATA(reported_commit).

    IF sy-subrc <> 0.
      APPEND `  COMMIT ENTITIES failed` TO messages.
      LOOP AT reported_commit-task INTO DATA(reported_line).
        IF reported_line-%msg IS BOUND.
          APPEND |  { reported_line-TaskID }: { reported_line-%msg->if_message~get_text( ) }| TO messages.
        ENDIF.
      ENDLOOP.
    ELSE.
      APPEND |  { lines( overdue_tasks ) - lines( failed-task ) } task(s) set to overdue| TO messages.
    ENDIF.

    save_log( messages = messages in_job = in_job ).
  ENDMETHOD.


  METHOD save_log.
    TRY.
        DATA(log) = cl_bali_log=>create( ).
        log->set_header( header = cl_bali_header_setter=>create( object      = log_object
                                                                 subobject   = log_subobject
                                                                 external_id = log_ext_id ) ).
        LOOP AT messages INTO DATA(text).
          log->add_item( item = cl_bali_free_text_setter=>create( severity = if_bali_constants=>c_category_free_text
                                                                  text     = CONV #( text ) ) ).
        ENDLOOP.
        " assign_to_current_appl_job: 잡 로그 화면에서 이 로그가 보이게 연결 (실제 시스템에서 확인 필요)
        cl_bali_log_db=>get_instance( )->save_log( log                        = log
                                                   assign_to_current_appl_job = in_job ).
        COMMIT WORK.   " 잡·콘솔은 RAP 바깥이므로 로그를 직접 커밋
      CATCH cx_bali_runtime.
        " 로그 실패는 잡 결과를 바꾸지 않음
    ENDTRY.
  ENDMETHOD.

ENDCLASS.
```

**왜 이렇게 쓰나**
- **`if_apj_rt_run`**: cheat sheet의 Application Jobs 예제가 쓰는 인터페이스입니다. "애플리케이션 잡의 전제는 `if_apj_rt_run`을 구현한 클래스이며, 잡이 그 `execute`를 실행한다"고 설명하고, 잡 파라미터는 **공개 속성**(`DATA text TYPE c LENGTH 10`)으로 두고 예약할 때 `name = 'TEXT'`로 값을 넘깁니다. 이 문제의 `simulate`도 같은 방식입니다.
- **예전 방식 `if_apj_dt_exec_object` / `if_apj_rt_exec_object`**: 이전 튜토리얼과 기존 코드에서는 설계 시점 인터페이스 `if_apj_dt_exec_object~get_parameters`(파라미터 정의 `et_parameter_def`와 기본값 `et_parameter_val`을 돌려줌)와 실행 인터페이스 `if_apj_rt_exec_object~execute`(`it_parameters`로 값을 받음)의 조합을 씁니다. 이 문제 작성 중 로컬·GitHub 공식 예제에서 이 두 인터페이스 코드를 열어 보지 못했으므로, 아래 골격은 **기억에 의존한 참고용**입니다(실제 시스템에서 확인 필요).

```abap
" 참고용: 예전 인터페이스 조합 (시그니처·컴포넌트 이름은 실제 시스템에서 확인 필요)
CLASS zcl_rap_gtask_job_old_### DEFINITION PUBLIC FINAL CREATE PUBLIC.
  PUBLIC SECTION.
    INTERFACES if_apj_dt_exec_object.
    INTERFACES if_apj_rt_exec_object.
ENDCLASS.

CLASS zcl_rap_gtask_job_old_### IMPLEMENTATION.
  METHOD if_apj_dt_exec_object~get_parameters.
    et_parameter_def = VALUE #( ( selname        = 'P_SIMUL'
                                  kind           = if_apj_dt_exec_object=>parameter
                                  datatype       = 'C'
                                  length         = 1
                                  param_text     = 'Simulate only'
                                  checkbox_ind   = abap_true
                                  changeable_ind = abap_true ) ).
    et_parameter_val = VALUE #( ( selname = 'P_SIMUL'
                                  kind    = if_apj_dt_exec_object=>parameter
                                  sign    = 'I'
                                  option  = 'EQ'
                                  low     = abap_true ) ).
  ENDMETHOD.

  METHOD if_apj_rt_exec_object~execute.
    DATA simulate TYPE abap_boolean.
    LOOP AT it_parameters INTO DATA(parameter).
      CASE parameter-selname.
        WHEN 'P_SIMUL'.
          simulate = parameter-low.
      ENDCASE.
    ENDLOOP.
    " ... 이후 로직은 zcl_rap_gtask_job_###=>run과 같음
  ENDMETHOD.
ENDCLASS.
```

- **잡 안의 EML은 "바깥 소비자"입니다**: `IN LOCAL MODE`가 아니므로 전역 권한, 기능 제어, 읽기 전용 필드, 잠금이 모두 적용됩니다. `Status`는 읽기 전용이 아니라서 직접 `UPDATE`할 수 있습니다(반대로 `CheckStatus`는 8단계처럼 액션을 거쳐야 합니다).
- **잠금 실패**: 사용자가 Edit 중이면 draft가 활성 인스턴스를 독점 잠금하므로 `failed-task`에 그 Task가 들어오고 `%fail-cause`가 잠금 원인(`if_abap_behv=>cause-locked`)이 됩니다. 잡은 실패한 건만 로그에 남기고 나머지는 커밋합니다.
- **권한**: 잡은 예약한 사용자(또는 운영에서는 기술 사용자) 권한으로 돕니다. RAP630 연습 1.2는 잡에서 쓰는 사용자에게 업무 권한이 없을 수 있으므로 `MODIFY ENTITIES ... PRIVILEGED`(BDEF가 privileged mode를 허용하는 경우)를 쓰는 예를 보여 줍니다. 이 Task BO는 권한 검사가 비어 있어 필요 없습니다.
- **`COMMIT ENTITIES RESPONSE OF`**: RAP630 연습 1.2와 같은 형태입니다. `sy-subrc`가 0이 아니면 저장 실패이며, late 단계의 메시지는 `reported_commit`에 있습니다.
- **로그 커밋**: 잡과 콘솔 클래스는 RAP 핸들러가 아니므로 트랜잭션 소유자로서 `COMMIT WORK`를 할 수 있습니다(cheat sheet의 잡 예제도 `execute` 안에서 `COMMIT WORK`). 커밋을 업무 저장(`COMMIT ENTITIES`) **뒤**에 두어, 업무 저장이 성공했든 실패했든 로그는 남게 했습니다.
- `assign_to_current_appl_job` 매개변수는 공식 예제 코드에서 열어 보지 못했습니다. 활성화 오류가 나면 이 매개변수를 지우세요. 그러면 로그는 저장되지만 잡 로그 화면과 연결되지 않고, `ZCL_RAP_GTASK_LOG_###`로는 여전히 볼 수 있습니다(실제 시스템에서 확인 필요).

**클래스 구조 해설**
- `if_apj_rt_run~execute`는 BDEF와 무관한 인터페이스 메서드이며, 잡 프레임워크가 클래스 인스턴스를 만들고 **공개 속성에 파라미터 값을 넣은 뒤** 부릅니다(cheat sheet 설명).
- `failed-task`, `reported_commit-task`의 `task`는 BDEF 엔터티 별칭입니다. `COMMIT ENTITIES RESPONSE OF zrap_r_gtask_###`의 응답 타입도 BDEF에서 생기는 late 응답 파생 타입입니다.

</details>

#### 10단계. 잡 카탈로그·템플릿 만들고 예약하기

요구사항
1. 패키지에서 **New > Other ABAP Repository Object > Application Job Catalog Entry**로 `ZRAP_GTASK_JC_###`(설명 `Mark overdue tasks`)를 만들고, 클래스 `ZCL_RAP_GTASK_JOB_###`를 지정해 활성화하세요.
2. **Application Job Template** `ZRAP_GTASK_JT_###`(설명 `Mark overdue tasks - default`)를 만들어 카탈로그 항목을 지정하고, 파라미터 `SIMULATE` 기본값을 비워(= 실제 변경) 저장하세요. (두 메뉴 이름은 실제 시스템에서 확인)
3. 콘솔 클래스 `ZCL_RAP_GTASK_SCHED_###`를 만들어
   - `cl_apj_rt_api=>schedule_job`으로 템플릿을 **즉시 1회** 실행하도록 예약하고(파라미터 `SIMULATE` = 공백), 잡 이름·번호를 출력하세요.
   - 15초 기다린 뒤 `cl_apj_rt_api=>get_job_status`로 상태와 상태 텍스트를 출력하세요.
   - 마지막으로 Task 전체(번호, 기한, 상태)를 출력하세요.
4. 실행 후 `ZCL_RAP_GTASK_LOG_###`로 `JOB`, `STATUS` 로그를 확인하세요.
5. 정답 해설을 보고 "매분 반복, 30분 뒤 종료" 예약과 잡 목록 조회·취소 방법을 적으세요.

**확인**
- 스케줄 클래스 출력: 잡 이름/번호, 상태(완료 상태 코드와 텍스트), Task 00000001·00000002의 상태가 X.
- 로그 클래스 출력: `JOB` 아래 `... 2 overdue task(s), simulate =` 와 `2 task(s) set to overdue`, `STATUS` 아래 `Task 00000001: status -> X`, `Task 00000002: status -> X`.

<details><summary>정답·해설</summary>

```abap
CLASS zcl_rap_gtask_sched_### DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_oo_adt_classrun.

  PRIVATE SECTION.
    CONSTANTS template_name TYPE cl_apj_dt_create_content=>ty_template_name VALUE 'ZRAP_GTASK_JT_###'.
    CONSTANTS job_text      TYPE cl_apj_rt_api=>ty_job_text                VALUE 'Mark overdue tasks'.
    CONSTANTS wait_seconds  TYPE i VALUE 15.
ENDCLASS.


CLASS zcl_rap_gtask_sched_### IMPLEMENTATION.

  METHOD if_oo_adt_classrun~main.
    " 1) 즉시 1회 실행 예약
    TRY.
        cl_apj_rt_api=>schedule_job(
          EXPORTING
            iv_job_template_name   = template_name
            iv_job_text            = job_text
            is_start_info          = VALUE #( start_immediately = abap_true )
            " 반복 정보 없음 = 1회 (필수 여부·기본값은 실제 시스템에서 확인 필요)
            is_scheduling_info     = VALUE #( test_mode = abap_false
                                              timezone  = 'UTC' )
            it_job_parameter_value = VALUE #( ( name    = 'SIMULATE'          " 공개 속성 이름
                                                t_value = VALUE #( ( sign = 'I' option = 'EQ' low = abap_false ) ) ) )
          IMPORTING
            ev_jobname             = DATA(jobname)
            ev_jobcount            = DATA(jobcount) ).

        out->write( |Job scheduled: { jobname } / { jobcount }| ).

      CATCH cx_apj_rt INTO DATA(schedule_error).
        out->write( schedule_error->get_longtext( ) ).
        RETURN.
    ENDTRY.

    " 2) 잡이 돌 시간을 줌 (데모용)
    WAIT UP TO wait_seconds SECONDS.

    " 3) 상태 확인
    TRY.
        cl_apj_rt_api=>get_job_status(
          EXPORTING
            iv_jobname         = jobname
            iv_jobcount        = jobcount
          IMPORTING
            ev_job_status      = DATA(job_status)
            ev_job_status_text = DATA(job_status_text) ).

        out->write( |Job status: { job_status } { job_status_text }| ).

      CATCH cx_apj_rt INTO DATA(status_error).
        out->write( status_error->get_longtext( ) ).
    ENDTRY.

    " 4) 결과 데이터
    SELECT FROM zrap_r_gtask_###
      FIELDS TaskID, DueDate, Status, CheckStatus
      ORDER BY TaskID
      INTO TABLE @DATA(tasks).
    out->write( tasks ).
  ENDMETHOD.

ENDCLASS.
```

**왜 이렇게 쓰나**
- 잡 관련 객체는 세 겹입니다: **클래스**(무엇을 할지) → **카탈로그 항목**(이 클래스를 잡으로 쓸 수 있게 등록, 파라미터 정의) → **템플릿**(파라미터 기본값을 채운 실행 단위). 예약 API와 Fiori 앱은 모두 **템플릿 이름**으로 잡을 만듭니다.
- 메서드·매개변수 이름(`schedule_job`의 `iv_job_template_name`, `iv_job_text`, `is_start_info-start_immediately`, `it_job_parameter_value`의 `name`/`t_value`, `ev_jobname`/`ev_jobcount`, `get_job_status`의 `ev_job_status`/`ev_job_status_text`, 예외 `cx_apj_rt`)은 cheat sheet 예제와 같습니다.
- `is_scheduling_info`: cheat sheet는 매분 반복 예제만 보여 줍니다(아래). 1회 실행에서 이 매개변수를 생략할 수 있는지, `timezone`만 줘도 되는지는 확인하지 못했습니다. 활성화 시 "필수 매개변수"류 오류가 나면 cheat sheet처럼 모든 필드를 주고, 반대로 오류가 나면 이 줄을 지우세요(실제 시스템에서 확인 필요).

cheat sheet의 반복 예약과 잡 관리(이름만 이 문제에 맞춤)

```abap
" 매분 반복, 30분 뒤 종료 (cheat sheet 예제와 같은 매개변수)
GET TIME STAMP FIELD DATA(ts).
cl_apj_rt_api=>schedule_job(
  EXPORTING
    iv_job_template_name   = 'ZRAP_GTASK_JT_###'
    iv_job_text            = 'Mark overdue tasks (every minute)'
    is_start_info          = VALUE #( start_immediately = abap_true )
    is_scheduling_info     = VALUE #( test_mode            = abap_false
                                      periodic_granularity = 'MI'       " 분 단위
                                      periodic_value       = '1'
                                      timezone             = 'UTC' )
    is_end_info            = VALUE #( type      = 'DATE'              " 시각으로 종료
                                      timestamp = cl_abap_tstmp=>move_to_short(
                                                    cl_abap_tstmp=>add( tstmp = ts secs = 1800 ) ) )
    it_job_parameter_value = VALUE #( ( name    = 'SIMULATE'
                                        t_value = VALUE #( ( sign = 'I' option = 'EQ' low = abap_true ) ) ) )
  IMPORTING
    ev_jobname             = DATA(jobname)
    ev_jobcount            = DATA(jobcount) ).

" 카탈로그 항목 기준 잡 목록 조회와 취소
DATA(jobs) = cl_apj_rt_api=>find_jobs_with_jce( 'ZRAP_GTASK_JC_###' ).
LOOP AT jobs INTO DATA(job).
  cl_apj_rt_api=>cancel_job( iv_jobname  = job-jobname
                             iv_jobcount = job-jobcount ).
ENDLOOP.
```

(위 조각은 `TRY ... CATCH cx_apj_rt`로 감싸서 쓰세요. 반복 잡은 시험이 끝나면 **반드시 취소**하세요. 공유 트라이얼에서 매분 도는 잡은 다른 사용자에게도 부담입니다.)

**카탈로그·템플릿을 코드로 만들기**: cheat sheet는 ADT 대신 `cl_apj_dt_create_content=>get_instance( )`의 `exists_job_cat_entry`, `create_job_cat_entry( iv_catalog_name, iv_class_name, iv_text, iv_catalog_entry_type = cl_apj_dt_create_content=>class_based, iv_transport_request, iv_package )`, `create_job_template_entry( iv_template_name, iv_catalog_name, iv_text, iv_transport_request, iv_package )`, 그리고 삭제 메서드를 보여 줍니다. 패키지가 `ZLOCAL` 아래의 로컬 패키지면 전송 요청을 비워야 하는지 등은 시스템마다 다를 수 있습니다(실제 시스템에서 확인 필요).

**트라이얼 제약**
- 운영 시스템에서는 관리자가 Fiori 앱(애플리케이션 잡 앱)에서 템플릿을 골라 예약·모니터링합니다. 트라이얼 사용자는 관리자 비즈니스 역할이 없어 이 앱을 못 쓸 가능성이 큽니다. 그래서 이 문제는 `cl_apj_rt_api`로 예약하고 콘솔·로그로 확인합니다. API 예약 자체에도 권한이 필요할 수 있으며, `cx_apj_rt` 예외 텍스트에 권한 관련 내용이 나오면 트라이얼 제약입니다(실제 시스템에서 확인 필요).
- 잡이 바로 시작되지 않을 수 있습니다(공유 시스템의 백그라운드 작업 프로세스 상황). 상태가 아직 예약/진행이면 몇 분 뒤 스케줄 클래스의 3~4번 부분만 다시 실행하세요.

</details>

#### 11단계. BAS에서 Fiori elements 앱을 만들어 ABAP 환경에 배포하고 런치패드에 올리기

요구사항
1. 아래 흐름을 순서대로 따라 하되, **트라이얼에서 막히는 지점이 어디인지** 표시하며 진행하세요. 막힌 단계 이후는 "운영 시스템이라면 무엇을 할지" 문장으로 적으세요.
   1) BTP 트라이얼 계정에서 SAP Business Application Studio를 열고 **SAP Fiori** 유형 개발 공간(Dev Space)을 만들어 시작합니다.
   2) Fiori 앱 생성기(Template Wizard)에서 **List Report Page**(OData V4)를 고릅니다.
   3) 데이터 소스: **Connect to a System** → ABAP 환경 → 서비스 `ZRAP_UI_GTASK_O4_###`(2단계에서 Publish 한 것), 메인 엔터티 `Task`.
   4) 프로젝트 속성: 모듈 이름 `ztask###`, 앱 제목 `Tasks (###)`, **배포 설정 추가 = 예**, **FLP(런치패드) 설정 추가 = 예**.
   5) 배포 설정: 대상 ABAP, SAPUI5 ABAP 저장소 이름 `ZTASK###`, 패키지 `ZRAP_###`, 전송 요청.
   6) FLP 설정: 시맨틱 객체 `ZRAPTask###`, 액션 `manage`, 타일 제목 `Tasks (###)`.
   7) 로컬 미리보기(`npm start` 또는 생성기가 만든 실행 구성)로 앱이 뜨는지 확인한 뒤, 터미널에서 `npm run deploy`로 배포합니다.
   8) ADT에서 패키지를 새로고침해 배포로 생긴 객체를 확인합니다.
   9) IAM 앱: 앱에 서비스 `ZRAP_UI_GTASK_O4_###`를 추가하고 Publish Locally.
   10) 비즈니스 카탈로그 `ZRAP_GTASK_BC_###`: IAM 앱을 할당하고 Publish Locally.
   11) 관리자: 비즈니스 역할 만들기 → 카탈로그 추가 → 사용자 할당 → 런치패드 공간·페이지에 타일 배치.
2. ADT Fiori 미리보기(2단계)와 배포된 앱의 차이를 세 가지 적으세요.

**확인**
- (가능한 곳까지) BAS 로컬 미리보기에 Task 목록이 나오고, 8·9번까지 되면 ADT 패키지에 UI5 앱 관련 객체와 IAM 앱이 보입니다.
- 운영 시스템이라면 런치패드에 `Tasks (###)` 타일이 보이고, 눌렀을 때 목록이 열립니다.

<details><summary>정답·해설</summary>

이 단계는 ABAP 코드가 없는 도구 흐름입니다. 이 문제를 쓰면서 BAS·배포·IAM 관련 공식 문서는 열어 보지 못했고(help.sap.com 자동 조회 불가), RAP630 연습 1.1의 "문제 해결" 안내만 확인했습니다. 아래는 그 안내와 일반적으로 알려진 흐름을 정리한 것이며, 화면 이름·옵션은 **모두 실제 시스템에서 확인 필요**입니다.

**단계별 해설**

| 단계 | 하는 일 | 왜 필요한가 | 트라이얼 |
|---|---|---|---|
| 1) Dev Space | Fiori 도구(생성기, 미리보기, 배포 스크립트)가 든 개발 환경 | ADT에는 UI5 앱 프로젝트를 만드는 도구가 없음 | BTP 트라이얼에서 BAS 구독이 가능한 것으로 알려짐(확인 필요) |
| 2)~3) 생성기 | `manifest.json`(데이터 소스 = 서비스 URL, 엔터티), `webapp`, `ui5.yaml` 생성 | Fiori elements 앱은 **서비스 메타데이터 + 어노테이션**으로 화면을 그림. ABAP 쪽 MDE가 그대로 쓰임 | ABAP 트라이얼은 SAP가 운영하는 별도 서브계정이라, 자기 BAS에서 시스템 연결이 되는지가 첫 관문(확인 필요) |
| 4)~6) 배포·FLP 설정 | `ui5-deploy.yaml`(대상 시스템, 저장소 이름, 패키지, 전송), 앱 설명자에 시맨틱 객체·액션 | 런치패드는 "시맨틱 객체 + 액션"으로 앱을 찾음(인텐트 기반 탐색) | 설정 파일 생성은 가능 |
| 7) 배포 | `npm run deploy`가 빌드 결과를 ABAP 환경의 UI5 저장소에 올림 | 앱 파일이 ABAP 시스템에 있어야 런치패드에서 열림 | 개발 사용자에게 배포 권한이 있는지 확인 필요 |
| 8) ADT 확인 | 패키지에 UI5 앱(BSP 저장소 객체), 앱 설명자 관련 객체가 생김. 시스템 버전에 따라 IAM 앱이 자동 생성되기도 함 | 배포 결과도 전송 가능한 개발 객체 | 확인 필요 |
| 9) IAM 앱 | 앱이 쓰는 **서비스(OData V4 바인딩)** 와 필요한 권한 객체를 묶음. 없으면 ADT에서 New > IAM App으로 만들고 앱 ID를 연결 | 런치패드 사용자가 그 서비스를 호출할 권한의 단위 | 생성은 될 수 있으나 의미 있는 확인은 11)이 필요 |
| 10) 비즈니스 카탈로그 | IAM 앱 여러 개를 업무 단위로 묶음 | 역할에 할당하는 최소 단위 | 위와 같음 |
| 11) 비즈니스 역할·공간·페이지 | 관리자가 Fiori 관리 앱에서 역할 생성, 카탈로그 추가, 사용자 할당, 런치패드 레이아웃 | 사용자가 타일을 보고 앱을 열 수 있게 하는 마지막 단계 | **트라이얼 사용자는 관리자 역할이 없어 불가**로 보는 것이 안전 |

**RAP630이 보여 주는 IAM의 의미**: RAP630 연습 1.1에서 생성기로 만든 은행 앱이 "이 국가의 은행을 만들 권한이 없음" 오류를 내자, 문서는 "적절한 IAM 앱을 만들어 비즈니스 카탈로그에 넣고, 그 카탈로그를 역할에 넣어 사용자에게 할당해야만 해결된다"고 설명합니다. 즉 **IAM 앱 → 비즈니스 카탈로그 → 비즈니스 역할 → 사용자**가 ABAP 환경 권한의 표준 사슬이고, 런치패드 등록도 같은 사슬을 탑니다. ADT Fiori 미리보기가 권한 없이 되는 것은 **개발자 테스트용**이기 때문입니다.

**ADT 미리보기와 배포 앱의 차이**
1. 미리보기는 ADT가 서비스 바인딩에서 즉석으로 띄우는 **테스트 화면**이고 `manifest.json`을 고칠 수 없습니다. 배포 앱은 BAS에서 `manifest.json`(라우팅, 변형 관리, 페이지 설정, 확장 코드)을 직접 바꿀 수 있습니다.
2. 미리보기는 개발자 본인만 씁니다. 배포 앱은 IAM·카탈로그·역할을 통해 **업무 사용자**에게 배포됩니다.
3. 배포 앱은 런치패드 인텐트(시맨틱 객체·액션)를 가져 다른 앱에서 탐색해 올 수 있고, 전송 요청으로 다음 시스템에 옮겨집니다.

**트라이얼에서 현실적인 목표**
- 확실히 되는 것: 2단계의 ADT Fiori 미리보기(이 문제의 모든 기능 확인 가능).
- 될 수도 있는 것: BAS에서 앱 생성과 로컬 미리보기, 배포(시스템 연결·권한에 달림).
- 안 되는 것으로 보는 것이 안전: 비즈니스 역할 관리와 런치패드 공간·페이지 설정(관리자 앱 필요).

**자주 나는 오류와 해결**
- 생성기에서 서비스가 안 보임: 서비스 바인딩을 Publish 했는지, OData **V4** 바인딩인지 확인하세요(List Report OData V4 템플릿은 V4 서비스만 보여 줌).
- 배포 시 저장소 이름 오류: SAPUI5 ABAP 저장소 이름은 길이 제한이 있습니다(짧게, 대문자 `Z`로 시작). 정확한 최대 길이는 생성기 입력 검사 메시지로 확인하세요(실제 시스템에서 확인 필요).

</details>

## 출처

- SAP-samples/abap-platform-rap100 — `exercises/ex01/README.md`(테이블에서 Generate ABAP Repository Objects → OData UI Service, 생성기 이름 표, 생성 객체 설명, MDE `selectionField` 수정, 생성기 오류 안내), `exercises/ex02/README.md`(생성된 C 뷰의 `semanticKey`, `@AccessControl` 경고), `exercises/ex03/README.md`(생성된 BDEF의 `mandatory : create`/`readonly : update`, 관리 필드 read-only), `src/`(`zrap100_r_traveltp_sol` CDS·BDEF, `zrap100_c_traveltp_sol` CDS·BDEF·DDLX, `zrap100_bp_traveltp_sol` 클래스, `zrap100_ui_travel_sol` SRVD): https://github.com/SAP-samples/abap-platform-rap100
- SAP-samples/abap-platform-rap110 — `exercises/ex01/README.md`(생성 클래스 `ZDMO_GEN_RAP110_SINGLE`로 패키지·BO 생성): https://github.com/SAP-samples/abap-platform-rap110
- SAP-samples/abap-platform-rap-workshops — `rap6xx/rap620/exercises/ex3/README.md`와 `sources/ex2_CLAS_zcl_ce_rap_products_####_step_2.txt`(Service Consumption Model 생성 절차, 생성 클래스 `tys_`/`tyt_` 타입, `/iwbep/cl_cp_factory_remote=>create_v2_remote_proxy`, `create_by_url`, `create_by_cloud_destination` 언급, custom entity 값 도움말, 트라이얼 주의문): https://github.com/SAP-samples/abap-platform-rap-workshops/tree/main/rap6xx/rap620
- SAP-samples/abap-platform-rap-opensap — `week5/unit2.md`, `unit3.md`, `unit4.md`, `sources/$metadata.xml`, `W5U2_CLAS_zcl_ce_rap_agency_####.txt`, `W5U3_DDLS_zce_rap_agency_####.txt`, `W5U4_CLAS_zcl_ce_rap_agency_####.txt`, `W5U5_CLAS_ZBP_I_RAP_TRAVEL_####.txt`(원격 검증), `W5U5_DDLS_ZC_RAP_Travel_####.txt`, `W5U6_SRVD_ZUI_RAP_TRAVEL_####.txt`(ES5 여행사 서비스, `cl_web_odata_client_factory`, custom entity, 값 도움말): https://github.com/SAP-samples/abap-platform-rap-opensap/tree/main/week5
- SAP-samples/abap-platform-rap630 — `README.md`(트라이얼에 RAP Generator 설치됨), `exercises/ex1/README.md`(릴리스된 BO `I_BankTP`에서 UI 서비스 생성, IAM 앱·비즈니스 카탈로그·역할로 권한 해결, EML `COMMIT ENTITIES RESPONSE OF`, `PRIVILEGED`, 잡에서 쓰는 사용자 권한): https://github.com/SAP-samples/abap-platform-rap630
- SAP-samples/abap-platform-bgpf-appl-log-events-side-effects — `README.md`, `src/zbgpfcl_calc_inventory_006.clas.abap`, `src/zbgpfr_inventorytp_006.bdef.asbdef`, `src/zbgpfbp_r_inventorytp_006.clas.locals_imp.abap`(액션 → `save_modified`에서 bgPF 등록, `if_bgmc_op_single`에서 EML, COMMIT 없음, 이벤트 기반 side effects, 가용 릴리스): https://github.com/SAP-samples/abap-platform-bgpf-appl-log-events-side-effects
- SAP-samples/abap-cheat-sheets — `22_Released_ABAP_Classes.md`(RAP, Transactional Consistency `cl_abap_tx`, Application Log `cl_bali_log`/`cl_bali_header_setter`/`cl_bali_free_text_setter`/`cl_bali_exception_setter`/`cl_bali_log_db`/`cl_bali_log_filter`/`xco_cp_bal`, Running Code in the Background `cl_bgmc_process_factory`/`if_bgmc_op_single`/`if_bgmc_op_single_tx_uncontr`, Calling Services `cl_web_http_client_manager`/`cl_http_destination_provider`, Application Jobs `if_apj_rt_run`/`cl_apj_dt_create_content`/`cl_apj_rt_api`), `08_EML_ABAP_for_RAP.md`(트랜잭션 단계별 허용 작업 표, RAP Additional and Unmanaged Save), `36_RAP_Behavior_Definition_Language.md`(필드 특성 조합 `mandatory : create, readonly : update`), `33_ABAP_Release_News.md`(`CL_ABAP_TX` 항목): https://github.com/SAP-samples/abap-cheat-sheets
- SAP-samples/abap-platform-refscen-flight (ABAP-platform-cloud 브랜치) — `src/reuse/supplement/#dmo#i_supplement.bdef.asbdef`(`field ( mandatory : create, readonly : update )` 실제 사용 예): https://github.com/SAP-samples/abap-platform-refscen-flight/tree/ABAP-platform-cloud
