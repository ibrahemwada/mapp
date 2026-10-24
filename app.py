"""SME Business Assistant — Day 1 database and memory foundation + your favorite UI + BUTTONS WORKING"""

import sqlite3
from datetime import datetime
from pathlib import Path
import re
import pandas as pd
import streamlit as st
import time
import threading
from contextlib import contextmanager
from pathlib import Path
import threading
import time
try:
    import zxingcpp
    import numpy as np
except ImportError:
    zxingcpp = None
    np = None
try:
    from streamlit_webrtc import webrtc_streamer, WebRtcMode
    import av
except ImportError:
    webrtc_streamer = None
    WebRtcMode = None
    av = None
import streamlit.components.v1 as components
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None

DB = Path(__file__).resolve().parent / "sme_business_assistant.db"

st.set_page_config(page_title="SME Business Assistant", page_icon="🏪", layout="wide")

# YOUR FAVORITE UI + MEMORY UI MERGED
st.markdown("""
<style>
.stApp{background:#f5f8fc}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0F1E3A,#0d2039)}
[data-testid="stSidebar"] *{color:#f2f6ff!important}
.brand{font-size:24px;font-weight:800;line-height:1.15}
.brand span{color:#22d3a6}
.panel{background:white;border:1px solid #dce7f6;border-radius:14px;padding:18px;margin-bottom:14px}
.card{background:white;border:1px solid #E5E7EB;border-radius:14px;padding:18px;margin-bottom:16px;box-shadow:0 1px 2px rgba(0,0,0,0.05)}
.assistant-card{background:#F0FDF4;border:1px solid #BBF7D0;border-radius:14px;padding:18px;}
.mic-card{background:#162A4A;padding:18px;border-radius:14px;text-align:center;margin-top:20px;border:1px solid #1E3A8A}
.mic-circle{background:#22d3a6;width:55px;height:55px;border-radius:50%;margin:0 auto;display:flex;align-items:center;justify-content:center;font-size:24px;}
.metric-green{background:#E8F5E9;border-radius:12px;padding:16px;border:1px solid #C8E6C9}
.metric-blue{background:#E3F2FD;border-radius:12px;padding:16px;border:1px solid #BBDEFB}
.metric-orange{background:#FFF3E0;border-radius:12px;padding:16px;border:1px solid #FFE0B2}
.metric-purple{background:#F3E5F5;border-radius:12px;padding:16px;border:1px solid #E1BEE7}
="select"] input {
    color: black !i
</style>
""", unsafe_allow_html=True)

TRANSLATIONS = {
    "English": {
        "morning":"Good morning",
        "happening":"Here's what's happening today.",
        "top":"Top Selling Products",
        "recent":"Recent Sales",
        "add":"Add Product",
        "sale":"Record Sale",
        "exp":"Add Expense",
        "voice":"Voice Assistant",
        "stock_alert":"Stock Alert",
        "online":"Your Assistant - Online",
        "total_today":"Total Sales (Today)",
        "stock_value":"Estimated Stock Value",
        "low_stock":"Low-Stock Products",
        "stock_val2":"Stock Value",
        "from_sales":"↑ from saved sales",
        "products_count":"products",
        "alert_level":"Alert level",
        "total_in_stock":"Total in stock",
        "shop_name_label":"Your shop/business name:",
        "save_business":"Save my business name",
        "first_time":"👋 First time? Type your shop name here so assistant will remember you.",
        "remember":"Memory: I remember you —",
        "debtors": "Debtors",
        "collect_payment": "Collect Payment - small small",
"select_who_paid": "Select who paid you",
"delete_debt": "Delete Debt",
"delete_this_one": "Delete This One",
"delete_all_paid": "Delete ALL Paid",
"how_much_paid_now": "How much they paid now? ₦",
"collect_this_amount": "Collect this amount",
"mark_fully_paid": "Mark Fully Paid",
"delete_debtor": "Delete Debtor",
"delete_confirm": "Delete this debtor permanently?",
        "welcome_greeting": "Good morning {shop}! Your stock value is {value}. You have {low} low stock items.",
        "best_selling_q": "What are my best selling products?",
        "add_stock_title": "Add Stock - Buying & Selling Price",
"add_stock_memory": "Memory: This saves to SQLite - helper will remember.",
"choose_label": "Choose",
"add_existing_radio": "Add stock to an existing product",
"register_new_radio": "Register a new product",
"search_catalogue": "🔍 Search product catalogue",
"no_products_yet": "No products yet. Register a new one first.",
"current_label": "Current",
"qty_received": "Quantity received",
"buying_cost_selected": "Buying cost per selected unit (₦)",
"supplier_note": "Supplier / note",
"save_stock_received": "Save stock received",
"brand_optional": "Brand (optional)",
"stock_unit": "Stock unit",
"buying_price": "Buying price per unit ₦ *",
"quantity": "Quantity *",
"selling_price": "Selling price per unit ₦ *",
"low_stock_alert": "Low-stock alert at",
"size_variant": "Size / variant (optional)",
"save_to_stock": "Save to Stock",
"close_btn": "Close",
"product_name_label": "Product name *",
"business_category": "Business category",
"cat_provisions": "Provisions",
"cat_textiles": "Textiles",
"cat_pharmacy": "Pharmacy",
"cat_electronics": "Electronics",
"cat_others": "Others",
"restock_q": "What should I restock?",
"online": "Assistant",
"debtors_desc": "Add who you owe money — name, date, amount.",
"person_name": "Person Name",
"how_much_owe": "How much you owe",
"date": "Date",
"save_business_name": "Save my business name",
"saved_msg": "Saved! Good morning, {shop}!",
"memory_msg": "Memory: I remember you - {shop}",
"add_stock_title": "Add Stock - Buying & Selling Price",
"product_name_label": "Product Name *",
"product_placeholder": "e.g. Indomie (Carton)",
"business_category": "Business category",
"cat_provisions": "Provisions / Groceries",
"cat_textiles": "Textiles / Fabrics",
"cat_chemist": "Chemist / Pharmacy",
"cat_drinks": "Drinks / Beverages",
"cat_others": "Others",
"reason": "Reason",
"reason_placeholder": "e.g. Rice bag",
"save_debt": "Save Debt",
"total_owe": "Total you owe",
"mark_paid": "Mark as Paid",
"choose_paid": "Choose person to mark as paid",
"paid_btn": "Mark Paid",
"product": "Product",
"qty": "Qty",
"revenue": "Revenue",
"time": "Time",
"total": "Total",
"only_left": "Only {qty} piece left",
"reorder": "Reorder",
"good_morning": "Good morning {shop}! Your stock value is {value}. You have {low} low stock items. Memory is saved in SQLite.",
"best_selling_q": "What are my best selling products?",
"what_restock_q": "What should I restock?",
"restock_label": "Restock:",
    },
    "Hausa": {
        "morning":"Barka da safiya",
        "happening":"Ga abin da ke faruwa yau.",
        "top":"Kayayyaki Mafi Siyarwa",
        "recent":"Siyarwa ta Karshe",
        "add":"Ƙara Kaya",
        "sale":"Rubuta Siyarwa",
        "exp":"Ƙara Kashe Kudi",
        "voice":"Mataimakin Murya",
        "stock_alert":"Gargadin Kaya",
        "online":"Mataimakinka - A Kunnuwa",
        "total_today":"Jimillar Tallace-tallace (Yau)",
        "stock_value":"Kiyasin Darajar Kaya",
        "low_stock":"Kayayyakin da Suka Yi Karanci",
        "stock_val2":"Darajar Kaya",
        "from_sales":"↑ daga tallace-tallacen da aka ajiye",
        "products_count":"kayan kaya",
        "alert_level":"Matsayin gargadi",
        "total_in_stock":"Jimilla a store",
        "shop_name_label":"Sunan shagon ka / kasuwancin ka:",
        "save_business":"Ajiye sunan kasuwancina",
        "first_time":"👋 Farkon shigowa? Rubuta sunan shagon ka anan domin na tuna da kai.",
        "remember":"Na tuna da kai —",
        "debtors": "Bashi",
        "welcome_greeting": "Barka da safiya {shop}! Darajar kayan ka {value} ne. Kayan da suka kusa karewa {low} ne.",
        "best_selling_q": "Wadanne kaya ne suka fi sayuwa?",
        "brand_optional": "Alama (zaɓi ne)",
        "add_existing_radio": "Ƙara kaya ga wanda ke akwai",
        "delete_debt": "Goge bashi",
"delete_this_one": "Goge wannan",
"delete_all_paid": "Goge duk wanda ya biya",
"register_new_radio": "Yi rijistar sabon kaya",
"collect_payment": "Karɓar Bashi - kaɗan kaɗan",
"select_who_paid": "Zaɓi wanda ya biya ka",
"how_much_paid_now": "Nawa ya biya yanzu? ₦",
"collect_this_amount": "Karɓi wannan kuɗin",
"mark_fully_paid": "Alama an biya duka",
"delete_debtor": "Goge Bashin",
"delete_confirm": "Goge wannan bashin gaba daya?",
"search_catalogue": "Bincika jerin kaya",
"qty_received": "Yawan da aka karɓa (guda)",
"buying_cost_selected": "Farashin siyan a na'aura da aka zaɓa (₦)",
"supplier_note": "Mai kaya / bayanin kula",
"save_stock_received": "Ajiye kayan da aka karɓa",
"current_label": "Yanzu",
"stock_unit": "Nau'in Kidaya",
"buying_price": "Farashin siyan ₦ *",
"quantity": "Yawa *",
"selling_price": "Farashin sayarwa ₦ *",
"low_stock_alert": "Gargadi idan ya ragu",
"size_variant": "Girma / nau'i (zaɓi ne)",
"save_to_stock": "Ajiye a Kaya",
"close_btn": "Rufe",
"restock_q": "Me zan sake sayo?",
"online": "Mataimaki",
"debtors_desc": "Yi rubutu wanda kake bin sa bashi — suna, rana, kudi.",
"person_name": "Sunan Mutum",
"how_much_owe": "Nawa kake bin sa?",
"date": "Rana",
"save_business_name": "Ajiye sunan shagon na",
"saved_msg": "An ajiye! Barka da safiya, {shop}!",
"memory_msg": "Na tuna da kai - {shop}",
"add_stock_title": "Kara Kaya - Farashin Siya da Siyarwa",
"product_name_label": "Sunan Kaya *",
"product_placeholder": "e.g. Indomie (Kwatan)",
"business_category": "Nau'in Kasuwanci",
"cat_provisions": "Kayan Abinci",
"cat_textiles": "Yadi",
"cat_chemist": "Magunguna",
"cat_drinks": "Abin Sha",
"cat_others": "Sauran",
"reason": "Dalili",
"reason_placeholder": "e.g. Buhu na shinkafa",
"save_debt": "Ajiye Bashi",
"total_owe": "Jimillar Bashin da kake bi",
"mark_paid": "Alama a matsayin An Biya",
"choose_paid": "Zabi wanda ya biya",
"paid_btn": "An Biya",
"product": "Kaya",
"qty": "Yawa",
"revenue": "Kudin Shiga",
"time": "Lokaci",
"total": "Jimilla",
"only_left": "Sauran {qty} ne kawai",
"reorder": "Sake Siya",
"good_morning": "Barka da safiya {shop}! Darajar kayanka ₦{value} ce. Kana da kaya {low} da suka kusa karewa.",
"best_selling_q": "Wane kaya ne ya fi siyarwa?",
"what_restock_q": "Me zan sake siya?",
"restock_label": "Sake siya:",
"save_business_name": "Ajiye sunan shagon na",
"saved_msg": "An ajiye! Barka da safiya, {shop}!",
"memory_msg": "Na tuna da kai - {shop}",
"add_stock_title": "Kara Kaya - Farashin Siya da Siyarwa",
"product_name_label": "Sunan Kaya *",
"product_placeholder": "e.g. Indomie (Kwatan)",
"business_category": "Nau'in Kasuwanci",
    },
    "Nigerian Pidgin": {
        "morning":"Good morning",
        "happening":"Na wetin dey happen today.",
        "top":"Market wey dey sell pass",
        "recent":"Sales wey just happen",
        "add":"Add New Market",
        "sale":"Write Sale",
        "exp":"Add Money wey you spend",
        "voice":"Person wey dey talk",
        "stock_alert":"Market wey don nearly finish",
        "online":"Your Assistant - Online",
        "total_today":"Total Sales (Today)",
        "stock_value":"How much your market worth",
        "low_stock":"Market wey remain small",
        "stock_val2":"Market Value",
        "from_sales":"↑ from sales wey you save",
        "products_count":"products",
        "alert_level":"Alert level",
        "total_in_stock":"Total for inside store",
        "shop_name_label":"Your shop name:",
        "save_business":"Save my business name",
        "first_time":"👋 First time? Type your shop name make I remember you.",
        "remember":"I remember you —",
        "debtors": "Gbese List",
        "welcome_greeting": "Good morning {shop}! Your market value na {value}. Na {low} items wan finish.",
        "best_selling_q": "Wetin be my best selling products?",
        "brand_optional": "Brand (optional)",
        "add_existing_radio": "Add market to product wey don dey",
        "delete_debt": "Comot Debt",
"Delete this one": "Comot This One",
"delete all paid": "Clear All Wey Don Pay",
"register_new_radio": "Register new product",
"collect_payment": "Collect Payment - small small",
"select_who_paid": "Choose who pay you",
"how_much_paid_now": "How much e pay now? ₦",
"collect_this_amount": "Collect this money",
"mark_fully_paid": "E don pay finish",
"delete_debtor": "Comot this person",
"delete_confirm": "You sure say you wan delete this debtor?",
"search_catalogue": "Search product wey you don add before",
"qty_received": "How many you receive",
"buying_cost_selected": "How much you buy am for this unit (₦)",
"supplier_note": "Supplier / note",
"save_stock_received": "Save stock wey you receive",
"current_label": "Current",
"stock_unit": "How you dey count am",
"buying_price": "How much you buy am ₦ *",
"quantity": "Quantity *",
"selling_price": "Selling price ₦ *",
"low_stock_alert": "Alert when e remain small",
"size_variant": "Size / variant (optional)",
"save_to_stock": "Save for Stock",
"close_btn": "Close",
"restock_q": "Wetin I suppose restock?",
"online": "Assistant",
"debtors_desc": "Write who you dey owe - name, date, amount.",
"person_name": "Person Name",
"how_much_owe": "How much you dey owe?",
"date": "Date",
"save_business_name": "Save my shop name",
"saved_msg": "Don save! Good morning, {shop}!",
"memory_msg": "I remember you - {shop}",
"add_stock_title": "Add Market - Price Wey You Buy and Sell",
"product_name_label": "Market Name *",
"product_placeholder": "e.g. Indomie (Carton)",
"business_category": "Type of Business",
"cat_provisions": "Food / Groceries",
"cat_textiles": "Clothes / Fabrics",
"cat_chemist": "Chemist / Drugs",
"cat_drinks": "Drinks",
"cat_others": "Others",
"reason": "Wetin happen",
"reason_placeholder": "e.g. Bag of rice",
"save_debt": "Save Gbese",
"total_owe": "Total Gbese you dey owe",
"mark_paid": "Mark as you don pay",
"choose_paid": "Choose who you pay",
"paid_btn": "Don Pay",
"product": "Market",
"qty": "How many",
"revenue": "Money wey you make",
"time": "Time",
"total": "Total",
"only_left": "Na {qty} remain",
"reorder": "Go buy again",
"good_morning": "Good morning {shop}! Your market value na {value}. You get {low} market wey don nearly finish.",
"best_selling_q": "Wetin be my market wey dey sell pass?",
"what_restock_q": "Wetin I suppose restock?",
"restock_label": "Buy again:",
"save_business_name": "Save my shop name",
"saved_msg": "Don save! Good morning, {shop}!",
"memory_msg": "I remember you - {shop}",
"add_stock_title": "Add Market - Price Wey You Buy and Sell",
"product_name_label": "Market Name *",
"product_placeholder": "e.g. Indomie (Carton)",
"business_category": "Type of Business",
    }
}
def t(k): return TRANSLATIONS.get(st.session_state.get("lang","English"), TRANSLATIONS["English"]).get(k,k)
def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con

