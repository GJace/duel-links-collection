Context and decisions. Not needed for the code.

Planning session: `claude --resume eae12112-1956-44dc-9d22-aeb24cfc5e4e` (named "yugioh duel links collection notes").

## Problem

Too many cards. When browsing DLM decks I don't know which cards I own.

## Checked, nothing exists (Nov 2026)

- DLM has no collection feature. Profile page only has settings.
- No Duel Links collection exporter found. Related tools:
  - [YGOPRODeck Companion App](https://ygoprodeck.com/master-duel/companion-app): exports collection to CSV, Master Duel only.
  - [duellinksjson](https://github.com/byi8220/duellinksjson): abandoned Duel Links card list to JSON.
  - [Yugioh-bot](https://github.com/will7200/yugioh-bot), [duel-links-bot](https://awesome.ecosyste.ms/projects/github.com%2Fftuyama%2Fduel-links-bot): old farming bots using screen reading. Show screen automation works on Duel Links.

## Rejected options

- Manual entry: thousands of cards.
- Reading game memory or local files (Steam): ToS, likely encrypted.
- Intercepting Android traffic: encrypted, likely cert-pinned, ToS.
- Android + adb: works, but I want it to run all day on the Windows PC.
- Matching thumbnail art only: small images, foil effects. Detail panel text is more reliable.
- Hover to read details: game doesn't update the panel on hover.
- Batches by card type: rarity first gives the useful data (UR/SR) early.

## Accepted risk

Automated input breaks ToS. Read-only, no gameplay, random delays.
