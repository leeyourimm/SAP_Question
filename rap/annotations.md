## 0. 한눈에 보기
이 탭은 문제 R-01 ~ R-13에서 직접 붙여 보는 CDS 어노테이션을 "무엇을 하려면 어떤 어노테이션을 어디에 붙이나" 기준으로 정리한 사전입니다. 문제 해설에 `(→ 어노테이션 탭: @UI.lineItem)`처럼 나오면 여기서 해당 항목을 찾아보세요.
표기: **(소스 예제에서는 확인 못 함)** 은 로컬에 받아 둔 SAP 샘플 코드에서는 보지 못했지만 존재한다고 판단한 것, **(GitHub 공개 코드에서만 확인)** 은 SAP 공식 샘플 이외의 공개 저장소에서 쓰임을 확인한 것입니다. 실제 SAP 시스템에서 직접 실행해 보지는 못했으므로, 표시된 항목은 ADT 코드 완성(Ctrl+Space)으로 이름과 값을 한 번 더 확인하세요.

**RAP 계층별로 어노테이션이 놓이는 자리**

| 객체 | 예 (이 문제집 이름) | 주로 붙이는 어노테이션 | 이유 |
|---|---|---|---|
| 데이터베이스 테이블 | `ZRAP_ATRAV_###` | `@EndUserText.label`, `@AbapCatalog.*`, 금액 필드의 `@Semantics.amount.currencyCode : 'tab.field'` | 테이블 기술 속성(전송, 확장, 유지보수)과 금액-통화 참조 |
| R 뷰(기본 BO 뷰, root view entity) | `ZRAP_R_TRAVEL_###` | `@AccessControl.authorizationCheck`, `@Metadata.allowExtensions`, `@Semantics.*`(관리 필드, 금액, LOB), `@ObjectModel.sapObjectNodeType.name`, `@AbapCatalog.extensibility` | "데이터의 의미"는 모델 가장 아래에 한 번만 정의하고 위로 전파시킴 |
| C 뷰(프로젝션, transactional_query) | `ZRAP_C_TRAVEL_###` | `@Search.*`, `@Consumption.valueHelpDefinition`, `@ObjectModel.text.element`, `@ObjectModel.semanticKey`, `@ObjectModel.virtualElementCalculatedBy`, `@Metadata.allowExtensions` | 이 서비스(앱)에서만 필요한 검색·값 도움말·텍스트 |
| I 뷰(인터페이스, transactional_interface) | `ZRAP_I_TRAVEL_###` | `@Metadata.ignorePropagatedAnnotations: true`, `@AccessControl.authorizationCheck` | 다른 BO나 확장이 쓰는 안정된 계약, UI 관련은 두지 않음 |
| MDE(메타데이터 확장) | `ZRAP_C_TRAVEL_###` (DDLX) | `@Metadata.layer`, `@UI.*` 전부, `@EndUserText.label`, 일부 `@Consumption.*` | 화면 배치를 데이터 모델과 분리해 따로 바꾸고 전송 |
| 추상 엔터티 | `ZRAP_A_DISCOUNT_###` | `@EndUserText.label`, 파라미터의 `@Consumption.valueHelpDefinition`, `@UI.defaultValue` | 액션 파라미터 팝업, 이벤트 페이로드 |
| 커스텀 엔터티 | R-08 | `@ObjectModel.query.implementedBy` | 데이터를 ABAP 클래스가 직접 만들어 줌 |
| DCL(접근 제어) | `ZRAP_R_TRAVEL_###` (DCLS) | `@EndUserText.label`, `@MappingRole: true` | 역할 정의 자체의 속성 |
| SRVD(서비스 정의) | `ZRAP_UI_TRAVEL_###` | `@EndUserText.label`, `@ObjectModel.leadingEntity.name` | 서비스 설명, 미리보기 시작 엔터티 |
| BDEF | `ZRAP_R_TRAVEL_###` | **어노테이션 없음** (키워드와 `##` 프라그마만) | 동작은 어노테이션이 아니라 BDL 문법으로 정의 |

**하고 싶은 일 → 쓸 어노테이션 → 어느 객체에**

| 하고 싶은 일 | 쓸 어노테이션 | 어느 객체에 |
|---|---|---|
| 목록(List Report)에 열 보이기 | `@UI.lineItem` | MDE 요소 |
| 열 순서·폭·중요도 정하기 | `@UI.lineItem: [{ position, importance, cssDefault.width }]` | MDE 요소 |
| 필터 바에 처음부터 필터 필드 보이기 | `@UI.selectionField` | MDE 요소 |
| 필터 기본값 넣기 | `@Consumption.filter.defaultValue` | MDE 또는 C 뷰 요소 |
| 필터 목록에서 아예 빼기 | `@Consumption.filter.hidden` | MDE 또는 C 뷰 요소 |
| 화면에서만 필드 숨기기(OData에는 남김) | `@UI.hidden` | MDE 요소 |
| OData에서 필드 자체를 빼기 | `@Consumption.hidden` | C 뷰 요소 |
| 기본 정렬·그룹 지정 | `@UI.presentationVariant` | MDE 헤더 |
| 미리 정의된 조건의 보기(탭) 만들기 | `@UI.selectionVariant` + `@UI.selectionPresentationVariant` | MDE 헤더 |
| 목록 제목·객체 페이지 제목 | `@UI.headerInfo` | MDE 헤더 |
| 객체 페이지에 섹션 만들기 | `@UI.facet` | MDE (보통 첫 요소 위) |
| 객체 페이지 "일반 정보" 폼 | `@UI.identification` + facet `#IDENTIFICATION_REFERENCE` | MDE 요소 |
| 폼을 여러 묶음으로 나누기 | `@UI.fieldGroup` + facet `#FIELDGROUP_REFERENCE` | MDE 요소 |
| 자식(Booking) 표를 객체 페이지에 | facet `#LINEITEM_REFERENCE` + 자식 MDE의 `@UI.lineItem` | 부모 MDE + 자식 MDE |
| 헤더에 KPI 숫자·별점·진행 막대 | `@UI.dataPoint` + facet `#DATAPOINT_REFERENCE` | MDE 요소 |
| 액션 버튼(목록 툴바) | `@UI.lineItem: [{ type: #FOR_ACTION, dataAction }]` | MDE 요소 |
| 액션 버튼(객체 페이지 헤더) | `@UI.identification: [{ type: #FOR_ACTION }]` | MDE 요소 |
| 액션 버튼(객체 페이지 아래 바닥) | `@UI.identification: [{ determining: true }]` | MDE 요소 |
| 복사 버튼 | `isCopyAction: true` (lineItem/identification) | MDE 요소 |
| 수정·삭제 버튼 숨기기 | `@UI.updateHidden`, `@UI.deleteHidden` | MDE 헤더 |
| 상태를 색(빨강/노랑/초록)으로 | `criticality` 속성 (lineItem/identification/dataPoint) | MDE 요소 + 가상 요소/계산 필드 |
| ID 대신 이름 보이기 | `@ObjectModel.text.element` + `@UI.textArrangement` | C 뷰 요소 (+ MDE) |
| 언어별 텍스트 연결 | `@ObjectModel.text.association` + 텍스트 뷰의 `@Semantics.text`, `@Semantics.language` | 값 도움말 뷰 |
| 값 도움말(F4) 붙이기 | `@Consumption.valueHelpDefinition` | C 뷰 요소 (또는 MDE) |
| 값 도움말을 드롭다운으로 | `@ObjectModel.resultSet.sizeCategory: #XS` | 값 도움말 뷰 헤더 |
| 값 도움말로 입력값 검증 | `useForValidation: true` | C 뷰 요소 |
| 값 고르면 다른 필드도 채우기 | `additionalBinding: [{ usage: #RESULT }]` | C 뷰 요소 |
| 검색창 켜기 | `@Search.searchable` + `@Search.defaultSearchElement` | C 뷰 헤더 + 요소 |
| 오타 허용 검색 | `@Search.fuzzinessThreshold` | C 뷰 요소 |
| 금액 옆에 통화 | `@Semantics.amount.currencyCode` | 테이블 필드, R 뷰 요소 |
| 수량 옆에 단위 | `@Semantics.quantity.unitOfMeasure` | 테이블 필드, R 뷰 요소 |
| 생성자·변경 시각 자동 채우기, ETag | `@Semantics.user.*`, `@Semantics.systemDateTime.*` | R 뷰 요소 |
| 첨부 파일 업로드·다운로드 | `@Semantics.largeObject` + `@Semantics.mimeType` | R 뷰 요소 |
| 메일·전화 링크 | `@Semantics.eMail.address`, `@Semantics.telephone.type` | R 또는 I 뷰 요소 |
| 굵은 글씨 키·편집 상태 표시 | `@ObjectModel.semanticKey` | C 뷰 헤더 |
| DB에 없는 계산 필드 | `@ObjectModel.virtualElementCalculatedBy` | C 뷰 `virtual` 요소 |
| ABAP 클래스로 읽는 엔터티 | `@ObjectModel.query.implementedBy` | 커스텀 엔터티 헤더 |
| 권한 검사 켜기 | `@AccessControl.authorizationCheck` | 모든 CDS 뷰 헤더 |
| MDE로 UI 붙이도록 허용 | `@Metadata.allowExtensions: true` | C 뷰 헤더 |
| 아래 뷰의 어노테이션 무시 | `@Metadata.ignorePropagatedAnnotations` | 뷰 헤더 |
| MDE 레이어 지정 | `@Metadata.layer` | MDE 헤더 |
| 고객 필드 확장 허용 | `@AbapCatalog.extensibility.*` | R/C/I/확장 포함 뷰 헤더 |
| 테이블에 확장 필드 허용 | `@AbapCatalog.enhancement.category`, `.fieldSuffix`, `.quotaMaximumFields` | 테이블 |
| 트리(계층) 표 | `@OData.hierarchy.recursiveHierarchy` | C 뷰 헤더 |
| 미리보기 시작 엔터티 표시 | `@ObjectModel.leadingEntity.name` | SRVD |
| 액션 파라미터 기본값 | `@UI.defaultValue` | 추상 엔터티 요소 |
| 이벤트·SAP 객체 노드 유형 이름 | `@ObjectModel.sapObjectNodeType.name` | R 뷰 헤더 |
| 테스트 클래스와 BDEF 연결 | ABAP Doc `"! @testing BDEF:...` | 테스트 클래스 정의 위 (어노테이션 아님) |

## 1. 어노테이션 기본
어노테이션은 CDS 소스에 붙이는 "메타데이터 꼬리표"입니다. 데이터베이스 결과는 바꾸지 않고, 그것을 읽는 쪽(ABAP 런타임, RAP 프레임워크, OData 노출 계층, Fiori Elements)이 해석합니다.
이 그룹은 문법, 전파(상속), MDE 레이어, 그리고 어떤 어노테이션이 OData `$metadata`까지 나가는지를 다룹니다. 다른 그룹을 읽기 전에 먼저 보세요.

### 어노테이션 문법 (헤더 · 요소 · 배열 · 구조)
**하는 일** 어노테이션을 어디에, 어떤 모양으로 쓰는지 정하는 기본 규칙입니다. 헤더 어노테이션은 `define ...` 앞에, 요소 어노테이션은 해당 필드 바로 앞에 씁니다.
**붙이는 곳** 테이블 / 뷰 엔터티 헤더 / 요소 / 프로젝션 / MDE / 파라미터 / 커스텀 엔터티 / 추상 엔터티 / SRVD
**값**

| 모양 | 의미 |
|---|---|
| `@A.b.c: 값` | 점 표기. 가장 흔한 형태 |
| `@A: { b: 값, c: 값 }` | 같은 이름공간을 중괄호로 묶은 구조 표기. 점 표기와 결과 동일 |
| `@A.b: [ {...}, {...} ]` | 배열. `@UI.lineItem`, `@UI.facet`처럼 여러 개를 가질 수 있는 것 |
| `'문자열'` / `숫자` / `true`·`false` / `#ENUM` | 값 종류. 열거값은 반드시 `#`를 붙이고 따옴표 없이 씀 |
| `#( 요소명 )` | 상수 대신 다른 요소 값을 참조 (예: `hidden: #(IsActiveEntity)`) |
| `@<A.b: 값` | 요소 **뒤**에 붙이는 형식 (DDIC 기반 뷰 시절 문법) |

**예시**
```cds
@EndUserText.label: 'Travel'                        // 헤더, 점 표기
@ObjectModel.usageType: { serviceQuality: #X,      // 헤더, 구조 표기
                          sizeCategory:   #S,
                          dataClass:      #MIXED }
define root view entity ZRAP_R_TRAVEL_###
  as select from zrap_atrav_###
{
  key travel_id as TravelID,
      @Semantics.amount.currencyCode: 'CurrencyCode' // 요소 어노테이션
      total_price as TotalPrice,
      currency_code as CurrencyCode
}
```
**결과** 문법 자체는 화면을 바꾸지 않습니다. 같은 어노테이션을 점 표기와 구조 표기로 섞어 써도 되지만, 한 요소에서 같은 속성을 두 번 정의하면 활성화 오류가 납니다.
**자주 하는 실수**
- 열거값에 따옴표를 붙임: `'#CHECK'`는 7.54(클라우드 기준 이전 릴리스)부터 더 이상 허용되지 않습니다. `#CHECK`처럼 쓰세요.
- 배열이어야 하는 어노테이션(`@UI.lineItem`)을 `{ }` 하나로만 씀. 대부분 받아 주지만, 여러 개를 넣을 때는 `[ ]`가 필요합니다.
- 필드 이름을 가리키는 값(`'CurrencyCode'`)에 DB 컬럼명(`currency_code`)을 씀. 뷰에서는 **별칭(alias)** 을 가리켜야 합니다.
**쓰는 문제** R-01 ~ R-13 전부

### 전파 (propagation, 어노테이션 상속)
**하는 일** 아래 계층(데이터 엘리먼트, 테이블 필드, 기본 뷰)의 **요소 어노테이션**이 그 필드를 그대로 가져오는 위 뷰(R → C)로 자동으로 따라 올라가는 것입니다. 데이터 엘리먼트의 필드 라벨도 이렇게 올라가서 `@EndUserText.label` 역할을 합니다.
**붙이는 곳** 요소 (헤더 어노테이션은 전파되지 않음)
**값**

| 상황 | 결과 |
|---|---|
| 위 뷰에 같은 어노테이션이 없음 | 아래 것이 그대로 적용 |
| 위 뷰에 같은 어노테이션을 다시 씀 | 위 것이 덮어씀 |
| 위 뷰 헤더에 `@Metadata.ignorePropagatedAnnotations: true` | 아래에서 올라오는 요소 어노테이션을 모두 무시 |
| 요소에 `null` 값 지정 (예: `@EndUserText.label: null`) | 배열이 아닌 요소 어노테이션은 `null`로 지정해 무효화 가능 |

**예시**
```cds
// R 뷰
@Semantics.amount.currencyCode: 'CurrencyCode'
total_price as TotalPrice,

// C 뷰 (projection) : 아무것도 안 써도 위 어노테이션이 따라 옴
define root view entity ZRAP_C_TRAVEL_###
  provider contract transactional_query
  as projection on ZRAP_R_TRAVEL_###
{
  key TravelID,
      TotalPrice,      // currencyCode 참조가 전파됨
      CurrencyCode
}
```
**결과** 실제로 어떤 값이 적용됐는지는 ADT에서 엔터티를 열고 **Active Annotations** 뷰(마우스 오른쪽 → Open With → Active Annotations)로 확인할 수 있습니다. 어디서 온 값인지(Origin)도 보여 줍니다.
**자주 하는 실수**
- 헤더 어노테이션(`@Search.searchable`, `@UI.headerInfo` 등)도 전파된다고 생각함. 헤더는 각 뷰에서 다시 써야 합니다.
- R 뷰에 `@Metadata.ignorePropagatedAnnotations: true`를 써서 데이터 엘리먼트 라벨까지 사라져 Fiori 열 제목이 필드명으로 나옴.
**쓰는 문제** R-01, R-03

### @Metadata.layer
**하는 일** MDE(메타데이터 확장)가 어느 레이어에 속하는지 정합니다. 같은 엔터티에 MDE가 여러 개 있으면 레이어가 높은 쪽 값이 이깁니다.
**붙이는 곳** MDE 헤더 (MDE에는 필수)
**값**

| 값 | 의미 (우선순위 낮음 → 높음) |
|---|---|
| `#CORE` | 원래 개발자(SAP 표준 또는 앱 개발자)의 기본 레이어 |
| `#LOCALIZATION` | 국가별 현지화 |
| `#INDUSTRY` | 산업별 솔루션 |
| `#PARTNER` | 파트너 |
| `#CUSTOMER` | 고객. 가장 높음 |

적용 순서: **MDE(CUSTOMER > PARTNER > INDUSTRY > LOCALIZATION > CORE) > 엔터티 자신의 DDL 소스 > 아래에서 전파된 값**. 같은 레이어에 MDE가 두 개 이상이면 어느 것이 이길지 정해져 있지 않으므로 피하세요.
**예시**
```cds
@Metadata.layer: #CORE
@UI.headerInfo: { typeName: 'Travel', typeNamePlural: 'Travels' }
annotate entity ZRAP_C_TRAVEL_### with
{
  @UI.lineItem: [{ position: 10 }]
  TravelID;
}
```
**결과** R-10에서 `#CUSTOMER` 레이어 MDE를 하나 더 만들어 `@UI.lineItem.label`만 바꾸면, `#CORE` MDE를 고치지 않아도 목록 열 제목이 바뀝니다.
**자주 하는 실수**
- MDE를 만들었는데 대상 뷰에 `@Metadata.allowExtensions: true`가 없어 활성화 오류.
- 레이어 값 중 `#CORE`, `#CUSTOMER`만 소스 예제에서 확인했고 나머지 세 값은 ABAP 릴리스 노트의 레이어 이름(core, localization, industry, partner, customer)으로 확인했습니다. 코드 완성으로 철자를 확인하세요.
**쓰는 문제** R-01, R-05, R-10

### @Metadata.allowExtensions
**하는 일** 이 엔터티에 MDE(`annotate entity ... with`)를 붙여도 된다고 허락합니다.
**붙이는 곳** 뷰 엔터티 헤더 / 프로젝션 / 커스텀 엔터티
**값**

| 값 | 의미 |
|---|---|
| `true` | MDE 허용 |
| `false` 또는 생략 | MDE 불가 |

