---
published: true
layout: single
title:  "[GitHub Blog] Github 블로그에 carousel 추가"
excerpt: ""
categories:
  - GitHub Blog
tags:
  - [GitHub Blog, Jekyll]
use_math: true
carousels:
  - images:
      - image: /assets/images/sample_image1.png
      - image: /assets/images/sample_image2.png
      
---


# jekyll 블로그에 carousel 적용하기
{% include carousel.html height="50" unit="%" duration="7" number="1" %}

## 설정추가
페이지에 이미지 경로를 설정을 추가한다.
```
carousels:
- images: 
  - image: /assets/images/image-1.jpg
    url: post-name-1
  - image: /assets/images/image-2.jpg
    url: post-name-2
  - image: /assets/images/image-3.jpg
    url: post-name-3
```

## carousel.html 파일 준비
아래 파일을 다운받아 `_includes` 폴더 아래에 `carousel.html` 로 저장한다.

파일은 [여기](https://jekyllcodex.org/without-plugin/slider/)서 다운로드 한다.

## 사용
아래처럼 include 해서 사용할 수 있다. 옵션도 있는것 같다.
{% raw %}
<pre>
  <code>
    {% include carousel.html height="50" unit="%" duration="7" number="1" %}
  </code>
</pre>
{% endraw %}





## reference
{% capture notice-2 %}
- [https://jekyllcodex.org/without-plugin/slider/](https://jekyllcodex.org/without-plugin/slider/)
- [https://cadamini.github.io/test-images-carousel/](https://cadamini.github.io/test-images-carousel/)
{% endcapture %}

<div class="notice">{{ notice-2 | markdownify }}</div>


