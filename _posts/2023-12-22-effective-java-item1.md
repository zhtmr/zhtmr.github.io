---
published: true
layout: single
title:  "[Effective Java] 아이템1. 생성자 대신 정적 팩터리 메서드를 고려하라"
excerpt: ""
categories:
  - Effective Java
tags:
  - ['Effective Java']
use_math: true
---
> - 정적팩토리 메소드가 무엇인지 알아본다.
> - 생성자 대신 정적팩토리 메소드를 사용함으로써 얻는 이점을 알아본다.

# 정적 팩토리 메소드(Static Factory Method) 란?
객체의 인스턴스를 얻는 방법은 생성자를 호출하는 것이다. 