---
published: true
layout: single
title: "[Spring] @Transactional이 동작하지 않는 경우"
excerpt: "@Transactional이 프록시를 거치지 않아 적용되지 않는 케이스 정리"
categories:
  - Spring
tags: [['Spring', '트랜잭션', 'TIL']]
use_math: false
---

> @Transactional을 붙였는데도 트랜잭션이 적용되지 않는 경우들을 정리한 글이다.

## 들어가며

요즘 프로젝트를 하다가 @Transactional을 붙였는데도 롤백이 되지 않는 상황을 겪었다. 분명히 트랜잭션 어노테이션을 붙였는데 왜 안 되는지 한참 헤맸다. 그래서 트랜잭션이 적용되지 않는 케이스를 정리해봤다.

## 같은 클래스 내부 호출(self-invocation)

가장 흔한 건 같은 클래스 안에서 메서드를 호출할 때다. 스프링은 프록시로 트랜잭션을 처리하는데, 내부 호출(self-invocation)은 프록시를 거치지 않기 때문에 트랜잭션이 적용되지 않는다.

예를 들면 이런 코드다.

```java
public class OrderService {
  public void outer() {
    this.inner(); // 이렇게 부르면 트랜잭션 안먹음
  }

  @Transactional
  public void inner() {
    // ...
  }
}
```

outer에서 inner를 호출하면 this로 호출하는 꼴이라 프록시 객체를 거치지 않는다. 결국 트랜잭션이 시작되지 않는다.

## private 메서드에 @Transactional

또 하나는 private 메서드에 @Transactional을 붙이는 경우인데, 이것도 동작하지 않는다. 프록시 기반 @Transactional은 기본적으로 public 메서드에만 적용되기 때문이다. 여기에 더해 CGLIB 서브클래스 프록시는 private(그리고 final, static) 메서드를 오버라이드할 수 없어 가로채지도 못한다. private 메서드가 안 되는 건 이 두 제약이 함께 작용한 결과다.

## 예외 발생 시 롤백 동작

@Transactional이 기본적으로 롤백하는 대상은 RuntimeException과 Error뿐이다. IOException, SQLException 같은 checked 예외는 메서드 밖으로 던져져도 기본 설정에서는 롤백되지 않고 그대로 커밋된다. checked 예외에서도 롤백하려면 `@Transactional(rollbackFor = Exception.class)`처럼 롤백 대상을 명시해야 한다.

또 한 가지, 트랜잭션 메서드 안에서 예외를 try-catch로 잡고 다시 던지지 않으면 롤백 트리거 자체가 발생하지 않는다.

## 해결 방법

- self injection을 한다.
- 아예 클래스를 분리해서 외부 빈을 주입받아 호출한다.
- AOP 프록시를 직접 꺼내 쓰는 방법도 있지만 권장되지는 않는다.

## 정리

정리하면, 트랜잭션은 프록시 기반이라 프록시를 거치지 않는 호출에서는 동작하지 않는다. 이 점만 기억하면 된다.
