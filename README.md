# 🎙️ Multilingual Voice Form Assistant

A multilingual, offline-first voice assistant that helps users fill out healthcare and civic forms using natural speech instead of typing.

The system listens to the user's voice, converts speech into text using a local speech-recognition model, extracts relevant information using a local LLM, fills the form automatically, and allows the user to confirm or correct the information using voice.

---

## 🚨 Problem

Many healthcare and government forms require users to read, type, and understand complex digital interfaces.

This can create difficulties for:

- Semi-literate users
- Elderly users
- Digitally underserved communities
- Users who are more comfortable speaking in regional languages
- Users concerned about sending sensitive information to cloud services

---

## 💡 Our Solution

The Multilingual Voice Form Assistant allows users to complete forms through a natural voice conversation.

Instead of manually typing information, the user simply speaks.

For example:

> "My name is Atharva Shukla and I am 20 years old."

The system automatically extracts:

```text
Name: Atharva Shukla
Age: 20
