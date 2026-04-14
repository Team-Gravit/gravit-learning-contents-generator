## JSON 출력 템플릿

백오피스 전달용 JSON 구조. Phase 6(`build-staging-output`)에서 사용한다.

```json
{
  "unit_id": 28,
  "generated_at": "2026-04-14T10:00:00+09:00",
  "lessons": [
    {
      "id": 80,
      "unit_id": 28,
      "title": "네트워크 기초 개념 문제집",
      "problems": [
        {
          "id": 509,
          "lesson_id": 80,
          "instruction": "아래 제시한 개념에 대한 설명으로 옳은 것은?",
          "content": "네트워크는 여러 장치들이 연결된 구조이다.",
          "problem_type": "OBJECTIVE",
          "options": [
            {
              "id": 1395,
              "problem_id": 509,
              "content": "단일 컴퓨터만 사용하는 시스템이다",
              "explanation": "네트워크는 여러 장치가 연결되므로 오답이다.",
              "is_answer": false
            },
            {
              "id": 1396,
              "problem_id": 509,
              "content": "여러 컴퓨터나 통신 장치들이 연결되어 데이터를 주고받을 수 있는 구조이다",
              "explanation": "정답이다.",
              "is_answer": true
            }
          ]
        },
        {
          "id": 510,
          "lesson_id": 80,
          "instruction": "빈칸에 들어갈 알맞은 말을 작성하시오",
          "content": "네트워크는 ___ 및 자원 공유를 위한 통신 체계이다.",
          "problem_type": "SUBJECTIVE",
          "answer": {
            "id": 159,
            "problem_id": 510,
            "content": "정보 교환,information exchange",
            "explanation": "네트워크는 정보 교환 및 자원 공유를 위한 통신 체계이다."
          }
        }
      ]
    }
  ]
}
```
