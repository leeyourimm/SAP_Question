# 04. SAPUI5 · Fiori

SAPUI5 프레임워크와 SAP Fiori(런치패드, Fiori Elements, 배포) 서면 시험 대비 통합 문제. 원본 문제(06 UI5·Fiori, 10 손코딩 14단원, 11 UI5·Fiori 문제 은행, 13 모의고사 3회)를 주제별로 묶어 한 문제 안에서 여러 각도로 묻는다. 별도 언급이 없으면 UI5 1.120 이상, `data-sap-ui-async="true"`, `compatVersion="edge"`(복합 바인딩 구문 사용 가능), 모듈 맨 앞 `"use strict"` 환경을 가정한다.

## 1. Fiori 개념 · 런치패드 · 배포

### D-001. Fiori란 무엇인가: 디자인 원칙, 기술, 앱 유형, 테마 [개념] ★
<!-- src: U5-001, UB-001, UB-002, MX-069, UB-018, UB-011, UB-016 -->
면접 첫 질문 "SAPUI5와 Fiori는 같은 것인가?"부터 시작해 Fiori의 기본 개념을 정리한다.

(1) SAPUI5, OpenUI5, SAP Fiori 세 용어를 각각 정의하고 서로의 관계를 쓰시오. "Fiori = UI5"라고 답하면 왜 감점인지도 쓰시오.
(2) SAP Fiori 디자인 원칙 5가지를 쓰고 각각 한 줄로 설명하시오.
(3) OpenUI5만으로 개발할 때 사용할 수 **없는** 것을 모두 고르시오.
① `sap.m.Table` ② `sap.ui.table.TreeTable` ③ `sap.ui.comp.smarttable.SmartTable` ④ `sap.f.FlexibleColumnLayout` ⑤ `sap.uxap.ObjectPageLayout` ⑥ `sap.viz.ui5.controls.VizFrame`
(4) 전통적인 Fiori 앱 3가지 유형(Transactional, Analytical, Fact sheet)을 설명하고, 다음 중 **옳지 않은** 것을 모두 고르시오.
① Transactional 앱은 생성·변경·승인 같은 업무 처리를 하며 일반 DB에서도 동작한다.
② Analytical 앱은 KPI와 실시간 분석을 보여 주며 SAP HANA의 분석 기능(VDM 등)을 활용한다.
③ Fact sheet 앱은 S/4HANA에서 Fiori Elements의 List Report로 대체되었다.
④ Analytical List Page는 거래 처리용 floorplan이므로 draft가 켜진 BO에서만 쓸 수 있다.
⑤ Overview Page는 여러 데이터 소스의 정보를 카드 형태로 한 화면에 보여 준다.
⑥ 오늘날에는 구현 방식으로 freestyle 앱과 Fiori Elements 앱을 구분하는 경우가 많다.
(5) UI5 테마에 대한 설명으로 옳지 않은 것을 고르고, 런타임에 테마를 바꾸는 API를 쓰시오.
① 최신 Fiori 테마는 Horizon(`sap_horizon`, `sap_horizon_dark` 등)이다.
② bootstrap의 `data-sap-ui-theme` 또는 URL 파라미터 `sap-theme`로 테마를 지정할 수 있다.
③ 고객 브랜드 색은 UI Theme Designer로 커스텀 테마를 만들어 적용한다.
④ 커스텀 CSS에서 색을 하드코딩하는 대신 `sapThemeHighlight-asColor` 같은 테마 파라미터 클래스를 쓰면 테마가 바뀌어도 어울린다.
⑤ 테마를 바꾸려면 모든 뷰 XML의 `class` 속성을 테마 이름으로 고쳐야 한다.
(6) 표준 Fiori 앱(예: Manage Purchase Orders)을 도입할 때 SAP Fiori Apps Reference Library에서 확인하는 정보를 4가지 이상 쓰고, 이후 작업 순서를 쓰시오.

<details><summary>정답·해설</summary>

**(1)**
- **SAPUI5**: SAP의 HTML5/JavaScript UI 프레임워크(컨트롤 라이브러리, MVC, 데이터 바인딩, 라우팅, OData 모델). SAP 제품 라이선스에 포함되어 배포된다.
- **OpenUI5**: SAPUI5의 오픈소스 버전(Apache 2.0). 핵심(`sap.ui.core`, `sap.m`, `sap.f`, `sap.ui.table`, `sap.uxap`, `sap.ui.mdc` 등)은 같지만 `sap.ui.comp`(Smart 컨트롤), `sap.viz`(차트), `sap.suite.*` 같은 일부 라이브러리는 SAPUI5에만 있다.
- **SAP Fiori**: SAP의 UX 디자인 시스템(디자인 원칙, 가이드라인, floorplan, 런치패드). "어떤 화면을 어떻게 보여 줄지"에 대한 규칙이다.
- 관계: Fiori 앱은 주로 SAPUI5로 구현한다(freestyle 또는 Fiori Elements). Fiori는 디자인·사용자 경험, SAPUI5는 그것을 만드는 기술 중 하나다. Fiori 가이드라인은 UI5 외에 SAP GUI(Belize/Quartz 테마), iOS/Android SDK에도 적용된다. UI5로 만들어도 가이드라인을 따르지 않으면 "Fiori 앱"이라 부르기 어렵다. 그래서 둘을 같다고 하면 감점이다.

**(2)** (순서 무관, 5개 모두)
1. **Role-based(역할 기반)**: 사용자의 역할에 맞는 앱과 정보만 제공. 거대한 트랜잭션 하나 대신 역할별 작은 앱.
2. **Adaptive(적응형)**: 데스크톱·태블릿·폰 등 기기, 화면 크기, 사용 상황에 맞게 바뀐다(반응형, 밀도 cozy/compact).
3. **Simple(단순)**: 한 앱은 한 가지 업무에 집중(1:1:3 — 한 사용자, 한 유스케이스, 세 화면 정도), 꼭 필요한 기능만.
4. **Coherent(일관성)**: 같은 디자인 언어, 상호작용 패턴(floorplan), 용어를 써서 하나의 제품처럼 느껴진다.
5. **Delightful(즐거움)**: 효율적으로 일하면서 만족감을 느끼도록 정서적 경험까지 고려.

**(3)** ③, ⑥. Smart 컨트롤(`sap.ui.comp`), VizFrame 차트(`sap.viz`), `sap.suite.*`는 SAPUI5 전용이다. OpenUI5에서 비슷한 기능이 필요하면 `sap.ui.mdc` 기반 컨트롤이나 직접 구성한 테이블·필터바를 쓴다.

**(4)** 유형: Transactional = 업무 처리(생성·변경·승인), Analytical = KPI·분석, Fact sheet = 업무 객체 핵심 정보 요약 + 연관 객체로 이동하는 조회용 앱.
옳지 않은 것: ③, ④.
- ③ Fact sheet는 S/4HANA에서 주로 **Object Page**가 이어받았다. List Report는 목록·검색 floorplan이다.
- ④ ALP는 차트와 테이블을 함께 보며 분석·드릴다운하는 floorplan이다. draft와 무관하고 보통 집계 가능한(analytical) 서비스를 쓴다. 거래 처리는 List Report + Object Page가 대표적이다.
- ⑥은 현재 실무 구분(직접 코딩하는 freestyle과 어노테이션 기반 Fiori Elements)이다.

**(5)** ⑤. 테마는 라이브러리별 CSS(`library.css`)와 테마 파라미터로 적용되며 뷰를 고칠 필요가 없다. 런타임 변경: `Theming.setTheme("sap_horizon_dark")`(`sap/ui/core/Theming`, 이전 `sap.ui.getCore().applyTheme`). 커스텀 CSS는 manifest `sap.ui5.resources.css`에 등록하고 테마 색 클래스를 쓴다(Walkthrough Step 14).

**(6)** (예시 4가지 이상)
- App ID(예: F0842A)와 앱 유형(transactional/analytical, Fiori Elements/freestyle)
- 필요한 백엔드·프런트엔드 버전(S/4HANA 릴리스, SAPUI5 버전), 사전 요구 SAP Note
- 활성화할 OData 서비스 이름과 버전
- BSP/ICF 노드 이름, 컴포넌트 ID
- 표준 business role, business catalog, target mapping의 semantic object-action
- 확장 가능 지점(extension points), 지원 기기

작업 순서: "Implementation Information" 탭 확인 → `/IWFND/MAINT_SERVICE`로 서비스 활성화 → ICF 활성화 → 표준 역할 복사·배정. Task list `SAP_FIORI_CONTENT_ACTIVATION`(`STC01`)으로 한꺼번에 활성화하기도 한다.

</details>

---

### D-002. 런치패드 구성 요소: catalog·role·space·page·group과 설정 계층 [개념] ★★
<!-- src: U5-002, UB-009, MX-070, UB-008, MX-097, UB-003 -->
S/4HANA 온프레미스 임베디드 런치패드에서 RAP OData V4 기반 앱 `ZTRAVEL`을 사용자에게 열어 주려 한다.

(1) tile, target mapping, business catalog, group, space, page, business role(PFCG 역할)의 의미를 쓰고, 사용자부터 앱까지의 연결 관계를 한 줄로 쓰시오.
(2) "catalog = ____, space/page(예전 group) = ____"의 빈칸을 채우고, catalog에 없는 앱을 page에 배치하면 어떻게 되는지 쓰시오.
(3) 사용자가 앱을 열고 데이터를 읽게 하려면 PFCG 롤에 들어가야 할 것 **2개**를 고르고, 하나만 있을 때의 증상을 각각 쓰시오.
① 앱 타일과 target mapping이 든 business catalog ② 해당 OData 서비스(서비스 그룹)에 대한 S_SERVICE 권한 ③ S_DEVELOP ④ SAP_ALL 프로필 ⑤ SE11의 S_TCODE 권한
(4) classic(groups) 모드와 spaces & pages 모드를 화면 구성 단위, 역할과의 연결, 관리자의 통제 범위 측면에서 비교하고, spaces·pages가 권장되는 이유와 켜는 설정 트랜잭션을 쓰시오.
(5) `/UI2/FLPD_CUST`와 `/UI2/FLPD_CONF`의 차이(적용 범위, 이송 요청 종류, 우선순위)를 쓰시오. 개인화까지 포함한 덮어쓰기 순서도 쓰시오.
(6) 트랜잭션과 용도를 짝지으시오(틀린 짝 하나를 찾아 바르게 고치시오).

| 트랜잭션 | 용도 |
|---|---|
| `/UI2/SEMOBJ` | 고객 semantic object 정의 |
| `/UI2/FLPD_CUST` | Launchpad Designer, client-specific 설정 |
| `/UI2/FLPCM_CONF` | Launchpad Content Manager, cross-client 설정 |
| `/UI2/FLIA` | OData 서비스를 Gateway에 등록하고 활성화 |
| `/IWFND/ERROR_LOG` | Gateway(프런트엔드) OData 오류 로그 |

<details><summary>정답·해설</summary>

**(1)**
- **tile**: 런치패드에서 앱을 여는 시각적 진입점(정적/동적 타일, 링크).
- **target mapping**: intent(semantic object + action)를 실제 앱(UI5 컴포넌트, 트랜잭션 등)에 연결하는 정의. 타일을 누르면 어떤 앱이 열릴지 결정.
- **business catalog**: 타일과 target mapping의 묶음. 역할에 할당되어 "실행할 수 있는 앱(권한)"을 정한다.
- **group**: 예전 홈 화면 배치 단위(타일 묶음). space/page로 대체 중.
- **space / page**: space(상단 탭) 안에 page, page는 section 안에 타일·링크를 배치. "무엇이 어디에 보이는가(레이아웃)".
- **business role(PFCG)**: catalog와 space(또는 group)를 사용자에게 할당하는 단위. 백엔드 권한(S_SERVICE 등)도 함께 넣는다.
- 연결: 사용자 → 역할 → (catalog: 실행 가능한 앱) + (space → page → section → tile: 보이는 배치) → intent → target mapping → 앱.

**(2)** catalog = **권한(어떤 앱을 쓸 수 있나)**, space/page/group = **레이아웃(어디에 보이나)**. page에 배치할 수 있는 앱은 롤의 catalog 안에 있는 앱으로 제한되며, catalog에 없는 앱은 배치해도 사용자가 실행할 수 없다. 앱 실행에는 이와 별도로 OData 서비스 권한(S_SERVICE)과 업무 권한이 필요하다.

**(3)** ①, ②. catalog(+space)는 "무엇이 보이고 실행되는가", S_SERVICE는 "서비스를 호출할 수 있는가"를 정한다. 데이터 수준 권한은 그다음 CDS DCL과 RAP 권한 구현(authorization master)이 검사한다.
- catalog만 있음: 타일은 보이고 앱은 열리지만 서비스 호출이 403으로 실패.
- S_SERVICE만 있음: 타일이 보이지 않는다.

**(4)**
- **Classic(groups)**: 홈 화면 = 그룹 목록. 그룹은 catalog의 타일을 모은 단위이고 PFCG 역할에 group을 넣는다. 사용자가 그룹을 자유롭게 추가·삭제·정렬해 사용자마다 화면이 달라지고, 그룹이 많으면 초기 로딩이 느리다. catalog 권한과 배치가 섞여 관리가 어렵다.
- **Spaces & pages**: space → page → section → 타일/링크. 관리자가 page 레이아웃을 설계하고 space를 역할 메뉴(Launchpad Space)에 배정해 역할별로 같은 화면 구조를 설계·전송한다. 타일은 여전히 역할의 catalog에서만 고를 수 있고, 사용자는 "My Home" 등 허용 범위에서만 개인화한다.
- S/4HANA 2020부터 spaces 모드 권장, `/UI2/FLP_CUS_CONF`(클라이언트별)에서 켠다. 관리 앱: Manage Launchpad Spaces/Pages. 두 모드 모두 "catalog = 권한, group/page = 레이아웃" 분담은 같다.

**(5)** `_CONF`(configuration) = **cross-client**, **workbench 요청**에 기록. `_CUST`(customizing) = **client-specific**, **customizing 요청**에 기록. 같은 객체를 `_CUST`에서 바꾸면 그 클라이언트에서만 그 변경이 우선한다. 덮어쓰기 순서: SAP 기본 → CONF → CUST → 사용자 개인화(personalization, 가장 위). Content Manager(`/UI2/FLPCM_CONF`, `/UI2/FLPCM_CUST`)도 같은 구분.

**(6)** 틀린 짝: `/UI2/FLIA`. 이것은 런치패드 **intent analysis** 도구로, 사용자·역할 기준으로 어떤 intent가 어떤 target mapping과 catalog로 해석되는지 점검한다. 서비스 등록·활성화는 `/IWFND/MAINT_SERVICE`(V4는 `/IWFND/V4_ADMIN`).

</details>

---

### D-003. 앱을 타일로 등록하고 intent로 이동하기, 문제 해결 [개념] ★★
<!-- src: UB-004, UB-005, U5-003, UB-006, UB-012, MX-071, UB-007 -->
BAS에서 개발한 freestyle 앱을 ABAP 저장소에 BSP `ZTRAVEL_MNG`로 배포했다. manifest 일부는 다음과 같다.

```json
"sap.app": {
  "id": "zdemo.travel.manage",
  "type": "application",
  "crossNavigation": {
    "____(가)____": {
      "manageTravel": {
        "semanticObject": "ZTravel", "action": "manage",
        "title": "{{appTitle}}",
        "signature": { "parameters": {}, "additionalParameters": "allowed" }
      }
    }
  }
}
```

(1) 빈칸 (가)를 채우고, 이 선언의 의미를 쓰시오.
(2) 사용자가 이 앱을 런치패드 타일로 열 수 있게 하는 작업 7단계를 순서대로 쓰시오(트랜잭션 포함, OData 서비스 활성화 포함).
(3) Launchpad Designer에서 target mapping을 만들 때 다음 표를 채우시오. URL과 ID를 바꿔 쓰면 어떤 오류가 나는가?

| Semantic Object | Action | Application Type | URL | ID |
|---|---|---|---|---|
| (a) | (b) | (c) | (d) | (e) |

(4) 다음 URL로 앱이 열렸다. semantic object, action, 시작 파라미터와 값, 앱 내부 라우터가 받는 해시를 쓰고, 컴포넌트에서 시작 파라미터를 읽는 코드와 그 값의 형태를 쓰시오.
```
https://host/sap/bc/ui2/flp?sap-client=100#SalesOrder-display?SalesOrder=27&sap-ui-tech-hint=UI5&/items/10
```
(5) 런치패드 안에서 실행 중인 앱에서 semantic object `Travel`, action `approve` 앱을 `TravelID=42`와 함께 여는 코드의 빈칸을 채우고, 만들어지는 URL 해시를 쓰시오.
```js
sap.ui.require(["sap/ushell/Container"], async (Container) => {
  const oNav = await Container.____(1)____("____(2)____");
  await oNav.navigate({
    ____(3)____: { semanticObject: "Travel", action: "approve" },
    ____(4)____: { TravelID: "42" }
  });
});
```
(6) 앱끼리 URL을 하드코딩하지 않고 intent로 이동하는 이유, 1.120 이전 API, 로컬(런치패드 밖) 실행 시 주의점을 쓰시오.
(7) 다음 두 증상의 원인 후보와 확인 도구(트랜잭션)를 각각 쓰시오. (A) 홈 화면에 타일이 보이지 않는다. (B) 타일은 보이는데 누르면 "Could not open app" 또는 빈 화면이 뜬다.

<details><summary>정답·해설</summary>

**(1)** `inbounds`. 앱이 받을 수 있는 intent(`#ZTravel-manage`)를 선언한 것. BTP 런치패드나 descriptor 기반 도구는 이 값을 읽어 target mapping을 자동 생성하기도 한다(BTP Work Zone 등록 시 필요).

**(2)**
1. **OData 서비스 활성화**: V2는 `/IWFND/MAINT_SERVICE`에서 등록, V4는 `/IWFND/V4_ADMIN`에서 service group 게시. `SICF`에서 `/sap/bc/ui5_ui5/sap/ztravel_mng` 노드 활성 확인.
2. **Semantic object 생성**: `/UI2/SEMOBJ`(예: `ZTravel`). 표준 것을 쓰면 생략.
3. **Business catalog 생성**: `/UI2/FLPD_CUST`(또는 `_CONF`, Content Manager `/UI2/FLPCM_*`).
4. **Target mapping**(catalog 안): semantic object + action → 앱 유형 SAPUI5 Fiori App, URL, ID.
5. **Tile**(catalog 안): 같은 semantic object/action을 지정한 static 또는 dynamic App Launcher.
6. **화면 배치**: spaces & pages 모드면 page/space에, classic이면 group에 타일 추가.
7. **PFCG 역할**: 역할 메뉴에 catalog(+space 또는 group)를 넣고 사용자 배정, `S_SERVICE` 권한 포함.

타일과 target mapping은 intent(semantic object + action)로 연결된다. 흔한 실수: catalog만 넣고 space/group을 빠뜨려 "앱 찾기에는 있는데 홈에는 없다", `S_SERVICE`를 빠뜨려 데이터가 403.

**(3)** (a) `ZTravel` (b) `manage` (c) `SAPUI5 Fiori App` (d) `/sap/bc/ui5_ui5/sap/ztravel_mng` (e) `zdemo.travel.manage`
URL은 BSP 애플리케이션의 ICF 경로(소문자), ID는 BSP 이름이 아니라 **컴포넌트 이름(`sap.app.id`)**이다. 바꿔 쓰면 "Could not open app / Component not found".

**(4)** semantic object `SalesOrder`, action `display`, 시작 파라미터 `SalesOrder = 27`(그리고 런치패드용 `sap-ui-tech-hint = UI5`), 앱 내부 해시 `items/10`.
런치패드 해시 구조는 `#<SemanticObject>-<action>?<파라미터>&/<앱 내부 해시>`이고 `&/` 뒤가 앱 라우터(HashChanger)가 보는 부분이다. 읽기: `this.getComponentData().startupParameters.SalesOrder` → 값은 배열 `["27"]`.

**(5)** (1) `getServiceAsync` (2) `Navigation` (3) `target` (4) `params`. 해시: `#Travel-approve?TravelID=42`.

**(6)** intent로 요청하면 런치패드가 **사용자 역할의 catalog에 있는 target mapping**을 찾아 실제 앱을 결정한다. 같은 intent라도 역할에 따라 다른 앱이 열릴 수 있고, 매핑이 없으면 이동이 실패한다. 1.120 이전에는 `getServiceAsync("CrossApplicationNavigation")`의 `toExternal({ target, params })`를 썼다(현재 deprecated). 런치패드 밖에서는 `sap.ushell.Container`가 없으므로 존재 여부를 확인하거나 FLP sandbox로 실행한다.

**(7)**
(A) 타일 미표시
- PFCG 역할에 catalog/space(또는 group)가 없거나 사용자에게 역할 미배정 → `PFCG`, `SU01`.
- catalog에는 있는데 page/group에 배치 안 함 → Launchpad Designer/Content Manager, Manage Pages 앱.
- 런치패드 캐시 → `/UI2/INVALIDATE_GLOBAL_CACHES`, 브라우저 캐시 삭제.
- 일관성 점검 → `/UI2/FLC`, `/UI2/FLP_CONTCHECK`.

(B) 앱 열기 실패
- tile의 intent와 맞는 target mapping이 없거나 다른(미배정) catalog에 있음 → `/UI2/FLIA`(intent analysis).
- target mapping의 URL/ID(컴포넌트 이름) 오타, ICF 노드 비활성 → `SICF`.
- 앱은 열리나 데이터 오류 → 서비스 미등록·권한 → `/IWFND/MAINT_SERVICE`, `/IWFND/ERROR_LOG`, `/IWBEP/ERROR_LOG`, `SU53`.
- 브라우저 F12 콘솔·네트워크 탭에서 404(Component-preload.js, manifest.json) 확인.
핵심: "타일은 catalog로 권한, page/group으로 표시"를 구분한다.

</details>

---

### D-004. Fiori 시스템 아키텍처와 BTP 연결 경로 [개념] ★★
<!-- src: U5-004, MX-072, UB-097, UB-098 -->
같은 freestyle 앱을 (가) 온프레미스 S/4HANA 런치패드와 (나) SAP BTP Cloud Foundry에서 실행하려 한다.

(1) 온프레미스 Fiori 아키텍처 설명으로 **틀린** 것을 고르고 바르게 고치시오.
① front-end server(FES)에는 UI5 라이브러리, Fiori launchpad, 앱의 UI 리소스(BSP 저장소)가 있다.
② embedded 배포에서는 SAP Gateway 기능(SAP_GWFND)이 백엔드와 같은 시스템에서 동작한다.
③ hub 배포에서는 업무 로직과 OData 서비스 구현(RAP BO, SEGW의 DPC 클래스)이 FES에 있고 백엔드는 DB 역할만 한다.
④ hub 배포에서 FES는 system alias(trusted RFC 연결)로 백엔드의 OData 서비스를 호출한다.
⑤ SAP BTP에서는 SAP Build Work Zone(런치패드)이 front-end 역할을 하고, 온프레미스 백엔드에는 Cloud Connector를 거쳐 접속한다.
(2) BTP에 배포한 앱이 온프레미스 OData를 호출하는 경로를 approuter, `xs-app.json`, destination, Cloud Connector, HTML5 Application Repository를 써서 설명하시오.
(3) 아래 `xs-app.json`의 빈칸을 채우고, route 순서에 관한 규칙을 쓰시오.
```json
{
  "authenticationMethod": "route",
  "routes": [
    { "source": "^/sap/(.*)$", "target": "/sap/$1",
      "____(1)____": "S4H_BACKEND", "authenticationType": "xsuaa", "csrfProtection": false },
    { "source": "^(.*)$", "target": "$1",
      "service": "____(2)____", "authenticationType": "xsuaa" }
  ]
}
```
(4) BTP 연결 구성에 대한 설명으로 **옳지 않은** 것을 고르고 이유를 쓰시오.
① Destination 서비스가 백엔드 URL과 인증 정보를 중앙에서 관리한다.
② Cloud Connector는 온프레미스 쪽에서 BTP로 나가는 보안 터널을 만들므로 방화벽에 인바운드 포트를 열 필요가 없다.
③ approuter의 `xs-app.json` routes가 `/sap/opu/odata/...` 요청을 destination으로 넘긴다.
④ Cloud Connector를 거치는 destination은 ProxyType을 `Internet`으로 설정한다.
(5) 로컬(`http://localhost:8080`)에서 실행하자 OData 요청이 CORS 오류로 실패한다. manifest의 `uri`가 `"https://s4h.example.com:44300/sap/opu/odata/sap/ZTRAVEL_SRV/"`일 때 원인과 올바른 해결 방법(설정 코드 포함)을 쓰시오. 해결책이 아닌 것도 쓰시오.
(6) manifest의 `dataSources.uri`를 상대 경로로 두는 이점을 (2)·(5)와 연결해 한 줄로 쓰시오.

<details><summary>정답·해설</summary>

**(1)** ③. hub 배포에서도 업무 로직과 서비스 구현(모델·데이터 제공 클래스, CDS/RAP)은 **백엔드**에 있다. FES의 Gateway hub에는 서비스 등록(`/IWFND/MAINT_SERVICE`)과 라우팅만 있다. ① FES = UI 계층(런치패드, 테마, UI5, 앱 정적 리소스). ② embedded는 S/4HANA 권장. ④ system alias가 백엔드로 가는 경로. ⑤ 클라우드 런치패드 + Destination + Cloud Connector 조합.

**(2)** 브라우저 → **approuter**(XSUAA 사용자 인증, 세션) → `xs-app.json` route 규칙으로 분배:
- 정적 파일(`index.html`, `Component-preload.js`, manifest 등) → **HTML5 Application Repository**
- `/sap/opu/odata/...` → **destination**(BTP Destination 서비스의 백엔드 URL, 인증 예: PrincipalPropagation) → **Cloud Connector**(고객망 안의 리버스 터널 에이전트) → 온프레미스 S/4HANA.

**(3)** (1) `destination` (2) `html5-apps-repo-rt`. route는 위에서부터 처음 일치하는 것이 적용되므로 catch-all(`^(.*)$`)은 맨 마지막에 둔다. `mta.yaml`에는 HTML5 앱 모듈, 배포용 content 모듈, destination·xsuaa·html5-apps-repo 서비스 인스턴스가 정의된다.

**(4)** ④. Cloud Connector를 거치는 destination은 ProxyType이 **`OnPremise`**이고 URL에는 Cloud Connector에 등록한 가상 호스트를 쓴다. `Internet`은 공개 인터넷 서비스를 직접 부를 때. ②가 Cloud Connector를 쓰는 핵심 이유다.

**(5)** 원인: 브라우저 same-origin policy 때문에 `localhost:8080` 페이지에서 다른 출처(`s4h.example.com:44300`)로 보내는 XHR이 서버의 CORS 허용 헤더 없이 차단된다. 절대 URL은 배포 환경(런치패드, BTP)에서도 맞지 않는다.
해결: ① manifest `uri`를 상대 경로 `"/sap/opu/odata/sap/ZTRAVEL_SRV/"`로 바꾸고, ② 로컬 개발 서버의 프록시가 이 경로를 백엔드로 전달하게 한다.
```yaml
server:
  customMiddleware:
    - name: fiori-tools-proxy
      afterMiddleware: compression
      configuration:
        backend:
          - path: /sap
            url: https://s4h.example.com:44300
            client: "100"
```
브라우저 보안 기능을 끄는 플래그나 백엔드의 무분별한 CORS 허용은 해결책이 아니다. BTP에서는 approuter + destination이 같은 역할을 한다.

**(6)** 실제 호스트는 로컬에서는 프록시, BTP에서는 destination, 온프레미스에서는 같은 출처가 결정하므로 개발·운영 환경이 달라도 코드를 바꾸지 않는다.

</details>

---

### D-005. 배포 방법과 개발 도구(UI5 Tooling, Fiori tools) [개념] ★★
<!-- src: UB-094, MX-073, UB-095, UB-096, U5-045, MX-074 -->
BAS(또는 VS Code + SAP Fiori tools)로 만든 앱 `zdemo.travel.manage`를 배포한다.

(1) UI5 Tooling 설정 파일과 명령의 빈칸을 채우시오.
```yaml
specVersion: "3.0"
metadata:
  name: zdemo.travel.manage
type: ____(1)____
framework:
  name: ____(2)____
  version: "1.120.0"
  ____(3)____:
    - name: sap.m
    - name: sap.ui.core
    - name: themelib_sap_horizon
```
```text
$ ui5 ____(4)____     # 로컬 개발 서버 실행 (기본 http://localhost:8080)
$ ui5 ____(5)____     # 배포용 결과물(Component-preload.js 포함)을 dist 폴더에 생성
```
(2) ABAP 시스템(클라이언트 100)의 패키지 `ZTRAVEL`, 이송 요청 `S4HK900123`, BSP `ZTRAVEL_MNG`로 배포하는 `ui5-deploy.yaml`의 빈칸을 채우시오.
```yaml
builder:
  customTasks:
    - name: ____(6)____
      afterTask: generateCachebusterInfo
      configuration:
        target:
          url: https://s4h.example.com:44300
          ____(7)____: "100"
        app:
          name: ____(8)____
          package: ____(9)____
          transport: ____(10)____
```
(3) 온프레미스 ABAP 저장소 배포 절차(명령, 내부 동작, 대안 리포트, 결과물)와 배포 후 런치패드에 띄우기 위한 작업을 쓰시오.
(4) BTP Cloud Foundry 배포 절차(생성 파일, 빌드·배포 명령, 저장 위치, 라우팅, 런치패드 등록)를 쓰시오.
(5) ABAP 저장소 배포에 대한 설명으로 **옳지 않은** 것을 고르고 이유를 쓰시오.
① UI5 앱은 BSP 애플리케이션 형태로 저장되며 SE80에서 파일을 볼 수 있다.
② 기본 ICF 경로는 `/sap/bc/ui5_ui5/sap/<BSP 이름 소문자>`이다.
③ 리포트 `/UI5/UI5_REPOSITORY_LOAD`로 로컬 폴더의 앱을 업로드·다운로드할 수 있다.
④ 배포 후 새 버전이 안 보이면 `/UI5/APP_INDEX_CALCULATE`로 앱 인덱스를 재계산해 볼 수 있다.
⑤ BSP 이름은 manifest의 `sap.app.id`와 반드시 같아야 하므로 점(.)을 포함할 수 있다.
(6) SAP Fiori tools에 대한 설명으로 **옳지 않은** 것을 고르시오. 그리고 `npm start`가 실행하는 명령을 쓰시오.
① Application Generator로 List Report Page 같은 템플릿에서 앱을 만든다.
② Page Map·Page Editor로 편집하면 결과가 manifest나 어노테이션 파일에 저장된다.
③ Guided Development가 기능(열 추가, 커스텀 액션)을 단계별 안내와 코드 조각으로 넣어 준다.
④ Service Modeler로 OData 서비스의 엔터티·연관·어노테이션 구조를 볼 수 있다.
⑤ Fiori tools는 SAP GUI의 SE80 안에서 실행되는 도구 모음이다.

<details><summary>정답·해설</summary>

**(1)** (1) `application` (2) `SAPUI5`(OpenUI5를 쓰면 `OpenUI5`) (3) `libraries` (4) `serve` (5) `build`
프로젝트 type: `application`, `library`, `theme-library`, `module`. `ui5 build`는 소스를 압축(minify)하고 모듈을 `Component-preload.js`로 번들링해 요청 수를 줄인다.

**(2)** (6) `deploy-to-abap` (7) `client` (8) `ZTRAVEL_MNG` (9) `ZTRAVEL` (10) `S4HK900123`
로컬 패키지(`$TMP`)면 transport가 필요 없지만 다른 시스템으로 이송할 수 없다. 인증 정보는 yaml에 쓰지 말고 환경 변수(`.env`)나 실행 시 입력. BSP 이름은 15자 이하, 고객 네임스페이스(Z/Y 또는 /고객/).

**(3)** `npx fiori add deploy-config`로 `ui5-deploy.yaml` 생성 → `npm run deploy`(`fiori deploy`): `ui5 build`로 `dist` 생성 후 `deploy-to-abap` 태스크가 ADT 서비스(`/sap/bc/adt/filestore/ui5-bsp`)로 BSP 애플리케이션 업로드, 패키지·이송 요청에 기록. 대안: 압축 파일을 리포트 `/UI5/UI5_REPOSITORY_LOAD`(SE38)로 업로드(예전 Web IDE도 같은 서비스로 직접 배포). 결과: BSP 앱 + ICF 노드 `/sap/bc/ui5_ui5/sap/<bsp>`, SAPUI5 앱 인덱스 갱신, 이송 요청으로 품질·운영으로 이동.
런치패드: catalog에 타일·target mapping(semantic object/action → URL·컴포넌트 ID) 생성, 롤에 catalog와 space/page 할당, OData 서비스 권한(S_SERVICE) 부여(D-003 참고).

**(4)** `npx fiori add deploy-config cf`로 `mta.yaml`, `xs-app.json` 생성 → `mbt build`로 `.mtar` → `cf deploy`. 정적 파일은 **HTML5 Application Repository**, 제공·라우팅은 managed approuter(Work Zone/Launchpad 서비스) 또는 standalone approuter(`xs-app.json`), 백엔드는 destination(+Cloud Connector). 런치패드: SAP Build Work Zone Content Manager에서 HTML5 앱을 content provider로 가져와 role·group/catalog/space에 배치하고 사이트에 할당, BTP 역할 컬렉션으로 사용자 배정. manifest `crossNavigation.inbounds` 필요.
공통 핵심: 소스(`webapp`)가 아니라 **빌드 결과(`dist`)**를 배포하고, 배포 정보는 `ui5-deploy.yaml`/`mta.yaml`에 둔다.

**(5)** ⑤. BSP 이름(15자 이하, 점 불가)과 컴포넌트 ID(`sap.app.id`, 점 구분 네임스페이스)는 서로 다르며, target mapping에서 URL(BSP 경로)과 ID(컴포넌트)를 각각 지정해 연결한다. manifest `sap.platform.abap.uri`에 BSP 경로가 기록된다.

**(6)** ⑤. Fiori tools는 SAP Business Application Studio와 VS Code용 확장 기능이다(XML 어노테이션 언어 서버, mock 데이터 미리보기, 배포 설정 생성 등도 제공). `npm start`는 `fiori run --open ...`을 실행하고, 배포는 `npm run deploy`(`fiori deploy`, ABAP 저장소 또는 Cloud Foundry). BAS는 이 도구들이 미리 구성된 클라우드 IDE, 로컬은 VS Code + Fiori tools 확장.

</details>

---

## 2. 프로젝트 구조 · 부트스트랩 · manifest

### D-006. 부트스트랩부터 첫 화면까지, Component.js [코드] ★★
<!-- src: U5-005, UB-013, U5-007, UB-024, UB-025 -->
네임스페이스 `my.travel` 앱의 `index.html`과 `Component.js`다.

