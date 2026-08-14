# Edition One — explainer video script

Runtime ≈ 5:50 · ~810 words · 8 scenes · pace 150 wpm

Narration is what you say. **On screen** is what you show.

---

## Fix these before you record

1. **Point GitHub Pages at `/docs`** — Settings → Pages → Source → `main` / `docs`. Until then the live site 404s and you can only record locally.
2. **The leaderboard is showing watched accounts, not contestants.** On camera it reads `+423,946%`, which looks fabricated. Either point `build_leaderboard_data.py` at the `contestants` table, or skip the board in Scene 2 and film it after launch.
3. **Never let your investor password appear on screen.** You're filming Myfxbook settings pages. Use a throwaway account, or pause recording before typing into any password field.

## Before you hit record

- Record at 1920×1080. Browser zoom 110% — the site's mono labels are small at native size.
- Hide bookmarks bar, close other tabs, turn off notifications.
- Load the homepage once so the intro animation plays out, then reload. It only runs once per session, so it won't interrupt your take.
- For the Myfxbook half, have a second account ready that's already connected and verified. Verifying live on camera means waiting hours for badges to turn green.
- Generate the voiceover **per scene**, not as one long file. Re-syncing one scene after a re-shoot beats re-cutting the whole track.

---

## Scene 1 — Cold open · 0:00–0:30

**On screen**
- Homepage hero, full screen. Hold on "Find out where you stand."
- Slow scroll through the chips: no entry fee · live verified accounts · top 5 published.

**Narration**

> This is JibYourMentor. It's a trading competition for Moroccan traders — thirty places, three months, one leaderboard.
>
> There's no entry fee, and no money passes through us. In the next five minutes I'll show you what it is, and exactly how to enter.

---

## Scene 2 — What JYM actually is · 0:30–1:12

**On screen**
- Scroll to "What is JYM" — Apply / Trade / Record.
- Continue to the Top Five card. Let the deal-in animation play, then hover so it tilts.
- If the board is fixed by now: scroll to "Top five. Live." and hold three seconds.

**Narration**

> The problem here is simple. Anyone can say they're a good trader. Almost nobody can prove it.
>
> In JYM you trade your own account, at your own broker, exactly the way you already trade. Myfxbook reads the results — not us. We can't edit them, and neither can you.
>
> After three months, the top five are published with their real numbers attached. Finish outside the top five and nothing is published at all.

---

## Scene 3 — Who can enter · 1:12–1:58

**On screen**
- Scroll to "Who can enter." Move the cursor across each requirement card so it lifts on hover — pause about a second on each.
- Hold longer on the two crossed-out cards: "No entry fee" and "Nothing to send us."

**Narration**

> Here's what you need. A live MT4 or MT5 account at a regulated broker — real money, not a demo, not a prop firm account. At least five hundred dollars in it. And that account connected to Myfxbook, so the numbers can be checked.
>
> Here's what you don't need. An entry fee — there isn't one. Screenshots, reports, weekly updates — we never ask for any of that.
>
> And you never send us your password. Not once, not ever.

---

## Scene 4 — Applying on the site · 1:58–2:42

**On screen**
- Click **Apply now**. Let the modal animate open.
- Fill the fields at a readable pace: name, email, Myfxbook link, broker, platform.
- Tick the confirmation box. Click **Send application**.
- Hold on the confirmation — checkmark, "Reviewing your application," progress bar. Don't click away; let it close itself.

**Narration**

> To apply, click Apply now. You'll need your name, your email, and the public link to your Myfxbook account. Then your broker and your platform. Everything else is optional.
>
> Tick the box to confirm the account is yours and that it's the only one you're entering. Send it.
>
> That's the whole application. You'll see this screen, and we start checking your profile straight away.

---

## Scene 5 — Creating and connecting Myfxbook · 2:42–3:42

**On screen**
- Go to `myfxbook.com`. Show sign-up, then land on the logged-in dashboard.
- Open the add-account flow from **Portfolio**. Step through: broker → platform (MT4/MT5) → server.
- Reach the investor password field — then **cut away or blur**. Resume on the connected account page.

> **Confirm on screen:** Myfxbook moves these menus around. Follow whatever the live UI says rather than a memorised path — the narration describes the steps rather than naming exact buttons, so it stays true either way.

**Narration**

> If you don't have Myfxbook yet, this is the part worth watching closely. Go to myfxbook dot com and create a free account.
>
> Then add your trading account. You'll choose your broker, your platform — MT4 or MT5 — and your server. Then you connect it using your *investor* password.
>
> That's the read-only password from your broker. It lets Myfxbook read your trades. It does not let anyone place a trade, move money, or touch your account. If you're about to type your normal trading password here — stop. That's the wrong one.

---

## Scene 6 — The two green badges · 3:42–4:46

**On screen**
- Open a public account page with both badges green. Zoom in on **Track record** and **Trading privileges**.
- Hover each badge so Myfxbook's own explanation tooltip appears. Hold long enough to read.
- Then show a page missing them, so the difference is obvious.

**Narration**

> Now the part that matters most — the two badges.
>
> **Track record verified** means Myfxbook compared your results against data coming directly from your broker.
>
> **Trading privileges verified** means Myfxbook confirmed the account is genuinely under your control — either by having you place a pending order using a key they give you, or by changing the investor password to one they provide.
>
> Both of these have to be green. Not one of them. Both. This is the entire point of JYM: by the time your name reaches that board, nobody has to take your word for anything.

---

## Scene 7 — Making your balance visible · 4:46–5:20

**On screen**
- Open your account's settings/privacy on Myfxbook. Turn balance visibility on. Save.
- Open your **public** page in a logged-out window — point the cursor at the balance now showing.

> **Confirm on screen:** the exact wording of this setting varies. What matters is the outcome — the balance is readable on the public page by someone who isn't signed in. Film the logged-out view; that's the proof.

**Narration**

> One last step. We need to confirm your account holds at least five hundred dollars — and we can only see what you choose to make public.
>
> In your Myfxbook account settings, switch your balance to visible. Then open your own public page while signed out, and look.
>
> If you can see the balance there, so can we. If you can't, neither can we — and you'll get an email from us asking for exactly this.

---

## Scene 8 — What happens next · 5:20–5:50

**On screen**
- Open a status link — `status.html?id=…` — with all three checks green. Let the badges animate in.
- Cut to the confirmation email.
- End on the homepage hero with the Apply button visible. Hold for the outro.

**Narration**

> Once you've applied, you get your own status link. It shows the three checks — track record, trading privileges, balance — and it updates as each one clears.
>
> When all three are green, you're in, and you'll get an email confirming it. After that you just trade, the way you always do, until the competition starts.
>
> That's everything. Thirty places. The link is below.

---

## Voiceover settings

- **Pace:** ~150 wpm. Slow to ~130 for Scene 6 — the two verifications are the part people rewind.
- **Pauses:** a full beat between scenes, and after "Not one of them. Both." Let that land.
- **Emphasis:** the word *investor* in Scene 5 carries the whole safety message. If your TTS flattens it, generate that line separately.
- **Numbers:** write "five hundred dollars" in the input text, not "$500" — most engines read the symbol awkwardly.
- **Accent:** for a Moroccan audience, a neutral English voice reads as more credible than an over-produced American one. Test both on Scene 3 before committing.
