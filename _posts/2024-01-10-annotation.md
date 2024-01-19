---
published: true
layout: single
title:  "[Java] 어노테이션(annotation)을 활용해 세션 정보 가져오기"
excerpt: ""
categories:
  - Java
tags:
  - Java
use_math: true
---

# 어노테이션 유지정책
어노테이션을 언제까지 유지할 것인가

## CLASS(default)
```java
@Retention(value=RetentionPolicy.CLASS)
public @interface MyAnnotation {
  String value() default "기본값사용";   // 어노테이션 사용하는 쪽에서 따로 값 설정 없이 기본값으로 사용.
}
```
컴파일 과정까지 유지하겠다. `.class` 파일에 어노테이션을 포함한다. 바이트코드로 어노테이션 확인 가능. 그러나 런타임에 메모리에 로딩되지 않기 때문에 리플렉션 API로 알아낼 수 없다.

## SOURCE
```java
@Retention(value=RetentionPolicy.SOURCE)
public @interface MyAnnotation {
  String value();
}
```
소스 파일에만 남긴다. `.class` 파일에 포함 안된다. 컴파일 시 제거된다. 바이트코드로 확인 불가능하다.

## RUNTIME
```java
@Retention(value=RetentionPolicy.RUNTIME)
public @interface MyAnnotation3 {
  String value();
}
```
`.class` 파일에도 포함되고, 실행할 때도 메모리에 로딩된다. 그렇기 때문에 리플렉션으로 정보를 알아낼 수 있다.

## 리플렉션으로 어노테이션 정보 가져오기

```java
@MyAnnotation
public class MyClass {
  
}
```
```java
Class<?> clazz = MyClass.class;
clazz.getAnnotation(MyAnnotation.class);
```

# 어노테이션 적용 범위
`@Target`을 사용하여 애노테이션을 붙일 수 있는 범위를 제어할 수 있다.

| 종류                                                                    | 범위                   |
|-----------------------------------------------------------------------|----------------------|
| `ElementType.TYPE`                                                      | 클래스, 인터페이스에 붙일 수 있다. |
| `ElementType.FIELD`                                                     | 필드 선언 앞에 붙인다.        |
| `ElementType.METHOD`                                                    | 메소드 선언 위에 붙인다.       |
| `ElementType.LOCAL_VARIABLE`                                            |로컬 변수 앞에 붙인다.|
| `{ElementType.LOCAL_VARIABLE, ElementType.PARAMETER, ElementType.FIELD}` | 배열 형태로 여러군데서 사용하게 할 수 있다.|

```java
@Target({ElementType.LOCAL_VARIABLE, ElementType.PARAMETER, ElementType.FIELD})
public @interface MyAnnotation {
}
```


# 어노테이션 활용
`RetentionPolicy.RUNTIME` 유지 정책을 가진 어노테이션을 활용하면 실행중인 어플리케이션에서 특정 정보를 추출할 수 있다. 
아래와 같이 로그인한 유저의 세션(httpSession) 체크를 어노테이션 기반으로 바꿀 수 있다.

## 유저 세션 정보 확인
```java
@Target(ElementType.PARAMETER)
@Retention(RetentionPolicy.RUNTIME)
public @interface LoginUser {

}
```
우선 어노테이션을 정의한다. 해당 어노테이션을 파라미터 앞에 붙일 수 있도록 `@Target`을 지정하고, 
런타임 시에도 메모리 상에 어노테이션 정보가 유지되도록 `@Retention` 범위를 지정한다. 이를 통해 리플렉션으로 어노테이션 정보를 가져올 수 있다. 

이제 어노테이션을 이용해 컨트롤러로 넘어오는 DTO(Data Transfer Object) 객체를 검증하게 된다.