```html
<script
  id="____(1)____"
  src="resources/____(2)____"
  data-sap-ui-theme="sap_horizon"
  data-sap-ui-____(3)____='{ "my.travel": "./" }'
  data-sap-ui-____(4)____="true"
  data-sap-ui-compat-version="edge"
  data-sap-ui-____(5)____="module:sap/ui/core/ComponentSupport">
</script>
...
<body class="sapUiBody" id="content">
  <div data-sap-ui-component data-name="my.travel" data-id="container"></div>
</body>
```

```js
sap.ui.define(["sap/ui/core/UIComponent"], (UIComponent) => {
  "use strict";
  return UIComponent.extend("my.travel.Component", {
    metadata: {
      interfaces: ["sap.ui.core.IAsyncContentCreation"],
      manifest: "json"
    },
    init() {
      this.getRouter().initialize();
    }
  });
});
```

(1) 빈칸 (1)~(5)를 채우고, `resource-roots`, `async`, `on-init`(ComponentSupport)의 역할을 각각 쓰시오.
(2) 위 `Component.js`로 실행하면 화면이 비고 콘솔에 TypeError가 난다. 원인과 수정 코드를 쓰고, 컴포넌트·커스텀 컨트롤에서 부모 메서드를 재정의할 때의 규칙을 쓰시오.
(3) `Component.js` 채점 포인트 5가지(클래스 이름, metadata, 인터페이스, init 순서, 라우터)를 쓰시오. 디바이스 모델을 추가하려면 무엇을 쓰는가?
(4) `interfaces: ["sap.ui.core.IAsyncContentCreation"]`를 넣었을 때 달라지는 점 3가지와, 성능 체크리스트가 이를 권장하는 이유를 쓰시오.
(5) 독립 실행(index.html) 방식에서 브라우저가 첫 화면을 표시하기까지 일어나는 일을 7단계로 쓰시오(bootstrap, Component, manifest, 모델, rootView, router, 컨트롤러 훅 포함).
(6) 런치패드에서 실행되면 (5)의 어느 단계가 달라지며, 그래서 앱 설정은 어디에 두어야 하는가?

<details><summary>정답·해설</summary>

**(1)** (1) `sap-ui-bootstrap` (2) `sap-ui-core.js` (3) `resource-roots`(예전 표기 `resourceroots`) (4) `async` (5) `on-init`(예전 표기 `oninit`)
- `resource-roots`: 모듈 이름 접두어(`my/travel/...`)를 실제 URL로 매핑.
- `async="true"`: 라이브러리와 모듈을 비동기로 로드. UI5 권장사항(golden rule)의 기본.
- `on-init`에 `module:sap/ui/core/ComponentSupport`: `data-sap-ui-component`가 붙은 div를 찾아 컴포넌트를 생성. 인라인 스크립트가 없어 CSP 친화적.

**(2)** `init`을 재정의하면서 부모 `UIComponent.prototype.init`을 호출하지 않았다. 부모 init이 manifest의 모델을 만들고 rootView를 생성하며 routing 설정으로 router를 만드는데, 실행되지 않아 rootView가 없고 `this.getRouter()`가 `undefined`라 `initialize`에서 TypeError.
```js
init() {
  UIComponent.prototype.init.apply(this, arguments);   // 반드시 먼저
  this.getRouter().initialize();
}
```
규칙: 컨트롤러 `onInit`과 달리 컴포넌트·커스텀 컨트롤의 `init`, `onAfterRendering` 등을 재정의할 때는 부모 메서드를 `Parent.prototype.<메서드>.apply(this, arguments)`로 호출한다(JavaScript 프로토타입 상속).

**(3)** ① 클래스 이름이 `<namespace>.Component`(`my.travel.Component`) ② `metadata.manifest: "json"`(설정을 manifest에서 읽음) ③ `IAsyncContentCreation` 선언 ④ `UIComponent.prototype.init.apply(this, arguments)`를 **먼저** 호출(빠뜨리면 모델·라우터가 만들어지지 않음) ⑤ `this.getRouter().initialize()`(routing 설정에 따라 해시를 해석하고 첫 화면으로 이동). 디바이스 모델은 `sap/ui/model/json/JSONModel` + `sap/ui/Device`로 만들어 `this.setModel(oDeviceModel, "device")`.

**(4)**
- rootView와 그 안의 중첩 뷰가 **비동기로** 생성된다(rootView에 `async: true`를 따로 지정하지 않아도 됨). `createContent`가 Promise를 반환해도 된다.
- 컴포넌트 생성 Promise는 rootView 생성까지 끝난 뒤 resolve된다.
- 비동기 생성이 강제되어 동기 XHR이 사라지므로 메인 스레드를 막지 않고 리소스를 병렬로 받는다.
성능 체크리스트 항목: "IAsyncContentCreation을 쓰거나 rootView·routing을 async로 설정". 동기 로딩은 페이지를 멈추게 하고, 브라우저 deprecated 경고가 나며 CSP(`unsafe-eval`)와도 충돌한다.

**(5)**
1. index.html이 `sap-ui-core.js`를 bootstrap으로 로드하며 theme, 라이브러리, `resource-roots`, async, `on-init` 설정을 읽는다.
2. 코어 초기화 후 `ComponentSupport`(또는 `ComponentContainer`)가 컴포넌트를 생성한다.
3. 컴포넌트가 manifest.json을 읽고(manifest first) `sap.ui5.dependencies`의 라이브러리를 로드한다.
4. `sap.ui5.models` 정의대로 모델(i18n ResourceModel, OData 모델 등)을 만들어 컴포넌트에 설정한다.
5. `Component.js`의 `init`: 부모 init이 rootView와 router를 만들고, 앱 코드가 `getRouter().initialize()` 호출.
6. 라우터가 현재 해시에 맞는 route의 target 뷰를 rootView 컨테이너(`App`의 `pages`)에 넣는다.
7. 각 뷰 컨트롤러 `onInit` → 렌더링(`onBeforeRendering`/`onAfterRendering`) → 바인딩이 데이터를 요청해 표시.

**(6)** 1~2단계 대신 런치패드가 target mapping의 URL로 컴포넌트를 찾아 직접 생성하므로 index.html은 쓰이지 않는다. 그래서 앱 설정은 index.html이 아니라 **manifest**에 두어야 한다.

</details>

---

### D-007. 프로젝트 파일과 manifest.json 섹션 [코드] ★★
<!-- src: U5-006, UB-020, UB-021, UB-019 -->
OData 서비스를 기본 모델로, i18n 파일을 이름 있는 모델로 선언한 `manifest.json`이다.

```json
{
  "____(1)____": {
    "id": "my.travel",
    "type": "application",
    "____(2)____": {
      "mainService": {
        "uri": "/sap/opu/odata4/sap/zui_travel_o4/srvd/sap/zui_travel/0001/",
        "type": "____(3)____",
        "settings": { "____(4)____": "4.0", "annotations": ["localAnnotations"] }
      },
      "localAnnotations": { "uri": "annotations/annotation.xml", "type": "ODataAnnotation" }
    }
  },
  "____(5)____": {
    "rootView": { "viewName": "my.travel.view.App", "type": "XML", "id": "app" },
    "models": {
      "i18n": {
        "type": "____(6)____",
        "settings": { "bundleName": "my.travel.i18n.i18n" }
      },
      "____(7)____": {
        "____(8)____": "mainService",
        "preload": true,
        "settings": { "operationMode": "Server", "autoExpandSelect": true }
      }
    }
  }
}
```

(1) 빈칸 (1)~(8)을 채우시오.
(2) `sap.app`과 `sap.ui5`가 각각 담는 것을 쓰고, 그 밖의 네임스페이스(`sap.ui`, `sap.fiori`, `sap.platform.abap`, `sap.cloud`)에 무엇이 들어가는지 쓰시오.
(3) 다음 연결 중 **옳지 않은** 것을 고르고 바르게 고치시오.
① 앱 ID, 제목, `dataSources`, `crossNavigation` → `sap.app` ② `rootView`, `models`, `routing`, `dependencies` → `sap.ui5` ③ `deviceTypes`, 아이콘 → `sap.ui` ④ `registrationIds`, `archeType` → `sap.fiori` ⑤ `routing`의 route 목록 → `sap.app`
(4) 모델 키가 `""`일 때와 `"i18n"`일 때 뷰 바인딩 문법을 각각 예로 쓰시오. 모델 `type`을 생략하면 무엇이 선택되는가? 같은 서비스가 V2(`/sap/opu/odata/sap/ZTRAVEL_SRV/`)라면 (4)번 빈칸 값은?
(5) BAS 생성기로 만든 freestyle 앱의 파일 역할 표를 채우시오.

| 역할 | 파일 |
|---|---|
| 앱 descriptor | (a) |
| 컴포넌트 클래스, init에서 라우터 초기화 | (b) |
| 기본 언어 텍스트 | (c) |
| 로컬 테스트용 메타데이터와 mock 데이터 | (d) |
| UI5 Tooling 설정(프레임워크 버전, proxy 미들웨어, 빌드 태스크) | (e) |
| BTP approuter 라우팅 규칙 | (f) |

뷰, 컨트롤러, 포매터, 테스트, 빌드 결과는 각각 어디에 두는가?

<details><summary>정답·해설</summary>

**(1)** (1) `sap.app` (2) `dataSources` (3) `OData` (4) `odataVersion` (5) `sap.ui5` (6) `sap.ui.model.resource.ResourceModel` (7) `""`(빈 문자열 = 기본 모델) (8) `dataSource`

**(2)** `sap.app`: 앱 식별 정보(id, type, 제목)와 데이터 소스(서비스 URL, 어노테이션 파일), crossNavigation — "어디서 무엇을". `sap.ui5`: UI5 고유 런타임 설정(rootView, dependencies, models, routing, contentDensities, resources, extends) — 그 dataSource를 참조해 모델을 만든다. `sap.ui`: 지원 기기(deviceTypes), 아이콘. `sap.fiori`: registrationIds(Fiori 앱 ID), archeType. `sap.platform.abap`: ABAP 저장소 URI(BSP 경로). `sap.cloud`: BTP 서비스 이름, public 여부.

**(3)** ⑤. 라우팅은 UI5 런타임 설정이므로 `sap.ui5.routing`(config, routes, targets)에 둔다.

**(4)** 기본 모델: `{Description}`, `{/TravelSet}`처럼 이름 없이. 이름 있는 모델: `{i18n>title}`처럼 `모델이름>` 접두어. 모델 `type`을 생략하면 dataSource의 `odataVersion`에 따라 `sap.ui.model.odata.v2.ODataModel` 또는 `v4.ODataModel`이 선택된다. V2라면 `"2.0"`(V2는 `settings.localUri: "localService/metadata.xml"`도 흔히 둔다).

**(5)** (a) `webapp/manifest.json` (b) `webapp/Component.js` (c) `webapp/i18n/i18n.properties` (d) `webapp/localService/`(`metadata.xml`, `mockdata/*.json`, mockserver 설정) (e) `ui5.yaml`(로컬 실행용 `ui5-local.yaml`, 배포용 `ui5-deploy.yaml` 등) (f) `xs-app.json`
뷰 `webapp/view/*.view.xml`, 컨트롤러 `webapp/controller/*.controller.js`, 포매터 `webapp/model/formatter.js`, 테스트 `webapp/test/`(unit, integration), 빌드하면 `dist/`에 `Component-preload.js`.

</details>

---

### D-008. 모듈 로딩(sap.ui.define)과 deprecated API 교체 [코드] ★★
<!-- src: U5-008, U5-009, UB-088, MX-082 -->
다음은 오래된 습관이 섞인 컨트롤러다.

```js
sap.ui.define([
  "sap/ui/core/mvc/Controller",
  "sap/ui/model/json/JSONModel",
  "sap/m/MessageToast"
], function (Controller, MessageToast, JSONModel) {
  return Controller.extend("zmx.flights.controller.Main", {
    onInit: function () {
      var oModel = new JSONModel();
      oModel.loadData("model/flights.json");
      this.setModel(oModel, "flight");
      jQuery.sap.require("sap.m.MessageBox");
    },
    onOpen: function () {
      if (!this._oDialog) {
        this._oDialog = sap.ui.xmlfragment("zmx.flights.view.Dialog", this);
        this.getView().addDependent(this._oDialog);
      }
      this._oDialog.open();
      sap.m.MessageBox.show("opened");
    },
    onSearch: function (oEvent) {
      var sQuery = oEvent.getParameter("query");
      var oList = sap.ui.getCore().byId("flightList");
      oList.getBinding("items").filter(
        new sap.ui.model.Filter("carrier", FilterOperator.EQ, sQuery));
      setTimeout(function () {
        MessageToast.show(this.getView().getModel("i18n").getResourceBundle().getText("filtered"));
      }, 0);
    }
  });
});
```

(1) `sap.ui.define`과 `sap.ui.require`의 차이를 쓰시오. `sap.ui.require("sap/m/MessageBox")`처럼 문자열 하나만 주면 어떻게 동작하는가?
(2) AMD 방식이 전역 이름(`sap.m.Button`)이나 `jQuery.sap.require`보다 나은 이유 4가지를 쓰시오. 모듈 경로 표기 규칙도 쓰시오.
(3) 위 코드에서 실행 시 오류가 나거나 권장사항을 어기는 곳을 **8가지 이상** 찾아 이유와 함께 쓰시오(첫 번째 문제는 `new JSONModel()`에서 나는 오류가 무엇인지 구체적으로 쓰시오).
(4) 고친 전체 코드를 쓰시오(`loadFragment`와 `??=` 사용, 빈 검색어면 필터 해제).
(5) 다음 deprecated 동기 factory/API의 대체를 쓰시오: `sap.ui.view`, `sap.ui.component`, `sap.ui.controller`, `sap.ui.xmlfragment`, `sap.ui.getCore().byId`, `jQuery.sap.require`/`sap.ui.requireSync`. 이것들이 언제 제거되며 무엇으로 찾는가?

<details><summary>정답·해설</summary>

**(1)** `sap.ui.define(aDeps, fnFactory)`: **모듈을 정의**한다. 파일당 하나, 최상단. 의존 모듈이 모두 로드되면 factory를 실행하고 반환값이 모듈의 값(export)이 된다. `sap.ui.require(aDeps, fnCallback)`: 모듈을 정의하지 않고 **필요한 모듈을 비동기로 로드해 콜백 실행**(예: 이벤트 핸들러에서 늦게 필요해진 모듈). 문자열 하나만 주면 이미 로드된 경우 그 값을 **동기로** 돌려주고, 없으면 `undefined`.

**(2)** 의존성이 코드에 명시되어 로드 순서 보장 / 비동기 로딩으로 화면이 멈추지 않음 / 전역 네임스페이스 오염 없음 / 빌드 도구가 의존성을 분석해 번들(`Component-preload.js`)을 만들 수 있음. `jQuery.sap.require`와 `sap.ui.requireSync`는 동기 XHR(+eval)을 써서 deprecated, UI5 2.x에서 제거. 모듈 경로는 점이 아니라 슬래시(`sap/m/Button`)로 쓴다. 의존성 배열 순서와 factory 파라미터 순서가 일치해야 한다.

**(3)**
1. 의존성 배열과 파라미터 순서가 다르다. 파라미터는 이름이 아니라 **위치**로 연결되므로 두 번째 인자 `MessageToast`가 실제로는 JSONModel 클래스, 세 번째 `JSONModel`이 실제로는 MessageToast 모듈이다. `new JSONModel()`은 MessageToast 객체를 생성자로 부르므로 **TypeError(생성자가 아님)**, `MessageToast.show`도 실패. → `function (Controller, JSONModel, MessageToast)`.
2. `"use strict"` 누락(권장사항).
3. 컨트롤러에는 `setModel`이 없다 → `this.getView().setModel(oModel, "flight")`(여러 뷰가 쓰면 manifest/컴포넌트에).
4. `"model/flights.json"` 상대 경로는 index.html 기준이라 배포 위치에 따라 깨진다 → manifest `uri` 또는 `sap.ui.require.toUrl("zmx/flights/model/flights.json")`.
5. `jQuery.sap.require`: 동기 XHR + eval → `"sap/m/MessageBox"`를 의존성 배열에.
6. `sap.ui.xmlfragment`: 동기 factory → `this.loadFragment({ name })`(또는 `Fragment.load`).
7. `sap.m.MessageBox`, `sap.ui.model.Filter` 전역 이름 접근: 로드 보장이 없고 권장 위반 → 의존성으로 받은 지역 변수.
8. `FilterOperator`를 불러오지 않음(ReferenceError) → `"sap/ui/model/FilterOperator"` 추가.
9. `sap.ui.getCore().byId("flightList")`: 실제 ID에는 뷰 접두어(`<뷰ID>--flightList`)가 붙어 못 찾고, `getCore`도 1.120부터 deprecated → `this.byId("flightList")`.
10. `setTimeout`의 일반 함수 안 `this`는 컨트롤러가 아님(strict에서 undefined) → 화살표 함수나 `.bind(this)`.
11. (권장) `FilterOperator.EQ`로 빈 검색어면 "빈 값과 같음" 필터가 걸려 전체가 사라짐 → 빈 값이면 `filter([])`. 연산자는 문자열 `"Contains"`도 동작하지만 `FilterOperator` 상수가 안전.

**(4)**
```js
sap.ui.define([
  "sap/ui/core/mvc/Controller",
  "sap/ui/model/json/JSONModel",
  "sap/m/MessageToast",
  "sap/m/MessageBox",
  "sap/ui/model/Filter",
  "sap/ui/model/FilterOperator"
], function (Controller, JSONModel, MessageToast, MessageBox, Filter, FilterOperator) {
  "use strict";
  return Controller.extend("zmx.flights.controller.Main", {
    onInit: function () {
      const oModel = new JSONModel();
      oModel.loadData(sap.ui.require.toUrl("zmx/flights/model/flights.json"));
      this.getView().setModel(oModel, "flight");
    },
    async onOpen() {
      this._oDialog ??= await this.loadFragment({ name: "zmx.flights.view.Dialog" });
      this._oDialog.open();
      MessageBox.show("opened");
    },
    onSearch: function (oEvent) {
      const sQuery = oEvent.getParameter("query");
      const aFilters = sQuery ? [new Filter("carrier", FilterOperator.Contains, sQuery)] : [];
      this.byId("flightList").getBinding("items").filter(aFilters);
      setTimeout(() => {
        MessageToast.show(this.getView().getModel("i18n").getResourceBundle().getText("filtered"));
      }, 0);
    }
  });
});
```
(`loadFragment`가 addDependent까지 하므로 수동 `addDependent`는 불필요.)

**(5)** `sap.ui.view` → `View.create`/`XMLView.create`, `sap.ui.component` → `Component.create`, `sap.ui.controller` → `Controller.create`, `sap.ui.xmlfragment` → `Fragment.load`/`this.loadFragment`, `sap.ui.getCore().byId` → `Element.getElementById`(컨트롤러 안에서는 `this.byId`), `jQuery.sap.require`/`requireSync` → `sap.ui.define` 의존성 또는 비동기 `sap.ui.require`. UI5 2.x에서 제거되는 마이그레이션 대상이며 UI5 linter(`@ui5/linter`, `ui5 lint`)로 찾는다.

</details>

---

## 3. MVC · 생명주기 · 이벤트

### D-009. 컨트롤러 생명주기와 라우팅 시 호출 횟수 [코드] ★★
<!-- src: U5-010, UB-026, UB-027, MX-084, UB-033, UB-032 -->
XML 뷰 `Main`에 `<Text id="txt" text="Hello"/>`와 `<SearchField id="searchField"/>`가 있고 컨트롤러는 다음과 같다.

```js
return Controller.extend("my.app.controller.Main", {
  onInit: function () {
    console.log("1 init", !!this.byId("txt"), !!this.byId("txt").getDomRef());
  },
  onBeforeRendering: function () { console.log("2 before"); },
  onAfterRendering: function () { console.log("3 after", !!this.byId("txt").getDomRef()); },
  onExit: function () { console.log("4 exit"); }
});
```

(1) 뷰가 생성되어 처음 렌더링되고, 한 번 다시 렌더링된 뒤, `oView.destroy()`가 호출되었다. 콘솔 출력을 순서대로 모두 쓰고 각 훅의 호출 시점·횟수·용도를 쓰시오.
(2) 다음 중 옳은 것을 고르시오.
① `onInit`은 뷰가 다시 렌더링될 때마다 호출된다.
② `onBeforeRendering`과 `onAfterRendering`은 뷰가 (재)렌더링될 때마다 호출될 수 있다.
③ `onExit`은 다른 route로 이동할 때마다 호출된다.
④ `onAfterRendering`에서는 아직 DOM이 없으므로 DOM 접근을 하면 안 된다.
(3) `onInit`에 `this.byId("searchField").getDomRef().focus();`를 넣었더니 TypeError가 난다. 원인과 고치는 방법 두 가지(코드 포함)를 쓰시오. DOM을 직접 만지지 않아도 되는 이유도 쓰시오.
(4) 라우트 `list`(pattern `""`)와 `detail`(pattern `"Travel/{id}"`)이 각각 List, Detail 뷰를 타깃으로 하고, 두 컨트롤러 모두 `onInit`에서 자기 라우트에 `attachPatternMatched`를 등록했다(Detail의 핸들러는 `console.log("matched " + id)`, onInit은 `console.log("init")`). 앱 시작 → 상세 id=1 → 뒤로 → 상세 id=2 → 뒤로 순으로 조작했다. (a) Detail 콘솔 출력 순서 (b) Detail `onInit` 횟수 (c) detail 패턴 핸들러 횟수 (d) List `onInit` 횟수 (e) list 패턴 핸들러 횟수 (f) List `onExit` 횟수를 쓰시오.
(5) (4)의 결과에서 "두 번째 상세에 첫 번째 데이터가 보인다"는 버그의 원인과 올바른 코드 위치를 쓰시오.
(6) 컨트롤러 `onExit`에서 정리해야 할 대상 4가지 이상과, 정리하지 않을 때의 문제를 쓰시오. 자동으로 정리되어 따로 destroy할 필요가 없는 것은?

<details><summary>정답·해설</summary>

**(1)**
```text
1 init true false
2 before
3 after true
2 before
3 after true
4 exit
```
- `onInit`: 뷰의 컨트롤이 모두 만들어진 뒤, 렌더링 전에 **한 번**. 그래서 `byId("txt")`는 있지만(true) DOM은 아직 없다(`getDomRef()` → null → false). 모델 설정, 라우터 이벤트 연결 같은 초기화.
- `onBeforeRendering`/`onAfterRendering`: 렌더링될 **때마다**. 재렌더링되면 또 한 쌍. `onAfterRendering`에서는 DOM이 있다.
- `onExit`: 뷰가 destroy될 때 한 번. 이벤트 해제, 타이머 정리.

**(2)** ②. `onInit`(뷰 인스턴스 생성 후)과 `onExit`(destroy 시)은 인스턴스당 한 번. 라우터는 만든 뷰를 캐시해 재사용하므로 route 이동만으로는 `onExit`이 호출되지 않는다. `onAfterRendering`은 DOM이 생긴 뒤다. 재렌더링이 잦을 수 있으므로 무거운 로직이나 이벤트 등록은 `onAfterRendering`에 두지 않는다.

**(3)** `onInit` 시점에는 렌더링 전이라 `getDomRef()`가 `null` → `null.focus()`에서 TypeError.
방법 1: 컨트롤에 렌더링 후 delegate를 붙인다.
```js
onInit() {
  const oField = this.byId("searchField");
  oField.addEventDelegate({ onAfterRendering: () => oField.focus() });
}
```
방법 2: 컨트롤러 `onAfterRendering`에서 `this.byId("searchField").focus()`(재렌더링마다 실행됨에 주의). 라우팅으로 다시 들어올 때마다 필요하면 `patternMatched` 핸들러에서 렌더링 후 처리.
UI5 컨트롤은 `focus()` 메서드를 제공하므로 DOM을 직접 만지지 않아도 된다. DOM 직접 조작은 재렌더링 때 사라진다.

**(4)** (a) `init` → `matched 1` → `matched 2` (b) 1 (c) 2 (d) 1 (e) 3 (f) 0
라우터는 타깃 뷰를 한 번 만들면 캐시해 다시 쓴다. 그래서 `onInit`은 처음 표시될 때 한 번. pattern matched는 해시가 그 라우트에 맞을 때마다(detail은 2·4단계, list는 1·3·5단계). `onExit`은 뷰가 파괴될 때(앱·컴포넌트 종료)만.

**(5)** 파라미터에 따라 데이터를 바꾸는 코드(`bindElement`)를 `onInit`에 두면 뷰가 재사용될 때 다시 실행되지 않는다. `onInit`에서는 `getRoute("detail").attachPatternMatched(this._onMatched, this)`만 한 번 등록하고, 바인딩은 `_onMatched`에서 한다.

**(6)**
- 코드로 만들었지만 뷰의 aggregation/dependent로 넣지 않은 컨트롤(`new Dialog()`, addDependent 안 한 프래그먼트, `new Popover()`) → `destroy()`
- `EventBus.subscribe` 구독 → `unsubscribe`
- `setInterval`/`setTimeout` 타이머 → `clearInterval`/`clearTimeout`
- 다른 객체(전역 모델, 라우터, `window`, `document`)에 붙인 핸들러 → `detach...`/`removeEventListener`
- 컨트롤러가 만든 모델 등 큰 객체 → `destroy()`
문제: 메모리 누수, 다시 뷰를 만들 때 중복 ID 오류, 이미 destroy된 뷰를 참조하는 콜백 실행 오류. `addDependent`로 붙인 컨트롤과 뷰 안의 컨트롤은 뷰 destroy 때 자동 정리된다.

</details>

---

### D-010. MVC 역할, 뷰 ID 접두어와 byId, XML 네임스페이스, 코드 재사용 [코드] ★★
<!-- src: U5-011, U5-012, UB-028, UB-029, UB-030 -->
`Element`는 `sap/ui/core/Element` 모듈이다(`Element.getElementById`는 예전 `sap.ui.getCore().byId`와 같은 전역 ID 조회). 컴포넌트 없이 다음처럼 뷰를 만들었다.

```js
XMLView.create({ id: "main", viewName: "zdemo.app.view.Main" })
  .then(function (oView) { oView.placeAt("content"); });
```

```xml
<mvc:View
  controllerName="____(가)____"
  xmlns="____(나)____"
  xmlns:mvc="____(다)____"
  xmlns:core="____(라)____"
  xmlns:form="____(마)____">
  <Page title="{i18n>title}">
    <form:SimpleForm editable="true">
      <Label text="Name"/>
      <Input id="nameInput" value="{/name}"/>
    </form:SimpleForm>
    <core:Icon src="sap-icon://hello-world"/>
    <Button id="btnSave" text="Save"/>
  </Page>
</mvc:View>
```
(컨트롤러 파일은 `webapp/controller/Main.controller.js`, 앱 네임스페이스 `zdemo.app`)

(1) 빈칸 (가)~(마)를 채우시오. `controllerName`을 쓰는 규칙과 기본 네임스페이스를 고르는 기준도 쓰시오.
(2) 컨트롤러 `onAfterRendering`의 출력 (a)~(d)를 쓰시오.
```js
console.log(this.byId("btnSave").getId());                                       // (a)
console.log(this.getView().createId("btnSave"));                                 // (b)
console.log(Element.getElementById("btnSave"));                                  // (c)
console.log(Element.getElementById("main--btnSave") === this.byId("btnSave"));   // (d)
```
(3) 컨트롤러 안에서 `nameInput`을 얻는 방법으로 가장 적절한 것을 고르고, 나머지가 왜 부적절한지 쓰시오. 컴포넌트 안의 뷰라면 ID가 어떻게 되는가?
① `sap.ui.getCore().byId("nameInput")` ② `this.byId("nameInput")` ③ `document.getElementById("nameInput")` ④ `Element.getElementById("nameInput")`
(4) Model, View, Controller의 책임을 각각 쓰고, XML 뷰를 권장하는 이유를 3가지 이상 쓰시오.
(5) 여러 컨트롤러에서 같은 함수(라우터 얻기, 뒤로 가기, i18n 읽기, 다이얼로그 열기)를 쓰려 한다. 코드 재사용 방법 3가지 이상을 쓰고 BaseController 구조를 설명하시오. 피해야 할 방식도 쓰시오.

<details><summary>정답·해설</summary>

**(1)** (가) `zdemo.app.controller.Main` (나) `sap.m` (다) `sap.ui.core.mvc` (라) `sap.ui.core` (마) `sap.ui.layout.form`
`controllerName`은 파일 경로가 아니라 모듈 이름(점 표기, `.controller.js` 제외). 기본 `xmlns`는 가장 많이 쓰는 라이브러리(보통 `sap.m`).

**(2)** (a) `main--btnSave` (b) `main--btnSave` (c) `undefined` (d) `true`
XML 뷰 안의 컨트롤 ID는 `뷰ID--컨트롤ID`. `this.byId(id)`(= `this.getView().byId(id)`)는 내부에서 `createId`로 접두어를 붙여 전역 조회하므로 짧은 ID로 찾는다. 짧은 ID `"btnSave"`로 전역 조회하면 그런 요소가 없어 `undefined`.

**(3)** ②. ①④는 전역 ID로 찾으므로 접두어 없는 `nameInput`을 못 찾고, ①은 1.119부터 deprecated(대체 `Element.getElementById`). ③은 UI5 컨트롤이 아니라 DOM 요소를 돌려주고 렌더링 전에는 없다. 컴포넌트 안의 뷰라면 ID는 `컴포넌트ID---뷰ID--컨트롤ID`처럼 더 길어진다. 그래서 전역 조회에 ID를 하드코딩하면 안 되고, 같은 뷰를 두 번 띄우면 충돌하거나 다른 인스턴스를 잡는다. 프래그먼트도 뷰 ID 접두어를 주면(`Fragment.load({ id: oView.getId() })` 또는 `this.loadFragment`) `this.byId`로 찾는다.

**(4)**
- **Model**: 데이터 보관과 접근(JSONModel, ODataModel, ResourceModel). 뷰와는 바인딩으로만 연결.
- **View**: 화면 구조(컨트롤 트리) 선언, 로직 없음. XML/JS/HTML/JSON 뷰가 있으나 XML이 표준.
- **Controller**: 이벤트 처리, 뷰·모델 사이 흐름 제어, 생명주기 훅.
XML 뷰 권장 이유: 선언적이라 구조와 로직이 분리되고 읽기 쉽다 / 빌드 시 XML 전처리(템플릿, 캐시) / SAP Fiori tools와 Fiori Elements의 기본 방식 / 디자인 도구·flexibility(UI adaptation) 지원.

**(5)**
1. **BaseController**: `controller/BaseController.js`가 `sap/ui/core/mvc/Controller`를 extend하고 `getRouter()`, `getModel(sName)`, `getResourceBundle()`, `onNavBack()` 같은 공통 메서드를 둔다. 각 컨트롤러는 `sap.ui.define(["./BaseController"], (BaseController) => BaseController.extend("zdemo.app.controller.Main", {...}))`로 상속.
2. **유틸리티/포매터 모듈**: `model/formatter.js`, `util/Helper.js`처럼 일반 객체를 반환하는 모듈을 의존성으로 주입(XML에서는 `core:require`).
3. **Controller extension**(`sap/ui/core/mvc/ControllerExtension`)을 여러 컨트롤러에 붙인다.
4. **Fragment**: 공통 UI 조각 재사용(로직은 사용하는 컨트롤러가 담당).
5. **Component 수준**: 공통 모델·서비스를 컴포넌트에 두고 `this.getOwnerComponent()`로 접근. 다른 앱과는 reuse component/library.
피할 것: 컨트롤러끼리 서로의 인스턴스를 찾아 메서드를 호출(결합도 높음). 화면 간 데이터 전달은 모델, 라우팅 파라미터, EventBus로 한다.

</details>

---

### D-011. 이벤트 처리: 이벤트 객체, 파라미터 전달, 중복 등록, EventBus [코드] ★★
<!-- src: U5-035, UB-031, UB-047, UB-083, UB-079 -->
JSONModel 데이터가 `{ "Products": [ { "ID": "P1", "Name": "Pen" }, { "ID": "P2", "Name": "Ink" } ] }`인 뷰와 컨트롤러다.

```xml
<Button id="btnSave" text="Save" ____(1)____=".onSave"/>
<Input liveChange=".onLiveChange"/>
<Select change=".onSelectChange">
  <core:Item key="EUR" text="Euro"/>
  <core:Item key="USD" text="US Dollar"/>
</Select>
<List id="prodList" items="{/Products}" itemPress=".onItemPress">
  <CustomListItem type="Navigation">
    <Button text="{Name}" press=".onDelete(${ID}, 'X')"/>
  </CustomListItem>
</List>
```

```js
onSave: function (oEvent) {
  var oButton = oEvent.____(2)____();          // 이벤트를 발생시킨 컨트롤
  console.log(oButton.getText());               // "Save"
},
onLiveChange: function (oEvent) {
  var sValue = oEvent.____(3)____("value");     // 현재 입력 문자열
},
onSelectChange: function (oEvent) {
  var sKey = oEvent.getParameter("____(4)____").____(5)____();   // "EUR" 또는 "USD"
},
onDelete(sId, sFlag) {
  console.log(sId, sFlag, typeof sId, this === this.getView().getController());
},
onItemPress(oEvent) {
  const sId = oEvent.getSource().getBindingContext().getProperty("ID");
}
```

(1) 빈칸 (1)~(5)를 채우시오. XML에서 핸들러 이름 앞 점(`.onSave`)의 의미는? 이벤트 이름과 파라미터는 어디에서 확인하는가?
(2) 이벤트 객체를 Promise `then`이나 `setTimeout` 안에서 `oEvent.getSource()`로 쓰면 어떻게 되는지, 어떻게 해야 하는지 쓰시오.
(3) 사용자가 두 번째 행의 버튼을 눌렀을 때 `onDelete`의 콘솔 출력을 쓰고 이유를 설명하시오. 이벤트 객체, 이벤트 파라미터, 소스 컨트롤 속성을 넘기는 문법도 쓰시오.
(4) 목록 항목을 눌렀을 때 `onItemPress`에서 TypeError가 난다. 원인과 수정 코드를 쓰고, 항목 자체의 `press` 이벤트와 비교하시오. 이름 있는 모델이면 무엇을 바꿔야 하는가?
(5) 상세 화면 컨트롤러가 다음과 같다. 상세를 세 번째 열었을 때 저장 버튼을 한 번 누르면 저장 요청이 세 번 간다. 원인과 수정 방법 2가지를 쓰시오. 같은 버그를 만드는 다른 위치도 쓰시오.
```js
onInit() {
  this.getOwnerComponent().getRouter().getRoute("detail").attachPatternMatched(this._onMatched, this);
},
_onMatched(oEvent) {
  this.getView().bindElement("/Travel(" + oEvent.getParameter("arguments").id + ")");
  this.byId("saveBtn").attachPress(this.onSave, this);
}
```
(6) FCL의 목록과 상세처럼 서로 직접 참조하지 않는 두 뷰가 "상세에서 저장됨"을 알리려 한다. 컴포넌트 범위 EventBus로 상세의 publish 코드와 목록의 subscribe/unsubscribe 코드를 쓰고, 주의점 3가지와 공유 모델 방식과의 비교를 쓰시오.

<details><summary>정답·해설</summary>