def now():
    return datetime.now().isoformat(timespec="seconds")

def init_db():
    with db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS products(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, category TEXT NOT NULL, brand TEXT DEFAULT '',
            variant TEXT DEFAULT '', unit TEXT NOT NULL, buy REAL DEFAULT 0,
            sell REAL DEFAULT 0, stock REAL DEFAULT 0, low_level REAL DEFAULT 5,
            created TEXT NOT NULL)""")
        con.execute("""CREATE TABLE IF NOT EXISTS stock_movements(
            id INTEGER PRIMARY KEY AUTOINCREMENT, product_id INTEGER NOT NULL,
            movement TEXT NOT NULL, quantity REAL NOT NULL, unit TEXT NOT NULL,
            unit_cost REAL DEFAULT 0, note TEXT DEFAULT '', created TEXT NOT NULL,
            FOREIGN KEY(product_id) REFERENCES products(id))""")
        con.execute("""CREATE TABLE IF NOT EXISTS business_profile(
            id INTEGER PRIMARY KEY CHECK(id = 1), business_name TEXT DEFAULT '',
            business_type TEXT DEFAULT 'General shop', preferred_language TEXT DEFAULT 'English',
            owner_preferences TEXT DEFAULT '', updated_at TEXT NOT NULL)""")
        con.execute("""INSERT OR IGNORE INTO business_profile
            (id, business_name, business_type, preferred_language, owner_preferences, updated_at)
            VALUES (1, '', 'General shop', 'English', '',?)""", (now(),))
        con.execute("""CREATE TABLE IF NOT EXISTS assistant_memory(
            id INTEGER PRIMARY KEY AUTOINCREMENT, memory_type TEXT NOT NULL,
            memory_key TEXT NOT NULL UNIQUE, memory_value TEXT NOT NULL,
            created_at TEXT NOT NULL, updated_at TEXT NOT NULL)""")
        con.execute("""CREATE TABLE IF NOT EXISTS assistant_messages(
            id INTEGER PRIMARY KEY AUTOINCREMENT, role TEXT NOT NULL,
            content TEXT NOT NULL, created_at TEXT NOT NULL)""")
        con.execute("""CREATE TABLE IF NOT EXISTS customers(
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, phone TEXT DEFAULT '',
            notes TEXT DEFAULT '', created_at TEXT NOT NULL)""")
        con.execute("""CREATE TABLE IF NOT EXISTS sales(
            id INTEGER PRIMARY KEY AUTOINCREMENT, customer_id INTEGER,
            subtotal REAL DEFAULT 0, discount REAL DEFAULT 0,
            total REAL DEFAULT 0, paid REAL DEFAULT 0,
            status TEXT DEFAULT 'completed', note TEXT DEFAULT '', created_at TEXT NOT NULL)""")
        con.execute("""CREATE TABLE IF NOT EXISTS sale_items(
            id INTEGER PRIMARY KEY AUTOINCREMENT, sale_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL, quantity REAL NOT NULL,
            unit TEXT NOT NULL, unit_price REAL NOT NULL, line_total REAL NOT NULL,
            FOREIGN KEY(sale_id) REFERENCES sales(id),
            FOREIGN KEY(product_id) REFERENCES products(id))""")
        con.execute("""CREATE TABLE IF NOT EXISTS expenses(
            id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT NOT NULL,
            amount REAL NOT NULL, description TEXT DEFAULT '', created_at TEXT NOT NULL)""")
    con.execute("""CREATE TABLE IF NOT EXISTS debtors(
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
            amount REAL NOT NULL, debt_date TEXT NOT NULL,
            note TEXT DEFAULT '', status TEXT DEFAULT 'unpaid',
            created_at TEXT NOT NULL)""")
def get_products():
    with db() as con:
        return pd.read_sql_query("SELECT * FROM products ORDER BY name COLLATE NOCASE", con)

def naira(amount): return f"₦{float(amount):,.2f}"
def product_label(row):
    parts=[str(row["name"])]
    if row["brand"]: parts.append(str(row["brand"]))
    if row["variant"]: parts.append(str(row["variant"]))
    parts.append(str(row["category"]))
    return " — ".join(parts)

def get_profile():
    with db() as con:
        return con.execute("SELECT * FROM business_profile WHERE id=1").fetchone()

def save_memory(memory_type, key, value):
    stamp=now()
    with db() as con:
        con.execute("""INSERT INTO assistant_memory(memory_type,memory_key,memory_value,created_at,updated_at)
            VALUES(?,?,?,?,?) ON CONFLICT(memory_key) DO UPDATE SET
            memory_type=excluded.memory_type, memory_value=excluded.memory_value,
            updated_at=excluded.updated_at""", (memory_type, key.strip(), value.strip(), stamp, stamp))

def answer_question(question):
    q = re.sub(r"\s+", " ", question.strip().lower())
    if not q: return "Please type a question about your saved business records."
    profile=get_profile()
    business_name=profile["business_name"].strip() if profile and profile["business_name"] else "your business"
    products=get_products()
    if any(g in q for g in ["hello","good morning","sannu","ina kwana"]):
        return f"Hello! I am ready to help with {business_name}. I can answer about products, stock levels, low-stock and stock value from saved records."
    if any(term in q for term in ["low stock","running low","almost finish","restock"]):
        if products.empty: return "I don't have any products saved yet. Add products first."
        low=products[products["stock"] <= products["low_level"]]
        if low.empty: return "No products are currently at or below their low-stock alert level."
        lines=[f"• {r['name']}: {r['stock']:g} {r['unit']} left; alert is {r['low_level']:g}" for _,r in low.head(12).iterrows()]
        return "Low stock:\n" + "\n".join(lines)
    if any(term in q for term in ["stock value","inventory value"]):
        value=float((products["stock"]*products["buy"]).sum()) if not products.empty else 0.0
        return f"Estimated stock value at buying prices is {naira(value)}. This is estimate, not cash."
    if any(term in q for term in ["how many products","product types"]):
        return f"There are {len(products)} product records."
    if any(term in q for term in ["show products","list products","my products"]):
        if products.empty: return "Catalogue is empty. Use 'Add Stock / Products' to register."
        lines=[f"• {r['name']}: {r['stock']:g} {r['unit']}" for _,r in products.head(15).iterrows()]
        return "Saved products:\n" + "\n".join(lines)
    matches=[]
    if not products.empty:
        for _,row in products.iterrows():
            if str(row["name"]).lower() in q: matches.append((len(str(row["name"])),row))
        matches.sort(key=lambda x:x[0],reverse=True)
    if matches:
        row=matches[0][1]
        return (f"Saved record for {row['name']}:\n• Stock: {row['stock']:g} {row['unit']}\n• Buying: {naira(row['buy'])}\n• Selling: {naira(row['sell'])}\n• Low alert: {row['low_level']:g}")
    return "I don't know that from saved records. Ask about a saved product, stock balance, low-stock, count or stock value."

init_db()
products=get_products()
if 'lang' not in st.session_state: st.session_state.lang=get_profile()["preferred_language"] or "English"
# === FIX FOR BUTTONS - DON'T CHANGE YOUR DESIGN ===
if 'show_add' not in st.session_state: st.session_state.show_add=False
if 'show_sale' not in st.session_state: st.session_state.show_sale=False
if 'show_exp' not in st.session_state: st.session_state.show_exp=False
if 'show_voice' not in st.session_state: st.session_state.show_voice=False

# SIDEBAR WITH MIC BACK
with st.sidebar:
    st.markdown('<div class="brand">🏪 SME Business<br><span>Assistant</span></div>', unsafe_allow_html=True)
    st.caption("Your business. Your language. Your assistant.")
        # === LANGUAGE SELECTOR ===
    sel_lang = st.radio("lang", ["English","Hausa","Nigerian Pidgin"], label_visibility="collapsed", key="lang_radio", index=["English","Hausa","Nigerian Pidgin"].index(st.session_state.lang) if st.session_state.lang in ["English","Hausa","Nigerian Pidgin"] else 0)
    if sel_lang != st.session_state.lang:
        st.session_state.lang = sel_lang
        st.rerun()

    # === Navigation that CHANGES with language ===
    eng_menu = ["Dashboard","Assistant","Add Stock / Products","Product Catalogue","Smart calculator","Debtors","Settings"]
    if st.session_state.lang == "Hausa":
        display_menu = ["Allon Gida","Mataimaki","Ƙara Kaya","Jerin Kaya","smart calculator","Bin Bashin","Saiti"]
    elif st.session_state.lang == "Nigerian Pidgin":
        display_menu = ["Dashboard","Helper","Add Market","Product List","smart calcularor","People Wey Owe You","Settings"]
    else:
        display_menu = eng_menu

    menu_map = dict(zip(display_menu, eng_menu))
    page_display = st.radio("Navigation", display_menu, label_visibility="collapsed", key="nav_radio")
    page = menu_map[page_display]
   

profile=get_profile()
business_label=profile["business_name"].strip() if profile and profile["business_name"] else "your business"

if page=="Dashboard":
    # === YOUR FAVORITE - SHOP NAME ASK + GOOD MORNING FIX ===
    if not business_label or business_label == "your business":
        st.warning(t('first_time'))
        new_shop = st.text_input(t('shop_name_label'), value="ibrahim store", key="dash_shop_name")
        if st.button(t('save_business_name'), type="primary"):
            if new_shop.strip():
                with db() as con:
                    con.execute("UPDATE business_profile SET business_name=?, updated_at=? WHERE id=1", (new_shop.strip(), now()))
                st.success(t('saved_msg').format(shop=new_shop.strip()))
                st.rerun()
    else:
        st.success(f"{t('memory_msg').format(shop=business_label)} ✅")

    profile=get_profile()
    business_label=profile["business_name"].strip() if profile and profile["business_name"] else "your business"

    st.markdown(f"### ☀️ {t('morning')}, {business_label}")
    st.caption(f"{t('happening')} | {datetime.now().strftime('%a %d %b %Y')}")

    value=(products["stock"]*products["buy"]).sum() if not products.empty else 0
    low=int((products["stock"] <= products["low_level"]).sum()) if not products.empty else 0
    with db() as con:
        sales_df=pd.read_sql_query("SELECT total, created_at FROM sales ORDER BY id DESC", con)
    total_sales=sales_df["total"].sum() if not sales_df.empty else 0

    m1,m2,m3,m4=st.columns(4)
    m1.markdown(f"<div class='metric-green'><small>{t('total_today')}</small><h3>₦{total_sales:,.0f}</h3><small style='color:green'>{t('from_sales')}</small></div>", unsafe_allow_html=True)
    m2.markdown(f"<div class='metric-blue'><small>{t('stock_value')}</small><h3>{naira(value)}</h3><small>{len(products)} {t('products_count')}</small></div>", unsafe_allow_html=True)
    m3.markdown(f"<div class='metric-orange'><small>{t('low_stock')}</small><h3>{low} items</h3><small>{t('alert_level')}</small></div>", unsafe_allow_html=True)
    m4.markdown(f"<div class='metric-purple'><small>{t('stock_val2')}</small><h3>{naira(value)}</h3><small>{t('total_in_stock')}</small></div>", unsafe_allow_html=True)
    st.write("")
    # === YOUR 4 BUTTONS NOW WORKING - SAME DESIGN ===
    b1,b2,b3,b4=st.columns(4)
    if b1.button(f"➕ {t('add')}", use_container_width=True, type="primary"):
        st.session_state.show_add=True; st.session_state.show_sale=False; st.session_state.show_exp=False; st.session_state.show_voice=False
    if b2.button(f"🧾 {t('sale')}", use_container_width=True):
        st.session_state.show_sale=True; st.session_state.show_add=False; st.session_state.show_exp=False; st.session_state.show_voice=False
    if b3.button(f"💼 {t('exp')}", use_container_width=True):
        st.session_state.show_exp=True; st.session_state.show_add=False; st.session_state.show_sale=False; st.session_state.show_voice=False
    if b4.button(f"🎤 {t('voice')}", use_container_width=True):
        st.session_state.show_voice=True; st.session_state.show_add=False; st.session_state.show_sale=False; st.session_state.show_exp=False

    # ---- 1. ADD PRODUCT OPENS HERE ----
    if st.session_state.show_add:
        st.markdown("---")
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader(f"🟡 {t('add_stock_title')}")
        with st.form("dash_add", clear_on_submit=True):
            name=st.text_input(t('product_name_label'), placeholder=t('product_placeholder'))
            left,right=st.columns(2)
            with left:
                category=st.selectbox(t('business_category'), [t('cat_provisions'), t('cat_textiles'), t('cat_pharmacy'), t('cat_electronics'), t('cat_others')], key="dash_cat")
                brand=st.text_input(t('brand_optional'))
                unit=st.selectbox(t('stock_unit'), ["piece","pack","carton","bag","crate","bottle","sachet"])
                buy=st.number_input(t('buying_price'), min_value=0.0, step=50.0)
            with right:
                qty=st.number_input(t('quantity'), min_value=0.0, value=10.0, step=1.0)
                sell=st.number_input(t('selling_price'), min_value=0.0, step=50.0)
                low_level=st.number_input(t('low_stock_alert'), min_value=0.0, value=5.0)
                variant=st.text_input(t('size_variant'))
            c1,c2=st.columns(2)
            do_save=c1.form_submit_button(f"💾 {t('save_to_stock')}", use_container_width=True, type="primary", key="dash_add_save")
            do_close=c2.form_submit_button(t('close_btn'), use_container_width=True, key="dash_add_close")
            if do_close: st.session_state.show_add=False; st.rerun()
            if do_save:
                if not name.strip(): st.error("Product name required")
                elif buy<=0 or sell<=0: st.error("Fill buying and selling")
                elif sell<=buy: st.error("Selling must be > Buying")
                else:
                    with db() as con:
                        cur=con.execute("INSERT INTO products(name,category,brand,variant,unit,buy,sell,stock,low_level,created) VALUES(?,?,?,?,?,?,?,?,?,?)",(name.strip(),category,brand.strip(),variant.strip(),unit,buy,sell,qty,low_level,now()))
                        con.execute("INSERT INTO stock_movements(product_id,movement,quantity,unit,unit_cost,note,created) VALUES(?,?,?,?,?,?,?)",(cur.lastrowid,"STOCK IN",qty,unit,buy,"Dashboard add",now()))
                    st.success(f"✅ {name} saved! Memory will remember"); st.session_state.show_add=False; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # ---- 2. RECORD SALE OPENS HERE ----
    if st.session_state.show_sale:
        st.markdown("---")
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("🧾 Record Sale - Sell from memory")
        if products.empty:
            st.warning("No products yet. Press Add Product first.")
        else:
            prod_name=st.selectbox("Choose product to sell", products["name"].tolist(), key="sale_prod")
            row=products[products["name"]==prod_name].iloc[0]
            st.info(f"Available: {row['stock']:g} {row['unit']} | Sell at: ₦{row['sell']:,.0f} | Profit: ₦{row['sell']-row['buy']:,.0f} each")
            q=st.number_input(f"How many {row['unit']} to sell?", 1.0, float(row["stock"]) if row["stock"]>0 else 1.0, 1.0)
         
            if st.button("💵 Confirm Sale", type="primary", use_container_width=True):
                total=q*row["sell"]
                with db() as con:
                    con.execute("UPDATE products SET stock=stock-? WHERE id=?", (q, int(row["id"])))
                    cur=con.execute("INSERT INTO sales(total,paid,status,note,created_at) VALUES(?,?,?,?,?)",(total,total,"completed",f"Sold {prod_name}",now()))
                    con.execute("INSERT INTO sale_items(sale_id,product_id,quantity,unit,unit_price,line_total) VALUES(?,?,?,?,?,?)",(cur.lastrowid,int(row["id"]),q,row["unit"],row["sell"],total))
                st.success(f"Sold {q:g} x {prod_name} = ₦{total:,.0f}"); st.session_state.show_sale=False; st.rerun()
            if st.button("Close sale", key="close_sale"): st.session_state.show_sale=False; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # ---- 3. ADD EXPENSE OPENS HERE ----
    if st.session_state.show_exp:
        st.markdown("---")
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("💼 Add Expense")
        with st.form("dash_exp", clear_on_submit=True):
            desc=st.text_input("What did you spend on? e.g. Transport")
            amount=st.number_input("Amount ₦", 0.0, step=100.0)
            cat=st.selectbox("Category", ["Transport","Rent","Light","Airtime","Others"])
            c1,c2=st.columns(2)
            do_save=c1.form_submit_button("Save Expense", type="primary", use_container_width=True)
            do_close=c2.form_submit_button("Close", use_container_width=True)
            if do_close: st.session_state.show_exp=False; st.rerun()
            if do_save:
                if desc and amount>0:
                    with db() as con:
                        con.execute("INSERT INTO expenses(category,amount,description,created_at) VALUES(?,?,?,?)",(cat,amount,desc,now()))
                    st.success(f"Expense ₦{amount:,.0f} saved!"); st.session_state.show_exp=False; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # ---- 4. VOICE ASSISTANT OPENS HERE ----
    if st.session_state.show_voice:
        st.markdown("---")
        st.markdown("<div class='assistant-card'>", unsafe_allow_html=True)
        st.subheader(f"🎤 Voice Assistant - Online ●")
        st.success(f"I understand English, Hausa, Pidgin. Memory ready for {business_label}.")
        v=st.text_input("Ask...", placeholder="What is my profit? / Nawa ne riba ta?", key="voice_ask")
        if v:
            st.info(answer_question(v))
        if st.button("Close voice", key="close_voice"): st.session_state.show_voice=False; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    left,right=st.columns([1.5,1])
    with left:
        with st.expander(f"🏆 {t('top')}", expanded=False):
          if products.empty:
            st.markdown("<div class='card'>No products yet. Add in 'Add Stock / Products'.<br><br><table style='width:100%'><tr style='color:#64748B'><th>#</th><th>Product</th><th>Quantity Sold</th><th>Revenue</th></tr><tr><td>1</td><td>Indomie (Carton) - Demo</td><td>12 cartons</td><td>₦72,000</td></tr></table></div>", unsafe_allow_html=True)
          else:
            with db() as con:
                top=pd.read_sql_query("""SELECT p.name as Product, SUM(si.quantity) as Qty, SUM(si.line_total) as Revenue
                FROM sale_items si JOIN products p ON p.id=si.product_id GROUP BY p.name ORDER BY Qty DESC LIMIT 10""", con)
            if top.empty:
                st.markdown("<div class='card'>No sales yet - Your Product + Qty will show here after you sell.<br>Current stock preview:</div>", unsafe_allow_html=True)
                st.dataframe(products[["name","stock","unit"]].rename(columns={"name":"Product","stock":"Qty","unit":"Unit"}), use_container_width=True, hide_index=True)
            else:
                st.dataframe(top, use_container_width=True, hide_index=True)

        with st.expander(f"⚠️ {t('stock_alert')}", expanded=False):
          if products.empty:
            st.markdown("<div class='card' style='background:#F0FDF4'>No low stock - Nothing added yet</div>", unsafe_allow_html=True)
          else:
            low_df=products[products["stock"]<=products["low_level"]]
            if low_df.empty: st.success("All stocks are good!")
            else:
                for _,r in low_df.iterrows():
                    st.markdown(f"<div class='card' style='background:#FFF1F2'>{r['name']} - Only {r['stock']:g} {r['unit']} left <span style='float:right;background:#DC2626;color:white;padding:4px 10px;border-radius:8px'>{t('reorder')}</spaan></div>", unsafe_allow_html=True)

    with right:
      with st.expander(f"📋 {t('recent')}", expanded=False):
        with db() as con:
            recent=pd.read_sql_query("""SELECT s.created_at as Time, p.name as Product, si.quantity as Qty, si.line_total as Total
            FROM sale_items si JOIN sales s ON s.id=si.sale_id JOIN products p ON p.id=si.product_id ORDER BY s.id DESC LIMIT 8""", con)
        if recent.empty:
            st.markdown("<div class='card'><table style='width:100%'><tr style='color:#64748B'><th>Time</th><th>Product</th><th>Qty</th><th>Total</th></tr><tr><td>09:42 AM</td><td>Indomie (Carton)</td><td>2</td><td>₦16,000</td></tr><tr><td>10:15 AM</td><td>Peak Milk</td><td>1</td><td>₦6,000</td></tr></table><small style='color:gray'>Demo - real Time + Product will show after sales</small></div>", unsafe_allow_html=True)
        else:
            st.dataframe(recent, use_container_width=True, hide_index=True)

        st.markdown(f"<div class='assistant-card'><b>✨ {t('online')}</b> <span style='float:right;color:#16A34A;font-size:12px'>● Online</span><p style='margin-top:10px'>{t('welcome_greeting').format(shop=business_label, value=naira(value), low=low)}</p>",unsafe_allow_html=True)
        if st.button("What are my best selling products?"): st.info(t('check_top'))
        if st.button("What should I restock?"):
            if not products.empty:
                low_names=products[products["stock"]<=products["low_level"]]["name"].tolist()
                st.info(f"Restock: {', '.join(low_names) if low_names else 'Nothing for now'}")

elif page=="Assistant":
    st.header("Business Assistant - Memory Mode")
    st.write(f"Ask about saved records for {business_label}. Uses Python rules + SQLite, no external AI yet.")
    with db() as con:
        messages=con.execute("SELECT role, content, created_at FROM assistant_messages ORDER BY id DESC LIMIT 30").fetchall()
    for m in reversed(messages):
        with st.chat_message(m["role"]): st.markdown(m["content"])
    prompt=st.chat_input("Ask about your business records…")
    if prompt:
        reply=answer_question(prompt)
        with db() as con:
            con.execute("INSERT INTO assistant_messages(role,content,created_at) VALUES(?,?,?)",("user",prompt,now()))
            con.execute("INSERT INTO assistant_messages(role,content,created_at) VALUES(?,?,?)",("assistant",reply,now()))
        st.rerun()
    if st.button("Clear chat history"):
        with db() as con: con.execute("DELETE FROM assistant_messages")
        st.rerun()

elif page=="Add Stock / Products":
    st.header("📦 Add Stock / Products")

    APP_DIR_ADD = Path(__file__).resolve().parent
    DB_PATH_ADD = APP_DIR_ADD / "sme_barcode_test.db"

    @contextmanager
    def db_add():
        con = sqlite3.connect(DB_PATH_ADD, timeout=10)
        con.row_factory = sqlite3.Row
        try:
            yield con
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()

    def now_add():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def init_db_add():
        with db_add() as con:
            con.execute("""CREATE TABLE IF NOT EXISTS products 
                (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, category TEXT NOT NULL DEFAULT '', 
                brand TEXT NOT NULL DEFAULT '', variant TEXT NOT NULL DEFAULT '', unit TEXT NOT NULL DEFAULT 'piece', 
                buy REAL NOT NULL DEFAULT 0, sell REAL NOT NULL DEFAULT 0, stock REAL NOT NULL DEFAULT 0, 
                low_level REAL NOT NULL DEFAULT 5, created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""")
            cols = {r["name"] for r in con.execute("PRAGMA table_info(products)").fetchall()}
            if "barcode" not in cols:
                con.execute("ALTER TABLE products ADD COLUMN barcode TEXT")
            if "subunit" not in cols:
                con.execute("ALTER TABLE products ADD COLUMN subunit TEXT DEFAULT ''")
            if "subunits_per_unit" not in cols:
                con.execute("ALTER TABLE products ADD COLUMN subunits_per_unit REAL DEFAULT 1")
            if "buy_subunit" not in cols:
                con.execute("ALTER TABLE products ADD COLUMN buy_subunit REAL DEFAULT 0")
            if "sell_subunit" not in cols:
                con.execute("ALTER TABLE products ADD COLUMN sell_subunit REAL DEFAULT 0")
            con.execute("""CREATE TABLE IF NOT EXISTS stock_movements 
                (id INTEGER PRIMARY KEY AUTOINCREMENT, product_id INTEGER NOT NULL, movement TEXT NOT NULL, 
                quantity REAL NOT NULL, unit TEXT NOT NULL, unit_cost REAL NOT NULL DEFAULT 0, 
                note TEXT NOT NULL DEFAULT '', created TEXT NOT NULL, 
                FOREIGN KEY(product_id) REFERENCES products(id))""")
            con.execute("""CREATE UNIQUE INDEX IF NOT EXISTS idx_products_barcode_unique ON products(barcode) WHERE barcode IS NOT NULL AND TRIM(barcode) != ''""")

    def get_products_add():
        with db_add() as con:
            return con.execute("SELECT * FROM products ORDER BY name COLLATE NOCASE").fetchall()

    def get_product_by_barcode_add(barcode):
        barcode = (barcode or "").strip()
        if not barcode: return None
        with db_add() as con:
            return con.execute("SELECT * FROM products WHERE barcode = ? LIMIT 1", (barcode,)).fetchone()

    def product_caption_add(p):
        parts = [p["name"]]
        if p["brand"]: parts.append(p["brand"])
        if p["variant"]: parts.append(p["variant"])
        parts.append(f"(barcode: {p['barcode'] or 'not set'})")
        return " — ".join(parts)

    def add_movement_add(con, pid, mov, qty, unit, cost, note):
        con.execute("INSERT INTO stock_movements (product_id, movement, quantity, unit, unit_cost, note, created) VALUES (?,?,?,?,?,?,?)",
                    (pid, mov, qty, unit, cost, note, now_add()))

    def save_stock_received_add(product, qty, cost, note):
        buy_subunit = round(float(cost) / float(product["subunits_per_unit"] or 1), 2) if product["subunit"] else 0.0
        with db_add() as con:
            con.execute("UPDATE products SET stock = stock + ?, buy = ?, buy_subunit = ? WHERE id = ?", (qty, cost, buy_subunit, int(product["id"])))
            add_movement_add(con, int(product["id"]), "STOCK IN", qty, product["unit"], cost, note.strip())

    def render_stock_in_form_add(product, form_key):
        st.subheader(product["name"])
        details = [f"**Current stock:** {product['stock']:g} {product['unit']}", f"**Buying price:** ₦{product['buy']:,.2f} per {product['unit']}"]
        if product["subunit"]:
            count = float(product["subunits_per_unit"] or 1)
            details.append(f"**Smaller unit:** {count:g} {product['subunit']}(s) per {product['unit']}")
            details.append(f"**Selling price:** ₦{float(product['sell_subunit']):,.2f} per {product['subunit']}")
        if product["barcode"]: details.append(f"**Barcode:** `{product['barcode']}`")
        st.markdown("  |  ".join(details))
        with st.form(form_key):
            qty = st.number_input("Quantity received", min_value=0.001, value=1.0, step=1.0)
            cost = st.number_input("Buying cost per unit (₦)", min_value=0.0, value=float(product["buy"]), step=50.0)
            note = st.text_input("Supplier / note (optional)")
            submitted = st.form_submit_button("Save stock received", type="primary")
        if submitted:
            save_stock_received_add(product, float(qty), float(cost), note)
            st.session_state["test_notice"] = f"Stock updated for {product['name']}."
            st.rerun()

    class LiveBarcodeProcessorAdd:
        def __init__(self, result_queue):
            self.result_queue = result_queue
            self.last_value = ""
            self.last_time = 0.0
            self.lock = threading.Lock()
        def recv(self, frame):
            image = frame.to_ndarray(format="rgb24")
            if zxingcpp is not None and np is not None:
                try:
                    results = zxingcpp.read_barcodes(image)
                    if results:
                        value = next((r.text.strip() for r in results if r.text.strip()), "")
                        if value:
                            with self.lock:
                                if value != self.last_value or time.time() - self.last_time > 2:
                                    self.result_queue.put(value)
                                    self.last_value = value
                                    self.last_time = time.time()
                except Exception:
                    pass
            return frame

    def play_beep_add():
        components.html("""<script>const Ctx = window.AudioContext || window.webkitAudioContext; if (Ctx) { const ctx = new Ctx(); const osc = ctx.createOscillator(); const gain = ctx.createGain(); osc.type='sine'; osc.frequency.value=880; gain.gain.value=0.15; osc.connect(gain); gain.connect(ctx.destination); osc.start(); osc.stop(ctx.currentTime+0.16); }</script>""", height=0)

    def camera_barcode_input_add(prefix, barcode_state_key):
        st.markdown("**Live camera scanner**")
        if webrtc_streamer is None or zxingcpp is None or np is None:
            st.warning("Live camera packages are missing. Install requirements.")
            return
        open_key = f"{prefix}_camera_open"
        if open_key not in st.session_state:
            st.session_state[open_key] = False
        col_open, col_close = st.columns(2)
        with col_open:
            if st.button("📷 Open Camera", key=f"{prefix}_open_button", disabled=st.session_state[open_key], use_container_width=True):
                st.session_state[open_key] = True
                st.rerun()
        with col_close:
            if st.button("⏹ Close Camera", key=f"{prefix}_close_button", disabled=not st.session_state[open_key], use_container_width=True):
                st.session_state[open_key] = False
                st.rerun()
        if st.session_state[open_key]:
            if st_autorefresh is not None:
                st_autorefresh(interval=500, key=f"{prefix}_camera_poll")
            if f"{prefix}_queue" not in st.session_state:
                import queue
                st.session_state[f"{prefix}_queue"] = queue.Queue()
            result_queue = st.session_state[f"{prefix}_queue"]
            st.caption("Live video is active. Hold one barcode steady.")
            webrtc_streamer(key=f"{prefix}_live_video", mode=WebRtcMode.SENDRECV, video_processor_factory=lambda: LiveBarcodeProcessorAdd(result_queue), media_stream_constraints={"video": True, "audio": False}, async_processing=True)
            latest = None
            try:
                while True:
                    latest = result_queue.get_nowait()
            except Exception:
                pass
            if latest:
                previous = st.session_state.get(f"{prefix}_last_detected")
                st.session_state[f"{prefix}_last_detected"] = latest
                if st.session_state.get(barcode_state_key) != latest:
                    st.session_state[barcode_state_key] = latest
                    st.session_state[f"{prefix}_beep_pending"] = True
                    st.rerun()
                elif previous != latest:
                    st.session_state[f"{prefix}_beep_pending"] = True
        if st.session_state.pop(f"{prefix}_beep_pending", False):
            play_beep_add()
            st.success(f"Barcode captured: {st.session_state.get(barcode_state_key, '')}")

    # --- MAIN LOGIC (SAME AS YOUR app.py main()) ---
    init_db_add()
    st.caption(f"DB: {DB_PATH_ADD.name} | Pro version - bag=mudu, carton=piece")
    notice = st.session_state.pop("test_notice", None)
    if notice:
        st.success(notice)

    mode = st.radio("Choose what you want to do", ["Add to Existing Stock", "Register New Stock"], horizontal=True)

    if mode == "Add to Existing Stock":
        st.subheader("Add to Existing Stock")
        camera_barcode_input_add("existing", "existing_barcode")
        barcode = st.text_input("Or enter barcode manually", key="existing_barcode").strip()
        if barcode:
            product = get_product_by_barcode_add(barcode)
            if product:
                st.success("Barcode found locally.")
                render_stock_in_form_add(product, f"stock_in_barcode_{product['id']}")
            else:
                st.warning("Barcode not found locally. Register first.")
        if not barcode:
            products = get_products_add()
            if not products:
                st.info("No products yet. Go to Register New Stock")
            else:
                product_map = {product_caption_add(p): p for p in products}
                choice = st.selectbox("Or select by name", list(product_map.keys()), index=None, placeholder="Type to search…")
                if choice:
                    render_stock_in_form_add(product_map[choice], f"stock_in_manual_{product_map[choice]['id']}")

    else:
        st.subheader("Register New Stock")
        camera_barcode_input_add("new_product", "new_product_barcode")
        barcode = st.text_input("Or enter barcode manually (optional)", key="new_product_barcode").strip()
        duplicate = get_product_by_barcode_add(barcode) if barcode else None
        if duplicate:
            st.error(f"Already registered to ‘{duplicate['name']}’")

        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Product name *", key="register_name")
            category = st.selectbox("Category", ["Provisions", "Textiles", "Pharmacy", "Electronics", "Others"], key="register_category")
            brand = st.text_input("Brand (optional)", key="register_brand")
            variant = st.text_input("Size / variant", key="register_variant")
            unit = st.selectbox("Stock unit", ["piece","pack","carton","bag","crate","bottle","sachet","kg","g","litre","ml","dozen","box","bundle","roll"], key="register_unit")
        with col2:
            qty = st.number_input("Opening quantity", min_value=0.0, value=1.0, step=1.0, key="register_opening_qty")
            buy = st.number_input("Buying price per main unit (₦)", min_value=0.0, step=50.0, key="register_buy")
            sell = st.number_input("Selling price per main unit (₦)", min_value=0.0, step=50.0, key="register_sell")
            low_level = st.number_input("Low-stock alert level", min_value=0.0, value=5.0, step=1.0, key="register_low_level")

        default_subunits = {"pack":"piece","carton":"piece","crate":"piece","bag":"mudu","dozen":"piece","box":"piece","bundle":"piece","kg":"g","g":"mg","litre":"ml","bottle":"ml","roll":"metre"}
        options_by_unit = {"pack":["piece","sachet"],"carton":["piece","bottle","sachet"],"crate":["piece","bottle"],"bag":["mudu","kg","g","cup"],"dozen":["piece"],"box":["piece","sachet"],"bundle":["piece"],"kg":["g"],"g":["mg"],"litre":["ml"],"bottle":["ml"],"roll":["metre","yard"]}
        default_subunit = default_subunits.get(unit, "piece")
        default_track_subunit = unit in default_subunits
        track_subunit = st.checkbox("Also sell this product by a smaller unit (e.g. piece or mudu)", value=default_track_subunit, key=f"register_track_subunit_{unit}")

        subunit = ""
        subunits_per_unit = 1.0
        sell_subunit = 0.0
        buy_subunit = 0.0
        if track_subunit:
            subunit_options = options_by_unit.get(unit, ["piece","mudu","bottle","sachet","g","ml","cup","other"])
            subunit_index = subunit_options.index(default_subunit) if default_subunit in subunit_options else 0
            subunit = st.selectbox("Smaller selling unit", subunit_options, index=subunit_index, key=f"register_subunit_{unit}")
            subunits_per_unit = st.number_input(f"How many {subunit}(s) are in 1 {unit}?", min_value=1.0, value=1.0, step=1.0, key=f"register_subunit_count_{unit}_{subunit}")
            sell_subunit = st.number_input(f"Selling price per {subunit} (₦)", min_value=0.0, step=10.0, key=f"register_subunit_sell_{unit}_{subunit}")
            if subunits_per_unit > 0 and sell > 0:
                estimated_price = float(sell) / float(subunits_per_unit)
                st.caption(f"Estimated price per {subunit}: ₦{estimated_price:,.2f}. Entered price overrides estimate.")

        save = st.button("💾 Register product", type="primary", use_container_width=True)
        if save:
            if not name.strip():
                st.error("Product name is required.")
            elif buy <= 0 or sell <= 0:
                st.error("Enter buying and selling price > 0")
            elif track_subunit and float(subunits_per_unit) <= 0:
                st.error("Number of smaller units must be > 0")
            else:
                latest_duplicate = get_product_by_barcode_add(barcode) if barcode else None
                if latest_duplicate:
                    st.error(f"Barcode already belongs to ‘{latest_duplicate['name']}’")
                else:
                    try:
                        if track_subunit:
                            buy_subunit = round(float(buy) / float(subunits_per_unit), 2)
                            if float(sell_subunit) <= 0:
                                sell_subunit = round(float(sell) / float(subunits_per_unit), 2)
                        with db_add() as con:
                            cur = con.execute("""INSERT INTO products (name, category, brand, variant, unit, buy, sell, stock, low_level, created, barcode, subunit, subunits_per_unit, buy_subunit, sell_subunit) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                                (name.strip(), category, brand.strip(), variant.strip(), unit, float(buy), float(sell), float(qty), float(low_level), now_add(), barcode or None, subunit, float(subunits_per_unit), float(buy_subunit), float(sell_subunit)))
                            if qty > 0:
                                add_movement_add(con, int(cur.lastrowid), "STOCK IN", float(qty), unit, float(buy), "New product registered")
                        st.session_state["test_notice"] = f"{name.strip()} registered."
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("That barcode is already in DB")

        st.divider()
    st.subheader("Local product catalogue - All Prices")
    products = get_products_add()
    if not products:
        st.caption("No products saved yet.")
    else:
        rows = []
        for p in products:
            # Get values safely
            buy_main = float(p["buy"] or 0)
            sell_main = float(p["sell"] or 0)
            sell_piece = float(p["sell_piece"] or 0)
            sell_mudu = float(p["sell_mudu"] or 0)
            subunit = p["subunit"] or ""
            sub_per = float(p["subunits_per_unit"] or 0) if subunit else 0
            sell_sub = float(p["sell_subunit"] or 0) if subunit else 0
            buy_sub = float(p["buy_subunit"] or 0) if subunit else 0

            rows.append({
                "Product": p["name"],
                "Barcode": p["barcode"] or "",
                "Brand": p["brand"],
                "Unit": p["unit"],
                "Stock": f"{p['stock']:g}",
                "Buy per Bag/Carton ₦": f"₦{buy_main:,.0f}",
                "Sell per Bag/Carton ₦": f"₦{sell_main:,.0f}",
                "Sell per PIECE ₦": f"₦{sell_piece:,.0f}" if sell_piece > 0 else "—",
                "Sell per MUDU ₦": f"₦{sell_mudu:,.0f}" if sell_mudu > 0 else "—",
                "Smaller Unit": subunit or "—",
                "Qty in 1 Main": f"{sub_per:g}" if sub_per > 0 else "—",
                "Buy per Smaller ₦": f"₦{buy_sub:,.0f}" if buy_sub > 0 else "—",
                "Sell per Smaller ₦": f"₦{sell_sub:,.0f}" if sell_sub > 0 else "—",
            })
        st.dataframe(rows, use_container_width=True, hide_index=True)
        
        # --- EXTRA: Card view for bag products to see all prices clearly ---
        st.markdown("**📦 Bag/Carton Breakdown View**")
        bag_rows = [p for p in products if p["unit"] in ["bag","carton","pack","crate"]]
        if bag_rows:
            for p in bag_rows:
                with st.container(border=True):
                    c1, c2, c3, c4 = st.columns(4)
                    with c1:
                        st.write(f"**{p['name']}**")
                        st.caption(f"{p['unit']} | {p['stock']:g} left | `{p['barcode'] or 'no barcode'}`")
                    with c2:
                        st.metric("Per Bag/Carton", f"₦{float(p['sell']):,.0f}")
                        st.caption(f"Buy: ₦{float(p['buy']):,.0f}")
                    with c3:
                        st.metric("Per PIECE", f"₦{float(p['sell_piece'] or 0):,.0f}")
                        if p["subunit"] == "piece":
                            st.caption(f"Sub: ₦{float(p['sell_subunit'] or 0):,.0f}")
                    with c4:
                        st.metric("Per MUDU", f"₦{float(p['sell_mudu'] or 0):,.0f}")
                        if p["subunit"] == "mudu":
                            st.caption(f"Sub: ₦{float(p['sell_subunit'] or 0):,.0f}")
        else:
            st.caption("No bag/carton products yet")

    with st.expander("View stock history"):
        with db_add() as con:
            history = con.execute("""SELECT p.name AS Product, p.barcode AS Barcode, m.movement AS Movement, 
                m.quantity AS Quantity, m.unit AS Unit, m.unit_cost AS 'Unit cost', m.note AS Note, m.created AS Date 
                FROM stock_movements m JOIN products p ON p.id = m.product_id ORDER BY m.id DESC""").fetchall()
        if history:
            st.dataframe([dict(row) for row in history], use_container_width=True, hide_index=True)
        else:
            st.caption("No stock movements yet.")
