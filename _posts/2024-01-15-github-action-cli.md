---
published: true
layout: single
title:  "[Github Action] github CLI 로 github action 트리거 하기"
excerpt: ""
categories:
  - Github
tags:
  - ['Git','Github']
use_math: true
---

# 기존 workflow 
```yaml
# blogposts.yml

name: Blog post workflow
on:
  push:
    branches:
      - main
  schedule:
    # Runs every day at
    - cron: '0 1 * * *'

jobs:
  pull_blog_rss:
    name: Update with latest blog posts
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Get RSS Feed
        uses: kohrongying/readme-the-rss@master
        with:
          feed_url: https://zhtmr.github.io/feed.xml
          count: 6 # default 5
      - name: Commit file changes
        run: |
          git config --global user.name 'username'
          git config --global user.email 'uesremail'
          git add .
          git diff --quiet --cached || git commit -m "[auto] $(date -u +"%Y-%m-%d-%r") Blog Posting List Update"    
      - name: Push changes
        uses: ad-m/github-push-action@master
        with:
          github_token: ${{ secrets.GH_TOKEN }}
```
기존 블로그 포스트 github action 은 cron job 으로 매일 아침 10시에 RSS 긁어와서 기존 커밋 내역과 비교 후 달라진 내용(추가된 게시글 있는 경우)이 있을 경우 git commit 된다.
# workflow 파일 설정
```yaml
on:
  push:
    branches:
      - main
  schedule:
    # Runs every day at
    - cron: '0 1 * * *'
  workflow_dispatch:     # workflow를 수동으로 trigger 할 수 있는 옵션 추가
```
trigger 조건에 `workflow_dispatch`를 추가해 준다.

# Github CLI 설치
로컬 터미널에서 workflow 를 실행시키기 위해 github cli 를 설치한다.
```shell
brew install gh	
```

# cli 로 workflow 트리거하기
```shell
# `blogposts.yml` workflow 를 `master` 브랜치에서 실행 시킨다.
gh workflow run blogposts --ref master
```

>🫨 `blogposts` 처럼 yml 파일 명으로 못찾는 경우 `gh workflow list` 치면 나오는 ID 값을 넣어준다. [참고](https://github.com/cli/cli/issues/6328)



# gh login
실행 중에 아래와 같은 로그인 요청 시 `gh auth login` 입력 한다.
```shell
To get started with GitHub CLI, please run:  gh auth login
Alternatively, populate the GH_TOKEN environment variable with a GitHub API authentication token.
```
차례대로 `GitHub.com`, `HTTPS`, `Y`, `Login with a web browser` 를 선택 후 브라우저에 one-time code 를 붙여 넣는다.
![img_1.png](https://zhtmr.github.io/static-files-for-posting/20240115/gh-cli.png?raw=true){: .align-center}

# npm script 이용
매번 일일이 `gh workflow run blogposts --ref master` 치는게 귀찮으므로 `npm init`으로 package.json 파일 만든 후 `script` 태그 안에 넣어주자.
```json
{
  "name": "zhtmr",
  "version": "1.0.0",
  "description": "",
  "main": "index.js",
  "scripts": {
    "test": "echo \"Error: no test specified\" && exit 1",
    "deploy": "gh workflow run ID값 --ref master"
  },
  "author": "",
  "license": "ISC"
}
```
npm run deploy 로 실행하면 github action 동작한다.
```shell
npm run deploy
```







## reference
{% capture notice-2 %}
- [https://fe-developers.kakaoent.com/2022/220929-workflow-dispatch-with-inquirer-js/](https://fe-developers.kakaoent.com/2022/220929-workflow-dispatch-with-inquirer-js/)
- [https://github.com/cli/cli/issues/6328](https://github.com/cli/cli/issues/6328)
{% endcapture %}

<div class="notice">{{ notice-2 | markdownify }}</div>


