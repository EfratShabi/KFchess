# Kung Fu Chess — Roadmap להשלמת ארכיטקטורת השרת

> **מסמך זה מיועד ל-Claude Code**, כדי שיבצע את ההשלמה ההדרגתית של שכבות השרת בפרויקט,
> בהתאם לדיאגרמת היעד (`Server_design_diagram.png`, 8 השכבות) ולעקרונות ב-`CLAUDE.md`.
> המסמך נבנה על סמך בדיקה בפועל של הקוד הקיים בריפו (לא הנחות).

---

## 0. איך לעבוד עם המסמך הזה (הוראות לקלוד קוד)

1. **קרא קודם** את `CLAUDE.md` (שכבות, single responsibility, no magic strings, dataclasses,
   symmetry של serializer/deserializer, WS כ-transport בלבד) ו-`server_design.md` — הם ה"חוקה" של הפרויקט.
2. **עבוד שלב (Phase) אחר שלב**, לפי הסדר במסמך. אל תדלג קדימה — כל שלב בונה על הקודם.
3. בכל שלב: **קודם בדוק שוב את הקוד בפועל** (ייתכן שתוקן מאז כתיבת מסמך זה), ורק אז ממש.
4. כל שינוי מלווה ב**טסטים** (תיקיית `tests/`, pytest). אל תסמן שלב כ"הושלם" בלי טסט ירוק.
5. שמור על ה-protocol constants הקיימים ב-`protocol.py` (`MSG_TYPES`, `FIELDS`) — כל הודעה חדשה
   נכנסת לשם, לא כמחרוזת מפוזרת בקוד.
