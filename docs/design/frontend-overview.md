# Frontend Overview

## Layout & Navigation
- **Global Header**: displays service logo (left) and user profile entry (right). Header is fixed at the top of `page` container.
- **Two-panel layout**: left panel is the chat input/history (sticky), right panel is the D-Day dashboard with tabs/GNB. Layout uses a 1:1 grid on desktop and stacks on screens <900px.

## Chat Panel
- Components: `ChatPanel`, `useDday` hook.
- Features:
  - Message bubbles differentiate user vs assistant colors.
  - Input embedded send button (Google `send` icon) positioned inside the text field on the right.
  - History is appended for each user query and D-Day response; errors currently suppressed.

## D-Day Panel (GNB)
- Tabs/GNB: `공유 디데이`, `즐겨찾기`, `내 기록`, `설정`.
- `공유 디데이`: fetches `/dday` list, displays cards in a grid. Each card shows poster, title, D-Day, release date, genre.
- `즐겨찾기`: shows the most recent D-Day result (from POST) and switches automatically after a successful query.
- `내 기록`, `설정`: placeholders for future features (calendar integration, reactions, etc.).

## Planned Enhancements
- Hook "같이 기다려요" 버튼을 반응 API와 연결해 실시간 카운트/토글을 반영한다(optimistic UI).
- 공유 목록 상단에 `/dday/longest` 응답을 요약 배지로 노출해 가장 멀리 있는 개봉일을 강조한다.
- 비어 있는 탭(`내 기록`, `설정`)에 대한 빈 상태 문구/예시 데이터를 보완하고, 추후 캘린더 연동·반응 로그 등을 수용할 섹션 설계를 진행한다.
- 로딩 중에는 공유 그리드 skeleton, 채팅 패널에는 진행중 표시를 노출해 상호작용 상태를 명확히 한다.

## Tech Stack
- React + Vite + TypeScript.
- CSS modules via single `styles.css` (global). No UI framework currently; layout relies on CSS Grid/Flex.
- Fetch API calls: `POST /dday` for creation, `GET /dday` for shared list (proxy configured in `vite.config.ts`).

Use this document to keep frontend structure/design choices in sync while implementing new UI features such as reactions or calendar integration.
