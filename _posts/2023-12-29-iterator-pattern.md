---
published: true
layout: single
title:  "[디자인패턴] 이터레이터 패턴(Iterator Pattern)"
excerpt: ""
categories:
  - Design Pattern
tags:
  - ['Design Pattern', 'Java', 'Refactoring']
use_math: true
---
> - 이터레이터에 대해 알아본다.
> - 이터레이터 패턴 적용 시 장점과 단점 및 개선 방향을 알아본다.

# 이터레이터(Iterator)란?
자료구조마다 데이터를 저장하는 방식이 다르다보니 데이터를 꺼내는 방법 또한 다르다. 순차적으로 접근 가능한 자료구조의 경우, for 문을 통해 가져오면 되지만 
`Set`이나 `Map` 등은 데이터의 순서를 저장하지 않는다. 이러한 자료구조의 경우 데이터를 조회하기 위해 탐색알고리즘을 이용해야 한다. 
각각의 자료구조마다 데이터를 조회하기 위한 방식에 **일관성**이 없다.    

이렇게 자료구조의 특성을 정확히 이해해야만 사용가능한 조회 방식은 너무 비효율적이다. 

![](/assets/images/20231229/iterator.png){: .align-center}

이터레이터 패턴은 직접 자료구조에 접근해 꺼내는 방식이 아닌, 값을 **꺼내주는 일을 대신하는 클래스**를 만들고 이를 통해 값을 꺼낸다. 
이터레이터를 쓰는 경우 데이터를 일관된 방식으로 조작할 수 있어 편리하다.

![img.png](/assets/images/20231229/iterable.png){: .align-center}
*java Collection들은 iterable 인터페이스를 구현하고있다.*



## 인터페이스 정의
기존에 만들었던 `List` 인터페이스에 데이터 조회를 일관성있게 하기 위한 `iterator()` 규칙을 추가한다. 이제부터 자료구조에 상관없이 데이터를 조회할땐 `Iterator()`를 구현해서 사용하면 된다.
```java
  public interface List<E> {
        ... 
    Iterator<E> iterator();
  }
```

## 인터페이스 구현체
```java
public class LinkedListIterator<E> implements Iterator<E> {

  LinkedList<E> list;
  int cursor;

  public LinkedListIterator(LinkedList<E> list) {
    this.list = list;
  }

  @Override
  public boolean hasNext() {
    return cursor >= 0 && cursor < list.size();
  }

  @Override
  public E next() {
    return list.get(cursor++);
  }
}
```
구체적인 조회 방식은 사용하는 자료구조에 맞게 `Iterator` 인터페이스를 통해 구현한다. 해당 코드에서는 `LinkedList` 에서 사용할 목적으로 구현했다.


`hasNext()` 는 반복할 항목이 남았는지 확인하는 용도로 사용하고 실제 값을 가져오는 작업은 `next()` 를 통해 가져오면 된다. 호출부에서 둘을 적절히 사용해 데이터를 조회하게 된다.

## LinkedList 에 반복자 구현하기
```java
public class LinkedList<E> extends AbstractList<E> {
          ...
  
  @Override
  public Iterator<E> iterator() {
    return new LinkedListIterator<>(this);
  }
          ...
}
```
현재 `LinkedList` 는 `List` 인터페이스를 구현한 `AbstractList` 클래스를 상속받아 만들고 있으므로, 메소드를 재정의 해준다. 구현부에는 아까 만들어놓은 반복자(`LinkedListIterator`)를 반환해주는 코드를 작성한다.


`LinkedListIterator`에서 `LinkedList`에 접근하기 위해선 생성자로 이터레이터를 사용하고자 하는 인스턴스를 주입해 줘야 한다. 

`LinkedList`클래스가 호출되면서 이터레이터도 사용될 것이기 때문에 `this`로 주입해 주면 된다.
그러면 `LinkedListIterator`는 호출될때마다 새로운 `LinkedList`객체를 받아 처음부터(cursor) 리스트 사이즈만큼(list.size()) 순회하면서 값을 찾을 것이다.

이제 `LinkedList`는 데이터 조회를 위한 새로운 기능을 갖추게 되었다!

`LinkedList`를 사용하고 있는 곳에서 아래처럼 반복자를 생성해 데이터를 조회한다.
```java
  new LinkedList<>().iterator();
```
![](/assets/images/20231229/ListIterator2.png){: .align-center}

## Iterator 를 이용해 데이터 조회하기

