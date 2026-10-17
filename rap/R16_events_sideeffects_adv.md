## 5. 고급·특수 기능 보충

### R-16. 비즈니스 이벤트·사이드 이펙트 고급: 자식 이벤트, 파생 이벤트, 이벤트 기반 사이드 이펙트, 전역 사이드 이펙트 [작성] ★★★
<!-- covers: RAP business event, event without parameter, event parameter, deep parameter, abstract BDEF with hierarchy, root abstract entity, composition in abstract entity, association to parent in abstract entity, with control, event on child entity, RAISE ENTITY EVENT child entity, TYPE TABLE FOR EVENT, %key, %param, derived event, managed event on parameter view entity, privileged payload read, event for side effects, event-driven side effect, event affects field, determine action executed on global, global side effects, $self affects, affects entity, affects permissions, permissions create _assoc, permissions field, affects messages, affects field *, source field group, executed on field group, determination ( always ), with additional save, with full data, save_modified, FOR EVENTS OF, cl_abap_behavior_event_handler, FOR ENTITY EVENT, one method for several events, cl_abap_tx=>save, CX_ABAP_BEHV_SAVE_FAILED, CX_RAP_EVENT_HDLR_ERROR_RETRY, delay_time, retry local events, CX_RAP_EVENT_HDLR_ERROR, EML in event handler, projection use side effects, projection use event for side effects, interface use event, interface use side effects, event binding, SAP Event Mesh, Enterprise Event Enablement -->
**목표**

1. 이벤트 세 종류(파라미터 없음, 평면 파라미터, `deep parameter`)를 정의하고, 자식 엔터티에도 이벤트를 정의해 `save_modified`에서 직접 발생시킬 수 있습니다.
2. `managed event … on … parameter …`로 **파생 이벤트**를 만들고, 구현 없이 프레임워크가 다른 payload로 함께 발생시키는 원리를 설명할 수 있습니다.
3. 로컬 이벤트 소비 클래스에서 EML로 BO를 다시 바꾸고(`cl_abap_tx=>save( )`), 잠금 때문에 실패하면 `CX_RAP_EVENT_HDLR_ERROR_RETRY`로 **자동 재시도**를 요청할 수 있습니다.
4. `event … for side effects`와 `event X affects …`로, 화면 밖(백그라운드)에서 바뀐 데이터를 열려 있는 Fiori 화면이 다시 읽게 만들 수 있습니다.
5. 사이드 이펙트의 트리거 다섯 가지(field, `$self`, action, determine action, event)와 대상 다섯 가지(field, permissions, `$self`, entity, messages), 필드 그룹, `executed on global`(전역 사이드 이펙트)을 모두 써 보고 Fiori에서 결과를 확인할 수 있습니다.
6. 프로젝션 BDEF의 `use side effects`/`use event`, 인터페이스 BDEF의 `use event`, 이벤트 바인딩과 SAP Event Mesh의 관계를 설명할 수 있습니다.

**전제**

- R-02(사이드 이펙트 기본: field → field, determine action + messages, action → permissions)와 R-04 8~9단계(Travel 이벤트 `travel_accepted`/`travel_rejected`, 로컬 이벤트 핸들러 기본형)를 끝냈다고 가정합니다. 이 문제는 그 **다음 단계 기능**만 다루므로, 기본 개념 설명은 짧게 하고 R-02/R-04를 가리킵니다.
- 기존 Travel BO를 건드리지 않도록 **전용 BO(지원 티켓)** 를 새로 만듭니다. 루트 `Ticket`(티켓) 아래에 자식 `Message`(티켓 대화 메시지)가 있습니다.
- 표준 데모 객체: `/DMO/I_Customer`(고객 뷰), `/DMO/I_Customer_StdVH`(고객 값 도움말). BTP 트라이얼에 기본 설치되어 있습니다.
- 사용하는 기능의 릴리스(치트시트 33 `ABAP_Release_News` 기준): 비즈니스 이벤트 7.89(2208), 사이드 이펙트 7.91(2302), 파생 이벤트·인터페이스 `use event` 7.93(2308), **자식 엔터티 이벤트 7.96(2405)**, **이벤트 기반 사이드 이펙트 9.14(2502)**, **로컬 이벤트 재시도 9.16(2508)**, **전역 사이드 이펙트 9.18(2602)**. BTP ABAP 환경(트라이얼 포함)은 항상 최신 릴리스를 쓰므로 모두 쓸 수 있어야 하지만, 실제 시스템에서 한 번도 실행해 보지 못했으므로 활성화 오류가 나면 각 단계의 "(실제 시스템에서 확인 필요)" 표시를 먼저 보세요.

**이 문제의 시나리오**

| 기능 | 티켓 BO에서의 쓰임 |
|---|---|
| 파라미터 없는 이벤트 `ticket_created` | 티켓이 처음 저장되면 발생. 로컬 소비자가 제목에 `URGENT`가 있으면 **자동 에스컬레이션** |
| 평면 파라미터 이벤트 `ticket_escalated` | 에스컬레이션 단계가 바뀌면 새 우선순위·단계·SLA 기한을 payload로 전달 |
| deep 파라미터 이벤트 `ticket_closed` | 티켓을 닫으면 헤더 + **메시지 목록(표)** 을 한 번에 전달 |
| 자식 엔터티 이벤트 `message_posted` | Message 엔터티에 정의. 고객/상담원 메시지가 저장될 때마다 발생 |
| 파생 이벤트 `ticket_created_contact` | `ticket_created`가 발생하면 프레임워크가 고객 이름·이메일을 담아 자동 발생 |
| 사이드 이펙트용 이벤트 `escalation_changed` | 백그라운드(이벤트 소비자)가 에스컬레이션하면 열려 있는 화면이 우선순위·SLA·메시지 표를 다시 읽음 |
| 전역 사이드 이펙트 `refreshSla` | 사용자가 전용 단축키를 누르면 SLA 신호등(남은 시간)을 다시 계산 |
| `$self affects` | 메시지가 생기거나 바뀌면 부모 티켓의 메시지 수·마지막 메시지 시각·상태를 다시 읽음 |
| `affects entity _Messages` | 닫기/다시 열기/에스컬레이션 액션이 시스템 메시지를 추가하면 메시지 표를 다시 읽음 |
| `affects permissions ( … )` | 닫은 뒤 버튼·편집 가능 여부·메시지 추가 버튼을 다시 읽음, 작성자 유형을 바꾸면 "내부 메모" 체크박스 편집 가능 여부를 다시 읽음 |
| 필드 그룹 + determine action | 우선순위·분류 둘 중 하나를 바꾸고 그룹 밖으로 나가면 SLA 기한 재계산 + 메시지 |

**만들 객체**

| 순서 | 객체 유형 | 이름 | 역할 |
|---|---|---|---|
| 1 | 데이터베이스 테이블 | `ZRAP_TKT_A_###` | 티켓 활성 데이터 |
| 2 | 데이터베이스 테이블 | `ZRAP_TMSG_A_###` | 메시지 활성 데이터 |
| 3 | 데이터베이스 테이블 | `ZRAP_TKT_D_###`, `ZRAP_TMSG_D_###` | draft 테이블 |
| 4 | 데이터베이스 테이블 | `ZRAP_TKTEVL_###` | 이벤트 수신 로그 |
| 5 | 메시지 클래스 / 예외 클래스 | `ZRAP_TKT_MSG_###` / `ZCM_RAP_TKT_###` | 이 BO 전용 메시지 |
| 6 | CDS 뷰 엔터티 | `ZRAP_R_TICKET_###`, `ZRAP_R_TKTMSG_###` | BO 기본 뷰(루트·자식) |
| 7 | CDS 추상 엔터티 | `ZRAP_A_TKT_ESC_###`, `ZRAP_A_TMSG_EVT_###` | 평면 이벤트 파라미터(루트·자식) |
| 8 | CDS 추상 엔터티 + 추상 BDEF | `ZRAP_D_TKT_CLOSED_###`, `ZRAP_D_TKT_CLMSG_###` | deep 이벤트 파라미터(계층) |
| 9 | CDS 뷰 엔터티 | `ZRAP_P_TKT_CONTACT_###` | 파생 이벤트 payload |
| 10 | 행동 정의 / 행동 풀 | `ZRAP_R_TICKET_###` / `ZBP_RAP_R_TICKET_###` | 이벤트·사이드 이펙트·행동 전체 |
| 11 | CDS 프로젝션·MDE·BDEF | `ZRAP_C_TICKET_###`, `ZRAP_C_TKTMSG_###` | UI 소비 계층 (`use side effects`, `use event`) |
| 12 | CDS 프로젝션·BDEF | `ZRAP_I_TICKET_###`, `ZRAP_I_TKTMSG_###` | 인터페이스 계층 (`use event`) |
| 13 | 서비스 정의 / 바인딩 | `ZRAP_UI_TICKET_###` / `ZRAP_UI_TICKET_O4_###` | Fiori Preview |
| 14 | ABAP 클래스 | `ZCL_RAP_TKT_EVT_###` | 로컬 이벤트 소비(이벤트 핸들러 클래스) |
| 15 | ABAP 클래스(예외) | `ZCX_RAP_TKT_RETRY_###` | 재시도 요청 예외 |
| 16 | ABAP 클래스(콘솔) | `ZCL_RAP_TKT_TEST_###` | EML로 이벤트 발생·로그 확인 |
| 17 | 이벤트 바인딩(개념) | `ZRAP_EVB_TKT_CLOSED_###` | 원격 소비용 매핑 |

> 진행 방법: 1~4단계에서 데이터 모델과 파라미터 엔터티를 만들고, 5단계에서 BDEF를 한 번에 씁니다. BDEF를 저장하면 구현이 없다는 경고가 나오므로 **Ctrl+1 → Add missing method(s)** 로 핸들러 뼈대를 만든 뒤 6~7단계 정답과 비교하세요. 8단계에서 서비스를 열면 9~11단계에서 이벤트와 사이드 이펙트를 화면으로 확인합니다.

#### 1단계. 테이블 다섯 개 만들기: 티켓, 메시지, draft, 이벤트 로그

요구사항

1. 티켓 활성 테이블 `ZRAP_TKT_A_###`를 아래 필드 표대로 만드세요. 키는 UUID(`numbering : managed`)입니다.

| 필드 | 키 | 데이터 엘리먼트(또는 내장 타입) | 타입 | 길이 | 소수 | 설명 |
|---|---|---|---|---|---|---|
| client | ✓ | abap.clnt | CLNT | 3 | 0 | 클라이언트 |
| ticket_uuid | ✓ | sysuuid_x16 | RAW | 16 | 0 | 티켓 키(프레임워크가 채움) |
| ticket_no |  | abap.numc(10) | NUMC | 10 | 0 | 사람이 읽는 티켓 번호(저장 때 결정) |
| title |  | abap.char(80) | CHAR | 80 | 0 | 제목 |
| customer_id |  | /dmo/customer_id | NUMC | 6 | 0 | 고객 |
| category |  | abap.char(2) | CHAR | 2 | 0 | 분류: HW 하드웨어, SW 소프트웨어, AC 계정 |
| priority |  | abap.char(1) | CHAR | 1 | 0 | 우선순위: L, M, H, U(긴급) |
| status |  | abap.char(1) | CHAR | 1 | 0 | 상태: N 신규, P 처리 중, W 고객 답변 대기, C 닫힘 |
| escalation_level |  | abap.int1 | INT1 | 3 | 0 | 에스컬레이션 단계(0~3) |
| opened_at |  | abap.utclong | UTCL | – | – | 접수 시각(SLA 기준) |
| sla_due_at |  | abap.utclong | UTCL | – | – | SLA 기한 |
| sla_status |  | abap.char(1) | CHAR | 1 | 0 | SLA 신호등: G, Y, R |
| sla_criticality |  | abap.int1 | INT1 | 3 | 0 | 신호등 색(3 초록, 2 노랑, 1 빨강, 0 없음) |
| message_count |  | abap.int4 | INT4 | 10 | 0 | 메시지 수 |
| last_message_at |  | abap.utclong | UTCL | – | – | 마지막 메시지 시각 |
| created_by |  | abp_creation_user | CHAR | 12 | 0 | 생성자 |
| created_at |  | abp_creation_tstmpl | DEC | 21 | 7 | 생성 시각 |
| local_last_changed_by |  | abp_locinst_lastchange_user | CHAR | 12 | 0 | 마지막 변경자 |
| local_last_changed_at |  | abp_locinst_lastchange_tstmpl | DEC | 21 | 7 | 인스턴스 ETag |
| last_changed_at |  | abp_lastchange_tstmpl | DEC | 21 | 7 | total ETag |

2. 메시지 활성 테이블 `ZRAP_TMSG_A_###`를 만드세요.

| 필드 | 키 | 데이터 엘리먼트(또는 내장 타입) | 타입 | 길이 | 소수 | 설명 |
|---|---|---|---|---|---|---|
| client | ✓ | abap.clnt | CLNT | 3 | 0 | 클라이언트 |
| message_uuid | ✓ | sysuuid_x16 | RAW | 16 | 0 | 메시지 키(프레임워크가 채움) |
| ticket_uuid |  | sysuuid_x16 | RAW | 16 | 0 | 부모 티켓 키 |
| message_text |  | abap.char(255) | CHAR | 255 | 0 | 본문 |
| author_type |  | abap.char(1) | CHAR | 1 | 0 | 작성자 유형: C 고객, A 상담원, S 시스템 |
| is_internal |  | abap_boolean | CHAR | 1 | 0 | 내부 메모 여부(상담원만) |
| posted_by |  | abp_creation_user | CHAR | 12 | 0 | 작성자 |
| posted_at |  | abp_creation_tstmpl | DEC | 21 | 7 | 작성 시각 |
| local_last_changed_at |  | abp_locinst_lastchange_tstmpl | DEC | 21 | 7 | 인스턴스 ETag |

3. draft 테이블 두 개(`ZRAP_TKT_D_###`, `ZRAP_TMSG_D_###`)를 만드세요. UUID 키이므로 late numbering용 `DRAFTUUID`는 필요 없습니다. 필드 이름은 5단계 CDS 별칭을 소문자로 쓴 이름(밑줄 없음)이고, 마지막에 `"%admin"` include를 넣습니다. BDEF를 먼저 쓰고 `draft table` 이름에서 Ctrl+1로 만들어도 됩니다.
4. 이벤트 수신 로그 테이블 `ZRAP_TKTEVL_###`를 만드세요.

| 필드 | 키 | 데이터 엘리먼트(또는 내장 타입) | 타입 | 길이 | 소수 | 설명 |
|---|---|---|---|---|---|---|
| client | ✓ | abap.clnt | CLNT | 3 | 0 | 클라이언트 |
| log_uuid | ✓ | sysuuid_x16 | RAW | 16 | 0 | 로그 줄 키 |
| event_name |  | abap.char(30) | CHAR | 30 | 0 | 받은 이벤트 이름 |
| ticket_uuid |  | sysuuid_x16 | RAW | 16 | 0 | 티켓 키 |
| message_uuid |  | sysuuid_x16 | RAW | 16 | 0 | 메시지 키(자식 이벤트만) |
| info |  | abap.char(255) | CHAR | 255 | 0 | payload 요약 |
| received_at |  | abap.utclong | UTCL | – | – | 수신 시각 |

**확인**

- 다섯 테이블이 활성화됩니다. `ZRAP_TKT_D_###`를 열어 `"%admin"` 아래 draft 관리 필드(`draftentitycreationdatetime` 등)가 포함되었는지 Element Info(F2)로 봅니다.

<details><summary>정답·해설</summary>

```abap
@EndUserText.label : 'Support ticket (active)'
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table zrap_tkt_a_### {
  key client            : abap.clnt not null;
  key ticket_uuid       : sysuuid_x16 not null;
  ticket_no             : abap.numc(10);
  title                 : abap.char(80);
  customer_id           : /dmo/customer_id;
  category              : abap.char(2);
  priority              : abap.char(1);
  status                : abap.char(1);
  escalation_level      : abap.int1;
  opened_at             : abap.utclong;
  sla_due_at            : abap.utclong;
  sla_status            : abap.char(1);
  sla_criticality       : abap.int1;
  message_count         : abap.int4;
  last_message_at       : abap.utclong;
  created_by            : abp_creation_user;
  created_at            : abp_creation_tstmpl;
  local_last_changed_by : abp_locinst_lastchange_user;
  local_last_changed_at : abp_locinst_lastchange_tstmpl;
  last_changed_at       : abp_lastchange_tstmpl;
}
```

```abap
@EndUserText.label : 'Support ticket message (active)'
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table zrap_tmsg_a_### {
  key client            : abap.clnt not null;
  key message_uuid      : sysuuid_x16 not null;
  ticket_uuid           : sysuuid_x16;
  message_text          : abap.char(255);
  author_type           : abap.char(1);
  is_internal           : abap_boolean;
  posted_by             : abp_creation_user;
  posted_at             : abp_creation_tstmpl;
  local_last_changed_at : abp_locinst_lastchange_tstmpl;
}
```

```abap
@EndUserText.label : 'Draft table for entity ZRAP_R_TICKET_###'
@AbapCatalog.enhancement.category : #EXTENSIBLE_ANY
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table zrap_tkt_d_### {
  key mandt          : mandt not null;
  key ticketuuid     : sysuuid_x16 not null;
  ticketno           : abap.numc(10);
  title              : abap.char(80);
  customerid         : /dmo/customer_id;
  category           : abap.char(2);
  priority           : abap.char(1);
  status             : abap.char(1);
  escalationlevel    : abap.int1;
  openedat           : abap.utclong;
  sladueat           : abap.utclong;
  slastatus          : abap.char(1);
  slacriticality     : abap.int1;
  messagecount       : abap.int4;
  lastmessageat      : abap.utclong;
  createdby          : abp_creation_user;
  createdat          : abp_creation_tstmpl;
  locallastchangedby : abp_locinst_lastchange_user;
  locallastchangedat : abp_locinst_lastchange_tstmpl;
  lastchangedat      : abp_lastchange_tstmpl;
  "%admin"           : include sych_bdl_draft_admin_inc;   // draft 관리 정보
}
```

```abap
@EndUserText.label : 'Draft table for entity ZRAP_R_TKTMSG_###'
@AbapCatalog.enhancement.category : #EXTENSIBLE_ANY
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table zrap_tmsg_d_### {
  key mandt          : mandt not null;
  key messageuuid    : sysuuid_x16 not null;
  ticketuuid         : sysuuid_x16;
  messagetext        : abap.char(255);
  authortype         : abap.char(1);
  isinternal         : abap_boolean;
  postedby           : abp_creation_user;
  postedat           : abp_creation_tstmpl;
  locallastchangedat : abp_locinst_lastchange_tstmpl;
  "%admin"           : include sych_bdl_draft_admin_inc;
}
```

```abap
@EndUserText.label : 'Ticket event log'
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table zrap_tktevl_### {
  key client   : abap.clnt not null;
  key log_uuid : sysuuid_x16 not null;
  event_name   : abap.char(30);
  ticket_uuid  : sysuuid_x16;
  message_uuid : sysuuid_x16;
  info         : abap.char(255);
  received_at  : abap.utclong;
}
```

draft 테이블 필드 표 (`ZRAP_TKT_D_###`; `ZRAP_TMSG_D_###`도 같은 규칙)

| 필드 | 키 | 데이터 엘리먼트 | 타입 | 길이 | 소수 | 설명 |
|---|---|---|---|---|---|---|
| mandt | ✓ | mandt | CLNT | 3 | 0 | 클라이언트 |
| ticketuuid | ✓ | sysuuid_x16 | RAW | 16 | 0 | draft도 같은 UUID 키를 씀 |
| ticketno ~ lastchangedat |  | (활성 테이블과 같은 타입) |  |  |  | CDS 별칭과 같은 이름(밑줄 없음) |
| "%admin" |  | include sych_bdl_draft_admin_inc |  |  |  | draft 관리 정보 |

해설

- **왜 UUID 키인가**: R-01~R-04의 Travel은 late numbering이어서 draft 테이블에 `DRAFTUUID`가 따로 필요했습니다. 이 문제는 이벤트와 사이드 이펙트에 집중하려고 `numbering : managed`(UUID)를 씁니다. draft와 활성 인스턴스가 같은 키를 가지므로 draft 테이블 키도 그대로입니다.
- **utclong**: SLA 계산에 `utclong_add( )`, `utclong_diff( )` 내장 함수를 쓰기 위해 `abap.utclong`을 골랐습니다. Fiori에서는 날짜·시각(DateTimeOffset)으로 보입니다.
- **sla_criticality를 저장하는 이유**: 신호등 색을 계산 필드로 만들면 draft 테이블에도 같은 필드가 필요하고 매핑이 복잡해집니다. 결정(determination)이 상태와 색을 함께 저장하게 해서 단순하게 했습니다.
- **로그 테이블**: 이벤트 소비자는 별도 트랜잭션에서 비동기로 돌기 때문에 디버거로 보기 어렵습니다. 받은 이벤트를 테이블에 남겨 Data Preview(F8)로 확인합니다(R-04 9단계와 같은 방법).

