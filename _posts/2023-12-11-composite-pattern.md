---
published: true
layout: single
title:  "[디자인패턴]컴포지트 패턴(Composite Pattern)"
excerpt: ""
categories:
  - Design Pattern
tags:
  - Design Pattern
use_math: true
---

# 컴포지트 패턴(Composite pattern)

> 컴포지트 패턴에 대해 알아보고, 도입 전과 후의 차이점을 알아봅니다. 
 

다음과 같이 구현된 메뉴 출력 프로그램이 있다.

```
  [ 메인 메뉴 ]
  1. 과제
  2. 게시글
  3. 회원
  4. 가입인사
  5. 도움말
  0. 종료
```
메인 메뉴에서 해당 번호를 누르면 서브메뉴가 출력된다. 
예를들어 사용자로 부터 2를 입력받아 게시글 메뉴로 들어가면 아래와 같은 메뉴가 출력된다.

```
  [ 게시글 ]
  1. 등록
  2. 조회
  3. 변경
  4. 삭제
  5. 목록
  0. 이전
```

---

## Before
각각의 메뉴 클래스에 입력을 받는 소스코드가 존재하고 그 입력을 처리하는 과정도 각각의 메뉴 클래스에 구현되어 있다.

### MainMenu.class

```java
  public class MainMenu {
  
      ...
  
    Menu assignmentMenu = new AssignmentMenu("과제", this.prompt);
    Menu boardMenu = new BoardMenu("게시글", this.prompt);
    Menu greetingMenu = new BoardMenu("가입인사", this.prompt);
    Menu memberMenu = new MemberMenu("회원", this.prompt);
    Menu helpMenu = new HelpMenu("도움말", this.prompt);
    
    printMenu(); // 메인메뉴 출력
  
    while(true) {
    String input = this.prompt.input("메인> ");

      switch (input) {
        case "1":
          assignmentMenu.execute(prompt);
          break;
        case "2":
          boardMenu.execute(prompt);
          break;
        case "3":
          memberMenu.execute(prompt);
          break;
        case "4":
          greetingMenu.execute(prompt);
          break;
        case "5":
          helpMenu.execute(prompt);
          break;
        case "0":
          System.out.println("종료합니다.");
          return;
        case "menu":
          this.printMenu();
          break;
        default:
          System.out.println("메뉴 번호가 옳지 않습니다.");
      }
    } 
  }
```

### BoardMenu.class

```java
public class BoardMenu {

  public void execute(Prompt prompt) {
  
      ...

    Board[] boards = new Board[3]; // 게시글 저장할 배열
    int length = 0; // 현재 게시글 저장 인덱스

    this.printMenu(); // 서브메뉴 출력

    while (true) {
      String input = prompt.input("메인/%s> ", this.title);

      switch (input) {
        case "1":
          this.add();
          break;
        case "2":
          this.view();
          break;
        case "3":
          this.modify();
          break;
        case "4":
          this.delete();
          break;
        case "5":
          this.list();
          break;
        case "0":
          return;
        case "menu":
          this.printMenu();
          break;
        default:
          System.out.println("메뉴 번호가 옳지 않습니다!");
      }
    }

    void add () {
      // 게시글 등록  
    }

    void list () {
      // 게시글 목록
    }

    void view () {
      // 게시글 상세조회  
    }

    void modify () {
      // 게시글 수정
    }

    void delete () {
      // 게시글 삭제
    }
  }
}
```
위 소스코드 처럼 `switch` 문으로 입력 데이터에 대한 분기처리를 각 메뉴 클래스마다 시행하고 있다.
새로운 메뉴가 추가될 때마다 `MainMenu` 에 서브메뉴 인스턴스를 생성해야하고 `case` 를 추가해야 한다. 
그리고 현재 코드는 모든 서브메뉴 클래스가 중복 코드를 다수 포함하고 있다. (switch 로 입력을 처리하는 부분, CRUD 기능)
또한 메뉴클래스가 서로 계층구조를 가지고 있음에도, 이것이 코드상에 잘 표현이 되지 않는다.