### As-is
```java
private void printMenu() {
  System.out.printf("[%s]\n", this.getTitle());

  for (int i = 0; i < this.menus.size(); i++) {
    System.out.printf("%d. %s\n", (i + 1), menus.get(i).getTitle());
  }

  System.out.printf("0. %s\n", "이전");
}
```
현재 `printMenu()`메소드는 다음과 같이 반복문을 이용해 `LinkedList`의 `get()` 메소드에 직접 접근하고 있다. 만약 `list` 타입이 아니라 `hashMap`같은 자료구조로 메뉴출력을 하도록 변경된다면 해당 소스코드도 변경해야 한다.


### To-be
```java
private void printMenu() {
  System.out.printf("[%s]\n", this.getTitle());

  Iterator<Menu> iterator = this.menus.iterator();
  int i = 1;
  while (iterator.hasNext()) {
    Menu menu = iterator.next();
    System.out.printf("%d. %s\n", i++, menu.getTitle());
  }

  System.out.printf("0. %s\n", "이전");
}
```
`Iterator`를 사용하면 위 처럼 사용가능하다. 자료구조가 변경되더라도 `Iterator`를 구현한 자료구조에서는 동일한 방식으로 데이터 조회가 가능하기 때문에 소스변경을 할 필요가 없다.
또한 내부 구조를 노출하지 않고 조회할 수 있다는 장점도 있다.

## 개선해야 될 부분
이터레이터 패턴을 적용해 자료구조에 의존하지 않고 데이터를 조회하는 방식으로 변경은 했지만 `LinkedListIterator`코드를 보면 내부에서 값을 찾기 위해 항상 처음부터 순차적으로 찾는다.
코드의 일관성은 좋아졌지만 굳이 클래스로 따로 빼놓을 이유가 없고, call stack 측면에서 복잡도만 더 높아졌다. 이 부분을 좀 더 개선해보자.

### static nested class 사용
우선 자료구조마다 각자 이터레이터를 구현한 클래스를 따로 만들지 말고, 자료구조 클래스 내부에 이터레이터 구현클래스를 두고 관리하기 쉽도록 개선해보자. 


어차피 자료구조마다 `Iterator`를 구현할 것이라면 해당 자료구조 코드 가까이 배치해 코드간의 응집도를 높여 좀 더 컴팩트하게 관리하자. 

```java
public class LinkedList<E> extends AbstractList<E> {
        ... //생략

  @Override
  public Iterator<E> iterator() {
    return new IteratorImpl<>(this);
  }

  /* static nested class */
  private static class IteratorImpl<E> implements Iterator<E> {

    LinkedList<E> list;
    int cursor;

    public IteratorImpl(LinkedList<E> list) {
      this.list = list;
    }

    @Override
    public boolean hasNext() {
      return cursor >= 0 && cursor < list.size();
    }

    @Override
    public E next() {
      return list.get(cursor++);
    }
  }
        ...
}
```
`LinkedList`클래스 내부에 static nested class 로 이터레이터 구현클래스를 만들었다. 현재 메소드는 정적(static)클래스가 될 수 있는 조건을 갖추고 있기 때문에 static을 붙이는 것이 권장된다.


static nested class가 될 수 있는 조건 및 특징은 다음과 같다.

1. **_외부 클래스 인스턴스와 독립적_**: 정적 중첩 클래스는 외부 클래스의 인스턴스와 관련이 없다. 외부 클래스의 인스턴스를 생성하지 않고도 인스턴스화 할 수 있다.
2. **_외부 클래스 인스턴스의 비정적 멤버에 직접 액세스할 수 없음_**: 정적 중첩 클래스는 외부 클래스의 정적 멤버만 직접 액세스할 수 있다. 비정적 멤버에는 직접 액세스할 수 없다.
3. **_정적 멤버를 가질 수 있음_**: 정적 중첩 클래스는 정적 필드 및 메서드를 가질 수 있다.
4. **_독립적으로 인스턴스화 가능_**: 외부 클래스의 인스턴스를 생성하지 않고도 정적 중첩 클래스의 인스턴스를 생성할 수 있다.

위에서 구현한 중첩클래스는 외부클래스의 <U>인스턴스 멤버에 엑세스하고 있지 않다.</U>  중첩클래스(멤버클래스) 내부에서 자체적으로 직접 `LinkedList`객체를 통한 순회를 하고 있다.

✍️ 인스턴스 멤버에 엑세스하고 있지 않다는 말은 해당 클래스는 단순히 파라미터로 받은 값을 내부적으로 처리할 뿐이지, 외부 인스턴스의 필드나 메서드에 접근하고 있지 않다는 것을 의미한다.
주로 유틸리티 함수(Math 클래스 등)를 static class로 사용한다.
{: .notice--info }

외부클래스의 인스턴스 필드인 first나 last에는 직접 접근이 불가능하다. 
<U>static nested class내부에서 외부클래스 인스턴스 주소를 저장하지 않기 때문이다.</U>

