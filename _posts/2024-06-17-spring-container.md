---
published: true
layout: single
title:  "[Spring] bean"
excerpt: ""
categories:
  - Spring
tags:
  - ['Spring', 'Spring Boot']
use_math: true
---

> - 
> 
> 

# 스프링 Bean 으로 등록하는 방법
## 컴포넌트 스캔 방식
보통 스프링에서 객체를 bean 으로 등록할때, 아래 코드처럼 `@Bean` 을 통해 등록하는 클래스를 만들고 스프링이 컴포넌트 스캔할 수 있도록 `@Configuration`을 붙이면 된다.


```java
@Configuration
public class Config {
  @Bean
  public DispatcherServlet dispatcherServlet() {
    return new DispatcherServlet();
  }

  @Bean
  public ServletWebServerFactory servletWebServerFactory() {
    return new TomcatServletWebServerFactory();
  }
}
```

## 자동 구성정보 (AutoConfiguration)
우선 애플리케이션에서 사용이 될 수 있는 Infrastructure bean 을 담은 `@Configuration` 클래스들을 만들어 둔다.

위의 코드를 예시로 들자면, 서블릿 컨테이너를 생성 하는데 필요한 팩토리 bean 을 담고 있는 구성 정보와, 스프링 웹을 사용하기 위해 필요한 DispatcherServlet bean 을 생성하는 구성정보를 만들어 둔다.
![img_3.png](https://github.com/zhtmr/static-files-for-posting/blob/main/static-files-for-posting/20240622/img_3.png?raw=true){: .align-center}
*구성정보를 담고 있는 클래스들을 만든다.*

애플리케이션의 필요에 따라 configuration 구성정보를 골라 자동으로 구성해준다. 


구성정보를 어떤 방식으로 만드느냐 -> 컴포넌트 스캔 / 자동 구성정보(AutoConfiguration)