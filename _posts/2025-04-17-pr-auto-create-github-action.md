---
published: true
layout: single
title: "[Github Action] PR(Pull Request) 생성 및 병합 자동화 하기"
excerpt: ""
categories:
  - Github
tags:
  - ['Github']
use_math: false
---


> Github Action 을 이용해 Pull Request 를 자동으로 생성하고 auto-merge 하는 방법과 적용하면서 겪었던 오류 상황과 해결방법을 다룹니다.



## PR 생성의 귀찮음..
github flow 를 이용해 개발하게 되면 Pull Request 생성이 필수다. 문제는 로컬에서 push 를 한 후, github 에 접속해 PR 을 직접 생성해야 한다는 것이다.

물론, 이 과정에서 작업 내용을 작성하면서 한번 더 점검할 수도 있어 수동으로 직접 만드는 것도 의미가 있다고 생각하지만, 간단한 스터디 용으로 사용하는 경우엔 일일이 수동으로 만드는 과정 자체가 단순 반복적인 과정으로 느껴졌다.

## PR 을 자동으로 생성하는 Action
역시나.. 이미 Github Action marketplace 에는 PR 을 자동으로 생성해주는 workflow 가 오래전부터 사용되고 있었다.
![](https://zhtmr.github.io/static-files-for-posting/20250417/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202025-04-17%20%EC%98%A4%ED%9B%84%202.29.42.png?raw=true)

그 중 star 수가 가장 많고, Github staff 가 직접 만든 [Crate Pull Request](https://github.com/marketplace/actions/create-pull-request) 를 사용해보기로 했다.
![](https://zhtmr.github.io/static-files-for-posting/20250417/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202025-04-17%20%EC%98%A4%ED%9B%84%202.38.19.png?raw=true)

기본적인 작성법은 다음과 같다. 여기에 옵션으로 branch, base, title, body, labels, assignees, reviewers 등을 추가할 수 있도록 지원하고 있다.
- branch: pr 시 작업 브랜치 (feature 브랜치 등)
- base: 소스를 통합할 브랜치 (main 브랜치 등)
- title: PR 의 제목
- body: PR 의 내용
- labels: PR 라벨
- assignees: PR 을 작성한 사람
- reviewers: PR 리뷰할 사람


```yml
- uses: actions/checkout@v4

# Make changes to pull request here

- name: Create Pull Request
  uses: peter-evans/create-pull-request@v7
```

다른 블로그나 workflow 가이드를 봐도 굉장히 사용법이 굉장히 간단해 보인다. 바로 프로젝트에 적용해 봤다.

## 문제
title 은 단순히 작업 브랜치에서 main 브랜치로 푸시한다는 것을 표시하고, body 의 내용으로는 브랜치 푸시 상태와 커밋 메시지를 그대로 출력하고 싶었다.
assignees 의 경우 로컬에서 push 한 사람의 github 계정이 찍혀야 하기 때문에 {% raw %}`${{ github.actor }}`{% endraw %} 로 작성하고, reviewers 는 팀원 전체가 선택되어야 하므로 github var 에 직접 REVIEWERS 라는 이름으로 인원수에 맞게 `,` 로 구분해 등록했다.
![](https://zhtmr.github.io/static-files-for-posting/20250417/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202025-04-17%20%EC%98%A4%ED%9B%84%202.55.01.png?raw=true)

{% raw %}
```yml

name: Auto PR and Merge

on:
  push:
    branches:
      - 'sw**'
      - 'cm**'

jobs:
  create-pull-request:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Create Pull Request
        id: cpr
        uses: peter-evans/create-pull-request@v7
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          base: main
          branch: ${{ github.ref_name }}
          title: "[auto] ${{github.ref_name}} → main"
          body: |
            - 자동 PR: `${{ github.ref_name }} → main`
            - 커밋 메시지: `${{ github.event.head_commit.message }}`
          labels: auto-merge
          assignees: ${{ github.actor }}
          reviewers: ${{ vars.REVIEWERS }}
          draft: false
```
{% endraw %}

이대로 만들고 로컬에서 push 하면 github 에 자동으로 PR 이 생성될 줄 알았는데, 자동으로 생성되지도 않을 뿐더러 수동으로 생성해도 아무런 변경사항이 없어 main 브랜치에 병합을 할 수 없는 상황이었다. 


### actions setting 문제
찾아보니 github action 권한 문제일 수 있다고 나와서 설정을 다시 해줬다.
`Repository` > `Settings` > `Actions` > `General` 로 들어가게 되면 맨 아래 부분에 `Workflow permissions` 부분이 있다. 

`Read and Write` 권한을 체크하고, 아래에 Github Actions 가 PR 을 만들 수 있는 권한도 체크한다.
![](https://zhtmr.github.io/static-files-for-posting/20250417/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202025-04-17%20%EC%98%A4%ED%9B%84%203.04.53.png?raw=true)

### 잘못된 branch 옵션 사용
이번엔 action 은 작동하지만 여전히 PR 자동 생성은 되지 않았다.
workflow 로그 내역을 보니 계속 main 과 feature 브랜치가 변경사항이 없어 병합이 안된다고 나왔다. 분명 로컬에서는 작업한 내용이 있고, 이를 push 했음에도 불구하고 변경사항이 없다고 하니 도저히 원인을 찾을 수가 없었다.

```sql
fatal: remotes/origin/main...remotes/origin/sw-test4: no merge base

[INFO] Both branches are the same. No action needed.
```
굉장히 많은 시도와 수정을 거듭했지만 여전히 PR 이 생성되지 않았다.. 결국 개발자에게 직접 이슈를 남겨 물어보기로 했다. issues 에 들어가보니 뭔가 비슷한 상황을 겪고있는 개발자들이 꽤 있는것 처럼 보여서 먼저 해당 글들을 확인해 봤다.
뭔가 branch 설정에 대한 이슈 같았다. 나도 내 문제를 [이슈](https://github.com/peter-evans/create-pull-request/issues/3912)로 남겨보기로 했다. 

다행히 답변이 하루만에 도착해 확인해봤다.
![](https://zhtmr.github.io/static-files-for-posting/20250417/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202025-04-17%20%EC%98%A4%ED%9B%84%203.24.56.png?raw=true)
역시 `branch` 옵션의 사용 방법이 잘못되었다. `github.ref_name` 으로 사용하게 될 경우 branch 의 이름을 가져오게 된다. 
예를 들어 로컬에서 `sw-test` 라는 브랜치 명으로 push 하게 되면 `sw-test` 라는 값이 저 변수 대신 들어가게 된다. 

다른 블로그 글이나 [Crate Pull Request](https://github.com/marketplace/actions/create-pull-request) action 메뉴얼을 봐도 브랜치 명을 직접 명시해서 사용하는 것으로 나와 있어, 그냥 브랜치 명만 적으면 되는 줄 알았다. 저게 문제가 될 것 이라는 생각은 전혀 하지 못했다.

아마 workflow 가 동작하면서 내부적으로 github 액션을 트리거 한 *branch 의 전체 경로*를 필요로 하는 것 같았다. GPT 에 물어보니 `github.event.ref` 방식으로 전체 경로를 가져올 수 있다고 해서 해당 방법으로 다시 작성해 봤다.

{% raw %}
```yml
jobs:
  auto-pr:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Code
        uses: actions/checkout@v3

      - name: Create Pull Request to main
        id: create_pr
        uses: peter-evans/create-pull-request@v7
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          base: main
          branch: ${{ github.event.ref }}  # refs/heads/sw-test
          title: "[auto] ${{ github.event.head_commit.message }}"
          body: |
            자동 PR 생성: `${{ github.ref_name }} → main`
            커밋 메시지: `${{ github.event.head_commit.message }}`
          labels: auto-merge
          assignees: ${{ github.actor }}
          reviewers: ${{ vars.REVIEWERS }}
          draft: false
```
{% endraw %}

### github token 문제
이번엔 드디어 자동으로 PR 이 생성되었다! 
![](https://zhtmr.github.io/static-files-for-posting/20250417/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202025-04-17%20%EC%98%A4%ED%9B%84%203.44.16.png?raw=true)

그러나 이번에는 GitHub Actions Bot이 PR을 생성하면서, 코드를 push한 작성자조차도 스스로 approve(승인)할 수 있는 상황이 발생하게 되었다. 
현재 branch protection rule 에 1명이 승인할 경우 merge 할 수 있도록 설정이 되어 있어, 이렇게 될 경우 의도와 다르게 상대방의 코드 리뷰 없이 코드 작성자가 스스로 병합하게 되는 상황이 발생할 수 있다.
혼자서 작업하는 저장소의 경우에는 신경쓰지 않아도 되지만, 공동 작업하는 경우에는 중요한 문제가 될 수 있다.

위 token 옵션에 `secrets.GITHUB_TOKEN` 를 사용하게 되면 개발자는 따로 secrets 에 정의할 필요없이 github 이 내부적으로 토큰을 만들어 사용하게 되며, PR 생성의 주체는 Bot 으로 동작하게 된다.

#### ✅ Personal Access Token (PAT) 사용

![](https://zhtmr.github.io/static-files-for-posting/20250417/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202025-04-17%20%EC%98%A4%ED%9B%84%204.05.39.png?raw=true)

[Create Pull Request 메뉴얼](https://github.com/peter-evans/create-pull-request?tab=readme-ov-file#branch-token)에 Personal Access Token (PAT) 사용 시 권한 설정에 대해 잘 나와 있어 `GH_TOKEN` 이라는 이름으로 토큰을 만들고 secrets 에 등록해 줬다.
그리고 yml 파일 token 부분도 `secrets.GH_TOKEN` 으로 수정 후 다시 테스트 해봤다.


![](https://zhtmr.github.io/static-files-for-posting/20250417/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202025-04-17%20%EC%98%A4%ED%9B%84%204.11.45.png?raw=true)

그러나 위 사진처럼 상대방이 작성한 PR 이 내 닉네임(zhtmr) 으로 올라갔다. 내 계정에서 만든 토큰(GH_TOKEN)을 사용했기 때문이다. 또한 옆 Reviewer 도 맞지 않게 출력된다.


#### ✅ Assignees 와 Reviewer 가 동적으로 변해야 한다.
작성자 계정은 PAT 를 만든 계정을 따라간다는 것을 이해했다. 정상적으로 작동하려면 다음과 같이 작동해야 한다.

- **PR 의 작성자 닉네임은 실제로 push 한 계정 닉네임이 표시되어야 한다.**
- **Assignees 엔 실제 작성자가 표시되어야 하고, Reviewers 에는 작성자를 제외한 나머지 인원이 표시되어야 한다.**


##### token 파싱
먼저 PR 작성자 닉네임을 실제 코드를 push 한 계정으로 표시하기 위해선 프로젝트에 참여 중인 모두가 PAT 를 발급 받아야 한다고 생각했다. github 에서 발급받은 팀원들의 토큰을 secrets 에 모두 등록해 준다. (GH_TOKEN, GH_TOKEN_CM)
![](https://zhtmr.github.io/static-files-for-posting/20250417/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202025-04-17%20%EC%98%A4%ED%9B%84%204.39.55.png?raw=true)

그리고 이를 push 하는 계정에 따라 동적으로 선택해야 한다. 
push 를 하는 계정에서 github action workflow 가 동작하기 때문에 파싱하는 로직이 필요하다. steps 부분에 아래 코드를 추가한다. 

{% raw %}
```yml
steps:
    - name: Install yq
      run: sudo apt-get update && sudo apt-get install -y yq

    - name: Load token map
      id: token-map
      run: |
        ACTOR="${{ github.actor }}"
        TOKEN_VAR=$(yq ".\"$ACTOR\"" .github/workflows/user-token-map.yml | tr -d '"')  # 쌍따옴표 제거!
        echo "token_var=$TOKEN_VAR"
        echo "token_var=$TOKEN_VAR" >> $GITHUB_OUTPUT
```
{% endraw %}

`user-token-map.yml` 내부에는 아래와 같이 assignees 가 될 닉네임과 token secrets 변수가 정의되어 있다. 꼭 yml 에 정의할 필요는 없다. 다른 형식의 파일로 정의해도 되고, 파이썬 같은 스크립트를 실행하게 만들어도 상관없다.
```yml
cmnowhere: GH_TOKEN_CM
zhtmr: GH_TOKEN
```

`Load token map` 단계에서 `TOKEN_VAR` 변수가 만들어 지는데 해당 변수를 이후 create pull request 하는 단계의 token 옵션 에서 사용될 예정이다. 
주의할 점은 기존에 토큰 값을 입력할때 `secrets.GH_TOKEN` 방식으로 입력 했듯이 secrets 다음에 `.`(마침표)가 필요하기 때문에 마침표까지 결과에 같이 포함시켜야 한다. (`".\"$ACTOR\""`) 

##### Reviewer 파싱
기존에 이미 github var 에 REVIEWER 는 등록해 두었으니 이를 이용하면 된다.
{% raw %}
```yml
- name: Set reviewers except self
  id: reviewers
  run: |
    ALL_REVIEWERS="${{ vars.REVIEWERS }}"
    ACTOR="${{ github.actor }}"
    FILTERED=$(echo "$ALL_REVIEWERS" | tr ',' '\n' | grep -v "^$ACTOR$" | paste -sd "," -)
    echo "filtered=$FILTERED" >> $GITHUB_OUTPUT
```
{% endraw %}
모든 리뷰어(작성자 포함)에서 작성자를 제외하는 방식(`grep -v`)으로 FILTERED 라는 변수를 만든다. 이후 create pull request 단계에서 reviewers 값으로 사용될 예정이다.


## 개선
### create pull request

{% raw %}
```yml
- name: Create Pull Request to main
  id: create_pr
  uses: peter-evans/create-pull-request@v7
  with:
    author: ${{ github.actor }} <${{ github.actor }}@users.noreply.github.com>
    committer: ${{ github.actor }} <${{ github.actor }}@users.noreply.github.com>
    token: ${{ secrets[steps.token-map.outputs.token_var] }}
    base: main
    branch: ${{ github.event.ref }}
    title: "[auto] ${{ github.event.head_commit.message }}"
    body: |
      자동 PR 생성: `${{ github.ref_name }} → main`
      커밋 메시지: `${{ github.event.head_commit.message }}`
    labels: auto-merge
    assignees: ${{ github.actor }}
    reviewers: ${{ steps.reviewers.outputs.filtered }}
    draft: false
```
{% endraw %}

token 부분과 reviewers 부분에 위에서 작업한 변수 값을 넣으면 된다.
reviewer 의 경우 값 자체가 치환되는 것이기 때문에 {% raw %} `${{ steps.reviewers.outputs.filtered }}` {% endraw %} 이런식으로 바로 변수값을 사용하면 된다.
그러나 token 의 경우 secrets 이후 부분만 바뀌어야 하기 때문에 윗 방식으로는 사용하기 어렵다. ({% raw %} ${{ secrets.이부분 }} {% endraw %})

(아니면 token 파싱 시 애초에 secrets 라는 단어까지 파싱해서 가져와도 될듯)

동적으로 생성된 이름을 secrets 의 값으로 참조하기 위해 대괄호안에 정의한다.
{% raw %}
```yml
${{ secrets[steps.token-map.outputs.token_var] }}
```
{% endraw %}


![](https://zhtmr.github.io/static-files-for-posting/20250417/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202025-04-17%20%EC%98%A4%ED%9B%84%205.32.35.png?raw=true)
정상적으로 잘 작동하는 것을 볼 수 있다.

### auto-merge
하나 더 자동화 할 수 있는 부분이 있는데 바로 *merge 버튼을 클릭*하는 행위다. 보틍 merge 조건을 만족하게 되면 PR 작성자가 `Merge pull Request` 버튼을 직접 눌러 병합을 완료한다.
![](https://zhtmr.github.io/static-files-for-posting/20250417/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202025-04-17%20%EC%98%A4%ED%9B%84%205.34.48.png?raw=true)

github 에선 자체적으로 PR 의 요구사항을 만족하는 경우 auto-merge 를 수행하게 하는 옵션이 있다.
![](https://zhtmr.github.io/static-files-for-posting/20250417/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202025-04-17%20%EC%98%A4%ED%9B%84%205.58.43.png?raw=true)

해당 옵션이 활성화된 상태에서 PR을 작성하게 되는 경우 `Enable auto-merge` 라는 버튼이 보인다.
![](https://docs.github.com/assets/cb-153682/mw-1440/images/help/pull_requests/enable-auto-merge-drop-down.webp)
이 버튼을 누르면 더 이상 merge 를 하기위해 `Merge pull Request` 버튼이 활성화 될때까지 기다릴 필요 없이 github 가 알아서 merge 조건을 만족하는 경우 merge 시켜 준다. 조건을 만족하지 못하면 병합하지 않는다. (당연함..)

workflow 를 이용하면 이 `Enable auto-merge` 를 누르는 행위를 자동화 할 수 있다.
github actions marketplace 에 같은 개발자가 만든 [automerge](https://github.com/marketplace/actions/enable-pull-request-automerge) 에 대한 workflow도 있길래 같이 적용해 봤다. 

우선 자동 병합 기능을 사용하기 위해선 다음 조건이 충족되어야 한다.
- 대상 저장소 설정에서 `Allow auto-merge` 옵션이 활성화 되어 있어야 한다.
- base 브랜치(나의 경우 main)에 하나 이상의 branch protection rule 이 있어야 한다.
- 요구사항(ex. 1 approve)이 충족되지 않은 경우 auto merge 수행한다. 이미 요구사항이 충족되는 경우엔 즉시 병합한다.

`create pull request` 단계 이후에 다음 단계를 추가하면 된다. [메뉴얼](https://github.com/marketplace/actions/enable-pull-request-automerge#create-pull-request-example)에서 처럼 create pull request 와 auto merge 를 통합해 사용하기 위해선 개인 엑세스 토큰(PAT) 을 사용해야 한다. 

{% raw %}
```yml
- name: Create Pull Request to main
  id: create_pr
  uses: peter-evans/create-pull-request@v7
  with:
    author: ${{ github.actor }} <${{ github.actor }}@users.noreply.github.com>
    committer: ${{ github.actor }} <${{ github.actor }}@users.noreply.github.com>
    token: ${{ secrets[steps.token-map.outputs.token_var] }}
    base: main
    branch: ${{ github.event.ref }}
    title: "[auto] ${{ github.event.head_commit.message }}"
    body: |
      자동 PR 생성: `${{ github.ref_name }} → main`
      커밋 메시지: `${{ github.event.head_commit.message }}`
    labels: auto-merge
    assignees: ${{ github.actor }}
    reviewers: ${{ steps.reviewers.outputs.filtered }}
    draft: false

- name: Enable Auto Merge
  if: steps.create_pr.outputs.pull-request-operation == 'created' || steps.create_pr.outputs.pull-request-operation == 'updated'
  uses: peter-evans/enable-pull-request-automerge@v3
  with:
    token: ${{ secrets[steps.token-map.outputs.token_var] }}
    pull-request-number: ${{ steps.create_pr.outputs.pull-request-number }}
    merge-method: squash
  env:
    GH_TOKEN: ${{ secrets[steps.token-map.outputs.token_var] }} 
```
{% endraw %}


## reference
- [https://github.com/peter-evans/create-pull-request](https://github.com/peter-evans/create-pull-request)
- [https://github.com/marketplace/actions/enable-pull-request-automerge#enable-pull-request-auto-merge](https://github.com/marketplace/actions/enable-pull-request-automerge#enable-pull-request-auto-merge)
- [https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/automatically-merging-a-pull-request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/automatically-merging-a-pull-request)
