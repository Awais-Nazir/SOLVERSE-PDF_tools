<b>StandAlone Installer:
 
 - Used Inno Installer to make it stand alone installer. 
 - uploaded zip file with installer and required files in the google drive
 - google drive link (direct download) can be shared with users so that they can download and use it


<b>
 - tried IPC with mutex to handle multiple GUIs instance while selecting 2...
 
 # ask chatgpt to not include this ipc forwading in this merge_launcher.py file 
# as ipc forwarding is already handled in merge_app.py Perfect — that’s a very smart pause.
Documenting **why** earlier approaches failed will save you (and future-you) *weeks* later.
Below is a **clean, professional, reference-quality write-up** you can drop straight into `progress.md`.

---

# 📄 Progress Notes — Single Instance & Multi-PDF Context Menu Handling

## Background

The goal is to allow users to:

* Select **multiple PDF files** in Windows Explorer
* Right-click → **Merge PDFs**
* Open **only one GUI window**
* Have **all selected PDFs loaded together**

Windows Explorer launches **one executable per selected file**, which creates concurrency and timing challenges.

---

## Attempt 1 — Mutex Only (Launcher-Level)

### Approach

* Used a **system-wide mutex** in `merge_launcher.exe`
* First launcher instance created the mutex
* Subsequent instances detected mutex and exited

### Result

* Prevented multiple GUI windows
* ❌ Only **one PDF** reached the app
* ❌ Additional PDFs were lost

### Root Cause

* Windows launches all launcher processes almost simultaneously
* Secondary launchers exited **before merge_app.exe started**
* No mechanism existed to aggregate arguments

### Conclusion

> Mutex alone prevents duplication but **cannot collect multiple arguments**
> ❌ Not sufficient

---

## Attempt 2 — IPC (Socket-Based Single Instance) in merge_app

### Approach

* Implemented a TCP IPC server in `merge_app.py`
* New instances attempted to:

  * Connect to existing server
  * Forward PDF paths
  * Exit if successful
* Primary instance started GUI + IPC server

### Result

* Worked when launch timing was ideal
* ❌ Failed when context menu launched multiple instances rapidly
* ❌ Connection attempts happened **before IPC server was ready**

### Observed Logs

* Launchers forwarded files too early
* IPC server started **hundreds of milliseconds later**
* Connection timeouts caused secondary instances to self-promote

### Conclusion

> IPC forwarding is valid **only after the primary app is fully initialized**
> ❌ Startup-time IPC is unreliable for Explorer multi-selection

---

## Attempt 3 — IPC + Retry / Delay

### Approach

* Added retry logic:

  * Random delays (min/max)
  * Multiple IPC attempts before giving up
* Increased wait times (e.g. 15–25 seconds)

### Result

* Eventually worked
* ❌ Extremely slow startup
* ❌ Fragile and machine-dependent
* ❌ Not deterministic

### Why This Is Bad

* Relies on timing luck
* Breaks on slower/faster machines
* Unacceptable UX

### Conclusion

> Retry-based timing hacks are **not production-safe**
> ❌ Rejected

---

## Attempt 4 — Mutex + IPC in Launcher

### Approach

* Launcher:

  * Used mutex to detect primary
  * Tried IPC forwarding itself
* merge_app also had IPC logic

### Result

* One GUI window appeared
* ❌ Only one PDF loaded
* ❌ IPC attempts happened **before merge_app IPC server existed**

### Root Cause

* IPC forwarding occurred in the wrong process
* Launcher exited too early
* App startup timing still uncontrolled

### Conclusion

> IPC forwarding **must not happen in launcher**
> ❌ Architectural mismatch

---

## Key Technical Insight (Final Learning)

### Windows Explorer Behavior

* Context menu launches:

  * One process per selected file
  * Within ~5–15 ms of each other
* Arguments are **never batched**

### Critical Rule

> **Startup-time IPC is unreliable**
> **Argument aggregation must happen *before* the GUI launches**

---

## Final Decision

### ❌ Rejected Approaches

* Mutex-only
* IPC-only
* Retry-based IPC
* IPC inside launcher

### ✅ Accepted Direction

**Queue-Based Argument Aggregation (Pre-GUI)**

* Launcher acts as **collector**
* merge_app acts as **consumer**
* IPC remains only for **runtime forwarding**

---

## Next Step

Design and implement:

> **Queue-based launcher architecture**
> using a shared, atomic file to collect all selected PDFs
> before launching `merge_app.exe`

---

If you want, next I will:

* Design the **exact queue file format**
* Define **launcher flow step-by-step**
* Add **logging strategy**
* Ensure it works with PyInstaller + Inno Setup

Just say **“Proceed with queue-based design”** 🚀
