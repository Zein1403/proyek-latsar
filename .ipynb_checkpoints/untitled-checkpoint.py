# inventory_app.py
import streamlit as st
import csv
import os
from datetime import datetime

# File name
filename = 'manual_data.csv'

# Options
satuan_options = ['Meter', 'kg', 'liter', 'buah']
tempat_options = ['Gudang lantai 1', 'Gudang A lantai 4', 'Gudang B lantai 4', 'Gudang lantai 6']

# Create CSV with header if not exists
if not os.path.exists(filename):
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Nama', 'Jumlah', 'Satuan', 'Tempat', 'Tanggal'])

st.title("📦 Inventory Management App")

# Sidebar menu
menu = st.sidebar.radio("Menu", ["Tambah Item", "Kurangi Item", "Pindahkan Item", "Lihat CSV"])

# Load CSV data
def load_data():
    with open(filename, 'r', newline='') as f:
        return list(csv.DictReader(f))

# Save CSV data
def save_data(rows):
    with open(filename, 'w', newline='') as f:
        fieldnames = ['Nama', 'Jumlah', 'Satuan', 'Tempat', 'Tanggal']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

# ---- ADD ITEM ----
if menu == "Tambah Item":
    st.header("Tambah / Update Item")
    nama = st.text_input("Nama")
    jumlah = st.number_input("Jumlah", min_value=1, value=1)
    satuan = st.selectbox("Satuan", satuan_options)
    tempat = st.selectbox("Tempat", tempat_options)

    if st.button("Submit"):
        rows = load_data()
        found = False

        for row in rows:
            if (row['Nama'].strip().lower() == nama.lower() and
                row['Satuan'] == satuan and
                row['Tempat'] == tempat):
                row['Jumlah'] = str(int(row['Jumlah']) + jumlah)
                row['Tanggal'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                found = True
                break

        if not found:
            rows.append({
                'Nama': nama,
                'Jumlah': str(jumlah),
                'Satuan': satuan,
                'Tempat': tempat,
                'Tanggal': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })

        save_data(rows)
        st.success(f"✅ Data '{nama}' berhasil ditambahkan / diperbarui.")

# ---- DECREASE ITEM ----
elif menu == "Kurangi Item":
    st.header("Kurangi Item")
    nama = st.text_input("Nama")
    jumlah = st.number_input("Jumlah yang dikurangi", min_value=1, value=1)
    satuan = st.selectbox("Satuan", satuan_options)
    tempat = st.selectbox("Tempat", tempat_options)

    if st.button("Kurangi"):
        rows = load_data()
        updated_rows = []
        found = False

        for row in rows:
            if (row['Nama'].strip().lower() == nama.lower() and
                row['Satuan'] == satuan and
                row['Tempat'] == tempat):
                current_qty = int(row['Jumlah'])
                if current_qty < jumlah:
                    st.error(f"❌ Jumlah yang diminta ({jumlah}) melebihi stok ({current_qty}).")
                    save_data(rows)
                    st.stop()
                elif current_qty == jumlah:
                    st.info(f"🗑️ Item '{nama}' dihapus dari lokasi.")
                    found = True
                    continue
                else:
                    row['Jumlah'] = str(current_qty - jumlah)
                    row['Tanggal'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    st.success(f"➖ Berhasil mengurangi {jumlah} {satuan} dari '{nama}'.")
                    found = True
            updated_rows.append(row)

        if not found:
            st.error("❌ Item tidak ditemukan.")
        else:
            save_data(updated_rows)

# ---- MOVE ITEM ----
elif menu == "Pindahkan Item":
    st.header("Pindahkan Item")
    nama = st.text_input("Nama")
    jumlah = st.number_input("Jumlah dipindahkan", min_value=1, value=1)
    satuan = st.selectbox("Satuan", satuan_options)
    source_tempat = st.selectbox("Dari", tempat_options)
    dest_tempat = st.selectbox("Ke", tempat_options)

    if st.button("Pindahkan"):
        if source_tempat == dest_tempat:
            st.error("⚠️ Lokasi asal dan tujuan tidak boleh sama.")
        else:
            rows = load_data()
            updated_rows = []
            found = False

            for row in rows:
                if (row['Nama'].strip().lower() == nama.lower() and
                    row['Satuan'] == satuan and
                    row['Tempat'] == source_tempat):
                    current_qty = int(row['Jumlah'])
                    if current_qty < jumlah:
                        st.error(f"❌ Stok di {source_tempat} tidak cukup ({current_qty}).")
                        save_data(rows)
                        st.stop()
                    elif current_qty == jumlah:
                        found = True
                        continue
                    else:
                        row['Jumlah'] = str(current_qty - jumlah)
                        row['Tanggal'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        found = True
                updated_rows.append(row)

            if not found:
                st.error(f"❌ Item tidak ditemukan di {source_tempat}.")
            else:
                # Tambah ke lokasi tujuan
                merged = False
                for row in updated_rows:
                    if (row['Nama'].strip().lower() == nama.lower() and
                        row['Satuan'] == satuan and
                        row['Tempat'] == dest_tempat):
                        row['Jumlah'] = str(int(row['Jumlah']) + jumlah)
                        row['Tanggal'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        merged = True
                        break
                if not merged:
                    updated_rows.append({
                        'Nama': nama,
                        'Jumlah': str(jumlah),
                        'Satuan': satuan,
                        'Tempat': dest_tempat,
                        'Tanggal': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })

                save_data(updated_rows)
                st.success(f"✅ {jumlah} {satuan} dari {source_tempat} berhasil dipindahkan ke {dest_tempat}.")

# ---- DISPLAY CSV ----
elif menu == "Lihat CSV":
    st.header("📄 Data Inventory")
    rows = load_data()
    if rows:
        st.dataframe(rows)
    else:
        st.info("📂 Data masih kosong.")
