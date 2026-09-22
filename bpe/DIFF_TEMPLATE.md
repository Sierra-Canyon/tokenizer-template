# DIFF: my tokenizer against `cl100k_base`

Copy this to `bpe/DIFF.md` and fill in every angle bracket:

```
cp bpe/DIFF_TEMPLATE.md bpe/DIFF.md
```

<!,
Two rules for the whole file.

A number with no sentence beside it is not a finding. A sentence with no number
beside it is not evidence. Every section wants both.

Paste real output. Do not retype it, do not round it, and do not tidy up the
ugly parts. The ugly parts are usually the result.
,>

---

**Corpus:** `data/<file>` · <n> bytes · <what it is, and why you picked it>
**Vocab size:** <n> · **Merges learned:** <n>
**Round-trip:** <clean, or: failed on `<the string>`>

---

## 1. What my tokenizer learned

| Merge | Bytes | Length | Decodes to |
|---|---|---:|---|
| #1 | `<b'..'>` | <n> | `<..>` |
| #10 | `<b'..'>` | <n> | `<..>` |
| #100 | `<b'..'>` | <n> | `<..>` |

**What merge #1 tells me about my text:** <one or two sentences. If it decoded to
a replacement character, say so and say what that means about the script my
corpus is written in.>

## 2. Compression

| Tokenizer | ids on my corpus | bytes / token |
|---|---:|---:|
| `BasicTokenizer`, mine | <n> | <n.nn> |
| `RegexTokenizer`, mine | <n> | <n.nn> |
| `cl100k_base` | <n> | <n.nn> |

**Which of my two won:** <name it, and say by how much.>

**Merges my `BasicTokenizer` learned that the regex split could never form:**
<n> of <n>. Examples: <paste five or six>

**Why that explains the result above:** <one or two sentences.>

**Why my comparison against `cl100k_base` is unfair in my favour:** <one or two
sentences. This one is not optional and there is a real answer.>

## 3. The ten probe strings

| String | mine | `cl100k_base` | my pieces |
|---|---:|---:|---|
| `1234567890` | <n> | <n> | <..> |
| `12,345,678` | <n> | <n> | <..> |
| `hello` | <n> | <n> | <..> |
| `' hello'` | <n> | <n> | <..> |
| `Hello` | <n> | <n> | <..> |
| `'    '` | <n> | <n> | <..> |
| `'\t'` | <n> | <n> | <..> |
| `'    def foo():'` | <n> | <n> | <..> |
| `strawberry` | <n> | <n> | <..> |
| `🙂🙃` | <n> | <n> | <..> |

**The row where the gap is widest, and why:** <...>

## 4. Three differences, explained

<!,
This is the part that is actually graded. A difference is not "cl100k is
better." A difference is a specific thing one tokenizer does that the other
does not, with the output that shows it and a mechanism that explains it.
,>

### Difference 1 — <short name>
**What I saw:** <...>
**Evidence:**
```
<paste>
```
**Why it happens:** <...>

### Difference 2 — <short name>
**What I saw:** <...>
**Evidence:**
```
<paste>
```
**Why it happens:** <...>

### Difference 3 — <short name>
**What I saw:** <...>
**Evidence:**
```
<paste>
```
**Why it happens:** <...>

## 5. Tokens I have that `cl100k_base` does not

```
<paste the sorted list from the vocabulary cell>
```

**What that list is mostly made of:** <one or two sentences. Say what it tells
you about the difference between 512 merges on your corpus and 100,000 merges
on the internet.>

---

<!,
Why this file exists: A06 and the capstone both ask you to compare something you
built against something professional, and the honest version of that comparison
is harder than the flattering one. Practising it here, where the stakes are one
assignment, is the point.
,>