</details>

#### 2단계. 전용 메시지 클래스와 예외 클래스

요구사항

1. 메시지 클래스 `ZRAP_TKT_MSG_###`에 아래 메시지를 등록하세요.

| 번호 | 텍스트 | 쓰는 곳 | severity |
|---|---|---|---|
| 001 | Enter a customer. | validateCustomer | 오류 |
| 002 | Customer &1 does not exist. | validateCustomer | 오류 |
| 003 | Category &1 is not valid. Use HW, SW or AC. | validateCategory | 오류 |
| 004 | Ticket &1 escalated to level &2. | escalate | 성공 |
| 005 | Ticket &1 has been closed. | closeTicket | 성공 |
| 006 | Ticket &1 has been reopened. | reopenTicket | 성공 |

2. 예외 클래스 `ZCM_RAP_TKT_###`를 R-02의 `ZCM_RAP_###`와 같은 구조로 만드세요(`CX_STATIC_CHECK` 상속, `IF_T100_MESSAGE`, `IF_T100_DYN_MSG`, `IF_ABAP_BEHV_MESSAGE`). 자리표시자 속성은 `mv_customer_id`, `mv_category`, `mv_ticket_no`, `mv_level`입니다.

**확인**

- 메시지 6개가 저장되고 예외 클래스가 활성화됩니다.

<details><summary>정답·해설</summary>

```abap
CLASS zcm_rap_tkt_### DEFINITION
  PUBLIC
  INHERITING FROM cx_static_check
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_t100_message.
    INTERFACES if_t100_dyn_msg.
    INTERFACES if_abap_behv_message.

    CONSTANTS:
      BEGIN OF enter_customer,
        msgid TYPE symsgid VALUE 'ZRAP_TKT_MSG_###',
        msgno TYPE symsgno VALUE '001',
        attr1 TYPE scx_attrname VALUE '',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF enter_customer,

      BEGIN OF customer_unknown,
        msgid TYPE symsgid VALUE 'ZRAP_TKT_MSG_###',
        msgno TYPE symsgno VALUE '002',
        attr1 TYPE scx_attrname VALUE 'MV_CUSTOMER_ID',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF customer_unknown,

      BEGIN OF category_invalid,
        msgid TYPE symsgid VALUE 'ZRAP_TKT_MSG_###',
        msgno TYPE symsgno VALUE '003',
        attr1 TYPE scx_attrname VALUE 'MV_CATEGORY',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF category_invalid,

      BEGIN OF ticket_escalated,
        msgid TYPE symsgid VALUE 'ZRAP_TKT_MSG_###',
        msgno TYPE symsgno VALUE '004',
        attr1 TYPE scx_attrname VALUE 'MV_TICKET_NO',
        attr2 TYPE scx_attrname VALUE 'MV_LEVEL',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF ticket_escalated,

      BEGIN OF ticket_closed,
        msgid TYPE symsgid VALUE 'ZRAP_TKT_MSG_###',
        msgno TYPE symsgno VALUE '005',
        attr1 TYPE scx_attrname VALUE 'MV_TICKET_NO',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF ticket_closed,

      BEGIN OF ticket_reopened,
        msgid TYPE symsgid VALUE 'ZRAP_TKT_MSG_###',
        msgno TYPE symsgno VALUE '006',
        attr1 TYPE scx_attrname VALUE 'MV_TICKET_NO',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF ticket_reopened.

    METHODS constructor
      IMPORTING
        textid      LIKE if_t100_message=>t100key OPTIONAL
        severity    TYPE if_abap_behv_message=>t_severity OPTIONAL
        previous    LIKE previous OPTIONAL
        customer_id TYPE /dmo/customer_id OPTIONAL
        category    TYPE c LENGTH 2 OPTIONAL
        ticket_no   TYPE n LENGTH 10 OPTIONAL
        level       TYPE i OPTIONAL.

    DATA mv_customer_id TYPE /dmo/customer_id READ-ONLY.
    DATA mv_category    TYPE c LENGTH 2 READ-ONLY.
    DATA mv_ticket_no   TYPE n LENGTH 10 READ-ONLY.
    DATA mv_level       TYPE i READ-ONLY.

  PROTECTED SECTION.
  PRIVATE SECTION.
ENDCLASS.


CLASS zcm_rap_tkt_### IMPLEMENTATION.

  METHOD constructor ##ADT_SUPPRESS_GENERATION.
    super->constructor( previous = previous ).

    mv_customer_id = customer_id.
    mv_category    = category.
    mv_ticket_no   = ticket_no.
    mv_level       = level.

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

해설

- 구조와 이유는 R-02 1단계와 같습니다. 이 문제만의 메시지를 R-02의 `ZRAP_MSG_###`에 섞으면 다른 보충 문제와 번호가 겹칠 수 있어 전용 클래스를 만들었습니다.
- 속성 타입은 테이블 필드와 같은 내장 타입(`c LENGTH 2`, `n LENGTH 10`)과 `i`로 적었습니다. 릴리스 여부를 따로 확인할 필요가 없도록 데이터 엘리먼트 대신 내장 타입을 썼습니다. 참조 전달 파라미터는 타입이 맞아야 하므로, INT1 필드(EscalationLevel)를 넘길 때는 `CONV #( … )`로 바꿔 넘깁니다(6단계 escalate).

</details>

#### 3단계. CDS 데이터 모델: 기본 뷰, 프로젝션, 인터페이스, MDE

요구사항

1. 루트 뷰 `ZRAP_R_TICKET_###`(`define root view entity`): 1단계 테이블의 모든 필드에 CamelCase 별칭(`TicketUUID`, `TicketNo`, `Title`, `CustomerID`, `Category`, `Priority`, `Status`, `EscalationLevel`, `OpenedAt`, `SlaDueAt`, `SlaStatus`, `SlaCriticality`, `MessageCount`, `LastMessageAt`, `CreatedBy`, `CreatedAt`, `LocalLastChangedBy`, `LocalLastChangedAt`, `LastChangedAt`), 자식 `_Messages` 컴포지션, 고객 연관 `_Customer`(`/DMO/I_Customer`).
2. 자식 뷰 `ZRAP_R_TKTMSG_###`: `MessageUUID`, `TicketUUID`, `MessageText`, `AuthorType`, `IsInternal`, `PostedBy`, `PostedAt`, `LocalLastChangedAt`, 부모 연관 `_Ticket`.
3. 프로젝션 `ZRAP_C_TICKET_###`/`ZRAP_C_TKTMSG_###`(`provider contract transactional_query`): 고객 이름 `CustomerName` 추가, 컴포지션·부모 연관 redirect.
4. 인터페이스 `ZRAP_I_TICKET_###`/`ZRAP_I_TKTMSG_###`(`provider contract transactional_interface`): 필드 그대로 노출.
5. 메타데이터 확장(MDE) `ZRAP_C_TICKET_###`, `ZRAP_C_TKTMSG_###`: 목록 열, 헤더, 일반 정보 묶음, 메시지 표, 액션 버튼 세 개(`escalate`, `closeTicket`, `reopenTicket`), SLA 신호등 색.

**직접 추가할 어노테이션**

- `@AccessControl.authorizationCheck` — 이 실습에서는 DCL 없이 쓰겠다는 표시
- `@EndUserText.label` — 뷰 설명
- `@Metadata.ignorePropagatedAnnotations` — R 뷰가 테이블/하위 뷰 어노테이션을 물려받지 않게
- `@Semantics.user.createdBy`, `@Semantics.systemDateTime.createdAt`, `@Semantics.user.localInstanceLastChangedBy`, `@Semantics.systemDateTime.localInstanceLastChangedAt`, `@Semantics.systemDateTime.lastChangedAt` — 관리형 프레임워크가 관리 필드를 자동으로 채우게
- `@Metadata.allowExtensions` — 프로젝션 뷰에 MDE를 허용
- `@ObjectModel.text.element` — 고객 번호 옆에 이름을 보여 줌
- `@Consumption.valueHelpDefinition` — 고객 번호 입력 도움말
- `@UI.headerInfo` — 객체 페이지 제목/목록 제목
- `@UI.facet` — 객체 페이지 섹션 구성(필드 그룹, 메시지 표)
- `@UI.lineItem`, `@UI.identification`, `@UI.fieldGroup` — 목록 열, 객체 페이지 필드, 액션 버튼(`type: #FOR_ACTION`)
- `@UI.selectionField` — 목록 필터
- `@UI.hidden` — UUID 숨기기
- (lineItem/identification의) `criticality` — SLA 상태를 신호등 색으로

**확인**

- 여섯 개 뷰와 MDE 두 개가 활성화됩니다(R 뷰는 5단계 BDEF 전이라도 활성화됩니다).
- `ZRAP_R_TICKET_###`에서 F8(Data Preview)을 열면 빈 결과가 나옵니다.

<details><summary>정답·해설</summary>

```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED           // DCL 없이 사용 (→ 어노테이션 탭: @AccessControl.authorizationCheck)
@EndUserText.label: 'Support ticket'                         // (→ 어노테이션 탭: @EndUserText.label)
@Metadata.ignorePropagatedAnnotations: true                  // (→ 어노테이션 탭: @Metadata.ignorePropagatedAnnotations)
define root view entity ZRAP_R_TICKET_###
  as select from zrap_tkt_a_###
  composition [0..*] of ZRAP_R_TKTMSG_### as _Messages     // 자식: 티켓 메시지
  association [0..1] to /DMO/I_Customer   as _Customer
    on $projection.CustomerID = _Customer.CustomerID
{
  key ticket_uuid           as TicketUUID,
      ticket_no             as TicketNo,
      title                 as Title,
      customer_id           as CustomerID,
      category              as Category,
      priority              as Priority,
      status                as Status,
      escalation_level      as EscalationLevel,
      opened_at             as OpenedAt,
      sla_due_at            as SlaDueAt,
      sla_status            as SlaStatus,
      sla_criticality       as SlaCriticality,
      message_count         as MessageCount,
      last_message_at       as LastMessageAt,
      @Semantics.user.createdBy: true                           // 생성자 자동 (→ 어노테이션 탭: @Semantics.user.createdBy)
      created_by            as CreatedBy,
      @Semantics.systemDateTime.createdAt: true                 // 생성 시각 자동
      created_at            as CreatedAt,
      @Semantics.user.localInstanceLastChangedBy: true          // 마지막 변경자 자동
      local_last_changed_by as LocalLastChangedBy,
      @Semantics.systemDateTime.localInstanceLastChangedAt: true // 인스턴스 ETag
      local_last_changed_at as LocalLastChangedAt,
      @Semantics.systemDateTime.lastChangedAt: true             // total ETag
      last_changed_at       as LastChangedAt,

      _Messages,
      _Customer
}
```

```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Support ticket message'
@Metadata.ignorePropagatedAnnotations: true
define view entity ZRAP_R_TKTMSG_###
  as select from zrap_tmsg_a_###
  association to parent ZRAP_R_TICKET_### as _Ticket
    on $projection.TicketUUID = _Ticket.TicketUUID
{
  key message_uuid          as MessageUUID,
      ticket_uuid           as TicketUUID,
      message_text          as MessageText,
      author_type           as AuthorType,
      is_internal           as IsInternal,
      @Semantics.user.createdBy: true                            // 작성자 자동
      posted_by             as PostedBy,
      @Semantics.systemDateTime.createdAt: true                  // 작성 시각 자동
      posted_at             as PostedAt,
      @Semantics.systemDateTime.localInstanceLastChangedAt: true
      local_last_changed_at as LocalLastChangedAt,

      _Ticket
}
```

```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Support ticket (projection)'
@Metadata.allowExtensions: true                              // MDE 허용 (→ 어노테이션 탭: @Metadata.allowExtensions)
define root view entity ZRAP_C_TICKET_###
  provider contract transactional_query
  as projection on ZRAP_R_TICKET_###
{
  key TicketUUID,
      TicketNo,
      Title,
      @ObjectModel.text.element: ['CustomerName']            // 번호 옆에 이름 (→ 어노테이션 탭: @ObjectModel.text.element)
      @Consumption.valueHelpDefinition: [{ entity: { name: '/DMO/I_Customer_StdVH', element: 'CustomerID' } }] // (→ 어노테이션 탭: @Consumption.valueHelpDefinition)
      CustomerID,
      _Customer.LastName as CustomerName,
      Category,
      Priority,
      Status,
      EscalationLevel,
      OpenedAt,
      SlaDueAt,
      SlaStatus,
      SlaCriticality,
      MessageCount,
      LastMessageAt,
      CreatedBy,
      CreatedAt,
      LocalLastChangedBy,
      LocalLastChangedAt,
      LastChangedAt,

      _Messages : redirected to composition child ZRAP_C_TKTMSG_###,
      _Customer
}
```

```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Support ticket message (projection)'
@Metadata.allowExtensions: true
define view entity ZRAP_C_TKTMSG_###
  as projection on ZRAP_R_TKTMSG_###
{
  key MessageUUID,
      TicketUUID,
      MessageText,
      AuthorType,
      IsInternal,
      PostedBy,
      PostedAt,
      LocalLastChangedAt,

      _Ticket : redirected to parent ZRAP_C_TICKET_###
}
```

```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Support ticket (interface)'
define root view entity ZRAP_I_TICKET_###
  provider contract transactional_interface
  as projection on ZRAP_R_TICKET_###
{
  key TicketUUID,
      TicketNo,
      Title,
      CustomerID,
      Category,
      Priority,
      Status,
      EscalationLevel,
      OpenedAt,
      SlaDueAt,
      SlaStatus,
      SlaCriticality,
      MessageCount,
      LastMessageAt,
      CreatedBy,
      CreatedAt,
      LocalLastChangedBy,
      LocalLastChangedAt,
      LastChangedAt,

      _Messages : redirected to composition child ZRAP_I_TKTMSG_###
}
```

```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Support ticket message (interface)'
define view entity ZRAP_I_TKTMSG_###
  as projection on ZRAP_R_TKTMSG_###
{
  key MessageUUID,
      TicketUUID,
      MessageText,
      AuthorType,
      IsInternal,
      PostedBy,
      PostedAt,
      LocalLastChangedAt,

      _Ticket : redirected to parent ZRAP_I_TICKET_###
}
```

MDE `ZRAP_C_TICKET_###`:

```cds
@Metadata.layer: #CUSTOMER
@UI.headerInfo: { typeName: 'Ticket', typeNamePlural: 'Tickets',            // (→ 어노테이션 탭: @UI.headerInfo)
                  title: { type: #STANDARD, value: 'Title' },
                  description: { type: #STANDARD, value: 'TicketNo' } }
annotate entity ZRAP_C_TICKET_### with
{
  @UI.facet: [                                                              // (→ 어노테이션 탭: @UI.facet)
    { id: 'Ticket',   purpose: #STANDARD, type: #IDENTIFICATION_REFERENCE, label: 'Ticket',   position: 10 },
    { id: 'Sla',      purpose: #STANDARD, type: #FIELDGROUP_REFERENCE,     label: 'SLA',      position: 20, targetQualifier: 'Sla' },
    { id: 'Messages', purpose: #STANDARD, type: #LINEITEM_REFERENCE,       label: 'Messages', position: 30, targetElement: '_Messages' } ]

  @UI.hidden: true                                                          // (→ 어노테이션 탭: @UI.hidden)
  TicketUUID;

  @UI.lineItem:       [ { position: 10, importance: #HIGH },                // (→ 어노테이션 탭: @UI.lineItem)
                        { type: #FOR_ACTION, dataAction: 'escalate',     label: 'Escalate' },
                        { type: #FOR_ACTION, dataAction: 'closeTicket',  label: 'Close' },
                        { type: #FOR_ACTION, dataAction: 'reopenTicket', label: 'Reopen' } ]
  @UI.identification: [ { position: 10 },                                   // (→ 어노테이션 탭: @UI.identification)
                        { type: #FOR_ACTION, dataAction: 'escalate',     label: 'Escalate' },
                        { type: #FOR_ACTION, dataAction: 'closeTicket',  label: 'Close' },
                        { type: #FOR_ACTION, dataAction: 'reopenTicket', label: 'Reopen' } ]
  @UI.selectionField: [ { position: 10 } ]                                  // (→ 어노테이션 탭: @UI.selectionField)
  TicketNo;

  @UI.lineItem:       [ { position: 20, importance: #HIGH } ]
  @UI.identification: [ { position: 20 } ]
  Title;

  @UI.lineItem:       [ { position: 30 } ]
  @UI.identification: [ { position: 30 } ]
  @UI.selectionField: [ { position: 20 } ]
  CustomerID;

  @UI.lineItem:       [ { position: 40 } ]
  @UI.identification: [ { position: 40, label: 'Category (HW/SW/AC)' } ]
  Category;

  @UI.lineItem:       [ { position: 50 } ]
  @UI.identification: [ { position: 50, label: 'Priority (L/M/H/U)' } ]
  @UI.selectionField: [ { position: 30 } ]
  Priority;

  @UI.lineItem:       [ { position: 60 } ]
  @UI.identification: [ { position: 60, label: 'Status (N/P/W/C)' } ]
  @UI.selectionField: [ { position: 40 } ]
  Status;

  @UI.lineItem:       [ { position: 70, label: 'Esc. Level' } ]
  @UI.identification: [ { position: 70, label: 'Escalation Level' } ]
  EscalationLevel;

  @UI.fieldGroup:     [ { qualifier: 'Sla', position: 10 } ]                 // (→ 어노테이션 탭: @UI.fieldGroup)
  OpenedAt;

  @UI.fieldGroup:     [ { qualifier: 'Sla', position: 20 } ]
  SlaDueAt;

  @UI.lineItem:       [ { position: 80, label: 'SLA', criticality: 'SlaCriticality' } ]   // 신호등 색
  @UI.fieldGroup:     [ { qualifier: 'Sla', position: 30, label: 'SLA', criticality: 'SlaCriticality' } ]
  SlaStatus;

  @UI.hidden: true
  SlaCriticality;

  @UI.lineItem:       [ { position: 90, label: 'Messages' } ]
  @UI.fieldGroup:     [ { qualifier: 'Sla', position: 40, label: 'Messages' } ]
  MessageCount;

  @UI.fieldGroup:     [ { qualifier: 'Sla', position: 50, label: 'Last Message' } ]
  LastMessageAt;

  @UI.hidden: true
  LocalLastChangedAt;
}
```

MDE `ZRAP_C_TKTMSG_###`:

```cds
@Metadata.layer: #CUSTOMER
@UI.headerInfo: { typeName: 'Message', typeNamePlural: 'Messages',
                  title: { type: #STANDARD, value: 'MessageText' } }
annotate entity ZRAP_C_TKTMSG_### with
{
  @UI.facet: [ { id: 'Message', purpose: #STANDARD, type: #IDENTIFICATION_REFERENCE, label: 'Message', position: 10 } ]

  @UI.hidden: true
  MessageUUID;

  @UI.hidden: true
  TicketUUID;

  @UI.lineItem:       [ { position: 10, importance: #HIGH } ]
  @UI.identification: [ { position: 10 } ]
  MessageText;

  @UI.lineItem:       [ { position: 20, label: 'Author (C/A/S)' } ]
  @UI.identification: [ { position: 20, label: 'Author (C/A/S)' } ]
  AuthorType;

  @UI.lineItem:       [ { position: 30, label: 'Internal' } ]
  @UI.identification: [ { position: 30, label: 'Internal Note' } ]
  IsInternal;

  @UI.lineItem:       [ { position: 40 } ]
  PostedBy;

  @UI.lineItem:       [ { position: 50 } ]
  PostedAt;

  @UI.hidden: true
  LocalLastChangedAt;
}
```

해설

- 기본 구조(R/C/I 3계층, redirect, MDE)는 R-01·R-03과 같습니다. 이 단계의 목적은 9~11단계에서 **사이드 이펙트 결과가 눈에 보이도록** 화면을 준비하는 것입니다. 메시지 수, 마지막 메시지 시각, SLA 신호등은 모두 사용자가 직접 입력하지 않고 서버가 바꾸는 필드라, 사이드 이펙트가 없으면 화면이 옛 값을 계속 보여 줍니다.
- 상태·우선순위·분류는 실습을 짧게 하려고 코드 값(`N`, `U`, `HW`)을 그대로 보입니다. 실무라면 CDS 열거형이나 텍스트 연관을 붙입니다(R-01 참고).
- 인터페이스 뷰에는 UI 어노테이션을 붙이지 않습니다. 다른 BO나 이벤트 소비자가 쓰는 안정된 API 계층이기 때문입니다(R-03 9단계).