### HandlerMethodArgumentResolver
```java
@RequiredArgsConstructor
@Component
public class LoginUserArgumentResolver implements HandlerMethodArgumentResolver {

    private final HttpSession httpSession;

    @Override
    public boolean supportsParameter(MethodParameter parameter) {
        // 파라미터에 LoginUser 어노테이션이 붙어 있는가?
        boolean isLoginUserAnnotation = parameter.getParameterAnnotation(LoginUser.class) != null;
        // 파라미터 타입이 SessionUser 인가?
        /* if(parameter.getParameterType == LoginUser.class) {return true} */
        boolean isUserClass = SessionUser.class.equals(parameter.getParameterType());
        // 둘다 참일 경우 true 반환
        return isLoginUserAnnotation && isUserClass;
    }

    @Override
    public Object resolveArgument(MethodParameter parameter, ModelAndViewContainer mavContainer, 
      NativeWebRequest webRequest, WebDataBinderFactory binderFactory) throws Exception {

        // 위 supportsParameter 메소드 true 이면 실행
        return httpSession.getAttribute("user");
    }
}
```
`HandlerMethodArgumentResolver`를 구현하면 컨트롤러 진입 시 파라미터를 전처리 할 수 있다. 위 코드에서는 유저 정보를 받는 DTO 객체의 어노테이션 타입을 확인하고,
메소드의 현재 파라미터 타입이 `SessionUser`인지 확인한다. 맨위에서 정의한 어노테이션의 규칙에 맞는지 다시 확인하는 것이다. 
`supportsParameter`가 true 를 리턴하게되면, `resolveArgument`에서 실제 세션 정보를 가져온다.

#### WebConfig
```java
@RequiredArgsConstructor
@Configuration
public class WebConfig implements WebMvcConfigurer {
  private final LoginUserArgumentResolver loginUserArgumentResolver;
  private final UserAgentArgumentResolver userAgentArgumentResolver;

  @Override
  public void addArgumentResolvers(List<HandlerMethodArgumentResolver> resolvers) {
    resolvers.add(loginUserArgumentResolver);
    resolvers.add(userAgentArgumentResolver);
  }
}
```
위에서 정의한 `HandlerMethodArgumentResolver`구현체를 앱 시작 시 인식하기 위해 `WebMvcConfigurer`인터페이스를 구현해 넣어준다.

#### IndexController
```java
@RequiredArgsConstructor
@Controller
public class IndexController {

  private final PostsService postsService;
  private final HttpSession httpSession;  // 이제 세션에서 바로 꺼내지 않고 어노테이션을 이용해 꺼낸다.

  @GetMapping("/")
  public String index(Model model, @LoginUser SessionUser user, @UserInfo String useragent) {
    model.addAttribute("posts", postsService.findAllDesc());
    // 로그인한 유저 세션 가져오기
    //  -> 어노테이션 기반(LoginUserArgumentResolver) 으로 변경 시 컨트롤러로 전달되는 파라미터에서(user) 모두 검증이 끝난 상태로 가져옴.
    //     - 파라미터는 세션에서 가져옴(resolveArgument 메소드 리턴 부분. httpsession.getAttribute)
    //     - 정의한 어노테이션이 붙어있는지 / 타입 체크.

    //        SessionUser user = (SessionUser) httpSession.getAttribute("user");

    if (user != null) {
      model.addAttribute("userName", user.getName());
    }
    model.addAttribute("userAgent", useragent);
    return "index";
  }
```

로그인 한 유저가 인덱스 페이지 접근 시 간단하게 어노테이션으로 세션 정보를 가져올 수 있다. 
```java
  ... 
HttpServletRequest req = (HttpServletRequest) webRequest.getNativeRequest();
req.getHeader("User-Agent");
```
세션 정보뿐만 아니라 접속 정보 등을 가져오는 코드를 resolver 에 등록해 사용할 수도 있다.



## reference
{% capture notice-2 %}
- [스프링 부트와 AWS로 혼자 구현하는 웹 서비스](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=218568947&start=slayer)
{% endcapture %}

<div class="notice">{{ notice-2 | markdownify }}</div>