데이터 그 자체를 핸들링 하는 소스코드는 유지보수하기 힘들고 객체지향 패러다임과는 맞지 않다.
컴포지트 패턴은 [SOLID 객체지향 원리](https://ko.wikipedia.org/wiki/SOLID_(%EA%B0%9D%EC%B2%B4_%EC%A7%80%ED%96%A5_%EC%84%A4%EA%B3%84)) 중 OCP(Open/Closed Principle) 를 만족한다.


---

## After
기존의 `switch` 로 데이터를 입력 받아서 메뉴를 호출하는 방식이 아닌, 
메뉴를 `상위메뉴 객체`와 `하위 메뉴 객체`로 캡슐화 하고 객체끼리 상호작용하도록 수정한다.
`폴더`와 `파일`의 구조처럼 계층적인 트리구조의 형식을 취한다.

![img.png](/assets/images/classdiagram.png) 

우선 `Menu`인터페이스를 구현해 `MenuGroup`과 `MenuItem`을 공통적으로 처리할 수 있게 만든다.
`MenuGroup` 은 반복적으로 `Menu`를 가질 수 있다. 즉, `MenuGroup` 또는 `MenuItem` 을 가질 수 있다.(`add()` 로 배열에 추가)

데이터를 이런식으로 조직화하다 보면 복합객체(MenuGroup)를 따라서 가지가 연결되다가 마지막에는 잎(MenuItem)으로 끝나는 트리구조가 만들어진다.

### MenuGroup.class
```java
public class MenuGroup implements Menu {

  String title;
  Menu[] menus = new Menu[10];
  int menuSize;

  public MenuGroup(String title) {
    this.title = title;
  }

  public void add(Menu menu) {
    // menus 배열에 서브메뉴를 넣는다
  }

  public void remove(Menu menu) {
    // menus 배열에서 서브메뉴 삭제
  }
  
  @Override
  public void execute(Prompt prompt) {
    this.printMenu();
    // 메뉴 번호 입력 및 메뉴 출력
    // menus 배열에 있는 서브메뉴 실행(execute)
    
  }
}
```
기존 소스에서는 `add()`,`remove()` 와 같이 메뉴를 추가하고 삭제하는 기능이 각각의 메뉴에 존재했다.
이제 새로운 메뉴를 만드는 작업은 `MenuGroup`에서 한다.
`MenuGroup`에서 서브클래스 요소들을 관리하기 위한 `menus` 배열이 있고 해당 배열에 추가/삭제는 `add()`, `remove()`를 통해서 한다.

### MenuItem
```java

public class MenuItem implements Menu {

  String title;
  MenuHandler menuHandler;

  public MenuItem(String title) {
    this.title = title;
  }

  public MenuItem(String title, MenuHandler menuHandler) {
    this(title);
    this.menuHandler = menuHandler;
  }

  @Override
  public void execute(Prompt prompt) {
    if (this.menuHandler != null) {
      this.menuHandler.action();
    }
  }

  @Override
  public String getTitle() {
    return this.title;
  }
```
컴포지트 패턴에서 leaf 에 해당하는 부분이다. leaf 부분은 CRUD 작업에 대한 `MenuHandler` 를 주입받아 사용한다.
이는 기존에 메뉴 객체에 섞여있던 `메뉴 출력`과 `CRUD 기능` 부분을 분리시키기 위함이다.

### Client
```java

public class Client {
  public static void main(String[] args) {
    ...

    Prompt prompt = new Prompt(System.in);
    //    new MainMenu(prompt).execute(); 
    BoardRepository boardRepository = new BoardRepository();

    MenuGroup mainMenu = new MenuGroup("메인");
    MenuGroup assignmentMenu = new MenuGroup("과제");
    MenuGroup boardMenu = new MenuGroup("게시글");
    MenuGroup memberMenu = new MenuGroup("회원");
    MenuGroup greetingMenu = new MenuGroup("가입인사");
    MenuGroup helpMenu = new MenuGroup("도움말");

    mainMenu.add(assignmentMenu);
    assignmentMenu.add(new MenuItem("등록"));
    assignmentMenu.add(new MenuItem("조회"));
    assignmentMenu.add(new MenuItem("변경"));
    assignmentMenu.add(new MenuItem("삭제"));
    assignmentMenu.add(new MenuItem("목록"));

    mainMenu.add(boardMenu);
    boardMenu.add(new MenuItem("등록", new BoardAddHandler(boardRepository, prompt)));
    boardMenu.add(new MenuItem("조회", new BoardViewHandler()));
    boardMenu.add(new MenuItem("변경", new BoardModifyHandler()));
    boardMenu.add(new MenuItem("삭제", new BoardDeleteHandler()));
    boardMenu.add(new MenuItem("목록", new BoardListHandler(boardRepository)));
  }
}
```
컴포지트 패턴을 사용하는 경우 사용자가 단일 객체와 복합 객체 모두 동일하게 다룰 수 있다. 
기존에 `new MainMenu(prompt).execute()` 로 각 메뉴들을 호출했다면 이제는 메뉴의 종속관계가 코드상에 확실히 표현되고, 추가/삭제를 간편히 할 수 있다.