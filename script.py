import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from PyQt5.QtCore import Qt
from pygam import LinearGAM, s
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QComboBox, QCheckBox,
    QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QSpinBox, QTextEdit
)
from PyQt5.QtGui import QIcon

def run(output, gf_list, treat, factor, k_value):
    df = None
    graph_text = None
    factor_unit = None
    output_unit = None
    treat_name = None
    graph_gf_text = None

    if treat == "cntrl":
        treat_name = ""
    elif treat == "cold":
        treat_name = "(Cold)"

    if output == "GermP_Ort":
        df = pd.read_excel("germination_data.xlsx")
        graph_text = "Germination"
        output_unit = "%"
    elif output == "DormP_Ort":
        df = pd.read_excel("germination_data.xlsx")
        graph_text = "Dormancy"
        output_unit = "%"
    elif output == "GermP_Ort_diff":
        df = pd.read_excel("germination_data_treat_diff.xlsx")
        graph_text = "Difference"
        output_unit = "cold - control"
    elif output == "Viability":
        df = pd.read_excel("germination_data.xlsx")
        graph_text = "Viability"
        output_unit = "%"
    elif output == "Mass_Ort":
        df = pd.read_excel("mass_data.xlsx")
        graph_text = "Mass"
        treat_name = ""
        output_unit = "g"
    elif output == "Length_Ort":
        df = pd.read_excel("length_data.xlsx")
        graph_text = "Length"
        output_unit = "mm"
    elif output == "Shape_Ort":
        df = pd.read_excel("length_data.xlsx")
        graph_text = "Shape"
        output_unit = ""

    if factor == "Altitude":
        factor_unit = "m"
    elif factor == "Productivity":
        factor_unit = "g C/m^2/year"

    gf_mapping = {
        "ANN": "Annual",
        "BIE": "Biennial",
        "WOO": "Woody",
        "PER": "Perennial",
        "VAR": "Variation",
    }

    if "ALL" in gf_list:
        graph_gf_text = "All"
    else:
        graph_gf_text = ", ".join(gf_mapping[v] for v in gf_list if v in gf_mapping)

    if output == "GermP_Ort" or output == "DormP_Ort" or output == "Viability":
        d = df[(df['treat'] == treat) & (df['rep'] == 1)].copy()
    else:
        d = df.copy()
        d = d[d['rep'] == 1]

    # SUB olanları WOO yap
    d['GF'] = d['GF'].replace('SUB', 'WOO')

    if "ALL" in gf_list:
        d['GF'] = 'ALL'
    else:
        d = d[d['GF'].isin(gf_list)]

    productivity_df = d.groupby('site')[f'{factor}'].first().reset_index()
    cwm_df = d.groupby(['site', 'GF']).apply(
        lambda g: (g[f'{output}'] * g['abundance']).sum() / g['abundance'].sum()).reset_index(name='CWM')
    cwm_df = cwm_df.merge(productivity_df, on='site')

    fig, ax = plt.subplots(figsize=(16, 7))
    # Mavi-pembe palet (tek yıllık -> mavi, çok yıllık -> pembe).
    # İkiden fazla tip seçilirse renkler dönüşümlü kullanılır.
    palette = ["#2E75B6", "#E07BB0"]
    colors = [palette[i % len(palette)] for i in range(len(gf_list))]

    for i, gf in enumerate(gf_list):
        gf_data = cwm_df[cwm_df['GF'] == gf]

        x_vals = gf_data[f'{factor}'].values

        y_vals = gf_data['CWM'].values

        ax.scatter(x_vals, y_vals, label=gf, color=colors[i], s=100, edgecolor='k')

        if len(x_vals) > 3:
            X = x_vals.reshape(-1, 1)

            gam = LinearGAM(s(0, n_splines=k_value)).fit(X, y_vals)

            XX = np.linspace(X.min(), X.max(), 200)
            XX = XX.reshape(-1, 1)

            preds = gam.predict(XX)
            conf = gam.confidence_intervals(XX, width=0.95)

            ax.plot(XX, preds, color=colors[i], linewidth=2)

            ax.fill_between(XX.flatten(), conf[:, 0], conf[:, 1], color=colors[i], alpha=0.2)

            edf = gam.statistics_['edof']
            pval = gam.statistics_['p_values'][1]
            if pval < 0.001:
                p_text = "p < 0.001"
            else:
                p_text = f"p = {pval:.3f}"

            ax.text(0.02, 0.95 - 0.06 * i, f"k={k_value}, edf={edf:.2f}, {p_text}",
                    color=colors[i], fontsize=12, transform=ax.transAxes,
                    verticalalignment='top')

        else:
            ax.text(0.02, 0.95 - 0.06 * i, "Not enough data for GAM",
                    color=colors[i], fontsize=12, transform=ax.transAxes,
                    verticalalignment='top')

    ax.set_xlabel(f'Site {factor} ({factor_unit})', fontsize=14, fontweight='bold')
    ax.set_ylabel(f'{graph_text} CWM ({output_unit})', fontsize=14, fontweight='bold')
    # ax.set_title(f'{graph_text} CWM by {factor} for {graph_gf_text} Plants {treat_name}', fontsize=16, fontweight='bold')
    # Lejant yalnızca birden fazla tip gösterilirken görünsün
    if len(gf_list) > 1:
        ax.legend(title='GF')
    ax.grid(axis='y', linestyle='--', alpha=0.6)

    plt.tight_layout()

    safe_gf = graph_gf_text.replace(", ", "_")
    filename = f"{graph_text}_{factor}_{safe_gf}_{treat}_k{k_value}.png"
    plt.savefig(f"{output_path}/{filename}", dpi=600, bbox_inches="tight")

    plt.show()


class MiniGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SeedScope v2.0 💚")
        self.setWindowIcon(QIcon("sprout.png"))
        self.setFixedSize(400, 400)

        layout = QVBoxLayout()

        # OUTPUT
        layout.addWidget(QLabel("Output"))
        self.output_box = QComboBox()
        self.output_box.addItems([
            "GermP_Ort", "DormP_Ort", "Viability",
            "Mass_Ort", "Length_Ort", "Shape_Ort", "GermP_Ort_diff"
        ])
        self.output_box.currentIndexChanged.connect(self.output_changed)
        layout.addWidget(self.output_box)

        # GF CHECKBOX
        layout.addWidget(QLabel("GF"))
        gf_layout = QHBoxLayout()

        self.gf_boxes = {}
        for gf in ["ANN", "BIE", "PER", "VAR", "WOO", "ALL"]:
            cb = QCheckBox(gf)
            self.gf_boxes[gf] = cb
            gf_layout.addWidget(cb)

            # ALL checkbox için sinyal
            if gf == "ALL":
                cb.stateChanged.connect(self.all_checked_changed)

        layout.addLayout(gf_layout)

        # TREAT
        self.label_treat = QLabel("Treat")
        layout.addWidget(self.label_treat)
        self.treat_box = QComboBox()
        self.treat_box.addItems(["cntrl","cold"])
        layout.addWidget(self.treat_box)

        # FACTOR
        layout.addWidget(QLabel("Factor"))
        self.factor_box = QComboBox()
        self.factor_box.addItems(["Altitude","Productivity"])
        layout.addWidget(self.factor_box)

        # K VALUE
        layout.addWidget(QLabel("k value"))
        self.k_spin = QSpinBox()
        self.k_spin.setRange(5,40)
        self.k_spin.setValue(20)
        layout.addWidget(self.k_spin)

        # PATH
        self.path_btn = QPushButton("Select Output Path (Desktop by default)")
        self.path_btn.clicked.connect(self.select_path)
        layout.addWidget(self.path_btn)

        # RUN
        self.run_btn = QPushButton("Run")
        self.run_btn.clicked.connect(self.execute)
        layout.addWidget(self.run_btn)

        # PANEL
        self.notification_panel = QTextEdit()
        self.notification_panel.setReadOnly(True)
        self.notification_panel.setFixedHeight(80)  # panel boyutu
        # layout.addWidget(self.notification_panel)

        self.setLayout(layout)

        self.output_path = os.path.join(os.path.expanduser("~"), "Desktop")

    def select_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if path:
            self.output_path = path

    def all_checked_changed(self, state):
        all_checked = self.gf_boxes["ALL"].isChecked()
        for gf, cb in self.gf_boxes.items():
            if gf != "ALL":
                cb.setDisabled(all_checked)
                cb.setChecked(False)

    def output_changed(self, index):
        output = self.output_box.currentText()
        if output in ["GermP_Ort", "DormP_Ort", "Viability"]:
            self.treat_box.show()
            self.label_treat.show()
        else:
            self.treat_box.hide()
            self.label_treat.hide()

    def notify(self, msg, error=False):
        if error:
            self.notification_panel.setTextColor(Qt.red)
        else:
            self.notification_panel.setTextColor(Qt.darkGreen)
        self.notification_panel.append(msg)

    def execute(self):
        global output_path

        output = self.output_box.currentText()
        treat = self.treat_box.currentText()
        factor = self.factor_box.currentText()
        k_value = self.k_spin.value()

        gf_list = [gf for gf, cb in self.gf_boxes.items() if cb.isChecked()]

        if not gf_list:
            self.notify("Select at least one GF", error=True)
            return

        output_path = self.output_path

        try:
            run(output, gf_list, treat, factor, k_value)
            self.notify("Grafik başarıyla oluşturuldu!", error=False)
        except Exception as e:
            self.notify(f"Hata oluştu: {e}", error=True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MiniGUI()
    window.show()
    sys.exit(app.exec_())

#######################################################################################################################

# output    : "GermP_Ort", "DormP_Ort, "Viability", "Mass_Ort", "Length_Ort", "Shape_Ort"
# gf        : "ANN", "BIE", "PER", "VAR", "WOO"    -   "ALL" for all types together
# treat     : "cntrl", "cold"
# factor    : "Altitude", "Productivity"
# k value   : GAM spline number (5, 10, ...)

# treat value is not used in mass, length and shape calculations. it can be entered anything.

#_output = "Shape_Ort"
#_gf_list = ['WOO']
#_treat = "cntrl"
#_factor = "Productivity"
#_k_value = 20
#output_path = "C:/Users/Asus/Desktop/yazılım/mırna_tez/yepyepyepyepyeni_graphs"

#run(_output, _gf_list, _treat, _factor, _k_value)

# todo hiçbir gf seçili değilse run disable
# excel dosyalarını da exeye dahil et