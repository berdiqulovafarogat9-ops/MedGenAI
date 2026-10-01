from kivy.app import App
from kivy.uix.label import Label


class MedGenDiagnosticApp(App):

    def build(self):
        return Label(
            text="MEDGEN AI\n\nKIVY RUNTIME OK",
            font_size=28,
            halign="center",
            valign="middle"
        )


if __name__ == "__main__":
    MedGenDiagnosticApp().run()
