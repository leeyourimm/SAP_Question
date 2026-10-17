## 2. 비관리형(Unmanaged) BO

이 단원은 RAP에서 가장 손이 많이 가는 구현 방식인 **unmanaged**를 처음부터 끝까지 직접 만듭니다. managed BO에서는 프레임워크가 해 주던 일(트랜잭션 버퍼, CRUD, 잠금, ETag 값 채우기, 키 번호 매기기, DB 저장)을 **전부 여러분의 코드가** 해야 합니다. 그래서 unmanaged를 끝까지 구현해 보면 "RAP 프레임워크가 managed에서 뒤에서 무엇을 하고 있었는지"가 그대로 보입니다.

세 문제는 이어집니다.

| 문제 | 무엇을 만드나 | 핵심 |
|---|---|---|
| R-05 | RAP과 무관한 "레거시" 구매 주문 애플리케이션 (Z 테이블 + 자체 버퍼를 가진 Z 클래스) | 레거시 API의 계약: 메시지 테이블, X(제어) 구조, 액션 코드, 임시 번호, 번호 매핑, 저장/초기화 |
| R-06 | 레거시를 감싸는 unmanaged RAP BO (non-draft, late numbering) | 핸들러 메서드 전부, 세이버 메서드 전부, mapped/failed/reported, %cid/%cid_ref/%pid/%tmp |
| R-07 | 같은 레거시를 감싸는 unmanaged + draft BO, 그리고 behavior pool 단위 테스트 | draft일 때 프레임워크가 어떤 핸들러를 부르는지, early numbering, 테스트 대역(test double) 주입 |

> 이 단원은 공식 예제 **ABAP Flight Reference Scenario의 `/DMO/I_Travel_U`**(레거시 함수 모듈 `/DMO/FLIGHT_TRAVEL_*`와 클래스 `/DMO/CL_FLIGHT_LEGACY`를 감싸는 unmanaged BO)의 구조를 그대로 따릅니다. 다만 BTP ABAP 환경(ABAP for Cloud Development)에서는 함수 모듈을 새로 만들 수 없고 BAPI도 쓸 수 없으므로, "레거시"를 **직접 작성한 Z 클래스**로 흉내 냅니다.

### R-05. 레거시 주문 애플리케이션 만들기 (RAP으로 감쌀 대상) [작성] ★★★
<!-- covers: unmanaged 준비, 레거시 API 설계, 데이터 엘리먼트, 도메인, DB 테이블, 금액/수량 참조, DDIC 구조(제어 구조), 메시지 클래스, 잠금 객체, cl_abap_lock_object_factory, 번호 범위 객체, cl_numberrange_runtime, cl_numberrange_intervals, 트랜잭션 버퍼, early/late/external numbering, 임시 번호, adjust_numbers 매핑, X 구조, 액션 코드, 전부 아니면 전무(all-or-nothing), 상태 전이, save/initialize, ABAP Unit, cl_osql_test_environment, LOCAL FRIENDS -->
**목표**

- unmanaged RAP BO가 "감싸는 대상"인 레거시 애플리케이션이 어떤 계약(API 모양)을 가져야 하는지 설명할 수 있습니다.
- 자체 트랜잭션 버퍼(생성/변경/삭제 표시)를 가진 싱글턴 클래스를 작성하고, 저장 전까지는 DB를 건드리지 않게 만들 수 있습니다.
- early / late / external 세 가지 번호 매기기 방식과 임시 번호(preliminary number) → 최종 번호 매핑을 직접 구현할 수 있습니다.
- X(제어) 구조와 액션 코드(C/U/D)로 "어떤 필드를 바꿀지, 어떤 하위 행을 만들고 지울지"를 전달하는 레거시 API 패턴을 구현할 수 있습니다.
- 잠금 객체와 번호 범위 객체를 ADT에서 만들고 클라우드 릴리스 API(`cl_abap_lock_object_factory`, `cl_numberrange_runtime`)로 사용할 수 있습니다.
- `cl_osql_test_environment`로 DB를 대역으로 바꾼 ABAP Unit 테스트를 작성할 수 있습니다.

**전제**

- 패키지 `ZRAP_###`가 있고 ADT에서 ABAP Cloud 프로젝트로 접속되어 있습니다.
- 표준 데모 데이터 `/DMO/AGENCY`(공급업체 마스터로 재사용), `/DMO/SUPPLEMENT`(제품 마스터로 재사용)가 채워져 있습니다. 비어 있으면 ADT에서 `/DMO/CL_FLIGHT_DATA_GENERATOR`를 F9(Run As > ABAP Application (Console))로 한 번 실행하세요.
- 이 문제는 RAP 객체를 하나도 만들지 않습니다. **RAP을 모르는 옛날 개발자가 만든 프로그램**이라고 생각하고 작성하세요. RAP은 R-06에서 이것을 "감쌉니다".

**만들 객체**

| 순서 | 객체 유형 | 이름 | 역할 |
|---|---|---|---|
| 1 | 도메인 / 데이터 엘리먼트 | `ZLEG_ORDER_ID_###` | 주문 번호(NUMC 10). 번호 범위 객체의 길이 도메인으로도 사용 |
| 2 | DB 테이블 | `ZLEG_ORDH_###` | 주문 헤더 |
| 3 | DB 테이블 | `ZLEG_ORDI_###` | 주문 품목 |
| 4 | DDIC 구조 | `ZLEG_S_ORDH_X_###` | 헤더 변경 플래그(제어 구조). R-06 BDEF의 `mapping ... control`에서 재사용 |
| 5 | DDIC 구조 | `ZLEG_S_ORDI_X_###` | 품목 변경 플래그(제어 구조) |
| 6 | 메시지 클래스 | `ZLEG_MSG_###` | 레거시 메시지 |
| 7 | 잠금 객체 | `EZLEG_ORD_###` | 주문 단위 배타 잠금 |
| 8 | 번호 범위 객체 | `ZLEGORD###` | 주문 번호 채번 |
| 9 | 인터페이스 | `ZIF_LEG_ORDER_###` | 레거시 API: 타입, 상수, 메서드 시그니처 |
| 10 | 클래스 | `ZCL_LEG_ORDER_###` | 레거시 API 구현 (싱글턴 + 자체 버퍼) + 테스트 클래스 |
| 11 | 클래스 | `ZCL_LEG_ORDER_SETUP_###` | 번호 범위 구간 초기화 + 데모 데이터 생성 콘솔 |

#### 1단계. 주문 번호 도메인과 데이터 엘리먼트 만들기

요구사항

1. 도메인 `ZLEG_ORDER_ID_###`를 만드세요. (ADT: 패키지 우클릭 > New > Other ABAP Repository Object > Dictionary > Domain)
   - 데이터 타입 `NUMC`, 길이 `10`, 설명 "Legacy order ID ###".
   - 출력 길이 10, 대소문자 구분 없음, 값 범위 없음.
2. 같은 이름의 데이터 엘리먼트 `ZLEG_ORDER_ID_###`를 만들고 도메인 `ZLEG_ORDER_ID_###`를 지정하세요.
   - 필드 라벨: Short `Order`, Medium `Order ID`, Long `Purchase Order ID`, Heading `Order ID`.
3. 왜 내장 타입 `abap.numc(10)`이 아니라 도메인까지 만드는지 한 줄로 적어 보세요. (힌트: 8단계의 번호 범위 객체)

**확인** 두 객체가 활성화되고, 데이터 엘리먼트의 F2(Element Info)에 NUMC 10과 라벨이 보입니다.

<details><summary>정답·해설</summary>

ADT의 도메인/데이터 엘리먼트 편집기는 폼(form) 편집기입니다. 입력값은 다음과 같습니다.

| 객체 | 항목 | 값 |
|---|---|---|
| 도메인 `ZLEG_ORDER_ID_###` | Description | Legacy order ID ### |
| | Data Type | NUMC |
| | Length | 10 |
| | Output Length | 10 |
| 데이터 엘리먼트 `ZLEG_ORDER_ID_###` | Description | Legacy order ID ### |
| | Category | Domain → `ZLEG_ORDER_ID_###` |
| | Field Labels | Short(10) `Order` / Medium(20) `Order ID` / Long(40) `Purchase Order ID` / Heading(55) `Order ID` |

왜 이렇게 쓰나

- **번호 범위 객체(Number Range Object)는 "번호 길이 도메인"을 반드시 요구**합니다. 공식 예제 `/DMO/TRAVL` 번호 범위 객체도 도메인 `/DMO/TRAVEL_ID`를 길이 도메인으로 씁니다. 내장 타입만으로는 번호 범위 객체를 만들 수 없습니다.
- 데이터 엘리먼트의 필드 라벨은 이후 CDS 뷰와 Fiori 화면에 그대로 전파됩니다. 그래서 R-06에서 `@EndUserText.label`을 주문 번호에 따로 달 필요가 없습니다.
- NUMC는 숫자만 담는 문자형입니다. 앞자리 0이 채워진 `0000000042` 형태로 저장되며 화면에는 `ALPHA = OUT` 변환으로 `42`처럼 보여 줄 수 있습니다.

</details>

#### 2단계. 레거시 DB 테이블 두 개 만들기

요구사항

1. 헤더 테이블 `ZLEG_ORDH_###`를 아래 필드 표대로 만드세요.

| 필드 | 키 | 데이터 엘리먼트(또는 내장 타입) | 타입 | 길이 | 소수 | 설명 |
|---|---|---|---|---|---|---|
| client | ✔ | `abap.clnt` | CLNT | 3 | 0 | 클라이언트 |
| order_id | ✔ | `zleg_order_id_###` | NUMC | 10 | 0 | 주문 번호 |
| requester |  | `abap.char(40)` | CHAR | 40 | 0 | 요청자 이름(자유 입력) |
| supplier_id |  | `/dmo/agency_id` | NUMC | 6 | 0 | 공급업체(= /DMO 여행사 마스터 재사용) |
| order_date |  | `abap.dats` | DATS | 8 | 0 | 주문일 |
| delivery_date |  | `abap.dats` | DATS | 8 | 0 | 희망 납기일 |
| total_amount |  | `/dmo/total_price` | CURR | 16 | 2 | 총액 (참조: currency_code) |
| currency_code |  | `/dmo/currency_code` | CUKY | 5 | 0 | 통화 |
| status |  | `abap.char(1)` | CHAR | 1 | 0 | 상태 N 신규 / A 승인 / R 반려 / C 완료 |
| note |  | `abap.char(255)` | CHAR | 255 | 0 | 메모 |
| created_by |  | `abp_creation_user` | CHAR | 12 | 0 | 생성자 |
| created_at |  | `abp_creation_tstmpl` | DEC | 21 | 7 | 생성 시각 |
| last_changed_by |  | `abp_locinst_lastchange_user` | CHAR | 12 | 0 | 최종 변경자 |
| local_last_changed_at |  | `abp_locinst_lastchange_tstmpl` | DEC | 21 | 7 | 인스턴스 최종 변경 시각 (R-06의 ETag) |
| last_changed_at |  | `abp_lastchange_tstmpl` | DEC | 21 | 7 | 최종 변경 시각 (R-07의 total ETag) |

2. 품목 테이블 `ZLEG_ORDI_###`를 아래 필드 표대로 만드세요.

| 필드 | 키 | 데이터 엘리먼트(또는 내장 타입) | 타입 | 길이 | 소수 | 설명 |
|---|---|---|---|---|---|---|
| client | ✔ | `abap.clnt` | CLNT | 3 | 0 | 클라이언트 |
| order_id | ✔ | `zleg_order_id_###` | NUMC | 10 | 0 | 주문 번호 |
| item_no | ✔ | `abap.numc(4)` | NUMC | 4 | 0 | 품목 번호 (10, 20, 30 …) |
| product_id |  | `/dmo/supplement_id` | CHAR | 10 | 0 | 제품(= /DMO 부가서비스 마스터 재사용) |
| item_text |  | `abap.char(40)` | CHAR | 40 | 0 | 품목 설명 |
| quantity |  | `abap.quan(13,3)` | QUAN | 13 | 3 | 수량 (참조: quantity_unit) |
| quantity_unit |  | `abap.unit(3)` | UNIT | 3 | 0 | 수량 단위 |
| unit_price |  | `abap.curr(15,2)` | CURR | 15 | 2 | 단가 (참조: currency_code) |
| item_amount |  | `abap.curr(15,2)` | CURR | 15 | 2 | 품목 금액 = 수량 × 단가 (참조: currency_code) |
| currency_code |  | `/dmo/currency_code` | CUKY | 5 | 0 | 통화 (헤더 통화를 따름) |

3. 두 테이블 모두 Delivery Class `A`, 데이터 유지 `RESTRICTED`, 확장 불가로 만드세요.
4. 금액 필드에는 통화 참조, 수량 필드에는 단위 참조 어노테이션을 반드시 다세요.

**직접 추가할 어노테이션**

- `@EndUserText.label` — 테이블 설명.
- `@AbapCatalog.enhancement.category` — 이 테이블을 고객/파트너가 필드 추가로 확장할 수 있는지.
- `@AbapCatalog.tableCategory` — 투명 테이블인지.
- `@AbapCatalog.deliveryClass` — 어떤 종류의 데이터(애플리케이션 데이터 등)를 담는지.
- `@AbapCatalog.dataMaintenance` — 데이터 미리보기/유지보수 도구에서 직접 편집을 허용할지.
- `@Semantics.amount.currencyCode` — 금액 필드가 어느 통화 필드를 따르는지.
- `@Semantics.quantity.unitOfMeasure` — 수량 필드가 어느 단위 필드를 따르는지.

**확인** 두 테이블이 활성화됩니다. 테이블 편집기에서 F8(Data Preview)를 누르면 빈 테이블이 열립니다.

<details><summary>정답·해설</summary>

```cds
@EndUserText.label : 'Legacy purchase order header ###'
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE   // 확장 불가
@AbapCatalog.tableCategory : #TRANSPARENT             // 투명 테이블
@AbapCatalog.deliveryClass : #A                       // 애플리케이션 데이터
@AbapCatalog.dataMaintenance : #RESTRICTED            // 데이터 미리보기에서 편집 제한
define table zleg_ordh_### {
  key client            : abap.clnt not null;
  key order_id          : zleg_order_id_### not null;
  requester             : abap.char(40);
  supplier_id           : /dmo/agency_id;
  order_date            : abap.dats;
  delivery_date         : abap.dats;
  @Semantics.amount.currencyCode : 'zleg_ordh_###.currency_code'   // 총액의 통화 참조
  total_amount          : /dmo/total_price;
  currency_code         : /dmo/currency_code;
  status                : abap.char(1);
  note                  : abap.char(255);
  created_by            : abp_creation_user;
  created_at            : abp_creation_tstmpl;
  last_changed_by       : abp_locinst_lastchange_user;
  local_last_changed_at : abp_locinst_lastchange_tstmpl;
  last_changed_at       : abp_lastchange_tstmpl;
}
```

```cds
@EndUserText.label : 'Legacy purchase order item ###'
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table zleg_ordi_### {
  key client        : abap.clnt not null;
  key order_id      : zleg_order_id_### not null;
  key item_no       : abap.numc(4) not null;
  product_id        : /dmo/supplement_id;
  item_text         : abap.char(40);
  @Semantics.quantity.unitOfMeasure : 'zleg_ordi_###.quantity_unit'   // 수량의 단위 참조
  quantity          : abap.quan(13,3);
  quantity_unit     : abap.unit(3);
  @Semantics.amount.currencyCode : 'zleg_ordi_###.currency_code'      // 단가의 통화 참조
  unit_price        : abap.curr(15,2);
  @Semantics.amount.currencyCode : 'zleg_ordi_###.currency_code'      // 품목 금액의 통화 참조
  item_amount       : abap.curr(15,2);
  currency_code     : /dmo/currency_code;
}
```

왜 이렇게 쓰나

- **unmanaged에서는 테이블 필드 이름과 CDS 요소 이름이 달라도 됩니다.** 다만 그 차이를 R-06 BDEF의 `mapping for` 블록에서 직접 연결해야 합니다. 공식 예제 `/dmo/travel`도 `lastchangedat`, `description`처럼 CDS 이름(`LastChangedAt`, `Memo`)과 다른 필드 이름을 씁니다.
- 관리 필드는 `abp_*` 데이터 엘리먼트를 쓰지만, **unmanaged에서는 프레임워크가 이 값을 채워 주지 않습니다.** 누가, 언제 채우는지가 바로 이 문제의 레거시 클래스가 해야 할 일입니다(7~9단계).
- `local_last_changed_at`과 `last_changed_at`을 둘 다 두는 이유: R-06에서는 `etag master`로 앞의 것을, R-07(draft)에서는 `total etag`로 뒤의 것을 씁니다. 치트시트 BDL 문서도 "`total etag`와 `etag master`에는 서로 다른 필드를 쓰는 것을 권장"한다고 적고 있습니다.
- 품목의 `currency_code`는 헤더 통화를 그대로 따르게 레거시가 맞춰 줍니다(9단계 `determine_totals`). 금액 필드는 같은 테이블 안의 통화 필드만 참조할 수 있기 때문에 품목 테이블에도 통화 필드가 필요합니다.

자주 나는 오류와 해결

- 금액/수량 필드에 참조 어노테이션을 빠뜨리면 활성화 시 "참조 필드가 없다"는 오류가 납니다. 참조 문자열은 `'테이블명.필드명'` 형식이며 소문자로 써도 됩니다.

</details>

#### 3단계. 제어(X) 구조 두 개 만들기

요구사항

레거시 API는 "변경할 값"과 함께 "어떤 필드를 실제로 바꾸라는 것인지"를 알려 주는 **플래그 구조**(BAPI에서 흔히 보는 `...X` 구조)를 받습니다. 이 구조는 R-06 BDEF의 `mapping for zleg_ordh_### control zleg_s_ordh_x_###`에서도 그대로 재사용됩니다.

1. ADT에서 New > Other ABAP Repository Object > Dictionary > **Structure** 로 `ZLEG_S_ORDH_X_###`를 만드세요. 필드: `requester`, `supplier_id`, `order_date`, `delivery_date`, `currency_code`, `note`. 모든 필드의 타입은 데이터 엘리먼트 `xsdboolean`.
2. 같은 방법으로 `ZLEG_S_ORDI_X_###`를 만드세요. 필드: `product_id`, `item_text`, `quantity`, `quantity_unit`, `unit_price`. 타입은 모두 `xsdboolean`.
3. 필드 이름은 **DB 테이블의 필드 이름과 정확히 같아야** 합니다. 왜 그런지 생각해 보세요.
4. 상태(`status`), 총액(`total_amount`), 관리 필드는 플래그 구조에 넣지 마세요. 이 값들은 호출자가 직접 바꾸지 못하고 레거시가 계산합니다.

**직접 추가할 어노테이션**

- `@EndUserText.label` — 구조 설명.
- `@AbapCatalog.enhancement.category` — 구조 확장 가능 여부.

**확인** 두 구조가 활성화됩니다.

<details><summary>정답·해설</summary>

```cds
@EndUserText.label : 'Legacy order header change flags ###'
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE
define structure zleg_s_ordh_x_### {
  requester     : xsdboolean;
  supplier_id   : xsdboolean;
  order_date    : xsdboolean;
  delivery_date : xsdboolean;
  currency_code : xsdboolean;
  note          : xsdboolean;
}
```

```cds
@EndUserText.label : 'Legacy order item change flags ###'
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE
define structure zleg_s_ordi_x_### {
  product_id    : xsdboolean;
  item_text     : xsdboolean;
  quantity      : xsdboolean;
  quantity_unit : xsdboolean;
  unit_price    : xsdboolean;
}
```

왜 이렇게 쓰나

- 공식 레거시 예제의 `/DMO/S_TRAVEL_INTX`도 같은 모양입니다. 필드마다 `XSDBOOLEAN` 타입이고 이름은 `/DMO/TRAVEL` 테이블 필드와 같습니다.
- 이름이 같아야 하는 이유는 두 가지입니다. (1) 레거시 클래스가 "플래그 필드 이름 = 값 필드 이름"이라는 규칙으로 RTTI 루프를 돌며 값을 복사합니다(7단계 `_apply_flags`). (2) R-06 BDEF의 `mapping for <DB 테이블> control <제어 구조>`는 CDS 요소 ↔ DB 필드 매핑을 제어 구조에도 똑같이 적용합니다. 그래서 `CORRESPONDING zleg_s_ordh_x_###( entity MAPPING FROM ENTITY )` 한 줄로 RAP의 `%control` 플래그가 레거시 X 구조로 바뀝니다.
- 이 구조는 `ZIF_LEG_ORDER_###` 안에서 `INCLUDE TYPE ... AS _intx` 로 들어갑니다. `/DMO/S_TRAVEL_INX`도 키 + `.INCLUDE /DMO/S_TRAVEL_INTX`(그룹 이름 `_INTX`) 구조입니다.

</details>

#### 4단계. 레거시 메시지 클래스 만들기

요구사항

레거시 API는 업무 오류가 나도 **예외를 던지지 않고 메시지 테이블을 돌려줍니다**. 그 메시지들의 원문을 메시지 클래스에 만드세요.

1. 메시지 클래스 `ZLEG_MSG_###` (ADT: New > Other ABAP Repository Object > Texts > Message Class)를 만들고 아래 메시지를 넣으세요. `&1`~`&4`는 자리표시자입니다.

| 번호 | 텍스트 (영어 원문) | 뜻 |
|---|---|---|
| 001 | Order key is missing. | 주문 번호가 비었음 |
| 002 | Order &1 does not exist. | 주문 없음 |
| 003 | Item &2 of order &1 does not exist. | 품목 없음 |
| 004 | Order &1 is locked by user &2. | 다른 사용자가 잠금 |
| 005 | Order &1 already exists. | 외부 번호 중복 |
| 006 | Invalid action code &3 for item &2 of order &1. | 액션 코드 오류 |
| 007 | Item &2 of order &1 already exists. | 품목 번호 중복 |
| 010 | Supplier &1 does not exist. | 공급업체 없음 |
| 011 | Delivery date &2 must not be before order date &1. | 납기일 < 주문일 |
| 012 | Currency is mandatory for order &1. | 통화 필수 |
| 013 | Requester is mandatory for order &1. | 요청자 필수 |
| 020 | Quantity of item &2 must be greater than zero. | 수량 > 0 |
| 021 | Unit of measure of item &2 is missing. | 단위 필수 |
| 022 | Unit price of item &2 must be greater than zero. | 단가 > 0 |
| 023 | Product &1 does not exist. | 제품 없음 |
| 030 | Status change from &1 to &2 is not allowed. | 허용되지 않는 상태 전이 |
| 031 | Order &1 cannot be changed in status &2. | 상태 때문에 변경 불가 |
| 032 | Order &1 cannot be deleted in status &2. | 상태 때문에 삭제 불가 |
| 033 | Order &1 has no items and cannot be approved. | 품목 없는 주문 승인 불가 |
| 040 | Number range error: &1 | 번호 범위 기술 오류 |
| 041 | No more order numbers available. | 번호 소진 |
| 050 | You are not authorized to change order &1. | 권한 없음 (R-06에서 사용) |
| 051 | Own order &1 above &2 &3 must be approved by another user. | 본인 주문 고액 승인 금지 (R-06에서 사용) |

2. 메시지는 짧고 사실만 말하게 쓰세요. 화면에 그대로 뜹니다.

**확인** 메시지 클래스를 저장·활성화하고, 편집기에서 메시지 23개가 보입니다.

<details><summary>정답·해설</summary>

메시지 클래스 편집기는 표 형식입니다. 위 표의 번호와 영어 원문을 그대로 입력하면 됩니다. "Self-Explanatory" 체크는 모두 켜 두세요(긴 설명 텍스트를 따로 쓰지 않음).

왜 이렇게 쓰나

- 레거시 API가 예외 대신 메시지를 돌려주는 이유: 한 번의 호출에서 **여러 오류를 한꺼번에** 알려 줄 수 있고, 호출자가 "오류가 있으니 이 호출만 없던 일로 하고 계속 진행"할 수 있기 때문입니다. `/DMO/FLIGHT_TRAVEL_*` 함수 모듈도 `ET_MESSAGES TYPE /DMO/T_MESSAGE`를 돌려줍니다.
- RAP 쪽에서 보면 이 방식이 오히려 편합니다. RAP 핸들러는 **예외를 밖으로 던지면 안 되고**(치트시트 EML 문서의 "Raising an exception … It is not allowed to leave a RAP transaction this way") failed/reported로 결과를 돌려줘야 하므로, 메시지 테이블을 failed/reported로 옮겨 적기만 하면 됩니다(R-06).
- 메시지 번호 체계를 묶어 두면(001~007 키/존재, 010~023 필드 검증, 030~033 상태, 040~ 기술, 050~ 권한) R-06에서 메시지 번호 → `%fail-cause` 변환표를 만들기 쉽습니다.

</details>

#### 5단계. 잠금 객체와 번호 범위 객체 만들기

요구사항

1. 잠금 객체 `EZLEG_ORD_###`를 만드세요. (ADT: New > Other ABAP Repository Object > Dictionary > Lock Object)
   - Primary Table: `ZLEG_ORDH_###`, Lock Mode: **Write Lock (E, 배타)**.
   - Secondary Table: `ZLEG_ORDI_###`, Lock Mode: E. (헤더 키 `order_id`로 연결)
   - Lock Parameter: `ORDER_ID` (CLIENT는 자동으로 포함됩니다.)
2. 번호 범위 객체 `ZLEGORD###`를 만드세요. (ADT: New > Other ABAP Repository Object > 검색창에 "Number Range")
   - Number Length Domain: `ZLEG_ORDER_ID_###`
   - Percentage Warning 10, Buffering: 메인 메모리 버퍼 사용(기본값)
   - 구간(interval) `01`은 11단계 콘솔 클래스에서 코드로 만듭니다(0000000001 ~ 8999999999).
3. 번호 범위를 9로 시작하는 번호(9000000000 이상)까지 쓰지 않는 이유를 적어 보세요.

**확인** 두 객체가 활성화됩니다. 잠금 객체의 개요 화면에 Lock Parameter `ORDER_ID`가 보입니다.

<details><summary>정답·해설</summary>

| 객체 | 항목 | 값 |
|---|---|---|
| 잠금 객체 `EZLEG_ORD_###` | Description | Lock legacy order ### |
| | Primary Table / Lock Mode | `ZLEG_ORDH_###` / Write Lock |
| | Secondary Table / Lock Mode | `ZLEG_ORDI_###` / Write Lock |
| | Lock Parameters | `CLIENT`, `ORDER_ID` |
| 번호 범위 객체 `ZLEGORD###` | Description | Legacy order numbers ### |
| | Number Length Domain | `ZLEG_ORDER_ID_###` |
| | Percentage Warning | 10 |
| | Buffering | Main memory buffering, 버퍼 번호 개수 1 (공식 `/DMO/TRAVL`과 같은 설정) |

왜 이렇게 쓰나

- **잠금 객체**: 공식 예제의 `/DMO/ETRAVEL`도 기본 테이블 `/DMO/TRAVEL`, 모드 E, 파라미터 `CLIENT`, `TRAVEL_ID`입니다. ABAP Cloud에서는 `ENQUEUE_...` 함수 모듈을 직접 호출할 수 없으므로 **`cl_abap_lock_object_factory=>get_instance( iv_name = 'EZLEG_ORD_###' )->enqueue( ... )`** 로 사용합니다(8단계). 잠금은 기본적으로 트랜잭션(SAP LUW)이 끝날 때(COMMIT/ROLLBACK) 풀립니다.
- 품목 테이블을 보조 테이블로 넣으면 "주문 하나를 잠그면 그 품목들도 잠긴다"는 의미가 문서화됩니다. RAP에서도 품목은 `lock dependent by _Order`(R-06)이므로 잠금의 단위는 언제나 주문 헤더입니다.
- **번호 범위 객체**: 이름 길이가 최대 10자라 `ZLEGORD###`처럼 밑줄 없이 지었습니다. ABAP Cloud에서는 `cl_numberrange_runtime=>number_get`으로 번호를 받고, `cl_numberrange_intervals=>create/read/update`로 구간을 관리합니다(공식 `/DMO/CL_FLIGHT_DATA_GENERATOR`의 `reset_numberrange_interval`과 같은 방식).
- **9로 시작하는 번호를 남겨 두는 이유**: late numbering에서는 저장 직전까지 "임시 번호"를 써야 합니다. 이 레거시는 공식 `/DMO/CL_FLIGHT_LEGACY`의 `late_numbering_boundary`와 같은 아이디어로 `9000000000` 이상을 임시 번호 전용으로 예약합니다. 최종 번호가 임시 번호 영역과 겹치면 "이 번호가 임시인가 최종인가"를 구분할 수 없습니다.

자주 나는 오류와 해결

- 트라이얼 시스템의 ADT에서 번호 범위 객체 생성 메뉴를 찾지 못하면 (실제 시스템에서 확인 필요), 7단계 클래스의 상수 `mv_number_source`를 "MAX + 1" 방식(`c_number_source-max_plus_one`)으로 바꾸어 진행할 수 있도록 대체 경로를 함께 구현합니다. 그 방식의 위험(동시 저장 시 번호 충돌)도 7단계 해설에 적었습니다.

</details>

#### 6단계. 레거시 API 인터페이스 `ZIF_LEG_ORDER_###` 만들기

요구사항

레거시 클래스의 **공개 계약**을 인터페이스로 분리합니다. 이렇게 해 두면 R-07에서 RAP behavior pool을 테스트할 때 이 인터페이스를 구현한 가짜(fake) 레거시를 끼워 넣을 수 있습니다.

1. 타입
   - `t_order_id`(= `zleg_order_id_###`), `t_item_no`, `t_status`, `t_numbering_mode`(CHAR 1), `t_action_code`(CHAR 1)
   - DB 행 타입 `ts_order`/`tt_order`, `ts_item`/`tt_item`, 번호 목록 `tt_order_id`
   - 입력 구조 `ts_order_in`(관리 필드·상태·총액 제외), `ts_item_in`/`tt_item_in`
   - 제어 구조 `ts_order_inx`(order_id + `INCLUDE TYPE zleg_s_ordh_x_### AS _intx`), `ts_item_inx`/`tt_item_inx`(item_no + action_code + `INCLUDE TYPE zleg_s_ordi_x_### AS _intx`)
   - 메시지 `ts_message`/`tt_message`: msgty, msgid, msgno, msgv1~4 + 어느 주문(`order_id`)·품목(`item_no`)·필드(`fieldname`, DB 필드 이름)에 대한 메시지인지
   - 번호 매핑 `ts_order_mapping`/`tt_order_mapping`(preliminary/final 주문 번호), `ts_item_key`, `ts_item_mapping`/`tt_item_mapping`
2. 상수: `numbering_mode`(early `E` / late `L` / external `X`), `action_code`(create `C` / update `U` / delete `D`), `status`(new `N` / approved `A` / rejected `R` / completed `C`), `late_numbering_boundary = '9000000000'`, `message_class = 'ZLEG_MSG_###'`.
3. 메서드 (모두 업무 오류는 `et_messages`로만 알림, 예외 없음)
   - `create_order` — 헤더 + 품목 생성, 번호 매기기 방식 선택
   - `update_order` — 헤더 X 구조 + 품목 테이블(액션 코드 C/U/D)
   - `delete_order`
   - `set_status` — 상태 전이
   - `read_orders` — 여러 주문을 한 번에(버퍼 우선, 다음 DB), 품목 포함 여부 선택
   - `lock_order`
   - `draw_order_ids` — 최종 번호를 미리 뽑기(R-07 draft early numbering용)
   - `check_orders` — 버퍼 전체의 저장 전 검사
   - `determine_totals` — 버퍼 전체의 총액 재계산(상향식 파생)
   - `adjust_numbers` — 임시 번호 → 최종 번호, 매핑 반환
   - `save` — 버퍼를 DB에 기록(COMMIT 없음)
   - `initialize` — 버퍼 비우기

**확인** 인터페이스가 활성화됩니다. (구조 `ZLEG_S_ORD*_X_###`가 먼저 활성화되어 있어야 합니다.)

<details><summary>정답·해설</summary>

```abap
"! <p class="shorttext synchronized">Legacy purchase order API ###</p>
"! 레거시 주문 애플리케이션의 공개 계약.
"! - 모든 쓰기 메서드는 버퍼만 바꾼다. DB는 save( )에서만 바뀐다.
"! - 업무 오류는 예외가 아니라 et_messages로 돌려준다.
"! - 한 번의 호출 안에서는 전부 아니면 전무(all-or-nothing): 오류가 있으면 그 호출의 변경은 버퍼에 남지 않는다.
"! - 버퍼는 호출 사이에 유지된다. 처음부터 다시 하려면 initialize( )를 부른다.
INTERFACE zif_leg_order_### PUBLIC.

  "------------------------------------------------------------------
  " 기본 타입
  "------------------------------------------------------------------
  TYPES t_order_id       TYPE zleg_order_id_###.
  TYPES t_item_no        TYPE zleg_ordi_###-item_no.
  TYPES t_status         TYPE zleg_ordh_###-status.
  TYPES t_numbering_mode TYPE c LENGTH 1.
  TYPES t_action_code    TYPE c LENGTH 1.

  TYPES ts_order    TYPE zleg_ordh_###.
  TYPES tt_order    TYPE STANDARD TABLE OF ts_order WITH EMPTY KEY.
  TYPES ts_item     TYPE zleg_ordi_###.
  TYPES tt_item     TYPE STANDARD TABLE OF ts_item WITH EMPTY KEY.
  TYPES tt_order_id TYPE STANDARD TABLE OF t_order_id WITH EMPTY KEY.

  "------------------------------------------------------------------
  " 입력 구조: 호출자가 바꿀 수 있는 필드만 (상태/총액/관리 필드 없음)
  "------------------------------------------------------------------
  TYPES: BEGIN OF ts_order_in,
           order_id      TYPE t_order_id,
           requester     TYPE zleg_ordh_###-requester,
           supplier_id   TYPE zleg_ordh_###-supplier_id,
           order_date    TYPE zleg_ordh_###-order_date,
           delivery_date TYPE zleg_ordh_###-delivery_date,
           currency_code TYPE zleg_ordh_###-currency_code,
           note          TYPE zleg_ordh_###-note,
         END OF ts_order_in.

  TYPES: BEGIN OF ts_item_in,
           item_no       TYPE t_item_no,
           product_id    TYPE zleg_ordi_###-product_id,
           item_text     TYPE zleg_ordi_###-item_text,
           quantity      TYPE zleg_ordi_###-quantity,
           quantity_unit TYPE zleg_ordi_###-quantity_unit,
           unit_price    TYPE zleg_ordi_###-unit_price,
         END OF ts_item_in,
         tt_item_in TYPE STANDARD TABLE OF ts_item_in WITH EMPTY KEY.

  "------------------------------------------------------------------
  " 제어(X) 구조: 키(+액션 코드) + 필드별 변경 플래그
  "------------------------------------------------------------------
  TYPES BEGIN OF ts_order_inx.
  TYPES   order_id TYPE t_order_id.
          INCLUDE TYPE zleg_s_ordh_x_### AS _intx.
  TYPES END OF ts_order_inx.

  TYPES BEGIN OF ts_item_inx.
  TYPES   item_no     TYPE t_item_no.
  TYPES   action_code TYPE t_action_code.
          INCLUDE TYPE zleg_s_ordi_x_### AS _intx.
  TYPES END OF ts_item_inx.
  TYPES tt_item_inx TYPE STANDARD TABLE OF ts_item_inx WITH EMPTY KEY.

  "------------------------------------------------------------------
  " 메시지: T100 정보 + 어느 주문/품목/필드에 대한 것인지
  "------------------------------------------------------------------
  TYPES: BEGIN OF ts_message,
           msgty     TYPE symsgty,
           msgid     TYPE symsgid,
           msgno     TYPE symsgno,
           msgv1     TYPE symsgv,
           msgv2     TYPE symsgv,
           msgv3     TYPE symsgv,
           msgv4     TYPE symsgv,
           order_id  TYPE t_order_id,
           item_no   TYPE t_item_no,
           fieldname TYPE string,     " DB 필드 이름, 예: 'DELIVERY_DATE'
         END OF ts_message,
         tt_message TYPE STANDARD TABLE OF ts_message WITH EMPTY KEY.

  "------------------------------------------------------------------
  " late numbering: 임시 번호 → 최종 번호
  "------------------------------------------------------------------
  TYPES: BEGIN OF ts_order_mapping,
           preliminary TYPE t_order_id,
           final       TYPE t_order_id,
         END OF ts_order_mapping,
         tt_order_mapping TYPE STANDARD TABLE OF ts_order_mapping WITH EMPTY KEY,
         BEGIN OF ts_item_key,
           order_id TYPE t_order_id,
           item_no  TYPE t_item_no,
         END OF ts_item_key,
         BEGIN OF ts_item_mapping,
           preliminary TYPE ts_item_key,
           final       TYPE ts_item_key,
         END OF ts_item_mapping,
         tt_item_mapping TYPE STANDARD TABLE OF ts_item_mapping WITH EMPTY KEY.

  "------------------------------------------------------------------
  " 상수
  "------------------------------------------------------------------
  CONSTANTS:
    BEGIN OF numbering_mode,
      early    TYPE t_numbering_mode VALUE 'E', " 생성 즉시 최종 번호
      late     TYPE t_numbering_mode VALUE 'L', " 임시 번호(9로 시작) → adjust_numbers에서 최종 번호
      external TYPE t_numbering_mode VALUE 'X', " 호출자가 준 번호를 그대로 사용
    END OF numbering_mode,
    BEGIN OF action_code,
      create TYPE t_action_code VALUE 'C',
      update TYPE t_action_code VALUE 'U',
      delete TYPE t_action_code VALUE 'D',
    END OF action_code,
    BEGIN OF status,
      new       TYPE t_status VALUE 'N',
      approved  TYPE t_status VALUE 'A',
      rejected  TYPE t_status VALUE 'R',
      completed TYPE t_status VALUE 'C',
    END OF status,
    late_numbering_boundary TYPE t_order_id VALUE '9000000000',
    message_class           TYPE symsgid    VALUE 'ZLEG_MSG_###'.

  "------------------------------------------------------------------
  " 메서드
  "------------------------------------------------------------------
  METHODS create_order
    IMPORTING is_order          TYPE ts_order_in
              it_items          TYPE tt_item_in OPTIONAL
              iv_numbering_mode TYPE t_numbering_mode DEFAULT zif_leg_order_###=>numbering_mode-early
    EXPORTING es_order          TYPE ts_order
              et_items          TYPE tt_item
              et_messages       TYPE tt_message.

  "! it_items와 it_itemsx는 같은 인덱스끼리 짝이다. action_code = 'C'이고 item_no가 비어 있으면 레거시가 번호를 붙인다.
  METHODS update_order
    IMPORTING is_order    TYPE ts_order_in
              is_orderx   TYPE ts_order_inx
              it_items    TYPE tt_item_in  OPTIONAL
              it_itemsx   TYPE tt_item_inx OPTIONAL
    EXPORTING es_order    TYPE ts_order
              et_items    TYPE tt_item
              et_messages TYPE tt_message.

  METHODS delete_order
    IMPORTING iv_order_id TYPE t_order_id
    EXPORTING et_messages TYPE tt_message.

  METHODS set_status
    IMPORTING iv_order_id TYPE t_order_id
              iv_status   TYPE t_status
    EXPORTING es_order    TYPE ts_order
              et_messages TYPE tt_message.

  METHODS read_orders
    IMPORTING it_order_ids  TYPE tt_order_id
              iv_with_items TYPE abap_bool DEFAULT abap_true
    EXPORTING et_orders     TYPE tt_order
              et_items      TYPE tt_item
              et_messages   TYPE tt_message.

  METHODS lock_order
    IMPORTING iv_order_id TYPE t_order_id
    EXPORTING et_messages TYPE tt_message.

  "! 최종 번호를 미리 뽑는다(draft의 early numbering용). iv_floor보다 큰 번호만 돌려준다(MAX+1 방식일 때 사용).
  METHODS draw_order_ids
    IMPORTING iv_quantity TYPE i
              iv_floor    TYPE t_order_id OPTIONAL
    EXPORTING et_ids      TYPE tt_order_id
              et_messages TYPE tt_message.

  METHODS check_orders
    EXPORTING et_messages TYPE tt_message.

  METHODS determine_totals.

  METHODS adjust_numbers
    EXPORTING et_order_mapping TYPE tt_order_mapping
              et_item_mapping  TYPE tt_item_mapping.

  METHODS save.

  METHODS initialize.

ENDINTERFACE.
```

왜 이렇게 쓰나

- `/DMO/IF_FLIGHT_LEGACY`도 같은 역할(레거시 API에서 쓰는 모든 타입·상수 모음)을 합니다. 거기서는 메서드가 함수 모듈에 있었지만, 이 문제에서는 **메서드까지 인터페이스에 둡니다.** 그래야 RAP behavior pool이 구체 클래스가 아니라 인터페이스에 의존하게 되고, R-07에서 가짜 구현을 주입할 수 있습니다.
- `INCLUDE TYPE ... AS _intx`: 그룹 이름 `_intx`로 제어 플래그 묶음 전체를 한 번에 다룰 수 있습니다(`ls_x-_intx = CORRESPONDING #( ... )`). `/DMO/S_TRAVEL_INX`의 `.INCLUDE` 그룹 이름 `_INTX`와 같은 방식입니다.
- 메시지에 `order_id`/`item_no`/`fieldname`을 실어 보내는 것이 이 레거시의 핵심 설계입니다. RAP에서 `check_before_save`는 버퍼 전체를 한 번에 검사하므로 "어느 인스턴스의 어느 필드" 오류인지 알아야 failed/reported의 `%tky`, `%path`, `%element`를 채울 수 있습니다.
- `update_order`가 헤더와 품목 생성/변경/삭제를 모두 받는 이유: 공식 레거시 `/DMO/FLIGHT_TRAVEL_UPDATE`처럼 "주문 하나 = 업무 단위"로 묶어 한 번의 호출이 전부 아니면 전무로 처리되게 하기 위해서입니다. RAP의 품목 create-by-association/update/delete도 모두 이 메서드로 들어갑니다(R-06).

</details>

#### 7단계. 레거시 클래스 정의와 공통 도우미 메서드

요구사항

1. 클래스 `ZCL_LEG_ORDER_###`를 `PUBLIC FINAL CREATE PRIVATE`로 만들고 `ZIF_LEG_ORDER_###`를 구현하세요. `get_instance( )`로 싱글턴을 돌려줍니다(반환 타입은 인터페이스).
2. 자체 트랜잭션 버퍼 `ms_buffer`를 두세요.
   - `orders`: 헤더 행 + 변경 종류(`change`: C 생성 / U 변경 / D 삭제), 키 `order_id`의 정렬 테이블
   - `items`: 품목 행 + 변경 종류, 키 `order_id item_no`의 정렬 테이블
3. 번호 공급 방식 `mv_number_source`(번호 범위 `N` / MAX+1 `M`)와 마지막 임시 번호 `mv_last_preliminary`, 마지막으로 뽑은 번호 `mv_last_drawn`을 두세요.
4. 아래 private 도우미를 이 단계에서 구현하세요.
   - `_add_message`: 메시지 한 줄 추가 (메시지 클래스·심각도 기본값 E)
   - `_find_order`: 버퍼 → DB 순서로 헤더 한 건 찾기 (삭제 표시면 없음, 임시 번호는 DB를 보지 않음)
   - `_get_items_mass`: 여러 주문의 품목을 **SELECT 한 번**으로 읽고 버퍼 변경분을 덮어씀
   - `_put_order`, `_put_item`: 버퍼에 넣기 (생성된 행을 삭제하면 버퍼에서 아예 제거, 생성된 행을 변경하면 계속 C로 유지)
   - `_set_admin`: 생성자/변경자/시각 채우기 (`GET TIME STAMP`, `cl_abap_context_info`)
   - `_apply_flags`: 플래그가 켜진 필드만 원본 → 대상으로 복사 (RTTI)
   - `_draw_final_numbers`: 최종 번호 N개 뽑기 (번호 범위 / MAX+1)
   - `_is_transition_allowed`: 상태 전이표 N→A, N→R, A→C, R→N
5. 클래스 정의에 지금 단계에서 만들지 않는 메서드(인터페이스 메서드)의 구현은 8~10단계에서 붙입니다. 이 단계에서는 IMPLEMENTATION 안에 인터페이스 메서드를 빈 `METHOD ... ENDMETHOD.`로 두면 활성화할 수 있습니다(ADT 퀵픽스 "Add implementation" 사용).

**확인** 클래스가 활성화됩니다(인터페이스 메서드는 빈 껍데기 상태). 아직 실행할 것은 없습니다.

<details><summary>정답·해설</summary>

클래스 정의 전체와 이 단계 도우미 메서드 구현입니다. 8~10단계의 `METHOD zif_leg_order_###~...` 블록은 같은 `IMPLEMENTATION` 안에 이어 붙입니다.

```abap
"! <p class="shorttext synchronized">Legacy purchase order application ###</p>
"! RAP을 모르는 레거시 애플리케이션 흉내. 자체 버퍼를 가진 싱글턴.
CLASS zcl_leg_order_### DEFINITION
  PUBLIC
  FINAL
  CREATE PRIVATE.

  PUBLIC SECTION.
    INTERFACES zif_leg_order_###.

    "! 싱글턴: 한 ABAP 세션(= 한 RAP 트랜잭션)에서 버퍼는 하나다
    CLASS-METHODS get_instance
      RETURNING VALUE(ro_instance) TYPE REF TO zif_leg_order_###.

  PROTECTED SECTION.
  PRIVATE SECTION.
    "--- 버퍼 행: DB 행 + 변경 종류 -----------------------------------
    TYPES BEGIN OF ty_order_entry.
            INCLUDE TYPE zleg_ordh_###.
    TYPES   change TYPE c LENGTH 1.
    TYPES END OF ty_order_entry.
    TYPES tt_order_entry TYPE SORTED TABLE OF ty_order_entry WITH UNIQUE KEY order_id.

    TYPES BEGIN OF ty_item_entry.
            INCLUDE TYPE zleg_ordi_###.
    TYPES   change TYPE c LENGTH 1.
    TYPES END OF ty_item_entry.
    TYPES tt_item_entry TYPE SORTED TABLE OF ty_item_entry WITH UNIQUE KEY order_id item_no.

    TYPES: BEGIN OF ty_buffer,
             orders TYPE tt_order_entry,
             items  TYPE tt_item_entry,
           END OF ty_buffer.

    CONSTANTS:
      BEGIN OF c_change,
        created TYPE c LENGTH 1 VALUE 'C', " 아직 DB에 없음 → INSERT
        updated TYPE c LENGTH 1 VALUE 'U', " DB에 있음, 바뀜 → UPDATE
        deleted TYPE c LENGTH 1 VALUE 'D', " DB에 있음, 지움 → DELETE
      END OF c_change,
      BEGIN OF c_number_source,
        number_range TYPE c LENGTH 1 VALUE 'N', " 번호 범위 객체 ZLEGORD###
        max_plus_one TYPE c LENGTH 1 VALUE 'M', " 대체 경로: DB 최대값 + 1 (동시성 위험)
      END OF c_number_source,
      c_nr_object   TYPE cl_numberrange_runtime=>nr_object   VALUE 'ZLEGORD###',
      c_nr_interval TYPE cl_numberrange_runtime=>nr_interval VALUE '01',
      c_item_step   TYPE i VALUE 10.

    CLASS-DATA go_instance TYPE REF TO zcl_leg_order_###.

    DATA ms_buffer           TYPE ty_buffer.
    DATA mv_number_source    TYPE c LENGTH 1 VALUE c_number_source-number_range.
    DATA mv_last_preliminary TYPE zif_leg_order_###=>t_order_id VALUE zif_leg_order_###=>late_numbering_boundary.
    DATA mv_last_drawn       TYPE zif_leg_order_###=>t_order_id.

    METHODS _add_message
      IMPORTING iv_msgno     TYPE symsgno
                iv_msgty     TYPE symsgty DEFAULT 'E'
                iv_v1        TYPE simple OPTIONAL
                iv_v2        TYPE simple OPTIONAL
                iv_v3        TYPE simple OPTIONAL
                iv_v4        TYPE simple OPTIONAL
                iv_order_id  TYPE zif_leg_order_###=>t_order_id OPTIONAL
                iv_item_no   TYPE zif_leg_order_###=>t_item_no OPTIONAL
                iv_fieldname TYPE string OPTIONAL
      CHANGING  ct_messages  TYPE zif_leg_order_###=>tt_message.

    METHODS _find_order
      IMPORTING iv_order_id TYPE zif_leg_order_###=>t_order_id
      EXPORTING es_order    TYPE zif_leg_order_###=>ts_order
                ev_found    TYPE abap_bool.

    METHODS _get_items_mass
      IMPORTING it_order_ids    TYPE zif_leg_order_###=>tt_order_id
      RETURNING VALUE(rt_items) TYPE zif_leg_order_###=>tt_item.

    METHODS _put_order
      IMPORTING is_order  TYPE zif_leg_order_###=>ts_order
                iv_change TYPE c.

    METHODS _put_item
      IMPORTING is_item   TYPE zif_leg_order_###=>ts_item
                iv_change TYPE c.

    METHODS _set_admin
      IMPORTING iv_new   TYPE abap_bool
      CHANGING  cs_order TYPE zif_leg_order_###=>ts_order.

    METHODS _apply_flags
      IMPORTING is_source TYPE any
                is_flags  TYPE any
      CHANGING  cs_target TYPE any.

    METHODS _draw_final_numbers
      IMPORTING iv_quantity TYPE i
                iv_floor    TYPE zif_leg_order_###=>t_order_id OPTIONAL
      EXPORTING et_ids      TYPE zif_leg_order_###=>tt_order_id
      CHANGING  ct_messages TYPE zif_leg_order_###=>tt_message.

    METHODS _is_transition_allowed
      IMPORTING iv_from           TYPE zif_leg_order_###=>t_status
                iv_to             TYPE zif_leg_order_###=>t_status
      RETURNING VALUE(rv_allowed) TYPE abap_bool.

    "--- 8~10단계에서 구현 -------------------------------------------
    METHODS _create_item
      IMPORTING is_order    TYPE zif_leg_order_###=>ts_order
                is_item_in  TYPE zif_leg_order_###=>ts_item_in
      EXPORTING es_item     TYPE zif_leg_order_###=>ts_item
      CHANGING  ct_messages TYPE zif_leg_order_###=>tt_message.

    METHODS _update_item
      IMPORTING iv_order_id TYPE zif_leg_order_###=>t_order_id
                is_item_in  TYPE zif_leg_order_###=>ts_item_in
                is_itemx    TYPE zif_leg_order_###=>ts_item_inx
      EXPORTING es_item     TYPE zif_leg_order_###=>ts_item
      CHANGING  ct_messages TYPE zif_leg_order_###=>tt_message.

    METHODS _delete_item
      IMPORTING iv_order_id TYPE zif_leg_order_###=>t_order_id
                iv_item_no  TYPE zif_leg_order_###=>t_item_no
      CHANGING  ct_messages TYPE zif_leg_order_###=>tt_message.

    METHODS _check_item_immediate
      IMPORTING is_item      TYPE zif_leg_order_###=>ts_item
      CHANGING  ct_messages  TYPE zif_leg_order_###=>tt_message
      RETURNING VALUE(rv_ok) TYPE abap_bool.

    METHODS _has_error
      IMPORTING it_messages     TYPE zif_leg_order_###=>tt_message
      RETURNING VALUE(rv_error) TYPE abap_bool.
ENDCLASS.

CLASS zcl_leg_order_### IMPLEMENTATION.

  METHOD get_instance.
    IF go_instance IS NOT BOUND.
      go_instance = NEW #( ).
    ENDIF.
    ro_instance = go_instance.
  ENDMETHOD.

  METHOD _add_message.
    APPEND VALUE #( msgty     = iv_msgty
                    msgid     = zif_leg_order_###=>message_class
                    msgno     = iv_msgno
                    msgv1     = iv_v1
                    msgv2     = iv_v2
                    msgv3     = iv_v3
                    msgv4     = iv_v4
                    order_id  = iv_order_id
                    item_no   = iv_item_no
                    fieldname = iv_fieldname ) TO ct_messages.
  ENDMETHOD.

  METHOD _has_error.
    rv_error = xsdbool( line_exists( it_messages[ msgty = 'E' ] )
                     OR line_exists( it_messages[ msgty = 'A' ] ) ).
  ENDMETHOD.

  METHOD _find_order.
    CLEAR: es_order, ev_found.

    " 1) 버퍼가 언제나 우선: 이 세션에서 바꾼 내용이 DB보다 최신이다
    READ TABLE ms_buffer-orders INTO DATA(ls_entry)
         WITH TABLE KEY order_id = iv_order_id.
    IF sy-subrc = 0.
      IF ls_entry-change <> c_change-deleted.
        es_order = CORRESPONDING #( ls_entry ).
        ev_found = abap_true.
      ENDIF.
      RETURN.
    ENDIF.

    " 2) 임시 번호는 DB에 있을 수 없다
    IF iv_order_id >= zif_leg_order_###=>late_numbering_boundary.
      RETURN.
    ENDIF.

    SELECT SINGLE * FROM zleg_ordh_###
      WHERE order_id = @iv_order_id
      INTO @es_order.
    ev_found = xsdbool( sy-subrc = 0 ).
  ENDMETHOD.

  METHOD _get_items_mass.
    CLEAR rt_items.
    CHECK it_order_ids IS NOT INITIAL.   " FOR ALL ENTRIES에 빈 표를 주면 전체를 읽는다!

    " DB: 주문 수와 관계없이 SELECT 한 번
    SELECT * FROM zleg_ordi_###
      FOR ALL ENTRIES IN @it_order_ids
      WHERE order_id = @it_order_ids-table_line
      INTO TABLE @rt_items.

    " 버퍼 변경분으로 덮어쓰기 (생성/변경은 버퍼 값, 삭제는 제거)
    LOOP AT it_order_ids INTO DATA(lv_order_id).
      LOOP AT ms_buffer-items INTO DATA(ls_entry) WHERE order_id = lv_order_id.
        DELETE rt_items WHERE order_id = ls_entry-order_id
                          AND item_no  = ls_entry-item_no.
        IF ls_entry-change <> c_change-deleted.
          APPEND CORRESPONDING #( ls_entry ) TO rt_items.
        ENDIF.
      ENDLOOP.
    ENDLOOP.

    SORT rt_items BY order_id item_no.
  ENDMETHOD.

  METHOD _put_order.
    DATA ls_new TYPE ty_order_entry.

    READ TABLE ms_buffer-orders INTO DATA(ls_old)
         WITH TABLE KEY order_id = is_order-order_id.
    IF sy-subrc <> 0.
      ls_new = CORRESPONDING #( is_order ).
      ls_new-change = iv_change.
      INSERT ls_new INTO TABLE ms_buffer-orders.
      RETURN.
    ENDIF.

    " 이번 세션에서 만든 주문을 지우면: DB에 간 적이 없으니 흔적도 남기지 않는다
    IF iv_change = c_change-deleted AND ls_old-change = c_change-created.
      DELETE TABLE ms_buffer-orders WITH TABLE KEY order_id = is_order-order_id.
      RETURN.
    ENDIF.

    ls_new = CORRESPONDING #( is_order ).
    ls_new-change = COND #( WHEN iv_change = c_change-deleted     THEN c_change-deleted
                            WHEN ls_old-change = c_change-created THEN c_change-created
                            ELSE c_change-updated ).
    " 정렬 테이블의 키 필드는 필드 심볼로 덮어쓸 수 없으므로 MODIFY TABLE 사용
    MODIFY TABLE ms_buffer-orders FROM ls_new.
  ENDMETHOD.

  METHOD _put_item.
    DATA ls_new TYPE ty_item_entry.

    READ TABLE ms_buffer-items INTO DATA(ls_old)
         WITH TABLE KEY order_id = is_item-order_id
                        item_no  = is_item-item_no.
    IF sy-subrc <> 0.
      ls_new = CORRESPONDING #( is_item ).
      ls_new-change = iv_change.
      INSERT ls_new INTO TABLE ms_buffer-items.
      RETURN.
    ENDIF.

    IF iv_change = c_change-deleted AND ls_old-change = c_change-created.
      DELETE TABLE ms_buffer-items WITH TABLE KEY order_id = is_item-order_id
                                                  item_no  = is_item-item_no.
      RETURN.
    ENDIF.

    ls_new = CORRESPONDING #( is_item ).
    ls_new-change = COND #( WHEN iv_change = c_change-deleted     THEN c_change-deleted
                            WHEN ls_old-change = c_change-created THEN c_change-created
                            ELSE c_change-updated ).
    MODIFY TABLE ms_buffer-items FROM ls_new.
  ENDMETHOD.

  METHOD _set_admin.
    DATA lv_now TYPE timestampl.
    GET TIME STAMP FIELD lv_now.
    DATA(lv_user) = cl_abap_context_info=>get_user_technical_name( ).

    IF iv_new = abap_true.
      cs_order-created_by = lv_user.
      cs_order-created_at = lv_now.
    ENDIF.
    " ETag 필드는 '변경하는 순간' 버퍼에서 갱신한다 (save에서 다시 찍지 않는다 → 해설 참고)
    cs_order-last_changed_by       = lv_user.
    cs_order-local_last_changed_at = lv_now.
    cs_order-last_changed_at       = lv_now.
  ENDMETHOD.

  METHOD _apply_flags.
    " 플래그 구조의 컴포넌트 이름 = 값 구조의 컴포넌트 이름 (3단계에서 맞춘 규칙)
    DATA(lo_flags) = CAST cl_abap_structdescr( cl_abap_typedescr=>describe_by_data( is_flags ) ).

    LOOP AT lo_flags->components INTO DATA(ls_component).
      ASSIGN COMPONENT ls_component-name OF STRUCTURE is_flags TO FIELD-SYMBOL(<lv_flag>).
      IF sy-subrc <> 0.
        CONTINUE.
      ENDIF.
      IF <lv_flag> <> abap_true.
        CONTINUE.
      ENDIF.
      ASSIGN COMPONENT ls_component-name OF STRUCTURE is_source TO FIELD-SYMBOL(<lv_new>).
      IF sy-subrc <> 0.
        CONTINUE.
      ENDIF.
      ASSIGN COMPONENT ls_component-name OF STRUCTURE cs_target TO FIELD-SYMBOL(<lv_old>).
      IF sy-subrc <> 0.
        CONTINUE.
      ENDIF.
      <lv_old> = <lv_new>.
    ENDLOOP.
  ENDMETHOD.

  METHOD _draw_final_numbers.
    DATA lv_last TYPE int8.

    CLEAR et_ids.
    IF iv_quantity <= 0.
      RETURN.
    ENDIF.

    CASE mv_number_source.

      WHEN c_number_source-number_range.
        TRY.
            cl_numberrange_runtime=>number_get(
              EXPORTING nr_range_nr       = c_nr_interval
                        object            = c_nr_object
                        quantity          = CONV #( iv_quantity )
              IMPORTING number            = DATA(lv_number)
                        returncode        = DATA(lv_returncode)
                        returned_quantity = DATA(lv_returned) ).
          CATCH cx_number_ranges INTO DATA(lx_number_ranges).
            _add_message( EXPORTING iv_msgno    = '040'
                                    iv_v1       = lx_number_ranges->get_text( )
                          CHANGING  ct_messages = ct_messages ).
            RETURN.
        ENDTRY.
        " returncode 2: 구간의 마지막 번호를 줌, 3: 요청보다 적게 줌
        IF lv_returncode = '2' OR lv_returncode = '3' OR lv_returned <> iv_quantity.
          _add_message( EXPORTING iv_msgno = '041' CHANGING ct_messages = ct_messages ).
          RETURN.
        ENDIF.
        lv_last = lv_number.   " number_get은 받은 번호 중 '마지막' 번호를 돌려준다

      WHEN c_number_source-max_plus_one.
        " 대체 경로. 두 세션이 동시에 저장하면 같은 번호를 뽑을 수 있다(학습용).
        SELECT MAX( order_id ) FROM zleg_ordh_###
          WHERE order_id < @zif_leg_order_###=>late_numbering_boundary
          INTO @DATA(lv_db_max).
        lv_last = lv_db_max.
        LOOP AT ms_buffer-orders INTO DATA(ls_entry)
             WHERE order_id < zif_leg_order_###=>late_numbering_boundary.
          IF ls_entry-order_id > lv_last.
            lv_last = ls_entry-order_id.
          ENDIF.
        ENDLOOP.
        IF mv_last_drawn > lv_last.
          lv_last = mv_last_drawn.
        ENDIF.
        IF iv_floor > lv_last.
          lv_last = iv_floor.
        ENDIF.
        lv_last = lv_last + iv_quantity.

    ENDCASE.

    DATA(lv_first) = lv_last - iv_quantity + 1.
    DO iv_quantity TIMES.
      APPEND CONV zif_leg_order_###=>t_order_id( lv_first + sy-index - 1 ) TO et_ids.
    ENDDO.
    mv_last_drawn = lv_last.
  ENDMETHOD.

  METHOD _is_transition_allowed.
    rv_allowed = xsdbool(
         ( iv_from = zif_leg_order_###=>status-new
           AND ( iv_to = zif_leg_order_###=>status-approved OR iv_to = zif_leg_order_###=>status-rejected ) )
      OR ( iv_from = zif_leg_order_###=>status-approved AND iv_to = zif_leg_order_###=>status-completed )
      OR ( iv_from = zif_leg_order_###=>status-rejected AND iv_to = zif_leg_order_###=>status-new ) ).
  ENDMETHOD.

  " 8~10단계: 인터페이스 메서드(zif_leg_order_###~create_order 등) / _create_item / _update_item / _delete_item / _check_item_immediate
  " 를 이 아래에 붙입니다.

ENDCLASS.
```

왜 이렇게 쓰나 (버퍼 설계)

- **버퍼 = "DB에 반영할 변경 목록"**입니다. 각 행에 C/U/D 표시를 붙여 두면 `save`는 표시대로 INSERT/UPDATE/DELETE만 하면 됩니다. 치트시트의 unmanaged 예제(`ZBP_DEMO_ABAP_RAP_RO_U`의 `lcl_buffer`)도 `changed`/`deleted` 플래그로 같은 일을 합니다.
- **생성 후 삭제 = 흔적 없음**: 이번 세션에서 만든 주문(C)을 지우면 버퍼에서 행을 아예 지웁니다. D로 남기면 save에서 DB에 없는 행을 DELETE하게 됩니다.
- **생성 후 변경 = 계속 C**: 아직 DB에 없으니 save에서는 여전히 INSERT여야 합니다.
- **읽기는 언제나 버퍼 우선**(`_find_order`, `_get_items_mass`): RAP의 read 핸들러는 "트랜잭션 버퍼의 현재 상태"를 돌려줘야 합니다. DB만 읽으면 방금 바꾼 값이 안 보입니다(R-06의 "흔한 실수" 표 참고).
- **ETag 시각을 변경 순간에 찍는 이유**: Fiori(OData)는 수정 응답에 담긴 ETag 값을 기억했다가 다음 수정 때 `If-Match`로 돌려보냅니다. 응답의 ETag는 저장 전 트랜잭션 버퍼에서 읽힙니다. 그런데 `save`에서 시각을 다시 찍으면 DB 값이 응답 값과 달라져, 사용자가 바로 다음에 수정할 때 "다른 사용자가 변경함" 오류가 납니다. 공식 레거시도 `_update_admin`으로 버퍼 변경 시점에 `lastchangedat`을 찍고 `save`에서는 그대로 INSERT/UPDATE만 합니다.
- `cl_numberrange_runtime=>number_get`은 요청한 개수만큼 번호를 예약하고 **그 중 마지막 번호**를 돌려줍니다. 그래서 첫 번호 = 마지막 − 개수 + 1 입니다(공식 레거시의 `lv_travel_id_max = CONV i( lv_key ) - lines( ... )`와 같은 계산). 주문 번호가 최대 10자리라 `i`(약 21억)를 넘을 수 있으므로 `int8`로 계산합니다.
- **MAX+1 대체 경로의 위험**: 두 사용자가 거의 동시에 저장하면 둘 다 같은 MAX를 읽고 같은 번호를 쓰려다 INSERT 중복 키로 덤프가 납니다. 번호 범위 객체는 번호 예약을 DB 트랜잭션과 분리해서 처리하므로 이 문제가 없습니다. 학습 환경에서만 대체 경로를 쓰세요.
- `_apply_flags`는 RTTI(`cl_abap_structdescr`)로 플래그 구조의 컴포넌트를 돌며 `ASSIGN COMPONENT`로 같은 이름의 값을 복사합니다. 공식 레거시 `_update`는 "컴포넌트 위치 3번부터"라는 위치 규칙을 쓰지만, 이름 규칙이 더 안전합니다(필드 순서를 바꿔도 깨지지 않음).

자주 나는 오류와 해결

- `MODIFY TABLE` 대신 `READ TABLE ... ASSIGNING <fs>` 후 `<fs> = CORRESPONDING #( ... )`로 통째로 덮어쓰면, 정렬 테이블의 키 필드를 바꾸려 한다는 런타임 오류가 날 수 있습니다. 키를 포함한 행 전체 교체는 `MODIFY TABLE ... FROM`을 쓰세요.
- `FOR ALL ENTRIES IN`의 내부 테이블이 비어 있으면 WHERE 조건이 무시되어 **테이블 전체**를 읽습니다. 그래서 `_get_items_mass` 첫 줄에 `CHECK it_order_ids IS NOT INITIAL`을 둡니다.

</details>

#### 8단계. 생성과 읽기: `create_order`, `read_orders`, `draw_order_ids`

요구사항

1. `create_order`
   - 시작할 때 버퍼와 임시 번호 카운터를 **스냅숏**으로 저장하고, 끝에서 오류 메시지가 하나라도 있으면 스냅숏으로 되돌리세요(전부 아니면 전무).
   - 번호: early → `_draw_final_numbers`로 최종 번호 1개, late → `mv_last_preliminary + 1`(9000000001부터), external → `is_order-order_id`를 그대로 쓰되 비었으면 001, 이미 있으면 005, 임시 번호 영역이면 001.
   - 레거시 파생(determination): 상태 `N`, 주문일이 비었으면 오늘(`cl_abap_context_info=>get_system_date( )`), 총액 0, 관리 필드(`_set_admin` 신규).
   - 품목은 `_create_item`으로 하나씩 만듭니다.
2. `_create_item`
   - 품목 번호가 비었으면 그 주문의 기존 품목(버퍼+DB) 최대값 + 10, 있으면 중복 검사(007).
   - 통화는 헤더 통화. 단가가 비었고 제품이 있으면 `/DMO/SUPPLEMENT`의 가격을 기본값으로 쓰되, 제품 통화가 주문 통화와 같을 때만.
   - 즉시 검사 `_check_item_immediate`: 수량 > 0 (020, 필드 `QUANTITY`), 단가 < 0 이면 022(필드 `UNIT_PRICE`).
   - 품목 금액 = 수량 × 단가. 버퍼에 C로 넣습니다.
3. `read_orders`: 중복 번호를 제거하고, DB 헤더는 **SELECT 한 번**(FOR ALL ENTRIES), 각 번호마다 버퍼 → DB 순으로 찾고, 없으면 002. `iv_with_items = abap_true`면 `_get_items_mass`로 품목까지.
4. `draw_order_ids`: `_draw_final_numbers`를 그대로 공개합니다.

**확인** 클래스가 활성화됩니다. 동작 확인은 11단계 콘솔과 12단계 단위 테스트에서 합니다.

<details><summary>정답·해설</summary>

```abap
  METHOD zif_leg_order_###~create_order.
    CLEAR: es_order, et_items, et_messages.

    " 전부 아니면 전무: 이 호출이 실패하면 버퍼를 호출 전 상태로 되돌린다
    DATA(ls_snapshot)        = ms_buffer.
    DATA(lv_prelim_snapshot) = mv_last_preliminary.

    DATA(ls_order) = CORRESPONDING zif_leg_order_###=>ts_order( is_order ).

    "--- 1) 키 결정 ----------------------------------------------------
    CASE iv_numbering_mode.

      WHEN zif_leg_order_###=>numbering_mode-early.
        _draw_final_numbers( EXPORTING iv_quantity = 1
                             IMPORTING et_ids      = DATA(lt_ids)
                             CHANGING  ct_messages = et_messages ).
        IF _has_error( et_messages ) = abap_true.
          RETURN.
        ENDIF.
        ls_order-order_id = lt_ids[ 1 ].

      WHEN zif_leg_order_###=>numbering_mode-late.
        " 임시 번호: 9000000001, 9000000002 순서 (adjust_numbers에서 최종 번호로 바뀐다)
        mv_last_preliminary = mv_last_preliminary + 1.
        ls_order-order_id   = mv_last_preliminary.

      WHEN zif_leg_order_###=>numbering_mode-external.
        IF ls_order-order_id IS INITIAL
        OR ls_order-order_id >= zif_leg_order_###=>late_numbering_boundary.
          _add_message( EXPORTING iv_msgno = '001' iv_fieldname = `ORDER_ID`
                        CHANGING  ct_messages = et_messages ).
          RETURN.
        ENDIF.
        _find_order( EXPORTING iv_order_id = ls_order-order_id
                     IMPORTING ev_found    = DATA(lv_exists) ).
        IF lv_exists = abap_true.
          _add_message( EXPORTING iv_msgno = '005' iv_v1 = ls_order-order_id iv_order_id = ls_order-order_id
                        CHANGING  ct_messages = et_messages ).
          RETURN.
        ENDIF.

      WHEN OTHERS.
        ASSERT 1 = 0.   " 프로그래밍 오류: 정의되지 않은 번호 매기기 방식
    ENDCASE.

    "--- 2) 레거시 파생값(determination) --------------------------------
    ls_order-status       = zif_leg_order_###=>status-new.
    ls_order-total_amount = 0.
    IF ls_order-order_date IS INITIAL.
      ls_order-order_date = cl_abap_context_info=>get_system_date( ).
    ENDIF.
    _set_admin( EXPORTING iv_new = abap_true CHANGING cs_order = ls_order ).
    _put_order( is_order = ls_order iv_change = c_change-created ).

    "--- 3) 품목 ---------------------------------------------------------
    LOOP AT it_items INTO DATA(ls_item_in).
      _create_item( EXPORTING is_order    = ls_order
                              is_item_in  = ls_item_in
                    IMPORTING es_item     = DATA(ls_item)
                    CHANGING  ct_messages = et_messages ).
      IF ls_item IS NOT INITIAL.
        APPEND ls_item TO et_items.
      ENDIF.
    ENDLOOP.

    "--- 4) 전부 아니면 전무 ---------------------------------------------
    IF _has_error( et_messages ) = abap_true.
      ms_buffer           = ls_snapshot.
      mv_last_preliminary = lv_prelim_snapshot.
      CLEAR: es_order, et_items.
      RETURN.
    ENDIF.

    es_order = ls_order.
  ENDMETHOD.

  METHOD _create_item.
    CLEAR es_item.

    DATA(ls_item) = CORRESPONDING zif_leg_order_###=>ts_item( is_item_in ).
    ls_item-order_id      = is_order-order_id.
    ls_item-currency_code = is_order-currency_code.

    DATA(lt_existing) = _get_items_mass( VALUE #( ( is_order-order_id ) ) ).

    IF ls_item-item_no IS INITIAL.
      " 품목 번호는 항상 레거시가 즉시(early) 정한다: 최대값 + 10
      DATA(lv_max) = REDUCE zif_leg_order_###=>t_item_no(
                       INIT m = CONV zif_leg_order_###=>t_item_no( 0 )
                       FOR ls_e IN lt_existing
                       NEXT m = COND #( WHEN ls_e-item_no > m THEN ls_e-item_no ELSE m ) ).
      ls_item-item_no = lv_max + c_item_step.
    ELSEIF line_exists( lt_existing[ item_no = ls_item-item_no ] ).
      _add_message( EXPORTING iv_msgno    = '007'
                              iv_v1       = ls_item-order_id
                              iv_v2       = ls_item-item_no
                              iv_order_id = ls_item-order_id
                              iv_item_no  = ls_item-item_no
                    CHANGING  ct_messages = ct_messages ).
      RETURN.
    ENDIF.

    " 레거시 파생: 단가 기본값 = 제품 가격 (통화가 같을 때만)
    IF ls_item-unit_price IS INITIAL AND ls_item-product_id IS NOT INITIAL.
      SELECT SINGLE price, currency_code
        FROM /dmo/supplement
        WHERE supplement_id = @ls_item-product_id
        INTO @DATA(ls_product).
      IF sy-subrc = 0 AND ls_product-currency_code = ls_item-currency_code.
        ls_item-unit_price = ls_product-price.
      ENDIF.
    ENDIF.

    IF _check_item_immediate( EXPORTING is_item     = ls_item
                              CHANGING  ct_messages = ct_messages ) = abap_false.
      RETURN.
    ENDIF.

    ls_item-item_amount = ls_item-quantity * ls_item-unit_price.
    _put_item( is_item = ls_item iv_change = c_change-created ).
    es_item = ls_item.
  ENDMETHOD.

  METHOD _check_item_immediate.
    " 값만 보면 알 수 있는 싼 검사는 즉시 한다.
    " DB를 봐야 하는 비싼 검사(제품 존재 등)는 check_orders에서 한 번에 한다.
    rv_ok = abap_true.

    IF is_item-quantity <= 0.
      _add_message( EXPORTING iv_msgno     = '020'
                              iv_v2        = is_item-item_no
                              iv_order_id  = is_item-order_id
                              iv_item_no   = is_item-item_no
                              iv_fieldname = `QUANTITY`
                    CHANGING  ct_messages  = ct_messages ).
      rv_ok = abap_false.
    ENDIF.

    IF is_item-unit_price < 0.
      _add_message( EXPORTING iv_msgno     = '022'
                              iv_v2        = is_item-item_no
                              iv_order_id  = is_item-order_id
                              iv_item_no   = is_item-item_no
                              iv_fieldname = `UNIT_PRICE`
                    CHANGING  ct_messages  = ct_messages ).
      rv_ok = abap_false.
    ENDIF.
  ENDMETHOD.

  METHOD zif_leg_order_###~read_orders.
    DATA lt_ids TYPE SORTED TABLE OF zif_leg_order_###=>t_order_id WITH UNIQUE KEY table_line.
    DATA lt_db  TYPE SORTED TABLE OF zleg_ordh_### WITH UNIQUE KEY order_id.

    CLEAR: et_orders, et_items, et_messages.

    LOOP AT it_order_ids INTO DATA(lv_id).
      INSERT lv_id INTO TABLE lt_ids.          " 중복은 sy-subrc = 4로 무시됨
    ENDLOOP.
    CHECK lt_ids IS NOT INITIAL.

    " DB 헤더: 번호 개수와 상관없이 SELECT 한 번
    SELECT * FROM zleg_ordh_###
      FOR ALL ENTRIES IN @lt_ids
      WHERE order_id = @lt_ids-table_line
      INTO TABLE @lt_db.

    LOOP AT lt_ids INTO lv_id.
      READ TABLE ms_buffer-orders INTO DATA(ls_entry) WITH TABLE KEY order_id = lv_id.
      IF sy-subrc = 0.
        IF ls_entry-change = c_change-deleted.
          _add_message( EXPORTING iv_msgno = '002' iv_v1 = lv_id iv_order_id = lv_id
                        CHANGING  ct_messages = et_messages ).
        ELSE.
          APPEND CORRESPONDING #( ls_entry ) TO et_orders.
        ENDIF.
        CONTINUE.
      ENDIF.

      READ TABLE lt_db INTO DATA(ls_db) WITH TABLE KEY order_id = lv_id.
      IF sy-subrc = 0.
        APPEND ls_db TO et_orders.
      ELSE.
        _add_message( EXPORTING iv_msgno = '002' iv_v1 = lv_id iv_order_id = lv_id
                      CHANGING  ct_messages = et_messages ).
      ENDIF.
    ENDLOOP.

    IF iv_with_items = abap_true AND et_orders IS NOT INITIAL.
      et_items = _get_items_mass( VALUE #( FOR ls_o IN et_orders ( ls_o-order_id ) ) ).
    ENDIF.
  ENDMETHOD.

  METHOD zif_leg_order_###~draw_order_ids.
    CLEAR: et_ids, et_messages.
    _draw_final_numbers( EXPORTING iv_quantity = iv_quantity
                                   iv_floor    = iv_floor
                         IMPORTING et_ids      = et_ids
                         CHANGING  ct_messages = et_messages ).
  ENDMETHOD.
```

왜 이렇게 쓰나

- **스냅숏 방식의 전부 아니면 전무**: 공식 레거시는 "임시 버퍼(`mt_create_buffer_2`)에 먼저 쓰고 성공하면 `cud_copy`, 실패하면 `cud_disc`"로 같은 효과를 냅니다. 여기서는 버퍼 구조 전체를 값으로 복사해 두었다가 되돌립니다. 버퍼가 작을 때 가장 단순하고 확실한 방법입니다.
- early 모드에서 이미 뽑은 번호는 실패해도 되돌리지 않습니다. 번호 범위는 원래 "구멍(gap)"이 생길 수 있는 설계입니다.
- **즉시 검사와 저장 전 검사를 나눈 이유**: 수량이 0 이하인 것은 값만 보면 알 수 있으니 바로 거절합니다. 반면 "공급업체가 존재하는가", "납기일이 주문일보다 빠른가"는 (a) DB 조회가 필요하거나 (b) 두 필드를 따로따로 입력하는 중간 상태에서는 일시적으로 틀릴 수 있습니다. 이런 검사는 저장 직전에 버퍼 전체를 대상으로 한 번에 합니다(10단계 `check_orders`). R-06에서 이 둘이 각각 **핸들러의 즉시 오류**와 **`check_before_save`의 저장 거부**로 나뉘어 보이게 됩니다.
- `read_orders`는 RAP read 핸들러가 키 여러 개를 한꺼번에 넘겨줄 것을 대비한 "대량 읽기" API입니다. 공식 레거시의 `get_travel`은 한 건씩이라 RAP 핸들러가 키마다 함수를 부르지만, 루프 안 SELECT를 피하려면 이렇게 대량 API를 두는 편이 낫습니다.
- 단가 기본값 SELECT는 품목 하나를 만들 때 한 번 실행됩니다. 레거시 API가 품목 단위로 호출되는 구조라 어쩔 수 없는 부분이며, 대량 생성이 잦다면 `create_order`에서 제품 가격을 한꺼번에 읽어 넘기도록 바꾸면 됩니다.

</details>

#### 9단계. 변경·삭제·상태·잠금: `update_order`, `delete_order`, `set_status`, `lock_order`

요구사항

1. `update_order`
   - 주문 번호가 비었으면 001, 없으면 002, 상태가 `N`이 아니면 031(v1 주문, v2 상태).
   - 헤더: `is_orderx-_intx`에서 켜진 필드만 `_apply_flags`로 복사. 품목만 바뀌어도 **헤더 관리 필드(ETag)는 항상 갱신**합니다.
   - 품목: `it_itemsx`를 돌며 같은 인덱스의 `it_items` 행과 짝지어 액션 코드 C → `_create_item`, U → `_update_item`, D → `_delete_item`, 그 밖 → 006.
   - 시작 시 스냅숏, 오류면 되돌리기.
2. `_update_item`: 품목이 없으면 003. 켜진 필드만 복사, 즉시 검사, 금액 재계산, 버퍼 U.
3. `_delete_item`: 품목이 없으면 003, 있으면 버퍼 D(이번 세션 생성분이면 버퍼에서 제거).
4. `delete_order`: 001/002 검사, 상태가 `N` 또는 `R`이 아니면 032. 품목을 모두 D로, 헤더를 D로.
5. `set_status`: 없으면 002, 전이표에 없으면 030(v1 현재, v2 목표), 승인(`A`)인데 품목이 없으면 033. 성공하면 상태 변경 + 관리 필드 갱신.
6. `lock_order`: `cl_abap_lock_object_factory`로 `EZLEG_ORD_###`를 `ORDER_ID` 파라미터로 잠급니다. 다른 사용자가 잠갔으면(`cx_abap_foreign_lock`) 004(v1 주문, v2 사용자 이름), 그 밖의 잠금 기술 오류(`cx_abap_lock_failure`)는 `RAISE SHORTDUMP`.

**확인** 클래스가 활성화됩니다.

<details><summary>정답·해설</summary>

```abap
  METHOD zif_leg_order_###~update_order.
    CLEAR: es_order, et_items, et_messages.

    IF is_order-order_id IS INITIAL.
      _add_message( EXPORTING iv_msgno = '001' CHANGING ct_messages = et_messages ).
      RETURN.
    ENDIF.

    DATA(ls_snapshot) = ms_buffer.

    _find_order( EXPORTING iv_order_id = is_order-order_id
                 IMPORTING es_order    = DATA(ls_order)
                           ev_found    = DATA(lv_found) ).
    IF lv_found = abap_false.
      _add_message( EXPORTING iv_msgno = '002' iv_v1 = is_order-order_id iv_order_id = is_order-order_id
                    CHANGING  ct_messages = et_messages ).
      RETURN.
    ENDIF.

    IF ls_order-status <> zif_leg_order_###=>status-new.
      _add_message( EXPORTING iv_msgno    = '031'
                              iv_v1       = ls_order-order_id
                              iv_v2       = ls_order-status
                              iv_order_id = ls_order-order_id
                    CHANGING  ct_messages = et_messages ).
      RETURN.
    ENDIF.

    "--- 헤더: 플래그가 켜진 필드만 -------------------------------------
    DATA(ls_source) = CORRESPONDING zif_leg_order_###=>ts_order( is_order ).
    _apply_flags( EXPORTING is_source = ls_source
                            is_flags  = is_orderx-_intx
                  CHANGING  cs_target = ls_order ).
    " 품목만 바뀌어도 헤더 ETag는 갱신: 품목은 'etag dependent'(R-06)라 헤더 ETag가 BO 전체를 대표한다
    _set_admin( EXPORTING iv_new = abap_false CHANGING cs_order = ls_order ).
    _put_order( is_order = ls_order iv_change = c_change-updated ).

    "--- 품목: X 테이블의 액션 코드대로 ---------------------------------
    LOOP AT it_itemsx INTO DATA(ls_itemx).
      DATA(lv_index) = sy-tabix.
      DATA(ls_item_in) = VALUE zif_leg_order_###=>ts_item_in( ).
      READ TABLE it_items INTO ls_item_in INDEX lv_index.
      CLEAR es_order.   " (가독성용: 아래에서 다시 채운다)

      CASE ls_itemx-action_code.
        WHEN zif_leg_order_###=>action_code-create.
          ls_item_in-item_no = ls_itemx-item_no.
          _create_item( EXPORTING is_order    = ls_order
                                  is_item_in  = ls_item_in
                        IMPORTING es_item     = DATA(ls_item)
                        CHANGING  ct_messages = et_messages ).
          IF ls_item IS NOT INITIAL.
            APPEND ls_item TO et_items.
          ENDIF.

        WHEN zif_leg_order_###=>action_code-update.
          _update_item( EXPORTING iv_order_id = ls_order-order_id
                                  is_item_in  = ls_item_in
                                  is_itemx    = ls_itemx
                        IMPORTING es_item     = ls_item
                        CHANGING  ct_messages = et_messages ).
          IF ls_item IS NOT INITIAL.
            APPEND ls_item TO et_items.
          ENDIF.

        WHEN zif_leg_order_###=>action_code-delete.
          _delete_item( EXPORTING iv_order_id = ls_order-order_id
                                  iv_item_no  = ls_itemx-item_no
                        CHANGING  ct_messages = et_messages ).

        WHEN OTHERS.
          _add_message( EXPORTING iv_msgno    = '006'
                                  iv_v1       = ls_order-order_id
                                  iv_v2       = ls_itemx-item_no
                                  iv_v3       = ls_itemx-action_code
                                  iv_order_id = ls_order-order_id
                                  iv_item_no  = ls_itemx-item_no
                        CHANGING  ct_messages = et_messages ).
      ENDCASE.
      CLEAR ls_item.
    ENDLOOP.

    IF _has_error( et_messages ) = abap_true.
      ms_buffer = ls_snapshot.
      CLEAR: es_order, et_items.
      RETURN.
    ENDIF.

    es_order = ls_order.
  ENDMETHOD.

  METHOD _update_item.
    CLEAR es_item.

    DATA(lt_items) = _get_items_mass( VALUE #( ( iv_order_id ) ) ).
    READ TABLE lt_items INTO DATA(ls_item) WITH KEY item_no = is_itemx-item_no.
    IF sy-subrc <> 0.
      _add_message( EXPORTING iv_msgno    = '003'
                              iv_v1       = iv_order_id
                              iv_v2       = is_itemx-item_no
                              iv_order_id = iv_order_id
                              iv_item_no  = is_itemx-item_no
                    CHANGING  ct_messages = ct_messages ).
      RETURN.
    ENDIF.

    DATA(ls_source) = CORRESPONDING zif_leg_order_###=>ts_item( is_item_in ).
    _apply_flags( EXPORTING is_source = ls_source
                            is_flags  = is_itemx-_intx
                  CHANGING  cs_target = ls_item ).

    IF _check_item_immediate( EXPORTING is_item     = ls_item
                              CHANGING  ct_messages = ct_messages ) = abap_false.
      RETURN.
    ENDIF.

    ls_item-item_amount = ls_item-quantity * ls_item-unit_price.
    _put_item( is_item = ls_item iv_change = c_change-updated ).
    es_item = ls_item.
  ENDMETHOD.

  METHOD _delete_item.
    DATA(lt_items) = _get_items_mass( VALUE #( ( iv_order_id ) ) ).
    READ TABLE lt_items INTO DATA(ls_item) WITH KEY item_no = iv_item_no.
    IF sy-subrc <> 0.
      _add_message( EXPORTING iv_msgno    = '003'
                              iv_v1       = iv_order_id
                              iv_v2       = iv_item_no
                              iv_order_id = iv_order_id
                              iv_item_no  = iv_item_no
                    CHANGING  ct_messages = ct_messages ).
      RETURN.
    ENDIF.
    _put_item( is_item = ls_item iv_change = c_change-deleted ).
  ENDMETHOD.

  METHOD zif_leg_order_###~delete_order.
    CLEAR et_messages.

    IF iv_order_id IS INITIAL.
      _add_message( EXPORTING iv_msgno = '001' CHANGING ct_messages = et_messages ).
      RETURN.
    ENDIF.

    _find_order( EXPORTING iv_order_id = iv_order_id
                 IMPORTING es_order    = DATA(ls_order)
                           ev_found    = DATA(lv_found) ).
    IF lv_found = abap_false.
      _add_message( EXPORTING iv_msgno = '002' iv_v1 = iv_order_id iv_order_id = iv_order_id
                    CHANGING  ct_messages = et_messages ).
      RETURN.
    ENDIF.

    IF ls_order-status <> zif_leg_order_###=>status-new
    AND ls_order-status <> zif_leg_order_###=>status-rejected.
      _add_message( EXPORTING iv_msgno    = '032'
                              iv_v1       = iv_order_id
                              iv_v2       = ls_order-status
                              iv_order_id = iv_order_id
                    CHANGING  ct_messages = et_messages ).
      RETURN.
    ENDIF.

    " 하위 → 상위 순서로 삭제 표시 (DB에 있는 품목도 버퍼에 D로 올린다)
    LOOP AT _get_items_mass( VALUE #( ( iv_order_id ) ) ) INTO DATA(ls_item).
      _put_item( is_item = ls_item iv_change = c_change-deleted ).
    ENDLOOP.
    _put_order( is_order = ls_order iv_change = c_change-deleted ).
  ENDMETHOD.

  METHOD zif_leg_order_###~set_status.
    CLEAR: es_order, et_messages.

    _find_order( EXPORTING iv_order_id = iv_order_id
                 IMPORTING es_order    = DATA(ls_order)
                           ev_found    = DATA(lv_found) ).
    IF lv_found = abap_false.
      _add_message( EXPORTING iv_msgno = '002' iv_v1 = iv_order_id iv_order_id = iv_order_id
                    CHANGING  ct_messages = et_messages ).
      RETURN.
    ENDIF.

    IF _is_transition_allowed( iv_from = ls_order-status iv_to = iv_status ) = abap_false.
      _add_message( EXPORTING iv_msgno     = '030'
                              iv_v1        = ls_order-status
                              iv_v2        = iv_status
                              iv_order_id  = iv_order_id
                              iv_fieldname = `STATUS`
                    CHANGING  ct_messages  = et_messages ).
      RETURN.
    ENDIF.

    IF iv_status = zif_leg_order_###=>status-approved
    AND _get_items_mass( VALUE #( ( iv_order_id ) ) ) IS INITIAL.
      _add_message( EXPORTING iv_msgno = '033' iv_v1 = iv_order_id iv_order_id = iv_order_id
                    CHANGING  ct_messages = et_messages ).
      RETURN.
    ENDIF.

    ls_order-status = iv_status.
    _set_admin( EXPORTING iv_new = abap_false CHANGING cs_order = ls_order ).
    _put_order( is_order = ls_order iv_change = c_change-updated ).
    es_order = ls_order.
  ENDMETHOD.

  METHOD zif_leg_order_###~lock_order.
    CLEAR et_messages.

    " 임시 번호(9로 시작)는 아직 아무도 볼 수 없는 새 주문이므로 잠글 필요가 없다
    IF iv_order_id >= zif_leg_order_###=>late_numbering_boundary.
      RETURN.
    ENDIF.

    DATA(lv_order_id) = iv_order_id.
    TRY.
        DATA(lo_lock) = cl_abap_lock_object_factory=>get_instance( iv_name = 'EZLEG_ORD_###' ).
        lo_lock->enqueue(
          it_parameter = VALUE #( ( name = 'ORDER_ID' value = REF #( lv_order_id ) ) ) ).

      CATCH cx_abap_foreign_lock INTO DATA(lx_foreign_lock).
        " 업무 상황: 다른 사용자가 편집 중 → 메시지로 알린다
        _add_message( EXPORTING iv_msgno    = '004'
                                iv_v1       = iv_order_id
                                iv_v2       = lx_foreign_lock->user_name
                                iv_order_id = iv_order_id
                      CHANGING  ct_messages = et_messages ).

      CATCH cx_abap_lock_failure INTO DATA(lx_lock_failure).
        " 기술 오류(잠금 서버 문제 등): 계속하면 안 된다
        RAISE SHORTDUMP lx_lock_failure.
    ENDTRY.
  ENDMETHOD.
```

왜 이렇게 쓰나

- **X 구조의 의미**: `update_order( is_order = VALUE #( order_id = '1' note = '' ) is_orderx = VALUE #( order_id = '1' ) )`처럼 플래그가 모두 꺼져 있으면 메모는 **지워지지 않습니다**. "빈 값으로 바꾸기"와 "건드리지 않기"를 구분하는 유일한 방법이 플래그입니다. RAP의 `%control`이 정확히 같은 역할을 하므로 R-06에서는 `%control` → X 구조 변환만 하면 됩니다.
- **품목만 바꿔도 헤더 ETag 갱신**: R-06 BDEF에서 품목은 `etag dependent by _Order`입니다. 즉 "품목이 바뀌었는지"도 헤더의 ETag 하나로 판단합니다. 그래서 품목 변경이 헤더의 `local_last_changed_at`을 반드시 바꿔야 합니다. 이걸 빠뜨리면 두 사용자가 같은 주문의 품목을 동시에 바꿔도 충돌을 잡지 못합니다.
- **`lock_order`가 예외를 메시지로 바꾸는 기준**: `cx_abap_foreign_lock`은 "다른 사람이 쓰는 중"이라는 정상적인 업무 상황이라 메시지 004로 돌려줍니다(RAP에서는 `%fail-cause = locked`). 반면 `cx_abap_lock_failure`는 시스템 문제라 공식 RAP 예제(`/DMO/BP_TRAVEL_U`의 `lock`)처럼 `RAISE SHORTDUMP`로 멈춥니다.
- `REF #( iv_order_id )` 대신 지역 변수 `lv_order_id`의 참조를 넘긴 이유: 잠금 파라미터 표는 `REF TO data`를 받습니다. IMPORTING 파라미터 참조를 넘겨도 동작은 하겠지만 읽기 전용 데이터의 참조를 외부에 넘기는 것보다 지역 복사본이 명확합니다.
- 잠금은 별도의 해제 메서드가 없습니다. `cl_abap_lock_object_factory`의 enqueue는 기본 범위에서 트랜잭션이 끝날 때(COMMIT/ROLLBACK) 함께 풀리므로, RAP 트랜잭션과 수명이 같습니다.

</details>

#### 10단계. 저장 순서용 메서드: `check_orders`, `determine_totals`, `adjust_numbers`, `save`, `initialize`

요구사항

1. `check_orders` (버퍼 안의 생성/변경 주문·품목 전부, **DB 조회는 종류별로 한 번씩**)
   - 헤더: 요청자 필수(013, `REQUESTER`), 통화 필수(012, `CURRENCY_CODE`), 공급업체 존재(010, `SUPPLIER_ID`, `/DMO/AGENCY`), 납기일 ≥ 주문일(011, `DELIVERY_DATE`)
   - 품목: 단위 필수(021, `QUANTITY_UNIT`), 수량 > 0(020), 단가 > 0(022), 제품 존재(023, `PRODUCT_ID`, `/DMO/SUPPLEMENT`)
2. `determine_totals`: 버퍼의 생성/변경 주문마다 품목(버퍼+DB)을 모아 품목 통화를 헤더 통화로 맞추고 총액 = Σ 품목 금액. 총액이 달라졌을 때만 헤더를 버퍼에 다시 씁니다. 품목 조회는 SELECT 한 번.
3. `adjust_numbers`: 버퍼에서 임시 번호(≥ 9000000000)를 가진 생성 주문을 모아 최종 번호를 한꺼번에 뽑고, 헤더와 그 품목들의 키를 바꾼 뒤 매핑 두 개(주문, 품목)를 돌려줍니다. 이미 최종 번호를 가진 주문에 이번에 새로 생긴 품목은 번호가 그대로라도 "같은 번호 → 같은 번호" 매핑을 돌려줍니다(R-06에서 품목도 late numbering 엔터티이기 때문). 이 시점에는 되돌아갈 수 없으므로 번호를 못 받으면 `ASSERT`로 멈춥니다.
4. `save`: 임시 번호가 남아 있으면 `ASSERT`로 멈추고(adjust_numbers를 안 부른 것), C/U/D별로 모아 헤더·품목 테이블에 INSERT/UPDATE/DELETE. **COMMIT WORK는 하지 않습니다.** 끝나면 `initialize`.
5. `initialize`: 버퍼와 임시 번호 카운터 초기화.

**확인** 클래스 전체가 활성화됩니다(이제 빈 메서드가 없어야 합니다).

<details><summary>정답·해설</summary>

```abap
  METHOD zif_leg_order_###~check_orders.
    DATA lt_orders    TYPE zif_leg_order_###=>tt_order.
    DATA lt_items     TYPE zif_leg_order_###=>tt_item.
    DATA lt_suppliers TYPE SORTED TABLE OF /dmo/agency_id WITH UNIQUE KEY table_line.
    DATA lt_products  TYPE SORTED TABLE OF /dmo/supplement_id WITH UNIQUE KEY table_line.

    CLEAR et_messages.

    LOOP AT ms_buffer-orders INTO DATA(ls_order_entry) WHERE change <> c_change-deleted.
      APPEND CORRESPONDING #( ls_order_entry ) TO lt_orders.
      IF ls_order_entry-supplier_id IS NOT INITIAL.
        INSERT ls_order_entry-supplier_id INTO TABLE lt_suppliers.
      ENDIF.
    ENDLOOP.
    LOOP AT ms_buffer-items INTO DATA(ls_item_entry) WHERE change <> c_change-deleted.
      APPEND CORRESPONDING #( ls_item_entry ) TO lt_items.
      IF ls_item_entry-product_id IS NOT INITIAL.
        INSERT ls_item_entry-product_id INTO TABLE lt_products.
      ENDIF.
    ENDLOOP.

    "--- 마스터 존재 확인: 종류별 SELECT 한 번 --------------------------
    IF lt_suppliers IS NOT INITIAL.
      SELECT agency_id FROM /dmo/agency
        FOR ALL ENTRIES IN @lt_suppliers
        WHERE agency_id = @lt_suppliers-table_line
        INTO TABLE @DATA(lt_known_suppliers).
    ENDIF.
    IF lt_products IS NOT INITIAL.
      SELECT supplement_id FROM /dmo/supplement
        FOR ALL ENTRIES IN @lt_products
        WHERE supplement_id = @lt_products-table_line
        INTO TABLE @DATA(lt_known_products).
    ENDIF.

    "--- 헤더 ------------------------------------------------------------
    LOOP AT lt_orders INTO DATA(ls_order).
      IF ls_order-requester IS INITIAL.
        _add_message( EXPORTING iv_msgno = '013' iv_v1 = ls_order-order_id
                                iv_order_id = ls_order-order_id iv_fieldname = `REQUESTER`
                      CHANGING  ct_messages = et_messages ).
      ENDIF.
      IF ls_order-currency_code IS INITIAL.
        _add_message( EXPORTING iv_msgno = '012' iv_v1 = ls_order-order_id
                                iv_order_id = ls_order-order_id iv_fieldname = `CURRENCY_CODE`
                      CHANGING  ct_messages = et_messages ).
      ENDIF.
      IF ls_order-supplier_id IS INITIAL
      OR NOT line_exists( lt_known_suppliers[ agency_id = ls_order-supplier_id ] ).
        _add_message( EXPORTING iv_msgno = '010' iv_v1 = ls_order-supplier_id
                                iv_order_id = ls_order-order_id iv_fieldname = `SUPPLIER_ID`
                      CHANGING  ct_messages = et_messages ).
      ENDIF.
      IF ls_order-delivery_date IS NOT INITIAL
      AND ls_order-delivery_date < ls_order-order_date.
        _add_message( EXPORTING iv_msgno = '011' iv_v1 = ls_order-order_date iv_v2 = ls_order-delivery_date
                                iv_order_id = ls_order-order_id iv_fieldname = `DELIVERY_DATE`
                      CHANGING  ct_messages = et_messages ).
      ENDIF.
    ENDLOOP.

    "--- 품목 ------------------------------------------------------------
    LOOP AT lt_items INTO DATA(ls_item).
      IF ls_item-quantity_unit IS INITIAL.
        _add_message( EXPORTING iv_msgno = '021' iv_v2 = ls_item-item_no
                                iv_order_id = ls_item-order_id iv_item_no = ls_item-item_no
                                iv_fieldname = `QUANTITY_UNIT`
                      CHANGING  ct_messages = et_messages ).
      ENDIF.
      IF ls_item-quantity <= 0.
        _add_message( EXPORTING iv_msgno = '020' iv_v2 = ls_item-item_no
                                iv_order_id = ls_item-order_id iv_item_no = ls_item-item_no
                                iv_fieldname = `QUANTITY`
                      CHANGING  ct_messages = et_messages ).
      ENDIF.
      IF ls_item-unit_price <= 0.
        _add_message( EXPORTING iv_msgno = '022' iv_v2 = ls_item-item_no
                                iv_order_id = ls_item-order_id iv_item_no = ls_item-item_no
                                iv_fieldname = `UNIT_PRICE`
                      CHANGING  ct_messages = et_messages ).
      ENDIF.
      IF ls_item-product_id IS NOT INITIAL
      AND NOT line_exists( lt_known_products[ supplement_id = ls_item-product_id ] ).
        _add_message( EXPORTING iv_msgno = '023' iv_v1 = ls_item-product_id
                                iv_order_id = ls_item-order_id iv_item_no = ls_item-item_no
                                iv_fieldname = `PRODUCT_ID`
                      CHANGING  ct_messages = et_messages ).
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

  METHOD zif_leg_order_###~determine_totals.
    DATA lt_order_ids TYPE zif_leg_order_###=>tt_order_id.

    LOOP AT ms_buffer-orders INTO DATA(ls_entry) WHERE change <> c_change-deleted.
      APPEND ls_entry-order_id TO lt_order_ids.
    ENDLOOP.
    CHECK lt_order_ids IS NOT INITIAL.

    " 모든 관련 품목을 한 번에 (버퍼 + DB)
    DATA(lt_all_items) = _get_items_mass( lt_order_ids ).

    LOOP AT ms_buffer-orders INTO ls_entry WHERE change <> c_change-deleted.
      DATA(ls_order) = CORRESPONDING zif_leg_order_###=>ts_order( ls_entry ).
      ls_order-total_amount = 0.

      LOOP AT lt_all_items INTO DATA(ls_item) WHERE order_id = ls_order-order_id.
        " 헤더 통화가 바뀌었으면 품목 통화도 따라간다 (상향식 파생 전에 하향 동기화)
        IF ls_item-currency_code <> ls_order-currency_code.
          ls_item-currency_code = ls_order-currency_code.
          _put_item( is_item = ls_item iv_change = c_change-updated ).
        ENDIF.
        ls_order-total_amount = ls_order-total_amount + ls_item-item_amount.
      ENDLOOP.

      IF ls_order-total_amount <> ls_entry-total_amount.
        " 관리 필드(ETag)는 건드리지 않는다: 이미 변경 시점에 갱신되었다
        _put_order( is_order = ls_order iv_change = c_change-updated ).
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

  METHOD zif_leg_order_###~adjust_numbers.
    DATA lt_prelim      TYPE STANDARD TABLE OF ty_order_entry WITH EMPTY KEY.
    DATA lt_item_moves  TYPE STANDARD TABLE OF ty_item_entry WITH EMPTY KEY.
    DATA lt_messages    TYPE zif_leg_order_###=>tt_message.

    CLEAR: et_order_mapping, et_item_mapping.

    LOOP AT ms_buffer-orders INTO DATA(ls_entry)
         WHERE change = c_change-created
           AND order_id >= zif_leg_order_###=>late_numbering_boundary.
      APPEND ls_entry TO lt_prelim.
    ENDLOOP.

    IF lt_prelim IS NOT INITIAL.
      _draw_final_numbers( EXPORTING iv_quantity = lines( lt_prelim )
                           IMPORTING et_ids      = DATA(lt_final_ids)
                           CHANGING  ct_messages = lt_messages ).
      " 저장 후반(late save)은 되돌아갈 수 없는 지점이다. 번호를 못 받으면 계속할 방법이 없다.
      ASSERT lt_messages IS INITIAL.
    ENDIF.

    "--- 1) 임시 번호 주문 → 최종 번호 (헤더 + 그 품목) ------------------
    LOOP AT lt_prelim INTO ls_entry.
      DATA(lv_final) = lt_final_ids[ sy-tabix ].

      APPEND VALUE #( preliminary = ls_entry-order_id
                      final       = lv_final ) TO et_order_mapping.

      " 헤더 키 교체 (정렬 테이블이므로 지우고 다시 넣기)
      DELETE TABLE ms_buffer-orders WITH TABLE KEY order_id = ls_entry-order_id.
      DATA(ls_moved) = ls_entry.
      ls_moved-order_id = lv_final.
      INSERT ls_moved INTO TABLE ms_buffer-orders.

      " 품목 키 교체: 먼저 모으고, 지우고, 바꿔서 넣는다 (순회 중인 표를 바꾸지 않기 위해)
      CLEAR lt_item_moves.
      LOOP AT ms_buffer-items INTO DATA(ls_item_entry) WHERE order_id = ls_entry-order_id.
        APPEND ls_item_entry TO lt_item_moves.
      ENDLOOP.
      DELETE ms_buffer-items WHERE order_id = ls_entry-order_id.
      LOOP AT lt_item_moves INTO ls_item_entry.
        APPEND VALUE #( preliminary = VALUE #( order_id = ls_item_entry-order_id item_no = ls_item_entry-item_no )
                        final       = VALUE #( order_id = lv_final               item_no = ls_item_entry-item_no ) )
               TO et_item_mapping.
        ls_item_entry-order_id = lv_final.
        INSERT ls_item_entry INTO TABLE ms_buffer-items.
      ENDLOOP.
    ENDLOOP.

    "--- 2) 이미 최종 번호를 가진 주문에 이번에 새로 붙은 품목: a = a 매핑 ---
    " RAP에서 품목도 'late numbering' 엔터티이므로, 이번 트랜잭션에 생성된 품목은
    " 번호가 바뀌지 않더라도 전부 매핑을 돌려준다 (공식 /DMO/CL_FLIGHT_LEGACY와 같은 규칙).
    LOOP AT ms_buffer-items INTO DATA(ls_new_item) WHERE change = c_change-created.
      IF NOT line_exists( et_item_mapping[ final-order_id = ls_new_item-order_id
                                           final-item_no  = ls_new_item-item_no ] ).
        APPEND VALUE #( preliminary = VALUE #( order_id = ls_new_item-order_id item_no = ls_new_item-item_no )
                        final       = VALUE #( order_id = ls_new_item-order_id item_no = ls_new_item-item_no ) )
               TO et_item_mapping.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

  METHOD zif_leg_order_###~save.
    DATA: lt_ins_h TYPE STANDARD TABLE OF zleg_ordh_### WITH EMPTY KEY,
          lt_upd_h TYPE STANDARD TABLE OF zleg_ordh_### WITH EMPTY KEY,
          lt_del_h TYPE STANDARD TABLE OF zleg_ordh_### WITH EMPTY KEY,
          lt_ins_i TYPE STANDARD TABLE OF zleg_ordi_### WITH EMPTY KEY,
          lt_upd_i TYPE STANDARD TABLE OF zleg_ordi_### WITH EMPTY KEY,
          lt_del_i TYPE STANDARD TABLE OF zleg_ordi_### WITH EMPTY KEY.

    LOOP AT ms_buffer-orders INTO DATA(ls_order).
      " 임시 번호가 DB로 가면 안 된다. 여기서 멈추면 adjust_numbers를 부르지 않은 것이다.
      ASSERT ls_order-order_id < zif_leg_order_###=>late_numbering_boundary.
      CASE ls_order-change.
        WHEN c_change-created. APPEND CORRESPONDING #( ls_order ) TO lt_ins_h.
        WHEN c_change-updated. APPEND CORRESPONDING #( ls_order ) TO lt_upd_h.
        WHEN c_change-deleted. APPEND CORRESPONDING #( ls_order ) TO lt_del_h.
      ENDCASE.
    ENDLOOP.

    LOOP AT ms_buffer-items INTO DATA(ls_item).
      CASE ls_item-change.
        WHEN c_change-created. APPEND CORRESPONDING #( ls_item ) TO lt_ins_i.
        WHEN c_change-updated. APPEND CORRESPONDING #( ls_item ) TO lt_upd_i.
        WHEN c_change-deleted. APPEND CORRESPONDING #( ls_item ) TO lt_del_i.
      ENDCASE.
    ENDLOOP.

    " 상위 생성 → 하위 생성 → 변경 → 하위 삭제 → 상위 삭제
    INSERT zleg_ordh_### FROM TABLE @lt_ins_h.
    INSERT zleg_ordi_### FROM TABLE @lt_ins_i.
    UPDATE zleg_ordh_### FROM TABLE @lt_upd_h.
    UPDATE zleg_ordi_### FROM TABLE @lt_upd_i.
    DELETE zleg_ordi_### FROM TABLE @lt_del_i.
    DELETE zleg_ordh_### FROM TABLE @lt_del_h.

    " COMMIT WORK는 하지 않는다: 트랜잭션의 주인은 호출자(콘솔) 또는 RAP이다
    zif_leg_order_###~initialize( ).
  ENDMETHOD.

  METHOD zif_leg_order_###~initialize.
    CLEAR ms_buffer.
    mv_last_preliminary = zif_leg_order_###=>late_numbering_boundary.
  ENDMETHOD.
```

왜 이렇게 쓰나 (RAP 저장 순서와의 대응)

| 레거시 메서드 | R-06에서 부르는 RAP 세이버 메서드 | 저장 단계 | 실패해도 되나 |
|---|---|---|---|
| `determine_totals` | `finalize` | early save | 메시지를 낼 수는 있음(이 레거시는 내지 않음) |
| `check_orders` | `check_before_save` | early save | **예** — 여기서 실패하면 저장이 거부되고 상호작용 단계로 돌아감 |
| `adjust_numbers` | `adjust_numbers` | late save | **아니요** — 되돌릴 수 없는 지점 |
| `save` | `save` | late save | **아니요** |
| `initialize` | `cleanup` (그리고 ROLLBACK 시) | 마지막 | - |

- 치트시트 EML 문서는 저장 순서를 "early save phase(`finalize` → `check_before_save` → 실패 시 `cleanup_finalize`)"와 "late save phase(`adjust_numbers` → `save`) → `cleanup`"으로 설명하고, **late save phase에 들어간 뒤에는 상호작용 단계로 돌아갈 수 없다**고 강조합니다. 그래서 레거시 `adjust_numbers`/`save`는 메시지를 돌려주지 않고 `ASSERT`로 멈춥니다. 공식 레거시 `lcl_travel_buffer->adjust_numbers`/`save`도 똑같이 `ASSERT`를 씁니다.
- `check_orders`가 모든 검사 대상을 먼저 모은 다음 **마스터 테이블마다 SELECT 한 번**으로 끝내는 것이 "루프 안 SELECT 금지" 원칙의 전형적인 적용입니다.
- `determine_totals`가 헤더의 관리 필드를 바꾸지 않는 이유: 이 메서드는 RAP의 `finalize`, 즉 저장 직전에 불립니다. 이때 ETag를 바꾸면 사용자가 받은 응답의 ETag와 DB 값이 달라집니다(7단계 해설). 총액 변화의 원인이었던 품목 변경이 이미 ETag를 갱신했습니다.
- `save` 안에서 COMMIT WORK를 하지 않는 것이 RAP 연동의 핵심 규칙입니다. 치트시트 EML 문서의 "허용/금지 문장" 표에 따르면 RAP이 트랜잭션 주인일 때 핸들러·세이버 안의 `COMMIT WORK`/`ROLLBACK WORK`는 금지입니다. 레거시 `save`는 "DB에 쓰기만" 하고, 커밋은 RAP(`COMMIT ENTITIES`) 또는 레거시를 직접 쓰는 콘솔 프로그램이 합니다.

</details>

#### 11단계. 번호 범위 구간 + 데모 데이터 콘솔 클래스

요구사항

`ZCL_LEG_ORDER_SETUP_###`(인터페이스 `if_oo_adt_classrun`)를 만들어 F9로 실행하면 아래를 하도록 하세요.

1. 번호 범위 객체 `ZLEGORD###`에 구간 `01`(0000000001 ~ 8999999999)이 없으면 `cl_numberrange_intervals=>create`로 만듭니다. 번호 범위 객체가 없으면(`cx_nr_object_not_found`) 안내 문구를 출력하고 계속합니다.
2. 레거시 테이블 두 개를 비웁니다.
3. **레거시 API만으로** 주문 3건을 만듭니다(early 2건, late 1건).
   - 주문 A: 요청자 "Yurim", 공급업체 `/DMO/AGENCY` 첫 번째 ID, 통화 EUR, 품목 2개(제품은 `/DMO/SUPPLEMENT`에서 EUR 가격을 가진 앞의 두 건, 수량 2/5, 단위 `PC`)
   - 주문 B: 요청자 "Minsu", 품목 1개
   - 주문 C(late): 요청자 "Jisoo", 품목 1개
4. `determine_totals` → `check_orders`(메시지 출력) → 오류가 없으면 `adjust_numbers`(매핑 출력) → `save` → `COMMIT WORK`.
5. 주문 B를 승인(`set_status` A) 후 저장·커밋합니다.
6. 마지막으로 DB의 헤더/품목을 출력합니다.
7. 일부러 틀린 호출 하나를 넣어 메시지가 어떻게 나오는지 보세요: 존재하지 않는 공급업체 `999999`로 주문을 만들고 `check_orders`의 메시지 010을 출력한 뒤 `initialize`로 버리기.

**확인** 콘솔에 매핑(예: `9000000001 -> 0000000003`)과 DB 내용(주문 3건, 총액이 품목 합과 같음, 주문 B 상태 A)이 출력됩니다. 다시 실행해도 같은 결과(번호만 증가)가 나옵니다.

<details><summary>정답·해설</summary>

```abap
"! <p class="shorttext synchronized">Setup + demo data for legacy orders ###</p>
CLASS zcl_leg_order_setup_### DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_oo_adt_classrun.

  PRIVATE SECTION.
    CONSTANTS c_nr_object   TYPE cl_numberrange_runtime=>nr_object   VALUE 'ZLEGORD###'.
    CONSTANTS c_nr_interval TYPE cl_numberrange_runtime=>nr_interval VALUE '01'.

    METHODS ensure_number_range
      IMPORTING io_out TYPE REF TO if_oo_adt_classrun_out.

    METHODS write_messages
      IMPORTING io_out      TYPE REF TO if_oo_adt_classrun_out
                it_messages TYPE zif_leg_order_###=>tt_message.
ENDCLASS.

CLASS zcl_leg_order_setup_### IMPLEMENTATION.

  METHOD if_oo_adt_classrun~main.
    DATA(lo_legacy) = zcl_leg_order_###=>get_instance( ).

    "--- 1) 번호 범위 구간 ------------------------------------------------
    ensure_number_range( out ).

    "--- 2) 테이블 비우기 ---------------------------------------------------
    DELETE FROM zleg_ordi_###.
    DELETE FROM zleg_ordh_###.
    COMMIT WORK.
    lo_legacy->initialize( ).

    "--- 마스터 데이터 고르기 ----------------------------------------------
    SELECT agency_id FROM /dmo/agency ORDER BY agency_id INTO TABLE @DATA(lt_agencies) UP TO 2 ROWS.
    SELECT supplement_id, price FROM /dmo/supplement
      WHERE currency_code = 'EUR'
      ORDER BY supplement_id
      INTO TABLE @DATA(lt_products) UP TO 2 ROWS.
    IF lines( lt_agencies ) < 2 OR lines( lt_products ) < 2.
      out->write( `/DMO 데모 데이터가 없습니다. /DMO/CL_FLIGHT_DATA_GENERATOR를 먼저 실행하세요.` ).
      RETURN.
    ENDIF.

    "--- 3) 주문 3건 ---------------------------------------------------------
    lo_legacy->create_order(
      EXPORTING is_order = VALUE #( requester     = 'Yurim'
                                    supplier_id   = lt_agencies[ 1 ]-agency_id
                                    delivery_date = cl_abap_context_info=>get_system_date( ) + 14
                                    currency_code = 'EUR'
                                    note          = 'Office supplies' )
                it_items = VALUE #( ( product_id = lt_products[ 1 ]-supplement_id item_text = 'First product'
                                      quantity = 2 quantity_unit = 'PC' )
                                    ( product_id = lt_products[ 2 ]-supplement_id item_text = 'Second product'
                                      quantity = 5 quantity_unit = 'PC' ) )
                iv_numbering_mode = zif_leg_order_###=>numbering_mode-early
      IMPORTING es_order    = DATA(ls_order_a)
                et_messages = DATA(lt_messages) ).
    write_messages( io_out = out it_messages = lt_messages ).

    lo_legacy->create_order(
      EXPORTING is_order = VALUE #( requester     = 'Minsu'
                                    supplier_id   = lt_agencies[ 2 ]-agency_id
                                    currency_code = 'EUR' )
                it_items = VALUE #( ( product_id = lt_products[ 1 ]-supplement_id item_text = 'Single item'
                                      quantity = 10 quantity_unit = 'PC' ) )
      IMPORTING es_order    = DATA(ls_order_b)
                et_messages = lt_messages ).
    write_messages( io_out = out it_messages = lt_messages ).

    lo_legacy->create_order(
      EXPORTING is_order = VALUE #( requester     = 'Jisoo'
                                    supplier_id   = lt_agencies[ 1 ]-agency_id
                                    currency_code = 'EUR' )
                it_items = VALUE #( ( item_text = 'Manual price' quantity = 1 quantity_unit = 'PC' unit_price = '99.90' ) )
                iv_numbering_mode = zif_leg_order_###=>numbering_mode-late
      IMPORTING es_order    = DATA(ls_order_c)
                et_messages = lt_messages ).
    write_messages( io_out = out it_messages = lt_messages ).
    out->write( |생성: A={ ls_order_a-order_id } B={ ls_order_b-order_id } C(임시)={ ls_order_c-order_id }| ).

    "--- 4) 저장 순서를 손으로 재현 ------------------------------------------
    lo_legacy->determine_totals( ).
    lo_legacy->check_orders( IMPORTING et_messages = lt_messages ).
    IF lt_messages IS NOT INITIAL.
      write_messages( io_out = out it_messages = lt_messages ).
      lo_legacy->initialize( ).
      RETURN.
    ENDIF.
    lo_legacy->adjust_numbers( IMPORTING et_order_mapping = DATA(lt_order_map)
                                         et_item_mapping  = DATA(lt_item_map) ).
    LOOP AT lt_order_map INTO DATA(ls_map).
      out->write( |번호 매핑: { ls_map-preliminary } -> { ls_map-final }| ).
    ENDLOOP.
    out->write( |품목 매핑 { lines( lt_item_map ) }건| ).
    lo_legacy->save( ).
    COMMIT WORK.

    "--- 5) 주문 B 승인 --------------------------------------------------------
    lo_legacy->set_status( EXPORTING iv_order_id = ls_order_b-order_id
                                     iv_status   = zif_leg_order_###=>status-approved
                           IMPORTING et_messages = lt_messages ).
    write_messages( io_out = out it_messages = lt_messages ).
    lo_legacy->save( ).
    COMMIT WORK.

    "--- 7) 일부러 틀린 데이터: 저장 전 검사에서 걸린다 ---------------------
    lo_legacy->create_order(
      EXPORTING is_order = VALUE #( requester = 'Wrong' supplier_id = '999999' currency_code = 'EUR' )
                it_items = VALUE #( ( item_text = 'x' quantity = 1 quantity_unit = 'PC' unit_price = 1 ) )
      IMPORTING et_messages = lt_messages ).
    out->write( |잘못된 공급업체로 생성 호출 메시지 수: { lines( lt_messages ) } (즉시 검사는 통과)| ).
    lo_legacy->check_orders( IMPORTING et_messages = lt_messages ).
    out->write( `저장 전 검사 결과:` ).
    write_messages( io_out = out it_messages = lt_messages ).
    lo_legacy->initialize( ).   " 버리기: DB에는 아무 것도 가지 않는다

    "--- 6) 결과 ----------------------------------------------------------------
    SELECT * FROM zleg_ordh_### ORDER BY order_id INTO TABLE @DATA(lt_db_orders).
    SELECT * FROM zleg_ordi_### ORDER BY order_id, item_no INTO TABLE @DATA(lt_db_items).
    out->write( name = `ZLEG_ORDH_###` data = lt_db_orders ).
    out->write( name = `ZLEG_ORDI_###` data = lt_db_items ).
  ENDMETHOD.

  METHOD ensure_number_range.
    TRY.
        cl_numberrange_intervals=>read(
          EXPORTING object   = c_nr_object
          IMPORTING interval = DATA(lt_intervals) ).

        IF NOT line_exists( lt_intervals[ nrrangenr = c_nr_interval ] ).
          cl_numberrange_intervals=>create(
            EXPORTING interval = VALUE #( ( nrrangenr  = c_nr_interval
                                            fromnumber = '0000000001'
                                            tonumber   = '8999999999'
                                            procind    = 'I' ) )
                      object   = c_nr_object ).
          COMMIT WORK.
          io_out->write( `번호 범위 구간 01을 만들었습니다.` ).
        ELSE.
          io_out->write( `번호 범위 구간 01이 이미 있습니다.` ).
        ENDIF.

      CATCH cx_nr_object_not_found.
        io_out->write( `번호 범위 객체 ZLEGORD###가 없습니다. 5단계를 확인하거나 MAX+1 대체 경로를 쓰세요.` ).
      CATCH cx_number_ranges INTO DATA(lx_number_ranges).
        io_out->write( lx_number_ranges->get_text( ) ).
    ENDTRY.
  ENDMETHOD.

  METHOD write_messages.
    LOOP AT it_messages INTO DATA(ls_message).
      MESSAGE ID ls_message-msgid TYPE 'I' NUMBER ls_message-msgno
              WITH ls_message-msgv1 ls_message-msgv2 ls_message-msgv3 ls_message-msgv4
              INTO DATA(lv_text).
      io_out->write( |{ ls_message-msgty } { ls_message-msgno } [{ ls_message-order_id }/{ ls_message-item_no }/{ ls_message-fieldname }] { lv_text }| ).
    ENDLOOP.
  ENDMETHOD.

ENDCLASS.
```

왜 이렇게 쓰나

- 이 콘솔 클래스가 바로 **"RAP이 앞으로 대신 해 줄 일을 손으로 하는 프로그램"**입니다. R-06에서 RAP은 `determine_totals`(finalize) → `check_orders`(check_before_save) → `adjust_numbers` → `save` → `COMMIT WORK` → `initialize`(cleanup) 순서를 자동으로 지켜 줍니다. 순서를 직접 써 보면 세이버 메서드 각각이 왜 존재하는지 감이 옵니다.
- 이 콘솔은 RAP 바깥(트랜잭션 주인이 자기 자신)이므로 `COMMIT WORK`를 해도 됩니다. 같은 코드를 RAP 핸들러 안에 쓰면 안 됩니다.
- 번호 범위 구간 생성은 공식 `/DMO/CL_FLIGHT_DATA_GENERATOR=>reset_numberrange_interval`과 같은 API(`cl_numberrange_intervals=>read/create`, `procind = 'I'`)를 씁니다.
- `MESSAGE ... INTO`는 클라우드에서도 허용되는 형태(화면 출력 없이 텍스트만 얻기)입니다.

자주 나는 오류와 해결

- 실행 중 `ASSERT` 덤프(`_draw_final_numbers`가 메시지 040/041을 만든 뒤 `adjust_numbers`의 ASSERT): 번호 범위 구간이 없다는 뜻입니다. 콘솔 출력의 첫 줄을 확인하세요. 번호 범위 객체를 만들 수 없는 환경이면 7단계 클래스의 `mv_number_source` 초기값을 `c_number_source-max_plus_one`으로 바꾸세요.

</details>

#### 12단계. 레거시 클래스 ABAP Unit 테스트 (DB 대역)

요구사항

`ZCL_LEG_ORDER_###`의 **Test Classes** 탭에 테스트를 작성하세요.

1. 테스트 클래스 `ltc_leg_order`를 레거시 클래스의 `LOCAL FRIENDS`로 선언해, 테스트마다 **새 인스턴스**(`NEW zcl_leg_order_###( )`)를 만들고 번호 공급 방식을 MAX+1로 바꿉니다(번호 범위 객체 없이도 테스트가 돌도록).
2. `cl_osql_test_environment`로 `ZLEG_ORDH_###`, `ZLEG_ORDI_###`, `/DMO/AGENCY`, `/DMO/SUPPLEMENT`를 대역으로 바꾸고, 공급업체 `070001`, 제품 `TST-0001`(EUR 10.00)을 넣으세요.
3. 테스트 메서드 (각각 하나의 계약을 검증)
   - `create_early_gets_final_number`: DB에 주문 `0000000041`이 있을 때 early 생성 → `0000000042`
   - `create_late_and_adjust_numbers`: late 생성 → 임시 번호 ≥ 9000000000, `adjust_numbers` → 최종 번호와 품목 매핑, 버퍼에서 읽으면 최종 번호로 보임
   - `update_only_flagged_fields`: 플래그를 켠 필드만 바뀌고 나머지는 유지
   - `update_rejected_when_approved`: 상태 A 주문 변경 → 메시지 031, 버퍼 불변
   - `status_transition_rules`: N→C 금지(030), 품목 없는 N→A 금지(033)
   - `all_or_nothing_on_item_error`: 품목 수량 0으로 생성 → 메시지 020, 그 주문은 읽히지 않음
   - `check_orders_reports_fields`: 없는 공급업체 + 납기일 < 주문일 → 010(`SUPPLIER_ID`), 011(`DELIVERY_DATE`)
   - `determine_totals_sums_items`: 2×10.00 + 3×10.00 → 50.00
   - `save_writes_db_clears_buffer`: 저장 후 대역 DB에 행이 있고 버퍼가 비었음
   - `delete_created_leaves_no_trace`: 이번 세션에 만든 주문을 삭제하면 저장해도 DB에 아무것도 없음

**확인** Ctrl+Shift+F10으로 실행해 10개 테스트가 모두 초록색입니다. 일부러 `_put_order`의 "생성 후 삭제" 분기를 지워 보고 `delete_created_leaves_no_trace`가 빨개지는지 보세요.

<details><summary>정답·해설</summary>

```abap
*"* use this source file for your ABAP unit test classes
CLASS ltc_leg_order DEFINITION DEFERRED.
CLASS zcl_leg_order_### DEFINITION LOCAL FRIENDS ltc_leg_order.

CLASS ltc_leg_order DEFINITION FINAL FOR TESTING
  DURATION SHORT
  RISK LEVEL HARMLESS.

  PRIVATE SECTION.
    CLASS-DATA go_sql_env TYPE REF TO if_osql_test_environment.

    DATA mo_cut TYPE REF TO zcl_leg_order_###.     " 테스트 대상(구체 클래스: private 설정용)
    DATA mo_api TYPE REF TO zif_leg_order_###.     " 같은 객체를 API로 보기

    CONSTANTS c_supplier TYPE /dmo/agency_id     VALUE '070001'.
    CONSTANTS c_product  TYPE /dmo/supplement_id VALUE 'TST-0001'.

    CLASS-METHODS class_setup.
    CLASS-METHODS class_teardown.
    METHODS setup.
    METHODS teardown.

    METHODS valid_order RETURNING VALUE(rs_order) TYPE zif_leg_order_###=>ts_order_in.
    METHODS one_item    RETURNING VALUE(rt_items) TYPE zif_leg_order_###=>tt_item_in.

    METHODS create_early_gets_final_number   FOR TESTING.
    METHODS create_late_and_adjust_numbers   FOR TESTING.
    METHODS update_only_flagged_fields FOR TESTING.
    METHODS update_rejected_when_approved    FOR TESTING.
    METHODS status_transition_rules          FOR TESTING.
    METHODS all_or_nothing_on_item_error     FOR TESTING.
    METHODS check_orders_reports_fields      FOR TESTING.
    METHODS determine_totals_sums_items      FOR TESTING.
    METHODS save_writes_db_clears_buffer FOR TESTING.
    METHODS delete_created_leaves_no_trace FOR TESTING.
ENDCLASS.

CLASS ltc_leg_order IMPLEMENTATION.

  METHOD class_setup.
    go_sql_env = cl_osql_test_environment=>create(
                   i_dependency_list = VALUE #( ( 'ZLEG_ORDH_###' )
                                                ( 'ZLEG_ORDI_###' )
                                                ( '/DMO/AGENCY' )
                                                ( '/DMO/SUPPLEMENT' ) ) ).
  ENDMETHOD.

  METHOD class_teardown.
    go_sql_env->destroy( ).
  ENDMETHOD.

  METHOD setup.
    go_sql_env->clear_doubles( ).
    DATA lt_agencies  TYPE STANDARD TABLE OF /dmo/agency WITH EMPTY KEY.
    DATA lt_products  TYPE STANDARD TABLE OF /dmo/supplement WITH EMPTY KEY.
    lt_agencies = VALUE #( ( agency_id = c_supplier name = 'Test supplier' ) ).
    lt_products = VALUE #( ( supplement_id = c_product price = '10.00' currency_code = 'EUR' ) ).
    go_sql_env->insert_test_data( lt_agencies ).
    go_sql_env->insert_test_data( lt_products ).

    " 싱글턴을 쓰지 않고 매번 새 인스턴스: 테스트끼리 버퍼가 섞이지 않는다
    mo_cut = NEW zcl_leg_order_###( ).
    mo_cut->mv_number_source = zcl_leg_order_###=>c_number_source-max_plus_one.
    mo_api = mo_cut.
  ENDMETHOD.

  METHOD teardown.
    mo_api->initialize( ).
  ENDMETHOD.

  METHOD valid_order.
    rs_order = VALUE #( requester     = 'Tester'
                        supplier_id   = c_supplier
                        order_date    = '20260101'
                        delivery_date = '20260201'
                        currency_code = 'EUR' ).
  ENDMETHOD.

  METHOD one_item.
    rt_items = VALUE #( ( product_id = c_product quantity = 2 quantity_unit = 'PC' ) ).
  ENDMETHOD.

  METHOD create_early_gets_final_number.
    DATA lt_existing TYPE STANDARD TABLE OF zleg_ordh_### WITH EMPTY KEY.
    lt_existing = VALUE #( ( order_id = '0000000041' status = 'N' ) ).
    go_sql_env->insert_test_data( lt_existing ).

    mo_api->create_order( EXPORTING is_order          = valid_order( )
                                    iv_numbering_mode = zif_leg_order_###=>numbering_mode-early
                          IMPORTING es_order          = DATA(ls_order)
                                    et_messages       = DATA(lt_messages) ).

    cl_abap_unit_assert=>assert_initial( lt_messages ).
    cl_abap_unit_assert=>assert_equals( act = ls_order-order_id exp = '0000000042' ).
    cl_abap_unit_assert=>assert_equals( act = ls_order-status   exp = zif_leg_order_###=>status-new ).
    cl_abap_unit_assert=>assert_not_initial( ls_order-local_last_changed_at ).
  ENDMETHOD.

  METHOD create_late_and_adjust_numbers.
    mo_api->create_order( EXPORTING is_order          = valid_order( )
                                    it_items          = one_item( )
                                    iv_numbering_mode = zif_leg_order_###=>numbering_mode-late
                          IMPORTING es_order          = DATA(ls_order)
                                    et_items          = DATA(lt_items) ).

    cl_abap_unit_assert=>assert_true( xsdbool( ls_order-order_id >= zif_leg_order_###=>late_numbering_boundary ) ).
    cl_abap_unit_assert=>assert_equals( act = lt_items[ 1 ]-item_no exp = '0010' ).

    mo_api->adjust_numbers( IMPORTING et_order_mapping = DATA(lt_order_map)
                                      et_item_mapping  = DATA(lt_item_map) ).

    cl_abap_unit_assert=>assert_equals( act = lines( lt_order_map ) exp = 1 ).
    cl_abap_unit_assert=>assert_equals( act = lt_order_map[ 1 ]-preliminary exp = ls_order-order_id ).
    cl_abap_unit_assert=>assert_equals( act = lt_order_map[ 1 ]-final       exp = '0000000001' ).
    cl_abap_unit_assert=>assert_equals( act = lt_item_map[ 1 ]-final-order_id exp = '0000000001' ).
    cl_abap_unit_assert=>assert_equals( act = lt_item_map[ 1 ]-final-item_no  exp = '0010' ).

    " 이제 최종 번호로만 읽힌다
    mo_api->read_orders( EXPORTING it_order_ids = VALUE #( ( '0000000001' ) )
                         IMPORTING et_orders    = DATA(lt_orders)
                                   et_items     = DATA(lt_read_items) ).
    cl_abap_unit_assert=>assert_equals( act = lines( lt_orders )     exp = 1 ).
    cl_abap_unit_assert=>assert_equals( act = lines( lt_read_items ) exp = 1 ).
  ENDMETHOD.

  METHOD update_only_flagged_fields.
    mo_api->create_order( EXPORTING is_order = VALUE #( BASE valid_order( ) note = 'keep me' )
                          IMPORTING es_order = DATA(ls_created) ).

    DATA ls_orderx TYPE zif_leg_order_###=>ts_order_inx.
    ls_orderx-order_id             = ls_created-order_id.
    ls_orderx-_intx-delivery_date  = abap_true.          " 납기일만 바꾸겠다

    mo_api->update_order( EXPORTING is_order    = VALUE #( order_id      = ls_created-order_id
                                                           delivery_date = '20260315'
                                                           note          = '' )      " 플래그 꺼짐 → 무시
                                    is_orderx   = ls_orderx
                          IMPORTING es_order    = DATA(ls_updated)
                                    et_messages = DATA(lt_messages) ).

    cl_abap_unit_assert=>assert_initial( lt_messages ).
    cl_abap_unit_assert=>assert_equals( act = ls_updated-delivery_date exp = '20260315' ).
    cl_abap_unit_assert=>assert_equals( act = ls_updated-note          exp = 'keep me' ).
    cl_abap_unit_assert=>assert_equals( act = ls_updated-requester     exp = 'Tester' ).
  ENDMETHOD.

  METHOD update_rejected_when_approved.
    DATA lt_db_orders TYPE STANDARD TABLE OF zleg_ordh_### WITH EMPTY KEY.
    lt_db_orders = VALUE #( ( order_id = '0000000007' status = 'A' requester = 'Old' currency_code = 'EUR' ) ).
    go_sql_env->insert_test_data( lt_db_orders ).

    DATA ls_orderx TYPE zif_leg_order_###=>ts_order_inx.
    ls_orderx-order_id         = '0000000007'.
    ls_orderx-_intx-requester  = abap_true.

    mo_api->update_order( EXPORTING is_order    = VALUE #( order_id = '0000000007' requester = 'New' )
                                    is_orderx   = ls_orderx
                          IMPORTING et_messages = DATA(lt_messages) ).

    cl_abap_unit_assert=>assert_equals( act = lt_messages[ 1 ]-msgno exp = '031' ).
    mo_api->read_orders( EXPORTING it_order_ids = VALUE #( ( '0000000007' ) )
                         IMPORTING et_orders    = DATA(lt_orders) ).
    cl_abap_unit_assert=>assert_equals( act = lt_orders[ 1 ]-requester exp = 'Old' ).
  ENDMETHOD.

  METHOD status_transition_rules.
    mo_api->create_order( EXPORTING is_order = valid_order( )
                          IMPORTING es_order = DATA(ls_order) ).

    mo_api->set_status( EXPORTING iv_order_id = ls_order-order_id
                                  iv_status   = zif_leg_order_###=>status-completed
                        IMPORTING et_messages = DATA(lt_messages) ).
    cl_abap_unit_assert=>assert_equals( act = lt_messages[ 1 ]-msgno exp = '030' ).

    mo_api->set_status( EXPORTING iv_order_id = ls_order-order_id
                                  iv_status   = zif_leg_order_###=>status-approved
                        IMPORTING et_messages = lt_messages ).
    cl_abap_unit_assert=>assert_equals( act = lt_messages[ 1 ]-msgno exp = '033' ).

    mo_api->set_status( EXPORTING iv_order_id = ls_order-order_id
                                  iv_status   = zif_leg_order_###=>status-rejected
                        IMPORTING es_order    = DATA(ls_rejected)
                                  et_messages = lt_messages ).
    cl_abap_unit_assert=>assert_initial( lt_messages ).
    cl_abap_unit_assert=>assert_equals( act = ls_rejected-status exp = zif_leg_order_###=>status-rejected ).
  ENDMETHOD.

  METHOD all_or_nothing_on_item_error.
    mo_api->create_order( EXPORTING is_order          = valid_order( )
                                    it_items          = VALUE #( ( product_id = c_product quantity = 0 quantity_unit = 'PC' ) )
                                    iv_numbering_mode = zif_leg_order_###=>numbering_mode-late
                          IMPORTING es_order          = DATA(ls_order)
                                    et_messages       = DATA(lt_messages) ).

    cl_abap_unit_assert=>assert_equals( act = lt_messages[ 1 ]-msgno     exp = '020' ).
    cl_abap_unit_assert=>assert_equals( act = lt_messages[ 1 ]-fieldname exp = `QUANTITY` ).
    cl_abap_unit_assert=>assert_initial( ls_order ).
    " 헤더도 버퍼에 남지 않아야 한다
    cl_abap_unit_assert=>assert_initial( mo_cut->ms_buffer-orders ).
  ENDMETHOD.

  METHOD check_orders_reports_fields.
    mo_api->create_order( EXPORTING is_order = VALUE #( BASE valid_order( )
                                                        supplier_id   = '999999'
                                                        delivery_date = '20251231' )   " 주문일 20260101보다 이전
                          IMPORTING et_messages = DATA(lt_create_messages) ).
    cl_abap_unit_assert=>assert_initial( lt_create_messages ).    " 즉시 검사는 통과

    mo_api->check_orders( IMPORTING et_messages = DATA(lt_messages) ).

    cl_abap_unit_assert=>assert_true( xsdbool( line_exists( lt_messages[ msgno = '010' fieldname = `SUPPLIER_ID` ] ) ) ).
    cl_abap_unit_assert=>assert_true( xsdbool( line_exists( lt_messages[ msgno = '011' fieldname = `DELIVERY_DATE` ] ) ) ).
  ENDMETHOD.

  METHOD determine_totals_sums_items.
    mo_api->create_order( EXPORTING is_order = valid_order( )
                                    it_items = VALUE #( ( product_id = c_product quantity = 2 quantity_unit = 'PC' )
                                                        ( product_id = c_product quantity = 3 quantity_unit = 'PC' ) )
                          IMPORTING es_order = DATA(ls_order)
                                    et_items = DATA(lt_items) ).
    " 단가 기본값이 제품 가격(10.00 EUR)에서 왔는지
    cl_abap_unit_assert=>assert_equals( act = lt_items[ 1 ]-unit_price exp = '10.00' ).

    mo_api->determine_totals( ).

    mo_api->read_orders( EXPORTING it_order_ids = VALUE #( ( ls_order-order_id ) )
                         IMPORTING et_orders    = DATA(lt_orders) ).
    cl_abap_unit_assert=>assert_equals( act = lt_orders[ 1 ]-total_amount exp = '50.00' ).
  ENDMETHOD.

  METHOD save_writes_db_clears_buffer.
    mo_api->create_order( EXPORTING is_order = valid_order( )
                                    it_items = one_item( )
                          IMPORTING es_order = DATA(ls_order) ).
    mo_api->determine_totals( ).
    mo_api->adjust_numbers( ).
    mo_api->save( ).

    SELECT COUNT(*) FROM zleg_ordh_### WHERE order_id = @ls_order-order_id INTO @DATA(lv_headers).
    SELECT COUNT(*) FROM zleg_ordi_### WHERE order_id = @ls_order-order_id INTO @DATA(lv_items).
    cl_abap_unit_assert=>assert_equals( act = lv_headers exp = 1 ).
    cl_abap_unit_assert=>assert_equals( act = lv_items   exp = 1 ).
    cl_abap_unit_assert=>assert_initial( mo_cut->ms_buffer ).
  ENDMETHOD.

  METHOD delete_created_leaves_no_trace.
    mo_api->create_order( EXPORTING is_order = valid_order( )
                                    it_items = one_item( )
                          IMPORTING es_order = DATA(ls_order) ).
    mo_api->delete_order( EXPORTING iv_order_id = ls_order-order_id
                          IMPORTING et_messages = DATA(lt_messages) ).
    cl_abap_unit_assert=>assert_initial( lt_messages ).
    cl_abap_unit_assert=>assert_initial( mo_cut->ms_buffer ).

    mo_api->save( ).
    SELECT COUNT(*) FROM zleg_ordh_### INTO @DATA(lv_headers).
    cl_abap_unit_assert=>assert_equals( act = lv_headers exp = 0 ).
  ENDMETHOD.

ENDCLASS.
```

왜 이렇게 쓰나

- `CLASS zcl_leg_order_### DEFINITION LOCAL FRIENDS ltc_leg_order.`는 **테스트 클래스에게만** private 영역(생성자, `mv_number_source`, `ms_buffer`)을 열어 줍니다. 운영 코드에는 테스트용 공개 메서드를 하나도 추가하지 않았습니다.
- 싱글턴(`get_instance`)을 쓰지 않고 `NEW`로 만드는 이유: 싱글턴은 테스트 메서드 사이에 버퍼가 남아 서로 영향을 줍니다. 테스트 격리의 기본입니다.
- `cl_osql_test_environment`는 지정한 테이블에 대한 ABAP SQL을 **테스트 대역 테이블**로 돌려 보냅니다. 그래서 `save`가 실제로 INSERT를 해도 진짜 테이블은 바뀌지 않고, 테스트 끝의 `destroy`로 사라집니다. RAP400 연습의 테스트 클래스도 같은 API를 씁니다.
- 테스트 이름이 곧 레거시의 "계약 목록"입니다. R-06에서 RAP이 이 계약(전부 아니면 전무, 버퍼 우선 읽기, 임시 번호, 매핑)에 기대어 동작하므로, 레거시를 고칠 때 이 테스트가 RAP 쪽 회귀를 막아 줍니다.

클래스 구조 해설 (R-05 전체)

| 구성 | 위치 | 언제 불리나 |
|---|---|---|
| `get_instance` | 공개 정적 메서드 | 콘솔, RAP behavior pool이 레거시를 얻을 때 |
| `ZIF_LEG_ORDER_###~*` | 인터페이스 구현 | 외부 호출자(콘솔, R-06의 핸들러/세이버) |
| `_find_order`, `_get_items_mass` | private | 모든 읽기/변경 전: 버퍼 → DB 순서 보장 |
| `_put_order`, `_put_item` | private | 모든 변경: C/U/D 표시 규칙 한곳에 모음 |
| `_set_admin` | private | 생성·변경·상태 변경 순간 (ETag 갱신) |
| `_draw_final_numbers` | private | early 생성, `adjust_numbers`, `draw_order_ids` |
| 테스트 클래스 `ltc_leg_order` | Test Classes 탭 | ADT의 ABAP Unit 실행 시 |

</details>

### R-06. Unmanaged BO로 레거시 감싸기: 핸들러·세이버 전 메서드 구현 [작성] ★★★
<!-- covers: unmanaged implementation, strict(2), late numbering, %cid, %cid_ref, %tmp, %key, %tky, mapped/failed/reported, %fail-cause, %element, %msg, %global, mapping for ... control, CORRESPONDING MAPPING FROM ENTITY USING CONTROL, MAPPING TO ENTITY, X 구조 변환, create, update, delete, read, lock, read by association, create by association, cl_abap_lock_object_factory, RAISE SHORTDUMP, action result $self, factory action, MODIFY ENTITIES IN LOCAL MODE, READ ENTITIES IN LOCAL MODE, instance feature control(%update/%delete/%action/%assoc/%field), global authorization, instance authorization, four-eyes 원칙, etag master, etag dependent, lock master/dependent, authorization dependent, saver finalize/check_before_save/adjust_numbers/save/cleanup/cleanup_finalize, 예외 클래스 if_abap_behv_message + if_t100_dyn_msg, 계산 필드(Criticality), 프로젝션 BDEF use etag, 서비스 정의/바인딩, Fiori Elements, OData ETag(If-Match) 충돌 확인, EML 콘솔, COMMIT ENTITIES RESPONSE OF, ROLLBACK ENTITIES -->
**목표**

- unmanaged BO의 핸들러 메서드(create, update, delete, read, lock, rba, cba, action, factory action, features, authorizations)를 **빠짐없이** 직접 구현할 수 있습니다.
- 세이버 메서드 6개(finalize, check_before_save, adjust_numbers, save, cleanup, cleanup_finalize)가 언제 불리는지 알고, 레거시 API의 어느 메서드와 짝지어야 하는지 설명할 수 있습니다.
- `%control` ↔ X 구조, `%cid`/`%cid_ref`, late numbering의 임시 키와 `%tmp`, mapped/failed/reported를 레거시 메시지 테이블과 정확히 연결할 수 있습니다.
- `mapping for ... control ...`과 `CORRESPONDING ... MAPPING FROM ENTITY [USING CONTROL]` / `MAPPING TO ENTITY`로 필드 매핑 코드를 없앨 수 있습니다.
- Fiori Elements 미리보기와 EML 콘솔로 생성·변경·삭제·액션·잠금·ETag 충돌·저장 거부를 직접 확인할 수 있습니다.

**전제**

- R-05를 끝내서 `ZLEG_ORDH_###`, `ZLEG_ORDI_###`, `ZLEG_S_ORDH_X_###`, `ZLEG_S_ORDI_X_###`, `ZLEG_MSG_###`, `EZLEG_ORD_###`, `ZLEGORD###`, `ZIF_LEG_ORDER_###`, `ZCL_LEG_ORDER_###`가 활성화되어 있고, `ZCL_LEG_ORDER_SETUP_###`를 한 번 실행해 데모 주문이 몇 건 들어 있습니다.
- 표준 객체 `/DMO/I_Agency`, `/DMO/I_Agency_StdVH`, `/DMO/I_Supplement`, `/DMO/I_Supplement_StdVH`, `I_Currency`, `I_CurrencyStdVH`, `I_UnitOfMeasure`를 사용합니다(트라이얼 시스템에 모두 있습니다).
- 이 문제의 BO는 **draft가 없는** unmanaged BO입니다. draft는 R-07에서 붙입니다.

**만들 객체**

| 순서 | 객체 유형 | 이름 | 역할 |
|---|---|---|---|
| 1 | 클래스(예외) | `ZCM_LEG_ORDER_###` | 레거시 메시지 한 줄을 RAP 메시지(`if_abap_behv_message`)로 감싸는 범용 예외 클래스 |
| 2 | 클래스 | `ZCL_RAP_ORDER_AUX_###` | 메시지 → `%fail-cause`, DB 필드 이름 → CDS 요소 이름, 상태 → Criticality 변환 |
| 3 | CDS 루트 뷰 엔터티 | `ZRAP_R_ORDER_U_###` | 주문 헤더 (BO 루트) |
| 4 | CDS 뷰 엔터티 | `ZRAP_R_ORDITEM_U_###` | 주문 품목 (자식) |
| 5 | CDS 프로젝션 뷰 | `ZRAP_C_ORDER_U_###`, `ZRAP_C_ORDITEM_U_###` | UI용 프로젝션 |
| 6 | 메타데이터 확장 | `ZRAP_C_ORDER_U_###`, `ZRAP_C_ORDITEM_U_###` | UI 어노테이션 |
| 7 | 행동 정의 | `ZRAP_R_ORDER_U_###` | unmanaged BDEF |
| 8 | 행동 정의 | `ZRAP_C_ORDER_U_###` | 프로젝션 BDEF |
| 9 | 클래스(행동 풀) | `ZBP_RAP_R_ORDER_U_###` | 핸들러 `lhc_order`, `lhc_item` + 세이버 `lsc_zrap_r_order_u_###` |
| 10 | 서비스 정의 / 바인딩 | `ZRAP_UI_ORDER_U_###` / `ZRAP_UI_ORDER_U_O4_###` | OData V4 UI 서비스 |
| 11 | 클래스 | `ZCL_RAP_ORDER_U_EML_###` | EML 콘솔로 BO 전체 동작 확인 |

> **왜 R-02의 `ZCM_RAP_###`를 쓰지 않나요?** `ZCM_RAP_###`는 메시지 클래스 `ZRAP_MSG_###`의 메시지마다 상수(textid)를 하나씩 두는 방식입니다. 이 문제의 메시지는 **레거시가 런타임에 돌려주는** `ZLEG_MSG_###`의 아무 번호나 될 수 있으므로, 메시지 클래스·번호·변수를 그대로 받아 감싸는 범용 클래스 `ZCM_LEG_ORDER_###`를 따로 만듭니다. 구조(`CX_STATIC_CHECK` 상속 + `IF_ABAP_BEHV_MESSAGE` + `IF_T100_DYN_MSG`)는 `ZCM_RAP_###`와 같습니다.

#### 1단계. 메시지 예외 클래스와 보조 클래스 만들기

요구사항

1. 예외 클래스 `ZCM_LEG_ORDER_###`
   - `CX_STATIC_CHECK`를 상속하고 `IF_T100_DYN_MSG`, `IF_T100_MESSAGE`, `IF_ABAP_BEHV_MESSAGE`를 구현합니다.
   - 읽기 전용 속성 `v1`~`v4`(TYPE `symsgv`)를 두고, T100 키의 `attr1`~`attr4`가 `'V1'`~`'V4'`를 가리키게 해서 메시지의 `&1`~`&4`가 채워지게 합니다.
   - 생성자 파라미터: `textid`, `previous`, `severity`(기본값 error), `v1`~`v4`.
   - 정적 메서드 `from_legacy( is_message TYPE zif_leg_order_###=>ts_message )`: 레거시 메시지 한 줄을 받아 인스턴스를 만들어 돌려줍니다. 메시지 유형 E/A → error, W → warning, I → information, S → success.
2. 보조 클래스 `ZCL_RAP_ORDER_AUX_###` (정적 메서드만)
   - `get_fail_cause( is_message, iv_dependent )`: 메시지 번호 001·002·003 → `cause-not_found`(단, `iv_dependent = abap_true`이면 `cause-dependency`), 004 → `cause-locked`, 005·007 → `cause-conflict`, 050·051 → `cause-unauthorized`, 나머지 → `cause-unspecific`.
   - `is_error( is_message )`: 유형이 E 또는 A이면 `abap_true`.
   - `get_element_name( iv_fieldname )`: 레거시 DB 필드 이름(`DELIVERY_DATE`)을 CDS 요소 이름(`DELIVERYDATE`)으로 바꿉니다. 이 BO의 CDS 별칭은 "DB 이름에서 밑줄을 뺀 CamelCase"로 짓기로 약속합니다.
   - `get_status_criticality( iv_status )`: A·C → 3(녹색), R → 1(빨강), 그 밖 → 2(노랑). 반환 타입은 `int1`.

**확인** 두 클래스가 활성화됩니다. `ZCM_LEG_ORDER_###=>from_legacy( VALUE #( msgty = 'E' msgid = 'ZLEG_MSG_###' msgno = '002' msgv1 = '42' ) )->if_message~get_text( )`를 임시 콘솔 코드에서 출력하면 `Order 42 does not exist.`가 나옵니다.

<details><summary>정답·해설</summary>

```abap
"! <p class="shorttext synchronized">Legacy order message as RAP message ###</p>
"! 레거시 메시지(메시지 클래스 + 번호 + 변수 4개)를 그대로 감싸는 범용 RAP 메시지.
CLASS zcm_leg_order_### DEFINITION
  PUBLIC
  INHERITING FROM cx_static_check
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_t100_dyn_msg.        " 동적 T100 메시지 (msgty/msgv1..4 포함)
    INTERFACES if_t100_message.        " T100 키 (msgid, msgno, attr1..4)
    INTERFACES if_abap_behv_message.   " RAP이 %msg로 받아 주는 인터페이스 (m_severity)

    DATA v1 TYPE symsgv READ-ONLY.
    DATA v2 TYPE symsgv READ-ONLY.
    DATA v3 TYPE symsgv READ-ONLY.
    DATA v4 TYPE symsgv READ-ONLY.

    METHODS constructor
      IMPORTING textid   LIKE if_t100_message=>t100key OPTIONAL
                previous TYPE REF TO cx_root OPTIONAL
                severity TYPE if_abap_behv_message=>t_severity DEFAULT if_abap_behv_message=>severity-error
                v1       TYPE symsgv OPTIONAL
                v2       TYPE symsgv OPTIONAL
                v3       TYPE symsgv OPTIONAL
                v4       TYPE symsgv OPTIONAL.

    "! 레거시 메시지 한 줄 → RAP 메시지 객체
    CLASS-METHODS from_legacy
      IMPORTING is_message        TYPE zif_leg_order_###=>ts_message
      RETURNING VALUE(ro_message) TYPE REF TO zcm_leg_order_###.

  PROTECTED SECTION.
  PRIVATE SECTION.
ENDCLASS.

CLASS zcm_leg_order_### IMPLEMENTATION.

  METHOD constructor ##ADT_SUPPRESS_GENERATION.
    super->constructor( previous = previous ).

    CLEAR me->textid.
    IF textid IS INITIAL.
      if_t100_message~t100key = if_t100_message=>default_textid.
    ELSE.
      if_t100_message~t100key = textid.
    ENDIF.

    if_abap_behv_message~m_severity = severity.

    me->v1 = v1.
    me->v2 = v2.
    me->v3 = v3.
    me->v4 = v4.
  ENDMETHOD.

  METHOD from_legacy.
    DATA(lv_severity) = SWITCH if_abap_behv_message=>t_severity( is_message-msgty
                          WHEN 'E' OR 'A' THEN if_abap_behv_message=>severity-error
                          WHEN 'W'        THEN if_abap_behv_message=>severity-warning
                          WHEN 'I'        THEN if_abap_behv_message=>severity-information
                          WHEN 'S'        THEN if_abap_behv_message=>severity-success
                          ELSE                 if_abap_behv_message=>severity-none ).

    ro_message = NEW zcm_leg_order_###(
                   textid   = VALUE #( msgid = is_message-msgid
                                       msgno = is_message-msgno
                                       attr1 = 'V1'            " &1 ← 속성 V1
                                       attr2 = 'V2'
                                       attr3 = 'V3'
                                       attr4 = 'V4' )
                   severity = lv_severity
                   v1       = is_message-msgv1
                   v2       = is_message-msgv2
                   v3       = is_message-msgv3
                   v4       = is_message-msgv4 ).

    " IF_T100_DYN_MSG의 원래 메시지 유형도 남겨 둔다(테스트에서 확인용)
    ro_message->if_t100_dyn_msg~msgty = is_message-msgty.
  ENDMETHOD.

ENDCLASS.
```

```abap
"! <p class="shorttext synchronized">Helpers for unmanaged order BO ###</p>
CLASS zcl_rap_order_aux_### DEFINITION
  PUBLIC
  FINAL
  CREATE PRIVATE.

  PUBLIC SECTION.
    "! 레거시 메시지 → failed의 %fail-cause
    "! @parameter iv_dependent | 부모 때문에 실패한 자식(예: 부모 주문이 없어서 품목 생성 실패)이면 abap_true
    CLASS-METHODS get_fail_cause
      IMPORTING is_message      TYPE zif_leg_order_###=>ts_message
                iv_dependent    TYPE abap_bool DEFAULT abap_false
      RETURNING VALUE(rv_cause) TYPE if_abap_behv=>t_fail_cause.

    CLASS-METHODS is_error
      IMPORTING is_message      TYPE zif_leg_order_###=>ts_message
      RETURNING VALUE(rv_error) TYPE abap_bool.

    "! 'DELIVERY_DATE' → 'DELIVERYDATE' (%element의 컴포넌트 이름)
    CLASS-METHODS get_element_name
      IMPORTING iv_fieldname      TYPE string
      RETURNING VALUE(rv_element) TYPE string.

    "! 0 = 회색, 1 = 빨강, 2 = 노랑, 3 = 녹색 (UI.lineItem criticality 규칙)
    CLASS-METHODS get_status_criticality
      IMPORTING iv_status             TYPE zif_leg_order_###=>t_status
      RETURNING VALUE(rv_criticality) TYPE int1.

  PROTECTED SECTION.
  PRIVATE SECTION.
ENDCLASS.

CLASS zcl_rap_order_aux_### IMPLEMENTATION.

  METHOD get_fail_cause.
    rv_cause = if_abap_behv=>cause-unspecific.

    IF is_message-msgid <> zif_leg_order_###=>message_class.
      RETURN.
    ENDIF.

    CASE is_message-msgno.
      WHEN '001' OR '002' OR '003'.        " 키 없음 / 주문 없음 / 품목 없음
        rv_cause = COND #( WHEN iv_dependent = abap_true
                           THEN if_abap_behv=>cause-dependency
                           ELSE if_abap_behv=>cause-not_found ).
      WHEN '004'.                          " 다른 사용자가 잠금
        rv_cause = if_abap_behv=>cause-locked.
      WHEN '005' OR '007'.                 " 번호 중복
        rv_cause = if_abap_behv=>cause-conflict.
      WHEN '050' OR '051'.                 " 권한
        rv_cause = if_abap_behv=>cause-unauthorized.
    ENDCASE.
  ENDMETHOD.

  METHOD is_error.
    rv_error = xsdbool( is_message-msgty = 'E' OR is_message-msgty = 'A' ).
  ENDMETHOD.

  METHOD get_element_name.
    " 약속: CDS 별칭 = DB 필드 이름에서 밑줄만 뺀 것 (대소문자 무시)
    rv_element = to_upper( replace( val = iv_fieldname sub = `_` with = `` occ = 0 ) ).
  ENDMETHOD.

  METHOD get_status_criticality.
    rv_criticality = SWITCH #( iv_status
                       WHEN zif_leg_order_###=>status-approved
                         OR zif_leg_order_###=>status-completed THEN 3
                       WHEN zif_leg_order_###=>status-rejected  THEN 1
                       ELSE 2 ).
  ENDMETHOD.

ENDCLASS.
```

왜 이렇게 쓰나

- RAP 응답의 `%msg`는 `if_abap_behv_message` 타입 참조입니다. 이 인터페이스는 `if_t100_dyn_msg`(→ `if_t100_message`)를 포함하므로, T100 키(`msgid`/`msgno`/`attr1~4`)와 **변수 값을 담은 속성**(`V1`~`V4`)만 있으면 화면에 문장이 만들어집니다. openSAP 예제 `ZCM_RAP_####`의 생성자 패턴(`CLEAR me->textid`, `if_t100_message~t100key`, `if_abap_behv_message~m_severity`)을 그대로 따랐습니다.
- 공식 `/DMO/BP_TRAVEL_U`는 핸들러의 `new_message( id = ... number = ... severity = ... v1 = ... )`로 메시지를 만듭니다. 이 방법도 됩니다. 다만 `new_message`는 핸들러/세이버 인스턴스 메서드라 **보조 클래스나 레거시 쪽에서는 쓸 수 없고**, 이 문제집의 규격(예외 클래스 기반 메시지)에도 맞지 않아 예외 클래스로 감쌌습니다.
- `get_fail_cause`는 공식 `/DMO/CL_TRAVEL_AUXILIARY=>get_cause_from_message`와 같은 역할입니다. **`%fail-cause`는 OData 응답 코드를 정합니다.** `not_found` → 404, `locked` → 409(또는 423), `unauthorized` → 403, `conflict` → 409, `unspecific` → 400 계열로 바뀌어 Fiori가 알맞은 문구를 보여 줍니다(정확한 HTTP 코드 대응은 실제 시스템에서 확인 필요).
- `dependency`는 "내 잘못이 아니라 **부모가 실패해서** 나도 실패"라는 뜻입니다. 부모 주문이 없는데 품목을 만들려 한 경우 품목 쪽 failed에 씁니다.
- `get_element_name`처럼 이름 규칙으로 변환하면 필드가 늘어나도 코드가 안 바뀝니다. 대신 2단계에서 CDS 별칭을 반드시 규칙대로 지어야 합니다.

</details>

#### 2단계. 인터페이스(R) CDS 뷰 2개 만들기

요구사항

1. 루트 뷰 엔터티 `ZRAP_R_ORDER_U_###` (`define root view entity ... as select from zleg_ordh_###`)
   - 필드(별칭은 DB 이름에서 밑줄을 뺀 CamelCase): `OrderID`(키), `Requester`, `SupplierID`, `OrderDate`, `DeliveryDate`, `TotalAmount`, `CurrencyCode`, `Status`, `Note`, `CreatedBy`, `CreatedAt`, `LastChangedBy`, `LocalLastChangedAt`, `LastChangedAt`.
   - 계산 필드 `StatusCriticality`: `case`로 A·C → 3, R → 1, 그 밖 → 2. (1단계의 `get_status_criticality`와 같은 규칙)
   - 컴포지션 `_Items` → `ZRAP_R_ORDITEM_U_###` (0..*), 연관 `_Supplier` → `/DMO/I_Agency`, `_Currency` → `I_Currency`.
2. 자식 뷰 엔터티 `ZRAP_R_ORDITEM_U_###` (`as select from zleg_ordi_###`)
   - 필드: `OrderID`, `ItemNo`(둘 다 키), `ProductID`, `ItemText`, `Quantity`, `QuantityUnit`, `UnitPrice`, `ItemAmount`, `CurrencyCode`.
   - `association to parent ZRAP_R_ORDER_U_### as _Order`, 연관 `_Product` → `/DMO/I_Supplement`.
3. 두 뷰는 서로를 참조하므로 **먼저 둘 다 저장한 다음** 함께 활성화하세요(Ctrl+Shift+F3, 모두 활성화).

**직접 추가할 어노테이션**

- `@AccessControl.authorizationCheck` — 이 뷰에 DCL 접근 제어를 걸지 여부
- `@EndUserText.label` — 뷰 설명
- `@Metadata.ignorePropagatedAnnotations` — 아래 계층(테이블/연관 뷰)에서 넘어오는 어노테이션을 무시할지
- `@Semantics.amount.currencyCode` — 금액 필드가 어느 통화 필드를 따르는지 (TotalAmount, UnitPrice, ItemAmount)
- `@Semantics.quantity.unitOfMeasure` — 수량 필드가 어느 단위 필드를 따르는지
- `@Semantics.user.createdBy`, `@Semantics.systemDateTime.createdAt` — 생성자/생성 시각 필드 표시
- `@Semantics.user.localInstanceLastChangedBy`, `@Semantics.systemDateTime.localInstanceLastChangedAt` — 인스턴스 최종 변경자/변경 시각(ETag 후보) 표시
- `@Semantics.systemDateTime.lastChangedAt` — 전체 최종 변경 시각(R-07의 total ETag 후보) 표시

**확인** 두 뷰가 활성화되고, 루트 뷰에서 F8(Data Preview)을 누르면 R-05에서 만든 주문이 보이며 `StatusCriticality` 열이 상태에 따라 1·2·3으로 나옵니다. 품목 뷰 Data Preview에서 `_Order` 연관을 따라가 볼 수 있습니다.

<details><summary>정답·해설</summary>

```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED          // DCL 없이 공개 (실습용)
@EndUserText.label: 'Purchase order (unmanaged) ###'      // 뷰 설명
@Metadata.ignorePropagatedAnnotations: true               // 테이블 쪽 어노테이션 상속 안 함
define root view entity ZRAP_R_ORDER_U_###
  as select from zleg_ordh_###

  composition [0..*] of ZRAP_R_ORDITEM_U_### as _Items     // BO 안의 자식: 같이 잠기고 같이 지워진다

  association [0..1] to /DMO/I_Agency as _Supplier
    on $projection.SupplierID = _Supplier.AgencyID
  association [0..1] to I_Currency    as _Currency
    on $projection.CurrencyCode = _Currency.Currency
{
  key order_id              as OrderID,
      requester             as Requester,
      supplier_id           as SupplierID,
      order_date            as OrderDate,
      delivery_date         as DeliveryDate,

      @Semantics.amount.currencyCode: 'CurrencyCode'      // TotalAmount의 통화 = CurrencyCode
      total_amount          as TotalAmount,
      currency_code         as CurrencyCode,

      status                as Status,

      // 계산 필드: DB에 없음. read 핸들러에서도 같은 값을 채워야 한다(6·7단계)
      case status
        when 'A' then 3
        when 'C' then 3
        when 'R' then 1
        else 2
      end                   as StatusCriticality,

      note                  as Note,

      @Semantics.user.createdBy: true                     // 생성자
      created_by            as CreatedBy,
      @Semantics.systemDateTime.createdAt: true           // 생성 시각
      created_at            as CreatedAt,
      @Semantics.user.localInstanceLastChangedBy: true    // 이 인스턴스의 최종 변경자
      last_changed_by       as LastChangedBy,
      @Semantics.systemDateTime.localInstanceLastChangedAt: true  // 이 인스턴스의 최종 변경 시각 → etag master
      local_last_changed_at as LocalLastChangedAt,
      @Semantics.systemDateTime.lastChangedAt: true       // BO 전체 최종 변경 시각 → R-07 total etag
      last_changed_at       as LastChangedAt,

      /* Associations */
      _Items,
      _Supplier,
      _Currency
}
```

```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Purchase order item (unmanaged) ###'
@Metadata.ignorePropagatedAnnotations: true
define view entity ZRAP_R_ORDITEM_U_###
  as select from zleg_ordi_###

  association to parent ZRAP_R_ORDER_U_### as _Order        // 컴포지션의 역방향: 부모
    on $projection.OrderID = _Order.OrderID
  association [0..1] to /DMO/I_Supplement  as _Product
    on $projection.ProductID = _Product.SupplementID
{
  key order_id      as OrderID,
  key item_no       as ItemNo,
      product_id    as ProductID,
      item_text     as ItemText,

      @Semantics.quantity.unitOfMeasure: 'QuantityUnit'   // 수량의 단위 = QuantityUnit
      quantity      as Quantity,
      quantity_unit as QuantityUnit,

      @Semantics.amount.currencyCode: 'CurrencyCode'
      unit_price    as UnitPrice,
      @Semantics.amount.currencyCode: 'CurrencyCode'
      item_amount   as ItemAmount,
      currency_code as CurrencyCode,

      /* Associations */
      _Order,
      _Product
}
```

왜 이렇게 쓰나

- **unmanaged에서 CDS 뷰의 역할**: OData 목록 조회(`GET .../PurchaseOrder`)와 필터·정렬·검색은 **CDS 뷰를 SQL로 직접 읽습니다**. 반면 생성·변경 직후 응답, 액션 결과, EML `READ ENTITIES`는 **read 핸들러**(7단계)를 거칩니다. 그래서 계산 필드 `StatusCriticality`는 CDS(목록용)와 read 핸들러(트랜잭션용) **두 곳**에서 같은 규칙으로 만들어야 합니다. 보조 클래스의 `get_status_criticality`가 그 "두 번째 사본"입니다.
- `@Semantics.systemDateTime.*` / `@Semantics.user.*`: managed BO에서는 이 어노테이션을 보고 프레임워크가 값을 **자동으로 채웁니다**. unmanaged에서는 아무도 대신 채워 주지 않으므로 R-05 레거시의 `_set_admin`이 채웁니다. 그래도 어노테이션을 다는 이유는 (1) OData 메타데이터에 의미가 실리고 (2) 생성 마법사·Fiori가 관리 필드로 인식하며 (3) R-07에서 draft로 바꿀 때 필요하기 때문입니다(→ 어노테이션 탭: `@Semantics.systemDateTime.localInstanceLastChangedAt`).
- 별칭 규칙(밑줄 제거)을 지켰기 때문에 1단계 `get_element_name( 'DELIVERY_DATE' )` = `DELIVERYDATE`가 `%element-DeliveryDate`의 컴포넌트 이름과 맞습니다.
- `association to parent`가 있어야 BDEF에서 `lock dependent by _Order` 같은 문장을 쓸 수 있습니다.

자주 나는 오류와 해결

- "ZRAP_R_ORDITEM_U_### does not exist" (루트 뷰만 먼저 활성화할 때): 두 뷰를 모두 저장한 뒤 함께 활성화하세요.
- `@Semantics.amount.currencyCode` 누락 시 테이블 쪽 참조와 달라 경고가 납니다. 금액 필드 3개 모두 달았는지 확인하세요.

</details>

#### 3단계. 프로젝션 뷰 2개와 메타데이터 확장 2개 만들기

요구사항

1. 프로젝션 루트 뷰 `ZRAP_C_ORDER_U_###` (`provider contract transactional_query`, `as projection on ZRAP_R_ORDER_U_###`)
   - R 뷰의 필드를 모두 노출하고, `_Supplier.Name as SupplierName`을 추가합니다.
   - `_Items`는 `redirected to composition child ZRAP_C_ORDITEM_U_###`로 바꿉니다.
   - 값 도움말: `SupplierID` → `/DMO/I_Agency_StdVH`(`AgencyID`), `CurrencyCode` → `I_CurrencyStdVH`(`Currency`).
2. 프로젝션 뷰 `ZRAP_C_ORDITEM_U_###`
   - `_Product._SupplementText[1: LanguageCode = $session.system_language].Description as ProductText` 추가.
   - `_Order`는 `redirected to parent ZRAP_C_ORDER_U_###`.
   - 값 도움말: `ProductID` → `/DMO/I_Supplement_StdVH`(`SupplementID`), `QuantityUnit` → `I_UnitOfMeasure`(`UnitOfMeasure`).
3. 메타데이터 확장(MDE) 두 개 (`@Metadata.layer: #CORE`)
   - 주문 목록: OrderID, Requester, SupplierID, OrderDate, DeliveryDate, TotalAmount, Status(색 표시). 선택 필드: OrderID, Requester, SupplierID, Status.
   - 주문 상세: 일반 정보 섹션(identification) + 품목 표 섹션(lineItem 참조) + 관리 정보 섹션(fieldGroup).
   - 액션 버튼 3개: 목록과 상세에 `approveOrder`(Approve), `rejectOrder`(Reject), `copyOrder`(Copy).
   - 품목 표: ItemNo, ProductID, ItemText, Quantity, UnitPrice, ItemAmount.

**직접 추가할 어노테이션**

- `@Metadata.allowExtensions` — 이 뷰에 MDE를 붙일 수 있게 허용
- `@Search.searchable` / `@Search.defaultSearchElement` — 검색창(전체 텍스트 검색) 활성화와 검색 대상 필드
- `@Consumption.valueHelpDefinition` — 필드 값 도움말(F4)과 `useForValidation`(입력값 검증)
- `@ObjectModel.text.element` — 코드 필드 옆에 보여 줄 텍스트 필드
- `@Metadata.layer` — MDE의 계층(우선순위)
- `@UI.headerInfo` — 상세 화면 제목·목록 이름
- `@UI.facet` — 상세 화면의 섹션 구성
- `@UI.lineItem` — 목록 열, `criticality`로 색, `type: #FOR_ACTION`으로 버튼
- `@UI.identification` — 상세 화면 "일반 정보" 필드, `#FOR_ACTION` 버튼
- `@UI.fieldGroup` — 섹션 안 필드 묶음
- `@UI.selectionField` — 목록 위 필터 막대
- `@UI.hidden` — 화면에서 숨김
- `@UI.textArrangement` — 코드와 텍스트를 어떻게 함께 보여 줄지

**확인** 네 객체가 활성화됩니다. (Fiori 미리보기는 11단계 서비스 바인딩 뒤에 가능합니다.)

<details><summary>정답·해설</summary>

```cds
@EndUserText.label: 'Purchase order (unmanaged) - projection ###'
@AccessControl.authorizationCheck: #NOT_REQUIRED
@Metadata.allowExtensions: true                         // MDE 허용
@Search.searchable: true                                // 검색창 활성화
define root view entity ZRAP_C_ORDER_U_###
  provider contract transactional_query                 // 트랜잭션 UI용 프로젝션
  as projection on ZRAP_R_ORDER_U_###
{
  key OrderID,

      @Search.defaultSearchElement: true                // 검색 대상
      Requester,

      @Consumption.valueHelpDefinition: [{ entity: { name: '/DMO/I_Agency_StdVH', element: 'AgencyID' },
                                           useForValidation: true }]   // F4 + 입력값 검증
      @ObjectModel.text.element: ['SupplierName']       // 번호 옆에 이름
      @Search.defaultSearchElement: true
      SupplierID,
      _Supplier.Name as SupplierName,

      OrderDate,
      DeliveryDate,
      TotalAmount,

      @Consumption.valueHelpDefinition: [{ entity: { name: 'I_CurrencyStdVH', element: 'Currency' },
                                           useForValidation: true }]
      CurrencyCode,

      Status,
      StatusCriticality,
      Note,
      CreatedBy,
      CreatedAt,
      LastChangedBy,
      LocalLastChangedAt,
      LastChangedAt,

      /* Associations */
      _Items : redirected to composition child ZRAP_C_ORDITEM_U_###,
      _Supplier,
      _Currency
}
```

```cds
@EndUserText.label: 'Purchase order item (unmanaged) - projection ###'
@AccessControl.authorizationCheck: #NOT_REQUIRED
@Metadata.allowExtensions: true
define view entity ZRAP_C_ORDITEM_U_###
  as projection on ZRAP_R_ORDITEM_U_###
{
  key OrderID,
  key ItemNo,

      @Consumption.valueHelpDefinition: [{ entity: { name: '/DMO/I_Supplement_StdVH', element: 'SupplementID' },
                                           useForValidation: true }]
      @ObjectModel.text.element: ['ProductText']
      ProductID,
      _Product._SupplementText[1: LanguageCode = $session.system_language].Description as ProductText,

      ItemText,
      Quantity,

      @Consumption.valueHelpDefinition: [{ entity: { name: 'I_UnitOfMeasure', element: 'UnitOfMeasure' } }]
      QuantityUnit,

      UnitPrice,
      ItemAmount,
      CurrencyCode,

      /* Associations */
      _Order : redirected to parent ZRAP_C_ORDER_U_###,
      _Product
}
```

```cds
@Metadata.layer: #CORE                                   // 기본 계층
@UI.headerInfo: { typeName: 'Purchase Order',
                  typeNamePlural: 'Purchase Orders',
                  title:       { type: #STANDARD, value: 'OrderID' },
                  description: { type: #STANDARD, value: 'Requester' } }
annotate entity ZRAP_C_ORDER_U_### with
{
  @UI.facet: [ { id: 'General',   purpose: #STANDARD, type: #IDENTIFICATION_REFERENCE,
                 label: 'General Information', position: 10 },
               { id: 'Items',     purpose: #STANDARD, type: #LINEITEM_REFERENCE,
                 label: 'Items', position: 20, targetElement: '_Items' },
               { id: 'Admin',     purpose: #STANDARD, type: #FIELDGROUP_REFERENCE,
                 label: 'Administrative Data', position: 30, targetQualifier: 'Admin' } ]

  @UI: { lineItem:       [ { position: 10, importance: #HIGH },
                           { type: #FOR_ACTION, dataAction: 'approveOrder', label: 'Approve' },
                           { type: #FOR_ACTION, dataAction: 'rejectOrder',  label: 'Reject' },
                           { type: #FOR_ACTION, dataAction: 'copyOrder',    label: 'Copy' } ],
         identification: [ { position: 10 },
                           { type: #FOR_ACTION, dataAction: 'approveOrder', label: 'Approve' },
                           { type: #FOR_ACTION, dataAction: 'rejectOrder',  label: 'Reject' },
                           { type: #FOR_ACTION, dataAction: 'copyOrder',    label: 'Copy' } ],
         selectionField: [ { position: 10 } ] }
  OrderID;

  @UI: { lineItem:       [ { position: 20, importance: #HIGH } ],
         identification: [ { position: 20 } ],
         selectionField: [ { position: 20 } ] }
  Requester;

  @UI: { lineItem:       [ { position: 30, importance: #HIGH } ],
         identification: [ { position: 30 } ],
         selectionField: [ { position: 30 } ],
         textArrangement: #TEXT_LAST }                  // "070001 (Sunshine Travel)"처럼
  SupplierID;

  @UI.hidden: true
  SupplierName;

  @UI: { lineItem:       [ { position: 40 } ],
         identification: [ { position: 40 } ] }
  OrderDate;

  @UI: { lineItem:       [ { position: 50 } ],
         identification: [ { position: 50 } ] }
  DeliveryDate;

  @UI: { lineItem:       [ { position: 60, importance: #HIGH } ],
         identification: [ { position: 60 } ] }
  TotalAmount;

  @UI.identification: [ { position: 65 } ]
  CurrencyCode;

  @UI: { lineItem:       [ { position: 70, importance: #HIGH, criticality: 'StatusCriticality' } ],
         identification: [ { position: 70, criticality: 'StatusCriticality' } ],
         selectionField: [ { position: 40 } ] }
  Status;

  @UI.hidden: true
  StatusCriticality;

  @UI.identification: [ { position: 80, label: 'Note' } ]
  Note;

  @UI.fieldGroup: [ { qualifier: 'Admin', position: 10 } ]
  CreatedBy;
  @UI.fieldGroup: [ { qualifier: 'Admin', position: 20 } ]
  CreatedAt;
  @UI.fieldGroup: [ { qualifier: 'Admin', position: 30 } ]
  LastChangedBy;
  @UI.fieldGroup: [ { qualifier: 'Admin', position: 40 } ]
  LocalLastChangedAt;
  @UI.hidden: true
  LastChangedAt;
}
```

```cds
@Metadata.layer: #CORE
@UI.headerInfo: { typeName: 'Item',
                  typeNamePlural: 'Items',
                  title: { type: #STANDARD, value: 'ItemNo' } }
annotate entity ZRAP_C_ORDITEM_U_### with
{
  @UI.facet: [ { id: 'Item', purpose: #STANDARD, type: #IDENTIFICATION_REFERENCE,
                 label: 'Item', position: 10 } ]

  @UI: { lineItem: [ { position: 10, importance: #HIGH } ], identification: [ { position: 10 } ] }
  ItemNo;

  @UI: { lineItem: [ { position: 20, importance: #HIGH } ], identification: [ { position: 20 } ],
         textArrangement: #TEXT_LAST }
  ProductID;

  @UI.hidden: true
  ProductText;

  @UI: { lineItem: [ { position: 30 } ], identification: [ { position: 30 } ] }
  ItemText;

  @UI: { lineItem: [ { position: 40, importance: #HIGH } ], identification: [ { position: 40 } ] }
  Quantity;

  @UI: { lineItem: [ { position: 50 } ], identification: [ { position: 50 } ] }
  UnitPrice;

  @UI: { lineItem: [ { position: 60, importance: #HIGH } ], identification: [ { position: 60 } ] }
  ItemAmount;
}
```

왜 이렇게 쓰나

- `provider contract transactional_query`: 이 프로젝션이 "트랜잭션 BO 위의 UI용 쿼리"임을 선언합니다. 이 계약이 있어야 프로젝션 BDEF(4단계)를 만들 수 있습니다.
- `_Supplier.Name as SupplierName`처럼 **연관 경로로 읽는 필드는 프로젝션에만** 두었습니다. 이 필드는 RAP 트랜잭션 버퍼(레거시)에 없으므로 R 뷰에 두면 read 핸들러가 채워야 할 필드가 늘어납니다. 프로젝션의 경로 필드는 OData 레이어가 읽어 줍니다(공식 `/DMO/C_Travel_U`의 `_Agency.Name as AgencyName`과 같은 방식).
- `useForValidation: true`: Fiori가 값 도움말 목록에 없는 값을 입력하면 저장 전에 경고합니다. 그래도 **서버 쪽 검사(레거시 `check_orders` 010)는 반드시 있어야 합니다.** EML이나 API로 들어오는 요청은 UI 검증을 거치지 않기 때문입니다.
- 액션 버튼은 `lineItem`(목록 위 표 도구 모음)과 `identification`(상세 화면 머리글) 두 군데에 둡니다(→ 어노테이션 탭: `@UI.lineItem`의 `#FOR_ACTION`).

</details>

#### 4단계. unmanaged 행동 정의(BDEF)와 프로젝션 BDEF 만들기

요구사항

1. 루트 뷰 `ZRAP_R_ORDER_U_###`에서 오른쪽 클릭 > New Behavior Definition, 구현 유형 **Unmanaged**로 만드세요.
2. 머리글: `unmanaged implementation in class zbp_rap_r_order_u_### unique;`, `strict ( 2 );`
3. 주문(`alias Order`)
   - `late numbering`, `lock master`, `authorization master ( global, instance )`, `etag master LocalLastChangedAt`
   - `create;`, `update ( features : instance );`, `delete ( features : instance );`
   - 읽기 전용: `OrderID`, `Status`, `TotalAmount`, `StatusCriticality`, 관리 필드 5개
   - 필수: `Requester`, `SupplierID`
   - 동적 필드 제어: `CurrencyCode` (품목이 있으면 읽기 전용)
   - `association _Items { create ( features : instance, authorization : update ); }`
   - 액션: `approveOrder`, `rejectOrder` (둘 다 `features : instance`, `result [1] $self`), 인스턴스 팩토리 액션 `copyOrder [1]`
   - `mapping for zleg_ordh_### control zleg_s_ordh_x_###` 블록
4. 품목(`alias Item`)
   - `late numbering`, `lock dependent by _Order`, `authorization dependent by _Order`, `etag dependent by _Order`
   - `update ( features : instance );`, `delete ( features : instance );`
   - 읽기 전용: `OrderID`, `ItemNo`, `ItemAmount`, `CurrencyCode` / 필수: `Quantity`, `QuantityUnit`
   - `association _Order;`
   - `mapping for zleg_ordi_### control zleg_s_ordi_x_###` 블록
5. 프로젝션 BDEF `ZRAP_C_ORDER_U_###`(`projection; strict ( 2 );`): 두 엔터티 모두 `use etag`, 주문은 create/update/delete/액션 3개/`use association _Items { create; }`, 품목은 update/delete/`use association _Order;`.
6. 아직 행동 풀이 없으므로 활성화하면 "class does not exist" 오류가 납니다. 다음 단계에서 퀵픽스로 만듭니다.

**확인** 두 BDEF를 저장했을 때 남는 오류가 "구현 클래스 없음" 하나뿐입니다.

<details><summary>정답·해설</summary>

```bdef
unmanaged implementation in class zbp_rap_r_order_u_### unique; // 전체 BO의 행동 풀 하나
strict ( 2 );                                                   // 최신 엄격 문법 검사

define behavior for ZRAP_R_ORDER_U_### alias Order
late numbering                                   // 최종 OrderID는 저장 직전 adjust_numbers에서
lock master                                      // 잠금의 주인 = 주문. lock 핸들러를 직접 구현
authorization master ( global, instance )        // 전역 + 인스턴스 권한 핸들러를 직접 구현
etag master LocalLastChangedAt                   // 낙관적 잠금 필드
{
  create;
  update ( features : instance );                // 상태가 N일 때만 변경 가능 (핸들러가 판단)
  delete ( features : instance );                // 상태가 N 또는 R일 때만 삭제 가능

  field ( readonly ) OrderID, Status, TotalAmount, StatusCriticality,
                     CreatedBy, CreatedAt, LastChangedBy, LocalLastChangedAt, LastChangedAt;
  field ( mandatory ) Requester, SupplierID;
  field ( features : instance ) CurrencyCode;     // 품목이 생기면 읽기 전용

  association _Items { create ( features : instance, authorization : update ); }

  action ( features : instance ) approveOrder result [1] $self;
  action ( features : instance ) rejectOrder  result [1] $self;
  factory action copyOrder [1];                  // 인스턴스에 묶인 팩토리 액션: 새 주문 1건

  mapping for zleg_ordh_### control zleg_s_ordh_x_###
  {
    OrderID            = order_id;
    Requester          = requester;
    SupplierID         = supplier_id;
    OrderDate          = order_date;
    DeliveryDate       = delivery_date;
    TotalAmount        = total_amount;
    CurrencyCode       = currency_code;
    Status             = status;
    Note               = note;
    CreatedBy          = created_by;
    CreatedAt          = created_at;
    LastChangedBy      = last_changed_by;
    LocalLastChangedAt = local_last_changed_at;
    LastChangedAt      = last_changed_at;
  }
}

define behavior for ZRAP_R_ORDITEM_U_### alias Item
late numbering                                   // 부모 OrderID가 바뀌므로 품목 키도 저장 때 바뀐다
lock dependent by _Order                         // 잠금은 부모 주문으로
authorization dependent by _Order                // 권한도 부모 주문으로
etag dependent by _Order                         // ETag도 부모 주문 것을 사용
{
  update ( features : instance );
  delete ( features : instance );

  field ( readonly ) OrderID, ItemNo, ItemAmount, CurrencyCode;
  field ( mandatory ) Quantity, QuantityUnit;

  association _Order;

  mapping for zleg_ordi_### control zleg_s_ordi_x_###
  {
    OrderID      = order_id;
    ItemNo       = item_no;
    ProductID    = product_id;
    ItemText     = item_text;
    Quantity     = quantity;
    QuantityUnit = quantity_unit;
    UnitPrice    = unit_price;
    ItemAmount   = item_amount;
    CurrencyCode = currency_code;
  }
}
```

```bdef
projection;
strict ( 2 );

define behavior for ZRAP_C_ORDER_U_### alias Order
use etag                                          // R 뷰의 etag master를 OData ETag로 노출
{
  use create;
  use update;
  use delete;

  use action approveOrder;
  use action rejectOrder;
  use action copyOrder;

  use association _Items { create; }
}

define behavior for ZRAP_C_ORDITEM_U_### alias Item
use etag
{
  use update;
  use delete;

  use association _Order;
}
```

왜 이렇게 쓰나

- **`late numbering`을 품목에도 쓰는 이유**: 품목 키는 `OrderID + ItemNo`입니다. `ItemNo`는 레거시가 생성 즉시 정하지만, 새 주문의 품목은 `OrderID`가 저장 직전에 임시 번호 → 최종 번호로 바뀝니다. 키의 일부라도 저장 때 바뀌면 그 엔터티는 late numbering이어야 합니다(공식 `/DMO/I_Booking_U`도 같은 이유로 `late numbering`).
- 치트시트 BDL 문서에 따르면 late numbering은 managed·unmanaged 모두 가능하지만, unmanaged에서 `early numbering`은 **draft가 켜진 경우에만** 쓸 수 있습니다. 그래서 non-draft인 이 문제는 late numbering(또는 create 핸들러에서 키를 바로 주는 방식)을 씁니다. R-07의 draft BO에서는 early numbering을 씁니다.
- **`mapping for ... control ...`**: CDS 요소 이름 ↔ DB 필드 이름 대응표입니다. `control zleg_s_ordh_x_###`를 붙이면 `%control`(필드별 "보냈음" 표시) ↔ X 구조(필드별 'X')의 대응도 함께 생깁니다. 핸들러에서 `CORRESPONDING ... MAPPING FROM ENTITY`, `MAPPING TO ENTITY`, `USING CONTROL`이 이 표를 씁니다. X 구조에 없는 필드(OrderID, Status, 관리 필드)도 매핑에 넣어 두면 `MAPPING TO ENTITY`(DB 행 → 엔터티)에서 쓰입니다.
- **`etag master LocalLastChangedAt` + 품목 `etag dependent by _Order`**: 품목에는 자기 ETag가 없고 부모의 ETag를 씁니다. 그래서 R-05 레거시의 `update_order`가 **품목만 바뀌어도 헤더의 `local_last_changed_at`을 갱신**하도록 만들었습니다.
- **`authorization master ( global, instance )`**: global은 "이 사용자가 이 종류의 작업을 아예 할 수 있나"(인스턴스 없이, create 포함), instance는 "이 주문에 대해 할 수 있나"입니다. strict(2)에서는 create가 인스턴스 권한으로 검사될 수 없으므로 create를 막으려면 global(또는 precheck)이 필요합니다(정확한 strict 규칙 문구는 실제 시스템에서 확인 필요).
- **`create ( features : instance, authorization : update )`**: 품목 추가를 "부모 주문의 update 권한"으로 검사하라는 뜻입니다. 공식 draft 예제 `/DMO/R_Travel_D`도 `_Booking { create ( features : instance, authorization : update ); }`로 씁니다.
- **`factory action copyOrder [1]`**: 기존 주문 하나를 받아 **새 인스턴스**를 만드는 액션입니다. 결과는 `result`가 아니라 `mapped`로 돌려줍니다(8단계).

자주 나는 오류와 해결

- "Field CurrencyCode: ... both static and dynamic" 류의 오류: 같은 필드를 `mandatory`와 `features : instance`에 동시에 넣지 마세요. 이 정답에서는 `CurrencyCode`를 동적 제어에만 두고, 필수 여부도 features 핸들러가 `fc-f-mandatory`로 돌려줍니다(8단계).
- 프로젝션 BDEF에서 "use etag not possible": R BDEF에 `etag master`/`etag dependent`가 없으면 납니다.

</details>

#### 5단계. 행동 풀 만들기: 클래스 골격과 공통 로컬 클래스

요구사항

1. BDEF 첫 줄의 클래스 이름에서 퀵픽스(Ctrl+1) "Create behavior implementation class zbp_rap_r_order_u_###"로 행동 풀을 만드세요. ADT가 Local Types 탭에 `lhc_order`, `lhc_item`, `lsc_zrap_r_order_u_###` 골격을 만들어 줍니다.
2. 생성된 골격을 지우고 아래 구조로 **정의 부분**을 다시 쓰세요. 구현(IMPLEMENTATION)은 6~10단계에서 채웁니다. 이번 단계에서는 모든 메서드를 빈 `METHOD ... ENDMETHOD.`로 두고 활성화합니다.
   - `lcl_legacy`: `get( )`이 `ZIF_LEG_ORDER_###` 참조를 돌려주는 정적 팩토리. 평소에는 `zcl_leg_order_###=>get_instance( )`, 테스트 때는 대역(R-07)을 돌려줄 수 있도록 정적 속성 `go_double`을 둡니다.
   - `lcl_msg`: 레거시 메시지 테이블을 failed/reported로 옮기는 정적 메서드 `to_order`, `to_item`.
   - `lhc_order`(`cl_abap_behavior_handler` 상속): BDEF에서 생기는 모든 핸들러 메서드 + 상태 변경 공통 메서드 `change_status`.
   - `lhc_item`: 품목 핸들러 메서드.
   - `lsc_zrap_r_order_u_###`(`cl_abap_behavior_saver` 상속): `finalize`, `check_before_save`, `adjust_numbers`, `save`, `cleanup`, `cleanup_finalize` 재정의.
3. 행동 풀 전역 클래스(`ZBP_RAP_R_ORDER_U_###`)의 정의는 `ABSTRACT FINAL FOR BEHAVIOR OF zrap_r_order_u_###` 그대로 둡니다.

**확인** 행동 풀, R BDEF, 프로젝션 BDEF가 모두 활성화됩니다. BDEF 편집기에서 `approveOrder`에 커서를 두고 F3을 누르면 `lhc_order` 정의의 해당 메서드로 이동합니다.

<details><summary>정답·해설</summary>

전역 클래스(Global Class 탭) — 생성된 그대로입니다.

```abap
CLASS zbp_rap_r_order_u_### DEFINITION PUBLIC ABSTRACT FINAL FOR BEHAVIOR OF zrap_r_order_u_###.
ENDCLASS.

CLASS zbp_rap_r_order_u_### IMPLEMENTATION.
ENDCLASS.
```

Local Types 탭 — 정의 부분 전체입니다. (R-07에서 테스트 클래스를 위해 맨 위에 몇 줄을 더 붙입니다.)

```abap
*"* use this source file for the definition and implementation of
*"* local helper classes, interface definitions and type
*"* declarations

"=====================================================================
" lcl_legacy: 레거시 API를 얻는 단 하나의 통로
"=====================================================================
CLASS lcl_legacy DEFINITION FINAL CREATE PRIVATE.
  PUBLIC SECTION.
    CLASS-METHODS get
      RETURNING VALUE(ro_legacy) TYPE REF TO zif_leg_order_###.
  PRIVATE SECTION.
    "! 테스트 대역. 테스트 클래스만(FRIENDS, R-07) 채운다.
    CLASS-DATA go_double TYPE REF TO zif_leg_order_###.
ENDCLASS.

CLASS lcl_legacy IMPLEMENTATION.
  METHOD get.
    ro_legacy = COND #( WHEN go_double IS BOUND
                        THEN go_double
                        ELSE zcl_leg_order_###=>get_instance( ) ).
  ENDMETHOD.
ENDCLASS.

"=====================================================================
" lcl_msg: 레거시 메시지 테이블 → failed / reported (EARLY: 핸들러용)
"=====================================================================
CLASS lcl_msg DEFINITION FINAL ABSTRACT.
  PUBLIC SECTION.
    TYPES tt_order_failed   TYPE TABLE FOR FAILED   zrap_r_order_u_###\\order.
    TYPES tt_order_reported TYPE TABLE FOR REPORTED zrap_r_order_u_###\\order.
    TYPES tt_item_failed    TYPE TABLE FOR FAILED   zrap_r_order_u_###\\item.
    TYPES tt_item_reported  TYPE TABLE FOR REPORTED zrap_r_order_u_###\\item.

    "! 주문 인스턴스에 대한 메시지
    "! @parameter iv_cid       | 생성이면 %cid, 그 밖이면 %cid_ref (비어 있어도 됨)
    "! @parameter ev_failed    | 오류(E/A)가 있어 failed에 한 줄 추가했으면 abap_true
    CLASS-METHODS to_order
      IMPORTING iv_cid       TYPE abp_behv_cid OPTIONAL
                iv_order_id  TYPE zif_leg_order_###=>t_order_id OPTIONAL
                iv_dependent TYPE abap_bool DEFAULT abap_false
                it_messages  TYPE zif_leg_order_###=>tt_message
      EXPORTING ev_failed    TYPE abap_bool
      CHANGING  ct_failed    TYPE tt_order_failed
                ct_reported  TYPE tt_order_reported.

    "! 품목 인스턴스에 대한 메시지
    CLASS-METHODS to_item
      IMPORTING iv_cid       TYPE abp_behv_cid OPTIONAL
                iv_order_id  TYPE zif_leg_order_###=>t_order_id OPTIONAL
                iv_item_no   TYPE zif_leg_order_###=>t_item_no OPTIONAL
                iv_dependent TYPE abap_bool DEFAULT abap_false
                it_messages  TYPE zif_leg_order_###=>tt_message
      EXPORTING ev_failed    TYPE abap_bool
      CHANGING  ct_failed    TYPE tt_item_failed
                ct_reported  TYPE tt_item_reported.
ENDCLASS.

"=====================================================================
" lhc_order: 주문 핸들러
"=====================================================================
CLASS lhc_order DEFINITION INHERITING FROM cl_abap_behavior_handler.
  PRIVATE SECTION.
    TYPES tt_order_tky TYPE TABLE FOR READ IMPORT zrap_r_order_u_###\\order.

    "--- 권한 / 기능 제어 ------------------------------------------------
    METHODS get_global_authorizations FOR GLOBAL AUTHORIZATION
      IMPORTING REQUEST requested_authorizations FOR Order RESULT result.

    METHODS get_instance_authorizations FOR INSTANCE AUTHORIZATION
      IMPORTING keys REQUEST requested_authorizations FOR Order RESULT result.

    METHODS get_instance_features FOR INSTANCE FEATURES
      IMPORTING keys REQUEST requested_features FOR Order RESULT result.

    "--- 표준 작업 -------------------------------------------------------
    METHODS create FOR MODIFY
      IMPORTING entities FOR CREATE Order.

    METHODS update FOR MODIFY
      IMPORTING entities FOR UPDATE Order.

    METHODS delete FOR MODIFY
      IMPORTING keys FOR DELETE Order.

    METHODS read FOR READ
      IMPORTING keys FOR READ Order RESULT result.

    METHODS lock FOR LOCK
      IMPORTING keys FOR LOCK Order.

    "--- 연관 ------------------------------------------------------------
    METHODS rba_Items FOR READ
      IMPORTING keys_rba FOR READ Order\_Items FULL result_requested RESULT result LINK association_links.

    METHODS cba_Items FOR MODIFY
      IMPORTING entities_cba FOR CREATE Order\_Items.

    "--- 액션 ------------------------------------------------------------
    METHODS approveOrder FOR MODIFY
      IMPORTING keys FOR ACTION Order~approveOrder RESULT result.

    METHODS rejectOrder FOR MODIFY
      IMPORTING keys FOR ACTION Order~rejectOrder RESULT result.

    METHODS copyOrder FOR MODIFY
      IMPORTING keys FOR ACTION Order~copyOrder.

    "--- 내부 공통 -------------------------------------------------------
    "! 두 상태 액션의 공통 처리: 레거시 set_status 호출 + 메시지 매핑
    METHODS change_status
      IMPORTING it_keys     TYPE tt_order_tky
                iv_status   TYPE zif_leg_order_###=>t_status
      CHANGING  ct_failed   TYPE lcl_msg=>tt_order_failed
                ct_reported TYPE lcl_msg=>tt_order_reported.
ENDCLASS.

"=====================================================================
" lhc_item: 품목 핸들러
"=====================================================================
CLASS lhc_item DEFINITION INHERITING FROM cl_abap_behavior_handler.
  PRIVATE SECTION.
    METHODS get_instance_features FOR INSTANCE FEATURES
      IMPORTING keys REQUEST requested_features FOR Item RESULT result.

    METHODS update FOR MODIFY
      IMPORTING entities FOR UPDATE Item.

    METHODS delete FOR MODIFY
      IMPORTING keys FOR DELETE Item.

    METHODS read FOR READ
      IMPORTING keys FOR READ Item RESULT result.

    METHODS rba_Order FOR READ
      IMPORTING keys_rba FOR READ Item\_Order FULL result_requested RESULT result LINK association_links.
ENDCLASS.

"=====================================================================
" lsc_zrap_r_order_u_###: 세이버
"=====================================================================
CLASS lsc_zrap_r_order_u_### DEFINITION INHERITING FROM cl_abap_behavior_saver.
  PROTECTED SECTION.
    METHODS finalize          REDEFINITION.
    METHODS check_before_save REDEFINITION.
    METHODS adjust_numbers    REDEFINITION.
    METHODS save              REDEFINITION.
    METHODS cleanup           REDEFINITION.
    METHODS cleanup_finalize  REDEFINITION.
ENDCLASS.
```

이 단계에서는 `lcl_msg`, `lhc_order`, `lhc_item`, `lsc_zrap_r_order_u_###`의 IMPLEMENTATION에 모든 메서드를 빈 껍데기로 두세요. (예: `CLASS lhc_order IMPLEMENTATION. METHOD create. ENDMETHOD. ... ENDCLASS.`)

클래스 구조 해설

| 메서드 | BDEF의 어느 줄에서 생기나 | 프레임워크가 언제 부르나 |
|---|---|---|
| `get_global_authorizations` | `authorization master ( global, ... )` | 인스턴스와 무관하게, 작업 요청 전(UI가 버튼을 그릴 때, create 전) |
| `get_instance_authorizations` | `authorization master ( ..., instance )` | update/delete/액션/cba 전에 대상 인스턴스마다 (IN LOCAL MODE EML이면 건너뜀) |
| `get_instance_features` | `( features : instance )`가 붙은 모든 것 | UI가 버튼·필드 상태를 물을 때, 그리고 외부 요청 처리 전 |
| `create` / `update` / `delete` | `create;` `update;` `delete;` | MODIFY 요청마다 (상호작용 단계) |
| `read` | 모든 엔터티에 암묵적 | READ 요청, 변경 후 응답 만들 때, ETag 비교값을 얻을 때 |
| `lock` | `lock master` | update/delete/액션/cba 전 (생성 중인 새 인스턴스는 제외) |
| `rba_Items` / `rba_Order` | `association _Items` / `association _Order` | `READ ... BY \_Items` 요청 |
| `cba_Items` | `association _Items { create; }` | `CREATE BY \_Items` 요청 |
| `approveOrder` / `rejectOrder` / `copyOrder` | `action ...` / `factory action ...` | EXECUTE 요청 |
| 세이버 6개 | `unmanaged` (세이버는 항상 필요) | `COMMIT ENTITIES` 또는 OData 요청 끝 |

- 핸들러 메서드 시그니처의 `entities`, `keys`, `result`, `RESULT ... LINK` 같은 파라미터 타입은 모두 BDEF에서 파생됩니다(예: `TABLE FOR CREATE zrap_r_order_u_###\\order`). 그리고 모든 FOR MODIFY/READ 메서드에는 `mapped`, `failed`, `reported` CHANGING 파라미터가 **암묵적으로** 붙습니다(공식 테스트 클래스가 `behavior_handler->create( EXPORTING entities = ... CHANGING mapped = ... failed = ... reported = ... )`처럼 부르는 것으로 확인할 수 있습니다).
- **`lcl_legacy`를 두는 이유**: 모든 핸들러가 `zcl_leg_order_###=>get_instance( )`를 직접 부르면, 단위 테스트에서 진짜 레거시(진짜 DB, 진짜 잠금)를 피할 방법이 없습니다. 통로를 하나로 모아 두면 R-07에서 `go_double`에 가짜를 넣기만 하면 됩니다. `CREATE PRIVATE` + `PRIVATE SECTION`의 `go_double`이라 행동 풀 안의 다른 코드도 대역을 바꿀 수 없습니다.
- **`lcl_msg`를 핸들러 밖에 둔 이유**: 주문 핸들러의 cba는 **품목** failed/reported를 채워야 하고, 품목 핸들러는 품목 것을 채웁니다. 매핑 코드를 한 곳에 두면 두 핸들러가 같은 규칙을 씁니다.
- 세이버 메서드 중 `adjust_numbers`는 BDEF에 `late numbering`이 있을 때만 의미가 있습니다. `cleanup_finalize`는 `check_before_save`(또는 `finalize`)가 실패했을 때 불립니다.

</details>

#### 6단계. 메시지 매핑과 create · update · delete 구현

요구사항

1. `lcl_msg=>to_order` / `to_item`
   - 메시지마다 reported에 한 줄: `%cid`, 키, `%msg = zcm_leg_order_###=>from_legacy( ... )`, 메시지에 `fieldname`이 있으면 `%element-<요소>`를 켭니다(`ASSIGN COMPONENT`).
   - 오류(E/A) 메시지가 하나라도 있으면 failed에 **한 줄만** 추가: `%cid`, 키, `%fail-cause`(1단계 `get_fail_cause`). `ev_failed = abap_true`.
2. `create` (주문)
   - 엔터티마다 `CORRESPONDING zleg_ordh_###( <entity> MAPPING FROM ENTITY USING CONTROL )`로 **보낸 필드만** DB 형식으로 옮기고, 레거시 `create_order`를 **late 모드**로 부릅니다.
   - 성공하면 `mapped-order`에 `%cid`와 레거시가 준 **임시 번호**(9000000001…)를 `OrderID`로 넣습니다.
3. `update` (주문)
   - 값: `CORRESPONDING #( <entity> MAPPING FROM ENTITY )`, 플래그: `ls_orderx-_intx = CORRESPONDING #( <entity> MAPPING FROM ENTITY )`(→ `%control`이 X 구조로 바뀜).
   - 레거시 `update_order` 호출, 메시지는 `%cid_ref`와 함께 매핑.
4. `delete` (주문): 키마다 레거시 `delete_order`.
5. 핸들러 안에서 `COMMIT WORK`, `ROLLBACK WORK`, 예외 전파(`RAISE EXCEPTION`)를 쓰지 마세요.

**확인** 활성화됩니다. (실행 확인은 11·12단계)

<details><summary>정답·해설</summary>

```abap
CLASS lcl_msg IMPLEMENTATION.

  METHOD to_order.
    DATA ls_reported LIKE LINE OF ct_reported.

    ev_failed = abap_false.

    LOOP AT it_messages INTO DATA(ls_message).
      "--- failed: 인스턴스당 한 줄, 첫 오류의 원인으로 -------------------
      IF zcl_rap_order_aux_###=>is_error( ls_message ) = abap_true
      AND ev_failed = abap_false.
        APPEND VALUE #( %cid        = iv_cid
                        OrderID     = iv_order_id
                        %fail-cause = zcl_rap_order_aux_###=>get_fail_cause(
                                        is_message   = ls_message
                                        iv_dependent = iv_dependent ) )
               TO ct_failed.
        ev_failed = abap_true.
      ENDIF.

      "--- reported: 메시지마다 한 줄 -----------------------------------
      CLEAR ls_reported.
      ls_reported-%cid    = iv_cid.
      ls_reported-OrderID = iv_order_id.
      ls_reported-%msg    = zcm_leg_order_###=>from_legacy( ls_message ).

      IF ls_message-fieldname IS NOT INITIAL.
        DATA(lv_element) = zcl_rap_order_aux_###=>get_element_name( ls_message-fieldname ).
        ASSIGN COMPONENT lv_element OF STRUCTURE ls_reported-%element TO FIELD-SYMBOL(<lv_flag>).
        IF sy-subrc = 0.
          <lv_flag> = if_abap_behv=>mk-on.      " Fiori가 이 필드를 빨갛게 표시
        ENDIF.
      ENDIF.

      APPEND ls_reported TO ct_reported.
    ENDLOOP.
  ENDMETHOD.

  METHOD to_item.
    DATA ls_reported LIKE LINE OF ct_reported.

    ev_failed = abap_false.

    LOOP AT it_messages INTO DATA(ls_message).
      IF zcl_rap_order_aux_###=>is_error( ls_message ) = abap_true
      AND ev_failed = abap_false.
        APPEND VALUE #( %cid        = iv_cid
                        OrderID     = iv_order_id
                        ItemNo      = iv_item_no
                        %fail-cause = zcl_rap_order_aux_###=>get_fail_cause(
                                        is_message   = ls_message
                                        iv_dependent = iv_dependent ) )
               TO ct_failed.
        ev_failed = abap_true.
      ENDIF.

      CLEAR ls_reported.
      ls_reported-%cid    = iv_cid.
      ls_reported-OrderID = iv_order_id.
      ls_reported-ItemNo  = iv_item_no.
      ls_reported-%msg    = zcm_leg_order_###=>from_legacy( ls_message ).

      IF ls_message-fieldname IS NOT INITIAL.
        DATA(lv_element) = zcl_rap_order_aux_###=>get_element_name( ls_message-fieldname ).
        ASSIGN COMPONENT lv_element OF STRUCTURE ls_reported-%element TO FIELD-SYMBOL(<lv_flag>).
        IF sy-subrc = 0.
          <lv_flag> = if_abap_behv=>mk-on.
        ENDIF.
      ENDIF.

      APPEND ls_reported TO ct_reported.
    ENDLOOP.
  ENDMETHOD.

ENDCLASS.
```

`lhc_order` 구현의 앞부분입니다. 7~8단계의 메서드는 같은 `CLASS lhc_order IMPLEMENTATION` 안에 이어 붙입니다.

```abap
CLASS lhc_order IMPLEMENTATION.

  "------------------------------------------------------------------
  " CREATE: 임시 번호로 레거시 버퍼에 만들고, %cid ↔ 임시 키를 mapped로 알린다
  "------------------------------------------------------------------
  METHOD create.
    DATA ls_order_db TYPE zleg_ordh_###.

    LOOP AT entities ASSIGNING FIELD-SYMBOL(<entity>).
      " %control이 켜진 필드만 복사 (보내지 않은 필드는 초기값 → 레거시 기본값 적용)
      ls_order_db = CORRESPONDING #( <entity> MAPPING FROM ENTITY USING CONTROL ).

      lcl_legacy=>get( )->create_order(
        EXPORTING is_order          = CORRESPONDING #( ls_order_db )
                  iv_numbering_mode = zif_leg_order_###=>numbering_mode-late
        IMPORTING es_order          = DATA(ls_created)
                  et_messages       = DATA(lt_messages) ).

      lcl_msg=>to_order( EXPORTING iv_cid      = <entity>-%cid
                                   it_messages = lt_messages
                         IMPORTING ev_failed   = DATA(lv_failed)
                         CHANGING  ct_failed   = failed-order
                                   ct_reported = reported-order ).

      IF lv_failed = abap_false.
        " late numbering: 키 필드에 '임시 키'를 넣는다. 최종 키는 adjust_numbers에서.
        INSERT VALUE #( %cid    = <entity>-%cid
                        OrderID = ls_created-order_id ) INTO TABLE mapped-order.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

  "------------------------------------------------------------------
  " UPDATE: %control → X 구조
  "------------------------------------------------------------------
  METHOD update.
    DATA ls_order_db TYPE zleg_ordh_###.
    DATA ls_orderx   TYPE zif_leg_order_###=>ts_order_inx.

    LOOP AT entities ASSIGNING FIELD-SYMBOL(<entity>).
      ls_order_db = CORRESPONDING #( <entity> MAPPING FROM ENTITY ).

      CLEAR ls_orderx.
      ls_orderx-order_id = <entity>-OrderID.
      " BDEF의 'control zleg_s_ordh_x_###' 덕분에 %control-Note = mk-on → note = 'X'
      ls_orderx-_intx    = CORRESPONDING #( <entity> MAPPING FROM ENTITY ).

      lcl_legacy=>get( )->update_order(
        EXPORTING is_order    = CORRESPONDING #( ls_order_db )
                  is_orderx   = ls_orderx
        IMPORTING et_messages = DATA(lt_messages) ).

      lcl_msg=>to_order( EXPORTING iv_cid      = <entity>-%cid_ref
                                   iv_order_id = <entity>-OrderID
                                   it_messages = lt_messages
                         CHANGING  ct_failed   = failed-order
                                   ct_reported = reported-order ).
    ENDLOOP.
  ENDMETHOD.

  "------------------------------------------------------------------
  " DELETE
  "------------------------------------------------------------------
  METHOD delete.
    LOOP AT keys ASSIGNING FIELD-SYMBOL(<key>).
      lcl_legacy=>get( )->delete_order(
        EXPORTING iv_order_id = <key>-OrderID
        IMPORTING et_messages = DATA(lt_messages) ).

      lcl_msg=>to_order( EXPORTING iv_cid      = <key>-%cid_ref
                                   iv_order_id = <key>-OrderID
                                   it_messages = lt_messages
                         CHANGING  ct_failed   = failed-order
                                   ct_reported = reported-order ).
    ENDLOOP.
  ENDMETHOD.
```

왜 이렇게 쓰나

- **`USING CONTROL`(create)과 그냥 `MAPPING FROM ENTITY`(update)의 차이**: create에서는 "보내지 않은 필드"를 초기값으로 두어야 레거시가 기본값(주문일 = 오늘 등)을 넣을 수 있으므로 `USING CONTROL`로 보낸 필드만 복사합니다. update에서는 값은 모두 복사하되, **어느 필드를 반영할지는 X 구조가 결정**합니다. 공식 `/DMO/BP_TRAVEL_U`의 create/update도 정확히 이 조합입니다.
- `ls_orderx-_intx = CORRESPONDING #( <entity> MAPPING FROM ENTITY )`: 원본이 엔터티이고 대상이 BDEF `mapping ... control`에 적은 **제어 구조와 같은 타입**이면, `%control`의 각 플래그(`mk-on` = `'01'`)가 X 구조의 해당 필드(`'X'`)로 옮겨집니다. 이 한 줄이 "RAP의 부분 변경 의미"를 레거시의 "X 구조 의미"로 바꾸는 핵심입니다.
- **`%cid`와 `%cid_ref`**: create에는 소비자가 붙인 임시 이름 `%cid`가 있고, 같은 요청 안에서 그 인스턴스를 다시 가리킬 때(update, delete, 액션, cba) `%cid_ref`를 씁니다. failed/reported에 `%cid`를 넣어 주면 프레임워크와 소비자가 "어느 요청 줄의 실패인지"를 압니다. update에서 `%cid_ref`가 비어 있어도(키로 직접 지정한 경우) 문제없습니다.
- **임시 키를 `%key`에 넣는 방식**: late numbering에서는 생성 시 `%pid`(프레임워크용 임시 ID)를 쓰거나, 키 필드 자체에 임시 값을 넣을 수 있습니다. 치트시트 EML 문서는 "임시 키는 `%key`나 `%pid` 또는 둘 다에 담을 수 있고, `adjust_numbers`에서 `%key`의 임시 값은 `%tmp`로 옮겨진다"고 설명합니다. 이 문제는 공식 `/DMO/I_Travel_U`처럼 **키 필드에 레거시의 임시 번호**를 넣습니다. 그러면 저장 전까지 모든 핸들러가 `OrderID` 하나로 인스턴스를 찾을 수 있어 레거시와 잘 맞습니다.
- 메시지를 실패 여부와 상관없이 reported에 모두 넣는 이유: 경고(W)·정보(I) 메시지도 사용자에게 보여야 하기 때문입니다. failed는 "이 인스턴스의 작업이 거부됨"이라는 **사실**이고, reported는 그 **설명**입니다.

</details>

#### 7단계. read · lock · read-by-association · create-by-association 구현

요구사항

1. `read`
   - 키 전체를 **한 번에** 레거시 `read_orders`(품목 제외)에 넘깁니다.
   - 찾으면 `CORRESPONDING #( ls_order MAPPING TO ENTITY )`로 결과를 만들고 `StatusCriticality`를 보조 클래스로 채웁니다. 못 찾으면 failed에 `%tky` + `cause-not_found`.
   - 같은 키가 여러 번 와도 결과는 한 번만 넣습니다(`GROUP BY <key>-%tky`).
2. `lock`: 키마다 레거시 `lock_order`. 메시지 004는 `cause-locked`로 매핑됩니다.
3. `rba_Items`
   - 부모 키 전체로 `read_orders`(품목 포함)를 한 번 부르고, 부모가 없으면 `failed-order`에 `%tky`, `%assoc-_Items = mk-on`, `cause-not_found`.
   - 품목마다 `association_links`(`source-%tky` = 부모, `target-%tky` = 품목 키)를 채우고, `result_requested = abap_true`일 때만 `result`도 채웁니다.
   - 끝에 링크와 결과의 중복을 제거합니다.
4. `cba_Items`
   - 부모 존재를 한 번에 확인. 부모가 없으면 부모 failed(`%cid` = `%cid_ref`, `%tky`, `%assoc-_Items`, not_found) + **모든 자식** failed(`%cid`, `cause-dependency`).
   - 자식마다 레거시 `update_order`를 액션 코드 `C`로 부릅니다(품목 번호는 비워 두어 레거시가 매김). 성공하면 `mapped-item`에 `%cid`, `OrderID`, `ItemNo`.

**확인** 활성화됩니다.

<details><summary>정답·해설</summary>

```abap
  "------------------------------------------------------------------
  " READ: 레거시 버퍼 → (없으면) DB
  "------------------------------------------------------------------
  METHOD read.
    DATA ls_result LIKE LINE OF result.

    lcl_legacy=>get( )->read_orders(
      EXPORTING it_order_ids  = VALUE #( FOR ls_key IN keys ( ls_key-OrderID ) )
                iv_with_items = abap_false
      IMPORTING et_orders     = DATA(lt_orders) ).

    LOOP AT keys ASSIGNING FIELD-SYMBOL(<key>) GROUP BY <key>-%tky.
      READ TABLE lt_orders INTO DATA(ls_order) WITH KEY order_id = <key>-OrderID.
      IF sy-subrc = 0.
        ls_result = CORRESPONDING #( ls_order MAPPING TO ENTITY ).
        " CDS의 case와 같은 규칙으로 계산 필드를 채운다
        ls_result-StatusCriticality = zcl_rap_order_aux_###=>get_status_criticality( ls_order-status ).
        INSERT ls_result INTO TABLE result.
      ELSE.
        APPEND VALUE #( %tky        = <key>-%tky
                        %fail-cause = if_abap_behv=>cause-not_found ) TO failed-order.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

  "------------------------------------------------------------------
  " LOCK: 레거시 잠금 객체 (임시 번호는 레거시가 건너뜀)
  "------------------------------------------------------------------
  METHOD lock.
    LOOP AT keys ASSIGNING FIELD-SYMBOL(<key>).
      lcl_legacy=>get( )->lock_order(
        EXPORTING iv_order_id = <key>-OrderID
        IMPORTING et_messages = DATA(lt_messages) ).

      lcl_msg=>to_order( EXPORTING iv_order_id = <key>-OrderID
                                   it_messages = lt_messages
                         CHANGING  ct_failed   = failed-order
                                   ct_reported = reported-order ).
    ENDLOOP.
  ENDMETHOD.

  "------------------------------------------------------------------
  " READ BY ASSOCIATION: 주문 → 품목
  "------------------------------------------------------------------
  METHOD rba_Items.
    DATA ls_item_result LIKE LINE OF result.

    lcl_legacy=>get( )->read_orders(
      EXPORTING it_order_ids  = VALUE #( FOR ls_key IN keys_rba ( ls_key-OrderID ) )
                iv_with_items = abap_true
      IMPORTING et_orders     = DATA(lt_orders)
                et_items      = DATA(lt_items) ).

    LOOP AT keys_rba ASSIGNING FIELD-SYMBOL(<key>) GROUP BY <key>-%tky.

      IF NOT line_exists( lt_orders[ order_id = <key>-OrderID ] ).
        APPEND VALUE #( %tky          = <key>-%tky
                        %assoc-_Items = if_abap_behv=>mk-on      " 연관 읽기가 실패했다는 표시
                        %fail-cause   = if_abap_behv=>cause-not_found ) TO failed-order.
        CONTINUE.
      ENDIF.

      LOOP AT lt_items INTO DATA(ls_item) WHERE order_id = <key>-OrderID.
        INSERT VALUE #( source-%tky = <key>-%tky
                        target-%tky = VALUE #( OrderID = ls_item-order_id
                                               ItemNo  = ls_item-item_no ) )
               INTO TABLE association_links.

        IF result_requested = abap_true.          " FULL을 요청했을 때만 데이터까지
          ls_item_result = CORRESPONDING #( ls_item MAPPING TO ENTITY ).
          INSERT ls_item_result INTO TABLE result.
        ENDIF.
      ENDLOOP.
    ENDLOOP.

    SORT association_links BY target ASCENDING.
    DELETE ADJACENT DUPLICATES FROM association_links COMPARING ALL FIELDS.
    SORT result BY %tky ASCENDING.
    DELETE ADJACENT DUPLICATES FROM result COMPARING ALL FIELDS.
  ENDMETHOD.

  "------------------------------------------------------------------
  " CREATE BY ASSOCIATION: 주문 → 새 품목
  "------------------------------------------------------------------
  METHOD cba_Items.
    DATA ls_item_db TYPE zleg_ordi_###.

    " 부모 존재 여부를 한 번에 확인
    lcl_legacy=>get( )->read_orders(
      EXPORTING it_order_ids  = VALUE #( FOR ls_e IN entities_cba ( ls_e-OrderID ) )
                iv_with_items = abap_false
      IMPORTING et_orders     = DATA(lt_parents) ).

    LOOP AT entities_cba ASSIGNING FIELD-SYMBOL(<parent>).

      "--- 부모가 없으면: 부모는 not_found, 자식은 전부 dependency -------
      IF NOT line_exists( lt_parents[ order_id = <parent>-OrderID ] ).
        APPEND VALUE #( %cid          = <parent>-%cid_ref
                        %tky          = <parent>-%tky
                        %assoc-_Items = if_abap_behv=>mk-on
                        %fail-cause   = if_abap_behv=>cause-not_found ) TO failed-order.
        LOOP AT <parent>-%target ASSIGNING FIELD-SYMBOL(<orphan>).
          APPEND VALUE #( %cid        = <orphan>-%cid
                          %fail-cause = if_abap_behv=>cause-dependency ) TO failed-item.
        ENDLOOP.
        CONTINUE.
      ENDIF.

      "--- 자식마다 레거시 호출 (자식 하나 = 레거시 호출 하나 = 결과 하나) -
      LOOP AT <parent>-%target ASSIGNING FIELD-SYMBOL(<item>).
        ls_item_db = CORRESPONDING #( <item> MAPPING FROM ENTITY USING CONTROL ).

        lcl_legacy=>get( )->update_order(
          EXPORTING is_order    = VALUE #( order_id = <parent>-OrderID )
                    is_orderx   = VALUE #( order_id = <parent>-OrderID )   " 헤더 필드는 안 바꿈
                    it_items    = VALUE #( ( CORRESPONDING #( ls_item_db ) ) )
                    it_itemsx   = VALUE #( ( action_code = zif_leg_order_###=>action_code-create ) )
          IMPORTING et_items    = DATA(lt_created)
                    et_messages = DATA(lt_messages) ).

        lcl_msg=>to_item( EXPORTING iv_cid      = <item>-%cid
                                    iv_order_id = <parent>-OrderID
                                    it_messages = lt_messages
                          IMPORTING ev_failed   = DATA(lv_failed)
                          CHANGING  ct_failed   = failed-item
                                    ct_reported = reported-item ).

        IF lv_failed = abap_false.
          INSERT VALUE #( %cid    = <item>-%cid
                          OrderID = lt_created[ 1 ]-order_id     " 부모가 새 주문이면 임시 번호
                          ItemNo  = lt_created[ 1 ]-item_no ) INTO TABLE mapped-item.
        ENDIF.
      ENDLOOP.
    ENDLOOP.
  ENDMETHOD.
```

왜 이렇게 쓰나

- **read는 반드시 버퍼를 먼저 봐야 합니다.** 같은 트랜잭션에서 방금 만든(아직 DB에 없는) 주문, 방금 바꾼 값을 읽을 수 있어야 하기 때문입니다. 레거시 `read_orders`가 "버퍼 → DB" 순서로 찾도록 R-05에서 만든 이유입니다. 프레임워크는 OData 변경 요청의 응답을 만들 때, 그리고 **ETag를 비교할 현재 값**을 얻을 때 이 read 핸들러를 부릅니다.
- **`GROUP BY <key>-%tky`**: 공식 예제와 같은 방식으로 같은 키의 중복 요청을 한 번만 처리합니다. 결과 표에 같은 키가 두 번 들어가면 런타임 오류가 날 수 있습니다.
- **lock 핸들러는 업무 오류(다른 사용자 잠금)만 메시지로**, 잠금 서버 장애는 레거시가 `RAISE SHORTDUMP`로 끝냅니다. 핸들러 밖으로 예외를 던지는 것은 RAP 계약 위반이므로, "계속할 수 없는 기술 오류"는 덤프로 멈추는 것이 공식 예제의 선택입니다.
- **잠금은 언제 걸리나**: managed와 달리 unmanaged에서도 프레임워크가 update/delete/액션/cba 전에 lock 핸들러를 **자동으로 부릅니다**(`lock master`). 개발자가 handler에서 `lock_order`를 직접 부를 필요가 없습니다. 생성 중인 새 인스턴스(임시 번호)는 잠그지 않습니다.
- **rba의 `result_requested`**: `READ ... BY \_Items LINK DATA(links)`처럼 링크만 원하는 요청에는 데이터를 만들 필요가 없습니다. 공식 예제와 치트시트 예제 모두 이 파라미터로 분기합니다.
- **cba 실패의 두 종류**: 부모가 없으면 부모 쪽은 `not_found`(+ `%assoc-_Items`), 자식들은 "부모 때문에" 실패했으므로 `dependency`입니다. 치트시트 unmanaged 예제(`ZBP_DEMO_ABAP_RAP_RO_U`)의 `cba_Child`가 같은 규칙을 씁니다.
- **자식마다 레거시를 따로 부르는 이유**: 레거시 `update_order`는 한 번의 호출이 전부 아니면 전무라서, 자식 세 개를 한 번에 넘기면 하나만 틀려도 셋 다 실패합니다. RAP에서는 **인스턴스별로** 성공/실패를 알리는 것이 원칙이므로 자식 하나에 호출 하나로 나눕니다(공식 `cba_Booking`도 자식마다 `/DMO/FLIGHT_TRAVEL_UPDATE`를 부릅니다).
- `ItemNo`는 BDEF에서 읽기 전용이라 소비자가 보낼 수 없습니다. 레거시 `_create_item`이 "최대값 + 10"으로 즉시 매깁니다. 그래도 엔터티는 `late numbering`이므로 10단계 `adjust_numbers`에서 품목 매핑을 돌려줘야 합니다.

</details>

#### 8단계. 액션, 팩토리 액션, 동적 기능 제어, 권한

요구사항

1. `change_status`(공통): 키마다 레거시 `set_status`를 부르고 메시지를 매핑합니다.
2. `approveOrder` / `rejectOrder`: `change_status`를 부른 뒤 `READ ENTITIES ... IN LOCAL MODE ... ALL FIELDS`로 최신 값을 읽어, **실패하지 않은** 인스턴스만 `result`(`%tky`, `%param`)에 넣습니다.
3. `copyOrder`(팩토리 액션)
   - 원본 주문과 품목을 `READ ENTITIES IN LOCAL MODE`로 읽습니다(없으면 not_found).
   - `MODIFY ENTITIES ... IN LOCAL MODE`로 새 주문(`%cid` = 액션 키의 `%cid`, 주문일 = 오늘, 납기일 = 오늘 + 14, 메모 = `Copy of <원본 번호>`)과 품목(`CREATE BY \_Items`, `%cid_ref` = 새 주문의 `%cid`)을 한 번에 만듭니다.
   - 결과는 `mapped-order`로 돌려줍니다.
4. `get_instance_features`
   - `update`, `approveOrder`, `rejectOrder`, 품목 추가(`%assoc-_Items`): 상태 N일 때만 enabled.
   - `delete`: 상태 N 또는 R일 때만 enabled.
   - `%field-CurrencyCode`: 품목이 하나라도 있으면 `fc-f-read_only`, 없으면 `fc-f-mandatory`.
5. `get_global_authorizations`: 이 문제에서는 요청된 작업을 모두 허용합니다. 실제 권한 객체로 막는 방법은 주석으로 남기세요(R-03 참고).
6. `get_instance_authorizations`(4개의 눈 원칙)
   - `update`, `delete`, `rejectOrder`, `copyOrder`: 허용.
   - `approveOrder`: **본인이 만든 주문이고 총액이 1,000 초과**이면 `auth-unauthorized` + reported에 메시지 051(v1 주문, v2 한도, v3 통화).

**확인** 활성화됩니다.

<details><summary>정답·해설</summary>

```abap
  "------------------------------------------------------------------
  " 상태 액션 공통
  "------------------------------------------------------------------
  METHOD change_status.
    LOOP AT it_keys ASSIGNING FIELD-SYMBOL(<key>).
      lcl_legacy=>get( )->set_status(
        EXPORTING iv_order_id = <key>-OrderID
                  iv_status   = iv_status
        IMPORTING et_messages = DATA(lt_messages) ).

      lcl_msg=>to_order( EXPORTING iv_order_id = <key>-OrderID
                                   it_messages = lt_messages
                         CHANGING  ct_failed   = ct_failed
                                   ct_reported = ct_reported ).
    ENDLOOP.
  ENDMETHOD.

  METHOD approveOrder.
    change_status( EXPORTING it_keys     = CORRESPONDING #( keys )
                             iv_status   = zif_leg_order_###=>status-approved
                   CHANGING  ct_failed   = failed-order
                             ct_reported = reported-order ).

    " 결과($self)는 '바뀐 뒤의' 인스턴스: 버퍼에서 다시 읽는다
    READ ENTITIES OF zrap_r_order_u_### IN LOCAL MODE
      ENTITY Order
        ALL FIELDS WITH CORRESPONDING #( keys )
      RESULT DATA(lt_orders).

    LOOP AT lt_orders INTO DATA(ls_order).
      CHECK NOT line_exists( failed-order[ OrderID = ls_order-OrderID ] ).
      APPEND VALUE #( %tky   = ls_order-%tky
                      %param = ls_order ) TO result.
    ENDLOOP.
  ENDMETHOD.

  METHOD rejectOrder.
    change_status( EXPORTING it_keys     = CORRESPONDING #( keys )
                             iv_status   = zif_leg_order_###=>status-rejected
                   CHANGING  ct_failed   = failed-order
                             ct_reported = reported-order ).

    READ ENTITIES OF zrap_r_order_u_### IN LOCAL MODE
      ENTITY Order
        ALL FIELDS WITH CORRESPONDING #( keys )
      RESULT DATA(lt_orders).

    LOOP AT lt_orders INTO DATA(ls_order).
      CHECK NOT line_exists( failed-order[ OrderID = ls_order-OrderID ] ).
      APPEND VALUE #( %tky   = ls_order-%tky
                      %param = ls_order ) TO result.
    ENDLOOP.
  ENDMETHOD.

  "------------------------------------------------------------------
  " FACTORY ACTION: 자기 BO의 create / cba를 EML로 다시 부른다
  "------------------------------------------------------------------
  METHOD copyOrder.
    DATA lt_orders_new TYPE TABLE FOR CREATE zrap_r_order_u_###\\order.
    DATA lt_items_new  TYPE TABLE FOR CREATE zrap_r_order_u_###\\order\_items.

    READ ENTITIES OF zrap_r_order_u_### IN LOCAL MODE
      ENTITY Order
        ALL FIELDS WITH CORRESPONDING #( keys )
      RESULT DATA(lt_orders).

    READ ENTITIES OF zrap_r_order_u_### IN LOCAL MODE
      ENTITY Order BY \_Items
        ALL FIELDS WITH CORRESPONDING #( keys )
      RESULT DATA(lt_items).

    DATA(lv_today) = cl_abap_context_info=>get_system_date( ).

    LOOP AT keys ASSIGNING FIELD-SYMBOL(<key>).
      READ TABLE lt_orders ASSIGNING FIELD-SYMBOL(<source>) WITH KEY OrderID = <key>-OrderID.
      IF sy-subrc <> 0.
        APPEND VALUE #( %tky        = <key>-%tky
                        %fail-cause = if_abap_behv=>cause-not_found ) TO failed-order.
        CONTINUE.
      ENDIF.

      " 새 주문: %cid는 액션 요청의 %cid를 그대로 쓴다 → mapped에서 연결된다
      APPEND VALUE #( %cid         = <key>-%cid
                      Requester    = <source>-Requester
                      SupplierID   = <source>-SupplierID
                      OrderDate    = lv_today
                      DeliveryDate = lv_today + 14
                      CurrencyCode = <source>-CurrencyCode
                      Note         = |Copy of { <source>-OrderID ALPHA = OUT }| ) TO lt_orders_new.

      " 새 주문의 품목들: %cid_ref로 '방금 만들 새 주문'을 가리킨다
      APPEND VALUE #( %cid_ref = <key>-%cid
                      %target  = VALUE #( FOR ls_item IN lt_items WHERE ( OrderID = <source>-OrderID )
                                          ( %cid         = <key>-%cid && ls_item-ItemNo
                                            ProductID    = ls_item-ProductID
                                            ItemText     = ls_item-ItemText
                                            Quantity     = ls_item-Quantity
                                            QuantityUnit = ls_item-QuantityUnit
                                            UnitPrice    = ls_item-UnitPrice ) ) ) TO lt_items_new.
    ENDLOOP.

    CHECK lt_orders_new IS NOT INITIAL.

    MODIFY ENTITIES OF zrap_r_order_u_### IN LOCAL MODE
      ENTITY Order
        CREATE FIELDS ( Requester SupplierID OrderDate DeliveryDate CurrencyCode Note )
          WITH lt_orders_new
        CREATE BY \_Items
          FIELDS ( ProductID ItemText Quantity QuantityUnit UnitPrice )
          WITH lt_items_new
      MAPPED   DATA(ls_mapped)
      FAILED   DATA(ls_failed)
      REPORTED DATA(ls_reported).

    " 팩토리 액션의 결과 = mapped (%cid → 새 키)
    mapped-order = ls_mapped-order.
    mapped-item  = ls_mapped-item.
    APPEND LINES OF ls_failed-order   TO failed-order.
    APPEND LINES OF ls_failed-item    TO failed-item.
    APPEND LINES OF ls_reported-order TO reported-order.
    APPEND LINES OF ls_reported-item  TO reported-item.
  ENDMETHOD.

  "------------------------------------------------------------------
  " 동적 기능 제어
  "------------------------------------------------------------------
  METHOD get_instance_features.
    READ ENTITIES OF zrap_r_order_u_### IN LOCAL MODE
      ENTITY Order
        FIELDS ( Status ) WITH CORRESPONDING #( keys )
      RESULT DATA(lt_orders)
      FAILED failed.

    READ ENTITIES OF zrap_r_order_u_### IN LOCAL MODE
      ENTITY Order BY \_Items
        FIELDS ( ItemNo ) WITH CORRESPONDING #( lt_orders )
      LINK DATA(lt_links).

    LOOP AT lt_orders INTO DATA(ls_order).
      DATA(lv_is_new)    = xsdbool( ls_order-Status = zif_leg_order_###=>status-new ).
      DATA(lv_deletable) = xsdbool( ls_order-Status = zif_leg_order_###=>status-new
                                 OR ls_order-Status = zif_leg_order_###=>status-rejected ).
      DATA(lv_has_items) = xsdbool( line_exists( lt_links[ source-OrderID = ls_order-OrderID ] ) ).

      APPEND VALUE #(
        %tky                 = ls_order-%tky
        %update              = COND #( WHEN lv_is_new = abap_true
                                       THEN if_abap_behv=>fc-o-enabled ELSE if_abap_behv=>fc-o-disabled )
        %delete              = COND #( WHEN lv_deletable = abap_true
                                       THEN if_abap_behv=>fc-o-enabled ELSE if_abap_behv=>fc-o-disabled )
        %assoc-_Items        = COND #( WHEN lv_is_new = abap_true
                                       THEN if_abap_behv=>fc-o-enabled ELSE if_abap_behv=>fc-o-disabled )
        %action-approveOrder = COND #( WHEN lv_is_new = abap_true
                                       THEN if_abap_behv=>fc-o-enabled ELSE if_abap_behv=>fc-o-disabled )
        %action-rejectOrder  = COND #( WHEN lv_is_new = abap_true
                                       THEN if_abap_behv=>fc-o-enabled ELSE if_abap_behv=>fc-o-disabled )
        %field-CurrencyCode  = COND #( WHEN lv_has_items = abap_true
                                       THEN if_abap_behv=>fc-f-read_only ELSE if_abap_behv=>fc-f-mandatory )
      ) TO result.
    ENDLOOP.
  ENDMETHOD.

  "------------------------------------------------------------------
  " 전역 권한: 인스턴스 없이 '이 작업 자체'를 할 수 있나
  "------------------------------------------------------------------
  METHOD get_global_authorizations.
    " 실습에서는 모두 허용한다. 실제로는 권한 객체 검사를 넣는다. 예:
    "   AUTHORITY-CHECK OBJECT 'Z_ORD_###' ID 'ACTVT' FIELD '01'.
    "   result-%create = COND #( WHEN sy-subrc = 0 THEN if_abap_behv=>auth-allowed
    "                                             ELSE if_abap_behv=>auth-unauthorized ).
    "   거부할 때는 reported-order에 %global = if_abap_behv=>mk-on 인 메시지를 넣는다.
    IF requested_authorizations-%create = if_abap_behv=>mk-on.
      result-%create = if_abap_behv=>auth-allowed.
    ENDIF.
    IF requested_authorizations-%update = if_abap_behv=>mk-on.
      result-%update = if_abap_behv=>auth-allowed.
    ENDIF.
    IF requested_authorizations-%delete = if_abap_behv=>mk-on.
      result-%delete = if_abap_behv=>auth-allowed.
    ENDIF.
    IF requested_authorizations-%action-approveOrder = if_abap_behv=>mk-on.
      result-%action-approveOrder = if_abap_behv=>auth-allowed.
    ENDIF.
    IF requested_authorizations-%action-rejectOrder = if_abap_behv=>mk-on.
      result-%action-rejectOrder = if_abap_behv=>auth-allowed.
    ENDIF.
    IF requested_authorizations-%action-copyOrder = if_abap_behv=>mk-on.
      result-%action-copyOrder = if_abap_behv=>auth-allowed.
    ENDIF.
  ENDMETHOD.

  "------------------------------------------------------------------
  " 인스턴스 권한: 4개의 눈 원칙 (본인 고액 주문은 본인이 승인 불가)
  "------------------------------------------------------------------
  METHOD get_instance_authorizations.
    CONSTANTS lc_approval_limit TYPE zleg_ordh_###-total_amount VALUE '1000.00'.

    READ ENTITIES OF zrap_r_order_u_### IN LOCAL MODE
      ENTITY Order
        FIELDS ( CreatedBy TotalAmount CurrencyCode ) WITH CORRESPONDING #( keys )
      RESULT DATA(lt_orders)
      FAILED failed.

    DATA(lv_me) = cl_abap_context_info=>get_user_technical_name( ).

    LOOP AT lt_orders INTO DATA(ls_order).
      DATA(lv_own_big_order) = xsdbool( ls_order-CreatedBy   = lv_me
                                    AND ls_order-TotalAmount > lc_approval_limit ).

      IF lv_own_big_order = abap_true
      AND requested_authorizations-%action-approveOrder = if_abap_behv=>mk-on.
        APPEND VALUE #( %tky = ls_order-%tky
                        %msg = zcm_leg_order_###=>from_legacy( VALUE #(
                                 msgty = 'E'
                                 msgid = zif_leg_order_###=>message_class
                                 msgno = '051'
                                 msgv1 = |{ ls_order-OrderID ALPHA = OUT }|
                                 msgv2 = |{ lc_approval_limit NUMBER = USER }|
                                 msgv3 = ls_order-CurrencyCode ) ) ) TO reported-order.
      ENDIF.

      APPEND VALUE #( %tky                 = ls_order-%tky
                      %update              = if_abap_behv=>auth-allowed
                      %delete              = if_abap_behv=>auth-allowed
                      %action-rejectOrder  = if_abap_behv=>auth-allowed
                      %action-copyOrder    = if_abap_behv=>auth-allowed
                      %action-approveOrder = COND #( WHEN lv_own_big_order = abap_true
                                                     THEN if_abap_behv=>auth-unauthorized
                                                     ELSE if_abap_behv=>auth-allowed ) ) TO result.
    ENDLOOP.
  ENDMETHOD.

ENDCLASS.
```

왜 이렇게 쓰나

- **액션 결과 `result [1] $self`**: "액션을 실행한 뒤의 그 인스턴스"를 돌려주라는 뜻입니다. Fiori는 이 결과로 화면을 바로 갱신합니다. 상태를 바꾼 뒤 `READ ENTITIES ... IN LOCAL MODE`로 **버퍼에서** 다시 읽으므로 아직 저장하지 않은 새 상태가 보입니다(read 핸들러가 레거시 버퍼를 먼저 보기 때문).
- **`IN LOCAL MODE`**: 같은 BO 안에서 부르는 EML은 권한·기능 제어 검사를 건너뜁니다. `get_instance_features` 안에서 일반 READ를 하면 다시 features 검사가 일어나는 순환이 생길 수 있고, `copyOrder`의 MODIFY가 "update 비활성" 같은 제어에 막히면 안 되기 때문입니다.
- **팩토리 액션에서 자기 BO의 EML을 다시 부르는 패턴**: 공식 `/DMO/BP_TRAVEL_M`의 `copyTravel`과 같습니다. unmanaged에서도 동작합니다. `MODIFY ENTITIES IN LOCAL MODE ... CREATE`가 **우리의 `create` 핸들러를**, `CREATE BY \_Items`가 **`cba_Items` 핸들러를** 다시 부릅니다. `%cid_ref = <key>-%cid`는 "같은 요청 안에서 방금 `%cid`로 만든 새 주문"을 가리키고, 프레임워크가 cba 핸들러에 넘기기 전에 그 주문의 (임시) 키로 바꿔 줍니다.
- 팩토리 액션은 `result`가 없고 **`mapped`가 결과**입니다. 액션 요청의 `%cid`와 새 키를 연결해 주어야 Fiori가 복사본의 상세 화면으로 이동합니다.
- **기능 제어(features)와 권한(authorization)의 차이**: features는 "**지금 이 인스턴스 상태에서** 이 작업이 의미가 있나"(승인된 주문은 변경 불가), authorization은 "**이 사용자가** 할 수 있나"(본인 고액 주문 승인 불가)입니다. Fiori에서는 둘 다 버튼을 회색으로 만들지만, 권한 거부는 메시지(`reported`)를 남깁니다.
- **인스턴스 권한에 failed를 직접 쓰지 않는 이유**: `result`에 `auth-unauthorized`를 돌려주면 프레임워크가 해당 작업을 failed(`cause-unauthorized`)로 만듭니다. 우리는 **이유**(메시지 051)만 reported에 넣습니다. 공식 `/DMO/BP_TRAVEL_D`의 `get_instance_authorizations`도 reported만 채웁니다.
- 4개의 눈 검사에서 총액은 **저장된 값**이 기준입니다. 레거시 `determine_totals`는 저장 직전(finalize)에만 총액을 계산하므로, 아직 저장하지 않은 새 주문은 총액이 0입니다. "저장된 주문을 승인한다"는 업무 흐름에서는 문제없습니다. 통화가 다른 주문을 같은 한도로 비교하는 것은 실습용 단순화입니다.
- `%field-CurrencyCode`의 `fc-f-mandatory`: 동적으로 "필수"를 줄 수도 있습니다. 다만 create 시점에는 인스턴스가 없어 동적 제어가 적용되지 않으므로, 통화 누락은 결국 레거시 `check_orders`(메시지 012)가 저장 때 막습니다.

자주 나는 오류와 해결

- "The component %ACTION-COPYORDER does not exist" 류: 팩토리 액션에 `authorization : update`를 붙였다면 권한 결과에 `%action-copyOrder`가 없습니다. 이 정답의 BDEF처럼 권한 지정 없이 두거나, 결과에서 그 줄을 지우세요.
- `get_instance_features`에서 `FAILED failed` 생략 시 문법 오류는 아니지만, 없는 키를 물었을 때 응답이 비어 프레임워크가 혼란스러워합니다. 공식 예제처럼 넘겨 주세요.

</details>

#### 9단계. 품목 핸들러 `lhc_item` 구현

요구사항

1. `update`: 품목마다 레거시 `update_order`를 부릅니다. 헤더는 키만, 품목은 액션 코드 `U` + `_intx = CORRESPONDING #( <entity> MAPPING FROM ENTITY )`.
2. `delete`: 품목마다 액션 코드 `D`.
3. `read`: 요청 키들의 주문 번호로 `read_orders`(품목 포함)를 한 번 부르고, 품목을 찾으면 `MAPPING TO ENTITY`, 없으면 not_found.
4. `rba_Order`: 품목 → 부모 주문. `association_links`(`source-%tky` = 품목, `target-OrderID` = 주문)와, 요청 시 `result`(주문 + `StatusCriticality`).
5. `get_instance_features`: 부모 주문 상태가 N일 때만 품목 update/delete enabled. 부모 상태는 `READ ENTITIES ... ENTITY Item BY \_Order`로 읽습니다.

**확인** 행동 풀 전체가 활성화됩니다(세이버는 아직 빈 껍데기).

<details><summary>정답·해설</summary>

```abap
CLASS lhc_item IMPLEMENTATION.

  METHOD update.
    DATA ls_item_db TYPE zleg_ordi_###.
    DATA ls_itemx   TYPE zif_leg_order_###=>ts_item_inx.

    LOOP AT entities ASSIGNING FIELD-SYMBOL(<entity>).
      ls_item_db = CORRESPONDING #( <entity> MAPPING FROM ENTITY ).

      CLEAR ls_itemx.
      ls_itemx-item_no     = <entity>-ItemNo.
      ls_itemx-action_code = zif_leg_order_###=>action_code-update.
      ls_itemx-_intx       = CORRESPONDING #( <entity> MAPPING FROM ENTITY ).   " %control → X

      lcl_legacy=>get( )->update_order(
        EXPORTING is_order    = VALUE #( order_id = <entity>-OrderID )
                  is_orderx   = VALUE #( order_id = <entity>-OrderID )
                  it_items    = VALUE #( ( CORRESPONDING #( ls_item_db ) ) )
                  it_itemsx   = VALUE #( ( ls_itemx ) )
        IMPORTING et_messages = DATA(lt_messages) ).

      lcl_msg=>to_item( EXPORTING iv_cid      = <entity>-%cid_ref
                                  iv_order_id = <entity>-OrderID
                                  iv_item_no  = <entity>-ItemNo
                                  it_messages = lt_messages
                        CHANGING  ct_failed   = failed-item
                                  ct_reported = reported-item ).
    ENDLOOP.
  ENDMETHOD.

  METHOD delete.
    LOOP AT keys ASSIGNING FIELD-SYMBOL(<key>).
      lcl_legacy=>get( )->update_order(
        EXPORTING is_order    = VALUE #( order_id = <key>-OrderID )
                  is_orderx   = VALUE #( order_id = <key>-OrderID )
                  it_items    = VALUE #( ( item_no = <key>-ItemNo ) )
                  it_itemsx   = VALUE #( ( item_no     = <key>-ItemNo
                                           action_code = zif_leg_order_###=>action_code-delete ) )
        IMPORTING et_messages = DATA(lt_messages) ).

      lcl_msg=>to_item( EXPORTING iv_cid      = <key>-%cid_ref
                                  iv_order_id = <key>-OrderID
                                  iv_item_no  = <key>-ItemNo
                                  it_messages = lt_messages
                        CHANGING  ct_failed   = failed-item
                                  ct_reported = reported-item ).
    ENDLOOP.
  ENDMETHOD.

  METHOD read.
    DATA ls_result LIKE LINE OF result.

    lcl_legacy=>get( )->read_orders(
      EXPORTING it_order_ids  = VALUE #( FOR ls_key IN keys ( ls_key-OrderID ) )
                iv_with_items = abap_true
      IMPORTING et_items      = DATA(lt_items) ).

    LOOP AT keys ASSIGNING FIELD-SYMBOL(<key>) GROUP BY <key>-%tky.
      READ TABLE lt_items INTO DATA(ls_item)
           WITH KEY order_id = <key>-OrderID
                    item_no  = <key>-ItemNo.
      IF sy-subrc = 0.
        ls_result = CORRESPONDING #( ls_item MAPPING TO ENTITY ).
        INSERT ls_result INTO TABLE result.
      ELSE.
        APPEND VALUE #( %tky        = <key>-%tky
                        %fail-cause = if_abap_behv=>cause-not_found ) TO failed-item.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

  METHOD rba_Order.
    DATA ls_order_result LIKE LINE OF result.

    lcl_legacy=>get( )->read_orders(
      EXPORTING it_order_ids  = VALUE #( FOR ls_key IN keys_rba ( ls_key-OrderID ) )
                iv_with_items = abap_false
      IMPORTING et_orders     = DATA(lt_orders) ).

    LOOP AT keys_rba ASSIGNING FIELD-SYMBOL(<key>) GROUP BY <key>-%tky.
      READ TABLE lt_orders INTO DATA(ls_order) WITH KEY order_id = <key>-OrderID.
      IF sy-subrc <> 0.
        APPEND VALUE #( %tky           = <key>-%tky
                        %assoc-_Order  = if_abap_behv=>mk-on
                        %fail-cause    = if_abap_behv=>cause-not_found ) TO failed-item.
        CONTINUE.
      ENDIF.

      INSERT VALUE #( source-%tky    = <key>-%tky
                      target-OrderID = ls_order-order_id ) INTO TABLE association_links.

      IF result_requested = abap_true.
        ls_order_result = CORRESPONDING #( ls_order MAPPING TO ENTITY ).
        ls_order_result-StatusCriticality = zcl_rap_order_aux_###=>get_status_criticality( ls_order-status ).
        INSERT ls_order_result INTO TABLE result.
      ENDIF.
    ENDLOOP.

    SORT association_links BY source ASCENDING.
    DELETE ADJACENT DUPLICATES FROM association_links COMPARING ALL FIELDS.
    SORT result BY %tky ASCENDING.
    DELETE ADJACENT DUPLICATES FROM result COMPARING ALL FIELDS.
  ENDMETHOD.

  METHOD get_instance_features.
    READ ENTITIES OF zrap_r_order_u_### IN LOCAL MODE
      ENTITY Item BY \_Order
        FIELDS ( Status ) WITH CORRESPONDING #( keys )
      RESULT DATA(lt_parents)
      FAILED failed.

    LOOP AT keys ASSIGNING FIELD-SYMBOL(<key>).
      DATA(lv_parent_new) = xsdbool( line_exists( lt_parents[ OrderID = <key>-OrderID
                                                              Status  = zif_leg_order_###=>status-new ] ) ).
      APPEND VALUE #( %tky    = <key>-%tky
                      %update = COND #( WHEN lv_parent_new = abap_true
                                        THEN if_abap_behv=>fc-o-enabled ELSE if_abap_behv=>fc-o-disabled )
                      %delete = COND #( WHEN lv_parent_new = abap_true
                                        THEN if_abap_behv=>fc-o-enabled ELSE if_abap_behv=>fc-o-disabled ) )
             TO result.
    ENDLOOP.
  ENDMETHOD.

ENDCLASS.
```

왜 이렇게 쓰나

- 품목 변경도 레거시 입장에서는 **"주문 하나에 대한 `update_order`"** 입니다. 헤더 X 구조를 키만 채워 보내면 헤더 필드는 하나도 안 바뀌지만, 레거시가 헤더 관리 필드(ETag)는 갱신합니다. 그래서 `etag dependent by _Order`가 성립합니다(R-05 9단계 해설).
- 품목 read에서 `read_orders`를 **주문 번호 단위로 한 번** 부르는 이유: 레거시에는 "품목 하나 읽기" API가 없고, 키 수만큼 부르면 루프 안 DB 읽기가 됩니다. 공식 `/DMO/BP_BOOKING_U`의 read도 여행 번호로 묶어(`GROUP BY travelid`) 한 번씩 읽습니다.
- `rba_Order`의 링크는 `target-OrderID`만 채워도 됩니다(공식 `rba_Travel`도 `target-travelid`만 채움). 부모 키가 OrderID 하나이기 때문입니다.
- 품목 features에서 부모 상태를 `BY \_Order`로 읽는 것은 **우리 자신의 `rba_Order` 핸들러**를 부르는 것입니다. 즉 한 핸들러를 잘 만들어 두면 BO 안의 다른 로직이 그것을 EML로 재사용합니다.

클래스 구조 해설 (핸들러 파생 타입 정리)

| 파라미터 | 파생 타입 | 꼭 쓰는 성분 |
|---|---|---|
| `create`의 `entities` | `TABLE FOR CREATE zrap_r_order_u_###\\order` | `%cid`, `%control`, 필드 |
| `update`의 `entities` | `TABLE FOR UPDATE ...\\order` | `%cid_ref`, `%tky`/키, `%control`, 필드 |
| `delete`의 `keys` | `TABLE FOR DELETE ...\\order` | `%cid_ref`, `%tky`/키 |
| `read`의 `keys` / `result` | `TABLE FOR READ IMPORT` / `TABLE FOR READ RESULT` | `%tky`, `%control`(요청 필드) |
| `rba_Items`의 `keys_rba`, `result`, `association_links` | `TABLE FOR READ IMPORT ...\\order\_items`, `... RESULT ...`, `TABLE FOR READ LINK ...` | `source-%tky`, `target-%tky` |
| `cba_Items`의 `entities_cba` | `TABLE FOR CREATE ...\\order\_items` | `%cid_ref`, `%tky`, `%target`(각 `%cid`) |
| 액션의 `keys` / `result` | `TABLE FOR ACTION IMPORT ...~approveOrder` / `TABLE FOR ACTION RESULT ...` | `%tky`, `%cid_ref`, (팩토리면 `%cid`) / `%tky`, `%param` |
| `mapped` / `failed` / `reported` (암묵적 CHANGING) | `RESPONSE FOR MAPPED/FAILED/REPORTED EARLY zrap_r_order_u_###` | 엔터티별 표 `-order`, `-item` |

</details>

#### 10단계. 세이버 `lsc_zrap_r_order_u_###` 구현

요구사항

1. `finalize`: 레거시 `determine_totals`(총액 파생).
2. `check_before_save`: 레거시 `check_orders`를 부르고, 메시지를 **LATE 응답**으로 옮깁니다.
   - 품목 번호가 없는 메시지 → `failed-order`(오류일 때, 주문당 한 줄) + `reported-order`(`%element` 포함).
   - 품목 번호가 있는 메시지 → `failed-item` + `reported-item`(`%element`, 부모를 가리키는 `%path`).
3. `adjust_numbers`: 레거시 `adjust_numbers`의 두 매핑을 `mapped-order`(`%tmp-OrderID` = 임시, `OrderID` = 최종)와 `mapped-item`(`%tmp`에 임시 주문 번호 + 품목 번호)으로 옮깁니다.
4. `save`: 레거시 `save`.
5. `cleanup`: 레거시 `initialize`.
6. `cleanup_finalize`: 아무것도 하지 않되 **왜 비워 두는지** 주석으로 남깁니다.

**확인** 행동 풀 전체가 활성화되고, 빈 메서드가 하나도 남지 않습니다.

<details><summary>정답·해설</summary>

```abap
CLASS lsc_zrap_r_order_u_### IMPLEMENTATION.

  "------------------------------------------------------------------
  " 1) early save: 저장 전 마지막 파생 (총액)
  "------------------------------------------------------------------
  METHOD finalize.
    lcl_legacy=>get( )->determine_totals( ).
  ENDMETHOD.

  "------------------------------------------------------------------
  " 2) early save: 저장해도 되는가? (실패하면 저장 거부 → 상호작용 단계로)
  "------------------------------------------------------------------
  METHOD check_before_save.
    DATA ls_order_rep LIKE LINE OF reported-order.
    DATA ls_item_rep  LIKE LINE OF reported-item.

    lcl_legacy=>get( )->check_orders( IMPORTING et_messages = DATA(lt_messages) ).

    LOOP AT lt_messages INTO DATA(ls_message).
      DATA(lv_is_error) = zcl_rap_order_aux_###=>is_error( ls_message ).
      DATA(lv_element)  = zcl_rap_order_aux_###=>get_element_name( ls_message-fieldname ).

      IF ls_message-item_no IS INITIAL.
        "--- 주문 헤더에 대한 메시지 ----------------------------------
        IF lv_is_error = abap_true
        AND NOT line_exists( failed-order[ OrderID = ls_message-order_id ] ).
          APPEND VALUE #( OrderID = ls_message-order_id ) TO failed-order.
        ENDIF.

        CLEAR ls_order_rep.
        ls_order_rep-OrderID = ls_message-order_id.
        ls_order_rep-%msg    = zcm_leg_order_###=>from_legacy( ls_message ).
        IF lv_element IS NOT INITIAL.
          ASSIGN COMPONENT lv_element OF STRUCTURE ls_order_rep-%element TO FIELD-SYMBOL(<lv_order_flag>).
          IF sy-subrc = 0.
            <lv_order_flag> = if_abap_behv=>mk-on.
          ENDIF.
        ENDIF.
        APPEND ls_order_rep TO reported-order.

      ELSE.
        "--- 품목에 대한 메시지 ---------------------------------------
        IF lv_is_error = abap_true
        AND NOT line_exists( failed-item[ OrderID = ls_message-order_id ItemNo = ls_message-item_no ] ).
          APPEND VALUE #( OrderID = ls_message-order_id
                          ItemNo  = ls_message-item_no ) TO failed-item.
        ENDIF.

        CLEAR ls_item_rep.
        ls_item_rep-OrderID             = ls_message-order_id.
        ls_item_rep-ItemNo              = ls_message-item_no.
        ls_item_rep-%msg                = zcm_leg_order_###=>from_legacy( ls_message ).
        ls_item_rep-%path-order-OrderID = ls_message-order_id.   " UI가 부모 화면에 메시지를 붙일 수 있게
        IF lv_element IS NOT INITIAL.
          ASSIGN COMPONENT lv_element OF STRUCTURE ls_item_rep-%element TO FIELD-SYMBOL(<lv_item_flag>).
          IF sy-subrc = 0.
            <lv_item_flag> = if_abap_behv=>mk-on.
          ENDIF.
        ENDIF.
        APPEND ls_item_rep TO reported-item.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

  "------------------------------------------------------------------
  " 3) late save: 임시 키 → 최종 키 (되돌릴 수 없는 지점)
  "------------------------------------------------------------------
  METHOD adjust_numbers.
    lcl_legacy=>get( )->adjust_numbers(
      IMPORTING et_order_mapping = DATA(lt_order_map)
                et_item_mapping  = DATA(lt_item_map) ).

    mapped-order = VALUE #( FOR ls_om IN lt_order_map
                            ( %tmp    = VALUE #( OrderID = ls_om-preliminary )   " 상호작용 단계에서 쓰던 키
                              OrderID = ls_om-final ) ).                        " 최종 키

    mapped-item  = VALUE #( FOR ls_im IN lt_item_map
                            ( %tmp    = VALUE #( OrderID = ls_im-preliminary-order_id
                                                 ItemNo  = ls_im-preliminary-item_no )
                              OrderID = ls_im-final-order_id
                              ItemNo  = ls_im-final-item_no ) ).
  ENDMETHOD.

  "------------------------------------------------------------------
  " 4) late save: DB 쓰기 (COMMIT은 프레임워크가)
  "------------------------------------------------------------------
  METHOD save.
    lcl_legacy=>get( )->save( ).
  ENDMETHOD.

  "------------------------------------------------------------------
  " 5) 저장 성공 후 또는 ROLLBACK ENTITIES 후: 버퍼 비우기
  "------------------------------------------------------------------
  METHOD cleanup.
    lcl_legacy=>get( )->initialize( ).
  ENDMETHOD.

  "------------------------------------------------------------------
  " 6) finalize/check_before_save가 실패했을 때
  "------------------------------------------------------------------
  METHOD cleanup_finalize.
    " 저장이 거부되면 트랜잭션은 상호작용 단계로 돌아간다.
    " 사용자가 오류를 고쳐 다시 저장할 수 있어야 하므로 버퍼는 지우지 않는다.
    " finalize에서 바꾼 것은 총액뿐이고, 다음 저장 시도에서 다시 계산되므로 되돌릴 필요가 없다.
  ENDMETHOD.

ENDCLASS.
```

왜 이렇게 쓰나

- **저장 순서**(치트시트 EML 문서의 "Phases of a RAP Transaction"): `finalize` → `check_before_save` → (둘 중 하나라도 failed가 있으면 `cleanup_finalize` 후 상호작용 단계로 복귀) → `adjust_numbers` → `save` → `cleanup`. late save(`adjust_numbers`, `save`)에 들어가면 **되돌아갈 수 없으므로** 여기서는 실패를 알리지 않습니다. 실패할 수 있는 모든 검사는 `check_before_save`까지 끝내야 합니다. R-05 레거시가 `adjust_numbers`/`save`에서 `ASSERT`를 쓰는 이유이기도 합니다.
- **managed와 비교**: managed BO에서는 `finalize`가 on save determination을, `check_before_save`가 on save validation을 실행합니다(치트시트 BDL/EML 문서). unmanaged non-draft에서는 그 역할을 **세이버 메서드에 직접** 씁니다. 그래서 `finalize` = 레거시 파생(`determine_totals`), `check_before_save` = 레거시 검증(`check_orders`)입니다.
- **LATE 응답 타입**: 세이버의 `failed`, `reported`, `mapped`는 `RESPONSE FOR ... LATE`입니다. 이 시점에는 `%cid`가 없고, 인스턴스는 키(우리 경우 임시 번호가 든 `OrderID`)로 식별합니다. 그래서 `check_before_save`에서 `OrderID = ls_message-order_id`(임시 번호 포함)를 그대로 쓰면 됩니다. 공식 `/DMO/BP_TRAVEL_U`의 세이버 테스트도 `RESPONSE FOR MAPPED LATE` 타입을 씁니다.
- **`%tmp`**: 치트시트 EML 문서는 "`adjust_numbers`에 도달하면 `%key`에 있던 임시 키 값이 `%tmp`로 옮겨지고, `%key`는 최종 키를 담는다"고 설명합니다. 그래서 매핑 한 줄 = `%tmp`(임시) + 키 필드(최종)입니다. 품목은 주문 번호가 그대로인 경우에도 레거시가 a=a 매핑을 주므로(R-05 10단계) 이번 트랜잭션에서 생성된 품목이 빠짐없이 매핑됩니다.
- `%path-order-OrderID`: 품목 메시지를 부모 주문 화면에서 보여 주기 위한 경로입니다. 공식 draft 예제의 `%path = VALUE #( travel-%tky = ... )`처럼 부모 엔터티 별칭(대소문자 무관) 아래에 부모 키를 넣습니다. LATE reported에서 `%path`/`%element`가 그대로 제공되는지는 실제 시스템에서 확인 필요합니다. 활성화 오류("component %PATH does not exist")가 나면 그 줄만 지우세요.
- `save` 안에서 `COMMIT WORK`를 하지 않는 것은 레거시가 이미 지키고 있습니다. 치트시트 EML 문서의 허용 문장 표에 따르면 RAP 핸들러·세이버 안에서 `COMMIT WORK`/`ROLLBACK WORK`는 금지이고, **DB 변경은 late save 단계에서만** 허용됩니다.

클래스 구조 해설

| 세이버 메서드 | 파라미터(암묵적) | 레거시 짝 | 실패 가능? |
|---|---|---|---|
| `finalize` | `CHANGING failed reported` (LATE) | `determine_totals` | 예 (이 BO는 실패시키지 않음) |
| `check_before_save` | `CHANGING failed reported` (LATE) | `check_orders` | **예** → 저장 거부 |
| `cleanup_finalize` | 없음 | (없음) | - |
| `adjust_numbers` | `CHANGING mapped reported` (LATE) | `adjust_numbers` | 아니요 |
| `save` | `CHANGING reported` (LATE) | `save` | 아니요 |
| `cleanup` | 없음 | `initialize` | - |

(파라미터 구성은 공식 `/DMO/BP_TRAVEL_U`의 세이버 테스트 `ltcl_saver`가 각 메서드를 부르는 방식에서 확인할 수 있습니다.)

</details>

#### 11단계. 서비스 정의·바인딩과 Fiori 미리보기로 전체 시험

요구사항

1. 서비스 정의 `ZRAP_UI_ORDER_U_###`: 주문(`PurchaseOrder`), 품목(`PurchaseOrderItem`), 값 도움말 뷰 4개(`/DMO/I_Agency_StdVH`, `/DMO/I_Supplement_StdVH`, `I_CurrencyStdVH`, `I_UnitOfMeasure`)를 노출합니다.
2. 서비스 바인딩 `ZRAP_UI_ORDER_U_O4_###`: Binding Type **OData V4 - UI**, Publish 후 `PurchaseOrder`를 선택하고 Preview.
3. 아래 시나리오를 차례로 해 보고 결과를 기록하세요.
   1. 목록에서 Go → R-05 데모 주문이 보이고 상태 색이 다릅니다.
   2. Create → 요청자, 공급업체(F4), 납기일, 통화 입력 후 Save → **번호가 최종 번호로** 보입니다(임시 번호 9…가 화면에 남지 않음).
   3. 새 주문을 열어 품목 표의 Create → 제품(F4), 수량, 단위, 단가 입력 후 저장 → 주문으로 돌아가 Total Amount가 갱신되었는지, 통화 필드가 읽기 전용이 되었는지 확인.
   4. 공급업체에 `999999`를 넣고 저장 → 저장이 거부되고 Supplier 필드에 메시지가 붙습니다(`check_before_save`).
   5. Approve → 상태 A(녹색), Edit·Delete·Approve·Reject 버튼이 비활성화.
   6. 승인된 주문에서 Copy → 새 주문(상태 N)의 상세 화면으로 이동하고 품목도 복사되었는지 확인.
   7. **ETag 충돌**: 같은 주문을 브라우저 탭 두 개로 엽니다. 탭 A에서 Note를 바꿔 저장, 탭 B에서 (새로 고침 없이) Note를 바꿔 저장 → 탭 B에서 "다른 사용자가 변경함" 류의 오류가 나야 합니다.
4. (선택) 다른 사용자 ID가 있으면 4개의 눈 원칙도 시험합니다. 본인이 만든 총액 1,000 초과 주문의 Approve 버튼이 비활성화되고 메시지 051이 보입니다.

**직접 추가할 어노테이션**

- `@EndUserText.label` — 서비스 정의 설명
- `@ObjectModel.leadingEntity.name` — 서비스의 대표 엔터티 지정 (선택)

**확인** 위 시나리오 1~7이 설명대로 동작합니다. 특히 7번에서 탭 B의 저장이 거부되면 ETag가 제대로 동작하는 것입니다.

<details><summary>정답·해설</summary>

```cds
@EndUserText.label: 'Purchase order (unmanaged) service ###'
@ObjectModel.leadingEntity.name: 'ZRAP_C_ORDER_U_###'      // 대표 엔터티
define service ZRAP_UI_ORDER_U_### {
  expose ZRAP_C_ORDER_U_###      as PurchaseOrder;
  expose ZRAP_C_ORDITEM_U_###    as PurchaseOrderItem;
  expose /DMO/I_Agency_StdVH     as Supplier;
  expose /DMO/I_Supplement_StdVH as Product;
  expose I_CurrencyStdVH         as Currency;
  expose I_UnitOfMeasure         as UnitOfMeasure;
}
```

서비스 바인딩: New > Other ABAP Repository Object > Business Services > Service Binding, 이름 `ZRAP_UI_ORDER_U_O4_###`, Binding Type `OData V4 - UI`, Service Definition `ZRAP_UI_ORDER_U_###` → 활성화 → **Publish** → 엔터티 목록에서 `PurchaseOrder` 선택 → **Preview**.

시나리오별로 무엇이 일어나는지

| 시나리오 | 프레임워크가 부르는 순서 (대략) |
|---|---|
| 2 생성 | `get_global_authorizations` → `create`(임시 9000000001) → `read`(응답) → `finalize` → `check_before_save` → `adjust_numbers`(최종 번호) → `save` → `cleanup` |
| 3 품목 추가 | `get_instance_features` → `get_instance_authorizations`(update) → `lock` → `cba_Items` → 저장 순서 |
| 4 저장 거부 | `update` → `finalize` → `check_before_save`(failed) → `cleanup_finalize` → 요청 전체 롤백(`cleanup`) |
| 5 승인 | `get_instance_authorizations` → `get_instance_features` → `lock` → `approveOrder`(+ 내부 `read`) → 저장 순서 |
| 6 복사 | `copyOrder` → (내부 EML) `create` + `cba_Items` → 저장 순서(`adjust_numbers`가 새 번호) |
| 7 ETag | 탭 B의 PATCH에 `If-Match: <예전 ETag>` → 프레임워크가 `read`로 현재 `LocalLastChangedAt`을 얻어 비교 → 다르면 `update`를 부르지 않고 거부 |

왜 이렇게 쓰나

- **non-draft에서 잠금은 "한 요청 동안"만** 유지됩니다. OData 요청 하나가 하나의 RAP 트랜잭션이고, 저장이 끝나면 잠금이 풀립니다. 그래서 두 사용자가 같은 주문을 **동시에 화면에 열어 두는** 상황은 잠금이 아니라 **ETag**가 막습니다(시나리오 7). 화면을 연 동안 계속 잠가 두는 것은 R-07의 draft가 하는 일입니다.
- ETag 비교는 RAP 런타임(OData 계층)이 합니다. unmanaged 개발자가 할 일은 (1) BDEF에 `etag master` 필드 지정, (2) **모든 변경에서 그 필드 갱신**(레거시 `_set_admin`), (3) read 핸들러가 버퍼 값을 정확히 돌려주기 — 세 가지입니다. ETag 비교가 EML 호출에도 일어나는지는 실제 시스템에서 확인 필요합니다(EML에는 If-Match 같은 ETag 입력이 없으므로 일반적으로 비교하지 않습니다).
- 시나리오 2에서 임시 번호가 화면에 남지 않는 이유: OData 생성 요청은 "생성 + 저장"이 한 번에 일어나고, 응답을 만들기 전에 `adjust_numbers`가 끝나 프레임워크가 최종 키로 응답합니다.
- 오류 메시지 문구(탭 B의 ETag 충돌 문구 등)는 Fiori 버전에 따라 다릅니다(실제 화면에서 확인 필요).

자주 나는 오류와 해결

- Preview에서 목록은 나오는데 Create 후 "Entity not found": read 핸들러가 임시 번호를 못 찾는 경우입니다. 레거시 `read_orders`가 버퍼를 먼저 보는지, `mapped-order`에 레거시가 돌려준 번호를 넣었는지 확인하세요.
- 저장 시 짧은 덤프 `ASSERTION_FAILED`(레거시 `save` 또는 `adjust_numbers`): 번호 범위 구간이 없거나(`ZCL_LEG_ORDER_SETUP_###` 재실행), `adjust_numbers`가 레거시를 부르지 않은 것입니다.
- 품목을 추가했는데 헤더 총액이 그대로: `finalize`에서 `determine_totals`를 부르는지 확인하세요. 목록 화면은 DB를 직접 읽으므로 **저장 후에만** 바뀝니다.
- 값 도움말 창이 비어 있음: 서비스 정의에 값 도움말 뷰를 노출했는지 확인하세요.

</details>

#### 12단계. EML 콘솔로 BO 계약 확인하기 + 자주 나는 오류 정리

요구사항

`if_oo_adt_classrun`을 구현한 `ZCL_RAP_ORDER_U_EML_###`를 만들고, 메서드 하나에 시나리오 하나씩 아래를 구현해 콘솔에 결과를 출력하세요.

1. `demo_deep_create`: 주문 1건 + 품목 2건을 **한 번의 MODIFY**로 만듭니다(`%cid` / `%cid_ref`). `mapped`에 나온 **임시 번호**를 출력하고, `COMMIT ENTITIES RESPONSE OF ...`로 저장한 뒤 DB에서 **최종 번호**를 찾아 돌려줍니다.
2. `demo_update_with_control`: `UPDATE FIELDS ( Note )`로 Note만 바꾸면서 일부러 `Requester`에도 값을 넣습니다. 저장 후 READ로 Requester가 **안 바뀐 것**을 확인합니다.
3. `demo_action`: `EXECUTE approveOrder` → `RESULT`의 상태를 출력하고 저장합니다.
4. `demo_disabled_update`: 승인된 주문을 다시 바꾸려 하면 실패합니다. `failed`의 `%fail-cause`와 reported 메시지를 출력합니다.
5. `demo_save_rejected`: 없는 공급업체로 주문을 만들면 MODIFY는 성공하지만 `COMMIT ENTITIES`가 실패(`sy-subrc <> 0`)합니다. LATE 응답을 출력하고 `ROLLBACK ENTITIES`.
6. `demo_rollback`: 주문을 만든 뒤 `ROLLBACK ENTITIES` → DB에 없음을 확인합니다.

마지막으로, 이 문제를 풀며 만난 오류를 아래 해설의 표와 비교해 보세요.

**확인** F9로 실행하면 각 시나리오의 기대 결과(임시 번호 → 최종 번호, Requester 유지, 상태 A, `cause` 값, 저장 거부 메시지, 롤백 후 0건)가 출력됩니다.

<details><summary>정답·해설</summary>

```abap
"! <p class="shorttext synchronized">EML playground for unmanaged order BO ###</p>
CLASS zcl_rap_order_u_eml_### DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_oo_adt_classrun.

  PRIVATE SECTION.
    CONSTANTS c_requester TYPE zleg_ordh_###-requester VALUE 'EML demo ###'.

    DATA out TYPE REF TO if_oo_adt_classrun_out.

    METHODS demo_deep_create
      RETURNING VALUE(rv_order_id) TYPE zleg_ordh_###-order_id.
    METHODS demo_update_with_control
      IMPORTING iv_order_id TYPE zleg_ordh_###-order_id.
    METHODS demo_action
      IMPORTING iv_order_id TYPE zleg_ordh_###-order_id.
    METHODS demo_disabled_update
      IMPORTING iv_order_id TYPE zleg_ordh_###-order_id.
    METHODS demo_save_rejected.
    METHODS demo_rollback.
ENDCLASS.

CLASS zcl_rap_order_u_eml_### IMPLEMENTATION.

  METHOD if_oo_adt_classrun~main.
    me->out = out.

    DATA(lv_order_id) = demo_deep_create( ).
    IF lv_order_id IS INITIAL.
      RETURN.
    ENDIF.
    demo_update_with_control( lv_order_id ).
    demo_action( lv_order_id ).
    demo_disabled_update( lv_order_id ).
    demo_save_rejected( ).
    demo_rollback( ).
  ENDMETHOD.

  "------------------------------------------------------------------
  " 1) 깊은 생성: 주문 + 품목 2건, %cid / %cid_ref
  "------------------------------------------------------------------
  METHOD demo_deep_create.
    out->write( `=== 1) Deep create ===` ).

    DATA(lv_delivery) = CONV d( cl_abap_context_info=>get_system_date( ) + 14 ).

    MODIFY ENTITIES OF zrap_r_order_u_###
      ENTITY Order
        CREATE FIELDS ( Requester SupplierID DeliveryDate CurrencyCode Note )
          WITH VALUE #( ( %cid         = 'ORDER_1'
                          Requester    = c_requester
                          SupplierID   = '070001'
                          DeliveryDate = lv_delivery
                          CurrencyCode = 'EUR'
                          Note         = 'Created by EML' ) )
        CREATE BY \_Items
          FIELDS ( ProductID ItemText Quantity QuantityUnit UnitPrice )
          WITH VALUE #( ( %cid_ref = 'ORDER_1'                 " 같은 요청 안의 새 주문을 가리킴
                          %target  = VALUE #(
                            ( %cid = 'ITEM_1' ProductID = 'BV-0001' ItemText = 'Coffee'
                              Quantity = 2 QuantityUnit = 'EA' UnitPrice = '25.00' )
                            ( %cid = 'ITEM_2' ProductID = 'ML-0001' ItemText = 'Lunch'
                              Quantity = 1 QuantityUnit = 'EA' UnitPrice = '30.00' ) ) ) )
      MAPPED   DATA(ls_mapped)
      FAILED   DATA(ls_failed)
      REPORTED DATA(ls_reported).

    IF ls_failed IS NOT INITIAL.
      LOOP AT ls_reported-order INTO DATA(ls_rep_o).
        out->write( |Order message: { ls_rep_o-%msg->if_message~get_text( ) }| ).
      ENDLOOP.
      LOOP AT ls_reported-item INTO DATA(ls_rep_i).
        out->write( |Item message: { ls_rep_i-%msg->if_message~get_text( ) }| ).
      ENDLOOP.
      ROLLBACK ENTITIES.
      RETURN.
    ENDIF.

    " 아직 저장 전: mapped의 키는 레거시 임시 번호(9000000001부터)
    out->write( |Preliminary OrderID in MAPPED: { ls_mapped-order[ 1 ]-OrderID }| ).
    LOOP AT ls_mapped-item INTO DATA(ls_mapped_item).
      out->write( |  item %cid { ls_mapped_item-%cid } -> { ls_mapped_item-OrderID }/{ ls_mapped_item-ItemNo }| ).
    ENDLOOP.

    COMMIT ENTITIES RESPONSE OF zrap_r_order_u_###
      FAILED   DATA(ls_commit_failed)
      REPORTED DATA(ls_commit_reported).

    IF sy-subrc <> 0.
      out->write( `Save rejected:` ).
      LOOP AT ls_commit_reported-order INTO DATA(ls_late_rep).
        out->write( ls_late_rep-%msg->if_message~get_text( ) ).
      ENDLOOP.
      ROLLBACK ENTITIES.
      RETURN.
    ENDIF.

    " 최종 번호 찾기: 가장 최근에 이 요청자로 만든 주문
    " (임시 키 → 최종 키를 코드로 얻으려면 COMMIT ENTITIES BEGIN과 END 사이에서
    "  CONVERT KEY를 쓴다. %pid를 쓰는 BO의 예: CONVERT KEY OF bdef FROM <mapped>-%pid TO DATA(key).
    "  이 BO처럼 %key에 임시 값을 담는 경우의 문법은 실제 시스템에서 확인 필요)
    SELECT FROM zleg_ordh_###
      FIELDS order_id, status, total_amount, currency_code
      WHERE requester = @c_requester
      ORDER BY created_at DESCENDING
      INTO TABLE @DATA(lt_saved)
      UP TO 1 ROWS.

    IF lt_saved IS NOT INITIAL.
      rv_order_id = lt_saved[ 1 ]-order_id.
      out->write( |Final OrderID in DB: { rv_order_id }, status { lt_saved[ 1 ]-status }, | &&
                  |total { lt_saved[ 1 ]-total_amount } { lt_saved[ 1 ]-currency_code }| ).
    ENDIF.
  ENDMETHOD.

  "------------------------------------------------------------------
  " 2) %control: 보낸 필드만 바뀐다
  "------------------------------------------------------------------
  METHOD demo_update_with_control.
    out->write( `=== 2) Update only Note (%control) ===` ).

    MODIFY ENTITIES OF zrap_r_order_u_###
      ENTITY Order
        UPDATE FIELDS ( Note )                          " %control-Note만 켜진다
        WITH VALUE #( ( OrderID   = iv_order_id
                        Note      = 'Changed by EML'
                        Requester = 'SHOULD NOT BE SAVED' ) )   " %control 꺼짐 → 무시
      FAILED   DATA(ls_failed)
      REPORTED DATA(ls_reported).

    IF ls_failed IS NOT INITIAL.
      out->write( `Update failed` ).
      ROLLBACK ENTITIES.
      RETURN.
    ENDIF.

    COMMIT ENTITIES.

    READ ENTITIES OF zrap_r_order_u_###
      ENTITY Order
        FIELDS ( Requester Note LocalLastChangedAt ) WITH VALUE #( ( OrderID = iv_order_id ) )
      RESULT DATA(lt_orders).

    out->write( |Requester = { lt_orders[ 1 ]-Requester } (unchanged), Note = { lt_orders[ 1 ]-Note }| ).
    out->write( |ETag field LocalLastChangedAt = { lt_orders[ 1 ]-LocalLastChangedAt }| ).
  ENDMETHOD.

  "------------------------------------------------------------------
  " 3) 액션과 결과
  "------------------------------------------------------------------
  METHOD demo_action.
    out->write( `=== 3) Action approveOrder ===` ).

    MODIFY ENTITIES OF zrap_r_order_u_###
      ENTITY Order
        EXECUTE approveOrder FROM VALUE #( ( OrderID = iv_order_id ) )
      RESULT   DATA(lt_result)
      FAILED   DATA(ls_failed)
      REPORTED DATA(ls_reported).

    IF ls_failed IS NOT INITIAL.
      LOOP AT ls_reported-order INTO DATA(ls_rep).
        out->write( |Approve failed: { ls_rep-%msg->if_message~get_text( ) }| ).
      ENDLOOP.
      ROLLBACK ENTITIES.
      RETURN.
    ENDIF.

    out->write( |Result status (before commit): { lt_result[ 1 ]-%param-Status }, | &&
                |criticality { lt_result[ 1 ]-%param-StatusCriticality }| ).
    COMMIT ENTITIES.
  ENDMETHOD.

  "------------------------------------------------------------------
  " 4) 기능 제어/레거시 상태 검사로 거부되는 변경
  "------------------------------------------------------------------
  METHOD demo_disabled_update.
    out->write( `=== 4) Update an approved order ===` ).

    MODIFY ENTITIES OF zrap_r_order_u_###
      ENTITY Order
        UPDATE FIELDS ( Note ) WITH VALUE #( ( OrderID = iv_order_id Note = 'Too late' ) )
      FAILED   DATA(ls_failed)
      REPORTED DATA(ls_reported).

    LOOP AT ls_failed-order INTO DATA(ls_fail).
      out->write( |Failed OrderID { ls_fail-OrderID }, %fail-cause = { ls_fail-%fail-cause }| ).
    ENDLOOP.
    LOOP AT ls_reported-order INTO DATA(ls_rep).
      out->write( |Message: { ls_rep-%msg->if_message~get_text( ) }| ).
    ENDLOOP.

    ROLLBACK ENTITIES.
  ENDMETHOD.

  "------------------------------------------------------------------
  " 5) check_before_save가 거부하는 저장
  "------------------------------------------------------------------
  METHOD demo_save_rejected.
    out->write( `=== 5) Save rejected by check_before_save ===` ).

    MODIFY ENTITIES OF zrap_r_order_u_###
      ENTITY Order
        CREATE FIELDS ( Requester SupplierID CurrencyCode )
        WITH VALUE #( ( %cid = 'BAD' Requester = c_requester SupplierID = '999999' CurrencyCode = 'EUR' ) )
      MAPPED DATA(ls_mapped)
      FAILED DATA(ls_failed).

    out->write( |MODIFY failed? { COND string( WHEN ls_failed IS INITIAL THEN `no` ELSE `yes` ) }| &&
                | (the supplier is only checked at save)| ).

    COMMIT ENTITIES RESPONSE OF zrap_r_order_u_###
      FAILED   DATA(ls_commit_failed)
      REPORTED DATA(ls_commit_reported).

    out->write( |COMMIT sy-subrc = { sy-subrc }| ).
    LOOP AT ls_commit_failed-order INTO DATA(ls_late_fail).
      out->write( |Failed (LATE) OrderID { ls_late_fail-OrderID }| ).
    ENDLOOP.
    LOOP AT ls_commit_reported-order INTO DATA(ls_late_rep).
      out->write( |Message (LATE): { ls_late_rep-%msg->if_message~get_text( ) }| ).
    ENDLOOP.

    " 거부된 트랜잭션 버퍼는 직접 버려야 한다
    ROLLBACK ENTITIES.
  ENDMETHOD.

  "------------------------------------------------------------------
  " 6) ROLLBACK ENTITIES: 버퍼 폐기 (cleanup 호출)
  "------------------------------------------------------------------
  METHOD demo_rollback.
    out->write( `=== 6) Rollback ===` ).

    MODIFY ENTITIES OF zrap_r_order_u_###
      ENTITY Order
        CREATE FIELDS ( Requester SupplierID CurrencyCode )
        WITH VALUE #( ( %cid = 'TMP' Requester = 'Rollback demo ###' SupplierID = '070001' CurrencyCode = 'EUR' ) ).

    ROLLBACK ENTITIES.

    SELECT COUNT(*) FROM zleg_ordh_### WHERE requester = 'Rollback demo ###' INTO @DATA(lv_count).
    out->write( |Orders with requester 'Rollback demo ###' in DB: { lv_count } (expected 0)| ).
  ENDMETHOD.

ENDCLASS.
```

예상 출력(번호는 환경마다 다름, 콘솔의 한 줄을 한 항목으로 적음)

- `=== 1) Deep create ===`
- `Preliminary OrderID in MAPPED: 9000000001`
- `  item %cid ITEM_1 -> 9000000001/0010`
- `  item %cid ITEM_2 -> 9000000001/0020`
- `Final OrderID in DB: 0000000004, status N, total 80.00 EUR`
- `=== 2) Update only Note (%control) ===`
- `Requester = EML demo ### (unchanged), Note = Changed by EML`
- `ETag field LocalLastChangedAt = (실행 시각의 타임스탬프)`
- `=== 3) Action approveOrder ===`
- `Result status (before commit): A, criticality 3`
- `=== 4) Update an approved order ===`
- `Failed OrderID 0000000004, %fail-cause = (disabled 또는 unspecific, 아래 해설 참고)`
- `Message: (기능 제어 거부 메시지 또는 레거시 메시지 031)`
- `=== 5) Save rejected by check_before_save ===`
- `MODIFY failed? no (the supplier is only checked at save)`
- `COMMIT sy-subrc = 4`
- `Failed (LATE) OrderID 9000000001`
- `Message (LATE): Supplier 999999 does not exist.`
- `=== 6) Rollback ===`
- `Orders with requester 'Rollback demo ###' in DB: 0 (expected 0)`

왜 이렇게 쓰나

- 시나리오 4의 `%fail-cause`는 두 가지 중 하나입니다. 프레임워크가 동적 기능 제어(`%update` disabled)를 먼저 적용하면 `disabled` 원인으로 핸들러 호출 없이 거부되고, 그렇지 않으면 레거시 메시지 031이 `unspecific`으로 돌아옵니다. 어느 쪽인지 출력으로 확인해 보세요(EML 호출에 동적 기능 제어가 강제되는지는 실제 시스템에서 확인 필요). **어느 경우든 레거시의 상태 검사가 마지막 방어선**이라는 점이 중요합니다.
- 시나리오 5: 필드 사이의 관계나 마스터 존재 같은 검사는 **저장 시점**에 일어나므로 MODIFY는 성공하고 COMMIT이 실패합니다. 실패한 COMMIT 뒤에는 버퍼가 그대로 남아 있으므로 `ROLLBACK ENTITIES`로 버려야 다음 시나리오가 깨끗하게 시작됩니다. LATE 응답의 `OrderID`는 아직 임시 번호입니다(`adjust_numbers` 전에 거부됨).
- 시나리오 1에서 공급업체 `070001`, 제품 `BV-0001`/`ML-0001`, 단위 `EA`는 `/DMO` 데모 데이터와 `I_UnitOfMeasure`에 보통 있는 값입니다. 없으면 Data Preview로 실제 값을 찾아 바꾸세요.

자주 나는 오류와 해결 (R-06 전체)

| 증상 | 원인 | 해결 |
|---|---|---|
| 활성화: "Method CREATE ... not implemented" | BDEF에 선언했는데 핸들러에 메서드가 없음 | 5단계 정의와 BDEF를 대조하거나 BDEF 줄에서 퀵픽스로 추가 |
| 런타임 `BEHAVIOR_ILLEGAL_STATEMENT` | 핸들러/세이버 안의 `COMMIT WORK`, 잘못된 단계의 DB 쓰기 | DB 쓰기는 `save`에서만, COMMIT은 하지 않기 |
| 생성 후 응답에서 "instance not found" | `mapped`의 키와 read가 찾는 키가 다름 | `mapped-order-OrderID` = 레거시가 돌려준 번호인지 확인 |
| 저장 후 DB에 9000000001 번호 | `adjust_numbers`가 매핑을 안 돌려주거나 레거시를 안 부름 | 레거시 `save`의 ASSERT가 원래 막아 줌. 세이버 `adjust_numbers` 확인 |
| 품목 생성 성공인데 저장 시 덤프 | 품목 매핑 누락(late numbering 엔터티는 생성분 전부 매핑 필요) | R-05 10단계의 a=a 매핑 보강 확인 |
| UPDATE가 아무 필드도 안 바꿈 | X 구조로 `%control`이 안 옮겨짐 | BDEF `mapping ... control` 지정과 `_intx = CORRESPONDING #( ... MAPPING FROM ENTITY )` 확인 |
| 필드 메시지가 필드에 안 붙음 | `%element` 컴포넌트 이름 불일치 | CDS 별칭이 "DB 이름에서 밑줄 제거" 규칙인지 확인 |
| ETag 충돌이 안 잡힘 | 품목 변경 때 헤더 `local_last_changed_at`을 안 바꿈 | 레거시 `update_order`의 `_set_admin` 확인 |
| Fiori 버튼이 항상 활성 | `features : instance`를 BDEF에서 빠뜨렸거나 프로젝션 BDEF에 `use action` 누락 | BDEF/프로젝션 BDEF 대조 |

</details>

### R-07. Unmanaged + Draft, 그리고 unmanaged BO 단위 테스트 [작성] ★★★
<!-- covers: with draft, draft table, sych_bdl_draft_admin_inc, %is_draft, %tky, early numbering, FOR NUMBERING, earlynumbering_create, earlynumbering_cba, total etag, draft action Edit/Activate optimized/Discard/Resume, draft determine action Prepare, determination on modify, validation on save, %state_area, %path, %element, IN LOCAL MODE, association with draft, use draft, 프로젝션 draft BDEF, draft와 active의 핸들러 호출 순서, ABAP Unit, FOR TESTING, CREATE OBJECT FOR TESTING, FRIENDS, DEFINITION DEFERRED, RESPONSE FOR MAPPED/FAILED/REPORTED EARLY/LATE, 테스트 대역(fake), 의존성 주입, cl_abap_testdouble, cl_osql_test_environment, COMMIT ENTITIES 통합 테스트, cl_botd_txbufdbl_bo_test_env, @testing BDEF -->
**목표**

- 레거시를 감싼 unmanaged BO에 draft를 붙일 때 BDEF·테이블·핸들러에서 **무엇이 바뀌는지**(early numbering, draft 테이블, total etag, draft 액션, Prepare) 설명하고 구현할 수 있습니다.
- draft 인스턴스는 프레임워크가, active 인스턴스는 unmanaged 핸들러가 처리한다는 분업을 이해하고, 어떤 Fiori 동작에서 어떤 핸들러가 불리는지 직접 확인할 수 있습니다.
- draft BO에서 determination(on modify)과 validation(on save, `%state_area`, `%path`)을 구현할 수 있습니다.
- R-06 행동 풀의 핸들러·세이버 메서드를 **레거시 없이**(가짜 레거시 주입) 단위 테스트할 수 있습니다.
- `cl_abap_testdouble`, `cl_osql_test_environment` + `COMMIT ENTITIES` 통합 테스트, `cl_botd_txbufdbl_bo_test_env`(BO 소비자 테스트)의 쓰임새를 구분할 수 있습니다.

**전제**

- R-05, R-06을 끝냈습니다. 레거시 `ZCL_LEG_ORDER_###`와 R-06의 BO `ZRAP_R_ORDER_U_###`, 행동 풀 `ZBP_RAP_R_ORDER_U_###`, 보조 클래스 `ZCM_LEG_ORDER_###`, `ZCL_RAP_ORDER_AUX_###`가 활성화되어 있습니다.
- 앞쪽(1~8단계)은 **새 BO** `ZRAP_R_ORDER_UD_###` 계열을 만듭니다. CDS 엔터티는 BO 하나에만 속할 수 있으므로 R-06의 뷰를 재사용하지 않고 새로 만듭니다. 같은 레거시 테이블·클래스를 감쌉니다.
- 뒤쪽(9~12단계)은 **R-06의 행동 풀**에 테스트 클래스를 붙입니다.

**만들 객체**

| 순서 | 객체 유형 | 이름 | 역할 |
|---|---|---|---|
| 1 | DB 테이블(draft) | `ZRAP_DORDH_###`, `ZRAP_DORDI_###` | 주문/품목 draft 테이블 |
| 2 | CDS 뷰 | `ZRAP_R_ORDER_UD_###`, `ZRAP_R_ORDITEM_UD_###` | draft BO의 R 뷰 |
| 3 | CDS 프로젝션 + MDE | `ZRAP_C_ORDER_UD_###`, `ZRAP_C_ORDITEM_UD_###` | UI 프로젝션 |
| 4 | 행동 정의 | `ZRAP_R_ORDER_UD_###`, `ZRAP_C_ORDER_UD_###` | unmanaged + draft BDEF, 프로젝션 BDEF |
| 5 | 행동 풀 | `ZBP_RAP_R_ORDER_UD_###` | numbering, active 핸들러, determination/validation, 세이버 |
| 6 | 서비스 정의 / 바인딩 | `ZRAP_UI_ORDER_UD_###` / `ZRAP_UI_ORDER_UD_O4_###` | OData V4 UI |
| 7 | 테스트 클래스(로컬) | R-06 행동 풀 `ZBP_RAP_R_ORDER_U_###`의 Test Classes 탭 | 가짜 레거시, 핸들러/세이버/통합 테스트 |
| 8 | 클래스 + 테스트 | `ZCL_RAP_ORDER_STATS_###` | BO를 EML로 쓰는 소비자 클래스와 트랜잭션 버퍼 대역 테스트 |

> **draft에서 누가 무엇을 하나**: draft 인스턴스(`%is_draft = 01`)의 생성·변경·삭제·읽기는 RAP 프레임워크가 **draft 테이블**로 직접 처리합니다. unmanaged 핸들러(create/update/delete/read/rba/cba)는 **active 인스턴스**에 대해서만 불립니다. Activate할 때 프레임워크가 draft 내용을 active 쪽 핸들러 호출(create/update/delete/cba)로 바꿔 부르고, 그 뒤에 세이버가 돕니다. 이 분업은 SAP 문서의 설명을 바탕으로 한 것이며, 정확한 호출 순서는 8단계에서 브레이크포인트로 직접 확인합니다(실제 시스템에서 확인 필요).

#### 1단계. draft 테이블 두 개 만들기

요구사항

1. draft 테이블은 **CDS 요소 이름(별칭)** 을 필드 이름으로 씁니다. 타입은 레거시 테이블과 같게 맞춥니다.
2. 키: 주문은 `client` + `orderid`, 품목은 `client` + `orderid` + `itemno`. 이 BO는 **early numbering**이므로 `DRAFTUUID` 같은 추가 키가 필요 없습니다(치트시트 BDL 문서: late numbering일 때만 추가 키 필요).
3. 계산 필드 `statuscriticality`(int1)도 CDS 요소이므로 draft 테이블에 둡니다.
4. 마지막에 draft 관리 정보 `"%admin" : include sych_bdl_draft_admin_inc;`를 넣습니다.
5. 실무에서는 BDEF의 `draft table` 이름에서 퀵픽스 "Create draft table"로 만드는 것이 가장 안전합니다. 퀵픽스 결과가 아래 표와 같은지 비교해 보세요.

주문 draft 테이블 `ZRAP_DORDH_###`

| 필드 | 키 | 데이터 엘리먼트(또는 내장 타입) | 타입 | 길이 | 소수 | 설명 |
|---|---|---|---|---|---|---|
| client | ✔ | `mandt` | CLNT | 3 | 0 | 클라이언트 |
| orderid | ✔ | `zleg_order_id_###` | NUMC | 10 | 0 | 주문 번호 (early numbering으로 즉시 최종 번호) |
| requester |  | `abap.char(40)` | CHAR | 40 | 0 | 요청자 |
| supplierid |  | `/dmo/agency_id` | NUMC | 6 | 0 | 공급업체 |
| orderdate |  | `abap.dats` | DATS | 8 | 0 | 주문일 |
| deliverydate |  | `abap.dats` | DATS | 8 | 0 | 납기일 |
| totalamount |  | `/dmo/total_price` | CURR | 16 | 2 | 총액 (참조: currencycode) |
| currencycode |  | `/dmo/currency_code` | CUKY | 5 | 0 | 통화 |
| status |  | `abap.char(1)` | CHAR | 1 | 0 | 상태 |
| statuscriticality |  | `abap.int1` | INT1 | 3 | 0 | 상태 색 (계산 필드) |
| note |  | `abap.char(255)` | CHAR | 255 | 0 | 메모 |
| createdby |  | `abp_creation_user` | CHAR | 12 | 0 | 생성자 |
| createdat |  | `abp_creation_tstmpl` | DEC | 21 | 7 | 생성 시각 |
| lastchangedby |  | `abp_locinst_lastchange_user` | CHAR | 12 | 0 | 최종 변경자 |
| locallastchangedat |  | `abp_locinst_lastchange_tstmpl` | DEC | 21 | 7 | 인스턴스 최종 변경 시각 (etag master) |
| lastchangedat |  | `abp_lastchange_tstmpl` | DEC | 21 | 7 | 최종 변경 시각 (total etag) |
| %admin |  | `sych_bdl_draft_admin_inc` (include) | - | - | - | draft 관리 정보 |

품목 draft 테이블 `ZRAP_DORDI_###`

| 필드 | 키 | 데이터 엘리먼트(또는 내장 타입) | 타입 | 길이 | 소수 | 설명 |
|---|---|---|---|---|---|---|
| client | ✔ | `mandt` | CLNT | 3 | 0 | 클라이언트 |
| orderid | ✔ | `zleg_order_id_###` | NUMC | 10 | 0 | 주문 번호 |
| itemno | ✔ | `abap.numc(4)` | NUMC | 4 | 0 | 품목 번호 |
| productid |  | `/dmo/supplement_id` | CHAR | 10 | 0 | 제품 |
| itemtext |  | `abap.char(40)` | CHAR | 40 | 0 | 품목 설명 |
| quantity |  | `abap.quan(13,3)` | QUAN | 13 | 3 | 수량 (참조: quantityunit) |
| quantityunit |  | `abap.unit(3)` | UNIT | 3 | 0 | 단위 |
| unitprice |  | `abap.curr(15,2)` | CURR | 15 | 2 | 단가 (참조: currencycode) |
| itemamount |  | `abap.curr(15,2)` | CURR | 15 | 2 | 품목 금액 (참조: currencycode) |
| currencycode |  | `/dmo/currency_code` | CUKY | 5 | 0 | 통화 |
| %admin |  | `sych_bdl_draft_admin_inc` (include) | - | - | - | draft 관리 정보 |

**직접 추가할 어노테이션**

- `@EndUserText.label`, `@AbapCatalog.enhancement.category`, `@AbapCatalog.tableCategory`, `@AbapCatalog.deliveryClass`, `@AbapCatalog.dataMaintenance` — R-05와 같은 테이블 기본 속성
- `@Semantics.amount.currencyCode` / `@Semantics.quantity.unitOfMeasure` — 금액·수량의 참조 필드

**확인** 두 테이블이 활성화됩니다. (BDEF가 아직 없으므로 퀵픽스 대신 직접 만들었다면, 4단계에서 BDEF를 활성화할 때 "draft table does not match" 류의 오류가 없어야 합니다.)

<details><summary>정답·해설</summary>

```cds
@EndUserText.label : 'Draft: purchase order (unmanaged) ###'
@AbapCatalog.enhancement.category : #EXTENSIBLE_ANY      // draft 테이블은 퀵픽스가 이렇게 만든다
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table zrap_dordh_### {
  key client         : mandt not null;
  key orderid        : zleg_order_id_### not null;
  requester          : abap.char(40);
  supplierid         : /dmo/agency_id;
  orderdate          : abap.dats;
  deliverydate       : abap.dats;
  @Semantics.amount.currencyCode : 'zrap_dordh_###.currencycode'
  totalamount        : /dmo/total_price;
  currencycode       : /dmo/currency_code;
  status             : abap.char(1);
  statuscriticality  : abap.int1;
  note               : abap.char(255);
  createdby          : abp_creation_user;
  createdat          : abp_creation_tstmpl;
  lastchangedby      : abp_locinst_lastchange_user;
  locallastchangedat : abp_locinst_lastchange_tstmpl;
  lastchangedat      : abp_lastchange_tstmpl;
  "%admin"           : include sych_bdl_draft_admin_inc;   // draft 관리 정보 (만든 사람, 잠금 시각 등)
}
```

```cds
@EndUserText.label : 'Draft: purchase order item (unmanaged) ###'
@AbapCatalog.enhancement.category : #EXTENSIBLE_ANY
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table zrap_dordi_### {
  key client     : mandt not null;
  key orderid    : zleg_order_id_### not null;
  key itemno     : abap.numc(4) not null;
  productid      : /dmo/supplement_id;
  itemtext       : abap.char(40);
  @Semantics.quantity.unitOfMeasure : 'zrap_dordi_###.quantityunit'
  quantity       : abap.quan(13,3);
  quantityunit   : abap.unit(3);
  @Semantics.amount.currencyCode : 'zrap_dordi_###.currencycode'
  unitprice      : abap.curr(15,2);
  @Semantics.amount.currencyCode : 'zrap_dordi_###.currencycode'
  itemamount     : abap.curr(15,2);
  currencycode   : /dmo/currency_code;
  "%admin"       : include sych_bdl_draft_admin_inc;
}
```

왜 이렇게 쓰나

- **draft 테이블은 CDS의 모양을 따릅니다.** 치트시트 BDL 문서는 "draft 테이블은 CDS 엔터티의 필드를 반영해야 하고, 별칭이 있으면 별칭 이름을 써야 하며, 타입이 호환되어야 하고, client 필드가 있어야 한다"고 설명합니다. 공식 `/DMO/D_TRAVEL_D`도 `TRAVELID`, `AGENCYID`처럼 CDS 이름을 필드 이름으로 씁니다.
- active 데이터는 여전히 **레거시 테이블**(`ZLEG_ORDH_###`)에 있습니다. draft 테이블은 프레임워크 전용 작업 공간입니다. 같은 문서가 "draft 테이블을 ABAP SQL로 직접 읽거나 바꾸지 말 것"을 권합니다.
- `%admin` include에는 draft를 만든 사용자, 마지막 변경 시각, 잠금 상태 같은 관리 정보가 들어 있습니다. 직접 채우지 않습니다.
- `@AbapCatalog.enhancement.category`는 퀵픽스가 만드는 값(`#EXTENSIBLE_ANY`)을 그대로 두었습니다. 확장 계획이 없으면 `#NOT_EXTENSIBLE`로 바꿔도 됩니다(퀵픽스 생성값은 시스템 버전에 따라 다를 수 있음, 확인 필요).

</details>

#### 2단계. draft BO의 R 뷰 두 개 만들기

요구사항

1. `ZRAP_R_ORDER_UD_###`(루트)와 `ZRAP_R_ORDITEM_UD_###`(자식)를 만드세요. 필드·연관·계산 필드는 R-06 2단계와 **완전히 같고**, 컴포지션/부모 연관의 대상만 UD 뷰로 바꿉니다.
2. 두 뷰를 함께 활성화합니다.

**직접 추가할 어노테이션**

- `@AccessControl.authorizationCheck`, `@EndUserText.label`, `@Metadata.ignorePropagatedAnnotations` — 뷰 기본 속성
- `@Semantics.amount.currencyCode`, `@Semantics.quantity.unitOfMeasure` — 금액·수량 참조
- `@Semantics.user.createdBy`, `@Semantics.systemDateTime.createdAt`, `@Semantics.user.localInstanceLastChangedBy`, `@Semantics.systemDateTime.localInstanceLastChangedAt`, `@Semantics.systemDateTime.lastChangedAt` — 관리 필드 의미 (draft에서는 특히 마지막 두 개가 ETag / total ETag 역할과 연결됨)

**확인** 두 뷰가 활성화되고 Data Preview에 R-06과 같은 데이터가 보입니다(같은 레거시 테이블을 읽기 때문).

<details><summary>정답·해설</summary>

```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Purchase order (unmanaged, draft) ###'
@Metadata.ignorePropagatedAnnotations: true
define root view entity ZRAP_R_ORDER_UD_###
  as select from zleg_ordh_###

  composition [0..*] of ZRAP_R_ORDITEM_UD_### as _Items

  association [0..1] to /DMO/I_Agency as _Supplier
    on $projection.SupplierID = _Supplier.AgencyID
  association [0..1] to I_Currency    as _Currency
    on $projection.CurrencyCode = _Currency.Currency
{
  key order_id              as OrderID,
      requester             as Requester,
      supplier_id           as SupplierID,
      order_date            as OrderDate,
      delivery_date         as DeliveryDate,
      @Semantics.amount.currencyCode: 'CurrencyCode'
      total_amount          as TotalAmount,
      currency_code         as CurrencyCode,
      status                as Status,
      case status
        when 'A' then 3
        when 'C' then 3
        when 'R' then 1
        else 2
      end                   as StatusCriticality,
      note                  as Note,
      @Semantics.user.createdBy: true
      created_by            as CreatedBy,
      @Semantics.systemDateTime.createdAt: true
      created_at            as CreatedAt,
      @Semantics.user.localInstanceLastChangedBy: true
      last_changed_by       as LastChangedBy,
      @Semantics.systemDateTime.localInstanceLastChangedAt: true   // etag master
      local_last_changed_at as LocalLastChangedAt,
      @Semantics.systemDateTime.lastChangedAt: true                // total etag
      last_changed_at       as LastChangedAt,

      _Items,
      _Supplier,
      _Currency
}
```

```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Purchase order item (unmanaged, draft) ###'
@Metadata.ignorePropagatedAnnotations: true
define view entity ZRAP_R_ORDITEM_UD_###
  as select from zleg_ordi_###

  association to parent ZRAP_R_ORDER_UD_### as _Order
    on $projection.OrderID = _Order.OrderID
  association [0..1] to /DMO/I_Supplement   as _Product
    on $projection.ProductID = _Product.SupplementID
{
  key order_id      as OrderID,
  key item_no       as ItemNo,
      product_id    as ProductID,
      item_text     as ItemText,
      @Semantics.quantity.unitOfMeasure: 'QuantityUnit'
      quantity      as Quantity,
      quantity_unit as QuantityUnit,
      @Semantics.amount.currencyCode: 'CurrencyCode'
      unit_price    as UnitPrice,
      @Semantics.amount.currencyCode: 'CurrencyCode'
      item_amount   as ItemAmount,
      currency_code as CurrencyCode,

      _Order,
      _Product
}
```

왜 이렇게 쓰나

- 같은 테이블 위에 BO를 두 개 만드는 것은 **실습을 위한 것**입니다. 실무에서는 같은 데이터에 트랜잭션 BO가 둘이면 잠금·검증이 갈라질 수 있으므로 하나만 둡니다. 여기서는 두 BO가 **같은 레거시 클래스와 같은 잠금 객체**를 쓰므로 데이터 일관성은 레거시가 지켜 줍니다.
- draft 쿼리(목록 화면)는 프레임워크가 active(CDS → 레거시 테이블)와 draft(draft 테이블)를 합쳐서 보여 줍니다. 그래서 draft 테이블의 필드가 CDS 요소와 1:1로 맞아야 합니다.

</details>

#### 3단계. 프로젝션 뷰 두 개와 MDE 두 개 만들기

요구사항

1. `ZRAP_C_ORDER_UD_###`, `ZRAP_C_ORDITEM_UD_###`를 R-06 3단계와 같은 구조로 만들되 대상 뷰 이름을 UD로 바꿉니다.
2. MDE도 같은 구조로 만들되, 상세 화면 `identification`에서 `copyOrder` 버튼은 뺍니다(이 BO에는 복사가 없습니다). draft 버튼(Edit, Save, Discard)은 Fiori가 자동으로 그립니다.

**직접 추가할 어노테이션**

- `@Metadata.allowExtensions`, `@Search.searchable`, `@Search.defaultSearchElement`, `@Consumption.valueHelpDefinition`, `@ObjectModel.text.element` — 프로젝션 (R-06과 같은 목적)
- `@Metadata.layer`, `@UI.headerInfo`, `@UI.facet`, `@UI.lineItem`, `@UI.identification`, `@UI.fieldGroup`, `@UI.selectionField`, `@UI.hidden`, `@UI.textArrangement` — MDE

**확인** 네 객체가 활성화됩니다.

<details><summary>정답·해설</summary>

```cds
@EndUserText.label: 'Purchase order (unmanaged, draft) - projection ###'
@AccessControl.authorizationCheck: #NOT_REQUIRED
@Metadata.allowExtensions: true
@Search.searchable: true
define root view entity ZRAP_C_ORDER_UD_###
  provider contract transactional_query
  as projection on ZRAP_R_ORDER_UD_###
{
  key OrderID,
      @Search.defaultSearchElement: true
      Requester,
      @Consumption.valueHelpDefinition: [{ entity: { name: '/DMO/I_Agency_StdVH', element: 'AgencyID' },
                                           useForValidation: true }]
      @ObjectModel.text.element: ['SupplierName']
      @Search.defaultSearchElement: true
      SupplierID,
      _Supplier.Name as SupplierName,
      OrderDate,
      DeliveryDate,
      TotalAmount,
      @Consumption.valueHelpDefinition: [{ entity: { name: 'I_CurrencyStdVH', element: 'Currency' },
                                           useForValidation: true }]
      CurrencyCode,
      Status,
      StatusCriticality,
      Note,
      CreatedBy,
      CreatedAt,
      LastChangedBy,
      LocalLastChangedAt,
      LastChangedAt,

      _Items : redirected to composition child ZRAP_C_ORDITEM_UD_###,
      _Supplier,
      _Currency
}
```

```cds
@EndUserText.label: 'Purchase order item (unmanaged, draft) - projection ###'
@AccessControl.authorizationCheck: #NOT_REQUIRED
@Metadata.allowExtensions: true
define view entity ZRAP_C_ORDITEM_UD_###
  as projection on ZRAP_R_ORDITEM_UD_###
{
  key OrderID,
  key ItemNo,
      @Consumption.valueHelpDefinition: [{ entity: { name: '/DMO/I_Supplement_StdVH', element: 'SupplementID' },
                                           useForValidation: true }]
      @ObjectModel.text.element: ['ProductText']
      ProductID,
      _Product._SupplementText[1: LanguageCode = $session.system_language].Description as ProductText,
      ItemText,
      Quantity,
      @Consumption.valueHelpDefinition: [{ entity: { name: 'I_UnitOfMeasure', element: 'UnitOfMeasure' } }]
      QuantityUnit,
      UnitPrice,
      ItemAmount,
      CurrencyCode,

      _Order : redirected to parent ZRAP_C_ORDER_UD_###,
      _Product
}
```

```cds
@Metadata.layer: #CORE
@UI.headerInfo: { typeName: 'Purchase Order',
                  typeNamePlural: 'Purchase Orders (Draft)',
                  title:       { type: #STANDARD, value: 'OrderID' },
                  description: { type: #STANDARD, value: 'Requester' } }
annotate entity ZRAP_C_ORDER_UD_### with
{
  @UI.facet: [ { id: 'General', purpose: #STANDARD, type: #IDENTIFICATION_REFERENCE,
                 label: 'General Information', position: 10 },
               { id: 'Items',   purpose: #STANDARD, type: #LINEITEM_REFERENCE,
                 label: 'Items', position: 20, targetElement: '_Items' },
               { id: 'Admin',   purpose: #STANDARD, type: #FIELDGROUP_REFERENCE,
                 label: 'Administrative Data', position: 30, targetQualifier: 'Admin' } ]

  @UI: { lineItem:       [ { position: 10, importance: #HIGH },
                           { type: #FOR_ACTION, dataAction: 'approveOrder', label: 'Approve' },
                           { type: #FOR_ACTION, dataAction: 'rejectOrder',  label: 'Reject' } ],
         identification: [ { position: 10 },
                           { type: #FOR_ACTION, dataAction: 'approveOrder', label: 'Approve' },
                           { type: #FOR_ACTION, dataAction: 'rejectOrder',  label: 'Reject' } ],
         selectionField: [ { position: 10 } ] }
  OrderID;

  @UI: { lineItem: [ { position: 20, importance: #HIGH } ], identification: [ { position: 20 } ],
         selectionField: [ { position: 20 } ] }
  Requester;

  @UI: { lineItem: [ { position: 30, importance: #HIGH } ], identification: [ { position: 30 } ],
         selectionField: [ { position: 30 } ], textArrangement: #TEXT_LAST }
  SupplierID;

  @UI.hidden: true
  SupplierName;

  @UI: { lineItem: [ { position: 40 } ], identification: [ { position: 40 } ] }
  OrderDate;

  @UI: { lineItem: [ { position: 50 } ], identification: [ { position: 50 } ] }
  DeliveryDate;

  @UI: { lineItem: [ { position: 60, importance: #HIGH } ], identification: [ { position: 60 } ] }
  TotalAmount;

  @UI.identification: [ { position: 65 } ]
  CurrencyCode;

  @UI: { lineItem:       [ { position: 70, importance: #HIGH, criticality: 'StatusCriticality' } ],
         identification: [ { position: 70, criticality: 'StatusCriticality' } ],
         selectionField: [ { position: 40 } ] }
  Status;

  @UI.hidden: true
  StatusCriticality;

  @UI.identification: [ { position: 80, label: 'Note' } ]
  Note;

  @UI.fieldGroup: [ { qualifier: 'Admin', position: 10 } ]
  CreatedBy;
  @UI.fieldGroup: [ { qualifier: 'Admin', position: 20 } ]
  CreatedAt;
  @UI.fieldGroup: [ { qualifier: 'Admin', position: 30 } ]
  LastChangedBy;
  @UI.fieldGroup: [ { qualifier: 'Admin', position: 40 } ]
  LocalLastChangedAt;
  @UI.fieldGroup: [ { qualifier: 'Admin', position: 50 } ]
  LastChangedAt;
}
```

```cds
@Metadata.layer: #CORE
@UI.headerInfo: { typeName: 'Item', typeNamePlural: 'Items',
                  title: { type: #STANDARD, value: 'ItemNo' } }
annotate entity ZRAP_C_ORDITEM_UD_### with
{
  @UI.facet: [ { id: 'Item', purpose: #STANDARD, type: #IDENTIFICATION_REFERENCE,
                 label: 'Item', position: 10 } ]

  @UI: { lineItem: [ { position: 10, importance: #HIGH } ], identification: [ { position: 10 } ] }
  ItemNo;

  @UI: { lineItem: [ { position: 20, importance: #HIGH } ], identification: [ { position: 20 } ],
         textArrangement: #TEXT_LAST }
  ProductID;

  @UI.hidden: true
  ProductText;

  @UI: { lineItem: [ { position: 30 } ], identification: [ { position: 30 } ] }
  ItemText;

  @UI: { lineItem: [ { position: 40, importance: #HIGH } ], identification: [ { position: 40 } ] }
  Quantity;

  @UI: { lineItem: [ { position: 50 } ], identification: [ { position: 50 } ] }
  UnitPrice;

  @UI: { lineItem: [ { position: 60, importance: #HIGH } ], identification: [ { position: 60 } ] }
  ItemAmount;
}
```

왜 이렇게 쓰나

- 프로젝션 CDS에는 draft 전용 문법이 없습니다. draft는 **BDEF**(`with draft;`, 프로젝션 BDEF의 `use draft;`)에서 켭니다. Fiori Elements는 OData 메타데이터에서 draft 지원을 읽고 Edit/Save/Discard 버튼과 "Draft" 표시를 자동으로 그립니다.
- `LastChangedAt`을 관리 정보 섹션에 보이게 둔 이유: Activate할 때마다 바뀌는 값(total ETag)이 실제로 바뀌는지 눈으로 확인하기 위해서입니다.

</details>

#### 4단계. unmanaged + draft BDEF와 프로젝션 BDEF

요구사항

1. BDEF `ZRAP_R_ORDER_UD_###`: 머리글에 `unmanaged implementation in class zbp_rap_r_order_ud_### unique;`, `strict ( 2 );`, **`with draft;`**.
2. 주문(`alias Order`)
   - `draft table zrap_dordh_###`, **`early numbering`**, `lock master`, **`total etag LastChangedAt`**, `authorization master ( global, instance )`, `etag master LocalLastChangedAt`
   - create, `update ( features : instance )`, `delete ( features : instance )`
   - 읽기 전용/필수 필드는 R-06과 같게. 단 `CurrencyCode`는 정적 필수.
   - `association _Items { create ( features : instance, authorization : update ); with draft; }`
   - 액션 `approveOrder`, `rejectOrder`(`features : instance`, `result [1] $self`)
   - determination `setDefaults on modify { create; }` — draft를 만들자마자 주문일·상태가 보이게
   - validation `validateHeader on save { create; field SupplierID, OrderDate, DeliveryDate, CurrencyCode; }`
   - draft 액션 `Edit`, `Activate optimized`, `Discard`, `Resume`, 그리고 `draft determine action Prepare { validation validateHeader; validation Item~validateItem; }`
   - `mapping for zleg_ordh_### control zleg_s_ordh_x_###`
3. 품목(`alias Item`)
   - `draft table zrap_dordi_###`, `early numbering`, `lock dependent by _Order`, `authorization dependent by _Order`, `etag dependent by _Order`
   - update/delete(`features : instance`), `association _Order { with draft; }`
   - determination `calculateAmounts on modify { create; field Quantity, UnitPrice; }`
   - validation `validateItem on save { create; field ProductID, Quantity, QuantityUnit, UnitPrice; }`
   - `mapping for zleg_ordi_### control zleg_s_ordi_x_###`
4. 프로젝션 BDEF `ZRAP_C_ORDER_UD_###`: `use draft;`, draft 액션 5개 `use action`, `use association _Items { create; with draft; }`, 품목 `use association _Order { with draft; }`.

**확인** 두 BDEF를 저장하면 남는 오류는 "구현 클래스 없음"뿐입니다. (draft 테이블이 BDEF와 맞지 않으면 여기서 오류가 납니다.)

<details><summary>정답·해설</summary>

```bdef
unmanaged implementation in class zbp_rap_r_order_ud_### unique;
strict ( 2 );
with draft;                                       // 이 BO는 draft를 지원한다

define behavior for ZRAP_R_ORDER_UD_### alias Order
draft table zrap_dordh_###                        // draft 인스턴스 저장소 (프레임워크 전용)
early numbering                                   // 키를 생성 즉시(FOR NUMBERING) 확정
lock master
total etag LastChangedAt                          // draft 재개(Resume) 가능 여부 판단용
authorization master ( global, instance )
etag master LocalLastChangedAt                    // OData 낙관적 잠금
{
  create;
  update ( features : instance );
  delete ( features : instance );

  field ( readonly ) OrderID, Status, TotalAmount, StatusCriticality,
                     CreatedBy, CreatedAt, LastChangedBy, LocalLastChangedAt, LastChangedAt;
  field ( mandatory ) Requester, SupplierID, CurrencyCode;

  association _Items { create ( features : instance, authorization : update ); with draft; }

  action ( features : instance ) approveOrder result [1] $self;
  action ( features : instance ) rejectOrder  result [1] $self;

  determination setDefaults on modify { create; }   // draft 생성 즉시 기본값

  validation validateHeader on save { create; field SupplierID, OrderDate, DeliveryDate, CurrencyCode; }

  draft action Edit;                               // active → draft 복사 (+ active 잠금)
  draft action Activate optimized;                 // draft → active (핸들러 호출로 변환)
  draft action Discard;                            // draft 버리기
  draft action Resume;                             // 잠금이 풀린 draft를 다시 잠그고 계속
  draft determine action Prepare                   // Activate 전에 실행할 검증 묶음
  {
    validation validateHeader;
    validation Item~validateItem;
  }

  mapping for zleg_ordh_### control zleg_s_ordh_x_###
  {
    OrderID            = order_id;
    Requester          = requester;
    SupplierID         = supplier_id;
    OrderDate          = order_date;
    DeliveryDate       = delivery_date;
    TotalAmount        = total_amount;
    CurrencyCode       = currency_code;
    Status             = status;
    Note               = note;
    CreatedBy          = created_by;
    CreatedAt          = created_at;
    LastChangedBy      = last_changed_by;
    LocalLastChangedAt = local_last_changed_at;
    LastChangedAt      = last_changed_at;
  }
}

define behavior for ZRAP_R_ORDITEM_UD_### alias Item
draft table zrap_dordi_###
early numbering
lock dependent by _Order
authorization dependent by _Order
etag dependent by _Order
{
  update ( features : instance );
  delete ( features : instance );

  field ( readonly ) OrderID, ItemNo, ItemAmount, CurrencyCode;
  field ( mandatory ) ProductID, Quantity, QuantityUnit;

  association _Order { with draft; }

  determination calculateAmounts on modify { create; field Quantity, UnitPrice; }

  validation validateItem on save { create; field ProductID, Quantity, QuantityUnit, UnitPrice; }

  mapping for zleg_ordi_### control zleg_s_ordi_x_###
  {
    OrderID      = order_id;
    ItemNo       = item_no;
    ProductID    = product_id;
    ItemText     = item_text;
    Quantity     = quantity;
    QuantityUnit = quantity_unit;
    UnitPrice    = unit_price;
    ItemAmount   = item_amount;
    CurrencyCode = currency_code;
  }
}
```

```bdef
projection;
strict ( 2 );
use draft;                                        // 프로젝션에서도 draft 사용

define behavior for ZRAP_C_ORDER_UD_### alias Order
use etag
{
  use create;
  use update;
  use delete;

  use action approveOrder;
  use action rejectOrder;

  use action Edit;
  use action Activate;
  use action Discard;
  use action Resume;
  use action Prepare;

  use association _Items { create; with draft; }
}

define behavior for ZRAP_C_ORDITEM_UD_### alias Item
use etag
{
  use update;
  use delete;

  use association _Order { with draft; }
}
```

왜 이렇게 쓰나

- **late → early numbering으로 바꾼 이유**: draft는 여러 요청(여러 ABAP 세션)에 걸쳐 살아 있으므로, 화면에서 draft를 만들자마자 **키가 있어야** 다음 요청에서 그 draft를 찾을 수 있습니다. 치트시트 BDL 문서는 "unmanaged에서 `early numbering`은 draft가 켜진 경우에만 쓸 수 있고, `FOR NUMBERING` 핸들러 메서드로 구현한다"고 설명합니다. (draft + late numbering 조합도 가능하지만 draft 테이블에 `DRAFTUUID` 키가 필요해집니다.)
- **`total etag`**: Edit로 draft를 만들면 active가 잠기고, 잠금이 (설정된 시간 뒤) 풀린 뒤 다시 draft를 고치면 `Resume`이 돕니다. 이때 draft가 만들어질 때의 total ETag와 지금 active의 total ETag가 같아야만 이어서 작업할 수 있습니다(치트시트 BDL 문서). 레거시 `_set_admin`이 모든 변경에서 `last_changed_at`을 바꾸므로 그 역할을 합니다. `etag master`와 다른 필드를 쓰라는 권장도 지켰습니다.
- **`with draft`가 붙은 연관**: draft 인스턴스끼리의 부모-자식 연결도 draft 쪽에서 따라가야 하므로 `association _Items { create; with draft; }`처럼 씁니다. 빠뜨리면 활성화 오류가 납니다.
- **determination/validation을 다시 쓸 수 있는 이유**: R-06(non-draft unmanaged)에서는 검증을 세이버(`check_before_save`)에 직접 썼습니다. draft BO에서는 draft 인스턴스의 변경을 프레임워크가 관리하므로 managed와 같은 방식으로 determination/validation을 정의하고 `Prepare`에 묶을 수 있습니다. non-draft unmanaged BO에서 determination/validation을 정의할 수 있는지는 실제 시스템에서 확인 필요합니다(이 문제집은 확인된 경로인 세이버 방식을 썼습니다).
- `Activate optimized`: 치트시트 BDL 문서는 "determination/validation 실행 횟수를 줄이므로 `optimized`를 권장"한다고 설명합니다.
- `copyOrder`는 뺐습니다. draft BO의 팩토리 액션은 "draft로 만들지, active로 만들지"를 결정해야 해서 범위가 커집니다(R-10/R-11 참조).

자주 나는 오류와 해결

- "Draft table ZRAP_DORDH_### does not match" 류: draft 테이블 필드 이름이 CDS 별칭과 다르거나 필드가 빠졌습니다. 퀵픽스 "Create draft table"로 다시 만들면 가장 빠릅니다.
- "total etag is mandatory for draft": draft BO의 루트에는 `total etag`가 필수입니다.
- "Early numbering requires ... FOR NUMBERING": 5단계 numbering 메서드를 아직 만들지 않았기 때문입니다.

</details>

#### 5단계. draft 행동 풀 만들기: 정의 부분과 early numbering 핸들러

요구사항

1. BDEF 퀵픽스로 `ZBP_RAP_R_ORDER_UD_###`를 만들고, Local Types를 아래 구조로 정의하세요.
   - `lcl_legacy`(R-06과 같되 테스트 대역 없이), `lcl_msg`(R-06의 `to_order`/`to_item` + 메시지 번호로 RAP 메시지를 만드는 `new`)
   - `lhc_order`: 권한 2개, features, **`earlynumbering_create`**, **`earlynumbering_cba_Items`**, create/update/delete/read/lock/rba/cba, 액션 2개, determination `setDefaults`, validation `validateHeader`, 공통 `change_status`
   - `lhc_item`: features, update/delete/read/rba_Order, determination `calculateAmounts`, validation `validateItem`
   - `lsc_zrap_r_order_ud_###`: `finalize`, `check_before_save`, `save`, `cleanup`, `cleanup_finalize` (**`adjust_numbers` 없음**)
2. `earlynumbering_create`
   - 이미 `OrderID`가 있는 요청은 그대로 `mapped`에 넣습니다(멱등).
   - 나머지는 개수만큼 레거시 `draw_order_ids`로 최종 번호를 받아 `mapped-order`(`%cid`, `%is_draft`, `OrderID`)에 넣습니다. 하한(`iv_floor`)으로 draft 테이블의 최대 번호를 넘깁니다(MAX+1 방식 대비).
   - 번호를 못 받으면 failed(`cause-unspecific`) + reported(레거시 메시지 040/041).
3. `earlynumbering_cba_Items`
   - `READ ENTITIES ... BY \_Items ... LINK`로 부모별 기존 품목 번호의 최대값을 구합니다(draft 부모는 draft 품목, active 부모는 레거시 품목).
   - 같은 요청 안에서 이미 번호가 있는 품목도 최대값 계산에 넣고, 번호가 없는 품목에 +10씩 매겨 `mapped-item`(`%cid`, `%is_draft`, `OrderID`, `ItemNo`)에 넣습니다.

**확인** 행동 풀과 BDEF가 활성화됩니다(나머지 메서드는 빈 껍데기로 두고 6~8단계에서 채웁니다).

<details><summary>정답·해설</summary>

```abap
*"* Local Types of ZBP_RAP_R_ORDER_UD_###

CLASS lcl_legacy DEFINITION FINAL CREATE PRIVATE.
  PUBLIC SECTION.
    CLASS-METHODS get
      RETURNING VALUE(ro_legacy) TYPE REF TO zif_leg_order_###.
ENDCLASS.

CLASS lcl_legacy IMPLEMENTATION.
  METHOD get.
    ro_legacy = zcl_leg_order_###=>get_instance( ).
  ENDMETHOD.
ENDCLASS.

CLASS lcl_msg DEFINITION FINAL ABSTRACT.
  PUBLIC SECTION.
    TYPES tt_order_failed   TYPE TABLE FOR FAILED   zrap_r_order_ud_###\\order.
    TYPES tt_order_reported TYPE TABLE FOR REPORTED zrap_r_order_ud_###\\order.
    TYPES tt_item_failed    TYPE TABLE FOR FAILED   zrap_r_order_ud_###\\item.
    TYPES tt_item_reported  TYPE TABLE FOR REPORTED zrap_r_order_ud_###\\item.

    "! 레거시 메시지 클래스의 번호로 RAP 메시지를 만든다 (validation용)
    CLASS-METHODS new
      IMPORTING iv_msgno      TYPE symsgno
                iv_v1         TYPE simple OPTIONAL
                iv_v2         TYPE simple OPTIONAL
                iv_v3         TYPE simple OPTIONAL
      RETURNING VALUE(ro_msg) TYPE REF TO if_abap_behv_message.

    CLASS-METHODS to_order
      IMPORTING iv_order_id  TYPE zif_leg_order_###=>t_order_id OPTIONAL
                iv_cid       TYPE abp_behv_cid OPTIONAL
                it_messages  TYPE zif_leg_order_###=>tt_message
      EXPORTING ev_failed    TYPE abap_bool
      CHANGING  ct_failed    TYPE tt_order_failed
                ct_reported  TYPE tt_order_reported.

    CLASS-METHODS to_item
      IMPORTING iv_order_id  TYPE zif_leg_order_###=>t_order_id OPTIONAL
                iv_item_no   TYPE zif_leg_order_###=>t_item_no OPTIONAL
                iv_cid       TYPE abp_behv_cid OPTIONAL
                iv_dependent TYPE abap_bool DEFAULT abap_false
                it_messages  TYPE zif_leg_order_###=>tt_message
      EXPORTING ev_failed    TYPE abap_bool
      CHANGING  ct_failed    TYPE tt_item_failed
                ct_reported  TYPE tt_item_reported.
ENDCLASS.

CLASS lhc_order DEFINITION INHERITING FROM cl_abap_behavior_handler.
  PRIVATE SECTION.
    TYPES tt_order_tky TYPE TABLE FOR READ IMPORT zrap_r_order_ud_###\\order.

    METHODS get_global_authorizations FOR GLOBAL AUTHORIZATION
      IMPORTING REQUEST requested_authorizations FOR Order RESULT result.
    METHODS get_instance_authorizations FOR INSTANCE AUTHORIZATION
      IMPORTING keys REQUEST requested_authorizations FOR Order RESULT result.
    METHODS get_instance_features FOR INSTANCE FEATURES
      IMPORTING keys REQUEST requested_features FOR Order RESULT result.

    "--- early numbering (draft와 active 생성 모두) ----------------------
    METHODS earlynumbering_create FOR NUMBERING
      IMPORTING entities FOR CREATE Order.
    METHODS earlynumbering_cba_Items FOR NUMBERING
      IMPORTING entities FOR CREATE Order\_Items.

    "--- active 인스턴스 (draft는 프레임워크가 처리) ---------------------
    METHODS create FOR MODIFY
      IMPORTING entities FOR CREATE Order.
    METHODS update FOR MODIFY
      IMPORTING entities FOR UPDATE Order.
    METHODS delete FOR MODIFY
      IMPORTING keys FOR DELETE Order.
    METHODS read FOR READ
      IMPORTING keys FOR READ Order RESULT result.
    METHODS lock FOR LOCK
      IMPORTING keys FOR LOCK Order.
    METHODS rba_Items FOR READ
      IMPORTING keys_rba FOR READ Order\_Items FULL result_requested RESULT result LINK association_links.
    METHODS cba_Items FOR MODIFY
      IMPORTING entities_cba FOR CREATE Order\_Items.

    METHODS approveOrder FOR MODIFY
      IMPORTING keys FOR ACTION Order~approveOrder RESULT result.
    METHODS rejectOrder FOR MODIFY
      IMPORTING keys FOR ACTION Order~rejectOrder RESULT result.

    "--- determination / validation ------------------------------------
    METHODS setDefaults FOR DETERMINE ON MODIFY
      IMPORTING keys FOR Order~setDefaults.
    METHODS validateHeader FOR VALIDATE ON SAVE
      IMPORTING keys FOR Order~validateHeader.

    METHODS change_status
      IMPORTING it_keys     TYPE tt_order_tky
                iv_status   TYPE zif_leg_order_###=>t_status
      CHANGING  ct_failed   TYPE lcl_msg=>tt_order_failed
                ct_reported TYPE lcl_msg=>tt_order_reported.
ENDCLASS.

CLASS lhc_item DEFINITION INHERITING FROM cl_abap_behavior_handler.
  PRIVATE SECTION.
    METHODS get_instance_features FOR INSTANCE FEATURES
      IMPORTING keys REQUEST requested_features FOR Item RESULT result.
    METHODS update FOR MODIFY
      IMPORTING entities FOR UPDATE Item.
    METHODS delete FOR MODIFY
      IMPORTING keys FOR DELETE Item.
    METHODS read FOR READ
      IMPORTING keys FOR READ Item RESULT result.
    METHODS rba_Order FOR READ
      IMPORTING keys_rba FOR READ Item\_Order FULL result_requested RESULT result LINK association_links.
    METHODS calculateAmounts FOR DETERMINE ON MODIFY
      IMPORTING keys FOR Item~calculateAmounts.
    METHODS validateItem FOR VALIDATE ON SAVE
      IMPORTING keys FOR Item~validateItem.
ENDCLASS.

CLASS lsc_zrap_r_order_ud_### DEFINITION INHERITING FROM cl_abap_behavior_saver.
  PROTECTED SECTION.
    METHODS finalize          REDEFINITION.
    METHODS check_before_save REDEFINITION.
    METHODS save              REDEFINITION.
    METHODS cleanup           REDEFINITION.
    METHODS cleanup_finalize  REDEFINITION.
ENDCLASS.
```

`lcl_msg` 구현은 R-06 6단계의 `to_order`/`to_item`과 같고(엔터티 타입만 UD), `new`가 추가됩니다.

```abap
CLASS lcl_msg IMPLEMENTATION.

  METHOD new.
    ro_msg = zcm_leg_order_###=>from_legacy( VALUE #(
               msgty = 'E'
               msgid = zif_leg_order_###=>message_class
               msgno = iv_msgno
               msgv1 = |{ iv_v1 }|
               msgv2 = |{ iv_v2 }|
               msgv3 = |{ iv_v3 }| ) ).
  ENDMETHOD.

  METHOD to_order.
    DATA ls_reported LIKE LINE OF ct_reported.

    ev_failed = abap_false.
    LOOP AT it_messages INTO DATA(ls_message).
      IF zcl_rap_order_aux_###=>is_error( ls_message ) = abap_true AND ev_failed = abap_false.
        APPEND VALUE #( %cid        = iv_cid
                        OrderID     = iv_order_id
                        %fail-cause = zcl_rap_order_aux_###=>get_fail_cause( ls_message ) ) TO ct_failed.
        ev_failed = abap_true.
      ENDIF.

      CLEAR ls_reported.
      ls_reported-%cid    = iv_cid.
      ls_reported-OrderID = iv_order_id.
      ls_reported-%msg    = zcm_leg_order_###=>from_legacy( ls_message ).
      IF ls_message-fieldname IS NOT INITIAL.
        DATA(lv_element) = zcl_rap_order_aux_###=>get_element_name( ls_message-fieldname ).
        ASSIGN COMPONENT lv_element OF STRUCTURE ls_reported-%element TO FIELD-SYMBOL(<lv_flag>).
        IF sy-subrc = 0.
          <lv_flag> = if_abap_behv=>mk-on.
        ENDIF.
      ENDIF.
      APPEND ls_reported TO ct_reported.
    ENDLOOP.
  ENDMETHOD.

  METHOD to_item.
    DATA ls_reported LIKE LINE OF ct_reported.

    ev_failed = abap_false.
    LOOP AT it_messages INTO DATA(ls_message).
      IF zcl_rap_order_aux_###=>is_error( ls_message ) = abap_true AND ev_failed = abap_false.
        APPEND VALUE #( %cid        = iv_cid
                        OrderID     = iv_order_id
                        ItemNo      = iv_item_no
                        %fail-cause = zcl_rap_order_aux_###=>get_fail_cause(
                                        is_message   = ls_message
                                        iv_dependent = iv_dependent ) ) TO ct_failed.
        ev_failed = abap_true.
      ENDIF.

      CLEAR ls_reported.
      ls_reported-%cid    = iv_cid.
      ls_reported-OrderID = iv_order_id.
      ls_reported-ItemNo  = iv_item_no.
      ls_reported-%msg    = zcm_leg_order_###=>from_legacy( ls_message ).
      IF ls_message-fieldname IS NOT INITIAL.
        DATA(lv_element) = zcl_rap_order_aux_###=>get_element_name( ls_message-fieldname ).
        ASSIGN COMPONENT lv_element OF STRUCTURE ls_reported-%element TO FIELD-SYMBOL(<lv_flag>).
        IF sy-subrc = 0.
          <lv_flag> = if_abap_behv=>mk-on.
        ENDIF.
      ENDIF.
      APPEND ls_reported TO ct_reported.
    ENDLOOP.
  ENDMETHOD.

ENDCLASS.
```

`lhc_order` 구현의 numbering 부분입니다(6~7단계 메서드는 같은 IMPLEMENTATION에 이어 붙입니다).

```abap
CLASS lhc_order IMPLEMENTATION.

  "------------------------------------------------------------------
  " 주문 번호: draft를 만드는 순간 최종 번호를 준다
  "------------------------------------------------------------------
  METHOD earlynumbering_create.
    DATA lv_floor TYPE zif_leg_order_###=>t_order_id.

    " 이미 키가 있는 요청은 그대로 통과 (draft BO에서는 반드시 멱등이어야 함)
    LOOP AT entities INTO DATA(ls_entity) WHERE OrderID IS NOT INITIAL.
      APPEND VALUE #( %cid      = ls_entity-%cid
                      %is_draft = ls_entity-%is_draft
                      OrderID   = ls_entity-OrderID ) TO mapped-order.
    ENDLOOP.

    DATA(lt_new) = entities.
    DELETE lt_new WHERE OrderID IS NOT INITIAL.
    IF lt_new IS INITIAL.
      RETURN.
    ENDIF.

    " MAX+1 방식(R-05의 대체 경로)일 때만 의미가 있는 하한:
    " 아직 활성화되지 않은 draft들이 이미 받은 번호보다 커야 한다.
    " (draft 테이블 직접 읽기는 권장되지 않지만, 읽기만 하고 번호 범위 방식에서는 쓰이지 않는다)
    SELECT MAX( orderid ) FROM zrap_dordh_### INTO @lv_floor.

    lcl_legacy=>get( )->draw_order_ids(
      EXPORTING iv_quantity = lines( lt_new )
                iv_floor    = lv_floor
      IMPORTING et_ids      = DATA(lt_ids)
                et_messages = DATA(lt_messages) ).

    IF lines( lt_ids ) < lines( lt_new ).
      LOOP AT lt_new INTO ls_entity.
        APPEND VALUE #( %cid        = ls_entity-%cid
                        %is_draft   = ls_entity-%is_draft
                        %fail-cause = if_abap_behv=>cause-unspecific ) TO failed-order.
        APPEND VALUE #( %cid      = ls_entity-%cid
                        %is_draft = ls_entity-%is_draft
                        %msg      = COND #( WHEN lt_messages IS NOT INITIAL
                                            THEN zcm_leg_order_###=>from_legacy( lt_messages[ 1 ] )
                                            ELSE lcl_msg=>new( '041' ) ) ) TO reported-order.
      ENDLOOP.
      RETURN.
    ENDIF.

    LOOP AT lt_new INTO ls_entity.
      DATA(lv_index) = sy-tabix.
      APPEND VALUE #( %cid      = ls_entity-%cid
                      %is_draft = ls_entity-%is_draft
                      OrderID   = lt_ids[ lv_index ] ) TO mapped-order.
    ENDLOOP.
  ENDMETHOD.

  "------------------------------------------------------------------
  " 품목 번호: 부모별 최대값 + 10
  "------------------------------------------------------------------
  METHOD earlynumbering_cba_Items.
    DATA lv_max TYPE zif_leg_order_###=>t_item_no.

    " 부모별 기존 품목: draft 부모 → draft 품목(프레임워크), active 부모 → rba_Items 핸들러(레거시)
    READ ENTITIES OF zrap_r_order_ud_### IN LOCAL MODE
      ENTITY Order BY \_Items
        FROM CORRESPONDING #( entities )
      LINK DATA(lt_links).

    LOOP AT entities ASSIGNING FIELD-SYMBOL(<parent>) GROUP BY <parent>-%tky.

      lv_max = REDUCE #( INIT m = CONV zif_leg_order_###=>t_item_no( 0 )
                         FOR ls_link IN lt_links
                         WHERE ( source-OrderID   = <parent>-OrderID
                             AND source-%is_draft = <parent>-%is_draft )
                         NEXT m = COND #( WHEN ls_link-target-ItemNo > m
                                          THEN ls_link-target-ItemNo ELSE m ) ).

      " 같은 요청 안에서 이미 번호를 가진 품목(예: Activate가 넘기는 draft 품목)도 고려
      LOOP AT GROUP <parent> ASSIGNING FIELD-SYMBOL(<member>).
        LOOP AT <member>-%target ASSIGNING FIELD-SYMBOL(<preset>) WHERE ItemNo IS NOT INITIAL.
          IF <preset>-ItemNo > lv_max.
            lv_max = <preset>-ItemNo.
          ENDIF.
        ENDLOOP.
      ENDLOOP.

      LOOP AT GROUP <parent> ASSIGNING <member>.
        LOOP AT <member>-%target ASSIGNING FIELD-SYMBOL(<item>).
          APPEND CORRESPONDING #( <item> ) TO mapped-item ASSIGNING FIELD-SYMBOL(<mapped>).
          <mapped>-%is_draft = <member>-%is_draft.
          <mapped>-OrderID   = <member>-OrderID.
          IF <item>-ItemNo IS INITIAL.
            lv_max = lv_max + 10.
            <mapped>-ItemNo = lv_max.
          ENDIF.
        ENDLOOP.
      ENDLOOP.

    ENDLOOP.
  ENDMETHOD.
```

왜 이렇게 쓰나

- **`FOR NUMBERING` 메서드는 draft 생성과 active 생성 모두에서** 불립니다. Fiori에서 Create를 누르면 `%is_draft = 01`인 생성 요청이 오고, 여기서 준 번호가 draft 테이블의 키가 됩니다. 공식 `/DMO/BP_TRAVEL_M`의 `earlynumbering_create` 주석("Ensure Travel ID is not set yet (idempotent) - must be checked when BO is draft-enabled")처럼 **이미 키가 있으면 다시 매기지 않는** 처리가 반드시 필요합니다.
- `mapped`에 `%is_draft`를 꼭 넣으세요. draft BO에서 인스턴스를 식별하는 `%tky`는 `%is_draft + 키`입니다.
- 번호 범위 방식에서는 draft를 버리면(Discard) 번호에 빈칸이 생깁니다. 번호 범위는 원래 빈칸을 허용하는 설계라 문제가 아닙니다. 반면 MAX+1 방식은 "다른 사람의 아직 활성화되지 않은 draft"가 쓰는 번호를 알 수 없어 충돌하므로, draft 테이블의 최대값을 하한으로 넘겨 위험을 줄였습니다. 그래도 동시 생성 경쟁은 남으므로 **draft BO에서는 번호 범위 방식을 쓰는 것이 원칙**입니다.
- `earlynumbering_cba_Items`의 최대값 계산은 공식 `earlynumbering_cba_booking`과 같은 2단계 구조(기존 자식 + 같은 요청의 번호 있는 자식)입니다. `READ ... BY \_Items ... LINK`만 요청했으므로 데이터는 읽지 않고 키만 받습니다.

</details>

#### 6단계. active 인스턴스 핸들러 구현

요구사항

1. 주문 `create`: draft가 활성화될 때(또는 active를 EML로 직접 만들 때) 불립니다. 키(`OrderID`)는 이미 numbering에서 정해졌으므로 레거시 `create_order`를 **external 모드**로 부릅니다. `mapped`는 numbering에서 이미 채웠으므로 다시 넣지 않습니다.
2. 주문 `update`/`delete`/`read`/`lock`/`rba_Items`: R-06과 같은 방식(엔터티 타입만 UD).
3. 주문 `cba_Items`: 품목 번호도 numbering에서 정해졌으므로 `it_items`와 `it_itemsx`의 `item_no`에 그 번호를 넣어 넘깁니다.
4. 품목 `update`/`delete`/`read`/`rba_Order`: R-06과 같은 방식.
5. create/update/delete/cba 맨 앞에 **"여기에는 active만 온다"** 는 가정을 `ASSERT`로 적으세요. 가정이 틀리면 덤프로 바로 드러나게 하기 위해서입니다.

**확인** 활성화됩니다.

<details><summary>정답·해설</summary>

```abap
  "------------------------------------------------------------------
  " ACTIVE CREATE: draft 활성화 시. 키는 이미 있다 → external 모드
  "------------------------------------------------------------------
  METHOD create.
    DATA ls_order_db TYPE zleg_ordh_###.

    LOOP AT entities ASSIGNING FIELD-SYMBOL(<entity>).
      " 가정: draft 인스턴스는 프레임워크가 draft 테이블로 처리하므로 여기 오지 않는다
      ASSERT <entity>-%is_draft = if_abap_behv=>mk-off.

      ls_order_db = CORRESPONDING #( <entity> MAPPING FROM ENTITY USING CONTROL ).
      ls_order_db-order_id = <entity>-OrderID.          " numbering에서 정한 최종 번호

      lcl_legacy=>get( )->create_order(
        EXPORTING is_order          = CORRESPONDING #( ls_order_db )
                  iv_numbering_mode = zif_leg_order_###=>numbering_mode-external
        IMPORTING et_messages       = DATA(lt_messages) ).

      lcl_msg=>to_order( EXPORTING iv_cid      = <entity>-%cid
                                   iv_order_id = <entity>-OrderID
                                   it_messages = lt_messages
                         CHANGING  ct_failed   = failed-order
                                   ct_reported = reported-order ).
      " mapped는 earlynumbering_create에서 이미 채웠다
    ENDLOOP.
  ENDMETHOD.

  METHOD update.
    DATA ls_order_db TYPE zleg_ordh_###.
    DATA ls_orderx   TYPE zif_leg_order_###=>ts_order_inx.

    LOOP AT entities ASSIGNING FIELD-SYMBOL(<entity>).
      ASSERT <entity>-%is_draft = if_abap_behv=>mk-off.

      ls_order_db = CORRESPONDING #( <entity> MAPPING FROM ENTITY ).
      CLEAR ls_orderx.
      ls_orderx-order_id = <entity>-OrderID.
      ls_orderx-_intx    = CORRESPONDING #( <entity> MAPPING FROM ENTITY ).

      lcl_legacy=>get( )->update_order(
        EXPORTING is_order    = CORRESPONDING #( ls_order_db )
                  is_orderx   = ls_orderx
        IMPORTING et_messages = DATA(lt_messages) ).

      lcl_msg=>to_order( EXPORTING iv_cid      = <entity>-%cid_ref
                                   iv_order_id = <entity>-OrderID
                                   it_messages = lt_messages
                         CHANGING  ct_failed   = failed-order
                                   ct_reported = reported-order ).
    ENDLOOP.
  ENDMETHOD.

  METHOD delete.
    LOOP AT keys ASSIGNING FIELD-SYMBOL(<key>).
      ASSERT <key>-%is_draft = if_abap_behv=>mk-off.

      lcl_legacy=>get( )->delete_order(
        EXPORTING iv_order_id = <key>-OrderID
        IMPORTING et_messages = DATA(lt_messages) ).

      lcl_msg=>to_order( EXPORTING iv_cid      = <key>-%cid_ref
                                   iv_order_id = <key>-OrderID
                                   it_messages = lt_messages
                         CHANGING  ct_failed   = failed-order
                                   ct_reported = reported-order ).
    ENDLOOP.
  ENDMETHOD.

  METHOD read.
    DATA ls_result LIKE LINE OF result.

    lcl_legacy=>get( )->read_orders(
      EXPORTING it_order_ids  = VALUE #( FOR ls_key IN keys ( ls_key-OrderID ) )
                iv_with_items = abap_false
      IMPORTING et_orders     = DATA(lt_orders) ).

    LOOP AT keys ASSIGNING FIELD-SYMBOL(<key>) GROUP BY <key>-%tky.
      READ TABLE lt_orders INTO DATA(ls_order) WITH KEY order_id = <key>-OrderID.
      IF sy-subrc = 0.
        ls_result = CORRESPONDING #( ls_order MAPPING TO ENTITY ).   " %is_draft = 00 (active)
        ls_result-StatusCriticality = zcl_rap_order_aux_###=>get_status_criticality( ls_order-status ).
        INSERT ls_result INTO TABLE result.
      ELSE.
        APPEND VALUE #( %tky        = <key>-%tky
                        %fail-cause = if_abap_behv=>cause-not_found ) TO failed-order.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

  METHOD lock.
    LOOP AT keys ASSIGNING FIELD-SYMBOL(<key>).
      lcl_legacy=>get( )->lock_order(
        EXPORTING iv_order_id = <key>-OrderID
        IMPORTING et_messages = DATA(lt_messages) ).

      lcl_msg=>to_order( EXPORTING iv_order_id = <key>-OrderID
                                   it_messages = lt_messages
                         CHANGING  ct_failed   = failed-order
                                   ct_reported = reported-order ).
    ENDLOOP.
  ENDMETHOD.

  METHOD rba_Items.
    DATA ls_item_result LIKE LINE OF result.

    lcl_legacy=>get( )->read_orders(
      EXPORTING it_order_ids  = VALUE #( FOR ls_key IN keys_rba ( ls_key-OrderID ) )
                iv_with_items = abap_true
      IMPORTING et_orders     = DATA(lt_orders)
                et_items      = DATA(lt_items) ).

    LOOP AT keys_rba ASSIGNING FIELD-SYMBOL(<key>) GROUP BY <key>-%tky.
      IF NOT line_exists( lt_orders[ order_id = <key>-OrderID ] ).
        APPEND VALUE #( %tky          = <key>-%tky
                        %assoc-_Items = if_abap_behv=>mk-on
                        %fail-cause   = if_abap_behv=>cause-not_found ) TO failed-order.
        CONTINUE.
      ENDIF.

      LOOP AT lt_items INTO DATA(ls_item) WHERE order_id = <key>-OrderID.
        INSERT VALUE #( source-%tky = <key>-%tky
                        target-%tky = VALUE #( OrderID = ls_item-order_id
                                               ItemNo  = ls_item-item_no ) ) INTO TABLE association_links.
        IF result_requested = abap_true.
          ls_item_result = CORRESPONDING #( ls_item MAPPING TO ENTITY ).
          INSERT ls_item_result INTO TABLE result.
        ENDIF.
      ENDLOOP.
    ENDLOOP.

    SORT association_links BY target ASCENDING.
    DELETE ADJACENT DUPLICATES FROM association_links COMPARING ALL FIELDS.
    SORT result BY %tky ASCENDING.
    DELETE ADJACENT DUPLICATES FROM result COMPARING ALL FIELDS.
  ENDMETHOD.

  METHOD cba_Items.
    DATA ls_item_db TYPE zleg_ordi_###.

    lcl_legacy=>get( )->read_orders(
      EXPORTING it_order_ids  = VALUE #( FOR ls_e IN entities_cba ( ls_e-OrderID ) )
                iv_with_items = abap_false
      IMPORTING et_orders     = DATA(lt_parents) ).

    LOOP AT entities_cba ASSIGNING FIELD-SYMBOL(<parent>).
      ASSERT <parent>-%is_draft = if_abap_behv=>mk-off.

      IF NOT line_exists( lt_parents[ order_id = <parent>-OrderID ] ).
        APPEND VALUE #( %cid          = <parent>-%cid_ref
                        %tky          = <parent>-%tky
                        %assoc-_Items = if_abap_behv=>mk-on
                        %fail-cause   = if_abap_behv=>cause-not_found ) TO failed-order.
        LOOP AT <parent>-%target ASSIGNING FIELD-SYMBOL(<orphan>).
          APPEND VALUE #( %cid        = <orphan>-%cid
                          %fail-cause = if_abap_behv=>cause-dependency ) TO failed-item.
        ENDLOOP.
        CONTINUE.
      ENDIF.

      LOOP AT <parent>-%target ASSIGNING FIELD-SYMBOL(<item>).
        ls_item_db = CORRESPONDING #( <item> MAPPING FROM ENTITY USING CONTROL ).
        ls_item_db-item_no = <item>-ItemNo.               " numbering에서 정한 번호

        lcl_legacy=>get( )->update_order(
          EXPORTING is_order    = VALUE #( order_id = <parent>-OrderID )
                    is_orderx   = VALUE #( order_id = <parent>-OrderID )
                    it_items    = VALUE #( ( CORRESPONDING #( ls_item_db ) ) )
                    it_itemsx   = VALUE #( ( item_no     = <item>-ItemNo
                                             action_code = zif_leg_order_###=>action_code-create ) )
          IMPORTING et_messages = DATA(lt_messages) ).

        lcl_msg=>to_item( EXPORTING iv_cid      = <item>-%cid
                                    iv_order_id = <parent>-OrderID
                                    iv_item_no  = <item>-ItemNo
                                    it_messages = lt_messages
                          CHANGING  ct_failed   = failed-item
                                    ct_reported = reported-item ).
      ENDLOOP.
    ENDLOOP.
  ENDMETHOD.
```

품목 핸들러의 active 부분입니다(7단계 메서드는 같은 IMPLEMENTATION에 이어 붙입니다).

```abap
CLASS lhc_item IMPLEMENTATION.

  METHOD update.
    DATA ls_item_db TYPE zleg_ordi_###.
    DATA ls_itemx   TYPE zif_leg_order_###=>ts_item_inx.

    LOOP AT entities ASSIGNING FIELD-SYMBOL(<entity>).
      ASSERT <entity>-%is_draft = if_abap_behv=>mk-off.

      ls_item_db = CORRESPONDING #( <entity> MAPPING FROM ENTITY ).
      CLEAR ls_itemx.
      ls_itemx-item_no     = <entity>-ItemNo.
      ls_itemx-action_code = zif_leg_order_###=>action_code-update.
      ls_itemx-_intx       = CORRESPONDING #( <entity> MAPPING FROM ENTITY ).

      lcl_legacy=>get( )->update_order(
        EXPORTING is_order    = VALUE #( order_id = <entity>-OrderID )
                  is_orderx   = VALUE #( order_id = <entity>-OrderID )
                  it_items    = VALUE #( ( CORRESPONDING #( ls_item_db ) ) )
                  it_itemsx   = VALUE #( ( ls_itemx ) )
        IMPORTING et_messages = DATA(lt_messages) ).

      lcl_msg=>to_item( EXPORTING iv_cid      = <entity>-%cid_ref
                                  iv_order_id = <entity>-OrderID
                                  iv_item_no  = <entity>-ItemNo
                                  it_messages = lt_messages
                        CHANGING  ct_failed   = failed-item
                                  ct_reported = reported-item ).
    ENDLOOP.
  ENDMETHOD.

  METHOD delete.
    LOOP AT keys ASSIGNING FIELD-SYMBOL(<key>).
      ASSERT <key>-%is_draft = if_abap_behv=>mk-off.

      lcl_legacy=>get( )->update_order(
        EXPORTING is_order    = VALUE #( order_id = <key>-OrderID )
                  is_orderx   = VALUE #( order_id = <key>-OrderID )
                  it_items    = VALUE #( ( item_no = <key>-ItemNo ) )
                  it_itemsx   = VALUE #( ( item_no     = <key>-ItemNo
                                           action_code = zif_leg_order_###=>action_code-delete ) )
        IMPORTING et_messages = DATA(lt_messages) ).

      lcl_msg=>to_item( EXPORTING iv_cid      = <key>-%cid_ref
                                  iv_order_id = <key>-OrderID
                                  iv_item_no  = <key>-ItemNo
                                  it_messages = lt_messages
                        CHANGING  ct_failed   = failed-item
                                  ct_reported = reported-item ).
    ENDLOOP.
  ENDMETHOD.

  METHOD read.
    DATA ls_result LIKE LINE OF result.

    lcl_legacy=>get( )->read_orders(
      EXPORTING it_order_ids  = VALUE #( FOR ls_key IN keys ( ls_key-OrderID ) )
                iv_with_items = abap_true
      IMPORTING et_items      = DATA(lt_items) ).

    LOOP AT keys ASSIGNING FIELD-SYMBOL(<key>) GROUP BY <key>-%tky.
      READ TABLE lt_items INTO DATA(ls_item) WITH KEY order_id = <key>-OrderID
                                                      item_no  = <key>-ItemNo.
      IF sy-subrc = 0.
        ls_result = CORRESPONDING #( ls_item MAPPING TO ENTITY ).
        INSERT ls_result INTO TABLE result.
      ELSE.
        APPEND VALUE #( %tky        = <key>-%tky
                        %fail-cause = if_abap_behv=>cause-not_found ) TO failed-item.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

  METHOD rba_Order.
    DATA ls_order_result LIKE LINE OF result.

    lcl_legacy=>get( )->read_orders(
      EXPORTING it_order_ids  = VALUE #( FOR ls_key IN keys_rba ( ls_key-OrderID ) )
                iv_with_items = abap_false
      IMPORTING et_orders     = DATA(lt_orders) ).

    LOOP AT keys_rba ASSIGNING FIELD-SYMBOL(<key>) GROUP BY <key>-%tky.
      READ TABLE lt_orders INTO DATA(ls_order) WITH KEY order_id = <key>-OrderID.
      IF sy-subrc <> 0.
        APPEND VALUE #( %tky          = <key>-%tky
                        %assoc-_Order = if_abap_behv=>mk-on
                        %fail-cause   = if_abap_behv=>cause-not_found ) TO failed-item.
        CONTINUE.
      ENDIF.

      INSERT VALUE #( source-%tky    = <key>-%tky
                      target-OrderID = ls_order-order_id ) INTO TABLE association_links.

      IF result_requested = abap_true.
        ls_order_result = CORRESPONDING #( ls_order MAPPING TO ENTITY ).
        ls_order_result-StatusCriticality = zcl_rap_order_aux_###=>get_status_criticality( ls_order-status ).
        INSERT ls_order_result INTO TABLE result.
      ENDIF.
    ENDLOOP.

    SORT association_links BY source ASCENDING.
    DELETE ADJACENT DUPLICATES FROM association_links COMPARING ALL FIELDS.
    SORT result BY %tky ASCENDING.
    DELETE ADJACENT DUPLICATES FROM result COMPARING ALL FIELDS.
  ENDMETHOD.
```

왜 이렇게 쓰나

- **R-06과 달라진 곳은 세 군데뿐**입니다. (1) create가 late 대신 **external** 모드(키가 이미 정해짐), (2) create/cba가 `mapped`를 채우지 않음(numbering 메서드가 이미 채움), (3) `ASSERT %is_draft = mk-off`. 이것이 "unmanaged에 draft를 붙여도 레거시 감싸기 코드는 거의 그대로"라는 뜻입니다. draft 인스턴스의 저장소·버퍼·잠금 연장은 프레임워크가 맡습니다.
- 레거시 external 모드는 번호가 이미 있으면 메시지 005(`cause-conflict`)를 냅니다. 번호 범위에서 받은 번호라 정상적으로는 일어나지 않지만, 두 BO(R-06, R-07)가 같은 테이블을 쓰면서 MAX+1 방식을 쓰면 일어날 수 있습니다.
- `ASSERT`로 가정을 적어 두는 이유: draft 지원 unmanaged BO에서 "핸들러에는 active만 온다"는 것은 이 문제의 설계 전제입니다(실제 시스템에서 확인 필요). 전제가 틀렸다면 조용히 잘못 저장되는 것보다 **즉시 덤프로 드러나는 편**이 안전합니다. 8단계의 브레이크포인트 실험으로 직접 확인하세요.

</details>

#### 7단계. determination · validation · 액션 · 기능 제어 · 권한

요구사항

1. `setDefaults`(주문, on modify create): 주문일이 비었으면 오늘, 상태는 `N`. `MODIFY ENTITIES ... IN LOCAL MODE`로 씁니다.
2. `calculateAmounts`(품목, on modify create/Quantity/UnitPrice)
   - 해당 품목의 `ItemAmount` = 수량 × 단가, `CurrencyCode` = 부모 통화.
   - 부모 주문의 `TotalAmount` = 그 주문 모든 품목 `ItemAmount`의 합.
3. `validateHeader`(on save): 공급업체 존재(010, `/DMO/AGENCY`를 SELECT 한 번), 납기일 ≥ 주문일(011), 통화 필수(012). 먼저 `%state_area = 'VALIDATE_HEADER'`로 이전 메시지를 지우고, 오류마다 failed + reported(`%element`).
4. `validateItem`(on save): 수량 > 0(020), 단위 필수(021), 단가 > 0(022), 제품 존재(023, `/DMO/SUPPLEMENT`를 SELECT 한 번). `%state_area = 'VALIDATE_ITEM'`, 부모를 가리키는 `%path`.
5. 액션 `approveOrder`/`rejectOrder`: draft 인스턴스에 대해 오면 failed(`cause-disabled`), active면 R-06과 같은 처리.
6. 주문 features: R-06 규칙 + **draft 인스턴스에서는 승인/반려 비활성**. 품목 features: 부모 상태 N일 때만 update/delete.
7. 권한: 전역·인스턴스 모두 허용(인스턴스 결과에 `%action-Edit` 포함).

**확인** 행동 풀 전체가 활성화됩니다(세이버는 8단계).

<details><summary>정답·해설</summary>

```abap
  "------------------------------------------------------------------
  " DETERMINATION: draft 생성 즉시 기본값
  "------------------------------------------------------------------
  METHOD setDefaults.
    READ ENTITIES OF zrap_r_order_ud_### IN LOCAL MODE
      ENTITY Order
        FIELDS ( OrderDate Status ) WITH CORRESPONDING #( keys )
      RESULT DATA(lt_orders).

    DELETE lt_orders WHERE OrderDate IS NOT INITIAL AND Status IS NOT INITIAL.
    IF lt_orders IS INITIAL.
      RETURN.
    ENDIF.

    DATA(lv_today) = cl_abap_context_info=>get_system_date( ).

    MODIFY ENTITIES OF zrap_r_order_ud_### IN LOCAL MODE
      ENTITY Order
        UPDATE FIELDS ( OrderDate Status )             " Status는 readonly지만 LOCAL MODE에서는 쓸 수 있다
        WITH VALUE #( FOR ls_order IN lt_orders
                      ( %tky      = ls_order-%tky
                        OrderDate = COND #( WHEN ls_order-OrderDate IS INITIAL
                                            THEN lv_today ELSE ls_order-OrderDate )
                        Status    = zif_leg_order_###=>status-new ) )
      REPORTED DATA(ls_update_reported).

    reported = CORRESPONDING #( DEEP ls_update_reported ).
  ENDMETHOD.

  "------------------------------------------------------------------
  " VALIDATION: 헤더
  "------------------------------------------------------------------
  METHOD validateHeader.
    DATA lt_suppliers TYPE SORTED TABLE OF /dmo/agency_id WITH UNIQUE KEY table_line.

    READ ENTITIES OF zrap_r_order_ud_### IN LOCAL MODE
      ENTITY Order
        FIELDS ( SupplierID OrderDate DeliveryDate CurrencyCode ) WITH CORRESPONDING #( keys )
      RESULT DATA(lt_orders).

    LOOP AT lt_orders INTO DATA(ls_order) WHERE SupplierID IS NOT INITIAL.
      INSERT ls_order-SupplierID INTO TABLE lt_suppliers.
    ENDLOOP.
    IF lt_suppliers IS NOT INITIAL.
      SELECT FROM /dmo/agency FIELDS agency_id
        FOR ALL ENTRIES IN @lt_suppliers
        WHERE agency_id = @lt_suppliers-table_line
        INTO TABLE @DATA(lt_known).
    ENDIF.

    LOOP AT lt_orders INTO ls_order.
      " 이 검증이 예전에 남긴 메시지를 먼저 지운다
      APPEND VALUE #( %tky = ls_order-%tky %state_area = 'VALIDATE_HEADER' ) TO reported-order.

      IF ls_order-SupplierID IS INITIAL
      OR NOT line_exists( lt_known[ agency_id = ls_order-SupplierID ] ).
        APPEND VALUE #( %tky = ls_order-%tky ) TO failed-order.
        APPEND VALUE #( %tky                = ls_order-%tky
                        %state_area         = 'VALIDATE_HEADER'
                        %msg                = lcl_msg=>new( iv_msgno = '010' iv_v1 = ls_order-SupplierID )
                        %element-SupplierID = if_abap_behv=>mk-on ) TO reported-order.
      ENDIF.

      IF ls_order-DeliveryDate IS NOT INITIAL
      AND ls_order-DeliveryDate < ls_order-OrderDate.
        APPEND VALUE #( %tky = ls_order-%tky ) TO failed-order.
        APPEND VALUE #( %tky                  = ls_order-%tky
                        %state_area           = 'VALIDATE_HEADER'
                        %msg                  = lcl_msg=>new( iv_msgno = '011'
                                                              iv_v1    = |{ ls_order-OrderDate DATE = USER }|
                                                              iv_v2    = |{ ls_order-DeliveryDate DATE = USER }| )
                        %element-OrderDate    = if_abap_behv=>mk-on
                        %element-DeliveryDate = if_abap_behv=>mk-on ) TO reported-order.
      ENDIF.

      IF ls_order-CurrencyCode IS INITIAL.
        APPEND VALUE #( %tky = ls_order-%tky ) TO failed-order.
        APPEND VALUE #( %tky                  = ls_order-%tky
                        %state_area           = 'VALIDATE_HEADER'
                        %msg                  = lcl_msg=>new( iv_msgno = '012' iv_v1 = ls_order-OrderID )
                        %element-CurrencyCode = if_abap_behv=>mk-on ) TO reported-order.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

  "------------------------------------------------------------------
  " 액션: active 인스턴스에만
  "------------------------------------------------------------------
  METHOD change_status.
    LOOP AT it_keys ASSIGNING FIELD-SYMBOL(<key>).
      IF <key>-%is_draft = if_abap_behv=>mk-on.
        APPEND VALUE #( %tky = <key>-%tky %fail-cause = if_abap_behv=>cause-disabled ) TO ct_failed.
        CONTINUE.
      ENDIF.

      lcl_legacy=>get( )->set_status(
        EXPORTING iv_order_id = <key>-OrderID
                  iv_status   = iv_status
        IMPORTING et_messages = DATA(lt_messages) ).

      lcl_msg=>to_order( EXPORTING iv_order_id = <key>-OrderID
                                   it_messages = lt_messages
                         CHANGING  ct_failed   = ct_failed
                                   ct_reported = ct_reported ).
    ENDLOOP.
  ENDMETHOD.

  METHOD approveOrder.
    change_status( EXPORTING it_keys     = CORRESPONDING #( keys )
                             iv_status   = zif_leg_order_###=>status-approved
                   CHANGING  ct_failed   = failed-order
                             ct_reported = reported-order ).

    READ ENTITIES OF zrap_r_order_ud_### IN LOCAL MODE
      ENTITY Order ALL FIELDS WITH CORRESPONDING #( keys )
      RESULT DATA(lt_orders).

    LOOP AT lt_orders INTO DATA(ls_order).
      CHECK NOT line_exists( failed-order[ OrderID = ls_order-OrderID ] ).
      APPEND VALUE #( %tky = ls_order-%tky %param = ls_order ) TO result.
    ENDLOOP.
  ENDMETHOD.

  METHOD rejectOrder.
    change_status( EXPORTING it_keys     = CORRESPONDING #( keys )
                             iv_status   = zif_leg_order_###=>status-rejected
                   CHANGING  ct_failed   = failed-order
                             ct_reported = reported-order ).

    READ ENTITIES OF zrap_r_order_ud_### IN LOCAL MODE
      ENTITY Order ALL FIELDS WITH CORRESPONDING #( keys )
      RESULT DATA(lt_orders).

    LOOP AT lt_orders INTO DATA(ls_order).
      CHECK NOT line_exists( failed-order[ OrderID = ls_order-OrderID ] ).
      APPEND VALUE #( %tky = ls_order-%tky %param = ls_order ) TO result.
    ENDLOOP.
  ENDMETHOD.

  "------------------------------------------------------------------
  " 기능 제어 / 권한
  "------------------------------------------------------------------
  METHOD get_instance_features.
    READ ENTITIES OF zrap_r_order_ud_### IN LOCAL MODE
      ENTITY Order
        FIELDS ( Status ) WITH CORRESPONDING #( keys )
      RESULT DATA(lt_orders)
      FAILED failed.

    LOOP AT lt_orders INTO DATA(ls_order).
      DATA(lv_is_new)    = xsdbool( ls_order-Status = zif_leg_order_###=>status-new ).
      DATA(lv_is_active) = xsdbool( ls_order-%is_draft = if_abap_behv=>mk-off ).
      DATA(lv_deletable) = xsdbool( ls_order-Status = zif_leg_order_###=>status-new
                                 OR ls_order-Status = zif_leg_order_###=>status-rejected ).

      APPEND VALUE #(
        %tky                 = ls_order-%tky
        %update              = COND #( WHEN lv_is_new = abap_true
                                       THEN if_abap_behv=>fc-o-enabled ELSE if_abap_behv=>fc-o-disabled )
        %delete              = COND #( WHEN lv_deletable = abap_true
                                       THEN if_abap_behv=>fc-o-enabled ELSE if_abap_behv=>fc-o-disabled )
        %assoc-_Items        = COND #( WHEN lv_is_new = abap_true
                                       THEN if_abap_behv=>fc-o-enabled ELSE if_abap_behv=>fc-o-disabled )
        %action-approveOrder = COND #( WHEN lv_is_new = abap_true AND lv_is_active = abap_true
                                       THEN if_abap_behv=>fc-o-enabled ELSE if_abap_behv=>fc-o-disabled )
        %action-rejectOrder  = COND #( WHEN lv_is_new = abap_true AND lv_is_active = abap_true
                                       THEN if_abap_behv=>fc-o-enabled ELSE if_abap_behv=>fc-o-disabled )
      ) TO result.
    ENDLOOP.
  ENDMETHOD.

  METHOD get_global_authorizations.
    " 실습: 모두 허용 (R-06 8단계 주석 참고)
    IF requested_authorizations-%create = if_abap_behv=>mk-on.
      result-%create = if_abap_behv=>auth-allowed.
    ENDIF.
    IF requested_authorizations-%update = if_abap_behv=>mk-on.
      result-%update = if_abap_behv=>auth-allowed.
    ENDIF.
    IF requested_authorizations-%delete = if_abap_behv=>mk-on.
      result-%delete = if_abap_behv=>auth-allowed.
    ENDIF.
    IF requested_authorizations-%action-Edit = if_abap_behv=>mk-on.
      result-%action-Edit = if_abap_behv=>auth-allowed.
    ENDIF.
    IF requested_authorizations-%action-approveOrder = if_abap_behv=>mk-on.
      result-%action-approveOrder = if_abap_behv=>auth-allowed.
    ENDIF.
    IF requested_authorizations-%action-rejectOrder = if_abap_behv=>mk-on.
      result-%action-rejectOrder = if_abap_behv=>auth-allowed.
    ENDIF.
  ENDMETHOD.

  METHOD get_instance_authorizations.
    " Edit은 update와 같은 권한으로 본다 (공식 /DMO/BP_TRAVEL_D와 같은 규칙)
    result = VALUE #( FOR ls_key IN keys
                      ( %tky                 = ls_key-%tky
                        %update              = if_abap_behv=>auth-allowed
                        %action-Edit         = if_abap_behv=>auth-allowed
                        %delete              = if_abap_behv=>auth-allowed
                        %action-approveOrder = if_abap_behv=>auth-allowed
                        %action-rejectOrder  = if_abap_behv=>auth-allowed ) ).
  ENDMETHOD.

ENDCLASS.
```

품목 핸들러에 이어 붙일 메서드입니다.

```abap
  "------------------------------------------------------------------
  " DETERMINATION: 품목 금액, 품목 통화, 부모 총액
  "------------------------------------------------------------------
  METHOD calculateAmounts.
    DATA lt_item_upd TYPE TABLE FOR UPDATE zrap_r_order_ud_###\\item.

    READ ENTITIES OF zrap_r_order_ud_### IN LOCAL MODE
      ENTITY Item
        FIELDS ( Quantity UnitPrice ) WITH CORRESPONDING #( keys )
      RESULT DATA(lt_items).

    READ ENTITIES OF zrap_r_order_ud_### IN LOCAL MODE
      ENTITY Item BY \_Order
        FIELDS ( CurrencyCode ) WITH CORRESPONDING #( keys )
      RESULT DATA(lt_orders).

    "--- 1) 품목 금액 + 통화 ----------------------------------------------
    LOOP AT lt_items INTO DATA(ls_item).
      READ TABLE lt_orders INTO DATA(ls_parent)
           WITH KEY OrderID = ls_item-OrderID %is_draft = ls_item-%is_draft.
      APPEND VALUE #( %tky         = ls_item-%tky
                      ItemAmount   = ls_item-Quantity * ls_item-UnitPrice
                      CurrencyCode = ls_parent-CurrencyCode ) TO lt_item_upd.
      CLEAR ls_parent.
    ENDLOOP.

    MODIFY ENTITIES OF zrap_r_order_ud_### IN LOCAL MODE
      ENTITY Item
        UPDATE FIELDS ( ItemAmount CurrencyCode ) WITH lt_item_upd
      REPORTED DATA(ls_item_reported).

    "--- 2) 부모 총액 = 형제 품목 금액의 합 --------------------------------
    READ ENTITIES OF zrap_r_order_ud_### IN LOCAL MODE
      ENTITY Order BY \_Items
        FIELDS ( ItemAmount ) WITH CORRESPONDING #( lt_orders )
      RESULT DATA(lt_siblings).

    MODIFY ENTITIES OF zrap_r_order_ud_### IN LOCAL MODE
      ENTITY Order
        UPDATE FIELDS ( TotalAmount )
        WITH VALUE #( FOR ls_order IN lt_orders
                      ( %tky        = ls_order-%tky
                        TotalAmount = REDUCE /dmo/total_price(
                                        INIT lv_sum = CONV /dmo/total_price( 0 )
                                        FOR ls_sib IN lt_siblings
                                        WHERE ( OrderID = ls_order-OrderID AND %is_draft = ls_order-%is_draft )
                                        NEXT lv_sum = lv_sum + ls_sib-ItemAmount ) ) )
      REPORTED DATA(ls_order_reported).

    reported = CORRESPONDING #( DEEP ls_item_reported ).
    APPEND LINES OF ls_order_reported-order TO reported-order.
  ENDMETHOD.

  "------------------------------------------------------------------
  " VALIDATION: 품목
  "------------------------------------------------------------------
  METHOD validateItem.
    DATA lt_products TYPE SORTED TABLE OF /dmo/supplement_id WITH UNIQUE KEY table_line.

    READ ENTITIES OF zrap_r_order_ud_### IN LOCAL MODE
      ENTITY Item
        FIELDS ( ProductID Quantity QuantityUnit UnitPrice ) WITH CORRESPONDING #( keys )
      RESULT DATA(lt_items).

    LOOP AT lt_items INTO DATA(ls_item) WHERE ProductID IS NOT INITIAL.
      INSERT ls_item-ProductID INTO TABLE lt_products.
    ENDLOOP.
    IF lt_products IS NOT INITIAL.
      SELECT FROM /dmo/supplement FIELDS supplement_id
        FOR ALL ENTRIES IN @lt_products
        WHERE supplement_id = @lt_products-table_line
        INTO TABLE @DATA(lt_known).
    ENDIF.

    LOOP AT lt_items INTO ls_item.
      " 부모 주문 화면에서도 메시지가 보이도록 %path로 부모를 가리킨다
      DATA(ls_path) = VALUE #( reported-item[ 1 ]-%path OPTIONAL ).
      CLEAR ls_path.
      ls_path-order-%is_draft = ls_item-%is_draft.
      ls_path-order-OrderID   = ls_item-OrderID.

      APPEND VALUE #( %tky = ls_item-%tky %state_area = 'VALIDATE_ITEM' %path = ls_path ) TO reported-item.

      IF ls_item-Quantity <= 0.
        APPEND VALUE #( %tky = ls_item-%tky ) TO failed-item.
        APPEND VALUE #( %tky              = ls_item-%tky
                        %state_area       = 'VALIDATE_ITEM'
                        %path             = ls_path
                        %msg              = lcl_msg=>new( iv_msgno = '020' iv_v2 = ls_item-ItemNo )
                        %element-Quantity = if_abap_behv=>mk-on ) TO reported-item.
      ENDIF.

      IF ls_item-QuantityUnit IS INITIAL.
        APPEND VALUE #( %tky = ls_item-%tky ) TO failed-item.
        APPEND VALUE #( %tky                  = ls_item-%tky
                        %state_area           = 'VALIDATE_ITEM'
                        %path                 = ls_path
                        %msg                  = lcl_msg=>new( iv_msgno = '021' iv_v2 = ls_item-ItemNo )
                        %element-QuantityUnit = if_abap_behv=>mk-on ) TO reported-item.
      ENDIF.

      IF ls_item-UnitPrice <= 0.
        APPEND VALUE #( %tky = ls_item-%tky ) TO failed-item.
        APPEND VALUE #( %tky               = ls_item-%tky
                        %state_area        = 'VALIDATE_ITEM'
                        %path              = ls_path
                        %msg               = lcl_msg=>new( iv_msgno = '022' iv_v2 = ls_item-ItemNo )
                        %element-UnitPrice = if_abap_behv=>mk-on ) TO reported-item.
      ENDIF.

      IF ls_item-ProductID IS INITIAL
      OR NOT line_exists( lt_known[ supplement_id = ls_item-ProductID ] ).
        APPEND VALUE #( %tky = ls_item-%tky ) TO failed-item.
        APPEND VALUE #( %tky               = ls_item-%tky
                        %state_area        = 'VALIDATE_ITEM'
                        %path              = ls_path
                        %msg               = lcl_msg=>new( iv_msgno = '023' iv_v1 = ls_item-ProductID )
                        %element-ProductID = if_abap_behv=>mk-on ) TO reported-item.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

  METHOD get_instance_features.
    READ ENTITIES OF zrap_r_order_ud_### IN LOCAL MODE
      ENTITY Item BY \_Order
        FIELDS ( Status ) WITH CORRESPONDING #( keys )
      RESULT DATA(lt_parents)
      FAILED failed.

    LOOP AT keys ASSIGNING FIELD-SYMBOL(<key>).
      DATA(lv_parent_new) = xsdbool( line_exists( lt_parents[ OrderID   = <key>-OrderID
                                                              %is_draft = <key>-%is_draft
                                                              Status    = zif_leg_order_###=>status-new ] ) ).
      APPEND VALUE #( %tky    = <key>-%tky
                      %update = COND #( WHEN lv_parent_new = abap_true
                                        THEN if_abap_behv=>fc-o-enabled ELSE if_abap_behv=>fc-o-disabled )
                      %delete = COND #( WHEN lv_parent_new = abap_true
                                        THEN if_abap_behv=>fc-o-enabled ELSE if_abap_behv=>fc-o-disabled ) )
             TO result.
    ENDLOOP.
  ENDMETHOD.

ENDCLASS.
```

왜 이렇게 쓰나

- **determination은 draft 인스턴스에서 "입력하는 동안" 값을 채워 주는 장치**입니다. R-06(non-draft)에서는 레거시가 생성·저장 때 기본값과 총액을 정했기 때문에 사용자는 저장해야 값이 보였습니다. draft에서는 저장(Activate) 전까지 레거시를 부르지 않으므로, 화면에 보일 값을 determination이 draft 버퍼에서 계산합니다. **최종 값은 여전히 레거시가 정합니다**(활성화 때 `create_order`/`determine_totals`). 두 계산 규칙이 같아야 사용자가 놀라지 않습니다.
- `MODIFY ... IN LOCAL MODE`로 readonly 필드(`Status`, `TotalAmount`, `ItemAmount`)를 바꿀 수 있습니다. readonly는 **외부 소비자**에 대한 제한입니다. 공식 draft 예제의 `setStatusToOpen`, `calculateTotalPrice`도 같은 방식입니다.
- active 인스턴스에 대해 이 determination이 돌면(EML로 active를 직접 만들 때 등) `MODIFY IN LOCAL MODE`가 우리의 active `update` 핸들러로 가는데, `ItemAmount`·`TotalAmount`·`Status`는 X 구조에 없으므로 레거시가 무시하고 자기 규칙으로 계산합니다. 레거시 쪽이 진실의 원천이라 안전합니다.
- **validation의 `%state_area`**: draft는 여러 요청에 걸쳐 살아 있으므로, 예전 Prepare에서 남긴 메시지를 지우지 않으면 고친 뒤에도 오류가 계속 보입니다. "먼저 같은 state area로 빈 줄을 넣어 지우고 → 오류가 있으면 다시 넣는" 패턴은 공식 `/DMO/BP_TRAVEL_D`의 `validateDates`와 같습니다.
- `%path`: 품목 오류를 부모 주문의 object page에서도 보여 주는 경로입니다. 공식 예제는 `%path = VALUE #( travel-%tky = ... )`로 부모의 `%tky`를 넣습니다. 여기서는 부모 `%tky`가 "같은 `%is_draft` + 같은 `OrderID`"라는 점을 이용해 링크 조회 없이 만들었습니다. `ls_path`의 타입을 얻으려고 `VALUE #( reported-item[ 1 ]-%path OPTIONAL )`를 쓴 것은 타입 이름을 몰라도 되게 하는 요령입니다.
- **validation과 레거시 `check_orders`의 이중 검사**: Prepare의 validation은 draft를 보고 **활성화 전에** 사용자에게 알려 줍니다. 레거시 `check_orders`(8단계 `check_before_save`)는 active 저장 직전 마지막 방어선입니다. 같은 메시지 번호를 쓰므로 사용자는 같은 문장을 봅니다.
- 품목 삭제 시 부모 총액은 draft에서 바로 갱신되지 않습니다(`calculateAmounts`는 create/필드 변경에만 반응). 활성화 때 레거시 `determine_totals`가 바로잡습니다. 즉시 갱신하려면 side effects와 부모 쪽 determination(R-10/R-11)을 씁니다.

</details>

#### 8단계. 세이버, 서비스, Fiori에서 draft 동작과 핸들러 호출 확인

요구사항

1. 세이버: R-06 10단계와 같되 **`adjust_numbers`가 없습니다**. `check_before_save`의 `%path`는 `order-OrderID`만 채웁니다(active만 저장되므로).
2. 서비스 정의 `ZRAP_UI_ORDER_UD_###`, 바인딩 `ZRAP_UI_ORDER_UD_O4_###`(OData V4 - UI)를 만들고 Preview를 엽니다.
3. **호출 순서 실험**: 행동 풀의 `earlynumbering_create`, `create`, `update`, `read`, `lock`, `rba_Items`, `cba_Items`, `validateHeader`, `check_before_save`, `save`에 ADT 브레이크포인트(외부 브레이크포인트)를 걸고, 아래 동작을 하나씩 하면서 **어디서 멈추는지** 표에 기록하세요.
   1. Create → 필드 입력 → (자동 저장되는 draft 변경)
   2. 품목 추가
   3. Save(= Activate)
   4. 활성화된 주문에서 Edit
   5. Edit 중인 주문에서 Note 변경 후 Save
   6. Edit 후 Discard
4. 잠금 확인: 브라우저 A에서 Edit한 상태로 두고, 다른 사용자(또는 다른 브라우저 세션)에서 같은 주문을 Edit → "다른 사용자가 편집 중" 메시지(레거시 메시지 004)가 나는지 확인하세요.

**직접 추가할 어노테이션**

- `@EndUserText.label`, `@ObjectModel.leadingEntity.name` — 서비스 정의 (R-06과 같은 목적)

**확인** 실험 결과가 아래 해설의 "예상 호출 표"와 일치하는지 비교합니다. 다르면 그 차이를 메모해 두세요(이 표 자체가 확인 필요 항목입니다).

<details><summary>정답·해설</summary>

```abap
CLASS lsc_zrap_r_order_ud_### IMPLEMENTATION.

  METHOD finalize.
    lcl_legacy=>get( )->determine_totals( ).
  ENDMETHOD.

  METHOD check_before_save.
    DATA ls_order_rep LIKE LINE OF reported-order.
    DATA ls_item_rep  LIKE LINE OF reported-item.

    lcl_legacy=>get( )->check_orders( IMPORTING et_messages = DATA(lt_messages) ).

    LOOP AT lt_messages INTO DATA(ls_message).
      DATA(lv_is_error) = zcl_rap_order_aux_###=>is_error( ls_message ).
      DATA(lv_element)  = zcl_rap_order_aux_###=>get_element_name( ls_message-fieldname ).

      IF ls_message-item_no IS INITIAL.
        IF lv_is_error = abap_true
        AND NOT line_exists( failed-order[ OrderID = ls_message-order_id ] ).
          APPEND VALUE #( OrderID = ls_message-order_id ) TO failed-order.
        ENDIF.
        CLEAR ls_order_rep.
        ls_order_rep-OrderID = ls_message-order_id.
        ls_order_rep-%msg    = zcm_leg_order_###=>from_legacy( ls_message ).
        IF lv_element IS NOT INITIAL.
          ASSIGN COMPONENT lv_element OF STRUCTURE ls_order_rep-%element TO FIELD-SYMBOL(<lv_order_flag>).
          IF sy-subrc = 0.
            <lv_order_flag> = if_abap_behv=>mk-on.
          ENDIF.
        ENDIF.
        APPEND ls_order_rep TO reported-order.
      ELSE.
        IF lv_is_error = abap_true
        AND NOT line_exists( failed-item[ OrderID = ls_message-order_id ItemNo = ls_message-item_no ] ).
          APPEND VALUE #( OrderID = ls_message-order_id ItemNo = ls_message-item_no ) TO failed-item.
        ENDIF.
        CLEAR ls_item_rep.
        ls_item_rep-OrderID             = ls_message-order_id.
        ls_item_rep-ItemNo              = ls_message-item_no.
        ls_item_rep-%msg                = zcm_leg_order_###=>from_legacy( ls_message ).
        ls_item_rep-%path-order-OrderID = ls_message-order_id.
        IF lv_element IS NOT INITIAL.
          ASSIGN COMPONENT lv_element OF STRUCTURE ls_item_rep-%element TO FIELD-SYMBOL(<lv_item_flag>).
          IF sy-subrc = 0.
            <lv_item_flag> = if_abap_behv=>mk-on.
          ENDIF.
        ENDIF.
        APPEND ls_item_rep TO reported-item.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

  METHOD save.
    lcl_legacy=>get( )->save( ).
  ENDMETHOD.

  METHOD cleanup.
    lcl_legacy=>get( )->initialize( ).
  ENDMETHOD.

  METHOD cleanup_finalize.
    " R-06과 같은 이유로 비워 둔다: 저장이 거부되면 사용자가 고쳐서 다시 활성화한다.
  ENDMETHOD.

ENDCLASS.
```

```cds
@EndUserText.label: 'Purchase order (unmanaged, draft) service ###'
@ObjectModel.leadingEntity.name: 'ZRAP_C_ORDER_UD_###'
define service ZRAP_UI_ORDER_UD_### {
  expose ZRAP_C_ORDER_UD_###     as PurchaseOrder;
  expose ZRAP_C_ORDITEM_UD_###   as PurchaseOrderItem;
  expose /DMO/I_Agency_StdVH     as Supplier;
  expose /DMO/I_Supplement_StdVH as Product;
  expose I_CurrencyStdVH         as Currency;
  expose I_UnitOfMeasure         as UnitOfMeasure;
}
```

예상 호출 표 (SAP 문서와 이 문제의 설계를 바탕으로 한 예상, **실제 시스템에서 확인 필요**)

| Fiori 동작 | 우리 코드에서 멈출 것으로 예상되는 곳 | 프레임워크가 하는 일 |
|---|---|---|
| 1 Create, 필드 입력 | `get_global_authorizations` → `earlynumbering_create`(`%is_draft = 01`) → `setDefaults` | draft 테이블에 새 행, 필드 변경마다 draft 갱신 |
| 2 품목 추가 | `earlynumbering_cba_Items` → `calculateAmounts`(수량/단가 입력 시) | draft 품목 행 추가 |
| 3 Save(Activate) | `validateHeader`, `validateItem`(Prepare) → `create`(active, `%is_draft = 00`) → `cba_Items` → `finalize` → `check_before_save` → `save` → `cleanup` | draft → active 변환 요청 생성, 성공 후 draft 삭제 |
| 4 Edit | `get_instance_authorizations`(Edit) → `lock` → `read` + `rba_Items`(active) | active 내용을 draft 테이블로 복사 |
| 5 Edit 후 Save | Prepare 검증 → `update`(바뀐 필드만 `%control`) → 저장 순서 | draft와 active 비교 후 변경분만 핸들러 호출 |
| 6 Discard | (없음) | draft 행 삭제, 잠금 해제 |

왜 이렇게 쓰나

- **세이버에 `adjust_numbers`가 없는 이유**: early numbering이라 저장 때 바뀌는 키가 없습니다. 레거시 `adjust_numbers`를 불러도 매핑이 비어 있지만, 부를 필요 자체가 없습니다. (레거시 `save`의 ASSERT는 "임시 번호가 남아 있지 않다"는 검사라 external 모드 주문은 통과합니다.)
- **잠금 수명의 차이**: R-06(non-draft)에서는 잠금이 요청 하나 동안만 유지됐습니다. draft에서는 Edit 순간 active 인스턴스를 잠그고(우리 `lock` 핸들러 → 레거시 `lock_order`), 프레임워크가 그 잠금을 draft가 사는 동안 유지합니다(일정 시간 뒤에는 낙관적 잠금 단계로 넘어가 total ETag로 판단 → `Resume`). 그래서 4번 실험에서 다른 사용자는 레거시 메시지 004를 받습니다.
- 3번 Activate에서 `create`/`cba_Items`가 받는 키는 draft 때 numbering이 준 번호 그대로입니다. 그래서 active 핸들러가 레거시 **external** 모드를 씁니다.
- 실험 결과가 표와 다르면, 그것이 바로 여러분 시스템의 사실입니다. 특히 5번에서 프레임워크가 "바뀐 필드만" `%control`을 켜는지, 아니면 전체 필드를 보내는지 확인해 보세요. 어느 경우든 X 구조 변환 덕분에 레거시는 올바르게 동작합니다.

자주 나는 오류와 해결

- Activate 시 `ASSERTION_FAILED`(우리 핸들러의 `ASSERT %is_draft = mk-off`): 전제가 틀린 경우입니다. 덤프의 호출 스택에서 어느 핸들러가 draft 인스턴스를 받았는지 확인하고, 그 핸들러에서 draft 인스턴스를 건너뛰도록(`CONTINUE`) 바꾼 뒤 결과를 비교하세요.
- Create 직후 "Order ... already exists"(005): MAX+1 방식에서 두 draft가 같은 번호를 받은 경우입니다. 번호 범위 방식으로 바꾸세요.
- Edit 버튼이 승인된 주문에서도 보임: Fiori의 Edit 버튼 표시는 `update` 기능 제어와 Edit 권한의 조합으로 정해집니다. 버튼이 보여도 Activate 때 레거시가 031로 거부합니다(Edit 자체에 기능 제어를 거는 문법은 실제 시스템에서 확인 필요).

</details>

#### 9단계. R-06 행동 풀을 테스트할 수 있게 만들기: FRIENDS와 가짜 레거시

요구사항

1. R-06 행동 풀 `ZBP_RAP_R_ORDER_U_###`의 **Local Types** 탭 맨 위에 테스트 클래스 두 개(`ltc_handler`, `ltc_saver`)를 `DEFINITION DEFERRED FOR TESTING`으로 미리 선언하세요.
2. 같은 탭에서 클래스 정의 네 개의 첫 문장에 `FRIENDS`를 붙이세요.
   - `lcl_legacy`: `ltc_handler`, `ltc_saver` (private 정적 속성 `go_double`에 가짜를 넣기 위해)
   - `lhc_order`, `lhc_item`: `ltc_handler` (private 핸들러 메서드를 직접 부르기 위해)
   - `lsc_zrap_r_order_u_###`: `ltc_saver` (protected 세이버 메서드를 직접 부르기 위해)
3. **Test Classes** 탭 맨 앞에 레거시 API의 가짜(fake) 클래스 `ltd_legacy`를 만드세요.
   - `ZIF_LEG_ORDER_###`를 구현하되 DB, 잠금, 번호 범위를 전혀 쓰지 않습니다.
   - **테스트가 미리 정하는 값**: 존재하는 주문/품목(`mt_orders`, `mt_items`), 모든 메서드가 돌려줄 메시지(`mt_messages`), `adjust_numbers`가 돌려줄 매핑 두 개.
   - **테스트가 나중에 확인하는 기록**: 호출된 메서드 이름 목록(`mt_calls`), 마지막으로 받은 numbering 모드, 헤더 값, 헤더 X 구조, 품목 값, 품목 X 구조.
   - `create_order`는 오류 메시지가 없으면 임시 번호 9000000001부터 돌려주고, `update_order`는 액션 코드 C인 품목에 10, 20, 30 순서로 번호를 붙여 돌려줍니다.
   - 메시지 한 줄을 쉽게 만드는 정적 도우미 `msg`와 호출 여부를 묻는 `was_called`를 두세요.
4. 아직 테스트 메서드는 없습니다. 이 단계에서는 활성화만 합니다(테스트 클래스 `ltc_handler`, `ltc_saver`는 10·11단계에서 만들므로, 이 단계에서는 Test Classes 탭에 두 클래스의 빈 정의/구현을 임시로 넣어 두어야 활성화됩니다).

**확인** 행동 풀 전체가 활성화됩니다. Local Types 탭의 `lcl_legacy` 정의에서 `go_double`에 커서를 두고 "Where-used"(Ctrl+Shift+G)를 실행하면, 아직은 `lcl_legacy` 구현에서만 쓰입니다.

<details><summary>정답·해설</summary>

Local Types 탭 **맨 위**에 추가합니다. (`*"* use this source file ...` 주석 바로 아래)

```abap
" 테스트 클래스 이름을 미리 알린다. 실제 정의는 Test Classes 탭에 있다.
CLASS ltc_handler DEFINITION DEFERRED FOR TESTING.
CLASS ltc_saver   DEFINITION DEFERRED FOR TESTING.
```

그리고 5단계에서 만든 네 클래스 정의의 **첫 문장만** 아래처럼 바꿉니다. 나머지 정의(PUBLIC/PRIVATE SECTION)와 구현은 그대로입니다.

```abap
CLASS lcl_legacy DEFINITION FINAL CREATE PRIVATE
  FRIENDS ltc_handler ltc_saver.
```

```abap
CLASS lhc_order DEFINITION INHERITING FROM cl_abap_behavior_handler
  FRIENDS ltc_handler.
```

```abap
CLASS lhc_item DEFINITION INHERITING FROM cl_abap_behavior_handler
  FRIENDS ltc_handler.
```

```abap
CLASS lsc_zrap_r_order_u_### DEFINITION INHERITING FROM cl_abap_behavior_saver
  FRIENDS ltc_saver.
```

Test Classes 탭 — 가짜 레거시입니다. (10·11단계의 테스트 클래스는 이 아래에 이어 붙입니다.)

```abap
*"* use this source file for your ABAP unit test classes

"=====================================================================
" ltd_legacy: 레거시 API의 가짜(fake). DB·잠금·번호 범위를 쓰지 않는다.
"=====================================================================
CLASS ltd_legacy DEFINITION FINAL FOR TESTING.
  PUBLIC SECTION.
    INTERFACES zif_leg_order_###.

    TYPES: BEGIN OF ty_call,
             method   TYPE string,
             order_id TYPE zif_leg_order_###=>t_order_id,
           END OF ty_call,
           tt_call TYPE STANDARD TABLE OF ty_call WITH EMPTY KEY.

    "--- 테스트가 미리 정하는 동작 --------------------------------------
    "! 이 주문/품목은 '존재한다' (read_orders가 돌려주고 set_status가 바꾼다)
    DATA mt_orders        TYPE zif_leg_order_###=>tt_order.
    DATA mt_items         TYPE zif_leg_order_###=>tt_item.
    "! 메시지를 돌려주는 모든 메서드가 이 메시지를 돌려준다
    DATA mt_messages      TYPE zif_leg_order_###=>tt_message.
    DATA mt_order_mapping TYPE zif_leg_order_###=>tt_order_mapping.
    DATA mt_item_mapping  TYPE zif_leg_order_###=>tt_item_mapping.

    "--- 테스트가 나중에 확인하는 기록 ----------------------------------
    DATA mt_calls          TYPE tt_call.
    DATA mv_numbering_mode TYPE zif_leg_order_###=>t_numbering_mode.
    DATA ms_order_in       TYPE zif_leg_order_###=>ts_order_in.
    DATA ms_orderx         TYPE zif_leg_order_###=>ts_order_inx.
    DATA mt_items_in       TYPE zif_leg_order_###=>tt_item_in.
    DATA mt_itemsx         TYPE zif_leg_order_###=>tt_item_inx.

    "! 메서드가 한 번이라도 불렸나 (이름은 대문자, 예: `SAVE`)
    METHODS was_called
      IMPORTING iv_method        TYPE string
      RETURNING VALUE(rv_called) TYPE abap_bool.

    "! 레거시 메시지 한 줄 만들기 (메시지 클래스는 레거시 것)
    CLASS-METHODS msg
      IMPORTING iv_msgno          TYPE symsgno
                iv_msgty          TYPE symsgty DEFAULT 'E'
                iv_order_id       TYPE zif_leg_order_###=>t_order_id OPTIONAL
                iv_item_no        TYPE zif_leg_order_###=>t_item_no OPTIONAL
                iv_fieldname      TYPE string OPTIONAL
      RETURNING VALUE(rs_message) TYPE zif_leg_order_###=>ts_message.

  PRIVATE SECTION.
    DATA mv_last_preliminary TYPE zif_leg_order_###=>t_order_id
         VALUE zif_leg_order_###=>late_numbering_boundary.

    METHODS log
      IMPORTING iv_method   TYPE string
                iv_order_id TYPE zif_leg_order_###=>t_order_id OPTIONAL.

    METHODS has_error
      RETURNING VALUE(rv_error) TYPE abap_bool.
ENDCLASS.

CLASS ltd_legacy IMPLEMENTATION.

  METHOD msg.
    rs_message = VALUE #( msgty     = iv_msgty
                          msgid     = zif_leg_order_###=>message_class
                          msgno     = iv_msgno
                          msgv1     = iv_order_id
                          order_id  = iv_order_id
                          item_no   = iv_item_no
                          fieldname = iv_fieldname ).
  ENDMETHOD.

  METHOD was_called.
    rv_called = xsdbool( line_exists( mt_calls[ method = iv_method ] ) ).
  ENDMETHOD.

  METHOD log.
    APPEND VALUE #( method = iv_method order_id = iv_order_id ) TO mt_calls.
  ENDMETHOD.

  METHOD has_error.
    rv_error = xsdbool( line_exists( mt_messages[ msgty = 'E' ] )
                     OR line_exists( mt_messages[ msgty = 'A' ] ) ).
  ENDMETHOD.

  METHOD zif_leg_order_###~create_order.
    log( iv_method = `CREATE_ORDER` iv_order_id = is_order-order_id ).
    mv_numbering_mode = iv_numbering_mode.
    ms_order_in       = is_order.
    mt_items_in       = it_items.
    CLEAR: es_order, et_items.
    et_messages = mt_messages.
    IF has_error( ) = abap_true.
      RETURN.                                    " 전부 아니면 전무: 아무것도 만들지 않음
    ENDIF.

    es_order = CORRESPONDING #( is_order ).
    IF iv_numbering_mode = zif_leg_order_###=>numbering_mode-external.
      es_order-order_id = is_order-order_id.
    ELSE.
      mv_last_preliminary = mv_last_preliminary + 1.
      es_order-order_id   = mv_last_preliminary.
    ENDIF.
    es_order-status = zif_leg_order_###=>status-new.
    APPEND es_order TO mt_orders.                " 같은 테스트 안에서 다시 읽을 수 있게
  ENDMETHOD.

  METHOD zif_leg_order_###~update_order.
    log( iv_method = `UPDATE_ORDER` iv_order_id = is_orderx-order_id ).
    ms_order_in = is_order.
    ms_orderx   = is_orderx.
    mt_items_in = it_items.
    mt_itemsx   = it_itemsx.
    CLEAR: es_order, et_items.
    et_messages = mt_messages.
    IF has_error( ) = abap_true.
      RETURN.
    ENDIF.

    " 액션 코드 C인 품목: 레거시처럼 10, 20, 30 순서로 번호를 붙여 돌려준다
    LOOP AT it_itemsx INTO DATA(ls_itemx).
      DATA(lv_index) = sy-tabix.
      IF ls_itemx-action_code <> zif_leg_order_###=>action_code-create.
        CONTINUE.
      ENDIF.
      DATA(ls_item) = CORRESPONDING zif_leg_order_###=>ts_item( it_items[ lv_index ] ).
      ls_item-order_id = is_orderx-order_id.
      ls_item-item_no  = ( lines( mt_items ) + 1 ) * 10.
      APPEND ls_item TO mt_items.
      APPEND ls_item TO et_items.
    ENDLOOP.
  ENDMETHOD.

  METHOD zif_leg_order_###~delete_order.
    log( iv_method = `DELETE_ORDER` iv_order_id = iv_order_id ).
    et_messages = mt_messages.
  ENDMETHOD.

  METHOD zif_leg_order_###~set_status.
    log( iv_method = `SET_STATUS` iv_order_id = iv_order_id ).
    CLEAR es_order.
    et_messages = mt_messages.
    IF has_error( ) = abap_true.
      RETURN.
    ENDIF.
    LOOP AT mt_orders ASSIGNING FIELD-SYMBOL(<ls_order>) WHERE order_id = iv_order_id.
      <ls_order>-status = iv_status.
      es_order = <ls_order>.
    ENDLOOP.
  ENDMETHOD.

  METHOD zif_leg_order_###~read_orders.
    log( iv_method = `READ_ORDERS` ).
    CLEAR: et_orders, et_items, et_messages.

    LOOP AT mt_orders INTO DATA(ls_order).
      IF line_exists( it_order_ids[ table_line = ls_order-order_id ] ).
        APPEND ls_order TO et_orders.
      ENDIF.
    ENDLOOP.

    IF iv_with_items = abap_true.
      LOOP AT mt_items INTO DATA(ls_item).
        IF line_exists( it_order_ids[ table_line = ls_item-order_id ] ).
          APPEND ls_item TO et_items.
        ENDIF.
      ENDLOOP.
    ENDIF.
  ENDMETHOD.

  METHOD zif_leg_order_###~lock_order.
    log( iv_method = `LOCK_ORDER` iv_order_id = iv_order_id ).
    et_messages = mt_messages.
  ENDMETHOD.

  METHOD zif_leg_order_###~draw_order_ids.
    log( iv_method = `DRAW_ORDER_IDS` ).
    CLEAR et_ids.
    et_messages = mt_messages.
  ENDMETHOD.

  METHOD zif_leg_order_###~check_orders.
    log( iv_method = `CHECK_ORDERS` ).
    et_messages = mt_messages.
  ENDMETHOD.

  METHOD zif_leg_order_###~determine_totals.
    log( iv_method = `DETERMINE_TOTALS` ).
  ENDMETHOD.

  METHOD zif_leg_order_###~adjust_numbers.
    log( iv_method = `ADJUST_NUMBERS` ).
    et_order_mapping = mt_order_mapping.
    et_item_mapping  = mt_item_mapping.
  ENDMETHOD.

  METHOD zif_leg_order_###~save.
    log( iv_method = `SAVE` ).
  ENDMETHOD.

  METHOD zif_leg_order_###~initialize.
    log( iv_method = `INITIALIZE` ).
  ENDMETHOD.

ENDCLASS.
```

이 단계에서 활성화하려면 Test Classes 탭 아래쪽에 다음 임시 정의가 필요합니다. 10·11단계에서 진짜 정의로 바꿉니다.

```abap
CLASS ltc_handler DEFINITION FINAL FOR TESTING DURATION SHORT RISK LEVEL HARMLESS.
ENDCLASS.

CLASS ltc_handler IMPLEMENTATION.
ENDCLASS.

CLASS ltc_saver DEFINITION FINAL FOR TESTING DURATION SHORT RISK LEVEL HARMLESS.
ENDCLASS.

CLASS ltc_saver IMPLEMENTATION.
ENDCLASS.
```

클래스 구조 해설

| 클래스 | 어디에 | 누가 누구의 친구인가 | 하는 일 |
|---|---|---|---|
| `ltd_legacy` | Test Classes 탭 | (친구 아님, PUBLIC SECTION만 씀) | `ZIF_LEG_ORDER_###`의 가짜. 정해 둔 값을 돌려주고 받은 값을 기록 |
| `ltc_handler` | Test Classes 탭 | `lcl_legacy`, `lhc_order`, `lhc_item`이 `ltc_handler`를 친구로 지정 | 핸들러 메서드 단위 테스트 (10단계) |
| `ltc_saver` | Test Classes 탭 | `lcl_legacy`, `lsc_zrap_r_order_u_###`가 `ltc_saver`를 친구로 지정 | 세이버 메서드 단위 테스트 (11단계) |
| `ltc_integration` | Test Classes 탭 | 친구 필요 없음 (EML만 씀) | 진짜 레거시 + DB 대역 통합 테스트 (11단계) |
| `ltc_order_stats` | `ZCL_RAP_ORDER_STATS_###`의 Test Classes 탭 | 친구 필요 없음 | BO 소비자 테스트, BO 전체를 트랜잭션 버퍼 대역으로 (12단계) |

왜 이렇게 쓰나

- **`DEFINITION DEFERRED FOR TESTING` + `FRIENDS`**: 핸들러 메서드는 `PRIVATE SECTION`, 세이버 메서드는 `PROTECTED SECTION`에 있어 밖에서 부를 수 없습니다. 테스트 클래스를 친구로 지정하면 테스트만 접근할 수 있습니다. 그런데 Local Types 탭은 Test Classes 탭보다 **먼저** 컴파일되므로, 아직 정의되지 않은 `ltc_handler`를 `FRIENDS`에 쓰려면 이름을 미리 알려야 합니다. 그것이 `DEFERRED`입니다. 공식 `/DMO/BP_TRAVEL_U`도 `CLASS ltcl_handler DEFINITION DEFERRED FOR TESTING.` 다음에 `lhc_travel ... FRIENDS ltcl_handler`, `ltcl_saver`에 대해서도 같은 방식을 씁니다.
- **의존성 주입 지점이 하나뿐**: 모든 핸들러·세이버가 `lcl_legacy=>get( )`만 거쳐 레거시를 쓰므로, 테스트는 `lcl_legacy=>go_double = 가짜` 한 줄로 레거시 전체를 바꿀 수 있습니다. 공식 예제는 레거시가 함수 모듈이라 `cl_function_test_environment`로 함수 모듈을 대역으로 바꿉니다. 이 문제의 레거시는 클래스 + 인터페이스이므로 주입이 더 간단합니다.
- **스텁(stub)이 아니라 가짜(fake)를 쓴 이유**: 단순히 값을 돌려주는 스텁이면 `cl_abap_testdouble`로 충분합니다(10단계 마지막 테스트). 하지만 기능 제어 테스트처럼 "create가 만든 주문을 read가 다시 읽는" 흐름에서는 상태를 가진 가짜가 편합니다. 또 `mt_calls`, `ms_orderx`처럼 **핸들러가 레거시에 무엇을 넘겼는지**를 기록해 두면 "%control → X 구조" 변환을 직접 검증할 수 있습니다.
- **`mt_messages` 하나로 모든 메서드의 메시지를 정하는 이유**: 핸들러 메서드 하나는 보통 레거시 메서드 한 종류만 부릅니다. 테스트마다 "이번에 레거시가 무슨 메시지를 낼지"만 정하면 되므로 메서드별 설정은 필요 없습니다. 여러 레거시 메서드를 부르는 핸들러(예: `cba_Items`는 `read_orders` + `update_order`)를 테스트할 때는, `read_orders`가 메시지를 돌려주지 않게 만들어 두었으므로 문제가 없습니다.
- `INTERFACES ... PARTIALLY IMPLEMENTED`를 쓰면 필요한 메서드만 구현해도 됩니다(테스트 클래스에서만 허용, ABAP 치트시트 "ABAP Unit Tests"). 여기서는 모든 메서드에 호출 기록을 남기려고 전부 구현했습니다.

자주 나는 오류와 해결

- "The class LTC_HANDLER is unknown"(Local Types 탭): `DEFINITION DEFERRED` 줄이 `FRIENDS`를 쓴 정의보다 **아래**에 있습니다. 탭 맨 위로 옮기세요.
- "LTC_HANDLER is defined as deferred but not defined": Test Classes 탭에 `ltc_handler` 정의가 아직 없습니다. 위의 임시 빈 정의를 넣으세요.
- "Method CREATE_ORDER is not implemented"(가짜): 인터페이스 메서드를 하나라도 빠뜨렸습니다. 모두 구현하거나 `PARTIALLY IMPLEMENTED`를 쓰세요.
- `ls_item-item_no = ( lines( mt_items ) + 1 ) * 10.`에서 경고가 나면, `item_no`가 NUMC 4이므로 정수 → NUMC 변환입니다. 9999를 넘지 않는 한 문제없습니다.

</details>

#### 10단계. 핸들러 단위 테스트: 가짜 레거시로 계약 검증

요구사항

Test Classes 탭의 임시 `ltc_handler`를 진짜 테스트 클래스로 바꾸세요.

1. 클래스 위에 ABAP Doc `"! @testing BDEF:ZRAP_R_ORDER_U_###`를 붙이세요.
2. `setup`: 가짜를 새로 만들어 `lcl_legacy=>go_double`에 넣고, `CREATE OBJECT ... FOR TESTING`으로 `lhc_order`, `lhc_item` 인스턴스를 만드세요. `teardown`: `go_double`을 비우세요.
3. 응답 변수는 `RESPONSE FOR MAPPED/FAILED/REPORTED EARLY zrap_r_order_u_###`로 선언하세요.
4. 테스트 메서드 (하나의 메서드 = 하나의 계약)
   - `create_success_maps_cid`: 성공하면 `mapped-order`에 `%cid` + 임시 번호 `9000000001`, 레거시는 late 모드로 불렸고, `%control`이 꺼진 필드(Note)는 레거시에 가지 않았음
   - `create_error_fills_failed`: 레거시 메시지 010(필드 `SUPPLIER_ID`) → `mapped` 비었음, `failed-order` 한 줄(`%cid`, `cause-unspecific`), `reported-order`의 `%element-SupplierID`가 켜짐, `%msg`의 심각도가 오류
   - `update_sends_only_flagged`: `%control-Note`만 켠 update → 가짜가 받은 X 구조에서 `note = 'X'`, `requester`는 비었음
   - `read_found_and_not_found`: 키 두 개 중 하나만 존재 → `result` 한 줄(`StatusCriticality = 3`), `failed-order` 한 줄(`cause-not_found`)
   - `lock_conflict_is_locked`: 레거시 메시지 004 → `cause-locked`
   - `cba_missing_parent_dependency`: 부모가 없음 → 부모 failed 한 줄(`%assoc-_Items`, not_found), 자식 failed 두 줄(dependency), 레거시 `update_order`는 불리지 않음
   - `cba_success_maps_item`: 부모 있음 → `mapped-item`에 `%cid`, 주문 번호, 품목 번호 `0010`, 레거시가 받은 품목 액션 코드 C
   - `features_by_status`: 상태 N(품목 있음) / A 주문 → `%update`, `%action-approveOrder`, `%field-CurrencyCode` 결과
   - `item_update_action_code_u`: 품목 update → 액션 코드 U, `_intx-quantity = 'X'`, `_intx-unit_price` 비었음
   - `lock_with_abap_testdouble`: 가짜 대신 `cl_abap_testdouble`로 같은 잠금 테스트

**직접 추가할 어노테이션**

- `"! @testing BDEF:ZRAP_R_ORDER_U_###` (ABAP Doc) — 이 테스트 클래스가 BDEF를 테스트한다고 연결합니다. BDEF 편집기에서 단위 테스트를 실행하면 이 테스트가 함께 실행됩니다.

**확인** Test Classes 탭에서 Ctrl+Shift+F10을 누르면 `ltc_handler`의 10개 테스트가 모두 초록색입니다. 일부러 6단계 `create`의 `USING CONTROL`을 지워 보고 `create_success_maps_cid`가 빨개지는지 보세요(보내지 않은 Note까지 레거시에 넘어감).

<details><summary>정답·해설</summary>

```abap
"! @testing BDEF:ZRAP_R_ORDER_U_###
CLASS ltc_handler DEFINITION FINAL FOR TESTING
  DURATION SHORT
  RISK LEVEL HARMLESS.

  PRIVATE SECTION.
    CONSTANTS c_cid         TYPE abp_behv_cid VALUE 'C1'.
    CONSTANTS c_order_id    TYPE zif_leg_order_###=>t_order_id VALUE '0000000001'.
    CONSTANTS c_approved_id TYPE zif_leg_order_###=>t_order_id VALUE '0000000002'.
    CONSTANTS c_missing_id  TYPE zif_leg_order_###=>t_order_id VALUE '0000000099'.
    CONSTANTS c_prelim_id   TYPE zif_leg_order_###=>t_order_id VALUE '9000000001'.
    CONSTANTS c_item_10     TYPE zif_leg_order_###=>t_item_no  VALUE '0010'.

    DATA mo_fake  TYPE REF TO ltd_legacy.
    DATA mo_order TYPE REF TO lhc_order.
    DATA mo_item  TYPE REF TO lhc_item.

    DATA mapped   TYPE RESPONSE FOR MAPPED   EARLY zrap_r_order_u_###.
    DATA failed   TYPE RESPONSE FOR FAILED   EARLY zrap_r_order_u_###.
    DATA reported TYPE RESPONSE FOR REPORTED EARLY zrap_r_order_u_###.

    METHODS setup.
    METHODS teardown.

    METHODS create_success_maps_cid       FOR TESTING RAISING cx_static_check.
    METHODS create_error_fills_failed     FOR TESTING RAISING cx_static_check.
    METHODS update_sends_only_flagged     FOR TESTING RAISING cx_static_check.
    METHODS read_found_and_not_found      FOR TESTING RAISING cx_static_check.
    METHODS lock_conflict_is_locked       FOR TESTING RAISING cx_static_check.
    METHODS cba_missing_parent_dependency FOR TESTING RAISING cx_static_check.
    METHODS cba_success_maps_item         FOR TESTING RAISING cx_static_check.
    METHODS features_by_status            FOR TESTING RAISING cx_static_check.
    METHODS item_update_action_code_u     FOR TESTING RAISING cx_static_check.
    METHODS lock_with_abap_testdouble     FOR TESTING RAISING cx_static_check.
ENDCLASS.

CLASS ltc_handler IMPLEMENTATION.

  METHOD setup.
    mo_fake = NEW #( ).
    lcl_legacy=>go_double = mo_fake.            " FRIENDS 덕분에 private 정적 속성에 접근
    CREATE OBJECT mo_order FOR TESTING.         " 핸들러는 NEW로 만들 수 없다
    CREATE OBJECT mo_item  FOR TESTING.
    CLEAR: mapped, failed, reported.
  ENDMETHOD.

  METHOD teardown.
    CLEAR lcl_legacy=>go_double.                " 다음 테스트(특히 통합 테스트)가 진짜 레거시를 쓰도록
  ENDMETHOD.

  METHOD create_success_maps_cid.
    DATA lt_entities TYPE TABLE FOR CREATE zrap_r_order_u_###\\order.

    lt_entities = VALUE #( ( %cid       = c_cid
                             Requester  = 'ALICE'
                             SupplierID = '070001'
                             Note       = 'not sent'                 " 값은 있지만 %control이 꺼져 있음
                             %control   = VALUE #( Requester  = if_abap_behv=>mk-on
                                                   SupplierID = if_abap_behv=>mk-on ) ) ).

    mo_order->create( EXPORTING entities = lt_entities
                      CHANGING  mapped   = mapped
                                failed   = failed
                                reported = reported ).

    cl_abap_unit_assert=>assert_initial( failed ).
    cl_abap_unit_assert=>assert_initial( reported ).

    cl_abap_unit_assert=>assert_equals( act = lines( mapped-order ) exp = 1 ).
    cl_abap_unit_assert=>assert_equals( act = mapped-order[ 1 ]-%cid    exp = c_cid ).
    cl_abap_unit_assert=>assert_equals( act = mapped-order[ 1 ]-OrderID exp = c_prelim_id ).

    " 레거시에 무엇이 넘어갔나
    cl_abap_unit_assert=>assert_equals( act = mo_fake->mv_numbering_mode
                                        exp = zif_leg_order_###=>numbering_mode-late ).
    cl_abap_unit_assert=>assert_equals( act = mo_fake->ms_order_in-requester exp = 'ALICE' ).
    cl_abap_unit_assert=>assert_initial( mo_fake->ms_order_in-note ).
  ENDMETHOD.

  METHOD create_error_fills_failed.
    mo_fake->mt_messages = VALUE #( ( ltd_legacy=>msg( iv_msgno     = '010'
                                                       iv_fieldname = `SUPPLIER_ID` ) ) ).

    mo_order->create( EXPORTING entities = VALUE #( ( %cid                = c_cid
                                                      SupplierID          = '999999'
                                                      %control-SupplierID = if_abap_behv=>mk-on ) )
                      CHANGING  mapped   = mapped
                                failed   = failed
                                reported = reported ).

    cl_abap_unit_assert=>assert_initial( mapped ).

    " failed: 인스턴스당 한 줄, 원인은 보조 클래스 규칙(010 → unspecific)
    cl_abap_unit_assert=>assert_equals( act = lines( failed-order ) exp = 1 ).
    cl_abap_unit_assert=>assert_equals( act = failed-order[ 1 ]-%cid        exp = c_cid ).
    cl_abap_unit_assert=>assert_equals( act = failed-order[ 1 ]-%fail-cause exp = if_abap_behv=>cause-unspecific ).

    " reported: 메시지 객체 + 필드 표시
    cl_abap_unit_assert=>assert_equals( act = lines( reported-order ) exp = 1 ).
    DATA(ls_reported) = reported-order[ 1 ].
    cl_abap_unit_assert=>assert_equals( act = ls_reported-%cid                exp = c_cid ).
    cl_abap_unit_assert=>assert_equals( act = ls_reported-%element-SupplierID exp = if_abap_behv=>mk-on ).
    cl_abap_unit_assert=>assert_equals( act = ls_reported-%msg->m_severity
                                        exp = if_abap_behv_message=>severity-error ).
    cl_abap_unit_assert=>assert_equals( act = ls_reported-%msg->if_t100_message~t100key-msgno
                                        exp = '010' ).
  ENDMETHOD.

  METHOD update_sends_only_flagged.
    mo_order->update( EXPORTING entities = VALUE #( ( OrderID       = c_order_id
                                                      Note          = 'changed'
                                                      Requester     = 'BOB'       " %control 꺼짐
                                                      %control-Note = if_abap_behv=>mk-on ) )
                      CHANGING  mapped   = mapped
                                failed   = failed
                                reported = reported ).

    cl_abap_unit_assert=>assert_initial( failed ).
    cl_abap_unit_assert=>assert_equals( act = mo_fake->ms_orderx-order_id   exp = c_order_id ).
    cl_abap_unit_assert=>assert_equals( act = mo_fake->ms_orderx-_intx-note exp = abap_true ).
    cl_abap_unit_assert=>assert_initial( mo_fake->ms_orderx-_intx-requester ).
    cl_abap_unit_assert=>assert_equals( act = mo_fake->ms_order_in-note exp = 'changed' ).
  ENDMETHOD.

  METHOD read_found_and_not_found.
    DATA lt_result TYPE TABLE FOR READ RESULT zrap_r_order_u_###\\order.

    mo_fake->mt_orders = VALUE #( ( order_id = c_order_id
                                    status   = zif_leg_order_###=>status-approved
                                    note     = 'exists' ) ).

    mo_order->read( EXPORTING keys     = VALUE #( ( OrderID = c_order_id   %control-Note = if_abap_behv=>mk-on )
                                                  ( OrderID = c_missing_id %control-Note = if_abap_behv=>mk-on ) )
                    CHANGING  result   = lt_result
                              failed   = failed
                              reported = reported ).

    cl_abap_unit_assert=>assert_equals( act = lines( lt_result ) exp = 1 ).
    cl_abap_unit_assert=>assert_equals( act = lt_result[ 1 ]-Note              exp = 'exists' ).
    cl_abap_unit_assert=>assert_equals( act = lt_result[ 1 ]-StatusCriticality exp = 3 ).

    cl_abap_unit_assert=>assert_equals( act = lines( failed-order ) exp = 1 ).
    cl_abap_unit_assert=>assert_equals( act = failed-order[ 1 ]-OrderID     exp = c_missing_id ).
    cl_abap_unit_assert=>assert_equals( act = failed-order[ 1 ]-%fail-cause exp = if_abap_behv=>cause-not_found ).
  ENDMETHOD.

  METHOD lock_conflict_is_locked.
    mo_fake->mt_messages = VALUE #( ( ltd_legacy=>msg( iv_msgno    = '004'
                                                       iv_order_id = c_order_id ) ) ).

    mo_order->lock( EXPORTING keys     = VALUE #( ( OrderID = c_order_id ) )
                    CHANGING  failed   = failed
                              reported = reported ).

    cl_abap_unit_assert=>assert_equals( act = failed-order[ 1 ]-OrderID     exp = c_order_id ).
    cl_abap_unit_assert=>assert_equals( act = failed-order[ 1 ]-%fail-cause exp = if_abap_behv=>cause-locked ).
    cl_abap_unit_assert=>assert_not_initial( reported-order ).
  ENDMETHOD.

  METHOD cba_missing_parent_dependency.
    DATA lt_cba TYPE TABLE FOR CREATE zrap_r_order_u_###\\order\_items.

    " mt_orders가 비어 있으므로 부모가 없다
    lt_cba = VALUE #( ( OrderID = c_missing_id
                        %target = VALUE #( ( %cid = 'I1'  Quantity = 1  %control-Quantity = if_abap_behv=>mk-on )
                                           ( %cid = 'I2'  Quantity = 2  %control-Quantity = if_abap_behv=>mk-on ) ) ) ).

    mo_order->cba_Items( EXPORTING entities_cba = lt_cba
                         CHANGING  mapped       = mapped
                                   failed       = failed
                                   reported     = reported ).

    cl_abap_unit_assert=>assert_equals( act = lines( failed-order ) exp = 1 ).
    cl_abap_unit_assert=>assert_equals( act = failed-order[ 1 ]-%assoc-_Items exp = if_abap_behv=>mk-on ).
    cl_abap_unit_assert=>assert_equals( act = failed-order[ 1 ]-%fail-cause   exp = if_abap_behv=>cause-not_found ).

    cl_abap_unit_assert=>assert_equals( act = lines( failed-item ) exp = 2 ).
    LOOP AT failed-item INTO DATA(ls_failed_item).
      cl_abap_unit_assert=>assert_equals( act = ls_failed_item-%fail-cause exp = if_abap_behv=>cause-dependency ).
    ENDLOOP.

    cl_abap_unit_assert=>assert_initial( mapped ).
    cl_abap_unit_assert=>assert_false( mo_fake->was_called( `UPDATE_ORDER` ) ).
  ENDMETHOD.

  METHOD cba_success_maps_item.
    mo_fake->mt_orders = VALUE #( ( order_id = c_order_id  status = zif_leg_order_###=>status-new ) ).

    mo_order->cba_Items(
      EXPORTING entities_cba = VALUE #( ( OrderID = c_order_id
                                          %target = VALUE #( ( %cid               = 'I1'
                                                               ProductID          = 'TST-0001'
                                                               Quantity           = 2
                                                               %control-ProductID = if_abap_behv=>mk-on
                                                               %control-Quantity  = if_abap_behv=>mk-on ) ) ) )
      CHANGING  mapped       = mapped
                failed       = failed
                reported     = reported ).

    cl_abap_unit_assert=>assert_initial( failed ).
    cl_abap_unit_assert=>assert_equals( act = lines( mapped-item ) exp = 1 ).
    cl_abap_unit_assert=>assert_equals( act = mapped-item[ 1 ]-%cid    exp = 'I1' ).
    cl_abap_unit_assert=>assert_equals( act = mapped-item[ 1 ]-OrderID exp = c_order_id ).
    cl_abap_unit_assert=>assert_equals( act = mapped-item[ 1 ]-ItemNo  exp = c_item_10 ).

    cl_abap_unit_assert=>assert_equals( act = mo_fake->mt_itemsx[ 1 ]-action_code
                                        exp = zif_leg_order_###=>action_code-create ).
    cl_abap_unit_assert=>assert_equals( act = mo_fake->mt_items_in[ 1 ]-quantity exp = 2 ).
  ENDMETHOD.

  METHOD features_by_status.
    DATA lt_result TYPE TABLE FOR INSTANCE FEATURES RESULT zrap_r_order_u_###\\order.

    mo_fake->mt_orders = VALUE #( ( order_id = c_order_id    status = zif_leg_order_###=>status-new )
                                  ( order_id = c_approved_id status = zif_leg_order_###=>status-approved ) ).
    mo_fake->mt_items  = VALUE #( ( order_id = c_order_id    item_no = c_item_10 ) ).

    " get_instance_features는 안에서 READ ENTITIES IN LOCAL MODE를 쓴다.
    " 그 READ는 프레임워크를 거쳐 우리 read/rba_Items 핸들러 → lcl_legacy=>get( ) → 가짜로 간다.
    mo_order->get_instance_features(
      EXPORTING keys               = VALUE #( ( OrderID = c_order_id ) ( OrderID = c_approved_id ) )
                requested_features = VALUE #( %update              = if_abap_behv=>mk-on
                                              %action-approveOrder = if_abap_behv=>mk-on )
      CHANGING  result             = lt_result
                failed             = failed
                reported           = reported ).

    cl_abap_unit_assert=>assert_initial( failed ).
    cl_abap_unit_assert=>assert_equals( act = lines( lt_result ) exp = 2 ).

    DATA(ls_new) = lt_result[ OrderID = c_order_id ].
    cl_abap_unit_assert=>assert_equals( act = ls_new-%update              exp = if_abap_behv=>fc-o-enabled ).
    cl_abap_unit_assert=>assert_equals( act = ls_new-%action-approveOrder exp = if_abap_behv=>fc-o-enabled ).
    cl_abap_unit_assert=>assert_equals( act = ls_new-%field-CurrencyCode  exp = if_abap_behv=>fc-f-read_only ).

    DATA(ls_approved) = lt_result[ OrderID = c_approved_id ].
    cl_abap_unit_assert=>assert_equals( act = ls_approved-%update              exp = if_abap_behv=>fc-o-disabled ).
    cl_abap_unit_assert=>assert_equals( act = ls_approved-%action-approveOrder exp = if_abap_behv=>fc-o-disabled ).
    cl_abap_unit_assert=>assert_equals( act = ls_approved-%field-CurrencyCode  exp = if_abap_behv=>fc-f-mandatory ).
  ENDMETHOD.

  METHOD item_update_action_code_u.
    mo_item->update( EXPORTING entities = VALUE #( ( OrderID           = c_order_id
                                                     ItemNo            = c_item_10
                                                     Quantity          = 5
                                                     UnitPrice         = '99.00'      " %control 꺼짐
                                                     %control-Quantity = if_abap_behv=>mk-on ) )
                     CHANGING  mapped   = mapped
                               failed   = failed
                               reported = reported ).

    cl_abap_unit_assert=>assert_initial( failed ).
    cl_abap_unit_assert=>assert_equals( act = lines( mo_fake->mt_itemsx ) exp = 1 ).

    DATA(ls_itemx) = mo_fake->mt_itemsx[ 1 ].
    cl_abap_unit_assert=>assert_equals( act = ls_itemx-action_code    exp = zif_leg_order_###=>action_code-update ).
    cl_abap_unit_assert=>assert_equals( act = ls_itemx-item_no        exp = c_item_10 ).
    cl_abap_unit_assert=>assert_equals( act = ls_itemx-_intx-quantity exp = abap_true ).
    cl_abap_unit_assert=>assert_initial( ls_itemx-_intx-unit_price ).
  ENDMETHOD.

  METHOD lock_with_abap_testdouble.
    " 1) 인터페이스로 대역 객체를 만든다 (가짜 클래스를 직접 쓰지 않음)
    DATA(lo_double) = CAST zif_leg_order_###( cl_abap_testdouble=>create( 'ZIF_LEG_ORDER_###' ) ).

    " 2) '이 인자로 lock_order가 불리면 ET_MESSAGES에 이 값을 돌려줘라'
    DATA(lt_messages) = VALUE zif_leg_order_###=>tt_message(
                          ( ltd_legacy=>msg( iv_msgno = '004' iv_order_id = c_order_id ) ) ).
    cl_abap_testdouble=>configure_call( lo_double )->set_parameter( name  = 'ET_MESSAGES'
                                                                   value = lt_messages ).
    lo_double->lock_order( iv_order_id = c_order_id ).       " 설정을 이 호출(인자)에 묶는다

    " 3) 주입하고 테스트
    lcl_legacy=>go_double = lo_double.

    mo_order->lock( EXPORTING keys     = VALUE #( ( OrderID = c_order_id ) )
                    CHANGING  failed   = failed
                              reported = reported ).

    cl_abap_unit_assert=>assert_equals( act = failed-order[ 1 ]-%fail-cause exp = if_abap_behv=>cause-locked ).
  ENDMETHOD.

ENDCLASS.
```

왜 이렇게 쓰나

- **`CREATE OBJECT ... FOR TESTING`**: 행동 핸들러 클래스(`cl_abap_behavior_handler` 상속)는 프레임워크만 만들 수 있어 `NEW`가 금지됩니다. 테스트에서만 `FOR TESTING` 추가로 인스턴스를 만들 수 있습니다. 공식 `/DMO/BP_TRAVEL_U`의 `ltcl_handler`와 `ltcl_saver`가 같은 문장을 씁니다.
- **핸들러를 직접 부를 때의 파라미터**: BDEF가 만드는 암묵적 파라미터 `mapped`, `failed`, `reported`(그리고 read의 `result`, features의 `result`)를 `CHANGING`으로 넘깁니다. 타입은 BO 전체 응답 `RESPONSE FOR ... EARLY zrap_r_order_u_###`이며 주문/품목 핸들러가 같은 타입을 씁니다. lock은 `mapped`가 없어 `failed`, `reported`만 넘깁니다(공식 `lock_success` 테스트와 같음).
- **단언(assert)의 대상**: unmanaged BO 핸들러의 계약은 "레거시 결과를 RAP 응답으로 정확히 옮기는가"입니다. 그래서 테스트는 두 방향을 확인합니다. (1) 레거시 → RAP: `mapped`/`failed`/`reported`의 키, `%cid`, `%fail-cause`, `%element`. (2) RAP → 레거시: 가짜가 받은 numbering 모드, X 구조, 액션 코드.
- **`%msg` 검사**: `%msg`의 정적 타입은 `if_abap_behv_message`이며, 이 인터페이스는 `if_t100_dyn_msg`(→ `if_t100_message`)를 포함합니다. 그래서 `m_severity`와 `if_t100_message~t100key-msgno`를 바로 읽을 수 있습니다.
- **`features_by_status`는 반쯤 통합 테스트입니다.** 기능 제어 메서드가 `READ ENTITIES ... IN LOCAL MODE`를 쓰므로, 이 테스트는 프레임워크를 거쳐 프레임워크가 만든 **다른** `lhc_order` 인스턴스의 `read`/`rba_Items`를 부릅니다. `go_double`이 정적 속성이라 그 인스턴스도 가짜를 씁니다. 공식 `/DMO/BP_TRAVEL_U`의 기능 제어 테스트는 이 READ를 BO 대역으로 바꾸는 코드가 주석 처리되어 있습니다. 이 방식이 여러분 시스템에서 동작하는지는 실제 시스템에서 확인 필요합니다. 동작하지 않으면 이 테스트를 11단계 통합 테스트 쪽으로 옮기세요.
- **`cl_abap_testdouble`과 가짜 클래스의 비교**: `cl_abap_testdouble=>create`는 인터페이스만 주면 대역 객체를 만들어 주므로 가짜 클래스를 쓸 필요가 없습니다. 반환값은 `->returning( )`(ABAP 치트시트 "ABAP Unit Tests"의 예), 출력 파라미터는 `->set_parameter( name = ... value = ... )`로 정합니다. `set_parameter`의 정확한 사용법(대문자 이름, 설정 뒤 기록 호출에 인자를 모두 줘야 하는지)은 실제 시스템에서 확인 필요합니다. 상태를 기억해야 하는 흐름에는 가짜 클래스가, 값 하나를 돌려주면 되는 경우에는 `cl_abap_testdouble`이 편합니다.
- 함수 모듈 레거시를 감싼 경우라면 공식 예제처럼 `cl_function_test_environment=>create( function_modules = ... )`와 `get_double( )->configure_call( )->ignore_all_parameters( )->then_set_output( )`을 씁니다. 이 문제의 레거시는 클래스라서 필요 없습니다.

자주 나는 오류와 해결

- "LHC_ORDER cannot be instantiated" / "Instance creation of LHC_ORDER is not allowed": `CREATE OBJECT ... FOR TESTING` 대신 `NEW`를 썼습니다.
- "Access to private component CREATE of LHC_ORDER is not allowed": 9단계의 `FRIENDS ltc_handler`를 빠뜨렸거나 테스트 클래스 이름이 다릅니다.
- 테스트가 진짜 DB/잠금을 건드림(예: `cause-locked`가 아니라 실제 잠금 오류): `setup`에서 `go_double`을 설정하지 않았습니다. `lcl_legacy=>get( )`에 브레이크포인트를 걸어 어느 객체가 반환되는지 보세요.
- 테스트 하나만 실행하면 통과하고 전체 실행에서 실패: 테스트 사이에 상태가 남았습니다. `setup`에서 가짜를 **새로** 만들고 응답 변수를 `CLEAR`하는지 확인하세요.
- `create_error_fills_failed`에서 `%fail-cause`가 기대와 다름: 가짜 메시지의 `msgid`가 레거시 메시지 클래스가 아니면 보조 클래스가 무조건 `unspecific`을 돌려줍니다. `ltd_legacy=>msg`를 쓰세요.

</details>

#### 11단계. 세이버 단위 테스트와 EML 통합 테스트

요구사항

1. Test Classes 탭의 임시 `ltc_saver`를 진짜 테스트 클래스로 바꾸세요.
   - 응답 변수는 `RESPONSE FOR MAPPED/FAILED/REPORTED LATE zrap_r_order_u_###`.
   - `setup`: 가짜 주입 + `CREATE OBJECT mo_saver FOR TESTING`. `teardown`: `go_double` 비우기.
   - `finalize_derives_totals`: `finalize` → 레거시 `determine_totals`가 불렸고 failed는 비었음
   - `check_maps_header_and_item`: 레거시 메시지 3개(헤더 011 `DELIVERY_DATE`, 품목 020 `QUANTITY`, 품목 021 `QUANTITY_UNIT`) → `failed-order` 한 줄, `failed-item` 한 줄(인스턴스당 한 줄), `reported-order` 한 줄(`%element-DeliveryDate`), `reported-item` 두 줄(`%element-Quantity`, `%element-QuantityUnit`)
   - `adjust_numbers_maps_tmp`: 주문 매핑 1개, 품목 매핑 2개(새 주문의 품목 + 기존 주문의 새 품목 a=a) → `mapped-order`/`mapped-item`의 `%tmp`와 최종 키
   - `save_delegates`, `cleanup_initializes`: 레거시 `save`/`initialize`가 불렸음
   - `cleanup_finalize_keeps_buffer`: 예외 없음 + 레거시를 한 번도 부르지 않음(버퍼 유지)
2. 같은 탭에 통합 테스트 클래스 `ltc_integration`을 만드세요. **가짜를 쓰지 않고** 진짜 레거시를 씁니다.
   - `class_setup`: `cl_osql_test_environment`로 `ZLEG_ORDH_###`, `ZLEG_ORDI_###`, `/DMO/AGENCY`, `/DMO/SUPPLEMENT`를 대역으로 바꿉니다.
   - `setup`: 대역 비우기 + 공급업체 `070001`, 제품 `TST-0001`(EUR 10.00) 넣기. `teardown`: `ROLLBACK ENTITIES`.
   - `create_commit_final_number`: EML로 주문 + 품목 생성 → `mapped`의 주문 번호는 임시 번호(≥ 9000000000) → `COMMIT ENTITIES` 성공 → 대역 DB의 주문 번호는 최종 번호(< 9000000000), 상태 N, 총액 20.00, 품목의 주문 번호도 최종 번호
   - `commit_rejected_by_check`: 납기일 < 주문일 → 생성은 성공, `COMMIT ENTITIES`가 실패(`failed-order`, `%element-DeliveryDate`), 대역 DB는 비어 있음

**직접 추가할 어노테이션**

- `"! @testing BDEF:ZRAP_R_ORDER_U_###` (ABAP Doc) — `ltc_saver`와 `ltc_integration` 위에 붙여 BDEF와 연결합니다.

**확인** Ctrl+Shift+F10으로 `ltc_saver` 6개, `ltc_integration` 2개가 모두 초록색입니다. 일부러 10단계(R-06) 세이버의 `check_before_save`에서 `%element`를 켜는 `ASSIGN COMPONENT` 블록을 지워 보고 `check_maps_header_and_item`이 빨개지는지 보세요.

<details><summary>정답·해설</summary>

```abap
"! @testing BDEF:ZRAP_R_ORDER_U_###
CLASS ltc_saver DEFINITION FINAL FOR TESTING
  DURATION SHORT
  RISK LEVEL HARMLESS.

  PRIVATE SECTION.
    CONSTANTS c_prelim   TYPE zif_leg_order_###=>t_order_id VALUE '9000000001'.
    CONSTANTS c_final    TYPE zif_leg_order_###=>t_order_id VALUE '0000000042'.
    CONSTANTS c_existing TYPE zif_leg_order_###=>t_order_id VALUE '0000000005'.
    CONSTANTS c_item_10  TYPE zif_leg_order_###=>t_item_no  VALUE '0010'.
    CONSTANTS c_item_30  TYPE zif_leg_order_###=>t_item_no  VALUE '0030'.

    DATA mo_fake  TYPE REF TO ltd_legacy.
    DATA mo_saver TYPE REF TO lsc_zrap_r_order_u_###.

    DATA mapped   TYPE RESPONSE FOR MAPPED   LATE zrap_r_order_u_###.
    DATA failed   TYPE RESPONSE FOR FAILED   LATE zrap_r_order_u_###.
    DATA reported TYPE RESPONSE FOR REPORTED LATE zrap_r_order_u_###.

    METHODS setup.
    METHODS teardown.

    METHODS finalize_derives_totals       FOR TESTING RAISING cx_static_check.
    METHODS check_maps_header_and_item    FOR TESTING RAISING cx_static_check.
    METHODS adjust_numbers_maps_tmp       FOR TESTING RAISING cx_static_check.
    METHODS save_delegates                FOR TESTING RAISING cx_static_check.
    METHODS cleanup_initializes           FOR TESTING RAISING cx_static_check.
    METHODS cleanup_finalize_keeps_buffer FOR TESTING RAISING cx_static_check.
ENDCLASS.

CLASS ltc_saver IMPLEMENTATION.

  METHOD setup.
    mo_fake = NEW #( ).
    lcl_legacy=>go_double = mo_fake.
    CREATE OBJECT mo_saver FOR TESTING.
    CLEAR: mapped, failed, reported.
  ENDMETHOD.

  METHOD teardown.
    CLEAR lcl_legacy=>go_double.
  ENDMETHOD.

  METHOD finalize_derives_totals.
    mo_saver->finalize( CHANGING failed   = failed
                                 reported = reported ).

    cl_abap_unit_assert=>assert_true( mo_fake->was_called( `DETERMINE_TOTALS` ) ).
    cl_abap_unit_assert=>assert_initial( failed ).
  ENDMETHOD.

  METHOD check_maps_header_and_item.
    mo_fake->mt_messages = VALUE #(
      ( ltd_legacy=>msg( iv_msgno = '011' iv_order_id = c_prelim
                         iv_fieldname = `DELIVERY_DATE` ) )
      ( ltd_legacy=>msg( iv_msgno = '020' iv_order_id = c_prelim iv_item_no = c_item_10
                         iv_fieldname = `QUANTITY` ) )
      ( ltd_legacy=>msg( iv_msgno = '021' iv_order_id = c_prelim iv_item_no = c_item_10
                         iv_fieldname = `QUANTITY_UNIT` ) ) ).

    mo_saver->check_before_save( CHANGING failed   = failed
                                          reported = reported ).

    " failed: 인스턴스당 한 줄 (LATE: %cid 없음, 키로 식별)
    cl_abap_unit_assert=>assert_equals( act = lines( failed-order ) exp = 1 ).
    cl_abap_unit_assert=>assert_equals( act = failed-order[ 1 ]-OrderID exp = c_prelim ).
    cl_abap_unit_assert=>assert_equals( act = lines( failed-item ) exp = 1 ).
    cl_abap_unit_assert=>assert_equals( act = failed-item[ 1 ]-OrderID exp = c_prelim ).
    cl_abap_unit_assert=>assert_equals( act = failed-item[ 1 ]-ItemNo  exp = c_item_10 ).

    " reported: 메시지마다 한 줄 + 필드 표시
    cl_abap_unit_assert=>assert_equals( act = lines( reported-order ) exp = 1 ).
    cl_abap_unit_assert=>assert_equals( act = reported-order[ 1 ]-%element-DeliveryDate
                                        exp = if_abap_behv=>mk-on ).
    cl_abap_unit_assert=>assert_equals( act = lines( reported-item ) exp = 2 ).
    cl_abap_unit_assert=>assert_equals( act = reported-item[ 1 ]-%element-Quantity
                                        exp = if_abap_behv=>mk-on ).
    cl_abap_unit_assert=>assert_equals( act = reported-item[ 2 ]-%element-QuantityUnit
                                        exp = if_abap_behv=>mk-on ).
  ENDMETHOD.

  METHOD adjust_numbers_maps_tmp.
    mo_fake->mt_order_mapping = VALUE #( ( preliminary = c_prelim  final = c_final ) ).
    mo_fake->mt_item_mapping  = VALUE #(
      " 새 주문의 품목: 주문 번호가 바뀐다
      ( preliminary = VALUE #( order_id = c_prelim   item_no = c_item_10 )
        final       = VALUE #( order_id = c_final    item_no = c_item_10 ) )
      " 기존 주문에 추가한 품목: 키가 그대로여도 매핑이 있어야 한다 (a = a)
      ( preliminary = VALUE #( order_id = c_existing item_no = c_item_30 )
        final       = VALUE #( order_id = c_existing item_no = c_item_30 ) ) ).

    mo_saver->adjust_numbers( CHANGING mapped   = mapped
                                       reported = reported ).

    cl_abap_unit_assert=>assert_initial( reported ).

    cl_abap_unit_assert=>assert_equals( act = lines( mapped-order ) exp = 1 ).
    cl_abap_unit_assert=>assert_equals( act = mapped-order[ OrderID = c_final ]-%tmp-OrderID
                                        exp = c_prelim ).

    cl_abap_unit_assert=>assert_equals( act = lines( mapped-item ) exp = 2 ).
    DATA(ls_new_item) = mapped-item[ OrderID = c_final ItemNo = c_item_10 ].
    cl_abap_unit_assert=>assert_equals( act = ls_new_item-%tmp-OrderID exp = c_prelim ).
    cl_abap_unit_assert=>assert_equals( act = ls_new_item-%tmp-ItemNo  exp = c_item_10 ).
    DATA(ls_same_item) = mapped-item[ OrderID = c_existing ItemNo = c_item_30 ].
    cl_abap_unit_assert=>assert_equals( act = ls_same_item-%tmp-OrderID exp = c_existing ).
  ENDMETHOD.

  METHOD save_delegates.
    mo_saver->save( CHANGING reported = reported ).

    cl_abap_unit_assert=>assert_true( mo_fake->was_called( `SAVE` ) ).
    cl_abap_unit_assert=>assert_initial( reported ).
  ENDMETHOD.

  METHOD cleanup_initializes.
    mo_saver->cleanup( ).

    cl_abap_unit_assert=>assert_true( mo_fake->was_called( `INITIALIZE` ) ).
  ENDMETHOD.

  METHOD cleanup_finalize_keeps_buffer.
    TRY.
        mo_saver->cleanup_finalize( ).
      CATCH cx_root INTO DATA(lx_root).
        cl_abap_unit_assert=>fail( msg = lx_root->get_text( ) ).
    ENDTRY.

    " 레거시를 전혀 부르지 않았다 = 버퍼를 지우지 않았다 (사용자가 고쳐서 다시 저장할 수 있다)
    cl_abap_unit_assert=>assert_initial( mo_fake->mt_calls ).
  ENDMETHOD.

ENDCLASS.

"=====================================================================
" 통합 테스트: 진짜 레거시 + DB 대역 + EML + COMMIT ENTITIES
"=====================================================================
"! @testing BDEF:ZRAP_R_ORDER_U_###
CLASS ltc_integration DEFINITION FINAL FOR TESTING
  DURATION SHORT
  RISK LEVEL HARMLESS.

  PRIVATE SECTION.
    CLASS-DATA go_sql_env TYPE REF TO if_osql_test_environment.

    CONSTANTS c_supplier TYPE /dmo/agency_id     VALUE '070001'.
    CONSTANTS c_product  TYPE /dmo/supplement_id VALUE 'TST-0001'.

    CLASS-METHODS class_setup.
    CLASS-METHODS class_teardown.
    METHODS setup.
    METHODS teardown.

    METHODS create_commit_final_number FOR TESTING RAISING cx_static_check.
    METHODS commit_rejected_by_check   FOR TESTING RAISING cx_static_check.
ENDCLASS.

CLASS ltc_integration IMPLEMENTATION.

  METHOD class_setup.
    " 레거시 클래스의 Open SQL이 읽고 쓰는 테이블을 모두 대역으로
    go_sql_env = cl_osql_test_environment=>create(
                   i_dependency_list = VALUE #( ( 'ZLEG_ORDH_###' )
                                                ( 'ZLEG_ORDI_###' )
                                                ( '/DMO/AGENCY' )
                                                ( '/DMO/SUPPLEMENT' ) ) ).
  ENDMETHOD.

  METHOD class_teardown.
    go_sql_env->destroy( ).
  ENDMETHOD.

  METHOD setup.
    DATA lt_agency     TYPE STANDARD TABLE OF /dmo/agency     WITH EMPTY KEY.
    DATA lt_supplement TYPE STANDARD TABLE OF /dmo/supplement WITH EMPTY KEY.

    go_sql_env->clear_doubles( ).

    lt_agency     = VALUE #( ( agency_id = c_supplier  name = 'Test supplier' ) ).
    lt_supplement = VALUE #( ( supplement_id = c_product  price = '10.00'  currency_code = 'EUR' ) ).
    go_sql_env->insert_test_data( lt_agency ).
    go_sql_env->insert_test_data( lt_supplement ).
  ENDMETHOD.

  METHOD teardown.
    " 레거시 버퍼를 비운다 (세이버 cleanup → 레거시 initialize)
    ROLLBACK ENTITIES.
  ENDMETHOD.

  METHOD create_commit_final_number.
    DATA(lv_today) = cl_abap_context_info=>get_system_date( ).

    "--- 상호작용 단계 ---------------------------------------------------
    MODIFY ENTITIES OF zrap_r_order_u_###
      ENTITY Order
        CREATE FIELDS ( Requester SupplierID OrderDate DeliveryDate CurrencyCode )
        WITH VALUE #( ( %cid         = 'O1'
                        Requester    = 'ALICE'
                        SupplierID   = c_supplier
                        OrderDate    = lv_today
                        DeliveryDate = lv_today + 7
                        CurrencyCode = 'EUR' ) )
        CREATE BY \_Items FIELDS ( ProductID Quantity QuantityUnit UnitPrice )
        WITH VALUE #( ( %cid_ref = 'O1'
                        %target  = VALUE #( ( %cid         = 'I1'
                                              ProductID    = c_product
                                              Quantity     = 2
                                              QuantityUnit = 'EA'
                                              UnitPrice    = '10.00' ) ) ) )
      MAPPED   DATA(ls_mapped)
      FAILED   DATA(ls_failed)
      REPORTED DATA(ls_reported).

    cl_abap_unit_assert=>assert_initial( ls_failed ).
    cl_abap_unit_assert=>assert_initial( ls_reported ).
    " 키 필드에는 레거시 임시 번호
    cl_abap_unit_assert=>assert_true(
      xsdbool( ls_mapped-order[ 1 ]-OrderID >= zif_leg_order_###=>late_numbering_boundary ) ).

    "--- 저장 단계 -------------------------------------------------------
    COMMIT ENTITIES RESPONSE OF zrap_r_order_u_###
      FAILED   DATA(ls_commit_failed)
      REPORTED DATA(ls_commit_reported).

    cl_abap_unit_assert=>assert_initial( ls_commit_failed ).
    cl_abap_unit_assert=>assert_initial( ls_commit_reported ).

    " DB(대역)에는 최종 번호로 들어갔다
    SELECT * FROM zleg_ordh_### INTO TABLE @DATA(lt_headers).
    cl_abap_unit_assert=>assert_equals( act = lines( lt_headers ) exp = 1 ).
    DATA(ls_header) = lt_headers[ 1 ].
    cl_abap_unit_assert=>assert_true(
      xsdbool( ls_header-order_id < zif_leg_order_###=>late_numbering_boundary ) ).
    cl_abap_unit_assert=>assert_equals( act = ls_header-status       exp = zif_leg_order_###=>status-new ).
    cl_abap_unit_assert=>assert_equals( act = ls_header-total_amount exp = '20.00' ).   " finalize의 총액 파생

    SELECT * FROM zleg_ordi_### INTO TABLE @DATA(lt_items).
    cl_abap_unit_assert=>assert_equals( act = lines( lt_items ) exp = 1 ).
    cl_abap_unit_assert=>assert_equals( act = lt_items[ 1 ]-order_id exp = ls_header-order_id ).
  ENDMETHOD.

  METHOD commit_rejected_by_check.
    DATA(lv_today) = cl_abap_context_info=>get_system_date( ).

    MODIFY ENTITIES OF zrap_r_order_u_###
      ENTITY Order
        CREATE FIELDS ( Requester SupplierID OrderDate DeliveryDate CurrencyCode )
        WITH VALUE #( ( %cid         = 'O1'
                        Requester    = 'ALICE'
                        SupplierID   = c_supplier
                        OrderDate    = lv_today
                        DeliveryDate = lv_today - 1          " 주문일보다 앞
                        CurrencyCode = 'EUR' ) )
      FAILED DATA(ls_failed).

    " 납기일 검사는 저장 전 검사이므로 생성 자체는 성공
    cl_abap_unit_assert=>assert_initial( ls_failed ).

    COMMIT ENTITIES RESPONSE OF zrap_r_order_u_###
      FAILED   DATA(ls_commit_failed)
      REPORTED DATA(ls_commit_reported).

    cl_abap_unit_assert=>assert_not_initial( ls_commit_failed-order ).
    cl_abap_unit_assert=>assert_true(
      xsdbool( line_exists( ls_commit_reported-order[ %element-DeliveryDate = if_abap_behv=>mk-on ] ) ) ).

    " 저장이 거부되었으므로 DB(대역)는 비어 있다
    SELECT COUNT(*) FROM zleg_ordh_### INTO @DATA(lv_count).
    cl_abap_unit_assert=>assert_equals( act = lv_count exp = 0 ).
  ENDMETHOD.

ENDCLASS.
```

왜 이렇게 쓰나

- **세이버 테스트의 LATE 타입**: 세이버 메서드의 암묵적 파라미터는 `RESPONSE FOR ... LATE`입니다. 공식 `ltcl_saver`가 `finalize`/`check_before_save`는 `CHANGING failed reported`, `adjust_numbers`는 `CHANGING mapped reported`, `save`는 `CHANGING reported`, `cleanup`/`cleanup_finalize`는 파라미터 없이 부르는 것과 같은 모양입니다.
- **`adjust_numbers` 테스트에 a=a 매핑을 넣은 이유**: late numbering 엔터티는 이번 트랜잭션에서 생성된 **모든** 인스턴스에 대해 `adjust_numbers`에서 매핑을 받아야 합니다. 기존 주문에 품목만 추가한 경우에도 마찬가지입니다(R-05 10단계에서 레거시에 이 매핑을 추가한 이유). 이 테스트는 세이버가 그 매핑을 빠뜨리지 않고 옮기는지 확인합니다. 공식 테스트도 `mapped-travel[ KEY entity %key = ... ]-%tmp`로 "최종 키로 찾은 줄의 `%tmp`가 임시 키인가"를 확인합니다.
- **단위 테스트와 통합 테스트의 역할 분담**

| | 단위 테스트 (`ltc_handler`, `ltc_saver`) | 통합 테스트 (`ltc_integration`) |
|---|---|---|
| 레거시 | 가짜 (`ltd_legacy`) | 진짜 (`ZCL_LEG_ORDER_###`) |
| DB | 안 씀 | `cl_osql_test_environment` 대역 |
| 부르는 방법 | 핸들러/세이버 메서드 직접 호출 | EML (`MODIFY ENTITIES`, `COMMIT ENTITIES`) |
| 확인하는 것 | 메서드 하나의 매핑 규칙 | 핸들러 → 저장 순서 → 레거시 → DB 전체 흐름, late numbering 키 교체 |
| 빠르기/안정성 | 매우 빠름, 외부 영향 없음 | 느림, 번호 범위·잠금 서버에 의존 |

- **통합 테스트에서 `COMMIT ENTITIES`를 써도 되는 이유**: RAP 워크숍 `rap400` 연습 3의 테스트 클래스도 대역 환경에서 `MODIFY ENTITIES` → `COMMIT ENTITIES` → `SELECT`로 결과를 확인합니다. 쓰기는 대역 테이블로 가므로 실제 데이터는 바뀌지 않습니다. 다만 **번호 범위 `ZLEGORD###`의 번호는 실제로 소비**됩니다(번호 범위 객체는 Open SQL 대역의 대상이 아님). 팀 규칙상 영구 부작용이 있는 테스트를 `RISK LEVEL DANGEROUS`로 분류해야 한다면 그렇게 바꾸세요. 번호 범위 대신 MAX+1 방식(R-05 7단계)을 쓰고 있다면 대역 테이블이 비어 있으므로 최종 번호는 `0000000001`이 됩니다.
- **최종 번호를 `mapped`가 아니라 DB에서 확인하는 이유**: `MODIFY`의 `mapped`에는 상호작용 단계의 키(임시 번호)만 있습니다. 저장 뒤의 최종 키를 EML로 얻으려면 late numbering 전용 문법(`CONVERT KEY`)이 필요한데, 이 BO처럼 임시 번호를 `%pid`가 아니라 키 필드에 넣은 경우의 사용법은 실제 시스템에서 확인 필요합니다. 그래서 테스트는 확실한 방법인 대역 DB 조회를 씁니다.
- **`teardown`의 `ROLLBACK ENTITIES`**: 실패한 저장(두 번째 테스트)은 트랜잭션을 상호작용 단계로 되돌릴 뿐 버퍼를 지우지 않습니다(`cleanup_finalize`가 비어 있음). 다음 테스트가 남은 버퍼를 보지 않도록 반드시 롤백합니다. 레거시가 싱글턴이라 버퍼가 테스트 사이에 살아남기 때문에 특히 중요합니다.

자주 나는 오류와 해결

- 통합 테스트에서 `COMMIT ENTITIES`가 실패하고 reported에 010(공급업체 없음): `/DMO/AGENCY`를 대역 목록에 넣었지만 `setup`에서 데이터를 넣지 않았습니다. 대역 테이블은 처음에 비어 있습니다.
- 통합 테스트에서 040(번호 범위 오류): 번호 범위 구간이 없습니다. R-05 11단계의 콘솔 클래스로 구간을 만들거나 MAX+1 방식으로 바꾸세요.
- 통합 테스트가 단독으로는 통과하고 함께 돌리면 실패: 단위 테스트의 `teardown`이 `go_double`을 비우지 않아 통합 테스트가 가짜를 쓰고 있습니다.
- `mapped-order[ OrderID = c_final ]`에서 `CX_SY_ITAB_LINE_NOT_FOUND`: 세이버가 `%tmp`와 키를 거꾸로 넣었습니다(임시 번호를 키에, 최종 번호를 `%tmp`에). R-06 10단계 `adjust_numbers`를 다시 보세요.
- 세이버 테스트에서 "Access to protected component FINALIZE is not allowed": 9단계의 `FRIENDS ltc_saver`를 빠뜨렸습니다.
- 통합 테스트에서 행동 풀 안의 EML이 문법/실행 오류로 막히면(실제 시스템에서 확인 필요), `rap400`처럼 별도의 전역 테스트 클래스(`FOR TESTING`이 붙은 클래스)로 옮기세요. 그 경우 `"! @testing BDEF:` 줄을 같이 옮깁니다.

</details>

#### 12단계. BO 소비자 클래스와 트랜잭션 버퍼 대역 테스트, R-07 오류 정리

요구사항

1. 전역 클래스 `ZCL_RAP_ORDER_STATS_###`를 만드세요(BO를 **쓰는 쪽** 코드).
   - 공개 메서드 `summarize_open( it_keys ) RETURNING rs_summary`: 받은 주문 키들을 `READ ENTITIES OF zrap_r_order_u_###`로 읽어, 상태 N 주문의 개수와 총액 합계, 통화, 통화가 섞였는지, 찾지 못한 키 수를 돌려줍니다.
   - 통화가 섞이면 합계는 비웁니다(의미 없는 합계를 돌려주지 않음).
2. 이 클래스의 Test Classes 탭에 `ltc_order_stats`를 만드세요.
   - `class_setup`: `cl_botd_txbufdbl_bo_test_env`로 `ZRAP_R_ORDER_U_###`의 트랜잭션 버퍼 대역 환경을 만듭니다. `class_teardown`: `destroy`.
   - `setup`: `clear_doubles` + `get_test_double` + 테스트 대상 생성.
   - 테스트 데이터는 대역의 `insert_test_data( instances = ... )`로 넣습니다(`TABLE FOR CREATE`).
   - `sums_only_open_orders`: N 100.00 EUR, N 50.00 EUR, A 999.00 EUR → 2건, 150.00, EUR
   - `counts_unknown_keys`: 1건만 있는데 키 2개 → not_found 1
   - `mixed_currency_no_sum`: N EUR + N USD → mixed, 합계 비었음, 2건
3. 마지막으로 R-07 전체에서 자주 나는 오류를 표로 정리하세요.

**확인** `ZCL_RAP_ORDER_STATS_###`에서 Ctrl+Shift+F10으로 3개 테스트가 초록색입니다. 테스트 실행 중 R-06 행동 풀의 `lhc_order->read`에 브레이크포인트를 걸어도 **멈추지 않는** 것을 확인하세요(BO 전체가 대역으로 바뀜).

<details><summary>정답·해설</summary>

전역 클래스(Global Class 탭)입니다.

```abap
"! 구매 주문 BO의 소비자: 열린(신규) 주문 요약
CLASS zcl_rap_order_stats_### DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    TYPES tt_keys TYPE TABLE FOR READ IMPORT zrap_r_order_u_###\\order.

    TYPES: BEGIN OF ts_open_summary,
             open_count     TYPE i,
             open_amount    TYPE zleg_ordh_###-total_amount,
             currency_code  TYPE zleg_ordh_###-currency_code,
             mixed_currency TYPE abap_bool,
             not_found      TYPE i,
           END OF ts_open_summary.

    "! 주어진 주문 중 상태 N(신규) 주문의 개수와 총액 합계
    METHODS summarize_open
      IMPORTING it_keys           TYPE tt_keys
      RETURNING VALUE(rs_summary) TYPE ts_open_summary.

  PROTECTED SECTION.
  PRIVATE SECTION.
ENDCLASS.

CLASS zcl_rap_order_stats_### IMPLEMENTATION.

  METHOD summarize_open.
    READ ENTITIES OF zrap_r_order_u_###
      ENTITY Order
        FIELDS ( Status TotalAmount CurrencyCode ) WITH CORRESPONDING #( it_keys )
      RESULT DATA(lt_orders)
      FAILED DATA(ls_failed).

    rs_summary-not_found = lines( ls_failed-order ).

    LOOP AT lt_orders INTO DATA(ls_order)
         WHERE Status = zif_leg_order_###=>status-new.
      IF rs_summary-open_count = 0.
        rs_summary-currency_code = ls_order-CurrencyCode.
      ELSEIF ls_order-CurrencyCode <> rs_summary-currency_code.
        rs_summary-mixed_currency = abap_true.
      ENDIF.
      rs_summary-open_count  += 1.
      rs_summary-open_amount += ls_order-TotalAmount.
    ENDLOOP.

    IF rs_summary-mixed_currency = abap_true.
      CLEAR: rs_summary-open_amount, rs_summary-currency_code.   " 통화가 섞인 합계는 의미 없음
    ENDIF.
  ENDMETHOD.

ENDCLASS.
```

Test Classes 탭입니다.

```abap
CLASS ltc_order_stats DEFINITION FINAL FOR TESTING
  DURATION SHORT
  RISK LEVEL HARMLESS.

  PRIVATE SECTION.
    CLASS-DATA go_env TYPE REF TO if_botd_txbufdbl_bo_test_env.

    DATA mo_double TYPE REF TO if_botd_txbufdbl_test_double.
    DATA mo_cut    TYPE REF TO zcl_rap_order_stats_###.

    CLASS-METHODS class_setup.
    CLASS-METHODS class_teardown.
    METHODS setup.

    METHODS sums_only_open_orders FOR TESTING RAISING cx_static_check.
    METHODS counts_unknown_keys   FOR TESTING RAISING cx_static_check.
    METHODS mixed_currency_no_sum FOR TESTING RAISING cx_static_check.
ENDCLASS.

CLASS ltc_order_stats IMPLEMENTATION.

  METHOD class_setup.
    " BO 전체(핸들러·세이버·레거시)를 트랜잭션 버퍼 대역으로 바꾼다
    go_env = cl_botd_txbufdbl_bo_test_env=>create(
               environment_config = cl_botd_txbufdbl_bo_test_env=>prepare_environment_config(
                 )->set_bdef_dependencies( bdef_dependencies = VALUE #( ( 'ZRAP_R_ORDER_U_###' ) ) ) ).
  ENDMETHOD.

  METHOD class_teardown.
    go_env->destroy( ).
  ENDMETHOD.

  METHOD setup.
    go_env->clear_doubles( ).
    mo_double = go_env->get_test_double( 'ZRAP_R_ORDER_U_###' ).
    mo_cut    = NEW #( ).
  ENDMETHOD.

  METHOD sums_only_open_orders.
    DATA lt_orders TYPE TABLE FOR CREATE zrap_r_order_u_###\\order.

    lt_orders = VALUE #( %control = VALUE #( OrderID      = if_abap_behv=>mk-on
                                             Status       = if_abap_behv=>mk-on
                                             TotalAmount  = if_abap_behv=>mk-on
                                             CurrencyCode = if_abap_behv=>mk-on )
                         ( %cid = 'O1' OrderID = '0000000001' Status = 'N' TotalAmount = '100.00' CurrencyCode = 'EUR' )
                         ( %cid = 'O2' OrderID = '0000000002' Status = 'N' TotalAmount = '50.00'  CurrencyCode = 'EUR' )
                         ( %cid = 'O3' OrderID = '0000000003' Status = 'A' TotalAmount = '999.00' CurrencyCode = 'EUR' ) ).
    mo_double->insert_test_data( instances = lt_orders ).

    DATA(ls_summary) = mo_cut->summarize_open( VALUE #( ( OrderID = '0000000001' )
                                                         ( OrderID = '0000000002' )
                                                         ( OrderID = '0000000003' ) ) ).

    cl_abap_unit_assert=>assert_equals( act = ls_summary-open_count    exp = 2 ).
    cl_abap_unit_assert=>assert_equals( act = ls_summary-open_amount   exp = '150.00' ).
    cl_abap_unit_assert=>assert_equals( act = ls_summary-currency_code exp = 'EUR' ).
    cl_abap_unit_assert=>assert_false( ls_summary-mixed_currency ).
    cl_abap_unit_assert=>assert_equals( act = ls_summary-not_found     exp = 0 ).
  ENDMETHOD.

  METHOD counts_unknown_keys.
    DATA lt_orders TYPE TABLE FOR CREATE zrap_r_order_u_###\\order.

    lt_orders = VALUE #( %control = VALUE #( OrderID      = if_abap_behv=>mk-on
                                             Status       = if_abap_behv=>mk-on
                                             TotalAmount  = if_abap_behv=>mk-on
                                             CurrencyCode = if_abap_behv=>mk-on )
                         ( %cid = 'O1' OrderID = '0000000001' Status = 'N' TotalAmount = '10.00' CurrencyCode = 'EUR' ) ).
    mo_double->insert_test_data( instances = lt_orders ).

    DATA(ls_summary) = mo_cut->summarize_open( VALUE #( ( OrderID = '0000000001' )
                                                         ( OrderID = '0000000099' ) ) ).

    cl_abap_unit_assert=>assert_equals( act = ls_summary-open_count exp = 1 ).
    cl_abap_unit_assert=>assert_equals( act = ls_summary-not_found  exp = 1 ).
  ENDMETHOD.

  METHOD mixed_currency_no_sum.
    DATA lt_orders TYPE TABLE FOR CREATE zrap_r_order_u_###\\order.

    lt_orders = VALUE #( %control = VALUE #( OrderID      = if_abap_behv=>mk-on
                                             Status       = if_abap_behv=>mk-on
                                             TotalAmount  = if_abap_behv=>mk-on
                                             CurrencyCode = if_abap_behv=>mk-on )
                         ( %cid = 'O1' OrderID = '0000000001' Status = 'N' TotalAmount = '100.00' CurrencyCode = 'EUR' )
                         ( %cid = 'O2' OrderID = '0000000002' Status = 'N' TotalAmount = '100.00' CurrencyCode = 'USD' ) ).
    mo_double->insert_test_data( instances = lt_orders ).

    DATA(ls_summary) = mo_cut->summarize_open( VALUE #( ( OrderID = '0000000001' )
                                                         ( OrderID = '0000000002' ) ) ).

    cl_abap_unit_assert=>assert_equals( act = ls_summary-open_count exp = 2 ).
    cl_abap_unit_assert=>assert_true( ls_summary-mixed_currency ).
    cl_abap_unit_assert=>assert_initial( ls_summary-open_amount ).
  ENDMETHOD.

ENDCLASS.
```

왜 이렇게 쓰나

- **무엇을 테스트하나**: 이 테스트의 대상(CUT)은 BO가 아니라 **BO를 쓰는 코드**입니다. BO가 어떻게 구현되었는지(unmanaged, 레거시, 번호 범위, 잠금)는 소비자와 상관이 없어야 합니다. `cl_botd_txbufdbl_bo_test_env`는 지정한 BDEF의 EML을 프레임워크 안의 **트랜잭션 버퍼 대역**으로 돌려, 우리 핸들러·세이버·레거시를 전혀 부르지 않습니다. 그래서 "확인"에서 `lhc_order->read` 브레이크포인트가 멈추지 않습니다.
- **데이터를 넣는 두 가지 방법**: (1) 테스트 안에서 `MODIFY ENTITIES ... CREATE`를 실행해 대역 버퍼에 기록하거나, (2) `insert_test_data( instances = ... )`로 바로 넣습니다. 이 BO는 `OrderID`, `Status`, `TotalAmount`가 읽기 전용이고 키가 late numbering이라 (1)로는 원하는 상태의 주문을 만들기 어렵습니다. 그래서 ABAP 치트시트 "ABAP Unit Tests"의 트랜잭션 버퍼 대역 예처럼 (2)를 씁니다. 공식 `/DMO/TC_BOTD_TRAVEL_M_DEMOS`의 주석은 `insert_test_data`를 "create가 internal일 때" 쓰는 API로 설명하므로, 읽기 전용 필드와 late numbering 키를 이렇게 넣을 수 있는지는 실제 시스템에서 확인 필요합니다. 막히면 같은 공식 데모처럼 `mo_double->configure_additional_behavior( )->set_fields_handler( fields_handler = NEW ltd_fields_handler( ) )`로 `if_botd_bufdbl_fields_handler`를 구현한 로컬 클래스를 등록해, CREATE 때 읽기 전용 필드(`OrderID` 등)를 채우는 방법을 쓰세요.
- **세 가지 테스트 도구 비교**

| 도구 | 바꾸는 것 | 쓰는 곳 |
|---|---|---|
| 가짜 클래스 / `cl_abap_testdouble` | 인터페이스 하나(`ZIF_LEG_ORDER_###`) | 행동 풀 단위 테스트 (10·11단계) |
| `cl_osql_test_environment` | Open SQL이 접근하는 테이블 | 레거시·통합 테스트 (R-05 12단계, 11단계) |
| `cl_botd_txbufdbl_bo_test_env` | BO 하나 전체(EML) | BO 소비자 테스트 (이 단계) |

- `TABLE FOR CREATE`에서 줄 앞에 `%control = VALUE #( ... )`를 한 번만 쓰면 모든 줄에 같은 값이 들어갑니다(`VALUE` 연산자의 공통 값 문법, 치트시트 예와 같음).
- 같은 목적의 다른 변형으로 `cl_botd_mockemlapi_bo_test_env`(EML 호출마다 입력/출력을 직접 정하는 방식)도 있습니다(공식 `/DMO/TC_BOTD_TRAVEL_M_DEMOS`). 결과를 버퍼가 알아서 만들어 주는 txbufdbl 쪽이 보통 더 간단합니다.

R-07 전체: 자주 나는 오류와 해결

| 증상 | 원인 | 해결 |
|---|---|---|
| draft 테이블 활성화 오류 "`%admin` ... unknown" | `"%admin" : include sych_bdl_draft_admin_inc;` 줄이 없거나 오타 | BDEF의 `draft table` 퀵픽스로 테이블을 생성하게 하고 필드 표와 비교 (1단계) |
| 활성화 오류 "Early numbering requires ... FOR NUMBERING" | BDEF에 `early numbering`을 썼지만 행동 풀에 numbering 메서드가 없음 | `earlynumbering_create`, `earlynumbering_cba_Items` 구현 (5단계) |
| Create 직후 키가 비어 있음 | numbering 메서드가 이미 키가 있는 줄을 덮어쓰거나, `%is_draft`를 mapped에 넣지 않음 | 키가 있는 줄은 그대로 돌려주고, `%cid`·`%is_draft`·키를 모두 mapped에 (5단계) |
| Activate 때 `ASSERTION_FAILED` | active 핸들러가 draft 인스턴스를 받음 (전제와 다름) | 호출 스택 확인 후 draft 인스턴스는 `CONTINUE` (6·8단계) |
| Activate 때 레거시 005 "already exists" | MAX+1 번호로 두 draft가 같은 번호를 받음 | 번호 범위 방식 사용 (R-05 7단계) |
| validation 메시지가 화면에서 사라지지 않음 | `%state_area`를 비우는 줄(메시지 없이 `%state_area`만)이 없음 | validation 시작 시 상태 영역을 비우는 줄 추가 (7단계) |
| 품목 메시지가 품목 표에 붙지 않음 | `%path`에 부모 키가 없음 | `%path-order-%is_draft`, `%path-order-OrderID` 채우기 (7단계) |
| "Access to private component ..." (테스트) | `FRIENDS` 또는 `DEFINITION DEFERRED` 누락 | 9단계 |
| 단위 테스트가 실제 DB/잠금을 건드림 | `go_double` 미설정, 또는 이전 테스트가 비우지 않음 | `setup`/`teardown` 확인 (10단계) |
| 통합 테스트의 결과가 실행 순서에 따라 다름 | 레거시 싱글턴 버퍼가 남음 | `teardown`에서 `ROLLBACK ENTITIES` (11단계) |
| txbufdbl 테스트에서 "BDEF not found" | `set_bdef_dependencies`, `get_test_double`에 소문자/별칭 사용 | 루트 엔터티 이름을 대문자로 (`'ZRAP_R_ORDER_U_###'`) |
| txbufdbl 테스트에서 `insert_test_data`가 읽기 전용 키를 거부 | late numbering/읽기 전용 필드 제한 (확인 필요) | `set_fields_handler`로 CREATE 때 키 부여 (이 단계 해설) |

클래스 구조 해설 (R-07에서 만든 테스트 전체)

| 테스트 클래스 | 위치 | 대상 | 대역 | 확인하는 계약 |
|---|---|---|---|---|
| `ltc_handler` | R-06 행동 풀 Test Classes | `lhc_order`, `lhc_item` | `ltd_legacy`, `cl_abap_testdouble` | 레거시 결과 ↔ mapped/failed/reported, %control ↔ X 구조 |
| `ltc_saver` | R-06 행동 풀 Test Classes | `lsc_zrap_r_order_u_###` | `ltd_legacy` | LATE 응답, `%tmp` 매핑, 위임 |
| `ltc_integration` | R-06 행동 풀 Test Classes | BO 전체 (EML) | `cl_osql_test_environment` | 저장 순서, 임시 → 최종 번호, 저장 거부 |
| `ltc_order_stats` | `ZCL_RAP_ORDER_STATS_###` Test Classes | 소비자 클래스 | `cl_botd_txbufdbl_bo_test_env` | BO 구현과 무관한 소비자 로직 |

</details>

## 출처

이 단원을 쓰면서 실제로 읽은 자료입니다.

- SAP-samples/abap-platform-refscen-flight (브랜치 ABAP-platform-cloud)
  - unmanaged 예제 폴더: https://github.com/SAP-samples/abap-platform-refscen-flight/tree/ABAP-platform-cloud/src/unmanaged
  - https://github.com/SAP-samples/abap-platform-refscen-flight/blob/ABAP-platform-cloud/src/unmanaged/%23dmo%23bp_travel_u.clas.locals_imp.abap
  - https://github.com/SAP-samples/abap-platform-refscen-flight/blob/ABAP-platform-cloud/src/unmanaged/%23dmo%23bp_travel_u.clas.testclasses.abap
  - https://github.com/SAP-samples/abap-platform-refscen-flight/blob/ABAP-platform-cloud/src/unmanaged/%23dmo%23bp_booking_u.clas.locals_imp.abap
  - https://github.com/SAP-samples/abap-platform-refscen-flight/blob/ABAP-platform-cloud/src/unmanaged/%23dmo%23cl_travel_auxiliary.clas.abap
  - https://github.com/SAP-samples/abap-platform-refscen-flight/blob/ABAP-platform-cloud/src/unmanaged/%23dmo%23c_travel_u.bdef.asbdef
  - 레거시 폴더(`/DMO/CL_FLIGHT_LEGACY`, `/DMO/IF_FLIGHT_LEGACY`, `/DMO/ETRAVEL`, `/DMO/S_TRAVEL_INX`): https://github.com/SAP-samples/abap-platform-refscen-flight/tree/ABAP-platform-cloud/src/legacy
  - managed 폴더(`/DMO/BP_TRAVEL_M`, `/DMO/I_TRAVEL_M` BDEF, `/DMO/TC_BOTD_TRAVEL_M_DEMOS`, `/DMO/TC_TRAVEL_M_BO_CONSUMER`): https://github.com/SAP-samples/abap-platform-refscen-flight/tree/ABAP-platform-cloud/src/managed
  - https://github.com/SAP-samples/abap-platform-refscen-flight/blob/ABAP-platform-cloud/src/managed/%23dmo%23tc_botd_travel_m_demos.clas.testclasses.abap
  - https://github.com/SAP-samples/abap-platform-refscen-flight/blob/ABAP-platform-cloud/src/managed/%23dmo%23tc_botd_travel_m_demos.clas.locals_imp.abap
  - draft 폴더(`/DMO/R_TRAVEL_D` BDEF, `/DMO/BP_TRAVEL_D`, `/DMO/BP_BOOKING_D`, `/DMO/C_TRAVEL_A_D` BDEF, draft 테이블): https://github.com/SAP-samples/abap-platform-refscen-flight/tree/ABAP-platform-cloud/src/draft
  - 재사용 폴더(`/DMO/I_Agency`, `/DMO/I_Agency_StdVH`, `/DMO/I_Supplement`, `/DMO/I_Supplement_StdVH`): https://github.com/SAP-samples/abap-platform-refscen-flight/tree/ABAP-platform-cloud/src/reuse
- SAP-samples/abap-cheat-sheets
  - https://github.com/SAP-samples/abap-cheat-sheets/blob/main/08_EML_ABAP_for_RAP.md
  - https://github.com/SAP-samples/abap-cheat-sheets/blob/main/14_ABAP_Unit_Tests.md
  - https://github.com/SAP-samples/abap-cheat-sheets/blob/main/36_RAP_Behavior_Definition_Language.md
  - https://github.com/SAP-samples/abap-cheat-sheets/blob/main/src/zbp_demo_abap_rap_ro_u.clas.locals_imp.abap
- SAP-samples/abap-platform-rap-workshops
  - rap400 연습 2~4 (특히 연습 3의 EML 테스트 클래스 `EX3_CLAS_ZRAP400_TC_TRAVEL_EML`): https://github.com/SAP-samples/abap-platform-rap-workshops/tree/main/rap4xx/rap400/exercises
  - rap610 연습: https://github.com/SAP-samples/abap-platform-rap-workshops/tree/main/rap6xx/rap610
  - rap620 연습: https://github.com/SAP-samples/abap-platform-rap-workshops/tree/main/rap6xx/rap620
- SAP-samples/abap-platform-rap-opensap
  - 3주차 6단원 메시지 예외 클래스 `ZCM_RAP`: https://github.com/SAP-samples/abap-platform-rap-opensap/blob/main/week3/sources/W3U6_CLAS_ZCM_RAP.txt

