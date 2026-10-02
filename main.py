
import json
import math
import os
import webbrowser
import threading
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

from kivy.clock import Clock

from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line

BG = "#07111F"
PANEL = "#0D1B2A"
INPUT = "#10263A"
ACCENT = "#38BDF8"
TEXT = "#EAF4FF"
MUTED = "#8FA8BC"

HISTORY_FILE = "medgen_history.json"


class Molecule3DView(Widget):
    def __init__(self, atoms=None, **kwargs):
        super().__init__(**kwargs)
        self.atoms = atoms or []
        self.yaw = 0.45
        self.pitch = 0.25
        self.scale = 6.0
        self.last_touch = None
        self.bind(pos=lambda *_: self.redraw(), size=lambda *_: self.redraw())
        self.redraw()

    def set_atoms(self, atoms):
        self.atoms = atoms or []
        self.redraw()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.last_touch = touch.pos
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.last_touch is not None:
            dx = touch.x - self.last_touch[0]
            dy = touch.y - self.last_touch[1]
            self.yaw += dx * 0.01
            self.pitch += dy * 0.008
            self.last_touch = touch.pos
            self.redraw()
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        self.last_touch = None
        return super().on_touch_up(touch)

    def _project(self, x, y, z):
        import math
        cy, sy = math.cos(self.yaw), math.sin(self.yaw)
        cp, sp = math.cos(self.pitch), math.sin(self.pitch)
        x1 = x * cy - z * sy
        z1 = x * sy + z * cy
        y1 = y * cp - z1 * sp
        z2 = y * sp + z1 * cp
        px = self.center_x + x1 * self.scale
        py = self.center_y + y1 * self.scale
        return px, py, z2

    def redraw(self):
        self.canvas.clear()
        if not self.atoms:
            return
        pts=[]
        for a in self.atoms:
            try:
                pts.append((*self._project(a[0],a[1],a[2]), a[3] if len(a)>3 else 'C'))
            except Exception:
                pass
        if not pts: return
        # bonds: connect sequential backbone/atoms for a readable molecular path
        Color(0.25,0.75,0.95,0.75)
        for i in range(len(pts)-1):
            x1,y1,_=pts[i]; x2,y2,_=pts[i+1]
            Line(points=[x1,y1,x2,y2], width=1.2)
        # atoms, depth sorted
        for x,y,z,elem in sorted(pts,key=lambda t:t[2]):
            r=max(3.0, min(10.0, 7.0/(1+0.015*max(-z,0))))
            Color(0.2,0.85,1,0.9) if elem=='C' else Color(1,0.45,0.35,0.95)
            Ellipse(pos=(x-r,y-r), size=(2*r,2*r))