</details>

#### 4단계. 이벤트 payload 만들기: 평면 추상 엔터티, 계층 추상 엔터티 + 추상 BDEF, 파생 이벤트용 뷰 엔터티

요구사항

1. 평면 파라미터 `ZRAP_A_TKT_ESC_###`(`ticket_escalated`용, 추상 엔터티): `ticket_no`(numc 10), `customer_id`(/dmo/customer_id), `priority`(char 1), `escalation_level`(int1), `sla_due_at`(utclong).
2. 자식 이벤트 파라미터 `ZRAP_A_TMSG_EVT_###`(`message_posted`용, 추상 엔터티): `ticket_uuid`(sysuuid_x16), `author_type`(char 1), `is_internal`(abap_boolean), `message_text`(char 255).
3. deep 파라미터(`ticket_closed`용) — **계층 구조**:
   - 루트 추상 엔터티 `ZRAP_D_TKT_CLOSED_###`(`define root abstract entity`): 키 `ticket_uuid`, `ticket_no`, `title`, `customer_id`, `escalation_level`, `message_count`, `closed_at`(utclong), 그리고 자식으로 가는 컴포지션 `_Messages`(0..*).
   - 자식 추상 엔터티 `ZRAP_D_TKT_CLMSG_###`: 키 `message_uuid`, `ticket_uuid`, `author_type`, `message_text`, 부모로 가는 연관 `_Closed`.
   - 같은 이름의 **추상 BDEF** `ZRAP_D_TKT_CLOSED_###`: 구현 유형 `abstract`, strict 모드 2, `with hierarchy`, 루트에서 `_Messages`를 계층에 포함.
4. 파생 이벤트 payload `ZRAP_P_TKT_CONTACT_###`(**뷰 엔터티**, 추상 엔터티가 아님): 티켓 활성 테이블과 `/DMO/I_Customer`를 조인해 `TicketUUID`(키), `TicketNo`, `FirstName`, `LastName`, `EMailAddress`를 내보냅니다. **연관을 두지 마세요.**

**직접 추가할 어노테이션**

- `@EndUserText.label` — 추상 엔터티·뷰 설명
- `@AccessControl.authorizationCheck` — 파생 이벤트 payload 뷰의 접근 제어 여부

**확인**

- 추상 엔터티 네 개, 추상 BDEF 하나, 뷰 엔터티 하나가 활성화됩니다. 순서: 자식 추상 엔터티와 루트 추상 엔터티는 서로를 가리키므로 **두 개를 함께 선택해 한 번에 활성화**(Ctrl+Shift+F3)하세요. 그다음 추상 BDEF를 활성화합니다.
- 추상 BDEF에서 `ZRAP_D_TKT_CLOSED_###`에 커서를 두고 F2를 누르면 파생 타입 구조를 볼 수 있습니다(ADT 버전에 따라 다름).

<details><summary>정답·해설</summary>

```cds
@EndUserText.label: 'Ticket escalated (event payload)'       // (→ 어노테이션 탭: @EndUserText.label)
define abstract entity ZRAP_A_TKT_ESC_###
{
  ticket_no        : abap.numc(10);
  customer_id      : /dmo/customer_id;
  priority         : abap.char(1);
  escalation_level : abap.int1;
  sla_due_at       : abap.utclong;
}
```

```cds
@EndUserText.label: 'Message posted (child event payload)'
define abstract entity ZRAP_A_TMSG_EVT_###
{
  ticket_uuid  : sysuuid_x16;       // 자식 이벤트의 %key는 메시지 키뿐이라 부모 키를 payload로 전달
  author_type  : abap.char(1);
  is_internal  : abap_boolean;
  message_text : abap.char(255);
}
```

deep 파라미터(루트):

```cds
@EndUserText.label: 'Ticket closed (deep event payload)'
define root abstract entity ZRAP_D_TKT_CLOSED_###
{
  key ticket_uuid      : sysuuid_x16;
      ticket_no        : abap.numc(10);
      title            : abap.char(80);
      customer_id      : /dmo/customer_id;
      escalation_level : abap.int1;
      message_count    : abap.int4;
      closed_at        : abap.utclong;
      _Messages        : composition [0..*] of ZRAP_D_TKT_CLMSG_###;   // 추상 엔터티의 컴포지션: AS 없이 이름 : composition …
}
```

deep 파라미터(자식):

```cds
@EndUserText.label: 'Ticket closed - message line'
define abstract entity ZRAP_D_TKT_CLMSG_###
{
  key message_uuid : sysuuid_x16;
      ticket_uuid  : sysuuid_x16;
      author_type  : abap.char(1);
      message_text : abap.char(255);
      _Closed      : association to parent ZRAP_D_TKT_CLOSED_###
                       on _Closed.ticket_uuid = $projection.ticket_uuid;   // 대상이 추상 엔터티면 ON은 생략 가능
}
```

추상 BDEF (`ZRAP_D_TKT_CLOSED_###`, 루트 추상 엔터티에서 New → Behavior Definition):

```bdef
abstract;                 // 구현 유형: 추상 BDEF (파라미터 타입 전용, 트랜잭션 행동 없음)
strict ( 2 );
with hierarchy;           // 컴포지션을 따라 "구조 안에 표"가 들어가는 계층형 파생 타입을 만듦

define behavior for ZRAP_D_TKT_CLOSED_### alias Closed
{
  association _Messages;  // 자식을 같은 BDEF에 포함하면 컴포지션을 반드시 association으로 적어야 함
}

define behavior for ZRAP_D_TKT_CLMSG_### alias ClosedMessage
{
}
```

파생 이벤트 payload:

```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED             // (→ 어노테이션 탭: @AccessControl.authorizationCheck)
@EndUserText.label: 'Ticket contact (derived event payload)'
define view entity ZRAP_P_TKT_CONTACT_###
  as select from zrap_tkt_a_###   as Ticket
    inner join   /DMO/I_Customer as Customer on Customer.CustomerID = Ticket.customer_id
{
  key Ticket.ticket_uuid    as TicketUUID,     // 키 = 이벤트가 정의된 엔터티(Ticket)의 키와 같아야 함
      Ticket.ticket_no      as TicketNo,
      Customer.FirstName    as FirstName,
      Customer.LastName     as LastName,
      Customer.EMailAddress as EMailAddress
}
```

해설

- **평면 파라미터**(`parameter`): CDS 추상 엔터티의 필드 하나하나가 `%param`의 컴포넌트가 됩니다. R-04 8단계의 `ZRAP_A_TRAVEL_EVT_###`와 같습니다.
- **deep 파라미터**(`deep parameter`): ABAP 키워드 문서(RAP - `event`)에 따르면 `deep parameter`에는 `with hierarchy`가 있는 **추상 BDEF**를 지정해야 하고, 파생 타입은 "모든 엔터티 필드 + 컴포지션마다 컴포넌트 하나"인 계층이 됩니다. 컴포지션 카디널리티가 `[0..*]`이므로 `%param-_Messages`는 **내부 테이블**, `[0..1]`이었다면 구조가 됩니다(문서 RAP - `with hierarchy`).
- **추상 엔터티의 컴포지션 문법**은 뷰 엔터티와 조금 다릅니다. 뷰 엔터티는 `composition [0..*] of X as _Name`(헤더에 선언)이지만, 추상 엔터티는 요소 목록 안에 `_Name : composition [0..*] of X`로 적고 `AS`를 쓰지 않습니다. 부모 연관의 `ON` 조건은 대상이 추상 엔터티이면 생략할 수 있습니다(문서 CDS DDL - abstract entity `COMPOSITION` / `ASSOCIATION TO PARENT`). 여기서는 읽기 쉽게 적었습니다.
- 추상 BDEF 규칙: 자식 엔터티를 같은 추상 BDEF에 넣으면 부모 쪽에 `association _Messages;`가 **반드시** 있어야 하고, 자식 행동을 정의하지 않으면 반대로 적으면 안 됩니다. 자식의 부모 연관(`_Closed`)은 적지 않아도 됩니다(실제 시스템에서 확인 필요: 활성화 경고가 나오면 자식 본문에 `association _Closed;`를 추가해 보세요). `with control`은 액션 입력 파라미터에서 "어떤 필드를 채웠는지" 표시할 때 쓰는 것이라 이벤트 payload에는 넣지 않았습니다.
- **파생 이벤트 payload는 뷰 엔터티**입니다. 문서(RAP - `managed event`) 규칙: ① CDS **뷰 엔터티**일 것, ② **연관이 없을 것**, ③ 키 필드가 원래 이벤트가 정의된 엔터티의 키와 **같을 것**, ④ payload는 항상 평면(deep 불가). 프레임워크는 원래 이벤트의 키로 이 뷰를 읽어 payload를 채우며, 이때 **PRIVILEGED 접근**(권한 검사 없음)으로 읽습니다. 그래서 `@AccessControl.authorizationCheck: #NOT_REQUIRED`로 두고, 민감한 필드는 넣지 않는 것이 좋습니다. Flight Reference Scenario의 `/DMO/ZZ_P_AgencyReview_Contact`(`/DMO/I_Agency` 위의 뷰 엔터티)가 같은 패턴입니다.
- 조인한 `/DMO/I_Customer`에는 `_Country` 연관이 있지만, 이 뷰가 그 연관을 **노출하지 않으므로** "연관 없음" 조건을 지킵니다.

</details>

#### 5단계. 행동 정의: 이벤트 다섯 종류와 사이드 이펙트 전부

요구사항

1. 헤더: 관리형, `with additional save with full data`, 구현 클래스 `ZBP_RAP_R_TICKET_###`, strict 2, draft.
2. Ticket(루트): draft 테이블, `lock master`, `total etag LastChangedAt`, `etag master LocalLastChangedAt`, `authorization master ( global )`.
   - 표준 연산: create, update/delete(인스턴스 기능 제어), `_Messages` 생성(인스턴스 기능 제어, draft).
   - 필드: `TicketUUID`는 `numbering : managed` + 읽기 전용, 서버가 바꾸는 필드(TicketNo, Status, EscalationLevel, OpenedAt, SlaDueAt, SlaStatus, SlaCriticality, MessageCount, LastMessageAt, 관리 필드)는 읽기 전용, Title/CustomerID/Category는 필수.
   - 액션(인스턴스 기능 제어, `result [1] $self`): `escalate`, `closeTicket`, `reopenTicket`.
   - 결정: `setInitialValues`(on modify, create), `setTicketNo`(on save, create), `calcSlaDue`(on save, create + Priority, Category), `calcSlaStatus`(on save, create + SlaDueAt, Status).
   - 검증: `validateCustomer`, `validateCategory`(on save).
   - determine action: `recalcSla`(calcSlaDue·calcSlaStatus 강제 실행 + validateCategory), `refreshSla`(calcSlaStatus 강제 실행).
   - Prepare에 두 검증 연결.
   - **이벤트**: `ticket_created`(파라미터 없음), `ticket_escalated`(평면), `ticket_closed`(deep), 파생 이벤트 `ticket_created_contact`(`ticket_created` 기반), 사이드 이펙트 전용 `escalation_changed`.
   - **사이드 이펙트**:
     - 우선순위·분류(필드 그룹)가 바뀌면 `recalcSla` 실행 → SLA 세 필드 + 메시지 다시 읽기
     - **전역**: `refreshSla`를 `executed on global`로 → SLA 상태·색 다시 읽기
     - `escalate` → 버튼 권한(escalate) + 메시지
     - `closeTicket`, `reopenTicket` → 메시지 표(entity `_Messages`), 권한(세 액션, update, `create _Messages`), 메시지
     - **이벤트** `escalation_changed` → Priority, EscalationLevel, SLA 세 필드, 메시지 표
3. Message(자식): draft 테이블, `lock dependent by _Ticket`, `authorization dependent by _Ticket`, `etag master LocalLastChangedAt`.
   - update(인스턴스 기능 제어). **delete는 정의하지 않음**(대화 기록은 지우지 않음).
   - 필드: MessageUUID managed + 읽기 전용, TicketUUID/PostedBy/PostedAt/LocalLastChangedAt 읽기 전용, MessageText/AuthorType 필수, IsInternal은 **필드 단위 인스턴스 기능 제어**.
   - 결정 `updateTicketStats`(on modify, create + AuthorType, IsInternal): 부모 티켓의 메시지 수·마지막 시각·상태 갱신.
   - **자식 이벤트** `message_posted`(평면 파라미터 `ZRAP_A_TMSG_EVT_###`).
   - **사이드 이펙트**: `$self affects` 부모의 MessageCount/LastMessageAt/Status, `field AuthorType affects permissions ( field IsInternal )`.
4. 두 엔터티 모두 `mapping for` 테이블.

**확인**

- 저장하면 "메서드가 구현되지 않았다"는 경고(또는 오류)가 나옵니다. 정상입니다. `implementation in class` 줄의 클래스 이름에서 Ctrl+1로 행동 풀을 만들고, 6~7단계로 갑니다.
- 문법 오류(빨간 줄)는 없어야 합니다. 특히 `executed on global`, `event … for side effects`, 자식 엔터티의 `event` 줄에 오류가 나면 해설의 "(실제 시스템에서 확인 필요)" 항목을 보세요.

<details><summary>정답·해설</summary>

```bdef
managed with additional save with full data   // save_modified에서 이벤트를 발생시키기 위해 추가 저장. full data: 변경 안 된 필드도 받음
implementation in class zbp_rap_r_ticket_### unique;
strict ( 2 );
with draft;

define behavior for ZRAP_R_TICKET_### alias Ticket
persistent table zrap_tkt_a_###
draft table zrap_tkt_d_###
lock master
total etag LastChangedAt
authorization master ( global )
etag master LocalLastChangedAt
{
  create;
  update ( features : instance );
  delete ( features : instance );
  association _Messages { create ( features : instance ); with draft; }

  field ( numbering : managed, readonly ) TicketUUID;
  field ( readonly ) TicketNo, Status, EscalationLevel, OpenedAt, SlaDueAt, SlaStatus, SlaCriticality,
                     MessageCount, LastMessageAt,
                     CreatedBy, CreatedAt, LocalLastChangedBy, LocalLastChangedAt, LastChangedAt;
  field ( mandatory ) Title, CustomerID, Category;

  action ( features : instance ) escalate     result [1] $self;
  action ( features : instance ) closeTicket  result [1] $self;
  action ( features : instance ) reopenTicket result [1] $self;

  determination setInitialValues on modify { create; }
  determination setTicketNo      on save   { create; }
  determination calcSlaDue       on save   { create; field Priority, Category; }
  determination calcSlaStatus    on save   { create; field SlaDueAt, Status; }

  validation validateCustomer on save { create; field CustomerID; }
  validation validateCategory on save { create; field Category; }

  // determine action: on save 결정/검증을 "지금" 실행. (always)는 트리거 조건과 상관없이 실행
  determine action recalcSla
  {
    determination ( always ) calcSlaDue;
    determination ( always ) calcSlaStatus;
    validation validateCategory;
  }
  determine action refreshSla
  {
    determination ( always ) calcSlaStatus;
  }

  draft action Resume;
  draft action Edit;
  draft action Activate optimized;
  draft action Discard;
  draft determine action Prepare
  {
    validation validateCustomer;
    validation validateCategory;
  }

  // ---------- RAP business events ----------
  event ticket_created;                                              // 1) 파라미터 없음: %key만
  event ticket_escalated parameter ZRAP_A_TKT_ESC_###;               // 2) 평면 파라미터
  event ticket_closed deep parameter ZRAP_D_TKT_CLOSED_###;          // 3) deep 파라미터(추상 BDEF with hierarchy)
  managed event ticket_created_contact on ticket_created
                parameter ZRAP_P_TKT_CONTACT_###;                    // 4) 파생 이벤트: 구현 없음, payload = 뷰 엔터티
  event escalation_changed for side effects;                         // 5) 사이드 이펙트 전용 이벤트

  side effects
  {
    // 트리거 = 필드 그룹(Priority, Category). 그룹 밖으로 커서가 나가면 determine action 실행
    determine action recalcSla executed on field Priority, field Category
      affects field SlaDueAt, field SlaStatus, field SlaCriticality, messages;

    // 전역 사이드 이펙트: 사용자가 전용 단축키로 호출 (9.18, 실제 시스템에서 확인 필요)
    determine action refreshSla executed on global
      affects field SlaStatus, field SlaCriticality;

    // 액션 → 버튼 상태(권한/기능 제어) + 메시지
    action escalate affects permissions ( action escalate ), messages;

    // 액션 → 자식 엔터티 표 전체 + 여러 권한 + 메시지
    action closeTicket affects entity _Messages,
                               permissions ( action escalate, action closeTicket, action reopenTicket,
                                             update, create _Messages ),
                               messages;
    action reopenTicket affects entity _Messages,
                                permissions ( action escalate, action closeTicket, action reopenTicket,
                                              update, create _Messages ),
                                messages;

    // 이벤트 기반 사이드 이펙트: 서버가 이 이벤트를 발생시키면 열린 화면이 대상을 다시 읽음 (9.14)
    event escalation_changed affects field Priority, field EscalationLevel,
                                     field SlaDueAt, field SlaStatus, field SlaCriticality,
                                     entity _Messages;
  }

  mapping for zrap_tkt_a_###
  {
    TicketUUID         = ticket_uuid;
    TicketNo           = ticket_no;
    Title              = title;
    CustomerID         = customer_id;
    Category           = category;
    Priority           = priority;
    Status             = status;
    EscalationLevel    = escalation_level;
    OpenedAt           = opened_at;
    SlaDueAt           = sla_due_at;
    SlaStatus          = sla_status;
    SlaCriticality     = sla_criticality;
    MessageCount       = message_count;
    LastMessageAt      = last_message_at;
    CreatedBy          = created_by;
    CreatedAt          = created_at;
    LocalLastChangedBy = local_last_changed_by;
    LocalLastChangedAt = local_last_changed_at;
    LastChangedAt      = last_changed_at;
  }
}

define behavior for ZRAP_R_TKTMSG_### alias Message
persistent table zrap_tmsg_a_###
draft table zrap_tmsg_d_###
lock dependent by _Ticket
authorization dependent by _Ticket
etag master LocalLastChangedAt
{
  update ( features : instance );
  // delete 없음: 대화 기록은 지우지 않음

  field ( numbering : managed, readonly ) MessageUUID;
  field ( readonly ) TicketUUID, PostedBy, PostedAt, LocalLastChangedAt;
  field ( mandatory ) MessageText, AuthorType;
  field ( features : instance ) IsInternal;      // 필드 단위 동적 기능 제어

  determination updateTicketStats on modify { create; field AuthorType, IsInternal; }

  association _Ticket { with draft; }

  // 자식 엔터티 이벤트 (7.96부터)
  event message_posted parameter ZRAP_A_TMSG_EVT_###;

  side effects
  {
    // $self: 이 엔터티(메시지)에 생성/변경이 일어나면 부모 필드를 다시 읽음. 자기 필드는 대상 불가
    $self affects field _Ticket.MessageCount, field _Ticket.LastMessageAt, field _Ticket.Status;
    // 필드 → 다른 필드의 기능 제어(편집 가능 여부) 다시 읽기
    field AuthorType affects permissions ( field IsInternal );
  }

  mapping for zrap_tmsg_a_###
  {
    MessageUUID        = message_uuid;
    TicketUUID         = ticket_uuid;
    MessageText        = message_text;
    AuthorType         = author_type;
    IsInternal         = is_internal;
    PostedBy           = posted_by;
    PostedAt           = posted_at;
    LocalLastChangedAt = local_last_changed_at;
  }
}
```

**이벤트 줄 해설**

| 줄 | 종류 | 누가 발생시키나 | payload |
|---|---|---|---|
| `event ticket_created;` | 기본 이벤트 | `save_modified`에서 `RAISE ENTITY EVENT` | `%key`(TicketUUID)만 |
| `event ticket_escalated parameter …;` | 평면 파라미터 | `save_modified` | `%key` + `%param`(추상 엔터티 필드) |
| `event ticket_closed deep parameter …;` | deep 파라미터 | `save_modified` | `%key` + `%param`(헤더 필드 + `_Messages` 표) |
| `managed event ticket_created_contact on ticket_created parameter …;` | 파생 이벤트 | **프레임워크**가 `ticket_created`와 함께 자동 발생 | 뷰 엔터티를 키로 읽은 결과(고객 이름·이메일) |
| `event escalation_changed for side effects;` | 사이드 이펙트 전용 | `save_modified` | `%key`만. 화면 갱신 신호로만 씀 |
| Message의 `event message_posted parameter …;` | 자식 엔터티 이벤트 | `save_modified` (`RAISE ENTITY EVENT zrap_r_tktmsg_###~…`) | `%key`(MessageUUID) + `%param` |

