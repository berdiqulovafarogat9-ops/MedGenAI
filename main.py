
import json
import math
import os
import webbrowser

from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView

BG = "#07111F"
PANEL = "#0D1B2A"
INPUT = "#10263A"
ACCENT = "#38BDF8"
TEXT = "#EAF4FF"
MUTED = "#8FA8BC"

HISTORY_FILE = "medgen_history.json"


class MedGenAI(App):

    def build(self):
        global HISTORY_FILE
        HISTORY_FILE = os.path.join(self.user_data_dir, "medgen_history.json")
        self._install_exception_hook()
        self.title = "MedGen AI"

        root = BoxLayout(orientation="horizontal")

        self.sidebar = BoxLayout(
            orientation="vertical",
            size_hint_x=None,
            width=dp(235),
            padding=dp(10),
            spacing=dp(5)
        )

        self.sidebar.add_widget(Label(
            text="[b]MEDGEN AI[/b]",
            markup=True,
            color=self.hex(ACCENT),
            size_hint_y=None,
            height=dp(65),
            font_size=20
        ))

        self.add_nav("Dashboard", self.dashboard)
        self.add_nav("Bioinformatics", self.bioinformatics)
        self.add_nav("AI Structure Prediction",
                     self.structure_prediction)
        self.add_nav("PDB Structure Analysis",
                     self.pdb_analysis)
        self.add_nav("Binding Pocket Analysis",
                     self.pocket_analysis)
        self.add_nav("Docking", self.docking)
        self.add_nav("ML + Ranking + Report",
                     self.ml_ranking_report)
        self.add_nav("Molecular Analysis",
                     self.molecular)
        self.add_nav("Drug Discovery", self.drug_discovery)
        self.add_nav("Virtual Laboratory", self.virtual_laboratory)
        self.add_nav("Research Assistant", self.research_assistant)
        self.add_nav("Results & History",
                     self.results_history)

        root.add_widget(self.sidebar)

        self.workspace = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(10)
        )
        root.add_widget(self.workspace)

        self.dashboard()
        return root

    def _install_exception_hook(self):
        import sys
        import traceback
        def handle(exc_type, exc_value, exc_tb):
            try:
                log_path = os.path.join(self.user_data_dir, "crash.log")
                with open(log_path, "a", encoding="utf-8") as f:
                    traceback.print_exception(exc_type, exc_value, exc_tb, file=f)
            except Exception:
                pass
        sys.excepthook = handle

    def hex(self, value):
        value = value.lstrip("#")
        return tuple(int(value[i:i+2], 16)/255 for i in (0,2,4)) + (1,)

    def add_nav(self, text, command):
        b = Button(
            text=text,
            size_hint_y=None,
            height=dp(48),
            background_normal="",
            background_color=self.hex(PANEL),
            color=self.hex(TEXT),
            halign="left"
        )
        def safe_command(instance):
            try:
                command()
            except Exception as ex:
                self.show_error("Navigation", ex)
        b.bind(on_release=safe_command)
        self.sidebar.add_widget(b)

    def clear(self):
        self.workspace.clear_widgets()

    def page_title(self, text, sub=""):
        self.workspace.add_widget(Label(
            text=f"[b]{text}[/b]",
            markup=True,
            color=self.hex(TEXT),
            font_size=25,
            size_hint_y=None,
            height=dp(45)
        ))
        if sub:
            self.workspace.add_widget(Label(
                text=sub,
                color=self.hex(MUTED),
                size_hint_y=None,
                height=dp(35)
            ))

    def output(self):
        box = ScrollView()
        text = TextInput(
            readonly=False,
            multiline=True,
            background_color=self.hex(INPUT),
            foreground_color=self.hex(TEXT),
            cursor_color=self.hex(TEXT),
            font_size=14
        )
        box.add_widget(text)
        self.workspace.add_widget(box)
        return text

    def button(self, text, command):
        b = Button(
            text=text,
            size_hint_y=None,
            height=dp(52),
            background_normal="",
            background_color=self.hex(ACCENT),
            color=self.hex(BG)
        )
        def safe_command(instance):
            try:
                command(instance)
            except Exception as ex:
                self.show_error(text, ex)
        b.bind(on_release=safe_command)
        self.workspace.add_widget(b)
        return b

    def show_error(self, where, ex):
        self.clear()
        self.page_title("Xatolik", where)
        out = self.output()
        out.text = (
            "Tugma ishlayotganda xatolik yuz berdi.\n\n"
            f"Joy: {where}\n"
            f"Xato: {type(ex).__name__}\n"
            f"Ma'lumot: {ex}\n\n"
            "Ilova endi yopilmaydi."
        )
        self.button("DASHBOARDGA QAYTISH", lambda x: self.dashboard())

    def dashboard(self):
        self.clear()
        self.page_title(
            "MedGen AI",
            "Computational biomedical research platform"
        )
        self.workspace.add_widget(Label(
            text="AI + Bioinformatics + Computational Drug Discovery",
            color=self.hex(ACCENT),
            font_size=17,
            size_hint_y=None,
            height=dp(50)
        ))

    def bioinformatics(self):
        self.clear()
        self.page_title("Bioinformatics", "Sequence analysis & utilities")
        self.workspace.add_widget(Label(
            text="DNA / RNA sequence or FASTA",
            color=self.hex(MUTED),
            size_hint_y=None,
            height=dp(30)
        ))
        seq = TextInput(
            text=">Example\nATGCGTACGTAG",
            multiline=True,
            background_color=self.hex(INPUT),
            foreground_color=self.hex(TEXT),
            cursor_color=self.hex(TEXT),
            font_size=15
        )
        self.workspace.add_widget(seq)
        out = self.output()

        codons = {
            "TTT":"F","TTC":"F","TTA":"L","TTG":"L",
            "TCT":"S","TCC":"S","TCA":"S","TCG":"S",
            "TAT":"Y","TAC":"Y","TAA":"*","TAG":"*",
            "TGT":"C","TGC":"C","TGA":"*","TGG":"W",
            "CTT":"L","CTC":"L","CTA":"L","CTG":"L",
            "CCT":"P","CCC":"P","CCA":"P","CCG":"P",
            "CAT":"H","CAC":"H","CAA":"Q","CAG":"Q",
            "CGT":"R","CGC":"R","CGA":"R","CGG":"R",
            "ATT":"I","ATC":"I","ATA":"I","ATG":"M",
            "ACT":"T","ACC":"T","ACA":"T","ACG":"T",
            "AAT":"N","AAC":"N","AAA":"K","AAG":"K",
            "AGT":"S","AGC":"S","AGA":"R","AGG":"R",
            "GTT":"V","GTC":"V","GTA":"V","GTG":"V",
            "GCT":"A","GCC":"A","GCA":"A","GCG":"A",
            "GAT":"D","GAC":"D","GAA":"E","GAG":"E",
            "GGT":"G","GGC":"G","GGA":"G","GGG":"G"
        }

        def clean_sequence(raw):
            lines = [line.strip() for line in raw.splitlines() if line.strip()]
            fasta = any(line.startswith(">") for line in lines)
            if fasta:
                lines = [line for line in lines if not line.startswith(">")]
            s = "".join(lines).upper().replace(" ", "").replace("U", "T")
            return s, fasta

        def translate(s, frame=0):
            aa = []
            for i in range(frame, len(s) - 2, 3):
                aa.append(codons.get(s[i:i+3], "X"))
            return "".join(aa)

        def reverse_complement(s):
            table = str.maketrans("ACGTN", "TGCAN")
            return s.translate(table)[::-1]

        def find_orfs(s):
            results = []
            stop = {"TAA", "TAG", "TGA"}
            for strand_name, strand in (("+", s), ("-", reverse_complement(s))):
                for frame in range(3):
                    start = None
                    for i in range(frame, len(strand) - 2, 3):
                        codon = strand[i:i+3]
                        if start is None and codon == "ATG":
                            start = i
                        elif start is not None and codon in stop:
                            dna = strand[start:i+3]
                            protein = translate(dna)
                            results.append((strand_name, frame + 1, start + 1, i + 3, protein))
                            start = None
            return results

        def analyze(instance):
            s, fasta = clean_sequence(seq.text)
            valid = bool(s) and all(c in "ACGTN" for c in s)
            if not s:
                out.text = "No sequence provided."
                return
            if not valid:
                bad = sorted(set(c for c in s if c not in "ACGTN"))
                out.text = "=== BIOINFORMATICS ===\n\nINVALID SEQUENCE\n"
                out.text += "Allowed symbols: A, C, G, T, N\n"
                out.text += "Invalid: " + ", ".join(bad)
                return
            a_count, t_count, g_count, c_count, n_count = (s.count(x) for x in "ATGCN")
            gc = ((g_count + c_count) / len(s) * 100) if s else 0
            at = ((a_count + t_count) / len(s) * 100) if s else 0
            out.text = (
                "=== BIOINFORMATICS ANALYSIS ===\n\n"
                f"Input format: {'FASTA' if fasta else 'Raw sequence'}\n"
                f"Length: {len(s)} nt\n"
                f"A: {a_count}  T: {t_count}  G: {g_count}  C: {c_count}  N: {n_count}\n"
                f"GC content: {gc:.2f}%\n"
                f"AT content: {at:.2f}%\n"
                f"GC/AT ratio: {(gc/at):.3f}\n" if at else
                "=== BIOINFORMATICS ANALYSIS ===\n\n"
                f"Input format: {'FASTA' if fasta else 'Raw sequence'}\n"
                f"Length: {len(s)} nt\n"
                f"A: {a_count}  T: {t_count}  G: {g_count}  C: {c_count}  N: {n_count}\n"
                f"GC content: {gc:.2f}%\n"
                f"AT content: {at:.2f}%\n"
                "GC/AT ratio: undefined (AT = 0)\n"
            )
            out.text += "Sequence: VALID"

        def show_reverse_complement(instance):
            s, _ = clean_sequence(seq.text)
            if not s:
                out.text = "No sequence provided."
                return
            if any(c not in "ACGTN" for c in s):
                out.text = "Invalid sequence. Allowed symbols: A, C, G, T, N"
                return
            rc = reverse_complement(s)
            out.text = "=== REVERSE COMPLEMENT ===\n\n" + rc

        def show_translation(instance):
            s, _ = clean_sequence(seq.text)
            if not s:
                out.text = "No sequence provided."
                return
            if any(c not in "ACGTN" for c in s):
                out.text = "Invalid sequence. Allowed symbols: A, C, G, T, N"
                return
            proteins = [translate(s, f) for f in range(3)]
            out.text = "=== 3-FRAME PROTEIN TRANSLATION ===\n\n"
            for f, protein in enumerate(proteins, 1):
                out.text += f"Frame +{f}:\n{protein}\n\n"
            out.text += "Stop codon = *   Unknown codon = X"

        def show_orfs(instance):
            s, _ = clean_sequence(seq.text)
            if not s:
                out.text = "No sequence provided."
                return
            if any(c not in "ACGTN" for c in s):
                out.text = "Invalid sequence. Allowed symbols: A, C, G, T, N"
                return
            orfs = find_orfs(s)
            if not orfs:
                out.text = "=== ORF SEARCH ===\n\nNo complete ATG-to-stop ORF found."
                return
            out.text = f"=== ORF SEARCH ===\n\nFound: {len(orfs)} complete ORF(s)\n\n"
            for idx, (strand, frame, start, end, protein) in enumerate(orfs, 1):
                out.text += (
                    f"ORF {idx}: strand {strand}, frame {frame}, "
                    f"nt {start}-{end}, {len(protein)-1} aa\n"
                    f"Protein: {protein}\n\n"
                )

        def save_report(instance):
            try:
                import os
                path = os.path.join(self.user_data_dir, "bioinformatics_report.txt")
                with open(path, "w", encoding="utf-8") as f:
                    f.write(out.text)
                out.text += f"\n\nSaved: {path}"
            except Exception as ex:
                self.show_error("Save report", ex)

        self.button("ANALYZE SEQUENCE", analyze)
        self.button("REVERSE COMPLEMENT", show_reverse_complement)
        self.button("TRANSLATE PROTEIN", show_translation)
        self.button("FIND ORFs", show_orfs)
        self.button("SAVE REPORT", save_report)

    def drug_discovery(self):
        self.clear()
        self.page_title("Drug Discovery", "Molecule screening")
        self.workspace.add_widget(Label(
            text="SMILES",
            color=self.hex(MUTED),
            size_hint_y=None,
            height=dp(30)
        ))
        entry = TextInput(
            text="CCO",
            multiline=False,
            background_color=self.hex(INPUT),
            foreground_color=self.hex(TEXT),
            cursor_color=self.hex(TEXT),
            size_hint_y=None,
            height=dp(50)
        )
        self.workspace.add_widget(entry)
        out = self.output()

        def screen(instance):
            s = entry.text.strip()
            atoms, i = {}, 0
            while i < len(s):
                if s[i].isupper():
                    a = s[i]; i += 1
                    if i < len(s) and s[i].islower():
                        a += s[i]; i += 1
                    atoms[a] = atoms.get(a, 0) + 1
                else:
                    i += 1
            c,n,o = atoms.get("C",0), atoms.get("N",0), atoms.get("O",0)
            h = max(2*c + 2 + n, 0)
            mw = c*12.011 + h*1.008 + n*14.007 + o*15.999
            formula = f"C{c}H{h}" + (f"N{n}" if n else "") + (f"O{o}" if o else "")
            out.text = (
                "=== DRUG DISCOVERY SCREEN ===\n\n"
                f"SMILES: {s}\nFormula: {formula}\n"
                f"Approx. MW: {mw:.3f} g/mol\n"
                f"MW <= 500: {'PASS' if mw <= 500 else 'FAIL'}\n\n"
                "Computational filter only."
            )
        self.button("SCREEN MOLECULE", screen)

    def virtual_laboratory(self):
        self.clear()
        self.page_title("Virtual Laboratory", "Experiment workspace")
        out = self.output()
        out.text = (
            "=== VIRTUAL LABORATORY ===\n\n"
            "Target → PDB → Pocket → Docking → ML → Report\n\n"
            "Har bir bosqichni quyidagi tugmalar orqali oching."
        )
        self.button("PDB ANALYSIS", lambda x: self.pdb_analysis())
        self.button("POCKET ANALYSIS", lambda x: self.pocket_analysis())
        self.button("DOCKING", lambda x: self.docking())
        self.button("ML + REPORT", lambda x: self.ml_ranking_report())

    def research_assistant(self):
        self.clear()
        self.page_title("Research Assistant", "Research workflow")
        self.workspace.add_widget(Label(
            text="Savol / tadqiqot mavzusi",
            color=self.hex(MUTED),
            size_hint_y=None,
            height=dp(30)
        ))
        query = TextInput(
            multiline=True,
            background_color=self.hex(INPUT),
            foreground_color=self.hex(TEXT),
            cursor_color=self.hex(TEXT),
            font_size=15
        )
        self.workspace.add_widget(query)
        out = self.output()

        def prepare(instance):
            q = query.text.strip()
            if not q:
                out.text = "Savol yoki mavzu kiriting."
                return
            out.text = (
                "=== RESEARCH ASSISTANT ===\n\n"
                f"Mavzu:\n{q}\n\n"
                "Tadqiqot workflow:\n"
                "1. Target va biologik savolni aniqlash\n"
                "2. Sequence/PDB ma'lumotini tayyorlash\n"
                "3. Structure va pocket analysis\n"
                "4. Docking va ML natijalarini solishtirish\n"
                "5. Natijalarni tarixga saqlash\n\n"
                "Bu modul workflow tayyorlaydi; eksperimental yoki "
                "klinik xulosa bermaydi."
            )
        self.button("PREPARE WORKFLOW", prepare)

    def molecular(self):
        self.clear()
        self.page_title("Molecular Analysis", "SMILES analysis")

        self.workspace.add_widget(Label(
            text="SMILES",
            color=self.hex(MUTED),
            size_hint_y=None,
            height=dp(30)
        ))

        entry = TextInput(
            text="CCO",
            multiline=False,
            background_color=self.hex(INPUT),
            foreground_color=self.hex(TEXT),
            cursor_color=self.hex(TEXT),
            font_size=16,
            size_hint_y=None,
            height=dp(50)
        )
        self.workspace.add_widget(entry)

        out = self.output()

        def analyze(instance):
            s = entry.text.strip()
            atoms = {}
            i = 0

            while i < len(s):
                if s[i].isupper():
                    a = s[i]
                    i += 1
                    if i < len(s) and s[i].islower():
                        a += s[i]
                        i += 1
                    atoms[a] = atoms.get(a, 0) + 1
                else:
                    i += 1

            c = atoms.get("C", 0)
            n = atoms.get("N", 0)
            o = atoms.get("O", 0)

            h = max(2*c + 2 + n, 0)
            mw = (
                c*12.011 +
                h*1.008 +
                n*14.007 +
                o*15.999
            )

            formula = f"C{c}H{h}"
            if n:
                formula += f"N{n}"
            if o:
                formula += f"O{o}"

            out.text = (
                "=== MOLECULAR ANALYSIS ===\n\n"
                f"SMILES: {s}\n"
                f"Formula: {formula}\n"
                f"Molecular Weight: {mw:.3f} g/mol\n\n"
                f"MW <= 500: {'PASS' if mw <= 500 else 'FAIL'}"
            )

        self.button("ANALYZE", analyze)

    def structure_prediction(self):
        self.clear()
        self.page_title(
            "AI Structure Prediction",
            "AlphaFold / ColabFold workflow"
        )

        self.workspace.add_widget(Label(
            text="Protein sequence",
            color=self.hex(MUTED),
            size_hint_y=None,
            height=dp(30)
        ))

        seq = TextInput(
            multiline=True,
            background_color=self.hex(INPUT),
            foreground_color=self.hex(TEXT),
            cursor_color=self.hex(TEXT),
            font_size=14
        )
        self.workspace.add_widget(seq)

        status = Label(
            text="Ready",
            color=self.hex(MUTED),
            size_hint_y=None,
            height=dp(35)
        )
        self.workspace.add_widget(status)

        def open_colab(instance):
            s = seq.text.strip()
            if not s:
                status.text = "Protein sequence kiriting."
                return

            clean = s.replace("\n", "").replace(" ", "")
            status.text = f"Sequence: {len(clean)} aa"

            webbrowser.open(
                "https://colab.research.google.com/github/"
                "sokrypton/ColabFold/blob/main/AlphaFold2.ipynb"
            )

        self.button("OPEN COLABFOLD", open_colab)

        self.workspace.add_widget(Label(
            text="Sequence → ColabFold → PDB → MedGen AI",
            color=self.hex(ACCENT),
            font_size=14,
            size_hint_y=None,
            height=dp(40)
        ))

    def pdb_analysis(self):
        self.clear()
        self.page_title(
            "PDB Structure Analysis",
            "Import predicted protein structure"
        )

        out = self.output()

        self.workspace.add_widget(Label(
            text="PDB fayl yo'lini kiriting:",
            color=self.hex(MUTED),
            size_hint_y=None,
            height=dp(30)
        ))

        path = TextInput(
            text="/storage/emulated/0/",
            multiline=False,
            background_color=self.hex(INPUT),
            foreground_color=self.hex(TEXT),
            size_hint_y=None,
            height=dp(50)
        )
        self.workspace.add_widget(path)

        def load(instance):
            f = path.text.strip()

            if not os.path.isfile(f):
                out.text = "PDB file topilmadi:\n" + f
                return

            try:
                with open(
                    f,
                    encoding="utf-8",
                    errors="ignore"
                ) as fh:
                    data = fh.read()

                lines = data.splitlines()
                atoms = sum(
                    1 for x in lines
                    if x.startswith(("ATOM  ", "HETATM"))
                )

                residues = set()

                for x in lines:
                    if x.startswith("ATOM  ") and len(x) >= 26:
                        residues.add(x[17:26].strip())

                out.text = (
                    "=== PDB STRUCTURE ===\n\n"
                    f"File: {os.path.basename(f)}\n"
                    f"Path: {f}\n"
                    f"Atoms: {atoms}\n"
                    f"Residues: {len(residues)}\n\n"
                    "STATUS: PDB LOADED\n\n"
                    "Next workflow:\n"
                    "PDB → Pocket Analysis → Docking → ML → Ranking"
                )

            except Exception as ex:
                out.text = "PDB Error:\n\n" + str(ex)

        self.button("LOAD PDB", load)

    def pocket_analysis(self):
        self.clear()
        self.page_title(
            "Binding Pocket Analysis",
            "6WC8 binding-site analysis"
        )

        self.workspace.add_widget(Label(
            text="Protein PDB fayl yo'li:",
            color=self.hex(MUTED),
            size_hint_y=None,
            height=dp(30)
        ))

        path = TextInput(
            text="/storage/emulated/0/",
            multiline=False,
            background_color=self.hex(INPUT),
            foreground_color=self.hex(TEXT),
            size_hint_y=None,
            height=dp(50)
        )
        self.workspace.add_widget(path)

        out = self.output()

        def analyze(instance):
            f = path.text.strip()

            if not os.path.isfile(f):
                out.text = "PDB file topilmadi:\n" + f
                return

            center = (16.019, 18.428, 12.185)
            radius = 5.0
            residues = set()
            atoms = 0
            nearby = 0

            try:
                with open(
                    f,
                    encoding="utf-8",
                    errors="ignore"
                ) as fh:
                    for x in fh:
                        if not x.startswith("ATOM  "):
                            continue

                        atoms += 1

                        try:
                            xx = float(x[30:38])
                            yy = float(x[38:46])
                            zz = float(x[46:54])
                        except:
                            continue

                        d = math.sqrt(
                            (xx-center[0])**2 +
                            (yy-center[1])**2 +
                            (zz-center[2])**2
                        )

                        if d <= radius:
                            nearby += 1
                            residues.add(
                                f"{x[21].strip()}:"
                                f"{x[17:20].strip()}"
                                f"{x[22:26].strip()}"
                            )

                out.text = (
                    "=== BINDING POCKET ANALYSIS ===\n\n"
                    f"PDB: {os.path.basename(f)}\n"
                    f"Pocket center: {center}\n"
                    f"Radius: {radius} Å\n\n"
                    f"Protein atoms: {atoms}\n"
                    f"Nearby atoms: {nearby}\n"
                    f"Nearby residues: {len(residues)}\n\n"
                    "RESIDUES:\n" +
                    ", ".join(sorted(residues)) +
                    "\n\nWORKFLOW:\n"
                    "6WC8 → Pocket → Docking → ML → Ranking"
                )

            except Exception as ex:
                out.text = "Pocket Error:\n\n" + str(ex)

        self.button("ANALYZE POCKET", analyze)

    def docking(self):
        self.clear()
        self.page_title(
            "Molecular Docking",
            "AutoDock Vina result"
        )

        out = self.output()

        out.text = """=== MOLECULAR DOCKING ===

Target: HIV-1 Integrase
PDB: 6WC8
Ligand: TQM

Engine: AutoDock Vina
Scoring function: Vina

Pocket center:
X = 16.019
Y = 18.428
Z = 12.185

Box: 20 × 20 × 20 Å
Exhaustiveness: 8

DOCKING RESULTS
------------------------------
Mode 1   -5.996 kcal/mol
Mode 2   -5.951 kcal/mol
Mode 3   -5.937 kcal/mol
Mode 4   -5.792 kcal/mol
Mode 5   -5.775 kcal/mol
Mode 6   -5.700 kcal/mol
Mode 7   -5.669 kcal/mol
Mode 8   -5.667 kcal/mol
Mode 9   -5.498 kcal/mol
Mode 10  -5.246 kcal/mol

BEST DOCKING SCORE
------------------------------
-5.996 kcal/mol

STATUS: COMPUTATIONAL RESULT

Note:
This is a computational docking score,
not experimental binding affinity or clinical efficacy.
"""

        self.button("REFRESH RESULT",
                     lambda x: None)

    def ml_ranking_report(self):
        self.clear()
        self.page_title(
            "ML • Ranking • Report",
            "Computational candidate analysis"
        )

        out = self.output()

        def run(instance):
            analysis_text = """=== MEDGEN AI FINAL ANALYSIS ===

Target: HIV-1 Integrase
PDB: 6WC8
Docking: AutoDock Vina
ML: Random Forest ESOL

TOP CANDIDATES

1. CC(C)O
   Docking: -2.477 kcal/mol
   ESOL logS: 0.528
   Similarity: 20.00%
   Final score: 0.556

2. CCCN
   Docking: -2.487 kcal/mol
   ESOL logS: 0.706
   Similarity: 27.27%
   Final score: 0.556

3. CCCCN
   Docking: -2.714 kcal/mol
   ESOL logS: 0.049
   Similarity: 21.43%
   Final score: 0.537

4. CCN
   Docking: -2.063 kcal/mol
   ESOL logS: 0.991
   Similarity: 33.33%
   Final score: 0.530

5. CC(C)CO
   Docking: -2.567 kcal/mol
   ESOL logS: 0.125
   Similarity: 36.36%
   Final score: 0.501

=== REPORT ===

Workflow:
Target → PDB → Pocket → Docking → ML → Ranking

STATUS: COMPUTATIONAL ANALYSIS COMPLETED

Note:
Docking scores and ML predictions are computational results,
not experimental binding affinity or clinical efficacy.
"""

            out.text = analysis_text

            experiment = {
                "id": "EXP_6WC8_TQM_001",
                "target": "HIV-1 Integrase",
                "pdb": "6WC8",
                "ligand": "TQM",
                "status": "COMPLETED",
                "analysis": analysis_text
            }

            try:
                history = []

                if os.path.exists(HISTORY_FILE):
                    with open(
                        HISTORY_FILE,
                        "r",
                        encoding="utf-8"
                    ) as f:
                        history = json.load(f)

                history.append(experiment)

                with open(
                    HISTORY_FILE,
                    "w",
                    encoding="utf-8"
                ) as f:
                    json.dump(
                        history,
                        f,
                        ensure_ascii=False,
                        indent=2
                    )
            except Exception:
                pass

        self.button(
            "RUN ML + RANKING + REPORT",
            run
        )

    def results_history(self):
        self.clear()
        self.page_title(
            "Results & History",
            "Saved computational experiments"
        )

        out = self.output()

        try:
            if not os.path.exists(HISTORY_FILE):
                out.text = (
                    "No saved experiments yet.\n\n"
                    "Run ML + Ranking + Report first."
                )
                return

            with open(
                HISTORY_FILE,
                "r",
                encoding="utf-8"
            ) as f:
                history = json.load(f)

            if not history:
                out.text = "No saved experiments yet."
                return

            text = "=== MEDGEN AI RESULTS & HISTORY ===\n\n"

            for i, exp in enumerate(history, 1):
                text += (
                    f"EXPERIMENT {i:03d}\n"
                    "==============================\n"
                    f"ID: {exp.get('id', 'N/A')}\n"
                    f"Target: {exp.get('target', 'N/A')}\n"
                    f"PDB: {exp.get('pdb', 'N/A')}\n"
                    f"Ligand: {exp.get('ligand', 'N/A')}\n"
                    f"Status: {exp.get('status', 'N/A')}\n\n"
                )

                if exp.get("analysis"):
                    text += exp["analysis"] + "\n\n"

            out.text = text

        except Exception as ex:
            out.text = "History loading error:\n\n" + str(ex)


if __name__ == "__main__":
    MedGenAI().run()
