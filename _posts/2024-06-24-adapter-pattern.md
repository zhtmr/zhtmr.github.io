---
published: true
layout: single
title:  "[디자인패턴] 어댑터 패턴(Adapter Pattern)"
excerpt: ""
categories:
  - Design Pattern
tags:
  - ['Design Pattern', 'Java', 'Refactoring']
use_math: true
---

# 어댑터 패턴
![](https://zhtmr.github.io/static-files-for-posting/images/20240624/%EC%96%B4%EB%8C%91%ED%84%B0%ED%8C%A8%ED%84%B4_%EC%82%AC%EC%A7%841.png?raw=true)
*출처: https://refactoring.guru/ko/design-patterns/adapter*

## 정의
기존 코드를 클라이언트가 사용하는 인터페이스의 구현체로 바꿔주는 패턴
- 클라이언트가 사용하는 인터페이스를 따르지 않는 기존 코드를 재사용할 수 있게 해준다.

## 주요 구성 요소
![](https://zhtmr.github.io/static-files-for-posting/images/20240624/adapter-pattern.drawio.png?raw=true){: .align-center}


클라이언트는 `Target` 인터페이스에만 의존한다. 그리고 기존에 사용하던 코드(`Adaptee`)와 `Target` 사이에 `Adapter`라는 구현체가 있다. 여기서 `Adapter` 의 역할은 기존에 사용하던 코드를 클라이언트가 의존하는 타입의 객체로 **변환시켜 주는 역할**을 한다.

## 어댑터 패턴 적용 전
![img.png](https://zhtmr.github.io/static-files-for-posting/images/20240624/%ED%8C%A8%ED%82%A4%EC%A7%80%EA%B5%AC%EC%A1%B0.png?raw=true){: .align-center}
*어댑터 패턴 적용 전 패키지 구조*


<details>
<summary>적용 전 코드보기</summary>
<div markdown="1">

### LoginHandler
{:.no_toc}

```java
public class LoginHandler {

    UserDetailsService userDetailsService;

    public LoginHandler(UserDetailsService userDetailsService) {
        this.userDetailsService = userDetailsService;
    }

    public String login(String username, String password) {
        UserDetails userDetails = userDetailsService.loadUser(username);
        if (userDetails.getPassword().equals(password)) {
            return userDetails.getUsername();
        } else {
            throw new IllegalArgumentException();
        }
    }
}
```
### UserDetails
{:.no_toc}

```java
public interface UserDetails {

    String getUsername();

    String getPassword();

}

```
### UserDetailsService
{:.no_toc}

```java
public interface UserDetailsService {

    UserDetails loadUser(String username);

}
```

### Account
{:.no_toc}

```java
public class Account {

    private String name;

    private String password;

    private String email;

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

}
```

### AccountService
{:.no_toc}

```java
public class AccountService {

    public Account findAccountByUsername(String username) {
        Account account = new Account();
        account.setName(username);
        account.setPassword(username);
        account.setEmail(username);
        return account;
    }

    public void createNewAccount(Account account) {

    }

    public void updateAccount(Account account) {

    }

}

```
</div>
</details>

코드를 간략하게 살펴보면, `UserDetails` 인터페이스는 유저의 이름과 비밀번호를 가져오는 기능을 하고, `UserDetailsService` 는 유저의 이름을 받아 그 유저 정보를 반환하는 역할을 하고있다.

기존에는 `AccountService` 를 통해 유저 정보를 가져왔는데, 앱을 개선하는 과정에서 새로운 방식으로(`LoginHandler`) 호출해야 하는 상황에 놓인 것이다.

예를 들어 security 패키지(외부 라이브러리라고 가정)를 우리 프로젝트에 통합하여 쓰고자 한다.  
이제부터 클라이언트는 `UserDetailService` 를 통해 데이터를 가져와야 한다고 하면 기존의 코드를 변경하지 않고 어떻게 새로운 방식과 통합할 수 있을까?

그러기 위해 먼저 서로 호환되지 않는 `AccountService` 와 `UserDetailsService` 를 연결해야 하고, `Account` 와 `UserDetails` 를 연결해야 한다.


## 어댑터 패턴 적용 하기

기존의 코드(Adaptee) 를 Target 타입에 맞게 변형해주는 클래스(Adapter)를 정의해야 한다.

Adapter 클래스는 Adaptee 를 포함하도록 만든다.

<details>
<summary>적용 후 코드보기</summary>
<div markdown="1">


### AccountUserDetailsService

`UserDetails` 구현체에서 기존에 쓰던 `AccountService` 객체를 사용하도록 한다.
이 객체는 기존 서비스의 반환값을 Target 인터페이스 규격에 맞춰 반환 하는 역할을 한다.

```java
public class AccountUserDetailsService implements UserDetailsService {

    private AccountService accountService;

    public AccountUserDetailsService(AccountService accountService) {
        this.accountService = accountService;
    }

    @Override
    public UserDetails loadUser(String username) {
        return new AccountUserDetails(accountService.findAccountByUsername(username));
    }
}
```

### AccountUserDetails

```java
public class AccountUserDetails implements UserDetails {

    private Account account;

    public AccountUserDetails(Account account) {
        this.account = account;
    }

    @Override
    public String getUsername() {
        return account.getName();
    }

    @Override
    public String getPassword() {
        return account.getPassword();
    }
}
```

### Client

```java
public class App {

    public static void main(String[] args) {
        AccountService accountService = new AccountService();
        UserDetailsService userDetailsService = new AccountUserDetailsService(accountService);
        LoginHandler loginHandler = new LoginHandler(userDetailsService);
        String login = loginHandler.login("keesun", "keesun");
        System.out.println(login);
    }
}
```
</div>
</details>

Adaptee 를 호출해 나온 결과를 클라이언트가 원하는 타입인 Target 타입으로 바꿔주는 역할을 하는것이 Adapter 다.

## 장점과 단점
- 장점
  - 기존 코드를 변경하지 않고 원하는 인터페이스 구현체를 만들어 재사용 가능. (OCP)
  - 기존 코드가 하던 일과 특정 인터페이스 구현체로 변환하는 작업을 각기 다른 클래스로 분리하여 관리할 수 있다. (SRP)

- 단점
  - 새 클래스가 생겨 복잡도가 증가할 수 있다.

## 자바에서 찾아보는 어댑터 패턴
### Arrays.asList()
배열 형태(`...args`형태의 가변인자 포함)를 파라미터로 받아 List 타입을 반환한다.
```java
List<String> strings = Arrays.asList("a", "b", "c");
```

![](https://zhtmr.github.io/static-files-for-posting/images/20240624/adapter_in_java.png?raw=true)

### Enumeration()
```java
// list to enumeration
Enumeration<String> enumeration = Collections.enumeration(strings);
// enumeration to list
ArrayList<String> list = Collections.list(enumeration);
```

### io package
```java
// io
try(InputStream is = new FileInputStream("input.txt");
    InputStreamReader isr = new InputStreamReader(is);
    BufferedReader reader = new BufferedReader(isr)) {
    while(reader.ready()) {
        System.out.println(reader.readLine());
    }
} catch (IOException e) {
    throw new RuntimeException(e);
}
```

## 스프링에서 찾아보는 어댑터 패턴
### HandlerAdapter
Spring MVC 에는 `DispatcherServlet` 이라는 프론트 컨트롤러 역할을 하는 핸들러 클래스가 있다.
내부 메소드 중 각 상황에 맞는 핸들러를 선택하는 메소드가 있는데 이 부분에 어댑터 패턴이 적용되어 있다.

<details>
<summary>doDispatch 메소드 살펴보기</summary>
<div markdown="1">


### DispatcherServlet - doDispatch
```java
protected void doDispatch(HttpServletRequest request, HttpServletResponse response) throws Exception {
  HttpServletRequest processedRequest = request;
  HandlerExecutionChain mappedHandler = null;
  boolean multipartRequestParsed = false;
  WebAsyncManager asyncManager = WebAsyncUtils.getAsyncManager(request);

  try {
    try {
      ModelAndView mv = null;
      Exception dispatchException = null;

      try {
        processedRequest = this.checkMultipart(request);
        multipartRequestParsed = processedRequest != request;
        mappedHandler = this.getHandler(processedRequest);
        if (mappedHandler == null) {
          this.noHandlerFound(processedRequest, response);
          return;
        }

        // 최근 요청에 맞는 적절한 어댑터를 가져온다.
        HandlerAdapter ha = this.getHandlerAdapter(mappedHandler.getHandler());
        String method = request.getMethod();
        boolean isGet = "GET".equals(method);
        if (isGet || "HEAD".equals(method)) {
          long lastModified = ha.getLastModified(request, mappedHandler.getHandler());
          if ((new ServletWebRequest(request, response)).checkNotModified(lastModified) && isGet) {
            return;
          }
        }

        if (!mappedHandler.applyPreHandle(processedRequest, response)) {
          return;
        }

        // 어댑터를 실행해 Target 타입으로 변환한다.
        mv = ha.handle(processedRequest, response, mappedHandler.getHandler());
        if (asyncManager.isConcurrentHandlingStarted()) {
          return;
        }

        this.applyDefaultViewName(processedRequest, mv);
        mappedHandler.applyPostHandle(processedRequest, response, mv);
      } catch (Exception var20) {
        Exception ex = var20;
        dispatchException = ex;
      } catch (Throwable var21) {
        Throwable err = var21;
        dispatchException = new NestedServletException("Handler dispatch failed", err);
      }

      this.processDispatchResult(processedRequest, response, mappedHandler, mv, (Exception)dispatchException);
    } catch (Exception var22) {
      Exception ex = var22;
      this.triggerAfterCompletion(processedRequest, response, mappedHandler, ex);
    } catch (Throwable var23) {
      Throwable err = var23;
      this.triggerAfterCompletion(processedRequest, response, mappedHandler, new NestedServletException("Handler processing failed", err));
    }

  } finally {
    if (asyncManager.isConcurrentHandlingStarted()) {
      if (mappedHandler != null) {
        mappedHandler.applyAfterConcurrentHandlingStarted(processedRequest, response);
      }
    } else if (multipartRequestParsed) {
      this.cleanupMultipart(processedRequest);
    }

  }
}
```
</div>
</details>

해당 메소드 중간에 보면
```java
HandlerAdapter ha = this.getHandlerAdapter(mappedHandler.getHandler());
```
이런 코드가 있는데, 해당 요청에 맞는 핸들러를 처리할 수 있는 어댑터를 가져오는 코드다.
그 후 적합한 어댑터를 통해 `ModelAndView` 객체를 반환하는 코드가 있다.

```java
mv = ha.handle(processedRequest, response, mappedHandler.getHandler());
```
어댑터의 `handle` 메소드의 결과로 Target 타입(ModelAndView) 를 반환한다.
다양한 종류의 핸들러에 대해 일관된 방식으로 `ModelAndView`를 반환해 준다.

해당 메소드를 들어가보면 어댑터 용 인터페이스가 있다.
```java
public interface HandlerAdapter {
  boolean supports(Object var1);

  @Nullable
  ModelAndView handle(HttpServletRequest var1, HttpServletResponse var2, Object var3) throws Exception;

  long getLastModified(HttpServletRequest var1, Object var2);
}
```
그리고 그 중 요청에 대해 @RequestMapping 어노테이션을 처리하는 핸들러인 `RequestMappingHandlerAdapter` 이 있다는 것을 알 수 있다.

![](https://zhtmr.github.io/static-files-for-posting/images/20240624/HandlerAdapter.png?raw=true){: .align-center}
*다양한 종류의 요청을 처리하는 핸들러가 있다.*




## 어댑터 패턴 vs. 데코레이터 패턴
아래는 어댑터 패턴과 데코레이터 패턴을 간략하게 비교한 것이다.

<details>
<summary>차이점 비교 클릭</summary>
<div markdown="1">

### 어댑터 패턴 (Adapter Pattern)

**정의**: 어댑터 패턴은 호환되지 않는 인터페이스를 가진 클래스를 호환되도록 변환해주는 패턴.
주로 기존 클래스를 재사용하면서도 인터페이스가 맞지 않을 때 사용한다.

**목적**: 기존 클래스의 인터페이스를 원하는 인터페이스로 변환하여 서로 호환되지 않는 인터페이스를 가진 클래스들이 함께 동작할 수 있게 한다.

**구조**:

- *타깃 인터페이스(Target Interface)*: 클라이언트가 사용하고자 하는 인터페이스.
- *어댑터(Adapter)*: 타깃 인터페이스를 구현하고 어댑티(Adaptee)의 메소드를 호출하여 변환을 수행.
- *어댑티(Adaptee)*: 어댑터에 의해 변환되는 기존 클래스.

### 데코레이터 패턴 (Decorator Pattern)
**정의**: 데코레이터 패턴은 객체에 동적으로 새로운 행동을 추가할 수 있게 해주는 패턴. 상속을 통해 기능을 확장하는 대신 데코레이터 객체를 통해 기능을 추가한다.

**목적**: 객체의 기능을 동적으로 확장할 수 있도록 하며, 상속보다 유연한 기능 확장을 제공한다.

**구조**:

- *컴포넌트(Component)*: 기본 인터페이스로, 데코레이터와 구체 컴포넌트가 구현한다.
- *구체 컴포넌트(Concrete Component)*: 기본 기능을 구현하는 클래스.
- *데코레이터(Decorator)*: 컴포넌트 인터페이스를 구현하며, 컴포넌트 객체를 포함한다. 추가적인 기능을 정의할 수 있다.
- *구체 데코레이터(Concrete Decorator)*: 데코레이터 클래스를 확장하여 구체적인 기능을 추가한다.

</div>
</details>


어댑터 패턴을 공부하면서 데코레이터 패턴과 비슷하다는 느낌을 받았다.
합성이라는 방식(멤버변수)으로 클래스를 확장하고 있기 때문에 그렇게 느꼈던 것 같다.

보는 시각에 따라 어댑터패턴이 될 수도 있고, 데코레이터패턴이 될 수도 있다. 목적에 따라 분류를 해보자면, **기존 코드와의 호환**에 목적이 있다면 **어댑터패턴**으로 볼 수 있고,
기존코드의 **기능을 확장**한다는 개념으로 본다면 **데코레이터 패턴**으로 볼 수 있다.

예를 들어, 위에서 예시로 든 `AccountUserDetailsService` 나 `AccountUserDetails` 와 같은 어댑터를 새로 만들지 않고 기존의 클래스에 Target 타입을 구현하는 방향으로 간다면 새로운 기능을 추가하는 개념으로 볼 수도 있는 것이다.

```java
public class AccountService implements UserDetailService{

    public Account findAccountByUsername(String username) {
        Account account = new Account();
        account.setName(username);
        account.setPassword(username);
        account.setEmail(username);
        return account;
    }

    public void createNewAccount(Account account) {

    }

    public void updateAccount(Account account) {

    }
    
    // 새롭게 추가된 기능
    @Override
    public UserDetail loadUser(String username) {
      return findAccountByUsername(username);
    }

}
```

각각의 방법은 장단점이 있어 프로젝트의 상황을 고려해 선택하면 될 것 같다.

## 디자인패턴에 대한 생각
사실 디자인패턴 이라는 것은 특정한 상황을 효율적으로 해결하기 위한 말 그대로 일종의 패턴들에 불과하기 때문에
패턴 자체에 매몰되기 보다는 각 패턴의 특징을 이해한 후, 지금 나의 상황에 맞는 적절한 패턴을 선택할 수 있는 시야를 갖는 것이 더 중요하다고 생각한다.
그러기 위해선 다양한 예제를 접하면서 왜 해당 패턴을 사용했을까에 대해 스스로 충분히 고민해보는 시간을 가져야 할 것 같다.
