import dearpygui.dearpygui as dpg
from custom_utils import Utils as u
from evaluator import evaluator
import os
import xlsxwriter


class DpgExt:
    """dummy class dpg extension"""

    @staticmethod
    def draw_answ_table():
        dpg.delete_item("TR")
        with dpg.table(parent="MRW", label="Tabella Risposte", header_row=False, tag="TR"):
            dpg.add_table_column()
            for _entry in u.retrieve_or_display_answers():
                _qst_number, _qst_letter = _entry.split(";")[0].split(" ")
                with dpg.table_row():
                    dpg.add_text(f"{_qst_number} {_qst_letter}")

    @staticmethod
    def mod_answers_file(sender, app_data, user_data):
        u.answer_modifier(user_data[0], user_data[1])
        DpgExt.draw_answ_table()
        dpg.set_value("num", "")
        dpg.set_value("answ", "")

    @staticmethod
    def show_confirm(sender, app_data, user_data):
        dpg.configure_item("DC", show=True)

    @staticmethod
    def confirm_delete(sender, app_data, user_data):
        for i in range(1, 61):
            u.answer_modifier(i, "")
        DpgExt.draw_answ_table()
        DpgExt.exit_confirm("", "", "")

    @staticmethod
    def exit_confirm(sender, app_data, user_data):
        dpg.configure_item("DC", show=False)

    @staticmethod
    def confirm_launch(sender, app_data, user_data):
        path = dpg.get_value("pathToScan")
        dpg.show_item("progress")

        is_60_question_form = dpg.get_value("60QuestionForm")
        is_barcode_ean13 = dpg.get_value("EAN13")
        debug = dpg.get_value("debug")
        max_number_of_tests = dpg.get_value("maxPeople")
        valid_ids = [f"{i:03}" for i in range(max_number_of_tests)] if is_barcode_ean13 else \
            [f"{i:04}" for i in range(1000)]

        how_many_people_got_a_question_right_dict = {i: 0 for i in range(60-20*int(not is_60_question_form))}
        all_users = []
        workbook = xlsxwriter.Workbook("excel_graduatorie.xlsx")
        workbook.add_worksheet()

        placement = 0
        numero_di_presenti_effettivi = len(os.listdir(path))
        for user_index, file_name in enumerate(os.listdir(path)):
            abs_img_path = os.path.join(path, file_name)
            dpg.set_value("progressCount", f"Analizzando:{file_name}. {user_index}^ scansione analizzata su "
                                           f"{numero_di_presenti_effettivi}")
            all_users, how_many_people_got_a_question_right_dict = evaluator(abs_img_path, valid_ids,
                                                                             how_many_people_got_a_question_right_dict,
                                                                             all_users,
                                                                             is_60_question_form, debug)
        sorted_by_score_user_list = sorted(all_users, key=lambda x: (x.score, x.per_sub_score), reverse=True)
        for placement, user in enumerate(sorted_by_score_user_list):
            u.xlsx_dumper(user, placement + 1, u.retrieve_or_display_answers(), workbook, is_60_question_form)

        worksheet = workbook.worksheets()[0]
        for col, number_of_people_who_correctly_answered in how_many_people_got_a_question_right_dict.items():
            worksheet.write(3, 3 + col, f"{round(number_of_people_who_correctly_answered / (placement + 1) * 100)}%",
                            workbook.add_format({'bold': 1,
                                                 'border': 1,
                                                 'align': 'center',
                                                 'valign': 'vcenter'})
                            )
        workbook.close()

        DpgExt.exit_launch("", "", "")
        dpg.show_item("EX")

    @staticmethod
    def exit_launch(sender, app_data, user_data):
        dpg.hide_item("LA")
        dpg.hide_item("progress")
        dpg.set_value("pathToScan", "")

    @staticmethod
    def confirm_path(sender, app_data, user_data):
        dpg.configure_item("LA", show=True)

    @staticmethod
    def run_excel(sender, app_data, user_data):
        os.system("start excel excel_graduatorie.xlsx")
        dpg.hide_item("EX")

    @staticmethod
    def build_answers(sender, app_data, user_data):
        new_answer = (dpg.get_value(sender))
        question_number = int(user_data.split(":")[0])
        u.answer_modifier(question_number, new_answer)
        DpgExt.draw_answ_table()
        if question_number < 60:
            dpg.set_value("BuilderNumber", f"{question_number + 1}:")
        else:
            dpg.set_value("BuilderNumber", f"{1}:")
        dpg.set_value("AnswBuilder", "")
        dpg.focus_item("AnswBuilder")


