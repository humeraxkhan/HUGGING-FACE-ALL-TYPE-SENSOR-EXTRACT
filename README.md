# 📦 Sensor Query Cleaner + Auto Tagger (WhatsApp Chat Parser)

A Streamlit app to **extract product queries** from **WhatsApp `.txt` chat files**, specifically targeting sensor and industrial product inquiries. This app:

✅ Removes sender names  
✅ Extracts only product lines  
✅ Detects quantities and sensor types  
✅ Supports any `.txt` file format exported from WhatsApp  

---

## 🚀 Features

- 📂 Upload multiple WhatsApp `.txt` chat files  
- 🧠 Auto-detect sensor types like Reed, Proximity, Capacitive, etc.  
- 🧹 Filters out casual messages, confirmations, and photos  
- 🧾 Extracts date, quantity, and product name  
- 📊 Displays clean queries in a table and chart  
- 📥 Download results as Excel (`.xlsx`)

---

## 🧠 Sensor Auto-Tagging Examples

| Sensor Type        | Detected Keywords                     |
|--------------------|----------------------------------------|
| Proximity          | `e2e`, `tl-w5`, `npn`, `pnp`           |
| Reed Switch        | `reed`, `magnetic`                    |
| Capacitive         | `capacitive`, `ec5`                   |
| Photoelectric      | `e3fa`, `photo`, `photocell`          |
| Temperature Sensor | `pt100`, `temperature`                |
| Inductive          | `inductive`                           |
| Pressure           | `pressure`, `dz`                      |
| Other              | Default fallback if unmatched         |

---

## 📤 How to Use

1. Click **“Upload .txt file”** to upload exported WhatsApp chat.
2. App will clean and extract valid product queries.
3. Click **“Download Excel”** to get your result.
4. View bar chart and statistics instantly.

---

## 💡 Exporting WhatsApp Chat

1. Open the chat in WhatsApp  
2. Tap **More > Export Chat > Without Media**  
3. Upload the `.txt` file here

---

## 💻 Tech Stack

- Python 🐍  
- Streamlit 🎈  
- Pandas 📊  
- Regex for pattern cleaning ✨  
- Excel download via `xlsxwriter` 📥

---

## 👩‍💻 Author

Made with 💡 by **Humera Khan**  
Drop feedback anytime!

---

