# ☕ CoffeeChat-Piro  
피로그래머들을 위한 커피챗 플랫폼

## 📖 소개
**CoffeeChat-Piro**는 피로그래머들을 연결하고 소통을 촉진하는 커뮤니티 플랫폼입니다.  
피로그래밍 21기 최종 프로젝트로 개발되었으며, **커피챗** 플랫폼으로 리팩토링 했습니다.

## 🌟협업 페이지 링크

[노션 링크](https://www.notion.so/PiroTime-5d7fb0a939be45ee9e663767952b0b3c)

## 🖥️서비스 화면

### 모든 페이지 모바일(아이폰 14 Pro Max 기준 max-width: 430px) 반응형 지원

#### 홈(랜딩페이지)
- 피로그래머들의 접근을 더 편리하게 하기 위해 메인페이지에 로그인 화면 노출
- 로그인 및 회원가입 버튼 생성
- 회원가입 시 멘토 프로필 리스트 화면으로 이동

<p align="center">
  <img src="https://github.com/user-attachments/assets/9054bbff-ceb1-45be-acb3-124bc41a9e89" height="500">
  <img src="https://github.com/user-attachments/assets/b2164ca9-34a8-4b22-b189-5f2088b427a7" height="500">
</p>

#### 멘토 프로필 탐색 페이지
- 맨토의 프로필 클릭 가능

<p align="center">
  <img src="https://github.com/user-attachments/assets/b4fe943e-4dcc-484b-88ab-552eaa0f6f3b" height="500">
  <img src="https://github.com/user-attachments/assets/67158378-4624-4801-8bca-2abf6a64d256" height="500">
</p>

#### 커피챗 신청 페이지
- 멘토의 프로필을 구경 후 '커피챗 신청' 버튼 클릭을 통해 신청 가능
- 커피챗 2회 제한을 두어 신청 횟수가 다 차면 '커피챗 마감' 버튼으로 변경 

<p align="center">
  <img src="https://github.com/user-attachments/assets/1408ade1-9580-4510-949a-41371b960782" height="500">
  <img src="https://github.com/user-attachments/assets/d8f6c908-2081-47e0-8e08-792426552f8c" height="500">
</p>

#### 마이페이지 - 커피챗 현황(신청/진행/완료) 확인 
- 신청한 커피챗 내역과 신청 받은 내역 확인 가능
- 신청 받은 내역에서 커피챗 수락이나 거절 가능
- 완료 시 커피챗에 대한 리뷰 작성 가능

<p align="center">
  <img src="https://github.com/user-attachments/assets/8a4cd153-30fe-4ee2-a92e-834901dc6e22" height="500">
  <img src="https://github.com/user-attachments/assets/1351dd0f-128b-488b-85d9-8b13cf7b6cfb" height="500">
</p>

#### 마이페이지 - 내 정보 수정, 프로필 스크랩 페이지
- 내 정보 탭: 닉네임, 기수, 이메일 변경 가능
- 스크랩 탭: 멘토 프로필 스크랩 가능, 클릭 시 멘토 프로필 상세페이지로 이동

<p align="center">
  <img src="https://github.com/user-attachments/assets/cce9b324-d83d-43d9-9019-f95e100fab1e" height="500">
  <img src="https://github.com/user-attachments/assets/e5d5328b-319f-4631-acd4-1de34ca15e28" height="500">
</p>

## 💫리팩토링 후 개선점
- 사용자 피드백 반영(글씨체와 글씨 크기 조절 및 랜딩페이지를 로그인 페이지로 사용)
- 필요없는 코드나 변수 정리 후 클린코드 작성
- CI/CD 구축하여 빌드 및 배포 자동화
- 실제 21/22기 플랫폼 사용(50명 사용자 유치)


## 🎯 개발 환경
- **백엔드**: Python 3.8, Django 4.2, Django Rest Framework (DRF)  
- **프론트엔드**: HTML5, CSS3, JavaScript  
- **데이터베이스**: PostgreSQL 16.4  
- **서버/배포 환경**: AWS EC2 (Ubuntu 20.04)  
- **웹 서버**: Nginx 1.23 (Reverse Proxy)  
- **WSGI 서버**: Gunicorn 20.1.0  
- **버전 관리 및 협업**: Git, GitHub, Notion, Zep, Figma  
- **CI/CD 도구**: GitHub Actions, appleboy/ssh-action

# 📂기획 및 설계 산출물
## 💭요구사항 정의 및 기능 명세([Notion](https://www.notion.so/REFAC-a83511059aa4464faca56b94dfa60135)) - 일부 캡쳐
<img src="https://github.com/user-attachments/assets/83eb6190-721c-4535-b879-59ec85f7f08b" alt="기능 명세서" width="800"  height="500">

## 🎨화면 설계([Figma](https://www.figma.com/design/GNy9zyW1y3IQk1oaukzBrK/PiroTime?node-id=70-4&t=HZbUcis6l2gl7siK-0))- 일부 캡쳐
<img src="https://github.com/user-attachments/assets/5d007748-9b92-4d79-a2ad-84594e9ba3ee" alt="기능 명세서" width="800"  height="500">

## 📜[ERD](https://www.erdcloud.com/d/7zKaYteiMHxbz34pf)
<img src="https://github.com/user-attachments/assets/c263d3b1-1639-411a-b98b-2a12efc023b1" alt="ERD" width="1000"  height="500">


# 💞팀원 소개

#### CoffeeChat-Piro을 개발한 피로그래밍 21기 팀원들을 소개합니다!

<table>
  <tr>
    <td align="center">
      <a href="https://github.com/JuheeeKim">
        <img src="https://github.com/user-attachments/assets/8904c618-4873-40ec-ab9d-789d2c8f55db" width="250px;" alt="나"><br>
        <b>FE/BE 팀장: 김주희</b>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/YourLink1">
        <img src="https://github.com/user-attachments/assets/64d688b5-173e-4a3e-bcc8-5be6fe3f2a70" width="250px;" alt="수용빠"><br>
        <b>FE/BE 팀원: 이수용</b>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/nawkwoo">
        <img src="https://github.com/user-attachments/assets/ef2e635a-001d-4250-8bcc-6abe958be91d" width="250px;" alt="관우빠"><br>
        <b>FE/BE 팀원: 손관우</b>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/C2hazelnut">
        <img src="https://github.com/user-attachments/assets/188861f6-37dc-4d84-8857-a2de6882e38d" width="250px;" alt="연진"><br>
        <b>FE/BE 팀원: 이연진</b>
      </a>
    </td>
  </tr>
</table>


