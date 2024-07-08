---
published: true
layout: single
title:  "프론트 컨트롤러(DispatcherServlet) 직접 구현해보기"
excerpt: ""
categories:
  - Java
tags:
  - ['Java','Spring','Refactoring']
use_math: true
---

# 프론트 컨트롤러

## 현재 모습
모든 서블릿이 서블릿 컨테이너로부터 직접 요청을 받고 작업 후 리턴하는 방식. 필요로 하는 공통적인 작업이 각 서블릿에서 중복으로 수행됨
# 