**(1)** (1) `press` (2) `getSource` (3) `getParameter` (4) `selectedItem` (5) `getKey`
점으로 시작하면 컨트롤러 메서드를 뜻한다(권장). 이벤트 이름과 파라미터는 컨트롤 API 문서의 Events 섹션에 정의되어 있다.

**(2)** 이벤트 객체는 재사용(pool)되므로 핸들러가 끝난 뒤에는 `getSource()`·파라미터 값이 없다. 필요한 값은 핸들러 시작 부분에서 변수에 꺼내 둔다.

**(3)** `P2 X string true`. 괄호로 인자를 쓰면 이벤트 객체 대신 그 값들이 전달된다. `${ID}`는 expression binding 문법으로 **이벤트를 발생시킨 컨트롤의 바인딩 컨텍스트**(`/Products/1`) 기준이라 `"P2"`. 핸들러가 `.`으로 시작하는 컨트롤러 메서드라 `this`는 컨트롤러. 이벤트 객체는 `$event`(`.onDelete($event, ${ID})`), 이벤트 파라미터는 `${$parameters>/...}`, 소스 속성은 `${$source>/text}`.

**(4)** `itemPress`는 **List**의 이벤트라 `getSource()`는 List 자체이고, List에는 행 컨텍스트가 없어 `getBindingContext()`가 `undefined` → TypeError. 눌린 항목은 파라미터 `listItem`.
```js
const oItem = oEvent.getParameter("listItem");
const sId = oItem.getBindingContext().getProperty("ID");
```
항목 자체의 `press`(`<CustomListItem press=".onPress">`)를 쓰면 `getSource()`가 항목이다. 이름 있는 모델이면 `getBindingContext("모델명")`.

**(5)** 뷰가 재사용되어 `_onMatched`가 들어올 때마다 같은 버튼에 같은 핸들러를 추가 등록한다. 세 번 들어오면 핸들러 3개.
- 가장 좋은 방법: XML에 `press=".onSave"`로 선언.
- 코드로 해야 하면 `onInit`에서 한 번만 등록하거나, 등록 전에 `detachPress(this.onSave, this)`로 해제.
`onAfterRendering`에서 `attach*`나 `addEventListener`를 부르는 것도 같은 버그(재렌더링마다 추가).

**(6)**
```js
// 상세: 저장 후
this.getOwnerComponent().getEventBus().publish("travel", "saved", { id: sId });

// 목록
onInit() {
  this.getOwnerComponent().getEventBus().subscribe("travel", "saved", this._onSaved, this);
},
onExit() {
  this.getOwnerComponent().getEventBus().unsubscribe("travel", "saved", this._onSaved, this);
},
_onSaved(sChannel, sEvent, oData) {
  this.byId("list").getBinding("items").refresh();
}
```
EventBus는 publish/subscribe 통로이고, 컴포넌트 범위를 쓰면 같은 앱 안에서만 오간다(런치패드의 다른 앱과 섞이지 않음). 주의: 반드시 구독 해제(누수·중복 호출 방지) / 전역 `sap.ui.getCore().getEventBus()`는 다른 앱과 충돌 가능 / 남용하면 흐름 추적이 어렵다. 비교: 상태(선택 항목, 레이아웃, 편집 모드)는 컴포넌트 수준 공유 JSONModel(`appView`)에 두고 바인딩하는 편이 단순하고, EventBus는 "저장됨" 같은 일회성 사건 알림에 적합하다. 컨트롤러끼리 직접 메서드를 호출하는 방식은 피한다.

</details>

---

## 4. 컨트롤 · Fragment · Dialog · 커스텀 컨트롤

### D-012. 컨트롤 라이브러리, aggregation/association, 리스트·선택 컨트롤, 콘텐츠 밀도 [개념] ★★
<!-- src: U5-013, UB-014, UB-017, UB-039, UB-044, U5-014 -->
(1) 각 컨트롤이 속한 라이브러리(네임스페이스)를 쓰시오. XML 뷰와 manifest에서 라이브러리를 각각 어떻게 선언하는가?

| 컨트롤 | 라이브러리 |
|---|---|
| `ObjectPageLayout` | (a) |
| `FlexibleColumnLayout`, `DynamicPage` | (b) |
| `SimpleForm` | (c) |
| `Grid`, `VerticalLayout` | (d) |
| `SmartFilterBar`, `SmartTable` | (e) |
| Grid Table(`Table`, `TreeTable`) | (f) |
| `Button`, `Input`, `List`, 반응형 `Table`, `Page` | (g) |

(2) 라이브러리 설명으로 **틀린** 것을 고르고 바르게 고치시오.
① `sap.f.FlexibleColumnLayout`은 최대 3열(begin/mid/end)을 보여 주고 `TwoColumnsMidExpanded` 같은 레이아웃 타입으로 열 너비를 바꾼다.
② `sap.ui.table.Table`은 화면이 좁아지면 열을 자동으로 pop-in하는 폰 우선 반응형 테이블이다.
③ `sap.f.DynamicPage`는 스크롤 시 접히는(snap) 헤더를 가진 페이지 레이아웃이다.
(3) 컨트롤 metadata의 aggregation과 association의 차이를 소유권(생명주기), 렌더링, 예시로 쓰고, default aggregation이 XML에서 주는 이점을 쓰시오. 같은 인스턴스를 두 aggregation에 넣으면?
(4) `sap.m.List`에 대해 **옳지 않은** 것을 고르고 이유를 쓰시오. `itemPress`와 항목 `press`에서 눌린 항목을 얻는 방법도 쓰시오.
① `StandardListItem`은 title, description, icon 정도의 고정 레이아웃이다.
② `ObjectListItem`은 number/numberUnit, firstStatus, attributes를 보여 주기 좋다.
③ `CustomListItem`은 `content`에 원하는 컨트롤을 자유롭게 넣는다.
④ `type="Navigation"`은 오른쪽에 화살표를 표시하고 클릭 시 List의 `itemPress`를 발생시킨다.
⑤ 기본 `type`인 `Inactive`에서도 클릭하면 `itemPress`가 발생한다.
(5) 요구사항과 선택 입력 컨트롤의 연결이 가장 적절하지 **않은** 것을 고르고 대안을 쓰시오.
① 5개 고정 값 중 하나, 직접 입력 금지 → `Select` ② 수백 개 값 중 타이핑으로 좁혀 하나 → `ComboBox` ③ 여러 값을 골라 토큰으로 표시 → `MultiComboBox`/`MultiInput` ④ 수만 건 고객 중 조건 검색 후 하나 → `Select`에 전체 고객 바인딩 ⑤ 자유 입력 + 값 도움말 대화상자 → `Input`(`showValueHelp`)
(6) 콘텐츠 밀도 cozy와 compact의 차이를 쓰고, manifest 설정과 코드(Component, App 컨트롤러)로 기기에 맞춰 밀도를 고르는 방법을 쓰시오. 런치패드 안과 다이얼로그에서의 주의점도 쓰시오.

<details><summary>정답·해설</summary>

**(1)** (a) `sap.uxap` (b) `sap.f` (c) `sap.ui.layout.form` (d) `sap.ui.layout` (e) `sap.ui.comp`(`sap.ui.comp.smartfilterbar`, `sap.ui.comp.smarttable`, SAPUI5 전용) (f) `sap.ui.table` (g) `sap.m`(데스크톱·모바일 겸용 기본 반응형 라이브러리)
XML 뷰는 `xmlns:uxap="sap.uxap"`처럼 네임스페이스로, manifest는 `sap.ui5.dependencies.libs`에 넣어야 preload가 효율적으로 동작한다.

**(2)** ②. 열 pop-in(`minScreenWidth`, `demandPopin`)은 `sap.m.Table`의 기능이다. `sap.ui.table.Table`(Grid Table)은 많은 행을 가상 스크롤로 보여 주는 데스크톱 중심 테이블이고 폰에는 권장되지 않는다. FCL은 List-Detail-Detail 패턴에 쓰고 Fiori Elements V4에서도 설정으로 켤 수 있다.

**(3)**
- **aggregation**: 부모가 자식을 **소유**. 자식은 한 부모에만 속하고 부모가 destroy되면 함께 destroy, 보통 부모 렌더러 안에서 렌더링. 예: `Page`의 `content`, `List`의 `items`, `Dialog`의 `beginButton`.
- **association**: 다른 컨트롤을 **ID로 참조**만. 생명주기에 영향 없고 렌더링하지 않음. 예: `Label`의 `labelFor`, `ariaLabelledBy`.
- **default aggregation**: aggregation 태그를 생략할 수 있다. `<Page><Button/></Page>` = `<Page><content><Button/></content></Page>`.
같은 인스턴스를 두 번째 aggregation에 넣으면 첫 부모에서 빠져 옮겨진다. 그래서 리스트 템플릿처럼 여러 번 쓰려면 clone이 필요하다.

**(4)** ⑤. `itemPress`는 항목 `type`이 `Active`, `Navigation`, `DetailAndActive`일 때만 발생한다. 기본 `Inactive`는 클릭에 반응하지 않는다("목록을 눌러도 아무 일도 안 일어난다"의 대표 원인). `itemPress`에서는 `oEvent.getParameter("listItem")`, 항목 `press`에서는 `oEvent.getSource()`.

**(5)** ④. Select는 모든 항목을 한 번에 불러와 렌더링하므로 대량 데이터에 맞지 않고 검색 조건도 넣을 수 없다. JSONModel이면 기본 size limit 100건까지만 표시되는 문제도 있다. 대안: Input + 값 도움말 대화상자(`SelectDialog`, `ValueHelpDialog`)로 서버 검색.

**(6)**
- **cozy**: 컨트롤 크기·간격이 커서 터치에 적합(기본값). **compact**: 작고 촘촘해 마우스·키보드 데스크톱에서 더 많은 정보를 보여 준다.
- manifest `sap.ui5.contentDensities`: `{ "compact": true, "cozy": true }`(앱이 지원하는 밀도 선언).
```js
// Component.js
getContentDensityClass: function () {
  return Device.support.touch ? "sapUiSizeCozy" : "sapUiSizeCompact";
}
// App 컨트롤러 onInit
this.getView().addStyleClass(this.getOwnerComponent().getContentDensityClass());
```
- 런치패드 안에서는 사용자 설정에 따라 셸이 body에 밀도 클래스를 붙인다. 다이얼로그는 static area에 렌더링되므로 `addDependent`를 하거나 `syncStyleClass`로 같은 클래스를 맞춰 준다.

</details>

---

### D-013. sap.m.Table과 sap.ui.table.Table [코드] ★★
<!-- src: UB-034, UB-035, MX-075, UB-036, UB-037, UB-038 -->
JSONModel의 `/Flights` 배열(항공사 `Carrid`, 가격 `Price`, 통화 `Currency`)을 두 종류의 테이블로 보여 준다.

```xml
<!-- (A) 반응형 테이블 -->
<Table id="flightTable" ____(1)____="{/Flights}" mode="____(2)____">
  <columns>
    <Column><Text text="항공사"/></Column>
    <Column minScreenWidth="Tablet" demandPopin="true"><Text text="가격"/></Column>
  </columns>
  <items>
    <____(3)____>
      <cells>
        <Text text="{Carrid}"/>
        <ObjectNumber number="{Price}" unit="{Currency}"/>
      </cells>
    </____(3)____>
  </items>
</Table>
<Button text="선택 확인" press=".onCheck"/>

<!-- (B) 그리드 테이블 -->
<mvc:View xmlns="sap.m" xmlns:mvc="sap.ui.core.mvc" xmlns:table="____(4)____">
  <table:Table ____(5)____="{/Flights}" selectionMode="____(6)____">
    <table:columns>
      <table:Column width="8rem">
        <table:label><Label text="항공사"/></table:label>
        <table:____(7)____><Text text="{Carrid}"/></table:____(7)____>
      </table:Column>
    </table:columns>
  </table:Table>
</mvc:View>
```
```js
onCheck() {
  const aCarrid = this.byId("flightTable").____(8)____()
    .map((oItem) => oItem.____(9)____().getProperty("Carrid"));
  MessageToast.show(aCarrid.join(", "));
}
```

(1) 빈칸 (1)~(9)를 채우시오((2)는 다중 선택, (6)은 여러 행을 체크박스로 선택하는 값). 컨텍스트 배열을 바로 얻는 메서드와, 그리드 테이블에서 선택 행을 얻는 방법, 보이는 행 수 설정 속성을 쓰시오.
(2) 두 테이블을 지원 기기, 렌더링 방식(대량 데이터), 바인딩 aggregation과 행 템플릿, 반응형, 대표 기능, 파생 컨트롤 측면에서 비교하시오.
(3) 다음 중 **옳지 않은** 것을 모두 고르시오.
① 휴대폰에서 고객 목록을 보며 좁은 화면에서 일부 열을 행 아래로 내려야 한다 → `sap.m.Table`
② 데스크톱에서 2만 행, 30열을 스크롤하며 앞 두 열을 고정 → `sap.ui.table.Table`
③ BOM처럼 부모-자식 구조를 펼치고 접기 → `sap.ui.table.TreeTable`
④ 금액 소계·총계를 그룹별로 보여 주는 분석 화면 → `sap.ui.table.AnalyticalTable`
⑤ 계층 구조와 pop-in이 모두 필요한 폰 화면 → `sap.ui.table.TreeTable`
⑥ `sap.m.Table`도 행 가상화를 하므로 수십만 건을 한 번에 바인딩해도 성능 문제가 없다.
(4) `xmlns="sap.m"` 뷰에 다음 테이블을 넣었더니 행이 표시되지 않고 오류가 난다. 잘못된 곳을 모두 찾아 고치시오.
```xml
<Table rows="{/Flights}">
  <columns>
    <Column>
      <Text text="항공사"/>
      <template><Text text="{Carrid}"/></template>
    </Column>
  </columns>
</Table>
```

<details><summary>정답·해설</summary>

**(1)** (1) `items` (2) `MultiSelect` (3) `ColumnListItem` (4) `sap.ui.table` (5) `rows` (6) `MultiToggle` (7) `template` (8) `getSelectedItems` (9) `getBindingContext`
- `columns`의 열 수와 `cells`의 셀 수·순서가 같아야 한다. 이름 있는 모델이면 `getBindingContext("모델명")`.
- `getSelectedContexts()`를 쓰면 컨텍스트 배열을 바로 받는다(`.map(c => c.getProperty("Carrid"))`). 단일 선택 목록-상세는 `mode="SingleSelectMaster"`와 `selectionChange`.
- 그리드 테이블 선택 값: `None`, `Single`, `MultiToggle`. 선택 행은 `getSelectedIndices()` + `getContextByIndex(i)`(대량 선택은 `MultiSelectionPlugin`). 보이는 행 수는 예전 `visibleRowCount` 대신 `rowMode`(Fixed, Auto, Interactive).

**(2)**

| 구분 | `sap.m.Table`(Responsive) | `sap.ui.table.Table`(Grid) |
|---|---|---|
| 기기 | 데스크톱·태블릿·폰 | 데스크톱·태블릿(폰 미지원) |
| 렌더링 | 바인딩된 행을 모두 DOM에 렌더링. 많으면 `growing`(기본 20건씩)으로 나눠 로드 | 보이는 행만 렌더링하고 스크롤 시 행 재사용(가상 스크롤). 수천 행 가능 |
| 바인딩 | `items` + `ColumnListItem`(`cells`) | `rows` + 각 `Column`의 `label`·`template`(템플릿을 행 수만큼 복제·재사용) |
| 반응형 | 열 숨김, pop-in(`minScreenWidth`, `demandPopin`) | 없음, 가로 스크롤 |
| 기능 | `mode`(SingleSelectMaster, MultiSelect, Delete), growing, 그룹 헤더, 행마다 자유 레이아웃 | 열 고정(freeze), 크기 조절·이동, `selectionMode`, 셀 단위 키보드 탐색 |
| 파생 | – | `TreeTable`(계층), `AnalyticalTable`(합계·그룹, V2 분석 서비스) |

선택 기준: 폰·적은 행·자유 셀 레이아웃이면 `sap.m.Table`, 데스크톱 대량 행·많은 열·엑셀 같은 조작이면 grid table. 공식 문서도 200행 이상은 responsive table이 "부분 지원". Fiori Elements V4는 `tableType`(ResponsiveTable, GridTable, AnalyticalTable, TreeTable)으로 고른다.

**(3)** ⑤, ⑥. ⑤ `sap.ui.table` 계열은 폰을 지원하지 않고 pop-in도 없다. 폰의 계층 데이터는 `sap.m.Tree`나 drill-down 목록으로 설계한다. ⑥ `sap.m.Table`은 행마다 DOM을 만들어 행이 많으면 느려지므로 growing으로 나눠 불러야 하며, 대량 스크롤은 그리드 테이블을 쓴다.

**(4)** `sap.m.Table`에는 `rows` aggregation이 없다 → `items`. `sap.m.Column`에는 `template` aggregation이 없다(그리드 테이블 문법) → 열에는 헤더만, 셀은 `ColumnListItem`의 `cells`에. XML 파서는 없는 aggregation 이름에 오류를 낸다.
```xml
<Table items="{/Flights}">
  <columns><Column><Text text="항공사"/></Column></columns>
  <items>
    <ColumnListItem><cells><Text text="{Carrid}"/></cells></ColumnListItem>
  </items>
</Table>
```
그리드 테이블을 쓰려면 `xmlns:table="sap.ui.table"`을 선언하고 `<table:Table rows=...>`, `<table:template>`을 쓴다.

</details>

---

### D-014. Fragment와 Dialog, MessageBox, 값 도움말 [코드] ★★
<!-- src: U5-015, U5-016, UB-078, UB-082, UB-010, UB-080, MX-085, UB-081 -->
`my.app.view.HelloDialog` 프래그먼트의 루트는 `<Dialog id="helloDialog" title="{i18n>dialogTitle}">`이고, i18n 모델은 manifest로 컴포넌트에 설정되어 있다. 컨트롤러가 속한 뷰의 ID는 `main`이다.

```js
// 버전 A (문제 있음)
onOpenDialog: function () {
  Fragment.load({ name: "my.app.view.HelloDialog", controller: this })
    .then(function (oDialog) { oDialog.open(); });
},
onCloseDialog: function () {
  this.byId("helloDialog").close();
}

// 버전 B
onOpenDialog: function () {
  var oView = this.getView();
  if (!this._pDialog) {
    this._pDialog = Fragment.load({
      ____(1)____: oView.getId(),
      name: "my.app.view.HelloDialog",
      ____(2)____: this
    }).then(function (oDialog) {
      oView.____(3)____(oDialog);
      return oDialog;
    });
  }
  this._pDialog.then(function (oDialog) { oDialog.____(4)____(); });
}
```

(1) 버전 A로 버튼을 눌러 다이얼로그를 열 때 생기는 문제 3가지를 쓰시오.
(2) 버전 B의 빈칸 (1)~(4)를 채우고 각각의 의미를 쓰시오. Promise를 멤버에 저장하는 이유와, UI5 1.93+에서 같은 일을 하는 한 줄 코드(기본 적용되는 것 포함)를 쓰시오.
(3) 프래그먼트 안에 `<Button id="btn"/>`이 있다. (a)~(e)를 각각 따로 실행했을 때 버튼의 전체 ID를 쓰고, `this.byId("btn")`으로 찾을 수 있는 경우를 고르시오. (b), (e)는 어떻게 찾는가?
```js
Fragment.load({ name: "my.app.view.Frag", controller: this });                          // (a)
Fragment.load({ id: "f1", name: "my.app.view.Frag", controller: this });                // (b)
Fragment.load({ id: this.getView().getId(), name: "my.app.view.Frag", controller: this }); // (c)
this.loadFragment({ name: "my.app.view.Frag" });                                        // (d)
this.loadFragment({ id: "f2", name: "my.app.view.Frag" });                              // (e)
```
(4) Dialog의 `close()`와 `destroy()`의 차이를 쓰고, 다음 중 옳은 것을 고르시오. 매번 새 내용이 필요할 때의 처리 방법도 쓰시오.
① `close()`를 호출하면 인스턴스가 제거되어 다음에 다시 로드해야 한다. ② 자주 여는 Dialog는 한 번 만든 뒤 `close()`/`open()`으로 재사용한다. ③ `destroy()` 후에도 같은 변수로 `open()`할 수 있다. ④ `addDependent`로 붙인 Dialog는 뷰가 destroy되어도 남으므로 `onExit`에서 꼭 destroy해야 한다.
(5) 메시지 표시 컨트롤 선택이 Fiori 가이드라인에 맞지 **않는** 것을 고르고 이유를 쓰시오.
① 저장 성공 같은 짧은 알림 → `MessageToast` ② 삭제 전 확인 → `MessageBox.confirm` ③ 폼 입력 오류 여러 건을 필드와 연결해 모아 보기 → `MessagePopover`(메시지 모델 연결) ④ 페이지 상단에 계속 보여야 하는 안내 → `MessageStrip` ⑤ 서버의 치명적 오류로 작업 불가 → `MessageToast`로 3초 표시
(6) OData V4 컨텍스트를 삭제하기 전에 확인을 받는 코드의 빈칸을 채우고, MessageBox의 동작 특성과 V2에서의 삭제 방법을 쓰시오.
```js
onDelete: function (oEvent) {
  const oContext = oEvent.getSource().getBindingContext();
  MessageBox.____(1)____("이 출장을 삭제하시겠습니까?", {
    actions: [MessageBox.____(2)____.DELETE, MessageBox.Action.CANCEL],
    emphasizedAction: MessageBox.Action.DELETE,
    ____(3)____: (sAction) => {
      if (sAction ____(4)____ MessageBox.Action.DELETE) {
        oContext.____(5)____().then(() => MessageToast.____(6)____("삭제했습니다"));
      }
    }
  });
}
```
(7) Input에 값 도움말 아이콘을 표시하고 SelectDialog로 항공사를 골라 넣는 코드의 빈칸을 채우시오. SelectDialog의 닫기, 다중 선택, Fiori Elements에서의 대응을 쓰시오.
```xml
<Input id="carrInput" ____(1)____="true" valueHelpRequest=".onValueHelp"/>
<!-- CarrierVH.fragment.xml -->
<SelectDialog id="carrDialog" title="항공사" items="{/CarrierSet}"
  search=".onVHSearch" ____(2)____=".onVHConfirm" cancel=".onVHCancel">
  <StandardListItem title="{Carrid}" description="{Carrname}"/>
</SelectDialog>
```
```js
async onValueHelp() {
  this._oVH ??= await this.loadFragment({ name: "zdemo.view.CarrierVH" });
  this._oVH.open();
},
onVHSearch(oEvent) {
  const sValue = oEvent.getParameter("value");
  oEvent.getSource().getBinding("items").filter([new Filter("Carrname", FilterOperator.Contains, sValue)]);
},
onVHConfirm(oEvent) {
  const oItem = oEvent.getParameter("____(3)____");
  if (oItem) { this.byId("carrInput").setValue(oItem.____(4)____()); }
}
```

<details><summary>정답·해설</summary>

**(1)**
1. 누를 때마다 프래그먼트를 새로 로드한다. 첫 다이얼로그가 destroy되지 않았으므로 두 번째 클릭에서 ID `helloDialog` 중복 오류(duplicate id).
2. `id`를 주지 않아 컨트롤 ID가 접두어 없는 `helloDialog`. `this.byId("helloDialog")`는 `main--helloDialog`를 찾으므로 `undefined` → `close()`에서 TypeError.
3. `addDependent`를 하지 않아 뷰/컴포넌트의 모델을 물려받지 못한다. `{i18n>dialogTitle}`이 해결되지 않아 제목이 비어 보이고, 뷰가 destroy되어도 다이얼로그가 남는다(메모리 누수).

**(2)** (1) `id` (2) `controller` (3) `addDependent` (4) `open`
- `id: oView.getId()`: 컨트롤 ID에 뷰 접두어(`main--helloDialog`)가 붙어 `this.byId`로 찾는다.
- `controller: this`: 프래그먼트 안 `press=".onCloseDialog"`가 이 컨트롤러 메서드에 연결된다(프래그먼트 핸들러는 연 컨트롤러에서 찾는다).
- `addDependent`: 다이얼로그는 static area에 렌더링되므로 뷰의 dependent로 넣어야 모델(i18n 등)·바인딩 컨텍스트를 물려받고 뷰와 함께 정리된다.
- Promise 저장: 두 번 눌러도 프래그먼트를 다시 만들지 않아 중복 ID 오류를 막는다.
- 1.93+: `this._pDialog ??= this.loadFragment({ name: "my.app.view.HelloDialog" });` — `loadFragment`는 기본으로 id를 뷰 ID로, controller를 현재 컨트롤러로 설정하고 addDependent까지 한다.

**(3)** (a) `btn` (b) `f1--btn` (c) `main--btn` (d) `main--btn` (e) `main--f2--btn`. `this.byId("btn")`으로 찾을 수 있는 것: (c), (d).
`Fragment.load`는 `id`를 주면 그것을 접두어로, 안 주면 접두어 없이 쓴다. `loadFragment`는 뷰 ID를 자동 접두어로 쓰고 `id`를 더 주면 둘 다 붙는다. (b)는 `Fragment.byId("f1", "btn")`, (e)는 `this.byId("f2--btn")`. (a)는 두 번 로드하면 중복 ID 오류.

**(4)** `close()`는 화면에서 숨길 뿐 인스턴스와 입력값이 남는다(재사용 가능, 입력값 초기화는 직접). `destroy()`는 인스턴스와 하위 컨트롤을 제거하므로 이후 사용하면 오류, 다시 쓰려면 새로 만들어야 한다. 정답 ②. ④는 반대로 dependent는 뷰와 함께 destroy된다. 매번 새 내용이 필요하면 `afterClose` 이벤트에서 destroy하고 변수도 비운다.

**(5)** ⑤. MessageToast는 자동으로 사라지고 사용자 확인을 받지 않으므로 오류에 쓰면 안 된다(성공·정보성 전용). 치명적 오류는 사용자가 닫아야 하는 모달 `MessageBox.error`.

**(6)** (1) `confirm`(또는 `warning`) (2) `Action` (3) `onClose` (4) `===` (5) `delete` (6) `show`
MessageBox는 **비동기**라 `confirm(...)` 다음 줄은 사용자가 누르기 전에 바로 실행된다. 후속 처리는 `onClose` 콜백 안에 두고, 화살표 함수라 `this`가 컨트롤러로 유지된다. 문구는 i18n에서 읽는다. V4 `Context#delete()`는 Promise를 돌려주고 기본 `$auto` 그룹이면 바로 DELETE를 보낸다(실패는 catch). V2는 `oModel.remove(oContext.getPath(), { success, error })`.

**(7)** (1) `showValueHelp` (2) `confirm` (3) `selectedItem` (4) `getTitle`
SelectDialog는 확인 시 자동으로 닫히므로 `close()`가 필요 없다. 다중 선택(`multiSelect="true"`)이면 `selectedItems`. 검색 필터는 OData면 서버에서 수행된다. Smart/Fiori Elements 앱에서는 `Common.ValueList` 어노테이션으로 값 도움말이 자동 생성된다.

</details>

---

### D-015. 커스텀 컨트롤 작성 [작성] ★★★
<!-- src: U5-036, U5-037 -->
(1) 다음 조건의 커스텀 컨트롤 `my.app.control.Counter`를 작성하시오.
- 속성 `value`(int, 기본값 0), 이벤트 `change`(파라미터 `value`)
- 렌더러는 `apiVersion: 2`, `<div class="myCounter">현재값</div>` 출력(루트 요소에 컨트롤 ID)
- 클릭하면 value를 1 늘리고 `change` 이벤트 발생
(2) metadata 선언으로 자동 생성되는 메서드를 속성·aggregation(`items`, multiple)·이벤트별로 쓰시오.
(3) `openStart`의 두 번째 인자로 컨트롤을 넘기는 이유와 `oRm.text`의 장점을 쓰시오. 자식 aggregation `content`를 선언하고 렌더링하는 방법도 쓰시오.
(4) 다음 중 **틀린** 것을 고르고, 맞는 API 목록과 그 장점을 쓰시오.
① `properties`에 `text`를 선언하면 `getText`, `setText`가 자동 생성된다.
② `events`에 `press`를 선언하면 `attachPress`, `detachPress`, `firePress`가 생성된다.
③ 렌더러 `apiVersion: 2`에서는 `oRm.write("<div>")`처럼 HTML 문자열을 이어 붙이는 방식이 권장된다.
④ setter로 속성을 바꾸면 기본적으로 컨트롤이 invalidate되어 다시 렌더링된다.
(5) ④의 재렌더링을 막고 싶을 때 쓰는 방법을 쓰시오.

<details><summary>정답·해설</summary>

**(1)**
```js
sap.ui.define(["sap/ui/core/Control"], function (Control) {
  "use strict";
  return Control.extend("my.app.control.Counter", {
    metadata: {
      properties: { value: { type: "int", defaultValue: 0 } },
      events: { change: { parameters: { value: { type: "int" } } } }
    },
    renderer: {
      apiVersion: 2,
      render: function (oRm, oControl) {
        oRm.openStart("div", oControl);   // id, data-sap-ui 속성 자동 출력
        oRm.class("myCounter");
        oRm.openEnd();
        oRm.text(String(oControl.getValue()));
        oRm.close("div");
      }
    },
    onclick: function () {
      var iNew = this.getValue() + 1;
      this.setValue(iNew);                // 속성 변경 → invalidate → 다시 렌더링
      this.fireChange({ value: iNew });
    }
  });
});
```

**(2)** 속성 `value`: `getValue`/`setValue`. aggregation `items`(multiple): `addItem`, `insertItem`, `removeItem`, `getItems`, `removeAllItems`, `destroyItems` 등. 이벤트 `change`: `attachChange`/`detachChange`/`fireChange`.

**(3)** 컨트롤을 넘겨야 루트 요소에 ID와 `data-sap-ui` 속성이 붙고 브라우저 이벤트 훅(`onclick` 등)이 연결된다. `oRm.text`는 HTML 이스케이프를 해 준다(XSS 방지). aggregation은 `aggregations: { content: { type: "sap.ui.core.Control", multiple: true } }`로 선언하고 렌더러에서 `oRm.renderControl(oChild)`로 그린다.

**(4)** ③. `apiVersion: 2`는 semantic rendering API(`openStart`, `attr`, `class`, `style`, `openEnd`, `text`, `close`, `voidStart`/`voidEnd`)만 쓴다. 덕분에 DOM을 통째로 바꾸지 않고 바뀐 부분만 패치(in-place DOM patching)할 수 있다. `write`, `writeEscaped` 같은 문자열 API는 deprecated이며 apiVersion 2에서 쓰면 안 된다.

**(5)** `this.setProperty("value", iNew, true)`(세 번째 인자 true = suppress invalidate)로 바꾸고 DOM을 직접 갱신한다.

</details>

---

## 5. 모델과 데이터 바인딩

### D-016. 모델 종류, 바인딩 모드, JSONModel의 갱신 규칙과 전파 [코드] ★★
<!-- src: U5-017, U5-019, UB-049, UB-045, MX-076, UB-050, UB-057 -->
모델은 `new JSONModel({ qty: 1, name: "Kim" })`이고 뷰에는 다음 컨트롤이 있다(타입 지정 없음).

```xml
<Input id="inp" value="{/qty}"/>
<Text  id="txt" text="{/qty}"/>
<Input value="{/name}"/>                           <!-- (가) -->
<Input value="{/name}" valueLiveUpdate="true"/>    <!-- (나) -->
<Text text="Hello {/name}"/>
```

(1) JSONModel, OData V2 Model, ResourceModel, OData V4 Model의 기본 바인딩 모드를 쓰고, OneWay/TwoWay/OneTime의 의미를 쓰시오. V2 모델에서 편집 화면을 만들려면 어떻게 바꾸는가?
(2) 각 경우는 서로 독립이다. 결과를 쓰시오.
- (A) 그대로 `setModel` 후 사용자가 `inp`에 `5`를 입력하고 Enter. `getProperty("/qty")` 값(타입 포함)과 Text 값은?
- (B) `setModel` **전에** `setDefaultBindingMode("OneWay")`. 사용자가 `5` 입력 후 Enter. `getProperty("/qty")`, Text, Input에 보이는 값은?
- (C) `setModel` **전에** `setDefaultBindingMode("OneTime")`. 화면이 뜬 뒤 `setProperty("/qty", 9)`. Input과 Text 값은?
숫자를 유지하려면 바인딩을 어떻게 쓰는가? `setDefaultBindingMode`를 setModel 전에 불러야 하는 이유는?
(3) 사용자가 이름 Input의 내용을 지우고 `Lee`를 타이핑만 하고 아직 Enter나 포커스 이동을 하지 않았다. (가)에 입력한 경우와 (나)에 입력한 경우 각각 `Hello ...` Text에 보이는 값을 쓰고 이유를 쓰시오. OData V2 모델이면 무엇이 다른가?
(4) 다음 코드 실행 직후 (a) 콘솔 출력 (b) 화면 Text 값을 쓰고 (c) 화면까지 바뀌게 하는 올바른 코드 한 줄과 이미 직접 고쳤을 때의 대처를 쓰시오.
```js
const oModel = new JSONModel({ flight: { carrid: "LH", seatsocc: 10 } });
this.getView().setModel(oModel);          // 뷰: <Text text="{/flight/seatsocc}"/> → 10 표시
const oFlight = oModel.getProperty("/flight");
oFlight.seatsocc = 11;
console.log(oModel.getProperty("/flight/seatsocc"));
```
(5) 콘솔 출력 6개를 쓰시오.
```js
const oModel = new JSONModel({ a: 1, b: { c: 2, d: [10, 20, 30] } });
oModel.setData({ b: { c: 5, e: 9 } }, true);
console.log(oModel.getProperty("/a"), oModel.getProperty("/b/c"),
            oModel.getProperty("/b/d/1"), oModel.getProperty("/b/e"));   // (1)~(4)
oModel.setData({ b: { c: 7 } });
console.log(oModel.getProperty("/a"), oModel.getProperty("/b/e"));      // (5)(6)
```
(6) JSONModel에 150건 배열을 넣고 growing 없는 `List`에 바인딩했다. 표시 건수와 해결 방법, 더 나은 대안을 쓰시오. 같은 원인으로 생기는 다른 증상도 쓰시오.
(7) 모델 전파(propagation) 규칙을 쓰고, 다음 두 현상의 원인과 해결을 쓰시오. (A) 뷰 컨트롤러 `onInit`에서 `this.getView().getModel()`이 `undefined`(모델은 manifest로 컴포넌트에 설정). (B) 코드로 만든 `new Dialog()`에서 `{i18n>...}` 바인딩이 비어 있다. 전역 `sap.ui.getCore().setModel()`을 쓰면 안 되는 이유도 쓰시오.

<details><summary>정답·해설</summary>

**(1)** JSONModel(XMLModel도): **TwoWay**. OData V2: **OneWay**(서버 데이터를 화면에서 바로 바꾸지 않도록). ResourceModel: **OneTime**만 지원(텍스트는 바뀌지 않음). OData V4: **TwoWay**(변경은 update group 규칙에 따라 전송). OneWay = 모델 → 뷰, TwoWay = 양방향, OneTime = 처음 한 번만 모델 → 뷰. V2 편집 화면은 `oModel.setDefaultBindingMode("TwoWay")` 또는 manifest `settings.defaultBindingMode: "TwoWay"`.