**예시**
```cds
@AccessControl.authorizationCheck: #CHECK
@Metadata.allowExtensions: true
@EndUserText.label: 'Travel - Projection'
define root view entity ZRAP_C_TRAVEL_###
  provider contract transactional_query
  as projection on ZRAP_R_TRAVEL_###
{ ... }
```
**결과** 화면은 바뀌지 않습니다. MDE를 활성화할 수 있게 될 뿐입니다.
**자주 하는 실수**
- R 뷰에만 붙이고 MDE는 C 뷰 이름으로 만들어 오류. MDE를 붙이는 그 엔터티에 있어야 합니다.
- 고객 확장(R-10)에서 다른 개발자가 `#CUSTOMER` MDE를 붙이게 하려면 이 값이 꼭 `true`여야 합니다.
**쓰는 문제** R-01, R-05, R-10

### @Metadata.ignorePropagatedAnnotations
**하는 일** 아래 계층(데이터 소스, 데이터 엘리먼트)에서 전파되어 오는 요소 어노테이션을 무시하고, 이 뷰에 직접 쓴 것만 쓰겠다고 선언합니다.
**붙이는 곳** 뷰 엔터티 헤더 / 프로젝션
**값**

| 값 | 의미 |
|---|---|
| `true` | 전파된 어노테이션 무시 |
| `false`(기본) | 전파 허용 |

**예시**
```cds
@Metadata.ignorePropagatedAnnotations: true
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Travel - Interface'
define root view entity ZRAP_I_TRAVEL_###
  provider contract transactional_interface
  as projection on ZRAP_R_TRAVEL_###
{ ... }
```
**결과** 인터페이스 뷰는 다른 BO가 쓰는 계약이므로, R 뷰의 UI성 어노테이션이 섞여 들어가지 않게 할 때 씁니다. 값 도움말 뷰(`/DMO/I_Overall_Status_VH`)에도 자주 붙어 있습니다.
**자주 하는 실수**
- 붙인 뒤 `@Semantics.amount.currencyCode`까지 사라져 금액 필드에서 "참조 필드 없음" 오류가 남. 필요한 것은 다시 써야 합니다.
**쓰는 문제** R-03, R-08

### 어디까지 OData로 나가나 (어노테이션 → OData 어휘)
**하는 일** RAP 서비스 바인딩(OData V4)은 CDS 어노테이션 일부를 OData 어휘(vocabulary) 어노테이션으로 바꿔 `$metadata`에 내보냅니다. Fiori Elements는 이 `$metadata`만 보고 화면을 그립니다.
**붙이는 곳** (개념) 서비스에 노출된 엔터티의 모든 어노테이션
**값**

| CDS 어노테이션 | `$metadata`에 나오는 어휘(대표) |
|---|---|
| `@EndUserText.label` | `Common.Label` |
| `@EndUserText.quickInfo` | `Common.QuickInfo` |
| `@UI.lineItem` / `@UI.identification` / `@UI.fieldGroup` | `UI.LineItem` / `UI.Identification` / `UI.FieldGroup#qualifier` |
| `@UI.selectionField` | `UI.SelectionFields` |
| `@UI.headerInfo` | `UI.HeaderInfo` |
| `@UI.facet` | `UI.Facets` (purpose `#HEADER`는 `UI.HeaderFacets`) |
| `@UI.dataPoint` / `@UI.chart` | `UI.DataPoint#q` / `UI.Chart#q` |
| `@UI.presentationVariant` / `@UI.selectionVariant` | `UI.PresentationVariant` / `UI.SelectionVariant` |
| `@UI.hidden` | `UI.Hidden` |
| `@ObjectModel.text.element` + `@UI.textArrangement` | `Common.Text` + `UI.TextArrangement` |
| `@ObjectModel.semanticKey` | `Common.SemanticKey` |
| `@Consumption.valueHelpDefinition` | `Common.ValueList` (+ `useForValidation`이면 `Common.ValueListForValidation`) |
| `@ObjectModel.resultSet.sizeCategory: #XS` (값 도움말 쪽) | `Common.ValueListWithFixedValues` (드롭다운) |
| `@Semantics.amount.currencyCode` / `.quantity.unitOfMeasure` | `Measures.ISOCurrency` / `Measures.Unit` |
| `@Semantics.largeObject` / `@Semantics.mimeType` | `Edm.Stream` 속성 + `Core.MediaType`, `Core.ContentDisposition`, `Core.AcceptableMediaTypes` / `Core.IsMediaType` |
| `@Search.searchable` | 엔터티 집합의 검색 지원(`Capabilities.SearchRestrictions`) |
| BDEF `field ( readonly )` / `( mandatory )` | `Core.Computed` / `Common.FieldControl` (어노테이션이 아니라 BDEF에서 생성) |

**나가지 않는 것**: `@AbapCatalog.*`, `@AccessControl.*`, `@Metadata.*`, `@ObjectModel.usageType`, `@ObjectModel.query.implementedBy`, `@ObjectModel.virtualElementCalculatedBy`(값만 나감), `@ObjectModel.leadingEntity.name` 등은 ABAP 쪽에서만 쓰입니다.
**예시**
```cds
@UI.lineItem: [{ position: 10, importance: #HIGH }]
@EndUserText.label: 'Travel ID'
TravelID;
```
**결과** 서비스 바인딩 → URL 끝에 `/$metadata` 를 붙여 열면 `<Annotation Term="SAP__UI.LineItem">` 아래에 `TravelID` DataField가 보입니다. (SAP 서비스는 어휘 별칭을 `SAP__UI`, `SAP__common`, `SAP__core` 처럼 내보냅니다.)
**자주 하는 실수**
- MDE를 바꿨는데 화면이 그대로: 브라우저 캐시 때문입니다. 미리보기 탭을 새로 열거나 강력 새로고침 하세요.
- 위 표의 어휘 이름은 대표적인 결과만 적었습니다. 정확한 모양은 자신의 `$metadata`로 확인하세요(일부는 실제 시스템에서 확인 필요).
**쓰는 문제** R-01, R-02, R-05

## 2. 테이블·뷰 기술 어노테이션
테이블과 뷰의 "기술적 성격"(설명, 전송, 확장 가능 여부, 권한 검사, 데이터 양)을 정하는 어노테이션입니다. 화면에는 거의 영향이 없지만 빠지면 활성화 경고나 오류가 나는 것이 많습니다.
ADT의 테이블 생성 마법사와 "Define View Entity" 템플릿이 대부분 자동으로 넣어 주므로, 여기서는 각 값의 의미를 알고 바꿀 수 있게 하는 데 집중합니다.

### @EndUserText.label
**하는 일** 사람이 읽는 짧은 설명(라벨)을 줍니다. 헤더에 붙이면 객체 설명, 요소에 붙이면 필드 라벨(Fiori 열 제목·폼 라벨)이 됩니다.
**붙이는 곳** 테이블 / 뷰 엔터티 헤더 / 요소 / 프로젝션 / MDE / 파라미터 / 커스텀 엔터티 / 추상 엔터티 / SRVD / DCL
**값** 문자열 (최대 60자). 번역 대상 텍스트로 관리됩니다.
**예시**
```cds
@EndUserText.label: 'Travel data'                 // 헤더: 객체 설명
define root view entity ZRAP_R_TRAVEL_### ...
{
  @EndUserText.label: 'Overall Status Indicator'    // 요소: 필드 라벨
  virtual OverallStatusIndicator : abap.int2,
}
```
**결과** OData `Common.Label`로 나가 Fiori 열 제목과 폼 라벨이 바뀝니다. `@UI.lineItem.label`이 있으면 그쪽이 목록에서 우선합니다.
**자주 하는 실수**
- 데이터 엘리먼트에 이미 좋은 필드 라벨이 있는데 모든 필드에 다시 씀(번역 부담만 늘어남).
- 액션 파라미터(추상 엔터티)는 데이터 엘리먼트 라벨을 물려받으므로, `abap.int4` 같은 내장 타입일 때만 직접 쓰면 됩니다.
**쓰는 문제** R-01 ~ R-13 전부

### @EndUserText.quickInfo / @EndUserText.heading
**하는 일** `quickInfo`는 마우스를 올렸을 때 보이는 긴 설명(툴팁), `heading`은 열 머리글용 텍스트입니다.
**붙이는 곳** 요소 / MDE / CDS 단순 타입(`define type`)
**값** 문자열
**예시**
```cds
@EndUserText: { label: 'Airline',
                quickInfo: 'Airline that operates the flight' }
CarrierID;
```
**결과** OData `Common.QuickInfo`(`heading`은 `Common.Heading`)로 나가 툴팁으로 보입니다.
**자주 하는 실수**
- 피처 쇼케이스 소스에는 `quickinfo`(소문자 i)로 적힌 곳도 있습니다. CDS 어노테이션 이름은 대소문자를 구분하지 않지만, 코드 완성이 제안하는 `quickInfo`로 통일하세요.
**쓰는 문제** R-01

### @AbapCatalog.enhancement.category
**하는 일** 테이블(또는 DDIC 구조)을 나중에 append 등으로 확장할 수 있는지 정합니다.
**붙이는 곳** 테이블
**값**

| 값 | 의미 |
|---|---|
| `#NOT_EXTENSIBLE` | 확장 불가. 실습 테이블 기본값 |
| `#EXTENSIBLE_CHARACTER` | 문자형 필드만 추가 가능 |
| `#EXTENSIBLE_CHARACTER_NUMERIC` | 문자·숫자형 필드 추가 가능 |
| `#EXTENSIBLE_ANY` | 아무 타입이나 추가 가능 |
| `#NOT_CLASSIFIED` | 분류 안 함 (오래된 객체) |

(`#NOT_EXTENSIBLE` 외 값은 소스 예제에서는 확인 못 함)
**예시**
```cds
@EndUserText.label : 'Travel data'
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table zrap_atrav_### {
  key client    : abap.clnt not null;
  key travel_id : /dmo/travel_id not null;
  ...
}
```
**결과** 화면 변화 없음. 확장 필드 추가 가능 여부와 "확장 카테고리 없음" 경고에 영향.
**자주 하는 실수**
- 옛 소스(openSAP)에 보이는 `@AbapCatalog.enhancementCategory`(점 없음)는 예전 표기입니다. 현재 마법사는 `enhancement.category`를 만듭니다.
- R-10에서 테이블에 고객 필드를 허용하려면 `#NOT_EXTENSIBLE`을 바꾸고 아래 `fieldSuffix`/quota도 함께 정해야 합니다.
**쓰는 문제** R-01, R-05, R-10

### @AbapCatalog.tableCategory
**하는 일** 테이블 종류를 정합니다.
**붙이는 곳** 테이블
**값**

| 값 | 의미 |
|---|---|
| `#TRANSPARENT` | 일반 데이터베이스 테이블 (DB에 같은 이름의 테이블이 생김) |
| `#GLOBAL_TEMPORARY` | 전역 임시 테이블 (소스 예제에서는 확인 못 함) |

**예시** 위 `@AbapCatalog.enhancement.category` 예시 참고.
**결과** 화면 변화 없음.
**자주 하는 실수** 바꿀 일이 거의 없습니다. RAP 활성·draft 테이블 모두 `#TRANSPARENT`.
**쓰는 문제** R-01, R-04, R-05

### @AbapCatalog.deliveryClass
**하는 일** 전달 클래스: 설치·업그레이드·클라이언트 복사 때 테이블 **데이터**를 어떻게 다룰지 정합니다.
**붙이는 곳** 테이블
**값**

| 값 | 의미 |
|---|---|
| `#A` | 애플리케이션 테이블(마스터·트랜잭션 데이터). 실습 테이블 전부 |
| `#C` | 고객 설정(Customizing) 테이블 — R-09 같은 설정 데이터에 쓰는 경우가 있음 (소스 예제에서는 확인 못 함) |
| `#L` | 임시 데이터 (소스 예제에서는 확인 못 함) |

**예시** 위 테이블 예시 참고.
**결과** 화면 변화 없음.
**자주 하는 실수** draft 테이블은 ADT가 생성해 줄 때 값을 그대로 두세요. 설정 테이블을 `#C`로 바꾸면 전송 동작(Customizing 전송)이 달라지므로 트라이얼에서는 `#A`가 무난합니다.
**쓰는 문제** R-01, R-09

### @AbapCatalog.dataMaintenance
**하는 일** 도구(ADT Data Preview 등)로 테이블 내용을 보고 고칠 수 있는지를 정합니다.
**붙이는 곳** 테이블
**값**

| 값 | 의미 |
|---|---|
| `#RESTRICTED` | 표시는 되고 유지보수는 제한. 마법사 기본값 |
| `#ALLOWED` | 표시·유지보수 허용 (소스 예제에서는 확인 못 함) |
| `#NOT_ALLOWED` | 표시·유지보수 불가 (소스 예제에서는 확인 못 함) |

**예시** 위 테이블 예시 참고.
**결과** ADT Data Preview로 테이블 내용을 볼 수 있느냐에 영향. 화면(Fiori) 변화 없음.
**자주 하는 실수** 이 값을 바꾼다고 RAP 앱에서 수정 가능 여부가 바뀌지는 않습니다. RAP의 수정 가능 여부는 BDEF가 정합니다.
**쓰는 문제** R-01

### @AbapCatalog.enhancement.fieldSuffix / quotaMaximumFields / quotaMaximumBytes
**하는 일** 테이블을 "개발자 확장성(C0 릴리스)" 대상으로 만들 때 필요한 값: 고객이 추가하는 필드 이름에 붙일 접미사와, 추가할 수 있는 필드 수·바이트 한도입니다.
**붙이는 곳** 테이블
**값**

| 속성 | 의미 |
|---|---|
| `fieldSuffix` | 확장 필드 이름 접미사 (예: `'ZAG'`) |
| `quotaMaximumFields` | 추가 가능한 최대 필드 수 |
| `quotaMaximumBytes` | 추가 가능한 최대 바이트 수 |
| ~~`quotaShareCustomer` / `quotaSharePartner`~~ | 릴리스 노트상 **더 이상 사용 불가**. 쓰지 마세요 |

**예시** (소스 예제에서는 확인 못 함 — 이름은 ABAP 릴리스 노트에서 확인, 문법은 실제 시스템에서 확인 필요)
```cds
@EndUserText.label : 'Travel data'
@AbapCatalog.enhancement.category : #EXTENSIBLE_ANY
@AbapCatalog.enhancement.fieldSuffix : 'ZTR'
@AbapCatalog.enhancement.quotaMaximumFields : 100
@AbapCatalog.enhancement.quotaMaximumBytes : 10000
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table zrap_atrav_### { ... }
```
**결과** 화면 변화 없음. 테이블에 append(확장 구조)를 붙일 수 있게 됩니다.
**자주 하는 실수** 뷰 쪽 확장(`@AbapCatalog.extensibility`)만 켜고 테이블 쪽을 안 켜서 확장 필드를 저장할 곳이 없음.
**쓰는 문제** R-10

### @AbapCatalog.viewEnhancementCategory
**하는 일** 이 뷰를 `extend view entity`로 확장할 때 어떤 종류의 확장을 허용할지 정합니다.
**붙이는 곳** 뷰 엔터티 헤더
**값**

| 값 | 의미 |
|---|---|
| `[#NONE]` | 확장 금지 |
| `[#PROJECTION_LIST]` | SELECT 목록(필드)에 요소 추가 허용 |
| `[#GROUP_BY]` | 집계·GROUP BY가 있는 뷰의 확장 허용 (소스 예제에서는 확인 못 함) |
| `[#UNION]` | UNION이 있는 뷰의 확장 허용 (소스 예제에서는 확인 못 함) |

배열이므로 `[ ]`로 씁니다.
**예시**
```cds
@AbapCatalog.viewEnhancementCategory: [#PROJECTION_LIST]
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Travel - Extension Include View'
define view entity ZRAP_E_TRAVEL_###
  as select from zrap_atrav_### as Travel
{
  key travel_id as TravelID
}
```
**결과** 화면 변화 없음. `[#NONE]`이면 다른 개발자가 `extend view entity`를 활성화할 수 없습니다.
**자주 하는 실수** 값 도움말·기술용 뷰에는 `[#NONE]`을 붙여 두는 것이 SAP 샘플의 관례입니다. 확장을 받을 R-10 뷰에서 `[#NONE]`을 그대로 두면 확장이 막힙니다.
**쓰는 문제** R-10

### @AbapCatalog.extensibility (extensible, dataSources, elementSuffix, quota, allowNewDatasources, allowNewCompositions)
**하는 일** RAP BO의 CDS 뷰를 C0 확장 가능(고객이 필드·연관을 추가할 수 있게)으로 표시하고, 확장 범위를 제한합니다.
**붙이는 곳** 뷰 엔터티 헤더 / 프로젝션 (R, I, C 뷰와 확장 포함 뷰 모두)
**값**

| 속성 | 의미 |
|---|---|
| `extensible: true` | 이 뷰를 확장 가능으로 표시 |
| `dataSources: ['별칭']` | 확장 필드를 가져올 수 있는 데이터 소스(별칭 또는 연관) 목록 |
| `elementSuffix: 'ZAG'` | 확장 요소 이름 접미사 |
| `quota.maximumFields` / `quota.maximumBytes` | 추가 가능한 필드 수·바이트 한도 |
| `allowNewDatasources: false` | 확장에서 새 데이터 소스(조인/연관 대상) 추가 금지 |
| `allowNewCompositions: true` | 확장에서 새 컴포지션(자식 노드) 추가 허용 |

**예시** (`/DMO/R_AgencyTP` 참고)
```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Travel'
@AbapCatalog.extensibility: {
  extensible: true,
  elementSuffix: 'ZTR',
  allowNewDatasources: false,
  dataSources: ['_Extension'],
  quota: { maximumFields: 500, maximumBytes: 50000 },
  allowNewCompositions: true
}
define root view entity ZRAP_R_TRAVEL_### ...
```
**결과** 화면 변화 없음. ADT에서 이 뷰에 `extend view entity`를 만들 수 있게 되고, 범위를 벗어나는 확장은 오류가 납니다.
**자주 하는 실수**
- R 뷰에만 붙이고 C/I 뷰에는 안 붙임. 확장 필드를 끝까지(서비스까지) 내보내려면 경로상의 뷰마다 필요합니다.
- `dataSources`에 DB 테이블명을 씀. 뷰 안의 **별칭**(`Travel`) 또는 연관명(`_Extension`)을 써야 합니다.
**쓰는 문제** R-10