elif page=="Product Catalogue":
    st.header("📋 Product Catalogue - All Prices")
    
    APP_DIR_CAT = Path(__file__).resolve().parent
    DB_PATH_CAT = APP_DIR_CAT / "sme_barcode_test.db"

    @contextmanager
    def db_cat():
        con = sqlite3.connect(DB_PATH_CAT, timeout=10)
        con.row_factory = sqlite3.Row
        try:
            yield con
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()

    def get_products_cat():
        with db_cat() as con:
            return con.execute("SELECT * FROM products ORDER BY name COLLATE NOCASE").fetchall()

    def get_product_by_barcode_cat(barcode):
        barcode = (barcode or "").strip()
        if not barcode: return None
        with db_cat() as con:
            return con.execute("SELECT * FROM products WHERE barcode = ? LIMIT 1", (barcode,)).fetchone()

    # --- SEARCH & FILTER ---
    c1, c2 = st.columns([2,1])
    with c1:
        search = st.text_input("🔍 Search product / barcode / brand", placeholder="Type rice, indomie, barcode...")
    with c2:
        filter_unit = st.selectbox("Filter by unit", ["All", "bag", "carton", "pack", "piece", "mudu", "kg"], index=0)

    products = get_products_cat()
    
    # Filter
    if search:
        s = search.lower()
        products = [p for p in products if s in p["name"].lower() or s in (p["barcode"] or "").lower() or s in (p["brand"] or "").lower()]
    if filter_unit != "All":
        products = [p for p in products if p["unit"] == filter_unit]

    if not products:
        st.info("No products found")
    else:
        # --- SUMMARY METRICS ---
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Total Products", len(products))
        with m2:
            total_stock = sum(float(p["stock"] or 0) for p in products)
            st.metric("Total Stock", f"{total_stock:g}")
        with m3:
            bag_count = len([p for p in products if p["unit"] == "bag"])
            st.metric("Bag Products", bag_count)
        with m4:
            piece_priced = len([p for p in products if float(p["sell_piece"] or 0) > 0])
            st.metric("With Piece Price", piece_priced)

        st.divider()

        # --- MAIN TABLE - ALL PRICES ---
        st.subheader(f"All Prices Table ({len(products)} products)")
        rows = []
        for p in products:
            rows.append({
                "Product": p["name"],
                "Barcode": p["barcode"] or "—",
                "Brand": p["brand"] or "—",
                "Variant": p["variant"] or "—",
                "Unit": p["unit"],
                "Stock": f"{float(p['stock'] or 0):g}",
                "Buy Main ₦": float(p["buy"] or 0),
                "Sell Main (Bag/Carton) ₦": float(p["sell"] or 0),
                "Sell PIECE ₦": float(p["sell_piece"] or 0),
                "Sell MUDU ₦": float(p["sell_mudu"] or 0),
                "Subunit": p["subunit"] or "—",
                "Qty/Sub": float(p["subunits_per_unit"] or 0) if p["subunit"] else 0,
                "Buy Sub ₦": float(p["buy_subunit"] or 0) if p["subunit"] else 0,
                "Sell Sub ₦": float(p["sell_subunit"] or 0) if p["subunit"] else 0,
                "Low Alert": float(p["low_level"] or 0),
            })
        
        # Show with formatting
        st.dataframe(rows, use_container_width=True, hide_index=True)

        st.divider()

        # --- CARD VIEW - BAG BREAKDOWN ---
        st.subheader("📦 Bag / Carton Detailed Price Cards")
        for p in products:
            if p["unit"] in ["bag", "carton", "pack", "crate"]:
                with st.container(border=True):
                    top1, top2 = st.columns([2,1])
                    with top1:
                        st.markdown(f"### {p['name']} — {p['unit'].upper()}")
                        st.caption(f"Brand: {p['brand'] or '—'} | Size: {p['variant'] or '—'} | Barcode: `{p['barcode'] or 'none'}` | Stock: **{float(p['stock'] or 0):g} {p['unit']}**")
                    with top2:
                        if float(p["stock"] or 0) <= float(p["low_level"] or 5):
                            st.error("⚠️ LOW STOCK")
                        else:
                            st.success("✅ In Stock")

                    # Price columns
                    col_a, col_b, col_c, col_d = st.columns(4)
                    with col_a:
                        st.metric("Buy per Bag", f"₦{float(p['buy'] or 0):,.0f}")
                        st.metric("Sell per Bag", f"₦{float(p['sell'] or 0):,.0f}")
                    with col_b:
                        sp = float(p["sell_piece"] or 0)
                        if sp > 0:
                            st.metric("Per PIECE", f"₦{sp:,.0f}", delta=f"Profit ₦{sp - (float(p['buy'] or 0)/float(p['subunits_per_unit'] or 1)):,.0f}" if float(p["subunits_per_unit"] or 0) > 0 else None)
                        else:
                            st.metric("Per PIECE", "—")
                            if p["subunit"] == "piece":
                                st.metric("Sub Piece", f"₦{float(p['sell_subunit'] or 0):,.0f}")
                    with col_c:
                        sm = float(p["sell_mudu"] or 0)
                        if sm > 0:
                            st.metric("Per MUDU", f"₦{sm:,.0f}")
                        else:
                            st.metric("Per MUDU", "—")
                            if p["subunit"] == "mudu":
                                st.metric("Sub Mudu", f"₦{float(p['sell_subunit'] or 0):,.0f}")
                    with col_d:
                        if p["subunit"]:
                            st.write(f"**Also sells as {p['subunit']}**")
                            st.write(f"{float(p['subunits_per_unit'] or 0):g} {p['subunit']} in 1 {p['unit']}")
                            st.write(f"Buy: ₦{float(p['buy_subunit'] or 0):,.0f}")
                            st.write(f"Sell: ₦{float(p['sell_subunit'] or 0):,.0f}")
                        else:
                            st.write("No smaller unit set")

        st.divider()
        
        # --- LOW STOCK ALERT TABLE ---
        st.subheader("⚠️ Low Stock Alert")
        low_products = [p for p in products if float(p["stock"] or 0) <= float(p["low_level"] or 5)]
        if low_products:
            low_rows = [{"Product": p["name"], "Unit": p["unit"], "Stock": float(p["stock"] or 0), "Alert Level": float(p["low_level"] or 0), "Barcode": p["barcode"] or ""} for p in low_products]
            st.dataframe(low_rows, use_container_width=True, hide_index=True)
        else:
            st.success("All products are above low-stock level")

    with st.expander("View stock history for catalogue"):
        with db_cat() as con:
            history = con.execute("""SELECT p.name AS Product, p.barcode AS Barcode, m.movement AS Movement, 
                m.quantity AS Quantity, m.unit AS Unit, m.unit_cost AS 'Cost', m.note AS Note, m.created AS Date 
                FROM stock_movements m JOIN products p ON p.id = m.product_id ORDER BY m.id DESC LIMIT 100""").fetchall()
        if history:
            st.dataframe([dict(row) for row in history], use_container_width=True, hide_index=True)
        else:
            st.caption("No movements yet")           

