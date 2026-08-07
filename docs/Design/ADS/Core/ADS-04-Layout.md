# ADS-04 — Layout System

**Document ID:** ADS-04  
**Title:** Layout System  
**Version:** 0.1.0  
**Status:** Draft  
**Owner:** Project Atlas  

---

# Purpose

The Atlas Layout System defines the spatial organization of the Atlas workspace.

Its purpose is to create a consistent, predictable, and efficient environment where users can focus on engineering rather than navigating software.

Every Atlas application should follow the layout principles defined in this document.

---

# Design Philosophy

The workspace is the product.

Everything else supports the workspace.

Atlas is not a collection of windows.

Atlas is a single engineering workspace where every panel, tool, and interaction contributes to a unified experience.

---

# Workspace Hierarchy

The interface follows a clear visual hierarchy.

```
Application

↓

Workspace

↓

Panels

↓

Tools

↓

Content

↓

Interactions
```

Users should always know where they are and where to focus.

---

# Primary Layout

Atlas is organized into six functional regions.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Menu Bar                                                                    │
├───────────────┬──────────────────────────────┬───────────────────────────────┤
│ Explorer      │                              │ Inspector                    │
│               │                              │                               │
│ Projects      │                              │ Properties                    │
│ Resources     │       3D Workspace           │ Semantics                     │
│ Layers        │                              │ Relationships                 │
│ Assets        │                              │ History                       │
│               │                              │ AI Context                    │
├───────────────┴──────────────────────────────┴───────────────────────────────┤
│ Status Bar / Console / Notifications                                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

The 3D Workspace is always the primary focus.

---

# Layout Regions

## Menu Bar

Provides access to application-level functionality.

Examples:

- File
- Edit
- View
- Insert
- AI
- Help

The menu bar should remain lightweight.

---

## Explorer

The Explorer manages navigation.

It contains:

- Projects
- Resources
- Layers
- Collections
- Assets

The Explorer is for finding and organizing—not editing.

---

## Workspace

The Workspace is the heart of Atlas.

It is where users:

- View models
- Create resources
- Modify resources
- Inspect engineering data
- Collaborate

The workspace should receive the majority of screen space.

---

## Inspector

The Inspector provides contextual information.

It displays only information relevant to the current selection.

Typical sections include:

- Properties
- Metadata
- Semantics
- Relationships
- Validation
- AI Insights

The Inspector should never become a secondary explorer.

---

## Bottom Panel

The Bottom Panel provides supporting information.

Examples:

- Console
- Notifications
- AI Output
- Validation Results
- Import/Export Logs

It should remain collapsible.

---

## Status Bar

The Status Bar communicates application state.

Examples:

- Current Project
- Selection Count
- Grid Units
- Snap Mode
- Save Status
- AI Activity

Status should always be visible but never distracting.

---

# Workspace Rules

The workspace always has priority.

Whenever additional space is required:

1. Collapse secondary panels.
2. Resize supporting panels.
3. Never reduce the workspace unnecessarily.

---

# Panel Behavior

Panels should be:

- Resizable
- Dockable
- Collapsible
- Persistent

Panel layouts should be remembered between sessions.

---

# Contextual Interfaces

Atlas avoids unnecessary modal dialogs.

Instead:

- Side panels update dynamically.
- Context menus appear near the cursor.
- Toolbars change based on selection.
- AI suggestions appear contextually.

Users should remain inside the workspace whenever possible.

---

# Responsive Layout

Atlas supports different screen sizes without changing its interaction model.

Large Displays

- Full workspace
- Persistent Explorer
- Persistent Inspector

Medium Displays

- Collapsible Explorer
- Collapsible Inspector

Small Displays

- Overlay panels
- Adaptive workspace
- Context-first navigation

Regardless of screen size, the workspace remains central.

---

# Visual Balance

The interface should emphasize content over chrome.

The model should always attract more attention than the interface surrounding it.

Whitespace should improve readability rather than waste space.

---

# Design Rules

The layout should:

- Maximize workspace visibility.
- Minimize unnecessary navigation.
- Preserve user context.
- Support uninterrupted workflows.
- Scale across future Atlas products.

---

# Success Criteria

The Layout System succeeds when:

- Users immediately understand the interface.
- Navigation feels effortless.
- Panels never compete with the workspace.
- Engineering remains the visual priority.
- Users can customize their workspace without losing consistency.

---

# Layout Statement

Atlas is organized around work, not windows.

The workspace is the destination.

Everything else exists to support it.