### @AccessControl.authorizationCheck
**하는 일** 이 CDS 엔터티를 ABAP SQL/RAP로 읽을 때 CDS 접근 제어(DCL)를 적용할지 정합니다.
**붙이는 곳** 뷰 엔터티 헤더 / 프로젝션 / 커스텀 엔터티 / 추상 엔터티(형식상) / 테이블 함수
**값**

| 값 | 의미 |
|---|---|
| `#CHECK` | DCL이 있으면 적용, 없으면 활성화 경고 |
| `#MANDATORY` | DCL이 반드시 있어야 함 (없으면 오류) |
| `#NOT_REQUIRED` | 접근 제어 불필요. DCL이 있으면 적용은 됨 |
| `#NOT_ALLOWED` | 접근 제어 금지. DCL이 있어도 무시 (릴리스 노트에서 확인) |

**예시**
```cds
@AccessControl.authorizationCheck: #CHECK
@EndUserText.label: 'Travel'
define root view entity ZRAP_R_TRAVEL_### ...
```
**결과** `#CHECK` + DCL이 있으면 Fiori 목록에 권한 있는 행만 나옵니다. OData 메타데이터에는 나가지 않습니다.
**자주 하는 실수**
- `#CHECK`로 두고 DCL을 안 만들어 "No access control" 경고를 계속 봄 → R-03에서 DCL을 만들어 해결.
- 값 도움말 뷰까지 `#CHECK`로 해서 값 목록이 비어 보임.
**쓰는 문제** R-01, R-03, R-05, R-08

### @MappingRole
**하는 일** DCL(접근 제어) 소스의 역할(`define role`)이 사용자에게 자동으로 매핑되는 역할임을 표시합니다. ADT 템플릿이 넣어 줍니다.
**붙이는 곳** DCL(`define role` 앞)
**값**

| 값 | 의미 |
|---|---|
| `true` | 모든 사용자에게 자동 적용되는 CDS 역할 |

**예시**
```cds
@EndUserText.label: 'Access control for ZRAP_R_TRAVEL_###'
@MappingRole: true
define role ZRAP_R_TRAVEL_### {
  grant select on ZRAP_R_TRAVEL_###
    where ( AgencyID ) = aspect pfcg_auth( ZRAPAGNCY, ZRAPAGNCY, ACTVT = '03' );
}
```
**결과** 화면 변화 없음. 이 역할 조건이 SELECT에 덧붙습니다.
**자주 하는 실수** 어노테이션을 지우면 역할이 적용되지 않습니다. 템플릿 값을 그대로 두세요. (예시의 권한 객체 이름은 R-03 문제 기준의 가상 이름)
**쓰는 문제** R-03

### @ClientHandling.type / @ClientHandling.algorithm (뷰 엔터티에는 쓰지 않음)
**하는 일** 클라이언트(MANDT) 처리를 정합니다. **CDS 뷰 엔터티는 클라이언트 처리를 자동으로** 하므로 이 어노테이션을 쓰지 않습니다. 쓰는 곳은 CDS 테이블 함수와 옛 DDIC 기반 뷰입니다.
**붙이는 곳** 테이블 함수 헤더 (뷰 엔터티 아님)
**값**

| 속성 | 값 | 의미 |
|---|---|---|
| `type` | `#CLIENT_DEPENDENT` | 클라이언트 종속 |
| `type` | `#CLIENT_INDEPENDENT` | 클라이언트 독립 |
| `algorithm` | `#SESSION_VARIABLE` | 세션 변수(`$session.client`)로 클라이언트 처리 |

**예시** (치트시트 `ZDEMO_ABAP_TABLE_FUNCTION`)
```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED
@ClientHandling.type: #CLIENT_DEPENDENT
@ClientHandling.algorithm: #SESSION_VARIABLE
define table function ZRAP_TF_DEMO_###
  returns { client : abap.clnt; carrier_id : abap.char(3); }
  implemented by method zcl_rap_tf_###=>read;
```
**결과** 화면 변화 없음.
**자주 하는 실수** 뷰 엔터티에 복사해 넣고 "허용되지 않는 어노테이션" 오류를 봄. RAP 실습의 뷰 엔터티에는 필요 없습니다.
**쓰는 문제** (참고용) R-08에서 테이블 함수를 고려할 때

### @Environment.systemField
**하는 일** CDS **파라미터**에 ABAP 시스템 값을 자동으로 넘기게 합니다. ABAP SQL에서 이 엔터티를 읽을 때 실제 파라미터를 생략할 수 있습니다.
**붙이는 곳** 파라미터
**값**

| 값 | 의미 |
|---|---|
| `#CLIENT` | 현재 클라이언트 |
| `#SYSTEM_DATE` | 시스템 날짜 (소스 예제에서는 확인 못 함) |
| `#SYSTEM_LANGUAGE` | 로그온 언어 (소스 예제에서는 확인 못 함) |
| `#USER` | 사용자 이름 (소스 예제에서는 확인 못 함) |

**예시**
```cds
define view entity ZRAP_R_OPENTRAV_###
  with parameters
    @Environment.systemField: #SYSTEM_DATE
    p_today : abap.dats
  as select from zrap_atrav_###
{
  key travel_id as TravelID
}
where end_date >= $parameters.p_today
```
**결과** 화면 변화 없음. `SELECT FROM zrap_r_opentrav_### ...`처럼 파라미터 없이 읽어도 오늘 날짜가 들어갑니다.
**자주 하는 실수** 뷰 엔터티 본문에서는 `$session.system_date`를 직접 쓰는 편이 더 간단합니다. 파라미터가 있는 뷰는 RAP BO의 루트로 쓸 수 없습니다.
**쓰는 문제** (참고용) R-08

### @ObjectModel.usageType (serviceQuality, sizeCategory, dataClass)
**하는 일** 뷰의 성능 특성(얼마나 자주·빠르게 불릴 것인지, 데이터 양, 데이터 종류)을 선언합니다. 성능 검사 도구와 소비자에게 주는 정보입니다.
**붙이는 곳** 뷰 엔터티 헤더
**값**

| 속성 | 값 | 의미 |
|---|---|---|
| `serviceQuality` | `#A` | 자주 불리는 가벼운 뷰(값 도움말 등) |
| | `#B`, `#C`, `#D` | 점점 무거운 처리 허용 (소스 예제에서는 확인 못 함) |
| | `#X` | 트랜잭션 BO 뷰 등 특별 분류 (rf 소스에서 확인) |
| | `#P` | 다른 뷰 구성용 내부 뷰 (소스 예제에서는 확인 못 함) |
| `sizeCategory` | `#XS` `#S` `#M` `#L` `#XL` `#XXL` | 예상 행 수 (`#S`, `#XS` 소스 확인) |
| `dataClass` | `#MASTER` `#MIXED` `#TRANSACTIONAL` `#ORGANIZATIONAL` `#CUSTOMIZING` `#META` | 데이터 종류 (`#MASTER`, `#MIXED` 소스 확인) |

**예시**
```cds
@ObjectModel.usageType:{
  serviceQuality: #A,
  sizeCategory: #S,
  dataClass: #MASTER
}
@ObjectModel.resultSet.sizeCategory: #XS
define view entity ZRAP_I_TRAVSTAT_VH_### ...
```
**결과** 화면 변화 없음.
**자주 하는 실수** `@ObjectModel.resultSet.sizeCategory`(값 도움말을 드롭다운으로)와 이름이 비슷해 헷갈립니다. 화면을 바꾸는 것은 `resultSet` 쪽입니다.
**쓰는 문제** R-01

### @VDM.viewType (참고만)
**하는 일** SAP S/4HANA 가상 데이터 모델(VDM)에서 뷰의 역할(기본/복합/소비/트랜잭션)을 표시합니다. (소스 예제에서는 확인 못 함 — openSAP 자료는 VDM 이름 규칙만 언급)
**붙이는 곳** 뷰 엔터티 헤더
**값**

| 값 | 의미 |
|---|---|
| `#BASIC` / `#COMPOSITE` / `#CONSUMPTION` / `#TRANSACTIONAL` | VDM 계층 구분 (실제 시스템에서 확인 필요) |

**예시**
```cds
@VDM.viewType: #BASIC
define view entity ZRAP_I_AGENCY_### as select from /dmo/agency { key agency_id as AgencyID }
```
**결과** 화면 변화 없음. 이 문제집에서는 **쓰지 않습니다.** 대신 이름 규칙(R_ / C_ / I_)으로 계층을 구분합니다.
**자주 하는 실수** 표준 SAP 뷰에서 복사해 와서 의미 없이 남겨 둠.
**쓰는 문제** (없음)

### @AbapCatalog.entityBuffer.definitionAllowed
**하는 일** CDS 뷰 엔터티(또는 CDS 테이블 엔터티)에 테이블 버퍼를 정의할 수 있게 허용합니다. 실제 버퍼 방식은 별도 `define view entity buffer on ...` 객체로 정합니다.
**붙이는 곳** 뷰 엔터티 헤더
**값**

| 값 | 의미 |
|---|---|
| `true` | 엔터티 버퍼 정의 허용 |
| `false` | 불허 |

**예시**
```cds
@AbapCatalog.entityBuffer.definitionAllowed: true
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Booking Status Value Help'
define view entity ZRAP_I_BOOKSTAT_VH_### ...
```
**결과** 화면 변화 없음. 자주 읽는 작은 설정성 데이터 조회가 빨라질 수 있습니다.
**자주 하는 실수** 자주 바뀌는 트랜잭션 데이터(Travel)에 버퍼를 거는 것. 이 문제집에서는 선택 사항입니다.
**쓰는 문제** (선택) R-09

## 3. 의미 어노테이션 (@Semantics)
`@Semantics`는 "이 필드가 무엇인지"(금액, 통화, 생성 시각, 파일, 이메일 ...)를 알려 줍니다. RAP 프레임워크(관리 필드 자동 채우기, ETag, 스트림 처리)와 Fiori(통화 표시, 링크, 업로드 컨트롤)가 이 정보를 씁니다.
원칙: 데이터의 의미이므로 **R 뷰(또는 테이블)에 한 번** 붙이고 위로 전파시킵니다. MDE에는 쓸 수 없습니다.

### @Semantics.amount.currencyCode
**하는 일** 금액 필드가 어느 통화 코드 필드를 따르는지 연결합니다. 소수점 자리와 통화 기호가 이 연결로 결정됩니다.
**붙이는 곳** 테이블(필드) / 요소 / 추상 엔터티
**값** 문자열: 같은 뷰 안 통화 필드의 **별칭**. 테이블에서는 `'테이블명.필드명'`.
**예시**
```cds
// 테이블 (DDIC)
@Semantics.amount.currencyCode : 'zrap_atrav_###.currency_code'
total_price   : /dmo/total_price;
currency_code : /dmo/currency_code;

// R 뷰
@Semantics.amount.currencyCode: 'CurrencyCode'
total_price   as TotalPrice,
currency_code as CurrencyCode,
```
**결과** OData `Measures.ISOCurrency`. Fiori에서 금액 옆에 통화가 붙어 한 칸에 `1,250.00 EUR`처럼 보이고, 편집 시 통화 필드가 금액 옆에 함께 나옵니다.
**자주 하는 실수**
- 테이블에서 참조를 빼먹어 "참조 필드가 없습니다" 류의 활성화 오류.
- 뷰에서 DB 컬럼명(`'currency_code'`)을 적음. 뷰에서는 별칭(`'CurrencyCode'`).
- 통화 필드의 타입이 통화 키(CUKY) 계열 데이터 엘리먼트가 아님. `/dmo/currency_code`를 쓰세요.
**쓰는 문제** R-01, R-05, R-08

### @Semantics.quantity.unitOfMeasure
**하는 일** 수량 필드가 어느 단위(UoM) 필드를 따르는지 연결합니다.
**붙이는 곳** 테이블(필드) / 요소 / 추상 엔터티
**값** 문자열: 단위 필드의 별칭(테이블에서는 `'테이블.필드'`)
**예시**
```cds
@Semantics.quantity.unitOfMeasure: 'QuantityUnit'
quantity      as Quantity,
quantity_unit as QuantityUnit,
```
**결과** OData `Measures.Unit`. 수량 옆에 단위가 함께 표시됩니다.
**자주 하는 실수** 단위 필드 타입이 단위 키(UNIT) 계열이 아님. Order BO(R-05)의 품목 수량에 쓰세요.
**쓰는 문제** R-05

### @Semantics.currencyCode / @Semantics.unitOfMeasure (뷰 엔터티에서는 쓰지 않음)
**하는 일** "이 필드가 통화 코드(단위)다"라고 표시하던 옛 어노테이션입니다. 옛 DDIC 기반 뷰(`define view`)에서 쓰였습니다.
**붙이는 곳** (옛) DDIC 기반 뷰 요소
**값** `true`
**예시**
```cds
// 옛 DDIC 기반 뷰에서만
@Semantics.currencyCode: true
currency_code as CurrencyCode,
```
**결과** 뷰 엔터티에서는 통화 키 타입(데이터 엘리먼트)만으로 충분합니다.
**자주 하는 실수** 뷰 엔터티에 쓰면 "Annotation Semantics.currencyCode is not allowed in view entities." 오류가 납니다(openSAP 자료에 적힌 메시지). `unitOfMeasure: true`도 같은 이유로 쓰지 마세요(이쪽 메시지는 실제 시스템에서 확인 필요).
**쓰는 문제** (쓰지 않음 — 오류 이해용)

### @Semantics.systemDateTime.createdAt
**하는 일** 인스턴스 생성 시각 필드임을 표시합니다. managed BO에서는 생성 시 프레임워크가 자동으로 채웁니다.
**붙이는 곳** 요소 (R 뷰)
**값** `true`
**예시**
```cds
@Semantics.user.createdBy: true
created_by as CreatedBy,
@Semantics.systemDateTime.createdAt: true
created_at as CreatedAt,
```
**결과** 화면 변화는 거의 없고, managed 저장 시 값이 자동으로 들어갑니다. 타입은 `abp_creation_tstmpl` 같은 타임스탬프여야 합니다.
**자주 하는 실수** BDEF에서 이 필드를 `readonly`로 안 해서 사용자가 입력할 수 있게 둠.
**쓰는 문제** R-01

### @Semantics.systemDateTime.lastChangedAt
**하는 일** 인스턴스(활성 데이터)가 마지막으로 바뀐 시각. managed BO에서 자동 갱신되며, BDEF의 **total etag**(draft 재개 시 충돌 판단)에 씁니다.
**붙이는 곳** 요소 (R 뷰)
**값** `true`
**예시**
```cds
@Semantics.systemDateTime.lastChangedAt: true
last_changed_at as LastChangedAt,
```
**결과** BDEF `total etag LastChangedAt`과 짝. 화면 변화 없음.
**자주 하는 실수** draft BO인데 이 필드가 없어서 `total etag`를 지정할 수 없음.
**쓰는 문제** R-01, R-04

### @Semantics.systemDateTime.localInstanceLastChangedAt
**하는 일** 이 인스턴스(그리고 draft 포함)가 마지막으로 바뀐 시각. managed BO에서 자동 갱신되며 **etag master**(낙관적 잠금)에 씁니다.
**붙이는 곳** 요소 (R 뷰, 자식 엔터티 포함)
**값** `true`
**예시**
```cds
@Semantics.user.localInstanceLastChangedBy: true
local_last_changed_by as LocalLastChangedBy,
@Semantics.systemDateTime.localInstanceLastChangedAt: true
local_last_changed_at as LocalLastChangedAt,
```
**결과** BDEF `etag master LocalLastChangedAt`. 두 사용자가 동시에 고치면 뒤 사람이 ETag 불일치 오류를 받습니다.
**자주 하는 실수** `lastChangedAt`과 혼동. 인스턴스별 ETag에는 `localInstanceLastChangedAt`, draft 전체용 total etag에는 `lastChangedAt`.
**쓰는 문제** R-01, R-05, R-12

### @Semantics.user.createdBy / lastChangedBy / localInstanceLastChangedBy
**하는 일** 생성자·변경자 사용자 필드임을 표시합니다. managed BO에서 자동으로 채워집니다.
**붙이는 곳** 요소 (R 뷰)
**값**

| 어노테이션 | 의미 |
|---|---|
| `@Semantics.user.createdBy: true` | 생성 사용자 |
| `@Semantics.user.lastChangedBy: true` | 마지막 변경 사용자 |
| `@Semantics.user.localInstanceLastChangedBy: true` | 이 인스턴스의 마지막 변경 사용자 |

**예시**
```cds
@Semantics.user.createdBy: true
created_by as CreatedBy,
@Semantics.user.localInstanceLastChangedBy: true
local_last_changed_by as LocalLastChangedBy,
```
**결과** 저장 시 `sy-uname`에 해당하는 사용자 ID가 자동으로 들어갑니다. 화면 변화 없음.
**자주 하는 실수** unmanaged BO(R-05)에서는 자동으로 채워지지 않습니다. 레거시 클래스나 핸들러에서 직접 채워야 합니다.
**쓰는 문제** R-01, R-05

### @Semantics.largeObject
**하는 일** 필드를 큰 객체(LOB, 파일)로 표시해 OData 스트림 속성으로 내보냅니다. Fiori에 업로드/다운로드 컨트롤이 생깁니다.
**붙이는 곳** 요소 (R 뷰 또는 C 뷰), 타입은 `abap.rawstring`(예: `/dmo/attachment`)
**값**

| 속성 | 의미 |
|---|---|
| `mimeType: '필드'` | MIME 유형이 들어 있는 필드 (필수, 대소문자 구분) |
| `fileName: '필드'` | 파일 이름 필드 (선택, 대소문자 구분) |
| `contentDispositionPreference` | `#ATTACHMENT` 다운로드 / `#INLINE` 브라우저에서 열기 |
| `acceptableMimeTypes: ['image/*', 'application/pdf']` | 허용 MIME 유형 목록. `*` 가능 |
| `cacheControl.maxAge` | 캐시 시간 (`#MEDIUM` 등, 피처 쇼케이스에서 확인) |