- 파생 이벤트 문법은 ABAP 키워드 문서 `managed event DerivedEventName on RefEvent parameter ViewEntityName;` 그대로입니다. 문서 예는 BDEF 확장(`extend behavior`)에서 정의하지만, 문서 설명대로 "참조 이벤트는 현재 BDEF의 이벤트"이면 기본 BDEF에 바로 써도 됩니다. 파생 이벤트는 행동 풀 구현이 **필요 없습니다**.
- 자식 엔터티 이벤트는 릴리스 7.96(2405)부터입니다. 그전에는 루트에만 이벤트를 정의할 수 있었습니다.
- `for side effects` 이벤트는 문서상 "event-driven side effect에만" 쓰는 이벤트입니다. 다른 소비자(로컬 핸들러, 이벤트 바인딩)용이 아니므로, 같은 상황을 외부에 알리려면 `ticket_escalated`처럼 일반 이벤트를 따로 둡니다.

**사이드 이펙트 해설** (R-02 9단계 표의 확장)

| 이 BDEF의 줄 | 트리거 | 대상 | 화면에서 일어나는 일 |
|---|---|---|---|
| `determine action recalcSla executed on field Priority, field Category affects …, messages` | **필드 그룹** | 필드 3개 + 메시지 | 우선순위나 분류를 바꾸고 두 필드 밖으로 나가면 서버가 SLA를 계산, 기한·신호등이 바뀌고 분류 오류 메시지가 즉시 뜸 |
| `determine action refreshSla executed on global affects …` | **전역**(사용자 단축키) | 필드 2개 | 아무것도 바꾸지 않아도 사용자가 단축키를 누르면 SLA 신호등을 현재 시각 기준으로 다시 계산 |
| `action escalate affects permissions ( action escalate ), messages` | 액션 | 권한, 메시지 | 3단계까지 올리면 Escalate 버튼이 즉시 비활성화, 성공 메시지 |
| `action closeTicket affects entity _Messages, permissions ( …, update, create _Messages ), messages` | 액션 | **자식 표**, **여러 권한**, 메시지 | 닫으면 "Ticket closed" 시스템 메시지 줄이 표에 바로 나타나고, Edit/Close/Escalate 버튼과 메시지 추가(+) 버튼 상태가 바로 바뀜 |
| `event escalation_changed affects …, entity _Messages` | **이벤트** | 필드 5개 + 자식 표 | 백그라운드에서 에스컬레이션되면, 그 티켓을 보고 있던 화면이 새로 고침 없이 우선순위·단계·SLA·메시지 표를 다시 읽음 |
| `$self affects field _Ticket.MessageCount, …` | **$self**(자식 CUD) | 부모 필드 | 메시지 줄을 추가하거나 작성자 유형을 바꾸면 헤더의 메시지 수·마지막 시각·상태가 바로 바뀜 |
| `field AuthorType affects permissions ( field IsInternal )` | 필드 | 다른 필드 권한 | 작성자를 A로 바꾸면 Internal 체크박스가 편집 가능해지고, C로 바꾸면 읽기 전용으로 바뀜 |

- **필드 그룹**: determine action의 `executed on` 뒤에 필드를 여러 개 쓰면 그 필드들이 하나의 그룹으로 간주되어, 하나 이상 바꾼 뒤 **그룹 밖으로 커서가 나갈 때** 한 번만 실행됩니다(문서 RAP - `side effects`). 소스는 `field (Priority, Category)`, `field _Assoc.X`, `$self`, `entity _Assoc`, `entity (_A1, _A2)` 형태도 됩니다. Fiori Feature Showcase는 `determine action updateTimes executed on entity _Child affects field TotalPieces;`처럼 자식 변경을 소스로 씁니다.
- **permissions 목록**: 문서에 "여러 권한을 괄호 안에 쉼표로 나열"(`permissions(action MyActionFC, update)`)과 `( {create|update|delete} _assoc )`가 모두 있으므로 위 형식은 문서 문법 안에 있습니다.
- **`$self` 제약**: 트리거가 `$self`이면 대상에 자기 엔터티 필드나 `$self`를 쓸 수 없고, 연관 경로(`_Ticket.X`)로만 다른 엔터티를 지정할 수 있습니다. 반대로 대상이 `$self`인 형태(`action X affects $self;`)는 Feature Showcase의 `action overwriteTimezone affects $self;`에 있습니다.
- **전역 사이드 이펙트**(`executed on global`): 치트시트 33(릴리스 9.18, 2602)의 문장 "Global side effects are invoked by an end user with a dedicated key stroke. … `side effects { determine action MyDetermineAction executed on global affects field MyField; }`"을 그대로 따랐습니다. 이 문법은 로컬로 받은 ABAP 키워드 문서 미러(`ABENBDL_SIDE_EFFECTS`)에는 아직 없고 릴리스 뉴스에서만 확인했습니다. 어느 키를 눌러야 하는지(전용 단축키)도 자료에서 확인하지 못했습니다(실제 시스템에서 확인 필요).
- **이벤트 기반 사이드 이펙트**: 일반 사이드 이펙트는 "UI에서 사용자가 한 일"(필드 변경, 액션)이 트리거입니다. 이벤트 기반은 트리거가 **서버에서 발생한 이벤트**라서, 다른 사용자·백그라운드 작업·이벤트 소비자가 데이터를 바꿨을 때도 열린 화면이 따라옵니다. 문서상 이벤트는 `for side effects`로 정의하고 `side effects { event X affects … }`로 대상을 정합니다. 서버에서 브라우저로 알림을 밀어 주는 채널이 필요하므로, 실제 동작은 Fiori Elements(UI5) 버전과 미리보기 환경의 지원에 달려 있습니다(실제 시스템에서 확인 필요).
- `with full data`: `save_modified`의 `update-ticket`에 바뀌지 않은 필드도 채워 줍니다. 이벤트 payload에 우선순위·고객 같은 값을 다시 읽지 않고 넣기 위해 필요합니다(RAP110 ex11).

**자주 나는 오류와 해결**

- `ticket_created_contact`에서 "키가 맞지 않는다"류 오류 → payload 뷰의 키 이름·타입이 `TicketUUID`(sysuuid_x16)와 같은지, 뷰에 연관이 없는지 확인하세요.
- `executed on global`에 문법 오류 → 시스템 릴리스가 9.18 미만이면 지원되지 않습니다. ADT에서 About(시스템 정보)로 릴리스를 확인하고, 안 되면 그 줄만 주석 처리해 나머지를 진행하세요.
- 사이드 이펙트 대상에 정의되지 않은 액션/필드를 적으면 활성화 오류가 납니다. 이름은 대소문자까지 BDEF 정의와 같게 쓰세요.

**클래스 구조 해설** 이 BDEF에서 생기는 행동 풀 메서드: `get_instance_features`(Ticket, Message 각각), `get_global_authorizations`, 결정 5개, 검증 2개, 액션 3개. 이벤트·파생 이벤트·사이드 이펙트·determine action 줄은 **핸들러 메서드를 만들지 않습니다**. 이벤트는 세이버의 `save_modified`에서 직접 발생시키고(7단계), 파생 이벤트와 사이드 이펙트는 프레임워크/OData 메타데이터가 처리합니다.

</details>

#### 6단계. 행동 풀: 기능 제어, 결정, 검증, 액션 (사이드 이펙트가 "다시 읽을 값"을 만드는 코드)

요구사항

1. 행동 풀 `ZBP_RAP_R_TICKET_###`의 Local Types에 상수·도우미 클래스 `lcl_tkt`를 먼저 두세요.
   - 상수: 상태(N/P/W/C), 우선순위(L/M/H/U), 작성자(C/A/S), 최대 에스컬레이션 단계 3.
   - `next_priority( )`: L→M→H→U, U는 그대로.
   - `sla_hours( )`: U 4시간, H 8시간, M 24시간, L 72시간, 분류 `AC`는 24시간 추가.
   - `sla_light( )`: 닫힘이거나 기한이 없으면 공백/0, 기한 지남 R/1, 2시간 미만 Y/2, 그 외 G/3.
2. `lhc_ticket`:
   - `get_global_authorizations`: 데모이므로 모두 허용(실무는 R-03 6단계처럼 권한 객체 검사).
   - `get_instance_features`: 닫힌 티켓은 update/delete/메시지 추가/Close/Escalate 비활성, Reopen은 닫힌 티켓에서만 활성, Escalate는 단계 3 이상이면 비활성.
   - `setInitialValues`(on modify): 처음 만들 때만 Priority 기본 M, Status N, EscalationLevel 0, OpenedAt 현재 시각.
   - `setTicketNo`(on save): 현재 최대 번호 + 1.
   - `calcSlaDue`, `calcSlaStatus`(on save): 위 규칙대로.
   - `validateCustomer`, `validateCategory`: state message(`%state_area`), 오류 시 `failed` + `reported`.
   - `escalate`: Priority 한 단계 올림, EscalationLevel + 1, **시스템 메시지(Message, 작성자 S, 내부 메모)를 자식으로 추가**, 성공 메시지 004.
   - `closeTicket`: Status C, 시스템 메시지 "Ticket closed by 사용자", 성공 메시지 005.
   - `reopenTicket`: Status P, 시스템 메시지 "Ticket reopened", 성공 메시지 006.
3. `lhc_message`:
   - `get_instance_features`: 시스템 메시지(S)는 수정 불가, `IsInternal`은 작성자가 A일 때만 편집 가능.
   - `updateTicketStats`(on modify): 부모 티켓의 MessageCount(전체 메시지 수), LastMessageAt(현재 시각), Status(고객 메시지 → P, 상담원 공개 메시지 → W, 내부 메모·시스템 메시지 → 그대로, 닫힌 티켓은 그대로)를 갱신.

**확인**

- 행동 풀이 활성화되고 BDEF의 경고가 사라집니다.
- 8단계 서비스를 만든 뒤 확인하므로 이 단계만으로는 화면 변화가 없습니다. 원하면 7단계까지 끝낸 뒤 11단계 콘솔 클래스로 먼저 확인해도 됩니다.

<details><summary>정답·해설</summary>

Local Types 탭 앞부분(도우미 + Ticket 핸들러):

```abap
"! Constants and small calculations shared by handlers and saver
CLASS lcl_tkt DEFINITION ABSTRACT FINAL.
  PUBLIC SECTION.
    CONSTANTS:
      BEGIN OF status,
        new      TYPE c LENGTH 1 VALUE 'N',
        progress TYPE c LENGTH 1 VALUE 'P',
        waiting  TYPE c LENGTH 1 VALUE 'W',
        closed   TYPE c LENGTH 1 VALUE 'C',
      END OF status,
      BEGIN OF priority,
        low    TYPE c LENGTH 1 VALUE 'L',
        medium TYPE c LENGTH 1 VALUE 'M',
        high   TYPE c LENGTH 1 VALUE 'H',
        urgent TYPE c LENGTH 1 VALUE 'U',
      END OF priority,
      BEGIN OF author,
        customer TYPE c LENGTH 1 VALUE 'C',
        agent    TYPE c LENGTH 1 VALUE 'A',
        system   TYPE c LENGTH 1 VALUE 'S',
      END OF author,
      max_escalation_level TYPE i VALUE 3.

    TYPES c_prio TYPE c LENGTH 1.
    TYPES:
      BEGIN OF ty_light,
        status      TYPE c LENGTH 1,
        criticality TYPE i,
      END OF ty_light.

    "parameter names differ from the constant names (status, priority) on purpose
    CLASS-METHODS next_priority
      IMPORTING current       TYPE c
      RETURNING VALUE(result) TYPE c_prio.

    CLASS-METHODS sla_hours
      IMPORTING prio          TYPE c
                category      TYPE c
      RETURNING VALUE(result) TYPE i.

    CLASS-METHODS sla_light
      IMPORTING ticket_status TYPE c
                due           TYPE utclong
      RETURNING VALUE(result) TYPE ty_light.
ENDCLASS.


CLASS lcl_tkt IMPLEMENTATION.

  METHOD next_priority.
    result = SWITCH #( current
                       WHEN priority-low    THEN priority-medium
                       WHEN priority-medium THEN priority-high
                       ELSE priority-urgent ).
  ENDMETHOD.

  METHOD sla_hours.
    result = SWITCH #( prio
                       WHEN priority-urgent THEN 4
                       WHEN priority-high   THEN 8
                       WHEN priority-low    THEN 72
                       ELSE 24 ).
    IF category = 'AC'.
      result = result + 24.
    ENDIF.
  ENDMETHOD.

  METHOD sla_light.
    IF ticket_status = status-closed OR due IS INITIAL.
      result = VALUE #( status = ' ' criticality = 0 ).
      RETURN.
    ENDIF.

    DATA(remaining_seconds) = utclong_diff( high = due
                                            low  = utclong_current( ) ).
    result = COND #( WHEN remaining_seconds < 0    THEN VALUE #( status = 'R' criticality = 1 )
                     WHEN remaining_seconds < 7200 THEN VALUE #( status = 'Y' criticality = 2 )
                     ELSE                               VALUE #( status = 'G' criticality = 3 ) ).
  ENDMETHOD.

ENDCLASS.


CLASS lhc_ticket DEFINITION INHERITING FROM cl_abap_behavior_handler.
  PRIVATE SECTION.

    METHODS get_global_authorizations FOR GLOBAL AUTHORIZATION
      IMPORTING REQUEST requested_authorizations FOR Ticket RESULT result.

    METHODS get_instance_features FOR INSTANCE FEATURES
      IMPORTING keys REQUEST requested_features FOR Ticket RESULT result.

    METHODS setInitialValues FOR DETERMINE ON MODIFY
      IMPORTING keys FOR Ticket~setInitialValues.

    METHODS setTicketNo FOR DETERMINE ON SAVE
      IMPORTING keys FOR Ticket~setTicketNo.

    METHODS calcSlaDue FOR DETERMINE ON SAVE
      IMPORTING keys FOR Ticket~calcSlaDue.

    METHODS calcSlaStatus FOR DETERMINE ON SAVE
      IMPORTING keys FOR Ticket~calcSlaStatus.

    METHODS validateCustomer FOR VALIDATE ON SAVE
      IMPORTING keys FOR Ticket~validateCustomer.

    METHODS validateCategory FOR VALIDATE ON SAVE
      IMPORTING keys FOR Ticket~validateCategory.

    METHODS escalate FOR MODIFY
      IMPORTING keys FOR ACTION Ticket~escalate RESULT result.

    METHODS closeTicket FOR MODIFY
      IMPORTING keys FOR ACTION Ticket~closeTicket RESULT result.

    METHODS reopenTicket FOR MODIFY
      IMPORTING keys FOR ACTION Ticket~reopenTicket RESULT result.

ENDCLASS.


CLASS lhc_ticket IMPLEMENTATION.

  METHOD get_global_authorizations.
    "Demo: everything allowed. A real BO checks an IAM authorization object here (see R-03).
    result = VALUE #( %create              = if_abap_behv=>auth-allowed
                      %update              = if_abap_behv=>auth-allowed
                      %delete              = if_abap_behv=>auth-allowed
                      %action-escalate     = if_abap_behv=>auth-allowed
                      %action-closeTicket  = if_abap_behv=>auth-allowed
                      %action-reopenTicket = if_abap_behv=>auth-allowed ).
  ENDMETHOD.


  METHOD get_instance_features.
    READ ENTITIES OF zrap_r_ticket_### IN LOCAL MODE
      ENTITY Ticket
        FIELDS ( Status EscalationLevel )
        WITH CORRESPONDING #( keys )
      RESULT DATA(tickets)
      FAILED failed.

    result = VALUE #(
      FOR ticket IN tickets
      LET is_closed = xsdbool( ticket-Status = lcl_tkt=>status-closed ) IN
      ( %tky                 = ticket-%tky
        %update              = COND #( WHEN is_closed = abap_true THEN if_abap_behv=>fc-o-disabled
                                                                  ELSE if_abap_behv=>fc-o-enabled )
        %delete              = COND #( WHEN is_closed = abap_true THEN if_abap_behv=>fc-o-disabled
                                                                  ELSE if_abap_behv=>fc-o-enabled )
        %assoc-_Messages     = COND #( WHEN is_closed = abap_true THEN if_abap_behv=>fc-o-disabled
                                                                  ELSE if_abap_behv=>fc-o-enabled )
        %action-closeTicket  = COND #( WHEN is_closed = abap_true THEN if_abap_behv=>fc-o-disabled
                                                                  ELSE if_abap_behv=>fc-o-enabled )
        %action-reopenTicket = COND #( WHEN is_closed = abap_true THEN if_abap_behv=>fc-o-enabled
                                                                  ELSE if_abap_behv=>fc-o-disabled )
        %action-escalate     = COND #( WHEN is_closed = abap_true
                                         OR ticket-EscalationLevel >= lcl_tkt=>max_escalation_level
                                       THEN if_abap_behv=>fc-o-disabled
                                       ELSE if_abap_behv=>fc-o-enabled ) ) ).
  ENDMETHOD.


  METHOD setInitialValues.
    READ ENTITIES OF zrap_r_ticket_### IN LOCAL MODE
      ENTITY Ticket
        FIELDS ( Priority OpenedAt )
        WITH CORRESPONDING #( keys )
      RESULT DATA(tickets).

    "only instances that were never initialized
    DELETE tickets WHERE OpenedAt IS NOT INITIAL.
    CHECK tickets IS NOT INITIAL.

    DATA(now) = utclong_current( ).

    MODIFY ENTITIES OF zrap_r_ticket_### IN LOCAL MODE
      ENTITY Ticket
        UPDATE FIELDS ( Priority Status EscalationLevel OpenedAt )
        WITH VALUE #( FOR ticket IN tickets
                      ( %tky            = ticket-%tky
                        Priority        = COND #( WHEN ticket-Priority IS INITIAL
                                                  THEN lcl_tkt=>priority-medium
                                                  ELSE ticket-Priority )
                        Status          = lcl_tkt=>status-new
                        EscalationLevel = 0
                        OpenedAt        = now ) ).
  ENDMETHOD.


  METHOD setTicketNo.
    READ ENTITIES OF zrap_r_ticket_### IN LOCAL MODE
      ENTITY Ticket
        FIELDS ( TicketNo )
        WITH CORRESPONDING #( keys )
      RESULT DATA(tickets).

    DELETE tickets WHERE TicketNo IS NOT INITIAL.
    CHECK tickets IS NOT INITIAL.

    "Simple for the exercise. Productive code uses a number range object (R-04 step 3).
    SELECT SINGLE FROM zrap_tkt_a_###
      FIELDS MAX( ticket_no )
      INTO @DATA(max_no).

    MODIFY ENTITIES OF zrap_r_ticket_### IN LOCAL MODE
      ENTITY Ticket
        UPDATE FIELDS ( TicketNo )
        WITH VALUE #( FOR ticket IN tickets INDEX INTO idx
                      ( %tky     = ticket-%tky
                        TicketNo = max_no + idx ) ).
  ENDMETHOD.


  METHOD calcSlaDue.
    READ ENTITIES OF zrap_r_ticket_### IN LOCAL MODE
      ENTITY Ticket
        FIELDS ( Priority Category OpenedAt )
        WITH CORRESPONDING #( keys )
      RESULT DATA(tickets).

    DATA(now) = utclong_current( ).

    MODIFY ENTITIES OF zrap_r_ticket_### IN LOCAL MODE
      ENTITY Ticket
        UPDATE FIELDS ( SlaDueAt )
        WITH VALUE #( FOR ticket IN tickets
                      ( %tky     = ticket-%tky
                        SlaDueAt = utclong_add(
                                     val   = COND utclong( WHEN ticket-OpenedAt IS INITIAL THEN now
                                                                                         ELSE ticket-OpenedAt )
                                     hours = lcl_tkt=>sla_hours( prio     = ticket-Priority
                                                                 category = ticket-Category ) ) ) ).
  ENDMETHOD.


  METHOD calcSlaStatus.
    READ ENTITIES OF zrap_r_ticket_### IN LOCAL MODE
      ENTITY Ticket
        FIELDS ( Status SlaDueAt )
        WITH CORRESPONDING #( keys )
      RESULT DATA(tickets).

    DATA updates TYPE TABLE FOR UPDATE zrap_r_ticket_###\\Ticket.

    LOOP AT tickets INTO DATA(ticket).
      DATA(light) = lcl_tkt=>sla_light( ticket_status = ticket-Status
                                        due           = ticket-SlaDueAt ).
      APPEND VALUE #( %tky           = ticket-%tky
                      SlaStatus      = light-status
                      SlaCriticality = light-criticality ) TO updates.
    ENDLOOP.

    MODIFY ENTITIES OF zrap_r_ticket_### IN LOCAL MODE
      ENTITY Ticket
        UPDATE FIELDS ( SlaStatus SlaCriticality )
        WITH updates.
  ENDMETHOD.


  METHOD validateCustomer.
    READ ENTITIES OF zrap_r_ticket_### IN LOCAL MODE
      ENTITY Ticket
        FIELDS ( CustomerID )
        WITH CORRESPONDING #( keys )
      RESULT DATA(tickets).

    DATA customer_ids TYPE SORTED TABLE OF /dmo/customer_id WITH UNIQUE KEY table_line.
    LOOP AT tickets INTO DATA(ticket) WHERE CustomerID IS NOT INITIAL.
      INSERT ticket-CustomerID INTO TABLE customer_ids.   "duplicates are ignored (sy-subrc = 4)
    ENDLOOP.

    IF customer_ids IS NOT INITIAL.
      SELECT FROM /DMO/I_Customer
        FIELDS CustomerID
        FOR ALL ENTRIES IN @customer_ids
        WHERE CustomerID = @customer_ids-table_line
        INTO TABLE @DATA(valid_customers).
    ENDIF.

    LOOP AT tickets INTO ticket.
      "clear old state messages of this validation
      APPEND VALUE #( %tky        = ticket-%tky
                      %state_area = 'VALIDATE_CUSTOMER' ) TO reported-ticket.

      IF ticket-CustomerID IS INITIAL.
        APPEND VALUE #( %tky = ticket-%tky ) TO failed-ticket.
        APPEND VALUE #( %tky                = ticket-%tky
                        %state_area         = 'VALIDATE_CUSTOMER'
                        %msg                = NEW zcm_rap_tkt_###( textid = zcm_rap_tkt_###=>enter_customer )
                        %element-CustomerID = if_abap_behv=>mk-on ) TO reported-ticket.
      ELSEIF NOT line_exists( valid_customers[ CustomerID = ticket-CustomerID ] ).
        APPEND VALUE #( %tky = ticket-%tky ) TO failed-ticket.
        APPEND VALUE #( %tky                = ticket-%tky
                        %state_area         = 'VALIDATE_CUSTOMER'
                        %msg                = NEW zcm_rap_tkt_###( textid      = zcm_rap_tkt_###=>customer_unknown
                                                                   customer_id = ticket-CustomerID )
                        %element-CustomerID = if_abap_behv=>mk-on ) TO reported-ticket.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.


  METHOD validateCategory.
    READ ENTITIES OF zrap_r_ticket_### IN LOCAL MODE
      ENTITY Ticket
        FIELDS ( Category )
        WITH CORRESPONDING #( keys )
      RESULT DATA(tickets).

    LOOP AT tickets INTO DATA(ticket).
      APPEND VALUE #( %tky        = ticket-%tky
                      %state_area = 'VALIDATE_CATEGORY' ) TO reported-ticket.

      IF ticket-Category <> 'HW' AND ticket-Category <> 'SW' AND ticket-Category <> 'AC'.
        APPEND VALUE #( %tky = ticket-%tky ) TO failed-ticket.
        APPEND VALUE #( %tky              = ticket-%tky
                        %state_area       = 'VALIDATE_CATEGORY'
                        %msg              = NEW zcm_rap_tkt_###( textid   = zcm_rap_tkt_###=>category_invalid
                                                                 category = ticket-Category )
                        %element-Category = if_abap_behv=>mk-on ) TO reported-ticket.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.


  METHOD escalate.
    READ ENTITIES OF zrap_r_ticket_### IN LOCAL MODE
      ENTITY Ticket
        FIELDS ( TicketNo Priority EscalationLevel )
        WITH CORRESPONDING #( keys )
      RESULT DATA(tickets).

    MODIFY ENTITIES OF zrap_r_ticket_### IN LOCAL MODE
      "1) raise priority and level
      ENTITY Ticket
        UPDATE FIELDS ( Priority EscalationLevel )
        WITH VALUE #( FOR ticket IN tickets
                      ( %tky            = ticket-%tky
                        Priority        = lcl_tkt=>next_priority( ticket-Priority )
                        EscalationLevel = ticket-EscalationLevel + 1 ) )
      "2) add a system message as child (-> side effect 'entity _Messages' makes it visible)
      ENTITY Ticket
        CREATE BY \_Messages
        FIELDS ( MessageText AuthorType IsInternal )
        WITH VALUE #( FOR ticket IN tickets INDEX INTO idx
                      ( %tky    = ticket-%tky
                        %target = VALUE #( ( %cid        = |ESC_{ idx }|
                                             %is_draft   = ticket-%is_draft
                                             MessageText = |Escalated to level { ticket-EscalationLevel + 1 }|
                                             AuthorType  = lcl_tkt=>author-system
                                             IsInternal  = abap_true ) ) ) ).

    "result [1] $self
    READ ENTITIES OF zrap_r_ticket_### IN LOCAL MODE
      ENTITY Ticket
        ALL FIELDS WITH CORRESPONDING #( keys )
      RESULT DATA(updated).

    result = VALUE #( FOR ticket IN updated ( %tky = ticket-%tky %param = ticket ) ).

    reported-ticket = VALUE #( FOR ticket IN updated
                               ( %tky = ticket-%tky
                                 %msg = NEW zcm_rap_tkt_###( textid    = zcm_rap_tkt_###=>ticket_escalated
                                                             ticket_no = ticket-TicketNo
                                                             level     = CONV #( ticket-EscalationLevel )
                                                             severity  = if_abap_behv_message=>severity-success ) ) ).
  ENDMETHOD.


  METHOD closeTicket.
    DATA(user) = cl_abap_context_info=>get_user_technical_name( ).

    MODIFY ENTITIES OF zrap_r_ticket_### IN LOCAL MODE
      ENTITY Ticket
        UPDATE FIELDS ( Status )
        WITH VALUE #( FOR key IN keys ( %tky = key-%tky Status = lcl_tkt=>status-closed ) )
      ENTITY Ticket
        CREATE BY \_Messages
        FIELDS ( MessageText AuthorType IsInternal )
        WITH VALUE #( FOR key IN keys INDEX INTO idx
                      ( %tky    = key-%tky
                        %target = VALUE #( ( %cid        = |CLOSE_{ idx }|
                                             %is_draft   = key-%is_draft
                                             MessageText = |Ticket closed by { user }|
                                             AuthorType  = lcl_tkt=>author-system
                                             IsInternal  = abap_false ) ) ) ).

    READ ENTITIES OF zrap_r_ticket_### IN LOCAL MODE
      ENTITY Ticket
        ALL FIELDS WITH CORRESPONDING #( keys )
      RESULT DATA(updated).

    result = VALUE #( FOR ticket IN updated ( %tky = ticket-%tky %param = ticket ) ).

    reported-ticket = VALUE #( FOR ticket IN updated
                               ( %tky = ticket-%tky
                                 %msg = NEW zcm_rap_tkt_###( textid    = zcm_rap_tkt_###=>ticket_closed
                                                             ticket_no = ticket-TicketNo
                                                             severity  = if_abap_behv_message=>severity-success ) ) ).
  ENDMETHOD.


  METHOD reopenTicket.
    MODIFY ENTITIES OF zrap_r_ticket_### IN LOCAL MODE
      ENTITY Ticket
        UPDATE FIELDS ( Status )
        WITH VALUE #( FOR key IN keys ( %tky = key-%tky Status = lcl_tkt=>status-progress ) )
      ENTITY Ticket
        CREATE BY \_Messages
        FIELDS ( MessageText AuthorType IsInternal )
        WITH VALUE #( FOR key IN keys INDEX INTO idx
                      ( %tky    = key-%tky
                        %target = VALUE #( ( %cid        = |REOPEN_{ idx }|
                                             %is_draft   = key-%is_draft
                                             MessageText = |Ticket reopened|
                                             AuthorType  = lcl_tkt=>author-system
                                             IsInternal  = abap_false ) ) ) ).

    READ ENTITIES OF zrap_r_ticket_### IN LOCAL MODE
      ENTITY Ticket
        ALL FIELDS WITH CORRESPONDING #( keys )
      RESULT DATA(updated).

    result = VALUE #( FOR ticket IN updated ( %tky = ticket-%tky %param = ticket ) ).

    reported-ticket = VALUE #( FOR ticket IN updated
                               ( %tky = ticket-%tky
                                 %msg = NEW zcm_rap_tkt_###( textid    = zcm_rap_tkt_###=>ticket_reopened
                                                             ticket_no = ticket-TicketNo
                                                             severity  = if_abap_behv_message=>severity-success ) ) ).
  ENDMETHOD.

ENDCLASS.
```

