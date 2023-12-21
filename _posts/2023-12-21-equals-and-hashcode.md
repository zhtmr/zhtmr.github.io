---
published: true
layout: single
title:  "[Java] equals() 와 hashCode() 를 재정의하는 이유"
excerpt: ""
categories:
  - Java
tags:
  - Java
use_math: true
---

> - equals() 와 hashCode() 의 차이점을 알아본다.
> - equals() 와 hashCode() 를 재정의하는 이유에 대해 알아본다.



## Object 클래스의 equals()
_"`equals()` 와 `==` 는 둘다 동일하게 동작한다."_   
모든 java 클래스의 부모 클래스인 `Object` 클래스에는 `equals()` 메소드가 정의 되어 있다.

![](/assets/images/20231221/equals-method.png){: .align-center}
*Object 클래스의 equals()*

`equals()` 를 호출하는 객체의 인스턴스와 파라미터로 전달되는 객체의 인스턴스가 같은지 `==` 연산자를 통해 확인한다. 
만약 어떤 객체가 같은지 서로 비교해야하는 로직에서 `equals()` 메소드를 따로 재정의하지 않으면 결과값은 항상 false 가 나올 것이다. 
이는 우리가 기대했던 결과가 아니다. 주로 `equals()` 비교를 하는 경우는 객체의 내용물이 같으면 같은 객체로 보고 작업을 하겠다는 목적일텐데, 이렇게되면 인스턴스의 주소값 비교(동일성 비교)를 통해 false 가 리턴될 것이기 때문이다.
그렇기 때문에 객체의 동등성(equality) 비교를 원하는 경우엔 해당 메소드를 필수로 재정의 해야한다.

보통 동등성/동일성 키워드로 검색을 하게되면 `==` 는 동일성(identity), `equals()` 는 동등성(equality) 이라고 결론을 내리고 끝나는 글이 많아서 마치 암기의 영역같아 보이지만, 
실제로 `equals()` 로 동등성이 보장될 수 있는 이유가 바로 재정의(override)를 통해 값 비교를 하고 있기 때문이다.

그럼 객체간의 비교를 하려면 `equals()` 메소드만 재정의해서 쓰면 되는걸까? 

## Object 클래스의 hashCode()
![](/assets/images/20231221/hashcode-method.png){: .align-center}
*Object 클래스의 hashCode()*

