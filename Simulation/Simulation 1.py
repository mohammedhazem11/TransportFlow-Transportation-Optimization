import tkinter as tk
from tkinter import ttk, messagebox

# ============================================================
# TRANSPORTFLOW - THREE-SCENARIO TRANSPORTATION SIMULATION
# Methods: Vogel's Approximation Method (VAM), Least Cost, MODI
# ============================================================

CITIES = ["Company 1", "Company 2", "Company 3", "Company 4"]
DESTINATIONS = [
    "Bank", "Hospital", "Store", "Telecom", "University",
    "Insurance", "Airline", "Factory", "Ministry", "Media"
]
COST = [
    [1, 3, 9, 8, 5, 2, 2, 4, 12, 3],
    [4, 4, 14, 12, 9, 2, 7, 7, 16, 2],
    [18, 20, 8, 10, 13, 19, 20, 22, 4, 21],
    [13, 15, 4, 6, 8, 15, 16, 18, 1, 17]
]
SUPPLY = [40, 60, 50, 50]

SCENARIOS = {
    "Demand > Supply": {
        "demand": [30, 30, 20, 20, 20, 20, 20, 20, 20, 20],
        "description": "Demand is 20 units higher than supply.",
        "accent": "#f59e0b"
    },
    "Supply > Demand": {
        "demand": [15, 15, 20, 20, 20, 20, 20, 20, 20, 10],
        "description": "Supply is 20 units higher than demand.",
        "accent": "#8b5cf6"
    },
    "Balanced": {
        "demand": [20] * 10,
        "description": "Total supply equals total demand.",
        "accent": "#0d9488"
    }
}

BG = "#eef4fb"
PANEL = "#ffffff"
INK = "#14213d"
MUTED = "#64748b"
BLUE = "#2563eb"
BLUE_DARK = "#173b75"
BLUE_LIGHT = "#dbeafe"
TEAL = "#0d9488"
TEAL_LIGHT = "#ccfbf1"
PURPLE = "#8b5cf6"
AMBER = "#f59e0b"
AMBER_LIGHT = "#fef3c7"
GREEN = "#16a34a"
GREEN_LIGHT = "#dcfce7"
BORDER = "#d8e3f0"
ROAD = "#dce5ef"


# ----------------------- OPTIMIZATION ------------------------

def balance_problem(cost, supply, demand):
    balanced_cost = [row[:] for row in cost]
    balanced_supply = supply[:]
    balanced_demand = demand[:]
    row_names = CITIES[:]
    col_names = DESTINATIONS[:]

    supply_total = sum(balanced_supply)
    demand_total = sum(balanced_demand)

    if supply_total > demand_total:
        difference = supply_total - demand_total
        balanced_demand.append(difference)
        col_names.append("Dummy Destination")
        for row in balanced_cost:
            row.append(0)
    elif demand_total > supply_total:
        difference = demand_total - supply_total
        balanced_supply.append(difference)
        row_names.append("Dummy Source")
        balanced_cost.append([0] * len(balanced_demand))

    return balanced_cost, balanced_supply, balanced_demand, row_names, col_names


def vogel_approximation(cost, supply, demand):
    supply_left = supply[:]
    demand_left = demand[:]
    rows, cols = len(supply_left), len(demand_left)
    allocation = [[0] * cols for _ in range(rows)]

    while any(x > 0 for x in supply_left) and any(x > 0 for x in demand_left):
        row_penalties = [None] * rows
        col_penalties = [None] * cols

        for i in range(rows):
            if supply_left[i] <= 0:
                continue
            values = sorted(cost[i][j] for j in range(cols) if demand_left[j] > 0)
            if values:
                row_penalties[i] = values[1] - values[0] if len(values) >= 2 else values[0]

        for j in range(cols):
            if demand_left[j] <= 0:
                continue
            values = sorted(cost[i][j] for i in range(rows) if supply_left[i] > 0)
            if values:
                col_penalties[j] = values[1] - values[0] if len(values) >= 2 else values[0]

        best_row_penalty = max((p for p in row_penalties if p is not None), default=-1)
        best_col_penalty = max((p for p in col_penalties if p is not None), default=-1)

        if best_row_penalty < 0 and best_col_penalty < 0:
            break

        if best_row_penalty >= best_col_penalty:
            i = row_penalties.index(best_row_penalty)
            candidates = [(cost[i][j], j) for j in range(cols) if demand_left[j] > 0]
            _, j = min(candidates)
        else:
            j = col_penalties.index(best_col_penalty)
            candidates = [(cost[i][j], i) for i in range(rows) if supply_left[i] > 0]
            _, i = min(candidates)

        amount = min(supply_left[i], demand_left[j])
        allocation[i][j] += amount
        supply_left[i] -= amount
        demand_left[j] -= amount

    return allocation


