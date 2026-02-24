# Frontend Design Guide

## 색상 팔레트
- **Global Background**: `#F6F7FB` (page padding)와 `#FFFFFF`(본문). 두 톤을 섞어 밝은 분위기를 유지.
- **Panel Surface**: `#FFFFFF` + `1px` border `rgba(15, 23, 42, 0.06)` + 24px radius. 필요 시 살짝 `box-shadow: 0 2px 8px rgba(15, 23, 42, 0.08)`으로 부각.
- **Accent Purple**: `#8B5CF6` (`--accent`). 버튼, D-Day 숫자, 강조 텍스트, 봇 메시지 하이라이트 등에 사용.
- **Accent Soft**: `rgba(139, 92, 246, 0.12)` (`--accent-soft`). 배경형 태그나 그래디언트 오버레이에 사용.
- **Text Primary**: `#0F172A`; **Secondary**: `rgba(15, 23, 42, 0.6)`; **Error**: `#DC2626`.

## 타이포그래피
- **Font family**: `'Pretendard', 'SUIT', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`.
- **Scale**: H1 `1.4rem`, H2 `1.2rem`, Body `1rem`, Caption `0.8rem` (uppercase spacing 0.2em).
- **Line height**: 1.5 기본, 카드/헤더는 1.3으로 컴팩트하게.

## 레이아웃 원칙
- 데스크톱 기본은 좌우 1:1 split (`grid-template-columns: 1fr 1fr`). 모바일(<900px)은 단일 컬럼으로 스택.
- `layout` 컨테이너는 `max-width: 1200px`, 좌우 padding 24px, 하단 32px. 헤더는 별도 `top-header`로 페이지 상단에 고정.
- 채팅 패널은 sticky(`top: 32px`)로 고정하고, 디데이 패널은 전체 높이에 맞춰 스크롤 허용.

## 컴포넌트 스타일
- **GNB**: 상단 고정, 메뉴 사이 1px divider. Active 탭은 bold + `#0F172A` 색상만으로 구분.
- **Buttons**: 기본 pill(44px 높이). 배경 `--accent`, 텍스트 `#FFF`; 비중이 낮은 버튼은 하얀 배경 + 얇은 그림자. Hover 대신 색온도만 조정하여 안정된 느낌 유지.
- **Inputs**: Pill, `border: 1px solid rgba(15,23,42,0.1)` + 내부 그림자. Placeholder는 `rgba(15,23,42,0.35)`.
- **Chat Bubbles**: 사용자 = `--accent` 배경, 오른쪽 정렬; AI = 연한 회색(`rgba(15,23,42,0.05)`) 배경, 왼쪽 정렬. 하단 radius만 살짝 깎아 말풍선 느낌 강조.
- **Shared Cards**: 3:4 포스터 비율 + 하단 오버레이. 포스터 아래 `audience-badge`는 pill 버튼(그림자, border 없음, hover 효과 없음).

## 상태 피드백
- 로딩: 채팅 버튼 텍스트를 "찾는 중..."으로 바꾸고, 디데이 패널에는 "공유 디데이를 불러오는 중" placeholder.
- 오류: 빨간 텍스트(`error-text`)를 노출하되 카드 레이아웃은 유지.
- Empty states: 중앙 정렬 문구 + 연한 secondary 텍스트 색상을 사용해 가벼운 느낌 유지.

## 애니메이션/전환
- 주요 컴포넌트는 `transition: color 0.2s ease, background 0.2s ease`. 레이아웃 이동(채팅 패널→결과 패널 전환)은 없음.
- Sticky 헤더/패널이 겹치지 않도록 z-index 2 이상 유지.

이 문서는 라이트 톤 레이아웃을 유지하기 위한 기준이다. 새로운 컴포넌트나 테마 옵션을 도입할 때도 `--accent`와 화이트 서피스를 기반으로 한 단정한 무드를 유지한다.
