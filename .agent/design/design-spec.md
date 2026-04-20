# TriageGeist — Design Specification
Delhi Hospital · Dark Theme · ChatGPT-style UI

---

## Global Design Tokens

### Colors
| Token | Hex | Usage |
|---|---|---|
| `bg-base` | `#0d0d0d` | Main page background |
| `bg-surface` | `#111111` | Cards, panels, sidebar |
| `bg-elevated` | `#1a1a1a` | Chat bubbles, input fields |
| `border` | `#1f1f1f` | Dividers, card borders |
| `border-subtle` | `#2a2a2a` | Input field borders |
| `accent-blue` | `#2563eb` | Primary CTA, logo, links |
| `accent-blue-light` | `#3b82f6` | Hover states |
| `accent-blue-muted` | `#1d3461` | Selected state backgrounds |
| `text-primary` | `#f5f5f5` | Headings, main text |
| `text-secondary` | `#9ca3af` | Labels, secondary text |
| `text-muted` | `#6b7280` | Placeholder, footer text |
| `text-faint` | `#374151` | Very subtle text |
| `green` | `#22c55e` | Online status indicator |
| `acuity-1` | `#ef4444` | Resuscitation (red) |
| `acuity-2` | `#f97316` | Emergent (orange) |
| `acuity-3` | `#eab308` | Urgent (yellow) |
| `acuity-4` | `#22c55e` | Semi-urgent (green) |
| `acuity-5` | `#14b8a6` | Non-urgent (teal) |

### Typography
| Element | Size | Weight |
|---|---|---|
| Page heading | 26–30px | 700–800 |
| Card heading | 17px | 700 |
| Body text | 12–13px | 400 |
| Labels | 10–11px | 400–600 |
| Footer | 9–10px | 400 |
| Font family | system-ui, sans-serif | — |

### Spacing & Shape
- Border radius (cards): 12–16px
- Border radius (buttons): 6–8px
- Border radius (pills/tags): 14px (fully rounded)
- Card padding: 24px
- Header height: 52–60px

---

## Page 1 — Home / Landing Page

**Reference:** mockup-1.svg

### Header
| Component | Detail |
|---|---|
| Background | `#111111` |
| Bottom border | 1px `#2a2a2a` |
| Height | 60px |
| Logo (cross icon) | Two overlapping rects, `#2563eb`, positioned left |
| Hospital name | "Delhi Hospital", 16px, 700, `#f5f5f5` |
| Site name | "TriageGeist", 10px, `#6b7280`, below hospital name |
| Staff Login button | Top-right, outlined style, border `#2563eb`, text `#2563eb`, 96×32px, radius 6px |

### Hero Section
| Component | Detail |
|---|---|
| Heading | "Welcome to TriageGeist", 26px, 700, `#f5f5f5`, centered |
| Subheading | 13px, `#6b7280`, centered |

### Patient Block (Left Card)
| Component | Detail |
|---|---|
| Position | Left, x=60 |
| Size | 300×240px |
| Background | `#1a1a1a` |
| Border | `#2a2a2a` + subtle blue glow `#2563eb` at 40% opacity |
| Icon | Patient silhouette in `#1e3a5f` circle, icon color `#2563eb` |
| Title | "I am a Patient", 17px, 700, `#f5f5f5` |
| Subtitle line 1 | "Start voice triage", 11px, `#6b7280` |
| Subtitle line 2 | "No login required", 11px, `#6b7280` |
| Auth note | "Enter your 3-digit session code to begin", 10px, `#6b7280` |
| CTA Button | "Get Started", filled `#2563eb`, 120×36px, radius 8px, white text |

> **Session code:** Nurse enters a 3-digit session code (NOT their 4-digit login PIN) to begin a voice triage session. This code is separate from their profile login.

### Staff Block (Right Card)
| Component | Detail |
|---|---|
| Position | Right, x=440 |
| Size | 300×240px |
| Background | `#1a1a1a` |
| Border | `#2a2a2a` |
| Icon | Stethoscope in `#1e3a5f` circle, icon color `#2563eb` |
| Title | "I am Staff", 17px, 700, `#f5f5f5` |
| Subtitle line 1 | "Nurse / Doctor / Admin", 11px, `#6b7280` |
| Subtitle line 2 | "Enter your 3-digit code to begin triage", 11px, `#6b7280` |
| Auth note | "3-digit session code — different from your login PIN", 10px, `#6b7280` |
| CTA Button | "Staff Login", outlined `#2563eb`, 120×36px, radius 8px |

> **Two codes explained:**
> - **3-digit session code** — used on this landing page to quickly start a triage session. Lightweight, fast.
> - **4-digit PIN** — used on the Staff Login page (top-right button) to access full profile, dashboard, admin tools.

### Footer
| Component | Detail |
|---|---|
| Background | `#111111` |
| Text | "© 2025 Delhi Hospital — TriageGeist v1.0.2", 10px, `#6b7280`, centered |

