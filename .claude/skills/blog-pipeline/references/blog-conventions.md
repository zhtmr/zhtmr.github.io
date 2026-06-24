# zhtmr.github.io 블로그 컨벤션 (단일 진실 원천)

이 블로그는 **Jekyll + Minimal Mistakes 테마**(`air` 스킨, `locale: ko-KR`) 기반 한국어 기술 블로그다.
모든 에이전트·스킬이 이 파일을 컨벤션의 기준으로 삼는다. 컨벤션이 바뀌면 여기만 갱신한다.

## 목차
- [Frontmatter](#frontmatter)
- [제목·본문 구조](#제목본문-구조)
- [코드블록](#코드블록)
- [이미지](#이미지)
- [TOC](#toc)
- [카테고리 목록](#카테고리-목록)
- [파일명](#파일명)
- [커밋 메시지](#커밋-메시지)
- [빌드·배포](#빌드배포)

## Frontmatter
```yaml
---
published: true
layout: single
title: "[카테고리약어] 제목"      # 예: [JPA], [PS], [Github], [Spring]
excerpt: ""                       # 한 줄 요약 또는 빈 문자열. TIL은 "항해99 스터디" 등
categories:
  - JPA                           # 단일 카테고리 원칙. 아래 카테고리 목록 중 하나
tags:
  - ['JPA', 'TIL']                # 배열-in-배열 형식. 예: [ 'PS', '백트래킹', 'TIL' ]
use_math: true                    # 본문에 $...$ LaTeX 수식 있으면 true
---
```
- `_config.yml`의 `defaults`가 layout=single, author_profile, comments, share, related, toc_sticky, toc_label="목차"를 이미 부여하므로 frontmatter에는 위 핵심 필드만 둔다.
- `title`은 거의 항상 `"[카테고리] 제목"` 패턴. 검색·목록에서 분류가 한눈에 보이게 하는 관습.

## 제목·본문 구조
- 글 전체 제목은 frontmatter `title`이 담당. 본문 최상위 섹션 제목은 `##`부터 시작(일부 옛 글은 본문 첫 `#`에 제목을 반복하나, 신규 글은 `##`부터 권장).
- 글 첫머리에 그 포스트가 다루는 내용을 요약하는 `> 인용 블록`을 두는 관습.
- 제목 계층은 한 단계씩(`##` → `###`). 건너뛰지 않는다.

## 코드블록
- 항상 언어 태그를 단 펜스로: ` ```java `, ` ```yml `, ` ```bash `, ` ```sql `, ` ```json `, ` ```text ` 등.
- `_config.yml`: kramdown(GFM) + rouge, `block.line_numbers: true` — 코드블록에 줄번호가 자동 표시된다.
- 최근 코드블록에 **복사 버튼**이 추가됨(커밋 `코드 블록에 복사 버튼...`). 마크업은 표준 펜스 그대로 두면 되고, 버튼은 JS가 주입한다.
- **Liquid 충돌 주의**: 본문/코드에 `{{ ... }}` 또는 `{% ... %}`가 그대로 있으면 그 블록을 `{% raw %}` ~ `{% endraw %}`로 감싼다. 안 감싸면 Jekyll이 Liquid로 해석해 빌드가 깨지거나 내용이 사라진다. (GitHub Actions YAML 예제 등에서 빈번)

## 이미지
- **외부 호스팅 컨벤션**(최근 전환됨, 커밋 "이미지 경로 수정"): 별도 저장소 `static-files-for-posting`에 이미지를 두고 raw URL로 참조한다.
  ```markdown
  ![설명](https://zhtmr.github.io/static-files-for-posting/images/YYYYMMDD/<파일명>?raw=true)
  ```
  - 끝에 `?raw=true` 필수. 날짜 디렉토리(`YYYYMMDD`)로 정리.
  - 정렬: `{: .align-center}` 등 Minimal Mistakes 유틸 클래스 사용 가능 — `![..](url){: .align-center}`.
- 옛 글 일부는 `assets/images/...` 로컬 경로를 쓰지만, 신규 글은 외부 호스팅 방식을 따른다.
- 사용자가 파일명/로컬 경로만 줬다면 URL을 임의로 완성하지 말고 "이미지 경로 확정 필요"로 표시해 사용자에게 확인.

## TOC
- 기본 `toc: false`(`_config.yml` defaults). 섹션이 많아 목차가 유용하면 frontmatter에 `toc: true` 추가. `toc_sticky: true`, `toc_label: 목차`는 전역 설정.
- 특정 제목을 목차에서 제외: 제목 바로 아래 줄에 `{:.no_toc}`.

## 카테고리 목록
`_pages/category-*.md`에 정의된 카테고리(이 목록 밖 값을 categories에 쓰면 아카이브 페이지가 깨진다):
`JPA, algorithm, archive, aws, cs, database, designpattern, docker, effectivejava, git, github, java, javascript, project, ps, redis, spring, springboot, springsecurity, troubleshooting`
- 대소문자·표기는 실제 페이지 정의를 따른다. 새 카테고리가 필요하면 `_pages/category-<name>.md`도 함께 만들어야 한다.

## 파일명
- `_posts/YYYY-MM-DD-slug.md`. 날짜는 발행일 기준. slug은 영문 소문자-하이픈.
- TIL/시리즈는 관습적으로 접미사 사용: `-TIL`, `hanghae99-TIL-NN`.

## 커밋 메시지
- 한국어. 프리픽스 혼용: `post: <내용>`(글 추가/수정), `chore: <내용>`(설정·잡무), 또는 평문(`이미지 경로 수정`).
- 신규 발행: `post: <제목 요약>`. 수정 발행: `post: <내용> 수정`.
- 기존 커밋엔 Co-Authored-By 서명이 없다 — 사용자가 요청하지 않으면 서명을 붙이지 않는다.

## 빌드·배포
- `master` 푸시 → GitHub Pages 자동 빌드·배포. 별도 CI 발행 단계 없음.
- 로컬 미리보기: `bundle exec jekyll serve`(Gemfile 존재). Docker도 가능(`Dockerfile`).
- `master`에서 직접 작업하는 워크플로우(브랜치/PR 강제 아님). 단, 푸시는 항상 사용자 승인 후.
