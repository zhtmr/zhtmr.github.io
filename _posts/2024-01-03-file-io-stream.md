---
published: true
layout: single
title:  "[Java] FileInputStream / FileOutputStream"
excerpt: ""
categories:
  - Java
tags:
  - ['Java', 'Refactoring']
use_math: true
---
> [이전 글](https://zhtmr.github.io/design%20pattern/iterator-pattern/)에서는 이터레이터 패턴을 이용해 메뉴관리를 개선해봤다.
> 이번 글에서는 데이터 저장/조회를 메모리가 아닌 파일에 쓰고/읽도록 변경해 본다.

현재 메모리 상에서 `List` 구현체에 저장하는 로직만 있기때문에 데이터가 영속성을 갖지 않는다. 프로그램이 종료되면 메모리에 올라가 있던 데이터가 지워진다.
이 부분을 아래 그림처럼 파일에 저장되도록 수정해보자.

![](/assets/images/20240103/data-persist.png){: .align-center}
*파일로부터 데이터를 읽어들인다.*

파일 입출력을 구현하기 전에, 먼저 각 메뉴에 대한 데이터 입출력을 편하게 다루기 위해 `App` 클래스 소스코드를 정리한다. 
현재 `App`클래스는 아래와 같이 main 메소드에 실행 순서에 따라 작성되어 있다. 

# App 클래스 리팩토링
## before 
```java
public class App {

  public static void main(String[] args) throws Exception {
    Prompt prompt = new Prompt(System.in);

    // 현재 소스에서는 List 에 저장하고 있다.
    List<Board> boardRepository = new LinkedList<>();
    List<Assignment> assignmentRepository = new LinkedList<>();
    List<Member> memberRepository = new ArrayList<>();
    List<Board> greetingRepository = new ArrayList<>();
    
    // 메인 메뉴
    MenuGroup mainMenu = MenuGroup.getInstance("메인");

    // 과제 메뉴
    MenuGroup assignmentMenu = mainMenu.addGroup("과제");
    assignmentMenu.addItem("등록", new AssignmentAddHandler(assignmentRepository, prompt));
    assignmentMenu.addItem("조회", new AssignmentViewHandler(assignmentRepository, prompt));
    assignmentMenu.addItem("변경", new AssignmentModifyHandler(assignmentRepository, prompt));
    assignmentMenu.addItem("삭제", new AssignmentDeleteHandler(assignmentRepository, prompt));
    assignmentMenu.addItem("목록", new AssignmentListHandler(assignmentRepository, prompt));

    // 게시글 메뉴
    // 가입인사 메뉴
    // 회원 메뉴
    // 도움말 메뉴
    
    while (true) {
      try {
        mainMenu.execute(prompt);
        prompt.close();
        break;
      } catch (Exception e) {
        System.out.println("main() 예외 발생");
      }
    }

  }
}
```

역할에 따라 메소드로 구분하고 메소드 호출로 동작하도록 수정해보자. 
구현을 단순화 하기 위해 프로그램이 종료될때 파일에 출력하고, 프로그램이 시작될때 파일을 모두 읽어 메모리에 로딩하기로 한다.

## after
```java
public class App {

  Prompt prompt = new Prompt(System.in);
  List<Board> boardRepository = new LinkedList<>();
  List<Assignment> assignmentRepository = new LinkedList<>();
  List<Member> memberRepository = new ArrayList<>();
  List<Board> greetingRepository = new ArrayList<>();
  MenuGroup mainMenu;
  
  // 생성자가 호출되는 시점에 파일에서 데이터 로딩한다.
  App() {
    prepareMenu();
    loadAssignment();
    loadMember();
    loadBoard();
    loadGreeting();
  }

  void prepareMenu() {
    // 메인 메뉴
    mainMenu = MenuGroup.getInstance("메인");

    // 과제 메뉴
    MenuGroup assignmentMenu = mainMenu.addGroup("과제");
    assignmentMenu.addItem("등록", new AssignmentAddHandler(assignmentRepository, prompt));
    assignmentMenu.addItem("조회", new AssignmentViewHandler(assignmentRepository, prompt));
    assignmentMenu.addItem("변경", new AssignmentModifyHandler(assignmentRepository, prompt));
    assignmentMenu.addItem("삭제", new AssignmentDeleteHandler(assignmentRepository, prompt));
    assignmentMenu.addItem("목록", new AssignmentListHandler(assignmentRepository, prompt));

    // 게시글 메뉴
    // 가입인사 메뉴
    // 회원 메뉴
    // 도움말 메뉴
  }
  
  void run() {
    while (true) {
      try {
        mainMenu.execute(prompt);
        prompt.close();
        break;
      } catch (Exception e) {
        System.out.println("main() 예외 발생");
      }
    }
    // 프로그램 종료 시 파일에 데이터 저장
    saveAssignment();
    saveMember();
    saveBoard();
    saveGreeting();
  }
  
  /* 아래 메소드들을 통해 파일 입출력을 다룬다. */
  void saveAssignment() {
      ...
  }
  
  void loadAssignment() {
      ...
  }
  
  void saveMember() {
      ...
  }
  
  void loadMember() {
      ...
  }
  
  void saveBoard() {
      ...
  }
  
  void loadBoard() {
      ...
  }

  void saveGreeting() {
      ...
  }
  
  void loadGreeting() {
      ...
  }
  
  public static void main(String[] args) throws Exception {
    new App().run();  // App 생성자 호출
  }
}
```
`run()`메소드가 종료되기 전에 각 메뉴에서 `List`구현체에 저장했던 데이터들을 파일에 저장하도록 하고, 
프로그램 시작 시 `App`클래스 생성자를 호출해 데이터를 불러오는 메소드를 최초 호출하도록 수정한다.

# FileOutputStream
파일에 데이터를 출력하기위해 `FileOutputStream`를 사용한다. 생성자에 String 타입으로 파일명을 지정해 줄 수 있다.
파일에 데이터를 저장할 때는 `byte`(8 bit)단위로 읽어 저장한다.

```java
void saveAssignment() {
  try (FileOutputStream out = new FileOutputStream("assignment.data")) {

    // 추후 파일에서 데이터 로딩 시 데이터 갯수를 for 횟수로 사용하기 위해 미리 파일에 기록해둔다. 
    out.write(assignmentRepository.size() >> 8);
    out.write(assignmentRepository.size());

    for (Assignment assignment : assignmentRepository) {
      byte[] bytes = assignment.getTitle().getBytes(StandardCharsets.UTF_8);
      // byte갯수를 2바이트로 출력
      out.write(bytes.length >> 8);
      out.write(bytes.length);
      out.write(bytes);

      bytes = assignment.getContent().getBytes(StandardCharsets.UTF_8);
      out.write(bytes.length >> 8);
      out.write(bytes.length);
      out.write(bytes);

      out.write(assignment.getDeadline().toString().getBytes(StandardCharsets.UTF_8));
    }
  } catch (Exception e) {
    System.out.println("과제 데이터 저장 중 오류 발생!");
    e.printStackTrace();
  }
}
```

1. **전체 데이터의 갯수를 미리 파일에 기록해 둔다. 데이터 로딩 시(`loadAssignment()`) 반복 횟수로 사용된다.**
```java
  out.write(assignmentRepository.size() >> 8);
  out.write(assignmentRepository.size());
```
`FileOutputStream`의 `write()`는 한가지 재밌는 점이 있는데, 파라미터로 `int` 타입(4byte)을 받지만 실제로 쓰이는건 **맨 끝 1 byte**만 사용된다는 것이다.
이는 옛날 C언어에서 파일 입출력을 다룰때의 API spec을 그대로 계승했기 때문이다. 실제로 JVM은 내부적으로 [JNI](https://bit.ly/48BV9vC)를 이용해 OS 의 API를 호출한다.
이는 의도적으로 대부분의 언어에서 파일입출력 방식을 통일시키기 위함으로 보인다.([스택오버플로우에도 비슷한 질문이 올라온다.](https://bit.ly/3S500Ac))


   ![img.png](/assets/images/20240103/write-jni.png){: .align-center}
*FileOutputStream 의 write()는 내부적으로 OS API를 호출한다.*

   `size()`가 1 byte를 넘어갈 경우를 대비해 `write()`가 충분한 크기(2byte)를 읽게 한다.

2. **title, content 의 정보를 읽어와 byte 배열로 변환한다.**
```java
  byte[] bytes = assignment.getTitle().getBytes(StandardCharsets.UTF_8);
  // byte갯수를 2바이트로 출력
  out.write(bytes.length >> 8);
  out.write(bytes.length);   
  out.write(bytes);
```
이때도 마찬가지로 각 항목의 글자수를 함께 파일에 기록해 둔다. `write([] byte)`을 사용하면 바이트 배열 전체를 기록한다.
`getDeadline()`의 경우 `java.sql.Date` 타입인데, 이는 `toString()`을 호출하면 `yyyy-mm-dd`형식으로 반환되기 때문에 따로 글자수를 지정할 필요가 없어 날짜를 다루기 편하다.



# FileInputStream
파일에 입력한 데이터를 읽기위해 `FileInputStream`를 사용한다. 생성자에 String 타입으로 읽어 들일 파일명을 지정해 줄 수 있다.
마찬가지로 `byte`(8 bit)단위로 읽어온다.
```java
void loadAssignment() {
  try (FileInputStream in = new FileInputStream("assignment.data")) {
    byte[] bytes = new byte[60000];
    int size = in.read() << 8 | in.read();

    for (int i = 0; i < size; i++) {
      int len = in.read() << 8 | in.read();
      in.read(bytes, 0, len);
      String title = new String(bytes, 0, len, StandardCharsets.UTF_8);

      len = in.read() << 8 | in.read();
      in.read(bytes, 0, len);
      String content = new String(bytes, 0, len, StandardCharsets.UTF_8);

      // 날짜는 10 byte 만 읽는다
      in.read(bytes, 0, 10);
      Date deadline = Date.valueOf(new String(bytes, 0, 10, StandardCharsets.UTF_8));

      Assignment assignment = new Assignment();
      assignment.setTitle(title);
      assignment.setContent(content);
      assignment.setDeadline(deadline);

      assignmentRepository.add(assignment);
    }
  } catch (Exception e) {
    System.out.println("과제 데이터 로딩 중 오류 발생!");
    e.printStackTrace();
  }

}
```
1. **파일에 저장 시 맨 처음 2byte에 입력한 데이터 전체 갯수(`size()`)를 지정했으므로 이를 읽어온다.**
```java
int size = in.read() << 8 | in.read();
```
8bit 왼쪽 이동 비트 연산의 결과와 마지막 비트의 OR 연산을 이용하면 총 2byte를 읽어올 수 있다.

    ```
       0101
    OR 0011
     = 0111
    ```

2. **size만큼 반복문을 돌면서 데이터의 자릿수 만큼 가져온다.**
```java
  int len = in.read() << 8 | in.read();
  in.read(bytes, 0, len);  // 읽어온 만큼 버퍼에 기록한다.
```
파일에 입력 시 데이터 갯수의 사이즈를 먼저 입력하고 데이터를 입력했으므로 입력한 데이터의 길이를 알 수 있다.
읽어 온 데이터의 길이를 `len`변수에 재할당하면서 계속 읽어나간다. 
이를 버퍼(`byte[] bytes = new byte[60000]`)에 임시 저장했다가 바로 String 객체로 읽어 변환한다. 그리고 버퍼는 계속 재사용 된다.
날짜의 경우 형식이 항상 정해져 있기 때문에 10byte만 읽는다.(`yyyy-mm-dd`)

    읽어온 데이터는 메모리에 로딩 시킨다.(`assignmentRepository.add(assignment)`)

# 데이터 입출력 흐름
![](/assets/images/20240103/io-flow.png){: .align-center}
*데이터 흐름*

# DataOutputStream / DataInputStream (wrapper class 구현) 
이전 코드에서 `FileOutputStream` 과 `FileInputStream` 을 이용해 파일 입출력을 다루면서 불편한 점이 있었는데, 
그건 바로 *byte 형식으로 데이터를 다룬다는 것*이다. 파일 입출력 시 바이트 하나하나 읽어오는 코드를 여기저기 중복으로 작성해야 했다.
이런 부분을 대신할 클래스(`wrapper class`) 를 만들어보자.

## DataOutputStream
```java
public class DataOutputStream extends FileOutputStream {
  public DataOutputStream(String name) throws FileNotFoundException {
    super(name);
  }

  // 2 byte 출력하기
  public void writeShort(int value) throws IOException {
    write(value >> 8);
    write(value);
  }

  // 4 byte 출력하기
  public void writeInt(int value) throws IOException {
    write(value >> 24);
    write(value >> 16);
    write(value >> 8);
    write(value);
  }

  // 8 byte 출력하기
  public void writeLong(long value) throws IOException {
    write((int) (value >> 56));
    write((int) (value >> 48));
    write((int) (value >> 40));
    write((int) (value >> 32));
    write((int) (value >> 24));
    write((int) (value >> 16));
    write((int) (value >> 8));
    write((int) value);
  }

  // 문자열 출력
  public void writeUTF(String value) throws IOException {
    byte[] bytes = value.getBytes(StandardCharsets.UTF_8);
    writeShort(bytes.length);
    write(bytes);
  }

  public void writeBoolean(boolean value) throws IOException {
    if (value) {
      write(1);
    } else {
      write(0);  // 실제로는 0x00 또는 0x01 이다. 즉, 논리값 출력.
    }
  }
}
```
기존에 비즈니스 로직에서 비트 이동 연산을 하던 코드를 추출해 메소드안에서 작업하도록 만들었다. 이로 인해 클라이언트 코드가 간결해 진다.


### saveAssignment
```java
void saveAssignment() {
  try (DataOutputStream out = new DataOutputStream("assignment.data")) {

    // 저장할 데이터 갯수를 2바이트로 출력한다.
    out.writeShort(assignmentRepository.size());

    for (Assignment assignment : assignmentRepository) {
      out.writeUTF(assignment.getTitle());
      out.writeUTF(assignment.getContent());
      out.writeUTF(assignment.getDeadline().toString());
    }
  } catch (Exception e) {
    System.out.println("과제 데이터 저장 중 오류 발생!");
    e.printStackTrace();
  }
}
```
파라미터로 데이터만 전달해주면 바이트를 하나씩 이동하면서 파일에 쓰는 작업은 메소드 내부에서 한다.

## DataInputStream
```java
public class DataInputStream extends FileInputStream {
  public DataInputStream(String name) throws FileNotFoundException {
    super(name);
  }

  public short readShort() throws IOException {
    return (short) (read() << 8 | read());
  }

  public int readInt() throws IOException {
    return (read() << 24 | read() << 16 | read() << 8 | read());
  }

  public long readLong() throws IOException {
    return ((long) read() << 56 | 
      (long) read() << 48 | 
      (long) read() << 40 | 
      (long) read() << 32 | 
      (long) read() << 24 | 
      (long) read() << 16 | 
      (long) read() << 8 | 
      (long) read());
  }

  public boolean readBoolean() throws IOException {
    return read() == 1; // 0이면 false, 1이면 true 리턴한다.
  }

  public String readUTF() throws IOException {
    int len = read() << 8 | read();
    byte[] buf = new byte[60000];
    read(buf, 0, len);
    return new String(buf, 0, len, StandardCharsets.UTF_8);
  }
}
```

### loadAssignment
```java
void loadAssignment() {
  try (DataInputStream in = new DataInputStream("assignment.data")) {
    int size = in.readShort();

    for (int i = 0; i < size; i++) {
      Assignment assignment = new Assignment();
      assignment.setTitle(in.readUTF());
      assignment.setContent(in.readUTF());
      assignment.setDeadline(Date.valueOf(in.readUTF()));
      assignmentRepository.add(assignment);
    }
  } catch (Exception e) {
    System.out.println("과제 데이터 로딩 중 오류 발생!");
    e.printStackTrace();
  }
}
```

## 소스코드
[소스코드](https://github.com/zhtmr/mystudy/tree/main/myapp)


추후에 데코레이터패턴을 이용해 결합도 낮추기, 버퍼사용해 성능 개선, 객체 직렬화 등을 적용해 본다.