**(2)**
- (A) `getProperty("/qty")` → `"5"`(문자열), Text → `5`. TwoWay라 Input의 change 때 모델에 쓰고, 같은 경로의 Text도 갱신된다. 타입이 없어 문자열이 그대로 저장되어 숫자 1이 문자열 "5"가 된다.
- (B) `getProperty` → `1`, Text → `1`, Input에는 사용자가 입력한 5가 그대로 보임. OneWay는 모델 → 뷰만.
- (C) Input `1`, Text `1`. OneTime은 바인딩 생성 시 한 번만 읽는다.
숫자 유지: `value="{path:'/qty', type:'sap.ui.model.type.Integer'}"`. `setDefaultBindingMode`는 그 이후에 **생성되는** 바인딩에만 적용되므로 setModel(바인딩 생성) 전에 호출한다.

**(3)** (가) `Hello Kim`, (나) `Hello Lee`. Input `value` → 모델은 기본적으로 `change` 이벤트(Enter, 포커스 이탈) 때 갱신된다. `valueLiveUpdate="true"`면 키 입력마다 갱신되어 TwoWay로 모델과 다른 컨트롤에 즉시 반영된다(Walkthrough Step 15 HelloPanel). OData V2 모델이면 모델 변경이 서버로 바로 가지 않고 `submitChanges` 전까지 pending change로 쌓인다.

**(4)** (a) `11` (b) `10`(변경되지 않음) (c) `oModel.setProperty("/flight/seatsocc", 11);`
`getProperty`는 내부 객체의 **참조**를 돌려주므로 직접 고치면 데이터 자체는 바뀐다(콘솔 11). 하지만 모델이 변경을 몰라 바인딩에 통지가 가지 않는다. 이미 직접 고쳤다면 `oModel.refresh()`(필요하면 `refresh(true)`)로 강제 검사. 원본을 보존해야 하는 "취소" 기능이면 참조 공유 때문에 원본도 바뀐다는 점에 주의(D-037).

**(5)** (1) `1` (2) `5` (3) `20` (4) `9` (5) `undefined` (6) `undefined`
`setData(oData, true)`는 기존 데이터에 깊게 합친다(deep merge): a와 d가 남고 c는 5, e 추가. 배열은 인덱스 경로(`/b/d/1` = 20). 두 번째 인자 없는 `setData`는 데이터 전체를 **교체**해 a와 e가 사라진다. 일부 값만 바꿀 때는 `setProperty("/b/c", 7)`을 써야 그 값만 갱신된다.

**(6)** 100건. 모델의 기본 size limit은 100이며 오류 메시지가 없다. `oModel.setSizeLimit(200)`(충분히 큰 수)을 바인딩 전에 호출. 데이터가 아주 많으면 `growing="true"`나 서버 페이징(OData)이 성능상 낫다. `Select`/`ComboBox`가 값 일부만 보이는 것도 같은 원인.

**(7)** 규칙: 모델은 설정된 객체에서 자식(aggregation)으로 전파된다. 컴포넌트 모델은 rootView와 그 아래, 뷰 모델은 뷰 안 컨트롤이 쓴다. 같은 이름 모델이 아래쪽에 설정되면 아래쪽이 우선. 바인딩 컨텍스트도 같은 방식으로 전파.
- (A) `onInit` 시점에는 뷰가 아직 컴포넌트(부모)에 붙기 전일 수 있어 전파된 모델이 없다 → `this.getOwnerComponent().getModel()`(Walkthrough Step 22 주의 문구).
- (B) Dialog는 static area에 렌더링되어 부모가 없으므로 아무 모델도 받지 못한다 → `this.getView().addDependent(oDialog)`.
전역 `sap.ui.getCore().setModel()`은 deprecated이고, 런치패드에서 여러 앱이 섞일 때 충돌한다.

</details>

---

### D-017. 바인딩 경로·컨텍스트·바인딩 종류와 이름 있는 모델 [코드] ★★
<!-- src: U5-018, UB-046, UB-023, U5-023, U5-026, MX-081 -->
뷰의 기본 모델이 다음과 같다.

```js
var oModel = new JSONModel({
  company: {
    name: "ACME",
    employees: [ { first: "Kim", age: 31 }, { first: "Lee", age: 25 } ]
  },
  products: [
    { name: "Apple", price: 3 }, { name: "Banana", price: 1 }, { name: "Carrot", price: 2 }
  ]
});
this.getView().setModel(oModel);
```

```xml
<Text text="{/company/name}"/>                          <!-- (a) -->
<Text text="{/company/employees/1/first}"/>             <!-- (b) -->
<Text text="{/company/employees/length}"/>              <!-- (c) -->
<Panel binding="{/company/employees/1}">
  <Text text="{first}"/>                                <!-- (d) -->
  <Text text="{/company/name}"/>                        <!-- (e) -->
  <Text text="{name}"/>                                 <!-- (f) -->
  <Text text="{/first}"/>                               <!-- (g) -->
  <Text text="{employees/0/first}"/>                    <!-- (h) -->
</Panel>
<Text text="Boss: {/company/employees/0/first} ({/company/employees/0/age})"/>  <!-- (i) -->
<List items="{/products}">
  <StandardListItem title="{name}" type="Navigation" press=".onItemPress"/>
</List>
```

(1) (a)~(i)에 표시되는 값을 쓰시오(없으면 "빈 값"). (c)가 값을 갖는 이유, (i)에 필요한 환경 설정을 쓰시오.
(2) 사용자가 리스트의 **세 번째** 항목을 눌렀다. 출력을 쓰시오.
```js
onItemPress: function (oEvent) {
  var oCtx = oEvent.getSource().getBindingContext();
  console.log(oCtx.getPath());              // (p)
  console.log(oCtx.getObject().name);       // (q)
  console.log(oCtx.getProperty("price"));   // (r)
}
```
(3) 모델을 이름 `prod`로 설정하고 XML을 `items="{prod>/products}"`, `title="{prod>name}"`으로 바꾼 뒤 (2)의 핸들러를 그대로 실행하면 어떻게 되는지, 어떻게 고치는지 쓰시오.
(4) 컴포넌트 `init`에서 `this.setModel(new JSONModel({ name: "Comp" }))`, `this.setModel(new JSONModel({ name: "Emp" }), "emp")`를, 뷰 `onInit`에서 `this.getView().setModel(new JSONModel({ name: "View" }))`를 했다. `{/name}`, `{emp>/name}`, `{emp/name}`, `{hr>/name}`에 표시되는 값과 이유를 쓰시오.
(5) property binding, aggregation(list) binding, element(context) binding을 각각 예와 함께 설명하고, template 대신 factory 함수를 쓰는 경우와 형태를 쓰시오. OData V4 aggregation binding에 함께 줄 수 있는 것도 쓰시오.
(6) 컨트롤러 `onInit`에서 `this.getView().setModel(oModel, "flight")`로 JSONModel을 설정했다. 다음 XML에서 잘못된 곳 4곳을 찾아 고치고, 어떤 오류가 "에러 없이 화면만 비는지" 쓰시오.
```xml
<mvc:View controllerName="zmx.flights.controller.Main" xmlns:mvc="sap.ui.core.mvc" xmlns="sap.m">
  <Page title="{i18n>title}">
    <content>
      <SearchField search=".onSearch" width="50%"/>
      <List items="{/Flights}">
        <StandardListItem title="{flight>carrier}" description="{connid}"/>
      </List>
      <f:SimpleForm editable="true">
        <Label text="Carrier"/>
        <Input value="{flight>/selected/carrier"/>
      </f:SimpleForm>
    </content>
  </Page>
</mvc:View>
```

<details><summary>정답·해설</summary>

**(1)** (a) `ACME` (b) `Lee` (c) `2` (d) `Lee` (e) `ACME` (f) 빈 값 (g) 빈 값 (h) 빈 값 (i) `Boss: Kim (31)`
- `/`로 시작하면 절대 경로(컨텍스트 무관), 배열은 0부터.
- (c) JSONModel은 경로 조각을 JS 객체 속성으로 따라가므로 배열의 `length`도 읽힌다.
- `binding="{...}"`은 element(context) 바인딩. Panel과 자식의 컨텍스트가 `/company/employees/1`이 된다. (d)는 `/company/employees/1/first`, (f)는 `.../1/name`이 없어 `undefined` → text 기본값 빈 문자열, (h)는 `.../1/employees/0/first`로 없음, (g) 절대 경로 `/first`는 없음.
- (i) 문자열과 여러 바인딩을 섞는 복합(composite) 바인딩. `compatVersion="edge"` 또는 `bindingSyntax="complex"` 필요.

**(2)** (p) `/products/2` (q) `Carrot` (r) `2`. `oEvent.getSource()`는 눌린 StandardListItem. `getObject()`는 컨텍스트가 가리키는 객체 전체, `getProperty("price")`는 컨텍스트 기준 상대 경로 값. 상세로 이동할 때 `getPath()`나 키 값을 라우트 파라미터로 넘기는 패턴이 흔하다.

**(3)** `getBindingContext()`는 기본(이름 없는) 모델의 컨텍스트를 돌려주므로 `undefined`, `oCtx.getPath()`에서 TypeError → `getBindingContext("prod")`.

**(4)** `{/name}` → `View`(같은 이름 모델이 뷰에 직접 설정되면 컴포넌트에서 전파된 것보다 우선). `{emp>/name}` → `Emp`(뷰에 없으니 컴포넌트에서 전파). `{emp/name}` → 빈 값(`>`가 없어 기본 모델의 **상대 경로**, 컨텍스트 없음). `{hr>/name}` → 빈 값(모델이 어디에도 없음, 오류 없이 비어 찾기 어려운 버그).

**(5)**
- **property binding**: 속성 하나를 모델 값에. `<Text text="{/company/name}"/>`, `<Input value="{Description}"/>`.
- **aggregation binding**: aggregation을 배열/엔티티셋에 연결하고 template을 항목마다 복제. `<List items="{/Travel}"><StandardListItem title="{Description}"/></List>`. 복제본은 `/Travel/0`, `/Travel/1` 같은 컨텍스트를 받는다.
- **element binding**: 컨트롤에 컨텍스트를 설정해 하위 상대 경로의 기준을 정한다. `oView.bindElement("/Travel(1)")` 또는 `binding="{/Travel(1)}"`. 상세 화면에서 라우트 파라미터로 대상을 바꿀 때.
- **factory**: 항목마다 다른 컨트롤이 필요할 때(데이터 타입에 따라 Input/CheckBox/DatePicker). `items: { path: "/fields", factory: this.createField.bind(this) }`, 함수는 `(sId, oContext)`를 받아 새 컨트롤 반환.
상대 경로는 컨텍스트가 있어야 해석되고 절대 경로는 항상 루트부터. V4는 path와 함께 `parameters: { $select, $expand }`, `filters`, `sorter`를 줄 수 있다.

**(6)**
1. `items="{/Flights}"` → `items="{flight>/Flights}"`(이름 있는 모델은 `모델이름>` 접두어. 지금은 기본 모델을 찾음).
2. `description="{connid}"` → `"{flight>connid}"`(항목 안 상대 경로도 같은 모델 이름).
3. `f:` 네임스페이스 선언 없음 → `xmlns:f="sap.ui.layout.form"`.
4. `value="{flight>/selected/carrier"` → 닫는 `}` 누락.
1·2번은 실행해도 에러 없이 화면만 비어 필기시험 단골이다. `title="{flight>carrier}"`는 맞다. `.onSearch`처럼 점을 붙이면 컨트롤러 메서드임이 분명하다(권장).

</details>

---

### D-018. 필터·정렬·그룹: AND/OR 규칙과 검색 핸들러 [코드] ★★★
<!-- src: U5-024, U5-025, MX-079 -->
다음 JSONModel이 `<List id="list" items="{/products}">`에 바인딩되어 있다(`Filter`, `FilterOperator`, `Sorter`는 의존성으로 받음).

```js
new JSONModel({ products: [
  { name: "Apple",     cat: "F", price: 3 },
  { name: "Banana",    cat: "F", price: 1 },
  { name: "Carrot",    cat: "V", price: 2 },
  { name: "Avocado",   cat: "F", price: 5 },
  { name: "Aubergine", cat: "V", price: 4 }
]});
```

(1) 각 단계는 앞 단계에 이어서 실행된다. (a)~(c)를 쓰고, 배열로 넘긴 필터의 결합 규칙과 새 `filter` 호출의 효과를 쓰시오.
```js
var oBinding = this.byId("list").getBinding("items");
oBinding.filter([ new Filter("cat", FilterOperator.EQ, "F"), new Filter("price", FilterOperator.GT, 2) ]);
console.log(oBinding.getLength());                                  // (a)
oBinding.filter([ new Filter("name", FilterOperator.StartsWith, "A"), new Filter("name", FilterOperator.EndsWith, "t") ]);
console.log(oBinding.getLength());                                  // (b)
oBinding.sort(new Sorter("price", true));
console.log(oBinding.getContexts()[0].getProperty("name"));        // (c)
```
(2) 다른 데이터와 그룹 정렬이다. (a) 화면 순서를 그룹 머리글과 함께 쓰고, (b) 이어서 `this.byId("list").getBinding("items").filter(new Filter("price", FilterOperator.GE, 500))` 실행 후 보이는 항목을 쓰시오. 그룹 머리글이 생기는 조건과 머리글 텍스트를 바꾸는 방법도 쓰시오.
```js
{ flights: [
  { name: "LH400", carrier: "LH", price: 900 }, { name: "AA17", carrier: "AA", price: 500 },
  { name: "LH401", carrier: "LH", price: 300 }, { name: "UA58", carrier: "UA", price: 500 } ] }
```
```xml
<List id="list" items="{ path: '/flights',
    sorter: [ { path: 'carrier', descending: false, group: true },
              { path: 'price',   descending: true } ] }">
  <StandardListItem title="{name}"/>
</List>
```
(3) `<Table id="travelTable" items="{/Travel}">`의 `SearchField` `search` 핸들러 `onSearch`를 작성하시오. 조건: 검색어가 있으면 `Description`에 포함(Contains) **그리고** `TotalPrice` > 1000, 비면 필터 해제, 항상 `TotalPrice` 내림차순.
(4) (3)의 바인딩이 OData 모델이면 서버로 어떤 쿼리 옵션이 가는지(V4/V2 차이 포함) 쓰고, `getBinding`과 `getBindingContext`를 혼동하면 안 되는 이유를 쓰시오.

<details><summary>정답·해설</summary>

**(1)** (a) `2` (b) `4` (c) `Avocado`
배열로 넘기면 **같은 경로끼리는 OR, 다른 경로끼리는 AND**.
- (a) cat과 price는 다른 경로 → AND: cat=F 이고 price>2 → Apple, Avocado.
- (b) 새 `filter` 호출은 이전 필터를 **대체**. 둘 다 name → OR: A로 시작(Apple, Avocado, Aubergine) 또는 t로 끝(Carrot) → 4건.
- (c) 필터 유지 + price 내림차순: Avocado(5), Aubergine(4), Apple(3), Carrot(2).
다른 논리가 필요하면 `new Filter({ filters: [...], and: true/false })`로 명시한다.

**(2)** (a) [AA] AA17 → [LH] LH400, LH401 → [UA] UA58 (b) [AA] AA17 → [LH] LH400 → [UA] UA58
첫 정렬자(carrier 오름차순, `group: true`)로 묶고 그룹 안에서는 두 번째 정렬자(price 내림차순)로 정렬해 LH400(900)이 먼저. 그룹 머리글은 첫 정렬자에 `group: true`가 있어야 생기고 기본 텍스트는 그룹 키 값(`groupHeaderFactory`로 변경). `filter`는 정렬을 유지한 채 조건에 맞는 항목만 남겨 LH401(300)이 빠진다.

**(3)**
```js
onSearch: function (oEvent) {
  var sQuery = oEvent.getParameter("query");
  var aFilters = [];
  if (sQuery) {
    aFilters.push(new Filter({
      filters: [
        new Filter("Description", FilterOperator.Contains, sQuery),
        new Filter("TotalPrice", FilterOperator.GT, 1000)
      ],
      and: true
    }));
  }
  var oBinding = this.byId("travelTable").getBinding("items");
  oBinding.filter(aFilters);                      // 빈 배열 → 필터 해제
  oBinding.sort(new Sorter("TotalPrice", true));  // true = descending
}
```
경로가 다른 필터를 배열로 넘겨도 AND지만, 의도를 분명히 하려면 multi-filter를 쓴다. `Sorter(path, bDescending)`.

**(4)** V4: `$filter=contains(Description,'...') and TotalPrice gt 1000&$orderby=TotalPrice desc`. V2는 `substringof('...',Description)`. 바인딩(필터·정렬 대상)은 `getBinding("items")`로 얻고, `getBindingContext()`는 컨트롤의 컨텍스트(행 데이터)라 `filter`가 없다.

</details>

---

## 6. 포매터 · i18n · 데이터 타입

### D-019. Expression·composite 바인딩과 formatter 작성·테스트 [작성] ★★★
<!-- src: U5-020, UB-056, UB-048, U5-021, UB-052, UB-053, MX-099 -->
기본 모델 데이터가 `{ stock: 0, price: 12.5, status: "A", items: [1, 2, 3], first: "Gildong", last: "Hong", qty: 3 }`이다.

```xml
<Text text="{= ${/stock} > 0 ? 'In Stock' : 'Sold Out' }"/>   <!-- (a) -->
<Text text="{= ${/price} * 2 }"/>                              <!-- (b) -->
<Text text="{= ${/items}.length }"/>                           <!-- (c) -->
<Button visible="{= ${/status} === 'A' }"/>                    <!-- (d) visible -->
<Text text="{= ${/missing} || 'N/A' }"/>                       <!-- (e) -->
<Text text="{ parts: [ { path: '/first' }, { path: '/last' } ], formatter: '.fmtName' }"/>  <!-- (f) -->
<Text text="{/last}, {/first} ({/qty})"/>                     <!-- (g) -->
```
```js
fmtName(sFirst, sLast) { return sLast.toUpperCase() + " " + sFirst; }
```

(1) (a)~(g)의 값을 쓰시오.
(2) 조건 `${/stock} < 10 && ${/status} === 'A'`를 XML 속성에 그대로 쓰면 왜 오류인지, 어떻게 써야 하는지 쓰시오.
(3) 문법적으로 **잘못된** expression binding을 고르고 이유를 쓰시오. 이름 있는 모델의 경우 문법도 쓰시오.
① `visible="{= ${/items}.length > 0 }"` ② `state="{= ${Price} > 100 ? 'Error' : 'Success' }"` ③ `text="{= ${Qty} * ${Price} }"` ④ `enabled="{= ${/mode} === 'edit' &amp;&amp; !${/busy} }"` ⑤ `visible="{= /mode === 'edit' }"`
(4) `OverallStatus`(`O`=Open, `A`=Accepted, `X`=Cancelled)를 `ObjectStatus`로 보여 주려 한다. 다음을 작성하시오.
- `my/travel/model/formatter.js`: `statusText`(i18n 키 `statusOpen`/`statusAccepted`/`statusCancelled`, 그 외는 입력값 그대로, 값이 없으면 빈 문자열)와 `statusState`(O→Warning, A→Success, X→Error, 그 외 None; `sap/ui/core/library`의 `ValueState` 사용)
- 컨트롤러에서 formatter를 쓸 수 있게 하는 부분과 XML `ObjectStatus` 한 줄
- `statusState`의 QUnit 테스트(A·X·알 수 없는 값)
(5) 다른 개발자의 formatter가 화면을 열 때 `Cannot read properties of undefined (reading 'toUpperCase')`를 낸다(데이터가 로드되면 정상). 원인 2가지를 쓰시오.
```js
statusText(sStatus) {
  switch (sStatus.toUpperCase()) { case "A": return "Accepted"; case "X": return "Cancelled"; }
}
```
(6) formatter를 `core:require="{ Formatter: 'ui5/walkthrough/model/formatter' }"`로 불러와 `formatter: 'Formatter.statusText'`로 지정했더니 (4)의 `statusText`에서 `this.getOwnerComponent is not a function`이 난다. 원인과 XML 수정, 다른 해결책을 쓰시오.
(7) `.formatter.xxx`처럼 점으로 시작할 때 함수를 찾는 위치와 `this`는? `statusText`를 단위 테스트하려면 어떻게 하는가? formatter 대신 데이터 타입이나 expression을 쓸 때는 언제인가?

<details><summary>정답·해설</summary>

**(1)** (a) `Sold Out`(0 > 0 false) (b) `25` (c) `3` (d) `true`(버튼 보임) (e) `N/A`(없는 경로는 undefined) (f) `HONG Gildong`(`parts` 값이 순서대로 인자) (g) `Hong, Gildong (3)`(문자열 + 여러 바인딩의 composite binding, `compatVersion="edge"` 또는 `bindingSyntax="complex"` 필요)

**(2)** XML 속성 값 안에서 `<`와 `&`는 특수문자라 파싱 오류. `${/stock} &lt; 10 &amp;&amp; ${/status} === 'A'`처럼 엔티티로 쓰거나, 비교 방향을 바꿔 `10 > ${/stock}`(`>`는 허용)으로 쓰고 `&&`는 `&amp;&amp;`.

**(3)** ⑤. expression binding 안에서 모델 값은 `${경로}`로 감싸야 한다. 이름 있는 모델은 `${model>/path}`. 식이 길어지거나 재사용되면 formatter로 옮기는 것이 가독성과 테스트에 좋다.

**(4)**
```js
// webapp/model/formatter.js
sap.ui.define(["sap/ui/core/library"], function (coreLibrary) {
  "use strict";
  const ValueState = coreLibrary.ValueState;
  return {
    statusText: function (sStatus) {
      if (!sStatus) { return ""; }
      const oBundle = this.getOwnerComponent().getModel("i18n").getResourceBundle();
      switch (sStatus) {
        case "O": return oBundle.getText("statusOpen");
        case "A": return oBundle.getText("statusAccepted");
        case "X": return oBundle.getText("statusCancelled");
        default:  return sStatus;
      }
    },
    statusState: function (sStatus) {
      switch (sStatus) {
        case "O": return ValueState.Warning;
        case "A": return ValueState.Success;
        case "X": return ValueState.Error;
        default:  return ValueState.None;
      }
    }
  };
});
```
```js
// List.controller.js
sap.ui.define(["sap/ui/core/mvc/Controller", "my/travel/model/formatter"],
  function (Controller, formatter) {
    "use strict";
    return Controller.extend("my.travel.controller.List", { formatter: formatter });
  });
```
```xml
<ObjectStatus text="{ path: 'OverallStatus', formatter: '.formatter.statusText' }"
              state="{ path: 'OverallStatus', formatter: '.formatter.statusState' }"/>
```
```js
// webapp/test/unit/model/formatter.js
sap.ui.define(["my/travel/model/formatter", "sap/ui/core/library"], function (formatter, coreLibrary) {
  "use strict";
  const ValueState = coreLibrary.ValueState;
  QUnit.module("formatter.statusState");
  QUnit.test("A는 Success", function (assert) {
    assert.strictEqual(formatter.statusState("A"), ValueState.Success);
  });
  QUnit.test("X는 Error", function (assert) {
    assert.strictEqual(formatter.statusState("X"), ValueState.Error);
  });
  QUnit.test("알 수 없는 값은 None", function (assert) {
    assert.strictEqual(formatter.statusState("Z"), ValueState.None);
  });
});
```
채점: `sap.ui.define`으로 객체를 돌려주는 모듈 / statusText에서 ResourceBundle 사용(`this` = 컨트롤러) / ValueState 매핑과 기본값 None / 컨트롤러 `formatter: formatter` / XML `.formatter.xxx` 두 속성 / QUnit `module`·`test`·`assert.strictEqual` / 세 경우 모두. (문자열 `"Warning"` 등을 반환해도 동작한다.)

**(5)** ① 데이터가 도착하기 전 바인딩 초기화 때 formatter가 `undefined`(또는 `null`)로 먼저 호출되어 `toUpperCase`에서 TypeError. ② A, X 외 값이면 `undefined`를 반환해 화면이 빈다. → 입력이 없으면 `""`를 반환하는 방어 코드와 `default` 분기로 항상 값을 반환한다. 고정 문구는 하드코딩 말고 i18n에서 읽는다.

**(6)** `core:require`로 불러온 모듈 함수를 그대로 지정하면 `this`가 컨트롤러가 아니다. Walkthrough처럼 `formatter: 'Formatter.statusText.bind($controller)'`로 고친다. `.bind(obj)`는 `this`를 고정한 새 함수를 만든다(JS의 `this`는 호출 방식으로 정해짐). 다른 해결: formatter가 `this`에 의존하지 않도록 ResourceBundle을 인자로 받거나, i18n 텍스트를 바인딩 `parts`로 넘긴다.

**(7)** 컨트롤러 기준으로 함수를 찾고 formatter 안의 `this`는 그 뷰의 컨트롤러다(그래서 `this.getOwnerComponent()` 가능). `statusText` 테스트는 `this`를 흉내 낸 객체로 `formatter.statusText.call(oStub, "A")`. 순수 함수 `statusState`는 바로 테스트. 화면 흐름은 OPA5. formatter는 표시용 **단방향** 변환이다. 입력값을 모델로 되돌리는(parse) 양방향 변환과 검증이 필요하면 데이터 타입(`sap.ui.model.type.*` 또는 커스텀 SimpleType), 간단한 계산은 expression(`{= ${/qty} * ${/price} }`). 여러 값은 `parts: ['TotalPrice', 'CurrencyCode']`.

</details>

---

### D-020. i18n ResourceModel: 설정, getText, 언어 fallback [코드] ★★
<!-- src: U5-022, UB-022, UB-051, MX-078, UB-084 -->
앱 네임스페이스는 `ui5.walkthrough`이고 i18n 파일은 다음과 같다.

```properties
# i18n/i18n.properties (기본)
appTitle=Travel Approval
helloMsg=Hello ____(1)____
bookMsg=Hello {0}, you have {1} new bookings
flightCount={1} has {0} flights
quote=It''s {0}
title=Flights
```
```properties
# i18n/i18n_de.properties
flightCount={1} hat {0} Flüge
```
```json
"i18n": {
  "type": "sap.ui.model.resource.ResourceModel",
  "settings": { "bundleName": "ui5.walkthrough.i18n.i18n.properties" }
}
```
```xml
<Page title="{____(2)____}"><Button text="Say Hello" press=".onSayHello"/></Page>
```
```js
onSayHello: function () {
  var oBundle = this.getView().getModel("i18n").____(3)____();
  MessageToast.show(oBundle.____(4)____("helloMsg", [____(5)____]));   // "Hello Kim"
}
```

(1) 빈칸 (1)~(5)를 채우시오(이름 있는 모델과 ResourceModel 경로 규칙 포함).
(2) 위 설정으로 실행하면 화면에 `appTitle`처럼 키 이름이 보이고 콘솔에 404가 찍힌다. 원인과 수정(대안 포함)을 쓰고, 화면에 키가 보일 때 의심할 3가지를 쓰시오.
(3) 번들 설정을 고친 뒤 사용자 언어가 `de_DE`일 때 결과를 쓰시오.
```js
oBundle.getText("bookMsg", ["Kim", 3]);      // (a)
oBundle.getText("flightCount", [3, "LH"]);   // (b)
oBundle.getText("quote", ["LH"]);            // (c)
oBundle.getText("title");                    // (d)
oBundle.getText("noSuchKey");                // (e)
```
(4) `supportedLocales`/`fallbackLocale` 설정이 없을 때 (가) 언어 `de`, (나) 언어 `ko_KR`이면 UI5가 텍스트를 찾기 위해 참조하는 파일을 순서대로 쓰시오. 키 단위 탐색의 의미도 쓰시오.
(5) UI5가 사용자 언어를 결정하는 우선순위를 쓰고, `supportedLocales`, `fallbackLocale`의 역할과 설정 예를 쓰시오.
(6) properties 파일 인코딩, 작은따옴표, placeholder와 관련된 작성 규칙을 쓰고, XML 뷰에서 파라미터가 있는 텍스트를 쓰는 방법을 쓰시오.

<details><summary>정답·해설</summary>

**(1)** (1) `{0}` (2) `i18n>appTitle` (3) `getResourceBundle` (4) `getText` (5) `"Kim"`
이름 있는 모델은 `모델이름>경로`, ResourceModel의 경로는 슬래시 없이 키 이름. 플레이스홀더는 `{0}`, `{1}` 순서이고 `getText(key, [값 배열])`로 채운다.

**(2)** `bundleName`은 점 표기의 모듈 이름이며 확장자를 붙이지 않는다. 위 설정은 `i18n/i18n/properties.properties`를 찾는다. → `"bundleName": "ui5.walkthrough.i18n.i18n"`(또는 `"bundleUrl": "i18n/i18n.properties"`). ResourceBundle은 키를 못 찾으면 키 문자열을 그대로 돌려주므로, 키가 보이면 ① 번들 경로 오류 ② 키 오타 ③ 모델 이름 불일치(`{i18n>...}`인데 모델 이름이 `I18n` 등)를 의심한다.

**(3)** (a) `Hello Kim, you have 3 new bookings` (b) `LH hat 3 Flüge` (c) `It's LH` (d) `Flights` (e) `noSuchKey`
- 치환 순서는 문장 속 위치가 아니라 번호로 정해진다.
- 작은따옴표는 메시지 형식의 escape 문자라 하나를 쓰려면 `''`. `Don't {0}`처럼 쓰면 치환이 깨진다.
- `title`은 독일어 파일에 없어 기본 파일 값.
- 어디에도 없으면 키 자체 반환(콘솔 경고).

**(4)** (가) `i18n_de.properties` → `i18n_en.properties` → `i18n.properties` (나) `i18n_ko_KR.properties` → `i18n_ko.properties` → `i18n_en.properties` → `i18n.properties`
기본 fallback 로케일이 `en`이라 요청 언어 다음에 영어 파일을 찾고 마지막에 접미어 없는 기본 파일을 쓴다(그래서 `de_DE`는 `i18n_de_DE` → `i18n_de` → `i18n_en` → `i18n`). **키 단위**로 찾으므로 `i18n_ko`에 일부 키만 있으면 나머지는 다음 파일에서 가져오고, 어디에도 없으면 키를 표시한다. 파일이 없으면 404가 나고 다음으로 내려간다.

**(5)** 우선순위(대략): URL 파라미터 `sap-language`/`sap-locale`(또는 `sap-ui-language`) → bootstrap/설정 → 런치패드 사용자 설정(ABAP 로그온 언어) → 브라우저 언어.
`supportedLocales`: 실제로 존재하는 언어 목록. 목록에 없는 언어 파일은 요청하지 않아 불필요한 404를 막는다. `fallbackLocale`: 사용자 언어가 지원 목록에 없을 때 쓸 언어.
```json
"i18n": { "type": "sap.ui.model.resource.ResourceModel",
  "settings": { "bundleName": "zdemo.i18n.i18n",
                "supportedLocales": ["", "ko", "en"], "fallbackLocale": "" } }
```

**(6)** properties 파일은 UTF-8로 저장(예전 ISO-8859-1 시절에는 한글을 `\uXXXX`로 escape). 작은따옴표는 `''`. 문장을 코드에서 이어 붙이지 말고 `{0}` placeholder를 써야 번역이 가능하다. XML에서 파라미터 텍스트는 `parts`(i18n 텍스트 + 데이터 값)와 formatter로 `formatMessage`(`sap/base/strings/formatMessage`)를 쓴다.

</details>

---

### D-021. 데이터 타입(sap.ui.model.type / odata.type)과 입력 검증 [코드] ★★
<!-- src: U5-027, UB-054, UB-085, UB-055 -->
JSONModel 값 `"/fldate": "20261013"`(ABAP DATS 형식 문자열)을 다음처럼 바인딩했다.

```xml
<Text text="{
  path: '/fldate',
  type: 'sap.ui.model.type.Date',
  formatOptions: { source: { pattern: 'yyyyMMdd' }, pattern: 'yyyy.MM.dd' }
}"/>
```

(1) 화면에 표시되는 값을 쓰고, `source.pattern`과 `pattern`의 의미를 쓰시오. 같은 바인딩을 TwoWay Input에 쓰고 사용자가 `2026.12.25`를 입력하면 모델 값은? 형식이 틀리면? `pattern` 대신 `style: 'medium'`을 쓰면?
(2) 데이터 타입을 바인딩에 지정했을 때 일어나는 format, parse, validate를 각각 설명하시오(`formatOptions`, `constraints` 예 포함).
(3) formatter와 비교해 언제 타입을 써야 하는지 쓰시오. 금액과 통화를 함께 다룰 때의 바인딩 형태도 쓰시오.
(4) 데이터 타입 선택으로 **옳지 않은** 것을 고르고 이유를 쓰시오.
① OData `Edm.Decimal` 금액에는 `sap.ui.model.odata.type.Decimal`이나 `sap.ui.model.type.Currency`(금액+통화 composite)를 쓴다.
② JSONModel 숫자에는 `sap.ui.model.type.Float`, `Integer` 같은 simple 타입을 쓴다.
③ OData V4 모델에서는 메타데이터로 OData 타입이 자동 결정되므로 대부분 `type`을 생략해도 된다.
④ `Edm.DateTimeOffset` 값에 `sap.ui.model.type.Date`를 지정하면 시간대가 자동 처리되어 가장 안전하다.
(5) UI5에서 사용자 입력을 검증하는 방법을 쓰시오: 타입 constraints, 이벤트 3가지, `handleValidation`과 메시지 모델(Messaging), 직접 검증(`required`의 한계 포함), 서버 검증.

<details><summary>정답·해설</summary>

**(1)** `2026.10.13`. `source.pattern`은 **모델에 저장된 값의 형식**, `pattern`은 **화면 표시 형식**. 타입은 parse도 하므로 `2026.12.25` 입력 시 모델에는 `20261225`. 형식이 맞지 않으면 `parseError`. `style: 'medium'`이면 사용자 locale에 맞는 형식으로 표시. OData 모델에서는 `sap.ui.model.odata.type.Date`/`DateTimeOffset`을 쓴다.

**(2)**
- **format**: 모델 값 → 화면 문자열. 로케일 맞춤 날짜/숫자/통화(`formatOptions` 예: `{ pattern: 'dd.MM.yyyy' }`, `{ maxFractionDigits: 2 }`).
- **parse**: TwoWay에서 입력 문자열 → 모델 값(숫자, Date 객체 등). 실패 시 `parseError`.
- **validate**: `constraints`(예: `{ minimum: 0, maximum: 100 }`, `maxLength`) 위반 시 `validationError`. 메시지 모델에 등록되면 입력 필드 valueState(빨간 테두리)와 메시지로 자동 표시.