**예시**
```cds
@Semantics.largeObject: { mimeType: 'MimeType',
                          fileName: 'FileName',
                          acceptableMimeTypes: [ 'image/*', 'application/pdf' ],
                          contentDispositionPreference: #ATTACHMENT }
attachment as Attachment,
@Semantics.mimeType: true
mime_type  as MimeType,
file_name  as FileName,
```
**결과** `$metadata`에 `Attachment`가 `Edm.Stream` 속성으로 나오고 `Core.MediaType`, `Core.ContentDisposition`, `Core.AcceptableMediaTypes`가 붙습니다. 객체 페이지 편집 모드에 업로드 버튼, 표시 모드에 파일 링크가 보입니다.
**자주 하는 실수**
- `mimeType: 'mime_type'`처럼 컬럼명을 씀(별칭, 대소문자 정확히).
- draft 테이블에 첨부 필드를 빼먹음.
- `MimeType`·`FileName`을 화면에도 노출해 사용자가 직접 입력하게 둠 → MDE에서 `@UI.hidden: true`.
**쓰는 문제** R-01

### @Semantics.mimeType
**하는 일** MIME 유형(`image/png` 등)이 들어 있는 필드임을 표시합니다. `largeObject.mimeType`이 가리키는 필드에 붙입니다.
**붙이는 곳** 요소
**값** `true`
**예시** 위 `@Semantics.largeObject` 예시 참고.
**결과** OData `Core.IsMediaType`. 업로드 시 프레임워크가 이 필드에 MIME 유형을 채웁니다.
**자주 하는 실수** 빼먹으면 스트림 속성이 제대로 생성되지 않습니다(LOB 세트로 함께 쓰세요).
**쓰는 문제** R-01

### @Semantics.text
**하는 일** 사람이 읽는 텍스트(이름, 설명) 필드임을 표시합니다. 텍스트 뷰에서 "이게 설명 필드"라고 알려 줄 때 씁니다.
**붙이는 곳** 요소
**값** `true`
**예시** (`/DMO/I_Overall_Status_VH_Text`)
```cds
define view entity ZRAP_I_TRAVSTAT_TEXT_###
  as select from /dmo/oall_stat_t
{
      @ObjectModel.text.element: ['Text']
  key overall_status as OverallStatus,
      @Semantics.language: true
  key language       as Language,
      @Semantics.text: true
      text           as Text
}
```
**결과** `@ObjectModel.text.association`이 이 뷰를 가리킬 때 어느 필드를 텍스트로 쓸지 결정됩니다.
**자주 하는 실수** 텍스트 뷰에 `@Semantics.language`를 같이 안 붙여 언어별로 행이 여러 개 나옴.
**쓰는 문제** R-01

### @Semantics.language
**하는 일** 언어 키 필드임을 표시합니다. 텍스트 뷰의 언어 키에 붙이면 로그온 언어로 자동 필터됩니다.
**붙이는 곳** 요소 (텍스트 뷰의 키)
**값** `true`
**예시** 위 `@Semantics.text` 예시 참고.
**결과** 텍스트 연관을 따라갈 때 로그온 언어 행만 선택됩니다.
**자주 하는 실수** 언어 필드를 키에 넣지 않음 → 텍스트 뷰 키가 유일하지 않음.
**쓰는 문제** R-01

### @Semantics.eMail.address / @Semantics.eMail.type
**하는 일** 이메일 주소 필드임을 표시합니다. `type`은 업무용·우선 등 종류.
**붙이는 곳** 요소
**값**

| 속성 | 값 |
|---|---|
| `address` | `true` |
| `type` | `[#PREF]` 등 배열 (피처 쇼케이스에서 `#PREF` 확인) |

**예시**
```cds
@Semantics.eMail.address: true
email_address as EMailAddress,
```
**결과** OData `Communication.IsEmailAddress`. Fiori에서 클릭하면 메일 앱이 열리는 링크로 보입니다.
**자주 하는 실수** `eMail`의 대문자 M. 코드 완성으로 넣으세요.
**쓰는 문제** R-01

### @Semantics.telephone.type
**하는 일** 전화번호 필드임과 종류를 표시합니다.
**붙이는 곳** 요소
**값**

| 값 | 의미 |
|---|---|
| `[#WORK]` | 회사 전화 |
| `[#HOME]` | 집 전화 |
| `[#CELL]` | 휴대전화 |
| `[#PREF]` | 우선 번호 |

배열이므로 `[ ]`.
**예시**
```cds
@Semantics.telephone.type: [#WORK]
phone_number as PhoneNumber,
```
**결과** Fiori에서 전화 링크(tel:)로 보이고, 연락처 퀵뷰에 들어갑니다.
**자주 하는 실수** `[ ]` 없이 `#WORK`만 씀.
**쓰는 문제** R-01

### @Semantics.name.* / @Semantics.organization.name
**하는 일** 사람 이름의 각 부분 또는 조직 이름임을 표시합니다. 연락처 카드에 쓰입니다.
**붙이는 곳** 요소
**값**

| 어노테이션 | 의미 |
|---|---|
| `@Semantics.name.fullName: true` | 전체 이름 |
| `@Semantics.name.givenName: true` | 이름 |
| `@Semantics.name.familyName: true` | 성 |
| `@Semantics.name.prefix: true` | 호칭 |
| `@Semantics.organization.name: true` | 조직(회사) 이름 |

**예시**
```cds
@Semantics.name.givenName: true
first_name as FirstName,
@Semantics.name.familyName: true
last_name  as LastName,
```
**결과** `@UI.lineItem: [{ type: #AS_CONTACT, value: '_Customer' }]`로 연락처 퀵뷰를 만들 때 이름 부분으로 쓰입니다.
**자주 하는 실수** 화면에 보이는 효과가 없다고 생략. 연락처 퀵뷰를 쓸 때만 의미가 있습니다.
**쓰는 문제** R-01 (선택)

### @Semantics.address.*
**하는 일** 주소의 각 부분임을 표시합니다.
**붙이는 곳** 요소
**값**

| 어노테이션 | 의미 |
|---|---|
| `street` | 거리 |
| `city` | 도시 |
| `zipCode` | 우편번호 |
| `country` | 국가 |
| `label` | 줄바꿈까지 포함한 완성된 주소 문자열 (주소 facet용) |

모두 `true`.
**예시**
```cds
@Semantics.address.street: true
street      as Street,
@Semantics.address.zipCode: true
postal_code as PostalCode,
@Semantics.address.city: true
city        as City,
@Semantics.address.country: true
country_code as CountryCode,
```
**결과** 연락처 퀵뷰의 주소 부분, 그리고 `label`은 facet `type: #ADDRESS_REFERENCE`로 표시됩니다(피처 쇼케이스).
**자주 하는 실수** `zipCode`를 `postalCode`로 씀. 소스 표기는 `zipCode`입니다.
**쓰는 문제** R-01 (Agency/Customer 값 도움말 확장 시, 선택)

### @Semantics.imageUrl
**하는 일** 필드가 이미지 URL임을 표시합니다.
**붙이는 곳** 요소
**값** `true`
**예시**
```cds
@Semantics.imageUrl: true
image_url as ImageUrl,
```
**결과** 목록 열이나 `@UI.headerInfo.imageUrl`에서 URL 문자열 대신 그림이 보입니다.
**자주 하는 실수** `@UI.headerInfo.imageUrl`만 지정하고 이 어노테이션을 빼서 텍스트로 나옴.
**쓰는 문제** R-01 (선택)

### @Semantics.timeZone / @Semantics.timeZoneReference
**하는 일** `timeZone`은 필드가 시간대 값임을, `timeZoneReference`는 타임스탬프 필드를 어느 시간대 필드 기준으로 보여 줄지 지정합니다.
**붙이는 곳** 요소 / 추상 엔터티 요소
**값**

| 어노테이션 | 값 |
|---|---|
| `@Semantics.timeZone` | `true` |
| `@Semantics.timeZoneReference` | 시간대 필드 별칭 |

**예시** (피처 쇼케이스 `/DMO/FSA_R_RootTP`)
```cds
@Semantics.timeZoneReference: 'IANATimezone'
Timestamp as IANATimestamp,
```
**결과** UI가 UTC 타임스탬프를 지정한 시간대로 바꿔 보여 줍니다(변환은 UI에서).
**자주 하는 실수** 타임스탬프가 UTC가 아닌데 사용.
**쓰는 문제** (선택) R-01

### @Semantics.dateTime / @Semantics.nullValueIndicatorFor
**하는 일** `dateTime`은 DEC 타입 숫자를 날짜-시각(타임스탬프)으로 해석하게 합니다. `nullValueIndicatorFor`는 "다른 필드가 NULL(값 없음)인지"를 알려 주는 표시 필드를 만듭니다.
**붙이는 곳** 요소
**값**

| 어노테이션 | 값 |
|---|---|
| `@Semantics.dateTime` | `true` |
| `@Semantics.nullValueIndicatorFor` | 대상 필드 별칭 |

**예시** (피처 쇼케이스)
```cds
@Semantics.dateTime: true
type_dec_time as TypeDecTime,

@Semantics.nullValueIndicatorFor: 'CriticalityCode'
cast(' ' as abap_boolean preserving type) as CriticalityNullValInd,
```
**결과** `dateTime`: DEC(21,7) 숫자가 날짜·시각으로 표시. `nullValueIndicatorFor`: UUID가 아닌 키의 퀵뷰에서 값 없음을 구분.
**자주 하는 실수** 일반 타임스탬프 타입(`timestampl` 계열 데이터 엘리먼트)에는 필요 없습니다.
**쓰는 문제** (참고)

### @Semantics.valueRange.maximum
**하는 일** 필드 값 범위의 최댓값을 선언합니다. rf 싱글턴 예제는 루트 뷰 헤더에 `'1'`을 붙여, 루트 인스턴스가 하나뿐임을 표시합니다.
**붙이는 곳** 뷰 엔터티 헤더 / 요소
**값** 문자열 숫자 (예: `'1'`)
**예시** (`/DMO/I_CarriersLockSingleton_S`)
```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Booking Fee Config Singleton'
@Semantics.valueRange.maximum: '1'
define root view entity ZRAP_I_FEECFG_S_###
  as select from I_Language
    left outer join zrap_feecfg_### as cfg on 0 = 0
  composition [0..*] of ZRAP_I_FEECFG_###   as _Fee
{
  key 1 as SingletonID,
      max(cfg.last_changed_at) as LastChangedAtMax,
      _Fee
}
where I_Language.Language = $session.system_language
```
**결과** 싱글턴 루트 패턴에서 쓰입니다. 정확히 어떤 화면 효과를 내는지는 소스 설명이 없어 실제 시스템에서 확인 필요합니다. (예시 객체 이름은 R-09용 가상 이름)
**자주 하는 실수** 싱글턴 여부는 이 어노테이션이 아니라 루트 뷰의 고정 키(`key 1`)와 서비스 구성으로 만들어집니다. 이것만 붙인다고 싱글턴이 되지 않습니다.
**쓰는 문제** R-09

### @Semantics.booleanIndicator (GitHub 공개 코드에서만 확인)
**하는 일** `CHAR(1)` 같은 필드를 참/거짓 값으로 해석하라고 표시합니다.
**붙이는 곳** 요소
**값** `true`
**예시**
```cds
@Semantics.booleanIndicator: true
is_deleted as IsDeleted,
```
**결과** UI에서 체크박스처럼 보일 수 있습니다. 다만 요즘은 `abap_boolean` 타입을 쓰면 OData `Edm.Boolean`으로 바로 나가므로 이 어노테이션이 필요 없는 경우가 많습니다(실제 시스템에서 확인 필요).
**자주 하는 실수** `abap_boolean` 필드에 중복으로 붙임.
**쓰는 문제** (참고)

### @Semantics.businessDate.from / .to (분석 샘플에서만 확인)
**하는 일** 유효 기간의 시작일·종료일 필드임을 표시합니다. 시간 종속 데이터(계층, 마스터 데이터)에 씁니다.
**붙이는 곳** 요소
**값** `true`
**예시** (SAP-samples/abap-platform-analytics-data-modeling)
```cds
@Semantics.businessDate.to: true
key date_to   as DateTo,
@Semantics.businessDate.from: true
    date_from as DateFrom,
```
**결과** 분석 엔진이 기준일에 유효한 행을 고를 때 씁니다. 트랜잭션 Fiori 화면 변화는 없습니다.
**자주 하는 실수** Travel의 `BeginDate`/`EndDate`(여행 기간)에 붙임. 그것은 "데이터 유효 기간"이 아니라 업무 값이므로 붙이지 않습니다.
**쓰는 문제** (참고)

### @Semantics.uuid (GitHub SAP 샘플에서만 확인)
**하는 일** 필드가 UUID(16바이트 RAW)임을 표시합니다.
**붙이는 곳** 요소
**값** `true`
**예시** (SAP-samples/teched2025-AD163)
```cds
@Semantics.uuid: true
key order_uuid as OrderUuid,
```
**결과** 화면 변화 없음. 이 문제집은 Travel·Order 키를 숫자 ID로 쓰므로 필수는 아닙니다. 타입이 `sysuuid_x16`이면 OData `Edm.Guid`로 나갑니다(실제 시스템에서 확인 필요).
**자주 하는 실수** 문자 UUID(`sysuuid_c32`)에 붙임.
**쓰는 문제** (참고)

## 4. 모델 어노테이션 (@ObjectModel)
`@ObjectModel`은 엔터티와 필드의 "모델상 역할"을 정합니다: 사람이 쓰는 키, 텍스트 필드, 값 도움말·텍스트 뷰라는 표시, 계산 필드와 커스텀 엔터티의 구현 클래스 등입니다.
일부(텍스트, 시맨틱 키)는 Fiori 화면을 바로 바꾸고, 일부(구현 클래스)는 RAP 런타임이 ABAP 코드를 부르게 만듭니다.

### @ObjectModel.semanticKey
**하는 일** 기술 키(UUID 등)와 별개로 사용자가 알아보는 업무 키를 지정합니다. 이 문제집의 Travel은 기술 키와 업무 키가 같은 `TravelID`입니다.
**붙이는 곳** 뷰 엔터티 헤더 / 프로젝션
**값** 요소 별칭 배열 `['TravelID']`
**예시**
```cds
@ObjectModel.semanticKey: ['TravelID']
@Search.searchable: true
define root view entity ZRAP_C_TRAVEL_###
  provider contract transactional_query
  as projection on ZRAP_R_TRAVEL_### ...
```
**결과** OData `Common.SemanticKey`. 목록에서 그 필드가 **굵게** 보이고, draft 앱에서 "초안", "다른 사용자가 편집 중" 같은 편집 상태가 그 필드 옆에 표시됩니다.
**자주 하는 실수** late numbering이라 draft에서는 `TravelID`가 비어 있음 → 초안 행의 굵은 키가 빈칸으로 보이는 것은 정상입니다.
**쓰는 문제** R-01, R-05, R-07

### @ObjectModel.representativeKey
**하는 일** 여러 키 필드 중 이 엔터티를 대표하는 키(보통 마지막 키)를 지정합니다. 다른 뷰가 `@ObjectModel.foreignKey.association`으로 이 엔터티를 가리킬 때 기준이 됩니다.
**붙이는 곳** 뷰 엔터티 헤더
**값** 요소 별칭 문자열
**예시** (rap500 Carrier 차원 뷰)
```cds
@ObjectModel.representativeKey: 'ConnectionID'
define view entity ZRAP_I_CONNECTION_###
  as select from /dmo/connection
{
  key carrier_id    as CarrierID,
  key connection_id as ConnectionID
}
```
**결과** 화면 변화 거의 없음. 주로 분석·값 도움말 모델링용.
**자주 하는 실수** 단일 키 뷰에도 붙여야 한다고 생각함. 단일 키면 생략 가능합니다.
**쓰는 문제** R-11 (선택)

### @ObjectModel.text.element
**하는 일** 코드·ID 필드에 "이 필드의 설명 텍스트는 같은 뷰의 이 요소"라고 연결합니다.
**붙이는 곳** 요소 (C 뷰, 값 도움말 뷰)
**값** 요소 별칭 배열 `['CustomerName']`
**예시**
```cds
@ObjectModel.text.element: ['CustomerName']
CustomerID,
_Customer.LastName as CustomerName,
```
**결과** OData `Common.Text`. Fiori가 `CustomerID` 칸에 `Smith (000123)`처럼 텍스트와 ID를 같이 보여 줍니다. 배치 방식은 `@UI.textArrangement`로 정합니다.
**자주 하는 실수** 텍스트 요소를 뷰에 추가하지 않고 이름만 적음 → 활성화 오류.
**쓰는 문제** R-01, R-05

### @ObjectModel.text.association
**하는 일** 텍스트가 별도의 (언어 종속) 텍스트 뷰에 있을 때, 그 텍스트 뷰로 가는 **연관**을 지정합니다.
**붙이는 곳** 요소 (값 도움말 뷰, R/C 뷰)
**값** 연관 이름 문자열 `'_Text'`
**예시** (`/DMO/I_Overall_Status_VH`)
```cds
@ObjectModel.resultSet.sizeCategory: #XS
define view entity ZRAP_I_TRAVSTAT_VH_###
  as select from /dmo/oall_stat
  association [0..*] to ZRAP_I_TRAVSTAT_TEXT_### as _Text
    on $projection.OverallStatus = _Text.OverallStatus
{
      @UI.textArrangement: #TEXT_ONLY
      @ObjectModel.text.association: '_Text'
  key overall_status as OverallStatus,
      _Text
}
```
**결과** 상태 코드 `O` 대신 로그온 언어의 `Open`이 보입니다. 텍스트 뷰에는 `@Semantics.text`/`@Semantics.language`가 필요합니다.
**자주 하는 실수** 연관을 SELECT 목록에 노출(`_Text,`)하지 않음.
**쓰는 문제** R-01

### @ObjectModel.dataCategory
**하는 일** 이 뷰가 어떤 종류의 보조 뷰인지 표시합니다.
**붙이는 곳** 뷰 엔터티 헤더
**값**

| 값 | 의미 |
|---|---|
| `#TEXT` | 텍스트 뷰 (언어별 설명) |
| `#VALUE_HELP` | 값 도움말 전용 뷰 |

**예시** (`/DMO/I_Supplement_StdVH`)
```cds
@ObjectModel.dataCategory: #VALUE_HELP
@ObjectModel.semanticKey: ['AgencyID']
@Search.searchable: true
define view entity ZRAP_I_AGENCY_STDVH_### ...
```
**결과** 화면 변화는 거의 없고 뷰의 용도를 알려 주는 정보입니다(분석 모델링에서는 `#TEXT`가 텍스트 결합에 쓰임).
**자주 하는 실수** 트랜잭션 BO 뷰에 붙임.
**쓰는 문제** R-01