6. אחרי כל שלב — עדכן את `todo` ואת `server_design.md` כדי שישקפו את המצב האמיתי.
7. אם שלב דורש החלטת תשתית (ספק ענן, Kubernetes אמיתי מול docker-compose מקומי וכו') —
   סמן זאת כשאלה פתוחה בסוף השלב ואל תנחש.

---

## 1. תמונת מצב: מה קיים היום מול הדיאגרמה

הפרויקט היום הוא **תהליך (process) יחיד** — `server/app.py` — שמריץ הכול ביחד: אימות, matchmaking,
לולאת ה-tick של המשחק (100ms), ושידור (broadcast) לשחקנים. זהו מימוש תקין ומלוכד ל-Phase 1
("הכול בתוך ה-Shard"), אבל הוא עדיין לא הפרדה בין השכבות שהדיאגרמה מתארת.

| # בדיאגרמה | רכיב | מצב בפועל |
|---|---|---|
| 1 | Player (WS direct moves) | ✅ קיים — `server/connection.py`, `server/app.py` |
| 1 | Spectator (WS view only) | ❌ לא קיים כלל. יש שדה `viewers=[]` ריק ב-`session.py` שלא בשימוש |
| 2 | WS Player Gateway (TLS, rate limit, ticket check) | ⚠️ חלקי — אין הפרדה מהשרת עצמו, אין TLS, אין rate limit, אין ticket (room_id+epoch+expiry) |
| 2 | API Gateway (login, history, rooms) | ⚠️ חלקי — login קיים אבל **בתוך אותו חיבור WS** (`server/login.py`), לא HTTP נפרד, אין "history", אין "rooms" |
| 3 | Matchmaker (stateless, Elo, ZSET) | ✅ קיים וטוב — `server/matchmaking.py`, Redis ZSET + Lua script, timeout/expire. אבל **לא stateless כתהליך נפרד** — קריאה ישירה בתוך `app.py` |
| 3 | Game Allocator (geo+load, issues ticket) | ❌ לא קיים בכלל |
| 4 | Game Server Shard (tick 100ms, GameEngine source of truth) | ✅ קיים וטוב — `server/session.py` + `core/services/game_service.py` + `core/real_time/real_time.py`. Recovery handler בפנים — ❌ לא קיים (אין reconnect כלל היום) |
| 5 | Redis Cluster (owner, epoch, lease, snapshot) | ⚠️ Redis בשימוש **רק ל-matchmaking queue**. אין snapshot, אין owner/epoch/lease/fencing, אין Streams |
| 5 | NATS (planned) | ❌ לא קיים — וזה תואם את המפה: זה roadmap מוצהר, לא דחוף |
| 6 | Spectator Edge Servers | ❌ לא קיים בכלל — אין consumer group, אין fan-out |
| 7 | PostgreSQL (users, elo, results) | ⚠️ חלקי — `users`+`rating` קיימים (`server/db.py`), **טבלת `results`/היסטוריית משחקים לא קיימת** |
| 7 | Result Writer (async batch write) | ❌ לא קיים — עדכון הדירוג (`game_result.py`) קורה **סינכרונית בתוך ה-tick loop task**, לא כתיבה אסינכרונית באצווה |
| 8 | Observability (logs, metrics, health, lease TTL watch) | ⚠️ חלקי — יש logging בסיסי (`server/logging_config.py`) לקובץ+קונסולה. אין metrics, אין health endpoint, אין lease TTL (כי אין lease) |

**מסקנה:** הליבה העסקית (לוח שחמט, תזוזות, cooldown, ניקוד, GameService, tick loop) חזקה ובעלת
כיסוי טסטים טוב. מה שחסר הוא **כל שכבת ה-scale/resilience/spectator** שהדיאגרמה מתארת —
בדיוק כמו שרשום ב-`todo`: "שרת: בחירת חדר", "התחברות/יצירת חשבון בגרפיקה".

---

## 2. סדר עדיפויות מומלץ (Phases)

הסדר נבחר כך שכל שלב עומד לבד, ניתן לבדיקה, ולא שובר את מה שכבר עובד. NATS מכוון בכוונה
לסוף (Phase 7) — בדיוק כפי שכתוב ב-`server_design.md`: "Roadmap קבוע... אחרי delta frames ופיצול תהליכים".

```
Phase 1 — Persistence: טבלת results + Result Writer אסינכרוני
Phase 2 — הפרדת API Gateway (HTTP: login/register/history/rooms) מ-WS
Phase 3 — WS Player Gateway דק + Ticket (room_id + epoch + expiry)
Phase 4 — Game Allocator + הפיכת Matchmaker לשירות עצמאי (stateless)
Phase 5 — Redis: snapshot + owner/epoch/lease (fencing) + Recovery handler ב-Shard
Phase 6 — Spectator support (protocol + Redis Streams + Spectator Edge Servers)
Phase 7 — Observability (metrics, health, lease-TTL watch) — ואז NATS כצעד roadmap נפרד
```

---

### Phase 1 — Persistence: היסטוריית משחקים + Result Writer אסינכרוני

**מטרה:** לסגור את שכבה 7 בדיאגרמה. היום `apply_rating_changes` כותב ל-Postgres סינכרונית
מתוך `run_session_tick_loop`, וחוסם את ה-task עד שהכתיבה מסתיימת. וגם אין טבלת תוצאות בכלל.

**משימות:**
- הוסף טבלת `results` ב-`server/db.py` (`init_db`): `room_id, white_username, black_username, winner, white_rating_after, black_rating_after, finished_at`.
- הוסף מתודה ל-`AccountRepository`: `save_result(...)`.
- צור `server/result_writer.py`: תור (asyncio.Queue) + worker task אחד שצורך תוצאות משחק שהסתיימו
  וכותב ל-Postgres באצווה (batch), במקום כתיבה סינכרונית תוך כדי ה-tick loop.
- עדכן את `run_session_tick_loop` ב-`app.py` כך שבסיום משחק הוא רק **מפרסם** (put) תוצאה
  ל-`result_writer`, ולא קורא ל-DB ישירות.
- הוסף endpoint/הודעת פרוטוקול ל"היסטוריה" (למשל `GET_HISTORY` ב-`MSG_TYPES`) שממנה חוזרת רשימת
  משחקים אחרונים של המשתמש — זה החלק החסר מ"API Gateway... history".

**טסטים:** `tests/test_db.py`, `tests/test_game_result.py` — להוסיף בדיקה ש-`results` נשמר,
ושה-writer לא חוסם את ה-tick loop (למשל assert על תזמון).

---

### Phase 2 — הפרדת API Gateway מ-WS

**מטרה:** היום login/register עוברים על אותו חיבור WS שדרכו ישוחק המשחק (`server/login.py`
מתבצע בתוך `handle_player_lifecycle`). בדיאגרמה זה gateway HTTP נפרד ("login, history, rooms").

**משימות:**
- צור מודול/תהליך HTTP חדש (`server/api_gateway.py`), למשל עם `aiohttp` או `FastAPI` (להוסיף
  ל-`requirements.txt`): endpoints ל-`POST /register`, `POST /login`, `GET /history`, `GET /rooms`.
- `login`/`register` מחזירים טוקן חתום (JWT או HMAC פשוט) — לא רק "עברת אימות בזיכרון של החיבור".
- שרת ה-WS (Phase 3) יאמת את הטוקן במקום להריץ תהליך login מלא בתוך ה-socket.
- זה השלב שבו `server/login.py` הופך לקוד שמופעל מתוך ה-API Gateway, לא מתוך `app.py`.

**טסטים:** טסטים חדשים ל-HTTP endpoints (למשל עם `httpx`/`aiohttp` test client). לשמור על
`tests/test_auth.py`, `tests/test_login.py` הקיימים ולוודא שעדיין עוברים אחרי הריפקטור.

**החלטה פתוחה:** FastAPI מול aiohttp מול הרחבת websockets עצמו ל-HTTP — לבחור לפי מה שכבר
מותקן/מוכר לצוות. ברירת מחדל מומלצת: FastAPI (typing, docs אוטומטיים, קל לבדוק).

---

### Phase 3 — WS Player Gateway דק + Ticket

**מטרה:** לפי `server_design.md` — gateway "דק" שרק עושה TLS, rate limit, ואימות ticket
(`room_id + epoch + expiry`) **פעם אחת** בכניסה, ואז proxy גולמי. היום `app.py` הוא גם gateway
וגם matchmaker וגם game shard יחד.

**משימות:**
- הגדר מבנה `Ticket` (dataclass) עם `room_id`, `epoch`, `expiry`, וחתימה (HMAC secret משותף).
- ה-API Gateway (Phase 2) או ה-Matchmaker (Phase 4) הם שמנפיקים ticket אחרי match — לא ה-WS gateway עצמו.
- `server/app.py` יתפצל: קובץ gateway חדש (`server/ws_gateway.py`) שמבצע רק: קבלת חיבור,
  אימות rate-limit בסיסי, אימות ה-ticket מול Redis/חתימה, ואז מעביר את ה-socket ל"שכבת ה-shard"
  (בשלב זה עדיין אותו תהליך — הפרדה לתהליך/container נפרד יכולה לבוא בשלב תשתית מאוחר יותר).
- ה-shard (session.py/app.py) כבר לא עושה אימות בעצמו — הוא מקבל חיבור עם ticket כבר מאומת.

**טסטים:** טסט ל-ticket תקין/פג-תוקף/room_id שגוי/epoch שגוי (fencing).

---

### Phase 4 — Game Allocator + Matchmaker כשירות עצמאי

**מטרה:** בדיאגרמה, ה-Matchmaker רק מחליט "מי משחק נגד מי", וה-Game Allocator (★) מחליט
"על איזה shard/מכונה זה ירוץ" (geo + load) ומנפיק את ה-ticket. היום שני התפקידים האלה לא קיימים
כשירותים נפרדים — matchmaking.py כן קיים (טוב!) אבל allocator לא קיים בכלל, וגם אין יותר מ-shard
אחד שאפשר להקצות אליו.

**משימות:**
- הגדר interface `GameAllocator` שמקבל את שני השחקנים שהתאימו ומחזיר: `shard_id` + ticket חתום.
  בשלב הזה, אם יש רק shard אחד (התהליך הנוכחי) — המימוש הפשוט ביותר הוא allocator "טריוויאלי"
  שתמיד מחזיר את אותו shard, אבל **הממשק** כבר בנוי כך שאפשר להוסיף שקלול geo/load בעתיד
  בלי לשנות קוד קורא.
- `MatchmakingQueue.try_match` נשאר אחראי רק להתאמה לפי Elo (ZSET) — לא לגעת בהקצאה.
- לזרוק את תוצאת ה-match + ticket ה-allocator דרך ה-API Gateway/WS Gateway בחזרה ללקוח (כבר יש
  `MatchFound` בפרוטוקול — צריך להוסיף לו שדה `ticket`).

**טסטים:** `tests/test_matchmaking.py` נשאר; להוסיף טסט ל-allocator (מוקאפ מרובה shards ובדיקת חלוקה).

---

### Phase 5 — Redis: snapshot + owner/epoch/lease (fencing) + Recovery

**מטרה:** זה הלב של יכולת ה-resilience בדיאגרמה. היום Redis משמש רק לתור matchmaking.
אין snapshot של מצב משחק, ואין מנגנון fencing/lease, כך שאם ה-shard קורס — המשחק פשוט אבד.

**משימות:**
- לכל room: `room:{id}:meta` (Redis Hash) — snapshot אחרון (תוצאה של `session.snapshot()` הקיים!
  יש כבר מתודה מוכנה ב-`session.py` — רק צריך לכתוב אותה ל-Redis כל N טיקים, לא רק לשדר ללקוחות).
- `room:{id}:owner` — מזהה ה-shard המחזיק כרגע את החדר, עם `epoch` (מספר סידורי שעולה בכל
  reassignment) ו-`lease` בעל TTL קצר (למשל 5 שניות) שמתחדש (`EXPIRE`) ע"י ה-shard החי כל טיק
  אחדים.
- הוסף `RecoveryHandler` בתוך אותו קוד shard קיים (`server/session.py`/`app.py` — **לא** מיקרו-שירות
  נפרד, כפי שנקבע ב-`server_design.md`): כשה-shard עולה, הוא בודק אם יש lease פג תוקף לחדר
  שהוא אמור להחזיק, לוקח owner+epoch חדש, וטוען את ה-snapshot האחרון מ-Redis כדי להמשיך את המשחק.
- `room:{id}:stream` (Redis Stream) — גיבוי אירועים (לא רק snapshot) לצורך שחזור מדויק וגם
  כבסיס לשלב הבא (spectators).

**טסטים:** טסט אינטגרציה עם Redis (יש כבר redis בשימוש בטסטים? לבדוק `tests/conftest.py`) —
lease expiry, epoch bump, טעינת snapshot אחרי "קריסה" מדומה.

---

### Phase 6 — Spectator support (Protocol + Streams + Edge Servers)

**מטרה:** שכבה 1 ו-6 בדיאגרמה — צופים (`WS view only`) ו-Spectator Edge Servers עם consumer
group. **כרגע אין שום דבר מזה** — אין הודעת פרוטוקול לצפייה, `viewers` ריק ולא בשימוש.

**משימות:**
- הוסף ל-`protocol.py`: `MSG_TYPES['SPECTATE']`, הודעת בקשה לצפייה ב-`room_id` (ללא ticket
  שחקן, רק אימות בסיסי/rate-limit).
- הרחב את `MatchFound`/API כדי לתמוך ב-"רשימת חדרים פעילים" (ה-"rooms" מה-API Gateway ב-Phase 2).
- צור `server/spectator_edge.py`: consumer group שקורא מ-`room:{id}:stream` (Redis Streams,
  שכבר קיים מ-Phase 5) ומשדר את העדכונים הלאה לצופים המחוברים אליו — **בלי לגעת ב-shard בכלל**,
  כדי שהעומס מהצופים לא ישפיע על המשחק עצמו (בדיוק כפי שכתוב ב-`server_design.md`).
- `session.py` — `viewers` list הופך לשימושי: חיבור spectator מצטרף אליו, אבל בלי הרשאת `try_move`/`try_jump`.

**טסטים:** טסט לזרימת spectator מקצה לקצה — התחברות, קבלת snapshot ראשוני, קבלת עדכונים חיים,
וידוא ש-spectator לא יכול לשלוח move.

---

### Phase 7 — Observability, ואז NATS (roadmap)

**מטרה:** שכבה 8. יש כבר logging בסיסי — חסר metrics, health endpoint, וניטור lease TTL
(כניטור *משלים*, לא כמקור אמת לכשל — הלוגיקה עצמה כבר ב-Phase 5).

**משימות:**
- הוסף health endpoint (`/health`) ל-API Gateway שמחזיר סטטוס DB/Redis.
- metrics בסיסיים (למשל Prometheus client): מספר חדרים פעילים, latency ל-tick, מספר צופים,
  כמות reassignments (epoch bumps).
- דשבורד/log נפרד שמסתכל על `lease` TTLs ב-Redis כאיתות "יש shard שאיבד lease ולא חודש" —
  זה ה-"lease TTL watch" בדיאגרמה, אבל הוא ניטור בלבד, לא מפעיל recovery בעצמו.
- **רק אחרי זה** — NATS ל-spectator fan-out, כפי שנקבע מפורשות כ"Roadmap קבוע... לא מותנה"
  אחרי delta frames + פיצול תהליכים. אל תתחיל את זה לפני שלבים 1-6 סגורים.

---

## 3. מה **לא** לגעת בו (כבר טוב, לא לשבור)

- `core/domain`, `core/real_time`, `core/services/game_service.py` — לוגיקת המשחק עצמה (לוח,
  תזוזות, cooldown, midair capture, ניקוד) — כיסוי טסטים רחב (`tests/test_piece.py`,
  `test_board.py`, `test_movement.py` ועוד). לא לגעת אלא אם באג מוכח.
- `server/rating.py` (Elo) — תקין, רק שינוי הקריאה אליו יהיה אסינכרוני (Phase 1).
- `server/matchmaking.py` — הלוגיקה של Lua script + ZSET כבר עומדת בדרישת "stateless, Elo, ZSET" מהדיאגרמה. רק ההרצה כשירות נפרד (Phase 4) חסרה.

---

## 4. שאלות פתוחות שדורשות החלטת בעלים (לא לנחש)

1. **סביבת יעד**: docker-compose מקומי מספיק לשלב הזה, או שיש כוונה אמיתית ל-Kubernetes/ענן
   (כפי שמוזכר ב-`interfaces/server_Design.md` לגבי 100M/10M concurrent)? זה משפיע על עד כמה
   "אמיתי" צריך להיות ה-Game Allocator ב-Phase 4.
2. **HTTP framework** ל-API Gateway (FastAPI/aiohttp/אחר) — ראה Phase 2.
3. **חתימת ticket**: HMAC secret משותף בין gateway ל-shard מספיק, או שנדרש JWT מלא עם claims?
4. **NATS**: להשאיר כ-roadmap עתידי בלבד (כפי שמומלץ כאן), או שיש לחץ עסקי להקדים אותו?

---

## 5. הגדרת "סיום" לכל שלב (Definition of Done)

לכל Phase: קוד + טסטים ירוקים (`pytest`) + עדכון `server_design.md`/`todo` + הרצה מקומית מוצלחת
עם `docker-compose up` שמדגימה את היכולת החדשה (למשל: הריגת תהליך shard תוך כדי משחק ב-Phase 5
ואימות שהמשחק ממשיך אחרי recovery).