Local Types 탭 이어서(Message 핸들러):

```abap
CLASS lhc_message DEFINITION INHERITING FROM cl_abap_behavior_handler.
  PRIVATE SECTION.

    METHODS get_instance_features FOR INSTANCE FEATURES
      IMPORTING keys REQUEST requested_features FOR Message RESULT result.

    METHODS updateTicketStats FOR DETERMINE ON MODIFY
      IMPORTING keys FOR Message~updateTicketStats.

ENDCLASS.


CLASS lhc_message IMPLEMENTATION.

  METHOD get_instance_features.
    READ ENTITIES OF zrap_r_ticket_### IN LOCAL MODE
      ENTITY Message
        FIELDS ( AuthorType )
        WITH CORRESPONDING #( keys )
      RESULT DATA(messages)
      FAILED failed.

    result = VALUE #( FOR message IN messages
                      ( %tky              = message-%tky
                        %update           = COND #( WHEN message-AuthorType = lcl_tkt=>author-system
                                                    THEN if_abap_behv=>fc-o-disabled
                                                    ELSE if_abap_behv=>fc-o-enabled )
                        "field-level instance feature control
                        %field-IsInternal = COND #( WHEN message-AuthorType = lcl_tkt=>author-agent
                                                    THEN if_abap_behv=>fc-f-unrestricted
                                                    ELSE if_abap_behv=>fc-f-read_only ) ) ).
  ENDMETHOD.


  METHOD updateTicketStats.
    "1) the changed messages
    READ ENTITIES OF zrap_r_ticket_### IN LOCAL MODE
      ENTITY Message
        FIELDS ( TicketUUID AuthorType IsInternal )
        WITH CORRESPONDING #( keys )
      RESULT DATA(messages).

    "2) their parent tickets (source = message, target = ticket)
    READ ENTITIES OF zrap_r_ticket_### IN LOCAL MODE
      ENTITY Message BY \_Ticket
        FIELDS ( Status )
        WITH CORRESPONDING #( keys )
      LINK DATA(msg_links)
      RESULT DATA(tickets).

    CHECK tickets IS NOT INITIAL.

    "3) all messages of these tickets, to count them
    READ ENTITIES OF zrap_r_ticket_### IN LOCAL MODE
      ENTITY Ticket BY \_Messages
        FIELDS ( MessageUUID )
        WITH CORRESPONDING #( tickets )
      LINK DATA(all_links).

    DATA updates TYPE TABLE FOR UPDATE zrap_r_ticket_###\\Ticket.
    DATA(now) = utclong_current( ).

    LOOP AT tickets INTO DATA(ticket).
      DATA(new_status) = ticket-Status.

      IF ticket-Status <> lcl_tkt=>status-closed.
        LOOP AT msg_links INTO DATA(link) WHERE target-TicketUUID = ticket-TicketUUID.
          READ TABLE messages INTO DATA(message)
               WITH KEY MessageUUID = link-source-MessageUUID.
          IF sy-subrc <> 0.
            CONTINUE.
          ENDIF.
          CASE message-AuthorType.
            WHEN lcl_tkt=>author-customer.
              new_status = lcl_tkt=>status-progress.          "customer answered -> agent's turn
            WHEN lcl_tkt=>author-agent.
              IF message-IsInternal = abap_false.
                new_status = lcl_tkt=>status-waiting.         "agent answered -> customer's turn
              ENDIF.
          ENDCASE.
        ENDLOOP.
      ENDIF.

      APPEND VALUE #( %tky          = ticket-%tky
                      MessageCount  = REDUCE i( INIT n = 0
                                                FOR l IN all_links
                                                WHERE ( source-TicketUUID = ticket-TicketUUID )
                                                NEXT n = n + 1 )
                      LastMessageAt = now
                      Status        = new_status ) TO updates.
    ENDLOOP.

    MODIFY ENTITIES OF zrap_r_ticket_### IN LOCAL MODE
      ENTITY Ticket
        UPDATE FIELDS ( MessageCount LastMessageAt Status )
        WITH updates.
  ENDMETHOD.

ENDCLASS.
```

해설

- 이 단계의 코드는 R-02와 같은 패턴(IN LOCAL MODE, `FIELDS ( … )`, `%tky`, state message)입니다. 새로운 점은 **사이드 이펙트가 다시 읽을 값을 누가 바꾸는가**를 정리하는 것입니다.

| 사이드 이펙트 대상 | 그 값을 바꾸는 코드 |
|---|---|
| `SlaDueAt`, `SlaStatus`, `SlaCriticality` | `calcSlaDue`, `calcSlaStatus`(on save 결정이지만 determine action `recalcSla`/`refreshSla`로 draft 중에도 실행) |
| `messages` | `validateCategory`(recalcSla에 포함) |
| `permissions ( … )` | `get_instance_features`(Ticket), `%field-IsInternal`(Message) |
| `entity _Messages` | 액션 안의 `CREATE BY \_Messages`(시스템 메시지) |
| `_Ticket.MessageCount` 등 | 자식의 `updateTicketStats`가 부모를 `MODIFY`(같은 BO 안이므로 IN LOCAL MODE로 가능) |

- **on save 결정을 draft 중에 돌리는 방법**: `calcSlaDue`는 on save라서 원래는 Activate(Prepare) 때만 실행됩니다. 사이드 이펙트의 determine action(`recalcSla`)이 필드 그룹 변경 때 이것을 즉시 실행시켜 줍니다. `( always )`는 트리거 조건(`field Priority, Category`)이 맞지 않아도 실행하라는 뜻이며, `refreshSla`처럼 "아무 필드도 안 바뀌었지만 시간이 흘러 결과가 달라지는" 계산에 꼭 필요합니다.
- **updateTicketStats를 on modify로 둔 이유**: `$self affects field _Ticket.MessageCount`가 의미 있으려면 draft에서 메시지를 추가한 **그 순간** 부모 값이 바뀌어 있어야 합니다. on save라면 Activate 전까지 값이 그대로라 사이드 이펙트가 같은 옛 값을 다시 읽을 뿐입니다.
- **시스템 메시지와 기능 제어**: 액션은 IN LOCAL MODE로 자식을 만들기 때문에 `IsInternal`의 읽기 전용(기능 제어)과 무관하게 값을 넣을 수 있습니다. 외부 소비자(EML, UI)에게만 기능 제어가 적용됩니다.
- `setTicketNo`의 `MAX + 1`은 동시에 두 사람이 저장하면 같은 번호가 나올 수 있습니다. 실무에서는 번호 범위 객체를 쓰세요(R-04 3단계).
- `cl_abap_context_info=>get_user_technical_name( )`은 ABAP Cloud에서 `sy-uname` 대신 쓰는 릴리스된 API입니다.

**클래스 구조 해설**

- `FOR INSTANCE FEATURES … FOR Ticket`과 `FOR Message`는 BDEF의 `( features : instance )`가 붙은 줄(update, delete, `_Messages` create, 액션 3개, `field ( features : instance ) IsInternal`)에서 생깁니다. 결과 구조의 `%assoc-_Messages`, `%action-escalate`, `%field-IsInternal`이 각각 그 줄에 대응합니다.
- 결정 메서드는 `determination` 줄마다 하나씩, 액션 메서드는 `action` 줄마다 하나씩 생기며 `result [1] $self` 때문에 `RESULT result`가 붙습니다.
- determine action(`recalcSla`, `refreshSla`)은 메서드가 생기지 않습니다. 프레임워크가 포함된 결정·검증을 대신 호출합니다.

</details>

#### 7단계. 세이버 save_modified: 루트·자식·deep·사이드 이펙트용 이벤트 발생시키기

요구사항

1. 세이버 클래스 `lsc_zrap_r_ticket_###`(`cl_abap_behavior_saver` 상속)에서 `save_modified`와 `cleanup_finalize`를 재정의하세요.
2. `save_modified`에서 다음 순서로 이벤트를 발생시키세요.
   - `create-ticket` → `ticket_created`(키만). 파생 이벤트 `ticket_created_contact`는 **발생시키지 않습니다**(프레임워크가 함께 발생).
   - `update-ticket` 중 `%control-EscalationLevel`이 켜진 줄 → `ticket_escalated`(평면 payload) **그리고** `escalation_changed`(사이드 이펙트용, 키만).
   - `update-ticket` 중 `%control-Status`가 켜져 있고 Status가 C인 줄 → `ticket_closed`(deep payload). 메시지 목록은 `READ ENTITIES … BY \_Messages`로 읽고, **내부 메모(IsInternal)는 빼고** 넣습니다.
   - `create-message` → 자식 엔터티 이벤트 `message_posted`(`RAISE ENTITY EVENT zrap_r_tktmsg_###~message_posted`).
3. 타입은 BDEF 파생 타입 `TYPE TABLE FOR EVENT`로 선언해서 써 보세요.

**확인**

- 행동 풀이 활성화됩니다.
- 디버거로 `save_modified`에 중단점을 두고 9단계에서 Fiori로 티켓을 저장하면 중단점에 걸립니다. `create-ticket`, `create-message`, `update-ticket-%control`의 내용을 확인하세요.

<details><summary>정답·해설</summary>

```abap
CLASS lsc_zrap_r_ticket_### DEFINITION INHERITING FROM cl_abap_behavior_saver.
  PROTECTED SECTION.
    METHODS save_modified    REDEFINITION.
    METHODS cleanup_finalize REDEFINITION.
ENDCLASS.


CLASS lsc_zrap_r_ticket_### IMPLEMENTATION.

  METHOD save_modified.

    "------------------------------------------------------------------
    " 1) ticket_created: no parameter -> %key only.
    "    The derived event ticket_created_contact is raised by the framework.
    "------------------------------------------------------------------
    IF create-ticket IS NOT INITIAL.
      RAISE ENTITY EVENT zrap_r_ticket_###~ticket_created
        FROM VALUE #( FOR ticket IN create-ticket
                      ( %key-TicketUUID = ticket-TicketUUID ) ).
    ENDIF.

    IF update-ticket IS NOT INITIAL.

      "----------------------------------------------------------------
      " 2) ticket_escalated: flat parameter (abstract entity)
      "----------------------------------------------------------------
      DATA escalated TYPE TABLE FOR EVENT zrap_r_ticket_###~ticket_escalated.

      escalated = VALUE #( FOR ticket IN update-ticket
                           WHERE ( %control-EscalationLevel = if_abap_behv=>mk-on )
                           ( %key-TicketUUID = ticket-TicketUUID
                             %param          = VALUE #( ticket_no        = ticket-TicketNo
                                                        customer_id      = ticket-CustomerID
                                                        priority         = ticket-Priority
                                                        escalation_level = ticket-EscalationLevel
                                                        sla_due_at       = ticket-SlaDueAt ) ) ).

      IF escalated IS NOT INITIAL.
        RAISE ENTITY EVENT zrap_r_ticket_###~ticket_escalated FROM escalated.

        "--------------------------------------------------------------
        " 5) escalation_changed: event for side effects (keys only).
        "    Open Fiori pages reload the targets defined in 'side effects'.
        "--------------------------------------------------------------
        RAISE ENTITY EVENT zrap_r_ticket_###~escalation_changed
          FROM VALUE #( FOR esc IN escalated ( %key = esc-%key ) ).
      ENDIF.

      "----------------------------------------------------------------
      " 3) ticket_closed: deep parameter (abstract BDEF with hierarchy)
      "----------------------------------------------------------------
      DATA closed_tickets LIKE update-ticket.
      closed_tickets = VALUE #( FOR ticket IN update-ticket
                                WHERE ( %control-Status = if_abap_behv=>mk-on
                                    AND Status          = lcl_tkt=>status-closed )
                                ( ticket ) ).

      IF closed_tickets IS NOT INITIAL.
        READ ENTITIES OF zrap_r_ticket_### IN LOCAL MODE
          ENTITY Ticket BY \_Messages
            FIELDS ( MessageUUID TicketUUID AuthorType IsInternal MessageText )
            WITH VALUE #( FOR ticket IN closed_tickets
                          ( %is_draft  = if_abap_behv=>mk-off
                            TicketUUID = ticket-TicketUUID ) )
          RESULT DATA(closed_messages).

        DATA closed TYPE TABLE FOR EVENT zrap_r_ticket_###~ticket_closed.

        closed = VALUE #(
          FOR ticket IN closed_tickets
          ( %key-TicketUUID = ticket-TicketUUID
            %param          = VALUE #(
              ticket_uuid      = ticket-TicketUUID
              ticket_no        = ticket-TicketNo
              title            = ticket-Title
              customer_id      = ticket-CustomerID
              escalation_level = ticket-EscalationLevel
              message_count    = ticket-MessageCount
              closed_at        = utclong_current( )
              "composition component of the hierarchical type = internal table
              _messages        = VALUE #( FOR msg IN closed_messages
                                          WHERE ( TicketUUID = ticket-TicketUUID
                                              AND IsInternal = abap_false )
                                          ( message_uuid = msg-MessageUUID
                                            ticket_uuid  = msg-TicketUUID
                                            author_type  = msg-AuthorType
                                            message_text = msg-MessageText ) ) ) ) ).

        RAISE ENTITY EVENT zrap_r_ticket_###~ticket_closed FROM closed.
      ENDIF.

    ENDIF.

    "------------------------------------------------------------------
    " 4) message_posted: event of the CHILD entity (release 7.96+).
    "    ent~evt uses the child entity name; %key = child key.
    "------------------------------------------------------------------
    IF create-message IS NOT INITIAL.
      RAISE ENTITY EVENT zrap_r_tktmsg_###~message_posted
        FROM VALUE #( FOR msg IN create-message
                      ( %key-MessageUUID = msg-MessageUUID
                        %param           = VALUE #( ticket_uuid  = msg-TicketUUID
                                                    author_type  = msg-AuthorType
                                                    is_internal  = msg-IsInternal
                                                    message_text = msg-MessageText ) ) ).
    ENDIF.

  ENDMETHOD.


  METHOD cleanup_finalize.
  ENDMETHOD.

ENDCLASS.
```