### @ObjectModel.resultSet.sizeCategory
**하는 일** 결과 집합이 아주 작다고 선언합니다. 값 도움말 뷰에 붙이면 Fiori가 팝업 대신 **드롭다운**을 보여 줍니다.
**붙이는 곳** 뷰 엔터티 헤더 (값 도움말 대상 뷰)
**값**

| 값 | 의미 |
|---|---|
| `#XS` | 아주 작음 (수십 건 이하) → 드롭다운 |

**예시**
```cds
@ObjectModel.resultSet.sizeCategory: #XS
define view entity ZRAP_I_TRAVSTAT_VH_### ...
```
**결과** OData `Common.ValueListWithFixedValues`. 상태 필드가 고정 값 드롭다운으로 바뀝니다. 입력값 검증 효과도 있습니다.
**자주 하는 실수** 행이 수천 건인 뷰(고객)에 붙여 드롭다운이 느려짐.
**쓰는 문제** R-01, R-05

### @ObjectModel.virtualElementCalculatedBy
**하는 일** `virtual` 요소의 값을 ABAP 클래스가 계산하도록 연결합니다. 클래스는 `IF_SADL_EXIT_CALC_ELEMENT_READ`를 구현합니다.
**붙이는 곳** 프로젝션(C 뷰)의 `virtual` 요소
**값** `'ABAP:클래스명'`
**예시**
```cds
@ObjectModel.virtualElementCalculatedBy: 'ABAP:ZCL_RAP_TRAV_VE_###'
@EndUserText.label: 'Overall Status Indicator'
virtual OverallStatusIndicator : abap.int2,
```
**결과** OData에는 일반 읽기 전용 속성처럼 나갑니다. 값은 조회할 때마다 클래스의 `calculate` 메서드가 채웁니다. `criticality`에 쓰면 상태 색이 나옵니다.
**자주 하는 실수**
- `ABAP:` 접두어 누락.
- `get_calculation_info`에서 필요한 원본 필드(`OverallStatus`)를 요청하지 않아 계산 시 값이 비어 있음.
- 가상 요소로 필터·정렬하려면 아래 `filter/sort.transformedBy`가 따로 필요합니다.
**쓰는 문제** R-01, R-02

### @ObjectModel.filter.transformedBy / @ObjectModel.sort.transformedBy (GitHub 공개 코드에서만 확인)
**하는 일** 가상 요소에 대한 필터·정렬 조건을 실제 DB 필드 조건으로 바꿔 주는 ABAP 클래스를 지정합니다.
**붙이는 곳** 프로젝션의 `virtual` 요소
**값** `'ABAP:클래스명'` (함께 `@ObjectModel.filter.enabled: true`, `@ObjectModel.sort.enabled: true`가 쓰이는 것을 공개 코드에서 확인)
**예시**
```cds
@ObjectModel.virtualElementCalculatedBy: 'ABAP:ZCL_RAP_TRAV_VE_###'
@ObjectModel.filter.enabled: true
@ObjectModel.filter.transformedBy: 'ABAP:ZCL_RAP_TRAV_VE_###'
virtual OverallStatusIndicator : abap.int2,
```
**결과** 목록에서 가상 요소로 필터해도 오류 없이 동작합니다. 클래스가 구현할 인터페이스 이름(`IF_SADL_EXIT_FILTER_TRANSFORM` / `IF_SADL_EXIT_SORT_TRANSFORM`)은 실제 시스템에서 확인 필요.
**자주 하는 실수** 계산 클래스만 만들고 필터를 허용해 런타임 오류.
**쓰는 문제** (심화) R-02

### @ObjectModel.query.implementedBy
**하는 일** 커스텀 엔터티의 데이터를 제공하는 ABAP 클래스를 지정합니다. 클래스는 `IF_RAP_QUERY_PROVIDER`를 구현해 `select` 메서드에서 페이징·필터·정렬을 처리합니다.
**붙이는 곳** 커스텀 엔터티 헤더
**값** `'ABAP:클래스명'`
**예시**
```cds
@EndUserText.label: 'Flight Weather (custom entity)'
@ObjectModel.query.implementedBy: 'ABAP:ZCL_RAP_CE_FLIGHT_###'
define root custom entity ZRAP_CE_FLIGHT_###
{
  key CarrierID    : /dmo/carrier_id;
  key ConnectionID : /dmo/connection_id;
      Distance     : abap.int4;
}
```
**결과** 서비스로 노출하면 OData 읽기 요청이 들어올 때마다 이 클래스가 호출됩니다. `$metadata`는 일반 엔터티와 같습니다.
**자주 하는 실수**
- `select`에서 `io_request->get_paging( )` 등 요청 정보를 읽지 않고 데이터만 넘김 → "요청된 정보를 처리하지 않았다"는 류의 런타임 오류.
- 커스텀 엔터티는 SQL로 읽을 수 없습니다(`SELECT FROM` 불가).
**쓰는 문제** R-08

### @OData.property.valueControl
**하는 일** 커스텀 엔터티에서 "값이 없음(null)"을 표현하기 위한 짝 필드를 지정합니다. 짝 필드 타입은 `rap_cp_odata_value_control`.
**붙이는 곳** 커스텀 엔터티 요소
**값** 짝 필드 이름 문자열
**예시** (openSAP week5 `zce_rap_agency_####`)
```cds
@OData.property.valueControl: 'Name_vc'
Name    : abap.char( 31 );
Name_vc : rap_cp_odata_value_control;
```
**결과** 원격 OData 서비스 결과를 그대로 전달하는 커스텀 엔터티에서 null과 빈 값을 구분할 수 있습니다. 정확한 OData 표현은 실제 시스템에서 확인 필요.
**자주 하는 실수** 일반 뷰 엔터티에 사용.
**쓰는 문제** R-08 (선택)

### @ObjectModel.foreignKey.association
**하는 일** 이 필드가 연관 대상 엔터티의 (대표) 키를 가리키는 외래 키라고 표시합니다.
**붙이는 곳** 요소
**값** 연관 이름 `'_Carrier'`
**예시**
```cds
association [1] to ZRAP_I_CARRIER_### as _Carrier
  on $projection.CarrierID = _Carrier.CarrierID
{
  @ObjectModel.foreignKey.association: '_Carrier'
  key carrier_id as CarrierID,
  ...
  _Carrier
}
```
**결과** 분석 모델에서 차원 연결에 쓰입니다. 트랜잭션 Fiori 화면에는 큰 변화가 없습니다.
**자주 하는 실수** 값 도움말이 생긴다고 기대함. 값 도움말은 `@Consumption.valueHelpDefinition`이 만듭니다.
**쓰는 문제** R-11 (선택)

### @ObjectModel.sapObjectNodeType.name (GitHub SAP 샘플에서만 확인)
**하는 일** 이 BO 노드의 SAP 객체 노드 유형 이름을 선언합니다. 비즈니스 이벤트, 협업 기능 등에서 BO를 식별하는 이름으로 쓰입니다.
**붙이는 곳** 뷰 엔터티 헤더 (R 뷰 루트)
**값** 문자열 (예: `'ZRAP_Travel_###'`)
**예시** (SAP-samples/abap-platform-bgpf-appl-log-events-side-effects)
```cds
@AccessControl.authorizationCheck: #CHECK
@Metadata.allowExtensions: true
@EndUserText.label: 'Travel'
@ObjectModel.sapObjectNodeType.name: 'ZRAP_Travel_###'
define root view entity ZRAP_R_TRAVEL_### ...
```
**결과** 화면 변화 없음. 최근 ADT 생성 마법사가 자동으로 넣어 주기도 합니다. 이벤트 정의에 꼭 필요한지는 실제 시스템에서 확인 필요.
**자주 하는 실수** 다른 BO와 같은 이름 사용.
**쓰는 문제** R-04 (선택)

### @ObjectModel.collectiveValueHelp.for.element / modelingPattern / supportedCapabilities
**하는 일** 여러 값 도움말을 하나의 "모음 값 도움말"로 묶는 추상 엔터티임을 선언합니다.
**붙이는 곳** 추상 엔터티 헤더
**값**

| 어노테이션 | 값 |
|---|---|
| `@ObjectModel.collectiveValueHelp.for.element` | 대상 필드 이름 |
| `@ObjectModel.modelingPattern` | `#COLLECTIVE_VALUE_HELP` |
| `@ObjectModel.supportedCapabilities` | `[#COLLECTIVE_VALUE_HELP]` |

**예시** (피처 쇼케이스 `/DMO/FSA_D_CountryCVH`)
```cds
@EndUserText.label: 'Customer Collective Value Help'
@ObjectModel.supportedCapabilities: [#COLLECTIVE_VALUE_HELP]
@ObjectModel.modelingPattern: #COLLECTIVE_VALUE_HELP
@ObjectModel.collectiveValueHelp.for.element: 'CustomerID'
define abstract entity ZRAP_D_CUSTOMER_CVH_###
{
  @Consumption.valueHelpDefinition: [
    { entity: { name: '/DMO/I_Customer_StdVH', element: 'CustomerID' }, label: 'By Customer' },
    { entity: { name: 'ZRAP_I_CUST_BY_CITY_###', element: 'CustomerID' },
      label: 'By City', qualifier: 'ByCity' } ]
  CustomerID : /dmo/customer_id;
}
```
**결과** 값 도움말 팝업에 "검색 방법" 선택 목록이 생깁니다. (예시의 `ZRAP_I_CUST_BY_CITY_###`는 가상의 보조 뷰)
**자주 하는 실수** 모음 값 도움말에서는 `useForValidation`이 동작하지 않습니다(피처 쇼케이스 설명).
**쓰는 문제** (선택) R-01

### @ObjectModel.compositionRoot / @OData.publish (옛 BOPF 방식 — RAP에서는 쓰지 않음)
**하는 일** RAP 이전(CDS + BOPF, SEGW 없는 OData V2 자동 노출) 시절에 루트 노드와 서비스 노출을 지정하던 어노테이션입니다.
**붙이는 곳** 옛 DDIC 기반 뷰(`define view`) 헤더
**값** `true`
**예시** (옛 코드 모양, 공개 저장소에서 확인)
```cds
@ObjectModel.compositionRoot: true
@ObjectModel.transactionalProcessingEnabled: true
@OData.publish: true
define view ZI_OLD_HEADER as select from ...
```
**결과** RAP에서는 각각 `define root view entity`와 `composition`, 그리고 SRVD + 서비스 바인딩이 이 역할을 합니다.
**자주 하는 실수** 블로그 예제를 복사해 RAP 뷰 엔터티에 넣음 → 허용되지 않거나 의미 없음. 이 문제집에서는 **쓰지 않습니다**.
**쓰는 문제** (없음 — 구분용)

## 5. 검색·값 도움말·필터 (@Search, @Consumption)
목록 위 검색창, 입력 필드의 값 도움말(F4), 필터 바의 동작을 정합니다. 서비스(앱)마다 달라질 수 있는 것이므로 보통 **C 뷰**에 붙이고, `@Consumption.filter.*`와 `@Consumption.valueHelpDefinition`은 MDE에도 쓸 수 있습니다.
`@Search.*`는 MDE에 쓰지 않습니다(소스 MDE 어디에도 없음).

### @Search.searchable
**하는 일** 이 엔터티에 자유 텍스트 검색을 켭니다.
**붙이는 곳** 뷰 엔터티 헤더 / 프로젝션 / 값 도움말 뷰
**값**

| 값 | 의미 |
|---|---|
| `true` | 검색 가능 |
| `false` | 검색 불가 |

**예시**
```cds
@Search.searchable: true
define root view entity ZRAP_C_TRAVEL_###
  provider contract transactional_query
  as projection on ZRAP_R_TRAVEL_###
{
  @Search.defaultSearchElement: true
  key TravelID,
  ...
}
```
**결과** List Report 필터 바 왼쪽에 **검색** 입력란이 생기고, 값 도움말 팝업에도 검색창이 생깁니다.
**자주 하는 실수** `@Search.defaultSearchElement`를 하나도 안 붙여 활성화 오류(검색 대상 요소가 최소 하나 필요).
**쓰는 문제** R-01, R-05, R-08

### @Search.defaultSearchElement
**하는 일** 자유 텍스트 검색 대상에 이 요소를 포함합니다.
**붙이는 곳** 요소
**값** `true`
**예시**
```cds
@Search.defaultSearchElement: true
@Search.fuzzinessThreshold: 0.8
Description,
```
**결과** 검색창에 입력한 글자로 이 필드를 찾습니다.
**자주 하는 실수** 금액·날짜 필드에 붙임. 검색은 문자 필드에 의미가 있습니다.
**쓰는 문제** R-01, R-05

### @Search.fuzzinessThreshold
**하는 일** 오타 허용(퍼지) 검색의 기준값입니다. 1에 가까울수록 정확히 같은 것만 찾습니다.
**붙이는 곳** 요소
**값** 0 ~ 1 사이 소수 (소스 예: `0.8`, `0.87`, `0.9`)
**예시**
```cds
@Search: { defaultSearchElement: true, fuzzinessThreshold: 0.87 }
LastName,
```
**결과** `Smth`로 검색해도 `Smith`가 나올 수 있습니다(데이터베이스 퍼지 검색 지원에 따라 다름).
**자주 하는 실수** 0.5처럼 너무 낮게 해서 엉뚱한 결과가 많이 나옴.
**쓰는 문제** R-01

### @Search.ranking (GitHub 공개 코드에서만 확인)
**하는 일** 검색 결과 순위에서 이 요소 일치의 가중치를 정합니다.
**붙이는 곳** 요소
**값**

| 값 | 의미 |
|---|---|
| `#HIGH` | 높은 가중치 |
| `#MEDIUM` | 보통 |
| `#LOW` | 낮은 가중치 |

**예시**
```cds
@Search.defaultSearchElement: true
@Search.ranking: #HIGH
key AgencyID,
@Search.defaultSearchElement: true
@Search.ranking: #LOW
Name,
```
**결과** 같은 검색어라도 키 일치가 위에 옵니다(효과 크기는 실제 시스템에서 확인 필요).
**자주 하는 실수** 모든 요소를 `#HIGH`로 해서 의미가 없어짐.
**쓰는 문제** (선택) R-01

### @Consumption.valueHelpDefinition
**하는 일** 입력 필드에 값 도움말(F4)을 붙입니다. 어떤 엔터티의 어떤 요소에서 값을 고를지, 다른 필드와 어떻게 연동할지 정합니다.
**붙이는 곳** 요소 (C 뷰, R 뷰, MDE) / 파라미터 / 추상 엔터티 요소(액션 파라미터)
**값**

| 속성 | 의미 |
|---|---|
| `entity.name` | 값 도움말 제공 엔터티 (예: `'/DMO/I_Agency_StdVH'`) |
| `entity.element` | 그 엔터티에서 이 필드로 돌려줄 요소 |
| `additionalBinding: [{ localElement, element, usage }]` | 추가 필드 연동 (아래 표) |
| `useForValidation: true` | 입력값이 값 목록에 있는지 검증 |
| `qualifier: 'q'` | 같은 필드에 여러 값 도움말이 있을 때 구분 |
| `label: '...'` | 여러 값 도움말 중 선택 목록에 보일 이름 |
| `distinctValues: true` | 중복 제거된 값만 보이기 (GitHub 공개 코드에서만 확인) |
| `presentationVariantQualifier: 'q'` | 값 도움말 결과 정렬 등에 쓸 presentationVariant 지정 (소스 예제에서는 확인 못 함) |

`additionalBinding.usage` 값:

| 값 | 의미 |
|---|---|
| `#FILTER` | 내 화면의 `localElement` 값으로 값 도움말 목록을 거름 |
| `#RESULT` | 값을 고르면 `element` 값이 내 `localElement`에 채워짐 |
| `#FILTER_AND_RESULT` | 둘 다 (생략 시 기본 동작으로 쓰이는 경우가 많음) |

**예시**
```cds
@Consumption.valueHelpDefinition: [{
  entity: { name: '/DMO/I_Flight', element: 'ConnectionID' },
  additionalBinding: [
    { localElement: 'CarrierID',  element: 'AirlineID',  usage: #FILTER_AND_RESULT },
    { localElement: 'FlightDate', element: 'FlightDate', usage: #RESULT },
    { localElement: 'FlightPrice', element: 'Price',     usage: #RESULT },
    { localElement: 'CurrencyCode', element: 'CurrencyCode', usage: #RESULT } ],
  useForValidation: true
}]
ConnectionID,
```
**결과** OData `Common.ValueList`(+ `Common.ValueListForValidation`). Booking에서 연결편을 고르면 항공사·날짜·가격·통화가 함께 채워지고, 없는 값을 입력하면 빨간 오류 표시가 납니다(draft에서는 잘못된 값이 draft에 저장되지 않음).
**자주 하는 실수**
- `element`(값 도움말 쪽)와 `localElement`(내 쪽)를 반대로 씀.
- 값 도움말 엔터티를 SRVD에 노출하지 않아 팝업이 비어 있음 → `expose /DMO/I_Agency_StdVH as Agency;`.
- 같은 필드에 값 도움말 두 개를 두고 `qualifier`를 안 써서 `useForValidation`이 이상하게 동작.
**쓰는 문제** R-01, R-02, R-05, R-11

### @Consumption.valueHelpDefault.display / .fetchValues
**하는 일** `display`: 값 도움말 결과 표에 이 요소를 기본으로 보일지 정합니다. `fetchValues`: 값 도움말을 열 때 바로 값을 가져올지, 사용자가 요청할 때만 가져올지 정합니다.
**붙이는 곳** `display`: 값 도움말 뷰 요소 / `fetchValues`: 뷰 헤더 (rf 추천 예제는 R·C 뷰 헤더)
**값**

| 어노테이션 | 값 | 의미 |
|---|---|---|
| `display` | `true` / `false` | 결과 표 기본 열 표시 여부 |
| `fetchValues` | `#ON_EXPLICIT_REQUEST` | 사용자가 "Go"를 누를 때만 조회 (rf `rec` 예제) |

**예시**
```cds
// 값 도움말 뷰
@Consumption.valueHelpDefault.display: false
building as Building,

// 추천(recommendations) 예제 C 뷰 헤더
@Consumption.valueHelpDefault.fetchValues: #ON_EXPLICIT_REQUEST
define root view entity ZRAP_C_TRAVEL_REC_### ...
```
**결과** 값 도움말 팝업의 열 구성과 첫 조회 시점이 바뀝니다.
**자주 하는 실수** `fetchValues`의 다른 값은 소스에서 확인하지 못했습니다. 코드 완성으로 확인하세요.
**쓰는 문제** R-01, R-11

