---
published: true
layout: single
title:  "[DB] connection 을 공유하면 생기는 문제"
excerpt: ""
categories:
  - 
tags:
  - 
use_math: true
---


# connection 공유 시 발생하는 문제
Phantom-Read 가능성

## 트랜잭션 관리가 안됨


# Solution
## 1. 쿼리마다 하나의 connection 을 가지게 하기
Phantom-Read 가능성을 회피하고자 쿼리마다 새로운 connection 을 가지도록 수정

### 문제1. 인증/인가 작업에 시간 소요
DB Connection 을 얻기 위해 매번 mysql 에 로그인을 하는 것과 같다.

### 문제2. 트랜잭션 관리가 안됨
각 쿼리마다 서로 다른 트랜잭션 격리를 가진다. 
일련의 과정을 하나의 작업으로 처리해야 하는 경우(트랜잭션) commit/rollback 이 일괄적으로 이루어져야 하는데, 이런 방식이라면 각 쿼리마다 commit/rollback 을 따로 해줘야 한다. 
만약 이 과정이 동기화 되지 않을 경우 치명적이다. 
 

-> connection 을 query 단위로 생성하는게 아니라 thread 단위로 가지게 해야한다.

## 2. 스레드 당 커넥션 하나씩 생성하는 방법
**스레드마다 커넥션을 하나씩 할당한다.**
위 방식에선 쿼리 실행 시 커넥션이 생성되기 때문에 각각의 커넥션을 하나의 트랜잭션으로 관리하기가 어려웠다.
이를 해결하기 위해 `ThreadLocal` 을 이용해 실행 중인 스레드의 커넥션을 저장한다.
`ThreadLocal` 은 내부에 `ThreadLocalMap` 을 가지고 있고 key, value 형식으로 현재 실행중인 스레드 이름과 Connection 객체를 저장한다.
유저마다 고유한 커넥션 객체를 가지게 되는 셈이다.

![img_1.png](https://raw.githubusercontent.com/zhtmr/static-files-for-posting/9ca54cbd0f0758d40aeef18766184ec2aef25982/20240213/threadLocal.png){: .align-center}
*ThreadLocal*

### 문제1. 접속 유저 수(스레드 수) 만큼 커넥션 수도 증가한다

아래 코드처럼 `ThreadLocal` 내에 커넥션 객체가 없을 경우 새로 만든다.
```java
// ThreadConnection.java

// 스레드에 커넥션 객체가 없을 경우 새로 만든다.
public Connection getConnection() throws SQLException {
  Connection con = connectionThreadLocal.get();
  if (con == null) {
    con = DriverManager.getConnection(url, username, password)
    System.out.printf("%s: db 커넥션 생성\n", Thread.currentThread().getName());
    connectionThreadLocal.set(con);
  } else {
    System.out.printf("%s: 기존에 보관했던 커넥션 사용\n", Thread.currentThread().getName());
  }
}

// 스레드에서 커넥션 객체를 제거한다.
public void remove() {
  Connection con = connectionThreadLocal.get();
  if (con != null) {
    try {con.close();} catch (Exception e) {}
    connectionThreadLocal.remove();
    System.out.printf("%s: db 커넥션 제거\n", Thread.currentThread().getName());
  }
}
```

mysql console 에서 `SHOW PROCESSLIST` 로 현재 연결된 connection 목록을 볼 수 있다. 생성된 스레드 수 만큼 커넥션이 생성된다.

![img_1.png](https://github.com/zhtmr/static-files-for-posting/blob/main/20240213/processlist.png?raw=true)

![img_2.png](https://github.com/zhtmr/static-files-for-posting/blob/main/20240213/serverapp-log.png?raw=true)

## 3. Thread pool
**커넥션을 재사용 한다.**   
2번 방식의 문제는 커넥션 생성 갯수에 제한이 없다는 것이다. 스레드 수와 커넥션 수가 비례한다.
유저가 접속할때 스레드와 함께 커넥션이 생성되고, 종료 시 `remove()` 메소드를 통해 스레드에 할당된 커넥션을 제거할 수 있지만, `remove()` 를 호출하지 않는다면 DB 커넥션 타임아웃 설정에 따라 기존에 생성된 커넥션을 계속 유지하고 있다.
쿼리 작업을 하지 않고 있어도 DB 커넥션이 메모리를 점유하고 있다는 것이다. 

커넥션 풀을 이용하면 커넥션 수를 일정하게 유지할 수 있고, 스레드의 작업이 끝나면 커넥션은 커넥션 풀로 반환되고 이는 다른 스레드에서 사용 가능하다.

## proxy


# 트랜잭션 격리레벨 종류
# 동시성제어
