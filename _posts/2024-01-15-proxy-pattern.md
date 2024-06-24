---
published: true
layout: single
title:  "[Java] reflection 을 이용한 proxy 객체 활용(프록시 패턴)"
excerpt: ""
categories:
  - Java
tags:
  - ['Java','Design pattern', 'Refactoring']
use_math: true
---

> - 프록시 패턴에 대해 알아본다.
> - `java.lang.reflect.Proxy` 를 이용해 프록시 객체(stub)를 자동 생성하도록 해보자.
> - 런타임 시점에 의존객체를 주입한다.

# Reflection?
Java의 리플렉션은 런타임 시 클래스의 메타데이터(예: 필드, 메서드, 생성자, 주석 등)를 검사하거나 상호 작용할 수 있는 기능이다. 
컴파일 시 이름을 몰라도 클래스, 메서드 및 필드를 동적으로 조작할 수 있는 방법을 제공한다.

{:.no_toc}
## Class
다음과 같이 런타임 시 클래스나 인터페이스 정보를 가져올 수 있다.
```java
Class<?> clazz = MyClass.class; 
Class<?> clazz = obj.getClass(); 
Class<?> clazz = Class.forName("com.mysql.cj.jdbc.Driver"); 
```

{:.no_toc}
## Class 상세 정보 확인
```java
Class<?> clazz = MyClass.class;

// 클래스 이름 확인
String className = clazz.getName();

// 접근제한자 정보 확인
int modifiers = clazz.getModifiers();

// super class 정보 확인
Class<?> superClass = clazz.getSuperclass();

// 구현된 인터페이스 정보 확인
Class<?>[] interfaces = clazz.getInterfaces();
```

{:.no_toc}
## 필드 및 메소드 정보 확인
```java
// 모든 필드 정보 가져오기
Field[] fields = clazz.getDeclaredFields();

// 모든 메소드 정보 가져오기
Method[] methods = clazz.getDeclaredMethods();
```

{:.no_toc}
## 필드 수정
```java
// private 필드 접근
Field privateField = clazz.getDeclaredField("fieldName");
privateField.setAccessible(true); // true 로 바꿔주면 private 필드에 접근 가능하다.
Object value = privateField.get(obj);

// private 필드 수정
privateField.set(obj, newValue);
```

{:.no_toc}
## 메소드 호출
아래처럼 리플렉션을 이용해 메소드를 호출할 수 있다.
```java
// 파라미터 전달과 함께 메소드 호출
Method method = clazz.getDeclaredMethod("methodName", parameterTypes);
Object result = method.invoke(obj, arg1, arg2);
```

## 리플렉션은 언제 쓸까?
인스턴스를 직접 생성해서 메소드를 호출하는 것이 훨씬 직관적이고 이해가 쉬워보이는데 왜 굳이 리플렉션을 사용해서 호출하는걸까? 

클라이언트 코드를 작성하는 입장과 프레임워크/라이브러리 코드를 작성하는 입장이 다르기 때문이다. 인스턴스를 직접 생성한다는 것은 타입이 정적으로 결정된다는 의미이다. 범용적으로 사용되어야 하는 소스코드에서는 제약 사항이 많다.

예를 들어, 리플렉션은 객체를 바이트 스트림으로 변환해야 하는 직렬화 및 역직렬화 프로세스에서 클래스 구조를 동적으로 검사하고 조작할 수 있게 해준다. 
`Gson` 라이브러리 역시 리플렉션을 이용해 객체의 타입을 추론한다.

또한, 곧 알아볼 Proxy 객체 생성에도 리플렉션이 사용된다. 스프링에서는 이를 더 발전시켜 `AOP(Aspect-Oriented Programming)` 를 가능하게 한다. 스프링에서 주로 쓰이는 `@Transactional` 어노테이션 또한 프록시를 통해 트랜잭션을 관리한다.

