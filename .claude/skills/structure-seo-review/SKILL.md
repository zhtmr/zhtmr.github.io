---
name: structure-seo-review
description: zhtmr.github.io 블로그 포스트의 구조·가독성과 SEO·메타데이터·링크·이미지 무결성을 검증하는 스킬. 제목 계층, TOC, 코드블록 포맷, frontmatter(categories/tags/excerpt/title 패턴), 이미지 경로·alt, 깨진 링크, Liquid raw 래핑을 번들 스크립트로 점검해 findings JSON으로 보고한다. "구조 검수", "메타데이터 확인", "frontmatter 점검", "이미지 깨졌는지", "링크 확인", "SEO 점검", "빌드 깨지는지" 같은 요청에 사용.
---

# structure-seo-review — 구조·가독성·SEO·무결성 검수

포스트의 두 층위를 검증한다: **구조·가독성**과 **SEO·메타데이터·무결성**. 결과는 `_workspace/02_review_seo.json`. 블로그 컨벤션은 `../blog-pipeline/references/blog-conventions.md` 참조.

## 핵심 원리: 존재 확인이 아니라 교차 검증
"이미지 태그가 있다"로 끝내지 않는다. **경계면을 맞춰본다** — 이미지 URL이 실제로 도달 가능한가? `categories` 값이 `_pages/category-*.md`에 정의된 카테고리와 일치하는가? `{{ }}`를 포함한 코드가 `{% raw %}`로 감싸졌는가? 이런 경계면 불일치가 깨진 이미지·빌드 실패의 실제 원인이다. 단순 존재 확인은 이런 버그를 못 잡는다.

## 반복 점검은 스크립트로
frontmatter 파싱, 카테고리 대조, 이미지/링크 추출, raw 래핑·언어 태그 검사는 손으로 세지 말고 번들 스크립트로 결정적으로 수행한다:

```bash
python .claude/skills/structure-seo-review/scripts/check_post.py \
    _workspace/01_structured.md --repo-root . [--check-urls]
```
- `--check-urls`: 이미지·외부 링크에 HTTP 요청을 보내 도달성까지 확인(네트워크 필요). 생략 시 형식·경로 정적 검사만.
- 출력 JSON의 `findings`를 그대로 검수 결과의 토대로 삼고, 스크립트가 못 잡는 판단형 항목(아래 체크리스트)을 사람이 보강한다.

## 구조·가독성 체크리스트 (판단형 — 사람이 본다)
- 제목 계층이 논리적인가(단계 건너뜀 없음, `##`→`###` 순서). 본문 최상위는 `##`.
- 문단이 지나치게 길어 스캔이 어렵지 않은가. 코드/명령이 인라인이 아니라 블록으로 분리됐는가.
- 코드블록마다 언어 태그가 있는가(스크립트가 잡아주지만 적절성은 사람이 확인 — 예: `bash`인데 `java`로 표기).
- TOC가 유용한 분량인데 `toc: false`인가, 혹은 짧은 글에 불필요하게 `toc: true`인가.
- 표/리스트가 적절히 쓰였는가(나열은 리스트, 비교는 표).

## SEO·메타데이터 체크리스트
- `title`이 `"[카테고리] 제목"` 패턴인가. 검색에서 의미가 드러나는 제목인가.
- `categories`가 기존 카테고리와 일치하는가(스크립트가 대조). 단일 카테고리 원칙.
- `tags`가 배열 형식이고 내용을 대표하는가.
- `excerpt`가 비어도 무방하나, 있으면 한 줄 요약으로 적절한가.
- 이미지 alt가 비어 있지 않은가(접근성·SEO). 이미지 URL이 `static-files-for-posting` 외부 호스팅 + `?raw=true` 컨벤션을 따르는가.

## 출력 스키마 (`_workspace/02_review_seo.json`)
```json
{
  "summary": "이미지 N/깨짐 M, 미정의 카테고리 X, 빌드 위험 Y건 — 한 줄 요약",
  "script_output": { "counts": { } },
  "findings": [
    {
      "id": "seo-1",
      "kind": "structure | frontmatter | image | link | seo",
      "severity": "high | med | low",
      "location": "섹션 / frontmatter 필드 / 라인",
      "problem": "무엇이 잘못됐나",
      "fix": "어떻게 고치나"
    }
  ]
}
```
- **high**: 빌드를 깨거나(raw 미래핑) 깨진 이미지·링크·미정의 카테고리. 즉시 강조.
- 도달성 확인이 불가하면 "검증 불가"로 표시하고 정적 검사 결과만 보고(단정 금지).
- frontmatter가 아직 잠정(post-structurer가 비워둠)이면 "publisher 확정 예정"과 진짜 오류를 구분.

## 재호출
publisher가 frontmatter를 확정한 뒤 재호출되면 frontmatter·이미지 항목만 재검증하고 나머지는 보존한다.