elif page=="Smart calculator":
    st.header(f"🧮 {t('Smart calculator')}")
    
    # --- YOUR ORIGINAL CALCULATOR CODE STARTS HERE - SAME LOGIC, NO CHANGE ---
    # NOTE: I commented only the 3 lines that crash inside sme.py
    # st.set_page_config(page_title="Shop Calculator", page_icon="🛒", layout="centered")
    # st.title("🛒 Shop Calculator - CART")
    # st.caption("Add many items - Total dey gather")
    
    import threading  # your import, kept same
    DB_NAME_CALC = "sme.db"

    def get_db_calc():
        return sqlite3.connect(DB_NAME_CALC, check_same_thread=False)

    def get_price_calc(name):
        try:
            with get_db_calc() as con:
                row = con.execute("SELECT selling_price FROM stock WHERE product_name=?", (name,)).fetchone()
                return float(row[0]) if row and row[0] is not None else 0.0
        except sqlite3.Error:
            return 0.0

    def all_names_calc():
        try:
            with get_db_calc() as con:
                return [r[0] for r in con.execute("SELECT product_name FROM stock ORDER BY product_name").fetchall()]
        except sqlite3.Error:
            return []

    def has_barcode_column_calc():
        try:
            with get_db_calc() as con:
                return "barcode" in [r[1] for r in con.execute("PRAGMA table_info(stock)").fetchall()]
        except sqlite3.Error:
            return False

    def find_product_by_barcode_calc(code):
        if not code:
            return None
        try:
            with get_db_calc() as con:
                cols = [r[1] for r in con.execute("PRAGMA table_info(stock)").fetchall()]
                if "barcode" not in cols:
                    return None
                row = con.execute("SELECT product_name FROM stock WHERE TRIM(CAST(barcode AS TEXT))=? LIMIT 1", (str(code).strip(),)).fetchone()
                return row[0] if row else None
        except sqlite3.Error:
            return None

    def play_beep_calc():
        st.components.v1.html("""
        <script>
        try {
          const audio = new (window.AudioContext || window.webkitAudioContext)();
          const oscillator = audio.createOscillator();
          const gain = audio.createGain();
          oscillator.connect(gain); gain.connect(audio.destination);
          oscillator.frequency.value = 880; gain.gain.value = 0.12;
          oscillator.start(); oscillator.stop(audio.currentTime + 0.16);
          oscillator.onended = () => audio.close();
        } catch (e) {}
        </script>
        """, height=0)

    for key, value in {"cart": [], "show_cam": False, "scanned_code": "", "last_beep_code": "", "prod": None, "barcode_input_field": ""}.items():
        if key not in st.session_state:
            st.session_state[key] = value

    names_calc = all_names_calc()
    if not names_calc:
        st.error("No stock in sme.db - Go to your Add Stock app")
        st.stop()
    st.success(f"Found {len(names_calc)} products")

    st.divider()
    st.subheader("➕ Add Item to Cart")
    left, right = st.columns([2, 1.2])

    with right:
        st.write("📷 Barcode Scan")
        if not st.session_state.show_cam:
            if st.button("📷 Open Scanner", use_container_width=True):
                st.session_state.show_cam = True
                st.rerun()
        else:
            if st.button("❌ Close Scanner", use_container_width=True):
                st.session_state.show_cam = False
                st.rerun()

        if st.session_state.show_cam:
            st.caption("Live camera: hold the barcode steady in view.")
            try:
                from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
                from pyzbar.pyzbar import decode

                class BarcodeProcessor:
                    def __init__(self):
                        self.lock = threading.Lock()
                        self.barcode = None
                    def recv(self, frame):
                        image = frame.to_ndarray(format="bgr24")
                        try:
                            results = decode(image)
                            if results:
                                value = results[0].data.decode("utf-8", errors="ignore").strip()
                                if value:
                                    with self.lock:
                                        self.barcode = value
                        except Exception:
                            pass
                        return frame
                    def get_barcode(self):
                        with self.lock:
                            return self.barcode

                ctx = webrtc_streamer(key="shop-calculator-barcode-live", mode=WebRtcMode.SENDRECV, rtc_configuration=RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]} ]}), video_processor_factory=BarcodeProcessor, media_stream_constraints={"video": True, "audio": False}, async_processing=True)
                if ctx.state.playing and ctx.video_processor:
                    message = st.empty()
                    for _ in range(30):
                        scanned = ctx.video_processor.get_barcode()
                        if scanned:
                            message.success(f"✅ Captured barcode: {scanned}")
                            if st.session_state.scanned_code != scanned:
                                st.session_state.scanned_code = scanned
                                st.session_state.barcode_input_field = scanned
                                product = find_product_by_barcode_calc(scanned)
                                if product in names_calc:
                                    st.session_state.prod = product
                                if st.session_state.last_beep_code != scanned:
                                    st.session_state.last_beep_code = scanned
                                    play_beep_calc()
                            break
                        time.sleep(0.15)
                    message.empty()
            except Exception as exc:
                st.error("Could not start the live scanner. Check installed packages.")
                st.code(str(exc))

        barcode_input = st.text_input("Barcode number", key="barcode_input_field", placeholder="Type or scan code").strip()
        if barcode_input:
            product = find_product_by_barcode_calc(barcode_input)
            if product and product in names_calc:
                if st.session_state.prod != product:
                    st.session_state.prod = product
                st.success(f"Found: {product}")
            else:
                name_matches = [n for n in names_calc if barcode_input.lower() in n.lower()]
                if name_matches:
                    if st.session_state.prod != name_matches[0]:
                        st.session_state.prod = name_matches[0]
                    st.success(f"Found by product name: {name_matches[0]}")
                elif not has_barcode_column_calc():
                    st.warning("Your stock table has no 'barcode' column. Add one and save each product barcode there.")
                else:
                    st.warning("Barcode not found in local stock. Check that it is saved in sme.db.")

    with left:
        if st.session_state.prod not in names_calc:
            st.session_state.prod = names_calc[0]
        prod = st.selectbox("Select Product", names_calc, key="prod")
        col1, col2 = st.columns(2)
        with col1:
            unit = st.selectbox("Unit", ["KG", "Grams", "Carton", "Pieces", "Bag", "Mudu"], key="unit")
        with col2:
            if unit == "Grams":
                qty = st.number_input("Grams", min_value=0.0, value=500.0, step=100.0, key="qty")
            else:
                qty = st.number_input(f"How many {unit}?", min_value=0.0, value=1.0, step=1.0, key="qty2")
        price = get_price_calc(prod)
        if price:
            st.metric("Price", f"₦{price:,.2f} per {unit}")
        if st.button("➕ ADD TO CART", use_container_width=True, type="primary"):
            total = (price / 1000) * qty if unit == "Grams" else price * qty
            st.session_state.cart.append({"name": prod, "qty": qty, "unit": unit, "price": price, "total": total})
            st.success(f"Added {prod} ₦{total:,.2f}")
            time.sleep(0.8)
            st.rerun()

    st.divider()
    st.subheader("🧺 Cart - Money dey gather")
    if not st.session_state.cart:
        st.write("Cart empty")
    else:
        grand = 0.0
        for i, item in enumerate(st.session_state.cart):
            a, b, c = st.columns([4, 2, 1])
            with a:
                st.write(f"{i+1}. {item['name']} {item['qty']} {item['unit']}")
            with b:
                st.write(f"₦{item['total']:,.2f}")
            with c:
                if st.button("❌", key=f"rem_{i}"):
                    st.session_state.cart.pop(i)
                    st.rerun()
            grand += item["total"]
        st.success(f"### 💰 GRAND TOTAL: ₦{grand:,.2f}")
        cc1, cc2 = st.columns(2)
        with cc1:
            if st.button("💵 PAY / CHECKOUT", use_container_width=True, type="primary"):
                with get_db_calc() as con:
                    con.execute("""CREATE TABLE IF NOT EXISTS sales (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, qty REAL, unit TEXT, total REAL, time TEXT)""")
                    now = datetime.now().strftime("%Y-%m-%d %H:%M")
                    for item in st.session_state.cart:
                        con.execute("INSERT INTO sales (name,qty,unit,total,time) VALUES (?,?,?,?,?)", (item["name"], item["qty"], item["unit"], item["total"], now))
                    con.commit()
                st.session_state.cart = []
                st.session_state.scanned_code = ""
                st.session_state.barcode_input_field = ""
                st.balloons()
                st.success("Paid! Cart cleared")
                time.sleep(0.7)
                st.rerun()
        with cc2:
            if st.button("Clear Cart", use_container_width=True):
                st.session_state.cart = []
                st.session_state.scanned_code = ""
                st.session_state.barcode_input_field = ""
                st.rerun()