### @Consumption.filter.* (defaultValue, hidden, selectionType, multipleSelections, mandatory)
**하는 일** 필터 바에서 이 필드를 어떻게 필터할지 정합니다.
**붙이는 곳** 요소 (C 뷰, MDE) / 파라미터
**값**

| 속성 | 값 | 의미 |
|---|---|---|
| `defaultValue` | `'값'` | 필터 기본값 (변형을 바꾸면 무시됨) |
| `hidden` | `true` | "필터 조정" 목록에서 숨김 |
| `selectionType` | `#SINGLE` / `#INTERVAL` / `#RANGE` | 단일 값 / 구간 / 범위 조건 (`#INTERVAL`, `#RANGE`는 공개 코드에서 확인, `#SINGLE`은 확인 못 함) |
| `multipleSelections` | `true` / `false` | 여러 값 허용 (공개 코드에서 확인) |
| `mandatory` | `true` / `false` | 필수 필터 (공개 코드에서 확인) |

**예시**
```cds
annotate entity ZRAP_C_TRAVEL_### with
{
  @UI.selectionField: [{ position: 40 }]
  @Consumption.filter.defaultValue: 'O'
  OverallStatus;

  @Consumption.filter.hidden: true
  LocalLastChangedAt;
}
```
**결과** 앱을 열면 상태 필터에 `O`가 미리 들어가 있고, `LocalLastChangedAt`은 필터 추가 목록에 안 보입니다. 정확한 OData 어휘 매핑(`Common.FilterDefaultValue` 등)은 `$metadata`로 확인하세요.
**자주 하는 실수** 복잡한 기본 조건을 `defaultValue`로 하려 함 → 그런 경우는 `@UI.selectionVariant`가 낫습니다(피처 쇼케이스 설명).
**쓰는 문제** R-01, R-06

### @Consumption.hidden
**하는 일** 요소를 소비자(OData 서비스)에게 **아예 노출하지 않습니다.** 내부 계산용 필드에 씁니다.
**붙이는 곳** 요소 (C 뷰, R 뷰)
**값** `true`
**예시** (rf 싱글턴 C 뷰)
```cds
@Consumption.hidden: true
LastChangedAtMax,
```
**결과** `$metadata`에 속성이 없습니다. EML/ABAP 안에서는 여전히 읽을 수 있습니다.
**자주 하는 실수** `@UI.hidden`과 혼동. `@UI.hidden`은 화면에서만 숨기고 OData에는 남습니다. ETag·draft에 필요한 필드(`LocalLastChangedAt`)에 `@Consumption.hidden`을 붙이면 ETag 처리가 깨질 수 있으니 `@UI.hidden`을 쓰세요.
**쓰는 문제** R-01, R-09

### @Consumption.semanticObject
**하는 일** 필드에 시맨틱 객체(Fiori 런치패드의 앱 이동 대상 이름)를 지정합니다. `semanticObjectAction`과 함께 의도 기반 이동(IBN)을 만듭니다.
**붙이는 곳** 요소 (MDE, C 뷰)
**값** 시맨틱 객체 이름 문자열
**예시** (피처 쇼케이스)
```cds
@Consumption.semanticObject: 'Customer'
@UI.lineItem: [{ type: #FOR_INTENT_BASED_NAVIGATION,
                 semanticObjectAction: 'display',
                 label: 'Show Customer' }]
CustomerID;
```
**결과** OData `Common.SemanticObject`. 런치패드에 배포된 앱 사이에서만 실제 이동이 됩니다. ADT 미리보기에서는 동작하지 않습니다.
**자주 하는 실수** 트라이얼 미리보기에서 버튼이 안 눌린다고 오류로 생각함(정상).
**쓰는 문제** (선택) R-11

## 6. UI: 헤더 정보와 목록 (List Report)
`@UI.*` 어노테이션은 Fiori Elements가 화면을 그리는 방법을 정합니다. RAP에서는 **MDE**에 모아 쓰는 것이 원칙입니다(데이터 모델과 화면을 분리).
이 그룹은 List Report(목록 화면)와 엔터티 전체에 걸친 헤더 어노테이션을 다룹니다. `position`은 10, 20, 30 ...처럼 띄워 두면 나중에 사이에 끼워 넣기 쉽습니다.

### @UI.headerInfo
**하는 일** 엔터티의 이름(단수·복수), 객체 페이지 제목·부제목, 아이콘·이미지를 정합니다.
**붙이는 곳** MDE 헤더 (또는 뷰 헤더)
**값**

| 속성 | 의미 |
|---|---|
| `typeName` | 단수 이름. 객체 페이지 맨 위 작은 제목 |
| `typeNamePlural` | 복수 이름. 목록 표 제목, 객체 페이지 안 자식 표 제목 |
| `title: { type: #STANDARD, value: '요소', label }` | 객체 페이지 큰 제목 (`type: #AS_CONNECTED_FIELDS, valueQualifier`도 가능) |
| `description: { type: #STANDARD, value: '요소' }` | 제목 아래 부제목 |
| `imageUrl: '요소'` | 제목 왼쪽 그림 (이미지 URL 요소) |
| `typeImageUrl: 'sap-icon://...'` | 그림이 없을 때 보일 아이콘 |

**예시**
```cds
@Metadata.layer: #CORE
@UI.headerInfo: {
  typeName: 'Travel',
  typeNamePlural: 'Travels',
  typeImageUrl: 'sap-icon://flight',
  title:       { type: #STANDARD, value: 'TravelID' },
  description: { type: #STANDARD, value: 'Description' }
}
annotate entity ZRAP_C_TRAVEL_### with { ... }
```
**결과** OData `UI.HeaderInfo`. 목록 표 위에 "Travels (25)", 객체 페이지 위에 "Travel / 00000012 / 설명"이 보입니다.
**자주 하는 실수** late numbering 때문에 새 draft의 `TravelID`가 비어 제목이 비어 보임 → `description`에 `Description`을 넣어 두면 덜 어색합니다.
**쓰는 문제** R-01, R-05, R-09

### @UI.presentationVariant
**하는 일** 결과를 어떻게 보여 줄지(정렬, 그룹, 최대 건수, 표/차트) 정합니다. 한정자 없이 하나 두면 목록의 기본 정렬이 됩니다.
**붙이는 곳** MDE 헤더
**값**

| 속성 | 의미 |
|---|---|
| `sortOrder: [{ by: '요소', direction: #ASC/#DESC }]` | 정렬 (방향 생략 시 오름차순) |
| `groupBy: ['요소']` | 그룹 |
| `visualizations: [{ type: #AS_LINEITEM }]` | 표로 표시 (`#AS_CHART`도 있음) |
| `maxItems: 5` | 표시 최대 건수 |
| `qualifier: 'pv'` | 이름 붙이기 (selectionPresentationVariant, facet에서 참조) |
| `text: '...'` | 변형 이름 |
| `requestAtLeast: ['요소']` | 항상 함께 조회할 요소 (소스 예제에서는 확인 못 함) |

**예시**
```cds
@UI.presentationVariant: [{
  sortOrder: [{ by: 'TravelID', direction: #DESC }],
  visualizations: [{ type: #AS_LINEITEM }]
}]
annotate entity ZRAP_C_TRAVEL_### with { ... }
```
**결과** OData `UI.PresentationVariant`. 앱을 열면 최근 Travel이 위에 옵니다.
**자주 하는 실수** `by`에 DB 컬럼명 사용. 별칭을 쓰세요. `visualizations`를 빼면 표가 안 그려지는 경우가 있습니다.
**쓰는 문제** R-01, R-05

### @UI.selectionVariant
**하는 일** 미리 정해 둔 필터 조건(보기)을 정의합니다. 혼자서는 잘 안 쓰이고 `selectionPresentationVariant`로 묶어 씁니다.
**붙이는 곳** MDE 헤더
**값**

| 속성 | 의미 |
|---|---|
| `qualifier` | 이름 |
| `text` | 보기 제목 |
| `filter` | 조건 문자열 (예: `'OverallStatus EQ ''O'''`) |

**예시** (피처 쇼케이스 형식)
```cds
@UI.selectionVariant: [{
  qualifier: 'svOpen',
  text: 'Open Travels',
  filter: 'OverallStatus EQ ''O'''
}]
```
**결과** OData `UI.SelectionVariant`.
**자주 하는 실수** 문자열 안 따옴표 이스케이프. 피처 쇼케이스는 숫자 조건(`'CriticalityCode GE 0 and CriticalityCode LE 2'`)만 보여 주므로 문자 상수 이스케이프는 실제 시스템에서 확인 필요.
**쓰는 문제** (선택) R-06

### @UI.selectionPresentationVariant
**하는 일** selectionVariant(조건)와 presentationVariant(보기 방식)를 하나로 묶습니다. 객체 페이지 표 facet(`#SELECTIONPRESENTATIONVARIANT_REFERENCE`)에서도 씁니다.
**붙이는 곳** MDE 헤더
**값** `qualifier`, `text`, `presentationVariantQualifier`, `selectionVariantQualifier`
**예시**
```cds
@UI.selectionPresentationVariant: [{
  qualifier: 'spvOpen',
  text: 'Open Travels',
  presentationVariantQualifier: 'pvDefault',
  selectionVariantQualifier: 'svOpen'
}]
```
**결과** OData `UI.SelectionPresentationVariant`. 앱 설정(manifest)에서 여러 표 보기를 탭으로 만들 때 이것을 참조합니다(manifest 설정은 RAP 범위 밖).
**자주 하는 실수** 참조하는 qualifier 이름 오타 → 조용히 무시됨.
**쓰는 문제** (선택) R-06

### @UI.lineItem
**하는 일** 목록 표의 열, 그리고 표 툴바·행 안의 버튼을 정의합니다. 객체 페이지 안의 자식 표 열도 이것으로 정합니다.
**붙이는 곳** MDE 요소 (행 강조용은 MDE 헤더)
**값**

| 속성 | 의미 |
|---|---|
| `position` | 열 순서 |
| `label` | 열 제목 (없으면 요소 라벨) |
| `importance` | `#HIGH` / `#MEDIUM` / `#LOW` — 좁은 화면에서 어떤 열을 남길지 |
| `type` | 아래 표 |
| `dataAction: '액션명'` | `#FOR_ACTION`/`#WITH_ACTION`일 때 BDEF 액션 이름 |
| `invocationGrouping: #CHANGE_SET` | 여러 행 선택 시 액션 호출을 한 변경 집합으로 (`#ISOLATED`는 소스 예제에서는 확인 못 함) |
| `inline: true` | 버튼을 툴바가 아니라 행 안에 |
| `emphasized: true` | 강조 버튼 |
| `isCopyAction: true` | factory 액션을 "복사" 버튼으로 |
| `criticality: '요소'` | 상태 색 (0 중립, 1 빨강, 2 노랑, 3 초록, 5 신규) |
| `criticalityRepresentation` | `#WITHOUT_ICON` / `#WITH_ICON` |
| `value: '요소'` / `valueQualifier` | 표시 값 (연관 경로 가능) / 참조할 fieldGroup·connectedFields 한정자 |
| `url: '요소'` | `#WITH_URL`일 때 링크 주소 요소 |
| `semanticObjectAction` | IBN 이동 액션 |
| `requiresContext: true` | IBN 버튼이 행 선택을 요구 |
| `cssDefault.width: '5em'` | 열 너비 |
| `qualifier` | 같은 엔터티에 표를 여러 개 정의할 때 |

`type` 값:

| 값 | 의미 |
|---|---|
| `#STANDARD` | 보통 데이터 열 (기본값) |
| `#FOR_ACTION` | 액션 버튼 |
| `#WITH_ACTION` | 값을 링크로 보이고 누르면 액션 실행 |
| `#FOR_INTENT_BASED_NAVIGATION` / `#WITH_INTENT_BASED_NAVIGATION` | 런치패드 앱 이동 버튼 / 링크 |
| `#WITH_URL` | 외부 URL 링크 |
| `#AS_DATAPOINT` | `@UI.dataPoint`(별점·진행 막대)로 표시 |
| `#AS_FIELDGROUP` | 여러 필드를 한 열에 |
| `#AS_CONTACT` | 연락처 퀵뷰 |
| `#AS_CHART` | 마이크로 차트 |

**예시**
```cds
annotate entity ZRAP_C_TRAVEL_### with
{
  @UI.lineItem: [
    { position: 10, importance: #HIGH },
    { type: #FOR_ACTION, dataAction: 'acceptTravel', label: 'Accept Travel' },
    { type: #FOR_ACTION, dataAction: 'rejectTravel', label: 'Reject Travel' },
    { type: #FOR_ACTION, dataAction: 'deductDiscount', label: 'Deduct Discount',
      invocationGrouping: #CHANGE_SET }
  ]
  TravelID;

  @UI.lineItem: [{ position: 100, importance: #HIGH,
                   criticality: 'OverallStatusIndicator' }]
  @UI.textArrangement: #TEXT_ONLY
  OverallStatus;
}
```
**결과** OData `UI.LineItem`(`DataField`, `DataFieldForAction`, `DataFieldForAnnotation` 등). 목록에 열이 생기고 표 오른쪽 위에 Accept/Reject 버튼이 생깁니다. 상태 칸이 색으로 표시됩니다.
**자주 하는 실수**
- `dataAction`에 projection BDEF에 `use action`으로 노출하지 않은 액션 이름 → 버튼이 안 보임.
- 액션 버튼을 넣은 요소가 우연히 `@UI.hidden`이면 버튼도 안 보일 수 있음. 키 필드 같은 항상 보이는 요소에 넣으세요.
- 행 전체 색 강조는 요소가 아닌 **헤더**에 `@UI.lineItem: [{ criticality: '요소' }]`.
**쓰는 문제** R-01, R-02, R-05, R-06

### @UI.selectionField
**하는 일** 필터 바에 처음부터 보이는 필터 필드를 정합니다.
**붙이는 곳** MDE 요소
**값** `[{ position: n }]` (배열)
**예시**
```cds
@UI.selectionField: [{ position: 10 }]
TravelID;
@UI.selectionField: [{ position: 20 }]
AgencyID;
```
**결과** OData `UI.SelectionFields`. 필터 바에 Travel ID, Agency ID 입력란이 나오고, 값 도움말이 있으면 F4도 됩니다.
**자주 하는 실수** 값 도움말이 없는 코드 필드를 필터로 둬서 사용자가 코드를 외워야 함.
**쓰는 문제** R-01, R-05

### @UI.hidden
**하는 일** 화면에서 요소를 숨깁니다. OData에는 그대로 남아 프레임워크·다른 어노테이션이 참조할 수 있습니다.
**붙이는 곳** MDE 요소 / 뷰 요소
**값** `true` 또는 `#(불리언 요소)`
**예시**
```cds
@UI.hidden: true
MimeType;
@UI.hidden: true
LocalLastChangedAt;
```
**결과** OData `UI.Hidden`. 열·필드·필터 조정 목록에서 사라집니다.
**자주 하는 실수** `@Consumption.hidden`(OData에서 제거)과 혼동. 가상 요소 `OverallStatusIndicator`처럼 criticality 계산에만 쓰는 필드는 `@UI.hidden`으로 숨겨야 criticality 참조가 살아 있습니다.
**쓰는 문제** R-01, R-02, R-05

### @UI.textArrangement
**하는 일** `@ObjectModel.text.element`/`text.association`으로 연결된 텍스트와 ID를 어떻게 배치할지 정합니다.
**붙이는 곳** MDE 요소 / 뷰 요소
**값**

| 값 | 의미 |
|---|---|
| `#TEXT_FIRST` | `텍스트 (ID)` |
| `#TEXT_LAST` | `ID (텍스트)` |
| `#TEXT_ONLY` | 텍스트만 |
| `#TEXT_SEPARATE` | 텍스트와 ID를 따로 |

**예시**
```cds
@UI.textArrangement: #TEXT_FIRST
CustomerID;
```
**결과** OData `UI.TextArrangement`. 목록·폼에서 `Smith (000123)`처럼 보입니다.
**자주 하는 실수** 텍스트 연결(`@ObjectModel.text.element`) 없이 이것만 붙임 → 효과 없음.
**쓰는 문제** R-01, R-05

### @UI.multiLineText
**하는 일** 긴 문자열을 여러 줄 입력/표시 칸으로 보여 줍니다.
**붙이는 곳** MDE 요소
**값** `true`
**예시**
```cds
@UI.multiLineText: true
Description;
```
**결과** OData `UI.MultiLineText`. 객체 페이지에서 텍스트 영역(textarea)이 됩니다.
**자주 하는 실수** 목록 열에서는 효과가 거의 없습니다. 폼(identification/fieldGroup)에서 보세요.
**쓰는 문제** R-01

### @UI.masked (GitHub 공개 코드에서만 확인)
**하는 일** 입력값을 비밀번호처럼 가려서 표시합니다.
**붙이는 곳** MDE 요소 / 뷰 요소
**값** `true`
**예시**
```cds
@UI.masked: true
ApiKey;
```
**결과** 입력란이 `••••`로 보입니다(실제 시스템에서 확인 필요). 보안 기능은 아니므로 민감한 값은 애초에 서비스에 내보내지 마세요.
**자주 하는 실수** 이걸로 보안이 된다고 생각함. `$metadata`·응답에는 원래 값이 그대로 있습니다.
**쓰는 문제** (참고)

### @UI.updateHidden / @UI.deleteHidden
**하는 일** 객체 페이지·목록의 수정(Edit) 버튼과 삭제 버튼을 숨깁니다. 상수 또는 불리언 요소를 참조합니다.
**붙이는 곳** MDE 헤더
**값** `true` / `false` / `#(불리언 요소)`
**예시** (피처 쇼케이스)
```cds
@UI.updateHidden: #(UpdateHidden)
@UI.deleteHidden: #(DeleteHidden)
annotate entity ZRAP_C_TRAVEL_### with { ... }
```
**결과** OData `UI.UpdateHidden` / `UI.DeleteHidden`. 버튼이 보이지 않습니다.
**자주 하는 실수**
- **권한·기능 제어 대용으로 쓰기.** 버튼만 숨길 뿐 API로는 여전히 수정됩니다. 진짜 제어는 BDEF의 `features : instance`(동적 기능 제어)와 권한 구현으로 하세요.
- `@UI.createHidden`은 GitHub 공개 코드에서 쓰임을 봤지만 SAP 샘플로는 확인하지 못했습니다.
**쓰는 문제** (참고) R-02 — 동적 기능 제어와 비교용