아래 코드처럼 외부클래스의 인스턴스 필드 엑세스는 불가능하다. `this`를 통해 외부 클래스의 인스턴스 주소를 생성자 파라미터로 넘겨서 사용할 뿐이다.
![](/assets/images/20231229/cant-accsess.png){: .align-center}



이펙티브 자바 _p.146(아이템24)_ 에서 정적 멤버 클래스에 대해 아래와 같이 서술하고 있다. 

> _정적 멤버 클래스와 비정적 멤버 클래스의 구문상 차이는 단지 static이 붙어있고 없고 뿐이지만, 의미상 차이는 의외로 꽤 크다. 
> 비정적 멤버 클래스의 인스턴스는 바깥 클래스의 인스턴스와 암묵적으로 연결된다. 그래서 비정적 멤버 클래스의 인스턴스 메서드에서 정규화된 this를 사용해 바깥 인스턴스의 메서드를 호출하거나 바깥 인스턴스의 참조를 가져올 수 있다. 
> 정규화된 this란 `클래스명.this` 형태로 바깥 클래스의 이름을 명시하는 용법을 말한다.[JLS, 15.8.4] 따라서 개념상 중첩 클래스의 인스턴스가 바깥 인스턴스와 독립적으로 존재할 수 있다면 정적 멤버 클래스로 만들어야 한다. 
> 비정적 멤버 클래스는 바깥 인스턴스 없이는 생성할 수 없기 때문이다._
>    
> _비정적 멤버 클래스의 인스턴스와 바깥 인스턴스 사이의 관계는 멤버 클래스가 인스턴스화될 때 확립되며, 더 이상 변경할 수 없다. 
> 이 관계는 바깥 클래스의 인스턴스 메서드에서 비정적 멤버 클래스의 생성자를 호출할 때 자동으로 만들어지는 게 보통이지만, 드물게는 직접 `바깥 인스턴스의 클래스.new MemberClass(args)`를 호출해 수동으로 만들기도 한다. 
> 예상할 수 있듯, 이 관계 정보는 비정적 멤버 클래스의 인스턴스 안에 만들어져 메모리 공간을 차지하며, 생성 시간도 더 걸린다._
> 
> _`멤버 클래스에서 바깥 인스턴스에 접근할 일이 없다면 무조건 static을 붙여서 정적 멤버 클래스로 만들자.`
> static을 생략하면 바깥 인스턴스로의 숨은 외부 참조를 갖게 된다. 앞서도 얘기했듯 이 참조를 저장하려면 시간과 공간이 소비된다. 
> 더 심각한 문제는 가비지 컬렉션이 바깥 클래스의 인스턴스를 수거하지 못하는 메모리 누수가 생길 수 있다는 점이다(아이템 7). 참조가 눈에 보이지 않으니 문제의 원인을 찾기 어려워 때때로 심각한 상황을 초래하기도 한다._

만약 위 클래스에 `static` 을 떼고 생성자를 없애게 되면 자바 컴파일러는 클래스 내부에 아래와 같은 코드를 암묵적으로 추가한다.
```java
  private class IteratorImpl<E> implements Iterator<E> {
  
    // 바깥 객체의 주소를 저장할 빌트인 필드
    final LinkedList this;

    // inner 객체를 생성할 때 바깥 객체의 주소를 받는 생성자
    public IteratorImpl<E>(LinkedList p) {
      this.this = p;
    }
        ...
  }
```

non-static class는 외부 인스턴스 주소를 통해서만 생성 가능하기 때문에 암묵적으로 `this`변수를 만들어 인스턴스 값을 저장한다. 참조를 저장하기 위한 공간과 시간이 소비된다. 

![img.png](/assets/images/20231229/innerclass-byte.png){: .align-center}
*non-static class로 만들면 숨은 외부 참조를 갖게된다.*
![img.png](/assets/images/20231229/static-nested-class.png){: .align-center}
*바깥 클래스를 참조하지 않는 경우엔 static 을 붙여라!*

그러나 현재 개선하고자 하는 목적은 외부의 참조를 끊고 독립적으로 동작하게 만드는 것이 목적이 아니라 **`Iterator`의 코드를 수정해 응집도를 높히는 것이다.** 


또한 처음에 `LinkedListIterator`클래스로 따로 분리시켰던 코드를 `LinkedList`에서 관리하기 때문에 이를 통한 이점도 챙길 수 있다. 
이는 `GRASP pattern`의 `Information Expert`조건을 만족시킬 수 있는 상황이다.

