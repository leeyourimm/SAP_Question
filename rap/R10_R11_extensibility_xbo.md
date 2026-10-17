## 3. 특수 BO 패턴

### R-10. 확장 가능한 BO 만들고 직접 확장하기 (Developer Extensibility) [작성] ★★★
<!-- covers: extensible BDEF, extensible { with determinations on modify / on save / with validations on save / with additional save }, extensible entity, mapping corresponding extensible, draft determine action Prepare extensible, draft query view (draft table ... query), extension include structure, @AbapCatalog.enhancement.fieldSuffix, @AbapCatalog.enhancement.quotaMaximumFields, @AbapCatalog.enhancement.quotaMaximumBytes, @AbapCatalog.extensibility (extensible, elementSuffix, dataSources, allowNewDatasources, allowNewCompositions, quota), extension include view (E view), transactional_interface, interface BDEF extensible, projection BDEF extensible, SRVD @AbapCatalog.extensibility.extensible, provider contracts odata_v4_ui, C0 release contract, append structure (extend type), extend view entity, extension using interface, extend behavior for, extend draft determine action Prepare, extension for projection, extension behavior pool, field control in extension, MDE #CUSTOMER layer, composition extension (allowNewCompositions), extension child entity, define behavior ... using interface, with additional save, save_modified, RAISE ENTITY EVENT, extend service, LOB attachment, @Semantics.largeObject, numbering : managed, determination on save -->

**목표**
- 다른 개발자(고객·파트너)가 **원본을 고치지 않고** 필드·로직·자식 노드를 덧붙일 수 있는 "확장 가능한(extensible) RAP BO"를 설계·구현할 수 있습니다.
- 확장 include 구조, 확장 include 뷰(E 뷰), `@AbapCatalog.extensibility` 어노테이션, `extensible` BDEF, draft query 뷰가 각각 어떤 확장 지점을 여는지 설명할 수 있습니다.
- 고객 입장에서 append 구조, `extend view entity`, BDEF 확장(`extension using interface`), 확장 행동 풀, `#CUSTOMER` 레이어 MDE, 서비스 확장으로 실제 확장을 만들 수 있습니다.
- 확장으로 **새 자식 엔터티(리뷰)** 를 composition으로 붙이고, `with additional save`로 저장 시점에 비즈니스 이벤트를 발생시킬 수 있습니다.
- 확장 요소의 이름 규칙(ZZ 접두사 + 필드 접미사), 확장할 수 있는 것과 없는 것, C0 릴리스 계약의 의미를 설명할 수 있습니다.

**전제**
- R-01 ~ R-04를 끝내서 managed + draft BO, 결정/검증, LOB, 메시지 처리를 할 수 있어야 합니다.
- R-02에서 만든 메시지 클래스 `ZRAP_MSG_###`와 예외 클래스 `ZCM_RAP_###`(CX_STATIC_CHECK 상속, IF_ABAP_BEHV_MESSAGE + IF_T100_DYN_MSG, 생성자 파라미터 `textid`, `severity`)를 재사용합니다. 생성자 파라미터 이름이 다르면 정답 코드의 호출부를 맞춰 고치세요.
- 표준 객체: `I_Country`, `I_CountryVH`, 데이터 엘리먼트 `land1`, `/dmo/email_address`, `/dmo/attachment`, `/dmo/mime_type`, `/dmo/filename`, `sysuuid_x16`, 관리 필드용 `abp_*`.
- 기본 BO는 패키지 `ZRAP_###`, 고객 확장은 **별도 패키지 `ZRAP_###_EXT`** 에 만듭니다(같은 소프트웨어 컴포넌트 ZLOCAL 아래 둬도 됩니다).

**만들 객체**

| 순서 | 객체 유형 | 이름 | 역할 |
|---|---|---|---|
| 1 | 구조(Structure) | ZRAP_S_SUPPLIER_EXT_### | 확장 include 구조 (고객 필드가 붙는 자리) |
| 2 | 테이블 | ZRAP_ASUPL_### / ZRAP_DSUPL_### | 공급업체 활성 / draft 테이블 |
| 3 | CDS 뷰 엔터티 | ZRAP_E_SUPPLIER_### | 확장 include 뷰 (DB 확장 필드를 CDS로 올리는 입구) |
| 4 | CDS 루트 뷰 엔터티 | ZRAP_R_SUPPLIER_### | 기본 BO 루트 (확장 가능) |
| 5 | CDS 뷰 엔터티 | ZRAP_R_SUPPLIERDRAFT_### | draft query 뷰 (확장 가능) |
| 6 | BDEF | ZRAP_R_SUPPLIER_### | managed + draft + extensible |
| 7 | 클래스 | ZBP_RAP_R_SUPPLIER_### | 기본 행동 풀 |
| 8 | CDS + BDEF | ZRAP_I_SUPPLIERTP_### | 인터페이스 계층 (확장 BDEF가 이 위에 올라감) |
| 9 | CDS + BDEF + MDE | ZRAP_C_SUPPLIER_### | 프로젝션 (확장 가능) |
| 10 | SRVD / SRVB | ZRAP_UI_SUPPLIER_### / ZRAP_UI_SUPPLIER_O4_### | 확장 가능한 UI 서비스 |
| 11 | 클래스 | ZCL_RAP_GEN_SUPPL_### | 데모 데이터 생성(EML) |
| 12 | 패키지 | ZRAP_###_EXT | 고객 확장 패키지 |
| 13 | append 구조 | ZRAP_X_SUPPL_APPEND_### | 확장 필드 ZZPAYMENTTERMZSU, ZZCERTIFIEDZSU |
| 14 | CDS 뷰 확장 | ZRAP_X_E_SUPPLIER_###, ZRAP_X_R_SUPPLIER_###, ZRAP_X_I_SUPPLIER_###, ZRAP_X_C_SUPPLIER_###, ZRAP_X_RD_SUPPLIER_### | 다섯 뷰에 확장 필드 추가 |
| 15 | MDE | ZRAP_X_C_SUPPLIER_MDE_### | `#CUSTOMER` 레이어 UI 어노테이션 |
| 16 | 메시지 클래스 / 예외 클래스 | ZRAP_X_MSG_### / ZCM_RAP_X_SUPPL_### | 확장 전용 메시지 |
| 17 | BDEF 확장 | ZRAP_X_R_SUPPLIER_### / ZRAP_X_C_SUPPLIER_### | 행동 확장 / 프로젝션 확장 |
| 18 | 클래스 | ZBP_RAP_X_SUPPLIER_### | 확장 행동 풀 |
| 19 | 테이블 | ZRAPX_SREVA_### / ZRAPX_SREVD_### | 리뷰(확장 자식) 활성 / draft |
| 20 | CDS | ZRAPX_R_SUPPLREV_###, ZRAPX_I_SUPPLREV_###, ZRAPX_C_SUPPLREV_###, ZRAPX_D_REVCREATED_### | 리뷰 R/I/C 뷰, 이벤트 파라미터 |
| 21 | SRVD 확장 | ZRAP_X_UI_SUPPLIER_### | 리뷰 엔터티 노출 |

#### 1단계. 확장 include 구조와 공급업체 테이블(활성·draft)

요구사항
1. 패키지 `ZRAP_###` 에 구조 `ZRAP_S_SUPPLIER_EXT_###`(설명 "Supplier extension include")를 만드세요. 필드는 자리 표시용 `dummy_field : abap.char(1)` 하나만 둡니다. 이 구조가 **고객 필드가 붙을 유일한 자리** 입니다.
   - 확장 범주는 "아무 타입이나 확장 가능", 필드 접미사는 `ZSU`, 필드 수 한도 350개, 바이트 한도 3500으로 지정하세요.
2. 활성 테이블 `ZRAP_ASUPL_###` 를 아래 필드 표대로 만들고, 마지막에 1번 구조를 `include` 하세요.
3. draft 테이블 `ZRAP_DSUPL_###` 도 만드세요. 필드 이름은 **CDS 별칭과 같게**(밑줄 없이) 하고, draft 관리 include `sych_bdl_draft_admin_inc` 와 1번 구조를 **둘 다** include 하세요. (활성/draft 양쪽에 같은 확장 include가 있어야 고객 필드가 draft에도 저장됩니다.)

활성 테이블 `ZRAP_ASUPL_###` 필드 표

| 필드 | 키 | 데이터 엘리먼트(또는 내장 타입) | 타입 | 길이 | 소수 | 설명 |
|---|---|---|---|---|---|---|
| client | X | abap.clnt | CLNT | 3 | 0 | 클라이언트 |
| supplier_uuid | X | sysuuid_x16 | RAW | 16 | 0 | 기술 키 (managed numbering) |
| supplier_id |  | abap.numc(8) | NUMC | 8 | 0 | 사람이 읽는 공급업체 번호 (저장 시 결정) |
| name |  | abap.char(80) | CHAR | 80 | 0 | 공급업체 이름 |
| country_code |  | land1 | CHAR | 3 | 0 | 국가 |
| email_address |  | /dmo/email_address | CHAR | 256 | 0 | 이메일 |
| rating |  | abap.int1 | INT1 | 3 | 0 | 평점(1~5, 0=미평가) |
| attachment |  | /dmo/attachment | RAWSTRING | 0 | 0 | 첨부 파일(LOB) |
| mime_type |  | /dmo/mime_type | CHAR | 128 | 0 | 첨부 MIME 유형 |
| filename |  | /dmo/filename | CHAR | 128 | 0 | 첨부 파일 이름 |
| local_created_by |  | abp_creation_user | CHAR | 12 | 0 | 생성자 |
| local_created_at |  | abp_creation_tstmpl | DEC | 21 | 7 | 생성 시각 |
| local_last_changed_by |  | abp_locinst_lastchange_user | CHAR | 12 | 0 | 최종 변경자 |
| local_last_changed_at |  | abp_locinst_lastchange_tstmpl | DEC | 21 | 7 | 인스턴스 최종 변경 시각 (etag) |
| last_changed_at |  | abp_lastchange_tstmpl | DEC | 21 | 7 | 최종 변경 시각 (total etag) |
| .include |  | zrap_s_supplier_ext_### | 구조 |  |  | 확장 include |

(길이는 /DMO 데이터 엘리먼트의 일반적인 정의 기준입니다. 실제 길이는 ADT에서 F2로 확인하세요.)

**직접 추가할 어노테이션** (DDIC)
- `@AbapCatalog.enhancement.category` — 구조/테이블을 append로 넓힐 수 있는지 정함.
- `@AbapCatalog.enhancement.fieldSuffix` — 확장 필드 이름 끝에 반드시 붙여야 하는 접미사(이름 충돌 방지).
- `@AbapCatalog.enhancement.quotaMaximumFields` / `@AbapCatalog.enhancement.quotaMaximumBytes` — 고객이 붙일 수 있는 필드 수·크기 한도.
- `@AbapCatalog.tableCategory`, `@AbapCatalog.deliveryClass`, `@AbapCatalog.dataMaintenance` — 테이블 기본 속성.

**확인**
- 세 객체가 모두 활성화되는지 확인하세요.
- `ZRAP_ASUPL_###` 를 Data Preview로 열면 열 목록 끝에 `DUMMY_FIELD` 가 보여야 합니다(include가 펼쳐진 결과).

<details><summary>정답·해설</summary>

```abap
@EndUserText.label : 'Supplier extension include'
@AbapCatalog.enhancement.category : #EXTENSIBLE_ANY      " 어떤 타입의 필드든 append로 추가 허용
@AbapCatalog.enhancement.fieldSuffix : 'ZSU'             " 확장 필드는 반드시 ...ZSU 로 끝나야 함
@AbapCatalog.enhancement.quotaMaximumFields : 350        " 고객이 추가할 수 있는 최대 필드 수
@AbapCatalog.enhancement.quotaMaximumBytes : 3500        " 고객이 추가할 수 있는 최대 크기
define structure zrap_s_supplier_ext_### {
  dummy_field : abap.char(1);                            " 빈 구조는 만들 수 없으므로 자리 표시 필드
}
```

```abap
@EndUserText.label : 'Supplier (active)'
@AbapCatalog.enhancement.category : #EXTENSIBLE_ANY      " include 구조가 확장 가능하므로 테이블도 같은 범주
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A                          " 애플리케이션 데이터
@AbapCatalog.dataMaintenance : #RESTRICTED
define table zrap_asupl_### {
  key client            : abap.clnt not null;
  key supplier_uuid     : sysuuid_x16 not null;
  supplier_id           : abap.numc(8);
  name                  : abap.char(80);
  country_code          : land1;
  email_address         : /dmo/email_address;
  rating                : abap.int1;
  attachment            : /dmo/attachment;
  mime_type             : /dmo/mime_type;
  filename              : /dmo/filename;
  local_created_by      : abp_creation_user;
  local_created_at      : abp_creation_tstmpl;
  local_last_changed_by : abp_locinst_lastchange_user;
  local_last_changed_at : abp_locinst_lastchange_tstmpl;
  last_changed_at       : abp_lastchange_tstmpl;
  include zrap_s_supplier_ext_###;                       " 확장 include: 고객 필드가 여기로 들어옴
}
```

```abap
@EndUserText.label : 'Supplier (draft)'
@AbapCatalog.enhancement.category : #EXTENSIBLE_ANY
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table zrap_dsupl_### {
  key mandt          : mandt not null;
  key supplieruuid   : sysuuid_x16 not null;
  supplierid         : abap.numc(8);
  name               : abap.char(80);
  countrycode        : land1;
  emailaddress       : /dmo/email_address;
  rating             : abap.int1;
  attachment         : /dmo/attachment;
  mimetype           : /dmo/mime_type;
  filename           : /dmo/filename;
  localcreatedby     : abp_creation_user;
  localcreatedat     : abp_creation_tstmpl;
  locallastchangedby : abp_locinst_lastchange_user;
  locallastchangedat : abp_locinst_lastchange_tstmpl;
  lastchangedat      : abp_lastchange_tstmpl;
  "%admin"           : include sych_bdl_draft_admin_inc;  " draft 관리 필드
  include zrap_s_supplier_ext_###;                       " 활성 테이블과 같은 확장 include
}
```