class MedGenAI(App):
    def build(self):
        global HISTORY_FILE

            # 1. App storage
            HISTORY_FILE = os.path.join(
                self.user_data_dir,
                "medgen_history.json"
            )

            # 2. Basic app settings
            self.title = "MedGen AI"
            self.language = "uz"

            # 3. Create root UI
            root = BoxLayout(
                orientation="vertical",
                spacing=dp(8),
                padding=dp(8)
            )

            # 4. Header
            header = BoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(55),
                spacing=dp(6)
            )

            title = Label(
                text="MEDGEN AI",
                font_size=22,
                bold=True,
                halign="left",
                valign="middle"
            )

            header.add_widget(title)

            root.add_widget(header)

            # 5. Workspace
            self.workspace = BoxLayout(
                orientation="vertical",
                spacing=dp(8)
            )

            root.add_widget(self.workspace)

            # 6. Dashboard
        self.dashboard()

        Clock.schedule_once(
            lambda *_: self.refresh_news(),
            0.5
        )

        Clock.schedule_interval(
            lambda *_: self.refresh_news(),
            3600
        )

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


    LANG = {
        "uz": {
            "home":"Bosh sahifa","news":"So‘nggi yangiliklar","modules":"Modullar","saved":"Saqlanganlar","collections":"Kolleksiyalar","settings":"Sozlamalar","language":"Til","search":"Kasallik, gen, protein, dori, PDB yoki maqola...","search_title":"Ilmiy qidiruv","latest":"So‘nggi biomedical yangiliklar","open":"Ochish","close":"Yopish","back":"Bosh sahifaga qaytish","refresh":"Yangilash","open_source":"Manbani ochish","no_results":"Natija topilmadi","loading":"Ma’lumot yuklanmoqda...","virtual":"Virtual Laboratory","viewer2d":"2D ko‘rinish","viewer3d":"3D molekulyar ko‘rish","load_pdb":"PDB yuklash","demo":"Demo model","pdb_path":"PDB fayl yo‘li","news_source":"Manba","global":"Global biomedical research portal","bioinformatics":"Bioinformatics","drug_discovery":"Drug Discovery","structure_prediction":"Structure Prediction","pdb_analysis":"PDB Analysis","binding_pocket":"Binding Pocket","docking":"Docking","ml_ranking":"ML + Ranking","research_assistant":"Research Assistant","results_history":"Results & History","analyze":"Tahlil qilish","analyze_sequence":"Ketma-ketlikni tahlil qilish","analyze_pocket":"Pocketni tahlil qilish","clear":"Tozalash","copy_sequence":"Ketma-ketlikni nusxalash","find_orfs":"ORF topish","load_pdb":"PDB yuklash","prepare_workflow":"Workflow tayyorlash","refresh_result":"Natijani yangilash","reverse_complement":"Reverse Complement","save_fasta":"FASTA saqlash","save_report":"Hisobotni saqlash","screen_molecule":"Molekulani tekshirish","translate_protein":"Protein tarjimasi","open_colabfold":"ColabFold ochish","search_hint":"Qidiruv natijalari: Disease • Gene • Protein • Drug • PDB • Research • News"},
        "ru": {
        "home":"Главная","news":"Последние новости","modules":"Модули","saved":"Сохранённые","collections":"Коллекции","settings":"Настройки","language":"Язык","search":"Болезнь, ген, белок, препарат, PDB или статья...","search_title":"Научный поиск","latest":"Последние биомедицинские новости","open":"Открыть","close":"Закрыть","back":"На главную","refresh":"Обновить","open_source":"Открыть источник","no_results":"Ничего не найдено","loading":"Загрузка данных...","virtual":"Виртуальная лаборатория","viewer2d":"2D вид","viewer3d":"3D молекулярный просмотр","load_pdb":"Загрузить PDB","demo":"Демо-модель","pdb_path":"Путь к PDB","news_source":"Источник","global":"Глобальный портал биомедицинских исследований","bioinformatics":"Биоинформатика","drug_discovery":"Поиск лекарств","structure_prediction":"Предсказание структуры","pdb_analysis":"Анализ PDB","binding_pocket":"Анализ кармана","docking":"Докинг","ml_ranking":"ML и ранжирование","research_assistant":"Научный помощник","results_history":"Результаты и история","analyze":"Анализировать","analyze_sequence":"Анализировать последовательность","analyze_pocket":"Анализ кармана","clear":"Очистить","copy_sequence":"Копировать последовательность","find_orfs":"Найти ORF","load_pdb":"Загрузить PDB","prepare_workflow":"Подготовить workflow","refresh_result":"Обновить результат","reverse_complement":"Обратный комплемент","save_fasta":"Сохранить FASTA","save_report":"Сохранить отчёт","screen_molecule":"Проверить молекулу","translate_protein":"Транслировать белок","open_colabfold":"Открыть ColabFold","search_hint":"Поиск: Disease • Gene • Protein • Drug • PDB • Research • News"},
        "en": {
        "home":"Home","news":"Latest News","modules":"Modules","saved":"Saved","collections":"Collections","settings":"Settings","language":"Language","search":"Disease, gene, protein, drug, PDB or research...","search_title":"Scientific Search","latest":"Latest biomedical news","open":"Open","close":"Close","back":"Back to Home","refresh":"Refresh","open_source":"Open Source","no_results":"No results found","loading":"Loading data...","virtual":"Virtual Laboratory","viewer2d":"2D view","viewer3d":"3D molecular viewer","load_pdb":"Load PDB","demo":"Demo model","pdb_path":"PDB file path","news_source":"Source","global":"Global biomedical research portal","bioinformatics":"Bioinformatics","drug_discovery":"Drug Discovery","structure_prediction":"Structure Prediction","pdb_analysis":"PDB Analysis","binding_pocket":"Binding Pocket","docking":"Docking","ml_ranking":"ML + Ranking","research_assistant":"Research Assistant","results_history":"Results & History","analyze":"Analyze","analyze_sequence":"Analyze Sequence","analyze_pocket":"Analyze Pocket","clear":"Clear","copy_sequence":"Copy Sequence","find_orfs":"Find ORFs","load_pdb":"Load PDB","prepare_workflow":"Prepare Workflow","refresh_result":"Refresh Result","reverse_complement":"Reverse Complement","save_fasta":"Save FASTA","save_report":"Save Report","screen_molecule":"Screen Molecule","translate_protein":"Translate Protein","open_colabfold":"Open ColabFold","search_hint":"Search: Disease • Gene • Protein • Drug • PDB • Research • News"}}

    def tr(self, key, fallback=None):
        return self.LANG.get(getattr(self, 'language', 'uz'), self.LANG['uz']).get(key, fallback or key)

    def tx(self, text):
        if text in self.LANG.get(getattr(self, 'language', 'uz'), {}):
            return self.tr(text)
        maps={
            "DASHBOARDGA QAYTISH":"back","BACK HOME":"back","OPEN SOURCE":"open_source","CLOSE":"close",
            "REFRESH":"refresh","Open module":"open","Experiment workspace":"virtual",
            "Virtual Laboratory":"virtual","Global Search":"search_title","Latest Biomedical News":"latest",
            "Modules & Sections":"modules","Disease • Gene • Protein • Drug • PDB • Research • News":"search_hint",
            "Bioinformatics":"bioinformatics","Drug Discovery":"drug_discovery","Structure Prediction":"structure_prediction",
            "PDB Analysis":"pdb_analysis","Binding Pocket":"binding_pocket","Docking":"docking","ML + Ranking":"ml_ranking",
            "Research Assistant":"research_assistant","Results & History":"results_history",
            "ANALYZE":"analyze","ANALYZE SEQUENCE":"analyze_sequence","ANALYZE POCKET":"analyze_pocket","CLEAR":"clear","COPY SEQUENCE":"copy_sequence","FIND ORFs":"find_orfs","LOAD PDB":"load_pdb","PREPARE WORKFLOW":"prepare_workflow","REFRESH RESULT":"refresh_result","REVERSE COMPLEMENT":"reverse_complement","SAVE FASTA":"save_fasta","SAVE REPORT":"save_report","SCREEN MOLECULE":"screen_molecule","TRANSLATE PROTEIN":"translate_protein","OPEN COLABFOLD":"open_colabfold",
            "Open module":"open","PDB ANALYSIS":"PDB Analysis","POCKET ANALYSIS":"Binding Pocket","DOCKING":"Docking","ML + REPORT":"ML + Ranking",
            "SCREEN MOLECULE":"SCREEN MOLECULE","SAVE REPORT":"SAVE REPORT","CLEAR":"CLEAR","ANALYZE":"ANALYZE","VALIDATE":"VALIDATE","COPY FASTA":"COPY FASTA","OPEN COLABFOLD":"OPEN COLABFOLD","SAVE FASTA":"SAVE FASTA","FIND ORFS":"FIND ORFS","REVERSE COMPLEMENT":"REVERSE COMPLEMENT","TRANSLATE 3 FRAMES":"TRANSLATE 3 FRAMES"}
        return self.tr(maps[text]) if text in maps else text

    def add_nav(self, text, command):
        b = Button(
            text=self.tx(text),
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
        self.workspace.add_widget(Label(text=f"[b]{self.tx(text)}[/b]", markup=True, color=self.hex(TEXT), font_size=25, size_hint_y=None, height=dp(45)))
        if sub:
            self.workspace.add_widget(Label(text=self.tx(sub), color=self.hex(MUTED), size_hint_y=None, height=dp(35)))

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
            text=self.tx(text),
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

    def card_button(self, icon, title, subtitle, command):
        b=Button(text=f"{icon}  [b]{self.tx(title)}[/b]\n[size=12]{self.tx(subtitle)}[/size]", markup=True, background_normal="", background_color=self.hex(PANEL), color=self.hex(TEXT), halign="left", valign="middle", size_hint_y=None, height=dp(92))
        b.bind(on_release=lambda *_: command())
        return b

    def open_menu(self):
        box=BoxLayout(orientation="vertical",padding=dp(12),spacing=dp(5))
        box.add_widget(Label(text="[b]MEDGEN AI[/b]\n"+self.tr("modules"),markup=True,color=self.hex(ACCENT),size_hint_y=None,height=dp(60)))
        fixed=[("🏠",self.tr("home"),self.dashboard),("📰",self.tr("news"),self.show_news_home),("🧰",self.tr("modules"),self.dashboard),("❤️",self.tr("saved"),self.results_history),("📚",self.tr("collections"),self.research_assistant)]
        for icon,name,cmd in fixed:
            b=Button(text=f"{icon}  {name}",size_hint_y=None,height=dp(44),background_normal="",background_color=self.hex(PANEL),color=self.hex(TEXT))
            b.bind(on_release=lambda inst,c=cmd:(self._close_menu(),c()))
            box.add_widget(b)
        for icon,name,cmd in self.modules:
            b=Button(text=f"{icon}  {self.tx(name)}",size_hint_y=None,height=dp(42),background_normal="",background_color=self.hex(PANEL),color=self.hex(TEXT))
            b.bind(on_release=lambda inst,c=cmd:(self._close_menu(),c()))
            box.add_widget(b)
        close=Button(text=self.tr("close"),size_hint_y=None,height=dp(44),background_normal="",background_color=self.hex(ACCENT),color=self.hex(BG))
        close.bind(on_release=lambda *_:self._close_menu()); box.add_widget(close)
        self.menu_popup=Popup(title="",content=ScrollView(),size_hint=(0.86,0.92),background_color=self.hex(BG),separator_color=self.hex(ACCENT))
        self.menu_popup.content.add_widget(box); self.menu_popup.open()


    def _close_menu(self):
        if getattr(self, "menu_popup", None):
            self.menu_popup.dismiss()

    def open_language(self):
        box=BoxLayout(orientation="vertical",padding=dp(12),spacing=dp(8))
        for code,name in (("uz","🇺🇿 O‘zbek"),("ru","🇷🇺 Русский"),("en","🇬🇧 English")):
            b=Button(text=name,size_hint_y=None,height=dp(50),background_normal="",background_color=self.hex(PANEL),color=self.hex(TEXT))
            b.bind(on_release=lambda inst,c=code:self.set_language(c)); box.add_widget(b)
        self.lang_popup=Popup(title=self.tr("language"),content=box,size_hint=(0.75,0.42)); self.lang_popup.open()


    def set_language(self, code):
        self.language=code
        if getattr(self,"lang_popup",None): self.lang_popup.dismiss()
        self.search_box.hint_text=self.tr("search")
        self.lang_btn.text=code.upper()
        self.dashboard()


    def search_global(self):
        q=self.search_box.text.strip()
        if not q: self.dashboard(); return
        self.clear(); self.page_title("search_title",self.tr("search_hint"))
        out=self.output(); out.text=self.tr("loading")+"\n\n"+q
        threading.Thread(target=self._online_search,args=(q,),daemon=True).start()

    def _online_search(self,q):
        import urllib.parse, json
        results=[]
        def esearch(db,term,label):
            try:
                params=urllib.parse.urlencode({"db":db,"term":term,"retmax":5,"retmode":"json","tool":"MedGenAI","email":"medgenai@example.com"})
                u="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?"+params
                data=json.loads(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"MedGenAI/1.0"}),timeout=10).read().decode())
                ids=data.get("esearchresult",{}).get("idlist",[])
                if ids: results.append((label,ids))
            except Exception: pass
        esearch("pubmed",q,"Research / PubMed")
        esearch("gene",q,"Gene")
        esearch("protein",q,"Protein")
        esearch("structure",q,"PDB / Structure")
        Clock.schedule_once(lambda *_:self._show_search_results(q,results),0)

    def _show_search_results(self,q,results):
        self.clear(); self.page_title("search_title",q)
        if not results:
            self.workspace.add_widget(Label(text=self.tr("no_results"),color=self.hex(MUTED),size_hint_y=None,height=dp(55)))
            self.button(self.tr("back"),lambda *_:self.dashboard()); return
        for label,ids in results:
            card=self.card_button("🔎",label,f"{len(ids)} results",lambda db=label,ids=ids:self._open_ncbi_results(db,ids))
            self.workspace.add_widget(card)
        self.button(self.tr("back"),lambda *_:self.dashboard())

    def _open_ncbi_results(self,label,ids):
        db={"Research / PubMed":"pubmed","Gene":"gene","Protein":"protein","PDB / Structure":"structure"}.get(label,"pubmed")
        url="https://www.ncbi.nlm.nih.gov/"+({"pubmed":"pubmed","gene":"gene","protein":"protein","structure":"structure"}.get(db,db))+"/?term="+urllib.parse.quote(self.search_box.text.strip())
        webbrowser.open(url)


    def refresh_news(self):
        self.news_items=[]; threading.Thread(target=self._fetch_news,daemon=True).start()

    def _fetch_news(self):
        feeds=[("NIH","https://www.nih.gov/news-events/news-releases/rss.xml"),("WHO","https://www.who.int/feeds/entity/mediacentre/news/en/rss.xml")]
        items=[]
        for source,url in feeds:
            try:
                data=urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"MedGenAI/1.0"}),timeout=10).read()
                root=ET.fromstring(data)
                for it in root.findall(".//item")[:12]:
                    title=(it.findtext("title") or "").strip(); link=(it.findtext("link") or "").strip(); pub=(it.findtext("pubDate") or "").strip()
                    if title: items.append((title,link,f"{source} • {pub}"))
            except Exception: pass
        items=items[:24]
        Clock.schedule_once(lambda *_:self._apply_news(items),0)

    def _apply_news(self,items):
        self.news_items=items
        if getattr(self,"on_dashboard",False): self.dashboard()

    def show_news_home(self):
        self.clear(); self.page_title("news",self.tr("latest"))
        grid=GridLayout(cols=1,spacing=dp(7),size_hint_y=None); grid.bind(minimum_height=grid.setter("height"))
        for item in getattr(self,"news_items",[]): grid.add_widget(self.card_button("📰",item[0],item[2],lambda item=item:self.show_news(item)))
        if not self.news_items: grid.add_widget(Label(text=self.tr("loading"),color=self.hex(MUTED),size_hint_y=None,height=dp(50)))
        sc=ScrollView(); sc.add_widget(grid); self.workspace.add_widget(sc)
        self.button(self.tr("refresh"),lambda *_:self.refresh_news()); self.button(self.tr("back"),lambda *_:self.dashboard())

    def show_news(self,item):
        title,link,meta=item; self.clear(); self.page_title(title,meta)
        out=self.output(); out.text=f"{title}\n\n{self.tr('news_source')}: {meta}\n\n{link}"
        self.button(self.tr("open_source"),lambda *_:webbrowser.open(link)); self.button(self.tr("back"),lambda *_:self.dashboard())


    def dashboard(self):
        self.clear(); self.on_dashboard=True
        self.page_title("home",self.tr("global"))
        self.workspace.add_widget(Label(text="🧬  AI • Bioinformatics • Drug Discovery • Research • News",color=self.hex(ACCENT),font_size=15,size_hint_y=None,height=dp(38)))
        grid=GridLayout(cols=2,spacing=dp(7),size_hint_y=None); grid.bind(minimum_height=grid.setter("height"))
        for icon,name,cmd in self.modules: grid.add_widget(self.card_button(icon,name,"Open module",cmd))
        sc=ScrollView(size_hint_y=None,height=dp(250)); sc.add_widget(grid); self.workspace.add_widget(sc)
        self.workspace.add_widget(Label(text="[b]📰 "+self.tr("latest")+"[/b]",markup=True,color=self.hex(TEXT),font_size=18,size_hint_y=None,height=dp(42)))
        ng=GridLayout(cols=1,spacing=dp(7),size_hint_y=None); ng.bind(minimum_height=ng.setter("height"))
        for item in getattr(self,"news_items",[])[:12]: ng.add_widget(self.card_button("📰",item[0],item[2],lambda item=item:self.show_news(item)))
        if not self.news_items: ng.add_widget(Label(text=self.tr("loading"),color=self.hex(MUTED),size_hint_y=None,height=dp(50)))
        nsc=ScrollView(); nsc.add_widget(ng); self.workspace.add_widget(nsc)
        self.on_dashboard=True


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
        self.page_title(
            "Drug Discovery",
            "Molecule screening & drug-likeness"
        )

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

        def tokenize_smiles(smiles):
            atoms = []
            i = 0
            while i < len(smiles):
                ch = smiles[i]
                if ch == "[":
                    j = smiles.find("]", i + 1)
                    if j == -1:
                        raise ValueError("Unclosed bracket in SMILES.")
                    content = smiles[i + 1:j]
                    import re
                    m = re.search(
                        r"(Cl|Br|Si|Na|Li|Ca|Mg|Al|[A-Z][a-z]?)",
                        content
                    )
                    if not m:
                        raise ValueError(
                            f"Unsupported bracket atom: [{content}]"
                        )
                    atoms.append(m.group(1))
                    i = j + 1
                    continue
                if ch.isupper():
                    if (i + 1 < len(smiles) and
                            smiles[i:i+2] in (
                                "Cl", "Br", "Si", "Na", "Li",
                                "Ca", "Mg", "Al")):
                        atoms.append(smiles[i:i+2])
                        i += 2
                    else:
                        atoms.append(ch)
                        i += 1
                    continue
                if ch in "bcnops":
                    atoms.append(ch.upper())
                    i += 1
                    continue
                if ch.isdigit() or ch in "()[]=#-+@/.":
                    i += 1
                    continue
                raise ValueError(
                    f"Unsupported SMILES character: '{ch}'"
                )
            return atoms

        def molecular_formula(atoms):
            counts = {}
            for atom in atoms:
                counts[atom] = counts.get(atom, 0) + 1
            c = counts.get("C", 0)
            n = counts.get("N", 0)
            halogens = sum(
                counts.get(x, 0) for x in ("F", "Cl", "Br", "I")
            )
            h = max(0, 2*c + 2 + n - halogens)
            if c == 0:
                h = max(0, n - halogens)
            counts["H"] = h
            order = [
                "C", "H", "N", "O", "S", "P",
                "F", "Cl", "Br", "I"
            ]
            formula = ""
            for element in order:
                count = counts.get(element, 0)
                if count:
                    formula += element if count == 1 else f"{element}{count}"
            for element in sorted(counts):
                if element not in order and counts[element]:
                    formula += (
                        element if counts[element] == 1
                        else f"{element}{counts[element]}"
                    )
            return formula, counts

        def molecular_weight(counts):
            weights = {
                "H": 1.008, "C": 12.011, "N": 14.007,
                "O": 15.999, "F": 18.998, "P": 30.974,
                "S": 32.06, "Cl": 35.45, "Br": 79.904,
                "I": 126.904, "Si": 28.085, "Na": 22.990,
                "Li": 6.941, "Ca": 40.078, "Mg": 24.305,
                "Al": 26.982
            }
            return sum(weights.get(k, 0.0) * v for k, v in counts.items())

        def estimate_hbd_hba(atoms):
            hbd = atoms.count("N") + atoms.count("O") + atoms.count("S")
            hba = atoms.count("N") + atoms.count("O") + atoms.count("S")
            return min(hbd, 8), min(hba, 12)

        def estimate_rotatable_bonds(smiles, atoms):
            import re
            explicit_single = len(
                re.findall(r"(?<![=#])-(?![=#])", smiles)
            )
            implicit = max(0, len(atoms) - 1)
            return max(
                0,
                min(12, explicit_single if explicit_single else implicit // 2)
            )

        def estimate_tpsa(hbd, hba, atoms):
            return round(
                17.0 * atoms.count("N")
                + 17.0 * atoms.count("O")
                + 25.0 * atoms.count("S"),
                1
            )

        def screen(instance):
            smiles = entry.text.strip()
            if not smiles:
                out.text = "SMILES kiriting."
                return
            try:
                atoms = tokenize_smiles(smiles)
                if not atoms:
                    raise ValueError("SMILES tarkibida atom topilmadi.")
                formula, counts = molecular_formula(atoms)
                mw = molecular_weight(counts)
                hbd, hba = estimate_hbd_hba(atoms)
                rot = estimate_rotatable_bonds(smiles, atoms)
                tpsa = estimate_tpsa(hbd, hba, atoms)
                checks = {
                    "Molecular weight <= 500": mw <= 500,
                    "H-bond donors <= 5": hbd <= 5,
                    "H-bond acceptors <= 10": hba <= 10,
                    "Rotatable bonds <= 10": rot <= 10,
                    "Approx. TPSA <= 140": tpsa <= 140,
                }
                passed = sum(checks.values())
                lines = [
                    "=== DRUG DISCOVERY SCREEN ===", "",
                    f"SMILES: {smiles}",
                    f"Formula: {formula}",
                    f"Approx. Molecular Weight: {mw:.3f} g/mol",
                    f"H-bond Donors (HBD): {hbd}",
                    f"H-bond Acceptors (HBA): {hba}",
                    f"Approx. Rotatable Bonds: {rot}",
                    f"Approx. TPSA: {tpsa:.1f} Å²", "",
                    "=== FILTERS ===",
                ]
                for name, ok in checks.items():
                    lines.append(f"{'PASS' if ok else 'FAIL'}  {name}")
                lines.extend([
                    "",
                    f"Filters passed: {passed}/{len(checks)}", "",
                    "Interpretation:",
                    "Computational screening only.",
                    "It is not a clinical efficacy, safety, or toxicity prediction.",
                    "",
                    "Note: descriptors marked 'Approx.' use a lightweight",
                    "built-in estimator and are not a substitute for RDKit."
                ])
                out.text = "\n".join(lines)
            except Exception as ex:
                self.show_error("Drug Discovery", ex)

        def save_report(instance):
            try:
                import os
                path = os.path.join(
                    self.user_data_dir,
                    "drug_discovery_report.txt"
                )
                with open(path, "w", encoding="utf-8") as f:
                    f.write(out.text)
                out.text += f"\n\nSaved: {path}"
            except Exception as ex:
                self.show_error("Save report", ex)

        def clear_fields(instance):
            entry.text = ""
            out.text = "SMILES maydoniga molekula kiriting."

        self.button("SCREEN MOLECULE", screen)
        self.button("SAVE REPORT", save_report)
        self.button("CLEAR", clear_fields)

    def virtual_laboratory(self):
        self.clear(); self.page_title("virtual","Target → PDB → Pocket → Docking → ML → Report")
        self.workspace.add_widget(Label(text="Interactive 2D / 3D molecular workspace",color=self.hex(MUTED),size_hint_y=None,height=dp(35)))
        path=TextInput(hint_text=self.tr("pdb_path"),multiline=False,background_color=self.hex(INPUT),foreground_color=self.hex(TEXT),size_hint_y=None,height=dp(46))
        self.workspace.add_widget(path)
        viewer=Molecule3DView(size_hint_y=None,height=dp(330)); self.workspace.add_widget(viewer)
        status=Label(text="3D viewer ready — drag to rotate",color=self.hex(MUTED),size_hint_y=None,height=dp(32)); self.workspace.add_widget(status)
        def load_demo(*_):
            import math
            atoms=[]
            for i in range(34):
                t=i*0.55; atoms.append((math.cos(t)*4, math.sin(t)*4, i*0.45-7, 'C'))
            viewer.set_atoms(atoms); status.text="Demo molecular model • drag to rotate"
        def load_pdb(*_):
            try:
                fn=path.text.strip()
                if not os.path.isfile(fn): status.text="PDB file not found"; return
                atoms=[]
                with open(fn,encoding="utf-8",errors="ignore") as f:
                    for line in f:
                        if line.startswith("ATOM") and line[12:16].strip() in ("CA","C","N","O"):
                            atoms.append((float(line[30:38]),float(line[38:46]),float(line[46:54]),line[76:78].strip() or "C"))
                if atoms:
                    # center and scale
                    cx=sum(a[0] for a in atoms)/len(atoms); cy=sum(a[1] for a in atoms)/len(atoms); cz=sum(a[2] for a in atoms)/len(atoms)
                    m=max(max(abs(a[0]-cx),abs(a[1]-cy),abs(a[2]-cz)) for a in atoms) or 1
                    viewer.scale=min(9,180/m); viewer.set_atoms([(a[0]-cx,a[1]-cy,a[2]-cz,a[3]) for a in atoms[:600]])
                    status.text=f"Loaded {min(len(atoms),600)} atoms • drag to rotate"
                else: status.text="No supported ATOM records found"
            except Exception as ex: status.text=f"PDB error: {ex}"
        self.button(self.tr("demo"),load_demo)
        self.button(self.tr("load_pdb"),load_pdb)
        self.button("PDB ANALYSIS",lambda *_:self.pdb_analysis())
        self.button("POCKET ANALYSIS",lambda *_:self.pocket_analysis())
        self.button("DOCKING",lambda *_:self.docking())
        self.button("ML + REPORT",lambda *_:self.ml_ranking_report())
        load_demo()


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
            "Protein sequence validation + ColabFold workflow"
        )

        self.workspace.add_widget(Label(
            text="Protein sequence (FASTA or raw amino-acid sequence)",
            color=self.hex(MUTED), size_hint_y=None, height=dp(30)
        ))

        seq = TextInput(
            multiline=True,
            hint_text="Masalan: MKTIIALSYIFCLVFADYKDDDDK",
            background_color=self.hex(INPUT),
            foreground_color=self.hex(TEXT),
            cursor_color=self.hex(TEXT), font_size=14
        )
        self.workspace.add_widget(seq)

        status = Label(text="Ready", color=self.hex(MUTED), size_hint_y=None, height=dp(35))
        self.workspace.add_widget(status)

        output = TextInput(
            text="Natijalar shu yerda chiqadi.", readonly=True, multiline=True,
            background_color=self.hex(PANEL), foreground_color=self.hex(TEXT), font_size=13
        )
        self.workspace.add_widget(output)

        valid_aa = set("ACDEFGHIKLMNPQRSTVWY")

        def clean_sequence(raw):
            lines = []
            for line in raw.splitlines():
                line = line.strip()
                if not line or line.startswith(">"):
                    continue
                lines.append(line.replace(" ", "").replace("\t", ""))
            return "".join(lines).upper()

        def validate():
            clean = clean_sequence(seq.text)
            invalid = sorted(set(clean) - valid_aa)
            return clean, invalid

        def analyze(instance):
            clean, invalid = validate()
            if not clean:
                status.text = "Protein sequence kiriting."
                output.text = "Sequence bo'sh."
                return
            if invalid:
                status.text = "Noto'g'ri amino-kislota belgisi."
                output.text = ("VALIDATION ERROR\n\nNoto'g'ri belgilar: " +
                               ", ".join(invalid) +
                               "\n\nRuxsat etilgan: ACDEFGHIKLMNPQRSTVWY")
                return

            length = len(clean)
            counts = {aa: clean.count(aa) for aa in sorted(valid_aa)}
            hydrophobic = sum(clean.count(x) for x in "AVILMFWY")
            pos = sum(clean.count(x) for x in "KRH")
            neg = sum(clean.count(x) for x in "DE")
            warnings = []
            if length < 30:
                warnings.append("Juda qisqa sequence; prediction sifati cheklanishi mumkin.")
            if length > 2000:
                warnings.append("Juda uzun sequence; Colab GPU xotirasi yetmasligi mumkin.")
            if clean.count("C") >= 2:
                warnings.append("Cysteine mavjud; disulfide bondlar biologik kontekstga bog'liq.")

            result = [
                "STRUCTURE PREDICTION — SEQUENCE CHECK", "",
                f"Length: {length} aa",
                f"Hydrophobic residues: {hydrophobic} ({hydrophobic / length * 100:.1f}%)",
                f"Positive (K/R/H): {pos}", f"Negative (D/E): {neg}",
                f"Net charge count: {pos - neg}", "", "AMINO ACID COUNTS",
                " ".join(f"{aa}:{counts[aa]}" for aa in sorted(valid_aa)), "",
                "WORKFLOW", "1. Sequence validated locally",
                "2. Copy sequence to ColabFold", "3. Run notebook with GPU",
                "4. Download result ZIP / PDB", "5. Analyze PDB in MedGen AI"
            ]
            if warnings:
                result += ["", "NOTES"] + [f"- {w}" for w in warnings]
            output.text = "\n".join(result)
            status.text = f"Valid sequence: {length} aa"

        def copy_sequence(instance):
            clean, invalid = validate()
            if not clean:
                status.text = "Avval sequence kiriting."
                return
            if invalid:
                status.text = "Copy qilinmadi: sequence noto'g'ri."
                return
            try:
                from kivy.core.clipboard import Clipboard
                Clipboard.copy(clean)
                status.text = "Sequence clipboard'ga nusxalandi."
            except Exception as ex:
                self.show_error("Clipboard", ex)

        def save_fasta(instance):
            clean, invalid = validate()
            if not clean:
                status.text = "Avval sequence kiriting."
                return
            if invalid:
                status.text = "FASTA saqlanmadi: sequence noto'g'ri."
                return
            try:
                path = os.path.join(self.user_data_dir, "structure_prediction.fasta")
                with open(path, "w", encoding="utf-8") as f:
                    f.write(">MedGen_AI_protein\n")
                    for i in range(0, len(clean), 80):
                        f.write(clean[i:i+80] + "\n")
                status.text = "FASTA saqlandi."
                output.text = f"FASTA saved:\n{path}\n\nOPEN COLABFOLD ni bosing."
            except Exception as ex:
                self.show_error("Save FASTA", ex)

        def open_colab(instance):
            clean, invalid = validate()
            if not clean:
                status.text = "Avval protein sequence kiriting."
                return
            if invalid:
                status.text = "ColabFold ochilmadi: sequence noto'g'ri."
                return
            try:
                from kivy.core.clipboard import Clipboard
                Clipboard.copy(clean)
            except Exception:
                pass
            status.text = f"ColabFold ochilmoqda: {len(clean)} aa"
            webbrowser.open(
                "https://colab.research.google.com/github/"
                "sokrypton/ColabFold/blob/main/AlphaFold2.ipynb"
            )
            output.text += ("\n\nCOLABFOLD OPENED\n"
                            "Sequence clipboard'ga nusxalandi; notebookdagi inputga joylang.\n"
                            "ColabFold natijasi ZIP/PDB ko'rinishida olinadi.")

        self.button("ANALYZE SEQUENCE", analyze)
        self.button("COPY SEQUENCE", copy_sequence)
        self.button("SAVE FASTA", save_fasta)
        self.button("OPEN COLABFOLD", open_colab)

        self.workspace.add_widget(Label(
            text="MedGen AI → Validate → ColabFold → PDB → PDB Analysis",
            color=self.hex(ACCENT), font_size=14, size_hint_y=None, height=dp(40)
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
