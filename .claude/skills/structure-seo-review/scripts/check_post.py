#!/usr/bin/env python3
"""
check_post.py — zhtmr.github.io 포스트 정적 점검기.

frontmatter / 카테고리 정합성 / 이미지 / 링크 / Liquid raw 래핑을 결정적으로 검사해
JSON으로 출력한다. structure-seo-reviewer 에이전트가 호출한다. 표준 라이브러리만 사용.

사용법:
  python check_post.py <post.md> [--repo-root <dir>] [--check-urls]

--check-urls 를 주면 이미지/외부 링크에 HTTP HEAD 를 보내 도달성까지 확인한다(네트워크 필요).
없으면 형식·경로 정적 검사만 수행한다.
"""
import sys, os, re, json, glob, argparse

def split_frontmatter(text):
    """('---\\n...\\n---' 블록, 본문) 반환. frontmatter 없으면 (None, text)."""
    if not text.startswith('---'):
        return None, text
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n?(.*)$', text, re.DOTALL)
    if not m:
        return None, text
    return m.group(1), m.group(2)

def parse_simple_yaml(fm):
    """frontmatter 의 최상위 key 와 categories 목록을 느슨하게 추출(YAML 파서 없이)."""
    keys = {}
    categories = []
    in_cats = False
    for line in fm.splitlines():
        if re.match(r'^categories\s*:', line):
            in_cats = True
            inline = line.split(':', 1)[1].strip()
            if inline and inline not in ('', '[]'):
                categories += [c.strip().strip("'\"[]") for c in inline.strip('[]').split(',') if c.strip()]
            continue
        if in_cats:
            mm = re.match(r'^\s*-\s*(.+)$', line)
            if mm:
                categories.append(mm.group(1).strip().strip("'\""))
                continue
            else:
                in_cats = False
        m = re.match(r'^([A-Za-z_]+)\s*:\s*(.*)$', line)
        if m:
            keys[m.group(1)] = m.group(2).strip()
    return keys, [c for c in categories if c]

def known_categories(repo_root):
    cats = set()
    for p in glob.glob(os.path.join(repo_root, '_pages', 'category-*.md')):
        name = os.path.basename(p)[len('category-'):-len('.md')]
        cats.add(name.lower())
    return cats

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('post')
    ap.add_argument('--repo-root', default='.')
    ap.add_argument('--check-urls', action='store_true')
    args = ap.parse_args()

    findings = []
    def add(kind, severity, location, problem, fix):
        findings.append({"kind": kind, "severity": severity,
                         "location": location, "problem": problem, "fix": fix})

    with open(args.post, encoding='utf-8') as f:
        text = f.read()

    fm, body = split_frontmatter(text)
    if fm is None:
        add("frontmatter", "high", "파일 최상단", "frontmatter(--- 블록)가 없다.",
            "published/layout/title/categories/tags/use_math 를 포함한 frontmatter 추가")
        keys, cats = {}, []
    else:
        keys, cats = parse_simple_yaml(fm)
        for req in ("layout", "title"):
            if req not in keys or not keys[req]:
                add("frontmatter", "high", "frontmatter", f"필수 필드 '{req}' 누락/빈값.",
                    f"{req} 값을 컨벤션대로 채우기")
        if "title" in keys and not re.search(r'^\s*["\']?\[.+\]', keys["title"]):
            add("seo", "low", "frontmatter.title",
                "title 이 \"[카테고리] 제목\" 패턴이 아님.",
                '예: title: "[JPA] ..." 형태 권장')
        # 카테고리 정합성
        known = known_categories(args.repo_root)
        for c in cats:
            if known and c.lower() not in known:
                add("frontmatter", "high", "frontmatter.categories",
                    f"categories '{c}' 가 _pages/category-*.md 에 정의되지 않음.",
                    f"기존 카테고리 중 선택하거나 _pages/category-{c.lower()}.md 생성")
        if not cats:
            add("frontmatter", "med", "frontmatter.categories",
                "categories 가 비어 있음.", "대표 카테고리 1개 지정")

    # Liquid raw 래핑 검사: {{ }} / {% %} 가 raw 블록 밖에 있는지
    raw_spans = [(m.start(), m.end()) for m in re.finditer(
        r'\{%\s*raw\s*%\}.*?\{%\s*endraw\s*%\}', body, re.DOTALL)]
    def in_raw(pos):
        return any(s <= pos < e for s, e in raw_spans)
    for m in re.finditer(r'\{\{.*?\}\}|\{%(?!\s*(?:raw|endraw)\s*%\}).*?%\}', body, re.DOTALL):
        if not in_raw(m.start()):
            ln = body[:m.start()].count('\n') + 1
            add("structure", "high", f"본문 line~{ln}",
                f"raw 블록 밖에 Liquid 구문이 노출됨: {m.group(0)[:40]!r}",
                "{% raw %} ... {% endraw %} 로 감싸 빌드 깨짐 방지")

    # 코드블록 언어 태그 검사 — 펜스를 열기/닫기로 번갈아 보고, '여는' 펜스만 검사한다
    # (닫는 펜스 ``` 는 언어 태그가 없는 게 정상이므로 오탐하지 않도록).
    opening = True
    for m in re.finditer(r'^```(\w*)\s*$', body, re.MULTILINE):
        if opening and m.group(1) == '':
            ln = body[:m.start()].count('\n') + 1
            add("structure", "low", f"본문 line~{ln}",
                "코드블록에 언어 태그가 없음.", "```java / ```bash 등 언어 명시")
        opening = not opening

    # 이미지 추출
    images = re.findall(r'!\[[^\]]*\]\(([^)\s]+)', body)
    for img in images:
        if img.startswith('http') and 'raw=true' not in img and 'static-files-for-posting' in img:
            add("image", "med", img,
                "static-files-for-posting 이미지에 ?raw=true 누락 가능.",
                "원본 이미지 URL 끝에 ?raw=true 확인")
    # alt 없는 이미지
    for m in re.finditer(r'!\[\s*\]\(', body):
        ln = body[:m.start()].count('\n') + 1
        add("seo", "low", f"본문 line~{ln}", "이미지 alt 텍스트가 비어 있음.",
            "![설명](url) 로 alt 추가(접근성·SEO)")

    # 링크 추출(이미지 제외)
    links = [u for u in re.findall(r'(?<!\!)\[[^\]]+\]\(([^)\s]+)\)', body)
             if u.startswith('http')]

    result = {
        "post": args.post,
        "frontmatter_keys": list(keys.keys()),
        "categories": cats,
        "counts": {"images": len(images), "links": len(links),
                   "raw_blocks": len(raw_spans), "findings": len(findings)},
    }

    if args.check_urls:
        import urllib.request
        def reachable(url):
            try:
                req = urllib.request.Request(url, method='HEAD',
                        headers={'User-Agent': 'post-checker'})
                with urllib.request.urlopen(req, timeout=10) as r:
                    return 200 <= r.status < 400
            except Exception:
                # HEAD 거부 서버 대비 GET 재시도
                try:
                    req = urllib.request.Request(url, headers={'User-Agent': 'post-checker'})
                    with urllib.request.urlopen(req, timeout=10) as r:
                        return 200 <= r.status < 400
                except Exception:
                    return False
        for url in images + links:
            if url.startswith('http') and not reachable(url):
                add("link" if url in links else "image", "high", url,
                    "URL 도달 실패(깨진 이미지/링크 가능).", "URL 확인·수정")
        result["counts"]["findings"] = len(findings)

    result["findings"] = findings
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