**(3)** formatter는 표시용 단방향이라 입력값을 되돌리지 못하고 검증도 없다. 입력 필드, 로케일 형식, 검증이 필요하면 타입. 표시 텍스트 매핑·아이콘·상태 색 같은 단순 변환은 formatter. 금액: `{ parts: ['TotalPrice', 'CurrencyCode'], type: 'sap.ui.model.type.Currency', formatOptions: { showMeasure: false } }`처럼 두 값을 묶는다. OData 모델은 Edm 타입 기반 `sap.ui.model.odata.type.*`가 메타데이터로 자동 적용되기도 한다(V4는 기본).

**(4)** ④. OData 값에는 OData 형식(JS Date 객체, 문자열 날짜 등)을 이해하는 `sap.ui.model.odata.type.*`(`DateTimeOffset`, `Date`)를 써야 한다. simple 타입을 잘못 쓰면 파싱 오류나 하루 밀림(시간대) 문제가 생긴다. V2는 자동 타입 결정이 제한적이라 명시하는 경우가 많고, V4는 자동 결정된다.

**(5)**
1. **타입과 constraints**: `type: 'sap.ui.model.type.String', constraints: { maxLength: 10, minLength: 1 }`, `Integer`의 `minimum/maximum`, `search`(정규식). 화면 → 모델로 갈 때 parse·validate.
2. **이벤트**: 형식 오류 `parseError`, 제약 위반 `validationError`, 성공 `validationSuccess`.
3. **자동 메시지**: manifest `sap.ui5`에 `"handleValidation": true` → 오류가 메시지 모델(`sap/ui/core/Messaging`, 이전 `sap.ui.getCore().getMessageManager()`)에 등록되고 Input이 `valueState="Error"`와 메시지를 자동 표시. `MessagePopover`로 모아 보여 준다.
4. **직접 검증**: 저장 버튼에서 필수값 검사 후 `setValueState("Error")`, `setValueStateText(...)`. `required="true"`는 별표만 표시할 뿐 검증하지 않는다("required만 넣으면 검증된다"는 흔한 오답).
5. **서버 검증**: 브라우저 검증은 우회될 수 있는 편의 기능이므로 백엔드(RAP validation, Gateway)에서 반드시 다시 검사. 서버 메시지(`sap-message` 헤더, 오류 응답)는 OData 모델이 메시지 모델로 전달한다.

</details>

---

## 7. OData V2 · V4

### D-022. OData V2 모델과 V4 모델 비교, read vs 바인딩, CSRF, Gateway 문제 해결 [개념] ★★
<!-- src: U5-028, MX-086, UB-071, UB-069, UB-065, UB-070 -->
(1) `sap.ui.model.odata.v2.ODataModel`과 `v4.ODataModel`을 CRUD API, 변경 전송(batch/group), 읽기 결과를 코드에서 받는 방법, 기본 바인딩 모드, `$select` 자동 생성 측면에서 표로 비교하시오. "V4에서 create는 어떻게 하나?"에 한 줄로 답하시오.
(2) V4 모델 설명으로 **옳지 않은** 것을 고르고 이유를 쓰시오.
① V2의 `read()` 같은 직접 CRUD 메서드가 없고 `bindList`, `bindContext`로 접근한다.
② 기본 설정에서 변경 요청은 `$auto` 그룹으로 자동으로 `$batch`에 담겨 전송된다.
③ `$$updateGroupId`를 직접 만든 그룹(`"travelGroup"`)으로 주면 `submitBatch("travelGroup")` 때 전송된다.
④ 서버에서 필터·정렬을 하려면 `operationMode: "Server"`를 설정한다.
⑤ V4 모델의 기본 바인딩 모드는 OneWay라서 Input에 입력한 값이 모델에 반영되지 않는다.
(3) V2 화면에서 `oModel.read()`로 받아 JSONModel에 넣는 방식과 컨트롤을 OData 모델에 직접 바인딩하는 방식의 장단점, 각각 적합한 경우를 쓰시오. V4에서 코드로 데이터가 필요할 때는?
(4) manifest에서 OData 모델에 `"preload": true`를 설정했다. 메타데이터 로드 완료를 `attachMetadataLoaded` 대신 `metadataLoaded()` Promise로 기다려야 하는 이유와 코드를 쓰고, 일반 원칙을 쓰시오. preload를 쓰지 말아야 할 모델은?
(5) OData 모델과 CSRF 토큰에 대한 설명으로 **옳지 않은** 것을 고르고, 직접 HTTP를 호출할 때의 절차와 토큰을 미리 받는 모델 파라미터를 쓰시오.
① 모델은 변경 요청 전에 `X-CSRF-Token: Fetch`로 토큰을 받아 POST/PUT/MERGE/DELETE 헤더에 넣는다.
② 토큰 만료로 서버가 403과 `X-CSRF-Token: Required`를 돌려주면 모델은 토큰을 다시 받아 재시도한다.
③ OData 모델을 쓰면 개발자가 직접 토큰 헤더를 넣을 필요가 없다.
④ `jQuery.ajax`나 `fetch`로 같은 서비스에 직접 POST할 때도 UI5가 토큰을 자동으로 넣는다.
⑤ GET 요청에는 CSRF 토큰이 필요 없다.
(6) OData 문제를 조사할 때의 트랜잭션 표를 채우시오.

| 목적 | 트랜잭션 |
|---|---|
| 프런트엔드 Gateway 오류 로그("HTTP 500") | (a) |
| 백엔드(비즈니스 로직) 오류 로그 | (b) |
| UI 없이 서비스 URL 직접 호출 | (c) |
| 메타데이터 캐시 삭제(프런트/백엔드) | (d) |
| V2 서비스 등록·활성화, ICF·system alias | (e) |
| V4 서비스 그룹 게시 | (f) |
| 요청·응답 payload 기록 | (g) |

브라우저에서 `$batch` 오류를 확인하는 방법도 쓰시오.

<details><summary>정답·해설</summary>

**(1)**

| 관점 | V2 Model | V4 Model |
|---|---|---|
| CRUD API | 모델에 `read`, `create`, `update`, `remove`, `callFunction`. 경로 문자열 + success/error 콜백 | 모델에 CRUD 메서드 **없음**. 읽기 = list/context 바인딩, 생성 = `ODataListBinding.create()`, 수정 = `Context.setProperty()`(또는 TwoWay), 삭제 = `Context.delete()`, 액션 = `bindContext("...Action(...)")` + `invoke()`(예전 `execute()`) |
| batch/group | `useBatch`(기본 true). `setDeferredGroups([...])` 그룹은 쌓았다가 `submitChanges()`로 한 번에. 변경 추적 `hasPendingChanges`/`resetChanges` | `groupId`(읽기), `updateGroupId`(변경). `$auto`(자동 batch, 기본), `$direct`(batch 없이 바로), 사용자 정의 이름(수동, `submitBatch("이름")`). `$$updateGroupId` 바인딩 파라미터 |
| 읽기 결과 | `read`의 success `oData.results`, 또는 바인딩 후 `getObject` | Promise: `requestObject()`, `requestProperty()`, `oListBinding.requestContexts()`. 동기 `getObject`는 이미 읽힌 값만 |
| 기본 바인딩 모드 | OneWay | TwoWay |
| `$select` | 직접 지정 | `autoExpandSelect: true`면 바인딩된 속성만 `$select`/`$expand` 자동 생성 |

"모델이 아니라 **list binding의 `create()`**." RAP OData V4 UI 서비스, Fiori Elements V4가 V4 모델을 쓴다.

**(2)** ⑤. V4 기본은 TwoWay. 입력값이 컨텍스트에 반영되고 updateGroup 설정에 따라 PATCH가 나간다. 직접 만든 그룹이면 저장 버튼에서 `submitBatch`, 취소는 `resetChanges`.

**(3)**
- **직접 바인딩**: 필요한 데이터만 요청(growing 페이징, `$select`), 캐시·변경 추적·batch·CSRF·메시지 처리 자동, 정렬·필터도 서버. 코드가 적고 성능이 좋아 **기본 방식**.
- **read + JSONModel**: 응답 가공·병합, 여러 엔티티를 조합한 화면 전용 구조, 저장하지 않을 임시 편집 데이터, 한 번 쓰는 계산(차트용 집계)에. 단점: 페이징·변경 추적·저장을 직접 구현, 데이터가 많으면 전부 받아 느림.
- V4에는 `read`가 없고 `bindList(...).requestContexts()`나 `bindContext(...).requestObject()`. 면접관은 "무조건 read로 JSONModel에"를 좋지 않게 본다.

**(4)** preload를 켜면 모델이 컴포넌트 코드보다 먼저 생성되어 메타데이터를 component preload와 병렬로 받는다. 앱이 `attachMetadataLoaded`를 등록하기 전에 이벤트가 이미 발생했을 수 있어 핸들러가 영원히 안 불릴 수 있다. Promise는 끝난 뒤 `then`을 붙여도 실행된다.
```js
oModel.metadataLoaded(true).then(() => { /* 준비 완료 */ }, () => { /* 오류 화면 */ });
```
V4는 `getMetaModel().requestObject(...)` 등 Promise API. 원칙: "이미 일어났을 수 있는 일회성 사건은 이벤트가 아니라 Promise로 기다린다." preload는 원격(OData) 모델에만 의미가 있고 로컬 JSON이나 component preload에 포함된 i18n에는 쓰지 않는다.

**(5)** ④. 토큰 처리는 OData 모델 내부 기능이다. 직접 호출하면 먼저 GET(HEAD)에 `X-CSRF-Token: Fetch`를 보내 응답 헤더의 토큰을 받고 변경 요청에 직접 넣는다(V2 모델의 `getSecurityToken()`/`refreshSecurityToken()`으로 얻을 수도 있음). 미리 받기: V2 `earlyTokenRequest`, V4 `earlyRequests`(첫 저장 지연 감소).

**(6)** (a) `/IWFND/ERROR_LOG` (b) `/IWBEP/ERROR_LOG` (c) `/IWFND/GW_CLIENT` (d) `/IWFND/CACHE_CLEANUP`(프런트), `/IWBEP/CACHE_CLEANUP`(백엔드) (e) `/IWFND/MAINT_SERVICE` (f) `/IWFND/V4_ADMIN` (g) `/IWFND/TRACES`
`/IWFND/ERROR_LOG`에서 오류 요청을 골라 GW Client로 재현할 수 있다. 브라우저 F12 네트워크 탭에서 `$batch` 응답 본문 안의 개별 응답 상태를 확인한다(batch 자체는 200이어도 내부 요청이 실패할 수 있음).

</details>

---

### D-023. OData V2 모델: read·CRUD, deferred group과 $batch, createEntry, growing [코드] ★★★
<!-- src: U5-029, UB-058, UB-060, UB-061, MX-087, UB-064, UB-062 -->
V2 서비스(엔티티셋 `TravelSet`, 키 `TravelID`; `FlightSet`, `BookingSet`)를 다루는 코드다.

```js
var oModel = this.getView().getModel();
// 1) 조건 읽기 + 연관 함께 + 필요한 필드만
oModel.____(1)____("/FlightSet", {
  ____(2)____: [ new Filter("Carrid", FilterOperator.EQ, "LH") ],
  ____(3)____: { "____(4)____": "ToBookings", "$select": "Carrid,Connid,Fldate,Price,ToBookings" },
  ____(5)____: (oData) => { this.getView().getModel("view").setProperty("/flights", oData.____(6)____); },
  error: (oError) => { MessageBox.error(oError.message); }
});
// 2) 키 경로 만들기: "/TravelSet('00000042')"
var sPath = oModel.____(7)____("/TravelSet", { TravelID: "00000042" });
// 3) 수정(바꿀 속성만)  4) 삭제
oModel.____(8)____(sPath, { Description: "Changed" }, { success: fnOk, error: fnErr });
oModel.____(9)____(sPath, { success: fnOk, error: fnErr });
// 5) setProperty로 바꾼 값을 한 번에 전송
oModel.setProperty(sPath + "/Description", "Again");
oModel.____(10)____({ success: fnOk, error: fnErr });
```

(1) 빈칸 (1)~(10)을 채우고, 컬렉션/단건 결과 형태, `createKey`를 쓸 수 있는 시점, `update`가 보내는 HTTP 메서드, `setProperty` 변경이 쌓이는 그룹을 쓰시오. 콜백을 화살표 함수로 쓴 이유와, 화면 표시용 데이터에 이 방식이 권장되지 않는 이유도 쓰시오.
(2) `useBatch: true`에서 아래를 실행했다. (a) ③ 시점까지 서버로 간 MERGE 수 (b) ④ 이후 HTTP 요청 형태 (c) ② 직후 `hasPendingChanges(true)`와 `hasPendingChanges()`의 값을 쓰시오. `setDeferredGroups`의 함정과 deferred가 아닌 그룹의 동작도 쓰시오.
```js
oModel.setDeferredGroups(["saveGroup"]);                                                          // ①
oModel.update("/BookingSet(Carrid='LH',Bookid='1')", { Class: "C" }, { groupId: "saveGroup" });
oModel.update("/BookingSet(Carrid='LH',Bookid='2')", { Class: "Y" }, { groupId: "saveGroup" });   // ②
console.log("waiting");                                                                           // ③
oModel.submitChanges({ groupId: "saveGroup", success: () => {}, error: () => {} });               // ④
```
(3) `$batch`와 changeset에 대해 **옳지 않은** 것을 고르고 이유를 쓰시오. SEGW와 RAP에서 changeset은 어떻게 처리되는가?
① deferred 그룹의 요청은 `submitChanges` 때 하나의 `$batch`로 전송된다. ② 같은 `changeSetId`의 변경 요청들은 하나의 changeset으로 함께 성공하거나 함께 실패한다. ③ `useBatch: false`면 각 요청이 개별 HTTP 요청으로 간다. ④ `read()`도 changeset 안에 들어가 변경 요청과 함께 원자적으로 처리된다.
(4) 생성 다이얼로그를 열 때 `createEntry`로 빈 엔트리를 만들고 저장에서 `submitChanges`를 부른다. 사용자가 [취소]로 닫았다가 다시 열어 저장하면 레코드가 두 건 생긴다. 원인과 수정 코드를 쓰고, 저장 쪽 보완점과 V4에서의 취소 방법을 쓰시오.
```js
onOpenCreate() {
  const oCtx = this.getView().getModel().createEntry("/TravelSet", { properties: { AgencyID: "070001" } });
  this.byId("createDialog").setBindingContext(oCtx);
  this.byId("createDialog").open();
},
onCancel() { this.byId("createDialog").close(); },
onSave()   { this.getView().getModel().submitChanges(); this.byId("createDialog").close(); }
```
(5) V2 리스트에 다음 필터를 적용했다(`Seatsmax`는 `Edm.Int32`, `Planetype`은 `Edm.String`). 생성되는 `$filter`를 쓰고, V4 모델이면 무엇이 달라지는지, `Edm.Decimal` 리터럴 표기를 쓰시오.
```js
oBinding.filter([ new Filter("Seatsmax", FilterOperator.GT, 200), new Filter("Planetype", FilterOperator.Contains, "A3") ]);
```
(6) `/FlightSet`에 1,000건이 있다. `<Table items="{/FlightSet}" growing="true" growingThreshold="20" growingScrollToLoad="false">`가 처음 표시된 뒤 [More]를 두 번 눌렀다. GET 세 건의 `$skip`/`$top`과 표시 행 수를 쓰시오. growing을 안 쓰면 몇 건을 요청하는가? `growingScrollToLoad="true"`의 조건과 전체 건수 표시 방법도 쓰시오.

<details><summary>정답·해설</summary>

**(1)** (1) `read` (2) `filters` (3) `urlParameters` (4) `$expand` (5) `success` (6) `results` (7) `createKey` (8) `update` (9) `remove` (10) `submitChanges`
- 컬렉션은 success의 `oData.results` 배열, 단건은 객체 그대로. `read`는 비동기.
- `createKey`는 메타데이터의 키 정의·타입으로 경로를 만들므로 메타데이터 로드 후에 쓴다.
- V2 `update`는 기본 MERGE(설정에 따라 PUT/PATCH).
- `setProperty`/TwoWay 변경은 기본 deferred 그룹 `"changes"`에 쌓여 `submitChanges` 전까지 전송되지 않는다(`hasPendingChanges()`로 확인, `resetChanges()`로 취소).
- 화살표 함수라 `this`(컨트롤러)가 유지된다(D-035).
- 화면 표시용이면 JSONModel에 복사하기보다 OData 모델에 직접 바인딩하는 것이 캐시·페이징·변경 추적 면에서 권장된다.

**(2)** (a) 0건 (b) `$batch` POST 1개, 안에 MERGE 2건 (c) `hasPendingChanges(true)` → `true`, 인자 없이 → `false`
deferred 그룹 요청은 `submitChanges` 때 하나의 `$batch`로 묶인다. `hasPendingChanges()`는 기본적으로 `createEntry`/`setProperty`로 생긴 클라이언트 변경만 보고, 인자 `true`를 주어야 `create`/`update`/`remove`로 쌓인 deferred 요청까지 본다. `setDeferredGroups`는 목록을 **교체**하므로 기본 `"changes"`를 계속 deferred로 두려면 `["changes", "saveGroup"]`. deferred가 아닌 그룹은 같은 이벤트 루프 안의 요청들이 자동으로 하나의 batch로 묶여 바로 전송된다. `resetChanges()`로 쌓인 변경을 버린다.

**(3)** ④. `$batch`에서 GET은 changeset 밖에 따로 들어간다. changeset에는 변경 요청(POST/PUT/PATCH/MERGE/DELETE)만 들어가고 changeset이 원자성의 단위다. SEGW는 `CHANGESET_BEGIN`/`CHANGESET_END`, RAP는 changeset 하나를 하나의 트랜잭션(저장 시퀀스)으로 처리한다.

**(4)** `createEntry`는 엔트리를 pending change(기본 deferred 그룹 `changes`)로 만든다. 취소 때 다이얼로그만 닫고 엔트리를 지우지 않아 다음 `submitChanges`에서 이전 것과 새 것이 함께 POST된다.
```js
onCancel() {
  const oDialog = this.byId("createDialog");
  this.getView().getModel().deleteCreatedEntry(oDialog.getBindingContext());
  oDialog.close();
}
```
저장에도 `success`/`error` 콜백을 두어 실패 시 닫지 않고 메시지를 보여 준다. V4는 `oListBinding.create()` 컨텍스트를 `oContext.delete()`로 취소(transient면 서버 요청 없이 제거).

**(5)** V2: `$filter=Seatsmax gt 200 and substringof('A3',Planetype)`. V4: `$filter=Seatsmax gt 200 and contains(Planetype,'A3')`. 경로가 다르면 AND, 같으면 OR. V2 `substringof(값, 속성)`과 V4 `contains(속성, 값)`은 인자 순서가 반대. `Edm.Decimal`이면 V2 리터럴에 `200m`처럼 접미사.

**(6)** `$skip=0&$top=20` → `$skip=20&$top=20` → `$skip=40&$top=20`, 표시 60행. `growingThreshold`는 한 번에 요청하는 건수. growing을 안 쓰면 V2 리스트 바인딩은 size limit(기본 100)만큼 요청. `growingScrollToLoad="true"`면 스크롤 끝에서 자동 로드되며 테이블이 스크롤 가능한 컨테이너(예: `Page`) 안에 있어야 한다. 전체 건수("Flights (1000)")는 `updateFinished` 이벤트의 `total` 파라미터.

</details>

---

### D-024. OData V4 모델: 바인딩 파라미터, update group, 생성, action, $expand [코드] ★★★
<!-- src: U5-030, UB-066, UB-067, UB-068, MX-080, UB-063 -->
OData V4 모델(RAP 서비스)의 Travel을 다루는 화면이다.

```xml
<Table id="travelTable" growing="true" growingThreshold="20" items="{
    path: '/____(1)____',
    parameters: {
      $count: true,
      ____(2)____: 'TravelID,Description,TotalPrice,CurrencyCode',
      ____(3)____: '_Agency($select=Name)',
      $orderby: 'TravelID desc',
      ____(4)____: 'travelGroup'
    },
    ____(5)____: [ { path: 'OverallStatus', operator: 'EQ', value1: 'O' } ] }">
  <columns> ... </columns>
  <items>
    <ColumnListItem type="Navigation" press=".onPress">
      <cells>
        <ObjectIdentifier title="{TravelID}" text="{Description}"/>
        <Text text="{____(6)____}"/>
        <ObjectNumber number="{ parts: ['TotalPrice', 'CurrencyCode'],
                                type: 'sap.ui.model.____(7)____', formatOptions: { showMeasure: false } }"
                      unit="{CurrencyCode}"/>
      </cells>
    </ColumnListItem>
  </items>
</Table>
```
```js
var oModel = this.getView().getModel();     // v4.ODataModel
// 코드로 list binding 만들기
var oListBinding = oModel.____(8)____("/Travel", undefined, undefined, undefined, { $$updateGroupId: "travelGroup" });
var oNewContext = oListBinding.____(9)____({ Description: "Seoul trip", CurrencyCode: "EUR" });
onSave: function () {
  oModel.____(10)____("travelGroup");
  oNewContext.created().then(function () { MessageToast.show("saved"); });
},
onCancel: function () { oModel.____(11)____("travelGroup"); },
// 단건 읽기
oModel.____(12)____("/Travel(42)").____(13)____().then(function (oTravel) { console.log(oTravel.Description); });
```

(1) 빈칸 (1)~(13)을 채우시오. `$`와 `$$` 접두어의 차이, `$auto`/`$direct`/애플리케이션 그룹의 전송 방식, `created()`의 의미, `autoExpandSelect`의 효과, 정적 `filters`가 서버로 가는 조건을 쓰시오.
(2) SimpleForm이 `binding="{ path: '/Travel(1)', parameters: { $$updateGroupId: 'myGroup' } }"`이고 `Description`의 서버 값은 `"Trip"`이다. 사용자가 `"Business trip"`으로 바꾸고 Enter를 눌렀다. (a) PATCH가 전송되었는가 (b) `hasPendingChanges("myGroup")` (c) `resetChanges("myGroup")` 후 Input 값과 `hasPendingChanges("myGroup")`을 쓰시오. `$$updateGroupId`를 지정하지 않았다면?
(3) bound action `acceptTravel`(네임스페이스 `com.sap.gateway.srvd.zui_travel.v0001`)을 선택된 Travel로 호출하는 코드의 빈칸을 채우고, `(...)`의 의미, 파라미터 넣는 법, 오류 처리를 쓰시오.
```js
async onAccept() {
  const oContext = this.byId("travelTable").getSelectedContexts()[0];
  const oAction = this.getView().getModel().bindContext(
    "com.sap.gateway.srvd.zui_travel.v0001.acceptTravel____(a)____", ____(b)____);
  try { await oAction.____(c)____(); MessageToast.show("승인됨"); }
  catch (oError) { MessageBox.error(oError.message); }
}
```
(4) 키 경로 표기: 키가 문자열이면, draft 서비스면 경로를 어떻게 쓰는가?
(5) 상세 화면에서 항공편 헤더와 예약 목록을 보여 준다. (가) 예약을 navigation property로 따로 바인딩할 때와 (나) `$expand`로 한 번에 읽을 때의 요청 차이와 장단점을 쓰고, V2 `bindElement`에서 `$expand`와 busy 처리를 지정하는 코드를 쓰시오. V4 표기와 SEGW 백엔드 주의점도 쓰시오.

<details><summary>정답·해설</summary>

**(1)** (1) `Travel`(엔터티 집합) (2) `$select` (3) `$expand` (4) `$$updateGroupId` (5) `filters` (6) `_Agency/Name` (7) `type.Currency` (8) `bindList` (9) `create` (10) `submitBatch` (11) `resetChanges` (12) `bindContext` (13) `requestObject`
- `$`로 시작 = OData 시스템 쿼리 옵션(`$select`, `$expand`, `$orderby`, `$count`), `$$`로 시작 = UI5 모델 내부 설정(`$$groupId`, `$$updateGroupId`, `$$operationMode`).
- `$auto` = 자동 batch 전송, `$direct` = batch 없이 개별 요청, `$`로 시작하지 않는 애플리케이션 그룹 = submit mode API라 `submitBatch` 호출 때까지 PATCH/POST가 쌓인다.
- `create`가 반환한 컨텍스트는 아직 서버에 없는 transient 상태이고, `created()` Promise는 서버 저장이 끝나면 resolve.
- `autoExpandSelect: true`면 바인딩된 경로로 `$select`/`$expand`를 자동 계산(필요한 열만 받음).
- 정적 `filters`는 operationMode Server에서 `$filter`로 전송. 연관 값은 `내비게이션속성/속성` 경로. 금액+통화는 Currency 타입에 `parts`.
- `bindList` 인자: (경로, 컨텍스트, sorter, filter, 파라미터). 읽기는 Promise(`requestObject`, `requestProperty`).

**(2)** (a) 전송되지 않았다 (b) `true` (c) Input은 `Trip`으로 돌아가고 `false`. 애플리케이션 그룹(`myGroup`)은 submit mode API라 `submitBatch("myGroup")` 전까지 큐에만 쌓이고, `resetChanges`는 그 그룹의 two-way 변경을 버리고 원래 값을 복원한다. 지정하지 않으면 기본 `$auto`라 Enter 직후 자동으로 batch 전송. 이 구조로 폼의 [저장]/[취소]를 구현한다.

**(3)** (a) `(...)` (b) `oContext` (c) `invoke`(1.123 이전은 `execute`)
`(...)`는 deferred operation binding으로 바인딩 생성 시 요청하지 않고 `invoke()` 때 POST한다. bound action은 대상 컨텍스트를 두 번째 인자로 주어 상대 경로로 바인딩. 파라미터는 `oAction.setParameter("name", value)`. 반환 Promise는 서버 오류 시 reject되고 서버 메시지는 메시지 모델로 전달된다.

**(4)** 정수 키는 `/Travel(42)`, 문자열 키는 `/Travel('42')`, draft 서비스는 키 전체 `/Travel(TravelUUID=...,IsActiveEntity=true)`.

**(5)**
- (가) 헤더를 `bindElement("/FlightSet(...)")`, 테이블을 상대 경로 `items="{ToBookings}"`로 바인딩하면 헤더 GET과 `FlightSet(...)/ToBookings` GET이 각각 발생(V2는 한 `$batch` 안 두 요청). 예약 목록에 growing·정렬·필터를 서버에서 독립적으로 적용 가능.
- (나) `$expand=ToBookings`로 한 번의 GET에 함께 받는다. 요청 수는 줄지만 하위 데이터가 많으면 응답이 커지고 하위 목록의 서버 페이징은 못 쓴다.
```js
this.getView().bindElement({
  path: "/FlightSet(Carrid='LH',Connid='0400',Fldate=datetime'2026-10-13T00:00:00')",
  parameters: { expand: "ToBookings" },          // V2
  events: {
    dataRequested: () => this.getView().setBusy(true),
    dataReceived:  () => this.getView().setBusy(false)
  }
});
```
V4는 `parameters: { $expand: "_Booking" }`처럼 `$` 접두어. SEGW에서는 `GET_EXPANDED_ENTITY`를 구현하지 않으면 navigation마다 GET_ENTITYSET이 반복 호출되어 느릴 수 있다(RAP은 프레임워크가 처리).

</details>

---

## 8. 라우팅

### D-025. routing 설정, 패턴 매칭, FCL, 쿼리 파라미터, 라우팅 이벤트 [코드] ★★★
<!-- src: U5-031, U5-032, UB-075, UB-074, UB-077, UB-072 -->
루트 뷰 `App.view.xml`에 `<App id="app"/>`이 있다.

```json
"routing": {
  "config": {
    "routerClass": "sap.m.routing.Router",
    "type": "View", "viewType": "XML", "path": "my.travel.view",
    "____(1)____": "app",
    "____(2)____": "pages",
    "async": true,
    "____(3)____": { "target": "notFound" }
  },
  "routes": [
    { "pattern": "____(4)____", "name": "list", "target": "list" },
    { "pattern": "travel/____(5)____", "name": "detail", "target": "detail" }
  ],
  "____(6)____": {
    "list":     { "id": "list",     "name": "List" },
    "detail":   { "id": "detail",   "name": "Detail" },
    "notFound": { "id": "notFound", "name": "NotFound" }
  }
}
```

(1) 빈칸 (1)~(6)을 채우시오((4)는 해시가 없을 때 첫 화면, (5)는 필수 파라미터 `travelId`). route와 target의 역할을 각각 쓰고, `sap.m.routing.Router`가 하는 일을 쓰시오.
(2) 다른 앱의 route가 아래 순서로 정의되어 있고(`greedy` 없음, `bypassed`에 notFound target), 해시 (a)~(f)에 매칭되는 route 이름(없으면 "bypassed")과 `arguments`를 쓰시오. `{param}`과 `:param:`의 차이, 매칭 규칙, 그 밖의 패턴 문법을 쓰시오.
```json
"routes": [
  { "pattern": "",                            "name": "home" },
  { "pattern": "product/{id}",                "name": "product" },
  { "pattern": "product/{id}/supplier/:sid:", "name": "supplier" },
  { "pattern": "settings",                    "name": "settings" }
]
```
(a) `#` (b) `#product/5` (c) `#product/5/supplier` (d) `#product/5/supplier/7` (e) `#product` (f) `#settings/x`
(3) 검색어와 정렬 기준을 URL에 남겨 북마크하려 한다. 빈칸을 채우고 결과 해시, 값의 타입 주의점, 세 번째 인자의 의미를 쓰시오.
```json
{ "pattern": "flights____(가)____", "name": "flights", "target": "flights" }
```
```js
oRouter.navTo("flights", { "____(나)____": { search: "LH", sortField: "Price", sortDescending: true } }, ____(다)____);
_onMatched(oEvent) {
  const oQuery = oEvent.getParameter("arguments")["____(나)____"] || {};
  this._applySearch(oQuery.search);
}
```
((가)는 쿼리가 **선택**인 패턴)
(4) rootView가 `<f:FlexibleColumnLayout id="fcl"/>`인 목록(왼쪽)·상세(가운데) 2열 앱의 빈칸을 채우시오. FCL의 aggregation 3개, 레이아웃을 URL에 반영하는 방법, 그 밖의 레이아웃 값을 쓰시오.
```json
"config": { "routerClass": "____(a)____", "controlId": "____(b)____", ... },
"routes": [
  { "pattern": ":layout:", "name": "list", "target": ["list"] },
  { "pattern": "detail/{id}/{layout}", "name": "detail", "target": ["list", "detail"] }
],
"targets": {
  "list":   { "name": "List",   "controlAggregation": "____(c)____" },
  "detail": { "name": "Detail", "controlAggregation": "____(d)____" }
}
```
```js
this.getOwnerComponent().getRouter().navTo("detail", { id: sId, layout: "____(e)____" });  // 상세를 넓게 보는 2열
```
(5) `oRouter.navTo("notFound")`(notFound route가 있다고 가정)와 `oRouter.getTargets().display("notFound")`의 차이와 각각 쓰는 경우, display 화면에서 "뒤로"의 주의점을 쓰시오.
(6) 라우팅 이벤트 설명으로 **옳지 않은** 것을 고르고 바르게 고치시오.
① `Route#attachPatternMatched`: 그 route 패턴이 해시와 직접 일치할 때만 발생.
② `Route#attachMatched`: 그 route가 일치할 때, 그 route를 부모로 하는 중첩 route가 일치할 때도 발생.
③ `Router#attachRouteMatched`: 어느 route든 일치하면 발생.
④ `Router#attachBypassed`: 어떤 route와도 일치하지 않는 해시일 때 발생.
⑤ `attachPatternMatched`는 뷰가 처음 생성될 때 한 번만 발생하므로 데이터 바인딩에는 `onInit`이 더 적합하다.

<details><summary>정답·해설</summary>

**(1)** (1) `controlId` (2) `controlAggregation` (3) `bypassed` (4) `""` (5) `{travelId}` (6) `targets`
route = "URL 해시 패턴 → 이름(+target)", target = "어떤 뷰를 어느 컨테이너(controlId)의 어떤 aggregation(pages)에 넣을지". 하나의 route가 여러 target을 가질 수 있다(FCL의 begin/mid 열). `sap.m.routing.Router`는 `sap.m.App`/`NavContainer`의 화면 전환 애니메이션을 처리한다.

**(2)** (a) home, arguments 없음 (b) product, `{ id: "5" }` (c) supplier, `{ id: "5" }`(sid는 undefined) (d) supplier, `{ id: "5", sid: "7" }` (e) bypassed(필수 `{id}` 없음) (f) bypassed(`settings`는 정확히 `settings`만)
`{param}` 필수, `:param:` 선택. 패턴은 해시 **전체**와 일치해야 하고 정의 순서대로 검사해 처음 일치한 route만 실행된다. (b)는 supplier의 고정 구간 `supplier`가 없어 product만 일치, `{id}`는 한 구간만 받으므로 (c)는 product와 맞지 않는다. 값은 문자열("5"). 나머지를 모두 받는 `:all*:`(rest as string), 쿼리 `{?query}`/`:?query:`도 있다. 어디에도 안 맞으면 router의 `bypassed` 이벤트와 bypassed target 표시.

**(3)** (가) `:?query:` (나) `?query` (다) `true`
`{?query}`는 필수, `:?query:`는 선택 쿼리 파라미터. 결과 해시 `#/flights?search=LH&sortField=Price&sortDescending=true`. 값은 문자열로 돌아오므로 `sortDescending === "true"`처럼 비교. 세 번째 인자 `true`(bReplace)는 히스토리에 새 항목을 만들지 않고 현재 항목을 교체한다.

**(4)** (a) `sap.f.routing.Router` (b) `fcl` (c) `beginColumnPages` (d) `midColumnPages` (e) `TwoColumnsMidExpanded`
FCL aggregation: `beginColumnPages`, `midColumnPages`, `endColumnPages`. `sap.f.routing.Router`는 FCL 열 전환 애니메이션 처리. 레이아웃을 route 파라미터로 받아 `patternMatched`에서 FCL `setLayout`(또는 layout 바인딩 모델)에 반영하면 URL로 레이아웃까지 북마크된다. 다른 값: `OneColumn`, `TwoColumnsBeginExpanded`, `ThreeColumnsMidExpanded`, `MidColumnFullScreen` 등(`sap.f.LayoutType`).

**(5)** `navTo(route)`: route로 이동해 URL 해시가 바뀌고 히스토리에 남으며 route의 target들이 표시된다(북마크 가능한 전환). `getTargets().display(target)`: target(뷰)만 표시, 해시 그대로, route 이벤트도 없음. "존재하지 않는 주문번호"처럼 URL은 사용자가 입력한 그대로 두고 오류 화면만 보여 줄 때나 해시와 무관한 내부 전환에. display로 띄운 화면에서 "뒤로"를 누르면 해시 변화가 없었으므로 그 이전 해시로 간다. 그래서 not found 뷰의 뒤로 버튼은 `display(..., { fromTarget })`로 받은 정보로 직접 돌아가게 구현하기도 한다.

**(6)** ⑤. `patternMatched`는 해시가 그 route와 일치할 **때마다**(같은 뷰를 재사용해도) 발생하므로 파라미터 기반 바인딩은 여기서 한다. `onInit`은 뷰 인스턴스당 한 번(D-009). 상세 컨트롤러는 `onInit`에서 `getRoute("detail").attachPatternMatched(this._onMatched, this)`를 한 번 등록한다. `attachRouteMatched`(Router)와 `attachMatched`(Route)는 하위 route까지 포함해 발생한다.

