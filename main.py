from __future__ import annotations

import tkinter as tk
from decimal import Decimal
from tkinter import messagebox, ttk

from formulation_calculator import calculate_formulation
from item_database import ItemDatabase, search_items, search_product_names
from pail_calculator import calculate_pails, calculate_total, parse_quantity
from printout_formatter import build_pail_printout, build_printout


BG = "#f3f6fb"
NAVY = "#142b4a"
BLUE = "#2563eb"
TEXT = "#1f2937"
MUTED = "#64748b"
WHITE = "#ffffff"
BORDER = "#dbe3ef"
GREEN = "#16845b"
RED = "#b42318"


def pretty_decimal(value: Decimal, places: int = 2) -> str:
    text = f"{value:.{places}f}"
    return text.rstrip("0").rstrip(".") if "." in text else text


class MaterialRow:
    def __init__(self, app: "DmasterCounterApp", row_number: int) -> None:
        self.app = app
        self.frame = ttk.Frame(app.rows_frame, style="Row.TFrame", padding=(10, 8))
        self.name_var = tk.StringVar()
        self.quantity_var = tk.StringVar()
        self.name_entry = ttk.Entry(self.frame, textvariable=self.name_var, font=("Segoe UI", 10))
        self.name_entry.bind("<Return>", lambda event: app.complete_item_name(self.name_entry, "material"))
        self.quantity_entry = ttk.Entry(
            self.frame,
            textvariable=self.quantity_var,
            font=("Segoe UI", 10),
            justify="right",
        )
        self.equivalent_label = ttk.Label(self.frame, text="—", style="Result.TLabel", anchor="e")
        self.whole_label = ttk.Label(self.frame, text="—", style="Whole.TLabel", anchor="center")
        self.error_label = ttk.Label(self.frame, text="", style="Error.TLabel")
        self.remove_button = ttk.Button(
            self.frame,
            text="Hapus",
            style="Remove.TButton",
            command=lambda: app.remove_row(self),
        )

        self.frame.columnconfigure(0, weight=5, minsize=220)
        self.frame.columnconfigure(1, weight=2, minsize=110)
        self.frame.columnconfigure(2, weight=2, minsize=110)
        self.frame.columnconfigure(3, weight=2, minsize=110)
        self.frame.columnconfigure(4, weight=0, minsize=70)
        self.name_entry.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        self.quantity_entry.grid(row=0, column=1, sticky="ew", padx=(0, 12))
        self.equivalent_label.grid(row=0, column=2, sticky="ew", padx=(0, 12))
        self.whole_label.grid(row=0, column=3, sticky="ew", padx=(0, 12))
        self.remove_button.grid(row=0, column=4, sticky="e")
        self.error_label.grid(row=1, column=0, columnspan=5, sticky="w", pady=(3, 0))
        self.name_var.trace_add("write", lambda *_: app.refresh())
        self.quantity_var.trace_add("write", lambda *_: app.refresh())

    def set_result(self, equivalent: str, whole: str, error: str = "") -> None:
        self.equivalent_label.configure(text=equivalent)
        self.whole_label.configure(text=whole)
        self.error_label.configure(text=error)


class FormulationRow:
    def __init__(self, app: "DmasterCounterApp") -> None:
        self.app = app
        self.frame = ttk.Frame(app.formulation_rows_frame, style="Row.TFrame", padding=(10, 8))
        self.name_var = tk.StringVar()
        self.gramasi_var = tk.StringVar()
        self.name_entry = ttk.Entry(self.frame, textvariable=self.name_var, font=("Segoe UI", 10))
        self.name_entry.bind("<Return>", lambda event: app.complete_item_name(self.name_entry, "material"))
        self.name_entry.bind("<Return>", lambda event: app.complete_item_name(self.name_entry, "material"))
        self.quantity_label = ttk.Label(self.frame, text="—", style="Result.TLabel", anchor="e")
        self.percentage_label = ttk.Label(self.frame, text="—", style="Result.TLabel", anchor="e")
        self.gramasi_entry = ttk.Entry(
            self.frame, textvariable=self.gramasi_var, font=("Segoe UI", 10), justify="right"
        )
        self.error_label = ttk.Label(self.frame, text="", style="Error.TLabel")
        self.remove_button = ttk.Button(
            self.frame,
            text="Hapus",
            style="Remove.TButton",
            command=lambda: app.remove_formulation_row(self),
        )

        self.frame.columnconfigure(0, weight=5, minsize=210)
        self.frame.columnconfigure(1, weight=2, minsize=120)
        self.frame.columnconfigure(2, weight=2, minsize=120)
        self.frame.columnconfigure(3, weight=2, minsize=130)
        self.frame.columnconfigure(4, weight=0, minsize=70)
        self.name_entry.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        self.quantity_label.grid(row=0, column=1, sticky="ew", padx=(0, 12))
        self.percentage_label.grid(row=0, column=2, sticky="ew", padx=(0, 12))
        self.gramasi_entry.grid(row=0, column=3, sticky="ew", padx=(0, 12))
        self.remove_button.grid(row=0, column=4, sticky="e")
        self.error_label.grid(row=1, column=0, columnspan=5, sticky="w", pady=(3, 0))
        self.name_var.trace_add("write", lambda *_: app.refresh_formulation())
        self.gramasi_var.trace_add("write", lambda *_: app.refresh_formulation())

    def set_result(self, quantity: str = "—", percentage: str = "—", error: str = "") -> None:
        self.quantity_label.configure(text=quantity)
        self.percentage_label.configure(text=percentage)
        self.error_label.configure(text=error)


class DmasterCounterApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.item_database = ItemDatabase()
        self.rows: list[MaterialRow] = []
        self._refreshing = False
        self._autocomplete_popup: tk.Toplevel | None = None
        self._autocomplete_list: tk.Listbox | None = None
        self._autocomplete_entry: ttk.Entry | None = None
        self._itemlist_return_page = "calculator"
        self.root.title("DmasterCounter | Kalkulator Pail Produksi")
        self.root.geometry("1080x760")
        self.root.minsize(740, 460)
        self.root.configure(bg=BG)
        self._setup_styles()
        self._build_ui()
        self.root.bind_all("<MouseWheel>", self._on_mousewheel)
        self.root.bind_all("<Button-4>", self._on_mousewheel)
        self.root.bind_all("<Button-5>", self._on_mousewheel)
        self.add_row()

    def _setup_styles(self) -> None:
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background=BG)
        style.configure("Card.TFrame", background=WHITE)
        style.configure("Row.TFrame", background=WHITE)
        style.configure("TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 10))
        style.configure("Title.TLabel", background=BG, foreground=NAVY, font=("Segoe UI", 22, "bold"))
        style.configure("Subtitle.TLabel", background=BG, foreground=MUTED, font=("Segoe UI", 10))
        style.configure("Copyright.TLabel", background=BG, foreground="#94a3b8", font=("Segoe UI", 8))
        style.configure("Section.TLabel", background=WHITE, foreground=NAVY, font=("Segoe UI", 12, "bold"))
        style.configure("Header.TLabel", background="#edf2f8", foreground="#475569", font=("Segoe UI", 9, "bold"))
        style.configure("Result.TLabel", background=WHITE, foreground=TEXT, font=("Segoe UI", 10))
        style.configure("Whole.TLabel", background=WHITE, foreground=GREEN, font=("Segoe UI", 11, "bold"))
        style.configure("Error.TLabel", background=WHITE, foreground=RED, font=("Segoe UI", 9))
        style.configure("CardTitle.TLabel", background=WHITE, foreground=MUTED, font=("Segoe UI", 9, "bold"))
        style.configure("CardValue.TLabel", background=WHITE, foreground=NAVY, font=("Segoe UI", 18, "bold"))
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), padding=(14, 9))
        style.map("Primary.TButton", background=[("!disabled", BLUE), ("active", "#1d4ed8")], foreground=[("!disabled", WHITE)])
        style.configure("Secondary.TButton", font=("Segoe UI", 10), padding=(12, 8))
        style.configure("Remove.TButton", font=("Segoe UI", 9), padding=(7, 5))
        style.configure("TEntry", padding=(8, 7), fieldbackground=WHITE)

    def _build_ui(self) -> None:
        page = ttk.Frame(self.root, style="TFrame")
        page.pack(fill="both", expand=True)
        ttk.Label(
            self.root,
            text="© 2026 Dominicus Daimon Pradana. All rights reserved.",
            style="Copyright.TLabel",
        ).pack(side="bottom", anchor="e", padx=14, pady=(0, 5))
        self.page_canvas = tk.Canvas(page, bg=BG, highlightthickness=0)
        self.page_scrollbar = ttk.Scrollbar(page, orient="vertical", command=self.page_canvas.yview)
        self.page_canvas.configure(yscrollcommand=self.page_scrollbar.set)
        self.page_canvas.pack(side="left", fill="both", expand=True)
        self.page_scrollbar.pack(side="right", fill="y")

        outer = ttk.Frame(self.page_canvas, padding=(28, 22, 28, 22))
        self.page_window = self.page_canvas.create_window((0, 0), window=outer, anchor="nw")
        outer.bind("<Configure>", self._update_page_scroll_region)
        self.page_canvas.bind("<Configure>", self._fit_page_width)

        self.calculator_page = ttk.Frame(outer)
        self.calculator_page.pack(fill="both", expand=True)
        self.active_page = "calculator"

        heading = ttk.Frame(self.calculator_page)
        heading.pack(fill="x", pady=(0, 18))
        heading_text = ttk.Frame(heading)
        heading_text.pack(side="left", fill="x", expand=True)
        ttk.Label(heading_text, text="DmasterCounter", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            heading_text,
            text="Kalkulator kebutuhan pail untuk produk dan material produksi",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(3, 0))
        ttk.Button(
            heading,
            text="Berikutnya: Perhitungan Formulasi  →",
            style="Primary.TButton",
            command=self.show_formulation_page,
        ).pack(side="right", padx=(12, 0))
        ttk.Button(
            heading,
            text="ItemList",
            style="Secondary.TButton",
            command=self.show_itemlist_page,
        ).pack(side="right", padx=(0, 8))

        product_card = ttk.Frame(self.calculator_page, style="Card.TFrame", padding=16)
        product_card.pack(fill="x", pady=(0, 14))
        ttk.Label(product_card, text="NAMA PRODUK", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 7))
        self.product_name = tk.StringVar()
        product_entry = ttk.Entry(product_card, textvariable=self.product_name, font=("Segoe UI", 11))
        product_entry.bind("<Return>", lambda event: self.complete_item_name(product_entry, "product"))
        product_entry.pack(fill="x")
        self.product_name.trace_add("write", lambda *_: self._on_product_name_changed())

        summary = ttk.Frame(self.calculator_page)
        summary.pack(fill="x", pady=(0, 14))
        self.product_summary = self._summary_card(summary, "TOTAL PRODUK", "0 kg", "0 pail utuh")
        self.material_summary = self._summary_card(summary, "TOTAL PAIL MATERIAL", "0 pail", "Pembulatan per material")
        summary.columnconfigure(0, weight=1, uniform="summary")
        summary.columnconfigure(1, weight=1, uniform="summary")

        materials_card = ttk.Frame(self.calculator_page, style="Card.TFrame", padding=(14, 14, 14, 10))
        materials_card.pack(fill="both", expand=True)
        top_line = ttk.Frame(materials_card, style="Card.TFrame")
        top_line.pack(fill="x", pady=(0, 10))
        ttk.Label(top_line, text="Daftar Material", style="Section.TLabel").pack(side="left")
        ttk.Button(top_line, text="+ Tambah Material", style="Secondary.TButton", command=self.add_row).pack(side="right")

        headers = ttk.Frame(materials_card, style="Card.TFrame", padding=(10, 8))
        headers.pack(fill="x")
        headers.columnconfigure(0, weight=5, minsize=220)
        headers.columnconfigure(1, weight=2, minsize=110)
        headers.columnconfigure(2, weight=2, minsize=110)
        headers.columnconfigure(3, weight=2, minsize=110)
        headers.columnconfigure(4, weight=0, minsize=70)
        for col, title, anchor in (
            (0, "NAMA MATERIAL", "w"),
            (1, "JUMLAH (KG)", "e"),
            (2, "PAIL SETARA", "e"),
            (3, "PAIL UTUH", "center"),
            (4, "", "e"),
        ):
            ttk.Label(headers, text=title, style="Header.TLabel", anchor=anchor).grid(
                row=0, column=col, sticky="ew", padx=(0, 12) if col < 4 else 0
            )

        self.rows_frame = ttk.Frame(materials_card, style="Card.TFrame")
        self.rows_frame.pack(fill="x")
        self.rows_frame.bind("<Configure>", self._update_page_scroll_region)

        foot = ttk.Frame(self.calculator_page)
        foot.pack(fill="x", pady=(12, 0))
        ttk.Label(foot, text="Kapasitas pail: 15 kg  ·  Desimal ≥ 0,50 dibulatkan ke atas", style="Subtitle.TLabel").pack(side="left")
        ttk.Button(foot, text="Bersihkan Semua", style="Secondary.TButton", command=self.clear_all).pack(side="right")

        printouts = ttk.Frame(self.calculator_page)
        printouts.pack(fill="x", pady=(14, 0))
        printouts.columnconfigure(0, weight=1, uniform="printouts")
        printouts.columnconfigure(1, weight=1, uniform="printouts")
        self.printout_text = self._create_print_panel(
            printouts, "Pratinjau Print Out Material", self.copy_printout, 0
        )
        self.pail_printout_text = self._create_print_panel(
            printouts, "Pratinjau Print Out Pail", self.copy_pail_printout, 1
        )

        self.formulation_page = ttk.Frame(outer)
        formulation_heading = ttk.Frame(self.formulation_page)
        formulation_heading.pack(fill="x")
        ttk.Button(
            formulation_heading,
            text="← Kembali ke Kalkulator",
            style="Secondary.TButton",
            command=self.show_calculator_page,
        ).pack(side="left", padx=(0, 16))
        ttk.Button(
            formulation_heading,
            text="ItemList",
            style="Secondary.TButton",
            command=self.show_itemlist_page,
        ).pack(side="right")
        ttk.Label(
            formulation_heading,
            text="Perhitungan Formulasi",
            style="Title.TLabel",
        ).pack(side="left", anchor="center")

        ttk.Label(
            self.formulation_page,
            text="Masukkan gramasi acuan tiap bahan, lalu isi total produksi untuk menghitung jumlah kg.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(12, 16))

        formulation_card = ttk.Frame(self.formulation_page, style="Card.TFrame", padding=(14, 14, 14, 12))
        formulation_card.pack(fill="x")
        formulation_top = ttk.Frame(formulation_card, style="Card.TFrame")
        formulation_top.pack(fill="x", pady=(0, 10))
        ttk.Label(formulation_top, text="Komposisi Bahan", style="Section.TLabel").pack(side="left")
        ttk.Button(
            formulation_top,
            text="+ Tambah Bahan",
            style="Secondary.TButton",
            command=self.add_formulation_row,
        ).pack(side="right")

        formulation_headers = ttk.Frame(formulation_card, style="Card.TFrame", padding=(10, 8))
        formulation_headers.pack(fill="x")
        for column, weight, minimum in ((0, 5, 210), (1, 2, 120), (2, 2, 120), (3, 2, 130), (4, 0, 70)):
            formulation_headers.columnconfigure(column, weight=weight, minsize=minimum)
        for column, label, anchor in (
            (0, "NAMA BAHAN", "w"),
            (1, "JUMLAH (KG)", "e"),
            (2, "PERSENTASE", "e"),
            (3, "GRAMASI ACUAN", "e"),
            (4, "", "e"),
        ):
            ttk.Label(formulation_headers, text=label, style="Header.TLabel", anchor=anchor).grid(
                row=0, column=column, sticky="ew", padx=(0, 12) if column < 4 else 0
            )

        self.formulation_rows_frame = ttk.Frame(formulation_card, style="Card.TFrame")
        self.formulation_rows_frame.pack(fill="x")
        self.formulation_rows_frame.bind("<Configure>", self._update_page_scroll_region)

        target_card = ttk.Frame(self.formulation_page, style="Card.TFrame", padding=16)
        target_card.pack(fill="x", pady=(14, 0))
        target_title = ttk.Frame(target_card, style="Card.TFrame")
        target_title.pack(fill="x")
        ttk.Label(target_title, text="Total Produksi", style="Section.TLabel").pack(side="left")
        ttk.Label(target_title, text="Masukkan target batch dalam kg", style="CardTitle.TLabel").pack(side="right")
        target_input_line = ttk.Frame(target_card, style="Card.TFrame")
        target_input_line.pack(fill="x", pady=(10, 0))
        self.formulation_total_var = tk.StringVar()
        self.formulation_total_entry = ttk.Entry(
            target_input_line,
            textvariable=self.formulation_total_var,
            font=("Segoe UI", 12),
            justify="right",
        )
        self.formulation_total_entry.pack(side="left", fill="x", expand=True)
        ttk.Label(target_input_line, text="kg", style="Section.TLabel").pack(side="left", padx=(10, 4))
        self.formulation_rows: list[FormulationRow] = []
        self.formulation_total_var.trace_add("write", lambda *_: self.refresh_formulation())

        self.formulation_summary = ttk.Frame(self.formulation_page, style="Card.TFrame", padding=16)
        self.formulation_summary.pack(fill="x", pady=(14, 0))
        self.formulation_summary.columnconfigure(0, weight=1)
        self.formulation_summary.columnconfigure(1, weight=1)
        ttk.Label(self.formulation_summary, text="TOTAL GRAMASI ACUAN", style="CardTitle.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(self.formulation_summary, text="TOTAL PERSENTASE", style="CardTitle.TLabel").grid(
            row=0, column=1, sticky="w", padx=(16, 0)
        )
        self.formulation_gramasi_total = ttk.Label(
            self.formulation_summary, text="0 g", style="CardValue.TLabel"
        )
        self.formulation_gramasi_total.grid(row=1, column=0, sticky="w", pady=(5, 0))
        self.formulation_percentage_total = ttk.Label(
            self.formulation_summary, text="0%", style="CardValue.TLabel"
        )
        self.formulation_percentage_total.grid(row=1, column=1, sticky="w", padx=(16, 0), pady=(5, 0))
        self.formulation_status = ttk.Label(
            self.formulation_page, text="", style="Error.TLabel"
        )
        self.formulation_status.pack(anchor="w", pady=(8, 0))
        self.add_formulation_row()

        self.itemlist_page = ttk.Frame(outer)
        itemlist_heading = ttk.Frame(self.itemlist_page)
        itemlist_heading.pack(fill="x")
        ttk.Button(
            itemlist_heading,
            text="← Kembali",
            style="Secondary.TButton",
            command=self.return_from_itemlist,
        ).pack(side="left", padx=(0, 16))
        ttk.Label(itemlist_heading, text="ItemList", style="Title.TLabel").pack(side="left")
        ttk.Label(
            self.itemlist_page,
            text="Kelola daftar nama produk dan bahan. Data tersimpan lokal di komputer ini.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(12, 16))

        self.itemlist_kind = tk.StringVar(value="material")
        kind_tabs = ttk.Frame(self.itemlist_page)
        kind_tabs.pack(fill="x", pady=(0, 12))
        ttk.Radiobutton(
            kind_tabs,
            text="Bahan / Material",
            value="material",
            variable=self.itemlist_kind,
            command=self.refresh_itemlist,
        ).pack(side="left", padx=(0, 16))
        ttk.Radiobutton(
            kind_tabs,
            text="Produk",
            value="product",
            variable=self.itemlist_kind,
            command=self.refresh_itemlist,
        ).pack(side="left")

        item_card = ttk.Frame(self.itemlist_page, style="Card.TFrame", padding=16)
        item_card.pack(fill="x")
        ttk.Label(item_card, text="Nama lengkap", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 7))
        add_line = ttk.Frame(item_card, style="Card.TFrame")
        add_line.pack(fill="x")
        self.itemlist_name_var = tk.StringVar()
        item_name_entry = ttk.Entry(add_line, textvariable=self.itemlist_name_var, font=("Segoe UI", 11))
        item_name_entry.pack(side="left", fill="x", expand=True)
        item_name_entry.bind("<Return>", lambda _event: self.add_itemlist_item())
        ttk.Button(
            add_line,
            text="+ Tambah",
            style="Primary.TButton",
            command=self.add_itemlist_item,
        ).pack(side="left", padx=(10, 0))

        list_card = ttk.Frame(self.itemlist_page, style="Card.TFrame", padding=16)
        list_card.pack(fill="both", expand=True, pady=(14, 0))
        list_header = ttk.Frame(list_card, style="Card.TFrame")
        list_header.pack(fill="x", pady=(0, 8))
        ttk.Label(list_header, text="Daftar tersimpan", style="Section.TLabel").pack(side="left")
        ttk.Button(
            list_header,
            text="Hapus pilihan",
            style="Remove.TButton",
            command=self.delete_selected_item,
        ).pack(side="right")
        self.itemlist_listbox = tk.Listbox(
            list_card,
            height=12,
            font=("Segoe UI", 10),
            bg="#fbfcfe",
            fg=TEXT,
            relief="solid",
            borderwidth=1,
            selectbackground=BLUE,
            selectforeground=WHITE,
            activestyle="none",
        )
        self.itemlist_listbox.pack(fill="both", expand=True)
        self.itemlist_listbox.bind("<Double-Button-1>", lambda _event: self.delete_selected_item())
        self._itemlist_current_items: list[tuple[int, str]] = []
        self.refresh_itemlist()

    def show_formulation_page(self) -> None:
        self._show_page("formulation", "DmasterCounter | Perhitungan Formulasi")

    def show_calculator_page(self) -> None:
        self._show_page("calculator", "DmasterCounter | Kalkulator Pail Produksi")
        self._update_product_title()

    def show_itemlist_page(self) -> None:
        if self.active_page in {"calculator", "formulation"}:
            self._itemlist_return_page = self.active_page
        self.refresh_itemlist()
        self._show_page("itemlist", "DmasterCounter | ItemList")

    def return_from_itemlist(self) -> None:
        if self._itemlist_return_page == "formulation":
            self._show_page("formulation", "DmasterCounter | Perhitungan Formulasi")
        else:
            self.show_calculator_page()

    def _show_page(self, page_name: str, title: str) -> None:
        for name in ("calculator", "formulation", "itemlist"):
            getattr(self, f"{name}_page").pack_forget()
        getattr(self, f"{page_name}_page").pack(fill="both", expand=True)
        self.active_page = page_name
        self.root.title(title)
        self._reset_page_scroll()

    def refresh_itemlist(self) -> None:
        if not hasattr(self, "itemlist_listbox"):
            return
        self._itemlist_current_items = self.item_database.list_items(self.itemlist_kind.get())
        self.itemlist_listbox.delete(0, "end")
        for _item_id, name in self._itemlist_current_items:
            self.itemlist_listbox.insert("end", name)

    def add_itemlist_item(self) -> None:
        name = self.itemlist_name_var.get().strip()
        try:
            added = self.item_database.add_item(self.itemlist_kind.get(), name)
        except ValueError as exc:
            messagebox.showwarning("Nama belum diisi", str(exc))
            return
        if not added:
            messagebox.showinfo("Sudah terdaftar", f"{name} sudah ada di ItemList.")
            return
        self.itemlist_name_var.set("")
        self.refresh_itemlist()

    def delete_selected_item(self) -> None:
        selected = self.itemlist_listbox.curselection()
        if not selected:
            messagebox.showinfo("Belum ada pilihan", "Pilih nama yang ingin dihapus terlebih dahulu.")
            return
        index = selected[0]
        item_id, name = self._itemlist_current_items[index]
        if not messagebox.askyesno("Hapus item", f"Hapus '{name}' dari ItemList?"):
            return
        self.item_database.delete_item(item_id)
        self.refresh_itemlist()

    def complete_item_name(self, entry: ttk.Entry, kind: str) -> str:
        query = entry.get().strip()
        if not query:
            return "break"
        if kind == "product":
            matches = search_product_names(
                self.item_database.list_items("product"),
                self.item_database.list_items("material"),
                query,
            )
        else:
            matches = search_items(self.item_database.list_items(kind), query)
        if not matches:
            return "break"
        if len(matches) == 1:
            entry.delete(0, "end")
            entry.insert(0, matches[0][1])
            self._close_autocomplete()
            entry.icursor("end")
            return "break"
        self._show_autocomplete(entry, matches)
        return "break"

    def _show_autocomplete(self, entry: ttk.Entry, matches: list[tuple[int, str]]) -> None:
        self._close_autocomplete()
        popup = tk.Toplevel(self.root)
        popup.overrideredirect(True)
        listbox = tk.Listbox(
            popup,
            height=min(len(matches), 8),
            width=max(26, min(max(len(name) for _, name in matches) + 4, 55)),
            font=("Segoe UI", 10),
            bg=WHITE,
            fg=TEXT,
            selectbackground=BLUE,
            selectforeground=WHITE,
            activestyle="none",
        )
        listbox.pack(fill="both", expand=True)
        for _item_id, name in matches:
            listbox.insert("end", name)
        listbox.selection_set(0)
        listbox.activate(0)
        popup.update_idletasks()
        x = entry.winfo_rootx()
        y = entry.winfo_rooty() + entry.winfo_height()
        popup.geometry(f"+{x}+{y}")
        popup.lift()
        listbox.bind("<Return>", lambda _event: self._accept_autocomplete())
        listbox.bind("<KP_Enter>", lambda _event: self._accept_autocomplete())
        listbox.bind("<ButtonRelease-1>", lambda _event: self._accept_autocomplete())
        listbox.bind("<Double-Button-1>", lambda _event: self._accept_autocomplete())
        listbox.bind("<Escape>", lambda _event: self._cancel_autocomplete())
        listbox.bind("<Up>", self._move_autocomplete_selection)
        listbox.bind("<Down>", self._move_autocomplete_selection)
        self._autocomplete_popup = popup
        self._autocomplete_list = listbox
        self._autocomplete_entry = entry
        listbox.focus_set()

    def _move_autocomplete_selection(self, event: tk.Event) -> str:
        if self._autocomplete_list is None:
            return "break"
        count = self._autocomplete_list.size()
        if count == 0:
            return "break"
        selection = self._autocomplete_list.curselection()
        index = selection[0] if selection else 0
        index = max(0, min(count - 1, index + (1 if event.keysym == "Down" else -1)))
        self._autocomplete_list.selection_clear(0, "end")
        self._autocomplete_list.selection_set(index)
        self._autocomplete_list.activate(index)
        self._autocomplete_list.see(index)
        return "break"

    def _accept_autocomplete(self) -> str:
        if self._autocomplete_list is None or self._autocomplete_entry is None:
            return "break"
        selected = self._autocomplete_list.curselection()
        if not selected:
            return "break"
        value = self._autocomplete_list.get(selected[0])
        entry = self._autocomplete_entry
        entry.delete(0, "end")
        entry.insert(0, value)
        self._close_autocomplete()
        entry.focus_set()
        entry.icursor("end")
        return "break"

    def _cancel_autocomplete(self) -> str:
        entry = self._autocomplete_entry
        self._close_autocomplete()
        if entry is not None:
            entry.focus_set()
            entry.icursor("end")
        return "break"

    def _close_autocomplete(self) -> None:
        if self._autocomplete_popup is not None:
            try:
                self._autocomplete_popup.destroy()
            except tk.TclError:
                pass
        self._autocomplete_popup = None
        self._autocomplete_list = None
        self._autocomplete_entry = None

    def add_formulation_row(self) -> None:
        row = FormulationRow(self)
        self.formulation_rows.append(row)
        row.frame.pack(fill="x", pady=(0, 5))
        self.refresh_formulation()
        row.name_entry.focus_set()

    def remove_formulation_row(self, row: FormulationRow) -> None:
        row.frame.destroy()
        self.formulation_rows.remove(row)
        self.refresh_formulation()

    def refresh_formulation(self) -> None:
        gramasi_values: list[Decimal] = []
        active_rows: list[FormulationRow] = []
        invalid_found = False

        for row in self.formulation_rows:
            raw = row.gramasi_var.get().strip()
            if not raw:
                row.set_result()
                continue
            if not row.name_var.get().strip():
                row.set_result(error="Isi nama bahan.")
                invalid_found = True
                continue
            try:
                gramasi = parse_quantity(raw)
                if gramasi <= 0:
                    raise ValueError("Gramasi harus lebih besar dari 0.")
            except ValueError as exc:
                row.set_result(error=str(exc))
                invalid_found = True
                continue
            active_rows.append(row)
            gramasi_values.append(gramasi)
            row.set_result("—", "—")

        if invalid_found:
            self.formulation_gramasi_total.configure(text="Periksa input")
            self.formulation_percentage_total.configure(text="—")
            self.formulation_status.configure(text="Lengkapi atau perbaiki baris bahan yang ditandai.")
            return

        if not gramasi_values:
            self.formulation_gramasi_total.configure(text="0 g")
            self.formulation_percentage_total.configure(text="0%")
            self.formulation_status.configure(text="Masukkan gramasi bahan, lalu isi total produksi.")
            return

        gramasi_total = sum(gramasi_values, Decimal("0"))
        percentages = [value / gramasi_total * Decimal("100") for value in gramasi_values]
        self.formulation_gramasi_total.configure(text=f"{pretty_decimal(gramasi_total)} g")
        self.formulation_percentage_total.configure(text=f"{pretty_decimal(sum(percentages, Decimal('0')))}%")

        target_raw = self.formulation_total_var.get().strip()
        if not target_raw:
            for row, percentage in zip(active_rows, percentages):
                row.set_result("—", f"{pretty_decimal(percentage)}%")
            self.formulation_status.configure(text="Isi total produksi untuk menghitung jumlah kg setiap bahan.")
            return

        try:
            results, _ = calculate_formulation(gramasi_values, target_raw)
        except ValueError as exc:
            for row, percentage in zip(active_rows, percentages):
                row.set_result("—", f"{pretty_decimal(percentage)}%")
            self.formulation_status.configure(text=str(exc))
            return

        for row, result in zip(active_rows, results):
            row.set_result(
                f"{pretty_decimal(result.quantity_kg, 3)} kg",
                f"{pretty_decimal(result.percentage)}%",
            )
        self.formulation_status.configure(text="Perhitungan diperbarui otomatis.")

    def _reset_page_scroll(self) -> None:
        self.root.after_idle(lambda: self.page_canvas.configure(scrollregion=self.page_canvas.bbox("all")))
        self.root.after_idle(lambda: self.page_canvas.yview_moveto(0))

    def _summary_card(self, parent: ttk.Frame, title: str, value: str, detail: str) -> ttk.Frame:
        card = ttk.Frame(parent, style="Card.TFrame", padding=(16, 12))
        card.grid(row=0, column=0 if title == "TOTAL PRODUK" else 1, sticky="ew", padx=(0, 7) if title == "TOTAL PRODUK" else (7, 0))
        ttk.Label(card, text=title, style="CardTitle.TLabel").pack(anchor="w")
        value_label = ttk.Label(card, text=value, style="CardValue.TLabel")
        value_label.pack(anchor="w", pady=(5, 1))
        detail_label = ttk.Label(card, text=detail, style="Subtitle.TLabel")
        detail_label.pack(anchor="w")
        setattr(card, "value_label", value_label)
        setattr(card, "detail_label", detail_label)
        return card

    def _update_page_scroll_region(self, _event: tk.Event) -> None:
        self.page_canvas.configure(scrollregion=self.page_canvas.bbox("all"))

    def _fit_page_width(self, event: tk.Event) -> None:
        self.page_canvas.itemconfigure(self.page_window, width=event.width)

    def _on_mousewheel(self, event: tk.Event) -> str:
        if getattr(event, "num", None) == 4:
            direction = -1
        elif getattr(event, "num", None) == 5:
            direction = 1
        else:
            direction = -1 if event.delta > 0 else 1
        self.page_canvas.yview_scroll(direction, "units")
        return "break"

    def _update_product_title(self) -> None:
        if self.active_page != "calculator":
            return
        name = self.product_name.get().strip()
        suffix = f" — {name}" if name else ""
        self.root.title(f"DmasterCounter{suffix} | Kalkulator Pail Produksi")

    def _on_product_name_changed(self) -> None:
        self._update_product_title()
        self.update_printout()

    def _create_print_panel(
        self,
        parent: ttk.Frame,
        title: str,
        copy_command: object,
        column: int,
    ) -> tk.Text:
        card = ttk.Frame(parent, style="Card.TFrame", padding=14)
        card.grid(row=0, column=column, sticky="nsew", padx=(0, 7) if column == 0 else (7, 0))
        header = ttk.Frame(card, style="Card.TFrame")
        header.pack(fill="x", pady=(0, 8))
        ttk.Label(header, text=title, style="Section.TLabel").pack(side="left")
        ttk.Button(header, text="Salin", style="Secondary.TButton", command=copy_command).pack(side="right")
        text_box = tk.Text(
            card,
            height=9,
            wrap="word",
            font=("Consolas", 10),
            bg="#fbfcfe",
            fg=TEXT,
            relief="solid",
            borderwidth=1,
            padx=12,
            pady=10,
        )
        text_box.pack(fill="x")
        text_box.configure(state="disabled")
        return text_box

    def update_printout(self) -> None:
        material_rows = [(row.name_var.get(), row.quantity_var.get()) for row in self.rows]
        self._set_print_text(self.printout_text, build_printout(self.product_name.get(), material_rows))
        self._set_print_text(
            self.pail_printout_text,
            build_pail_printout(self.product_name.get(), material_rows),
        )

    @staticmethod
    def _set_print_text(text_box: tk.Text, output: str) -> None:
        text_box.configure(state="normal")
        text_box.delete("1.0", "end")
        text_box.insert("1.0", output)
        text_box.configure(state="disabled")

    def copy_printout(self) -> None:
        self._copy_print_text(self.printout_text)

    def copy_pail_printout(self) -> None:
        self._copy_print_text(self.pail_printout_text)

    def _copy_print_text(self, text_box: tk.Text) -> None:
        output = text_box.get("1.0", "end-1c")
        if not output.strip():
            messagebox.showinfo("Pratinjau kosong", "Isi nama produk dan bahan beserta jumlah kg terlebih dahulu.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(output)
        self.root.update()
        messagebox.showinfo("Tersalin", "Teks print out sudah disalin ke clipboard.")

    def add_row(self) -> None:
        row = MaterialRow(self, len(self.rows) + 1)
        self.rows.append(row)
        row.frame.pack(fill="x", pady=(0, 5))
        self.refresh()
        row.name_entry.focus_set()

    def remove_row(self, row: MaterialRow) -> None:
        row.frame.destroy()
        self.rows.remove(row)
        self.refresh()

    def clear_all(self) -> None:
        if not any(row.name_var.get().strip() or row.quantity_var.get().strip() for row in self.rows):
            return
        if not messagebox.askyesno("Bersihkan data", "Hapus nama produk dan seluruh daftar material?"):
            return
        self.product_name.set("")
        for row in self.rows:
            row.frame.destroy()
        self.rows.clear()
        self.add_row()

    def refresh(self) -> None:
        if self._refreshing:
            return
        self._refreshing = True
        try:
            entered_quantities: list[Decimal] = []
            material_whole_pails = 0
            invalid_found = False
            for row in self.rows:
                raw = row.quantity_var.get().strip()
                if not raw:
                    row.set_result("—", "—")
                    continue
                try:
                    quantity = parse_quantity(raw)
                    result = calculate_pails(quantity)
                    row.set_result(f"{pretty_decimal(result.equivalent_pails)} pail", str(result.whole_pails))
                    entered_quantities.append(quantity)
                    material_whole_pails += result.whole_pails
                except ValueError as exc:
                    row.set_result("—", "—", str(exc))
                    invalid_found = True

            if invalid_found:
                self._set_card(self.product_summary, "Periksa input", "Total belum dihitung")
                self._set_card(self.material_summary, "—", "Periksa jumlah material")
                return

            total = calculate_total(entered_quantities)
            self._set_card(
                self.product_summary,
                f"{pretty_decimal(total.quantity_kg)} kg",
                f"{pretty_decimal(total.equivalent_pails)} pail setara  ·  {total.whole_pails} pail utuh",
            )
            self._set_card(
                self.material_summary,
                f"{material_whole_pails} pail",
                "Jumlah pail utuh per material",
            )
        finally:
            self._refreshing = False
            self.update_printout()

    @staticmethod
    def _set_card(card: ttk.Frame, value: str, detail: str) -> None:
        getattr(card, "value_label").configure(text=value)
        getattr(card, "detail_label").configure(text=detail)


def main() -> None:
    root = tk.Tk()
    DmasterCounterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
