---
name: post-publishing
description: 검수가 끝난 zhtmr.github.io 포스트를 발행하는 스킬. frontmatter(published/layout/title/excerpt/categories/tags/use_math)를 컨벤션대로 확정하고, YYYY-MM-DD-slug.md 파일명으로 _posts/에 배치한 뒤 한국어 커밋 메시지로 커밋하고 master에 푸시한다. "발행", "포스트 올려", "커밋하고 푸시", "배포", "글 게시" 같은 요청에 사용. 푸시는 외부 비가역 행동이므로 항상 최종 확인을 받는다.
---

# post-publishing — frontmatter 확정·파일 배치·커밋·푸시

수정 완료본(`_workspace/04_final.md`)을 실제 발행 가능한 포스트로 확정하고 master에 배포한다. 컨벤션 상세는 `../blog-pipeline/references/blog-conventions.md` 참조.

## 발행은 비가역이다 — 확인 우선
master 푸시는 GitHub Pages로 즉시 공개 배포된다. **푸시 직전 반드시** 최종 frontmatter + 파일명 + 커밋 메시지를 사용자에게 보여주고 명시적 승인을 받는다. 승인 없이 푸시하지 않는다. 파일 생성·로컬 커밋까지는 진행하되, 푸시만 게이트한다.

## 1. frontmatter 확정
`04_final.md`의 잠정 frontmatter를 컨벤션대로 완성한다:
```yaml
---
published: true
layout: single
title: "[카테고리] 제목"
excerpt: ""              # 한 줄 요약 또는 빈 문자열
categories:
  - JPA                  # 기존 카테고리 중 1개 (_pages/category-*.md)
tags:
  - ['JPA', 'TIL']       # 배열, 내용 대표 태그
use_math: false          # 수식(LaTeX) 사용 시 true
---
```
- **부족한 필드는 지어내지 않는다.** 카테고리/태그/제목이 불명확하면 사용자에게 질의한다. categories는 반드시 `_pages/category-*.md`에 존재하는 값으로.
- `use_math`: 본문에 `$...$` LaTeX 수식이 있으면 `true`.

## 2. 파일명·배치
- 파일명: `_posts/YYYY-MM-DD-slug.md`. 날짜는 **발행일 기준** — 지어내지 말고 실제 날짜를 확인한다(시스템/사용자). slug은 영문 소문자-하이픈, 내용을 대표하게(TIL은 관습적으로 `-TIL` 접미사 가능).
- 동일 `YYYY-MM-DD-slug.md`가 이미 있으면 덮어쓰지 말고 사용자에게 알린다(중복 발행 방지).

## 3. 커밋·푸시
- 저장소 커밋 컨벤션을 따른다: 신규 발행은 보통 `post: <제목 요약>`. 수정 발행은 `post: <내용> 수정`. 그 외 잡무는 `chore: ...`. 평문 한국어도 기존에 혼용됨.
- 이 블로그는 `master`에서 직접 작업하는 워크플로우다. 별도 지시가 없으면 master에 커밋 후, **승인 후** master에 푸시한다.
- 커밋만 하고 푸시는 별도 확인 — 사용자가 "커밋만"이라 하면 푸시하지 않는다.

```bash
git add _posts/YYYY-MM-DD-slug.md
git commit -m "post: <제목 요약>"
# 사용자 승인 후:
git push origin master
```

## 에러 핸들링
- 푸시 실패(인증/충돌/네트워크): 1회 재시도 → 재실패 시 **로컬 커밋은 보존**한 채 중단하고 원인을 보고한다. `--force`·히스토리 변경 금지.
- 커밋 메시지 끝에 임의의 서명/Co-Authored-By를 붙이지 않는다(사용자가 요청하지 않는 한 — 이 저장소 기존 커밋엔 서명이 없다).

## 수정 발행(재호출)
이미 발행된 글의 수정이면 새 파일을 만들지 말고 기존 `_posts/` 파일을 찾아 수정하고 `post: <내용> 수정`으로 커밋한다.