</details>

---

### D-026. 목록→상세 이동, 뒤로 가기, 딥 링크 [작성] ★★
<!-- src: U5-033, U5-034, MX-083, UB-073, UB-076 -->
route `detail`의 패턴은 `travel/{travelId}`, 기본 모델은 OData V4다. `History`는 `sap/ui/core/routing/History`로 받았다.

(1) 다음 세 메서드를 작성하시오.
- List 컨트롤러 `onPress(oEvent)`: 눌린 항목의 `TravelID`로 detail route로 이동
- Detail 컨트롤러 `onInit`과 `_onMatched`: 파라미터로 뷰에 element binding(`/Travel(<id>)`, `_Booking` 함께 읽기)
- Detail 컨트롤러 `onNavBack`: 앱 안의 이전 화면이 있으면 브라우저 뒤로, 없으면 list route로 이동(history 대체)
(2) (1)의 채점 포인트 6가지를 쓰시오. `attachPatternMatched`와 `attachRouteMatched`의 차이도 쓰시오.
(3) TravelID가 `Edm.String`이면 path를 어떻게 쓰는가? draft BO의 활성 인스턴스 경로는? 키 타입을 틀리면? 키를 직접 조립하지 않는 대안은?
(4) 다음 코드에서 잘못된 곳 3가지를 찾아 이유와 함께 고치시오. route 이름과 패턴 파라미터 이름의 관계도 쓰시오.
```js
onPress: function (oEvent) {
  var oCtx = oEvent.getSource().getBindingContext();
  this.getOwnerComponent().getRouter().navTo("detail", { id: oCtx.getProperty("TravelID") });
},
onInit: function () {
  this.getOwnerComponent().getRouter().getRoute("detail").attachPatternMatched(this._onObjectMatched);
},
_onObjectMatched: function (oEvent) {
  var sId = oEvent.getParameter("travelId");
  this.getView().bindElement("/Travel(" + sId + ")");
}
```
(5) 다른 앱(JSONModel `invoice`)의 route `detail` 패턴은 `detail/{invoicePath}`이다. 아래처럼 이동하면 상세가 아니라 not found가 뜨고 URL은 `#/detail/Invoices/3`이 된다. 원인과 수정 코드(상세 쪽 포함)를 쓰고, 실무에서 더 권장되는 방식을 쓰시오.
```js
onPress(oEvent) {
  const oItem = oEvent.getSource();
  this.getOwnerComponent().getRouter().navTo("detail", {
    invoicePath: oItem.getBindingContext("invoice").getPath().substr(1)   // "Invoices/3"
  });
}
```
(6) 목록에서 선택한 객체를 `this.getOwnerComponent().selectedFlight`에 넣고 상세 `_onMatched`에서 그 값으로 `new JSONModel(oFlight)`을 만들었다. 상세에서 F5를 누르거나 URL을 동료에게 보내면 상세가 빈다. 원인과 올바른 설계(V2 `createKey` 코드 포함), 목록을 거쳐 올 때와 직접 들어올 때의 요청 차이, 키가 없을 때 처리를 쓰시오.

<details><summary>정답·해설</summary>

**(1)**
```js
// List.controller.js
onPress: function (oEvent) {
  var oCtx = oEvent.getSource().getBindingContext();
  this.getOwnerComponent().getRouter().navTo("detail", { travelId: oCtx.getProperty("TravelID") });
},

// Detail.controller.js
onInit: function () {
  this.getOwnerComponent().getRouter().getRoute("detail").attachPatternMatched(this._onMatched, this);
},
_onMatched: function (oEvent) {
  var sId = oEvent.getParameter("arguments").travelId;
  this.getView().bindElement({ path: "/Travel(" + sId + ")", parameters: { $expand: "_Booking" } });
},
onNavBack: function () {
  var sPreviousHash = History.getInstance().getPreviousHash();
  if (sPreviousHash !== undefined) {
    window.history.go(-1);
  } else {
    this.getOwnerComponent().getRouter().navTo("list", {}, true);   // true = replace
  }
}
```

**(2)** ① `navTo(이름, 파라미터 객체)` ② `attachPatternMatched(handler, this)`의 두 번째 인자 `this` ③ `getParameter("arguments").travelId` ④ `bindElement` ⑤ `getPreviousHash() !== undefined` ⑥ `navTo`의 세 번째 인자 `true`(replace). `attachPatternMatched`는 해당 route만, `attachRouteMatched`는 하위 route까지 포함.

**(3)** 문자열 키는 따옴표: `"/Travel('" + sId + "')"` → `/Travel('00000001')`. draft BO는 키 두 개: `/Travel(TravelID='00000001',IsActiveEntity=true)`. 정수 키(Edm.Int32 등)는 따옴표 없이. 키 타입을 틀리면 서버가 400. 특수문자가 있는 값은 `encodeURIComponent`. 대안: 목록 컨텍스트의 `getCanonicalPath()`.

**(4)**
1. `navTo` 파라미터 이름이 `id`인데 패턴 필수 파라미터는 `travelId`. 필수 세그먼트 값이 없어 URL을 만들 수 없으므로 오류가 나고 이동하지 않는다 → `{ travelId: ... }`.
2. `attachPatternMatched`에 리스너 객체를 안 줘서 핸들러의 `this`가 컨트롤러가 아님 → `this.getView()`에서 TypeError → `attachPatternMatched(this._onObjectMatched, this)`.
3. 라우트 파라미터는 `arguments` 객체 안에 있다. `getParameter("travelId")`는 undefined → `/Travel(undefined)` → `oEvent.getParameter("arguments").travelId`.
route 이름(`"detail"`)과 패턴 파라미터 이름(`travelId`)은 서로 다른 개념이다.

**(5)** 값 `Invoices/3`의 `/` 때문에 해시가 `detail/Invoices/3`으로 3단계가 되어 `detail/{invoicePath}`(2단계)와 일치하지 않는다. 인코딩해 넘기고 상세에서 디코딩한다.
```js
// 목록
invoicePath: window.encodeURIComponent(oItem.getBindingContext("invoice").getPath().substr(1))   // "Invoices%2F3"
// 상세 _onObjectMatched
this.getView().bindElement({
  path: "/" + window.decodeURIComponent(oEvent.getParameter("arguments").invoicePath),
  model: "invoice"
});
```
실무에서는 경로 전체 대신 키 값만(`detail/{carrid}/{connid}`) 넘기고 상세에서 `createKey`(V2)나 문자열 조합으로 경로를 만드는 방식이 더 읽기 쉽다. 키에 특수문자가 있을 수 있으면 항상 인코딩.

**(6)** 상세가 목록에서 메모리에 넣어 둔 값에 의존한다. 새로 고침·링크로 바로 상세 해시에 들어오면 목록을 거치지 않아 `undefined`. 상세는 **route 파라미터만으로** 데이터를 스스로 읽어야 한다.
```js
_onMatched(oEvent) {
  const oArgs = oEvent.getParameter("arguments");
  const sPath = this.getView().getModel().createKey("/FlightSet", {
    Carrid: oArgs.carrid, Connid: oArgs.connid
  });                                   // "/FlightSet(Carrid='LH',Connid='0400')"
  this.getView().bindElement({ path: sPath });
}
```
OData 모델은 목록에서 읽은 엔티티를 캐시하므로 목록을 거치면 추가 요청 없이 바로 표시, 직접 들어오면 그때 GET. 키가 없으면 `dataReceived`에서 데이터가 없을 때 not found target을 표시. `createKey`는 메타데이터 로드 후에만 동작하므로 필요하면 `metadataLoaded()`를 기다린다.

</details>

---

## 9. 확장 · Fiori Elements

### D-027. Fiori Elements floorplan, freestyle·FE·FPM 선택, draft 동작 [개념] ★★
<!-- src: U5-039, UB-099, MX-089, MX-096 -->
(1) Fiori Elements floorplan 설명으로 **틀린** 것을 고르고 바르게 고치시오. Object Page 화면을 구성하는 어노테이션도 쓰시오.
① List Report: 필터 바와 테이블로 많은 데이터를 찾고 행을 눌러 Object Page로 이동한다.
② Worklist: 처리할 작업 목록을 보여 주며 복잡한 필터 바 없이 검색과 탭 정도로 구성되는 경우가 많다.
③ Analytical List Page: 차트(시각 필터)와 테이블을 결합해 분석한다. 집계 가능한 서비스가 필요하다.
④ Overview Page: 여러 데이터 소스의 정보를 카드 형태로 한 화면에 요약한다.
⑤ Object Page: 한 객체의 상세를 섹션별로 보여 주는 조회 전용 화면이며 편집 기능은 없다.
(2) Fiori Elements와 freestyle의 장단점을 쓰시오.
(3) Freestyle, Fiori Elements, Flexible Programming Model(FPM) 중 무엇을 고를지 판단 순서를 쓰고, 각각에 맞는 예를 하나씩 드시오. FPM에서 쓰는 수단과 둘을 섞는 방법도 쓰시오. SAP의 권장 방향은?
(4) RAP draft BO로 만든 FE V4 Object Page 동작으로 **옳지 않은** 것을 고르고 실제 동작을 쓰시오.
① Edit 버튼은 `Edit` action으로 draft를 만들고, 이후 필드 변경은 PATCH로 draft에 저장된다.
② Save 버튼은 `Prepare`와 `Activate` action으로 draft를 활성 인스턴스로 바꾼다.
③ Discard는 draft를 지운다.
④ 사용자가 브라우저를 닫아도 draft는 남아 나중에 이어서 편집할 수 있다.
⑤ 한 사용자가 draft로 편집하는 동안 다른 사용자도 같은 인스턴스의 draft를 따로 만들어 동시에 편집할 수 있다.

<details><summary>정답·해설</summary>

**(1)** ⑤. Object Page는 조회뿐 아니라 생성·편집·삭제를 지원한다(draft 서비스면 Edit/Save/Discard, 하위 테이블 행 생성 등). 구성: `UI.HeaderInfo`(제목), `UI.HeaderFacets`(헤더), `UI.Facets`(섹션), `UI.FieldGroup`/`UI.Identification`(폼), `UI.LineItem`(하위 테이블).

**(2)**
- **Fiori Elements**: 표준 floorplan(List Report/Object Page/Worklist/OVP/ALP)을 OData 메타데이터와 어노테이션으로 생성. 장점: 개발 속도, 가이드라인 자동 준수, draft·메시지·변형 관리·Excel 내보내기·접근성 기본 제공, UI5 업그레이드 시 자동 개선, RAP/CAP과 궁합, 유지보수 쉬움. 단점: floorplan에 맞지 않는 화면(대시보드, 드래그앤드롭, 복잡한 입력 마법사, 그래픽 편집기)은 어렵고 어노테이션 학습 필요.
- **Freestyle**: 화면과 흐름을 자유롭게. 단점은 개발·테스트·유지보수·업그레이드 대응 비용, 가이드라인과 표준 기능을 직접 구현해야 함.

**(3)** 판단 순서: 표준 floorplan으로 되는가? → **Fiori Elements**(예: RAP draft BO 출장 목록 조회·생성·수정 앱). 대부분 되지만 일부만 다른가? → **FPM**(예: Object Page에 맞춤 차트 섹션 하나 추가). 전혀 다른 UX인가? → **Freestyle**(예: 좌석 배치도를 클릭해 좌석을 고르는 앱, 드래그 앤 드롭 계획판, 특수 장비 연동).
FPM 수단: custom section/column/action, controller extension, building block(`sap.fe.macros`), custom page. 섞기: 표준 floorplan 안에 freestyle 부분을 넣거나, freestyle 앱 안에서 building block을 쓴다. 권장 방향: "가능하면 Fiori Elements, 필요한 부분만 확장".

**(4)** ⑤. draft를 만들면 활성 인스턴스는 draft 소유자에게 **배타적으로 잠긴다**. 다른 사용자는 "다른 사용자가 편집 중(locked by)" 표시를 보고 편집할 수 없다. 일정 시간이 지나면 잠금이 만료되어 다른 사용자가 draft를 넘겨받을 수 있다. 활성화 때 total ETag로 그사이 활성 데이터가 바뀌지 않았는지 확인한다.

</details>

---

### D-028. UI 어노테이션: 소스·우선순위, LineItem·SelectionFields·HeaderInfo·facet, side effects [코드] ★★★
<!-- src: U5-040, U5-041, MX-090, MX-091, MX-092, MX-098 -->
RAP Travel 서비스의 메타데이터 확장이다.

```cds
@Metadata.layer: #CUSTOMER
@UI.headerInfo: { typeName: 'Travel', typeNamePlural: 'Travels',
                  title: { type: #STANDARD, value: '____(1)____' } }
annotate view ZMX_C_Travel with
{
  @UI.facet: [ { id: 'General', purpose: #STANDARD, type: #____(2)____, label: '일반', position: 10 } ]
  @UI: { lineItem:       [ { position: 10 },
                           { type: #____(3)____, dataAction: 'acceptTravel', label: '승인' } ],
         identification: [ { position: 10 },
                           { type: #FOR_ACTION, dataAction: 'acceptTravel', label: '승인' } ],
         ____(4)____:    [ { position: 10 } ] }
  TravelID;
  @UI.lineItem: [ { position: 30, importance: #HIGH } ]
  TotalPrice;
  @UI.lineItem: [ { position: 20, label: '설명' } ]
  Description;
  @UI.lineItem: [ { position: 25, ____(5)____: 'StatusCriticality' } ]
  OverallStatus;
  BeginDate;
  @UI.hidden: true
  StatusCriticality;
}
```

(1) 빈칸 (1)~(5)를 채우시오((1)은 Object Page 제목을 TravelID로, (4)는 필터 바 필드). 메타데이터 확장을 쓰기 위한 대상 뷰의 전제 어노테이션과, StatusCriticality를 계산하는 식의 예를 쓰시오.
(2) 이 앱의 List Report에 대해 (a) 처음 보이는 열을 왼쪽부터 (b) "승인"이 나타나는 위치(LineItem과 Identification 각각) (c) BeginDate를 사용자가 볼 수 있는가 (d) StatusCriticality 값 0·1·2·3의 색 의미를 쓰시오.
(3) 같은 내용을 로컬 `annotation.xml`로 쓴 일부다(UI 어휘 별칭 `UI`). 빈칸을 채우시오.
```xml
<Annotations Target="TravelService.TravelType">
  <Annotation Term="UI.____(a)____">
    <Collection>
      <Record Type="UI.____(b)____"><PropertyValue Property="Value" Path="TravelID"/></Record>
      <Record Type="UI.____(b)____"><PropertyValue Property="Value" Path="Description"/></Record>
    </Collection>
  </Annotation>
  <Annotation Term="UI.____(c)____">
    <Collection>
      <____(d)____>AgencyID</____(d)____>
      <____(d)____>OverallStatus</____(d)____>
    </Collection>
  </Annotation>
  <Annotation Term="UI.____(e)____">
    <Record Type="UI.HeaderInfoType">
      <PropertyValue Property="TypeName" String="Travel"/>
      <PropertyValue Property="____(f)____" String="Travels"/>
      <PropertyValue Property="Title">
        <Record Type="UI.DataField"><PropertyValue Property="Value" Path="Description"/></Record>
      </PropertyValue>
    </Record>
  </Annotation>
</Annotations>
```
액션 버튼용 레코드 타입은 무엇인가?
(4) 어노테이션과 화면 영역의 짝으로 **옳지 않은** 것을 고르고, 원하는 동작을 위한 올바른 어노테이션을 쓰시오.
① `@UI.headerInfo.typeNamePlural` – List Report 테이블 제목 ② `@UI.selectionField` – 필터 바 기본 필드 ③ `@UI.lineItem` – 테이블 열 ④ `@UI.facet`(`#IDENTIFICATION_REFERENCE`) + `@UI.identification` – Object Page 섹션 필드 ⑤ `@UI.hidden: true` – 필터 바에서만 숨기고 테이블에는 보임
(5) FE 앱이 쓰는 어노테이션의 소스 2가지를 쓰고, 같은 Target·Term이 여러 곳에 있을 때의 우선순위(덮어쓰기 단위 포함)와 manifest 설정을 쓰시오. 어디에 두는 것이 일반적 권장인가?
(6) draft가 켜진 Travel Object Page에서 BookingFee를 바꾸면 TotalPrice가 즉시 다시 계산돼 보여야 하는데, 지금은 저장하거나 새로 고쳐야 보인다. RAP 쪽 계산, 화면에 안 보이는 이유, BDEF side effects 선언, 메타데이터 어노테이션과 FE 동작, 백엔드에서 선언할 수 없을 때의 대안을 쓰시오.

<details><summary>정답·해설</summary>

**(1)** (1) `TravelID` (2) `IDENTIFICATION_REFERENCE` (3) `FOR_ACTION` (4) `selectionField` (5) `criticality`
- `#IDENTIFICATION_REFERENCE` facet은 `@UI.identification` 필드들을 한 섹션으로 보여 준다. 필드 그룹을 여러 개 두려면 `#FIELDGROUP_REFERENCE` + `targetQualifier`와 `@UI.fieldGroup`.
- 전제: 대상 뷰에 `@Metadata.allowExtensions: true`.
- 계산: projection 뷰에서 `case OverallStatus when 'A' then 3 when 'X' then 1 else 2 end as StatusCriticality`.

**(2)** (a) TravelID → 설명(Description) → OverallStatus → TotalPrice(position 10, 20, 25, 30 순서. 적은 순서가 아니라 `position`으로 정해진다) (b) LineItem의 `#FOR_ACTION`은 열이 아니라 **테이블 툴바 버튼**(행을 선택해야 활성화, 어느 요소에 붙여도 툴바 버튼), identification의 `#FOR_ACTION`은 **Object Page 머리글 오른쪽 위 버튼**. `dataAction`은 BDEF action 이름과 같아야 하고, 동적 기능 제어로 비활성화된 인스턴스를 선택하면 버튼도 비활성화. (c) 처음에는 열로 안 보이지만 테이블 설정(열 추가) 대화상자에서 추가할 수 있다(숨겨진 요소가 아니므로). (d) 0 = 중립, 1 = 빨강(Negative/오류), 2 = 노랑(Critical/경고), 3 = 초록(Positive/성공).

**(3)** (a) `LineItem` (b) `DataField` (c) `SelectionFields` (d) `PropertyPath` (e) `HeaderInfo` (f) `TypeNamePlural`. 액션 버튼은 `DataFieldForAction`. `UI.LineItem` = 테이블 열, `UI.SelectionFields` = 필터 바 필드(속성 경로 목록), `UI.HeaderInfo` = Object Page 제목과 List Report 테이블 제목(TypeNamePlural). CDS의 `@UI.lineItem`, `@UI.selectionField`, `@UI.headerInfo`와 같은 결과.

**(4)** ⑤. `@UI.hidden: true`는 UI 전체(테이블·폼·필터·열 설정 대화상자)에서 숨긴다. 화면 로직에 필요한 기술 필드(criticality 값, UUID)에 쓴다. 필터 바에서만 빼려면 `@Consumption.filter.hidden: true`. `headerInfo`의 `typeName`/`title`은 Object Page 머리글에도 쓰인다.

**(5)** 소스:
1. **백엔드 서비스 메타데이터**: RAP/CDS 어노테이션(`@UI...`, 메타데이터 확장)이 `$metadata`(또는 SEGW annotation model, V2 별도 annotation 문서 `/IWFND/CATALOGSERVICE;v=2/Annotations(...)`)로 노출.
2. **로컬 annotation 파일**: `webapp/annotations/annotation.xml`(Fiori tools annotation 편집기/Service Modeler). CAP이면 `.cds` 어노테이션.
우선순위: 메타데이터가 먼저, 이어서 manifest에 나열된 annotation 데이터 소스 **순서대로** 로드되며 **나중 것이 앞의 것을 덮어쓴다**. 덮어쓰기는 같은 Target + Term + Qualifier 단위의 **통째 교체**이지 속성 병합이 아니다(로컬에서 `UI.LineItem`을 정의하면 백엔드 LineItem 열 전체가 바뀜). 보통 로컬이 백엔드를 덮어쓴다.
```json
"dataSources": {
  "mainService": { "uri": "/sap/opu/odata4/.../0001/", "type": "OData",
                   "settings": { "odataVersion": "4.0", "annotations": ["annotation"] } },
  "annotation":  { "type": "ODataAnnotation", "uri": "annotations/annotation.xml",
                   "settings": { "localUri": "annotations/annotation.xml" } }
}
```
권장: 재사용성과 일관성을 위해 가능한 한 백엔드(CDS)에 두고 앱 고유 UI만 로컬에.

**(6)**
- **RAP 계산**: BDEF `determination calculateTotalPrice on modify { field BookingFee; }`가 있어야 draft PATCH 때 TotalPrice가 다시 계산된다. 구현은 `IN LOCAL MODE`로 Booking 가격과 BookingFee를 읽어 합산 후 UPDATE.
- **안 보이는 이유**: FE는 PATCH 응답으로 **바꾼 필드(BookingFee)가 속한 엔터티**만 갱신한다. 서버에서 다른 필드가 바뀐 줄 몰라 TotalPrice를 다시 읽지 않는다.
- **side effects**: BDEF `side effects { field BookingFee affects field TotalPrice; }`(자식 변경이 부모에 영향이면 `affects field _Travel.TotalPrice`, 엔터티 전체면 `affects entity`).
- **어노테이션·FE 동작**: OData 메타데이터에 `Common.SideEffects`(SourceProperties → TargetProperties)로 노출되고, 사용자가 BookingFee 필드를 떠나면 FE가 PATCH 뒤 TotalPrice를 다시 요청해 갱신한다.
- 대안: 앱 로컬 annotation.xml에 같은 `Common.SideEffects`를 쓴다.

</details>

---

### D-029. Fiori Elements V4 manifest 설정과 확장(controller extension, custom action) [코드] ★★★
<!-- src: UB-100, MX-093, UB-101, MX-094, UB-102, U5-038 -->
RAP OData V4 서비스 기반 FE 앱 `zmx.travel`의 manifest와 확장 코드다.

```json
"sap.ui5": {
  "models": { "": { "dataSource": "mainService", "preload": true,
                    "settings": { "operationMode": "Server", "autoExpandSelect": true, "earlyRequests": true } } },
  "extends": { "extensions": {
    "sap.ui.____(1)____": {
      "sap.fe.templates.ListReport.ListReportController": { "____(2)____": "zmx.travel.ext.controller.ListExt" }
    } } },
  "routing": {
    "routes": [
      { "pattern": ":?query:", "name": "TravelList", "target": "TravelList" },
      { "pattern": "Travel({key}):?query:", "name": "TravelObjectPage", "target": "TravelObjectPage" }
    ],
    "targets": {
      "TravelList": {
        "type": "Component", "id": "TravelList",
        "name": "sap.fe.templates.____(3)____",
        "options": { "settings": {
          "____(4)____": "/Travel",
          "initialLoad": "____(5)____",
          "variantManagement": "____(6)____",
          "controlConfiguration": {
            "@com.sap.vocabularies.UI.v1.LineItem": {
              "tableSettings": { "type": "____(7)____", "selectionMode": "____(8)____" },
              "actions": { "showInfo": {
                "press": ".____(9)____.zmx.travel.ext.controller.ListExt.onShowInfo",
                "text": "정보", "enabled": true } }
            } },
          "navigation": { "Travel": { "detail": { "route": "____(10)____" } } }
        } }
      },
      "TravelObjectPage": { "type": "Component", "id": "TravelObjectPage",
        "name": "sap.fe.templates.____(11)____", "options": { "settings": { "contextPath": "/Travel" } } }
    }
  }
}
```
```js
// webapp/ext/controller/ListExt.controller.js
sap.ui.define(["sap/ui/core/mvc/____(12)____", "sap/m/MessageToast"], function (ControllerExtension, MessageToast) {
  "use strict";
  return ControllerExtension.extend("zmx.travel.ext.controller.ListExt", {
    ____(13)____: {
      onInit: function () { this._oModel = this.base.____(14)____().getModel(); },
      ____(15)____: {            // Object Page 확장이라면: 바인딩이 끝난 뒤 훅
        onAfterBinding: async function (oBindingContext) {
          const oTravel = await oBindingContext.requestObject();
          if (oTravel.OverallStatus === "X") { console.warn("취소된 출장: " + oTravel.TravelID); }
        }
      }
    },
    onShowInfo: function () { MessageToast.show("Custom action pressed"); }
  });
});
```

(1) 빈칸 (1)~(15)를 채우시오((5) 열자마자 조회, (6) 페이지 수준 변형 관리, (7) grid table, (8) 다중 선택). 각 설정의 다른 가능한 값을 쓰시오.
(2) FE V4 타깃의 `type`이 `Component`인 이유, `contextPath`(예전 설정 이름), `navigation`의 역할, 어노테이션과 manifest 설정의 역할 분담을 쓰고, 이런 설정을 화면으로 편집하는 도구를 쓰시오.
(3) Object Page에서 자식 Booking의 Object Page로 이동하는 세 번째 라우트를 추가할 때 pattern, navigation, contextPath를 쓰시오.
(4) `override` 안과 밖에 두는 메서드의 차이, extensionAPI만 써야 하는 이유, Object Page 컨트롤러 확장 등록 키 형식을 쓰시오.
(5) 요구사항과 FE V4 확장 방법의 연결이 **옳지 않은** 것을 고르고 올바른 방법을 쓰시오.
① Object Page에 표준 어노테이션으로 만들 수 없는 지도 영역 → custom section(프래그먼트) ② List Report 테이블에 진행률 막대 열 → custom column ③ 툴바에 "선택 항목 일괄 승인" 버튼 → custom action(manifest `actions` + 핸들러) ④ 저장 직전 확인 대화상자 → controller extension의 `editFlow` 훅 ⑤ 내부 `sap.m.Table`을 `byId`로 찾아 `setMode` 변경 → 권장되는 안정적 방법
(6) SAP 표준 Fiori 앱(또는 FE 앱)을 원본을 고치지 않고 확장하는 방법 6가지를 쓰고 각각 무엇을 바꿀 수 있는지 쓰시오. 공통 원칙과 백엔드 확장과의 구분도 쓰시오.

<details><summary>정답·해설</summary>

**(1)** (1) `controllerExtensions` (2) `controllerName` (3) `ListReport` (4) `contextPath` (5) `Enabled` (6) `Page` (7) `GridTable` (8) `Multi` (9) `extension` (10) `TravelObjectPage` (11) `ObjectPage` (12) `ControllerExtension` (13) `override` (14) `getExtensionAPI` (15) `routing`
다른 값: `initialLoad` = `Enabled`/`Disabled`/`Auto`, `variantManagement` = `Page`/`Control`/`None`, 테이블 `type` = `ResponsiveTable`/`GridTable`/`AnalyticalTable`/`TreeTable`, `selectionMode` = `None`/`Single`/`Multi`/`Auto`.

**(2)** FE V4 화면 템플릿이 컴포넌트(`sap.fe.templates.*`)라서 타깃 `type`이 `Component`. 어느 엔터티를 보여 줄지는 `contextPath`(예전 `entitySet`). `navigation`은 행을 눌렀을 때 갈 라우트. 어노테이션은 "무엇을 보여 줄지", manifest 설정은 "어떻게 보여 줄지". BAS/VS Code의 Fiori tools **Page Map**에서 화면으로 바꾸면 manifest에 기록된다.

**(3)** pattern `"Travel({key})/_Booking({key2}):?query:"`. TravelObjectPage의 `navigation`에 `"_Booking": { "detail": { "route": "BookingObjectPage" } }`를 추가하고 새 타깃의 `contextPath`는 `/Travel/_Booking`.

**(4)** `override` 안: 표준 컨트롤러의 생명주기 메서드(`onInit` 등)와 확장 가능한 훅(`routing.onAfterBinding`, `editFlow.onBeforeSave` 등). 밖: 확장의 일반 메서드(`onShowInfo`), 커스텀 액션 `press`가 `.extension.<확장 컨트롤러 이름>.<메서드>`로 가리킨다. FE 내부 컨트롤·메서드에 직접 접근하지 말고 `this.base.getExtensionAPI()`(모델, 라우팅, 메시지, editFlow 등 공개 API)만 써야 버전 업그레이드에도 깨지지 않는다. Object Page 등록 키: `sap.fe.templates.ObjectPage.ObjectPageController#<앱ID>::TravelObjectPage`. Page Map에서 생성하면 자동 기록된다.

**(5)** ⑤. FE가 만든 내부 컨트롤 ID와 구조는 공개 API가 아니어서 버전이 바뀌면 깨진다. 동작 변경은 manifest 설정(`tableSettings.selectionMode`), extensionAPI, building block으로 한다. 완전히 새로운 화면은 custom page(FPM)에 building block을 조합한다.

**(6)**
1. **Controller extension**: `sap.ui.core.mvc.ControllerExtension`을 상속해 원 컨트롤러의 생명주기 훅·공개 메서드를 `override`하거나 핸들러 추가. FE V4는 manifest 등록 + `override: { onInit, routing: {...}, editFlow: {...} }`.
2. **Extension point**: 원 뷰의 `<core:ExtensionPoint name="..."/>` 위치에 프래그먼트 삽입(manifest `sap.ui5.extends.extensions.sap.ui.viewExtensions`).
3. **View replacement / modification**: 뷰 전체 교체, 컨트롤 숨기기(`visible: false`).
4. **Adaptation project**(Fiori tools/BAS): 원본을 참조하는 app variant를 만들어 위 확장과 UI 변경을 descriptor change로 관리, 원본 업그레이드에도 유지.
5. **Key user adaptation(UI adaptation at runtime)**: 키 유저가 런치패드에서 필드 추가/숨김/이동, 그룹 변경 → SAPUI5 flexibility 레이어에 저장.
6. **Fiori Elements 확장**: 어노테이션 변경, manifest의 custom column/section/action(프래그먼트 + 핸들러), FPM(custom page에서 building block `macros:Table`, `macros:Field`, `macros:FilterBar`로 FE 기능 재사용).
공통 원칙: 원본 수정(modification) 대신 확장(extension) — 업그레이드 안정성과 지원 범위 때문. 백엔드 확장(CDS 확장, RAP BO 확장, BAdI)과 구분한다.

</details>

---

### D-030. Smart controls(sap.ui.comp)와 MDC [코드] ★★
<!-- src: UB-040, UB-041, UB-042, UB-043, MX-095 -->
엔티티셋 `TravelSet`(OData V2)에 대해 필터바와 테이블을 연결하는 XML과 핸들러다.

```xml
<mvc:View xmlns:mvc="sap.ui.core.mvc"
  xmlns:smartFilterBar="sap.ui.comp.smartfilterbar" xmlns:smartTable="sap.ui.comp.smarttable">
  <smartFilterBar:SmartFilterBar id="smartFilterBar" ____(1)____="TravelSet"/>
  <smartTable:SmartTable entitySet="TravelSet"
    ____(2)____="smartFilterBar"
    tableType="____(3)____"
    ____(4)____="true"
    useExportToExcel="true"
    ____(5)____=".onBeforeRebind"/>
</mvc:View>
```
```js
onBeforeRebind(oEvent) {
  const mBindingParams = oEvent.____(6)____("bindingParams");
  mBindingParams.____(7)____.push(new Filter("OverallStatus", FilterOperator.____(8)____, "X"));   // 취소 아닌 것
  mBindingParams.sorter.push(new Sorter("BeginDate", ____(9)____));                              // 최신순
}
```

(1) 빈칸 (1)~(9)를 채우시오((3) 반응형 테이블, (4) 화면을 열자마자 조회, (5) 바인딩 직전 이벤트). `tableType`의 다른 값, 어노테이션 없이 열을 지정하는 속성, 변형 저장을 위한 속성을 쓰시오.
(2) `bindingParams`에 들어 있는 것과 이 핸들러의 용도를 쓰시오. 권한성 조건을 여기에 넣을 때의 주의점은?
(3) SmartTable과 SmartFilterBar가 열·필터 필드를 코드 없이 만드는 원리(사용하는 어노테이션 포함), 둘의 연동 방식, 전제 조건, 기본 제공 부가 기능을 쓰시오.
(4) `sap.ui.comp`와 `sap.ui.mdc`의 차이를 지원 모델, 메타데이터를 읽는 방식, 주 사용처, 라이브러리 배포 범위 측면에서 쓰시오.
(5) Smart controls 설명으로 **옳지 않은** 것을 고르고 이유를 쓰시오.
① SmartFilterBar는 `entitySet`을 주면 메타데이터와 어노테이션으로 필터 필드를 만든다. ② SmartTable은 `smartFilterId`로 SmartFilterBar와 연결된다. ③ SmartTable 기본 열은 `initiallyVisibleFields`나 `UI.LineItem`으로 정해진다. ④ Smart controls는 OData V2 모델 기반이다. ⑤ RAP OData V4 서비스로 새 앱을 만들 때는 building block 대신 Smart controls를 쓰는 것이 권장된다.

<details><summary>정답·해설</summary>

**(1)** (1) `entitySet` (2) `smartFilterId` (3) `ResponsiveTable` (4) `enableAutoBinding` (5) `beforeRebindTable` (6) `getParameter` (7) `filters` (8) `NE` (9) `true`(descending)
`tableType`: `ResponsiveTable`(sap.m.Table), `Table`(grid), `AnalyticalTable`, `TreeTable`. 어노테이션 없이 열 지정: `initiallyVisibleFields="TravelID,AgencyID"`. 변형 저장: `persistencyKey`.

**(2)** `bindingParams`에는 `filters`, `sorter`(배열), `parameters`(예: `parameters.select`, `parameters.expand`)가 있고 여기서 수정한 내용이 실제 바인딩에 반영된다. 사용자에게 보이지 않는 고정 조건이나 기본 정렬을 넣을 때 쓴다. 권한성 조건은 서버에서도 반드시 검사해야 한다(클라이언트 조건은 우회 가능). `Sorter(sPath, bDescending)`.

**(3)**
- `entitySet`의 **OData 메타데이터와 어노테이션**을 읽어 UI를 자동 생성.
  - SmartTable: `UI.LineItem`으로 열과 순서, `sap:label`/`Common.Label`로 헤더, 타입·단위(`Measures.ISOCurrency`)로 셀 형식.
  - SmartFilterBar: `UI.SelectionFields`로 필터 필드, `Common.ValueList`로 값 도움말, `sap:filterable`, `sap:filter-restriction`으로 입력 방식.
- 연동: SmartFilterBar 조건이 `smartFilterId`로 연결된 SmartTable 바인딩에 `$filter`로 반영되고, Go를 누르면 rebind.
- 전제: **OData V2 모델**이 뷰에 설정되고, 백엔드(CDS `@UI` 또는 SEGW/로컬 annotation.xml)에서 어노테이션 제공, `sap.ui.comp`(SAPUI5 전용) 필요.
- 부가 기능: 변형 관리(variant), 열 개인화, Excel 내보내기(`useExportToExcel`).