`Object` 클래스의 `hashCode()` 메소드 또한 [JNI(Java Native Interface)](https://ko.wikipedia.org/wiki/%EC%9E%90%EB%B0%94_%EB%84%A4%EC%9D%B4%ED%8B%B0%EB%B8%8C_%EC%9D%B8%ED%84%B0%ED%8E%98%EC%9D%B4%EC%8A%A4)
로 정의되어 있다. 해당 메소드는 특정한 알고리즘을 통해 일정 길이의 값을 뽑아내는 역할을 한다. 이는 `equals()` 재정의를 통한 필드값을 일일이 확인하는 방식과는 별개로 해시함수의 결과값이 서로 같은지를 알아보기 위함이다.
일종의 `인증(authentication)` 에 목적이 있는 것이다. 우리가 일상에서 내가 나라는 신원을 증명하기위해 주민등록증 같은 신분증을 제시하는 것과 같다. 내가 나 임을 증명하기 위해 자라온 일생을 처음부터 끝까지 나열하는 사람은 없을 것이다.

![hash.png](/assets/images/20231221/hash.png){: .align-center}
*hash function*

만약 `hashCode()` 라는 메소드를 통한 비교를 하지않고, 일일이 데이터 값을 비교한다면 비효율적일 것이다. 바이트 값을 모두 비교하면서 두 객체가 서로 같은지 확인해야 할 것이다.
**같음을 증명하기 위해 모든 값을 비교할 필요가 없다**는 것이 바로 해시알고리즘의 목적이다. 약간의 리소스를 희생하더라도 시간적 이득을 보겠다는 것에 가장 큰 의미가 있다.(Space-Time trade-off)

만약 `equals()` 만 재정의하고 `hashCode()` 는 재정의 하지 않는다면 어떻게 될까?

```java
public class Test {

  public static void main(String[] args) {
    My obj1 = new My();
    obj1.name = "홍길동";
    obj1.age = 20;

    My obj2 = new My();
    obj2.name = "홍길동";
    obj2.age = 20;

    System.out.println(obj1 == obj2); // false
    System.out.println(obj1.equals(obj2)); // true

    System.out.println(Integer.toHexString(obj1.hashCode())); // 7ad041f3
    System.out.println(Integer.toHexString(obj2.hashCode())); // 251a69d7
  }

  static class My {
    String name;
    int age;

    @Override
    public boolean equals(Object obj) {
      if (this == obj)
        return true;
      if (obj == null)
        return false;
      if (getClass() != obj.getClass())
        return false;
      My other = (My) obj;
      return age == other.age && Objects.equals(name, other.name);
    }
  }
}
```
`equals()` 비교는 true 가 나오지만 hash code 값은 다르다는 것을 알 수 있다. `Object` 에 정의된 `hashCode()` 는 각 인스턴스마다 고유한 값을 리턴하기 때문이다. 
만약 `HashMap` 같은 곳에 key 로 저렇게 넣을 경우 **같은 데이터를 가지고 있음에도** 서로 다른 객체로 받아들여 저장되지 않을 것이다.
![img.png](/assets/images/20231221/hashmap-put.png){: .align-center}
*HashMap 클래스의 put()은 hashCode()를 통해 비교한다.*
![img_1.png](/assets/images/20231221/hashmap-hash.png){: .align-center}


[java 공식 api 문서](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/lang/Object.html#hashCode())에서는 두 개체가 동일하면 해당 해시 값도 동일해야 함을 강조한다.
따라서 객체의 내용을 비교하기 위해 `equals()` 메서드를 재정의하는 경우 일관성을 보장하기 위해 `hashCode()` 메서드도 재정의하는 것이 중요하다.

![](/assets/images/20231221/equals-api-doc.png){: .align-center}
*equals() 재정의 시 hashCode() 도 반드시 재정의 해야한다.*

정리하자면 `equals()` 를 통해 데이터를 비교하고, `hashCode()`를 통해 데이터의 무결성을 보장하는 것이다. 
따라서 인스턴스가 다르더라도 데이터가 같으면 같은 해시 값을 리턴하도록 오버라이딩 해야 한다.
이제야 비로소 `equals()` 는 동등성(equality), `hashCode()`는 동일성(identity)을 보장한다는 의미를 이해할 수 있을 것이다.

## String 이나 wrapper 클래스가 key 로 쓰이는 이유
`HashMap` 이나 `HashSet`은 데이터를 저장할 때 `key - value` 형식으로 저장하는데 이때 key 는 중복이 되면 안되고 고유한 값이어야 한다. 
이를 보장하기 위해 `hashCode()` 를 재정의한 객체를 주로 key 로 사용하는데 대표적인게 `Integer`, `String` 이다. `Integer`는 내부에 `hashCode()` 를 재정의 하고 있으며, 받은 정수 값 그대로 리턴한다. 따라서 같은 수를 넣지 않는 한 중복 될 일이 없다.
`String` 클래스는 불변(Immutable)객체 이기 때문에 key 값으로 사용된다.

`String` 의 경우 변수 할당 방식이 두가지 인데 `new String()` 으로 만들거나 `""` 리터럴 형식으로 사용한다.

### new String()
```java
public class Test {
  public static void main(String[] args) {
    
    String s1; // s1은 String 인스턴스 주소를 담는 레퍼런스이다.

    // String 인스턴스
    // - 힙에 Hello 문자 코드를 저장할 메모리를 만들고 그 주소를 리턴한다.
    // - 내용물의 동일 여부를 검사하지 않고 무조건 인스턴스를 생성한다.
    // - 가비지가 되면 가비지 컬렉터에 의해 제거된다.
    s1 = new String("Hello");
    String s2 = new String("Hello");

    // 인스턴스가 같은지를 비교해보면,
    System.out.println(s1 == s2); // false => 서로 다른 인스턴스이다.
  }
}
```

### 문자열 리터럴 방식
```java
public class Exam0111 {
  public static void main(String[] args) {

    // 문자열 리터럴
    // - string constant pool 메모리 영역에 String 인스턴스를 생성한다.
    // - 상수풀에 이미 같은 문자열의 인스턴스가 있다면, 그 주소를 리턴한다.
    // - 왜? 메모리 절약을 위해 중복 데이터를 갖는 인스턴스를 생성하지 않는다.
    // - JVM이 끝날 때까지 메모리에 유지된다.
    //
    String x1 = "Hello"; // 새 String 인스턴스의 주소를 리턴한다.
    String x2 = "Hello"; // 기존의 String 인스턴스 주소를 리턴한다.

    // 인스턴스의 주소를 비교해 보면,
    System.out.println(x1 == x2); // true => 두 String 객체는 같다.
  }
}
```
주로 String 문자열을 만들땐 리터럴 방식으로 만들고 할당하는데 이렇게 만들어진 String 은 불변객체가 된다.
문자열을 수정하는 것처럼 보이는 작업(`replace()`,`concat()` 등)을 수행할 때 사실은 새로운 문자열 객체가 생성되는 것이다.
같은 변수에 재할당하더라도 기존 데이터를 덮어쓰는게 아니라 `String constant pool` 에 저장되고, 새로운 인스턴스 주소를 갖게 된다.

```java
public class ImmutableString {
  public static void main(String[] args) {
    
    String s1 = new String("Hello");
    
    String s2 = s1.replace('l', 'x');
    System.out.println(s1 == s2); // false
    System.out.printf("%s : %s\n", s1, s2); // Hello : Hexxo

    String s3 = s1.concat(", world!");
    System.out.printf("%s : %s\n", s1, s3); // Hello : Hello, world!
  }
}
```

자바 문자열의 불변성은 여러 가지 중요한 이점을 갖는다.

- **스레드 안정성(Thread-safe)**: 문자열이 불변이기 때문에 중간에 바뀔 위험이 없어 여러 스레드 간에 안전하게 공유할 수 있으며, 동시 수정으로 인한 데이터 손상의 위험이 없다. 
스레드가 문자열을 변경하려면 원래 문자열을 그대로 두고 새로운 문자열을 생성하기 때문이다.

- **캐싱(Caching)**: 문자열이 불변이기 때문에 자바는 이들을 캐시할 수 있다. 
특정 값의 문자열을 만들 때, 자바는 문자열 상수 풀(string constant pool)에서 동일한 값을 갖는 기존의 문자열을 재사용할 수 있다. 이는 메모리 사용량을 줄이고 성능을 향상시킬 수 있다.

- **보안(Security)**: 문자열은 종종 암호나 API 키와 같은 민감한 정보를 저장하는 데 사용된다. 불변성은 이러한 문자열이 생성된 후에 값이 실수나 악의적으로 변경되지 않도록 보장한다.

- **최적화(Optimization)**: 불변성은 한번더 최적화 할 수 있는 기회를 제공한다. 예를 들어, 문자열의 `hashCode()`는 한 번 계산하고 캐시할 수 있습니다. 왜냐하면 값이 변하지 않기 때문이다. 긴 문자열의 경우 짧은 해시값으로 관리할 수 있다.

- **코드 단순화**: 불변 객체를 사용할 때 예상치 않은 변경을 걱정할 필요가 없다. 이로 인해 코드가 단순화되고 더 예측 가능해진다.




## @EqualsAndHashCode 활용 예시
lombok 라이브러리를 쓰면 `equals()` 와 `hashCode()` 를 쉽게 재정의 해주는 어노테이션을 제공한다.  
[https://jojoldu.tistory.com/134](https://jojoldu.tistory.com/134)

## @Data 사용시 주의점
lombok 에는 @Data 라는 강력한 어노테이션을 지원하는데 이는 constructor, getter, setter, toString, equals, hashcode 메소드를 자동으로 재정의 해준다.
주로 dto 객체에서 사용하는 메소드들인데 구현의 귀찮음을 한번에 해결해 준다는 편리함이 있지만 재정의되는 메소드들 중에 equals, hashCode 도 있다는 것을 충분히 인지한 후에 사용해야 한다.

```java
  @Test
  public void name() {
    Set fruits = new HashSet<>();

    Fruit fruit = new Fruit("apple", "banana");
    fruit.add(fruit);
    assertTrue(fruits.contains(fruit));

    fruit.setLastName("melon");
    assertFalse(fruits.contains(fruit));
  }
```


### reference
- [https://jojoldu.tistory.com/134](https://jojoldu.tistory.com/134)
- [https://deveric.tistory.com/123](https://deveric.tistory.com/123)
- [https://lkhlkh23.tistory.com/159](https://lkhlkh23.tistory.com/159)