### @UI.adaptationHidden
**하는 일** 키 사용자 UI 조정(UI Adaptation)에서 이 속성을 추가·제거·이동할 수 없게 막습니다.
**붙이는 곳** MDE 요소
**값** `true`
**예시**
```cds
@UI.adaptationHidden: true
Description;
```
**결과** 배포된 앱의 UI 조정 모드와 필터 추가 목록에서 이 필드를 다룰 수 없습니다. ADT 미리보기에서는 대부분 효과를 볼 수 없습니다.
**자주 하는 실수** `@UI.hidden`처럼 화면에서 숨겨진다고 기대함. 보통 표시는 그대로입니다.
**쓰는 문제** (참고)

## 7. UI: 객체 페이지 (Object Page)
객체 페이지는 `@UI.facet`으로 **틀(섹션·헤더 영역)** 을 만들고, 그 틀이 가리키는 **내용**(`@UI.identification`, `@UI.fieldGroup`, `@UI.lineItem`, `@UI.dataPoint`, `@UI.chart`)을 요소마다 붙여 채웁니다.
"facet은 목차, 나머지는 본문"이라고 생각하면 쉽습니다. facet은 보통 MDE의 첫 번째 요소 위에 한 번만 씁니다.

### @UI.facet
**하는 일** 객체 페이지의 헤더 영역과 본문 섹션(탭), 하위 섹션 구조를 정의합니다.
**붙이는 곳** MDE 요소 (관례상 첫 요소 위, 하나의 배열로)
**값**

| 속성 | 의미 |
|---|---|
| `id` | facet ID (`parentId`가 참조) |
| `parentId` | 이 facet이 들어갈 상위 `#COLLECTION`의 id |
| `purpose` | `#STANDARD` 본문(기본) / `#HEADER` 헤더 영역 / `#QUICK_VIEW` 퀵뷰 / `#FILTER` 필터 묶음 |
| `type` | 아래 표 |
| `position` | 순서 |
| `label` | 섹션 제목 |
| `targetQualifier` | 가리킬 fieldGroup·dataPoint·chart·variant의 qualifier |
| `targetElement: '_Booking'` | 다른 엔터티(연관)의 어노테이션을 가리킬 때 |
| `hidden` | `true` 또는 `#(요소)` — 동적으로 숨김 (예: `#(IsActiveEntity)` 편집 중에만 보이기) |
| `isPartOfPreview: false` | 처음엔 접혀 있고 "더 보기"로 열림 |

`type` 값:

| 값 | 무엇을 보여 주나 |
|---|---|
| `#COLLECTION` | 다른 facet을 담는 그릇 (탭/섹션) |
| `#IDENTIFICATION_REFERENCE` | `@UI.identification` 폼 |
| `#FIELDGROUP_REFERENCE` | `@UI.fieldGroup` (qualifier로 지정) |
| `#LINEITEM_REFERENCE` | 연관 엔터티의 `@UI.lineItem` 표 (자식 표) |
| `#DATAPOINT_REFERENCE` | `@UI.dataPoint` (보통 헤더) |
| `#CHART_REFERENCE` | `@UI.chart` (헤더 마이크로 차트 등) |
| `#PRESENTATIONVARIANT_REFERENCE` | 자식 엔터티의 presentationVariant로 정렬된 표 |
| `#SELECTIONPRESENTATIONVARIANT_REFERENCE` | 자식 엔터티의 selectionPresentationVariant 표 |
| `#ADDRESS_REFERENCE` | `@Semantics.address.label` 주소 |

**예시**
```cds
annotate entity ZRAP_C_TRAVEL_### with
{
  @UI.facet: [
    { id: 'TravelHeaderPrice', purpose: #HEADER, type: #DATAPOINT_REFERENCE,
      targetQualifier: 'TotalPrice', position: 10 },
    { id: 'idCollection', type: #COLLECTION, label: 'Travel', position: 10 },
    { id: 'idIdentification', parentId: 'idCollection',
      type: #IDENTIFICATION_REFERENCE, label: 'General Information', position: 10 },
    { id: 'idDates', parentId: 'idCollection',
      type: #FIELDGROUP_REFERENCE, targetQualifier: 'Dates', label: 'Dates', position: 20 },
    { id: 'idBooking', type: #LINEITEM_REFERENCE, label: 'Bookings',
      position: 20, targetElement: '_Booking' }
  ]
  @UI.lineItem: [{ position: 10 }]
  @UI.identification: [{ position: 10 }]
  TravelID;
}
```
**결과** OData `UI.Facets`(`CollectionFacet`, `ReferenceFacet`)와 `UI.HeaderFacets`. 헤더에 총액, 본문에 "Travel" 탭 아래 두 하위 섹션, 그리고 "Bookings" 표 섹션이 생깁니다.
**자주 하는 실수**
- `#LINEITEM_REFERENCE`에 `targetElement`를 빼먹음 → 자기 자신의 lineItem을 찾음.
- 자식 MDE에 `@UI.lineItem`이 없어 빈 표.
- `targetElement`의 연관이 C 뷰에서 `redirected to composition child`로 노출되지 않음.
- `id` 중복.
**쓰는 문제** R-01, R-05, R-09

### @UI.identification
**하는 일** 객체 페이지 기본 폼("일반 정보")에 들어갈 필드와, 객체 페이지 헤더·바닥의 액션 버튼을 정의합니다.
**붙이는 곳** MDE 요소
**값**

| 속성 | 의미 |
|---|---|
| `position`, `label`, `importance` | 폼 순서·라벨 |
| `type: #FOR_ACTION`, `dataAction` | 객체 페이지 헤더(편집 버튼 옆)에 액션 버튼 |
| `determining: true` | 액션 버튼을 페이지 **바닥(footer)** 에 표시 |
| `isCopyAction: true` | 복사 버튼 |
| `criticality`, `criticalityRepresentation: #WITH_ICON` | 버튼·값 색 |
| `type: #AS_DATAPOINT` | 데이터 포인트로 표시 |

**예시**
```cds
@UI.identification: [
  { position: 10, label: 'Travel ID' },
  { type: #FOR_ACTION, dataAction: 'acceptTravel', label: 'Accept Travel' },
  { type: #FOR_ACTION, dataAction: 'rejectTravel', label: 'Reject Travel', determining: true }
]
TravelID;
```
**결과** OData `UI.Identification`. 폼에 Travel ID, 헤더에 Accept 버튼, 바닥 바에 Reject 버튼이 보입니다.
**자주 하는 실수** facet에 `#IDENTIFICATION_REFERENCE`가 없어 폼이 아예 안 보임. 액션 버튼은 facet 없이도 헤더에 나옵니다.
**쓰는 문제** R-01, R-02, R-05

### @UI.fieldGroup
**하는 일** 필드를 이름 붙인 묶음(qualifier)으로 모아, facet `#FIELDGROUP_REFERENCE`로 원하는 위치(본문 하위 섹션, 헤더)에 보여 줍니다.
**붙이는 곳** MDE 요소
**값**

| 속성 | 의미 |
|---|---|
| `qualifier` | 묶음 이름 (facet `targetQualifier`와 같아야 함) |
| `position`, `label` | 순서·라벨 |
| `type: #FOR_ACTION` + `dataAction` | 그 섹션 툴바에 액션 버튼 (`inline: true`면 폼 안) |
| `type: #AS_CONNECTED_FIELDS` + `valueQualifier` | connectedFields를 한 줄로 |
| `type: #AS_CONTACT` + `value: '_Customer'` | 연락처 퀵뷰 |
| `value: '_Child.StringProperty'` | 연관 값을 여러 값 입력란으로 |

**예시**
```cds
@UI.fieldGroup: [{ qualifier: 'Dates', position: 10 }]
BeginDate;
@UI.fieldGroup: [{ qualifier: 'Dates', position: 20 }]
EndDate;
@UI.fieldGroup: [{ qualifier: 'Prices', position: 10 }]
BookingFee;
```
**결과** OData `UI.FieldGroup#Dates`. "Dates" 하위 섹션에 시작일·종료일이 나란히 나옵니다.
**자주 하는 실수** qualifier 대소문자가 facet과 다름 → 섹션이 비어 있음.
**쓰는 문제** R-01, R-05, R-09