**(4)**
- **sap.ui.comp**: OData V2 모델과 V2 어노테이션에 직접 묶임. 컨트롤이 메타데이터를 스스로 해석. Fiori Elements V2와 V2 freestyle 앱에서 사용. SAPUI5 전용.
- **sap.ui.mdc**: 모델 독립. 컨트롤은 일반 동작(테이블, 필터바, 필드, 값 도움말)만 구현하고 메타데이터로 열·필드를 정하는 부분은 앱이 제공하는 **delegate**(`TableDelegate`, `FilterBarDelegate`)가 담당. OData V4, JSON 등 어떤 모델에도. Fiori Elements V4(`sap.fe`) 내부가 MDC 기반. OpenUI5에도 포함.
신규 V4 앱은 building block(`macros:Table`, `macros:FilterBar`)을 쓰며 내부적으로 MDC를 쓴다.

**(5)** ⑤. Smart controls는 V2 모델 전용이다. V4 서비스로 freestyle 화면에 어노테이션 기반 컨트롤을 넣으려면 FPM building block(`sap.fe.macros`: FilterBar, Table, Field 등). 기존 V2 앱 유지보수에서는 여전히 Smart controls를 많이 만난다.

</details>

---

### D-031. 읽기 전용 Fiori Elements 앱 끝까지 만들기 (RAP → FE 통합) [작성] ★★★
<!-- src: MX-100 -->
`/dmo/flight`로 "항공편 좌석 현황" 읽기 전용 List Report + Object Page 앱을 만든다. 다음을 작성하시오.

(1) CDS 뷰 엔티티 `ZMX_C_FlightLoad`: 키(항공사·노선·날짜), 항공사 이름(`/DMO/I_Carrier`의 Name, association), 최대·점유 좌석, 점유율 상태(90% 이상 1, 50% 이상 2, 그 밖 3), 가격과 통화. 검색 가능, 항공사 값 도움말과 텍스트 표시.
(2) 메타데이터 확장: 머리글(제목 = 노선), 필터 필드(항공사, 날짜), 테이블 열 4개 이상(상태 색 포함), Object Page 섹션 하나.
(3) 서비스 정의.
(4) 서비스 바인딩부터 BAS에서 앱을 만들어 런치패드에 올릴 때까지의 단계.
(5) 이 앱에 생성·편집 버튼이 나타나지 않는 이유와, 편집 기능을 넣으려면 무엇을 추가해야 하는지 쓰시오. 권한 검사가 필요하면?

<details><summary>정답·해설</summary>

**(1)**
```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: '항공편 좌석 현황'
@Metadata.allowExtensions: true
@Search.searchable: true
define view entity ZMX_C_FlightLoad
  as select from /dmo/flight
  association [1..1] to /DMO/I_Carrier as _Carrier
    on $projection.CarrierId = _Carrier.AirlineID
{
      @Search.defaultSearchElement: true
      @ObjectModel.text.element: ['CarrierName']
      @Consumption.valueHelpDefinition: [{ entity: { name: '/DMO/I_Carrier', element: 'AirlineID' } }]
  key carrier_id     as CarrierId,
  key connection_id  as ConnectionId,
  key flight_date    as FlightDate,
      _Carrier.Name  as CarrierName,
      seats_max      as SeatsMax,
      seats_occupied as SeatsOccupied,
      case
        when seats_occupied * 100 >= seats_max * 90 then 1
        when seats_occupied * 100 >= seats_max * 50 then 2
        else 3
      end            as LoadCriticality,
      @Semantics.amount.currencyCode: 'CurrencyCode'
      price          as Price,
      currency_code  as CurrencyCode,
      _Carrier
}
```

**(2)**
```cds
@Metadata.layer: #CUSTOMER
@UI.headerInfo: { typeName: 'Flight', typeNamePlural: 'Flights',
                  title: { type: #STANDARD, value: 'ConnectionId' } }
annotate view ZMX_C_FlightLoad with
{
  @UI.facet: [ { id: 'Main', purpose: #STANDARD, type: #IDENTIFICATION_REFERENCE,
                 label: '좌석 정보', position: 10 } ]
  @UI: { lineItem: [ { position: 10 } ], selectionField: [ { position: 10 } ], identification: [ { position: 10 } ] }
  CarrierId;
  @UI: { lineItem: [ { position: 20 } ], identification: [ { position: 20 } ] }
  ConnectionId;
  @UI: { lineItem: [ { position: 30 } ], selectionField: [ { position: 20 } ], identification: [ { position: 30 } ] }
  FlightDate;
  @UI: { lineItem: [ { position: 40, criticality: 'LoadCriticality', label: '점유 좌석' } ],
         identification: [ { position: 40, criticality: 'LoadCriticality' } ] }
  SeatsOccupied;
  @UI: { lineItem: [ { position: 50 } ], identification: [ { position: 50 } ] }
  SeatsMax;
  @UI: { lineItem: [ { position: 60 } ], identification: [ { position: 60 } ] }
  Price;
  @UI.hidden: true
  LoadCriticality;
}
```

**(3)**
```cds
@EndUserText.label: '항공편 좌석 현황 서비스'
define service ZMX_UI_FLIGHTLOAD {
  expose ZMX_C_FlightLoad as FlightLoad;
  expose /DMO/I_Carrier   as Carrier;
}
```

**(4)**
1. 서비스 바인딩 `ZMX_UI_FLIGHTLOAD_O4` 생성, 바인딩 유형 **OData V4 - UI**, 활성화.
2. Publish(온프레미스는 `/IWFND/V4_ADMIN`에서 서비스 그룹 공개), 바인딩 화면의 Preview로 List Report 확인.
3. BAS/VS Code에서 Fiori 생성기 → 템플릿 **List Report Page** → 데이터 소스로 시스템과 서비스 선택 → 메인 엔터티 `FlightLoad` → 앱 ID·이름 입력.
4. `npm start`로 확인 후 `npm run deploy`로 배포, 런치패드 catalog·target mapping·롤 할당.

채점(8점): CDS 키·association·노출·통화 어노테이션 2 / 상태 CASE와 `@Search` 1 / `@Metadata.allowExtensions`와 headerInfo·selectionField 1 / lineItem 4열 이상과 criticality 1 / facet + identification 1 / 서비스 정의 1 / 바인딩 유형(OData V4 - UI)·Publish·생성기 단계 1.

**(5)** BDEF가 없으므로 서비스는 읽기 전용이고, FE는 생성·편집·삭제 버튼을 자동으로 숨긴다. `@ObjectModel.text.element`로 항공사 코드 옆에 이름이 보이고 `valueHelpDefinition`으로 필터 값 도움말이 생긴다. 편집 기능을 넣으려면 루트 뷰(`define root view entity`)와 BDEF, projection 계층을 추가해 RAP BO로 확장한다. 권한이 필요하면 `#CHECK`로 바꾸고 DCL 롤을 만든다.

</details>

---

## 10. 성능 · 보안 · 테스트 · 디버깅

### D-032. 성능 체크리스트, Component-preload, lazy loading, cache buster, 개발 권장사항 [개념] ★★
<!-- src: UB-086, UB-087, UB-089, MX-088, UB-015, U5-044 -->
UI5 앱이 처음 열릴 때와 목록을 스크롤할 때 느리다는 불만이 있다.

(1) 성능을 높이는 방법을 로딩 측면 4가지, 데이터(OData) 측면 4가지 쓰시오.
(2) 공식 성능 체크리스트의 권장 사항이 **아닌** 것을 고르고, 체크리스트의 다른 항목을 3가지 이상 쓰시오.
① bootstrap에서 비동기 로딩(`data-sap-ui-async="true"`)을 켠다. ② 의존 라이브러리는 bootstrap `data-sap-ui-libs`보다 manifest `sap.ui5.dependencies`에 정의한다. ③ 앱 리소스가 `Component-preload.js`로 한 번에 로드되는지 확인한다. ④ OData 모델 preload와 메타데이터 캐시를 활용하고 aggregation 바인딩에 `$select`를 쓴다. ⑤ 필요할 때마다 `jQuery.sap.require`로 동기 로드해 초기 로딩을 줄인다.
(3) `Component-preload.js`가 무엇이고 어떻게 만들어지며 왜 중요한지 쓰시오. 배포 후 네트워크 탭에 개별 파일(`Main.view.xml`, `Main.controller.js` …)이 각각 요청된다면 의심할 것 4가지를 쓰시오.
(4) 차트 라이브러리 `sap.viz`를 [분석] 탭을 열 때만 불러오도록 빈칸을 채우고, 주의점과 1.118 이전 API를 쓰시오. 라우팅 target이 lazy loading과 어떤 관계인지도 쓰시오.
```json
"dependencies": { "libs": { "sap.m": {}, "sap.viz": { "____(1)____": true } } }
```
```js
sap.ui.define(["sap/ui/core/mvc/Controller", "sap/ui/core/____(2)____"], (Controller, Lib) => ...
  async onOpenAnalytics() {
    await Lib.____(3)____({ name: "sap.viz" });
    this._oChart ??= await this.loadFragment({ name: "zdemo.view.Chart" });
  }
```
(5) Application Cache Buster가 해결하는 문제와 동작 방식(ABAP 서버 포함)을 쓰고, "왜 캐시를 무기한 써도 안전한가"에 한 줄로 답하시오. 재배포 후 사용자에게 옛 화면이 보일 때 확인할 것 4가지를 쓰시오.
(6) UI5 개발 권장사항(golden rules)에 **어긋나는** 것을 모두 고르고 각각의 올바른 대안을 쓰시오. 그 밖의 권장사항도 쓰시오.
① 디버그 출력에 `console.log` 대신 `sap/base/Log`(`Log.info`, `Log.error`)를 쓴다.
② 컨트롤 모양을 바꾸려고 `document.getElementById(...)`로 렌더링된 DOM을 직접 수정한다.
③ 공개 API에 없는 기능 때문에 `_`로 시작하는 private 메서드를 호출·override한다.
④ `data-sap-ui-async="true"`를 설정하고 모듈은 `sap.ui.define` 의존성으로 로드한다.
⑤ 여러 컨트롤러에서 쓰려고 모델을 `window.oGlobalModel` 전역 변수에 넣는다.

<details><summary>정답·해설</summary>

**(1)**
- 로딩: ① `data-sap-ui-async="true"`, 컴포넌트·뷰를 비동기로(manifest `"async": true`, IAsyncContentCreation), 동기 XHR 금지 ② `ui5 build`로 `Component-preload.js`를 만들어 요청을 하나로 ③ 당장 필요 없는 라이브러리는 `"lazy": true`, 무거운 컨트롤은 필요할 때 Fragment로 ④ CDN·캐시 버스팅으로 정적 파일을 브라우저 캐시에.
- 데이터: ① `$select`(V4 `autoExpandSelect`)로 필요한 열만, `$expand`는 꼭 필요한 연관만 ② `growing`·페이징으로 일부만 읽고 필터·정렬은 서버(operationMode Server) ③ `$batch`로 요청을 묶고 V4 `earlyRequests: true`로 `$metadata`를 먼저 ④ 큰 목록에서는 expression·formatter 계산을 가볍게, 바뀌지 않는 값은 OneTime 바인딩.

**(2)** ⑤. 체크리스트는 오히려 `jquery.sap.*`를 모듈화된 대체 API로, 동기 factory를 비동기 버전으로 바꾸라고 권장한다. 다른 항목: Support Assistant로 점검, CDN에서 UI5 로드, 404 리소스 제거, manifest first, library preload 활성화, IAsyncContentCreation/async routing, 네트워크 요청 점검, 리스트·테이블 점검.

**(3)** 앱의 JS, XML 뷰·프래그먼트, properties, manifest 등을 압축(minify)해 하나의 JS 파일에 모듈 묶음으로 담은 번들. `ui5 build`(`npm run build`)가 `dist/`에 생성(예전 Grunt/Web IDE 빌드). 컴포넌트 로드 시 UI5가 먼저 이 파일을 요청해 수십 개 요청을 1개로 줄이므로 왕복 지연이 큰 WAN/모바일에서 초기 로딩이 크게 준다. 라이브러리도 `library-preload.js`로 같은 방식.
개별 파일 요청 시 의심: 빌드 없이 소스(`webapp`)를 배포 / preload 파일 404 / 디버그 모드(`sap-ui-debug=true`) 실행 중 / 컴포넌트 이름(namespace)과 preload 안 모듈 이름 불일치. 개발 중에는 개별 파일, 운영은 반드시 `dist`.

**(4)** (1) `lazy` (2) `Lib` (3) `load`. `lazy: true`는 "쓰지만 컴포넌트 로딩 때 미리 받지 말라"는 표시라 실제 사용 전에 반드시 직접 로드해야 한다. 안 하면 프래그먼트의 `viz:VizFrame` 등에서 모듈을 동기로 찾거나 오류. 1.118 이전: `sap.ui.getCore().loadLibrary("sap.viz", { async: true })`. 라우팅 target은 처음 표시될 때 뷰를 로드하므로 자연스럽게 lazy loading이 된다.

**(5)** 문제: 정적 리소스를 오래 캐시하면 빠르지만 재배포 후에도 옛 파일을 쓰고, 캐시를 끄면 매번 다운로드해 느리다. 동작: 서버가 파일별 타임스탬프 목록(`sap-ui-cachebuster-info.json`)을 제공하고 UI5는 요청 URL에 `~<timestamp>~` 토큰을 넣는다. 파일이 바뀌면 토큰이 바뀌어 새 URL이 되므로 바뀐 파일만 새로 받는다. ABAP 서버에서는 UI5 리소스 핸들러가 토큰을 붙이고 변경 정보는 SAPUI5 앱 인덱스(`/UI5/APP_INDEX_CALCULATE`)가 관리한다. 한 줄: **파일이 바뀌면 URL 자체가 바뀌기 때문**.
옛 화면: 앱 인덱스 재계산(`/UI5/APP_INDEX_CALCULATE`), 런치패드 캐시 무효화(`/UI2/INVALIDATE_GLOBAL_CACHES`), 브라우저 캐시 삭제·강력 새로고침, 새 `Component-preload.js`가 실제로 배포됐는지 확인.

**(6)** ②, ③, ⑤.
- ① 권장: `Log`는 로그 레벨과 컴포넌트 이름을 지원하고 운영에서 출력이 제어된다.
- ② 위반: 재렌더링되면 변경이 사라지고 컨트롤 상태와 어긋난다 → 속성/`addStyleClass` 또는 커스텀 컨트롤.
- ③ 위반: private API는 예고 없이 바뀌어 업그레이드 시 깨진다.
- ④ 권장: 비동기 로딩, AMD.
- ⑤ 위반: 전역 변수 금지 → 컴포넌트 모델(`this.getOwnerComponent().getModel()`)이나 manifest 모델로 공유.
그 밖에: deprecated API 쓰지 않기, 동기 XHR 금지, manifest 우선 설정, CSP 준수(인라인 스크립트 지양), `ui5 lint`로 검사.

</details>

---

### D-033. UI5 보안: XSS, 렌더러, CSP, 서버 권한, clickjacking [개념] ★★★
<!-- src: UB-090, UB-091, UB-092, UB-093 -->
사용자가 입력한 댓글을 표시하는 커스텀 컨트롤 렌더러다. 댓글에 `<img src=x onerror=alert(1)>`을 넣으면 스크립트가 실행된다.

```js
renderer: {
  apiVersion: 2,
  render(oRm, oControl) {
    oRm.openStart("div", oControl).class("zComment").openEnd();
    oRm.unsafeHtml(oControl.getText());
    oRm.close("div");
  }
}
```

(1) 원인을 쓰고 고치시오. 속성 값과 꼭 HTML을 허용해야 하는 경우는 어떻게 처리하는가?
(2) XSS를 막는 책임이 프레임워크와 애플리케이션 사이에 어떻게 나뉘는지 쓰시오. 애플리케이션이 데이터를 미리 HTML escape하면 안 되는 이유, 특히 주의할 컨트롤과 처리 방법, UI5 sanitizer의 정체도 쓰시오.
(3) CSP(`script-src`에 `'unsafe-inline'`, `'unsafe-eval'` 없음) 환경에 대한 설명으로 **옳지 않은** 것을 고르고 이유를 쓰시오. CSP를 주는 권장 방식과 피해야 할 코드도 쓰시오.
① index.html에 인라인 `<script>`로 초기화 코드를 쓰지 말고 별도 JS 파일(또는 `data-sap-ui-on-init`의 모듈)로 둔다.
② 모듈을 비동기로 로드하면 `eval`이 필요 없어 `'unsafe-eval'` 없이도 동작하기 쉽다.
③ `setTimeout("doSomething()", 100)`처럼 문자열 코드를 넘기는 것은 CSP에서 무시되므로 함수를 넘긴다.
④ 바로 적용하기 전에 `Content-Security-Policy-Report-Only` 헤더로 시험한다.
⑤ 동기 모듈 로딩(`jQuery.sap.require`)은 CSP와 관계없다.
(4) "UI5에서 삭제 버튼을 숨겼으니(`visible=false`) 권한 없는 사용자는 삭제할 수 없다"는 주장의 문제점과 올바른 위치를 쓰시오. 브라우저 local storage에 대한 권고도 쓰시오.
(5) clickjacking이 무엇이며 UI5와 서버에서 어떻게 막는지 쓰시오.

<details><summary>정답·해설</summary>

**(1)** `unsafeHtml`은 문자열을 escape하지 않고 그대로 HTML로 출력하므로 사용자 입력이 태그로 해석되어 `onerror` 스크립트가 실행된다. → `oRm.text(oControl.getText());`(자동 HTML escape). RenderManager semantic API(`openStart`, `attr`, `class`, `style`, `text`)는 값을 escape하므로 속성 값도 문자열 조합 대신 `oRm.attr("title", sValue)`. 꼭 HTML을 허용해야 하면 `sap/base/security/sanitizeHTML`로 정제 후 출력.

**(2)**
- **프레임워크**: 표준 컨트롤은 속성 값을 렌더링할 때 컨텍스트에 맞게 escape(출력 인코딩)하고 타입이 지정된 속성은 입력 검증을 한다. 컨트롤 API는 escape되지 않은 원래 값을 기대하므로 앱이 미리 escape하면 이중 escape되어 `&amp;lt;`처럼 보인다.
- **예외 컨트롤**: 임의 HTML을 넣는 `sap.ui.core.HTML`, `sap.m.FormattedText`(허용 태그만 남기는 sanitizer), `RichTextEditor`. `sap.ui.core.HTML`에 사용자 데이터를 넣으면 `sanitizeContent: true`를 쓰거나 `sap/base/security/encodeXML`로 인코딩.
- **애플리케이션 책임**: HTML 페이지 자체(index.html)의 출력 인코딩, 서버가 보내는 JSON/XML의 안전한 처리, **커스텀 컨트롤 렌더러**의 escape, `innerHTML`/`eval` 같은 직접 DOM 조작 금지.
- UI5 sanitizer는 Google Caja HTML sanitizer를 HTML5에 맞게 조정한 것이며 URL allowlist로 링크도 검사한다.

**(3)** ⑤. 동기 로딩은 내부적으로 `eval`을 써서 `'unsafe-eval'`이 필요하다. CSP는 웹 서버가 `Content-Security-Policy` 헤더로 주는 것이 권장. 피할 것: 인라인 이벤트 핸들러(`onclick="..."`), `javascript:` URL, `new Function()`, 문자열 `setTimeout`.

**(4)** 브라우저는 신뢰할 수 없는 클라이언트다. 개발자 도구로 코드를 바꾸거나 프록시(Fiddler 등)로 요청을 조작해 숨겨진 기능의 OData 요청을 직접 보낼 수 있다. 화면 제어는 사용성일 뿐이고 권한 검사는 반드시 서버(OData 서비스, RAP 권한 제어, `AUTHORITY-CHECK`, `S_SERVICE`)에서, 입력 검증도 서버에서 다시 한다. local storage도 안전한 저장소가 아니므로 사용자·업무 데이터를 넣지 않는다.

**(5)** Clickjacking(UI redressing): 공격자 페이지가 보이지 않는 iframe으로 정상 앱을 겹쳐 놓고, 사용자가 다른 것을 클릭한다고 착각하게 해 앱의 버튼을 누르게 하는 공격. UI5는 1.28부터 **frame options**(`data-sap-ui-frameOptions="trusted"` 또는 `"deny"`, 허용 출처 allowlist)로 신뢰하지 않는 출처에서 iframe에 넣으면 앱을 차단한다. 서버의 `X-Frame-Options`/CSP `frame-ancestors` 헤더도 함께 쓴다.

</details>

---

### D-034. 테스트(QUnit·OPA5·MockServer)와 디버깅 도구 [코드] ★★★
<!-- src: U5-042, U5-043, UB-105, UB-103, UB-104, UB-106 -->
List 뷰의 `btnCreate` 버튼을 누르면 Detail 뷰의 `detailPage`가 나타나는지 검사하는 OPA5 코드다(`Press`는 `sap/ui/test/actions/Press`).

```js
opaTest("Should open the detail page on create", function (Given, When, Then) {
  Given.____(1)____({ componentConfig: { name: "my.travel" } });
  When.onTheListPage.iPressCreate();
  Then.onTheDetailPage.iShouldSeeThePage();
  Then.____(2)____();
});

Opa5.____(3)____({
  onTheListPage: { actions: {
    iPressCreate: function () {
      return this.____(4)____({ id: "btnCreate", viewName: "List",
        ____(5)____: new Press(), errorMessage: "Create button not found" });
    } } },
  onTheDetailPage: { assertions: {
    iShouldSeeThePage: function () {
      return this.____(4)____({ id: "detailPage", viewName: "Detail",
        ____(6)____: function () { Opa5.assert.ok(true, "Detail page is shown"); },
        errorMessage: "Detail page not shown" });
    } } }
});
```

(1) 빈칸 (1)~(6)을 채우고 `waitFor`의 동작과 `viewName`+짧은 `id`의 이점을 쓰시오.
(2) QUnit과 OPA5의 차이, Given/When/Then 구조, page object 패턴을 설명하시오. 그 밖의 테스트·품질 도구도 쓰시오.
(3) 백엔드가 준비되지 않았거나 테스트를 백엔드와 분리하려 할 때 쓰는 mock server를 설명하시오(종류, 필요한 파일, 실행 방법, 용도, mock 데이터 관리).
(4) UI5 지원 도구 설명으로 **옳지 않은** 것을 고르고 바르게 고치시오. Support Assistant는 무엇인가?
① `Ctrl+Shift+Alt+S`: Diagnostics 창, 컨트롤 트리와 바인딩 정보 ② `Ctrl+Shift+Alt+P`: Technical Information(UI5 버전, 로드된 라이브러리, debug sources 설정) ③ `sap-ui-debug=true`: 압축되지 않은 `-dbg` 소스 로드 ④ UI5 Inspector: Chrome/Edge 확장, 컨트롤 트리·속성·바인딩 ⑤ `Ctrl+Shift+Alt+T`: 앱의 OData 서비스를 Gateway에 등록
(5) 송장 목록에서 수량과 제품명은 보이는데 가격(number)만 비어 있고 콘솔 오류는 없다(데이터 속성 이름은 `ExtendedPrice`). 원인과 UI5 도구로 찾는 방법을 쓰시오. "조용히 빈 값"이 되는 오류 유형 3가지도 쓰시오.
```xml
<ObjectListItem core:require="{ Currency: 'sap/ui/model/type/Currency' }"
  title="{invoice>Quantity} x {invoice>ProductName}"
  number="{ parts: [ 'invoice>ExTendedPrice', 'view>/currency' ], type: 'Currency', formatOptions: { showMeasure: false } }"
  numberUnit="{view>/currency}"/>
```
(6) 문제 재현용 URL 파라미터 표를 채우고, 런치패드에서 붙이는 위치와 특정 모듈만 디버그하는 방법을 쓰시오.

| 목적 | 파라미터 |
|---|---|
| 압축되지 않은 디버그 소스 | (a)`=true` |
| 영어로 화면 확인 | (b)`=EN` |
| 다크 테마로 확인 | (c)`=sap_horizon_dark` |
| 콘솔 로그 수준 DEBUG | (d)`=DEBUG` |

<details><summary>정답·해설</summary>

**(1)** (1) `iStartMyUIComponent` (2) `iTeardownMyUIComponent` (3) `createPageObjects` (4) `waitFor` (5) `actions` (6) `success`
`waitFor`는 조건(id, viewName, controlType, matchers)에 맞는 컨트롤이 나타나고 상호작용 가능해질 때까지 폴링한 뒤 `actions`를 실행하거나 `success`를 부른다. 시간 안에 못 찾으면 `errorMessage`로 실패. `viewName`과 짧은 `id`를 주면 뷰 접두어를 OPA가 처리한다.

**(2)**
- **QUnit**: 단위 테스트. formatter, 모델 로직, 컨트롤러 함수를 UI 없이 검증. `QUnit.module`, `QUnit.test(name, function (assert) { assert.strictEqual(...) })`, sinon으로 stub/spy.
- **OPA5**(One Page Acceptance): 통합 테스트. 실제 컴포넌트를 띄워 클릭·입력과 화면 결과를 검증하고 비동기 렌더링/요청을 `waitFor`로 기다린다.
- **Given/When/Then**: Given = arrangements(앱 시작 `iStartMyUIComponent`), When = actions(`Press`, `EnterText`), Then = assertions(결과 확인, 마지막 `iTeardownMyUIComponent`).
- **page object**: `Opa5.createPageObjects({ onTheListPage: { actions, assertions } })`로 화면별 동작·검증을 모아 재사용하고 테스트 문장을 읽기 쉽게(`When.onTheListPage.iPressCreate()`).
- 그 밖에: wdi5/UIVeri5(E2E), Karma 또는 ui5-test-runner로 CI 실행, `ui5 lint`(정적 검사).

**(3)** `sap/ui/core/util/MockServer`(V2) 또는 Fiori tools의 `sap-fe-mockserver` 미들웨어가 OData 요청을 가로채 `localService/metadata.xml`과 `localService/mockdata/<EntitySet>.json`으로 응답을 흉내 낸다(CRUD, `$filter`, `$expand`, `$batch` 처리). 실행: Fiori tools는 `npm run start-mock`(`ui5-mock.yaml`에 mockserver 미들웨어), 수동 MockServer는 `test/initMockServer.js`에서 `rootUri`를 manifest dataSource URI와 같게 설정 후 시작. 용도: 백엔드 없이 UI 개발, OPA5 테스트(데이터가 항상 같아 안정적, 빠름), 오류 상황(500) 재현. mock 데이터는 실제 `$metadata`와 맞아야 하므로 백엔드 `$metadata`를 `metadata.xml`로 저장해 쓰고 백엔드가 바뀌면 다시 받는다.

**(4)** ⑤. `Ctrl+Shift+Alt+T`는 **Test Recorder**(사용자 조작을 기록해 OPA5/wdi5 테스트 코드 조각 생성). 서비스 등록은 `/IWFND/MAINT_SERVICE`. Support Assistant(Technical Information에서 실행)는 규칙 기반으로 성능·모범 사례 위반을 점검한다.

**(5)** 바인딩 경로 오타 `ExTendedPrice` → `ExtendedPrice`. 존재하지 않는 경로는 오류 없이 빈 값. `Ctrl+Shift+Alt+S` Diagnostics → Control Tree에서 `ObjectListItem` 선택 → **Binding Infos** 탭에서 `number` 경로가 invalid로 표시(UI5 Inspector의 Bindings 탭도 같음). 경로 오타, 모델 이름 오타, 상대/절대 경로 혼동은 모두 "조용히 빈 값"이므로 콘솔만 보지 말고 바인딩 정보를 확인한다(Walkthrough Step 29의 일부러 넣은 버그).

**(6)** (a) `sap-ui-debug` (b) `sap-language`(또는 `sap-ui-language`, `sap-locale`) (c) `sap-theme`(또는 `sap-ui-theme`) (d) `sap-ui-logLevel`
예: `index.html?sap-ui-debug=true&sap-language=EN`. 런치패드에서는 `#` 앞(쿼리 부분)에 붙인다. `sap-ui-debug=true`는 전체를 디버그 소스로 바꿔 느리므로 `sap-ui-debug=zdemo/travel/`처럼 특정 모듈만 지정할 수 있다.

</details>

---

## 11. JavaScript 기초 (UI5 맥락)

### D-035. this, 클로저, 스코프와 호이스팅, 프로토타입 상속 [코드] ★★
<!-- src: UB-108, UB-059, UB-120, UB-107, UB-113, UB-114, UB-116, UB-115 -->
모두 `sap.ui.define` 안(`"use strict"`)의 코드다.

```js
// [A] 컨트롤러 onInit
onInit() {
  this.name = "Main";
  const oObj = { name: "Obj", regular: function () { return this.name; }, arrow: () => this.name };
  console.log(oObj.regular());                                         // (a)
  console.log(oObj.arrow());                                           // (b)
  const fn = oObj.regular;
  try { console.log(fn()); } catch (e) { console.log("TypeError"); }   // (c)
  console.log(oObj.regular.call(this));                                // (d)
}

// [B] 조회 성공 후 오류 "Cannot read properties of undefined (reading 'getView')"
onLoad() {
  this.getOwnerComponent().getModel().read("/CarrierSet", {
    success: function (oData) { this.getView().getModel("view").setProperty("/carriers", oData.results); }
  });
}

// [C] 버튼 3개
const aA = [];
for (var i = 0; i < 3; i++) { aA.push(new Button({ text: "B" + i, press: function () { console.log(i); } })); }
aA[0].firePress(); aA[2].firePress();
const aB = [];
for (let j = 0; j < 3; j++) { aB.push(new Button({ text: "B" + j, press: function () { console.log(j); } })); }
aB[0].firePress(); aB[2].firePress();
```

(1) [A]의 (a)~(d)를 쓰고(오류는 `TypeError`), 일반 함수와 화살표 함수의 `this` 결정 규칙을 쓰시오. 컨트롤러 메서드와 그 안 콜백은 각각 어떤 형태로 쓰는 것이 좋은가?
(2) [B]의 원인과 고치는 방법 3가지를 쓰시오. 같은 문제가 생기는 다른 곳과 UI5 `attach*`의 해결법도 쓰시오.
(3) `"use strict"`의 효과로 **옳지 않은** 것을 고르시오. 런치패드에서 특히 중요한 효과는?
① 선언하지 않은 변수에 대입하면 전역 변수가 생기지 않고 ReferenceError가 난다. ② 일반 함수를 그냥 호출하면 `this`가 window가 아니라 `undefined`. ③ 같은 이름의 파라미터를 두 번 쓰는 실수를 문법 오류로 잡는다. ④ 비동기 콜백에서도 `this`가 자동으로 컨트롤러로 고정된다.
(4) [C]의 (A) var, (B) let 각각 버튼 텍스트 세 개와 `firePress()` 두 번의 출력을 쓰고 이유를 쓰시오. UI5에서 더 좋은 해결책은?
(5) 세 조각을 각각 따로 실행했을 때 출력(또는 오류 종류)을 쓰고 이유를 쓰시오.
```js
console.log(a); var a = 1;                                          // (가)
console.log(b); let b = 2;                                          // (나)
console.log(typeof fnLater, typeof fnExpr); function fnLater() {} var fnExpr = function () {};   // (다)
```
(6) var/let/const 설명으로 **옳지 않은** 것을 고르고 이유와 현대 UI5 관례를 쓰시오.
① `let`/`const`는 블록 범위, `var`는 함수 범위 ② `const oModel = new JSONModel(); oModel.setProperty("/a", 1);` 정상 ③ `const aItems = []; aItems.push(1);` 정상 ④ `const aItems = []; aItems = [1];` TypeError ⑤ `const`로 받은 JSONModel 데이터 객체는 속성을 바꿀 수 없어 모델이 보호된다
(7) 다음 컨트롤러의 `iCounter`는 어떤 성질의 변수인가? 같은 뷰가 두 번 생성되면 어떤 문제가 생기고 인스턴스별 상태는 어디에 두어야 하는가? 모듈 범위 변수를 써도 되는 경우는?
```js
sap.ui.define(["sap/ui/core/mvc/Controller"], (Controller) => {
  "use strict";
  let iCounter = 0;
  return Controller.extend("zdemo.controller.Item", {
    onAdd() { iCounter++; this.byId("count").setText(String(iCounter)); }
  });
});
```
(8) 부모 메서드를 호출하는 코드의 빈칸을 채우고, `extend`가 내부적으로 하는 일과 `apply`/`call` 차이를 쓰시오.
```js
return BaseController.extend("zdemo.controller.Detail", {
  onInit() {
    BaseController.____(가)____.onInit.____(나)____(this, arguments);
    this.getRouter().getRoute("detail").attachPatternMatched(this._onMatched, this);
  }
});
return Button.extend("zdemo.control.MyButton", {
  renderer: "sap.m.ButtonRenderer",
  onAfterRendering() {
    if (Button.prototype.onAfterRendering) { Button.prototype.onAfterRendering.____(다)____(this, arguments); }
    this.$().attr("data-test", "x");
  }
});
```

<details><summary>정답·해설</summary>

**(1)** (a) `Obj` (b) `Main` (c) `TypeError` (d) `Main`
일반 함수의 `this`는 **호출 방식**으로 정해진다(`oObj.regular()` → oObj, 떼어 낸 함수를 그냥 호출하면 strict에서 `undefined` → `undefined.name` TypeError, `call`/`apply`/`bind`로 명시하면 그 값). 화살표 함수는 자신의 `this`가 없고 **정의된 곳**(onInit)의 this를 쓴다. 컨트롤러 메서드 자체는 일반 함수(축약 메서드)로, 그 안의 콜백은 화살표 함수로. 컨트롤러 메서드를 화살표 함수로 정의하면 `this`가 컨트롤러가 되지 않는다.

**(2)** 일반 `function` 콜백은 모델 내부에서 호출될 때 `this`가 컨트롤러가 아니다(strict에서 `undefined`).
1. 화살표 함수: `success: (oData) => { this.getView()... }`
2. `bind`: `success: function (oData) { ... }.bind(this)`
3. 변수 저장: `const that = this;` 후 `that.getView()`
같은 문제: `setTimeout`, `Promise.then(function(){})`, `attachEvent(handler)`(listener 생략). UI5 `attach*`는 `attachPress(fnHandler, oListener)`처럼 두 번째 인자로 `this`를 지정한다.

**(3)** ④. strict mode는 실수를 오류로 드러낼 뿐 `this`를 연결해 주지 않는다. 오히려 콜백의 `this`가 `undefined`가 되어 바로 TypeError가 나므로 화살표 함수나 `bind`가 필요하다. 실수로 전역 변수를 만들지 않게 하는 효과는 여러 앱이 한 페이지에서 실행되는 런치패드에서 특히 중요하다.

**(4)** (A) 텍스트 `B0`, `B1`, `B2` / 출력 `3`, `3`. (B) 텍스트 `B0`, `B1`, `B2` / 출력 `0`, `2`.
텍스트는 버튼을 만들 때 바로 계산된다. 핸들러는 나중에 실행되며 변수를 **참조**(클로저)한다. `var`는 함수 범위 변수 하나를 모든 핸들러가 공유해 반복이 끝난 뒤의 3을 보고, `let`은 반복마다 새 바인딩이 생긴다. UI5에서는 핸들러 안에서 반복 변수 대신 `oEvent.getSource()`나 바인딩 컨텍스트로 행 데이터를 얻는 것이 더 좋다.

