---
published: true
layout: single
title:  "[Java] 기존 인터페이스에 새로운 규칙을 추가해보자!(추상클래스, 인터페이스 상속)"
excerpt: ""
categories:
  - Java
tags:
  - ['java', 'refactoring']
use_math: true
---
> - 인터페이스 간의 상속에 대해 알아본다.
> - 추상클래스와 함께 사용하는 방법과 이점을 알아본다.

# 인터페이스 상속
만약 이미 인터페이스를 구현한 클래스가 여럿 존재하는 상태에서 새로운 규칙을 인터페이스에 정의하고 싶을땐 어떻게 해야할까?
이 글에서는 기존 인터페이스에 새로운 규칙 추가시 발생하는 딜레마를 해결하는 과정에 대해 설명한다.

```java
  // Interface
  public interface Spec {
    void m1();
  }
```
```java
  // Concrete Class
  public class A implements Spec {

    @Override
    public void m1() {
      System.out.println("A.m1()");
    }
  }
```
```java
  // Concrete Class
  public class B implements Spec {

  @Override
  public void m1() {
    System.out.println("B.m1()");
  }
}
```
현재 이런식으로 구현된 상태인데 새로운 클래스 `C` 는 `m1()` 기능외에 새로운 기능을 정의해서 쓰고싶은 상황이다.
```java
  public class C implements Spec {
    @Override
    public void m1() {
      System.out.println("A.m1()");
    }
    
    // 새로운 기능 추가
    public void m2() {
      ...
    }
  }
```
인터페이스는 일종의 *규칙 모음*이기 때문에 정의된 규칙은 모든 구현클래스가 따라야만 한다. 
만약 `m2()` 를 `Spec` 인터페이스에 추상메소드로 정의한다면 `Spec` 을 구현한 모든 클래스에서 재정의해야 한다. 
새로운 기능을 인터페이스에 정의하면서도 기존 구현클래스에는 오류전파가 되지 않도록 하려면 어떻게 해야할까?   
자바에서는 이러한 문제에 대한 해결책을 제시한다.

## default method
java 8 이후로 인터페이스에서 `default method` 를 작성할 수 있다.
- 기존 프로젝트에 영향을 끼치지 않으면서 기존 규칙에 새 메서드를 추가할 때 유용한다.
- 인터페이스에서 미리 구현한 메서드이기 때문에 클래스에서 구현을 생략할 수 있다.
- 서브클래스의 구현을 강제할 수 없다는 것이 단점이다.

```java
  public implements Spec {
    void m1();
    
    // default method : 서브클래스에서 재정의 할 메소드이기 때문에 빈 상태로 구현만 해둔다.
    default void m2() {}
  }
```
앞에 `default` 키워드를 넣고 구현부까지 작성해 주면 된다. 
이때 `default` 는 접근제한자의 default 가 아니라 인터페이스의 *디폴트 메소드*를 뜻한다. (인터페이스는 항상 추상메소드(`public abstract`) 만 가질 수 있다..)

```java
  public class C implements Spec {
    @Override
    public void m1() {
      System.out.println("A.m1()");
    }
  
    // 새로운 기능 추가. 이 메소드는 추상메소드가 아니기 때문에 구현을 강제하지 않는다.
    @Override
    public void m2() {
        ...
    }
  }
```
`default method` 가 필요한 구현클래스에선 필요에 따라 메소드를 재정의해서 사용하면 된다. 
그러나 `default mehthod` 는 추상메소드가 아니기 때문에 서브클래스의 구현을 강제하지 않는다는 단점이 있다. 실수로 구현하지 않아도 정상적인 작동을 하며, 이를 막을 수가 없다.

## extends interface
위에서 문제가 되는 구현의 강제성을 유도하기 위해 새로운 기능이 정의된 인터페이스를 만들고, 기존의 인터페이스를 상속받게 한다.

![](/assets/images/20231220/interface-extends.png){: .align-center}
*새로운 인터페이스가 기존의 인터페이스를 상속한다.*

기존 구현클래스들은 그대로 `Spec` 인터페이스를 구현하게 놔두고, 새로운 기능이 추가적으로 필요한 클래스는 `Spec` 을 상속받은 `Spec2` 인터페이스를 구현하는 것이다.
이렇게 함으로써 기존 소스에 영향을 주지 않고 메소드 구현을 강제하면서도 새로운 기능을 추가할 수 있다.

```java
  public interface Spec2 extends Spec{
    void m3();
  }
```
```java
  public class C implements Spec2{
    // 서브인터페이스 구현 시 수퍼인터페이스도 모두 구현해야 한다.
    @Override
    public void m1() {
      System.out.println("A.m1()");
    }
    
    @Override
    public void m2() {
          ...
    }
  
    @Override
    public void m3() { // 추가
          ...
    }
    
  }
```
인터페이스 간의 상속을 통해 문제를 해결한 것처럼 보인다. 하지만 만약 구현해야하는 기능이 100개 정도된다면 모든 구현 클래스에서 메소드를 재정의 해야한다.

## with abstract class
이 방식은 위에서 언급한 단점을 커버할 수 있을 뿐만 아니라 새로운 기능추가 시 코드가 더 간결해진다. 일부 메소드 구현을 추상클래스에서 하기때문에 메소드 구현의 피로도가 낮아진다.
규모가 커지면서 공통기능을 인터페이스로 많이 추출해야 하는 경우엔 중간에 추상클래스를 두고 작업하는 것이 좋다.
[이전 글](https://zhtmr.github.io/java/abstract-class/) 에서도 이와같은 방식을 활용했다.

![](/assets/images/20231220/interface-with-abstract.png){: .align-center}
*추상클래스가 인터페이스를 상속받는다*

```java
  interface CommonSpec {
    m1();
    m2();
    m3();
    m4();
  }
  
  abstract class AbstractSpec implements CommonSpec{
    @Override
    public void m1() {}
    
    @Override
    public void m2() {}
    
    @Override
    public void m3() {}
    
    @Override
    public void m4() {}
  }
```

```java
  public class MyClass extends AbstractSpec {
    // 구현클래스에서 필요한 메소드만 재정의 한다.
    @Override
    public void m1() {
      System.out.println("MyClass.m1()");
    }
    
    @Override
    public void m2() {
      System.out.println("MyClass.m2()");
    }
  } 
```