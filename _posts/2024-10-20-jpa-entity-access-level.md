---
published: true
layout: single
title: "[JPA] 엔티티 클래스에 `@NoArgsConstructor(access = AccessLevel.PROTECTED)` 를 붙이는 이유"
excerpt: ""
categories:
  - JPA
tags:
  - ['JPA']
use_math: true
---

# 엔티티 클래스에 `@NoArgsConstructor(access = AccessLevel.PROTECTED)` 를 붙이는 이유

> JPA 를 사용하다보면 Entity 클래스에 `@NoArgsConstructor(access = AccessLevel.PROTECTED)` 를 붙여서 기본 생성자의 생성 범위를 제한하는 경우가 있는데 왜 굳이 protected 를 붙이는지, 다른 접근 제한자는 왜 안되는지에 대해 알아보자.

## 지연로딩과 프록시 객체

```java
@Entity
@Table(name = "orders")
@Getter
@Setter
@NoArgsConstructor(access = AccessLevel.PROTECTED)  // 생성 메소드(createOrder) 를 통해서만 엔티티를 만들도록한다.
public class Order {

  @Id
  @GeneratedValue
  @Column(name = "order_id")
  private Long id;

  @ManyToOne(fetch = FetchType.LAZY)
  @JoinColumn(name = "member_id")
  private Member member;

  @OneToMany(mappedBy = "order", cascade = CascadeType.ALL)
  private List<OrderItem> orderItems = new ArrayList<>();

  @OneToOne(fetch = FetchType.LAZY, cascade = CascadeType.ALL)
  @JoinColumn(name = "delivery_id")
  private Delivery delivery;

  private LocalDateTime orderDate;

  @Enumerated(EnumType.STRING)
  private OrderStatus status;

  public void setMember(Member member) {
    this.member = member;
    member.getOrders().add(this);
  }

  public void addOrderItem(OrderItem orderItem) {
    orderItems.add(orderItem);
    orderItem.setOrder(this);
  }

  public void setDelivery(Delivery delivery) {
    this.delivery = delivery;
    delivery.setOrder(this);
  }

  /**
   * 객체 생성 static factory method
   * 
   */
  public static Order createOrder(Member member, Delivery delivery, OrderItem... orderItems) {
    Order order = new Order();
    order.setMember(member);
    order.setDelivery(delivery);
    for (OrderItem orderItem : orderItems) {
      order.addOrderItem(orderItem);
    }
    order.setStatus(OrderStatus.ORDER);
    order.setOrderDate(LocalDateTime.now());
    return order;
  }

  ...
}
```

JPA 에서 다대일 연관관계를 맺을때 불필요한 쿼리가 생성되는 것을 방지하기 위해 `@ManyToOne(fetch = FetchType.LAZY)` 로 지연로딩을 하게되는데
`FetchType.EAGER` 와 달리 실제로 find 한 Order 객체에서 member 를 탐색하는 시점에 member 를 쿼리하게 된다.

```java
Order findOrder = em.find(Order.class, id);  // 1
findOrder.getMember().getName();   // 2
```
위 코드에서 `getMember().getName()` 을 호출하는 시점에 실제로 `select * from member where memberId = ?` 쿼리가 실행된다.
즉, 최초 findOrder 만 조회한 상태(1번) 일때는 Order 엔티티 안에 member 엔티티가 없다는 의미가 된다.

그러나 그렇게 되는 경우 위 코드는 NullPointerException 오류가 발생할 것이다. null 에다가 getName() 은 불가능하기 때문.
JPA 는 이런 상황을 방지하기 위해 **Lazy 로딩의 대상이 되는 Member 엔티티**를 감싸는 프록시 객체를 만들어 우선 findOrder 객체를 만든다.