해설

- **왜 save_modified인가**: `RAISE ENTITY EVENT`는 세이버 메서드의 late save 단계에서만 쓸 수 있고, 다른 곳에서 쓰면 런타임 오류 `BEHAVIOR_ILLEGAL_STATEMENT`가 납니다(키워드 문서 `RAISE ENTITY EVENT`). 관리형 BO에서는 `with additional save`를 붙이고 `save_modified`에서 발생시키는 것이 권장 방법입니다.
- **자식 엔터티 이벤트**: 문서상 `RAISE ENTITY EVENT ent~evt`의 `ent`는 "RAP BO 엔터티 이름"이고 루트와 자식 모두 가능합니다. 그래서 자식은 루트 BDEF 이름이 아니라 **자식 CDS 엔터티 이름** `zrap_r_tktmsg_###`를 씁니다. `%key`도 자식 키(`MessageUUID`)입니다. 부모 티켓 키는 `%key`에 없으므로 payload(`ticket_uuid`)로 넘겼습니다. 자식 엔터티 이벤트 자체는 7.96 릴리스 뉴스와 문서 문장으로 확인했고, 자식용 `RAISE`/`TABLE FOR EVENT` 형식은 같은 규칙을 적용한 것입니다(실제 시스템에서 확인 필요).
- **deep payload**: `with hierarchy` 추상 BDEF의 파생 타입은 "필드 + 컴포지션마다 컴포넌트"입니다. 컴포넌트 이름은 컴포지션 이름(`_Messages`)을 따른다고 보고 `_messages`로 채웠습니다(ABAP은 대소문자를 구분하지 않음). 컴포넌트 이름이 다르면 ADT에서 `closed`에 커서를 두고 F2로 실제 구조를 보고 맞추세요(실제 시스템에서 확인 필요).
- **내부 메모를 빼는 이유**: 이벤트는 다른 시스템(Event Mesh 구독자)까지 갈 수 있는 "공개 계약"입니다. payload에 무엇을 넣을지는 API 설계이므로 내부 정보는 처음부터 빼 둡니다.
- **`escalation_changed`를 따로 두는 이유**: 사이드 이펙트용 이벤트는 문서상 event-driven side effect **전용**입니다. 같은 사실을 로컬 소비자/외부에 알리는 것은 `ticket_escalated`가 맡고, 화면 갱신 신호는 `escalation_changed`가 맡습니다.
- **파생 이벤트를 발생시키지 않는 이유**: `managed event … on ticket_created`는 참조 이벤트가 발생하면 프레임워크가 payload 뷰를 키로 읽어 **자동으로** 발생시킵니다. 코드에서 `RAISE ENTITY EVENT … ticket_created_contact`를 쓰지 않습니다.
- `READ ENTITIES` in `save_modified`: late save에서 트랜잭션 버퍼를 읽는 것은 허용됩니다(데이터 변경·`MODIFY`는 불가). 방금 Activate로 만들어진 메시지도 버퍼에서 함께 읽힙니다.
- 이벤트는 저장(커밋)이 성공해야 소비자에게 전달됩니다. 이후 단계에서 저장이 실패하면 소비자 메서드는 호출되지 않습니다.

**클래스 구조 해설**

- `create`, `update`, `delete`는 `save_modified`의 import 파라미터(`TYPE REQUEST FOR CHANGE` / `REQUEST FOR DELETE`)이고, 컴포넌트 이름이 엔터티 별칭(`ticket`, `message`)입니다. `with full data` 때문에 `update-ticket`에 바뀌지 않은 필드도 들어 있고, `%control`로 실제로 바뀐 필드를 구별합니다.
- `TYPE TABLE FOR EVENT <엔터티>~<이벤트>`는 BDEF의 `event … [deep] parameter …` 줄에서 생기는 파생 타입입니다. 파라미터가 없으면 `%key`만, 있으면 `%key` + `%param`이 있습니다.

</details>

#### 8단계. 프로젝션·인터페이스 BDEF와 서비스: `use side effects`, `use event`

요구사항

1. 프로젝션 BDEF `ZRAP_C_TICKET_###`:
   - 헤더에 `use draft;`와 **`use side effects;`**.
   - Ticket: 표준 연산, 액션 3개, **determine action 2개(`recalcSla`, `refreshSla`)**, draft 액션 5개, `_Messages` 생성, 그리고 사이드 이펙트용 이벤트 **`use event escalation_changed;`**.
   - Message: update, `_Ticket` 연관.
2. 인터페이스 BDEF `ZRAP_I_TICKET_###`:
   - 헤더에 `use draft;`, `use side effects;`.
   - Ticket: 프로젝션과 같은 연산 + 이벤트 4개(`ticket_created`, `ticket_escalated`, `ticket_closed`, `escalation_changed`)를 `use event`로 재사용.
   - Message: `use event message_posted;`.
3. 서비스 정의 `ZRAP_UI_TICKET_###`(Ticket, Message, 고객 값 도움말 노출), 서비스 바인딩 `ZRAP_UI_TICKET_O4_###`(OData V4 - UI) 만들고 Publish.

**직접 추가할 어노테이션**

- (SRVD) `@EndUserText.label` — 서비스 설명

**확인**

- 서비스 바인딩에서 Ticket을 선택하고 Preview를 엽니다. 목록이 비어 있고 Create 버튼이 보입니다.
- 서비스 바인딩 화면의 Service URL을 브라우저에서 열고 끝에 `$metadata`를 붙여 보세요. 사이드 이펙트는 OData 메타데이터의 어노테이션으로 번역되므로 `SideEffects`라는 단어가 여러 번 나와야 합니다(`Common.SideEffects` 형식, 실제 문자열은 시스템에서 확인 필요).
- 프로젝션 BDEF에서 `use event ticket_closed;`를 시험 삼아 추가하면 활성화 오류가 나는지 확인하고 지우세요(아래 해설).

<details><summary>정답·해설</summary>

```bdef
projection;
strict ( 2 );
use draft;
use side effects;             // 기본 BO의 사이드 이펙트를 전부 재사용(프로젝션에 없는 필드/액션 것은 자동으로 빠짐)

define behavior for ZRAP_C_TICKET_### alias Ticket
use etag
{
  use create;
  use update;
  use delete;

  use action escalate;
  use action closeTicket;
  use action reopenTicket;
  use action recalcSla;       // 사이드 이펙트가 호출하는 determine action도 노출해야 UI가 호출 가능
  use action refreshSla;

  use action Edit;
  use action Activate;
  use action Discard;
  use action Resume;
  use action Prepare;

  use association _Messages { create; with draft; }

  use event escalation_changed;   // "for side effects" 이벤트만 프로젝션에서 재사용 가능
}

define behavior for ZRAP_C_TKTMSG_### alias Message
use etag
{
  use update;

  use association _Ticket { with draft; }
}
```

```bdef
interface;
use draft;
use side effects;             // 인터페이스는 재사용만 가능(새 사이드 이펙트 정의 불가)

define behavior for ZRAP_I_TICKET_### alias Ticket
use etag
{
  use create;
  use update;
  use delete;

  use action escalate;
  use action closeTicket;
  use action reopenTicket;
  use action recalcSla;
  use action refreshSla;

  use action Edit;
  use action Activate;
  use action Discard;
  use action Resume;
  use action Prepare;

  use association _Messages { create; with draft; }

  use event ticket_created;       // 일반 이벤트: 인터페이스 BDEF에서만 재사용 가능 (7.93)
  use event ticket_escalated;
  use event ticket_closed;
  use event escalation_changed;
}

define behavior for ZRAP_I_TKTMSG_### alias Message
use etag
{
  use update;

  use association _Ticket { with draft; }

  use event message_posted;       // 자식 엔터티 이벤트 재사용
}
```

```cds
@EndUserText.label: 'Support ticket UI service'               // (→ 어노테이션 탭: @EndUserText.label)
define service ZRAP_UI_TICKET_### {
  expose ZRAP_C_TICKET_###     as Ticket;
  expose ZRAP_C_TKTMSG_###     as Message;
  expose /DMO/I_Customer_StdVH as Customer;
}
```

해설

- **`use side effects`**: 헤더에 한 번 쓰면 기본 BO의 모든 엔터티 사이드 이펙트가 재사용됩니다. 프로젝션에 노출되지 않은 필드·액션을 쓰는 사이드 이펙트는 자동으로 걸러집니다. 그래서 `recalcSla`, `refreshSla`를 `use action`으로 노출하지 않으면 해당 사이드 이펙트가 조용히 사라집니다(Flight Reference Scenario의 `/DMO/C_Travel_D_D`가 `use action validateDateRange;` 등을 노출하는 이유).
- 프로젝션 BDEF는 사이드 이펙트를 **재사용**할 뿐 아니라 **새로 정의**할 수도 있습니다(RAP110 `ZRAP110_C_TRAVELTP_SOL`의 Booking이 프로젝션에서 `side effects { field BookingDate affects field DaysToFlightIndicator … }`를 정의). 인터페이스 BDEF는 재사용만 됩니다(문서 RAP - `use`).
- **이벤트 재사용 규칙**(문서 RAP - `use`, RAP - `event`):

| 이벤트 종류 | 인터페이스 BDEF | 프로젝션 BDEF |
|---|---|---|
| 일반 이벤트(`event X [parameter …]`) | `use event X [as Alias]`, 파라미터 재정의 가능 | **불가** |
| 사이드 이펙트용(`event X for side effects`) | `use event X [as Alias]` | `use event X [as Alias]` |
| 파생 이벤트(`managed event`) | 문서에서 확인하지 못함(실제 시스템에서 확인 필요) | 불가로 추정 |

- 인터페이스 BDEF에서 이벤트를 재사용하면, 이벤트 핸들러 클래스를 인터페이스 기준(`FOR EVENTS OF zrap_i_ticket_###`, 메서드 `FOR zrap_i_ticket_###~ticket_closed`)으로 만들 수 있습니다. 이때 `%key`/`%param`은 인터페이스 BDEF 기준입니다(문서 `METHODS, FOR ENTITY EVENT`). 다른 개발팀·다른 소프트웨어 컴포넌트가 이 BO의 이벤트를 받을 때는 내부 R 계층 대신 이 안정된 인터페이스를 쓰게 하는 것이 목적입니다. 이 문제 10단계는 같은 패키지 안이라 R 계층에 직접 붙입니다.
- `$metadata`에서 사이드 이펙트를 확인하는 습관을 들이세요. 화면에서 아무 일도 안 일어날 때, 메타데이터에 없으면 BDEF/프로젝션 문제이고, 있으면 UI(캐시·UI5 버전) 문제입니다.

</details>

#### 9단계. Fiori에서 사이드 이펙트 다섯 가지를 직접 확인하기

요구사항

아래 표의 순서대로 Preview에서 조작하고, "보여야 하는 결과"를 확인하세요. 결과가 다르면 오른쪽 열을 점검합니다.

| # | 조작 | 관련 BDEF 줄 | 보여야 하는 결과 |
|---|---|---|---|
| 1 | Create → Title `Printer jam`, Customer 아무나, Category `HW` 입력 | `setInitialValues`(on modify) | 저장 전인데도 Priority `M`, Status `N`, Opened At이 채워짐(생성 응답에 포함) |
| 2 | Priority를 `U`로 바꾸고 **Category 칸으로 이동**(아직 반응 없음) → Category를 `XX`로 바꾸고 **두 필드 밖(Title)으로 이동** | `determine action recalcSla executed on field Priority, field Category affects …, messages` | 이때 한 번만 서버 호출: SLA Due가 접수 시각 + 4시간으로, SLA 신호등이 초록(G)으로 바뀌고, Category 칸이 빨갛게 되며 메시지 003이 즉시 뜸. Category를 `HW`로 고치고 밖으로 나가면 메시지가 사라짐 |
| 3 | Messages 표에서 + (Create) → 줄이 생김 | `$self affects field _Ticket.MessageCount, …` | 헤더 SLA 묶음의 Messages가 1, Last Message 시각이 채워짐 |
| 4 | 새 줄의 Author를 `C`로, 본문 입력 | `$self affects … _Ticket.Status`, `field AuthorType affects permissions ( field IsInternal )` | 헤더 Status가 `P`로 바뀜. Internal 체크박스는 읽기 전용 |
| 5 | 메시지를 하나 더 추가해 Author를 `A`로 | 같은 줄 | Internal 체크박스가 **편집 가능**으로 바뀜. Status가 `W`로 바뀜. Internal을 체크하면 Status는 그대로 |
| 6 | Save | `setTicketNo`, `calcSlaDue/Status`, 이벤트 | Ticket No가 채워짐(활성화 시 on save 결정) |
| 7 | 표시 화면에서 Escalate 세 번 | `action escalate affects permissions ( action escalate ), messages` + `result [1] $self` | 매번 Priority·Level·SLA가 바뀌고 성공 메시지 004. 세 번째 후 Escalate 버튼이 **바로** 회색. 시스템 메시지 줄은 F5를 해야 보임(escalate에는 `entity _Messages`를 지정하지 않았음 — 일부러 비교용) |
| 8 | Close | `action closeTicket affects entity _Messages, permissions ( … ), messages` | "Ticket closed by …" 줄이 **즉시** 표에 나타남. Close·Escalate·Edit 관련 버튼이 비활성, Reopen이 활성 |
| 9 | Reopen | 같은 형태 | "Ticket reopened" 줄이 즉시 나타나고 버튼 상태가 반대로 돌아감 |

**확인**

- 위 9개 행이 모두 표대로 보이면 이 단계 완료입니다.
- 7번에서 escalate 후 시스템 메시지가 즉시 보이지 않는 것을 확인하고, BDEF의 escalate 줄에 `entity _Messages,`를 추가·재활성화한 뒤 다시 해 보면 즉시 보입니다. 대상 하나 차이로 화면이 달라지는 것을 직접 비교하는 것이 목적입니다.

<details><summary>정답·해설</summary>

정답 코드는 5~8단계에 모두 있습니다. 이 단계는 결과 해석이 핵심입니다.

- **2번(필드 그룹)**: 문서에 따르면 determine action의 소스로 필드를 여러 개 쓰면 "필드 그룹"이 되어, 그룹 안에서 커서가 움직이는 동안은 실행되지 않고 **그룹 밖으로 나갈 때** 실행됩니다. 단일 필드 사이드 이펙트(`field A affects field B`)는 필드마다 즉시 실행되는 것과 다릅니다. 연관된 두 값을 함께 고칠 때 서버 왕복을 줄이는 기능입니다.
- **2번의 메시지**: `affects messages`가 없으면 `validateCategory`가 실행되어도 Fiori는 메시지를 다시 읽지 않아 저장 때까지 오류를 모릅니다. 메시지와 함께 `%element-Category`가 켜져 있으므로 칸이 빨갛게 표시됩니다.
- **3~5번(`$self`)**: 트리거 `$self`는 "이 엔터티(Message)에 생성·변경·삭제가 일어날 때"입니다. 메시지 줄을 만들거나 Author를 바꾸는 것은 모두 Message의 update이므로, 부모 티켓의 세 필드가 다시 읽힙니다. 값 자체는 6단계 `updateTicketStats`(on modify)가 바꿉니다.
- **4~5번(permissions(field))**: `IsInternal`의 편집 가능 여부는 `get_instance_features`의 `%field-IsInternal`이 정합니다. 사이드 이펙트가 없으면 Author를 바꿔도 체크박스 상태는 처음 읽은 그대로입니다.
- **7번 vs 8번(`entity _Messages`)**: 둘 다 자식 줄을 만드는 액션이지만 `entity _Messages`를 지정한 Close만 표가 즉시 갱신됩니다. 액션 결과(`result [1] $self`)는 **자기 인스턴스**만 돌려주므로 자식 표 갱신은 사이드 이펙트로 따로 알려야 합니다.
- **8번(permissions 목록)**: 닫힘 상태가 되면 `get_instance_features` 결과가 여러 개 바뀝니다. `permissions ( action escalate, action closeTicket, action reopenTicket, update, create _Messages )`로 다섯 가지를 한 번에 다시 읽게 했습니다. `create _Messages`가 없으면 표의 + 버튼이 그대로 활성으로 남아 눌렀을 때 오류가 납니다.
- 사이드 이펙트는 **draft 화면**(편집 모드)에서 가장 잘 보입니다. 표시 모드의 액션 후에도 동작하지만, 필드 트리거는 편집 중에만 의미가 있습니다.

**자주 나는 문제와 해결**

- 아무 사이드 이펙트도 동작하지 않음 → 프로젝션 BDEF `use side effects;` 누락, 또는 브라우저 캐시. Preview를 새로 열고 Ctrl+F5.
- 2번에서 SLA는 바뀌는데 메시지가 안 뜸 → `recalcSla`에 `validation validateCategory;`가 있는지, 프로젝션에 `use action recalcSla;`가 있는지 확인.
- 3번에서 Messages가 안 바뀜 → `updateTicketStats`를 on save로 만들었거나, 프로젝션 Message에 `use update`가 빠져 Author 변경이 안 되는 경우.

</details>

#### 10단계. 로컬 이벤트 소비자: 파생·deep·자식 이벤트 받기, EML로 자동 에스컬레이션, 재시도

요구사항

1. 재시도 예외 클래스 `ZCX_RAP_TKT_RETRY_###`를 만드세요. 상위 클래스는 `CX_RAP_EVENT_HDLR_ERROR_RETRY`, 생성자는 `delay_time`(초, 정수)과 `previous`를 받아 상위 생성자에 넘깁니다.
2. 이벤트 핸들러 클래스 `ZCL_RAP_TKT_EVT_###`(전역 클래스 정의에 `FOR EVENTS OF zrap_r_ticket_###`)를 만들고, Local Types에 `cl_abap_behavior_event_handler`를 상속한 `lhe_ticket`을 만드세요. 메서드:
   - `on_ticket_created`(`ticket_created`): 새 티켓을 EML로 읽어 **제목에 `URGENT`가 있고 단계가 0이면 `escalate` 액션을 EML로 실행**합니다. 실행 결과 `failed`의 원인이 잠금(locked/conflict)이면 `ZCX_RAP_TKT_RETRY_###`(30초 뒤 재시도)를 발생시킵니다. 성공하면 `cl_abap_tx=>save( )`로 저장 단계로 넘어가고(`CX_ABAP_BEHV_SAVE_FAILED`는 잡아서 60초 뒤 재시도), 로그를 남깁니다.
   - `on_created_contact`(파생 이벤트 `ticket_created_contact`): payload의 티켓 번호·이름·이메일을 로그에 남깁니다.
   - `on_info_events`: **메서드 하나로 두 이벤트**(`ticket_escalated`, `ticket_closed`)를 받습니다. deep payload의 메시지 표 줄 수도 로그에 남깁니다.
   - `on_message_posted`(자식 이벤트 `message_posted`): 작성자와 본문을 로그에 남깁니다.
