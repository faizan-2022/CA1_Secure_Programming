# Meridian Expenses — Python / Flask

Issued for **CCT MSc Cybersecurity (Sep 2026 intake)**, Secure Programming and Scripting, **CA1 (40%)**.

> ## ⚠️ This application is deliberately insecure
> It is a teaching artefact. It contains multiple serious, exploitable security
> defects **on purpose**. Do not deploy it, do not put it on a public network,
> and do not reuse any of this code in real work.
>
> It binds to **127.0.0.1 only**. Keep it that way.
>
> All data in it is fabricated. No real person, account or payment appears here.

## What it is

A small staff expense-claim portal: staff sign in, submit claims, view their own
claims and download receipts. Finance and admin roles exist. It is about the size
of a real internal tool that nobody security-reviewed.

## Running it

```
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python seed.py          # creates expenses.db and sample receipts
python app.py           # http://127.0.0.1:5000
```

Sample accounts (the passwords are weak on purpose):

| Username | Password | Role |
|---|---|---|
| `jdoe` | `password1` | staff |
| `rsmith` | `letmein` | staff |
| `achen` | `Summer2026` | finance |
| `admin` | `admin` | admin |

## Your task

The brief is the authority — this file only tells you how to run the thing. In
summary you must identify **at least six distinct security vulnerabilities**,
demonstrate each one, classify it, assess its impact, and fix it.

Two things students routinely lose marks on:

- **Six distinct vulnerabilities, not six instances of one.** Three injectable
  parameters in the same query pattern is one vulnerability found three times.
- **A proof-of-concept is required.** "This looks vulnerable to X" scores far
  below a request, a response and a screenshot showing X actually happening.

## Rules of engagement

Test **only** this application, **only** on your own machine, **only** on
localhost. Nothing here authorises you to test any CCT system, any third-party
site, or anything else. Doing so is a disciplinary matter and, under the Criminal
Justice (Offences Relating to Information Systems) Act 2017, potentially a
criminal one.

## Declaring AI use

The AI Fluency declaration table in the brief is compulsory. Using a tool to help
find or explain a vulnerability is permitted; not declaring it is not.
