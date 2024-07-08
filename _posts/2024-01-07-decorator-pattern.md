---
published: true
layout: single
title:  "[Design Pattern] 데코레이터 패턴(Decorator Pattern)"
excerpt: ""
categories:
  - Design Pattern
tags:
  - ['Design Pattern', 'Java', 'Refactoring']
use_math: true

---
> - [이전 글](https://zhtmr.github.io/java/file-io-stream/#%EC%A0%95%EB%A6%AC--%EA%B0%9C%EC%84%A0%EC%82%AC%ED%95%AD)에 이어서 상속을 이용한 방식의 문제점을 알아본다.
> - 데코레이터 패턴에 대해 알아본다.
> - 데코레이터 패턴을 이용해 직렬화(Serialize)를 적용해 본다.

# 문제
앞선 코드에서 기존 클래스의 기능을 확장하기 위해 상속을 이용해 `DataInputStream`, `DataOutputStream`, `Buffered~` 를 만들었다.
다중 상속이 불가능하기 때문에 기능을 조합하기 위해선 특정 기능을 구현한 서브클래스를 계속해서 만들어야 한다.



[![](https://github.com/zhtmr/static-files-for-posting/blob/main/20240108/aggregation.png?raw=true){: .align-center}
*상속과 집합 관계의 차이점.*](javascript:return false;)

```java
// 아래와 같은 관계를 집합 관계라 한다.
public class A {
  // 객체 A 는 B 에 대한 참조를 갖고있다.
  private B obj;
  
  public A(B b) {
    this.B = b;
  }
}
```


## 해결

![](https://github.com/zhtmr/static-files-for-posting/blob/main/20240108/Welcome_To_littleBits.gif?raw=true){: .align-center}
*데코레이터 패턴은 기능 추가, 삭제를 자유롭게 할 수 있다!*





[![](https://mermaid.ink/img/pako:eNq1U7FuwyAQ_RV0U6LEVruiqEvdMZO3ioXC2UWxwcJ4qBL_e7FNSkkUqYM7cbx7d--4484gjESgIBre94XiteUt04TMd_JqqgqRnCeEkF2NrsBeWNU5ZfRmS0nprNJ1cAvTuwmUZvhocAJHpmOyUrVdg6umXJIVKIzlzthr1kwuCMqFQANxFc2jak53irsE3TzQ367Tx6Hm9r6CFP6vEsL4Dpc8TwZ667uZTHTHwg-XLEu7-ZCVvm2pJPlODJ4ZkCx7CdYf5H-HPOV5jGIa9tCibbmSfjPm_jJwn9giA-pNye2JAdOj5_HBmfJLC6DODriHoZO-6WGRgFa86X_QN6m88JXZcf1uTOTg7D2GdZyO8RugkzbL?type=png){: .align-center}*데코레이터 패턴*](javascript:return false;)


| 특징                              | 데코레이터 패턴                                                  | 상속                                                           |
|----------------------------------|------------------------------------------------------------------|---------------------------------------------------------------|
| 확장 방법                        | 데코레이터로 감싸기                                            | 기존 클래스를 특수화한 새로운 클래스 생성                     |
| 유연성                           | 매우 유연함, 데코레이터 동적 추가/제거 가능                   | 상대적으로 유연성이 떨어지며 변경이 모든 하위 클래스에 영향   |
| 코드 재사용                      | 높음, 데코레이터는 여러 구성 요소 간에 재사용 가능             | 계층 구조를 통한 코드 재사용                                   |
| 합성 vs. 상속                    | 합성을 강조, 상속보다 합성 선호                                 | 클래스 계층 구조 생성을 통한 코드 재사용                      |
| 동적 vs. 정적 바인딩             | 동적 바인딩, 데코레이터는 실행 중에 동적으로 추가/제거 가능    | 정적 바인딩, 컴파일 시에 결정                                   |

## 예시
예시
로깅 기능 추가: 기존 객체의 메서드 호출 시점과 반환 값을 로깅하여 디버깅이나 모니터링에 활용할 수 있습니다. 데코레이터 클래스를 생성하여 기존 객체를 감싸고, 메서드 호출 시점에 로깅 로직을 추가하면 됩니다.
인증 및 권한 부여: 기존 객체의 메서드 호출 전에 인증 및 권한 부여를 수행하여 접근 제어를 구현할 수 있습니다. 데코레이터 클래스를 생성하여 기존 객체를 감싸고, 메서드 호출 전에 인증 및 권한 부여 로직을 추가하면 됩니다.
캐싱 기능 추가: 기존 객체의 메서드 호출 결과를 캐싱하여 성능을 향상시킬 수 있습니다. 데코레이터 클래스를 생성하여 기존 객체를 감싸고, 메서드 호출 전에 캐시에 결과를 저장하고 반환 로직을 추가하면 됩니다.
트랜잭션 관리: 기존 객체의 메서드 호출을 트랜잭션 단위로 관리할 수 있습니다. 데코레이터 클래스를 생성하여 기존 객체를 감싸고, 메서드 호출 전에 트랜잭션을 시작하고, 메서드 호출 후에 트랜잭션을 커밋 또는 롤백하는 로직을 추가하면 됩니다.
데이터 변환: 기존 객체의 반환값을 변환하여 다른 형식으로 제공할 수 있습니다. 데코레이터 클래스를 생성하여 기존 객체를 감싸고, 메서드 호출 후에 반환값을 변환하는 로직을 추가하면 됩니다.

# FileWriter / FileReader
- 중간에 인코딩 과정이 포함됨
- 따라서 바이너리 파일이 아닌, 텍스트 파일을 읽어야 한다. (파일이 깨진다.)



# 직렬화
## ObjectInputStream / ObjectOutputStream

## CSV

## JSON