✍️ **Information Expert**: 역할을 수행할 수 있는 정보를 가지고 있는 객체에 역할을 부여하자. 
단순해 보이는 이 원칙은 객체지향의 기본 원리 중에 하나이다. 객체는 데이터와 처리로직이 함께 묶여 있는 것이고, 
자신의 데이터를 감추고자 하면 오직 자기 자신의 처리 로직에서만 데이터를 처리하고, 외부에는 그 기능(역할)만을 제공해야 하기 때문이다.
{: .notice--info }

---

### non-static class(inner class) 사용
static nested class 와의 차이점은 생성자에 파라미터가 없다. 이는 파라미터로 데이터를 받아 가공처리 하는 방식이 아니라, 
inner class 내부에 암묵적으로 생성된 `this`를 통해 외부 클래스에 접근하겠다는 의미다. 

inner class를 사용하면 외부클래스의 변수를 사용할 수 있다. 

`Iterator`호출을 통해 순회를 할 때마다 멤버클래스 생성자로 인스턴스를 받아서 처리하는 것이 아니라, 외부 인스턴스의 주소에 직접 접근해 해당 필드의 데이터를 이용해 작업하게 된다.
```java
public class LinkedList<E> extends AbstractList<E> {
      ... //생략
  
  @Override
  public Iterator<E> iterator() {
    return new IteratorImpl<>();
  }
  
  /* non-static class */
  private class IteratorImpl<E> implements Iterator<E> {

    Node<E> cursor;
    
    // 생성자 코드를 통해 외부 클래스 변수를 참조한다.
    public IteratorImpl() {
      this.cursor = (Node<E>) LinkedList.this.first;  
    }

    @Override
    public boolean hasNext() {
      return cursor != null;
    }

    @Override
    public E next() {
      E value = cursor.value;
      cursor = cursor.next;
      return value;
    }
  }
      ...
}
```

실제로 `java.util.LinkedList`에서 내부클래스로 `Iterator`를 구현하고 있다.
![img.png](/assets/images/20231229/innerclass-listiterator.png){: .align-center}
*java.util.LinkedList의 Iterator*

---
### 익명 클래스(anonymous class) 사용
익명 클래스란 클래스의 이름이 존재하지 않는 클래스다. 아래 코드처럼 생성과 구현부분은 존재하지만 `class`라는 키워드도 없고 클래스의 이름도 없다. 

쓰이는 시점에 선언과 동시에 인스턴스가 만들어진다.
따라서 익명 클래스는 재사용이 불가능하다. 

익명 클래스는 객체로서 다루겠다는 의미보다는 **1회성 이거나 짧은 구현부를 가진 간단한 클래스**의 경우 굳이 클래스로 정의할 필요가 없다는 것에 좀 더 의미가 있다. 

선언과 구현을 동시에 하기때문에 인터페이스 또한 익명클래스로 바로 구현해서 쓸 수 있다. 그리고 모양을 잘 보면 객체를 생성해 바로 리턴한다. 이는 이펙티브 자바에서 말하는 정적 팩토리 메소드 구현에 주로 사용된다.(팩토리 메소드 패턴이 아니다.)
```java
  ...
@Override
public Iterator<E> iterator() {
  return new Iterator<>() {   // 익명 클래스
    Node<E> cursor = LinkedList.this.first;

    @Override
    public boolean hasNext() {
      return cursor != null;
    }

    @Override
    public E next() {
      E value = cursor.value;
      cursor = cursor.next;
      return value;
    }
  };
}
```

#### 소스코드
[771eaae](https://github.com/zhtmr/mystudy/commit/771eaae488ad5ab78de175e53703caf960dfcafe)

## 정리
이펙티브 자바에선 멤버 클래스에 대해 아래와 같이 정리하고 있다.
> 메서드 밖에서도 사용해야 하거나 메소드 안에 정의하기엔 너무 길다면 `멤버 클래스`로 만든다. 
> - 멤버 클래스의 인스턴스가 바깥 인스턴스를 참조한다면 👉 <U>non-static class</U>
> - 멤버 클래스의 인스턴스가 바깥 인스턴스를 참조하지 않는다면 👉 <U>static nested class</U>
> - 멤버 클래스가 한 메소드 안에서만 쓰이면서 그 인스턴스를 생성하는 지점이 단 한 곳이고 해당 타입으로 쓰기에 적합한 클래스나 인터페이스가 이미 있다면 👉 <U>anonymous class</U>


## reference
{% capture notice-2 %}
- [한빛출판네트워크](https://www.hanbit.co.kr/channel/category/category_view.html?cms_code=CMS8586826397)
- 이펙티브 자바 3판
{% endcapture %}

<div class="notice">{{ notice-2 | markdownify }}</div>


