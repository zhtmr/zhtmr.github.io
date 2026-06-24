---
name: blog-pipeline
description: zhtmr.github.io 블로그 글을 초안 → 구조화 → 검수(기술·문체·구조/SEO) → 발행(커밋·푸시)까지 한 번에 처리하는 오케스트레이터 스킬. 사용자가 직접 쓴 초안/메모를 받아 포스트로 다듬고, 4축으로 검수하고, master에 발행한다. 트리거 — "블로그 글 써줘", "포스트 발행", "이 초안 올려줘", "글 검수하고 게시", "TIL 정리해서 올려", "블로그 파이프라인". 후속 작업 — "다시 검수", "재실행", "기술 검수만 다시", "문체만 다시", "이 문단 수정해서 다시 올려", "발행 전 단계로", "이전 결과 기반으로 보완", "방금 글 수정 발행"도 모두 이 스킬. 단순 오탈자 교정·번역·새 글 처음부터 집필이 아니라, 초안 기반 구조화+검수+발행이 목적일 때 사용.
---

# blog-pipeline — 글 작성·검수·발행 풀 파이프라인 오케스트레이터

사용자가 **직접 쓴 초안/메모**를 받아, 구조화 → 4축 검수 → 발행까지 조율한다. 개별 작업의 "어떻게"는 각 전문 스킬에, 이 오케스트레이터는 "누가 언제 어떤 순서로"를 담는다.

## 실행 모드: 하이브리드 (서브 에이전트 중심)
검수는 **독립 산출물(findings)을 병렬 생성**하는 팬아웃/팬인이라 팀 통신 오버헤드가 이득보다 크다. 따라서 서브 에이전트(`Agent` 도구)로 구성한다. (에이전트 팀도 검토했으나, 리뷰어들이 서로 합의할 필요 없이 각자 findings만 내고 취합은 리더가 하므로 서브 에이전트가 적합.) Phase별 모드는 각 섹션 상단에 명시한다. **모든 `Agent` 호출은 `model: "opus"`.**

```
[리더 = blog-pipeline 따르는 메인]
  Phase 0  컨텍스트 확인 (초기/새/부분 재실행)
  Phase 1  구조화        ── post-structurer (서브, 1)
  Phase 2  검수 팬아웃   ── tech / style / structure-seo-reviewer (서브, 병렬 3) → 팬인 취합
  Phase 3  수정 반영     ── post-structurer 재호출 (서브, 1)  [확정 findings만]
  Phase 4  발행          ── publisher (서브, 1) [푸시 전 사용자 승인]
  Phase 5  피드백 수집 (하네스 진화)
```

데이터는 작업 디렉토리 하위 `_workspace/`에 파일로 주고받는다. 파일명: `{단계}_{산출물}`.

---

## Phase 0: 컨텍스트 확인
**실행 모드:** 리더 직접 (에이전트 없음)

`_workspace/` 존재 여부와 사용자 요청을 보고 실행 모드를 정한다:
- `_workspace/` 없음 → **초기 실행**. `_workspace/` 생성, 사용자 초안을 `_workspace/00_input.md`로 저장(파일이면 복사, 붙여넣기면 기록). Phase 1부터.
- `_workspace/` 있음 + 사용자가 **새 글** 제공 → 기존 `_workspace/`를 `_workspace_prev/`로 옮기고 새로 시작.
- `_workspace/` 있음 + **부분 수정 요청**(예: "기술 검수만 다시", "이 문단만") → **부분 재실행**: 해당 Phase/에이전트만 재호출하고 나머지 산출물은 보존.
- `_posts/`의 기존 글 **수정 발행** 요청 → 그 파일을 `_workspace/00_input.md`로 불러와 시작, publisher는 새 파일 대신 원본을 수정.

`_workspace/`는 `.gitignore`에 등록돼 있어 커밋되지 않는다(중간 산출물은 감사·재실행용으로 보존).

---

## Phase 1: 구조화
**실행 모드:** 서브 에이전트 1 (`post-structurer`)

거친 초안을 구조화된 포스트 본문으로 다듬는다. **의미 불변** — 내용을 더하거나 빼지 않는다.

