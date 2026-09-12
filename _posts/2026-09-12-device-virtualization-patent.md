---
layout: post
title: "Newly Granted Patent: Device Virtualization for Scalable I/O Management"
date: 2026-09-12 09:00:00 -0800
categories: [Architecture]
tags: [patents, architecture, hardware, virtualization, pcie]
toc: true
---

I'm glad to share that I've been granted a new US patent,
[US 12,650,940 B2, "Device Virtualization Techniques"](/assets/img/posts/patent-US-12650940-B2.png),
alongside co-inventors Ryan Holmqvist, Kapil Karkra, Orden Smith, Nicholas
Adams, and Vinay Raghav, assigned to Intel Corporation.

![US Patent 12,650,940 B2, Device Virtualization Techniques](/assets/img/posts/patent-US-12650940-B2.png)

## The Problem

Modern systems increasingly need to manage large, dynamic pools of I/O
devices behind a stable software-facing identity. NVMe storage is one
example, but the same challenge shows up for GPUs and AI accelerators:
large clusters of them get added, removed, reassigned, and hot-plugged as
workloads scale, while drivers and orchestration software generally expect
well-known, stable device identities. Solving that mismatch well requires
sitting squarely at the hardware/software interface, not purely in silicon
and not purely in software.

## The Idea, in Brief

The patent describes a mechanism for a physical I/O device to be locked
behind a virtual identity. Reads that would normally return the physical
device's identifying information are intercepted and substituted with
values associated with the virtual device. The device can later be
unlocked, exposing the real physical identity to a native driver, in
response to a request to a predetermined address. It's a lightweight,
general building block for letting system software manage the *appearance*
of I/O devices independently from their physical reality, without requiring
a full virtualization stack to intervene on every transaction. Because the
mechanism only cares about device identity and access, it applies just as
well to a rack of AI accelerators as it does to a bank of NVMe drives.

## Why This Matters as a System Architect

This isn't the first time I've worked this class of problem. I'm the
architect of record for **Intel VMD** (Volume Management Device), the
hardware underpinning **Intel VROC** (Virtual RAID on CPU). VMD is, at its
core, an I/O aggregation technology. It lets system software manage large
numbers of NVMe drives far more easily, and it enables hot-plug and
software RAID even in the presence of I/O virtualization.

This new patent tackles a kindred scalability and management challenge, but
through a different, more general mechanism, and with an eye toward the
kind of large, fluid device pools that AI infrastructure now demands. It's
not a replacement or extension of VMD, just a related idea from the same
design space. I'm sharing it here as a patent, on its own merits, without
speculating on what Intel may or may not do with it.

## A First-Principles Problem

What I find most representative of how I work as an architect is the way
this idea was derived, not just the claims it produced. It started from
taking VMD apart down to its fundamental function and asking what actually
makes it work at the hardware/software boundary. Underneath all the
plumbing, the core hook is deceptively simple: control what identity a
device presents to software, and you control how software organizes,
pools, and manages that device, without touching the device itself or the
driver stack built around it. Once that hook is isolated, the rest follows
from minimalism. The mechanism in this patent is a small, cheap trick
implemented largely in existing interfaces, no new datapaths, no
significant hardware cost, just a deliberate substitution at the right
place in the read path to fool software into seeing what the system wants
it to see. That's the trade I look for in every design: a small, well-placed
mechanism with disproportionate leverage at the system level.

## Full Patent Portfolio

For anyone curious to dig further, all of my granted patents and pending
applications are publicly searchable through the
[USPTO Patent Public Search tool](https://ppubs.uspto.gov/basic/). Here's
the current list, as of today:

| Patent / Publication No. | Title | Lead Inventor | Publication Date |
|---|---|---|---|
| US 2026/0228328 A1 | Device, Method and System to Protect Communications with a Resource of a Trusted Execution Environment | Shalini Sharma, et al. | 2026-08-06 |
| US 2026/0220060 A1 | Apparatus and Method for Efficient Management of High-Bandwidth IO Links | Filip Schmole, et al. | 2026-07-30 |
| US 2026/0187012 A1 | Methods for Performance-Optimal Tunneling of PCIe UIO/Flit-Mode Packets | Filip Schmole, et al. | 2026-07-02 |
| US 2026/0187234 A1 | Preventing Consumption of Incorrect Data Caused by Silent Drop of Trusted Write from Trusted Input/Output Devices to Private Memory of Trusted Virtual Machines | Shalini Sharma, et al. | 2026-07-02 |
| US 2026/0186839 A1 | Quality of Service Support for Input/Output and Other Agents | Andrew J. Herdrich, et al. | 2026-07-02 |
| **US 12,650,940 B2** | **Device Virtualization Techniques** | **Filip Schmole, et al.** | **2026-06-09** |
| US 2025/0103397 A1 | Quality of Service Support for Input/Output and Other Agents | Andrew J. Herdrich, et al. | 2025-03-27 |
| US 12,248,561 B2 | Apparatus and Method for Role-Based Register Protection for TDX-IO | Vedvyas Shanbhogue, et al. | 2025-03-11 |
| US 2024/0419616 A1 | Memory Access for Multi-Chiplet System-in-Package | Kapil Sood, et al. | 2024-12-19 |
| US 2024/0291786 A1 | Management Control Message Routing | Janusz P. Jurski, et al. | 2024-08-29 |
| US 2024/0272911 A1 | Adjustment of Address Space Allocated to Firmware | Ramamurthy Krithivas, et al. | 2024-08-15 |
| US 2023/0136091 A1 | High-Performance Storage Infrastructure Offload | Kapil Karkra, et al. | 2023-05-04 |
| US 2023/0109533 A1 | Memory Usage Hints Between a Processor of a Server and a Network Interface Device | Daniel Biederman, et al. | 2023-04-06 |
| US 2023/0098288 A1 | Apparatus and Method for Role-Based Register Protection for TDX-IO | Vedvyas Shanbhogue, et al. | 2023-03-30 |
| US 2023/0077239 A1 | Device Virtualization Techniques | Filip Schmole, et al. | 2023-03-09 |
| US 11,216,396 B2 | Persistent Memory Write Semantics on PCIe with Existing TLP Definition | Mark A. Schmisseur, et al. | 2022-01-04 |
| US 2018/0089115 A1 | Persistent Memory Write Semantics on PCIe with Existing TLP Definition | Mark A. Schmisseur, et al. | 2018-03-29 |