![](https://raw.githubusercontent.com/zhtmr/static-files-for-posting/018897a917be5333b888f905d5224700d7abfe30/20240116/gson.png){: .align-center}
*gson 은 리플렉션을 이용해 타입을 알아낸다.*

[이전 글](https://zhtmr.github.io/java/annotation/)에서 어노테이션을 통해 세션을 확인하는 과정 또한 내부적으로 리플렉션을 사용한다.
![](https://raw.githubusercontent.com/zhtmr/static-files-for-posting/bfc38f3d2b533335a1ba0c298b4ba2b4d67615bd/20240116/getParameterType.png){: .align-center}
*HandlerMethodArgumentResolver 는 내부적으로 리플렉션을 이용해 정보를 가져온다.*

## 리플렉션 사용시 주의 사항
### 오버헤드
리플렉션은 런타임 시 유형 검사 및 메소드 호출을 포함하는 작업이기 때문에 일반적인 작업보다 느리다. 시간과 메모리 측면에서 오버헤드가 발생한다.

### 보안문제
리플렉션은 접근제한자를 모두 무시하기 때문에 보안 취약성이 있다.

### 코드 가독성
리플렉션에 크게 의존하는 코드는 가독성이 낮고 유지 관리가 더 어렵다. 클래스의 대부분이 런타임 시 동적으로 결정되는 경우 개발자는 클래스의 구조와 동작을 이해하는 것이 어려울 수 있다.

### 컴파일 안정성
리플렉션은 컴파일 타입 검사를 우회하기 때문에 잠재적인 오류가 발생할 가능성이 있다.


# Proxy?
프록시란 **'대리'**, **'대신'** 이라는 뜻을 가진다. 
이 글에서는 분산 컴퓨팅 환경에서 원격 메소드를 호출을 대신 해주는 객체라고 보면 될 것 같다. 

## 프록시 패턴
작은 규모의 Stand-alone 어플리케이션에서는 굳이 프록시가 의미가 없다. 
서비스의 규모가 커지고 도메인이 많아지면서 단일 서버에서 모든 요청을 처리하기 버겁고, 동시 처리가 필요해지는 시점이 되면 각 도메인을 별도의 서버로 분산시켜서 운영하는 것이 더 효율적일 것이다. 

이때, 단일 어플리케이션에서 동작하던 코드를 분리하는 작업을 해야 하는데 이렇게 되면 함수간 서로 원격 호출을 할 수 밖에 없다.
이런 분산 컴퓨팅 환경에서 기존의 방식과 동일하게 함수를 호출하면서도 원격 호출의 기능을 추가하려면 어떻게 해야 될까?

클라이언트 쪽에서는 프록시를 이용해 호출하는지, 아닌지 관심이 없다. 아키텍처가 변경되어도 기존 호출 방식 그대로 동작해야 한다. (Open-Closed Principle)

이에 대한 고민은 꾸준히 진행되어 왔다. ([RPC](https://ko.wikipedia.org/wiki/%EC%9B%90%EA%B2%A9_%ED%94%84%EB%A1%9C%EC%8B%9C%EC%A0%80_%ED%98%B8%EC%B6%9C), [RMI](https://ko.wikipedia.org/wiki/%EC%9E%90%EB%B0%94_%EC%9B%90%EA%B2%A9_%ED%95%A8%EC%88%98_%ED%98%B8%EC%B6%9C), [CORBA](https://ko.wikipedia.org/wiki/%EA%B3%B5%ED%86%B5_%EA%B0%9D%EC%B2%B4_%EC%9A%94%EA%B5%AC_%EB%A7%A4%EA%B0%9C%EC%9E%90_%EA%B5%AC%EC%A1%B0))
(최근에는 stub 객체를 사용하지 않는 RESTful 방식으로 통신한다.)


![](https://raw.githubusercontent.com/zhtmr/static-files-for-posting/cc0e5b26c01a52f783ecbe507e4f41cd88ea5a2e/20240116/proxy-pattern.png){: .align-center}*proxy pattern*

## stub

분산 애플리케이션에서 스텁은 그 자체로 제 기능은 발휘하지 못하지만 원래 객체가 무엇인지 알아낼 수 있는 참조 역할을 하고, 원 객체의 기능조작을 위임받은 proxy 역할을 하는 작은 객체로 생각하면 된다.
**클라이언트에서는 기존과 동일한 메소드를 호출하는 것처럼** 보이지만 실제 프록시 객체 내부에서 원격 호출을 하고 있는 셈이다.

실제 구현 시 stub 에 대응되는 원격 객체(server 쪽에 존재)와 **같은 인터페이스를 구현**해 동작 규칙을 동일하게 만든다.

현재 프로젝트에 구현된 동작 방식은

1. 클라이언트와 서버의 연결이 수립되면, proxy 객체(stub)는 원격 메소드 호출에 필요한 파라미터들을 마살링(Marshalling) 하여 원격 JVM 으로 전송한 뒤 응답 결과를 기다린다.
        (현재 프로젝트에서는 `도메인명`, `호출할 함수명`, `함수 호출에 필요한 파라미터`)
2. 서버의 스켈레톤(skeleton) 은 클라이언트가 보낸 마샬된 파라미터를 원래대로 언마살량 한다.
3. 이 파라미터를 실제 원격 객체에게 전달하여 메소드를 호출한다.
4. 호출 후 결과 값이나 예외를 스켈레톤에게 되돌려준다.
5. 스켈레톤은 다시 결과값이나 예외를 마샬링하여 호출자(stub)에게 전달한다.
 

![](https://github.com/zhtmr/static-files-for-posting/blob/091a3aa93a625c2120a05525297e69d8bfcd2bfd/20240117/proxy-diagram.png?raw=true){: .align-center}
*stub 을 통해 원격 메소드에 접근한다.*

## skeleton
스텁은 객체 그 자체와 동일한 비즈니스 메소드를 가진 인터페이스를 구현하지만, 스텁의 메소드는 비즈니스 로직 자체를 담고있지는 않으며, 
클라이언트가 스텁의 비즈니스 메소드를 호출하면 호출된 메소드 명과 매개변수로 전달된 값들이 스트림 형태로 네트워크를 통해 스켈레톤에 전달된다.
해당 스트림을 스켈레톤이 받게 되면 스켈레톤은 스트림을 분석하여 어떤 메소드가 요청되었는지를 파악하고, 
서버에 있는 객체의 비즈니스 메소드를 호출하게 된다. 메소드의 실행 결과값은 다시 스켈레톤에 의해 스텁으로 전달되며, 
스텁은 마치 해당 비즈니스 로직을 로컬 컴퓨터에서 처리한 것처럼 클라이언트 애플리케이션에 결과값을 전달한다.


# reflection 으로 proxy 객체(stub) 자동 생성하기
[기존 소스](https://github.com/zhtmr/mystudy/commit/cb91aaa99dff2a3457367fe5f26478b663ebc20c)에서는 stub 객체를 각각의 도메인마다 만들었었다. 그러다보니 구현체의 기능과 소스코드가 동일한 상태에서 도메인만 바뀐 `DaoImpl` 클래스가 계속 생겨났다.
그리고 이 구현체들을 `ClientApp`에서 컴파일 시점에 주입하도록 만들었다. 

![](https://raw.githubusercontent.com/zhtmr/static-files-for-posting/86c762a09ac25be54594c256caff216706a8145b/20240117/previous-dao.png){: .align-center}
*도메인이 새로 생기면 인터페이스와 구현체도 새로 만들어야했다.*

![](https://github.com/zhtmr/static-files-for-posting/blob/main/static-files-for-posting/20240117/injection.png?raw=true){: .align-center}
*각 도메인 레퍼런스 타입에 맞는 dao 인스턴스를 직접 주입해줘야 했다.*



## newProxyInstance
```java
// java.lang.reflect.Proxy.class
public static Object newProxyInstance(ClassLoader loader, Class<?>[] interfaces, InvocationHandler h)
```
`java.lang.reflect.Proxy` 클래스에는 `newProxyInstance` 라는 정적 팩토리 메소드가 존재하는데 런타임 시점에 파라미터로 넘겨준 하나 이상의 인터페이스를 구현하는 동적 프록시 인스턴스를 만들어 반환해 준다.

파라미터:
- **loader**: 프록시 클래스를 정의하는 클래스 로더. 프록시 클래스를 동적으로 로드하는 역할을 담당한다.
- **interfaces**: 자동 생성할 클래스가 구현해야 하는 인터페이스 목록. 배열 타입이다.
- **h (InvocationHandler)**: `InvocationHandler` 구현체를 넣어준다. 프록시 인스턴스를 전달받은 `Handler` 객체가 CRUD 메소드를 호출할 때마다 호출된다.


## stub (client proxy Dao)
```java
public class DaoProxyGenerator {

  private String host;
  private int port;
  private Gson gson;

  public DaoProxyGenerator(String host, int port) {
    this.host = host;
    this.port = port;
    gson = new GsonBuilder().setDateFormat("yyyy-MM-dd").create();
  }

  public <T> T create(Class<T> clazz, String dataName) {
    return (T) Proxy.newProxyInstance(DaoProxyGenerator.class.getClassLoader(),
      new Class<?>[] {clazz}, (proxy, method, args) -> {
        // 서버에 요청할 때마다 연결한다.
        try (Socket socket = new Socket(host, port);
          DataInputStream in = new DataInputStream(socket.getInputStream());
          DataOutputStream out = new DataOutputStream(socket.getOutputStream())) {
          out.writeUTF(dataName);
          out.writeUTF(method.getName());
          if (args == null) {
            out.writeUTF("");
          } else {
            out.writeUTF(gson.toJson(args[0]));
          }

          String code = in.readUTF();
          String entity = in.readUTF();

          if (!code.equals("200")) {
            throw new Exception(entity);
          }

          Type returnType = method.getGenericReturnType();

          if (returnType == void.class) {
            return null;
          } else {
            return gson.fromJson(entity, returnType);
          }
        } catch (Exception e) {
          e.printStackTrace();
          throw new DaoException(e);
        }
      });
  }
}
```
기존에 종속성을 주입하는 과정과 다른점은 클라이언트가 직접 인스턴스를 생성하지 않는다는 것이다. 

`DaoProxyGenerator` 라는 클래스의 정적 팩토리 메소드에서 런타임 시점에 인스턴스를 생성해 반환해 준다. 이런 방식을 취함으로써 좀 더 낮은 결합도를 갖게 되었고, `dao` 객체 생성 로직을 하나의 클래스에 모두 캡슐화 함으로써 높은 응집도를 갖게 되었다. (low coupling, high cohesion) 

만약 상호작용(상속, 포함, 구현 등)하는 객체들이 많아지면 개발자가 그 모든 관계를 일일이 기억하고 주입해 준다는 것은 불가능에 가깝다.

스프링 프레임워크는 이러한 고민을 리플렉션과 프록시를 통해 해결한다. 스프링에서 DI(Dependency Injection)는 스프링 IoC 컨테이너에서 이루어지는데, 애플리케이션이나 클래스가 아니라 외부 컨테이너에서 주입된다. 
복잡한 의존 객체에 대한 라이프사이클을 스프링에게 위임할 수 있는 것이다. 

프록시는 AOP(Aspect-Oriented Programming) 및 런타임 시 동적으로 기능을 제공하려는 기타 다양한 경우와 같은 시나리오에서 유용하다.

## skeleton (ServerApp)
```java
// ServerApp.class
public class ServerApp {
    ...
  
  // skeleton method
  void processRequest(DataInputStream in, DataOutputStream out) throws IOException {
    System.out.println("[클라이언트 요청]");
    String dataName = in.readUTF();
    String command = in.readUTF();
    String value = in.readUTF();

    try {
      Object dao = daoMap.get(dataName);
      if (dao == null) {
        throw new RequestException("요청 데이터가 없습니다!");
      }
      System.out.printf("데이터: %s\n", dataName);

      Method commandHandler = findMethod(dao.getClass(), command);
      System.out.printf("메서드: %s\n", commandHandler.getName());

      Object[] args = getArguments(commandHandler, value);

      // 메소드를 호출한다.
      Object returnValue = commandHandler.invoke(dao, args);

      out.writeUTF("200");
      out.writeUTF(gson.toJson(returnValue));
      System.out.println("클라이언트에게 응답 완료!");

    } catch (RequestException e) {
      out.writeUTF("400");
      out.writeUTF(gson.toJson(e.getMessage()));

    } catch (Exception e) {
      out.writeUTF("500");
      out.writeUTF(gson.toJson(e.getMessage()));
    }
  }
}
```
skeleton(ServerApp) 은 `Dao` 구현체들을 미리 `Map` 에 담아뒀다가 stub 객체로부터 마샬링 데이터가 전달되면 리플렉션을 통해 호출해야 될 Dao 객체의 메소드를 찾아서 호출한다.


## 현재 프로젝트 구조

{:.no_toc}
### app-api
```
app-api
└── src
    └── main
        ├── java
        │   └── bitcamp
        │       └── myapp
        │           └── dao
        │               └── DaoProxyGenerator.java
        └── resources
└── build.gradle

8 directories, 2 files
```

{:.no_toc}
### app-common
```
app-common
└── src
    └── main
        ├── java
        │   └── bitcamp
        │       └── myapp
        │           ├── dao
        │           │   ├── AssignmentDao.java
        │           │   ├── BoardDao.java
        │           │   ├── DaoException.java
        │           │   └── MemberDao.java
        │           └── vo
        │               ├── Assignment.java
        │               ├── Board.java
        │               └── Member.java
        └── resources
└── build.gradle

9 directories, 8 files
```

{:.no_toc}
### app-server
```
app-server
└── src
    └── main
        ├── java
        │   └── bitcamp
        │       ├── RequestException.java
        │       └── myapp
        │           ├── ServerApp.java
        │           └── dao
        │               └── json
        │                   ├── AbstractDao.java
        │                   ├── AssignmentDaoImpl.java
        │                   ├── BoardDaoImpl.java
        │                   └── MemberDaoImpl.java
        └── resources
├── assignment.json
├── board.json
├── build.gradle
├── greeting.json
└── member.json

9 directories, 11 files
```

{:.no_toc}
### app-client
```
app-client
└── src
    └── main
        ├── java
        │   └── bitcamp
        │       ├── menu
        │       │   ├── AbstractMenu.java
        │       │   ├── AbstractMenuHandler.java
        │       │   ├── Menu.java
        │       │   ├── MenuGroup.java
        │       │   ├── MenuHandler.java
        │       │   └── MenuItem.java
        │       ├── myapp
        │       │   ├── ClientApp.java
        │       │   └── handler
        │       │       ├── HelpHandler.java
        │       │       ├── assignment
        │       │       │   ├── AssignmentAddHandler.java
        │       │       │   ├── AssignmentDeleteHandler.java
        │       │       │   ├── AssignmentListHandler.java
        │       │       │   ├── AssignmentModifyHandler.java
        │       │       │   └── AssignmentViewHandler.java
        │       │       ├── board
        │       │       │   ├── BoardAddHandler.java
        │       │       │   ├── BoardDeleteHandler.java
        │       │       │   ├── BoardListHandler.java
        │       │       │   ├── BoardModifyHandler.java
        │       │       │   └── BoardViewHandler.java
        │       │       └── member
        │       │           ├── MemberAddHandler.java
        │       │           ├── MemberDeleteHandler.java
        │       │           ├── MemberListHandler.java
        │       │           ├── MemberModifyHandler.java
        │       │           └── MemberViewHandler.java
        │       └── util
        │           ├── AnsiEscape.java
        │           └── Prompt.java
        └── resources
└── build.gradle

13 directories, 26 files
```

## 좀 더 찾아볼 내용
스프링에서 프록시 객체를 생성하는 방법
- JDK Dynamic Proxy
- CGLib

## reference
{% capture notice-2 %}
- [stub/skeleton](https://vascocenter.tistory.com/entry/%EB%B6%84%EC%82%B0%EA%B0%9C%EC%B2%B4-%EC%95%A0%ED%94%8C%EB%A6%AC%EC%BC%80%EC%9D%B4%EC%85%98%EC%97%90%EC%84%9C%EC%9D%98-%EC%8A%A4%ED%85%81stub-%EC%8A%A4%EC%BC%88%EB%A0%88%ED%86%A4Skeleton)
{% endcapture %}

<div class="notice">{{ notice-2 | markdownify }}</div>