def main():
    dpg.create_context()

    with dpg.theme() as global_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (255, 16, 16), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_TitleBg, (60, 60, 60), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_Button, (100, 100, 100), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (255, 100, 100), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_TextSelectedBg, (150, 75, 75), category=dpg.mvThemeCat_Core)
    dpg.bind_theme(global_theme)

    with dpg.window(label="Mostra Risposte", width=150, height=650,
                    no_resize=True, tag="MRW", no_close=True, no_move=True):
        with dpg.table(parent="MRW", label="Tabella Risposte", header_row=False, tag="TR"):
            dpg.add_table_column()
            for entry in u.retrieve_or_display_answers():
                qst_number, qst_letter = entry.split(";")[0].split(" ")
                with dpg.table_row():
                    dpg.add_text(f"{qst_number} {qst_letter}")

    with dpg.window(label="Modifica Risposte", width=500, pos=(150, 0),
                    no_resize=True, no_close=True, no_move=True):
        with dpg.group(label="##NumGruop", horizontal=True):
            dpg.add_text("Numero domanda:  ")
            dpg.add_input_text(tag="num")

        with dpg.group(label="##AnswGruop", horizontal=True):
            dpg.add_text("Risposta esatta: ")
            dpg.add_input_text(tag="answ")

        dpg.add_spacer(height=5)
        with dpg.group(label="##ModGruop", horizontal=True):
            dpg.add_spacer(width=90)
            dpg.add_button(pos=(225, 85), label="Modifica", callback=DpgExt.mod_answers_file, tag="mod")

        dpg.add_spacer(height=5)

    with dpg.window(label="Crea Nuove Risposte", width=500, height=235, pos=(150, 115),
                    no_resize=True, no_close=True, no_move=True):
        dpg.add_spacer(height=5)
        with dpg.group(label="##DeleteMain", horizontal=True):
            dpg.add_spacer(width=125)
            dpg.add_button(label="Cancellare tutte le risposte?", callback=DpgExt.show_confirm)

        dpg.add_spacer(height=5)
        with dpg.group(label="##DeleteConfirm", horizontal=True, show=False, tag="DC"):
            dpg.add_spacer(width=150)
            dpg.add_text("Sicuro: ", tag="sure")
            dpg.add_button(label="Sì", tag="y", callback=DpgExt.confirm_delete)
            dpg.add_button(label="No", tag="n", callback=DpgExt.exit_confirm)
            dpg.add_spacer(height=5)

        dpg.add_separator()
        dpg.add_spacer(height=5)
        with dpg.group(label="dummy"):
            with dpg.group(label="##text"):
                dpg.add_text("Inserire una risposta alla volta e premere ENTER")
            with dpg.group(label="##BuilderGruop", horizontal=True):
                dpg.add_spacer(width=25)
                dpg.add_text("1: ", tag="BuilderNumber")
                dpg.add_input_text(label="", tag="AnswBuilder", on_enter=True,
                                   callback=DpgExt.build_answers)

    with dpg.window(label="Analisi Scansioni", width=500, height=300, pos=(150, 350),
                    no_move=True, no_close=True, no_resize=True):
        dpg.add_spacer(height=5)
        with dpg.group(label="##percorsi", horizontal=True):
            dpg.add_text("Percorso alle sacnsioni: ")
            dpg.add_input_text(label="", tag="pathToScan", callback=DpgExt.confirm_launch, on_enter=True, width=250)
            dpg.add_button(label="OK", callback=DpgExt.confirm_path)

        dpg.add_spacer(height=5)
        with dpg.group(label="##Launch", show=False, tag="LA"):
            with dpg.group(label="##debugLaunch", horizontal=True, tag="debugLaunch"):
                dpg.add_text("Massimo numero di partecipanti (approx per eccesso in dubbio): ")
                dpg.add_input_int(label="", tag="maxPeople", width=250, default_value=800)
                dpg.add_spacer(height=20)
            with dpg.group(horizontal=True, tag="CQN"):
                dpg.add_text("Simulazione da 60 quesiti?")
                dpg.add_checkbox(label="", tag="60QuestionForm", default_value=False)
                dpg.add_spacer(width=125)
                dpg.add_text("EAN13?")
                dpg.add_checkbox(label="", tag="EAN13", default_value=True)
            with dpg.group(horizontal=True, tag="DEB"):
                dpg.add_text("Debug?")
                dpg.add_combo(items=["No", "weak", "all"], tag="debug")

            with dpg.group(label="##ConfiL", horizontal=True, tag="confL"):
                dpg.add_spacer(width=100)
                dpg.add_text("Avviare analisi delle scansioni: ", tag="sureL")
                dpg.add_button(label="Sì", tag="yL", callback=DpgExt.confirm_launch)
                dpg.add_button(label="No", tag="nL", callback=DpgExt.exit_launch)
                dpg.add_spacer(height=5)

        with dpg.group(label="##Progress", show=False, horizontal=True, tag="progress"):
            dpg.add_spacer(width=70)
            dpg.add_text("", tag="progressCount")
            dpg.add_spacer(height=5)

        dpg.add_spacer(height=5)
        dpg.add_separator()
        dpg.add_spacer(height=5)

        with dpg.group(label="##Excel", horizontal=True, show=False, tag="EX"):
            dpg.add_spacer(width=200)
            dpg.add_button(label="Excel", callback=DpgExt.run_excel)

    dpg.create_viewport(title='Lettore Ottico v6.1', width=800, height=600)
    dpg.setup_dearpygui()
    dpg.show_viewport()

    while dpg.is_dearpygui_running():
        dpg.set_item_user_data("mod", [dpg.get_value("num"), dpg.get_value("answ")])
        dpg.set_item_user_data("AnswBuilder", dpg.get_value("BuilderNumber"))
        dpg.set_item_user_data("yL", dpg.get_value("pathToScan"))

        dpg.render_dearpygui_frame()

    dpg.destroy_context()


if __name__ == '__main__':
    main()

