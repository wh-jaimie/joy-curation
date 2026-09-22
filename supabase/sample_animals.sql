-- 동물 주제 샘플 콘텐츠 (Supabase SQL Editor 에서 Run)
update public.content set
  month_label = '2026년 10월 · 1개월차',
  subject     = '첫 달 주제는 ''동물''이에요. 아이들이 가장 먼저, 가장 좋아하는 소재라 영어책 입문에 딱이에요. 동물 이름·울음소리·색깔이 반복되며 첫 영어 단어가 자연스럽게 귀에 들어옵니다. 5권은 조작북(만지고 여는 책)부터 이야기책까지 단계별로 담았어요. 잘 읽어야 한다는 부담은 내려놓고, 소리와 그림을 함께 즐겨주세요.',
  read_method = '• 하루 1~2권, 같은 책을 여러 번 반복해도 좋아요. 반복이 아이에겐 최고의 학습이에요.
• Dear Zoo는 플랩을 아이가 직접 열게 해주세요. "What''s this?" 하고 기다렸다가 함께 열기.
• Brown Bear는 노래하듯 리듬을 타고, "What do you see?"에서 아이가 다음 동물을 맞히게 해보세요.
• Moo, Baa, La La La!는 동물 소리를 크게, 과장되게! 아이가 따라 내면 성공이에요.
• 뜻을 일일이 한국어로 통역하지 마세요. 그림을 가리키며 영어 단어만 반복해도 충분해요.
• 아이가 지루해하면 바로 덮어도 괜찮아요. ''즐거운 기억''이 다음 책으로 이어집니다.',
  activities  = '동물 흉내 놀이 — 책 속 동물 소리·동작을 따라하며 "What animal am I?" 맞히기
동물 카드 만들기 — 좋아한 동물을 그려 벽에 붙이고 지나갈 때마다 영어로 불러주기
Dear Zoo 역할놀이 — 상자에 인형을 숨기고 "Too big! Too tall!" 하며 하나씩 꺼내기
색깔 찾기 — Brown Bear를 읽고 집에서 같은 색 물건 찾아 "I see a red ___" 말하기
바깥 연계 — 동물원·마트에서 진짜 동물/그림을 볼 때 배운 단어로 불러주기
최애 투표 — 5권 중 제일 좋아한 책에 스티커 붙이기',
  expressions = 'What''s this? - 이건 뭐야?
What do you see? - 뭐가 보여?
It''s a bear! - 곰이다!
Open it! - 열어봐!
Too big! / Too tall! - 너무 커! / 너무 키가 크다!
What sound does it make? - 무슨 소리를 내지?
The cow says moo. - 소는 음메 하고 울어.
Can you roar like a lion? - 사자처럼 으르렁 할 수 있어?
I like the ___ best. - 나는 ___가 제일 좋아.
One more time? - 한 번 더 볼까?',
  updated_at  = now()
where theme_key = 'animals';
