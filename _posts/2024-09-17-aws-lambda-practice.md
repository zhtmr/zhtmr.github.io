---
published: true
layout: single
title: "[AWS] Web Application with Serverless 실습"
excerpt: ""
categories:
  - AWS
tags:
  - [ 'AWS', 'Lambda', 'dynamoDB', 'API Gateway', 'S3' ]
use_math: true
---

> [AWS TechCamp](https://aws.amazon.com/ko/events/seminars/aws-techcamp/) 서버리스 관련 워크샵 요약 정리


## 실습 과정 요약
![img_3.png](https://github.com/zhtmr/static-files-for-posting/blob/main/static-files-for-posting/20240917/img_3.png?raw=true){: .align-center}


## 각 서비스의 역할
- **S3** : 정적 웹사이트 호스팅
- **DynamoDB** : 간단한 웹 어플리케이션의 데이터를 저장하는 용도. no-sql 기반.
- **API Gateway** : 엔드포인트와 REST API 를 관리함. 사용자가 설정한 라우팅 설정에 따라 각 엔드포인트를 대리하여 요청과 응답을 받는 프록시 역할을 한다. lambda 와 연결.
- **Lambda** : 앱 서버

## DynamoDB 생성
RDBMS 의 경우, 스키마를 정의하고 이 스키마를 이용해 데이터를 저장하게 된다. 그러나 DynamoDB 와 같은 NoSQL 데이터베이스는 스키마를 정의할 필요 없이 key-value 형태로 자유롭게 데이터를 저장할 수 있다.
![img_3.png](https://github.com/zhtmr/static-files-for-posting/blob/main/static-files-for-posting/20240917/dynamo-create.png?raw=true){: .align-center}

테이블 생성 버튼을 눌러 테이블 이름과 파티션 키를 입력 한다. 파티션 키는 검색에 필요한 키값으로 필수적으로 입력해야 한다.
- 테이블 이름 : `hello-member`
- 파티션 키 : `name`

## Lambda 생성
![img_3.png](https://github.com/zhtmr/static-files-for-posting/blob/main/static-files-for-posting/20240917/lambda.png?raw=true){: .align-center}
*Lambda 를 이용해 백엔드 서비스 코드를 만들수 있다.*

AWS 의 대표적인 서버리스 서비스. 서버에 대한 설정이나 관리를 고민할 필요 없이 간단하게 서버를 만들 수 있다. 예를 들어 많은 요청 발생 시 자동으로 확장되고, 관리되므로 서비스에만 집중할 수 있다.
간단하고 빠르게 서버를 만들고 싶은 경우 사용할 수 있다.



함수 생성 버튼을 눌러 아래와 같이 입력한다.
![img_3.png](https://github.com/zhtmr/static-files-for-posting/blob/main/static-files-for-posting/20240917/lambda-create-func.png?raw=true){: .align-center}

- 선택 옵션 : `새로 작성`
- 함수 이름 : `api-service-create`
- 런타임 : `Python 3.9`

함수에 대한 권한 설정 부분은 아래와 같이 진행한다.
![img_4.png](https://github.com/zhtmr/static-files-for-posting/blob/main/static-files-for-posting/20240917/lambda-permission.png?raw=true){: .align-center}

이 함수는 추후 DynamoDB 에 연결할 예정이다. AWS 서비스끼리 서로 연결하거나 이용하거나 호출하거나 할 때에는 권한이 필요하다.
- 역할 이름 : `my-lambda-role`
- 정책 템플릿 : `단순 마이크로서비스 권한 - DynamoDB`

코드 부분에 아래와 같이 입력 후 `Deploy` 버튼을 누른다.
![img_3.png](https://github.com/zhtmr/static-files-for-posting/blob/main/static-files-for-posting/20240917/lambda-code.png?raw=true){: .align-center}

<details>
<summary>코드보기</summary>
<div markdown="1">


> 이 코드는 멤버의 이름과 기분 상태를 랜덤으로 매핑시켜주고, 이를 DynamoDB에 저장하는 기능이다.
>
> ```python
> import json
> import boto3
> import random
> import json
>
> def lambda_handler(event, context):
>    
>    member_name = ['Ama','Jone','Zon','Penny','Jessie']
>    member_status = ['Happy','Sad','Serious','Satisfied','Free']
>    
>    dynamodb = boto3.resource('dynamodb',endpoint_url='http://dynamodb.ap-northeast-2.amazonaws.com')
>    member_table = dynamodb.Table('hello-member')
>    
>    name = member_name[random.randint(0,4)]
>    status = member_status[random.randint(0, 4)]
>    
>    member_table.put_item(
>       Item={
>            'name': name,
>            'status': status,
>        }
>    )
>    
>    documents = {'name':name,'status':status}
>    
>    print(documents)
>    
>    return {
>        'statusCode': 200,
>        'headers': {'Access-Control-Allow-Origin': '*'},
>        'body': json.dumps(documents)
>    }
> ```
> 
</div>
</details>


`Test` 버튼을 눌러 아래와 같이 테스트 이벤트를 구성 후 저장 버튼을 누른다.
![img_3.png](https://github.com/zhtmr/static-files-for-posting/blob/main/static-files-for-posting/20240917/lambda-test-conf.png?raw=true){: .align-center}

- 이벤트 이름 :  `my-api-test`
- 템플릿 : `hello-world`

테스트 결과가 아래와 같은 형식으로 나온다면 제대로 설정된 것이다.
![img_3.png](https://github.com/zhtmr/static-files-for-posting/blob/main/static-files-for-posting/20240917/lambda-test-res.png?raw=true){: .align-center}

이제 DynamoDB 에 데이터가 잘 들어갔는지 확인해보자. DynamoDB 로 이동해 `hello-member` 테이블을 누른다.
![img_3.png](https://github.com/zhtmr/static-files-for-posting/blob/main/static-files-for-posting/20240917/dynamo-table.png?raw=true){: .align-center}

표 항목 탐색을 누른다.
![img_3.png](https://github.com/zhtmr/static-files-for-posting/blob/main/static-files-for-posting/20240917/dynamo-table-search.png?raw=true){: .align-center}

아래와 같이 Lambda 의 코드가 실행되어 DynamoDB 에 값이 잘 들어가 있다.
![img_3.png](https://github.com/zhtmr/static-files-for-posting/blob/main/static-files-for-posting/20240917/dynamo-table-data.png?raw=true)

여기까지 Lambda 와 DynamoDB 를 만들고, 잘 동작되는 것을 확인했다. 
이제 클라이언트에서 이 Lambda 의 함수를 호출할 수 있도록 엔드포인트를 제공해야 한다.

## API Gateway 구성하기
서비스에서 API Gateway 를 검색 후 REST API 유형을 선택한다. 
![img_3.png](https://github.com/zhtmr/static-files-for-posting/blob/main/static-files-for-posting/20240917/api-gateway-init.png?raw=true){: .align-center}

새 API 를 선택하고 API 이름에 `my-api` 를 입력한다.
![img_3.png](https://github.com/zhtmr/static-files-for-posting/blob/main/static-files-for-posting/20240917/api-gateway-create.png?raw=true){: .align-center}

`my-api` 선택 후 메서드를 생성한다.
![img_3.png](https://github.com/zhtmr/static-files-for-posting/blob/main/static-files-for-posting/20240917/api-gateway-method-create.png?raw=true){: .align-center}

아래와 같이 메서드 세부 정보를 설정 후 메서드를 생성한다.
- 메서드 유형 : `GET`
- 통합 유형 : `Lambda 함수`
- Lambda 프록시 통합 토글 `ON`
- Lambda 함수 선택에서 기존에 만들어 두었던 `api-service-create` 를 선택한다.

![img_3.png](https://github.com/zhtmr/static-files-for-posting/blob/main/static-files-for-posting/20240917/api-gateway-method-create2.png?raw=true){: .align-center}

생성한 API의 리소스 메뉴에서 방금 생성한 GET 메서드를 누르면 이제는 오른쪽에 해당 메서드에 관련된 정보가 보이게 된다. 테스트 탭을 선택 후 테스트를 준비한다.

![img_3.png](https://github.com/zhtmr/static-files-for-posting/blob/main/static-files-for-posting/20240917/api-gateway-test.png?raw=true){: .align-center}


테스트 버튼을 눌러 API 호출을 테스트 해본다. 서비스가 복잡해지면 Request Body 나 Header 에 값을 추가할 수도 있다.
![img_3.png](https://github.com/zhtmr/static-files-for-posting/blob/main/static-files-for-posting/20240917/api-gateway-test2.png?raw=true){: .align-center}

테스트 성공 시 상태 코드에 200 과 함께 응답 본문에 Lambda 함수 실행 결과가 올바르게 출력된다면 성공이다.
![img_3.png](https://github.com/zhtmr/static-files-for-posting/blob/main/static-files-for-posting/20240917/api-gateway-res.png?raw=true){: .align-center}

### CORS 설정
API gateway 를 만들었지만, 바로 호출하면 CORS 관련 에러가 발생한다. 브라우저에서 실행하는 스크립트의 요청을 허용하려면 API에 대한 CORS(cross-origin resource sharing)를 구성해야한다.
CORS는 다른 도메인에서 리소스를 요청할 때 발생하는 보안 정책이다. API Gateway에 메소드를 만들었다 하더라도, 기본적으로는 CORS가 허용되지 않으므로 브라우저에서 다른 도메인(예: 클라이언트 서버와 API 서버의 도메인이 다를 경우)으로 요청을 보낼 때 문제가 발생할 수 있다.

리소스 메뉴에서 `/` 경로를 선택 후 CORS 를 활성화 한다.
![img_3.png](https://github.com/zhtmr/static-files-for-posting/blob/main/static-files-for-posting/20240917/api-gateway-cors-enable.png?raw=true){: .align-center}

CORS 설정 화면에서 Access-Control-Allow-Methods 에 GET 메서드를 선택한다. GET 요청에 대해 리소스 접근을 허용한다. 
![img_3.png](https://github.com/zhtmr/static-files-for-posting/blob/main/static-files-for-posting/20240917/api-gateway-cors-setting.png?raw=true){: .align-center}

참고로 위 사진에서 Access-Control-Allow-Methods 항목에 OPTIONS 메소드가 기본값으로 포함되어 있는데, 이는 프리플라이트 요청(Preflight Request) 이다. 클라이언트에서 요청하려는 URL이 외부 도메인일 경우, 
브라우저는 안전하지 않은 HTTP 요청(예: POST, PUT, DELETE)을 보내기 전에 OPTIONS 메소드를 사용하여 서버에 프리플라이트 요청을 보낸다. 서버가 이 요청에 대해 적절한 응답을 하지 않으면 브라우저는 CORS 에러를 발생시킨다. 실제 요청이 유효한지 서버가 미리 파악할 수 있도록 하는 수단이다.

CORS 설정을 마쳤으면 API 배포 버튼을 눌러 이 api 를 실제 사용할 수 있게 준비한다.
- 스테이지 : *새 스테이지*
- 스테이지 이름 : `dev`
![img_3.png](https://github.com/zhtmr/static-files-for-posting/blob/main/static-files-for-posting/20240917/api-gateway-deploy.png?raw=truehttps://github.com/zhtmr/static-files-for-posting/blob/main/static-files-for-posting/20240917/api-gateway-deploy.png?raw=truehttps://github.com/zhtmr/static-files-for-posting/blob/main/static-files-for-posting/20240917/api-gateway-deploy.png?raw=truehttps://github.com/zhtmr/static-files-for-posting/blob/main/static-files-for-posting/20240917/api-gateway-deploy.png?raw=truehttps://github.com/zhtmr/static-files-for-posting/blob/main/static-files-for-posting/20240917/api-gateway-deploy.png?raw=truehttps://github.com/zhtmr/static-files-for-posting/blob/main/static-files-for-posting/20240917/api-gateway-deploy.png?raw=true){: .align-center}

배포가 완료되면 호출 URL 이 표시된다. 
![img_3.png](https://github.com/zhtmr/static-files-for-posting/blob/main/static-files-for-posting/20240917/api-gateway-url.png?raw=true){: .align-center}

이 URL 을 브라우저에 붙여넣고 호출하면 아래와 같은 응답을 얻을 수 있다.

![img_3.png](https://github.com/zhtmr/static-files-for-posting/blob/main/static-files-for-posting/20240917/api-gateway-result.png?raw=true){: .align-center}

Lambda 에 API gateway 를 연결해 클라이언트에서 접근 가능한 엔드포인트를 만드는 작업이 완료되었습니다.
이제 이 데이터를 S3 의 정적 웹사이트 호스팅 기능을 사용해 html 페이지에 표시하는 작업을 진행해보겠습니다. 

## S3 웹서버 기능 사용하기
AWS 서비스에서 S3 를 검색 후 버킷을 생성한다. 버킷의 이름은 고유해야 한다.
![img_3.png](https://github.com/zhtmr/static-files-for-posting/blob/main/static-files-for-posting/20240917/s3-create-bucket.png?raw=true){: .align-center}

아래쪽으로 내려 퍼블릭 엑세스 차단 설정을 해제한다. 정적 웹 호스팅 용도로 사용하기 위해 모든 접근을 허용해야 클라이언트(브라우저)에서 html 파일을 내려받을 수 있다.
![img_3.png](https://github.com/zhtmr/static-files-for-posting/blob/main/static-files-for-posting/20240917/s3-public-access.png?raw=true){: .align-center}

버킷 생성을 누르고 생성이 완료되면 해당 버킷을 눌러 들어 간다. 그 후 아래와 같은 html 코드를 index.html 파일로 만들어 버킷에 업로드 한다.

<details>
<summary>코드보기</summary>
<div markdown="1">

앞에서 API gateway 로 만든 url 로 ajax 호출을 하고, 데이터를 가져와 화면에 뿌리는 역할을 하는 간단한 html 코드다.
```html
<html>

<head>
    <meta charset="utf-8" name="viewport"
        content="width=device-width, height=device-height, minimum-scale=1.0, maximum-scale=1.0, initial-scale=1.0">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
    <title>Hello World!</title>
    <style>
        #title {
            font-family: arial;
            font-size: 2em;
            color: #eb971a;
            margin-top: 50px;
            text-align: center;
        }

        button {
            background-color: #eb971a;
            border: none;
            color: white;
            border-radius: 5px;
            width: 40%;
            height: 35px;
            font-size: 13pt;
            margin-top: 30px;
            text-align: center;
        }

        #sentence {
            font-size: 17pt;
            margin-top: 30px;
            font-weight: bold;
            color: #eb971a;
        }
    </style>
</head>

<body>
    <p id="title">Hello World From <b>Lambda</b></p>
    <hr id="lambda-line" width="800px" align="center" color="#eb971a;">
    <center><button onclick="checkEvent();">Who are you?</button></center>
    <center>
        <div id="sentence"></div>
    </center>
</body>
<script type="text/javascript">
    function checkEvent() {
        $.ajax({
            type: "GET",
            url: "URL을입력하세요",
            dataType: 'json',
            success: function (data) {
                document.getElementById('sentence').innerHTML = data.status + "&nbsp;&nbsp;" + data.name
            },
            error: function (error) {
                alert('ERROR::');
                console.log(error)
            }
        });
    }
</script>

</html>
```
</div>
</details>


![img_3.png](https://github.com/zhtmr/static-files-for-posting/blob/main/static-files-for-posting/20240917/s3-upload-file.png?raw=true){: .align-center}

![img_3.png](https://github.com/zhtmr/static-files-for-posting/blob/main/static-files-for-posting/20240917/s3-upload-file2.png?raw=true){: .align-center}

index.html 파일을 업로드 했으면 정적 웹사이트 호스팅 기능을 활성화 하고, 권한을 부여해야 한다.
![img_3.png](https://github.com/zhtmr/static-files-for-posting/blob/main/static-files-for-posting/20240917/s3-property.png?raw=true){: .align-center}

속성 탭에서 맨 아래쪽으로 스크롤하면 정적 웹 사이트 호스팅 기능이 있다.
![img_3.png](https://github.com/zhtmr/static-files-for-posting/blob/main/static-files-for-posting/20240917/s3-static-website-hosting1.png?raw=true){: .align-center}

편집을 눌러 활성화 한다. 웹사이트 처음 진입 시 기본 페이지가 될 파일을 입력한다.(index.html)
![img_5.png](https://github.com/zhtmr/static-files-for-posting/blob/main/static-files-for-posting/20240917/s3-static-website-hosting2.png?raw=true){: .align-center}

변경 사항 저장을 누르면 정적 웹 사이트 호스팅이 시작된다.
![img_3.png](https://github.com/zhtmr/static-files-for-posting/blob/main/static-files-for-posting/20240917/s3-hosting.png?raw=true){: .align-center}

그러나 해당 URL 클릭 시 아직 권한이 없어 접속이 안된다. 외부에서 파일을 읽어 들일수 있도록 권한을 부여해야 한다.
다음 그림과 같이 권한 탭에서 **버킷 정책**에 JSON 으로 작성된 권한 설정을 해준다.

<details>
<summary>JSON 설정</summary>
<div markdown="1">

```json
{
  "Version": "2024-09-18",
  "Statement": [
    {
      "Sid": "Stmt1709405011428",
      "Action": [
        "s3:GetObject"
      ],
      "Effect": "Allow",
      "Resource": [
        "arn:aws:s3:::my-bucket-238423",    // 본인버킷 번호
        "arn:aws:s3:::my-bucket-238423/*"    // 본인버킷 번호
      ],
      "Principal": "*"
    }
  ]
}
```
</div>
</details>

![img_3.png](https://github.com/zhtmr/static-files-for-posting/blob/main/static-files-for-posting/20240917/s3-permission.png?raw=true){: .align-center}

권한 설정이 마무리되면 S3 호출 URL 로 이동한다. index.html 의 화면이 잘 나오고 버튼을 누를때마다 Lambda 로 ajax 호출해 데이터를 가져오는 것을 볼 수 있다.

## 결과

![result](https://github.com/user-attachments/assets/3eb65307-ce0f-4e6d-9c4e-41d3d6a8c8ee){: .align-center}

서버리스 사용 이전엔 spring 을 통해 웹 어플리케이션 서버를 배포하곤 했다. REST API 를 스프링에서 제공하도록 만들고, 이 백엔드 서버를 AWS EC2 같은 클라우드에 배포해 기동시키는 형태였다. 

그러나 서버리스 아키텍쳐를 활용하게 되면 서버 구성이나 관리에 대한 설정/코드 등을 작성할 필요 없이 그냥 서비스 코드를 Lambda 에 넣어놓고 이를 호출하도록 구성하면 된다. 또한 API gateway 를 통해 클라이언트에게 API 를 제공하게 함으로써 Lambda 의 코드와 연동이 가능하다는 것을 알게 되었다.

서버리스는 다음과 같은 특징을 가진다.
- 특정 **작업을 호출할때에만 함수가 호출**되는 원리이다 보니 호출된 만큼만 비용을 지불한다.
- 인프라 관리에 신경 쓸 필요가 없다.
- 네트워크 처리량에 따라 서버의 갯수를 자동으로 늘려준다. (auto-scaling)
- 한 함수가 한번 호출될때 제한이 있다.(1500MB, 300초) 즉, 웹소켓 같이 계속 켜놔야 하는 작업은 하기 힘들다.
- 로컬 데이터에 접근 불가능하다. 이는 Lambda 가 **stateless** 하기 때문이다. Lambda 함수는 실행될 때마다 새로운 인스턴스가 생성되고, 람다 함수 내에서는 내부적으로 변수 값의 변화등을 저장하거나 추적하지 않는다. 따라서 호출 사이에 **상태를 저장하거나 공유할 필요가 있다면 S3 나 DynamoDB, RDS 등을 연동해서 사용해야 한다**.

이런 특징들을 살펴보면, 단일 작업을 하는 간단한 서버 같은 경우는 서버리스를 통해 쉽게 만들 수 있다는 장점이 있는 것 같다.
그러나 그렇다고 스프링과 같은 프레임워크가 필요 없다는 의미는 아니다. 복잡한 비즈니스 로직을 가진 엔터프라이즈 급의 통합 시스템에서는 모든 로직을 함수로 나누어 관리할 경우 관리가 어려워 질 수 있다.
또한, 이미 스프링 같은 프레임워크는 풍부한 생태계를 가지고 있어 다양한 라이브러리와 모듈을 사용해 개발할 수 있다는 장점이 있다.