왜 이렇게 쓰나
- 참조 샘플 `/DMO/AGENCY` 테이블과 draft 테이블 `/DMO/AGENCY_D` 는 둘 다 맨 끝에 `/DMO/S_EXT_INCL_AGENCY` 를 include 합니다. 고객 append는 이 include 구조에만 붙고, 구조를 쓰는 두 테이블에 **동시에** 반영됩니다. 그래서 확장 개발자는 테이블을 직접 건드리지 않습니다.
- 샘플 include 구조의 메타데이터(abapGit XML)는 `EXCLASS 4`(=#EXTENSIBLE_ANY), `FIELD_SUFFIX ZAG`, `QUOTA_MAX_FIELDS 350`, `QUOTA_MAX_BYTES 3500` 입니다. ADT 소스 형식에서는 이것이 `@AbapCatalog.enhancement.*` 어노테이션으로 보입니다. ABAP 릴리스 노트에 따르면 `fieldSuffix`, `quotaMaximumFields`, `quotaMaximumBytes` 는 **DDIC 객체를 C0로 릴리스하기 위한 필수 어노테이션** 이고, 예전의 `quotaShareCustomer`/`quotaSharePartner` 는 없어졌습니다. (→ 어노테이션 탭: @AbapCatalog.enhancement.fieldSuffix)
- draft 테이블은 late numbering이 아니므로 DRAFTUUID 키가 필요 없습니다(키 = UUID). R-01의 Travel처럼 late numbering이면 DRAFTUUID 키가 필요합니다.

자주 나는 오류와 해결
- 테이블 활성화 시 확장 범주 경고가 나오면, include 구조와 테이블의 `@AbapCatalog.enhancement.category` 를 같게(#EXTENSIBLE_ANY) 맞추세요.
- 어노테이션 이름 철자는 ADT에서 Ctrl+Space 코드 완성으로 고르는 것이 가장 안전합니다(실제 시스템에서 확인 필요).

</details>

#### 2단계. 확장 포인트가 열린 CDS 데이터 모델 (E 뷰·R 뷰·draft query 뷰)

요구사항
1. **확장 include 뷰** `ZRAP_E_SUPPLIER_###` 를 만드세요. 활성 테이블을 별칭 `Supplier` 로 select 하고, 키 `SupplierUUID` 하나만 내보냅니다. 고객은 나중에 이 뷰에 DB 확장 필드를 올립니다.
2. **루트 뷰** `ZRAP_R_SUPPLIER_###` 를 만드세요.
   - 활성 테이블을 별칭 `Supplier` 로 select, 필드 별칭: SupplierUUID, SupplierID, Name, CountryCode, EMailAddress, Rating, Attachment, MimeType, Filename, LocalCreatedBy, LocalCreatedAt, LocalLastChangedBy, LocalLastChangedAt, LastChangedAt.
   - 연관: `_Country`(I_Country, [0..1]), `_Extension`(E 뷰, [1], 키로 연결). `_Extension` 은 필드 목록에 노출하지 않습니다.
   - 확장 허용: 데이터 소스는 `_Extension` 만, 새 데이터 소스 추가 금지, **새 composition 허용**, 필드 접미사 `ZSU`, 한도 500필드/50000바이트.
   - LOB: Attachment는 MimeType·Filename을 따르는 LOB, 표시 방식 inline.
3. **draft query 뷰** `ZRAP_R_SUPPLIERDRAFT_###` 를 만드세요. draft 테이블을 별칭 `Supplier` 로 select 하고, 모든 필드 + draft 관리 필드 6개(draftentitycreationdatetime, draftentitylastchangedatetime, draftadministrativedatauuid, draftentityoperationcode, hasactiveentity, draftfieldchanges)를 내보냅니다. 확장 허용(데이터 소스 `Supplier`).

**직접 추가할 어노테이션**
- `@AbapCatalog.viewEnhancementCategory` — E 뷰를 필드 목록 확장(#PROJECTION_LIST)으로 열어 둠.
- `@AbapCatalog.extensibility.extensible` — 이 뷰를 고객이 `extend view entity` 로 확장할 수 있게 허용.
- `@AbapCatalog.extensibility.elementSuffix` — 확장 요소 이름 접미사.
- `@AbapCatalog.extensibility.dataSources` — 확장 요소가 어느 데이터 소스(별칭/연관)에서만 올 수 있는지.
- `@AbapCatalog.extensibility.allowNewDatasources` — 고객이 새 연관/조인을 추가할 수 있는지.
- `@AbapCatalog.extensibility.allowNewCompositions` — 고객이 새 자식(composition)을 붙일 수 있는지.
- `@AbapCatalog.extensibility.quota.maximumFields` / `quota.maximumBytes` — 확장 한도.
- `@Semantics.largeObject` (mimeType, fileName, contentDispositionPreference) — 첨부 파일 업로드/다운로드 UI.
- `@Semantics.mimeType` — MIME 유형 필드 표시.
- `@Semantics.user.createdBy`, `@Semantics.systemDateTime.createdAt`, `@Semantics.user.localInstanceLastChangedBy`, `@Semantics.systemDateTime.localInstanceLastChangedAt`, `@Semantics.systemDateTime.lastChangedAt` — managed 프레임워크가 관리 필드 자동 채움.
- `@AccessControl.authorizationCheck`, `@EndUserText.label`.

**확인**
- 세 뷰가 활성화되고, R 뷰 Data Preview가 (빈) 결과를 보여 주면 됩니다.
- R 뷰에서 F2(Element Info)를 눌러 `_Extension` 연관이 보이는지 확인하세요.

<details><summary>정답·해설</summary>

```cds
@AbapCatalog.viewEnhancementCategory: [#PROJECTION_LIST]   // 필드 목록 확장 허용
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Supplier - Extension Include View'

@AbapCatalog.extensibility: {
  extensible: true,              // extend view entity 허용
  elementSuffix: 'ZSU',          // 확장 요소 이름 접미사
  allowNewDatasources: false,    // 새 조인/연관 금지
  dataSources: ['Supplier'],     // 확장 필드는 별칭 Supplier(=활성 테이블)에서만
  quota: {
    maximumFields: 500,
    maximumBytes: 50000
  }
}

define view entity ZRAP_E_SUPPLIER_###
  as select from zrap_asupl_### as Supplier
{
  key supplier_uuid as SupplierUUID
}
```

```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Supplier - Root (extensible)'

@AbapCatalog.extensibility: {
  extensible: true,
  elementSuffix: 'ZSU',
  allowNewDatasources: false,
  dataSources: ['_Extension'],   // 확장 필드는 _Extension(E 뷰) 경로로만 들어옴
  quota: {
    maximumFields: 500,
    maximumBytes: 50000
  },
  allowNewCompositions: true     // 고객이 자식 노드(composition)를 추가할 수 있음 (10단계)
}

define root view entity ZRAP_R_SUPPLIER_###
  as select from zrap_asupl_### as Supplier
  association [0..1] to I_Country           as _Country   on $projection.CountryCode  = _Country.Country
  association [1]    to ZRAP_E_SUPPLIER_### as _Extension on $projection.SupplierUUID = _Extension.SupplierUUID
{
  key supplier_uuid         as SupplierUUID,
      supplier_id           as SupplierID,
      name                  as Name,
      country_code          as CountryCode,
      email_address         as EMailAddress,
      rating                as Rating,

      @Semantics.largeObject: { mimeType: 'MimeType',               // MIME 유형이 들어 있는 요소
                                fileName: 'Filename',               // 파일 이름 요소
                                contentDispositionPreference: #INLINE } // 브라우저 안에서 열기
      attachment            as Attachment,

      @Semantics.mimeType: true                                     // 이 필드가 MIME 유형임
      mime_type             as MimeType,
      filename              as Filename,

      @Semantics.user.createdBy: true
      local_created_by      as LocalCreatedBy,
      @Semantics.systemDateTime.createdAt: true
      local_created_at      as LocalCreatedAt,
      @Semantics.user.localInstanceLastChangedBy: true
      local_last_changed_by as LocalLastChangedBy,
      @Semantics.systemDateTime.localInstanceLastChangedAt: true    // etag master
      local_last_changed_at as LocalLastChangedAt,
      @Semantics.systemDateTime.lastChangedAt: true                 // total etag
      last_changed_at       as LastChangedAt,

      _Country
}
```

```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Draft Query View: Supplier'

@AbapCatalog.extensibility: {
  extensible: true,
  dataSources: ['Supplier'],     // draft 테이블(별칭 Supplier)의 확장 필드를 올릴 수 있음
  elementSuffix: 'ZSU',
  quota: {
    maximumFields: 500,
    maximumBytes: 50000
  }
}

define view entity ZRAP_R_SUPPLIERDRAFT_###
  as select from zrap_dsupl_### as Supplier
{
  key supplieruuid                  as SupplierUUID,
      supplierid                    as SupplierID,
      name                          as Name,
      countrycode                   as CountryCode,
      emailaddress                  as EMailAddress,
      rating                        as Rating,
      attachment                    as Attachment,
      mimetype                      as MimeType,
      filename                      as Filename,
      localcreatedby                as LocalCreatedBy,
      localcreatedat                as LocalCreatedAt,
      locallastchangedby            as LocalLastChangedBy,
      locallastchangedat            as LocalLastChangedAt,
      lastchangedat                 as LastChangedAt,
      draftentitycreationdatetime   as Draftentitycreationdatetime,
      draftentitylastchangedatetime as Draftentitylastchangedatetime,
      draftadministrativedatauuid   as Draftadministrativedatauuid,
      draftentityoperationcode      as Draftentityoperationcode,
      hasactiveentity               as Hasactiveentity,
      draftfieldchanges             as Draftfieldchanges
}
```

왜 이렇게 쓰나
- **E 뷰(확장 include 뷰)** 는 참조 샘플 `/DMO/E_Agency` 와 같은 구조입니다. 고객 필드는 DB에서 E 뷰로 한 번만 올라오고, R 뷰는 `_Extension.필드` 로 가져다 씁니다. R 뷰의 `dataSources: ['_Extension']` 가 "확장 필드는 이 연관을 통해서만 와야 한다"는 규칙을 강제합니다. (→ 어노테이션 탭: @AbapCatalog.extensibility)
- 프로젝션·인터페이스·draft query 뷰는 자기 데이터 소스 별칭(`Supplier`)을 `dataSources` 에 적습니다. 그래서 별칭 이름을 모든 뷰에서 `Supplier` 로 통일했습니다(고객 확장 코드가 `Supplier.필드` 형태로 일관됨).
- `allowNewCompositions: true` 가 없으면 10단계에서 고객이 리뷰 자식을 붙일 수 없습니다. 샘플 R/I/C 뷰에 모두 들어 있습니다.
- **draft query 뷰**: 릴리스 노트에 "draft query 뷰는 선택 사항이지만, RAP 확장성에서는 BDEF를 C0로 릴리스하기 위한 **필수 전제**"라고 나옵니다. draft 테이블에 붙은 고객 필드를 CDS로 읽게 해 주는 통로이기 때문입니다.
- `@Semantics.largeObject` 를 R 뷰에 두면 프로젝션으로 전파됩니다. (→ 어노테이션 탭: @Semantics.largeObject)

자주 나는 오류와 해결
- `dataSources` 에 적은 이름이 실제 별칭/연관 이름과 다르면 활성화 오류가 납니다. 대소문자까지 맞추세요.
- draft query 뷰의 draft 관리 필드 이름은 draft 테이블이 include한 `sych_bdl_draft_admin_inc` 의 필드명과 같아야 합니다.

</details>

#### 3단계. 확장 가능한 행동 정의(BDEF)와 메시지 준비

요구사항
1. `ZRAP_MSG_###` 에 메시지를 추가하세요.
   - 101 `공급업체 이름을 입력하세요.`
   - 102 `이메일 주소 형식이 올바르지 않습니다(예: name@company.com).`
   - 103 `국가 코드가 비어 있거나 존재하지 않습니다.`
   - 104 `평점은 1에서 5 사이여야 합니다.`
   - 105 `첨부 파일의 MIME 유형이 비어 있거나 허용되지 않습니다(txt, jpg, png, pdf).`
2. `ZCM_RAP_###` 에 위 메시지용 상수 `supplier_name_required`, `supplier_email_invalid`, `supplier_country_invalid`, `supplier_rating_invalid`, `supplier_attachment_invalid` 를 추가하세요.
3. BDEF `ZRAP_R_SUPPLIER_###` 를 만드세요 (managed, 행동 풀 `ZBP_RAP_R_SUPPLIER_###`, strict 2, draft).
   - BO 전체에 확장 허용: 고객이 on modify 결정, on save 결정, on save 검증, `with additional save` 를 추가할 수 있게 하세요.
   - 엔터티 별칭 `Supplier`, 엔터티 자체도 확장 허용, draft 테이블에 **draft query 뷰 지정**, lock master, total etag `LastChangedAt`, etag master `LocalLastChangedAt`, 권한 없음.
   - SupplierUUID: managed numbering + 읽기 전용. SupplierID와 관리 필드: 읽기 전용. Name, EMailAddress, CountryCode: 필수.
   - 결정 `setSupplierID on save { create; }`, 검증 `validateName`, `validateEMailAddress`, `validateCountryCode`, `validateRating`, `validateAttachment`(Attachment·MimeType·Filename 변경 시).
   - draft 액션 Resume/Edit/Activate optimized/Discard, `draft determine action Prepare` 는 **확장 가능** 하게 하고 5개 검증을 넣으세요.
   - 매핑은 `corresponding extensible`.

**확인**
- BDEF 활성화 후, 행동 풀이 없다는 경고가 나오면 4단계에서 만듭니다. 퀵픽스(Ctrl+1)로 클래스를 생성해도 됩니다.

<details><summary>정답·해설</summary>

`ZCM_RAP_###` 에 추가할 상수 (R-02에서 만든 클래스의 PUBLIC SECTION 안, 기존 상수 아래):

```abap
    CONSTANTS:
      BEGIN OF supplier_name_required,
        msgid TYPE symsgid VALUE 'ZRAP_MSG_###',
        msgno TYPE symsgno VALUE '101',
        attr1 TYPE scx_attrname VALUE '',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF supplier_name_required,
      BEGIN OF supplier_email_invalid,
        msgid TYPE symsgid VALUE 'ZRAP_MSG_###',
        msgno TYPE symsgno VALUE '102',
        attr1 TYPE scx_attrname VALUE '',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF supplier_email_invalid,
      BEGIN OF supplier_country_invalid,
        msgid TYPE symsgid VALUE 'ZRAP_MSG_###',
        msgno TYPE symsgno VALUE '103',
        attr1 TYPE scx_attrname VALUE '',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF supplier_country_invalid,
      BEGIN OF supplier_rating_invalid,
        msgid TYPE symsgid VALUE 'ZRAP_MSG_###',
        msgno TYPE symsgno VALUE '104',
        attr1 TYPE scx_attrname VALUE '',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF supplier_rating_invalid,
      BEGIN OF supplier_attachment_invalid,
        msgid TYPE symsgid VALUE 'ZRAP_MSG_###',
        msgno TYPE symsgno VALUE '105',
        attr1 TYPE scx_attrname VALUE '',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF supplier_attachment_invalid.
```

```bdef
managed implementation in class zbp_rap_r_supplier_### unique;
strict ( 2 );
with draft;
extensible                                  // BO 전체: 고객이 추가할 수 있는 것의 종류를 명시
{
  with determinations on modify;            // 고객 on modify 결정 허용
  with determinations on save;              // 고객 on save 결정 허용
  with validations on save;                 // 고객 검증 허용
  with additional save;                     // 고객이 저장 단계에 자기 로직(save_modified) 추가 허용
}

define behavior for ZRAP_R_SUPPLIER_### alias Supplier
persistent table zrap_asupl_###
draft table zrap_dsupl_### query ZRAP_R_SUPPLIERDRAFT_###   // draft query 뷰 (확장 C0 전제)
lock master
total etag LastChangedAt
authorization master ( none )
etag master LocalLastChangedAt
extensible                                  // 이 엔터티의 행동을 고객이 extend behavior for 로 확장 가능
{
  create;
  update;
  delete;

  field ( readonly, numbering : managed ) SupplierUUID;
  field ( readonly ) SupplierID, LocalCreatedBy, LocalCreatedAt, LocalLastChangedBy, LocalLastChangedAt, LastChangedAt;
  field ( mandatory ) Name, EMailAddress, CountryCode;

  draft action Resume;
  draft action Edit;
  draft action Activate optimized;
  draft action Discard;

  determination setSupplierID on save { create; }

  validation validateName on save { create; field Name; }
  validation validateEMailAddress on save { create; field EMailAddress; }
  validation validateCountryCode on save { create; field CountryCode; }
  validation validateRating on save { create; field Rating; }
  validation validateAttachment on save { create; field Attachment; field MimeType; field Filename; }

  draft determine action Prepare extensible   // 고객이 extend draft determine action Prepare 로 자기 검증 추가 가능
  {
    validation validateName;
    validation validateEMailAddress;
    validation validateCountryCode;
    validation validateRating;
    validation validateAttachment;
  }

  mapping for zrap_asupl_### corresponding extensible   // 같은 이름 필드 + 고객 확장 필드 자동 매핑
  {
    SupplierUUID       = supplier_uuid;
    SupplierID         = supplier_id;
    Name               = name;
    CountryCode        = country_code;
    EMailAddress       = email_address;
    Rating             = rating;
    Attachment         = attachment;
    MimeType           = mime_type;
    Filename           = filename;
    LocalCreatedBy     = local_created_by;
    LocalCreatedAt     = local_created_at;
    LocalLastChangedBy = local_last_changed_by;
    LocalLastChangedAt = local_last_changed_at;
    LastChangedAt      = last_changed_at;
  }
}
```

왜 이렇게 쓰나
- 헤더의 `extensible { ... }` 블록은 참조 샘플 `/DMO/R_AgencyTP` 와 같은 4줄입니다. 여기 적은 종류만 고객이 추가할 수 있습니다. 예를 들어 `with additional save` 를 빼면 고객은 저장 단계 로직(10단계의 이벤트 발생)을 넣을 수 없습니다.
- 엔터티 줄의 `extensible` 이 없으면 `extend behavior for Supplier` 자체가 불가능합니다.
- `draft determine action Prepare extensible` — 고객 검증이 Prepare(= Fiori의 저장 직전 검사)에도 돌게 하려면 Prepare가 확장 가능해야 합니다.
- `mapping ... corresponding extensible` — `corresponding` 은 이름이 같은 필드를 자동 매핑하고, `extensible` 은 고객이 추가한 필드도 매핑에 포함되게 합니다. 고객 필드 `ZZPaymentTermZSU`(CDS) ↔ `zzpaymenttermzsu`(DB)는 이름이 같아(대소문자 무시) 자동으로 연결됩니다.
- `draft table ... query ...` 는 2단계 draft query 뷰를 BDEF에 연결합니다.

클래스 구조 해설
- `determination setSupplierID on save` → 행동 풀에 `FOR DETERMINE ON SAVE IMPORTING keys FOR Supplier~setSupplierID` 메서드가 생깁니다. 파생 타입 `keys` 는 `TABLE FOR DETERMINATION zrap_r_supplier_###\\supplier~setsupplierid` 입니다.
- `validation ... on save` → `FOR VALIDATE ON SAVE` 메서드. Activate/Prepare 때와 직접 저장(EML COMMIT) 때 호출됩니다.

</details>

#### 4단계. 기본 행동 풀 구현 (ID 결정, 검증, LOB 검사)

요구사항
1. `ZBP_RAP_R_SUPPLIER_###` 의 로컬 핸들러 `lhc_supplier` 를 구현하세요.
2. 상수: state area 이름 5개(`VALIDATE_NAME` 등), 허용 MIME 유형 표(`text/plain`→.txt, `image/jpeg`→.jpg, `image/png`→.png, `application/pdf`→.pdf).
3. `setSupplierID`: SupplierID가 비어 있는 인스턴스만 골라, 활성 테이블의 최댓값 + 1부터 차례로 번호를 줍니다.
4. 검증 5개: 모든 검증은 먼저 `%state_area` 로 이전 메시지를 지우고, 오류면 `failed` + `reported`(`%element-필드 = mk-on`)를 채웁니다.
   - Name 비어 있음 → 101
   - EMailAddress 가 `+*@+*.+*` 패턴이 아님 → 102
   - CountryCode 비어 있음 또는 I_Country에 없음 → 103 (I_Country는 FOR ALL ENTRIES로 한 번만 읽음)
   - Rating 이 0이 아니면서 1~5 밖 → 104
   - Attachment 가 있는데 MimeType 이 없거나 허용 목록에 없음, 또는 MimeType 만 있고 Attachment 가 없음 → 105

**확인**
- 클래스 활성화. 6단계에서 데이터 생성 클래스로 실제 동작을 확인합니다.

<details><summary>정답·해설</summary>

글로벌 클래스:

```abap
CLASS zbp_rap_r_supplier_### DEFINITION PUBLIC ABSTRACT FINAL FOR BEHAVIOR OF zrap_r_supplier_###.
ENDCLASS.

CLASS zbp_rap_r_supplier_### IMPLEMENTATION.
ENDCLASS.
```

로컬 타입(Local Types):

```abap
CLASS lhc_supplier DEFINITION INHERITING FROM cl_abap_behavior_handler.
  PRIVATE SECTION.
    CONSTANTS:
      BEGIN OF state_area,
        name       TYPE string VALUE 'VALIDATE_NAME',
        email      TYPE string VALUE 'VALIDATE_EMAIL',
        country    TYPE string VALUE 'VALIDATE_COUNTRY',
        rating     TYPE string VALUE 'VALIDATE_RATING',
        attachment TYPE string VALUE 'VALIDATE_ATTACHMENT',
      END OF state_area.

    TYPES: BEGIN OF ty_mimetype,
             mimetype       TYPE string,
             file_extension TYPE string,
           END OF ty_mimetype,
           tt_mimetype TYPE SORTED TABLE OF ty_mimetype WITH UNIQUE KEY mimetype.

    METHODS get_allowed_mimetypes
      RETURNING VALUE(result) TYPE tt_mimetype.

    METHODS setsupplierid FOR DETERMINE ON SAVE
      IMPORTING keys FOR supplier~setsupplierid.

    METHODS validatename FOR VALIDATE ON SAVE
      IMPORTING keys FOR supplier~validatename.

    METHODS validateemailaddress FOR VALIDATE ON SAVE
      IMPORTING keys FOR supplier~validateemailaddress.

    METHODS validatecountrycode FOR VALIDATE ON SAVE
      IMPORTING keys FOR supplier~validatecountrycode.

    METHODS validaterating FOR VALIDATE ON SAVE
      IMPORTING keys FOR supplier~validaterating.

    METHODS validateattachment FOR VALIDATE ON SAVE
      IMPORTING keys FOR supplier~validateattachment.
ENDCLASS.

CLASS lhc_supplier IMPLEMENTATION.

  METHOD get_allowed_mimetypes.
    result = VALUE #( ( mimetype = `application/pdf` file_extension = `.pdf` )
                      ( mimetype = `image/jpeg`      file_extension = `.jpg` )
                      ( mimetype = `image/png`       file_extension = `.png` )
                      ( mimetype = `text/plain`      file_extension = `.txt` ) ).
  ENDMETHOD.

  METHOD setsupplierid.
    DATA max_id TYPE zrap_asupl_###-supplier_id.

    READ ENTITIES OF zrap_r_supplier_### IN LOCAL MODE
      ENTITY Supplier
        FIELDS ( SupplierID )
        WITH CORRESPONDING #( keys )
      RESULT DATA(suppliers).

    DELETE suppliers WHERE SupplierID IS NOT INITIAL.
    IF suppliers IS INITIAL.
      RETURN.
    ENDIF.

    " on save 결정이므로 활성 테이블만 보면 됨 (draft에는 아직 번호가 없음)
    SELECT SINGLE FROM zrap_asupl_### FIELDS MAX( supplier_id ) INTO @max_id.

    MODIFY ENTITIES OF zrap_r_supplier_### IN LOCAL MODE
      ENTITY Supplier
        UPDATE FIELDS ( SupplierID )
        WITH VALUE #( FOR supplier IN suppliers INDEX INTO i
                      ( %tky       = supplier-%tky
                        SupplierID = max_id + i ) )
      REPORTED DATA(update_reported).

    reported = CORRESPONDING #( DEEP update_reported ).
  ENDMETHOD.

  METHOD validatename.
    READ ENTITIES OF zrap_r_supplier_### IN LOCAL MODE
      ENTITY Supplier
        FIELDS ( Name )
        WITH CORRESPONDING #( keys )
      RESULT DATA(suppliers).

    LOOP AT suppliers INTO DATA(supplier).
      APPEND VALUE #( %tky        = supplier-%tky
                      %state_area = state_area-name ) TO reported-supplier.

      IF supplier-Name IS INITIAL.
        APPEND VALUE #( %tky = supplier-%tky ) TO failed-supplier.
        APPEND VALUE #( %tky          = supplier-%tky
                        %state_area   = state_area-name
                        %msg          = NEW zcm_rap_###( textid   = zcm_rap_###=>supplier_name_required
                                                         severity = if_abap_behv_message=>severity-error )
                        %element-Name = if_abap_behv=>mk-on ) TO reported-supplier.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

  METHOD validateemailaddress.
    READ ENTITIES OF zrap_r_supplier_### IN LOCAL MODE
      ENTITY Supplier
        FIELDS ( EMailAddress )
        WITH CORRESPONDING #( keys )
      RESULT DATA(suppliers).

    LOOP AT suppliers INTO DATA(supplier).
      APPEND VALUE #( %tky        = supplier-%tky
                      %state_area = state_area-email ) TO reported-supplier.

      " string으로 바꿔 뒤쪽 공백을 없앤 뒤 패턴 비교 (+ 는 한 글자, * 는 0글자 이상)
      IF CONV string( supplier-EMailAddress ) NP '+*@+*.+*' ##OPERATOR[STRING].
        APPEND VALUE #( %tky = supplier-%tky ) TO failed-supplier.
        APPEND VALUE #( %tky                  = supplier-%tky
                        %state_area           = state_area-email
                        %msg                  = NEW zcm_rap_###( textid   = zcm_rap_###=>supplier_email_invalid
                                                                 severity = if_abap_behv_message=>severity-error )
                        %element-EMailAddress = if_abap_behv=>mk-on ) TO reported-supplier.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

  METHOD validatecountrycode.
    DATA countries TYPE SORTED TABLE OF i_country WITH UNIQUE KEY country.

    READ ENTITIES OF zrap_r_supplier_### IN LOCAL MODE
      ENTITY Supplier
        FIELDS ( CountryCode )
        WITH CORRESPONDING #( keys )
      RESULT DATA(suppliers).

    " 중복 없는 국가 코드 목록 → DB는 한 번만 조회
    countries = CORRESPONDING #( suppliers DISCARDING DUPLICATES MAPPING country = CountryCode EXCEPT * ).
    DELETE countries WHERE country IS INITIAL.

    IF countries IS NOT INITIAL.
      SELECT FROM i_country FIELDS country
        FOR ALL ENTRIES IN @countries
        WHERE country = @countries-country
        INTO TABLE @DATA(countries_db).
    ENDIF.

    LOOP AT suppliers INTO DATA(supplier).
      APPEND VALUE #( %tky        = supplier-%tky
                      %state_area = state_area-country ) TO reported-supplier.

      IF    supplier-CountryCode IS INITIAL
         OR NOT line_exists( countries_db[ country = supplier-CountryCode ] ).
        APPEND VALUE #( %tky = supplier-%tky ) TO failed-supplier.
        APPEND VALUE #( %tky                 = supplier-%tky
                        %state_area          = state_area-country
                        %msg                 = NEW zcm_rap_###( textid   = zcm_rap_###=>supplier_country_invalid
                                                                severity = if_abap_behv_message=>severity-error )
                        %element-CountryCode = if_abap_behv=>mk-on ) TO reported-supplier.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

  METHOD validaterating.
    READ ENTITIES OF zrap_r_supplier_### IN LOCAL MODE
      ENTITY Supplier
        FIELDS ( Rating )
        WITH CORRESPONDING #( keys )
      RESULT DATA(suppliers).

    LOOP AT suppliers INTO DATA(supplier).
      APPEND VALUE #( %tky        = supplier-%tky
                      %state_area = state_area-rating ) TO reported-supplier.

      IF supplier-Rating IS NOT INITIAL AND ( supplier-Rating < 1 OR supplier-Rating > 5 ).
        APPEND VALUE #( %tky = supplier-%tky ) TO failed-supplier.
        APPEND VALUE #( %tky            = supplier-%tky
                        %state_area     = state_area-rating
                        %msg            = NEW zcm_rap_###( textid   = zcm_rap_###=>supplier_rating_invalid
                                                           severity = if_abap_behv_message=>severity-error )
                        %element-Rating = if_abap_behv=>mk-on ) TO reported-supplier.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

  METHOD validateattachment.
    DATA(allowed) = get_allowed_mimetypes( ).

    READ ENTITIES OF zrap_r_supplier_### IN LOCAL MODE
      ENTITY Supplier
        FIELDS ( Attachment MimeType Filename )
        WITH CORRESPONDING #( keys )
      RESULT DATA(suppliers).

    LOOP AT suppliers INTO DATA(supplier).
      APPEND VALUE #( %tky        = supplier-%tky
                      %state_area = state_area-attachment ) TO reported-supplier.

      DATA(is_invalid) = xsdbool(
           ( supplier-Attachment IS NOT INITIAL
             AND ( supplier-MimeType IS INITIAL
                   OR NOT line_exists( allowed[ mimetype = CONV string( supplier-MimeType ) ] ) ) )
        OR ( supplier-Attachment IS INITIAL AND supplier-MimeType IS NOT INITIAL ) ).

      IF is_invalid = abap_true.
        APPEND VALUE #( %tky = supplier-%tky ) TO failed-supplier.
        APPEND VALUE #( %tky                = supplier-%tky
                        %state_area         = state_area-attachment
                        %msg                = NEW zcm_rap_###( textid   = zcm_rap_###=>supplier_attachment_invalid
                                                               severity = if_abap_behv_message=>severity-error )
                        %element-Attachment = if_abap_behv=>mk-on
                        %element-MimeType   = if_abap_behv=>mk-on ) TO reported-supplier.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

ENDCLASS.
```

왜 이렇게 쓰나
- 모든 READ는 `IN LOCAL MODE` + 필요한 `FIELDS` 만 + `WITH CORRESPONDING #( keys )` 입니다. draft BO이므로 `keys` 에 `%is_draft` 가 들어 있고, `%tky` 를 그대로 넘기면 draft/활성 구분이 자동으로 유지됩니다.
- 국가 검증은 참조 샘플 `validatecountrycode` 와 같은 방식(중복 제거 → FOR ALL ENTRIES 한 번)입니다. 루프 안 SELECT를 쓰지 않습니다.
- 첨부 검증은 샘플(`validatelargeobject`)보다 단순화했습니다. 샘플은 확장자와 MIME 유형 일치까지 확인합니다. 원하면 `substring_from( val = filename pcre = '(.[^.]*)$' )` 로 확장자를 뽑아 비교해 보세요.
- `setSupplierID` 는 "저장 시"라서 같은 LUW에서 동시에 여러 사용자가 저장하면 번호가 겹칠 수 있습니다. 실무에서는 번호 범위 객체(`cl_numberrange_runtime=>number_get`, 샘플의 `adjust_numbers`)를 씁니다.

클래스 구조 해설
- 메서드 6개의 시그니처는 3단계 BDEF의 `determination`/`validation` 줄에서 생깁니다. `FOR supplier~validatename` 의 `supplier` 는 BDEF 별칭(`alias Supplier`)입니다.
- 이 BO는 managed + `authorization master ( none )` 이고 추가 저장이 없어서 세이버 클래스(lsc_)가 필요 없습니다. 저장 단계 로직은 10단계에서 **고객 확장 쪽** 세이버로 들어갑니다.

</details>

#### 5단계. 인터페이스·프로젝션 계층, MDE, 서비스

요구사항
1. 인터페이스 뷰 `ZRAP_I_SUPPLIERTP_###` (provider contract `transactional_interface`, R 뷰를 별칭 `Supplier` 로 projection). 확장 허용(데이터 소스 `Supplier`, 접미사 ZSU, composition 허용). 전파 어노테이션은 무시하고 관리 필드/LOB semantics를 다시 적으세요.
2. 인터페이스 BDEF `ZRAP_I_SUPPLIERTP_###`: `interface; use draft; extensible;`, 별칭 `Supplier`, create/update/delete와 draft 액션 5개 사용.
3. 프로젝션 뷰 `ZRAP_C_SUPPLIER_###` (transactional_query, 별칭 `Supplier`): 국가명 텍스트(`_Country._Text.CountryName`, localized), 국가 값 도움말(I_CountryVH), 검색, semantic key SupplierID, MDE 허용, 확장 허용.
4. 프로젝션 BDEF `ZRAP_C_SUPPLIER_###`: `projection; strict ( 2 ); use draft; extensible;`, 엔터티 `extensible`, `use etag`.
5. MDE `ZRAP_C_SUPPLIER_###`(`#CORE`): headerInfo(Supplier/Suppliers, 제목 Name, 설명 SupplierID), 페이싯 "General"(General_FG)과 "Contact"(Contact_FG), Rating은 별점 데이터포인트, 첨부 표시, 숨김 필드.
6. SRVD `ZRAP_UI_SUPPLIER_###`: 확장 가능, provider contract `odata_v4_ui`, `Supplier` 노출. 서비스 바인딩 `ZRAP_UI_SUPPLIER_O4_###`(OData V4 - UI) 생성 후 Publish.

**직접 추가할 어노테이션**
- `@AbapCatalog.extensibility.*` (I, C 뷰), `@AbapCatalog.extensibility.extensible` (SRVD) — 서비스 정의 확장(`extend service`) 허용.
- `@Metadata.ignorePropagatedAnnotations` — 아래 계층 어노테이션을 물려받지 않음.
- `@Metadata.allowExtensions` — MDE 허용 (고객 `#CUSTOMER` MDE도 이것이 있어야 함).
- `@ObjectModel.semanticKey` — 사람이 읽는 키(초안 표시 등).
- `@ObjectModel.text.element` — 코드 옆에 텍스트 표시.
- `@Consumption.valueHelpDefinition` — 값 도움말.
- `@Search.searchable`, `@Search.defaultSearchElement`, `@Search.fuzzinessThreshold` — 검색.
- `@ObjectModel.leadingEntity.name` (SRVD) — 서비스의 대표 엔터티.
- MDE: `@Metadata.layer`, `@UI.headerInfo`, `@UI.presentationVariant`, `@UI.facet`, `@UI.lineItem`, `@UI.selectionField`, `@UI.fieldGroup`, `@UI.identification`, `@UI.dataPoint`, `@UI.hidden`, `@UI.textArrangement`.

**확인**
- 서비스 바인딩에서 `Supplier` 를 선택하고 Preview를 누르면 List Report가 열립니다. Create → 이름/국가/이메일 입력 → 평점 4 → 첨부 업로드 → Create(저장) 후 SupplierID가 채워지는지 보세요.
- 이메일을 `abc` 로 두고 저장하면 이메일 필드가 빨갛게 표시되고 메시지 102가 나와야 합니다.

<details><summary>정답·해설</summary>

```cds
@Metadata.ignorePropagatedAnnotations: true      // R 뷰 어노테이션을 물려받지 않음 (인터페이스는 깨끗하게)
@EndUserText.label: 'Supplier - Interface'
@AccessControl.authorizationCheck: #NOT_REQUIRED

@AbapCatalog.extensibility: {
  extensible: true,
  dataSources: ['Supplier'],
  elementSuffix: 'ZSU',
  quota: {
    maximumFields: 500,
    maximumBytes: 50000
  },
  allowNewCompositions: true
}

define root view entity ZRAP_I_SUPPLIERTP_###
  provider contract transactional_interface        // 다른 BO·확장이 EML로 쓰는 안정된 계층
  as projection on ZRAP_R_SUPPLIER_### as Supplier
{
  key SupplierUUID,
      SupplierID,
      Name,
      @Consumption.valueHelpDefinition: [{ entity: { name: 'I_CountryVH', element: 'Country' } }]
      CountryCode,
      @Semantics.eMail.address: true
      EMailAddress,
      Rating,
      @Semantics.largeObject: { mimeType: 'MimeType',
                                fileName: 'Filename',
                                contentDispositionPreference: #INLINE }
      Attachment,
      @Semantics.mimeType: true
      MimeType,
      Filename,
      @Semantics.user.createdBy: true
      LocalCreatedBy,
      @Semantics.systemDateTime.createdAt: true
      LocalCreatedAt,
      @Semantics.user.localInstanceLastChangedBy: true
      LocalLastChangedBy,
      @Semantics.systemDateTime.localInstanceLastChangedAt: true
      LocalLastChangedAt,
      @Semantics.systemDateTime.lastChangedAt: true
      LastChangedAt,
      /* Associations */
      _Country
}
```

```bdef
interface;
use draft;
extensible;                     // 이 인터페이스 위에 BDEF 확장(extension using interface)을 허용

define behavior for ZRAP_I_SUPPLIERTP_### alias Supplier
{
  use create;
  use update;
  use delete;

  use action Resume;
  use action Edit;
  use action Activate;
  use action Discard;
  use action Prepare;
}
```

```cds
@EndUserText.label: 'Supplier - Projection'
@AccessControl.authorizationCheck: #NOT_REQUIRED
@Search.searchable: true
@Metadata.allowExtensions: true                   // CORE MDE + 고객 CUSTOMER MDE 허용
@ObjectModel.semanticKey: ['SupplierID']

@AbapCatalog.extensibility: {
  extensible: true,
  dataSources: ['Supplier'],
  elementSuffix: 'ZSU',
  quota: {
    maximumFields: 500,
    maximumBytes: 50000
  },
  allowNewCompositions: true
}

define root view entity ZRAP_C_SUPPLIER_###
  provider contract transactional_query
  as projection on ZRAP_R_SUPPLIER_### as Supplier
{
  key SupplierUUID,

      @Search.defaultSearchElement: true
      SupplierID,

      @Search.defaultSearchElement: true
      @Search.fuzzinessThreshold: 0.8
      Name,

      @ObjectModel.text.element: ['CountryName']
      @Consumption.valueHelpDefinition: [{ entity: { name: 'I_CountryVH', element: 'Country' },
                                           useForValidation: true }]
      CountryCode,
      _Country._Text.CountryName as CountryName : localized,   // 로그온 언어 텍스트

      EMailAddress,
      Rating,
      Attachment,
      MimeType,
      Filename,
      LocalLastChangedAt,

      /* Associations */
      _Country
}
```

```bdef
projection;
strict ( 2 );
use draft;
extensible;                     // 고객이 extension for projection 을 만들 수 있음

define behavior for ZRAP_C_SUPPLIER_### alias Supplier
extensible
use etag
{
  use create;
  use update;
  use delete;

  use action Resume;
  use action Edit;
  use action Activate;
  use action Discard;
  use action Prepare;
}
```

```cds
@Metadata.layer: #CORE                            // 기본(SAP/소유자) 레이어

@UI: { headerInfo: { typeName: 'Supplier',
                     typeNamePlural: 'Suppliers',
                     title:       { type: #STANDARD, value: 'Name' },
                     description: { type: #STANDARD, value: 'SupplierID' } },
       presentationVariant: [{ sortOrder: [{ by: 'SupplierID', direction: #ASC }],
                               visualizations: [{ type: #AS_LINEITEM }] }] }

annotate view ZRAP_C_SUPPLIER_### with
{
  @UI.facet: [
    { id: 'Supplier',  purpose: #STANDARD, type: #COLLECTION,           label: 'Supplier',     position: 10 },
    { id: 'General',   parentId: 'Supplier', purpose: #STANDARD, type: #FIELDGROUP_REFERENCE,
      targetQualifier: 'General_FG', label: 'General',      position: 10 },
    { id: 'Contact',   parentId: 'Supplier', purpose: #STANDARD, type: #FIELDGROUP_REFERENCE,
      targetQualifier: 'Contact_FG', label: 'Contact Data', position: 20 },
    { id: 'RatingDP',  purpose: #HEADER, type: #DATAPOINT_REFERENCE,
      targetQualifier: 'Rating', label: 'Rating', position: 10 }
  ]
  @UI.hidden: true
  SupplierUUID;

  @UI: { lineItem:       [ { position: 10, importance: #HIGH } ],
         selectionField: [ { position: 10 } ],
         fieldGroup:     [ { position: 10, qualifier: 'General_FG' } ] }
  SupplierID;

  @UI: { lineItem:       [ { position: 20, importance: #HIGH } ],
         selectionField: [ { position: 20 } ],
         fieldGroup:     [ { position: 20, qualifier: 'General_FG' } ] }
  Name;

  @UI: { lineItem:       [ { position: 30, importance: #MEDIUM } ],
         selectionField: [ { position: 30 } ],
         fieldGroup:     [ { position: 30, qualifier: 'General_FG' } ] }
  @UI.textArrangement: #TEXT_FIRST
  CountryCode;

  @UI.hidden: true
  CountryName;

  @UI: { lineItem:   [ { position: 40, importance: #MEDIUM } ],
         fieldGroup: [ { position: 10, qualifier: 'Contact_FG' } ] }
  EMailAddress;

  @UI: { dataPoint:  { qualifier: 'Rating', title: 'Rating', visualization: #RATING, targetValue: 5 },
         lineItem:   [ { position: 50, importance: #HIGH, type: #AS_DATAPOINT, valueQualifier: 'Rating', label: 'Rating' } ],
         fieldGroup: [ { position: 40, qualifier: 'General_FG' } ] }
  Rating;

  @UI: { fieldGroup: [ { position: 50, qualifier: 'General_FG', label: 'Attachment' } ] }
  Attachment;

  @UI.hidden: true
  MimeType;

  @UI.hidden: true
  Filename;

  @UI.hidden: true
  LocalLastChangedAt;
}
```

```cds
@EndUserText.label: 'Supplier'
@AbapCatalog.extensibility.extensible: true       // extend service 허용
@ObjectModel.leadingEntity.name: 'ZRAP_C_SUPPLIER_###'
define service ZRAP_UI_SUPPLIER_###
  provider contracts odata_v4_ui {                // C0 릴리스하려면 provider contract가 필요
  expose ZRAP_C_SUPPLIER_### as Supplier;
}
```

왜 이렇게 쓰나
- **인터페이스 계층이 왜 필요한가**: 고객 BDEF 확장은 `extension using interface zrap_i_suppliertp_###` 로 시작합니다(9단계). 고객 코드는 R 뷰가 아니라 인터페이스(`transactional_interface`)를 통해서만 BO를 읽고 고칩니다. 그래서 소유자는 R 계층을 자유롭게 바꿀 수 있고, 인터페이스만 안정적으로 유지하면 됩니다. 참조 샘플 `/DMO/I_AgencyTP` + 인터페이스 BDEF(`interface; use draft; extensible;`)와 같은 구조입니다.
- 프로젝션 BDEF의 `extensible;`(헤더)와 엔터티 `extensible` 은 고객이 `extension for projection` 에서 새 액션·연관을 `use` 할 수 있게 합니다.
- SRVD의 `provider contracts odata_v4_ui` — 참조 저장소 README에 "서비스 정의는 provider contract가 있어야 Extend(C0)로 릴리스할 수 있다"고 나와 있고, 같은 저장소의 `service_definition_agency` 파일이 `provider contracts odata_v2_ui, odata_v4_ui` 를 씁니다. (→ 어노테이션 탭: @AbapCatalog.extensibility.extensible)
- 별점 표시는 `@UI.dataPoint` 의 `visualization: #RATING` + lineItem `type: #AS_DATAPOINT` 조합입니다(샘플 리뷰 MDE와 같은 방식). (→ 어노테이션 탭: @UI.dataPoint)

자주 나는 오류와 해결
- 인터페이스 BDEF 별칭이 R BDEF 별칭과 다르면 확장 코드에서 엔터티 이름이 어긋납니다. 둘 다 `Supplier` 로 맞추세요.
- 서비스 바인딩 Preview에서 `@UI.dataPoint` 별이 안 보이면 lineItem의 `valueQualifier` 와 dataPoint `qualifier` 가 같은지 확인하세요.

</details>

#### 6단계. 동작 확인(EML 데이터 생성)과 C0 릴리스

요구사항
1. 콘솔 클래스 `ZCL_RAP_GEN_SUPPL_###` 를 만드세요. EML로 **활성 인스턴스** 공급업체 3건(정상 2건, 이메일 오류 1건)을 만들고 `COMMIT ENTITIES` 후 결과(SupplierID, failed/reported 메시지)를 콘솔에 출력합니다. 시작할 때 기존 데이터를 지웁니다(활성·draft 테이블).
2. 기본 BO 객체를 **C0(Extend) 계약**으로 릴리스하세요. 대상: `ZRAP_S_SUPPLIER_EXT_###`, `ZRAP_E_SUPPLIER_###`, `ZRAP_R_SUPPLIER_###`(CDS), `ZRAP_R_SUPPLIERDRAFT_###`, `ZRAP_I_SUPPLIERTP_###`(CDS·BDEF), `ZRAP_C_SUPPLIER_###`(CDS·BDEF), `ZRAP_UI_SUPPLIER_###`(SRVD), BDEF `ZRAP_R_SUPPLIER_###`.

**확인**
- 콘솔에 2건은 SupplierID(예: 00000001, 00000002)와 함께 성공, 1건은 failed + 메시지 102가 출력됩니다.
- 각 객체의 Properties → API State 탭에서 C0 상태가 보이면 됩니다.

<details><summary>정답·해설</summary>

```abap
CLASS zcl_rap_gen_suppl_### DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_oo_adt_classrun.
ENDCLASS.

CLASS zcl_rap_gen_suppl_### IMPLEMENTATION.

  METHOD if_oo_adt_classrun~main.
    DELETE FROM zrap_asupl_###.
    DELETE FROM zrap_dsupl_###.
    COMMIT WORK.

    MODIFY ENTITIES OF zrap_r_supplier_###
      ENTITY Supplier
        CREATE FIELDS ( Name CountryCode EMailAddress Rating )
        WITH VALUE #(
          ( %cid = 'S1' %is_draft = if_abap_behv=>mk-off
            Name = 'Seoul Steel Co.'   CountryCode = 'KR' EMailAddress = 'sales@seoulsteel.example' Rating = 4 )
          ( %cid = 'S2' %is_draft = if_abap_behv=>mk-off
            Name = 'Berlin Parts GmbH' CountryCode = 'DE' EMailAddress = 'info@berlinparts.example' Rating = 5 )
          ( %cid = 'S3' %is_draft = if_abap_behv=>mk-off
            Name = 'Broken Mail Ltd.'  CountryCode = 'GB' EMailAddress = 'no-at-sign'               Rating = 3 ) )
      MAPPED   DATA(mapped)
      FAILED   DATA(failed)
      REPORTED DATA(reported).

    COMMIT ENTITIES
      RESPONSE OF zrap_r_supplier_###
        FAILED   DATA(commit_failed)
        REPORTED DATA(commit_reported).

    IF commit_failed IS INITIAL.
      out->write( |커밋 성공| ).
    ELSE.
      out->write( |커밋 실패: { lines( commit_failed-supplier ) }건| ).
      LOOP AT commit_reported-supplier INTO DATA(rep) WHERE %msg IS BOUND.
        out->write( |  메시지: { rep-%msg->if_message~get_text( ) }| ).
      ENDLOOP.
    ENDIF.

    SELECT FROM zrap_asupl_### FIELDS supplier_id, name, rating ORDER BY supplier_id INTO TABLE @DATA(result).
    out->write( result ).
  ENDMETHOD.

ENDCLASS.
```

C0 릴리스 순서 (ADT)
1. 객체를 열고 Properties 뷰 → **API State** 탭 → "Use in Cloud Development / Extend" 영역에서 릴리스 상태를 **Released** 로 추가합니다. (메뉴·문구는 ADT 버전에 따라 다를 수 있습니다. 실제 시스템에서 확인 필요)
2. 릴리스할 때 ADT가 확장성 규칙(접미사·한도·draft query 뷰·provider contract 등)을 검사하고, 빠진 것이 있으면 오류로 알려 줍니다. 오류가 나면 1~5단계에서 빠뜨린 어노테이션을 확인하세요.

왜 이렇게 쓰나
- 이 BO는 draft BO이지만, EML에서 `%is_draft = if_abap_behv=>mk-off` 로 만들면 draft를 거치지 않고 바로 활성 인스턴스를 만듭니다. 이때도 on save 결정·검증이 모두 실행됩니다. 3번째 건은 `COMMIT ENTITIES` 중 검증에서 실패하므로 **세 건 모두 롤백** 됩니다(한 LUW). 정상 2건만 넣고 싶으면 3번째를 별도 MODIFY/COMMIT으로 나누어 보세요. 이 차이를 직접 확인하는 것이 이 단계의 핵심입니다.
- **C0 계약(Extend)** 은 "이 객체를 다른 소프트웨어 컴포넌트에서 확장해도 된다"는 약속입니다. 릴리스 노트 기준으로 DDIC 객체는 `fieldSuffix`/`quotaMaximumFields`/`quotaMaximumBytes` 가, draft BO의 BDEF는 draft query 뷰가, SRVD는 provider contract가 C0의 전제입니다. C1(Use System-Internally/Cloud Development)이 "사용해도 된다"는 약속이라면 C0은 "확장해도 된다"는 약속입니다.
- BTP 트라이얼은 모든 개발이 같은 소프트웨어 컴포넌트(ZLOCAL)에 있어 C0 없이도 확장이 활성화될 수 있습니다. 그래도 릴리스 검사로 설계 실수를 잡을 수 있으니 해 보세요. (트라이얼에서 릴리스 상태 변경이 허용되는지는 실제 시스템에서 확인 필요)

</details>

#### 7단계. [고객] 확장 패키지와 확장 필드 추가 (append 구조)

이제부터는 **고객(확장 개발자)** 역할입니다. 기본 BO 패키지 `ZRAP_###` 의 객체는 **하나도 고치지 않습니다**.

요구사항
1. 패키지 `ZRAP_###_EXT` 를 만드세요(상위 패키지는 ZLOCAL 또는 `ZRAP_###` 과 같은 수준).
2. 확장 include 구조 `ZRAP_S_SUPPLIER_EXT_###` 에 append 구조 `ZRAP_X_SUPPL_APPEND_###` 를 만들어 필드 2개를 추가하세요.
   - `zzpaymenttermzsu : abap.char(4)` — 지급 조건(NT00/NT30/NT60)
   - `zzcertifiedzsu : abap_boolean` — 인증 공급업체 여부(평점에서 자동 결정)
3. 필드 이름 규칙을 지키세요: **ZZ로 시작**, **기본 BO가 정한 접미사 ZSU로 끝남**.

append 구조 필드 표

| 필드 | 키 | 데이터 엘리먼트(또는 내장 타입) | 타입 | 길이 | 소수 | 설명 |
|---|---|---|---|---|---|---|
| zzpaymenttermzsu |  | abap.char(4) | CHAR | 4 | 0 | 지급 조건 |
| zzcertifiedzsu |  | abap_boolean | CHAR | 1 | 0 | 인증 여부 |

**직접 추가할 어노테이션** (DDIC)
- `@AbapCatalog.enhancement.category` — append 구조 자체는 더 확장되지 않게 닫음.
- `@EndUserText.label`.

**확인**
- append 구조 활성화 후 `ZRAP_ASUPL_###` 와 `ZRAP_DSUPL_###` 를 **열어 보기만** 하세요(수정하지 않음). Data Preview 열 목록에 `ZZPAYMENTTERMZSU`, `ZZCERTIFIEDZSU` 가 보이면 성공입니다. 두 테이블에 동시에 생긴 것을 확인하세요.

<details><summary>정답·해설</summary>

```abap
@EndUserText.label : 'Supplier extension fields (customer)'
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE     " append 구조 자체는 더 이상 확장하지 않음
extend type zrap_s_supplier_ext_### with zrap_x_suppl_append_### {
  zzpaymenttermzsu : abap.char(4);                      " ZZ 접두사 + ZSU 접미사
  zzcertifiedzsu   : abap_boolean;
}
```

만드는 방법(ADT): 프로젝트 탐색기에서 `ZRAP_S_SUPPLIER_EXT_###` 를 열고, 컨텍스트 메뉴 또는 New → Other ABAP Repository Object → Dictionary 에서 append 구조를 선택해 대상 구조를 지정합니다. 소스 형식은 위와 같은 `extend type ... with ...` 입니다. (참조 샘플은 abapGit XML로만 보관되어 있어 ADT 소스 문법 `extend type` 과 메뉴 위치는 실제 시스템에서 확인 필요)

왜 이렇게 쓰나
- 참조 샘플의 append `/DMO/ZZ_S_EXT_AGENCY_SLOGAN` 은 `TABCLASS APPEND`, `SQLTAB /DMO/S_EXT_INCL_AGENCY`(대상 include), `EXCLASS 1`(=#NOT_EXTENSIBLE), 필드 `/DMO/ZZSLOGANZAG` 입니다. 즉 이름 = (네임스페이스) + `ZZ` + 의미 + 접미사 `ZAG`. 네임스페이스가 없는 우리는 `ZZ...ZSU` 입니다.
- 접미사는 서로 다른 BO의 확장 필드가 같은 이름으로 부딪히는 것을 막습니다. `ZZ`(또는 `YY`) 접두사는 기본 BO 소유자가 나중에 같은 이름의 필드를 추가해도 충돌하지 않게 합니다.
- include 구조에 붙였으므로 활성 테이블과 draft 테이블이 **동시에** 넓어집니다. 테이블을 따로 고치면 안 됩니다(소유자 객체이고, C0 계약상 고객이 바꿀 수 없음).
- 확장 필드에는 내장 타입이나 릴리스된 데이터 엘리먼트(`abap_boolean` 등), 또는 고객이 직접 만든 데이터 엘리먼트를 씁니다. 샘플은 직접 만든 `/DMO/ZZ_SLOGAN` 데이터 엘리먼트를 씁니다.

자주 나는 오류와 해결
- 필드 이름에 접미사가 없거나 다르면 활성화 시 접미사 위반 오류가 납니다.
- 한도(350필드/3500)를 넘으면 오류가 납니다.

</details>

#### 8단계. [고객] CDS 뷰 확장과 `#CUSTOMER` 레이어 MDE

요구사항
1. 새 필드를 다섯 개 뷰에 차례로 올리세요. 모두 `extend view entity` 입니다.
   - `ZRAP_X_E_SUPPLIER_###` → E 뷰: `Supplier.zzpaymenttermzsu as ZZPaymentTermZSU`, `Supplier.zzcertifiedzsu as ZZCertifiedZSU`
   - `ZRAP_X_R_SUPPLIER_###` → R 뷰: `_Extension.ZZPaymentTermZSU`, `_Extension.ZZCertifiedZSU`
   - `ZRAP_X_RD_SUPPLIER_###` → draft query 뷰: `Supplier.zzpaymenttermzsu as ZZPaymentTermZSU`, ...
   - `ZRAP_X_I_SUPPLIER_###` → 인터페이스 뷰: `Supplier.ZZPaymentTermZSU`, ...
   - `ZRAP_X_C_SUPPLIER_###` → 프로젝션 뷰: `Supplier.ZZPaymentTermZSU`, ... (필드 라벨 지정)
2. MDE `ZRAP_X_C_SUPPLIER_MDE_###` 를 `#CUSTOMER` 레이어로 만들어 두 필드를 목록(lineItem), 필터(selectionField), 기본 MDE의 `General_FG` 필드 그룹에 넣으세요. 기본 MDE는 고치지 않습니다.

**직접 추가할 어노테이션**
- `@EndUserText.label` (C 뷰 확장 요소) — 화면 라벨.
- `@Metadata.layer` — MDE 레이어(#CORE < ... < #CUSTOMER 순으로 우선).
- `@UI.lineItem`, `@UI.selectionField`, `@UI.fieldGroup` — 기존 필드 그룹 qualifier를 재사용해 같은 섹션에 끼워 넣기.

**확인**
- 다섯 확장 + MDE 활성화 후 서비스 바인딩 Preview를 새로 고치세요(F12 → 캐시 지우기). 목록에 "Payment Terms", "Certified" 열이 보이고, 객체 페이지 General 섹션에 두 필드가 보이면 성공입니다.
- Edit → Payment Terms에 `NT30` 입력 → Save → 다시 열었을 때 값이 남아 있어야 합니다(draft → 활성까지 확장 필드가 흘러감 = `mapping ... corresponding extensible` 덕분).

<details><summary>정답·해설</summary>

```cds
extend view entity ZRAP_E_SUPPLIER_### with
{
  Supplier.zzpaymenttermzsu as ZZPaymentTermZSU,   // DB 필드 → CDS 요소 (dataSources: Supplier)
  Supplier.zzcertifiedzsu   as ZZCertifiedZSU
}
```

```cds
extend view entity ZRAP_R_SUPPLIER_### with
{
  _Extension.ZZPaymentTermZSU,                     // R 뷰는 _Extension 경로로만 받음 (dataSources: _Extension)
  _Extension.ZZCertifiedZSU
}
```

```cds
extend view entity ZRAP_R_SUPPLIERDRAFT_### with
{
  Supplier.zzpaymenttermzsu as ZZPaymentTermZSU,   // draft 테이블의 같은 include 필드
  Supplier.zzcertifiedzsu   as ZZCertifiedZSU
}
```

```cds
extend view entity ZRAP_I_SUPPLIERTP_### with
{
  Supplier.ZZPaymentTermZSU,
  Supplier.ZZCertifiedZSU
}
```

```cds
extend view entity ZRAP_C_SUPPLIER_### with
{
  @EndUserText.label: 'Payment Terms'
  Supplier.ZZPaymentTermZSU,
  @EndUserText.label: 'Certified'
  Supplier.ZZCertifiedZSU
}
```

```cds
@Metadata.layer: #CUSTOMER                         // 고객 레이어: CORE MDE 위에 덮어 얹힘
annotate view ZRAP_C_SUPPLIER_### with
{
  @UI: { lineItem:       [ { position: 60, importance: #MEDIUM } ],
         selectionField: [ { position: 60 } ],
         fieldGroup:     [ { position: 60, qualifier: 'General_FG' } ] }   // 기본 MDE의 필드 그룹 재사용
  ZZPaymentTermZSU;

  @UI: { lineItem:   [ { position: 70, importance: #LOW } ],
         fieldGroup: [ { position: 70, qualifier: 'General_FG' } ] }
  ZZCertifiedZSU;
}
```

왜 이렇게 쓰나
- 확장 필드가 지나가는 길: DB(include) → **E 뷰** → (`_Extension`) → **R 뷰** → **I 뷰** / **C 뷰**, 그리고 draft 쪽은 draft 테이블(include) → **draft query 뷰**. 참조 샘플의 slogan 확장(`zz_x_slogan_e/r/i/c/r_agencydraft`)이 정확히 이 다섯 개입니다. 하나라도 빠지면 BDEF가 draft/활성 사이에서 필드를 옮기지 못하거나 화면에 보이지 않습니다.
- 각 뷰가 허용한 데이터 소스 이름(`Supplier`, `_Extension`)만 쓸 수 있습니다. 예를 들어 R 뷰 확장에서 `Supplier.zzpaymenttermzsu` 를 쓰면 `dataSources` 위반 오류가 납니다. (→ 어노테이션 탭: @AbapCatalog.extensibility)
- 샘플은 UI 어노테이션을 C 뷰 확장 안에 직접 적었습니다(`zz_x_slogan_c_agency`). 여기서는 문제 요구대로 `#CUSTOMER` MDE로 분리했습니다. 둘 다 가능합니다. MDE가 확장 요소를 annotate 할 수 있는지는 기본 C 뷰의 `@Metadata.allowExtensions: true` 가 전제입니다(확장 요소에 대한 MDE 적용은 실제 시스템에서 확인 필요). (→ 어노테이션 탭: @Metadata.layer)
- 레이어 우선순위: 같은 요소·같은 어노테이션이면 `#CUSTOMER` 가 `#CORE` 를 이깁니다. 다른 요소에 적은 어노테이션은 합쳐집니다.

</details>

#### 9단계. [고객] BDEF 확장과 확장 행동 풀 (검증·결정·필드 제어)

요구사항
1. 고객 메시지 클래스 `ZRAP_X_MSG_###`:
   - 001 `지급 조건 &1 은(는) 허용되지 않습니다. NT00, NT30, NT60 중에서 고르세요.`
   - 002 `리뷰 평점은 1에서 5 사이여야 합니다.`
2. 고객 예외 클래스 `ZCM_RAP_X_SUPPL_###` (CX_STATIC_CHECK 상속, IF_ABAP_BEHV_MESSAGE + IF_T100_DYN_MSG, 속성 `payment_term`).
3. BDEF 확장 `ZRAP_X_R_SUPPLIER_###` (대상: 인터페이스 `zrap_i_suppliertp_###`, 행동 풀 `ZBP_RAP_X_SUPPLIER_###`):
   - `extend behavior for Supplier`
   - 필드 제어: `ZZCertifiedZSU` 읽기 전용, `ZZPaymentTermZSU` 필수.
   - 검증 `zzValidatePaymentTerm on save { create; field ZZPaymentTermZSU; }`
   - 결정 `zzSetDefaults on modify { create; field Rating; }` — 생성 시 지급 조건이 비면 `NT30`, 평점이 4 이상이면 인증 = X, 아니면 공백.
   - Prepare 확장: `zzValidatePaymentTerm` 추가.
4. 확장 행동 풀 `ZBP_RAP_X_SUPPLIER_###` 구현. **읽기·쓰기는 인터페이스 BDEF(`zrap_i_suppliertp_###`) 를 통해서** 합니다.

**확인**
- Preview에서 새 공급업체를 만들면 Payment Terms에 `NT30` 이 자동으로 들어갑니다.
- `NT99` 입력 → Save → 메시지 001 + 필드 강조.
- 평점 5로 저장 후 다시 열면 Certified = 예. (확장에 side effect가 없으므로 편집 중에는 바로 안 바뀌고 저장·새로 고침 후 보입니다.)
- Certified 필드는 편집 모드에서 입력할 수 없어야 합니다.

<details><summary>정답·해설</summary>

```abap
CLASS zcm_rap_x_suppl_### DEFINITION
  PUBLIC
  INHERITING FROM cx_static_check
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_abap_behv_message.
    INTERFACES if_t100_dyn_msg.

    CONSTANTS message_class TYPE symsgid VALUE 'ZRAP_X_MSG_###'.

    CONSTANTS:
      BEGIN OF payment_term_invalid,
        msgid TYPE symsgid      VALUE message_class,
        msgno TYPE symsgno      VALUE '001',
        attr1 TYPE scx_attrname VALUE 'PAYMENT_TERM',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF payment_term_invalid,
      BEGIN OF review_rating_invalid,
        msgid TYPE symsgid      VALUE message_class,
        msgno TYPE symsgno      VALUE '002',
        attr1 TYPE scx_attrname VALUE '',
        attr2 TYPE scx_attrname VALUE '',
        attr3 TYPE scx_attrname VALUE '',
        attr4 TYPE scx_attrname VALUE '',
      END OF review_rating_invalid.

    DATA payment_term TYPE c LENGTH 10 READ-ONLY.

    METHODS constructor
      IMPORTING
        textid       LIKE if_t100_message=>t100key OPTIONAL
        previous     LIKE previous OPTIONAL
        severity     TYPE if_abap_behv_message=>t_severity DEFAULT if_abap_behv_message=>severity-error
        payment_term TYPE csequence OPTIONAL.
ENDCLASS.

CLASS zcm_rap_x_suppl_### IMPLEMENTATION.

  METHOD constructor ##ADT_SUPPRESS_GENERATION.
    super->constructor( previous = previous ).

    me->payment_term = payment_term.
    if_abap_behv_message~m_severity = severity.

    CLEAR me->textid.
    IF textid IS INITIAL.
      if_t100_message~t100key = if_t100_message=>default_textid.
    ELSE.
      if_t100_message~t100key = textid.
    ENDIF.
  ENDMETHOD.

ENDCLASS.
```

```bdef
extension using interface zrap_i_suppliertp_###      // 확장은 인터페이스 BDEF 위에 만든다
implementation in class zbp_rap_x_supplier_### unique;

extend behavior for Supplier                          // 기본 BDEF의 별칭
{
  field ( readonly ) ZZCertifiedZSU;                  // 확장 필드에 대한 필드 제어
  field ( mandatory ) ZZPaymentTermZSU;

  validation zzValidatePaymentTerm on save { create; field ZZPaymentTermZSU; }

  determination zzSetDefaults on modify { create; field Rating; }   // 기본 필드(Rating) 변경도 트리거 가능

  extend draft determine action Prepare               // 기본 Prepare가 extensible 이라서 가능
  {
    validation zzValidatePaymentTerm;
  }
}
```

확장 행동 풀 글로벌 클래스(샘플과 같이 **기본 BDEF** 를 FOR BEHAVIOR OF 로 지정):

```abap
CLASS zbp_rap_x_supplier_### DEFINITION PUBLIC ABSTRACT FINAL FOR BEHAVIOR OF zrap_r_supplier_###.
ENDCLASS.

CLASS zbp_rap_x_supplier_### IMPLEMENTATION.
ENDCLASS.
```

로컬 타입:

```abap
CLASS lhc_supplier DEFINITION INHERITING FROM cl_abap_behavior_handler.
  PRIVATE SECTION.
    CONSTANTS state_area_payment_term TYPE string VALUE 'ZZ_VALIDATE_PAYMENT_TERM'.

    CONSTANTS:
      BEGIN OF payment_term,
        immediate TYPE c LENGTH 4 VALUE 'NT00',
        days_30   TYPE c LENGTH 4 VALUE 'NT30',
        days_60   TYPE c LENGTH 4 VALUE 'NT60',
      END OF payment_term.

    CONSTANTS certified_min_rating TYPE i VALUE 4.

    METHODS zzvalidatepaymentterm FOR VALIDATE ON SAVE
      IMPORTING keys FOR supplier~zzvalidatepaymentterm.

    METHODS zzsetdefaults FOR DETERMINE ON MODIFY
      IMPORTING keys FOR supplier~zzsetdefaults.
ENDCLASS.

CLASS lhc_supplier IMPLEMENTATION.

  METHOD zzvalidatepaymentterm.
    READ ENTITIES OF zrap_i_suppliertp_### IN LOCAL MODE
      ENTITY Supplier
        FIELDS ( ZZPaymentTermZSU )
        WITH CORRESPONDING #( keys )
      RESULT DATA(suppliers).

    LOOP AT suppliers INTO DATA(supplier).
      APPEND VALUE #( %tky        = supplier-%tky
                      %state_area = state_area_payment_term ) TO reported-supplier.

      IF     supplier-ZZPaymentTermZSU <> payment_term-immediate
         AND supplier-ZZPaymentTermZSU <> payment_term-days_30
         AND supplier-ZZPaymentTermZSU <> payment_term-days_60.
        APPEND VALUE #( %tky = supplier-%tky ) TO failed-supplier.
        APPEND VALUE #( %tky                      = supplier-%tky
                        %state_area               = state_area_payment_term
                        %msg                      = NEW zcm_rap_x_suppl_###(
                                                          textid       = zcm_rap_x_suppl_###=>payment_term_invalid
                                                          payment_term = supplier-ZZPaymentTermZSU )
                        %element-ZZPaymentTermZSU = if_abap_behv=>mk-on ) TO reported-supplier.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

  METHOD zzsetdefaults.
    DATA updates TYPE TABLE FOR UPDATE zrap_i_suppliertp_###.

    READ ENTITIES OF zrap_i_suppliertp_### IN LOCAL MODE
      ENTITY Supplier
        FIELDS ( Rating ZZPaymentTermZSU ZZCertifiedZSU )
        WITH CORRESPONDING #( keys )
      RESULT DATA(suppliers).

    LOOP AT suppliers INTO DATA(supplier).
      DATA(new_term) = COND #( WHEN supplier-ZZPaymentTermZSU IS INITIAL
                               THEN payment_term-days_30
                               ELSE supplier-ZZPaymentTermZSU ).
      DATA(new_certified) = xsdbool( supplier-Rating >= certified_min_rating ).

      " 바뀐 것이 있을 때만 UPDATE (결정이 자기 자신을 계속 트리거하지 않도록)
      IF new_term <> supplier-ZZPaymentTermZSU OR new_certified <> supplier-ZZCertifiedZSU.
        APPEND VALUE #( %tky             = supplier-%tky
                        ZZPaymentTermZSU = new_term
                        ZZCertifiedZSU   = new_certified
                        %control = VALUE #( ZZPaymentTermZSU = if_abap_behv=>mk-on
                                            ZZCertifiedZSU   = if_abap_behv=>mk-on ) ) TO updates.
      ENDIF.
    ENDLOOP.

    IF updates IS INITIAL.
      RETURN.
    ENDIF.

    MODIFY ENTITIES OF zrap_i_suppliertp_### IN LOCAL MODE
      ENTITY Supplier
        UPDATE FROM updates
      REPORTED DATA(update_reported).

    reported = CORRESPONDING #( DEEP update_reported ).
  ENDMETHOD.

ENDCLASS.
```

왜 이렇게 쓰나
- 첫 줄 `extension using interface zrap_i_suppliertp_###` 와 `extend behavior for <별칭>` 은 참조 샘플 `/DMO/ZZ_X_COUNTRY_R_AGENCYTP` 와 같은 문법입니다. 확장 행동 풀의 글로벌 클래스는 샘플처럼 `FOR BEHAVIOR OF <기본 R BDEF>` 입니다.
- 확장 코드에서 EML은 **인터페이스 BDEF** 로 합니다(`READ ENTITIES OF zrap_i_suppliertp_###`). 샘플 확장 핸들러도 모두 `/dmo/i_agencytp` 로 읽고 씁니다. `IN LOCAL MODE` 는 확장에서도 같은 의미(기능 제어·권한 건너뜀)입니다.
- 확장 요소 이름(검증·결정·이벤트·액션)도 고객 접두사로 시작합니다. 샘플은 `/DMO/zzValidateDiallingCode` 처럼 (네임스페이스)+`zz` 를 씁니다. 우리는 `zz...` 입니다. 기본 BO가 나중에 같은 이름을 추가해도 충돌하지 않게 하기 위해서입니다.
- 결정의 트리거로 **기본 필드 `Rating`** 을 쓸 수 있습니다(샘플의 `zzDetermineCountryCode on modify { field PhoneNumber; }` 와 같은 방식).
- `field ( readonly ) ...` / `field ( mandatory ) ...` 를 확장 필드에 거는 것은 샘플에 없는 형태입니다. 확장 필드에는 필드 특성을 줄 수 있지만 **기본 필드의 특성은 확장에서 바꿀 수 없다**는 것이 원칙입니다(확장 BDEF의 필드 특성 문법은 실제 시스템에서 확인 필요, 릴리스 버전에 따라 다름).
- 기본 BDEF에 side effect가 없고 인터페이스 BDEF에 `use side effects` 가 없으므로, 편집 중 Rating을 바꿔도 Certified가 즉시 화면에 갱신되지 않습니다. 기본 BO 소유자가 side effect를 열어 주어야 하는 부분이라는 점을 기억하세요.

클래스 구조 해설
- `zzvalidatepaymentterm`, `zzsetdefaults` 의 시그니처는 확장 BDEF의 `validation`/`determination` 줄에서 생깁니다. `FOR supplier~...` 의 `supplier` 는 기본 BDEF의 별칭입니다.
- 프레임워크는 기본 행동 풀의 검증과 확장 행동 풀의 검증을 **모두** 호출합니다. 순서는 보장되지 않으므로 서로 결과에 의존하지 않게 작성합니다.

</details>

#### 10단계. [고객] 새 자식 노드 추가 — 공급업체 리뷰 (composition 확장 + with additional save + 이벤트)

요구사항
1. 테이블 `ZRAPX_SREVA_###`(활성), `ZRAPX_SREVD_###`(draft) — 아래 필드 표.
2. CDS
   - `ZRAPX_R_SUPPLREV_###`: 활성 테이블 select, `association to parent ZRAP_R_SUPPLIER_### as _Supplier`.
   - `ZRAPX_I_SUPPLREV_###`: 인터페이스 projection, `_Supplier : redirected to parent ZRAP_I_SUPPLIERTP_###`.
   - `ZRAPX_C_SUPPLREV_###`: UI projection, `_Supplier : redirected to parent ZRAP_C_SUPPLIER_###`, MDE 허용.
   - 뷰 확장 3개: R 뷰에 `composition [0..*] of ZRAPX_R_SUPPLREV_### as ZZ_ReviewZSU`, I 뷰에 `Supplier.ZZ_ReviewZSU : redirected to composition child ...`, C 뷰에 같은 redirect + 객체 페이지 "Reviews" 표 페이싯.
   - 추상 엔터티 `ZRAPX_D_REVCREATED_###` (ReviewUUID, Rating, ReviewComment) — 이벤트 파라미터.
   - 리뷰 MDE `ZRAPX_C_SUPPLREV_###`(`#CUSTOMER`).
3. BDEF 확장 `ZRAP_X_R_SUPPLIER_###` 에 추가
   - `extend behavior for Supplier` 안: `association ZZ_ReviewZSU { create; with draft; }`, 이벤트 `zzReviewCreated parameter ZRAPX_D_REVCREATED_###`, Prepare에 리뷰 검증 추가.
   - `define behavior for ZRAPX_R_SUPPLREV_### alias ZZ_Review using ZRAPX_I_SUPPLREV_###` : `with additional save`, 테이블 2개, etag master, `lock dependent`, `authorization dependent`, update/delete, ReviewUUID managed numbering, 읽기 전용 필드, Rating 필수, 검증 `zzValidateRating`, `association _Supplier { with draft; }`, 매핑.
4. 확장 행동 풀에 리뷰 핸들러(`zzValidateRating`, 오류 시 `%path` 로 부모 표시)와 세이버(`save_modified` 에서 새 리뷰마다 `RAISE ENTITY EVENT`) 추가.
5. 프로젝션 확장 `ZRAP_X_C_SUPPLIER_###` (`extension for projection`)와 서비스 확장 `ZRAP_X_UI_SUPPLIER_###` (`extend service`).

리뷰 활성 테이블 `ZRAPX_SREVA_###`

| 필드 | 키 | 데이터 엘리먼트(또는 내장 타입) | 타입 | 길이 | 소수 | 설명 |
|---|---|---|---|---|---|---|
| client | X | abap.clnt | CLNT | 3 | 0 | 클라이언트 |
| review_uuid | X | sysuuid_x16 | RAW | 16 | 0 | 리뷰 키 (managed numbering) |
| supplier_uuid |  | sysuuid_x16 | RAW | 16 | 0 | 부모 공급업체 |
| rating |  | abap.int1 | INT1 | 3 | 0 | 평점 1~5 |
| review_comment |  | abap.char(255) | CHAR | 255 | 0 | 리뷰 내용 |
| reviewer |  | abp_creation_user | CHAR | 12 | 0 | 작성자 |
| local_created_at |  | abp_creation_tstmpl | DEC | 21 | 7 | 작성 시각 |
| local_last_changed_at |  | abp_locinst_lastchange_tstmpl | DEC | 21 | 7 | 최종 변경(etag) |

draft 테이블 `ZRAPX_SREVD_###`: mandt(키), reviewuuid(키), supplieruuid, rating, reviewcomment, reviewer, localcreatedat, locallastchangedat + `"%admin" : include sych_bdl_draft_admin_inc`.

**직접 추가할 어노테이션**
- 테이블: `@AbapCatalog.enhancement.category`, `@AbapCatalog.tableCategory`, `@AbapCatalog.deliveryClass`, `@AbapCatalog.dataMaintenance`.
- CDS: `@Semantics.user.createdBy`, `@Semantics.systemDateTime.createdAt`, `@Semantics.systemDateTime.localInstanceLastChangedAt`, `@Metadata.ignorePropagatedAnnotations`, `@Metadata.allowExtensions`.
- C 뷰 확장: `@UI.facet` (type #LINEITEM_REFERENCE, targetElement) — 새 composition을 표 섹션으로.
- 리뷰 MDE: `@UI.headerInfo`, `@UI.lineItem`, `@UI.identification`, `@UI.dataPoint`(#RATING), `@UI.multiLineText`, `@UI.hidden`.

**확인**
- 공급업체 객체 페이지에 "Reviews" 표가 생기고, Edit 모드에서 Create로 리뷰를 추가할 수 있어야 합니다.
- 평점 7로 Save → 리뷰 행과 함께 메시지 002가 표시되어야 합니다(`%path` 덕분에 부모 화면에서 보임).
- 정상 리뷰를 저장하면 저장 단계에서 이벤트가 발생합니다. R-04에서 만든 이벤트 소비 패턴(로컬 이벤트 핸들러 `FOR EVENTS OF zrap_i_suppliertp_###`)으로 받아 보면 확인할 수 있습니다(선택).

<details><summary>정답·해설</summary>

```abap
@EndUserText.label : 'Supplier review (extension, active)'
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table zrapx_sreva_### {
  key client            : abap.clnt not null;
  key review_uuid       : sysuuid_x16 not null;
  supplier_uuid         : sysuuid_x16;
  rating                : abap.int1;
  review_comment        : abap.char(255);
  reviewer              : abp_creation_user;
  local_created_at      : abp_creation_tstmpl;
  local_last_changed_at : abp_locinst_lastchange_tstmpl;
}
```

```abap
@EndUserText.label : 'Supplier review (extension, draft)'
@AbapCatalog.enhancement.category : #EXTENSIBLE_ANY
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table zrapx_srevd_### {
  key mandt          : mandt not null;
  key reviewuuid     : sysuuid_x16 not null;
  supplieruuid       : sysuuid_x16;
  rating             : abap.int1;
  reviewcomment      : abap.char(255);
  reviewer           : abp_creation_user;
  localcreatedat     : abp_creation_tstmpl;
  locallastchangedat : abp_locinst_lastchange_tstmpl;
  "%admin"           : include sych_bdl_draft_admin_inc;
}
```

```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Supplier Review (extension)'
define view entity ZRAPX_R_SUPPLREV_###
  as select from zrapx_sreva_###
  association to parent ZRAP_R_SUPPLIER_### as _Supplier on $projection.SupplierUUID = _Supplier.SupplierUUID
{
  key review_uuid           as ReviewUUID,
      supplier_uuid         as SupplierUUID,
      rating                as Rating,
      review_comment        as ReviewComment,
      @Semantics.user.createdBy: true
      reviewer              as Reviewer,
      @Semantics.systemDateTime.createdAt: true
      local_created_at      as LocalCreatedAt,
      @Semantics.systemDateTime.localInstanceLastChangedAt: true
      local_last_changed_at as LocalLastChangedAt,
      _Supplier
}
```

```cds
extend view entity ZRAP_R_SUPPLIER_### with
composition [0..*] of ZRAPX_R_SUPPLREV_### as ZZ_ReviewZSU   // allowNewCompositions: true 덕분에 가능
{
  ZZ_ReviewZSU
}
```

```cds
@Metadata.ignorePropagatedAnnotations: true
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Supplier Review - Interface'
define view entity ZRAPX_I_SUPPLREV_###
  as projection on ZRAPX_R_SUPPLREV_###
{
  key ReviewUUID,
      SupplierUUID,
      Rating,
      ReviewComment,
      @Semantics.user.createdBy: true
      Reviewer,
      @Semantics.systemDateTime.createdAt: true
      LocalCreatedAt,
      @Semantics.systemDateTime.localInstanceLastChangedAt: true
      LocalLastChangedAt,
      /* Associations */
      _Supplier : redirected to parent ZRAP_I_SUPPLIERTP_###
}
```

```cds
extend view entity ZRAP_I_SUPPLIERTP_### with
{
  Supplier.ZZ_ReviewZSU : redirected to composition child ZRAPX_I_SUPPLREV_###
}
```

```cds
@EndUserText.label: 'Supplier Review'
@AccessControl.authorizationCheck: #NOT_REQUIRED
@Metadata.allowExtensions: true
define view entity ZRAPX_C_SUPPLREV_###
  as projection on ZRAPX_R_SUPPLREV_###
{
  key ReviewUUID,
      SupplierUUID,
      Rating,
      ReviewComment,
      Reviewer,
      LocalCreatedAt,
      LocalLastChangedAt,
      /* Associations */
      _Supplier : redirected to parent ZRAP_C_SUPPLIER_###
}
```

```cds
extend view entity ZRAP_C_SUPPLIER_### with
{
  @UI.facet: [ { id:            'ZZReview',
                 purpose:       #STANDARD,
                 type:          #LINEITEM_REFERENCE,      // 자식 목록을 표로 표시
                 label:         'Reviews',
                 position:      30,
                 targetElement: 'ZZ_ReviewZSU' } ]          // 확장 composition 이름
  Supplier.ZZ_ReviewZSU : redirected to composition child ZRAPX_C_SUPPLREV_###
}
```

```cds
@EndUserText.label: 'Supplier review created - event parameter'
define abstract entity ZRAPX_D_REVCREATED_###
{
  ReviewUUID    : sysuuid_x16;
  Rating        : abap.int1;
  ReviewComment : abap.char(255);
}
```

```cds
@Metadata.layer: #CUSTOMER
@UI: { headerInfo: { typeName: 'Review',
                     typeNamePlural: 'Reviews',
                     title: { type: #STANDARD, value: 'ReviewComment' } },
       presentationVariant: [{ sortOrder: [{ by: 'LocalCreatedAt', direction: #DESC }],
                               visualizations: [{ type: #AS_LINEITEM }] }] }
annotate view ZRAPX_C_SUPPLREV_### with
{
  @UI.facet: [ { id: 'Review', purpose: #STANDARD, type: #IDENTIFICATION_REFERENCE, label: 'Review', position: 10 } ]
  @UI.hidden: true
  ReviewUUID;

  @UI.hidden: true
  SupplierUUID;

  @UI: { dataPoint:      { title: 'Rating', visualization: #RATING, targetValue: 5 },
         lineItem:       [ { position: 10, importance: #HIGH, type: #AS_DATAPOINT, label: 'Rating' } ],
         identification: [ { position: 10, label: 'Rating' } ] }
  Rating;

  @UI.multiLineText: true
  @UI: { lineItem:       [ { position: 20 } ],
         identification: [ { position: 20 } ] }
  ReviewComment;

  @UI: { lineItem: [ { position: 30 } ] }
  Reviewer;

  @UI: { lineItem: [ { position: 40 } ] }
  LocalCreatedAt;

  @UI.hidden: true
  LocalLastChangedAt;
}
```

BDEF 확장 `ZRAP_X_R_SUPPLIER_###` 최종본 (9단계 내용 + 리뷰):

```bdef
extension using interface zrap_i_suppliertp_###
implementation in class zbp_rap_x_supplier_### unique;

extend behavior for Supplier
{
  field ( readonly ) ZZCertifiedZSU;
  field ( mandatory ) ZZPaymentTermZSU;

  validation zzValidatePaymentTerm on save { create; field ZZPaymentTermZSU; }

  determination zzSetDefaults on modify { create; field Rating; }

  event zzReviewCreated parameter ZRAPX_D_REVCREATED_###;   // 고객 이벤트

  association ZZ_ReviewZSU { create; with draft; }          // 새 composition에 create-by-association

  extend draft determine action Prepare
  {
    validation zzValidatePaymentTerm;
    validation ZZ_Review~zzValidateRating;                  // 자식 검증도 Prepare에 포함
  }
}

define behavior for ZRAPX_R_SUPPLREV_### alias ZZ_Review using ZRAPX_I_SUPPLREV_###
with additional save                                        // 기본 BDEF가 허용했기 때문에 가능
persistent table zrapx_sreva_###
draft table zrapx_srevd_###
etag master LocalLastChangedAt
lock dependent
authorization dependent
{
  update;
  delete;

  field ( readonly, numbering : managed ) ReviewUUID;
  field ( readonly ) SupplierUUID, Reviewer, LocalCreatedAt, LocalLastChangedAt;
  field ( mandatory ) Rating;

  validation zzValidateRating on save { create; field Rating; }

  association _Supplier { with draft; }

  mapping for zrapx_sreva_### corresponding
  {
    ReviewUUID         = review_uuid;
    SupplierUUID       = supplier_uuid;
    Rating             = rating;
    ReviewComment      = review_comment;
    Reviewer           = reviewer;
    LocalCreatedAt     = local_created_at;
    LocalLastChangedAt = local_last_changed_at;
  }
}
```

확장 행동 풀 `ZBP_RAP_X_SUPPLIER_###` 로컬 타입에 **추가** (9단계 `lhc_supplier` 아래):

```abap
CLASS lhc_zz_review DEFINITION INHERITING FROM cl_abap_behavior_handler.
  PRIVATE SECTION.
    CONSTANTS state_area_rating TYPE string VALUE 'ZZ_VALIDATE_REVIEW_RATING'.

    METHODS zzvalidaterating FOR VALIDATE ON SAVE
      IMPORTING keys FOR zz_review~zzvalidaterating.
ENDCLASS.

CLASS lhc_zz_review IMPLEMENTATION.

  METHOD zzvalidaterating.
    READ ENTITIES OF zrap_i_suppliertp_### IN LOCAL MODE
      ENTITY ZZ_Review
        FIELDS ( Rating )
        WITH CORRESPONDING #( keys )
        RESULT DATA(reviews)
      ENTITY ZZ_Review BY \_Supplier
        FROM CORRESPONDING #( keys )
        LINK DATA(supplier_links).

    LOOP AT reviews INTO DATA(review).
      APPEND VALUE #( %tky        = review-%tky
                      %state_area = state_area_rating ) TO reported-zz_review.

      IF review-Rating < 1 OR review-Rating > 5.
        APPEND VALUE #( %tky = review-%tky ) TO failed-zz_review.
        APPEND VALUE #( %tky              = review-%tky
                        %state_area       = state_area_rating
                        %msg              = NEW zcm_rap_x_suppl_###( textid = zcm_rap_x_suppl_###=>review_rating_invalid )
                        %element-Rating   = if_abap_behv=>mk-on
                        %path-supplier-%tky = VALUE #( supplier_links[ KEY draft source-%tky = review-%tky ]-target-%tky OPTIONAL ) )
               TO reported-zz_review.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

ENDCLASS.

CLASS lsc_supplier_ext DEFINITION INHERITING FROM cl_abap_behavior_saver.
  PROTECTED SECTION.
    METHODS save_modified    REDEFINITION.
    METHODS cleanup_finalize REDEFINITION.
ENDCLASS.

CLASS lsc_supplier_ext IMPLEMENTATION.

  METHOD save_modified.
    " with additional save: managed 저장이 DB에 쓰는 것과 같은 시점에 추가 로직 실행
    IF create-zz_review IS INITIAL.
      RETURN.
    ENDIF.

    RAISE ENTITY EVENT zrap_i_suppliertp_###~zzReviewCreated
      FROM VALUE #( FOR review IN create-zz_review
                    ( SupplierUUID  = review-SupplierUUID
                      ReviewUUID    = review-ReviewUUID
                      Rating        = review-Rating
                      ReviewComment = review-ReviewComment ) ).
  ENDMETHOD.

  METHOD cleanup_finalize.
  ENDMETHOD.

ENDCLASS.
```

프로젝션 확장 `ZRAP_X_C_SUPPLIER_###`:

```bdef
extension for projection;

extend behavior for Supplier
{
  use association ZZ_ReviewZSU { create; with draft; }
}

define behavior for ZRAPX_C_SUPPLREV_### alias ZZ_Review
{
  use update;
  use delete;

  use association _Supplier { with draft; }
}
```

서비스 확장 `ZRAP_X_UI_SUPPLIER_###`:

```cds
extend service ZRAP_UI_SUPPLIER_### with {
  expose ZRAPX_C_SUPPLREV_### as ZZ_Review;
}
```

왜 이렇게 쓰나
- 전체 구조는 참조 샘플의 리뷰 확장(`zz_x_review_r_agency`, `zz_x_review_i_agency`, `zz_x_review_c_agency`, `zz_x_review_r_agencytp`, `zz_x_review_c_agencytp`, `zz_x_review_ui_agency`)과 1:1로 대응합니다.
- **새 엔터티는 `define behavior for ... using <인터페이스 뷰>`** 로 정의합니다. 확장이 인터페이스 위에서 동작하므로, 새 엔터티도 자기 인터페이스 뷰를 알려 줘야 합니다(샘플: `using /DMO/ZZ_I_AGENCY_REVIEWTP`).
- `lock dependent` / `authorization dependent` 에 `by _Supplier` 를 쓰지 않은 것은 샘플과 같습니다(부모 연관이 하나뿐이라 추론됨).
- 샘플 리뷰는 late numbering(`adjust_numbers` + `%tmp`)으로 순번 키를 만들지만, 여기서는 단순하게 `numbering : managed` UUID를 썼습니다.
- **`with additional save` 의 의미**: managed BO가 DB에 쓰는 것은 그대로 두고, 같은 저장 단계에서 `save_modified` 를 추가로 호출해 줍니다. 여기서는 새 리뷰마다 비즈니스 이벤트를 발생시켰습니다(샘플 `lsc_r_agency~save_modified` 와 같은 방식). 이벤트는 저장 단계에서만 발생시킬 수 있으므로 additional save가 꼭 필요합니다. 기본 BDEF 헤더의 `extensible { with additional save; }` 가 없으면 이 줄을 쓸 수 없습니다.
- `RAISE ENTITY EVENT` 의 이름은 `<인터페이스 BDEF>~<이벤트>` 입니다. 이벤트 파생 타입은 키(SupplierUUID) + 파라미터(ReviewUUID, Rating, ReviewComment)를 한 줄로 가지므로 위처럼 평평하게 채웁니다(샘플과 같은 방식).
- C 뷰 확장의 `@UI.facet` 은 **새 요소** 에 붙였기 때문에 기본 MDE의 페이싯 배열을 덮어쓰지 않고 페이싯 하나가 추가됩니다(샘플과 같은 방식). (→ 어노테이션 탭: @UI.facet)

클래스 구조 해설
- `lhc_zz_review~zzvalidaterating` 은 확장 BDEF의 `validation zzValidateRating` 줄에서 생깁니다. `reported-zz_review`, `failed-zz_review` 의 이름은 새 엔터티 별칭 `ZZ_Review` 에서 옵니다.
- `%path-supplier-%tky` 는 자식 메시지를 부모 인스턴스 아래에 보여 주기 위한 경로입니다. `LINK DATA(...)` 의 `KEY draft` 는 draft 여부까지 포함한 키로 찾는다는 뜻입니다(샘플과 같음).
- `lsc_supplier_ext~save_modified` 는 기본 BO의 저장 단계에서 프레임워크가 호출합니다. `create-zz_review` 에는 이번 저장에서 새로 만들어진 리뷰가 들어 있습니다.

자주 나는 오류와 해결
- 리뷰 draft 테이블이 없거나 필드명이 CDS 별칭과 다르면 BDEF 확장 활성화 시 draft 테이블 오류가 납니다. ADT 퀵픽스로 draft 테이블을 생성하면 이름이 자동으로 맞춰집니다.
- 서비스 바인딩 Preview에서 리뷰 표가 안 보이면 서비스 확장(`extend service`)이 활성화되었는지, 바인딩을 다시 Publish 했는지 확인하세요.

</details>

#### 11단계. 확장 규칙 총정리와 최종 확인

요구사항
1. 아래 표의 각 항목에 대해, **이 실습의 어느 단계에서 그 규칙을 만났는지** 적어 보세요.
2. 고객 패키지 `ZRAP_###_EXT` 를 통째로 삭제했다고 가정할 때 기본 BO가 그대로 동작하는지 설명해 보세요(실제로 삭제하지는 마세요).
3. 서비스 바인딩 Preview에서 끝에서 끝까지 확인: 공급업체 생성(지급 조건 기본값) → 평점 5 → 리뷰 2건(정상 1건, 평점 9 오류 1건) → 오류 수정 → 저장 → 다시 열어 Certified와 리뷰 확인.

**확인**
- 위 3번 시나리오가 모두 기대대로 동작하면 R-10 완료입니다.

<details><summary>정답·해설</summary>

| 규칙 | 내용 | 만난 단계 |
|---|---|---|
| 필드 이름 | 확장 필드는 `ZZ`(또는 `YY`, 네임스페이스) 접두사 + 기본 BO가 정한 접미사(`ZSU`) | 1, 7 |
| 확장 요소 이름 | 검증·결정·이벤트·액션·연관 이름도 `zz`/`ZZ_` 접두사(샘플: `/DMO/zz...`, `/DMO/ZZ_ReviewZAG`) | 9, 10 |
| 필드 추가 위치 | 테이블이 아니라 **확장 include 구조** 에만 append. 한도(quota) 안에서만 | 1, 7 |
| 뷰 확장 | `@AbapCatalog.extensibility.extensible: true` 인 뷰만, `dataSources` 에 적힌 소스에서만 요소 추가 | 2, 8 |
| 새 연관·조인 | `allowNewDatasources: false` 이면 금지 | 2 |
| 새 자식 | `allowNewCompositions: true` 인 뷰만 | 2, 10 |
| 행동 확장 | 기본 BDEF가 `extensible` + `extensible { ... }` 에 적은 종류만(결정 on modify/on save, 검증, additional save). 엔터티가 `extensible` 이어야 `extend behavior for` 가능 | 3, 9 |
| Prepare | 기본이 `draft determine action Prepare extensible` 일 때만 `extend draft determine action Prepare` | 3, 9 |
| 매핑 | 기본 매핑이 `corresponding extensible` 이면 확장 필드 자동 매핑 | 3, 8 |
| 확장의 EML | 인터페이스 BDEF(`transactional_interface`) 를 통해서만 | 5, 9 |
| draft | draft BO는 draft query 뷰가 있어야 확장 가능(C0 전제) | 2, 6 |
| 서비스 | SRVD가 `@AbapCatalog.extensibility.extensible: true` + provider contract | 5, 10 |
| 바꿀 수 없는 것 | 기본 필드의 타입·이름·필드 특성, 기본 결정/검증의 구현, 기본 매핑, 키 구조, 기본 테이블 자체 | 전체 |

- 기본 BO는 고객 객체를 전혀 참조하지 않으므로, 고객 패키지가 없어져도(의존 관계가 역방향) 그대로 활성화·동작합니다. 이것이 Developer Extensibility의 핵심인 **"수정(modification) 없는 확장"** 입니다. 반대로 기본 BO 소유자는 C0로 릴리스한 확장 지점(별칭, 데이터 소스 이름, 인터페이스 요소, Prepare의 extensible 등)을 호환되지 않게 바꾸면 안 됩니다.
- 참고: S/4HANA Cloud의 **키 사용자 확장**(Custom Fields 앱)이 만드는 필드는 `ZZ1_` 접두사를 쓰는 것으로 알려져 있습니다. 이 실습(개발자 확장, ADT)과는 다른 도구입니다. (이 내용은 참조 자료에 없음, 실제 시스템에서 확인 필요)
- 릴리스 노트에는 이 밖에도 추상 BDEF 확장(`extension for abstract`), BDEF 확장의 확장(extension layering), `EXTEND CUSTOM ENTITY`, `EXTEND ABSTRACT ENTITY`, `EXTEND SERVICE` 가 소개되어 있습니다. 필요할 때 같은 원리로 적용하면 됩니다.

</details>

### R-11. Cross-BO 연관·협업 Draft·계층(Tree)·추천값: 최신 RAP 기능 [작성] ★★★
<!-- covers: with cross associations, cross-BO association, association to one (other BO root), link action, unlink action, inverse function, use association with link action, redirected to (other BO projection), with collaborative draft, use collaborative draft, draft action Share, use action Share, draft query view, authorization master ( global ), define own authorization context (설명), define hierarchy, parent child hierarchy, child to parent association, directory ... filter by, start where, siblings order by, @OData.hierarchy.recursiveHierarchy, instance hierarchy, managed reorder action, field ( hierarchy-index ), ascending association, descending association with cascading delete, copy action (설명), early numbering, earlynumbering_create, earlynumbering_cba, composition of exact one to many, association of many to one, determine action, side effects (determine action executed on ... affects messages), field ( recommendations ), recommendation function, side effects recommendation function executed on, use recommendations, @Consumption.valueHelpDefault.fetchValues, value help view, ISLM / cl_aic_islm_compl_api_factory (설명) -->

**목표**
- 서로 다른 BO(Travel → R-10의 Supplier)를 `with cross associations` 로 잇고, **link / unlink 액션과 inverse function** 으로 연관(외래 키)을 RAP 방식으로 관리할 수 있습니다.
- 작은 BO를 `with collaborative draft` + `draft action Share` 로 바꾸고, 사용자가 화면에서 무엇을 보게 되는지 설명할 수 있습니다.
- 자기 참조(부모 단위) 데이터를 `define hierarchy` 로 계층화하고, `instance hierarchy` + `managed reorder action` + link/unlink로 **편집 가능한 트리(draft)** 를 만들 수 있습니다.
- `field ( recommendations )` + `recommendation function` + side effect로 값 추천을 만들고, 결정적(ABAP) 방식과 AI(ISLM) 방식의 차이를 설명할 수 있습니다.

**전제**
- R-01~R-04의 managed Travel BO(`ZRAP_R_TRAVEL_###`, draft, 별칭 `Travel`), R-10의 Supplier BO(`ZRAP_R_SUPPLIER_###`, `ZRAP_C_SUPPLIER_###`).
- `ZRAP_MSG_###` / `ZCM_RAP_###`(생성자 `textid`, `severity`).
- 이 문제의 기능들은 비교적 최근 릴리스에 들어왔습니다(릴리스 노트: 연관 비표준 연산 link/unlink/inverse, 편집 가능한 트리 `instance hierarchy`, `with collaborative draft`, RAP recommendations). **BTP ABAP 트라이얼은 항상 최신 릴리스** 이므로 사용할 수 있어야 하지만, Fiori Elements 화면 동작은 UI5 버전에 따라 다를 수 있습니다. 문법은 모두 ABAP Flight Reference Scenario(`xbo`, `colldraft`, `hierarchy`, `rec` 패키지)에서 확인한 것만 씁니다.

**만들 객체**

| 순서 | 객체 유형 | 이름 | 역할 |
|---|---|---|---|
| 1 | 테이블 수정 | ZRAP_ATRAV_### / ZRAP_DTRAV_### | Travel에 SUPPLIER_UUID 추가 |
| 2 | CDS·BDEF 수정 | ZRAP_R_TRAVEL_###, ZRAP_C_TRAVEL_###(+MDE), ZRAP_UI_TRAVEL_### | 교차 연관 `_Supplier` + link/unlink/inverse |
| 3 | 테이블 | ZRAP_APROJ_### / ZRAP_DPROJ_### | 프로젝트(협업 draft) 활성 / draft |
| 4 | CDS | ZRAP_R_PROJECT_###, ZRAP_R_PROJECTDRAFT_###, ZRAP_C_PROJECT_###(+MDE) | 프로젝트 R / draft query / C |
| 5 | BDEF | ZRAP_R_PROJECT_###, ZRAP_C_PROJECT_### | collaborative draft + Share (+ 추천값) |
| 6 | 클래스 | ZBP_RAP_R_PROJECT_### | 프로젝트 행동 풀 |
| 7 | SRVD / SRVB | ZRAP_UI_PROJECT_### / ZRAP_UI_PROJECT_O4_### | 프로젝트 UI 서비스 |
| 8 | 테이블 | ZRAP_ORGTREE_### / ZRAP_DORGT_### | 조직도(루트, 계층 디렉터리) |
| 9 | 테이블 | ZRAP_ORGUNIT_### / ZRAP_DORGU_### | 조직 단위(자기 참조 부모) |
| 10 | CDS | ZRAP_I_ORGTREE_###, ZRAP_I_ORGUNIT_###, ZRAP_I_ORGUNITHN_###(hierarchy) | 기본 뷰 + 계층 정의 |
| 11 | CDS | ZRAP_R_ORGTREE_###, ZRAP_R_ORGUNIT_###, ZRAP_C_ORGTREE_###, ZRAP_C_ORGUNIT_###(+MDE 2개) | 트리 BO |
| 12 | BDEF | ZRAP_R_ORGTREE_###, ZRAP_C_ORGTREE_### | instance hierarchy, reorder, link/unlink |
| 13 | 클래스 | ZBP_RAP_R_ORGTREE_###, ZBP_RAP_R_ORGUNIT_### | early numbering / 검증 |
| 14 | SRVD / SRVB | ZRAP_UI_ORGTREE_### / ZRAP_UI_ORGTREE_O4_### | 트리 UI 서비스 |
| 15 | 클래스 | ZCL_RAP_GEN_ORG_### | 데모 조직도 생성 |
| 16 | 테이블 + CDS | ZRAP_PCAT_###, ZRAP_I_PRJCAT_VH_### | 카테고리 마스터 + 값 도움말 |
| 17 | 클래스 | ZCL_RAP_GEN_PCAT_### | 카테고리 데이터 생성 |

#### 1단계. Cross-BO 데이터 모델: Travel → Supplier 교차 연관

요구사항
1. Travel 활성 테이블 `ZRAP_ATRAV_###` 에 `supplier_uuid : sysuuid_x16` 을 추가하고, draft 테이블 `ZRAP_DTRAV_###` 에 `supplieruuid : sysuuid_x16` 을 추가하세요(draft 필드명 = CDS 별칭 소문자).
2. `ZRAP_R_TRAVEL_###` (R-01) 에
   - 필드 `supplier_uuid as SupplierUUID`
   - 연관 `association to one ZRAP_R_SUPPLIER_### as _Supplier on $projection.SupplierUUID = _Supplier.SupplierUUID` (다른 BO의 **루트** 로 가는 연관)
   - 연관 `_Supplier` 노출.
3. `ZRAP_C_TRAVEL_###` 에 `SupplierUUID`, `_Supplier.Name as SupplierName`, `_Supplier : redirected to ZRAP_C_SUPPLIER_###` 추가. MDE에 SupplierName을 목록·객체 페이지에 표시, SupplierUUID는 숨김.
4. 서비스 정의 `ZRAP_UI_TRAVEL_###` 에 `expose ZRAP_C_SUPPLIER_### as Supplier;` 추가.
5. R-03의 인터페이스 뷰 `ZRAP_I_TRAVEL_###` 를 만들었다면 거기에도 `SupplierUUID` 를 추가하세요.

Travel 테이블 추가 필드

| 필드 | 키 | 데이터 엘리먼트(또는 내장 타입) | 타입 | 길이 | 소수 | 설명 |
|---|---|---|---|---|---|---|
| supplier_uuid (활성) / supplieruuid (draft) |  | sysuuid_x16 | RAW | 16 | 0 | 연결된 공급업체(다른 BO) 키 |

**직접 추가할 어노테이션**
- (C 뷰) 새 어노테이션 없음. MDE: `@UI.lineItem`, `@UI.identification`(또는 기존 fieldGroup), `@UI.hidden`.

**확인**
- 다섯 객체 활성화 후 Travel Preview를 새로 고치면 "Supplier" 열(비어 있음)이 보입니다.
- R 뷰 Data Preview에서 한 줄 선택 → 우클릭 Follow Association → `_Supplier` 가 보이면 연관이 맞습니다.

<details><summary>정답·해설</summary>

R-01 테이블 소스에 추가할 줄(기존 필드 목록 안, `last_changed_at` 위 등 원하는 위치):

```abap
  supplier_uuid         : sysuuid_x16;
```

R-01 draft 테이블 소스에 추가할 줄:

```abap
  supplieruuid          : sysuuid_x16;
```

`ZRAP_R_TRAVEL_###` 에 추가할 부분(기존 코드는 R-01 그대로 두고 표시한 줄만 추가):

```cds
define root view entity ZRAP_R_TRAVEL_###
  as select from zrap_atrav_### as Travel
  // ... R-01의 기존 composition / association ...
  association to one ZRAP_R_SUPPLIER_### as _Supplier                 // ★ 추가: 다른 BO 루트로 가는 연관
    on $projection.SupplierUUID = _Supplier.SupplierUUID
{
  // ... R-01의 기존 필드 ...
  supplier_uuid as SupplierUUID,                                       // ★ 추가: 외래 키
  // ... 기존 관리 필드 ...
  _Supplier                                                            // ★ 추가: 연관 노출
  // ... 기존 연관 (_Booking 등) ...
}
```

`ZRAP_C_TRAVEL_###` 에 추가할 부분:

```cds
  SupplierUUID,                                                        // ★ 추가
  _Supplier.Name as SupplierName,                                      // ★ 추가: 공급업체 이름(경로 표현식)
  // ... 기존 연관 ...
  _Supplier : redirected to ZRAP_C_SUPPLIER_###                        // ★ 추가: 상대 BO의 프로젝션으로 재지정
```

MDE `ZRAP_C_TRAVEL_###` 에 추가:

```cds
  @UI.hidden: true
  SupplierUUID;

  @UI: { lineItem:       [ { position: 75, importance: #MEDIUM, label: 'Supplier' } ],
         identification: [ { position: 75, label: 'Supplier' } ] }
  SupplierName;
```

서비스 정의 `ZRAP_UI_TRAVEL_###` 에 추가:

```cds
  expose ZRAP_C_SUPPLIER_### as Supplier;
```

왜 이렇게 쓰나
- 참조 샘플 `/DMO/R_TRAVELTP_XBO` 는 `association to one /DMO/R_AGENCYTP_XBO as _Agency on $projection.AgencyUuid = _Agency.AgencyUuid` 로 **다른 BO의 루트** 를 가리킵니다. composition이 아니므로 Supplier의 생명주기는 Travel과 독립입니다(Travel을 지워도 Supplier는 남음).
- 프로젝션에서는 `_Agency: redirected to /DMO/C_AGENCYTP_XBO` 처럼 상대 BO의 **프로젝션 뷰** 로 재지정합니다. composition이 아니므로 `redirected to composition child` 가 아니라 그냥 `redirected to` 입니다.
- `_Supplier.Name as SupplierName` 같은 경로 표현식은 projection 뷰에서 쓸 수 있습니다(계층 샘플 `/DMO/C_EmployeeTP_HD` 의 `_Manager.FirstName as ManagerFirstName` 과 같음).
- 서비스에 Supplier를 노출해야 OData에서 `_Supplier` 내비게이션이 생깁니다.

자주 나는 오류와 해결
- draft 테이블에 필드를 추가하지 않으면 BDEF 활성화 시 "draft table is not compatible" 류 오류가 납니다. BDEF의 draft 테이블 이름에서 Ctrl+1 → 재생성 퀵픽스를 써도 됩니다(R-01에서 손으로 만든 필드 순서가 바뀔 수 있으니 결과를 확인하세요).

</details>

#### 2단계. 교차 연관 행동: link / unlink 액션과 inverse function

요구사항
1. `ZRAP_R_TRAVEL_###` BDEF 헤더에 `with cross associations;` 를 추가하세요(`with draft;` 아래).
2. Travel 엔터티에
   - `SupplierUUID` 를 읽기 전용으로(직접 입력이 아니라 link/unlink로만 바뀌게)
   - 연관 `_Supplier` 에 draft, link 액션 `linkSupplier`, unlink 액션 `unlinkSupplier`, inverse function `getTravelsBySupplier`
   - 매핑에 `SupplierUUID = supplier_uuid;` 추가(R-01 매핑이 `corresponding` 이면 생략 가능).
3. 프로젝션 BDEF `ZRAP_C_TRAVEL_###` 에서 `_Supplier` 를 draft + link/unlink와 함께 사용하세요.
4. 행동 풀에는 **코드를 추가하지 않습니다**(managed 구현). 왜 그런지 설명하세요.

**확인**
- 두 BDEF 활성화. 행동 풀에 새 메서드가 필요하다는 오류가 **없어야** 합니다.
- 서비스 바인딩에서 서비스 URL을 브라우저로 열고 `$metadata` 를 붙여, Travel 엔터티 타입 주변에 `linkSupplier`/`unlinkSupplier` 가 보이는지 확인하세요(OData에서 어떤 형태로 보이는지는 실제 시스템에서 확인 필요).
- EML로 시험하고 싶으면 테스트 클래스에서 `MODIFY ENTITIES OF zrap_r_travel_### ENTITY Travel EXECUTE` 까지 입력한 뒤 Ctrl+Space로 `linkSupplier` 가 제안되는지, 그리고 F2로 파생 타입의 구성 요소(키, 연결 대상 키)를 확인하세요. (link 액션의 EML 문법은 참조 자료에 예제가 없어 실제 시스템에서 확인 필요)

<details><summary>정답·해설</summary>

`ZRAP_R_TRAVEL_###` BDEF에 추가할 부분:

```bdef
managed implementation in class zbp_rap_r_travel_### unique;
strict ( 2 );
with draft;
with cross associations;                    // ★ 추가: 다른 BO 루트로 가는 연관에 행동(연산) 정의 허용

define behavior for ZRAP_R_TRAVEL_### alias Travel
// ... R-01의 persistent table / draft table / lock / etag / authorization 그대로 ...
{
  // ... R-01의 기존 내용 ...

  field ( readonly ) SupplierUUID;          // ★ 추가: 외래 키는 link/unlink로만 변경

  association _Supplier                     // ★ 추가
  {
    with draft;                             // draft 인스턴스 간 연관도 따라감
    link action linkSupplier;               // 외래 키를 대상 키로 채움
    unlink action unlinkSupplier;           // 외래 키를 비움
    inverse function getTravelsBySupplier;  // 대상(Supplier) 키 → 이 키를 가진 Travel 목록
  }

  mapping for zrap_atrav_###                // R-01 매핑에 한 줄 추가
  {
    // ... 기존 매핑 ...
    SupplierUUID = supplier_uuid;
  }
}
```

`ZRAP_C_TRAVEL_###` 프로젝션 BDEF의 Travel 블록에 추가:

```bdef
  use association _Supplier
  {
    with draft;
    link action linkSupplier;
    unlink action unlinkSupplier;
  }
```

왜 이렇게 쓰나
- 참조 샘플 `/DMO/R_TRAVELTP_XBO` 의 BDEF가 바로 이 형태입니다: 헤더 `with cross associations;`, `field ( readonly ) ... AgencyUuid`, 그리고 `association _Agency { with draft; link action linkAction; unlink action unlinkAction; inverse function inverseFunction; }`. 샘플 행동 풀(`/DMO/BP_R_TRAVELTP_XBO`)에는 날짜 검증만 있고 link/unlink/inverse 구현이 **없습니다**. 즉 managed BO에서는 연관 조건(`$projection.SupplierUUID = _Supplier.SupplierUUID`)을 보고 프레임워크가 외래 키를 채우고/비우고/역으로 찾는 일을 대신합니다.
- **link action**: "이 Travel을 저 Supplier에 연결" → SupplierUUID에 대상 키를 씀. **unlink action**: 외래 키를 지움. **inverse function**: Supplier 키(외래 키 값)를 입력으로 받아 그 키를 가진 Travel 인스턴스들을 돌려줌(BDL 치트시트 설명). 외래 키를 읽기 전용으로 두면 "연결 변경은 반드시 link/unlink를 거친다"는 규칙이 생겨, 연결 변경에도 잠금·etag·권한이 일관되게 적용됩니다.
- 프로젝션에서 link/unlink를 노출하는 문법은 계층 샘플 `/DMO/C_AgencyTP_HD` 의 `use association _Manager { with draft; link action linkManager; unlink action unlinkManager; }` 를 따랐습니다. inverse function을 프로젝션에 노출하는 예는 참조 자료에 없어 넣지 않았습니다(실제 시스템에서 확인 필요).
- 샘플에서는 대상 BO(`/DMO/R_AGENCYTP_XBO`)에도 `with cross associations;` 가 있습니다. 그쪽은 `association _Travel using /DMO/R_TRAVELTP_XBO \_Agency { create; with draft; }` 처럼 **반대 방향 연관에 행동을 정의** 하기 때문입니다. 우리 Supplier에는 반대 방향 행동이 없으므로 넣지 않았습니다. 활성화 시 Supplier 쪽에도 필요하다는 메시지가 나오면 R-10 BDEF 헤더에 추가하세요(실제 시스템에서 확인 필요).
- 더 나아가기(선택): 샘플은 Agency 객체 페이지에서 **Travel을 바로 생성** 하기 위해 `association _Travel using ... \_Agency { create; with draft; }` 와 `use draft as dependent;` 인 별도 프로젝션(`/DMO/C_TRAVELTP_XBO_DRAFTDP`)을 씁니다("Draft Scope"). 두 BO의 draft가 함께 활성화되는 고급 시나리오입니다.

클래스 구조 해설
- managed + 연관 조건이 단순 외래 키이므로 행동 풀 메서드가 생기지 않습니다. 만약 연관 조건으로 외래 키를 결정할 수 없는 구조(unmanaged 등)라면 구현 메서드가 필요해집니다(실제 시스템에서 ADT 퀵픽스로 확인 필요).

</details>

#### 3단계. 협업 draft용 작은 BO: 프로젝트 데이터 모델

요구사항
1. 테이블 `ZRAP_APROJ_###`(활성), `ZRAP_DPROJ_###`(draft)를 만드세요. Category 필드는 9단계 추천값에서 씁니다(미리 넣어 두면 draft 테이블을 다시 만들 필요가 없음).
2. CDS
   - `ZRAP_R_PROJECT_###` 루트 뷰 (별칭: ProjectUUID, ProjectID, Title, Description, Category, 관리 필드 5개).
   - `ZRAP_R_PROJECTDRAFT_###` draft query 뷰 (draft 테이블 + draft 관리 필드 6개).
   - `ZRAP_C_PROJECT_###` 프로젝션(transactional_query, semantic key ProjectID, 검색, MDE 허용).
   - MDE `ZRAP_C_PROJECT_###`: headerInfo(Project/Projects, 제목 Title, 설명 ProjectID), 페이싯 1개(Identification), 목록/필터.

프로젝트 활성 테이블 `ZRAP_APROJ_###`

| 필드 | 키 | 데이터 엘리먼트(또는 내장 타입) | 타입 | 길이 | 소수 | 설명 |
|---|---|---|---|---|---|---|
| client | X | abap.clnt | CLNT | 3 | 0 | 클라이언트 |
| project_uuid | X | sysuuid_x16 | RAW | 16 | 0 | 기술 키 |
| project_id |  | abap.numc(8) | NUMC | 8 | 0 | 프로젝트 번호(생성 시 입력) |
| title |  | abap.char(80) | CHAR | 80 | 0 | 제목 |
| description |  | abap.char(255) | CHAR | 255 | 0 | 설명 |
| category |  | abap.char(20) | CHAR | 20 | 0 | 카테고리(추천 대상) |
| local_created_by |  | abp_creation_user | CHAR | 12 | 0 | 생성자 |
| local_created_at |  | abp_creation_tstmpl | DEC | 21 | 7 | 생성 시각 |
| local_last_changed_by |  | abp_locinst_lastchange_user | CHAR | 12 | 0 | 최종 변경자 |
| local_last_changed_at |  | abp_locinst_lastchange_tstmpl | DEC | 21 | 7 | etag |
| last_changed_at |  | abp_lastchange_tstmpl | DEC | 21 | 7 | total etag |

draft 테이블 `ZRAP_DPROJ_###`: mandt(키), projectuuid(키), projectid, title, description, category, localcreatedby, localcreatedat, locallastchangedby, locallastchangedat, lastchangedat + `"%admin"`.

**직접 추가할 어노테이션**
- 테이블: `@AbapCatalog.enhancement.category`, `@AbapCatalog.tableCategory`, `@AbapCatalog.deliveryClass`, `@AbapCatalog.dataMaintenance`.
- CDS: `@Semantics.user.createdBy`, `@Semantics.systemDateTime.createdAt`, `@Semantics.user.localInstanceLastChangedBy`, `@Semantics.systemDateTime.localInstanceLastChangedAt`, `@Semantics.systemDateTime.lastChangedAt`, `@ObjectModel.semanticKey`, `@Search.searchable`, `@Search.defaultSearchElement`, `@Metadata.allowExtensions`, `@Metadata.ignorePropagatedAnnotations`.
- MDE: `@UI.headerInfo`, `@UI.presentationVariant`, `@UI.facet`, `@UI.lineItem`, `@UI.selectionField`, `@UI.identification`, `@UI.multiLineText`, `@UI.hidden`.

**확인**
- 테이블 2개, CDS 3개, MDE 활성화. R 뷰 Data Preview가 열리면 됩니다(BO는 다음 단계).

<details><summary>정답·해설</summary>

```abap
@EndUserText.label : 'Project (active)'
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table zrap_aproj_### {
  key client            : abap.clnt not null;
  key project_uuid      : sysuuid_x16 not null;
  project_id            : abap.numc(8);
  title                 : abap.char(80);
  description           : abap.char(255);
  category              : abap.char(20);
  local_created_by      : abp_creation_user;
  local_created_at      : abp_creation_tstmpl;
  local_last_changed_by : abp_locinst_lastchange_user;
  local_last_changed_at : abp_locinst_lastchange_tstmpl;
  last_changed_at       : abp_lastchange_tstmpl;
}
```

```abap
@EndUserText.label : 'Project (draft)'
@AbapCatalog.enhancement.category : #EXTENSIBLE_ANY
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table zrap_dproj_### {
  key mandt          : mandt not null;
  key projectuuid    : sysuuid_x16 not null;
  projectid          : abap.numc(8);
  title              : abap.char(80);
  description        : abap.char(255);
  category           : abap.char(20);
  localcreatedby     : abp_creation_user;
  localcreatedat     : abp_creation_tstmpl;
  locallastchangedby : abp_locinst_lastchange_user;
  locallastchangedat : abp_locinst_lastchange_tstmpl;
  lastchangedat      : abp_lastchange_tstmpl;
  "%admin"           : include sych_bdl_draft_admin_inc;
}
```

```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Project (collaborative draft)'
@Metadata.ignorePropagatedAnnotations: true
define root view entity ZRAP_R_PROJECT_###
  as select from zrap_aproj_###
{
  key project_uuid          as ProjectUUID,
      project_id            as ProjectID,
      title                 as Title,
      description           as Description,
      category              as Category,
      @Semantics.user.createdBy: true
      local_created_by      as LocalCreatedBy,
      @Semantics.systemDateTime.createdAt: true
      local_created_at      as LocalCreatedAt,
      @Semantics.user.localInstanceLastChangedBy: true
      local_last_changed_by as LocalLastChangedBy,
      @Semantics.systemDateTime.localInstanceLastChangedAt: true
      local_last_changed_at as LocalLastChangedAt,
      @Semantics.systemDateTime.lastChangedAt: true
      last_changed_at       as LastChangedAt
}
```

```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Draft Query View: Project'
@Metadata.ignorePropagatedAnnotations: true
define view entity ZRAP_R_PROJECTDRAFT_###
  as select from zrap_dproj_###
{
  key projectuuid                   as ProjectUUID,
      projectid                     as ProjectID,
      title                         as Title,
      description                   as Description,
      category                      as Category,
      localcreatedby                as LocalCreatedBy,
      localcreatedat                as LocalCreatedAt,
      locallastchangedby            as LocalLastChangedBy,
      locallastchangedat            as LocalLastChangedAt,
      lastchangedat                 as LastChangedAt,
      draftentitycreationdatetime   as draftentitycreationdatetime,
      draftentitylastchangedatetime as draftentitylastchangedatetime,
      draftadministrativedatauuid   as draftadministrativedatauuid,
      draftentityoperationcode      as draftentityoperationcode,
      hasactiveentity               as hasactiveentity,
      draftfieldchanges             as draftfieldchanges
}
```

```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Project - Projection'
@Metadata.allowExtensions: true
@Metadata.ignorePropagatedAnnotations: true
@ObjectModel.semanticKey: [ 'ProjectID' ]
@Search.searchable: true
define root view entity ZRAP_C_PROJECT_###
  provider contract transactional_query
  as projection on ZRAP_R_PROJECT_###
{
  key ProjectUUID,
      @Search.defaultSearchElement: true
      ProjectID,
      @Search.defaultSearchElement: true
      Title,
      Description,
      Category,
      @Semantics.systemDateTime.localInstanceLastChangedAt: true
      LocalLastChangedAt
}
```

```cds
@Metadata.layer: #CORE
@UI.headerInfo: { typeName: 'Project',
                  typeNamePlural: 'Projects',
                  title:       { type: #STANDARD, value: 'Title' },
                  description: { type: #STANDARD, value: 'ProjectID' } }
@UI.presentationVariant: [ { sortOrder: [ { by: 'ProjectID', direction: #DESC } ],
                             visualizations: [ { type: #AS_LINEITEM } ] } ]
annotate entity ZRAP_C_PROJECT_### with
{
  @UI.facet: [ { id: 'Project', purpose: #STANDARD, type: #IDENTIFICATION_REFERENCE, label: 'Project', position: 10 } ]
  @UI.hidden: true
  ProjectUUID;

  @UI: { lineItem: [ { position: 10, importance: #HIGH } ], selectionField: [ { position: 10 } ],
         identification: [ { position: 10, label: 'Project ID' } ] }
  ProjectID;

  @UI: { lineItem: [ { position: 20, importance: #HIGH } ], selectionField: [ { position: 20 } ],
         identification: [ { position: 20 } ] }
  Title;

  @UI.multiLineText: true
  @UI: { identification: [ { position: 30 } ] }
  Description;

  @UI: { lineItem: [ { position: 40, importance: #MEDIUM } ], selectionField: [ { position: 40 } ],
         identification: [ { position: 40 } ] }
  Category;

  @UI.hidden: true
  LocalLastChangedAt;
}
```

왜 이렇게 쓰나
- 협업 draft 참조 샘플(`/DMO/R_TravelTP_CD`)도 UUID 키 + managed numbering + draft query 뷰(`/DMO/R_TravelDraft_CD`) 구조입니다. 협업 draft는 여러 사용자가 **같은 draft 인스턴스** 를 고치는 방식이라, 키가 처음부터 확정되는 UUID가 다루기 쉽습니다.
- `@Metadata.ignorePropagatedAnnotations: true` 를 프로젝션에도 둔 것은 샘플과 같습니다. 그래서 C 뷰의 `LocalLastChangedAt` 에 semantics를 다시 적었습니다. (→ 어노테이션 탭: @Metadata.ignorePropagatedAnnotations)

</details>

#### 4단계. `with collaborative draft` + `draft action Share`

요구사항
1. `ZRAP_MSG_###` 에 121 `프로젝트 제목을 입력하세요.`, 122 `프로젝트 번호를 입력하세요.`, 123 `프로젝트 번호가 이미 사용 중입니다.` 를 추가하고 `ZCM_RAP_###` 에 상수 `project_title_required`, `project_id_required`, `project_id_duplicate` 를 추가하세요(3단계 R-10 상수와 같은 형식).
2. BDEF `ZRAP_R_PROJECT_###`:
   - managed, 행동 풀 `ZBP_RAP_R_PROJECT_###`, strict 2, **`with collaborative draft;`**
   - persistent/draft 테이블(draft query 뷰 지정), etag master LocalLastChangedAt, lock master total etag LastChangedAt, `authorization master ( global )`.
   - ProjectUUID managed numbering + readonly, 관리 필드 readonly, ProjectID는 `readonly : update, mandatory : create`, Title 필수.
   - 검증 `validateProjectID on save { create; field ProjectID; }`, `validateTitle on save { create; field Title; }`.
   - draft 액션: Activate optimized, Discard, Edit, Resume, Prepare(검증 2개), **`draft action Share;`**
3. 행동 풀: 전역 권한(create/update/Edit/delete 허용 — 실습용), 두 검증.
4. 프로젝션 BDEF: **`use collaborative draft;`**, `use action Share;`
5. SRVD `ZRAP_UI_PROJECT_###`, 바인딩 `ZRAP_UI_PROJECT_O4_###`(OData V4 - UI).
6. 두 사람(또는 브라우저 두 개, 서로 다른 사용자)이 같은 프로젝트를 편집해 보고, 사용자에게 무엇이 보이는지 정리하세요.

**확인**
- Preview: 프로젝트 생성(번호 1001, 제목 입력) → Save.
- Edit → 객체 페이지 머리글/툴바에 **공유(Share)** 관련 버튼이 보이는지 확인. 다른 사용자를 초대하고, 그 사용자가 같은 프로젝트를 열면 같은 draft를 함께 편집할 수 있어야 합니다.
- 트라이얼에서 다른 사용자를 쓰기 어렵다면, 최소한 BDEF 활성화·Edit/Save 동작과 `$metadata` 에 `Share` 액션이 있는지까지 확인하세요.

<details><summary>정답·해설</summary>

```bdef
managed implementation in class zbp_rap_r_project_### unique;
strict ( 2 );
with collaborative draft;                     // 여러 사용자가 같은 draft 인스턴스를 동시에 편집

define behavior for ZRAP_R_PROJECT_### alias Project
persistent table zrap_aproj_###
draft table zrap_dproj_### query ZRAP_R_PROJECTDRAFT_###
etag master LocalLastChangedAt
lock master total etag LastChangedAt
authorization master ( global )
{
  field ( readonly, numbering : managed ) ProjectUUID;
  field ( readonly ) LocalCreatedBy, LocalCreatedAt, LocalLastChangedBy, LocalLastChangedAt, LastChangedAt;
  field ( readonly : update, mandatory : create ) ProjectID;
  field ( mandatory ) Title;

  create;
  update;
  delete;

  validation validateProjectID on save { create; field ProjectID; }
  validation validateTitle on save { create; field Title; }

  draft action Activate optimized;
  draft action Discard;
  draft action Edit;
  draft action Resume;
  draft determine action Prepare
  {
    validation validateProjectID;
    validation validateTitle;
  }
  draft action Share;                          // 다른 사용자를 draft에 초대하는 액션

  mapping for zrap_aproj_### corresponding
  {
    ProjectUUID        = project_uuid;
    ProjectID          = project_id;
    Title              = title;
    Description        = description;
    Category           = category;
    LocalCreatedBy     = local_created_by;
    LocalCreatedAt     = local_created_at;
    LocalLastChangedBy = local_last_changed_by;
    LocalLastChangedAt = local_last_changed_at;
    LastChangedAt      = last_changed_at;
  }
}
```

```abap
CLASS zbp_rap_r_project_### DEFINITION PUBLIC ABSTRACT FINAL FOR BEHAVIOR OF zrap_r_project_###.
ENDCLASS.

CLASS zbp_rap_r_project_### IMPLEMENTATION.
ENDCLASS.
```

로컬 타입:

```abap
CLASS lhc_project DEFINITION INHERITING FROM cl_abap_behavior_handler.
  PRIVATE SECTION.
    CONSTANTS:
      BEGIN OF state_area,
        project_id TYPE string VALUE 'VALIDATE_PROJECT_ID',
        title      TYPE string VALUE 'VALIDATE_TITLE',
      END OF state_area.

    METHODS get_global_authorizations FOR GLOBAL AUTHORIZATION
      IMPORTING REQUEST requested_authorizations FOR Project RESULT result.

    METHODS validateprojectid FOR VALIDATE ON SAVE
      IMPORTING keys FOR project~validateprojectid.

    METHODS validatetitle FOR VALIDATE ON SAVE
      IMPORTING keys FOR project~validatetitle.
ENDCLASS.

CLASS lhc_project IMPLEMENTATION.

  METHOD get_global_authorizations.
    " 실습용: 모두 허용. 실제로는 AUTHORITY-CHECK OBJECT ... 결과로 allowed/unauthorized 결정
    IF requested_authorizations-%create = if_abap_behv=>mk-on.
      result-%create = if_abap_behv=>auth-allowed.
    ENDIF.
    " Edit는 update와 같이 취급 (샘플과 같은 규칙)
    IF    requested_authorizations-%update      = if_abap_behv=>mk-on
       OR requested_authorizations-%action-Edit = if_abap_behv=>mk-on.
      result-%update      = if_abap_behv=>auth-allowed.
      result-%action-Edit = if_abap_behv=>auth-allowed.
    ENDIF.
    IF requested_authorizations-%delete = if_abap_behv=>mk-on.
      result-%delete = if_abap_behv=>auth-allowed.
    ENDIF.
  ENDMETHOD.

  METHOD validateprojectid.
    TYPES: BEGIN OF ty_id,
             project_id TYPE zrap_aproj_###-project_id,
           END OF ty_id.
    DATA ids TYPE SORTED TABLE OF ty_id WITH UNIQUE KEY project_id.

    READ ENTITIES OF zrap_r_project_### IN LOCAL MODE
      ENTITY Project
        FIELDS ( ProjectID )
        WITH CORRESPONDING #( keys )
      RESULT DATA(projects).

    ids = CORRESPONDING #( projects DISCARDING DUPLICATES MAPPING project_id = ProjectID EXCEPT * ).
    DELETE ids WHERE project_id IS INITIAL.

    IF ids IS NOT INITIAL.
      " 같은 번호를 쓰는 활성 인스턴스 (자기 자신 제외는 루프에서)
      SELECT FROM zrap_aproj_### FIELDS project_uuid, project_id
        FOR ALL ENTRIES IN @ids
        WHERE project_id = @ids-project_id
        INTO TABLE @DATA(existing).
    ENDIF.

    LOOP AT projects INTO DATA(project).
      APPEND VALUE #( %tky        = project-%tky
                      %state_area = state_area-project_id ) TO reported-project.

      IF project-ProjectID IS INITIAL.
        APPEND VALUE #( %tky = project-%tky ) TO failed-project.
        APPEND VALUE #( %tky               = project-%tky
                        %state_area        = state_area-project_id
                        %msg               = NEW zcm_rap_###( textid   = zcm_rap_###=>project_id_required
                                                              severity = if_abap_behv_message=>severity-error )
                        %element-ProjectID = if_abap_behv=>mk-on ) TO reported-project.
      ELSE.
        LOOP AT existing INTO DATA(other) WHERE project_id = project-ProjectID AND project_uuid <> project-ProjectUUID.
          APPEND VALUE #( %tky = project-%tky ) TO failed-project.
          APPEND VALUE #( %tky               = project-%tky
                          %state_area        = state_area-project_id
                          %msg               = NEW zcm_rap_###( textid   = zcm_rap_###=>project_id_duplicate
                                                                severity = if_abap_behv_message=>severity-error )
                          %element-ProjectID = if_abap_behv=>mk-on ) TO reported-project.
          EXIT.
        ENDLOOP.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

  METHOD validatetitle.
    READ ENTITIES OF zrap_r_project_### IN LOCAL MODE
      ENTITY Project
        FIELDS ( Title )
        WITH CORRESPONDING #( keys )
      RESULT DATA(projects).

    LOOP AT projects INTO DATA(project).
      APPEND VALUE #( %tky        = project-%tky
                      %state_area = state_area-title ) TO reported-project.

      IF project-Title IS INITIAL.
        APPEND VALUE #( %tky = project-%tky ) TO failed-project.
        APPEND VALUE #( %tky           = project-%tky
                        %state_area    = state_area-title
                        %msg           = NEW zcm_rap_###( textid   = zcm_rap_###=>project_title_required
                                                          severity = if_abap_behv_message=>severity-error )
                        %element-Title = if_abap_behv=>mk-on ) TO reported-project.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

ENDCLASS.
```

```bdef
projection;
strict ( 2 );
use collaborative draft;                     // 프로젝션도 collaborative draft를 사용한다고 선언

define behavior for ZRAP_C_PROJECT_### alias Project
use etag
{
  use create;
  use update;
  use delete;

  use action Activate;
  use action Discard;
  use action Edit;
  use action Resume;
  use action Prepare;
  use action Share;                          // UI에 Share 노출
}
```

```cds
@EndUserText.label: 'Project'
@ObjectModel.leadingEntity.name: 'ZRAP_C_PROJECT_###'
define service ZRAP_UI_PROJECT_### {
  expose ZRAP_C_PROJECT_### as Project;
}
```

왜 이렇게 쓰나
- 헤더 `with collaborative draft;`, `draft action Share;`, 프로젝션 `use collaborative draft;` + `use action Share;` 는 참조 샘플 `/DMO/R_TravelTP_CD` / `/DMO/C_TravelTP_CD` 와 같습니다. BDL 치트시트도 "`with collaborative draft` 는 draft 처리를 켜면서 여러 사용자가 같은 draft 인스턴스에서 동시에 작업하게 한다"고 설명합니다.
- **일반 draft와의 차이**: 일반 draft는 Edit를 누른 사용자 한 명만 draft를 가지며(배타적), 다른 사용자는 "다른 사용자가 편집 중" 상태로 막힙니다. 협업 draft는 draft 소유자가 **Share** 로 다른 사용자를 초대할 수 있고, 초대된 사용자는 같은 draft에 들어와 함께 고칩니다. 마지막에 누군가 Save(Activate)하면 공동 결과가 활성 데이터가 됩니다.
- **사용자가 보는 것(Fiori Elements V4 기준, 일반적인 동작)**: 편집 모드 객체 페이지에 공유/초대 버튼과 현재 함께 편집 중인 사용자 표시(아바타 등)가 나타나고, 다른 사용자가 바꾼 값이 화면에 반영되며, 같은 필드를 동시에 고치지 못하게 표시됩니다. 정확한 버튼 이름·위치·실시간 반영 방식은 UI5/Fiori Elements 버전에 따라 다르므로 실제 시스템에서 확인하세요.
- 샘플은 `authorization master ( instance, global )` 과 `define own authorization context { '/DMO/TR_CD'; }` 를 함께 씁니다. 권한 컨텍스트는 "이 BO가 검사하는 권한 객체 목록"을 선언하는 문법입니다. 이 실습은 권한 객체를 만들지 않으므로 `( global )` + 모두 허용으로 단순화했습니다. 협업 draft에 권한 컨텍스트가 필수인지는 참조 자료로 확인되지 않습니다(실제 시스템에서 확인 필요).
- `mandatory` 는 화면 표시용 특성일 뿐 저장을 막지 않으므로, ProjectID/Title 검증을 직접 구현했습니다. 중복 검사는 FOR ALL ENTRIES로 한 번만 조회합니다.

클래스 구조 해설
- `authorization master ( global )` → `FOR GLOBAL AUTHORIZATION ... REQUEST requested_authorizations ... RESULT result` 메서드. 인스턴스 키가 없고 요청된 연산 플래그만 들어옵니다. Edit 액션도 `%action-Edit` 로 따로 요청되므로 update와 함께 처리합니다(샘플과 같은 규칙).
- Share는 draft 액션이라 행동 풀 구현이 없습니다(Edit/Activate와 같이 프레임워크가 처리).

</details>

#### 5단계. 조직도 트리 데이터 모델: 루트(디렉터리)와 자기 참조 조직 단위

편집 가능한 트리는 참조 샘플(`/DMO/FLIGHT_HIERARCHY` 의 draft 시나리오)과 똑같이 **루트 엔터티(계층 디렉터리) + 자식 엔터티(트리 노드, 자기 참조 부모)** 구조로 만듭니다. 샘플의 Agency → Employee(Manager) 가 우리의 OrgTree → OrgUnit(ParentUnit) 입니다.

요구사항
1. 루트 테이블 `ZRAP_ORGTREE_###`(활성)과 `ZRAP_DORGT_###`(draft).
2. 노드 테이블 `ZRAP_ORGUNIT_###`(활성)과 `ZRAP_DORGU_###`(draft). `parent_unit` 은 같은 조직도 안의 다른 `unit_id` 를 가리키고, 최상위 단위는 `000000`(초기값)입니다. `sibling_order_number` 는 형제 사이 순서입니다.
3. 두 키 모두 early numbering(7단계)으로 정해지므로 draft 테이블에 DRAFTUUID 키가 필요 없습니다.

루트 테이블 `ZRAP_ORGTREE_###`

| 필드 | 키 | 데이터 엘리먼트(또는 내장 타입) | 타입 | 길이 | 소수 | 설명 |
|---|---|---|---|---|---|---|
| client | X | abap.clnt | CLNT | 3 | 0 | 클라이언트 |
| org_id | X | abap.numc(6) | NUMC | 6 | 0 | 조직도 번호 (early numbering) |
| name |  | abap.char(60) | CHAR | 60 | 0 | 조직도 이름 |
| description |  | abap.char(255) | CHAR | 255 | 0 | 설명 |
| local_created_by |  | abp_creation_user | CHAR | 12 | 0 | 생성자 |
| local_created_at |  | abp_creation_tstmpl | DEC | 21 | 7 | 생성 시각 |
| local_last_changed_by |  | abp_locinst_lastchange_user | CHAR | 12 | 0 | 최종 변경자 |
| local_last_changed_at |  | abp_locinst_lastchange_tstmpl | DEC | 21 | 7 | etag |
| last_changed_at |  | abp_lastchange_tstmpl | DEC | 21 | 7 | total etag |

노드 테이블 `ZRAP_ORGUNIT_###`

| 필드 | 키 | 데이터 엘리먼트(또는 내장 타입) | 타입 | 길이 | 소수 | 설명 |
|---|---|---|---|---|---|---|
| client | X | abap.clnt | CLNT | 3 | 0 | 클라이언트 |
| org_id | X | abap.numc(6) | NUMC | 6 | 0 | 소속 조직도 |
| unit_id | X | abap.numc(6) | NUMC | 6 | 0 | 단위 번호 (조직도 안에서 early numbering) |
| unit_name |  | abap.char(60) | CHAR | 60 | 0 | 단위 이름 |
| unit_type |  | abap.char(4) | CHAR | 4 | 0 | 유형(DIV/DEPT/TEAM) |
| head_name |  | abap.char(60) | CHAR | 60 | 0 | 책임자 |
| parent_unit |  | abap.numc(6) | NUMC | 6 | 0 | 상위 단위(자기 참조) |
| sibling_order_number |  | abap.numc(3) | NUMC | 3 | 0 | 형제 순서(계층 인덱스) |
| local_created_by |  | abp_creation_user | CHAR | 12 | 0 | 생성자 |
| local_created_at |  | abp_creation_tstmpl | DEC | 21 | 7 | 생성 시각 |
| local_last_changed_by |  | abp_locinst_lastchange_user | CHAR | 12 | 0 | 최종 변경자 |
| local_last_changed_at |  | abp_locinst_lastchange_tstmpl | DEC | 21 | 7 | etag |

**직접 추가할 어노테이션** (DDIC)
- `@AbapCatalog.enhancement.category`, `@AbapCatalog.tableCategory`, `@AbapCatalog.deliveryClass`, `@AbapCatalog.dataMaintenance`.

**확인**
- 네 테이블 활성화.

<details><summary>정답·해설</summary>

```abap
@EndUserText.label : 'Org tree (active)'
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table zrap_orgtree_### {
  key client            : abap.clnt not null;
  key org_id            : abap.numc(6) not null;
  name                  : abap.char(60);
  description           : abap.char(255);
  local_created_by      : abp_creation_user;
  local_created_at      : abp_creation_tstmpl;
  local_last_changed_by : abp_locinst_lastchange_user;
  local_last_changed_at : abp_locinst_lastchange_tstmpl;
  last_changed_at       : abp_lastchange_tstmpl;
}
```

```abap
@EndUserText.label : 'Org tree (draft)'
@AbapCatalog.enhancement.category : #EXTENSIBLE_ANY
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table zrap_dorgt_### {
  key mandt          : mandt not null;
  key orgid          : abap.numc(6) not null;
  name               : abap.char(60);
  description        : abap.char(255);
  localcreatedby     : abp_creation_user;
  localcreatedat     : abp_creation_tstmpl;
  locallastchangedby : abp_locinst_lastchange_user;
  locallastchangedat : abp_locinst_lastchange_tstmpl;
  lastchangedat      : abp_lastchange_tstmpl;
  "%admin"           : include sych_bdl_draft_admin_inc;
}
```

```abap
@EndUserText.label : 'Org unit (active)'
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table zrap_orgunit_### {
  key client            : abap.clnt not null;
  key org_id            : abap.numc(6) not null;
  key unit_id           : abap.numc(6) not null;
  unit_name             : abap.char(60);
  unit_type             : abap.char(4);
  head_name             : abap.char(60);
  parent_unit           : abap.numc(6);
  sibling_order_number  : abap.numc(3);
  local_created_by      : abp_creation_user;
  local_created_at      : abp_creation_tstmpl;
  local_last_changed_by : abp_locinst_lastchange_user;
  local_last_changed_at : abp_locinst_lastchange_tstmpl;
}
```

```abap
@EndUserText.label : 'Org unit (draft)'
@AbapCatalog.enhancement.category : #EXTENSIBLE_ANY
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table zrap_dorgu_### {
  key mandt          : mandt not null;
  key orgid          : abap.numc(6) not null;
  key unitid         : abap.numc(6) not null;
  unitname           : abap.char(60);
  unittype           : abap.char(4);
  headname           : abap.char(60);
  parentunit         : abap.numc(6);
  siblingordernumber : abap.numc(3);
  localcreatedby     : abp_creation_user;
  localcreatedat     : abp_creation_tstmpl;
  locallastchangedby : abp_locinst_lastchange_user;
  locallastchangedat : abp_locinst_lastchange_tstmpl;
  "%admin"           : include sych_bdl_draft_admin_inc;
}
```

왜 이렇게 쓰나
- 샘플 노드 테이블 `/DMO/EMPLOY_A_HD` 는 키 (AGENCY, EMPLOYEE), 부모 참조 MANAGER, 형제 순서 SIBLING_ORDER_NUMBER(NUMC 3) 입니다. 같은 구조를 그대로 옮겼습니다. 형제 순서 필드는 7단계에서 `field ( hierarchy-index )` 로 지정되어 프레임워크가 관리합니다.
- 부모 참조 키에 조직도 번호가 함께 들어가야(키 = OrgId + UnitId) 서로 다른 조직도의 단위가 섞이지 않습니다.

</details>

#### 6단계. CDS 계층 정의(`define hierarchy`)와 트리 BO 뷰

요구사항
1. 기본 뷰 `ZRAP_I_ORGTREE_###`(루트 테이블)와 `ZRAP_I_ORGUNIT_###`(노드 테이블).
   - `ZRAP_I_ORGUNIT_###` 연관: `_OrgTree`(다:1, 기본 루트 뷰), `_ParentUnit`(다:1 자기 자신, OrgId + ParentUnit = UnitId), `_ChildUnit`(다:다 자기 자신, OrgId + UnitId = ParentUnit).
2. 계층 `ZRAP_I_ORGUNITHN_###`:
   - 파라미터 `P_OrgId : abap.numc( 6 )`
   - 원천 `ZRAP_I_ORGUNIT_###`, 자식→부모 연관 `_ParentUnit`
   - 디렉터리 `_OrgTree` 를 파라미터로 필터
   - 시작 조건: ParentUnit이 초기값
   - 형제 정렬: SiblingOrderNumber 오름차순
   - 요소: OrgId, UnitId(키), ParentUnit, SiblingOrderNumber
3. TP 뷰
   - `ZRAP_R_ORGTREE_###` 루트: 기본 뷰에서 select, `composition of exact one to many ZRAP_R_ORGUNIT_### as _OrgUnit`.
   - `ZRAP_R_ORGUNIT_###`: 기본 뷰에서 select, `association to parent ... as _OrgTree`, `_ParentUnit`(of many to one 자기 자신), `_ChildUnit`(of one to many 자기 자신).

**직접 추가할 어노테이션**
- `@Semantics.user.*`, `@Semantics.systemDateTime.*` — 관리 필드.
- `@EndUserText.label` (ParentUnit에 'Parent Unit').
- `@AccessControl.authorizationCheck`.

**확인**
- 다섯 객체 활성화.
- 계층 `ZRAP_I_ORGUNITHN_###` 는 Data Preview에서 파라미터 입력 창이 뜹니다. 8단계 데이터 생성 후 `000001` 을 넣으면 트리 순서대로 행과 계층 정보 열(예: 계층 레벨 등)이 나와야 합니다(어떤 계층 열이 보이는지는 실제 시스템에서 확인 필요).

<details><summary>정답·해설</summary>

```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Org Tree - Basic'
define view entity ZRAP_I_ORGTREE_###
  as select from zrap_orgtree_###
{
  key org_id                as OrgId,
      name                  as Name,
      description           as Description,
      @Semantics.user.createdBy: true
      local_created_by      as LocalCreatedBy,
      @Semantics.systemDateTime.createdAt: true
      local_created_at      as LocalCreatedAt,
      @Semantics.user.localInstanceLastChangedBy: true
      local_last_changed_by as LocalLastChangedBy,
      @Semantics.systemDateTime.localInstanceLastChangedAt: true
      local_last_changed_at as LocalLastChangedAt,
      @Semantics.systemDateTime.lastChangedAt: true
      last_changed_at       as LastChangedAt
}
```

```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Org Unit - Basic'
define view entity ZRAP_I_ORGUNIT_###
  as select from zrap_orgunit_###
  association of many to one  ZRAP_I_ORGTREE_### as _OrgTree    on  $projection.OrgId = _OrgTree.OrgId
  association of many to one  ZRAP_I_ORGUNIT_### as _ParentUnit on  $projection.OrgId      = _ParentUnit.OrgId
                                                                 and $projection.ParentUnit = _ParentUnit.UnitId
  association of many to many ZRAP_I_ORGUNIT_### as _ChildUnit  on  $projection.OrgId  = _ChildUnit.OrgId
                                                                 and $projection.UnitId = _ChildUnit.ParentUnit
{
  key org_id                as OrgId,
  key unit_id               as UnitId,
      unit_name             as UnitName,
      unit_type             as UnitType,
      head_name             as HeadName,
      @EndUserText.label: 'Parent Unit'
      parent_unit           as ParentUnit,
      sibling_order_number  as SiblingOrderNumber,
      @Semantics.user.createdBy: true
      local_created_by      as LocalCreatedBy,
      @Semantics.systemDateTime.createdAt: true
      local_created_at      as LocalCreatedAt,
      @Semantics.user.localInstanceLastChangedBy: true
      local_last_changed_by as LocalLastChangedBy,
      @Semantics.systemDateTime.localInstanceLastChangedAt: true
      local_last_changed_at as LocalLastChangedAt,

      _OrgTree,
      _ParentUnit,
      _ChildUnit
}
```

```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Org Unit Hierarchy'
define hierarchy ZRAP_I_ORGUNITHN_###
  with parameters
    P_OrgId : abap.numc( 6 )                 // 어느 조직도의 트리인지
  as parent child hierarchy(
    source ZRAP_I_ORGUNIT_###                // 노드 원천
    child to parent association _ParentUnit  // 자식 → 부모 연결
    directory _OrgTree filter by             // 계층 디렉터리(루트)로 범위 제한
      OrgId = $parameters.P_OrgId
    start where                              // 최상위 노드 조건
      ParentUnit is initial
    siblings order by                        // 형제 정렬
      SiblingOrderNumber ascending
  )
{
  key OrgId,
  key UnitId,
      ParentUnit,
      SiblingOrderNumber
}
```

```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Org Tree - Root (draft tree)'
define root view entity ZRAP_R_ORGTREE_###
  as select from ZRAP_I_ORGTREE_###
  composition of exact one to many ZRAP_R_ORGUNIT_### as _OrgUnit
{
  key OrgId,
      Name,
      Description,
      LocalCreatedBy,
      LocalCreatedAt,
      LocalLastChangedBy,
      LocalLastChangedAt,
      LastChangedAt,
      /* Associations */
      _OrgUnit
}
```

```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Org Unit - Tree node'
define view entity ZRAP_R_ORGUNIT_###
  as select from ZRAP_I_ORGUNIT_###
  association to parent ZRAP_R_ORGTREE_###          as _OrgTree    on  $projection.OrgId = _OrgTree.OrgId
  association of many to one ZRAP_R_ORGUNIT_###     as _ParentUnit on  $projection.OrgId      = _ParentUnit.OrgId
                                                                    and $projection.ParentUnit = _ParentUnit.UnitId
  association of one to many ZRAP_R_ORGUNIT_###     as _ChildUnit  on  $projection.OrgId  = _ChildUnit.OrgId
                                                                    and $projection.UnitId = _ChildUnit.ParentUnit
{
  key OrgId,
  key UnitId,
      UnitName,
      UnitType,
      HeadName,
      ParentUnit,
      SiblingOrderNumber,
      LocalCreatedBy,
      LocalCreatedAt,
      LocalLastChangedBy,
      LocalLastChangedAt,
      /* Associations */
      _OrgTree,
      _ParentUnit,
      _ChildUnit
}
```

왜 이렇게 쓰나
- `define hierarchy ... as parent child hierarchy( source ... child to parent association ... directory ... filter by ... start where ... siblings order by ... )` 는 샘플 `/DMO/I_EmployeeHN_HD` 와 같은 구조입니다. 읽기 전용 샘플 `/DMO/I_EmployeeHN_HR` 에는 `directory` 와 파라미터가 없습니다. **편집 가능한 트리(draft)** 는 트리가 루트 BO 인스턴스 하나에 속하므로 디렉터리(=루트)와 파라미터로 범위를 정합니다.
- 계층은 반드시 **기본 뷰(I)** 를 원천으로 하고, TP 뷰(R)와 같은 키·부모 연관 구조를 가져야 합니다. 그래서 I 뷰와 R 뷰 양쪽에 `_ParentUnit`/`_ChildUnit` 을 같은 조건으로 둡니다(샘플과 같음).
- `composition of exact one to many` — 노드는 정확히 하나의 루트에 속한다는 카디널리티 문법입니다(샘플 `/DMO/R_AgencyTP_HD`).
- 파라미터 타입은 샘플이 데이터 엘리먼트(`/dmo/agency_id`)를 썼고, 여기서는 루트 키와 같은 내장 타입 `abap.numc( 6 )` 를 썼습니다.

</details>

#### 7단계. 트리 BDEF: `instance hierarchy`, `managed reorder action`, link/unlink와 early numbering

요구사항
1. `ZRAP_MSG_###` 에 131 `조직도 이름을 입력하세요.`, 132 `조직 단위 이름을 입력하세요.` 추가, `ZCM_RAP_###` 에 상수 `orgtree_name_required`, `orgunit_name_required` 추가.
2. BDEF `ZRAP_R_ORGTREE_###` (managed, strict 2, draft):
   - OrgTree: 행동 풀 `ZBP_RAP_R_ORGTREE_###`, **early numbering**, 테이블 2개, lock master, total etag, 권한 없음, etag master. OrgId·관리 필드 readonly, Name 필수, `association _OrgUnit { create; with draft; }`, draft 액션, 검증 `validateName`, Prepare(루트 + 노드 검증).
   - OrgUnit: 행동 풀 `ZBP_RAP_R_ORGUNIT_###`, early numbering, 테이블 2개, `lock dependent by _OrgTree`, `authorization dependent by _OrgTree`, etag master. update/delete, OrgId·UnitId·SiblingOrderNumber·ParentUnit readonly.
   - 연관: `_OrgTree { with draft; }`, `_ParentUnit { with draft; link action linkParentUnit; unlink action unlinkParentUnit; }`, `_ChildUnit { with draft; }`
   - **`instance hierarchy ZRAP_I_ORGUNITHN_###`** 블록: `managed reorder action changeNextSibling`, `field ( hierarchy-index ) SiblingOrderNumber`, `ascending association _ParentUnit`, `descending association _ChildUnit { with cascading delete; }`
   - 검증 `validateUnitName`, `determine action checkUnitName`, side effect(UnitName 변경 시 메시지 갱신).
3. `ZBP_RAP_R_ORGTREE_###`: `earlynumbering_create`(활성·draft 최댓값 + 1), `earlynumbering_cba_orgunit`(조직도별 최댓값 + 1, 같은 요청 안의 여러 조직도·번호 충돌 방지), `validateName`.
4. `ZBP_RAP_R_ORGUNIT_###`: `validateUnitName` (`%path` 로 루트 표시).

**확인**
- BDEF와 두 클래스 활성화. 8단계에서 화면으로 확인합니다.

<details><summary>정답·해설</summary>

```bdef
managed;
strict ( 2 );
with draft;

define behavior for ZRAP_R_ORGTREE_### alias OrgTree
implementation in class zbp_rap_r_orgtree_### unique
early numbering
persistent table zrap_orgtree_###
draft table zrap_dorgt_###
lock master
total etag LastChangedAt
authorization master ( none )
etag master LocalLastChangedAt
{
  create;
  update;
  delete;

  field ( readonly ) OrgId, LocalCreatedBy, LocalCreatedAt, LocalLastChangedBy, LocalLastChangedAt, LastChangedAt;
  field ( mandatory ) Name;

  association _OrgUnit { create; with draft; }

  draft action Resume;
  draft action Edit;
  draft action Activate optimized;
  draft action Discard;

  validation validateName on save { create; field Name; }

  draft determine action Prepare
  {
    validation validateName;
    validation OrgUnit~validateUnitName;      // 자식 검증도 Prepare에 포함
  }

  mapping for zrap_orgtree_###
  {
    OrgId              = org_id;
    Name               = name;
    Description        = description;
    LocalCreatedBy     = local_created_by;
    LocalCreatedAt     = local_created_at;
    LocalLastChangedBy = local_last_changed_by;
    LocalLastChangedAt = local_last_changed_at;
    LastChangedAt      = last_changed_at;
  }
}

define behavior for ZRAP_R_ORGUNIT_### alias OrgUnit
implementation in class zbp_rap_r_orgunit_### unique
early numbering
persistent table zrap_orgunit_###
draft table zrap_dorgu_###
lock dependent by _OrgTree
authorization dependent by _OrgTree
etag master LocalLastChangedAt
{
  update;
  delete;

  field ( readonly ) OrgId, UnitId, SiblingOrderNumber;
  field ( readonly ) ParentUnit;                       // 부모 변경은 link/unlink(또는 트리 이동)로만
  field ( mandatory ) UnitName;

  association _OrgTree { with draft; }
  association _ParentUnit
  {
    with draft;
    link action linkParentUnit;                        // 다른 부모 밑으로 붙이기
    unlink action unlinkParentUnit;                    // 최상위로 떼어 내기
  }
  association _ChildUnit { with draft; }

  instance hierarchy ZRAP_I_ORGUNITHN_###              // 이 엔터티가 편집 가능한 트리의 노드임
  {
    managed reorder action changeNextSibling;          // 형제 사이 순서 변경(드래그 등), 프레임워크 구현
    field ( hierarchy-index ) SiblingOrderNumber;      // 순서를 저장하는 필드
    ascending association _ParentUnit;                 // 위로(부모) 가는 연관
    descending association _ChildUnit { with cascading delete; }   // 아래로(자식), 부모 삭제 시 자식도 삭제
  }

  validation validateUnitName on save { create; field UnitName; }

  determine action checkUnitName { validation validateUnitName; }

  side effects
  {
    determine action checkUnitName executed on field UnitName affects messages;
  }

  mapping for zrap_orgunit_###
  {
    OrgId              = org_id;
    UnitId             = unit_id;
    UnitName           = unit_name;
    UnitType           = unit_type;
    HeadName           = head_name;
    ParentUnit         = parent_unit;
    SiblingOrderNumber = sibling_order_number;
    LocalCreatedBy     = local_created_by;
    LocalCreatedAt     = local_created_at;
    LocalLastChangedBy = local_last_changed_by;
    LocalLastChangedAt = local_last_changed_at;
  }
}
```

`ZBP_RAP_R_ORGTREE_###` 글로벌 클래스:

```abap
CLASS zbp_rap_r_orgtree_### DEFINITION PUBLIC ABSTRACT FINAL FOR BEHAVIOR OF zrap_r_orgtree_###.
ENDCLASS.

CLASS zbp_rap_r_orgtree_### IMPLEMENTATION.
ENDCLASS.
```

로컬 타입:

```abap
CLASS lhc_orgtree DEFINITION INHERITING FROM cl_abap_behavior_handler.
  PRIVATE SECTION.
    CONSTANTS state_area_name TYPE string VALUE 'VALIDATE_NAME'.

    TYPES: BEGIN OF ty_max_unit,
             org_id   TYPE zrap_orgunit_###-org_id,
             max_unit TYPE zrap_orgunit_###-unit_id,
           END OF ty_max_unit,
           tt_max_unit TYPE SORTED TABLE OF ty_max_unit WITH UNIQUE KEY org_id.

    METHODS earlynumbering_create FOR NUMBERING
      IMPORTING entities FOR CREATE OrgTree.

    METHODS earlynumbering_cba_orgunit FOR NUMBERING
      IMPORTING entities FOR CREATE OrgTree\_OrgUnit.

    METHODS validatename FOR VALIDATE ON SAVE
      IMPORTING keys FOR OrgTree~validatename.
ENDCLASS.

CLASS lhc_orgtree IMPLEMENTATION.

  METHOD earlynumbering_create.
    DATA max_id TYPE zrap_orgtree_###-org_id.

    " 이미 번호가 있는 인스턴스는 그대로 mapped에 돌려줌
    LOOP AT entities INTO DATA(entity) WHERE OrgId IS NOT INITIAL.
      APPEND CORRESPONDING #( entity ) TO mapped-orgtree.
    ENDLOOP.

    DATA(entities_wo_id) = entities.
    DELETE entities_wo_id WHERE OrgId IS NOT INITIAL.
    IF entities_wo_id IS INITIAL.
      RETURN.
    ENDIF.

    " 활성과 draft 양쪽의 최댓값 (draft에도 이미 번호가 있으므로)
    SELECT SINGLE FROM zrap_orgtree_### FIELDS MAX( org_id ) INTO @DATA(max_active).
    SELECT SINGLE FROM zrap_dorgt_###   FIELDS MAX( orgid )  INTO @DATA(max_draft).
    max_id = COND #( WHEN max_draft > max_active THEN max_draft ELSE max_active ).

    LOOP AT entities_wo_id INTO DATA(entity_wo_id).
      max_id += 1.
      APPEND VALUE #( %cid      = entity_wo_id-%cid
                      %is_draft = entity_wo_id-%is_draft
                      OrgId     = max_id ) TO mapped-orgtree.
    ENDLOOP.
  ENDMETHOD.

  METHOD earlynumbering_cba_orgunit.
    DATA max_units TYPE tt_max_unit.

    " 각 조직도에 이미 있는 단위 (draft 포함, %tky로 읽음)
    READ ENTITIES OF zrap_r_orgtree_### IN LOCAL MODE
      ENTITY OrgTree BY \_OrgUnit
        FROM CORRESPONDING #( entities )
        LINK DATA(existing_units).

    " 조직도별 최댓값 = MAX(기존 단위, 요청에 번호를 들고 온 단위)
    LOOP AT existing_units INTO DATA(link).
      ASSIGN max_units[ org_id = link-source-OrgId ] TO FIELD-SYMBOL(<max>).
      IF sy-subrc <> 0.
        INSERT VALUE #( org_id = link-source-OrgId ) INTO TABLE max_units ASSIGNING <max>.
      ENDIF.
      IF link-target-UnitId > <max>-max_unit.
        <max>-max_unit = link-target-UnitId.
      ENDIF.
    ENDLOOP.

    LOOP AT entities INTO DATA(parent).
      LOOP AT parent-%target INTO DATA(target) WHERE UnitId IS NOT INITIAL.
        ASSIGN max_units[ org_id = parent-OrgId ] TO <max>.
        IF sy-subrc <> 0.
          INSERT VALUE #( org_id = parent-OrgId ) INTO TABLE max_units ASSIGNING <max>.
        ENDIF.
        IF target-UnitId > <max>-max_unit.
          <max>-max_unit = target-UnitId.
        ENDIF.
      ENDLOOP.
    ENDLOOP.

    " 번호 부여 (같은 조직도가 여러 줄에 나와도 max_units가 이어서 증가하므로 충돌 없음)
    LOOP AT entities INTO parent.
      ASSIGN max_units[ org_id = parent-OrgId ] TO <max>.
      IF sy-subrc <> 0.
        INSERT VALUE #( org_id = parent-OrgId ) INTO TABLE max_units ASSIGNING <max>.
      ENDIF.

      LOOP AT parent-%target INTO target.
        APPEND CORRESPONDING #( target ) TO mapped-orgunit ASSIGNING FIELD-SYMBOL(<mapped>).
        <mapped>-OrgId = parent-OrgId.
        IF target-UnitId IS INITIAL.
          <max>-max_unit += 1.
          <mapped>-UnitId = <max>-max_unit.
        ENDIF.
      ENDLOOP.
    ENDLOOP.
  ENDMETHOD.

  METHOD validatename.
    READ ENTITIES OF zrap_r_orgtree_### IN LOCAL MODE
      ENTITY OrgTree
        FIELDS ( Name )
        WITH CORRESPONDING #( keys )
      RESULT DATA(trees).

    LOOP AT trees INTO DATA(tree).
      APPEND VALUE #( %tky        = tree-%tky
                      %state_area = state_area_name ) TO reported-orgtree.

      IF tree-Name IS INITIAL.
        APPEND VALUE #( %tky = tree-%tky ) TO failed-orgtree.
        APPEND VALUE #( %tky          = tree-%tky
                        %state_area   = state_area_name
                        %msg          = NEW zcm_rap_###( textid   = zcm_rap_###=>orgtree_name_required
                                                         severity = if_abap_behv_message=>severity-error )
                        %element-Name = if_abap_behv=>mk-on ) TO reported-orgtree.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

ENDCLASS.
```

`ZBP_RAP_R_ORGUNIT_###` 글로벌 클래스:

```abap
CLASS zbp_rap_r_orgunit_### DEFINITION PUBLIC ABSTRACT FINAL FOR BEHAVIOR OF zrap_r_orgtree_###.
ENDCLASS.

CLASS zbp_rap_r_orgunit_### IMPLEMENTATION.
ENDCLASS.
```

로컬 타입:

```abap
CLASS lhc_orgunit DEFINITION INHERITING FROM cl_abap_behavior_handler.
  PRIVATE SECTION.
    CONSTANTS state_area_unit_name TYPE string VALUE 'VALIDATE_UNIT_NAME'.

    METHODS validateunitname FOR VALIDATE ON SAVE
      IMPORTING keys FOR OrgUnit~validateunitname.
ENDCLASS.

CLASS lhc_orgunit IMPLEMENTATION.

  METHOD validateunitname.
    READ ENTITIES OF zrap_r_orgtree_### IN LOCAL MODE
      ENTITY OrgUnit
        FIELDS ( UnitName )
        WITH CORRESPONDING #( keys )
        RESULT DATA(units)
      ENTITY OrgUnit BY \_OrgTree
        FROM CORRESPONDING #( keys )
        LINK DATA(tree_links).

    LOOP AT units INTO DATA(unit).
      APPEND VALUE #( %tky        = unit-%tky
                      %state_area = state_area_unit_name ) TO reported-orgunit.

      IF unit-UnitName IS INITIAL.
        APPEND VALUE #( %tky = unit-%tky ) TO failed-orgunit.
        APPEND VALUE #( %tky              = unit-%tky
                        %state_area       = state_area_unit_name
                        %msg              = NEW zcm_rap_###( textid   = zcm_rap_###=>orgunit_name_required
                                                             severity = if_abap_behv_message=>severity-error )
                        %element-UnitName = if_abap_behv=>mk-on
                        %path             = VALUE #( orgtree-%tky = VALUE #( tree_links[ KEY id source-%tky = unit-%tky ]-target-%tky OPTIONAL ) ) )
               TO reported-orgunit.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

ENDCLASS.
```

왜 이렇게 쓰나
- `instance hierarchy <계층 이름> { managed reorder action ...; field ( hierarchy-index ) ...; ascending association ...; descending association ... { with cascading delete; } }` 는 샘플 `/DMO/R_AgencyTP_HD` 의 Employee 블록과 같은 문법입니다. 릴리스 노트: "editable treeview 시나리오는 `instance hierarchy` 로 트리를 편집 가능하게 하고, reorder action으로 노드를 형제 사이 특정 위치로 옮긴다".
- `managed reorder action` 은 프레임워크가 SiblingOrderNumber를 다시 매겨 줍니다(구현 코드 없음). `with cascading delete` 는 부모 노드를 지우면 하위 노드도 같이 지웁니다.
- ParentUnit을 readonly로 두고 `link action`/`unlink action` 을 연 것도 샘플(Manager)과 같습니다. 트리 UI에서 노드를 다른 부모로 옮기는 동작이 이 액션들을 쓰는 것으로 보입니다(Fiori 트리 테이블의 잘라내기/붙여넣기·드래그 동작은 UI5 버전에 따라 다름, 실제 시스템에서 확인 필요).
- 샘플에는 `copy action copy;` 도 있습니다. 하위 트리 전체를 복사하는 액션인데, 샘플 구현(`_copy_recursion`)은 재귀적으로 create-by-association을 만드는 긴 코드입니다. 이 실습에서는 생략했고, 도전 과제로 샘플을 읽어 보세요. (릴리스 노트: copy action은 최신 릴리스에 추가된 트리 액션)
- **early numbering**: 키가 생성 즉시 정해져야 트리의 부모 참조(ParentUnit = 다른 노드의 UnitId)가 draft 단계부터 의미를 가집니다. 그래서 샘플도 late numbering이 아니라 early numbering을 씁니다. 루트 번호는 샘플이 번호 범위 객체를 쓰지만 여기서는 단순하게 MAX + 1을 썼습니다.
- 샘플의 cba 번호 부여는 루트 한 줄마다 최댓값을 다시 계산하므로, 같은 조직도가 한 요청에 여러 줄로 오면 번호가 겹칠 수 있습니다. 정답은 조직도별 최댓값을 정렬 테이블 `max_units` 에 들고 다니며 이어서 증가시켜 이를 막았습니다.

클래스 구조 해설
- `early numbering` (OrgTree) → `FOR NUMBERING IMPORTING entities FOR CREATE OrgTree`. 결과는 `mapped-orgtree` 에 `%cid` + `%is_draft` + 키로 돌려줍니다.
- 자식은 직접 create가 없고 `association _OrgUnit { create; }` 로만 생성되므로, 번호 메서드도 `FOR CREATE OrgTree\_OrgUnit` (create-by-association) 입니다. 이 메서드는 **루트 행동 풀** 에 있어야 합니다(연관 생성은 부모 엔터티의 연산이기 때문, 샘플도 Agency 행동 풀에 `earlynumbering_cba_employee` 가 있음).
- `ZBP_RAP_R_ORGUNIT_###` 는 BDEF의 OrgUnit 줄 `implementation in class zbp_rap_r_orgunit_### unique` 로 연결됩니다. 글로벌 클래스의 `FOR BEHAVIOR OF` 는 BDEF 이름(= 루트 이름 `zrap_r_orgtree_###`)입니다.
- `determine action checkUnitName` 은 구현이 없습니다. 지정한 검증을 즉시 실행해 주는 액션이고, side effect로 UnitName이 바뀔 때마다 Fiori가 호출해 메시지를 바로 보여 줍니다(샘플과 같음).

</details>

#### 8단계. 트리 프로젝션, `@OData.hierarchy.recursiveHierarchy`, 서비스와 확인

요구사항
1. `ZRAP_C_ORGTREE_###`(루트 projection, transactional_query, MDE 허용)와 `ZRAP_C_ORGUNIT_###`(노드 projection):
   - 노드 projection에 **계층 연결 어노테이션** 을 붙이세요(계층 `ZRAP_I_ORGUNITHN_###`).
   - OrgName(`_OrgTree.Name`), ParentUnitName(`_ParentUnit.UnitName`) 경로 필드, 검색.
   - 연관 재지정: `_OrgTree` → parent, `_ParentUnit`/`_ChildUnit` → 자기 자신 projection.
2. MDE 2개: 루트(General 필드 그룹 + "Organization Units" 표 페이싯), 노드(목록 열: UnitName, UnitType, HeadName, ParentUnit, SiblingOrderNumber).
3. 프로젝션 BDEF `ZRAP_C_ORGTREE_###`: `use draft; use side effects;`, 노드에서 `use action changeNextSibling;`, link/unlink 노출.
4. SRVD `ZRAP_UI_ORGTREE_###`(두 엔터티 노출), 바인딩 `ZRAP_UI_ORGTREE_O4_###`(OData V4 - UI).
5. 데모 데이터 클래스 `ZCL_RAP_GEN_ORG_###`: 조직도 1개, 단위 7개(CEO Office → Sales/Engineering → 팀 4개).

**직접 추가할 어노테이션**
- `@OData.hierarchy.recursiveHierarchy` — 이 엔터티를 어떤 CDS 계층으로 트리 표시할지 OData에 알려 줌.
- `@ObjectModel.text.element`, `@Search.searchable`, `@Search.defaultSearchElement`, `@Search.fuzzinessThreshold`, `@Metadata.allowExtensions`.
- MDE: `@UI.headerInfo`, `@UI.presentationVariant`, `@UI.facet`(#LINEITEM_REFERENCE, targetElement), `@UI.fieldGroup`, `@UI.lineItem`, `@UI.selectionField`, `@UI.identification`, `@UI.hidden`.

**확인**
- 데이터 생성 클래스 실행(F9) → Preview → 조직도 000001 선택 → 객체 페이지의 "Organization Units" 섹션이 **트리 표**(펼치기/접기 화살표)로 보여야 합니다.
- Edit → 노드를 펼친 뒤 형제 순서 바꾸기(드래그 또는 이동 버튼), 다른 부모로 옮기기, 하위 단위 만들기, 단위 이름 지우기(즉시 메시지) → Save.
- 부모 노드(Sales Division)를 삭제하면 하위 팀도 같이 삭제되는지 확인(cascading delete).
- 화면의 버튼 이름·위치는 UI5 버전에 따라 다를 수 있습니다(실제 시스템에서 확인 필요).

<details><summary>정답·해설</summary>

```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Org Tree - Projection'
@Metadata.allowExtensions: true
define root view entity ZRAP_C_ORGTREE_###
  provider contract transactional_query
  as projection on ZRAP_R_ORGTREE_###
{
  key OrgId,
      Name,
      Description,
      LocalLastChangedAt,
      /* Associations */
      _OrgUnit : redirected to composition child ZRAP_C_ORGUNIT_###
}
```

```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Org Unit - Projection (tree)'
@Metadata.allowExtensions: true
@OData.hierarchy.recursiveHierarchy: [{ entity.name: 'ZRAP_I_ORGUNITHN_###' }]   // 트리 표시용 계층 연결
@Search.searchable: true
define view entity ZRAP_C_ORGUNIT_###
  as projection on ZRAP_R_ORGUNIT_###
{
      @ObjectModel.text.element: ['OrgName']
  key OrgId,
  key UnitId,
      _OrgTree.Name        as OrgName,

      @Search.defaultSearchElement: true
      @Search.fuzzinessThreshold: 0.87
      UnitName,
      UnitType,
      @Search.defaultSearchElement: true
      @Search.fuzzinessThreshold: 0.87
      HeadName,
      ParentUnit,
      _ParentUnit.UnitName as ParentUnitName,
      SiblingOrderNumber,
      LocalLastChangedAt,

      /* Associations */
      _OrgTree    : redirected to parent ZRAP_C_ORGTREE_###,
      _ParentUnit : redirected to ZRAP_C_ORGUNIT_###,
      _ChildUnit  : redirected to ZRAP_C_ORGUNIT_###
}
```

```cds
@Metadata.layer: #CORE
@UI: { headerInfo: { typeName: 'Organization',
                     typeNamePlural: 'Organizations',
                     title:       { type: #STANDARD, value: 'Name' },
                     description: { type: #STANDARD, value: 'OrgId' } },
       presentationVariant: [{ sortOrder: [{ by: 'OrgId', direction: #ASC }],
                               visualizations: [{ type: #AS_LINEITEM }] }] }
annotate view ZRAP_C_ORGTREE_### with
{
  @UI.facet: [
    { id: 'OrgTree', purpose: #STANDARD, type: #COLLECTION, label: 'Organization', position: 10 },
    { id: 'General', parentId: 'OrgTree', purpose: #STANDARD, type: #FIELDGROUP_REFERENCE,
      targetQualifier: 'General_FG', label: 'General', position: 10 },
    { id: 'OrgUnit', purpose: #STANDARD, type: #LINEITEM_REFERENCE,
      label: 'Organization Units', position: 20, targetElement: '_OrgUnit' }   // 트리 표가 들어갈 자리
  ]
  @UI: { lineItem: [ { position: 10, importance: #HIGH } ], selectionField: [ { position: 10 } ],
         fieldGroup: [ { position: 10, qualifier: 'General_FG' } ] }
  OrgId;

  @UI: { lineItem: [ { position: 20, importance: #HIGH } ], selectionField: [ { position: 20 } ],
         fieldGroup: [ { position: 20, qualifier: 'General_FG' } ] }
  Name;

  @UI: { fieldGroup: [ { position: 30, qualifier: 'General_FG' } ] }
  Description;

  @UI.hidden: true
  LocalLastChangedAt;
}
```

```cds
@Metadata.layer: #CORE
@UI: { headerInfo: { typeName: 'Organization Unit',
                     typeNamePlural: 'Organization Units',
                     title:       { type: #STANDARD, value: 'UnitName' },
                     description: { type: #STANDARD, value: 'UnitId' } },
       presentationVariant: [{ sortOrder: [{ by: 'SiblingOrderNumber', direction: #ASC }],
                               visualizations: [{ type: #AS_LINEITEM }] }] }
annotate view ZRAP_C_ORGUNIT_### with
{
  @UI.facet: [ { id: 'OrgUnit', purpose: #STANDARD, type: #IDENTIFICATION_REFERENCE, label: 'Unit', position: 10 } ]
  @UI.hidden: true
  OrgId;

  @UI: { lineItem: [ { position: 10 } ], identification: [ { position: 10 } ] }
  UnitId;

  @UI: { lineItem: [ { position: 20, importance: #HIGH } ], identification: [ { position: 20 } ],
         selectionField: [ { position: 20 } ] }
  UnitName;

  @UI: { lineItem: [ { position: 30 } ], identification: [ { position: 30 } ] }
  UnitType;

  @UI: { lineItem: [ { position: 40 } ], identification: [ { position: 40 } ] }
  HeadName;

  @UI: { lineItem: [ { position: 50, label: 'Parent Unit' } ], identification: [ { position: 50, label: 'Parent Unit' } ] }
  @UI.textArrangement: #TEXT_FIRST
  ParentUnit;

  @UI.hidden: true
  ParentUnitName;

  @UI.hidden: true
  OrgName;

  @UI: { lineItem: [ { position: 60, label: 'Order' } ] }
  SiblingOrderNumber;

  @UI.hidden: true
  LocalLastChangedAt;
}
```

```bdef
projection;
strict ( 2 );
use draft;
use side effects;

define behavior for ZRAP_C_ORGTREE_### alias OrgTree
use etag
{
  use create;
  use update;
  use delete;

  use action Resume;
  use action Edit;
  use action Activate;
  use action Discard;
  use action Prepare;

  use association _OrgUnit { create; with draft; }
}

define behavior for ZRAP_C_ORGUNIT_### alias OrgUnit
use etag
{
  use update;
  use delete;

  use action changeNextSibling;              // reorder 액션 노출

  use association _OrgTree { with draft; }
  use association _ParentUnit
  {
    with draft;
    link action linkParentUnit;
    unlink action unlinkParentUnit;
  }
  use association _ChildUnit { with draft; }
}
```

```cds
@EndUserText.label: 'Organization Tree'
@ObjectModel.leadingEntity.name: 'ZRAP_C_ORGTREE_###'
define service ZRAP_UI_ORGTREE_### {
  expose ZRAP_C_ORGTREE_### as OrgTree;
  expose ZRAP_C_ORGUNIT_### as OrgUnit;
}
```

```abap
CLASS zcl_rap_gen_org_### DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_oo_adt_classrun.
ENDCLASS.

CLASS zcl_rap_gen_org_### IMPLEMENTATION.

  METHOD if_oo_adt_classrun~main.
    DATA units TYPE STANDARD TABLE OF zrap_orgunit_### WITH EMPTY KEY.
    DATA now   TYPE timestampl.

    GET TIME STAMP FIELD now.
    DATA(user) = cl_abap_context_info=>get_user_technical_name( ).

    DELETE FROM zrap_orgtree_###.
    DELETE FROM zrap_dorgt_###.
    DELETE FROM zrap_orgunit_###.
    DELETE FROM zrap_dorgu_###.

    INSERT zrap_orgtree_### FROM @( VALUE zrap_orgtree_###( org_id = '000001'
                                             name                  = 'ACME Korea'
                                             description           = 'Demo organization'
                                             local_created_by      = user
                                             local_created_at      = now
                                             local_last_changed_by = user
                                             local_last_changed_at = now
                                             last_changed_at       = now ) ).

    " parent_unit = '000000' → 최상위
    units = VALUE #( org_id = '000001' local_created_by = user local_created_at = now
                     local_last_changed_by = user local_last_changed_at = now
                     ( unit_id = '000001' unit_name = 'CEO Office'           unit_type = 'DIV'  head_name = 'Kim'  parent_unit = '000000' sibling_order_number = '001' )
                     ( unit_id = '000002' unit_name = 'Sales Division'       unit_type = 'DIV'  head_name = 'Lee'  parent_unit = '000001' sibling_order_number = '001' )
                     ( unit_id = '000003' unit_name = 'Engineering Division' unit_type = 'DIV'  head_name = 'Park' parent_unit = '000001' sibling_order_number = '002' )
                     ( unit_id = '000004' unit_name = 'Domestic Sales'       unit_type = 'TEAM' head_name = 'Choi' parent_unit = '000002' sibling_order_number = '001' )
                     ( unit_id = '000005' unit_name = 'Global Sales'         unit_type = 'TEAM' head_name = 'Jung' parent_unit = '000002' sibling_order_number = '002' )
                     ( unit_id = '000006' unit_name = 'Platform Team'        unit_type = 'TEAM' head_name = 'Kang' parent_unit = '000003' sibling_order_number = '001' )
                     ( unit_id = '000007' unit_name = 'Mobile Team'          unit_type = 'TEAM' head_name = 'Yoon' parent_unit = '000003' sibling_order_number = '002' ) ).

    INSERT zrap_orgunit_### FROM TABLE @units.
    COMMIT WORK.

    out->write( |조직도 1건, 단위 { lines( units ) }건 생성| ).

    " 계층을 ABAP SQL로 직접 읽어 보기 (파라미터 전달)
    SELECT FROM ZRAP_I_ORGUNITHN_###( P_OrgId = '000001' )
      FIELDS UnitId, ParentUnit, SiblingOrderNumber
      INTO TABLE @DATA(tree).
    out->write( tree ).
  ENDMETHOD.

ENDCLASS.
```

왜 이렇게 쓰나
- `@OData.hierarchy.recursiveHierarchy:[{ entity.name: '...' }]` 는 샘플 `/DMO/C_EmployeeTP_HD`(편집 가능), `/DMO/C_Employee_HR`(읽기 전용) 모두에 있는 핵심 어노테이션입니다. OData V4 서비스가 이 엔터티에 계층 정보를 붙여 Fiori Elements가 트리 표로 그립니다. (→ 어노테이션 탭: @OData.hierarchy.recursiveHierarchy)
- **목록(List Report) 자체를 트리로**: 읽기 전용 샘플(`/DMO/UI_Employee_HR`)은 노드 엔터티를 서비스의 대표 엔터티로 두고 디렉터리 없는 계층을 써서 List Report가 바로 트리가 됩니다. 편집 가능한 draft 트리는 위처럼 **루트 객체 페이지 안의 트리 표** 입니다. 둘의 차이를 기억하세요.
- 데이터 생성은 EML 대신 직접 INSERT 했습니다. ParentUnit이 readonly라 외부 EML로는 부모를 지정할 수 없기 때문입니다(실무라면 link 액션 또는 BO 내부 `IN LOCAL MODE`).
- 계층은 ABAP SQL에서도 `FROM 계층( 파라미터 = 값 )` 으로 읽을 수 있습니다(릴리스 노트: CDS 계층은 ABAP SQL 계층으로 접근). 결과 순서가 트리 순서인지 확인해 보세요.

자주 나는 오류와 해결
- 트리 표가 평범한 표로 보이면: 서비스 바인딩이 OData **V4** 인지, C 뷰의 계층 이름 철자, MDE의 `targetElement: '_OrgUnit'` 을 확인하세요.

</details>

#### 9단계. 추천값(Recommendations) 준비: 카테고리 마스터·값 도움말·BDEF

요구사항
1. 카테고리 마스터 테이블 `ZRAP_PCAT_###` 와 데이터 생성 클래스 `ZCL_RAP_GEN_PCAT_###`(5개 카테고리 + 키워드).
2. 값 도움말 뷰 `ZRAP_I_PRJCAT_VH_###`(Category, CategoryText).
3. `ZRAP_C_PROJECT_###` 의 Category에 값 도움말을 걸고, R/C 뷰 헤더에 "값 도움말 목록은 사용자가 명시적으로 요청할 때만 가져오기"를 지정하세요.
4. `ZRAP_R_PROJECT_###` BDEF에
   - `field ( recommendations ) Category;`
   - `recommendation function GetRecommendedCategory;`
   - side effect: Title 또는 Description이 바뀌면 추천 함수 다시 실행.

카테고리 테이블 `ZRAP_PCAT_###`

| 필드 | 키 | 데이터 엘리먼트(또는 내장 타입) | 타입 | 길이 | 소수 | 설명 |
|---|---|---|---|---|---|---|
| client | X | abap.clnt | CLNT | 3 | 0 | 클라이언트 |
| category | X | abap.char(20) | CHAR | 20 | 0 | 카테고리 코드 |
| category_text |  | abap.char(60) | CHAR | 60 | 0 | 카테고리 이름 |
| keywords |  | abap.char(255) | CHAR | 255 | 0 | 쉼표로 구분한 키워드(추천 계산용) |

**직접 추가할 어노테이션**
- `@Consumption.valueHelpDefinition` — Category 값 도움말.
- `@Consumption.valueHelpDefault.fetchValues` — 값 도움말 목록 기본 로딩 방식.
- (VH 뷰) `@Search.searchable`, `@Search.defaultSearchElement`, `@ObjectModel.text.element`, `@Semantics.text`.

**확인**
- 데이터 생성 클래스 실행 후 Preview: Category 값 도움말에 5개 카테고리가 보입니다.
- BDEF 활성화 시 `GetRecommendedCategory` 구현이 없다는 메시지가 나오면 10단계에서 구현합니다.

<details><summary>정답·해설</summary>

```abap
@EndUserText.label : 'Project category master'
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table zrap_pcat_### {
  key client    : abap.clnt not null;
  key category  : abap.char(20) not null;
  category_text : abap.char(60);
  keywords      : abap.char(255);
}
```

```abap
CLASS zcl_rap_gen_pcat_### DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_oo_adt_classrun.
ENDCLASS.

CLASS zcl_rap_gen_pcat_### IMPLEMENTATION.

  METHOD if_oo_adt_classrun~main.
    DATA categories TYPE STANDARD TABLE OF zrap_pcat_### WITH EMPTY KEY.

    categories = VALUE #(
      ( category = 'IT'        category_text = 'IT / System'
        keywords = 'erp,sap,abap,rap,fiori,cloud,system,migration,시스템,클라우드,개발,전환' )
      ( category = 'MARKETING' category_text = 'Marketing'
        keywords = 'campaign,brand,marketing,social,launch,캠페인,브랜드,마케팅,홍보,출시' )
      ( category = 'HR'        category_text = 'Human Resources'
        keywords = 'hiring,training,onboarding,culture,채용,교육,온보딩,인사,조직문화' )
      ( category = 'FACILITY'  category_text = 'Facility'
        keywords = 'office,building,move,renovation,사무실,이전,건물,공사,시설' )
      ( category = 'FINANCE'   category_text = 'Finance'
        keywords = 'budget,audit,tax,closing,예산,감사,세금,결산,재무' ) ).

    DELETE FROM zrap_pcat_###.
    INSERT zrap_pcat_### FROM TABLE @categories.
    COMMIT WORK.

    out->write( |카테고리 { lines( categories ) }건 생성| ).
  ENDMETHOD.

ENDCLASS.
```

```cds
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Project Category Value Help'
@Search.searchable: true
define view entity ZRAP_I_PRJCAT_VH_###
  as select from zrap_pcat_###
{
      @Search.defaultSearchElement: true
      @ObjectModel.text.element: ['CategoryText']   // 코드 옆에 이름 표시
  key category      as Category,
      @Search.defaultSearchElement: true
      @Semantics.text: true                          // 텍스트 필드임
      category_text as CategoryText
}
```

`ZRAP_R_PROJECT_###` 헤더 어노테이션에 추가:

```cds
@Consumption.valueHelpDefault.fetchValues: #ON_EXPLICIT_REQUEST   // ★ 추가
define root view entity ZRAP_R_PROJECT_###
```

`ZRAP_C_PROJECT_###` 에 추가/수정:

```cds
@Consumption.valueHelpDefault.fetchValues: #ON_EXPLICIT_REQUEST   // ★ 추가 (헤더)
define root view entity ZRAP_C_PROJECT_###
  provider contract transactional_query
  as projection on ZRAP_R_PROJECT_###
{
  // ...
      @Consumption.valueHelpDefinition: [{ entity: { name: 'ZRAP_I_PRJCAT_VH_###',
                                                     element: 'Category' } }]   // ★ 추가
      Category,
  // ...
}
```

`ZRAP_R_PROJECT_###` BDEF의 Project 블록에 추가:

```bdef
  field ( recommendations ) Category;                 // 이 필드에 추천값을 제공
  recommendation function GetRecommendedCategory;     // 추천값을 계산하는 함수

  side effects
  {
    recommendation function GetRecommendedCategory executed on field Title, field Description;   // 입력이 바뀌면 다시 계산
  }
```

왜 이렇게 쓰나
- 참조 샘플 `/DMO/R_TravelTP_REC` 가 `field ( recommendations ) Destination, Accommodation;` + `recommendation function GetRecommendedValuesFunction;` + `side effects { recommendation function ... executed on field Description, field Destination; }` 입니다. 릴리스 노트 설명: "추천은 값 도움말을 확장해 문맥에 맞는 제안을 주는 기능이며, BDEF에서 원천(source)·대상(target) 필드를 정하고, 함수는 side effect 안에 넣어야 하며, 추천값은 행동 풀에서 구현한다". 여기서 원천 = Title·Description, 대상 = Category 입니다.
- 추천값은 결국 **값 도움말의 값** 이어야 합니다. 그래서 대상 필드에 값 도움말을 걸었습니다(샘플도 Destination/Accommodation에 VH가 있음).
- `@Consumption.valueHelpDefault.fetchValues: #ON_EXPLICIT_REQUEST` 는 샘플의 R/C 헤더에 있는 어노테이션으로, 값 도움말 목록을 열자마자 전부 읽지 않고 사용자가 요청할 때 읽게 합니다(추천값이 먼저 눈에 띄게 하는 용도로 보임, 정확한 화면 효과는 실제 시스템에서 확인 필요). (→ 어노테이션 탭: @Consumption.valueHelpDefault.fetchValues)

</details>

#### 10단계. 추천 함수 구현과 확인 — 결정적 방식 vs AI(ISLM)

요구사항
1. `ZBP_RAP_R_PROJECT_###` 의 `lhc_project` 에 `GetRecommendedCategory` 를 구현하세요.
   - Title·Description을 읽어 소문자로 합친 문자열에서, 카테고리마다 키워드 일치 개수를 셉니다(카테고리 표는 **한 번만** SELECT).
   - 일치 개수 내림차순 상위 3개를 `value`(카테고리 코드), `score`(0~100), `suggested`(1위만 X)로 돌려줍니다.
2. 프로젝션 BDEF `ZRAP_C_PROJECT_###` 헤더에 `use side effects;` 와 `use recommendations;` 를 추가하세요.
3. 추천을 AI로 바꾸려면 무엇이 필요한지 정리하세요.

**확인**
- Preview → 새 프로젝트 → Title에 `SAP 클라우드 ERP 전환` 입력 → Category 값 도움말(또는 입력 필드)에 IT가 추천(1순위)으로 표시되어야 합니다. Title을 `브랜드 캠페인 출시` 로 바꾸면 MARKETING이 추천됩니다.
- 추천이 어떻게 보이는지(추천 구역, 기본 선택 여부)는 Fiori Elements 버전에 따라 다를 수 있습니다(실제 시스템에서 확인 필요).

<details><summary>정답·해설</summary>

`lhc_project` DEFINITION의 PRIVATE SECTION에 추가:

```abap
    TYPES: BEGIN OF ty_rec_value,
             value     TYPE string,
             score     TYPE int1,
             suggested TYPE abap_bool,
           END OF ty_rec_value,
           tt_rec_value TYPE STANDARD TABLE OF ty_rec_value WITH EMPTY KEY.

    TYPES: BEGIN OF ty_hit,
             category TYPE zrap_pcat_###-category,
             hits     TYPE i,
           END OF ty_hit,
           tt_hit TYPE STANDARD TABLE OF ty_hit WITH EMPTY KEY.

    CONSTANTS max_recommendations TYPE i VALUE 3.

    METHODS getrecommendedcategory FOR READ
      IMPORTING keys FOR FUNCTION Project~GetRecommendedCategory RESULT result.
```

IMPLEMENTATION에 추가:

```abap
  METHOD getrecommendedcategory.
    DATA hits       TYPE tt_hit.
    DATA rec_values TYPE tt_rec_value.

    READ ENTITIES OF zrap_r_project_### IN LOCAL MODE
      ENTITY Project
        FIELDS ( Title Description )
        WITH CORRESPONDING #( keys )
      RESULT DATA(projects)
      FAILED failed.

    IF projects IS INITIAL.
      RETURN.
    ENDIF.

    " 카테고리 마스터는 한 번만 읽음
    SELECT FROM zrap_pcat_### FIELDS category, keywords INTO TABLE @DATA(categories).

    LOOP AT projects ASSIGNING FIELD-SYMBOL(<project>).
      CLEAR: hits, rec_values.
      DATA(text) = to_lower( |{ <project>-Title } { <project>-Description }| ).

      LOOP AT categories INTO DATA(category).
        DATA(keywords) = to_lower( CONV string( category-keywords ) ).
        SPLIT keywords AT ',' INTO TABLE DATA(words).
        DATA(count) = 0.
        LOOP AT words INTO DATA(word).
          word = condense( word ).
          IF word IS NOT INITIAL AND find( val = text sub = word ) >= 0.
            count += 1.
          ENDIF.
        ENDLOOP.
        IF count > 0.
          APPEND VALUE #( category = category-category hits = count ) TO hits.
        ENDIF.
      ENDLOOP.

      SORT hits BY hits DESCENDING category ASCENDING.

      LOOP AT hits INTO DATA(hit) TO max_recommendations.
        APPEND VALUE #( value     = condense( CONV string( hit-category ) )
                        score     = nmin( val1 = 100 val2 = hit-hits * 30 )
                        suggested = xsdbool( sy-tabix = 1 ) ) TO rec_values.
      ENDLOOP.

      " %param-<엔터티 별칭>-<추천 필드> 에 추천 목록을 넣음 (샘플: %param-travel-destination)
      INSERT VALUE #( %tky          = <project>-%tky
                      %param-project = VALUE #( category = CORRESPONDING #( rec_values ) ) )
             INTO TABLE result.
    ENDLOOP.
  ENDMETHOD.
```

프로젝션 BDEF 헤더 최종본:

```bdef
projection;
strict ( 2 );
use collaborative draft;
use side effects;              // ★ 추가: R BDEF의 side effect를 UI에 노출
use recommendations;           // ★ 추가: 추천 기능을 UI에 노출
```

왜 이렇게 쓰나
- 시그니처 `FOR READ IMPORTING keys FOR FUNCTION Project~GetRecommendedCategory RESULT result` 와 결과 형태 `%param-<별칭> = VALUE #( <필드> = CORRESPONDING #( 추천표 ) )`, 추천표 구성 요소(`value`, `score`, `suggested`)는 샘플 `lhc_r_traveltp_rec~GetRecommendedValuesFunction` 과 같습니다. 파생 타입의 정확한 구성 요소는 ADT에서 `result` 위에 F2로 확인하세요(`CORRESPONDING` 이라 이름이 같은 것만 옮겨짐).
- 샘플은 첫 번째만 `suggested = abap_true`, score를 `100 - 순번` 으로 줍니다. 여기서는 일치 개수로 점수를 매겼습니다.
- `SELECT` 는 루프 밖에서 한 번만 합니다. 키 목록이 여러 개여도 DB 접근은 1회입니다.
- **결정적 방식 vs AI**: 샘플 README는 "목적지는 AI 기반, 숙소는 결정적 방식으로 추천"한다고 설명합니다. 샘플 AI 유틸 클래스 `/DMO/CL_AI_UTIL_REC` 는 `cl_aic_islm_compl_api_factory=>get( )->create_instance( 'MyIntelligentScen' )` 로 **ISLM(Intelligent Scenario Lifecycle Management)의 지능형 시나리오** 를 통해 생성형 AI completion API(`if_aic_completion_api->execute_for_string`)를 부르도록 되어 있습니다. 하지만 배포된 샘플 코드에서는 AI 호출 줄이 주석 처리되어 빈 목록을 돌려줍니다. 즉 **추천 기능 자체는 AI가 필요 없고 평범한 ABAP 구현으로 충분** 하며, AI를 쓰려면 ISLM 지능형 시나리오 설정과 AI 서비스 연결(Generative AI Hub 등)이 따로 필요합니다. 트라이얼에서 ISLM/AI 연결이 가능한지는 실제 시스템에서 확인하세요.
- 샘플 주석처럼 AI 결과는 **반드시 실제 값 목록으로 걸러야** 합니다(AI가 존재하지 않는 국가명을 낼 수 있어 `country_names` 로 필터). 추천값이 값 도움말에 없는 값이면 사용자가 고를 수 없습니다.

클래스 구조 해설
- `recommendation function GetRecommendedCategory` 줄이 `FOR READ ... FOR FUNCTION` 메서드를 만듭니다. 읽기 연산이므로 MODIFY를 하면 안 되고, `failed` 만 채울 수 있습니다.
- 언제 호출되나: side effect `executed on field Title, field Description` 때문에 사용자가 그 필드를 바꾸면 Fiori가 이 함수를 호출하고, 결과를 Category 필드의 추천으로 표시합니다.
- 이 BO는 collaborative draft와 recommendations를 함께 씁니다. 두 기능을 한 BO에 함께 쓴 예는 참조 자료에 없으므로, 활성화 오류가 나면 추천 부분을 별도 BO로 옮겨 시험하세요(실제 시스템에서 확인 필요).

</details>

## 출처

- SAP-samples, ABAP Flight Reference Scenario (branch ABAP-platform-cloud)
  - 확장 가능한 Agency BO와 확장 예제(cntry, slogn, rev, rev/a, rev/d, rev/e): https://github.com/SAP-samples/abap-platform-refscen-flight/tree/ABAP-platform-cloud/src/reuse/agency
  - Cross-BO(link/unlink/inverse function): https://github.com/SAP-samples/abap-platform-refscen-flight/tree/ABAP-platform-cloud/src/xbo
  - Collaborative draft: https://github.com/SAP-samples/abap-platform-refscen-flight/tree/ABAP-platform-cloud/src/colldraft
  - 계층(draft 편집 트리 / 읽기 전용): https://github.com/SAP-samples/abap-platform-refscen-flight/tree/ABAP-platform-cloud/src/hierarchy
  - Recommendations: https://github.com/SAP-samples/abap-platform-refscen-flight/tree/ABAP-platform-cloud/src/rec
  - README(패키지 설명, C0 릴리스와 provider contract 안내): https://github.com/SAP-samples/abap-platform-refscen-flight/blob/ABAP-platform-cloud/README.md
  - service_definition_agency: https://github.com/SAP-samples/abap-platform-refscen-flight/blob/ABAP-platform-cloud/service_definition_agency
- SAP-samples, ABAP Cheat Sheets
  - RAP Behavior Definition Language: https://github.com/SAP-samples/abap-cheat-sheets/blob/main/36_RAP_Behavior_Definition_Language.md
  - ABAP Release News (C0 DDIC 어노테이션, draft query 뷰, recommendations, collaborative draft, link/unlink/inverse, editable treeview, copy action): https://github.com/SAP-samples/abap-cheat-sheets/blob/main/33_ABAP_Release_News.md
- SAP-samples, ABAP Platform RAP Workshops — RAP610 (ABAP Cloud로 S/4HANA 확장, 개발자 확장성 배경): https://github.com/SAP-samples/abap-platform-rap-workshops/tree/main/rap6xx/rap610