```
Agent(subagent_type="post-structurer", model="opus",
  prompt="_workspace/00_input.md 를 post-structuring 스킬에 따라 구조화하라.
          결과를 _workspace/01_structured.md 로 저장. 의미는 보존하고 구조·포맷만.
          확인 필요한 모호점은 <!-- STRUCTURE-NOTES --> 에 남겨라.")
```
산출물 `01_structured.md`의 `<!-- STRUCTURE-NOTES -->`에 사용자 확인이 필요한 의미상 모호점이 있으면, Phase 2로 넘어가기 전에 사용자에게 먼저 확인한다(잘못된 토대 위에서 검수하면 낭비).

---

## Phase 2: 검수 (팬아웃 → 팬인)
**실행 모드:** 서브 에이전트 3 병렬 → 리더 취합

세 리뷰어를 **한 메시지에서 동시에** 호출해 병렬 실행한다(독립 작업). 각자 findings JSON을 `_workspace/`에 쓴다.

```
# 한 메시지에 3개 Agent 호출 (병렬)
Agent(subagent_type="tech-reviewer", model="opus",
  prompt="_workspace/01_structured.md 를 tech-review 스킬로 검수. → _workspace/02_review_tech.json")
Agent(subagent_type="style-reviewer", model="opus",
  prompt="_workspace/01_structured.md 를 korean-style-review 스킬로 검수. → _workspace/02_review_style.json")
Agent(subagent_type="structure-seo-reviewer", model="opus",
  prompt="_workspace/01_structured.md 를 structure-seo-review 스킬(번들 스크립트 포함)로 검수.
          → _workspace/02_review_seo.json")
```

**팬인 — 리더가 취합한다:**
1. 세 findings JSON을 읽어 하나의 검수 리포트로 통합한다.
2. **중복·상충 정리**: 같은 구간을 여러 리뷰어가 지적하면 묶고, 상충하면(예: 문체 수정안이 기술 정확성과 충돌) **삭제하지 말고 양쪽 출처를 병기**해 사용자가 판단하게 한다.
3. severity 순으로 정렬해 사용자에게 제시한다. high(빌드 깨짐·사실 오류) 먼저.
4. 사용자에게 어떤 findings를 적용할지 확인받아 `_workspace/03_decisions.md`로 확정한다. (findings 0건이면 "검수 통과"로 바로 Phase 4 제안.)

---

## Phase 3: 수정 반영
**실행 모드:** 서브 에이전트 1 (`post-structurer` 재호출)

확정된 수정만 본문에 반영한다(미확정은 손대지 않음 — 병렬 편집 충돌 방지).

```
Agent(subagent_type="post-structurer", model="opus",
  prompt="_workspace/01_structured.md 에 _workspace/03_decisions.md 의 확정 수정을 반영하라.
          관련 findings: _workspace/02_review_*.json. 결과를 _workspace/04_final.md 로 저장.
          의미를 바꿀 위험이 있는 수정은 적용하지 말고 NOTES에 남겨라.")
```
수정이 본문 의미에 영향을 줄 만큼 컸다면, 영향받은 항목만 재검수(Phase 2 부분 재실행)를 제안한다. 사소한 표현 수정이면 생략.

---

## Phase 4: 발행
**실행 모드:** 서브 에이전트 1 (`publisher`) — 푸시 전 사용자 승인 게이트

```
Agent(subagent_type="publisher", model="opus",
  prompt="_workspace/04_final.md 를 post-publishing 스킬로 발행하라.
          frontmatter 확정 → _posts/YYYY-MM-DD-slug.md 배치 → 커밋.
          푸시 전 최종 frontmatter·파일명·커밋 메시지를 사용자에게 보여주고 승인을 받아라.")
```
- 발행일·카테고리·태그가 불명확하면 publisher가 사용자에게 질의한다(지어내지 않음).
- **푸시는 비가역**: publisher가 제시한 최종안을 사용자가 승인한 뒤에만 `git push origin master`. 사용자가 "커밋만"이면 푸시 생략.

---

## Phase 5: 피드백 수집 (하네스 진화)
발행 후 한 번 묻는다: "결과나 파이프라인에서 바꾸고 싶은 점이 있나요?" 피드백이 있으면 유형별로 반영하고 **프로젝트 루트의 `CLAUDE.md`** 변경 이력 테이블에 기록한다:
- 결과물 품질 → 해당 스킬 수정 / 에이전트 역할 → 에이전트 `.md` / 순서 → 이 오케스트레이터 / 트리거 누락 → description 확장.
없으면 강요하지 않고 종료.

