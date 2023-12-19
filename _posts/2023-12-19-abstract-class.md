---
published: true
layout: single
title:  "[Java] Abstract 클래스가 Interface 를 구현하게 하기"
excerpt: ""
categories:
  - Java
tags:
  - ['refactoring', 'java']
use_math: true
mermaid: true
---

> [이전 글](../design%20pattern/composite-pattern/)에서 계층구조를 가지는 메뉴에 컴포지트 패턴을 적용해봤다. 이번 글에서는 추상클래스를 적용해 공통기능 추출 및 자동화 해본다.

# 문제
현재까지 작업한 소스에서 `BoardAddHandler`, `BoardDeleteHandler`, `BoardListHandler`, `BoardViewHandler`, `BoardModifyHandler` 등 각 도메인의 핸들러마다 공통으로 중복되는 소스코드가 있다.

```java
  public class BoardAddHandler implements MenuHandler {

  ...

  @Override
  public void action(Menu menu) {
    System.out.printf(AnsiEscape.ANSI_BOLD + "[%s]\n" + AnsiEscape.ANSI_CLEAR, menu.getTitle());

    ...
  }
}
```
인터페이스에 정의된 `action(Menu menu)` 추상메소드를 구현해서 재정의 했지만 아직 중복코드가 남아 있는 상태다.
이 부분을 추출하고자 한다.


![](/assets/images/12-19/classdiagram.png){: .align-center}
*클래스 다이어그램*

위 클래스 다이어그램 처럼 concrete class(구상클래스) 에서 직접적으로 인터페이스를 구현하지 않고 중간에 부모 클래스가 일부 구현하게 한다. (Generalization)
그리고 구상 클래스는 부모클래스를 상속받는다.
이는 인터페이스에 정의된 추상메소드가 많은 경우 구상클래스에서 메소드 재정의를 해야하는 부담을 줄여준다.

## AbstractMenuHandler
```java
  public class AbstractMenuHandler implements MenuHandler {
  
    protected Menu menu;
  
    @Override
    public void action(Menu menu) {
      this.printMenuTitle(menu.getTitle());
    }
  
    private void printMenuTitle(String title) {
      System.out.printf(AnsiEscape.ANSI_BOLD + "[%s]\n" + AnsiEscape.ANSI_CLEAR, title);
    }
  
  }
```

각 핸들러에서 중복되는 코드를 추출해 부모클래스에서 구현하도록 했다.

## BoardAddHandler
```java
  public class BoardAddHandler extends AbstractMenuHandler {

    private ArrayList<Board> objectRepository;
    private Prompt prompt;
  
    public BoardAddHandler(ArrayList<Board> objectRepository, Prompt prompt) {
      this.prompt = prompt;
      this.objectRepository = objectRepository;
    }
  
    @Override
    protected void action(Menu menu) { // MenuHandler 인터페이스 추상메소드 재정의
      super.action(menu) // 부모클래스에 일부 구현된 action 메소드 호출
      Board board = new Board();
      board.setTitle(this.prompt.input("제목? "));
      board.setContent(this.prompt.input("내용? "));
      board.setWriter(this.prompt.input("작성자? "));
      board.setCreatedDate(this.prompt.input("작성일? "));
  
      objectRepository.add(board);
    }
  }
```
구상클래스에서는 기존 메소드에 `super.action(menu)` 를 추가해 부모 클래스에 정의된 공통 소스코드를 호출하게 한 후 이어서 작업하게된다.
이전보다 좀 더 객체지향 스러워지긴 했으나 여전히 문제가 남아있다.

메소드를 재정의하는 과정에서 `super.action(menu)` 을 필수로 호출해야 한다. 개발자가 실수로 작성하지 않는 경우를 미연에 방지할 수가 없다.

## 수정된 AbstractMenuHandler
```java
  public abstract class AbstractMenuHandler implements MenuHandler {
    
    protected Prompt prompt; // 이것도 구상클래스에서 공통적으로 쓰이므로 추상클래스에서 세팅하도록 한다.
    protected Menu menu;

    public AbstractMenuHandler(Prompt prompt) {
      this.prompt = prompt;
    }
    
    @Override
    public void action(Menu menu) {
      this.printMenuTitle(menu.getTitle());
      this.menu = menu; // 서브클래스 구현 시 사용할 일이 있으면 쓸 수 있도록 보관해 둔다.
      
      // Menu 를 실행할 때 이 메소드가 호출되면 즉시 서브 클래스의 action() 메소드를 호출한다.
      this.action();
    }
  
    private void printMenuTitle(String title) {
      System.out.printf(AnsiEscape.ANSI_BOLD + "[%s]\n" + AnsiEscape.ANSI_CLEAR, title);
    }

    // 서브클래스가 구현해야 할 메소드. 외부에서 호출할 메소드가 아니다(protected)
    protected abstract void action(); 
}
```
`AbstractMenuHandler` 에 `action()` 추상 메소드를 정의하고 추상 클래스로 변경했다. 
그리고 기존 인터페이스에서 구현한 `action(Menu menu)` 에서 이 메소드를 호출하게 한다.

## 수정된 BoardAddHandler
```java
  public class BoardAddHandler extends AbstractMenuHandler {

  private ArrayList<Board> objectRepository;

  public BoardAddHandler(ArrayList<Board> objectRepository, Prompt prompt) {
    super(prompt);
    this.objectRepository = objectRepository;
  }

  @Override
  protected void action() { // AbstractMenuHandler 추상메소드 재정의
    Board board = new Board();
    board.setTitle(this.prompt.input("제목? "));
    board.setContent(this.prompt.input("내용? "));
    board.setWriter(this.prompt.input("작성자? "));
    board.setCreatedDate(this.prompt.input("작성일? "));

    objectRepository.add(board);
  }
}
```
`AbstractMenuHandler` 를 상속받은 클래스는 추상메소드를 필수적으로 구현해야 한다.

기존에는 `MenuHandler` 인터페이스를 직접 구현해 사용했지만 수정된 코드에서는 인터페이스와 구상클래스 중간에 있는 `AbstractMenuHandler` 의 메소드를 재정의해서 사용하게 된다.

### 실행흐름
### As-is
```shell
  App 클래스에서 메뉴 호출(execute())
                  ⬇︎
  MenuItem 의 action(menu) 실행
                  ⬇︎
  MenuHandler 를 구현한 BoardAddHandler 에서 action(menu) 실행
```

### To-be
```shell
  App 클래스에서 메뉴 호출(execute())
                  ⬇︎
  MenuItem 의 action(menu) 실행
                  ⬇︎
  MenuHandler 를 구현한 AbstractMenuHandler 에서 action(menu) 실행
                  ⬇︎
  AbstractMenuHandler 를 상속받은 BoardAddHandler 에서 action() 실행
```

기존의 `MenuHandler 를 구현한 BoardAddHandler 에서 action(menu) 실행` 이 부분을 분리한 것이라 보면 된다.
