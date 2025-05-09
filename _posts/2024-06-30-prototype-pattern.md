---
published: true
layout: single
title:  "[디자인패턴] 프로토타입 패턴(Prototype Pattern)"
excerpt: ""
categories:
  - Design Pattern
tags:
  - ['Design Pattern', 'Java', 'Refactoring']
use_math: true
---


# 프로토타입 패턴

> - 프로토타입 패턴에 대해 알아보고 사용 사례를 살펴봅니다.

## 정의
기존 인스턴스를 복제하여 새로운 인스턴스를 만드는 방법
- 복제 기능을 갖추고 있는 기존 인스턴스를 프로토타입으로 사용해 새 인스턴스를 만들 수 있다.

## 주요 구성 요소
![img](https://zhtmr.github.io/static-files-for-posting/images/20240629/prototype-pattern.drawio.png?raw=true){: .align-center}




## 객체를 복제할 때 생기는 문제점
객체를 복제하는 것은 생각처럼 간단한 일이 아닐 수 있다. 다음과 같은 몇가지 문제가 있는데 하나씩 살펴보자.

<details>
<summary>객체 외부에서 private 필드를 복사할 수 없다.</summary>
<div markdown="1">

> ```java
> class Person {
>   private String name;
>   private int age;
>
>   public Person(String name, int age) {
>       this.name = name;
>       this.age = age;
>   }
>
>   // Getter
>   public String getName() {
>       return name;
>   }
>
>   public int getAge() {
>       return age;
>   }
> }
>
> public class Main {
>   public static void main(String[] args) {
>       Person person1 = new Person("Alice", 30);
>
>        // 비공개 필드 접근 시도 - 오류 발생
>        // String name = person1.name; // 컴파일 에러
>        // int age = person1.age; // 컴파일 에러
>
>        // 복제본을 생성하려고 하지만 비공개 필드에 접근할 수 없음
>        Person person2 = new Person(person1.getName(), person1.getAge());
>        
>        System.out.println(person1.getName() + ", " + person1.getAge());
>        System.out.println(person2.getName() + ", " + person2.getAge());
>    }
> }
>
> ```

</div>
</details>

<details>
<summary>객체의 복제본을 생성하려면 객체의 클래스를 알아야 한다.</summary>
<div markdown="1">

클래스 의존도가 높아진다.


> ```java
> class Employee {
>    private String name;
>    private int salary;
>
>    public Employee(String name, int salary) {
>        this.name = name;
>        this.salary = salary;
>    }
>
>    // Getter
>    public String getName() {
>        return name;
>    }
>
>    public int getSalary() {
>        return salary;
>    }
>
>    // 복사 생성자 필요
>    public Employee(Employee other) {
>        this.name = other.name;
>        this.salary = other.salary;
>    }
> }
>
> public class Main {
>   public static void main(String[] args) {
>       Employee emp1 = new Employee("Bob", 50000);
>
>       // 복제본을 생성하려면 Employee 클래스에 의존
>       Employee emp2 = new Employee(emp1); // Employee 클래스에 의존
>        
>       System.out.println(emp1.getName() + ", " + emp1.getSalary());
>       System.out.println(emp2.getName() + ", " + emp2.getSalary());
>   }
> }
>
> ```
</div>
</details>

<details>
<summary>인터페이스 기반 설계 문제</summary>
<div markdown="1">

구체 클래스에 의존하지 않고 객체를 복제하기 어렵다.


> ```java
> interface Copyable {
>     Copyable copy();
> }
>
> class Student implements Copyable {
>    private String name;
>    private int grade;
>
>    public Student(String name, int grade) {
>       this.name = name;
>       this.grade = grade;
>    }
>
>     @Override
>     public Copyable copy() {
>         return new Student(this.name, this.grade);
>     }
>
>     // Getter
>     public String getName() {
>         return name;
>     }
>
>     public int getGrade() {
>         return grade;
>     }
> }
>
> public class Main {
>   public static void main(String[] args) {
>       Copyable student1 = new Student("Charlie", 10);
>
>       // 인터페이스를 통해서는 구체적인 클래스에 접근할 수 없음
>       // Student student2 = (Student) student1.copy(); // 다운캐스팅 필요 - 유연성 저하
>         
>       Copyable student2 = student1.copy(); // Copyable 인터페이스로는 구체적인 필드 접근 불가
>         
>       // student2가 Student 타입인지 확인 후 캐스팅 필요
>       if (student2 instanceof Student) {
>           Student copiedStudent = (Student) student2;
>           System.out.println(copiedStudent.getName() + ", " + copiedStudent.getGrade());
>       }
>   }
> }
> ```

</div>
</details>

위와 같은 문제를 회피하면서도 복제할 수 있는 방법에 대해 알아보자.

## 프로토타입 패턴 예제
우선 프로토타입 패턴의 구성요소대로 인터페이스를 만든다. 왜 인터페이스가 필요한지에 대해선 코드를 통해 알아 보겠다.
```java
public interface Prototype {
  Prototype clone();
}
```
그 후 인터페이스를 구현하는 클래스 내에서 clone() 메소드를 재정의한다.

### GameCharacter
```java
public class GameCharacter implements Prototype {
  private String name;
  private int level;
  private String profession;

  public GameCharacter(String name, int level, String profession) {
    this.name = name;
    this.level = level;
    this.profession = profession;
  }
  
  public String getName() {
    return name;
  }

  public void setName(String name) {
    this.name = name;
  }

  public int getLevel() {
    return level;
  }

  public void setLevel(int level) {
    this.level = level;
  }

  public String getProfession() {
    return profession;
  }

  public void setProfession(String profession) {
    this.profession = profession;
  }

  // clone 재정의
  @Override
  public Prototype clone() {
    return new GameCharacter(name, level, profession);
  }

  @Override
  public String toString() {
    return "GameCharacter [name=" + name + ", level=" + level + ", profession=" + profession + "]";
  }

  @Override
  public boolean equals(Object o) {
    if (this == o)
      return true;
    if (!(o instanceof GameCharacter))
      return false;
    GameCharacter that = (GameCharacter) o;
    return level == that.level && Objects.equals(name, that.name) && Objects.equals(profession,
      that.profession);
  }
}
```

### Client

```java
public class Client {
  public static void main(String[] args) {
    List<Prototype> characters = new ArrayList<>();  // 원본 저장용 리스트
    List<Prototype> charactersCopy = new ArrayList<>();  // 복제 저장용 리스트

    // 원본 객체 생성
    GameCharacter originalCharacter = new GameCharacter("Archer", 10, "Archer");
    characters.add(originalCharacter);

    // 복제 객체 생성
    GameCharacter clonedCharacter = (GameCharacter) originalCharacter.clone();
    characters.add(clonedCharacter);

    // 복제 객체의 속성 변경
    clonedCharacter.setName("Mage");
    clonedCharacter.setProfession("Mage");

    // 출력
    System.out.println("Original Character: " + originalCharacter);
    System.out.println("Cloned Character: " + clonedCharacter);
    System.out.println();
    
    cloneAndCompare(characters, charactersCopy);
  }

  private static void cloneAndCompare(List<Prototype> characters, List<Prototype> charactersCopy) {
    // 이 부분이 인터페이스를 사용한 이유다. 
    for (Prototype character : characters) {
      charactersCopy.add(character.clone());
    }

    for (int i = 0; i < characters.size(); i++) {
      if (characters.get(i) != charactersCopy.get(i)) {
        System.out.println(i + ": 서로 다른 캐릭터 객체다. (yay!)");
        if (characters.get(i).equals(charactersCopy.get(i))) {
          System.out.println(i + ": 그리고 서로 같은 객체다.(yay!)");
        } else {
          System.out.println(i + ": 그러나 서로 다른 객체다. (booo!)");
        }
      } else {
        System.out.println(i + ": 서로 같은 프로토타입 객체다. (booo!)");
      }
    }
  }
}
```
위 코드에서 `characters` 배열에서 값을 꺼내 각각을 clone() 할때 구체적인 클래스를 몰라도 일관된 방식으로 코드를 작성 가능하다. clone() 내부에서 구체 클래스가 만들어져 복제된다.
```java
for (Prototype character : characters) {
  charactersCopy.add(character.clone());
}
```
### 출력결과

```bash
Original Character: GameCharacter [name=Archer, level=10, profession=Archer]
Cloned Character: GameCharacter [name=Mage, level=10, profession=Mage]

0: 서로 다른 캐릭터 객체다. (yay!)
0: 그리고 서로 같은 객체다.(yay!)
1: 서로 다른 캐릭터 객체다. (yay!)
1: 그리고 서로 같은 객체다.(yay!)
```
clone() 팩토리 메소드 안에서 새로운 객체를 리턴하고 있기 때문에 서로 다른 주소값을 가진 객체다. 
그리고 객체 내부 필드값이 같은 경우 같은 객체로 보기위해 equals() 를 재정의 하였기 때문에 서로 같은 객체임이 보장된다.

### java 에서 지원하는 Cloneable 인터페이스
java 에서는 clone() 을 위한 Java Native Interface 를 지원한다. 해당 메소드 구현 시 `super.clone()` 을 호출하게 되면 내부적으로 얕은 복사가 진행된다.
```java
@HotSpotIntrinsicCandidate
protected native Object clone() throws CloneNotSupportedException;
```

해당 메소드는 Object 클래스에 있고, 복제 메소드가 필요한 클래스에서 재정의 하면 되는데, 그 클래스는 Cloneable 이라는 인터페이스를 구현하고 있어야 한다.
```java
public interface Cloneable {
}
```
Cloneable 인터페이스는 아무런 메소드도 존재하지 않는데, 이를 마커 인터페이스(Marker Interface)라 한다. 마커 인터페이스가 구현된 클래스는 특정 속성임을 java 가 알 수 있도록 해준다.
Cloneable 인터페이스가 구현되어 있는 클래스는 clone() 메소드를 호출할 수 있다는 자격이라고 보면된다. 만약 마커 인터페이스가 없는 상태에서 clone() 을 호출하게 되면 `CloneNotSupportedException`이 발생한다.

직렬화 객체에 직렬화가 가능함을 알리기위해 붙이는 Serializable 인터페이스의 경우도 마커 인터페이스다. 

<details>
<summary>JNI</summary>
<div markdown="1">

Java Native Interface 는 java 구현되지 않은 일부 프로세스를 가능하게 만든다. 예를 들어 하드웨어 조작 명령이나 직접적인 OS API 명령
![img](https://zhtmr.github.io/static-files-for-posting/images/20240629/jni.png?raw=true){: .align-center}
*출처 : https://medium.com/@sarafanshul/jni-101-introduction-to-java-native-interface-8a1256ca4d8e*
</div>
</details>

<details>
<summary>얕은복사 / 깊은복사</summary>
<div markdown="1">

> 객체의 복제와 항상 함께 등장하는 주제 중 하나가 shallow copy / deep copy 라고 생각한다. 간단히 정리하면
> - shallow copy : 객체의 최상위 레벨만 복사. 하위 객체는 참조를 공유. 원본 객체나 복사된 객체의 변경이 서로에게 영향을 미칠 수 있다.
> - deep copy : 객체 전체를 재귀적으로 복사. 하위 객체까지 모두 독립적인 복사본 생성. 서로 영향을 미치지 않는다.

</div>
</details>

## 장점과 단점
- 장점
  - 복잡한 객체를 만드는 과정을 숨길 수 있다.
  - 기존 객체를 복제하는 과정이 새 인스턴스를 만드는 것보다 비용면에서 효율적일 수도 있다.
  - 추상적인 타입을 리턴할 수 있다.
- 단점
  - 복제한 객체를 만드는 과정 자체가 복잡할 수 있다. (순환 참조가 있는 경우)

## 자바에서 찾아보는 프로토타입
### ArrayList.clone()
ArrayList 를 복사할때 clone() 메소드를 사용하면 된다.

![img.png](https://zhtmr.github.io/static-files-for-posting/images/20240629/arraylist-cloneable.png?raw=true){: .align-center}
*ArrayList 는 Cloneable 인터페이스를 구현하고 있다.*

그러나 이 방법은 잘 쓰이지 않는다. 왜냐하면 보통 ArrayList 를 받을때 아래처럼 인터페이스 타입으로 받기 때문이다.
```java
List<Item> items = new ArrayList<>();
```
List 인터페이스에는 clone() 메소드가 존재하지 않는다.

### 프로토타입 패턴을 쓰지 않고 생성자로 복사
ArrayList 의 생성자 중에 컬렉션 타입을 받는 생성자가 있다. 인자로 전달하면 복제된다.

#### ArrayList
```java
public ArrayList(Collection<? extends E> c) {
    Object[] a = c.toArray();
    if ((size = a.length) != 0) {
        if (c.getClass() == ArrayList.class) {
            elementData = a;
        } else {
            elementData = Arrays.copyOf(a, size, Object[].class);
        }
    } else {
        // replace with empty array.
        elementData = EMPTY_ELEMENTDATA;
    }
}
```

#### Client
```java
List<Item> clone = new ArrayList<>(items);  // 파라미터로 컬렉션 타입을 전달하면 복제된다.
```
해당 메소드 중간에 Arrays.copyOf() 메소드를 통해 파라미터로 넘겨받은 컬렉션을 복사한다.

### 리플랙션 사용
리플랙션을 이용한 라이브러리를 사용하면 복잡한 코드를 직접 짜지 않아도 쉽게 복제가 가능하다.
첫번째 인자로 오는 타겟 객체를 두번째 인자의 타입으로 변환시켜준다.

리플랙션 관련해서는 [해당 글](https://zhtmr.github.io/java/proxy-pattern/)에서 정리했다.


#### ModelMapper 라이브러리
```java
ModelMapper modelMapper = new ModelMapper();
GithubIssueData githubIssueData = modelMapper.map(githubIssue, GithubIssueData.class);
```

#### ObjectMapper 라이브러리
```java
Map<String, Object> response = om.readValue(response, Map.class);
```
ObjectMapper 는 팀 프로젝트에서 OAuth 인증 시 플랫폼 별 상이한 JSON 을 파싱하기 위해 사용했던 경험이 있다.
[(코드보기)](https://github.com/bitcamp-teams/mos/blob/develop/mos/src/main/java/com/mos/global/auth/handler/RequestAttributes.java#L22)


#### Gson 라이브러리
복제할 인스턴스를 GsonBuilder 의 toJson() 의 파라미터로 넘겨주면 새로운 JSON 형태로 반환해준다.
아래 코드는 프로젝트에서 사용했던 코드의 일부분이다. [(전체 코드보기)](https://github.com/bitcamp-teams/mos/blob/develop/mos/src/main/java/com/mos/global/common/message/Result.java#L89)

```java
// Result.class
@Override
public String toString() {
  return new GsonBuilder().serializeNulls().create().toJson(this);
}
```
Rest api 반환 객체에 toString 을 재정의하고 JSON 객체로 리턴하기 위해 GsonBuilder 를 사용했다.
클라이언트 쪽 코드는 아래와 같이 일반적인 toString 을 호출하듯이 하면 JSON 형태로 반환할 수 있다.

```java
@PostMapping("add")
public String add(@RequestBody @Valid CodeRequestDto codeRequestDto) throws Exception {
  codeService.add(codeRequestDto);
  return new Result<>().setResultData(codeService.list(Paging.builder().build())).toString();
}
```
아래에서 살펴볼 직렬화 방식과 같다고 보면 된다.

### 객체를 복제하는 다양한 방법

<details>
  <summary>복사 생성자</summary>
<div markdown="1">

> ### 복사 생성자
> 클래스 내부에 `복사 생성자`를 정의하여, 해당 클래스의 인스턴스를 매개변수로 받아 필드 값을 복사한다.
>
> ```java
> class Person {
>   private String name;
>   private int age;
>
> // 생성자
> public Person(String name, int age) {
>   this.name = name;
>   this.age = age;
> }
>
> // 복사 생성자
> public Person(Person other) {
>   this.name = other.name;
>   this.age = other.age;
> }
>
> //  // Getter 가 없어도 private 필드 복사 가능
> //  public String getName() {
> //    return name;
> //  }
> //
> //  public int getAge() {
> //    return age;
> //  }
>
> 
> @Override
> public String toString() {
>   return "Person{name='" + name + "', age=" + age + "}";
> }
> }
>
> public class Main {
>   public static void main(String[] args) {
>       Person person1 = new Person("Alice", 30);
>       Person person2 = new Person(person1); // 복사 생성자 사용
>
>     System.out.println(person1);
>     System.out.println(person2);
>   }
> }
>
> ```
</div>
</details>

<details>
  <summary>직렬화</summary>
<div markdown="1">

> ### 직렬화
> 객체를 직렬화한 후 역직렬화하는 방법. 이 방법은 기존 객체와의 참조가 끊어져 깊은 복사를 보장한다.
>
> ```java
> import java.io.*;
>
> public class MyClass implements Serializable {
>     private int field1;
>     private String field2;
>     
>     public MyClass deepCopy() {
>         try {
>             ByteArrayOutputStream bos = new ByteArrayOutputStream();
>             ObjectOutputStream out = new ObjectOutputStream(bos);
>             out.writeObject(this);
>             
>             ByteArrayInputStream bis = new ByteArrayInputStream(bos.toByteArray());
>             ObjectInputStream in = new ObjectInputStream(bis);
>             return (MyClass) in.readObject();
>         } catch (IOException | ClassNotFoundException e) {
>             e.printStackTrace();
>             return null;
>         }
>     }
>     
>     // 기타 메서드 및 접근자
> }
>
> ```
>
> 자바스크립트에서는 `JSON.stringify()` 와 `JSON.parse()` 를 통해 가능하다.
> ```javascript
> const obj = {
>   a: 1,
>   b: {
>     c: 2,
>   },
> };
>
> const copiedObj = JSON.parse(JSON.stringify(obj));
>
> copiedObj.b.c = 3
>
> obj.b.c === copiedObj.b.c  //false 
> ```

</div>
</details>

<details>
  <summary>팩토리 메소드</summary>
<div markdown="1">

> ### 팩토리 메소드
> 클래스의 의존성을 줄일 수 있다.
>
> ```java
> public interface Copyable {
>     Copyable copy();
> }
>
>
> public class MyClass implements Copyable {
>     private int field1;
>     private String field2;
>     
>     @Override
>     public MyClass copy() {
>         return new MyClass(this);
>     }
>     
>     // 복사 생성자
>     public MyClass(MyClass other) {
>         this.field1 = other.field1;
>         this.field2 = other.field2;
>     }
>     
>     // 기타 메서드 및 접근자
> }
>
> ```
</div>
</details>

## 정리
프로토타입 패턴은 다른 패턴들에 비해 간단하다. 미리 만들어 놓은 프로토타입 객체를 복제하여 새로운 객체를 생성하는 패턴이다.
객체 생성 시 매번 DB 를 조회해야 하는 등과 같이 생성 비용이 큰 경우 사용할 수 있을 것 같다.

그러나 형태는 간단하지만 현업에서 쓰려면 clone() 메소드를 어떻게 작성해야 할지 생각을 해야될 것 같다.
특히 java 에서 지원하는 Cloneable 의 기본적인 구현 방식(`super.clone()`)은 얕은 복사임을 인지하고 있어야 하고, 만약 깊은 복사를 구현해야 하는 경우, 객체의 모든 하위 객체들도 올바르게 복제되어야 하므로 구현이 까다로울 수 있다.
또한 복제된 객체가 프로토타입 객체에 밀접하게 연관되어 있어, 만약 원본 객체의 내용이 변경되면 새로운 객체를 만들기 위해 프로토타입을 갱신해야 할 수도 있다.


## 참고
- [https://refactoring.guru/ko/design-patterns/prototype](https://refactoring.guru/ko/design-patterns/prototype)
- [https://medium.com/@sarafanshul/jni-101-introduction-to-java-native-interface-8a1256ca4d8e](https://medium.com/@sarafanshul/jni-101-introduction-to-java-native-interface-8a1256ca4d8e)