**(5)** (가) `undefined` (나) `ReferenceError` (다) `function undefined`
`var` 선언은 범위 맨 위로 끌어올려지고(hoisting) `undefined`로 초기화. `let`/`const`도 끌어올려지지만 선언문 실행 전까지 접근 불가 구간(TDZ)이라 ReferenceError. 함수 **선언문**은 본문까지 끌어올려지고, 함수 **표현식**을 담은 `var` 변수는 대입 전까지 `undefined`.

**(6)** ⑤. `const`는 **변수의 재할당**만 막고 가리키는 객체의 내용 변경은 막지 않는다(②③ 가능, ④ 재할당은 TypeError). 객체 자체를 막으려면 `Object.freeze`. 관례: 기본 `const`, 재할당이 필요할 때만 `let`, `var`는 쓰지 않는다.

**(7)** factory 함수 안의 지역 변수로 메서드들이 클로저로 참조한다. 외부에서 접근할 수 없는 **private** 변수지만 factory는 모듈당 **한 번만** 실행되므로 모든 컨트롤러 인스턴스가 **공유**하는 정적(static) 변수와 같다. 뷰가 두 개(두 탭 등)면 한쪽에서 추가해도 함께 증가해 값이 섞인다. 인스턴스별 상태는 `onInit`에서 `this._iCounter = 0`처럼 인스턴스 속성에, 또는 뷰 JSONModel(`this.getView().setModel(new JSONModel({ count: 0 }), "view")`)에 두고 바인딩. 모듈 범위 변수는 상수, 공통 유틸 함수, 정말 공유할 캐시에만. 이 구조가 JavaScript module pattern이고 `sap.ui.define`이 그 역할을 한다.

**(8)** (가) `prototype` (나) `apply` (다) `apply`(또는 `call(this, ...)`)
`extend`: 부모 prototype을 상속하는 새 생성자(하위 클래스)를 만들고, 넘긴 객체의 메서드를 그 prototype에 추가하며 UI5 metadata(속성, aggregation, 이벤트)를 등록한다. 같은 이름 메서드를 정의하면 부모를 가리므로(override) 부모 동작이 필요하면 `Parent.prototype.method.apply(this, arguments)`로 명시 호출. `apply`는 인자 배열(`arguments`), `call`은 인자를 하나씩. 부모에 메서드가 없을 수 있으면 존재 여부를 먼저 확인.

</details>

---

### D-036. 비동기: 이벤트 루프, async/await, Promise로 감싸기와 병렬 조회 [작성] ★★★
<!-- src: UB-110, MX-077, UB-111, UB-112 -->
(1) 두 코드의 콘솔 출력 순서를 각각 쓰고 매크로태스크/마이크로태스크로 설명하시오.
```js
// (A)
async function load() { console.log("A"); await null; console.log("B"); }
console.log("1");
setTimeout(() => console.log("2"), 0);
load();
Promise.resolve().then(() => console.log("3"));
console.log("4");

// (B)
console.log("1");
setTimeout(() => console.log("2"), 0);
Promise.resolve().then(() => console.log("3"));
(async () => { console.log("4"); await null; console.log("5"); })();
console.log("6");
```
(2) (1)이 UI5 코드에 주는 교훈 2가지(`setTimeout(fn, 0)`, `requestObject().then` 다음 줄)를 쓰시오.
(3) 서버에 항공사가 18건 있다. 버튼을 눌렀을 때 출력 순서를 쓰고, 조회 완료 후에 무언가를 하려면 어떻게 해야 하는지, 오류는 어떻게 처리하는지 쓰시오.
```js
_read(sPath) {
  return new Promise((resolve, reject) => {
    this.getOwnerComponent().getModel().read(sPath, { success: resolve, error: reject });
  });
},
async onLoad() { console.log("A"); const oData = await this._read("/CarrierSet"); console.log("C " + oData.results.length); },
onPress() { this.onLoad(); console.log("B"); }
```
(4) OData V2 `read`를 Promise로 감싸는 `_read(sPath, mParams)`를 작성하고, `/CarrierSet`과 `/AirportSet`을 **동시에** 조회해 둘 다 끝나면 `view` 모델의 `/carriers`, `/airports`에 넣고 busy를 끄는 `onInit`을 작성하시오. 하나라도 실패하면 `MessageBox.error`.
(5) (4)의 채점 포인트 5가지와, 하나가 실패해도 나머지 결과를 쓰고 싶을 때의 API, V2 모델이 두 read를 보내는 방식을 쓰시오.

<details><summary>정답·해설</summary>

**(1)** (A) `1, A, 4, B, 3, 2` (B) `1, 4, 6, 3, 5, 2`
- (A) 동기: `1` → setTimeout 콜백은 **매크로태스크** 큐 → `load()`가 `A`를 찍고 `await`에서 나머지(B)를 **마이크로태스크**로 예약 → then(3) 예약 → `4`. 동기 코드가 끝나면 마이크로태스크를 예약 순서대로: `B`, `3`. 그다음 매크로태스크 `2`.
- (B) then(3)이 async 함수보다 먼저 예약되므로 마이크로태스크는 `3`, `5` 순서.
- Promise(`then`, `await`)는 `setTimeout(0)`보다 먼저 실행된다.

**(2)** ① `setTimeout(fn, 0)`으로 "렌더링 후 실행"을 흉내 내는 코드가 기대대로 동작하지 않을 수 있다. ② `oContext.requestObject().then(...)` 바로 다음 줄에서 결과를 쓰면 아직 비어 있다. 값이 필요한 코드는 `then` 안이나 `await` 뒤에 둔다.

**(3)** `A`, `B`, `C 18`. `onLoad`는 `await`에서 멈추고 즉시 Promise를 반환하므로 `onPress`는 기다리지 않고 `B`를 찍는다. 응답 후 `success`가 `resolve`를 부르면 나머지가 실행된다. 완료 후 처리가 필요하면 `onPress`도 async로 하고 `await this.onLoad()`. `error`로 reject되면 `await`가 예외를 던지므로 `try/catch`.

**(4)**
```js
_read(sPath, mParams = {}) {
  const oModel = this.getOwnerComponent().getModel();
  return new Promise((resolve, reject) => {
    oModel.read(sPath, {
      ...mParams,
      success: (oData) => resolve(oData),
      error: (oError) => reject(oError)
    });
  });
},

async onInit() {
  const oView = this.getView();
  oView.setModel(new JSONModel({ carriers: [], airports: [] }), "view");
  oView.setBusy(true);
  try {
    const [oCarr, oAirp] = await Promise.all([
      this._read("/CarrierSet"),
      this._read("/AirportSet")
    ]);
    const oViewModel = oView.getModel("view");
    oViewModel.setProperty("/carriers", oCarr.results);
    oViewModel.setProperty("/airports", oAirp.results);
  } catch (oError) {
    MessageBox.error(oError.message || "조회 실패");
  } finally {
    oView.setBusy(false);
  }
}
```

**(5)** ① `new Promise`에서 success→resolve, error→reject 연결 ② `Promise.all`로 병렬(순차 `await` 두 번이면 시간이 두 배) ③ 구조 분해로 결과 받기 ④ 실패 처리와 `finally`에서 busy 해제 ⑤ 화살표 함수로 this 유지. 부분 성공: `Promise.allSettled`. V2 모델은 같은 시점의 두 read를 하나의 `$batch`로 묶어 보낸다.

</details>

---

### D-037. 값과 연산자: ==/===, ||/??/?., 배열 메서드, 얕은·깊은 복사 [코드] ★★
<!-- src: UB-109, UB-119, UB-117, UB-118 -->
(1) 사용자가 `qtyInput`에 `10`을 입력했다. 각 줄의 출력을 쓰고, 숫자 계산 전에 해야 할 일을 쓰시오.
```js
const sQty = this.byId("qtyInput").getValue();
console.log(typeof sQty);                               // (a)
console.log(sQty == 10, sQty === 10);                   // (b)
console.log(sQty + 5, Number(sQty) + 5);                // (c)
console.log(null == undefined, null === undefined);     // (d)
console.log("" == 0);                                   // (e)
```
(2) 각 줄의 출력을 쓰고(빈 문자열이면 "빈 문자열") `||`, `??`, `?.`, `??=`의 차이를 쓰시오. falsy 값 6가지도 쓰시오.
```js
const oItem = { qty: 0, note: "", discount: null };
console.log(oItem.qty || 1, oItem.qty ?? 1);            // (f)
console.log(oItem.note || "-");                         // (g)
console.log(oItem.note ?? "-");                         // (h)
console.log(oItem.discount ?? 5);                       // (i)
console.log(oItem.supplier?.name);                      // (j)
```
(3) 출력 4개를 쓰고 각 메서드의 의미를 쓰시오. (n)에서 주의할 점과 원본 배열의 변화는?
```js
const aFlights = [ { carrid: "LH", price: 500, seatsfree: 10 },
                   { carrid: "AA", price: 300, seatsfree: 0 },
                   { carrid: "LH", price: 700, seatsfree: 5 } ];
console.log(aFlights.filter((f) => f.carrid === "LH").map((f) => f.price));   // (k)
console.log(aFlights.reduce((sum, f) => sum + f.seatsfree, 0));                // (l)
console.log(aFlights.some((f) => f.seatsfree === 0));                           // (m)
console.log(aFlights.find((f) => f.price > 400).price);                         // (n)
```
(4) 편집 모드에 들어갈 때 원본을 백업하고 [취소]에서 복원하려 했지만, Input에서 값을 바꾸고 [취소]해도 바뀐 값이 남는다(Input은 `view>/travel/Description`에 TwoWay). 원인과 수정 코드를 쓰고, 얕은 복사 방법의 한계, `JSON.parse(JSON.stringify())`의 한계, OData 모델일 때의 대안을 쓰시오.
```js
onEdit() {
  this._oBackup = this.getView().getModel("view").getProperty("/travel");
  this.getView().getModel("view").setProperty("/editMode", true);
},
onCancel() {
  this.getView().getModel("view").setProperty("/travel", this._oBackup);
  this.getView().getModel("view").setProperty("/editMode", false);
}
```

<details><summary>정답·해설</summary>

**(1)** (a) `string` (b) `true false` (c) `105 15` (d) `true false` (e) `true`
`Input.getValue()`는 항상 문자열. `==`는 타입 변환 후 비교(`"10"` → 10), `===`는 타입까지. 문자열 + 숫자는 연결. `""`도 `==`로 0과 같아 "입력 없음"을 0으로 착각하는 버그가 생긴다. 항상 `===`, 계산 전에 `Number()`/`parseInt(s, 10)` 또는 `sap.ui.model.type.Integer` 타입 바인딩으로 변환.

**(2)** (f) `1 0` (g) `-` (h) 빈 문자열 (i) `5` (j) `undefined`
`||`는 왼쪽이 falsy(`0`, `""`, `null`, `undefined`, `NaN`, `false`)면 오른쪽 → 수량 0이 기본값 1로 바뀌는 버그. `??`는 왼쪽이 `null`/`undefined`일 때만 오른쪽. `?.`는 중간 값이 null/undefined면 오류 대신 `undefined`. `??=`는 "아직 없을 때만 대입"(Walkthrough의 `this.oDialog ??= await this.loadFragment(...)`).

**(3)** (k) `[500, 700]` (l) `15` (m) `true` (n) `500`
`filter` = 조건을 만족하는 새 배열, `map` = 변환한 새 배열, `reduce` = 누적값(초기값 0), `some` = 하나라도 만족하면 true, `find` = 처음 만족하는 요소 하나(없으면 `undefined`라 `.price` 전에 확인 필요). 원본 배열은 바뀌지 않는다. 화면 표시용이면 가공 결과를 JSONModel에 넣거나 바인딩 필터·정렬을 쓴다.

**(4)** `getProperty`는 객체의 **참조**를 반환하므로 `_oBackup`과 모델의 `/travel`은 같은 객체다. TwoWay로 입력값이 바뀌면 백업도 함께 바뀐다. 백업 때 **깊은 복사**를 한다.
```js
onEdit() {
  const oTravel = this.getView().getModel("view").getProperty("/travel");
  this._oBackup = structuredClone(oTravel);      // 또는 JSON.parse(JSON.stringify(oTravel))
  this.getView().getModel("view").setProperty("/editMode", true);
}
```
`Object.assign({}, o)`나 `{ ...o }`는 **얕은 복사**라 중첩 객체(`travel.bookings` 배열)는 여전히 공유. `JSON.parse(JSON.stringify())`는 Date를 문자열로 바꾸고 함수·undefined를 잃는다. OData 모델을 직접 바인딩했다면 백업 대신 `resetChanges`(V2/V4).

</details>

---

## 12. 손코딩

### D-038. 항공편 목록 + 검색 + 상세 이동 앱 작성과 오류 수정 [작성] ★★★
<!-- src: HC-042, HC-044 -->
JSON 파일 `model/flights.json`이 다음 구조로 있다.

```json
{ "Flights": [
  { "CarrierName": "Lufthansa", "ConnectionId": "0400", "CityFrom": "FRANKFURT", "CityTo": "NEW YORK",
    "FlightDate": "2026-12-01", "Price": 666.0, "Currency": "EUR" },
  { "CarrierName": "Korean Air", "ConnectionId": "0901", "CityFrom": "SEOUL", "CityTo": "TOKYO",
    "FlightDate": "2026-12-03", "Price": 350.0, "Currency": "USD" }
] }
```

네임스페이스 `zhc.flights` 앱을 작성하시오.
(1) `manifest.json`의 `sap.ui5` 부분: 이름 있는 JSON 모델 `flight`(위 파일), 라우팅(라우트 `list` 패턴 빈 문자열, `detail` 패턴 `detail/{flightPath}`, 대상 뷰 List/Detail, 컨트롤 `app`의 `pages`). App 뷰와 Component.js에서 필요한 것도 쓰시오.
(2) `List.view.xml`: Page, SearchField(검색 이벤트), id `flightList`인 List(비행일 정렬), ObjectListItem(제목: 항공사명 + 노선, 숫자: 가격·통화(Currency 타입), 속성: 출발 → 도착, 비행일, 누르면 이동).
(3) `List.controller.js`: `onSearch`(항공사명 **또는** 도착 도시에 검색어 포함, 빈 검색어면 필터 해제), `onPress`(바인딩 경로를 인코딩해 detail로 이동).
(4) `Detail.view.xml`과 `Detail.controller.js`: 패턴 일치 시 element binding, 뒤로 가기(이전 기록이 없으면 list로 대체 이동).
(5) 다음은 같은 기능을 의도한 다른 개발자의 코드다. 검색도 이동도 동작하지 않는다. 오류를 **12개 이상** 찾아 위치·문제·수정을 표로 쓰시오.
```xml
<mvc:View controllerName="zhc.flights.controller.List" xmlns="sap.m" xmlns:mvc="sap.ui.core.mvc">
  <Page title="항공편">
    <SearchField search=".onSearch"/>
    <List id="flightList" items="{flight>Flights}">
      <ObjectListItem title="{CarrierName}" type="Navigation" press=".onPress"/>
    </List>
  </Page>
</mvc:View>
```
```js
sap.ui.define([
  "sap/ui/core/mvc/Controller",
  "sap/ui/model/Filter"
], function (Controller, FilterOperator, Filter) {
  return Controller.extend("zhc.flights.controller.List", {
    onInit: function () {
      var oModel = new sap.ui.model.json.JSONModel("model/flights.json");
      this.getView().setModel(oModel);
    },
    onSearch: function (oEvent) {
      var sQuery = oEvent.getParameter("value");
      var oFilter = new Filter("CarrierName", FilterOperator.EQ, sQuery);
      this.byId("flightList").getBinding("items").filter(oFilter);
    },
    onPress: function (oEvent) {
      var oCtx = oEvent.getSource().getBindingContext();
      this.getRouter().navTo("Detail", { flightPath: oCtx.getPath() });
    }
  });
});
```

<details><summary>정답·해설</summary>

**(1)**
```json
"sap.ui5": {
  "rootView": { "viewName": "zhc.flights.view.App", "type": "XML", "id": "app" },
  "models": {
    "flight": { "type": "sap.ui.model.json.JSONModel", "uri": "model/flights.json" }
  },
  "routing": {
    "config": {
      "routerClass": "sap.m.routing.Router",
      "type": "View", "viewType": "XML", "path": "zhc.flights.view",
      "controlId": "app", "controlAggregation": "pages", "async": true
    },
    "routes": [
      { "pattern": "", "name": "list", "target": "list" },
      { "pattern": "detail/{flightPath}", "name": "detail", "target": "detail" }
    ],
    "targets": {
      "list":   { "id": "list",   "name": "List" },
      "detail": { "id": "detail", "name": "Detail" }
    }
  }
}
```
`App.view.xml`은 `<App id="app"/>` 하나, `Component.js`의 `init`에서 부모 init 후 `this.getRouter().initialize();`.

**(2)**
```xml
<mvc:View controllerName="zhc.flights.controller.List" xmlns="sap.m" xmlns:mvc="sap.ui.core.mvc">
  <Page title="항공편">
    <subHeader>
      <Toolbar><SearchField width="50%" search=".onSearch"/></Toolbar>
    </subHeader>
    <content>
      <List id="flightList" items="{ path: 'flight>/Flights', sorter: { path: 'FlightDate' } }">
        <ObjectListItem
          title="{flight>CarrierName} {flight>ConnectionId}"
          number="{ parts: ['flight>Price', 'flight>Currency'],
                    type: 'sap.ui.model.type.Currency',
                    formatOptions: { showMeasure: false } }"
          numberUnit="{flight>Currency}"
          type="Navigation" press=".onPress">
          <attributes>
            <ObjectAttribute text="{flight>CityFrom} → {flight>CityTo}"/>
            <ObjectAttribute text="{flight>FlightDate}"/>
          </attributes>
        </ObjectListItem>
      </List>
    </content>
  </Page>
</mvc:View>
```

**(3)**
```js
sap.ui.define([
  "sap/ui/core/mvc/Controller",
  "sap/ui/model/Filter",
  "sap/ui/model/FilterOperator"
], function (Controller, Filter, FilterOperator) {
  "use strict";
  return Controller.extend("zhc.flights.controller.List", {
    onSearch: function (oEvent) {
      var sQuery = oEvent.getParameter("query");
      var aFilters = [];
      if (sQuery) {
        aFilters.push(new Filter({
          filters: [
            new Filter("CarrierName", FilterOperator.Contains, sQuery),
            new Filter("CityTo", FilterOperator.Contains, sQuery)
          ],
          and: false                                   // OR 결합
        }));
      }
      this.byId("flightList").getBinding("items").filter(aFilters);
    },
    onPress: function (oEvent) {
      var oItem = oEvent.getSource();
      var sPath = oItem.getBindingContext("flight").getPath();   // "/Flights/1"
      this.getOwnerComponent().getRouter().navTo("detail", {
        flightPath: window.encodeURIComponent(sPath.substr(1))   // "Flights%2F1"
      });
    }
  });
});
```

**(4)**
```xml
<mvc:View controllerName="zhc.flights.controller.Detail" xmlns="sap.m" xmlns:mvc="sap.ui.core.mvc">
  <Page title="항공편 상세" showNavButton="true" navButtonPress=".onNavBack">
    <ObjectHeader title="{flight>CarrierName} {flight>ConnectionId}"
                  number="{flight>Price}" numberUnit="{flight>Currency}">
      <ObjectAttribute text="{flight>CityFrom} → {flight>CityTo}"/>
      <ObjectAttribute text="{flight>FlightDate}"/>
    </ObjectHeader>
  </Page>
</mvc:View>
```
```js
sap.ui.define([
  "sap/ui/core/mvc/Controller",
  "sap/ui/core/routing/History"
], function (Controller, History) {
  "use strict";
  return Controller.extend("zhc.flights.controller.Detail", {
    onInit: function () {
      this.getOwnerComponent().getRouter().getRoute("detail").attachPatternMatched(this._onMatched, this);
    },
    _onMatched: function (oEvent) {
      var sPath = window.decodeURIComponent(oEvent.getParameter("arguments").flightPath);
      this.getView().bindElement({ path: "/" + sPath, model: "flight" });
    },
    onNavBack: function () {
      var sPrevious = History.getInstance().getPreviousHash();
      if (sPrevious !== undefined) {
        window.history.go(-1);
      } else {
        this.getOwnerComponent().getRouter().navTo("list", {}, true);   // history 대체
      }
    }
  });
});
```
채점 기준(100점): manifest 이름 있는 모델·routing config/routes/targets 20 / List 뷰 집합 바인딩(모델 접두어, 절대 경로, sorter)·이벤트 연결 15 / Currency 복합 바인딩·ObjectListItem 속성 5 / onSearch `query`·OR 필터(`and: false`)·빈 값이면 빈 배열 20 / onPress 모델 이름으로 컨텍스트·경로 인코딩·navTo 15 / Detail attachPatternMatched + decode + bindElement(model 지정) 15 / onNavBack History 확인 후 `go(-1)`/`navTo(..., true)` 10.
해설:
- 모델을 manifest(컴포넌트)에 두어야 List와 Detail 두 뷰가 같은 모델을 본다. List `onInit`에서 `setModel`하면 Detail에서 안 보이는 것이 흔한 오답.
- `/Flights/1`의 `/`는 해시 패턴을 깨므로 인코딩·디코딩한다. 예전 Walkthrough(1.38)는 `substr(1)`만 넘기고 상세에서 `"/" +`로 되살렸고, 최신 버전은 인코딩을 추가했다.
- `search` 이벤트의 검색어 파라미터는 `query`, `liveChange`는 `newValue`.
- `{a} {b}` 형식은 complex binding 문법이 켜져 있어야 한다(`compatVersion="edge"` 또는 `bindingSyntax: complex`).
- `navTo`의 세 번째 인자 `true`는 브라우저 기록을 쌓지 않고 현재 항목을 대체한다.

**(5)**

| # | 위치 | 문제 | 수정 |
|---|---|---|---|
| 1 | `items="{flight>Flights}"` | 루트 배열인데 상대 경로 → 아무것도 안 나옴 | `items="{flight>/Flights}"` |
| 2 | `title="{CarrierName}"` | 모델 이름 없이 기본 모델을 찾음 | `title="{flight>CarrierName}"` |
| 3 | `sap.ui.define` 의존성 | `FilterOperator`를 불러오지 않았고, 인자 순서가 배열과 다름(Filter 자리에 FilterOperator) | 배열에 `"sap/ui/model/FilterOperator"` 추가, `function (Controller, Filter, FilterOperator)` |
| 4 | `new sap.ui.model.json.JSONModel(...)` | 전역 이름 접근(비동기 로딩에서 undefined 가능) | 의존성으로 JSONModel을 받아 사용 |
| 5 | `setModel(oModel)` | 기본 모델로 설정했는데 뷰는 `flight>` 사용. 뷰에만 설정해 상세에서 못 봄 | manifest에 이름 있는 모델 `flight`(또는 `setModel(oModel, "flight")`을 컴포넌트에) |
| 6 | `"model/flights.json"` | index.html 기준 상대 경로라 배포 위치에 따라 깨짐 | manifest `uri` 또는 `sap.ui.require.toUrl("zhc/flights/model/flights.json")` |
| 7 | `getParameter("value")` | `search`의 검색어는 `query` | `getParameter("query")` |
| 8 | `FilterOperator.EQ` | 완전 일치. 빈 검색어면 "빈 값과 같음" 필터로 전체가 사라짐 | `Contains`, 빈 값이면 `filter([])` |
| 9 | `getBindingContext()` | 이름 있는 모델의 컨텍스트를 못 얻어 undefined | `getBindingContext("flight")` |
| 10 | `this.getRouter()` | Controller에 getRouter 없음 | `this.getOwnerComponent().getRouter()` |
| 11 | `navTo("Detail", ...)` | 라우트 이름은 대소문자 구분 | `navTo("detail", ...)` |
| 12 | `flightPath: oCtx.getPath()` | `/Flights/1`의 `/`가 패턴을 깸 | `encodeURIComponent(oCtx.getPath().substr(1))` |
| 13 | `"use strict";` 누락 | 권장 사항(감점 소) | 추가 |

채점: 1~12 항목당 8점(최대 96점), 13 지적 4점. UI5 오류 문제의 단골은 "모델 이름 접두어", "절대/상대 경로", "sap.ui.define 인자 순서", "이벤트 파라미터 이름", "getOwnerComponent().getRouter()"다. 화면에 아무것도 안 나오면 먼저 바인딩 경로와 모델 이름을 의심한다.

</details>

---

### D-039. Dialog 프래그먼트로 항목 추가 [작성] ★★
<!-- src: HC-043 -->
D-038 앱의 List 화면 툴바에 "추가" 버튼을 두고, 누르면 Dialog 프래그먼트 `zhc.flights.view.AddDialog`가 열려 항공사명·노선·출발·도착·비행일·가격·통화를 입력받게 하시오.
- 프래그먼트는 한 번만 만들어 재사용하고, 열 때마다 입력값을 초기화한다(입력용 JSON 모델 `new`).
- 저장: 항공사명과 노선이 비어 있으면 `MessageToast`로 알리고 닫지 않는다. 정상이면 `flight` 모델의 `/Flights`에 추가(가격은 숫자로)하고 닫는다.
- 취소: 닫기만 한다.

(1) 프래그먼트 XML을 작성하시오(SimpleForm, begin/endButton).
(2) 툴바 버튼과 컨트롤러 메서드 `onOpenAdd`, `onSave`, `onCancel`을 작성하시오(필요한 의존성 포함).
(3) `loadFragment`가 해 주는 일과 구 방식 코드, `addDependent`를 안 하면 생기는 일을 쓰시오.
(4) JSON 모델 배열에 `push`만 하면 생길 수 있는 문제와 해결, 프래그먼트 핸들러 `.onSave`를 찾는 위치를 쓰시오.

<details><summary>정답·해설</summary>

**(1)**
```xml
<core:FragmentDefinition xmlns="sap.m" xmlns:core="sap.ui.core" xmlns:f="sap.ui.layout.form">
  <Dialog id="addDialog" title="항공편 추가">
    <content>
      <f:SimpleForm editable="true" layout="ResponsiveGridLayout">
        <Label text="항공사" required="true"/>
        <Input value="{new>/CarrierName}"/>
        <Label text="노선" required="true"/>
        <Input value="{new>/ConnectionId}" maxLength="4"/>
        <Label text="출발 / 도착"/>
        <Input value="{new>/CityFrom}"/>
        <Input value="{new>/CityTo}"/>
        <Label text="비행일"/>
        <DatePicker value="{new>/FlightDate}" valueFormat="yyyy-MM-dd"/>
        <Label text="가격 / 통화"/>
        <Input value="{new>/Price}" type="Number"/>
        <Input value="{new>/Currency}" maxLength="5"/>
      </f:SimpleForm>
    </content>
    <beginButton><Button text="저장" type="Emphasized" press=".onSave"/></beginButton>
    <endButton><Button text="취소" press=".onCancel"/></endButton>
  </Dialog>
</core:FragmentDefinition>
```

**(2)** 툴바: `<Button text="추가" icon="sap-icon://add" press=".onOpenAdd"/>`. 의존성에 `"sap/ui/model/json/JSONModel"`, `"sap/m/MessageToast"` 추가.
```js
onOpenAdd: function () {
  this.getView().setModel(new JSONModel({
    CarrierName: "", ConnectionId: "", CityFrom: "", CityTo: "",
    FlightDate: "", Price: "", Currency: "EUR"
  }), "new");                                         // 열 때마다 초기화
  if (!this._pAddDialog) {                            // 한 번만 생성
    this._pAddDialog = this.loadFragment({ name: "zhc.flights.view.AddDialog" });
  }
  this._pAddDialog.then(function (oDialog) { oDialog.open(); });
},

onSave: function () {
  var oNew = this.getView().getModel("new").getData();
  if (!oNew.CarrierName || !oNew.ConnectionId) {
    MessageToast.show("항공사와 노선은 필수입니다");
    return;                                            // 닫지 않음
  }
  var oModel = this.getView().getModel("flight");
  var aFlights = oModel.getProperty("/Flights");
  aFlights.push(Object.assign({}, oNew, { Price: parseFloat(oNew.Price) || 0 }));
  oModel.setProperty("/Flights", aFlights);            // 바인딩 갱신
  this.byId("addDialog").close();
  MessageToast.show("추가되었습니다");
},

onCancel: function () {
  this.byId("addDialog").close();
}
```
채점 기준(100점): FragmentDefinition + Dialog(id, title, begin/endButton) 20 / 폼 입력 컨트롤과 `new>` 바인딩 15 / 입력 모델 초기화(열 때마다) 10 / loadFragment(또는 Fragment.load + addDependent)로 한 번만 생성·Promise 처리 20 / onSave 필수 검사·배열 추가·setProperty/refresh·닫기 25 / onCancel 5 / MessageToast 의존성 5.

**(3)** `this.loadFragment`(1.93+)는 프래그먼트를 뷰의 dependent로 붙이고 컨트롤 ID 앞에 뷰 ID를 붙이므로 `this.byId("addDialog")`로 찾을 수 있고, 뷰의 모델(`flight`, `new`)도 상속된다. 구 방식: `Fragment.load({ id: this.getView().getId(), name: ..., controller: this })` 후 `this.getView().addDependent(oDialog)`. `addDependent`를 안 하면 Dialog가 뷰의 모델·i18n을 보지 못하고 뷰가 사라질 때 함께 파괴되지 않는다.

**(4)** 배열을 직접 `push`만 하면 바인딩이 변경을 모를 수 있으므로 `setProperty`로 다시 넣거나 `oModel.refresh()`. 프래그먼트 핸들러 `.onSave`는 프래그먼트를 연 컨트롤러에서 찾는다.

</details>

---

## 출처

- https://training.sap.com/certification/C_FIORD_2404 (C_FIORD 시험 주제 영역과 비중)
- https://learning.sap.com/live-sessions/get-certified-sap-certified-associate-sap-fiori-application-developer
- https://learning.sap.com/courses/developing-uis-with-sapui5-1/working-with-models_e8a80842-2cb6-48e3-86b3-321d324f8f2f
- https://learning.sap.com/learning-journeys/develop-sapui5-applications/implementing-router-configuration_a90df07d-7729-4716-a776-c0aa6ac16847
- https://ui5.sap.com/1.38.63/docs/guide/68b9644a253741e8a4b9e4279a35c247.html (Data Binding, 모델별 기본 바인딩 모드)
- https://ui5.sap.com/1.38.65/docs/guide/902313063d6f45aeaa3388cc4c13c34e.html (Routing Configuration)
- https://github.com/wridgeu/wridgeu.github.io/wiki/UI5-Basics-of-Routing (패턴 구문 정리)
- https://developers.sap.com/tutorials/fiori-tools-rap-modify-list-report.html (CDS UI 어노테이션과 List Report)
- https://developers.sap.com/tutorials/fiori-tools-rap-prepare-service.html
- https://ui5.sap.com/#/topic (SAPUI5 Demo Kit: Walkthrough, Data Binding, Routing, Testing, Golden Rules)
- https://sdk.openui5.org/1.38.62/docs/guide/2366345a94f64ec1a80f9d9ce50a59ef.html (OpenUI5 Walkthrough Step 32: Routing with Parameters)
- https://github.com/SAP/openui5-docs/tree/main/docs/03_Get-Started (Walkthrough Step 9, 10, 16, 17, 20, 22, 23, 25, 29, 31, 32, 38)
- https://raw.githubusercontent.com/SAP/openui5-docs/main/docs/03_Get-Started/performance-checklist-9c6400e.md
- https://raw.githubusercontent.com/SAP/openui5-docs/main/docs/03_Get-Started/is-your-application-ready-for-asynchronous-loading-493a15a.md
- https://raw.githubusercontent.com/SAP/openui5-docs/main/docs/08_More_About_Controls/growing-feature-for-table-and-list-9164ba7.md
- https://raw.githubusercontent.com/SAP/openui5-docs/main/docs/08_More_About_Controls/tables-which-one-should-i-choose-148892f.md
- https://raw.githubusercontent.com/SAP/openui5-docs/main/docs/04_Essentials/manifest-model-preload-26ba6a5.md
- https://raw.githubusercontent.com/SAP/openui5-docs/main/docs/04_Essentials/binding-path-2888af4.md
- https://raw.githubusercontent.com/SAP/openui5-docs/main/docs/04_Essentials/batch-control-74142a3.md
- https://raw.githubusercontent.com/SAP/openui5-docs/main/docs/04_Essentials/handling-events-in-xml-views-b0fb4de.md
- https://raw.githubusercontent.com/SAP/openui5-docs/main/docs/04_Essentials/ids-in-declarative-fragments-0715706.md
- https://raw.githubusercontent.com/SAP/openui5-docs/main/docs/03_Get-Started/step-13-make-table-sorting-bookmarkable-3975987.md
- https://raw.githubusercontent.com/SAP/openui5-docs/main/docs/05_Developing_Apps/content-security-policy-fe1a6db.md
- https://raw.githubusercontent.com/SAP/openui5-docs/main/docs/05_Developing_Apps/cross-site-scripting-91f0bd3.md
- https://raw.githubusercontent.com/SAP/openui5-docs/main/docs/05_Developing_Apps/browser-security-91f3b66.md
- https://raw.githubusercontent.com/SAP/openui5-docs/main/docs/02_Read-Me-First/keyboard-shortcuts-for-openui5-tools-154844c.md
- https://github.com/UI5/tutorials
- https://learning.sap.com/courses/learning-the-basics-of-sap-fiori/configuring-sap-fiori-launchpad_be40d546-d8f8-4a6b-b69f-7c77e1a0e9e1
- https://learning.sap.com/courses/developing-an-sap-fiori-elements-app-based-on-a-cap-odata-v4-service/using-controller-extensions_f47e841f-2dd8-4b88-ba5e-39c0eedd983e
- https://learning.sap.com/courses/getting-started-with-creating-an-sap-fiori-elements-app-based-on-an-odata-v4-rap-service/getting-an-overview-of-the-flexible-programming-model
- https://learning.sap.com/certifications/sap-certified-associate-back-end-developer-abap-cloud (C_ABAPD 인증)
- https://blogs.sap.com/2023/07/27/fiori-launchpad-configuration-your-6-steps-guide-to-a-customized-experience/
- https://blogs.sap.com/2014/07/07/primer-on-sapmtable/
- https://groups.community.sap.com/t5/technology-blogs-by-sap/deploying-ui5-applications-on-s-4-hana-on-premise-abap-server-using-vsc/ba-p/13564803
- https://pathlock.com/blog/sap-fiori/fiori-launchpad-t-codes
- https://www.erpqna.com/sap-fiori-application-developer-certification/
- https://climbtheladder.com/sapui5-interview-questions/
- https://dev.to/lalyadav/sap-ui5-interview-questions-and-answers-1p07
- https://static.glassdoor.de/Interview/sap-developer-interview-questions-SRCH_KO0,13_IP693.htm
- https://eursap.eu/blog/an-introduction-to-sap-certification-exams-how-to-make-the-most-of-your-sap-certification-attempt (인증 시험 형식)