elif page=="Debtors":
    st.header(f"📒 {t('debtors')}")
    st.write(t('debtors_desc'))

    # --- ensure new columns exist (phone + partial payment) ---
    with db() as con:
        try: con.execute("ALTER TABLE debtors ADD COLUMN phone TEXT")
        except: pass
        try: con.execute("ALTER TABLE debtors ADD COLUMN paid_amount REAL DEFAULT 0")
        except: pass
        try: con.execute("ALTER TABLE debtors ADD COLUMN balance REAL DEFAULT 0")
        except: pass
        # fix old rows where balance is empty
        try: con.execute("UPDATE debtors SET balance=amount WHERE balance IS NULL OR balance=0 AND paid_amount IS NULL")
        except: pass

    with st.form("add_debtor", clear_on_submit=True):
        c1,c2 = st.columns(2)
        with c1:
            d_name = st.text_input(f"{t('person_name')} *", placeholder="e.g. Musa")
            d_phone = st.text_input("Phone Number", placeholder="e.g. 08012345678")
            d_amount = st.number_input(f"{t('how_much_owe')} ₦ *", min_value=0.0, step=100.0)
        with c2:
            d_date = st.date_input(f"{t('date')}", value=datetime.now().date())
            d_note = st.text_input(f"{t('reason')} (optional)", placeholder=t('reason_placeholder'))
        if st.form_submit_button(f"💾 {t('save_debt')}", type="primary", use_container_width=True):
            if not d_name.strip() or d_amount<=0:
                st.error("Fill name and amount")
            else:
                with db() as con:
                    con.execute("INSERT INTO debtors(name,phone,amount,debt_date,note,status,paid_amount,balance,created_at) VALUES(?,?,?,?,?,?,?,?,?)",
                                (d_name.strip(), d_phone.strip(), d_amount, str(d_date), d_note.strip(), "unpaid", 0, d_amount, now()))
                st.success(f"Saved! {d_name} - ₦{d_amount:,.0f}")
                st.rerun()
        
    st.markdown("---")
    with db() as con:
        debt_df = pd.read_sql_query("SELECT * FROM debtors ORDER BY id DESC", con)

    if debt_df.empty:
        st.info("No debtors yet / Babu bashi")
    else:
        # show table
        st.dataframe(debt_df, use_container_width=True)

        # metrics
        total_owe = debt_df['balance'].sum() if 'balance' in debt_df.columns else debt_df['amount'].sum()
        st.metric("Total Owing / Jimillar Bashi", f"₦{total_owe:,.0f}")

        st.subheader(f"💰 {t('collect_payment')}")

        unpaid_df = debt_df[debt_df['balance']>0] if 'balance' in debt_df.columns else debt_df[debt_df['status']=='unpaid']

        if unpaid_df.empty:
            st.success("All debts paid! / Duk bashi an biya!")
        else:
            unpaid_df['label'] = unpaid_df.apply(lambda r: f"{r['id']} - {r['name']} - Bal ₦{r.get('balance', r['amount']):,.0f}", axis=1)
            opt_map = dict(zip(unpaid_df['label'], unpaid_df['id']))
            sel_label = st.selectbox(t('select_who_paid'), list(opt_map.keys()), key="sel_person")
            collect_amt = st.number_input(t('how_much_paid_now'), min_value=1.0, step=100.0, key="collect_input")

            c1,c2,c3 = st.columns(3)
            if c1.button(t('collect_this_amount'), key="btn_collect", use_container_width=True, type="primary"):
                sel_id = opt_map[sel_label]
                with db() as con:
                    row = con.execute("SELECT amount, paid_amount, balance FROM debtors WHERE id=?", (sel_id,)).fetchone()
                    amt, paid, bal = row[0], (row[1] or 0), (row[2] or row[0])
                    new_paid = paid + collect_amt
                    new_bal = amt - new_paid
                    if new_bal <= 0:
                        con.execute("UPDATE debtors SET paid_amount=?, balance=0, status='paid' WHERE id=?", (amt, sel_id))
                    else:
                        con.execute("UPDATE debtors SET paid_amount=?, balance=?, status='unpaid' WHERE id=?", (new_paid, new_bal, sel_id))
                st.success(f"Collected ₦{collect_amt:,.0f}")
                st.rerun()

            if c2.button(t('mark_fully_paid'), key="btn_fully", use_container_width=True):
                sel_id = opt_map[sel_label]
                with db() as con:
                    con.execute("UPDATE debtors SET paid_amount=amount, balance=0, status='paid' WHERE id=?", (sel_id,))
                st.success("Marked as fully paid!")
                st.rerun()

            if c3.button(t('delete_debt'), key="btn_del_unpaid", use_container_width=True):
                sel_id = opt_map[sel_label]
                with db() as con:
                    con.execute("DELETE FROM debtors WHERE id=?", (sel_id,))
                st.success("Deleted!")
                st.rerun()

        # --- DOWN 👇 DELETE SECTION - ALWAYS AT BOTTOM ---
        st.markdown("---")
        st.subheader("🗑️ Delete Any Record / Goge kowane bashi")

        if "pending_del" not in st.session_state:
            st.session_state.pending_del = None
            st.session_state.pending_label = None

        all_labels = debt_df.apply(lambda r: f"{r['id']} - {r['name']} - {r['status']} - ₦{r['amount']}", axis=1).tolist()
        all_map = dict(zip(all_labels, debt_df['id'].tolist()))
        del_label = st.selectbox("Select who to delete", list(all_map.keys()), key="del_any")

        col_a, col_b = st.columns(2)
        if col_a.button(f"🗑️ {t('delete_this_one')}", key="btn_del_one", use_container_width=True, type="primary"):
            st.session_state.pending_del = all_map[del_label]
            st.session_state.pending_label = del_label

        if col_b.button(f"🧹 {t('delete_all_paid')}", key="btn_del_all_paid", use_container_width=True):
            with db() as con:
                con.execute("DELETE FROM debtors WHERE status='paid' OR balance=0")
            st.success("All paid records deleted!")
            st.rerun()

        if st.session_state.pending_del is not None:
            name_only = st.session_state.pending_label.split(" - ")[1]
            st.warning(f"⚠️ Are you sure {name_only} has paid? / Ka tabbata {name_only} ya biya?")
            cy, cn = st.columns(2)
            if cy.button(f"✅ Yes, {name_only} has paid - Delete", key="yes_confirm", use_container_width=True, type="primary"):
                with db() as con:
                    con.execute("DELETE FROM debtors WHERE id=?", (st.session_state.pending_del,))
                st.session_state.pending_del = None
                st.session_state.pending_label = None
                st.success("Deleted!")
                st.rerun()
            if cn.button("❌ Cancel", key="no_confirm", use_container_width=True):
                st.session_state.pending_del = None
                st.session_state.pending_label = None
                st.rerun()