def least_cost_method(cost, supply, demand):
    supply_left = supply[:]
    demand_left = demand[:]
    rows, cols = len(supply_left), len(demand_left)
    allocation = [[0] * cols for _ in range(rows)]

    while any(x > 0 for x in supply_left) and any(x > 0 for x in demand_left):
        choices = [
            (cost[i][j], i, j)
            for i in range(rows)
            for j in range(cols)
            if supply_left[i] > 0 and demand_left[j] > 0
        ]
        if not choices:
            break
        _, i, j = min(choices)
        amount = min(supply_left[i], demand_left[j])
        allocation[i][j] += amount
        supply_left[i] -= amount
        demand_left[j] -= amount

    return allocation


def total_cost(allocation, cost):
    return sum(
        allocation[i][j] * cost[i][j]
        for i in range(len(allocation))
        for j in range(len(allocation[i]))
    )


# -------------------------- MODI METHOD -----------------------

def complete_basis(allocation, cost):
    m, n = len(cost), len(cost[0])

    basis = {
        (i, j)
        for i in range(m)
        for j in range(n)
        if allocation[i][j] > 0
    }

    parent = list(range(m + n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        root_a = find(a)
        root_b = find(b)
        if root_a != root_b:
            parent[root_a] = root_b

    for i, j in basis:
        union(i, m + j)

    candidates = sorted(
        (cost[i][j], i, j)
        for i in range(m)
        for j in range(n)
        if (i, j) not in basis
    )

    for _, i, j in candidates:
        if len(basis) >= m + n - 1:
            break
        if find(i) != find(m + j):
            basis.add((i, j))
            union(i, m + j)

    return basis


def potentials(cost, basis):
    m, n = len(cost), len(cost[0])
    u = [None] * m
    v = [None] * n
    u[0] = 0

    changed = True
    while changed:
        changed = False
        for i, j in basis:
            if u[i] is not None and v[j] is None:
                v[j] = cost[i][j] - u[i]
                changed = True
            elif v[j] is not None and u[i] is None:
                u[i] = cost[i][j] - v[j]
                changed = True

    return u, v


def loop_path(basis, row, col):
    adjacency = {}

    for i, j in basis:
        adjacency.setdefault(("r", i), []).append((("c", j), (i, j)))
        adjacency.setdefault(("c", j), []).append((("r", i), (i, j)))

    start = ("r", row)
    target = ("c", col)
    stack = [(start, [])]
    visited = {start}

    while stack:
        node, path = stack.pop()
        if node == target:
            return path
        for next_node, cell in adjacency.get(node, []):
            if next_node not in visited:
                visited.add(next_node)
                stack.append((next_node, path + [cell]))

    return None


def modi(cost, start_allocation):
    allocation = [row[:] for row in start_allocation]
    m, n = len(cost), len(cost[0])
    basis = complete_basis(allocation, cost)

    while True:
        u, v = potentials(cost, basis)
        best = None

        for i in range(m):
            for j in range(n):
                if (i, j) not in basis:
                    delta = cost[i][j] - u[i] - v[j]
                    if delta < -1e-9 and (best is None or delta < best[0]):
                        best = (delta, i, j)

        if best is None:
            return allocation, total_cost(allocation, cost), []

        delta, i, j = best
        path = loop_path(basis, i, j)
        if path is None:
            raise RuntimeError("MODI could not find a closed loop.")

        minus_cells = path[0::2]
        plus_cells = path[1::2]
        if not minus_cells:
            raise RuntimeError("MODI loop has no minus cells.")

        theta = min(allocation[a][b] for a, b in minus_cells)
        leaving_cell = next(
            cell for cell in minus_cells
            if allocation[cell[0]][cell[1]] == theta
        )

        allocation[i][j] += theta
        for a, b in plus_cells:
            allocation[a][b] += theta
        for a, b in minus_cells:
            allocation[a][b] -= theta

        basis.remove(leaving_cell)
        basis.add((i, j))


# -------------------------- APPLICATION ----------------------

class TransportSimulation:
    def __init__(self, root):
        self.root = root
        self.root.title("TransportFlow | Three-Scenario Simulation")
        self.root.geometry("1280x760")
        self.root.minsize(1000, 650)
        self.root.configure(bg=BG)

        self.canvas_width = 850
        self.canvas_height = 530
        self.routes = []
        self.route_index = 0
        self.animation_token = 0
        self.is_running = False
        self.scenario_name = "Balanced"
        self.current_row_names = CITIES[:]
        self.current_col_names = DESTINATIONS[:]
        self._all_scenarios = []
        self._all_scenario_index = 0

        self._configure_styles()
        self._build_ui()
        self.root.after(100, self.draw_scene)
        self._set_metrics("— EGP", "—", "—")

    def _configure_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"),
                        padding=(10, 8), background=BLUE, foreground="white", borderwidth=0)
        style.map("Primary.TButton",
                  background=[("active", "#1d4ed8"), ("disabled", "#94a3b8")])
        style.configure("Secondary.TButton", font=("Segoe UI", 10, "bold"),
                        padding=(10, 7), background="#e7eef8", foreground=INK, borderwidth=0)
        style.map("Secondary.TButton", background=[("active", "#d7e5f7")])
        style.configure("App.TCombobox", font=("Segoe UI", 10), padding=6)

    def _build_ui(self):
        # Scrollable page: keeps all controls reachable on smaller laptop screens.
        self.page_container = tk.Frame(self.root, bg=BG)
        self.page_container.pack(fill="both", expand=True)

        self.page_canvas = tk.Canvas(self.page_container, bg=BG, highlightthickness=0)
        self.page_scrollbar = ttk.Scrollbar(
            self.page_container, orient="vertical", command=self.page_canvas.yview
        )
        self.page_canvas.configure(yscrollcommand=self.page_scrollbar.set)
        self.page_scrollbar.pack(side="right", fill="y")
        self.page_canvas.pack(side="left", fill="both", expand=True)

        self.page_frame = tk.Frame(self.page_canvas, bg=BG)
        self.page_window = self.page_canvas.create_window(
            (0, 0), window=self.page_frame, anchor="nw"
        )
        self.page_frame.bind("<Configure>", self._update_scroll_region)
        self.page_canvas.bind("<Configure>", self._fit_page_width)
        self.root.bind_all("<MouseWheel>", self._on_mousewheel)
        self.root.bind_all("<Button-4>", self._on_mousewheel_linux)
        self.root.bind_all("<Button-5>", self._on_mousewheel_linux)

        header = tk.Frame(self.page_frame, bg=BLUE_DARK, height=82)
        header.pack(fill="x")
        header.pack_propagate(False)

        brand = tk.Frame(header, bg=BLUE_DARK)
        brand.pack(side="left", padx=22, pady=11)
        tk.Label(brand, text="TRANSPORTFLOW", bg=BLUE_DARK, fg="white",
                 font=("Segoe UI", 21, "bold")).pack(anchor="w")
        tk.Label(brand, text="Smart allocation • Three scenarios • Animated routes",
                 bg=BLUE_DARK, fg="#c7dcff", font=("Segoe UI", 9)).pack(anchor="w")
        tk.Label(header, text="OPTIMIZATION LAB / SIMULATION", bg=BLUE_DARK,
                 fg="#a5f3fc", font=("Segoe UI", 9, "bold")).pack(side="right", padx=22)

        main = tk.Frame(self.page_frame, bg=BG)
        main.pack(fill="both", expand=True, padx=14, pady=12)

        left = tk.Frame(main, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        left.pack(side="left", fill="both", expand=True, padx=(0, 12))

        scene_top = tk.Frame(left, bg=PANEL)
        scene_top.pack(fill="x", padx=14, pady=(12, 7))
        tk.Label(scene_top, text="Live transportation network", bg=PANEL, fg=INK,
                 font=("Segoe UI", 13, "bold")).pack(side="left")
        self.live_badge = tk.Label(scene_top, text="● READY", bg=GREEN_LIGHT, fg=GREEN,
                                   font=("Segoe UI", 9, "bold"), padx=9, pady=4)
        self.live_badge.pack(side="right")

        self.canvas = tk.Canvas(left, bg="#f8fbff", highlightthickness=0, height=500)
        self.canvas.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.canvas.bind("<Configure>", lambda _event: self.draw_scene() if not self.is_running else None)

        right = tk.Frame(main, bg=PANEL, width=300, highlightbackground=BORDER, highlightthickness=1)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        tk.Label(right, text="Simulation controls", bg=PANEL, fg=INK,
                 font=("Segoe UI", 15, "bold")).pack(anchor="w", padx=16, pady=(15, 2))
        tk.Label(right, text="Select a scenario and allocation method.", bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 9)).pack(anchor="w", padx=16, pady=(0, 10))

        tk.Label(right, text="SCENARIO", bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=16, pady=(0, 4))
        self.scenario_var = tk.StringVar(value="Balanced")
        self.scenario_box = ttk.Combobox(right, textvariable=self.scenario_var,
                                         values=list(SCENARIOS.keys()), state="readonly",
                                         style="App.TCombobox")
        self.scenario_box.pack(fill="x", padx=16, pady=(0, 5))
        self.scenario_box.bind("<<ComboboxSelected>>", self._scenario_changed)

        self.scenario_description = tk.Label(
            right, text=SCENARIOS["Balanced"]["description"], bg="#ccfbf1", fg="#115e59",
            font=("Segoe UI", 9), justify="left", wraplength=250, padx=9, pady=7
        )
        self.scenario_description.pack(fill="x", padx=16, pady=(2, 10))

        tk.Label(right, text="ALLOCATION METHOD", bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=16, pady=(0, 4))
        self.method_var = tk.StringVar(value="VAM")
        self.method_box = ttk.Combobox(right, textvariable=self.method_var,
                                       values=["VAM", "Least Cost", "MODI"], state="readonly",
                                       style="App.TCombobox")
        self.method_box.pack(fill="x", padx=16, pady=(0, 9))
        self.method_box.bind("<<ComboboxSelected>>", self._method_changed)

        self.start_button = ttk.Button(right, text="▶  Start simulation",
                                       style="Primary.TButton", command=self.start_simulation)
        self.start_button.pack(fill="x", padx=16, pady=3)
        ttk.Button(right, text="↻  Reset scene", style="Secondary.TButton",
                   command=self.reset).pack(fill="x", padx=16, pady=3)
        self.all_button = ttk.Button(right, text="▶▶  Run all 3 scenarios",
                                      style="Secondary.TButton", command=self.run_all_scenarios)
        self.all_button.pack(fill="x", padx=16, pady=3)

        tk.Label(right, text="LIVE SUMMARY", bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=16, pady=(14, 5))
        self.cost_value = self._metric_card(right, "Transportation cost", "— EGP", BLUE)
        self.routes_value = self._metric_card(right, "Active routes", "—", TEAL)
        self.people_value = self._metric_card(right, "Units allocated", "—", PURPLE)

        tk.Label(right, text="CURRENT STATUS", bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=16, pady=(11, 4))
        self.status_label = tk.Label(right, text="Ready to start", bg="#f1f5f9", fg=INK,
                                     font=("Segoe UI", 9), justify="left", anchor="nw",
                                     wraplength=255, padx=9, pady=8, height=4)
        self.status_label.pack(fill="x", padx=16)
        self.result_label = tk.Label(right, text="", bg=PANEL, fg=MUTED,
                                     font=("Segoe UI", 9), justify="left", wraplength=255)
        self.result_label.pack(anchor="w", padx=16, pady=(7, 0))

        footer = tk.Frame(self.page_frame, bg=BG)
        footer.pack(fill="x", padx=18, pady=(0, 8))
        for label, color in [("● Source", BLUE), ("■ Destination", TEAL),
                             ("━ Active route", AMBER), ("● Completed", GREEN)]:
            tk.Label(footer, text=label, bg=BG, fg=color,
                     font=("Segoe UI", 8, "bold")).pack(side="left", padx=(0, 13))
        tk.Label(footer, text="Visual demonstration • Not live GPS data", bg=BG, fg=MUTED,
                 font=("Segoe UI", 8)).pack(side="right")

    def _update_scroll_region(self, _event=None):
        self.page_canvas.configure(scrollregion=self.page_canvas.bbox("all"))

    def _fit_page_width(self, event):
        self.page_canvas.itemconfigure(self.page_window, width=event.width)

    def _on_mousewheel(self, event):
        # Windows: delta is usually +/-120. Keep the scroll responsive on laptops.
        if event.delta:
            self.page_canvas.yview_scroll(int(-event.delta / 120), "units")

    def _on_mousewheel_linux(self, event):
        if event.num == 4:
            self.page_canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.page_canvas.yview_scroll(1, "units")

    def _metric_card(self, parent, label, value, accent):
        card = tk.Frame(parent, bg="#f8fafc", highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="x", padx=16, pady=2)
        tk.Frame(card, bg=accent, width=4).pack(side="left", fill="y")
        content = tk.Frame(card, bg="#f8fafc")
        content.pack(side="left", fill="both", expand=True, padx=8, pady=5)
        tk.Label(content, text=label, bg="#f8fafc", fg=MUTED,
                 font=("Segoe UI", 8)).pack(anchor="w")
        value_label = tk.Label(content, text=value, bg="#f8fafc", fg=INK,
                               font=("Segoe UI", 12, "bold"))
        value_label.pack(anchor="w")
        return value_label

    def _set_metrics(self, cost, routes, people):
        self.cost_value.config(text=cost)
        self.routes_value.config(text=routes)
        self.people_value.config(text=people)

    def _scenario_changed(self, _event=None):
        if self.is_running:
            return
        name = self.scenario_var.get()
        self.scenario_description.config(text=SCENARIOS[name]["description"])
        self.reset()

    def _method_changed(self, _event=None):
        if not self.is_running:
            self.status_label.config(
                text=f"{self.method_var.get()} selected.\nPress Start simulation to calculate routes."
            )

    # -------------------------- DRAWING -----------------------

    def draw_scene(self):
        if not hasattr(self, "canvas") or not self.canvas.winfo_exists():
            return
        self.canvas.delete("all")
        width = max(self.canvas.winfo_width(), 650)
        height = max(self.canvas.winfo_height(), 450)
        self.canvas.create_rectangle(0, 0, width, height, fill="#f8fbff", outline="")
        for x in range(16, width, 38):
            self.canvas.create_line(x, 0, x, height, fill="#edf3fa")
        for y in range(16, height, 38):
            self.canvas.create_line(0, y, width, y, fill="#edf3fa")

        demand_original = SCENARIOS[self.scenario_var.get()]["demand"]
        _, balanced_supply, balanced_demand, row_names, col_names = balance_problem(
            COST, SUPPLY, demand_original
        )
        self.current_row_names = row_names
        self.current_col_names = col_names

        self.canvas.create_text(18, 18, text="SOURCES", anchor="w",
                                font=("Segoe UI", 8, "bold"), fill=MUTED)
        self.canvas.create_text(width - 18, 18, text="DESTINATIONS", anchor="e",
                                font=("Segoe UI", 8, "bold"), fill=MUTED)

        source_x = max(95, width * 0.17)
        dest_x = width - max(105, width * 0.18)
        top, bottom = 65, height - 40
        source_count = len(row_names)
        dest_count = len(col_names)
        source_ys = [top + (bottom - top) * i / max(source_count - 1, 1)
                     for i in range(source_count)]
        dest_ys = [top + (bottom - top) * j / max(dest_count - 1, 1)
                   for j in range(dest_count)]

        road_left, road_right = source_x + 42, dest_x - 42
        if road_right > road_left:
            self.canvas.create_rectangle(road_left, 36, road_right, height - 16,
                                         fill=ROAD, outline="")
            mid = (road_left + road_right) / 2
            for y in range(45, height - 18, 32):
                self.canvas.create_line(mid, y, mid, y + 13, fill="white", width=3)
            self.canvas.create_text(mid, 27, text="TRANSPORT CORRIDOR",
                                    fill="#8495ad", font=("Segoe UI", 7, "bold"))

        self.source_positions = {
            name: (source_x, source_ys[i]) for i, name in enumerate(row_names)
        }
        self.dest_positions = {
            name: (dest_x, dest_ys[j]) for j, name in enumerate(col_names)
        }

        for i, name in enumerate(row_names):
            self._draw_source(name, source_x, source_ys[i], balanced_supply[i],
                              is_dummy=(name == "Dummy Source"))
        for j, name in enumerate(col_names):
            self._draw_destination(name, dest_x, dest_ys[j], balanced_demand[j],
                                   is_dummy=(name == "Dummy Destination"))

    def _draw_source(self, name, x, y, supply, is_dummy=False):
        color = PURPLE if is_dummy else BLUE
        light = "#ede9fe" if is_dummy else BLUE_LIGHT
        self.canvas.create_oval(x - 25, y - 25, x + 25, y + 25,
                                fill=light, outline=color, width=2)
        if is_dummy:
            self.canvas.create_text(x, y, text="D", fill=color,
                                    font=("Segoe UI", 13, "bold"))
        else:
            self.canvas.create_polygon(x - 14, y - 3, x, y - 14, x + 14, y - 3,
                                       fill=color, outline=color)
            self.canvas.create_rectangle(x - 11, y - 3, x + 11, y + 10,
                                         fill="white", outline=color)
        label = name.replace(" ", "\n") if name == "Dummy Source" else name
        self.canvas.create_text(x, y + 34, text=label, fill="#1e3a8a",
                                font=("Segoe UI", 8, "bold"), width=100)
        self.canvas.create_text(x, y + 46, text=f"Supply {supply}",
                                fill=MUTED, font=("Segoe UI", 7))

    def _draw_destination(self, name, x, y, demand, is_dummy=False):
        fill = "#ede9fe" if is_dummy else TEAL_LIGHT
        outline = PURPLE if is_dummy else "#7dd3c7"
        color = "#5b21b6" if is_dummy else "#115e59"
        box_width = 78 if is_dummy else 66
        self.canvas.create_rectangle(x - box_width, y - 14, x + box_width, y + 14,
                                     fill=fill, outline=outline, width=1)
        self.canvas.create_text(x, y - 2, text=name, fill=color,
                                font=("Segoe UI", 7, "bold"), width=box_width * 2 - 4)
        self.canvas.create_text(x, y + 21, text=f"Demand {demand}",
                                fill=MUTED, font=("Segoe UI", 7))

    # ----------------------- ROUTE SIMULATION -----------------

    def _get_scenario_data(self):
        return SCENARIOS[self.scenario_var.get()]["demand"][:]

    def get_allocation(self, method, demand):
        cost, supply, demand, row_names, col_names = balance_problem(COST, SUPPLY, demand)
        if method == "VAM":
            allocation = vogel_approximation(cost, supply, demand)
        elif method == "Least Cost":
            allocation = least_cost_method(cost, supply, demand)
        else:
            initial_allocation = vogel_approximation(cost, supply, demand)
            allocation, _, _ = modi(cost, initial_allocation)
        return allocation, cost, supply, demand, row_names, col_names

    def start_simulation(self):
        if self.is_running:
            return
        self._all_scenarios = []
        self._begin_scenario(self.scenario_var.get())

    def _begin_scenario(self, scenario_name):
        self.animation_token += 1
        token = self.animation_token
        method = self.method_var.get()
        demand_original = SCENARIOS[scenario_name]["demand"][:]
        allocation, cost, supply, demand, row_names, col_names = self.get_allocation(
            method, demand_original
        )

        self.scenario_name = scenario_name
        self.current_allocation = allocation
        self.current_cost = cost
        self.current_supply = supply
        self.current_demand = demand
        self.current_row_names = row_names
        self.current_col_names = col_names
        self.route_index = 0
        self.routes = []

        for i, source in enumerate(row_names):
            for j, destination in enumerate(col_names):
                amount = allocation[i][j]
                if amount > 0:
                    self.routes.append((source, destination, amount, cost[i][j]))

        self.draw_scene()
        self.is_running = True
        self.start_button.state(["disabled"])
        self.all_button.state(["disabled"])
        self.live_badge.config(text="● RUNNING", bg=AMBER_LIGHT, fg="#92400e")

        assigned = sum(route[2] for route in self.routes)
        cost_total = total_cost(allocation, cost)
        self._set_metrics(f"{cost_total:,.0f} EGP", str(len(self.routes)), f"{assigned:,}")

        supply_total = sum(SUPPLY)
        demand_total = sum(demand_original)
        summary = f"Supply: {supply_total} | Demand: {demand_total}"
        if supply_total > demand_total:
            summary += f"\nDummy Destination: {supply_total - demand_total} unused units."
        elif demand_total > supply_total:
            summary += f"\nDummy Source: {demand_total - supply_total} unmet units."
        summary += f"\nMethod: {method} | Total cost: {cost_total:,.0f} EGP"
        self.result_label.config(text=summary)
        self.status_label.config(
            text=f"{scenario_name}\n{method} allocation calculated.\nAnimating assigned routes..."
        )
        self._animate_next_route(token)

    def _animate_next_route(self, token):
        if token != self.animation_token:
            return
        if self.route_index >= len(self.routes):
            self.is_running = False
            self.start_button.state(["!disabled"])
            self.all_button.state(["!disabled"])
            self.live_badge.config(text="● COMPLETE", bg=GREEN_LIGHT, fg=GREEN)
            self.status_label.config(
                text=f"{self.scenario_name}\nSimulation complete.\nAll allocated routes finished."
            )
            return

        source, destination, amount, unit_cost = self.routes[self.route_index]
        self.status_label.config(
            text=f"{self.scenario_name}\nRoute {self.route_index + 1} of {len(self.routes)}\n"
                 f"{source} → {destination}\nUnits: {amount} | Unit cost: {unit_cost} EGP"
        )
        x1, y1 = self.source_positions[source]
        x2, y2 = self.dest_positions[destination]

        self.canvas.create_line(x1 + 30, y1, x2 - 68, y2,
                                fill=AMBER, width=2, dash=(6, 4), tags="route")
        bus_items = self._create_bus(x1 + 45, y1)
        steps = 40
        dx = (x2 - 80 - (x1 + 45)) / steps
        dy = (y2 - y1) / steps

        def move(step=0):
            if token != self.animation_token:
                return
            if step >= steps:
                for item in bus_items:
                    self.canvas.delete(item)
                arrival = self.canvas.create_text(
                    x2, y2 - 20, text=f"+{amount}", fill=GREEN,
                    font=("Segoe UI", 8, "bold"), tags="arrival"
                )
                self.root.after(550, lambda: self.canvas.delete(arrival))
                self.route_index += 1
                self.root.after(180, lambda: self._animate_next_route(token))
                return
            for item in bus_items:
                self.canvas.move(item, dx, dy)
            self.root.after(22, lambda: move(step + 1))
        move()

    def _create_bus(self, x, y):
        return [
            self.canvas.create_rectangle(x - 19, y - 9, x + 19, y + 8,
                                         fill=BLUE, outline=BLUE_DARK, tags="moving"),
            self.canvas.create_rectangle(x + 4, y - 6, x + 14, y,
                                         fill="#bfdbfe", outline=BLUE_DARK, tags="moving"),
            self.canvas.create_rectangle(x - 13, y - 6, x, y,
                                         fill="#bfdbfe", outline=BLUE_DARK, tags="moving"),
            self.canvas.create_oval(x - 13, y + 5, x - 6, y + 12,
                                    fill="#1f2937", outline="white", tags="moving"),
            self.canvas.create_oval(x + 8, y + 5, x + 15, y + 12,
                                    fill="#1f2937", outline="white", tags="moving")
        ]

    def run_all_scenarios(self):
        if self.is_running:
            messagebox.showinfo("Simulation running",
                                "Wait for the current simulation to finish, or press Reset first.")
            return
        self._all_scenarios = list(SCENARIOS.keys())
        self._all_scenario_index = 0
        self.all_button.state(["disabled"])
        self._run_next_scenario()

    def _run_next_scenario(self):
        if self._all_scenario_index >= len(self._all_scenarios):
            self.is_running = False
            self.start_button.state(["!disabled"])
            self.all_button.state(["!disabled"])
            self.live_badge.config(text="● ALL COMPLETE", bg=GREEN_LIGHT, fg=GREEN)
            self.status_label.config(text="All three scenarios completed.")
            self.scenario_description.config(text="All three scenarios have been simulated.")
            return

        name = self._all_scenarios[self._all_scenario_index]
        self.scenario_var.set(name)
        self.scenario_description.config(text=SCENARIOS[name]["description"])
        self._begin_scenario(name)
        token = self.animation_token

        def check_finished():
            if token != self.animation_token:
                return
            if self.is_running:
                self.root.after(200, check_finished)
            else:
                self._all_scenario_index += 1
                self.root.after(500, self._run_next_scenario)
        self.root.after(200, check_finished)

    def reset(self):
        self.animation_token += 1
        self.is_running = False
        self.routes = []
        self.route_index = 0
        self.start_button.state(["!disabled"])
        self.all_button.state(["!disabled"])
        self.live_badge.config(text="● READY", bg=GREEN_LIGHT, fg=GREEN)
        self.status_label.config(text="Ready to start")
        self.result_label.config(text="")
        self._set_metrics("— EGP", "—", "—")
        self.draw_scene()


if __name__ == "__main__":
    root = tk.Tk()
    app = TransportSimulation(root)
    root.mainloop()
