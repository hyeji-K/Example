# 프로젝트 포트폴리오: WAITWITH (AI 기반 D-Day 공유 에이전트)

## 1. 프로젝트 개요
**WAITWITH(웨잇위드)**는 사용자가 기대하는 영화나 드라마의 개봉일을 AI를 통해 손쉽게 검색하고 다 함께 디데이(D-Day) 카운트다운을 공유할 수 있는 **AI Agent 기반 서비스**입니다. 
단순히 정보를 검색해 주는 것을 넘어, 챗봇과 대화하듯 소통하며 사용자의 의도를 분석하고 자율적으로 도구(Tool)를 호출하여 작동하는 에이전틱 워크플로우(Agentic Workflow)를 구현했습니다.

### 기획 의도
- 새로운 콘텐츠의 개봉 소식을 커뮤니티 게시판 이리저리에 의존하는 불편함 해소.
- "내가 기다리는 영화를 남들도 얼마나 기다릴까?" 하는 '함께 기다리는 감정'의 서비스화.
- 채팅 형태의 자연스러운 정보 탐색과 직관적인 대시보드(카드 UI)의 결합.

---

## 2. 사용 기술 Stack
* **Backend**: Python, FastAPI, SQLAlchemy
* **AI & LLM**: OpenAI API (gpt-4o-mini), LangChain (Tool Calling, Streaming)
* **Frontend**: React, TypeScript, Vite
* **External API**: TMDb (The Movie Database)
* **Database**: SQLite (개발용)

---

## 3. 핵심 시스템 아키텍처 및 구현 기술

### 3.1. Single-Pass Streaming 오케스트레이션 (SSE)
- LLM의 사고 과정(`analysis`), 도구 호출(`tool_started`), 도구 결과(`tool_result`), 최종 텍스트 토큰(`token`)을 **단일 스트림(Server-Sent Events)** 파이프라인으로 구축했습니다.
- 프론트엔드에서는 수신되는 이벤트를 실시간으로 파싱하여, 'Agent가 생각하는 과정'을 사용자가 시각적으로 체감할 수 있도록 State UI(스테이지 버블)로 렌더링합니다.

### 3.2. 자율적 도구 호출 (LLM Tool Calling)
- LangChain의 `StructuredTool`을 이용해 TMDb 검색 API를 `movie_search`, `tv_search` 두 개의 도구로 추상화했습니다.
- 시스템 프롬프트를 통해 Agent가 사용자의 발화 내용(영화인지, 드라마인지, 일상 대화인지)을 분석하고 **스스로 적합한 도구를 선택**하여 실행하도록 설계했습니다.

### 3.3. 'Human-in-the-loop' 구조 구현 (디데이 컨펌 UI)
- 단순히 검색 결과를 바로 DB에 주입하는 대신, "디데이로 등록할까요?"라고 **사용자에게 확인(Confirmation)을 요청**하는 단계를 구현했습니다.
- 이는 Agent가 내린 결정을 인간이 최종 승인하는 'Human-in-the-loop' 턴 구조를 SSE 스트리밍 통신 위에서 자연스럽게 풀어낸 경험입니다. (수신된 `confirmation_required` 이벤트에 따라 프론트에서 버튼 렌더링 및 별도 API 호출)

### 3.4. 데이터 정규화 및 통합
- TMDb의 JSON 응답을 `MovieData` 도메인 객체로 일관되게 파싱하고, DB 모델(`Project`)에 주입하기 쉬운 파라미터 형태로 변환하는 서비스 레이어를 분리했습니다.
- 외부 API의 `source`와 `external_id`를 복합 유니크 키로 설정하여, 중복된 콘텐츠가 여러 개 생성되는 것을 방지하는 무결성을 확보했습니다.

---

## 4. 트러블슈팅 및 극복 과정

* **문제**: LLM이 스트리밍 응답 도중 Tool Call을 할 때 응답 포맷이 깨지거나 빈 텍스트(Token)를 뱉는 경우가 있었습니다.
* **해결**: `astream_events`에서 내보내는 청크를 정밀하게 분석하여 `_chunk_contains_tool_call` 로직을 구현했습니다. 도구 실행이 시작된 시점을 정확히 캐치하여 프론트엔드에 `tool_started` 이벤트를 선제적으로 넘겨줌으로써 UX의 어색함을 방지했습니다.
* **문제**: 사용자가 단순히 정보만 묻고 지나가고 싶을 때와 디데이로 박제하고 싶을 때를 구분하기 어려웠습니다.
* **해결**: 검색 성공 시 정보를 먼저 채팅 응답(스트림)으로 뿌려주고, 마지막에 `PendingConfirmation` (확인/취소 버튼) 상태를 발동시키는 투-트랙 통신으로 변경하여 사용자 제어권을 강화했습니다.

---

## 5. 향후 발전 계획 (Roadmap)
이 프로젝트는 단순 챗봇을 넘어 본격적인 Agentic 서비스로의 확장을 준비하고 있습니다.
1. **LangGraph 도입**: 현재의 선형적 추론 구조를 LangGraph의 순환형(Cyclic) 상태 머신 구조로 변경하여, 검색 실패 시 자기교정(Self-Correction)이 가능한 구조로 업그레이드할 예정입니다.
2. **벡터 검색 연동 (RAG)**: 리뷰 데이터나 시놉시스 기반 추천을 처리하기 위해 ChromaDB 등과 결합할 계획입니다.
3. **사용자 반응 기능**: "같이 기다려요" 버튼 클릭에 대한 상호작용 및 알림 시스템 구축.