elif page=="Settings":
    st.header("⚙️ Settings")
    tab1, tab2 = st.tabs(["🧠 Business Memory", "📜 Stock History"])
    with tab1:
      st.header("Business Memory - Before AI")
      st.write("These are saved facts and preferences—not guesses. Assistant will use these to remember.")
      current=get_profile()
      with st.form("business_profile"):
        name=st.text_input("Business name", value=current["business_name"] or "")
        kind=st.selectbox("Main business type", ["General shop","Provisions / groceries","Textiles / fabrics","Chemist / pharmacy","Mixed retail","Other"])
        language=st.selectbox("Preferred language", ["English","Hausa","Nigerian Pidgin"], index=0)
        prefs=st.text_area("How should assistant help you?", value=current["owner_preferences"] or "", placeholder="e.g. Keep answers simple and remind me to check stock every Saturday.")
        if st.form_submit_button("Save business memory", type="primary"):
           with db() as con:
            con.execute("UPDATE business_profile SET business_name=?, business_type=?, preferred_language=?, owner_preferences=?, updated_at=? WHERE id=1",(name.strip(),kind,language,prefs.strip(),now()))
           st.success("Business profile saved - assistant will remember.")
           st.rerun()
    
    with tab2:
      st.header("Stock history - Memory")
      with db() as con:
        history=pd.read_sql_query("""SELECT p.name AS Product,p.brand AS Brand,m.movement AS Movement,m.quantity AS Quantity,m.unit AS Unit,m.unit_cost AS 'Unit cost',m.note AS Note,m.created AS 'Date' FROM stock_movements m JOIN products p ON p.id=m.product_id ORDER BY m.id DESC""", con)
        if history.empty: 
           st.info("No stock movements yet.")
        else: 
           st.dataframe(history, use_container_width=True, hide_index=True)