---

## 에이전트 디스패치 원칙 (미스파이어 대비)
서브에이전트 첫 디스패치에서 간헐적으로 **미스파이어**가 발생할 수 있다: `tool_uses=0`으로 아무 도구도 쓰지 않고 엉뚱한 텍스트(스킬 설명·일반 지시문 등)만 반환하는 현상. 이를 방지·복구하려면:
- **프롬프트를 자기완결적으로 준다.** "Skill 도구로 불러"에만 의존하지 말고, 에이전트가 **Read할 정확한 파일 절대경로**(입력 + 해당 SKILL.md)와 **Write할 출력 절대경로**를 명시하고, "반드시 도구로 파일을 읽고 써라. 설명만 반환하면 실패다"를 못박는다. (이 패턴이 미스파이어를 크게 줄인다.)
- **완료를 산출물로 검증한다.** 에이전트 반환 메시지를 믿지 말고, 기대 출력 파일이 실제로 생성됐는지 리더가 직접 확인한다(Glob/Read). `tool_uses=0`이거나 파일이 없으면 실패로 간주.

## 에러 핸들링
- **에이전트 미스파이어/실패**: 위 기준으로 실패 판정 시 **1회 자동 재시도**(자기완결 프롬프트로). 재실패 시 그 산출물 없이 진행하되 최종 보고에 "검수 N축 누락"을 명시한다(특히 검수 한 축이 빠지면 사용자에게 명확히 알린다).
- **API 529/일시 과부하**: 서버측 일시 장애다. 에이전트가 529로 죽었어도 **기대 출력 파일이 이미 생성됐는지 먼저 확인**한다 — 작업은 끝내고 최종 보고만 유실됐을 수 있다(이 경우 재시도 불필요). 파일이 없으면 잠시 후 재시도.
- **상충 findings**: 삭제하지 않고 출처 병기 후 사용자 판단(Phase 2-2).
- **빌드 위험(high, raw 미래핑·미정의 카테고리)**: 발행을 막고 먼저 해결한다 — 깨진 채 master에 푸시되면 사이트 전체 빌드가 실패할 수 있다.
- **푸시 실패**: 로컬 커밋 보존한 채 중단, 원인 보고. `--force`·히스토리 변경 금지.
- **의미 변형 위험**: 구조화/문체 수정이 내용을 바꿀 듯하면 적용 보류 후 사용자 확인.

## 데이터 흐름 요약
| 파일 | 생성자 | 소비자 |
|------|--------|--------|
| `_workspace/00_input.md` | 리더(Phase 0) | post-structurer |
| `_workspace/01_structured.md` | post-structurer | 리뷰어 3종 |
| `_workspace/02_review_{tech,style,seo}.json` | 리뷰어 3종 | 리더(팬인) |
| `_workspace/03_decisions.md` | 리더+사용자 | post-structurer |
| `_workspace/04_final.md` | post-structurer | publisher |
| `_posts/YYYY-MM-DD-slug.md` | publisher | (발행물) |

## 테스트 시나리오
**정상 흐름:** "이 초안 검수해서 올려줘" + Spring 초안 →
Phase 0 초기 실행 → Phase 1 구조화(NOTES 없음) → Phase 2 병렬 검수(tech 1건, style 2건, seo 0건) →
리더 취합·사용자 확정(3건 모두 적용) → Phase 3 반영 → Phase 4 publisher가 frontmatter 확정·커밋·승인 후 푸시 → Phase 5 피드백 1회.
기대: `_posts/`에 컨벤션 맞는 파일 1개, master 푸시 완료, `_workspace/`에 전 단계 산출물 보존.

**에러 흐름:** 검수 중 `style-reviewer`가 실패 →
1회 재시도 → 재실패 시 tech·seo findings만으로 취합하고 "문체 검수 누락"을 사용자에게 명시 →
사용자가 그대로 진행 선택 시 Phase 3~4 계속, 최종 보고에 누락 기록.
seo-reviewer가 `{% raw %}` 미래핑(high) 발견 시 → 발행 차단, Phase 3에서 먼저 수정 후 재검증.
