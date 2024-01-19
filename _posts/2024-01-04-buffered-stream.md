---
published: true
layout: single
title:  "[Java] BufferedInputStream / BufferedOutputStream"
excerpt: ""
categories:
  - Java
tags:
  - ['Java', 'Refactoring']
use_math: true
---

> - [이전 글](https://zhtmr.github.io/java/file-io-stream/)에 이어서 파일 입출력 성능을 개선해본다.
> - 버퍼(buffer)를 사용해야 하는 이유를 알아본다.

# FileInputStream / FileOutputStream 을 그대로 사용 시 문제점
![](/assets/images/20240104/hdd-4313739_640.jpg){: .align-center}
*Hdd*

파일에 읽고 쓰는 작업을 하는 `write()`와 `read()`는 JNI(Java Native Interface)를 통해 직접 OS의 API를 호출해 하드웨어를 제어한다고 했다.
읽고 쓰는 작업이 증가하면 이 API 호출 횟수 또한 증가하게 되고, 이는 **하드웨어(HDD)에 접근하는 횟수 또한 증가한다는 것이다.**

문제는 HDD의 동작방식에 있다. 전통적인 하드 디스크는 데이터를 디스크에 읽고 쓸때 물리적으로 움직이는 시간이 필요한데 다음의 세가지 요소들의 총 합으로 결정된다.
- seek time : hdd의 arm이 데이터를 읽고 쓰기 위해 적절한 위치까지 이동하는데 걸리는 시간
- rotational time : arm의 head 아래로 디스크를 회전시켜 이동시키는데 걸리는 시간
- transfer time : 디스크에 데이터의 총 길이만큼 읽고 쓰는 시간

`write()`, `read()`를 계속해서 호출하게 되면 위의 과정이 반복적으로 일어난다.
만약 어플리케이션에서 이런 방식으로 데이터의 입출력을 다룬다면 I/O-burst 상황이 생기며, I/O 작업을 하는 동안 서비스는 blocking 상태에 있게 된다. 

스레드수를 늘려 I/O-bound 문제를 회피한다고 해도, 이렇게 직접 Hdd에 읽고/쓰는 방식은 금방 한계에 부딪힐 것이다.
왜냐하면 Java의 스레드도 마찬가지로 JNI를 호출해 OS의 스레드를 이용하는데, 
스레드가 늘어날수록 CPU 작업(CPU-bound)과 I/O 작업(I/O-bound) 간의 race condition 상황([context switching](https://bit.ly/3RQ1SLE))이 자주 발생해 전체적인 퍼포먼스가 떨어진다.


데이터 입출력 시간을 줄이는 것의 핵심은 **hdd에 접근하는 횟수를 최대한 줄이는 것**이다.

> Java 21에서 스레드의 컨텍스트 스위칭 비용을 최소화하기 위해 [virtual thread](https://techblog.woowahan.com/15398/) 가 도입되었다.


{: .notice--info }
💡 HDD는 디스크에 기록된 자성의 세기가 1년에 1% 감소하고, SSD는 전원이 인가되지 않은 상태에서는 셀의 누설전류로 인해 빠르면 1년 이내에 데이터 손실이 일어날 수 있다고 한다.


# 버퍼(buffer) 사용
Hdd 에 직접 읽고 쓰는 JNI(Java Native Interface) 호출 빈도를 최대한 줄이기 위해 데이터를 미리 일정한 크기의 버퍼에 담아 두었다가 버퍼가 가득 차면 Hdd 에 write하거나 read 하도록 수정한다.
기존에 사용하던 `DataInputStream` 과 `DataOutputStream` 을 각각 상속해 버퍼 기능이 추가된 클래스를 만든다.
![](/assets/images/20240105/diagram2.png){: .align-center}


![](/assets/images/20240104/buffer.png){: .align-center}
*buffer에 모았다가 한번에 내보낸다.*

{:.no_toc}
## BufferedDataInputStream
```java
public class BufferedDataInputStream extends DataInputStream {

  private final byte[] buf = new byte[8192];
  int size; // 읽은 바이트 수
  int cursor; // 버퍼 인덱스

  public BufferedDataInputStream(String name) throws FileNotFoundException {
    super(name);
  }

  @Override
  public int read() throws IOException {
    if (cursor == size) {
      cursor = 0;
      size = super.read(buf);  // 읽은 바이트 수를 리턴한다.
      if (size == -1) {
        return -1; // 읽을 데이터가 없다.
      }
    }
    return buf[cursor++] & 0xFF;  // sign-magnitude 방식으로 읽어야 한다. 
    // byte -> int 형변환시 음수로 바뀔 경우를 위해 `AND 비트 연산`한다.
  }

  @Override
  public int read(byte[] arr) throws IOException {
    return read(arr, 0, arr.length);
  }

  @Override
  public int read(byte[] arr, int off, int len) throws IOException {
    for (int i = off, count = 0; count < len; count++, i++) {
      int b = read();
      if (b == -1) {
        return count > 0 ? count : -1;  // 읽은 데이터가 없으면 -1을 리턴해야한다.
      }
      arr[i] = (byte) b;
    }
    return len;
  }
}
```
먼저 데이터를 임시로 담아둘 공간(`buf`)을 선언한다. 이때 데이터를 최대한 많이 담겠다고 버퍼의 크기를 무지막지하게 늘리면 안된다.
서버프로그램은 여러 사람이 동시에 접속해 사용하게 되는데 버퍼의 크기가 크면 그만큼 메모리 사용량이 많아진다. (접속자 수 * 버퍼 size)

- \`**size = super.read(buf)**\`: 최초 메소드 호출 시 부모 클래스(`FileInputStream`)의 `read`메소드를 통해 버퍼에 데이터를 읽어오고, 실제로 읽은 바이트 수를 `size`변수에 저장한다.
그리고 읽은 데이터가 없다면(EOF) `size`에 -1을 리턴하고 이를 그대로 리턴하면서 메소드를 종료한다. 
- \`**return buf[cursor++] & 0xFF**\`: 읽은 데이터가 있다면 현재 커서가 위치한 버퍼의 값을 반환하고, 커서를 증가시킨다. 
이때 버퍼의 레퍼런스 타입(byte)과 메소드 리턴타입(int) 간의 타입이 문제가 된다.  
byte를 읽은 후 int 메모리에 저장할때 앞 3byte가 비어있는 상태가 되는데 만약 읽어들인 byte가 [sign-magnitude 방식](https://bit.ly/3tGy63W)에 의해 `7f`(0111 1111)를 넘어가게 되면(맨 앞자리가 1이 되면) 
음수로 간주하고 2의 보수를 취한다. 이는 우리가 얻고자 하는 데이터가 아닌 다른 값이 된다. **byte 를 읽은 그대로 반환하기 위해** `FF`(1111 1111)와 `&`연산을 하게되면 유효한 값이 그대로 출력된다.

{:.no_toc}
## BufferedDataOutputStream
```java
public class BufferedDataOutputStream extends DataOutputStream {

  private final byte[] buf = new byte[8192]; // 8kb
  int size;

  public BufferedDataOutputStream(String name) throws FileNotFoundException {
    super(name);
  }

  @Override
  public void write(int b) throws IOException {
    if (size == buf.length) {
      // 버퍼가 모두 찼다면, 버퍼에 저장된 데이터를 파일로 출력한다.
      flush();
    }
    buf[size++] = (byte) b;
  }

  @Override
  public void write(byte[] bytes) throws IOException {
    for (byte b : bytes) {
      if (size == buf.length) {
        flush();
      }
      buf[size++] = b;
    }
  }

  // 버퍼에 저장된 데이터를 파일로 출력한다.
  public void flush() throws IOException {
    super.write(buf, 0, size);
    size = 0;
  }

  // try-with-resources 구문에서 자동 호출되는 메서드이다.
  @Override
  public void close() throws IOException {
    // 출력 스트림을 닫기전에 버퍼에 남아있는 데이터를 파일로 출력한다.
    flush();
    super.close();
  }
}
```
`FileInputStream` 의 `write()`를 호출해 Hdd로부터 1byte씩 읽어오는 방식이 아니라 버퍼의 현재 데이터가 들어있는 사이즈 만큼씩 읽는다.

호출부(App)에서는 인스턴스 구현부만 바꿔주면 된다. 이제 wrapper class(`DataOutputStream, DataInputStream 클래스`)에 전달되는 인스턴스는 `write()`, `read()`를 재정의해서 버퍼기능이 추가된 인스턴스가 된다.


![](/assets/images/20240104/buffered-stream.png){: .align-center}
*버퍼를 사용하도록 메소드 재정의*


## 성능 비교
위에서 구현한 `DataInputStream` 그리고 `BufferedDataInputStream` 테스트 시 
데이터 400만개(72Mb) 기준 

읽기
- **DataInputStream**: 32.7초
- **BufferedDataInputStream**: 12.1초

쓰기
- **DataOutputStream**: 56.2초
- **BufferedDataOutputStream**: 0.4초

## reference
{% capture notice-2 %}
- [hdd 저장기간](https://eshop.macsales.com/blog/43702-we-bet-you-didnt-know-that-your-hdds-or-ssds-may-need-exercise-too/)
- [data seek time](https://www.lifewire.com/what-does-seek-time-mean-2626007)
- [hdd 구조](https://bubble-dev.tistory.com/entry/%ED%95%98%EB%93%9C%EB%94%94%EC%8A%A4%ED%81%AC-%EA%B5%AC%EC%A1%B03-%EB%B9%84%EC%9A%A9)
{% endcapture %}

<div class="notice">{{ notice-2 | markdownify }}</div>