### @UI.dataPoint
**하는 일** 하나의 값을 KPI처럼 보여 주는 정의입니다. 헤더 숫자, 별점(#RATING), 진행 막대(#PROGRESS), 마이크로 차트의 측정값에 씁니다.
**붙이는 곳** MDE 요소
**값**

| 속성 | 의미 |
|---|---|
| `qualifier` | 이름. **요소 이름과 같게** 두는 것이 관례(표에서 `#AS_DATAPOINT`가 찾을 수 있도록) |
| `title` | 제목 |
| `visualization` | `#PROGRESS` 진행 막대 / `#RATING` 별점 / `#NUMBER` 숫자 / 생략하면 숫자(Key Value) |
| `targetValue` | 목표값(별 개수, 진행 100%). 상수 또는 `#(요소)` |
| `targetValueElement` | 목표값 요소 (마이크로 차트) |
| `criticality` | 색 요소 |
| `minimumValue` / `maximumValue` | 최소·최대 (차트 렌더링) |
| `forecastValue` | 예측값 (bullet 차트) |
| `criticalityCalculation` | 임계값으로 색 계산 (area 차트) |
| `hidden` | `true` 또는 `#(요소)` |

**예시** (RAP110 Booking 형식)
```cds
@UI: {
  dataPoint: { qualifier: 'RemainingDaysToFlight',
               title: 'Days to Flight',
               criticality: 'DaysToFlightIndicator',
               targetValue: #(InitialDaysToFlight),
               visualization: #PROGRESS },
  lineItem:       [{ type: #AS_DATAPOINT, position: 110, importance: #HIGH }],
  identification: [{ type: #AS_DATAPOINT, position: 110 }]
}
RemainingDaysToFlight;
```
**결과** OData `UI.DataPoint#RemainingDaysToFlight`. 표와 폼에 색깔 있는 진행 막대가 보입니다. 헤더에 두려면 facet `purpose: #HEADER, type: #DATAPOINT_REFERENCE, targetQualifier: 'RemainingDaysToFlight'`.
**자주 하는 실수** qualifier를 요소 이름과 다르게 지어 `#AS_DATAPOINT` 열이 비어 있음(피처 쇼케이스가 "가장 중요"라고 강조한 점).
**쓰는 문제** R-01, R-02

### @UI.chart
**하는 일** 차트를 정의합니다. RAP 트랜잭션 앱에서는 주로 객체 페이지 **헤더의 마이크로 차트**에 씁니다.
**붙이는 곳** MDE 헤더 (차트가 속한 엔터티)
**값**

| 속성 | 의미 |
|---|---|
| `qualifier`, `title`, `description` | 이름·제목 |
| `chartType` | `#BULLET`, `#AREA`, `#COLUMN`, `#LINE`, `#BAR`, `#BAR_STACKED`, `#DONUT`, `#PIE` (피처 쇼케이스에서 확인한 값) |
| `measures: ['요소']` | 측정값 (dataPoint가 있는 요소) |
| `dimensions: ['요소']` | 차원 |
| `measureAttributes: [{ measure, role: #AXIS_1, asDataPoint: true }]` | 측정값 속성 |
| `dimensionAttributes: [{ dimension, role: #CATEGORY }]` | 차원 속성 |

**예시**
```cds
@UI.chart: [{
  qualifier: 'PriceBullet',
  title: 'Total Price',
  chartType: #BULLET,
  measures: ['TotalPrice'],
  measureAttributes: [{ measure: 'TotalPrice', role: #AXIS_1, asDataPoint: true }]
}]
annotate entity ZRAP_C_TRAVEL_### with
{
  @UI.facet: [{ purpose: #HEADER, type: #CHART_REFERENCE, targetQualifier: 'PriceBullet' }]
  @UI.dataPoint: { qualifier: 'TotalPrice', targetValue: 5000, minimumValue: 0 }
  TotalPrice;
}
```
**결과** OData `UI.Chart#PriceBullet`. 헤더에 막대형 마이크로 차트가 보입니다.
**자주 하는 실수** 본문 섹션 차트(`#COLUMN` 등 일반 차트)는 집계(`@Aggregation.default`)가 필요하고, 피처 쇼케이스도 V4 트랜잭션 서비스에서는 주석 처리해 두었습니다. 마이크로 차트부터 연습하세요.
**쓰는 문제** (선택) R-01

### @UI.connectedFields
**하는 일** 의미상 이어진 두 값(이름+성, 값/목표)을 한 라벨 아래 템플릿으로 붙여 보여 줍니다.
**붙이는 곳** MDE 요소
**값** `qualifier`, `groupLabel`, `name`, `template: '{a} / {b}'`
**예시** (rf 계층 Employee)
```cds
@UI.connectedFields: [{ qualifier: 'FullName', groupLabel: 'Full Name',
                        name: 'First', template: '{First} {Last}' }]
FirstName;
@UI.connectedFields: [{ qualifier: 'FullName', name: 'Last' }]
LastName;
```
그리고 표시할 곳: `@UI.fieldGroup: [{ qualifier: 'Name_FG', type: #AS_CONNECTED_FIELDS, valueQualifier: 'FullName' }]` 또는 `@UI.headerInfo.title: { type: #AS_CONNECTED_FIELDS, valueQualifier: 'FullName' }`.
**결과** OData `UI.ConnectedFields#FullName`. "Full Name: John Smith"처럼 보입니다.
**자주 하는 실수** `@UI.lineItem`·`@UI.identification`·헤더 facet에서는 표시되지 않습니다(피처 쇼케이스 설명). 폼(fieldGroup)에서 쓰세요.
**쓰는 문제** (선택) R-11

### @UI.valueCriticality
**하는 일** 값마다 고정된 색(criticality)을 지정합니다. 차트 차원의 색칠에 씁니다.
**붙이는 곳** MDE 요소
**값** `[{ value: '1', criticality: #NEGATIVE }, { value: '3', criticality: #POSITIVE }]` (`#NEGATIVE`, `#CRITICAL`, `#POSITIVE` 확인)
**예시**
```cds
@UI.valueCriticality: [
  { value: 'X', criticality: #NEGATIVE },
  { value: 'O', criticality: #CRITICAL },
  { value: 'A', criticality: #POSITIVE } ]
OverallStatus;
```
**결과** 차트에서 상태별 색이 고정됩니다. 목록 칸 색에는 보통 `criticality` 속성(가상 요소)을 씁니다.
**자주 하는 실수** 목록 칸 색이 바뀔 거라 기대함. 화면별 효과는 실제 시스템에서 확인 필요.
**쓰는 문제** (참고)

### @UI.defaultValue (액션 파라미터)
**하는 일** 액션 파라미터 팝업의 입력란에 기본값을 넣습니다. 상수 또는 액션 대상 엔터티의 요소 값을 참조할 수 있습니다.
**붙이는 곳** 추상 엔터티 요소 (액션 파라미터)
**값** `'상수'` 또는 `#( 'ELEMENT_OF_REFERENCED_ENTITY: 요소' )`
**예시**
```cds
@EndUserText.label: 'Discount parameter'
define abstract entity ZRAP_A_DISCOUNT_###
{
  @EndUserText.label: 'Discount (%)'
  @UI.defaultValue: '10'
  discount_percent : abap.int1;
}
```
**결과** "Deduct Discount" 버튼을 누르면 팝업 입력란에 10이 미리 들어가 있습니다(상수 형식은 소스에서 문자열 설명만 확인 — 숫자 파라미터에 문자열 상수가 받아들여지는지 실제 시스템에서 확인 필요). 엔터티 값을 넣으려면 `#( 'ELEMENT_OF_REFERENCED_ENTITY: OverallStatus' )`.
**자주 하는 실수** 복잡한 계산 기본값은 어노테이션이 아니라 BDEF의 `default function GetDefaultsFor...`로 합니다(클라우드 최신 릴리스).
**쓰는 문제** R-02

## 8. 분석·계층·서비스 정의·기타
집계(분석 표), 트리(계층) 표, 서비스 정의(SRVD)에 붙이는 어노테이션과, 외부 서비스 프록시에서 보게 되는 OData 이름 어노테이션을 모았습니다.
R-11의 계층 문제와 SRVD 작성 단계에서 주로 씁니다. 분석 쿼리(`@Analytics.query`)는 RAP 트랜잭션 앱과 다른 엔진(분석 엔진)이 처리하므로 개념만 알아 두면 됩니다.

### @Aggregation.default
**하는 일** 측정값 요소의 기본 집계 방식을 정합니다.
**붙이는 곳** 요소 (분석용 뷰·프로젝션)
**값**

| 값 | 의미 |
|---|---|
| `#SUM` | 합계 |
| `#MIN` / `#MAX` | 최소 / 최대 |
| `#AVG` | 평균 |
| `#COUNT_DISTINCT` | 서로 다른 값 개수 (`@Aggregation.referenceElement: ['요소']`와 함께) |
| `#NONE` | 집계 안 함 (소스 예제에서는 확인 못 함) |

**예시** (rf `/DMO/C_Travel_ANA`)
```cds
@OData.applySupportedForAggregation: #FULL
define root view entity ZRAP_C_TRAVEL_ANA_###
  provider contract transactional_query
  as projection on ZRAP_R_TRAVEL_###
{
  key TravelID,
      @Aggregation.default: #SUM
      @Semantics.amount.currencyCode: 'CurrencyCode'
      TotalPrice,
      CurrencyCode
}
```
**결과** OData V4 `$apply`(집계) 요청을 받을 수 있게 되고, 분석 표(그룹·합계 행)를 쓰는 Fiori 앱에서 합계가 계산됩니다.
**자주 하는 실수** 옛 DDIC 기반 뷰의 `@DefaultAggregation`을 씀 — 뷰 엔터티에서는 `@Aggregation.default`입니다.
**쓰는 문제** (선택) R-11

### @OData.applySupportedForAggregation
**하는 일** 이 엔터티가 OData `$apply` 집계를 지원함을 선언합니다.
**붙이는 곳** 프로젝션 헤더
**값** `#FULL` (rf에서 확인, 다른 값은 확인 못 함)
**예시** 위 `@Aggregation.default` 예시 참고.
**결과** 분석 표(Analytical Table) 앱이 이 엔터티를 집계할 수 있습니다.
**자주 하는 실수** 트랜잭션 Travel 앱 C 뷰에 붙였다가 draft 동작과 섞여 혼란. 분석용 C 뷰를 따로 만드세요.
**쓰는 문제** (선택) R-11

### @Analytics.dataCategory / @Analytics.query / @AnalyticsDetails.query.axis (분석 모델 — 개념만)
**하는 일** 분석 모델에서 뷰의 역할(차원·큐브)과 분석 쿼리, 쿼리 결과 축을 정합니다.
**붙이는 곳** 뷰 엔터티 헤더 / 요소
**값**

| 어노테이션 | 값 |
|---|---|
| `@Analytics.dataCategory` | `#DIMENSION`, `#CUBE` (rap500에서 확인) |
| `@Analytics.query` | `true` — 분석 쿼리 뷰 |
| `@AnalyticsDetails.query.axis` | `#ROWS`, `#COLUMNS`, `#FREE` (이 중 `#FREE`만 공개 코드에서 확인) |

**예시** (rap500)
```cds
@Analytics.dataCategory: #DIMENSION
@Analytics.internalName: #LOCAL
@ObjectModel.representativeKey: 'CarrierId'
define view entity ZRAP_I_CARRIER_DIM_###
  as select from /dmo/carrier
{
      @ObjectModel.text.element: ['Name']
  key carrier_id as CarrierId,
      name       as Name
}
```
**결과** SAP Analytics Cloud 등 분석 클라이언트용 모델. RAP 트랜잭션 Fiori 앱 화면에는 영향 없음.
**자주 하는 실수** RAP BO 뷰에 붙임. 이 문제집에서는 쓰지 않습니다.
**쓰는 문제** (없음 — 구분용)

### @OData.hierarchy.recursiveHierarchy
**하는 일** 엔터티를 트리(재귀 계층)로 표시하도록, CDS 계층(`define hierarchy`)을 연결합니다.
**붙이는 곳** 뷰 엔터티 헤더 / 프로젝션 (C 뷰)
**값** `[{ entity.name: '계층 CDS 이름' }]`
**예시** (rf `/DMO/C_Employee_HR` 형식)
```cds
define hierarchy ZRAP_I_EMPLOYEE_HN_###
  as parent child hierarchy (
    source ZRAP_I_EMPLOYEE_###
    child to parent association _Manager
    start where Manager is initial
    siblings order by LastName ascending
  )
{
  key Employee,
      Manager
}

@AccessControl.authorizationCheck: #NOT_REQUIRED
@Metadata.allowExtensions: true
@OData.hierarchy.recursiveHierarchy: [{ entity.name: 'ZRAP_I_EMPLOYEE_HN_###' }]
define view entity ZRAP_C_EMPLOYEE_###
  as select from ZRAP_I_EMPLOYEE_###
  association of many to one ZRAP_C_EMPLOYEE_### as _Manager
    on $projection.Manager = _Manager.Employee
{ key Employee, FirstName, LastName, Manager, _Manager }
```
**결과** `$metadata`에 계층 관련 어노테이션(`Aggregation.RecursiveHierarchy` 계열)이 생기고 List Report가 펼치기·접기 되는 트리 표로 보입니다. 계층 CDS는 SRVD에 노출하지 않아도 되고, rf 예제는 C 뷰만 노출합니다.
**자주 하는 실수**
- `define hierarchy`의 키와 C 뷰 키가 다름.
- 트리 표 표시 여부는 Fiori 앱 설정(트리 테이블)에도 달려 있습니다. ADT 미리보기에서 트리가 안 보이면 SAP 문서의 "Implementing Treeviews"를 확인하세요(실제 시스템에서 확인 필요).
- CDS 계층 자체에는 `@Hierarchy.*` 같은 별도 어노테이션을 쓰지 않습니다. 계층 정의는 `define hierarchy ... as parent child hierarchy` **문법**으로 합니다.
**쓰는 문제** R-11

### @OData.entityType.name / @OData.entitySet.name (원격 서비스 프록시에서 보게 됨)
**하는 일** OData 엔터티 유형·엔터티 집합 이름을 지정합니다. 원격 OData 서비스를 소비할 때 ADT의 서비스 소비 모델이 생성하는 추상 엔터티에 붙어 있습니다.
**붙이는 곳** 추상 엔터티 / 뷰 엔터티 헤더
**값** 문자열
**예시** (SAP-samples/btp-abap-cna 생성 코드)
```cds
@OData.entitySet.name: 'A_SupplierText'
@OData.entityType.name: 'A_SupplierTextType'
define root abstract entity ZA_SUPPLIERTEXT {
  key Supplier : abap.char( 10 );
  ...
}
```
**결과** 원격 서비스 쪽 이름과 ABAP 쪽 이름을 연결합니다. 직접 만드는 RAP 서비스에서는 보통 쓰지 않습니다. (로컬 소스 예제에서는 확인 못 하고 GitHub SAP 샘플에서 확인)
**자주 하는 실수** 생성된 이름을 손으로 바꿔 원격 호출이 실패.
**쓰는 문제** (참고) R-08 — 원격 데이터를 커스텀 엔터티로 감쌀 때

### SRVD의 @EndUserText.label / @ObjectModel.leadingEntity.name
**하는 일** 서비스 정의의 설명과, 서비스 바인딩 미리보기에서 시작점으로 쓸 대표 엔터티(leading entity)를 지정합니다.
**붙이는 곳** SRVD (`define service` 앞)
**값**

| 어노테이션 | 값 |
|---|---|
| `@EndUserText.label` | 서비스 설명 |
| `@ObjectModel.leadingEntity.name` | 노출된 엔터티 중 하나의 CDS 이름 |

**예시**
```cds
@EndUserText.label: 'Travel UI Service'
@ObjectModel.leadingEntity.name: 'ZRAP_C_TRAVEL_###'
define service ZRAP_UI_TRAVEL_### {
  expose ZRAP_C_TRAVEL_###    as Travel;
  expose ZRAP_C_BOOKING_###   as Booking;
  expose /DMO/I_Agency_StdVH  as Agency;
  expose /DMO/I_Customer_StdVH as Customer;
}
```
**결과** 서비스 바인딩 엔터티 목록에서 Travel에 작은 "L" 표시가 붙어, 어느 것을 Preview 해야 할지 알기 쉽습니다. OData에는 영향 없음.
**자주 하는 실수** `expose ... as` 뒤의 별칭이 아니라 CDS 이름을 써야 합니다.
**쓰는 문제** R-01, R-05, R-09

## 9. 테스트·문서·어노테이션이 아닌 것
마지막으로 "어노테이션처럼 생겼지만 어노테이션이 아닌 것"과, 뷰 엔터티 이전 방식의 흔적을 정리합니다.
특히 RAP의 **동작**(생성·수정·액션·검증·권한·draft)은 CDS 어노테이션이 아니라 BDEF 문법으로 정의한다는 점을 마지막 표에서 확인하세요.

### "! @testing (ABAP Doc 테스트 관계)
**하는 일** ABAP Unit 테스트 클래스가 어떤 저장소 객체(BDEF, 클래스, CDS)를 테스트하는지 연결합니다. CDS 어노테이션이 아니라 **ABAP Doc 주석**입니다.
**붙이는 곳** 테스트 클래스 정의 바로 위 (ABAP 소스)
**값** `BDEF:이름`, 또는 클래스 이름 등 객체 지정
**예시** (rf `/DMO/BP_R_AGENCYTP_HD` 테스트 클래스 형식)
```abap
"! @testing BDEF:ZRAP_R_TRAVEL_###
CLASS ltc_travel DEFINITION FINAL FOR TESTING
  DURATION SHORT
  RISK LEVEL HARMLESS.
  PRIVATE SECTION.
    METHODS accept_sets_status FOR TESTING.
ENDCLASS.
```
**결과** BDEF(또는 대상 객체)에서 Ctrl+Shift+F10(ABAP Unit 실행)을 해도 이 테스트가 같이 실행됩니다. 화면·OData 영향 없음.
**자주 하는 실수** `"!`와 `@testing` 사이·위치 오류로 연결이 안 됨. 클래스 정의 **바로 위** 줄에 두세요.
**쓰는 문제** R-13

### @AbapCatalog.sqlViewName (옛 DDIC 기반 뷰 — 뷰 엔터티에서는 쓰지 않음)
**하는 일** 옛 CDS DDIC 기반 뷰(`define view`)가 데이터베이스에 만들 SQL 뷰 이름을 지정하던 어노테이션입니다.
**붙이는 곳** (옛) `define view` 헤더
**값** 16자 이하 문자열
**예시**
```cds
// 옛 방식 (쓰지 마세요)
@AbapCatalog.sqlViewName: 'ZVTRAVEL###'
define view ZRAP_OLD_TRAVEL_### as select from zrap_atrav_### { ... }

// 현재 방식: SQL 뷰 이름이 따로 없음
define view entity ZRAP_R_TRAVEL_### as select from zrap_atrav_### { ... }
```
**결과** 뷰 엔터티(`define view entity`)는 별도의 DDIC SQL 뷰를 만들지 않으므로 이 어노테이션이 없습니다. 활성화가 빠르고 이름을 두 개 관리할 필요도 없습니다. `@AbapCatalog.preserveKey`, `@AbapCatalog.compiler.compareFilter`, `@ClientHandling` 같은 것도 옛 뷰 쪽 어노테이션입니다.
**자주 하는 실수** 블로그 예제를 복사해 뷰 엔터티에 넣음 → 허용되지 않는 어노테이션 오류. RAP BO에는 뷰 엔터티만 쓰세요.
**쓰는 문제** (없음 — 구분용)

### BDEF 프라그마 ##DRAFT_OP_NOT_REQUIRED (어노테이션 아님)
**하는 일** BDEF 구문 검사 경고 하나를 끄는 프라그마입니다. rf 싱글턴 예제(`/DMO/I_CarriersLockSingleton_S`)는 `update`/`delete`가 없는 싱글턴 루트에 draft 액션(`Edit`, `Activate` 등)을 선언하면서 이 프라그마를 붙였습니다.
**붙이는 곳** BDEF의 `define behavior for ...` 헤더 끝 (`{` 앞)
**값** 없음 (`##이름`)
**예시**
```bdef
define behavior for ZRAP_I_FEECFG_S_### alias FeeConfigAll
with unmanaged save
draft table zrap_dfeecfgs_###
lock master
total etag LastChangedAtMax
authorization master ( none )
##DRAFT_OP_NOT_REQUIRED
{
  association _Fee { create; with draft; }
  draft action Edit;
  draft action Activate optimized;
  draft action Discard;
  draft action Resume;
  draft determine action Prepare;
}
```
**결과** 화면 변화 없음. 경고만 사라집니다. 경고의 정확한 문구는 소스에서 확인하지 못했습니다 — 프라그마를 지우고 활성화해 ADT가 보여 주는 경고를 직접 읽어 보세요.
**자주 하는 실수** 경고 내용을 확인하지 않고 습관적으로 붙임. 프라그마는 "알고 있고 의도한 것"일 때만 씁니다.
**쓰는 문제** R-09

### BDEF 키워드 ↔ 어노테이션이 아닌 것 (정리 표)
**하는 일** 처음 RAP를 배울 때 "이것도 어노테이션으로 하나?" 헷갈리는 기능을 정리합니다. 아래는 모두 **BDEF(또는 클래스)** 에서 하며 CDS 어노테이션이 아닙니다.
**붙이는 곳** BDEF / 행동 풀 클래스
**값**

| 하고 싶은 일 | 어노테이션? | 실제로 쓰는 것 (BDEF 키워드 등) |
|---|---|---|
| 생성·수정·삭제 허용 | 아님 | `create; update; delete;` |
| 필드 읽기 전용·필수 | 아님 | `field ( readonly ) ...; field ( mandatory ) ...;` |
| 번호 자동 부여 | 아님 | `field ( numbering : managed )`, `late numbering`, `early numbering` |
| draft | 아님 | `with draft;`, `draft table`, `draft action Edit/Activate/Discard/Resume/Prepare` |
| 잠금 | 아님 | `lock master`, `lock dependent by` |
| ETag | 아님 (필드 의미는 `@Semantics.systemDateTime.*`) | `etag master`, `total etag` |
| 권한 | 아님 (읽기 행 제한은 DCL) | `authorization master ( global, instance )` + 클래스 |
| 액션·함수 | 아님 (버튼 표시만 `@UI.lineItem #FOR_ACTION`) | `action`, `function`, `factory action`, `static action` |
| 검증·결정 | 아님 | `validation ... on save`, `determination ... on modify` |
| 동적 기능 제어(버튼 활성/비활성) | 아님 (`@UI.updateHidden`은 숨김일 뿐) | `( features : instance )` + `get_instance_features` |
| 사이드 이펙트(화면 새로 고침) | 아님 | `side effects { field ... affects ... }` |
| 이벤트 | 아님 (페이로드 구조만 추상 엔터티) | `event ... parameter ...` + `RAISE ENTITY EVENT` |
| 필드-컬럼 매핑 | 아님 | `mapping for 테이블 { ... }` |
| 저장 방식 | 아님 | `managed`, `unmanaged`, `with unmanaged save`, `with additional save` |
| 프로젝션에 노출 | 아님 | `use create; use action ...;` |
| 테스트 대상 연결 | 아님 (ABAP Doc) | `"! @testing BDEF:...` |
| 경고 끄기 | 아님 | `##DRAFT_OP_NOT_REQUIRED` 같은 프라그마 |

**예시**
```bdef
managed implementation in class zbp_rap_r_travel_### unique;
strict ( 2 );
with draft;

define behavior for ZRAP_R_TRAVEL_### alias Travel
persistent table zrap_atrav_###
draft table zrap_dtrav_###
lock master
total etag LastChangedAt
authorization master ( instance )
etag master LocalLastChangedAt
late numbering
{
  create; update; delete;
  field ( readonly ) TravelID, OverallStatus, CreatedBy, CreatedAt;
  action ( features : instance ) acceptTravel result [1] $self;
  ...
}
```
**결과** BDEF는 `$metadata`에 `Core.Computed`, `Common.FieldControl`, 액션 정의 등을 **자동으로** 만들어 냅니다. 그래서 같은 효과를 내려고 CDS 어노테이션을 찾을 필요가 없습니다.
**자주 하는 실수** `@UI.hidden`이나 `@UI.updateHidden`으로 수정을 "막았다"고 생각함. API(EML, OData 직접 호출)로는 여전히 수정됩니다.
**쓰는 문제** R-02, R-04, R-05, R-12, R-13

## 출처
아래는 이 탭을 쓰며 실제로 열어 본 자료입니다.
- SAP-samples/abap-cheat-sheets: https://github.com/SAP-samples/abap-cheat-sheets — `15_CDS_View_Entities.md`, `26_ABAP_Dictionary.md`, `33_ABAP_Release_News.md`(어노테이션 변경 이력: enhancement quota, extensibility, ClientHandling, authorizationCheck `#NOT_ALLOWED`, MDE 레이어), `12_AMDP.md`, `14_ABAP_Unit_Tests.md`, `src/zdemo_abap_table_function.ddls.asddls`
- SAP-samples/abap-platform-refscen-flight (ABAP-platform-cloud): https://github.com/SAP-samples/abap-platform-refscen-flight/tree/ABAP-platform-cloud — `src/reuse/`(값 도움말 뷰, 텍스트 뷰, agency 확장성 뷰 `/DMO/R_AgencyTP`, `/DMO/I_AgencyTP`, `/DMO/E_Agency`), `src/reuse/carrier/`(싱글턴, `##DRAFT_OP_NOT_REQUIRED`), `src/hierarchy/`(계층, connectedFields, SRVD leadingEntity), `src/rec/`(fetchValues), `src/ana/`(집계), `src/draft/`(invocationGrouping), 테스트 클래스(`"! @testing`)
- SAP-samples/abap-platform-rap110: https://github.com/SAP-samples/abap-platform-rap110 — `src/zrap110_r_traveltp_sol.ddls.asddls`, `src/zrap110_c_traveltp_sol.ddlx.asddlxs`, `src/zrap110_c_bookingtp_sol.ddlx.asddlxs`, `exercises/ex01/README.md`, `exercises/ex02/README.md`(largeObject 설명)
- SAP-samples/abap-platform-rap-workshops: https://github.com/SAP-samples/abap-platform-rap-workshops — `rap5xx/rap500/README.md`, `rap5xx/rap500/exercises/ex1/README.md`(분석 차원, representativeKey, foreignKey)
- SAP-samples/abap-platform-rap-opensap: https://github.com/SAP-samples/abap-platform-rap-opensap — `week4/unit2.md`(Semantics.currencyCode 오류 메시지), `week5/sources/W5U3_DDLS_zce_rap_agency_####.txt`(커스텀 엔터티)
- SAP-samples/abap-platform-fiori-feature-showcase: https://github.com/SAP-samples/abap-platform-fiori-feature-showcase — `01_general_features.md`, `02_list_report_header.md`, `03_list_report_content.md`, `04_object_page_general.md`, `05_object_page_header.md`, `06_object_page_content.md`, 그리고 ABAP-platform-cloud 브랜치의 `src/*.ddls.asddls`, `src/*.ddlx.asddlxs`
- GitHub 코드 검색으로 존재만 확인한 것 (검색 결과 조각만 열어 봄):
  - https://github.com/SAP-samples/abap-platform-bgpf-appl-log-events-side-effects (`@ObjectModel.sapObjectNodeType.name`)
  - https://github.com/SAP-samples/abap-platform-analytics-data-modeling (`@Semantics.businessDate.*`)
  - https://github.com/SAP-samples/teched2025-AD163 (`@Semantics.uuid`)
  - https://github.com/SAP-samples/btp-abap-cna (`@OData.entityType.name`, `@OData.entitySet.name`)
  - https://github.com/Xexer/abap_rap_blog (`@Search.ranking`, `@UI.createHidden`)
  - https://github.com/glaubertech/SAP-ABAP-Restful (`@ObjectModel.filter.transformedBy`)
  - https://github.com/Icosa2050/ZCDS-Ref-App (`@ObjectModel.sort.transformedBy`, `@Semantics.booleanIndicator`)
  - https://github.com/FioriS4HANARAP/Chapter-4-5-6-CDS-ABAP-backend-code (`@Consumption.filter.selectionType`, `multipleSelections`, `mandatory`)
  - https://github.com/jasper07/Teched17 (`@UI.masked`)
  - https://github.com/Code-Moises/SAP-RAP-HOTEL-MANAGEMENT (`distinctValues`)
  - https://github.com/hardyp/ABAPToTheFuture04 (`@ObjectModel.compositionRoot`, `@OData.publish` 옛 방식)