3. 로그 줄 만들기는 도우미 메서드 `new_log_line`으로 공통화하세요.

**확인** (11단계 콘솔 클래스나 Fiori에서 티켓을 만든 뒤)

- 몇 초 뒤 `ZRAP_TKTEVL_###` Data Preview(F8)에 `TICKET_CREATED`, `TICKET_CREATED_CONTACT`, `MESSAGE_POSTED` 줄이 생깁니다. `TICKET_CREATED_CONTACT` 줄의 info에 고객 이름과 이메일이 있으면 **파생 이벤트가 프레임워크에 의해 발생**한 것입니다(코드 어디에도 RAISE가 없음).
- 제목에 `URGENT`가 들어간 티켓은 잠시 뒤 Priority가 한 단계 오르고 Escalation Level 1, 시스템 메시지 "Escalated to level 1"이 생기며, 로그에 `TICKET_ESCALATED`와 그 시스템 메시지의 `MESSAGE_POSTED`가 이어서 생깁니다(이벤트 → 소비자 → 수정 → 새 이벤트의 연쇄).
- 티켓을 닫으면 `TICKET_CLOSED` 줄(공개 메시지 수 포함)과 메시지별 `TICKET_CLOSED_MSG` 줄이 생깁니다. 내부 메모는 나오지 않습니다.

<details><summary>정답·해설</summary>

재시도 예외 클래스:

```abap
CLASS zcx_rap_tkt_retry_### DEFINITION
  PUBLIC
  INHERITING FROM cx_rap_event_hdlr_error_retry   " framework retries the event handler (max. 3 attempts)
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    METHODS constructor
      IMPORTING
        delay_time TYPE i OPTIONAL                  " seconds until the next attempt
        previous   LIKE previous OPTIONAL.

  PROTECTED SECTION.
  PRIVATE SECTION.
ENDCLASS.


CLASS zcx_rap_tkt_retry_### IMPLEMENTATION.

  METHOD constructor ##ADT_SUPPRESS_GENERATION.
    super->constructor( delay_time = delay_time
                        previous   = previous ).
  ENDMETHOD.

ENDCLASS.
```

이벤트 핸들러 클래스(Global Class 탭):

```abap
CLASS zcl_rap_tkt_evt_### DEFINITION
  PUBLIC
  ABSTRACT
  FINAL
  FOR EVENTS OF zrap_r_ticket_###.   " RAP event handler class of the ticket BO

  PUBLIC SECTION.
  PROTECTED SECTION.
  PRIVATE SECTION.
ENDCLASS.


CLASS zcl_rap_tkt_evt_### IMPLEMENTATION.
ENDCLASS.
```

Local Types 탭:

```abap
CLASS lhe_ticket DEFINITION INHERITING FROM cl_abap_behavior_event_handler.

  PRIVATE SECTION.

    TYPES tt_log TYPE STANDARD TABLE OF zrap_tktevl_### WITH EMPTY KEY.

    "root event without parameter
    METHODS on_ticket_created FOR ENTITY EVENT
      created FOR Ticket~ticket_created.

    "derived event (payload = view entity ZRAP_P_TKT_CONTACT_###)
    METHODS on_created_contact FOR ENTITY EVENT
      contact FOR Ticket~ticket_created_contact.

    "one handler method for two events (flat + deep parameter)
    METHODS on_info_events FOR ENTITY EVENT
      escalated FOR Ticket~ticket_escalated
      closed    FOR Ticket~ticket_closed.

    "event of the child entity
    METHODS on_message_posted FOR ENTITY EVENT
      posted FOR Message~message_posted.

    METHODS new_log_line
      IMPORTING event_name   TYPE zrap_tktevl_###-event_name
                ticket_uuid  TYPE sysuuid_x16
                message_uuid TYPE sysuuid_x16 OPTIONAL
                info         TYPE csequence OPTIONAL
      RETURNING VALUE(line)  TYPE zrap_tktevl_###.

ENDCLASS.


CLASS lhe_ticket IMPLEMENTATION.

  METHOD on_ticket_created.

    "--- 1) modify phase: read the new (active) tickets ------------------
    READ ENTITIES OF zrap_r_ticket_###
      ENTITY Ticket
        FIELDS ( TicketNo Title EscalationLevel )
        WITH VALUE #( FOR evt IN created
                      ( %is_draft  = if_abap_behv=>mk-off
                        TicketUUID = evt-%key-TicketUUID ) )
      RESULT DATA(tickets).

    "--- 2) auto-escalate urgent tickets with EML -----------------------
    DATA escalate_keys TYPE TABLE FOR ACTION IMPORT zrap_r_ticket_###~escalate.

    LOOP AT tickets INTO DATA(ticket).
      IF to_upper( ticket-Title ) CS 'URGENT' AND ticket-EscalationLevel = 0.
        APPEND VALUE #( %tky = ticket-%tky ) TO escalate_keys.
      ENDIF.
    ENDLOOP.

    IF escalate_keys IS NOT INITIAL.
      MODIFY ENTITIES OF zrap_r_ticket_###
        ENTITY Ticket
          EXECUTE escalate FROM escalate_keys
        FAILED DATA(failed).

      "temporary problem (instance locked, e.g. a user is editing it in a draft)
      "-> raising a retry exception rolls back and lets the framework try again later
      LOOP AT failed-ticket INTO DATA(fail)
           WHERE %fail-cause = if_abap_behv=>cause-locked
              OR %fail-cause = if_abap_behv=>cause-conflict.
        RAISE EXCEPTION NEW zcx_rap_tkt_retry_###( delay_time = 30 ).
      ENDLOOP.
    ENDIF.

    "--- 3) switch to the save phase: runs the RAP save sequence -------
    "        (COMMIT ENTITIES is not allowed in an event handler)
    TRY.
        cl_abap_tx=>save( ).
      CATCH cx_abap_behv_save_failed INTO DATA(save_failed).
        RAISE EXCEPTION NEW zcx_rap_tkt_retry_###( delay_time = 60
                                                   previous   = save_failed ).
    ENDTRY.

    "--- 4) database changes are allowed only now -----------------------
    DATA log TYPE tt_log.
    LOOP AT created INTO DATA(evt).
      APPEND new_log_line(
               event_name  = 'TICKET_CREATED'
               ticket_uuid = evt-%key-TicketUUID
               info        = COND string( WHEN line_exists( escalate_keys[ TicketUUID = evt-%key-TicketUUID ] )
                                          THEN `auto-escalated (URGENT in title)`
                                          ELSE `no action` ) ) TO log.
    ENDLOOP.

    DELETE log WHERE log_uuid IS INITIAL.
    IF log IS NOT INITIAL.
      INSERT zrap_tktevl_### FROM TABLE @log.
    ENDIF.

  ENDMETHOD.


  METHOD on_created_contact.
    cl_abap_tx=>save( ).

    DATA(log) = VALUE tt_log(
      FOR evt IN contact
      ( new_log_line( event_name  = 'TICKET_CREATED_CONTACT'
                      ticket_uuid = evt-%key-TicketUUID
                      info        = |{ evt-%param-TicketNo } { evt-%param-FirstName } { evt-%param-LastName } <{ evt-%param-EMailAddress }>| ) ) ).

    DELETE log WHERE log_uuid IS INITIAL.
    IF log IS NOT INITIAL.
      INSERT zrap_tktevl_### FROM TABLE @log.
    ENDIF.
  ENDMETHOD.


  METHOD on_info_events.
    "Only the table of the event that was actually raised is filled.
    cl_abap_tx=>save( ).

    DATA log TYPE tt_log.

    LOOP AT escalated INTO DATA(esc).
      APPEND new_log_line(
               event_name  = 'TICKET_ESCALATED'
               ticket_uuid = esc-%key-TicketUUID
               info        = |{ esc-%param-ticket_no }: level { esc-%param-escalation_level }, priority { esc-%param-priority }, due { esc-%param-sla_due_at }| ) TO log.
    ENDLOOP.

    LOOP AT closed INTO DATA(cls).
      "deep parameter: header fields + table of messages
      APPEND new_log_line(
               event_name  = 'TICKET_CLOSED'
               ticket_uuid = cls-%key-TicketUUID
               info        = |{ cls-%param-ticket_no } closed, { lines( cls-%param-_messages ) } public messages| ) TO log.

      LOOP AT cls-%param-_messages INTO DATA(msg).
        APPEND new_log_line(
                 event_name   = 'TICKET_CLOSED_MSG'
                 ticket_uuid  = cls-%key-TicketUUID
                 message_uuid = msg-message_uuid
                 info         = |{ msg-author_type }: { msg-message_text }| ) TO log.
      ENDLOOP.
    ENDLOOP.

    DELETE log WHERE log_uuid IS INITIAL.
    IF log IS NOT INITIAL.
      INSERT zrap_tktevl_### FROM TABLE @log.
    ENDIF.
  ENDMETHOD.


  METHOD on_message_posted.
    cl_abap_tx=>save( ).

    DATA(log) = VALUE tt_log(
      FOR evt IN posted
      ( new_log_line( event_name   = 'MESSAGE_POSTED'
                      ticket_uuid  = evt-%param-ticket_uuid
                      message_uuid = evt-%key-MessageUUID
                      info         = |{ evt-%param-author_type }{ COND string( WHEN evt-%param-is_internal = abap_true THEN ` (internal)` ) }: { evt-%param-message_text }| ) ) ).

    DELETE log WHERE log_uuid IS INITIAL.
    IF log IS NOT INITIAL.
      INSERT zrap_tktevl_### FROM TABLE @log.
    ENDIF.
  ENDMETHOD.


  METHOD new_log_line.
    TRY.
        line = VALUE #( log_uuid     = cl_system_uuid=>create_uuid_x16_static( )
                        event_name   = event_name
                        ticket_uuid  = ticket_uuid
                        message_uuid = message_uuid
                        info         = info
                        received_at  = utclong_current( ) ).
      CATCH cx_uuid_error.
        CLEAR line.   "line without key is removed by the caller
    ENDTRY.
  ENDMETHOD.

ENDCLASS.
```

해설

- **이벤트 핸들러 메서드 규칙**(문서 `METHODS, FOR ENTITY EVENT`): 로컬 클래스의 PRIVATE 영역에 인스턴스 메서드로 정의, 파라미터는 `TYPE TABLE FOR EVENT`(이름은 자유), 응답 파라미터(failed/reported) 없음. **한 메서드가 여러 이벤트를 받을 수 있고**(`on_info_events`), 한 핸들러 클래스 안에서 같은 이벤트를 두 번 받을 수는 없습니다. `ent`에는 엔터티(여기서는 별칭 `Ticket`, `Message`)나 인터페이스 BDEF를 씁니다. 자식 엔터티 이벤트(`Message~message_posted`)도 같은 형식입니다(실제 시스템에서 확인 필요).
- **트랜잭션 단계**: 핸들러는 원래 트랜잭션이 커밋된 뒤, 자기만의 RAP 트랜잭션에서 **modify(인터랙션) 단계**로 시작합니다. EML `READ`/`MODIFY`는 바로 쓸 수 있지만, DB 변경(INSERT)이나 BO 저장은 `cl_abap_tx=>save( )`로 save 단계로 바꾼 다음에만 됩니다. `COMMIT ENTITIES`/`COMMIT WORK`는 쓰지 않습니다. `cl_abap_tx=>save( )`가 RAP 저장 시퀀스를 실행하므로 `escalate`로 바꾼 내용이 이 호출에서 저장되고, 그 저장의 `save_modified`가 다시 `ticket_escalated`·`escalation_changed`를 발생시킵니다.
- **`CX_ABAP_BEHV_SAVE_FAILED`**: 저장 시퀀스(early/late save)에서 실패하면 이 예외가 납니다. 문서는 이 예외를 잡아 로그를 남기거나, `CX_ABAP_BEHV_EVENT_HDLR_ERROR`(재시도 없음) 계열 사용자 예외로 바꿔 이벤트 프레임워크에 보고하라고 권합니다. 핸들러 밖으로 나갈 수 있는 예외는 이 계열뿐입니다.
- **재시도(9.16)**: 문서(`METHODS, FOR ENTITY EVENT`)와 릴리스 뉴스에 따르면 로컬 이벤트가 잠금 같은 일시적 문제로 실패할 때 프레임워크가 **최대 3번** 다시 실행합니다. 구현은 `CX_RAP_EVENT_HDLR_ERROR_RETRY`를 상속한 예외를 발생시키는 것이고, 생성자 파라미터 `delay_time`(정수, 초)으로 다음 시도까지의 간격을 정합니다. 재시도가 필요 없는 오류는 `CX_RAP_EVENT_HDLR_ERROR` 상속 예외를 씁니다. 예외를 발생시키면 그때까지의 변경은 암묵적으로 롤백됩니다. 상위 클래스 생성자의 정확한 시그니처(다른 필수 파라미터 유무)와 이 클래스가 ABAP Cloud에 릴리스되었는지는 확인하지 못했습니다. `super->constructor`에서 오류가 나면 상위 클래스를 F2로 열어 시그니처를 맞추세요(실제 시스템에서 확인 필요).
- **잠금 원인**: draft BO에서는 누군가 티켓을 Edit으로 열면 활성 인스턴스가 잠깁니다. 이때 EML로 활성 인스턴스에 액션을 실행하면 `failed`에 잠금 원인이 들어옵니다. draft가 있을 때 원인 값이 `locked`인지 `conflict`인지 확실하지 않아 둘 다 검사했습니다(실제 시스템에서 확인 필요).
- **IN LOCAL MODE를 쓰지 않는 이유**: 이벤트 핸들러는 BO의 "소비자"입니다. 행동 풀 밖이므로 `IN LOCAL MODE`를 쓸 수 없고, 쓸 수 있더라도 권한·기능 제어(닫힌 티켓 에스컬레이션 금지)를 그대로 지키는 편이 안전합니다.
- **파생 이벤트 받기**: `ticket_created_contact`의 payload(`%param-FirstName` 등)는 프레임워크가 `ZRAP_P_TKT_CONTACT_###`를 PRIVILEGED로 읽어 채웁니다. 파생 이벤트의 원래 목적은 이벤트 바인딩(원격 소비)에 다른 payload를 주는 것인데, 로컬 핸들러에서도 받을 수 있는지는 문서에서 명시적으로 확인하지 못했습니다(실제 시스템에서 확인 필요). 활성화 오류가 나면 이 메서드만 지우고 진행하세요.
- 문자열 템플릿 안의 COND는 결과 타입을 추론할 곳이 없으므로 `COND string( … )`처럼 타입을 적어야 합니다. ELSE가 없으면 조건이 거짓일 때 빈 문자열이 됩니다.

**클래스 구조 해설**

- `FOR EVENTS OF zrap_r_ticket_###`가 붙은 전역 클래스는 "이벤트 핸들러 클래스 풀"이고, 실제 메서드는 CCIMP(Local Types)의 `cl_abap_behavior_event_handler` 하위 클래스에 둡니다(행동 풀의 `FOR BEHAVIOR OF` + `lhc_*`와 같은 구조). 로컬 클래스는 암묵적으로 ABSTRACT·FINAL입니다.
- 파라미터 이름 `created`, `contact`, `escalated`, `closed`, `posted`는 자유롭게 정한 이름이고, 타입은 각 BDEF `event` 줄에서 생기는 `TABLE FOR EVENT`입니다.
- 호출 시점: 원래 트랜잭션의 커밋 성공 후 **비동기**. 원래 트랜잭션이 롤백되면 호출되지 않습니다. 같은 이벤트를 여러 핸들러 클래스가 받을 수 있지만, 그 사이 순서는 보장되지 않는다고 생각하세요.

</details>

#### 11단계. 이벤트 기반 사이드 이펙트와 전역 사이드 이펙트를 화면으로 확인하고, EML 콘솔로 이벤트 연쇄 확인하기

요구사항

1. 콘솔 클래스 `ZCL_RAP_TKT_TEST_###`(`if_oo_adt_classrun`)를 만드세요.
   - 실행하면 먼저 **이전 실행에서 받은 이벤트 로그**(최근 30줄)를 출력합니다(이벤트는 비동기라 같은 실행 안에서는 아직 안 보일 수 있음).
   - 이어서 EML로 활성 티켓 두 개를 만듭니다. T1: 제목 `URGENT: VPN down`(Category SW, Priority H) + 고객 메시지 1개. T2: 제목 `Password reset`(Category AC, Priority L) + 고객 메시지 1개 + 상담원 내부 메모 1개. `COMMIT ENTITIES`.
   - 두 번째 트랜잭션에서 T2에 `closeTicket`을 실행하고 `COMMIT ENTITIES`.
   - 만든 티켓 번호와 실패 여부를 출력합니다.
2. **이벤트 기반 사이드 이펙트** 확인(Fiori):
   - Preview에서 새 티켓을 만들고 Title에 `URGENT printer`를 넣어 **Save**합니다. 표시 화면에 그대로 머무르세요.
   - 몇 초 안에 새로 고침 없이 Priority가 한 단계 오르고, Escalation Level 1, SLA 값, Messages 표의 "Escalated to level 1" 줄이 나타나는지 봅니다.
3. **재시도** 확인: 2번을 다시 하되, Save 직후 **바로 Edit**을 눌러 draft를 만든 채 40초쯤 기다렸다가 Save합니다. 로그에 `TICKET_CREATED`가 늦게 생기고 에스컬레이션이 결국 반영되는지 확인합니다.
4. **전역 사이드 이펙트** 확인: 티켓 하나를 열어 둔 채(SLA 초록), 행동 풀 `lcl_tkt=>sla_light`의 `7200`을 `999999`로 바꿔 활성화합니다. 화면에서 아무 필드도 바꾸지 말고 전역 사이드 이펙트 단축키를 눌러 SLA가 노란색(Y)으로 바뀌는지 봅니다. 확인 뒤 `7200`으로 되돌리세요.

**확인**

- 콘솔을 두 번 실행합니다. 두 번째 실행의 앞부분 로그에 다음이 보이면 성공입니다: `TICKET_CREATED`(T1은 auto-escalated), `TICKET_CREATED_CONTACT` ×2, `MESSAGE_POSTED`(고객 메시지 2, 내부 메모 1, 시스템 메시지 "Ticket closed…" 1, "Escalated to level 1" 1), `TICKET_ESCALATED`(T1, level 1, priority U), `TICKET_CLOSED`(T2, public messages 2) + `TICKET_CLOSED_MSG` ×2.
- 2번에서 화면이 저절로 바뀌지 않으면 F5를 눌러 값이 바뀌어 있는지 봅니다. F5 후에만 보이면 백엔드(이벤트·소비자·저장)는 정상이고, 이벤트 기반 사이드 이펙트의 UI 쪽 지원 문제입니다(해설 참고).

<details><summary>정답·해설</summary>