![img.png](https://github.com/zhtmr/static-files-for-posting/blob/main/static-files-for-posting/20241020/img.png?raw=true){: .align-center}
*프록시 객체*

프록시 객체는 내부에 Member 엔티티를 가지고 있는데, getName() 으로 실제 그 엔티티를 호출하는 시점에 DB 에 쿼리가 날아가고, Member 엔티티의 값이 채워진다.
아마도 이때 `member.setName("AAA")` 등과 같이 Member 엔티티에 값을 채워 1차 캐시에 저장하게 될텐데,
런타임 환경에서 member 엔티티 객체를 생성하기 위해 리플렉션을 사용하게 되는 경우 기본 생성자가 필요하다. (이는 JPA 뿐만 아니라 Mybatis 에서 쿼리를 VO 에 매핑하는 경우에도 마찬가지다.)

즉, 프록시 객체로 로딩되는 엔티티에 `@NoArgsConstructor(access = AccessLevel.PRIVATE)` 같이 외부에서 생성자를 사용할 수 없는 경우엔 애초에 오류가 발생한다.
![img_1.png](https://github.com/zhtmr/static-files-for-posting/blob/main/static-files-for-posting/20241020/img_1.png?raw=true){: .align-center}
*생성자 접근 제한자는 public, protected 만 가능하다*

정리하자면 JPA 에서 엔티티는 Public 이거나 Protected 생성자만을 가져아 한다.

>  ✅️ 엔티티 간의 글로벌 로딩 전략(lazy / eager) 이 아니라 특정 로직에서 필요한 쿼리(ex. findAll() 같은 리스트 조회 쿼리)는 JPQL 로 작성하게 된다. 
> JPQL 의 경우엔 바로 DB 로 쿼리가 날아가기 때문에 글로벌 엔티티 로딩 전략에 영향받지 않음. 
> 이런 경우엔 @ManyToOne 관계는 fetch join 으로 가져오고, @OneToMany 관계는 batch size 설정을 통해 in() 쿼리로 가져오면 쿼리 호출 횟수를 최소화 할 수 있다.



## `@NoArgsConstructor(access = AccessLevel.PUBLIC)` 으로 설정하면 안되나?

기본 생성자의 접근 지정자가 Public 이거나 Protected 이여야 하는 이유는 알겠는데,
그럼 `@NoArgsConstructor` 로 쓰는건(Public) 어떤 문제가 있나?

이 경우는 기능상의 문제가 아니라 휴먼 에러를 방지하기 위함이다.
```java
@Transactional
public Long order(Long memberId, Long itemId, int count) {
  // 엔티티 조회
  Member member = memberRepository.findOne(memberId);
  Item item = itemRepository.findOne(itemId);

  // 배송정보
  Delivery delivery = new Delivery();
  delivery.setAddress(member.getAddress());
  delivery.setStatus(DeliveryStatus.READY);

  // 주문상품 생성
  OrderItem orderItem = OrderItem.createOrderItem(item, item.getPrice(), count);

  // 주문 생성
  Order order = Order.createOrder(member, delivery, orderItem);

  // 주문 저장
  orderRepository.save(order);
  return order.getId();
}
```

위와 같은 비즈니스 로직에서 주문상품과 주문 엔티티를 만들때 정적 팩토리 메소드를 이용해 객체를 만들어내고 있다.
```java
// Order Entity
public static Order createOrder(Member member, Delivery delivery, OrderItem... orderItems) {
  Order order = new Order();
  order.setMember(member);
  order.setDelivery(delivery);
  for (OrderItem orderItem : orderItems) {
    order.addOrderItem(orderItem);
  }
  order.setStatus(OrderStatus.ORDER);
  order.setOrderDate(LocalDateTime.now());
  return order;
}
```
Order 엔티티 내부에 객체를 만드는 메소드를 놔두고 서비스 계층에서 엔티티가 필요한 경우 이 메소드를 호출하도록 한다.
이렇게 하는 이유는 엔티티와 관련된 메소드를 한 클래스에 모아놓음으로써 응집도가 올라가고, 같이 작업하거나 다른 사람이 유지보수를 하는 경우 외부에서 객체 생성을 방지하는데에 목적이 있다.

따라서 서비스 계층에서 `new Order()` 를 타이핑하는 순간 컴파일 에러를 만나게 된다. 만약 객체생성을 막지 않으면, 어디서든 객체의 값이 변경될 수 있고 이를 추적하기 힘들다.

이렇게 엔티티 안에 비즈니스 로직을 구성하는 방식을 도메인 모델 패턴(Domain Model Pattern) 이라고 하고, 반대로 엔티티에 비즈니스 로직이 없고 서비스 계층에 있는 경우를 트랜잭션 스크립트 패턴(Transaction Script Pattern) 이라고 한다.



## 정리
- 프록시 객체 생성 시 기본 생성자가 필요하기 때문
- 객체 생성 메소드를 통해서만 객체를 생성하도록 강제하기 위함