---

## Page 2 — Triage Result Page

**Reference:** mockup-4.svg

### Header
Same as Page 1 header. Page label "Triage Result" shown right-aligned in `#6b7280`.

### Result Card
| Component | Detail |
|---|---|
| Size | 480×340px, centered |
| Background | `#111111` |
| Border | 1px `#1f1f1f` |
| Border radius | 16px |

#### Acuity Badge
| Component | Detail |
|---|---|
| Container | 240×80px, centered in card |
| Background | Tinted version of acuity color (e.g. `#1c1309` for orange) |
| Border | 1.5px acuity color |
| Label | "ACUITY LEVEL", 11px, 600, letter-spacing 2, acuity color |
| Number | 44px, 900 weight, acuity color |

#### Acuity Level Colors
| Level | Label | Color |
|---|---|---|
| 1 | RESUSCITATION | `#ef4444` red |
| 2 | EMERGENT | `#f97316` orange |
| 3 | URGENT | `#eab308` yellow |
| 4 | SEMI-URGENT | `#22c55e` green |
| 5 | NON-URGENT | `#14b8a6` teal |

#### Acuity Label
| Component | Detail |
|---|---|
| Level name | 13px, 700, acuity color, centered |
| Description | 11px, `#6b7280`, centered |

#### Chief Complaint System
| Component | Detail |
|---|---|
| Label | "CHIEF COMPLAINT SYSTEM", 11px, `#9ca3af`, centered |
| Pill tag | 140×28px, background `#1e3a5f`, radius 14px |
| Pill text | 12px, 600, `#93c5fd` |

#### Queue Number
| Component | Detail |
|---|---|
| Label | "YOUR QUEUE NUMBER", 11px, `#9ca3af`, centered |
| Number | 52px, 900 weight, `#f5f5f5`, format `#007` |
| Caption | "Please wait — a nurse will call your number", 10px, `#4b5563` |

### Status Bar
| Component | Detail |
|---|---|
| Background | `#0a0a0a` |
| Green dot | `#22c55e`, radius 4px |
| Status text | "System Online · Model v1.0.2", 10px, `#6b7280` |
| Right text | "Delhi Hospital © 2025", 10px, `#374151` |

---

## Page 3 — Staff Login Page

**Reference:** mockup-5.svg (role selector removed)

### Layout
Two-panel split: left branding panel + right login form. Divider: 1px `#1f1f1f`.

### Left Panel
| Component | Detail |
|---|---|
| Background | `#0d0d0d` |
| Width | 360px |
| Logo | Same cross icon as header |
| Hospital name | 18px, 700, `#f5f5f5` |
| Site name | 11px, `#2563eb`, letter-spacing 2 |
| Heading | "Staff Portal", 22px, 700, `#f5f5f5` |
| Description | 12px, `#6b7280`, 2 lines |
| Stat card 1 | "99%", `#3b82f6`, label "Model Accuracy", bg `#111111` |
| Stat card 2 | "Live", `#22c55e`, label "System Status", bg `#111111` |

### Right Panel — Login Form
| Component | Detail |
|---|---|
| Heading | "Sign In", 18px, 700, `#f5f5f5`, centered |
| Subheading | "Enter your staff credentials", 11px, `#6b7280` |

#### Staff ID Field
| Component | Detail |
|---|---|
| Label | "Nurse ID / Staff ID", 11px, `#9ca3af` |
| Input | 280×36px, bg `#111111`, border `#2a2a2a`, radius 8px |
| Placeholder | "e.g. NURSE-001", `#4b5563` |

#### PIN Field
| Component | Detail |
|---|---|
| Label | "4-Digit PIN", 11px, `#9ca3af` |
| Input | 280×36px, bg `#111111`, border `#2a2a2a`, radius 8px |
| Masked input | 4 dots shown, filled `#4b5563`, empty `#1f1f1f` |

> **Role selector removed.** Role is determined automatically from the Staff ID on the backend.

#### Sign In Button
| Component | Detail |
|---|---|
| Size | 280×40px |
| Background | `#2563eb` |
| Text | "Sign In →", 13px, 700, white |
| Radius | 8px |

#### Back Link
| Component | Detail |
|---|---|
| Text | "← Back to Home", 11px, `#6b7280`, centered |
| Position | Below sign in button |

---

## Auth Flow Summary

```
Landing Page
├── Patient block → enter 3-digit session code → Patient Chatbot → Result Page
├── Staff block   → enter 3-digit session code → Nurse Chatbot  → Result Page
└── Staff Login (top-right) → Login Page (Staff ID + 4-digit PIN) → Dashboard
```

| Code Type | Digits | Purpose |
|---|---|---|
| Session code | 3 digits | Quick triage session start from landing page |
| Login PIN | 4 digits | Full profile access, dashboard, admin tools |