```abap
CLASS zcl_rap_tkt_test_### DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_oo_adt_classrun.

  PRIVATE SECTION.
    METHODS show_log
      IMPORTING out TYPE REF TO if_oo_adt_classrun_out.
ENDCLASS.


CLASS zcl_rap_tkt_test_### IMPLEMENTATION.

  METHOD if_oo_adt_classrun~main.

    "--- A) events received since the previous run (asynchronous!) -----
    show_log( out ).

    "--- B) transaction 1: create two active tickets with messages -----
    SELECT SINGLE FROM /DMO/I_Customer
      FIELDS CustomerID
      INTO @DATA(customer_id).

    MODIFY ENTITIES OF zrap_r_ticket_###
      ENTITY Ticket
        CREATE FIELDS ( Title CustomerID Category Priority )
        WITH VALUE #( ( %cid       = 'T1'
                        %is_draft  = if_abap_behv=>mk-off
                        Title      = 'URGENT: VPN down'
                        CustomerID = customer_id
                        Category   = 'SW'
                        Priority   = 'H' )
                      ( %cid       = 'T2'
                        %is_draft  = if_abap_behv=>mk-off
                        Title      = 'Password reset'
                        CustomerID = customer_id
                        Category   = 'AC'
                        Priority   = 'L' ) )
        CREATE BY \_Messages
        FIELDS ( MessageText AuthorType IsInternal )
        WITH VALUE #( ( %cid_ref  = 'T1'
                        %is_draft = if_abap_behv=>mk-off
                        %target   = VALUE #( ( %cid        = 'M1'
                                               %is_draft   = if_abap_behv=>mk-off
                                               MessageText = 'Nobody can connect to the VPN.'
                                               AuthorType  = 'C'
                                               IsInternal  = abap_false ) ) )
                      ( %cid_ref  = 'T2'
                        %is_draft = if_abap_behv=>mk-off
                        %target   = VALUE #( ( %cid        = 'M2'
                                               %is_draft   = if_abap_behv=>mk-off
                                               MessageText = 'Please reset my password.'
                                               AuthorType  = 'C'
                                               IsInternal  = abap_false )
                                             ( %cid        = 'M3'
                                               %is_draft   = if_abap_behv=>mk-off
                                               MessageText = 'Identity checked by phone.'
                                               AuthorType  = 'A'
                                               IsInternal  = abap_true ) ) ) )
      MAPPED DATA(mapped)
      FAILED DATA(failed)
      REPORTED DATA(reported).

    IF failed IS NOT INITIAL.
      out->write( |Create failed: { lines( failed-ticket ) } ticket(s), { lines( failed-message ) } message(s)| ).
      ROLLBACK ENTITIES.
      RETURN.
    ENDIF.

    COMMIT ENTITIES
      RESPONSE OF zrap_r_ticket_###
      FAILED DATA(commit_failed)
      REPORTED DATA(commit_reported).

    IF commit_failed IS NOT INITIAL.
      out->write( |Commit failed (validation?) - { lines( commit_failed-ticket ) } ticket(s)| ).
      RETURN.
    ENDIF.

    DATA(t1_uuid) = mapped-ticket[ %cid = 'T1' ]-TicketUUID.
    DATA(t2_uuid) = mapped-ticket[ %cid = 'T2' ]-TicketUUID.

    "--- C) transaction 2: close T2 -> ticket_closed (deep) ------------
    MODIFY ENTITIES OF zrap_r_ticket_###
      ENTITY Ticket
        EXECUTE closeTicket
        FROM VALUE #( ( %is_draft  = if_abap_behv=>mk-off
                        TicketUUID = t2_uuid ) )
      FAILED DATA(close_failed).

    IF close_failed IS INITIAL.
      COMMIT ENTITIES.
    ELSE.
      ROLLBACK ENTITIES.
      out->write( 'Close failed' ).
    ENDIF.

    "--- D) what was saved -----------------------------------------------
    READ ENTITIES OF zrap_r_ticket_###
      ENTITY Ticket
        FIELDS ( TicketNo Title Priority Status EscalationLevel MessageCount )
        WITH VALUE #( ( %is_draft = if_abap_behv=>mk-off TicketUUID = t1_uuid )
                      ( %is_draft = if_abap_behv=>mk-off TicketUUID = t2_uuid ) )
      RESULT DATA(tickets).

    out->write( |--- tickets just saved (escalation of T1 follows asynchronously) ---| ).
    LOOP AT tickets INTO DATA(ticket).
      out->write( |{ ticket-TicketNo } { ticket-Title }: priority { ticket-Priority }, status { ticket-Status }, | &&
                  |level { ticket-EscalationLevel }, messages { ticket-MessageCount }| ).
    ENDLOOP.
    out->write( `Run the class again in a few seconds to see the received events.` ).

  ENDMETHOD.


  METHOD show_log.
    SELECT FROM zrap_tktevl_###
      FIELDS received_at, event_name, info
      ORDER BY received_at DESCENDING
      INTO TABLE @DATA(log)
      UP TO 30 ROWS.

    out->write( |--- last { lines( log ) } received events ---| ).
    out->write( log ).
  ENDMETHOD.

ENDCLASS.
```

예상 콘솔 출력(두 번째 실행 앞부분, 순서·시각은 다를 수 있음):

```
--- last 12 received events ---
RECEIVED_AT                  EVENT_NAME              INFO
2026-10-17 09:15:07.1234567  TICKET_ESCALATED        0000000001: level 1, priority U, due ...
2026-10-17 09:15:06.9876543  MESSAGE_POSTED          S (internal): Escalated to level 1
2026-10-17 09:15:05.5555555  TICKET_CLOSED           0000000002 closed, 2 public messages
2026-10-17 09:15:05.5555000  TICKET_CLOSED_MSG       C: Please reset my password.
2026-10-17 09:15:05.5554000  TICKET_CLOSED_MSG       S: Ticket closed by CB0000000123
2026-10-17 09:15:05.4444444  MESSAGE_POSTED          S: Ticket closed by CB0000000123
2026-10-17 09:15:04.3333333  TICKET_CREATED          auto-escalated (URGENT in title)
2026-10-17 09:15:04.2222222  TICKET_CREATED          no action
2026-10-17 09:15:04.1111111  TICKET_CREATED_CONTACT  0000000001 <FirstName> <LastName> <<EMailAddress>>
...
```

**이벤트 기반 사이드 이펙트 해설**

- 흐름: Fiori Save → 커밋 → `ticket_created` → (비동기) `on_ticket_created`가 EML로 `escalate` → `cl_abap_tx=>save( )` → `save_modified`가 `escalation_changed` 발생 → 서버가 이 이벤트를 알리고, 해당 티켓을 보고 있는 Fiori 화면이 BDEF의 `event escalation_changed affects …` 대상(Priority, Level, SLA, 메시지 표)을 다시 읽습니다.
- 일반 사이드 이펙트와의 차이: 트리거가 **이 화면의 사용자 동작이 아니라 서버의 이벤트**입니다. 그래서 다른 사용자, 백그라운드 작업(예: 애플리케이션 잡, bgPF), 이벤트 소비자가 바꾼 데이터도 열려 있는 화면에 반영할 수 있습니다.
- **정직한 한계**: 서버에서 브라우저로 알림을 밀어 주려면 Fiori Elements 쪽 지원(푸시 채널)이 필요합니다. ADT 서비스 바인딩 Preview가 이 기능을 지원하는지, 어떤 UI5 버전부터인지 이번에 읽은 자료에서는 확인하지 못했습니다(실제 시스템에서 확인 필요). 화면이 저절로 바뀌지 않아도 F5 뒤 값이 바뀌어 있으면 BDEF/ABAP 쪽은 맞게 만든 것입니다. 프로젝션 BDEF의 `use event escalation_changed;`가 이 화면 알림에 필요한지도 확인하지 못했습니다(문서는 "재사용 가능"까지만 말함).

**재시도 해설**

- Save 직후 Edit을 누르면 활성 티켓이 draft로 잠깁니다. 그 사이에 소비자가 `escalate`를 실행하면 실패(잠금) → `ZCX_RAP_TKT_RETRY_###( delay_time = 30 )` → 30초 뒤 다시 시도(최대 3번). 세 번 안에 Save나 Discard로 잠금이 풀리면 에스컬레이션이 성공하고, 로그의 `TICKET_CREATED` 수신 시각이 다른 줄보다 늦습니다.
- 세 번 모두 실패하면 이벤트 처리는 포기됩니다(AIF 로깅이 켜져 있으면 기록, 문서 기준). 비즈니스상 반드시 처리해야 한다면 "미처리 티켓을 다시 찾는" 주기 작업을 따로 두는 것이 안전합니다.
- 이벤트가 비동기로 언제 처리되는지는 시스템 부하에 따라 다릅니다. Save 직후 Edit이 소비자보다 늦으면 잠금이 안 생겨 재시도가 일어나지 않습니다. 몇 번 시도해 보세요.

**전역 사이드 이펙트 해설**

- SLA 신호등은 **입력이 바뀌지 않아도 시간이 흐르면** 바뀌는 값입니다. 필드 트리거로는 다시 계산할 계기가 없습니다. `determine action refreshSla executed on global affects …`는 사용자가 전용 키 입력으로 "전역 새로 고침"을 요청하면 determine action(`calcSlaStatus` 강제 실행)을 돌리고 지정 필드를 다시 읽습니다(릴리스 9.18 뉴스 문장).
- 4번 실습에서는 시간이 흐르는 대신 **임계값(코드)을 바꿔** 같은 효과를 냅니다. 화면에서 아무것도 바꾸지 않았는데 단축키 한 번으로 G → Y가 되면, 서버 계산이 다시 실행되었다는 증거입니다.
- 어느 키 조합이 "전용 단축키"인지는 이번에 읽은 자료에 없습니다. SAP Fiori Elements 문서(사이드 이펙트/전역 사이드 이펙트)에서 확인하세요(실제 시스템에서 확인 필요). `executed on global`이 활성화 오류면 시스템 릴리스가 9.18 미만입니다.

</details>

#### 12단계. 원격 소비 개념: 이벤트 바인딩, SAP Event Mesh, 트라이얼에서 가능한 것

요구사항

1. 원격 소비 흐름을 그림(글)로 정리하세요: BDEF `event` → `RAISE ENTITY EVENT` → **이벤트 바인딩**(BDEF 이벤트 ↔ 외부 이벤트 유형) → 통신 설정(채널 바인딩) → SAP Event Mesh → 구독자(다른 시스템).
2. `ticket_closed`에 대한 이벤트 바인딩 `ZRAP_EVB_TKT_CLOSED_###`를 ADT에서 만들어 보세요(만들 수 있는 경우).
   - Namespace `zrap###`, Business Object `Ticket`, Business Object Operation `Closed`.
   - Events: Minor version 1, Patch version 0, Root Entity Name `ZRAP_R_TICKET_###`, Entity Event Name `TICKET_CLOSED`.
3. 아래 질문에 답하세요.
   - 파생 이벤트(`ticket_created_contact`)는 원격 소비에서 어떤 의미가 있나?
   - 사이드 이펙트용 이벤트(`escalation_changed`)를 바인딩해야 하나?
   - 자식 엔터티 이벤트(`message_posted`)는 바인딩 편집기에서 어떻게 지정하나?

**확인**

- 이벤트 바인딩이 활성화되면 편집기의 Type 칸에 `zrap###.Ticket.Closed.v1` 같은 이름이 생깁니다.
- 트라이얼에서 메뉴가 없거나 활성화가 막히면 그 사실을 적어 두고 개념 정리만 하세요.

<details><summary>정답·해설</summary>

```
[ZRAP_R_TICKET_### BDEF]  event ticket_closed deep parameter ...
        │  save_modified: RAISE ENTITY EVENT
        ▼
[로컬 소비]  FOR EVENTS OF 클래스 (10단계)  ← 이벤트 바인딩 없이 동작
        │
[원격 소비]  이벤트 바인딩 ZRAP_EVB_TKT_CLOSED_###
        │      Type = <namespace>.<business object>.<operation>.v<major>
        ▼
   Enterprise Event Enablement 채널 바인딩(Outbound Topic = 위 Type)
        ▼
   SAP Event Mesh  ──►  구독자(다른 BTP 앱, S/4HANA, CAP 서비스 등)
```

- **이벤트 바인딩**(ADT: 패키지 → New → Other ABAP Repository Object → Business Services → Event Binding): BDEF 이벤트를 외부 이벤트 유형(namespace, 비즈니스 객체, 작업, 버전)에 연결하는 설계 객체입니다. RAP110 ex11b에 따르면 편집기에는 General Information(Namespace, Business Object, Business Object Operation)과 Events(Minor/Patch Version, Root Entity Name, Entity Event Name)가 있고, Type은 `namespace.businessobject.operation.v*` 형태로 자동 생성됩니다. 문서(RAP - `event`)도 "이벤트를 만들고 발생시킨 뒤에는 이벤트 유형에 매핑하는 이벤트 바인딩을 정의해야 한다"고 말합니다. 단, 이것은 **원격 소비**에 필요한 것이고, 10단계 같은 로컬 소비는 바인딩 없이 동작합니다(RAP110 ex11은 로컬 소비만 구현).
- **채널 설정과 Event Mesh**: RAP110 ex11b는 SAP BTP Cockpit에서 SAP Event Mesh 인스턴스를 구성하고, ABAP 환경에 아웃바운드 통신 약정을 만든 뒤, Fiori 앱 "Enterprise Event Enablement - Configure Channel Binding"에서 채널에 Outbound Topic(바인딩의 Type)을 추가하고, "Enterprise Event Enablement - Event Monitor" 앱에서 보낸 이벤트와 payload를 확인하는 순서를 설명합니다. 그 핸즈온에서도 이 구성은 SAP 팀이 미리 해 두었고, TechEd 2023 버전에서는 이 연습을 **하지 말라**고 적어 두었습니다.
- **트라이얼에서 가능한 것(정직하게)**: 이벤트 정의·발생·로컬 소비(1~11단계)는 트라이얼에서 할 수 있어야 합니다. 이벤트 바인딩 객체 생성·활성화는 설계 시점 작업이라 시도해 볼 수 있지만 가능 여부는 확인하지 못했습니다. Event Mesh 인스턴스, 통신 약정, 채널 바인딩은 BTP 하위 계정과 ABAP 환경의 **관리자 권한**이 필요하고 트라이얼은 여러 사람이 공유하는 시스템이라, 개인이 끝까지 구성하기는 어렵다고 보는 것이 현실적입니다(실제 시스템에서 확인 필요). 원격 소비를 끝까지 해 보려면 관리자 권한이 있는 BTP 하위 계정(유료/무료 티어)의 ABAP 환경이 필요합니다.
- **질문 답**
  - 파생 이벤트: 같은 사건(`ticket_created`)에 대해 **구독자마다 다른 payload**(예: 고객 연락처만)를 주고 싶을 때 씁니다. 원래 이벤트의 payload를 바꾸면 기존 구독자 계약이 깨지므로, 파생 이벤트를 따로 만들어 별도 바인딩/유형으로 내보냅니다. payload는 PRIVILEGED로 읽히므로 넣을 필드를 신중히 고릅니다. 확장(BDEF extension)에서 원래 BO를 바꾸지 않고 파생 이벤트를 추가할 수 있다는 점도 큰 장점입니다(Flight Reference Scenario의 Agency 확장 `/DMO/AgencyReviewCreatedCntct`).
  - 사이드 이펙트용 이벤트: 문서상 event-driven side effect **전용**이므로 외부 구독자용 바인딩 대상이 아닙니다. 같은 사실을 외부에 알리려면 `ticket_escalated` 같은 일반 이벤트를 바인딩합니다.
  - 자식 엔터티 이벤트: RAP110의 편집기 설명에는 "Root Entity Name"과 "Entity Event Name"만 나옵니다. 자식 엔터티 이벤트를 지정하는 칸이 따로 있는지(예: 엔터티 이름 칸)는 7.96 이후 편집기에서 확인해야 합니다(실제 시스템에서 확인 필요).

</details>

## 출처
- SAP-samples/abap-cheat-sheets
  - https://github.com/SAP-samples/abap-cheat-sheets/blob/main/36_RAP_Behavior_Definition_Language.md
  - https://github.com/SAP-samples/abap-cheat-sheets/blob/main/08_EML_ABAP_for_RAP.md
  - https://github.com/SAP-samples/abap-cheat-sheets/blob/main/33_ABAP_Release_News.md
  - https://github.com/SAP-samples/abap-cheat-sheets/blob/main/src/zdemo_abap_rap_ro_m_as.bdef.asbdef
  - https://github.com/SAP-samples/abap-cheat-sheets/blob/main/src/zbp_demo_abap_rap_ro_m_as.clas.locals_imp.abap
  - https://github.com/SAP-samples/abap-cheat-sheets/blob/main/src/zcl_demo_abap_rap_evt_handler.clas.abap
  - https://github.com/SAP-samples/abap-cheat-sheets/blob/main/src/zcl_demo_abap_rap_evt_handler.clas.locals_imp.abap
  - https://github.com/SAP-samples/abap-cheat-sheets/blob/rap/README.md
  - https://github.com/SAP-samples/abap-cheat-sheets/blob/rap/src/zr_demo_abap96.bdef.asbdef
- SAP-samples/abap-platform-rap110
  - https://github.com/SAP-samples/abap-platform-rap110/blob/main/exercises/ex11/README.md
  - https://github.com/SAP-samples/abap-platform-rap110/blob/main/exercises/ex11b/README.md
  - https://github.com/SAP-samples/abap-platform-rap110/blob/main/src/zrap110_r_traveltp_sol.bdef.asbdef
  - https://github.com/SAP-samples/abap-platform-rap110/blob/main/src/zrap110_c_traveltp_sol.bdef.asbdef
- SAP-samples/abap-platform-refscen-flight (ABAP-platform-cloud 브랜치)
  - https://github.com/SAP-samples/abap-platform-refscen-flight/blob/ABAP-platform-cloud/src/reuse/agency/rev/%23dmo%23zz_x_review_r_agencytp.bdef.asbdef
  - https://github.com/SAP-samples/abap-platform-refscen-flight/blob/ABAP-platform-cloud/src/reuse/agency/rev/%23dmo%23zz_bp_x_review_r_agencytp.clas.locals_imp.abap
  - https://github.com/SAP-samples/abap-platform-refscen-flight/blob/ABAP-platform-cloud/src/reuse/agency/rev/d/%23dmo%23zz_x_rev_cntct_r_agencytp.bdef.asbdef
  - https://github.com/SAP-samples/abap-platform-refscen-flight/blob/ABAP-platform-cloud/src/reuse/agency/rev/d/%23dmo%23zz_p_agencyreview_contact.ddls.asddls
  - https://github.com/SAP-samples/abap-platform-refscen-flight/blob/ABAP-platform-cloud/src/reuse/agency/rev/e/%23dmo%23zz_d_agencyreviewcreated.ddls.asddls
  - https://github.com/SAP-samples/abap-platform-refscen-flight/blob/ABAP-platform-cloud/src/reuse/agency/%23dmo%23i_agencytp.bdef.asbdef
  - https://github.com/SAP-samples/abap-platform-refscen-flight/blob/ABAP-platform-cloud/src/draft/%23dmo%23r_travel_d.bdef.asbdef
  - https://github.com/SAP-samples/abap-platform-refscen-flight/blob/ABAP-platform-cloud/src/draft/%23dmo%23c_travel_d_d.bdef.asbdef
  - https://github.com/SAP-samples/abap-platform-refscen-flight/blob/ABAP-platform-cloud/src/xbo/%23dmo%23r_traveltp_xbo.bdef.asbdef
  - https://github.com/SAP-samples/abap-platform-refscen-flight/blob/ABAP-platform-cloud/src/hierarchy/draft/%23dmo%23r_agencytp_hd.bdef.asbdef
  - https://github.com/SAP-samples/abap-platform-refscen-flight/blob/ABAP-platform-cloud/src/legacy/%23dmo%23i_customer.ddls.asddls
- SAP-samples/abap-platform-fiori-feature-showcase (ABAP-platform-cloud 브랜치)
  - https://github.com/SAP-samples/abap-platform-fiori-feature-showcase/blob/ABAP-platform-cloud/src/%23dmo%23fsa_r_roottp.bdef.asbdef
  - https://github.com/SAP-samples/abap-platform-fiori-feature-showcase/blob/ABAP-platform-cloud/src/%23dmo%23fsa_c_roottp.bdef.asbdef
  - https://github.com/SAP-samples/abap-platform-fiori-feature-showcase/blob/ABAP-platform-cloud/src/%23dmo%23fsa_d_overwritetimezonep.bdef.asbdef
  - https://github.com/SAP-samples/abap-platform-fiori-feature-showcase/blob/ABAP-platform-cloud/src/%23dmo%23fsa_d_overwritetimezonep.ddls.asddls
- ABAP 키워드 문서(ABAP Cloud)의 Markdown 미러 marianfoo/abap-docs (각 파일의 원본은 help.sap.com ABAP Keyword Documentation)
  - https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABENBDL_EVENT.md
  - https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABENBDL_EVENT_OVERVIEW.md
  - https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABENBDL_MANAGED_EVENT.md
  - https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABENBDL_EVENT_SIDE_EFFECT.md
  - https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABENBDL_SIDE_EFFECTS.md
  - https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABENBDL_SIDE_EFFECTS_TARGET.md
  - https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABENBDL_USE_PROJECTION.md
  - https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABENBDL_DETERMINE_ACTION.md
  - https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABENBDL_BDEF_ABSTRACT_HEADER.md
  - https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABENBDL_DEFINE_BEH_ABSTRACT.md
  - https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABENBDL_ASSOCIATION_ABSTRACT.md
  - https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABENCDS_ABSENT_COMPOSITION.md
  - https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABENCDS_ABSENT_TO_PARENT_ASSOC.md
  - https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABAPRAISE_ENTITY_EVENT.md
  - https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABENMETHOD_FOR_ENTITY_EVENT.md
  - https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABENCL_ABAP_BEHAVIOR_EVENT_HANDLER.md
  - https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABENRAP_DERIVED_EVENT_GLOSRY.md
  - https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABENRAP_EVENT_SIDEEF_GLOSRY.md
  - https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABENNEWS-796-CDS_BDL.md
  - https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABENNEWS-914-CDS_BDL.md
  - https://github.com/marianfoo/abap-docs/blob/main/docs/cloud/md/ABENNEWS-916-EML.md
